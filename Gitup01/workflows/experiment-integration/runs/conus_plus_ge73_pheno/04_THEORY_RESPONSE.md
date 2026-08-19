# Phase 4 Theory and Nuclear Response: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
input_inventory: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
implementation_manifest: workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
target_response_key: Ge73
theory_status: REUSE
response_status: REUSE
```

Required previous state:

```text
Gate I = PASS
Gate D0 = PASS
Gate T0 = PASS
Gate S0 = PASS
```

## Approved Theory Contract

```text
incoming flavor: electron_antineutrino
neutrino or antineutrino: antineutrino source; shared Li2026 path uses flavor-indexed LEFT coefficients
outgoing flavor treatment: no experiment-specific flavor conversion in this phase
theory baseline: shared Li2026 one-body amplitude
Wilson basis: LEFT coefficient triplets plus existing SM helper
coefficient order: repository-native triplet keys (dimension, operator index, quark label)
complex coefficients supported: yes by shared amplitude input mapping
target isotope: Ge73
Response key: Ge73
new Lorentz structure: no
new propagator structure: no
```

## Reference Code

| Role | File | Symbol |
|---|---|---|
| Response loader | `src/cevns_pyeft/nuclear/response.py` | `ResponseDB` |
| Response object | `src/cevns_pyeft/nuclear/response.py` | `ResponseW` |
| Response evaluator | `src/cevns_pyeft/nuclear/response.py` | `ResponseW.W_np`, `ResponseW.W_iso` |
| Theory response contraction | `src/cevns_pyeft/theory/li2026/responses.py` | `compute_R_matrices` |
| Amplitude entry point | `src/cevns_pyeft/theory/li2026/amplitude.py` | `amplitude_squared_onebody_li2026` |
| Shared cross-section caller | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |

Reference path:

```text
data/responses/responses_all.json
→ ResponseDB("...").get("Ge73")
→ ResponseW
→ amplitude_squared_onebody_li2026(...)
→ Amp2Result.amp2
```

Verified contract:

```text
Response input variable: y = (0.5 q b)^2
Response basis labels: np basis with p,n labels; iso basis available through W_iso
Response channel labels: Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP
amplitude input arguments: ResponseW, E_nu_GeV, ER_keV, left_hat, basis, c10_mass_mode
energy units: GeV for amplitude entry point
recoil units: keV
return type: Amp2Result
return shape: scalar object with total amp2 and per-channel pieces
```

No experiment-specific amplitude or nuclear Response implementation was
created.

## Nuclear-Response Diagnostics

Grid definition:

```text
recoil grid: 0.0 to 4.0 keVnr inclusive, 41 points
recoil unit: keVnr
target mass: A * AMU_GEV, A = 73
q definition: q = sqrt(2 m_A T)
q unit: MeV in output CSV
dimensionless response variable: y = (0.5 q b)^2
grid size: 1312 rows = 41 recoil points x 8 channels x 2 x 2 np basis entries
```

Created:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/nuclear_response_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/nuclear_response_channels.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/nuclear_response_channels.pdf
```

The figure is nonblank and shows raw `W_np` channel values versus recoil.
Individual channels or interference entries are not forced nonnegative.

## Theory Benchmarks

Created:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/theory_response_benchmarks.csv
```

Benchmarks:

| Benchmark | E_nu [MeV] | Recoil [keVnr] | Coefficient point | Amplitude squared | Finite | Nonnegative |
|---|---:|---:|---|---:|---|---|
| `sm_low_recoil` | 2.0 | 0.05 | SM | `9.805216750533882e-13` | yes | yes |
| `sm_mid_recoil` | 5.0 | 0.50 | SM | `3.3892758353508845e-12` | yes | yes |
| `sm_upper_recoil` | 10.0 | 2.50 | SM | `6.1456336886785915e-12` | yes | yes |
| `zero_bsm_mid_recoil` | 5.0 | 0.50 | zero BSM | `0.0` | yes | yes |

## Implementation Decision

```text
theory classification: REUSE
Response classification: REUSE
reason: shared Li2026 amplitude accepts the repository-native LEFT coefficient triplets and Ge73 Response exists
shared files reused:
  src/cevns_pyeft/nuclear/response.py
  data/responses/responses_all.json
  src/cevns_pyeft/theory/li2026/amplitude.py
  src/cevns_pyeft/theory/li2026/responses.py
new code required: no theory or Response code
diagnostic artifacts: yes
```

## Files

### Created

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/nuclear_response_grid.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/theory_response_benchmarks.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/nuclear_response_channels.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/nuclear_response_channels.pdf
tests/test_conus_plus_ge73_pheno_theory.py
workflows/experiment-integration/runs/conus_plus_ge73_pheno/04_THEORY_RESPONSE.md
```

### Modified

```text
None.
```

### Must Not Modify

```text
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
src/cevns_pyeft/theory/li2026/
existing experiment implementations
existing reference arrays
```

## Tests

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_theory.py
...                                                                      [100%]
3 passed in 0.43s
```

Checks:

```text
Response key exists
A, Z, N match Ge73
expected channels are available
shared amplitude callable loads
SM amplitude is finite and nonnegative
diagnostic CSV values are finite
benchmark CSV values are finite and nonnegative
diagnostic figure exists and is nonempty
```

## Gate T1

```text
status: PASS
```

Reasons:

- The approved theory is covered by the shared Li2026 implementation.
- The approved `Ge73` target Response loads.
- Response basis and channel conventions are documented.
- Response diagnostics and theory benchmarks were generated.
- Focused tests pass.
- No experiment-specific theory or Response code was created.

## Next Skill

```text
cevns-kinematics-cross-section
```

Do not execute detector response or later phases automatically.
