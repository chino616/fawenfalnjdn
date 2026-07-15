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

## Run Notebook Checks

Notebook execution requires `nbconvert` and `ipykernel`. If they are not installed in the Python environment, install them into a local virtual environment first.

```powershell
Get-ChildItem -Path .\src\cevns_pyeft -Recurse -Filter *_check.ipynb | ForEach-Object {
    & ".\.venv\Scripts\python.exe" -m nbconvert --execute --to notebook --inplace $_.FullName
}
```

If using the shared Codex conda Python instead, replace the Python path accordingly.
