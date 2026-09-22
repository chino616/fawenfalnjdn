# Phase 7 Slow Counts: CsI2017

## 1. Status

Gate L status: PASS

The direct Slow implementation is wired through the validated SNS source state,
shared Li2026 differential cross section, target-time normalization, and the
CsI2017 detector response.  After explicit user approval, authoritative Slow
reference arrays were generated from the direct Slow defaults and the saved
reference reproducibility test passes.

## 2. Reference Path Inspected

| Role | File | Symbol |
|---|---|---|
| Dataset Slow callable | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | `slow_counts_csi2017` |
| Source state and flux | `src/cevns_pyeft/experiments/coherent/sns.py` | `sns_component_state`, `loadNeutrinoEmpiricalFluxSNS` |
| Shared rate integration | `src/cevns_pyeft/rates/counts.py` | `_rate_per_kg` |
| Differential cross section | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |
| Detector efficiency | `src/cevns_pyeft/experiments/base.py` | `_interp_eff` |

Verified call chain:

```text
slow_counts_csi2017
-> loadNeutrinoEmpiricalFluxSNS("CsI2017")
-> sns_component_state(mu/e/mub)
-> _rate_per_kg
-> differential_cross_section_nn(..., rho=source_state)
-> deterministic PE = 1.17 * E_R_keV
-> COHERENT_eff.txt efficiency
-> bin integration over 25 PE bins
```

## 3. Public Output Contract

```text
callable: cevns_pyeft.experiments.coherent.slow_counts_csi2017.slow_counts_csi2017
return type: dict
bin axis: PE
shape: (25,)
unit: expected_events_per_bin
components: mu, e, mub, total
source states:
  mu  -> particle_kind=nu,     rho=|mu><mu|
  e   -> particle_kind=nu,     rho=|e><e|
  mub -> particle_kind=antinu, rho=|mu><mu|
```

Detector response remains scalar after `Tr(rho K)`.  No detector helper accepts
or folds a Flavor matrix.

## 4. Numerical Snapshot

Lightweight direct-integration settings used by the Phase 7 regression test:

```text
n_enu = 6
PE grid = 251 points from 0.001 to 50.0
detector mass multiplier = 14.6 kg
```

Current SM totals with these settings:

| component | total events |
|---|---:|
| mu | 28.048148797486174 |
| e | 39.46366914537668 |
| mub | 77.46507368744231 |
| total | 144.97689163030518 |

The pre-existing frozen Fast reference with matching coarse SNS grid gives
`144.19010104208792` total events.  After the Slow path was corrected to use
the Source Gate prompt-line energy (`29.792140909877446 MeV`) rather than the
legacy `29.65 MeV` literal, the relative difference is approximately
`5.46e-3` and is dominated by the prompt `mu` component.  This stale Fast array
predates the Flavor tensor storage schema and is not accepted as the
authoritative Slow reference.

Component-level stale-Fast comparison now lives in:

```text
workflows/experiment-integration/runs/CsI2017/artifacts/slow_vs_stale_fast_split_components.csv
```

It shows the total delta `+0.7867905882172579` events is almost entirely the
prompt `mu` component (`+0.7867962739236027` events).  The delayed `e` and
`mub` continua agree with the stale diagnostic at the `5e-8` relative level.

## 5. Tests

Generated diagnostic artifacts:

```text
workflows/experiment-integration/runs/CsI2017/artifacts/slow_bin_counts.csv
workflows/experiment-integration/runs/CsI2017/artifacts/slow_component_totals.csv
workflows/experiment-integration/runs/CsI2017/artifacts/slow_convergence.csv
workflows/experiment-integration/runs/CsI2017/artifacts/slow_vs_stale_fast_split_components.csv
workflows/experiment-integration/runs/CsI2017/figures/slow_bin_counts.png
workflows/experiment-integration/runs/CsI2017/figures/slow_convergence.png
```

Convergence diagnostics currently recorded:

| label | settings | total events | runtime_s |
|---|---|---:|---:|
| coarse | `{'n_enu': 6}` | 144.97689163030518 | 19.935365 |
| medium | `{'n_enu': 12}` | 167.55855004906758 | 45.729138 |

The diagnostic artifacts are not reference arrays.  They are current-state
evidence for the direct Slow chain and remain separate from the authoritative
Gate L saved reference.

Authoritative Gate L reference:

```text
tests/reference_CsI2017/slow_reference.npy
tests/reference_CsI2017/slow_reference.json
settings = {'n_enu': 120, 'direct_slow_defaults': True}
shape = (25,)
sum = 174.3932295894691
sha256 = 456542ed3fdcca6e91c17ca86fceb1034dc0144f7c17148500a4fa9d19582274
```

## 6. Tests

Executed:

```text
python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp tests/test_csi_slow_counts_phase7.py tests/test_csi_slow_source_state_p3.py
```

Result:

```text
39 passed

python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp tests/test_li2026_p0_contract.py tests/test_li2026_p1_csi_kernel.py tests/test_source_state_p2.py tests/test_li2026_units_contract.py tests/test_csi_slow_counts_phase7.py tests/test_csi_slow_source_state_p3.py
75 passed

python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp -k "not conus"
205 passed, 1 skipped, 33 deselected

python tools/experiment_integration/generate_csi_slow_references.py --dataset all --write-reference-arrays --acknowledge-reference-update "I approve updating CsI Slow reference arrays"
REFERENCE_WRITTEN for CsI2017 and CsI2021
```

The CsI Phase 7/source subset contains 39 collected tests.  Coverage added in
`tests/test_csi_slow_counts_phase7.py`:

- output shape, finite/nonnegative counts, and component sum;
- `counts_per_npe = counts_per_bin / bin_width`;
- `include_sm=False` with no NP coefficients gives zero counts;
- explicit `(3,3)` Flavor Wilson matrix input remains finite and nonnegative;
- Slow path has no Fast, reference-fast, statistics, or likelihood dependency.
- stale Fast split metadata is diagnosed as non-authoritative for Gate L.
- CsI Slow reference generation is non-writing by default and requires an
  explicit approval phrase before formal reference arrays can be saved.
- saved authoritative Slow reference arrays reproduce direct Slow defaults at
  `rtol=1e-12, atol=1e-12`.

## 7. Blockers

No CsI2017 Slow-counts blocker remains for Gate L.

Next action: proceed to P4/Fast only after preserving the Gate L Slow reference
contract.  The existing stale Fast split remains diagnostic-only and must not be
treated as a flavor-compatible Fast kernel.
