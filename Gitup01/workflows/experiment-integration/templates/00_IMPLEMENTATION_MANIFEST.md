# Phase 0 Implementation Manifest Template

## Purpose

This template defines the required outputs of:

```text
skills/cevns-experiment-intake/SKILL.md
```

Phase 0 converts a user-supplied experiment physics document into a concrete
implementation plan.

Phase 0 does not create production code or production data.

## Required outputs

Create one output directory for every independent dataset:

```text
runs/<dataset_id>/
├── 00_INPUT_INVENTORY.md
└── 00_IMPLEMENTATION_MANIFEST.yaml
```

Independent runs, detector configurations, source configurations, binning
schemes, observed datasets, or likelihoods must not be merged under one
dataset ID unless the user document explicitly defines them as one combined
analysis.

---

# Part I: Input Inventory

Create:

```text
runs/<dataset_id>/00_INPUT_INVENTORY.md
```

Use the following structure.

## Dataset identity

```text
dataset_id:
experiment_family:
run_period:
detector_configuration:
source_configuration:
target_configuration:
statistical_data_mode:
```

## Input paths

```text
physics_document:
reference_documents:
machine_readable_attachments:
optional_reference_code:
repository_files_inspected:
```

## Experiment goal

State the intended calculation:

```text
signal:
slow:
fast:
statistics:
validation:
```

## Observable axes

For every observable record:

```text
name:
physical meaning:
true or reconstructed:
unit:
support:
binning:
returned axis:
```

Record the expected final event-count shape.

## Supplied scalar parameters

For every scalar record:

| Quantity | Symbol or key | Value | Unit | Source section |
|---|---|---:|---|---|

## Supplied formulas

For every formula record:

```text
name:
definition:
variables:
units:
validity range:
approximation:
source section:
intended implementation module:
```

## Supplied numerical tables

For every numerical table record:

```text
name:
source section or attachment:
row count:
column names:
column units:
interpolation rule:
boundary rule:
normalization:
intended machine-readable file:
```

Do not request a table again when it is already present in the document.

## Source definition

Record:

```text
source type:
components:
flavors:
energy support:
time support:
normalization:
interpolation:
matching:
lower-bound behavior:
upper-bound behavior:
extrapolation:
physical constraints:
uncertainties:
```

The inventory must explicitly state whether the source definition guarantees:

```text
finite values
nonnegative differential flux
zero outside physical support
continuity at matching points
correct integrated normalization
```

If the user document contains a legacy numerical rule that violates a physical
constraint, record both:

```text
documented legacy or reproduction rule
recommended publication rule
```

Do not silently choose between them.

## Detector and target definition

Record:

```text
detectors:
active masses:
live times:
exposures:
exposure semantics:
materials:
isotopes:
abundances or stoichiometry:
nuclei-per-kilogram convention:
nuclear-response keys:
```

State explicitly whether exposure already includes mass and live time.

## Theory and response definition

Record:

```text
incoming flavor:
outgoing flavor or flavor sum:
neutrino or antineutrino:
Wilson basis:
coefficient order:
standard-model point:
nuclear-response keys:
required theory extensions:
```

## Kinematics and differential cross section

Record:

```text
true recoil variable:
incident-energy variable:
units:
minimum incident energy:
recoil endpoint:
exact kinematics:
reproduction approximation:
differential-cross-section callable:
cross-section unit:
out-of-support behavior:
```

Do not silently replace an approximation explicitly required by the user
document.

## Detector response

Record separately:

```text
mean reconstructed observable
stochastic response
efficiency
binning
migration outside analysis window
```

Do not combine these into one opaque description when they can be validated
independently.

## Slow counts

Record:

```text
physical integration chain:
integration order:
integration variables:
integration support:
numerical settings:
component axes:
returned shape:
returned unit:
reference targets:
```

## Fast counts

Record every requested Fast representation separately.

Examples:

```text
quadratic EFT kernel
detector-response matrix
cumulative spectrum
source cache
validated surrogate
```

For every representation record:

