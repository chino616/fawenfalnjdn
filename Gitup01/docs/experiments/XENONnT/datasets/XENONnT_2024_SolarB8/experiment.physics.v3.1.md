# XENONnT_2024_SolarB8 — onboarding v3.1：原子核Response新版本

**2026-11-10。主路线：真实核响应表；本地约定下已计算，外部核源认证待补。**

[精简版](<experiment.physics.summary.v3.1.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v3.1.md>) · [两实验总入口](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>) · [来源](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml>) · [配置/决定](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P03_PHYSICS_CONTRACT.yaml>) · [实际Benchmark](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/RESULT.json>) · [旧KN v3.0](<experiment.physics.v3.0.md>)

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
| dataset | XENONnT_2024_SolarB8；原YAML/NPZ身份与数据不变 |
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
| `source.total_flux` | 5460000 | cm^-2 s^-1 | R01；2411.11749v1 PDF p5 Eq.(11)后，参考总通量；形状表不含该值 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `source_energy_MeV` | 829; dtype=float64; 范围 [0, 16.56]; 首/中/末 [0, 8.28, 16.56] | MeV | R04；Bahcall官网b8spectrum.txt全部829行第一列；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `source_shape_per_MeV` | 829; dtype=float64; 范围 [0, 0.1321716]; 首/中/末 [0, 0.1154396, 0] | MeV^-1 | R04；同表第二列中心归一化谱；不重归一化，不含总通量/效率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |

官网四列表完整保留：[829×4原数值表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>)。列3/4是原有效±3σ谱形，不是12%的整体通量误差，未转成逐点独立高斯。

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
| `target.anchor_mass_kg` | 1000 | kg | 项目配置选择；不是文献测量；计算归一化锚点1t，不是实测探测器质量；与质量时间因子配对 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `target.Z` | 54 | 1 | R09；NIST Xenon，Z=54 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.avogadro` | 6.02214076e+23 | mol^-1 | R13；SI第9版§2.2/Table1精确值 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.amu_GeV` | 0.93149410372 | GeV/u | R18；foundation/constants.py::AMU_GEV；原子质量的GeV换算 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.electron_mass_GeV` | 0.00051099895069 | GeV | R18；foundation/constants.py::m_e；裸核质量近似扣除Z个电子，忽略电子结合能 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |

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

平均摩尔质量 131.292761448 g/mol；每吨总核数 4.58680333447e+27。上述组成是NIST天然Xe参考，未冒充两实验独立样品化验。完整输入：[九核素原表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt>)。

物质数仍使用NIST九核素原子质量；**本版振幅、相空间和运动学统一使用 `m_A=A×0.93149410372 GeV`**，依据R20现有共享振幅约定。旧裸核质量仅留在历史KN包中。计算中的1000kg和31557600s是代数归一化锚点，不是虚构实测质量/活时间。现代SI下将u数值当g/mol是明确的摩尔质量常量近似，未称为精确恒等。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `target_mass_number` | 9; dtype=float64; 范围 [124, 136]; 首/中/末 [124, 130, 136] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_atomic_mass_u` | 9; dtype=float64; 范围 [123.905892, 135.907214484]; 首/中/末 [123.905892, 129.903509349, 135.907214484] | u | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_number_fraction` | 9; dtype=float64; 范围 [0.00089, 0.269086]; 首/中/末 [0.000952, 0.04071, 0.088573] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `run_exposures_tyr` | 2; dtype=float64; 范围 [1.174398, 2.342593]; 首/中/末 [1.174398, 2.342593, 2.342593] | t yr | R17；官方statistical_model_base.yaml livetime_sr0/1；每t yr模板的曝光乘数。合计3.516991，与论文打印3.51分别报告；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |

R17早期发布曝光SR0=1.174398、SR1=2.342593 t·yr，合计3.516991。R03/R01打印3.51另列，当前结果没有暗中缩放到3.51。

### 本章参考文献与核验范围

- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R13] BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

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
| M | 12.3180386109 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| SigmaPP | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| SigmaP | 0.000636917224406 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| PhiPP | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| PhiPT | 0 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
| Delta | 0.00118516033688 | 共享SM振幅逐通道输出，再用相同源与探测器折叠 |
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

**本章是探测器读出，与第4章原子核Response是两步。** 继续使用R17官方早期YBe重铸基底与中位产额；已有探测器数值不因换核结构而重提取。

<a id="eq-response"></a>

$$
P_{ri}(T)=\sum_{j,k,l}\mathcal B_r(T,L_y(T),Q_y(T);i,j,k,l),\qquad0\leq\sum_iP_{ri}(T)\leq1 \tag{3}
$$

公式依据：项目对R17原HDF5接受后四维箱概率的精确边际化；原单能模板与utils.py::Template.interpolator。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $r,i$ | SR0/SR1与各run自身的cS2箱序号；三箱 | 1 | R17原HDF5 /bins/0；第6章完整边界 |
| $\mathcal B_r$ | 已取得；原基底每run16×10×10×3×3×3×3 | 1，接受后箱概率 | R17 orthonormal_basis；原文件1600个/run |
| $T,L_y,Q_y$ | T核反冲；Ly/Qy是物理产额坐标，分别1…10 | keVnr；photon/keVnr；electron/keVnr | 正式response_energy_keV/response_Ly/response_Qy与501点YBe中位数 |
| $j,k,l$ | shadow、S1BDT、S2BDT三个观测轴各三箱 | 1 | R17原/bin轴；求和后保留cS2边际 |
| $P_{ri}$ | 已取得的数值核，经插值推导；Runtime形状16×10×10×3/run | 1 | SM20261107数组claims；solar_b8.XenonBasisObservation |

<a id="eq-interpolation"></a>

$$
\mathcal B_r(T,L,Q)=\sum_{a,b,c\in\{0,1\}}w_a^E(T)w_b^L(L)w_c^Q(Q)\,\mathcal B_{r,e+a,\ell+b,q+c} \tag{4}
$$

公式依据：R17 utils.py::Template.interpolator的三线性内插；当前实现为RegularGridInterpolator(method=linear)，不是任意平滑。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $e,\ell,q$ | 包含输入坐标的相邻网格单元索引 | 1 | 显式16×10×10的物理坐标网格 |
| $w_0,w_1$ | 项目线性权重：(x_high−x)/Δx与(x−x_low)/Δx；和为1 | 1 | 同一网格单元的三轴权重乘积 |
| $L(T),Q(T)$ | 已取得；原YBe median JSON map在T上线性插值 | photon/keVnr、electron/keVnr | R17 ly_ybe_model_median.json/qy_ybe_model_median.json |

原YBe表的**存储域0.3–10keV**不等于已认证响应域。当前只在单能基底 **0.51–5keVnr** 内使用；T域外本重铸模型返回零，不外推；Ly/Qy超网格时拒绝，不裁剪成端点。已有模板包含选择，不再乘另一条接受度曲线。原模型对九种Xe同位素共用；本轮对已覆盖的七种同位素共用这一真实反冲NR响应，核素差异在核数/质量/共享截面中进入；这是实际组件的采用约定，不是额外同位素标定。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `response_energy_keV` | 16; dtype=float64; 范围 [0.51, 5]; 首/中/末 [0.51, 1.75, 5] | keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Ly` | 10; dtype=float64; 范围 [1, 10]; 首/中/末 [1, 6, 10] | photon/keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Qy` | 10; dtype=float64; 范围 [1, 10]; 首/中/末 [1, 6, 10] | electron/keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR0` | 16×10×10×3; dtype=float64; 范围 [2.7e-09, 0.134859163244]; 首/中/末 [5.5073198944e-08, 3.63508902598e-05, 0.00171576203184] | 1 | R17；SR0原始1600个单能模板，对shadow/S1BDT/S2BDT求和；含全部原模板选取，不额外乘接受度；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR1` | 16×10×10×3; dtype=float64; 范围 [2.7e-09, 0.134927461973]; 首/中/末 [2.92771698041e-08, 2.54910647518e-05, 0.00121735674367] | 1 | R17；SR1原始1600个单能模板，对shadow/S1BDT/S2BDT求和；含全部原模板选取，不额外乘接受度；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_energy_keV` | 501; dtype=float64; 范围 [0.3, 10]; 首/中/末 [0.3, 1.73205080757, 10] | keVnr | R17；官方YBe median JSON coordinate_system，501节点；仅在响应0.51–5keV域使用；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Ly_median` | 501; dtype=float64; 范围 [4.96483304998, 5.84943426556]; 首/中/末 [4.96948391067, 4.97702186212, 5.84943426556] | photon/keVnr | R17；data/signal/ly_ybe_model_median.json 原始map；非旧WIMP Qy；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Qy_median` | 501; dtype=float64; 范围 [2.74488347604, 6.42315153388]; 首/中/末 [2.74488347604, 6.42026853025, 5.21471791433] | electron/keVnr | R17；data/signal/qy_ybe_model_median.json 原始map；非旧WIMP Qy；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |

