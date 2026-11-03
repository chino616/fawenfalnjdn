# archive-lifecycle

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.archive_lifecycle",
  "skills": [
    "cevns.engineering.experiment_archive",
    "cevns.engineering.resource_manifest_auditor"
  ],
  "handoffs": [
    "cevns.experiment_onboarding",
    "cevns.runtime_maintenance"
  ]
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

Explicit archive/status request, selected source path, exact historical identity and intended
outcome: inspect/recover files, change runtime isolation status, or restore runnable physics.
Archive recovery permission is restricted to the named source; it does not unquarantine all backups.

## Sequence

1. Verify selected source identity and preservation/recovery scope; keep historical evidence intact.
2. For archived/spec-only status use `cevns.engineering.experiment_archive` and check isolation
   from default IDs, load, selection, registry and statistics; unrelated experiments must still work.
3. For recovery, prepare a reversible destination and resource/provenance audit with
   `cevns.engineering.resource_manifest_auditor`. Recovery does not imply active registration.
4. If runnable scientific recovery is requested, hand exact identity/material/claim candidates
   to experiment-onboarding. Engineering compatibility restoration uses runtime-maintenance
   after scope is explicit. Do not promote archived approvals to a changed artifact revision.

## Records, gates, failure and exit

Source/destination inventory and hashes, status/change manifest, resource audit, tests and
rollback. Human identity/physics/write decisions apply to their actual scope. Ambiguous source,
identity or meaning blocks activation. Exit with preserved history and verified isolation, or
an explicit downstream handoff. No default archive material discovery occurs.

## Reversible execution entry

[Dataset management](../../../../cevns_pyeft/experiments/MANAGEMENT.md) provides explicit archive/activate and physical install/uninstall as distinct operations. Start with its read-only plan; execute only the authorized dataset/action. Backups are read only for the exact transaction's rollback/recover. The registry distinguishes installed from active; remaining experiments must pass fresh-process validation. Exporting or reinstalling files does not upgrade historical scientific acceptance.
