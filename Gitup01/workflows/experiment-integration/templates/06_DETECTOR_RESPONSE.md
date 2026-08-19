# Phase 6 Detector Response

## 1. Purpose

Implement and validate the mapping from true nuclear recoil to the reconstructed
experimental observable:

```text
true recoil T
→ mean visible observable
→ stochastic detector response
→ efficiency
→ reconstructed observable
```

Detector Response is experiment-specific input.

It is not the nuclear Response used by the theory and cross-section layers.

This phase does not calculate final binned event counts.

---

## 2. Inputs

```text
dataset_id:
input_inventory:
implementation_manifest:
experiment_spec:
true_recoil_variable:
reconstructed_observable:
```

Required previous state:

```text
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
```

Use the detector-response definition approved in Phase 0.

Do not re-extract the complete physics document.

---

## 3. Approved Detector-Response Contract

### Mean mapping

```text
true variable:
true-variable unit:
mean reconstructed variable:
reconstructed-variable unit:
quenching or yield model:
model parameters:
valid recoil range:
```

The mean mapping is:

```text
T → x_mean(T)
```

### Stochastic response

```text
response model:
response density:
resolution model:
resolution parameters:
normalization domain:
```

The response density is:

```text
R(x_reco | T)
```

### Efficiency

```text
efficiency model:
efficiency variable:
efficiency unit:
efficiency parameters:
efficiency domain:
```

State explicitly whether efficiency acts on:

```text
true recoil
mean visible observable
reconstructed observable
```

### Analysis binning

```text
bin variable:
bin unit:
bin edges:
number of bins:
edge convention:
```

Binning should normally be reused from `experiment.yaml`.

---

## 4. Reference Code

Inspect the actual detector-response and folding interfaces listed in:

```text
CSI_REFERENCE_MAP.md
```

Relevant references normally include:

```text
src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py
src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py
src/cevns_pyeft/rates/counts.py
```

Record the actual implementation:

| Role | File | Symbol |
|---|---|---|
| Mean observable mapping | | |
| Resolution model | | |
| Response density | | |
| Efficiency | | |
| Folding or bin integration | | |
| Existing tests | | |

### Relevant signatures

Copy only short, relevant signatures or fragments.

```python
# Reference file:
# Reference symbol:

```

Record the verified contract:

```text
input units:
returned units:
scalar behavior:
array behavior:
broadcasting:
normalization convention:
efficiency placement:
bin-edge convention:
```

Do not copy an entire CsI module or any CsI physical parameters.

---

## 5. Configuration and Code Decision

### Configuration fields

Store small scalar experiment inputs in:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Examples:

```text
quenching parameters
yield parameters
resolution parameters
threshold
efficiency parameters
analysis window
```

### Numerical data

Use CSV or NPZ only when the response requires numerical tables, such as:

```text
measured efficiency curve
measured quenching curve
migration matrix
calibration covariance
```

### Code classification

Select one:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

Use `CONFIG_ONLY` when existing generic models can represent the complete
detector response using configuration values.

Use `ADAPTER` when experiment-specific formulas are required.

Typical adapter logic includes:

```text
quenching or yield formula
mean reconstructed-energy mapping
experiment-specific resolution width
experiment-specific efficiency function
```

Do not rewrite generic Gaussian functions, numerical integration, or bin
summation when reusable implementations already exist.

---

## 6. Production Implementation

### Files reused

```text
```

### Files created

Possible production outputs:

```text
src/cevns_pyeft/experiments/<family>/detector_response.py
tests/test_<dataset_id>_detector_response.py
runs/<dataset_id>/06_DETECTOR_RESPONSE.md
```

Possible numerical data:

```text
data/experiments/<dataset_id>/detector_efficiency.csv
data/experiments/<dataset_id>/quenching_curve.csv
data/experiments/<dataset_id>/migration_matrix.npz
```

Create only files approved by the Phase 0 manifest.

### Files modified

Normally:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Update it only after validation passes.

### Protected files

```text
existing CsI detector-response implementations
existing Ar detector-response implementations
shared theory modules
shared nuclear-response modules
shared cross-section modules
source modules
Slow modules
Fast modules
statistics modules
registry.py
```

---

## 7. Public API

Follow the actual repository naming convention.

When an experiment-specific adapter is needed, use an interface equivalent to:

```python
def mean_reconstructed_observable(true_recoil, experiment_spec):
    ...


def resolution_width(mean_observable, experiment_spec):
    ...


def response_density(
    reconstructed_observable,
    true_recoil,
    experiment_spec,
):
    ...


def efficiency(reconstructed_observable, experiment_spec):
    ...
```

These names are provisional until the repository API is inspected.

Record:

```text
implementation file:
public symbols:
input types:
input units:
returned types:
returned units:
scalar behavior:
array behavior:
broadcasting:
out-of-range behavior:
```

The response functions must not apply exposure, source flux, or cross section.

---

## 8. Diagnostic Outputs

Generate a documented validation grid:

```text
runs/<dataset_id>/artifacts/detector_response_grid.csv
```

Preferred columns:

```text
true_recoil
mean_reconstructed_observable
resolution_width
selected_reconstructed_observable
response_density
efficiency
```

Generate:

```text
runs/<dataset_id>/figures/mean_mapping.png
runs/<dataset_id>/figures/mean_mapping.pdf

runs/<dataset_id>/figures/resolution_width.png
runs/<dataset_id>/figures/resolution_width.pdf

runs/<dataset_id>/figures/detector_response_slices.png
runs/<dataset_id>/figures/detector_response_slices.pdf

runs/<dataset_id>/figures/efficiency.png
runs/<dataset_id>/figures/efficiency.pdf
```

The response-slice figure should show:

```text
R(x_reco | T)
```

for several documented true-recoil values.

Diagnostic files belong under the workflow run directory and must not be loaded
by production runtime code.

---

## 9. Tests

### Mean-mapping tests

```text
correct units
finite values
physical range
monotonicity when physically required
scalar and array behavior
```

### Resolution tests

```text
finite width
positive width
correct units
stable low-energy behavior
```

### Response-density tests

```text
finite values
nonnegative density
normalization over the full physical reconstructed domain
correct mean
correct width
scalar and array behavior
```

Do not renormalize the response only inside the analysis window.

Events migrating outside the analysis window remain lost unless the approved
detector model explicitly says otherwise.

### Efficiency tests

```text
finite values
0 <= efficiency <= 1
correct efficiency variable
correct threshold or interpolation
correct out-of-range behavior
```

### Binning tests

```text
strictly increasing bin edges
correct number of bins
correct units
correct edge convention
```

### Interface tests

```text
production callable loads
experiment.yaml parameters are consumed
no exposure factor is applied
no source or cross-section calculation is performed
diagnostic grid reproduces the figures
```

---

## 10. Experiment-Spec Update

After all Detector Response tests pass, update:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Record:

```text
detector-response status:
detector-response callable:
mean-mapping model:
resolution model:
efficiency model:
response data files:
true variable:
reconstructed variable:
units:
```

Do not mark Detector Response as implemented before validation passes.

---

## 11. Gate R

Gate R passes when:

```text
the approved mean mapping is implemented
the resolution model is implemented
the response density is correctly normalized
the efficiency acts on the correct variable
efficiency remains within [0, 1]
analysis binning is consistent
migration outside the analysis window is handled correctly
diagnostic grids and figures are generated
the public API is loadable
no source, cross-section, exposure, or event-count logic is duplicated
```

```text
status: PASS / BLOCKED
reasons:
next_skill:
```

Stop after Gate R.