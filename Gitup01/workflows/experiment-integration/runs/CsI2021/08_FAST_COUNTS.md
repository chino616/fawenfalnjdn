# Phase 8 Fast Counts: CsI2021

## 1. Status

P4 status: FAST_REFERENCE_PROMOTED

The Flavor Fast path now has the required operator-basis and storage contract
for CsI2021: 22 LEFT basis elements, Wilson coefficient tensor shape
`(22,3,3)`, `row=final,column=initial` metadata, and reconstruction through
`Tr(rho C_I^dagger C_J)`.  Legacy `tests/reference_fast_split/csi2021_*` files
remain stale diagnostics only and are rejected as authoritative Flavor Fast
kernels because they lack `flavor_schema_version`.

The CsI2021 Fast detector fold now matches the Slow PE interpolation contract
by carrying `pe_step=3.0` through the builder/storage path.  This removes the
previous lightweight Fast/Slow mismatch caused by direct sub-bin smearing in
Fast versus PE-grid interpolation in Slow.

The Fast continuum threshold now uses the same P0 exact kinematics helper as
Slow, `minimum_neutrino_energy_GeV`, instead of the legacy heavy-nucleus
approximation.  This keeps the delayed continuum on the same support in Slow
and Fast without changing antineutrino kernel physics.

This is now `fast_validated: true`: the full-resolution Flavor Fast reference
has been promoted into experiment metadata, and the production Fast kernel is
declared authoritative for CsI2021.

## 2. Path Inspected

| Role | File | Symbol |
|---|---|---|
| Fast basis | `src/cevns_pyeft/kernels/basis.py` | `li2026_left_basis`, `coeff_tensor_from_triplets` |
| Fast reconstruction | `src/cevns_pyeft/kernels/reconstruction.py` | `coefficient_bilinear`, `reconstruct_counts_from_kernel` |
| Fast storage | `src/cevns_pyeft/kernels/storage.py` | `save_fastscan_template`, `load_fastscan_template` |
| CsI2021 builder | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py` | `build_fast_kernel_csi2021` |
| Detector fold | `src/cevns_pyeft/kernels/builder.py` | `build_matrixized_kernel` |
| Slow reference | `tests/reference_CsI2021/slow_reference.npy` | authoritative Gate L Slow counts |

## 3. Frozen P4 Contract

```text
operator basis size = 22
Wilson coefficient tensor = (22,3,3)
Wilson flavor axes = row final, column initial
coefficient bilinear = B_IJ = Tr(rho C_I^dagger C_J)
storage schema = flavor_schema_version: 1
lnc_lnv_interference = false
detector fold contract = Slow PE interpolation grid
pe_step = 3.0
stale Fast metadata without flavor_schema_version = reject / diagnostic-only
```

## 4. Lightweight Slow/Fast Check

The current lightweight saved-kernel check builds a CsI2021 Fast template with
`n_er=3`, `n_enu=6`, `n_pe_sub=3`, `pe_step=3.0`, saves it, reloads it through
the schema validator, reconstructs the SM counts using the Flavor Wilson tensor
path, and compares the result to the direct Slow counts with the same
lightweight source/detector grid.

```text
Slow total = 100.55493552434457
Fast reconstructed total = 100.55493548246244
max absolute bin delta = 1.6333295604908926e-08
```

This check validates the P4 math/storage/reconstruction contract on the CsI2021
path.  It does not replace the Gate L Slow reference and does not validate a
full production Fast reference.

Full-resolution promotion against the Gate L Slow reference gives:

```text
python tools/experiment_integration/generate_csi_fast_references.py --dataset all --write-reference-kernels --acknowledge-reference-update "I approve updating CsI Fast reference kernels"
status = REFERENCE_WRITTEN
kernel_shape = (3,3,8,22,22,9)
Slow total = 332.9338350257275
Fast reconstructed total = 332.9338348870574
total delta = -1.3867010340007369e-07
max absolute bin delta = 3.1649634024688567e-08
worst-bin tolerance ratio under rtol=1e-9, atol=2e-8 = 0.3297257793673648
fast_slow_allclose = true
```

Authoritative Fast reference:

```text
tests/reference_CsI2021/fast_kernel.npz
tests/reference_CsI2021/fast_kernel.json
```

The guarded Fast reference generator also performs this comparison before any
reference promotion.  A production Fast kernel cannot be prepared or written
unless the full Fast prediction matches the Gate L Slow reference under
`rtol=1e-9, atol=2e-8`.

## 5. Tests

Executed:

```text
python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp tests/test_fast_flavor_tensor.py
17 passed

python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp tests/test_fast_flavor_tensor.py tests/test_csi_slow_counts_phase7.py::test_csi_gate_l_yaml_matches_authoritative_slow_reference_availability tests/test_csi_slow_source_state_p3.py::test_csi_phase6_connects_validated_detector_response_and_preserves_later_boundaries
19 passed

python -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp -k "not conus"
205 passed, 1 skipped, 33 deselected
```

Coverage added in `tests/test_fast_flavor_tensor.py`:

- `(22,3,3)` Flavor Wilson tensor basis construction;
- `Tr(rho C_I^dagger C_J)` bilinear orientation;
- Flavor pair-template reconstruction agrees with full-kernel reconstruction;
- saved Fast templates preserve `flavor_schema_version=1` metadata;
- stale saved metadata is rejected with `StaleKernelError`;
- lightweight CsI2021 saved Fast kernel reproduces direct Slow counts using the
  same PE interpolation grid contract.
- authoritative Fast reference generation is guarded and non-writing by default;
- `experiment.yaml` cannot mark `fast_validated: true` unless authoritative
  Fast kernel files and Flavor schema metadata exist;
- full-resolution authoritative Fast reference reproducibility passes against
  `tests/reference_CsI2021/fast_kernel.npz` with matching metadata.
- the guarded Fast generator records strict Fast/Slow alignment metadata and
  rejects reference promotion if the Gate L Slow reference comparison fails.
- the guarded Fast generator rejects `--write-reference-kernels` unless the
  exact Fast acknowledgement phrase is supplied, and preserves existing files
  on rejection.
- `--no-compute` remains non-writing even when the write flag and exact Fast
  acknowledgement are both supplied.

## 6. Remaining Blockers

No CsI2021 Fast-counts blocker remains for P4. The stale
`tests/reference_fast_split/csi2021_*` files remain diagnostic-only and are not
the authoritative Flavor Fast reference.
