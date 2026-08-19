# CEvNS Physics Audit
## Concrete Objective

The goal of this Skill is not merely to verify that the existing code runs
successfully.

Its primary goal is to determine whether the implemented physics model
corresponds to the physical experiment or benchmark that the user intends to
reproduce.

Given:

```text
current implementation
current numerical prediction
user-supplied physics document
official or independent experimental references
published numerical benchmarks
```

the Skill must answer the following questions in order:

```text
1. What physical dataset does the current code actually implement?

2. What physical dataset does the external benchmark describe?

3. Are these two definitions the same?

4. If they are different, which physical inputs are different?

5. If they are intended to be the same but the numerical results disagree,
   which physics layer is most likely responsible?

6. How large is the expected numerical effect of each identified difference?

7. Which issue should be checked or repaired first?

8. What level of experimental reproduction can currently be claimed?
```

The audit must reduce the discrepancy into physically interpretable layers:

```text
dataset identity
observable and units
exposure and normalization
detector inventory
source
target composition
kinematics
cross section
detector response
analysis window and binning
statistics
```

For each layer, the Skill must classify the result as:

```text
CONSISTENT
DIFFERENT
UNCERTAIN
MISSING
NOT_TESTED
```

and assign:

```text
importance:
CRITICAL / HIGH / MEDIUM / LOW

confidence:
HIGH / MEDIUM / LOW
```

The final output must allow a user who does not read the underlying Python
code to understand:

```text
what is already correct;
what is inconsistent;
how much each inconsistency may affect the prediction;
which issue should be addressed first;
what remains unknown;
whether the current result is suitable for physics interpretation.
```

The Skill must not attempt to make the result numerically agree with a
published benchmark by tuning parameters.

A successful audit is not defined by

```text
prediction == benchmark
```

but by producing a traceable physical explanation of the relation between the
current prediction and the benchmark.

For example, if

```text
current prediction = 150 events
published benchmark = 347 events
```

the required outcome is not to rescale 150 to 347.

The required outcome is a decomposition such as:

```text
current dataset definition                    150

exposure-definition difference                major effect
detector-inventory difference                 major effect
target-composition difference                 moderate effect
source-model difference                       moderate effect
detector-response difference                  remaining effect

final reproducible prediction                 ...

published benchmark                           347
```

where every step is supported by a documented physics input or a clearly
labelled diagnostic calculation.

The final audit must therefore provide exactly one recommended next action,
for example:

```text
REBUILD_OFFICIAL_DATASET
CHECK_EXPOSURE_CONTRACT
CHECK_OUTPUT_UNITS
CHECK_SOURCE_MODEL
CHECK_TARGET_COMPOSITION
CHECK_DETECTOR_RESPONSE
REQUEST_MISSING_REFERENCE
NO_ACTION_REQUIRED
```

The user should be able to select that action without inspecting or modifying
the underlying production code.


## Concrete Objective

The goal of this Skill is not merely to verify that the existing code runs
successfully.

Its primary goal is to determine whether the implemented physics model
corresponds to the physical experiment or benchmark that the user intends to
reproduce.

Given:

```text
current implementation
current numerical prediction
user-supplied physics document
official or independent experimental references
published numerical benchmarks
```

the Skill must answer the following questions in order:

```text
1. What physical dataset does the current code actually implement?

2. What physical dataset does the external benchmark describe?

3. Are these two definitions the same?

4. If they are different, which physical inputs are different?

5. If they are intended to be the same but the numerical results disagree,
   which physics layer is most likely responsible?

6. How large is the expected numerical effect of each identified difference?

7. Which issue should be checked or repaired first?

8. What level of experimental reproduction can currently be claimed?
```

The audit must reduce the discrepancy into physically interpretable layers:

```text
dataset identity
observable and units
exposure and normalization
detector inventory
source
target composition
kinematics
cross section
detector response
analysis window and binning
statistics
```

For each layer, the Skill must classify the result as:

```text
CONSISTENT
DIFFERENT
UNCERTAIN
MISSING
NOT_TESTED
```

and assign:

