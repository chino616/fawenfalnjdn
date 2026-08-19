---
name: cevns-source
description: Materialize and validate the approved source model, creating production source data and the minimum required source adapter.
---

# cevns-source

## Purpose

Execute the Source phase of the CEvNS experiment-integration workflow.

Convert the approved Phase 0 source plan into:

```text
machine-readable source data
source configuration
the minimum required source callable
focused source tests
a validated experiment-spec connection
```

This is the first phase that may create experiment-specific production physics
code and numerical data.

Do not re-parse the complete experiment physics document.

## Preconditions

Require:

```text
Gate I = PASS
Gate D0 = PASS
```

The target must also be ready.

Target readiness is satisfied by either:

```text
Gate T0 = PASS
```

or:

```text
target.status = REUSE or CONFIG_ONLY
```

with the target contract already validated during the Dataset phase.

If the approved source status is:

```text
BLOCKED
```

stop and report the blocker.

## Required references

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md

workflows/experiment-integration/templates/
03_SOURCE.md

workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md

workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml

workflows/experiment-integration/runs/<dataset_id>/
01_DATASET.md

data/experiments/<dataset_id>/experiment.yaml
```

If a conditional Target phase was executed, also read:

```text
workflows/experiment-integration/runs/<dataset_id>/
02_DETECTOR_TARGET.md
```

Inspect only the source interfaces identified by:

```text
workflows/experiment-integration/CSI_REFERENCE_MAP.md
```

The Phase 0 inventory and manifest are authoritative for:

```text
source components
flavors
source tables
units
support
interpolation
matching
boundary behavior
normalization
uncertainties
planned files
planned tests
```

Return to the original physics document only when the Phase 0 outputs contain
an explicit ambiguity or inconsistency.

Do not independently reinterpret the complete source definition.

## Procedure

### 1. Verify the approved source plan

Read:

```text
modules.source
```

from:

```text
00_IMPLEMENTATION_MANIFEST.yaml
```

Confirm:

```text
source status
source components
flavors
energy and time support
source unit
normalization convention
interpolation rule
matching rule
boundary behavior
physical constraints
approved files
approved public API
approved tests
blockers
```

Do not introduce a new source convention that was not approved in Phase 0.

### 2. Inspect existing source interfaces

Use `CSI_REFERENCE_MAP.md` to inspect only the source helpers used by the
existing experiment implementations.

Inspect:

```text
source callable signature
component labels
flavor labels
energy units
time units
normalization placement
scalar and array behavior
source-related tests
```

Use CsI only as a local API and validation reference.

Do not copy:

```text
SNS spectra
SNS timing distributions
CsI normalization parameters
CsI component weights
a complete CsI Slow implementation
```

Inspect actual functions and imports.

Do not infer APIs from filenames alone.

### 3. Select the implementation type

Use the approved Phase 0 classification.

#### REUSE

Reuse the verified existing source implementation.

Do not create new source code or duplicate source data.

#### CONFIG_ONLY

Materialize only the approved configuration and numerical tables.

Use an existing generic loader.

Do not create a source Python adapter.

#### ADAPTER

Create the thinnest experiment-level source adapter required by the approved
contract.

Typical reasons include:

```text
piecewise source definitions
matching between source models
normalization integrals
special boundary behavior
component routing
line spectra
time dependence
```

#### SHARED_EXTENSION

Create a reusable experiment-family source implementation.

Use this only when multiple datasets can share the source model.

#### CORE_EXTENSION

Modify shared source infrastructure only when the missing capability is
genuinely general.

Back up all modified shared files and run the complete affected regression
suite.

### 4. Materialize source parameters and tables

Store scalar parameters in:

```text
experiment.yaml
```

or in an approved source-specific YAML file when required by the current
schema.

Materialize approved numerical tables as:

```text
CSV or JSON
```

for small human-readable tables, or:

```text
NPY or NPZ
```

for large arrays, matrices, or multidimensional data.

Every table must include or document:

```text
column names or axes
units
normalization
interpolation
boundary behavior
provenance
```

Do not create files that are not listed in the approved manifest.

Do not infer missing numerical arrays from plots, summaries, or printed output.

### 5. Implement interpolation and boundaries

Implement exactly the approved:

```text
tabulated range
interpolation order
interpolation variable
matching point
matching formula
lower boundary
upper boundary
outside-support behavior
nonnegativity condition
continuity condition
```

Do not silently:

```text
extrapolate
clip
smooth
renormalize
replace negative values
change the interpolation order
change the matching point
```

When publication and reproduction modes differ, implement only the
authoritative mode identified by Phase 0 unless both are explicitly required.

### 6. Implement normalization

Implement the approved normalization exactly once.

Check whether the supplied source already includes:

```text
source power
geometric dilution
distance
detector position
time integration
component weights
```

Do not multiply any of these factors twice.

Recompute normalization diagnostics from the implemented source definition.

Do not preserve a diagnostic constant derived from an obsolete boundary rule.

### 7. Implement the source callable

Use the repository-native public API when available.

When a new callable is required, use a contract equivalent to:

```python
def differential_flux(
    energy,
    experiment_spec,
    *,
    component="total",
):
    ...
