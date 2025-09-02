#### 1. Write an system of equations (arithmetic circuit) that is satisfied if and only if x is 0 or 1
```math
x(x-1) = 0
```
#### 2. Write an system of equations (arithmetic circuit) that is satisfied if and only if x is 7 or 12
```math
(x-7)(x-12) = 0
```

#### 3. Write a system of equations (arithmetic circuit) that is satisfied if and only if x1, x2, x3, and x4 are all 0 or 1
Strictly if $(x_1, x_2, x_3, x_4) = (0, 0, 0, 0) \text{ or } (1, 1, 1, 1)$:
```math
\begin{align*}
x_1(x_1 - 1) &= 0 \\
x_1 - x_2 &= 0 \\
x_1 - x_3 &= 0 \\
x_1 - x_4 &= 0 \\
\end{align*}
```

Otherwise, simply:
```math
\begin{align*}
x_1(x_1 - 1) = 0 \\
x_2(x_2 - 1) = 0 \\
x_3(x_3 - 1) = 0 \\
x_4(x_4 - 1) = 0 \\
\end{align*}
```

#### 4. Write a system of equations (arithmetic circuit) that is satisfied if and only if x1, x2, x3, and x4 are all 1
```math
\begin{align*}
x_1 - 1 &= 0 \\
x_2 - 1 &= 0 \\
x_3 - 1 &= 0 \\
x_4 - 1 &= 0 \\
\end{align*}
```

#### 5. Write a system of equations (arithmetic circuit) that is satisfied if and only if x1, x2, x3, and x4 are all 0
```math
\begin{align*}
1 - x_1 = 1 \\
1 - x_2 = 1 \\
1 - x_3 = 1 \\
1 - x_4 = 1 \\
\end{align*}
```

#### 6. Write a system of equations (arithmetic circuit) that is satisfied if and only if at least one of x1, x2, x3, and x4 is 0
```math
x_1x_2x_3x_4 = 0
```

#### 7. Write a system of equations (arithmetic circuit) that is satisfied if and only if at least one of x1, x2, x3, and x4 equals 0. The other variables can have any value

#### 8. Write an arithmetic circuit that constrains x and y to both be 0 or 1. If x is 0, then y must be 1, and vice versa.

#### 9. Write an arithmetic circuit that constrains x and y to be 0 or 1. Furthermore, z is constrained to be the binary OR of x and y.

#### 10. Write an arithmetic circuit that constrains x1, x2, x3, x4 to all be 0 or 1. Then constrain x1, x2, x3, x4 to be the binary representation of z.

#### 11. Write an arithmetic circuit that constrains x to be in the set {3, 6, 9, 10}

#### 12. Write an arithmetic circuit that constrains x to be in the set {5, 6, 9, 10} and y to be in the set {5, 6, 9, 10} and that the sum of x and y must be 15

#### 13. Write an arithmetic circuit that constrains x to be in the set {5, 6, 9, 10} and y to be in the set {5, 6, 9, 10} and that the sum of x and y must be 15 OR the sum of x and y must be 11