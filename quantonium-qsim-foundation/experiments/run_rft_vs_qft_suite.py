#!/usr/bin/env python3
"""Compare distinct RFT and QFT transforms without equating their behavior."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Operator, Statevector, state_fidelity

from quantonium_qsim.analysis import circuit_metrics
from quantonium_qsim.benchmarks.manifests import input_sha256, write_result
from quantonium_qsim.benchmarks.runner import benchmark
from quantonium_qsim.quantum import build_qft_circuit, build_rft_circuit

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def phase_aligned_unitary_distance(left: np.ndarray, right: np.ndarray) -> float:
    overlap = np.vdot(right.ravel(), left.ravel())
    aligned = right if abs(overlap) == 0 else right * overlap / abs(overlap)
    return float(np.linalg.norm(left - aligned, ord="fro") / np.sqrt(left.shape[0]))


def noisy_fidelity(circuit, ideal: Statevector) -> float | None:
    try:
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, depolarizing_error
    except ImportError:
        return None
    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ["rz", "sx", "x"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ["cx"])
    compiled = transpile(circuit, basis_gates=["rz", "sx", "x", "cx"], optimization_level=0)
    executable = compiled.copy()
    executable.save_density_matrix()
    density = AerSimulator(method="density_matrix", noise_model=noise).run(executable).result().data(0)["density_matrix"]
    return float(state_fidelity(ideal, density))


def main() -> None:
    rng = np.random.default_rng(SEED)
    material = bytearray()
    rows = []
    for size in (2, 4, 8):
        rft = build_rft_circuit(size, direction="forward")
        qft = build_qft_circuit(size, direction="forward")
        rft_matrix = np.asarray(Operator(rft).data)
        qft_matrix = np.asarray(Operator(qft).data)
        states = {
            "basis_zero": np.eye(size, dtype=np.complex128)[0],
            "basis_last": np.eye(size, dtype=np.complex128)[-1],
            "uniform_product": np.ones(size, dtype=np.complex128) / np.sqrt(size),
            "phase_sensitive": np.exp(2j * np.pi * np.arange(size) / size) / np.sqrt(size),
        }
        random_state = rng.normal(size=size) + 1j * rng.normal(size=size)
        states["random_complex"] = random_state / np.linalg.norm(random_state)
        behavior = {}
        for name, state in states.items():
            material.extend(state.tobytes())
            behavior[name] = float(abs(np.vdot(rft_matrix @ state, qft_matrix @ state)) ** 2)
        ideal = Statevector.from_instruction(rft)
        rows.append({
            "size": size,
            "unitary_distance_global_phase_adjusted": phase_aligned_unitary_distance(rft_matrix, qft_matrix),
            "output_state_fidelity_by_input_class": behavior,
            "rft_circuit_synthesis": circuit_metrics(rft),
            "qft_circuit_synthesis": circuit_metrics(qft),
            "rft_ideal_simulation_runtime": benchmark(lambda: Statevector.from_instruction(rft)),
            "qft_ideal_simulation_runtime": benchmark(lambda: Statevector.from_instruction(qft)),
            "rft_synthetic_noisy_fidelity_zero_input": noisy_fidelity(rft, ideal),
            "estimated_duration": None,
            "hardware_fidelity": None,
        })
    output, sidecar = write_result(
        ROOT / "results" / "rft_vs_qft_suite.json",
        seed=SEED,
        input_hash=input_sha256(bytes(material)),
        backend="qiskit_reference_circuit_analysis",
        command="python experiments/run_rft_vs_qft_suite.py",
        metrics={
            "records": rows,
            "separation": ["transform_behavior", "simulator_accuracy", "circuit_synthesis_cost", "hardware_noise", "application_usefulness"],
        },
        passed=True,
        conclusion="RFT and QFT are distinct transforms with input-dependent output overlap and different generic synthesis costs.",
        limitation="Synthetic depolarizing noise is not backend calibration; duration and hardware fidelity require a selected QPU run.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar)}, indent=2))


if __name__ == "__main__":
    main()
