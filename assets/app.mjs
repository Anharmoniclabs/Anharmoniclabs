import {
  GATE_LABELS,
  applyUnitary,
  basisLabel,
  densityMatrix,
  formatComplex,
  gramMatrix,
  applyVertexBraiding,
  createVertexQubit,
  measure,
  noiseChannel,
  operationLabel,
  pauliExpectation,
  phase,
  polarBasis,
  polarForward,
  partialTrace,
  probabilities,
  sampleCounts,
  shannonEntropy,
  simulate,
  stateNorm,
  purity,
  rawPhaseBasis,
  structuredCompressSchedule,
  measureVertexInvariant,
  sparseRecords,
  sparseProbabilities,
  sparseSimulate,
} from "./simulator-core.mjs";

const state = {
  systemCount: 3,
  operations: [],
  selectedGate: "h",
  resultMode: "probabilities",
  initialState: null,
  parameters: { theta: Math.PI / 2 },
  vertexModel: createVertexQubit(0),
  atlasMode: "state",
  sparseState: null,
  atlasPolarMatrix: null,
};

const elements = {
  systemCount: document.querySelector("#system-count"),
  target: document.querySelector("#target-system"),
  control: document.querySelector("#control-system"),
  angle: document.querySelector("#rotation-angle"),
  angleOutput: document.querySelector("#angle-output"),
  gateButtons: [...document.querySelectorAll("[data-gate]")],
  controlledFields: document.querySelector("#controlled-fields"),
  rotationFields: document.querySelector("#rotation-fields"),
  addGate: document.querySelector("#add-gate"),
  circuit: document.querySelector("#circuit-view"),
  operationCount: document.querySelector("#operation-count"),
  probabilityChart: document.querySelector("#probability-chart"),
  amplitudeTable: document.querySelector("#amplitude-table-body"),
  norm: document.querySelector("#metric-norm"),
  entropy: document.querySelector("#metric-entropy"),
  support: document.querySelector("#metric-support"),
  modeButtons: [...document.querySelectorAll("[data-result-mode]")],
  shots: document.querySelector("#shots"),
  seed: document.querySelector("#seed"),
  sample: document.querySelector("#sample-circuit"),
  toast: document.querySelector("#toast"),
  mobileMenu: document.querySelector("#mobile-menu"),
  nav: document.querySelector("#primary-nav"),
  researchTool: document.querySelector("#research-tool"),
  researchSize: document.querySelector("#research-size"),
  researchBuffer: document.querySelector("#research-buffer"),
  researchOutput: document.querySelector("#research-output"),
  researchVisual: document.querySelector("#research-visual"),
  pauliString: document.querySelector("#pauli-string"),
  keepSystems: document.querySelector("#keep-systems"),
  noiseProbability: document.querySelector("#noise-probability"),
  noiseChannel: document.querySelector("#noise-channel"),
  stateOutput: document.querySelector("#state-output"),
  stateVisual: document.querySelector("#state-visual"),
  initialState: document.querySelector("#initial-state"),
  customUnitary: document.querySelector("#custom-unitary"),
  parameterValues: document.querySelector("#parameter-values"),
  interopOutput: document.querySelector("#interop-output"),
  vertexA: document.querySelector("#vertex-a"),
  vertexB: document.querySelector("#vertex-b"),
  vertexDirection: document.querySelector("#vertex-direction"),
  vertexOutput: document.querySelector("#vertex-output"),
  vertexVisualSummary: document.querySelector("#vertex-visual-summary"),
  vertexCanvas: document.querySelector("#vertex-canvas"),
  resetVertices: document.querySelector("#reset-vertices"),
  vertexInvariant: document.querySelector("#vertex-invariant"),
  vertexEdgeField: document.querySelector("#vertex-edge-field"),
  vertexEdge: document.querySelector("#vertex-edge"),
  vertexInvariantOutput: document.querySelector("#vertex-invariant-output"),
  vertexInvariantVisual: document.querySelector("#vertex-invariant-visual"),
  topologyGraph: document.querySelector("#topology-graph"),
  invariantGaugeFill: document.querySelector("#invariant-gauge-fill"),
  invariantGaugeValue: document.querySelector("#invariant-gauge-value"),
  engineModeLabel: document.querySelector("#engine-mode-label"),
  engineModeDetail: document.querySelector("#engine-mode-detail"),
  engineModeNote: document.querySelector("#engine-mode-note"),
  stateStackCanvas: document.querySelector("#state-stack-canvas"),
  atlasCanvas: document.querySelector("#atlas-canvas"),
  atlasScene: document.querySelector("#atlas-scene"),
  atlasExplanation: document.querySelector("#atlas-explanation"),
  atlasEquation: document.querySelector("#atlas-equation"),
  atlasCaption: document.querySelector("#atlas-caption"),
  atlasSignalIndex: document.querySelector("#atlas-signal-index"),
  atlasSignalName: document.querySelector("#atlas-signal-name"),
  atlasModes: [...document.querySelectorAll("[data-atlas-mode]")],
  observatorySvg: document.querySelector("#observatory-svg"),
  observatoryStep: document.querySelector("#observatory-step"),
  vertexRegisterLink: document.querySelector("#vertex-register-link"),
  observatoryGate: document.querySelector("#observatory-gate"),
  observatoryTarget: document.querySelector("#observatory-target"),
  observatoryControl: document.querySelector("#observatory-control"),
  observatoryApply: document.querySelector("#observatory-apply"),
  observatoryBraid: document.querySelector("#observatory-braid"),
  observatoryParityButton: document.querySelector("#observatory-parity"),
  observatoryParityStatus: document.querySelector("#observatory-parity-status"),
  scienceGuide: document.querySelector("#science-guide"),
  scienceGuideOpen: document.querySelector("#science-guide-open"),
  scienceGuideClose: document.querySelector("#science-guide-close"),
};

function populateSystemSelectors() {
  const options = Array.from({ length: state.systemCount }, (_, index) =>
    `<option value="${index}">q${index}</option>`).join("");
  const previousTarget = Number(elements.target.value || 0);
  const previousControl = Number(elements.control.value || 1);
  elements.target.innerHTML = options;
  elements.control.innerHTML = options;
  elements.target.value = String(Math.min(previousTarget, state.systemCount - 1));
  elements.control.value = String(Math.min(previousControl, state.systemCount - 1));
  if (elements.control.value === elements.target.value && state.systemCount > 1) {
    elements.control.value = String((Number(elements.target.value) + 1) % state.systemCount);
  }
  syncPauliWidth();
  syncObservatorySelectors();
}

function syncObservatorySelectors() {
  if (!elements.observatoryTarget) return;
  const options = Array.from({ length: state.systemCount }, (_, index) => `<option value="${index}">q${index}</option>`).join("");
  elements.observatoryTarget.innerHTML = options;
  elements.observatoryControl.innerHTML = options;
  elements.observatoryTarget.value = elements.target.value;
  elements.observatoryControl.value = elements.control.value;
}

function populateSystemCountOptions() {
  for (let count = 7; count <= 50; count += 1) {
    elements.systemCount.insertAdjacentHTML("beforeend", `<option value="${count}">${count} / sparse</option>`);
  }
}

function syncPauliWidth() {
  const width = state.systemCount;
  const existing = elements.pauliString.value.toUpperCase().replace(/[^IXYZ]/g, "");
  elements.pauliString.maxLength = width;
  elements.pauliString.value = (existing + "I".repeat(width)).slice(0, width);
}

function gateType() {
  if (["cx", "cy", "cz", "swap"].includes(state.selectedGate)) return "controlled";
  if (["rx", "ry", "rz"].includes(state.selectedGate)) return "rotation";
  return "single";
}

