from __future__ import annotations

from pathlib import Path

import pytest

from quantonium_qsim.rft.validation import load_frozen_hashes, validate_closure

FIXTURE = Path(__file__).parents[1] / "fixtures" / "canonical_basis_hashes_v1.json"


@pytest.mark.parametrize("size", [2, 4, 8, 16, 32])
def test_mathematical_closure_and_frozen_hash(size: int) -> None:
    hashes = load_frozen_hashes(FIXTURE)
    result = validate_closure(size, seed=73021, expected_hash=hashes[size])
    assert result.rank == size
    assert result.passed, result


def test_all_available_frozen_hashes() -> None:
    hashes = load_frozen_hashes(FIXTURE)
    for size, digest in hashes.items():
        assert validate_closure(size, expected_hash=digest).basis_sha256 == digest
