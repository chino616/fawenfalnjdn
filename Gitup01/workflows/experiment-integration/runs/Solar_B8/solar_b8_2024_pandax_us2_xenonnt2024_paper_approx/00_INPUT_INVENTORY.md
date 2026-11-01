# Phase 0 input inventory — Solar B8 2024 paper approximation

## Identity

```yaml
experiment_name: Solar 8B neutrino scattering
experiment_slug: Solar_B8
dataset_id: solar_b8_2024_pandax_us2_xenonnt2024_paper_approx
scope_gate: APPROVED
scientific_claim: paper_approximate_single_bin_eft_benchmark
backup_quarantine_applied: true
```

## Registered inputs

| source ID | path | role | status |
| --- | --- | --- | --- |
| B8-PAPER-INSTRUCTIONS | docs/8B/CEvNS_B8_P05B_P06_INPUT_PACKAGE_20261013/P05B_P06_REQUIRED_INPUTS.md | acceptance and missing-input contract | SOURCE_EXTRACTED |
| B8-PUBLISHED-VALUES | docs/experiment_integration/experiment_inputs/Solar_B8/solar_b8_2024_pandax_us2_xenonnt2024_paper_approx/reference/P05B_REFERENCE_VALUES.yaml | published benchmark numbers | REFERENCE_ONLY |
| B8-PANDAX-EFFICIENCY | paper_approx/pandax_us2_efficiency.csv | PandaX US2 2024 efficiency | MISSING |
| B8-XENONNT-2024-EFFICIENCY | paper_approx/xenonnt_2024_efficiency.csv | XENONnT 2024 efficiency | MISSING |
| B8-XE131-RESPONSE | paper_approx/xe131_response_reference.yaml | Xe-131 response convention | MISSING |
| B8-PEANUTS-PROBABILITY | paper_approx/peanuts_probability_reference.csv | exposure-averaged propagation | MISSING |
| B8-PAPER-CONTOURS | paper_approx/fig4_fig5_fig6_reference.csv | paper contour reference | MISSING |

## Detector benchmark

- PandaX US2: 1.04 t yr, 0.33 keVnr, N_meas=69.1, N_SM=44.9, sigma_stat=25.567, sigma_alpha=0.245.
- XENONnT 2024: 3.51 t yr, 0.50 keVnr, N_meas=10.7, N_SM=11.15, sigma_stat=3.95, sigma_alpha=0.13.

## Boundary

This is a paper-approximate benchmark, not an official collaboration likelihood.
No forward calculation is authorized until detector efficiencies and response
conventions are independently verified. The XENONnT 2026 release is a separate
dataset and is not an input to this one.