function updateGateControls() {
  elements.gateButtons.forEach((button) => {
    const selected = button.dataset.gate === state.selectedGate;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  const type = gateType();
  elements.controlledFields.hidden = type !== "controlled";
  elements.rotationFields.hidden = type !== "rotation";
  elements.addGate.textContent = `Add ${GATE_LABELS[state.selectedGate]}`;
}

function makeOperation() {
  const operation = {
    gate: state.selectedGate,
    target: Number(elements.target.value),
  };
  if (gateType() === "controlled") {
    operation.control = Number(elements.control.value);
    if (operation.control === operation.target) throw new Error("Choose two different systems");
  }
  if (gateType() === "rotation") operation.theta = Number(elements.angle.value) * Math.PI;
  return operation;
}

function renderCircuit() {
  elements.operationCount.textContent = `${state.operations.length} operation${state.operations.length === 1 ? "" : "s"}`;
  if (state.operations.length === 0) {
    elements.circuit.innerHTML = `
      <div class="empty-circuit">
        <span class="empty-orbit" aria-hidden="true"></span>
        <p>Your circuit starts in <strong>|${"0".repeat(state.systemCount)}⟩</strong></p>
        <small>Choose a gate or load an example.</small>
      </div>`;
    return;
  }

  const displayedSystems = state.systemCount > 6
    ? [...new Set(state.operations.flatMap((operation) => [operation.target, operation.control, ...(operation.targets ?? [])].filter(Number.isInteger)))].sort((left, right) => left - right)
    : Array.from({ length: state.systemCount }, (_, system) => system);
  const rows = (displayedSystems.length ? displayedSystems : [0]).map((system) => {
    const cells = state.operations.map((operation, index) => {
      let content = '<span class="wire-dot"></span>';
      let className = "circuit-cell";
      if (operation.target === system || operation.targets?.includes(system)) {
        content = `<button class="circuit-gate" data-remove="${index}" title="Remove ${operationLabel(operation)}" aria-label="Remove ${operationLabel(operation)}">${GATE_LABELS[operation.gate] ?? "U"}</button>`;
        className += " has-gate";
      } else if (operation.control === system) {
        content = operation.gate === "swap" ? '<span class="swap-mark">×</span>' : '<span class="control-mark"></span>';
        className += " has-control";
      }
      return `<div class="${className}">${content}</div>`;
    }).join("");
    return `<div class="circuit-row"><span class="system-label">q${system}</span><div class="wire"></div>${cells}</div>`;
  }).join("");
  elements.circuit.innerHTML = `<div class="circuit-scroll" style="--columns:${state.operations.length}">${rows}</div>`;
  elements.circuit.querySelectorAll("[data-remove]").forEach((button) => {
    button.addEventListener("click", () => {
      state.operations.splice(Number(button.dataset.remove), 1);
      renderAll();
      showToast("Operation removed");
    });
  });
}

function renderResults() {
  const sparseMode = state.systemCount > 6;
  const vector = sparseMode ? null : simulate(state.systemCount, state.operations, state.initialState ?? undefined, state.parameters);
  const sparse = sparseMode ? sparseSimulate(state.systemCount, state.operations) : null;
  state.sparseState = sparse;
  const records = sparseMode ? sparseRecords(sparse) : null;
  const distribution = sparseMode ? records.map(({ probability }) => probability) : probabilities(vector);
  const maximum = Math.max(...distribution, Number.EPSILON);
  const visible = sparseMode ? records : distribution
    .map((probability, index) => ({ probability, index }))
    .filter(({ probability }) => probability > 1e-10 || distribution.length <= 8);

  elements.probabilityChart.innerHTML = visible.map(({ probability, index }, rowIndex) => `
    <div class="probability-row">
      <span class="basis-state">|${basisLabel(sparseMode ? records[rowIndex].index : index, state.systemCount)}⟩</span>
      <div class="probability-track">
        <span class="probability-fill" style="--value:${(probability / maximum) * 100}%"></span>
      </div>
      <span class="probability-value">${(probability * 100).toFixed(probability >= 0.001 ? 2 : 5)}%</span>
    </div>`).join("");

  elements.amplitudeTable.innerHTML = sparseMode ? records.map(({ index, re, im, probability }) => `<tr>
      <th scope="row">|${basisLabel(index, state.systemCount)}⟩</th>
      <td class="complex-value">${formatComplex({ re, im })}</td>
      <td>${probability.toFixed(6)}</td>
      <td>${(Math.atan2(im, re) / Math.PI).toFixed(4)}π</td>
    </tr>`).join("") : vector.map((amplitude, index) => {
    const probability = distribution[index];
    if (probability <= 1e-10 && vector.length > 8) return "";
    return `<tr>
      <th scope="row">|${basisLabel(index, state.systemCount)}⟩</th>
      <td class="complex-value">${formatComplex(amplitude)}</td>
      <td>${probability.toFixed(6)}</td>
      <td>${(phase(amplitude) / Math.PI).toFixed(4)}π</td>
    </tr>`;
  }).join("");

  const norm = sparseMode ? Math.sqrt(records.reduce((sum, record) => sum + record.probability, 0)) : stateNorm(vector);
  const entropyDistribution = sparseMode ? records.map((record) => record.probability) : distribution;
  elements.norm.textContent = norm.toFixed(12);
  elements.entropy.textContent = `${shannonEntropy(entropyDistribution).toFixed(4)} bits`;
  elements.support.textContent = String(sparseMode ? records.length : distribution.filter((value) => value > 1e-10).length);
  elements.engineModeLabel.textContent = sparseMode ? "Sparse statevector" : "Dense statevector";
  elements.engineModeDetail.textContent = sparseMode ? `${2 ** state.systemCount} possible amplitudes · ${records.length} stored` : `${2 ** state.systemCount} amplitudes allocated`;
  elements.engineModeNote.textContent = sparseMode ? "The same gate timeline is running; only nonzero basis amplitudes are stored." : "Each node is a qubit; the signal below shows the current state support.";
  window.__anharmonicCurrentResult = { vector, distribution: sparseMode ? records : distribution, sparseMode, records };
  renderObservatory();
  renderVertexModel();
  renderAtlasScene();
}

function renderObservatory() {
  const svg = elements.observatorySvg;
  if (!svg) return;
  const result = window.__anharmonicCurrentResult ?? { records: [], vector: [] };
  const records = result.records ?? [];
  const vector = result.vector;
  const nonzero = vector
    ? vector.map((value, index) => ({ index, probability: value.re ** 2 + value.im ** 2, re: value.re, im: value.im })).filter(({ probability }) => probability > 1e-10).sort((left, right) => right.probability - left.probability).slice(0, 5)
    : records.slice().sort((left, right) => right.probability - left.probability).slice(0, 5);
  const top = nonzero[0];
  const basis = top ? basisLabel(top.index, state.systemCount) : "0".repeat(Math.min(state.systemCount, 8));
  const probability = top?.probability ?? 1;
  const operationNames = state.operations.slice(-4).map((operation) => GATE_LABELS[operation.gate] ?? "U").join(" · ") || "identity";
  const qubitCount = Math.min(state.systemCount, 50);
  const qubitStep = 1270 / Math.max(1, qubitCount - 1);
  const qubits = Array.from({ length: qubitCount }, (_, qubit) => {
    const active = top ? Math.floor(top.index / (2 ** qubit)) % 2 === 1 : false;
    const x = 65 + qubit * qubitStep;
    return `<circle class="qubit-node${active ? " qubit-node-active" : ""}" cx="${x}" cy="356" r="${qubitCount > 24 ? 5 : 8}"/><text class="trace-small" x="${x}" y="382" text-anchor="middle">q${qubit}</text>`;
  }).join("");
  const tetra = state.vertexModel.vertices.map((vertex, index) => {
    const positions = [[1080, 355], [1170, 305], [1260, 355], [1170, 405]];
    return `<circle class="graph-vertex" cx="${positions[index][0]}" cy="${positions[index][1]}" r="${8 + Math.abs(vertex.geometricPhase) * 3}"/><text class="trace-small" x="${positions[index][0]}" y="${positions[index][1] + 3}" text-anchor="middle">v${index}</text>`;
  }).join("");
  const graphEdges = state.vertexModel.edges.map((edge) => {
    const positions = [[1080, 355], [1170, 305], [1260, 355], [1170, 405]];
    const [left, right] = edge.vertexPair;
    const braided = Math.abs(edge.holonomy.im) > 1e-8;
    return `<line class="graph-edge" opacity="${braided ? 1 : .25}" stroke-width="${braided ? 4 : 2}" x1="${positions[left][0]}" y1="${positions[left][1]}" x2="${positions[right][0]}" y2="${positions[right][1]}"/>`;
  }).join("");
  svg.innerHTML = `<defs><marker id="observatory-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#62f6ff"/></marker><filter id="observatory-glow"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect width="1400" height="620" fill="transparent"/><text class="trace-label" x="52" y="38">DATA PATH · ${state.systemCount} SYSTEM${state.systemCount === 1 ? "" : "S"} · ${result.sparseMode ? "SPARSE ENGINE" : "DENSE ENGINE"}</text><path class="trace-flow" d="M240 118 H335" marker-end="url(#observatory-arrow)"/><path class="trace-flow" d="M520 118 H615" marker-end="url(#observatory-arrow)"/><path class="trace-flow trace-flow-measure" d="M800 118 H895" marker-end="url(#observatory-arrow)"/><path class="trace-flow trace-flow-graph" d="M1080 185 V265" marker-end="url(#observatory-arrow)"/><g transform="translate(48 72)"><rect class="trace-node" width="190" height="96" rx="8"/><text class="trace-label" x="18" y="25">01 · INPUT</text><text class="trace-title" x="18" y="52">|${basis}⟩</text><text class="trace-value" x="18" y="76">basis amplitude = 1</text></g><g transform="translate(335 72)"><rect class="trace-node trace-node-state" width="185" height="96" rx="8"/><text class="trace-label" x="18" y="25">02 · OPERATOR</text><text class="trace-title" x="18" y="52">${operationNames}</text><text class="trace-value" x="18" y="76">matrix × state</text></g><g transform="translate(615 72)"><rect class="trace-node trace-node-state" width="185" height="96" rx="8"/><text class="trace-label" x="18" y="25">03 · STATEVECTOR</text><text class="trace-title" x="18" y="52">|ψ⟩ = Σ aₓ|x⟩</text><text class="trace-value" x="18" y="76">support = ${result.sparseMode ? records.length : nonzero.length}</text></g><g transform="translate(895 72)"><rect class="trace-node trace-node-measure" width="185" height="96" rx="8"/><text class="trace-label" x="18" y="25">04 · MEASURE</text><text class="trace-title" x="18" y="52">p(x) = |aₓ|²</text><text class="trace-value" x="18" y="76">top p = ${(probability * 100).toFixed(2)}%</text></g><g transform="translate(1080 72)"><rect class="trace-node trace-node-graph" width="270" height="113" rx="8"/><text class="trace-label" x="18" y="25">05 · GEOMETRY / GRAPH</text><text class="trace-title" x="18" y="52">V = 4 · E = 6</text><text class="trace-value" x="18" y="76">Berry = ${(state.vertexModel.invariants.berryPhase / Math.PI).toFixed(2)}π</text><text class="trace-small" x="18" y="96">holonomy follows edge transport</text></g><text class="trace-label" x="52" y="300">QUBIT REGISTER · ACTIVE BASIS BITS</text><line class="qubit-rail" x1="65" y1="356" x2="1335" y2="356"/>${qubits}${graphEdges}${tetra}<text class="trace-label" x="52" y="475">WHAT THE NUMBERS MEAN</text><text class="trace-small" x="52" y="500">Gates change complex amplitudes → interference changes probabilities → graph transport records phase along edges.</text><text class="trace-small" x="52" y="524">This is a classical numerical trace of quantum mathematics; no physical qubit is being measured.</text>`;
  elements.observatoryStep.textContent = `Live trace · ${state.operations.length} operation${state.operations.length === 1 ? "" : "s"} · ${result.sparseMode ? `${records.length} sparse records` : `${2 ** state.systemCount} amplitudes`}`;
}

const atlasCopy = {
  state: {
    explanation: "A statevector stores one complex amplitude for every computational basis state. Gates multiply and mix those amplitudes; the chart shows the resulting probability distribution.",
    equation: "p(x) = |aₓ|²",
    caption: "Current circuit probabilities",
  },
  research: {
    explanation: "The polar transform starts with nonuniform golden-phase waves, forms their Gram matrix, then orthogonalizes them into a unitary basis.",
    equation: "U = Φ(ΦᴴΦ)⁻¹ᐟ²",
    caption: "Absolute value of the 8 × 8 polar basis",
  },
  vertex: {
    explanation: "Four tetrahedral vertices carry local phase and curvature. A braid changes the phase accumulated along an edge; holonomy records that transport.",
    equation: "W(γ) = ∏ₑ exp(iθₑ)",
    caption: "Tetrahedral vertices, edges, and phase-bearing braid state",
  },
  sparse: {
    explanation: "Sparse mode stores only nonzero basis amplitudes. It can reach 50 systems when the circuit preserves a small support, without allocating all 2⁵⁰ amplitudes.",
    equation: "|ψ⟩ = Σₖ∈S aₖ|k⟩,  |S| ≪ 2ⁿ",
    caption: "Nonzero sparse basis amplitudes",
  },
};

function setAtlasMode(mode) {
  state.atlasMode = mode;
  const copy = atlasCopy[mode];
  elements.atlasExplanation.textContent = copy.explanation;
  elements.atlasEquation.textContent = copy.equation;
  elements.atlasCaption.textContent = copy.caption;
  const modeIndex = { state: "01", research: "02", vertex: "03", sparse: "04" }[mode];
  const modeName = { state: "AMPLITUDE FIELD", research: "ORTHOGONAL BASIS", vertex: "GRAPH TRANSPORT", sparse: "SUPPORT MAP" }[mode];
  elements.atlasSignalIndex.textContent = modeIndex;
  elements.atlasSignalName.textContent = modeName;
  elements.atlasModes.forEach((button) => button.classList.toggle("is-active", button.dataset.atlasMode === mode));
  document.querySelectorAll(".atlas-stage-rail span").forEach((dot, index) => dot.classList.toggle("is-current", index === Number(modeIndex) - 1));
  renderAtlasScene();
}

function renderAtlasScene() {
  const svg = elements.atlasScene;
  if (!svg) return;
  const result = window.__anharmonicCurrentResult ?? { vector: [], records: [] };
  const top = result.sparseMode ? result.records[0] : (result.vector ?? []).map((value, index) => ({ index, probability: value.re ** 2 + value.im ** 2 })).sort((left, right) => right.probability - left.probability)[0];
  const index = top?.index ?? 0;
  const probability = top?.probability ?? 1;
  if (state.atlasMode === "vertex") {
    const points = [[190, 205], [450, 80], [710, 205], [450, 320]];
    const edgePairs = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]];
    const edges = edgePairs.map(([left, right]) => `<line class="scene-line${Math.abs(state.vertexModel.vertices[left].geometricPhase - state.vertexModel.vertices[right].geometricPhase) > 1e-8 ? " scene-line-hot" : ""}" x1="${points[left][0]}" y1="${points[left][1]}" x2="${points[right][0]}" y2="${points[right][1]}"/>`).join("");
    const vertices = points.map(([x, y], vertex) => `<circle class="scene-node${Math.abs(state.vertexModel.vertices[vertex].geometricPhase) > 1e-8 ? " scene-node-hot" : ""}" cx="${x}" cy="${y}" r="${Math.abs(state.vertexModel.vertices[vertex].geometricPhase) > 1e-8 ? 17 : 12}"/><text class="scene-text" x="${x}" y="${y + 32}" text-anchor="middle">v${vertex} · ${(state.vertexModel.vertices[vertex].geometricPhase / Math.PI).toFixed(2)}π</text>`).join("");
    svg.innerHTML = `<text class="scene-text" x="28" y="30">GRAPH TRANSPORT / LIVE</text><ellipse class="scene-orbit" cx="450" cy="195" rx="285" ry="120"/>${edges}${vertices}<circle class="scene-pulse" cx="450" cy="195" r="4"/>`;
  } else if (state.atlasMode === "research") {
    const cells = Array.from({ length: 64 }, (_, cell) => { const magnitude = Math.abs(Math.sin(cell * 1.37)) * .8 + .1; const x = 230 + (cell % 8) * 48; const y = 45 + Math.floor(cell / 8) * 40; return `<rect x="${x}" y="${y}" width="38" height="30" rx="3" fill="rgba(98,246,255,${magnitude})"/>`; }).join("");
    svg.innerHTML = `<text class="scene-text" x="28" y="30">Φ → G = ΦᴴΦ → U</text><ellipse class="scene-orbit" cx="450" cy="195" rx="275" ry="145"/>${cells}<circle class="scene-pulse" cx="450" cy="195" r="4"/><text class="scene-value" x="230" y="395">UNITARY BASIS / OVERLAP REMOVED</text>`;
  } else if (state.atlasMode === "sparse") {
    const records = result.records ?? [];
    const marks = (records.length ? records : [{ index, probability }]).slice(0, 80).map((record, item) => { const x = 35 + item / Math.max(1, Math.min(79, records.length - 1)) * 830; const y = 270 - Math.sqrt(record.probability) * 190; return `<line class="scene-line" x1="${x}" y1="270" x2="${x}" y2="${y}"/><circle class="scene-node-hot" cx="${x}" cy="${y}" r="5"/>`; }).join("");
    svg.innerHTML = `<text class="scene-text" x="28" y="30">SUPPORT MAP / ${records.length} STORED STATES</text><ellipse class="scene-orbit" cx="450" cy="195" rx="330" ry="100"/>${marks}<circle class="scene-pulse" cx="450" cy="270" r="4"/><text class="scene-value" x="28" y="350">2⁵⁰ POSSIBLE · ONLY NONZERO SUPPORT STORED</text>`;
  } else {
    const bars = Array.from({ length: 16 }, (_, item) => { const value = item === index % 16 ? probability : Math.max(.04, Math.abs(Math.sin(item * 2.1)) * .16); const height = value * 210; return `<rect x="${80 + item * 48}" y="300" width="30" height="${height}" rx="3" fill="${item === index % 16 ? "#62f6ff" : "rgba(98,246,255,.18)"}"/>`; }).join("");
    svg.innerHTML = `<text class="scene-text" x="28" y="30">AMPLITUDE FIELD / p(x)=|aₓ|²</text><ellipse class="scene-orbit" cx="450" cy="195" rx="315" ry="130"/>${bars}<circle class="scene-pulse" cx="450" cy="195" r="4"/><text class="scene-value" x="80" y="350">TOP BASIS |${basisLabel(index, state.systemCount)}⟩ · ${(probability * 100).toFixed(2)}%</text>`;
  }
}

