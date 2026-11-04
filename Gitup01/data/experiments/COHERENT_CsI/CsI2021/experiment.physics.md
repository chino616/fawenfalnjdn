# COHERENT CsI[Na] — CsI2021 物理输入

> DRAFT / PARTIAL。参数角色、机器验证、Runtime 执行和人工科学接受分别记录。

## 身份与权威

legacy_9bin_input_description; audit-ready extraction, not official physics confirmation

YAML 是直接标量和模型规格权威；NPZ 是数组权威。derived 只读缓存必须与上游推导一致；materialized_derived_resource 只能在依赖指纹匹配时使用。本文由机器输入渲染，不能独立维护数值。

当前运行权威：package_yaml_npz。数学表达、源码位置和 symbolic_equations 都是审计信息，禁止 eval 或动态导入。

## 能力与人工审核

| 能力 | 已有引擎 | 就绪状态 | 旧回归证据 | Package Runtime | 人工审核 | 阻断项 |
| --- | --- | --- | --- | --- | --- | --- |
| legacy_prediction | AVAILABLE | LEGACY_ONLY | INTERNAL_REGRESSION_PASSED | NOT_RUN | NOT_REVIEWED | [] |
| package_backed_prediction | AVAILABLE | PACKAGE_VERIFIED | NOT_RUN | PASS | NOT_REVIEWED | [] |
| fast | AVAILABLE | PACKAGE_VERIFIED | INTERFACE_EXISTS | PASS | NOT_REVIEWED | [] |
| legacy_approximate_statistics | AVAILABLE | LEGACY_ONLY | INTERNAL_REGRESSION_PASSED | PASS | NOT_REVIEWED | ['statistics_semantics'] |
| official_likelihood | NOT_IMPLEMENTED | BLOCKED | NOT_RUN | NOT_RUN | NOT_REVIEWED | ['official_experiment_sources', 'statistics_semantics'] |
| general_antineutrino_EFT | RESTRICTED | BLOCKED | NOT_RUN | NOT_RUN | NOT_REVIEWED | ['antineutrino_kernel'] |
| scientific_release | NOT_IMPLEMENTED | BLOCKED | NOT_RUN | NOT_RUN | NOT_REVIEWED | ['official_experiment_sources', 'eft_primary_conventions', 'nuclear_source_audit', 'antineutrino_kernel', 'statistics_semantics', 'source_endpoint', 'detector_validity'] |

## 参数及真实消费者

每项 value/adopted_value 为当前采用值；原来源值来自项目代码或数据，不等同官方论文原值。派生关系只允许校验器中明列的审计运算，不能自由执行公式。reference_only/unused_snapshot 没有计算消费者、不进入 canonical 数值指纹；旧引擎仍可能因整体代码/元数据哈希变化而失效。

### source

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source.baseline_m | 19.3 | 19.3 | m | direct_input | 源到探测器距离；几何稀释只在注量中施加。 | sns_fluence_legacy_v1.baseline_m (resource_generation) | physical | ['definition'] :: CsI2021Settings.run; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.total_pot | 3.198e+23 | 3.198e+23 | POT | direct_input | 本运行累计 POT；已经承载时间积分。 | sns_fluence_legacy_v1.total_pot (resource_generation) | physical | ['definition'] :: CsI2021Settings.run; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.yield_per_pot | 0.0848 | 0.0848 | neutrinos/species/POT | direct_input | 每种 SNS 分量的发射数系数。 | sns_fluence_legacy_v1.yield_per_pot (resource_generation) | physical | ['definition'] :: CsI2021Settings.run; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.tabulation_min | 0.001 | 0.001 | MeV | runtime_control | SNS 线性插值表端点；不是积分端点。 | sns_michel_tabulation_legacy_v1.tabulation_min (resource_generation) | materialization | ['definition'] :: SNSRun.energy_tabulation; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.tabulation_max | 300.0 | 300.0 | MeV | runtime_control | SNS 线性插值表端点；不是积分端点。 | sns_michel_tabulation_legacy_v1.tabulation_max (resource_generation) | materialization | ['definition'] :: SNSRun.energy_tabulation; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.mask_min | 0.001 | 0.001 | MeV | runtime_control | 仅在生成表格节点时使用的旧程序掩码。 | sns_michel_tabulation_legacy_v1.mask_min (resource_generation) | materialization | ['definition'] :: SNSRun.node_support; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.mask_max | 56.0 | 56.0 | MeV | runtime_control | 仅在生成表格节点时使用的旧程序掩码。 | sns_michel_tabulation_legacy_v1.mask_max (resource_generation) | materialization | ['definition'] :: SNSRun.node_support; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.tabulation_nodes | 200 | 200 | 1 | runtime_control | SNS 等间距表节点数，含两端。 | sns_michel_tabulation_legacy_v1.tabulation_nodes (resource_generation) | materialization | ['definition'] :: SNSRun.num_points; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.interpolation | true | True | boolean | runtime_control | 采用线性插值的旧复现设置。 | sns_michel_tabulation_legacy_v1.interpolation (resource_generation) | materialization | ['definition'] :: SNSRun.interpolation; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.fluence_per_species | 579361763793233.6 | None | cm^-2 | derived | 每种分量的积分注量权重；连续谱未重新归一化。 | sns_michel_tabulation_legacy_v1.fluence (resource_generation); sns_prompt_line_v1.fluence (runtime) | physical | ['source'] :: _n_time_integrated_flux_cm2; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| source.prompt_energy | 29.792140909877446 | None | MeV | derived | 静止带电 pion 两体衰变的 prompt νμ 能量。 | sns_prompt_line_v1.energy (runtime) | physical | ['source'] :: build_neutrino_empirical_flux_sns:E0; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| source.integration_min | 0.0 | 0.0 | MeV | runtime_control | 连续谱积分网格下限；零能节点不送入截面。 | legacy_csi2021_v1.energy_min (runtime) | numerics | ['source_adapter'] :: SNSLegacySource.for_run; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| source.integration_max | 52.827952069788324 | None | MeV | derived | 包含电子质量的 muon DAR 积分上限。 | legacy_csi2021_v1.energy_max (runtime) | physical | ['differential'] :: emax_muon_dar_mev; project-derived/PROJECT_DERIVED; DRAFT/human=false |

