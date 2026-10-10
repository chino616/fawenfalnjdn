# Experiment Migration Progress — CONUS+

This file is a reconstructible Master Skill index. It is not authority for
physics evidence, decisions, write approval, or Gate results. Resolve every
reference below against the cited ledger, contract, report, or authorization
record before resuming work.

```yaml
schema_version: 1
revision: 6
previous_revision: 5
updated_at: "2026-10-09T00:47:59+08:00"

workflow_status: ACTIVE
task_scope: physics_onboarding

experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft

scientific_claim_ref:
  path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P03_PHYSICS_CONTRACT.yaml
  field: scientific_claim
  decision_ref: D0003

checkpoint:
  phase_id: P02_P03
  phase_name: Target / Exposure and Source rebaseline review
  skill: cevns-experiment
  step_id: phase.P02.human_review
  next_action: "Review the equal-119 exposure implementation and the explicit Mueller 8-10 MeV extension limitation; after approval return to Phase 4 pre-code review."
  resume_requires:
    - decision:D0015:APPROVED
    - decision:D0016:APPROVED_AS_MODEL_ASSUMPTION
    - gate:P02.machine:PASS
    - gate:P03.machine:PASS

pending_decisions:
  - "P02/P03 post-rebaseline implementation review"
active_blockers: []

gates:
  P01:
    capability: dataset
    machine: PASS
    human: APPROVED
    evidence_fingerprint: 525B6F58B00E09EBABA190073B22813C5062E5DE2F220B32023BB6613F14A995
    report_ref: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/01_DATASET.md
    decision_refs: [D0009, D0010]
    depends_on: []
  P02:
    capability: target_exposure
    machine: PASS
    human: NOT_REVIEWED
    evidence_fingerprint: 718764473EAD6AFBF2BFAA91F690C900B4CDD63617D8BDAE58122EF5588ADAD5
    report_ref: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/02_DETECTOR_TARGET.md
    decision_refs: [D0004, D0005, D0011, D0012, D0015]
    depends_on: [P01]
  P03:
    capability: source
    machine: PASS
    human: NOT_REVIEWED
    evidence_fingerprint: D349FA29455213AED081116EC5FEB23B94422BB04303D42D515FF2193D037E38
    report_ref: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/03_SOURCE.md
    decision_refs: [D0013, D0014, D0016]
    depends_on: [P01]
  P04:
    capability: theory_response
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P01, P02]
  P05:
    capability: kinematics_cross_section
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P01, P02, P04]
  P06:
    capability: detector_response
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P01]
  P07:
    capability: slow_counts
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P01, P02, P03, P04, P05, P06]
  P08:
    capability: fast_counts
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P07]
  P09:
    capability: statistics
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P07]
  P10:
    capability: validation_release
    machine: NOT_RUN
    human: NOT_REVIEWED
    evidence_fingerprint: null
    report_ref: null
    decision_refs: []
    depends_on: [P01, P02, P03, P04, P05, P06, P07, P08]

authorization_refs:
  scope: D0008
  write: W0006

artifact_refs:
  source_register: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P00_SOURCE_REGISTER.yaml
  evidence_ledger: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P01_EVIDENCE_LEDGER.yaml
  missing_and_conflicts: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P02_MISSING_AND_CONFLICTS.md
  physics_contract: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P03_PHYSICS_CONTRACT.yaml
  decision_log: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P04_DECISION_LOG.yaml
  contract_status: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P05_CONTRACT_STATUS.md
  authorization_log: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/AUTHORIZATION_LOG.yaml
  input_inventory: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/00_INPUT_INVENTORY.md
  implementation_manifest: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/00_IMPLEMENTATION_MANIFEST.yaml
  phase_reports:
    P01: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/01_DATASET.md
    P02: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/02_DETECTOR_TARGET.md
    P03: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/03_SOURCE.md

source_fingerprints:
  - path: data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/experiment.yaml
    sha256: CBBAE61FFBDBC98D0ED4671CA9F5103901DBAC7B9EF3386CBF797EF3640786C6
    affects: [P01, P02, P03, P04, P05, P06, P07, P08, P10]
  - path: src/cevns_pyeft/experiments/specs.py
    sha256: 5B0633166370D9EC45D06BC2F9E069A319EBCA5A04C6B51C78CF070621DCDAC7
    affects: [P01, P10]
  - path: tests/test_experiment_specs.py
    sha256: 0CEE22E047549E7A758CF7B7B17460E3338E098F68829893B4DC33257DC95D56
    affects: [P01, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/00_IMPLEMENTATION_MANIFEST.yaml
    sha256: 43534DAE841955CBFEE66C060A0B41B276AA55BAF9AE53365F7776B80C38D9D2
    affects: [P01, P02, P03, P04, P05, P06, P07, P08, P09, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/01_DATASET.md
    sha256: 1BF43FDD505C5899B202A8D114DAAB8E8EA5C039F0814B4D9728B3F94C869739
    affects: [P01]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P01_EVIDENCE_LEDGER.yaml
    sha256: 6FA346EEB3E54D8D88A63A12BB1E34C92B2F143F6B95872CFA3E26449D08FD27
    affects: [P01, P02, P03, P04, P05, P06, P07, P08, P09, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P03_PHYSICS_CONTRACT.yaml
    sha256: 7DEF2B2A354A4BEA20FAE47891A8EF3E8D5CB460886BA2AEF4B89AC3E228D1F0
    affects: [P01, P02, P03, P04, P05, P06, P07, P08, P09, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P04_DECISION_LOG.yaml
    sha256: 5897A566B01A744734BAC7D632B9C6ED518C7341E9C26CA2102ADAED4850CF01
    affects: [P01, P02, P03, P04, P05, P06, P07, P08, P09, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P05_CONTRACT_STATUS.md
    sha256: 0A13FC809C28FD2FE0E063A04663DBD560615EADF834DE4C4DE991513DDB0C90
    affects: [P01, P02]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/AUTHORIZATION_LOG.yaml
    sha256: 6DDF48076F23741031E9234F66ADA7ABBCE9DDE2652A96A1CC184E085EF13DFA
    affects: []
  - path: docs/experiment_integration/experiment_inputs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/EXPERIMENT_USER_INPUT.md
    sha256: B3393303CA0DF00B0F5974047FE2CB2F27957605CB504DCF9D2B769BB8812581
    affects: [P02, P03, P04, P05, P06, P07, P08, P10]
  - path: src/cevns_pyeft/nuclear/response.py
    sha256: FC94A1582B11E58113E2F192BE9733DFAF5B27B2604FE075DA9E9F56B94D776F
    affects: [P02, P04, P07, P08, P10]
  - path: src/cevns_pyeft/rates/counts.py
    sha256: 776630B714F3CC0B03FAB897A4B4A34D25812744728654F38C4AB8AD2EA17733
    affects: [P02, P07, P10]
  - path: src/cevns_pyeft/foundation/constants.py
    sha256: 0BB51033D1CA64E18A7A7BB0FD4CCE38BC679558DD7392740F72D4683276CD44
    affects: [P02, P03, P04, P05, P07, P08, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/P02_MISSING_AND_CONFLICTS.md
    sha256: 293F3D0433DCE0399E1CFE2579107B22B750309721A13A36C5B5D152FCE43FE9
    affects: [P02, P03, P04, P05, P06, P07, P08, P09, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/02_DETECTOR_TARGET.md
    sha256: 718764473EAD6AFBF2BFAA91F690C900B4CDD63617D8BDAE58122EF5588ADAD5
    affects: [P02]
  - path: src/cevns_pyeft/experiments/conus_plus/__init__.py
    sha256: D9384BE64E10BD4D1AD9DABE67DA874C88B14A152BB5E272772DE3A5A6431FEB
    affects: [P03, P07, P08, P10]
  - path: src/cevns_pyeft/experiments/conus_plus/source.py
    sha256: DBD3DC2AEE9FC83C0A01E4CA938C50055598961520CCB324A62A6BB87878FCCE
    affects: [P03, P07, P08, P10]
  - path: data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/source/kopeikin_nodes.csv
    sha256: 8F9F3D7BA6EB695A92E9E81584987A450896D0A65B2FEE79589AE986282B5D56
    affects: [P03, P07, P08, P10]
  - path: data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/source/mueller_coefficients.csv
    sha256: 21CFEB811831656AD1773F2CBCB704EE6FBD99A6D9BB06A9A33AC520D1AF7B13
    affects: [P03, P07, P08, P10]
  - path: tests/test_conus_plus_source.py
    sha256: E1636777BBF15CB989A52590C0D9C805FA85E7CD372653E969A3403B357B8DEC
    affects: [P02, P03, P10]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/03_SOURCE.md
    sha256: D349FA29455213AED081116EC5FEB23B94422BB04303D42D515FF2193D037E38
    affects: [P03]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/diagnostics/03_source_spectrum.csv
    sha256: 9F60736291B6F2DCEFD4564B876E92F603EBC0365C3E690310ADC43176A92A64
    affects: [P03]
  - path: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/diagnostics/03_source_spectrum.png
    sha256: 3C4D8D919DB344C68B517A05ADE398037A6778FC24792D2ED83A0F22D3D96716
    affects: [P03]

stale_artifacts: []

handoff:
  state: FORMAL
  temporary_index_ref: null
  formal_index_ref: workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/00_MIGRATION_PROGRESS.md
  completed_at: "2026-10-01T02:56:28+08:00"
```

