#!/usr/bin/env python3
"""Parity check for the browser sparse mode against Qiskit Aer MPS."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT.parent / "tests" / "web" / "sparse_50_runner.mjs"


def main() -> None:
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise SystemExit("Install the qiskit extra to run 50-qubit backend parity") from exc

    browser = json.loads(subprocess.run(
        ["node", str(RUNNER)], cwd=ROOT.parent, check=True, capture_output=True, text=True
    ).stdout)
    circuit = QuantumCircuit(50, 50)
    circuit.x(49)
    circuit.cx(49, 0)
    circuit.x(1)
    circuit.swap(1, 48)
    circuit.cz(0, 2)
    circuit.measure(range(50), range(50))
    simulator = AerSimulator(method="matrix_product_state", shots=1024)
    result = simulator.run(transpile(circuit, simulator), seed_simulator=73021).result()
    counts = result.get_counts()
    if len(counts) != 1 or next(iter(counts.values())) != 1024:
        raise SystemExit(json.dumps({"browser": browser, "qiskit_counts": counts}, indent=2))
    qiskit_label = next(iter(counts))
    qiskit_index = int(qiskit_label, 2)
    if qiskit_index != browser["index"]:
        raise SystemExit(json.dumps({"browser": browser, "qiskit_index": qiskit_index}, indent=2))
    print(json.dumps({
        "passed": True,
        "qubits": 50,
        "browser_nonzero_amplitudes": browser["nonzeroAmplitudes"],
        "browser_index": browser["index"],
        "qiskit_index": qiskit_index,
        "shots": 1024,
        "backend": "qiskit_aer_matrix_product_state",
    }, indent=2))


if __name__ == "__main__":
    main()