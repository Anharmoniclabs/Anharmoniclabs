#!/usr/bin/env python3
"""Separated cold/warm timing categories for native Anharmonic Labs operations."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from anharmonic.verification.manifests import input_sha256, write_result
from anharmonic.verification.runner import benchmark
from anharmonic.statevector import StatevectorSimulator
from anharmonic.polar import canonical_polar_basis
from anharmonic.structured import ProductState, StructuredEngine
from anharmonic.structured.reconstruction import reconstruct_product_state
from anharmonic.references.qiskit_adapter import evolve as qiskit_evolve
from anharmonic.references.cirq_adapter import evolve as cirq_evolve
from anharmonic.references.qulacs_adapter import evolve as qulacs_evolve
from anharmonic.statevector import gates
from anharmonic.circuits import build_polar_circuit
from qiskit import transpile
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def main() -> None:
    rng = np.random.default_rng(SEED)
    state = rng.normal(size=16) + 1j * rng.normal(size=16)
    state /= np.linalg.norm(state)
    basis = canonical_polar_basis(16)
    structured = ProductState.phi_schedule(10)
    operations = [(gates.H, (0,)), (gates.CX, (0, 3)), (gates.rz(0.3), (1,))]
    qiskit_circuit = build_polar_circuit(16)

    def construct_polar_uncached():
        from anharmonic.polar.canonical import _basis
        _basis.cache_clear()
        return canonical_polar_basis(16)

    def qiskit_sampling():
        vector = Statevector(state)
        vector.seed(SEED)
        return vector.sample_counts(1024)

    categories = {
        "A_simulator_initialization": benchmark(lambda: StatevectorSimulator(4, state)),
        "B_circuit_construction": benchmark(lambda: [("h", 0), ("cx", 0, 3), ("rz", 0.3, 1)]),
        "C_anharmonic_compilation": {"status": "not_applicable_native_interpreter"},
        "C_qiskit_compilation": benchmark(lambda: transpile(qiskit_circuit, basis_gates=["rz", "sx", "x", "cx"], optimization_level=1)),
        "D_pure_state_evolution": benchmark(lambda: StatevectorSimulator(4, state).h(0).cx(0, 3).rz(0.3, 1)),
        "D_qiskit_state_evolution": benchmark(lambda: qiskit_evolve(state, operations)),
        "D_cirq_state_evolution": benchmark(lambda: cirq_evolve(state, operations)),
        "D_qulacs_state_evolution": benchmark(lambda: qulacs_evolve(state, operations)),
        "E_measurement_sampling": benchmark(lambda: StatevectorSimulator(4, state, seed=SEED).sample(1024)),
        "E_qiskit_measurement_sampling": benchmark(qiskit_sampling),
        "F_polar_operator_construction": benchmark(construct_polar_uncached),
        "G_polar_operator_application": benchmark(lambda: basis.conj().T @ state),
        "H_product_reconstruction": benchmark(lambda: reconstruct_product_state(structured)),
    }
    with StructuredEngine(64) as engine:
        categories["H_structured_compression"] = benchmark(
            lambda: engine.compress_structured_schedule(10_000)
        )
    output, sidecar = write_result(
        ROOT / "results" / "fair_benchmarks.json",
        seed=SEED,
        input_hash=input_sha256(state.tobytes() + structured.factors.tobytes()),
        backend="anharmonic_statevector_and_structured",
        command="python experiments/run_fair_benchmarks.py",
        metrics=categories,
        passed=True,
        conclusion="Cold-start and warm-run timing boundaries are reported separately with 30 repetitions.",
        limitation="Machine-local timings are not performance claims against absent external SDKs or QPUs.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar)}, indent=2))


if __name__ == "__main__":
    main()
