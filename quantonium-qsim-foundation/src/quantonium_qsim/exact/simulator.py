"""Independent exact complex statevector simulator.

Endianness is little-endian: qubit 0 is the least significant state-index bit.
For a multi-qubit unitary, ``targets[0]`` is its least significant local bit.
No external quantum SDK is imported by this module or the native execution path.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from quantonium_qsim.rft.canonical import canonical_rft_basis
from . import gates
from .measurement import probabilities as state_probabilities, sample_counts
from .observables import expectation_value, partial_trace, purity, reduced_density_matrix


class ExactSimulator:
    """Mutable double-precision statevector simulator."""

    endianness = "little: q0 is the least-significant statevector index bit"

    def __init__(
        self, num_qubits: int, initial_state: ArrayLike | None = None, *, seed: int | None = None
    ) -> None:
        if isinstance(num_qubits, bool) or not isinstance(num_qubits, (int, np.integer)):
            raise TypeError("num_qubits must be a positive integer")
        if num_qubits < 1:
            raise ValueError("num_qubits must be positive")
        self.num_qubits = int(num_qubits)
        self.seed = seed
        dimension = 1 << self.num_qubits
        if initial_state is None:
            self._state = np.zeros(dimension, dtype=np.complex128)
            self._state[0] = 1.0
        else:
            vector = np.asarray(initial_state, dtype=np.complex128)
            if vector.shape != (dimension,):
                raise ValueError(f"initial state must have shape ({dimension},)")
            norm = float(np.linalg.norm(vector))
            if not np.isfinite(norm) or norm == 0.0:
                raise ValueError("initial state must have a finite, non-zero norm")
            if not np.isclose(norm, 1.0, atol=1e-12):
                raise ValueError("initial state must be normalized")
            self._state = vector.copy()

    @classmethod
    def from_statevector(cls, state: ArrayLike, *, seed: int | None = None) -> "ExactSimulator":
        vector = np.asarray(state, dtype=np.complex128)
        if vector.ndim != 1 or vector.size < 2 or vector.size & (vector.size - 1):
            raise ValueError("state length must be a power of two of at least two")
        return cls(int(math.log2(vector.size)), vector, seed=seed)

    def statevector(self, *, copy: bool = True) -> NDArray[np.complex128]:
        return self._state.copy() if copy else self._state.view()

    def reset(self, state: ArrayLike | None = None) -> "ExactSimulator":
        replacement = ExactSimulator(self.num_qubits, state, seed=self.seed)
        self._state = replacement._state
        return self

    def apply_unitary(self, matrix: ArrayLike, targets: Sequence[int]) -> "ExactSimulator":
        target_tuple = tuple(int(q) for q in targets)
        if not target_tuple:
            raise ValueError("targets must not be empty")
        if len(set(target_tuple)) != len(target_tuple):
            raise ValueError("targets must be unique")
        if any(q < 0 or q >= self.num_qubits for q in target_tuple):
            raise ValueError("target qubit out of range")
        dimension = 1 << len(target_tuple)
        unitary = np.asarray(matrix, dtype=np.complex128)
        if unitary.shape != (dimension, dimension):
            raise ValueError(f"unitary must have shape ({dimension}, {dimension})")
        identity = np.eye(dimension, dtype=np.complex128)
        if not np.allclose(unitary.conj().T @ unitary, identity, atol=1e-12, rtol=0.0):
            raise ValueError("matrix is not unitary within tolerance")

        tensor = self._state.reshape((2,) * self.num_qubits)
        # C-order flattening makes the last axis the local LSB, hence reversed.
        axes = [self.num_qubits - 1 - q for q in reversed(target_tuple)]
        untouched = [axis for axis in range(self.num_qubits) if axis not in axes]
        permutation = untouched + axes
        inverse_permutation = np.argsort(permutation)
        blocks = np.transpose(tensor, permutation).reshape(-1, dimension)
        evolved = blocks @ unitary.T
        self._state = np.transpose(
            evolved.reshape((2,) * self.num_qubits), inverse_permutation
        ).reshape(-1)
        return self

    def apply(self, name: str, *qubits: int, theta: float | None = None) -> "ExactSimulator":
        key = name.lower()
        if key in {"rx", "ry", "rz", "phase"}:
            if theta is None or len(qubits) != 1:
                raise ValueError(f"{key} requires one qubit and theta")
            return self.apply_unitary(getattr(gates, key)(theta), qubits)
        if theta is not None or key not in gates.NAMED_GATES:
            raise ValueError(f"unknown gate {name!r}")
        expected = 2 if key in {"cx", "cy", "cz", "swap"} else 1
        if len(qubits) != expected:
            raise ValueError(f"{key} requires {expected} qubit(s)")
        return self.apply_unitary(gates.NAMED_GATES[key], qubits)

    def x(self, q: int): return self.apply("x", q)
    def y(self, q: int): return self.apply("y", q)
    def z(self, q: int): return self.apply("z", q)
    def h(self, q: int): return self.apply("h", q)
    def s(self, q: int): return self.apply("s", q)
    def sdg(self, q: int): return self.apply("sdg", q)
    def t(self, q: int): return self.apply("t", q)
    def tdg(self, q: int): return self.apply("tdg", q)
    def rx(self, theta: float, q: int): return self.apply("rx", q, theta=theta)
    def ry(self, theta: float, q: int): return self.apply("ry", q, theta=theta)
    def rz(self, theta: float, q: int): return self.apply("rz", q, theta=theta)
    def phase(self, theta: float, q: int): return self.apply("phase", q, theta=theta)
    def cx(self, control: int, target: int): return self.apply("cx", control, target)
    def cy(self, control: int, target: int): return self.apply("cy", control, target)
    def cz(self, control: int, target: int): return self.apply("cz", control, target)
    def swap(self, left: int, right: int): return self.apply("swap", left, right)

    def rft_forward(self) -> "ExactSimulator":
        basis = canonical_rft_basis(self._state.size)
        return self.apply_unitary(basis.conj().T, tuple(range(self.num_qubits)))

    def rft_inverse(self) -> "ExactSimulator":
        basis = canonical_rft_basis(self._state.size)
        return self.apply_unitary(basis, tuple(range(self.num_qubits)))

    def probabilities(self) -> NDArray[np.float64]:
        return state_probabilities(self._state)

    def sample(self, shots: int, *, seed: int | None = None) -> dict[str, int]:
        return sample_counts(
            self._state, shots, seed=self.seed if seed is None else seed, width=self.num_qubits
        )

    def expectation(self, observable: ArrayLike | str) -> complex:
        return expectation_value(self._state, observable)

    def reduced_density_matrix(self, keep_qubits: Sequence[int]) -> NDArray[np.complex128]:
        return reduced_density_matrix(self._state, list(keep_qubits), self.num_qubits)

    def partial_trace(self, trace_qubits: Sequence[int]) -> NDArray[np.complex128]:
        return partial_trace(self._state, list(trace_qubits), self.num_qubits)

    def purity(self, keep_qubits: Sequence[int] | None = None) -> float:
        value = self._state if keep_qubits is None else self.reduced_density_matrix(keep_qubits)
        return purity(value)
