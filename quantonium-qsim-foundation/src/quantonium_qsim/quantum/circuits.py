"""Qiskit circuit construction for the canonical RFT."""

from __future__ import annotations

import math

import numpy as np

from quantonium_qsim.rft.canonical_operator import canonical_rft_operator


def qubit_count(size: int) -> int:
    """Return log2(size), rejecting non-power-of-two dimensions."""
    if isinstance(size, bool) or not isinstance(size, (int, np.integer)):
        raise TypeError("size must be an integer")
    size = int(size)
    if size < 2 or size & (size - 1):
        raise ValueError("quantum state dimension must be a power of two and at least 2")
    return int(math.log2(size))


def _matrix_for_direction(size: int, direction: str) -> np.ndarray:
    operator = canonical_rft_operator(size)
    if direction == "forward":
        return operator.conj().T
    if direction == "inverse":
        return operator
    raise ValueError("direction must be 'forward' or 'inverse'")


def build_rft_circuit(size: int, *, direction: str = "forward"):
    """Build a generic Qiskit unitary circuit for the RFT.

    This is an exact finite matrix embedding, not a claim of efficient circuit
    synthesis.
    """
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import UnitaryGate
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("Install the 'quantum' extra to build Qiskit circuits") from exc

    count = qubit_count(size)
    matrix = _matrix_for_direction(size, direction)
    circuit = QuantumCircuit(count, name=f"rft_{direction}_{size}")
    circuit.append(UnitaryGate(matrix, label=f"RFT-{direction}"), range(count))
    return circuit


def build_qft_circuit(size: int, *, direction: str = "forward"):
    """Build a standard QFT circuit with matching transform orientation."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import QFTGate
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("Install the 'quantum' extra to build Qiskit circuits") from exc

    count = qubit_count(size)
    if direction not in {"forward", "inverse"}:
        raise ValueError("direction must be 'forward' or 'inverse'")
    gate = QFTGate(count)
    # Canonical RFT forward analysis uses an adjoint. Use inverse QFT for the
    # analogous forward-analysis orientation.
    if direction == "forward":
        gate = gate.inverse()
    circuit = QuantumCircuit(count, name=f"qft_{direction}_{size}")
    circuit.append(gate, range(count))
    return circuit
