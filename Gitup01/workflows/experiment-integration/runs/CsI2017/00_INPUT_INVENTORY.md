# CsI2017 P3 Flavor Slow Migration — Input Inventory

## Dataset identity

- dataset_id: CsI2017
- experiment_family: COHERENT_CsI
- run_period: 2017 release/current repository reproduction
- detector_configuration: CsI[Na], 14.57 kg source metadata; legacy Slow multiplier 14.6 kg
- source_configuration: stopped-pion SNS prompt nu_mu plus delayed nu_e and antinu_mu
- target_configuration: equal Cs:I stoichiometry using I-127 and Cs-133
- statistical_data_mode: background_subtracted_excess

The statistical mode is provisional and unused by P3. No authoritative
observed/background/covariance provenance was supplied with the Flavor
migration, so statistics remains blocked rather than inferred from local
tables.

## Input paths

Physics documents:

- F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/CEvNS-pyEFT Flavor 重构：问题处理优先级提示词.md
- F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/CEvNS_pyeFT_full_flavor_refactor_implementation_spec.md

References and attachments:

- PHASE1_SPLIT_REPORT.md
- data/responses/responses_all.json
- data/datafiles/COHERENT_eff.txt
- tests/reference_fast_split/csi2017_*.npy
- tests/reference_fast_split/csi2017_metadata.json

Repository files inspected:

- src/cevns_pyeft/experiments/base.py
- src/cevns_pyeft/experiments/registry.py
- src/cevns_pyeft/experiments/specs.py
- src/cevns_pyeft/experiments/coherent/sns.py
- src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py
- src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py
- src/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py
- src/cevns_pyeft/rates/counts.py
- src/cevns_pyeft/rates/differential.py
- src/cevns_pyeft/sources/state.py
- schemas/experiment.schema.json
- schemas/csv_contracts.json
- tests/test_source_state_p2.py
- tests/test_rates_differential_flavor.py

No standalone CsI2017 experiment.yaml exists; the legacy dataset is registered
in Python.

## Experiment goal

- signal: canonical 3x3 Flavor Wilson prediction for CsI2017.
- slow: pass rho and particle_kind for each SNS component before flux integration.
- fast: frozen until P4; the scalar Fast representation is not modified.
- statistics: out of scope and blocked by missing provenance.
- validation: preserve the legacy Slow result and add component/state regressions.

## Observable axes

- E_nu: true incident energy, MeV at rates boundary, integrated out.
- E_R: true nuclear recoil, keV, exact two-body support.
- PE: reconstructed photoelectrons, 0.001–50.0 PE in 25 bins.
- source_component: mu, e, mub, plus total.
- target: I127 and Cs133 diagnostic components.

Expected outputs:

- counts_per_bin[mu|e|mub|total]: shape (25,), events/bin.
- counts_per_npe[mu|e|mub|total]: shape (25,), events/PE.
- target_flavor_dndpe_grid[component][target]: shape (251,).
- pe_grid: shape (251,); pe_bins: shape (26,).

## Supplied scalar parameters

| Quantity | Value | Unit | Repository source |
|---|---:|---|---|
| Baseline | 19.3 | m | SNS_DATASETS |
| N_POT | 1.73e23 | count | SNS_DATASETS |
| Yield r | 0.08 | neutrinos/POT/component | SNS_DATASETS |
| Source detector mass | 14.57 | kg | SNS_DATASETS |
| Legacy Slow multiplier | 14.6 | kg | slow_counts_csi2017.py |
| Integrated component flux | 2.956729593266706e14 | cm^-2 | current source formula |
| Physical prompt line | 29.792140909877446 | MeV | pion decay formula |
| Legacy rate prompt value | 29.65 | MeV | rates/counts.py |
| PE yield | 1.17 | PE/keV | Slow wrapper |
| sin2thetaW default | 0.2387 | dimensionless | Slow API |
| Efficiency threshold | 4.9 | PE | Slow wrapper |
| Efficiency low value | 1e-10 | dimensionless | Slow wrapper |
| I/Cs mass weights | 127/260, 133/260 | dimensionless | Slow wrapper |

The 14.57/14.6 kg and 29.79214/29.65 MeV pairs are explicit legacy
reproduction differences. P3 preserves existing numerical behavior; it does
not silently resolve them.

## Supplied formulas and tables

