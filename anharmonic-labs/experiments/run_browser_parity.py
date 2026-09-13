#!/usr/bin/env python3
"""Compare browser-core statevectors with native and optional Qiskit references."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from anharmonic.statevector import StatevectorSimulator, gates

ROOT = Path(__file__).resolve().parents[1]
BROWSER_RUNNER = ROOT.parent / "tests" / "web" / "browser_parity_runner.mjs"


def as_complex(values: list[dict[str, float]]) -> np.ndarray:
    return np.asarray([value["re"] + 1j * value["im"] for value in values], dtype=np.complex128)


def browser_vectors() -> dict[str, np.ndarray]:
    completed = subprocess.run(
        ["node", str(BROWSER_RUNNER)],
        cwd=ROOT.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    return {name: as_complex(values) for name, values in json.loads(completed.stdout).items()}


def native_vectors() -> dict[str, np.ndarray]:
    circuits = {
        "bell": [("h", (0,)), ("cx", (0, 1))],
        "rotated_entanglement": [
            ("h", (0,)),
            ("cx", (0, 2)),
            ("rz", (1,), np.pi / 3),
            ("ry", (2,), -0.71),
        ],
        "nonadjacent": [
            ("x", (3,)),
            ("cx", (3, 0)),
            ("swap", (1, 2)),
            ("rx", (2,), 0.37),
        ],
    }
    results: dict[str, np.ndarray] = {}
    for name, operations in circuits.items():
        qubits = {"bell": 2, "rotated_entanglement": 3, "nonadjacent": 4}[name]
        simulator = StatevectorSimulator(qubits)
        for operation in operations:
            gate_name, targets, *angle = operation
            simulator.apply(gate_name, *targets, theta=angle[0] if angle else None)
        results[name] = simulator.statevector()
    return results


def qiskit_vectors() -> dict[str, np.ndarray] | None:
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
    except ImportError:
        return None
    circuits: dict[str, QuantumCircuit] = {}
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    circuits["bell"] = bell
    rotated = QuantumCircuit(3)
    rotated.h(0)
    rotated.cx(0, 2)
    rotated.rz(np.pi / 3, 1)
    rotated.ry(-0.71, 2)
    circuits["rotated_entanglement"] = rotated
    nonadjacent = QuantumCircuit(4)
    nonadjacent.x(3)
    nonadjacent.cx(3, 0)
    nonadjacent.swap(1, 2)
    nonadjacent.rx(0.37, 2)
    circuits["nonadjacent"] = nonadjacent
    return {name: np.asarray(Statevector.from_instruction(circuit).data) for name, circuit in circuits.items()}


def compare(reference: np.ndarray, candidate: np.ndarray) -> tuple[float, float]:
    if reference.shape != candidate.shape:
        raise AssertionError(f"shape mismatch: {reference.shape} != {candidate.shape}")
    phase_overlap = np.vdot(reference, candidate)
    phase = phase_overlap / abs(phase_overlap) if abs(phase_overlap) > 0 else 1.0
    aligned = candidate / phase
    amplitude_error = float(np.max(np.abs(reference - aligned)))
    probability_error = float(np.max(np.abs(np.abs(reference) ** 2 - np.abs(candidate) ** 2)))
    return amplitude_error, probability_error


def main() -> None:
    browser = browser_vectors()
    references = {"native": native_vectors(), "qiskit": qiskit_vectors()}
    report = {"browser": "passed", "comparisons": {}}
    for backend, vectors in references.items():
        if vectors is None:
            report[backend] = "skipped: qiskit is not installed"
            continue
        report[backend] = "passed"
        report["comparisons"][backend] = {}
        for name, reference in vectors.items():
            amplitude_error, probability_error = compare(reference, browser[name])
            passed = amplitude_error <= 1e-12 and probability_error <= 1e-12
            report["comparisons"][backend][name] = {
                "passed": passed,
                "max_phase_aligned_amplitude_error": amplitude_error,
                "max_probability_error": probability_error,
            }
            if not passed:
                raise SystemExit(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()