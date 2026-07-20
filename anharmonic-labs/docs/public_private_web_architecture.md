# Public simulation UI and private compute boundary

## Decision

Anharmonic Labs publishes a static quantum-simulation workbench through GitHub
Pages. The public application demonstrates standard finite-dimensional quantum
mathematics: state initialization, gate composition, exact complex amplitudes,
probabilities, seeded sampling, and established example circuits.

Research operator construction and native structured routines are not browser
features. They must execute in a separately deployed private service if they
are offered through the public product at all.

```text
GitHub Pages                         Private environment
┌──────────────────────────┐        ┌────────────────────────────┐
│ Static UX                │        │ Versioned research engine  │
│ Standard gate simulator  │        │ Private parameters         │
│ Public mathematics       │        │ Native implementation      │
└─────────────┬────────────┘        └──────────────┬─────────────┘
              │ bounded job request                │
              └───────────────────────────────────►│
              │ aggregate/measurement result       │
              ◄────────────────────────────────────┘
```

## What is safe to publish

- Standard one- and two-system gate matrices.
- Generic statevector evolution and measurement mathematics.
- Circuit-building controls and educational explanations.
- Public verification summaries with accurate limitations.
- An opaque identifier for a server capability, if a private service exists.

## What must not enter the Pages artifact

- Research frequency schedules, dictionaries, operator matrices, or their
  construction code.
- Native research libraries, WebAssembly builds, coefficients, or frozen basis
  fixtures.
- Source maps or build artifacts derived from private implementation code.
- API credentials, signing keys, provider tokens, or privileged service URLs.
- Error messages, traces, or manifests that reveal private parameters.

GitHub Pages publishes from the repository root. The browser entrypoint imports
only `assets/`; those files must be reviewed as a completely public artifact
before every release.

## Service contract principles

Do not expose an unrestricted endpoint of the form:

```text
arbitrary complex vector -> complete transformed complex vector
```

For a linear operator, callers can submit computational basis vectors and
recover the operator one column at a time. Hiding its source code would not hide
its behavior.

If protected compute is later enabled, prefer a job-oriented contract:

```text
POST /v1/simulations
{
  "experiment": "published-capability-id",
  "circuit": [/* validated public operations */],
  "shots": 1024,
  "seed": 79
}

202 Accepted
{
  "job_id": "opaque-id",
  "status": "queued"
}
```

The result should be bounded to the product's actual need, such as measurement
counts and signed integrity metadata. It should not return internal matrices,
full diagnostic traces, or private coefficients. Enforce request schemas,
dimension and shot limits, rate limits, audit logging, output review, and
versioned capability identifiers on the server.

Even a measurement-only service can leak operator behavior through repeated
queries or process tomography. Rate limits and restricted experiment families
reduce that exposure; they do not mathematically eliminate it. Decide what
behavior may safely become observable before connecting the service.

## Current confidentiality status

The Pages artifact does not contain the protected operator construction.
However, the surrounding repository currently contains research source code,
mathematical documentation, fixtures, and historical public provenance. A
public repository is not a trade-secret boundary, and deleting or renaming a
public disclosure does not reverse that disclosure.

Before treating any future implementation as confidential:

1. Identify which material is already public and which improvements are truly
   unpublished.
2. Keep unpublished implementations in a private repository with restricted
   access and secret-scanning enabled.
3. Publish only reviewed static browser assets from the Pages source branch.
4. Deploy private compute independently; GitHub Pages cannot run server-side
   Python or native code.
5. Obtain appropriate intellectual-property advice before relying on trade
   secret or patent treatment.

## Browser simulator scope

The current public core supports H, X, Y, Z, S, T, RX, RY, RZ, CX, CY, CZ, and
SWAP for one through six two-level systems. It displays amplitudes,
probabilities, normalization, Shannon entropy of the basis distribution,
support size, and deterministic measurement sampling. Its little-endian
convention matches the Python statevector engine.

This is a classical exact simulator. It makes no claim of quantum advantage,
hardware execution, general noise modeling, or protected-operator execution.
