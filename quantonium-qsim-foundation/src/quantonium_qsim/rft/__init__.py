"""Canonical Resonant Fourier Transform mathematics."""

from .canonical_operator import (
    PHI,
    canonical_rft_operator,
    forward_rft,
    inverse_rft,
    raw_phi_basis,
    rft_frequencies,
)
from .validation import (
    norm_preservation_error,
    roundtrip_error,
    unitarity_error,
)

__all__ = [
    "PHI",
    "canonical_rft_operator",
    "forward_rft",
    "inverse_rft",
    "raw_phi_basis",
    "rft_frequencies",
    "norm_preservation_error",
    "roundtrip_error",
    "unitarity_error",
]
