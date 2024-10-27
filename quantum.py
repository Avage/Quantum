import subprocess
import sys
from typing import TextIO, Tuple, List

iota_counter = 0


def enum(reset=False) -> int:
    """ Iota function to generate unique integer values """
    global iota_counter
    if reset:
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result


MEMORY_ALLOCATION = 640_000

OP_PUSH = enum(True)
OP_ADD = enum()
OP_SUB = enum()
OP_DUMP = enum()
OP_CLONE = enum()
OP_EQ = enum()
OP_GT = enum()
OP_GE = enum()
OP_LT = enum()
OP_LE = enum()
OP_IF = enum()
OP_ELSE = enum()
OP_END = enum()
OP_WHILE = enum()
OP_DO = enum()
OP_MEM = enum()
OP_LOAD = enum()
OP_SAVE = enum()
OP_SYSCALL1 = enum()
OP_SYSCALL3 = enum()
COUNT_OPS = enum()


class Token:
    """ Token class to represent a token in the program, with the file path, row, column, and value """

    def __init__(self, file_path: str, row: int, col: int, value: str):
        self.file_path = file_path
        self.row = row
        self.col = col
        self.value = value

    def __str__(self):
        return f"{self.file_path}:{self.row}:{self.col}"

    def get_location(self) -> Tuple[str, int, int]:
        return self.file_path, self.row, self.col


class Operation:
    """ Operation class to represent an operation in the program """

    def __init__(self, op_type: int, loc: Tuple[str, int, int], value: int = None, jump: int = None):
        self.type = op_type
        self.loc = loc
        self.value = value
        self.jump = jump


def simulate_program(prg: List[Operation]) -> None:
    assert COUNT_OPS == 20, 'Exhaustive handling of operands in `simulate_program`'
    stack = []
    memory = bytearray(MEMORY_ALLOCATION)
    op_index = 0
    while op_index < len(prg):
        op = prg[op_index]
        if op.type == OP_PUSH:
            stack.append(op.value)
            op_index += 1
        elif op.type == OP_ADD:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(val_1 + val_2)
            op_index += 1
        elif op.type == OP_SUB:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(val_1 - val_2)
            op_index += 1
        elif op.type == OP_DUMP:
            val_1 = stack.pop()
            print(val_1)
            op_index += 1
        elif op.type == OP_CLONE:
            val_1 = stack.pop()
            stack.append(val_1)
            stack.append(val_1)
            op_index += 1
        elif op.type == OP_EQ:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(int(val_1 == val_2))
            op_index += 1
        elif op.type == OP_GT:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(int(val_1 > val_2))
            op_index += 1
        elif op.type == OP_GE:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(int(val_1 >= val_2))
            op_index += 1
        elif op.type == OP_LT:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(int(val_1 < val_2))
            op_index += 1
        elif op.type == OP_LE:
            val_2 = stack.pop()
            val_1 = stack.pop()
            stack.append(int(val_1 <= val_2))
            op_index += 1
        elif op.type == OP_IF:
            assert op.jump is not None, "`end` is not referenced in `if` block"
            val_1 = stack.pop()
            if val_1 == 0:
                op_index = op.jump
            else:
                op_index += 1
        elif op.type == OP_ELSE:
            assert op.jump is not None, "`end` is not referenced in `else` block"
            op_index = op.jump
        elif op.type == OP_WHILE:
            op_index += 1
        elif op.type == OP_DO:
            assert op.jump is not None, "`end` is not referenced in `while-do` block"
            val_1 = stack.pop()
            if val_1 == 0:
                op_index = op.jump
            else:
                op_index += 1
        elif op.type == OP_END:
            assert op.jump is not None, "`end` doesn't have reference to the next instruction to jump"
            op_index = op.jump
        elif op.type == OP_MEM:
            stack.append(0)
            op_index += 1
        elif op.type == OP_LOAD:
            val_1 = stack.pop()
            stack.append(memory[val_1])
            op_index += 1
        elif op.type == OP_SAVE:
            val_2 = stack.pop()
            val_1 = stack.pop()
            memory[val_1] = val_2 & 0xFF
            op_index += 1
        elif op.type == OP_SYSCALL1:
            val_2 = stack.pop()
            val_1 = stack.pop()
            # 1 is exit syscall
            if val_2 == 1:
                exit(val_1)
            else:
                assert False, f'Unhandled syscall: {val_2}'
        elif op.type == OP_SYSCALL3:
            val_4 = stack.pop()
            val_3 = stack.pop()
            val_2 = stack.pop()
            val_1 = stack.pop()
            # 4 is write syscall
            if val_4 == 4:
                s = memory[val_2: val_2 + val_3].decode('utf-8')
                if val_1 == 1:
                    print(s, end='')
                elif val_1 == 2:
                    print(s, end='', file=sys.stderr)
                else:
                    assert False, f'Unknown file description: {val_1}'
            else:
                assert False, f'Unhandled syscall: {val_4}'
            op_index += 1
        else:
            assert False, f'Unhandled instruction: {op.type}'


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


