# Anharmonic Labs: Technical Differentiation and Method Comparison

Status: implementation-grounded technical assessment, 2026-07-20

## Purpose and limits

This document inventories the technical aspects implemented in this repository
and compares them with the closest established methods. It uses **novelty** in
the research and engineering sense: a feature may be distinctive in this stack
without being legally novel or patentable.

This is not a patentability or freedom-to-operate opinion. A legal novelty
conclusion requires claim construction, filing and priority dates, and a
professional search across patents, papers, theses, software, and public uses.
The author's own earlier publications are also relevant prior disclosures.

The classifications used below are:

- **Established** — a standard mathematical or software technique.
- **Project-specific engineering** — a useful implementation choice, but not a
  new primitive by itself.
- **Potentially distinctive combination** — the exact combination appears to
  be a meaningful research contribution, but worldwide novelty is not proven.
- **Candidate research novelty** — sufficiently specific to investigate in a
  formal literature and patent search.

## Executive assessment

The strongest candidate contribution is not statevector simulation, generic
unitary embedding, product-state storage, or Löwdin orthogonalization by itself.
It is the combined construction and validation envelope:

```text
golden irrational orbit
    -> square nonuniform Fourier/Vandermonde dictionary
    -> symmetric polar (Löwdin) orthogonalization
    -> one canonical unitary and transform orientation
    -> frozen numerical identity
    -> independent simulator, synthesis, noise, and hardware checks
```

The current dense operator is

```text
f_k = frac((k + 1) phi)
Phi[n,k] = exp(2 pi i n f_k) / sqrt(N)
U = Phi (Phi^H Phi)^(-1/2)
analysis = U^H x
synthesis = U X.
```

The selection of the golden orbit and the exact normalized operator is the
research-specific part. Irrational rotations, nonuniform Fourier matrices,
Vandermonde matrices, Gram matrices, inverse square roots, polar factors, and
symmetric orthogonalization all predate this project.

## Complete feature and comparison matrix

