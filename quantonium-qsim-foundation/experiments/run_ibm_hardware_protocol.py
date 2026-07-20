#!/usr/bin/env python3
"""Manual full N=2/N=4 RFT/QFT distribution and tomography protocol.

No job is submitted unless ``--submit`` is present. Credentials come only from
the environment via ``quantonium_qsim.adapters.ibm_runtime.runtime_service``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity
from qiskit.transpiler import generate_preset_pass_manager

from quantonium_qsim.adapters.ibm_runtime import (
    reconstruct_pauli_tomography,
    runtime_service,
    submit_sampler_v2,
    tomography_measurement_circuits,
)
from quantonium_qsim.benchmarks.manifests import input_sha256, write_result
from quantonium_qsim.benchmarks.metrics import compare_distributions
from quantonium_qsim.quantum import build_qft_circuit, build_rft_circuit

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def preparations(size: int) -> dict[str, QuantumCircuit]:
    qubits = size.bit_length() - 1
    result = {}
    for index in range(size):
        circuit = QuantumCircuit(qubits, name=f"basis_{index}")
        for q in range(qubits):
            if (index >> q) & 1:
                circuit.x(q)
        result[f"basis_{index}"] = circuit
    plus = QuantumCircuit(qubits, name="plus")
    plus.h(range(qubits))
    result["plus"] = plus
    phase = plus.copy(name="phase_sensitive")
    phase.s(0)
    result["phase_sensitive"] = phase
    if qubits == 2:
        bell = QuantumCircuit(2, name="bell")
        bell.h(0)
        bell.cx(0, 1)
        result["bell"] = bell
    return result


def probes(size: int) -> dict[str, QuantumCircuit]:
    qubits = size.bit_length() - 1
    transforms = {}
    forward = build_rft_circuit(size, direction="forward")
    inverse = build_rft_circuit(size, direction="inverse")
    transforms["rft_forward"] = forward
    transforms["rft_inverse"] = inverse
    roundtrip = QuantumCircuit(qubits, name="rft_barrier_roundtrip")
    roundtrip.compose(forward, inplace=True)
    roundtrip.barrier()
    roundtrip.compose(inverse, inplace=True)
    transforms["rft_barrier_roundtrip"] = roundtrip
    transforms["qft_control"] = build_qft_circuit(size, direction="forward")
    result = {}
    for prep_name, prep in preparations(size).items():
        for transform_name, transform in transforms.items():
            circuit = prep.copy(name=f"{prep_name}__{transform_name}")
            circuit.barrier()
            circuit.compose(transform, inplace=True)
            result[circuit.name] = circuit
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, choices=(2, 4), required=True)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--backend")
    parser.add_argument("--optimization", type=int, default=3, choices=range(4))
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()
    logical = probes(args.size)
    tomography = {
        (probe, setting): circuit
        for probe, base in logical.items()
        for setting, circuit in tomography_measurement_circuits(base).items()
    }
    print(json.dumps({
        "size": args.size,
        "logical_probes": len(logical),
        "tomography_circuits": len(tomography),
        "submit": args.submit,
    }, indent=2))
    if not args.submit:
        print("Dry run only. Add --submit after local/noisy validation passes.")
        return

    service = runtime_service()
    qubits = args.size.bit_length() - 1
    backend = service.backend(args.backend) if args.backend else service.least_busy(
        operational=True, simulator=False, min_num_qubits=qubits
    )
    manager = generate_preset_pass_manager(backend=backend, optimization_level=args.optimization)
    keys = list(tomography)
    isa = [manager.run(tomography[key]) for key in keys]

    # Backend-specific noisy simulation is a hard pre-submission gate. Any
    # failure here aborts before SamplerV2 is created, so a real job is never
    # used as the first validation target.
    from qiskit_aer import AerSimulator
    noisy_result = AerSimulator.from_backend(
        backend, method="matrix_product_state"
    ).run(isa, shots=args.shots, seed_simulator=SEED).result()
    if not noisy_result.success:
        raise RuntimeError(f"backend-noise simulation failed: {noisy_result.status}")
    noisy_grouped: dict[str, dict[str, dict[str, int]]] = {}
    for index, (probe, setting) in enumerate(keys):
        noisy_counts = {
            str(k): int(v) for k, v in noisy_result.get_counts(index).items()
        }
        noisy_grouped.setdefault(probe, {})[setting] = noisy_counts

    job = submit_sampler_v2(isa, backend, shots=args.shots, confirm=True)
    primitive = job.result()
    grouped: dict[str, dict[str, dict[str, int]]] = {}
    circuit_metadata: dict[str, dict[str, object]] = {}
    for index, ((probe, setting), circuit) in enumerate(zip(keys, isa)):
        counts = {str(k): int(v) for k, v in primitive[index].data.meas.get_counts().items()}
        grouped.setdefault(probe, {})[setting] = counts
        if probe not in circuit_metadata:
            operations = {str(k): int(v) for k, v in circuit.count_ops().items()}
            circuit_metadata[probe] = {
                "transpiled_depth": circuit.depth(),
                "one_qubit_gate_count": sum(v for k, v in operations.items() if k not in {"measure", "barrier", "cx", "cz", "ecr"}),
                "two_qubit_gate_count": sum(v for k, v in operations.items() if k in {"cx", "cz", "ecr"}),
                "operations": operations,
                "physical_layout": str(circuit.layout),
            }
    records = []
    for name, circuit in logical.items():
        ideal = Statevector.from_instruction(circuit)
        ideal_probabilities = ideal.probabilities()
        z_counts = grouped[name]["Z" * qubits]
        observed = np.array([z_counts.get(format(i, f"0{qubits}b"), 0) / args.shots for i in range(args.size)])
        noisy_z_counts = noisy_grouped[name]["Z" * qubits]
        noisy_observed = np.array([
            noisy_z_counts.get(format(i, f"0{qubits}b"), 0) / args.shots
            for i in range(args.size)
        ])
        rho = reconstruct_pauli_tomography(grouped[name], qubits)
        noisy_rho = reconstruct_pauli_tomography(noisy_grouped[name], qubits)
        records.append({
            "probe": name,
            "ideal_probabilities": ideal_probabilities.tolist(),
            "hardware_counts": z_counts,
            **compare_distributions(ideal_probabilities, observed),
            "noisy_aer_counts": noisy_z_counts,
            "noisy_aer_distribution_metrics": compare_distributions(
                ideal_probabilities, noisy_observed
            ),
            "noisy_aer_tomography_state_fidelity": float(
                state_fidelity(ideal, noisy_rho, validate=False)
            ),
            "tomography_density_matrix_real": rho.real.tolist(),
            "tomography_density_matrix_imag": rho.imag.tolist(),
            "tomography_state_fidelity": float(state_fidelity(ideal, rho, validate=False)),
            **circuit_metadata[name],
        })
    backend_name = str(backend.name() if callable(backend.name) else backend.name)
    properties = backend.properties() if hasattr(backend, "properties") else None
    calibration = str(getattr(properties, "last_update_date", None)) if properties else None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output, sidecar = write_result(
        ROOT / "results" / f"ibm_full_protocol_N{args.size}_{timestamp}.json",
        seed=SEED,
        input_hash=input_sha256(json.dumps(sorted(logical)).encode()),
        backend=backend_name,
        command=f"python experiments/run_ibm_hardware_protocol.py --size {args.size} --shots {args.shots} --submit",
        metrics={
            "job_id": job.job_id(), "logical_qubits": qubits, "shots": args.shots,
            "calibration_data_available": properties is not None,
            "calibration_timestamp_available": calibration,
            "noisy_simulation_backend": "AerSimulator.from_backend(matrix_product_state)",
            "experiments": records,
        },
        passed=True,
        conclusion="Distribution and X/Y/Z tomography evidence recorded from the selected IBM QPU.",
        limitation="Finite-shot tomography uses linear inversion and may produce a non-positive estimate; counts alone do not establish phase.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar), "job_id": job.job_id()}, indent=2))


if __name__ == "__main__":
    main()
