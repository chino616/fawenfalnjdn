# resource-maintenance

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.resource_maintenance",
  "skills": [
    "cevns.engineering.resource_manifest_auditor"
  ],
  "handoffs": []
}
```

Task triggers are assigned only by [routes.yaml](../../router/routes.yaml). Resolve Skill IDs through [catalog.yaml](../../../catalog.yaml).

## Entry and inputs

Explicit resource root and scope, manifest entries, provenance, expected units and approved
data meaning. A new resource file is not by itself approval of a new scientific definition.

## Sequence

1. Inventory selected canonical/legacy paths, hashes and readers with backup/archive isolation.
2. Invoke `cevns.engineering.resource_manifest_auditor`; distinguish absent files, aliases,
   external-root errors, stale hashes, conflicting sources and lazy statistics dependencies.
3. Propose scoped fixes and rollback. Resolve any change of scientific meaning with the human
   and the appropriate theory/capability route before adopting it.
4. Apply authorized path/manifest maintenance and repeat affected resource/consumer checks.

## Records, gates, failure and exit

Change manifest, provenance/resource audit, contract test plan and validation result. Gate is
canonical resolution/hash/consumer correctness, not automatic scientific acceptance. Missing
statistics blocks evaluation, not valid forward prediction. Leave unresolved semantic conflicts
explicit; never synthesize observations or silently choose a nuclear response convention.
Exit to the calling workflow with verified resource references or concrete blockers.
