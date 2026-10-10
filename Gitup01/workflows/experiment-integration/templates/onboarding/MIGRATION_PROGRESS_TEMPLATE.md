# Experiment Migration Progress

本文件是 Master Skill 的**可重建主线索引**，不是批准、科学证据或 Gate 结果的权威
记录。所有 `APPROVED` 状态必须能解析到 Decision Log、Phase 报告或 Authorization
Log 中仍适用于当前 artifact revision 的记录。

普通问答、比较、解释和只读检查不更新本文件。更新前先写权威记录、核对写入授权，
并确认磁盘上的 `revision` 仍等于更新者读取的 revision。

```yaml
schema_version: 1
revision: 0
previous_revision: null
updated_at: null  # ISO-8601 with timezone

workflow_status: ACTIVE  # ACTIVE|PAUSED|BLOCKED|COMPLETED
task_scope: physics_onboarding  # physics_onboarding|existing_dataset|skill_debug
workspace_kind: canonical  # canonical|isolated_candidate
execution_mode: stepwise  # stepwise|low_auto|high_auto
presentation_format: migration_blocks_v1  # recovery hint; every mainline reply follows _shared.md even if this field is absent
auto_run_id: null  # candidate link only; does not change canonical Gates
auto_plan_ref: null
candidate_review:
  status: IDLE  # IDLE|PENDING|IN_REVIEW|RESOLVED; only used in isolated_candidate
  phase_id: null
  resume_step_id: null
candidate_module_reports: {}  # isolated_candidate only: module_id -> status, report_ref, sha256, log_event_ref

experiment_name: null
experiment_slug: null
dataset_id: null  # pre-dataset temporary index may be null

scientific_claim_ref:
  path: null  # normally P03_PHYSICS_CONTRACT.yaml after onboarding
  field: identity_and_goal.requested_scientific_claim
  decision_ref: null  # Dxxxx

checkpoint:
  phase_id: null  # onboarding|phase0|P01..P10|final
  phase_name: null
  skill: cevns-experiment
  step_id: master.step0.scope
  next_action: null
  resume_requires: []
  # Examples:
  # - decision:D0012:APPROVED
  # - gate:P03.machine:PASS
  # - authorization:W0002:ACTIVE

pending_decisions: []  # Dxxxx only
active_blockers: []

gates: {}
# Example after the Source phase exists:
# gates:
#   P03:
#     capability: source
#     machine: NOT_RUN  # NOT_RUN|PASS|BLOCKED
#     human: NOT_REVIEWED  # NOT_REVIEWED|APPROVED|REVISE|BLOCKED
#     evidence_fingerprint: null
#     report_ref: null
#     decision_refs: []
#     depends_on: []

authorization_refs:
  scope: null  # Dxxxx
  write: null  # Wxxxx; index only, not authority

artifact_refs:
  source_register: null  # P00_SOURCE_REGISTER.yaml
  evidence_ledger: null  # P01_EVIDENCE_LEDGER.yaml
  missing_and_conflicts: null  # P02_MISSING_AND_CONFLICTS.md
  physics_contract: null  # P03_PHYSICS_CONTRACT.yaml
  decision_log: null  # P04_DECISION_LOG.yaml
  contract_status: null  # P05_CONTRACT_STATUS.md
  authorization_log: null  # AUTHORIZATION_LOG.yaml
  input_inventory: null  # 00_INPUT_INVENTORY.md
  implementation_manifest: null  # 00_IMPLEMENTATION_MANIFEST.yaml
  phase_reports: {}

source_fingerprints: []
# - path: inputs/source/example.csv
#   sha256: null
#   affects: [P03, P07, P08, P09, P10]

stale_artifacts: []

handoff:
  state: NONE  # NONE|TEMPORARY|FORMAL
  temporary_index_ref: null
  formal_index_ref: null
  completed_at: null
```

## Phase summary

| Phase/Gate | Capability | Machine | Human | Report | Next action |
|---|---|---|---|---|---|
| P01 | Dataset | NOT_RUN | NOT_REVIEWED | — | — |
| P02 | Target / Exposure | NOT_RUN | NOT_REVIEWED | — | — |
| P03 | Source | NOT_RUN | NOT_REVIEWED | — | — |
| P04 | Theory / Nuclear Response | NOT_RUN | NOT_REVIEWED | — | — |
| P05 | Kinematics / Cross Section | NOT_RUN | NOT_REVIEWED | — | — |
| P06 | Detector Response | NOT_RUN | NOT_REVIEWED | — | — |
| P07 | Slow counts | NOT_RUN | NOT_REVIEWED | — | — |
| P08 | Fast counts | NOT_RUN | NOT_REVIEWED | — | — |
| P09 | Statistics | NOT_RUN | NOT_REVIEWED | — | — |
| P10 | Validation / Release | NOT_RUN | NOT_REVIEWED | — | — |

Use `NOT_REQUESTED` only in the Phase 0 capability plan, not in Machine/Human Gate fields.

## Reconstruction rule

If this file is missing, stale, corrupt, or references an unavailable authority, rebuild it from:

1. P00-P05 onboarding artifacts;
2. valid `Dxxxx` entries in the Decision Log;
3. valid `Wxxxx` entries in the Authorization Log;
4. `00_IMPLEMENTATION_MANIFEST.yaml` dependency declarations;
5. current Phase reports and fingerprints.

Never infer approval from this file alone.
For an isolated candidate, keep canonical Human Gates unchanged and record
candidate checks separately. The canonical progress index does not advance
until a reviewed promotion succeeds.

## User navigation

以下导航放在四块回复的“你还可以”内，不单独形成第五块。返回主线后先按
`_shared.md` 第 1 节重建完整四块；本文件只提供断点事实，不决定回复版式。

```text
主线进度：<实验名称> → <中文阶段/任务> → <正在等待的决定或下一步>
可回复：返回主线｜继续当前问题｜查看完整进度｜修改范围｜暂停
```

等待明确的 Physics Decision 或 `APPROVE WRITE` 时，只说明当前停止位置和
该项决定的回复方式，不同时显示通用导航菜单。
隔离候选进度须标明 `low_auto` 或 `high_auto`，并说明原项目正式进度未改变；
“返回主线”恢复当前候选，“查看正式进度”只读取原项目。
