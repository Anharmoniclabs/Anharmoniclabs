"""Exact statevector simulation of canonical RFT matrices."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from quantonium_qsim.rft.canonical_operator import canonical_rft_operator
from .circuits import qubit_count


def normalize_state(state: ArrayLike) -> NDArray[np.complex128]:
    """Return a normalized complex statevector."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("state must be a non-empty one-dimensional vector")
    qubit_count(vector.size)
    norm = float(np.linalg.norm(vector))
    if norm == 0.0 or not np.isfinite(norm):
        raise ValueError("state must have a finite, non-zero norm")
    return np.asarray(vector / norm, dtype=np.complex128)


def simulate_rft_statevector(
    state: ArrayLike,
    *,
    direction: str = "forward",
) -> NDArray[np.complex128]:
    """Apply the RFT through Qiskit's exact Statevector/Operator machinery."""
    try:
        from qiskit.quantum_info import Operator, Statevector
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("Install the 'quantum' extra to run Qiskit simulation") from exc

    normalized = normalize_state(state)
    operator = canonical_rft_operator(normalized.size)
    if direction == "forward":
        matrix = operator.conj().T
    elif direction == "inverse":
        matrix = operator
    else:
        raise ValueError("direction must be 'forward' or 'inverse'")
    result = Statevector(normalized).evolve(Operator(matrix))
    return np.asarray(result.data, dtype=np.complex128)
