from __future__ import annotations

from anharmonic.analysis import circuit_metrics
from anharmonic.circuits import build_qft_circuit, build_polar_circuit

from _common import write_result


def main() -> None:
    records = []
    # Generic arbitrary-unitary synthesis grows quickly. Keep the default pass
    # small and expand deliberately in later experiments.
    for size in (2, 4, 8):
        polar = build_polar_circuit(size, direction="forward")
        qft = build_qft_circuit(size, direction="forward")
        records.append({
            "size": size,
            "qubits": size.bit_length() - 1,
            "polar_generic_unitary": circuit_metrics(polar),
            "qft_structured": circuit_metrics(qft),
        })
    path = write_result(
        "03_polar_vs_qft_circuit_metrics",
        {
            "experiment": "generic_polar_decomposition_vs_structured_qft",
            "warning": "This compares a generic exact unitary synthesis with a structured QFT circuit and is not evidence of quantum advantage.",
            "records": records,
        },
    )
    print(path)
    for record in records:
        print(record)


if __name__ == "__main__":
    main()