| Implemented aspect | Closest established method | Material difference | Assessment |
|---|---|---|---|
| Golden-orbit frequencies `frac((k+1)phi)` | Kronecker irrational-rotation sequences | Fixes one deterministic, badly approximable irrational rather than a uniform rational grid or random draw | Candidate component, but irrational or golden sampling is established |
| Square complex exponential dictionary `Phi` | DFT/NUDFT Vandermonde matrix | Uses nonuniform irrational frequencies at uniform sample indices; raw columns are not orthogonal | Established construction with project-specific nodes |
| Full-rank argument from distinct golden nodes | Vandermonde determinant theory | Irrationality prevents repeated nodes for finite `N` | Established theorem applied to this grid |
| `U = Phi(Phi^H Phi)^(-1/2)` | Löwdin symmetric orthogonalization / unitary polar factor | Applies the standard symmetric factor specifically to the golden Fourier dictionary | Potentially distinctive combination; orthogonalization itself is established |
| Symmetric rather than ordered orthogonalization | Gram–Schmidt or QR | Avoids dependence on a column ordering and selects the polar factor closest to `Phi` in the standard norm sense | Established advantage of the polar/Löwdin method |
| Fixed analysis/synthesis orientation | Fourier-library conventions | Declares `U^H` as analysis and `U` as synthesis everywhere | Project-specific correctness contract |
| Parameterized `phase_ratio` construction | Fractional/nonuniform Fourier transforms | Allows another irrational or real frequency stride but still polar-normalizes the complete square dictionary | Project-specific generalization |
| No silent alternate transform | Libraries that switch algorithms or approximate ill-conditioned systems | Raises on unsupported size or numerical singularity instead of substituting FFT, identity, pseudoinverse, or approximation | Project-specific scientific safeguard |
| Dense safety limit and immutable cached matrices | General dense linear algebra | Makes the cost and domain boundary explicit and prevents mutation of the canonical operator | Project-specific engineering |
| Portable rounded-byte basis hashes | Reproducible numerical fixtures | Freezes the finite numerical identity across published dimensions | Project-specific reproducibility mechanism |
| Polar operator as an all-register statevector unitary | Generic arbitrary-unitary simulation | Integrates the operator with the same target-order semantics as local gates | Project-specific integration, not a new simulation method |
| Independent NumPy statevector engine | Qiskit Aer, Cirq/qsim, Qulacs, and other Schrödinger simulators | A small auditable reference implementation with explicit little-endian arbitrary-target semantics | Established method; independent implementation is useful evidence |
| Arbitrary nonadjacent `k`-target unitary application | Tensor-axis permutation and batched matrix multiplication | Explicitly defines `targets[0]` as the local least-significant bit and tests cross-framework conversions | Project-specific correctness engineering |
| Gates, seeded sampling, expectations, partial trace, purity, fidelity | Standard quantum-information tooling | Implemented without delegating the native engine to an external SDK | Established functionality |
| Cross-simulator comparison with global-phase alignment | Differential quantum-software testing | Compares the native engine with direct dense NumPy, Qiskit, Cirq, Qulacs, and Clifford-only Stim | Established testing idea; unusually broad project-specific oracle mesh |
| Multiple simultaneous correctness metrics | Fidelity-only or counts-only tests | Requires fidelity, phase-aligned L2, maximum amplitude error, norm error, and probability TVD | Project-specific verification policy |
| Forward, inverse, and barrier-separated round-trip probes | Ordinary unitary/identity tests | Tests direction errors and prevents a compiler from trivially deleting the hardware round trip | Project-specific experimental design |
| Product-state factor representation | Product states; matrix-product states with bond dimension 1 | Stores one normalized two-component factor per logical label | Established representation |
| Golden-phase `ProductState.phi_schedule` | Deterministic product-state ansatz initialization | Fixes polar and azimuthal angles with two golden-ratio orbits | Potentially distinctive initialization schedule; no advantage is yet shown |
| Exact small-state reconstruction boundary | Tensor-product expansion | Allows direct validation only up to a declared limit and refuses exponential reconstruction above it | Project-specific scope control |
| Native fixed-buffer phase schedule | Streaming sketches, feature hashing, and bucketed phasor sums | Uses deterministic modulo buckets and a golden-dependent phase formula, followed by global normalization | Candidate implementation detail; no recovery theorem or task advantage yet |
| Fixed-buffer normalization and deterministic replay tests | Sketch consistency checks | Demonstrates repeatability and unit norm, not preservation of an arbitrary input state | Project-specific evidence with a strict limitation |
| Separate Statevector and Structured capability domains | Multi-backend simulators | Prevents the compact representation from masquerading as a universal entangled-state simulator | Potentially distinctive architecture/governance combination |
| Polar-versus-QFT behavioral comparison | Algorithm benchmark suites | Measures unitary distance and input-dependent output overlap before discussing circuit cost | Project-specific scientific comparison |
| Separation of behavior, simulator accuracy, synthesis cost, noise, and usefulness | Single-score benchmark claims | Prevents agreement in one layer from being used as evidence for another | Potentially distinctive evaluation methodology |
| Cold-start and warm-run timing categories | Microbenchmark methodology | Separates construction, compilation, evolution, sampling, and reconstruction with warmups and at least 30 runs | Established benchmarking practice, carefully applied |
| Generic Qiskit `UnitaryGate` synthesis | General unitary decomposition | Provides an exact finite hardware path but makes no efficient-synthesis claim | Established method and explicit limitation |
| Backend-derived noisy simulation gate before QPU submission | Device-noise simulation and staged hardware validation | A real job cannot be the first execution target; submission requires an explicit flag after backend-specific Aer simulation | Project-specific safety protocol |
| X/Y/Z tomography plus distribution metrics | Pauli tomography and linear inversion | Counts, phase-sensitive observables, density estimates, and circuit metadata are recorded together | Established measurements assembled into a stronger evidence package |
| Source-linked JSON manifests and SHA-256 sidecars | Reproducible-computing manifests | Records commit, dirty state, lineage commit, versions, platform, seed, input hash, command, conclusion, and limitation | Project-specific provenance integration |
| Immutable legacy-evidence boundary | Data/version migration practices | Historical records retain their original checksums and names while active APIs use the new identity | Project-specific provenance governance |

## 1. Golden-orbit Polar operator

### 1.1 What is technically specific

The raw matrix is a square nonuniform Fourier dictionary. Its nodes are

```text
z_k = exp(2 pi i frac((k+1)phi)).
```

Because `phi` is irrational, `z_i != z_j` for distinct finite indices. The
Vandermonde matrix is therefore full rank. Its columns are generally
nonorthogonal, so the implementation builds the Gram matrix and selects the
unitary polar factor by symmetric orthogonalization.