## Phase summary

| Phase/Gate | Capability | Machine | Human | Report | Next action |
|---|---|---|---|---|---|
| P01 | Dataset | PASS | APPROVED | `01_DATASET.md` | Complete |
| P02 | Target / Exposure | PASS | NOT_REVIEWED | `02_DETECTOR_TARGET.md` | Review the equal-119 calculation profile |
| P03 | Source | PASS | NOT_REVIEWED | `03_SOURCE.md` | Review the explicit 8–10 MeV extension limitation |
| P04 | Theory / Nuclear Response | NOT_RUN | NOT_REVIEWED | — | Start after P02/P03 rebaseline review |
| P05 | Kinematics / Cross Section | NOT_RUN | NOT_REVIEWED | — | Wait for prerequisite reviews |
| P06 | Detector Response | NOT_RUN | NOT_REVIEWED | — | Wait for its Phase review |
| P07 | Slow counts | NOT_RUN | NOT_REVIEWED | — | Blocked by P02–P06 |
| P08 | Fast counts | NOT_RUN | NOT_REVIEWED | — | Blocked by approved Slow |
| P09 | Statistics | NOT_RUN | NOT_REVIEWED | — | Requested benchmark starts after authoritative Slow |
| P10 | Validation / Release | NOT_RUN | NOT_REVIEWED | — | Blocked by requested capabilities |

## Reconstruction rule

If this file is missing, stale, corrupt, or references unavailable authority,
rebuild it from P00–P05 onboarding artifacts, valid Decision and Authorization
Log entries, the implementation manifest, current Phase reports, and current
fingerprints. Never infer approval from this index alone.
