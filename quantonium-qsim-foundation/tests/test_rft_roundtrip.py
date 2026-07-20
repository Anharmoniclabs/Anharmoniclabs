import numpy as np
import pytest

from quantonium_qsim.rft import canonical_rft_operator, norm_preservation_error, roundtrip_error


@pytest.mark.parametrize("size", [2, 4, 8, 16])
def test_roundtrip_and_norm_preservation(size: int) -> None:
    rng = np.random.default_rng(1000 + size)
    state = rng.normal(size=size) + 1j * rng.normal(size=size)
    operator = canonical_rft_operator(size)
    assert roundtrip_error(state, operator) < 1e-11
    assert norm_preservation_error(state, operator) < 1e-11
