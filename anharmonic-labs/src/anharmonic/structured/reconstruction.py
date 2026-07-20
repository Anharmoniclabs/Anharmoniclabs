"""Small-state reconstruction for the restricted product family."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .state import ProductState


def reconstruct_product_state(
    state: ProductState, *, max_labels: int = 20
) -> NDArray[np.complex128]:
    if state.num_labels > max_labels:
        raise ValueError(
            f"full reconstruction disabled above {max_labels} labels; "
            "the structured representation remains available"
        )
    result = np.array([1.0 + 0.0j])
    # Highest label is the leftmost Kronecker factor; label 0 is the LSB.
    for factor in reversed(state.factors):
        result = np.kron(result, factor)
    return np.asarray(result, dtype=np.complex128)


def reconstruct_factors(
    coefficients: ArrayLike, *, max_labels: int = 20
) -> NDArray[np.complex128]:
    values = np.asarray(coefficients, dtype=np.complex128)
    if values.ndim != 1 or values.size % 2 or values.size == 0:
        raise ValueError("coefficients must contain two values per label")
    return reconstruct_product_state(
        ProductState(values.reshape(-1, 2)), max_labels=max_labels
    )
