from __future__ import annotations

import numpy as np

from anharmonic.analysis import statevector_error
from anharmonic.circuits import normalize_state, simulate_polar_statevector
from anharmonic.polar import canonical_polar_operator

from _common import write_result


def main() -> None:
    seed = 20260720
    rng = np.random.default_rng(seed)
    records = []
    for size in (2, 4, 8, 16):
        state = normalize_state(rng.normal(size=size) + 1j * rng.normal(size=size))
        expected = canonical_polar_operator(size).conj().T @ state
        simulated = simulate_polar_statevector(state, direction="forward")
        records.append({"size": size, "qubits": size.bit_length() - 1, "relative_error_up_to_global_phase": statevector_error(expected, simulated)})
    path = write_result(
        "02_statevector_equivalence",
        {"experiment": "numpy_vs_qiskit_statevector", "backend": "qiskit.quantum_info.Statevector", "random_seed": seed, "records": records},
    )
    print(path)
    for record in records:
        print(record)


if __name__ == "__main__":
    main()
