const SQRT1_2 = Math.SQRT1_2;

export const GATE_LABELS = Object.freeze({
  h: "H",
  x: "X",
  y: "Y",
  z: "Z",
  s: "S",
  t: "T",
  rx: "RX",
  ry: "RY",
  rz: "RZ",
  cx: "CX",
  cy: "CY",
  cz: "CZ",
  swap: "SWAP",
});

function complex(re = 0, im = 0) {
  return { re, im };
}

function multiply(left, right) {
  return complex(
    left.re * right.re - left.im * right.im,
    left.re * right.im + left.im * right.re,
  );
}

function add(left, right) {
  return complex(left.re + right.re, left.im + right.im);
}

function scale(value, factor) {
  return complex(value.re * factor, value.im * factor);
}

function magnitudeSquared(value) {
  return value.re * value.re + value.im * value.im;
}

function gateMatrix(name, theta = 0) {
  const half = theta / 2;
  const matrices = {
    h: [
      complex(SQRT1_2), complex(SQRT1_2),
      complex(SQRT1_2), complex(-SQRT1_2),
    ],
    x: [complex(), complex(1), complex(1), complex()],
    y: [complex(), complex(0, -1), complex(0, 1), complex()],
    z: [complex(1), complex(), complex(), complex(-1)],
    s: [complex(1), complex(), complex(), complex(0, 1)],
    t: [
      complex(1), complex(), complex(),
      complex(Math.cos(Math.PI / 4), Math.sin(Math.PI / 4)),
    ],
    rx: [
      complex(Math.cos(half)), complex(0, -Math.sin(half)),
      complex(0, -Math.sin(half)), complex(Math.cos(half)),
    ],
    ry: [
      complex(Math.cos(half)), complex(-Math.sin(half)),
      complex(Math.sin(half)), complex(Math.cos(half)),
    ],
    rz: [
      complex(Math.cos(-half), Math.sin(-half)), complex(), complex(),
      complex(Math.cos(half), Math.sin(half)),
    ],
  };
  const matrix = matrices[name];
  if (!matrix) throw new Error(`Unsupported single-system gate: ${name}`);
  return matrix;
}

function assertIndex(index, count, label) {
  if (!Number.isInteger(index) || index < 0 || index >= count) {
    throw new Error(`${label} must be between 0 and ${count - 1}`);
  }
}

export function zeroState(systemCount) {
  if (!Number.isInteger(systemCount) || systemCount < 1 || systemCount > 10) {
    throw new Error("System count must be an integer from 1 through 10");
  }
  const state = Array.from({ length: 2 ** systemCount }, () => complex());
  state[0] = complex(1);
  return state;
}

export function applySingle(state, systemCount, target, name, theta = 0) {
  assertIndex(target, systemCount, "Target");
  const matrix = gateMatrix(name, theta);
  const next = state.map((value) => complex(value.re, value.im));
  const mask = 1 << target;

  for (let base = 0; base < state.length; base += 1) {
    if ((base & mask) !== 0) continue;
    const paired = base | mask;
    next[base] = add(multiply(matrix[0], state[base]), multiply(matrix[1], state[paired]));
    next[paired] = add(multiply(matrix[2], state[base]), multiply(matrix[3], state[paired]));
  }
  return next;
}

export function applyControlled(state, systemCount, control, target, name) {
  assertIndex(control, systemCount, "Control");
  assertIndex(target, systemCount, "Target");
  if (control === target) throw new Error("Control and target must differ");

  const matrix = gateMatrix(name.slice(1));
  const next = state.map((value) => complex(value.re, value.im));
  const controlMask = 1 << control;
  const targetMask = 1 << target;

  for (let base = 0; base < state.length; base += 1) {
    if ((base & controlMask) === 0 || (base & targetMask) !== 0) continue;
    const paired = base | targetMask;
    next[base] = add(multiply(matrix[0], state[base]), multiply(matrix[1], state[paired]));
    next[paired] = add(multiply(matrix[2], state[base]), multiply(matrix[3], state[paired]));
  }
  return next;
}

export function applySwap(state, systemCount, left, right) {
  assertIndex(left, systemCount, "First target");
  assertIndex(right, systemCount, "Second target");
  if (left === right) throw new Error("SWAP targets must differ");
  const next = state.map((value) => complex(value.re, value.im));
  const leftMask = 1 << left;
  const rightMask = 1 << right;

  for (let index = 0; index < state.length; index += 1) {
    const leftBit = (index & leftMask) !== 0;
    const rightBit = (index & rightMask) !== 0;
    if (leftBit || !rightBit) continue;
    const paired = index ^ leftMask ^ rightMask;
    next[index] = complex(state[paired].re, state[paired].im);
    next[paired] = complex(state[index].re, state[index].im);
  }
  return next;
}

