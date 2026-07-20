from __future__ import annotations

import numpy as np
import pytest

from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import StatevectorSimulator
from anharmonic.statevector import gates
from anharmonic.polar import canonical_polar_basis


def dense_embed(matrix: np.ndarray, targets: tuple[int, ...], qubits: int) -> np.ndarray:
    dimension = 1 << qubits
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    target_set = set(targets)
    for column in range(dimension):
        local_column = sum(((column >> q) & 1) << pos for pos, q in enumerate(targets))
        for local_row in range(1 << len(targets)):
            row = column
            for pos, q in enumerate(targets):
                row = (row & ~(1 << q)) | (((local_row >> pos) & 1) << q)
            if all(((row >> q) & 1) == ((column >> q) & 1) for q in range(qubits) if q not in target_set):
                result[row, column] = matrix[local_row, local_column]
    return result


@pytest.mark.parametrize("qubits", [1, 2, 3, 4])
def test_random_circuits_against_direct_numpy(qubits: int) -> None:
    rng = np.random.default_rng(412 + qubits)
    initial = rng.normal(size=1 << qubits) + 1j * rng.normal(size=1 << qubits)
    initial /= np.linalg.norm(initial)
    simulator = StatevectorSimulator(qubits, initial)
    reference = initial
    operations: list[tuple[np.ndarray, tuple[int, ...]]] = []
    for _ in range(12):
        q = int(rng.integers(qubits))
        matrix = gates.rx(float(rng.normal())) if rng.random() < 0.5 else gates.ry(float(rng.normal()))
        operations.append((matrix, (q,)))
        if qubits > 1:
            targets = tuple(int(x) for x in rng.choice(qubits, 2, replace=False))
            operations.append((gates.CX, targets))
    for matrix, targets in operations:
        simulator.apply_unitary(matrix, targets)
        reference = dense_embed(matrix, targets, qubits) @ reference
    metrics = compare_statevectors(reference, simulator.statevector())
    assert metrics["passed"], metrics


@pytest.mark.parametrize("qubits", [1, 2, 3, 4])
def test_polar_forward_inverse_against_numpy(qubits: int) -> None:
    rng = np.random.default_rng(qubits)
    state = rng.normal(size=1 << qubits) + 1j * rng.normal(size=1 << qubits)
    state /= np.linalg.norm(state)
    basis = canonical_polar_basis(state.size)
    forward = StatevectorSimulator(qubits, state).polar_forward().statevector()
    assert compare_statevectors(basis.conj().T @ state, forward)["passed"]
    restored = StatevectorSimulator(qubits, forward).polar_inverse().statevector()
    assert compare_statevectors(state, restored)["passed"]
