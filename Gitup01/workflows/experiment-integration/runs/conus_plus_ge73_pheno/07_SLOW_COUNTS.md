# Phase 7 Slow Counts: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
source_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/03_SOURCE.md
theory_response_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/04_THEORY_RESPONSE.md
cross_section_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/05_KINEMATICS_CROSS_SECTION.md
detector_response_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/06_DETECTOR_RESPONSE.md
```

Required gates:

```text
Gate D0 = PASS
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
Gate R = PASS
```

## Reference Code

Inspected only the Slow references listed in `CSI_REFERENCE_MAP.md`:

| Role | File | Symbol |
|---|---|---|
| Dataset-level Slow callable | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | `slow_counts_csi2017` |
| Dataset-level Slow callable | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `slow_counts_csi2021` |
| Dataset-level Slow callable | `src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py` | `slow_counts_ar2020` |
| Folding helper | `src/cevns_pyeft/rates/counts.py` | `_rate_per_kg`, `_folded_counts`, `bin_events_csi` |
| Differential cross section | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn`, `_trapz` |

Verified reference contract:

```text
return type: dict
counts_per_bin: component dictionary with total
bin axis: detector reconstructed observable
component behavior: source flavor and target components are preserved when applicable
bin integration: reconstructed-observable bins with strictly increasing edges
Slow boundary: no Fast imports, caches, or template kernels
```

No CsI/Ar source, target, quenching, efficiency, exposure, timing, or complete
Slow module was copied.

## Authoritative Calculation

Call chain:

```text
slow_counts_conus_plus_ge73_pheno
-> load_conus_plus_ge73_reactor_flux
-> differential_cross_section_conus_ge73
-> target_time_normalization
-> conus_ge73_response_density
-> conus_ge73_efficiency
-> reconstructed-energy bin integration
```

True-recoil kernel:

```text
S(T) = integral dE_nu [dPhi/dE_nu] [d sigma / dT]
E_nu support: max(E_nu,min(T), 0.01 MeV) to 10 MeV
T support: 0 to exact T_max(10 MeV) = 2.940351893369968 keVnr
default cross-section model: full_response
default kinematic convention: publication_reproduction
neutrino-energy integration: trapezoid over recoil-dependent grid
default n_neutrino: 240
```

Target-time normalization:

```text
nuclei per kilogram: 8.249507890410958e24
exposure: 119 kg day
seconds per day: 86400
normalization factor: 8.48181403260493e31 target seconds
```

Detector folding:

```text
dN/dE_reco = epsilon(E_reco) * integral dT [dN_true/dT] R(E_reco | T)
true-recoil integration: trapezoid
default n_true_recoil: 121
reconstructed-energy grid step: 1 eVee
efficiency domain: reconstructed energy E_reco
migration outside analysis window: not renormalized into the window
```

Bin counts:

```text
N_i = integral_{E_i}^{E_{i+1}} dE_reco dN/dE_reco
bin edges: 160, 170, ..., 350 eVee
number of bins: 19
output unit: expected_events_per_bin
```

## Public API

Implementation file:

```text
src/cevns_pyeft/experiments/conus/slow_counts_conus_plus_ge73_pheno.py
```

Public callable:

```python
slow_counts_conus_plus_ge73_pheno(
    coefficients=None,
    experiment_spec=None,
    *,
    wc_triplets=None,
    left_wcs=None,
    include_sm=True,
    cross_section_model="full_response",
    kinematics="publication_reproduction",
    sin2thetaW=0.23873,
    c10_mass_mode="flavor",
    return_components=False,
    integration_settings=None,
)
```

Return contract:

```text
counts_total: float64[19]
counts_per_bin["total"]: float64[19]
counts_per_bin["nuebar_Ge73"]: float64[19]
counts_per_evee["total"]: float64[19]
reco_energy_bins_evee: float64[20]
axes: ("reco_energy_evee",)
unit: expected_events_per_bin
```

Optional diagnostics when `return_components=True`:

```text
true_recoil_grid_keVnr
dndT_true_per_keVnr
reco_energy_grid_evee
dndE_reco_per_evee
```

Omitted component axes:

```text
detector axis: omitted; dataset is one effective Ge73 detector
target axis: omitted in public total; only Ge73 exists
source-flavor axis: omitted in public total; only reactor electron antineutrino exists
```

## Production Files

Created:

```text
src/cevns_pyeft/experiments/conus/slow_counts_conus_plus_ge73_pheno.py
tests/test_conus_plus_ge73_pheno_slow_counts.py
tests/reference_conus_plus_ge73_pheno/slow_reference.npy
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/true_recoil_spectrum.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/reconstructed_spectrum.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/slow_bin_counts.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/slow_convergence.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/true_recoil_spectrum.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/true_recoil_spectrum.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/reconstructed_spectrum.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/reconstructed_spectrum.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/slow_bin_counts.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/slow_bin_counts.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/07_SLOW_COUNTS.md
```

