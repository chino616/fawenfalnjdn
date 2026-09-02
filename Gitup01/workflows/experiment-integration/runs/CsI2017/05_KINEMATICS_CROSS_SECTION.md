# CsI2017 Phase 5 Kinematics and Differential Cross Section Report

## Inputs and Reference APIs

```text
dataset_id: CsI2017
Gate S0: PASS
Gate T1: PASS
targets: Cs-133 (Cs133), I-127 (I)
```

| Role | File | Symbol |
|---|---|---|
| Full Response differential | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |
| Flavor kernel | `src/cevns_pyeft/rates/differential.py` | `differential_flavor_kernel_nn` |
| Exact kinematics | `src/cevns_pyeft/theory/kinematics.py` | `minimum_neutrino_energy_GeV`, `two_body_recoil_max_GeV` |
| Helm form factor | `src/cevns_pyeft/theory/helm/form_factor.py` | `helm_form_factor` |
| Helm SM cross section | `src/cevns_pyeft/theory/helm/cross_section.py` | `dsigma_dER_helm_cm2_per_keV` |

Full-response call path:

```text
E_nu [MeV], E_R [keV], ResponseW, Wilson matrices, NeutrinoState
→ exact two-body support
→ Li2026 full nuclear Responses
→ incoming-Flavor kernel K [cm^2/keV]
→ Tr[rho K]
```

Helm call path:

```text
E_nu [MeV], E_R [keV], A, Z, sin2_theta_w
→ exact two-body support
→ SM weak charge
→ scalar Helm F_H(q)^2
→ d sigma/dT [cm^2/keV]
```

Verified full-response API:

```text
energy input: MeV, scalar or ndarray
recoil input: keV, scalar
target mass internally: A*AMU_GEV in GeV
Response argument: arbitrary ResponseW
Wilson argument: canonical 3x3 matrices keyed by LeftKey
state argument: NeutrinoState or rho plus explicit particle_kind
return unit: cm^2/keV
array shape: Enu input shape
out-of-support behavior: exact zero
negative/nonfinite energy: explicit error
```

## Production Decision and Model Selection

```text
kinematics classification: REUSE
cross-section classification: REUSE
new adapter required: no
default model: full_response
available models: [full_response, helm_sm]
full_response kinematics: exact_two_body
helm_sm kinematics: [exact_vector, mathematica_reproduction]
Helm allowed coefficient space: Standard Model weak charge only in the selected SM API
unsupported combinations: arbitrary Wilson coefficients passed to helm_sm
```

The two models are separate APIs and mutually exclusive. Full Response is never
multiplied by Helm. The Helm SM callable has no Wilson-coefficient parameter and
rejects such keyword arguments with `TypeError`.

## Helm Convention

```text
weak charge: Q_W = N - (1 - 4*sin2_theta_w)*Z
cross-section prefactor: G_F^2*m_A/(4*pi)
proton contribution: -(1 - 4*sin2_theta_w)*Z
neutron contribution: +N
c radius: 1.23*A^(1/3) - 0.60 fm
diffuseness a: 0.52 fm
skin s: 0.90 fm
R1^2: c^2 + 7*pi^2*a^2/3 - 5*s^2
form factor: 3*j1(q*R1)/(q*R1)*exp[-(q*s)^2/2]
q-to-zero treatment: explicit series expansion
F_H(0): exactly 1
proton/neutron form factors: one shared Helm shape in the SM comparison model
```

## Kinematics

```text
true recoil: E_R in keV
neutrino energy: E_nu in MeV
target mass: A*AMU_GEV in GeV
exact E_nu_min:
  0.5*(E_R + sqrt(E_R^2 + 2*m_A*E_R))
reproduction pre-mask approximation:
  sqrt(m_A*E_R/2)
selected authoritative differential support: exact
recoil endpoint:
  2*E_nu^2/(m_A + 2*E_nu)
outside support: exact zero
endpoint included: yes
```

The heavy-nucleus approximation remains a documented counts-grid optimization;
it does not replace the exact differential mask.

## Diagnostic Files

Created:

```text
workflows/experiment-integration/runs/CsI2017/artifacts/kinematic_endpoints.csv
workflows/experiment-integration/runs/CsI2017/artifacts/cross_section_grid.csv
workflows/experiment-integration/runs/CsI2017/figures/cross_section_vs_recoil.png
workflows/experiment-integration/runs/CsI2017/figures/cross_section_vs_recoil.pdf
workflows/experiment-integration/runs/CsI2017/figures/full_response_vs_helm.png
workflows/experiment-integration/runs/CsI2017/figures/full_response_vs_helm.pdf
workflows/experiment-integration/runs/CsI2017/05_KINEMATICS_CROSS_SECTION.md
```

Modified:

```text
None.
```

Protected:

```text
shared Li2026 theory
shared Helm implementation
shared kinematic helpers
shared Response data
all experiment production, Slow, Fast, statistics, reference and CONUS files
```

## Numerical Diagnostics

```text
energies: [10, 29.792140909877446, 50, 56] MeV
endpoint rows: 40
cross-section rows: 2904
exact endpoint inverse residual: 7.105427357601002e-15 MeV
F_Helm_Cs133(0): 1
F_Helm_I127(0): 1
full-response range: 0 to 2.978073762455483e-39 cm^2/keV
Helm exact-vector range: 0 to 2.978029112520407e-39 cm^2/keV
all out-of-support values: exactly zero
prompt full/Helm ratio, Cs-133: [0.9430959098382151, 1.0000149931157112]
prompt full/Helm ratio, I-127: [0.9555643113365764, 1.0000063464618287]
independent model normalization: none
```

The comparison uses identical target A/Z, energy, recoil grid,
`sin2_theta_w=0.2387`, mass convention, exact support and output units.

## Tests and Artifact Checks

```text
Helm + exact kinematics + Cs/I Flavor kernel + differential: 61 passed
endpoint CSV rows: 40
cross-section CSV rows: 2904
model labels: full_response, helm_sm
kinematic labels: exact_two_body, exact_vector, mathematica_reproduction
all totals finite and nonnegative: yes
all forbidden points zero: yes
Helm rejects Wilson kwargs: yes
figures reproducible from saved grids: yes
figure visual QA: PASS
endpoint CSV SHA-256:
  c5258eb67647e82240a3c4442a5dc9859cd5053f48434b87e4e38809af11a046
cross-section CSV SHA-256:
  288226343b91782b65232bd27555fde6b02cde7f64c8b380f8dcd8bf36fb4df6
```

## Blockers

```text
Gate X blocker: none
deferred nonblocking audit: physical nu/antinu kernel differences
```

## Gate X

```text
status: PASS
reasons:
  - exact kinematics and unit boundaries are reused
  - full_response and helm_sm are explicit and mutually exclusive
  - full_response supports the approved Flavor Wilson matrices
  - Helm SM convention, F(0) and coefficient restrictions pass
  - exact endpoints, masks, scalar/array behavior and unit ratios pass
  - diagnostic grids and raw model-comparison figures pass
default_cross_section_model: full_response
available_cross_section_models: [full_response, helm_sm]
next_skill: cevns-detector-response
```