### target

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target.detector_mass | 14.57 | 14.57 | kg | direct_input | 探测器总质量，只用于构造核数。 | csi_target_inventory_v1.detector_mass (runtime) | physical | ['definition'] :: CsI2021Settings.mass_kg; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.run_mass_metadata | 14.57 | 14.57 | kg | reference_only | 旧源配置中的质量元数据；实际 SNSSource 组装传零，不参与注量。 | 无计算消费者 | none | ['definition'] :: CsI2021Settings.run.mass_metadata_kg; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.atomic_mass_kg | 1.6605390666e-27 | 1.6605390666e-27 | kg | direct_input | 旧程序核数换算的原子质量常数。 | csi_target_inventory_v1.atomic_mass (runtime) | physical | ['recipes'] :: LEGACY_ATOMIC_MASS_KG; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.A | 133 | 133 | 1 | direct_input | 质量数 | csi_target_inventory_v1.mass_number (runtime) | physical | ['response_data'] :: nuclei/Cs133/basic/A; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.Z | 55 | 55 | 1 | reference_only | 质子数 | 无计算消费者 | none | ['response_data'] :: nuclei/Cs133/basic/Z; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.N | 78 | 78 | 1 | reference_only | 中子数 | 无计算消费者 | none | ['response_data'] :: nuclei/Cs133/basic/N; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.J | 3.5 | 3.5 | 1 | reference_only | 核自旋 | 无计算消费者 | none | ['response_data'] :: nuclei/Cs133/basic/J; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.T | 11.5 | 11.5 | 1 | reference_only | 源表记录的同位旋 | 无计算消费者 | none | ['response_data'] :: nuclei/Cs133/basic/T; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.b | 11.644334960750054 | 11.644334960750054 | GeV^-1 | direct_input | 谐振子长度；用于 y=(qb/2)^2 | nuclear_np_polynomial_v1.oscillator_length (runtime) | physical | ['response_data'] :: nuclei/Cs133/basic/b; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.isotopic_fraction | 1.0 | 1.0 | 1 | reference_only | 被建模元素中的同位素占比为一；实际材料丰度测量来源未登记。 | 无计算消费者 | none | ['assembly'] :: assemble_csi2021:single isotope per element; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.Cs133.mass_fraction | 0.5115384615384615 | None | 1 | derived | Cs:I=1:1 化学计量转成质量分数。 | csi_target_inventory_v1.mass_fraction (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.Cs133.mass_GeV | 123.88871579475999 | None | GeV | derived | 弹性运动学的 A*AMU_GEV 近似质量。 | csi_target_inventory_v1.mass_GeV (runtime); elastic_kinematics_v1.mass_GeV (runtime); li2026_dsigma_v1.mass_GeV (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.Cs133.mass_kg | 2.208516958578e-25 | None | kg | derived | 核数换算的 A*atomic_mass_kg 质量。 | csi_target_inventory_v1.mass_kg (runtime); legacy_csi2021_v1.isotope_mass_kg (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.Cs133.nuclei | 3.3747150347508443e+25 | None | nuclei | derived | 实际参与计算的靶核数。 | legacy_component_acceptance.nuclei (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.I127.A | 127 | 127 | 1 | direct_input | 质量数 | csi_target_inventory_v1.mass_number (runtime) | physical | ['response_data'] :: nuclei/I/basic/A; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.Z | 53 | 53 | 1 | reference_only | 质子数 | 无计算消费者 | none | ['response_data'] :: nuclei/I/basic/Z; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.N | 74 | 74 | 1 | reference_only | 中子数 | 无计算消费者 | none | ['response_data'] :: nuclei/I/basic/N; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.J | 2.5 | 2.5 | 1 | reference_only | 核自旋 | 无计算消费者 | none | ['response_data'] :: nuclei/I/basic/J; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.T | 10.5 | 10.5 | 1 | reference_only | 源表记录的同位旋 | 无计算消费者 | none | ['response_data'] :: nuclei/I/basic/T; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.b | 11.566047952236252 | 11.566047952236252 | GeV^-1 | direct_input | 谐振子长度；用于 y=(qb/2)^2 | nuclear_np_polynomial_v1.oscillator_length (runtime) | physical | ['response_data'] :: nuclei/I/basic/b; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.isotopic_fraction | 1.0 | 1.0 | 1 | reference_only | 被建模元素中的同位素占比为一；实际材料丰度测量来源未登记。 | 无计算消费者 | none | ['assembly'] :: assemble_csi2021:single isotope per element; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| target.I127.mass_fraction | 0.48846153846153845 | None | 1 | derived | Cs:I=1:1 化学计量转成质量分数。 | csi_target_inventory_v1.mass_fraction (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.I127.mass_GeV | 118.29975117244 | None | GeV | derived | 弹性运动学的 A*AMU_GEV 近似质量。 | csi_target_inventory_v1.mass_GeV (runtime); elastic_kinematics_v1.mass_GeV (runtime); li2026_dsigma_v1.mass_GeV (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.I127.mass_kg | 2.108884614582e-25 | None | kg | derived | 核数换算的 A*atomic_mass_kg 质量。 | csi_target_inventory_v1.mass_kg (runtime); legacy_csi2021_v1.isotope_mass_kg (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |
| target.I127.nuclei | 3.374715034750844e+25 | None | nuclei | derived | 实际参与计算的靶核数。 | legacy_component_acceptance.nuclei (runtime) | physical | ['assembly'] :: assemble_csi2021; project-derived/PROJECT_DERIVED; DRAFT/human=false |

### nuclear

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nuclear.Cs133.exp_factor | -2.0 | -2.0 | 1 | direct_input | 所有该核响应多项式共用的指数因子。 | nuclear_np_polynomial_v1.exp_factor (runtime) | physical | ['response_data'] :: nuclei/Cs133/exp_factor; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| nuclear.I127.exp_factor | -2.0 | -2.0 | 1 | direct_input | 所有该核响应多项式共用的指数因子。 | nuclear_np_polynomial_v1.exp_factor (runtime) | physical | ['response_data'] :: nuclei/I/exp_factor; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### interaction

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| interaction.include_sm | true | True | boolean | direct_input | 缺省 TheoryPoint 加入 SM 系数。 | li2026_sm_left_v1.include_sm (runtime) | physical | ['numerics'] :: TheoryPoint.include_sm; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| interaction.sin2thetaW | 0.2387 | 0.2387 | 1 | direct_input | 实验复现入口显式给定的弱混合角平方。 | li2026_sm_left_v1.sin2thetaW (runtime) | physical | ['definition'] :: ExperimentDefinition.reproduction_sin2thetaW; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### constants

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| constants.G_F | 1.1663787e-05 | 1.1663787e-05 | GeV^-2 | direct_input | Fermi 常数；记录当前公共常数版本的实际值。 | li2026_sm_left_v1.G_F (runtime) | physical | ['constants'] :: G_F; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.alpha_em | 0.0072973525643 | 0.0072973525643 | 1 | direct_input | 精细结构常数；记录当前公共常数版本的实际值。 | li2026_matching_v1.alpha_em (runtime) | physical | ['constants'] :: alpha_em; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.m_mu | 0.10565837550000001 | 0.10565837550000001 | GeV | direct_input | muon 质量；记录当前公共常数版本的实际值。 | sns_michel_tabulation_legacy_v1.muon_mass (resource_generation); sns_prompt_line_v1.muon_mass (derivation) | physical | ['constants'] :: m_mu; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.m_e | 0.0005109989506900001 | 0.0005109989506900001 | GeV | direct_input | 电子质量；记录当前公共常数版本的实际值。 | legacy_csi2021_v1.electron_mass (derivation) | physical | ['constants'] :: m_e; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.m_pi_charged | 0.13957039000000002 | 0.13957039000000002 | GeV | direct_input | 带电 pion 质量；记录当前公共常数版本的实际值。 | sns_prompt_line_v1.pion_mass (derivation) | physical | ['constants'] :: m_pi_charged; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.AMU_GEV | 0.93149410372 | 0.93149410372 | GeV | direct_input | 运动学原子质量常数；记录当前公共常数版本的实际值。 | csi_target_inventory_v1.amu (runtime) | physical | ['constants'] :: AMU_GEV; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| constants.GEV_INV2_TO_CM2 | 3.893793721e-28 | 3.893793721e-28 | cm^2/GeV^-2 | direct_input | 自然单位截面转换因子；记录当前公共常数版本的实际值。 | li2026_dsigma_v1.conversion (runtime) | physical | ['constants'] :: GEV_INV2_TO_CM2; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### lecs

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lecs.g_A | 1.2754 | 1.2754 | 1 | direct_input | 核子轴矢耦合，进入 c10 的 pion-pole 项。 | li2026_matching_v1.g_A (runtime) | physical | ['lecs'] :: Li2026LECs.g_A; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.Sigma_ud | 0.397 | 0.397 | 1 | unused_snapshot | 公共理论版本的轻夸克组合常数。 当前 matching 公式未直接使用，保留公共版本快照身份。 | 无计算消费者 | none | ['lecs'] :: Li2026LECs.Sigma_ud; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.B0_m_u | 0.0062 | 0.0062 | GeV^2 | direct_input | 手征常数 B0 与轻夸克质量的乘积，控制 c10 的 pion-pole 项；不是 B0 本身。 | li2026_matching_v1.B0_m_u (runtime) | physical | ['lecs'] :: Li2026LECs.B0_m_u; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.B0_m_d | 0.0133 | 0.0133 | GeV^2 | direct_input | 手征常数 B0 与轻夸克质量的乘积，控制 c10 的 pion-pole 项；不是 B0 本身。 | li2026_matching_v1.B0_m_d (runtime) | physical | ['lecs'] :: Li2026LECs.B0_m_d; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L1 | 1.855 | 1.855 | 1 | direct_input | 矢量/磁型匹配常数，进入 c6 与 dipole c12。 | li2026_matching_v1.L1 (runtime) | physical | ['lecs'] :: Li2026LECs.L1; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L2 | -1.017 | -1.017 | 1 | direct_input | 同位旋交叉矢量/磁型匹配常数，进入 c6。 | li2026_matching_v1.L2 (runtime) | physical | ['lecs'] :: Li2026LECs.L2; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L3 | 0.6377 | 0.6377 | 1 | direct_input | 核子轴矢匹配常数，进入 c2/c7。 | li2026_matching_v1.L3 (runtime) | physical | ['lecs'] :: Li2026LECs.L3; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L4 | -0.22 | -0.22 | 1 | direct_input | 轴矢同位旋混合匹配常数，进入 c2/c7。 | li2026_matching_v1.L4 (runtime) | physical | ['lecs'] :: Li2026LECs.L4; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L5 | 0.00138 | 0.00138 | GeV | direct_input | LNV tensor 型匹配常数，进入 c4/c8/c9。 | li2026_matching_v1.L5 (runtime) | physical | ['lecs'] :: Li2026LECs.L5; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L6 | -0.00049 | -0.00049 | GeV | direct_input | LNV tensor 型同位旋交叉常数，进入 c4/c8/c9。 | li2026_matching_v1.L6 (runtime) | physical | ['lecs'] :: Li2026LECs.L6; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L7 | -0.0067599999999999995 | -0.0067599999999999995 | GeV | direct_input | LNV tensor 型附加匹配常数，进入 c9。 | li2026_matching_v1.L7 (runtime) | physical | ['lecs'] :: Li2026LECs.L7; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L8 | 0.00265 | 0.00265 | GeV | direct_input | LNV tensor 型同位旋交叉附加常数，进入 c9。 | li2026_matching_v1.L8 (runtime) | physical | ['lecs'] :: Li2026LECs.L8; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L9 | 0.011519999999999999 | 0.011519999999999999 | GeV | unused_snapshot | 公共理论版本保留的 LEC，当前 matching 不消费。 当前 matching 公式未直接使用，保留公共版本快照身份。 | 无计算消费者 | none | ['lecs'] :: Li2026LECs.L9; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L10 | 0.024050000000000002 | 0.024050000000000002 | GeV | unused_snapshot | 公共理论版本保留的 LEC，当前 matching 不消费。 当前 matching 公式未直接使用，保留公共版本快照身份。 | 无计算消费者 | none | ['lecs'] :: Li2026LECs.L10; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L11 | -0.0177 | -0.0177 | GeV | direct_input | 轻夸克 pseudoscalar 的局域匹配常数，进入 c10。 | li2026_matching_v1.L11 (runtime) | physical | ['lecs'] :: Li2026LECs.L11; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L12 | -0.013900000000000001 | -0.013900000000000001 | GeV | direct_input | 轻夸克 pseudoscalar 的同位旋交叉局域常数，进入 c10。 | li2026_matching_v1.L12 (runtime) | physical | ['lecs'] :: Li2026LECs.L12; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L13 | -0.0504 | -0.0504 | GeV | direct_input | gluonic scalar 算符匹配到 c3 的常数。 | li2026_matching_v1.L13 (runtime) | physical | ['lecs'] :: Li2026LECs.L13; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.L14 | -0.306 | -0.306 | GeV | direct_input | gluonic pseudoscalar 算符匹配到 c10 的常数。 | li2026_matching_v1.L14 (runtime) | physical | ['lecs'] :: Li2026LECs.L14; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.sigma_u_p | 0.0185 | 0.0185 | GeV | direct_input | 核子中指定轻夸克的标量 sigma term，进入维七标量算符到 c3 的匹配。 | li2026_matching_v1.sigma_u_p (runtime) | physical | ['lecs'] :: Li2026LECs.sigma_u_p; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.sigma_d_p | 0.036000000000000004 | 0.036000000000000004 | GeV | direct_input | 核子中指定轻夸克的标量 sigma term，进入维七标量算符到 c3 的匹配。 | li2026_matching_v1.sigma_d_p (runtime) | physical | ['lecs'] :: Li2026LECs.sigma_d_p; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.sigma_u_n | 0.0167 | 0.0167 | GeV | direct_input | 核子中指定轻夸克的标量 sigma term，进入维七标量算符到 c3 的匹配。 | li2026_matching_v1.sigma_u_n (runtime) | physical | ['lecs'] :: Li2026LECs.sigma_u_n; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.sigma_d_n | 0.039700000000000006 | 0.039700000000000006 | GeV | direct_input | 核子中指定轻夸克的标量 sigma term，进入维七标量算符到 c3 的匹配。 | li2026_matching_v1.sigma_d_n (runtime) | physical | ['lecs'] :: Li2026LECs.sigma_d_n; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g1 | 1.0 | 1.0 | GeV | direct_input | 维七矢量算符到 c1 的直接匹配常数。 | li2026_matching_v1.g1 (runtime) | physical | ['lecs'] :: Li2026LECs.g1; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g2 | 1.0 | 1.0 | GeV | direct_input | 维七矢量算符到 c1 的同位旋交叉匹配常数。 | li2026_matching_v1.g2 (runtime) | physical | ['lecs'] :: Li2026LECs.g2; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g3 | 1.0 | 1.0 | GeV | direct_input | 维七轴矢算符到 c11 的直接匹配常数。 | li2026_matching_v1.g3 (runtime) | physical | ['lecs'] :: Li2026LECs.g3; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g4 | 1.0 | 1.0 | GeV | direct_input | 维七轴矢算符到 c11 的同位旋交叉匹配常数。 | li2026_matching_v1.g4 (runtime) | physical | ['lecs'] :: Li2026LECs.g4; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g5 | 1.0 | 1.0 | 1 | direct_input | 维八导数算符到 c13 的直接匹配常数。 | li2026_matching_v1.g5 (runtime) | physical | ['lecs'] :: Li2026LECs.g5; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g6 | 1.0 | 1.0 | 1 | direct_input | 维八导数算符到 c13 的同位旋交叉匹配常数。 | li2026_matching_v1.g6 (runtime) | physical | ['lecs'] :: Li2026LECs.g6; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g7 | 1.0 | 1.0 | 1 | direct_input | 维八轴矢导数算符到 c14 的直接匹配常数。 | li2026_matching_v1.g7 (runtime) | physical | ['lecs'] :: Li2026LECs.g7; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g8 | 1.0 | 1.0 | 1 | direct_input | 维八轴矢导数算符到 c14 的同位旋交叉匹配常数。 | li2026_matching_v1.g8 (runtime) | physical | ['lecs'] :: Li2026LECs.g8; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.g9 | 1.0 | 1.0 | 1 | direct_input | 维八 gluonic 算符到 c13 的匹配常数。 | li2026_matching_v1.g9 (runtime) | physical | ['lecs'] :: Li2026LECs.g9; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.m_u | 0.00216 | 0.00216 | GeV | unused_snapshot | 公共理论版本的 up 夸克质量。 当前 matching 公式未直接使用，保留公共版本快照身份。 | 无计算消费者 | none | ['lecs'] :: Li2026LECs.m_u; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.m_d | 0.00467 | 0.00467 | GeV | unused_snapshot | 公共理论版本的 down 夸克质量。 当前 matching 公式未直接使用，保留公共版本快照身份。 | 无计算消费者 | none | ['lecs'] :: Li2026LECs.m_d; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.m_pi | 0.13957039000000002 | 0.13957039000000002 | GeV | derived | pion-pole 分母所用的带电 pion 质量。 | li2026_matching_v1.m_pi (runtime) | physical | ['lecs'] :: Li2026LECs.m_pi; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| lecs.m_N | 0.938918755685 | 0.938918755685 | GeV | direct_input | 核子平均质量，进入粒子响应与 dipole/pion-pole 匹配。 | li2026_matching_v1.m_N (runtime); li2026_R_W_kernel_v1.m_N (runtime) | physical | ['lecs'] :: Li2026LECs.m_N; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### detector

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| detector.quenching_q1 | 0.0554628 | 0.0554628 | 1 | direct_input | 按一至四次幂顺序的 quenching 系数 q1；输入数值以 MeVnr 表示。 | csi_quenching_legacy_v1.q1 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.quenching; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.quenching_q2 | 4.30681 | 4.30681 | MeV^-1 | direct_input | 按一至四次幂顺序的 quenching 系数 q2；输入数值以 MeVnr 表示。 | csi_quenching_legacy_v1.q2 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.quenching; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.quenching_q3 | -111.707 | -111.707 | MeV^-2 | direct_input | 按一至四次幂顺序的 quenching 系数 q3；输入数值以 MeVnr 表示。 | csi_quenching_legacy_v1.q3 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.quenching; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.quenching_q4 | 840.384 | 840.384 | MeV^-3 | direct_input | 按一至四次幂顺序的 quenching 系数 q4；输入数值以 MeVnr 表示。 | csi_quenching_legacy_v1.q4 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.quenching; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.gamma_a | 0.0749 | 0.0749 | keVee/PE | direct_input | Gamma 参数 a0；均值 PE=Eee/a0。 | legacy_csi_gamma.a0 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.gamma_a; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.gamma_b | 9.56 | 9.56 | keVee^-1 | direct_input | Gamma 参数 b0；shape=1+b0*Eee。 | legacy_csi_gamma.b0 (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.gamma_b; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.efficiency_a | 1.32045 | 1.32045 | 1 | direct_input | logistic 振幅 | csi2021_logistic_legacy.a (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.efficiency:(a,b,c,d); legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.efficiency_b | 0.285979 | 0.285979 | PE^-1 | direct_input | logistic 陡度 | csi2021_logistic_legacy.b (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.efficiency:(a,b,c,d); legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.efficiency_c | 10.8646 | 10.8646 | PE | direct_input | logistic 中心 | csi2021_logistic_legacy.c (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.efficiency:(a,b,c,d); legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.efficiency_d | -0.3333 | -0.3333 | 1 | direct_input | logistic 常数偏移 | csi2021_logistic_legacy.d (runtime) | physical | ['detector_defaults'] :: CsIResponseDefaults.efficiency:(a,b,c,d); legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.acceptance_e | 0.848 | 0.848 | 1 | direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 | legacy_component_acceptance.e (runtime) | physical | ['detector_defaults'] :: CSI_COMPONENT_ACCEPTANCE; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.acceptance_mu | 0.997 | 0.997 | 1 | direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 | legacy_component_acceptance.mu (runtime) | physical | ['detector_defaults'] :: CSI_COMPONENT_ACCEPTANCE; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| detector.acceptance_mub | 0.848 | 0.848 | 1 | direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 | legacy_component_acceptance.mub (runtime) | physical | ['detector_defaults'] :: CSI_COMPONENT_ACCEPTANCE; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### numerics

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numerics.n_er | 21 | 21 | 1 | runtime_control | 每核素反冲网格节点数；线性且含端点。 | legacy_csi2021_v1.n_er (runtime) | numerics | ['numerics'] :: IntegrationSettings/n_er; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| numerics.n_enu | 120 | 120 | 1 | runtime_control | 连续谱能量网格节点数；各反冲只保留运动学允许节点。 | legacy_csi2021_v1.n_enu (runtime) | numerics | ['numerics'] :: IntegrationSettings/n_enu; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| numerics.n_observed_bin | 8 | 8 | 1 | runtime_control | 每 PE bin 子网格节点数；含端点。 | legacy_csi2021_v1.n_observed_bin (runtime) | numerics | ['numerics'] :: IntegrationSettings/n_observed_bin; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| numerics.observed_step | 3.0 | 3.0 | PE | runtime_control | 先采样 PE 密度的等间距步长。 | legacy_csi2021_v1.observed_step (runtime) | numerics | ['numerics'] :: IntegrationSettings/observed_step; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| numerics.recoil_min_keV | 0.1 | 0.1 | keV | runtime_control | 实际反冲网格下限。 | legacy_csi2021_v1.recoil_min_keV (runtime) | numerics | ['numerics'] :: IntegrationSettings/recoil_min_keV; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

### statistics

| 参数 | 采用值 | 来源原值 | 单位 | 角色 | 物理意义 | 真实消费者（阶段） | 指纹范围 | 来源与状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| statistics.sigma_alpha | 0.125 | 0.125 | 1 | direct_input | 信号归一化 Gaussian pull 的宽度。 | gaussian_two_pull_legacy_v1.sigma_alpha (runtime) | analysis | ['definition'] :: StatisticsDefinition.signal_sigma; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| statistics.sigma_beta | 0.35 | 0.35 | 1 | direct_input | 背景归一化 Gaussian pull 的宽度。 | gaussian_two_pull_legacy_v1.sigma_beta (runtime) | analysis | ['definition'] :: StatisticsDefinition.background_sigma; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |
| statistics.sigma_floor | 1e-12 | 1e-12 | counts/PE | direct_input | 对逐箱误差的下限裁剪；当前输入均大于下限。 | gaussian_two_pull_legacy_v1.sigma_floor (runtime) | analysis | ['profiling'] :: profile_gaussian_two_pull:sig; legacy-code-derived/SOURCE_EXTRACTED; DRAFT/human=false |

## 派生量和预计算归一化

| 派生参数 | 只读推导规格 | 依赖指纹 |
| --- | --- | --- |
| source.fluence_per_species | spherical_fluence.v1 ['source.yield_per_pot', 'source.total_pot', 'source.baseline_m'] | 25f031b0bc3059d414987a7639e0dc131b795fc7817201a6861a5091bed149a2 |
| source.prompt_energy | pion_line_energy.v1 ['constants.m_pi_charged', 'constants.m_mu'] | ebd99e5b9be89984a55eb1634ed4892ecf05d644c7093137b59f24be2928279d |
| source.integration_max | muon_dar_endpoint.v1 ['constants.m_mu', 'constants.m_e'] | 6478a71b920e00ef0843959dbcf196c2eb208543accbb30167a7fcb258acf089 |
| target.Cs133.mass_fraction | mass_fraction.v1 ['target.Cs133.A', 'target.Cs133.A', 'target.I127.A'] | c85c8d23c5057aac3e7c141446b470835bc324d8e380af092618141e439d11e7 |
| target.Cs133.mass_GeV | product.v1 ['target.Cs133.A', 'constants.AMU_GEV'] | 81c5a501ac2c76ba4871acd09a21dc9fea377f4a028af2b00430f74cb7d56ab1 |
| target.Cs133.mass_kg | product.v1 ['target.Cs133.A', 'target.atomic_mass_kg'] | 253848272c04364d1066a45491a0bd55b026cdec74aaba04b696ca2a70ce4337 |
| target.Cs133.nuclei | nucleus_inventory.v1 ['target.detector_mass', 'target.Cs133.mass_fraction', 'target.Cs133.mass_kg'] | 7d282d51ad66e9a48963f10de08568e94b3316ad69f279c0d29ff7480a073d95 |
| target.I127.mass_fraction | mass_fraction.v1 ['target.I127.A', 'target.Cs133.A', 'target.I127.A'] | f39e77c348bb9117eaa67bdbc13129d2cdec5c79d23da9aa5f686663c817b869 |
| target.I127.mass_GeV | product.v1 ['target.I127.A', 'constants.AMU_GEV'] | d86dbeaa5cf5b360fbc108b4e9a6753c3ad3e91ea227cf1876233c5d238d51bb |
| target.I127.mass_kg | product.v1 ['target.I127.A', 'target.atomic_mass_kg'] | 7ec7df431471de2326a14b208ace5c30d480a8c5f35ab1307ad895f95723323f |
| target.I127.nuclei | nucleus_inventory.v1 ['target.detector_mass', 'target.I127.mass_fraction', 'target.I127.mass_kg'] | 529fc19da2c34bc9021efae6aaff0997ee4906d8e11f3ac4b79c545361fccf44 |
| lecs.m_pi | identity.v1 ['constants.m_pi_charged'] | 65f4cd41571b0388231cdc09faa0d14a588ed5e56f7ebb1e048429f4f51364ea |

source_fluence_e/source_fluence_mub 是已经含 POT、yield、1/(4πL²) 的物化探测器注量。运行时数组为权威，不得再乘这些因子。上游参数、生成模型版本或坐标变化使数组指纹失效。prompt 线权重使用同一组源参数推导的 F；连续谱表不能被再次乘 F。

靶质量分数、单核质量和核数由显式输入只读推导；kg 质量用于核数，GeV 质量用于运动学，折叠的中间每 kg 因子按旧次序恢复。没有额外活时间因子。

## 模型公式与物理解释

### sns_fluence_legacy_v1

静止 pion 源用球面几何因子将每 POT 的每种产额转成探测器注量。该因子已经积分整个运行时间。

```text
F=r*N_POT/(4*pi*L_cm^2); L_cm=100*L_m
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| F | cm^-2 | cm^-2; per-species integrated fluence |
| r | neutrinos/species/POT | neutrinos/species/POT |
| N_POT | POT | POT |
| L_m | m | m |
| L_cm | cm | cm |

输入：['source.total_pot', 'source.yield_per_pot', 'source.baseline_m']。输出：F [cm^-2]。

实际参数引用：['source.baseline_m', 'source.total_pot', 'source.yield_per_pot']；模型依赖：[]。

定义域：positive baseline; nonnegative POT/yield。

归一化：per source component once。

边界行为：no live-time or target-mass multiplier。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'F': 'cm^-2', 'r': 'neutrinos/species/POT', 'N_POT': 'POT', 'L_m': 'm', 'L_cm': 'cm'}, 'output_unit': 'cm^-2', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'positive baseline; nonnegative POT/yield', 'bounds': [{'variable': 'L_m', 'unit': 'm', 'lower': 0, 'upper': None, 'lower_inclusive': False, 'upper_inclusive': False, 'parameter_ref': 'source.baseline_m'}]}, 'normalization': {'description': 'per source component once', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'sns_fluence_legacy_v1.boundary.v1', 'description': 'no live-time or target-mass multiplier'}}。

来源：['source'] :: _n_time_integrated_flux_cm2；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### sns_michel_tabulation_legacy_v1

delayed νe 与反νμ 的 Michel 形状先在完整等间距表上计算、裁剪并掩码，再线性插值。不是每个查询点都重新施加物理端点截断。

```text
f_e(E)=192*E^2*(1/2-E/m_mu)/m_mu^3; f_mub(E)=64*E^2*(3/4-E/m_mu)/m_mu^3; table_l=F*max(f_l(E_j),0)*1_mask(E_j); phi_l(E)=linear_interp(E_j,table_lj)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| E | MeV | MeV; neutrino energy |
| m_mu | MeV | MeV; 1000*constants.m_mu |
| E_j | MeV | MeV; source_energy_MeV |
| F | cm^-2 | cm^-2 |
| phi_l | cm^-2 MeV^-1 | cm^-2 MeV^-1 |
| f_l | MeV^-1 | MeV^-1 |
| mask | 1 | source.mask_min <= E_j <= source.mask_max |

输入：['source_energy_MeV', 'source_fluence_e', 'source_fluence_mub']。输出：phi_e,phi_mub [cm^-2 MeV^-1]。

实际参数引用：['source.tabulation_min', 'source.tabulation_max', 'source.mask_min', 'source.mask_max', 'source.tabulation_nodes', 'source.interpolation', 'source.fluence_per_species', 'constants.m_mu']；模型依赖：['sns_fluence_legacy_v1']。

定义域：integration uses declared DAR domain; table and mask domains are separately declared。

归一化：no re-normalization of clipped/interpolated table to F; analytic Michel functions integrate to 1 only on massless-electron ideal domain。

边界行为：linear interpolation; table-outside zero; final interpolation cell taper preserved。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'E': 'MeV', 'm_mu': 'MeV', 'E_j': 'MeV', 'F': 'cm^-2', 'phi_l': 'cm^-2 MeV^-1', 'f_l': 'MeV^-1', 'mask': '1'}, 'output_unit': 'cm^-2 MeV^-1', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'integration uses declared DAR domain; table and mask domains are separately declared', 'bounds': []}, 'normalization': {'description': 'no re-normalization of clipped/interpolated table to F; analytic Michel functions integrate to 1 only on massless-electron ideal domain', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'sns_michel_tabulation_legacy_v1.boundary.v1', 'description': 'linear interpolation; table-outside zero; final interpolation cell taper preserved'}}。

来源：['source'] :: build_neutrino_empirical_flux_sns；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### sns_prompt_line_v1

静止带电 pion 衰变产生 prompt νμ 谱线；积分直接加谱线权重乘截面。

```text
E0=(m_pi^2-m_mu^2)/(2*m_pi); phi_mu(E)=F*delta(E-E0)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| E0 | GeV | GeV in formula; converted to MeV |
| m_pi | GeV | GeV; charged pion mass |
| m_mu | GeV | GeV |
| F | cm^-2 | cm^-2 |
| delta | inverse_energy | inverse-energy Dirac distribution |

输入：['constants.m_pi_charged', 'constants.m_mu', 'source.fluence_per_species']。输出：line energy [MeV], weight [cm^-2]。

实际参数引用：['source.fluence_per_species', 'source.prompt_energy', 'constants.m_mu', 'constants.m_pi_charged']；模型依赖：['sns_fluence_legacy_v1']。

定义域：stationary two-body pion decay。

归一化：F once; no continuum prompt contribution。

边界行为：contributes iff E0 >= E_min(T)。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'E0': 'GeV', 'm_pi': 'GeV', 'm_mu': 'GeV', 'F': 'cm^-2', 'delta': 'inverse_energy'}, 'output_unit': 'not_scalar', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'stationary two-body pion decay', 'bounds': []}, 'normalization': {'description': 'F once; no continuum prompt contribution', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'sns_prompt_line_v1.boundary.v1', 'description': 'contributes iff E0 >= E_min(T)'}}。

来源：['source'] :: build_neutrino_empirical_flux_sns:muLine；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### sns_fixed_state_v1

固定纯味入射态，无传播或随能量变化；particle_kind 单独保存。

```text
rho_e=|e><e|; rho_mu=|mu><mu|; prompt=(nu,rho_mu); delayed_e=(nu,rho_e); delayed_mub=(antinu,rho_mu)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| rho_e | 1 | dimensionless 3x3 matrix |
| rho_mu | 1 | dimensionless 3x3 matrix |
| flavor_order | not_scalar | e,mu,tau |

输入：['state_rho_e', 'state_rho_mu']。输出：incident density and particle label。

实际参数引用：[]；模型依赖：[]。

定义域：constant state only。

归一化：trace(rho)=1。

边界行为：state parameters rejected; antinu tag does not alter current kernel。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'rho_e': '1', 'rho_mu': '1', 'flavor_order': 'not_scalar'}, 'output_unit': 'not_scalar', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'constant state only', 'bounds': []}, 'normalization': {'description': 'trace(rho)=1', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'sns_fixed_state_v1.boundary.v1', 'description': 'state parameters rejected; antinu tag does not alter current kernel'}}。

来源：['source'] :: sns_component_state；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### csi_target_inventory_v1

每个 CsI 化学式单元各含一个 Cs 和 I，质量分数不同而核数相等。动力学质量与核数质量采用各自显式常数。

```text
w_i=A_i/(A_Cs+A_I); m_i_kg=A_i*u_kg; m_i_GeV=A_i*u_GeV; N_i=Mdet*w_i/m_i_kg
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| w_i | 1 | 1; mass fraction |
| A_i | 1 | 1; isotope mass number |
| u_kg | kg | kg |
| u_GeV | GeV | GeV |
| Mdet | kg | kg |
| m_i_kg | kg | kg |
| m_i_GeV | GeV | GeV |
| N_i | nuclei | nuclei |

输入：['target.detector_mass', 'target.atomic_mass_kg', 'constants.AMU_GEV']。输出：isotope inventory with true nucleus counts。

实际参数引用：['target.detector_mass', 'target.atomic_mass_kg', 'target.Cs133.A', 'target.Cs133.mass_fraction', 'target.Cs133.mass_GeV', 'target.Cs133.mass_kg', 'target.I127.A', 'target.I127.mass_fraction', 'target.I127.mass_GeV', 'target.I127.mass_kg', 'constants.AMU_GEV']；模型依赖：[]。

定义域：Cs133/I127 only; equal Cs:I stoichiometry; no explicit Na dopant model。

归一化：sum_i N_i*m_i=Mdet; source does not contain nuclei or mass。

边界行为：zero detector mass gives zero counts。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'w_i': '1', 'A_i': '1', 'u_kg': 'kg', 'u_GeV': 'GeV', 'Mdet': 'kg', 'm_i_kg': 'kg', 'm_i_GeV': 'GeV', 'N_i': 'nuclei'}, 'output_unit': 'not_scalar', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'Cs133/I127 only; equal Cs:I stoichiometry; no explicit Na dopant model', 'bounds': []}, 'normalization': {'description': 'sum_i N_i*m_i=Mdet; source does not contain nuclei or mass', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'csi_target_inventory_v1.boundary.v1', 'description': 'zero detector mass gives zero counts'}}。

来源：['assembly'] :: assemble_csi2021; inventory_from_mass_fractions；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### li2026_sm_left_v1

SM 以四个维六 LEFT 系数加入通用 EFT 参数；零 BSM 是缺省参数点而非缺失占位。

```text
P=-G_F/sqrt(2); C6u1_SM=P*(1-8*s2/3)*I3; C6d1_SM=-P*(1-4*s2/3)*I3; C6u2_SM=-P*I3; C6d2_SM=P*I3; C_total=C_BSM+C_SM
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| P | GeV^-2 | GeV^-2 |
| G_F | GeV^-2 | GeV^-2 |
| s2 | 1 | sin^2(theta_W), dimensionless |
| I3 | 1 | 3x3 flavor identity |
| C_BSM | GeV^(4-d) | GeV^(4-d), 3x3 final-row/initial-column matrix |

输入：['interaction.include_sm', 'interaction.sin2thetaW']。输出：total LEFT Wilson coefficient matrices。

实际参数引用：['interaction.include_sm', 'interaction.sin2thetaW', 'constants.G_F']；模型依赖：[]。

定义域：22 supported operators; default BSM mapping empty。

归一化：no flux or target factor in Wilson coefficients。

边界行为：unknown operators rejected; LNV diagonal constrained to zero by engine。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'P': 'GeV^-2', 'G_F': 'GeV^-2', 's2': '1', 'I3': '1', 'C_BSM': 'GeV^(4-d)'}, 'output_unit': 'GeV^(4-d)', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': '22 supported operators; default BSM mapping empty', 'bounds': []}, 'normalization': {'description': 'no flux or target factor in Wilson coefficients', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'li2026_sm_left_v1.boundary.v1', 'description': 'unknown operators rejected; LNV diagonal constrained to zero by engine'}}。

来源：['differential'] :: _sm_left_dim6；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### li2026_matching_v1

通用引擎把 LEFT 矩阵匹配成质子/中子非相对论系数。完整线性表达式在本包 symbolic_equations.matching 中保存为数学审计定义。

```text
c_i^N=sum_o M_io^N(Ebar,q2,LECs)*C_o; Ebar=E-q0/2; c10_ud_p=B0_m_u*C7u5-B0_m_d*C7d5; c10_ud_n=-c10_ud_p; c_i^0=(cp_i+cn_i)/2; c_i^1=(cp_i-cn_i)/2
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| c_i^N | GeV^-2&#124;GeV^-3 | GeV^-2 for i=1..12; GeV^-3 for i=13,14 |
| C_o | GeV^(4-d) | GeV^(4-d), final-row/initial-column |
| M_io^N | GeV^(d-6)&#124;GeV^(d-7) | matching linear map, implied unit GeV^(d-6) or GeV^(d-7) |
| Ebar | GeV | GeV |
| q0 | GeV | GeV; recoil |
| q2 | GeV^2 | GeV^2; signed Lorentz transfer |
| LECs | not_scalar | parameter registry lecs.* |

输入：['LEFT coefficients', 'kinematics', 'lecs.*']。输出：cp[1..14], cn[1..14]。

实际参数引用：['constants.alpha_em', 'lecs.g_A', 'lecs.B0_m_u', 'lecs.B0_m_d', 'lecs.L1', 'lecs.L2', 'lecs.L3', 'lecs.L4', 'lecs.L5', 'lecs.L6', 'lecs.L7', 'lecs.L8', 'lecs.L11', 'lecs.L12', 'lecs.L13', 'lecs.L14', 'lecs.sigma_u_p', 'lecs.sigma_d_p', 'lecs.sigma_u_n', 'lecs.sigma_d_n', 'lecs.g1', 'lecs.g2', 'lecs.g3', 'lecs.g4', 'lecs.g5', 'lecs.g6', 'lecs.g7', 'lecs.g8', 'lecs.g9', 'lecs.m_pi', 'lecs.m_N']；模型依赖：['li2026_sm_left_v1', 'elastic_kinematics_v1']。

定义域：one-body current Li2026 proof convention; no SMEFT running pipeline。

归一化：np basis; LNC/LNV interference forbidden downstream。

边界行为：safe_ratio(n,q2)=0 when abs(q2)<=1e-30; safe_pion(n)=0 when abs(m_pi^2-q2)<=1e-30; this is a legacy numerical prescription。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'c_i^N': 'GeV^-2|GeV^-3', 'C_o': 'GeV^(4-d)', 'M_io^N': 'GeV^(d-6)|GeV^(d-7)', 'Ebar': 'GeV', 'q0': 'GeV', 'q2': 'GeV^2', 'LECs': 'not_scalar'}, 'output_unit': 'not_scalar', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'one-body current Li2026 proof convention; no SMEFT running pipeline', 'bounds': []}, 'normalization': {'description': 'np basis; LNC/LNV interference forbidden downstream', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'li2026_matching_v1.boundary.v1', 'description': 'safe_ratio(n,q2)=0 when abs(q2)<=1e-30; safe_pion(n)=0 when abs(m_pi^2-q2)<=1e-30; this is a legacy numerical prescription'}}。

来源：['matching'] :: left_to_ci:c10_mass_mode=quark_mass_resolved；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### elastic_kinematics_v1

两体弹性散射的精确支撑决定连续积分中保留的节点。核响应使用三动量模，匹配使用带符号四动量转移。

```text
Tmax(E)=2*E^2/(mA+2*E); Emin(T)=(T+sqrt(T^2+2*mA*T))/2; q0=T; qabs^2=2*mA*T; q2=T^2-qabs^2; y=(qabs*b/2)^2
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| T | GeV | GeV (input recoil keV multiplied by 1e-6) |
| E | GeV | GeV (input MeV multiplied by 1e-3) |
| mA | GeV | GeV |
| q0 | GeV | GeV |
| qabs | GeV | GeV |
| q2 | GeV^2 | GeV^2 |
| b | GeV^-1 | GeV^-1 |
| y | 1 | 1 |

输入：['target kinematic masses', 'recoil', 'energy']。输出：thresholds, momentum and dimensionless y。

实际参数引用：['target.Cs133.mass_GeV', 'target.I127.mass_GeV']；模型依赖：[]。

定义域：T>=0; E>0。

归一化：no normalization factor。

边界行为：T>Tmax gives zero; negative recoil/nonfinite inputs rejected。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'T': 'GeV', 'E': 'GeV', 'mA': 'GeV', 'q0': 'GeV', 'qabs': 'GeV', 'q2': 'GeV^2', 'b': 'GeV^-1', 'y': '1'}, 'output_unit': 'not_scalar', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'T>=0; E>0', 'bounds': []}, 'normalization': {'description': 'no normalization factor', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'elastic_kinematics_v1.boundary.v1', 'description': 'T>Tmax gives zero; negative recoil/nonfinite inputs rejected'}}。

来源：['kinematics'] :: two_body_recoil_max_GeV; minimum_neutrino_energy_GeV；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### nuclear_np_polynomial_v1

核结构响应矩阵按质子/中子排列。系数以最高保留精度打包；没有额外除以核自旋或 4π。M 为相干密度，Sigma 为纵/横自旋，Phi 为自旋轨道类，Delta 为轨道类，MPhiPP 为干涉。

```text
W_X,ab(y)=exp(e_i*y)*sum_k w_X,ab,k*y^k; a,b in (p,n)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| W_X | 1 | dimensionless 2x2 nuclear response |
| w_X,ab,k | 1 | dimensionless polynomial coefficient |
| e_i | 1 | 1; isotope exponential factor |
| y | 1 | 1 |
| k | 1 | nonnegative integer power |

输入：['nuclear_* arrays', 'target.*.b']。输出：W_X matrices [1]。

实际参数引用：['target.Cs133.b', 'nuclear.Cs133.exp_factor', 'target.I127.b', 'nuclear.I127.exp_factor']；模型依赖：['elastic_kinematics_v1']。

定义域：current tabulated polynomial model; no independently documented validity range。

归一化：source normalization preserved; M(0) internal checks do not prove external source convention。

边界行为：SigmaPDelta table excluded: corresponding particle response is identically zero。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'W_X': '1', 'w_X,ab,k': '1', 'e_i': '1', 'y': '1', 'k': '1'}, 'output_unit': '1', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'current tabulated polynomial model; no independently documented validity range', 'bounds': []}, 'normalization': {'description': 'source normalization preserved; M(0) internal checks do not prove external source convention', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'nuclear_np_polynomial_v1.boundary.v1', 'description': 'SigmaPDelta table excluded: corresponding particle response is identically zero'}}。

来源：['response_reader'] :: ResponseW.W_np；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### li2026_R_W_kernel_v1

粒子响应 R 与核响应 W 收缩为入射味空间的 Hermitian 振幅核 K。R 的多项式表达式列于 symbolic_equations.particle_response；同扇区内才允许干涉。

```text
B_ij^ab=(c_i^a)^dagger*c_j^b; S_ij=B_ij+B_ji; A_ij=B_ij-B_ji; K=sum_X,sum_ab R_X^ab*W_X^ab; MPhiPP contribution=(V+V^dagger)/2; R_SigmaPDelta=0
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| B_ij | GeV^(p_i+p_j) | ordered matrix bilinear |
| S_ij | GeV^(p_i+p_j) | symmetric bilinear |
| A_ij | GeV^(p_i+p_j) | antisymmetric bilinear |
| c_i^a | GeV^-2&#124;GeV^-3 | NR flavor coefficient matrix |
| R_X | GeV^-2 | GeV^-2, flavor 3x3 and nucleon 2x2 |
| W_X | 1 | 1, nucleon 2x2 |
| K | GeV^-2 | GeV^-2, flavor 3x3 |
| V | GeV^-2 | MPhiPP unhermitianized 3x3 contribution |

输入：['matched coefficients', 'nuclear matrices']。输出：K [GeV^-2]。

实际参数引用：['lecs.m_N']；模型依赖：['li2026_matching_v1', 'nuclear_np_polynomial_v1']。

定义域：one-body current operator sectors; constant SNS states for Fast。

归一化：no implicit 4*pi, spin-average, flux, exposure or target count added。

边界行为：Hermiticity/positivity checked by engine; antinu uses same kernel, audit open。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'B_ij': 'GeV^(p_i+p_j)', 'S_ij': 'GeV^(p_i+p_j)', 'A_ij': 'GeV^(p_i+p_j)', 'c_i^a': 'GeV^-2|GeV^-3', 'R_X': 'GeV^-2', 'W_X': '1', 'K': 'GeV^-2', 'V': 'GeV^-2'}, 'output_unit': 'GeV^-2', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'one-body current operator sectors; constant SNS states for Fast', 'bounds': []}, 'normalization': {'description': 'no implicit 4*pi, spin-average, flux, exposure or target count added', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'li2026_R_W_kernel_v1.boundary.v1', 'description': 'Hermiticity/positivity checked by engine; antinu uses same kernel, audit open'}}。

