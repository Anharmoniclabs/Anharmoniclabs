# Experiment Ledger

Every committed experimental conclusion should include:

- experiment name and script path;
- UTC timestamp;
- source Git commit;
- matrix dimension and qubit count;
- transform direction;
- backend or simulator;
- random seed when applicable;
- numerical error metric;
- circuit depth and gate counts when applicable;
- a plain statement of what the experiment does and does not establish.

Generated JSON files belong under `results/`. Do not edit result values by hand.
