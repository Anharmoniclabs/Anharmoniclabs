# From Riemann Zeta Zeros to Alzheimer’s EEG
## How failed spectral shortcuts led to a study of dimensionality, stability, and biomarkers

**Luis Minier — Anharmonic Labs**  
**Working paper, 11 September 2026**

## Abstract

This paper records how one research problem turned into another. I began with numerical experiments on the nontrivial zeros of the Riemann zeta function. I tested Fourier views, concentration statistics, finite matrices, special constants, metallic-ratio parameterizations, and positivity ideas. Several attractive patterns weakened when I introduced matched controls. Basel-based and metallic-ratio choices were not uniquely favored, and finite-window positivity became increasingly sensitive to tiny numerical and boundary effects. That failure changed the question from “which constant is special?” to “how much apparent structure is being created by the representation itself?”

That question is a version of the curse of dimensionality. The more coordinates, transforms, windows, kernels, and hyperparameters I searched, the more opportunities noise had to look meaningful. I then moved the same methodological question into a harder real-world system: resting-state EEG in Alzheimer’s disease. Using OpenNeuro ds004504, I compared conventional FFT-derived measurements with experimental metallic/harmonic basis summaries, mainly at Pz, and tested whether stronger spectral concentration became useful subject-level disease separation. The recorded transform gains were real enough to measure but were not disease-specific: both Alzheimer’s and control groups improved. A 24-feature winner-fraction-plus-SNR representation reached about 0.658 accuracy and 0.681 ROC AUC in a historical 76-subject working table; winner fractions alone were near chance; a compact fold-mean set reached about 0.700 AUC. These are exploratory results, not a diagnostic claim. The 76-subject table also does not match the canonical 36 AD + 29 control composition of ds004504 and therefore requires provenance reconstruction.

The research direction that survives is narrower and testable: in small-sample structured data, the most useful representation may be the smallest one whose information remains stable under resampling, perturbation, matched controls, and external replication. The repository accompanying this paper freezes a harness for testing that idea rather than preserving only the winning runs.

## 1. Where I actually started

I did not start by trying to diagnose Alzheimer’s disease. I was studying the Riemann zeta function.

For real part of `s > 1`, the zeta function is

`ζ(s) = Σ_{n=1}^∞ n^{-s}`.

It extends analytically to almost the whole complex plane. Its nontrivial zeros are complex numbers. The Riemann Hypothesis says that every nontrivial zero lies on the line `Re(s)=1/2`.

I have not proved the Riemann Hypothesis. My work used known zeros as structured numerical data. I treated their imaginary parts as a sequence and asked what different mathematical representations did to that sequence.

In ordinary language: I had a signal with famous hidden structure, and I kept changing the lens through which I looked at it.

## 2. Turning zeta zeros into an experimental signal

I represented zeros `ρ_k = 1/2 + i t_k` through their ordinates `t_k`. A finite block of ordinates can be mapped to an impulse train or another fixed grid, transformed, and summarized. I used FFT power, entropy-like quantities, Gini concentration, top-k concentration, effective support, local curvature, and finite-dimensional matrix tests.

The original hope was that a particular transform or scale might expose a clean signature. I tested constants that had appeared in earlier work: `ζ(2)=π²/6`, the golden ratio, the silver ratio, `√2`, and ordinary numerical controls.

The important correction was to stop comparing unequal filters. If one candidate has more gain, a narrower effective window, or a different normalization, it can appear more concentrated without containing more information. Matched-strength controls were therefore necessary.

Once I tightened those controls, the story became less exciting but more useful. Basel did not show a robust unique advantage. Silver and golden settings sometimes looked good, but ordinary or randomized matched settings could tie them. The correct result was not “the constant works.” It was “the earlier evidence was not specific enough.”

## 3. The second warning: finite-dimensional positivity

