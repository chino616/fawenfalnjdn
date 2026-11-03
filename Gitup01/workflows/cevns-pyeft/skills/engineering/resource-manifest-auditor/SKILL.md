---
name: resource-manifest-auditor
description: Audit resource manifest paths, aliases, hashes, scopes, and external roots.
---

# Resource manifest auditor

Run `tools/validate_resource_manifest.py --root <resource-root> [--dataset <id>]`. The tool
reuses `ResourceCatalog`, definition resource references, and `foundation.resources` alias
resolution.

The report must distinguish canonical path, resolved legacy path, external resource root, and
alias reason. It also checks hash equality, unknown/unused entries, ambiguous unscoped
overrides, lazy statistics, cwd independence, and an explicit root containing `data/`.

A missing statistics file blocks evaluation and is reported as a resource blocker; it must not be
hidden by changing physical code or substituting synthetic observations.

Every run outputs a change manifest, resource audit report, contract test plan, and validation
result.


For isolated automatic execution, follow `workflows/_shared/policies/automation.md`; candidates never change the source project without separate promotion approval.
