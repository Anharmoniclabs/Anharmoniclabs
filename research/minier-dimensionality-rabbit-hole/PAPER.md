# From Zeta Zeros to EEG: A Reproducible Research Trail Through Dimensionality, Spectral Structure, and Alzheimer’s Disease

**Luis Minier**  
**Anharmonic Labs — Research Note / Working Paper**  
**11 September 2026**

## Abstract

This paper documents an exploratory research path rather than presenting a solved theorem or a clinical diagnostic. The work began with numerical experiments on the nontrivial zeros of the Riemann zeta function. I was interested in whether transforms, kernels, special constants, concentration measures, and finite-dimensional operator constructions could reveal structure that ordinary spectral views hid. Repeated adversarial controls forced several attractive ideas to fail: a Basel-constant kernel did not beat matched-strength controls, metallic-ratio anchors were not uniquely favored, and finite-window positivity became increasingly vulnerable to tiny boundary and numerical effects. Those failures changed the question. Instead of asking whether one preferred constant or transform was special, I began asking what happens when a structured signal is represented in too many correlated coordinates, and whether a lower-dimensional, stability-first representation can retain useful information.

That question led to resting-state EEG and Alzheimer’s disease. EEG is almost the opposite of a clean number-theory sequence: it is noisy, biological, nonstationary, subject-dependent, and high-dimensional. Yet the same methodological danger appears in both domains. A representation can manufacture apparent structure simply because enough coordinates, kernels, windows, channels, or hyperparameters have been searched. I therefore treated dimensionality itself as an experimental variable. Using the public OpenNeuro dataset ds004504, I focused an exploratory AD-versus-control study on subject-level spectral features, including Pz, conventional FFT baselines, and a family of alternative metallic/harmonic basis measurements. The strongest observed transform-level SNR gains did not automatically become strong disease classifiers. In our recorded experiments, a compact 24-dimensional winner-fraction-plus-SNR representation reached about 0.658 accuracy, 0.657 balanced accuracy, and 0.681 ROC AUC across 76 AD/HC subjects in the working cohort; an all-winner 31-dimensional representation produced lower accuracy while AUC remained similar; winner fractions alone fell near chance. A fold-mean feature set reached roughly 0.700 AUC. These results are preliminary and do not establish a biomarker. They do, however, support the narrower research direction: representation quality, dimensionality, stability, and subject-level validation must be studied together rather than assuming that more features or a prettier transform imply more biological information.

The intended next step is a preregistered, leakage-resistant, multi-dataset study of dimensionality and stability in EEG biomarkers, with nested subject-level validation, permutation testing, feature-count sweeps, external replication, and explicit negative controls.

## 1. Why this project exists

I did not begin by trying to build an Alzheimer’s classifier. I began with the Riemann zeta function.

The zeta function can be written, for real part of s greater than one, as

`ζ(s) = Σ n^{-s}`,

and analytically continued beyond that region. Its nontrivial zeros are complex numbers. The Riemann Hypothesis says that every nontrivial zero has real part exactly one half. My work did not prove this. I used known zeros as structured numerical data and asked whether different representations exposed reproducible organization.

In plain language, I was taking a famously structured sequence and asking: if I listen to it through different mathematical filters, do any of those filters reveal something that survives controls?

That sounds simple. It is not. Once many transforms, constants, windows, kernels, normalizations, and summary statistics are available, it becomes easy to find something that looks special by accident. This is one form of the same problem that appears in machine learning: high-dimensional search gives noise many chances to imitate signal.

The useful part of the Riemann work was therefore not a claimed proof. It was the discipline imposed by failed controls.

## 2. The Riemann phase

### 2.1 Zeros as a signal

I treated a finite set of zeta-zero ordinates `t_k` from zeros `ρ_k = 1/2 + i t_k` as locations in an impulse-like signal. From that representation I computed Fourier-domain power and concentration statistics. The experiments included entropy-like measures, Gini concentration, top-k spectral concentration, effective support, local curvature around selected scales, and finite-dimensional kernel/operator tests.

