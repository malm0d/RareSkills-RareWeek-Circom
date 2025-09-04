'''
Prerequisites: Understand what a register-based architecture / VM is

SlimVM is a ZK VM with n registers. Register 0 is special as that is the destination register.

The supported opcodes are as follows

WRITE dst value
ADD r1 r2
SUB r1 r2
COPY rdst
ISZERO r
JUMPZ dst

ADD and SUB cannot read from register 0 and only write to it. The following code writes 5 to register 1 and counts down to zero.

IC
 0 WRITE 1 2   ; start register 1 at 2
 1 WRITE 2 1   ; constant one to subtract
 2 SUB 1 2     ; r0 = r1 - r2
 3 COPY 1      ; write subtracted value to r1
 4 ISZERO 1    ; did we decrement to zero?
 5 JUMPZ 2     ; jump to 2 if r0 == 0
 6 END

----------------
| 0| 0| 0| 0| 0|
----------------

IC = 0
WRITE 1 2
----------------
| 0| 2| 1| 0| 0|
----------------

IC = 1
WRITE 2 1
----------------
| 1| 2| 1| 0| 0|
----------------

IC = 2
SUB 1 2
----------------
| 1| 2| 1| 0| 0|
----------------

IC = 3
COPY 1
----------------
| 1| 1| 1| 0| 0|
----------------

IC = 4
ISZERO 1
----------------
| 0| 1| 1| 0| 0|
----------------

IC = 5
JUMPZ 2
----------------
| 0| 1| 1| 0| 0|
----------------

IC = 2
SUB 1 2
----------------
| 0| 1| 1| 0| 0|
----------------

IC = 3
COPY 1
----------------
| 0| 0| 1| 0| 0|
----------------

IC = 4
ISZERO 1
----------------
| 1| 0| 1| 0| 0|
----------------

IC = 5
JUMPZ 5
----------------
| 0| 0| 1| 0| 0|
----------------

PROGRAM END
'''

def write(prev_state, rdst, value):
    next_state = prev_state[:]
    next_state[rdst] = value
    return next_state

def add(prev_state, ra, rb):
    next_state = prev_state[:]
    next_state[0] = prev_state[ra] + prev_state[rb]
    return next_state

def sub(prev_state, ra, rb):
    next_state = prev_state[:]
    next_state[0] = prev_state[ra] - prev_state[rb]
    return next_state

def cpy(prev_state, rdst):
    next_state = prev_state[:]
    next_state[rdst] = prev_state[0]
    return next_state

def iszero(prev_state, r):
    next_state = prev_state[:]
    if prev_state[r] == 0:
        next_state[0] = 1
    else:
        next_state[0] = 0
    return next_state

def jumpz(prev_state, pc, r):
    if prev_state[0] == 0:
        pc = r
    else:
        pc = pc + 1
    return prev_state, pc 
    

def main():

    # the following program writes 4 to register 1 and decrements it
    # until it reaches 0
    instructions = ["WRITE", "WRITE", "SUB", "COPY", "ISZERO", "JUMPZ"]
    arg1 =         [1,       2,       1,     1,      1,        2,     ]
    arg2 =         [4,       1,       2,     1,      None,     None,  ]

    pc = 0
    cycles = 18
    steps = 0

    cont = True;
    prev_state = [0] * 3
    next_state = [0] * 3
    while steps < cycles:
        steps = steps + 1
        instr = instructions[pc]
        if instr == "WRITE":
            next_state = write(prev_state, arg1[pc], arg2[pc])
            pc = pc + 1
        if instr == "SUB":
            next_state = sub(prev_state, arg1[pc], arg2[pc])
            pc = pc + 1
        if instr == "COPY":
            next_state = cpy(prev_state, arg1[pc])
            pc = pc + 1
        if instr == "ISZERO":
            next_state = iszero(prev_state, arg1[pc])
            pc = pc + 1
        if instr == "JUMPZ":
            next_state, pc = jumpz(prev_state, pc, 2)

        print(next_state)
        prev_state = next_state
main()