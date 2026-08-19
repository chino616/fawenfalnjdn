---
name: cevns-validation-registry
description: Register and regression-test a completed CEvNS experiment.
---

# cevns-validation-registry

## Required references

Read:

```text
EXPERIMENT_WORKFLOW.md
CSI_REFERENCE_MAP.md
templates/10_VALIDATION_REGISTRY.md
```

## Procedure

Require all applicable prior Gates. Fill `templates/10_VALIDATION_REGISTRY.md`.

Use experiment-spec discovery when possible; modify `registry.py` only for a genuinely new callable type. Run new tests and all existing CsI2017, CsI2021, Ar2020, theory, Response, and Fast regressions. Do not update references merely to pass tests.

Create the completion report and stop after Gate V.

## Hard rules

- Use the user's physics document as the experiment definition.
- Use CsI only as a local API and validation reference.
- Do not copy a whole CsI module.
- Do not request data already present in the user's document.
- Back up every existing file before modification.
- Report created, modified, and prohibited files.
- Do not proceed past a failed Gate.
