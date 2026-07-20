# Anharmonic Labs Architecture

```text
Anharmonic Labs
├── Statevector   complete complex Hilbert-space evolution
├── Polar         phase basis → Gram matrix → inverse square root → unitary
├── Structured    restricted product-family coefficients and reconstruction
├── References    NumPy, Qiskit, Cirq, Qulacs, Stim, Aer, IBM Runtime
└── Verification  correctness metrics, fair timing, manifests, hash sidecars
```

Statevector owns arbitrary-circuit correctness. Structured owns only its
declared separable family. Neither native path delegates execution to a
reference adapter.

Statevector and Qiskit use little-endian state indexing: label 0 is the least
significant bit and the first target of a k-label operator is its least
significant local bit. The Cirq reference converts axes explicitly. The Stim
reference rejects non-Clifford operations.

Polar has one canonical dense definition. Requests beyond its safety limit
raise an error; they never switch transform families.
