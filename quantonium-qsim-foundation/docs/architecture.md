# Architecture

```text
Quantonium simulation stack
├── exact/       independent full complex statevector execution
├── rft/         one canonical phi-grid-polar-v1 transform
├── symbolic/    restricted product representation + original native QSC
├── adapters/    Qiskit, Cirq, Qulacs, Stim, IBM Runtime references
└── benchmarks/  correctness metrics, fair timing, reproducible manifests
```

The exact engine owns arbitrary-circuit correctness. The symbolic engine owns
only structured-state compression and reconstruction. There is no delegation
from either engine into an adapter. Optional adapter imports occur only when a
caller explicitly selects that reference.

The exact simulator and Qiskit share a documented little-endian convention:
label 0 is the least-significant index bit and the first k-unitary target is
the least-significant local bit. The Cirq adapter performs its axis conversion
explicitly; Stim rejects non-Clifford operations.

No canonical entry point has a transform fallback. Exact dense construction
raises above its documented safety limit.
