import assert from "node:assert/strict";
import test from "node:test";

import {
  applyVertexBraiding,
  applyControlled,
  applySingle,
  applySwap,
  densityMatrix,
  depolarize,
  gramMatrix,
  measure,
  pauliExpectation,
  polarBasis,
  polarForward,
  polarInverse,
  partialTrace,
  probabilities,
  operationLabel,
  createVertexQubit,
  measureVertexInvariant,
  purity,
  noiseChannel,
  sampleCounts,
  sparseRecords,
  sparseSimulate,
  simulate,
  stateNorm,
  zeroState,
} from "../../../assets/simulator-core.mjs";

const close = (actual, expected, tolerance = 1e-12) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);

test("zero state has unit norm", () => {
  close(stateNorm(zeroState(4)), 1);
});

test("Hadamard creates equal probabilities", () => {
  const result = applySingle(zeroState(1), 1, 0, "h");
  const distribution = probabilities(result);
  close(distribution[0], 0.5);
  close(distribution[1], 0.5);
});

test("Bell circuit uses little-endian control semantics", () => {
  const result = simulate(2, [
    { gate: "h", target: 0 },
    { gate: "cx", control: 0, target: 1 },
  ]);
  const distribution = probabilities(result);
  close(distribution[0], 0.5);
  close(distribution[1], 0);
  close(distribution[2], 0);
  close(distribution[3], 0.5);
});

test("controlled Y applies its complex phase", () => {
  let result = applySingle(zeroState(2), 2, 0, "x");
  result = applyControlled(result, 2, 0, 1, "cy");
  close(result[3].re, 0);
  close(result[3].im, 1);
});

test("SWAP exchanges basis coordinates", () => {
  let result = applySingle(zeroState(2), 2, 0, "x");
  result = applySwap(result, 2, 0, 1);
  close(probabilities(result)[2], 1);
});

test("rotations preserve normalization", () => {
  const result = simulate(3, [
    { gate: "rx", target: 0, theta: 0.371 },
    { gate: "ry", target: 1, theta: -1.9 },
    { gate: "rz", target: 2, theta: 2.7 },
    { gate: "cx", control: 1, target: 2 },
  ]);
  close(stateNorm(result), 1);
});

test("sampling is deterministic for a fixed seed", () => {
  const distribution = [0.5, 0.5];
  assert.deepEqual(
    sampleCounts(distribution, 100, 79, 1),
    sampleCounts(distribution, 100, 79, 1),
  );
});

test("golden-phase polar basis is unitary and round-trips", () => {
  const basis = polarBasis(4);
  const gram = gramMatrix(basis);
  gram.forEach((row, rowIndex) => row.forEach((value, columnIndex) => {
    close(value.re, rowIndex === columnIndex ? 1 : 0, 1e-10);
    close(value.im, 0, 1e-10);
  }));
  const initial = zeroState(2).map((value, index) => index === 1 ? { re: 0.5, im: 0.5 } : value);
  const roundTrip = polarInverse(polarForward(initial));
  roundTrip.forEach((value, index) => {
    close(value.re, initial[index].re, 1e-10);
    close(value.im, initial[index].im, 1e-10);
  });
});

test("density analysis detects Bell correlations and mixed reduction", () => {
  const bell = simulate(2, [
    { gate: "h", target: 0 },
    { gate: "cx", control: 0, target: 1 },
  ]);
  const reduced = partialTrace(densityMatrix(bell), 2, [0]);
  close(reduced[0][0].re, 0.5);
  close(reduced[1][1].re, 0.5);
  close(purity(densityMatrix(bell)), 1);
  close(pauliExpectation(bell, "XX"), 1);
  close(pauliExpectation(bell, "ZZ"), 1);
});

test("measurement collapses and depolarizing noise preserves trace", () => {
  const state = applySingle(zeroState(1), 1, 0, "h");
  const measured = measure(state, 1, 0, 0.1);
  close(stateNorm(measured.state), 1);
  assert.equal(measured.outcome, 1);
  const noisy = depolarize(state, 1, 0, 0.2);
  close(noisy[0][0].re + noisy[1][1].re, 1);
});

test("mid-circuit measurement feeds a classical conditional", () => {
  const result = simulate(2, [
    { gate: "x", target: 0 },
    { gate: "measure", target: 0, random: 0.1 },
    { gate: "x", target: 1, condition: [{ bit: 0, value: 1 }] },
  ]);
  close(probabilities(result)[3], 1);
});

test("noise channels preserve density-matrix trace", () => {
  const state = applySingle(zeroState(1), 1, 0, "h");
  ["bit-flip", "phase-flip", "bit-phase-flip", "phase-damping", "amplitude-damping"].forEach((channel) => {
    const matrix = noiseChannel(state, 1, 0, channel, 0.2);
    close(matrix[0][0].re + matrix[1][1].re, 1);
  });
});

test("named rotation parameters bind during replay", () => {
  const result = simulate(1, [{ gate: "rz", target: 0, theta: "angle" }], undefined, { angle: Math.PI });
  close(result[0].re, 0);
  close(result[0].im, -1);
  close(result[1].re, 0);
  close(result[1].im, 0);
});

test("parameterized and custom-unitary labels stay renderable", () => {
  assert.equal(operationLabel({ gate: "rz", target: 0, theta: "theta" }), "RZ(theta) q0");
  assert.equal(operationLabel({ gate: "unitary", targets: [0, 1] }), "U q0,q1");
});

test("custom unitaries accept ordinary numeric JSON matrices", () => {
  const result = simulate(1, [{
    gate: "unitary",
    targets: [0],
    matrix: [[0, 1], [1, 0]],
  }]);
  close(probabilities(result)[1], 1);
});

test("vertex geometry exposes tetrahedral edges and braid invariants", () => {
  const model = createVertexQubit(3);
  assert.equal(model.vertices.length, 4);
  assert.equal(model.edges.length, 6);
  model.vertices.forEach(({ coordinates }) => coordinates.forEach((coordinate) => assert.ok(Number.isFinite(coordinate))));
  applyVertexBraiding(model, 0, 1, true);
  close(model.invariants.berryPhase, Math.PI / 2);
  const holonomy = measureVertexInvariant(model, "holonomy", "v0-v1");
  close(holonomy.re, 0, 1e-12);
  close(holonomy.im, 1, 1e-12);
});

test("sparse mode preserves qubit-50 indices without 32-bit overflow", () => {
  const sparse = sparseSimulate(50, [
    { gate: "x", target: 49 },
    { gate: "cx", control: 49, target: 0 },
    { gate: "x", target: 1 },
    { gate: "swap", control: 1, target: 48 },
  ]);
  const records = sparseRecords(sparse);
  assert.equal(records.length, 1);
  assert.equal(records[0].index, 844424930131969);
  close(records[0].probability, 1);
});
