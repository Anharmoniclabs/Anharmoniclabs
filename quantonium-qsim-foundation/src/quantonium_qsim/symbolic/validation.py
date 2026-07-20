"""Validation metrics restricted to representable product states."""

from __future__ import annotations

import numpy as np

from quantonium_qsim.exact.observables import fidelity
from .reconstruction import reconstruct_product_state
from .state import PhiStructuredState


def validate_product_reconstruction(state: PhiStructuredState) -> dict[str, float | bool]:
    exact = reconstruct_product_state(state)
    reconstructed = reconstruct_product_state(
        PhiStructuredState(state.compressed_coefficients().reshape(-1, 2))
    )
    error = float(np.linalg.norm(exact - reconstructed))
    score = fidelity(exact, reconstructed)
    return {
        "fidelity": score,
        "reconstruction_error": error,
        "compression_ratio": state.compression_ratio,
        "passed": score >= 1.0 - 1e-12 and error <= 1e-11,
    }