```text
name:
mathematical basis:
required Slow input:
coefficient basis:
storage shape:
returned shape:
validation points:
blockers:
```

One blocked Fast representation must not automatically block another
independent Fast representation.

## Statistical data

Select exactly one primary data mode:

```text
raw_counts
signal_plus_background
on_off
background_subtracted_excess
unbinned_events
```

Record:

```text
observed data:
background data:
covariance:
nuisance parameters:
test statistic:
profiling or marginalization:
confidence construction:
reference values:
```

Do not infer an independent background array when the supplied data are already
background-subtracted.

## Missing information

For every missing input record:

```text
missing item:
expected source:
affected module:
reason required:
phase blocked:
other phases still possible:
```

A missing final validation benchmark does not necessarily block implementation
of the physical prediction.

## Current achievable implementation level

Select the highest currently achievable level:

```text
INPUT_PARSED
DATASET_PLANNED
SOURCE_PLANNED
TARGET_PLANNED
THEORY_PLANNED
CROSS_SECTION_PLANNED
DETECTOR_RESPONSE_PLANNED
SLOW_PLANNED
FAST_PARTIALLY_PLANNED
FAST_PLANNED
STATISTICS_PARTIALLY_PLANNED
STATISTICS_PLANNED
FULL_IMPLEMENTATION_PLANNED
```

---

# Part II: Implementation Manifest

Create:

```text
runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
```

Use the following schema.

```yaml
dataset_id:
experiment_family:
physics_document:

reference_documents: []
machine_readable_attachments: []
optional_reference_code: []

dataset_identity:
  run_period:
  detector_configuration:
  source_configuration:
  target_configuration:
  statistical_data_mode:

observable_contract:
  true_observables: []
  reconstructed_observables: []
  output_axes: []
  output_shape: []
  output_unit:

modules:

  dataset:
    status:
    user_document_sections: []
    supplied_inputs: []
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  source:
    status:
    user_document_sections: []
    supplied_inputs: []
    numerical_tables: []
    physical_contract:
      components: []
      flavors: []
      energy_unit:
      flux_unit:
      energy_support:
      time_support:
      normalization:
      interpolation:
      matching:
      lower_boundary:
      upper_boundary:
      extrapolation:
      nonnegative_required:
      zero_outside_support:
      publication_mode:
      reproduction_mode:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  target:
    status:
    user_document_sections: []
    supplied_inputs: []
    physical_contract:
      detectors: []
      materials: []
      isotopes: []
      exposure_semantics:
      nuclei_per_kg_convention:
      response_keys: []
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  theory_response:
    status:
    user_document_sections: []
    supplied_inputs: []
    physical_contract:
      incoming_flavor:
      outgoing_flavor:
      neutrino_or_antineutrino:
      coefficient_basis:
      coefficient_order: []
      standard_model_point:
      response_keys: []
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  kinematics_cross_section:
    status:
    user_document_sections: []
    supplied_inputs: []
    physical_contract:
      incident_energy_unit:
      recoil_energy_unit:
      cross_section_unit:
      minimum_incident_energy:
      recoil_endpoint:
      baseline_kinematics:
      diagnostic_kinematics:
      out_of_support_behavior:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    implementation_location:
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  detector_response:
    status:
    user_document_sections: []
    supplied_inputs: []
    numerical_tables: []
    physical_contract:
      true_observable:
      reconstructed_observable:
      mean_mapping:
      stochastic_response:
      efficiency:
      efficiency_domain:
      binning:
      migration_rule:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  slow_counts:
    status:
    user_document_sections: []
    supplied_inputs: []
    physical_contract:
      integration_chain:
      integration_order: []
      component_axes: []
      returned_axes: []
      returned_shape: []
      returned_unit:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    reference_outputs: []
    blockers: []

  fast_counts:
    status:
    user_document_sections: []
    supplied_inputs: []
    representations: []

    # Each item in representations must use:
    #
    # - name:
    #   status:
    #   mathematical_basis:
    #   required_slow_state:
    #   coefficient_basis:
    #   storage_file:
    #   storage_shape:
    #   returned_shape:
    #   create_files: []
    #   modify_files: []
    #   must_not_modify: []
    #   public_api: []
    #   tests: []
    #   blockers: []

    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    blockers: []

  statistics:
    status:
    user_document_sections: []
    supplied_inputs: []
    numerical_tables: []
    physical_contract:
      data_mode:
      observed_data:
      background_data:
      covariance:
      nuisance_parameters: []
      test_statistic:
      profiling:
      confidence_construction:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    reference_outputs: []
    blockers: []

  validation_registry:
    status:
    user_document_sections: []
    supplied_inputs: []
    discovery_strategy:
    csi_reference_files: []
    reuse_files: []
    create_files: []
    modify_files: []
    conditional_modify_files: []
    must_not_modify: []
    public_api: []
    tests: []
    regression_scope: []
    blockers: []

global_blockers: []

protected_existing_datasets: []

gate:
  phase: I
  status:
  reasons: []

next_skill:
```