The underlying question was whether the zeros generated unusually concentrated or stable structure under a candidate transform compared with controls.

### 2.2 Special constants and metallic anchors

I tested parameterizations tied to constants that had appeared repeatedly in earlier experiments: the Basel value `ζ(2)=π²/6`, the golden ratio, the silver ratio, `√2`, and ordinary controls such as 4.0. The important methodological correction was to compare candidates at matched strength. A transform with a larger effective gain, narrower bandwidth, or different normalization cannot be called better merely because its output is more concentrated.

Once those controls were tightened, the attractive story weakened. Basel did not show a robust special advantage. Silver/golden anchors could look good under particular views, but matched controls could tie or beat them. That is a negative result, and it matters.

### 2.3 Finite-window positivity and numerical ghosts

A second line of work concerned finite-dimensional positivity tests related to Weil-style thinking. The practical issue was that a matrix or operator that should be studied for positivity can develop extremely small negative eigenvalues under truncation, discretization, boundary effects, or floating-point arithmetic.

The observed behavior suggested a rapidly shrinking lower spectral scale as the window expanded. In the working notes, the boundary-layer scale was modeled heuristically in a form like

`λ_min scale ~ exp(-C e^(2L) / L)`.

This is not stated here as a proved theorem. Its value was operational: when the smallest meaningful scale becomes fantastically small, ordinary floating-point signs are not enough to certify positivity. Interval arithmetic, explicit error bounds, and convergence tests become necessary.

This was another lesson about dimensionality. Increasing the size of a finite approximation can add information, but it can also add ill-conditioning and make a yes/no conclusion less trustworthy.

## 3. The rabbit hole: dimensionality became the subject

The repeated pattern was:

1. Add a richer representation.
2. See a stronger-looking structure.
3. Add a fairer control.
4. Watch some of the advantage disappear.
5. Increase resolution or dimension.
6. Discover that numerical stability becomes harder, not easier.

That changed my research question.

Instead of asking, “Which constant is the key?”, I began asking, “How much of an observed effect survives when the representation is compressed, perturbed, cross-validated, and compared against matched nulls?”

This is closely related to the curse of dimensionality. As dimension grows, data become sparse relative to the space they occupy. Distances can become less informative, covariance estimates become unstable, flexible models can fit accidental structure, and the number of possible feature combinations explodes. With small biological cohorts this becomes especially dangerous.

The bridge from zeta experiments to EEG was therefore methodological, not mystical. I am not claiming that the Riemann zeros cause Alzheimer’s disease, encode brains, or provide a medical theory. The bridge is that both problems punish careless representation search.

## 4. Why EEG and Alzheimer’s disease

Resting-state EEG is a useful stress test for this idea because it contains many dimensions at once: subjects, electrodes, time points, frequency bins, frequency bands, windows, connectivity pairs, transforms, and derived features.

The public dataset used here is OpenNeuro **ds004504**, “A dataset of EEG recordings from: Alzheimer’s disease, Frontotemporal dementia and Healthy subjects.” The canonical dataset contains 88 participants: 36 with Alzheimer’s disease, 23 with frontotemporal dementia, and 29 healthy controls. EEG was recorded at 500 Hz with 19 scalp electrodes in the international 10–20 layout, including Pz. Recordings were resting-state, eyes closed. The release contains raw data and preprocessed derivatives. The published preprocessing includes 0.5–45 Hz band-pass filtering, mastoid re-referencing, artifact-subspace reconstruction, ICA, and automatic rejection of eye/jaw artifact components.

The present exploratory branch concentrated on AD versus healthy-control structure rather than claiming a three-class clinical system. Some working runs used a 76-subject AD/HC analysis table assembled during experimentation. That count does not equal the canonical 36+29 AD/CN count in the current ds004504 release, so it must be treated as a working-cohort artifact until the exact subject manifest is reconstructed and audited. The reproducible harness therefore defaults to the canonical dataset metadata and requires an explicit cohort manifest for any noncanonical run.

That distinction is important. A paper should not quietly turn an experimental table into a property of the source dataset.