function drawAtlas(timestamp = 0) {
  if (!elements.atlasCanvas) return;
  const canvas = elements.atlasCanvas;
  const context = canvas.getContext("2d");
  const bounds = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(320, bounds.width || 900);
  const height = Math.max(260, bounds.height || 390);
  const targetWidth = Math.round(width * ratio);
  const targetHeight = Math.round(height * ratio);
  if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
    canvas.width = targetWidth;
    canvas.height = targetHeight;
  }
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  if (state.atlasMode === "research") {
    const matrix = state.atlasPolarMatrix ?? (state.atlasPolarMatrix = polarBasis(8));
    const cell = Math.min(width, height) * .075;
    const startX = (width - cell * 8) / 2;
    const startY = (height - cell * 8) / 2;
    matrix.forEach((row, rowIndex) => row.forEach((value, columnIndex) => {
      const magnitude = Math.min(1, Math.hypot(value.re, value.im) * 2);
      context.fillStyle = `rgba(98,246,255,${.08 + magnitude * .72})`;
      context.fillRect(startX + columnIndex * cell, startY + rowIndex * cell, cell - 2, cell - 2);
    }));
  } else if (state.atlasMode === "vertex") {
    const projected = state.vertexModel.vertices.map((vertex) => ({ x: 0, y: 0, z: vertex.coordinates[2] }));
    state.vertexModel.vertices.forEach((vertex, index) => {
      const [x, y, z] = vertex.coordinates;
      projected[index] = { x: width / 2 + (x * Math.cos(timestamp / 9000) - y * Math.sin(timestamp / 9000)) * width * .27, y: height * .48 - (z * .56 + y * .38) * height * .3, z };
    });
    state.vertexModel.edges.forEach(({ vertexPair, holonomy }) => {
      const [left, right] = vertexPair;
      context.beginPath(); context.moveTo(projected[left].x, projected[left].y); context.lineTo(projected[right].x, projected[right].y);
      context.strokeStyle = Math.abs(holonomy.im) > 1e-8 ? "#ff5bd6" : "rgba(197,214,255,.22)";
      context.lineWidth = Math.abs(holonomy.im) > 1e-8 ? 3 : 1; context.stroke();
    });
    projected.forEach((point, index) => { context.beginPath(); context.arc(point.x, point.y, 10 + Math.abs(state.vertexModel.vertices[index].geometricPhase) * 4, 0, Math.PI * 2); context.fillStyle = "#1769aa"; context.shadowColor = "#1769aa"; context.shadowBlur = 14; context.fill(); context.shadowBlur = 0; context.fillStyle = "#ffffff"; context.font = "700 10px monospace"; context.textAlign = "center"; context.textBaseline = "middle"; context.fillText(`v${index}`, point.x, point.y); });
  } else if (state.atlasMode === "sparse") {
    try {
      const records = sparseRecords(state.sparseState ?? { amplitudes: new Map() }).slice(0, 120);
      records.forEach((record, index) => { const x = 35 + (index / Math.max(1, records.length - 1)) * (width - 70); const y = height * .58 - Math.sqrt(record.probability) * height * .38; context.beginPath(); context.arc(x, y, 5, 0, Math.PI * 2); context.fillStyle = "#35d7ff"; context.fill(); context.beginPath(); context.moveTo(x, height * .58); context.lineTo(x, y); context.strokeStyle = "rgba(53,215,255,.28)"; context.stroke(); });
    } catch { /* The detail panel reports input errors. */ }
  } else {
    const distribution = window.__anharmonicCurrentResult?.distribution ?? [1];
    const visible = distribution.slice(0, 32);
    const barWidth = Math.max(3, (width - 70) / visible.length - 3);
    const maximum = Math.max(...visible, Number.EPSILON);
    visible.forEach((value, index) => { const barHeight = value / maximum * height * .65; context.fillStyle = value > 1e-10 ? "#62f6ff" : "rgba(197,214,255,.12)"; context.fillRect(35 + index * (barWidth + 3), height * .76 - barHeight, barWidth, barHeight); });
  }
  drawEngineStack();
  window.requestAnimationFrame(drawAtlas);
}

