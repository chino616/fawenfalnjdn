# Phase 8 Fast Counts

## 1. Purpose

Construct one or more accelerated representations from a validated Slow
prediction.

Fast is never authoritative.

For every supported parameter point:

```text
Fast prediction
≈ validated Slow prediction
```

Slow must never be changed to match Fast.

---

## 2. Inputs

```text
dataset_id:
experiment_spec:
Slow callable:
Slow reference:
required Fast representations:
```

Required state:

```text
Gate L = PASS
```

---

## 3. Reference Code

Inspect the actual Fast wrappers and common kernel modules listed in
`CSI_REFERENCE_MAP.md`.

| Role | File | Symbol |
|---|---|---|
| Fast dataset wrapper | | |
| Basis definition | | |
| Kernel builder | | |
| Reconstruction | | |
| Storage | | |
| Existing Fast tests | | |

Record the verified call chain:

```text
coefficients or model parameters
→ Fast representation
→ reconstructed bin counts
```

Copy only relevant signatures or short fragments.

```python
# Reference file:
# Reference symbol:

```

Do not copy an entire CsI or Ar Fast module.

---

## 4. Representation Plan

Treat every Fast representation independently.

| Representation | Required for release | Status | Parameter dependence | Blocker |
|---|---|---|---|---|
| cumulative spectrum | | | | |
| EFT quadratic kernel | | | | |
| response matrix | | | | |
| source cache | | | | |
| other | | | | |

Allowed statuses:

```text
REUSE
ADAPTER
IMPLEMENTED
DEFERRED
BLOCKED
NOT_APPLICABLE
```

Do not create a representation whose basis or parameter dependence is not
fully defined.

---

## 5. Cumulative-Spectrum Fast

Use when acceleration concerns repeated bin integration of a fixed
reconstructed spectrum.

Record:

```text
input spectrum:
sampling grid:
interpolation rule:
cumulative integration rule:
bin reconstruction:
parameter dependence:
```

Typical outputs:

```text
fast_cumulative_<dataset_id>.py
cumulative_reference.npz
```

The cumulative representation does not replace coefficient-dependent Slow
physics unless that dependence is explicitly included in its construction.

---

## 6. EFT Kernel Fast

Use only when the event prediction has a documented polynomial dependence on
the selected Wilson-coefficient basis.

Record:

```text
coefficient basis:
coefficient order:
real or complex convention:
linear terms:
quadratic terms:
interference convention:
kernel shape:
bin axis:
Hermiticity requirement:
```

Do not generate a formal kernel when the complete basis order is unknown.

Do not infer missing basis groups from partial formulas.

Typical outputs:

```text
fast_kernel_<dataset_id>.py
kernel_<dataset_id>.npz
```

---

## 7. Public API

Follow the repository Fast API.

A wrapper may expose a contract equivalent to:

```python
def fast_counts(
    coefficients,
    experiment_spec,
    *,
    representation="cumulative",
):
    ...
```

Record:

```text
representation labels:
coefficient input:
return axes:
return shape:
return unit:
unsupported-input behavior:
```

Every Fast output must match the Slow output contract.

---

## 8. Validation Points

Use multiple documented points:

```text
Standard Model or zero-BSM point
single-coefficient points
interference-sensitive points
complex-coefficient points when supported
random bounded points
```

For each point and bin save:

```text
Slow
Fast
absolute difference
relative difference
tolerance
pass or fail
```

Create:

```text
runs/<dataset_id>/artifacts/fast_vs_slow.csv
runs/<dataset_id>/artifacts/fast_runtime.csv
runs/<dataset_id>/figures/fast_vs_slow.png
runs/<dataset_id>/figures/fast_relative_error.png
```

Do not validate only total event counts.

---

## 9. Tests

Required for every implemented representation:

```text
output shape
output unit
finite values
bin-by-bin Slow agreement
component agreement when exposed
parameter-point coverage
serialization round trip
stale-artifact metadata rejection
unsupported inputs raise errors
```

For EFT kernels also test:

```text
basis order
Hermiticity
linear terms
quadratic terms
interference
real and complex conventions
```

For cumulative Fast also test:

```text
grid refinement
interpolation order
cumulative monotonicity where applicable
bin-edge reconstruction
```

---

## 10. Files

### Create

```text
src/cevns_pyeft/experiments/<family>/fast_<method>_<dataset_id>.py
tests/test_<dataset_id>_fast_<method>.py
runs/<dataset_id>/08_FAST_COUNTS.md
runs/<dataset_id>/artifacts/*
runs/<dataset_id>/figures/*
```

Optional validated arrays:

```text
data or test reference *.npz
```

### Modify

Update `experiment.yaml` only for representations that pass validation.

### Must not modify

```text
Slow implementation
Slow reference arrays
source physics
cross-section physics
Detector Response
statistics
existing Fast references
```

---

## 11. Gate F

Evaluate each representation separately.

```text
representation:
status:
validation result:
blocker:
```

Overall Gate F passes when every representation marked
`required_for_release = yes` passes.

A deferred or optional representation may remain blocked without failing the
overall gate, provided it is not advertised as implemented.

```text
overall status: PASS / BLOCKED
validated representations:
blocked representations:
reasons:
next_skill:
```

Stop after Gate F.