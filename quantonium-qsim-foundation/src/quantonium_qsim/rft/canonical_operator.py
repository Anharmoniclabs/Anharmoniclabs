"""Canonical square Resonant Fourier Transform operator.

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

PHI: float = (1.0 + np.sqrt(5.0)) / 2.0


def _validate_size(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, (int, np.integer)):
        raise TypeError("size must be an integer")
    size = int(size)
    if size < 1:
        raise ValueError("size must be positive")
    return size


def rft_frequencies(size: int, *, phase_ratio: float = PHI) -> NDArray[np.float64]:
    """Return the canonical fractional frequency schedule."""
    size = _validate_size(size)
    if not np.isfinite(phase_ratio):
        raise ValueError("phase_ratio must be finite")
    k = np.arange(size, dtype=np.float64)
    return np.mod((k + 1.0) * float(phase_ratio), 1.0).astype(np.float64)


def raw_phi_basis(size: int, *, phase_ratio: float = PHI) -> NDArray[np.complex128]:
    """Return the raw, generally non-orthogonal, square phi-grid basis."""
    size = _validate_size(size)
    n = np.arange(size, dtype=np.float64)[:, np.newaxis]
    frequencies = rft_frequencies(size, phase_ratio=phase_ratio)[np.newaxis, :]
    basis = np.exp(2j * np.pi * n * frequencies) / np.sqrt(size)
    return np.asarray(basis, dtype=np.complex128)


def canonical_rft_operator(
    size: int,
    *,
    phase_ratio: float = PHI,
    eigenvalue_tolerance: float | None = None,
) -> NDArray[np.complex128]:
    """Construct the canonical unitary RFT basis matrix ``U``.

    ``eigenvalue_tolerance`` protects against numerically singular Gram
    matrices. When omitted, a dimension-scaled floating-point tolerance is
    used. The function never silently substitutes a different transform.
    """
    size = _validate_size(size)
    phi_basis = raw_phi_basis(size, phase_ratio=phase_ratio)
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
            "RFT Gram matrix is numerically singular at the requested size"
        )

    inverse_sqrt = (
        eigenvectors
        * (1.0 / np.sqrt(eigenvalues))[np.newaxis, :]
    ) @ eigenvectors.conj().T
    operator = phi_basis @ inverse_sqrt
    return np.asarray(operator, dtype=np.complex128)


def forward_rft(
    state: ArrayLike,
    *,
    operator: NDArray[np.complex128] | None = None,
) -> NDArray[np.complex128]:
    """Apply the canonical analysis transform ``U^H @ state``."""
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("state must be a non-empty one-dimensional vector")
    transform = canonical_rft_operator(vector.size) if operator is None else np.asarray(operator)
    if transform.shape != (vector.size, vector.size):
        raise ValueError("operator shape must match state dimension")
    return np.asarray(transform.conj().T @ vector, dtype=np.complex128)


def inverse_rft(
    coefficients: ArrayLike,
    *,
    operator: NDArray[np.complex128] | None = None,
) -> NDArray[np.complex128]:
    """Apply canonical synthesis ``U @ coefficients``."""
    vector = np.asarray(coefficients, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("coefficients must be a non-empty one-dimensional vector")
    transform = canonical_rft_operator(vector.size) if operator is None else np.asarray(operator)
    if transform.shape != (vector.size, vector.size):
        raise ValueError("operator shape must match coefficient dimension")
    return np.asarray(transform @ vector, dtype=np.complex128)
