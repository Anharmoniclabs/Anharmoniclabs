from __future__ import annotations

import ctypes

import numpy as np

from quantonium_qsim.exact import ExactSimulator
from quantonium_qsim.symbolic.engine import QSCParams
from quantonium_qsim.symbolic.reconstruction import reconstruct_product_state
from quantonium_qsim.symbolic.state import PhiStructuredState
from quantonium_qsim.symbolic.validation import validate_product_reconstruction


def test_ctypes_params_includes_variant_after_boolean_fields() -> None:
    names = [name for name, _ in QSCParams._fields_]
    assert names == [
        "num_qubits", "compression_size", "phi", "normalization",
        "use_simd", "use_assembly", "variant",
    ]
    assert QSCParams.variant.offset > QSCParams.use_assembly.offset
    # LP64 C ABI: four 8-byte fields, two bools, 2 bytes padding, one enum.
    assert ctypes.sizeof(QSCParams) == 40


def test_phi_product_reconstruction_matches_exact_initialization() -> None:
    state = PhiStructuredState.phi_schedule(6)
    reconstructed = reconstruct_product_state(state)
    exact = ExactSimulator(6, reconstructed).statevector()
    assert np.allclose(exact, reconstructed)
    result = validate_product_reconstruction(state)
    assert result["passed"]


def test_symbolic_representation_is_deterministic_and_normalized() -> None:
    left = PhiStructuredState.phi_schedule(12)
    right = PhiStructuredState.phi_schedule(12)
    assert np.array_equal(left.factors, right.factors)
    assert np.allclose(np.linalg.norm(left.factors, axis=1), 1.0)
