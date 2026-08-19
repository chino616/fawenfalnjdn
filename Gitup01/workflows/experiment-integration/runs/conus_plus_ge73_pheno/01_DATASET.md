# Phase 1 Dataset Report: conus_plus_ge73_pheno

## Inputs

- Physics document:
  `docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf`
- Phase 0 inventory:
  `workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md`
- Phase 0 manifest:
  `workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml`
- Template:
  `workflows/experiment-integration/templates/01_DATASET.md`

## User Document Definition

- Dataset ID: `conus_plus_ge73_pheno`
- Experiment family: CONUS+ phenomenology
- Dataset count: one effective detector dataset
- Detector: effective `Ge73`
- Target: `73Ge` only
- Exposure: `119 kg day`, already mass times live time
- Observable: reconstructed electron-equivalent energy `E_reco`
- Binning: `160 <= E_reco < 350 eVee`, 10 eVee width, 19 bins
- Statistical data mode: `background_subtracted_excess`

This is not the official CONUS+ C2/C3/C5 detector-by-detector model.

## CsI Local Reference

Read only for dataset/spec/discovery shape conventions:

- `src/cevns_pyeft/experiments/base.py`
- `src/cevns_pyeft/experiments/registry.py`
- `src/cevns_pyeft/experiments/specs.py`
- `schemas/experiment.schema.json`

No CsI physics parameters were copied.

## Files Created

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
data/experiments/conus_plus_ge73_pheno/README.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/01_DATASET.md
```

## Files Modified

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
backup/BACKUP_MANIFEST.md
```

## Files Not Created In Phase 1

```text
data/experiments/conus_plus_ge73_pheno/mueller_coefficients.csv
data/experiments/conus_plus_ge73_pheno/kopeikin_low_energy_spectrum.csv
data/experiments/conus_plus_ge73_pheno/excess_counts.csv
src/cevns_pyeft/experiments/conus/source.py
src/cevns_pyeft/experiments/conus/detector_response.py
src/cevns_pyeft/experiments/conus/slow_counts_conus_plus_ge73_pheno.py
src/cevns_pyeft/experiments/conus/fast_cumulative_conus_plus_ge73_pheno.py
src/cevns_pyeft/experiments/conus/fast_kernel_conus_plus_ge73_pheno.py
src/cevns_pyeft/experiments/conus/statistics_conus_plus_ge73_pheno.py
```

## Must Not Modify

```text
src/cevns_pyeft/experiments/registry.py
src/cevns_pyeft/theory/
src/cevns_pyeft/nuclear/
src/cevns_pyeft/rates/
src/cevns_pyeft/kernels/
src/cevns_pyeft/experiments/coherent/
tests/reference_fast_split/
```

## Dataset Spec Summary

The Phase 1 `experiment.yaml` includes:

- required discovery fields: `dataset_name`, `source_type`, `target_mode`
- dataset ID and family
- provenance and workflow run path
- effective `Ge73` detector identity
- `119 kg day` exposure semantics
- rule-based 160-350 eVee, 10 eVee, 19-bin binning
- `background_subtracted_excess` statistical data mode
- expected output axis and shape
- `Ge73` target nucleus config
- placeholder future callable paths
- planned future data file paths

## Checks Run

```text
PyYAML parse of experiment.yaml and Phase 0 manifest
cevns_pyeft.experiments.specs.load_experiment_spec("conus_plus_ge73_pheno")
cevns_pyeft.experiments.registry.list_experiments()
manual schema-required-field check: dataset_name, source_type, target_mode
manual dataset checks: 19 bins, 160-350 eVee, Ge73 target, background_subtracted_excess mode
```

## Results

- `experiment.yaml` parses with PyYAML.
- Phase 0 manifest parses with PyYAML.
- `load_experiment_spec("conus_plus_ge73_pheno")` returns:
  - `dataset_name`: `conus_plus_ge73_pheno`
  - `source_type`: `reactor`
  - `target_mode`: `Ge73_only`
- `list_experiments()` includes `conus_plus_ge73_pheno`.
- Required schema fields are present: `dataset_name`, `source_type`,
  `target_mode`.
- Dataset-specific checks passed:
  - `binning.number_of_bins == 19`
  - `analysis_window_evee == [160, 350]`
  - `target.response_key == Ge73`
  - `statistical_data_mode == background_subtracted_excess`
- Existing `tests/test_experiment_specs.py` was run and fails only because it
  still asserts the previously deleted `conus_plus_2025_*` and
  `conus_legacy_*` specs. That stale test cleanup is recorded for the later
  validation/registry phase.
- No CSV, NPY, NPZ, source, detector-response, Slow, Fast, statistics, or
  registry files were created or modified in Phase 1.

## Gate D0

```text
PASS
```

## Next Skill

```text
cevns-target
```

Do not execute the next Skill automatically.
