import numpy as np
import pytest

qiskit = pytest.importorskip("qiskit")

from quantonium_qsim.analysis import statevector_error
from quantonium_qsim.quantum import build_rft_circuit, normalize_state, qubit_count, simulate_rft_statevector
from quantonium_qsim.rft import canonical_rft_operator


@pytest.mark.parametrize("size", [2, 4, 8, 16])
def test_qiskit_statevector_matches_numpy(size: int) -> None:
    rng = np.random.default_rng(2000 + size)
    state = normalize_state(rng.normal(size=size) + 1j * rng.normal(size=size))
    expected = canonical_rft_operator(size).conj().T @ state
    actual = simulate_rft_statevector(state)
    assert statevector_error(expected, actual) < 1e-12


@pytest.mark.parametrize("size, expected", [(2, 1), (4, 2), (8, 3), (16, 4)])
def test_qubit_count(size: int, expected: int) -> None:
    assert qubit_count(size) == expected


@pytest.mark.parametrize("size", [0, 1, 3, 6])
def test_non_quantum_dimensions_rejected(size: int) -> None:
    with pytest.raises(ValueError):
        qubit_count(size)


def test_circuit_contains_exact_rft_unitary() -> None:
    from qiskit.quantum_info import Operator

    circuit = build_rft_circuit(4)
    expected = canonical_rft_operator(4).conj().T
    np.testing.assert_allclose(Operator(circuit).data, expected, atol=1e-12, rtol=1e-12)
