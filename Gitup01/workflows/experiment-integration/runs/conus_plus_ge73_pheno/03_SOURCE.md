# Phase 3 Source Report: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
input_inventory: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
implementation_manifest: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
target_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/02_DETECTOR_TARGET.md
source_status: ADAPTER
```

Required previous state:

```text
Gate I = PASS
Gate D0 = PASS
Gate T0 = PASS
```

## Approved Source Definition

```text
source_type: reactor
components: detector-position reactor electron antineutrino flux
flavors: electron_antineutrino
energy_unit: MeV
flux_unit: cm^-2 s^-1 MeV^-1
energy_support: 0.01 <= E_nu <= 10 MeV
time_support: steady-state flux; no time dependence in this source phase
normalization: dPhi/dE = Phi0 * rho(E) / N_rho, Phi0 = 1.5e13 cm^-2 s^-1
interpolation: linear interpolation of Kopeikin low-energy table
matching: c_match = rho_Mueller(2 MeV) / rho_Kopeikin(2 MeV)
lower_boundary: zero for E_nu < 0 and 0 <= E_nu < 0.01 MeV
upper_boundary: zero for E_nu > 10 MeV
zero_outside_support: yes
nonnegative_required: yes
```

Numerical tables:

| Table | Source | Shape | Units | Output file |
|---|---|---:|---|---|
| Mueller coefficients and fission fractions | Phase 0 inventory Table 1 | 4 isotopes x 7 fields | MeV polynomial coefficients | `data/experiments/conus_plus_ge73_pheno/mueller_coefficients.csv` |
| Kopeikin low-energy spectrum | Phase 0 inventory Table 2 | 32 x 2 | MeV, unnormalized rho | `data/experiments/conus_plus_ge73_pheno/kopeikin_low_energy_spectrum.csv` |

## Reference Code

Inspected only the source-related files listed in `CSI_REFERENCE_MAP.md`:

| Role | File | Symbol |
|---|---|---|
| Source callable | `src/cevns_pyeft/experiments/coherent/sns.py` | `loadNeutrinoEmpiricalFluxSNS` |
| Source caller | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | `loadNeutrinoEmpiricalFluxSNS("CsI2017")` |
| Source caller | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `loadNeutrinoEmpiricalFluxSNS("CsI2021")` |

Verified contract:

```text
input arguments: energy-like scalar or array
input units: MeV for measured flux
scalar behavior: scalar input returns float
array behavior: array input returns same-shape numpy array
component labels: measured flavor/component dict
return type: dict containing metadata and callables
return shape: scalar object with scalar/array callables
return unit: cm^-2 s^-1 MeV^-1 for CONUS source
out-of-support behavior: zero
```

No SNS spectrum, SNS timing distribution, CsI normalization parameter, or CsI
component weight was copied.

## Implementation Decision

```text
decision: ADAPTER
reason: the approved source is a piecewise Kopeikin-Mueller reactor spectrum with a 2 MeV matching factor, source-specific support boundaries, and recomputed normalization integral
reused API: repository pattern of returning a dict with basic metadata and measured callables
new logic required: table loading, Mueller polynomial spectrum, Kopeikin interpolation, piecewise release spectrum, normalization integral
```

## Production Files

### Reuse

```text
src/cevns_pyeft/experiments/specs.py
src/cevns_pyeft/experiments/registry.py
```

### Created

```text
data/experiments/conus_plus_ge73_pheno/mueller_coefficients.csv
data/experiments/conus_plus_ge73_pheno/kopeikin_low_energy_spectrum.csv
src/cevns_pyeft/experiments/conus/__init__.py
src/cevns_pyeft/experiments/conus/source.py
tests/test_conus_plus_ge73_pheno_source.py
workflows/experiment-integration/runs/conus_plus_ge73_pheno/03_SOURCE.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/source_spectrum_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_full.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_full.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_low_energy.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_low_energy.pdf
```

### Modified

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
backup/BACKUP_MANIFEST.md
```

