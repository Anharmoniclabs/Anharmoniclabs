/**
 * Anharmonic Labs Polar native variant kernel interface.
 *
 * IMPORTANT DOMAIN-1 CLASSIFICATION
 * ---------------------------------
 * This C kernel exposes historical and experimental unitary/transform variants.
 * It does NOT implement the canonical square polar-normalized Anharmonic Labs Polar
 *
 *     U = Phi (Phi^H Phi)^(-1/2).
 *
 * The canonical native implementation is ``src/anharmonic_phasemw_native/anharmonic_phasemw_core.hpp``.
 * Variant value 13 in this ABI is the historical unfolded phi carrier bank and
 * must never be reported as the canonical Anharmonic Labs Polar.
 */
/* SPDX-License-Identifier: LicenseRef-quantoniumos-Claims-NC
 * Copyright (C) 2025-2026 Luis M. Minier / quantoniumos
 */
#ifndef ANHARMONIC_PHASE_KERNEL_H
#define ANHARMONIC_PHASE_KERNEL_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ANHARMONIC_PHASE_PI 3.141592653589793238462643383279
#define ANHARMONIC_PHASE_2PI (2.0 * ANHARMONIC_PHASE_PI)
#define ANHARMONIC_PHASE_PHI 1.618033988749894848204586834366

typedef enum {
    ANHARMONIC_PHASE_SUCCESS = 0,
    ANHARMONIC_PHASE_ERROR_INVALID_PARAM = -1,
    ANHARMONIC_PHASE_ERROR_MEMORY = -2,
    ANHARMONIC_PHASE_ERROR_COMPUTATION = -3,
    ANHARMONIC_PHASE_ERROR_NOT_INITIALIZED = -4
} anharmonic_phase_error_t;

#define ANHARMONIC_PHASE_FLAG_DEFAULT            0x00000000
#define ANHARMONIC_PHASE_FLAG_OPTIMIZE_SIMD      0x00000001
#define ANHARMONIC_PHASE_FLAG_HIGH_PRECISION     0x00000002
#define ANHARMONIC_PHASE_FLAG_QUANTUM_SAFE       0x00000004
#define ANHARMONIC_PHASE_FLAG_DEBUG              0x00000008
#define ANHARMONIC_PHASE_FLAG_TOPOLOGICAL        0x00000010
#define ANHARMONIC_PHASE_FLAG_USE_RESONANCE      0x00000010

/*
 * Native variant ABI.
 *
 * These names identify individual native constructions. "Unitary" or successful
 * round-trip behavior does not make a variant equal to the canonical Anharmonic Labs Polar.
 */
typedef enum {
    ANHARMONIC_PHASE_VARIANT_STANDARD = 0,
    ANHARMONIC_PHASE_VARIANT_HARMONIC = 1,
    ANHARMONIC_PHASE_VARIANT_FIBONACCI = 2,
    ANHARMONIC_PHASE_VARIANT_CHAOTIC = 3,
    ANHARMONIC_PHASE_VARIANT_GEOMETRIC = 4,
    ANHARMONIC_PHASE_VARIANT_PHI_CHAOTIC = 5,
    ANHARMONIC_PHASE_VARIANT_HYPERBOLIC = 6,
    ANHARMONIC_PHASE_VARIANT_DCT = 7,
    ANHARMONIC_PHASE_VARIANT_HYBRID_DCT = 8,
    ANHARMONIC_PHASE_VARIANT_CASCADE = 9,
    ANHARMONIC_PHASE_VARIANT_ADAPTIVE_SPLIT = 10,
    ANHARMONIC_PHASE_VARIANT_ENTROPY_GUIDED = 11,
    ANHARMONIC_PHASE_VARIANT_DICTIONARY = 12,
    ANHARMONIC_PHASE_VARIANT_LEGACY_PHI_CARRIER = 13,
    ANHARMONIC_PHASE_VARIANT_BINARY_WAVE = 14,
    ANHARMONIC_PHASE_VARIANT_CRYPTO_SIS = 15
} anharmonic_phase_variant_t;

/*
 * Source compatibility only. New code must use
 * ANHARMONIC_PHASE_VARIANT_LEGACY_PHI_CARRIER. This alias is intentionally not exported by
 * the Python canonical API.
 */
#define ANHARMONIC_PHASE_VARIANT_CANONICAL ANHARMONIC_PHASE_VARIANT_LEGACY_PHI_CARRIER

#define ANHARMONIC_PHASE_DCT_NORM_FACTOR 0.7071067811865476

#define ANHARMONIC_PHASE_TETRA_V0_X  0.5773502691896258
#define ANHARMONIC_PHASE_TETRA_V0_Y  0.5773502691896258
#define ANHARMONIC_PHASE_TETRA_V0_Z  0.5773502691896258
#define ANHARMONIC_PHASE_TETRA_V1_X  0.5773502691896258
#define ANHARMONIC_PHASE_TETRA_V1_Y -0.5773502691896258
#define ANHARMONIC_PHASE_TETRA_V1_Z -0.5773502691896258

typedef struct {
    double real;
    double imag;
} topological_complex_t;

