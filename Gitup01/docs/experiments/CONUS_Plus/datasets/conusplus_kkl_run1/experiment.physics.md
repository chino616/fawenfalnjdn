# CONUS+ onboarding v3（2026-11-06，来源标注与下一步准备版）

<!-- report-navigation:start -->
[精简说明](experiment.physics.summary.md) · [用户资料](EXPERIMENT_USER_INPUT.md) · [来源登记 P00](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P00_SOURCE_REGISTER.yaml) · [证据台账 P01](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P01_EVIDENCE_LEDGER.yaml) · [缺失与冲突 P02](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P02_MISSING_AND_CONFLICTS.md) · [配置草稿 P03](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P03_PHYSICS_CONTRACT.yaml) · [Benchmark 登记](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmark/BENCHMARK_REGISTER.md) · [资料目录](README.md)
<!-- report-navigation:end -->

本数据集为 `CONUS_Plus/conusplus_kkl_run1`。采用天然锗五同位素、Nuclear Response、参考 PDF 的 Flux 和非负零端点。当前处于资料与方案审阅阶段，整体为 PARTIAL。

<a id="report-toc"></a>

## 目录

- [1. 实验范围与本次补充](#section-1)
- [2. Source](#section-2)
- [3. Target 与物理常数](#section-3)
- [4. 本实验选择的共享模块](#section-4)
- [5. Detector](#section-5)
- [6. Observable 与逐箱观测数据](#section-6)
- [7. Prediction folding](#section-7)
- [8. Statistics 与 Benchmark](#section-8)
- [9. 数值资源与逐字段来源索引](#section-9)
- [10. 来源缺口与下一步准备](#section-10)
- [11. 标准参考文献](#section-11)

<a id="section-1"></a>

## 1. 实验范围与本次补充

本次已把具体出处写到参数、公式和数值表旁。高能系数核到 Mueller 原文，低能点核到用户 PDF，观测点核到指定 benchmark 图 1。用户提供的 Flux 截图对应 Kopeikin 与 Mueller 两篇文献。[[16]](REFERENCES.md#ref-16)

待补的原始来源有两项，Kopeikin 32 点对应的原文表/图，以及本地 Ge Response 表的原始核计算数据和生成链。已经向用户询问这些材料的名称、链接或脚本。计算准备中的接口核验列在第 10 节。

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-requested_claim"></a>`requested_claim` | 保留天然锗五同位素，采用 Nuclear Response 和参考 PDF Flux，对照 2501.17843v3 的式 (33)、式 (34) 与表 II | 1 | [[14]](REFERENCES.md#ref-14) D_V2_001/D_V2_002 与 D_V3_001 | 用户选择逐字记录 |
| <a id="source-target-number_fractions"></a>`target.number_fractions` | {"Ge70": 0.2057, "Ge72": 0.2745, "Ge73": 0.0775, "Ge74": 0.365, "Ge76": 0.0773} | 1 | [[1]](REFERENCES.md#ref-1) Ref. [1], PDF p. 9, natural-Ge paragraph. NIST Ge composition rows agree. | benchmark 原文相应位置已核 |
| <a id="source-nuclear_structure_module"></a>`nuclear_structure_module` | nuclear_np_polynomial_v1 | 1 | [[14]](REFERENCES.md#ref-14) D_V2_001 and D_V2_002 | 用户选择逐字记录 |
| <a id="source-source-endpoint_mode"></a>`source.endpoint_mode` | 加入 (0,0)，在零点与首个原节点之间线性插值 | 1 | [[14]](REFERENCES.md#ref-14) D_V2_003 | 用户选择逐字记录 |
| <a id="source-version-scope"></a>`version.scope` | v3 来源标注版与数据已整合至主项目，原始出处待补项和 Phase 0 准备事项随文档记录 | 1 | [[14]](REFERENCES.md#ref-14) D_V3_001 | 用户选择逐字记录 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-2"></a>

## 2. Source

入射为电子反中微子，低于 2 MeV 使用参考 PDF 的低能谱表，高于或等于 2 MeV 使用 Mueller 系数。高能谱具体采用 Mueller 四核素表。[[1]](REFERENCES.md#ref-1) PDF pp. 8–9，第 III 节 [[2]](REFERENCES.md#ref-2) 式 (12)，表 VI

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-source-flavor"></a>`source.flavor` | electron antineutrino | 1 | [[1]](REFERENCES.md#ref-1) Ref. [1], PDF p. 8, reactor-source paragraph | benchmark 原文相应位置已核 |
| <a id="source-source-initial_density"></a>`source.initial_density` | [[1, 0, 0], [0, 0, 0], [0, 0, 0]] | 1 | [[1]](REFERENCES.md#ref-1) Project representation of the electron-antineutrino state as &#124;e><e&#124; in the ordered (e,mu,tau) active-flavor basis，输入 source.flavor | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-total_flux"></a>`source.total_flux` | 15000000000000.0 | cm^-2*s^-1 | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eq. (1.17) | benchmark 原文相应位置已核 |
| <a id="source-source-energy_max"></a>`source.energy_max` | 10.0 | MeV | [[4]](REFERENCES.md#ref-4) Eqs. (1.18)-(1.19); a chosen 0-10 MeV model domain | 用户 PDF 转录已核，上游数字表待核 |
| <a id="source-source-join_energy"></a>`source.join_energy` | 2.0 | MeV | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eqs. (1.27)-(1.28) | benchmark 原文相应位置已核 |
| <a id="source-source-fission_fractions"></a>`source.fission_fractions` | {"U235": 0.56, "U238": 0.07, "Pu239": 0.31, "Pu241": 0.06} | 1 | [[4]](REFERENCES.md#ref-4) Eqs. (1.22)-(1.26), PDF p. 5 | 用户 PDF 转录已核，上游数字表待核 |
| <a id="source-source-kkl_comparison_fractions"></a>`source.kkl_comparison_fractions` | {"U235": 0.53, "U238": 0.08, "Pu239": 0.32, "Pu241": 0.07} | 1 | [[10]](REFERENCES.md#ref-10) PDF p. 6, reactor-flux paragraph, U235/U238/Pu239/Pu241 order | CONUS+ 原文运行配比已核 |
| <a id="source-source-match_factor"></a>`source.match_factor` | 0.9677534794383329 | 1 | [[15]](REFERENCES.md#ref-15) build, high(2)/low_shape[-1]，输入 source.mueller_coefficients, source.fission_fractions, source.low_nodes, source.join_energy | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-normalization_integral"></a>`source.normalization_integral` | 6.461600041891649 | MeV | [[15]](REFERENCES.md#ref-15) build, low_default + high256，输入 source.match_factor, source.low_nodes, source.low_endpoint_node, source.energy_max, source.mueller_coefficients, source.fission_fractions | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-low_endpoint_node"></a>`source.low_endpoint_node` | [0, 0] | (MeV,1) | [[14]](REFERENCES.md#ref-14) D_V2_003, energy in MeV and relative shape | 用户选择逐字记录 |
| <a id="source-source-grid_step"></a>`source.grid_step` | 0.001 | MeV | [[15]](REFERENCES.md#ref-15) build, linspace(0,10,10001) | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |

### 高能谱的全部系数

各行依次为 a0 至 a5，指数中的能量按 E/MeV 取数值。原始每 MeV 每裂变谱在本处先作为相对形状，再按探测器处总通量归一化。[[2]](REFERENCES.md#ref-2) PDF p. 13，表 VI

| 核素 | a0 | a1 | a2 | a3 | a4 | a5 | 直接出处 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U235 | 3.217 | -3.111 | 1.395 | -0.369 | 0.04445 | -0.002053 | [[2]](REFERENCES.md#ref-2) 表 VI，PDF p. 13 |
| U238 | 0.4833 | 0.1927 | -0.1283 | -0.006762 | 0.002233 | -0.0001536 | [[2]](REFERENCES.md#ref-2) 表 VI，PDF p. 13 |
| Pu239 | 6.413 | -7.432 | 3.535 | -0.882 | 0.1025 | -0.00455 | [[2]](REFERENCES.md#ref-2) 表 VI，PDF p. 13 |
| Pu241 | 3.251 | -3.204 | 1.428 | -0.3675 | 0.04254 | -0.001896 | [[2]](REFERENCES.md#ref-2) 表 VI，PDF p. 13 |

### 低能谱的全部节点

以下 32 个点直接转录自用户 PDF 表 2，PDF 第 6 页、印刷第 5 页。原表将其归于 Kopeikin。原始论文中对应的数值表或图仍待定位，当前按相对形状使用。[[4]](REFERENCES.md#ref-4) [[3]](REFERENCES.md#ref-3)

| 节点行 | 能量 / MeV | 相对谱值 | 直接出处 | 核验范围 |
| --- | --- | --- | --- | --- |
| 1 | 0.010 | 0.0774 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 2 | 0.020 | 0.301 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 3 | 0.035 | 0.848 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 4 | 0.040 | 0.354 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 5 | 0.070 | 0.989 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 6 | 0.100 | 1.81 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 7 | 0.130 | 2.74 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 8 | 0.160 | 3.85 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 9 | 0.165 | 3.26 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 10 | 0.180 | 3.74 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 11 | 0.215 | 4.66 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 12 | 0.230 | 4.08 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 13 | 0.280 | 5.03 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 14 | 0.330 | 5.97 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 15 | 0.335 | 4.30 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 16 | 0.350 | 4.08 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 17 | 0.390 | 4.42 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 18 | 0.400 | 4.04 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 19 | 0.435 | 4.39 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 20 | 0.440 | 2.84 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 21 | 0.500 | 3.03 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 22 | 0.700 | 3.14 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 23 | 0.900 | 3.23 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 24 | 1.000 | 3.11 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 25 | 1.190 | 2.24 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 26 | 1.250 | 2.06 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 27 | 1.300 | 1.77 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 28 | 1.500 | 1.59 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 29 | 1.700 | 1.48 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 30 | 1.800 | 1.42 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 31 | 1.900 | 1.36 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |
| 32 | 2.000 | 1.30 | [[4]](REFERENCES.md#ref-4) 表 2，PDF p. 6 | 转录已核，上游原表待核 |

<a id="formula-mueller-shape"></a>

**Mueller混合相对谱形**

依据与处理过程见 [[2]](REFERENCES.md#ref-2)。Mueller et al. (2011)，PDF p. 13，式 (12) 与表 VI。裂变权重来自用户笔记 PDF p. 5，式 (1.22)–(1.26)。

$$
\rho_H(E_\nu)=\sum_r f_r\exp\!\left[\sum_{n=0}^{5}a_{rn}\left(\frac{E_\nu}{\mathrm{MeV}}\right)^n\right]. \tag{1}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $E_\nu$ | 入射中微子能量 | MeV | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $a_{rn}$ | 按E/MeV约定使用的系数数值 | 1 | `source.mueller_coefficients` | [[2]](REFERENCES.md#ref-2) Eq. (12), Table VI, PDF p. 13; exponent uses numerical E/MeV |
| $f_r$ | 参考PDF的裂变份额 | 1 | `source.fission_fractions` | [[4]](REFERENCES.md#ref-4) Eqs. (1.22)-(1.26), PDF p. 5 |
| $\rho_H$ | 归一化前相对数值谱形 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

<a id="formula-source-match"></a>

**拼接与归一化；零节点是用户确认的新选择**

依据与处理过程见 [[4]](REFERENCES.md#ref-4)。用户笔记 PDF p. 5，式 (1.27)–(1.28)。零端点按用户决定 D_V2_003 加入。

$$
c_m=\frac{\rho_H(E_m)}{K(E_m)},\quad \rho(E)=\begin{cases}c_m K_0(E),&0\le E<E_m,\\ \rho_H(E),&E_m\le E\le E_{\max},\\0,&\text{otherwise},\end{cases}\qquad K_0(0)=0. \tag{2}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $E_m$ | 拼接能量 | MeV | `source.join_energy` | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eqs. (1.27)-(1.28) |
| $E_{\max}$ | 所选模型上限 | MeV | `source.energy_max` | [[4]](REFERENCES.md#ref-4) Eqs. (1.18)-(1.19); a chosen 0-10 MeV model domain |
| $c_m$ | 拼接因子 | 1 | `source.match_factor` | [[15]](REFERENCES.md#ref-15) build, high(2)/low_shape[-1]，输入 source.mueller_coefficients, source.fission_fractions, source.low_nodes, source.join_energy |
| $K_0$ | 加(0,0)后的低能相对谱线性插值 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $K$ | 用户笔记原32节点的相对谱值 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\rho$ | 归一化前相对谱形 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

<a id="formula-absolute-flux"></a>

**探测器处总通量归一化**

依据与处理过程见 [[4]](REFERENCES.md#ref-4)。用户笔记 PDF pp. 4–5，式 (1.16)–(1.20)。总通量取 benchmark PDF p. 8，第 III 节。

$$
\mathcal N=\int_0^{E_{\max}}\rho(E)\,dE,\qquad \phi(E)=\Phi_0\frac{\rho(E)}{\mathcal N},\qquad \int_0^{E_{\max}}\phi(E)\,dE=\Phi_0. \tag{3}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $\Phi_0$ | 探测器位置每秒总通量 | cm^-2*s^-1 | `source.total_flux` | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eq. (1.17) |
| $\mathcal N$ | 相对谱归一化积分 | MeV | `source.normalization_integral` | [[15]](REFERENCES.md#ref-15) build, low_default + high256，输入 source.match_factor, source.low_nodes, source.low_endpoint_node, source.energy_max, source.mueller_coefficients, source.fission_fractions |
| $\phi$ | 微分通量；对应默认CSV数值列 | cm^-2*s^-1*MeV^-1 | `source.flux_table` | [[15]](REFERENCES.md#ref-15) build, flux_bytes and piecewise normalization，输入 source.total_flux, source.normalization_integral, source.match_factor, source.low_nodes, source.mueller_coefficients, source.fission_fractions, source.low_endpoint_node, source.grid_step |
| $E_{\max}$ | 模型上限 | MeV | `source.energy_max` | [[4]](REFERENCES.md#ref-4) Eqs. (1.18)-(1.19); a chosen 0-10 MeV model domain |

参考 PDF 配比为 U235/U238/Pu239/Pu241 = 0.56/0.07/0.31/0.06。NEON 图 23 图注可交叉核对该模型配比。CONUS+ 运行期配比为 0.53/0.08/0.32/0.07。两组值均保存在数据表中。[[4]](REFERENCES.md#ref-4) 式 (1.22)–(1.25) [[9]](REFERENCES.md#ref-9) 图 23 图注 [[10]](REFERENCES.md#ref-10) PDF p. 6

Mueller 原文的参考谱主要覆盖 2–8 MeV。本版按参考 PDF 将多项式延用到 10 MeV，并记录尾部扩展。全谱归一化包含低能段，因此低能原始来源的缺口也影响全谱绝对通量的溯源范围。[[2]](REFERENCES.md#ref-2) [[4]](REFERENCES.md#ref-4) 式 (1.18)、(1.28)

由原先线性外推算得零能量处相对谱为 -0.1462，零点位于 0.006538462 MeV。加入零节点后的归一积分为 6.461600041892 MeV，对照外推为 6.460892614098 MeV，相对变化 0.010949%。这些值来自同一输入重建。[[15]](REFERENCES.md#ref-15) build

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-3"></a>

## 3. Target 与物理常数

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-target-detector_mass"></a>`target.detector_mass` | 1.0 | kg | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 10 effective detector | benchmark 原文相应位置已核 |
| <a id="source-target-exposure"></a>`target.exposure` | 119.0 | kg*d | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 10 effective exposure | benchmark 原文相应位置已核 |
| <a id="source-target-atomic_mass_u"></a>`target.atomic_mass_u` | {"Ge70": 69.92424875, "Ge72": 71.922075826, "Ge73": 72.923458956, "Ge74": 73.921177761, "Ge76": 75.921402726} | u | [[5]](REFERENCES.md#ref-5) Ge isotope rows, relative atomic mass column | NIST 原始数值行已核 |
| <a id="source-constants-atomic_mass_kg"></a>`constants.atomic_mass_kg` | 1.66053906892e-27 | kg | [[6]](REFERENCES.md#ref-6) atomic mass constant row | 2022 CODATA 数值行已核 |
| <a id="source-constants-atomic_mass_energy_MeV"></a>`constants.atomic_mass_energy_MeV` | 931.49410372 | MeV | [[6]](REFERENCES.md#ref-6) atomic mass constant energy equivalent in MeV row | 2022 CODATA 数值行已核 |
| <a id="source-constants-atomic_mass_energy_GeV"></a>`constants.atomic_mass_energy_GeV` | 0.93149410372 | GeV | [[6]](REFERENCES.md#ref-6) atomic mass constant energy equivalent in MeV, divided by 1000，输入 constants.atomic_mass_energy_MeV | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-constants-electron_mass_energy_MeV"></a>`constants.electron_mass_energy_MeV` | 0.51099895069 | MeV | [[6]](REFERENCES.md#ref-6) electron mass energy equivalent in MeV row | 2022 CODATA 数值行已核 |
| <a id="source-constants-electron_mass_energy_GeV"></a>`constants.electron_mass_energy_GeV` | 0.00051099895069 | GeV | [[6]](REFERENCES.md#ref-6) electron mass energy equivalent in MeV, divided by 1000，输入 constants.electron_mass_energy_MeV | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-constants-avogadro_per_mol"></a>`constants.avogadro_per_mol` | 6.02214076e+23 | mol^-1 | [[6]](REFERENCES.md#ref-6) Avogadro constant row, exact | 2022 CODATA 数值行已核 |

<a id="formula-natural-inventory"></a>

**天然Ge每公斤核数**

依据与处理过程见 [[5]](REFERENCES.md#ref-5)。NIST 原子质量与数丰度及 CODATA 质量常数，按数分数求每公斤核数。

$$
\overline m_{\rm atom}=\sum_i x_i m_i^{\rm atom},\qquad n_i=\frac{x_i}{\overline m_{\rm atom}},\qquad \sum_i x_i=1. \tag{4}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $x_i$ | 天然Ge核素数分数 | 1 | `target.number_fractions` | [[1]](REFERENCES.md#ref-1) Ref. [1], PDF p. 9, natural-Ge paragraph. NIST Ge composition rows agree. |
| $m_i^{\rm atom}$ | 中性原子质量，用于每公斤库存 | kg | `target.atomic_mass_kg` | [[5]](REFERENCES.md#ref-5) Ge isotope rows; multiplied by CODATA [6] atomic mass constant，输入 target.atomic_mass_u, constants.atomic_mass_kg |
| $\overline m_{\rm atom}$ | 平均中性原子质量 | kg | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $n_i$ | 每公斤材料中核素i的核数 | nuclei/kg | `target.nuclei_per_kg` | [[5]](REFERENCES.md#ref-5) Natural-isotope atom inventory; see natural_ge_inventory.csv，输入 target.number_fractions, target.atomic_mass_kg |

| 核素 | 数分数 | 原子质量 / u | 每公斤核数 | 近似核质量 / GeV | 直接依据 |
| --- | --- | --- | --- | --- | --- |
| Ge70 | 0.20570000 | 69.924248750000 | 1.705625964555e+24 | 65.117673451254 | [[5]](REFERENCES.md#ref-5) Ge 对应行 + [[6]](REFERENCES.md#ref-6) 质量常数，按本节公式推导 |
| Ge72 | 0.27450000 | 71.922075826000 | 2.276102709142e+24 | 66.978637592800 | [[5]](REFERENCES.md#ref-5) Ge 对应行 + [[6]](REFERENCES.md#ref-6) 质量常数，按本节公式推导 |
| Ge73 | 0.07750000 | 72.923458956000 | 6.426155189744e+23 | 67.911420073959 | [[5]](REFERENCES.md#ref-5) Ge 对应行 + [[6]](REFERENCES.md#ref-6) 质量常数，按本节公式推导 |
| Ge74 | 0.36500000 | 73.921177761000 | 3.026511799041e+24 | 68.840789257987 | [[5]](REFERENCES.md#ref-5) Ge 对应行 + [[6]](REFERENCES.md#ref-6) 质量常数，按本节公式推导 |
| Ge76 | 0.07730000 | 75.921402726000 | 6.409571563448e+23 | 70.703987018998 | [[5]](REFERENCES.md#ref-5) Ge 对应行 + [[6]](REFERENCES.md#ref-6) 质量常数，按本节公式推导 |

每公斤核数使用中性原子质量。运动学核质量采用原子质量能量减去 Z 个电子静质量的近似，电子结合能修正作为明确的近似项记录。[[15]](REFERENCES.md#ref-15) build 中 nuclear_mass 与 nuclei_kg

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-4"></a>

## 4. 本实验选择的共享模块

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-interaction_module"></a>`interaction_module` | li2026_sm_left_v1 | 1 | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key li2026_sm_left_v1 | 当前代码身份与引用位置已核 |
| `nuclear_structure_module` | nuclear_np_polynomial_v1 | 1 | [[14]](REFERENCES.md#ref-14) D_V2_001 and D_V2_002 | 用户选择逐字记录 |
| <a id="source-nuclear-response_resource"></a>`nuclear.response_resource` | data/responses/responses_all.json | 1 | [[7]](REFERENCES.md#ref-7) nuclei.Ge70/Ge72/Ge73/Ge74/Ge76 | 本地表与键已核，原始核计算出处待核 |
| <a id="source-nuclear-response_keys"></a>`nuclear.response_keys` | ["Ge70", "Ge72", "Ge73", "Ge74", "Ge76"] | 1 | [[7]](REFERENCES.md#ref-7) All five keys read and finite W matrices checked | 本地表与键已核，原始核计算出处待核 |
| <a id="source-kinematics_module"></a>`kinematics_module` | elastic_kinematics_v1 | 1 | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key elastic_kinematics_v1 | 当前代码身份与引用位置已核 |
| <a id="source-cross_section_module"></a>`cross_section_module` | li2026_dsigma_v1 | 1 | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key li2026_dsigma_v1 | 当前代码身份与引用位置已核 |
| <a id="source-interaction-fermi_GeV_minus2"></a>`interaction.fermi_GeV_minus2` | 1.1663787e-05 | GeV^-2 | [[6]](REFERENCES.md#ref-6) Fermi coupling constant row | 2022 CODATA 数值行已核 |
| <a id="source-interaction-sin2thetaW_reference"></a>`interaction.sin2thetaW_reference` | 0.23857 | 1 | [[1]](REFERENCES.md#ref-1) Ref. [1], Sec. II.A, PDF p. 3, low-energy reference 0.23857(5) | benchmark 原文相应位置已核 |

Ge70、Ge72、Ge73、Ge74、Ge76 的本地 Response 键均可读取。数值来源目前定位到 responses_all.json 的相应 nuclei 条目，原始核计算出处保留待核状态。共享理论选择参考 Li 等人的框架，数值表的原始来源单独记录。[[7]](REFERENCES.md#ref-7) [[8]](REFERENCES.md#ref-8)

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-5"></a>

## 5. Detector

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-detector-Z"></a>`detector.Z` | 32 | 1 | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Ge atomic number; [5] | benchmark 原文相应位置已核 |
| <a id="source-detector-k"></a>`detector.k` | 0.162 | 1 | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (31) | benchmark 原文相应位置已核 |
| <a id="source-detector-fwhm_reference"></a>`detector.fwhm_reference` | 48 | eVee | [[1]](REFERENCES.md#ref-1) PDF p. 9, paragraph following Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-detector-sigma0"></a>`detector.sigma0` | 20.38 | eVee | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eqs. (29)-(30) | benchmark 原文相应位置已核 |
| <a id="source-detector-fano"></a>`detector.fano` | 0.1096 | 1 | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-detector-pair_energy"></a>`detector.pair_energy` | 2.96 | eVee | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-detector-threshold"></a>`detector.threshold` | 160.0 | eVee | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Sec. III effective detector | benchmark 原文相应位置已核 |
| <a id="source-detector-efficiency"></a>`detector.efficiency` | unity above the selected 160 eVee threshold; no additional official trigger correction | 1 | [[1]](REFERENCES.md#ref-1) Sec. III efficiency approximation | benchmark 原文相应位置已核 |
| <a id="source-numerics-minimum_true_ionization"></a>`numerics.minimum_true_ionization` | 2.96 | eVee | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 9 | benchmark 原文相应位置已核 |

<a id="formula-lindhard"></a>

**核反冲到平均电离能**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。benchmark PDF p. 9，式 (31)，含 11.5、3、0.15、0.7、0.6 系数与指数。

$$
\epsilon=11.5Z^{-7/3}\frac{T}{\mathrm{keV}},\quad g(\epsilon)=3\epsilon^{0.15}+0.7\epsilon^{0.6}+\epsilon,\quad Q(T)=\frac{k g(\epsilon)}{1+k g(\epsilon)},\quad \overline E(T)=10^3 Q(T)\frac{T}{\mathrm{keV}}\,\mathrm{eVee}. \tag{5}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $T$ | 真实核反冲能 | keVnr | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $Z$ | Ge原子序数 | 1 | `detector.Z` | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Ge atomic number; [5] |
| $k$ | Lindhard名义参数 | 1 | `detector.k` | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (31) |
| $Q$ | 淬灭因子 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\overline E$ | 真实平均电离能 | eVee | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\epsilon$ | Lindhard无量纲能量 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

<a id="formula-gaussian"></a>

**分辨率与全域归一响应**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。benchmark PDF p. 9，式 (29)–(30)。全域归一化由 Gaussian 定义得到。

$$
\sigma^2(E)=\sigma_0^2+F\eta E,\qquad G(x\mid T)=\frac{\exp[-(x-\overline E(T))^2/(2\sigma^2(\overline E(T)))]}{\sqrt{2\pi}\,\sigma(\overline E(T))},\qquad \int_{-\infty}^{\infty}G(x\mid T)\,dx=1. \tag{6}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $x$ | 重建电离能 | eVee | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $E$ | 展宽前真实电离能 | eVee | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\sigma_0$ | 基线分辨率 | eVee | `detector.sigma0` | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eqs. (29)-(30) |
| $F$ | Fano因子 | 1 | `detector.fano` | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) |
| $\eta$ | 电子空穴对能量 | eVee | `detector.pair_energy` | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) |
| $G$ | 条件响应密度 | eVee^-1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\sigma$ | 能量分辨率标准差 | eVee | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

<a id="formula-bin-probability"></a>

**选定分箱的响应概率**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。由 benchmark 式 (26)、(29)、(32) 对观测箱积分得到。

$$
P_b(T)=\int_{E_b}^{E_{b+1}}G(x\mid T)\,dx,\qquad 0\le\sum_b P_b(T)\le1. \tag{7}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $P_b$ | 包含窗口损失的分箱概率 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $E_b$ | 完整20条重建边界 | eVee | `observable.edges_eVee` | [[11]](REFERENCES.md#ref-11) 19 plotted centres +/-5 eVee，输入 statistics.observed |
| $G$ | 全域归一Gaussian密度 | eVee^-1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $T$ | 真实反冲能 | keVnr | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

处理顺序为真实核反冲、Lindhard 电离能、Gaussian 重建能、观测能分箱。Lindhard 中反冲能取 keV，分辨率中电离能取 eVee。采用 benchmark 阈值以上约 100% 的效率近似，Gaussian 窗口外尾部计作接受损失。[[1]](REFERENCES.md#ref-1) PDF pp. 8–10，式 (26)、(29)–(32)

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-6"></a>

## 6. Observable 与逐箱观测数据

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-observable-processing"></a>`observable.processing` | background-subtracted signed excess | 1 | [[1]](REFERENCES.md#ref-1) Sec. III; Eq. (33); Fig. 1 | benchmark 原文相应位置已核 |
| <a id="source-observable-native_unit"></a>`observable.native_unit` | counts kg^-1 (10 eVee)^-1 | 1 | [[1]](REFERENCES.md#ref-1) Fig. 1 vertical axis | benchmark 原文相应位置已核 |
| <a id="source-observable-edges_eVee"></a>`observable.edges_eVee` | [160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350] | eVee | [[11]](REFERENCES.md#ref-11) 19 plotted centres +/-5 eVee，输入 statistics.observed | 原图向量取点可重建，作者原始数表待取得 |

数据由指定 PDF 第 10 页图 1 的黑点和误差棒向量提取。表内能量为 eVee，观测和误差单位均为 counts kg^-1 (10 eVee)^-1。下表保留负中心值。mean 列为上下误差算术平均，当前作为候选统计约定记录。[[1]](REFERENCES.md#ref-1) 图 1 [[11]](REFERENCES.md#ref-11) CSV、provenance JSON 与 overlay

| 箱 | 中心 / eVee | excess | 下误差 | 上误差 | 候选 mean | 数据出处 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 165.0000 | 13.2710 | 22.9283 | 23.0530 | 22.9907 | [[11]](REFERENCES.md#ref-11) 第 1 行，源图 [1] 图 1 |
| 2 | 175.0000 | 38.0685 | 15.7009 | 15.7009 | 15.7009 | [[11]](REFERENCES.md#ref-11) 第 2 行，源图 [1] 图 1 |
| 3 | 185.0000 | 29.0966 | 12.5857 | 12.7103 | 12.6480 | [[11]](REFERENCES.md#ref-11) 第 3 行，源图 [1] 图 1 |
| 4 | 195.0000 | 21.3707 | 12.2118 | 12.2118 | 12.2118 | [[11]](REFERENCES.md#ref-11) 第 4 行，源图 [1] 图 1 |
| 5 | 205.0000 | 12.2741 | 11.5888 | 11.4642 | 11.5265 | [[11]](REFERENCES.md#ref-11) 第 5 行，源图 [1] 图 1 |
| 6 | 215.0000 | 4.9221 | 11.5888 | 11.5888 | 11.5888 | [[11]](REFERENCES.md#ref-11) 第 6 行，源图 [1] 图 1 |
| 7 | 225.0000 | 4.2991 | 11.2150 | 11.3396 | 11.2773 | [[11]](REFERENCES.md#ref-11) 第 7 行，源图 [1] 图 1 |
| 8 | 235.0000 | 0.0623 | 10.8411 | 10.7165 | 10.7788 | [[11]](REFERENCES.md#ref-11) 第 8 行，源图 [1] 图 1 |
| 9 | 245.0000 | 9.1589 | 11.0903 | 10.9657 | 11.0280 | [[11]](REFERENCES.md#ref-11) 第 9 行，源图 [1] 图 1 |
| 10 | 255.0000 | 2.4299 | 10.3427 | 10.2181 | 10.2804 | [[11]](REFERENCES.md#ref-11) 第 10 行，源图 [1] 图 1 |
| 11 | 265.0000 | 3.9252 | 10.4673 | 10.2181 | 10.3427 | [[11]](REFERENCES.md#ref-11) 第 11 行，源图 [1] 图 1 |
| 12 | 275.0000 | -2.5545 | 10.8411 | 10.7165 | 10.7788 | [[11]](REFERENCES.md#ref-11) 第 12 行，源图 [1] 图 1 |
| 13 | 285.0000 | 0.5607 | 10.4673 | 10.2181 | 10.3427 | [[11]](REFERENCES.md#ref-11) 第 13 行，源图 [1] 图 1 |
| 14 | 295.0000 | -10.5296 | 10.3427 | 9.9688 | 10.1558 | [[11]](REFERENCES.md#ref-11) 第 14 行，源图 [1] 图 1 |
| 15 | 305.0000 | -4.2991 | 10.2181 | 9.9688 | 10.0935 | [[11]](REFERENCES.md#ref-11) 第 15 行，源图 [1] 图 1 |
| 16 | 315.0000 | -8.7850 | 10.2181 | 9.5950 | 9.9065 | [[11]](REFERENCES.md#ref-11) 第 16 行，源图 [1] 图 1 |
| 17 | 325.0000 | -0.5607 | 9.9688 | 9.7196 | 9.8442 | [[11]](REFERENCES.md#ref-11) 第 17 行，源图 [1] 图 1 |
| 18 | 335.0000 | -0.9346 | 9.8442 | 9.7196 | 9.7819 | [[11]](REFERENCES.md#ref-11) 第 18 行，源图 [1] 图 1 |
| 19 | 345.0000 | 13.5202 | 9.7196 | 9.4704 | 9.5950 | [[11]](REFERENCES.md#ref-11) 第 19 行，源图 [1] 图 1 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-7"></a>

## 7. Prediction folding

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-numerics-seconds_per_day"></a>`numerics.seconds_per_day` | 86400.0 | s/d | [[13]](REFERENCES.md#ref-13) Chapter 4, Table 8, day row. PDF p. 142 / printed p. 140 | BIPM 单位定义已核 |
| <a id="source-numerics-plan"></a>`numerics.plan` | 按低能节点、2 MeV 拼接点和运动学边界分段积分，将 Gaussian 积入各观测箱，并在使用前核对收敛与窗口损失 | 1 | [[1]](REFERENCES.md#ref-1) 由式 (26)–(32)、源谱节点和观测箱边界推导的候选积分方案，输入 source.flux_table, observable.edges_eVee, target.nuclei_per_kg | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |

<a id="formula-fold"></a>

**天然Ge实验侧积分与曝光**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。由 benchmark PDF pp. 8–9，式 (26)、(32) 改写为对核反冲能积分。每天秒数见 BIPM 表 8。

$$
N_b=\mathcal E\,c_d\sum_i n_i\int dT\,P_b(T)\int dE_\nu\,\phi(E_\nu)\left[\frac{d\sigma_i}{dT}\right]_{\rm shared}. \tag{8}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $N_b$ | 逐箱预测事件数 | events/bin | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\mathcal E$ | 有效曝光 | kg*d | `target.exposure` | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 10 effective exposure |
| $c_d$ | 每天秒数 | s/d | `numerics.seconds_per_day` | [[13]](REFERENCES.md#ref-13) Chapter 4, Table 8, day row. PDF p. 142 / printed p. 140 |
| $n_i$ | 每公斤核数 | nuclei/kg | `target.nuclei_per_kg` | [[5]](REFERENCES.md#ref-5) Natural-isotope atom inventory; see natural_ge_inventory.csv，输入 target.number_fractions, target.atomic_mass_kg |
| $P_b$ | 分箱概率 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\phi$ | 探测器处微分通量 | cm^-2*s^-1*MeV^-1 | `source.flux_table` | [[15]](REFERENCES.md#ref-15) build, flux_bytes and piecewise normalization，输入 source.total_flux, source.normalization_integral, source.match_factor, source.low_nodes, source.mueller_coefficients, source.fission_fractions, source.low_endpoint_node, source.grid_step |
| $d\sigma_i/dT$ | 公共Response截面输出 | cm^2/keVnr | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $T$ | 积分核反冲能 | keVnr | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $E_\nu$ | 积分中微子能量 | MeV | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

按核素分别积分后按每公斤核数相加，曝光和秒/天换算各施加一次。反冲积分取 keVnr，源能积分取 MeV，所需截面输出为 cm²/keVnr。预测向图轴单位的转换、反中微子接口及积分收敛列入下一步实现审阅。[[1]](REFERENCES.md#ref-1) 式 (26)、(32) [[13]](REFERENCES.md#ref-13) 表 8

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-8"></a>

## 8. Statistics 与 Benchmark

| 参数/精确字段 | 采用值 | 单位 | 直接出处及定位/推导输入 | 核验范围 |
| --- | --- | --- | --- | --- |
| <a id="source-statistics-model_id"></a>`statistics.model_id` | gaussian_one_pull_legacy_v1 | 1 | [[12]](REFERENCES.md#ref-12) package_profiles.py::definition_from_generic/evaluate_statistics and profiling.py::profile_gaussian_one_pull | 当前代码身份与引用位置已核 |
| <a id="source-statistics-sigma_alpha"></a>`statistics.sigma_alpha` | 0.169 | 1 | [[1]](REFERENCES.md#ref-1) Eq. (33), PDF p. 10; cumulative systematic prior, no duplicated component pulls | benchmark 原文相应位置已核 |
| <a id="source-statistics-inference"></a>`statistics.inference` | 一维 1σ 对照采用 Δχ²=1，每次扫描一个 NSI，其余 NSI 固定零，并保留不连通区间。拟合前审阅本约定 | 1 | [[1]](REFERENCES.md#ref-1) [1] 式 (34) 与表 II 的 1σ 标记，以及本版候选单参数比较约定，输入 benchmark.targets | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |

<a id="formula-chi2"></a>

**19-bin单pull统计**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。benchmark PDF pp. 9–10，式 (33)。

$$
\chi^2(\boldsymbol\beta,\alpha)=\sum_{b=1}^{19}\frac{[d_b-(1+\alpha)t_b(\boldsymbol\beta)]^2}{s_b^2}+\left(\frac{\alpha}{s_\alpha}\right)^2. \tag{9}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $d_b$ | 有符号excess观测 | counts/kg/(10eVee) | `statistics.observed` | [[11]](REFERENCES.md#ref-11) Digitized Fig. 1 CSV; signed values preserved |
| $s_b$ | 候选对称误差 | counts/kg/(10eVee) | `statistics.sigma_mean` | [[11]](REFERENCES.md#ref-11) Arithmetic mean of plotted upper/lower lengths; explicit candidate statistical convention，输入 statistics.error_minus, statistics.error_plus |
| $t_b$ | 已转换到同一图轴单位的预测 | counts/kg/(10eVee) | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $s_\alpha$ | 累计归一化先验宽度 | 1 | `statistics.sigma_alpha` | [[1]](REFERENCES.md#ref-1) Eq. (33), PDF p. 10; cumulative systematic prior, no duplicated component pulls |
| $\alpha$ | 共同归一化nuisance | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $\boldsymbol\beta$ | 本次扫描的弱角或向量NSI参数 | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |

<a id="formula-profile"></a>

**解析profile**

依据与处理过程见 [[1]](REFERENCES.md#ref-1)。对 benchmark 式 (33) 的共同归一化参数求导并令导数为零得到。

$$
\widehat\alpha=\frac{\sum_b t_b(d_b-t_b)/s_b^2}{\sum_b t_b^2/s_b^2+s_\alpha^{-2}},\qquad \chi^2_{\rm prof}(\boldsymbol\beta)=\chi^2(\boldsymbol\beta,\widehat\alpha). \tag{10}
$$

| 符号 | 定义 | 单位 | 精确参数位置 | 依据与来源定位 |
| --- | --- | --- | --- | --- |
| $\widehat\alpha$ | 给定物理参数时的解析最优pull | 1 | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $d_b$ | 观测向量 | counts/kg/(10eVee) | `statistics.observed` | [[11]](REFERENCES.md#ref-11) Digitized Fig. 1 CSV; signed values preserved |
| $t_b$ | 同单位预测向量 | counts/kg/(10eVee) | 本式变量/推导量 | 本式定义的变量或中间量，依据见本式说明 |
| $s_b$ | 候选对称误差向量 | counts/kg/(10eVee) | `statistics.sigma_mean` | [[11]](REFERENCES.md#ref-11) Arithmetic mean of plotted upper/lower lengths; explicit candidate statistical convention，输入 statistics.error_minus, statistics.error_plus |
| $s_\alpha$ | 累计pull宽度 | 1 | `statistics.sigma_alpha` | [[1]](REFERENCES.md#ref-1) Eq. (33), PDF p. 10; cumulative systematic prior, no duplicated component pulls |

累计归一化宽度取 0.169。误差列直接保留图形提取的上下端点，拟合前需要确认候选对称化约定。该项具体问题已经列入 P02。[[1]](REFERENCES.md#ref-1) PDF p. 10，式 (33) 后的段落 [[11]](REFERENCES.md#ref-11)

弱混合角文献目标为 0.247 ± 0.052，来源为式 (34)。向量 NSI 的 1σ 比较目标取表 II 的 CONUS+ 列。[[1]](REFERENCES.md#ref-1) PDF pp. 11、13

| 参数 | 文献区间 | 出处 |
| --- | --- | --- |
| eps_uV_ee | [[-0.037, 0.026], [0.348, 0.411]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |
| eps_dV_ee | [[-0.034, 0.024], [0.322, 0.38]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |
| eps_uV_emu | [[-0.123, 0.123]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |
| eps_dV_emu | [[-0.114, 0.114]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |
| eps_uV_etau | [[-0.123, 0.123]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |
| eps_dV_etau | [[-0.114, 0.114]] | [[1]](REFERENCES.md#ref-1) 表 II，PDF p. 13，CONUS+ 列 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-9"></a>

## 9. 数值资源与逐字段来源索引

各物理输入的文件、列、行范围、单位和处理链集中在配套来源映射中。[来源映射](../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json)

| 字段 | 证据性质 | 具体出处/推导链 | 核验范围 |
| --- | --- | --- | --- |
| <a id="source-document-version"></a>`document.version` | PROJECT_DERIVED | [[14]](REFERENCES.md#ref-14) Current rewrite and main-project integration request | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-experiment_name"></a>`experiment_name` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III | benchmark 原文相应位置已核 |
| <a id="source-experiment_slug"></a>`experiment_slug` | PROJECT_DERIVED | [[14]](REFERENCES.md#ref-14) Project namespace chosen for the requested main-project CONUS+ integration | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-requested_claim-index"></a>`requested_claim` | USER_CONFIRMED | [[14]](REFERENCES.md#ref-14) D_V2_001/D_V2_002 与 D_V3_001 | 用户选择逐字记录 |
| <a id="source-observable-edges_eVee-index"></a>`observable.edges_eVee` | PROJECT_DERIVED | [[11]](REFERENCES.md#ref-11) 19 plotted centres +/-5 eVee，输入 statistics.observed | 原图向量取点可重建，作者原始数表待取得 |
| <a id="source-observable-processing-index"></a>`observable.processing` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III; Eq. (33); Fig. 1 | benchmark 原文相应位置已核 |
| <a id="source-observable-native_unit-index"></a>`observable.native_unit` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Fig. 1 vertical axis | benchmark 原文相应位置已核 |
| <a id="source-source-flavor-index"></a>`source.flavor` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Ref. [1], PDF p. 8, reactor-source paragraph | benchmark 原文相应位置已核 |
| <a id="source-source-total_flux-index"></a>`source.total_flux` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eq. (1.17) | benchmark 原文相应位置已核 |
| <a id="source-source-energy_max-index"></a>`source.energy_max` | SOURCE_EXTRACTED | [[4]](REFERENCES.md#ref-4) Eqs. (1.18)-(1.19); a chosen 0-10 MeV model domain | 用户 PDF 转录已核，上游数字表待核 |
| <a id="source-source-join_energy-index"></a>`source.join_energy` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III; [4] Eqs. (1.27)-(1.28) | benchmark 原文相应位置已核 |
| <a id="source-source-mueller_coefficients"></a>`source.mueller_coefficients` | SOURCE_EXTRACTED | [[2]](REFERENCES.md#ref-2) Eq. (12), Table VI, PDF p. 13; exponent uses numerical E/MeV | Mueller 原文 24 个系数已核 |
| <a id="source-source-low_nodes"></a>`source.low_nodes` | SOURCE_EXTRACTED | [[4]](REFERENCES.md#ref-4) Table 2, PDF p. 6 (printed p. 5) | 用户 PDF 转录已核，上游数字表待核 |
| <a id="source-source-fission_fractions-index"></a>`source.fission_fractions` | SOURCE_EXTRACTED | [[4]](REFERENCES.md#ref-4) Eqs. (1.22)-(1.26), PDF p. 5 | 用户 PDF 转录已核，上游数字表待核 |
| <a id="source-source-endpoint_mode-index"></a>`source.endpoint_mode` | USER_CONFIRMED | [[14]](REFERENCES.md#ref-14) D_V2_003 | 用户选择逐字记录 |
| <a id="source-source-match_factor-index"></a>`source.match_factor` | PROJECT_DERIVED | [[15]](REFERENCES.md#ref-15) build, high(2)/low_shape[-1]，输入 source.mueller_coefficients, source.fission_fractions, source.low_nodes, source.join_energy | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-normalization_integral-index"></a>`source.normalization_integral` | PROJECT_DERIVED | [[15]](REFERENCES.md#ref-15) build, low_default + high256，输入 source.match_factor, source.low_nodes, source.low_endpoint_node, source.energy_max, source.mueller_coefficients, source.fission_fractions | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-flux_table"></a>`source.flux_table` | PROJECT_DERIVED | [[15]](REFERENCES.md#ref-15) build, flux_bytes and piecewise normalization，输入 source.total_flux, source.normalization_integral, source.match_factor, source.low_nodes, source.mueller_coefficients, source.fission_fractions, source.low_endpoint_node, source.grid_step | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-formula_vs_grid"></a>`source.formula_vs_grid` | PROJECT_DERIVED | [[15]](REFERENCES.md#ref-15) build，分段处方与 CSV 采样 | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-target-number_fractions-index"></a>`target.number_fractions` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Ref. [1], PDF p. 9, natural-Ge paragraph. NIST Ge composition rows agree. | benchmark 原文相应位置已核 |
| <a id="source-target-atomic_mass_kg"></a>`target.atomic_mass_kg` | PROJECT_DERIVED | [[5]](REFERENCES.md#ref-5) Ge isotope rows; multiplied by CODATA [6] atomic mass constant，输入 target.atomic_mass_u, constants.atomic_mass_kg | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-target-nuclei_per_kg"></a>`target.nuclei_per_kg` | PROJECT_DERIVED | [[5]](REFERENCES.md#ref-5) Natural-isotope atom inventory; see natural_ge_inventory.csv，输入 target.number_fractions, target.atomic_mass_kg | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-target-nuclear_mass_GeV"></a>`target.nuclear_mass_GeV` | PROJECT_DERIVED | [[5]](REFERENCES.md#ref-5) Atomic mass times u energy minus Z electron rest energy [6]，输入 target.atomic_mass_u, constants.atomic_mass_energy_GeV, constants.electron_mass_energy_GeV, detector.Z | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-target-detector_mass-index"></a>`target.detector_mass` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 10 effective detector | benchmark 原文相应位置已核 |
| <a id="source-target-exposure-index"></a>`target.exposure` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 10 effective exposure | benchmark 原文相应位置已核 |
| <a id="source-interaction_module-index"></a>`interaction_module` | REFERENCE_ONLY | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key li2026_sm_left_v1 | 当前代码身份与引用位置已核 |
| <a id="source-nuclear_structure_module-index"></a>`nuclear_structure_module` | USER_CONFIRMED | [[14]](REFERENCES.md#ref-14) D_V2_001 and D_V2_002 | 用户选择逐字记录 |
| <a id="source-nuclear-response_resource-index"></a>`nuclear.response_resource` | SOURCE_EXTRACTED | [[7]](REFERENCES.md#ref-7) nuclei.Ge70/Ge72/Ge73/Ge74/Ge76 | 本地表与键已核，原始核计算出处待核 |
| <a id="source-nuclear-response_keys-index"></a>`nuclear.response_keys` | SOURCE_EXTRACTED | [[7]](REFERENCES.md#ref-7) All five keys read and finite W matrices checked | 本地表与键已核，原始核计算出处待核 |
| <a id="source-interaction-fermi_GeV_minus2-index"></a>`interaction.fermi_GeV_minus2` | SOURCE_EXTRACTED | [[6]](REFERENCES.md#ref-6) Fermi coupling constant row | 2022 CODATA 数值行已核 |
| <a id="source-interaction-sin2thetaW_reference-index"></a>`interaction.sin2thetaW_reference` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Ref. [1], Sec. II.A, PDF p. 3, low-energy reference 0.23857(5) | benchmark 原文相应位置已核 |
| <a id="source-kinematics_module-index"></a>`kinematics_module` | REFERENCE_ONLY | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key elastic_kinematics_v1 | 当前代码身份与引用位置已核 |
| <a id="source-cross_section_module-index"></a>`cross_section_module` | REFERENCE_ONLY | [[12]](REFERENCES.md#ref-12) model_bindings.json exact key li2026_dsigma_v1 | 当前代码身份与引用位置已核 |
| <a id="source-detector-Z-index"></a>`detector.Z` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Ge atomic number; [5] | benchmark 原文相应位置已核 |
| <a id="source-detector-k-index"></a>`detector.k` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (31) | benchmark 原文相应位置已核 |
| <a id="source-detector-sigma0-index"></a>`detector.sigma0` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eqs. (29)-(30) | benchmark 原文相应位置已核 |
| <a id="source-detector-fano-index"></a>`detector.fano` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-detector-pair_energy-index"></a>`detector.pair_energy` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-detector-threshold-index"></a>`detector.threshold` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF pp. 9-10; Sec. III effective detector | benchmark 原文相应位置已核 |
| <a id="source-detector-efficiency-index"></a>`detector.efficiency` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III efficiency approximation | benchmark 原文相应位置已核 |
| <a id="source-numerics-seconds_per_day-index"></a>`numerics.seconds_per_day` | SOURCE_EXTRACTED | [[13]](REFERENCES.md#ref-13) Chapter 4, Table 8, day row. PDF p. 142 / printed p. 140 | BIPM 单位定义已核 |
| <a id="source-numerics-minimum_true_ionization-index"></a>`numerics.minimum_true_ionization` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Sec. III, PDF p. 9 | benchmark 原文相应位置已核 |
| <a id="source-numerics-plan-index"></a>`numerics.plan` | PROJECT_DERIVED | [[1]](REFERENCES.md#ref-1) 由式 (26)–(32)、源谱节点和观测箱边界推导的候选积分方案，输入 source.flux_table, observable.edges_eVee, target.nuclei_per_kg | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-fast-requested"></a>`fast.requested` | PROJECT_DERIVED | [[14]](REFERENCES.md#ref-14) D_V3_001, current requested deliverable | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-statistics-model_id-index"></a>`statistics.model_id` | REFERENCE_ONLY | [[12]](REFERENCES.md#ref-12) package_profiles.py::definition_from_generic/evaluate_statistics and profiling.py::profile_gaussian_one_pull | 当前代码身份与引用位置已核 |
| <a id="source-statistics-observed"></a>`statistics.observed` | PROJECT_DERIVED | [[11]](REFERENCES.md#ref-11) Digitized Fig. 1 CSV; signed values preserved | 原图向量取点可重建，作者原始数表待取得 |
| <a id="source-statistics-error_minus"></a>`statistics.error_minus` | PROJECT_DERIVED | [[11]](REFERENCES.md#ref-11) CSV lower error lengths | 原图向量取点可重建，作者原始数表待取得 |
| <a id="source-statistics-error_plus"></a>`statistics.error_plus` | PROJECT_DERIVED | [[11]](REFERENCES.md#ref-11) CSV upper error lengths | 原图向量取点可重建，作者原始数表待取得 |
| <a id="source-statistics-sigma_mean"></a>`statistics.sigma_mean` | PROJECT_DERIVED | [[11]](REFERENCES.md#ref-11) Arithmetic mean of plotted upper/lower lengths; explicit candidate statistical convention，输入 statistics.error_minus, statistics.error_plus | 原图向量取点可重建，作者原始数表待取得 |
| <a id="source-statistics-sigma_alpha-index"></a>`statistics.sigma_alpha` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Eq. (33), PDF p. 10; cumulative systematic prior, no duplicated component pulls | benchmark 原文相应位置已核 |
| <a id="source-statistics-inference-index"></a>`statistics.inference` | PROJECT_DERIVED | [[1]](REFERENCES.md#ref-1) [1] 式 (34) 与表 II 的 1σ 标记，以及本版候选单参数比较约定，输入 benchmark.targets | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-benchmark-targets"></a>`benchmark.targets` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) Ref. [1], Eq. (34), PDF p. 11, and Table II CONUS+ column, PDF p. 13 | benchmark 原文相应位置已核 |
| <a id="source-provenance-open_items"></a>`provenance.open_items` | PROJECT_DERIVED | [[7]](REFERENCES.md#ref-7) Current P02 source gaps and implementation backlog | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-version-scope-index"></a>`version.scope` | USER_CONFIRMED | [[14]](REFERENCES.md#ref-14) D_V3_001 | 用户选择逐字记录 |
| <a id="source-target-atomic_mass_u-index"></a>`target.atomic_mass_u` | SOURCE_EXTRACTED | [[5]](REFERENCES.md#ref-5) Ge isotope rows, relative atomic mass column | NIST 原始数值行已核 |
| <a id="source-constants-atomic_mass_kg-index"></a>`constants.atomic_mass_kg` | SOURCE_EXTRACTED | [[6]](REFERENCES.md#ref-6) atomic mass constant row | 2022 CODATA 数值行已核 |
| <a id="source-constants-atomic_mass_energy_GeV-index"></a>`constants.atomic_mass_energy_GeV` | PROJECT_DERIVED | [[6]](REFERENCES.md#ref-6) atomic mass constant energy equivalent in MeV, divided by 1000，输入 constants.atomic_mass_energy_MeV | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-constants-electron_mass_energy_GeV-index"></a>`constants.electron_mass_energy_GeV` | PROJECT_DERIVED | [[6]](REFERENCES.md#ref-6) electron mass energy equivalent in MeV, divided by 1000，输入 constants.electron_mass_energy_MeV | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-constants-avogadro_per_mol-index"></a>`constants.avogadro_per_mol` | SOURCE_EXTRACTED | [[6]](REFERENCES.md#ref-6) Avogadro constant row, exact | 2022 CODATA 数值行已核 |
| <a id="source-constants-atomic_mass_energy_MeV-index"></a>`constants.atomic_mass_energy_MeV` | SOURCE_EXTRACTED | [[6]](REFERENCES.md#ref-6) atomic mass constant energy equivalent in MeV row | 2022 CODATA 数值行已核 |
| <a id="source-constants-electron_mass_energy_MeV-index"></a>`constants.electron_mass_energy_MeV` | SOURCE_EXTRACTED | [[6]](REFERENCES.md#ref-6) electron mass energy equivalent in MeV row | 2022 CODATA 数值行已核 |
| <a id="source-source-kkl_comparison_fractions-index"></a>`source.kkl_comparison_fractions` | SOURCE_EXTRACTED | [[10]](REFERENCES.md#ref-10) PDF p. 6, reactor-flux paragraph, U235/U238/Pu239/Pu241 order | CONUS+ 原文运行配比已核 |
| <a id="source-source-grid_step-index"></a>`source.grid_step` | PROJECT_DERIVED | [[15]](REFERENCES.md#ref-15) build, linspace(0,10,10001) | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-source-low_endpoint_node-index"></a>`source.low_endpoint_node` | USER_CONFIRMED | [[14]](REFERENCES.md#ref-14) D_V2_003, energy in MeV and relative shape | 用户选择逐字记录 |
| <a id="source-source-initial_density-index"></a>`source.initial_density` | PROJECT_DERIVED | [[1]](REFERENCES.md#ref-1) Project representation of the electron-antineutrino state as &#124;e><e&#124; in the ordered (e,mu,tau) active-flavor basis，输入 source.flavor | 项目推导或拟采用方案，输入核验范围沿依赖链查阅 |
| <a id="source-detector-fwhm_reference-index"></a>`detector.fwhm_reference` | SOURCE_EXTRACTED | [[1]](REFERENCES.md#ref-1) PDF p. 9, paragraph following Eq. (30) | benchmark 原文相应位置已核 |
| <a id="source-source-reference_identification"></a>`source.reference_identification` | SOURCE_EXTRACTED | [[16]](REFERENCES.md#ref-16) User figure, bibliography bullets | 截图书目对应已核 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-10"></a>

## 10. 来源缺口与下一步准备

现有数据已可重建 Flux 和天然锗库存。进入 Phase 0 时可以据本文件审阅路线、输入与实现范围。进入依赖这些输入的可信计算前，需要处理下列事项。

| 事项 | 已有依据 | 仍需补充/核验 | 影响与下一步 |
| --- | --- | --- | --- |
| 低能 32 点原始出处 | 用户 PDF 表 2 和本轮 Flux 文献图 | Kopeikin 原文图/表或作者数值文件 | 全谱归一化的原始来源限制，继续向上游核对 |
| Ge Response 数值链 | 本地 JSON、五个 Ge key、读取器与指纹 | 原始核计算论文/数据包/生成脚本及归一化转换 | Response 可信预测前处理 |
| 统计误差约定 | 原图上下误差及算术平均候选列 | 拟合前确认对称化办法，或取得作者数表 | 进入统计实现时确认 |
| 实现核验 | 源谱、靶核数、响应公式与单位已有 | 反中微子接口、Response 归一化、预测单位映射和积分收敛 | Phase 0 中分配实现与验证步骤 |

用户在补充交互中提供了 Flux 参考截图，已据此确认两篇文献的书目对应。32 点的原文数值定位和 Response 原始数据链继续保留待补。[[16]](REFERENCES.md#ref-16)

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-11"></a>

## 11. 标准参考文献

[1] V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D **111**, 075025 (2025). [[1]](REFERENCES.md#ref-1) 来源记录及阅读入口

[2] Th. A. Mueller et al., "Improved predictions of reactor antineutrino spectra," Phys. Rev. C **83**, 054615 (2011). [[2]](REFERENCES.md#ref-2) 来源记录及阅读入口

[3] V. I. Kopeikin, "Flux and spectrum of reactor antineutrinos," Phys. At. Nucl. **75**, 143-152 (2012). [[3]](REFERENCES.md#ref-3) 来源记录及阅读入口

[4] 作者未署名，"CEνNS-pyEFT 逐文件物理编程笔记：从 LEFT Wilson 系数到 COHERENT 分箱事件数"，第1章 "CONUS+ 的 73Ge 现象学分析"，未发表项目笔记（2026），用户提供，访问日期2026-11-06。 [[4]](REFERENCES.md#ref-4) 来源记录及阅读入口

[5] NIST Physical Measurement Laboratory, "Atomic weights and isotopic compositions for germanium," online data table, accessed 2026-11-06. [[5]](REFERENCES.md#ref-5) 来源记录及阅读入口

[6] NIST Physical Measurement Laboratory, "Fundamental physical constants: 2022 CODATA adjustment, complete listing," online data table, accessed 2026-11-06. [[6]](REFERENCES.md#ref-6) 来源记录及阅读入口

[7] CEvNS-pyEFT project, "responses_all.json: shared nuclear response tables," local numerical/software asset, format Mu2eNRET_ResponseW_v1, snapshot accessed 2026-11-06. 原始核计算表的逐项来源对应尚未闭合。 [[7]](REFERENCES.md#ref-7) 来源记录及阅读入口

[8] G. Li, C.-Q. Song, F.-J. Tang, and J.-H. Yu, "Comprehensive effective field theory framework for coherent elastic neutrino-nucleus scattering," arXiv:2601.19883v2 (2026). [[8]](REFERENCES.md#ref-8) 来源记录及阅读入口

[9] J. J. Choi et al. (NEON Collaboration), "Exploring coherent elastic neutrino-nucleus scattering using reactor electron antineutrinos in the NEON experiment," Eur. Phys. J. C **83**, 226 (2023). [[9]](REFERENCES.md#ref-9) 来源记录及阅读入口

[10] N. Ackermann et al. (CONUS Collaboration), "Direct observation of coherent elastic antineutrino-nucleus scattering," Nature **643**, 1229-1233 (2025). [[10]](REFERENCES.md#ref-10) 来源记录及阅读入口

[11] CEvNS-pyEFT project, CONUS+ Fig. 1 vector-digitized data and provenance, release 2026-11-06, derived numerical asset from Ref. [1]. [[11]](REFERENCES.md#ref-11) 来源记录及阅读入口

[12] CEvNS-pyEFT project, Model bindings, package statistics dispatch and nuclear response reader, local software snapshot, 2026-11-06. [[12]](REFERENCES.md#ref-12) 来源记录及阅读入口

[13] Bureau international des poids et mesures, The International System of Units (SI), 9th ed. (2019), version 4.01 (June 2026), DOI 10.59161/AUEZ1291. [[13]](REFERENCES.md#ref-13) 来源记录及阅读入口

[14] User and CEvNS-pyEFT project, CONUS+ configuration decisions recorded in the onboarding conversation, 2026-11-06, local project record. [[14]](REFERENCES.md#ref-14) 来源记录及阅读入口

[15] CEvNS-pyEFT project, CONUS+ source and natural-Ge input generation, build_inputs.py, version v3_20261106_provenance (2026), local reproducible calculation. [[15]](REFERENCES.md#ref-15) 来源记录及阅读入口

[16] User-provided Flux reference figure identifying Kopeikin (2012) and Mueller et al. (2011), received 2026-11-06, unpublished reference image. [[16]](REFERENCES.md#ref-16) 来源记录及阅读入口

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->
