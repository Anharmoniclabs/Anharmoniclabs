#!/usr/bin/env python3
"""Validate only states inside the Anharmonic Labs product-state family."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from anharmonic.verification.manifests import input_sha256, write_result
from anharmonic.structured import ProductState, StructuredEngine
from anharmonic.structured.validation import validate_product_reconstruction
from anharmonic.structured.reconstruction import reconstruct_product_state
from anharmonic.verification.metrics import compare_statevectors
from anharmonic.statevector import gates

ROOT = Path(__file__).resolve().parents[1]
SEED = 73021


def main() -> None:
    small = []
    material = bytearray()
    for labels in range(1, 11):
        state = ProductState.phi_schedule(labels)
        material.extend(state.factors.tobytes())
        row = {"logical_labels": labels, **validate_product_reconstruction(state)}
        if labels <= 4:
            exact = reconstruct_product_state(state)
            operations = [(gates.I, (q,)) for q in range(labels)]
            from anharmonic.references.qiskit_adapter import evolve as qiskit_evolve
            from anharmonic.references.cirq_adapter import evolve as cirq_evolve
            row["qiskit_reference"] = compare_statevectors(exact, qiskit_evolve(exact, operations))
            row["cirq_reference"] = compare_statevectors(exact, cirq_evolve(exact, operations))
        small.append(row)
    large = []
    with StructuredEngine(64) as engine:
        for labels in (1_000, 10_000, 100_000):
            first = engine.compress_structured_schedule(labels)
            second = engine.compress_structured_schedule(labels)
            large.append({
                "logical_labels": labels,
                "normalized": bool(np.isclose(np.linalg.norm(first), 1.0)),
                "deterministic": bool(np.array_equal(first, second)),
                "coefficient_max_abs": float(np.max(np.abs(first))),
                "coefficient_min_abs": float(np.min(np.abs(first))),
                **engine.performance(),
            })
    passed = all(row["passed"] for row in small) and all(
        row["normalized"] and row["deterministic"] for row in large
    )
    output, sidecar = write_result(
        ROOT / "results" / "structured_suite.json",
        seed=SEED,
        input_hash=input_sha256(bytes(material)),
        backend="anharmonic_structured_restricted_phi_structured",
        command="python experiments/run_structured_suite.py",
        metrics={"small_reconstruction": small, "large_structured": large},
        passed=passed,
        conclusion="Restricted product states reconstruct exactly; native structured schedules are deterministic and normalized.",
        limitation="These results do not establish simulation of arbitrary entangled circuits or physical qubits.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar), "passed": passed}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
