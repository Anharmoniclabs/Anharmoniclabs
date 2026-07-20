"""Statevector observables and density-matrix diagnostics."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .gates import I, X, Y, Z


def density_matrix(state: ArrayLike) -> NDArray[np.complex128]:
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1:
        raise ValueError("state must be a vector")
    return np.outer(vector, vector.conj())


def reduced_density_matrix(
    state: ArrayLike, keep_qubits: list[int] | tuple[int, ...], num_qubits: int
) -> NDArray[np.complex128]:
    """Trace out all but ``keep_qubits`` using little-endian local indexing."""
    vector = np.asarray(state, dtype=np.complex128)
    keep = tuple(int(q) for q in keep_qubits)
    if len(set(keep)) != len(keep) or any(q < 0 or q >= num_qubits for q in keep):
        raise ValueError("keep_qubits contains an invalid or duplicate qubit")
    traced = tuple(q for q in range(num_qubits) if q not in keep)
    result = np.zeros((1 << len(keep), 1 << len(keep)), dtype=np.complex128)
    for row, amplitude_row in enumerate(vector):
        env_row = sum(((row >> q) & 1) << pos for pos, q in enumerate(traced))
        local_row = sum(((row >> q) & 1) << pos for pos, q in enumerate(keep))
        for col, amplitude_col in enumerate(vector):
            env_col = sum(((col >> q) & 1) << pos for pos, q in enumerate(traced))
            if env_row == env_col:
                local_col = sum(((col >> q) & 1) << pos for pos, q in enumerate(keep))
                result[local_row, local_col] += amplitude_row * amplitude_col.conjugate()
    return result


def partial_trace(
    state: ArrayLike, trace_qubits: list[int] | tuple[int, ...], num_qubits: int
) -> NDArray[np.complex128]:
    trace = set(int(q) for q in trace_qubits)
    if len(trace) != len(trace_qubits):
        raise ValueError("trace_qubits contains duplicates")
    keep = [q for q in range(num_qubits) if q not in trace]
    return reduced_density_matrix(state, keep, num_qubits)


def purity(state_or_density: ArrayLike) -> float:
    value = np.asarray(state_or_density, dtype=np.complex128)
    rho = density_matrix(value) if value.ndim == 1 else value
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("input must be a statevector or square density matrix")
    return float(np.trace(rho @ rho).real)


def fidelity(left: ArrayLike, right: ArrayLike) -> float:
    """Pure-state fidelity, or density-matrix fidelity when SciPy is available."""
    a = np.asarray(left, dtype=np.complex128)
    b = np.asarray(right, dtype=np.complex128)
    if a.ndim == b.ndim == 1:
        return float(np.clip(abs(np.vdot(a, b)) ** 2, 0.0, 1.0))
    if a.ndim == 1:
        return float(np.clip(np.vdot(a, b @ a).real, 0.0, 1.0))
    if b.ndim == 1:
        return float(np.clip(np.vdot(b, a @ b).real, 0.0, 1.0))
    try:
        from scipy.linalg import sqrtm
    except ImportError as exc:  # pragma: no cover
        raise ImportError("density-matrix fidelity requires scipy") from exc
    root = sqrtm(a)
    value = np.trace(sqrtm(root @ b @ root)).real
    return float(np.clip(value * value, 0.0, 1.0))


def pauli_matrix(label: str) -> NDArray[np.complex128]:
    """Build a Pauli matrix; label leftmost character is highest qubit."""
    matrices = {"I": I, "X": X, "Y": Y, "Z": Z}
    if not label or any(char not in matrices for char in label.upper()):
        raise ValueError("Pauli label must contain only I, X, Y and Z")
    result = np.array([[1.0 + 0j]])
    for char in label.upper():
        result = np.kron(result, matrices[char])
    return result


def expectation_value(state: ArrayLike, observable: ArrayLike | str) -> complex:
    vector = np.asarray(state, dtype=np.complex128)
    matrix = pauli_matrix(observable) if isinstance(observable, str) else np.asarray(observable)
    if matrix.shape != (vector.size, vector.size):
        raise ValueError("observable dimension does not match state")
    value = complex(np.vdot(vector, matrix @ vector))
    return complex(value.real if abs(value.imag) < 1e-14 else value)
