# QuantoniumOS Quantum Simulation Lab

This repository contains the standalone quantum-simulation work for the QuantoniumOS project. Despite the repository name, it is **not an AI or language-model repository**.

The project represents the canonical Resonant Fourier Transform (RFT) as a finite-dimensional unitary, verifies the operator numerically, applies the forward or inverse transform to simulated quantum statevectors, and measures generic gate decompositions against a standard Quantum Fourier Transform circuit.

## Scientific boundary

This repository can establish that a finite RFT matrix is unitary to numerical precision and can be simulated as a quantum gate. It does **not** by itself establish quantum advantage, efficient asymptotic circuit synthesis, fault-tolerant feasibility, or execution on physical quantum hardware.

## Canonical convention

For dimension `N`, with the golden ratio `phi`:

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N)
G = Phi^H Phi
U = Phi G^(-1/2)
forward coefficients: X = U^H x
inverse synthesis:    x = U X
```

Rows are samples and columns are basis vectors. `G^(-1/2)` is computed through a Hermitian eigendecomposition.

## Setup

```bash
python -m pip install -e ".[dev,quantum]"
pytest -q
```

## Run the first experiments

```bash
python experiments/01_verify_rft_unitarity.py
python experiments/02_statevector_equivalence.py
python experiments/03_compare_qft_circuits.py
```

JSON records are written under `results/` and are intentionally ignored by Git except for the directory placeholder.

## Package layout

```text
src/quantonium_qsim/rft/       canonical RFT construction and validation
src/quantonium_qsim/quantum/   Qiskit circuits and statevector simulation
src/quantonium_qsim/analysis/  state equivalence and gate metrics
experiments/                    reproducible experiment entry points
tests/                          numerical and quantum-simulation tests
docs/                           architecture, mathematics, and provenance
```

## Provenance

The formula is frozen from the QuantoniumOS canonical implementation identified in `docs/provenance.md`. This repository reimplements only the narrow mathematical operator needed for quantum simulation and does not import unrelated QuantoniumOS services, AI code, desktop code, or experimental RFT variants.
