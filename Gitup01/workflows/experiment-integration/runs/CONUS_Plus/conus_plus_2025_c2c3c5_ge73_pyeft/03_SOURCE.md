# CONUS+ Phase 3 — Reactor antineutrino source

## Result

The CONUS+ detector-site reactor source is implemented as an experiment-specific
adapter.  It provides a pure electron-antineutrino state and per-second
differential fluxes for U235, U238, Pu239, Pu241 and their total.  The source
layer does not multiply target nuclei, exposure, detector response, efficiency
or bin widths.

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
contract_human_gate: APPROVED
machine_gate: PASS
implementation_human_gate: NOT_REVIEWED
module_classification: ADAPTER
```

## Approved physical contract

- Particle: electron antineutrino; `particle_kind=antinu`, Flavor `e`.
- Components: U235, U238, Pu239 and Pu241 with fractions 0.56, 0.07, 0.31 and 0.06.
- Energy support: 0–10 MeV inclusive; outside support is zero.
- Below 2 MeV: 32-point Kopeikin table with piecewise-linear interpolation.
- From 0 to 0.01 MeV: first-segment linear extrapolation clamped at zero.
- At 2 MeV: each isotope uses `S_r(2)/rho_Kop(2)`, so every component and the total are continuous.
- At and above 2 MeV: six-coefficient Mueller exponential polynomial.
- Absolute route: detector-site total flux `1.5e13 cm^-2 s^-1`.
- Output: `cm^-2 s^-1 MeV^-1`, time basis `per_second`.
- Flux uncertainty: 4.6%, metadata only until a statistics phase is requested.
- Thermal power, baseline geometry and fission energy are not multiplied.

For component `r`, the unnormalized shape is

```text
f_r * S_r^Mueller(E)                                      2 <= E <= 10 MeV
f_r * S_r^Mueller(2) / rho_Kop(2) * rho_Kop_nonnegative(E) 0 <= E < 2 MeV
0                                                         otherwise
```

The final differential flux is the shape multiplied by `Phi0/N_rho`.

## Numerical inputs and diagnostics

| Quantity | Value |
| --- | ---: |
| `rho_Mueller(2 MeV)` | 1.2580795232698319 |
| total match factor | 0.9677534794383323 |
| literal extrapolation zero crossing | 0.006538461538461538 MeV |
| literal signed `N_rho` | 6.460892614098174 |
| approved nonnegative `N_rho` | 6.461355163040058 |
| relative normalization change | 7.159211110787685e-05 |
| integrated detector-site flux | 1.5e13 cm^-2 s^-1 |

Machine-readable inputs:

- `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/source/kopeikin_nodes.csv`
- `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/source/mueller_coefficients.csv`

Diagnostics:

- `diagnostics/03_source_spectrum.csv`
- `diagnostics/03_source_spectrum.png`

## Code and interface

`src/cevns_pyeft/experiments/conus_plus/source.py` provides:

- `differential_flux(component, energy_mev)`: scalar-in/scalar-out and array-in/array-out differential flux;
- `total_differential_flux(energy_mev)`: total spectrum;
- `source_state()`: constant pure-electron `NeutrinoState` with `particle_kind="antinu"`;
- `load_reactor_flux()`: flux callables and explicit units, support, time basis and uncertainty metadata;
- table and normalization accessors used by diagnostics and tests.

The shared `sources.state.NeutrinoState` is reused. The time-integrated SNS flux
adapter is not reused because its normalization and component meanings differ.

## Verification

The focused physical assertions verified:

- 32 ordered Kopeikin nodes and four six-coefficient Mueller rows;
- fission fractions sum to one;
- finite and nonnegative flux on support;
- exact zero outside support;
- component sum equals total;
- each component is continuous at 2 MeV;
- `N_rho=6.461355163040058`;
- integrated flux is exactly `1.5e13 cm^-2 s^-1` at displayed precision;
- scalar, multidimensional-array, source-state and metadata behavior.

The independent assertion run passed.  The focused pytest suite was then run
with the project-designated Codex environment:

```text
F:\Work\.codex_conda_envs\codex-py311\python.exe
Python 3.11.15
NumPy 2.4.6
pytest 9.1.1
5 passed in 0.43s
```

The five tests cover table structure and selected registered values, fission
fractions, nonnegative support, component summation, 2 MeV matching,
detector-site normalization, scalar/array behavior, source state and metadata.
After approval persistence, the same five tests plus the two repository spec
regressions that do not require a writable pytest temporary directory passed
(`7 passed in 0.48s`), and the project loader independently confirmed the new
P03-complete status fields.  The remaining spec test could not enter its
`tmp_path` setup because the sandbox denies the default user temporary
directory; this was an environment setup error, not a failed assertion.
The complete 32-node and 24-coefficient transcription is additionally protected
by source review and registered SHA-256 fingerprints rather than by hard-coding
every table entry in the test.  This approval is for the designated environment;
older NumPy 1.x environments do not provide `numpy.trapezoid` and remain a
portability consideration for release validation.

## Approval and handoff

Machine Gate P03 is PASS.  After reviewing the formulas, Mueller and Kopeikin
tables, units, normalization, diagnostic spectrum, API and complete focused
test suite, the user approved the implementation on 2026-10-01.  P03 is
complete and the Master workflow may proceed to the Phase 4 pre-code physics
review; this approval does not pre-approve any Phase 4 physics choice or write.

## 2026-10-09 high-energy validity rebaseline

The implemented source formula and total detector-site normalization are
unchanged. The Mueller exponential-polynomial inputs are now explicitly
described as fitted over `2-8 MeV`; continuing the same polynomial over
`8-10 MeV` is the selected baseline extension, not an externally validated
prediction of that tail.

The focused tests verify that the baseline remains finite, positive and
integrable on both ranges. This is an implementation check only. P07 must
save the reconstructed-bin contributions from `E_nu <= 8 MeV` and
`E_nu > 8 MeV` separately and run declared high-energy extension controls.
No extension may be selected by tuning the tail to the paper curve.

The rebaseline verification run, including the selected-exposure metadata and
the existing nested-spec loader check, completed with `8 passed`.

The revised source implementation human gate is `NOT_REVIEWED` pending review
of this validity statement. The earlier P03 approval remains historical but
does not by itself approve the new evidence interpretation.