```

For a time-dependent source, add the required time argument.

Document:

```text
input type
input unit
input shape
component labels
returned type
returned unit
returned shape
returned axes
scalar behavior
array behavior
outside-support behavior
error behavior
```

The callable must return the differential source quantity, not merely a loaded
table.

### 8. Add focused source tests

Create only tests approved by the manifest.

Test:

```text
all tabulated nodes
all coefficient tables
source units
lower boundary
upper boundary
outside-support behavior
matching continuity
finite values
nonnegative values when physically required
integrated normalization
component sums
scalar input
array input
unknown-component errors
missing-data errors
```

For time-dependent sources, also test:

```text
time support
time normalization
time integration counted exactly once
```

For shared or core changes, run all affected existing source regressions.

Do not update reference values or relax tolerances merely to make tests pass.

### 9. Record numerical diagnostics

Compute and record:

```text
normalization integral
integrated source
matching factors
left matching value
right matching value
continuity residual
minimum sampled source value
maximum sampled source value
component-sum residual
```

Diagnostics must come from the implemented authoritative source definition.


### 10. Update the experiment specification

Only after Source tests pass, update:

```text
data/experiments/<dataset_id>/experiment.yaml
```

Record:

```text
source status
source callable
source data files
components
flavors
energy support
time support
returned source unit
normalization convention
boundary convention
```

Do not mark the source as implemented before its tests pass.

Do not modify `registry.py` unless the approved manifest explicitly identifies
a new callable type that the existing loader cannot resolve.

### 11. Create the Source report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
03_SOURCE.md
```

Use:

```text
workflows/experiment-integration/templates/
03_SOURCE.md
```

Record:

```text
approved source classification
source data files
source implementation
public API
boundary and interpolation rules
normalization
tests
numerical diagnostics
experiment.yaml update
blockers
Gate S0
```

Do not repeat unrelated target, theory, detector-response, Slow, Fast, or
statistical information.



## Allowed production outputs

Depending on the approved manifest, this Skill may create:

```text
data/experiments/<dataset_id>/source_*.csv
data/experiments/<dataset_id>/source_*.json
data/experiments/<dataset_id>/source_*.npy
data/experiments/<dataset_id>/source_*.npz

src/cevns_pyeft/experiments/<family>/source.py

tests/test_<dataset_id>_source.py

workflows/experiment-integration/runs/<dataset_id>/
03_SOURCE.md
```

It may modify:

```text
data/experiments/<dataset_id>/experiment.yaml
```

after validation passes.

Create only files approved by the Phase 0 manifest.

### Generate Source validation figures

After the Source callable passes its numerical tests:

1. sample the validated differential flux on a documented energy grid;
2. save the sampled values under the workflow run directory;
3. generate full-range and low-energy spectrum figures;
4. generate a literature-comparison figure when an appropriate published
   reference exists;
5. record the paper, figure number, normalization, and fission fractions.

Figures are validation artifacts and must not be imported by the runtime
package.

Do not pass Gate S0 when the numerical tests pass but the plotted spectrum
shows an unexplained discontinuity, negative region, incorrect support, or
unexpected normalization.

## Backup rule

Before modifying any existing file, create a backup under:

```text
backup/<relative-original-path>
```

Record the backup in:

```text
backup/BACKUP_MANIFEST.md
```

Do not create backups for files that are only read.

## Prohibited actions

During this Skill do not:

```text
repeat the complete Phase 0 extraction
change approved Phase 0 source physics
create unapproved source files
copy SNS or CsI physical source data
implement target physics
implement theory or nuclear response
implement differential cross section
implement detector response
implement Slow counts
implement Fast counts
implement statistics
modify unrelated experiment datasets
modify registry.py without an approved condition
start the next Skill automatically
```

## Gate S0

Gate S0 passes only when:

1. the source implementation matches the approved Phase 0 contract;
2. every source data file has explicit provenance;
3. all approved numerical values are reproduced;
4. the source callable is loadable;
5. input and output units are explicit;
6. support and boundary behavior are correct;
7. matching conditions pass;
8. normalization passes;
9. required physical constraints pass;
10. component sums pass;
11. scalar and array behavior pass;
12. `experiment.yaml` points to the validated source implementation;
13. all required Source tests pass;
14. no unrelated experiment behavior changes.

Set:

```text
PASS
```

or:

```text
BLOCKED
```

and record the reasons.

A blocked Gate S0 must identify:

```text
missing or inconsistent source input
affected source component
files not created
required resolution
next allowed action
```

## Final response

Report only:

```text
source classification
files created
files modified
conditionally modified files
protected files
public source API
source components
source support and units
tests run
numerical diagnostics
blockers
Gate S0 status
single next Skill
```

Then stop.

Do not execute the next Skill automatically.