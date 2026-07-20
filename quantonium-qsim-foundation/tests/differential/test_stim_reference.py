from __future__ import annotations

import pytest

pytest.importorskip("stim")

from quantonium_qsim.adapters.stim_adapter import evolve_clifford
from quantonium_qsim.benchmarks.metrics import compare_statevectors
from quantonium_qsim.exact import ExactSimulator


def test_stim_ghz_clifford_only() -> None:
    operations = [("h", (0,)), ("cx", (0, 2)), ("cx", (2, 1))]
    native = ExactSimulator(3).h(0).cx(0, 2).cx(2, 1).statevector()
    assert compare_statevectors(native, evolve_clifford(3, operations))["passed"]
