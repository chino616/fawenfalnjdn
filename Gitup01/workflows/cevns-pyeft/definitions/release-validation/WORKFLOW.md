# release-validation

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.release_validation",
  "skills": [
    "cevns.engineering.experiment_release_validator"
  ],
  "handoffs": []
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

An explicit benchmark/capability or release-validation request, exact code/resources/configuration,
reference provenance, environment and acceptance criteria. Re-running a benchmark does not
request a new dataset or change of scientific claim.

## Sequence

1. Identify requested checks and immutable input/reference fingerprints.
2. Use `cevns.engineering.experiment_release_validator` for applicable runtime/catalog, external
   root, cwd/import/wheel checks; run only the relevant benchmark/contract/regression scope.
3. Record commands, environment, results, unavailable dependencies and comparison tolerances.
4. Distinguish numerical consistency, legacy regression, publication reproduction and official
   likelihood reproduction. Report limitations; escalate a requested claim change to human review.

## Records, gates, failure and exit

Validation report, change manifest (empty if read-only), resource audit and contract test plan.
Machine gate reflects actual executed checks. Failures and unavailable dependencies remain
separate. Do not change formulas, references or tolerances to force success. Exit with verified
requested capability or explicit failed/not-run checks; publication/activation is not implied.
