# theory-extension

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.theory_extension",
  "skills": [
    "cevns.engineering.physics_modularity",
    "cevns.phase.p04.theory_response",
    "cevns.phase.p05.kinematics_cross_section",
    "cevns.phase.p10.validation"
  ],
  "handoffs": [
    "cevns.release_validation"
  ]
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

An explicit read-only review or scientific change of common theory/operator/matching/response
conventions, with the requested conclusion, evidence, units/basis/validity domain and existing
implementations. Determine audit-only versus semantic-change intent before selecting actions.

## Sequence and handoffs

1. Use `cevns.engineering.physics_modularity` to map implementation owners, callers and caches.
   For audit-only intent, inspect the selected scope and run only relevant authorized read-only checks;
   no dataset, production changes or implementation approvals are implied.
2. Use `cevns.phase.p04.theory_response` and, only if the requested review/change includes kinematics or cross-section boundaries,
   `cevns.phase.p05.kinematics_cross_section` for the focused physics review. This does not
   create a dataset or require unrelated P01–P03 intake.
3. In audit-only mode, report verified internal conventions, existing regression evidence and
   external-source gaps. Return the requested audit result; use P10 only when a scoped final
   capability/claim review is requested. Missing external source tables do not imply failure of
   unrelated historical regressions. Do not continue to implementation or invent human approval.
4. For a semantic change, record CORE_EXTENSION/SHARED_EXTENSION scope, human physics approval, allowed files,
   write authorization, regression plan for affected experiments and rollback.
5. Implement the approved change in the existing runtime owners. Check basis/complex
   coefficients/response conventions/units, independent benchmarks and affected regressions.
6. `cevns.phase.p10.validation` reviews only the resulting supported capability/claim.
   Release packaging, if requested, hands off to release-validation.

## Records, gates, blocks and exit

Evidence/decision/contract delta, dependency invalidation map, change manifest and validation
report. Machine checks and human physics approval are independent. Missing conventions or
benchmarks remain unresolved; never rewrite references/tolerances to pass. Exit with exact
verified applicability or BLOCKED; scientific source uncertainty is not repaired by moving files.
