"""Execute the canonical Anharmonic Labs Polar on IBM Quantum hardware.

This experiment performs two probes:

1. Forward Polar:
   |0...0> -> Polar forward -> measurement

2. Round trip:
   |0...0> -> Polar forward -> Polar inverse -> measurement

The hardware measurement distributions are compared against ideal
statevector probabilities.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2

from anharmonic.circuits.circuits import (
    build_polar_circuit,
    qubit_count,
)


def get_backend_name(backend: Any) -> str:
    """Return a backend name across Qiskit backend versions."""
    value = getattr(backend, "name", "unknown")
    return str(value() if callable(value) else value)


def build_forward_probe(size: int) -> QuantumCircuit:
    """Prepare |0...0> and apply the canonical forward Polar."""
    circuit = QuantumCircuit(qubit_count(size), name=f"polar_forward_N{size}")
    circuit.compose(
        build_polar_circuit(size, direction="forward"),
        inplace=True,
    )
    return circuit


def build_roundtrip_probe(size: int) -> QuantumCircuit:
    """Apply forward and inverse Polar to |0...0>."""
    circuit = QuantumCircuit(qubit_count(size), name=f"polar_roundtrip_N{size}")

    circuit.compose(
        build_polar_circuit(size, direction="forward"),
        inplace=True,
    )

    # Prevent the transpiler from algebraically cancelling the two
    # operators before they reach the physical processor.
    circuit.barrier()

    circuit.compose(
        build_polar_circuit(size, direction="inverse"),
        inplace=True,
    )

    return circuit


def ideal_probabilities(circuit: QuantumCircuit) -> dict[str, float]:
    """Calculate ideal probabilities before measurement."""
    state = Statevector.from_instruction(circuit)
    probabilities = state.probabilities()
    width = circuit.num_qubits

    return {
        format(index, f"0{width}b"): float(probability)
        for index, probability in enumerate(probabilities)
    }


def observed_probabilities(
    counts: dict[str, int],
    width: int,
) -> dict[str, float]:
    """Convert hardware counts into probabilities."""
    total = int(sum(counts.values()))

    if total <= 0:
        raise RuntimeError("The IBM job returned no measurement counts.")

    return {
        format(index, f"0{width}b"): (
            int(counts.get(format(index, f"0{width}b"), 0)) / total
        )
        for index in range(2**width)
    }


def compare_distributions(
    ideal: dict[str, float],
    observed: dict[str, float],
) -> dict[str, float]:
    """Calculate distribution fidelity and total variation distance."""
    labels = sorted(set(ideal) | set(observed))

    p = np.asarray(
        [ideal.get(label, 0.0) for label in labels],
        dtype=np.float64,
    )
    q = np.asarray(
        [observed.get(label, 0.0) for label in labels],
        dtype=np.float64,
    )

    total_variation_distance = 0.5 * float(np.sum(np.abs(p - q)))
    distribution_fidelity = float(np.sum(np.sqrt(p * q)) ** 2)

    return {
        "distribution_fidelity": distribution_fidelity,
        "total_variation_distance": total_variation_distance,
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--size",
        type=int,
        default=2,
        choices=(2, 4, 8),
        help="Polar matrix dimension.",
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=512,
        help="Hardware measurement shots.",
    )
    parser.add_argument(
        "--optimization",
        type=int,
        default=3,
        choices=(0, 1, 2, 3),
        help="Qiskit transpiler optimization level.",
    )
    parser.add_argument(
        "--backend",
        default=None,
        help="Optional exact IBM backend name.",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Submit to real IBM hardware.",
    )

    args = parser.parse_args()

    token = os.environ.get("IBM_QUANTUM_API_KEY")
    instance = os.environ.get("IBM_QUANTUM_CRN")

    if not token:
        raise SystemExit("IBM_QUANTUM_API_KEY is not set.")

    if not instance:
        raise SystemExit("IBM_QUANTUM_CRN is not set.")

    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance=instance,
    )

    logical_qubits = qubit_count(args.size)

    if args.backend:
        backend = service.backend(args.backend)
    else:
        backend = service.least_busy(
            operational=True,
            simulator=False,
            min_num_qubits=logical_qubits,
        )

    backend_name = get_backend_name(backend)

    print()
    print("IBM Quantum connection successful")
    print("---------------------------------")
    print(f"Backend:          {backend_name}")
    print(f"Polar dimension:    {args.size}")
    print(f"Logical qubits:   {logical_qubits}")
    print(f"Requested shots:  {args.shots}")
    print()

    logical_probes = [
        ("forward_zero", build_forward_probe(args.size)),
        ("roundtrip_zero", build_roundtrip_probe(args.size)),
    ]

    ideal_results = {
        name: ideal_probabilities(circuit)
        for name, circuit in logical_probes
    }

    measured_circuits: list[QuantumCircuit] = []

    for name, logical_circuit in logical_probes:
        measured = logical_circuit.copy(name=f"{name}_measured")
        measured.measure_all()
        measured_circuits.append(measured)

    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=args.optimization,
    )

    isa_circuits = [
        pass_manager.run(circuit)
        for circuit in measured_circuits
    ]

    print("Transpiled circuit metrics")
    print("---------------------------")

    for (name, _), circuit in zip(logical_probes, isa_circuits):
        print(f"{name}:")
        print(f"  depth:      {circuit.depth()}")
        print(f"  width:      {circuit.num_qubits}")
        print(f"  operations: {dict(circuit.count_ops())}")

    if not args.submit:
        print()
        print("DRY RUN COMPLETE")
        print("No quantum-hardware job was submitted.")
        print("Add --submit to execute these circuits.")
        return

    print()
    print("Submitting circuits to IBM Quantum hardware...")

    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=args.shots)

    job_id = job.job_id()

    print(f"Job ID: {job_id}")
    print("Waiting for the quantum processor...")

    primitive_result = job.result()

    experiment_results: list[dict[str, Any]] = []

    for index, ((name, _), isa_circuit) in enumerate(
        zip(logical_probes, isa_circuits)
    ):
        counts = primitive_result[index].data.meas.get_counts()

        counts = {
            str(bitstring): int(count)
            for bitstring, count in counts.items()
        }

        observed = observed_probabilities(
            counts,
            logical_qubits,
        )
        ideal = ideal_results[name]
        metrics = compare_distributions(ideal, observed)

        zero_state = "0" * logical_qubits
        zero_state_probability = observed.get(zero_state, 0.0)

        record = {
            "probe": name,
            "ideal_probabilities": ideal,
            "hardware_counts": counts,
            "hardware_probabilities": observed,
            "zero_state_probability": zero_state_probability,
            **metrics,
            "transpiled_depth": isa_circuit.depth(),
            "transpiled_width": isa_circuit.num_qubits,
            "transpiled_operations": {
                str(operation): int(count)
                for operation, count in isa_circuit.count_ops().items()
            },
            "layout": str(isa_circuit.layout),
        }

        experiment_results.append(record)

        print()
        print(f"Result: {name}")
        print(
            "  distribution fidelity:    "
            f"{metrics['distribution_fidelity']:.8f}"
        )
        print(
            "  total variation distance: "
            f"{metrics['total_variation_distance']:.8f}"
        )
        print(
            "  zero-state probability:   "
            f"{zero_state_probability:.8f}"
        )
        print(f"  counts:                   {counts}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    output = {
        "timestamp_utc": timestamp,
        "backend": backend_name,
        "job_id": job_id,
        "polar_dimension": args.size,
        "logical_qubits": logical_qubits,
        "shots": args.shots,
        "optimization_level": args.optimization,
        "experiment_type": "canonical_polar_ibm_hardware",
        "implementation_note": (
            "Exact finite matrix embedded as a generic Qiskit UnitaryGate."
        ),
        "results": experiment_results,
    }

    output_path = Path("results") / (
        f"04_ibm_hardware_polar_N{args.size}_{timestamp}.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print()
    print(f"Saved hardware result: {output_path}")


if __name__ == "__main__":
    main()
