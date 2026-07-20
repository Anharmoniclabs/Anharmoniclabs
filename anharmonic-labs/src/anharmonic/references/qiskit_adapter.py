"""Qiskit reference adapter. Never imported by the exact backend."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

Operation = tuple[ArrayLike, Sequence[int]]


def evolve(initial_state: ArrayLike, operations: Iterable[Operation]) -> NDArray[np.complex128]:
    try:
        from qiskit.quantum_info import Operator, Statevector
    except ImportError as exc:  # pragma: no cover
        raise ImportError("install the qiskit extra") from exc
    state = Statevector(np.asarray(initial_state, dtype=np.complex128))
    for matrix, targets in operations:
        state = state.evolve(Operator(np.asarray(matrix, dtype=np.complex128)), qargs=list(targets))
    return np.asarray(state.data, dtype=np.complex128)


def apply_matrix(initial_state: ArrayLike, matrix: ArrayLike) -> NDArray[np.complex128]:
    qubits = int(np.log2(np.asarray(initial_state).size))
    return evolve(initial_state, [(matrix, tuple(range(qubits)))])
