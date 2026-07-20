# Quantonium Quantum Simulation and Verification Laboratory

This is a standalone quantum-simulation laboratory. It is not an AI system and
contains no language-model code.

The project intentionally separates two different Quantonium engines:

- `quantonium_qsim.exact`: an independent complex statevector simulator for
  arbitrary gates and entangled states;
- `quantonium_qsim.symbolic`: the original native QSC engine plus an explicit
  product-state representation for its restricted phi-structured domain.

Qiskit, Cirq, Qulacs, Stim, Aer, and IBM Runtime are independent verification
targets under `quantonium_qsim.adapters`. They are never silent implementation
fallbacks for the exact or symbolic engines.

## Canonical RFT

The RFT follows QuantoniumOS source commit
`5bfe066e3b2e3fea722987d21252c69d5b63e2df` exactly:

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N)
G = Phi^H Phi
U = Phi G^(-1/2)
forward: X = U^H x
inverse: x = U X
```

Rows are samples and columns are basis vectors. The inverse square root uses a
Hermitian eigendecomposition. Canonical APIs never substitute FFT, DCT,
identity, raw-Phi, or an approximation. Frozen upstream hashes are checked for
every published size from 2 through 256.

## Exact simulator

The native Python path imports only NumPy and Quantonium modules. It supports
normalized initial states; X/Y/Z/H/S/Sdg/T/Tdg; rotations and phase; CX/CY/CZ
and SWAP; arbitrary k-label unitaries; forward/inverse RFT; probabilities;
seeded shots; Pauli expectations; reduced density matrices; partial trace;
purity; and fidelity.

Endianness is little-endian: label 0 is the least-significant statevector index
bit. For arbitrary unitaries, `targets[0]` is the least-significant local bit.

## Symbolic boundary

QSC is a classical, fixed-coefficient representation for a restricted family
of separable, product-form, phi-structured inputs. Its historical C ABI uses
the term `qubit`; the Python API calls these logical labels. QSC never holds a
general `2^n` statevector and does not simulate arbitrary entangled circuits.
Small representable states can be reconstructed for exact comparison. Large
tests assess only normalization, determinism, coefficient stability, memory,
and runtime inside the supported family.

The upstream C source, copyright, SPDX, patent, license, and scope notices are
preserved in `native/qsc`. The ctypes binding includes the header's final
`rft_variant_t variant` field, which the historical binding omitted.

## Install, build, and verify

```bash
python -m pip install -e ".[dev,qiskit,cirq,qulacs,stim,ibm]"
cmake -S native/qsc -B build/qsc
cmake --build build/qsc --config Release
pytest -q
python experiments/run_differential_suite.py
python experiments/run_symbolic_suite.py
python experiments/run_fair_benchmarks.py
python experiments/run_mathematical_closure.py
python experiments/run_rft_vs_qft_suite.py
```

Each generated suite record contains provenance, versions, seed, input hash,
exact command, metrics, conclusion, limitation, and a SHA-256 sidecar.

## IBM hardware

Real-QPU execution is manual. Credentials remain in `IBM_QUANTUM_API_KEY` and
optionally `IBM_QUANTUM_CRN`; normal CI never submits jobs. Dry-run and
submission commands are:

```bash
python experiments/run_ibm_hardware_protocol.py --size 2
python experiments/run_ibm_hardware_protocol.py --size 2 --submit
python experiments/run_ibm_hardware_protocol.py --size 4 --submit
```

The preserved N=2 result is valid evidence for its forward measurement
distribution. Its apparent perfect round trip is inconclusive because the
transpiled circuit contained measurement only. Counts do not verify phase;
X/Y/Z tomography is required before a state-fidelity conclusion.

## What is established

- canonical RFT closure and frozen upstream hash agreement;
- exact native state evolution agrees with direct NumPy and installed external
  references at the declared thresholds;
- QSC builds and behaves deterministically on its declared structured inputs;
- the architecture prevents external simulators from silently replacing
  Quantonium execution.

Not established: quantum advantage, efficient asymptotic RFT synthesis,
fault-tolerant feasibility, universal QSC simulation, or application advantage
over QFT. RFT and QFT are different transforms; circuit cost, simulator
accuracy, transform behavior, hardware noise, and usefulness are separate
questions.
