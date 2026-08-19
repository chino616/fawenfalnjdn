# Phase 6 Detector Response: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
input_inventory: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
implementation_manifest: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
kinematics_cross_section_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/05_KINEMATICS_CROSS_SECTION.md
detector_response_status: ADAPTER
```

Required previous state:

```text
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
```

## Approved Detector-Response Contract

Mean mapping:

```text
true variable: T
true-variable unit: keVnr
mean reconstructed variable: E_ee(T)
reconstructed-variable unit: eVee
quenching model: Lindhard Ge
epsilon_L(T) = 11.5 Z^(-7/3) T
g(epsilon_L) = 3 epsilon_L^0.15 + 0.7 epsilon_L^0.6 + epsilon_L
Q(T) = k g(epsilon_L) / (1 + k g(epsilon_L))
E_ee(T) = 1000 Q(T) T
Z = 32
k = 0.162
```

Stochastic response:

```text
response model: Gaussian in reconstructed energy
response density: R(E_reco | T) = Normal(E_reco; E_ee(T), sigma(E_ee(T)))
resolution model: sigma(E_ee) = sqrt(sigma_0^2 + F_Fano eta E_ee)
sigma_0 = 20.38 eVee
F_Fano = 0.1096
eta = 2.96 eV
response-density unit: eVee^-1
normalization domain: full reconstructed-energy real line
```

Efficiency:

```text
efficiency model: ideal threshold step
efficiency variable: reconstructed energy E_reco
efficiency unit: eVee
epsilon(E_reco) = Theta(E_reco - 160 eVee)
epsilon below threshold: 0
epsilon at/above threshold: 1
```

Analysis binning:

```text
bin variable: E_reco
bin unit: eVee
bin edges: 160, 170, ..., 350 eVee
number of bins: 19
edge convention: 160 <= E_reco < 350, 10 eVee width
```

## Reference Code

Inspected only the detector-response and folding references listed in
`CSI_REFERENCE_MAP.md`:

| Role | File | Symbol |
|---|---|---|
| CsI2017 visible observable and efficiency placement | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | `slow_counts_csi2017` |
| CsI2021 bin integration caller | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `slow_counts_csi2021`, `efficiency` |
| Generic CsI folding helper | `src/cevns_pyeft/rates/counts.py` | `bin_events_csi`, `empirical_dNdPE_response_csi` |

Verified reference contract:

```text
input units: CsI helpers use PE and keVnr; CONUS uses eVee and keVnr
return units: CONUS response density returns eVee^-1
scalar behavior: scalar inputs return float
array behavior: array inputs return numpy arrays
broadcasting: E_reco_eVee and T_keVnr broadcast through numpy
normalization convention: response density is normalized before analysis-window cuts
efficiency placement: efficiency acts on reconstructed observable
bin-edge convention: bin edges are strictly increasing reconstructed-observable edges
```

No CsI quenching, PE conversion, timing structure, efficiency curve, detector
parameters, or complete Slow module was copied.

## Implementation Decision

```text
classification: ADAPTER
reason: CONUS requires experiment-specific Lindhard Ge quenching, Gaussian eVee resolution, and threshold efficiency formulas
generic reusable code found: no standalone generic detector-response density module
new implementation layer: thin CONUS-family detector-response adapter
```

## Production Implementation

Created:

```text
src/cevns_pyeft/experiments/conus/detector_response.py
tests/test_conus_plus_ge73_pheno_detector_response.py
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/detector_response_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/mean_mapping.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/mean_mapping.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/resolution_width.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/resolution_width.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/detector_response_slices.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/detector_response_slices.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/efficiency.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/efficiency.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/06_DETECTOR_RESPONSE.md
```

Modified:

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
backup/BACKUP_MANIFEST.md
```

Backup:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_detector_response/experiment.yaml
```

Not modified:

```text
src/cevns_pyeft/rates/counts.py
src/cevns_pyeft/rates/differential.py
src/cevns_pyeft/experiments/coherent/
src/cevns_pyeft/experiments/conus/source.py
src/cevns_pyeft/experiments/conus/kinematics.py
Slow modules
Fast modules
statistics modules
registry.py
```

## Public API

Implementation file:

```text
src/cevns_pyeft/experiments/conus/detector_response.py
```

Public symbols:

```text
lindhard_quenching_ge(T_keVnr, experiment_spec=None) -> dimensionless Q
mean_reconstructed_energy_evee(T_keVnr, experiment_spec=None) -> eVee
resolution_width_evee(mean_evee, experiment_spec=None) -> eVee
conus_ge73_response_density(E_reco_eVee, T_keVnr, experiment_spec=None) -> eVee^-1
conus_ge73_efficiency(E_reco_eVee, experiment_spec=None) -> dimensionless
reco_energy_bin_edges_evee(experiment_spec=None) -> eVee bin edges
```

Behavior:

```text
scalar input: returns float for scalar-valued functions
array input: returns numpy array
broadcasting: response_density broadcasts E_reco_eVee and T_keVnr
negative true recoil: response density returns 0
efficiency domain: reconstructed energy E_reco_eVee
no source flux: yes
no cross section: yes
no exposure: yes
no final binned event counts: yes
```

## Diagnostic Outputs

Created validation grid:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/detector_response_grid.csv
```

