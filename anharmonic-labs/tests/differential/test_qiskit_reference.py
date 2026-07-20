from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qiskit")

from anharmonic.references.qiskit_adapter import evolve
from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import StatevectorSimulator
from anharmonic.statevector import gates


@pytest.mark.parametrize("qubits", [1, 2, 3, 4])
def test_qiskit_randomized_layouts(qubits: int) -> None:
    rng = np.random.default_rng(900 + qubits)
    state = rng.normal(size=1 << qubits) + 1j * rng.normal(size=1 << qubits)
    state /= np.linalg.norm(state)
    operations = []
    for _ in range(8):
        operations.append((gates.rz(float(rng.normal())), (int(rng.integers(qubits)),)))
        if qubits > 1:
            operations.append((gates.CX, tuple(int(x) for x in rng.choice(qubits, 2, replace=False))))
    native = StatevectorSimulator(qubits, state)
    for matrix, targets in operations:
        native.apply_unitary(matrix, targets)
    assert compare_statevectors(evolve(state, operations), native.statevector())["passed"]
