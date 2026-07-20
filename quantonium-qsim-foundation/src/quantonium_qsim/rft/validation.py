"""Numerical validation helpers for the canonical RFT."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .canonical_operator import canonical_rft_operator, forward_rft, inverse_rft


def unitarity_error(operator: ArrayLike) -> float:
    """Return the Frobenius norm of ``U^H U - I``."""
    matrix = np.asarray(operator, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    identity = np.eye(matrix.shape[0], dtype=np.complex128)
    return float(np.linalg.norm(matrix.conj().T @ matrix - identity, ord="fro"))


def roundtrip_error(state: ArrayLike, operator: NDArray[np.complex128] | None = None) -> float:
    """Return relative error after forward analysis and inverse synthesis."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("state must be a non-empty one-dimensional vector")
    transform = canonical_rft_operator(vector.size) if operator is None else operator
    reconstructed = inverse_rft(forward_rft(vector, operator=transform), operator=transform)
    denominator = max(float(np.linalg.norm(vector)), np.finfo(np.float64).tiny)
    return float(np.linalg.norm(reconstructed - vector) / denominator)


def norm_preservation_error(state: ArrayLike, operator: NDArray[np.complex128] | None = None) -> float:
    """Return the absolute difference between input and transformed norms."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("state must be a non-empty one-dimensional vector")
    transform = canonical_rft_operator(vector.size) if operator is None else operator
    transformed = forward_rft(vector, operator=transform)
    return float(abs(np.linalg.norm(transformed) - np.linalg.norm(vector)))