```text
importance:
CRITICAL / HIGH / MEDIUM / LOW

confidence:
HIGH / MEDIUM / LOW
```

The final output must allow a user who does not read the underlying Python
code to understand:

```text
what is already correct;
what is inconsistent;
how much each inconsistency may affect the prediction;
which issue should be addressed first;
what remains unknown;
whether the current result is suitable for physics interpretation.
```

The Skill must not attempt to make the result numerically agree with a
published benchmark by tuning parameters.

A successful audit is not defined by

```text
prediction == benchmark
```

but by producing a traceable physical explanation of the relation between the
current prediction and the benchmark.

For example, if

```text
current prediction = 150 events
published benchmark = 347 events
```

the required outcome is not to rescale 150 to 347.

The required outcome is a decomposition such as:

```text
current dataset definition                    150

exposure-definition difference                major effect
detector-inventory difference                 major effect
target-composition difference                 moderate effect
source-model difference                       moderate effect
detector-response difference                  remaining effect

final reproducible prediction                 ...

published benchmark                           347
```

where every step is supported by a documented physics input or a clearly
labelled diagnostic calculation.

The final audit must therefore provide exactly one recommended next action,
for example:

```text
REBUILD_OFFICIAL_DATASET
CHECK_EXPOSURE_CONTRACT
CHECK_OUTPUT_UNITS
CHECK_SOURCE_MODEL
CHECK_TARGET_COMPOSITION
CHECK_DETECTOR_RESPONSE
REQUEST_MISSING_REFERENCE
NO_ACTION_REQUIRED
```

The user should be able to select that action without inspecting or modifying
the underlying production code.

## Concrete Objective

The goal of this Skill is not merely to verify that the existing code runs
successfully.

Its primary goal is to determine whether the implemented physics model
corresponds to the physical experiment or benchmark that the user intends to
reproduce.

Given:

```text
current implementation
current numerical prediction
user-supplied physics document
official or independent experimental references
published numerical benchmarks
```

the Skill must answer the following questions in order:

```text
1. What physical dataset does the current code actually implement?

2. What physical dataset does the external benchmark describe?

3. Are these two definitions the same?

4. If they are different, which physical inputs are different?

5. If they are intended to be the same but the numerical results disagree,
   which physics layer is most likely responsible?

6. How large is the expected numerical effect of each identified difference?

7. Which issue should be checked or repaired first?

8. What level of experimental reproduction can currently be claimed?
```

The audit must reduce the discrepancy into physically interpretable layers:

```text
dataset identity
observable and units
exposure and normalization
detector inventory
source
target composition
kinematics
cross section
detector response
analysis window and binning
statistics
```

For each layer, the Skill must classify the result as:

```text
CONSISTENT
DIFFERENT
UNCERTAIN
MISSING
NOT_TESTED
```

and assign:

```text
importance:
CRITICAL / HIGH / MEDIUM / LOW

confidence:
HIGH / MEDIUM / LOW
```

The final output must allow a user who does not read the underlying Python
code to understand:

```text
what is already correct;
what is inconsistent;
how much each inconsistency may affect the prediction;
which issue should be addressed first;
what remains unknown;
whether the current result is suitable for physics interpretation.
```

The Skill must not attempt to make the result numerically agree with a
published benchmark by tuning parameters.

A successful audit is not defined by

```text
prediction == benchmark
```

but by producing a traceable physical explanation of the relation between the
current prediction and the benchmark.

For example, if

```text
current prediction = 150 events
published benchmark = 347 events
```

the required outcome is not to rescale 150 to 347.

The required outcome is a decomposition such as:

```text
current dataset definition                    150

exposure-definition difference                major effect
detector-inventory difference                 major effect
target-composition difference                 moderate effect
source-model difference                       moderate effect
detector-response difference                  remaining effect

final reproducible prediction                 ...

published benchmark                           347
```

where every step is supported by a documented physics input or a clearly
labelled diagnostic calculation.

The final audit must therefore provide exactly one recommended next action,
for example:

