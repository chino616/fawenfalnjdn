# CsI2021 Phase 3 Source Report

## Inputs and Approved Source

```text
dataset_id: CsI2021
source_status: SHARED_EXTENSION
Gate I: PASS
Gate D0: PASS
Gate T0: PASS
source_type: time-integrated stopped-pion SNS
components: [mu, e, mub]
flavors: [mu, e, mu]
particle_kinds: [nu, nu, antinu]
energy_unit: MeV
continuum_flux_unit: cm^-2 MeV^-1
prompt_flux_unit: cm^-2
tabulation_energy_support: [0.001, 300.0] MeV
physical_node_mask: [0.001, 56.0] MeV
time_support: time integrated through N_POT
normalization: r*N_POT/(4*pi*L_cm^2) once per component
interpolation: existing 200-node linear interpolation
matching: prompt mu line remains separate from delayed continua
lower_boundary: zero below first tabulation node
upper_boundary: zero beyond final tabulation node
boundary_note: preserve reproduction-mode taper in final physical-mask cell
nonnegative_required: yes
```

No new runtime source table was approved or created. The existing analytic
Michel formulas and SNS dataset parameters remain authoritative for P3
reproduction.

## Reference API and Call Chain

| Role | File | Symbol |
|---|---|---|
| Flux implementation | `src/cevns_pyeft/experiments/coherent/sns.py` | `loadNeutrinoEmpiricalFluxSNS` |
| Dataset parameters | `src/cevns_pyeft/experiments/coherent/sns.py` | `SNS_DATASETS` |
| Component routing | `src/cevns_pyeft/experiments/coherent/sns.py` | `sns_component_state` |
| Canonical state | `src/cevns_pyeft/sources/state.py` | `NeutrinoState`, `pure_flavor_state` |
| Source tests | `tests/test_csi_slow_source_state_p3.py` | `test_sns_*` |

```text
loadNeutrinoEmpiricalFluxSNS("CsI2021")
→ SNS_DATASETS["CsI2021"]
→ analytic delayed spectra plus prompt line
→ measured/natural callable dictionaries

sns_component_state(component)
→ pure_flavor_state(flavor, particle_kind=...)
→ immutable NeutrinoState
```

Verified contract:

```text
flux energy unit: MeV for measured callables; GeV for natural callables
scalar behavior: Python float
array behavior: ndarray with input energy shape
component labels: delayed e, delayed mub, continuous total, separate prompt mu
state input: one of mu, e, mub
state output: immutable constant (3,3) density plus particle_kind
out-of-tabulation behavior: zero
error behavior: reject unknown dataset and unknown/aggregate state component
```

## Implementation Decision

```text
decision: SHARED_EXTENSION
reason: CsI2017 and CsI2021 share one SNS component-to-state mapping
reused API: loadNeutrinoEmpiricalFluxSNS and NeutrinoState
new logic: sns_component_state(component)
```

Implemented routing:

```text
mu  -> NeutrinoState("nu", rho_mu)
e   -> NeutrinoState("nu", rho_e)
mub -> NeutrinoState("antinu", rho_mu)
```

## Files

Created:

```text
workflows/experiment-integration/runs/CsI2021/artifacts/source_spectrum_grid.csv
workflows/experiment-integration/runs/CsI2021/figures/source_flux_full.png
workflows/experiment-integration/runs/CsI2021/figures/source_flux_full.pdf
workflows/experiment-integration/runs/CsI2021/figures/source_flux_low_energy.png
workflows/experiment-integration/runs/CsI2021/figures/source_flux_low_energy.pdf
workflows/experiment-integration/runs/CsI2021/03_SOURCE.md
```

Shared backups are recorded in `backup/BACKUP_MANIFEST.md`.

Modified:

```text
src/cevns_pyeft/experiments/coherent/sns.py
tests/test_csi_slow_source_state_p3.py
data/experiments/CsI2017/experiment.yaml
data/experiments/CsI2021/experiment.yaml
```

Protected:

```text
src/cevns_pyeft/rates/counts.py
src/cevns_pyeft/rates/differential.py
all Slow, target, theory, nuclear-response, detector-response, Fast,
statistics, registry, reference_fast_split and CONUS files
```

No literature comparison figure was created because no authoritative comparison
curve was supplied or approved.

## Experiment-Spec Update

After focused Source tests passed, both specs were connected to:

```text
state callable: cevns_pyeft.experiments.coherent.sns.sns_component_state
flux callable: cevns_pyeft.experiments.coherent.sns.loadNeutrinoEmpiricalFluxSNS
spec_status: source_validated_slow_pending
target_validated: true
source_validated: true
slow_validated: false
```

Registry behavior remains unchanged.

## Tests

```text
Source focused before YAML update: 15 passed, 13 deselected
Source + experiment spec + P2 state: 32 passed
backup/current comparison:
  CsI2017 bitwise equal in interpolated and direct modes
  CsI2021 bitwise equal in interpolated and direct modes
  Ar2020 bitwise equal in interpolated and direct modes
```

Coverage includes state mapping, particle labels, immutable densities, prompt
line, fixed-grid bitwise hashes, scalar/array behavior, boundary behavior,
finite/nonnegative output, component sums, normalization diagnostics, errors,
spec loading and shared-source non-regression.

## Numerical Diagnostics

```text
prompt energy: 29.792140909877446 MeV
prompt/integrated component weight: 5.793617637932336e14 cm^-2
interpolated integral e: 5.790079910930172e14 cm^-2
interpolated integral mub: 6.602135657046989e14 cm^-2
interpolated continuous total: 1.239221556797716e15 cm^-2
minimum sampled total flux: 0
maximum sampled total flux: 3.699991298183052e13 cm^-2 MeV^-1
component-sum absolute residual: 7.8125e-3 cm^-2 MeV^-1
component-sum relative residual: below 5e-16
matching/continuity diagnostics: not applicable; prompt line is separate
```

These integrals are frozen reproduction diagnostics. P3 does not silently
correct or renormalize the existing endpoint convention.

## Source Figures

The full-range and low-energy PNG/PDF figures were visually inspected. They
are finite and nonnegative, identify the prompt line and 56 MeV mask, show the
interpolation nodes and retained boundary-cell taper, and reproduce the CSV
grid. No unexplained discontinuity or negative region was found.

## Blockers

```text
Gate S0 blocker: none
deferred nonblocking audit: exact physical endpoint/final interpolation cell
deferred nonblocking audit: physical nu/antinu kernel differences
missing source data: none; the approved source is analytic
```

## Gate S0

```text
status: PASS
reasons:
  - approved SHARED_EXTENSION state routing is implemented and loadable
  - pre-P3 flux arrays are bitwise unchanged
  - support, units, interpolation, boundary and normalization are explicit
  - state and flux scalar/array/error contracts pass
  - experiment.yaml resolves both validated source callables
  - Source tests and Ar2020 non-regression pass
  - validation figures pass visual QA
  - no unrelated production behavior changed
next_skill: cevns-theory-response
```

