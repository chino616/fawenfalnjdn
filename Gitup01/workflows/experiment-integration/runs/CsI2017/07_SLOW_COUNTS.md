# Phase 7 Slow Counts: CsI2017

## 1. Status

Gate L status: BLOCKED_PENDING_REFERENCE_ARRAY_APPROVAL

The direct Slow implementation is wired through the validated SNS source state,
shared Li2026 differential cross section, target-time normalization, and the
CsI2017 detector response.  The current user instruction forbids updating or
creating reference arrays in this pass, so the final Gate L reference-array
criterion is intentionally left open.

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

## 5. Tests

Generated diagnostic artifacts:

```text
workflows/experiment-integration/runs/CsI2017/artifacts/slow_bin_counts.csv
workflows/experiment-integration/runs/CsI2017/artifacts/slow_component_totals.csv
workflows/experiment-integration/runs/CsI2017/artifacts/slow_convergence.csv
workflows/experiment-integration/runs/CsI2017/figures/slow_bin_counts.png
workflows/experiment-integration/runs/CsI2017/figures/slow_convergence.png
```

Convergence diagnostics currently recorded:

| label | settings | total events | runtime_s |
|---|---|---:|---:|
| coarse | `{'n_enu': 6}` | 144.97689163030518 | 19.935365 |
| medium | `{'n_enu': 12}` | 167.55855004906758 | 45.729138 |

The diagnostic artifacts are not reference arrays.  They are current-state
evidence for the direct Slow chain and remain separate from the final Gate L
saved-reference criterion.

## 6. Tests

Executed:

```text
python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp tests/test_csi_slow_counts_phase7.py tests/test_csi_slow_source_state_p3.py
```

Result:

```text
35 passed
```

The CsI Phase 7/source subset contains 35 collected tests.  Coverage added in
`tests/test_csi_slow_counts_phase7.py`:

- output shape, finite/nonnegative counts, and component sum;
- `counts_per_npe = counts_per_bin / bin_width`;
- `include_sm=False` with no NP coefficients gives zero counts;
- explicit `(3,3)` Flavor Wilson matrix input remains finite and nonnegative;
- Slow path has no Fast, reference-fast, statistics, or likelihood dependency.

## 7. Blockers

Gate L cannot be marked PASS in this pass because the workflow template requires
an independently generated Slow reference array, while the current instruction
is not to update reference arrays.

Next action: after explicit approval for new CsI Slow reference arrays, generate
`tests/reference_CsI2017/slow_reference.npy` from the direct Slow calculation,
add saved-reference reproducibility checks, then update `experiment.yaml` to
`slow_validated: true`.