```text
REBUILD_OFFICIAL_DATASET
CHECK_EXPOSURE_CONTRACT
CHECK_OUTPUT_UNITS
CHECK_SOURCE_MODEL
CHECK_TARGET_COMPOSITION
CHECK_DETECTOR_RESPONSE
REQUEST_MISSING_REFERENCE
NO_ACTION_REQUIRED
```

The user should be able to select that action without inspecting or modifying
the underlying production code.

## Concrete Objective

The goal of this Skill is not merely to verify that the existing code runs
successfully.

Its primary goal is to determine whether the implemented physics model
corresponds to the physical experiment or benchmark that the user intends to
reproduce.

Given:

```text
current implementation
current numerical prediction
user-supplied physics document
official or independent experimental references
published numerical benchmarks
```

the Skill must answer the following questions in order:

```text
1. What physical dataset does the current code actually implement?

2. What physical dataset does the external benchmark describe?

3. Are these two definitions the same?

4. If they are different, which physical inputs are different?

5. If they are intended to be the same but the numerical results disagree,
   which physics layer is most likely responsible?

6. How large is the expected numerical effect of each identified difference?

7. Which issue should be checked or repaired first?

8. What level of experimental reproduction can currently be claimed?
```

The audit must reduce the discrepancy into physically interpretable layers:

```text
dataset identity
observable and units
exposure and normalization
detector inventory
source
target composition
kinematics
cross section
detector response
analysis window and binning
statistics
```

For each layer, the Skill must classify the result as:

```text
CONSISTENT
DIFFERENT
UNCERTAIN
MISSING
NOT_TESTED
```

and assign:

```text
importance:
CRITICAL / HIGH / MEDIUM / LOW

confidence:
HIGH / MEDIUM / LOW
```

The final output must allow a user who does not read the underlying Python
code to understand:

```text
what is already correct;
what is inconsistent;
how much each inconsistency may affect the prediction;
which issue should be addressed first;
what remains unknown;
whether the current result is suitable for physics interpretation.
```

The Skill must not attempt to make the result numerically agree with a
published benchmark by tuning parameters.

A successful audit is not defined by

```text
prediction == benchmark
```

but by producing a traceable physical explanation of the relation between the
current prediction and the benchmark.

For example, if

```text
current prediction = 150 events
published benchmark = 347 events
```

the required outcome is not to rescale 150 to 347.

The required outcome is a decomposition such as:

```text
current dataset definition                    150

exposure-definition difference                major effect
detector-inventory difference                 major effect
target-composition difference                 moderate effect
source-model difference                       moderate effect
detector-response difference                  remaining effect

final reproducible prediction                 ...

published benchmark                           347
```

where every step is supported by a documented physics input or a clearly
labelled diagnostic calculation.

The final audit must therefore provide exactly one recommended next action,
for example:

```text
REBUILD_OFFICIAL_DATASET
CHECK_EXPOSURE_CONTRACT
CHECK_OUTPUT_UNITS
CHECK_SOURCE_MODEL
CHECK_TARGET_COMPOSITION
CHECK_DETECTOR_RESPONSE
REQUEST_MISSING_REFERENCE
NO_ACTION_REQUIRED
```

The user should be able to select that action without inspecting or modifying
the underlying production code.

## Purpose

Perform an external physics audit of an already implemented CEvNS dataset.

This Skill answers:

1. What physical experiment does the current code actually implement?
2. What independent experimental or published benchmark should it reproduce?
3. Are they the same physical dataset?
4. If the prediction disagrees with the benchmark, which physics layer is responsible?
5. What should the user inspect or repair next?

This Skill is diagnostic first.

Do not modify production physics code during the initial audit.

Do not rescale the prediction to match a published benchmark.

---

# Invocation

Invoke after a validated Slow calculation exists.

Typical entry condition:

```text
Gate L = PASS
```

but an external benchmark is missing, not checked, or disagrees with the prediction.

Possible audit results:

```text
PASS
MISMATCH
BLOCKED
```

Definitions:

```text
PASS:
current implementation is consistent with the declared external benchmark

MISMATCH:
internal implementation is self-consistent but does not reproduce
the external physical dataset or benchmark

BLOCKED:
insufficient independent information exists to perform the comparison
```

---

# 1. Read current implementation

Read the complete dataset run record.

At minimum inspect:

```text
00_INPUT_INVENTORY.md
00_IMPLEMENTATION_MANIFEST.yaml
experiment.yaml

03_SOURCE.md
target report if present
04_THEORY_RESPONSE.md
05_KINEMATICS_CROSS_SECTION.md
06_DETECTOR_RESPONSE.md
07_SLOW_COUNTS.md
```

If Fast already exists, it may be inspected only as an internal consistency check.

Do not use Fast agreement with Slow as evidence that the physical experiment
is correct.

Inspect the actual current production callables used by the dataset.

Do not infer the implemented physics from filenames alone.

---

# 2. Reconstruct the current physical contract

Create a concise CURRENT CONTRACT containing:

```text
dataset identity
run period
detectors
target composition
active masses
exposures
source type
source normalization
source spectrum
fission fractions or source components
true-energy support
reconstructed-energy support
thresholds
binning
quenching
resolution
efficiency
statistical data mode
output units
Slow total prediction
```

For every field record:

```text
value
unit
source file
implementation symbol
```

The goal is to describe the physics without requiring the user to read Python.

---

# 3. Identify the intended physical claim

Determine whether the dataset intends to reproduce:

```text
OFFICIAL_EXPERIMENT
PHENOMENOLOGY_MODEL
LEGACY_CODE
PAPER_FIGURE
USER_DEFINED_MODEL
UNKNOWN
```

Do not infer OFFICIAL_EXPERIMENT merely from the experiment name.

For example:

```text
conus_plus_ge73_pheno
```

may be a phenomenological model rather than the official detector-level
CONUS+ analysis.

Record:

```text
current_intent:
intended_claim:
same_physical_dataset: YES / NO / UNCERTAIN
```

If the current implementation and the benchmark correspond to different
datasets, this is a major audit finding.

---

# 4. Find independent benchmarks

Search the supplied experiment paper and explicitly referenced sources.

When internet access is permitted, inspect the official experiment paper and
its supplemental material.

Prefer benchmark sources in this order:

```text
1. official collaboration paper
2. official supplementary material
3. official public data release
4. experiment calibration paper
5. collaboration conference note
6. independent phenomenology paper
7. legacy code output
```

Record benchmarks such as:

```text
predicted SM total
measured signal
exposure
detector masses
thresholds
published reconstructed spectrum
published recoil spectrum
source normalization
source spectrum
best-fit normalization
likelihood benchmark
```

For every benchmark record:

```text
value
unit
paper/reference
section/table/figure
directly published or inferred
confidence
```

Never use a digitized figure as production input.

Digitized curves may only be used for validation.

---

# 5. Build a contract comparison

Compare CURRENT CONTRACT with EXTERNAL CONTRACT.

Use this table:


| Physics layer | Current implementation | External reference | Match | Importance | Confidence |
| ------------- | ---------------------- | ------------------ | ----- | ---------- | ---------- |

Required layers:

```text
dataset identity
run period
detector inventory
exposure
active mass
target composition
source normalization
source spectrum
source composition
kinematics
cross section
quenching
resolution
efficiency
thresholds
analysis window
binning
observable definition
output units
statistical data mode
```

Match status:

```text
MATCH
DIFFERENT
MISSING_CURRENT
MISSING_REFERENCE
UNCERTAIN
NOT_APPLICABLE
```

Importance:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

---

# 6. Build a normalization ledger

This is mandatory.

Trace every multiplicative normalization factor from source to final events.

Use:

```text
source flux
× source geometry if applicable
× nuclei per kg
× isotope abundance
× detector mass / exposure
× live time
× seconds per day
× differential cross section
× detector efficiency
× bin integration
```

For each factor record:


| Factor | Value | Unit | Applied where | Number of applications | Expected |
| ------ | ----: | ---- | ------------- | ---------------------: | -------: |

Explicitly test for:

```text
mass applied twice
live time applied twice
exposure already mass × time
source geometry applied twice
seconds/day omitted
seconds/day applied twice
isotope abundance omitted
isotope abundance applied twice
efficiency already unfolded from data
flux already evaluated at detector position
```

Output:

```text
NORMALIZATION_LEDGER_STATUS:
PASS / SUSPICIOUS / FAIL
```

---

# 7. Build a unit ledger

Trace the unit at every major interface.

At minimum:

```text
dPhi/dE_nu
dSigma/dT
nuclei/kg
exposure
dN/dT
response density
dN/dE_reco
counts/bin
experimental plotted quantity
```

Use a table:


| Quantity | Current unit | Expected unit | Conversion | Status |
| -------- | ------------ | ------------- | ---------- | ------ |

Specially inspect whether published points are:

```text
events
events/bin
events/kg
events/kg/day
events/kg/(bin width)
excess counts
rate
```

Do not compare quantities with different units merely because their numerical
values look similar.

---

# 8. Numerical sanity checks

Automatically compute:

```text
current total event prediction
event rate per kg day
event rate per detector if applicable
event rate per target isotope
fraction of events in first bins
fraction above threshold
integrated source flux
average source energy
maximum recoil
response normalization
efficiency range
```

If an external total benchmark exists, compute:

```text
absolute difference
relative difference
difference divided by published uncertainty
```

Example:

```text
N_current = ...
N_reference = ...

delta = N_current - N_reference
relative_delta = delta / N_reference
pull = delta / sigma_reference
```

---

# 9. One-factor diagnostic estimates

For every identified contract difference, estimate its likely numerical impact
without altering production reference files.

Use controlled diagnostic calculations where possible.

Examples:

## Exposure

Compute:

```text
N_scaled =
N_current × exposure_reference / exposure_current
```

Label explicitly:

```text
DIAGNOSTIC ONLY
```

Do not save this as the official prediction.

## Source normalization

If only normalization differs, compute the expected normalization ratio.

## Target composition

If all isotope Responses exist, compute a diagnostic natural-isotope sum.

## Threshold

Re-integrate the validated reconstructed spectrum using the alternative
threshold if mathematically valid.

## Analysis window

Integrate the existing reconstructed spectrum over the reference analysis
window if support exists.

Every test must record:

```text
baseline
diagnostic change
new result
ratio to baseline
distance from benchmark before
distance from benchmark after
```

Do not tune free parameters.

---

# 10. Rank likely causes

For every mismatch assign:

```text
severity
confidence
estimated impact
evidence
```

Severity:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

Confidence:

```text
HIGH
MEDIUM
LOW
```

Rank issues using:

1. direct contradiction with official experiment definition;
2. expected numerical impact;
3. evidence quality;
4. whether it explains the sign of the discrepancy.

Do not rank speculative issues above documented contract differences.

---

# 11. Produce a user-friendly report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
PHYSICS_AUDIT.md
```

The report must be understandable without opening production code.

The first page must contain:

```text
DATASET
CURRENT PREDICTION
REFERENCE BENCHMARK
RELATIVE DIFFERENCE
INTERNAL VALIDATION STATUS
EXTERNAL PHYSICS STATUS
NUMBER OF CRITICAL ISSUES
NUMBER OF HIGH-PRIORITY ISSUES
RECOMMENDED NEXT CHECK
```

Example style:

```text
Current prediction:
150.49 events

Reference:
347 ± 59 events

Difference:
-56.6 %

Internal implementation:
PASS

External reproduction:
MISMATCH

Main finding:
The current implementation uses 119 kg day while the external analysis
uses 327 kg day.

This explains a large part of the discrepancy but not all of it.
```

---

# 12. Required issue cards

For every important issue generate a compact section:

```text
ISSUE 1 — Exposure

Status:
DIFFERENT

Current:
119 kg day

Reference:
327 kg day

Why it matters:
Event counts scale linearly with exposure.

Diagnostic result:
Current prediction = ...
Exposure-only diagnostic = ...
Reference = ...