---

# Allowed module status

Every module must have exactly one primary status:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

## REUSE

The current repository already satisfies the required physics and API contract.

The module must identify actual `reuse_files`.

## CONFIG_ONLY

The module requires only configuration or machine-readable data.

Typical outputs:

```text
YAML
CSV
JSON
NPY
NPZ
```

## ADAPTER

The shared implementation is reusable, but an experiment-level adapter is
required.

The module must identify:

```text
adapter file
public API
input units
returned shape
tests
```

## SHARED_EXTENSION

A reusable experiment-family implementation is required.

The module must identify which future or existing datasets can reuse it.

## CORE_EXTENSION

A shared theory, nuclear-response, rates, or kernel implementation must change.

The module must identify:

```text
exact missing capability
exact shared files
backup plan
new unit tests
full regression scope
```

## BLOCKED

An essential input is missing or inconsistent.

The module must identify:

```text
missing input
reason required
affected phase
possible independent work
resolution condition
```

---

# Public API entry format

Every planned public API entry must use:

```yaml
public_api:
  - name:
    location:
    purpose:
    inputs:
      - name:
        type:
        unit:
        shape:
        meaning:
    keyword_arguments: []
    returns:
      type:
      unit:
      shape:
      axes: []
    error_behavior:
```

Do not leave the returned shape unspecified.

For dataset-level count functions, prefer an API based on:

```text
coefficients
experiment_spec
```

Repository-internal database paths should normally be resolved through the
experiment specification or existing project configuration rather than passed
by every external caller.

---

# Test entry format

Every planned test must use:

```yaml
tests:
  - path:
    purpose:
    inputs:
    expected:
    tolerance:
    provenance:
```

Tests must check physical contracts, not only code execution.

Examples include:

```text
source support
source nonnegativity
source normalization
matching continuity
target normalization
response-key availability
kinematic endpoints
detector-response normalization
efficiency range
Slow component sums
Slow convergence
Slow/Fast binwise agreement
statistical benchmark
existing-dataset regression
```

---

# Source boundary and physical-constraint rules

The template must not prescribe a universal low-energy boundary condition.

The manifest must instead record the boundary rule from the experiment
definition.

For every source model, specify:

```text
valid tabulated range
interpolation rule
behavior below first node
behavior above last node
behavior outside physical support
matching points
continuity conditions
nonnegativity requirements
normalization requirements
```

When a documented reproduction rule yields an unphysical result, such as a
negative differential flux, the Phase 0 report must distinguish:

```text
reproduction mode
publication mode
```

The experiment-specific manifest must state which mode is authoritative.

Do not silently clip, extrapolate, or replace values.

---

# Fast representation rules

`fast_counts` may contain multiple independent Fast representations.

Example:

