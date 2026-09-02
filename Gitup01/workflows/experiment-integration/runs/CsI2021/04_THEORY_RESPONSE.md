# CsI2021 Phase 4 Theory and Nuclear Response Report

## Inputs and Classification

```text
dataset_id: CsI2021
theory_status: REUSE
response_status: REUSE
Gate I: PASS
Gate D0: PASS
Gate T0: PASS
Gate S0: PASS
target isotopes: [Cs-133, I-127]
Response keys: [Cs133, I]
```

No experiment-specific amplitude or nuclear-Response implementation was
created.

## Approved Theory Contract

```text
incoming flavor: density matrix rho in (e, mu, tau) initial-flavor space
particle identity: nu or antinu metadata from NeutrinoState
outgoing flavor: summed into K = C-dagger C
theory baseline: shared Li2026 one-body CEvNS
Wilson basis: 22 canonical LEFT operators
coefficient order: row=final flavor, column=initial flavor
complex coefficients supported: yes
target isotopes: Cs-133 and I-127
Response keys: Cs133 and I
new Lorentz structure: no
new propagator structure: no
```

Canonical Wilson order:

```text
C5_1, C6u1, C6d1, C6u2, C6d2,
C7u1, C7d1, C7u2, C7d2,
C7u3, C7d3, C7u4, C7d4, C7u5, C7d5, C7_6, C7_7,
C8u1, C8d1, C8u2, C8d2, C8_9
```

The current numerical kernel is shared by nu and antinu pending the dedicated
ANTI-NU physics audit; the particle label itself is preserved and tested.

## Reference Implementation

| Role | File | Symbol |
|---|---|---|
| Response data | `data/responses/responses_all.json` | `nuclei.Cs133`, `nuclei.I` |
| Response loader/object | `src/cevns_pyeft/nuclear/response.py` | `ResponseDB`, `ResponseW` |
| Response evaluator | `src/cevns_pyeft/nuclear/response.py` | `ResponseW.W_np` |
| LEFT mapping | `src/cevns_pyeft/theory/li2026/left_to_ci.py` | `left_to_ci` |
| Theory contraction | `src/cevns_pyeft/theory/li2026/responses.py` | `compute_R_matrices` |
| Amplitude entry | `src/cevns_pyeft/theory/li2026/amplitude.py` | `flavor_kernel_onebody_li2026` |
| State contraction | `src/cevns_pyeft/rates/differential.py` | `differential_cross_section_nn` |

Actual path:

```text
responses_all.json
→ ResponseDB.get("Cs133" or "I")
→ ResponseW.W_np(channel, y)
→ left_to_ci
→ compute_R_matrices
→ flavor_kernel_onebody_li2026
→ 3x3 Hermitian PSD incoming-Flavor kernel
→ Tr[rho K]
```

Verified conventions:

```text
Response input: y = (q*b/2)^2
Response native basis: ordered (p,n), 2x2
Response channels: Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP
amplitude E_nu unit: GeV
amplitude recoil input: keV
amplitude return: FlavorKernelResult with kernel shape (3,3)
differential return: cm^2/keV, scalar or Enu-shaped array
```

## Nuclear-Response Diagnostics

Grid definition:

```text
source energy used for physical endpoint: 56 MeV
recoil grid: 0 to isotope endpoint, 101 points
Cs-133 endpoint: 50.58035318425995 keV
I-127 endpoint: 52.9677159394953 keV
q definition: sqrt(2*m_A*E_R)
q unit: MeV in CSV; GeV internally
response variable: y = (q*b/2)^2
basis order: p,n
rows: 6464
```

Response ranges over all p/n entries:

```text
Cs133:
  Delta [0.001470119392642407, 2.777767329081821]
  M [185.17831762184602, 6084.002453757858]
  MPhiPP [-924.614275237974, -29.820569214943944]
  PhiPP [11.850502613466746, 346.7407632378248]
  PhiPT [-0.026221186833360246, 0.039924928818048044]
  SigmaP [-0.0011039931292083404, 0.4027959920988274]
  SigmaPDelta [-0.02365810892315016, 0.6733961453469848]
  SigmaPP [-0.0005519965646041798, 0.20139799604941389]
I:
  Delta [0.00865781749806687, 0.5358168796402408]
  M [191.86948377188614, 5475.961194368475]
  MPhiPP [-501.1646066768365, -12.830584905268843]
  PhiPP [3.7671650318104044, 201.1953955323554]
  PhiPT [-0.0016633002372620507, 0.004946488027305608]
  SigmaP [9.616246080137882e-05, 0.26026299886965265]
  SigmaPDelta [-0.1783018283767848, 0.0014404342615931293]
  SigmaPP [0.0005320904241356472, 0.1301314994348263]
```

Negative interference entries are valid raw repository responses and were not
clipped or independently normalized.

## Theory Benchmarks

Ten rows cover both targets at SM lower/mid/upper recoil, explicit nu and
antinu source labels, and an approved complex Flavor-changing
`C6u1[final=e,initial=mu] = 1e-6 + 2e-7j` point.

```text
amplitude-squared range: 4.4243625448264825e-11 to 1.529003132616062e-09
differential range: 3.269819126950483e-41 to 2.958566923094693e-39 cm^2/keV
all finite: yes
all total amplitudes nonnegative: yes
all differential values nonnegative: yes
```

## Files

Created:

```text
workflows/experiment-integration/runs/CsI2021/artifacts/nuclear_response_grid.csv
workflows/experiment-integration/runs/CsI2021/artifacts/theory_response_benchmarks.csv
workflows/experiment-integration/runs/CsI2021/figures/nuclear_response_channels.png
workflows/experiment-integration/runs/CsI2021/figures/nuclear_response_channels.pdf
workflows/experiment-integration/runs/CsI2021/04_THEORY_RESPONSE.md
```

Modified:

```text
None.
```

Protected:

```text
src/cevns_pyeft/theory/li2026/
src/cevns_pyeft/nuclear/response.py
data/responses/responses_all.json
all experiment production implementations
all Slow, Fast, statistics, reference arrays and CONUS files
```

## Tests and Artifact Validation

```text
Li2026 + Cs/I Flavor kernels + differential + source state: 124 passed
Response CSV rows: 6464
theory benchmark rows: 10
targets: exactly Cs133 and I
channels: exactly 8 approved repository channels
basis pairs: exactly pp, pn, np, nn
all Response grid values finite: yes
both dataset Response CSV SHA-256:
  3b59c45ed4b35b876161aac6119dd082b4560c7e443d7aca26fdfd213e4da937
Response figure visual QA: PASS after title/legend layout correction
```

## Blockers

```text
Gate T1 blocker: none
deferred nonblocking audit: physical nu/antinu kernel differences
```

## Gate T1

```text
status: PASS
reasons:
  - shared Li2026 theory accepts the canonical 22 complex Flavor matrices
  - Cs133 and I metadata and all eight native p/n Response channels load
  - raw Response grids and reproducible figures are complete
  - SM and complex Flavor-changing benchmarks are finite and nonnegative
  - existing theory/Flavor regressions pass
  - no production theory or Response file was modified
next_skill: cevns-kinematics-cross-section
```

