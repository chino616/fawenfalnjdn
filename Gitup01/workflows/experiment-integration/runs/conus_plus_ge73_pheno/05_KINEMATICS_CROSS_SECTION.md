# Phase 5 Kinematics and Differential Cross Section: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
input_inventory: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
implementation_manifest: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
source_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/03_SOURCE.md
theory_response_report: workflows/experiment-integration/runs/conus_plus_ge73_pheno/04_THEORY_RESPONSE.md
target: Ge73
target_mass: 67.99906957156 GeV
Response key: Ge73
```

Required previous state:

```text
Gate S0 = PASS
Gate T1 = PASS
```

## Reference Code

| Role | File | Symbol |
|---|---|---|
| Shared differential cross section | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |
| Shared amplitude model | `src/cevns_pyeft/theory/li2026/amplitude.py` | `amplitude_squared_onebody_li2026` |
| Shared Response model | `src/cevns_pyeft/nuclear/response.py` | `ResponseDB`, `ResponseW` |
| Helm form factor | `src/cevns_pyeft/theory/helm/form_factor.py` | placeholder only |
| Helm cross section | `src/cevns_pyeft/theory/helm/cross_section.py` | placeholder only |
| Kinematic endpoint helper | `src/cevns_pyeft/rates/differential.py` | `enr_max_keV` |
| Physical-support mask | `src/cevns_pyeft/rates/differential.py` | internal heavy-nucleus support in `differential_cross_section_nn` |

Required call path:

```text
E_nu and recoil
→ publication_reproduction heavy-nucleus support
→ selected nuclear model
→ shared differential_cross_section_nn for full_response
```

Verified shared contract:

```text
energy input units: MeV for differential_cross_section_nn
recoil input units: keVnr
cross-section output unit: cm^2 keV^-1
scalar behavior: scalar Enu returns scalar-like result
array behavior: shared callable supports array Enu for scalar recoil; CONUS adapter broadcasts Enu and recoil
broadcasting: CONUS adapter broadcasts E_nu_MeV and T_keVnr
out-of-support behavior: zero
```

## Cross-Section Model Selection

```text
default model: full_response
available models: full_response, helm_sm
Helm allowed coefficient space: Standard Model weak-charge comparison only
unsupported combinations: helm_sm with left_wcs or wc_triplets raises ValueError
```

### `full_response`

Uses:

```text
src/cevns_pyeft/rates/differential.py::differential_cross_section_nn
ResponseDB(...).get("Ge73")
include_sm=True by default
repository-native LEFT coefficient triplets for EFT terms
```

This branch does not call Helm and does not multiply the full nuclear Response
result by any Helm form factor.

### `helm_sm`

Uses:

```text
Standard Model weak charge
Q_W = N - (1 - 4 sin^2 theta_W) Z
Helm weak form factor
the same publication_reproduction support convention
```

This branch is only a Standard Model validation/comparison model. It rejects
EFT coefficients.

## Helm Convention

Implemented in:

```text
src/cevns_pyeft/experiments/conus/kinematics.py::helm_form_factor_ge73
```

Convention:

```text
weak charge definition: Q_W = N - (1 - 4 sin^2 theta_W) Z
proton contribution: -(1 - 4 sin^2 theta_W) Z
neutron contribution: N
nuclear radius convention: R = 1.2 A^(1/3) fm
effective radius: R0 = sqrt(R^2 - 5 s^2)
skin thickness: s = 0.9 fm
spherical Bessel convention: F(q) = 3 j1(q R0) / (q R0) * exp[-(q s)^2 / 2]
proton and neutron form factors: same Helm shape for weak-charge comparison
normalization F(0): 1
```

The `q -> 0` limit is handled analytically with `j1(x)/x -> 1/3`.

The repository `src/cevns_pyeft/theory/helm/` package currently contains
placeholders, so the Helm helper is implemented only inside the CONUS
experiment-family adapter for this validated comparison path. It is not added
to the nuclear Response database.

## Kinematics

```text
true recoil variable: T
recoil unit: keVnr
neutrino-energy unit: MeV
target-mass unit: GeV
target mass: m_A = A * AMU_GEV = 67.99906957156 GeV
exact E_nu_min: not used as default in this reproduction phase
reproduction E_nu_min: E_nu_min_MeV = 1000 * sqrt(m_A_GeV * T_keVnr * 1e-6 / 2)
selected default: publication_reproduction
recoil endpoint: exact two-body Tmax for diagnostics
integration support: E_nu >= E_nu_min and T >= 0
```

Supported kinematic labels:

```text
publication_reproduction
heavy_nucleus_approximation
```

Both labels currently select the approved heavy-nucleus reproduction threshold.
The exact endpoint is exposed separately as `recoil_max_exact_keV`.

Endpoint diagnostics:

| E_nu [MeV] | T_max exact [keVnr] | E_nu_min at endpoint [MeV] |
|---:|---:|---:|
| 1.0 | `0.029411302095702` | `0.9999852942408226` |
| 2.0 | `0.11764174838580714` | `1.9999411782608079` |
| 3.0 | `0.26468614933272083` | `2.99986765400609` |
| 5.0 | `0.7351960600988574` | `4.999632388456126` |
| 8.0 | `1.8819358828315047` | `7.999058976713282` |
| 10.0 | `2.940351893369968` | `9.998529715966558` |

## Public API

```text
callable: differential_cross_section_conus_ge73
implementation file: src/cevns_pyeft/experiments/conus/kinematics.py
model labels: full_response, helm_sm
kinematic labels: publication_reproduction, heavy_nucleus_approximation
input units: E_nu_MeV in MeV, T_keVnr in keVnr
return unit: cm^2 keV^-1
return shape: scalar for scalar/scalar input; broadcast numpy array otherwise
broadcasting: E_nu_MeV and T_keVnr broadcast through numpy
error behavior: unknown model/kinematics raises ValueError; helm_sm with EFT coefficients raises ValueError
```

Additional helpers:

```text
ge73_target_mass_gev
enu_min_heavy_nucleus_conus_ge73
recoil_max_exact_keV
physical_support_mask
q_from_recoil_MeV
helm_form_factor_ge73
weak_charge_ge73
helm_sm_differential_cross_section
```

## Production Decision

```text
kinematics classification: ADAPTER
cross-section classification: ADAPTER
full-response implementation: reuse shared differential_cross_section_nn through thin CONUS adapter
Helm implementation: CONUS-family SM-only comparison helper because shared Helm package is placeholder-only
new adapter required: yes
reason: explicit publication_reproduction kinematics, Response-key routing, scalar/array broadcasting, and mutually exclusive model labels
```

Created code:

```text
src/cevns_pyeft/experiments/conus/kinematics.py
```

Not created:

```text
src/cevns_pyeft/experiments/conus/cross_section.py
experiment-specific amplitude.py
experiment-specific nuclear_response.py
duplicate Li2026 cross section
```

## Cross-Section Diagnostics

Created:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/kinematic_endpoints.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/cross_section_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/cross_section_vs_recoil.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/cross_section_vs_recoil.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/full_response_vs_helm.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/full_response_vs_helm.pdf
```

