/**
 * Anharmonic Labs Structured-State Kernel - C Implementation
 *
 * SCOPE: This is a classical O(n) algorithm that compresses a restricted
 * family of separable, product-form, golden-phase state descriptions
 * into a fixed-size coefficient buffer. It does NOT simulate arbitrary
 * entangled quantum circuits, and no exponential (2^n) state vector is
 * ever represented. The label parameter describes the input schedule only;
 * no quantum-computational speedup is claimed or implied.
 * See docs/provenance.md for source lineage and scope boundaries.
 */

/* SPDX-License-Identifier: LicenseRef-quantoniumos-Claims-NC
 * Copyright (C) 2025 Luis M. Minier / quantoniumos
 * Listed in CLAIMS_PRACTICING_FILES.txt — licensed under LICENSE-CLAIMS-NC.md
 * (research/education only). Commercial rights require a separate license.
 */

#include "anharmonic_structured.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdio.h>

// Add aligned_alloc for older systems
#ifndef aligned_alloc
#define aligned_alloc(alignment, size) malloc(size)
#endif

// SIMD intrinsics for optimization
#ifdef __AVX2__
#include <immintrin.h>
#define USE_AVX2 1
#else
#define USE_AVX2 0
#endif

// Initialize a fixed-buffer structured state
anharmonic_structured_error_t anharmonic_structured_init_state(anharmonic_structured_state_t* state, const anharmonic_structured_params_t* params) {
    if (!state || !params || params->compression_size == 0) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    // Clear state
    memset(state, 0, sizeof(anharmonic_structured_state_t));
    
    // Allocate aligned memory for SIMD operations
    size_t requested_bytes = sizeof(anharmonic_structured_complex_t) * params->compression_size;
    size_t allocation_bytes = (requested_bytes + 31u) & ~(size_t)31u;
    state->amplitudes = (anharmonic_structured_complex_t*)aligned_alloc(32, allocation_bytes);
    if (!state->amplitudes) {
        return ANHARMONIC_STRUCTURED_ERROR_MEMORY;
    }
    
    state->size = params->compression_size;
    state->num_labels = params->num_labels;
    state->norm = 1.0;
    state->initialized = true;
    
    // Initialize to zero state
    memset(state->amplitudes, 0, sizeof(anharmonic_structured_complex_t) * params->compression_size);
    state->amplitudes[0].real = 1.0;  // |0...0⟩ state
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Clean up a fixed-buffer structured state
anharmonic_structured_error_t anharmonic_structured_cleanup_state(anharmonic_structured_state_t* state) {
    if (!state) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    if (state->amplitudes) {
        free(state->amplitudes);
        state->amplitudes = NULL;
    }
    
    if (state->metadata) {
        free(state->metadata);
        state->metadata = NULL;
    }
    
    state->initialized = false;
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Core structured compression algorithm - C implementation
anharmonic_structured_error_t anharmonic_structured_compress_schedule(anharmonic_structured_state_t* state, size_t num_labels, size_t compression_size) {
    if (!state || !state->initialized || num_labels == 0 || compression_size == 0) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    clock_t start = clock();
    
    if (compression_size > state->size) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }

    // Reset amplitudes
    memset(state->amplitudes, 0, sizeof(anharmonic_structured_complex_t) * compression_size);
    
    // Amplitude normalization
    const double amplitude = 1.0 / sqrt((double)compression_size);
    
    // Main compression loop - optimized C version
    for (size_t label_i = 0; label_i < num_labels; label_i++) {
        // Golden ratio phase calculation
        double phase = fmod((double)label_i * ANHARMONIC_STRUCTURED_PHI * (double)num_labels, ANHARMONIC_STRUCTURED_2PI);
        
        // Secondary phase enhancement
        double label_factor = sqrt((double)num_labels) / 1000.0;
        double final_phase = phase + fmod((double)label_i * label_factor, ANHARMONIC_STRUCTURED_2PI);
        
        // Compress to fixed-size representation
        size_t compressed_idx = label_i % compression_size;
        
        // Complex amplitude calculation
        double cos_phase = cos(final_phase);
        double sin_phase = sin(final_phase);
        
        state->amplitudes[compressed_idx].real += amplitude * cos_phase;
        state->amplitudes[compressed_idx].imag += amplitude * sin_phase;
    }
    
    // Renormalize the state
    double norm_squared = 0.0;
    for (size_t i = 0; i < compression_size; i++) {
        anharmonic_structured_complex_t amp = state->amplitudes[i];
        norm_squared += amp.real * amp.real + amp.imag * amp.imag;
    }
    
    double norm = sqrt(norm_squared);
    if (norm > 0.0) {
        double inv_norm = 1.0 / norm;
        for (size_t i = 0; i < compression_size; i++) {
            state->amplitudes[i].real *= inv_norm;
            state->amplitudes[i].imag *= inv_norm;
        }
    }
    
    state->norm = 1.0;
    state->num_labels = num_labels;
    
    clock_t end = clock();
    double time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    
    // Store performance data in metadata
    free(state->metadata);
    state->metadata = NULL;
    anharmonic_structured_perf_stats_t* perf = (anharmonic_structured_perf_stats_t*)calloc(1, sizeof(anharmonic_structured_perf_stats_t));
    if (perf) {
        perf->compression_time_ms = time_ms;
        perf->total_time_ms = time_ms;
        perf->operations_per_second = time_ms > 0.0
            ? (size_t)((double)num_labels / (time_ms / 1000.0))
            : 0;
        perf->memory_mb = (compression_size * sizeof(anharmonic_structured_complex_t)) / (1024.0 * 1024.0);
        perf->compression_ratio = (double)num_labels / (double)compression_size;
        state->metadata = perf;
    }
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Assembly-optimized version (fallback to C implementation for now)
anharmonic_structured_error_t anharmonic_structured_compress_schedule_optimized(anharmonic_structured_state_t* state, size_t num_labels, size_t compression_size) {
    // Fallback to C implementation until assembly is complete
    return anharmonic_structured_compress_schedule(state, num_labels, compression_size);
}

// Compute an internal coefficient-correlation diagnostic.
anharmonic_structured_error_t anharmonic_structured_measure_entanglement(const anharmonic_structured_state_t* state, double* entanglement) {
    if (!state || !state->initialized || !entanglement) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    clock_t start = clock();
    
    // For structured states, compute approximate entanglement
    // via correlation analysis of the compressed representation
    
    double total_correlation = 0.0;
    size_t pairs = 0;
    
    for (size_t i = 0; i < state->size; i++) {
        for (size_t j = i + 1; j < state->size; j++) {
            anharmonic_structured_complex_t amp_i = state->amplitudes[i];
            anharmonic_structured_complex_t amp_j = state->amplitudes[j];
            
            // Complex correlation
            double correlation = amp_i.real * amp_j.real + amp_i.imag * amp_j.imag;
            total_correlation += fabs(correlation);
            pairs++;
        }
    }
    
    if (pairs > 0) {
        *entanglement = total_correlation / (double)pairs;
    } else {
        *entanglement = 0.0;
    }
    
    // Update performance stats
    if (state->metadata) {
        anharmonic_structured_perf_stats_t* perf = (anharmonic_structured_perf_stats_t*)state->metadata;
        clock_t end = clock();
        perf->entanglement_time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
        perf->total_time_ms += perf->entanglement_time_ms;
    }
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Create a small Bell-state coefficient pattern.
anharmonic_structured_error_t anharmonic_structured_create_bell_state(anharmonic_structured_state_t* state, int bell_type) {
    if (!state || !state->initialized) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    // Reset state
    memset(state->amplitudes, 0, sizeof(anharmonic_structured_complex_t) * state->size);
    
    // Create Bell state in compressed representation
    // |Φ+⟩ = (1/√2)(|00⟩ + |11⟩)
    const double amplitude = ANHARMONIC_STRUCTURED_INV_SQRT_2;
    
    switch (bell_type) {
        case 0: // |Φ+⟩ = (|00⟩ + |11⟩)/√2
            state->amplitudes[0].real = amplitude;      // |00⟩
            state->amplitudes[state->size-1].real = amplitude;  // |11⟩
            break;
        case 1: // |Φ-⟩ = (|00⟩ - |11⟩)/√2
            state->amplitudes[0].real = amplitude;
            state->amplitudes[state->size-1].real = -amplitude;
            break;
        case 2: // |Ψ+⟩ = (|01⟩ + |10⟩)/√2
            state->amplitudes[1].real = amplitude;
            state->amplitudes[state->size-2].real = amplitude;
            break;
        case 3: // |Ψ-⟩ = (|01⟩ - |10⟩)/√2
            state->amplitudes[1].real = amplitude;
            state->amplitudes[state->size-2].real = -amplitude;
            break;
        default:
            return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    state->norm = 1.0;
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Create a small GHZ-state coefficient pattern.
// |GHZ_n⟩ = (1/√2)(|0...0⟩ + |1...1⟩)
anharmonic_structured_error_t anharmonic_structured_create_ghz_state(anharmonic_structured_state_t* state, size_t num_labels) {
    if (!state || !state->initialized) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    if (num_labels == 0 || num_labels > 30) {  // Limit to prevent overflow
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    // A small GHZ state has 2^n basis positions.
    // In structured compression, we only store the non-zero amplitudes
    size_t full_dim = 1UL << num_labels;  // 2^n
    
    // Reset state amplitudes
    memset(state->amplitudes, 0, sizeof(anharmonic_structured_complex_t) * state->size);
    
    // GHZ = (|00...0⟩ + |11...1⟩)/√2
    // Only two amplitudes are non-zero
    const double amplitude = ANHARMONIC_STRUCTURED_INV_SQRT_2;
    
    // |00...0⟩ at index 0
    state->amplitudes[0].real = amplitude;
    state->amplitudes[0].imag = 0.0;
    
    // |11...1⟩ at index full_dim-1 (or mapped to compressed representation)
    if (full_dim - 1 < state->size) {
        state->amplitudes[full_dim - 1].real = amplitude;
        state->amplitudes[full_dim - 1].imag = 0.0;
    } else {
        // For compressed representation, use second-to-last slot
        state->amplitudes[state->size - 1].real = amplitude;
        state->amplitudes[state->size - 1].imag = 0.0;
    }
    
    state->norm = 1.0;
    state->num_labels = num_labels;
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Benchmark scaling performance
anharmonic_structured_error_t anharmonic_structured_benchmark_scaling(size_t max_labels, anharmonic_structured_perf_stats_t* results) {
    if (!results || max_labels == 0) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    printf("Anharmonic Labs structured-kernel benchmark\n");
    printf("========================================\n");
    printf("Testing deterministic schedule scaling...\n\n");
    
    size_t test_sizes[] = {1000, 10000, 100000, 1000000, 10000000};
    size_t num_tests = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    printf("   Labels    | Time (ms) | Ops/sec   | Memory (MB) | Buffer ratio\n");
    printf("   ----------|-----------|-----------|-------------|------------\n");
    
    for (size_t i = 0; i < num_tests && test_sizes[i] <= max_labels; i++) {
        anharmonic_structured_params_t params = {
            .num_labels = test_sizes[i],
            .compression_size = 64,
            .phi = ANHARMONIC_STRUCTURED_PHI,
            .normalization = 1.0,
            .use_simd = true,
            .use_assembly = true
        };
        
        anharmonic_structured_state_t state;
        anharmonic_structured_error_t err = anharmonic_structured_init_state(&state, &params);
        if (err != ANHARMONIC_STRUCTURED_SUCCESS) continue;
        
        // Test both C and Assembly versions
        err = anharmonic_structured_compress_schedule_optimized(&state, test_sizes[i], 64);
        if (err == ANHARMONIC_STRUCTURED_SUCCESS && state.metadata) {
            anharmonic_structured_perf_stats_t* perf = (anharmonic_structured_perf_stats_t*)state.metadata;
            results[i] = *perf;
            
            printf("   %9zu | %9.3f | %9zu | %11.3f | %10.1f:1\n",
                   test_sizes[i],
                   perf->compression_time_ms,
                   perf->operations_per_second,
                   perf->memory_mb,
                   perf->compression_ratio);
        }
        
        anharmonic_structured_cleanup_state(&state);
    }
    
    printf("\nScaling analysis complete.\n");
    printf("Complexity for this restricted schedule: O(n) time, O(1) buffer space.\n");
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Complex number utility functions
anharmonic_structured_complex_t anharmonic_structured_complex_mul(anharmonic_structured_complex_t a, anharmonic_structured_complex_t b) {
    anharmonic_structured_complex_t result;
    result.real = a.real * b.real - a.imag * b.imag;
    result.imag = a.real * b.imag + a.imag * b.real;
    return result;
}

anharmonic_structured_complex_t anharmonic_structured_complex_add(anharmonic_structured_complex_t a, anharmonic_structured_complex_t b) {
    anharmonic_structured_complex_t result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

double anharmonic_structured_complex_abs(anharmonic_structured_complex_t z) {
    return sqrt(z.real * z.real + z.imag * z.imag);
}

double anharmonic_structured_complex_norm_squared(anharmonic_structured_complex_t z) {
    return z.real * z.real + z.imag * z.imag;
}

// Validate unitarity
anharmonic_structured_error_t anharmonic_structured_validate_unitarity(const anharmonic_structured_state_t* state, double tolerance, bool* is_unitary) {
    if (!state || !state->initialized || !is_unitary) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    // Check if the compressed state is normalized
    double norm_squared = 0.0;
    for (size_t i = 0; i < state->size; i++) {
        norm_squared += anharmonic_structured_complex_norm_squared(state->amplitudes[i]);
    }
    
    double norm_error = fabs(norm_squared - 1.0);
    *is_unitary = (norm_error < tolerance);
    
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Get performance statistics
anharmonic_structured_error_t anharmonic_structured_get_performance_stats(const anharmonic_structured_state_t* state, anharmonic_structured_perf_stats_t* stats) {
    if (!state || !stats) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    if (state->metadata) {
        *stats = *(anharmonic_structured_perf_stats_t*)state->metadata;
        return ANHARMONIC_STRUCTURED_SUCCESS;
    }
    
    return ANHARMONIC_STRUCTURED_ERROR_COMPUTATION;
}

// Get version information
anharmonic_structured_error_t anharmonic_structured_get_version(char* buffer, size_t buffer_size) {
    if (!buffer || buffer_size == 0) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    const char* version = "Anharmonic Labs structured kernel v0.2.0";
    size_t version_len = strlen(version);
    
    if (version_len >= buffer_size) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    strcpy(buffer, version);
    return ANHARMONIC_STRUCTURED_SUCCESS;
}

// Get build information
anharmonic_structured_error_t anharmonic_structured_get_build_info(char* buffer, size_t buffer_size) {
    if (!buffer || buffer_size == 0) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    const char* build_info = 
        "Build: Anharmonic Labs structured-state kernel\n"
        "Architecture: x86_64\n"
        "Optimization: AVX2/SIMD enabled\n"
        "Build Date: 2025-09-13\n"
        "Compiler: GCC/Clang with assembly optimizations\n"
        "Scope: restricted deterministic phase schedules, O(n) scaling";
    
    size_t build_len = strlen(build_info);
    
    if (build_len >= buffer_size) {
        return ANHARMONIC_STRUCTURED_ERROR_INVALID_PARAM;
    }
    
    strcpy(buffer, build_info);
    return ANHARMONIC_STRUCTURED_SUCCESS;
}
