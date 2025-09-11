# Circom Day 4

## Unstructured Recall

ZK Friendly hash functions are hashes that dont have bitwise operations in them.

No need to worry about overflow in finite fields (because it just mods back)

circomlib/mimc.circom
The signal t6 means x^6.

In mimc, it will be a problem if we hash(in + k). Because hash collisions can occur if
someone swaps k and in. i.e. hash(in + k) collides with hash(k + in).
In the code:
```
    var t;
    signal t2[nrounds];
    signal t4[nrounds];
    signal t6[nrounds];
    signal t7[nrounds-1];

    for (var i=0; i<nrounds; i++) {
        t = (i==0) ? k+x_in : k + t7[i-1] + c[i];
        t2[i] <== t*t;
        t4[i] <== t2[i]*t2[i];
        t6[i] <== t4[i]*t2[i];
        if (i<nrounds-1) {
            t7[i] <== t6[i]*t;
        } else {
            out <== t6[i]*t + k;
        }
    }
```
We dont just add k to the input and be done, but we add k to the STATE EVERY ROUND.
If its the first round, then we add k to the input. And then basically compute: t = (k + in)^7.
Then form the second round onwards, we compute (a new) t = k + (k + in)^7 + c. Note the middle term is t in the
previous round. And then compute t^7 again. And then in the final round, computes t^7 + k.

Poseidon uses square matrices, and depending on the size of the matrix, poseidon will select 
hard coded constants for specific sizes.
Also, Poseidon adds 1 to the input. (see: https://github.com/iden3/circomlib/blob/master/circuits/poseidon.circom#L67)
Because if the input is just 1, then there wont be any matrix multiplication, it will just be a
scalar multiplication of the matrix. Adding 1 enforces matrix multipication.

In Hash functions, we might see large arrays of random values. This is usually used for
deterministic randomness.

In mimc and poseidon, poseidon has less constraints so its preferred.

In the witness, anything that's public appears first. Thats why we often see "1" and "out"/"z" as
the first two elements in the witness.

*** Ask boss to go through nullifier in Tornado cash again (got lost).

Use snarkjs to deploy contract:
https://docs.circom.io/getting-started/compiling-circuits/
https://docs.circom.io/getting-started/computing-the-witness/
https://docs.circom.io/getting-started/proving-circuits/

To view a witness file, in the js directory of the circuit: `snarkjs wtns export json witness.wtns witness.json`

Schwartz zippel lemma.
Given polynomials f and g, if we pick a random x point, if f(r) != g(r), then it is with overwhelming probability
that the polynomials are not the same.
To compare if two arrays are the same very efficiently, more efficiently than O(n^2):
Given [a, b, c] and [c, a, b], concat all elements from both arrays and hash then hash the whole thing to get r,
then:
(a - r)(b - r)(c - r) === (c - r)(a - r)(b - r)

Permutation argument.

Conditional branching without if statement to branch if x is 7, out 4 else out 107:
(take one discard the other)
eqSeven <== IsEqual()([input, 7]);
out <== (1 - eqSeven) * 107 + (eqSeven) * 4;

In OR: x + y - xy, if we know x and y are exclusive, then we can just do: x + y

Quin selector, (aka linear scan)
It allows us to use a signal as an index for an array of signals.
See iterations exercises (Selector template).
Or: https://rareskills.io/post/quin-selector

The powers example, we can use a quin selector to compute the powers more efficiently
at compile time.

Powers of X
```
template Powers(n) {
    signal input x;
    signal input e;
    signal output out; // x**e

    assert(n > 0);

    signal powers[n];
    powers[0] <== 1;

    for (var i = 1 ...) {
        powers[i] <== powers[i - 1] * x;
    }

    component sel = Selector(n);
    for (var i = 0; ...) {
        sel.in[i] <== powers[i];
    }

    sel.idx <== e;
    out <== sel.out
}
```