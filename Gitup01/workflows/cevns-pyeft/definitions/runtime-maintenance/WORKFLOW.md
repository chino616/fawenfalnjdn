# runtime-maintenance

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.runtime_maintenance",
  "skills": [
    "cevns.engineering.physics_modularity",
    "cevns.engineering.experiment_migration",
    "cevns.engineering.resource_manifest_auditor",
    "cevns.engineering.experiment_release_validator"
  ],
  "handoffs": [
    "cevns.release_validation"
  ]
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

An authorized engineering defect, compatibility/catalog/loader/scaffold change, or documentation-only
edit. Require the affected behavior, exact dataset/resource scope where relevant, current runtime
contracts and an existing baseline. No new physics meaning is approved by this workflow.

## Sequence and Skill use

1. Record scope and baseline; distinguish a software defect from changed physics meaning.
2. For component boundary work, use `cevns.engineering.physics_modularity` to identify actual
   callers and contracts. For new definition scaffolding use `cevns.engineering.experiment_migration`
   and a custom catalog before any proposed active-manifest change.
3. Form a minimal file/change/test/rollback plan, preserve existing authorization, and implement
   only that scope. Apply [file lifecycle](../../../_shared/policies/file-lifecycle.md): map file
   operations to owning READMEs, parent navigation and actual consumers, and synchronize them
   in this change. No standing milestone numbering is imposed on ordinary maintenance.
4. If resource references change, use `cevns.engineering.resource_manifest_auditor`.
5. Check the affected runtime contracts and existing experiment behavior; use
   `cevns.engineering.experiment_release_validator` only when release/install scope is requested.
6. Report changes, resource audit (or explicit not applicable), contract test plan and actual results.

Documentation-only branch: read the target and callers, edit the authorized text, check links and
claims (use `tools/validate_docs.py --files` for the affected Markdown), report the diff.
No physics gate or runtime test is implied by a spelling/layout change.
Changed scientific claims require reclassification before they are adopted.

## Gates, artifacts and exit

Machine gate is the relevant contract/regression or documentation check. Human approval is
needed for newly introduced scientific meaning/activation, not repeated for already authorized
routine engineering work. Stop and reclassify if semantics cannot be preserved; do not enter
P01–P10 just because an experiment ID occurs. Artifacts use the shared run-report where needed.
Exit with reviewed scope and verified behavior, or requested release-validation handoff; never
claim a new scientific result from an engineering PASS.
