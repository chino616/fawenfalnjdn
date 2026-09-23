# Legacy statistics migration gate report

## Gate S-1

Migration source is fixed to:

`F:/Work/2026-07-15 CEvNSpyEFT-Local/CEvNS-pyEFT-main/CEvNS-pyEFT-main`

The source directory is not itself a git repository, so commit/branch is recorded as unavailable. File identity is frozen by size and SHA256 in `tests/reference/statistics_legacy/metadata.json`.

Target worktree:

`F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01`

Target commit at migration start: `f61399cf8401b2b48dc9d4c4043f548811170721` on `flavor-v6`.

Gate S-1 status: PASS for unique local source identity by absolute path and SHA256.

## Gate S0 Inventory

| Old file | Line range | Responsibility | Dependencies | Side effects | New destination | Action |
|---|---:|---|---|---|---|---|
| `cutoff_single.py` | 1-58 | imports, scipy fallbacks, engine coupling, confidence constants | `core.engine`, scipy, pandas, matplotlib/PIL optional | imports engine | `confidence.py`, reports | SPLIT |
| `cutoff_single.py` | 84-190 | old engine kernel build/save/load and scalar coefficient helpers | `core.engine` | filesystem I/O on demand | deferred predictor/scan compatibility notes | DEFER |
| `cutoff_single.py` | 201-272 | CsI2021 data contract and analytic two-pull chi2 | engine arrays | none | `datasets.py`, `profiling.py`, `likelihoods.py` | MOVE |
| `cutoff_single.py` | 303-427 | scalar prediction and polynomial extraction | old kernel format | none | `predictors.py` later if legacy scalar kernels are restored | DEFER |
| `cutoff_single.py` | 527-844 | 1D minima, interval extraction, adaptive threshold crossings | scipy optional | none | `confidence.py` | MOVE |
| `cutoff_single.py` | 874-1063 | 1D operator scan control | old kernel polynomial | none | `scans.py` simplified; full scalar operator coverage deferred | SPLIT |
| `cutoff_single.py` | 1109-1513 | plotting, CLI, batch outputs | pandas, matplotlib/PIL, argparse | writes output files when run | not runtime statistics | DEFER |
| `cutoff_multi.py` | 123-283 | component specs for CsI2021/CsI2017/Ar2020; CsI2017 text loading | engine arrays, datafiles | reads text files on call | `datasets.py` | MOVE |
| `cutoff_multi.py` | 404-450 | observable conversion and CsI profile likelihoods | none after split | none | `observables.py`, `likelihoods.py` | MOVE |
| `cutoff_multi.py` | 453-570 | Ar asymmetric sigma, IRLS, bounded minimize | scipy optional | none | `profiling.py`, `likelihoods.py` | MOVE |
| `cutoff_multi.py` | 582-688 | multi-experiment chi2 sum and scale estimate | old polynomial model | none | `likelihoods.py`, `scans.py` | SPLIT |
| `cutoff_multi.py` | 927-1156 | multi-experiment 1D scan | old kernels | none | `scans.py` minimal; full legacy scan deferred | DEFER |
| `chi2_2d.py` | 1-370 | plotting helpers and top-level `core` alias | `core.engine`, plotting | imports engine at module import | plotting deferred | DEFER |
| `chi2_2d.py` | 371-1085 | Flow A data classes, confidence constants, NSI conversion, CsI/Ar chi2 | `core.engine`, hard-coded `1.1664e-5` | imports engine arrays | `confidence.py`, `parameters.py`, `profiling.py` | SPLIT |
| `chi2_2d.py` | 1086-1508 | Flow A kernel-backed 2D scan for CsI2021/Ar2020/joint | saved legacy kernels | reads kernel files on call | `scans.py`, `predictors.py` later | DEFER |
| `chi2_2d.py` | 1502-1810 | Flow A COH combined API and CLI | output writers | writes files on call | scan API deferred | DEFER |
| `chi2_2d.py` | 1868-1912 | Flow B repo/data discovery and import-time CsI2017 data loading | data/datafiles | reads COHERENT text files at import time | `datasets.py` lazy loading | MOVE and remove side effect |
| `chi2_2d.py` | 1915-1940 | Flow B CsI2017 one-alpha likelihood | module globals | none after import | `profiling.py`, `likelihoods.py` | MOVE |
| `chi2_2d.py` | 2019-2188 | Flow B ee/mumu scans and grid combination | Flow B component object | console progress; no import write | `scans.py` later with workflow identity retained | DEFER |
| `chi2_2d.py` | 2209-2404 | Flow B plotting, output bundle, complete workflow | plotting/filesystem | writes outputs on call | plotting deferred | DEFER |

Gate S0 status: PASS for major code-region accounting. Flow A and Flow B are distinct; the Flow B import-time text-file read has been eliminated in the new implementation.

## Gate S0.5/S0.6/S0.7

Provenance records now live under:

- `data/experiments/CsI2021/statistics/provenance.yaml`
- `data/experiments/CsI2017/statistics/provenance.yaml`
- `data/experiments/Ar2020/statistics/provenance.yaml`

Observable contracts:

- CsI2021 likelihood observable: `counts/PE`; raw predictor output is `events/bin`; conversion divides by PE bin width explicitly in `observables.py`.
- CsI2017 likelihood observable: `counts/bin`.
- Ar2020 likelihood observable: `counts/bin`.

Confidence conventions:

- 1D legacy: 90/95/99 percent use 2.71/3.84/6.63.
- 2D Flow A table: 90 percent uses 4.61.
- 2D Flow B complete NSI constants: 90 percent uses 4.61.
- Old rounded API default `COHERENT_2D_90CL_THRESHOLD = 4.6` is kept as `legacy_2d_90_rounded_api`; it is not silently merged with 4.61.

Gate status: PASS for legacy reproduction/provenance honesty; PHYSICS_VALIDATED remains NO.

## Gate S1/S2

Legacy numerical artifacts are generated by `tools/statistics/generate_legacy_statistics_reference.py` directly from `CEvNS-pyEFT-main`. New pure-statistics tests compare against those artifacts.

Validation status: LEGACY_REPRODUCED for fixed profile cases; PROVENANCE_BLOCKED for official likelihood claims.
