# Phase 1 Split Report

## Status

Completed the phase-1 safe split scope requested in:

- `md-GPT/2026-07-15 CEvNS_pyEFT_phase1_split_plan.md`
- `md-GPT/2026-07-15 CEvNS_pyEFT_phase1_split_plan(1).md`

`core/engine.py` remains as the compatibility entry point and re-exports migrated names.

## Backup Records

Backups were created before modifying existing files and recorded in `backup/BACKUP_MANIFEST.md`.

Key source backups:

- `src/cevns_pyeft/core/engine.py`
  - `backup/20260715_120601__src__cevns_pyeft__core__engine.py`
  - `backup/20260715_121547__src__cevns_pyeft__core__engine.py`
  - `backup/20260715_122717__src__cevns_pyeft__core__engine.py`
  - `backup/20260715_123151__src__cevns_pyeft__core__engine.py`
  - `backup/20260715_124739__src__cevns_pyeft__core__engine.py`
  - `backup/20260715_125447__src__cevns_pyeft__core__engine.py`

Other modified existing files also have manifest entries:

- `src/cevns_pyeft/theory/li2026/__init__.py`
- `src/cevns_pyeft/experiments/coherent/__init__.py`
- `src/cevns_pyeft/experiments/coherent/csi.py`
- `src/cevns_pyeft/experiments/__init__.py`
- `src/cevns_pyeft/rates/__init__.py`
- `src/cevns_pyeft/rates/differential.py`
- `src/cevns_pyeft/rates/counts.py`

## Migration Map

- `core.engine` base constants, unit conversions, and coefficient definitions
  -> `foundation/constants.py`
- `core.engine.ResponseW`, `ResponseDB`, response polynomial helpers
  -> `nuclear/response.py`
- `core.engine.FormFactors`, `build_form_factors`, q2 unit helpers
  -> `theory/li2026/form_factors.py`
- `core.engine.Li2026LECs`, `DEFAULT_LECS`, `as_dict`
  -> `theory/li2026/lec.py`
- `core.engine.CiPN`, `LeftKinematics`, `left_to_ci`
  -> `theory/li2026/left_to_ci.py`
- `core.engine.RKinematics`, `responses_R`, `compute_R_matrices`
  -> `theory/li2026/responses.py`
- `core.engine.Amp2Result`, `amplitude_squared_onebody_li2026`
  -> `theory/li2026/amplitude.py`
- `core.engine.dsigma_dER_li2026_cm2_per_GeV`
  -> `theory/li2026/cross_section.py`
- COHERENT SNS flux datasets and loaders
  -> `experiments/coherent/sns.py`
- CsI2021 efficiency and CsI2017 slow wrapper
  -> `experiments/coherent/csi.py`
- Ar2020 data constants and slow wrapper
  -> `experiments/coherent/argon.py`
- Experiment path/table helpers and minimal config dataclasses
  -> `experiments/base.py`
- Minimal experiment registry
  -> `experiments/registry.py`
- Slow differential cross section and dR/dT helpers
  -> `rates/differential.py`
- Slow dN/dPE and bin expected counts helpers
  -> `rates/counts.py`

## Not Migrated

As required by the updated plan, these remain in `core/engine.py`:

- Compatibility re-exports for migrated public APIs
- Fast-scan kernel machinery
- Saved-kernel template helpers

These packages were not modified:

- `statistics/`
- `kernels/`
- `plotting/`

Helm files were created as placeholders only:

- `theory/helm/__init__.py`
- `theory/helm/form_factor.py`
- `theory/helm/cross_section.py`

## Interface Adjustments

No public physics API was intentionally changed.

The old imports continue to work through `core/engine.py` re-exports, for example:

```python
from cevns_pyeft.core.engine import ResponseDB, slow_counts_csi2021
```

The updated implementation-level adjustment is in `rates/differential.py`: `differential_cross_section_nn` now imports `amplitude_squared_onebody_li2026` directly from `theory/li2026/amplitude.py`. New split modules do not import `core.engine`.

## Tests And Checks

Environment:

```text
Python: F:\Work\.codex_conda_envs\codex-py311\python.exe
pytest: 9.1.1
```

After installing pytest, tests were executed with `python -m pytest -q`. Source/test files were also syntax-compiled.

Passed checks:

- Full `py_compile` over `src/` and `tests/`
- `python -m pytest -q`: 14 passed
- `python -m nbconvert --execute --to notebook --inplace ...`: 15 split notebooks passed
- Existing import smoke check
- Existing path smoke check
- Split component checks:
  - `tests/test_foundation_constants.py`
  - `tests/test_nuclear_response.py`
  - `tests/test_li2026_components.py`
  - `tests/test_coherent_experiments.py`
  - `tests/test_rates_split.py`
  - `tests/test_experiment_slow_wrappers.py`
- Fast-kernel smoke checks:
  - `build_fast_kernel_csi2021`
  - `build_fast_kernel_csi2017`
  - `build_fast_kernel_ar2020`

Numerical old-vs-new comparisons used:

```text
rtol = 0
atol = 0
```

Verified old-vs-new totals with small grids:

```text
slow_counts_csi2017: 342.62089359028045
slow_counts_ar2020: 197.00486667061836
slow_counts_csi2021: 773.8789850850715
```

For compared arrays, bin values, shapes, and dtypes were unchanged.

## Split Check Notebooks

The updated plan requires one compact notebook next to each migrated implementation module. These were added and executed:

- `foundation/constants_check.ipynb`
- `nuclear/response_check.ipynb`
- `theory/li2026/lec_check.ipynb`
- `theory/li2026/form_factors_check.ipynb`
- `theory/li2026/left_to_ci_check.ipynb`
- `theory/li2026/responses_check.ipynb`
- `theory/li2026/amplitude_check.ipynb`
- `theory/li2026/cross_section_check.ipynb`
- `experiments/base_check.ipynb`
- `experiments/registry_check.ipynb`
- `experiments/coherent/sns_check.ipynb`
- `experiments/coherent/csi_check.ipynb`
- `experiments/coherent/argon_check.ipynb`
- `rates/differential_check.ipynb`
- `rates/counts_check.ipynb`

Notebook execution tools were installed only in the project-local `.venv`, not in `F:\Work\.codex_conda_envs\codex-py311`.

## Known Constraint

The project directory is not a Git repository, so `git status` cannot be used for Phase 0 status capture in this folder.