def compile_program(prg: List[Operation], file_path: str) -> None:
    with open(file_path, 'w') as out:
        out.write('.global _main\n')
        out.write('.align 2\n')

        # Setup macros
        setup_macros_and_functions(out)

        out.write('_main:\n')
        assert COUNT_OPS == 20, 'Exhaustive handling of operands in `compile_program`'
        for op_index in range(len(prg)):
            op = prg[op_index]
            out.write(f'label_{op_index}:\n')
            if op.type == OP_PUSH:
                # Pushes the value to the stack
                out.write(f'   ;; -- push {op.value} --\n')
                out.write(f'   mov x0, #{op.value}\n')
                out.write('   push x0\n')
            elif op.type == OP_ADD:
                # Pops the top two values on the stack and pushes the result
                out.write('   ;; -- add --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   add x0, x0, x1\n')
                out.write('   push x0\n')
            elif op.type == OP_SUB:
                # Subtracts the top value from the second value on the stack and pushes the result
                out.write('   ;; -- sub --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   sub x0, x1, x0\n')
                out.write('   push x0\n')
            elif op.type == OP_DUMP:
                # Pops and prints the value at the top of the stack
                out.write('   ;; -- dump --\n')
                out.write('   pop x0\n')
                out.write('   bl dump\n')
            elif op.type == OP_CLONE:
                # Pops the value at the top of the stack and pushes it back 2 times
                out.write('   ;; -- clone --\n')
                out.write('   pop x0\n')
                out.write('   push x0\n')
                out.write('   push x0\n')
            elif op.type == OP_EQ:
                # Pops the top two values on the stack and pushes the result of the EQ comparison
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x0, x1\n')
                out.write('   cset x0, eq\n')
                out.write('   push x0\n')
            elif op.type == OP_GT:
                # Pops the top two values on the stack and pushes the result of the GT comparison
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x1, x0\n')
                out.write('   cset x0, gt\n')
                out.write('   push x0\n')
            elif op.type == OP_GE:
                # Pops the top two values on the stack and pushes the result of the GE comparison
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x1, x0\n')
                out.write('   cset x0, ge\n')
                out.write('   push x0\n')
            elif op.type == OP_LT:
                # Pops the top two values on the stack and pushes the result of the LT comparison
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x1, x0\n')
                out.write('   cset x0, lt\n')
                out.write('   push x0\n')
            elif op.type == OP_LE:
                # Pops the top two values on the stack and pushes the result of the LE comparison
                out.write('   ;; -- eq --\n')
                out.write('   pop x0\n')
                out.write('   pop x1\n')
                out.write('   cmp x1, x0\n')
                out.write('   cset x0, le\n')
                out.write('   push x0\n')
            elif op.type == OP_IF:
                # Pops the top value on the stack and jumps to the END of the IF block if it is 0
                assert op.jump is not None, "`end` is not referenced in `if` block"
                out.write('   ;; -- if --\n')
                out.write('   pop x0\n')
                out.write(f'   cbz x0, label_{op.jump}\n')
            elif op.type == OP_ELSE:
                # Jumps in case IF block was executed, marks the start of the ELSE block
                assert op.jump is not None, "`end` is not referenced in `else` block"
                out.write(f'   b label_{op.jump}\n')
                out.write('   ;; -- else --\n')
            elif op.type == OP_WHILE:
                # Marks the start of the WHILE block
                out.write('   ;; -- while --\n')
            elif op.type == OP_DO:
                # Pops the top value on the stack and jumps to the END of the WHILE block if it is 0
                assert op.jump is not None, "`end` is not referenced in `while-do` block"
                out.write('   ;; -- do --\n')
                out.write('   pop x0\n')
                out.write(f'   cbz x0, label_{op.jump}\n')
            elif op.type == OP_END:
                # Marks the end of an IF or ELSE block
                assert op.jump is not None, "`end` doesn't have reference to the next instruction to jump"
                out.write('   ;; -- end --\n')
                out.write(f'   b label_{op.jump}\n')
            elif op.type == OP_MEM:
                # Pushes the memory address to the stack
                out.write('   ;; -- mem --\n')
                out.write('   adrp x0, mem@PAGE\n')
                out.write('   add x0, x0, mem@PAGEOFF\n')
                out.write('   push x0\n')
            elif op.type == OP_LOAD:
                # Pops the top value on the stack and pushes the value at that memory address
                out.write('   ;; -- load --\n')
                out.write('   pop x0\n')
                out.write('   ldrb w1, [x0]\n')
                out.write('   push w1\n')
            elif op.type == OP_SAVE:
                # Pops the top two values on the stack and saves the top value to the memory address of the second value
                out.write('   ;; -- save --\n')
                out.write('   pop w0\n')
                out.write('   pop x1\n')
                out.write('   strb w0, [x1]\n')
            elif op.type == OP_SYSCALL1:
                # Pops the top two values on the stack and makes a syscall with the top value as the syscall number and
                # the second value as the argument
                out.write('   ;; -- syscall1 --\n')
                out.write('   pop x16\n')
                out.write('   pop x0\n')
                out.write('   svc #0\n')
            elif op.type == OP_SYSCALL3:
                # Pops the top four values on the stack and makes a syscall with the top value as the syscall number and
                # the next three values as the arguments
                out.write('   ;; -- syscall3 --\n')
                out.write('   pop x16\n')
                out.write('   pop x2\n')
                out.write('   pop x1\n')
                out.write('   pop x0\n')
                out.write('   svc #0\n')
            else:
                assert False, f'Unhandled instruction {op.type}'
        out.write(f'label_{op_index + 1}:\n')
        out.write('   mov x0, #0\n')
        out.write('   mov x16, #1\n')
        out.write('   svc #0\n')

        # Allocate memory
        out.write('.section __DATA, __BSS\n')
        out.write(f'mem: .skip {MEMORY_ALLOCATION}\n')


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
                for (col, word) in lex_line(line.split("#")[0])  # Skip comments
                ]