来源：['amplitude'] :: flavor_kernel_onebody_li2026；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### li2026_dsigma_v1

先将味核与入射密度矩阵收缩，再乘相空间因子及 GeV 到 cm² 和每 keV 的单位转换。

```text
d_sigma/dT_keV=Tr(rho*K)*mA/(8*pi*E^2)*GEV_INV2_TO_CM2*1e-6
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| rho | 1 | dimensionless 3x3 density |
| K | GeV^-2 | GeV^-2 |
| mA | GeV | GeV |
| E | GeV | GeV |
| GEV_INV2_TO_CM2 | cm^2/GeV^-2 | cm^2 per GeV^-2 |
| T_keV | keV | keV |

输入：['K', 'incident state', 'energy']。输出：cm^2/keV。

实际参数引用：['target.Cs133.mass_GeV', 'target.I127.mass_GeV', 'constants.GEV_INV2_TO_CM2']；模型依赖：['li2026_R_W_kernel_v1', 'sns_fixed_state_v1']。

定义域：elastic support only。

归一化：per nucleus; no source/efficiency/exposure factors。

边界行为：zero outside elastic support or at rates-grid E=0。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'rho': '1', 'K': 'GeV^-2', 'mA': 'GeV', 'E': 'GeV', 'GEV_INV2_TO_CM2': 'cm^2/GeV^-2', 'T_keV': 'keV'}, 'output_unit': 'cm^2/keV', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'elastic support only', 'bounds': []}, 'normalization': {'description': 'per nucleus; no source/efficiency/exposure factors', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'li2026_dsigma_v1.boundary.v1', 'description': 'zero outside elastic support or at rates-grid E=0'}}。

来源：['cross_section'] :: amplitude_kernel_to_dsigma_cm2_per_GeV; units.cm2_per_GeV_to_cm2_per_keV；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### csi_quenching_legacy_v1

真实核反冲映射成电子等效能量；四个系数的顺序固定。这里没有另乘一组光产额参数。

```text
t=T_keV*1e-3; Eee_keV=1e3*(q1*t+q2*t^2+q3*t^3+q4*t^4)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| T_keV | keVnr | keVnr |
| t | MeVnr | MeVnr |
| Eee_keV | keVee | keVee |
| q1 | 1 | 1 |
| q2 | MeV^-1 | MeV^-1 |
| q3 | MeV^-2 | MeV^-2 |
| q4 | MeV^-3 | MeV^-3 |

