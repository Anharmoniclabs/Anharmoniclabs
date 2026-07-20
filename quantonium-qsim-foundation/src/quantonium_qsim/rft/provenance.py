"""Pinned source provenance for the canonical RFT and QSC import."""

SOURCE_REPOSITORY = "https://github.com/LMMinier/quantoniumos"
SOURCE_COMMIT = "5bfe066e3b2e3fea722987d21252c69d5b63e2df"
CANONICAL_PATHS = (
    "docs/CANONICAL_PATHS.md",
    "algorithms/rft/core/resonant_fourier_transform.py",
    "algorithms/rft/core/canonical_api.py",
    "tests/fixtures/rft/canonical_basis_hashes_v1.json",
)
QSC_PATHS = (
    "algorithms/rft/kernels/kernel/quantum_symbolic_compression.c",
    "algorithms/rft/kernels/kernel/quantum_symbolic_compression.h",
    "algorithms/rft/kernels/python_bindings/quantum_symbolic_engine.py",
)
