from __future__ import annotations

from quantonium_qsim.analysis import circuit_metrics
from quantonium_qsim.quantum import build_qft_circuit, build_rft_circuit

from _common import write_result


def main() -> None:
    records = []
    # Generic arbitrary-unitary synthesis grows quickly. Keep the default pass
    # small and expand deliberately in later experiments.
    for size in (2, 4, 8):
        rft = build_rft_circuit(size, direction="forward")
        qft = build_qft_circuit(size, direction="forward")
        records.append({
            "size": size,
            "qubits": size.bit_length() - 1,
            "rft_generic_unitary": circuit_metrics(rft),
            "qft_structured": circuit_metrics(qft),
        })
    path = write_result(
        "03_rft_vs_qft_circuit_metrics",
        {
            "experiment": "generic_rft_decomposition_vs_structured_qft",
            "warning": "This compares a generic exact unitary synthesis with a structured QFT circuit and is not evidence of quantum advantage.",
            "records": records,
        },
    )
    print(path)
    for record in records:
        print(record)


if __name__ == "__main__":
    main()