输入：['recoil']。输出：electron-equivalent energy [keVee]。

实际参数引用：['detector.quenching_q1', 'detector.quenching_q2', 'detector.quenching_q3', 'detector.quenching_q4']；模型依赖：[]。

定义域：actual sampled recoil range from declared grid; official calibration range missing。

归一化：energy conversion only。

边界行为：nonpositive Eee causes response density zero。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'T_keV': 'keVnr', 't': 'MeVnr', 'Eee_keV': 'keVee', 'q1': '1', 'q2': 'MeV^-1', 'q3': 'MeV^-2', 'q4': 'MeV^-3'}, 'output_unit': 'keVee', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'actual sampled recoil range from declared grid; official calibration range missing', 'bounds': []}, 'normalization': {'description': 'energy conversion only', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'csi_quenching_legacy_v1.boundary.v1', 'description': 'nonpositive Eee causes response density zero'}}。

来源：['differential'] :: eee_quenching_csi；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### legacy_csi_gamma

Gamma 用 shape-rate 参数化：k 是 shape，lambda 是 rate，scale=1/lambda。它表示 PE 的条件密度而非 bin 概率。

```text
a=a0/Eee; b=b0*Eee; k=1+b; lambda=a*(1+b); p(x|T)=lambda^k/Gamma(k)*x^(k-1)*exp(-lambda*x); mean=k/lambda=Eee/a0; variance=k/lambda^2
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| Eee | keVee | keVee |
| a0 | keVee/PE | keVee/PE |
| b0 | keVee^-1 | keVee^-1 |
| a | PE^-1 | PE^-1 |
| b | 1 | 1 |
| k | 1 | 1; shape |
| lambda | PE^-1 | PE^-1; rate |
| x | PE | PE |
| p | PE^-1 | PE^-1 |
| mean | PE | PE |
| variance | PE^2 | PE^2 |

输入：['electron-equivalent energy', 'observed PE']。输出：response density [PE^-1]。

实际参数引用：['detector.gamma_a', 'detector.gamma_b']；模型依赖：['csi_quenching_legacy_v1']。

定义域：Eee>0 and x>0。

归一化：integral over x in (0,infinity)=1; not renormalized to analysis window。

边界行为：x<=0 or Eee<=0 gives zero; log evaluation uses max(x,1e-300)。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'Eee': 'keVee', 'a0': 'keVee/PE', 'b0': 'keVee^-1', 'a': 'PE^-1', 'b': '1', 'k': '1', 'lambda': 'PE^-1', 'x': 'PE', 'p': 'PE^-1', 'mean': 'PE', 'variance': 'PE^2'}, 'output_unit': 'PE^-1', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'Eee>0 and x>0', 'bounds': [{'variable': 'Eee', 'unit': 'keVee', 'lower': 0, 'upper': None, 'lower_inclusive': False, 'upper_inclusive': False, 'parameter_ref': None}, {'variable': 'x', 'unit': 'PE', 'lower': 0, 'upper': None, 'lower_inclusive': False, 'upper_inclusive': False, 'parameter_ref': None}]}, 'normalization': {'description': 'integral over x in (0,infinity)=1; not renormalized to analysis window', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'legacy_csi_gamma.boundary.v1', 'description': 'x<=0 or Eee<=0 gives zero; log evaluation uses max(x,1e-300)'}}。

来源：['differential'] :: p_smearing_csi；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### csi2021_logistic_legacy

重建 PE 上的选择效率，参数按 (a,b,c,d) 顺序。实现只有零下限，不能擅自改成双边裁剪。

```text
epsilon(x)=max(a/(1+exp(-b*(x-c)))+d,0)
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| x | PE | PE |
| a | 1 | 1; amplitude |
| b | PE^-1 | PE^-1; slope |
| c | PE | PE; center |
| d | 1 | 1; offset |
| epsilon | 1 | 1; efficiency |

