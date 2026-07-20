from __future__ import annotations

from anharmonic.polar import canonical_polar_operator, unitarity_error

from _common import write_result


def main() -> None:
    records = []
    for size in (2, 4, 8, 16):
        operator = canonical_polar_operator(size)
        records.append({"size": size, "qubits": size.bit_length() - 1, "unitarity_error_fro": unitarity_error(operator)})
    path = write_result("01_polar_unitarity", {"experiment": "canonical_polar_unitarity", "records": records})
    print(path)
    for record in records:
        print(record)


if __name__ == "__main__":
    main()
