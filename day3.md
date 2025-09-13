# Circom Day 3

Each hexadecimal character ranges from 0 - 9, then a to f.
With 0 = 0000, and f = 1111
Each hexadecimal character represents a 4 bit binary number: from 0000 - 1111. 
32 bits represent 8 hexadecimal characters
128 bits represent 32 hexadecimal characters
256 bits represent 64 hexadecinak characters
512 bits represent 128 hexadecimal characters

MD5 works in 32 bit chunks

What are the simplest cryptographic hash functions, simpler than MD5 (search chatgpt and can consider writing)

//-----------------------------------------------------

## Unstructured Recall

//----------------------------------------------------------------

`circomlib/bitify.circom`

```
template Example () {
    signal input x;
    signal output out[4];

    component n2b = Num2Bits(4);

    n2b.in <== x;

    for (var i = 0; i < n; i++) {
        out[i] <== n2b.out[i];
    }
}

component main = Example();

/* INPUT = {
    "x": 5
} */
```

Here, `out[0]` is the LSB. Also we can get an intuition because off numbers have the LSB as 1.

Num2Bits implicitly constrains the input to be less than 2^n where n is the number of bits.

//----------------------------------------------------------------

Write a template that encodes z = x & y into its binary representation, and convert the bits to the number.
```
template Some() {
    var n = 4;
    signal input x;
    signal input y;
    signal z[n];
    signal output out;

    component n2bX = Num2Bits(n);
    component n2bY = Num2Bits(n)

    n2bX.in <== x;
    n2bY.in <== y;

    for (var i = 0; i < n; i++) {
        z[i] <== n2bX.out[i] * n2bY.out[i];
    }

    component b2n = Bits2Num(n);

    for (var i = 0; i < n; i++) {
        b2n.in[i] <== z[i];
    }

    out <== b2n.out;
}
```

Note that in circom, if `out[n]` is an n-bit number, then `out[0]` is usually the LSB, and `out[n-1]` is the MSB.

//----------------------------------------------------------------

Addition and multiplication in 32 bits:
Max of 32 bits is: 2^(32) - 1;
If x and y are both 32 bits, then x + y will be 33 bits because it carries over 1 bit, and the past 32 bits become 0.

Overflow formula for addition: x + y % 2^32

//----------------------------------------------------------------

Noticing the last three bits when adding and multiplying 2 3-bit numbers:
Adding 2 3-bits could create a 4-bit number. To account overflow, the MSB gets discarded and the 
least 3 significant bits get preserved.
   011 (3)
+  110 (6)
= 1001 (9) -> Preserve 3 LSB -> 001 (1) [which is (3 + 6) % 2^3]

Its important to range check the two inputs (operands) to be sure they are 3 bits if we are actually
performing the addition of 2 3-bit numbers. Because adding 2 5-bit numbers could return the same result:
    10011 (19)
+   10110 (22)
=  101001 (41) -> Preserve 3 LSB -> 001 (1) [which is (19 + 22) % 2^3]

Thus its important to do a range check on the inputs (which Num2Bits does) to constraint the operands
to be 3 bits.

Multiplication of 2 32-bit numbers: 2^32 * 2^32, the result is 2^64 (a 64 bit number).
When we consider the overflow (constrain to 32 bits), we just take the least significant 32 bits.

1111 x 1111 => 100000000 (16 * 16 = 256, which is 2^4 * 2^4 = 2^8). It is also a 9-bit number.
With overflow it becomes 00000000 (0), which is correct because the largest possible number for
an 8 bit number is 255 (2^n - 1), so in an 8 bit constraint, 256 overflows to 0.

//----------------------------------------------------------------

`binsum` in circomlib

//----------------------------------------------------------------
```
var s;

for (var i = 0; i <n ;i ++) {
    ...
}
```
`var s` means symbolic variable.
`var i` in the loop is a scripting variable.

On Symbolic variables:
Symbolic variables cannot have more than one multiplication, they are signals that are unknown at 
compile time (placeholders) (or another way to look at it, variables that are assigned a value from a signal).
Symbolic variables holds either a single signal or a collection of signals that are added or multiplied together.
If a variable is never assigned a value from a signal, then it is not a symbolic variable.

//----------------------------------------------------------------

A good hash function follows a random distribution.

//----------------------------------------------------------------

Code a template that finds the inner product of two arrays:
template InnerProduct (n) {
    signal input in1[n];
    signal input in2[n];
    signal input expOut;
    signal output out;

    signal productArr[n];

    for (var i = 0; i < n; i++) {
        productArr[i] <== in1[i] * in2[i]; 
    }

    var s;

    for (var i = 0; i < n; i++) {
        s += productArr[i];
        log(s);
    }

    expOut === s;

    out <== expOut;
}

component main = InnerProduct(4);

/* INPUT = {
    "in1": [2, 4, 6, 8],
    "in2": [1, 2, 3, 4],
    "expOut": 60
} */

// expected output should be 2 + 8 + 18 + 32 = 60

//----------------------------------------------------------------

(optional) Code a very simple hash function, uses XOR, NOR, rotates, etc, has arrays for bitwise operations, rotation amounts etc.
Can consider working on this:
```
pragma circom 2.1.6;

include "circomlib/bitify.circom";

template XOR(n) {
    signal input in1[n];
    signal input in2[n];
    signal output out[n];

    for (var i = 0 ; i<n ; i++) {
        out[i] <== in1[i] + in2[i] - 2 * in1[i] * in2[i];
    }
}

template XNOR(n) {
    signal input in1[n];
    signal input in2[n];
    signal output out[n];

    for (var i = 0 ; i<n ; i++) {
        out[i] <== 1 - (in1[i] + in2[i] - 2 * in1[i] * in2[i]);
    }
}

template Rot(n, r) {
    signal input in[n];
    signal output out[n];

    for (var i = 0; i < n; i++) {
        out[i] <== in[(i + r) % n];
    }
}

template Crazy (n) {

    var k[2] = [13, 209];

    signal input in[n]; // 32-bit values
    signal output state[n + 1][32];

    var initState = 9812735;
    component n2b = Num2Bits(32);
    n2b.in <== initState;
    for (var j = 0; j < 32; j++) {
        state[0][j] <== n2b.out[j];
    }

    component XORs[n];
    component n2bs[n];
    for (var i = 1; i < n + 1; i++) {
        XORs[i - 1] = XOR(32);
        n2bs[i - 1] = Num2Bits(32);
        n2bs[i - 1].in <== k[i - 1];
        for (var j = 0; j < 32; j++) {
            XORs[i - 1].in1[j] <== state [i-1][j];
            XORs[i - 1].in2[j] <== n2bs[i - 1].out[j];
        }
        for (var j = 0; j < 32; j++) {
            state[i][j] <== XORs[i - 1].out[j];
        }
    }
}

component main = Crazy(2);

/* INPUT = {
    "in": [3,3]
} */
```

//----------------------------------------------------------------