Conclusion:
Exposure is definitely inconsistent, but exposure alone does / does not
explain the full discrepancy.

Recommended action:
Rebuild detector/exposure inventory.

User decision:
[ ] accept current phenomenology definition
[ ] create official detector-level definition
[ ] inspect more evidence
```

Create one card for each relevant layer.

---

# 13. Required physics issue order

Present issues in this order:

```text
1. dataset identity
2. observable and output unit
3. exposure and normalization
4. detector inventory
5. source
6. target composition
7. kinematics and cross section
8. detector response
9. analysis window and binning
10. statistics
```

This order is intended to prevent the user from debugging fine detector
effects before finding a factor-of-three exposure error.

---

# 14. Produce an automatic discrepancy tree

Include:

```text
Observed discrepancy
|
+-- Dataset identity
|
+-- Normalization
|   +-- exposure
|   +-- mass/live time
|   +-- source normalization
|   +-- nuclei/kg
|
+-- Source shape
|
+-- Target composition
|
+-- Cross section
|
+-- Detector
|   +-- threshold
|   +-- efficiency
|   +-- resolution
|   +-- quenching
|
+-- Observable / units
|
+-- Statistical definition
```

For every node mark:

```text
OK
DIFFERENT
UNKNOWN
NOT_TESTED
```

---

# 15. Create a diagnostic migration table

Generate:


| Step | Physics definition | Total prediction | Ratio to previous | Difference from benchmark |
| ---- | ------------------ | ---------------: | ----------------: | ------------------------: |

The first row must be the unchanged current implementation.

Subsequent rows may contain diagnostic-only one-factor changes.

Do not combine several undocumented changes in one row.

Do not overwrite any reference arrays.

---

# 16. Generate useful figures

When the required arrays exist, generate:

```text
audit_current_vs_reference_spectrum
audit_bin_ratio
audit_cumulative_events
audit_detector_components
audit_isotope_components
```

Only generate relevant figures.

Every figure must state its units.

Do not visually compare curves with inconsistent normalization without also
showing a normalized-shape comparison.

---

# 17. Final classification

Set:

```text
PHYSICS_AUDIT = PASS
```

when the current implementation and declared benchmark correspond to the same
dataset and agree within the declared validation tolerance.

Set:

```text
PHYSICS_AUDIT = MISMATCH
```

when the implementation is internally valid but one or more external physics
contracts disagree.

Set:

```text
PHYSICS_AUDIT = BLOCKED
```

when the necessary independent reference inputs cannot be established.

A MISMATCH does not mean that the existing code should be deleted.

It may mean that the code correctly implements a different phenomenological
dataset.

---

# 18. Do not repair automatically

During the first audit:

```text
do not modify source physics
do not modify target physics
do not modify detector response
do not modify Slow
do not modify reference arrays
do not modify Fast
do not modify statistics
```

Only diagnostic artifacts and reports may be created.

At the end recommend exactly one next action.

Examples:

```text
REBUILD_EXPOSURE_CONTRACT
REBUILD_OFFICIAL_DATASET
CHECK_SOURCE_MODEL
CHECK_TARGET_COMPOSITION
CHECK_DETECTOR_RESPONSE
CHECK_OUTPUT_UNITS
REQUEST_MISSING_REFERENCE
NO_ACTION_REQUIRED
```

Stop after the report.

---

# 19. Optional user-directed repair

Only after the user selects one issue may a repair run begin.

For a repair run:

1. back up every modified existing file;
2. modify only the selected physics layer;
3. rerun that layer's tests;
4. rerun Slow;
5. rerun Physics Audit;
6. report before/after numbers;
7. do not proceed automatically to another repair.

Produce:

```text
before
selected change
after
benchmark
remaining discrepancy
new recommended next action
```

The user should never need to inspect or edit the underlying Python code.

---

# Final response

Report only:

```text
dataset intent
current prediction
external benchmark
relative discrepancy
internal implementation status
external physics status
critical issues
high-priority issues
top diagnostic result
recommended next action
PHYSICS_AUDIT report path
```

Then stop.
