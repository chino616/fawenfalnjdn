---
name: cevns-dataset
description: Materialize an approved Phase 0 dataset plan as a minimal runtime experiment specification and validate it with the existing schema and loader.
---

# cevns-dataset

## Purpose

Execute Phase 1 of the experiment-integration workflow.

Convert the approved Phase 0 outputs into the minimum runtime dataset
specification.

This Skill does not re-parse the experiment physics document and does not
implement experiment physics.

## Preconditions

Require:

```text
Gate I = PASS
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/templates/01_DATASET.md
workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md
workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml
```

Inspect the current dataset schema and loader:

```text
schemas/experiment.schema.json
src/cevns_pyeft/experiments/base.py
src/cevns_pyeft/experiments/specs.py
src/cevns_pyeft/experiments/registry.py
data/experiments/*/experiment.yaml
tests/test_experiment_specs.py
```

The Phase 0 inventory and manifest are the authoritative inputs for this phase.

Return to the user physics document only when the Phase 0 outputs contain an
explicit ambiguity or inconsistency.

Do not independently reinterpret the experiment document.

## Procedure

### 1. Verify the approved Phase 0 plan

Confirm:

```text
dataset_id
experiment family
run and detector configuration
observable contract
binning
output axes and shape
statistical data mode
static target and exposure fields
planned callable placeholders
```

Do not introduce fields that were not approved in the Phase 0 manifest.

### 2. Map the approved fields to the current repository schema

Use the existing field names and loader conventions.

Do not replace the current schema with a new conceptual schema.

If a required concept cannot be represented, record a blocker or a conditional
schema extension. Do not modify the schema silently.

### 3. Create the minimum runtime specification

Create:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Include only the approved dataset-level fields:

```text
dataset identity
provenance
run and detector configuration
observable axes
regular or irregular binning
output axes, shape, and unit
statistical data mode
small static target fields
exposure and exposure semantics
callable placeholders
planned data-file references
```

For planned files that do not yet exist, mark them explicitly as pending when
supported by the current schema.

Do not create those data files in this phase.

### 4. Create the dataset README

Create:

```text
data/experiments/<dataset_id>/README.md
```

Record:

```text
dataset identity
Phase 0 source files
observable and binning
output contract
statistical data mode
implemented phase
pending modules
known blockers
```

Do not describe pending modules as implemented.

### 5. Create the Phase 1 report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/01_DATASET.md
```

Use:

```text
workflows/experiment-integration/templates/01_DATASET.md
```

Record the mapping from Phase 0 fields to the actual `experiment.yaml` fields.

### 6. Validate

Run the current schema and loader tests.

Verify:

```text
dataset ID is unique
experiment.yaml passes schema validation
experiment.yaml is loadable
repository paths are relative
binning is internally consistent
number of bins matches output shape
statistical data mode is valid
callable placeholders are accepted
no later-phase implementation was created
```

## Prohibited actions

Do not:

```text
re-read and re-extract the complete physics document
change Phase 0 physical definitions
create source tables
implement source
implement detector response
implement Slow
implement Fast
implement statistics
create observed-data tables
modify registry.py unless the approved manifest explicitly requires it
modify theory, nuclear, rates, or kernels
start the next Skill automatically
```

## Gate D0

Gate D0 passes when:

```text
the approved Phase 0 dataset plan is represented in experiment.yaml
the specification passes the existing schema
the specification is loadable
binning and output shape are consistent
no experiment physics has been implemented
```

Record:

```text
PASS
```

or:

```text
BLOCKED
```

with reasons.

## Final response

Report only:

```text
files created
files modified
Phase 0 fields materialized
schema tests
loader tests
Gate D0 status
single next Skill
```

Then stop.

Do not execute the next Skill automatically.