# Phase 7 Slow Counts: CsI2021

## 1. Status

Gate L status: BLOCKED_PENDING_REFERENCE_ARRAY_APPROVAL

The direct Slow implementation is wired through the validated SNS source state,
shared Li2026 differential cross section, target-time normalization, and the
CsI2021 detector response.  The current user instruction forbids updating or
creating reference arrays in this pass, so the final Gate L reference-array
criterion is intentionally left open.

## 2. Reference Path Inspected

| Role | File | Symbol |
|---|---|---|
| Dataset Slow callable | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `slow_counts_csi2021` |
| Source state and flux | `src/cevns_pyeft/experiments/coherent/sns.py` | `sns_component_state`, `loadNeutrinoEmpiricalFluxSNS` |
| Shared bin integration | `src/cevns_pyeft/rates/counts.py` | `bin_events_csi`, `empirical_dNdPE_response_csi` |
| Differential cross section | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |
| Detector response | `src/cevns_pyeft/rates/differential.py` | `p_smearing_csi` |
| Detector efficiency | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `efficiency_csi2021` |

Verified call chain:

```text
slow_counts_csi2021
-> loadNeutrinoEmpiricalFluxSNS("CsI2021")
-> sns_component_state(mu/e/mub)
-> bin_events_csi
-> empirical_dNdPE_response_csi
-> differential_cross_section_nn(..., rho=source_state)
-> p_smearing_csi Gamma detector response
-> efficiency_csi2021
-> bin integration over 9 PE bins
```

## 3. Public Output Contract

```text
callable: cevns_pyeft.experiments.coherent.slow_counts_csi2021.slow_counts_csi2021
return type: dict
bin axis: PE
shape: (9,)
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
n_er = 5
n_enu = 12
n_pe_bin = 3
detector mass = 14.57 kg
component acceptance = {mu: 0.997, e: 0.848, mub: 0.848}
```

Current SM totals with these settings:

| component | total events |
|---|---:|
| mu | 78.61895135672657 |
| e | 115.11368415447335 |
| mub | 188.15861336380596 |
| total | 381.8912488750059 |

The pre-existing frozen Fast reference with its own very coarse settings gives
`100.6872151330029` total events, while current direct Slow under matching
coarse nominal settings gives `100.55493552434457`.  The dominant difference is
in the delayed `mub` component and is unchanged by temporarily reverting the
Slow support threshold to the old heavy-nucleus approximation.  That indicates
the mismatch is not a source-state orientation error and should not be repaired
by changing Slow to match stale Fast output.

The old Fast array predates the Flavor tensor storage schema and is not accepted
as the authoritative Slow reference.  The Slow PE interpolation grid now
rejects an automatically generated `pe_step` coarser than the smallest PE bin
width, because such settings alias the detector response and can inflate the
diagnostic totals by orders of magnitude.

## 5. Tests

Generated diagnostic artifacts:

```text
workflows/experiment-integration/runs/CsI2021/artifacts/slow_bin_counts.csv
workflows/experiment-integration/runs/CsI2021/artifacts/slow_component_totals.csv
workflows/experiment-integration/runs/CsI2021/artifacts/slow_convergence.csv
workflows/experiment-integration/runs/CsI2021/artifacts/ar2020_shared_counts_nonregression.csv
workflows/experiment-integration/runs/CsI2021/figures/slow_bin_counts.png
workflows/experiment-integration/runs/CsI2021/figures/slow_convergence.png
```

Convergence diagnostics currently recorded:

| label | settings | total events | runtime_s |
|---|---|---:|---:|
| coarse | `{'n_er': 3, 'n_enu': 6, 'n_pe_bin': 3}` | 100.55493552434457 | 2.354932 |
| medium | `{'n_er': 5, 'n_enu': 12, 'n_pe_bin': 3}` | 381.8912488750059 | 20.206881 |

Ar2020 shared-counts non-regression diagnostic:

| settings | total events | finite | nonnegative |
|---|---:|---|---|
| `{'n_er': 3, 'n_enu': 6, 'n_pe_bin': 3}` | 23.203475634474284 | True | True |

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
`tests/reference_CsI2021/slow_reference.npy` from the direct Slow calculation,
add saved-reference reproducibility checks, then update `experiment.yaml` to
`slow_validated: true`.