export function simulate(systemCount, operations) {
  let state = zeroState(systemCount);
  for (const operation of operations) {
    const { gate, target, control, theta = 0 } = operation;
    if (["cx", "cy", "cz"].includes(gate)) {
      state = applyControlled(state, systemCount, control, target, gate);
    } else if (gate === "swap") {
      state = applySwap(state, systemCount, control, target);
    } else {
      state = applySingle(state, systemCount, target, gate, theta);
    }
  }
  return state;
}

export function probabilities(state) {
  const values = state.map(magnitudeSquared);
  const total = values.reduce((sum, value) => sum + value, 0);
  return values.map((value) => value / total);
}

export function stateNorm(state) {
  return Math.sqrt(state.reduce((sum, value) => sum + magnitudeSquared(value), 0));
}

export function phase(value) {
  if (magnitudeSquared(value) < 1e-24) return 0;
  return Math.atan2(value.im, value.re);
}

export function formatComplex(value, digits = 5) {
  const threshold = 10 ** -digits;
  const re = Math.abs(value.re) < threshold ? 0 : value.re;
  const im = Math.abs(value.im) < threshold ? 0 : value.im;
  if (im === 0) return re.toFixed(digits);
  if (re === 0) return `${im.toFixed(digits)}i`;
  return `${re.toFixed(digits)} ${im >= 0 ? "+" : "−"} ${Math.abs(im).toFixed(digits)}i`;
}

export function basisLabel(index, width) {
  return index.toString(2).padStart(width, "0");
}

export function shannonEntropy(distribution) {
  return distribution.reduce(
    (entropy, probability) => probability > 0 ? entropy - probability * Math.log2(probability) : entropy,
    0,
  );
}

function seededRandom(seed) {
  let value = seed >>> 0;
  return () => {
    value += 0x6D2B79F5;
    let mixed = value;
    mixed = Math.imul(mixed ^ (mixed >>> 15), mixed | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };
}

export function sampleCounts(distribution, shots, seed = 79, width = 1) {
  if (!Number.isInteger(shots) || shots < 1 || shots > 1_000_000) {
    throw new Error("Shots must be an integer from 1 through 1,000,000");
  }
  const random = seededRandom(seed);
  const cumulative = [];
  distribution.reduce((sum, probability, index) => {
    cumulative[index] = sum + probability;
    return cumulative[index];
  }, 0);
  cumulative[cumulative.length - 1] = 1;
  const counts = {};
  for (let shot = 0; shot < shots; shot += 1) {
    const draw = random();
    const index = cumulative.findIndex((value) => draw < value);
    const label = basisLabel(index, width);
    counts[label] = (counts[label] ?? 0) + 1;
  }
  return counts;
}

export function operationLabel(operation) {
  const base = GATE_LABELS[operation.gate] ?? operation.gate.toUpperCase();
  if (["rx", "ry", "rz"].includes(operation.gate)) {
    return `${base}(${formatAngle(operation.theta)}) q${operation.target}`;
  }
  if (["cx", "cy", "cz"].includes(operation.gate)) {
    return `${base} q${operation.control}→q${operation.target}`;
  }
  if (operation.gate === "swap") {
    return `${base} q${operation.control}↔q${operation.target}`;
  }
  return `${base} q${operation.target}`;
}

export function formatAngle(radians) {
  const ratio = radians / Math.PI;
  if (Math.abs(ratio) < 1e-12) return "0";
  if (Math.abs(ratio - 1) < 1e-12) return "π";
  if (Math.abs(ratio + 1) < 1e-12) return "−π";
  const known = [2, 3, 4, 6, 8];
  for (const denominator of known) {
    const numerator = Math.round(ratio * denominator);
    if (Math.abs(ratio - numerator / denominator) < 1e-12 && numerator !== 0) {
      const sign = numerator < 0 ? "−" : "";
      const absolute = Math.abs(numerator);
      const prefix = absolute === 1 ? "" : absolute;
      return `${sign}${prefix}π/${denominator}`;
    }
  }
  return `${radians.toFixed(3)} rad`;
}