输入：['observed PE']。输出：efficiency [1]。

实际参数引用：['detector.efficiency_a', 'detector.efficiency_b', 'detector.efficiency_c', 'detector.efficiency_d']；模型依赖：[]。

定义域：sampled analysis window。

归一化：dimensionless; applied after interpolation in current Slow strategy。

边界行为：lower-clamped at zero; folding rejects efficiency outside [0,1] on queried grid。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'x': 'PE', 'a': '1', 'b': 'PE^-1', 'c': 'PE', 'd': '1', 'epsilon': '1'}, 'output_unit': '1', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'sampled analysis window', 'bounds': []}, 'normalization': {'description': 'dimensionless; applied after interpolation in current Slow strategy', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'csi2021_logistic_legacy.boundary.v1', 'description': 'lower-clamped at zero; folding rejects efficiency outside [0,1] on queried grid'}}。

来源：['detector'] :: efficiency_csi2021；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### legacy_component_acceptance

prompt 与 delayed 分量使用各自的选择接受率；时间变化、时间坐标和硬件阈值没有由此补造。

```text
N_l,i,b=acceptance_l*N_pre_l,i,b*N_i; N_b=sum_l,i N_l,i,b
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| acceptance_l | 1 | 1; source-component selection |
| N_pre | events/nucleus/bin | events/nucleus/bin before acceptance |
| N_i | nuclei | nuclei |
| N_b | events/bin | events/bin |

输入：['preselection counts', 'target inventory']。输出：counts [events/bin]。

实际参数引用：['target.Cs133.nuclei', 'target.I127.nuclei', 'detector.acceptance_e', 'detector.acceptance_mu', 'detector.acceptance_mub']；模型依赖：[]。

定义域：three declared SNS components。

归一化：exactly once; not already in fluence or efficiency。

边界行为：analysis-window losses are excluded, not redistributed。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'acceptance_l': '1', 'N_pre': 'events/nucleus/bin', 'N_i': 'nuclei', 'N_b': 'events/bin'}, 'output_unit': 'events/bin', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'three declared SNS components', 'bounds': []}, 'normalization': {'description': 'exactly once; not already in fluence or efficiency', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'legacy_component_acceptance.boundary.v1', 'description': 'analysis-window losses are excluded, not redistributed'}}。

来源：['prediction'] :: predict:selection.acceptance；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### legacy_csi2021_v1

总预测式同时保留当前数值运算次序：先按反冲积分出 PE 密度，按每 kg 中间量裁剪，再插值、效率、bin 积分，最后恢复每核归一化并乘真实核数。中间质量因子代数抵消，不能再额外乘 Mdet。

```text
Y_li(T)=Trapz_E[phi_l(E)*dsigma_li(E,T)]_allowed + sum_lines F_line*dsigma_li(Eline,T); h_li(x_j)=max(Trapz_T[Y_li(T)*p(x_j|T)/m_i_kg],0); N_pre_li,b=m_i_kg*Trapz_x[linear_interp(x_j,h_li)*epsilon(x)]_bin; N_b=sum_li N_i*acceptance_l*N_pre_li,b
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| Y_li | events/nucleus/keV | events/nucleus/keV; time-integrated |
| phi_l | cm^-2 MeV^-1 | cm^-2 MeV^-1 |
| dsigma_li | cm^2/keV | cm^2/keV |
| F_line | cm^-2 | cm^-2 |
| T | keVnr | keVnr |
| x_j | PE | PE density sample |
| m_i_kg | kg/nucleus | kg/nucleus |
| h_li | events/kg/PE | events/kg/PE |
| N_pre_li,b | events/nucleus/bin | events/nucleus/bin |
| N_i | nuclei | nuclei |
| N_b | events/bin | events/bin |
| Trapz | not_scalar | composite trapezoid on actual selected nodes |