def construct_blocks(prg: List[Operation]) -> List[Operation]:
    stack = []
    assert COUNT_OPS == 20, ('Exhaustive handling of operands in `construct_blocks`. Note, not all operations need to '
                             'be implemented here. Only those that form blocks')
    for op_index in range(len(prg)):
        op = prg[op_index]
        if op.type == OP_IF:
            stack.append(op_index)
        elif op.type == OP_ELSE:
            assert stack, '`else` can be used only with with `if` blocks'
            block_start = stack.pop()
            assert prg[block_start].type == OP_IF, '`else` can be used only with with `if` blocks'
            prg[block_start].jump = op_index + 1
            stack.append(op_index)
        elif op.type == OP_WHILE:
            stack.append(op_index)
        elif op.type == OP_DO:
            block_while = stack.pop()
            prg[op_index].jump = block_while
            stack.append(op_index)
        elif op.type == OP_END:
            assert stack, 'Unnecessary `end` operation'
            block_start = stack.pop()
            if prg[block_start].type in [OP_IF, OP_ELSE]:
                prg[block_start].jump = op_index
                prg[op_index].jump = op_index + 1
            elif prg[block_start].type == OP_DO:
                assert prg[block_start].jump is not None, '`while` is not referenced in `do` block'
                prg[op_index].jump = prg[block_start].jump
                prg[block_start].jump = op_index + 1
            else:
                assert False, '`end` can be used only with with `if`, `else`, `while-do` blocks'
    return prg


def convert_to_op(token: Token) -> Operation:
    assert COUNT_OPS == 20, 'Exhaustive handling of operands in `convert_to_op`'

    if token.value == '+':
        return Operation(OP_ADD, token.get_location())
    elif token.value == '-':
        return Operation(OP_SUB, token.get_location())
    elif token.value == 'dump':
        return Operation(OP_DUMP, token.get_location())
    elif token.value == 'clone':
        return Operation(OP_CLONE, token.get_location())
    elif token.value == '=':
        return Operation(OP_EQ, token.get_location())
    elif token.value == '>':
        return Operation(OP_GT, token.get_location())
    elif token.value == '>=':
        return Operation(OP_GE, token.get_location())
    elif token.value == '<':
        return Operation(OP_LT, token.get_location())
    elif token.value == '<=':
        return Operation(OP_LE, token.get_location())
    elif token.value == 'if':
        return Operation(OP_IF, token.get_location())
    elif token.value == 'else':
        return Operation(OP_ELSE, token.get_location())
    elif token.value == 'end':
        return Operation(OP_END, token.get_location())
    elif token.value == 'while':
        return Operation(OP_WHILE, token.get_location())
    elif token.value == 'do':
        return Operation(OP_DO, token.get_location())
    elif token.value == 'mem':
        return Operation(OP_MEM, token.get_location())
    elif token.value == 'load':
        return Operation(OP_LOAD, token.get_location())
    elif token.value == 'save':
        return Operation(OP_SAVE, token.get_location())
    elif token.value == 'syscall1':
        return Operation(OP_SYSCALL1, token.get_location())
    elif token.value == 'syscall3':
        return Operation(OP_SYSCALL3, token.get_location())
    else:
        try:
            return Operation(OP_PUSH, token.get_location(), value=int(token.value))
        except ValueError as err:
            print(f"{token}: {err}")
            exit(1)


def load_program(path: str) -> List:
    return construct_blocks([convert_to_op(token) for token in lex_file(path)])


def usage(prg: str) -> None:
    print(f"Usage: {prg} <SUBCOMMAND> [ARGS]")
    print("SUBCOMMANDS:")
    print("   sim <file>     Simulate the program")
    print("   com <file>     Compile the program")


def call_cmd(cmd: List[str]) -> None:
    print(cmd)
    subprocess.call(cmd)


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
        options = ''
        if len(argv) < 1:
            usage(program_name)
            print("ERROR: no file is provided for compilation")
            exit(1)
        elif len(argv) > 1:
            options, program_path, *argv = argv
        else:
            program_path, *argv = argv
        program = load_program(program_path)
        compile_program(program, 'output.s')
        call_cmd(['as', '-o', 'output.o', 'output.s'])
        call_cmd(['ld', '-o', 'output', 'output.o'])
        if options == '-r':
            call_cmd(['./output'])
    else:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)
