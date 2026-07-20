"""Optional Qulacs statevector reference adapter."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

Operation = tuple[ArrayLike, Sequence[int]]


def evolve(initial_state: ArrayLike, operations: Iterable[Operation]) -> NDArray[np.complex128]:
    try:
        from qulacs import QuantumState
        from qulacs.gate import DenseMatrix
    except ImportError as exc:  # pragma: no cover
        raise ImportError("install the qulacs extra") from exc
    vector = np.asarray(initial_state, dtype=np.complex128)
    state = QuantumState(int(np.log2(vector.size)))
    state.load(vector)
    for matrix, targets in operations:
        DenseMatrix(list(targets), np.asarray(matrix, dtype=np.complex128)).update_quantum_state(state)
    return np.asarray(state.get_vector(), dtype=np.complex128)
