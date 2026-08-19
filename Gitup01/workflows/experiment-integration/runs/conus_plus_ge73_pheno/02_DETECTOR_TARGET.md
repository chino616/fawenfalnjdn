# Phase 2 Target Inventory Report: conus_plus_ge73_pheno

## Purpose

This phase records the detector and target inventory before source
implementation.

This is a text-only phase. No target code, target CSV, target test, runtime data,
or production source file was created.

## Inputs

- Physics document:
  `docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf`
- Phase 0 inventory:
  `workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md`
- Phase 0 manifest:
  `workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml`
- Phase 1 dataset report:
  `workflows/experiment-integration/runs/conus_plus_ge73_pheno/01_DATASET.md`
- Dataset spec:
  `data/experiments/conus_plus_ge73_pheno/experiment.yaml`
- Target template:
  `workflows/experiment-integration/templates/02_DETECTOR_TARGET.md`

## Phase 0 Target Decision

```text
dataset_id: conus_plus_ge73_pheno
target_status: CONFIG_ONLY
target_mode: Ge73_only
reason: one effective detector and one pure Ge73 target are already represented in experiment.yaml
Gate I status: PASS
Gate D0 status: PASS
```

The target status remains `CONFIG_ONLY`. Any later code should consume the
`experiment.yaml` fields and `ResponseDB.get("Ge73")`; no target adapter is
approved by this phase.

## Detector Inventory

| Detector | Material | Active mass | Live time | Exposure | Source |
|---|---|---:|---:|---:|---|
| `Ge73` | effective `73Ge` | included in exposure | included in exposure | `119 kg day` | Phase 0 inventory; `experiment.yaml` |

```text
detector labels: Ge73
detector count: 1
detector axis required: no public detector axis; optional diagnostic label Ge73
detector-dependent calibration: no
detector-dependent target: no
```

This is not the official CONUS+ C2/C3/C5 detector-by-detector model.

## Exposure Semantics

```text
active mass: not separately used
active-mass unit: kg
live time: not separately used
live-time unit: day
exposure: 119
exposure unit: kg day
exposure already includes active mass: yes
exposure already includes live time: yes
additional mass multiplication required: no
additional live-time multiplication required: no
detector-dependent exposure: no
isotope-dependent exposure: no
```

Later Slow/Fast/statistics phases must count exposure exactly once. For the
Slow normalization, the documented factor is:

```text
X = n_Ge73_per_kg * 119 kg day * 86400 s/day
```

## Target Inventory

### Material Inventory

| Material | Detector | Formula or composition | Mass fraction | Source |
|---|---|---|---:|---|
| effective `73Ge` | `Ge73` | pure `73Ge` | 1.0 | Phase 0 inventory; `experiment.yaml` |

```text
materials: effective 73Ge
compound targets: none
material normalization: single material, mass fraction 1.0
detector-dependent materials: no
```

### Isotope Inventory

| Material | Isotope | A | Z | N | Abundance or stoichiometric weight | Molar mass |
|---|---|---:|---:|---:|---:|---:|
| effective `73Ge` | `Ge73` | 73 | 32 | 41 | 1.0 | `73 g mol^-1` |

```text
isotopes: Ge73
natural, enriched, or pure: pure effective Ge73
abundance convention: pure isotope abundance = 1.0
stoichiometric convention: not applicable
abundance normalization: 1.0
isotope axis required: no public isotope axis; optional diagnostic label Ge73
```

No effective-isotope replacement is being introduced here. The user document
itself defines this phenomenological dataset as `73Ge` only, not natural
germanium.

## Nuclei-Per-Mass Convention

```text
component: Ge73
formula: nuclei_per_kg = Avogadro_constant * 1000 / molar_mass_g_per_mol
Avogadro constant: 6.02214076e23 mol^-1
molar mass: 73 g mol^-1
abundance factor: 1.0
stoichiometric factor: 1.0
mass fraction: 1.0
nuclei per kilogram: 8.249507890411e24 kg^-1
unit: nuclei kg^-1
future implementation owner: experiment configuration
```

The exposure-normalized target-time factor for later Slow counts is:

```text
nuclei_per_kg * 119 kg day * 86400 s/day = 8.481814032605e31 nucleus s
```

## Nuclear-Response Routing

| Isotope | A | Z | N | Response key | Available | Response source |
|---|---:|---:|---:|---|---|---|
| `Ge73` | 73 | 32 | 41 | `Ge73` | yes | `data/responses/responses_all.json` via `ResponseDB.get("Ge73")` |

