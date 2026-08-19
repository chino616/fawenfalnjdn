---
name: cevns-slow-counts
description: Implement and validate the authoritative direct-integration event prediction for one CEvNS dataset.
---

# cevns-slow-counts

## Purpose

Execute Phase 7.

Build the authoritative Slow prediction from validated Source, theory,
cross-section, target normalization, and Detector Response components.

Slow is the reference against which every Fast representation is validated.

## Preconditions

Require:

```text
Gate D0 = PASS
Gate S0 = PASS
Gate T1 = PASS
Gate X = PASS
Gate R = PASS
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/templates/07_SLOW_COUNTS.md

runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
runs/<dataset_id>/03_SOURCE.md
runs/<dataset_id>/04_THEORY_RESPONSE.md
runs/<dataset_id>/05_KINEMATICS_CROSS_SECTION.md
runs/<dataset_id>/06_DETECTOR_RESPONSE.md

data/experiments/<dataset_id>/experiment.yaml
```

Inspect the actual CsI and Ar Slow modules only for:

```text
public API
integration control flow
component axes
return shape
test structure
```

Do not copy a complete existing Slow module.

## Procedure

### 1. Inspect the real reference path

Record actual files, symbols, signatures, units, axes, and return values.

Trace:

```text
Slow wrapper
→ source
→ shared differential cross section
→ target-time normalization
→ detector folding
→ reconstructed bins
```

Do not start implementation before this path is documented.

### 2. Implement the direct calculation

Implement:

```text
neutrino-energy integration
true-recoil spectrum
target-time normalization
detector-response folding
reconstructed-bin integration
```

Use the validated Source, cross-section, Response, and Detector Response
callables.

Do not reproduce their physical formulas inside the Slow module.

Apply exposure exactly once.

### 3. Preserve model selection

Pass explicit selections for:

```text
full_response or helm_sm
exact or publication-reproduction kinematics
```

Do not combine Helm with the full nuclear Response.

### 4. Define the public output

Return the dataset prediction with the declared axes, shape, and unit.

Preserve detector, target, or source components only when applicable.

Document omitted component axes.

### 5. Generate diagnostics and reference data

Create:

```text
true-recoil spectrum grid
reconstructed-spectrum grid
binned Slow counts
convergence table
diagnostic figures
independent Slow reference array
```

Store diagnostics under the workflow run directory.

Store the validated regression reference under the approved test reference
directory.

### 6. Test

Validate:

```text
shape
units
finite and nonnegative physical counts
component sums
exposure counted once
support and endpoints
integration convergence
grid or tolerance refinement
benchmark coefficient points
supported complex coefficients
absence of Fast imports or caches
```

Do not change Slow to improve Fast agreement.

### 7. Update the experiment specification

After tests pass, record the validated Slow callable and output contract in
`experiment.yaml` when supported by the current schema.

### 8. Create the report

Create:

```text
runs/<dataset_id>/07_SLOW_COUNTS.md
```

using:

```text
templates/07_SLOW_COUNTS.md
```

## Allowed outputs

```text
src/cevns_pyeft/experiments/<family>/slow_counts_<dataset_id>.py
tests/test_<dataset_id>_slow_counts.py
tests/reference_<dataset_id>/slow_reference.npy
runs/<dataset_id>/artifacts/*
runs/<dataset_id>/figures/*
runs/<dataset_id>/07_SLOW_COUNTS.md
```

## Prohibited actions

Do not:

```text
import Fast kernels or Fast caches
derive Slow reference values from Fast
reimplement theory, source, cross section, or Detector Response
apply exposure more than once
modify another dataset
modify existing reference arrays to hide disagreement
implement Fast
implement statistics
start the next Skill automatically
```

## Gate L

Gate L passes only when the direct calculation, convergence tests, output
contract, diagnostics, and independent reference array are validated.

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
Slow classification
public callable
files created
files modified
output axes and shape
integration settings
tests run
numerical diagnostics
reference array
blockers
Gate L status
single next Skill
```

Then stop.