Another branch of the Riemann work involved finite-window positivity tests motivated by Weil-style ideas and operator constructions. The numerical problem was straightforward to state: a matrix that is supposed to approximate a positive object can develop tiny negative eigenvalues because of truncation, discretization, boundary conditions, or floating-point error.

In the working experiments the smallest scale appeared to collapse extremely rapidly as the window size grew. A heuristic boundary scale was written in the form

`λ_min ~ exp(-C e^(2L)/L)`.

I do not present that expression as a proved theorem here. The practical lesson is enough: if the meaningful eigenvalue scale becomes much smaller than ordinary floating-point resolution, the sign printed by a computer is not a proof. Certified interval arithmetic and explicit error bounds are needed.

Increasing dimension had given me a supposedly better approximation while simultaneously making the conclusion more fragile.

## 4. The curse of dimensionality became the real question

Across the Riemann experiments I kept seeing the same cycle:

1. Add a richer representation.
2. Find a stronger-looking pattern.
3. Add a fair control.
4. Lose part of the effect.
5. Increase resolution or feature count.
6. Gain detail but lose numerical or statistical stability.

That pushed me toward a different question: **what structure survives compression and hostile testing?**

This is where the curse of dimensionality enters. As the number of dimensions grows, a fixed amount of data occupies the space more sparsely. Flexible models get more ways to fit accidents. Covariance estimates become less stable. Distances can become less informative. Feature selection itself becomes a search problem. If many transforms and many parameters are tried, the researcher is effectively creating even more dimensions than appear in the final table.

The connection from Riemann zeros to EEG is therefore methodological. I am not claiming that zeta zeros explain the brain or Alzheimer’s disease. I am claiming that both problems can fool a researcher who searches enough representations without strong controls.

## 5. Why Alzheimer’s EEG was a useful next test

EEG is a much harsher environment than a sequence of mathematical zeros. It varies across people, time, electrodes, artifacts, preprocessing choices, frequency bands, and disease state. A single recording can be represented by thousands or millions of candidate measurements.

The public dataset used for this work is OpenNeuro **ds004504**, *A dataset of EEG recordings from: Alzheimer’s disease, Frontotemporal dementia and Healthy subjects*. The canonical release contains 88 people: 36 Alzheimer’s disease (AD), 23 frontotemporal dementia (FTD), and 29 cognitively normal controls. Recordings are resting-state, eyes closed, with 19 scalp electrodes in the international 10–20 layout, sampled at 500 Hz. Pz is one of those electrodes. The source provides raw recordings and preprocessed derivatives. The published preprocessing includes 0.5–45 Hz filtering, mastoid re-referencing, artifact-subspace reconstruction, ICA, and automatic removal of components classified as eye or jaw artifacts.

I focused several exploratory runs on Pz. This was not because I had proved Pz was the Alzheimer’s electrode. It was a deliberate way to reduce channel dimensionality and make the transform comparison easier to inspect.

## 6. FFT baseline and experimental bases

The baseline was conventional Fourier analysis. For samples `x[n]`, the discrete Fourier transform is

`X[k] = Σ x[n] exp(-2π i kn/N)`.

From the spectrum we can calculate power in standard frequency bands or other concentration statistics.

I then compared this with experimental parameterized basis/kernel views labeled golden, silver, bronze, best, and harmony in the working notebooks. Those names describe the parameterizations used in the experiments. They are not evidence that metallic constants have a known neurological role.

The question was deliberately mechanical: can another basis concentrate the signal more strongly than FFT, and if it can, does the difference separate AD from controls?

## 7. What the exploratory EEG runs showed

The recorded SNR advantages relative to FFT were approximately:

| Basis | SNR advantage vs FFT |
|---|---:|
| Golden | +2.597 dB |
| Silver | +2.720 dB |
| Bronze | +2.379 dB |
| Best candidate | +3.229 dB |
| Harmony | +3.784 dB |

