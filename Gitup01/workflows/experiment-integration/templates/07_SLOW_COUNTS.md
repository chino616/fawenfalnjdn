# Phase 7 Slow Counts

## 1. Purpose

Implement the authoritative direct-integration event prediction:

```text
source flux
× differential cross section
× target normalization
→ true recoil spectrum
→ detector-response folding
→ reconstructed bin counts
```

Slow is the numerical reference for all Fast implementations.

It must not import or depend on Fast caches, kernels, templates, or surrogate
models.

---

## 2. Inputs

```text
dataset_id:
experiment_spec:
source_report:
theory_response_report:
cross_section_report:
detector_response_report:
```

Required gates:

```text
Gate D0 = PASS
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
Gate R = PASS
```

For a configuration-only target, require documented target readiness instead of
a separate Target implementation.

---

## 3. Reference Code

Inspect the actual Slow implementations listed in `CSI_REFERENCE_MAP.md`.

| Role | File | Symbol |
|---|---|---|
| Dataset-level Slow callable | | |
| Source integration | | |
| Differential cross section | | |
| Detector-response folding | | |
| Bin integration | | |
| Existing Slow tests | | |

Record the verified call chain:

```text
public Slow callable
→ source callable
→ shared cross section
→ true-recoil integration
→ detector response
→ reconstructed-bin integration
```

Copy only short signatures or relevant fragments.

```python
# Reference file:
# Reference symbol:

```

Record:

```text
input coefficients:
experiment-spec input:
model selector:
kinematic selector:
return type:
return axes:
return shape:
return unit:
component behavior:
```

Do not copy a complete CsI or Ar Slow module.

---

## 4. Authoritative Calculation

### True-recoil kernel

Define:

```text
S(T) = integral dE_nu [dPhi/dE_nu] [d sigma/dT]
```

Record:

```text
E_nu support:
T support:
cross-section model:
kinematic convention:
integration algorithm:
relative tolerance:
absolute tolerance:
maximum recursion or subdivision:
```

### Target-time normalization

Record:

```text
nuclei per kilogram:
exposure:
seconds per day:
normalization factor:
```

The Slow calculation applies target number and exposure exactly once.

Fast and Statistics must not apply them again.

### Detector folding

Define:

```text
dN/dx_reco =
efficiency(x_reco)
× integral dT [dN_true/dT] R(x_reco | T)
```

Record:

```text
true-recoil range:
reconstructed range:
response domain:
efficiency domain:
integration algorithm:
tolerances:
```

Do not renormalize detector migration inside the analysis window.

### Bin counts

Define:

```text
N_i = integral_bin_i dx_reco dN/dx_reco
```

Record:

```text
bin edges:
number of bins:
edge convention:
output unit:
```

---

## 5. Public API

Follow the actual repository API.

When a dataset wrapper is required, use a contract equivalent to:

```python
def slow_counts(
    coefficients,
    experiment_spec,
    *,
    cross_section_model="full_response",
    kinematics="publication_reproduction",
    return_components=False,
):
    ...
```

The actual name must follow repository conventions.

Required output:

```text
counts_total
```

Optional component outputs:

```text
counts_by_detector
counts_by_target
counts_by_source
```

Omit inapplicable axes, but document them explicitly.

---

## 6. Production Files

### Create

```text
src/cevns_pyeft/experiments/<family>/slow_counts_<dataset_id>.py
tests/test_<dataset_id>_slow_counts.py
tests/reference_<dataset_id>/slow_reference.npy
runs/<dataset_id>/07_SLOW_COUNTS.md
```

### Diagnostic artifacts

```text
runs/<dataset_id>/artifacts/true_recoil_spectrum.csv
runs/<dataset_id>/artifacts/reconstructed_spectrum.csv
runs/<dataset_id>/artifacts/slow_bin_counts.csv
runs/<dataset_id>/artifacts/slow_convergence.csv

runs/<dataset_id>/figures/true_recoil_spectrum.png
runs/<dataset_id>/figures/reconstructed_spectrum.png
runs/<dataset_id>/figures/slow_bin_counts.png
```

PDF copies may also be generated.

### Modify

Update `experiment.yaml` only after Slow validation passes.

### Must not modify

```text
shared theory
shared nuclear Response data
source implementation
shared cross-section formulas
detector-response physics
existing Slow reference arrays
Fast implementation
statistics implementation
```

---

## 7. Tests

Required tests:

```text
public callable loads
output shape matches dataset bins
all counts are finite
total physical bin counts are nonnegative
component sums reproduce total
exposure is applied exactly once
units are consistent
physical support is respected
scalar coefficient input works
supported complex coefficients work
Slow has no Fast dependency
```

Numerical validation:

```text
source-integration convergence
true-recoil integration convergence
reconstructed-energy integration convergence
grid or tolerance refinement
independent benchmark point
saved reference reproducibility
```

For model selectors:

```text
full_response uses nuclear Response and not Helm
helm_sm uses Helm and not full nuclear Response
```

Do not replace the Slow reference merely because later Fast results disagree.

---

## 8. Numerical Results

Record:

```text
total predicted events:
counts by bin:
minimum bin count:
maximum bin count:
true-recoil integral:
reconstructed-spectrum integral:
sum of bin counts:
migration outside analysis window:
convergence residuals:
runtime:
```

Document every coefficient point used to generate a reference array.

---

## 9. Gate L

Gate L passes when:

```text
the direct integration follows the approved physical chain
output shape and units are correct
exposure is counted exactly once
component sums pass
integration convergence passes
diagnostic spectra and bin counts are generated
the reference array is independently generated
Slow has no dependency on Fast
```

```text
status: PASS / BLOCKED
reasons:
next_skill:
```

Stop after Gate L.