---
name: experiment-migration
description: Migrate a new CEvNS experiment through a custom catalog without changing existing physics.
---

# Experiment migration

Use this route for a new definition or a dataset moving from spec-only to runtime.

1. Validate the dataset ID and module boundary.
2. Generate a scaffold with `tools/scaffold_experiment.py`.
3. Register it in `ExperimentCatalog(builtins=False)`; do not edit the active manifest yet.
4. Resolve an explicit `ResourceCatalog` and run the Slow contract.
5. Verify observation name/unit/edges, identity/fingerprint, missing-statistics behavior,
   unsupported Fast behavior, selection, and component replacement.
6. Promote only after the user reviews the exact manifest entry and resources.

Every run outputs:

- change manifest;
- resource audit report;
- contract test plan;
- validation result.

Slow is the minimum capability. Fast, statistics, and legacy adapters are explicit optional
capabilities. Never modify a physical formula or reference array just to satisfy this route.


For isolated automatic execution, follow `workflows/_shared/policies/automation.md`; candidates never change the source project without separate promotion approval.
