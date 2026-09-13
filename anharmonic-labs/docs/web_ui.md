# Anharmonic Labs web laboratory

The repository-level `index.html`, `assets/`, and `.nojekyll` files form the
GitHub Pages application. It is a dependency-free static application: HTML,
CSS, SVG, and JavaScript modules.

The browser simulator contains browser-native standard statevector operations
plus bounded research and analysis tools: golden-phase raw and polar matrices,
Gram inspection, fixed-buffer structured schedule generation, density
matrices, partial trace, purity, Pauli expectations, seeded measurement
collapse, conditional operations, single-system noise channels, arbitrary
local unitaries, initial-state JSON loading, circuit/state JSON export, and
OpenQASM export. Browser dimensions are intentionally bounded.

The browser does not invoke Python, C, Qiskit, Cirq, Qulacs, Stim, Aer, IBM
Runtime, or real quantum hardware. OpenQASM and JSON are interoperability
outputs, not claims that external runtimes execute inside GitHub Pages. Do not
place service credentials or unpublished experiment data in browser assets.
Everything under the Pages source is public.

The public core supports H, X, Y, Z, S, T, RX, RY, RZ, CX, CY, CZ, and SWAP
for one through six two-level systems. It displays amplitudes, probabilities,
normalization, Shannon entropy, support size, and deterministic sampling. Its
little-endian convention matches the Python statevector engine.

The workbench also includes an explicitly experimental vertex-geometry panel.
It models four tetrahedral vertices and six edges, with deterministic braid
phase, holonomy, Wilson-loop, Berry-phase, winding, genus, and Euler
characteristic readouts. The local paper describes tetrahedral geometric data
storage and separately describes symbolic alpha/beta qubits; it does not define
"vertex qubits" as a formal physical qubit model. The browser panel is
therefore an inspectable geometric toy model, not topological hardware,
fault-tolerant quantum computation, or a claim of paper validation.

## Run locally

From the repository root:

```bash
python -m http.server 8000 --directory .
```

Then open `http://localhost:8000`.

Run the browser-core tests with:

```bash
node --test anharmonic-labs/tests/web/*.test.mjs
```

Run cross-runtime browser parity from the repository root with:

```bash
python anharmonic-labs/experiments/run_browser_parity.py
```

The parity harness runs identical Bell, rotated-entanglement, and nonadjacent
circuits through the browser JavaScript core and the native Python statevector
simulator, comparing global-phase-aligned amplitudes and probabilities. It
also compares Qiskit Statevector when the optional Qiskit dependency is
installed; otherwise it reports Qiskit as skipped rather than claiming an
external validation that did not run.

The browser also has a separate sparse mode for up to 50 systems. Run its
terminal parity check with:

```bash
python anharmonic-labs/experiments/run_sparse_50_parity.py
```

That check compares a deterministic sparse-preserving 50-qubit circuit with
Qiskit Aer's matrix-product-state simulator. It validates the final basis
measurement index over 1,024 shots. It does not claim that arbitrary 50-qubit
statevectors fit in memory: a dense state still has $2^{50}$ amplitudes.

## Publish

GitHub Pages is configured to deploy directly from the publishing branch root.
There is no custom Pages workflow. The default project URL is:

```text
https://anharmoniclabs.github.io/Anharmoniclabs/
```

No `CNAME` is included because a custom domain has not been selected. Add one
only after the domain is owned and its DNS records have been configured.
