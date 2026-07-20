"""Numerical closure and frozen-hash validation for the canonical Polar."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .canonical import (
    canonical_basis_sha256,
    canonical_polar_basis,
    raw_phase_basis,
)
from .operator import polar_forward, polar_inverse


@dataclass(frozen=True)
class ClosureResult:
    size: int
    rank: int
    left_identity_error: float
    right_identity_error: float
    norm_error: float
    roundtrip_error: float
    parseval_error: float
    basis_sha256: str
    expected_sha256: str | None
    deterministic: bool
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def load_frozen_hashes(path: str | Path) -> dict[int, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("formula_version") != "phi-grid-polar-v1":
        raise ValueError("fixture does not describe the canonical formula")
    return {int(key): value for key, value in payload["sizes"].items()}


def validate_closure(
    size: int, *, seed: int = 0, expected_hash: str | None = None
) -> ClosureResult:
    basis = canonical_polar_basis(size)
    identity = np.eye(size, dtype=np.complex128)
    rng = np.random.default_rng(seed)
    state = rng.normal(size=size) + 1j * rng.normal(size=size)
    state /= np.linalg.norm(state)
    transformed = polar_forward(state)
    reconstructed = polar_inverse(transformed)
    left = float(np.linalg.norm(basis.conj().T @ basis - identity, ord="fro"))
    right = float(np.linalg.norm(basis @ basis.conj().T - identity, ord="fro"))
    norm_error = abs(float(np.linalg.norm(transformed)) - 1.0)
    roundtrip = float(np.linalg.norm(reconstructed - state))
    parseval = abs(float(np.vdot(state, state).real - np.vdot(transformed, transformed).real))
    digest = canonical_basis_sha256(size)
    deterministic = bool(np.array_equal(basis, canonical_polar_basis(size)))
    passed = (
        np.linalg.matrix_rank(raw_phase_basis(size)) == size
        and max(left, right) <= 1e-11
        and norm_error <= 1e-12
        and roundtrip <= 1e-11
        and parseval <= 1e-12
        and deterministic
        and (expected_hash is None or digest == expected_hash)
    )
    return ClosureResult(
        size=size,
        rank=int(np.linalg.matrix_rank(raw_phase_basis(size))),
        left_identity_error=left,
        right_identity_error=right,
        norm_error=norm_error,
        roundtrip_error=roundtrip,
        parseval_error=parseval,
        basis_sha256=digest,
        expected_sha256=expected_hash,
        deterministic=deterministic,
        passed=passed,
    )


def unitarity_error(operator: np.ndarray) -> float:
    matrix = np.asarray(operator, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    return float(np.linalg.norm(matrix.conj().T @ matrix - np.eye(matrix.shape[0]), ord="fro"))


def roundtrip_error(state: np.ndarray, operator: np.ndarray | None = None) -> float:
    vector = np.asarray(state, dtype=np.complex128)
    transform = canonical_polar_basis(vector.size) if operator is None else operator
    reconstructed = polar_inverse(polar_forward(vector, operator=transform), operator=transform)
    return float(np.linalg.norm(reconstructed - vector) / max(np.linalg.norm(vector), 1e-300))


def norm_preservation_error(state: np.ndarray, operator: np.ndarray | None = None) -> float:
    vector = np.asarray(state, dtype=np.complex128)
    transform = canonical_polar_basis(vector.size) if operator is None else operator
    return float(abs(np.linalg.norm(polar_forward(vector, operator=transform)) - np.linalg.norm(vector)))