Backup:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_source/experiment.yaml
```

Nested backup creation under `backup/` was denied by the local Windows
filesystem, so the backup was stored under the workflow run directory and
recorded in `backup/BACKUP_MANIFEST.md`.

### Must Not Modify

```text
existing CsI or SNS source implementations
existing experiment source data
target files
theory modules
nuclear-response modules
rates modules
Slow modules
Fast modules
statistics modules
registry.py
```

## New Source Code

Planned call chain:

```text
experiment.yaml
→ load_conus_plus_ge73_reactor_flux(experiment_spec)
→ mueller_coefficients.csv and kopeikin_low_energy_spectrum.csv
→ measured["nuebar"](E_nu)
→ differential flux
```

Functions:

| Function | Purpose |
|---|---|
| `load_reactor_flux_tables(experiment_spec)` | load validated source tables |
| `mueller_spectrum_shape(E_MeV, tables)` | construct high-energy unnormalized Mueller shape |
| `kopeikin_spectrum_shape(E_MeV, tables)` | linearly interpolate low-energy Kopeikin table |
| `release_reactor_spectrum_shape(E_MeV, tables)` | construct approved piecewise release spectrum |
| `load_conus_plus_ge73_reactor_flux(experiment_spec)` | return normalized differential flux callables |

Public contract:

```text
energy input unit: MeV
component argument: no public component argument; measured component label is nuebar
return type: dict with basic metadata, source tables, and measured callables
return shape: scalar object; callables return scalar or array matching input
return unit: cm^-2 s^-1 MeV^-1
scalar behavior: scalar input returns float
array behavior: array input returns numpy array
outside-support behavior: zero below 0.01 MeV and above 10 MeV, including E_nu < 0
error behavior: raises when source tables are malformed or normalization is nonpositive
```

## Experiment-Spec Update

`data/experiments/conus_plus_ge73_pheno/experiment.yaml` now records:

```text
spec_status: source_phase_validated
provenance.phase: SOURCE_VALIDATED
source.status: ADAPTER_VALIDATED
source.component: reactor_electron_antineutrino_flux_at_detector
source.flavor: electron_antineutrino
source.energy_unit: MeV
source.flux_unit: cm^-2 s^-1 MeV^-1
source.phi0_cm2_s: 1.5e13
source.energy_min_mev: 0.01
source.matching_energy_mev: 2.0
source.energy_max_mev: 10.0
source.boundary_rule: zero_for_E_lt_0_and_0_to_0p01_and_E_gt_10
source.normalization_rule: recompute_N_rho_from_release_spectrum
phase1_boundaries.reactor_flux_implemented: true
phase1_boundaries.source_tables_created: true
```

`registry.py` was not modified.

## Tests

Test file:

```text
tests/test_conus_plus_ge73_pheno_source.py
```

Required checks implemented:

```text
Mueller coefficient values
Kopeikin table nodes
energy support
lower boundary
upper boundary
zero outside support
finite outputs
nonnegative flux
matching continuity
integrated normalization
scalar input
array input
matching diagnostics
```

Commands run:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_source.py
....                                                                     [100%]
4 passed in 0.54s
```

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'C:\Users\Ultimator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from cevns_pyeft.experiments.registry import get_experiment_spec; from cevns_pyeft.experiments.conus.source import load_conus_plus_ge73_reactor_flux; spec=get_experiment_spec('conus_plus_ge73_pheno'); flux=load_conus_plus_ge73_reactor_flux(spec); print(spec.data.get('spec_status')); print(flux['basic']['normalization_integral']); print(flux['basic']['c_match'])"
source_phase_validated
6.461225533793083
0.9677534794383323
```

## Numerical Results

```text
matching_factor: 0.9677534794383323
normalization_integral: 6.461225533793083
integrated_flux: 15000000000000.0 cm^-2 s^-1
rho_mueller_2MeV: 1.258079523269832
rho_kopeikin_2MeV: 1.3
minimum_flux_on_support_grid: 5989430.090963032 cm^-2 s^-1 MeV^-1
maximum_flux_on_support_grid: 13412675912711.447 cm^-2 s^-1 MeV^-1
matching_left: 1.2580795232698323
matching_right: 1.258079523269832
continuity_residual: 2.220446049250313e-16
component_sum_residual: 0.0
```

The normalization integral is evaluated over the physical release support. The
sub-threshold interval `0 <= E_nu < 0.01 MeV` remains zero and is not connected
to the nonzero `0.01 MeV` table value by trapezoidal quadrature.

## Source Spectrum Figures

Generated:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/source_spectrum_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_full.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_full.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_low_energy.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/source_flux_low_energy.pdf
```

Visual check:

```text
full-range figure: nonblank; support and 2 MeV matching point visible
low-energy figure: nonblank; Kopeikin nodes, 0.01 MeV support edge, and 2 MeV matching point visible
```

Reference-comparison figure:

```text
not generated
reason: no separate digitized literature curve or direct reference spectrum was supplied beyond the production Mueller and Kopeikin tables
```

## Gate S0

```text
status: PASS
```

Reasons:

- Source tables match the approved Phase 0 inputs.
- CsI/SNS source API was inspected only for local callable conventions.
- The new callable follows the repository dict-with-measured-callables pattern.
- Units, support, and returned shape are explicit.
- Boundary behavior passes.
- 2 MeV matching passes.
- Integrated normalization passes.
- Nonnegativity and scalar/array behavior pass.
- `experiment.yaml` points to the validated Source state.
- Focused Source tests pass.
- Source validation grid and figures were generated and visually checked.
- No unrelated experiment behavior changed.

## Next Skill

```text
cevns-theory-response
```

Do not execute the next Skill automatically.
