# Ar2020 — Physics Input

legacy implementation compatibility only; no new scientific confirmation

Status: DRAFT; human: NOT_REVIEWED. YAML/NPZ are machine authority; this document is a deterministic view.

## Parameters

| ID | Value | Unit | Role | Meaning | Consumers | Sources | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| source.baseline_m | 27.5 | m | direct_input | source.baseline_m; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.total_pot | 1.38e+23 | POT | direct_input | source.total_pot; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.yield_per_pot | 0.09 | neutrinos/species/POT | direct_input | source.yield_per_pot; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_min | 0.001 | MeV | runtime_control | source.tabulation_min; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_max | 300.0 | MeV | runtime_control | source.tabulation_max; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.mask_min | 0.001 | MeV | runtime_control | source.mask_min; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.mask_max | 56.0 | MeV | runtime_control | source.mask_max; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_nodes | 200 | 1 | runtime_control | source.tabulation_nodes; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.interpolation | True | boolean | runtime_control | source.interpolation; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| target.run_mass_metadata | 24.0 | kg | reference_only | target.run_mass_metadata; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| target.detector_mass | 24.0 | kg | direct_input | target.detector_mass; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.G_F | 1.1663787e-05 | GeV^-2 | direct_input | constants.G_F; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.alpha_em | 0.0072973525643 | 1 | direct_input | constants.alpha_em; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.m_mu | 0.10565837550000001 | GeV | direct_input | constants.m_mu; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.m_e | 0.0005109989506900001 | GeV | direct_input | constants.m_e; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.m_pi_charged | 0.13957039000000002 | GeV | direct_input | constants.m_pi_charged; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.AMU_GEV | 0.93149410372 | GeV | direct_input | constants.AMU_GEV; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| constants.GEV_INV2_TO_CM2 | 3.893793721e-28 | cm^2/GeV^-2 | direct_input | constants.GEV_INV2_TO_CM2; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g_A | 1.2754 | 1 | direct_input | lecs.g_A; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.Sigma_ud | 0.397 | 1 | unused_snapshot | lecs.Sigma_ud; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| lecs.B0_m_u | 0.0062 | GeV^2 | direct_input | lecs.B0_m_u; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.B0_m_d | 0.0133 | GeV^2 | direct_input | lecs.B0_m_d; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L1 | 1.855 | 1 | direct_input | lecs.L1; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L2 | -1.017 | 1 | direct_input | lecs.L2; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L3 | 0.6377 | 1 | direct_input | lecs.L3; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L4 | -0.22 | 1 | direct_input | lecs.L4; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L5 | 0.00138 | GeV | direct_input | lecs.L5; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L6 | -0.00049 | GeV | direct_input | lecs.L6; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L7 | -0.0067599999999999995 | GeV | direct_input | lecs.L7; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L8 | 0.00265 | GeV | direct_input | lecs.L8; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L9 | 0.011519999999999999 | GeV | unused_snapshot | lecs.L9; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| lecs.L10 | 0.024050000000000002 | GeV | unused_snapshot | lecs.L10; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| lecs.L11 | -0.0177 | GeV | direct_input | lecs.L11; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L12 | -0.013900000000000001 | GeV | direct_input | lecs.L12; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L13 | -0.0504 | GeV | direct_input | lecs.L13; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.L14 | -0.306 | GeV | direct_input | lecs.L14; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.sigma_u_p | 0.0185 | GeV | direct_input | lecs.sigma_u_p; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.sigma_d_p | 0.036000000000000004 | GeV | direct_input | lecs.sigma_d_p; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.sigma_u_n | 0.0167 | GeV | direct_input | lecs.sigma_u_n; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.sigma_d_n | 0.039700000000000006 | GeV | direct_input | lecs.sigma_d_n; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g1 | 1.0 | GeV | direct_input | lecs.g1; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g2 | 1.0 | GeV | direct_input | lecs.g2; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g3 | 1.0 | GeV | direct_input | lecs.g3; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g4 | 1.0 | GeV | direct_input | lecs.g4; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g5 | 1.0 | 1 | direct_input | lecs.g5; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g6 | 1.0 | 1 | direct_input | lecs.g6; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g7 | 1.0 | 1 | direct_input | lecs.g7; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g8 | 1.0 | 1 | direct_input | lecs.g8; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.g9 | 1.0 | 1 | direct_input | lecs.g9; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.m_u | 0.00216 | GeV | unused_snapshot | lecs.m_u; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| lecs.m_d | 0.00467 | GeV | unused_snapshot | lecs.m_d; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| lecs.m_pi | 0.13957039000000002 | GeV | direct_input | lecs.m_pi; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| lecs.m_N | 0.938918755685 | GeV | direct_input | lecs.m_N; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| target.atomic_mass_kg | 1.6605390666e-27 | kg | direct_input | target.atomic_mass_kg; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
| source.integration_min | 0.0 | MeV | runtime_control | source.integration_min; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.integration_max | 52.827952069788324 | MeV | derived | source.integration_max; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | PROJECT_DERIVED |
| source.line_energy | 29.792140909877446 | MeV | derived | source.line_energy; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | PROJECT_DERIVED |
| source.line_fluence | 130691199550501.83 | cm^-2 | derived | source.line_fluence; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Ar40.A | 40 | 1 | direct_input | target.Ar40.A; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
| target.Ar40.b | 9.831536784009149 | GeV^-1 | direct_input | target.Ar40.b; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| nuclear.Ar40.exp_factor | -2.0 | 1 | direct_input | nuclear.Ar40.exp_factor; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| target.Ar40.mass_GeV | 37.2597641488 | GeV | derived | target.Ar40.mass_GeV; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Ar40.mass_kg | 6.6421562664e-26 | kg | derived | target.Ar40.mass_kg; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Ar40.mass_fraction | 1.0 | 1 | derived | target.Ar40.mass_fraction; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Ar40.nuclei | 3.613284457248674e+26 | nuclei | derived | target.Ar40.nuclei; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| detector.efficiency_low | 0.0 | 1 | direct_input | detector.efficiency_low; legacy-code-derived | ['legacy_efficiency_curve_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.mean_linear | 0.246 | PE/keV | direct_input | detector.mean_linear; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.mean_quadratic | 0.00078 | PE/keV^2 | direct_input | detector.mean_quadratic; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.sigma_coefficient | 0.58 | PE^0.5 | direct_input | detector.sigma_coefficient; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| statistics.sigma_alpha | 0.12 | 1 | direct_input | statistics.sigma_alpha; legacy-code-derived | ['asymmetric_irls_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| statistics.sigma_beta | 0.146 | 1 | direct_input | statistics.sigma_beta; legacy-code-derived | ['asymmetric_irls_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| interaction.include_sm | True | boolean | direct_input | interaction.include_sm; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| interaction.sin2thetaW | 0.2387 | 1 | direct_input | interaction.sin2thetaW; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.slow.n_er | 21 | 1 | runtime_control | numerics.slow.n_er; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.slow.n_enu | 120 | 1 | runtime_control | numerics.slow.n_enu; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.slow.n_pe_bin | 8 | 1 | runtime_control | numerics.slow.n_pe_bin; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.fast.n_er | 21 | 1 | runtime_control | numerics.fast.n_er; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.fast.n_enu | 120 | 1 | runtime_control | numerics.fast.n_enu; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.fast.n_obs_sub | 8 | 1 | runtime_control | numerics.fast.n_obs_sub; legacy-code-derived | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.recoil_min_keV | 0.1 | keV | runtime_control | original recoil lower integration bound | ['observed_gaussian_legacy_v1'] | ['legacy'] | LEGACY_ONLY |

## Models and audit equations

### integrated_fluence_components_v1

preserve current integrated_fluence_components_v1

```text
fluence = declared continuum arrays + declared lines; no extra POT factor
```

| Variable | Unit |
| --- | --- |
| E | MeV |
| fluence | cm^-2 MeV^-1 |
| line_weight | cm^-2 |

Inputs: ['source.baseline_m', 'source.total_pot', 'source.yield_per_pot', 'source.tabulation_min', 'source.tabulation_max', 'source.mask_min', 'source.mask_max', 'source.tabulation_nodes', 'source.interpolation', 'source.integration_min', 'source.integration_max', 'source.line_energy', 'source.line_fluence']; resources: ['source_energy_MeV', 'rho_0', 'rho_1', 'source_fluence_1', 'rho_2', 'source_fluence_2']; dependencies: []
Contract: integrated_fluence_components.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### explicit_target_inventory_v1

preserve current explicit_target_inventory_v1

```text
sum_i(nuclei_i * mass_i_kg) = detector_mass_kg
```

| Variable | Unit |
| --- | --- |
| nuclei | nuclei |
| mass_i | kg |
| detector_mass | kg |

Inputs: ['target.detector_mass', 'target.atomic_mass_kg', 'target.Ar40.A', 'target.Ar40.mass_GeV', 'target.Ar40.mass_kg', 'target.Ar40.mass_fraction', 'target.Ar40.nuclei']; resources: []; dependencies: []
Contract: explicit_target_inventory.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### nuclear_polynomial_arrays_v1

preserve current nuclear_polynomial_arrays_v1

```text
W_ab(y)=exp(exp_factor*y)*sum_k coeff_abk*y**k
```

| Variable | Unit |
| --- | --- |
| W | 1 |
| y | 1 |
| coeff | 1 |
| b | GeV^-1 |

Inputs: ['target.Ar40.b', 'nuclear.Ar40.exp_factor']; resources: ['nuclear_Ar40_M', 'nuclear_Ar40_SigmaPP', 'nuclear_Ar40_SigmaP', 'nuclear_Ar40_PhiPP', 'nuclear_Ar40_PhiPT', 'nuclear_Ar40_Delta', 'nuclear_Ar40_MPhiPP']; dependencies: []
Contract: nuclear_polynomial_arrays.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### li2026_package_interaction_v1

preserve current li2026_package_interaction_v1

```text
dsigma=Tr(rho*K)*mA/(8*pi*E**2)*GeV_to_cm2*1e-6
```

| Variable | Unit |
| --- | --- |
| dsigma | cm^2/keV |
| rho | 1 |
| K | GeV^-2 |
| mass | GeV |
| E | GeV |

Inputs: ['constants.G_F', 'constants.alpha_em', 'constants.m_mu', 'constants.m_e', 'constants.m_pi_charged', 'constants.AMU_GEV', 'constants.GEV_INV2_TO_CM2', 'lecs.g_A', 'lecs.B0_m_u', 'lecs.B0_m_d', 'lecs.L1', 'lecs.L2', 'lecs.L3', 'lecs.L4', 'lecs.L5', 'lecs.L6', 'lecs.L7', 'lecs.L8', 'lecs.L11', 'lecs.L12', 'lecs.L13', 'lecs.L14', 'lecs.sigma_u_p', 'lecs.sigma_d_p', 'lecs.sigma_u_n', 'lecs.sigma_d_n', 'lecs.g1', 'lecs.g2', 'lecs.g3', 'lecs.g4', 'lecs.g5', 'lecs.g6', 'lecs.g7', 'lecs.g8', 'lecs.g9', 'lecs.m_pi', 'lecs.m_N', 'interaction.include_sm', 'interaction.sin2thetaW']; resources: []; dependencies: ['nuclear_polynomial_arrays_v1']
Contract: li2026_package_interaction.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### observed_gaussian_legacy_v1

preserve current observed_gaussian_legacy_v1

```text
mean=(linear+quadratic*T)*T; sigma=coefficient*sqrt(observed)
```

| Variable | Unit |
| --- | --- |
| T | keV |
| PE | PE |
| density | events/PE |
| counts | events/bin |

Inputs: ['detector.mean_linear', 'detector.mean_quadratic', 'detector.sigma_coefficient', 'numerics.slow.n_er', 'numerics.slow.n_enu', 'numerics.slow.n_pe_bin', 'numerics.fast.n_er', 'numerics.fast.n_enu', 'numerics.fast.n_obs_sub', 'numerics.recoil_min_keV']; resources: ['observable_edges']; dependencies: ['integrated_fluence_components_v1', 'explicit_target_inventory_v1', 'li2026_package_interaction_v1', 'legacy_efficiency_curve_v1']
Contract: observed_gaussian.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### asymmetric_irls_legacy_v1

preserve current asymmetric_irls_legacy_v1

```text
legacy asymmetric Gaussian IRLS; side selected from model residual
```

| Variable | Unit |
| --- | --- |
| signal | counts/bin |
| data | counts/bin |
| chi2 | 1 |
| alpha | 1 |
| beta | 1 |

Inputs: ['statistics.sigma_alpha', 'statistics.sigma_beta']; resources: ['statistics_observed', 'statistics_background', 'statistics_lower', 'statistics_upper']; dependencies: ['observed_gaussian_legacy_v1']
Contract: asymmetric_irls.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### legacy_efficiency_curve_v1

legacy efficiency: sorted unique PE, explicit left low/right last, strict threshold

```text
eff(x)=linear_interp(x,xp,fp); left=low; right=fp[-1]; x<=threshold gives low when declared
```

| Variable | Unit |
| --- | --- |
| x | PE |
| y | 1 |

Inputs: ['detector.efficiency_low']; resources: ['efficiency_energy', 'efficiency_values']; dependencies: []
Contract: legacy_efficiency_curve.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

## Resources

| Key | Unit | Shape | Dtype | Axes | Normalization | Meaning | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| source_energy_MeV | MeV | [200] | float64 | [{'name': 'energy', 'unit': 'MeV', 'rule': 'declared tabulation'}] | {'quantity_kind': 'coordinate', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | source_energy_MeV; legacy data snapshot | ['legacy'] |
| rho_0 | 1 | [3, 3] | complex128 | [{'name': 'flavor_row', 'unit': '1', 'values': ['e', 'mu', 'tau']}, {'name': 'flavor_column', 'unit': '1', 'values': ['e', 'mu', 'tau']}] | {'quantity_kind': 'density', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | rho_0; legacy data snapshot | ['legacy'] |
| rho_1 | 1 | [3, 3] | complex128 | [{'name': 'flavor_row', 'unit': '1', 'values': ['e', 'mu', 'tau']}, {'name': 'flavor_column', 'unit': '1', 'values': ['e', 'mu', 'tau']}] | {'quantity_kind': 'density', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | rho_1; legacy data snapshot | ['legacy'] |
| source_fluence_1 | cm^-2 MeV^-1 | [200] | float64 | [{'name': 'energy', 'unit': 'MeV', 'coordinate_ref': 'source_energy_MeV'}] | {'quantity_kind': 'integrated_detector_fluence_density', 'runtime_authority': 'array', 'included_factors': ['POT', 'yield', 'geometry'], 'runtime_factors': []} | source_fluence_1; legacy data snapshot | ['legacy'] |
| rho_2 | 1 | [3, 3] | complex128 | [{'name': 'flavor_row', 'unit': '1', 'values': ['e', 'mu', 'tau']}, {'name': 'flavor_column', 'unit': '1', 'values': ['e', 'mu', 'tau']}] | {'quantity_kind': 'density', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | rho_2; legacy data snapshot | ['legacy'] |
| source_fluence_2 | cm^-2 MeV^-1 | [200] | float64 | [{'name': 'energy', 'unit': 'MeV', 'coordinate_ref': 'source_energy_MeV'}] | {'quantity_kind': 'integrated_detector_fluence_density', 'runtime_authority': 'array', 'included_factors': ['POT', 'yield', 'geometry'], 'runtime_factors': []} | source_fluence_2; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_M | 1 | [2, 2, 7] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_M; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_SigmaPP | 1 | [2, 2, 0] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_SigmaPP; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_SigmaP | 1 | [2, 2, 0] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_SigmaP; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_PhiPP | 1 | [2, 2, 5] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_PhiPP; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_PhiPT | 1 | [2, 2, 0] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_PhiPT; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_Delta | 1 | [2, 2, 0] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_Delta; legacy data snapshot | ['legacy'] |
| nuclear_Ar40_MPhiPP | 1 | [2, 2, 6] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Ar40_MPhiPP; legacy data snapshot | ['legacy'] |
| efficiency_energy | PE | [80] | float64 | [{'name': 'PE', 'unit': 'PE', 'rule': 'legacy sorted/deduplicated'}] | {'quantity_kind': 'coordinate', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | efficiency_energy; legacy data snapshot | ['legacy'] |
| efficiency_values | 1 | [80] | float64 | [{'name': 'PE', 'unit': 'PE', 'coordinate_ref': 'efficiency_energy'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | efficiency_values; legacy data snapshot | ['legacy'] |
| observable_edges | PE | [13] | float64 | [{'name': 'edges', 'unit': 'PE', 'rule': 'exact legacy edges'}] | {'quantity_kind': 'coordinate', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | observable_edges; legacy data snapshot | ['legacy'] |
| statistics_observed | counts/bin | [12] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_observed; legacy data snapshot | ['legacy'] |
| statistics_background | counts/bin | [12] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_background; legacy data snapshot | ['legacy'] |
| statistics_lower | counts/bin | [12] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_lower; legacy data snapshot | ['legacy'] |
| statistics_upper | counts/bin | [12] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_upper; legacy data snapshot | ['legacy'] |

## Assembly and normalization

```json
{
  "profile": "observed_gaussian_legacy_v1",
  "source": {
    "energy_ref": "source_energy_MeV",
    "components": [
      {
        "id": "prompt_numu",
        "legacy_label": "mu",
        "particle_kind": "nu",
        "rho_ref": "rho_0",
        "continuum_ref": null,
        "lines": [
          {
            "id": "pion_DAR",
            "energy_ref": "source.line_energy",
            "fluence_ref": "source.line_fluence"
          }
        ]
      },
      {
        "id": "delayed_nue",
        "legacy_label": "e",
        "particle_kind": "nu",
        "rho_ref": "rho_1",
        "continuum_ref": "source_fluence_1",
        "lines": []
      },
      {
        "id": "delayed_numubar",
        "legacy_label": "mub",
        "particle_kind": "antinu",
        "rho_ref": "rho_2",
        "continuum_ref": "source_fluence_2",
        "lines": []
      }
    ],
    "integration_min_ref": "source.integration_min",
    "integration_max_ref": "source.integration_max",
    "baseline_ref": "source.baseline_m",
    "pot_ref": "source.total_pot",
    "yield_ref": "source.yield_per_pot"
  },
  "target": {
    "isotopes": [
      {
        "id": "Ar40",
        "responses": {
          "M": "nuclear_Ar40_M",
          "SigmaPP": "nuclear_Ar40_SigmaPP",
          "SigmaP": "nuclear_Ar40_SigmaP",
          "PhiPP": "nuclear_Ar40_PhiPP",
          "PhiPT": "nuclear_Ar40_PhiPT",
          "Delta": "nuclear_Ar40_Delta",
          "MPhiPP": "nuclear_Ar40_MPhiPP"
        }
      }
    ],
    "mass_ref": "target.detector_mass"
  },
  "interaction": {
    "model_id": "li2026_package_interaction_v1",
    "c10_mass_mode": "quark_mass_resolved"
  },
  "detector": {
    "profile": "observed_gaussian_legacy_v1",
    "efficiency_energy_ref": "efficiency_energy",
    "efficiency_values_ref": "efficiency_values",
    "efficiency_low_ref": "detector.efficiency_low",
    "efficiency_threshold_ref": null,
    "mean_linear_ref": "detector.mean_linear",
    "mean_quadratic_ref": "detector.mean_quadratic",
    "sigma_coefficient_ref": "detector.sigma_coefficient"
  },
  "statistics": {
    "model_id": "asymmetric_irls_legacy_v1",
    "observable_unit": "counts/bin",
    "observed_ref": "statistics_observed",
    "background_ref": "statistics_background",
    "lower_ref": "statistics_lower",
    "upper_ref": "statistics_upper",
    "sigma_alpha_ref": "statistics.sigma_alpha",
    "sigma_beta_ref": "statistics.sigma_beta"
  },
  "numerics": {
    "slow": {
      "n_er": "numerics.slow.n_er",
      "n_enu": "numerics.slow.n_enu",
      "n_pe_bin": "numerics.slow.n_pe_bin"
    },
    "fast": {
      "n_er": "numerics.fast.n_er",
      "n_enu": "numerics.fast.n_enu",
      "n_obs_sub": "numerics.fast.n_obs_sub"
    }
  }
}
```

## Capabilities

| Capability | State | Evidence | Blockers | Human |
| --- | --- | --- | --- | --- |
| signal | PASS | ['docs/PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md: Task10 numerical regression and two-file tests; legacy compatibility scope only', 'outputs/onboarding/task10/final-physics-junit.xml: numerical cases PASS; catalog import failure tracked and fixed separately'] | [] | NOT_REVIEWED |
| fast | PASS | ['docs/PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md: Task10 numerical regression and two-file tests; legacy compatibility scope only', 'outputs/onboarding/task10/final-physics-junit.xml: numerical cases PASS; catalog import failure tracked and fixed separately'] | [] | NOT_REVIEWED |
| legacy_statistics | PASS | ['docs/PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md: Task10 numerical regression and two-file tests; legacy compatibility scope only', 'outputs/onboarding/task10/final-physics-junit.xml: numerical cases PASS; catalog import failure tracked and fixed separately'] | [] | NOT_REVIEWED |
| official_likelihood | BLOCKED | [] | ['scientific source/convention review incomplete'] | NOT_REVIEWED |
| general_antineutrino_EFT | BLOCKED | [] | ['scientific source/convention review incomplete'] | NOT_REVIEWED |
| scientific_release | BLOCKED | [] | ['scientific source/convention review incomplete'] | NOT_REVIEWED |

## Provenance, missing and conflicts

| Source | Record |
| --- | --- |
| legacy | {'kind': 'legacy_implementation', 'version': 'legacy_12bin_modular_v1', 'definition_source_sha256': '38fcb00d763e98cb7be980554d5dc3922d3662d082256a924e4d1489760953f0', 'locator': 'current registered definition, response JSON, declared detector/statistical files; not official primary confirmation', 'declared_materials': [{'resource_id': 'responses', 'canonical_path': 'data/responses/responses_all.json', 'sha256': 'cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74', 'coordinate_contract': None}, {'resource_id': 'efficiency', 'canonical_path': 'data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt', 'sha256': 'f74f92bfdd116bcb2e14f31e3e98a24fb6a7e68458c4f647ca72357c78e55dd3', 'coordinate_contract': None}]} |

| Issue | State | Description | Blocks |
| --- | --- | --- | --- |
| science_review | MISSING | external nuclear source, antinu convention, official statistics and detector validity not fully reviewed | ['scientific_release', 'official_likelihood'] |

Archive SHA256: `2c44f2f9040472cfaffea6166cd178a239762e08813076de4ef2dd0c51a99244`. No equation text is executable.