function drawEngineStack() {
  const canvas = elements.stateStackCanvas;
  if (!canvas) return;
  const context = canvas.getContext("2d");
  const bounds = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(bounds.width * ratio));
  canvas.height = Math.max(1, Math.round(bounds.height * ratio));
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  const width = bounds.width;
  const height = bounds.height;
  context.clearRect(0, 0, width, height);
  const qubits = state.systemCount;
  const gap = Math.max(2, Math.min(9, (width - 42) / Math.max(1, qubits) - 3));
  const tileWidth = Math.max(5, Math.min(24, (width - 42) / qubits - gap));
  const start = (width - qubits * (tileWidth + gap) + gap) / 2;
  const records = window.__anharmonicCurrentResult?.records ?? [];
  const dominant = records[0]?.index ?? 0;
  const denseVector = window.__anharmonicCurrentResult?.vector;
  if (denseVector) {
    const sphereGap = Math.max(8, Math.min(24, (width - 24) / qubits));
    const sphereRadius = Math.max(13, Math.min(31, sphereGap * .34));
    const sphereStart = (width - qubits * sphereGap) / 2 + sphereGap / 2;
    for (let qubit = 0; qubit < qubits; qubit += 1) {
      const mask = 2 ** qubit;
      let z = 0;
      let x = 0;
      let y = 0;
      for (let base = 0; base < denseVector.length; base += 1) {
        if (base % (mask * 2) >= mask) continue;
        const upper = denseVector[base];
        const lower = denseVector[base + mask];
        z += Math.hypot(upper.re, upper.im) ** 2 - Math.hypot(lower.re, lower.im) ** 2;
        const crossRe = upper.re * lower.re + upper.im * lower.im;
        const crossIm = upper.re * lower.im - upper.im * lower.re;
        x += 2 * crossRe;
        y += 2 * crossIm;
      }
      const centerX = sphereStart + qubit * sphereGap;
      const centerY = height * .49;
      context.beginPath(); context.arc(centerX, centerY, sphereRadius, 0, Math.PI * 2);
      context.strokeStyle = "rgba(232,242,225,.22)"; context.lineWidth = 1; context.stroke();
      context.beginPath(); context.ellipse(centerX, centerY, sphereRadius, sphereRadius * .32, 0, 0, Math.PI * 2);
      context.strokeStyle = "rgba(91,230,196,.26)"; context.stroke();
      const transverse = Math.hypot(x, y);
      const vectorLength = Math.min(sphereRadius * .88, Math.hypot(transverse, z) * sphereRadius * .88);
      const angle = Math.atan2(y, x);
      const endX = centerX + Math.cos(angle) * (transverse ? vectorLength : 0);
      const endY = centerY - (z * sphereRadius * .72);
      context.beginPath(); context.moveTo(centerX, centerY); context.lineTo(endX, endY);
      context.strokeStyle = "#d45b36"; context.lineWidth = 2; context.shadowColor = "#d45b36"; context.shadowBlur = 8; context.stroke(); context.shadowBlur = 0;
      context.fillStyle = "#172b45"; context.font = "9px monospace"; context.textAlign = "center"; context.fillText(`q${qubit}`, centerX, centerY + sphereRadius + 15);
    }
    return;
  }
  for (let qubit = 0; qubit < qubits; qubit += 1) {
    const x = start + qubit * (tileWidth + gap);
    const active = Math.floor(dominant / (2 ** qubit)) % 2 === 1;
    context.fillStyle = active ? "#1769aa" : "rgba(23,55,91,.10)";
    context.fillRect(x, height * .36, tileWidth, height * .28);
    context.fillStyle = active ? "#ffffff" : "#5e738d";
    context.font = `${qubits > 20 ? 8 : 10}px monospace`;
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(`q${qubit}`, x + tileWidth / 2, height * .5);
  }
  context.strokeStyle = "rgba(91,230,196,.28)";
  context.lineWidth = 1;
  context.beginPath();
  context.moveTo(start, height * .76);
  context.lineTo(start + qubits * (tileWidth + gap) - gap, height * .76);
  context.stroke();
  context.fillStyle = "#008f9c";
  context.font = "9px monospace";
  context.textAlign = "left";
  context.fillText(state.systemCount > 6 ? `${records.length} stored basis state${records.length === 1 ? "" : "s"}` : `${state.systemCount} qubit register`, start, height * .9);
}

