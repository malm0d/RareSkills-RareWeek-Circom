# Circom Day 5

## Unstructured Recall
//----------------------------------------------------------------

`merkleTree.circom::DualMux`
https://github.com/tornadocash/tornado-core/blob/master/circuits/merkleTree.circom#L18
This is like a conditional swap.
`s` means to reverse (swap) or not. `s` is constrained to 1 or 0.
We need to use this because in a Merkle Tree, when hashing a leaf with its sibling,
our leaf could be on either the left or right. So DualMux helps to solve this by
allow `s` to specify `0` for the left, and `1` for the right.
```
// if s == 0 returns [in[0], in[1]]
// if s == 1 returns [in[1], in[0]]
template DualMux() {
    signal input in[2];
    signal input s;
    signal output out[2];

    s * (1 - s) === 0
    out[0] <== (in[1] - in[0])*s + in[0];
    out[1] <== (in[0] - in[1])*s + in[1];
}
```
When s = 0, `out[0]` returns `in[0]`, and `out[1]` returns `in[1]` (no swap).
```
out[0] <== (in[1] - in[0]) * 0 + in[0] = 0 + in[0] = in[0]
out[1] <== (in[0] - in[1]) * 0 + in[1] = 0 + in[1] = in[1]
```
When s = 1, `out[0]` returns `in[1]`, and `out[1]` returns `in[0]` (swap).
```
out[0] <== (in[1] - in[0]) * 1 + in[0] = in[1] - in[0] + in[0] = in[1]
out[1] <== (in[0] - in[1]) * 1 + in[1] = in[0] - in[1] + in[1] = in[0]
```

//----------------------------------------------------------------

`merkleTree.circom::HashLeftRight`
https://github.com/tornadocash/tornado-core/blob/master/circuits/merkleTree.circom#L4
This basically just computes the Mimc hash.
The `left` represents
```
// Computes MiMC([left, right])
template HashLeftRight() {
    signal input left;
    signal input right;
    signal output hash;

    component hasher = MiMCSponge(2, 1);
    hasher.ins[0] <== left;
    hasher.ins[1] <== right;
    hasher.k <== 0;
    hash <== hasher.outs[0];
}
```

//----------------------------------------------------------------

`merkleTree.circom::MerkleTreeChecker`
https://github.com/tornadocash/tornado-core/blob/master/circuits/merkleTree.circom#L30
Note that in line 41, `hashers[i - 1]`
Something about the leaf and roots.
```
selectors[i].in[0] <== i == 0 ? leaf : hashers[i - 1].hash;
```
This handles the first level vs subsequent levels:
-> Level 0 (i == 0): Use the original leaf as input.
-> Level 1+ (i > 0): Use the hash from the previous level (i - 1).
The circuit builds the tree bottom-up, so each level needs the result from the level below it.
And in:
```
root === hashers[levels - 1].hash;
```
This accesses the last hasher in the array:
-> Arrays are 0-indexed: hashers[0], hashers[1], ..., hashers[levels-1]
-> For levels = 3: valid indices are 0, 1, 2
-> The final hash (root) comes from hashers[2] = hashers[levels-1]

//----------------------------------------------------------------

`withdraw`
https://github.com/tornadocash/tornado-core/blob/master/circuits/withdraw.circom#L29
First checks whether you really know the secret,
then checks whether your hash is really in the tree

//----------------------------------------------------------------

In newer versions of circom, there is no more `private` keyword. Everything is defaulted
to being private. Public inputs are declared in `main` in curly braces.

//----------------------------------------------------------------

`Num2Bits`
Circom `<--` operator
"Non-deterministic signal` or `advise signal`

//----------------------------------------------------------------

Mod is allowed in circom
```
mod <-- num % denom;
```

//----------------------------------------------------------------

Add the necessary constraints to the Mod and sqrt examples:
```circom
pragma circom 2.1.6;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";

template ModConstraints() {
    signal input num;
    signal input den;
    signal output out;
    signal output mod; //remainder

    // Important part:
    // Inputs and outputs should be range-constrained to 32 bits.
    // This will constraint `num === den * out + mod;` to not overflow.
    // Because `num` could be 32 bits, `den` could be 32 bits, but 
    // `(den * out) + mod` could result in an overflow to more than 32 bits.
    // This also forces that for any `num` and `den`, there is only one pair of
    // `out` and `mod` that will satisfy the constraints. (Fundamental
    // theorem of division every integer division has a unique quotient 
    // and remainder)

    // denominator cannot be zero
    component isZero = IsZero();
    isZero.in <== den;
    0 === isZero.out;

    out <-- num \ den;
    mod <-- num % den;

    // mod is less than den
    // e.g: 5 / 4, remainder = 1. The remainder `mod` cannot
    // be more than the denominator
    component ltDen = LessThan(252);
    ltDen.in[0] <== mod;
    ltDen.in[1] <== den;
    1 === ltDen.out;

    // And others like:
    // out * den <= num
    // (out + 1) * den >= num

    // should get back the original number
    num === den * out + mod;
}


component main = ModConstraints();
```

```circom
pragma circom 2.1.6;

include "circomlib/comparators.circom";
// include "https://github.com/0xPARC/circom-secp256k1/blob/master/circuits/bigint.circom";

function sqrt(y) {
    var z;
    if (y > 3) {
        z = y;
        var x = y \ 2 + 1;
        while (x < z) {
            z = x;
            x = (y \ x + x) \ 2;
        }
    } else if (y != 0) {
        z = 1;
    }
    return z;
}

//How can we constrain that sqrtX is indeed the sq root of x
//sqrt10 = 9
template Example() {
    signal input x;
    signal input sqrtX;

    component gteZero = GreaterEqThan(252);
    gteZero.in[0] <== x;
    gteZero.in[1] <== 0;
    1 === gteZero.out;

    component isZeroX = IsZero();
    component isZeroSqrtX = IsZero();
    isZeroX.in <== x;
    isZeroSqrtX.in <== x;
    0 === isZeroX.out + isZeroSqrtX.out;

    signal isEqOneX <== IsEqual()([x, 1]);
    signal isEqOneSqrtX <== IsEqual()([x, 1]);
    0 === isEqOneX - isEqOneSqrtX;

    signal lte <== LessEqThan(252)([sqrtX, x]);
    1 === lte;

    // (sqrtX + 1) * (sqrtX + 1) > x
    // sqrtX * sqrtX + (x % sqrtX) === x
}

component main = Example();
```

//----------------------------------------------------------------

AliasCheck
Alias means congruence.
`in[254]` represents all the bits that circom can handle.
CompConstant -> Does the binary number fit in the field.
See "Alias bug".

//----------------------------------------------------------------

In the hack demo, in the first instance we changed 5 to 50, how come it still passed the constraint
since z <-- x * y, then a * b === z? Wouldnt it still violate the constraint?
```
signal z <-- x * y;
a * b === z;
```
Here, there is nothing that constraints what z is, and x and y can be anything.
Ultimately the product of a and b must still be z. Without constraining z, this means 
someone could maliciously change x and y, and so long as the result satisfies
the constrain a * b == z, then x and y can be changed to anything and that would go
undetected. This is a vulnerability.

Hack demo related resource
https://rareskills.io/post/underconstrained-circom

//----------------------------------------------------------------

ZKVMs
THe constraint is everything must be equal between the new and previous state, excpet
the register of which we changed the value inside.

circomlib/comparators::ForceEqualIfEnabled

IN ZKVms we write to register 0 most of the time because enabling the flexibility requries
more quin selectors, which introduces more constraints.

two shuffles make a ram:
https://eprint.iacr.org/2023/1115

