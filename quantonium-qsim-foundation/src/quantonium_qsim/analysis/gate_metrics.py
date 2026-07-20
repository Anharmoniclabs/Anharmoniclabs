"""Circuit resource summaries for exact generic decompositions."""

from __future__ import annotations

from typing import Any


def _operation_widths(circuit) -> tuple[int, int]:
    one_qubit = 0
    two_qubit = 0
    for instruction in circuit.data:
        width = int(instruction.operation.num_qubits)
        if width == 1:
            one_qubit += 1
        elif width == 2:
            two_qubit += 1
    return one_qubit, two_qubit


def circuit_metrics(circuit, *, transpile_circuit: bool = True) -> dict[str, Any]:
    """Return native and optional generic-basis resource metrics."""
    native_one, native_two = _operation_widths(circuit)
    result: dict[str, Any] = {
        "qubits": int(circuit.num_qubits),
        "depth": int(circuit.depth()),
        "total_operations": int(circuit.size()),
        "one_qubit_operations": native_one,
        "two_qubit_operations": native_two,
        "operation_counts": {str(k): int(v) for k, v in circuit.count_ops().items()},
    }
    if not transpile_circuit:
        return result

    try:
        from qiskit import transpile
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("Install the 'quantum' extra to transpile circuits") from exc

    compiled = transpile(
        circuit,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=1,
    )
    compiled_one, compiled_two = _operation_widths(compiled)
    result["transpiled"] = {
        "basis_gates": ["rz", "sx", "x", "cx"],
        "depth": int(compiled.depth()),
        "total_operations": int(compiled.size()),
        "one_qubit_operations": compiled_one,
        "two_qubit_operations": compiled_two,
        "operation_counts": {str(k): int(v) for k, v in compiled.count_ops().items()},
    }
    return result
