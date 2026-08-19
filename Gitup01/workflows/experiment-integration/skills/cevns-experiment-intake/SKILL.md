---
name: cevns-experiment-intake
description: Parse a CEvNS experiment document, inspect the current repository, and produce the Phase 0 input inventory and implementation manifest without modifying production code.
---

# cevns-experiment-intake

## Purpose

Execute Phase 0 of the CEvNS experiment-integration workflow.

Convert a user-supplied experiment physics document into:

1. an input inventory;
2. a module-by-module implementation plan;
3. explicit blockers;
4. one recommended next Skill.

Do not implement the experiment in this phase.

## Required references

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/RUN_OUTPUTS.md
workflows/experiment-integration/templates/
00_IMPLEMENTATION_MANIFEST.md
```

Also read:

```text
the complete user-specified experiment physics document
all explicitly referenced attachments
optional reference code supplied by the user
the current repository tree
relevant existing source, data, schema, and test files
```

The user physics document is the experiment definition.

Reference programs are secondary numerical references and must not replace the
physics document.

## Procedure

### 1. Identify independent datasets

Determine whether the input describes one or multiple datasets.

Split datasets when any of the following differ:

```text
run period
detector configuration
source configuration
target configuration
calibration
threshold or analysis window
binning
observed data
background model
covariance
likelihood
```

Assign one unique `dataset_id` to each independent dataset.

Do not merge independent runs merely because they appear in the same document.

### 2. Inventory the supplied inputs

For every dataset, extract all supplied:

```text
scalar parameters
formulas
numerical tables
source definitions
target definitions
detector parameters
bin edges
response models
observed data
background data
covariance matrices
nuisance parameters
test statistics
reference outputs
```

Record units, source sections, table shapes, interpolation rules, boundary
rules, normalization conventions, and intended machine-readable files.

Do not request data already present in the document or an attachment.

Do not infer missing arrays from printed summaries or plots.

### 3. Determine the statistical data mode

Assign exactly one primary data mode:

```text
raw_counts
signal_plus_background
on_off
background_subtracted_excess
unbinned_events
```

Do not treat background-subtracted data as raw Poisson counts.

Do not invent an independent background array when none is supplied.

### 4. Inspect the current repository

Inspect actual files and APIs rather than guessing from filenames.

Check the relevant parts of:

```text
src/cevns_pyeft/experiments/
src/cevns_pyeft/theory/
src/cevns_pyeft/nuclear/
src/cevns_pyeft/rates/
src/cevns_pyeft/kernels/
data/experiments/
schemas/
tests/
```

Use `CSI_REFERENCE_MAP.md` to determine which local CsI fragment may be
inspected for each module.

Use CsI only for:

```text
public API
control flow
units
returned shapes
component axes
validation structure
```

Do not copy a complete CsI module or any CsI-specific physical inputs.

### 5. Classify every module

Classify:

```text
dataset
source
target
theory_response
kinematics_cross_section
detector_response
slow_counts
fast_counts
statistics
validation_registry
```

Use exactly one primary status for each module:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

Apply the definitions in:

```text
templates/00_IMPLEMENTATION_MANIFEST.md
```

Do not create a Python file solely because the physics document contains a
subsection.

When a module contains multiple independent implementations, such as different
Fast representations, record them separately inside that module.

One blocked Fast representation must not automatically block another
implementable Fast representation.

### 6. Produce the concrete file plan

For every module identify:

```text
user-document sections
supplied inputs
CsI local references
files to reuse
files to create
files to modify
conditionally modified files
files that must not be modified
planned public APIs
planned tests
blockers
```

All paths must come from actual repository inspection.

For every planned callable, record:

```text
name
location
inputs
input units
returned type
returned unit
returned shape
returned axes
error behavior
```

For every planned test, record:

```text
test path
physical or API contract
input
expected result
tolerance
reference provenance
```

### 7. Create the Phase 0 outputs

For every independent dataset create:

```text
workflows/experiment-integration/runs/<dataset_id>/
├── 00_INPUT_INVENTORY.md
└── 00_IMPLEMENTATION_MANIFEST.yaml
```

Use the structure and consistency rules defined in:

```text
workflows/experiment-integration/templates/
00_IMPLEMENTATION_MANIFEST.md
```

Do not duplicate or invent a different schema inside this Skill.

### 8. Evaluate Gate I

Evaluate Gate I using the criteria defined in:

```text
templates/00_IMPLEMENTATION_MANIFEST.md
```

A blocker affecting a later phase does not necessarily make Gate I fail,
provided that:

```text
the blocker is explicit
the affected module is identified
the resolution condition is recorded
the remaining implementation plan is complete
```

Set:

```text
PASS
```

or:

```text
BLOCKED
```

and record the reasons.

## Phase boundary

During this Skill do not:

```text
create production Python modules
create the final experiment.yaml
materialize production CSV, NPY, or NPZ files
modify registry.py
modify theory, nuclear, rates, or kernels
implement source
implement detector response
implement Slow
implement Fast
implement statistics
generate reference arrays
start the next phase automatically
```

The normal outputs of this Skill are only:

```text
00_INPUT_INVENTORY.md
00_IMPLEMENTATION_MANIFEST.yaml
```

Phase 0 should not modify existing production files.

## Final response

After writing the Phase 0 outputs, report only:

```text
dataset IDs
module classifications
files planned for creation
files planned for modification
conditionally modified files
files that must not be modified
blockers
Gate I status
single next Skill
```

Also state:

```text
Production code created: none
Production data created: none
Existing production files modified: none
```

Then stop.

Do not execute the next Skill automatically.