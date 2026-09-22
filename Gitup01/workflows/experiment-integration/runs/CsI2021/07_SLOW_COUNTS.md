# Phase 7 Slow Counts: CsI2021

## 1. Status

Gate L status: PASS

The direct Slow implementation is wired through the validated SNS source state,
shared Li2026 differential cross section, target-time normalization, and the
CsI2021 detector response.  After explicit user approval, authoritative Slow
reference arrays were generated from the direct Slow defaults and the saved
reference reproducibility test passes.

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

Component-level stale-Fast comparison now lives in:

```text
workflows/experiment-integration/runs/CsI2021/artifacts/slow_vs_stale_fast_split_components.csv
```

It shows the total delta `-0.13227960865830823` events is dominated by the
delayed `mub` component (`-0.1314554726063193` events).  The prompt `mu`
component is numerically negligible in both coarse diagnostics.

## 5. Tests

Generated diagnostic artifacts:

```text
workflows/experiment-integration/runs/CsI2021/artifacts/slow_bin_counts.csv
workflows/experiment-integration/runs/CsI2021/artifacts/slow_component_totals.csv
workflows/experiment-integration/runs/CsI2021/artifacts/slow_convergence.csv
workflows/experiment-integration/runs/CsI2021/artifacts/ar2020_shared_counts_nonregression.csv
workflows/experiment-integration/runs/CsI2021/artifacts/slow_vs_stale_fast_split_components.csv
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
evidence for the direct Slow chain and remain separate from the authoritative
Gate L saved reference.

Authoritative Gate L reference:

```text
tests/reference_CsI2021/slow_reference.npy
tests/reference_CsI2021/slow_reference.json
settings = {'n_er': 21, 'n_enu': 120, 'n_pe_bin': 8, 'pe_step': 3.0, 'direct_slow_defaults': True}
shape = (9,)
sum = 332.9338350257275
sha256 = e180acc63414b2a29d8ab13482d768c9cb47d7c64cce2271d50ad0af26d24292
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

No CsI2021 Slow-counts blocker remains for Gate L.

Next action: proceed to P4/Fast only after preserving the Gate L Slow reference
contract.  The existing stale Fast split remains diagnostic-only and must not be
treated as a flavor-compatible Fast kernel.
