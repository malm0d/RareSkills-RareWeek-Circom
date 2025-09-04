# Register Based Architecture / VM

In computing, a register is a small high-speed storage location directly within the CPU used to temporarily hold data and instructions for quick processing, manipulation, and access.

Registers are the fastest form of memory, enabling almost instant access to data by the CPU. The data that registers store is usually small and measured in bits, e.g. 32-bit, 64-bit.

In a virtual machine, a register is similar to the physical CPU register but it exists within the VM's architecture; it is a small, high-speed data storage location that holds and manipulates data for processing.

Register based VMs work like a processor with virtual registers, and each instruction (or 'opcode') directs which registers are the operands (inputs) of an instruction and which register holds the result the instruction.

```Lua
MOVE A B    -- Register(A) := Register(B)
ADD A B C   -- Register(A) := Register(B) + Register(C)
```

Register based VMs still have a stack but values pushed onto the stack are treated as temporary values, and once they are not needed they are popped off the stack.

For example, Lua (Lua 5.0) uses a register based vm, where registers exist within activation records which get assigned onto a run-time stack.

[An activation record is a block of memory that holds all the information needed to execute a single procedure call, including parameters, local variables, and the return address to the calling procedure.]

Unlike stack based VMs, instructions in register based VMs can read their inputs from anywhere in the stack and they can be specific as to where outputs are stored in the stack. Register based VMs also generally do not have "push" and "pop" like opcodes which are used to move values around the stack.

A register based VM can have General-Purpose Registers - used to store intermediate values, variables, or temporary results; and/or Special Registers: Such as the instruction pointer (which holds the address of the next instruction to be executed) and the stack pointer (which manages the VM's stack).

### Resources:
[Lua 5.0 Implementation (PDF)](https://www.lua.org/doc/jucs05.pdf)
