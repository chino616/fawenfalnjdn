# CsI2021 Phase 6 Detector Response Report

## Contract and implementation

```text
dataset: CsI2021
prerequisite gates: S0=PASS, T1=PASS, X=PASS
true variable: E_R [keV]
reconstructed variable: PE
quenching: eee_quenching_csi
response: normalized p_smearing_csi Gamma density on PE in [0,infinity)
efficiency: a/(1+exp[-b*(PE-c)])+d, clamped at zero
parameters: a=1.32045, b=0.285979, c=10.8646, d=-0.3333
binning: 9 irregular PE bins with edges 0.001 through 60.001
migration: events outside the analysis window are excluded
component acceptance: separate and unchanged [mu=0.997,e=0.848,mub=0.848]
classification: REUSE
new production adapter: none
```

References are `eee_quenching_csi` and `p_smearing_csi` in
`rates/differential.py`, plus `efficiency_csi2021` and `PE_BINS_9` in
`slow_counts_csi2021.py`. No detector physics production file was modified.
Flavor contraction ends before this scalar detector layer. Saved response
slices are raw densities and were not renormalized in the analysis window.

## API and specification

```text
response: scalar/array PE plus scalar E_R [keV] -> density [PE^-1]
support: zero for PE <= 0
efficiency: scalar/array PE -> same form, bounded in [0,1]
source/cross-section/exposure/count logic in detector helpers: none
```

`data/experiments/CsI2021/experiment.yaml` records the validated quenching,
response, efficiency parameters, units and callables. Its phase is
`DETECTOR_RESPONSE_VALIDATED`; Slow remains pending Phase 7.

## Diagnostics and tests

Full-domain adaptive-quadrature moments:

| E_R keV | Integral | Mean numeric/analytic PE | Width numeric/analytic PE |
|---:|---:|---:|---:|
| 1 | 1.0 | 0.7965119276902535 / 0.7965119276902538 | 0.6356173901758894 / 0.6356173901758893 |
| 5 | 1.0000000000000009 | 4.960562283044062 / 4.960562283044060 | 2.325041415175825 / 2.325041415175824 |
| 20 | 1.0000000000000002 | 27.674037917222982 / 27.674037917222964 | 6.065626687513860 / 6.065626687513862 |
| 40 | 1.0000000000000082 | 54.89376555407254 / 54.89376555407209 | 8.646419040760362 / 8.646419040760325 |

```text
detector_response_grid.csv rows: 5818
mapping monotonic: yes
positive width for E_R > 0: yes
efficiency range: 0 to 0.9871499965788872
analysis bins: 9
PNG/PDF sets: mean mapping, width, response slices, efficiency
artifact nonempty check: PASS
figure visual QA: PASS
focused Detector Response tests: 7 passed, 21 deselected
CsI/spec/P2 regression: 39 passed
```

Created under this run directory:

```text
artifacts/detector_response_grid.csv
figures/mean_mapping.png/.pdf
figures/resolution_width.png/.pdf
figures/detector_response_slices.png/.pdf
figures/efficiency.png/.pdf
06_DETECTOR_RESPONSE.md
```

Modified existing files: `data/experiments/CsI2021/experiment.yaml`,
`tests/test_csi_slow_source_state_p3.py`, and `backup/BACKUP_MANIFEST.md`.

## Gate R

```text
status: PASS
reasons:
  - Gamma density is nonnegative and normalized on [0,infinity)
  - numeric means and widths agree with analytic moments
  - efficiency acts once on PE and remains in [0,1]
  - support, scalar/array behavior, binning, artifacts and visual QA pass
  - detector helpers add no source, cross-section, exposure or count logic
blockers: none
next_skill: cevns-slow-counts
```
