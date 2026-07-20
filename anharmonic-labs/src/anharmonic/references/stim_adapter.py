"""Stim reference adapter for Clifford circuits from |0...0> only."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray


def evolve_clifford(num_qubits: int, operations: Iterable[tuple[str, tuple[int, ...]]]) -> NDArray[np.complex128]:
    try:
        import stim
    except ImportError as exc:  # pragma: no cover
        raise ImportError("install the stim extra") from exc
    tableau = stim.TableauSimulator()
    tableau.set_num_qubits(num_qubits)
    supported = {"h", "x", "y", "z", "s", "sdg", "cx", "cy", "cz", "swap"}
    for name, targets in operations:
        key = name.lower()
        if key not in supported:
            raise ValueError(f"Stim adapter does not support non-Clifford gate {name!r}")
        method = getattr(tableau, "s_dag" if key == "sdg" else key)
        method(*targets)
    # Stim exports complex64 amplitudes. Promote and renormalize the exact
    # stabilizer vector so float32's rounded common magnitude does not masquerade
    # as an evolution error in double-precision comparisons.
    vector = np.asarray(tableau.state_vector(endian="little"), dtype=np.complex128)
    norm = np.linalg.norm(vector)
    return vector / norm
