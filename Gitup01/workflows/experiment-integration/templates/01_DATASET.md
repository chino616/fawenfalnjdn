# Phase 1 Dataset Report Template

## Purpose

Record how the approved Phase 0 dataset plan was materialized as a runtime
experiment specification.

This report does not repeat the full experiment-document extraction.

## Phase 0 inputs

```text
dataset_id:
input_inventory:
implementation_manifest:
Gate I status:
```

## Approved dataset contract

```text
experiment_family:
run_period:
detector_configuration:
source_configuration:
target_configuration:
statistical_data_mode:
```

## Observable contract

```text
true_observables:
reconstructed_observables:
output_axes:
output_shape:
output_unit:
```

## Binning

```text
mode:
minimum:
maximum:
width:
number_of_bins:
unit:
edge_convention:
edge_file:
```

Use only the fields relevant to the selected binning mode.

## Static dataset fields

```text
detectors:
targets:
response_keys:
exposure:
exposure_unit:
exposure_semantics:
analysis_threshold:
analysis_window:
```

## Callable placeholders

| Module | Status | Planned callable | Planned file | Implementation phase |
|---|---|---|---|---|
| source | | | | |
| detector response | | | | |
| slow counts | | | | |
| fast counts | | | | |
| statistics | | | | |

## Mapping to experiment.yaml

| Phase 0 field | experiment.yaml field | Value | Validation |
|---|---|---|---|

## Files

### Reused

```text
```

### Created

```text
data/experiments/<dataset_id>/experiment.yaml
data/experiments/<dataset_id>/README.md
runs/<dataset_id>/01_DATASET.md
```

### Modified

```text
```

### Conditional modifications

```text
```

### Must not modify

```text
existing experiment implementations
existing experiment reference arrays
shared theory modules
shared nuclear-response modules
shared rates modules
shared kernel modules
```

## Schema validation

```text
schema:
command:
result:
```

## Loader validation

```text
loader:
command:
result:
```

## Consistency checks

```text
dataset ID unique:
repository-relative paths:
binning valid:
bin count:
output shape:
statistical data mode valid:
callable placeholders accepted:
later-phase code created:
```

## Gate D0

```text
status:
reasons:
```

Stop after Gate D0.