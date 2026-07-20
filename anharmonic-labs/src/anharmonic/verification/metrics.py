"""Common correctness and distribution metrics."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def align_global_phase(reference: ArrayLike, candidate: ArrayLike) -> np.ndarray:
    left = np.asarray(reference, dtype=np.complex128)
    right = np.asarray(candidate, dtype=np.complex128)
    if left.shape != right.shape or left.ndim != 1:
        raise ValueError("statevectors must have the same vector shape")
    overlap = np.vdot(right, left)
    return right if abs(overlap) == 0 else right * overlap / abs(overlap)


def compare_statevectors(reference: ArrayLike, candidate: ArrayLike) -> dict[str, float | bool]:
    left = np.asarray(reference, dtype=np.complex128)
    right = np.asarray(candidate, dtype=np.complex128)
    aligned = align_global_phase(left, right)
    left_prob = np.abs(left) ** 2
    right_prob = np.abs(right) ** 2
    fidelity = float(abs(np.vdot(left, right)) ** 2)
    l2 = float(np.linalg.norm(left - aligned))
    maximum = float(np.max(np.abs(left - aligned)))
    tvd = 0.5 * float(np.sum(np.abs(left_prob - right_prob)))
    norm_error = abs(float(np.linalg.norm(right)) - 1.0)
    return {
        "state_fidelity": fidelity,
        "global_phase_adjusted_l2_error": l2,
        "maximum_amplitude_error": maximum,
        "probability_tvd": tvd,
        "norm_error": norm_error,
        "passed": fidelity >= 1.0 - 1e-12 and l2 <= 1e-11
        and maximum <= 1e-11 and norm_error <= 1e-12,
    }


def compare_distributions(reference: ArrayLike, candidate: ArrayLike) -> dict[str, float]:
    p = np.asarray(reference, dtype=np.float64)
    q = np.asarray(candidate, dtype=np.float64)
    if p.shape != q.shape or not np.isclose(p.sum(), 1.0) or not np.isclose(q.sum(), 1.0):
        raise ValueError("distributions must have equal shape and sum to one")
    coefficient = float(np.sum(np.sqrt(p * q)))
    return {
        "total_variation_distance": 0.5 * float(np.sum(np.abs(p - q))),
        "hellinger_distance": float(np.sqrt(max(0.0, 1.0 - coefficient))),
        "distribution_fidelity": coefficient * coefficient,
    }
