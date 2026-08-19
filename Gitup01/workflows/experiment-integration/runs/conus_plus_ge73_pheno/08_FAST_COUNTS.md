# Phase 8 Fast Counts: conus_plus_ge73_pheno

## Inputs

```text
dataset_id: conus_plus_ge73_pheno
experiment_spec: data/experiments/conus_plus_ge73_pheno/experiment.yaml
Slow callable: src.cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno.slow_counts_conus_plus_ge73_pheno
Slow reference: tests/reference_conus_plus_ge73_pheno/slow_reference.npy
required Fast representations: cumulative spectrum
optional blocked representation: EFT template Fast
```

Required state:

```text
Gate L = PASS
```

## Reference Code

Inspected only the Fast and kernel references listed in `CSI_REFERENCE_MAP.md`:

| Role | File | Symbol |
|---|---|---|
| Fast dataset wrapper | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py` | `build_fast_kernel_csi2021` |
| Fast dataset wrapper | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py` | `build_fast_kernel_csi2017` |
| Fast dataset wrapper | `src/cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py` | `build_fast_kernel_ar2020` |
| Basis definition | `src/cevns_pyeft/kernels/basis.py` | `BasisElement`, `li2026_left_basis_current` |
| Kernel builder | `src/cevns_pyeft/kernels/builder.py` | `build_matrixized_kernel`, `KernelPayload` |
| Reconstruction | `src/cevns_pyeft/kernels/reconstruction.py` | `reconstruct_counts_from_kernel` |
| Storage | `src/cevns_pyeft/kernels/storage.py` | `save_fastscan_template`, `load_fastscan_template` |

Verified interface conventions:

```text
Fast outputs must reproduce Slow bin axes, shape, and units.
Formal kernels require explicit basis metadata and serialization validation.
Saved representations need metadata checks to reject stale artifacts.
Validation is bin-by-bin, not only total counts.
```

No CsI/Ar kernel arrays, source models, detector models, or statistics were
copied.

## Representation Plan

| Representation | Required for release | Status | Parameter dependence | Blocker |
|---|---|---|---|---|
| cumulative spectrum | yes | IMPLEMENTED | fixed reconstructed spectrum for supplied coefficient point | none |
| EFT quadratic kernel | no | BLOCKED | full Wilson-coefficient basis template | complete 20-group EFT template basis mapping is not defined |
| response matrix | no | NOT_APPLICABLE | not requested | none |
| source cache | no | NOT_APPLICABLE | not requested | none |

The cumulative representation accelerates bin integration once a reconstructed
spectrum has been produced by the validated Slow path. It does not replace the
coefficient-dependent source, cross-section, detector-response, or exposure
calculation.

The formal EFT-template Fast remains blocked. No placeholder or partial kernel
was generated.

## Cumulative-Spectrum Fast

Implemented file:

```text
src/cevns_pyeft/experiments/conus/fast_cumulative_conus_plus_ge73_pheno.py
```

Public API:

```python
cumulative_fast_counts_conus_plus_ge73_pheno(
    slow_spectrum_callable=slow_counts_conus_plus_ge73_pheno,
    experiment_spec=None,
    *,
    coefficients=None,
    wc_triplets=None,
    left_wcs=None,
    include_sm=True,
    cross_section_model="full_response",
    kinematics="publication_reproduction",
    sin2thetaW=0.23873,
    c10_mass_mode="flavor",
    slow_integration_settings=None,
    fast_settings=None,
    return_representation=False,
)
```

Representation helpers:

```text
build_cumulative_fast_representation
reconstruct_counts_from_cumulative
save_cumulative_fast_representation
load_cumulative_fast_representation
validate_cumulative_fast_representation
```

Configuration:

```text
input spectrum: validated Slow reconstructed spectrum dN/dE_reco
sampling grid: 2 eVee default
interpolation rule: positive-spectrum log interpolation when possible
cumulative integration rule: trapezoid cumulative integral
bin reconstruction: F(E_high) - F(E_low)
f_floor: 1e-300
n_fit: 3 recorded metadata
n_cumulative: 2 recorded metadata
```

Saved representation:

```text
tests/reference_conus_plus_ge73_pheno/cumulative_reference.npz
tests/reference_conus_plus_ge73_pheno/cumulative_reference.json
```

## Validation Points

Validated points:

```text
sm_full_response
complex_c61u: wc_triplets[(6, 1, "u")] = 1.0e-8 + 2.0e-9j
helm_sm
```

Validation settings:

```text
n_true_recoil: 61
n_neutrino: 120
reco_step_evee: 2.0
relative tolerance: 1e-10
```

