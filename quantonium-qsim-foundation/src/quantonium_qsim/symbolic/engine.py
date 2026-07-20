"""Safe ctypes binding for the original QuantoniumOS QSC C engine.

QSC processes a restricted phi-structured classical representation. Historical
C ABI names containing ``qubit`` are preserved for compatibility only; this
binding exposes them as logical labels and never treats QSC as a universal
statevector simulator.
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

QSC_SUCCESS = 0
RFT_VARIANT_CASCADE = 9


class QSCComplex(ctypes.Structure):
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]


class QSCParams(ctypes.Structure):
    # Exact order/types from native/qsc/quantum_symbolic_compression.h.
    _fields_ = [
        ("num_qubits", ctypes.c_size_t),
        ("compression_size", ctypes.c_size_t),
        ("phi", ctypes.c_double),
        ("normalization", ctypes.c_double),
        ("use_simd", ctypes.c_bool),
        ("use_assembly", ctypes.c_bool),
        ("variant", ctypes.c_int),
    ]


class QSCState(ctypes.Structure):
    _fields_ = [
        ("amplitudes", ctypes.POINTER(QSCComplex)),
        ("size", ctypes.c_size_t),
        ("num_qubits", ctypes.c_size_t),
        ("norm", ctypes.c_double),
        ("initialized", ctypes.c_bool),
        ("metadata", ctypes.c_void_p),
    ]


class QSCPerfStats(ctypes.Structure):
    _fields_ = [
        ("compression_time_ms", ctypes.c_double),
        ("entanglement_time_ms", ctypes.c_double),
        ("total_time_ms", ctypes.c_double),
        ("operations_per_second", ctypes.c_size_t),
        ("memory_mb", ctypes.c_double),
        ("compression_ratio", ctypes.c_double),
    ]


def _library_candidates() -> list[Path]:
    project = Path(__file__).resolve().parents[3]
    names = ("libquantonium_qsc.so", "libquantonium_qsc.dylib", "quantonium_qsc.dll")
    configured = os.environ.get("QUANTONIUM_QSC_LIBRARY")
    paths = [Path(configured)] if configured else []
    for directory in (project / "build" / "qsc", project / "native" / "qsc" / "build"):
        paths.extend(directory / name for name in names)
        paths.extend(directory / "Release" / name for name in names)
    return paths


class SymbolicEngine:
    def __init__(self, compression_size: int = 64, library: str | Path | None = None):
        if compression_size < 1:
            raise ValueError("compression_size must be positive")
        candidates = [Path(library)] if library is not None else _library_candidates()
        selected = next((path for path in candidates if path.is_file()), None)
        if selected is None:
            raise RuntimeError(
                "QSC native library not found; run "
                "cmake -S native/qsc -B build/qsc && cmake --build build/qsc"
            )
        self.library_path = selected.resolve()
        self.lib = ctypes.CDLL(str(self.library_path))
        self.compression_size = int(compression_size)
        self.state = QSCState()
        self._configure_abi()

    def _configure_abi(self) -> None:
        self.lib.qsc_init_state.argtypes = [ctypes.POINTER(QSCState), ctypes.POINTER(QSCParams)]
        self.lib.qsc_init_state.restype = ctypes.c_int
        for name in ("qsc_compress_million_qubits", "qsc_compress_optimized_asm"):
            function = getattr(self.lib, name)
            function.argtypes = [ctypes.POINTER(QSCState), ctypes.c_size_t, ctypes.c_size_t]
            function.restype = ctypes.c_int
        self.lib.qsc_cleanup_state.argtypes = [ctypes.POINTER(QSCState)]
        self.lib.qsc_cleanup_state.restype = ctypes.c_int
        self.lib.qsc_get_performance_stats.argtypes = [
            ctypes.POINTER(QSCState), ctypes.POINTER(QSCPerfStats)
        ]
        self.lib.qsc_get_performance_stats.restype = ctypes.c_int
        self.lib.qsc_validate_unitarity.argtypes = [
            ctypes.POINTER(QSCState), ctypes.c_double, ctypes.POINTER(ctypes.c_bool)
        ]
        self.lib.qsc_validate_unitarity.restype = ctypes.c_int

    def initialize(self, num_labels: int, *, use_simd: bool = True) -> None:
        if num_labels < 1:
            raise ValueError("num_labels must be positive")
        self.close()
        params = QSCParams(
            num_qubits=int(num_labels),
            compression_size=self.compression_size,
            phi=(1.0 + np.sqrt(5.0)) / 2.0,
            normalization=1.0,
            use_simd=bool(use_simd),
            use_assembly=False,
            variant=RFT_VARIANT_CASCADE,
        )
        error = self.lib.qsc_init_state(ctypes.byref(self.state), ctypes.byref(params))
        if error != QSC_SUCCESS:
            raise RuntimeError(f"qsc_init_state failed with error {error}")

    def compress_structured_schedule(self, num_labels: int) -> NDArray[np.complex128]:
        """Run the original deterministic QSC phi-schedule compressor."""
        if not self.state.initialized or self.state.num_qubits != num_labels:
            self.initialize(num_labels)
        error = self.lib.qsc_compress_million_qubits(
            ctypes.byref(self.state), int(num_labels), self.compression_size
        )
        if error != QSC_SUCCESS:
            raise RuntimeError(f"QSC compression failed with error {error}")
        return self.coefficients()

    def coefficients(self) -> NDArray[np.complex128]:
        if not self.state.initialized or not self.state.amplitudes:
            raise RuntimeError("QSC state is not initialized")
        return np.array(
            [complex(self.state.amplitudes[i].real, self.state.amplitudes[i].imag)
             for i in range(self.state.size)],
            dtype=np.complex128,
        )

    def performance(self) -> dict[str, float | int]:
        stats = QSCPerfStats()
        error = self.lib.qsc_get_performance_stats(ctypes.byref(self.state), ctypes.byref(stats))
        if error != QSC_SUCCESS:
            raise RuntimeError(f"QSC statistics unavailable (error {error})")
        return {
            "compression_time_ms": stats.compression_time_ms,
            "total_time_ms": stats.total_time_ms,
            "operations_per_second": stats.operations_per_second,
            "memory_mb": stats.memory_mb,
            "compression_ratio": stats.compression_ratio,
        }

    def normalized(self, tolerance: float = 1e-12) -> bool:
        result = ctypes.c_bool()
        error = self.lib.qsc_validate_unitarity(
            ctypes.byref(self.state), float(tolerance), ctypes.byref(result)
        )
        if error != QSC_SUCCESS:
            raise RuntimeError(f"QSC normalization check failed with error {error}")
        return bool(result.value)

    def close(self) -> None:
        if getattr(self, "lib", None) is not None and self.state.initialized:
            self.lib.qsc_cleanup_state(ctypes.byref(self.state))

    def __enter__(self) -> "SymbolicEngine":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
