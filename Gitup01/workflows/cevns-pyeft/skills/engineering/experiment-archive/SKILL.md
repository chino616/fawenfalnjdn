---
name: experiment-archive
description: Archive or separate an experiment from runtime discovery without deleting history.
---

# Experiment archive

Use manifest status `archived` when historical material remains available but must not load;
use `spec_only` when a YAML/spec identity exists without a runnable definition.

Verify that the status is absent from default runtime IDs, `load_experiment`, selection, legacy
registry, statistics discovery, and active resource validation. Check that unrelated active
experiments still list/load/predict/evaluate. Keep historical documents marked
`archived/reference-only`; do not silently delete them.

Every run outputs a change manifest, resource audit report, contract test plan, and validation
result. Reversible status changes belong in the manifest; do not rewrite physics implementations.


For isolated automatic execution, follow `workflows/_shared/policies/automation.md`; candidates never change the source project without separate promotion approval.
