from __future__ import annotations

from itertools import product

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

from quantonium_qsim.adapters.ibm_runtime import (
    reconstruct_pauli_tomography,
    tomography_measurement_circuits,
)


def exact_counts(circuit: QuantumCircuit, shots: int = 4096) -> dict[str, int]:
    unmeasured = circuit.remove_final_measurements(inplace=False)
    probabilities = Statevector.from_instruction(unmeasured).probabilities()
    counts = {format(i, f"0{circuit.num_qubits}b"): int(round(p * shots))
              for i, p in enumerate(probabilities)}
    difference = shots - sum(counts.values())
    counts["0" * circuit.num_qubits] += difference
    return counts


@pytest.mark.parametrize("bell", [False, True])
def test_tomography_reconstructs_known_states(bell: bool) -> None:
    qubits = 2 if bell else 1
    circuit = QuantumCircuit(qubits, name="known")
    if bell:
        circuit.h(0)
        circuit.cx(0, 1)
    else:
        circuit.h(0)
        circuit.s(0)
    ideal = Statevector.from_instruction(circuit)
    measured = tomography_measurement_circuits(circuit)
    counts = {setting: exact_counts(value) for setting, value in measured.items()}
    rho = reconstruct_pauli_tomography(counts, qubits)
    assert state_fidelity(ideal, rho) > 1 - 1e-12