输入：['source', 'interaction', 'target', 'detector', 'observable']。输出：nonnegative 9-bin expected signal [events/bin]。

实际参数引用：['source.integration_min', 'source.integration_max', 'target.Cs133.mass_kg', 'target.I127.mass_kg', 'constants.m_e', 'numerics.n_er', 'numerics.n_enu', 'numerics.n_observed_bin', 'numerics.observed_step', 'numerics.recoil_min_keV']；模型依赖：['sns_michel_tabulation_legacy_v1', 'sns_prompt_line_v1', 'li2026_dsigma_v1', 'legacy_csi_gamma', 'csi2021_logistic_legacy', 'csi_target_inventory_v1', 'legacy_component_acceptance']。

定义域：T grid: linspace(Tmin,max_i endpoint,n_er) per isotope; E grid: linspace(0,DAR_endpoint,n_enu), filter E>=Emin(T),E>0 without threshold-node insertion; PE samples: arange(first_edge,last_edge+0.5*step,step); subnodes: linspace(each edge pair,n_observed_bin)。

归一化：fluence includes POT/geometry; nuclei include mass/stoichiometry; efficiency and acceptance each once; no live time, background or bin-width division in prediction。

边界行为：PE density interpolation outside sampled domain zero; negative density nodes clipped; endpoints shared by quadrature have measure zero; nine half-open bins and final upper edge retained by observation convention。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'Y_li': 'events/nucleus/keV', 'phi_l': 'cm^-2 MeV^-1', 'dsigma_li': 'cm^2/keV', 'F_line': 'cm^-2', 'T': 'keVnr', 'x_j': 'PE', 'm_i_kg': 'kg/nucleus', 'h_li': 'events/kg/PE', 'N_pre_li,b': 'events/nucleus/bin', 'N_i': 'nuclei', 'N_b': 'events/bin', 'Trapz': 'not_scalar'}, 'output_unit': 'events/bin', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'T grid: linspace(Tmin,max_i endpoint,n_er) per isotope; E grid: linspace(0,DAR_endpoint,n_enu), filter E>=Emin(T),E>0 without threshold-node insertion; PE samples: arange(first_edge,last_edge+0.5*step,step); subnodes: linspace(each edge pair,n_observed_bin)', 'bounds': []}, 'normalization': {'description': 'fluence includes POT/geometry; nuclei include mass/stoichiometry; efficiency and acceptance each once; no live time, background or bin-width division in prediction', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'legacy_csi2021_v1.boundary.v1', 'description': 'PE density interpolation outside sampled domain zero; negative density nodes clipped; endpoints shared by quadrature have measure zero; nine half-open bins and final upper edge retained by observation convention'}}。

来源：['folding'] :: rates/recoil.integrate_recoil_yield; legacy_density_fold; core/predict.predict；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

### gaussian_two_pull_legacy_v1

旧 residual/excess 数组的近似 Gaussian 统计。信号从 events/bin 转 counts/PE 一次。误差对角且与参数无关，两项归一化 pull 在全箱间相关；alpha/beta 无约束解析极小化。

```text
s_b=N_b/(edge[b+1]-edge[b]); model_b=(1+alpha)*s_b+(1+beta)*background_b; chi2=sum_b((observed_b-model_b)/sigma_b)^2+(alpha/sigma_alpha)^2+(beta/sigma_beta)^2
```

| 变量 | 单位（结构化） | 定义 |
| --- | --- | --- |
| N_b | events/bin | events/bin |
| edge | PE | PE |
| s_b | counts/PE | counts/PE |
| observed_b | counts/PE | counts/PE; may be negative |
| background_b | counts/PE | counts/PE |
| sigma_b | counts/PE | counts/PE |
| alpha | 1 | 1; signal normalization nuisance |
| beta | 1 | 1; background normalization nuisance |
| sigma_alpha | 1 | 1 |
| sigma_beta | 1 | 1 |
| chi2 | 1 | 1 |

输入：['signal prediction', 'statistics_observed', 'statistics_background', 'statistics_uncertainty', 'observable_pe_edges']。输出：profiled approximate chi2 [1]。

实际参数引用：['statistics.sigma_alpha', 'statistics.sigma_beta', 'statistics.sigma_floor']；模型依赖：['legacy_csi2021_v1']。

定义域：nine bins; independent symmetric errors plus two Gaussian normalization pulls。

归一化：observed/background/sigma already counts/PE; no covariance resource used; no Poisson interpretation。

边界行为：sigma=max(sigma,sigma_floor); solve 2x2 normal equations; singular solve returns alpha=beta=0,success=False; no clip_bounds in actual binding。

结构化合同：{'binding_status': 'BOUND_AND_TESTED', 'variable_units': {'N_b': 'events/bin', 'edge': 'PE', 's_b': 'counts/PE', 'observed_b': 'counts/PE', 'background_b': 'counts/PE', 'sigma_b': 'counts/PE', 'alpha': '1', 'beta': '1', 'sigma_alpha': '1', 'sigma_beta': '1', 'chi2': '1'}, 'output_unit': '1', 'domain': {'status': 'LEGACY_CODE_DERIVED', 'description': 'nine bins; independent symmetric errors plus two Gaussian normalization pulls', 'bounds': []}, 'normalization': {'description': 'observed/background/sigma already counts/PE; no covariance resource used; no Poisson interpretation', 'additional_runtime_factors': []}, 'boundary': {'policy_id': 'gaussian_two_pull_legacy_v1.boundary.v1', 'description': 'sigma=max(sigma,sigma_floor); solve 2x2 normal equations; singular solve returns alpha=beta=0,success=False; no clip_bounds in actual binding'}}。

来源：['profiling'] :: profile_gaussian_two_pull; statistics_binding.evaluate；legacy-code-derived/SOURCE_EXTRACTED；DRAFT，未人工确认。

## 共同 EFT 数学审计与算符

Audit equations only, never eval. cp/cn=proton/neutron NR matrices; C5_1 etc from operator table; E=Enu GeV, E2/E3/E4=E powers; qabs2/3/4=qabs powers. ord_(i,j)=dagger(c_i^a)*c_j^b; sym_/anti_=sum/difference with i,j exchanged. b11 etc are aliases expanded in equation table. _safe_div_by_q2(n,q2) and _safe_pion_pole(n,m_pi,q2) follow stated pole boundary; np.zeros_like means identically zero. pi=mathematical pi, j=imaginary unit; all L/g/B0/sigma/m constants reference lecs registry. FormFactors.build is not on this actual chain.

| 内部算符 | key | 维度 | 扇区 | 系数单位 | LNV 对角必须为零 |
| --- | --- | --- | --- | --- | --- |
| C5_1 | [5, 1, ''] | 5 | LNV | GeV^-1 | True |
| C6u1 | [6, 1, 'u'] | 6 | LNC | GeV^-2 | False |
| C6d1 | [6, 1, 'd'] | 6 | LNC | GeV^-2 | False |
| C6u2 | [6, 2, 'u'] | 6 | LNC | GeV^-2 | False |
| C6d2 | [6, 2, 'd'] | 6 | LNC | GeV^-2 | False |
| C7u1 | [7, 1, 'u'] | 7 | LNC | GeV^-3 | False |
| C7d1 | [7, 1, 'd'] | 7 | LNC | GeV^-3 | False |
| C7u2 | [7, 2, 'u'] | 7 | LNC | GeV^-3 | False |
| C7d2 | [7, 2, 'd'] | 7 | LNC | GeV^-3 | False |
| C7u3 | [7, 3, 'u'] | 7 | LNV | GeV^-3 | True |
| C7d3 | [7, 3, 'd'] | 7 | LNV | GeV^-3 | True |
| C7u4 | [7, 4, 'u'] | 7 | LNV | GeV^-3 | True |
| C7d4 | [7, 4, 'd'] | 7 | LNV | GeV^-3 | True |
| C7u5 | [7, 5, 'u'] | 7 | LNV | GeV^-3 | True |
| C7d5 | [7, 5, 'd'] | 7 | LNV | GeV^-3 | True |
| C7_6 | [7, 6, ''] | 7 | LNV | GeV^-3 | True |
| C7_7 | [7, 7, ''] | 7 | LNV | GeV^-3 | True |
| C8u1 | [8, 1, 'u'] | 8 | LNC | GeV^-4 | False |
| C8d1 | [8, 1, 'd'] | 8 | LNC | GeV^-4 | False |
| C8u2 | [8, 2, 'u'] | 8 | LNC | GeV^-4 | False |
| C8d2 | [8, 2, 'd'] | 8 | LNC | GeV^-4 | False |
| C8_9 | [8, 9, ''] | 8 | LNC | GeV^-4 | False |

### matching（audit_only，不可执行）

| 左端 | 数学表达（旧代码记号） | 源行 |
| --- | --- | --- |
| cp[1] | 2.0 * C6u1 + C6d1 + (g1 + g2) * C7u1 + g2 * C7d1 | 169 |
| cp[2] | 2.0 * (L3 + L4) * C6u2 + 2.0 * L4 * C6d2 | 170 |
| cp[3] | su_p * C7u4 + sd_p * C7d4 + L13 * C7_6 - _safe_div_by_q2(2.0 * alpha * Ebar / math.pi * C5_1, q2) | 171 |
| cp[4] | 2.0 * (L5 + L6) * C7u3 + 2.0 * L6 * C7d3 | 172 |
| cp[5] | 2.0 * C6u1 + C6d1 | 173 |
| cp[6] | (2.0 + 2.0 * L1 + 2.0 * L2) * C6u1 + (1.0 + 2.0 * L2) * C6d1 | 174 |
| cp[7] | 2.0 * (L3 + L4) * C6u2 + 2.0 * L4 * C6d2 | 175 |
| cp[8] | (L5 + L6) * C7u3 + L6 * C7d3 | 176 |
| cp[9] | (L5 + L6 + L7 + L8) * C7u3 + (L6 + L8) * C7d3 | 177 |
| cp[10] | _safe_pion_pole(g_A * m_N * c10_ud_p, m_pi, q2) + (L11 + L12) * C7u5 + L12 * C7d5 + L14 * C7_7 | 178 |
| cp[11] | 4.0 * (g3 + g4) * C7u2 + 4.0 * g4 * C7d2 | 179 |
| cp[12] | _safe_div_by_q2(alpha * m_N / (3.0 * math.pi) * (1.0 + 2.0 * L1) * C5_1, q2) | 180 |
| cp[13] | (g5 + g6) * C8u1 + g6 * C8d1 + g9 * C8_9 | 181 |
| cp[14] | 2.0 * (g7 + g8) * C8u2 + 2.0 * g8 * C8d2 | 182 |
| cn[1] | C6u1 + 2.0 * C6d1 + (g1 + g2) * C7d1 + g2 * C7u1 | 184 |
| cn[2] | 2.0 * (L3 + L4) * C6d2 + 2.0 * L4 * C6u2 | 185 |
| cn[3] | su_n * C7u4 + sd_n * C7d4 + L13 * C7_6 | 186 |
| cn[4] | 2.0 * (L5 + L6) * C7d3 + 2.0 * L6 * C7u3 | 187 |
| cn[5] | C6u1 + 2.0 * C6d1 | 188 |
| cn[6] | (2.0 + 2.0 * L1 + 2.0 * L2) * C6d1 + (1.0 + 2.0 * L2) * C6u1 | 189 |
| cn[7] | 2.0 * (L3 + L4) * C6d2 + 2.0 * L4 * C6u2 | 190 |
| cn[8] | (L5 + L6) * C7d3 + L6 * C7u3 | 191 |
| cn[9] | (L5 + L6 + L7 + L8) * C7d3 + (L6 + L8) * C7u3 | 192 |
| cn[10] | _safe_pion_pole(g_A * m_N * c10_ud_n, m_pi, q2) + (L11 + L12) * C7d5 + L12 * C7u5 + L14 * C7_7 | 193 |
| cn[11] | 4.0 * (g3 + g4) * C7d2 + 4.0 * g4 * C7u2 | 194 |
| cn[12] | cp[12] | 195 |
| cn[13] | (g5 + g6) * C8d1 + g6 * C8u1 + g9 * C8_9 | 196 |
| cn[14] | 2.0 * (g7 + g8) * C8d2 + 2.0 * g8 * C8u2 | 197 |

