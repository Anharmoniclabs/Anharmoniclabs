# Anharmonic Labs Provenance

Anharmonic Labs is the active project identity for the independent statevector
engine, polar operator layer, structured-state boundary, reference adapters,
verification framework, and QPU protocol in this repository.

## Mathematical lineage

The golden-phase polar convention was frozen from an earlier QuantoniumOS
authority record so that the renamed component does not erase scientific
lineage:

- source repository: `LMMinier/quantoniumos`
- source commit: `5bfe066e3b2e3fea722987d21252c69d5b63e2df`
- authority document: `docs/CANONICAL_PATHS.md`
- mathematical source: `algorithms/rft/core/resonant_fourier_transform.py`
- frozen source blob SHA: `a4a4c5bcbd933ba19063200fdf96159aea197ec9`

The inherited finite convention is:

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N)
U = Phi (Phi^H Phi)^(-1/2)
analysis: X = U^H x
synthesis: x = U X
```

Anharmonic Labs calls this component **Polar** because its defining operation
is the Gram/polar normalization. The rename does not claim invention of the
inherited formula.

## Native structured lineage

The structured C kernel descends from the earlier source files named
`quantum_symbolic_compression.c/.h` and retains their original copyright, SPDX,
patent, license, and scope notices. Anharmonic Labs renames its active ABI and
documents the backend as a restricted classical representation. It does not
reinterpret compact labels as physical qubits or claim universal quantum
simulation.

## Independently developed Anharmonic Labs layers

- complete complex statevector evolution and observables;
- explicit endianness and arbitrary-target unitary semantics;
- reference isolation for NumPy and external quantum SDKs;
- differential correctness metrics and fair timing boundaries;
- reproducible result manifests and SHA-256 sidecars;
- manual, noise-gated QPU distribution and tomography protocol.

Historical raw evidence is preserved under `results/legacy/`. It is immutable
lineage evidence, not active branding or an active API contract.
