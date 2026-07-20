"""Statevector comparison up to physically irrelevant global phase."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _validated_pair(reference: ArrayLike, candidate: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    left = np.asarray(reference, dtype=np.complex128)
    right = np.asarray(candidate, dtype=np.complex128)
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape or left.size == 0:
        raise ValueError("statevectors must be non-empty one-dimensional arrays of equal shape")
    return left, right


def align_global_phase(reference: ArrayLike, candidate: ArrayLike) -> NDArray[np.complex128]:
    """Return ``candidate`` phase-aligned to ``reference``."""
    left, right = _validated_pair(reference, candidate)
    overlap = np.vdot(right, left)
    if abs(overlap) <= np.finfo(np.float64).tiny:
        return np.asarray(right, dtype=np.complex128)
    phase = overlap / abs(overlap)
    return np.asarray(right * phase, dtype=np.complex128)


def statevector_error(reference: ArrayLike, candidate: ArrayLike) -> float:
    """Return relative L2 error after optimal global-phase alignment."""
    left, right = _validated_pair(reference, candidate)
    aligned = align_global_phase(left, right)
    denominator = max(float(np.linalg.norm(left)), np.finfo(np.float64).tiny)
    return float(np.linalg.norm(left - aligned) / denominator)
