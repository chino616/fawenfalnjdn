---
name: cevns-experiment-intake
description: Parse a CEvNS experiment document, inspect the current repository, and plan a modular experiment integration without modifying production code.
---

# cevns-experiment-intake

## Purpose

Convert a user-supplied CEvNS experiment physics document into:

1. a complete input inventory;
2. a module-by-module comparison with the current repository;
3. a concrete implementation manifest;
4. an explicit list of blockers;
5. a single recommended next Skill.

This Skill performs Phase 0 only.

It does not implement the experiment.

## Required references

Read:

```text
AGENTS.md
EXPERIMENT_WORKFLOW.md
CSI_REFERENCE_MAP.md
RUN_OUTPUTS.md
templates/00_IMPLEMENTATION_MANIFEST.md
```

Also read:

```text
the complete user-specified experiment physics document
all attachments explicitly referenced by that document
optional reference code supplied by the user
the current repository tree
the relevant existing source, data, schema, and test files
```

If this Skill is invoked from:

```text
workflows/experiment-integration/skills/cevns-experiment-intake/
```

resolve the workflow references from:

```text
workflows/experiment-integration/
```

Do not infer repository APIs from filenames alone.

Open the actual files and inspect their imports, public functions, returned
shapes, units, configuration fields, and tests.

## Inputs

The user must identify at least one experiment physics document.

Typical inputs are:

```text
physics_docs/experiments/<dataset_id>/experiment_physics.tex
papers or supplementary material
CSV, JSON, NPY, NPZ, YAML, or text data
optional Mathematica, Python, or notebook reference implementations
the current Gitup01 repository
```

Reference programs are secondary sources.

They may be used to determine the intended numerical procedure or benchmark,
but they do not replace the physics document as the experiment definition.

## Phase boundary

This Skill is responsible only for:

```text
INPUT_RECEIVED
→ INPUT_PARSED
→ IMPLEMENTATION_MANIFEST_COMPLETED
```

It must stop before:

```text
DATASET_IMPLEMENTATION
SOURCE_IMPLEMENTATION
TARGET_IMPLEMENTATION
THEORY_MODIFICATION
DETECTOR_IMPLEMENTATION
SLOW_IMPLEMENTATION
FAST_IMPLEMENTATION
STATISTICS_IMPLEMENTATION
REGISTRY_MODIFICATION
```

## Procedure

### Step 1: locate the experiment material

Identify:

```text
physics document
referenced papers
supplementary data
machine-readable files
optional reference code
existing repository modules
```

Record the exact path of every input.

Do not silently substitute a different paper, dataset, run, or detector
configuration.

### Step 2: identify independent datasets

Determine whether the physics document describes one dataset or multiple
independent datasets.

Create separate dataset IDs when any of the following differ:

```text
run period
detector set
source configuration
target composition
active mass
exposure
calibration
threshold
analysis window
binning
observed data
background model
covariance
likelihood
```

Do not combine independent runs or detector configurations under one dataset
ID merely because they appear in the same paper.

For every dataset, record:

```text
dataset_id
experiment family
run or acquisition period
detector configuration
source configuration
target configuration
observable axes
statistical data mode
```

### Step 3: extract the supplied physics inputs

For each dataset, inventory all information already supplied by the user.

Record:

```text
scalar parameters
physical constants
formulas
numerical tables
bin edges
source spectra
source normalizations
target compositions
isotope abundances
detector masses
live times
exposures
quenching or yield models
resolution models
efficiency curves
migration matrices
observed data
background data
covariance matrices
nuisance parameters
test statistics
confidence thresholds
reference event counts
reference spectra
reference chi-square values
```

For every numerical table, record:

```text
source document or attachment
table name or section
row count
column names
units
interpolation rule
normalization
intended target file
```

A value already present in the physics document or an attachment is not a
blocker.

Do not ask the user to provide it again.

### Step 4: determine the statistical data mode

Assign exactly one primary statistical data mode to each dataset:

```text
raw_counts
signal_plus_background
on_off
background_subtracted_excess
unbinned_events
```

If the document contains multiple distinct statistical products, split them
into separate analysis datasets or record the secondary products explicitly.

Do not infer an independent background array when the input is already
background-subtracted excess.

Do not treat background-subtracted data as raw Poisson counts.

### Step 5: inspect the current repository

Inspect the actual repository structure.

Check, when present:

```text
src/cevns_pyeft/experiments/base.py
src/cevns_pyeft/experiments/registry.py
src/cevns_pyeft/experiments/coherent/
src/cevns_pyeft/nuclear/
src/cevns_pyeft/theory/
src/cevns_pyeft/rates/
src/cevns_pyeft/kernels/
data/experiments/
schemas/
tests/
```

Use `CSI_REFERENCE_MAP.md` to restrict which CsI files are inspected for each
module.

Do not read or copy an entire CsI implementation when only one local interface
is relevant.

### Step 6: inspect the CsI reference module by module

