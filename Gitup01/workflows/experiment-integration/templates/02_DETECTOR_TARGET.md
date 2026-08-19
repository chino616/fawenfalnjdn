# Target Inventory Report Template

## Purpose

This template records the detector and target inventory before source
implementation.

This is a text-only phase. Do not create target code, target CSV files, target
tests, or runtime-data edits while filling this report.

## Required Inputs

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/runs/<dataset_id>/00_INPUT_INVENTORY.md
workflows/experiment-integration/runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
workflows/experiment-integration/runs/<dataset_id>/01_DATASET.md
data/experiments/<dataset_id>/experiment.yaml
```

Return to the physics document only if the Phase 0 inventory or manifest has a
specific target ambiguity.

## Phase 0 Target Decision

```text
dataset_id:
target_status:
target_mode:
reason:
Gate I status:
Gate D0 status:
```

The `target_status` may be:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

In this phase, the status is documentation only. Any code or data-file
implementation is deferred to a later explicit implementation phase.

## Detector Inventory

| Detector | Material | Active mass | Live time | Exposure | Source |
|---|---|---:|---:|---:|---|

Record:

```text
detector labels:
detector count:
detector axis required:
detector-dependent calibration:
detector-dependent target:
```

## Exposure Semantics

For each detector or exposure component record:

```text
active mass:
active-mass unit:
live time:
live-time unit:
exposure:
exposure unit:
exposure already includes active mass:
exposure already includes live time:
additional mass multiplication required:
additional live-time multiplication required:
detector-dependent exposure:
isotope-dependent exposure:
```

Exposure must be counted exactly once by later Slow/Fast/statistics phases.

## Target Inventory

### Material Inventory

| Material | Detector | Formula or composition | Mass fraction | Source |
|---|---|---|---:|---|

Record:

```text
materials:
compound targets:
material normalization:
detector-dependent materials:
```

### Isotope Inventory

| Material | Isotope | A | Z | N | Abundance or stoichiometric weight | Molar mass |
|---|---|---:|---:|---:|---:|---:|

Record:

```text
isotopes:
natural, enriched, or pure:
abundance convention:
stoichiometric convention:
abundance normalization:
isotope axis required:
```

If the experiment uses an effective isotope approximation, record:

```text
approximation name:
exact target composition being replaced:
effective target:
reason:
scope:
validation requirement:
```

Do not silently replace a natural or mixed target with one effective isotope.

## Nuclei-Per-Mass Convention

For every target component record:

```text
component:
formula:
Avogadro constant:
molar mass:
abundance factor:
stoichiometric factor:
mass fraction:
nuclei per kilogram:
unit:
future implementation owner:
```

For a pure isotope, the usual convention is:

```text
nuclei_per_kg = Avogadro_constant * 1000 / molar_mass_g_per_mol
```

## Nuclear-Response Routing

For every isotope record:

| Isotope | A | Z | N | Response key | Available | Response source |
|---|---:|---:|---:|---|---|---|

Record:

```text
Response database:
Response loader:
required response channels:
missing response keys:
fallback prohibited:
```

Do not silently replace a missing isotope Response with a nearby isotope,
natural-element average, isoscalar approximation, or another experiment's
Response key.

## Component Axes

```text
detector axis:
material axis:
isotope axis:
target-response axis:
```

For every retained axis record:

```text
axis name:
labels:
public output or diagnostic only:
sum rule:
```

## Future Implementation Classification

Record the smallest later implementation need:

```text
status:
reason:
future implementation required:
future implementation scope:
planned future files:
blocked inputs:
```

Allowed statuses:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

Do not implement the planned files in this phase.

## Files

### Created

```text
workflows/experiment-integration/runs/<dataset_id>/02_DETECTOR_TARGET.md
```

### Modified

```text
None expected.
```

### Protected

```text
data/experiments/<dataset_id>/experiment.yaml
src/cevns_pyeft/experiments/<family>/target.py
src/cevns_pyeft/experiments/<family>/target_inventory.py
data/experiments/<dataset_id>/target.csv
data/experiments/<dataset_id>/isotope_inventory.csv
tests/test_<dataset_id>_target.py
src/cevns_pyeft/experiments/registry.py
source files
theory modules
rates modules
kernel modules
Slow implementations
Fast implementations
statistics implementations
```

## Diagnostics

Record:

```text
number of detectors:
number of materials:
number of isotopes:
nuclei per kilogram by component:
total nuclei per kilogram:
exposure by detector:
Response keys:
component-sum residual:
```

These are text/report diagnostics. Do not add a test file in this phase.

## Gate T0

Gate T0 passes only when:

```text
detector inventory is complete
target composition is complete
exposure semantics are explicit
exposure is counted exactly once
nuclei-per-mass convention is explicit
required Response keys are identified
component axes and sum rules are defined
future implementation need is classified
no production code or runtime data were modified
```

Record:

```text
status: PASS
reasons:
```

or:

```text
status: BLOCKED
reasons:
```

## Next Skill

```text
cevns-source
```

Stop after Gate T0. Do not execute Source automatically.
