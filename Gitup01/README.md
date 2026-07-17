# CEvNS-pyEFT Split Minimal Copy

This folder contains the phase-1 split modules and their compact check notebooks.

## Can The Files Run Alone?

The individual `.py` files are not standalone scripts. They are package modules and should be run through the `cevns_pyeft` package layout under `src/`.

Required companions:

- package `__init__.py` files under `src/cevns_pyeft/`
- `foundation/constants.py`
- `nuclear/response.py`
- `theory/li2026/*.py`
- `experiments/base.py`, `experiments/registry.py`, `experiments/coherent/*.py`
- `rates/differential.py`, `rates/counts.py`
- `data/responses/responses_all.json`
- COHERENT data files under `data/datafiles/`

The slow COHERENT count entry points are split by dataset:

- `cevns_pyeft.experiments.coherent.slow_counts_csi2017`
- `cevns_pyeft.experiments.coherent.slow_counts_csi2021`
- `cevns_pyeft.experiments.coherent.slow_counts_ar2020`

The old aggregate files `experiments/coherent/csi.py` and `experiments/coherent/argon.py` are intentionally not included in this minimal copy.

The three slow-count check notebooks compare against:

`backup/pre_split_reference_slow_counts.json`

## Run Imports Or Python Snippets

From this folder:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci; print('ok')"
```

Old compatibility imports for the split APIs also work:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.core import engine; print(engine.left_to_ci is not None)"
```

The compatibility `core.engine` in this folder only re-exports the split modules. It does not include the old monolithic fast-kernel, statistics, plotting, or Streamlit code.

Slow-count functions are also available through the registry:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.experiments.registry import get_slow_count_function; print(get_slow_count_function('CsI2021').__name__)"
```

## Run Notebook Checks

Notebook execution requires `nbconvert` and `ipykernel`. If they are not installed in the Python environment, install them into a local virtual environment first.

```powershell
Get-ChildItem -Path .\src\cevns_pyeft -Recurse -Filter *_check.ipynb | ForEach-Object {
    & ".\.venv\Scripts\python.exe" -m nbconvert --execute --to notebook --inplace $_.FullName
}
```

If using the shared Codex conda Python instead, replace the Python path accordingly.

## Fast Kernel Split Modules

This minimal copy also includes the fast-kernel split modules:

- `cevns_pyeft.kernels.basis`
- `cevns_pyeft.kernels.builder`
- `cevns_pyeft.kernels.reconstruction`
- `cevns_pyeft.kernels.storage`
- `cevns_pyeft.experiments.coherent.fast_kernel_csi2017`
- `cevns_pyeft.experiments.coherent.fast_kernel_csi2021`
- `cevns_pyeft.experiments.coherent.fast_kernel_ar2020`

The fast split keeps the current implementation basis size and pair count:

```text
basis size = 22
pair count = 231
```

Reference arrays for fast checks are included under:

`tests/reference_fast_split/`

Fast APIs are available both from their split modules and from the compatibility shim:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.core import engine; print(len(engine.li2026_left_basis()), engine.build_fast_kernel_csi2021.__name__)"
```

## Data-Driven Experiment Extension

This copy now includes the experiment-integration pack under project-native
paths so new experiments can be added without first hard-coding them into the
COHERENT modules.

Key locations:

```text
data/experiments/                         Data-driven experiment inputs
data/experiments/conus_plus_2025/         CONUS+ publication-facing template
data/experiments/conus_plus_2025_reproduction/
data/experiments/conus_legacy_mathematica/
schemas/experiment.schema.json            Minimal experiment YAML contract
schemas/csv_contracts.json                CSV table contracts
docs/experiment_integration/              Integration notes, specs, prompts
tools/experiment_integration/             Validation and data-prep helpers
```

The current CONUS+ publication-facing files intentionally keep missing official
likelihood inputs as templates. They should not be described as a complete
official likelihood reproduction until observed spectra, backgrounds,
efficiencies, and covariance inputs are supplied.

Experiment specs are discovered from:

```text
data/experiments/<dataset_directory>/experiment.yaml
```

Registry access:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.experiments.registry import list_experiments; print(list_experiments())"
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.experiments.registry import get_experiment_spec; print(get_experiment_spec('conus_plus_2025_reproduction').source_type)"
```

Validate the migrated experiment input package:

```powershell
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" tools/experiment_integration/validate_experiment_package.py
```

When adding a new experiment, start from:

```text
docs/experiment_integration/experiment_specs/EXPERIMENT_SPEC_TEMPLATE.md
docs/experiment_integration/INTEGRATE_CEVNS_EXPERIMENT_SKILL.md
```
