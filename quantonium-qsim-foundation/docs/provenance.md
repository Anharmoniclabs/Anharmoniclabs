# Provenance

The mathematical convention in this repository was frozen from the QuantoniumOS canonical authority record:

- source repository: `LMMinier/quantoniumos`
- source commit: `5bfe066e3b2e3fea722987d21252c69d5b63e2df`
- authority document: `docs/CANONICAL_PATHS.md`
- canonical mathematical source: `algorithms/rft/core/resonant_fourier_transform.py`
- source blob SHA: `a4a4c5bcbd933ba19063200fdf96159aea197ec9`

Frozen convention:

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N)
U = Phi (Phi^H Phi)^(-1/2)
forward: X = U^H x
inverse: x = U X
orientation: rows=samples, columns=basis-vectors
```

The implementation here is intentionally narrow and independent. It does not copy QuantoniumOS application services, desktop code, legacy transforms, fast approximations, or AI research.
