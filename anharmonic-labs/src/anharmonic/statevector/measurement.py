"""Probability and seeded-shot utilities."""

from __future__ import annotations

from collections import Counter

import numpy as np
from numpy.typing import ArrayLike, NDArray


def probabilities(state: ArrayLike) -> NDArray[np.float64]:
    vector = np.asarray(state, dtype=np.complex128)
    return np.asarray(np.abs(vector) ** 2, dtype=np.float64)


def sample_counts(
    state: ArrayLike, shots: int, *, seed: int | None = None, width: int | None = None
) -> dict[str, int]:
    if isinstance(shots, bool) or int(shots) != shots or shots < 0:
        raise ValueError("shots must be a non-negative integer")
    probs = probabilities(state)
    if not np.isclose(probs.sum(), 1.0, atol=1e-12):
        raise ValueError("state probabilities must sum to one")
    width = width if width is not None else int(np.log2(probs.size))
    draws = np.random.default_rng(seed).choice(probs.size, size=int(shots), p=probs)
    return dict(sorted(Counter(format(int(value), f"0{width}b") for value in draws).items()))
