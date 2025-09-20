# Circom Day 6

## Unstructured Recall

Halo2 by ZCash and PSE (https://github.com/privacy-ethereum/halo2)

Always constraint the inputs, outputs, AND any transition values.

Halo2 is based on PLONK.
PLONK uses a tables -> there is a lookup table, an advise, instances etc.
The lookup table holds all premissible values for the circuit.
The selector basically "selects" the row to constraint: (s * (a + b - c)).
Regions (Ask David to go thorugh again)
PLONK is more flexible than Groth16.
It also uses KZG (commitment of polynomials to elliptic curves) and billinear pairing.

Github:

//----------------------------------------

ZKVM Register-based

Register 0 is always reserved for operation outputs.

Make a ZKVM with
ADD
SUB
CPY
SET

//----------------------------------------

Why do we need forceEnabled?

Architecturally, we want to enable and constraint the correct opcodes, while also allowing
all possible operations at every step. We need to selectively enable only one that should execute.
It allows conditional constraints.

//--------------------------------------------------------------------------------
//--------------------------------------------------------------------------------

ZKVM
```
pragma circom 2.1.6;

include "circomlib/comparators.circom";

//Quin selector.
template Select(n) {
    signal input in[n];
    signal input index;

    signal output out;

    signal arr[n];
    var sum;
    component eqs[n];
    for (var i = 0; i < n; i++) {
        eqs[i] = IsEqual();
        eqs[i].in[0] <== i;
        eqs[i].in[1] <== index;
        arr[i] <== eqs[i].out * in[i];
        sum += arr[i];
    }
    out <== sum;
}

// Constrain that an ADD operation executed correctly.
// Only register 0 changes to the sum, all other registers remain unchanged.
//
template AddOp(nReg) {
    signal input prev[nReg]; // states
    signal input curr[nReg];

    signal input arg1; // arg for first register
    signal input arg2; // arg for second register

    signal input enabled; //to compare or not

    component feqs[nReg];

    // All registers other than reg 0 should be the same value;
    for (var i = 1; i < nReg; i++) {
        feqs[i] = ForceEqualIfEnabled();
        feqs[i].in[0] <== prev[i];
        feqs[i].in[1] <== curr[i];
        feqs[i].enabled <== enabled;
    }

    component s1 = Select(nReg);
    component s2 = Select(nReg);

    // Extract values from the prev state used for ADD op.
    // The output should be the value in the registers.
    for (var i = 0; i < nReg; i++) {
        s1.in[i] <== prev[i];
        s2.in[i] <== prev[i];
    }
    s1.index <== arg1;
    s2.index <== arg2;

    // Constrain that reg 0 in the current state is the sum of the
    // values from the two given registers in the previous state
    feqs[0] = ForceEqualIfEnabled();
    feqs[0].in[0] <== curr[0];
    feqs[0].in[1] <== s1.out + s2.out;
    feqs[0].enabled <== enabled;
}

// We want to constraint that the SET opcode changed its target register's value and
// that every other register remains unchanged.
//
// If the index matches the register, then z[i] will be the value, and eqs[i].out
// will be 1. Then in `prev[i] * (1 - eqs[i].out) + z[i];`, this makes the value `z[i]`.
// Otherwise, if eqs[i].out is 0 (index doesnt match register), then z[i] will technically
// be 0, and so in `prev[i] * (1 - eqs[i].out) + z[i];` will just be `prev[i]`.
// `enabled` will not be on when we are comparing an updated register.
//
template SetOp(nReg) {
    signal input prev[nReg];
    signal input curr[nReg];

    signal input reg;
    signal input val;

    signal input enabled;

    component eqs[nReg];
    component feq[nReg];
    signal z[nReg];
    for (var i = 0; i < nReg; i++) {
        eqs[i] = IsEqual();
        eqs[i].in[0] <== i;
        eqs[i].in[1] <== reg;

        // z[i] <== 0 (if not eq), val (if eq)
        z[i] <== val * eqs[i].out;
        S
        feq[i] = ForceEqualIfEnabled();
        feq[i].in[0] <== curr[i];
        feq[i].in[1] <== prev[i] * (1 - eqs[i].out) + z[i];
        feq[i].enabled <== enabled;
    }
}


// Need arrays of program counters, next program counters, and executed op codes.
// Program counters array is length + 1, because we need to account for step 0.
// Each first item in each array should be 0 because there is no change in the state
// at step 0.
//
// state is a 2D array because we have to trace each state, and each state has n registers.
// Number of rows in the state array is nSteps + 1, because we need to account for the default
// state. I.e. if our program has 2 steps, then 2 transitions from the default state means
// 3 recorded states.
//
template SaturdayVM(nReg, _nSteps, nInstr) {
    var nSteps = _nSteps + 1;
    var SET = 1;
    var ADD = 2;
    signal input instructions[nInstr];
    signal input args1[nInstr];
    signal input args2[nInstr];

    // We can use symbolic variables here because these are not what we
    // really want to use for constraining state transitions.
    var isSet[nSteps];
    var isAdd[nSteps];
    var ops[nSteps];
    var arg1[nSteps];
    var arg2[nSteps];
    var pc[nSteps];
    var npc[nSteps];
    var state[nSteps][nReg];

    isSet[0] = 0;
    isAdd[0] = 0;
    pc[0] = 0;
    npc[0] = 0;
    ops[0] = 0;
    arg1[0] = 0;
    arg2[0] = 0;

    for (var j = 0; j < nReg; j++) {
        state[0][j] = 0;
    }

    for (var s = 1; s < nSteps; s++) {
        pc[s] = npc[s - 1]; // current pc = previous npc
        ops[s] = instructions[pc[s]]; // current op is instructions[pc]
        arg1[s] = args1[pc[s]]; // current arg1[step] is args1[pc]
        arg2[s] = args2[pc[s]]; // current arg2[ste] is args2[pc]

        isSet[s] = 0;
        isAdd[s] = 0;

        // copy all the previous values
        for (var j = 0; j < nReg; j++) {
            state[s][j] = state[s - 1][j];
        }

        if (ops[s] == SET) {
            state[s][arg1[s]] = arg2[s];
            npc[s] = pc[s] + 1;
            isSet[s] = 1;
        }
        if (ops[s] == ADD) {
            state[s][0] = state[s - 1][arg1[s]] + state[s - 1][arg2[s]];  
            npc[s] = pc[s] + 1;
            isAdd[s] = 1;
        }
    }

    // Arrays used for constraining state transitions
    signal output tisSet[nSteps];
    signal output tisAdd[nSteps];
    signal output tops[nSteps];
    signal output targ1[nSteps];
    signal output targ2[nSteps];
    signal output tpc[nSteps];
    signal output tnpc[nSteps];
    signal output tState[nSteps][nReg];

    // copy auxiliary state
    for (var s = 0; s < nSteps; s++) {
        if (s == 0) {
            tisSet[s] <-- 0;
            tisAdd[s] <-- 0;
            tops[s] <-- 0;
            targ1[s] <-- 0;
            targ2[s] <-- 0;
            tpc[s] <-- 0;
            tnpc[s] <-- 0;
        } else {
            tisSet[s] <-- isSet[s];
            tisAdd[s] <-- isAdd[s];
            tops[s] <-- ops[s];
            targ1[s] <-- arg1[s];
            targ2[s] <-- arg2[s];
            tpc[s] <-- pc[s];
            tnpc[s] <-- npc[s];
        }
    }

    // copy state to tstate
    for (var s = 0; s < nSteps; s++) {
        for (var r = 0; r < nReg; r++) {
            tState[s][r] <-- state[s][r];
        }
    }

    // constrain based on opcode
    component setOps[nSteps];
    component addOps[nSteps];
    for (var s = 1; s < nSteps; s++) {
        setOps[s] = SetOp(nReg);
        addOps[s] = AddOp(nReg);

        for (var j = 0; j < nReg; j++) {
            setOps[s].prev[j] <== tState[s - 1][j];
            setOps[s].curr[j] <== tState[s][j];
            addOps[s].prev[j] <== tState[s - 1][j];
            addOps[s].curr[j] <== tState[s][j];

        }
        setOps[s].reg <== targ1[s];
        setOps[s].val <== targ2[s];
        setOps[s].enabled <== tisSet[s];

        addOps[s].arg1 <== targ1[s];
        addOps[s].arg2 <== targ2[s];
        addOps[s].enabled <== tisAdd[s];
    }
}

component main = SaturdayVM(4,3,3);


/* INPUT = {
    "instructions": [1,1,2],
    "args1": [2,3,2],
    "args2": [10,11,3]
} */
```

//--------------------------------------------------------------------------------
//--------------------------------------------------------------------------------

Same as above but just cleaner and clearer.

```
template SaturdayVM (nReg, _nSteps, nInstrs) {
    // Account for step 0 at the initial state.
    var nSteps = _nSteps + 1;

    signal input instructions[nInstrs];
    signal input arg1s[nInstrs];
    signal input arg2s[nInstrs];

    var SET = 1;
    var ADD = 2;

    // For every step (state transition), we need to know what are our args,
    // opcodes, program counter, and the next program counter.
    // We also need to know, for each opcode, during each step, whether they
    // were executed or not (this is to use with `ForceEqualIfEnabled`)
    var states[nSteps][nReg];
    var sArg1[nSteps];
    var sArg2[nSteps];
    var sOpcode[nSteps];
    var sPC[nSteps];
    var sNPC[nSteps];
    var sIsSet[nSteps];
    var sIsAdd[nSteps];

    // The default (initial state) should be 0 for all registers.
    // The first step (step 0) should be 0 for other s (state) arrays because
    // there is no state change at the initial state.
    for (var reg = 0; reg < nReg; reg++) {
        states[0][reg] = 0;
    }
    sArg1[0] = 0;
    sArg2[0] = 0;
    sOpcode[0] = 0;
    sPC[0] = 0;
    sNPC[0] = 0;
    sIsSet[0] = 0;
    sIsAdd[0] = 0;

    // Execute state changes.
    // The PC for the current step should be the NPC from the previous step,
    // because NPC should be the next counter after execution. This also
    // means NPC gets updated after each execution, not PC.
    // The PC determines which instruction (and args) to use during each step,
    // while the NPC determine where to go next.
    for (var step = 1; step < nSteps; step++) {
        sPC[step] = sNPC[step - 1];
        sOpcode[step] = instructions[sPC[step]];
        sArg1[step] = arg1s[sPC[step]];
        sArg2[step] = arg2s[sPC[step]];

        // Only one of the following arrays will get updated each step;
        // updates only if the corresponding opcode is executed.
        sIsSet[step] = 0;
        sIsAdd[step] = 0;

        // Copy values from previous state to the current state.
        // Note that the current state will hold the result of the opcode.
        for (var reg = 0; reg < nReg; reg++) {
            states[step][reg] = states[step - 1][reg];
        }

        // SET reg val
        if (sOpcode[step] == SET) {
            states[step][sArg1[step]] = sArg2[step];
            sIsSet[step] = 1;
            sNPC[step] = sPC[step] + 1;
        }

        // ADD reg1 reg2
        // Note that ADD retrieves values already set in the given registers.
        // It writes the sum of values to register 0.
        if (sOpcode[step] == ADD) {
            states[step][0] = states[step-1][sArg1[step]] + states[step-1][sArg2[step]];
            sIsAdd[step] = 1;
            sNPC[step] = sPC[step] + 1;
        }
    }

    // Arrays for constraining state transitions
    signal output tStates[nSteps][nReg];
    signal output tArg1[nSteps];
    signal output tArg2[nSteps];
    signal output tOpcode[nSteps];
    signal output tPC[nSteps];
    signal output tNPC[nSteps];
    signal output tIsSet[nSteps];
    signal output tIsAdd[nSteps];

    // Copy states to tStates
    for (var step = 0; step < nSteps; step++) {
        for (var reg = 0; reg < nReg; reg++) {
            tStates[step][reg] <-- states[step][reg];
        }
    }

    // Copy s-arrays to t-arrays
    for (var step = 0; step < nSteps; step++) {
        tArg1[step] <-- sArg1[step];
        tArg2[step] <-- sArg2[step];
        tOpcode[step] <-- sOpcode[step];
        tPC[step] <-- sPC[step];
        tNPC[step] <-- sNPC[step];
        tIsSet[step] <-- sIsSet[step];
        tIsAdd[step] <-- sIsAdd[step];
    }

    // Constrain that the tStates has the default initial state, and that
    // all t-arrays have 0 as the initial value
    for (var reg = 0; reg < nReg; reg++) {
        tStates[0][reg] === 0;
    }
    tArg1[0] === 0;
    tArg2[0] === 0;
    tOpcode[0] === 0;
    tPC[0] === 0;
    tNPC[0] === 0;
    tIsSet[0] === 0;
    tIsAdd[0] === 0;

    // Constrain based on opcode
    component setOps[nSteps];
    component addOps[nSteps];

    // Constrain the state at each step, for every register
    for (var step = 1; step < nSteps; step++) {
        setOps[step] = SetOp(nReg);
        addOps[step] = AddOp(nReg);

        // SET reg val
        setOps[step].prev <== tStates[step - 1];
        setOps[step].curr <== tStates[step];
        setOps[step].reg <== tArg1[step];
        setOps[step].val <== tArg2[step];
        setOps[step].enabled <== tIsSet[step];

        // ADD reg1 reg2
        addOps[step].prev <== tStates[step - 1];
        addOps[step].curr <== tStates[step];
        addOps[step].reg1 <== tArg1[step];
        addOps[step].reg2 <== tArg2[step];
        addOps[step].enabled <== tIsAdd[step];
    }

}

component main = SaturdayVM(4, 3, 3);

/* INPUT = {
    "instructions": [1,1,2],
    "arg1s": [2,3,2],
    "arg2s": [10,11,3]
} */
```

//--------------------------------------------------------------------------------