```text
Response database: data/responses/responses_all.json
Response loader: src/cevns_pyeft/nuclear/response.py::ResponseDB
required response channels: Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP
missing response keys: none
fallback prohibited: yes
```

The existing `Ge73` entry records:

```text
A = 73
Z = 32
N = 41
J = 4.5
T = 4.5
b = 10.68180034434144
```

Do not fall back to natural germanium, another Ge isotope, or an isoscalar
approximation.

## CsI Local Reference

Read only for target/Response interface conventions:

- `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py`
- `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py`
- `src/cevns_pyeft/nuclear/response.py`

Only the `ResponseDB(...).get(response_key)` routing and component-label
convention were used. No Cs/I isotope values, stoichiometry, mass weights,
exposure, or response keys were copied.

## Component Axes

```text
detector axis: diagnostic only
material axis: diagnostic only
isotope axis: diagnostic only
target-response axis: required by ResponseDB object
```

| Axis | Labels | Public output or diagnostic only | Sum rule |
|---|---|---|---|
| detector | `Ge73` | diagnostic only | identity; one detector |
| material | effective `73Ge` | diagnostic only | identity; one material |
| isotope | `Ge73` | diagnostic only | identity; one isotope |
| target-response | `Ge73` | implementation input | one Response object routes all target response channels |

The public event-count output remains the 19-bin reconstructed-energy axis from
Phase 1.

## Future Implementation Classification

```text
status: CONFIG_ONLY
reason: one detector, one isotope, one Response key, and aggregate exposure are fully represented in experiment.yaml
future implementation required: no target-specific implementation
future implementation scope: consume experiment.yaml target fields and ResponseDB.get("Ge73") in later phases
planned future files: none for target
blocked inputs: none for target
```

The source, detector-response, Slow, Fast, and statistics phases still have
their own separate implementation plans. They must not create a target adapter
unless a later user request changes the target model.

## Files

### Created

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/02_DETECTOR_TARGET.md
```

### Modified

```text
None.
```

### Protected

```text
data/experiments/conus_plus_ge73_pheno/experiment.yaml
src/cevns_pyeft/experiments/conus/target.py
src/cevns_pyeft/experiments/conus/target_inventory.py
data/experiments/conus_plus_ge73_pheno/target.csv
data/experiments/conus_plus_ge73_pheno/isotope_inventory.csv
tests/test_conus_plus_ge73_pheno_target.py
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

```text
number of detectors: 1
number of materials: 1
number of isotopes: 1
nuclei per kilogram by component:
  Ge73: 8.249507890411e24 kg^-1
total nuclei per kilogram: 8.249507890411e24 kg^-1
exposure by detector:
  Ge73: 119 kg day
exposure-normalized target-time:
  Ge73: 8.481814032605e31 nucleus s
Response keys:
  Ge73
Response channels:
  Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP
component-sum residual: 0
```

## Checks Run

```text
Read experiment.yaml target and detector fields.
Read Phase 0 inventory target section.
Read Phase 0 manifest target classification.
Read Phase 1 dataset report and Gate D0 status.
Read ResponseDB interface in src/cevns_pyeft/nuclear/response.py.
Read CsI Slow target/Response routing references by text search.
Read Ge73 entry from data/responses/responses_all.json with Python stdlib json.
Computed nuclei_per_kg and exposure-normalized target-time.
```

Command result used for Response and numerical diagnostics:

```text
basic= {'name': 'Ge73', 'A': 73, 'Z': 32, 'N': 41, 'J': 4.5, 'T': 4.5, 'b': 10.68180034434144}
keys= Delta,M,MPhiPP,PhiPP,PhiPT,SigmaP,SigmaPDelta,SigmaPP
nuclei_per_kg= 8.249507890411e+24
exposure_nucleus_s= 8.481814032605e+31
```

No pytest target test was created or run, because Phase 2 is text-only.

## Gate T0

```text
status: PASS
```

Reasons:

- Detector inventory is complete for the effective single-detector model.
- Target composition is complete for the pure `Ge73` phenomenological target.
- Exposure semantics are explicit and aggregate exposure is counted once.
- Nuclei-per-mass convention is explicit.
- Required Response key `Ge73` exists in the repository Response database.
- Component axes and identity sum rules are defined.
- Future implementation need is classified as `CONFIG_ONLY`.
- No production code, runtime data, target CSV, target test, or source file was
  created or modified by this phase.

## Next Skill

```text
cevns-source
```

Do not execute Source automatically.
