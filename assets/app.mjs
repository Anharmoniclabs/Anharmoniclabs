import {
  GATE_LABELS,
  basisLabel,
  formatComplex,
  operationLabel,
  phase,
  probabilities,
  sampleCounts,
  shannonEntropy,
  simulate,
  stateNorm,
} from "./simulator-core.mjs";

const state = {
  systemCount: 3,
  operations: [],
  selectedGate: "h",
  resultMode: "probabilities",
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

  const rows = Array.from({ length: state.systemCount }, (_, system) => {
    const cells = state.operations.map((operation, index) => {
      let content = '<span class="wire-dot"></span>';
      let className = "circuit-cell";
      if (operation.target === system) {
        content = `<button class="circuit-gate" data-remove="${index}" title="Remove ${operationLabel(operation)}" aria-label="Remove ${operationLabel(operation)}">${GATE_LABELS[operation.gate]}</button>`;
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
  const vector = simulate(state.systemCount, state.operations);
  const distribution = probabilities(vector);
  const maximum = Math.max(...distribution, Number.EPSILON);
  const visible = distribution
    .map((probability, index) => ({ probability, index }))
    .filter(({ probability }) => probability > 1e-10 || distribution.length <= 8);

  elements.probabilityChart.innerHTML = visible.map(({ probability, index }) => `
    <div class="probability-row">
      <span class="basis-state">|${basisLabel(index, state.systemCount)}⟩</span>
      <div class="probability-track">
        <span class="probability-fill" style="--value:${(probability / maximum) * 100}%"></span>
      </div>
      <span class="probability-value">${(probability * 100).toFixed(probability >= 0.001 ? 2 : 5)}%</span>
    </div>`).join("");

  elements.amplitudeTable.innerHTML = vector.map((amplitude, index) => {
    const probability = distribution[index];
    if (probability <= 1e-10 && vector.length > 8) return "";
    return `<tr>
      <th scope="row">|${basisLabel(index, state.systemCount)}⟩</th>
      <td class="complex-value">${formatComplex(amplitude)}</td>
      <td>${probability.toFixed(6)}</td>
      <td>${(phase(amplitude) / Math.PI).toFixed(4)}π</td>
    </tr>`;
  }).join("");

  elements.norm.textContent = stateNorm(vector).toFixed(12);
  elements.entropy.textContent = `${shannonEntropy(distribution).toFixed(4)} bits`;
  elements.support.textContent = String(distribution.filter((value) => value > 1e-10).length);
  window.__anharmonicCurrentResult = { vector, distribution };
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
  if (!example) return;
  state.systemCount = example.systems;
  state.operations = example.operations;
  elements.systemCount.value = String(state.systemCount);
  populateSystemSelectors();
  renderAll();
  showToast(`${name === "ghz" ? "GHZ" : name[0].toUpperCase() + name.slice(1)} example loaded`);
}

function runSampling() {
  const shots = Number(elements.shots.value);
  const seed = Number(elements.seed.value);
  const counts = sampleCounts(
    window.__anharmonicCurrentResult.distribution,
    shots,
    seed,
    state.systemCount,
  );
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
  populateSystemSelectors();
  renderAll();
  showToast("System resized and reset");
});

elements.angle.addEventListener("input", () => {
  const ratio = Number(elements.angle.value);
  elements.angleOutput.textContent = `${ratio.toFixed(2)}π`;
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

elements.sample.addEventListener("click", runSampling);
elements.mobileMenu.addEventListener("click", () => {
  const open = elements.nav.classList.toggle("is-open");
  elements.mobileMenu.setAttribute("aria-expanded", String(open));
});
elements.nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  elements.nav.classList.remove("is-open");
  elements.mobileMenu.setAttribute("aria-expanded", "false");
}));

populateSystemSelectors();
updateGateControls();
setResultMode("probabilities");
renderAll();
