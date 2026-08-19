---
name: cevns-statistics
description: Implement statistics from the dataset's declared data model.
---

# cevns-statistics

## Required references

Read:

```text
EXPERIMENT_WORKFLOW.md
CSI_REFERENCE_MAP.md
templates/09_STATISTICS.md
```

## Procedure

Read only the statistical-data fragment and machine data. Determine the data mode before choosing a statistic.

Fill `templates/09_STATISTICS.md`. Prefer a configurable generic statistic. Create a dataset-specific module only when the likelihood structure cannot be expressed generically. Do not import CsI statistics unless the data model is identical.

Test data shapes, covariance, nuisance profiling, analytic/numeric agreement, and published or user-supplied benchmark values. Stop after Gate Q.

## Hard rules

- Use the user's physics document as the experiment definition.
- Use CsI only as a local API and validation reference.
- Do not copy a whole CsI module.
- Do not request data already present in the user's document.
- Back up every existing file before modification.
- Report created, modified, and prohibited files.
- Do not proceed past a failed Gate.
