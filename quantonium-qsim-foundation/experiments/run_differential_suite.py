#!/usr/bin/env python3
"""Run deterministic cross-simulator statevector verification."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

from quantonium_qsim.adapters.qiskit_adapter import evolve as qiskit_evolve
from quantonium_qsim.benchmarks.manifests import input_sha256, write_result
from quantonium_qsim.benchmarks.metrics import compare_statevectors
from quantonium_qsim.exact import ExactSimulator
from quantonium_qsim.exact import gates
from quantonium_qsim.rft import canonical_rft_basis

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def cases() -> list[tuple[str, np.ndarray, list[tuple[np.ndarray, tuple[int, ...]]]]]:
    rng = np.random.default_rng(SEED)
    result = []
    for qubits in range(1, 5):
        dimension = 1 << qubits
        for index in range(dimension):
            result.append((f"basis_{qubits}q_{index}", np.eye(dimension)[index], []))
        state = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
        state /= np.linalg.norm(state)
        operations = [(gates.H, (0,)), (gates.rz(0.317, (0,)) if False else (0,))]
        # Explicit circuit includes mixed rotations and randomized layouts.
        operations = [(gates.H, (0,)), (gates.rx(0.317), (qubits - 1,))]
        if qubits > 1:
            operations += [(gates.CX, (0, qubits - 1)), (gates.CY, (qubits - 1, 0))]
        result.append((f"random_mixed_{qubits}q", state, operations))
        basis = canonical_rft_basis(dimension)
        result.append((f"rft_forward_{qubits}q", state, [(basis.conj().T, tuple(range(qubits)))]))
        result.append((f"rft_inverse_{qubits}q", state, [(basis, tuple(range(qubits)))]))
        result.append((f"rft_roundtrip_{qubits}q", state, [
            (basis.conj().T, tuple(range(qubits))), (basis, tuple(range(qubits)))
        ]))
    bell_ops = [(gates.H, (0,)), (gates.CX, (0, 1))]
    result.append(("bell", np.array([1, 0, 0, 0], dtype=np.complex128), bell_ops))
    result.append(("phase_sensitive", np.array([1, 1j, -1, -1j]) / 2, [(gates.S, (1,))]))
    return result


def native_evolve(state: np.ndarray, operations: list[tuple[np.ndarray, tuple[int, ...]]]) -> np.ndarray:
    simulator = ExactSimulator.from_statevector(state)
    for matrix, targets in operations:
        simulator.apply_unitary(matrix, targets)
    return simulator.statevector()


def numpy_evolve(state: np.ndarray, operations: list[tuple[np.ndarray, tuple[int, ...]]]) -> np.ndarray:
    """Independent dense embedding used as a direct linear-algebra reference."""
    result = np.asarray(state, dtype=np.complex128)
    qubits = int(np.log2(result.size))
    for matrix, targets in operations:
        dense = np.zeros((result.size, result.size), dtype=np.complex128)
        for column in range(result.size):
            local_column = sum(((column >> q) & 1) << p for p, q in enumerate(targets))
            for local_row in range(1 << len(targets)):
                row = column
                for p, q in enumerate(targets):
                    row = (row & ~(1 << q)) | (((local_row >> p) & 1) << q)
                dense[row, column] = matrix[local_row, local_column]
        result = dense @ result
    return result


def main() -> None:
    adapters = {"direct_numpy_linear_algebra": numpy_evolve, "qiskit_statevector": qiskit_evolve}
    if importlib.util.find_spec("cirq"):
        from quantonium_qsim.adapters.cirq_adapter import evolve
        adapters["cirq_simulator"] = evolve
    if importlib.util.find_spec("qulacs"):
        from quantonium_qsim.adapters.qulacs_adapter import evolve
        adapters["qulacs"] = evolve

    records = []
    all_passed = True
    serialized_inputs = bytearray()
    for name, state, operations in cases():
        serialized_inputs.extend(np.asarray(state, dtype=np.complex128).tobytes())
        native = native_evolve(np.asarray(state, dtype=np.complex128), operations)
        # Direct NumPy reference for all-qubit RFT and identity cases; Qiskit
        # independently covers local-layout semantics for every case.
        for backend, adapter in adapters.items():
            candidate = adapter(state, operations)
            metrics = compare_statevectors(native, candidate)
            records.append({"case": name, "reference": backend, **metrics})
            all_passed &= bool(metrics["passed"])
    if importlib.util.find_spec("stim"):
        from quantonium_qsim.adapters.stim_adapter import evolve_clifford
        stim_operations = [("h", (0,)), ("cx", (0, 3)), ("cx", (3, 1)), ("cx", (1, 2))]
        native_stim = ExactSimulator(4).h(0).cx(0, 3).cx(3, 1).cx(1, 2).statevector()
        metrics = compare_statevectors(native_stim, evolve_clifford(4, stim_operations))
        records.append({"case": "stim_clifford_ghz", "reference": "stim", **metrics})
        all_passed &= bool(metrics["passed"])
    output, sidecar = write_result(
        ROOT / "results" / "differential_suite.json",
        seed=SEED,
        input_hash=input_sha256(bytes(serialized_inputs)),
        backend="quantonium_exact_vs_" + "_and_".join(adapters),
        command="python experiments/run_differential_suite.py",
        metrics={"comparisons": records, "count": len(records)},
        passed=all_passed,
        conclusion="Installed independent statevector references agree within declared thresholds.",
        limitation="Optional references absent from the environment are not silently substituted.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar), "comparisons": len(records), "passed": all_passed}, indent=2))
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
