import galois
import numpy as np

# For the following problems, assume that in our finite field,
# the field modulus is p = 71.
p = 71

# Helper functions
def mat_det_2x2(A):
    a = np.asarray(A)
    if a.shape != (2, 2):
        raise ValueError("Matrix must be 2x2")
    return (a[0][0] * a[1][1]) - (a[0][1] * a[1][0])    

def mat_adjugate_2x2(A):
    a = np.asarray(A)
    return np.matrix([[a[1][1], -a[0][1]],
                      [-a[1][0], a[0][0]]])

# --------------------------------------------------

# Problem 1
# Find the elements in the finite field that are congruent to the
# following values:
# a) -1
# b) -4
# c) -160
# d) 500
print("Problem 1:")
a1 = -1 % p
b1 = -4 % p
c1 = -160 % p
d1 = 500 % p
print(a1)   # 70 (the field element (p - 1) is always congruent to -1)
print(b1)   # 67
print(c1)   # 53
print(d1)   # 3
print()

# --------------------------------------------------

# Problem 2
# Find the elements in the finite field that are congruent to the
# following values:
# a) 5/6
# b) 11/12
# c) 21/12
# Verify by checking that a + b = c (mod p)
# [Note that the modular inverse of x is: pow(x, -1, p)]
print("Problem 2:")
a2 = 5 * pow(6, -1, p)
b2 = 11 * pow(12, -1, p)
c2 = 21 * pow(12, -1, p)
print(a2)   # 60
print(b2)   # 66
print(c2)   # 126
assert (a2 + b2) % p == c2 % p
print()

# --------------------------------------------------

# Problem 3
# Find the field elements that are congruent to the following:
# a) 2/3
# b) 1/2
# c) 1/3
# Verify by checking a * b = c (mod p)
print("Problem 3:")
a3 = 2 * pow(3, -1, p)
b3 = pow(2, -1, p)
c3 = pow(3, -1, p)
print(a3)   # 48
print(b3)   # 36
print(c3)   # 24
assert (a3 * b3) % p == c3 % p
print()

# --------------------------------------------------

# Problem 4
# Compute the inverse of the following matrix in the finite field:
# A = [[1, 1],
#     [1, 4]]
# Verify by checking that: A * A^-1 = I (Identity matrix)
#
# [FYI, explicitly its: A * (Adjugate(A)/det(A)) = I, where (Adjugate(A)/det(A) is A^-1)]
#
# [The trick here is to first convert the matrix to its finite field equivalent.
# Reason is simply, an actually invertible matrix (where det != 0) could have
# its det = 7, but if we attempt to invert first and then convert to a finite
# field equivalent, if p = 7, then its det = 0 which makes its seem not invertible.]
print("Problem 4:")
A = np.matrix([[1, 1],
               [1, 4]])
I = np.matrix([[1, 0],
               [0, 1]])

A_ff = A % p
adjugate_A_ff = mat_adjugate_2x2(A) % p
determinant_A_ff = int(mat_det_2x2(A) % p)
A_ff_inv = (pow(determinant_A_ff, -1, p) * adjugate_A_ff) % p
print(A_ff)
print(A_ff_inv)

product = np.matmul(A_ff, A_ff_inv) % p
print(product)
assert np.array_equal(product, I)
print()

# --------------------------------------------------

# Problem 5
# What is the modular square root of 12
# Verify your answer by checking that x * x = 12 (mod 71)
# Use brute force
# [We want to find x, such that x^2 mod p = 12]
print("Problem 5:")
field_elements_w_roots = set()
for i in range(0, p):
    field_elements_w_roots.add(i * i % p)

print(field_elements_w_roots)

first_sqrt = None
for i in field_elements_w_roots:
    if i * i % p == 12:
        first_sqrt = i

# Since p is in the form 4k + 3, we can find the first modular sqrt by:
def mod_sqrt(x, p):
    assert (p - 3) % 4 == 0, "prime not 4k + 3"
    exponent = (p + 1) // 4
    return pow(x, exponent, p) # x ^ e % p

print(first_sqrt)   # 15
assert (first_sqrt, mod_sqrt(12, p))

# Just like regular sqrt, there should be two solutions for each field element
# except for 0, which only has 0 as the sqrt.
# The second squart root is the additive inverse ( p - a )
second_sqrt = p - first_sqrt
print(second_sqrt)  # 56
assert (second_sqrt * second_sqrt % p, 12)
print()

# --------------------------------------------------

# Problem 6
# Use the galois library.
# Suppose we have: p(x) = 52x^2 + 24x + 61
#                  q(x) = 40x^2 + 40x + 58
# Find: p(x) + q(x)
#       p(x)q(x)
# 
# Also find the roots of: p(x), q(x), p(x)q(x)
print("Problem 6:")
GF71 = galois.GF(p)
px = galois.Poly([52, 24, 61], GF71)
qx = galois.Poly([40, 40, 58], GF71)

px_plus_qx = px + qx
print(px_plus_qx)   # 21x^2 + 64x + 48

pxqx = px * qx
print(pxqx) # 21x^4 + 58x^3 + 26x^2 + 69x + 59

px_roots = px.roots(True)
print(px_roots) # x = 34, 42

qx_roots = qx.roots(True)
print(qx_roots) # No roots

pxqx_roots = pxqx.roots(True)
print(pxqx_roots)   # x = 34, 42
print()
# We can also tell by the union of roots of the product polynomial,
# that the roots of pxqx is the union of the roots of px and qx.

# --------------------------------------------------

# Problem 7
# Find a polynomial f(x) that crosses the points (10, 15), (23, 29).
# Since these are two points, the polynomial will be of degree 1 and be the 
# equation for a line (y = ax + b).
# Verify your answer by checking that f(10) = 15 and f(23) = 29.
print("Problem 7:")
xs = GF71([10, 23])
ys = GF71([15, 29])
a = (ys[1] - ys[0]) / (xs[1] - xs[0])
b = ys[0] - (a * xs[0])
fx = galois.Poly([a, b], GF71)
print(fx)   # 12x + 37

assert fx(xs[0]) == ys[0]
assert fx(xs[1]) == ys[1]
print()

# --------------------------------------------------

# Problem 8
# What is Lagrange Interpolation and what does it do?
# Find a polynomial that crosses through the points (0, 1), (1, 2), (2, 1).
# Use this Stackoverflow answer as a starting point: https://stackoverflow.com/a/73434775
#
# Lagrange interpolation guarantees, over a set of n points, a unique single lowest-degree 
# polynomial of at most degree (n - 1) that passes through all those points.
print("Problem 8:")
x_vals = GF71(np.array([0, 1, 2]))
y_vals = GF71(np.array([1, 2, 1]))
lagrange_poly = galois.lagrange_poly(x_vals, y_vals)
print(lagrange_poly)    # 70x^2 + 2x + 1

y_res = lagrange_poly(x_vals)
print(y_res)    # [1, 2, 1]