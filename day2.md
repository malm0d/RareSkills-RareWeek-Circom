# Circom Day 2

For exercises, refer to: non-quadratic-constraints-e, interval-constraints-e, and array-permutations-e.

## Unstructured Recall

In circom, only 1 multiplication per constraint because of bilinear paring in the algorithm down the line

So you cant even do something like: x * x === y * y

Surprisingly:  0 === x * (x - y) works to enforce: x^2 - xy = 0 in a single statement.

"<==" is scripting language in runtime. (runtime equals)

Intermediate variables need to be signals because they are part witness

Anything part of the scripting language is not part of the zk proof, so signals indicate
a variable is part of the witness

If we have:
```
    signal input x;
    signal input y;
    signal intermediate;

    intermediate <== x * x
```
Circom calculates and appends "intermediate" to the input JSON:
```
INPUT: { "x": 2, "intermediate": 4, "y": some}
```
In the above if we put `input` for `intermediate`, then we must be explicit with the input in the JSON.

"output" is shorthand for ...

Code a powers function `XtoN` (a template in circom)
```
    signal powers[n];
    powers[0] <==x;
    for (var = 1; i < n; i++) {
        powers[i] <== x * powers[i - 1];
    }

    out <== powers[n-1];
```
Syntax for importing libraries (this is in zkrepl.dev but similar in other envs):
`include "circomlib/gates.circom";`
`include circomlib/comparators.circom;`

We should always constrain the output of a template, because most dont do this, esp for boolean constraints.
e.g. if we use LessThan() and put:
```
component lt = LessThan(252);
lt.in[0] <== 2;
lt.in[1] <== 1

1 === lt.out;
```
If we do not include the last statement, this will pass without any error even though it is incorrect.
We treat the output as boolean True or False, so when we constrain the output to 1, we are
asserting that the first input must be less than the second input.

Watchout for the "IsEqual" library template: this will not throw an assertion error as it just 
returns boolean - like how a regular function would.
Use "===" to constrain the output of "IsEqual" so that it will throw an error if the assertion fails.
E.g:
```
    signal x <== IsEqual()[1, 1];
    x === 1; // enforces that the result of IsEqual must be true otherwise throw error in circuit
```

We can use the dot notation to access signals from templates,
E.g: `MyTemplate.in <== 1;`, `MyTemplate.inArray[0] <== 1;`, `MyTemplate.out === 1`; `

Or do it inline:
`signal lt <== LessThan(5)([x,0]);`
But note that this syntax has to be a signal assignment.

When we have a component, you cant reassign the state in it. Thus if we are reusing templates,
its best to use the inline notation, example:
```
    signal isLtZero <== LessThan(252)([x, 0]);
    signal isGtTwenty <== GreaterThan(252)([x, 20]);
```
Because we cannot do this:
```
    component lt = LessThan(252);
    lt.in <== [1, 2];
    lt.out === 1;
    ...
    lt.in <== [3, 2]; // this is not allowed
```

In the circomlib library, most templates require you to specifiy the number of bits; we can just use 252 bits
which will cover most numbers. 252 bits is also the max.

Can use assert statement to assert values -> the compiler does not create any constraints for this

Reverse an array:
```
template Reverse(n) {
    signal input in[n];
    signal output out[n];

    for (var i = 0; i < n; i ++) {
        out[n - i - 1] <== in[i];
    }
}
```
Rotate left: [1, 2, 3, 4] ->(by 2)-> [3, 4, 1, 2]
```
    for (var i = 0; i < n; i++) {
        out[i] <== in[(i + r) % n];
    }
```
Rotate right: [1, 2, 3] ->(by 1)-> [3, 1, 2]
```
    for (var i = 0; i < n; i++) {
        out[i] <== in[(i - r + n) % n];
    }
```

In the example of writing a circuit that constrains x to be the cube root of z.
We technically cant compute z^(1/3). The limitation of circom is that our operations are simple,
such as regular arithmetic. Besides constraining it such as:
```
    signal x_squared <== x * x;
    z === x_squared * x;
```
What we can do is to compute an "advise" (which occurs only in scripting), and then
we write some constrain(s) to ensure that our advise is accurate.

An advise is denoted by "<--", its like a signal assignment but the compiler doesnt create a constraint
for it (as is for all scripting language in circom), unlike if we used "<==".

An advise is considered "external" / "from outside".

For example, say we have to take 100 / 9. We know that this would be 11 plus r = 1, so we approach this by
computing an intermediate signal such as:
```
template Advise() {
    signal input x;
    signal itm;

    itm <-- x * 9;
    0 === itm + 1;
}
```

Or, if we looked at `Num2Bits` in `circomlib/circuits/bitify.circom`:
```
template Num2Bits(n) {
    signal input in;
    signal output out[n];
    var lc1=0;

    var e2=1;
    for (var i = 0; i<n; i++) {
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] -1 ) === 0;
        lc1 += out[i] * e2;
        e2 = e2+e2;
    }

    lc1 === in;
}
```
In:
```
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] -1 ) === 0;
```
The first line is an advise, which is extracting the i-th bit of the input and assigning it to `out[i]`
WITHOUT generating a constraint.
- `in >> i` shifts right by `i` bits
- Eg: if `in` is 13 (1101) and `i` is 2, then `1101 >> 2 = 0011` (which is 3)
- And then `& 1` is just extracting the LSB: `0011 & 1 = 0001`
- And if we run this with `13` as the input, then `out[0] = (13 >> 0) = 1`, `out[1] = (13 >> 1) = 0`,
  `out[2] = (13 >> 2) = 1`, and `out[3] = (13 >> 3) = 1`.
Then the second line is essentially CONTRAINING that each value in out must be 0 or 1.

Also in:
```
template IsZero() {
    signal input in;
    signal output out;

    signal inv;

    inv <-- in!=0 ? 1/in : 0;

    out <== -in*inv +1;
    in*out === 0;
}
```
`inv` is a signal (part of the witness) but is assigned using an advise so it is not constrained.
Also, we cannot directly constrain `inv` because division is not allowed in constraints.
Thus, the template here indirectly constrains `inv` by linking it in the computation of `out`;
because by constraining `in * out === 0`, this enforces if `in` is 0 then `out` must be 1, and 
if `in` is not 0 then `out` must be 0. And this would only work if `inv` is given a correct value.