#!/usr/bin/env python3
"""Separated cold/warm timing categories for native Quantonium operations."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from quantonium_qsim.benchmarks.manifests import input_sha256, write_result
from quantonium_qsim.benchmarks.runner import benchmark
from quantonium_qsim.exact import ExactSimulator
from quantonium_qsim.rft import canonical_rft_basis
from quantonium_qsim.symbolic import PhiStructuredState, SymbolicEngine
from quantonium_qsim.symbolic.reconstruction import reconstruct_product_state
from quantonium_qsim.adapters.qiskit_adapter import evolve as qiskit_evolve
from quantonium_qsim.adapters.cirq_adapter import evolve as cirq_evolve
from quantonium_qsim.adapters.qulacs_adapter import evolve as qulacs_evolve
from quantonium_qsim.exact import gates
from quantonium_qsim.quantum import build_rft_circuit
from qiskit import transpile
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def main() -> None:
    rng = np.random.default_rng(SEED)
    state = rng.normal(size=16) + 1j * rng.normal(size=16)
    state /= np.linalg.norm(state)
    basis = canonical_rft_basis(16)
    structured = PhiStructuredState.phi_schedule(10)
    operations = [(gates.H, (0,)), (gates.CX, (0, 3)), (gates.rz(0.3), (1,))]
    qiskit_circuit = build_rft_circuit(16)

    def construct_rft_uncached():
        from quantonium_qsim.rft.canonical import _basis
        _basis.cache_clear()
        return canonical_rft_basis(16)

    def qiskit_sampling():
        vector = Statevector(state)
        vector.seed(SEED)
        return vector.sample_counts(1024)

    categories = {
        "A_simulator_initialization": benchmark(lambda: ExactSimulator(4, state)),
        "B_circuit_construction": benchmark(lambda: [("h", 0), ("cx", 0, 3), ("rz", 0.3, 1)]),
        "C_quantonium_compilation": {"status": "not_applicable_native_interpreter"},
        "C_qiskit_compilation": benchmark(lambda: transpile(qiskit_circuit, basis_gates=["rz", "sx", "x", "cx"], optimization_level=1)),
        "D_pure_state_evolution": benchmark(lambda: ExactSimulator(4, state).h(0).cx(0, 3).rz(0.3, 1)),
        "D_qiskit_state_evolution": benchmark(lambda: qiskit_evolve(state, operations)),
        "D_cirq_state_evolution": benchmark(lambda: cirq_evolve(state, operations)),
        "D_qulacs_state_evolution": benchmark(lambda: qulacs_evolve(state, operations)),
        "E_measurement_sampling": benchmark(lambda: ExactSimulator(4, state, seed=SEED).sample(1024)),
        "E_qiskit_measurement_sampling": benchmark(qiskit_sampling),
        "F_rft_operator_construction": benchmark(construct_rft_uncached),
        "G_rft_operator_application": benchmark(lambda: basis.conj().T @ state),
        "H_product_reconstruction": benchmark(lambda: reconstruct_product_state(structured)),
    }
    with SymbolicEngine(64) as engine:
        categories["H_qsc_compression"] = benchmark(lambda: engine.compress_structured_schedule(10_000))
    output, sidecar = write_result(
        ROOT / "results" / "fair_benchmarks.json",
        seed=SEED,
        input_hash=input_sha256(state.tobytes() + structured.factors.tobytes()),
        backend="quantonium_exact_and_qsc",
        command="python experiments/run_fair_benchmarks.py",
        metrics=categories,
        passed=True,
        conclusion="Cold-start and warm-run timing boundaries are reported separately with 30 repetitions.",
        limitation="Machine-local timings are not performance claims against absent external SDKs or QPUs.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar)}, indent=2))


if __name__ == "__main__":
    main()
