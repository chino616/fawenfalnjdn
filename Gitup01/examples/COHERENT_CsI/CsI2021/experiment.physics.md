# COHERENT CsI[Na] — CsI2021

[精简阅读版](experiment.physics.summary.md)

## 目录

[1. 实验范围](#section-1)

[2. Source](#section-2)

[3. Target](#section-3)

[4. 本实验选择的共享模块](#section-4)

[5. Detector](#section-5)

[6. Observable](#section-6)

[7. Prediction folding](#section-7)

[8. Statistics](#section-8)

[9. 数值资源](#section-9)

[10. 来源、限制与状态](#section-10)

[公式索引](#equation-index) · [参数索引](#parameter-index)

<a id="section-1"></a>

## 1. 实验范围

COHERENT CsI[Na] — CsI2021 使用 prompt_numu、delayed_nue、delayed_numubar，靶核素为 Cs133、I127；观测量为 reconstructed PE spectrum，共 9 个 PE 分箱。

科学主张：legacy_9bin_input_description; audit-ready extraction, not official physics confirmation。包状态 DRAFT / PARTIAL；人工科学审核 NOT_REVIEWED。

YAML 是标量与模型合同权威，NPZ 是数组权威；两份 Markdown 是同源派生说明。本文记录当前实验适配所需的输入与执行约定，不把旧实现恢复值认作官方论文原值。

当前是 POT 积分、无时间坐标的九箱配置；source.time_coordinate 为 null。不能据此构造 ROOTTime 或二维时间–能量分析。

<a id="section-2"></a>

## 2. Source

| 源分量 / 粒子标签 | 味态 NPZ | 连续谱 NPZ | 离散谱线 |
| --- | --- | --- | --- |
| prompt_numu / nu | [`state_rho_mu`](#res-state_rho_mu) | 无 | sns_prompt_line_v1 |
| delayed_nue / nu | [`state_rho_e`](#res-state_rho_e) | [`source_fluence_e`](#res-source_fluence_e) | 无 |
| delayed_numubar / antinu | [`state_rho_mu`](#res-state_rho_mu) | [`source_fluence_mub`](#res-source_fluence_mub) | 无 |

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`source.baseline_m`](#param-source-baseline_m) | 19.3 | m / direct_input | 源到探测器距离；几何稀释只在注量中施加。 |
| [`source.total_pot`](#param-source-total_pot) | 3.198e+23 | POT / direct_input | 本运行累计 POT；已经承载时间积分。 |
| [`source.yield_per_pot`](#param-source-yield_per_pot) | 0.0848 | neutrinos/species/POT / direct_input | 每种 SNS 分量的发射数系数。 |
| [`source.tabulation_min`](#param-source-tabulation_min) | 0.001 | MeV / runtime_control | SNS 线性插值表端点；不是积分端点。 |
| [`source.tabulation_max`](#param-source-tabulation_max) | 300.0 | MeV / runtime_control | SNS 线性插值表端点；不是积分端点。 |
| [`source.mask_min`](#param-source-mask_min) | 0.001 | MeV / runtime_control | 仅在生成表格节点时使用的旧程序掩码。 |
| [`source.mask_max`](#param-source-mask_max) | 56.0 | MeV / runtime_control | 仅在生成表格节点时使用的旧程序掩码。 |
| [`source.tabulation_nodes`](#param-source-tabulation_nodes) | 200 | 1 / runtime_control | SNS 等间距表节点数，含两端。 |
| [`source.interpolation`](#param-source-interpolation) | true | boolean / runtime_control | 采用线性插值的旧复现设置。 |
| [`source.fluence_per_species`](#param-source-fluence_per_species) | 579361763793233.6 | cm^-2 / derived | 每种分量的积分注量权重；连续谱未重新归一化。 |
| [`source.prompt_energy`](#param-source-prompt_energy) | 29.792140909877446 | MeV / derived | 静止带电 pion 两体衰变的 prompt νμ 能量。 |
| [`constants.m_mu`](#param-constants-m_mu) | 0.10565837550000001 | GeV / direct_input | muon 质量；记录当前公共常数版本的实际值。 |
| [`constants.m_pi_charged`](#param-constants-m_pi_charged) | 0.13957039000000002 | GeV / direct_input | 带电 pion 质量；记录当前公共常数版本的实际值。 |

### SNS 探测器注量

模型：`sns_fluence_legacy_v1`。静止 pion 源用球面几何因子将每 POT 的每种产额转成探测器注量。该因子已经积分整个运行时间。

<a id="eq-1"></a>

**(1) 每分量积分注量**

$$
F=\frac{rN_{\mathrm{POT}}}{4\pi(100L)^2}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $F$ | 每种源分量在探测器的积分注量 | cm^-2 | [`source.fluence_per_species`](#param-source-fluence_per_species) |
| $r$ | 每 POT、每分量产额 | neutrinos/species/POT | [`source.yield_per_pot`](#param-source-yield_per_pot) |
| $N_{\mathrm{POT}}$ | 积分质子数 | POT | [`source.total_pot`](#param-source-total_pot) |
| $L$ | 基线；100 将 m 转为 cm | m | [`source.baseline_m`](#param-source-baseline_m) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | [`source.total_pot`](#param-source-total_pot); [`source.yield_per_pot`](#param-source-yield_per_pot); [`source.baseline_m`](#param-source-baseline_m) |
| 输出 | F [cm^-2] |
| 定义域 | positive baseline; nonnegative POT/yield |
| 归一化 | per source component once |
| 边界/裁剪 | no live-time or target-mass multiplier |

### 延迟连续谱

模型：`sns_michel_tabulation_legacy_v1`。delayed νe 与反νμ 的 Michel 形状先在完整等间距表上计算、裁剪并掩码，再线性插值。不是每个查询点都重新施加物理端点截断。

<a id="eq-2"></a>

**(2) 延迟 Michel 形状**

$$
\begin{aligned}f_e(E_M)&=\frac{192E_M^2}{m_{\mu,M}^3}\left(\frac12-\frac{E_M}{m_{\mu,M}}\right)\\f_{\bar\mu}(E_M)&=\frac{64E_M^2}{m_{\mu,M}^3}\left(\frac34-\frac{E_M}{m_{\mu,M}}\right)\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $f_e,f_{\bar\mu}$ | 理想解析形状；实际使用已裁剪、掩码且未重新归一的表 | MeV^-1 | derived/constant（见定义） |
| $E_M$ | 连续谱能量坐标 | MeV | derived/constant（见定义） |
| $m_{\mu,M}$ | 下列 muon 质量乘 1000 后的 MeV 表示 | MeV | derived/constant（见定义） |
| $m_\mu$ | 机器登记的 muon 质量 | GeV | [`constants.m_mu`](#param-constants-m_mu) |

<a id="eq-3"></a>

**(3) 谱表网格、裁剪与 mask（数值物化规则）**

$$
\begin{aligned}E_j&=E_{\mathrm{tab,min}}+\frac{j}{n_{\mathrm{tab}}-1}(E_{\mathrm{tab,max}}-E_{\mathrm{tab,min}})\\\Phi_{\ell j}&=F\max\{f_\ell(E_j),0\}\,\mathbf1_{[E_{\mathrm{mask,min}},E_{\mathrm{mask,max}}]}(E_j)\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $E_j$ | 等间距表格的能量坐标；j=0..n_tab-1 | MeV | [`source_energy_MeV`](#res-source_energy_MeV) |
| $j$ | 谱表节点索引 | 1 | derived/constant（见定义） |
| $\ell$ | 本包源分量索引 | 1 | derived/constant（见定义） |
| $f_\ell$ | 上一式的 Michel 解析形状 | MeV^-1 | derived/constant（见定义） |
| $\Phi_{\ell j}$ | 节点上的探测器积分注量密度 | cm^-2 MeV^-1 | derived/constant（见定义） |
| $\Phi_{ej}$ | 电子分量节点表 | cm^-2 MeV^-1 | [`source_fluence_e`](#res-source_fluence_e) |
| $\Phi_{\bar\mu j}$ | 反 muon 分量节点表 | cm^-2 MeV^-1 | [`source_fluence_mub`](#res-source_fluence_mub) |
| $F$ | 每分量积分注量 | cm^-2 | [`source.fluence_per_species`](#param-source-fluence_per_species) |
| $E_{\mathrm{tab,min}}$ | 谱表下界 | MeV | [`source.tabulation_min`](#param-source-tabulation_min) |
| $E_{\mathrm{tab,max}}$ | 谱表上界 | MeV | [`source.tabulation_max`](#param-source-tabulation_max) |
| $n_{\mathrm{tab}}$ | 谱表节点数 | 1 | [`source.tabulation_nodes`](#param-source-tabulation_nodes) |
| $E_{\mathrm{mask,min}}$ | mask 下界 | MeV | [`source.mask_min`](#param-source-mask_min) |
| $E_{\mathrm{mask,max}}$ | mask 上界 | MeV | [`source.mask_max`](#param-source-mask_max) |
| $\mathbf1$ | 区间指示函数：在 mask 内为 1，否则为 0 | 1 | derived/constant（见定义） |

<a id="eq-4"></a>

**(4) 连续谱的线性插值（数值读取规则）**

$$
\phi_\ell(E)=\begin{cases}(1-t)\Phi_{\ell j}+t\Phi_{\ell,j+1},& E_j\le E\le E_{j+1}\\0,&E<E_{\mathrm{tab,min}}\ \text{or}\ E>E_{\mathrm{tab,max}}\end{cases},\qquad t=\frac{E-E_j}{E_{j+1}-E_j}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $\ell$ | 本包源分量索引 | 1 | derived/constant（见定义） |
| $E$ | 查询能量 | MeV | derived/constant（见定义） |
| $\phi_\ell$ | 插值后的积分注量密度 | cm^-2 MeV^-1 | derived/constant（见定义） |
| $E_j,E_{j+1}$ | 包围查询点的相邻节点，j=0..n_tab-2 | MeV | [`source_energy_MeV`](#res-source_energy_MeV) |
| $\Phi_{\ell j},\Phi_{\ell,j+1}$ | 上一式定义的相邻节点密度；按分量取对应 NPZ 表 | cm^-2 MeV^-1 | derived/constant（见定义） |
| $j$ | 插值区间索引 | 1 | derived/constant（见定义） |
| $t$ | 插值权重 | 1 | derived/constant（见定义） |
| $E_{\mathrm{tab,min}}$ | 谱表下界 | MeV | [`source.tabulation_min`](#param-source-tabulation_min) |
| $E_{\mathrm{tab,max}}$ | 谱表上界 | MeV | [`source.tabulation_max`](#param-source-tabulation_max) |

<a id="eq-5"></a>

**(5) 连续积分的实际 DAR 上界（衰变运动学）**

$$
E_{\mathrm{int,max}}=10^3\frac{m_\mu^2-m_e^2}{2m_\mu}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $E_{\mathrm{int,max}}$ | 当前运行使用的 MeV 上界 | MeV | [`source.integration_max`](#param-source-integration_max) |
| $m_\mu$ | muon 质量 | GeV | [`constants.m_mu`](#param-constants-m_mu) |
| $m_e$ | 电子质量 | GeV | [`constants.m_e`](#param-constants-m_e) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | [`source_energy_MeV`](#res-source_energy_MeV); [`source_fluence_e`](#res-source_fluence_e); [`source_fluence_mub`](#res-source_fluence_mub) |
| 输出 | phi_e,phi_mub [cm^-2 MeV^-1] |
| 定义域 | integration uses declared DAR domain; table and mask domains are separately declared |
| 归一化 | no re-normalization of clipped/interpolated table to F; analytic Michel functions integrate to 1 only on massless-electron ideal domain |
| 边界/裁剪 | linear interpolation; table-outside zero; final interpolation cell taper preserved |

### Prompt 谱线

模型：`sns_prompt_line_v1`。静止带电 pion 衰变产生 prompt νμ 谱线；积分直接加谱线权重乘截面。

<a id="eq-6"></a>

**(6) Prompt pion 衰变线**

$$
E_0=10^3\frac{m_\pi^2-m_\mu^2}{2m_\pi},\qquad\phi_\mu(E_M)=F\delta(E_M-E_0)
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $E_0$ | 谱线能量；GeV 质量换算为 MeV | MeV | [`source.prompt_energy`](#param-source-prompt_energy) |
| $m_\pi$ | 带电 pion 质量 | GeV | [`constants.m_pi_charged`](#param-constants-m_pi_charged) |
| $m_\mu$ | muon 质量 | GeV | [`constants.m_mu`](#param-constants-m_mu) |
| $F$ | 谱线的积分权重 | cm^-2 | [`source.fluence_per_species`](#param-source-fluence_per_species) |
| $E_M$ | 入射能量坐标 | MeV | derived/constant（见定义） |
| $\phi_\mu$ | prompt 注量密度 | cm^-2 MeV^-1 | derived/constant（见定义） |
| $\delta$ | Dirac delta 分布 | MeV^-1 | derived/constant（见定义） |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | [`constants.m_pi_charged`](#param-constants-m_pi_charged); [`constants.m_mu`](#param-constants-m_mu); [`source.fluence_per_species`](#param-source-fluence_per_species) |
| 输出 | line energy [MeV], weight [cm^-2] |
| 定义域 | stationary two-body pion decay |
| 归一化 | F once; no continuum prompt contribution |
| 边界/裁剪 | contributes iff E0 >= E_min(T) |

### 入射味态

模型：`sns_fixed_state_v1`。固定纯味入射态，无传播或随能量变化；particle_kind 单独保存。

<a id="eq-7"></a>

**(7) 固定纯味态**

$$
\rho_e=\begin{pmatrix}1&0&0\\0&0&0\\0&0&0\end{pmatrix},\qquad\rho_\mu=\begin{pmatrix}0&0&0\\0&1&0\\0&0&0\end{pmatrix}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $\rho_e$ | 电子味纯态，味序 e、mu、tau；trace 为 1 | 1 | [`state_rho_e`](#res-state_rho_e) |
| $\rho_\mu$ | muon 味纯态，味序 e、mu、tau；trace 为 1 | 1 | [`state_rho_mu`](#res-state_rho_mu) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | [`state_rho_e`](#res-state_rho_e); [`state_rho_mu`](#res-state_rho_mu) |
| 输出 | incident density and particle label |
| 定义域 | constant state only |
| 归一化 | trace(rho)=1 |
| 边界/裁剪 | state parameters rejected; antinu tag does not alter current kernel |

公式性质：积分注量是球面几何稀释与实验归一化输入；Michel 形状是无电子质量的理想衰变谱；prompt 线与积分上界来自衰变运动学；网格、mask 和插值是数值物化/读取规则。每 POT 产额的官方来源仍待核实。

理论 Michel 形状只在其理想支撑区间具有相应归一化。实际表先裁剪和 mask 再插值，包含末单元 taper；不在每个查询点重新截断到理想端点，也不将表重新归一化到 F。运行时 NPZ 已含 POT、产额和几何，连续谱不再乘 F；prompt 权重使用 F 一次。没有额外活时间因子。

<a id="section-3"></a>

## 3. Target

本包靶核素：Cs133, I127。质量分数、单核质量和核数的采用值只列于本节。

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`target.detector_mass`](#param-target-detector_mass) | 14.57 | kg / direct_input | 探测器总质量，只用于构造核数。 |
| [`target.atomic_mass_kg`](#param-target-atomic_mass_kg) | 1.6605390666e-27 | kg / direct_input | 旧程序核数换算的原子质量常数。 |
| [`target.Cs133.A`](#param-target-Cs133-A) | 133 | 1 / direct_input | 质量数 |
| [`target.Cs133.b`](#param-target-Cs133-b) | 11.644334960750054 | GeV^-1 / direct_input | 谐振子长度；用于 y=(qb/2)^2 |
| [`target.Cs133.mass_fraction`](#param-target-Cs133-mass_fraction) | 0.5115384615384615 | 1 / derived | Cs:I=1:1 化学计量转成质量分数。 |
| [`target.Cs133.mass_GeV`](#param-target-Cs133-mass_GeV) | 123.88871579475999 | GeV / derived | 弹性运动学的 A*AMU_GEV 近似质量。 |
| [`target.Cs133.mass_kg`](#param-target-Cs133-mass_kg) | 2.208516958578e-25 | kg / derived | 核数换算的 A*atomic_mass_kg 质量。 |
| [`target.I127.A`](#param-target-I127-A) | 127 | 1 / direct_input | 质量数 |
| [`target.I127.b`](#param-target-I127-b) | 11.566047952236252 | GeV^-1 / direct_input | 谐振子长度；用于 y=(qb/2)^2 |
| [`target.I127.mass_fraction`](#param-target-I127-mass_fraction) | 0.48846153846153845 | 1 / derived | Cs:I=1:1 化学计量转成质量分数。 |
| [`target.I127.mass_GeV`](#param-target-I127-mass_GeV) | 118.29975117244 | GeV / derived | 弹性运动学的 A*AMU_GEV 近似质量。 |
| [`target.I127.mass_kg`](#param-target-I127-mass_kg) | 2.108884614582e-25 | kg / derived | 核数换算的 A*atomic_mass_kg 质量。 |
| [`constants.AMU_GEV`](#param-constants-AMU_GEV) | 0.93149410372 | GeV / direct_input | 运动学原子质量常数；记录当前公共常数版本的实际值。 |

### CsI 核素计数

模型：`csi_target_inventory_v1`。每个 CsI 化学式单元各含一个 Cs 和 I，质量分数不同而核数相等。动力学质量与核数质量采用各自显式常数。

<a id="eq-8"></a>

**(8) CsI 化学计量与两种质量单位**

$$
w_i=\frac{A_i}{\sum_{j\in\mathrm{target}}A_j},\qquad m_{i,\mathrm{kg}}=A_i u_{\mathrm{kg}},\qquad m_{i,\mathrm{GeV}}=A_i u_{\mathrm{GeV}}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $i$ | 本包靶核素索引 | 1 | derived/constant（见定义） |
| $j$ | 化学式中核素索引，每个 CsI 单元各一个 Cs 和 I | 1 | derived/constant（见定义） |
| $A_i$ | 核素质量数 | 1 | derived/constant（见定义） |
| $w_i$ | 核素质量分数 | 1 | derived/constant（见定义） |
| $m_{i,\mathrm{kg}}$ | 用于核数的单核质量 | kg | derived/constant（见定义） |
| $m_{i,\mathrm{GeV}}$ | 用于运动学的单核质量 | GeV | derived/constant（见定义） |
| $u_{\mathrm{kg}}$ | kg 原子质量常数 | kg | [`target.atomic_mass_kg`](#param-target-atomic_mass_kg) |
| $u_{\mathrm{GeV}}$ | GeV 原子质量常数 | GeV | [`constants.AMU_GEV`](#param-constants-AMU_GEV) |
| $A_{Cs133}$ | Cs133 质量数 | 1 | [`target.Cs133.A`](#param-target-Cs133-A) |
| $A_{I127}$ | I127 质量数 | 1 | [`target.I127.A`](#param-target-I127-A) |

<a id="eq-9"></a>

**(9) 核数与质量归一化**

$$
N_i=\frac{M_{\mathrm{det}}w_i}{m_{i,\mathrm{kg}}},\qquad\sum_iN_i m_{i,\mathrm{kg}}=M_{\mathrm{det}}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $i$ | 本包靶核素索引 | 1 | derived/constant（见定义） |
| $M_{\mathrm{det}}$ | 实际计算靶质量 | kg | [`target.detector_mass`](#param-target-detector_mass) |
| $N_i$ | 各核素核数 | nuclei | derived/constant（见定义） |
| $w_i$ | 各核素质量分数 | 1 | derived/constant（见定义） |
| $m_{i,\mathrm{kg}}$ | 单核 kg 质量 | kg | derived/constant（见定义） |
| $N_{\mathrm{Cs133}}$ | Cs133 核数 | nuclei | [`target.Cs133.nuclei`](#param-target-Cs133-nuclei) |
| $w_{\mathrm{Cs133}}$ | Cs133 质量分数 | 1 | [`target.Cs133.mass_fraction`](#param-target-Cs133-mass_fraction) |
| $m_{\mathrm{Cs133},kg}$ | Cs133 单核质量 | kg | [`target.Cs133.mass_kg`](#param-target-Cs133-mass_kg) |
| $N_{\mathrm{I127}}$ | I127 核数 | nuclei | [`target.I127.nuclei`](#param-target-I127-nuclei) |
| $w_{\mathrm{I127}}$ | I127 质量分数 | 1 | [`target.I127.mass_fraction`](#param-target-I127-mass_fraction) |
| $m_{\mathrm{I127},kg}$ | I127 单核质量 | kg | [`target.I127.mass_kg`](#param-target-I127-mass_kg) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | [`target.detector_mass`](#param-target-detector_mass); [`target.atomic_mass_kg`](#param-target-atomic_mass_kg); [`constants.AMU_GEV`](#param-constants-AMU_GEV) |
| 输出 | isotope inventory with true nucleus counts |
| 定义域 | Cs133/I127 only; equal Cs:I stoichiometry; no explicit Na dopant model |
| 归一化 | sum_i N_i*m_i=Mdet; source does not contain nuclei or mass |
| 边界/裁剪 | zero detector mass gives zero counts |

<a id="section-4"></a>

## 4. 本实验选择的共享模块

Interaction 与 Nuclear Structure 是独立选择维度；下表只登记现有模块，不展开 matching、Particle Response、Nuclear Response、Helm、运动学或公共截面公式。

| 选择维度 | 实际 model ID | 已记录绑定状态 |
| --- | --- | --- |
| Interaction / 组合接口 | `li2026_sm_left_v1` | BOUND_AND_TESTED |
| Interaction / 组合接口 | `li2026_matching_v1` | BOUND_AND_TESTED |
| Kinematics / Cross-section | `elastic_kinematics_v1` | BOUND_AND_TESTED |
| Nuclear Structure | `nuclear_np_polynomial_v1` | BOUND_AND_TESTED |
| Interaction / 组合接口 | `li2026_R_W_kernel_v1` | BOUND_AND_TESTED |
| Kinematics / Cross-section | `li2026_dsigma_v1` | BOUND_AND_TESTED |

| 必要配置 | 当前选择 |
| --- | --- |
| theory / revision | `li2026_legacy` / current-07-onebody-proof-convention; source hashes pinned |
| 核子基底 / matching 质量方案 | np / quark_mass_resolved |
| 默认 BSM coefficient map | {} |
| SM / 弱混合角 | [`interaction.include_sm`](#param-interaction-include_sm) = true; [`interaction.sin2thetaW`](#param-interaction-sin2thetaW) = 0.2387 |
| LEC 配置 | YAML 中 lecs.* 的直接输入/只读状态；本报告参数索引给出精确 ID |
| 味序 / 系数矩阵轴 | ['e', 'mu', 'tau'] / {'row': 'final flavor', 'column': 'initial flavor'} |
| Nuclear Structure 资源 | 各核素/通道的 NPZ 系数绑定见第 9 节；未选择 Helm |

当前实际绑定合同入口：[v1 模型合同](../../../cevns_pyeft/experiments/model_bindings.json)、[v2 组件合同](../../../cevns_pyeft/experiments/component_bindings.json)。外部理论与核结构约定的未决问题保留在第 10 节，不以失效的历史文档链接代替证据。

<a id="section-5"></a>

## 5. Detector

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`target.Cs133.nuclei`](#param-target-Cs133-nuclei) | 3.3747150347508443e+25 | nuclei / derived | 实际参与计算的靶核数。 |
| [`target.I127.nuclei`](#param-target-I127-nuclei) | 3.374715034750844e+25 | nuclei / derived | 实际参与计算的靶核数。 |
| [`detector.quenching_q1`](#param-detector-quenching_q1) | 0.0554628 | 1 / direct_input | 按一至四次幂顺序的 quenching 系数 q1；输入数值以 MeVnr 表示。 |
| [`detector.quenching_q2`](#param-detector-quenching_q2) | 4.30681 | MeV^-1 / direct_input | 按一至四次幂顺序的 quenching 系数 q2；输入数值以 MeVnr 表示。 |
| [`detector.quenching_q3`](#param-detector-quenching_q3) | -111.707 | MeV^-2 / direct_input | 按一至四次幂顺序的 quenching 系数 q3；输入数值以 MeVnr 表示。 |
| [`detector.quenching_q4`](#param-detector-quenching_q4) | 840.384 | MeV^-3 / direct_input | 按一至四次幂顺序的 quenching 系数 q4；输入数值以 MeVnr 表示。 |
| [`detector.gamma_a`](#param-detector-gamma_a) | 0.0749 | keVee/PE / direct_input | Gamma 参数 a0；均值 PE=Eee/a0。 |
| [`detector.gamma_b`](#param-detector-gamma_b) | 9.56 | keVee^-1 / direct_input | Gamma 参数 b0；shape=1+b0*Eee。 |
| [`detector.efficiency_a`](#param-detector-efficiency_a) | 1.32045 | 1 / direct_input | logistic 振幅 |
| [`detector.efficiency_b`](#param-detector-efficiency_b) | 0.285979 | PE^-1 / direct_input | logistic 陡度 |
| [`detector.efficiency_c`](#param-detector-efficiency_c) | 10.8646 | PE / direct_input | logistic 中心 |
| [`detector.efficiency_d`](#param-detector-efficiency_d) | -0.3333 | 1 / direct_input | logistic 常数偏移 |
| [`detector.acceptance_e`](#param-detector-acceptance_e) | 0.848 | 1 / direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 |
| [`detector.acceptance_mu`](#param-detector-acceptance_mu) | 0.997 | 1 / direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 |
| [`detector.acceptance_mub`](#param-detector-acceptance_mub) | 0.848 | 1 / direct_input | 源分量选择接受率；在 PE 折叠后施加一次。 |

### CsI 淬灭映射

模型：`csi_quenching_legacy_v1`。真实核反冲映射成电子等效能量；四个系数的顺序固定。这里没有另乘一组光产额参数。

<a id="eq-10"></a>

**(10) CsI 淬灭**

$$
t=10^{-3}T_{\mathrm{keV}},\qquad E_{\mathrm{ee}}=10^3\sum_{j=1}^{4}q_j t^j
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $T_{\mathrm{keV}}$ | 核反冲能 | keV | derived/constant（见定义） |
| $t$ | 换为 MeV 的核反冲能 | MeV | derived/constant（见定义） |
| $E_{\mathrm{ee}}$ | 电子等效能量 | keVee | derived/constant（见定义） |
| $j$ | 淬灭多项式阶数 | 1 | derived/constant（见定义） |
| $q_1$ | 第 1 阶淬灭系数；不同于四动量平方 | 1 | [`detector.quenching_q1`](#param-detector-quenching_q1) |
| $q_2$ | 第 2 阶淬灭系数；不同于四动量平方 | MeV^-1 | [`detector.quenching_q2`](#param-detector-quenching_q2) |
| $q_3$ | 第 3 阶淬灭系数；不同于四动量平方 | MeV^-2 | [`detector.quenching_q3`](#param-detector-quenching_q3) |
| $q_4$ | 第 4 阶淬灭系数；不同于四动量平方 | MeV^-3 | [`detector.quenching_q4`](#param-detector-quenching_q4) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | recoil |
| 输出 | electron-equivalent energy [keVee] |
| 定义域 | actual sampled recoil range from declared grid; official calibration range missing |
| 归一化 | energy conversion only |
| 边界/裁剪 | nonpositive Eee causes response density zero |

### Gamma PE 响应

模型：`legacy_csi_gamma`。Gamma 用 shape-rate 参数化：k 是 shape，lambda 是 rate，scale=1/lambda。它表示 PE 的条件密度而非 bin 概率。

<a id="eq-11"></a>

**(11) Shape-rate Gamma 响应**

$$
\begin{aligned}k&=1+b_0E_{\mathrm{ee}},&\lambda&=\frac{a_0}{E_{\mathrm{ee}}}k\\p(x\mid T)&=\frac{\lambda^k}{\Gamma(k)}x^{k-1}e^{-\lambda x},&\langle x\rangle&=\frac{E_{\mathrm{ee}}}{a_0},\quad\operatorname{Var}(x)=\frac{k}{\lambda^2}\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $x$ | 重建光电子数 | PE | derived/constant（见定义） |
| $T$ | 真实反冲，先经淬灭映射 | keV | derived/constant（见定义） |
| $E_{\mathrm{ee}}$ | 电子等效能量 | keVee | derived/constant（见定义） |
| $a_0$ | Gamma 能量/PE 系数 | keVee/PE | [`detector.gamma_a`](#param-detector-gamma_a) |
| $b_0$ | Gamma shape 系数 | keVee^-1 | [`detector.gamma_b`](#param-detector-gamma_b) |
| $k$ | shape；不是 rate | 1 | derived/constant（见定义） |
| $\lambda$ | rate；scale 是其倒数 | PE^-1 | derived/constant（见定义） |
| $p$ | 条件 PE 密度 | PE^-1 | derived/constant（见定义） |
| $\Gamma$ | Euler Gamma 函数 | 1 | derived/constant（见定义） |
| $\langle x\rangle$ | 条件平均 PE | PE | derived/constant（见定义） |
| $\operatorname{Var}(x)$ | 条件方差 | PE^2 | derived/constant（见定义） |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | electron-equivalent energy; observed PE |
| 输出 | response density [PE^-1] |
| 定义域 | Eee>0 and x>0 |
| 归一化 | integral over x in (0,infinity)=1; not renormalized to analysis window |
| 边界/裁剪 | x<=0 or Eee<=0 gives zero; log evaluation uses max(x,1e-300) |

### PE 选择效率

模型：`csi2021_logistic_legacy`。重建 PE 上的选择效率，参数按 (a,b,c,d) 顺序。实现只有零下限，不能擅自改成双边裁剪。

<a id="eq-12"></a>

**(12) 重建 PE 上的效率**

$$
\epsilon(x)=\max\left\{\frac{a}{1+e^{-b_\epsilon(x-c)}}+d,\ 0\right\}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $x$ | 重建光电子数 | PE | derived/constant（见定义） |
| $\epsilon$ | 选择效率 | 1 | derived/constant（见定义） |
| $a$ | 振幅 | 1 | [`detector.efficiency_a`](#param-detector-efficiency_a) |
| $b_\epsilon$ | 斜率 | PE^-1 | [`detector.efficiency_b`](#param-detector-efficiency_b) |
| $c$ | 中心 | PE | [`detector.efficiency_c`](#param-detector-efficiency_c) |
| $d$ | 偏移 | 1 | [`detector.efficiency_d`](#param-detector-efficiency_d) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | observed PE |
| 输出 | efficiency [1] |
| 定义域 | sampled analysis window |
| 归一化 | dimensionless; applied after interpolation in current Slow strategy |
| 边界/裁剪 | lower-clamped at zero; folding rejects efficiency outside [0,1] on queried grid |

### 分量接受率

模型：`legacy_component_acceptance`。prompt 与 delayed 分量使用各自的选择接受率；时间变化、时间坐标和硬件阈值没有由此补造。

<a id="eq-13"></a>

**(13) 分量选择接受率的施加**

$$
N_{\ell i,b}=A_\ell N_i N^{\mathrm{pre}}_{\ell i,b}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $\ell$ | 本包源分量索引 | 1 | derived/constant（见定义） |
| $i$ | 本包靶核素索引 | 1 | derived/constant（见定义） |
| $b$ | 观测分箱索引 | 1 | derived/constant（见定义） |
| $N_{\ell i,b}$ | 该分量/核素的选后逐箱计数 | events/bin | derived/constant（见定义） |
| $N_i$ | 第 3 节登记的核数 | nuclei | derived/constant（见定义） |
| $N^{\mathrm{pre}}_{\ell i,b}$ | 已经完成 PE 响应、效率和分箱的每核产额 | events/nucleus/bin | derived/constant（见定义） |
| $A_\ell$ | 独立分量接受率；不包含在注量、PE 响应或效率中 | 1 | derived/constant（见定义） |
| $A_{\mathrm{mu}}$ | mu 分量接受率 | 1 | [`detector.acceptance_mu`](#param-detector-acceptance_mu) |
| $A_{\mathrm{e}}$ | e 分量接受率 | 1 | [`detector.acceptance_e`](#param-detector-acceptance_e) |
| $A_{\mathrm{mub}}$ | mub 分量接受率 | 1 | [`detector.acceptance_mub`](#param-detector-acceptance_mub) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | preselection counts; target inventory |
| 输出 | counts [events/bin] |
| 定义域 | three declared SNS components |
| 归一化 | exactly once; not already in fluence or efficiency |
| 边界/裁剪 | analysis-window losses are excluded, not redistributed |

施加顺序：真实反冲 → 淬灭得到 Eee → Gamma PE 条件密度 → 反冲积分和 PE 密度采样 → PE 插值 → 重建 PE 效率 → 箱积分 → 分量接受率及靶核数。Gamma 使用 shape-rate，scale 为 rate 的倒数；分析窗口损失不重分配。效率只有零下限，查询网格超出 [0,1] 会由已有 folding 合同拒绝。

<a id="section-6"></a>

## 6. Observable

观测量：reconstructed PE spectrum；坐标单位 PE；共 9 箱。

唯一 bin-edge 数组：[`observable_pe_edges`](#res-observable_pe_edges)。完整边界为 0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001 PE。

| Bin | 下边界 | 上边界 | 宽度 |
| --- | --- | --- | --- |
| 1 | 0.001 | 8.001 | 7.999999999999999 |
| 2 | 8.001 | 12.001 | 4.0 |
| 3 | 12.001 | 16.001 | 4.000000000000002 |
| 4 | 16.001 | 20.001 | 4.0 |
| 5 | 20.001 | 24.001 | 4.0 |
| 6 | 24.001 | 32.001 | 7.9999999999999964 |
| 7 | 32.001 | 40.001 | 8.0 |
| 8 | 40.001 | 48.001 | 8.0 |
| 9 | 48.001 | 60.001 | 12.0 |

边界约定：half-open adjacent bins; final upper edge retained; quadrature integrates endpoints

预测单位 events/bin；统计原生单位 counts/PE。预测是 signal only，已含效率、接受率、POT 与核数，不在预测阶段扣背景或除箱宽。

<a id="section-7"></a>

## 7. Prediction folding

1. 读取声明的连续积分注量、谱线与入射味态，不重复乘源归一化因子。

2. 逐核素调用第 4 节选定公共截面，得到每核反冲产额；公共模块的输入输出按既有合同。

3. 真实核反冲映射成电子等效能量；四个系数的顺序固定。这里没有另乘一组光产额参数。

4. Gamma 用 shape-rate 参数化：k 是 shape，lambda 是 rate，scale=1/lambda。它表示 PE 的条件密度而非 bin 概率。

5. 重建 PE 上的选择效率，参数按 (a,b,c,d) 顺序。实现只有零下限，不能擅自改成双边裁剪。

6. prompt 与 delayed 分量使用各自的选择接受率；时间变化、时间坐标和硬件阈值没有由此补造。

7. 总预测式同时保留当前数值运算次序：先按反冲积分出 PE 密度，按每 kg 中间量裁剪，再插值、效率、bin 积分，最后恢复每核归一化并乘真实核数。中间质量因子代数抵消，不能再额外乘 Mdet。

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`source.integration_min`](#param-source-integration_min) | 0.0 | MeV / runtime_control | 连续谱积分网格下限；零能节点不送入截面。 |
| [`source.integration_max`](#param-source-integration_max) | 52.827952069788324 | MeV / derived | 包含电子质量的 muon DAR 积分上限。 |
| [`constants.m_e`](#param-constants-m_e) | 0.0005109989506900001 | GeV / direct_input | 电子质量；记录当前公共常数版本的实际值。 |
| [`numerics.n_er`](#param-numerics-n_er) | 21 | 1 / runtime_control | 每核素反冲网格节点数；线性且含端点。 |
| [`numerics.n_enu`](#param-numerics-n_enu) | 120 | 1 / runtime_control | 连续谱能量网格节点数；各反冲只保留运动学允许节点。 |
| [`numerics.n_observed_bin`](#param-numerics-n_observed_bin) | 8 | 1 / runtime_control | 每 PE bin 子网格节点数；含端点。 |
| [`numerics.observed_step`](#param-numerics-observed_step) | 3.0 | PE / runtime_control | 先采样 PE 密度的等间距步长。 |
| [`numerics.recoil_min_keV`](#param-numerics-recoil_min_keV) | 0.1 | keV / runtime_control | 实际反冲网格下限。 |

### 逐箱预测与数值顺序

模型：`legacy_csi2021_v1`。总预测式同时保留当前数值运算次序：先按反冲积分出 PE 密度，按每 kg 中间量裁剪，再插值、效率、bin 积分，最后恢复每核归一化并乘真实核数。中间质量因子代数抵消，不能再额外乘 Mdet。

<a id="eq-14"></a>

**(14) 实验折叠的物理关系**

$$
\begin{aligned}Y_{\ell i}(T)&=\int_{\mathrm{allowed}}dE\,\phi_\ell(E)\frac{d\sigma_{\ell i}}{dT}+\sum_s F_s\frac{d\sigma_{\ell i}(E_s,T)}{dT}\\N_b&=\sum_{\ell,i}N_i A_\ell\int_{x_b}^{x_{b+1}}dx\,\epsilon(x)\int dT\,p(x\mid T)Y_{\ell i}(T)\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $\ell$ | 本包源分量索引 | 1 | derived/constant（见定义） |
| $i$ | 本包靶核素索引 | 1 | derived/constant（见定义） |
| $b$ | 观测分箱索引 | 1 | derived/constant（见定义） |
| $T$ | 核反冲积分变量 | keV | derived/constant（见定义） |
| $E$ | 源能量积分变量 | MeV | derived/constant（见定义） |
| $x$ | 重建光电子数 | PE | derived/constant（见定义） |
| $Y_{\ell i}$ | 每核反冲产额 | events/nucleus/keV | derived/constant（见定义） |
| $\phi_\ell$ | 已积分连续注量密度 | cm^-2 MeV^-1 | derived/constant（见定义） |
| $d\sigma_{\ell i}/dT$ | 每核截面 | cm^2/keV | derived/constant（见定义） |
| $s$ | 离散谱线索引 | 1 | derived/constant（见定义） |
| $F_s$ | 当前谱线使用的积分注量 | cm^-2 | [`source.fluence_per_species`](#param-source-fluence_per_species) |
| $E_s$ | 当前谱线能量 | MeV | [`source.prompt_energy`](#param-source-prompt_energy) |
| $N_i$ | 靶核数 | nuclei | derived/constant（见定义） |
| $A_\ell$ | 分量接受率 | 1 | derived/constant（见定义） |
| $N_b$ | 逐箱信号 | events/bin | derived/constant（见定义） |
| $\epsilon$ | PE 选择效率 | 1 | derived/constant（见定义） |
| $p$ | Gamma 条件密度 | PE^-1 | derived/constant（见定义） |
| $x_b,x_{b+1}$ | NPZ 登记的相邻箱边界 | PE | derived/constant（见定义） |
| $A_{\mathrm{e}}$ | e 分量接受率 | 1 | [`detector.acceptance_e`](#param-detector-acceptance_e) |
| $A_{\mathrm{mu}}$ | mu 分量接受率 | 1 | [`detector.acceptance_mu`](#param-detector-acceptance_mu) |
| $A_{\mathrm{mub}}$ | mub 分量接受率 | 1 | [`detector.acceptance_mub`](#param-detector-acceptance_mub) |
| $N_{\mathrm{Cs133}}$ | Cs133 靶核数 | nuclei | [`target.Cs133.nuclei`](#param-target-Cs133-nuclei) |
| $N_{\mathrm{I127}}$ | I127 靶核数 | nuclei | [`target.I127.nuclei`](#param-target-I127-nuclei) |

<a id="eq-15"></a>

**(15) 当前 PE 密度采样与箱积分（数值执行约定）**

$$
\begin{aligned}h_{\ell i}(x_j)&=\max\!\left\{\operatorname{Trapz}_{T}\!\left[\frac{Y_{\ell i}(T)p(x_j\mid T)}{m_{i,\mathrm{kg}}}\right],0\right\}\\N^{\mathrm{pre}}_{\ell i,b}&=m_{i,\mathrm{kg}}\operatorname{Trapz}_{x\in[x_b,x_{b+1}]}\!\left[\operatorname{Interp}(x_j,h_{\ell i};x)\epsilon(x)\right]\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $\ell$ | 本包源分量索引 | 1 | derived/constant（见定义） |
| $i$ | 本包靶核素索引 | 1 | derived/constant（见定义） |
| $b$ | 观测分箱索引 | 1 | derived/constant（见定义） |
| $j$ | PE 密度节点索引 | 1 | derived/constant（见定义） |
| $T$ | 反冲能积分变量 | keV | derived/constant（见定义） |
| $x,x_j,x_b,x_{b+1}$ | 重建坐标、密度采样点和相邻箱边界 | PE | derived/constant（见定义） |
| $Y_{\ell i}$ | 每核反冲产额，定义见前式 | events/nucleus/keV | derived/constant（见定义） |
| $p$ | Gamma 条件 PE 密度 | PE^-1 | derived/constant（见定义） |
| $m_{i,\mathrm{kg}}$ | 单核 kg 质量，见第 3 节 | kg | derived/constant（见定义） |
| $h_{\ell i}$ | 每 kg 的中间 PE 密度 | events/kg/PE | derived/constant（见定义） |
| $N^{\mathrm{pre}}_{\ell i,b}$ | 效率和箱积分后的每核产额 | events/nucleus/bin | derived/constant（见定义） |
| $\epsilon$ | PE 选择效率 | 1 | derived/constant（见定义） |
| $\operatorname{Trapz}$ | 实际所选节点上的复合梯形积分 | 1 | derived/constant（见定义） |
| $\operatorname{Interp}$ | PE 密度线性插值，采样范围外为 0 | 1 | derived/constant（见定义） |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | source; interaction; target; detector; observable |
| 输出 | nonnegative 9-bin expected signal [events/bin] |
| 定义域 | T grid: linspace(Tmin,max_i endpoint,n_er) per isotope; E grid: linspace(0,DAR_endpoint,n_enu), filter E>=Emin(T),E>0 without threshold-node insertion; PE samples: arange(first_edge,last_edge+0.5*step,step); subnodes: linspace(each edge pair,n_observed_bin) |
| 归一化 | fluence includes POT/geometry; nuclei include mass/stoichiometry; efficiency and acceptance each once; no live time, background or bin-width division in prediction |
| 边界/裁剪 | PE density interpolation outside sampled domain zero; negative density nodes clipped; endpoints shared by quadrature have measure zero; nine half-open bins and final upper edge retained by observation convention |

数值网格：连续能量在 source.integration_min/max 上取 numerics.n_enu 个线性节点；与显式 breakpoints（若有）合并、排序去重。每个反冲只保留正能量且达到公共运动学阈值的已有节点，不补插阈值节点，再做梯形积分；谱线按阈值单独加权。各核素反冲从 numerics.recoil_min_keV 到公共模块给出的支撑上界取 numerics.n_er 个含端点线性节点；上界覆盖所有分量的积分能量上界及谱线能量。

PE 密度网格从首个箱边界起，按 numerics.observed_step 递增，以最后箱边界加半步为开区间停止位置。先采样每 kg 密度并裁剪为非负，再插值到每箱 numerics.n_observed_bin 个含端点线性节点，乘效率后梯形积分，恢复单核质量因子，最后乘接受率和实际核数。中间 kg 因子抵消，不再额外乘 Mdet；插值范围外为零，窗口损失不重归一。

实际误差控制：fixed grids, no adaptive tolerance on actual legacy path; convergence not established in pilot。另有积分路径不等于当前绑定策略；这里不替换数值次序，也不据此声称收敛。

<a id="section-8"></a>

## 8. Statistics

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`statistics.sigma_alpha`](#param-statistics-sigma_alpha) | 0.125 | 1 / direct_input | 信号归一化 Gaussian pull 的宽度。 |
| [`statistics.sigma_beta`](#param-statistics-sigma_beta) | 0.35 | 1 / direct_input | 背景归一化 Gaussian pull 的宽度。 |
| [`statistics.sigma_floor`](#param-statistics-sigma_floor) | 1e-12 | counts/PE / direct_input | 对逐箱误差的下限裁剪；当前输入均大于下限。 |

### 双 pull 近似统计

模型：`gaussian_two_pull_legacy_v1`。旧 residual/excess 数组的近似 Gaussian 统计。信号从 events/bin 转 counts/PE 一次。误差对角且与参数无关，两项归一化 pull 在全箱间相关；alpha/beta 无约束解析极小化。

<a id="eq-16"></a>

**(16) 旧双 pull Gaussian 近似**

$$
\begin{aligned}s_b&=\frac{N_b}{x_{b+1}-x_b}\\\chi^2&=\sum_b\left[\frac{d_b-(1+\alpha)s_b-(1+\beta)B_b}{\sigma_b}\right]^2+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\left(\frac{\beta}{\sigma_\beta}\right)^2\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $b$ | 观测分箱索引 | 1 | derived/constant（见定义） |
| $s_b$ | 信号只除一次箱宽 | counts/PE | derived/constant（见定义） |
| $N_b$ | 预测逐箱信号 | events/bin | derived/constant（见定义） |
| $x_b,x_{b+1}$ | PE 箱边界 | PE | derived/constant（见定义） |
| $d_b$ | 旧 observed-like residual/excess | counts/PE | [`statistics_observed`](#res-statistics_observed) |
| $B_b$ | 背景数组 | counts/PE | [`statistics_background`](#res-statistics_background) |
| $\sigma_b$ | 误差取声明下限后使用 | counts/PE | [`statistics_uncertainty`](#res-statistics_uncertainty) |
| $\alpha,\beta$ | 信号与背景归一化 nuisance | 1 | derived/constant（见定义） |
| $\chi^2$ | 近似目标函数 | 1 | derived/constant（见定义） |
| $\sigma_\alpha$ | 信号 pull 宽度 | 1 | [`statistics.sigma_alpha`](#param-statistics-sigma_alpha) |
| $\sigma_\beta$ | 背景 pull 宽度 | 1 | [`statistics.sigma_beta`](#param-statistics-sigma_beta) |
| $\sigma_{\mathrm{floor}}$ | 逐箱误差下限 | counts/PE | [`statistics.sigma_floor`](#param-statistics-sigma_floor) |

<a id="eq-17"></a>

**(17) 双 pull 的解析 profiling**

$$
\begin{aligned}r_b&=d_b-s_b-B_b,\quad u_b=\max\{\sigma_b,\sigma_{\mathrm{floor}}\}\\\begin{pmatrix}\sum_b s_b^2/u_b^2+\sigma_\alpha^{-2}&\sum_b s_bB_b/u_b^2\\\sum_b s_bB_b/u_b^2&\sum_b B_b^2/u_b^2+\sigma_\beta^{-2}\end{pmatrix}\begin{pmatrix}\widehat\alpha\\\widehat\beta\end{pmatrix}&=\begin{pmatrix}\sum_b s_br_b/u_b^2\\\sum_b B_br_b/u_b^2\end{pmatrix}\\\chi^2_{\mathrm{prof}}&=\chi^2(\widehat\alpha,\widehat\beta)\end{aligned}
$$

| 符号 | 定义 | 单位 | Parameter ID / NPZ key |
| --- | --- | --- | --- |
| $b$ | 观测分箱索引 | 1 | derived/constant（见定义） |
| $d_b$ | 旧 observed-like residual/excess | counts/PE | [`statistics_observed`](#res-statistics_observed) |
| $B_b$ | 背景数组 | counts/PE | [`statistics_background`](#res-statistics_background) |
| $\sigma_b$ | 原生逐箱不确定度 | counts/PE | [`statistics_uncertainty`](#res-statistics_uncertainty) |
| $s_b$ | 逐箱信号除一次 PE 宽度后的密度 | counts/PE | derived/constant（见定义） |
| $r_b$ | 零 pull 下的残差 | counts/PE | derived/constant（见定义） |
| $u_b$ | 施加误差下限后的宽度 | counts/PE | derived/constant（见定义） |
| $\widehat\alpha,\widehat\beta$ | 无边界解析极小点 | 1 | derived/constant（见定义） |
| $\chi^2,\chi^2_{\mathrm{prof}}$ | 前式目标函数及其 profile 值 | 1 | derived/constant（见定义） |
| $\sigma_{\mathrm{floor}}$ | 逐箱误差下限 | counts/PE | [`statistics.sigma_floor`](#param-statistics-sigma_floor) |
| $\sigma_\alpha$ | 信号 Gaussian pull 宽度 | 1 | [`statistics.sigma_alpha`](#param-statistics-sigma_alpha) |
| $\sigma_\beta$ | 背景 Gaussian pull 宽度 | 1 | [`statistics.sigma_beta`](#param-statistics-sigma_beta) |

| 合同项 | 当前约定 |
| --- | --- |
| 输入 | signal prediction; [`statistics_observed`](#res-statistics_observed); [`statistics_background`](#res-statistics_background); [`statistics_uncertainty`](#res-statistics_uncertainty); [`observable_pe_edges`](#res-observable_pe_edges) |
| 输出 | profiled approximate chi2 [1] |
| 定义域 | nine bins; independent symmetric errors plus two Gaussian normalization pulls |
| 归一化 | observed/background/sigma already counts/PE; no covariance resource used; no Poisson interpretation |
| 边界/裁剪 | sigma=max(sigma,sigma_floor); solve 2x2 normal equations; singular solve returns alpha=beta=0,success=False; no clip_bounds in actual binding |

逐 bin 数据保持原生单位 counts/PE；以下每列直接读取所列 NPZ key。

| Bin | [`statistics_observed`](#res-statistics_observed) | [`statistics_background`](#res-statistics_background) | [`statistics_uncertainty`](#res-statistics_uncertainty) |
| --- | --- | --- | --- |
| 1 | 1.021 | 0.0 | 0.454695767 |
| 2 | 13.195 | 0.229 | 3.816688713 |
| 3 | 18.941 | 0.455 | 4.717813051 |
| 4 | 13.059 | 0.48 | 4.304453263 |
| 5 | 11.043 | 0.429 | 3.858024691 |
| 6 | 5.977 | 0.329 | 2.543540564 |
| 7 | 1.838 | 0.229 | 2.466380071 |
| 8 | 2.274 | 0.179 | 2.339616402 |
| 9 | -0.831 | 0.154 | 1.785714286 |

数据语义：observed 是旧 residual/excess，允许负值，不是 raw Poisson count；是否已扣除所列 BRN/NIN 背景尚未确认。信号从 events/bin 除一次 bin width，观测/背景/不确定度已是 counts/PE，不再次除宽度。

当前没有 covariance 资源；使用与参数无关的对角逐 bin Gaussian 误差。alpha 和 beta 的先验是独立、零均值 Gaussian，但每个归一化 nuisance 同时作用于所有箱，产生共同归一化变化。实际 binding 无 clip_bounds，执行无边界 2×2 正规方程；奇异时返回 alpha=beta=0、success=False。

本模型提供 profiled approximate chi2；没有在此定义官方 likelihood、指定零假设下的 test statistic、自由度或显著度/CL 映射。不能从模板补造这些科学主张。

<a id="section-9"></a>

## 9. 数值资源

| 核素 | Nuclear Structure 通道 → NPZ key |
| --- | --- |
| Cs133 | M → [`nuclear_Cs133_M`](#res-nuclear_Cs133_M); SigmaPP → [`nuclear_Cs133_SigmaPP`](#res-nuclear_Cs133_SigmaPP); SigmaP → [`nuclear_Cs133_SigmaP`](#res-nuclear_Cs133_SigmaP); PhiPP → [`nuclear_Cs133_PhiPP`](#res-nuclear_Cs133_PhiPP); PhiPT → [`nuclear_Cs133_PhiPT`](#res-nuclear_Cs133_PhiPT); Delta → [`nuclear_Cs133_Delta`](#res-nuclear_Cs133_Delta); MPhiPP → [`nuclear_Cs133_MPhiPP`](#res-nuclear_Cs133_MPhiPP) |
| I127 | M → [`nuclear_I127_M`](#res-nuclear_I127_M); SigmaPP → [`nuclear_I127_SigmaPP`](#res-nuclear_I127_SigmaPP); SigmaP → [`nuclear_I127_SigmaP`](#res-nuclear_I127_SigmaP); PhiPP → [`nuclear_I127_PhiPP`](#res-nuclear_I127_PhiPP); PhiPT → [`nuclear_I127_PhiPT`](#res-nuclear_I127_PhiPT); Delta → [`nuclear_I127_Delta`](#res-nuclear_I127_Delta); MPhiPP → [`nuclear_I127_MPhiPP`](#res-nuclear_I127_MPhiPP) |

核系数资源按左核子 p/n、右核子 p/n、升幂系数轴绑定；此处只记录资源接口，核结构计算由所选公共模块负责。原始归一化不改变，外部来源/约定待核。

| NPZ key | shape / dtype | 单位 / 含义 | 来源 ID |
| --- | --- | --- | --- |
| <a id="res-nuclear_Cs133_M"></a>`nuclear_Cs133_M` | [2, 2, 11] / float64 | 1 / Cs133 的 M 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_SigmaPP"></a>`nuclear_Cs133_SigmaPP` | [2, 2, 11] / float64 | 1 / Cs133 的 SigmaPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_SigmaP"></a>`nuclear_Cs133_SigmaP` | [2, 2, 11] / float64 | 1 / Cs133 的 SigmaP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_PhiPP"></a>`nuclear_Cs133_PhiPP` | [2, 2, 9] / float64 | 1 / Cs133 的 PhiPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_PhiPT"></a>`nuclear_Cs133_PhiPT` | [2, 2, 9] / float64 | 1 / Cs133 的 PhiPT 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_Delta"></a>`nuclear_Cs133_Delta` | [2, 2, 9] / float64 | 1 / Cs133 的 Delta 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_Cs133_MPhiPP"></a>`nuclear_Cs133_MPhiPP` | [2, 2, 10] / float64 | 1 / Cs133 的 MPhiPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_M"></a>`nuclear_I127_M` | [2, 2, 11] / float64 | 1 / I127 的 M 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_SigmaPP"></a>`nuclear_I127_SigmaPP` | [2, 2, 11] / float64 | 1 / I127 的 SigmaPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_SigmaP"></a>`nuclear_I127_SigmaP` | [2, 2, 11] / float64 | 1 / I127 的 SigmaP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_PhiPP"></a>`nuclear_I127_PhiPP` | [2, 2, 9] / float64 | 1 / I127 的 PhiPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_PhiPT"></a>`nuclear_I127_PhiPT` | [2, 2, 9] / float64 | 1 / I127 的 PhiPT 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_Delta"></a>`nuclear_I127_Delta` | [2, 2, 9] / float64 | 1 / I127 的 Delta 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-nuclear_I127_MPhiPP"></a>`nuclear_I127_MPhiPP` | [2, 2, 10] / float64 | 1 / I127 的 MPhiPP 核响应多项式系数；升幂顺序。 | response_data |
| <a id="res-source_energy_MeV"></a>`source_energy_MeV` | [200] / float64 | MeV / SNS 插值表的完整节点坐标，保留掩码外零节点。 | source |
| <a id="res-source_fluence_e"></a>`source_fluence_e` | [200] / float64 | cm^-2 MeV^-1 / 当前运行的 delayed e 插值表节点注量。 | source |
| <a id="res-source_fluence_mub"></a>`source_fluence_mub` | [200] / float64 | cm^-2 MeV^-1 / 当前运行的 delayed mub 插值表节点注量。 | source |
| <a id="res-state_rho_e"></a>`state_rho_e` | [3, 3] / complex128 | 1 / 固定纯味密度矩阵 e；mu 与 mub 共用 rho_mu，粒子标签不同。 | source |
| <a id="res-state_rho_mu"></a>`state_rho_mu` | [3, 3] / complex128 | 1 / 固定纯味密度矩阵 mu；mu 与 mub 共用 rho_mu，粒子标签不同。 | source |
| <a id="res-observable_pe_edges"></a>`observable_pe_edges` | [10] / float64 | PE / 九箱的十条精确边界。 | definition |
| <a id="res-statistics_observed"></a>`statistics_observed` | [9] / float64 | counts/PE / 旧 residual/excess 观测数组，末箱负值保留；背景扣除细节待官方证据。 | definition |
| <a id="res-statistics_background"></a>`statistics_background` | [9] / float64 | counts/PE / 旧 BRN+NIN 背景数组；实际 χ² 在信号之外加入该项。 | definition |
| <a id="res-statistics_uncertainty"></a>`statistics_uncertainty` | [9] / float64 | counts/PE / 逐箱对称 Gaussian 一标准差；不含额外协方差矩阵。 | definition |

数组保留原 dtype、精度和顺序，以 allow_pickle=False 读取；哈希、生成依赖和完整轴声明以 YAML 为准，不在正文 dump。

<a id="section-10"></a>

## 10. 来源、限制与状态

| 能力 | 已记录状态 | 人工审核 |
| --- | --- | --- |
| legacy_prediction | LEGACY_ONLY | NOT_REVIEWED |
| package_backed_prediction | PACKAGE_VERIFIED | NOT_REVIEWED |
| fast | PACKAGE_VERIFIED | NOT_REVIEWED |
| legacy_approximate_statistics | LEGACY_ONLY | NOT_REVIEWED |
| official_likelihood | BLOCKED | NOT_REVIEWED |
| general_antineutrino_EFT | BLOCKED | NOT_REVIEWED |
| scientific_release | BLOCKED | NOT_REVIEWED |

以上是输入中已有的状态，报告生成不重新执行 Runtime，也不提升能力或人工科学接受。

| 问题 ID / 状态 | 限制 | 影响范围 |
| --- | --- | --- |
| official_experiment_sources / MISSING | 缺官方论文、补充材料与 release 的独立核对；旧代码值不能称为官方原值。 | official_forward_reproduction, official_likelihood |
| eft_primary_conventions / MISSING | 算符 Lorentz/Lagrangian 定义、尺度及公共 matching 约定尚未逐项对照原始文献。 | official_EFT_operator_interpretation |
| nuclear_source_audit / MISSING | 外部核响应源、转换流程和归一化仍待核实；I 的 M_nn(0) 差异保留为未决问题。 | externally_validated_nuclear_response |
| antineutrino_kernel / MISSING | 反中微子标签保留，但当前使用同一味核；一般 EFT 的符号和 helicity 尚未独立验证。 | fully_validated_general_antineutrino_EFT |
| statistics_semantics / CONFLICT | observed 是旧 residual/excess；是否已扣除所列背景尚无原始证据，不消除负值，也不宣称官方 likelihood。 | official_likelihood, verified_background_subtraction_semantics |
| legacy_status_and_reference / CONFLICT | 历史阶段标签不能授予当前包人工批准；内部回归只支持对应技术范围。 | historical_human_approval_reconstruction |
| source_endpoint / MISSING | 源表端点、裁剪和插值不等同理想 Michel 谱的精确端点归一化。 | independent_source_endpoint_claim |
| detector_validity / MISSING | 淬灭、分辨率、效率和时间选择的原始校准及适用区间待补。 | official_detector_reproduction |
| pilot_runtime / MISSING | 历史 pilot 的独立运行缺口保留；是否已有后续技术证据须分别查看当前 capability，不自动关闭历史问题。 | standalone_two_file_runtime |

| 来源 ID | 路径 / locator | 种类 / 独立官方核实 |
| --- | --- | --- |
| definition | cevns_pyeft/experiments/coherent/csi2021_definition.py | project_code / False |
| assembly | cevns_pyeft/experiments/coherent/execution.py | project_code / False |
| source | cevns_pyeft/experiments/coherent/sns.py | project_code / False |
| source_adapter | cevns_pyeft/sources/sns.py | project_code / False |
| detector_defaults | cevns_pyeft/detectors/legacy_parameters.py | project_code / False |
| detector | cevns_pyeft/detectors/csi2021.py | project_code / False |
| differential | cevns_pyeft/rates/differential.py | project_code / False |
| targets | cevns_pyeft/targets/materials.py | project_code / False |
| recipes | cevns_pyeft/targets/recipes.py | project_code / False |
| constants | cevns_pyeft/foundation/constants.py | project_code / False |
| lecs | cevns_pyeft/theory/li2026/lec.py | project_code / False |
| operators | cevns_pyeft/theory/li2026/operators.py | project_code / False |
| matching | cevns_pyeft/theory/li2026/left_to_ci.py | project_code / False |
| particle_response | cevns_pyeft/theory/li2026/responses.py | project_code / False |
| amplitude | cevns_pyeft/theory/li2026/amplitude.py | project_code / False |
| cross_section | cevns_pyeft/theory/li2026/cross_section.py | project_code / False |
| kinematics | cevns_pyeft/theory/kinematics.py | project_code / False |
| response_reader | cevns_pyeft/nuclear/response.py | project_code / False |
| response_data | data/responses/responses_all.json | project_data / False |
| numerics | cevns_pyeft/contracts/parameters.py | project_code / False |
| prediction | cevns_pyeft/core/predict.py | project_code / False |
| recoil | cevns_pyeft/rates/recoil.py | project_code / False |
| folding | cevns_pyeft/rates/folding.py | project_code / False |
| statistics_binding | cevns_pyeft/experiments/coherent/statistics_binding.py | project_code / False |
| profiling | cevns_pyeft/statistics/profiling.py | project_code / False |
| statistics_provenance | data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml | project_document / False |
| old_spec | data/experiments/COHERENT_CsI/CsI2021/experiment.yaml | project_document / False |
| schema | workflows/_shared/schemas/experiment-input/experiment.schema.json | project_document / False |
| input_standard | workflows/_shared/INPUT_STANDARD.md | project_document / False |
| antinu_audit | docs/physics/physics-audits/antineutrino_sign_helicity_audit.md | project_document / False |
| nuclear_audit | docs/physics/nuclear-responses/nuclear_response_convention_audit.md | project_document / False |

<a id="equation-index"></a>

## Appendix A. 公式索引

| 编号 | 实验公式 | 模型 ID |
| --- | --- | --- |
| [1](#eq-1) | 每分量积分注量 | `sns_fluence_legacy_v1` |
| [2](#eq-2) | 延迟 Michel 形状 | `sns_michel_tabulation_legacy_v1` |
| [3](#eq-3) | 谱表网格、裁剪与 mask（数值物化规则） | `sns_michel_tabulation_legacy_v1` |
| [4](#eq-4) | 连续谱的线性插值（数值读取规则） | `sns_michel_tabulation_legacy_v1` |
| [5](#eq-5) | 连续积分的实际 DAR 上界（衰变运动学） | `sns_michel_tabulation_legacy_v1` |
| [6](#eq-6) | Prompt pion 衰变线 | `sns_prompt_line_v1` |
| [7](#eq-7) | 固定纯味态 | `sns_fixed_state_v1` |
| [8](#eq-8) | CsI 化学计量与两种质量单位 | `csi_target_inventory_v1` |
| [9](#eq-9) | 核数与质量归一化 | `csi_target_inventory_v1` |
| [10](#eq-10) | CsI 淬灭 | `csi_quenching_legacy_v1` |
| [11](#eq-11) | Shape-rate Gamma 响应 | `legacy_csi_gamma` |
| [12](#eq-12) | 重建 PE 上的效率 | `csi2021_logistic_legacy` |
| [13](#eq-13) | 分量选择接受率的施加 | `legacy_component_acceptance` |
| [14](#eq-14) | 实验折叠的物理关系 | `legacy_csi2021_v1` |
| [15](#eq-15) | 当前 PE 密度采样与箱积分（数值执行约定） | `legacy_csi2021_v1` |
| [16](#eq-16) | 旧双 pull Gaussian 近似 | `gaussian_two_pull_legacy_v1` |
| [17](#eq-17) | 双 pull 的解析 profiling | `gaussian_two_pull_legacy_v1` |

<a id="parameter-index"></a>

## Appendix B. 唯一参数索引

实验采用值只在对应模块表中列一次；共享模块参数通过精确 ID 回到 YAML 配置，不复制公共模块公式或 LEC 数值表。

| Parameter ID | 主文位置 / 配置入口 | 来源定位 |
| --- | --- | --- |
| <a id="param-source-baseline_m"></a>`source.baseline_m` | source | definition; CsI2021Settings.run |
| <a id="param-source-total_pot"></a>`source.total_pot` | source | definition; CsI2021Settings.run |
| <a id="param-source-yield_per_pot"></a>`source.yield_per_pot` | source | definition; CsI2021Settings.run |
| <a id="param-source-tabulation_min"></a>`source.tabulation_min` | source | definition; SNSRun.energy_tabulation |
| <a id="param-source-tabulation_max"></a>`source.tabulation_max` | source | definition; SNSRun.energy_tabulation |
| <a id="param-source-mask_min"></a>`source.mask_min` | source | definition; SNSRun.node_support |
| <a id="param-source-mask_max"></a>`source.mask_max` | source | definition; SNSRun.node_support |
| <a id="param-source-tabulation_nodes"></a>`source.tabulation_nodes` | source | definition; SNSRun.num_points |
| <a id="param-source-interpolation"></a>`source.interpolation` | source | definition; SNSRun.interpolation |
| <a id="param-source-fluence_per_species"></a>`source.fluence_per_species` | source | source; _n_time_integrated_flux_cm2 |
| <a id="param-source-prompt_energy"></a>`source.prompt_energy` | source | source; build_neutrino_empirical_flux_sns:E0 |
| <a id="param-source-integration_min"></a>`source.integration_min` | prediction | source_adapter; SNSLegacySource.for_run |
| <a id="param-source-integration_max"></a>`source.integration_max` | prediction | differential; emax_muon_dar_mev |
| <a id="param-target-detector_mass"></a>`target.detector_mass` | target | definition; CsI2021Settings.mass_kg |
| <a id="param-target-run_mass_metadata"></a>`target.run_mass_metadata` | 第 4 节共享配置 / YAML；非实验公式 | definition; CsI2021Settings.run.mass_metadata_kg |
| <a id="param-target-atomic_mass_kg"></a>`target.atomic_mass_kg` | target | recipes; LEGACY_ATOMIC_MASS_KG |
| <a id="param-target-Cs133-A"></a>`target.Cs133.A` | target | response_data; nuclei/Cs133/basic/A |
| <a id="param-target-Cs133-Z"></a>`target.Cs133.Z` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/Cs133/basic/Z |
| <a id="param-target-Cs133-N"></a>`target.Cs133.N` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/Cs133/basic/N |
| <a id="param-target-Cs133-J"></a>`target.Cs133.J` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/Cs133/basic/J |
| <a id="param-target-Cs133-T"></a>`target.Cs133.T` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/Cs133/basic/T |
| <a id="param-target-Cs133-b"></a>`target.Cs133.b` | target | response_data; nuclei/Cs133/basic/b |
| <a id="param-target-Cs133-isotopic_fraction"></a>`target.Cs133.isotopic_fraction` | 第 4 节共享配置 / YAML；非实验公式 | assembly; assemble_csi2021:single isotope per element |
| <a id="param-target-Cs133-mass_fraction"></a>`target.Cs133.mass_fraction` | target | assembly; assemble_csi2021 |
| <a id="param-target-Cs133-mass_GeV"></a>`target.Cs133.mass_GeV` | target | assembly; assemble_csi2021 |
| <a id="param-target-Cs133-mass_kg"></a>`target.Cs133.mass_kg` | target | assembly; assemble_csi2021 |
| <a id="param-target-Cs133-nuclei"></a>`target.Cs133.nuclei` | detector | assembly; assemble_csi2021 |
| <a id="param-nuclear-Cs133-exp_factor"></a>`nuclear.Cs133.exp_factor` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/Cs133/exp_factor |
| <a id="param-target-I127-A"></a>`target.I127.A` | target | response_data; nuclei/I/basic/A |
| <a id="param-target-I127-Z"></a>`target.I127.Z` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/I/basic/Z |
| <a id="param-target-I127-N"></a>`target.I127.N` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/I/basic/N |
| <a id="param-target-I127-J"></a>`target.I127.J` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/I/basic/J |
| <a id="param-target-I127-T"></a>`target.I127.T` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/I/basic/T |
| <a id="param-target-I127-b"></a>`target.I127.b` | target | response_data; nuclei/I/basic/b |
| <a id="param-target-I127-isotopic_fraction"></a>`target.I127.isotopic_fraction` | 第 4 节共享配置 / YAML；非实验公式 | assembly; assemble_csi2021:single isotope per element |
| <a id="param-target-I127-mass_fraction"></a>`target.I127.mass_fraction` | target | assembly; assemble_csi2021 |
| <a id="param-target-I127-mass_GeV"></a>`target.I127.mass_GeV` | target | assembly; assemble_csi2021 |
| <a id="param-target-I127-mass_kg"></a>`target.I127.mass_kg` | target | assembly; assemble_csi2021 |
| <a id="param-target-I127-nuclei"></a>`target.I127.nuclei` | detector | assembly; assemble_csi2021 |
| <a id="param-nuclear-I127-exp_factor"></a>`nuclear.I127.exp_factor` | 第 4 节共享配置 / YAML；非实验公式 | response_data; nuclei/I/exp_factor |
| <a id="param-interaction-include_sm"></a>`interaction.include_sm` | 第 4 节共享配置 / YAML；非实验公式 | numerics; TheoryPoint.include_sm |
| <a id="param-interaction-sin2thetaW"></a>`interaction.sin2thetaW` | 第 4 节共享配置 / YAML；非实验公式 | definition; ExperimentDefinition.reproduction_sin2thetaW |
| <a id="param-constants-G_F"></a>`constants.G_F` | 第 4 节共享配置 / YAML；非实验公式 | constants; G_F |
| <a id="param-constants-alpha_em"></a>`constants.alpha_em` | 第 4 节共享配置 / YAML；非实验公式 | constants; alpha_em |
| <a id="param-constants-m_mu"></a>`constants.m_mu` | source | constants; m_mu |
| <a id="param-constants-m_e"></a>`constants.m_e` | prediction | constants; m_e |
| <a id="param-constants-m_pi_charged"></a>`constants.m_pi_charged` | source | constants; m_pi_charged |
| <a id="param-constants-AMU_GEV"></a>`constants.AMU_GEV` | target | constants; AMU_GEV |
| <a id="param-constants-GEV_INV2_TO_CM2"></a>`constants.GEV_INV2_TO_CM2` | 第 4 节共享配置 / YAML；非实验公式 | constants; GEV_INV2_TO_CM2 |
| <a id="param-lecs-g_A"></a>`lecs.g_A` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g_A |
| <a id="param-lecs-Sigma_ud"></a>`lecs.Sigma_ud` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.Sigma_ud |
| <a id="param-lecs-B0_m_u"></a>`lecs.B0_m_u` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.B0_m_u |
| <a id="param-lecs-B0_m_d"></a>`lecs.B0_m_d` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.B0_m_d |
| <a id="param-lecs-L1"></a>`lecs.L1` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L1 |
| <a id="param-lecs-L2"></a>`lecs.L2` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L2 |
| <a id="param-lecs-L3"></a>`lecs.L3` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L3 |
| <a id="param-lecs-L4"></a>`lecs.L4` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L4 |
| <a id="param-lecs-L5"></a>`lecs.L5` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L5 |
| <a id="param-lecs-L6"></a>`lecs.L6` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L6 |
| <a id="param-lecs-L7"></a>`lecs.L7` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L7 |
| <a id="param-lecs-L8"></a>`lecs.L8` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L8 |
| <a id="param-lecs-L9"></a>`lecs.L9` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L9 |
| <a id="param-lecs-L10"></a>`lecs.L10` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L10 |
| <a id="param-lecs-L11"></a>`lecs.L11` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L11 |
| <a id="param-lecs-L12"></a>`lecs.L12` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L12 |
| <a id="param-lecs-L13"></a>`lecs.L13` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L13 |
| <a id="param-lecs-L14"></a>`lecs.L14` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.L14 |
| <a id="param-lecs-sigma_u_p"></a>`lecs.sigma_u_p` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.sigma_u_p |
| <a id="param-lecs-sigma_d_p"></a>`lecs.sigma_d_p` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.sigma_d_p |
| <a id="param-lecs-sigma_u_n"></a>`lecs.sigma_u_n` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.sigma_u_n |
| <a id="param-lecs-sigma_d_n"></a>`lecs.sigma_d_n` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.sigma_d_n |
| <a id="param-lecs-g1"></a>`lecs.g1` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g1 |
| <a id="param-lecs-g2"></a>`lecs.g2` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g2 |
| <a id="param-lecs-g3"></a>`lecs.g3` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g3 |
| <a id="param-lecs-g4"></a>`lecs.g4` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g4 |
| <a id="param-lecs-g5"></a>`lecs.g5` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g5 |
| <a id="param-lecs-g6"></a>`lecs.g6` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g6 |
| <a id="param-lecs-g7"></a>`lecs.g7` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g7 |
| <a id="param-lecs-g8"></a>`lecs.g8` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g8 |
| <a id="param-lecs-g9"></a>`lecs.g9` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.g9 |
| <a id="param-lecs-m_u"></a>`lecs.m_u` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.m_u |
| <a id="param-lecs-m_d"></a>`lecs.m_d` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.m_d |
| <a id="param-lecs-m_pi"></a>`lecs.m_pi` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.m_pi |
| <a id="param-lecs-m_N"></a>`lecs.m_N` | 第 4 节共享配置 / YAML；非实验公式 | lecs; Li2026LECs.m_N |
| <a id="param-detector-quenching_q1"></a>`detector.quenching_q1` | detector | detector_defaults; CsIResponseDefaults.quenching |
| <a id="param-detector-quenching_q2"></a>`detector.quenching_q2` | detector | detector_defaults; CsIResponseDefaults.quenching |
| <a id="param-detector-quenching_q3"></a>`detector.quenching_q3` | detector | detector_defaults; CsIResponseDefaults.quenching |
| <a id="param-detector-quenching_q4"></a>`detector.quenching_q4` | detector | detector_defaults; CsIResponseDefaults.quenching |
| <a id="param-detector-gamma_a"></a>`detector.gamma_a` | detector | detector_defaults; CsIResponseDefaults.gamma_a |
| <a id="param-detector-gamma_b"></a>`detector.gamma_b` | detector | detector_defaults; CsIResponseDefaults.gamma_b |
| <a id="param-detector-efficiency_a"></a>`detector.efficiency_a` | detector | detector_defaults; CsIResponseDefaults.efficiency:(a,b,c,d) |
| <a id="param-detector-efficiency_b"></a>`detector.efficiency_b` | detector | detector_defaults; CsIResponseDefaults.efficiency:(a,b,c,d) |
| <a id="param-detector-efficiency_c"></a>`detector.efficiency_c` | detector | detector_defaults; CsIResponseDefaults.efficiency:(a,b,c,d) |
| <a id="param-detector-efficiency_d"></a>`detector.efficiency_d` | detector | detector_defaults; CsIResponseDefaults.efficiency:(a,b,c,d) |
| <a id="param-detector-acceptance_e"></a>`detector.acceptance_e` | detector | detector_defaults; CSI_COMPONENT_ACCEPTANCE |
| <a id="param-detector-acceptance_mu"></a>`detector.acceptance_mu` | detector | detector_defaults; CSI_COMPONENT_ACCEPTANCE |
| <a id="param-detector-acceptance_mub"></a>`detector.acceptance_mub` | detector | detector_defaults; CSI_COMPONENT_ACCEPTANCE |
| <a id="param-numerics-n_er"></a>`numerics.n_er` | prediction | numerics; IntegrationSettings/n_er |
| <a id="param-numerics-n_enu"></a>`numerics.n_enu` | prediction | numerics; IntegrationSettings/n_enu |
| <a id="param-numerics-n_observed_bin"></a>`numerics.n_observed_bin` | prediction | numerics; IntegrationSettings/n_observed_bin |
| <a id="param-numerics-observed_step"></a>`numerics.observed_step` | prediction | numerics; IntegrationSettings/observed_step |
| <a id="param-numerics-recoil_min_keV"></a>`numerics.recoil_min_keV` | prediction | numerics; IntegrationSettings/recoil_min_keV |
| <a id="param-statistics-sigma_alpha"></a>`statistics.sigma_alpha` | statistics | definition; StatisticsDefinition.signal_sigma |
| <a id="param-statistics-sigma_beta"></a>`statistics.sigma_beta` | statistics | definition; StatisticsDefinition.background_sigma |
| <a id="param-statistics-sigma_floor"></a>`statistics.sigma_floor` | statistics | profiling; profile_gaussian_two_pull:sig |
