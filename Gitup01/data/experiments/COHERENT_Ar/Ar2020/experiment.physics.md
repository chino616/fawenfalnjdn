# COHERENT_Ar / Ar2020 — Physics Input

## 目录

[1. 实验与数据集概述](#section-1)

[2. 实验输入](#section-2)

[3. 本实验的计算路径](#section-3)

[4. 本实验采用的物理模型](#section-4)

[5. 数值资源概览](#section-5)

[6. 适用范围、缺失与未决问题](#section-6)

[7. 来源与验证状态](#section-7)

[Appendix A. 公式索引](#equation-index) · [Appendix B. 参数索引](#parameter-index) · [Appendix C. 资源索引](#resource-index)

<a id="section-1"></a>

## 1. 实验与数据集概述

COHERENT_Ar / Ar2020 使用本包声明的 prompt_numu、delayed_nue、delayed_numubar，靶核素为 Ar40。观测量为 reconstructed PE spectrum，采用 12 个 PE 分箱。

平均观测量是反冲能量的二次函数；宽度使用观测 PE 的平方根。它不是以真实反冲能量决定宽度的通常 Gaussian；保留原实现的积分顺序和边界。 效率在声明的 PE 坐标上线性插值，左侧取 efficiency_low，右侧取最后表值；仅当合同给出阈值时，对不高于阈值的点取低值。

本包主张：legacy implementation compatibility only; no new scientific confirmation。当前描述的是声明输入及所选近似预测/统计路径；官方源、核响应约定、探测器校准和统计解释仍须按第 6 节的问题分别核实。

包状态：DRAFT；人工科学审核：NOT_REVIEWED。YAML 是标量和模型合同权威，NPZ 是数组权威；本文是派生说明，不授予新的运行或科学批准。

<a id="section-2"></a>

## 2. 实验输入

### Neutrino Source

| 分量 | 粒子 / 味态 | 连续谱 / 谱线 | 密度矩阵 |
| --- | --- | --- | --- |
| prompt_numu | nu | pion_DAR | rho_0 |
| delayed_nue | nu | source_fluence_1 | rho_1 |
| delayed_numubar | antinu | source_fluence_2 | rho_2 |

入射粒子种类、连续谱、谱线与味态按上表的显式声明读取；积分注量不重复乘 POT、产额、几何或活时间。

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`source.baseline_m`](#param-source-baseline_m) | 27.5 | m / direct_input | source.baseline_m; legacy-code-derived |
| [`source.total_pot`](#param-source-total_pot) | 1.38e+23 | POT / direct_input | source.total_pot; legacy-code-derived |
| [`source.yield_per_pot`](#param-source-yield_per_pot) | 0.09 | neutrinos/species/POT / direct_input | source.yield_per_pot; legacy-code-derived |
| [`source.tabulation_min`](#param-source-tabulation_min) | 0.001 | MeV / runtime_control | source.tabulation_min; legacy-code-derived |
| [`source.tabulation_max`](#param-source-tabulation_max) | 300.0 | MeV / runtime_control | source.tabulation_max; legacy-code-derived |
| [`source.mask_min`](#param-source-mask_min) | 0.001 | MeV / runtime_control | source.mask_min; legacy-code-derived |
| [`source.mask_max`](#param-source-mask_max) | 56.0 | MeV / runtime_control | source.mask_max; legacy-code-derived |
| [`source.tabulation_nodes`](#param-source-tabulation_nodes) | 200 | 1 / runtime_control | source.tabulation_nodes; legacy-code-derived |
| [`source.interpolation`](#param-source-interpolation) | true | boolean / runtime_control | source.interpolation; legacy-code-derived |
| [`source.integration_min`](#param-source-integration_min) | 0.0 | MeV / runtime_control | source.integration_min; legacy-code-derived |
| [`source.integration_max`](#param-source-integration_max) | 52.827952069788324 | MeV / derived | source.integration_max; legacy-code-derived |
| [`source.line_energy`](#param-source-line_energy) | 29.792140909877446 | MeV / derived | source.line_energy; legacy-code-derived |
| [`source.line_fluence`](#param-source-line_fluence) | 130691199550501.83 | cm^-2 / derived | source.line_fluence; legacy-code-derived |

### Target and Exposure

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`target.run_mass_metadata`](#param-target-run_mass_metadata) | 24.0 | kg / reference_only | target.run_mass_metadata; legacy-code-derived |
| [`target.detector_mass`](#param-target-detector_mass) | 24.0 | kg / direct_input | target.detector_mass; legacy-code-derived |
| [`target.atomic_mass_kg`](#param-target-atomic_mass_kg) | 1.6605390666e-27 | kg / direct_input | target.atomic_mass_kg; legacy-code-derived |
| [`target.Ar40.A`](#param-target-Ar40-A) | 40 | 1 / direct_input | target.Ar40.A; legacy-code-derived |
| [`target.Ar40.b`](#param-target-Ar40-b) | 9.831536784009149 | GeV^-1 / direct_input | target.Ar40.b; legacy-code-derived |
| [`target.Ar40.mass_GeV`](#param-target-Ar40-mass_GeV) | 37.2597641488 | GeV / derived | target.Ar40.mass_GeV; legacy-code-derived |
| [`target.Ar40.mass_kg`](#param-target-Ar40-mass_kg) | 6.6421562664e-26 | kg / derived | target.Ar40.mass_kg; legacy-code-derived |
| [`target.Ar40.mass_fraction`](#param-target-Ar40-mass_fraction) | 1.0 | 1 / derived | target.Ar40.mass_fraction; legacy-code-derived |
| [`target.Ar40.nuclei`](#param-target-Ar40-nuclei) | 3.613284457248674e+26 | nuclei / derived | target.Ar40.nuclei; legacy-code-derived |

### Theory and EFT Input

核子基底：np。matching 质量方案：`quark_mass_resolved`。SM 开关、弱混合角及 LEC 采用值见下表；proton/neutron 系数分开进入核响应，内部算符名不替代原始 Lagrangian 证据。

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`constants.G_F`](#param-constants-G_F) | 1.1663787e-05 | GeV^-2 / direct_input | constants.G_F; legacy-code-derived |
| [`constants.alpha_em`](#param-constants-alpha_em) | 0.0072973525643 | 1 / direct_input | constants.alpha_em; legacy-code-derived |
| [`constants.m_mu`](#param-constants-m_mu) | 0.10565837550000001 | GeV / direct_input | constants.m_mu; legacy-code-derived |
| [`constants.m_e`](#param-constants-m_e) | 0.0005109989506900001 | GeV / direct_input | constants.m_e; legacy-code-derived |
| [`constants.m_pi_charged`](#param-constants-m_pi_charged) | 0.13957039000000002 | GeV / direct_input | constants.m_pi_charged; legacy-code-derived |
| [`constants.AMU_GEV`](#param-constants-AMU_GEV) | 0.93149410372 | GeV / direct_input | constants.AMU_GEV; legacy-code-derived |
| [`constants.GEV_INV2_TO_CM2`](#param-constants-GEV_INV2_TO_CM2) | 3.893793721e-28 | cm^2/GeV^-2 / direct_input | constants.GEV_INV2_TO_CM2; legacy-code-derived |
| [`lecs.g_A`](#param-lecs-g_A) | 1.2754 | 1 / direct_input | lecs.g_A; legacy-code-derived |
| [`lecs.Sigma_ud`](#param-lecs-Sigma_ud) | 0.397 | 1 / unused_snapshot | lecs.Sigma_ud; legacy-code-derived |
| [`lecs.B0_m_u`](#param-lecs-B0_m_u) | 0.0062 | GeV^2 / direct_input | lecs.B0_m_u; legacy-code-derived |
| [`lecs.B0_m_d`](#param-lecs-B0_m_d) | 0.0133 | GeV^2 / direct_input | lecs.B0_m_d; legacy-code-derived |
| [`lecs.L1`](#param-lecs-L1) | 1.855 | 1 / direct_input | lecs.L1; legacy-code-derived |
| [`lecs.L2`](#param-lecs-L2) | -1.017 | 1 / direct_input | lecs.L2; legacy-code-derived |
| [`lecs.L3`](#param-lecs-L3) | 0.6377 | 1 / direct_input | lecs.L3; legacy-code-derived |
| [`lecs.L4`](#param-lecs-L4) | -0.22 | 1 / direct_input | lecs.L4; legacy-code-derived |
| [`lecs.L5`](#param-lecs-L5) | 0.00138 | GeV / direct_input | lecs.L5; legacy-code-derived |
| [`lecs.L6`](#param-lecs-L6) | -0.00049 | GeV / direct_input | lecs.L6; legacy-code-derived |
| [`lecs.L7`](#param-lecs-L7) | -0.0067599999999999995 | GeV / direct_input | lecs.L7; legacy-code-derived |
| [`lecs.L8`](#param-lecs-L8) | 0.00265 | GeV / direct_input | lecs.L8; legacy-code-derived |
| [`lecs.L9`](#param-lecs-L9) | 0.011519999999999999 | GeV / unused_snapshot | lecs.L9; legacy-code-derived |
| [`lecs.L10`](#param-lecs-L10) | 0.024050000000000002 | GeV / unused_snapshot | lecs.L10; legacy-code-derived |
| [`lecs.L11`](#param-lecs-L11) | -0.0177 | GeV / direct_input | lecs.L11; legacy-code-derived |
| [`lecs.L12`](#param-lecs-L12) | -0.013900000000000001 | GeV / direct_input | lecs.L12; legacy-code-derived |
| [`lecs.L13`](#param-lecs-L13) | -0.0504 | GeV / direct_input | lecs.L13; legacy-code-derived |
| [`lecs.L14`](#param-lecs-L14) | -0.306 | GeV / direct_input | lecs.L14; legacy-code-derived |
| [`lecs.sigma_u_p`](#param-lecs-sigma_u_p) | 0.0185 | GeV / direct_input | lecs.sigma_u_p; legacy-code-derived |
| [`lecs.sigma_d_p`](#param-lecs-sigma_d_p) | 0.036000000000000004 | GeV / direct_input | lecs.sigma_d_p; legacy-code-derived |
| [`lecs.sigma_u_n`](#param-lecs-sigma_u_n) | 0.0167 | GeV / direct_input | lecs.sigma_u_n; legacy-code-derived |
| [`lecs.sigma_d_n`](#param-lecs-sigma_d_n) | 0.039700000000000006 | GeV / direct_input | lecs.sigma_d_n; legacy-code-derived |
| [`lecs.g1`](#param-lecs-g1) | 1.0 | GeV / direct_input | lecs.g1; legacy-code-derived |
| [`lecs.g2`](#param-lecs-g2) | 1.0 | GeV / direct_input | lecs.g2; legacy-code-derived |
| [`lecs.g3`](#param-lecs-g3) | 1.0 | GeV / direct_input | lecs.g3; legacy-code-derived |
| [`lecs.g4`](#param-lecs-g4) | 1.0 | GeV / direct_input | lecs.g4; legacy-code-derived |
| [`lecs.g5`](#param-lecs-g5) | 1.0 | 1 / direct_input | lecs.g5; legacy-code-derived |
| [`lecs.g6`](#param-lecs-g6) | 1.0 | 1 / direct_input | lecs.g6; legacy-code-derived |
| [`lecs.g7`](#param-lecs-g7) | 1.0 | 1 / direct_input | lecs.g7; legacy-code-derived |
| [`lecs.g8`](#param-lecs-g8) | 1.0 | 1 / direct_input | lecs.g8; legacy-code-derived |
| [`lecs.g9`](#param-lecs-g9) | 1.0 | 1 / direct_input | lecs.g9; legacy-code-derived |
| [`lecs.m_u`](#param-lecs-m_u) | 0.00216 | GeV / unused_snapshot | lecs.m_u; legacy-code-derived |
| [`lecs.m_d`](#param-lecs-m_d) | 0.00467 | GeV / unused_snapshot | lecs.m_d; legacy-code-derived |
| [`lecs.m_pi`](#param-lecs-m_pi) | 0.13957039000000002 | GeV / direct_input | lecs.m_pi; legacy-code-derived |
| [`lecs.m_N`](#param-lecs-m_N) | 0.938918755685 | GeV / direct_input | lecs.m_N; legacy-code-derived |
| [`interaction.include_sm`](#param-interaction-include_sm) | true | boolean / direct_input | interaction.include_sm; legacy-code-derived |
| [`interaction.sin2thetaW`](#param-interaction-sin2thetaW) | 0.2387 | 1 / direct_input | interaction.sin2thetaW; legacy-code-derived |

### Nuclear Response Input

核素：Ar40；响应通道：Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPP。每个系数数组的轴为左核子 p/n、右核子 p/n、多项式升幂 k。保留来源归一化；SigmaPDelta 不参与当前收缩，对应公共粒子响应为零。外部源约定仍待核实。

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`nuclear.Ar40.exp_factor`](#param-nuclear-Ar40-exp_factor) | -2.0 | 1 / direct_input | nuclear.Ar40.exp_factor; legacy-code-derived |

### Detector Response

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`detector.efficiency_low`](#param-detector-efficiency_low) | 0.0 | 1 / direct_input | detector.efficiency_low; legacy-code-derived |
| [`detector.mean_linear`](#param-detector-mean_linear) | 0.246 | PE/keV / direct_input | detector.mean_linear; legacy-code-derived |
| [`detector.mean_quadratic`](#param-detector-mean_quadratic) | 0.00078 | PE/keV^2 / direct_input | detector.mean_quadratic; legacy-code-derived |
| [`detector.sigma_coefficient`](#param-detector-sigma_coefficient) | 0.58 | PE^0.5 / direct_input | detector.sigma_coefficient; legacy-code-derived |

### Observable and Numerical Controls

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`numerics.slow.n_er`](#param-numerics-slow-n_er) | 21 | 1 / runtime_control | numerics.slow.n_er; legacy-code-derived |
| [`numerics.slow.n_enu`](#param-numerics-slow-n_enu) | 120 | 1 / runtime_control | numerics.slow.n_enu; legacy-code-derived |
| [`numerics.slow.n_pe_bin`](#param-numerics-slow-n_pe_bin) | 8 | 1 / runtime_control | numerics.slow.n_pe_bin; legacy-code-derived |
| [`numerics.fast.n_er`](#param-numerics-fast-n_er) | 21 | 1 / runtime_control | numerics.fast.n_er; legacy-code-derived |
| [`numerics.fast.n_enu`](#param-numerics-fast-n_enu) | 120 | 1 / runtime_control | numerics.fast.n_enu; legacy-code-derived |
| [`numerics.fast.n_obs_sub`](#param-numerics-fast-n_obs_sub) | 8 | 1 / runtime_control | numerics.fast.n_obs_sub; legacy-code-derived |
| [`numerics.recoil_min_keV`](#param-numerics-recoil_min_keV) | 0.1 | keV / runtime_control | original recoil lower integration bound |

### Statistical Data

统计输入单位：counts/bin。仅执行所选旧近似，不称官方 likelihood。

| Parameter ID | 采用值 | 单位 / 角色 | 含义 |
| --- | --- | --- | --- |
| [`statistics.sigma_alpha`](#param-statistics-sigma_alpha) | 0.12 | 1 / direct_input | statistics.sigma_alpha; legacy-code-derived |
| [`statistics.sigma_beta`](#param-statistics-sigma_beta) | 0.146 | 1 / direct_input | statistics.sigma_beta; legacy-code-derived |

观测边界来自 `observable_edges`：0.001, 10.001, 20.001, 30.001, 40.001, 50.001, 60.001, 70.001, 80.001, 90.001, 100.001, 110.001, 120.001 PE。相邻箱按原合同处理端点，不从 bin_count 猜造坐标。

<a id="section-3"></a>

## 3. 本实验的计算路径

1. 读取每个连续注量数组或离散谱线及其入射味态；归一化因子各使用一次。

2. 分别计算 Ar40 的每核反冲产额，结合显式核响应与所选 EFT 系数。

3. 平均观测量是反冲能量的二次函数；宽度使用观测 PE 的平方根。它不是以真实反冲能量决定宽度的通常 Gaussian；保留原实现的积分顺序和边界。

4. 效率在声明的 PE 坐标上线性插值，左侧取 efficiency_low，右侧取最后表值；仅当合同给出阈值时，对不高于阈值的点取低值。

5. 使用声明的观测、背景及上下侧误差；按模型残差选择误差侧，迭代求解带归一化 pull 的旧 Gaussian 近似。这里保留程序合同，不另造闭式 likelihood，也不宣称官方统计。

<a id="section-4"></a>

## 4. 本实验采用的物理模型

### Neutrino Source

**已积分的源分量**（`integrated_fluence_components_v1`；experiment_specific）。连续谱直接读取声明的探测器注量数组，离散谱线使用各自能量和权重。POT、产额和几何已包含，运行时不再相乘，也不额外乘活时间。

边界：preserve existing interpolation, support and clipping; no scientific correction

### Target and Exposure

**显式核素计数**（`explicit_target_inventory_v1`；experiment_specific）。核素质量分数、单核质量和核数由机器输入逐项登记；kg 质量用于核数归一化，GeV 质量用于反冲运动学。运行采用 detector_mass，run_mass_metadata 仅作历史元数据。

<a id="eq-1"></a>

**(1) 核数与质量归一化**

$$
N_i=\frac{M_{\mathrm{det}}w_i}{m_{i,\mathrm{kg}}},\qquad\sum_iN_i m_{i,\mathrm{kg}}=M_{\mathrm{det}}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $i$ | 本包靶核素索引 | 1 | — |
| $M_{\mathrm{det}}$ | 实际计算靶质量 | kg | [`target.detector_mass`](#param-target-detector_mass) |
| $N_i$ | 各核素核数 | nuclei | — |
| $w_i$ | 各核素质量分数 | 1 | — |
| $m_{i,\mathrm{kg}}$ | 单核 kg 质量 | kg | — |
| $N_{\mathrm{Ar40}}$ | Ar40 核数 | nuclei | [`target.Ar40.nuclei`](#param-target-Ar40-nuclei) |
| $w_{\mathrm{Ar40}}$ | Ar40 质量分数 | 1 | [`target.Ar40.mass_fraction`](#param-target-Ar40-mass_fraction) |
| $m_{\mathrm{Ar40},kg}$ | Ar40 单核质量 | kg | [`target.Ar40.mass_kg`](#param-target-Ar40-mass_kg) |

边界：preserve existing interpolation, support and clipping; no scientific correction

### Theory and EFT Input

**本包的 EFT 截面接口**（`li2026_package_interaction_v1`；shared_framework）。使用 np 核子基底、显式 SM 开关和 LEC 参数；默认 BSM 映射为空。公共 matching 和粒子响应由已登记引擎提供，不在实验文档复制逐项表达式。

<a id="eq-2"></a>

**(2) 公共 matching 的概括关系**

$$
\begin{aligned}c_j^p&=\sum_o{\cal M}_{jo}^{p}(E,q^2;\mathrm{LEC})C_o\\c_j^n&=\sum_o{\cal M}_{jo}^{n}(E,q^2;\mathrm{LEC})C_o\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $c_j^p$ | 质子 NR 味矩阵：j=1..12 为 GeV^-2，j=13,14 为 GeV^-3 | 按 j | — |
| $c_j^n$ | 中子 NR 味矩阵；与质子分别匹配 | 按 j | — |
| ${\cal M}_{jo}^{p},{\cal M}_{jo}^{n}$ | 分别作用于质子和中子的公共线性匹配映射 | 由算符维数决定 | — |
| $C_o$ | LEFT Wilson 矩阵，最终味为行、初始味为列；d_o 是算符维数 | GeV^(4-d_o) | — |
| $o,j$ | LEFT 算符与 NR 算符索引 | 1 | — |
| $E$ | 入射中微子能量；MeV 输入在截面前转 GeV | GeV | — |
| $q^2$ | 带符号四动量转移平方；不是淬灭系数 | GeV^2 | — |
| $\mathrm{LEC}$ | 本包 lecs.* 参数集合，采用值集中列于实验输入 | 各参数单位 | — |

<a id="eq-3"></a>

**(3) 公共响应收缩**

$$
K=\sum_X\sum_{u,v\in\{p,n\}}R_X^{uv}W_X^{uv}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $K$ | 入射味空间 Hermitian 核 | GeV^-2 | — |
| $R_X^{uv}$ | 公共粒子响应味矩阵 | GeV^-2 | — |
| $W_X^{uv}$ | 选定核素的核结构响应 | 1 | — |
| $X$ | 本包响应通道 | 1 | — |
| $u,v$ | 左右核子指标 p/n | 1 | — |

<a id="eq-4"></a>

**(4) 弹性支撑与动量转移**

$$
\begin{aligned}T_{\max}(E)&=\frac{2E^2}{m_i+2E},&E_{\min}(T)&=\frac{T+\sqrt{T^2+2m_iT}}2\\|\mathbf q|^2&=2m_iT,&q^2&=T^2-|\mathbf q|^2\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $E$ | 入射中微子能量；MeV 输入在截面前转 GeV | GeV | — |
| $T$ | 真实核反冲；keV 输入在运动学前转 GeV | GeV | — |
| $m_i$ | 由下列核素参数选取的动力学质量 | GeV | — |
| $i$ | 本包靶核素索引 | 1 | — |
| $T_{\max},E_{\min}$ | 允许反冲上界与入射能阈值 | GeV | — |
| $\lvert\mathbf q\rvert^2$ | 三动量模平方，用于核响应 | GeV^2 | — |
| $q^2$ | 带符号四动量转移平方；不是淬灭系数 | GeV^2 | — |
| $m_{\mathrm{Ar40}}$ | Ar40 动力学核质量 | GeV | [`target.Ar40.mass_GeV`](#param-target-Ar40-mass_GeV) |

<a id="eq-5"></a>

**(5) 每核、每 keV 的截面**

$$
\frac{d\sigma_i}{dT_{\mathrm{keV}}}=\operatorname{Tr}(\rho K_i)\frac{m_i}{8\pi E^2}\,C_{\mathrm{conv}}\,10^{-6}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $d\sigma_i/dT_{\mathrm{keV}}$ | 每核微分截面 | cm^2/keV | — |
| $i$ | 本包靶核素索引 | 1 | — |
| $\rho$ | 选定源分量的入射密度矩阵 | 1 | — |
| $K_i$ | 该核素的味核 | GeV^-2 | — |
| $m_i$ | 由下列核素参数选取的动力学质量 | GeV | — |
| $E$ | 入射中微子能量；MeV 输入在截面前转 GeV | GeV | — |
| $T_{\mathrm{keV}}$ | keV 表示的反冲能 | keV | — |
| $C_{\mathrm{conv}}$ | GeV^-2 到 cm^2 的换算 | cm^2/GeV^-2 | [`constants.GEV_INV2_TO_CM2`](#param-constants-GEV_INV2_TO_CM2) |
| $m_{\mathrm{Ar40}}$ | Ar40 动力学核质量 | GeV | [`target.Ar40.mass_GeV`](#param-target-Ar40-mass_GeV) |

### Nuclear Response Input

**所选核响应**（`nuclear_polynomial_arrays_v1`；experiment_specific）。使用本包核素的质子/中子多项式系数；保留原始归一化，不额外除以核自旋或 4π。

<a id="eq-6"></a>

**(6) 本包核响应多项式**

$$
W_{X,i}^{uv}(y)=e^{e_i y}\sum_{k\ge0}w_{X,i,k}^{uv}y^k,\qquad y=\left(\frac{|\mathbf q|b_i}{2}\right)^2
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $W_{X,i}^{uv}$ | 核响应；u,v 分别为左右核子指标 p/n | 1 | — |
| $X$ | 本包显式采用的响应通道 | 1 | — |
| $i$ | 本包靶核素索引 | 1 | — |
| $u,v$ | 两个独立核子指标，顺序 p、n | 1 | — |
| $w_{X,i,k}^{uv}$ | NPZ 中按升幂 k 排列的系数 | 1 | — |
| $k$ | 非负整数幂索引 | 1 | — |
| $y$ | 无量纲核变量 | 1 | — |
| $\lvert\mathbf q\rvert$ | 三动量模 | GeV | — |
| $b_i$ | 核素 oscillator length | GeV^-1 | — |
| $e_i$ | 核素指数系数 | 1 | — |
| $b_{\mathrm{Ar40}}$ | Ar40 长度 | GeV^-1 | [`target.Ar40.b`](#param-target-Ar40-b) |
| $e_{\mathrm{Ar40}}$ | Ar40 指数 | 1 | [`nuclear.Ar40.exp_factor`](#param-nuclear-Ar40-exp_factor) |

边界：preserve existing interpolation, support and clipping; no scientific correction

### Detector Response

**观测坐标 Gaussian 响应**（`observed_gaussian_legacy_v1`；experiment_specific）。平均观测量是反冲能量的二次函数；宽度使用观测 PE 的平方根。它不是以真实反冲能量决定宽度的通常 Gaussian；保留原实现的积分顺序和边界。

<a id="eq-7"></a>

**(7) 观测坐标上的 Gaussian 关系**

$$
\begin{aligned}\mu(T)&=(a+b_TT)T,&s(x)&=c\sqrt{x}\\p(x\mid T)&=\begin{cases}\dfrac{\exp[-(x-\mu(T))^2/(2s(x)^2)]}{\sqrt{2\pi}s(x)},&x>0\\0,&x\le0\end{cases}\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID |
| --- | --- | --- | --- |
| $x$ | 重建光电子数 | PE | — |
| $T$ | 真实核反冲 | keV | — |
| $\mu$ | 平均观测 PE | PE | — |
| $s$ | 使用观测 x 的宽度 | PE | — |
| $p$ | 旧观测响应密度；不声称在固定 T 下严格单位归一 | PE^-1 | — |
| $a$ | 线性响应 | PE/keV | [`detector.mean_linear`](#param-detector-mean_linear) |
| $b_T$ | 二次响应 | PE/keV^2 | [`detector.mean_quadratic`](#param-detector-mean_quadratic) |
| $c$ | 分辨率系数 | PE^0.5 | [`detector.sigma_coefficient`](#param-detector-sigma_coefficient) |

边界：preserve existing interpolation, support and clipping; no scientific correction

**表格效率与阈值**（`legacy_efficiency_curve_v1`；experiment_specific）。效率在声明的 PE 坐标上线性插值，左侧取 efficiency_low，右侧取最后表值；仅当合同给出阈值时，对不高于阈值的点取低值。

边界：preserve existing interpolation, support and clipping; no scientific correction

### Statistical Data

**非对称误差 IRLS**（`asymmetric_irls_legacy_v1`；experiment_specific）。使用声明的观测、背景及上下侧误差；按模型残差选择误差侧，迭代求解带归一化 pull 的旧 Gaussian 近似。这里保留程序合同，不另造闭式 likelihood，也不宣称官方统计。

边界：preserve existing interpolation, support and clipping; no scientific correction

公共理论参照：[算符覆盖](../../../../docs/physics/interaction-theory/legacy_operator_coverage.md)、[反中微子符号与 helicity 审计](../../../../docs/physics/physics-audits/antineutrino_sign_helicity_audit.md)、[核响应约定](../../../../docs/physics/nuclear-responses/nuclear_response_convention_audit.md)。完整 matching、内部别名和粒子响应展开留在机器合同及公共实现；本文不逐项刊载。

<a id="section-5"></a>

## 5. 数值资源概览

| 物理模块 | 数组数 | NPZ keys |
| --- | --- | --- |
| source | 6 | `source_energy_MeV`, `rho_0`, `rho_1`, `source_fluence_1`, `rho_2`, `source_fluence_2` |
| nuclear | 7 | `nuclear_Ar40_M`, `nuclear_Ar40_SigmaPP`, `nuclear_Ar40_SigmaP`, `nuclear_Ar40_PhiPP`, `nuclear_Ar40_PhiPT`, `nuclear_Ar40_Delta`, `nuclear_Ar40_MPhiPP` |
| detector | 3 | `efficiency_energy`, `efficiency_values`, `observable_edges` |
| statistics | 4 | `statistics_observed`, `statistics_background`, `statistics_lower`, `statistics_upper` |

核响应数组与核素/通道的绑定：

| 核素 | 通道 → NPZ key |
| --- | --- |
| Ar40 | M → `nuclear_Ar40_M`; SigmaPP → `nuclear_Ar40_SigmaPP`; SigmaP → `nuclear_Ar40_SigmaP`; PhiPP → `nuclear_Ar40_PhiPP`; PhiPT → `nuclear_Ar40_PhiPT`; Delta → `nuclear_Ar40_Delta`; MPhiPP → `nuclear_Ar40_MPhiPP` |

数组保持原 dtype、shape、顺序和精度，使用 allow_pickle=False。轴、归一化、生成依赖及逐项哈希由 YAML/NPZ 校验；正文不复制机器审计清单。

<a id="section-6"></a>

## 6. 适用范围、缺失与未决问题

| 问题 ID / 状态 | 物理限制 | 影响 |
| --- | --- | --- |
| science_review / MISSING | external nuclear source, antinu convention, official statistics and detector validity not fully reviewed | scientific_release, official_likelihood |

<a id="section-7"></a>

## 7. 来源与验证状态

| 能力 | 已记录状态 | 人工审核 |
| --- | --- | --- |
| signal | PASS | NOT_REVIEWED |
| fast | PASS | NOT_REVIEWED |
| legacy_statistics | PASS | NOT_REVIEWED |
| official_likelihood | BLOCKED | NOT_REVIEWED |
| general_antineutrino_EFT | BLOCKED | NOT_REVIEWED |
| scientific_release | BLOCKED | NOT_REVIEWED |

这里显示已有状态；渲染只读取输入，不重新运行预测，不自动提升能力或科学接受。

| Source ID | 来源 / 定位 | 种类 / 独立官方核实 |
| --- | --- | --- |
| legacy | current registered definition, response JSON, declared detector/statistical files; not official primary confirmation | legacy_implementation / 未登记 |

<a id="equation-index"></a>

## Appendix A. 本报告公式索引

| 编号 | 公式 | 模型 ID |
| --- | --- | --- |
| [1](#eq-1) | 核数与质量归一化 | `explicit_target_inventory_v1` |
| [2](#eq-2) | 公共 matching 的概括关系 | `li2026_package_interaction_v1` |
| [3](#eq-3) | 公共响应收缩 | `li2026_package_interaction_v1` |
| [4](#eq-4) | 弹性支撑与动量转移 | `li2026_package_interaction_v1` |
| [5](#eq-5) | 每核、每 keV 的截面 | `li2026_package_interaction_v1` |
| [6](#eq-6) | 本包核响应多项式 | `nuclear_polynomial_arrays_v1` |
| [7](#eq-7) | 观测坐标上的 Gaussian 关系 | `observed_gaussian_legacy_v1` |

<a id="parameter-index"></a>

## Appendix B. 参数索引

这里只列身份、主文位置和来源；采用值只在第 2 节维护。

| Parameter ID | 主文位置 | 来源定位 |
| --- | --- | --- |
| <a id="param-source-baseline_m"></a>`source.baseline_m` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-total_pot"></a>`source.total_pot` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-yield_per_pot"></a>`source.yield_per_pot` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-tabulation_min"></a>`source.tabulation_min` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-tabulation_max"></a>`source.tabulation_max` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-mask_min"></a>`source.mask_min` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-mask_max"></a>`source.mask_max` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-tabulation_nodes"></a>`source.tabulation_nodes` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-interpolation"></a>`source.interpolation` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-target-run_mass_metadata"></a>`target.run_mass_metadata` | Target and Exposure | legacy; LEGACY_ONLY |
| <a id="param-target-detector_mass"></a>`target.detector_mass` | Target and Exposure | legacy; LEGACY_ONLY |
| <a id="param-constants-G_F"></a>`constants.G_F` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-alpha_em"></a>`constants.alpha_em` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-m_mu"></a>`constants.m_mu` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-m_e"></a>`constants.m_e` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-m_pi_charged"></a>`constants.m_pi_charged` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-AMU_GEV"></a>`constants.AMU_GEV` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-constants-GEV_INV2_TO_CM2"></a>`constants.GEV_INV2_TO_CM2` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g_A"></a>`lecs.g_A` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-Sigma_ud"></a>`lecs.Sigma_ud` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-B0_m_u"></a>`lecs.B0_m_u` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-B0_m_d"></a>`lecs.B0_m_d` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L1"></a>`lecs.L1` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L2"></a>`lecs.L2` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L3"></a>`lecs.L3` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L4"></a>`lecs.L4` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L5"></a>`lecs.L5` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L6"></a>`lecs.L6` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L7"></a>`lecs.L7` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L8"></a>`lecs.L8` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L9"></a>`lecs.L9` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L10"></a>`lecs.L10` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L11"></a>`lecs.L11` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L12"></a>`lecs.L12` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L13"></a>`lecs.L13` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-L14"></a>`lecs.L14` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-sigma_u_p"></a>`lecs.sigma_u_p` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-sigma_d_p"></a>`lecs.sigma_d_p` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-sigma_u_n"></a>`lecs.sigma_u_n` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-sigma_d_n"></a>`lecs.sigma_d_n` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g1"></a>`lecs.g1` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g2"></a>`lecs.g2` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g3"></a>`lecs.g3` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g4"></a>`lecs.g4` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g5"></a>`lecs.g5` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g6"></a>`lecs.g6` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g7"></a>`lecs.g7` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g8"></a>`lecs.g8` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-g9"></a>`lecs.g9` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-m_u"></a>`lecs.m_u` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-m_d"></a>`lecs.m_d` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-m_pi"></a>`lecs.m_pi` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-lecs-m_N"></a>`lecs.m_N` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-target-atomic_mass_kg"></a>`target.atomic_mass_kg` | Target and Exposure | legacy; LEGACY_ONLY |
| <a id="param-source-integration_min"></a>`source.integration_min` | Neutrino Source | legacy; LEGACY_ONLY |
| <a id="param-source-integration_max"></a>`source.integration_max` | Neutrino Source | legacy; PROJECT_DERIVED |
| <a id="param-source-line_energy"></a>`source.line_energy` | Neutrino Source | legacy; PROJECT_DERIVED |
| <a id="param-source-line_fluence"></a>`source.line_fluence` | Neutrino Source | legacy; PROJECT_DERIVED |
| <a id="param-target-Ar40-A"></a>`target.Ar40.A` | Target and Exposure | legacy; LEGACY_ONLY |
| <a id="param-target-Ar40-b"></a>`target.Ar40.b` | Target and Exposure | legacy; LEGACY_ONLY |
| <a id="param-nuclear-Ar40-exp_factor"></a>`nuclear.Ar40.exp_factor` | Nuclear Response Input | legacy; LEGACY_ONLY |
| <a id="param-target-Ar40-mass_GeV"></a>`target.Ar40.mass_GeV` | Target and Exposure | legacy; PROJECT_DERIVED |
| <a id="param-target-Ar40-mass_kg"></a>`target.Ar40.mass_kg` | Target and Exposure | legacy; PROJECT_DERIVED |
| <a id="param-target-Ar40-mass_fraction"></a>`target.Ar40.mass_fraction` | Target and Exposure | legacy; PROJECT_DERIVED |
| <a id="param-target-Ar40-nuclei"></a>`target.Ar40.nuclei` | Target and Exposure | legacy; PROJECT_DERIVED |
| <a id="param-detector-efficiency_low"></a>`detector.efficiency_low` | Detector Response | legacy; LEGACY_ONLY |
| <a id="param-detector-mean_linear"></a>`detector.mean_linear` | Detector Response | legacy; LEGACY_ONLY |
| <a id="param-detector-mean_quadratic"></a>`detector.mean_quadratic` | Detector Response | legacy; LEGACY_ONLY |
| <a id="param-detector-sigma_coefficient"></a>`detector.sigma_coefficient` | Detector Response | legacy; LEGACY_ONLY |
| <a id="param-statistics-sigma_alpha"></a>`statistics.sigma_alpha` | Statistical Data | legacy; LEGACY_ONLY |
| <a id="param-statistics-sigma_beta"></a>`statistics.sigma_beta` | Statistical Data | legacy; LEGACY_ONLY |
| <a id="param-interaction-include_sm"></a>`interaction.include_sm` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-interaction-sin2thetaW"></a>`interaction.sin2thetaW` | Theory and EFT Input | legacy; LEGACY_ONLY |
| <a id="param-numerics-slow-n_er"></a>`numerics.slow.n_er` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-slow-n_enu"></a>`numerics.slow.n_enu` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-slow-n_pe_bin"></a>`numerics.slow.n_pe_bin` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-fast-n_er"></a>`numerics.fast.n_er` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-fast-n_enu"></a>`numerics.fast.n_enu` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-fast-n_obs_sub"></a>`numerics.fast.n_obs_sub` | Observable and Numerical Controls | legacy; LEGACY_ONLY |
| <a id="param-numerics-recoil_min_keV"></a>`numerics.recoil_min_keV` | Observable and Numerical Controls | legacy; LEGACY_ONLY |

<a id="resource-index"></a>

## Appendix C. 数值资源索引

| NPZ key | shape / dtype | 单位 | Source ID |
| --- | --- | --- | --- |
| `source_energy_MeV` | [200] / float64 | MeV | legacy |
| `rho_0` | [3, 3] / complex128 | 1 | legacy |
| `rho_1` | [3, 3] / complex128 | 1 | legacy |
| `source_fluence_1` | [200] / float64 | cm^-2 MeV^-1 | legacy |
| `rho_2` | [3, 3] / complex128 | 1 | legacy |
| `source_fluence_2` | [200] / float64 | cm^-2 MeV^-1 | legacy |
| `nuclear_Ar40_M` | [2, 2, 7] / float64 | 1 | legacy |
| `nuclear_Ar40_SigmaPP` | [2, 2, 0] / float64 | 1 | legacy |
| `nuclear_Ar40_SigmaP` | [2, 2, 0] / float64 | 1 | legacy |
| `nuclear_Ar40_PhiPP` | [2, 2, 5] / float64 | 1 | legacy |
| `nuclear_Ar40_PhiPT` | [2, 2, 0] / float64 | 1 | legacy |
| `nuclear_Ar40_Delta` | [2, 2, 0] / float64 | 1 | legacy |
| `nuclear_Ar40_MPhiPP` | [2, 2, 6] / float64 | 1 | legacy |
| `efficiency_energy` | [80] / float64 | PE | legacy |
| `efficiency_values` | [80] / float64 | 1 | legacy |
| `observable_edges` | [13] / float64 | PE | legacy |
| `statistics_observed` | [12] / float64 | counts/bin | legacy |
| `statistics_background` | [12] / float64 | counts/bin | legacy |
| `statistics_lower` | [12] / float64 | counts/bin | legacy |
| `statistics_upper` | [12] / float64 | counts/bin | legacy |
