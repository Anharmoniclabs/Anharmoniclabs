"""Cirq reference adapter with explicit little-endian conversion."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

Operation = tuple[ArrayLike, Sequence[int]]


def evolve(initial_state: ArrayLike, operations: Iterable[Operation]) -> NDArray[np.complex128]:
    try:
        import cirq
    except ImportError as exc:  # pragma: no cover
        raise ImportError("install the cirq extra") from exc
    vector = np.asarray(initial_state, dtype=np.complex128)
    num_qubits = int(np.log2(vector.size))
    qubits = cirq.LineQubit.range(num_qubits)
    circuit = cirq.Circuit()
    for matrix, targets in operations:
        target_tuple = tuple(int(q) for q in targets)
        gate = cirq.MatrixGate(np.asarray(matrix, dtype=np.complex128))
        # Cirq's first gate axis is MSB; Quantonium targets[0] is local LSB.
        circuit.append(gate.on(*(qubits[q] for q in reversed(target_tuple))))
    order = list(reversed(qubits))
    result = cirq.Simulator(dtype=np.complex128).simulate(
        circuit, initial_state=vector, qubit_order=order
    )
    return np.asarray(result.final_state_vector, dtype=np.complex128)


def apply_matrix(initial_state: ArrayLike, matrix: ArrayLike) -> NDArray[np.complex128]:
    qubits = int(np.log2(np.asarray(initial_state).size))
    return evolve(initial_state, [(matrix, tuple(range(qubits)))])
