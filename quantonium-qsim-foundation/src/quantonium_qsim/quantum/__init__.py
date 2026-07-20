"""Quantum-circuit and statevector adapters."""

from .circuits import build_qft_circuit, build_rft_circuit, qubit_count
from .simulation import normalize_state, simulate_rft_statevector

__all__ = [
    "build_qft_circuit",
    "build_rft_circuit",
    "qubit_count",
    "normalize_state",
    "simulate_rft_statevector",
]
