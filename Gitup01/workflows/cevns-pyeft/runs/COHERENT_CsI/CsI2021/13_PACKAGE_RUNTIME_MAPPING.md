# Package → Runtime 逐项映射

本任务的数值权威为 revision 2 的三份输入与 wheel 01。同期通用 Loader 接入后形成的
revision 3 独立保留，不能借其新的模型状态文字追认先前计算。105 个标量值和 23 个数组
是否相同由版本桥接审计证明；物理和统计 fingerprint 仍按各自实际实现记录。

算法只允许显式绑定；数学字符串用于审计，不执行 eval/exec，也不动态导入 YAML 指定模块。
固定常量/LEC 在 adapter 中与现有引擎核对，未消费快照明确排除。完整机器清单：
[package_to_runtime_mapping_final.json](../../../../../outputs/csi2021_package_execution_20261104/package_to_runtime_mapping_final.json)。

## 17 个模型

| model_id | 本次实际消费者 |
| --- | --- |
| sns_fluence_legacy_v1 | read_package: derived fluence identity check; source arrays already include POT/yield/geometry |
| sns_michel_tabulation_legacy_v1 | PackedSource.for_run: interpolate NPZ continuum; generation metadata validated, no resampling from legacy source |
| sns_prompt_line_v1 | PackedSource.for_run -> FluenceLine: YAML prompt energy and integrated fluence |
| sns_fixed_state_v1 | PackedState -> IncidentStateBatch / NeutrinoState: NPZ density matrix and explicit particle label |
| csi_target_inventory_v1 | PackagePreparation -> TargetInventory / TargetIsotope; derived mass/inventory consistency checked |
| li2026_sm_left_v1 | Li2026LegacyInteraction -> rates.differential._sm_left_dim6; GF fixed-contract check, sin2thetaW from TheoryPoint |
| li2026_matching_v1 | Li2026LegacyInteraction -> left_to_ci; active LECs validated against the existing engine |
| elastic_kinematics_v1 | ElasticKinematics -> theory.kinematics; same A*AMU_GEV kinematic mass |
| nuclear_np_polynomial_v1 | CsIPackage.responses -> ResponseW.W_np; seven arrays for each isotope |
| li2026_R_W_kernel_v1 | flavor_kernel_onebody_li2026; full response contraction, SigmaPDelta identically zero in engine |
| li2026_dsigma_v1 | Li2026LegacyInteraction.dsigma_dT -> DifferentialCrossSection, cm^2/keV |
| csi_quenching_legacy_v1 | CsIGammaResponse -> eee_quenching_csi, explicit four YAML coefficients |
| legacy_csi_gamma | CsIGammaResponse.density -> p_smearing_csi, explicit gamma_a/gamma_b |
| csi2021_logistic_legacy | CsI2021Efficiency(CsI2021EfficiencyParams), explicit a/b/c/d |
| legacy_component_acceptance | LegacyComponentAcceptance, source-to-legacy-label mapping checked |
| legacy_csi2021_v1 | PackageExecutor -> core.predict -> recoil_yield / legacy_density_fold; numerical settings validated |
| gaussian_two_pull_legacy_v1 | evaluate_package -> profile_gaussian_two_pull; counts divided by PE width once |

## 105 个标量

