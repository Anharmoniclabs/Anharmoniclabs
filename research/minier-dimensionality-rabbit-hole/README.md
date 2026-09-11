# Minier dimensionality research harness

This folder freezes the current research direction connecting two exploratory programs by **methodology**: numerical representation tests on Riemann zeta zeros and dimensionality/stability tests on Alzheimer’s EEG. It does **not** claim that zeta zeros cause or explain Alzheimer’s disease, does not claim a proof of RH, and does not claim a clinical biomarker.

## Contents

- `PAPER.md` — narrative working paper and honest limitations.
- `harness.py` — executable audit harness for zeta concentration/null tests and subject-level EEG dimensionality sweeps.
- `DATASETS.md` — canonical dataset sources, versions, licensing, and cohort warnings.
- `requirements.txt` — Python dependencies.

## Canonical EEG data

OpenNeuro ds004504 contains 88 resting-state eyes-closed EEG participants: 36 AD, 23 FTD, 29 controls; 19 channels; 500 Hz. Use the canonical OpenNeuro release rather than committing the multi-GB data into Git.

Example with OpenNeuro CLI:

```bash
npm install -g @openneuro/cli
openneuro download --snapshot 1.0.9 ds004504 data/ds004504
```

The repository intentionally stores pointers/manifests, not a duplicate of the source EEG dataset.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Riemann zero/null-control experiment
python harness.py zeta --zeros 109 --seed 20260911 --out results/zeta

# EEG dimensionality experiment after downloading ds004504
python harness.py eeg --bids-root data/ds004504 --group-a A --group-b C --channel Pz --out results/eeg
```

## Reproducibility rule

Any result using the earlier 76-subject working AD/HC table must provide the exact subject IDs in a cohort manifest. The current canonical ds004504 metadata gives 36 AD + 29 controls, so the 76-subject table is not silently treated as canonical.

## What counts as a positive result

A candidate representation must beat ordinary baselines and matched controls under subject-level validation, survive feature-count sweeps and label permutation, remain stable across folds/seeds, and replicate on an independent cohort. A transform-level SNR gain alone is not a disease biomarker.
