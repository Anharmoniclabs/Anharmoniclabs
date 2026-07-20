from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("cirq")

from anharmonic.references.cirq_adapter import evolve
from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import StatevectorSimulator
from anharmonic.statevector import gates


def test_cirq_phase_sensitive_nonadjacent_circuit() -> None:
    state = np.zeros(16, dtype=np.complex128)
    state[5] = 1 / np.sqrt(2)
    state[10] = 1j / np.sqrt(2)
    operations = [(gates.H, (3,)), (gates.CY, (3, 0)), (gates.rz(0.37), (2,)), (gates.SWAP, (0, 2))]
    native = StatevectorSimulator(4, state)
    for matrix, targets in operations:
        native.apply_unitary(matrix, targets)
    assert compare_statevectors(evolve(state, operations), native.statevector())["passed"]
