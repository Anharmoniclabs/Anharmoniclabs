# Datasets and references

## EEG — canonical source

**OpenNeuro ds004504**  
Title: *A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects*  
OpenNeuro DOI/version used for the current manifest: `10.18112/openneuro.ds004504.v1.0.9`  
License: CC0  
Canonical URL: `https://openneuro.org/datasets/ds004504`

Dataset descriptor: Miltiadous A, Tzimourta KD, Afrantou T, Ioannidis P, Grigoriadis N, Tsalikakis DG, Angelidis P, Tsipouras MG, Glavas E, Giannakeas N, Tzallas AT. *A Dataset of Scalp EEG Recordings of Alzheimer’s Disease, Frontotemporal Dementia and Healthy Subjects from Routine EEG.* Data. 2023;8(6):95. DOI: `10.3390/data8060095`.

Canonical cohort: 88 participants = 36 AD + 23 FTD + 29 cognitively normal controls. Resting-state eyes-closed EEG, 19 10–20 electrodes, 500 Hz. Raw and preprocessed derivatives are provided upstream.

### Working-cohort warning

Earlier exploratory notes contain a 76-subject AD/HC analysis table (36 AD, 40 HC in the recorded summary). That does **not** match the canonical ds004504 cohort above. Until the exact subject provenance is recovered, those 76-subject metrics are retained as historical exploratory results only and must not be represented as a canonical ds004504 evaluation.

## Zeta-zero inputs

The harness can generate the first `N` nontrivial zeta zeros using `mpmath.zetazero`. Generated ordinates are deterministic given `N` and the numerical precision. For larger experiments, freeze the exact zero list to a text/CSV artifact and hash it.

Recommended mathematical references:

- Riemann, B. (1859). *Über die Anzahl der Primzahlen unter einer gegebenen Grösse.*
- Edwards, H. M. (1974). *Riemann's Zeta Function.* Academic Press.
- Titchmarsh, E. C.; Heath-Brown, D. R. (1986). *The Theory of the Riemann Zeta-function*, 2nd ed. Oxford University Press.
- Montgomery, H. L. (1973). The pair correlation of zeros of the zeta function. *Proceedings of Symposia in Pure Mathematics* 24, 181–193.
- Odlyzko, A. M. numerical investigations of zeta zeros and spacing statistics.

## Alzheimer’s EEG context

The ds004504 descriptor should be cited for acquisition and preprocessing. For any new clinical claim, add literature on established EEG slowing, band-power changes, connectivity, aperiodic activity, and subject-level validation. The present repository treats the metallic/harmony transforms as experimental signal representations, not established neurological mechanisms.

## Data policy

Do not commit raw patient/participant EEG files to this repository. Pull them from the canonical CC0 source, preserve upstream identifiers, record the snapshot/version, and write derived tables without adding personally identifying information. All train/test splits must be by participant.
