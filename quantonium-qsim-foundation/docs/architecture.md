# Architecture

```text
canonical formula
      |
      v
src/quantonium_qsim/rft
  raw phi basis -> Gram eigendecomposition -> unitary U
      |
      +--------------------+
      |                    |
      v                    v
numerical validation   Qiskit adapter
U^H U, round trip      UnitaryGate / Operator / Statevector
                           |
                           v
                     circuit metrics
                     generic decomposition vs QFT
```

## Boundaries

- The canonical module contains one square Gram-normalized definition.
- Quantum dimensions must be powers of two.
- The Qiskit unitary is an exact matrix embedding, not an efficient synthesis claim.
- There is no AI, model training, tokenizer, neural network, chat interface, or agent code.
- There is no silent FFT, DCT, identity, raw-basis, or approximate fallback.
- Physical IBM hardware integration is intentionally deferred until simulation and decomposition results justify it.
