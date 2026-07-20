import numpy as np

from quantonium_qsim.analysis import align_global_phase, statevector_error


def test_global_phase_is_removed() -> None:
    reference = np.array([1.0, 1j], dtype=np.complex128) / np.sqrt(2)
    candidate = np.exp(0.731j) * reference
    np.testing.assert_allclose(align_global_phase(reference, candidate), reference, atol=1e-14)
    assert statevector_error(reference, candidate) < 1e-14
