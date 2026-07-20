"""Representations for the restricted Anharmonic Labs product-state family."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class ProductState:
    """Separable product state encoded by one normalized factor per label.

    ``factors[q] == (alpha_q, beta_q)``. Logical labels describe independent
    factors, not physical-qubit claims. This class cannot represent entanglement.
    """

    factors: NDArray[np.complex128]

    def __post_init__(self) -> None:
        values = np.asarray(self.factors, dtype=np.complex128)
        if values.ndim != 2 or values.shape[1] != 2 or values.shape[0] == 0:
            raise ValueError("factors must have shape (labels, 2)")
        norms = np.linalg.norm(values, axis=1)
        if not np.allclose(norms, 1.0, atol=1e-12, rtol=0.0):
            raise ValueError("each product factor must be normalized")
        frozen = values.copy()
        frozen.setflags(write=False)
        object.__setattr__(self, "factors", frozen)

    @property
    def num_labels(self) -> int:
        return int(self.factors.shape[0])

    @classmethod
    def from_angles(cls, theta: ArrayLike, phase: ArrayLike) -> "ProductState":
        theta_values = np.asarray(theta, dtype=np.float64)
        phase_values = np.asarray(phase, dtype=np.float64)
        if theta_values.ndim != 1 or theta_values.shape != phase_values.shape:
            raise ValueError("theta and phase must be equal-length vectors")
        factors = np.column_stack(
            [np.cos(theta_values / 2.0), np.exp(1j * phase_values) * np.sin(theta_values / 2.0)]
        )
        return cls(np.asarray(factors, dtype=np.complex128))

    @classmethod
    def phi_schedule(cls, num_labels: int) -> "ProductState":
        if num_labels < 1:
            raise ValueError("num_labels must be positive")
        phi = (1.0 + np.sqrt(5.0)) / 2.0
        index = np.arange(1, num_labels + 1, dtype=np.float64)
        theta = np.pi * np.mod(index * phi, 1.0)
        phase = 2.0 * np.pi * np.mod(index / phi, 1.0)
        return cls.from_angles(theta, phase)

    def compressed_coefficients(self) -> NDArray[np.complex128]:
        return self.factors.reshape(-1).copy()

    @property
    def compression_ratio(self) -> float:
        return float((1 << self.num_labels) / self.factors.size)