At first glance, harmony looked like the obvious winner. But the group means exposed the important part. In the historical 76-subject working table, AD moved from about 20.328 dB with FFT to 24.144 dB with harmony. Controls moved from about 20.226 dB to 23.982 dB.

Both groups improved.

That means a better concentrating transform is not automatically an Alzheimer’s marker. It may simply be a better concentrating transform.

The recorded subject-level classification summaries were:

| Feature family | Dimensions | Accuracy | Balanced accuracy | ROC AUC |
|---|---:|---:|---:|---:|
| Winner fractions + SNR | 24 | 0.6579 | 0.6569 | 0.6806 |
| All winner features | 31 | 0.6184 | 0.6181 | 0.6882 |
| Winner fractions only | 12 | 0.5263 | 0.5278 | 0.4736 |
| Fold-means best set | compact | 0.6567 | 0.6554 | 0.6996 |

For the 24-dimensional run the recorded confusion matrix was `TN=27, FP=13, FN=13, TP=23`.

These results are not strong enough for a clinical claim. They are strong enough to justify a better experiment about dimensionality.

## 8. A critical provenance problem

The canonical ds004504 dataset contains 36 AD and 29 normal controls, which would give 65 AD/CN participants if all canonical subjects were used. My historical summary contains 76 AD/HC subjects, including 40 controls.

Those cannot both describe the same canonical cohort.

The honest treatment is to preserve the 76-subject numbers as historical exploratory results while refusing to call them a canonical ds004504 evaluation until the exact subject manifest is recovered. The accompanying harness therefore reads the current `participants.tsv` directly and requires explicit manifests for noncanonical cohorts.

This is exactly why reproducibility infrastructure matters. A result without a frozen cohort is a clue, not a finished result.

## 9. What dimensionality appears to be doing

The 12-dimensional winner-fraction representation was near chance. Adding SNR information improved performance. Expanding to 31 winner features did not improve accuracy. A smaller fold-mean representation produced the best recorded AUC.

That pattern does not prove a universal law, but it is consistent with the hypothesis that more features are not automatically more useful. Some dimensions carry redundant information. Some carry noise. Some are unstable across folds. Some encode transform behavior shared by both groups rather than disease-specific behavior.

The target is therefore not the largest feature bank. The target is what I call the **stable low-dimensional residue**: the smallest representation that keeps its information when subjects, folds, preprocessing choices, and reasonable perturbations change.

## 10. The cumulative hypothesis

The research hypothesis that survives both projects is:

> In small-sample structured data, useful signal is better identified by the stability of a compact representation under perturbation and resampling than by the maximum concentration, dimensionality, or in-sample separation found during a large representation search.

For EEG specifically:

> A compact subject-level spectral representation selected entirely inside training folds may generalize better than a high-dimensional bank of transform winners, even when the larger bank looks richer on the development data.

This is falsifiable. If properly nested validation shows that performance reliably improves as dimension grows, and that improvement replicates externally, this hypothesis loses.

## 11. The experiment that should be run next

The next study should freeze the canonical cohort and make dimension itself the independent variable. Candidate dimensions should include 2, 4, 8, 12, 16, 24, 32, 64, and the complete feature set when available.

Every operation that learns from labels must occur inside the training portion of each outer fold: scaling, ranking, feature selection, hyperparameter tuning, and threshold selection. Test subjects must remain untouched until the final evaluation of that fold.

The study should repeat grouped subject-level folds over multiple seeds, run label permutations, compare the metallic/harmony family against matched random parameterizations, and report confidence intervals rather than only the best score.

The primary figure should be held-out performance versus feature dimension. A second figure should show feature-selection stability versus dimension. A third should compare real labels with the permutation null.

## 12. Controls that can kill the hypothesis

A serious harness needs controls designed to make the preferred idea fail.

