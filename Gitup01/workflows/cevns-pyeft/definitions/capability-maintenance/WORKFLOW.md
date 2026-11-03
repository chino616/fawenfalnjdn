# capability-maintenance

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.capability_maintenance",
  "skills": [
    "cevns.engineering.physics_modularity",
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

## Entry and inputs

An existing identified dataset, the requested Fast/statistical semantic change, current contract,
evidence/decisions and valid forward prediction/Slow reference. Software-only cache defects
belong to runtime maintenance; they do not automatically trigger this workflow.

## Sequence

1. Map the changed mathematics/data meaning and affected dependencies using
   `cevns.engineering.physics_modularity`; preserve unrelated dataset approvals.
2. Fast: require current P07 PASS and human Slow freeze; if invalidated, use
   `cevns.phase.p07.slow_counts` to regenerate/approve the direct reference. Invoke
   `cevns.phase.p08.fast_counts` for representation, parameter domain, cache semantics and per-bin tests.
3. Statistics: use `cevns.phase.p09.statistics` to distinguish representation, processing, design
   and likelihood; review required errors/covariance, priors, inference and benchmarks.
   Validated, accepted Slow is sufficient unless the prediction actually uses Fast.
   Background-subtracted data must not become raw Poisson. Physical nuisance dependencies
   still invalidate affected forward artifacts; observed/error-only changes do not invalidate the physical kernel.
4. Obtain the affected physics decisions and scoped write authorization, implement, verify and
   record changed evidence/contract, invalidate only actual dependent artifacts.
5. Use `cevns.phase.p10.validation` for the updated capability/scientific claim; hand requested
   packaging validation to release-validation.

## Gates, records, failure and exit

Capability delta, evidence/decision refs, allowed files, cache invalidation map and phase reports.
Each Fast representation is independently validated; machine PASS does not accept a new
mathematical/statistical meaning. Missing Slow/basis/data/covariance blocks the affected
capability only when required by its declared model; do not silently narrow an official-likelihood claim.
Use the [phase execution contract](../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)
and per-capability phase reports. Preserve existing valid decisions; do not recreate unrelated onboarding gates. Exit with exact verified scope.
