from __future__ import annotations

import numpy as np
import pytest

from anharmonic.statevector import StatevectorSimulator
from anharmonic.statevector.gates import CX, H, X
from anharmonic.statevector.observables import fidelity


def test_basis_states_and_little_endian_x() -> None:
    for index in range(16):
        state = np.eye(16, dtype=np.complex128)[index]
        assert np.array_equal(StatevectorSimulator(4, state).statevector(), state)
    simulator = StatevectorSimulator(3).x(0)
    assert np.argmax(simulator.probabilities()) == 1
    simulator.reset().x(2)
    assert np.argmax(simulator.probabilities()) == 4


def test_bell_ghz_and_nonadjacent_gate() -> None:
    bell = StatevectorSimulator(2).h(0).cx(0, 1)
    expected = np.array([1, 0, 0, 1], dtype=np.complex128) / np.sqrt(2)
    assert fidelity(bell.statevector(), expected) > 1 - 1e-14
    ghz = StatevectorSimulator(4).h(0).cx(0, 3).cx(3, 1).cx(1, 2)
    expected = np.zeros(16, dtype=np.complex128)
    expected[[0, 15]] = 1 / np.sqrt(2)
    assert np.allclose(ghz.statevector(), expected)


def test_arbitrary_unitary_and_invalid_matrix() -> None:
    simulator = StatevectorSimulator(2).apply_unitary(np.kron(H, X), [0, 1])
    assert np.isclose(np.linalg.norm(simulator.statevector()), 1.0)
    with pytest.raises(ValueError, match="not unitary"):
        simulator.apply_unitary(np.ones((2, 2)), [0])


def test_seeded_shots_probabilities_expectation_and_density() -> None:
    simulator = StatevectorSimulator(2, seed=17).h(0).cx(0, 1)
    assert simulator.sample(100) == simulator.sample(100)
    assert np.allclose(simulator.probabilities(), [0.5, 0, 0, 0.5])
    assert simulator.expectation("ZZ") == pytest.approx(1.0)
    reduced = simulator.reduced_density_matrix([0])
    assert np.allclose(reduced, np.eye(2) / 2)
    assert simulator.purity() == pytest.approx(1.0)
    assert simulator.purity([0]) == pytest.approx(0.5)
    assert np.allclose(simulator.partial_trace([1]), reduced)


def test_rotations_phase_and_inverse_pairs() -> None:
    state = StatevectorSimulator(2).h(0).t(0).tdg(0).s(1).sdg(1)
    state.rx(0.3, 0).rx(-0.3, 0).ry(-0.8, 1).ry(0.8, 1)
    state.rz(1.2, 0).rz(-1.2, 0).phase(0.7, 1).phase(-0.7, 1)
    expected = StatevectorSimulator(2).h(0).statevector()
    assert np.allclose(state.statevector(), expected, atol=1e-13)


def test_cx_matrix_abi() -> None:
    # local bit zero is control: |01> -> |11>
    result = StatevectorSimulator(2, np.array([0, 1, 0, 0])).apply_unitary(CX, [0, 1])
    assert np.argmax(result.probabilities()) == 3
