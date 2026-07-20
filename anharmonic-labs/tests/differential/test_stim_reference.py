from __future__ import annotations

import pytest

pytest.importorskip("stim")

from anharmonic.references.stim_adapter import evolve_clifford
from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import StatevectorSimulator


def test_stim_ghz_clifford_only() -> None:
    operations = [("h", (0,)), ("cx", (0, 2)), ("cx", (2, 1))]
    native = StatevectorSimulator(3).h(0).cx(0, 2).cx(2, 1).statevector()
    assert compare_statevectors(native, evolve_clifford(3, operations))["passed"]
