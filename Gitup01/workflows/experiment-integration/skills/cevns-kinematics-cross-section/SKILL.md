---
name: cevns-kinematics-cross-section
description: Validate the experiment kinematics, reuse the shared differential cross section, and expose explicit full-response and Helm model choices.
---

# cevns-kinematics-cross-section

## Purpose

Execute Phase 5.

Reuse the existing differential-cross-section implementation whenever it already
accepts the approved theory inputs and target Response object.

Create only the minimum adapter required for:

```text
experiment-specific kinematics
unit conversion
target routing
flavor routing
full_response versus helm_sm model selection
```

Do not duplicate the shared theory or differential-cross-section formulas.

## Preconditions

Require:

```text
Gate S0 = PASS
Gate T1 = PASS
```

Read:

```text
workflows/experiment-integration/AGENTS.md
workflows/experiment-integration/EXPERIMENT_WORKFLOW.md
workflows/experiment-integration/CSI_REFERENCE_MAP.md
workflows/experiment-integration/templates/
05_KINEMATICS_CROSS_SECTION.md

workflows/experiment-integration/runs/<dataset_id>/
00_INPUT_INVENTORY.md

workflows/experiment-integration/runs/<dataset_id>/
00_IMPLEMENTATION_MANIFEST.yaml

workflows/experiment-integration/runs/<dataset_id>/
03_SOURCE.md

workflows/experiment-integration/runs/<dataset_id>/
04_THEORY_RESPONSE.md

data/experiments/<dataset_id>/experiment.yaml
```

Inspect the actual shared implementation, including as applicable:

```text
src/cevns_pyeft/rates/differential.py
src/cevns_pyeft/theory/li2026/
src/cevns_pyeft/nuclear/response.py
existing Helm or form-factor helpers
existing kinematic helpers
existing cross-section tests
```

Do not infer callable signatures from filenames.

## Procedure

### 1. Inspect the shared cross-section contract

Record:

```text
actual callable
implementation file
energy input unit
recoil input unit
target-mass unit
Response argument
Wilson-coefficient argument
flavor argument
neutrino or antineutrino argument
returned unit
scalar behavior
array behavior
broadcasting
out-of-support behavior
```

Trace the actual call chain:

```text
E_nu and recoil
→ kinematic support
→ selected nuclear model
→ shared differential cross section
```

### 2. Decide whether the cross section is reusable

Classify:

```text
cross_section: REUSE / ADAPTER / CORE_EXTENSION / BLOCKED
```

Use `REUSE` when the shared callable accepts:

```text
arbitrary target Response object
approved Wilson coefficients
approved flavor
approved neutrino or antineutrino mode
required input units
```

Use `ADAPTER` when the shared formula is reusable but a thin wrapper is needed
for:

```text
unit conversion
experiment-spec lookup
Response-key lookup
kinematic approximation
model selection
```

Do not create a new differential-cross-section formula for an adapter.

### 3. Define the nuclear model selector

Support explicit, mutually exclusive model labels.

#### `full_response`

Use:

```text
shared theory implementation
approved Wilson coefficients
target Response object
all required nuclear-response channels
```

Do not call Helm in this branch.

Do not multiply the result by a Helm form factor.

#### `helm_sm`

Use:

```text
Standard Model weak charge
Helm form factor
the selected kinematic convention
```

Do not load or contract the full nuclear Response in this branch.

Reject non-Standard-Model Wilson coefficients unless an explicit validated
mapping exists.

Record:

```text
default model
available models
Helm coefficient restrictions
unsupported combinations
```

For general EFT analysis, the default should normally be:

```text
full_response
```

### 4. Validate or implement Helm

First inspect whether a shared Helm implementation already exists.

If it exists, reuse it.

If it does not exist, create the smallest approved shared or experiment-family
helper.

Record the convention:

```text
weak charge
radius convention
effective radius
skin thickness
spherical Bessel convention
proton and neutron treatment
F(0) normalization
```

Require:

```text
F_Helm(0) = 1
```

Helm belongs to the form-factor or cross-section path.

Do not add Helm data to the nuclear Response database.

### 5. Implement experiment kinematics

Record:

```text
recoil variable
recoil unit
neutrino-energy unit
target-mass unit
exact E_nu_min
publication or reproduction E_nu_min
selected default
recoil endpoint
physical support
```

