from __future__ import annotations

import ctypes

import numpy as np

from anharmonic.statevector import StatevectorSimulator
from anharmonic.structured.engine import KernelParams
from anharmonic.structured.reconstruction import reconstruct_product_state
from anharmonic.structured.state import ProductState
from anharmonic.structured.validation import validate_product_reconstruction


def test_ctypes_params_includes_variant_after_boolean_fields() -> None:
    names = [name for name, _ in KernelParams._fields_]
    assert names == [
        "num_labels", "compression_size", "phi", "normalization",
        "use_simd", "use_assembly", "variant",
    ]
    assert KernelParams.variant.offset > KernelParams.use_assembly.offset
    # LP64 C ABI: four 8-byte fields, two bools, 2 bytes padding, one enum.
    assert ctypes.sizeof(KernelParams) == 40


def test_phi_product_reconstruction_matches_exact_initialization() -> None:
    state = ProductState.phi_schedule(6)
    reconstructed = reconstruct_product_state(state)
    exact = StatevectorSimulator(6, reconstructed).statevector()
    assert np.allclose(exact, reconstructed)
    result = validate_product_reconstruction(state)
    assert result["passed"]


def test_structured_representation_is_deterministic_and_normalized() -> None:
    left = ProductState.phi_schedule(12)
    right = ProductState.phi_schedule(12)
    assert np.array_equal(left.factors, right.factors)
    assert np.allclose(np.linalg.norm(left.factors, axis=1), 1.0)