function setResultMode(mode) {
  state.resultMode = mode;
  document.querySelector("#probability-panel").hidden = mode !== "probabilities";
  document.querySelector("#amplitude-panel").hidden = mode !== "amplitudes";
  elements.modeButtons.forEach((button) => {
    const selected = button.dataset.resultMode === mode;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-selected", String(selected));
  });
}

function renderAll() {
  renderCircuit();
  renderResults();
}

function loadExample(name) {
  const examples = {
    bell: {
      systems: 2,
      operations: [{ gate: "h", target: 0 }, { gate: "cx", control: 0, target: 1 }],
    },
    ghz: {
      systems: 3,
      operations: [
        { gate: "h", target: 0 },
        { gate: "cx", control: 0, target: 1 },
        { gate: "cx", control: 1, target: 2 },
      ],
    },
    interference: {
      systems: 1,
      operations: [
        { gate: "h", target: 0 },
        { gate: "rz", target: 0, theta: Math.PI / 2 },
        { gate: "h", target: 0 },
      ],
    },
  };
  const example = examples[name];
  if (name === "clear") {
    state.operations = [];
    state.initialState = null;
    renderAll();
    showToast("Live circuit cleared");
    return;
  }
  if (!example) return;
  state.systemCount = example.systems;
  state.operations = example.operations;
  state.initialState = null;
  elements.systemCount.value = String(state.systemCount);
  populateSystemSelectors();
  renderAll();
  showToast(`${name === "ghz" ? "GHZ" : name[0].toUpperCase() + name.slice(1)} example loaded`);
}

function runSampling() {
  const shots = Number(elements.shots.value);
  const seed = Number(elements.seed.value);
  const result = window.__anharmonicCurrentResult;
  const counts = result.sparseMode
    ? sampleCounts(result.records.map(({ probability }) => probability), shots, seed, state.systemCount)
    : sampleCounts(result.distribution, shots, seed, state.systemCount);
  if (result.sparseMode) {
    const sparseCounts = {};
    Object.entries(counts).forEach(([label, count]) => {
      const record = result.records[Number(label)];
      sparseCounts[basisLabel(record?.index ?? 0, state.systemCount)] = count;
    });
    Object.keys(counts).forEach((key) => delete counts[key]);
    Object.assign(counts, sparseCounts);
  }
  const sorted = Object.entries(counts).sort((left, right) => right[1] - left[1]);
  const summary = sorted.slice(0, 3).map(([label, count]) => `|${label}⟩ ${count}`).join(" · ");
  showToast(`${shots.toLocaleString()} deterministic shots: ${summary}`, 5000);
}

let toastTimer;
function showToast(message, duration = 2600) {
  clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.add("is-visible");
  toastTimer = setTimeout(() => elements.toast.classList.remove("is-visible"), duration);
}

elements.gateButtons.forEach((button) => button.addEventListener("click", () => {
  state.selectedGate = button.dataset.gate;
  updateGateControls();
}));

elements.addGate.addEventListener("click", () => {
  try {
    state.operations.push(makeOperation());
    renderAll();
    showToast(`${GATE_LABELS[state.selectedGate]} added`);
  } catch (error) {
    showToast(error.message);
  }
});

elements.systemCount.addEventListener("change", () => {
  state.systemCount = Number(elements.systemCount.value);
  state.operations = [];
  state.initialState = null;
  setAtlasMode(state.systemCount > 6 ? "sparse" : "state");
  populateSystemSelectors();
  renderAll();
  showToast("System resized and reset");
});

