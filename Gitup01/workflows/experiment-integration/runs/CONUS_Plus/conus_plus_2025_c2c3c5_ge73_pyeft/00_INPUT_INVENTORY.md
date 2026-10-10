# Phase 0 Input Inventory — CONUS+

## Identity and gate state

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
scientific_claim: hybrid_approximate_signal_forward_model
scope_gate: APPROVED
pre_dataset_freeze: false
backup_quarantine_applied: true
```

This inventory records active inputs and candidate reuse points. It does not approve any
production implementation or convert a candidate callable into a verified physics dependency.

## Registered material inputs

| ID | Active path / locator | Role | Status | Important limitation |
| --- | --- | --- | --- | --- |
| S001 | `docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf` | Project migration physics note | USER_SUPPLIED | Not an official CONUS+ release; 119 kg-day convention not selected |
| S002 | `docs/CONUS_docs/2501.17843v2.pdf` | External phenomenology paper | USER_SUPPLIED | Natural-Ge result is reference-only for the Ge73-only contract |
| S003 | Current onboarding decisions | Dataset and physics choices | USER_CONFIRMED | Decisions remain bounded by the approved hybrid claim |

Recorded source hashes remain authoritative in `P00_SOURCE_REGISTER.yaml`.

## Canonical onboarding artifacts

All active experiment-specific onboarding files are under:

```text
docs/experiment_integration/experiment_inputs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/
workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/
```

Required onboarding artifacts present:

- `EXPERIMENT_USER_INPUT.md`
- `P00_SOURCE_REGISTER.yaml`
- `P01_EVIDENCE_LEDGER.yaml`
- `P02_MISSING_AND_CONFLICTS.md`
- `P03_PHYSICS_CONTRACT.yaml`
- `P04_DECISION_LOG.yaml`
- `P05_CONTRACT_STATUS.md`

## Active repository map

| Responsibility | Active candidate | Phase owner | Initial finding |
| --- | --- | --- | --- |
| Experiment schema | `schemas/experiment.schema.json` | P01 | Minimal schema; additional properties allowed |
| Spec discovery/loading | `src/cevns_pyeft/experiments/specs.py` | P01 | Phase 1 extends discovery recursively; flat legacy and nested experiment directories are both discovered |
| Registry | `src/cevns_pyeft/experiments/registry.py` | P10 | Existing CsI2017/CsI2021/Ar2020 registry must remain unchanged until release |
| Target wrapper/config | `src/cevns_pyeft/experiments/base.py` | P02 | Candidate shared dataclasses only; no CONUS target adapter exists |
| Nuclear response database | `src/cevns_pyeft/nuclear/response.py`, `data/responses/responses_all.json` | P02/P04 | `Ge73` key exists; physical channel mapping remains a Phase 2/4 review |
| Source state | `src/cevns_pyeft/sources/state.py` | P03 | Reusable state representation; no active reactor-spectrum adapter found |
| Kinematics | `src/cevns_pyeft/theory/kinematics.py` | P05 | Candidate shared two-body kinematics; units/boundaries require Phase 5 verification |
| CEvNS-pyEFT differential rate | `src/cevns_pyeft/rates/differential.py` | P04/P05 | Candidate shared LI2026 path; selected conventions require review |
| Count integration | `src/cevns_pyeft/rates/counts.py` | P07 | Candidate shared integration utilities; CONUS orchestration is absent |
| Fast basis/build/reconstruction | `src/cevns_pyeft/kernels/` | P08 | Reusable infrastructure exists; CONUS template meaning and full approved basis remain unresolved |
| Statistics | `src/cevns_pyeft/statistics/` | P09 | Not requested in current scope |
| Existing spec tests | `tests/test_experiment_specs.py` | P01/P10 | Must be extended for nested discovery without breaking flat legacy datasets |
| Shared physics regressions | `tests/test_rates_differential_flavor.py`, `tests/test_li2026_*`, `tests/test_nuclear_response_convention.py` | P04/P05/P10 | Existing regressions must remain passing for shared/core changes |

## Missing or phase-owned inputs

The following remain governed by `PROGRESSIVE_DETAIL_LOOP`:

- P01: resolved and machine-validated; the human implementation review remains pending.
- P02: Ge73 response/channel verification and nuclei-per-kg convention.
- P03: machine-readable Mueller coefficients and 32 Kopeikin nodes; interpolation and 2 MeV matching tests.
- P04/P08: complete approved Wilson basis/order and template semantics.
- P05: callable signatures, energy units and boundary behavior.
- P06: response normalization/truncation domain.
- P07/P10: Ge73-only authoritative Slow output and validation references.
- P09: official machine-readable data, only if statistics is later requested.

## Explicit exclusions

- `backup/**` is excluded from repository mapping, evidence, migration input and validation.
- The natural-Ge counts 90/143/113/346 are `REFERENCE_ONLY`.
- The 119 kg-day Fig. 1 effective comparison convention is not a runtime input.
- The Phase 1 dataset configuration and loader test coverage now exist; no CONUS source, detector, Slow, Fast, statistics, registry entry or cache has been implemented.

## Phase 1 machine result

- Dataset config: `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/experiment.yaml`.
- Loader: flat and nested `experiment.yaml` discovery supported.
- Direct dependency-free assertions: PASS.
- `pytest tests/test_experiment_specs.py`: NOT_RUN because `pytest` is not installed.
- P01 Machine Gate: PASS; Human implementation review: NOT_REVIEWED.