轴顺序：正式响应为(T,Ly,Qy,cS2箱)。原始7维基底为(T,Ly,Qy,cS2,shadow,S1BDT,S2BDT)。**Ly/Qy=1…10是物理产额，不能误当作±3 nuisance坐标。**背景文件的tLy/tQy七点坐标是另一种约定，见第8章。

| run | T[keVnr] | 三箱P（代表值） | ΣP | 来源/性质 |
|---|---|---|---|---|
| SR0 | 0.51 | [0.000250822205457, 6.73116676691e-05, 1.85242618582e-06] | 0.000319986299312 | R17原基底+YBe中位数；项目插值值 |
| SR0 | 1 | [0.00554983107397, 0.00445078372935, 0.000717062223603] | 0.0107176770269 | R17原基底+YBe中位数；项目插值值 |
| SR0 | 2 | [0.014382442902, 0.0358614994927, 0.0331001575679] | 0.0833440999626 | R17原基底+YBe中位数；项目插值值 |
| SR0 | 3 | [0.00678255508435, 0.0336521369328, 0.105760898709] | 0.146195590726 | R17原基底+YBe中位数；项目插值值 |
| SR1 | 0.51 | [0.000177950308868, 8.24732257891e-05, 2.61244062793e-06] | 0.000263035975285 | R17原基底+YBe中位数；项目插值值 |
| SR1 | 1 | [0.00360415749116, 0.00479188848612, 0.000919330392619] | 0.00931537636989 | R17原基底+YBe中位数；项目插值值 |
| SR1 | 2 | [0.00730870609176, 0.0296432030029, 0.0361044644005] | 0.0730563734952 | R17原基底+YBe中位数；项目插值值 |
| SR1 | 3 | [0.00270167687038, 0.0220718382697, 0.104573261227] | 0.129346776367 | R17原基底+YBe中位数；项目插值值 |

### 已取得但未另行施加的标定与接受度


[完整原文摘录文件：xenonnt_2024_calibration_inputs.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_calibration_inputs.v2.1.json>)

