# CsI2021 Phase 1 Dataset Report

## Phase 0 inputs

- dataset_id: CsI2021
- input_inventory: workflows/experiment-integration/runs/CsI2021/00_INPUT_INVENTORY.md
- implementation_manifest: workflows/experiment-integration/runs/CsI2021/00_IMPLEMENTATION_MANIFEST.yaml
- Gate I status: PASS

## Approved dataset contract

- experiment_family: COHERENT_CsI
- run_period: 2021 release/current reproduction
- detector_configuration: 14.57 kg CsI[Na] with CsI2021 efficiency and acceptance
- source_configuration: SNS prompt nu_mu plus delayed nu_e and antinu_mu
- target_configuration: equal Cs:I stoichiometry with Cs-133 and I-127
- statistical_data_mode: background_subtracted_excess

## Observable contract

- true_observables: E_nu_MeV, E_R_keV
- reconstructed_observables: PE
- output_axes: source_component, pe_bin
- output_shape: [9]
- output_unit: expected_events_per_bin

## Binning

- mode: explicit_edges
- minimum: 0.001
- maximum: 60.001
- number_of_bins: 9
- unit: PE
- edge_convention: adjacent half-open bins with the final upper edge retained
- edge_file: none
- edges: [0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001]

## Static dataset fields

- detectors: one 14.57 kg CsI[Na] detector
- targets: Cs133 and I127, equal stoichiometry
- response_keys: Cs133 and I
- exposure: 3.198e23 POT at 19.3 m and 14.57 kg
- exposure_unit: time-integrated SNS flux times kg
- exposure_semantics: detector mass is applied exactly once
- analysis_threshold: encoded by existing analytic efficiency, not redefined here
- analysis_window: 0.001–60.001 PE

## Callable placeholders

| Module | Status | Planned callable | Planned file | Implementation phase |
|---|---|---|---|---|
| source | pending | sns_component_state | experiments/coherent/sns.py | Phase 3 |
| detector response | reuse | current p_smearing_csi and CsI2021 efficiency | slow_counts_csi2021.py | Phase 6 validation |
| slow counts | pending | slow_counts_csi2021 | slow_counts_csi2021.py | Phase 7 |
| fast counts | blocked | Flavor Fast contract unresolved | none in P3 | P4/workflow Phase 8 |
| statistics | blocked | authoritative model unavailable | none | Phase 9 |

## Mapping to experiment.yaml

| Phase 0 field | experiment.yaml field | Value | Validation |
|---|---|---|---|
| dataset identity | dataset_name | CsI2021 | loader exact match |
| family | family | COHERENT_CsI | exact |
| source type | source_type | stopped_pion | schema enum |
| target | target_mode | CsI_equal_stoichiometry | required nonempty field |
| statistical mode | statistical_data_mode | background_subtracted_excess | approved Phase 0 value |
| true axes | expected_output/binning | E_nu_MeV, E_R_keV | static contract |
| reconstructed axis | binning.observable | PE | exact |
| output axes | expected_output.axes | source_component, pe_bin | exact |
| output shape | expected_output.shape | [9] | equals edge count minus one |
| output unit | expected_output.unit | expected_events_per_bin | exact |
| source components | source.components | mu, e, mub | approved static labels |
| particle metadata | source.particle_kinds | nu, nu, antinu | pending implementation |
| response files | planned_data_files | repository-relative paths | path test |

## Files

### Reused

- schemas/experiment.schema.json
- src/cevns_pyeft/experiments/specs.py
- src/cevns_pyeft/experiments/registry.py
- data/responses/responses_all.json

### Created

- data/experiments/CsI2021/experiment.yaml
- data/experiments/CsI2021/README.md
- workflows/experiment-integration/runs/CsI2021/01_DATASET.md
- tests/test_csi_slow_source_state_p3.py (shared Phase 1 dataset tests)

### Modified

None.

### Conditional modifications

registry.py was approved only if legacy registration could not be retained. It
was not modified because get_experiment_spec loads the spec independently.

### Must not modify

- Existing experiment production implementations
- Existing Fast/reference arrays
- Shared theory, nuclear-response, rates and kernel modules
- All CONUS implementations

## Schema validation

- schema: schemas/experiment.schema.json
- command: python -m pytest -q tests/test_csi_slow_source_state_p3.py tests/test_experiment_specs.py -p no:cacheprovider
- result: PASS; combined Phase 1 and existing spec suite 10 passed
- coverage: required fields, source_type enum, nonempty dataset identity and accepted additional approved fields

## Loader validation

- loader: get_experiment_spec through experiments/specs.py
- command result: CsI2021 stopped_pion CsI_equal_stoichiometry 9 [9]
- result: PASS; repository path resolves to data/experiments/CsI2021/experiment.yaml
- legacy registry behavior: unchanged

## Consistency checks

- dataset ID unique: PASS
- repository-relative paths: PASS
- binning valid: PASS
- bin count: 9
- output shape: [9]
- statistical data mode valid: PASS as approved provisional mode
- callable placeholders accepted: PASS
- later-phase code created: no

## Gate D0

- status: PASS
- reasons:
  - the approved CsI2021 dataset contract is represented by the minimum runtime spec
  - schema-required fields and loader behavior pass
  - explicit PE edges exactly match output shape
  - only dataset files and dataset validation tests were created

Stop after Gate D0.

