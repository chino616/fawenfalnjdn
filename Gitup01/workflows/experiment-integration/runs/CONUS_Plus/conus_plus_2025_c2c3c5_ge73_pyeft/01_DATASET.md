# Phase 1 Dataset Report — CONUS+

## Identity and gates

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
phase: 1
machine_gate: PASS
contract_human_gate: APPROVED
implementation_human_gate: APPROVED
```

## Approved contract

- Detectors: C2, C3, C5; C4 excluded.
- Observable: reconstructed ionization energy `E_reco` in eVee.
- Window: `[160, 350)` eVee.
- Binning: 20 explicit edges forming 19 adjacent 10 eVee half-open bins.
- Threshold metadata: C2=180, C3=160, C5=170 eVee.
- Primary output: `[detector, reconstructed_energy_bin]`, shape `[3, 19]`,
  `expected_events_per_bin`.
- Observed data: not attached; `data_mode=not_yet_known`.
- Exposure owner: per-detector kg day values 111.15, 103.40 and 111.86.

## Code and files

| Action | Path | Purpose |
| --- | --- | --- |
| Create | `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/experiment.yaml` | Machine-readable Phase 1 dataset contract |
| Create | `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/README.md` | Human-readable scope and limitations |
| Modify | `src/cevns_pyeft/experiments/specs.py` | Discover both flat and nested `experiment.yaml` files using recursive discovery |
| Modify | `tests/test_experiment_specs.py` | Cover flat/nested discovery and CONUS contract loading |

No Source, detector response, counting, Fast, statistics or registry implementation was added.

## Contract mapping

| Approved field | `experiment.yaml` key |
| --- | --- |
| Identity | `dataset_id`, `dataset_name`, `experiment_name`, `experiment_slug` |
| Detector scope/order | `run.detectors_included`, `run.detectors_excluded`, `run.detector_order` |
| Observable/unit | `detector.reconstructed_observable`, `detector.reconstructed_variable_unit` |
| Threshold metadata | `detector.threshold_detector_order`, `detector.thresholds_evee` |
| Analysis window | `analysis_window_evee` |
| Edges/count/convention | `binning.edges`, `number_of_bins`, `edge_convention` |
| Primary axes/shape/unit | `expected_output.axes`, `shape`, `unit` |
| Diagnostic axes | `expected_output.diagnostic_axes`, `diagnostic_shape` |
| Data semantics | `prediction_mode`, `statistical_data_mode`, `observed_data.*` |
| Exposure semantics | `exposure.*` |

## Units and normalization

- All reconstructed-energy edges and thresholds are in eVee.
- The primary output is expected events per bin, not a differential rate.
- Per-detector kg-day exposure is the sole mass-times-time owner.
- `326.41 kg day` is the raw sum; `327 kg day` is publication rounding only.

## Machine Gate P01

Attempted command:

```text
python -B -m pytest tests/test_experiment_specs.py -q
```

Result: `NOT_RUN`; the active Python environment does not provide the `pytest` module. No
dependency was installed.

Dependency-free assertions then verified:

- `specs.py` parses as valid Python;
- legacy registry names CsI2017, CsI2021 and Ar2020 remain exposed;
- existing flat CsI2017/CsI2021 specs remain discoverable;
- the nested CONUS+ spec is uniquely discoverable and loadable by dataset ID;
- source type and target mode match the contract;
- 20 edges produce exactly 19 bins;
- axes, shape and output unit match the approved contract;
- exposures sum to 326.41 kg day;
- no observed statistical data are attached.

Result: `P01=PASS` for the implemented dataset capability. Pytest execution remains an
environment limitation and must be rerun when pytest is available.

## Post-code review

- Shared change scope is limited to experiment-spec path discovery.
- Recursive discovery remains rooted under `data/experiments/`; it does not scan `backup/**`.
- Flat legacy layouts remain supported.
- The config intentionally marks Phase 2-10 capabilities as pending or false.
- The user approved the Phase 1 implementation with `APPROVE IMPLEMENTATION`.
- Decision `D0010` and evidence claim `C0031` record that approval.
- Phase 1 is complete. Phase 2 has not started and requires its own standardized
  pre-code review before any Target / Exposure implementation.

## Human Gate Dataset

```yaml
machine_gate: PASS
human_gate: APPROVED
approval: APPROVE IMPLEMENTATION
decision_ref: D0010
evidence_claim: C0031
```