First, random and ordinary transform parameters should be matched for gain and effective bandwidth. Second, label permutation should destroy disease separation; if it does not, the pipeline is leaking. Third, subject IDs must never cross train and test folds through separate epochs. Fourth, the result should be rerun on raw and official preprocessed data. Fifth, Pz should be compared with other channels and with compact multichannel baselines. Sixth, ordinary EEG features such as relative bandpower, spectral entropy, aperiodic parameters, and established connectivity summaries should be competitive baselines. Seventh, the chosen representation must be frozen before external replication.

## 13. Negative results are part of the result

The Riemann experiments did not establish a privileged Basel, silver, or golden constant. They did not prove RH. The finite positivity experiments exposed numerical sensitivity rather than eliminating it.

The EEG experiments did not establish a diagnostic biomarker. Harmony’s SNR gain occurred in both groups. Winner fractions alone were weak. The best exploratory AUC was around 0.70. The historical cohort provenance is incomplete.

These facts stay in the paper because removing them would create a false story in which every step was a success. The actual path was useful because several ideas failed.

## 14. Intended research program

The immediate goals are:

1. Reproduce the canonical ds004504 AD/CN cohort from its participant table.
2. Recreate every candidate feature from raw or official derivative EEG.
3. Run the frozen dimensionality sweep with nested subject-level validation.
4. Add FTD as a specificity challenge.
5. Measure stability across folds, seeds, channels, and preprocessing variants.
6. Run matched random-basis and label-permutation controls.
7. Lock one compact representation.
8. Test it on an independent Alzheimer’s EEG cohort.

Only after external replication should the work use the word **biomarker** in a strong sense.

## 15. What this research is and is not

This work is a reproducible investigation of representation, dimensionality, and stability. It is not a mathematical proof of the Riemann Hypothesis. It is not evidence that metallic ratios have a biological mechanism in Alzheimer’s disease. It is not a medical diagnostic and should not be used for patient decisions.

The tangible contribution is the research trail itself: a sequence of tests in which attractive spectral structure was repeatedly forced through controls, eventually turning dimensionality from a nuisance into the main variable being studied.

## 16. Conclusion

The path from Riemann zeros to Alzheimer’s EEG looks strange only if the subjects are treated as the connection. They are not. The connection is the failure mode.

In the zeta experiments, richer representations repeatedly produced patterns that became less special under fair controls. In finite operator experiments, larger approximations exposed smaller numerical scales and made certification harder. In EEG, alternative bases increased spectral concentration, but that improvement was shared by disease and control groups, and larger feature collections did not automatically classify better.

The research question that remains is simple enough to state without the rabbit hole:

**When data are limited and possible representations are abundant, what is the smallest structure that remains stable when we try to break it?**

For Alzheimer’s EEG, answering that question requires frozen cohorts, subject-level validation, dimensionality sweeps, null models, ordinary EEG baselines, and external replication. That is where the work currently stands.

## References

1. Riemann, B. (1859). *Über die Anzahl der Primzahlen unter einer gegebenen Grösse.* Monatsberichte der Berliner Akademie.
2. Edwards, H. M. (1974). *Riemann’s Zeta Function.* Academic Press.
3. Titchmarsh, E. C., & Heath-Brown, D. R. (1986). *The Theory of the Riemann Zeta-function*, 2nd ed. Oxford University Press.
4. Montgomery, H. L. (1973). The pair correlation of zeros of the zeta function. *Proceedings of Symposia in Pure Mathematics*, 24, 181–193.
5. Miltiadous, A., Tzimourta, K. D., Afrantou, T., Ioannidis, P., Grigoriadis, N., Tsalikakis, D. G., Angelidis, P., Tsipouras, M. G., Glavas, E., Giannakeas, N., & Tzallas, A. T. (2023). A Dataset of Scalp EEG Recordings of Alzheimer’s Disease, Frontotemporal Dementia and Healthy Subjects from Routine EEG. *Data*, 8(6), 95. DOI: 10.3390/data8060095.
6. OpenNeuro dataset ds004504, current manifest version used by this repository: DOI 10.18112/openneuro.ds004504.v1.0.9.