Diagnostic artifacts:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/fast_vs_slow.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/fast_runtime.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_vs_slow.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_vs_slow.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_relative_error.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_relative_error.pdf
```

Runtime and error summary:

| point | Slow total | Fast total | max abs error | max rel error | Slow runtime [s] | reconstruct runtime [s] | speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| sm_full_response | `150.4848297150` | `150.4848297150` | `4.796163466381e-14` | `5.757217090831e-14` | `2.424647199921` | `3.740005195141e-05` | `6.483004898152e+04` |
| complex_c61u | `151.4483698343` | `151.4483698343` | `3.919087276927e-14` | `1.512860019516e-13` | `3.888933399925` | `6.340001709759e-05` | `6.133962698999e+04` |
| helm_sm | `149.2233461214` | `149.2233461214` | `3.630429290524e-14` | `1.069373087233e-13` | `0.5447895000689` | `4.990003071725e-05` | `1.091761853125e+04` |

Worst point:

```text
point: complex_c61u
max_relative_error: 1.512860019516e-13
```

All 57 bin-by-bin comparisons passed.

## Production Files

Created:

```text
src/cevns_pyeft/experiments/conus/fast_cumulative_conus_plus_ge73_pheno.py
tests/test_conus_plus_ge73_pheno_cumulative_fast.py
tests/reference_conus_plus_ge73_pheno/cumulative_reference.npz
tests/reference_conus_plus_ge73_pheno/cumulative_reference.json
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/fast_vs_slow.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/fast_runtime.csv
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_vs_slow.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_vs_slow.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_relative_error.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/fast_relative_error.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/08_FAST_COUNTS.md
```

Modified:

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
backup/BACKUP_MANIFEST.md
```

Backup:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_fast_counts/experiment.yaml
```

Not modified:

```text
Slow implementation
Slow reference array
source physics
cross-section physics
detector-response physics
existing CsI/Ar Fast references
statistics modules
registry.py
```

## Experiment-Spec Update

`data/experiments/conus_plus_ge73_pheno/experiment.yaml` now records:

```text
spec_status: fast_validated
provenance.phase: FAST_VALIDATED
fast_counts.status: CUMULATIVE_VALIDATED_EFT_TEMPLATE_BLOCKED
fast_counts.validated_representations: [cumulative_spectrum]
fast_counts.blocked_representations: [eft_template_fast]
fast_counts.cumulative_spectrum_status: ADAPTER_VALIDATED
fast_counts.cumulative_spectrum_callable: src.cevns_pyeft.experiments.conus.fast_cumulative_conus_plus_ge73_pheno.cumulative_fast_counts_conus_plus_ge73_pheno
fast_counts.cumulative_spectrum_representation_file: tests/reference_conus_plus_ge73_pheno/cumulative_reference.npz
fast_counts.cumulative_spectrum_max_relative_error: 1.5128600195162766e-13
fast_counts.eft_template_fast_status: BLOCKED
phase1_boundaries.cumulative_fast_implemented: true
phase1_boundaries.eft_kernel_implemented: false
```

The Fast YAML fields are intentionally one-level nested because the current
repository `read_simple_yaml` helper supports only a small YAML subset.

## Tests

Focused cumulative Fast tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_cumulative_fast.py
......                                                                   [100%]
6 passed in 3.34s
```

Combined completed-phase tests:

```text
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests\test_conus_plus_ge73_pheno_source.py tests\test_conus_plus_ge73_pheno_theory.py tests\test_conus_plus_ge73_pheno_kinematics.py tests\test_conus_plus_ge73_pheno_detector_response.py tests\test_conus_plus_ge73_pheno_slow_counts.py tests\test_conus_plus_ge73_pheno_cumulative_fast.py
................................                                         [100%]
32 passed in 30.07s
```

Checks covered:

```text
public cumulative Fast callable loads
output shape, axis, and unit match Slow
finite nonnegative counts
bin-by-bin Slow agreement
serialization round trip
metadata validation
stale dataset metadata rejection
unsupported helm_sm + EFT input raises
diagnostic artifacts and figures exist
statistics dependency absent
EFT-template Fast remains blocked and unexposed
```

## Gate F

Representation results:

```text
cumulative_spectrum: PASS
eft_template_fast: BLOCKED, optional and not exposed as implemented
```

Overall:

```text
status: PASS
```

Reasons:

- The required cumulative-spectrum Fast representation passes bin-by-bin
  validation at SM, complex-coefficient, and Helm SM points.
- The saved representation round trips and rejects stale metadata.
- Fast outputs preserve Slow axes, shape, units, and component convention.
- No Slow implementation or Slow reference was changed to match Fast.
- No source, exposure, detector-response, or statistics factor is applied
  again by reconstruction.
- The incomplete EFT-template Fast is explicitly blocked and not marked
  implemented.

```text
next_skill: cevns-statistics
```

Stop after Gate F.
