import { simulate } from "../../assets/simulator-core.mjs";

const circuits = {
  bell: {
    systems: 2,
    operations: [
      { gate: "h", target: 0 },
      { gate: "cx", control: 0, target: 1 },
    ],
  },
  rotated_entanglement: {
    systems: 3,
    operations: [
      { gate: "h", target: 0 },
      { gate: "cx", control: 0, target: 2 },
      { gate: "rz", target: 1, theta: Math.PI / 3 },
      { gate: "ry", target: 2, theta: -0.71 },
    ],
  },
  nonadjacent: {
    systems: 4,
    operations: [
      { gate: "x", target: 3 },
      { gate: "cx", control: 3, target: 0 },
      { gate: "swap", control: 1, target: 2 },
      { gate: "rx", target: 2, theta: 0.37 },
    ],
  },
};

const encode = (state) => state.map(({ re, im }) => ({ re, im }));
const output = Object.fromEntries(Object.entries(circuits).map(([name, circuit]) => [
  name,
  encode(simulate(circuit.systems, circuit.operations)),
]));
process.stdout.write(JSON.stringify(output));