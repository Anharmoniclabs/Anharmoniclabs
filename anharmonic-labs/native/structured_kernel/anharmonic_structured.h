/**
 * Anharmonic Labs Structured-State Kernel - Header
 *
 * Classical fixed-buffer representation for a restricted family of separable,
 * product-form, phase-structured descriptions. This is not a universal quantum
 * circuit simulator and does not represent a general 2^n statevector.
 */

/* SPDX-License-Identifier: LicenseRef-quantoniumos-Claims-NC
 * Copyright (C) 2025 Luis M. Minier / quantoniumos
 * Listed in CLAIMS_PRACTICING_FILES.txt — licensed under LICENSE-CLAIMS-NC.md
 * (research/education only). Commercial rights require a separate license.
 */

#ifndef ANHARMONIC_STRUCTURED_H
#define ANHARMONIC_STRUCTURED_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <complex.h>
#include "../upstream_abi/phase_kernel_abi.h"  // For anharmonic_phase_variant_t

#ifdef __cplusplus
extern "C" {
#endif

// Mathematical constants
#define ANHARMONIC_STRUCTURED_PHI 1.618033988749894848204586834366  // Golden ratio
#define ANHARMONIC_STRUCTURED_PI 3.141592653589793238462643383279
#define ANHARMONIC_STRUCTURED_2PI (2.0 * ANHARMONIC_STRUCTURED_PI)
#define ANHARMONIC_STRUCTURED_INV_SQRT_2 0.7071067811865475244008443621048490

// Error codes
typedef enum {
    ANHARMONIC_STRUCTURED_SUCCESS = 0,
    ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM = -1,
    ANHARMONIC_STRUCTURED_ERROR_MEMORY = -2,
    ANHARMONIC_STRUCTURED_ERROR_COMPUTATION = -3,
    ANHARMONIC_STRUCTURED_ERROR_NOT_INITIALIZED = -4
} anharmonic_structured_error_t;

// Complex number structure (aligned for SIMD)
typedef struct {
    double real;
    double imag;
} __attribute__((aligned(16))) anharmonic_structured_complex_t;

// Structured phase-schedule parameters
typedef struct {
    size_t num_labels;          // Number of logical schedule labels
    size_t compression_size;    // Compressed state vector size (typically 64)
    double phi;                 // Golden ratio parameter
    double normalization;       // Normalization factor
    bool use_simd;             // Enable SIMD optimizations
    bool use_assembly;         // Enable assembly optimizations
    anharmonic_phase_variant_t variant;     // Phase schedule variant
} anharmonic_structured_params_t;

// Fixed-buffer structured state
typedef struct {
    anharmonic_structured_complex_t* amplitudes;  // Compressed amplitudes array
    size_t size;               // Size of amplitudes array
    size_t num_labels;         // Number of logical schedule labels represented
    double norm;               // State norm
    bool initialized;          // Initialization flag
    void* metadata;            // Optional metadata
} anharmonic_structured_state_t;

// Performance statistics
typedef struct {
    double compression_time_ms;
    double entanglement_time_ms;
    double total_time_ms;
    size_t operations_per_second;
    double memory_mb;
    double compression_ratio;
} anharmonic_structured_perf_stats_t;

// Core API functions
anharmonic_structured_error_t anharmonic_structured_init_state(anharmonic_structured_state_t* state, const anharmonic_structured_params_t* params);
anharmonic_structured_error_t anharmonic_structured_cleanup_state(anharmonic_structured_state_t* state);

// Structured compression engine
anharmonic_structured_error_t anharmonic_structured_compress_schedule(anharmonic_structured_state_t* state, size_t num_labels, size_t compression_size);
anharmonic_structured_error_t anharmonic_structured_compress_schedule_optimized(anharmonic_structured_state_t* state, size_t num_labels, size_t compression_size);

// Correlation diagnostics (not a general entanglement measure)
anharmonic_structured_error_t anharmonic_structured_measure_entanglement(const anharmonic_structured_state_t* state, double* entanglement);
anharmonic_structured_error_t anharmonic_structured_measure_bipartite_entanglement(const anharmonic_structured_state_t* state, size_t partition_size, double* entanglement);

// Small-state construction helpers
anharmonic_structured_error_t anharmonic_structured_create_bell_state(anharmonic_structured_state_t* state, int bell_type);
anharmonic_structured_error_t anharmonic_structured_create_ghz_state(anharmonic_structured_state_t* state, size_t num_labels);

// Small-state operation helpers
anharmonic_structured_error_t anharmonic_structured_apply_hadamard(anharmonic_structured_state_t* state, size_t label_index);
anharmonic_structured_error_t anharmonic_structured_apply_cnot(anharmonic_structured_state_t* state, size_t control, size_t target);
anharmonic_structured_error_t anharmonic_structured_apply_pauli_x(anharmonic_structured_state_t* state, size_t label_index);
anharmonic_structured_error_t anharmonic_structured_apply_pauli_z(anharmonic_structured_state_t* state, size_t label_index);

// Performance and validation
anharmonic_structured_error_t anharmonic_structured_validate_unitarity(const anharmonic_structured_state_t* state, double tolerance, bool* is_unitary);
anharmonic_structured_error_t anharmonic_structured_get_performance_stats(const anharmonic_structured_state_t* state, anharmonic_structured_perf_stats_t* stats);
anharmonic_structured_error_t anharmonic_structured_benchmark_scaling(size_t max_labels, anharmonic_structured_perf_stats_t* results);

// Build information functions
anharmonic_structured_error_t anharmonic_structured_get_version(char* buffer, size_t buffer_size);
anharmonic_structured_error_t anharmonic_structured_get_build_info(char* buffer, size_t buffer_size);

// Utility functions
anharmonic_structured_complex_t anharmonic_structured_complex_mul(anharmonic_structured_complex_t a, anharmonic_structured_complex_t b);
anharmonic_structured_complex_t anharmonic_structured_complex_add(anharmonic_structured_complex_t a, anharmonic_structured_complex_t b);
double anharmonic_structured_complex_abs(anharmonic_structured_complex_t z);
double anharmonic_structured_complex_norm_squared(anharmonic_structured_complex_t z);

// Assembly-optimized functions (implemented in .asm file)
extern void anharmonic_structured_schedule_compression_asm(const double* params, anharmonic_structured_complex_t* output, size_t num_labels, size_t compression_size);
extern void anharmonic_structured_entanglement_measure_asm(const anharmonic_structured_complex_t* state, double* result, size_t size);
extern void anharmonic_structured_complex_vector_norm_asm(anharmonic_structured_complex_t* vector, size_t size);

#ifdef __cplusplus
}
#endif

#endif // ANHARMONIC_STRUCTURED_H
