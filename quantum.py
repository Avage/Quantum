import subprocess
import sys
from typing import TextIO, Tuple, List

iota_counter = 0


class Token:
    def __init__(self, file_path: str, row: int, col: int, value: str):
        self.file_path = file_path
        self.row = row
        self.col = col
        self.value = value

    def __str__(self):
        return f"{self.file_path}:{self.row}:{self.col}"


def iota(reset=False) -> int:
    global iota_counter
    if reset:
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result


OP_PUSH = iota(True)
OP_ADD = iota()
OP_SUB = iota()
OP_POP = iota()
COUNT_OPS = iota()


def push(x: int) -> Tuple:
    return OP_PUSH, x


def add() -> Tuple:
    return (OP_ADD,)


def sub() -> Tuple:
    return (OP_SUB,)


def pop() -> Tuple:
    return (OP_POP,)


def simulate_program(prg: List[Tuple]) -> None:
    assert COUNT_OPS == 4, 'Exhaustive handling of operands in simulate_program'
    stack = []

    for op in prg:
        if op[0] == OP_PUSH:
            stack.append(op[1])
        elif op[0] == OP_ADD:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif op[0] == OP_SUB:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
        elif op[0] == OP_POP:
            a = stack.pop()
            print(a)
        else:
            assert False, 'Unhandled instruction'


def setup_macros_and_functions(out: TextIO) -> None:
    # Macros for pushing and popping from the stack
    out.write('.macro push Xn:req\n')
    out.write('   str \\Xn, [sp, #-16]!\n')
    out.write('.endm\n')
    out.write('.macro pop Xn:req\n')
    out.write('   ldr \\Xn, [sp], #16\n')
    out.write('.endm\n')

    # Pop function
    out.write('pop:\n')
    out.write('   stp x29, x30, [sp, -48]!\n')
    out.write('   mov x7, -3689348814741910324\n')
    out.write('   mov w3, 10\n')
    out.write('   mov x29, sp\n')
    out.write('   add x1, sp, 16\n')
    out.write('   mov x2, 1\n')
    out.write('   movk x7, 0xcccd, lsl 0\n')
    out.write('   strb w3, [sp, 47]\n')
    out.write('.L2:\n')
    out.write('   umulh x4, x0, x7\n')
    out.write('   sub x5, x1, x2\n')
    out.write('   mov x6, x0\n')
    out.write('   add x2, x2, 1\n')
    out.write('   lsr x4, x4, 3\n')
    out.write('   add x3, x4, x4, lsl 2\n')
    out.write('   sub x3, x0, x3, lsl 1\n')
    out.write('   mov x0, x4\n')
    out.write('   add w3, w3, 48\n')
    out.write('   strb w3, [x5, 31]\n')
    out.write('   cmp x6, 9\n')
    out.write('   bhi .L2\n')
    out.write('   sub x1, x1, x2\n')
    out.write('   mov w0, 1\n')
    out.write('   add x1, x1, 32\n')
    out.write('   mov x16, 4\n')
    out.write('   svc #0\n')
    out.write('   ldp x29, x30, [sp], 48\n')
    out.write('   ret\n')


def compile_program(prg: List[Tuple], file_path: str) -> None:
    with open(file_path, 'w') as out:
        out.write('.global _main\n')
        out.write('.align 2\n')

        setup_macros_and_functions(out)

        out.write('_main:\n')
        assert COUNT_OPS == 4, 'Exhaustive handling of operands in compile_program'
        for op in prg:
            if op[0] == OP_PUSH:
                out.write(f'   ;; -- push {op[1]} --\n')
                out.write(f'   mov x0, #{op[1]}\n')
                out.write(f'   push x0\n')
            elif op[0] == OP_ADD:
                out.write(f'   ;; -- add --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   add x0, x0, x1\n')
                out.write('   push x0\n')
            elif op[0] == OP_SUB:
                out.write(f'   ;; -- sub --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   sub x0, x1, x0\n')
                out.write('   push x0\n')
            elif op[0] == OP_POP:
                out.write(f'   ;; -- pop --\n')
                out.write('   pop x0\n')
                out.write('   bl pop\n')

        out.write('   mov x0, #0\n')
        out.write('   mov x16, #1\n')
        out.write('   svc #0\n')


def usage(prg: str) -> None:
    print(f"Usage: {prg} <SUBCOMMAND> [ARGS]")
    print("SUBCOMMANDS:")
    print("   sim <file>     Simulate the program")
    print("   com <file>     Compile the program")


def call_cmd(cmd: List[str]) -> None:
    print(cmd)
    subprocess.call(cmd)


def unpack(arr: List) -> Tuple:
    return arr[0], arr[1:]


# Find the end of the token value
def value_end(line: str):
    end = 0
    while end + 1 < len(line) and not line[end + 1].isspace():
        end += 1
    return end


# Lexical analysis of a line, finding each token
def lex_line(line: str) -> Tuple[int, str]:
    col_start = 0
    while col_start < len(line):
        if line[col_start].isspace():
            col_start += 1
        else:
            end = col_start + value_end(line[col_start:]) + 1
            yield col_start, line[col_start: end]
            col_start = end


# Lexical analysis of a file, returns a list of tuples containing the Token
def lex_file(file_path: str) -> List[Token]:
    with open(file_path, 'r') as f:
        return [Token(file_path, row, col, word)
                for (row, line) in enumerate(f.readlines())
                for (col, word) in lex_line(line)
                ]


def convert_to_op(token: Token) -> Tuple:
    assert COUNT_OPS == 4, 'Exhaustive handling of operands in convert_to_op'

    if token.value == '+':
        return add()
    elif token.value == '-':
        return sub()
    elif token.value == 'pop':
        return pop()
    else:
        try:
            return push(int(token.value))
        except ValueError as err:
            print(f"{token}: {err}")
            exit(1)


def load_program(path: str) -> List:
    return [convert_to_op(token) for token in lex_file(path)]


if __name__ == '__main__':
    argv = sys.argv
    (program_name, argv) = unpack(argv)

    if len(argv) < 1:
        usage(program_name)
        print("ERROR: no subcommand is provided")
        exit(1)

    (subcommand, argv) = unpack(argv)

    if subcommand == 'sim':
        if len(argv) < 1:
            usage(program_name)
            print("ERROR: no file is provided for simulation")
            exit(1)
        (program_path, argv) = unpack(argv)
        program = load_program(program_path)
        simulate_program(program)
    elif subcommand == 'com':
        if len(argv) < 1:
            usage(program_name)
            print("ERROR: no file is provided for compilation")
            exit(1)
        (program_path, argv) = unpack(argv)
        program = load_program(program_path)
        compile_program(program, 'output.s')
        call_cmd(['as', '-o', 'output.o', 'output.s'])
        call_cmd(['ld', '-o', 'output', 'output.o'])
    else:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)
