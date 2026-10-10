# Contract Status — conus_plus_2025_c2c3c5_ge73_pyeft

## Onboarding gates

```yaml
task_scope: physics_onboarding
input_mode: guided
execution_mode: stepwise
pre_dataset_freeze: false
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
dataset_identity_human_gate: APPROVED
scientific_claim_human_gate: APPROVED
onboarding_machine_gate: PASS
onboarding_human_gate: APPROVED
scope_human_gate: APPROVED
p01_contract_human_gate: APPROVED
p01_machine_gate: PASS
p01_implementation_human_gate: APPROVED
p02_contract_human_gate: APPROVED
p02_machine_gate: PASS
p02_implementation_human_gate: NOT_REVIEWED
p03_contract_human_gate: APPROVED
p03_machine_gate: PASS
p03_implementation_human_gate: NOT_REVIEWED
current_phase: phase_2_3_rebaseline_human_review
```

Master Scope Gate 已获批，`pre_dataset_freeze` 已解除。任何 production 写入仍必须通过
对应 Phase 的 Physics Gate 和路径级 Write Approval Gate。

## Approved core

- Dataset: C2/C3/C5 hybrid configuration.
- Target: Ge73-only.
- Selected calculation exposure: C2=C3=C5=119 kg day; the raw observed values remain reference metadata.
- Source: fixed detector-site flux, Kopeikin–Mueller piecewise model; 8–10 MeV is an explicit baseline extension beyond the 2–8 MeV fit domain.
- Detector: detector-specific exact step efficiency.
- Theory: project Ge73 nuclear Response, `sin²θW=0.23857`, CEvNS only.
- Scientific claim: `hybrid_approximate_signal_forward_model`.
- Publication counts 90/143/113/346: `REFERENCE_ONLY`.

## Progressive phase readiness

| Phase | Status | Current reason |
| --- | --- | --- |
| 1 Dataset | COMPLETE | Machine Gate passed and the reviewed implementation was approved by the user |
| 2 Target/Exposure | MACHINE PASS / REVIEW | Three independently calculated 119 kg day exposures and unique normalization ownership pass; revised result awaits human review |
| 3 Source | MACHINE PASS / REVIEW | Existing baseline passes; 2–8 MeV fit domain and 8–10 MeV extension limitation await human review |
| 4 Theory/Response | DRAFT / NEXT AFTER REVIEW | Project Ge73 Response mapping and Wilson-template scope require pre-code review |
| 5 Kinematics/Cross section | DRAFT | Actual callable, exact units and boundary convention require inspection |
| 6 Detector response | DRAFT | Response normalization domain requires decision |
| 7 Slow | BLOCKED | Depends on approved Phases 1–6 |
| 8 Fast | BLOCKED | Requires approved Slow; EFT kernel also lacks complete basis/order |
| 9 Statistics | DRAFT / REQUESTED | Starts after authoritative Slow; digitized excess requires the Data Semantics Gate |
| 10 Validation/Release | BLOCKED | Depends on implemented capabilities |

## Allowed claims now

- The dataset identity and intended hybrid model are user-approved.
- The two source PDFs and their differing physical scopes are registered.
- The selected exposure values and source-domain metadata pass focused machine checks; their revised human review is pending.
- Theory choices remain onboarding inputs awaiting Phase 4 verification.

## Not allowed claims now

- No end-to-end physical event-rate capability is available because Theory through Slow remain incomplete.
- No Slow or Fast calculation is validated.
- This is not an official CONUS+ natural-germanium reproduction.
- The 90/143/113/346 paper prediction is not a Ge73-only benchmark.
- No official likelihood or statistical reproduction is available.

## Next action

Review the P02/P03 rebaseline: three independent 119 kg day calculations, retention of raw
exposures as metadata, and the explicit Mueller 8–10 MeV extension limitation. After that review,
the mainline returns to the Phase 4 pre-code review. No Phase 4 implementation or benchmark write
is approved yet.
