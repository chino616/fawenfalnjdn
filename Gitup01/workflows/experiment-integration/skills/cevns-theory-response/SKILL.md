---
name: cevns-theory-response
description: Validate the shared theory and nuclear-response implementation for one dataset and generate reproducible intermediate Response diagnostics.
---

# cevns-theory-response

## Purpose

Execute Phase 4.

Validate that the approved theory and target nuclear Response can be reused for
the dataset.

For `REUSE`, do not create experiment-specific theory or nuclear-response code.

This phase may create diagnostic tables and figures under the workflow run
directory.

## Preconditions

Require:

```text
Gate I = PASS
Gate D0 = PASS
Gate S0 = PASS
target ready
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/templates/04_THEORY_RESPONSE.md

workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md

workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml

workflows/experiment-integration/runs/<dataset_id>/
01_DATASET.md

workflows/experiment-integration/runs/<dataset_id>/
03_SOURCE.md

data/experiments/<dataset_id>/experiment.yaml
```

Inspect the actual shared implementation, including as applicable:

```text
src/cevns_pyeft/theory/li2026/
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
existing theory and Response tests
```

Do not infer APIs from filenames alone.

## Procedure

### 1. Verify the approved theory contract

Confirm:

```text
incoming flavor
neutrino or antineutrino
outgoing-flavor treatment
theory baseline
Wilson-coefficient basis
coefficient order
complex-coefficient support
target isotope
Response key
```

Determine whether the approved interaction is already supported.

### 2. Inspect the shared call chain

Record the actual path:

```text
Response data
→ Response loader
→ target Response object
→ shared theory contraction
→ amplitude squared
```

Record:

```text
reference files
actual symbols
function signatures
input units
returned types
basis labels
channel labels
scalar and array behavior
```

Do not copy a complete theory, CsI, Ar, or Response module.

### 3. Classify the implementation

Select one:

```text
REUSE
ADAPTER
CORE_EXTENSION
BLOCKED
```

Use `REUSE` when the existing theory accepts the approved Wilson coefficients
and the existing Response database contains the required target.

Use `ADAPTER` only for a thin parameter, flavor, or basis wrapper.

Use `CORE_EXTENSION` only when the shared theory or Response infrastructure
lacks a genuinely general capability.

For `REUSE`:

```text
new theory code: no
new Response code: no
diagnostic artifacts: yes
```

### 4. Generate nuclear-Response diagnostics

Load the approved target Response.

Evaluate it on a documented recoil or momentum-transfer grid.

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
artifacts/nuclear_response_grid.csv

workflows/experiment-integration/runs/<dataset_id>/
figures/nuclear_response_channels.png

workflows/experiment-integration/runs/<dataset_id>/
figures/nuclear_response_channels.pdf
```

The saved grid must include the available repository-native information, such
as:

```text
target
recoil
momentum transfer
Response variable
channel
basis labels
value
```

Preserve the repository basis and channel names.

Do not independently normalize every channel.

Individual interference responses may be negative.

### 5. Evaluate theory benchmarks

Evaluate the shared amplitude or theory contraction at:

```text
one Standard Model or zero-BSM point
one additional approved coefficient point when available
representative physical energy-recoil points
```

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
artifacts/theory_response_benchmarks.csv
```

Verify that the total amplitude squared is finite and nonnegative.

Do not require individual interference contributions to be nonnegative.

### 6. Add or run focused tests

Validate:

```text
Response key exists
A, Z, and N match the dataset
expected Response channels are available
basis order is preserved
Response grid is finite
shared theory callable loads
flavor routing is correct
neutrino or antineutrino routing is correct
Wilson-coefficient order is preserved
total amplitude squared is finite and nonnegative
diagnostic figures are reproducible from the saved grid
```

For `CORE_EXTENSION`, run all affected theory, Response, CsI, Ar, Slow, and Fast
regressions.

Do not alter shared Response data or relax tolerances to make tests pass.

### 7. Create the phase report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
04_THEORY_RESPONSE.md
```

Use:

```text
workflows/experiment-integration/templates/
04_THEORY_RESPONSE.md
```

Record:

```text
classification
reference implementation
Response key
available channels and basis
diagnostic files
benchmark results
tests
files created
files modified
Gate T1
```

## Allowed outputs

For `REUSE`, create only:

```text
runs/<dataset_id>/artifacts/nuclear_response_grid.csv
runs/<dataset_id>/artifacts/theory_response_benchmarks.csv
runs/<dataset_id>/figures/nuclear_response_channels.png
runs/<dataset_id>/figures/nuclear_response_channels.pdf
runs/<dataset_id>/04_THEORY_RESPONSE.md
```

Do not modify production theory or Response files.

## Prohibited actions

Do not:

```text
write a second experiment-specific amplitude
write a second experiment-specific nuclear Response implementation
multiply a full nuclear Response result by a Helm form factor
copy CsI or Ar physical parameters
change shared Response data for diagnostic convenience
implement kinematics
implement detector response
implement Slow
implement Fast
implement statistics
start the next Skill automatically
```

## Gate T1

Gate T1 passes when:

```text
the approved theory is supported
the target Response loads
basis and channel conventions are documented
Response diagnostics are generated
the shared theory path passes benchmark checks
no unnecessary experiment-specific theory or Response code was created
```

Set:

```text
PASS
```

or:

```text
BLOCKED
```

and record reasons.

## Final response

Report only:

```text
theory classification
Response classification
reference implementation
Response key
files created
files modified
tests run
diagnostic results
blockers
Gate T1 status
single next Skill
```

Then stop.