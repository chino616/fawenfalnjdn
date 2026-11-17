# PandaX4T_2024_US2 — onboarding v3.1：原子核Response新版本

**2026-11-10。主路线：真实核响应表；本地约定下已计算，外部核源认证待补。**

[精简版](<experiment.physics.summary.v3.1.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v3.1.md>) · [两实验总入口](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>) · [来源](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml>) · [配置/决定](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P03_PHYSICS_CONTRACT.yaml>) · [实际Benchmark](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/RESULT.json>) · [旧KN v3.0](<experiment.physics.v3.0.md>)

<a id="report-toc"></a>

## 目录

- [1. 实验范围、身份与版本](#scope)
- [2. Source：总通量、谱形与味态](#source)
- [3. Target、核数与曝光](#target)
- [4. 原子核Response、振幅与截面选择](#modules)
- [5. Detector Response、Qy与数值取得状态](#detector)
- [6. Observable、完整分箱与观测身份](#observable)
- [7. Prediction folding、执行结果与复算](#prediction)
- [8. Statistics、观测与背景的来源和适用范围](#statistics)
- [9. 全部数值资源、轴与逐项来源](#resources)
- [10. 缺失、交接、验证与完整参考文献](#status)

<a id="scope"></a>

## 1. 实验范围、身份与版本

**本版明确采用原子核Response计算，不采用KN作为主预测。** “原子核Response”指振幅内的核结构；探测器响应另见第5章。本版为2026-11-10新版本v3.1；本地核表约定下已实际计算，外部核源认证仍属草稿，不标成论文精确复现终稿。

| 项目 | 本版选择/来源 |
|---|---|
| dataset | PandaX4T_2024_US2；原YAML/NPZ身份与数据不变 |
| 科学决定 | D0004：用户“我现在要求按照response计算”，结合“振幅的，原子核的response”；执行授权W0004，结果接受另行登记 |
| SM基准参数 | R01 arXiv:2411.11749v1 p3 Eq.(2)、p5 Eq.(11)后；sin²θW=0.23857，Φ=5.46×10⁶ cm⁻²s⁻¹固定 |
| 主预测 | 本地核表 → 共享SM匹配 → 粒子/核响应收缩 → 截面 → 原有源与探测器处理 → 事例数 |
| KN用途 | 仅同七核素、同A·amu质量的显式对照；旧九核素KN计算与v3.0原位保留 |
| 通量与校准 | 不拟合或换算通量；不使用作者/经验c_i；无逐箱事后缩放 |

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)


[返回目录](#report-toc)

<a id="source"></a>

## 2. Source：总通量、谱形与味态

<a id="eq-flux"></a>

$$
\frac{d\phi}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu) \tag{1}
$$

公式依据：R01 PDF p5式(11)及后文；R04官网b8spectrum.txt列1–4。总量×谱形为项目对输入的显式分解。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $E_\nu$ | 定义变量；829节点0–16.56 | MeV | R04第一列；`source_energy_MeV` |
| $f_{8B}$ | 已取得；中心谱829点；原积分0.999986544 | MeV⁻¹ | R04第二列；`source_shape_per_MeV` |
| $\Phi_{8B}$ | 已取得；实际值见下表 | cm⁻²s⁻¹ | R01 PDF p5式(11)后；形状表不含它 |
| 味态 | 本轮味普适；用trace-one I₃/3代表等价状态，不当作太阳真实味比例 | 1 | R01 PDF p3 Sec.II B的味普适范围；solar_b8.UniversalSMState |

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `source.total_flux` | 5460000 | cm^-2 s^-1 | R01；2411.11749v1 PDF p5 Eq.(11)后，参考总通量；形状表不含该值 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `source_energy_MeV` | 829; dtype=float64; 范围 [0, 16.56]; 首/中/末 [0, 8.28, 16.56] | MeV | R04；Bahcall官网b8spectrum.txt全部829行第一列；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `source_shape_per_MeV` | 829; dtype=float64; 范围 [0, 0.1321716]; 首/中/末 [0, 0.1154396, 0] | MeV^-1 | R04；同表第二列中心归一化谱；不重归一化，不含总通量/效率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |

官网四列表完整保留：[829×4原数值表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>)。列3/4是原有效±3σ谱形，不是12%的整体通量误差，未转成逐点独立高斯。

实际处理为表内分段线性插值、表外零；中心谱不重归一化。源只生成每秒微分flux，参考年秒数在事件归一化中施加一次，源不含效率或曝光。12%仅作为R01 PDF p6式(17)后的统计参考约束，本轮固定点未profile。传统味相关NSI需要另给太阳传播与味分量；这些数据本轮未取得，也不被I₃/3替代。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R05] VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. The Astrophysical Journal, 2017, 835(2): 202. DOI: [10.3847/1538-4357/835/2/202](https://doi.org/10.3847/1538-4357/835/2/202). [arXiv:1611.09867](https://arxiv.org/abs/1611.09867). 本任务采用的通量值与 12% 误差直接定位于文献 [1] 第 III 节和式 (17) 后文字，后者引用本篇；未声称从任意 SSM 表重新推导。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Vinyoles-abs.html>)


[返回目录](#report-toc)

<a id="target"></a>

## 3. Target、核数与曝光

<a id="eq-inventory"></a>

$$
\overline M=\sum_A f_A M_A,\qquad n_A^{(t)}=\frac{10^6N_{\rm A}f_A}{\overline M} \tag{2}
$$

公式依据：项目按R09全部九种天然Xe中心值及R13 SI阿伏伽德罗常量推导；10⁶为g/t换算。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $f_A$ | 已取得；九核素数丰度，和为1 | 1 | R09 Xe对应A行；不能直接当质量分数 |
| $M_A$ | 已取得；原子质量u的数值按1g/mol近似转换 | g/mol | R09第二列；R13 §2.3.1；不是裸核质量 |
| $N_{\rm A}$ | 已取得；SI精确常量，值见下表 | mol⁻¹ | R13 §2.2/Table1 |
| $n_A^{(t)}$ | 项目推导；每吨各核素核数见表 | nuclei/t | 本式与九行中心值；未传播丰度误差 |

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `target.anchor_mass_kg` | 1000 | kg | 项目配置选择；不是文献测量；计算归一化锚点1t，不是实测探测器质量；与质量时间因子配对 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `target.Z` | 54 | 1 | R09；NIST Xenon，Z=54 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.avogadro` | 6.02214076e+23 | mol^-1 | R13；SI第9版§2.2/Table1精确值 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.amu_GeV` | 0.93149410372 | GeV/u | R18；foundation/constants.py::AMU_GEV；原子质量的GeV换算 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.electron_mass_GeV` | 0.00051099895069 | GeV | R18；foundation/constants.py::m_e；裸核质量近似扣除Z个电子，忽略电子结合能 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |

| 核素A | 原子质量[u] | 数丰度 | 每吨核数[推导] | 直接出处 |
|---|---|---|---|---|
| 124 | 123.905892 | 0.000952 | 4.36663677441e+24 | R09 Xe对应A行；本式 |
| 126 | 125.9042983 | 0.00089 | 4.08225496767e+24 | R09 Xe对应A行；本式 |
| 128 | 127.903531 | 0.019102 | 8.7617117295e+25 | R09 Xe对应A行；本式 |
| 129 | 128.904780861 | 0.264006 | 1.21094360112e+27 | R09 Xe对应A行；本式 |
| 130 | 129.903509349 | 0.04071 | 1.86728763746e+26 | R09 Xe对应A行；本式 |
| 131 | 130.90508406 | 0.212324 | 9.73888431187e+26 | R09 Xe对应A行；本式 |
| 132 | 131.904155086 | 0.269086 | 1.23424456206e+27 | R09 Xe对应A行；本式 |
| 134 | 133.90539466 | 0.104357 | 4.78665035575e+26 | R09 Xe对应A行；本式 |
| 136 | 135.907214484 | 0.088573 | 4.06266931744e+26 | R09 Xe对应A行；本式 |

平均摩尔质量 131.292761448 g/mol；每吨总核数 4.58680333447e+27。上述组成是NIST天然Xe参考，未冒充两实验独立样品化验。完整输入：[九核素原表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>)。

物质数仍使用NIST九核素原子质量；**本版振幅、相空间和运动学统一使用 `m_A=A×0.93149410372 GeV`**，依据R20现有共享振幅约定。旧裸核质量仅留在历史KN包中。计算中的1000kg和31557600s是代数归一化锚点，不是虚构实测质量/活时间。现代SI下将u数值当g/mol是明确的摩尔质量常量近似，未称为精确恒等。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `target_mass_number` | 9; dtype=float64; 范围 [124, 136]; 首/中/末 [124, 130, 136] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_atomic_mass_u` | 9; dtype=float64; 范围 [123.905892, 135.907214484]; 首/中/末 [123.905892, 129.903509349, 135.907214484] | u | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_number_fraction` | 9; dtype=float64; 范围 [0.00089, 0.269086]; 首/中/末 [0.000952, 0.04071, 0.088573] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `run_exposures_tyr` | 1; dtype=float64; 范围 [1.04, 1.04]; 首/中/末 [1.04, 1.04, 1.04] | t yr | R02；2407.10892v3 PDF p3 US2总曝光，未拆造逐run曝光；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |

本轮采用R02 PDF p3的US2总曝光1.04t·yr。原文Run0/Run1 US2 FV质量2.78/2.16t可作参考；afterglow veto后的逐run有效曝光仍MISSING，未按质量比拆造。

### 本章参考文献与核验范围

- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R13] BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)

### 本轮实际参与求和的核素

| 核素 | 原数丰度 | 本轮每吨绝对核数 | 质量GeV | 处理依据 |
|---|---|---|---|---|
| Xe128 | 0.019102 | 8.7617117295e+25 | 119.231245276 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe129 | 0.264006 | 1.21094360112e+27 | 120.16273938 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe130 | 0.04071 | 1.86728763746e+26 | 121.094233484 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe131 | 0.212324 | 9.73888431187e+26 | 122.025727587 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe132 | 0.269086 | 1.23424456206e+27 | 122.957221691 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe134 | 0.104357 | 4.78665035575e+26 | 124.820209898 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |
| Xe136 | 0.088573 | 4.06266931744e+26 | 126.683198106 | R09原九行摩尔质量作分母；D0004不重归一；R20质量约定 |

覆盖天然Xe数丰度99.8158%；缺失Xe124、Xe126合计0.1842%。这不是给遗漏贡献设0的物理假设，而是只交付已覆盖核素的部分预测。七核素对应锚点质量998.248088987kg；完整材料锚点仍为1000kg，曝光分母不变。


[返回目录](#report-toc)

<a id="modules"></a>

## 4. 原子核Response、振幅与截面选择

| 步骤/选择 | 实际组件 | 数据/约定的直接依据 |
|---|---|---|
| 主Interaction | solar_sm_nuclear_table_v1；[SolarNuclearSM](<../../../../../cevns_pyeft/experiments/solar_nuclear.py>) | R20共享SM LEFT与left_to_ci；无一般BSM输入 |
| Nuclear Structure | ResponseDB，七个Xe键、八通道 | R16实际JSON；W=e⁻²ʸΣaₖyᵏ，y=(qb/2)²；q用GeV、b用GeV⁻¹；p/n顺序(p,n) |
| 振幅 | flavor_kernel_onebody_li2026 | R20 amplitude.py：compute_R_matrices→_contract_R_W→各通道和；不再乘KN、Helm或额外自旋因子 |
| 截面 | m_A Tr(ρK)/(8πEν²) | R20 cross_section.py；先cm²/GeV，再乘10⁻⁶为cm²/keV；核数/效率不在截面中 |
| 能量数组 | 固定T下对共享SM振幅作精确二次式重组 | SM非零c1,c2,c5,c6,c7不依赖E；共享R最高E²；三个合法E点确定系数，非实验拟合；第四点与原逐E API对照见测试 |
| 端点 | 精确弹性运动学；A·amu一致 | 仅将小于128ε·Σ\|多项式项\|的浮点相消残差置零，保留非零自旋项 |
| KN对照 | StandardModelKN；半径1.23fm、skin0.7fm | R01 p3 Eq.(3)；只在control使用，与主预测同七核素、同质量、同其余输入 |

### 已打开的真实核数组

| 核素 | J | b [GeV⁻¹] | M系数shape | M(0)：pp / pn / nn |
|---|---|---|---|---|
| Xe128 | 0 | 11.5792987149 | 2×2×11 | [2915.83781333, 3995.65032995, 5475.34622339] |
| Xe129 | 0.5 | 11.5924668142 | 2×2×11 | [2915.96164997, 4049.60832194, 5623.98602234] |
| Xe130 | 0 | 11.605553387 | 2×2×11 | [2915.85321599, 4103.52767595, 5774.9612686] |
| Xe131 | 1.5 | 11.6185595465 | 2×2×11 | [2915.97732507, 4157.7032823, 5928.19993319] |
| Xe132 | 0 | 11.6314863821 | 2×2×11 | [2915.99213116, 4211.83964872, 6083.55318828] |
| Xe134 | 0 | 11.6571063271 | 2×2×11 | [2915.95905802, 4319.24196891, 6397.84400768] |
| Xe136 | 0 | 11.6824214951 | 2×2×11 | [2915.99793279, 4427.99393271, 6723.98634021] |

全部八通道的系数、shape、b与y=0矩阵：[逐核素完整数值审计](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/NUCLEAR_INPUT_AUDIT.json>)；原件：[responses_all.json](<../../../../../data/responses/responses_all.json>)。SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

下表给出本次实际积分的通道，零项为现有SM/实现的结果，不能据此宣称一般EFT通道都不存在。

| 通道 | 各箱合计事例 | 取得/取零依据 |
|---|---|---|
| M | 25.8599517386 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| SigmaPP | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| SigmaP | 0.000712736249313 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| PhiPP | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| PhiPT | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| Delta | 0.00133330723304 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| MPhiPP | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| SigmaPDelta | 0 | 共享SM匹配/粒子响应与R16实际核数组收缩；SigmaPDelta在现有粒子响应定义为0 |

实际LEC值（沿用R20 `lec.py::DEFAULT_LECS`，本地约定；不是R01另公布的实验输入。表列共享配置全部值，SM主要用L1–L4与m_N）：

| 名称 | 实际值 | 单位 | 直接出处 |
|---|---|---|---|
| g_A | 1.2754 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| Sigma_ud | 0.397 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| B0_m_u | 0.0062 | GeV² | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| B0_m_d | 0.0133 | GeV² | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L1 | 1.855 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L2 | -1.017 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L3 | 0.6377 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L4 | -0.22 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L5 | 0.00138 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L6 | -0.00049 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L7 | -0.00676 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L8 | 0.00265 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L9 | 0.01152 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L10 | 0.02405 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L11 | -0.0177 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L12 | -0.0139 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L13 | -0.0504 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| L14 | -0.306 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| sigma_u_p | 0.0185 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| sigma_d_p | 0.036 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| sigma_u_n | 0.0167 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| sigma_d_n | 0.0397 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g1 | 1 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g2 | 1 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g3 | 1 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g4 | 1 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g5 | 1 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g6 | 1 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g7 | 1 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g8 | 1 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| g9 | 1 | 1 | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| m_u | 0.00216 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| m_d | 0.00467 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| m_pi | 0.13957039 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |
| m_N | 0.938918755685 | GeV | R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义 |

### 本章参考文献与核验范围

- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)
- [R20] CEvNS-pyEFT Project. Li2026 one-body SM matching, nuclear-amplitude and cross-section implementation[CP/OL]. 本地工作副本[2026-11-10]. 直接采用本地代码约定；不将其视为R01的核模型或已认证的上游核数据。 [本地直接采用源](<../../../../../cevns_pyeft/theory/li2026/amplitude.py>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)


[返回目录](#report-toc)

<a id="detector"></a>

## 5. Detector Response、Qy与数值取得状态

**本章是探测器读出，与第4章原子核Response是两步。** 继续使用用户D0003选择的无分辨率平均映射；核表路线不自动补出完整US2迁移概率。

**MISSING：2024 US2八个Ne箱的接受后概率P(Ne箱|T)。** 已有Qy、边际接受度和通用校准数值；它们不能唯一决定重建Ne的完整分布。

<a id="eq-mean-yield"></a>

$$
\overline N_e(T)=TQ_y(T) \tag{3}
$$

公式依据：R01 PDF p6式(15)；Qy曲线实际来自R02 PDF p5 Fig.4下图。本式只定义均值，不提供迁移核。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $T$ | 定义变量；Qy原表范围见下表 | keVnr | R02 Fig.4横轴 |
| $Q_y$ | 已取得nominal、best-fit、nominal包络；简化分支采用nominal，完整涨落核仍缺 | electron/keVnr | R02 Fig.4下图对应线型；完整数值文件如下 |
| $\overline N_e$ | 均值/项目派生量；不是逐次观测分布 | electron | 缺少涨落、损失与选择，不能以均值代替P |

| 实际数值文件 | shape/范围 | 单位 | 直接原文定位 | 采用/验证范围 |
|---|---|---|---|---|
| [pandax_qy_nominal.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) | [36, 2]; 各列范围 [0.2, 3.1]; [2.291009926, 6.829535124] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; Nominal dashed line | 2026-11-10简化平均映射主输入；不是完整Ne迁移概率 |
| [pandax_qy_bestfit.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_bestfit.txt>) | [37, 2]; 各列范围 [0.2, 3.1]; [4.422195042, 7.470914283] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; Best-fit solid line | 简化平均映射的best-fit产额敏感性对照；非独立标定 |
| [pandax_qy_nominal_band.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal_band.txt>) | [119, 3]; 各列范围 [0.2018500125, 3.055123576]; [0.1202865379, 6.196027928]; [4.518662938, 7.491408703] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; nominal gray +/-1 sigma band | Qy包络参考；未提供Ne迁移概率或联合协方差 |

Nominal与best-fit的数值含义不同：best-fit为paired+US2联合拟合后的均值曲线，不冒充US2独立标定；包络不是参数协方差。

<a id="eq-response"></a>

$$
P_{ri}(T)=\int_{n_i}^{n_{i+1}}dn\int dw\,p_r(n,w\mid T)\,\mathcal S_r(n,w,T) \tag{4}
$$

公式依据：项目对“通过选择并进入Ne箱”的概率定义；R02原生Ne/width分析沿width边际化到本次一维目标。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $P_{ri}$ | **MISSING**：US2低能八箱接受后核 | 1 | 阻断Ne重建谱、对应χ²与排除限 |
| $p_r(n,w\|T)$ | **MISSING**：给定T的重建Ne/width联合分布或等价一维核 | 密度单位取决于坐标 | 量子涨落、电子损失、读出及选择的完整配置可替代直接矩阵 |
| $\mathcal S_r$ | 条件选择MISSING；边际总接受度已取得 | 1 | R02 PDF p3 Fig.1黑色Total(US2)只约束ΣP(T) |
| $n_i$ | 4,4.5,…,8，八箱完整边界见第6章 | electron | R01 PDF p5式(12)后与R02 Fig.5 |

完整响应矩阵指“固定真实反冲T时，每个观测箱的通过概率”；模拟配置指能生成同一概率的涨落、电子输运/读出和选择参数及算法。均值Qy、总接受度或已对源谱积分的事例数图都不能唯一反演该核。未自行补Poisson/Gaussian宽度。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `efficiency_energy_keV` | 99; dtype=float64; 范围 [0.299999999496, 2.9999999995]; 首/中/末 [0.299999999496, 1.6404999995, 2.9999999995] | keVnr | R02；2407.10892v3 PDF p3 Fig.1黑色Total(US2)99个可见域矢量节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `efficiency` | 99; dtype=float64; 范围 [0.00579130467031, 0.191620952606]; 首/中/末 [0.00579130467031, 0.141846330574, 0.0155469009404] | 1 | R02；同曲线接受度；仅展示真实反冲接受度加权，不代表Ne 4–8的迁移概率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |

原Response路线在正式真实反冲箱可见域内对这99个PDF矢量节点分段线性插值。**R02 PDF p3 ROI说明及Fig.1标题明确，Total(US2)已包含Ne∈[4,8]选择。** 原27箱是该选后样本的真实T分布，总效率本身不提供每个Ne箱的分配。完整Response不能重复裁剪均值窗口；简化分支明确采用平均映射裁窗并量化损失；后验拟合谱缩放只作历史参考，不用于补成SSM预测。

<a id="eq-simplified-counts"></a>

$$
S_i^{\rm raw}=\mathcal E\int_{T(n_i)}^{T(n_{i+1})}dT\,\frac{dR}{dT} \tag{5}
$$

公式依据：R01 PDF p5式(11)–(13)、p6式(15)；dR/dT含源、靶核数、SM与R02 Fig.1总接受度。此式为c_i=1的项目基线。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $T(n_i)$ | 由R02 nominal Qy线性插值并反解TQy(T)=n_i；0.660084–1.186893 | keVnr | R01 p5脚注3与p6式(15)；显式参数卡记录算法 |
| $dR/dT$ | 本轮共享Source/Target/SM积分并乘Total(US2)一次 | events/(t·yr·keVnr) | R01式(11)；第2–4章；原正式包 |
| $S_i^{raw}$ | 固定SSM通量下计算8箱；后验拟合谱缩放仅为参考 | events/bin | RESULT.json与events_by_bin.tsv；第7章完整数值 |

历史经验比值=实验Fig.5拟合信号/[直接SM×(8.4/5.46)]；8.4×10⁶与75±28来自R02 PDF p6。该缩放仍保留实验拟合的产额/系统参数，不能视为同一基准Response下的SSM校准预测。独立前向计算始终固定Φ₀=5.46×10⁶、c_i=1；作者原始c_i未取得。

### 通用响应标定参考（未绑定本轮Ne核）

[完整原文摘录文件：pandax_response_calibration_2403.04239v2.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>)

| 参考参数 | 值 | 误差/变化 | 单位 | 直接出处 |
|---|---|---|---|---|
| p_dpe | 0.22 | 未单列 | 1 | R06；2403.04239v2 p21 Table II |
| g1 | 0.0997 | −0.0005/+0.0002 | PE/photon | R06；2403.04239v2 p21 Table II |
| g2b | 4.12 | −0.04/+0.06 | PE/electron | R06；2403.04239v2 p21 Table II |
| f_g1_Run1 | 0.90985 | 未单列 | 1 | R06；2403.04239v2 p21 Table II |
| f_g2b_Run1 | 1.22067 | 未单列 | 1 | R06；2403.04239v2 p21 Table II |
| pNR_0 | 0.7 | −0.3/+0.3 | 1 | R06；2403.04239v2 p21 Table II |
| pNR_1 | -1.6 | −0.7/+0.9 | 1 | R06；2403.04239v2 p21 Table II |
| pNR_2 | 1.3 | −0.7/+0.5 | 1 | R06；2403.04239v2 p21 Table II |
| pNR_3 | -0.6 | −0.4/+0.4 | 1 | R06；2403.04239v2 p21 Table II |
| A_NR | 1.06 | −0.1/+0.09 | 1 | R06；2403.04239v2 p21 Table II |

g₂b是bottom-array增益，不是总S2增益。以上10个印刷值及误差来自R06 PDF p21 Table II；没有US2 sub-keV专用的完整时间依赖/选择函数，不能把该表宣称为已取得完整响应配置。

### 本章参考文献与核验范围

- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R06] LUO Y, BO Z, ZHANG S, et al. (PandaX Collaboration). Signal response model in PandaX-4T[J]. Physical Review D, 2024, 110: 023029. DOI: [10.1103/PhysRevD.110.023029](https://doi.org/10.1103/PhysRevD.110.023029). 实际提取 [arXiv:2403.04239v2](https://arxiv.org/abs/2403.04239v2), 2024-03-08，第 21 页 Table II；本文 NR 拟合适用范围不能外推冒充 US2 sub-keV 校准。 [本地直接采用源](<../../../../references/Solar_CEvNS/2403.04239v2.pdf>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R11] ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)

**c_i的地位：** R01式(12)的c_i是作者简化分析的有效修正，原Response路线不引入。PandaX直接预测固定SSM通量且c=1；历史字段effective_calibration只保存后验拟合谱缩放比值，不代表独立的探测器校准或SSM预测。作者原始c_i仍未获得，严格论文等价性未认证。

### 本版实际执行的简化观测

| 输入 | 实际数值/文件 | 直接出处和处理 |
|---|---|---|
| Qy | [36×2 nominal表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) | R02 2407.10892v3 p5 Fig.4下图；T=0.2–3.1keVnr；分段线性，无外推 |
| 总接受度 | [99×2表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>) | R02 p3 Fig.1黑虚线Total(US2)，已含ROI；只乘一次 |
| 均值映射 | Ne=T Qy(T) | R01 p6 Eq.(15)；不展宽；逐箱积分使用逆映射T边界，不另乘第二次Jacobian |
| Ne箱界 | [4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8] | R01 p5式(12)后；8箱 |
| 反解T边界[keVnr] | [0.660083707212, 0.723216674108, 0.787020684029, 0.851620736559, 0.917067309103, 0.983359819647, 1.05046480663, 1.11832952786, 1.18689262165] | 由实际Qy表逐段线性和brentq反解；完整算法solar_mean_map.py::inverse_mean_edges |
| c_i | 不应用，即直接预测基线1 | 用户选择；不声称作者c_i=1；不匹配拟合图线振幅 |


[返回目录](#report-toc)

<a id="observable"></a>

## 6. Observable、完整分箱与观测身份

**当前输出为八个Ne箱，边界[4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8]；原包27个T箱仅为历史元数据。**

| 能力/坐标 | 完整边界 | 采用状态与出处 |
|---|---|---|
| 目标Ne谱 | [4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8] | electron；R01式(12)后与R02 Fig.5；信号P(Ne箱\|T) MISSING |
| 历史KN包的真实反冲投影（非本版Ne输出） | [0.299999999496, 0.399999999496, 0.499999999496, 0.599999999496, 0.699999999497, 0.799999999497, 0.899999999497, 0.999999999497, 1.0999999995, 1.1999999995, 1.2999999995, 1.3999999995, 1.4999999995, 1.5999999995, 1.6999999995, 1.7999999995, 1.8999999995, 1.9999999995, 2.0999999995, 2.1999999995, 2.2999999995, 2.3999999995, 2.4999999995, 2.5999999995, 2.6999999995, 2.7999999995, 2.8999999995, 2.9999999995] | keVnr；27箱项目输出选择，完整值来自正式NPZ；已含ROI选取，横轴仍为T，未分配Ne箱 |

原实验Fig.5观测八箱D=[73, 44, 29, 44, 41, 38, 28, 35]，合计332；后续官方事件CSV只用于核对，不凭相同一维计数认证2024完整事件ID。width的µs单位关联R11后续论文，原CSV表头未独立编码单位。

### 本章参考文献与核验范围

- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R11] ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)


[返回目录](#report-toc)

<a id="prediction"></a>

## 7. Prediction folding、执行结果与复算

**本版结果由真实核表独立计算。蓝色论文参考线由图中提取，始终不作为本项目Response预测。**

| 阶段 | 实际代码/输入 | 物理工作与出处 |
|---|---|---|
| P01–P03 | load_experiment_package | 读原YAML/NPZ：R04源谱、R09核数、R01参数、实验曝光 |
| P04 | with_solar_nuclear_response → SolarNuclearSM | 显式绑定R16七核素；R20匹配与粒子/核响应收缩 |
| P05 | SolarNuclearSM.dsigma_dT | 同A·amu、精确支撑、m/(8πE²)和cm²/keV转换 |
| P06 | MeanMapExecutor | R02 Qy+Total接受度+R01平均映射 |
| P07 | predict_experiment → integrate_recoil_yield | 逐核素卷积源谱，再乘核数/曝光与选区折叠；每因子一次 |
| P10 | run_solar_b8_nuclear_benchmark.py | T与Eν分别加密；逐核素/通道/运行期闭合，保留KN公平对照 |

### 实际逐箱信号 [events/bin]

| 箱 | 核表SM | 其中M | 同范围KN | 核表/KN−1 |
|---|---|---|---|---|
| 1 | 3.6030804791 | 3.60285399436 | 3.59499728318 | +0.224846% |
| 2 | 3.72182850521 | 3.72157738688 | 3.71266413633 | +0.246841% |
| 3 | 3.69899979608 | 3.69873224297 | 3.68907085523 | +0.269145% |
| 4 | 3.55855882202 | 3.55828337853 | 3.54820487965 | +0.291808% |
| 5 | 3.30914044746 | 3.30886622299 | 3.29875457441 | +0.314842% |
| 6 | 3.00299527432 | 3.00272915136 | 2.99287152888 | +0.338262% |
| 7 | 2.66351248098 | 2.66326036726 | 2.65390522199 | +0.362005% |
| 8 | 2.3038819769 | 2.30364899424 | 2.29502039558 | +0.386122% |

合计：**核表SM 25.861997782**；同范围KN 25.785488875事例。比较同时改变完整SM核通道与核结构；M-only列可单独查看相干主项。

| run | 实际信号数组 |
|---|---|
| US2 | [3.6030804791, 3.72182850521, 3.69899979608, 3.55855882202, 3.30914044746, 3.00299527432, 2.66351248098, 2.3038819769] |

已提取Total接受度T域积分47.041722159事例；均值窗口下/上方各为[11.707439492, 9.47228488492]。不能把这些迁移未知的域外事件强行补进八箱。

[结果、独立收敛与全部输入参数](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/RESULT.json>) · [完整各核素/通道数组](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/prediction.npz>) · [实际Runtime装配与全部资源哈希](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/PREPARED_MODEL.nuclear.json>)

![核表Response SM与同范围KN](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/events.png>)

绿实线=本版真实核表SM；橙虚线=同七核素KN直接计算；灰线=背景参考；黑点=观测及68.27% Garwood Poisson误差棒。PandaX蓝点线=论文作者S+B数字化参考。没有紫色校准线。

**历史比较边界。** 旧九核素/旧裸核质量KN结果和旧V/B−L点只在[历史v3.0](<experiment.physics.v3.0.md>)中保留。R01 Fig.1只作为文献参考，R01 Fig.2/4仍不是本次统计计算。

当前SM主入口`tools/run_solar_b8_sm_benchmark.py`默认转到本核表路线；只有显式`--legacy-kn`才运行历史KN。原包的KN装配仍可单独加载，不能把它与本版显式核表覆盖混用。

[onboarding＋P01–P10真实M核响应最小代码](<../../../../../../重构/20261110_PandaX_Response_P01_P10_物理与最小代码/README.md>)：各份代码独立运行，至多200行；M-only教学缩减与本版全部已实现SM通道分别标注。

[返回目录](#report-toc)

<a id="statistics"></a>

## 8. Statistics、观测与背景的来源和适用范围

**本轮不作拟合。** 信号前向积分不读取D/B；它们只进入比较图。

**已执行的是固定点前向预测与观测/名义背景作图；统计evaluator、χ²最小化、置信区间未实现/未运行。** 下列R01统计合同作为后续明确依据保留，不因公式写出就声称统计能力已完成。

<a id="eq-mean-counts"></a>

$$
\mu_i=(1+\alpha)(1+\beta_s)S_i(\theta)+\sum_k(1+\beta_k)B_i^k \tag{6}
$$

公式依据：项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $D_i$ | 观测计数已有；原始身份/当前范围见下表 | events/bin | 不是背景扣除残差 |
| $S_i$ | 本版已有简化Ne核表SM信号；完整探测器涨落信号仍MISSING，不冒充原生拟合输入 | events/bin | 第7章相应能力 |
| $B_i^k$ | 拟合/参考投影已有，原prefit形状另待补 | events/bin | 下表严格区分来源版本与用途 |
| $\alpha,\beta_s,\beta_k$ | 定义的统计归一化nuisance；本轮未profile | 1 | R01 PDF p6式(17)后；σ按单独模型表采用 |

<a id="eq-deviance"></a>

$$
\chi^2_{\rm prof}=\min_{\alpha,\boldsymbol\beta}\left[2\sum_i\left(\mu_i-D_i+D_i\ln\frac{D_i}{\mu_i}\right)+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\sum_k\left(\frac{\beta_k}{\sigma_k}\right)^2\right] \tag{7}
$$

公式依据：R01 PDF p6式(17)及后文；零观测的Dlog项取连续极限0。当前只记录合同，无minimizer结果。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $\sigma_\alpha$ | 0.12，太阳总通量整体约束 | 1 | R01式(17)后；联合实验只计一次 |
| $\sigma_k$ | 下列再分析模型的率不确定度 | 1 | 不能与原实验native表或light-WIMP约束静默合并 |
| $\mu_i>0$ | Poisson模型合法域；尚未选择具体优化参数化 | events/bin | 统计方法要求；未虚构协方差或置信阈值 |

上式pull求和覆盖信号率与各背景率的全部β参数；前一式背景求和中的k仅枚举背景组分。

| R01再分析归一化项 | 相对σ | 直接出处/实际采用状态 |
|---|---|---|
| signal | 0.22 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |
| cathode | 0.31 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |
| MD | 0.23 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |

### 原图观测、拟合背景与参考信号（八箱完整投影）

**R02 2407.10892v3 PDF p6 Fig.5上图**；[原数值文件](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_original_fig5.txt>)：

| 箱 | Ne下界 | Ne上界 | D | cathode | MD | 参考信号 |
|---|---|---|---|---|---|---|
| 1 | 4 | 4.5 | 73 | 27.26989126 | 34.093572 | 13.91851412 |
| 2 | 4.5 | 5 | 44 | 26.38805876 | 6.246193401 | 12.32647586 |
| 3 | 5 | 5.5 | 29 | 27.35400144 | 2.088536709 | 10.81135802 |
| 4 | 5.5 | 6 | 44 | 31.2185977 | 0.9701096464 | 9.663605793 |
| 5 | 6 | 6.5 | 41 | 20.83561346 | 0.4984230378 | 8.498071767 |
| 6 | 6.5 | 7 | 38 | 28.11892848 | 0.5458457304 | 7.432962388 |
| 7 | 7 | 7.5 | 28 | 24.75227235 | 0.2224757103 | 6.615482365 |
| 8 | 7.5 | 8 | 35 | 22.84922386 | 0.3367382347 | 5.586346254 |

**R01 2411.11749v1 PDF p7 Fig.1左图**；[原数值文件](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt>)：

| 箱 | Ne下界 | Ne上界 | D | cathode | MD | 参考信号 |
|---|---|---|---|---|---|---|
| 1 | 4 | 4.5 | 73 | 26.62983436 | 33.97790043 | 13.81782768 |
| 2 | 4.5 | 5 | 44 | 25.8011051 | 6.132596501 | 12.33779822 |
| 3 | 5 | 5.5 | 29 | 26.62983436 | 2.486187771 | 10.80184494 |
| 4 | 5.5 | 6 | 44 | 30.44198894 | 0.9944751082 | 9.671681397 |
| 5 | 6 | 6.5 | 41 | 20.16574585 | 0.4972375541 | 8.481800144 |
| 6 | 6.5 | 7 | 38 | 27.45856361 | 0.4972375541 | 7.628396164 |
| 7 | 7 | 7.5 | 28 | 24.14364658 | 0.1657458514 | 6.720131073 |
| 8 | 7.5 | 8 | 35 | 22.32044192 | 0.1657458514 | 5.687951539 |


以上背景/信号由堆叠多边形厚度数字化，非独立测得背景，也非无条件可用prefit形状。数字化精度不等于物理误差；不从包络推断协方差。


[完整原文摘录文件：pandax_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_prefit_inputs_2024.v2.1.json>)

| 参考参数 | 值 | 误差/变化 | 单位 | 直接出处 |
|---|---|---|---|---|
| cathode_Run0 | 100 | ±24 | events | R02；2407.10892v3 PDF p4 Table III, cathode, US2 Run0 |
| cathode_Run1 | 104 | ±21 | events | R02；2407.10892v3 PDF p4 Table III, cathode, US2 Run1 |
| MD_Run0 | 25 | ±3 | events | R02；2407.10892v3 PDF p4 Table III, MD, US2 Run0 |
| MD_Run1 | 20 | ±4 | events | R02；2407.10892v3 PDF p4 Table III, MD, US2 Run1 |
| ER_Run0 | 1.3 | ±0.1 | events | R02；2407.10892v3 PDF p4 Table III, ER, US2 Run0 |
| ER_Run1 | 0.9 | ±0.2 | events | R02；2407.10892v3 PDF p4 Table III, ER, US2 Run1 |
| total_background_Run0 | 126 | ±24 | events | R02；2407.10892v3 PDF p4 Table III, total_background, US2 Run0 |
| total_background_Run1 | 125 | ±21 | events | R02；2407.10892v3 PDF p4 Table III, total_background, US2 Run1 |
| signal_reference_Run0 | 18 | ±4 | events | R02；2407.10892v3 PDF p4 Table III, signal_reference, US2 Run0 |
| signal_reference_Run1 | 25 | ±6 | events | R02；2407.10892v3 PDF p4 Table III, signal_reference, US2 Run1 |

原US2逐run总率误差另列：

[完整原文摘录文件：pandax_us2_rate_uncertainties_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_us2_rate_uncertainties_2024.v2.1.json>)

| 参考参数 | 值 | 误差/变化 | 单位 | 直接出处 |
|---|---|---|---|---|
| signal_selection_Run0 | 0.11 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run0 |
| signal_selection_Run1 | 0.17 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run1 |
| signal_model_Run0 | 0.17 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run0 |
| signal_model_Run1 | 0.16 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run1 |
| cathode_model_Run0 | 0.24 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run0 |
| cathode_model_Run1 | 0.2 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run1 |
| MD_model_Run0 | 0.13 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run0 |
| MD_model_Run1 | 0.16 | 未单列 | fractional rate uncertainty | R02；PDF p5 Table IV, US2 Run1 |

上述是R02 Table III/IV原实验的约束与总数，不等于R01采用的22/31/23%再分析约束。后续官方259日Ne/width事件表只作来源可核的参考；不能凭8箱D一致认证2024完整事件身份或原prefit背景形状。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R11] ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)

Fig.2的通量扫描如何重参数化12% flux pull，以及Fig.4的90% CL构造/自由度/阈值，目前都未通过本项目统计实现认证。本轮没有选择单位协方差、擅补独立高斯或把χ²公式存在当作已有扫描结果。


[返回目录](#report-toc)

<a id="resources"></a>

## 9. 全部数值资源、轴与逐项来源

YAML/NPZ保持原包字节；当前执行权威是“原包＋显式核表覆盖”（PandaX另加Qy），不能只打开原包就认为默认已经更换。实际路径和哈希如下。

| 资源ID | 完整本地数值文件 | SHA256 | 本轮用途/直接定位 |
|---|---|---|---|
| package_input | [experiment.input.yaml](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) | c7299d35b5fdb192b425a12cb8b5571ea5218619e1bb5ce2f689e8b08bc1e046 |  |
| package_arrays | [experiment.resources.npz](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) | 56a44e766476c7bc8771e2e98e316c48a97e13d485d006d12324ba473b4f09b8 |  |
| mean_charge_yield | [pandax_qy_nominal.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) | 18e0cee351c09fb6e3c1b286b5a15de88c8a9c9aa371cb0367946aa57e36f75f | 2407.10892v3 p5 Fig.4 lower, digitized nominal Qy |
| nuclear_response | [responses_all.json](<../../../../../data/responses/responses_all.json>) | cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74 | existing np nuclear polynomial table; external source unresolved |

### 原包正式数组全部清单

原包observable_edges与KN配置为保留的历史元数据；当前观测边界与核模型以上述实际装配为准。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `efficiency` | 99; dtype=float64; 范围 [0.00579130467031, 0.191620952606]; 首/中/末 [0.00579130467031, 0.141846330574, 0.0155469009404] | 1 | R02；同曲线接受度；仅展示真实反冲接受度加权，不代表Ne 4–8的迁移概率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `efficiency_energy_keV` | 99; dtype=float64; 范围 [0.299999999496, 2.9999999995]; 首/中/末 [0.299999999496, 1.6404999995, 2.9999999995] | keVnr | R02；2407.10892v3 PDF p3 Fig.1黑色Total(US2)99个可见域矢量节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `observable_edges` | 28; dtype=float64; 范围 [0.299999999496, 2.9999999995]; 首/中/末 [0.299999999496, 1.6999999995, 2.9999999995] | keVnr | USER；本轮显式输出坐标：可见能区分27个真实反冲箱，非电子数箱；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `run_exposures_tyr` | 1; dtype=float64; 范围 [1.04, 1.04]; 首/中/末 [1.04, 1.04, 1.04] | t yr | R02；2407.10892v3 PDF p3 US2总曝光，未拆造逐run曝光；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `source_energy_MeV` | 829; dtype=float64; 范围 [0, 16.56]; 首/中/末 [0, 8.28, 16.56] | MeV | R04；Bahcall官网b8spectrum.txt全部829行第一列；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `source_shape_per_MeV` | 829; dtype=float64; 范围 [0, 0.1321716]; 首/中/末 [0, 0.1154396, 0] | MeV^-1 | R04；同表第二列中心归一化谱；不重归一化，不含总通量/效率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_atomic_mass_u` | 9; dtype=float64; 范围 [123.905892, 135.907214484]; 首/中/末 [123.905892, 129.903509349, 135.907214484] | u | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_mass_number` | 9; dtype=float64; 范围 [124, 136]; 首/中/末 [124, 130, 136] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_number_fraction` | 9; dtype=float64; 范围 [0.00089, 0.269086]; 首/中/末 [0.000952, 0.04071, 0.088573] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |

### 辅助表与其出处

| 数值文件 | shape/范围 | 单位 | 直接来源、定位与转换 | 本版用途 |
|---|---|---|---|---|
| [pandax_qy_nominal.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) | [36, 2]，各列范围：[0.2, 3.1]; [2.291009926, 6.829535124] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; Nominal dashed line；PDF vector digitization; logarithmic energy; no gain/efficiency/exposure | 2026-11-10简化平均映射主输入；不是完整Ne迁移概率 |
| [pandax_qy_bestfit.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_bestfit.txt>) | [37, 2]，各列范围：[0.2, 3.1]; [4.422195042, 7.470914283] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; Best-fit solid line；joint paired+US2 fitted mean; not US2-only calibration | 简化平均映射的best-fit产额敏感性对照；非独立标定 |
| [pandax_qy_nominal_band.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal_band.txt>) | [119, 3]，各列范围：[0.2018500125, 3.055123576]; [0.1202865379, 6.196027928]; [4.518662938, 7.491408703] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; nominal gray +/-1 sigma band；PDF vector band; no covariance inferred | Qy包络参考；未提供Ne迁移概率或联合协方差 |
| [pandax_original_fig5.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_original_fig5.txt>) | [8, 7]，各列范围：[1, 8]; [4, 7.5]; [4.5, 8]; [28, 73]; [20.83561346, 31.2185977]; [0.2224757103, 34.093572]; [5.586346254, 13.91851412] | D/background/reference signal events/bin, coordinate columns as declared | R02；2407.10892v3 PDF p6 Fig.5 upper, 4<=Ne<8；D integers; fitted stacked components separated by polygon thickness | 图线拟合/参考投影；非独立prefit背景 |
| [pandax_benchmark_fig1.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt>) | [8, 7]，各列范围：[1, 8]; [4, 7.5]; [4.5, 8]; [28, 73]; [20.16574585, 30.44198894]; [0.1657458514, 33.97790043]; [5.687951539, 13.81782768] | D/background/reference signal events/bin, coordinate columns as declared | R01；2411.11749v1 PDF p7 Fig.1 left；benchmark reference components; not independent prefit B | 图线拟合/参考投影；非独立prefit背景 |
| [b8_bahcall1996_official.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) | [829, 4]，各列范围：[0, 16.56]; [0, 0.1321716]; [0, 0.1339827]; [0, 0.1304072] | MeV; MeV^-1 | R04；official b8spectrum.txt, all four columns；byte-identical download | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenon_natural_isotopes_nist_v2.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) | [9, 3]，各列范围：[124, 136]; [123.905892, 135.907214484]; [0.00089, 0.269086] | 1; u; 1 | R09；Xe rows 124,126,128,129,130,131,132,134,136；parsed central values; uncertainties retained in official source download, not treated as zero | 本轮前向输入的直接来源，已封入正式NPZ |
| [pandax_official_later_run0_events.csv](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run0_events.csv>) | 158行；Ne, Width | electron; Width unit follows associated paper, not encoded in CSV header | R10；p4-light-dark-matter/run0_data.csv；byte-identical download | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_official_later_run1_events.csv](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run1_events.csv>) | 174行；Ne, Width | electron; Width unit follows associated paper, not encoded in CSV header | R10；p4-light-dark-matter/run1_data.csv；byte-identical download | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_official_later_run_bins_v2.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run_bins_v2.txt>) | [16, 5]，各列范围：[0, 1]; [1, 8]; [4, 7.5]; [4.5, 8]; [14, 38] | 1; 1; electron; electron; events/bin | R10；two event CSV; 0.5-electron bins in [4,8]；numpy.histogram by run | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_response_calibration_2403.04239v2.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>) | 10条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R06；2403.04239v2 p21 Table II；manual transcription with visual check | 通用标定参考；非US2 sub-keV完整响应 |
| [pandax_us2_rate_uncertainties_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_us2_rate_uncertainties_2024.v2.1.json>) | 8条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R02；2407.10892v3 PDF p5 Table IV, US2 columns；transcribed printed primary-source values | 原2024总数/率误差参考；完整形状另需取得 |
| [pandax_us2_acceptance_2407.10892v3.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>) | [99, 2]，各列范围：[0.299999999496, 2.9999999995]; [0.00579130467031, 0.191620952606] | as declared per column/key in the numerical file and chapter | R02；2407.10892v3 PDF p3 Fig.1, black dashed Total(US2), PDF curve index9；native PDF vertices calibrated to linear energy/log efficiency; edge intersections in PDF coordinates | 本轮前向输入的直接来源，已封入正式NPZ |
| [pandax_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_prefit_inputs_2024.v2.1.json>) | 10条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R02；2407.10892v3 PDF p4 Table III, US2 Run0/Run1 expectation；transcription of printed prefit totals and uncertainties | 原2024总数/率误差参考；完整形状另需取得 |

第4章的核表审计显示全部实际系数；外部作者来源未闭合是“来源认证待补”，与Xe124/Xe126“数值MISSING”分别记录。


[返回目录](#report-toc)

<a id="status"></a>

## 10. 缺失、交接、验证与完整参考文献

| 能力 | 状态 | 缺口/限制 |
|---|---|---|
| 本地核表SM事例数 | 已算；本地ResponseDB/Li2026约定 | 数值资源已具备；科学结果接受NOT_REVIEWED |
| 完整天然Xe九核素 | PARTIAL | MISSING：Xe124、Xe126核响应系数；未用KN/邻核补齐，七核素不重归一 |
| 核表外部作者/生成认证 | UNRESOLVED | R16原始作者发布、转换与外部绝对归一化；不阻断用户明确选择的本地复用 |
| 探测器读出 | US2无分辨率平均映射 | 完整US2接受后P(Ne箱\|T)仍未重建 |
| 2411.11749v1 Fig.1等价 | 未认证 | 该文采用KN且含作者c_i/拟合约定；本轮按用户要求改用核表，论文蓝线只作参考 |
| Fig.2/4统计 | 未计算 | 适用的背景与响应nuisance、拟合/置信区间约定仍需完成 |
| V/B−L旧结果 | 保留KN历史结果 | 本轮只重算SM；不得把旧矢量结果标为核表Response计算 |

计算入口：

```powershell
python -B tools/run_solar_b8_nuclear_benchmark.py --output <新的运行目录>
python -B tools/build_solar_b8_onboarding_v3_1.py --check
```

本次验证：[实际测试/文件保护/来源检查](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/VALIDATION.json>)。旧数值未改，结果接受NOT_REVIEWED；不自动推进历史完整探测器响应或统计门槛。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R05] VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. The Astrophysical Journal, 2017, 835(2): 202. DOI: [10.3847/1538-4357/835/2/202](https://doi.org/10.3847/1538-4357/835/2/202). [arXiv:1611.09867](https://arxiv.org/abs/1611.09867). 本任务采用的通量值与 12% 误差直接定位于文献 [1] 第 III 节和式 (17) 后文字，后者引用本篇；未声称从任意 SSM 表重新推导。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Vinyoles-abs.html>)
- [R06] LUO Y, BO Z, ZHANG S, et al. (PandaX Collaboration). Signal response model in PandaX-4T[J]. Physical Review D, 2024, 110: 023029. DOI: [10.1103/PhysRevD.110.023029](https://doi.org/10.1103/PhysRevD.110.023029). 实际提取 [arXiv:2403.04239v2](https://arxiv.org/abs/2403.04239v2), 2024-03-08，第 21 页 Table II；本文 NR 拟合适用范围不能外推冒充 US2 sub-keV 校准。 [本地直接采用源](<../../../../references/Solar_CEvNS/2403.04239v2.pdf>)
- [R07] APRILE E, et al. (XENON Collaboration). XENONnT WIMP search: Signal and background modeling and statistical inference[J]. Physical Review D, 2025, 111: 103040. DOI: [10.1103/PhysRevD.111.103040](https://doi.org/10.1103/PhysRevD.111.103040). 实际提取 [arXiv:2406.13638v1](https://arxiv.org/abs/2406.13638v1), 2024-06-19，第 6 页 Fig.3 右下图；期刊版为后续版本，不替换本次所用曲线。 [本地直接采用源](<../../../../references/Solar_CEvNS/2406.13638v1.pdf>)
- [R08] XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R11] ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)
- [R12] APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26；文献 [1] 的背景关联来源 [72]。 [本地直接采用源](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)
- [R13] BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。
- [R14] APRILE E, et al. (XENON Collaboration). Probing the Solar ⁸B Neutrino Fog with XENONnT[J]. Physical Review Letters, 2026, 137: 091807. DOI: [10.1103/xvpn-w3q9](https://doi.org/10.1103/xvpn-w3q9). 本库保存 [arXiv:2604.06002v2](https://arxiv.org/abs/2604.06002v2), 2026-08-28。文献 [8] README 指定它为后续数据与模板的关联论文；本任务只提取 SR0/SR1 候选，不纳入 SR2。 [本地直接采用源](<../../../../references/Solar_CEvNS/2604.06002v2.pdf>)
- [R15] CEvNS-pyEFT共享模型登记[CP/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `1d03f7e0136be69c7d8c12324eb4e26c1c0c6093496efc7c19bfd77f9f1bcf24`。 [本地直接采用源](<../../../../../cevns_pyeft/experiments/model_bindings.json>)
- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)
- [R20] CEvNS-pyEFT Project. Li2026 one-body SM matching, nuclear-amplitude and cross-section implementation[CP/OL]. 本地工作副本[2026-11-10]. 直接采用本地代码约定；不将其视为R01的核模型或已认证的上游核数据。 [本地直接采用源](<../../../../../cevns_pyeft/theory/li2026/amplitude.py>)


[返回目录](#report-toc)