## 5. Experimental representation

### 5.1 Baseline

The baseline is ordinary Fourier spectral analysis. For a signal `x[n]`, the discrete Fourier transform is

`X[k] = Σ x[n] exp(-2π i kn/N)`.

Power or magnitude summaries can then be measured in conventional EEG bands or over selected spectral windows.

### 5.2 Alternative basis family

The exploratory harness compared FFT-derived measurements with alternative parameterized basis/kernel views that we labeled with metallic-family names such as golden, silver, bronze, best, and harmony. These labels identify experimental parameterizations; they do not imply that the constants have a known neurological role.

The purpose was to ask a narrower question: can a structured nonuniform or modulated basis concentrate subject-level spectral energy more strongly than a conventional FFT baseline, and if so, does that concentration contain disease-separating information?

### 5.3 Pz focus

Pz was used as a focused channel in several runs to reduce the immediate channel dimension and make the transform comparison easier to audit. This is a deliberate dimensionality reduction, not a claim that Pz is the uniquely correct Alzheimer’s electrode.

### 5.4 Subject-level features

Rather than treating every short epoch as an independent person, the main disease-separation summaries were aggregated at subject level. Candidate features included transform winner fractions, SNR-like improvements relative to FFT, fold-level means, and combinations of these summaries.

The key rule is that train/test separation must occur by subject. Epoch-level random splitting can leak person-specific information across folds and inflate apparent performance.

## 6. Recorded exploratory results

The transform experiments recorded the following approximate SNR advantages over FFT:

| Experimental basis | SNR advantage vs FFT |
|---|---:|
| golden | +2.597 dB |
| silver | +2.720 dB |
| bronze | +2.379 dB |
| best candidate | +3.229 dB |
| harmony | +3.784 dB |

In the working 76-subject AD/HC table, mean FFT-to-harmony SNR changed from approximately 20.328 to 24.144 dB in AD and from 20.226 to 23.982 dB in controls. This is an important warning: both groups improved. A transform can improve signal concentration without automatically becoming a disease marker.

Recorded subject-level classification summaries were:

| Feature family | Dimensions | Accuracy | Balanced accuracy | ROC AUC |
|---|---:|---:|---:|---:|
| winner fractions + SNR | 24 | 0.6579 | 0.6569 | 0.6806 |
| all winner features | 31 | 0.6184 | 0.6181 | 0.6882 |
| winner fractions only | 12 | 0.5263 | 0.5278 | 0.4736 |
| fold-means best set | compact | 0.6567 | 0.6554 | 0.6996 |

For the 24-dimensional run, the recorded confusion matrix was TN=27, FP=13, FN=13, TP=23.

These numbers are exploratory. They are not a validated diagnostic accuracy estimate because the exact 76-subject cohort provenance, feature-selection nesting, and all preprocessing decisions need to be reconstructed from the run artifacts and rerun from a frozen manifest.

## 7. What the results actually say

The strongest conclusion is not “harmony detects Alzheimer’s.” The data do not justify that.

The useful observation is that transform-level concentration and disease-level discrimination are different objectives. Harmony produced the largest recorded SNR improvement, yet the disease classifiers remained moderate. Winner fractions by themselves were essentially unhelpful in the recorded run. Adding SNR information helped. Adding still more winner features did not reliably improve accuracy.

That is exactly the dimensionality problem that motivated the pivot.

A feature can be mathematically striking but biologically nonspecific. A larger feature vector can contain more measurements while producing a worse classifier. A transform can improve both classes almost equally. The research target therefore becomes the **stable low-dimensional residue**: the smallest set of features that survives subject resampling, preprocessing perturbation, matched controls, and external datasets.

## 8. What failed, and why it stays in the paper

Negative results are part of the result.

The Riemann experiments did not establish a privileged Basel, silver, or golden constant. Matched-strength controls removed some apparent advantages. The finite-window operator work did not prove the Riemann Hypothesis. Tiny negative eigenvalues could be numerical or truncation artifacts and require certified arithmetic before they can carry mathematical meaning.

