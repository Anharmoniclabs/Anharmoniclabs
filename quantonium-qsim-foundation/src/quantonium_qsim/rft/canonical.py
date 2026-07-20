"""Canonical square Resonant Fourier Transform.

This is an independently packaged copy of the QuantoniumOS ``phi-grid-polar-v1``
definition.  It deliberately has no alternative transform or large-size fallback.
Rows are samples, columns are basis vectors; forward is ``U.conj().T @ x``.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache

import numpy as np
from numpy.typing import ArrayLike, NDArray

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0
FORMULA_VERSION = "phi-grid-polar-v1"
PORTABLE_HASH_DECIMALS = 10
MAX_DENSE_SIZE = 4096


def _size(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise TypeError("size must be a positive integer")
    value = int(value)
    if value <= 0:
        raise ValueError("size must be a positive integer")
    if value > MAX_DENSE_SIZE:
        raise NotImplementedError(
            f"exact canonical RFT size {value} exceeds dense safety limit "
            f"{MAX_DENSE_SIZE}; no substitute transform is permitted"
        )
    return value


def rft_frequencies(size: int) -> NDArray[np.float64]:
    size = _size(size)
    return np.array([np.modf((k + 1) * PHI)[0] for k in range(size)])


def raw_phi_basis(size: int) -> NDArray[np.complex128]:
    size = _size(size)
    n = np.arange(size, dtype=np.float64)
    return np.asarray(
        np.exp(2j * np.pi * np.outer(n, rft_frequencies(size))) / np.sqrt(size),
        dtype=np.complex128,
    )


@lru_cache(maxsize=64)
def _basis(size: int) -> NDArray[np.complex128]:
    phi_matrix = raw_phi_basis(size)
    gram = phi_matrix.conj().T @ phi_matrix
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    # This matches the canonical authority. The tiny term avoids division by
    # zero without changing the transform to a pseudoinverse or fallback.
    eigenvalues = np.maximum(eigenvalues, 0.0)
    gram_inverse_sqrt = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues + 1e-300))
        @ eigenvectors.conj().T
    )
    result = np.asarray(phi_matrix @ gram_inverse_sqrt, dtype=np.complex128)
    result.setflags(write=False)
    return result


def canonical_rft_basis(size: int) -> NDArray[np.complex128]:
    """Return ``U = Phi (Phi^H Phi)^(-1/2)`` as a read-only matrix."""
    return _basis(_size(size))


def canonical_rft_forward(values: ArrayLike) -> NDArray[np.complex128]:
    vector = _vector(values, "values")
    return np.asarray(canonical_rft_basis(vector.size).conj().T @ vector)


def canonical_rft_inverse(coefficients: ArrayLike) -> NDArray[np.complex128]:
    vector = _vector(coefficients, "coefficients")
    return np.asarray(canonical_rft_basis(vector.size) @ vector)


def _vector(values: ArrayLike, name: str) -> NDArray[np.complex128]:
    vector = np.asarray(values, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError(f"{name} must be a non-empty vector")
    _size(vector.size)
    return vector


def canonical_basis_portable_bytes(
    basis: ArrayLike, decimals: int = PORTABLE_HASH_DECIMALS
) -> bytes:
    matrix = np.asarray(basis, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("basis must be square")
    real = np.round(matrix.real, decimals=decimals)
    imag = np.round(matrix.imag, decimals=decimals)
    cutoff = 0.5 * 10.0 ** (-decimals)
    real[np.abs(real) < cutoff] = 0.0
    imag[np.abs(imag) < cutoff] = 0.0
    interleaved = np.empty(matrix.size * 2, dtype="<f8")
    interleaved[0::2] = real.ravel(order="C")
    interleaved[1::2] = imag.ravel(order="C")
    return interleaved.tobytes()


def canonical_basis_sha256(size: int) -> str:
    return hashlib.sha256(
        canonical_basis_portable_bytes(canonical_rft_basis(size))
    ).hexdigest()


__all__ = [
    "PHI", "FORMULA_VERSION", "PORTABLE_HASH_DECIMALS", "canonical_rft_basis",
    "canonical_rft_forward", "canonical_rft_inverse", "canonical_basis_sha256",
    "canonical_basis_portable_bytes", "raw_phi_basis", "rft_frequencies",
]
