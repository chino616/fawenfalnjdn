---
name: cevns-detector-response
description: Implement and validate the experiment-specific mapping from true recoil to reconstructed observables, including quenching, resolution, efficiency, and migration.
---

# cevns-detector-response

## Purpose

Execute Phase 6.

Implement the detector-specific response:

```text
true recoil
→ mean reconstructed observable
→ stochastic resolution
→ efficiency
```

Detector Response is experimental input.

It is separate from the nuclear Response used by the theory and cross-section
layers.

This Skill does not calculate final Slow event counts.

## Preconditions

Require:

```text
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md

workflows/experiment-integration/templates/
06_DETECTOR_RESPONSE.md

workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md

workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml

workflows/experiment-integration/runs/<dataset_id>/
01_DATASET.md

workflows/experiment-integration/runs/<dataset_id>/
03_SOURCE.md

workflows/experiment-integration/runs/<dataset_id>/
04_THEORY_RESPONSE.md

workflows/experiment-integration/runs/<dataset_id>/
05_KINEMATICS_CROSS_SECTION.md

data/experiments/<dataset_id>/experiment.yaml
```

The Phase 0 inventory and manifest are authoritative for:

```text
reconstructed observable
quenching or yield
resolution
efficiency
migration
analysis bins
planned files
planned tests
```

Return to the original physics document only when the Phase 0 outputs contain
an explicit ambiguity or inconsistency.

## Procedure

### 1. Verify the approved detector-response contract

Confirm:

```text
true recoil variable and unit
reconstructed observable and unit
mean mapping
quenching or yield model
resolution model
efficiency model
efficiency domain
analysis window
binning
```

Do not introduce a new detector convention not approved in Phase 0.

### 2. Inspect the actual reference implementation

Inspect only the relevant detector-response and folding code identified by:

```text
CSI_REFERENCE_MAP.md
```

Normally inspect:

```text
src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py
src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py
src/cevns_pyeft/rates/counts.py
```

Record:

```text
actual files
actual symbols
function signatures
input units
return units
scalar and array behavior
broadcasting
response normalization
efficiency placement
binning convention
```

Use CsI only as an API and control-flow reference.

Do not copy:

```text
CsI quenching
CsI photoelectron conversion
CsI efficiency
CsI timing response
CsI detector parameters
a complete CsI Slow module
```

### 3. Select the implementation type

Use the approved Phase 0 classification:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

Use `CONFIG_ONLY` when generic detector-response models already represent the
complete experiment response.

Use `ADAPTER` when experiment-specific formulas are required.

Create the smallest implementation layer possible.

### 4. Materialize detector parameters

Store small scalar parameters in:

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
```

Use CSV or NPZ only for approved numerical curves or matrices.

Do not create a data table for a short analytic formula.

### 5. Implement the mean mapping

Implement:

```text
true recoil → mean reconstructed observable
```

The implementation may include:

```text
quenching
ionization yield
light yield
photoelectron conversion
calibration mapping
```

Validate physical units and the approved recoil domain.

Do not include resolution smearing or efficiency inside the mean mapping.

### 6. Implement the resolution model

Implement the approved stochastic width or migration model.

Reuse generic Gaussian or other shared probability distributions when
available.

Do not rewrite generic probability-density mathematics.

Require finite and positive resolution width over the approved domain.

### 7. Implement the response density

Implement:

```text
R(x_reco | T)
```

The response density must represent a probability density in the reconstructed
variable.

Its full-domain normalization must follow the approved detector model.

Do not renormalize only over the analysis window.

### 8. Implement efficiency

Implement the approved efficiency as a separate function.

State explicitly whether it depends on:

```text
true recoil
mean observable
reconstructed observable
```

Require:

```text
0 <= efficiency <= 1
```

Do not apply efficiency twice during later folding.

### 9. Define the public API

Follow the repository-native API.

When an experiment adapter is required, expose functions equivalent to:

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

Use actual repository naming after inspecting existing code.

The Detector Response API must not:

```text
load source flux
evaluate the cross section
apply exposure
integrate event counts
apply statistical data
```

### 10. Generate diagnostic artifacts

Create:

```text
runs/<dataset_id>/artifacts/detector_response_grid.csv

