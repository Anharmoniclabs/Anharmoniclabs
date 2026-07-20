import assert from "node:assert/strict";
import test from "node:test";

import {
  applyControlled,
  applySingle,
  applySwap,
  probabilities,
  sampleCounts,
  simulate,
  stateNorm,
  zeroState,
} from "../../../docs/assets/simulator-core.mjs";

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
