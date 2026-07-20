from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qulacs")

from anharmonic.references.qulacs_adapter import evolve
from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import StatevectorSimulator
from anharmonic.statevector import gates


def test_qulacs_clifford_and_rotation() -> None:
    initial = np.eye(8, dtype=np.complex128)[0]
    operations = [(gates.H, (0,)), (gates.CX, (0, 2)), (gates.ry(0.41), (1,))]
    native = StatevectorSimulator(3)
    for matrix, targets in operations:
        native.apply_unitary(matrix, targets)
    assert compare_statevectors(evolve(initial, operations), native.statevector())["passed"]
