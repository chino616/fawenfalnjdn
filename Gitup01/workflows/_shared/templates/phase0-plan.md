# Phase 0 implementation plan

Identity / scientific claim / contract revision / evidence references:

| Component | REUSE/CONFIG_ONLY/ADAPTER/SHARED_EXTENSION/CORE_EXTENSION/BLOCKED | Existing function/interface | Expected function/interface | Evidence and dependencies |
|---|---|---|---|---|

## Reuse map and adapter map

Map required responsibilities to verified current owners and minimal adapters.

## Capability and validation plans

Requested/optional capabilities, necessary phase gates, affected-experiment regressions,
acceptance criteria, missing inputs with owner and needed_by_phase:

Use [P04–P10 dependencies](../references/phase/PHASE_EXECUTION_CONTRACT.md).
Record the actual executor/API, supported observation dimensions and detector aggregation;
choose response density versus accepted bin probabilities and assign selection ownership.
P09 may consume Slow directly; P08 is required only for a selected Fast prediction.
Separate plan_status from machine_gate/human_gate and specify each independent capability_id.
Set numerical/inference acceptance criteria before using results to decide success; defer details
that are not needed yet without filling missing physics with defaults.

## Allowed files/actions and forbidden modifications

List exact paths/actions, protected implementations/data/reference arrays and rollback steps.

## Independent approvals

Human scope/physics decision references (CORE_EXTENSION separately):
Write authorization reference and exact scope:
Unresolved blockers and exit/resume conditions:

This plan consumes the partial contract; it does not recollect evidence or implement physics.