| parameter | value | unit | role | consumer slots |
| --- | --- | --- | --- | --- |
| source.baseline_m | 19.3 | m | direct_input | sns_fluence_legacy_v1:baseline_m |
| source.total_pot | 3.198e+23 | POT | direct_input | sns_fluence_legacy_v1:total_pot |
| source.yield_per_pot | 0.0848 | neutrinos/species/POT | direct_input | sns_fluence_legacy_v1:yield_per_pot |
| source.tabulation_min | 0.001 | MeV | runtime_control | sns_michel_tabulation_legacy_v1:tabulation_min |
| source.tabulation_max | 300.0 | MeV | runtime_control | sns_michel_tabulation_legacy_v1:tabulation_max |
| source.mask_min | 0.001 | MeV | runtime_control | sns_michel_tabulation_legacy_v1:mask_min |
| source.mask_max | 56.0 | MeV | runtime_control | sns_michel_tabulation_legacy_v1:mask_max |
| source.tabulation_nodes | 200 | 1 | runtime_control | sns_michel_tabulation_legacy_v1:tabulation_nodes |
| source.interpolation | True | boolean | runtime_control | sns_michel_tabulation_legacy_v1:interpolation |
| source.fluence_per_species | 579361763793233.6 | cm^-2 | derived | sns_michel_tabulation_legacy_v1:fluence; sns_prompt_line_v1:fluence |
| source.prompt_energy | 29.792140909877446 | MeV | derived | sns_prompt_line_v1:energy |
| source.integration_min | 0.0 | MeV | runtime_control | legacy_csi2021_v1:energy_min |
| source.integration_max | 52.827952069788324 | MeV | derived | legacy_csi2021_v1:energy_max |
| target.detector_mass | 14.57 | kg | direct_input | csi_target_inventory_v1:detector_mass |
| target.run_mass_metadata | 14.57 | kg | reference_only | excluded |
| target.atomic_mass_kg | 1.6605390666e-27 | kg | direct_input | csi_target_inventory_v1:atomic_mass |
| target.Cs133.A | 133 | 1 | direct_input | csi_target_inventory_v1:mass_number |
| target.Cs133.Z | 55 | 1 | reference_only | excluded |
| target.Cs133.N | 78 | 1 | reference_only | excluded |
| target.Cs133.J | 3.5 | 1 | reference_only | excluded |
| target.Cs133.T | 11.5 | 1 | reference_only | excluded |
| target.Cs133.b | 11.644334960750054 | GeV^-1 | direct_input | nuclear_np_polynomial_v1:oscillator_length |
| target.Cs133.isotopic_fraction | 1.0 | 1 | reference_only | excluded |
| target.Cs133.mass_fraction | 0.5115384615384615 | 1 | derived | csi_target_inventory_v1:mass_fraction |
| target.Cs133.mass_GeV | 123.88871579475999 | GeV | derived | csi_target_inventory_v1:mass_GeV; elastic_kinematics_v1:mass_GeV; li2026_dsigma_v1:mass_GeV |
| target.Cs133.mass_kg | 2.208516958578e-25 | kg | derived | csi_target_inventory_v1:mass_kg; legacy_csi2021_v1:isotope_mass_kg |
| target.Cs133.nuclei | 3.3747150347508443e+25 | nuclei | derived | legacy_component_acceptance:nuclei |
| nuclear.Cs133.exp_factor | -2.0 | 1 | direct_input | nuclear_np_polynomial_v1:exp_factor |
| target.I127.A | 127 | 1 | direct_input | csi_target_inventory_v1:mass_number |
| target.I127.Z | 53 | 1 | reference_only | excluded |
| target.I127.N | 74 | 1 | reference_only | excluded |
| target.I127.J | 2.5 | 1 | reference_only | excluded |
| target.I127.T | 10.5 | 1 | reference_only | excluded |
| target.I127.b | 11.566047952236252 | GeV^-1 | direct_input | nuclear_np_polynomial_v1:oscillator_length |
| target.I127.isotopic_fraction | 1.0 | 1 | reference_only | excluded |
| target.I127.mass_fraction | 0.48846153846153845 | 1 | derived | csi_target_inventory_v1:mass_fraction |
| target.I127.mass_GeV | 118.29975117244 | GeV | derived | csi_target_inventory_v1:mass_GeV; elastic_kinematics_v1:mass_GeV; li2026_dsigma_v1:mass_GeV |
| target.I127.mass_kg | 2.108884614582e-25 | kg | derived | csi_target_inventory_v1:mass_kg; legacy_csi2021_v1:isotope_mass_kg |
| target.I127.nuclei | 3.374715034750844e+25 | nuclei | derived | legacy_component_acceptance:nuclei |
| nuclear.I127.exp_factor | -2.0 | 1 | direct_input | nuclear_np_polynomial_v1:exp_factor |
| interaction.include_sm | True | boolean | direct_input | li2026_sm_left_v1:include_sm |
| interaction.sin2thetaW | 0.2387 | 1 | direct_input | li2026_sm_left_v1:sin2thetaW |
| constants.G_F | 1.1663787e-05 | GeV^-2 | direct_input | li2026_sm_left_v1:G_F |
| constants.alpha_em | 0.0072973525643 | 1 | direct_input | li2026_matching_v1:alpha_em |
| constants.m_mu | 0.10565837550000001 | GeV | direct_input | sns_michel_tabulation_legacy_v1:muon_mass; sns_prompt_line_v1:muon_mass |
| constants.m_e | 0.0005109989506900001 | GeV | direct_input | legacy_csi2021_v1:electron_mass |
| constants.m_pi_charged | 0.13957039000000002 | GeV | direct_input | sns_prompt_line_v1:pion_mass |
| constants.AMU_GEV | 0.93149410372 | GeV | direct_input | csi_target_inventory_v1:amu |
| constants.GEV_INV2_TO_CM2 | 3.893793721e-28 | cm^2/GeV^-2 | direct_input | li2026_dsigma_v1:conversion |
| lecs.g_A | 1.2754 | 1 | direct_input | li2026_matching_v1:g_A |
| lecs.Sigma_ud | 0.397 | 1 | unused_snapshot | excluded |
| lecs.B0_m_u | 0.0062 | GeV^2 | direct_input | li2026_matching_v1:B0_m_u |
| lecs.B0_m_d | 0.0133 | GeV^2 | direct_input | li2026_matching_v1:B0_m_d |
| lecs.L1 | 1.855 | 1 | direct_input | li2026_matching_v1:L1 |
| lecs.L2 | -1.017 | 1 | direct_input | li2026_matching_v1:L2 |
| lecs.L3 | 0.6377 | 1 | direct_input | li2026_matching_v1:L3 |
| lecs.L4 | -0.22 | 1 | direct_input | li2026_matching_v1:L4 |
| lecs.L5 | 0.00138 | GeV | direct_input | li2026_matching_v1:L5 |
| lecs.L6 | -0.00049 | GeV | direct_input | li2026_matching_v1:L6 |
| lecs.L7 | -0.0067599999999999995 | GeV | direct_input | li2026_matching_v1:L7 |
| lecs.L8 | 0.00265 | GeV | direct_input | li2026_matching_v1:L8 |
| lecs.L9 | 0.011519999999999999 | GeV | unused_snapshot | excluded |
| lecs.L10 | 0.024050000000000002 | GeV | unused_snapshot | excluded |
| lecs.L11 | -0.0177 | GeV | direct_input | li2026_matching_v1:L11 |
| lecs.L12 | -0.013900000000000001 | GeV | direct_input | li2026_matching_v1:L12 |
| lecs.L13 | -0.0504 | GeV | direct_input | li2026_matching_v1:L13 |
| lecs.L14 | -0.306 | GeV | direct_input | li2026_matching_v1:L14 |
| lecs.sigma_u_p | 0.0185 | GeV | direct_input | li2026_matching_v1:sigma_u_p |
| lecs.sigma_d_p | 0.036000000000000004 | GeV | direct_input | li2026_matching_v1:sigma_d_p |
| lecs.sigma_u_n | 0.0167 | GeV | direct_input | li2026_matching_v1:sigma_u_n |
| lecs.sigma_d_n | 0.039700000000000006 | GeV | direct_input | li2026_matching_v1:sigma_d_n |
| lecs.g1 | 1.0 | GeV | direct_input | li2026_matching_v1:g1 |
| lecs.g2 | 1.0 | GeV | direct_input | li2026_matching_v1:g2 |
| lecs.g3 | 1.0 | GeV | direct_input | li2026_matching_v1:g3 |
| lecs.g4 | 1.0 | GeV | direct_input | li2026_matching_v1:g4 |
| lecs.g5 | 1.0 | 1 | direct_input | li2026_matching_v1:g5 |
| lecs.g6 | 1.0 | 1 | direct_input | li2026_matching_v1:g6 |
| lecs.g7 | 1.0 | 1 | direct_input | li2026_matching_v1:g7 |
| lecs.g8 | 1.0 | 1 | direct_input | li2026_matching_v1:g8 |
| lecs.g9 | 1.0 | 1 | direct_input | li2026_matching_v1:g9 |
| lecs.m_u | 0.00216 | GeV | unused_snapshot | excluded |
| lecs.m_d | 0.00467 | GeV | unused_snapshot | excluded |
| lecs.m_pi | 0.13957039000000002 | GeV | derived | li2026_matching_v1:m_pi |
| lecs.m_N | 0.938918755685 | GeV | direct_input | li2026_matching_v1:m_N; li2026_R_W_kernel_v1:m_N |
| detector.quenching_q1 | 0.0554628 | 1 | direct_input | csi_quenching_legacy_v1:q1 |
| detector.quenching_q2 | 4.30681 | MeV^-1 | direct_input | csi_quenching_legacy_v1:q2 |
| detector.quenching_q3 | -111.707 | MeV^-2 | direct_input | csi_quenching_legacy_v1:q3 |
| detector.quenching_q4 | 840.384 | MeV^-3 | direct_input | csi_quenching_legacy_v1:q4 |
| detector.gamma_a | 0.0749 | keVee/PE | direct_input | legacy_csi_gamma:a0 |
| detector.gamma_b | 9.56 | keVee^-1 | direct_input | legacy_csi_gamma:b0 |
| detector.efficiency_a | 1.32045 | 1 | direct_input | csi2021_logistic_legacy:a |
| detector.efficiency_b | 0.285979 | PE^-1 | direct_input | csi2021_logistic_legacy:b |
| detector.efficiency_c | 10.8646 | PE | direct_input | csi2021_logistic_legacy:c |
| detector.efficiency_d | -0.3333 | 1 | direct_input | csi2021_logistic_legacy:d |
| detector.acceptance_e | 0.848 | 1 | direct_input | legacy_component_acceptance:e |
| detector.acceptance_mu | 0.997 | 1 | direct_input | legacy_component_acceptance:mu |
| detector.acceptance_mub | 0.848 | 1 | direct_input | legacy_component_acceptance:mub |
| numerics.n_er | 21 | 1 | runtime_control | legacy_csi2021_v1:n_er |
| numerics.n_enu | 120 | 1 | runtime_control | legacy_csi2021_v1:n_enu |
| numerics.n_observed_bin | 8 | 1 | runtime_control | legacy_csi2021_v1:n_observed_bin |
| numerics.observed_step | 3.0 | PE | runtime_control | legacy_csi2021_v1:observed_step |
| numerics.recoil_min_keV | 0.1 | keV | runtime_control | legacy_csi2021_v1:recoil_min_keV |
| statistics.sigma_alpha | 0.125 | 1 | direct_input | gaussian_two_pull_legacy_v1:sigma_alpha |
| statistics.sigma_beta | 0.35 | 1 | direct_input | gaussian_two_pull_legacy_v1:sigma_beta |
| statistics.sigma_floor | 1e-12 | counts/PE | direct_input | gaussian_two_pull_legacy_v1:sigma_floor |

