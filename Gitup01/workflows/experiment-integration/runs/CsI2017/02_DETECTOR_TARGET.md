# CsI2017 Phase 2 Detector/Target Report

## Phase 0 Target Decision

```text
dataset_id: CsI2017
target_status: REUSE
target_mode: CsI_equal_stoichiometry
reason: the existing Slow path already implements the approved Cs-133/I-127
        equal-stoichiometry target and both required Response records exist
Gate I status: PASS
Gate D0 status: PASS
```

The approved target contract is retained without creating a target module or
runtime target table.  The unresolved 14.57 kg/14.6 kg difference is an
exposure convention difference, not a second detector or a target-composition
change.  The two Flavor refactor documents do not supply a replacement value,
so this phase preserves the recorded reproduction behavior.

## Detector Inventory

| Detector | Material | Active mass | Live time | Exposure | Source |
|---|---|---:|---:|---:|---|
| CsI2017 CsI[Na] | CsI[Na] | 14.57 kg metadata; 14.6 kg legacy Slow factor | not separately supplied | 1.73e23 POT at 19.3 m; per-component integrated flux 2.956729593266706e14 cm^-2; legacy Slow flux-mass factor 4.31682520616939e15 kg cm^-2 | approved Phase 0/1 reports and current `slow_counts_csi2017.py` |

```text
detector labels: [CsI2017_CsI_Na]
detector count: 1
detector axis required: no; singleton detector is collapsed
detector-dependent calibration: yes, but deferred to detector-response validation
detector-dependent target: no
```

The Na dopant belongs to detector response and does not add a CEvNS target
component in the approved current reproduction.

## Exposure Semantics

```text
active mass: 14.57 kg in source metadata; 14.6 kg in the authoritative legacy Slow multiplication
active-mass unit: kg
live time: not supplied as an independent quantity
live-time unit: not applicable
exposure: time-integrated SNS flux followed by one detector-mass multiplication
exposure unit: cm^-2 times kg
exposure already includes active mass: no, the stored/integrated flux is per area
exposure already includes live time: yes, source normalization is time-integrated through N_POT
additional mass multiplication required: yes, exactly once; use 14.6 kg for legacy Slow reproduction
additional live-time multiplication required: no
detector-dependent exposure: no retained axis; there is one detector
isotope-dependent exposure: no; isotope dependence enters through nuclei/kg and mass fractions
```

The current event chain is:

```text
time-integrated component flux [cm^-2]
* cross section [cm^2/keV]
* nuclei per kg [kg^-1]
* 14.6 kg exactly once
```

The 14.57 kg metadata value must remain metadata and must not be multiplied in
addition to the 14.6 kg legacy factor.  Numerically, using 14.6 instead of
14.57 changes the mass normalization by `2.05902539464642e-3`; this phase does
not resolve or hide that difference.

## Target Inventory

### Material Inventory

| Material | Detector | Formula or composition | Mass fraction | Source |
|---|---|---|---:|---|
| CsI | CsI2017 CsI[Na] | one Cs atom and one I atom per formula unit | 1 | approved Phase 0/1 target contract |

```text
materials: [CsI]
compound targets: CsI with equal Cs:I number stoichiometry
material normalization: one kilogram of bulk CsI is split by 133/260 and 127/260 mass fractions
detector-dependent materials: no
```

### Isotope Inventory

| Material | Isotope | A | Z | N | Abundance or stoichiometric weight | Molar mass |
|---|---|---:|---:|---:|---:|---:|
| CsI | Cs-133 | 133 | 55 | 78 | 1 Cs atom/formula unit; mass fraction 133/260 = 0.5115384615384615 | 133 g/mol in the code's mass-number convention |
| CsI | I-127 | 127 | 53 | 74 | 1 I atom/formula unit; mass fraction 127/260 = 0.48846153846153845 | 127 g/mol in the code's mass-number convention |

```text
isotopes: [Cs-133, I-127]
natural, enriched, or pure: pure-isotope approximation fixed by the existing reproduction
abundance convention: no natural-abundance mixture is expanded
stoichiometric convention: one Cs-133 nucleus and one I-127 nucleus per CsI formula unit
abundance normalization: 133/260 + 127/260 = 1 exactly at recorded precision
isotope axis required: diagnostic/internal only
```

Approximation record:

```text
approximation name: CsI equal-stoichiometry pure-isotope reproduction
exact target composition being replaced: any subdominant natural isotopes and Na dopant are not represented as CEvNS target components
effective target: Cs-133 plus I-127
reason: this is the approved existing CsI Slow contract
scope: CsI2017 target normalization and Response routing
validation requirement: preserve the existing weighted target sum and Response keys
```

## Nuclei-Per-Mass Convention

The implementation uses

```text
u_kg = 1.6605390666e-27 kg
M_nucleus = A * u_kg
nuclei_per_kg_pure = 1 / (A * u_kg)
```

This is equivalent at recorded precision to using
`N_A = 6.02214076208112e23 mol^-1` with effective molar masses of 133 and
127 g/mol.

