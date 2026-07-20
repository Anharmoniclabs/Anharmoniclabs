"""Manual IBM Runtime helpers. Importing this module never submits a job."""

from __future__ import annotations

import os
from itertools import product
from typing import Any

import numpy as np

from quantonium_qsim.exact.gates import I, X, Y, Z


def runtime_service() -> Any:
    """Create a service from environment/config; credentials are never persisted."""
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:  # pragma: no cover
        raise ImportError("install the ibm extra") from exc
    token = os.environ.get("IBM_QUANTUM_API_KEY")
    instance = os.environ.get("IBM_QUANTUM_CRN")
    if not token:
        raise RuntimeError("IBM_QUANTUM_API_KEY is not set")
    kwargs = {"channel": "ibm_quantum_platform", "token": token}
    if instance:
        kwargs["instance"] = instance
    return QiskitRuntimeService(**kwargs)


def submit_sampler_v2(circuits: list[Any], backend: Any, *, shots: int, confirm: bool = False) -> Any:
    """Submit already-transpiled ISA circuits only after explicit confirmation."""
    if not confirm:
        raise RuntimeError("hardware submission requires confirm=True")
    from qiskit_ibm_runtime import SamplerV2
    return SamplerV2(mode=backend).run(circuits, shots=shots)


def tomography_measurement_circuits(circuit: Any) -> dict[str, Any]:
    """Return all X/Y/Z product-basis measurements for one- or two-label states."""
    if circuit.num_qubits not in (1, 2):
        raise ValueError("tomography protocol is intentionally limited to one or two labels")
    result = {}
    for setting in product("XYZ", repeat=circuit.num_qubits):
        measured = circuit.copy(name=f"{circuit.name}_tomography_{''.join(setting)}")
        for q, basis in enumerate(setting):
            if basis == "X":
                measured.h(q)
            elif basis == "Y":
                measured.sdg(q)
                measured.h(q)
        measured.measure_all()
        result["".join(setting)] = measured
    return result


def reconstruct_pauli_tomography(
    counts_by_setting: dict[str, dict[str, int]], num_qubits: int
) -> np.ndarray:
    """Linear-inversion density matrix from complete X/Y/Z product counts."""
    if num_qubits not in (1, 2):
        raise ValueError("tomography reconstruction supports one or two labels")
    paulis = {"I": I, "X": X, "Y": Y, "Z": Z}
    rho = np.zeros((1 << num_qubits, 1 << num_qubits), dtype=np.complex128)
    for label in product("IXYZ", repeat=num_qubits):  # label indexed q0, q1
        setting = "".join(char if char != "I" else "Z" for char in label)
        counts = counts_by_setting.get(setting)
        if not counts:
            raise ValueError(f"missing tomography setting {setting}")
        shots = sum(counts.values())
        expectation = 0.0
        for bitstring, count in counts.items():
            compact = bitstring.replace(" ", "")
            parity = 1
            for q, char in enumerate(label):
                if char != "I" and compact[-1 - q] == "1":
                    parity *= -1
            expectation += parity * count / shots
        matrix = np.array([[1.0 + 0j]])
        for char in reversed(label):
            matrix = np.kron(matrix, paulis[char])
        rho += expectation * matrix
    rho /= 1 << num_qubits
    return (rho + rho.conj().T) / 2.0
