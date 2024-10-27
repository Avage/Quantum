<h1 style="color: #ffa7d7;">Quantum</h1>

---

<p style="color: #ffffff; font-size: 16px;">A stack-based programming language implemented in Python.</p>

[//]: # (Quick Start section)
<h3 style="color: #ffa7d7;">Quick Start</h3>
To run the interpreter, use the following command:

```console
$ python3 quantum.py sim <file-path.qt>
```

To run the compiler, use the following command:

```console
$ python3 quantum.py com <file-path.qt>
./output
```

To compile and run, use `-r` flag:

```console
$ python3 quantum.py com -r <file-path.qt>
```


[//]: # (Push, dump, clone)
<h3 style="color: #ffa7d7;">Stack Operations</h3>
`<arg1>` - Pushes `<arg1>` into stack

<h4 style="color: #ffa7d7;">From here on, `<argX>` refers to the top values of the stack</h4>

`<arg1> dump` - Pops and prints top value of stack

`<arg1> clone` - Clones the top value of stack

[//]: # (+ -)
<h3 style="color: #ffa7d7;">Arithmetic Operations</h3>
`<arg1> <arg2> +` - Pops top two values of stack, adds second value to first value, and pushes the result back into
stack

`<arg1> <arg2> -` - Pops top two values of stack, subtracts top value from second value, and pushes the result back
into stack

[//]: # (Eq, gt, ge, lt, le)
<h3 style="color: #ffa7d7;">Comparison Operations</h3>
`<arg1> <arg2> eq` - Pops top two values of stack, compares them, and pushes 1 if they are equal, 0 otherwise

`<arg1> <arg2> gt` - Pops top two values of stack, compares them, and pushes 1 if the first value is greater than the 
second value, 0 otherwise

`<arg1> <arg2> ge` - Pops top two values of stack, compares them, and pushes 1 if the first value is greater than or 
equal to the second value, 0 otherwise

`<arg1> <arg2> lt` - Pops top two values of stack, compares them, and pushes 1 if the first value is less than the 
second value, 0 otherwise

`<arg1> <arg2> le` - Pops top two values of stack, compares them, and pushes 1 if the first value is less than or equal 
to the second value, 0 otherwise

[//]: # (If, else, end)
<h3 style="color: #ffa7d7;">Conditions</h3>
`<arg1> if <if-body> else <else-body> end` - Pops top value of stack, if it is 1, executes `<if-body>`, otherwise
executes `<else-body>`

[//]: # (While, do, end)
<h3 style="color: #ffa7d7;">Loops</h3>
`<arg1> while <condition> do <body> end` - Pops top value of stack, if it is 1, executes `<body>` and repeats the 
process, otherwise stops

[//]: # (Mem, load, store)
<h3 style="color: #ffa7d7;">Memory</h3>
`mem` - Pushes the memory address at the top of the stack

`<arg1> load` - Pops top value of stack, gets the value from memory at that address, and pushes it into stack

`<arg1> <arg2> store` - Pops top two values of stack, stores the top value at the memory address of the second value

[//]: # (Syscall1, syscall3)
<h3 style="color: #ffa7d7;">Syscalls</h3>
`<arg1> <arg2> syscall1` - Calls syscall1 with top two values of stack. `<arg1>` is syscall argument, `<arg2>` is 
syscall number

`<arg1> <arg2> <arg3> <arg4> syscall3` - Calls syscall3 with top three values of stack. `<arg1>`, `<arg2>`, `<arg3>` 
are syscall arguments, `<arg4>` is syscall number

[//]: # (Syscall1, syscall3)

[//]: # (#)
<h3 style="color: #ffa7d7;">Comments</h3>
`#` - Ignores the rest of the line