Modified:

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
backup/BACKUP_MANIFEST.md
```

Backup:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_slow_counts/experiment.yaml
```

Not modified:

```text
shared theory modules
shared nuclear Response data
source implementation
cross-section implementation
detector-response implementation
existing CsI/Ar Slow modules
Fast modules
statistics modules
registry.py
```

## Numerical Results

Default settings:

```text
n_true_recoil: 121
n_neutrino: 240
reco_step_evee: 1.0
runtime_s: 13.226071119308472
```

SM `full_response` bin counts:

| bin | E_low [eVee] | E_high [eVee] | counts |
|---:|---:|---:|---:|
| 1 | 160 | 170 | `34.17364951955` |
| 2 | 170 | 180 | `26.52169071139` |
| 3 | 180 | 190 | `20.61344100250` |
| 4 | 190 | 200 | `16.02914483515` |
| 5 | 200 | 210 | `12.45943889241` |
| 6 | 210 | 220 | `9.673234824025` |
| 7 | 220 | 230 | `7.495853766423` |
| 8 | 230 | 240 | `5.793870486261` |
| 9 | 240 | 250 | `4.464434857575` |
| 10 | 250 | 260 | `3.427636000277` |
| 11 | 260 | 270 | `2.620970974472` |
| 12 | 270 | 280 | `1.995291932570` |
| 13 | 280 | 290 | `1.511802262612` |
| 14 | 290 | 300 | `1.139800673562` |
| 15 | 300 | 310 | `0.8549627674328` |
| 16 | 310 | 320 | `0.6380157732365` |
| 17 | 320 | 330 | `0.4737070071901` |
| 18 | 330 | 340 | `0.3499943812517` |
| 19 | 340 | 350 | `0.2574053192391` |

Summary:

```text
total predicted events: 150.49434598713285
minimum bin count: 0.2574053192390878
maximum bin count: 34.17364951955145
reference array: tests/reference_conus_plus_ge73_pheno/slow_reference.npy
```

Convergence:

| label | n_true_recoil | n_neutrino | reco_step [eVee] | total counts | total relative delta | max bin relative delta |
|---|---:|---:|---:|---:|---:|---:|
| coarse | 41 | 80 | 5.0 | `150.6090383252` | `7.621039669306e-04` | `1.325096849143e-03` |
| medium | 61 | 120 | 2.0 | `150.4848297150` | `6.323341968326e-05` | `1.165397973771e-04` |
| default_reference | 121 | 240 | 1.0 | `150.4943459871` | `0.0` | `0.0` |

## Experiment-Spec Update

`data/experiments/conus_plus_ge73_pheno/experiment.yaml` now records:

```text
spec_status: slow_validated
provenance.phase: SLOW_VALIDATED
slow_counts.status: ADAPTER_VALIDATED
slow_counts.callable: src.cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno.slow_counts_conus_plus_ge73_pheno
slow_counts.reference_file: tests/reference_conus_plus_ge73_pheno/slow_reference.npy
slow_counts.default_cross_section_model: full_response
slow_counts.default_kinematics: publication_reproduction
slow_counts.output_shape: [19]
slow_counts.output_unit: expected_events_per_bin
slow_counts.exposure_applied: exactly_once
slow_counts.reference_total_counts_sm: 150.49434598713285
phase1_boundaries.slow_counts_implemented: true
```

## Tests

Focused Slow tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_slow_counts.py
......                                                                   [100%]
6 passed in 21.32s
```

Combined completed-phase tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_source.py tests\test_conus_plus_ge73_pheno_theory.py tests\test_conus_plus_ge73_pheno_kinematics.py tests\test_conus_plus_ge73_pheno_detector_response.py tests\test_conus_plus_ge73_pheno_slow_counts.py
..........................                                               [100%]
26 passed in 22.16s
```

Checks covered:

```text
public callable loads
output shape is 19 bins
counts are finite and nonnegative
component sum equals total
exposure normalization is applied exactly once
half exposure gives half counts
support endpoint matches T_max(10 MeV)
default reference array is reproduced
medium/default convergence passes
complex wc_triplets smoke test passes
helm_sm model selector passes for SM
helm_sm rejects EFT coefficients
diagnostic artifacts and figures exist
Slow module has no Fast, kernel, or statistics dependency
```

## Gate L

```text
status: PASS
```

Reasons:

- The direct integration follows the approved source -> cross section -> target
  normalization -> detector response -> reconstructed-bin chain.
- Output axes, shape, and units match the dataset contract.
- Exposure is counted exactly once and tested by linear scaling.
- The only physical component is `nuebar_Ge73`; it reproduces total counts.
- Integration convergence is documented and passes against the default
  reference.
- Diagnostic spectra, bin counts, convergence table, and figures were
  generated.
- The independent Slow reference array was saved.
- The Slow module has no Fast/cache/kernel/statistics dependency.

```text
next_skill: cevns-fast-counts
```

Stop after Gate L.
