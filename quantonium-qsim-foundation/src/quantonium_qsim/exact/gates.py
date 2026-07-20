"""Gate matrices for the exact simulator.

For multi-qubit matrices, the first target in ``targets`` is the least
significant local bit. This matches Qiskit's little-endian statevector ABI.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

ComplexMatrix = NDArray[np.complex128]
I = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.diag([1, -1]).astype(np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
S = np.diag([1, 1j]).astype(np.complex128)
SDG = S.conj().T
T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(np.complex128)
TDG = T.conj().T

# Local bit 0 is control, local bit 1 is target.
CX = np.array(
    [[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]],
    dtype=np.complex128,
)
CY = np.array(
    [[1, 0, 0, 0], [0, 0, 0, -1j], [0, 0, 1, 0], [0, 1j, 0, 0]],
    dtype=np.complex128,
)
CZ = np.diag([1, 1, 1, -1]).astype(np.complex128)
SWAP = np.array(
    [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
    dtype=np.complex128,
)


def rx(theta: float) -> ComplexMatrix:
    half = float(theta) / 2.0
    return np.cos(half) * I - 1j * np.sin(half) * X


def ry(theta: float) -> ComplexMatrix:
    half = float(theta) / 2.0
    return np.cos(half) * I - 1j * np.sin(half) * Y


def rz(theta: float) -> ComplexMatrix:
    half = float(theta) / 2.0
    return np.diag([np.exp(-1j * half), np.exp(1j * half)]).astype(np.complex128)


def phase(theta: float) -> ComplexMatrix:
    return np.diag([1.0, np.exp(1j * float(theta))]).astype(np.complex128)


NAMED_GATES = {
    "i": I, "x": X, "y": Y, "z": Z, "h": H, "s": S, "sdg": SDG,
    "t": T, "tdg": TDG, "cx": CX, "cy": CY, "cz": CZ, "swap": SWAP,
}