typedef struct {
    int vertex_id;
    double coordinates[3];
    topological_complex_t topological_charge;
    double local_curvature;
    double geometric_phase;
    int connections[10];
    int connection_count;
    topological_complex_t local_state[2];
} vertex_manifold_t;

typedef struct {
    char edge_id[16];
    int vertex_pair[2];
    topological_complex_t edge_weight;
    topological_complex_t braiding_matrix[4];
    topological_complex_t holonomy;
    topological_complex_t wilson_loop;
    double gauge_field[3];
    int error_syndrome;
    bool has_stored_data;
} topological_edge_t;

typedef struct {
    double winding_number_real;
    double winding_number_imag;
    int chern_number;
    double berry_phase;
    int genus;
    int euler_characteristic;
} topological_invariant_t;

typedef struct {
    int qubit_id;
    int num_vertices;
    vertex_manifold_t* vertices;
    topological_edge_t* edges;
    int num_edges;
    int code_distance;
    topological_complex_t global_state[2];
    topological_invariant_t invariants;
} enhanced_topological_qubit_t;

typedef struct {
    double real;
    double imag;
} anharmonic_phase_complex_t;

typedef struct {
    size_t size;
    anharmonic_phase_complex_t* basis;
    double* eigenvalues;
    bool initialized;
    uint32_t flags;
    anharmonic_phase_variant_t variant;
    size_t qubit_count;
    void* quantum_context;
    enhanced_topological_qubit_t* topological_qubits;
    size_t num_topological_qubits;
    bool topological_mode_enabled;
} anharmonic_phase_engine_t;

anharmonic_phase_error_t anharmonic_phase_init_topological_mode(anharmonic_phase_engine_t* engine, size_t num_topological_qubits);
anharmonic_phase_error_t anharmonic_phase_apply_braiding(anharmonic_phase_engine_t* engine, int qubit_id, int vertex_a, int vertex_b, bool clockwise);
anharmonic_phase_error_t anharmonic_phase_encode_topological_edge(anharmonic_phase_engine_t* engine, int qubit_id, const char* edge_id, const anharmonic_phase_complex_t* data, size_t data_size);
anharmonic_phase_error_t anharmonic_phase_decode_topological_edge(anharmonic_phase_engine_t* engine, int qubit_id, const char* edge_id, anharmonic_phase_complex_t* output, size_t* output_size);
anharmonic_phase_error_t anharmonic_phase_surface_code_correction(anharmonic_phase_engine_t* engine, int qubit_id);
anharmonic_phase_error_t anharmonic_phase_measure_topological_invariant(anharmonic_phase_engine_t* engine, int qubit_id, const char* invariant_type, double* result);

anharmonic_phase_error_t anharmonic_phase_init(anharmonic_phase_engine_t* engine, size_t size, uint32_t flags);
anharmonic_phase_error_t anharmonic_phase_cleanup(anharmonic_phase_engine_t* engine);
anharmonic_phase_error_t anharmonic_phase_forward(anharmonic_phase_engine_t* engine, const anharmonic_phase_complex_t* input, anharmonic_phase_complex_t* output, size_t size);
anharmonic_phase_error_t anharmonic_phase_inverse(anharmonic_phase_engine_t* engine, const anharmonic_phase_complex_t* input, anharmonic_phase_complex_t* output, size_t size);
anharmonic_phase_error_t anharmonic_phase_set_variant(anharmonic_phase_engine_t* engine, anharmonic_phase_variant_t variant, bool rebuild_basis);
anharmonic_phase_error_t anharmonic_phase_init_with_variant(anharmonic_phase_engine_t* engine, size_t size, uint32_t flags, anharmonic_phase_variant_t variant);

anharmonic_phase_error_t anharmonic_phase_quantum_basis(anharmonic_phase_engine_t* engine, size_t qubit_count);

anharmonic_phase_complex_t anharmonic_phase_complex_mul(anharmonic_phase_complex_t a, anharmonic_phase_complex_t b);
anharmonic_phase_complex_t anharmonic_phase_complex_add(anharmonic_phase_complex_t a, anharmonic_phase_complex_t b);
double anharmonic_phase_complex_abs(anharmonic_phase_complex_t z);

bool anharmonic_phase_build_basis(anharmonic_phase_engine_t* engine);
anharmonic_phase_error_t anharmonic_phase_validate_unitarity(const anharmonic_phase_engine_t* engine, double tolerance);

anharmonic_phase_error_t anharmonic_phase_von_neumann_entropy(const anharmonic_phase_engine_t* engine, const anharmonic_phase_complex_t* state, double* entropy, size_t size);
anharmonic_phase_error_t anharmonic_phase_entanglement_measure(const anharmonic_phase_engine_t* engine, const anharmonic_phase_complex_t* state, double* entanglement, size_t size);
anharmonic_phase_error_t anharmonic_phase_validate_bell_state(const anharmonic_phase_engine_t* engine, const anharmonic_phase_complex_t* bell_state, double* measured_entanglement, double tolerance);
anharmonic_phase_error_t anharmonic_phase_validate_golden_ratio_properties(const anharmonic_phase_engine_t* engine, double* phi_presence, double tolerance);

#ifdef __cplusplus
}
#endif

#endif