The candidate contribution is the **specific deterministic orbit plus this
canonical orthogonalization**, not the individual ingredients. The exact same
construction is already publicly described in the author's own preprint,
[The Resonance Fourier Transform: A Golden-Ratio Spectral Basis with
Diophantine Concentration Guarantees](https://doi.org/10.5281/zenodo.18599415).
Accordingly, Anharmonic Labs should treat that publication and its priority date
as part of the method's provenance, not describe the repository rename as a new
invention date.

### 1.2 Against the DFT and QFT

The DFT uses equally spaced roots of unity. Its matrix is already unitary after
normalization and supports FFT structure. The QFT implements the corresponding
unitary on amplitudes with structured circuits; exact and approximate QFT
circuits have well-developed complexity results, including the constructions
of [Coppersmith](https://arxiv.org/abs/quant-ph/0201067) and
[Cleve and Watrous](https://arxiv.org/abs/quant-ph/0006004).

Anharmonic Polar uses an irrational, nonuniform frequency grid and then mixes
all raw columns through `G^(-1/2)`. Consequently:

- it is not a re-labeled QFT;
- it does not inherit FFT or QFT circuit complexity;
- a generic unitary synthesis is an implementation path, not an efficient
  asymptotic algorithm;
- any advantage must be tied to a declared input ensemble or application.

The current comparison results confirm finite distinction, not superiority.
For dimensions 2, 4, and 8, the global-phase-adjusted unitary distances from
the QFT are approximately 0.981, 1.052, and 1.299. Output overlap varies
strongly by input. At dimension 8, the generic Polar synthesis had depth 75 and
18 two-qubit operations in the chosen basis, versus QFT depth 20 and 9
two-qubit operations. Those figures are environment- and transpiler-specific,
but they correctly reject an automatic efficiency claim.

### 1.3 Against NUDFT and NUFFT

Nonuniform Fourier transforms already evaluate complex exponentials at
noninteger frequencies or nonequispaced nodes. Dutt and Rokhlin gave fast
approximate algorithms with complexity depending on the requested accuracy
([SIAM J. Sci. Comput. 14, 1368–1393](https://doi.org/10.1137/0914081)).

The raw `Phi` matrix belongs to this broad nonuniform-Fourier family. The
distinction is that Anharmonic Polar does not stop at evaluating the raw
dictionary: it performs a global symmetric orthogonalization and defines the
resulting polar factor as the transform. This changes the basis atoms. A NUFFT
could potentially accelerate raw matrix operations, but it is not itself an
algorithm for applying the dense orthogonalized `U`.

### 1.4 Against Löwdin, Gram–Schmidt, QR, and polar decomposition

Löwdin introduced symmetric orthogonalization in 1950
([J. Chem. Phys. 18, 365](https://doi.org/10.1063/1.1747632)). Polar-factor
computation and its approximation properties are standard numerical linear
algebra; see [Higham, 1986](https://eprints.maths.manchester.ac.uk/694/).

Therefore:

- `Phi(Phi^H Phi)^(-1/2)` is not independently novel as an
  orthogonalization formula;
- using an eigendecomposition to form a positive inverse square root is
  standard;
- the potentially distinctive aspect is the selected golden dictionary and
  what can be proven or measured for signal classes associated with it.

QR or Gram–Schmidt could also create an orthonormal basis spanning the columns,
but the result would depend on ordering and would generally not equal the
symmetric polar factor. That makes the polar choice scientifically meaningful,
even though it is established.

### 1.5 Against fractional Fourier, chirp-Z, Slepian, and random features

- Fractional Fourier methods parameterize Fourier-like grids or rotations and
  admit FFT-related algorithms; see
  [Bailey and Swarztrauber](https://doi.org/10.1137/1033097).
- Bluestein/chirp methods rewrite Fourier evaluation as chirp convolution; see
  [Bluestein](https://doi.org/10.1109/TAU.1970.1162132).
- Discrete prolate spheroidal sequences solve a time/band concentration
  eigenproblem; see [Slepian](https://doi.org/10.1002/j.1538-7305.1978.tb02104.x).
- Random Fourier features sample frequencies to approximate shift-invariant
  kernels; see [Rahimi and Recht](https://papers.nips.cc/paper/2007/hash/013a006f03dbc5392effeb8f18fda755-Abstract.html).

Anharmonic Polar instead fixes one deterministic irrational orbit and
orthogonalizes a complete square dictionary. It is global rather than
windowed, deterministic rather than randomly sampled, and does not currently
solve the Slepian concentration optimization.

### 1.6 Against the author's earlier fast phase-modulated transform

An earlier self-authored framework described a different factorization,
`Psi = D_phi C_sigma F`, consisting of a DFT and diagonal phase operators
([public preprint record](https://doi.org/10.5281/zenodo.15126561)). That
operator is unitary by composition and is FFT-compatible.

The current canonical Polar operator is not that factorization. It begins with
a nonuniform Vandermonde matrix and forms its polar factor. The two methods
must not share numerical claims, complexity claims, circuit claims, or
validation results unless an explicit equivalence is proved. No such
equivalence is implemented here.

### 1.7 Current evidence

The mathematical closure suite currently reports, for dimensions 2 through
256:

- full numerical rank of the raw dictionary;
- left and right unitarity errors no larger than approximately `1.9e-13`;
- round-trip error no larger than approximately `9.4e-15`;
- norm and Parseval preservation within the declared thresholds;
- deterministic agreement with frozen portable hashes.

This establishes finite numerical closure for the tested implementation. It
does not establish a fast transform, a circuit-complexity bound, conditioning
at arbitrary dimension, spectral concentration on an application population,
or quantum advantage.

## 2. Statevector engine and independent reference mesh

### 2.1 What is implemented

The native statevector engine stores a complete `complex128` vector and applies
arbitrary target-local unitaries by tensor reshaping, axis permutation, batched
matrix multiplication, and inverse permutation. It also implements common
gates, deterministic sampling, Pauli expectations, reduced density matrices,
partial trace, purity, and fidelity.

This is standard Schrödinger statevector simulation. High-performance examples
include [Qulacs](https://doi.org/10.22331/q-2021-10-06-559) and
[qsim/Cirq](https://arxiv.org/abs/2111.02396). Anharmonic Labs does not
currently introduce a new statevector scaling law, sparse representation,
parallel algorithm, GPU kernel, gate-fusion method, or noise trajectory method.

### 2.2 What is distinctive in this stack

The contribution is auditability and integration:

- no external simulator executes the native path;
- little-endian indexing is stated as an API contract;
- arbitrary target ordering is explicit rather than incidental;
- Cirq axis ordering is converted deliberately;
- Stim is limited to Clifford cases instead of silently approximating
  unsupported gates;
- the Polar matrix is tested as a full-register unitary through the same path
  as ordinary gates.

The differential suite currently records 193 comparisons across direct dense
NumPy, Qiskit, Cirq, Qulacs, and Stim. The minimum recorded fidelity is
`0.9999999999999991`; the largest phase-aligned L2 error is approximately
`1.12e-15`.

Cross-implementation comparison is not new. QDiff compared multiple quantum
software stacks using distribution equivalence
([ASE 2021](https://doi.org/10.1109/ASE51524.2021.9678792)), and MorphQ uses
quantum-specific metamorphic relations
([ICSE 2023](https://arxiv.org/abs/2206.01111)). The Anharmonic contribution is
the particular oracle mesh and the inclusion of its custom Polar operator.

## 3. Structured representations

The repository contains two different structured mechanisms. They must not be
presented as one algorithm.

### 3.1 ProductState factorization

`ProductState` stores one normalized pair `(alpha_j, beta_j)` per label. It is
exact for separable states and cannot represent entanglement. In tensor-network
language this is the bond-dimension-one endpoint of a matrix-product-state
family; matrix product states and their limitations are established
([Schollwöck](https://arxiv.org/abs/1008.3477)).

The `phi_schedule` constructor is project-specific:

```text
theta_j = pi frac(j phi)
phase_j = 2 pi frac(j / phi)
factor_j = [cos(theta_j/2), exp(i phase_j) sin(theta_j/2)].
```

The storage is `2L` complex coefficients instead of `2^L`, but that ratio is a
**parameter-count ratio inside the product family**, not compression of an
arbitrary quantum state. Exact reconstruction is exponential and is therefore
disabled above a declared label limit.

The current suite reconstructs schedules with 1–10 labels at zero recorded
error. This validates serialization of representable product states; it does
not demonstrate general compression.

### 3.2 Native fixed-buffer phase schedule

The C kernel does not accept an input state or signal. Given label count `L`
and buffer size `M`, it generates

```text
theta_j = mod(j phi L, 2 pi) + mod(j sqrt(L)/1000, 2 pi)
b_j = j mod M
c_b = (1/sqrt(M)) sum_{j: b_j=b} exp(i theta_j),
```

then globally normalizes `c`.

Its implementation cost is `O(L + M)` time and `O(M)` storage. If `M=64` is
fixed, buffer storage is constant with respect to `L`. This resembles a
deterministic bucketed phasor sketch. Bucketed dimensional reduction itself is
established in streaming sketches and feature hashing; examples include
[Count Sketch](https://doi.org/10.1016/S0304-3975(03)00400-6) and
[feature hashing](https://arxiv.org/abs/0902.2206).

The candidate detail is the exact phase law plus deterministic modulo
aggregation. However, the implementation currently has:

- no arbitrary input to reconstruct;
- no decoder;
- no collision-error or distance-preservation theorem;
- no demonstrated relation between its 64 coefficients and amplitudes of the
  `ProductState` representation;
- no support for general entanglement or circuit evolution.

The current large-label evidence shows deterministic, normalized output for
1,000, 10,000, and 100,000 labels with a 1 KiB coefficient buffer. That is
evidence for a bounded-memory schedule generator, not a million-qubit or
universal quantum simulator.

### 3.3 Strongest architectural distinction

The most defensible structured-layer contribution is the enforced capability
boundary:

```text
Statevector: complete amplitudes, arbitrary finite unitaries, entanglement
ProductState: exact separable factors only
Native schedule: deterministic fixed-buffer phase sketch only
```

Many systems support multiple simulation backends, but this repository makes
misrepresentation of the compact paths a tested architectural error. That is a
meaningful scientific-engineering property even if it is not a new compression
algorithm.

## 4. Circuit synthesis and hardware protocol

### 4.1 Generic unitary synthesis

The Qiskit circuit wraps the finite Polar matrix in a generic unitary gate.
This proves that the tested matrix can be embedded as a finite quantum
operation. It does not supply a scalable decomposition. The standard QFT has
known structured circuits, while a generic `2^q x 2^q` unitary generally has
far higher synthesis cost. The repository correctly measures this cost instead
of treating a one-node `UnitaryGate` as one physical operation.

### 4.2 Hardware evidence design

The full protocol combines:

- computational-basis, uniform, phase-sensitive, and Bell preparations;
- forward, inverse, barrier-separated round trip, and QFT-control transforms;
- transpiled depth, operation counts, layout, and backend identity;
- ideal distributions;
- backend-derived noisy Aer simulation;
- real SamplerV2 results only after an explicit submission flag;
- X/Y/Z Pauli tomography;
- TVD, Hellinger distance, distribution fidelity, and state fidelity;
- calibration availability, job ID, seed, shots, and manifest hash.

Every ingredient is established. IBM documents backend-derived Aer noise models
and simulator configuration
([AerSimulator](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html)),
and Pauli tomography with linear inversion is standard. Linear inversion may
produce a non-positive density estimate, a limitation the protocol records;
see the tomography discussion in
[Ma et al.](https://arxiv.org/abs/1601.05379).

The project-specific contribution is the staged evidence contract and its use
for the custom Polar operator. No current non-legacy hardware result exists
under the Anharmonic Labs identity, so the protocol is implemented but not yet
current hardware evidence.

## 5. Reproducibility and scientific-claim controls

### 5.1 Distinctive engineering package

Each generated result includes:

- schema version;
- current Git commit and dirty-worktree status;
- pinned source-lineage commit;
- dependency and Python versions;
- platform and UTC timestamp;
- deterministic seed and input hash;
- backend and exact command;
- metrics, pass/fail result, conclusion, and limitation;
- a SHA-256 sidecar.

The use of hashes and manifests is established reproducibility practice. The
distinction is their integration with mathematical fixtures, simulator
differential tests, timing boundaries, and preserved historical evidence.

### 5.2 Claim separation

The comparison suite explicitly separates:

1. transform behavior;
2. simulator correctness;
3. circuit synthesis cost;
4. noise response;
5. application usefulness.

This prevents invalid inferences such as:

- unitary implies useful;
- simulated accurately implies physically advantageous;
- a generic unitary gate implies an efficient circuit;
- normalized compact coefficients imply a compressed quantum state;
- hardware counts alone reveal phase;
- a faster restricted representation outperforms a universal simulator on the
  same task.

This separation is one of the strongest methodological aspects of the stack.

## 6. What is not established or not present

The repository does **not** currently establish or implement:

- a classical or quantum asymptotic speedup for the Polar operator;
- an FFT-class algorithm for the dense canonical Polar factor;
- a scalable structured quantum circuit for that factor;
- superiority to QFT, NUFFT, FrFT, DPSS, wavelets, or learned dictionaries on
  a declared application dataset;
- arbitrary-state compression by either structured path;
- entangled-state evolution in the product or native fixed-buffer path;
- a physical anharmonic-oscillator Hamiltonian or its time evolution;
- a native density-matrix or stochastic-noise simulator;
- quantum error correction, fault tolerance, or error mitigation;
- cryptographic primitives or post-quantum security proofs;
- a current Anharmonic Labs QPU result;
- patent novelty or freedom to operate.

These exclusions are not weaknesses in the documentation. They define the
experiments required to turn candidate distinctions into defensible results.

## 7. Candidate claims worth formal investigation

Subject to a professional prior-art search, the following are the narrowest
research candidates supported by the implementation:

1. **Canonical golden-orbit polar basis** — the unitary polar factor of the
   square complex-exponential Vandermonde matrix whose nodes follow
   `frac((k+1)phi)`, with fixed analysis/synthesis orientation.
2. **Signal-class concentration results for that exact basis** — only to the
   extent proved in the author's cited preprint and reproduced by independent,
   preregistered tests; the current repository validates closure but does not
   reproduce the complete concentration study.
3. **Golden-phase product initialization** — the paired `theta` and phase
   irrational rotations as a deterministic separable ansatz, if a task-specific
   benefit can be demonstrated against random, Sobol, lattice, and ordinary
   product-state initializations.
4. **Fixed-buffer deterministic phase sketch** — the exact phase law and
   modulo-bucket aggregation, if a preserved quantity, recovery objective, or
   downstream task can be formally defined and compared with Count Sketch,
   random projections, sparse Fourier sketches, and reservoir features.
5. **Layered validation contract for a nonstandard unitary** — canonical hash
   identity, algebraic closure, independent simulator agreement, generic
   synthesis accounting, backend-noise gate, tomography, and immutable
   provenance as one reproducible protocol.

Items 1 and 2 are already connected to the author's public disclosure. Items 3
and 4 need stronger problem definitions and baselines. Item 5 is primarily a
scientific-software contribution rather than a new mathematical transform.

## 8. Experiments needed for stronger differentiation

### Polar operator

- Measure condition numbers and stability beyond the currently frozen sizes.
- Compare dense eigendecomposition, SVD polar factor, QR, and iterative polar
  algorithms on the same dictionaries.
- Benchmark against NUFFT, fractional Fourier, chirp-Z, DPSS, DFT, and learned
  dictionaries on preregistered signal ensembles.
- Reproduce coefficient-concentration claims from the cited preprint inside
  this repository with null models and confidence intervals.
- Search for exploitable algebraic structure in `G^(-1/2)` before making any
  fast-transform or circuit-complexity claim.

### Structured layer

- Rename native metrics around **sketch ratio**, not state compression, unless
  an encoder/decoder and source object are defined.
- Define what information the fixed buffer is intended to preserve.
- Compare against random projections, Count Sketch, feature hashing, reservoir
  features, and MPS truncation on that objective.
- Add collision, perturbation, and stability analysis.
- Prove or falsify any relationship between the native sketch and the
  `ProductState` factors.

### Hardware and reproducibility

- Generate current N=2 and N=4 hardware records under the Anharmonic Labs
  schema.
- Add readout-mitigation and physicality-constrained tomography as separately
  reported analyses, without overwriting raw linear-inversion evidence.
- Commit the identity migration and regenerate manifests so
  `git_worktree_dirty` becomes false.
- Archive a release and environment lock under a persistent DOI.

## 9. Bottom line

The defensible novelty story is narrow and technical:

> Anharmonic Labs defines and verifies a canonical unitary obtained by applying
> symmetric polar orthogonalization to a deterministic golden-ratio
> nonuniform Fourier dictionary, and surrounds it with unusually explicit
> capability boundaries and cross-layer reproducibility controls.

The statevector simulator, Löwdin step, Qiskit embedding, product-state format,
tomography, metrics, and hashing are supporting established methods. The
fixed-buffer native schedule may become a separate research contribution, but
today it is a deterministic bounded-memory phase sketch without an arbitrary
input, decoder, or preservation theorem.