Use CsI2017 and CsI2021 only as local API and validation references.

For each module inspect only the relevant CsI fragment.

#### Dataset

Inspect:

```text
experiment specification
registry entry or discovery mechanism
observable-axis metadata
returned-shape metadata
schema validation
```

#### Source

Inspect:

```text
source callable signature
component names
flavor labels
energy and time conventions
normalization placement
source tests
```

Do not copy the SNS spectrum.

#### Target

Inspect:

```text
target inventory
nuclei-per-kilogram calculation
response-key routing
component axes
exposure placement
```

Do not copy Cs or I physical parameters.

#### Theory and response

Inspect:

```text
Wilson basis
coefficient order
flavor routing
nuclear-response interface
amplitude coverage
```

Do not create a second amplitude in the experiment package.

#### Kinematics and cross section

Inspect:

```text
energy units
kinematic support
out-of-support behavior
differential-cross-section callable
returned cross-section units
```

Do not copy CsI-specific integration limits.

#### Detector response

Inspect:

```text
true-to-reconstructed mapping API
response-density API
efficiency domain
bin integration
response tests
```

Do not copy CsI quenching, PE mapping, timing, or efficiency.

#### Slow counts

Inspect:

```text
public API
integration order
component axes
returned shape
diagnostics
reference-test structure
```

Do not copy a complete Slow module.

#### Fast counts

Inspect:

```text
experiment wrapper
common-kernel boundary
basis definition
storage format
reconstruction API
Slow/Fast tests
```

Do not copy CsI kernel arrays.

#### Statistics

Inspect only when the new dataset uses the same data mode and likelihood
structure.

Do not assume that all CEvNS experiments use the CsI statistic.

### Step 7: classify every module

Classify the following modules:

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

Each module must receive exactly one primary status:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

Use the following definitions.

#### REUSE

The current repository already satisfies the required interface and physics
contract.

No new production implementation is required.

#### CONFIG_ONLY

Only configuration or machine-readable data is required.

Typical outputs are:

```text
YAML
CSV
JSON
NPY
NPZ
```

No new Python implementation is required.

#### ADAPTER

The shared physics implementation can be reused, but an experiment-level
adapter is required for:

```text
units
routing
component labels
target mapping
source mapping
detector mapping
returned shape
```

#### SHARED_EXTENSION

A new reusable experiment-family module is required.

Examples include:

```text
shared reactor source model
shared liquid-xenon detector response
shared germanium ionization model
```

#### CORE_EXTENSION

The current common implementation cannot represent the required physics.

A modification may be required under:

```text
src/cevns_pyeft/theory/
src/cevns_pyeft/nuclear/
src/cevns_pyeft/rates/
src/cevns_pyeft/kernels/
```

This classification must identify the exact missing capability.

#### BLOCKED

Essential information is missing, inconsistent, or unavailable.

A blocker must state:

```text
what is missing
why it is required
where it was expected
which phase cannot proceed
whether another module can still proceed
```

A LaTeX subsection does not automatically imply a new Python file.

### Step 8: determine the concrete file plan

For every module record:

```text
user_document_section
csi_reference_files
reuse_files
create_files
modify_files
must_not_modify
public_api
tests
blockers
```

All repository paths must come from actual repository inspection.

Do not invent files, functions, classes, schemas, or directories.

For every planned Python file, define the expected public API.

Record:

```text
function or class name
principal inputs
input units
coefficient convention
returned type
returned shape
returned axes
component labels
error behavior
```

Example:

```yaml
public_api:
  - name: slow_counts
    inputs:
      - coefficients
      - experiment_spec
    keyword_arguments:
      - return_components
    returns:
      type: numpy.ndarray
      shape:
        - reconstructed_energy_bin
      unit: expected_events_per_bin
```

For every planned test, record:

```text
test file path
test name or purpose
input point
expected output
tolerance
reference provenance
```

### Step 9: identify files that must not be modified

At minimum, consider protecting:

```text
existing CsI2017 implementation
existing CsI2021 implementation
existing Ar2020 implementation
existing reference arrays
shared theory files
shared nuclear-response files
shared rate files
shared kernel files
```

A shared-core file may move from `must_not_modify` to `modify_files` only when
the module is classified as `CORE_EXTENSION`.

Such a change must require:

```text
backup
new unit tests
existing theory regression tests
CsI2017 regression tests
CsI2021 regression tests
Ar2020 regression tests
Fast-kernel regression tests
```

### Step 10: create the Phase 0 outputs

Create:

```text
runs/<dataset_id>/00_INPUT_INVENTORY.md
runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
```

Use:

```text
templates/00_IMPLEMENTATION_MANIFEST.md
```

If the workflow root is:

```text
workflows/experiment-integration/
```

the full output paths are:

```text
workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md

workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml
```

Create one pair of files for each independent dataset.

## Required content of 00_INPUT_INVENTORY.md

The input inventory must include:

