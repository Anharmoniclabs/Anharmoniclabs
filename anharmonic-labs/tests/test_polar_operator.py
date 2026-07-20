import numpy as np
import pytest

from anharmonic.polar import PHI, canonical_polar_operator, raw_phase_basis, phase_frequencies, unitarity_error


@pytest.mark.parametrize("size", [1, 2, 4, 8, 16])
def test_operator_shape_dtype_and_unitarity(size: int) -> None:
    operator = canonical_polar_operator(size)
    assert operator.shape == (size, size)
    assert operator.dtype == np.complex128
    assert unitarity_error(operator) < 1e-11


def test_frequency_definition() -> None:
    expected = np.mod(np.arange(1, 5) * PHI, 1.0)
    np.testing.assert_allclose(phase_frequencies(4), expected, atol=0.0, rtol=0.0)


def test_raw_basis_is_not_substituted_for_canonical_operator() -> None:
    raw = raw_phase_basis(8)
    canonical = canonical_polar_operator(8)
    assert np.linalg.norm(raw.conj().T @ raw - np.eye(8)) > 1e-6
    assert unitarity_error(canonical) < 1e-11


@pytest.mark.parametrize("bad_size", [0, -1])
def test_invalid_size_rejected(bad_size: int) -> None:
    with pytest.raises(ValueError):
        canonical_polar_operator(bad_size)


def test_non_integer_size_rejected() -> None:
    with pytest.raises(TypeError):
        canonical_polar_operator(4.0)  # type: ignore[arg-type]
