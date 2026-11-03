# CEvNS-pyEFT Project Notes

This repository contains the split-minimal CEvNS-pyEFT package.

The material under

```text
workflows/cevns-pyeft/
```

defines a repository-local Codex workflow for adding, migrating, or
restructuring CEvNS experiment datasets.

It is not part of the runtime package and must not affect normal imports,
packaging, existing tests, or routine maintenance unless the task explicitly
concerns experiment integration.

## Workflow routing

For workflow-assisted work, the task-intent mapping is owned by
`workflows/cevns-pyeft/router/routes.yaml`. New/redefined dataset onboarding uses
the physics phase workflow; ordinary maintenance, theory/resource/capability changes,
archive lifecycle, repository/README maintenance and Skill QA follow the selected definition and its relevant gates.
An experiment name alone does not select onboarding.

Read the following files before any phase workflow or Skill:

```text
workflows/AGENTS.md
workflows/cevns-pyeft/AGENTS.md
workflows/_shared/README.md
workflows/_shared/INPUT_STANDARD.md
```

Then start only through the Master Skill:

```text
workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md
```

The Master Skill owns task scope, dataset/material ambiguity handling, input
mode, phase transitions, and the gate state. Do not bypass it by directly
entering an individual phase Skill or by treating local papers, placeholder
directories, or old code as user-approved physics scope.

For tasks that inspect or prepare experiment inputs, the shared input standard
is the common review basis. Identify applicable formats, units, coordinates,
normalization and provenance, then record which checks the actual reader ran
and which require scientific review. Shared templates contain no dataset values.

During physics onboarding, do not create or modify production experiment code before the Master Skill has
cleared the relevant physics gates and the current phase explicitly allows the
change.

Do not automatically continue to the next phase. Stop after the current phase
and wait for review unless the user explicitly requests multiple phases.
An explicitly activated low/high automatic run may explore multiple phases in
an isolated workspace under `workflows/_shared/policies/automation.md`; those are provisional
results. It does not advance canonical human gates or modify this repository.
Canonical promotion still requires the user's review and exact approval.

## Normal repository work

For tasks unrelated to adding or migrating an experiment dataset, do not load
or apply the experiment-onboarding physics workflow. The common workflow index may
route ordinary maintenance without invoking those physics gates.

Examples include:

- maintaining the existing theory, nuclear-response, rates, or kernel code;
- fixing ordinary package bugs;
- updating documentation unrelated to experiment integration;
- refactoring existing runtime modules without changing experiment datasets;
- running or repairing the existing test suite.

In those cases, treat

```text
workflows/cevns-pyeft/
```

as documentation-only material and leave it isolated from the runtime package.

## File changes and README synchronization

The user-facing [Skill library](cevns_pyeft/SKILLS.md) lists every catalog entry
and owns the add/edit/move/deprecate/remove checklist. Skill changes must update
the catalog, actual consumers, owning READMEs and its generated table in the
same task. Use `python -B tools/update_skill_library.py --write` explicitly;
the default/`--check` is read-only and is included in Skill-pack validation.
Do not count WORKFLOW definitions, shared templates or backup files as Skills.

All repository work follows
[file lifecycle](workflows/_shared/policies/file-lifecycle.md): create, delete,
move, rename or repurpose files together with their owning README, parent
navigation and actual consumers/registrations. Maintain these descriptions in
the same authorized task without waiting for a separate documentation request.
Remove or replace a deleted file's entry; retain a README while its directory
still has active contents. Record the file-to-README mapping and check affected
links before reporting completion. This is an executor responsibility; the
repository does not run an automatic README-editing filesystem watcher.

For bulk cleanup or a Git-based README review, use the explicit repository
maintenance route in routes.yaml and its workflow definition. Plan from a
verified Git revision or a saved file snapshot, group tasks by directory, and
sync only explicitly selected managed inventory blocks. Preserve manual prose
and report remaining references; do not initialize Git or stage/commit/push as
an implicit consequence of documentation maintenance.

This rule also applies to ordinary maintenance without activating experiment
onboarding. Existing physics/write authorization and historical evidence
boundaries remain in effect.

## Runtime isolation

Files under

```text
workflows/
```

must not be imported by:

```text
cevns_pyeft/
```

They must not be added as runtime package dependencies.

The workflow may create or modify files under the normal source, data, schema,
and test directories only within the authorized scope of the selected workflow.
Physics onboarding additionally requires the relevant phase gates.

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
