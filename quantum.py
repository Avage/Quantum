import subprocess
import sys
from typing import TextIO, Tuple, List

iota_counter = 0


class Token:
    """ Token class to represent a token in the program, with the file path, row, column, and value """

    def __init__(self, file_path: str, row: int, col: int, value: str):
        self.file_path = file_path
        self.row = row
        self.col = col
        self.value = value

    def __str__(self):
        return f"{self.file_path}:{self.row}:{self.col}"


def enum(reset=False) -> int:
    """ Iota function to generate unique integer values """
    global iota_counter
    if reset:
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result


OP_PUSH = enum(True)
OP_ADD = enum()
OP_SUB = enum()
OP_DUMP = enum()
OP_EQ = enum()
OP_IF = enum()
OP_ELSE = enum()
OP_END = enum()
COUNT_OPS = enum()


def op_push(x: int) -> Tuple:
    return OP_PUSH, x


def op_add() -> Tuple:
    return (OP_ADD,)


def op_sub() -> Tuple:
    return (OP_SUB,)


def op_dump() -> Tuple:
    return (OP_DUMP,)


def op_eq() -> Tuple:
    return (OP_EQ,)


def op_if() -> Tuple:
    return (OP_IF,)


def op_else() -> Tuple:
    return (OP_ELSE,)


def op_end() -> Tuple:
    return (OP_END,)


def simulate_program(prg: List[Tuple]) -> None:
    assert COUNT_OPS == 8, 'Exhaustive handling of operands in simulate_program'
    stack = []
    op_index = 0
    while op_index < len(prg):
        op = prg[op_index]
        if op[0] == OP_PUSH:
            stack.append(op[1])
            op_index += 1
        elif op[0] == OP_ADD:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
            op_index += 1
        elif op[0] == OP_SUB:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
            op_index += 1
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
            op_index += 1
        elif op[0] == OP_EQ:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))
            op_index += 1
        elif op[0] == OP_IF:
            assert len(op) >= 2, "END of the IF block is not referenced"
            a = stack.pop()
            if a == 0:
                op_index = op[1]
            else:
                op_index += 1
        elif op[0] == OP_ELSE:
            assert len(op) >= 2, "END of the ELSE block is not referenced"
            op_index = op[1]
        elif op[0] == OP_END:
            op_index += 1
        else:
            assert False, f'Unhandled instruction'


def setup_macros_and_functions(out: TextIO) -> None:
    """ Initial macros and functions setup """

    # Macros for pushing and popping from the stack
    out.write('.macro push Xn:req\n')
    out.write('   str \\Xn, [sp, #-16]!\n')
    out.write('.endm\n')
    out.write('.macro pop Xn:req\n')
    out.write('   ldr \\Xn, [sp], #16\n')
    out.write('.endm\n')

    # Dump function
    # Pops and prints value in x0
    out.write('dump:\n')
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
        assert COUNT_OPS == 8, 'Exhaustive handling of operands in compile_program'
        for op_index in range(len(prg)):
            op = prg[op_index]
            if op[0] == OP_PUSH:
                # Pushes the value to the stack
                out.write(f'   ;; -- push {op[1]} --\n')
                out.write(f'   mov x0, #{op[1]}\n')
                out.write('   push x0\n')
            elif op[0] == OP_ADD:
                # Pops the top two values on the stack and pushes the result
                out.write('   ;; -- add --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   add x0, x0, x1\n')
                out.write('   push x0\n')
            elif op[0] == OP_SUB:
                # Subtracts the top value from the second value on the stack and pushes the result
                out.write('   ;; -- sub --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   sub x0, x1, x0\n')
                out.write('   push x0\n')
            elif op[0] == OP_DUMP:
                # Pops and prints the value at the top of the stack
                out.write('   ;; -- dump --\n')
                out.write('   pop x0\n')
                out.write('   bl dump\n')
            elif op[0] == OP_EQ:
                # Compares the top two values on the stack and pushes the result
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x0, x1\n')
                out.write('   cset x0, eq\n')
                out.write('   push x0\n')
            elif op[0] == OP_IF:
                # Pops the top value on the stack and jumps to the END of the IF block if it is 0
                assert len(op) >= 2, "END of the IF block is not referenced"
                out.write('   ;; -- if --\n')
                out.write('   pop x0\n')
                out.write(f'   cbz x0, label_{op[1]}\n')
            elif op[0] == OP_ELSE:
                # Jumps in case IF block was executed, marks the start of the ELSE block
                assert len(op) >= 2, "END of the ELSE block is not referenced"
                out.write(f'   b label_{op[1]}\n')
                out.write('   ;; -- else --\n')
                out.write(f'label_{op_index + 1}:\n')
            elif op[0] == OP_END:
                # Marks the end of an IF or ELSE block
                out.write('   ;; -- end --\n')
                out.write(f'label_{op_index}:\n')
            else:
                assert False, 'Unhandled instruction'

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


def construct_blocks(prg: List[Tuple]) -> List[Tuple]:
    stack = []
    assert COUNT_OPS == 8, ('Exhaustive handling of operands in construct_blocks. Note, not all operations need to be '
                            'implemented here. Only those that form blocks')
    for op_index in range(len(prg)):
        op = prg[op_index]
        if op[0] == OP_IF:
            stack.append(op_index)
        elif op[0] == OP_ELSE:
            assert stack, 'ELSE can be used only with with IF blocks'
            block_start = stack.pop()
            assert prg[block_start][0] == OP_IF, 'ELSE can be used only with with IF blocks'
            prg[block_start] += (op_index + 1,)
            stack.append(op_index)
        elif op[0] == OP_END:
            assert stack, 'END can be used only with with IF or ELSE blocks'
            block_start = stack.pop()
            assert prg[block_start][0] == OP_IF or prg[block_start][0] == OP_ELSE, (
                'END can be used only with with IF or ELSE blocks')
            prg[block_start] += (op_index,)
    return prg


def convert_to_op(token: Token) -> Tuple:
    assert COUNT_OPS == 8, 'Exhaustive handling of operands in convert_to_op'

    if token.value == '+':
        return op_add()
    elif token.value == '-':
        return op_sub()
    elif token.value == 'dump':
        return op_dump()
    elif token.value == '=':
        return op_eq()
    elif token.value == 'if':
        return op_if()
    elif token.value == 'else':
        return op_else()
    elif token.value == 'end':
        return op_end()
    else:
        try:
            return op_push(int(token.value))
        except ValueError as err:
            print(f"{token}: {err}")
            exit(1)


def load_program(path: str) -> List:
    return construct_blocks([convert_to_op(token) for token in lex_file(path)])


if __name__ == '__main__':
    argv = sys.argv
    program_name, *argv = argv

    if len(argv) < 1:
        usage(program_name)
        print("ERROR: no subcommand is provided")
        exit(1)

    subcommand, *argv = argv

    if subcommand == 'sim':
        if len(argv) < 1:
            usage(program_name)
            print("ERROR: no file is provided for simulation")
            exit(1)
        program_path, *argv = argv
        program = load_program(program_path)
        simulate_program(program)
    elif subcommand == 'com':
        if len(argv) < 1:
            usage(program_name)
            print("ERROR: no file is provided for compilation")
            exit(1)
        program_path, *argv = argv
        program = load_program(program_path)
        compile_program(program, 'output.s')
        call_cmd(['as', '-o', 'output.o', 'output.s'])
        call_cmd(['ld', '-o', 'output', 'output.o'])
    else:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)