```text
component: Cs-133 pure component
formula: 1 / (133 * 1.6605390666e-27)
Avogadro constant: 6.02214076208112e23 mol^-1 (implied by the code constant)
molar mass: 133 g/mol
abundance factor: 1
stoichiometric factor: 1
mass fraction: 133/260
nuclei per kilogram, pure component: 4.52792538502340e24
nuclei per kilogram of CsI after mass fraction: 2.31620798541582e24
unit: nuclei/kg
future implementation owner: existing `rates/counts.py` plus CsI Slow weighting; REUSE
```

```text
component: I-127 pure component
formula: 1 / (127 * 1.6605390666e-27)
Avogadro constant: 6.02214076208112e23 mol^-1 (implied by the code constant)
molar mass: 127 g/mol
abundance factor: 1
stoichiometric factor: 1
mass fraction: 127/260
nuclei per kilogram, pure component: 4.74184311974892e24
nuclei per kilogram of CsI after mass fraction: 2.31620798541582e24
unit: nuclei/kg
future implementation owner: existing `rates/counts.py` plus CsI Slow weighting; REUSE
```

Thus each species has the same number density in bulk CsI and the total is
`4.63241597083163e24 nuclei/kg`.  With the legacy 14.6 kg Slow factor this is
`3.38166365870709e25` nuclei of each species and
`6.76332731741418e25` target nuclei in total.

## Nuclear-Response Routing

| Isotope | A | Z | N | Response key | Available | Response source |
|---|---:|---:|---:|---|---|---|
| Cs-133 | 133 | 55 | 78 | `Cs133` | yes | `data/responses/responses_all.json` through `ResponseDB.get("Cs133")` |
| I-127 | 127 | 53 | 74 | `I` | yes | `data/responses/responses_all.json` through `ResponseDB.get("I")` |

```text
Response database: data/responses/responses_all.json
Response loader: cevns_pyeft.nuclear.response.ResponseDB
required response channels: Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP
missing response keys: none
fallback prohibited: yes
```

Both records provide all eight listed channels.  No nearby-isotope,
natural-element, or other-experiment fallback is permitted.

## Component Axes

```text
detector axis: collapsed singleton [CsI2017_CsI_Na]
material axis: collapsed singleton [CsI]
isotope axis: diagnostic/internal [Cs133, I127]
target-response axis: diagnostic/internal [Cs133 -> Cs133, I127 -> I]
```

Axis contracts:

```text
axis name: isotope
labels: [Cs133, I127]
public output or diagnostic only: diagnostic only in `target_flavor_dndpe_grid`
sum rule: CsI prediction = (133/260)*Cs133_per_kg + (127/260)*I127_per_kg

axis name: target-response
labels: [Cs133, I]
public output or diagnostic only: diagnostic only
sum rule: one and only one Response key is routed for each isotope component
```

The material mass-fraction sum residual is `0`.  The relative residual between
the two equal-stoichiometry number densities is `-1.15894366002632e-16`, which
is floating-point roundoff.

## Future Implementation Classification

```text
status: REUSE
reason: current target composition, nuclei/kg convention, weights and Response routing satisfy the approved contract
future implementation required: no target implementation is required
future implementation scope: later source and Slow phases may pass Flavor state through the existing target path without changing target physics
planned future files: none for target
blocked inputs: none for Gate T0; the 14.57/14.6 kg physics resolution remains a separate audit and is frozen for reproduction
```

## Files

### Created

```text
workflows/experiment-integration/runs/CsI2017/02_DETECTOR_TARGET.md
```

### Modified

```text
None.
```

### Protected

```text
data/experiments/CsI2017/experiment.yaml
src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py
src/cevns_pyeft/rates/counts.py
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
data/experiments/CsI2017/target.csv
data/experiments/CsI2017/isotope_inventory.csv
tests/test_CsI2017_target.py
src/cevns_pyeft/experiments/registry.py
all source, theory, kernel, Fast, statistics and CONUS files
```

## Diagnostics

```text
number of detectors: 1
number of materials: 1
number of isotopes: 2
nuclei per kilogram by component: Cs133=2.31620798541582e24, I127=2.31620798541582e24 nuclei/kg CsI
total nuclei per kilogram: 4.63241597083163e24
exposure by detector: legacy reproduction uses 2.956729593266706e14 cm^-2 * 14.6 kg = 4.31682520616939e15 kg cm^-2 per SNS component
metadata-only comparison: 2.956729593266706e14 cm^-2 * 14.57 kg = 4.30795501738959e15 kg cm^-2
Response keys: [Cs133, I]
component-sum residual: mass fractions 0; equal-number relative residual -1.15894366002632e-16
tests added or run: none; Phase 2 is text-only
```

## Gate T0

```text
status: PASS
reasons:
  - the singleton detector inventory and both mass conventions are explicit
  - target composition and equal-stoichiometry normalization are complete
  - time-integrated flux and detector mass are each counted exactly once
  - nuclei-per-mass formulas and numerical diagnostics are explicit
  - Response keys Cs133 and I exist with all required channels
  - component axes, routing and sum rules are defined
  - the smallest future target classification is REUSE
  - no production code, runtime data, YAML or tests were modified in Phase 2
```

## Next Skill

```text
cevns-source
```

Stop after Gate T0.  Do not execute Source automatically.
