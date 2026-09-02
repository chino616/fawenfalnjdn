# CsI2021 P3 Flavor Slow Migration — Input Inventory

## Dataset identity

- dataset_id: CsI2021
- experiment_family: COHERENT_CsI
- run_period: 2021 release/current repository reproduction
- detector_configuration: 14.57 kg CsI[Na], CsI2021 efficiency and acceptance
- source_configuration: stopped-pion SNS prompt nu_mu plus delayed nu_e and antinu_mu
- target_configuration: equal Cs:I stoichiometry using I-127 and Cs-133
- statistical_data_mode: background_subtracted_excess

The statistical mode is provisional and unused by P3. No authoritative
observed/background/covariance provenance was supplied with the Flavor
migration, so statistics remains blocked.

## Input paths

Physics documents:

- F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/CEvNS-pyEFT Flavor 重构：问题处理优先级提示词.md
- F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/CEvNS_pyeFT_full_flavor_refactor_implementation_spec.md

References and attachments:

- PHASE1_SPLIT_REPORT.md
- data/responses/responses_all.json
- tests/reference_fast_split/csi2021_*.npy
- tests/reference_fast_split/csi2021_metadata.json

Repository files inspected:

- src/cevns_pyeft/experiments/base.py
- src/cevns_pyeft/experiments/registry.py
- src/cevns_pyeft/experiments/specs.py
- src/cevns_pyeft/experiments/coherent/sns.py
- src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py
- src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py
- src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py
- src/cevns_pyeft/rates/counts.py
- src/cevns_pyeft/rates/differential.py
- src/cevns_pyeft/sources/state.py
- schemas/experiment.schema.json
- tests/test_source_state_p2.py
- tests/test_rates_differential_flavor.py

No standalone CsI2021 experiment.yaml exists; the legacy dataset is registered
in Python.

## Experiment goal

- signal: canonical 3x3 Flavor Wilson prediction for CsI2021.
- slow: pass rho and particle_kind for every SNS component before integration.
- fast: frozen until P4.
- statistics: out of scope and blocked.
- validation: preserve legacy Slow totals and add state/component regressions.

## Observable axes

- E_nu: true incident energy, MeV at rates boundary, integrated out.
- E_R: true nuclear recoil, keV, exact two-body support.
- PE: reconstructed photoelectrons with edges
  [0.001,8.001,12.001,16.001,20.001,24.001,32.001,40.001,48.001,60.001].
- source_component: mu, e, mub, plus total.
- target: Cs133 and I127.

Expected outputs:

- counts_per_bin[mu|e|mub|total]: shape (9,), events/bin.
- counts_per_npe[mu|e|mub|total]: shape (9,), events/PE.
- target_flavor_counts_per_bin[component][target]: shape (9,).
- pe_bins: shape (10,).

## Supplied scalar parameters

| Quantity | Value | Unit | Repository source |
|---|---:|---|---|
| Baseline | 19.3 | m | SNS_DATASETS |
| N_POT | 3.198e23 | count | SNS_DATASETS |
| Yield r | 0.0848 | neutrinos/POT/component | SNS_DATASETS |
| Detector mass | 14.57 | kg | SNS_DATASETS/bin_events_csi |
| Integrated component flux | 5.793617637932336e14 | cm^-2 | current source formula |
| Physical prompt line | 29.792140909877446 | MeV | pion decay formula |
| Legacy rate prompt value | 29.65 | MeV | rates/counts.py |
| sin2thetaW default | 0.2387 | dimensionless | Slow API |
| Acceptance e | 0.848 | dimensionless | DEFAULT_ACCEPTANCE |
| Acceptance mu | 0.997 | dimensionless | DEFAULT_ACCEPTANCE |
| Acceptance mub | 0.848 | dimensionless | DEFAULT_ACCEPTANCE |
| Efficiency a,b,c,d | 1.32045,0.285979,10.8646,-0.3333 | mixed PE model | CsI2021EfficiencyParams |
| I/Cs mass weights | 127/260, 133/260 | dimensionless | combine_equal_stoichiometry |

The physical/legacy prompt-energy difference is preserved in P3 and not
silently corrected.

## Supplied formulas and tables

