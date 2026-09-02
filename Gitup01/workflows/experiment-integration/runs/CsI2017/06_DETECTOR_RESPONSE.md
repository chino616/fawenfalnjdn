# CsI2017 Phase 6 Detector Response Report

## Contract and implementation

```text
dataset: CsI2017
prerequisite gates: S0=PASS, T1=PASS, X=PASS
true variable: E_R [keV]
reconstructed variable: PE
mean mapping: PE = 1.17 * E_R_keV
response: deterministic Dirac mapping; width 0 PE; formal mass 1
efficiency: tabulated linear interpolation in reconstructed PE
threshold/low value: 4.9 PE / 1e-10
binning: 25 regular PE bins with edges 0.001 to 50.0
migration: events outside the analysis window are excluded
classification: REUSE
new production adapter: none
```

The reference implementation is `CSI2017_PE_PER_KEV` and
`CSI2017_BINS_25` in `slow_counts_csi2017.py`, with `_interp_eff` in
`experiments/base.py` configured from `data/datafiles/COHERENT_eff.txt`.
No detector physics production file was modified. A finite Gaussian width was
not invented. Flavor contraction ends before this scalar detector layer.

The distinct `14.57 kg` source metadata and `14.6 kg` legacy Slow multiplier
remain unchanged and are not part of Detector Response.

## API and specification

```text
mean input/output: scalar or array E_R [keV] -> PE
response: Dirac location with formal probability mass 1
efficiency: scalar/array PE -> same form, bounded in [0,1]
source/cross-section/exposure/count logic in detector helpers: none
```

`data/experiments/CsI2017/experiment.yaml` records the validated models,
threshold, data file, units and reuse callables. Its phase is
`DETECTOR_RESPONSE_VALIDATED`; Slow remains pending Phase 7.

## Diagnostics and tests

```text
detector_response_grid.csv rows: 705
mapping monotonic: yes
resolution width: 0 PE
formal Dirac mass: 1
efficiency range: 1e-10 to 0.6669701172242699
efficiency at 4.9 PE: 1e-10
analysis bins: 25
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

Modified existing files: `data/experiments/CsI2017/experiment.yaml`,
`tests/test_csi_slow_source_state_p3.py`, and `backup/BACKUP_MANIFEST.md`.

## Gate R

```text
status: PASS
reasons:
  - approved deterministic mapping and zero-width response are preserved
  - full-domain formal response mass is one without window renormalization
  - efficiency acts once on PE, remains in [0,1], and threshold behavior passes
  - binning, artifacts, tests and visual QA pass
  - detector helpers add no source, cross-section, exposure or count logic
blockers: none
next_skill: cevns-slow-counts
```