The EEG work did not establish a clinical Alzheimer’s biomarker. The best exploratory AUC was around 0.70, which is interesting enough to investigate but nowhere near sufficient for a diagnostic claim. The transform SNR improvement was shared by AD and controls. The 76-subject working cohort must be audited against the canonical dataset.

Keeping these failures visible prevents the research narrative from being rewritten after the fact.

## 9. The cumulative hypothesis

The cumulative hypothesis is deliberately narrower than the path that produced it:

> In small-sample structured data, useful signal may be better identified by the stability of a compact representation under perturbation and resampling than by the maximum concentration, dimensionality, or in-sample separation obtainable from a large feature search.

For Alzheimer’s EEG, the practical version is:

> A low-dimensional subject-level spectral representation selected for cross-fold stability may generalize better than a high-dimensional bank of transform winners, even when the larger bank appears richer in-sample.

This is falsifiable. If performance continues to improve reliably with feature dimension under properly nested validation and external replication, the hypothesis is wrong or incomplete.

## 10. Planned dimensionality experiment

The next study should freeze the dataset and perform a feature-count sweep. For each outer subject-level fold:

1. Fit every preprocessing statistic using training subjects only.
2. Rank or select features only inside the training data.
3. Evaluate dimensions such as 2, 4, 8, 12, 16, 24, 32, 64, and the full set.
4. Repeat with multiple seeds and grouped folds.
5. Compare observed labels with label permutations.
6. Compare the candidate basis family with matched random/ordinary parameter controls.
7. Record accuracy, balanced accuracy, ROC AUC, calibration, feature-selection stability, and confidence intervals.
8. Lock the chosen representation before external replication.

The primary result should be a curve of held-out performance versus dimension, not a single best score discovered after searching many configurations.

## 11. External validation plan

A genuine biomarker program needs more than ds004504. The intended progression is:

- reproduce the canonical ds004504 AD/CN cohort exactly;
- test raw and official preprocessed derivatives separately;
- add FTD as a specificity challenge rather than only asking disease versus healthy;
- replicate on at least one independent Alzheimer’s EEG cohort;
- test whether selected features correlate with severity measures where participant-level clinical metadata are legitimately available;
- compare against ordinary bandpower, spectral entropy, 1/f or aperiodic parameters, and established connectivity features;
- report failures and null results alongside wins.

A marker that only works on one dataset after extensive tuning is not a marker.

## 12. Reproducibility and data policy

The repository does not duplicate the multi-gigabyte EEG dataset. Instead it contains a dataset manifest and downloader instructions pointing to the canonical CC0 OpenNeuro source. This avoids silently changing the source data and makes the exact upstream dataset version explicit.

The harness records random seeds, cohort IDs, channel selection, preprocessing mode, feature definitions, fold assignments, and output tables. Noncanonical working cohorts must be supplied as explicit manifests.

The zeta side follows the same rule: known zeros or generated zero ordinates are inputs; candidate transforms are compared with controls; every parameter sweep should be logged rather than reporting only the winning setting.

## 13. Limitations

This work is exploratory and crosses domains, which creates an obvious risk of storytelling after the fact. The mathematical and neurological parts are connected by methodology, not by an established physical mechanism. Special constants are treated as candidate parameterizations, not biological facts. The EEG sample size is small for high-dimensional modeling. The recorded 76-subject working cohort needs provenance reconstruction. Multiple testing and researcher degrees of freedom can inflate results. SNR definitions can favor a transform without improving class specificity. Classification metrics from one dataset do not establish clinical utility.

These limitations are not footnotes. They define the work that remains.

## 14. Intended research contribution

The intended contribution is a transparent experimental framework for studying a recurring problem: when a dataset offers many possible representations, how do we distinguish real structure from structure created by the search itself?

The Riemann work supplied a harsh sandbox. Attractive constants failed controls. Larger finite approximations became numerically delicate. The EEG work supplied a real biological test. Alternative bases could improve concentration, but disease separation remained modest and depended on which compact summaries