| 参考参数 | 值 | 误差/变化 | 单位 | 直接出处 |
|---|---|---|---|---|
| g1_SR0 | 0.151 | ±0.001 | PE/photon | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| g2_SR0 | 16.5 | ±0.6 | PE/electron | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| fiducial_mass_SR0 | 3.97 | ±0.2 | t | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| livetime_SR0 | 108 | 未单列 | day | R03；2408.02877v1 PDF p2, Dataset and detector calibration text |
| g1_SR1 | 0.137 | ±0.001 | PE/photon | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| g2_SR1 | 16.9 | ±0.5 | PE/electron | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| fiducial_mass_SR1 | 4.1 | ±0.19 | t | R03；2408.02877v1 PDF p3, Dataset and detector calibration text |
| livetime_SR1 | 208.5 | 未单列 | day | R03；2408.02877v1 PDF p2, Dataset and detector calibration text |
| combined_exposure | 3.51 | 未单列 | t yr | R03；2408.02877v1 PDF p3, fiducial-volume paragraph |

R01 PDF p6式(14)使用g₂=16.9PE/electron与R07早期WIMP Qy作均值换算；它不是当前YBe模板的外乘参数。已提取的R07曲线保留原可见/原虚线外推标志；不能改称YBe专用Qy。当前模板已经包含读出与选择效应。

| 实际数值文件 | shape/范围 | 单位 | 直接原文定位 | 采用/验证范围 |
|---|---|---|---|---|
| [xenonnt_qy_sr0_23Vcm.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_23Vcm.txt>) | [99, 4]; 各列范围 [0.4999999979, 100]; [1.991116633, 7.452982227]; [0, 1]; [0, 1] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; deep red SR0 23 V/cm | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_qy_sr0_band.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_band.txt>) | [100, 3]; 各列范围 [0.4999999979, 100]; [1.883201701, 7.205418402]; [2.116291405, 7.770667665] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; same figure; deep red model band | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_2024_fig1_acceptance.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>) | [40, 8]; 各列范围 [0.429999996183, 2.77000000181]; [0.0180363902791, 0.255562907963]; [0.00527964624015, 0.478743981244]; [0.000111966577589, 0.123987528765]; [0, 1]; [0, 1]; [0, 1]; [0, 1] | All efficiencies and flags dimensionless. Energy keVnr. Total acceptance is already the black combined path. | R03；2408.02877v1 PDF p4 Fig.1 upper: light-blue S1, dark-blue S2, black combined acceptance | 原2024边际接受度对照；当前响应含选择，不再相乘 |
| [xenonnt_2024_fig1_sm_recoil_spectra.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_2024_fig1_sm_recoil_spectra.txt>) | [40, 6]; 各列范围 [0.429999996183, 2.77000000181]; [1.0677678874, 1091.71726397]; [0.022177392585, 2.76844400232]; [0, 1]; [0, 1]; [0, 1] | Rates events/(t yr keVnr). Flags dimensionless. With-acceptance rate already includes acceptance. | R03；2408.02877v1 PDF p4 Fig.1 lower: light-pink without acceptance and dark-red with acceptance SM curves | 原2024真实反冲SM参考谱；验证用途 |

六份YBe lower/median/upper文件都已保存；当前采用median，上下曲线没有被自动解释为独立高斯或完整联合协方差。R08的2026新版响应另存候选，不与本轮R17基底混用。

### 本章参考文献与核验范围

- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R12] APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26；文献 [1] 的背景关联来源 [72]。 [本地直接采用源](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R07] APRILE E, et al. (XENON Collaboration). XENONnT WIMP search: Signal and background modeling and statistical inference[J]. Physical Review D, 2025, 111: 103040. DOI: [10.1103/PhysRevD.111.103040](https://doi.org/10.1103/PhysRevD.111.103040). 实际提取 [arXiv:2406.13638v1](https://arxiv.org/abs/2406.13638v1), 2024-06-19，第 6 页 Fig.3 右下图；期刊版为后续版本，不替换本次所用曲线。 [本地直接采用源](<../../../../references/Solar_CEvNS/2406.13638v1.pdf>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R08] XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- [R14] APRILE E, et al. (XENON Collaboration). Probing the Solar ⁸B Neutrino Fog with XENONnT[J]. Physical Review Letters, 2026, 137: 091807. DOI: [10.1103/xvpn-w3q9](https://doi.org/10.1103/xvpn-w3q9). 本库保存 [arXiv:2604.06002v2](https://arxiv.org/abs/2604.06002v2), 2026-08-28。文献 [8] README 指定它为后续数据与模板的关联论文；本任务只提取 SR0/SR1 候选，不纳入 SR2。 [本地直接采用源](<../../../../references/Solar_CEvNS/2604.06002v2.pdf>)

**c_i的地位：** R01式(12)的c_i是作者简化分析的有效修正，原Response路线不引入。PandaX直接预测固定SSM通量且c=1；历史字段effective_calibration只保存后验拟合谱缩放比值，不代表独立的探测器校准或SSM预测。作者原始c_i仍未获得，严格论文等价性未认证。


[返回目录](#report-toc)

<a id="observable"></a>

## 6. Observable、完整分箱与观测身份

| run | 原生cS2完整箱界[PE] | 逐箱D | 直接出处 |
|---|---|---|---|
| SR0 | [90, 170.161773682, 249.88973999, 500] | [5, 3, 1] | R08原事件CSV与binning；R17原HDF5相同分箱核对 |
| SR1 | [90, 155.937850952, 232.292022705, 500] | [11, 11, 6] | R08原事件CSV与binning；R17原HDF5相同分箱核对 |

合计输出坐标是项目定义的箱序号1、2、3，`observable_edges=[0, 1, 2, 3]`，单位1；**各run按自身箱序号相加，不将所有事件放入一套公共PE箱界**。D合计[16,14,7]、总37；原37事件完整值保留。

R01正文写[120,500]PE，而其Fig.1绘图约[90,155,235,500]PE；官方SR1事件中有cS2=118.58632PE。当前采用上表官方原生90起点，未加cS2≥120筛选，也不声称已经解决作者120阈值与原37事件的关系。这个冲突只限制严格R01图/拟合复现。

| 实际数值文件 | shape/范围 | 单位 | 直接原文定位 | 采用/验证范围 |
|---|---|---|---|---|
| [xenonnt_official_observed_bins.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt>) | [6, 5]; 各列范围 [0, 1]; [1, 3]; [90, 249.88974]; [155.937851, 500]; [1, 11] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv; binning/sr0.yaml,sr1.yaml | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |
| [xenonnt_official_observed_events.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_events.txt>) | [37, 3]; 各列范围 [0, 1]; [0, 27]; [118.58632, 494.5456] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |

### 本章参考文献与核验范围

- [R08] XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)


[返回目录](#report-toc)

<a id="prediction"></a>

## 7. Prediction folding、执行结果与复算

**本版结果由真实核表独立计算。蓝色论文参考线由图中提取，始终不作为本项目Response预测。**

| 阶段 | 实际代码/输入 | 物理工作与出处 |
|---|---|---|
| P01–P03 | load_experiment_package | 读原YAML/NPZ：R04源谱、R09核数、R01参数、实验曝光 |
| P04 | with_solar_nuclear_response → SolarNuclearSM | 显式绑定R16七核素；R20匹配与粒子/核响应收缩 |
| P05 | SolarNuclearSM.dsigma_dT | 同A·amu、精确支撑、m/(8πE²)和cm²/keV转换 |
| P06 | SolarExecutor / XenonBasisObservation | R17单能基底插值和每run原生PE箱 |
| P07 | predict_experiment → integrate_recoil_yield | 逐核素卷积源谱，再乘核数/曝光与选区折叠；每因子一次 |
| P10 | run_solar_b8_nuclear_benchmark.py | T与Eν分别加密；逐核素/通道/运行期闭合，保留KN公平对照 |

### 实际逐箱信号 [events/bin]

| 箱 | 核表SM | 其中M | 同范围KN | 核表/KN−1 |
|---|---|---|---|---|
| 1 | 3.51546498451 | 3.51505601058 | 3.50094057916 | +0.414872% |
| 2 | 5.65087950106 | 5.65008149901 | 5.62367438369 | +0.483761% |
| 3 | 3.15351620293 | 3.15290110135 | 3.13465694591 | +0.601637% |

合计：**核表SM 12.319860689**；同范围KN 12.259271909事例。比较同时改变完整SM核通道与核结构；M-only列可单独查看相干主项。

| run | 实际信号数组 |
|---|---|
| SR0 | [1.58362627718, 1.94419157865, 0.968211946238] |
| SR1 | [1.93183870733, 3.7066879224, 2.1853042567] |

[结果、独立收敛与全部输入参数](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/RESULT.json>) · [完整各核素/通道数组](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/prediction.npz>) · [实际Runtime装配与全部资源哈希](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/PREPARED_MODEL.nuclear.json>)

![核表Response SM与同范围KN](<../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/events.png>)

绿实线=本版真实核表SM；橙虚线=同七核素KN直接计算；灰线=背景参考；黑点=观测及68.27% Garwood Poisson误差棒。PandaX蓝点线=论文作者S+B数字化参考。没有紫色校准线。

**历史比较边界。** 旧九核素/旧裸核质量KN结果和旧V/B−L点只在[历史v3.0](<experiment.physics.v3.0.md>)中保留。R01 Fig.1只作为文献参考，R01 Fig.2/4仍不是本次统计计算。

当前SM主入口`tools/run_solar_b8_sm_benchmark.py`默认转到本核表路线；只有显式`--legacy-kn`才运行历史KN。原包的KN装配仍可单独加载，不能把它与本版显式核表覆盖混用。

[返回目录](#report-toc)

<a id="statistics"></a>

## 8. Statistics、观测与背景的来源和适用范围

**本轮不作拟合。** 信号前向积分不读取D/B；它们只进入比较图。

**已执行的是固定点前向预测与观测/名义背景作图；统计evaluator、χ²最小化、置信区间未实现/未运行。** 下列R01统计合同作为后续明确依据保留，不因公式写出就声称统计能力已完成。

<a id="eq-mean-counts"></a>

$$
\mu_i=(1+\alpha)(1+\beta_s)S_i(\theta)+\sum_k(1+\beta_k)B_i^k \tag{5}
$$

公式依据：项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $D_i$ | 观测计数已有；原始身份/当前范围见下表 | events/bin | 不是背景扣除残差 |
| $S_i$ | XENONnT当前SM/V/B−L三箱可计算 | events/bin | 第7章相应能力 |
| $B_i^k$ | 当前R17名义背景已有，精确原2024配套性待核 | events/bin | 下表严格区分来源版本与用途 |
| $\alpha,\beta_s,\beta_k$ | 定义的统计归一化nuisance；本轮未profile | 1 | R01 PDF p6式(17)后；σ按单独模型表采用 |

<a id="eq-deviance"></a>

$$
\chi^2_{\rm prof}=\min_{\alpha,\boldsymbol\beta}\left[2\sum_i\left(\mu_i-D_i+D_i\ln\frac{D_i}{\mu_i}\right)+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\sum_k\left(\frac{\beta_k}{\sigma_k}\right)^2\right] \tag{6}
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
| signal FV | 0.05 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |
| AC | 0.048 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |
| neutron | 0.5 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |
| ER | 1 | R01 PDF p6式(17)后；后续统计参考，本轮未profile |

### 当前绘图的直接名义背景与观测

| 箱序号 | D | AC | neutron | ER | B合计 | SM+B |
|---|---|---|---|---|---|---|
| 1 | 16 | 8.416187322 | 0.069986037 | 0.010500863 | 8.496674222 | 12.010705140 |
| 2 | 14 | 8.416277632 | 0.120465065 | 0.055522764 | 8.592265462 | 14.241374035 |
| 3 | 7 | 8.416277632 | 0.276484079 | 0.613457152 | 9.306218864 | 12.460312596 |

B合计26.395158547，SM+B合计38.712391771，观测37。R17 AC/ER原数组为3⁴；neutron为7×7×3⁴，取tLy=tQy=0（索引3,3），对其余观测轴求和并乘相应run曝光。**R17的b8模板只作信号对照，没有作为额外背景加到本项目SM上。**

| 实际数值文件 | shape/范围 | 单位 | 直接原文定位 | 采用/验证范围 |
|---|---|---|---|---|
| [xenonnt_original_fig2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_original_fig2.txt>) | [3, 6]; 各列范围 [1, 3]; [7, 16]; [8.4182867, 8.418375626]; [0.0701057518, 0.2627899614]; [0.008421507254, 0.4919749226]; [2.606485679, 4.96995278] | D/background/reference signal events/bin, coordinate columns as declared | R03；2408.02877v1 PDF p6 Fig.2 upper | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_benchmark_fig1.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt>) | [3, 8]; 各列范围 [1, 3]; [90.00000017, 234.9999994]; [154.9999995, 500]; [7, 16]; [8.433333333, 8.433333333]; [0.1130267707, 0.2394635342]; [0.06729647667, 0.5126921747]; [2.699105414, 4.906604663] | D/background/reference signal events/bin, coordinate columns as declared | R01；2411.11749v1 PDF p7 Fig.1 right | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_sr0_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) |  记录；完整数组/标量见文件 | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr0_*; statistical_model_base.yaml in_events_per_bin | 早期发布名义背景/信号对照；B8不是额外背景 |
| [xenonnt_sr1_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>) |  记录；完整数组/标量见文件 | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr1_*; statistical_model_base.yaml in_events_per_bin | 早期发布名义背景/信号对照；B8不是额外背景 |

原图postfit与benchmark参考背景完整三箱如下，均为数字化参考，未取代上表R17直接名义模板：

**R03 PDF p6 Fig.2**：

| 箱 | D | AC | neutron | ER | 参考信号 |
|---|---|---|---|---|---|
| 1 | 16 | 8.4182867 | 0.0701057518 | 0.008421507254 | 3.135579713 |
| 2 | 14 | 8.418375626 | 0.1184531965 | 0.0445274149 | 4.96995278 |
| 3 | 7 | 8.418375626 | 0.2627899614 | 0.4919749226 | 2.606485679 |

**R01 PDF p7 Fig.1**：

| 箱 | D | AC | neutron | ER | 参考信号 |
|---|---|---|---|---|---|
| 1 | 16 | 8.433333333 | 0.1130267707 | 0.06729647667 | 3.094289923 |
| 2 | 14 | 8.433333333 | 0.1475095449 | 0.1200114238 | 4.906604663 |
| 3 | 7 | 8.433333333 | 0.2394635342 | 0.5126921747 | 2.699105414 |


### 原2024实验印刷的prefit与率约束（独立参考）

[完整原文摘录文件：xenonnt_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_prefit_inputs_2024.v2.1.json>)

| 参考参数 | 值 | 误差/变化 | 单位 | 直接出处 |
|---|---|---|---|---|
| AC_SR0_prefit | 7.5 | ±0.7 | events | R03；PDF p5 Table I expectation, AC(SR0) |
| AC_SR1_prefit | 17.8 | ±1 | events | R03；PDF p5 Table I expectation, AC(SR1) |
| ER_combined_prefit | 0.7 | ±0.7 | events | R03；PDF p5 Table I expectation, ER |
| neutron_combined_prefit | 0.5 | −0.3/+0.2 | events | R03；PDF p5 Table I expectation, Neutron |
| total_background_prefit | 26.4 | −1.3/+1.4 | events | R03；PDF p5 Table I expectation, Total background |
| signal_reference | 11.9 | −4.2/+4.5 | events | R03；PDF p5 Table I expectation, 8B |
| AC_SR0_relative_rate_uncertainty | 0.09 | 未单列 | 1 | R03；PDF p5 AC model paragraph |
| AC_SR1_relative_rate_uncertainty | 0.058 | 未单列 | 1 | R03；PDF p5 AC model paragraph |
| neutron_relative_rate_uncertainty | 0.58 | 未单列 | 1 | R03；PDF p5 neutron paragraph |
| ER_relative_rate_uncertainty | 1 | 未单列 | 1 | R03；PDF p5 ER paragraph |
| signal_total_acceptance_relative_uncertainty | 0.1 | 未单列 | 1 | R03；PDF p5 first column, S2 acceptance paragraph |
| neutron_SR0_prefit | 0.13 | ±0.07 | events | R03；2408.02877v1 PDF p5 neutron paragraph |
| neutron_SR1_prefit | 0.33 | ±0.19 | events | R03；2408.02877v1 PDF p5 neutron paragraph |
| ER_SR0_prefit | 0.13 | ±0.13 | events | R03；2408.02877v1 PDF p5 ER paragraph |
| ER_SR1_prefit | 0.56 | ±0.56 | events | R03；2408.02877v1 PDF p5 ER paragraph |

原实验声明AC率按run独立，其余参数联合约束（R03 PDF p6）。完整tLy/tQy约束函数/相关性与2024版本配套仍待核；不能把R17 light-WIMP分析中受约束的8B背景nuisance直接用于本任务自由信号拟合。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R08] XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- [R12] APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26；文献 [1] 的背景关联来源 [72]。 [本地直接采用源](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

Fig.2的通量扫描如何重参数化12% flux pull，以及Fig.4的90% CL构造/自由度/阈值，目前都未通过本项目统计实现认证。本轮没有选择单位协方差、擅补独立高斯或把χ²公式存在当作已有扫描结果。


[返回目录](#report-toc)

<a id="resources"></a>

## 9. 全部数值资源、轴与逐项来源

YAML/NPZ保持原包字节；当前执行权威是“原包＋显式核表覆盖”（PandaX另加Qy），不能只打开原包就认为默认已经更换。实际路径和哈希如下。

| 资源ID | 完整本地数值文件 | SHA256 | 本轮用途/直接定位 |
|---|---|---|---|
| package_input | [experiment.input.yaml](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) | 271e18b89398ed90c29db2f88924a10514125328a7c27f69de49baa33c1111c4 |  |
| package_arrays | [experiment.resources.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) | 39aa001f5c5657ddbb0099f232ee7e2a81f78ff383da3cf43b0dc214b62fdeb2 |  |
| nuclear_response | [responses_all.json](<../../../../../data/responses/responses_all.json>) | cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74 | existing np nuclear polynomial table; external source unresolved |

### 原包正式数组全部清单

原包observable_edges与KN配置为保留的历史元数据；当前观测边界与核模型以上述实际装配为准。

| 数组键 | shape/范围/代表值 | 单位 | 直接出处、转换与采用范围 | 本地文件 |
|---|---|---|---|---|
| `cs2_edges_SR0` | 4; dtype=float64; 范围 [90, 500]; 首/中/末 [90, 249.88973999, 500] | PE | R17；SR0原HDF5 /bins/0，原样保留；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `cs2_edges_SR1` | 4; dtype=float64; 范围 [90, 500]; 首/中/末 [90, 232.292022705, 500] | PE | R17；SR1原HDF5 /bins/0，原样保留；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `observable_edges` | 4; dtype=float64; 范围 [0, 3]; 首/中/末 [0, 2, 3] | 1 | USER；本轮显式输出坐标：按SR0/SR1各自三箱序号相加，不伪造统一PE边界；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Ly` | 10; dtype=float64; 范围 [1, 10]; 首/中/末 [1, 6, 10] | photon/keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Qy` | 10; dtype=float64; 范围 [1, 10]; 首/中/末 [1, 6, 10] | electron/keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR0` | 16×10×10×3; dtype=float64; 范围 [2.7e-09, 0.134859163244]; 首/中/末 [5.5073198944e-08, 3.63508902598e-05, 0.00171576203184] | 1 | R17；SR0原始1600个单能模板，对shadow/S1BDT/S2BDT求和；含全部原模板选取，不额外乘接受度；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR1` | 16×10×10×3; dtype=float64; 范围 [2.7e-09, 0.134927461973]; 首/中/末 [2.92771698041e-08, 2.54910647518e-05, 0.00121735674367] | 1 | R17；SR1原始1600个单能模板，对shadow/S1BDT/S2BDT求和；含全部原模板选取，不额外乘接受度；PROJECT_DERIVED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_energy_keV` | 16; dtype=float64; 范围 [0.51, 5]; 首/中/末 [0.51, 1.75, 5] | keVnr | R17；官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `run_exposures_tyr` | 2; dtype=float64; 范围 [1.174398, 2.342593]; 首/中/末 [1.174398, 2.342593, 2.342593] | t yr | R17；官方statistical_model_base.yaml livetime_sr0/1；每t yr模板的曝光乘数。合计3.516991，与论文打印3.51分别报告；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `source_energy_MeV` | 829; dtype=float64; 范围 [0, 16.56]; 首/中/末 [0, 8.28, 16.56] | MeV | R04；Bahcall官网b8spectrum.txt全部829行第一列；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `source_shape_per_MeV` | 829; dtype=float64; 范围 [0, 0.1321716]; 首/中/末 [0, 0.1154396, 0] | MeV^-1 | R04；同表第二列中心归一化谱；不重归一化，不含总通量/效率；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_atomic_mass_u` | 9; dtype=float64; 范围 [123.905892, 135.907214484]; 首/中/末 [123.905892, 129.903509349, 135.907214484] | u | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_mass_number` | 9; dtype=float64; 范围 [124, 136]; 首/中/末 [124, 130, 136] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_number_fraction` | 9; dtype=float64; 范围 [0.00089, 0.269086]; 首/中/末 [0.000952, 0.04071, 0.088573] | 1 | R09；NIST天然Xe表全部九行，对应A/原子质量/数丰度；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Ly_median` | 501; dtype=float64; 范围 [4.96483304998, 5.84943426556]; 首/中/末 [4.96948391067, 4.97702186212, 5.84943426556] | photon/keVnr | R17；data/signal/ly_ybe_model_median.json 原始map；非旧WIMP Qy；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Qy_median` | 501; dtype=float64; 范围 [2.74488347604, 6.42315153388]; 首/中/末 [2.74488347604, 6.42026853025, 5.21471791433] | electron/keVnr | R17；data/signal/qy_ybe_model_median.json 原始map；非旧WIMP Qy；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_energy_keV` | 501; dtype=float64; 范围 [0.3, 10]; 首/中/末 [0.3, 1.73205080757, 10] | keVnr | R17；官方YBe median JSON coordinate_system，501节点；仅在响应0.51–5keV域使用；SOURCE_EXTRACTED | [完整数值](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |

### 辅助表与其出处

| 数值文件 | shape/范围 | 单位 | 直接来源、定位与转换 | 本版用途 |
|---|---|---|---|---|
| [xenonnt_qy_sr0_23Vcm.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_23Vcm.txt>) | [99, 4]，各列范围：[0.4999999979, 100]; [1.991116633, 7.452982227]; [0, 1]; [0, 1] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; deep red SR0 23 V/cm；PDF vectors; clipped nodes and original extrapolation flags retained | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_qy_sr0_band.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_band.txt>) | [100, 3]，各列范围：[0.4999999979, 100]; [1.883201701, 7.205418402]; [2.116291405, 7.770667665] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; same figure; deep red model band；original band; no nuisance covariance inferred | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_original_fig2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_original_fig2.txt>) | [3, 6]，各列范围：[1, 3]; [7, 16]; [8.4182867, 8.418375626]; [0.0701057518, 0.2627899614]; [0.008421507254, 0.4919749226]; [2.606485679, 4.96995278] | D/background/reference signal events/bin, coordinate columns as declared | R03；2408.02877v1 PDF p6 Fig.2 upper；fitted components; run bin edges are in the separate official bin table | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_benchmark_fig1.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt>) | [3, 8]，各列范围：[1, 3]; [90.00000017, 234.9999994]; [154.9999995, 500]; [7, 16]; [8.433333333, 8.433333333]; [0.1130267707, 0.2394635342]; [0.06729647667, 0.5126921747]; [2.699105414, 4.906604663] | D/background/reference signal events/bin, coordinate columns as declared | R01；2411.11749v1 PDF p7 Fig.1 right；plot coordinates are not certified likelihood edges; reference B | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_official_observed_bins.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt>) | [6, 5]，各列范围：[0, 1]; [1, 3]; [90, 249.88974]; [155.937851, 500]; [1, 11] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv; binning/sr0.yaml,sr1.yaml；direct official histogram; no cuts | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |
| [xenonnt_official_observed_events.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_events.txt>) | [37, 3]，各列范围：[0, 1]; [0, 27]; [118.58632, 494.5456] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv；direct event values; original row order retained | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |
| [b8_bahcall1996_official.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>) | [829, 4]，各列范围：[0, 16.56]; [0, 0.1321716]; [0, 0.1339827]; [0, 0.1304072] | MeV; MeV^-1 | R04；official b8spectrum.txt, all four columns；byte-identical download | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenon_natural_isotopes_nist_v2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt>) | [9, 3]，各列范围：[124, 136]; [123.905892, 135.907214484]; [0.00089, 0.269086] | 1; u; 1 | R09；Xe rows 124,126,128,129,130,131,132,134,136；parsed central values; uncertainties retained in official source download, not treated as zero | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr0_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>) | energy_keVnr:[46]; tLy:[7]; tQy:[7]; probability:[7, 7, 46, 3, 3, 3, 3]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | 1, keVnr; nuisance coordinate dimensionless | R08；templates/sr0/mono/*; /templates/template and /bins/*；lossless direct HDF5 array stacking; no interpolation or normalization | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr0_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>) | tLy:[7]; tQy:[7]; AC:[3, 3, 3, 3]; ER:[3, 3, 3, 3]; neutron:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/(t yr bin) | R08；templates/sr0/ac,er,rg/*; /templates/template；lossless HDF5 array stacking | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr0_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_observed_4d_v2.npz>) | observed:[3, 3, 3, 3]; events:[9, 4]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/bin; PE and dimensionless classifiers | R08；data/sr0.csv; binning/sr0.yaml；histogramdd without cuts; exact event values | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>) | energy_keVnr:[46]; tLy:[7]; tQy:[7]; probability:[7, 7, 46, 3, 3, 3, 3]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | 1, keVnr; nuisance coordinate dimensionless | R08；templates/sr1/mono/*; /templates/template and /bins/*；lossless direct HDF5 array stacking; no interpolation or normalization | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>) | tLy:[7]; tQy:[7]; AC:[3, 3, 3, 3]; ER:[3, 3, 3, 3]; neutron:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/(t yr bin) | R08；templates/sr1/ac,er,rg/*; /templates/template；lossless HDF5 array stacking | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_observed_4d_v2.npz>) | observed:[3, 3, 3, 3]; events:[28, 4]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/bin; PE and dimensionless classifiers | R08；data/sr1.csv; binning/sr1.yaml；histogramdd without cuts; exact event values | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_2024_calibration_inputs.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_calibration_inputs.v2.1.json>) | 9条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R03；2408.02877v1 PDF p2-p3, Dataset and gain/FV paragraphs；transcribed printed primary-source values | 原2024标定/prefit总数/约束参考；完整likelihood未实例化 |
| [xenonnt_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_prefit_inputs_2024.v2.1.json>) | 15条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R03；2408.02877v1 PDF p5 Table I and background text, p6 statistical inference；transcribed printed primary-source values | 原2024标定/prefit总数/约束参考；完整likelihood未实例化 |
| [xenonnt_2024_fig1_acceptance.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>) | [40, 8]，各列范围：[0.429999996183, 2.77000000181]; [0.0180363902791, 0.255562907963]; [0.00527964624015, 0.478743981244]; [0.000111966577589, 0.123987528765]; [0, 1]; [0, 1]; [0, 1]; [0, 1] | All efficiencies and flags dimensionless. Energy keVnr. Total acceptance is already the black combined path. | R03；2408.02877v1 PDF p4 Fig.1 upper: light-blue S1, dark-blue S2, black combined acceptance；Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation | 原2024边际接受度对照；当前响应含选择，不再相乘 |
| [xenonnt_2024_fig1_sm_recoil_spectra.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_2024_fig1_sm_recoil_spectra.txt>) | [40, 6]，各列范围：[0.429999996183, 2.77000000181]; [1.0677678874, 1091.71726397]; [0.022177392585, 2.76844400232]; [0, 1]; [0, 1]; [0, 1] | Rates events/(t yr keVnr). Flags dimensionless. With-acceptance rate already includes acceptance. | R03；2408.02877v1 PDF p4 Fig.1 lower: light-pink without acceptance and dark-red with acceptance SM curves；Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation | 原2024真实反冲SM参考谱；验证用途 |
| [ly_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_lower.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [ly_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_median.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | 本轮前向输入的直接来源，已封入正式NPZ |
| [ly_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_upper.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [qy_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_lower.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [qy_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_median.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | 本轮前向输入的直接来源，已封入正式NPZ |
| [qy_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_upper.json>) | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [xenonnt_early_release_cevns_spectrum.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_early_release_cevns_spectrum.json>) | coordinate_system:[501]; map:[501]; rate:[] | map/coordinate_system according to coordinate_name; recoil keV, rate events/(t yr) | R17；data/signal/cevns_spectrum.json; utils.py::Template.required_keys and format_custom_signal_spectrum；byte-identical copy from pinned official archive | 官方已折叠CEvNS参考谱/CDF；不是中微子源谱 |
| [xenonnt_sr0_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_basis.npz>) | probability_basis:[16, 10, 10, 3, 3, 3, 3]; energy_keVnr:[16]; Ly_photon_per_keV:[10]; Qy_electron_per_keV:[10]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4]; axis_names:[7] | probability dimensionless; energy keVnr, Ly photon/keVnr, Qy electron/keVnr, cS2 PE | R17；data/orthonormal_basis/SR0 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr0_response_early_release_nominal_1d.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_nominal_1d.txt>) | [46, 4]，各列范围：[0.51, 5]; [0.000250822205457, 0.014421499093]; [6.73116676691e-05, 0.0400981009634]; [1.85242618582e-06, 0.127593835924] | keVnr; probabilities dimensionless | R17；utils.py::Template.interpolator/default_yield_model; original 1600 SR0 HDF5 plus ly/qy median JSON；Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency | 项目推导的一维名义响应对照；Runtime直接插值基底 |
| [xenonnt_sr0_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) | tLy:[7]; tQy:[7]; ac_rate_per_tyr_bin:[3, 3, 3, 3]; er_rate_per_tyr_bin:[3, 3, 3, 3]; b8_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; rg_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr0_*; statistical_model_base.yaml in_events_per_bin；lossless original HDF5 template stacking, no exposure applied or rescaling | 早期发布名义背景/信号对照；B8不是额外背景 |
| [xenonnt_sr1_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_basis.npz>) | probability_basis:[16, 10, 10, 3, 3, 3, 3]; energy_keVnr:[16]; Ly_photon_per_keV:[10]; Qy_electron_per_keV:[10]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4]; axis_names:[7] | probability dimensionless; energy keVnr, Ly photon/keVnr, Qy electron/keVnr, cS2 PE | R17；data/orthonormal_basis/SR1 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr1_response_early_release_nominal_1d.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_nominal_1d.txt>) | [46, 4]，各列范围：[0.51, 5]; [7.17318527876e-05, 0.00773730855365]; [8.24732257891e-05, 0.0296432030029]; [2.61244062793e-06, 0.120980106453] | keVnr; probabilities dimensionless | R17；utils.py::Template.interpolator/default_yield_model; original 1600 SR1 HDF5 plus ly/qy median JSON；Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency | 项目推导的一维名义响应对照；Runtime直接插值基底 |
| [xenonnt_sr1_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>) | tLy:[7]; tQy:[7]; ac_rate_per_tyr_bin:[3, 3, 3, 3]; er_rate_per_tyr_bin:[3, 3, 3, 3]; b8_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; rg_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr1_*; statistical_model_base.yaml in_events_per_bin；lossless original HDF5 template stacking, no exposure applied or rescaling | 早期发布名义背景/信号对照；B8不是额外背景 |

第4章的核表审计显示全部实际系数；外部作者来源未闭合是“来源认证待补”，与Xe124/Xe126“数值MISSING”分别记录。


[返回目录](#report-toc)

<a id="status"></a>

## 10. 缺失、交接、验证与完整参考文献

| 能力 | 状态 | 缺口/限制 |
|---|---|---|
| 本地核表SM事例数 | 已算；本地ResponseDB/Li2026约定 | 数值资源已具备；科学结果接受NOT_REVIEWED |
| 完整天然Xe九核素 | PARTIAL | MISSING：Xe124、Xe126核响应系数；未用KN/邻核补齐，七核素不重归一 |
| 核表外部作者/生成认证 | UNRESOLVED | R16原始作者发布、转换与外部绝对归一化；不阻断用户明确选择的本地复用 |
| 探测器读出 | R17早期YBe重铸基底 | 严格原2024模型版本等价性待核 |
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
