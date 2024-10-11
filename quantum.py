import subprocess
import sys

iota_counter = 0


def iota(reset=False):
    global iota_counter
    if reset:
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result


OP_PUSH = iota(True)
OP_ADD = iota()
OP_SUB = iota()
OP_DUMP = iota()
COUNT_OPS = iota()


def push(x):
    return (OP_PUSH, x)


def add():
    return (OP_ADD,)


def sub():
    return (OP_SUB,)


def dump():
    return (OP_DUMP,)


def simulate_program(prg):
    assert COUNT_OPS == 4, 'Exhaustive handling of operands in simulation'
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
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
        else:
            assert False, 'Unhandled instruction'


def compile_program(prg, file_path):
    with open(file_path, 'w') as out:
        out.write('.global _main\n')
        out.write('.align 2\n')

        # Macros for pushing and popping from the stack
        out.write('.macro push Xn:req\n')
        out.write('   str \\Xn, [sp, #-16]!\n')
        out.write('.endm\n')
        out.write('.macro pop Xn:req\n')
        out.write('   ldr \\Xn, [sp], #16\n')
        out.write('.endm\n')

        # Dump function
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

        out.write('_main:\n')

        assert COUNT_OPS == 4, 'Exhaustive handling of operands in compiling'

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
            elif op[0] == OP_DUMP:
                out.write(f'   ;; -- dump --\n')
                out.write('   pop x0\n')
                out.write('   bl dump\n')

        out.write('   mov x0, #0\n')
        out.write('   mov x16, #1\n')
        out.write('   svc #0\n')


# TODO: un-hardcode the program
program = [
    push(34),
    push(35),
    add(),
    dump(),
    push(420),
    dump()
]


def usage():
    print("Usage: quantum <SUBCOMMAND> [ARGS]")
    print("SUBCOMMANDS:")
    print("   sim      Simulate the program")
    print("   com      Compile the program")


def call_cmd(cmd):
    print(cmd)
    subprocess.call(cmd)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        print("ERROR: no subcommand is provided")

        exit(1)

    subcommand = sys.argv[1]

    if subcommand == 'sim':
        simulate_program(program)
    elif subcommand == 'com':
        compile_program(program, 'output.s')
        call_cmd(['as', '-o', 'output.o', 'output.s'])
        call_cmd(['ld', '-o', 'output', 'output.o'])
    else:
        usage()
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)
