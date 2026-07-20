# Mathematical Definition

Let `N >= 1`, `phi = (1 + sqrt(5))/2`, and

```text
f_k = frac((k + 1) phi),  k = 0, ..., N - 1.
```

Construct the raw square basis

```text
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N).
```

The raw columns are generally not orthogonal. Define the Hermitian Gram matrix

```text
G = Phi^H Phi.
```

For a positive-definite `G`, use its Hermitian eigendecomposition

```text
G = V diag(lambda) V^H
G^(-1/2) = V diag(lambda^(-1/2)) V^H.
```

The canonical polar/Loewdin-normalized operator is

```text
U = Phi G^(-1/2).
```

In exact arithmetic, `U^H U = I`. The transform orientation is:

```text
forward analysis: X = U^H x
inverse synthesis: x = U X.
```

For quantum simulation, a normalized sample state is transformed forward by the gate matrix `U^H`; the inverse circuit uses `U`.
