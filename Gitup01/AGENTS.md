# CEvNS-pyEFT Project Notes

This repository contains the split-minimal CEvNS-pyEFT package.

The material under

```text
workflows/experiment-integration/
```

defines a repository-local Codex workflow for adding, migrating, or
restructuring CEvNS experiment datasets.

It is not part of the runtime package and must not affect normal imports,
packaging, existing tests, or routine maintenance unless the task explicitly
concerns experiment integration.

## Workflow routing

Use the experiment-integration workflow only when the task explicitly involves
one or more of the following:

- adding a new CEvNS experiment or dataset;
- migrating an existing experiment implementation;
- adding or changing an experiment source model;
- adding a detector, target, calibration, or detector-response model;
- implementing experiment-specific Slow counts;
- implementing experiment-specific Fast counts or kernels;
- adding experiment-specific statistical data or likelihoods;
- registering a new experiment dataset.

For such tasks, read the following files before making changes:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
```

Then follow the phase order defined in:

```text
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
```

Always start with Phase 0 and read:

```text
workflows/experiment-integration/skills/cevns-experiment-intake/SKILL.md
```

Do not create or modify production experiment code before the Phase 0 input
inventory and implementation manifest have been completed.

Do not automatically continue to the next phase. Stop after the current phase
and wait for review unless the user explicitly requests multiple phases.

## Normal repository work

For tasks unrelated to adding or migrating an experiment dataset, do not load
or apply the experiment-integration workflow.

Examples include:

- maintaining the existing theory, nuclear-response, rates, or kernel code;
- fixing ordinary package bugs;
- updating documentation unrelated to experiment integration;
- refactoring existing runtime modules without changing experiment datasets;
- running or repairing the existing test suite.

In those cases, treat

```text
workflows/experiment-integration/
```

as documentation-only material and leave it isolated from the runtime package.

## Runtime isolation

Files under

```text
workflows/experiment-integration/
```

must not be imported by:

```text
src/cevns_pyeft/
```

They must not be added as runtime package dependencies.

The workflow may create or modify files under the normal source, data, schema,
and test directories only when an experiment-integration phase explicitly
requires those changes.

## Existing experiment protection

Unless the task explicitly requires a shared-core change, preserve the behavior
of all existing datasets, including:

```text
CsI2017
CsI2021
Ar2020
```

Any change to shared theory, nuclear response, rates, detector folding, or Fast
kernel infrastructure must run the existing regression tests for those
datasets.

Do not update existing reference arrays or relax tolerances merely to make a
new implementation pass.

## Backup rule

Before modifying an existing file during experiment integration, create a
backup under:

```text
backup/<relative-original-path>
```

Record every backup in:

```text
backup/BACKUP_MANIFEST.md
```

Do not overwrite an existing backup without recording the new revision.