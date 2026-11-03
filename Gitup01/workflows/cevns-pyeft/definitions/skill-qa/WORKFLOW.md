# skill-qa

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.skill_qa",
  "skills": [],
  "handoffs": []
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

Explicit workflow/Skill inspection, testing or structural maintenance; current catalog, routes,
definitions, policies, templates and realistic requests. This is workflow QA, not mock physics approval.

## Sequence

1. Inventory authority and protected areas; classify the authorized change as structure,
   routing or procedure. Preserve existing authorization for engineering edits.
2. Run the existing structural validator and reference auditor; make only authorized workflow changes.
3. Check catalog uniqueness/discovery, route/Skill references, phase mappings, policy links,
   invocation cycles, historical exceptions and backup isolation.
4. Evaluate realistic natural-language requests separately from fixture structure. Store raw
   inputs, expected routes, actual agent outputs, reviewer verdicts and unresolved failures in
   separate records. Static fixture checks do not establish natural-language behavior.
5. Check onboarding/interpretation/clarification, Phase 0 and handoff scenarios, and report
   unexecuted or human-review-pending cases explicitly.

## Artifacts, gates and exit

Use [QA guidance](../../qa/README.md). Machine gate covers structural/reference checks and
tests. A reviewer evaluates observed routing/handoffs; do not label automated review as human
acceptance. No real dataset, production physics code or scientific approval is created by a
scenario. Exit with exact tested coverage, changes and remaining issues. No speculative QA Skill
is necessary: this definition orchestrates the existing validators and scenario evaluations.