- Flux normalization: r N_POT/(4 pi L_cm^2), unit cm^-2.
- Delayed nu_e Michel spectrum: 192 E^2(1/2-E/m_mu)/m_mu^3.
- Delayed antinu_mu spectrum: 64 E^2(3/4-E/m_mu)/m_mu^3.
- Flavor contraction: dσ/dER = Tr[rho(E_nu) K(E_nu,ER)].
- Reconstruction: PE = 1.17 E_R(keV).
- Efficiency table: COHERENT_eff.txt, 36 rows and two columns (PE, efficiency);
  sorted unique linear interpolation, left 1e-10, right last value, and
  PE <= 4.9 forced to 1e-10.
- Frozen Fast reference: full kernel shape (3,3,8,22,22,25); protected and not
  an independent Flavor correctness reference for P3.

## Source definition

- Type: time-integrated stopped-pion SNS.
- Prompt mu: rho_mu, particle_kind nu, monoenergetic line.
- Delayed e: rho_e, particle_kind nu, Michel continuum.
- Delayed mub: rho_mu, particle_kind antinu, Michel continuum.
- Configured tabulation grid: 0.001–300 MeV; physical mask: 0.001–56 MeV.
- Default interpolation: 200-point linear interpolation; zero outside the
  tabulation range; values clipped nonnegative at nodes.
- Each component uses NTimeIntegratedFlux_cm^-2.
- Prompt is separate from the continuous spectra.

Current reproduction applies the physical mask at interpolation nodes, so the
last boundary cell may taper linearly. Exact zero outside 56 MeV is a separate
source-physics audit, not part of P3 state plumbing.

Physical checks:

- finite for finite input: yes.
- nonnegative at tabulation: yes.
- exact zero outside physical support: not guaranteed inside a boundary cell.
- correct integrated normalization: analytic intent; discretized regression needed.
- uncertainties: not represented.

## Detector and target definition

- Detector: one CsI[Na] module.
- Exposure: run-integrated flux multiplied once by detector mass.
- Material: equal Cs:I stoichiometry.
- Isotopes and response keys: Cs-133 -> Cs133; I-127 -> I.
- Nucleus mass convention: A times 1.6605390666e-27 kg.
- Verified records: Cs133 (A=133,Z=55,N=78,J=3.5);
  I (A=127,Z=53,N=74,J=2.5).

## Theory, kinematics and cross section

- Wilson basis: 22 canonical LeftKey operators with value shape (3,3).
- Flavor order: e, mu, tau; row is final, column is initial.
- Outgoing flavor is summed in K=C†C.
- SM coefficients are c_SM I3.
- rho is dimensionless; rates differential result is cm^2/keV.
- E_R is keV and E_nu is MeV at the rate API; theory converts to GeV.
- differential_cross_section_nn is authoritative and returns exact zero outside
  exact two-body support; invalid negative inputs raise.
- counts.py currently uses sqrt(m_A E_R/2) only as a pre-mask approximation.

## Detector response

- Mean mapping: PE = 1.17 E_R(keV).
- Stochastic response: none in the current CsI2017 delta-fold path.
- Efficiency: existing COHERENT table.
- Binning: 25 PE bins over 0.001–50.
- Flavor physics must end before this scalar layer.

## Slow counts

Integration chain:

source flux/state -> Flavor kernel -> Tr[rho K] -> E_nu integration ->
nuclei/kg -> PE mapping -> efficiency -> PE binning -> Cs/I combination.

- Integration order: E_nu at fixed E_R, deterministic E_R-to-PE mapping, PE bins.
- Defaults: n_enu=120 and a 251-point PE/E_R grid.
- Axes: source component, target, PE bin.
- Units: events/bin and events/PE.
- Legacy small-grid total: 342.62089359028045 from PHASE1_SPLIT_REPORT.md.
- Reference arrays and tolerances must not be changed to force a pass.

## Fast counts

Legacy representation is scalar N=c†Hc over 22 operators, with full stored
shape (3,3,8,22,22,25). It is blocked for Flavor use until P4 defines
Tr[rho C_I†C_J], tensor reconstruction, schema versioning and stale-kernel
behavior. Existing files and arrays are protected in P3.

## Statistical data

- Primary mode: background_subtracted_excess, provisional and unused in P3.
- Observed data, background, covariance, nuisance model, test statistic,
  profiling and confidence construction: not authoritatively supplied.
- Phase 9 is blocked pending a statistics document and provenance.

## Missing information

- ANTI-NU AUDIT: required for physical nu/antinu sign corrections, but does not
  block metadata plumbing or backward-equivalent P3 Slow migration.
- Flavor Fast contract: blocks P4/Phase 8 only.
- Authoritative statistics provenance: blocks Phase 9 only.
- Exact source-boundary and legacy mass/prompt discrepancies: recorded for a
  later physics audit and must not be silently changed in P3.

## Current achievable implementation level

SLOW_PLANNED