- Flux normalization: r N_POT/(4 pi L_cm^2), unit cm^-2.
- Delayed nu_e Michel spectrum: 192 E^2(1/2-E/m_mu)/m_mu^3.
- Delayed antinu_mu spectrum: 64 E^2(3/4-E/m_mu)/m_mu^3.
- Flavor contraction: dσ/dER = Tr[rho(E_nu) K(E_nu,ER)].
- Efficiency: a/(1+exp[-b(PE-c)])+d, clamped at zero.
- Cs/I combination: (133 Cs + 127 I)/260.
- PE stochastic response: existing p_smearing_csi.
- Frozen Fast reference: full kernel shape (3,3,8,22,22,9); protected and not
  authoritative for P3 Flavor correctness.
- No new numerical table is materialized in Phase 0.

## Source definition

- Type: time-integrated stopped-pion SNS.
- Prompt mu: rho_mu, particle_kind nu, monoenergetic line.
- Delayed e: rho_e, particle_kind nu, Michel continuum.
- Delayed mub: rho_mu, particle_kind antinu, Michel continuum.
- Configured tabulation grid: 0.001–300 MeV; physical mask: 0.001–56 MeV.
- Default interpolation: 200-point linear interpolation, node-wise nonnegative
  clipping and zero outside tabulation.
- Each component uses NTimeIntegratedFlux_cm^-2.
- Prompt is separate from continuous spectra.

As in CsI2017, interpolation can taper inside the final physical-support cell.
Exact source-boundary correction is outside P3.

Physical checks:

- finite for finite input: yes.
- nonnegative at tabulation: yes.
- exact zero outside physical support: not guaranteed inside a boundary cell.
- correct integrated normalization: analytic intent; discretized regression needed.
- uncertainties: not represented.

## Detector and target definition

- Detector: one 14.57 kg CsI[Na] module.
- Exposure: run-integrated flux multiplied once by detector mass.
- Material: equal Cs:I stoichiometry.
- Isotopes/response keys: Cs-133 -> Cs133; I-127 -> I.
- Nucleus mass convention: A times 1.6605390666e-27 kg.
- Verified records: Cs133 (A=133,Z=55,N=78,J=3.5);
  I (A=127,Z=53,N=74,J=2.5).

## Theory, kinematics and cross section

- Wilson basis: 22 canonical LeftKey operators with value shape (3,3).
- Flavor order: e, mu, tau; row final, column initial.
- Outgoing flavor is summed into K=C†C.
- SM is c_SM I3.
- rho is dimensionless; differential output is cm^2/keV.
- E_R is keV, E_nu is MeV at the rate API, and core quantities are GeV.
- differential_cross_section_nn supplies exact support and explicit particle metadata.
- counts.py currently uses an approximate pre-mask only for grid reduction.

## Detector response

- Mean PE relation is contained in the existing p_smearing_csi model.
- Stochastic response: p_smearing_csi.
- Efficiency: CsI2021 analytic logistic-like model, clamped at zero.
- Binning: nine irregular PE bins.
- Source acceptance is applied after per-component target combination.
- Flavor physics must end before this scalar layer.

## Slow counts

Integration chain:

source flux/state -> Flavor kernel -> Tr[rho K] -> E_nu integration ->
nuclei/kg -> recoil-to-PE smearing -> efficiency -> PE bins ->
Cs/I combination -> source acceptance.

- Integration order: E_nu at E_R, E_R/PE response, PE sub-bin integration.
- Defaults: n_er=21, n_enu=120, n_pe_bin=8, pe_step=3.
- Axes: source component, target, PE bin.
- Units: events/bin and events/PE.
- Legacy small-grid total: 773.8789850850715 from PHASE1_SPLIT_REPORT.md.
- Reference arrays and tolerances must not be changed to force a pass.

## Fast counts

The existing scalar N=c†Hc representation has stored full shape
(3,3,8,22,22,9). Flavor Fast use is blocked until P4 defines
Tr[rho C_I†C_J], tensor reconstruction and storage compatibility. P3 protects
all Fast source and reference files.

## Statistical data

- Primary mode: background_subtracted_excess, provisional and unused in P3.
- Observed/background/covariance/nuisance/test-statistic provenance is missing.
- Phase 9 is blocked; no Poisson interpretation is inferred.

## Missing information

- ANTI-NU AUDIT: blocks later sign corrections, not backward-equivalent P3.
- Flavor Fast contract: blocks P4/Phase 8 only.
- Authoritative statistics provenance: blocks Phase 9 only.
- Exact source boundary and prompt-energy resolution: separate physics audit.

## Current achievable implementation level

SLOW_PLANNED