```text
dataset identity
experiment goal
physics document path
reference-document paths
attachment paths
optional reference-code paths
source definition
detector inventory
target inventory
observable axes
binning
supplied scalar parameters
supplied formulas
supplied numerical tables
detector-response inputs
statistical data mode
observed data
background data
covariance
nuisance parameters
reference outputs
missing information
current achievable implementation level
```

For numerical tables, include shape and units.

For external reference programs, state whether the required arrays or tables
are actually embedded in the supplied file.

Do not infer missing arrays from printed summaries.

## Required schema of 00_IMPLEMENTATION_MANIFEST.yaml

Use this structure:

```yaml
dataset_id:
family:
physics_document:
reference_documents: []
attached_data: []
optional_reference_code: []

dataset_identity:
  run_period:
  detector_configuration:
  source_configuration:
  target_configuration:
  statistical_data_mode:
  observable_axes: []
  expected_output_shape: []

modules:
  dataset:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  source:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  target:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  theory_response:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  kinematics_cross_section:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  detector_response:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  slow_counts:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  fast_counts:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  statistics:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  validation_registry:
    status:
    user_document_section:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

global_blockers: []

gate:
  phase: I
  status:
  reasons: []

next_skill:
```

## Manifest consistency rules

The manifest must satisfy all of the following:

1. Every module has exactly one primary status.
2. Every `REUSE` module identifies actual reusable files.
3. Every `CONFIG_ONLY` module identifies concrete data or configuration files.
4. Every `ADAPTER` module identifies a concrete adapter path and public API.
5. Every `SHARED_EXTENSION` identifies the experiment family that will reuse it.
6. Every `CORE_EXTENSION` identifies exact common files and regression scope.
7. Every `BLOCKED` module contains at least one explicit blocker.
8. `create_files` and `reuse_files` must not contain the same path.
9. `modify_files` and `must_not_modify` must not contain the same path.
10. Production files must not be created during this phase.
11. Existing data in the user document must not be listed as missing.
12. Planned paths must match the current repository layout.
13. Planned APIs must include returned shapes.
14. Tests must be concrete enough to implement in later phases.
15. `next_skill` must name exactly one Skill.

## Prohibited actions

During this phase do not:

```text
create production Python modules
create the final experiment.yaml
materialize experiment CSV files
materialize experiment NPY or NPZ files
modify registry.py
modify theory files
modify nuclear-response files
modify rate files
modify kernel files
implement a source model
implement a target model
implement detector response
implement Slow counts
implement Fast counts
implement statistics
generate new reference arrays
run the complete experiment implementation
automatically start the next phase
```

The only files that may be created are:

```text
runs/<dataset_id>/00_INPUT_INVENTORY.md
runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
```

No existing production file should be modified.

## Backup rule

Phase 0 should not modify existing files.

If an unexpected existing workflow report must be updated, back it up under:

```text
backup/<relative-original-path>
```

and record the action in:

```text
backup/BACKUP_MANIFEST.md
```

Do not back up files that are only read.

## Gate I

Gate I passes only when:

1. every independent dataset has a unique dataset ID;
2. the physics document and attachments have been fully inventoried;
3. supplied numerical data have been recorded with units and shapes;
4. the statistical data mode has been identified;
5. every module has one valid classification;
6. reusable repository files have been verified by inspection;
7. planned file paths are concrete;
8. planned public APIs are defined;
9. planned output shapes are defined;
10. planned tests are concrete;
11. blockers are explicit;
12. protected files are listed;
13. no production code or data have been created or modified.

Use:

```yaml
gate:
  phase: I
  status: PASS
  reasons:
    - ...
```

when all conditions are satisfied.

Use:

```yaml
gate:
  phase: I
  status: BLOCKED
  reasons:
    - ...
```

when the implementation plan cannot be completed.

A blocker in a later module does not necessarily block the whole Phase 0
manifest.

For example, missing Fast templates may block `fast_counts` while still
allowing Gate I to pass if the blocker and later action are clearly recorded.

## Final response

After writing the two Phase 0 files, report only:

```text
Dataset IDs
Module classifications
Files planned for creation
Files planned for modification
Files that must not be modified
Blockers
Gate I status
Single next Skill
```

Also state:

```text
Production code created: none
Production data created: none
Existing production files modified: none
```

Then stop.

Do not begin the next Skill automatically.

## Hard rules

- Use the user's physics document as the experiment definition.
- Use attached machine data when they are explicitly part of the input.
- Use optional reference programs only as secondary numerical references.
- Use CsI only as a local API and validation reference.
- Do not copy a complete CsI module.
- Do not request data already present in the user's document.
- Do not infer missing arrays from printed output.
- Do not invent repository paths or functions.
- Do not create a Python file solely because a LaTeX subsection exists.
- Do not modify production code during Phase 0.
- Back up every existing file before modification.
- Report created, modified, reused, and prohibited files.
- Record units and returned shapes.
- Do not proceed past a failed Gate.
- Stop after Gate I.