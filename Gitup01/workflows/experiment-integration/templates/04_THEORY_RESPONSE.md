# Phase 4 Theory and Nuclear Response

## 1. Inputs

```text
dataset_id:
input_inventory:
implementation_manifest:
experiment_spec:
target_response_key:
theory_status:
response_status:
```

Required previous state:

```text
Gate I = PASS
Gate D0 = PASS
Gate S0 = PASS
target ready
```

This phase validates the shared theory and nuclear-response implementation.

A `REUSE` result may still generate diagnostic tables and figures.

Do not create experiment-specific amplitude or nuclear-response code unless the
approved manifest requires an adapter or core extension.

---

## 2. Approved Theory Contract

```text
incoming flavor:
neutrino or antineutrino:
outgoing flavor treatment:
theory baseline:
Wilson basis:
coefficient order:
complex coefficients supported:
target isotope:
Response key:
new Lorentz structure:
new propagator structure:
```

Expected classification:

```text
REUSE
ADAPTER
CORE_EXTENSION
BLOCKED
```

---

## 3. Reference Code

Inspect the actual repository implementation.

| Role | File | Symbol |
|---|---|---|
| Response loader | | |
| Response object | | |
| Response evaluator | | |
| Theory response contraction | | |
| Amplitude entry point | | |
| Existing tests | | |

Required reference path:

```text
Response data
→ Response loader
→ target Response object
→ theory response contraction
→ amplitude squared
```

Copy only relevant signatures or short fragments:

```python
# Reference file:
# Reference symbol:

```

Record the verified contract:

```text
Response input variable:
Response basis labels:
Response channel labels:
amplitude input arguments:
energy units:
recoil units:
return type:
return shape:
```

Do not copy a complete CsI, Ar, theory, or Response module.

---

## 4. Nuclear-Response Diagnostics

Load the approved target Response and evaluate it over a documented physical
momentum-transfer grid.

### Grid definition

```text
recoil grid:
recoil unit:
target mass:
q definition:
q unit:
dimensionless response variable:
grid size:
```

Use the same momentum-transfer and dimensionless-variable conventions as the
shared Response implementation.

### Response output

Create one of:

```text
runs/<dataset_id>/artifacts/nuclear_response_grid.csv
runs/<dataset_id>/artifacts/nuclear_response_grid.npz
```

For CSV, preferred columns are:

```text
target
recoil_keV
q_MeV
response_variable
channel
basis_i
basis_j
value
```

Use the actual basis labels exposed by the repository.

Do not rename an isospin or proton-neutron basis without an explicit
conversion.

### Response figures

Generate:

```text
runs/<dataset_id>/figures/nuclear_response_channels.png
runs/<dataset_id>/figures/nuclear_response_channels.pdf
```

The figure must show:

```text
raw response values versus q or recoil
channel labels
basis labels
physical grid range
target isotope
```

An optional normalized-shape figure may show:

```text
W(q) / W(0)
```

only when `W(0)` is finite and nonzero.

Do not replace the raw-response figure with independently normalized curves.

Individual interference responses may be negative. Require nonnegativity only
where the current Response contract physically requires it.

---

## 5. Theory Benchmarks

Evaluate the shared theory path at documented benchmark points.

Create:

```text
runs/<dataset_id>/artifacts/theory_response_benchmarks.csv
```

Preferred columns:

```text
benchmark
target
E_nu_MeV
recoil_keV
coefficient_point
amplitude_squared
finite
nonnegative
```

Required benchmarks:

```text
Standard Model or zero-BSM point
one additional approved Wilson-coefficient point when available
one point near the lower physical recoil range
one point near the upper physical recoil range
```

The total amplitude squared must be finite and nonnegative.

Do not require every individual response or interference contribution to be
nonnegative.

---

## 6. Implementation Decision

```text
theory classification:
Response classification:
reason:
shared files reused:
new code required:
```

For `REUSE`:

```text
new theory code: no
new Response code: no
diagnostic artifacts: yes
```

For `ADAPTER`, create only the minimum approved parameter or basis wrapper.

For `CORE_EXTENSION`, back up shared files and run all affected theory,
Response, CsI, Ar, Slow, and Fast regressions.

---

## 7. Files

### Reused

```text
```

### Created

Normally:

```text
runs/<dataset_id>/artifacts/nuclear_response_grid.csv
runs/<dataset_id>/artifacts/theory_response_benchmarks.csv
runs/<dataset_id>/figures/nuclear_response_channels.png
runs/<dataset_id>/figures/nuclear_response_channels.pdf
runs/<dataset_id>/04_THEORY_RESPONSE.md
```

### Modified

For `REUSE`:

```text
none
```

### Must not modify for REUSE

```text
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
shared theory files
existing experiment implementations
existing reference arrays
```

Diagnostic files belong under the workflow run directory and must not be
imported by runtime code.

---

## 8. Tests

Required checks:

```text
Response key exists
target metadata match A, Z, and N
expected channels are available
Response grid is finite
basis labels and order are preserved
shared amplitude callable loads
neutrino or antineutrino routing is correct
Wilson coefficient order is preserved
total amplitude squared is finite and nonnegative
scalar and array behavior match the verified API
diagnostic figures are reproducible from the saved grid
```

Do not change shared Response data because a diagnostic curve looks
unexpected. Investigate conventions first.

---

## 9. Gate T1

Gate T1 passes when:

```text
the shared theory covers the approved interaction
the approved target Response loads
Response diagnostics are generated
the response basis and channel order are documented
the shared amplitude path passes benchmark tests
no unnecessary experiment-specific theory or Response code was created
```

```text
status: PASS / BLOCKED
reasons:
next_skill:
```

Stop after Gate T1.