If the experiment requires a named approximation, expose it explicitly, for
example:

```text
exact
heavy_nucleus_approximation
publication_reproduction
```

Do not replace a shared exact formula globally.

### 6. Implement only the minimum adapter

When required, create an adapter equivalent to:

```python
def differential_cross_section(
    energy,
    recoil,
    experiment_spec,
    coefficients=None,
    *,
    model="full_response",
    kinematics="publication_reproduction",
):
    ...
```

Use the actual repository naming convention.

The adapter must:

```text
load target metadata
load the Response object for full_response
select the kinematic rule
call the shared cross-section implementation
select Helm only for helm_sm
preserve units and array behavior
```

It must not reproduce the complete theory formula.

Possible files:

```text
src/cevns_pyeft/experiments/<family>/kinematics.py
src/cevns_pyeft/experiments/<family>/cross_section.py
```

Create `cross_section.py` only when the existing shared API cannot expose the
model selector directly.

### 7. Generate diagnostic grids and figures

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
artifacts/kinematic_endpoints.csv

workflows/experiment-integration/runs/<dataset_id>/
artifacts/cross_section_grid.csv

workflows/experiment-integration/runs/<dataset_id>/
figures/cross_section_vs_recoil.png

workflows/experiment-integration/runs/<dataset_id>/
figures/cross_section_vs_recoil.pdf

workflows/experiment-integration/runs/<dataset_id>/
figures/full_response_vs_helm.png

workflows/experiment-integration/runs/<dataset_id>/
figures/full_response_vs_helm.pdf
```

The comparison must use:

```text
the same target
the same E_nu
the same recoil
the same kinematic convention
the same Standard Model constants
the same units
```

Do not independently normalize the two models.

### 8. Add focused tests

Test kinematics:

```text
exact endpoint
reproduction approximation
physical-support mask
zero outside support
unit conversion
scalar and array behavior
```

Test `full_response`:

```text
approved Response key
shared cross-section callable
Standard Model benchmark
approved EFT benchmark when available
finite total cross section
nonnegative total cross section
Helm is not called
```

Test `helm_sm`:

```text
F_Helm(0) = 1
stable q → 0 limit
finite form factor
finite nonnegative Standard Model cross section
full Response is not loaded
non-Standard-Model coefficients are rejected
```

Test saved diagnostics:

```text
saved grids reproduce the figures
model labels are explicit
units are explicit
```

Require nonnegativity only for the total physical differential cross section,
not separately reported interference terms.

### 9. Update the experiment specification

After all tests pass, update `experiment.yaml` only when required.

Record:

```text
default cross-section model
available cross-section models
kinematic convention
cross-section callable or adapter
Helm restrictions
```

Do not mark an adapter as implemented before validation passes.

### 10. Create the phase report

Create:

```text
workflows/experiment-integration/runs/<dataset_id>/
05_KINEMATICS_CROSS_SECTION.md
```

Use:

```text
workflows/experiment-integration/templates/
05_KINEMATICS_CROSS_SECTION.md
```

Record:

```text
shared cross-section callable
reuse or adapter decision
full_response path
helm_sm path
kinematic conventions
files
tests
diagnostic grids and figures
Gate X
```

## Prohibited actions

Do not:

```text
duplicate the shared Li2026 cross section
create an experiment-specific amplitude
create an experiment-specific nuclear Response implementation
multiply full_response by Helm
apply general EFT coefficients to helm_sm without a validated mapping
silently replace exact kinematics globally
modify shared theory or Response data without CORE_EXTENSION approval
implement detector response
implement Slow
implement Fast
implement statistics
start the next Skill automatically
```

## Gate X

Gate X passes when:

```text
the shared cross section is reused wherever possible
the selected kinematic convention is explicit
full_response and helm_sm are mutually exclusive
full_response passes theory and Response benchmarks
Helm conventions and restrictions are explicit
unsupported Helm coefficient combinations raise an error
physical masks and endpoints pass
units and array behavior pass
diagnostic grids and figures are generated
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
kinematics classification
cross-section classification
shared callable reused
new adapter
default model
available models
files created
files modified
tests run
diagnostic results
blockers
Gate X status
single next Skill
```

Then stop.