Grid:

```text
energies: 1, 2, 3, 5, 8, 10 MeV
rows: 960
models: full_response, helm_sm
kinematics: publication_reproduction
unit: cm^2 keV^-1
```

Representative diagnostic at `E_nu = 5 MeV`:

```text
Tmax_exact: 0.7351960600988574 keVnr
max full_response SM: 4.48888931252565e-40 cm^2 keV^-1
max helm_sm: 4.48540396909567e-40 cm^2 keV^-1
```

The generated figures are nonblank and use the same target, energy, recoil
grid, kinematic convention, and units for both models.

## Files

### Created

```text
src/cevns_pyeft/experiments/conus/kinematics.py
tests/test_conus_plus_ge73_pheno_kinematics.py
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/kinematic_endpoints.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/cross_section_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/cross_section_vs_recoil.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/cross_section_vs_recoil.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/full_response_vs_helm.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/full_response_vs_helm.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/05_KINEMATICS_CROSS_SECTION.md
```

### Modified

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
backup/BACKUP_MANIFEST.md
```

Backup:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_kinematics/experiment.yaml
```

### Must Not Modify Without CORE_EXTENSION Approval

```text
src/cevns_pyeft/theory/li2026/
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
existing experiment cross sections
existing reference arrays
```

## Experiment-Spec Update

`data/experiments/conus_plus_ge73_pheno/experiment.yaml` now records:

```text
spec_status: kinematics_cross_section_validated
provenance.phase: CROSS_SECTION_VALIDATED
kinematics.status: ADAPTER_VALIDATED
kinematics.default: publication_reproduction
cross_section.status: ADAPTER_VALIDATED
cross_section.callable: src.cevns_pyeft.experiments.conus.kinematics.differential_cross_section_conus_ge73
cross_section.shared_callable: src.cevns_pyeft.rates.differential.differential_cross_section_nn
cross_section.default_model: full_response
cross_section.available_models: full_response, helm_sm
phase1_boundaries.kinematics_cross_section_implemented: true
```

## Tests

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_kinematics.py
.....                                                                    [100%]
5 passed in 0.52s
```

Combined Phase 4/5 check:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_theory.py tests\test_conus_plus_ge73_pheno_kinematics.py
.......                                                                  [100%]
7 passed in 0.64s
```

Spec/import smoke check:

```text
kinematics_cross_section_validated
full_response
1.4282458060285336e-40
```

Checks covered:

```text
exact endpoint relation
publication reproduction E_nu_min
physical-support mask
zero outside support
scalar and array behavior
full_response finite nonnegative Standard Model cross section
Helm F(0) = 1
finite nonnegative helm_sm Standard Model cross section
helm_sm rejects EFT coefficients
saved grids and figures exist
diagnostic values are finite and nonnegative
model labels and units are explicit
```

## Gate X

```text
status: PASS
```

Reasons:

- The shared Li2026 differential cross section is reused for `full_response`.
- The selected kinematic convention is explicit.
- `full_response` and `helm_sm` are mutually exclusive model labels.
- `helm_sm` is SM-only and rejects EFT coefficients.
- Helm convention and q -> 0 behavior are explicit and tested.
- Physical masks and endpoints pass.
- Units and scalar/array behavior pass.
- Diagnostic grids and figures were generated.
- No shared theory, shared Response data, detector-response, Slow, Fast, or
  statistics files were modified.

```text
default_cross_section_model: full_response
available_cross_section_models: full_response, helm_sm
next_skill: cevns-detector-response
```

Stop after Gate X.
