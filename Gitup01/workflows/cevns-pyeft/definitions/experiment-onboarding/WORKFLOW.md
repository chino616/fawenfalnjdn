# experiment-onboarding

材料与文件检查以[共同输入规范](../../../_shared/INPUT_STANDARD.md)为依据，按本次目标选择适用字段、格式和真实消费者；填写件与审核结果按 dataset 保存。

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.experiment_onboarding",
  "skills": [
    "cevns.onboarding.experiment",
    "cevns.phase.p01.dataset",
    "cevns.phase.p02.target_exposure",
    "cevns.phase.p03.source",
    "cevns.phase.p04.theory_response",
    "cevns.phase.p05.kinematics_cross_section",
    "cevns.phase.p06.detector_response",
    "cevns.phase.p07.slow_counts",
    "cevns.phase.p08.fast_counts",
    "cevns.phase.p09.statistics",
    "cevns.phase.p10.validation"
  ],
  "handoffs": [
    "cevns.release_validation"
  ]
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and required inputs

Explicit new/redefined dataset intent, or an exact existing dataset and resume request. Inputs:
user-selected papers/data/code, intended scientific claim, existing decisions/contract where
available. Material availability and experiment names do not approve identity. Guided intake
does not require a complete contract. Keep evidence, semantic approval and write permission separate.

## Ordered steps and handoffs

1. Material registration starts the Evidence Ledger immediately, with independent source IDs,
   version/locator, units and status. Use `cevns.onboarding.experiment`.
2. Build dataset candidates, distinguish supporting files from different datasets, and obtain
   Dataset Identity approval for experiment_name / experiment_slug / dataset_id.
3. Clarify the requested scientific claim separately; official likelihood input gaps remain blocked.
4. **AI Physics Interpretation:** explain how the selected evidence maps to source, target,
   theory, detector, counts and statistics; label extraction, derivation and assumptions separately.
5. **Human Physics Clarification:** show competing interpretations, conflicts and approximations.
   Record the user's decision; AI interpretation alone cannot approve a physics field.
6. Update/finalize the Evidence Ledger and missing/conflict matrix; preserve all conflicting claims.
   Form the partial Physics Contract. Later numerical details may remain missing with an owner,
   needed_by_phase, candidate sources and blocking scope.
7. Hand off approved identity/claim, candidate evidence refs, fingerprints and blockers to **Phase 0** below.
   This handoff may be in conversation or an already authorized temporary directory; formal P00–P05
   and run directories are persisted only after Phase 0 scope and exact write authorization,
   with authority records written before the progress index. No formal-file prerequisite cycle exists.
8. Use catalog phase order for the default review sequence and the
   [phase execution contract](../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)
   for actual dependencies. P06 analysis can start when its own inputs are ready. P08/P09 are optional according
   to the accepted claim. Each phase: review required evidence -> pre-code physics decision ->
   authorized implementation -> machine checks -> human review -> authoritative records -> checkpoint.
   Missing inputs return to targeted intake and then the same phase; do not restart unrelated phases.
9. P07 establishes a direct-integral Slow reference and requires its explicit human freeze before
   P08. Each Fast representation has its own gate. P09 can use validated, accepted Slow directly;
    only a chosen Fast prediction adds its P08 dependency. P09 distinguishes data representation,
    processing, measurement design and likelihood; missing inputs block only models that require them.
10. P10 records validated capabilities, limitations and final scientific claim; a requested packaging
    check may hand off to release-validation. FULLY_INTEGRATED requires final human acceptance and
    actual canonical validation, never just a progress-index value.

## Phase 0 — mandatory pre-code planning gate

Use [phase0-plan](../../../_shared/templates/phase0-plan.md). Phase 0 consumes the partial
contract; it neither recollects evidence nor implements physics. It records:

- component classifications: REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED;
- reuse map and adapter map, existing functions to reuse and expected functions/interfaces;
- requested/optional capability plan and affected-input dependency map, including the actual executor,
  observation dimensions, detector aggregation, response/selection ownership and Slow/Fast choice;
- validation plan, exact allowed files/actions and forbidden modifications;
- current blockers, human scope approval, separate write authorization, and rollback plan.

CORE_EXTENSION additionally requires explicit physics approval and affected-existing-experiment
regression planning. Only then may the approved files be changed; a scope approval alone is not
a write authorization. Phase templates are [indexed here](../../../_shared/templates/phase/P01_P10_PHASE_TEMPLATES.md).

## Artifacts, gates, failure and exit

Source register, evidence ledger, missing/conflict matrix, partial contract, decision log,
Phase 0 implementation manifest, per-phase reports, authorization log and reconstructible
progress index. Formal locations and freeze conditions follow shared policies. An existing
dataset resumes only after checking current revision, fingerprints and effective approvals.
Machine states: PASS/BLOCKED/NOT_RUN; human states: APPROVED/REVISE/BLOCKED/NOT_REVIEWED.
Missing optional capability inputs block only that capability. Scientific changes invalidate
affected gates/dependent caches, not unrelated approvals. Isolated candidates do not advance
canonical human gates. Exit with the precise verified claim or an explicit blocked/partial result.