Columns:

```text
T_keVnr
mean_eVee
sigma_eVee
E_reco_eVee
response_density_per_eVee
efficiency
```

Figure outputs:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/mean_mapping.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/mean_mapping.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/resolution_width.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/resolution_width.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/detector_response_slices.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/detector_response_slices.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/efficiency.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/efficiency.pdf
```

Representative numerical diagnostics:

| T [keVnr] | Q(T) | mean [eVee] | sigma [eVee] |
|---:|---:|---:|---:|
| 0.05 | `0.11788851450847417` | `5.894425725423709` | `20.42686089481541` |
| 0.10 | `0.12935251521984925` | `12.935251521984924` | `20.48269519759927` |
| 0.50 | `0.1601263099041248` | `80.0631549520624` | `21.007574074055487` |
| 1.00 | `0.17548084697565272` | `175.48084697565272` | `21.73184746984143` |
| 3.00 | `0.20311823165917842` | `609.3546949775352` | `24.7594186669605` |

Gaussian check at `T = 0.5 keVnr`, integrated on `mean +/- 12 sigma`:

```text
normalization: 1.0
mean check: 80.06315495206242 eVee
sigma check: 21.007574074055487 eVee
```

Threshold check:

```text
epsilon([159.999, 160.0, 350.0] eVee) = [0, 1, 1]
```

## Experiment-Spec Update

`data/experiments/conus_plus_ge73_pheno/experiment.yaml` now records:

```text
spec_status: detector_response_validated
provenance.phase: DETECTOR_RESPONSE_VALIDATED
detector_response.status: ADAPTER_VALIDATED
detector_response.callable: src.cevns_pyeft.experiments.conus.detector_response.conus_ge73_response_density
detector_response.mean_mapping_callable: src.cevns_pyeft.experiments.conus.detector_response.mean_reconstructed_energy_evee
detector_response.resolution_callable: src.cevns_pyeft.experiments.conus.detector_response.resolution_width_evee
detector_response.efficiency_callable: src.cevns_pyeft.experiments.conus.detector_response.conus_ge73_efficiency
detector_response.bin_edges_callable: src.cevns_pyeft.experiments.conus.detector_response.reco_energy_bin_edges_evee
detector_response.true_unit: keVnr
detector_response.reconstructed_unit: eVee
detector_response.response_density_unit: eVee^-1
detector_response.mean_mapping_model: Lindhard_Ge
detector_response.response_model: Gaussian_in_reconstructed_energy
detector_response.efficiency_model: ideal_reconstructed_energy_threshold_step
phase1_boundaries.detector_response_implemented: true
```

## Tests

Focused detector-response tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_detector_response.py
........                                                                 [100%]
8 passed in 0.57s
```

Combined completed-phase tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_source.py tests\test_conus_plus_ge73_pheno_theory.py tests\test_conus_plus_ge73_pheno_kinematics.py tests\test_conus_plus_ge73_pheno_detector_response.py
....................                                                     [100%]
20 passed in 0.73s
```

Checks covered:

```text
Lindhard formula
finite physical quenching
monotonic mean mapping
positive resolution width
Gaussian density nonnegative and finite
full-domain Gaussian normalization
Gaussian mean and sigma recovery
scalar input
array input
broadcasting
negative true recoil response density is zero
threshold efficiency at reconstructed energy
0 <= efficiency <= 1
analysis bin edges
diagnostic files and labels
no source, cross-section, exposure, Slow, Fast, or statistics dependency
experiment.yaml parameters are consumed
```

## Gate R

```text
status: PASS
```

Reasons:

- The approved Lindhard Ge mean mapping is implemented.
- The approved Gaussian resolution model is implemented.
- The response density is finite, nonnegative, and normalized before applying
  the analysis window.
- Efficiency acts on reconstructed energy `E_reco`, not true recoil.
- Efficiency remains within `[0, 1]` and steps at `160 eVee`.
- Analysis binning is consistent with `160..350 eVee` and 19 bins.
- Migration outside the analysis window is not renormalized away.
- Scalar, array, and broadcasting behavior pass.
- Diagnostic grids and figures were generated.
- `experiment.yaml` points to the validated detector-response implementation.
- No source flux, cross-section, exposure, Slow counts, Fast counts, or
  statistics logic was duplicated.

```text
next_skill: cevns-slow-counts
```

Stop after Gate R.
