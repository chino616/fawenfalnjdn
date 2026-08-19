---
name: cevns-fast-counts
description: Build and validate accelerated event-count representations against the authoritative Slow calculation.
---

# cevns-fast-counts

## Purpose

Execute Phase 8.

Build only Fast representations justified by the approved parameter dependence.

Validate every representation bin by bin against the verified Slow prediction.

Fast is not authoritative.

## Preconditions

Require:

```text
Gate L = PASS
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/templates/08_FAST_COUNTS.md

runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
runs/<dataset_id>/07_SLOW_COUNTS.md
data/experiments/<dataset_id>/experiment.yaml
```

Inspect:

```text
existing CsI and Ar Fast wrappers
kernels/basis.py
kernels/builder.py
kernels/reconstruction.py
kernels/storage.py
existing Fast tests
```

Use these only for API, metadata, basis, serialization, and validation
conventions.

## Procedure

### 1. Inspect the real Fast interfaces

Record actual:

```text
files
symbols
function signatures
basis metadata
array shapes
serialization format
reconstruction API
stale-artifact checks
```

Do not infer the API from filenames.

### 2. Classify every requested representation

Treat independently:

```text
cumulative spectrum
EFT quadratic kernel
response matrix
source cache
other surrogate
```

For every representation record:

```text
required for release
parameter dependence
implementation status
inputs
outputs
blockers
```

Do not force all Fast methods into one implementation.

### 3. Build only unblocked representations

For cumulative Fast:

```text
sample the validated reconstructed spectrum
build the cumulative representation
reconstruct bin counts from bin edges
validate grid and interpolation convergence
```

For EFT kernels:

```text
confirm the complete coefficient basis and order
derive all linear and quadratic terms from Slow
store metadata and kernel arrays
validate reconstruction at multiple coefficient points
```

If the complete basis is unknown, mark the EFT kernel `BLOCKED`.

Do not generate placeholder or partial formal kernels.

### 4. Preserve the Slow contract

Fast must return the same:

```text
axes
shape
unit
component convention
coefficient convention
```

as Slow.

Fast must not apply source normalization, exposure, detector response, or
statistics again.

### 5. Validate bin by bin

Compare multiple parameter points and save:

```text
Slow
Fast
absolute difference
relative difference
tolerance
```

Do not validate only total event counts.

Include interference-sensitive and complex-coefficient points when supported.

### 6. Generate diagnostics

Create:

```text
fast_vs_slow.csv
fast_runtime.csv
fast_vs_slow.png
fast_relative_error.png
```

Record:

```text
maximum absolute error
maximum relative error
worst bin
worst parameter point
Slow runtime
Fast runtime
speedup
```

### 7. Test metadata and storage

Validate:

```text
basis order
shape
units
serialization round trip
source metadata
detector metadata
grid metadata
stale-artifact rejection
unsupported input errors
```

Never accept a cached artifact whose conventions differ from the current
dataset.

### 8. Update the experiment specification

Only validated Fast representations may be marked implemented in
`experiment.yaml`.

Blocked or deferred representations must remain explicitly unavailable.

### 9. Create the report

Create:

```text
runs/<dataset_id>/08_FAST_COUNTS.md
```

using:

```text
templates/08_FAST_COUNTS.md
```

## Prohibited actions

Do not:

```text
change Slow to match Fast
derive Slow references from Fast
generate a kernel with an incomplete basis
hide failed bins by comparing only totals
apply exposure or detector response again
relax tolerances without justification
replace existing Fast reference arrays
implement statistics
start the next Skill automatically
```

## Gate F

Evaluate every representation separately.

Overall Gate F passes only when every representation required for the current
release passes bin-by-bin validation.

Optional blocked representations may remain blocked if clearly documented and
not exposed as implemented.

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
Fast representations requested
representations implemented
representations blocked
files created
files modified
public APIs
parameter points
bin-by-bin errors
runtime and speedup
tests run
blockers
Gate F status
single next Skill
```

Then stop.