## 23 个数组

| key | shape | dtype | unit | raw-C SHA256 |
| --- | --- | --- | --- | --- |
| nuclear_Cs133_Delta | [2, 2, 9] | float64 | 1 | dbcc3f3d159b595c0a70514d8f113945aa5e3a2e088fe3f9381e6f45162bc3f7 |
| nuclear_Cs133_M | [2, 2, 11] | float64 | 1 | 73797039414d80ec53f94a52c5d9e81569e75b2b4149e1328d2cfb37da1da33f |
| nuclear_Cs133_MPhiPP | [2, 2, 10] | float64 | 1 | 28b48a8230713a7e04c7ab583e3036b1af351c56a6c564e8d88fa25e6045c366 |
| nuclear_Cs133_PhiPP | [2, 2, 9] | float64 | 1 | 63a6e92e566d08120c268f20b848c71f34b7a1f24e5ec0e6d2f2c54131671a11 |
| nuclear_Cs133_PhiPT | [2, 2, 9] | float64 | 1 | 5f6b68a684bd61c13b275a4c29d3631abcf113766d7cf765bdde2d235cf209b5 |
| nuclear_Cs133_SigmaP | [2, 2, 11] | float64 | 1 | 31aff312b6f4f8be5c02b4c82e7b79b39ba0747d4d346e877b9c826402d36276 |
| nuclear_Cs133_SigmaPP | [2, 2, 11] | float64 | 1 | d1599a240a75ea9a983403027ffbe5bdaca1e5fe56b0a0f9f3995a3a73febba1 |
| nuclear_I127_Delta | [2, 2, 9] | float64 | 1 | 193b05d4872cc90b93215521fb4f7bfb06886111f35170ed8ae814f3392a395a |
| nuclear_I127_M | [2, 2, 11] | float64 | 1 | 970240f1eeb77336d2f9443318f38e4e91cd65d85e1cff41d4da11dd2d2e6880 |
| nuclear_I127_MPhiPP | [2, 2, 10] | float64 | 1 | 35acd70771c0a44f72a522b7b85d024ee975b10f7ae262d07d93b1220c6a85bb |
| nuclear_I127_PhiPP | [2, 2, 9] | float64 | 1 | 87dce648dd0a4a7c065f23f2ae62a2eb7fe1a05cf1b967f5695a3a81c55ed794 |
| nuclear_I127_PhiPT | [2, 2, 9] | float64 | 1 | 06424d332423cec2647dfcf7e4ad9d9c84e4df790b4833463766573650657638 |
| nuclear_I127_SigmaP | [2, 2, 11] | float64 | 1 | bfdcebe00860d152b91b055cd19279b473b5c86e7b11387afe568afeee3091d0 |
| nuclear_I127_SigmaPP | [2, 2, 11] | float64 | 1 | 51b422c18e677c821ad27d2d46a7650abb5110fb3181c2464b1579f98e2703f5 |
| observable_pe_edges | [10] | float64 | PE | 9f0cbf1cc1c957c0bddc43e6387a967b56111fb74185fc1ad77534204d021d1d |
| source_energy_MeV | [200] | float64 | MeV | 2725a0489524f57c25b709d07fc6abc58fed19f32f3edeeda58041bf61419e56 |
| source_fluence_e | [200] | float64 | cm^-2 MeV^-1 | 0e240d501763a71c5de1660d4494faeccc48cf3f034ceb672bad7ce25418ae84 |
| source_fluence_mub | [200] | float64 | cm^-2 MeV^-1 | d935a5bce5e9f801c8be6e4a8e0d10cd09131354bfd1873f46a48ee80c44c988 |
| state_rho_e | [3, 3] | complex128 | 1 | 34508bf5f58e2486bf1ecbd3c8a5bdbbf7fe665c1d146a6d346ce6e467451b1a |
| state_rho_mu | [3, 3] | complex128 | 1 | 5261df4870b6c2c76f3e705d27fe3739aac1799d8689b16288771f91369aa9ec |
| statistics_background | [9] | float64 | counts/PE | 2e15dca3e291d72439d779d4fbc4a14722c1d658cebee9b7871e599fc148e9fa |
| statistics_observed | [9] | float64 | counts/PE | c87dc2e9bb63ea96598194c6d85ada6dda9dc18243c129b1b5272b7831a9ef1b |
| statistics_uncertainty | [9] | float64 | counts/PE | 92330c750bf386b5a52db8f25c09bfc0e6c073b4392bc84da5e6d61ac10fe57a |

## 真实交接与失效

一次 `load_package_experiment` 产生同一个 PreparedExperiment：
`PackedInteraction._responses` 直接交给 `dsigma_dT`，`CsIGammaResponse`、效率和选择对象
直接交给 `core.predict`。报告不是第二套参数源，P07 不重新从旧 definition 构造输入。
物理输入/核响应/数值设置/实现变化使 Slow 和对应 Fast、P09/P10 失效；只变统计观测
保留物理 fingerprint，改变 analysis fingerprint。相同内容换路径可复用；内容哈希比路径优先。
MD 是派生审查材料，数值/模型不符会拒绝；已发布的两种说明文字仅按精确替换兼容。

