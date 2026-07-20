"""Fair timing primitives with warm-up and separated timing boundaries."""

from __future__ import annotations

import resource
import statistics
import time
from collections.abc import Callable
from typing import Any

import numpy as np


def benchmark(
    function: Callable[[], Any], *, repetitions: int = 30, warmups: int = 3
) -> dict[str, float | int]:
    if repetitions < 30:
        raise ValueError("fair benchmarks require at least 30 timed repetitions")
    start_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    cold_start = time.perf_counter_ns()
    function()
    cold_ms = (time.perf_counter_ns() - cold_start) / 1e6
    for _ in range(warmups):
        function()
    durations = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        function()
        durations.append((time.perf_counter_ns() - start) / 1e6)
    end_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "cold_start_ms": cold_ms,
        "warm_median_ms": float(statistics.median(durations)),
        "warm_p95_ms": float(np.percentile(durations, 95)),
        "warm_stddev_ms": float(statistics.pstdev(durations)),
        "peak_resident_memory_delta_kib": int(max(0, end_rss - start_rss)),
        "warmups": warmups,
        "repetitions": repetitions,
    }
