---
name: cevns-target
description: Extract and validate the detector/target inventory as a text-only workflow phase before source implementation.
---

# cevns-target

## Purpose

Execute the Target Inventory phase.

This phase is intentionally text-only. It records the detector inventory, target
composition, exposure semantics, nuclei-per-mass convention, and nuclear
Response routing needed by later implementation phases.

Do not create target Python code, target CSV files, or target tests in this
phase. If the inventory later proves to require code, record that as a future
implementation need instead of implementing it here.

## Invocation condition

Invoke after:

```text
Gate I = PASS
Gate D0 = PASS
```

Invoke before:

```text
cevns-source
```

This phase applies to all target statuses, including:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

The status controls the recorded future implementation need. It does not allow
code creation during this phase.

## Required references

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/templates/02_DETECTOR_TARGET.md
workflows/experiment-integration/runs/<dataset_id>/00_INPUT_INVENTORY.md
workflows/experiment-integration/runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
workflows/experiment-integration/runs/<dataset_id>/01_DATASET.md
data/experiments/<dataset_id>/experiment.yaml
```

Return to the original physics document only when the Phase 0 inventory or
manifest contains an explicit target ambiguity or inconsistency.

Do not repeat the complete Phase 0 extraction.

## Phase boundary

This phase is responsible for documenting:

```text
detector inventory
target inventory
exposure normalization
nuclei-per-mass normalization
Response-key routing
component axes
target classification
future implementation need, if any
Gate T0
```

It is not responsible for:

```text
source implementation
target implementation
differential cross section
detector response
Slow counts
Fast counts
statistics
registry integration
```

## Procedure

1. Verify that Gate I and Gate D0 have passed.
2. Read the approved Phase 0 target decision.
3. Record every detector label, active mass, live time, exposure, material, and
   target mode.
4. Record every target component: isotope, `A`, `Z`, `N`, molar mass,
   abundance or stoichiometric weight, material fraction, and Response key.
5. State exposure semantics explicitly, including whether exposure already
   includes active mass and live time.
6. State the nuclei-per-kilogram formula for each component.
7. Verify Response-key availability from the existing repository interfaces.
8. Record required component axes and sum rules.
9. Record whether later implementation should be `REUSE`, `CONFIG_ONLY`,
   `ADAPTER`, `SHARED_EXTENSION`, `CORE_EXTENSION`, or `BLOCKED`.
10. Create or update only:

```text
workflows/experiment-integration/runs/<dataset_id>/02_DETECTOR_TARGET.md
```

## Prohibited actions

During this phase do not:

```text
create target.py
create target_inventory.py
create target.csv
create isotope_inventory.csv
create target tests
modify experiment.yaml
modify registry.py
modify source files
modify theory, rates, kernels, Slow, Fast, or statistics files
copy CsI physical target values
silently replace missing Response data
start cevns-source automatically
```

## Gate T0

Gate T0 passes only when:

1. detector inventory is complete;
2. target composition is complete;
3. exposure semantics are explicit;
4. exposure is counted exactly once in the documented convention;
5. nuclei-per-mass normalization is explicit;
6. required Response keys are identified;
7. component axes and sum rules are defined;
8. future implementation need is classified;
9. no production code or runtime data were modified by this phase.

Set:

```text
PASS
```

or:

```text
BLOCKED
```

and record the reason.

## Final response

Report only:

```text
target classification
files created
files modified
protected files
Response keys
component axes
numerical diagnostics
blockers
Gate T0 status
single next Skill: cevns-source
```

Then stop.
