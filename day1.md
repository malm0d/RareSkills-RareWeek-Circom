# Circom Day 1 

## Finite Fields and Aritmetic Circuit

For exercises, refer to: zk-constraint-exercises-q

## Unstructured Recall

The definition of modulo is: a = qn + r. For a is some regular integer, n is the field modulus (> 0),
q is the quotient, and r is the remainder. And 0 <= r < n. And r is the output of the modulo.
Eg: 17 % 5 ==> 17 mod 5 ==> 17 = 3(5) + 2 ==> 2


If the field modolus is prime, then every element (including 0) has an additive inverse; and every element has a multiplicative inverse (except 0).

The second modular square root is the additive inverse.

In a finite field, p - 1 is congruent to -1

The size of the proof in a ZK circuit is << n, where n is the number of variables

Testing that a signal is binary is simply: x(x-1) = 0

x(x-1) = 0 is the same as x(1-x) = 0

If we have a set, for example, { 21, 22 }, we can simply take (x - 21)(x - 22) = 0 to constrain it.

System of equations == arithmetic circuit

All boolean ciruits can be represented as arithmetic circuit

There is no <, <=, or >= or > in arithmetic circuits

We can easily identify a binary number to be even or odd by looking at the least significant bit

Write out truth tables: XOR, AND, OR, NAND, NOT

AND
x y z
0 0 0
1 0 0
0 1 0
1 1 1

OR
x y z
0 0 0
1 0 1
0 1 1
1 1 1

NAND
x y z
0 0 1
1 0 1
0 1 1
1 1 0

NOR
x y z
0 0 1
1 0 0
0 1 0
1 1 0

XOR
x y z
0 0 0
1 0 1
0 1 1
1 1 0

NOT
x y
1 0
0 1

z = x && y
Is:
x * y === 0
x(x-1) = 0
y(y-1) = 0

z != x
z = 1 - x
x(x - 1) = 0

z = x || y
x + y - xy = z
x(x-1) = 0
y(y-1) = 0

z = !(x && y)
z = 1 - xy
x(x-1) = 0
y(y-1) = 0

z = x XOR y
x + y - 2xy = z

z = !(x || y)
1 - x - y + xy = z
This is the same as: 1 - (x + y - xy) = z

In: z = x * y
z(z-1) = 0
x(x-1) = 0
If we constrain z and x to boolean values, then y is implicit that it needs to be boolean
otherwise the circuit wont be satisfied

Use zkrepl.dev for a remix like IDE for circom

//------------------
```circom
template AND (n) {
    signal input x[n];
    signal input y[n];
    signal input z[n];

    for (var i = 0; i < n; i++) {
        x[i] * (x[i] - 1) === 0;
        y[i] * (y[i] - 1) === 0;
        
        z[i] === x[i] * y[i];
    }
}

component main = AND(4);

/* INPUT = {"x": [1, 0, 1, 0], "y": [1, 1, 0, 0], "z": [1, 0, 0, 0]}
*/
```
//------------------

The compiler unrolls the dynamic constraints in the loop to static constraints.

The length of the array must be known during compilation, as is when we deal with arithmetic circuits.
If the length of the array is not known during compile time, the it wont compile.
Similarly, in an if statement if we try to assert something like an element at an index
and its not known during compile time, it wont compile.

Circom in general requires things to be known at compile time. For example if we do:
```circom
template Bad(n) {
    signal input x;

    if (x == 1) {
        signal input a[n];
    } else {
        signal input b[n];
    }
}

component main = Bad(2);
```

Or:

```
template DoesNotCompile (n) {
    signal input a[n];
    signal input b[n];
    signal input c[n];

    signal j;

    for (var i = 0; i < j; i++) {
        a[i] * (a[i] - 1) === 0;
        b[i] * (b[i] - 1) === 0;
        c[i] * (c[i] - 1) === 0;

        a[i] + b[i] - (2 * a[i] * b[i]) === c[i];
    }
}

component main = DoesNotCompile(2);
/*
INPUT = {"a": [1, 0], "b": [0, 1], "c": [1, 1]}
*/
```

These two will not compile because `x` and `j` are not known at compile time.

Linear constraints vs non-linear constraints
Linear constraints means signals involved in linear combination (no mulitplication of variables)
Non-linear constraints means signals that are multiplication of variables.

Use `log(...)` to help debug