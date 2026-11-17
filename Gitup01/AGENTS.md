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

## Mandatory onboarding provenance

All onboarding work follows the shared
[data provenance contract](workflows/_shared/references/onboarding/data-provenance-contract.md).
Every adopted scientific value, array, formula and processing choice must have a
traceable direct source or explicit derivation/decision in the generated output;
a parameter ID or bibliography alone is insufficient. Immediately after the first
readable draft, explain what is known, what data or original-source verification is
still missing, and its impact; interact with the user to supplement it, update the
same evidence records and regenerate affected outputs. Preserve unresolved gaps
and versions. Do not label an output final for its requested claim while required
provenance is unresolved, or promote secondary transcription to verified primary data.

This rule governs execution and output review; current schema/link checks do not
authenticate scientific sources. It grants no additional physics or write approval.

### Evidence beside each experimental input

Every Source, Target, Detector Response, Observable, Prediction and Statistics
section must contain its own input and availability table. Show actual scalar
values or array dimensions, axis ranges and representative values, units, a link
to the local numerical file, the exact primary-source locator, and the verified
scope and applicability. Resolve bibliography numbers to a readable standard
citation in the same section. The shared provenance contract defines the columns.

A formula symbol table must distinguish a definition from an available numerical
input. For every required function, coefficient, response kernel or distribution
whose numbers have not been obtained, show MISSING beside that symbol, identify
the required material and block the dependent calculation. Keep the bibliography,
array existence check and scientific applicability review as separate records.

Match required inputs to the requested observable and analysis. A one-dimensional
prediction uses the corresponding marginal response. Record additional inputs for
a native multidimensional likelihood under that separately requested capability.

Revisions must update the same source/evidence/configuration chain and its
generator. Preserve earlier report versions, label the new output as a draft
while required inputs remain unresolved, and end with a capability-specific
handoff table listing the concrete inputs required by the next phase.

### Numerical data behind shared modules

Naming a shared module such as ResponseDB, a nuclear response, a flux loader or
a detector model does not establish that its required numerical inputs exist or
have verified provenance. Before reporting a module as ready, open its actual
resource and record the isotope/run keys, channels, coefficient or grid arrays,
shape, axis order, units, normalization, representative values and full file link.
Trace the local file through its extraction/conversion to a pinned author release
or an exact paper/table/equation. A format name, matching function names or a
plausible upstream repository is insufficient to certify that correspondence.

Track numerical availability, direct-source verification, conversion equivalence
and applicability as separate checks in the same onboarding records and outputs.
If a local array exists but its original table or conversion cannot be verified,
show the actual array and mark its original provenance unresolved. If the array
itself is absent, show MISSING beside the required numerical input. Propagate
these gaps to predictions and benchmarks that depend on them. Apply the shared
provenance contract when regenerating the detailed report, summary and user input.

When the user selects an existing project data resource for direct reuse, record
that file and the existing reader convention as the direct adopted source. Keep
unverified external authorship or generation separately visible. Do not require
reconstructing that external pipeline as a new prerequisite for the authorized
local reuse. Restrict the remaining gap to claims that require external source
certification or paper equivalence. User selection does not turn unverified
external provenance into a verified fact.

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

## Paper figure theme

For new paper figures or a requested style update, first read
`plotting/paper_theme/README.md` and `plotting/paper_theme/PAPER_THEME_GUIDE.md`.
The single current theme authority is `plotting/paper_theme/PAPER_THEME.json`
(user-supplied v4.0). Reuse `theme_styles.py` and `plot_template.py`; keep physical
series identities stable across figures. Theme changes belong to `plotting/`,
while specific plot generators and output datasets retain their own directories.

Old STYLE files and modules in numbered figure collections are historical
reproduction snapshots, not defaults for new plots. Preserve published figures
and their numerical/provenance records when adopting the new theme. Use a new
output directory and record the adopted theme version/hash. This is a plotting
rule and does not activate experiment onboarding or authorize physics changes.

See `plotting/README.md` for the file architecture and
`plotting/paper_theme/MIGRATION.md` for current consumer and legacy boundaries.

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