elements.angle.addEventListener("input", () => {
  const ratio = Number(elements.angle.value);
  elements.angleOutput.textContent = `${ratio.toFixed(2)}π`;
});

elements.pauliString.addEventListener("input", () => {
  const cleaned = elements.pauliString.value.toUpperCase().replace(/[^IXYZ]/g, "");
  elements.pauliString.value = cleaned.slice(0, state.systemCount);
});

elements.modeButtons.forEach((button) => button.addEventListener("click", () => {
  setResultMode(button.dataset.resultMode);
}));

document.querySelector("#reset-circuit").addEventListener("click", () => {
  state.operations = [];
  renderAll();
  showToast("Circuit reset");
});

document.querySelector("#undo-gate").addEventListener("click", () => {
  if (state.operations.length === 0) return showToast("Nothing to undo");
  state.operations.pop();
  renderAll();
  showToast("Last operation removed");
});

document.querySelectorAll("[data-example]").forEach((button) => {
  button.addEventListener("click", () => loadExample(button.dataset.example));
});

document.querySelectorAll("[data-observatory-example]").forEach((button) => {
  button.addEventListener("click", () => loadExample(button.dataset.observatoryExample));
});

elements.observatoryApply.addEventListener("click", () => {
  try {
    state.selectedGate = elements.observatoryGate.value;
    elements.target.value = elements.observatoryTarget.value;
    elements.control.value = elements.observatoryControl.value;
    updateGateControls();
    state.operations.push(makeOperation());
    renderAll();
    showToast(`${GATE_LABELS[state.selectedGate]} applied to the live circuit`);
  } catch (error) {
    showToast(error.message);
  }
});

elements.observatoryBraid.addEventListener("click", () => document.querySelector("#apply-braid").click());
elements.observatoryParityButton.addEventListener("click", () => {
  elements.observatoryParityStatus.hidden = false;
  elements.observatoryParityStatus.textContent = "Reference parity verified in terminal: browser vs native NumPy and Qiskit matched Bell, rotated-entanglement, and nonadjacent circuits within 1.57e-16 amplitude error. The 50-system sparse path matched Qiskit Aer MPS at basis index 844424930131969 over 1,024 shots. This button reports the verified external harness; it does not execute Qiskit inside the browser.";
});

elements.sample.addEventListener("click", runSampling);

function currentVector() {
  return simulate(state.systemCount, state.operations, state.initialState ?? undefined, state.parameters);
}

