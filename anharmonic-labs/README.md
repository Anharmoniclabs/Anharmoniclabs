# Anharmonic Labs

Anharmonic Labs is a quantum-mathematics simulation and verification laboratory.
The name reflects its study of nonuniform phase spectra and operators beyond a
uniform harmonic grid. Its two principal representations are:

- **Anharmonic Labs Statevector** evolves complete complex vectors in finite
  Hilbert spaces, including arbitrary unitary gates and entangled states.
- **Anharmonic Labs Structured** folds a declared family of separable,
  phase-structured descriptions into compact coefficient representations.

**Anharmonic Labs Polar** is the native spectral operator layer. It builds a
golden-phase basis and obtains a unitary operator through Hermitian Gram/polar
normalization. Qiskit, Cirq, Qulacs, Stim, Aer, and IBM Runtime live under
**Anharmonic Labs References** and never silently implement the native engines.

## Web laboratory

The public simulation UX lives in the repository-level [`index.html`](../index.html)
Pages entrypoint and opens directly into an interactive, dependency-free
statevector workbench for standard gates, amplitudes, probabilities, and seeded
measurement sampling. Deployment uses GitHub's branch-backed Pages source; no
custom Pages workflow is stored in the repository.

GitHub Pages cannot protect client-side implementation details: every shipped
HTML, JavaScript, WebAssembly, and data file is public. The site therefore does
not contain the research operator constructor or native research kernels. The
required public/private boundary and the limitations of an oracle-style API are
documented in [Public simulation UI and private compute boundary](docs/public_private_web_architecture.md).

## Mathematical operator

For dimension `N` and golden ratio `phi`:

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i f_k n) / sqrt(N)
G = Phi^H Phi
U = Phi G^(-1/2)
analysis:  X = U^H x
synthesis: x = U X
```

Rows are samples and columns are basis vectors. `G^(-1/2)` is formed by a
Hermitian eigendecomposition. The canonical API never substitutes an FFT, DCT,
identity, raw dictionary, or approximation. Frozen source-lineage hashes are
checked at every published size from 2 through 256.

## Statevector engine

`anharmonic.statevector.StatevectorSimulator` is implemented independently
with NumPy. It supports normalized initial states; X, Y, Z, H, S, Sdg, T and
Tdg; RX, RY, RZ and phase; CX, CY, CZ and SWAP; arbitrary k-label unitaries;
polar analysis and synthesis; probabilities; deterministic shots; Pauli
expectations; reduced density matrices; partial trace; purity; and fidelity.

The convention is little-endian: label 0 is the least-significant state index
bit, and `targets[0]` is the least-significant local bit of a k-label unitary.

## Structured-state boundary

`anharmonic.structured.StructuredEngine` is a classical fixed-buffer engine
for a restricted separable, product-form, phase-structured family. It does not
hold a general `2^n` statevector and does not simulate arbitrary entangled
circuits. Small representable states can be reconstructed for direct
statevector comparison. Large runs assess normalization, determinism,
coefficient stability, memory, and runtime only inside the declared family.

Source copyright, SPDX, patent, license, and lineage notices remain preserved;
see [provenance](docs/provenance.md).

## Layout

```text
src/anharmonic/
├── statevector/   complete complex Hilbert-space evolution
├── polar/         golden-phase Gram/polar unitary construction
├── structured/    restricted structured-state representation and binding
├── references/    independent simulator and QPU integrations
├── verification/  metrics, timing, and reproducible manifests
├── circuits/      reference circuit construction
└── analysis/      state and circuit comparison helpers
```

## Install, build, and verify

```bash
python -m pip install -e ".[dev,qiskit,cirq,qulacs,stim,ibm]"
cmake -S native/structured_kernel -B build/anharmonic-structured
cmake --build build/anharmonic-structured --config Release
pytest -q
python experiments/run_mathematical_closure.py
python experiments/run_differential_suite.py
python experiments/run_structured_suite.py
python experiments/run_fair_benchmarks.py
python experiments/run_polar_vs_qft_suite.py
```

Generated results include source revision, dependencies, platform, timestamp,
seed, input hash, backend, exact command, metrics, conclusion, limitation, and a
SHA-256 sidecar. Preserved historical evidence is isolated in
`results/legacy/` and does not define the active API.

## Real hardware

Credentials remain outside the repository in `IBM_QUANTUM_API_KEY` and,
optionally, `IBM_QUANTUM_CRN`. Normal CI never submits QPU jobs.

```bash
python experiments/run_ibm_hardware_protocol.py --size 2
python experiments/run_ibm_hardware_protocol.py --size 2 --shots 1024 --submit
python experiments/run_ibm_hardware_protocol.py --size 4 --shots 1024 --submit
```

Submission is gated on backend-specific Aer simulation. The protocol records
measurement distributions plus X/Y/Z tomography for one- and two-label cases.

## Scientific status

The complete feature-by-feature prior-method comparison is documented in
[Technical Differentiation and Method Comparison](docs/technical_novelty_and_method_comparison.md).

Established: finite numerical closure, frozen-hash agreement, native
statevector agreement with independent references, structured-domain
determinism, native compilation, and reproducible experiment records.

Not established: quantum advantage, efficient asymptotic synthesis,
fault-tolerant feasibility, universal structured-state simulation, or
application superiority over the standard QFT. Transform behavior, simulator
accuracy, synthesis cost, hardware noise, and usefulness remain separate
questions.
