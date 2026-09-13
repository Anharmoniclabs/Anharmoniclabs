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
  measure: "MEASURE",
  unitary: "U",
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

export function simulate(systemCount, operations, initialState = zeroState(systemCount), parameters = {}) {
  if (!Array.isArray(initialState) || initialState.length !== 2 ** systemCount) {
    throw new Error("Initial state dimension must match system count");
  }
  let state = initialState.map((value) => complex(value.re, value.im));
  const classical = {};
  for (const operation of operations) {
    const { gate, target, control } = operation;
    const theta = typeof operation.theta === "string" ? Number(parameters[operation.theta] ?? 0) : (operation.theta ?? 0);
    if (operation.condition && operation.condition.some(({ bit, value }) => classical[bit] !== value)) continue;
    if (gate === "measure") {
      const measured = measure(state, systemCount, target, operation.random ?? 0.5);
      classical[target] = measured.outcome;
      state = measured.state;
      continue;
    }
    if (gate === "unitary") {
      state = applyUnitary(state, systemCount, operation.targets, operation.matrix);
      continue;
    }
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

export function applyUnitary(state, systemCount, targets, matrix, validateUnitary = true) {
  const targetList = [...targets];
  if (targetList.length < 1 || targetList.length > systemCount ||
      new Set(targetList).size !== targetList.length) {
    throw new Error("Unitary targets must be distinct system indices");
  }
  targetList.forEach((target) => assertIndex(target, systemCount, "Target"));
  const localDimension = 2 ** targetList.length;
  const normalizedMatrix = normalizeComplexMatrix(matrix);
  if (normalizedMatrix.length !== localDimension ||
      normalizedMatrix.some((row) => row.length !== localDimension)) {
    throw new Error(`Unitary matrix must be ${localDimension}x${localDimension}`);
  }
  if (validateUnitary) {
    const product = matrixMultiply(conjugateTranspose(normalizedMatrix), normalizedMatrix);
    const unitaryError = Math.sqrt(product.reduce((sum, row, rowIndex) => sum + row.reduce((inner, value, columnIndex) =>
      inner + (value.re - (rowIndex === columnIndex ? 1 : 0)) ** 2 + value.im ** 2, 0), 0));
    if (!Number.isFinite(unitaryError) || unitaryError > 1e-10) {
      throw new Error("Custom matrix is not unitary; its columns must be orthonormal");
    }
  }
  const next = state.map((value) => complex(value.re, value.im));
  const targetMasks = targetList.map((target) => 1 << target);
  for (let base = 0; base < state.length; base += 1) {
    if (targetMasks.some((mask) => (base & mask) !== 0)) continue;
    const indices = Array.from({ length: localDimension }, (_, localIndex) =>
      targetMasks.reduce((index, mask, bit) =>
        localIndex & (1 << bit) ? index | mask : index, base));
    indices.forEach((index, row) => {
      next[index] = normalizedMatrix[row].reduce((value, coefficient, column) =>
        add(value, multiply(coefficient, state[indices[column]])), complex());
    });
  }
  return next;
}

function normalizeComplexMatrix(matrix) {
  if (!Array.isArray(matrix) || matrix.length === 0 ||
      matrix.some((row) => !Array.isArray(row))) {
    throw new Error("Unitary matrix must be a non-empty square JSON matrix");
  }
  return matrix.map((row) => row.map((value) => {
    if (typeof value === "number") return complex(value);
    if (Array.isArray(value) && value.length === 2) return complex(Number(value[0]), Number(value[1]));
    if (value && typeof value === "object" && "re" in value && "im" in value) {
      return complex(Number(value.re), Number(value.im));
    }
    throw new Error("Matrix entries must be numbers, [real, imaginary] pairs, or {re, im} objects");
  }));
}

function matrixMultiply(left, right) {
  return left.map((row) => right[0].map((_, column) => row.reduce(
    (value, _, index) => add(value, multiply(row[index], right[index][column])),
    complex(),
  )));
}

export function phaseFrequencies(size, ratio = (1 + Math.sqrt(5)) / 2) {
  if (!Number.isInteger(size) || size < 1 || size > 64) throw new Error("Size must be an integer from 1 through 64");
  return Array.from({ length: size }, (_, index) => ((index + 1) * ratio) % 1);
}

export function rawPhaseBasis(size, ratio = (1 + Math.sqrt(5)) / 2) {
  const frequencies = phaseFrequencies(size, ratio);
  return Array.from({ length: size }, (_, row) => frequencies.map((frequency) =>
    complex(Math.cos(2 * Math.PI * frequency * row) / Math.sqrt(size),
      Math.sin(2 * Math.PI * frequency * row) / Math.sqrt(size))));
}

export function gramMatrix(matrix) {
  const columns = matrix[0].length;
  return Array.from({ length: columns }, (_, row) => Array.from({ length: columns }, (_, column) =>
    matrix.reduce((value, sourceRow) => add(value, multiply(
      complex(sourceRow[row].re, -sourceRow[row].im), sourceRow[column])), complex())));
}

function conjugateTranspose(matrix) {
  return matrix[0].map((_, column) => matrix.map((row) => complex(row[column].re, -row[column].im)));
}

function identityMatrix(size) {
  return Array.from({ length: size }, (_, row) => Array.from({ length: size }, (_, column) =>
    complex(row === column ? 1 : 0)));
}

export function polarBasis(size, ratio = (1 + Math.sqrt(5)) / 2) {
  const raw = rawPhaseBasis(size, ratio);
  const gram = gramMatrix(raw);
  let result = identityMatrix(size);
  let inverse = identityMatrix(size);
  // Newton-Schulz converges for the positive Gram matrices in the supported UI range.
  const scaleFactor = Math.max(...gram.map((row, index) => row.reduce((sum, value, column) =>
    sum + (index === column ? Math.hypot(value.re, value.im) : Math.hypot(value.re, value.im)), 0)));
  const normalized = gram.map((row) => row.map((value) => scale(value, 1 / scaleFactor)));
  for (let iteration = 0; iteration < 24; iteration += 1) {
    const inverseSquared = matrixMultiply(inverse, inverse);
    const correction = identityMatrix(size).map((row, rowIndex) => row.map((value, columnIndex) =>
      add(scale(value, 3), scale(matrixMultiply(normalized, inverseSquared)[rowIndex][columnIndex], -1))));
    inverse = matrixMultiply(inverse, correction).map((row) => row.map((value) => scale(value, 0.5)));
  }
  result = matrixMultiply(raw, inverse).map((row) => row.map((value) => scale(value, 1 / Math.sqrt(scaleFactor))));
  return result;
}

export function polarForward(values, ratio) {
  const basis = polarBasis(values.length, ratio);
  return conjugateTranspose(basis).map((row) => row.reduce((value, coefficient, index) =>
    add(value, multiply(coefficient, values[index])), complex()));
}

export function polarInverse(values, ratio) {
  return polarBasis(values.length, ratio).map((row) => row.reduce((value, coefficient, index) =>
    add(value, multiply(coefficient, values[index])), complex()));
}

export function densityMatrix(state) {
  return state.map((left) => state.map((right) => multiply(left, complex(right.re, -right.im))));
}

export function mixedDensityMatrix(weightedStates) {
  if (!weightedStates.length) throw new Error("At least one weighted state is required");
  const dimension = weightedStates[0].state.length;
  const result = Array.from({ length: dimension }, () => Array.from({ length: dimension }, () => complex()));
  weightedStates.forEach(({ state, weight }) => densityMatrix(state).forEach((row, rowIndex) =>
    row.forEach((value, columnIndex) => { result[rowIndex][columnIndex] = add(result[rowIndex][columnIndex], scale(value, weight)); })));
  return result;
}

export function partialTrace(matrix, systemCount, keptSystems) {
  const kept = [...keptSystems];
  const traced = Array.from({ length: systemCount }, (_, index) => index).filter((index) => !kept.includes(index));
  const dimension = 2 ** kept.length;
  const result = Array.from({ length: dimension }, () => Array.from({ length: dimension }, () => complex()));
  for (let row = 0; row < dimension; row += 1) for (let column = 0; column < dimension; column += 1) {
    for (let tracedIndex = 0; tracedIndex < 2 ** traced.length; tracedIndex += 1) {
      const left = [...kept, ...traced].reduce((value, system, bit) =>
        value | (((row >> bit) & 1) << system), 0) | traced.reduce((value, system, bit) =>
        value | (((tracedIndex >> bit) & 1) << system), 0);
      const right = [...kept, ...traced].reduce((value, system, bit) =>
        value | (((column >> bit) & 1) << system), 0) | traced.reduce((value, system, bit) =>
        value | (((tracedIndex >> bit) & 1) << system), 0);
      result[row][column] = add(result[row][column], matrix[left][right]);
    }
  }
  return result;
}

export function purity(matrix) {
  return matrixMultiply(matrix, matrix).reduce((value, row, index) => add(value, row[index]), complex()).re;
}

export function fidelity(left, right) {
  if (Array.isArray(left) && !Array.isArray(left[0])) {
    const overlap = left.reduce((value, amplitude, index) => add(value,
      multiply(complex(amplitude.re, -amplitude.im), right[index])), complex());
    return magnitudeSquared(overlap);
  }
  throw new Error("Mixed-state fidelity requires a density-matrix eigensolver");
}

const PAULI = {
  I: [complex(1), complex(), complex(), complex(1)],
  X: [complex(), complex(1), complex(1), complex()],
  Y: [complex(), complex(0, -1), complex(0, 1), complex()],
  Z: [complex(1), complex(), complex(), complex(-1)],
};

export function pauliExpectation(state, pauliString) {
  if (pauliString.length !== Math.log2(state.length)) throw new Error("Pauli string width must match state dimension");
  let transformed = state;
  [...pauliString].forEach((symbol, target) => {
    if (symbol !== "I") transformed = applySingle(transformed, pauliString.length, target, symbol.toLowerCase());
  });
  return state.reduce((value, amplitude, index) => add(value,
    multiply(complex(amplitude.re, -amplitude.im), transformed[index])), complex()).re;
}

export function measure(state, systemCount, target, random = Math.random()) {
  assertIndex(target, systemCount, "Target");
  const probabilityOne = state.reduce((sum, value, index) =>
    (index & (1 << target)) ? sum + magnitudeSquared(value) : sum, 0);
  const outcome = random < probabilityOne ? 1 : 0;
  const collapsed = state.map((value, index) => (Boolean(index & (1 << target)) === Boolean(outcome)) ? value : complex());
  const norm = stateNorm(collapsed);
  return { outcome, state: collapsed.map((value) => scale(value, 1 / norm)) };
}

export function depolarize(state, systemCount, target, probability) {
  const density = densityMatrix(state);
  const identity = density.map((row) => row.map((value) => scale(value, 1 - probability)));
  ["x", "y", "z"].forEach((gate) => {
    const transformed = densityMatrix(applySingle(state, systemCount, target, gate));
    transformed.forEach((row, rowIndex) => row.forEach((value, columnIndex) => {
      identity[rowIndex][columnIndex] = add(identity[rowIndex][columnIndex], scale(value, probability / 3));
    }));
  });
  return identity;
}

function densityUnitary(matrix, systemCount, target, unitary) {
  const dimension = matrix.length;
  const unitaryColumns = Array.from({ length: dimension }, (_, column) => {
    const basis = Array.from({ length: dimension }, () => complex());
    basis[column] = complex(1);
    return applyUnitary(basis, systemCount, [target], unitary, false);
  });
  const left = Array.from({ length: dimension }, () => Array.from({ length: dimension }, () => complex()));
  for (let column = 0; column < dimension; column += 1) {
    const transformedColumn = applyUnitary(matrix.map((row) => row[column]), systemCount, [target], unitary, false);
    transformedColumn.forEach((value, row) => { left[row][column] = value; });
  }
  return Array.from({ length: dimension }, (_, row) => Array.from({ length: dimension }, (_, column) =>
    left[row].reduce((value, item, index) => add(value,
      multiply(item, complex(unitaryColumns[index][column].re, -unitaryColumns[index][column].im))), complex())));
}

export function noiseChannel(state, systemCount, target, type, probability) {
  if (probability < 0 || probability > 1) throw new Error("Noise probability must be between 0 and 1");
  const density = densityMatrix(state);
  const mix = (terms) => terms.reduce((result, term) => {
    const transformed = densityUnitary(density, systemCount, target, term.matrix);
    transformed.forEach((row, rowIndex) => row.forEach((value, columnIndex) => {
      result[rowIndex][columnIndex] = add(result[rowIndex][columnIndex], scale(value, term.weight));
    }));
    return result;
  }, Array.from({ length: density.length }, () => Array.from({ length: density.length }, () => complex())));
  const identity = [[complex(1), complex()], [complex(), complex(1)]];
  const x = [[complex(), complex(1)], [complex(1), complex()]];
  const y = [[complex(), complex(0, -1)], [complex(0, 1), complex()]];
  const z = [[complex(1), complex()], [complex(), complex(-1)]];
  if (type === "depolarizing") return depolarize(state, systemCount, target, probability);
  if (type === "bit-flip") return mix([{ matrix: identity, weight: 1 - probability }, { matrix: x, weight: probability }]);
  if (type === "phase-flip") return mix([{ matrix: identity, weight: 1 - probability }, { matrix: z, weight: probability }]);
  if (type === "bit-phase-flip") return mix([{ matrix: identity, weight: 1 - probability }, { matrix: y, weight: probability }]);
  if (type === "phase-damping") return mix([{ matrix: identity, weight: 1 - probability }, { matrix: z, weight: probability }]);
  if (type === "amplitude-damping") {
    const damping = [
      [[complex(1), complex()], [complex(), complex(Math.sqrt(1 - probability))]],
      [[complex(), complex(Math.sqrt(probability))], [complex(), complex()]],
    ];
    return damping.reduce((result, matrix) => {
      const transformed = densityUnitary(density, systemCount, target, matrix);
      transformed.forEach((row, rowIndex) => row.forEach((value, columnIndex) => {
        result[rowIndex][columnIndex] = add(result[rowIndex][columnIndex], value);
      }));
      return result;
    }, Array.from({ length: density.length }, () => Array.from({ length: density.length }, () => complex())));
  }
  throw new Error(`Unsupported noise channel: ${type}`);
}

export function structuredCompressSchedule(labelCount, bufferSize = 64) {
  if (!Number.isInteger(labelCount) || labelCount < 1 || !Number.isInteger(bufferSize) || bufferSize < 1) {
    throw new Error("Label count and buffer size must be positive integers");
  }
  const phi = (1 + Math.sqrt(5)) / 2;
  const coefficients = Array.from({ length: bufferSize }, () => complex());
  for (let label = 0; label < labelCount; label += 1) {
    const phaseValue = (label * phi * labelCount) % (2 * Math.PI) +
      (label * Math.sqrt(labelCount) / 1000) % (2 * Math.PI);
    coefficients[label % bufferSize] = add(coefficients[label % bufferSize],
      complex(Math.cos(phaseValue) / Math.sqrt(bufferSize), Math.sin(phaseValue) / Math.sqrt(bufferSize)));
  }
  const norm = stateNorm(coefficients);
  return coefficients.map((value) => scale(value, 1 / norm));
}

const TETRAHEDRAL_COORDINATES = Object.freeze([
  [1 / Math.sqrt(3), 1 / Math.sqrt(3), 1 / Math.sqrt(3)],
  [1 / Math.sqrt(3), -1 / Math.sqrt(3), -1 / Math.sqrt(3)],
  [-1 / Math.sqrt(3), 1 / Math.sqrt(3), -1 / Math.sqrt(3)],
  [-1 / Math.sqrt(3), -1 / Math.sqrt(3), 1 / Math.sqrt(3)],
]);

function vertexEdgeId(left, right) {
  return `v${Math.min(left, right)}-v${Math.max(left, right)}`;
}

export function createVertexQubit(qubitId = 0) {
  const vertices = TETRAHEDRAL_COORDINATES.map((coordinates, vertexId) => ({
    vertexId,
    coordinates: [...coordinates],
    topologicalCharge: complex(),
    localCurvature: 0,
    geometricPhase: 0,
    connections: Array.from({ length: 4 }, (_, index) => index).filter((index) => index !== vertexId),
    localState: [complex(1), complex()],
  }));
  const edges = [];
  for (let left = 0; left < vertices.length; left += 1) for (let right = left + 1; right < vertices.length; right += 1) {
    edges.push({
      edgeId: vertexEdgeId(left, right),
      vertexPair: [left, right],
      edgeWeight: complex(1),
      braidingMatrix: [complex(1), complex(), complex(), complex(1)],
      holonomy: complex(1),
      wilsonLoop: complex(1),
      gaugeField: [0, 0, 0],
      errorSyndrome: 0,
      hasStoredData: false,
    });
  }
  return {
    qubitId,
    vertices,
    edges,
    codeDistance: 2,
    globalState: [complex(1), complex()],
    invariants: {
      windingNumber: complex(),
      chernNumber: 0,
      berryPhase: 0,
      genus: 0,
      eulerCharacteristic: 2,
    },
  };
}

export function applyVertexBraiding(model, vertexA, vertexB, clockwise = true) {
  if (!model || !Array.isArray(model.vertices) || vertexA === vertexB ||
      !model.vertices[vertexA] || !model.vertices[vertexB]) {
    throw new Error("Braiding requires two distinct vertex indices");
  }
  const edge = model.edges.find(({ vertexPair }) =>
    vertexPair.includes(vertexA) && vertexPair.includes(vertexB));
  if (!edge) throw new Error("No edge connects the selected vertices");
  const angle = clockwise ? Math.PI / 2 : -Math.PI / 2;
  const phaseFactor = complex(Math.cos(angle), Math.sin(angle));
  edge.braidingMatrix = [complex(1), complex(), complex(), phaseFactor];
  edge.holonomy = multiply(edge.holonomy, phaseFactor);
  edge.wilsonLoop = multiply(edge.wilsonLoop, phaseFactor);
  edge.gaugeField = [0, 0, angle];
  model.vertices[vertexA].geometricPhase += angle;
  model.vertices[vertexB].geometricPhase -= angle;
  model.vertices[vertexA].localCurvature += clockwise ? 0.25 : -0.25;
  model.vertices[vertexB].localCurvature += clockwise ? 0.25 : -0.25;
  model.globalState[0] = multiply(model.globalState[0], phaseFactor);
  model.invariants.berryPhase = (model.invariants.berryPhase + angle) % (2 * Math.PI);
  model.invariants.windingNumber = add(model.invariants.windingNumber, complex(angle / (2 * Math.PI)));
  return model;
}

export function measureVertexInvariant(model, invariantType, edgeId = null) {
  if (!model || !model.invariants) throw new Error("Vertex-qubit model is required");
  if (invariantType === "wilson_loop" || invariantType === "holonomy") {
    const edge = model.edges.find((candidate) => candidate.edgeId === edgeId) ?? model.edges[0];
    if (!edge) throw new Error("Vertex-qubit edge is unavailable");
    return edge[invariantType === "wilson_loop" ? "wilsonLoop" : "holonomy"];
  }
  if (!(invariantType in model.invariants)) throw new Error(`Unknown topological invariant: ${invariantType}`);
  return model.invariants[invariantType];
}

export function sparseZeroState(systemCount) {
  if (!Number.isInteger(systemCount) || systemCount < 1 || systemCount > 50) {
    throw new Error("Sparse system count must be an integer from 1 through 50");
  }
  return { systemCount, amplitudes: new Map([[0, complex(1)]]) };
}

function sparseAdd(amplitudes, index, value, tolerance = 1e-14) {
  const current = amplitudes.get(index) ?? complex();
  const next = add(current, value);
  if (Math.hypot(next.re, next.im) <= tolerance) amplitudes.delete(index);
  else amplitudes.set(index, next);
}

function sparseHasBit(index, mask) {
  return Math.floor(index / mask) % 2 === 1;
}

export function sparseApplySingle(sparse, target, name, theta = 0, maxTerms = 1_000_000) {
  const mask = 2 ** target;
  const matrix = gateMatrix(name, theta);
  const next = new Map();
  const bases = new Set([...sparse.amplitudes.keys()].map((index) =>
    sparseHasBit(index, mask) ? index - mask : index));
  bases.forEach((base) => {
    const zero = sparse.amplitudes.get(base) ?? complex();
    const one = sparse.amplitudes.get(base + mask) ?? complex();
    sparseAdd(next, base, add(multiply(matrix[0], zero), multiply(matrix[1], one)));
    sparseAdd(next, base + mask, add(multiply(matrix[2], zero), multiply(matrix[3], one)));
  });
  if (next.size > maxTerms) throw new Error(`Sparse state exceeded ${maxTerms} nonzero amplitudes`);
  return { systemCount: sparse.systemCount, amplitudes: next };
}

export function sparseApplyControlled(sparse, control, target, name, maxTerms = 1_000_000) {
  if (control === target) throw new Error("Control and target must differ");
  const controlMask = 2 ** control;
  const targetMask = 2 ** target;
  const matrix = gateMatrix(name.slice(1));
  const next = new Map(sparse.amplitudes);
  const bases = new Set([...sparse.amplitudes.keys()].filter((index) =>
    sparseHasBit(index, controlMask) && !sparseHasBit(index, targetMask)));
  bases.forEach((base) => {
    const zero = sparse.amplitudes.get(base) ?? complex();
    const one = sparse.amplitudes.get(base + targetMask) ?? complex();
    next.delete(base);
    next.delete(base + targetMask);
    sparseAdd(next, base, add(multiply(matrix[0], zero), multiply(matrix[1], one)));
    sparseAdd(next, base + targetMask, add(multiply(matrix[2], zero), multiply(matrix[3], one)));
  });
  if (next.size > maxTerms) throw new Error(`Sparse state exceeded ${maxTerms} nonzero amplitudes`);
  return { systemCount: sparse.systemCount, amplitudes: next };
}

export function sparseApplySwap(sparse, left, right) {
  if (left === right) throw new Error("SWAP targets must differ");
  const leftMask = 2 ** left;
  const rightMask = 2 ** right;
  const next = new Map();
  sparse.amplitudes.forEach((value, index) => {
    const leftBit = sparseHasBit(index, leftMask);
    const rightBit = sparseHasBit(index, rightMask);
    const target = leftBit === rightBit ? index : leftBit
      ? index - leftMask + rightMask
      : index + leftMask - rightMask;
    next.set(target, value);
  });
  return { systemCount: sparse.systemCount, amplitudes: next };
}

export function sparseSimulate(systemCount, operations, maxTerms = 1_000_000) {
  let sparse = sparseZeroState(systemCount);
  operations.forEach(({ gate, target, control, theta = 0 }) => {
    if (["cx", "cy", "cz"].includes(gate)) sparse = sparseApplyControlled(sparse, control, target, gate, maxTerms);
    else if (gate === "swap") sparse = sparseApplySwap(sparse, control, target);
    else sparse = sparseApplySingle(sparse, target, gate, theta, maxTerms);
  });
  return sparse;
}

export function sparseRecords(sparse) {
  return [...sparse.amplitudes.entries()].sort(([left], [right]) => left - right).map(([index, value]) => ({
    index,
    re: value.re,
    im: value.im,
    probability: magnitudeSquared(value),
  }));
}

export function sparseProbabilities(sparse) {
  return sparseRecords(sparse).map(({ index, probability }) => ({ index, probability }));
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
  if (operation.gate === "unitary") {
    return `${base} ${operation.targets.map((target) => `q${target}`).join(",")}`;
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
  if (typeof radians === "string") return radians;
  if (!Number.isFinite(radians)) return "0";
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