runs/<dataset_id>/figures/mean_mapping.png
runs/<dataset_id>/figures/mean_mapping.pdf

runs/<dataset_id>/figures/resolution_width.png
runs/<dataset_id>/figures/resolution_width.pdf

runs/<dataset_id>/figures/detector_response_slices.png
runs/<dataset_id>/figures/detector_response_slices.pdf

runs/<dataset_id>/figures/efficiency.png
runs/<dataset_id>/figures/efficiency.pdf
```

Use documented true-recoil and reconstructed-observable grids.

Figures must be reproducible from the saved grid.

### 11. Add focused tests

Test:

```text
mean-mapping units
mean-mapping physical range
mean-mapping monotonicity when required
positive resolution width
response-density nonnegativity
response-density normalization
response mean and width
efficiency range
efficiency domain
threshold or interpolation behavior
analysis bin edges
scalar input
array input
broadcasting
out-of-range behavior
```

Also test:

```text
Detector Response does not apply source flux
Detector Response does not call the cross section
Detector Response does not apply exposure
Detector Response does not calculate final binned counts
```

Do not relax tolerances or change experiment inputs merely to make tests pass.

### 12. Update the experiment specification

Only after all tests pass, update:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Record:

```text
detector-response status
detector-response callable
mean-mapping model
resolution model
efficiency model
data files
true variable and unit
reconstructed variable and unit
```

Do not mark Detector Response as implemented before validation passes.

### 13. Create the phase report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
06_DETECTOR_RESPONSE.md
```

Use:

```text
workflows/experiment-integration/templates/
06_DETECTOR_RESPONSE.md
```

Record:

```text
approved detector-response contract
reference implementation
classification
configuration fields
production implementation
public API
tests
diagnostic outputs
experiment.yaml update
Gate R
```

## Allowed outputs

Depending on the approved manifest, this Skill may create:

```text
src/cevns_pyeft/experiments/<family>/detector_response.py
tests/test_<dataset_id>_detector_response.py

data/experiments/<dataset_id>/detector_efficiency.csv
data/experiments/<dataset_id>/quenching_curve.csv
data/experiments/<dataset_id>/migration_matrix.npz

runs/<dataset_id>/artifacts/detector_response_grid.csv
runs/<dataset_id>/figures/*.png
runs/<dataset_id>/figures/*.pdf
runs/<dataset_id>/06_DETECTOR_RESPONSE.md
```

It may modify:

```text
data/experiments/<dataset_id>/experiment.yaml
```

after validation passes.

Create only files approved by the Phase 0 manifest.

## Backup rule

Before modifying an existing file, create a backup under:

```text
backup/<relative-original-path>
```

Record it in:

```text
backup/BACKUP_MANIFEST.md
```

Do not create backups for files that are only read.

## Prohibited actions

Do not:

```text
confuse Detector Response with nuclear Response
repeat the complete Phase 0 extraction
copy CsI detector parameters
rewrite generic probability distributions
renormalize migration only inside the analysis window
apply efficiency twice
apply exposure
load source flux
evaluate the differential cross section
calculate final Slow counts
implement Fast
implement statistics
modify registry.py without an approved condition
start the next Skill automatically
```

## Gate R

Gate R passes when:

1. the approved mean mapping is implemented;
2. the resolution model is implemented;
3. the response density is finite and correctly normalized;
4. efficiency acts on the correct variable;
5. efficiency remains between zero and one;
6. analysis binning is consistent;
7. migration outside the analysis window is handled correctly;
8. scalar, array, and broadcasting behavior pass;
9. diagnostic grids and figures are generated;
10. `experiment.yaml` points to the validated implementation;
11. no source, cross-section, exposure, or event-count logic is duplicated.

Set:

```text
PASS
```

or:

```text
BLOCKED
```

and record reasons.

## Final response

Report only:

```text
detector-response classification
reference implementation
configuration fields
production files
public API
tests run
diagnostic outputs
files modified
blockers
Gate R status
single next Skill
```

Then stop.

Do not execute the next Skill automatically.