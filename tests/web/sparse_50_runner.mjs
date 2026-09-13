import { sparseRecords, sparseSimulate } from "../../assets/simulator-core.mjs";

const sparse = sparseSimulate(50, [
  { gate: "x", target: 49 },
  { gate: "cx", control: 49, target: 0 },
  { gate: "x", target: 1 },
  { gate: "swap", control: 1, target: 48 },
  { gate: "cz", control: 0, target: 2 },
]);
const records = sparseRecords(sparse);
process.stdout.write(JSON.stringify({ nonzeroAmplitudes: records.length, index: records[0]?.index }));