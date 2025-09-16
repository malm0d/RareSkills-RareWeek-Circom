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


Why do we need forceEnabled?

//----------------------------------------

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

template AddOp(nReg) {
    signal input prev[nReg]; // states
    signal input curr[nReg];

    signal input arg1; // arg for first register
    signal input arg2; // arg for second register

    signal input enabled; //to compare or not

    component eqs1[nReg];
    component eqs2[nReg];
    component feqs[nReg];

    // In an ADD op, only register 0 changes.
    // This compares all registers except register 0.
    for (var i = 1; i < nReg; i++) {
        feqs[i] = ForceEqualIfEnabled();
        feqs[i].in[0] <== prev[i];
        feqs[i].in[1] <== curr[i];
        feqs[i].enabled <== enabled;
    }

    component s1 = Select(nReg);
    component s2 = Select(nReg);

    for (var i = 0; i < nReg; i++) {
        s1.in[i] <== prev[i];
        s2.in[i] <== prev[i];
    }

    // Index from the prev state the registers used for ADD.
    // The output should be the value of the registers.
    s1.index <== arg1;
    s2.index <== arg2;

    // Constraint the addition of the values of the registers in the prev
    // state to be equal to the value in register 0 in the current state.
    feqs[0] = ForceEqualIfEnabled();
    feqs[0].in[0] <== curr[0];
    feqs[0].in[1] <== s1.out + s2.out;
    feqs[0].enabled <== enabled;
}

// If the index matches the register, then z[i] will be the value, and eqs[i].out
// will be 1. Then in `prev[i] * (1 - eqs[i].out) + z[i];`, this makes the value z[i].
// `enabled` will not be on when we are comparing an updated register.
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

        z[i] <== val * eqs[i].out;
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

template SaturdayVM(nReg, _nSteps, nInstr) {
    var nSteps = _nSteps + 1;
    var SET = 1;
    var ADD = 2;
    signal input instructions[nInstr];
    signal input args1[nInstr];
    signal input args2[nInstr];

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

