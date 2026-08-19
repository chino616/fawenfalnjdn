# Phase 5 Kinematics and Differential Cross Section

## 1. Inputs

```text
dataset_id:
input_inventory:
implementation_manifest:
experiment_spec:
source_report:
theory_response_report:
target:
target_mass:
Response key:
```

Required previous state:

```text
Gate S0 = PASS
Gate T1 = PASS
```

This phase validates kinematics and exposes the approved differential
cross-section models.

---

## 2. Reference Code

Inspect the actual repository implementation.

| Role | File | Symbol |
|---|---|---|
| Shared differential cross section | | |
| Shared amplitude or Response model | | |
| Helm form factor | | |
| Kinematic endpoint helper | | |
| Physical-support mask | | |
| Existing tests | | |

Required call path:

```text
E_nu and recoil
→ kinematic support
→ selected nuclear model
→ differential cross section
```

Copy only relevant signatures or short fragments:

```python
# Reference file:
# Reference symbol:

```

Record:

```text
energy input units:
recoil input units:
cross-section output unit:
scalar behavior:
array behavior:
broadcasting:
out-of-support behavior:
```

Do not infer the API from filenames alone.

---

## 3. Cross-Section Model Selection

Support the following explicit model labels.

### `full_response`

Use:

```text
shared Li2026 theory
approved Wilson coefficients
target Response object
all required nuclear-response channels
```

This is the default model for general EFT calculations.

### `helm_sm`

Use:

```text
Standard Model weak charge
Helm weak form factor
shared kinematic convention
```

This is primarily a Standard Model validation and comparison model.

Do not apply arbitrary EFT Wilson coefficients to `helm_sm` unless an explicit
and validated coefficient-to-weak-charge mapping exists.

### Optional `helm_vector`

Allow only when the approved physics definition provides an explicit vector
charge mapping.

Do not silently approximate scalar, axial, tensor, pseudoscalar, or
interference responses with a Helm form factor.

Record:

```text
default model:
available models:
Helm allowed coefficient space:
unsupported combinations:
```

---

## 4. Helm Convention

Record the exact implemented convention:

```text
weak charge definition:
proton contribution:
neutron contribution:
nuclear radius convention:
effective radius:
skin thickness:
spherical Bessel convention:
proton and neutron form factors:
normalization F(0):
```

The usual Helm structure may be represented as:

```text
F_H(q) = 3 j1(q R0) / (q R0) * exp[-(q s)^2 / 2]
```

but the implementation must follow the verified repository convention.

Define the `q → 0` limit analytically or numerically stably:

```text
F_H(0) = 1
```

Do not mix charge-radius, matter-radius, and weak-radius conventions.

Helm belongs to the cross-section or form-factor layer, not to the nuclear
Response database.

---

## 5. Kinematics

Record:

```text
true recoil variable:
recoil unit:
neutrino-energy unit:
target-mass unit:
exact E_nu_min:
reproduction E_nu_min:
selected default:
recoil endpoint:
integration support:
```

If an experiment uses a named approximation, implement it as an explicit model
choice.

Example labels:

```text
exact
heavy_nucleus_approximation
publication_reproduction
```

Do not replace the shared exact formula globally.

Required behavior:

```text
outside physical support → zero cross section
invalid negative energy → explicit error or documented zero
endpoint convention → documented
```

---

## 6. Public API

Prefer the current repository-native cross-section API.

When a selector adapter is required, use a contract equivalent to:

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

These names are provisional until the real repository API is inspected.

Record:

```text
callable:
implementation file:
model labels:
kinematic labels:
input units:
return unit:
return shape:
broadcasting:
error behavior:
```

If the shared rates layer already supports model selection, do not create a new
cross-section module.

If a thin adapter is required, it must call shared implementations rather than
duplicate the full theory formulas.

---

## 7. Production Decision

```text
kinematics classification:
cross-section classification:
full-response implementation:
Helm implementation:
new adapter required:
reason:
```

Possible outputs:

```text
src/cevns_pyeft/experiments/<family>/kinematics.py
src/cevns_pyeft/experiments/<family>/cross_section.py
```

Create `cross_section.py` only when the existing shared API cannot expose the
approved model selector.

Do not create:

```text
experiment-specific amplitude.py
experiment-specific nuclear_response.py
a duplicate Li2026 cross section
```

---

## 8. Cross-Section Diagnostics

Create:

```text
runs/<dataset_id>/artifacts/kinematic_endpoints.csv
runs/<dataset_id>/artifacts/cross_section_grid.csv
```

Preferred cross-section-grid columns:

```text
E_nu_MeV
recoil_keV
model
kinematics
allowed
dsigma_dT_cm2_per_keV
```

Use several documented neutrino energies spanning the physical source support.

Generate:

```text
runs/<dataset_id>/figures/cross_section_vs_recoil.png
runs/<dataset_id>/figures/cross_section_vs_recoil.pdf
runs/<dataset_id>/figures/full_response_vs_helm.png
runs/<dataset_id>/figures/full_response_vs_helm.pdf
```

The comparison figure must show:

```text
full_response Standard Model result
helm_sm result
same target
same kinematics
same units
same weak-input constants
```

Optional ratio:

```text
full_response / helm_sm
```

Plot the ratio only where the denominator is finite and nonzero.

Do not normalize the two cross sections independently before comparing them.

---

## 9. Tests

### Kinematic tests

```text
exact endpoint relation
selected approximation
recoil endpoint
physical-support mask
zero outside support
scalar and array behavior
unit conversions
exact-versus-approximation difference
```

### Full-response tests

```text
approved Response key
Standard Model benchmark
one approved EFT benchmark
finite total cross section
nonnegative total cross section
correct output unit
```

### Helm tests

```text
F_H(0) = 1
finite form factor
stable q → 0 behavior
zero or finite behavior outside the selected numerical range
finite nonnegative Standard Model cross section
correct weak-charge convention
```

### Model-comparison tests

```text
same target mass
same source energy
same recoil
same kinematic convention
same constants
saved grid reproduces the figures
```

Require nonnegativity only for the total physical differential cross section,
not for separately reported interference contributions.

---

## 10. Files

### Created

```text
runs/<dataset_id>/artifacts/kinematic_endpoints.csv
runs/<dataset_id>/artifacts/cross_section_grid.csv
runs/<dataset_id>/figures/cross_section_vs_recoil.png
runs/<dataset_id>/figures/cross_section_vs_recoil.pdf
runs/<dataset_id>/figures/full_response_vs_helm.png
runs/<dataset_id>/figures/full_response_vs_helm.pdf
runs/<dataset_id>/05_KINEMATICS_CROSS_SECTION.md
```

Optional approved code:

```text
src/cevns_pyeft/experiments/<family>/kinematics.py
src/cevns_pyeft/experiments/<family>/cross_section.py
tests/test_<dataset_id>_cross_section.py
```

### Must not modify without CORE_EXTENSION approval

```text
shared Li2026 theory
shared nuclear Response database
existing experiment cross sections
existing reference arrays
```

---

## 11. Gate X

Gate X passes when:

```text
the selected kinematic convention is explicit
the full-response model passes its benchmarks
the Helm convention is explicit and tested
unsupported Helm coefficient combinations raise an error
physical masks and endpoints pass
units and array behavior pass
cross-section grids and figures are generated
full-response and Helm comparisons use identical external inputs
```

```text
status: PASS / BLOCKED
reasons:
default_cross_section_model:
available_cross_section_models:
next_skill:
```

Stop after Gate X.