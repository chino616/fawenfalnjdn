---
name: experiment-release-validator
description: Validate runtime/catalog consistency in isolated and release environments.
---

# Experiment release validator

Check that active manifest IDs, `BUILTIN_CATALOG.ids()`, and the default runtime list agree;
that spec-only and archived IDs remain separated; and that public imports still work.

Run syntax/import smoke checks, the relevant pytest matrix, an explicit external resource root,
changed cwd, `python -I` where dependencies permit it, and wheel verification when the project
provides a wheel tool. Record unavailable dependencies separately from code failures.

Do not add external resources, generated outputs, wheels, caches, or local backups to the source
package. A ZIP migration bundle must contain the changed source/docs/tests/tools and its change
manifest, not transient automatic-run state.

Every run outputs a change manifest, resource audit report, contract test plan, and validation
result.


For isolated automatic execution, follow `workflows/_shared/policies/automation.md`; candidates never change the source project without separate promotion approval.