### particle_response（audit_only，不可执行）

| 左端 | 数学表达（旧代码记号） | 源行 |
| --- | --- | --- |
| b11 | ord_(1, 1) | 113 |
| b1313 | ord_(13, 13) | 114 |
| b33 | ord_(3, 3) | 115 |
| b99 | ord_(9, 9) | 116 |
| s1_13 | sym_(1, 13) | 117 |
| a9_3 | anti_(9, 3) | 118 |
| b1111 | ord_(11, 11) | 119 |
| b1010 | ord_(10, 10) | 120 |
| b44 | ord_(4, 4) | 121 |
| a10_4 | anti_(10, 4) | 122 |
| s11_14 | sym_(11, 14) | 123 |
| s2_11 | sym_(2, 11) | 124 |
| b1414 | ord_(14, 14) | 125 |
| s2_14 | sym_(2, 14) | 126 |
| a6_14 | anti_(6, 14) | 127 |
| b22 | ord_(2, 2) | 128 |
| a6_2 | anti_(6, 2) | 129 |
| b66 | ord_(6, 6) | 130 |
| b88 | ord_(8, 8) | 131 |
| b55 | ord_(5, 5) | 132 |
| b3_8 | ord_(3, 8) | 133 |
| b9_8 | ord_(9, 8) | 134 |
| R_M | (4.0 * E2 - qabs2 - 2.0 * E * qabs2 / mA) * b11 + (16.0 * E4 - 4.0 * E2 * qabs2 - 16.0 * E3 * qabs2 / mA + 2.0 * E * qabs4 / mA) * b1313 + qabs2 * b33 + (8.0 * E3 - 2.0 * E * qabs2 - 6.0 * E2 * qabs2 / mA + qabs4 / (2.0 * mA)) * s1_13 + (2j * E * qabs2 / mN - 1j * qabs4 / (2.0 * mA * mN)) * a9_3 + (4.0 * E2 * qabs2 / (mN * mN) - 2.0 * E * qabs4 / (mA * mN * mN)) * b99 | 135 |
| R_SigmaPP | (E2 * qabs2 / (mN * mN) - E * qabs4 / (2.0 * mA * mN * mN) - qabs4 / (4.0 * mN * mN)) * b1111 + qabs4 / (4.0 * mN * mN) * b1010 + (E2 - E * qabs2 / (2.0 * mA)) * b44 + (1j * E * qabs2 / (2.0 * mN) - 1j * qabs4 / (8.0 * mA * mN)) * a10_4 + (E3 * qabs2 / (mA * mN) - E * qabs4 / (4.0 * mA * mN)) * s11_14 + (E2 * qabs2 / (2.0 * mA * mN) - qabs4 / (8.0 * mA * mN)) * s2_11 | 136 |
| R_SigmaP | (2.0 * E4 + 0.5 * E2 * qabs2 - 2.0 * E3 * qabs2 / mA - E * qabs4 / (4.0 * mA)) * b1414 + (E3 + 0.25 * E * qabs2 - 3.0 * E2 * qabs2 / (4.0 * mA) - qabs4 / (16.0 * mA)) * s2_14 + (2j * E2 * qabs2 / mN - 1j * E * qabs4 / (mA * mN)) * a6_14 + (0.5 * E2 + 0.125 * qabs2 - E * qabs2 / (4.0 * mA)) * b22 + (1j * E * qabs2 / mN - 1j * qabs4 / (4.0 * mA * mN)) * a6_2 + (2.0 * E2 * qabs2 / (mN * mN) + qabs4 / (2.0 * mN * mN) - E * qabs4 / (mA * mN * mN)) * b66 + (0.5 * E2 - E * qabs2 / (4.0 * mA) - 0.125 * qabs2) * b44 | 137 |
| R_PhiPP | (4.0 * E2 - 2.0 * E * qabs2 / mA) * b88 | 138 |
| R_PhiPT | (2.0 * E2 - 0.5 * qabs2 - E * qabs2 / mA) * b88 | 139 |
| R_Delta | (2.0 * E2 + 0.5 * qabs2 - E * qabs2 / mA) * b55 | 140 |
| R_MPhiPP | (-2.0 * E * qabs + qabs3 / (2.0 * mA)) * b3_8 + (-4j * E2 * qabs / mN + 2j * E * qabs3 / (mA * mN)) * b9_8 | 141 |
| R_SigmaPDelta | np.zeros_like(R_M) | 145 |

## 观测坐标、统计数组与数值设置

half-open adjacent bins; final upper edge retained; quadrature integrates endpoints

预测为 events/bin，已含源、核数、效率和接受率；统计输入是 counts/PE。仅对预测除一次箱宽，统计数组不再除宽度；负 residual 保留。

| bin | 左边界 PE | 右边界 PE | 宽度 PE | observed counts/PE | background counts/PE | sigma counts/PE |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.001 | 8.001 | 7.999999999999999 | 1.021 | 0.0 | 0.454695767 |
| 2 | 8.001 | 12.001 | 4.0 | 13.195 | 0.229 | 3.816688713 |
| 3 | 12.001 | 16.001 | 4.000000000000002 | 18.941 | 0.455 | 4.717813051 |
| 4 | 16.001 | 20.001 | 4.0 | 13.059 | 0.48 | 4.304453263 |
| 5 | 20.001 | 24.001 | 4.0 | 11.043 | 0.429 | 3.858024691 |
| 6 | 24.001 | 32.001 | 7.9999999999999964 | 5.977 | 0.329 | 2.543540564 |
| 7 | 32.001 | 40.001 | 8.0 | 1.838 | 0.229 | 2.466380071 |
| 8 | 40.001 | 48.001 | 8.0 | 2.274 | 0.179 | 2.339616402 |
| 9 | 48.001 | 60.001 | 12.0 | -0.831 | 0.154 | 1.785714286 |

fixed grids, no adaptive tolerance on actual legacy path; convergence not established in pilot

quad(epsabs=1e-11,epsrel=1e-10) exists but is NOT the bound runtime numerical strategy; no substitution in pilot

- source + POT -> integrated detector fluence
- fluence + interaction + state -> per-nucleus recoil yield
- recoil yield + response + efficiency + PE bins -> preselection events/nucleus/bin
- preselection + component acceptance + isotope nuclei -> events/bin
- events/bin / width -> approximate Gaussian evaluation

## 全部 NPZ 数组

归档 SHA256：`25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a`。

