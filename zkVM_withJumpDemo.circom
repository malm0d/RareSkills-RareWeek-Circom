// Demo WITH JUMP in VM. RUN in zkrepl.dev

pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/comparators.circom";

template QuinSelector(n) {
    signal input in[n];
    signal input index;
    signal output out;
    
    component isEqual[n];
    signal products[n];
    signal partialSums[n];
    
    for (var k = 0; k < n; k++) {
        isEqual[k] = IsEqual();
        isEqual[k].in[0] <== index;
        isEqual[k].in[1] <== k;
        products[k] <== in[k] * isEqual[k].out;
    }
    
    partialSums[0] <== products[0];
    for (var k = 1; k < n; k++) {
        partialSums[k] <== partialSums[k-1] + products[k];
    }
    
    out <== partialSums[n-1];
}

/*
program = INC DEC JMP

trace   1   0   0   1
pcs     0   1   2   0 
ins   INC DEC JMP INC
next    1   2   0   1 
*/

template A(nIns, nSteps) {
    signal input program[nIns];
    signal output trace[nSteps];
    signal output pc[nSteps];
    signal output ins[nSteps];
    signal output pcNext[nSteps];

    var INC = 1;
    var DEC = 2;
    var JMP = 3;

    var traceV[nSteps]; // trace of computation (claimed)
    var pcsV[nSteps];  // program counter at each step
    var insV[nSteps];  // claimed instruction at step (i.e. program[pcC[step]])
    var pcNextV[nSteps]; // pc for the next instruction 

    traceV[0] = 0;
    pcsV[0] = 0;
    insV[0] = program[0];
    pcsV[0] = 0;
    insV[0] = program[0];
    if (program[0] == INC) {
        traceV[0] = 1;
    }
    if (program[0] == DEC) {
        traceV[0] = -1;
    }
    if (program[0] == JMP) {
        traceV[0] = 0;
    }
    if (program[0] == INC || program[0] == DEC) {
        pcNextV[0] = 1;
    } else {
        pcNextV[0] = traceV[0];
    }
    for (var s = 1; s < nSteps; s++) {
        pcsV[s] = pcNextV[s - 1];
        insV[s] = program[pcsV[s]];

        if (insV[s] == INC) {
            traceV[s] = traceV[s - 1] + 1;
            pcNextV[s] = pcsV[s] + 1;
        }
        if (insV[s] == DEC) {
            traceV[s] = traceV[s - 1] - 1;
            pcNextV[s] = pcsV[s] + 1;
        }
        if (insV[s] == JMP) {
            traceV[s] = traceV[s - 1];
            pcNextV[s] = traceV[s];
        }

    }

    for (var s = 0; s < nSteps; s++) {
        trace[s] <-- traceV[s];
        pc[s] <-- pcsV[s];
        ins[s] <-- insV[s];
        pcNext[s] <-- pcNextV[s];
    }

    // constrain that pc starts at 0
    pc[0] === 0;

    // constrain that
    // if
    //   instruction[0] = INC -> trace[0] = 1 AND pcNext[s] == 1
    //   instruction[0] = DEC -> trace[0] = -1 AND pcNext[s] == 1
    //   instruction[0] = JMP -> trace[0] = 0 AND pcNext[s] == 0

    // constrain that at each step 1 and later, pcNext[s - 1] === pc[s]

    // constrain that at each step program[pc] === instruction

    // constrain that at each step
    // if
    //   instruction[s] = INC -> trace[s] = trace[s - 1] + 1 AND pcNext[s] == pc[s] + 1
    //   instruction[s] = DEC -> trace[s] = trace[s - 1] - 1 AND pcNext[s] == pc[s] + 1
    //   instruction[s] = JMP -> trace[s] = trace[s - 1] AND pcNext[s] == trace[s]
    
    // create boolean conditions for each instruction type at each step
    component isINC[nSteps];
    component isDEC[nSteps];
    component isJMP[nSteps];
    
    // create quin selectors for program lookup
    component programSelector[nSteps];
    
    // intermediate signals for quadratic constraints
    signal incDecNext[nSteps];
    signal jmpNext[nSteps];
    
    for (var s = 0; s < nSteps; s++) {
        // use quin selector to get program[pc[s]]
        programSelector[s] = QuinSelector(nIns);
        programSelector[s].in <== program;
        programSelector[s].index <== pc[s];
        
        // constrain that instruction at step s matches program[pc[s]]
        ins[s] === programSelector[s].out;
        
        // create boolean conditions
        isINC[s] = IsEqual();
        isINC[s].in[0] <== ins[s];
        isINC[s].in[1] <== INC;
        
        isDEC[s] = IsEqual();
        isDEC[s].in[0] <== ins[s];
        isDEC[s].in[1] <== DEC;
        
        isJMP[s] = IsEqual();
        isJMP[s].in[0] <== ins[s];
        isJMP[s].in[1] <== JMP;
        
        // constrain trace based on instruction type
        if (s == 0) {
            // initial trace: 0 + 1*isINC - 1*isDEC + 0*isJMP
            trace[s] === isINC[s].out - isDEC[s].out;
        } else {
            // trace[s] = trace[s-1] + 1*isINC - 1*isDEC + 0*isJMP
            trace[s] === trace[s - 1] + isINC[s].out - isDEC[s].out;
            
            // constrain that pcNext[s-1] === pc[s]
            pcNext[s - 1] === pc[s];
        }
        
        // constrain pcNext based on instruction type using intermediate signals
        // if INC or DEC: pcNext = pc + 1, if JMP: pcNext = trace
        incDecNext[s] <-- (isINC[s].out + isDEC[s].out) * (pc[s] + 1);
        jmpNext[s] <-- isJMP[s].out * trace[s];
        pcNext[s] === incDecNext[s] + jmpNext[s];
    }
}

component main = A(3, 8);