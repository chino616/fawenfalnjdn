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

For such tasks, the experiment-integration router is the mandatory entry point.
Read the following files before any phase workflow or Skill:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/_shared.md
```

Then start only through the Master Skill:

```text
workflows/experiment-integration/skills/cevns-experiment/SKILL.md
```

The Master Skill owns task scope, dataset/material ambiguity handling, input
mode, phase transitions, and the gate state. Do not bypass it by directly
entering an individual phase Skill or by treating local papers, placeholder
directories, or old code as user-approved physics scope.

Do not create or modify production experiment code before the Master Skill has
cleared the relevant physics gates and the current phase explicitly allows the
change.

Do not automatically continue to the next phase. Stop after the current phase
and wait for review unless the user explicitly requests multiple phases.
An explicitly activated low/high automatic run may explore multiple phases in
an isolated workspace under `AUTO_RUN_PROTOCOL.md`; those are provisional
results. It does not advance canonical human gates or modify this repository.
Canonical promotion still requires the user's review and exact approval.

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
cevns_pyeft/
```

They must not be added as runtime package dependencies.

The workflow may create or modify files under the normal source, data, schema,
and test directories only when an experiment-integration phase explicitly
requires those changes.

## Backup quarantine

`backup/**` is recovery-only storage and is outside the experiment-integration
physics workspace. The workflow must not automatically scan or read it for
material discovery, dataset candidates, evidence extraction, repository maps,
migration inputs, validation references, or `existing_dataset` detection.

Files under `backup/**` may be accessed only while creating a required backup,
or when the user explicitly requests backup recovery or audit. Explicit access
does not make archived content an approved physics input; bringing any recovered
material back into experiment integration requires the normal Master Skill gates.

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