| NPZ key | 用途 | 单位 | shape | dtype | 轴/坐标 | 角色 | 归一化/生成 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nuclear_Cs133_M | Cs133 的 M 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_SigmaPP | Cs133 的 SigmaPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_SigmaP | Cs133 的 SigmaP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_PhiPP | Cs133 的 PhiPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_PhiPT | Cs133 的 PhiPT 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_Delta | Cs133 的 Delta 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_Cs133_MPhiPP | Cs133 的 MPhiPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 10] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_M | I127 的 M 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_SigmaPP | I127 的 SigmaPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_SigmaP | I127 的 SigmaP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 11] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_PhiPP | I127 的 PhiPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_PhiPT | I127 的 PhiPT 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_Delta | I127 的 Delta 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 9] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| nuclear_I127_MPhiPP | I127 的 MPhiPP 核响应多项式系数；升幂顺序。 | 1 | [2, 2, 10] | float64 | [{'name': 'nucleon_left', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'nucleon_right', 'values': ['p', 'n'], 'unit': '1'}, {'name': 'polynomial_power', 'rule': '0..shape[-1]-1', 'unit': '1'}] | direct_input | {'description': 'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization', 'quantity_kind': 'nuclear_coefficient', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| source_energy_MeV | SNS 插值表的完整节点坐标，保留掩码外零节点。 | MeV | [200] | float64 | [{'name': 'source_table_node', 'rule': 'increasing; includes both endpoints', 'unit': '1'}] | materialized_derived_resource | {'description': 'coordinate only', 'quantity_kind': 'coordinate', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| source_fluence_e | 当前运行的 delayed e 插值表节点注量。 | cm^-2 MeV^-1 | [200] | float64 | [{'name': 'source_table_node', 'coordinate_ref': 'source_energy_MeV', 'unit': 'MeV'}] | materialized_derived_resource | {'description': 'includes POT, yield and 1/(4*pi*L^2); excludes target nuclei, efficiency and acceptance; bound to declared source parameters', 'quantity_kind': 'integrated_detector_fluence_density', 'included_factors': ['POT', 'yield', 'geometry'], 'runtime_factors': [], 'runtime_authority': 'array'} |
| source_fluence_mub | 当前运行的 delayed mub 插值表节点注量。 | cm^-2 MeV^-1 | [200] | float64 | [{'name': 'source_table_node', 'coordinate_ref': 'source_energy_MeV', 'unit': 'MeV'}] | materialized_derived_resource | {'description': 'includes POT, yield and 1/(4*pi*L^2); excludes target nuclei, efficiency and acceptance; bound to declared source parameters', 'quantity_kind': 'integrated_detector_fluence_density', 'included_factors': ['POT', 'yield', 'geometry'], 'runtime_factors': [], 'runtime_authority': 'array'} |
| state_rho_e | 固定纯味密度矩阵 e；mu 与 mub 共用 rho_mu，粒子标签不同。 | 1 | [3, 3] | complex128 | [{'name': 'flavor_row', 'values': ['e', 'mu', 'tau'], 'unit': '1'}, {'name': 'flavor_column', 'values': ['e', 'mu', 'tau'], 'unit': '1'}] | direct_input | {'description': 'Hermitian PSD; trace=1', 'quantity_kind': 'density_matrix', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| state_rho_mu | 固定纯味密度矩阵 mu；mu 与 mub 共用 rho_mu，粒子标签不同。 | 1 | [3, 3] | complex128 | [{'name': 'flavor_row', 'values': ['e', 'mu', 'tau'], 'unit': '1'}, {'name': 'flavor_column', 'values': ['e', 'mu', 'tau'], 'unit': '1'}] | direct_input | {'description': 'Hermitian PSD; trace=1', 'quantity_kind': 'density_matrix', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| observable_pe_edges | 九箱的十条精确边界。 | PE | [10] | float64 | [{'name': 'edge_index', 'rule': 'ascending edge order', 'unit': '1'}] | direct_input | {'description': 'coordinate only; no background or exposure', 'quantity_kind': 'coordinate', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| statistics_observed | 旧 residual/excess 观测数组，末箱负值保留；背景扣除细节待官方证据。 | counts/PE | [9] | float64 | [{'name': 'pe_bin', 'edges_ref': 'observable_pe_edges', 'order': 'ascending PE', 'unit': 'PE'}] | direct_input | {'description': 'already per PE width; never divide this array by width again', 'quantity_kind': 'statistic_density', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| statistics_background | 旧 BRN+NIN 背景数组；实际 χ² 在信号之外加入该项。 | counts/PE | [9] | float64 | [{'name': 'pe_bin', 'edges_ref': 'observable_pe_edges', 'order': 'ascending PE', 'unit': 'PE'}] | direct_input | {'description': 'already per PE width; never divide this array by width again', 'quantity_kind': 'statistic_density', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |
| statistics_uncertainty | 逐箱对称 Gaussian 一标准差；不含额外协方差矩阵。 | counts/PE | [9] | float64 | [{'name': 'pe_bin', 'edges_ref': 'observable_pe_edges', 'order': 'ascending PE', 'unit': 'PE'}] | direct_input | {'description': 'already per PE width; never divide this array by width again', 'quantity_kind': 'statistic_density', 'included_factors': [], 'runtime_factors': [], 'runtime_authority': 'array'} |

| 物化数组 | 生成参数 | 生成模型 | 生成资源 | 依赖指纹 |
| --- | --- | --- | --- | --- |
| source_energy_MeV | ['source.tabulation_min', 'source.tabulation_max', 'source.tabulation_nodes'] | ['sns_michel_tabulation_legacy_v1'] | [] | c6728c94c54dc0046a6f4d60ca76bdb96b5bf7196389d1d4588aa45a6208ecc9 |
| source_fluence_e | ['source.baseline_m', 'source.total_pot', 'source.yield_per_pot', 'source.tabulation_min', 'source.tabulation_max', 'source.mask_min', 'source.mask_max', 'source.tabulation_nodes', 'source.interpolation', 'source.fluence_per_species', 'constants.m_mu'] | ['sns_michel_tabulation_legacy_v1', 'sns_fluence_legacy_v1'] | ['source_energy_MeV'] | 99a1cbc19a57b62e0bf13b1409f17d3168dc3537de0edd874682adac05f04f8a |
| source_fluence_mub | ['source.baseline_m', 'source.total_pot', 'source.yield_per_pot', 'source.tabulation_min', 'source.tabulation_max', 'source.mask_min', 'source.mask_max', 'source.tabulation_nodes', 'source.interpolation', 'source.fluence_per_species', 'constants.m_mu'] | ['sns_michel_tabulation_legacy_v1', 'sns_fluence_legacy_v1'] | ['source_energy_MeV'] | 99a1cbc19a57b62e0bf13b1409f17d3168dc3537de0edd874682adac05f04f8a |

数值数组保留原精度和顺序，可用 allow_pickle=False 读取。SigmaPDelta 未打包，因为旧粒子响应为零；没有添加协方差或 ROOTTime。

## 来源与缺失/冲突

| 来源ID | 相对路径 | SHA256 | 来源种类 | 独立官方核实 |
| --- | --- | --- | --- | --- |
| definition | cevns_pyeft/experiments/coherent/csi2021_definition.py | 5c289735de0009280d6798eecd90c46bac0edafefe7ddaf4fac160604472dad7 | project_code | False |
| assembly | cevns_pyeft/experiments/coherent/execution.py | 4a05c51c2398463bbd28b64b4d1120f21b0672156908afcefcacd9a936df34d3 | project_code | False |
| source | cevns_pyeft/experiments/coherent/sns.py | 6f7e8c6b4f48ecf9c58f95c06ae0d573199d137358c295812c4714908403f76f | project_code | False |
| source_adapter | cevns_pyeft/sources/sns.py | fa1efcc5d7c43e98bd07526a869515e245f5c84df41e088da1a860906fccf539 | project_code | False |
| detector_defaults | cevns_pyeft/detectors/legacy_parameters.py | 78e0cdfdce640ad61f5c73546d1f710a72dd8371866fc1fede90cc75793d1eae | project_code | False |
| detector | cevns_pyeft/detectors/csi2021.py | d842e806c76deb4ca26af5345eaec7a2e331e2709b1aaa453c6ecff70e89f98b | project_code | False |
| differential | cevns_pyeft/rates/differential.py | b6df0f0f6818afbc18dbc63d0edbedde041c891aaf219c40dc5c7014994482b9 | project_code | False |
| targets | cevns_pyeft/targets/materials.py | b1c5fe27da58e0fadee8c14371c8ca0db392495064a41e4dbe03fe4463cbac56 | project_code | False |
| recipes | cevns_pyeft/targets/recipes.py | 9d5b126970c773b69385f33a82da93ac3b6c6f5d956ef05cad3e88f35e6f8ad4 | project_code | False |
| constants | cevns_pyeft/foundation/constants.py | 0bb51033d1ca64e18a7a7bb0fd4cce38bc679558dd7392740f72d4683276cd44 | project_code | False |
| lecs | cevns_pyeft/theory/li2026/lec.py | 9c981d8705ba6a17829c75e81b93ce6f85fdbcc290faf5bf64edde9dc8867691 | project_code | False |
| operators | cevns_pyeft/theory/li2026/operators.py | c1932f6de64333b3a344fc84b7f5ec19efddbbf9a33db2aa9e245df702609ff4 | project_code | False |
| matching | cevns_pyeft/theory/li2026/left_to_ci.py | 56027d356737d85de4ae22ba3b303ade16e1c0163887bbedbc53ac2f0d46ae48 | project_code | False |
| particle_response | cevns_pyeft/theory/li2026/responses.py | 5edb06d4dd7409d0bac8245f9bf25b24f81f9e473e37f5e4f311492e9542f01b | project_code | False |
| amplitude | cevns_pyeft/theory/li2026/amplitude.py | 40a2bbfcb60716da67ff3d5182d5af6dd075bcd7dfccf9a49b9b3b0a8a9b7aed | project_code | False |
| cross_section | cevns_pyeft/theory/li2026/cross_section.py | adc13f3e1acc9b88b85fc033a6117cc2f99a77d1bc88e66368e416e4f5304393 | project_code | False |
| kinematics | cevns_pyeft/theory/kinematics.py | 2fcdeae7b83a1183c1215461e8d1f91badda142cb78ba7cb0fbb25367c69bd16 | project_code | False |
| response_reader | cevns_pyeft/nuclear/response.py | fc94a1582b11e58113e2f192be9733dfaf5b27b2604fe075da9e9f56b94d776f | project_code | False |
| response_data | data/responses/responses_all.json | cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74 | project_data | False |
| numerics | cevns_pyeft/contracts/parameters.py | 3d8b55c7ba12cab050637d3a988ba8e8a0316d738cb56e11f024f484253ca45a | project_code | False |
| prediction | cevns_pyeft/core/predict.py | 6c35de8c8bc7839daaa05ffd371c5f906c31b0a47b944f7b3f64dd14c1541eff | project_code | False |
| recoil | cevns_pyeft/rates/recoil.py | c300780a0d82fc812af113af27c1ffba52ac52cfce76ed715cb9424050b1251b | project_code | False |
| folding | cevns_pyeft/rates/folding.py | e1600e659d3dc5816095bdf395b6dc9ab78b57ed345e638c6a95b72eb0e076d1 | project_code | False |
| statistics_binding | cevns_pyeft/experiments/coherent/statistics_binding.py | 35a70e08cdf3202304888271fd6708c48ca05d2b949845e0cd91e3955bf00ffd | project_code | False |
| profiling | cevns_pyeft/statistics/profiling.py | 1ff56e0d802ec8b05ac8002633b070d8019e40895569dc083683029d0a26c120 | project_code | False |
| statistics_provenance | data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml | 6def82c1188dd1a1ead8bd0aca9f1dbd24bac4b7f59b78f96c0a559408a6146f | project_document | False |
| old_spec | data/experiments/COHERENT_CsI/CsI2021/experiment.yaml | 2ae1856bd5e06f0212108e41839d96c1407af913cf8260c1f4403691c9155645 | project_document | False |
| schema | workflows/_shared/schemas/experiment-input/experiment.schema.json | 86863330b1b5d2ea1186db9ef826187c454501e4e933c78488d9d9f6d0fcb29d | project_document | False |
| input_standard | workflows/_shared/INPUT_STANDARD.md | ca5bb442c8da9568f3e31abbb36f872abd728450a818f4b9f9d6d93e94d4d651 | project_document | False |
| antinu_audit | docs/physics/physics-audits/antineutrino_sign_helicity_audit.md | 981833b2ac3c7467329a3476407b31958e7c5b948893eb8cc5653e41e555d157 | project_document | False |
| nuclear_audit | docs/physics/nuclear-responses/nuclear_response_convention_audit.md | 3099756b80d46beb0105ac26ba864077c3340d6e3313b389a3a12dcc35ff265a | project_document | False |

| 问题 | 状态 | 内容 | 影响能力 | 所需材料 |
| --- | --- | --- | --- | --- |
| official_experiment_sources | MISSING | 未获得旧九箱实验的官方论文/补充材料版本、数据表及逐参数原值；不能比较官方值与采用值是否舍入或冲突。 | ['official_forward_reproduction', 'official_likelihood'] | 官方实验论文、补充材料、release 和校准参数表 |
| eft_primary_conventions | MISSING | 22 个内部算符 key、系数单位、味轴、扇区和完整 matching 数学表达式已提取；一手文献的逐算符 Lorentz/Lagrangian 定义与重整化尺度未独立核对，不能由内部名称反推并伪称物理约定已确认。 | ['official_EFT_operator_interpretation'] | 原理论文献中算符基、Lagrangian、matching 和尺度约定 |
| nuclear_source_audit | MISSING | 聚合 JSON 可读且打包无损，但外部源表、转换流程、所有通道符号/归一化未独立确认；I 的 M_nn(0) 存在已记录残差。 | ['externally_validated_nuclear_response'] | 核响应原始源表和生成流水线 |
| antineutrino_kernel | MISSING | antinu 标签已保存，当前与相同 rho 的 nu 共用截面核。一般 EFT 的反中微子符号/螺旋度尚未逐算符审查。 | ['fully_validated_general_antineutrino_EFT'] | 逐算符反中微子公式和外部检验 |
| statistics_semantics | CONFLICT | 旧 spec/README 写统计阻断；当前 definition/runtime 实际提供 legacy Gaussian。observed 称 residual/background-subtracted，而公式又加 BRN+NIN，具体已扣背景组成缺原始证据；两者保留，不把代码可运行等同物理确认。 | ['official_likelihood', 'verified_background_subtraction_semantics'] | 官方 residual、BRN/NIN 定义、背景扣除过程、完整 likelihood/covariance |
| legacy_status_and_reference | CONFLICT | 旧 spec 标 fast_validated，旧 README 停在 DATASET_VALIDATED，所引 CsI2021 run/reference 路径不存在。当前 tests/reference/interface_refactor_v1 与 interface_kernel_v1 确实存在，属于内部冻结兼容基线。 | ['historical_human_approval_reconstruction'] | 有效阶段报告和人工批准记录 |
| source_endpoint | MISSING | 旧节点掩码上限与 DAR 积分上限不同；谱被裁剪、线性插值且不重归一化，保留实际行为；不能宣称精确物理 Michel 端点归一化。 | ['independent_source_endpoint_claim'] | 源谱/插值约定人工审查 |
| detector_validity | MISSING | Gamma/quenching/efficiency 原始校准适用区间、CsI[Na] 掺杂影响、硬件阈值和分量接受率的确切时间选择未登记；仅声明当前代码和实际采样范围。 | ['official_detector_reproduction'] | 官方探测器校准、时间窗和有效域说明 |
| pilot_runtime | MISSING | 当前 Loader 不读取 experiment.input.yaml/NPZ；未实现或执行只用两个机器文件的独立 Runtime 加载。 | ['standalone_two_file_runtime'] | 后续显式 schema/model binding/NPZ adapter 任务 |

## 历史 spec 与迁移边界

{
  "path": "experiment.yaml",
  "status": "legacy_compatibility",
  "package_authority": "experiment.input.yaml",
  "runtime_authority": "package_yaml_npz",
  "retirement_task": "Task09",
  "conflicts": [
    "historical fast_validated is not package-only Fast validation",
    "historical statistics blocked means authoritative provenance missing, not absence of executable legacy Gaussian",
    "old phase/reference/run paths remain historical and cannot grant current human approval"
  ]
}

旧 experiment.yaml 为兼容说明；运行权威见上表。新包不继承旧 fast_validated 或官方统计批准。Schema、模型绑定、消费、Runtime 和人工科学接受分别记录；技术证据声明不等于校验器重跑了相关计算。
