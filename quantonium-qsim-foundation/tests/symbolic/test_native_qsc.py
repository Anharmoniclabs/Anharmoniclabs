from __future__ import annotations

import numpy as np
import pytest

from quantonium_qsim.symbolic.engine import SymbolicEngine


def test_original_qsc_native_schedule_is_normalized_and_deterministic() -> None:
    try:
        engine = SymbolicEngine(compression_size=64)
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
