# Phase 3 Source

## 1. Inputs

```text
dataset_id:
input_inventory:
implementation_manifest:
experiment_spec:
source_status:
```

Required previous state:

```text
Gate I = PASS
Gate D0 = PASS
target ready
```

Use the approved Phase 0 source definition. Do not re-extract the complete
physics document.

---

## 2. Approved Source Definition

```text
source_type:
components:
flavors:
energy_unit:
flux_unit:
energy_support:
time_support:
normalization:
interpolation:
matching:
lower_boundary:
upper_boundary:
zero_outside_support:
nonnegative_required:
```

Numerical tables:

| Table | Source | Shape | Units | Output file |
|---|---|---:|---|---|
| | | | | |

---

## 3. Reference Code

Inspect only the source-related files listed in `CSI_REFERENCE_MAP.md`.

### Reference files

| Role | File | Symbol |
|---|---|---|
| Source caller | | |
| Flux implementation | | |
| Data loader | | |
| Component routing | | |
| Source tests | | |

### Actual call chain

```text
<experiment wrapper>
→ <source callable>
→ <data loader or source helper>
→ <returned differential flux>
```

### Relevant reference signatures

Copy only the relevant signatures or short source fragments.

```python
# Reference file:
# Reference symbol:

```

```python
# Reference file:
# Reference symbol:

```

Record the verified contract:

```text
input arguments:
input units:
scalar behavior:
array behavior:
component labels:
return type:
return shape:
return unit:
out-of-support behavior:
```

Do not copy an entire CsI or SNS module.

---

## 4. Implementation Decision

Select one:

```text
REUSE
CONFIG_ONLY
ADAPTER
SHARED_EXTENSION
CORE_EXTENSION
BLOCKED
```

```text
decision:
reason:
reused API:
new logic required:
```

Typical reasons for an adapter:

```text
piecewise spectrum
matching between spectra
normalization integral
special boundary behavior
component routing
time dependence
```

---

## 5. Production Files

### Reuse

```text
```

### Create

```text
data/experiments/<dataset_id>/<source_table>.csv
src/cevns_pyeft/experiments/<family>/source.py
tests/test_<dataset_id>_source.py
runs/<dataset_id>/03_SOURCE.md
```

Remove files that are not required by the approved manifest.

### Modify

```text
data/experiments/<dataset_id>/experiment.yaml
```

### Must not modify

```text
existing CsI or SNS source implementations
existing experiment source data
theory modules
nuclear-response modules
rates modules
Slow modules
Fast modules
statistics modules
registry.py
```

---

## 6. New Source Code

Follow the verified repository API.

### Planned call chain

```text
experiment.yaml
→ source callable
→ source tables
→ differential flux
```

### Planned functions

| Function | Purpose | Reference symbol |
|---|---|---|
| | load source data | |
| | construct raw spectrum | |
| | return normalized differential flux | |

### Code skeleton

Use actual repository names after inspecting the reference implementation.

```python
def load_source_data(experiment_spec):
    """Load validated source tables and metadata."""
    ...


def raw_spectrum(energy, experiment_spec, *, component="total"):
    """Return the unnormalized source spectrum."""
    ...


def differential_flux(energy, experiment_spec, *, component="total"):
    """Return the differential flux in the declared source unit."""
    ...
```

Required public contract:

```text
energy input unit:
component argument:
return type:
return shape:
return unit:
scalar behavior:
array behavior:
outside-support behavior:
error behavior:
```

Do not retain these provisional function names when the repository already has
a different established naming convention.

---

## 7. Experiment-Spec Update

After Source tests pass, update `experiment.yaml` with:

```text
source status:
source callable:
source data files:
components:
flavors:
energy support:
flux unit:
normalization rule:
boundary rule:
```

Do not mark the Source as implemented before validation passes.

---

## 8. Tests

Required tests:

```text
numerical table nodes
coefficient table values
energy support
lower boundary
upper boundary
zero outside support
finite outputs
nonnegative flux when required
matching continuity
integrated normalization
component sum
scalar input
array input
invalid component
missing source data
```

Test file:

```text
tests/test_<dataset_id>_source.py
```

Reference implementation used by tests:

```text
file:
symbol:
```

---

## 9. Numerical Results

```text
matching_factor:
normalization_integral:
integrated_flux:
minimum_flux:
maximum_flux:
matching_left:
matching_right:
continuity_residual:
component_sum_residual:
```

Diagnostics must be recomputed from the implemented source definition.

---

## Source Spectrum Figures

Generate:

```text
runs/<dataset_id>/artifacts/source_spectrum_grid.csv
runs/<dataset_id>/figures/source_flux_full.pdf
runs/<dataset_id>/figures/source_flux_full.png
runs/<dataset_id>/figures/source_flux_low_energy.pdf
runs/<dataset_id>/figures/source_flux_low_energy.png
runs/<dataset_id>/figures/source_flux_reference_comparison.pdf
runs/<dataset_id>/figures/source_flux_reference_comparison.png
```

The full-spectrum figure must show:

```text
final differential flux
low-energy source component
high-energy source component
matching point
physical support
```

The low-energy figure must show:

```text
all low-energy table nodes
interpolation
lower boundary
matching behavior near the transition energy
```

The reference-comparison figure must state:

```text
reference paper:
reference figure:
reference fission fractions:
reference normalization:
comparison normalization:
direct numerical data or digitized figure:
```

For digitized literature curves:

```text
use for validation only
do not use as production source input
```

Required plot checks:

```text
finite spectrum
nonnegative spectrum
zero outside support
continuous matching
correct integrated normalization
reproducible from source_spectrum_grid.csv
```


## 10. Gate S0

Gate S0 passes when:

```text
source tables match the approved inputs
reference API was inspected
the new callable follows the repository contract
units and returned shape are explicit
boundary behavior passes
matching passes
normalization passes
physical constraints pass
scalar and array tests pass
experiment.yaml loads the validated Source
```

```text
status: PASS / BLOCKED
reasons:
next_skill:
```

Stop after Gate S0.