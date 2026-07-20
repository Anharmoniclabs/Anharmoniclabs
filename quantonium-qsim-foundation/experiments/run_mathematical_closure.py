#!/usr/bin/env python3
"""Generate the canonical mathematical closure and frozen-hash record."""

from __future__ import annotations

import json
from pathlib import Path

from quantonium_qsim.benchmarks.manifests import input_sha256, write_result
from quantonium_qsim.rft.validation import load_frozen_hashes, validate_closure

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "canonical_basis_hashes_v1.json"
SEED = 73021


def main() -> None:
    hashes = load_frozen_hashes(FIXTURE)
    records = [validate_closure(size, seed=SEED, expected_hash=digest).as_dict()
               for size, digest in sorted(hashes.items())]
    passed = all(record["passed"] for record in records)
    output, sidecar = write_result(
        ROOT / "results" / "mathematical_closure.json",
        seed=SEED,
        input_hash=input_sha256(FIXTURE.read_bytes()),
        backend="quantonium_canonical_rft_numpy_eigh",
        command="python experiments/run_mathematical_closure.py",
        metrics={"sizes": records},
        passed=passed,
        conclusion="The canonical definition closes numerically and matches every frozen upstream basis hash.",
        limitation="Finite numerical closure is not a proof of efficient circuit synthesis or application advantage.",
    )
    print(json.dumps({"result": str(output), "sha256": str(sidecar), "sizes": len(records), "passed": passed}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
