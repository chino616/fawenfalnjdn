# CsI2017 — Physics Input

legacy implementation compatibility only; no new scientific confirmation

Status: DRAFT; human: NOT_REVIEWED. YAML/NPZ are machine authority; this document is a deterministic view.

## Parameters

| ID | Value | Unit | Role | Meaning | Consumers | Sources | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
| source.baseline_m | 19.3 | m | direct_input | source.baseline_m; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.total_pot | 1.73e+23 | POT | direct_input | source.total_pot; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.yield_per_pot | 0.08 | neutrinos/species/POT | direct_input | source.yield_per_pot; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_min | 0.001 | MeV | runtime_control | source.tabulation_min; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_max | 300.0 | MeV | runtime_control | source.tabulation_max; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.mask_min | 0.001 | MeV | runtime_control | source.mask_min; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.mask_max | 56.0 | MeV | runtime_control | source.mask_max; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.tabulation_nodes | 200 | 1 | runtime_control | source.tabulation_nodes; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| source.interpolation | True | boolean | runtime_control | source.interpolation; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | LEGACY_ONLY |
| target.run_mass_metadata | 14.57 | kg | reference_only | target.run_mass_metadata; legacy-code-derived | [] | ['legacy'] | LEGACY_ONLY |
| target.detector_mass | 14.6 | kg | direct_input | target.detector_mass; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
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
| source.line_fluence | 295672959326670.6 | cm^-2 | derived | source.line_fluence; legacy-code-derived | ['integrated_fluence_components_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Cs133.A | 133 | 1 | direct_input | target.Cs133.A; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
| target.Cs133.b | 11.644334960750054 | GeV^-1 | direct_input | target.Cs133.b; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| nuclear.Cs133.exp_factor | -2.0 | 1 | direct_input | nuclear.Cs133.exp_factor; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| target.Cs133.mass_GeV | 123.88871579475999 | GeV | derived | target.Cs133.mass_GeV; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Cs133.mass_kg | 2.208516958578e-25 | kg | derived | target.Cs133.mass_kg; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Cs133.mass_fraction | 0.5115384615384615 | 1 | derived | target.Cs133.mass_fraction; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.Cs133.nuclei | 3.381663658707092e+25 | nuclei | derived | target.Cs133.nuclei; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.I127.A | 127 | 1 | direct_input | target.I127.A; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | LEGACY_ONLY |
| target.I127.b | 11.566047952236252 | GeV^-1 | direct_input | target.I127.b; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| nuclear.I127.exp_factor | -2.0 | 1 | direct_input | nuclear.I127.exp_factor; legacy-code-derived | ['nuclear_polynomial_arrays_v1'] | ['legacy'] | LEGACY_ONLY |
| target.I127.mass_GeV | 118.29975117244 | GeV | derived | target.I127.mass_GeV; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.I127.mass_kg | 2.108884614582e-25 | kg | derived | target.I127.mass_kg; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.I127.mass_fraction | 0.4884615384615384 | 1 | derived | target.I127.mass_fraction; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| target.I127.nuclei | 3.3816636587070914e+25 | nuclei | derived | target.I127.nuclei; legacy-code-derived | ['explicit_target_inventory_v1'] | ['legacy'] | PROJECT_DERIVED |
| detector.efficiency_low | 1e-10 | 1 | direct_input | detector.efficiency_low; legacy-code-derived | ['legacy_efficiency_curve_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.pe_per_keV | 1.17 | PE/keV | direct_input | detector.pe_per_keV; legacy-code-derived | ['deterministic_pe_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.slow_pe_nodes | 251 | 1 | runtime_control | detector.slow_pe_nodes; legacy-code-derived | ['deterministic_pe_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| detector.efficiency_threshold | 4.9 | PE | direct_input | detector.efficiency_threshold; legacy-code-derived | ['legacy_efficiency_curve_v1'] | ['legacy'] | LEGACY_ONLY |
| statistics.sigma_alpha | 0.28 | 1 | direct_input | statistics.sigma_alpha; legacy-code-derived | ['gaussian_one_pull_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| interaction.include_sm | True | boolean | direct_input | interaction.include_sm; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| interaction.sin2thetaW | 0.2387 | 1 | direct_input | interaction.sin2thetaW; legacy-code-derived | ['li2026_package_interaction_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.slow.n_enu | 120 | 1 | runtime_control | numerics.slow.n_enu; legacy-code-derived | ['deterministic_pe_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.fast.n_er | 251 | 1 | runtime_control | numerics.fast.n_er; legacy-code-derived | ['deterministic_pe_legacy_v1'] | ['legacy'] | LEGACY_ONLY |
| numerics.fast.n_enu | 120 | 1 | runtime_control | numerics.fast.n_enu; legacy-code-derived | ['deterministic_pe_legacy_v1'] | ['legacy'] | LEGACY_ONLY |

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

Inputs: ['target.detector_mass', 'target.atomic_mass_kg', 'target.Cs133.A', 'target.Cs133.mass_GeV', 'target.Cs133.mass_kg', 'target.Cs133.mass_fraction', 'target.Cs133.nuclei', 'target.I127.A', 'target.I127.mass_GeV', 'target.I127.mass_kg', 'target.I127.mass_fraction', 'target.I127.nuclei']; resources: []; dependencies: []
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

Inputs: ['target.Cs133.b', 'nuclear.Cs133.exp_factor', 'target.I127.b', 'nuclear.I127.exp_factor']; resources: ['nuclear_Cs133_M', 'nuclear_Cs133_SigmaPP', 'nuclear_Cs133_SigmaP', 'nuclear_Cs133_PhiPP', 'nuclear_Cs133_PhiPT', 'nuclear_Cs133_Delta', 'nuclear_Cs133_MPhiPP', 'nuclear_I127_M', 'nuclear_I127_SigmaPP', 'nuclear_I127_SigmaP', 'nuclear_I127_PhiPP', 'nuclear_I127_PhiPT', 'nuclear_I127_Delta', 'nuclear_I127_MPhiPP']; dependencies: []
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

### deterministic_pe_legacy_v1

preserve current deterministic_pe_legacy_v1

```text
PE = pe_per_keV*T; sampled dN/dPE folded by bin-edge interpolation
```

| Variable | Unit |
| --- | --- |
| T | keV |
| PE | PE |
| density | events/PE |
| counts | events/bin |

Inputs: ['detector.pe_per_keV', 'detector.slow_pe_nodes', 'numerics.slow.n_enu', 'numerics.fast.n_er', 'numerics.fast.n_enu']; resources: ['observable_edges']; dependencies: ['integrated_fluence_components_v1', 'explicit_target_inventory_v1', 'li2026_package_interaction_v1', 'legacy_efficiency_curve_v1']
Contract: deterministic_pe.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
Sources: ['legacy']; current registered definition + existing numerical consumers

### gaussian_one_pull_legacy_v1

preserve current gaussian_one_pull_legacy_v1

```text
chi2=sum((d-(1+a)*s)**2/sigma**2)+(a/sa)**2
```

| Variable | Unit |
| --- | --- |
| signal | counts/bin |
| data | counts/bin |
| chi2 | 1 |
| alpha | 1 |
| beta | 1 |

Inputs: ['statistics.sigma_alpha']; resources: ['statistics_observed', 'statistics_uncertainty', 'statistics_lower', 'statistics_upper', 'statistics_spectrum']; dependencies: ['deterministic_pe_legacy_v1']
Contract: gaussian_one_pull.v1; binding: BOUND_UNVERIFIED; domain: legacy sampled domain only; official validity not independently confirmed; boundary: preserve existing interpolation, support and clipping; no scientific correction
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

Inputs: ['detector.efficiency_low', 'detector.efficiency_threshold']; resources: ['efficiency_energy', 'efficiency_values']; dependencies: []
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
| nuclear_Cs133_M | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_M; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_SigmaPP | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_SigmaPP; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_SigmaP | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_SigmaP; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_PhiPP | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_PhiPP; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_PhiPT | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_PhiPT; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_Delta | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_Delta; legacy data snapshot | ['legacy'] |
| nuclear_Cs133_MPhiPP | 1 | [2, 2, 10] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_Cs133_MPhiPP; legacy data snapshot | ['legacy'] |
| nuclear_I127_M | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_M; legacy data snapshot | ['legacy'] |
| nuclear_I127_SigmaPP | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_SigmaPP; legacy data snapshot | ['legacy'] |
| nuclear_I127_SigmaP | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_SigmaP; legacy data snapshot | ['legacy'] |
| nuclear_I127_PhiPP | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_PhiPP; legacy data snapshot | ['legacy'] |
| nuclear_I127_PhiPT | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_PhiPT; legacy data snapshot | ['legacy'] |
| nuclear_I127_Delta | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_Delta; legacy data snapshot | ['legacy'] |
| nuclear_I127_MPhiPP | 1 | [2, 2, 10] | float64 | [{'name': 'nucleon_left', 'unit': '1', 'values': ['p', 'n']}, {'name': 'nucleon_right', 'unit': '1', 'values': ['p', 'n']}, {'name': 'polynomial_power', 'unit': '1', 'rule': 'ascending coefficient power'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | nuclear_I127_MPhiPP; legacy data snapshot | ['legacy'] |
| efficiency_energy | PE | [36] | float64 | [{'name': 'PE', 'unit': 'PE', 'rule': 'legacy sorted/deduplicated'}] | {'quantity_kind': 'coordinate', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | efficiency_energy; legacy data snapshot | ['legacy'] |
| efficiency_values | 1 | [36] | float64 | [{'name': 'PE', 'unit': 'PE', 'coordinate_ref': 'efficiency_energy'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | efficiency_values; legacy data snapshot | ['legacy'] |
| observable_edges | PE | [26] | float64 | [{'name': 'edges', 'unit': 'PE', 'rule': 'exact legacy edges'}] | {'quantity_kind': 'coordinate', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | observable_edges; legacy data snapshot | ['legacy'] |
| statistics_observed | counts/bin | [25] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_observed; legacy data snapshot | ['legacy'] |
| statistics_uncertainty | counts/bin | [25] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_uncertainty; legacy data snapshot | ['legacy'] |
| statistics_lower | counts/bin | [25] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_lower; legacy data snapshot | ['legacy'] |
| statistics_upper | counts/bin | [25] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | statistics_upper; legacy data snapshot | ['legacy'] |
| statistics_spectrum | counts/bin | [25] | float64 | [{'name': 'bin', 'unit': 'PE', 'edges_ref': 'observable_edges'}] | {'quantity_kind': 'table', 'runtime_authority': 'array', 'included_factors': [], 'runtime_factors': []} | legacy spectrum reference; not multiplied into signal prediction | ['legacy'] |

## Assembly and normalization

```json
{
  "profile": "deterministic_pe_legacy_v1",
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
        "id": "Cs133",
        "responses": {
          "M": "nuclear_Cs133_M",
          "SigmaPP": "nuclear_Cs133_SigmaPP",
          "SigmaP": "nuclear_Cs133_SigmaP",
          "PhiPP": "nuclear_Cs133_PhiPP",
          "PhiPT": "nuclear_Cs133_PhiPT",
          "Delta": "nuclear_Cs133_Delta",
          "MPhiPP": "nuclear_Cs133_MPhiPP"
        }
      },
      {
        "id": "I127",
        "responses": {
          "M": "nuclear_I127_M",
          "SigmaPP": "nuclear_I127_SigmaPP",
          "SigmaP": "nuclear_I127_SigmaP",
          "PhiPP": "nuclear_I127_PhiPP",
          "PhiPT": "nuclear_I127_PhiPT",
          "Delta": "nuclear_I127_Delta",
          "MPhiPP": "nuclear_I127_MPhiPP"
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
    "profile": "deterministic_pe_legacy_v1",
    "efficiency_energy_ref": "efficiency_energy",
    "efficiency_values_ref": "efficiency_values",
    "efficiency_low_ref": "detector.efficiency_low",
    "efficiency_threshold_ref": "detector.efficiency_threshold",
    "pe_per_keV_ref": "detector.pe_per_keV",
    "slow_pe_nodes_ref": "detector.slow_pe_nodes"
  },
  "statistics": {
    "model_id": "gaussian_one_pull_legacy_v1",
    "observable_unit": "counts/bin",
    "observed_ref": "statistics_observed",
    "uncertainty_ref": "statistics_uncertainty",
    "lower_ref": "statistics_lower",
    "upper_ref": "statistics_upper",
    "sigma_alpha_ref": "statistics.sigma_alpha",
    "spectrum_ref": "statistics_spectrum"
  },
  "numerics": {
    "slow": {
      "n_enu": "numerics.slow.n_enu"
    },
    "fast": {
      "n_er": "numerics.fast.n_er",
      "n_enu": "numerics.fast.n_enu"
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
| legacy | {'kind': 'legacy_implementation', 'version': 'legacy_25bin_modular_v1', 'definition_source_sha256': 'ef49d117163b51615f1ea0c0976029c455a26e61cf4270ff307b3df16dc62f7f', 'locator': 'current registered definition, response JSON, declared detector/statistical files; not official primary confirmation', 'declared_materials': [{'resource_id': 'responses', 'canonical_path': 'data/responses/responses_all.json', 'sha256': 'cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74', 'coordinate_contract': None}, {'resource_id': 'observation_schema', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json', 'sha256': '0edd4b8cc260781fd83bd7ea2820c98efdde04d3c7cde1584e86b66d46021645', 'coordinate_contract': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json'}, {'resource_id': 'efficiency', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt', 'sha256': 'ca1f47b5cdfb01fa87a323cf3ee4ee8245488b2e5b0529ecb0863d5bf09a9a7c', 'coordinate_contract': None}, {'resource_id': 'data', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_data.txt', 'sha256': 'f764accdd388bd161d6d53d3e7a01ff484c13d3dfc0fc1f61cc7fcb40f72cbd0', 'coordinate_contract': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json'}, {'resource_id': 'lower', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_lower.txt', 'sha256': 'c802772432ddd5288df5bb316d70a9736ec5b80c79d337ed050fa42d62c097bb', 'coordinate_contract': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json'}, {'resource_id': 'upper', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_upper.txt', 'sha256': 'db03d10cc5997f4b08948d71f04c72c88fd48365dc5cedae3b494b04f5853ad5', 'coordinate_contract': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json'}, {'resource_id': 'spectrum', 'canonical_path': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_spectrum.txt', 'sha256': '1584411458e0d48ebb9afb0400bd51e19a0e0208857b96edbea0d59aff710f95', 'coordinate_contract': 'data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json'}]} |

| Issue | State | Description | Blocks |
| --- | --- | --- | --- |
| science_review | MISSING | external nuclear source, antinu convention, official statistics and detector validity not fully reviewed | ['scientific_release', 'official_likelihood'] |

Archive SHA256: `0e8c86d5e3a3b4989778cfe80bb18efff0d739e68f0845a4a25bbd5c7b56a657`. No equation text is executable.