```yaml
fast_counts:
  status: ADAPTER

  representations:
    - name: cumulative_fast
      status: ADAPTER
      mathematical_basis: cumulative integral of the validated reconstructed spectrum
      required_slow_state: SLOW_VALIDATED
      coefficient_basis:
      storage_file:
      storage_shape:
      returned_shape:
        - reconstructed_energy_bin
      create_files: []
      modify_files: []
      must_not_modify: []
      public_api: []
      tests: []
      blockers: []

    - name: eft_quadratic_kernel
      status: BLOCKED
      mathematical_basis: quadratic Wilson-coefficient kernel
      required_slow_state: SLOW_VALIDATED
      coefficient_basis:
      storage_file:
      storage_shape:
      returned_shape:
        - reconstructed_energy_bin
      create_files: []
      modify_files: []
      must_not_modify: []
      public_api: []
      tests: []
      blockers:
        - missing complete coefficient-basis mapping
```

A blocked EFT kernel must not block an otherwise implementable cumulative Fast
representation.

---

# File-plan rules

## create_files

Files that do not currently exist and are approved for later creation.

## modify_files

Existing files that later phases are expected to modify.

## conditional_modify_files

Existing files modified only if a stated condition is met.

Use:

```yaml
conditional_modify_files:
  - path:
    condition:
    required_tests: []
```

Do not put `registry.py` under unconditional `modify_files` merely because a
new dataset is being added.

## must_not_modify

Existing files protected from changes during the module.

Existing experiment implementations and reference arrays should normally be
protected unless a genuine shared-core extension is approved.

---

# Data-materialization rules

Use:

```text
scalar parameters
→ experiment.yaml

regular binning
→ experiment.yaml

small irregular numerical tables
→ CSV or JSON

large arrays and matrices
→ NPY or NPZ

single-isotope target
→ experiment.yaml

multi-isotope or detector-dependent inventory
→ YAML or CSV as appropriate

experiment-specific formulas not expressible by shared code
→ thin Python adapter
```

Do not create a separate data file when a small regular definition can be
represented clearly and losslessly in `experiment.yaml`.

---

# Manifest consistency checks

The completed manifest must satisfy:

1. Every module has exactly one primary status.
2. Every `REUSE` module identifies verified repository files.
3. Every `CONFIG_ONLY` module identifies concrete configuration or data fields.
4. Every `ADAPTER` module identifies a concrete implementation location.
5. Every planned callable specifies units and returned shape.
6. Every `CORE_EXTENSION` identifies exact shared files and regression scope.
7. Every `BLOCKED` module contains an explicit blocker.
8. `create_files` and `reuse_files` do not contain the same path.
9. `modify_files` and `must_not_modify` do not contain the same path.
10. Conditional changes are not listed as unconditional modifications.
11. Values already present in the user document are not listed as missing.
12. Repository paths are based on actual inspection.
13. Fast representations are separated when they have different mathematical
    bases or blockers.
14. Source boundary rules are explicit.
15. Statistical data mode is explicit.
16. Production code and production data are not created during Phase 0.
17. `next_skill` names exactly one Skill.

---

# Gate I

Gate I passes only when:

```text
dataset identities are unique
input documents are inventoried
supplied numerical data are recorded
observable axes and returned shape are defined
statistical data mode is defined
every module is classified
repository reuse has been verified
planned files are concrete
planned APIs are concrete
tests are concrete
blockers are explicit
protected files are explicit
no production code has been modified
no production data have been created
```

Use:

```yaml
gate:
  phase: I
  status: PASS
  reasons:
    - all required Phase 0 planning fields are complete
```

or:

```yaml
gate:
  phase: I
  status: BLOCKED
  reasons:
    - describe the missing Phase 0 planning information
```

A blocker affecting a later implementation phase does not automatically require
Gate I to be `BLOCKED`, provided that the blocker and resolution condition are
fully recorded.

---

# Phase 0 prohibition

During Phase 0 do not create or modify:

```text
production Python modules
final experiment.yaml
production CSV files
production NPY or NPZ files
registry.py
theory modules
nuclear-response modules
rate modules
kernel modules
Slow implementations
Fast implementations
statistics implementations
reference arrays
```

The only normal Phase 0 outputs are:

```text
runs/<dataset_id>/00_INPUT_INVENTORY.md
runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
```

Stop after Gate I.