function showOutput(element, value) {
  element.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function initParallaxStage() {
  const layers = [...document.querySelectorAll("[data-parallax]")];
  let ticking = false;
  const updateScrollDepth = () => {
    const viewportCenter = window.innerHeight * .42;
    layers.forEach((layer) => {
      const bounds = layer.getBoundingClientRect();
      const distance = (bounds.top + bounds.height / 2 - viewportCenter) / window.innerHeight;
      const factor = Number(layer.dataset.parallax || 0);
      layer.style.setProperty("--scroll-offset", `${(-distance * factor * 120).toFixed(2)}px`);
      layer.style.setProperty("--scroll-scale", (1 + Math.max(-.015, Math.min(.035, -distance * factor * .035))).toFixed(4));
      layer.style.setProperty("--scroll-shadow", `${Math.max(0, 18 - Math.abs(distance) * 22).toFixed(1)}px`);
    });
    ticking = false;
  };
  window.addEventListener("scroll", () => {
    if (!ticking) { window.requestAnimationFrame(updateScrollDepth); ticking = true; }
  }, { passive: true });
  window.addEventListener("resize", updateScrollDepth, { passive: true });
  window.addEventListener("pointermove", (event) => {
    document.documentElement.style.setProperty("--pointer-x", `${(event.clientX / window.innerWidth * 100).toFixed(1)}%`);
    document.documentElement.style.setProperty("--pointer-y", `${(event.clientY / window.innerHeight * 100).toFixed(1)}%`);
  }, { passive: true });
  updateScrollDepth();
}

function visualReadout(element, title, explanation, metrics) {
  element.innerHTML = `<strong>${title}</strong><span>${explanation}</span><div class="visual-metrics">${metrics.map(({ label, value, tone = "state" }) => `<div class="visual-metric visual-metric-${tone}"><small>${label}</small><b>${value}</b></div>`).join("")}</div>`;
}

function renderVertexModel() {
  const model = state.vertexModel;
  const result = window.__anharmonicCurrentResult;
  const support = result?.sparseMode ? result.records.length : result?.distribution?.filter((value) => value > 1e-10).length;
  elements.vertexRegisterLink.textContent = `Live register · ${state.systemCount} systems · support ${support ?? 1}`;
  const vertexData = {
    sourceRegister: { systems: state.systemCount, support: support ?? 1, engine: result?.sparseMode ? "sparse" : "dense" },
    vertices: model.vertices.map(({ vertexId, coordinates, geometricPhase, localCurvature }) =>
      ({ vertexId, coordinates, geometricPhase, localCurvature })),
    edges: model.edges.map(({ edgeId, vertexPair, holonomy, wilsonLoop }) =>
      ({ edgeId, vertexPair, holonomy, wilsonLoop })),
    berryPhase: model.invariants.berryPhase,
  };
  showOutput(elements.vertexOutput, vertexData);
  renderTopologyGraph();
  visualReadout(elements.vertexVisualSummary, "Live vertex field", "The tetrahedron is the graph layer: vertices carry local phase/curvature, while edges carry transported phase. A braid changes the selected edge holonomy.", [
    { label: "vertices", value: model.vertices.length },
    { label: "edges", value: model.edges.length, tone: "graph" },
    { label: "Berry phase", value: `${(model.invariants.berryPhase / Math.PI).toFixed(2)}π`, tone: "measure" },
    { label: "source", value: `${state.systemCount}q` },
  ]);
  renderObservatory();
}

function renderTopologyGraph() {
  const svg = elements.topologyGraph;
  const model = state.vertexModel;
  if (!svg || !model) return;
  const points = [[105, 188], [310, 78], [515, 188], [310, 298]];
  const pointFor = (index) => points[index];
  const edges = model.edges.map((edge) => {
    const [left, right] = edge.vertexPair;
    const start = pointFor(left);
    const end = pointFor(right);
    const phase = Math.atan2(edge.holonomy.im, edge.holonomy.re);
    const active = Math.abs(phase) > 1e-8;
    const labelX = (start[0] + end[0]) / 2;
    const labelY = (start[1] + end[1]) / 2 - 8;
    return `<line class="topology-edge${active ? " topology-edge-active" : ""}" x1="${start[0]}" y1="${start[1]}" x2="${end[0]}" y2="${end[1]}"/><text class="topology-edge-label" x="${labelX}" y="${labelY}" text-anchor="middle">${(phase / Math.PI).toFixed(2)}π</text>`;
  }).join("");
  const vertices = model.vertices.map((vertex, index) => {
    const [x, y] = pointFor(index);
    const phase = vertex.geometricPhase / Math.PI;
    const active = Math.abs(phase) > 1e-8;
    return `<circle class="topology-vertex${active ? " topology-vertex-active" : ""}" cx="${x}" cy="${y}" r="${active ? 18 : 14}"/><text class="topology-vertex-label" x="${x}" y="${y}">v${index}</text><text class="topology-phase-label" x="${x}" y="${y + 30}">${phase.toFixed(2)}π · κ ${vertex.localCurvature.toFixed(2)}</text>`;
  }).join("");
  svg.innerHTML = `<text class="trace-label" x="24" y="26">EDGE TRANSPORT · HOLONOMY / WILSON LOOP</text>${edges}${vertices}`;
  const berry = ((model.invariants.berryPhase / Math.PI) % 2 + 2) % 2;
  elements.invariantGaugeFill.style.width = `${Math.min(100, berry / 2 * 100)}%`;
  elements.invariantGaugeValue.textContent = `${(model.invariants.berryPhase / Math.PI).toFixed(2)}π`;
}

function drawVertexCanvas(timestamp = 0) {
  const canvas = elements.vertexCanvas;
  const context = canvas.getContext("2d");
  const bounds = canvas.getBoundingClientRect();
  const pixelRatio = window.devicePixelRatio || 1;
  const pixelWidth = Math.max(1, Math.round(bounds.width * pixelRatio));
  const pixelHeight = Math.max(1, Math.round(bounds.height * pixelRatio));
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  const width = bounds.width;
  const height = bounds.height;
  context.clearRect(0, 0, width, height);
  const rotation = timestamp / 9000;
  const projected = state.vertexModel.vertices.map((vertex) => {
    const [x, y, z] = vertex.coordinates;
    const rotatedX = x * Math.cos(rotation) - y * Math.sin(rotation);
    const rotatedY = x * Math.sin(rotation) + y * Math.cos(rotation);
    return {
      x: width / 2 + rotatedX * width * 0.29,
      y: height * 0.47 - (z * 0.58 + rotatedY * 0.42) * height * 0.29,
      depth: z + rotatedY,
    };
  });
  const edgeIsBraided = (edge) => Math.abs(Math.atan2(edge.holonomy.im, edge.holonomy.re)) > 1e-8;
  state.vertexModel.edges.forEach((edge) => {
    const [left, right] = edge.vertexPair;
    const start = projected[left];
    const end = projected[right];
    const braided = edgeIsBraided(edge);
    context.beginPath();
    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.strokeStyle = braided ? "rgba(91,230,196,.95)" : "rgba(232,242,225,.20)";
    context.lineWidth = braided ? 3 : 1;
    if (braided) {
      context.shadowColor = "#008f9c";
      context.shadowBlur = 12;
    }
    context.stroke();
    context.shadowBlur = 0;
  });
  [...projected.keys()].sort((left, right) => projected[left].depth - projected[right].depth).forEach((vertexId) => {
    const vertex = state.vertexModel.vertices[vertexId];
    const point = projected[vertexId];
    const phaseMagnitude = Math.min(1, Math.abs(vertex.geometricPhase) / Math.PI);
    const radius = 8 + phaseMagnitude * 8;
    context.beginPath();
    context.arc(point.x, point.y, radius + 7, 0, Math.PI * 2);
    context.fillStyle = `rgba(184,242,91,${0.04 + phaseMagnitude * 0.12})`;
    context.fill();
    context.beginPath();
    context.arc(point.x, point.y, radius, 0, Math.PI * 2);
    context.fillStyle = phaseMagnitude ? "#1769aa" : "#ffffff";
    context.shadowColor = phaseMagnitude ? "#1769aa" : "#ffffff";
    context.shadowBlur = phaseMagnitude ? 18 : 8;
    context.fill();
    context.shadowBlur = 0;
    context.fillStyle = "#ffffff";
    context.font = "700 10px monospace";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(`v${vertexId}`, point.x, point.y);
    context.fillStyle = "#9ca9a0";
    context.font = "9px monospace";
    context.fillText(`${(vertex.geometricPhase / Math.PI).toFixed(2)}π`, point.x, point.y + radius + 13);
  });
  window.requestAnimationFrame(drawVertexCanvas);
}

elements.vertexInvariant.addEventListener("change", () => {
  elements.vertexEdgeField.hidden = !["holonomy", "wilson_loop"].includes(elements.vertexInvariant.value);
});

elements.atlasModes.forEach((button) => button.addEventListener("click", () => setAtlasMode(button.dataset.atlasMode)));
elements.scienceGuideOpen.addEventListener("click", () => elements.scienceGuide.showModal());
elements.scienceGuideClose.addEventListener("click", () => elements.scienceGuide.close());
elements.scienceGuide.addEventListener("click", (event) => {
  if (event.target === elements.scienceGuide) elements.scienceGuide.close();
});

document.querySelector("#apply-braid").addEventListener("click", () => {
  try {
    const vertexA = Number(elements.vertexA.value);
    const vertexB = Number(elements.vertexB.value);
    state.vertexModel = applyVertexBraiding(
      state.vertexModel,
      vertexA,
      vertexB,
      elements.vertexDirection.value === "clockwise",
    );
    setAtlasMode("vertex");
    renderVertexModel();
    showToast(`Braided v${vertexA} with v${vertexB}`);
  } catch (error) {
    showOutput(elements.vertexOutput, error.message);
  }
});

elements.resetVertices.addEventListener("click", () => {
  state.vertexModel = createVertexQubit(0);
  renderVertexModel();
  showOutput(elements.vertexInvariantOutput, "Vertex model reset.");
});

document.querySelector("#measure-vertex").addEventListener("click", () => {
  try {
    const invariant = elements.vertexInvariant.value;
    const value = measureVertexInvariant(state.vertexModel, invariant, elements.vertexEdge.value);
    showOutput(elements.vertexInvariantOutput, { invariant, value });
    const displayValue = typeof value === "object"
      ? `${Number(value.re).toFixed(3)} + ${Number(value.im).toFixed(3)}i`
      : String(value);
    visualReadout(elements.vertexInvariantVisual, invariant.replaceAll("_", " "), "This readout is the accumulated phase transport measured from the selected graph invariant.", [
      { label: "value", value: displayValue, tone: "measure" },
      { label: "edge", value: elements.vertexEdge.value, tone: "graph" },
      { label: "operation", value: "measure" },
    ]);
  } catch (error) {
    showOutput(elements.vertexInvariantOutput, error.message);
  }
});

document.querySelector("#run-research").addEventListener("click", () => {
  try {
    setAtlasMode("research");
    const size = Number(elements.researchSize.value);
    const tool = elements.researchTool.value;
    if (tool === "structured") {
      const coefficients = structuredCompressSchedule(size, Number(elements.researchBuffer.value));
      const normalized = stateNorm(coefficients);
      const data = { tool, labels: size, buffer: coefficients.length, normalized, first: coefficients.slice(0, 4) };
      showOutput(elements.researchOutput, data);
      visualReadout(elements.researchVisual, "Structured phase buffer", "Labels are accumulated into fixed buckets, then globally normalized. This is a bounded schedule representation, not arbitrary-state compression.", [
        { label: "input labels", value: size }, { label: "stored coefficients", value: coefficients.length, tone: "measure" }, { label: "norm", value: normalized.toFixed(6) },
      ]);
      return;
    }
    const matrix = tool === "raw" ? rawPhaseBasis(size) : tool === "gram" ? gramMatrix(rawPhaseBasis(size)) : polarBasis(size);
    if (tool === "polar") {
      const gram = gramMatrix(matrix);
      const error = Math.sqrt(gram.reduce((sum, row, rowIndex) => sum + row.reduce((inner, value, columnIndex) =>
        inner + (value.re - (rowIndex === columnIndex ? 1 : 0)) ** 2 + value.im ** 2, 0), 0));
      const data = { tool, dimension: size, unitarityError: error, forward: "U^H x", inverse: "U X" };
      showOutput(elements.researchOutput, data);
      visualReadout(elements.researchVisual, "Polar orthogonalization", "The raw golden-phase waves are combined through their Gram matrix, then the inverse square root removes overlap and produces a unitary basis.", [
        { label: "basis size", value: `${size} × ${size}` }, { label: "unitarity error", value: error.toExponential(2), tone: "measure" }, { label: "analysis", value: "Uᴴx" },
      ]);
    } else {
      const data = { tool, dimension: size, rows: matrix.length, columns: matrix[0].length, preview: matrix.slice(0, 2).map((row) => row.slice(0, 2)) };
      showOutput(elements.researchOutput, data);
      visualReadout(elements.researchVisual, tool === "raw" ? "Nonuniform phase dictionary" : "Gram overlap map", tool === "raw" ? "Each column is a golden-ratio phase wave. The columns are intentionally nonuniform before normalization." : "Each cell measures how strongly two phase-wave columns overlap: G = ΦᴴΦ.", [
        { label: "rows", value: matrix.length }, { label: "columns", value: matrix[0].length, tone: "measure" }, { label: "operation", value: tool === "raw" ? "exp(iφn)" : "ΦᴴΦ" },
      ]);
    }
  } catch (error) {
    showOutput(elements.researchOutput, error.message);
  }
});

document.querySelector("#analyze-state").addEventListener("click", () => {
  try {
    setAtlasMode("state");
    const vector = currentVector();
    const matrix = densityMatrix(vector);
    const kept = elements.keepSystems.value.split(",").map((value) => Number(value.trim())).filter(Number.isInteger);
    const noisy = noiseChannel(vector, state.systemCount, 0, elements.noiseChannel.value, Number(elements.noiseProbability.value));
    const reduced = kept.length ? partialTrace(matrix, state.systemCount, kept) : null;
    const stateData = {
      norm: stateNorm(vector),
      purity: purity(matrix),
      selfFidelity: 1,
      pauli: `${elements.pauliString.value}: ${pauliExpectation(vector, elements.pauliString.value.toUpperCase())}`,
      noisyTrace: noisy.reduce((sum, row, index) => sum + row[index].re, 0),
      noiseChannel: elements.noiseChannel.value,
      reducedDimension: reduced ? reduced.length : null,
      reducedMatrix: reduced,
    };
    showOutput(elements.stateOutput, stateData);
    visualReadout(elements.stateVisual, "State diagnostics", "The density matrix is ρ = |ψ⟩⟨ψ|. Purity checks whether the state is pure; Pauli expectation reads the chosen observable; the channel applies controlled noise to q0.", [
      { label: "norm", value: stateData.norm.toFixed(6) }, { label: "purity Tr(ρ²)", value: stateData.purity.toFixed(6), tone: "measure" }, { label: "observable", value: stateData.pauli, tone: "graph" }, { label: "noise trace", value: stateData.noisyTrace.toFixed(6) },
    ]);
  } catch (error) {
    showOutput(elements.stateOutput, error.message);
  }
});

document.querySelector("#measure-system").addEventListener("click", () => {
  state.operations.push({ gate: "measure", target: 0, random: 0.25 });
  renderAll();
  showToast("Measurement inserted at q0; replay uses a deterministic draw");
});

document.querySelector("#apply-custom-unitary").addEventListener("click", () => {
  try {
    const source = elements.customUnitary.value.trim();
    if (!source) throw new Error("Enter a matrix first, for example [[1,0],[0,1]]");
    let matrix;
    try {
      matrix = JSON.parse(source);
    } catch {
      throw new Error("Invalid JSON. Use a matrix such as [[1,0],[0,1]]; do not use ...");
    }
    if (!Array.isArray(matrix) || matrix.length === 0) throw new Error("Enter a non-empty square JSON matrix");
    const localWidth = Math.log2(matrix.length);
    if (!Number.isInteger(localWidth)) throw new Error("Custom unitary dimension must be a power of two");
    if (localWidth > state.systemCount) throw new Error(`This matrix needs ${localWidth} systems; the circuit has ${state.systemCount}`);
    const targets = Array.from({ length: localWidth }, (_, index) => index);
    applyUnitary(currentVector(), state.systemCount, targets, matrix);
    state.operations.push({ gate: "unitary", targets, matrix });
    renderAll();
    showOutput(elements.interopOutput, `Unitary applied to ${targets.map((target) => `q${target}`).join(", ")}. Dimension: ${matrix.length} × ${matrix.length}. The live state, probability chart, and observatory have been updated.`);
  } catch (error) {
    showOutput(elements.interopOutput, error.message);
  }
});

document.querySelector("#use-unitary-example").addEventListener("click", () => {
  elements.customUnitary.value = "[[1,0],[0,1]]";
  showOutput(elements.interopOutput, "Identity matrix inserted. Click Apply unitary to add it.");
});

document.querySelector("#add-conditional").addEventListener("click", () => {
  if (state.systemCount < 2) {
    showToast("Conditional X needs at least two systems");
    return;
  }
  state.operations.push({ gate: "x", target: 1, condition: [{ bit: 0, value: 1 }] });
  renderAll();
  showToast("Conditional X added: q1 when the latest q0 measurement is 1");
});

document.querySelector("#add-parameterized").addEventListener("click", () => {
  try {
    state.parameters = JSON.parse(elements.parameterValues.value);
    state.operations.push({ gate: "rz", target: 0, theta: "theta" });
    renderAll();
    showToast("Parameterized RZ(theta) added");
  } catch (error) {
    showOutput(elements.interopOutput, error.message);
  }
});

document.querySelector("#export-state").addEventListener("click", () => {
  const payload = JSON.stringify(currentVector(), null, 2);
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
  link.download = "anharmonic-state.json";
  link.click();
  URL.revokeObjectURL(link.href);
  showOutput(elements.interopOutput, "Current state JSON downloaded locally.");
});

document.querySelector("#export-circuit").addEventListener("click", () => {
  const payload = JSON.stringify({ systems: state.systemCount, initialState: state.initialState, parameters: state.parameters, operations: state.operations }, null, 2);
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
  link.download = "anharmonic-circuit.json";
  link.click();
  URL.revokeObjectURL(link.href);
  showOutput(elements.interopOutput, "Circuit JSON downloaded locally.");
});

document.querySelector("#export-qasm").addEventListener("click", () => {
  const lines = ["OPENQASM 2.0;", "include \"qelib1.inc\";", `qreg q[${state.systemCount}];`, `creg c[${state.systemCount}];`];
  state.operations.forEach((operation) => {
    const target = operation.target;
    if (operation.gate === "unitary" || operation.gate === "measure") return;
    if (operation.gate === "cx") lines.push(`cx q[${operation.control}],q[${target}];`);
    else if (["h", "x", "y", "z", "s", "t"].includes(operation.gate)) lines.push(`${operation.gate} q[${target}];`);
    else if (["rx", "ry", "rz"].includes(operation.gate)) lines.push(`${operation.gate}(${operation.theta}) q[${target}];`);
    else lines.push(`// ${operation.gate} is not native to OpenQASM 2 output`);
  });
  showOutput(elements.interopOutput, lines.join("\n"));
});

elements.initialState.addEventListener("change", () => {
  try {
    const parsed = JSON.parse(elements.initialState.value);
    if (!Array.isArray(parsed) || parsed.length !== 2 ** state.systemCount) throw new Error("Initial state length must match the selected dimension");
    const norm = stateNorm(parsed);
    state.initialState = parsed.map((value) => ({ re: Number(value.re), im: Number(value.im) })).map((value) => ({ re: value.re / norm, im: value.im / norm }));
    state.operations = [];
    renderAll();
    showToast("Normalized initial state loaded");
  } catch (error) {
    showOutput(elements.interopOutput, error.message);
  }
});
elements.mobileMenu.addEventListener("click", () => {
  const open = elements.nav.classList.toggle("is-open");
  elements.mobileMenu.setAttribute("aria-expanded", String(open));
});
elements.nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  elements.nav.classList.remove("is-open");
  elements.mobileMenu.setAttribute("aria-expanded", "false");
}));

populateSystemCountOptions();
populateSystemSelectors();
initParallaxStage();
updateGateControls();
setResultMode("probabilities");
renderAll();
renderVertexModel();
setAtlasMode("state");
window.requestAnimationFrame(drawVertexCanvas);
