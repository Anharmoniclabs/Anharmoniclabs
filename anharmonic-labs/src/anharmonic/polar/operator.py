"""Configurable construction API for the Anharmonic Labs polar operator.

Convention
----------
    f_k = frac((k + 1) * phi)
    Phi[n, k] = exp(2*pi*i*f_k*n) / sqrt(N)
    U = Phi @ (Phi^H @ Phi)^(-1/2)
    forward(x) = U^H @ x
    inverse(X) = U @ X

The inverse square root is formed from a Hermitian eigendecomposition. No FFT,
DCT, identity, raw-dictionary, or approximate fallback is used.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .canonical import (
    PHI,
    canonical_polar_basis,
    polar_forward as canonical_polar_forward,
    polar_inverse as canonical_polar_inverse,
)

def _validate_size(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, (int, np.integer)):
        raise TypeError("size must be an integer")
    size = int(size)
    if size < 1:
        raise ValueError("size must be positive")
    return size


def phase_frequencies(size: int, *, phase_ratio: float = PHI) -> NDArray[np.float64]:
    """Return the canonical fractional frequency schedule."""
    if phase_ratio == PHI:
        from .canonical import phase_frequencies as canonical_frequencies
        return canonical_frequencies(size)
    size = _validate_size(size)
    if not np.isfinite(phase_ratio):
        raise ValueError("phase_ratio must be finite")
    k = np.arange(size, dtype=np.float64)
    return np.mod((k + 1.0) * float(phase_ratio), 1.0).astype(np.float64)


def raw_phase_basis(size: int, *, phase_ratio: float = PHI) -> NDArray[np.complex128]:
    """Return the raw, generally non-orthogonal, square phi-grid basis."""
    if phase_ratio == PHI:
        from .canonical import raw_phase_basis as canonical_raw_basis
        return canonical_raw_basis(size)
    size = _validate_size(size)
    n = np.arange(size, dtype=np.float64)[:, np.newaxis]
    frequencies = phase_frequencies(size, phase_ratio=phase_ratio)[np.newaxis, :]
    basis = np.exp(2j * np.pi * n * frequencies) / np.sqrt(size)
    return np.asarray(basis, dtype=np.complex128)


def canonical_polar_operator(
    size: int,
    *,
    phase_ratio: float = PHI,
    eigenvalue_tolerance: float | None = None,
) -> NDArray[np.complex128]:
    """Construct the canonical unitary Polar basis matrix ``U``.

    ``eigenvalue_tolerance`` protects against numerically singular Gram
    matrices. When omitted, a dimension-scaled floating-point tolerance is
    used. The function never silently substitutes a different transform.
    """
    if phase_ratio == PHI and eigenvalue_tolerance is None:
        return canonical_polar_basis(size)
    size = _validate_size(size)
    phi_basis = raw_phase_basis(size, phase_ratio=phase_ratio)
    gram = phi_basis.conj().T @ phi_basis
    eigenvalues, eigenvectors = np.linalg.eigh(gram)

    largest = float(np.max(eigenvalues))
    tolerance = (
        float(eigenvalue_tolerance)
        if eigenvalue_tolerance is not None
        else np.finfo(np.float64).eps * max(1, size) * max(1.0, largest) * 64.0
    )
    if tolerance < 0 or not np.isfinite(tolerance):
        raise ValueError("eigenvalue_tolerance must be finite and non-negative")
    if float(np.min(eigenvalues)) <= tolerance:
        raise np.linalg.LinAlgError(
            "Polar Gram matrix is numerically singular at the requested size"
        )

    inverse_sqrt = (
        eigenvectors
        * (1.0 / np.sqrt(eigenvalues))[np.newaxis, :]
    ) @ eigenvectors.conj().T
    operator = phi_basis @ inverse_sqrt
    return np.asarray(operator, dtype=np.complex128)


def polar_forward(
    state: ArrayLike,
    *,
    operator: NDArray[np.complex128] | None = None,
) -> NDArray[np.complex128]:
    """Apply the canonical analysis transform ``U^H @ state``."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("state must be a non-empty one-dimensional vector")
    if operator is None:
        return canonical_polar_forward(vector)
    transform = np.asarray(operator)
    if transform.shape != (vector.size, vector.size):
        raise ValueError("operator shape must match state dimension")
    return np.asarray(transform.conj().T @ vector, dtype=np.complex128)


def polar_inverse(
    coefficients: ArrayLike,
    *,
    operator: NDArray[np.complex128] | None = None,
) -> NDArray[np.complex128]:
    """Apply canonical synthesis ``U @ coefficients``."""
    vector = np.asarray(coefficients, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("coefficients must be a non-empty one-dimensional vector")
    if operator is None:
        return canonical_polar_inverse(vector)
    transform = np.asarray(operator)
    if transform.shape != (vector.size, vector.size):
        raise ValueError("operator shape must match coefficient dimension")
    return np.asarray(transform @ vector, dtype=np.complex128)
