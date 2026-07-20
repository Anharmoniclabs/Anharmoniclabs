"""Reproducible JSON result manifests and SHA-256 sidecars."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quantonium_qsim.rft.provenance import SOURCE_COMMIT


def _git_commit(project: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=project, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "uncommitted"


def dependency_versions() -> dict[str, str]:
    versions = {}
    for name in ("numpy", "qiskit", "qiskit-aer", "cirq", "qulacs", "stim", "qiskit-ibm-runtime"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def input_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_result(
    path: str | Path,
    *,
    seed: int,
    input_hash: str,
    backend: str,
    command: str,
    metrics: Any,
    passed: bool,
    conclusion: str,
    limitation: str,
) -> tuple[Path, Path]:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    project = Path(__file__).resolve().parents[3]
    payload = {
        "schema_version": "quantonium-qsim-result-v1",
        "git_commit_sha": _git_commit(project),
        "source_quantoniumos_commit_sha": SOURCE_COMMIT,
        "dependency_versions": dependency_versions(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "input_hash": input_hash,
        "backend": backend,
        "exact_command": command,
        "metrics": metrics,
        "passed": bool(passed),
        "conclusion": conclusion,
        "limitation": limitation,
    }
    serialized = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    destination.write_bytes(serialized)
    digest = hashlib.sha256(serialized).hexdigest()
    sidecar = destination.with_suffix(destination.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {destination.name}\n", encoding="utf-8")
    return destination, sidecar
