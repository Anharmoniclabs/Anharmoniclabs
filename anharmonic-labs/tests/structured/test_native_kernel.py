from __future__ import annotations

import numpy as np
import pytest

from anharmonic.structured.engine import StructuredEngine


def test_native_structured_schedule_is_normalized_and_deterministic() -> None:
    try:
        engine = StructuredEngine(compression_size=64)
    except RuntimeError as exc:
        pytest.skip(str(exc))
    with engine:
        first = engine.compress_structured_schedule(128)
        second = engine.compress_structured_schedule(128)
        assert np.allclose(first, second, atol=0.0, rtol=0.0)
        assert np.isclose(np.linalg.norm(first), 1.0)
        assert engine.normalized()
        stats = engine.performance()
        assert stats["memory_mb"] > 0
