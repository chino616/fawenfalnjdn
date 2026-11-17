# XENONnT_2024_SolarB8 — onboarding v3.0 完整整合版

**2026-11-09。文档整合版；科学接受NOT_REVIEWED，能力限制按章保留。**

[详细版v3.0](<experiment.physics.v3.0.md>) · [精简版v3.0](<experiment.physics.summary.v3.0.md>) · [用户资料v3.0](<EXPERIMENT_USER_INPUT.v3.0.md>) · [两实验完整总文档](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml>) · [P02当前缺口](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P02_MISSING_AND_CONFLICTS.md>) · [P03配置](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P03_PHYSICS_CONTRACT.yaml>) · [机器标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) · [完整数组](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) · [V/B−L Benchmark卡](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>) · [文档整合验收](<../../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/README.md>)

<a id="report-toc"></a>

## 目录

- [1. 实验范围、身份与版本](#scope)
- [2. Source：总通量、谱形与味态](#source)
- [3. Target、核数与曝光](#target)
- [4. 实际共享模块与参数选择](#modules)
- [5. Detector Response、Qy与数值取得状态](#detector)
- [6. Observable、完整分箱与观测身份](#observable)
- [7. Prediction folding、执行结果与复算](#prediction)
- [8. Statistics、观测与背景的来源和适用范围](#statistics)
- [9. 全部数值资源、轴与逐项来源](#resources)
- [10. 缺失、交接、验证与完整参考文献](#status)
- [公式索引](#equation-index)
- [参数/数组索引](#parameter-index)

<a id="scope"></a>

## 1. 实验范围、身份与版本

**版本3.0，2026-11-09整合；2026-11-10新增PandaX SM简化分支。** 本版收齐已有来源、数据、完整Response合同、SM与V/B−L计算和剩余依赖；不需要拼接v2.0–v2.3。数值依据是实际文件与运行记录，旧版保持原位。

本轮已实现：SM与V/B−L三箱重建谱。使用官方早期YBe重铸响应，精确2024原生likelihood等价性仍待核。

| 对象/目标 | 采用范围 | 当前能力 |
|---|---|---|
| 数据身份 | XENONnT_2024_SolarB8 | 同一dataset；不新增采集期或默认全局激活 |
| 物理benchmark | R01 arXiv:2411.11749v1 SM；R19正式期刊V/B−L定义 | 固定点前向谱完成；本轮未计算Fig.2拟合或Fig.4排除线 |
| 方法 | Source→Target→共享截面→完整选后箱概率→counts；PandaX另有显式均值映射简化分支 | SSM通量固定；简化c=1是直接预测，后验拟合谱缩放只作参考 |
| 审核状态 | 文档整合完成；科学结果Human=NOT_REVIEWED | 机器PASS不代替科学接受；PARTIAL能力逐项列于第10章 |

机器输入权威为[正式YAML](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>)与[正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>)；当前人读说明为本版。旧Compiler派生MD保留，不把旧模板的“靶未绑定”等通用文字当作当前实际数组/执行状态。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)

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

物质数使用原子质量；运动学使用 `m_kin[GeV]=atomic_mass[u]×amu_GeV−54×m_e[GeV]`，忽略电子结合能。计算中的1000kg和31557600s是代数归一化锚点，不是虚构实测质量/活时间。现代SI下将u数值当g/mol是明确的摩尔质量常量近似，未称为精确恒等。

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

[返回目录](#report-toc)

<a id="modules"></a>

## 4. 实际共享模块与参数选择

| 选择维度 | 本轮实际组件/实现 | 参数、具体依据与边界 |
|---|---|---|
| Interaction：SM | `coherent_sm_kn_v1`；[StandardModelKN](<../../../../../cevns_pyeft/theory/sm_coherent.py>) | R01 PDF p3式(1)–(3)；含−T/E树级SM；拒绝一般BSM系数 |
| Interaction：V/B−L | `light_vector_kn_v1`；[LightVectorKN](<../../../../../cevns_pyeft/theory/light_vector.py>) | R19 PDF p5/印刷p4式(2.6),(2.10)；实数、味普适对角耦合，κ=1/−1/3 |
| Nuclear Structure | `klein_nystrand_v1`解析KN | R01式(3)与参数表；覆盖九核素；本轮不读取多项式核响应JSON |
| Kinematics | 现有ElasticKinematics | 精确弹性端点；与SM截面低反冲近似分开 |
| Cross-section | 上述共享组件的dsigma_dT | 输入Eν MeV、T keVnr、核质量GeV；输出cm²/keV；不夹带核数或效率 |
| Detector | `xenon_mono_basis_v1` | 探测器Response独立于Nuclear Structure；具体数学定义见第5章 |

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `interaction.sin2thetaW` | 0.23857 | 1 | R01；2411.11749v1 PDF p3 Eq.(2)后参考弱混合角 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `interaction.include_sm` | True | boolean | 项目配置选择；不是文献测量；本轮用户指定纯标准模型，不扫描BSM | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `nuclear.radius_fm` | 1.23 | fm | R01；2411.11749v1 PDF p3 Eq.(3)后：R_A=1.23 A^(1/3) fm | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `nuclear.skin_fm` | 0.7 | fm | R01；同上，a_k=0.7 fm | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.G_F` | 1.1663787e-05 | GeV^-2 | R18；foundation/constants.py::G_F | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.hbarc_GeV_fm` | 0.1973269804 | GeV fm | R18；foundation/constants.py::HBARC_GEV_FM | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `constants.GeV_inverse2_to_cm2` | 3.893793721e-28 | cm^2 GeV^2 | R18；foundation/constants.py::GEV_INV2_TO_CM2；微分截面另乘1e-6转成每keV | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |

V/B−L只通过现有interaction组件替换接口加入，正式SM包保持原样。耦合定义采用**期刊版C_V=3Ag²**；v1 PDF p4式(10)印成C_V²，期刊版式(2.10)已经明确。本版显式保留这个版本差别，没有用sqrt(3A)g误代，也未把旧v1 SM输入换成另一套实验模型。公共截面内部公式不在实验章节重写，原公式与独立解析检查见[共享矢量模型报告](<../../../../../outputs/solar_b8_vector/20261108_run1/REPORT.md#model>)。

未采用的Full EFT候选：本地responses_all.json含Xe128/129/130/131/132/134/136，缺Xe124/126；上游核系数出处、绝对归一化及与S/A/T算符的匹配尚未闭合。这个缺口**不阻断当前解析KN的SM/V/B−L**；完整资源内容与后续适用性在第9、10章分别登记。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)
- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)

[返回目录](#report-toc)

<a id="detector"></a>

## 5. Detector Response、Qy与数值取得状态

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

原YBe表的**存储域0.3–10keV**不等于已认证响应域。当前只在单能基底 **0.51–5keVnr** 内使用；T域外本重铸模型返回零，不外推；Ly/Qy超网格时拒绝，不裁剪成端点。已有模板包含选择，不再乘另一条接受度曲线。当前实现对九种Xe同位素共用这一真实反冲NR响应，核素差异在核数/质量/共享截面中进入；这是实际组件的采用约定，不是额外同位素标定。

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

<a id="eq-prediction"></a>

$$
\mu_i^{\rm sig}=\sum_r\mathcal E_r t_{\rm yr}\sum_A n_A^{(t)}\int dT\,P_{ri}(T)\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT} \tag{5}
$$

公式依据：项目对R01式(11)–(13)采用Response后的实验侧折叠；Source、核数、截面、选择和曝光各一次。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $\mathcal E_r$或$\mathcal E$ | 已取得；具体曝光见第3章 | t·yr | R17或R02；参考年注量×参考吨核数×曝光/anchor_tonne |
| $t_{\rm yr}$ | 31557600；每年秒数只施加一次 | s/yr | R18 SEC_PER_YEAR=365.25×86400；单位约定 |
| $n_A^{(t)}$ | 已由九核素中心值推导 | nuclei/t | 第3章核数表 |
| $d\sigma_A/dT$ | 已存在的共享SM或V/B−L组件输出 | cm²/keVnr | 第4章模块/参数；不把核数或效率放进截面 |
| $P_{ri}$ | 已取得的接受后箱概率 | 1 | 第5章实际数值与有效域 |
| $\mu_i^{\rm sig}$ | 项目派生的重建事件数 | events/bin | 当前已执行的数值结果如下 |

完整Response路线直接在真实T上积分，不使用1/Qy代替能量相关均值映射的Jacobian，也不把均值转换当作概率迁移。

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `constants.seconds_per_year` | 31557600 | s/yr | R18；365.25×86400=31557600；计算单位约定，不是额外活时间 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `numerics.n_er` | 401 | 1 | 项目配置选择；不是文献测量；Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |
| `numerics.n_enu` | 240 | 1 | 项目配置选择；不是文献测量；Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 | [实际标量卡](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) |

上表401/240为正式包默认基础节点；已保存benchmark显式覆盖为T=201/401/801、Eν=120/480并分别加密，另并入原源谱、响应、产额与输出箱断点。积分为共享recoil/folding的梯形求积；预定逐箱条件max(2×10⁻⁴ events,0.2%)，两种维度分别检查。不能只凭一个相对差异超过0.2%就忽略其绝对容差条件。

<a id="benchmark-results"></a>

| 点 | m[MeV] | g | κ | 箱1 | 箱2 | 箱3 | 信号/投影总量[events] |
|---|---|---|---|---|---|---|---|
| SM | — | 0 | — | 3.514030918 | 5.649108573 | 3.154093732 | 12.317233224 |
| V10_g1 | 10 | 1e-05 | 1 | 2.436180037 | 4.084558483 | 2.405778680 | 8.926517199 |
| V10_g2 | 10 | 2e-05 | 1 | 0.463013854 | 1.009259782 | 0.802118992 | 2.274392628 |
| V10_g3 | 10 | 3e-05 | 1 | 1.375691753 | 1.278267183 | 0.266971082 | 2.920930019 |
| BL10_g2 | 10 | 2e-05 | −1/3 | 5.277932287 | 8.154747990 | 4.318106332 | 17.750786609 |
| V1_g2 | 1 | 2e-05 | 1 | 0.347819902 | 0.596343248 | 0.510307035 | 1.454470186 |
| V100_g2 | 100 | 2e-05 | 1 | 3.342058655 | 5.373834989 | 3.001488381 | 11.717382025 |

**非零m/g数值是项目选取的测试点，不是论文最佳拟合或排除界；κ与耦合定义来自R19。** 直接采用卡：[全部测试点、值的性质与固定输入哈希](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>)。SM总数与上一轮逐箱一致；所有核素、run和逐箱数组已保存。

相对R17原发布名义SM信号，三箱差异为[2.05719270579, 2.46324308072, 6.57183329468]%；逐run最大差异另见原比较记录。曝光3.516991与打印3.51以及早期重铸模型适用性均未通过c_i强行消除。该差异与此前同一官方CDF谱重铸的6.30%核对不是同一检查。

干涉分解的和允许含负项，完整逐箱表：

| 点 | SM总量 | 干涉项 | 纯NP项 | 闭合最大误差[events] |
|---|---|---|---|---|
| V10_g1 | 12.317233224 | -3.684051316 | 0.293335292 | 3.55e-15 |
| V10_g2 | 12.317233224 | -14.736205266 | 4.693364670 | 1.72e-15 |
| V10_g3 | 12.317233224 | -33.156461848 | 23.760158644 | 8.88e-15 |
| BL10_g2 | 12.317233224 | 4.912068422 | 0.521484963 | 5.33e-15 |
| V1_g2 | 12.317233224 | -19.713278715 | 8.850515677 | 4.22e-15 |
| V100_g2 | 12.317233224 | -0.607339908 | 0.007488709 | 4.44e-15 |

依据为共享矢量振幅的有符号分解及逐核素真实反冲重权重后独立折叠；它是内部解析闭合检验，不是外部非零点模板复现。

### SM前向图

![SM前向图](<../../../../../outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/events.png>)

### V/B−L前向图

![V/B−L前向图](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/events.png>)

| 实际结果/复算 | 入口 |
|---|---|
| SM逐箱、run/核素分量、收敛、参数指纹 | [SM_RESULT.json](<../../../../../outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json>) |
| V/B−L全部点、分解及逐箱数组 | [DATASET_RESULT.json](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json>) · [全部逐箱TSV](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/counts_by_point.tsv>) |
| SM复算 | `python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run` |
| V/B−L复算 | `python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/repeat_run` |

标准API可直接运行（以下为本实验路径）：

```python
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector
from cevns_pyeft.experiments.runtime import predict_experiment
sm = load_experiment_package("data/experiments/XENONnT/XENONnT_2024_SolarB8")
vector = with_solar_light_vector(sm, mass_MeV=10., coupling=2e-5, scenario="universal")
result = predict_experiment(vector, numerics={"n_er": 801, "n_enu": 480})
print(result.counts)
```

PandaX路径的返回量始终是keVnr投影；更换interaction不会凭空补出电子数Response。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

[返回目录](#report-toc)

<a id="statistics"></a>

## 8. Statistics、观测与背景的来源和适用范围

**已执行的是固定点前向预测与观测/名义背景作图；统计evaluator、χ²最小化、置信区间未实现/未运行。** 下列R01统计合同作为后续明确依据保留，不因公式写出就声称统计能力已完成。

<a id="eq-mean-counts"></a>

$$
\mu_i=(1+\alpha)(1+\beta_s)S_i(\theta)+\sum_k(1+\beta_k)B_i^k \tag{6}
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

正式Runtime数值权威是每实验YAML+NPZ。下列目录同时保存原始摘录、转换结果、候选与对照；“本地有文件”和“用于本轮计算”分别列出。完整哈希/原文件到正式键的关系见[本轮机器可读资源与溯源清单](<../../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/NUMERICAL_INVENTORY.json>)。

### 正式包全部数组索引

| 键 | shape | 单位 | 本版详细定义/数值所在章 | 完整文件 |
|---|---|---|---|---|
| `source_energy_MeV` | [829] | MeV | [第2章Source](#source) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `source_shape_per_MeV` | [829] | MeV^-1 | [第2章Source](#source) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_mass_number` | [9] | 1 | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_atomic_mass_u` | [9] | u | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `target_number_fraction` | [9] | 1 | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `run_exposures_tyr` | [2] | t yr | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_energy_keV` | [16] | keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Ly` | [10] | photon/keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_Qy` | [10] | electron/keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR0` | [16, 10, 10, 3] | 1 | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `cs2_edges_SR0` | [4] | PE | [第6章Observable](#observable) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `response_SR1` | [16, 10, 10, 3] | 1 | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `cs2_edges_SR1` | [4] | PE | [第6章Observable](#observable) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_energy_keV` | [501] | keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Ly_median` | [501] | photon/keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `yield_Qy_median` | [501] | electron/keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |
| `observable_edges` | [4] | 1 | [第6章Observable](#observable) | [正式NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) |

### 全部辅助数值文件：出处、处理和当前用途

| 文件/claim | 数值覆盖 | 单位 | 直接出处及转换 | 本轮用途/限制 |
|---|---|---|---|---|
| [xenonnt_qy_sr0_23Vcm.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_23Vcm.txt>) `XENONnT-C012` | [99, 4]，各列范围：[0.4999999979, 100]; [1.991116633, 7.452982227]; [0, 1]; [0, 1] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; deep red SR0 23 V/cm；PDF vectors; clipped nodes and original extrapolation flags retained | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_qy_sr0_band.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_band.txt>) `XENONnT-C013` | [100, 3]，各列范围：[0.4999999979, 100]; [1.883201701, 7.205418402]; [2.116291405, 7.770667665] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R07；2406.13638v1 PDF p6 Fig.3 bottom right; same figure; deep red model band；original band; no nuisance covariance inferred | 早期WIMP Qy参考；不是本轮YBe产额 |
| [xenonnt_original_fig2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_original_fig2.txt>) `XENONnT-C014` | [3, 6]，各列范围：[1, 3]; [7, 16]; [8.4182867, 8.418375626]; [0.0701057518, 0.2627899614]; [0.008421507254, 0.4919749226]; [2.606485679, 4.96995278] | D/background/reference signal events/bin, coordinate columns as declared | R03；2408.02877v1 PDF p6 Fig.2 upper；fitted components; run bin edges are in the separate official bin table | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_benchmark_fig1.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt>) `XENONnT-C015` | [3, 8]，各列范围：[1, 3]; [90.00000017, 234.9999994]; [154.9999995, 500]; [7, 16]; [8.433333333, 8.433333333]; [0.1130267707, 0.2394635342]; [0.06729647667, 0.5126921747]; [2.699105414, 4.906604663] | D/background/reference signal events/bin, coordinate columns as declared | R01；2411.11749v1 PDF p7 Fig.1 right；plot coordinates are not certified likelihood edges; reference B | 原图拟合/benchmark投影参考；非prefit原生模板 |
| [xenonnt_official_observed_bins.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt>) `XENONnT-C016` | [6, 5]，各列范围：[0, 1]; [1, 3]; [90, 249.88974]; [155.937851, 500]; [1, 11] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv; binning/sr0.yaml,sr1.yaml；direct official histogram; no cuts | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |
| [xenonnt_official_observed_events.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_events.txt>) `XENONnT-C017` | [37, 3]，各列范围：[0, 1]; [0, 27]; [118.58632, 494.5456] | as declared per column/key in the numerical file and chapter | R08；fixed commit data/sr0.csv,sr1.csv；direct event values; original row order retained | 官方SR0/SR1观测核对与绘图；不进入信号前向积分 |
| [b8_bahcall1996_official.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>) `XENONnT-C018` | [829, 4]，各列范围：[0, 16.56]; [0, 0.1321716]; [0, 0.1339827]; [0, 0.1304072] | MeV; MeV^-1 | R04；official b8spectrum.txt, all four columns；byte-identical download | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenon_natural_isotopes_nist_v2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt>) `XENONnT-C019` | [9, 3]，各列范围：[124, 136]; [123.905892, 135.907214484]; [0.00089, 0.269086] | 1; u; 1 | R09；Xe rows 124,126,128,129,130,131,132,134,136；parsed central values; uncertainties retained in official source download, not treated as zero | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr0_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>) `XENONnT-C020` | energy_keVnr:[46]; tLy:[7]; tQy:[7]; probability:[7, 7, 46, 3, 3, 3, 3]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | 1, keVnr; nuisance coordinate dimensionless | R08；templates/sr0/mono/*; /templates/template and /bins/*；lossless direct HDF5 array stacking; no interpolation or normalization | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr0_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>) `XENONnT-C021` | tLy:[7]; tQy:[7]; AC:[3, 3, 3, 3]; ER:[3, 3, 3, 3]; neutron:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/(t yr bin) | R08；templates/sr0/ac,er,rg/*; /templates/template；lossless HDF5 array stacking | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr0_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_observed_4d_v2.npz>) `XENONnT-C022` | observed:[3, 3, 3, 3]; events:[9, 4]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/bin; PE and dimensionless classifiers | R08；data/sr0.csv; binning/sr0.yaml；histogramdd without cuts; exact event values | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>) `XENONnT-C023` | energy_keVnr:[46]; tLy:[7]; tQy:[7]; probability:[7, 7, 46, 3, 3, 3, 3]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | 1, keVnr; nuisance coordinate dimensionless | R08；templates/sr1/mono/*; /templates/template and /bins/*；lossless direct HDF5 array stacking; no interpolation or normalization | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>) `XENONnT-C024` | tLy:[7]; tQy:[7]; AC:[3, 3, 3, 3]; ER:[3, 3, 3, 3]; neutron:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/(t yr bin) | R08；templates/sr1/ac,er,rg/*; /templates/template；lossless HDF5 array stacking | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_sr1_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_observed_4d_v2.npz>) `XENONnT-C025` | observed:[3, 3, 3, 3]; events:[28, 4]; axis_names:[4]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | events/bin; PE and dimensionless classifiers | R08；data/sr1.csv; binning/sr1.yaml；histogramdd without cuts; exact event values | 2026发布候选；未替换本轮早期响应/背景 |
| [xenonnt_2024_calibration_inputs.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_calibration_inputs.v2.1.json>) `XENONnT-C027` | 9条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R03；2408.02877v1 PDF p2-p3, Dataset and gain/FV paragraphs；transcribed printed primary-source values | 原2024标定/prefit总数/约束参考；完整likelihood未实例化 |
| [xenonnt_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_prefit_inputs_2024.v2.1.json>) `XENONnT-C028` | 15条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R03；2408.02877v1 PDF p5 Table I and background text, p6 statistical inference；transcribed printed primary-source values | 原2024标定/prefit总数/约束参考；完整likelihood未实例化 |
| [xenonnt_2024_fig1_acceptance.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>) `XENONnT-C031` | [40, 8]，各列范围：[0.429999996183, 2.77000000181]; [0.0180363902791, 0.255562907963]; [0.00527964624015, 0.478743981244]; [0.000111966577589, 0.123987528765]; [0, 1]; [0, 1]; [0, 1]; [0, 1] | All efficiencies and flags dimensionless. Energy keVnr. Total acceptance is already the black combined path. | R03；2408.02877v1 PDF p4 Fig.1 upper: light-blue S1, dark-blue S2, black combined acceptance；Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation | 原2024边际接受度对照；当前响应含选择，不再相乘 |
| [xenonnt_2024_fig1_sm_recoil_spectra.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_2024_fig1_sm_recoil_spectra.txt>) `XENONnT-C032` | [40, 6]，各列范围：[0.429999996183, 2.77000000181]; [1.0677678874, 1091.71726397]; [0.022177392585, 2.76844400232]; [0, 1]; [0, 1]; [0, 1] | Rates events/(t yr keVnr). Flags dimensionless. With-acceptance rate already includes acceptance. | R03；2408.02877v1 PDF p4 Fig.1 lower: light-pink without acceptance and dark-red with acceptance SM curves；Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation | 原2024真实反冲SM参考谱；验证用途 |
| [ly_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_lower.json>) `XENONnT-C033` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [ly_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_median.json>) `XENONnT-C034` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | 本轮前向输入的直接来源，已封入正式NPZ |
| [ly_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_upper.json>) `XENONnT-C035` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map photon/keVnr | R17；data/signal/ly_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [qy_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_lower.json>) `XENONnT-C036` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [qy_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_median.json>) `XENONnT-C037` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | 本轮前向输入的直接来源，已封入正式NPZ |
| [qy_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_upper.json>) `XENONnT-C038` | coordinate_system:[501]; map:[501] | coordinate_system keVnr; map electron/keVnr | R17；data/signal/qy_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；byte-identical copy from pinned official archive | YBe上下曲线参考；未据此虚构协方差或profile |
| [xenonnt_early_release_cevns_spectrum.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_early_release_cevns_spectrum.json>) `XENONnT-C039` | coordinate_system:[501]; map:[501]; rate:[] | map/coordinate_system according to coordinate_name; recoil keV, rate events/(t yr) | R17；data/signal/cevns_spectrum.json; utils.py::Template.required_keys and format_custom_signal_spectrum；byte-identical copy from pinned official archive | 官方已折叠CEvNS参考谱/CDF；不是中微子源谱 |
| [xenonnt_sr0_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_basis.npz>) `XENONnT-C040` | probability_basis:[16, 10, 10, 3, 3, 3, 3]; energy_keVnr:[16]; Ly_photon_per_keV:[10]; Qy_electron_per_keV:[10]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4]; axis_names:[7] | probability dimensionless; energy keVnr, Ly photon/keVnr, Qy electron/keVnr, cS2 PE | R17；data/orthonormal_basis/SR0 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr0_response_early_release_nominal_1d.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_nominal_1d.txt>) `XENONnT-C041` | [46, 4]，各列范围：[0.51, 5]; [0.000250822205457, 0.014421499093]; [6.73116676691e-05, 0.0400981009634]; [1.85242618582e-06, 0.127593835924] | keVnr; probabilities dimensionless | R17；utils.py::Template.interpolator/default_yield_model; original 1600 SR0 HDF5 plus ly/qy median JSON；Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency | 项目推导的一维名义响应对照；Runtime直接插值基底 |
| [xenonnt_sr0_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) `XENONnT-C042` | tLy:[7]; tQy:[7]; ac_rate_per_tyr_bin:[3, 3, 3, 3]; er_rate_per_tyr_bin:[3, 3, 3, 3]; b8_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; rg_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr0_*; statistical_model_base.yaml in_events_per_bin；lossless original HDF5 template stacking, no exposure applied or rescaling | 早期发布名义背景/信号对照；B8不是额外背景 |
| [xenonnt_sr1_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_basis.npz>) `XENONnT-C043` | probability_basis:[16, 10, 10, 3, 3, 3, 3]; energy_keVnr:[16]; Ly_photon_per_keV:[10]; Qy_electron_per_keV:[10]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4]; axis_names:[7] | probability dimensionless; energy keVnr, Ly photon/keVnr, Qy electron/keVnr, cS2 PE | R17；data/orthonormal_basis/SR1 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenonnt_sr1_response_early_release_nominal_1d.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_nominal_1d.txt>) `XENONnT-C044` | [46, 4]，各列范围：[0.51, 5]; [7.17318527876e-05, 0.00773730855365]; [8.24732257891e-05, 0.0296432030029]; [2.61244062793e-06, 0.120980106453] | keVnr; probabilities dimensionless | R17；utils.py::Template.interpolator/default_yield_model; original 1600 SR1 HDF5 plus ly/qy median JSON；Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency | 项目推导的一维名义响应对照；Runtime直接插值基底 |
| [xenonnt_sr1_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>) `XENONnT-C045` | tLy:[7]; tQy:[7]; ac_rate_per_tyr_bin:[3, 3, 3, 3]; er_rate_per_tyr_bin:[3, 3, 3, 3]; b8_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; rg_rate_per_tyr_bin:[7, 7, 3, 3, 3, 3]; bin_edges_0:[4]; bin_edges_1:[4]; bin_edges_2:[4]; bin_edges_3:[4] | rates events/(t yr bin); no bin-width factors; tLy/tQy nuisance coordinates -3..3 | R17；data/ac,er,b8,rg/template_XENONnT_sr1_*; statistical_model_base.yaml in_events_per_bin；lossless original HDF5 template stacking, no exposure applied or rescaling | 早期发布名义背景/信号对照；B8不是额外背景 |

### 辅助NPZ/产额JSON内的实际轴、shape和代表值

**[xenonnt_sr0_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>)**；R08，templates/sr0/mono/*; /templates/template and /bins/*；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| energy_keVnr | [46] | [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| probability | [7, 7, 46, 3, 3, 3, 3] | 范围[2.80869316971e-16, 0.0192432852281]；首/中/末[2.80869316971e-16, 5.81551069057e-05, 0.00131151182116] | 1；接受后箱概率，Σ≤1 |
| axis_names | [4] | cs2, s2_shadow_s2_time_shadow, s1_bdt_score, s2_bdt_score | 轴标签/原字段，保持原约定 |
| bin_edges_0 | [4] | [90, 170.161773682, 249.88973999, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.282301220403, 0.498535093, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.8069558, 0.883306158412, 0.923731456497, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr0_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>)**；R08，templates/sr0/ac,er,rg/*; /templates/template；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| AC | [3, 3, 3, 3] | 范围[0.046447105502, 0.103429398841]；首/中/末[0.0785140641019, 0.0734387181365, 0.0781295681954] | events/(t·yr·bin) |
| ER | [3, 3, 3, 3] | 范围[4.06979940323e-06, 0.0139162129334]；首/中/末[1.96194039495e-05, 0.000274765334254, 0.0047647275421] | events/(t·yr·bin) |
| neutron | [7, 7, 3, 3, 3, 3] | 范围[8.06431000303e-06, 0.0154989700128]；首/中/末[0.000119714672071, 0.000773050493153, 0.00246888085685] | events/(t·yr·bin) |
| bin_edges_0 | [4] | [90, 170.161773682, 249.88973999, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.282301220403, 0.498535093, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.8069558, 0.883306158412, 0.923731456497, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr0_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_observed_4d_v2.npz>)**；R08，data/sr0.csv; binning/sr0.yaml；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| observed | [3, 3, 3, 3] | 范围[0, 2]；首/中/末[0, 0, 0] | events/bin |
| events | [9, 4] | 范围[0.205162159769, 462.59204]；首/中/末[130.4071, 0.205162159769, 0.879023602523] | 原四观测量；各轴单位由axis_names/bin_edges确定 |
| axis_names | [4] | cs2, s2_shadow_s2_time_shadow_quantile, s1_bdt_score, s2_bdt_score | 轴标签/原字段，保持原约定 |
| bin_edges_0 | [4] | [90, 170.161773682, 249.88973999, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.282301220403, 0.498535093, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.8069558, 0.883306158412, 0.923731456497, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr1_response_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>)**；R08，templates/sr1/mono/*; /templates/template and /bins/*；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| energy_keVnr | [46] | [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| probability | [7, 7, 46, 3, 3, 3, 3] | 范围[2.86258842363e-16, 0.0267718568029]；首/中/末[2.86258842363e-16, 3.50864683372e-05, 0.0016268897475] | 1；接受后箱概率，Σ≤1 |
| axis_names | [4] | cs2, s2_shadow_s2_time_shadow, s1_bdt_score, s2_bdt_score | 轴标签/原字段，保持原约定 |
| bin_edges_0 | [4] | [90, 155.937850952, 232.292022705, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.278574121795, 0.493158321679, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.7752842, 0.859520047133, 0.902943575517, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr1_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>)**；R08，templates/sr1/ac,er,rg/*; /templates/template；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| AC | [3, 3, 3, 3] | 范围[0.0696992870144, 0.14249202366]；首/中/末[0.0796563280164, 0.0959936088839, 0.0817830746382] | events/(t·yr·bin) |
| ER | [3, 3, 3, 3] | 范围[9.30943269118e-06, 0.0402359495515]；首/中/末[3.26221309123e-05, 0.000381901859616, 0.012375573543] | events/(t·yr·bin) |
| neutron | [7, 7, 3, 3, 3, 3] | 范围[7.09532952034e-06, 0.0199811541618]；首/中/末[0.000102931938946, 0.000818956164145, 0.00504344960001] | events/(t·yr·bin) |
| bin_edges_0 | [4] | [90, 155.937850952, 232.292022705, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.278574121795, 0.493158321679, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.7752842, 0.859520047133, 0.902943575517, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr1_observed_4d_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_observed_4d_v2.npz>)**；R08，data/sr1.csv; binning/sr1.yaml；用途：2026发布候选；未替换本轮早期响应/背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| observed | [3, 3, 3, 3] | 范围[0, 2]；首/中/末[0, 0, 0] | events/bin |
| events | [28, 4] | 范围[0.0896611236416, 494.5456]；首/中/末[211.21495, 190.02835, 0.804648960016] | 原四观测量；各轴单位由axis_names/bin_edges确定 |
| axis_names | [4] | cs2, s2_shadow_s2_time_shadow_quantile, s1_bdt_score, s2_bdt_score | 轴标签/原字段，保持原约定 |
| bin_edges_0 | [4] | [90, 155.937850952, 232.292022705, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.278574121795, 0.493158321679, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.7752842, 0.859520047133, 0.902943575517, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[ly_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_lower.json>)**；R17，data/signal/ly_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：YBe上下曲线参考；未据此虚构协方差或profile。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[2.37600982425, 4.33739853185]；首/中/末[2.37600982425, 4.33625986357, 3.83736093827] | photon/keVnr |

**[ly_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_median.json>)**；R17，data/signal/ly_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：本轮前向输入的直接来源，已封入正式NPZ。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[4.96483304998, 5.84943426556]；首/中/末[4.96948391067, 4.97702186212, 5.84943426556] | photon/keVnr |

**[ly_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_upper.json>)**；R17，data/signal/ly_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：YBe上下曲线参考；未据此虚构协方差或profile。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[5.69268706096, 9.77501823636]；首/中/末[7.9112530398, 5.741499036, 9.77501823636] | photon/keVnr |

**[qy_ybe_model_lower.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_lower.json>)**；R17，data/signal/qy_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：YBe上下曲线参考；未据此虚构协方差或profile。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[0.214848574899, 5.99516547032]；首/中/末[0.214848574899, 5.98901013519, 4.87851687292] | electron/keVnr |

**[qy_ybe_model_median.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_median.json>)**；R17，data/signal/qy_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：本轮前向输入的直接来源，已封入正式NPZ。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[2.74488347604, 6.42315153388]；首/中/末[2.74488347604, 6.42026853025, 5.21471791433] | electron/keVnr |

**[qy_ybe_model_upper.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_upper.json>)**；R17，data/signal/qy_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13；用途：YBe上下曲线参考；未据此虚构协方差或profile。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0.3, 10]；首/中/末[0.3, 1.73205080757, 10] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[5.64397973243, 6.90647622377]；首/中/末[6.23420511688, 6.90298919425, 5.64397973243] | electron/keVnr |

**[xenonnt_early_release_cevns_spectrum.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_early_release_cevns_spectrum.json>)**；R17，data/signal/cevns_spectrum.json; utils.py::Template.required_keys and format_custom_signal_spectrum；用途：官方已折叠CEvNS参考谱/CDF；不是中微子源谱。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| coordinate_system | [501] | 范围[0, 1]；首/中/末[0, 0.991410149163, 1] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| map | [501] | 范围[0.45, 10]；首/中/末[0.45, 2.12132034356, 10] | CDF无量纲；非中微子flux |
| rate | [] | 范围[335.596469109, 335.596469109]；首/中/末[335.596469109, 335.596469109, 335.596469109] | events/(t·yr)，原CDF文件的积分总率；不是中微子通量 |

**[xenonnt_sr0_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_basis.npz>)**；R17，data/orthonormal_basis/SR0 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；用途：本轮前向输入的直接来源，已封入正式NPZ。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| probability_basis | [16, 10, 10, 3, 3, 3, 3] | 范围[1e-10, 0.0195405327283]；首/中/末[1e-10, 3.15418437324e-07, 0.000136502641328] | 1；接受后箱概率，Σ≤1 |
| energy_keVnr | [16] | [0.51, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 4.5, 5] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| Ly_photon_per_keV | [10] | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | photon/keVnr；物理产额坐标 |
| Qy_electron_per_keV | [10] | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | electron/keVnr；物理产额坐标 |
| bin_edges_0 | [4] | [90, 170.161773682, 249.88973999, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.33333333, 0.66666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.282301220403, 0.498535093, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.8069558, 0.883306158412, 0.923731456497, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| axis_names | [7] | energy, Ly, Qy, cs2, shadow, s1_bdt, s2_bdt | 轴标签/原字段，保持原约定 |

**[xenonnt_sr0_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>)**；R17，data/ac,er,b8,rg/template_XENONnT_sr0_*; statistical_model_base.yaml in_events_per_bin；用途：早期发布名义背景/信号对照；B8不是额外背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| ac_rate_per_tyr_bin | [3, 3, 3, 3] | 范围[0.046447105502, 0.103429398841]；首/中/末[0.0785140641019, 0.0734387181365, 0.0781295681954] | events/(t·yr·bin) |
| er_rate_per_tyr_bin | [3, 3, 3, 3] | 范围[4.34372123227e-06, 0.013963341936]；首/中/末[1.92632294713e-05, 0.000277660308585, 0.0047570984347] | events/(t·yr·bin) |
| b8_rate_per_tyr_bin | [7, 7, 3, 3, 3, 3] | 范围[0.000284494615223, 0.680859274933]；首/中/末[0.0027079467385, 0.0357528106372, 0.159899345716] | events/(t·yr·bin) |
| rg_rate_per_tyr_bin | [7, 7, 3, 3, 3, 3] | 范围[9.49905728031e-06, 0.0122560141522]；首/中/末[0.000102053370124, 0.000567923023391, 0.00274293467906] | events/(t·yr·bin) |
| bin_edges_0 | [4] | [90, 170.161773682, 249.88973999, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.282301220403, 0.498535093, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.8069558, 0.883306158412, 0.923731456497, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |

**[xenonnt_sr1_response_early_release_basis.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_basis.npz>)**；R17，data/orthonormal_basis/SR1 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator；用途：本轮前向输入的直接来源，已封入正式NPZ。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| probability_basis | [16, 10, 10, 3, 3, 3, 3] | 范围[1e-10, 0.026273586265]；首/中/末[1e-10, 2.61533625689e-07, 0.000110467614858] | 1；接受后箱概率，Σ≤1 |
| energy_keVnr | [16] | [0.51, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 4.5, 5] | 能量坐标keVnr（JSON坐标）；完整字段定义见R17原件 |
| Ly_photon_per_keV | [10] | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | photon/keVnr；物理产额坐标 |
| Qy_electron_per_keV | [10] | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | electron/keVnr；物理产额坐标 |
| bin_edges_0 | [4] | [90, 155.937850952, 232.292022705, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.33333333, 0.66666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.278574121795, 0.493158321679, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.7752842, 0.859520047133, 0.902943575517, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| axis_names | [7] | energy, Ly, Qy, cs2, shadow, s1_bdt, s2_bdt | 轴标签/原字段，保持原约定 |

**[xenonnt_sr1_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>)**；R17，data/ac,er,b8,rg/template_XENONnT_sr1_*; statistical_model_base.yaml in_events_per_bin；用途：早期发布名义背景/信号对照；B8不是额外背景。

| 原字段/轴 | shape | 范围与代表值/完整小轴 | 单位/解释 |
|---|---|---|---|
| tLy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| tQy | [7] | [-3, -2, -1, 0, 1, 2, 3] | 无量纲nuisance坐标；不能当物理Ly/Qy |
| ac_rate_per_tyr_bin | [3, 3, 3, 3] | 范围[0.0696992870144, 0.14249202366]；首/中/末[0.0796563280164, 0.0959936088839, 0.0817830746382] | events/(t·yr·bin) |
| er_rate_per_tyr_bin | [3, 3, 3, 3] | 范围[6.2894970629e-06, 0.0407181535813]；首/中/末[3.09811443615e-05, 0.00040710079431, 0.0123970041657] | events/(t·yr·bin) |
| b8_rate_per_tyr_bin | [7, 7, 3, 3, 3, 3] | 范围[0.000248742041875, 0.801032711149]；首/中/末[0.00213618525348, 0.0286258774891, 0.199740526988] | events/(t·yr·bin) |
| rg_rate_per_tyr_bin | [7, 7, 3, 3, 3, 3] | 范围[2.18442405186e-06, 0.0164279358369]；首/中/末[7.44636196078e-05, 0.000860807354494, 0.0044538833851] | events/(t·yr·bin) |
| bin_edges_0 | [4] | [90, 155.937850952, 232.292022705, 500] | cS2，PE |
| bin_edges_1 | [4] | [0, 0.333333333333, 0.666666666667, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_2 | [4] | [0, 0.278574121795, 0.493158321679, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |
| bin_edges_3 | [4] | [0.7752842, 0.859520047133, 0.902943575517, 1] | 原shadow/S1BDT/S2BDT维度，无量纲 |


### 未采用的共享核多项式候选

| 核素键 | J | 本地b数值 | 实际通道键 | M系数shape | M首/中/末系数 |
|---|---|---|---|---|---|
| Xe128 | 0 | 11.5792987149 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.83781333, 3995.65032995, 0.000151613884778] |
| Xe129 | 0.5 | 11.5924668142 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.96164997, 4049.60832194, 0.000341053359735] |
| Xe130 | 0 | 11.605553387 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.85321599, 4103.52767595, 0.000341089897576] |
| Xe131 | 1.5 | 11.6185595465 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.97732507, 4157.7032823, 0.000614895948032] |
| Xe132 | 0 | 11.6314863821 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.99213116, 4211.83964872, 0.000606401976742] |
| Xe134 | 0 | 11.6571063271 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.95905802, 4319.24196891, 0.00120771042527] |
| Xe136 | 0 | 11.6824214951 | Delta, M, MPhiPP, PhiPP, PhiPT, SigmaP, SigmaPDelta, SigmaPP | (2, 2, 11) | [2915.99793279, 4427.99393271, 0.00136461964265] |

完整本地资源：[responses_all.json，R16](<../../../../../data/responses/responses_all.json>)；b及系数的外部原始单位/基底/归一化对应仍未独立闭合，表内只报告实际容器值，不认证外部核源。Xe124/Xe126键缺失。当前SM/V/B−L未读取这些系数，不将其覆盖缺口误列为解析KN所需输入。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R07] APRILE E, et al. (XENON Collaboration). XENONnT WIMP search: Signal and background modeling and statistical inference[J]. Physical Review D, 2025, 111: 103040. DOI: [10.1103/PhysRevD.111.103040](https://doi.org/10.1103/PhysRevD.111.103040). 实际提取 [arXiv:2406.13638v1](https://arxiv.org/abs/2406.13638v1), 2024-06-19，第 6 页 Fig.3 右下图；期刊版为后续版本，不替换本次所用曲线。 [本地直接采用源](<../../../../references/Solar_CEvNS/2406.13638v1.pdf>)
- [R08] XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [本地直接采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

[返回目录](#report-toc)

<a id="status"></a>

## 10. 缺失、交接、验证与完整参考文献

本版对已运行SM/V/B−L和待补能力分别给出状态；未把过时“无响应/未绑定”或候选模型当作当前事实。

| 下一步能力 | 当前状态 | 具体需要什么/阻断范围 |
|---|---|---|
| 当前SM/V/B−L重建谱 | 可运行；早期R17重铸模型范围内已算 | 严格2024复现仍需模型版本等价性/重铸误差核验 |
| XENONnT精确原生4D likelihood | 未实现/未认证 | 2024配套81箱模板及tLy/tQy数值约束/相关性；R17已有模板与R08后续候选分开 |
| Fig.2/一维统计 | 未运行；不能把公式存在当拟合完成 | 明确采用分箱、flux nuisance参数化与数据/背景角色，再实现统计；联合通量约束仅一次 |
| Fig.4 V/B−L排除限 | 未请求/未运行；前向测试点已完成 | 具体χ²/CL构造、阈值与profile方案；无需S/A/T的自旋核输入 |
| S/A/T/Full EFT | 未实现本任务benchmark | 对应标量或自旋输入、匹配/归一化与外源核验；本地JSON存在不等于原文已核 |
| 味相关接触NSI | 不在当前模型范围 | 具体ε定义、flavor矩阵及太阳传播/味组成；不能沿用味普适代表态 |

### 实际验证层次

| 记录 | 实际结论 | 不能替代的验证 |
|---|---|---|
| 2026-11-09文档整合 | 当轮实际包/组件指纹与保存结果一致；数字文件和旧版本哈希保护；链接/数学/跳转另有验收 | 该文档整合未重算物理谱；2026-11-10新增的简化谱另外记录 |
| 2026-11-07 SM计算 | 95项通过、4项既有文档/资源清单检查失败；新增solar 7项通过；所选旧数值回归通过 | 不是“全仓库全部通过”；旧数组/容差未改 |
| 2026-11-08 V/B−L计算 | 27项相关测试全部通过；两实验各7点分别T/Eν收敛；带符号闭合通过 | 不是非零点外部模板复现或官方likelihood认证 |

[SM实际测试/失败原因](<../../../../../outputs/solar_b8_sm/20261107_run1/TEST_RESULTS.json>) · [SM输入与保存核验](<../../../../../outputs/solar_b8_sm/20261107_run1/VALIDATION.json>) · [V/B−L实际27项测试](<../../../../../outputs/solar_b8_vector/20261108_run1/TEST_RESULTS.json>) · [V/B−L验证范围](<../../../../../outputs/solar_b8_vector/20261108_run1/VALIDATION.json>) · [本轮v3.0生成与验收](<../../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/README.md>)

本轮来源核验分为：①文件存在与数值回读；②本地哈希与已登记来源一致；③原文真实性/转换/适用性继承P00/P01明确核验范围。文件或schema PASS不自动证明第三层完整。R18常量是项目明确采用的本地约定；R05 SSM只核书目，通量标量的直接出处是R01；R16外部核源未闭合；R13在线SI原文未缓存。

### 标准参考文献总表

<a id="ref-R01"></a>

**[R01]** DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。

[本地直接出处](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)；登记SHA256 `fffe6e2c364ad25a0f090cd933619866dba1d21603adc6fbab912500eb291479`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R02"></a>

**[R02]** BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。

[本地直接出处](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)；登记SHA256 `fc5e460404919cd82debece761b724576093f8b01539b566e9acd281e9102026`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R03"></a>

**[R03]** APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。

[本地直接出处](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)；登记SHA256 `db11a4d30b0127923b6af94614b16d52692b9a2637ad3c1f7928bfbbaec8e529`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R04"></a>

**[R04]** BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。

[本地直接出处](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)；登记SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R05"></a>

**[R05]** VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. The Astrophysical Journal, 2017, 835(2): 202. DOI: [10.3847/1538-4357/835/2/202](https://doi.org/10.3847/1538-4357/835/2/202). [arXiv:1611.09867](https://arxiv.org/abs/1611.09867). 本任务采用的通量值与 12% 误差直接定位于文献 [1] 第 III 节和式 (17) 后文字，后者引用本篇；未声称从任意 SSM 表重新推导。

[本地直接出处](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Vinyoles-abs.html>)；登记SHA256 `a52b8c04fea89ef0bc76fa058a1ad38f9b342cf4c7059ef7aa3487a5dfe91bb0`。

核验范围：仅核书目，上游SSM数表保持未独立核验。通量标量的直接来源为R01

<a id="ref-R06"></a>

**[R06]** LUO Y, BO Z, ZHANG S, et al. (PandaX Collaboration). Signal response model in PandaX-4T[J]. Physical Review D, 2024, 110: 023029. DOI: [10.1103/PhysRevD.110.023029](https://doi.org/10.1103/PhysRevD.110.023029). 实际提取 [arXiv:2403.04239v2](https://arxiv.org/abs/2403.04239v2), 2024-03-08，第 21 页 Table II；本文 NR 拟合适用范围不能外推冒充 US2 sub-keV 校准。

[本地直接出处](<../../../../references/Solar_CEvNS/2403.04239v2.pdf>)；登记SHA256 `4e15f95ddc9cf8b7ab71796fe4efe775d4fffdd4e0f58d8693241f9cc4d76f68`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R07"></a>

**[R07]** APRILE E, et al. (XENON Collaboration). XENONnT WIMP search: Signal and background modeling and statistical inference[J]. Physical Review D, 2025, 111: 103040. DOI: [10.1103/PhysRevD.111.103040](https://doi.org/10.1103/PhysRevD.111.103040). 实际提取 [arXiv:2406.13638v1](https://arxiv.org/abs/2406.13638v1), 2024-06-19，第 6 页 Fig.3 右下图；期刊版为后续版本，不替换本次所用曲线。

[本地直接出处](<../../../../references/Solar_CEvNS/2406.13638v1.pdf>)；登记SHA256 `139f039b7ee5a957fd3594ac2301e9e8cd3a6dbcd4f63f4a6e87e02c06da71fc`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R08"></a>

**[R08]** XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`；Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本；SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。

[本地直接出处](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)；登记SHA256 `f4886dda96ea6ac43aea547b3553cee27484362d37763db33aa07869047f1a74`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R09"></a>

**[R09]** NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。

[本地直接出处](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)；登记SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R10"></a>

**[R10]** PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。

[本地直接出处](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)；登记SHA256 `41f5759ba79120fbe49a1903255487cfbfc70e5185ce34c6995b2b854faf9ba8`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R11"></a>

**[R11]** ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。

[本地直接出处](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)；登记SHA256 `37170328542fc9b6c645bab732d2e269b014ad22a6e86b9b47e7428a9840d8e1`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R12"></a>

**[R12]** APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26；文献 [1] 的背景关联来源 [72]。

[本地直接出处](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)；登记SHA256 `011d164e7aa009c9cd95a398fa7bebb7436f3ff48abb8f869e62398f76770aff`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R13"></a>

**[R13]** BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。

核验范围：BIPM第9版V4.01，§2.2/Table1在线原文已核。未缓存该PDF

<a id="ref-R14"></a>

**[R14]** APRILE E, et al. (XENON Collaboration). Probing the Solar ⁸B Neutrino Fog with XENONnT[J]. Physical Review Letters, 2026, 137: 091807. DOI: [10.1103/xvpn-w3q9](https://doi.org/10.1103/xvpn-w3q9). 本库保存 [arXiv:2604.06002v2](https://arxiv.org/abs/2604.06002v2), 2026-08-28。文献 [8] README 指定它为后续数据与模板的关联论文；本任务只提取 SR0/SR1 候选，不纳入 SR2。

[本地直接出处](<../../../../references/Solar_CEvNS/2604.06002v2.pdf>)；登记SHA256 `a6a81a7fd423a3005152c02dcd45f93a444dc9c85c92d098a9f0f58db96917a4`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R15"></a>

**[R15]** CEvNS-pyEFT共享模型登记[CP/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `1d03f7e0136be69c7d8c12324eb4e26c1c0c6093496efc7c19bfd77f9f1bcf24`。

[本地直接出处](<../../../../../cevns_pyeft/experiments/model_bindings.json>)；登记SHA256 `1d03f7e0136be69c7d8c12324eb4e26c1c0c6093496efc7c19bfd77f9f1bcf24`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R16"></a>

**[R16]** 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。

[本地直接出处](<../../../../../data/responses/responses_all.json>)；登记SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R17"></a>

**[R17]** XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。

[本地直接出处](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)；登记SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。

核验范围：精确数值核验范围按P01与对应章节登记

<a id="ref-R18"></a>

**[R18]** CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。

[本地直接出处](<../../../../../cevns_pyeft/foundation/constants.py>)；登记SHA256 `0bb51033d1ca64e18a7a7bb0fd4cce38bc679558dd7392740f72d4683276cd44`。

核验范围：实际使用G_F、AMU_GEV、m_e、HBARC_GEV_FM、GEV_INV2_TO_CM2、SEC_PER_YEAR；数值由参数卡固定并与本地模块核对。

<a id="ref-R19"></a>

**[R19]** DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012).

[本地直接出处](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)；登记SHA256 `fa667efd721844f2c59eafcb692dfd87b811e58c84dc2cc29670b091db3b8c37`。

核验范围：本地PDF原文与第5页渲染核对；仅用式(2.6),(2.10)及κ/g定义明确新矢量耦合。arXiv:2411.11749v1 p4 Eq.(10) prints C_V^2; published Eq.(2.10) defines C_V=3 A g_V^2. Adopt the published expression explicitly, without replacing v1 SM inputs.

### 旧版保留与本版责任

v2.0/v2.1的提取记录、v2.2的SM报告、v2.3的矢量报告及原图/数组均保留。旧版只作为历史，不再要求读者来回拼接；版本列表统一在本实验README中。P00/P01/P03继续拥有来源、证据和配置权威；v3.0的输出映射另登记，不将文档整理当作新增科学批准。

[返回目录](#report-toc)

<a id="equation-index"></a>

## 公式索引

| 式 | 位置 | 来源/推导性质 |
|---|---|---|
| 1 | [eq-flux](#eq-flux) | R01 PDF p5式(11)及后文；R04官网b8spectrum.txt列1–4。总量×谱形为项目对输入的显式分解。 |
| 2 | [eq-inventory](#eq-inventory) | 项目按R09全部九种天然Xe中心值及R13 SI阿伏伽德罗常量推导；10⁶为g/t换算。 |
| 3 | [eq-response](#eq-response) | 项目对R17原HDF5接受后四维箱概率的精确边际化；原单能模板与utils.py::Template.interpolator。 |
| 4 | [eq-interpolation](#eq-interpolation) | R17 utils.py::Template.interpolator的三线性内插；当前实现为RegularGridInterpolator(method=linear)，不是任意平滑。 |
| 5 | [eq-prediction](#eq-prediction) | 项目对R01式(11)–(13)采用Response后的实验侧折叠；Source、核数、截面、选择和曝光各一次。 |
| 6 | [eq-mean-counts](#eq-mean-counts) | 项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。 |
| 7 | [eq-deviance](#eq-deviance) | R01 PDF p6式(17)及后文；零观测的Dlog项取连续极限0。当前只记录合同，无minimizer结果。 |

[返回目录](#report-toc)

<a id="parameter-index"></a>

## 参数/数组索引

| 精确ID/数组键 | 正文位置 | 输入权威 |
|---|---|---|
| `source.total_flux` | [source](#source) | 正式YAML；本版对应章已列值、单位、出处 |
| `target.anchor_mass_kg` | [target](#target) | 正式YAML；本版对应章已列值、单位、出处 |
| `target.Z` | [target](#target) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.avogadro` | [target](#target) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.amu_GeV` | [target](#target) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.electron_mass_GeV` | [target](#target) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.G_F` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.hbarc_GeV_fm` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.GeV_inverse2_to_cm2` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `constants.seconds_per_year` | [prediction](#prediction) | 正式YAML；本版对应章已列值、单位、出处 |
| `nuclear.radius_fm` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `nuclear.skin_fm` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `interaction.sin2thetaW` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `interaction.include_sm` | [modules](#modules) | 正式YAML；本版对应章已列值、单位、出处 |
| `numerics.n_er` | [prediction](#prediction) | 正式YAML；本版对应章已列值、单位、出处 |
| `numerics.n_enu` | [prediction](#prediction) | 正式YAML；本版对应章已列值、单位、出处 |
| `source_energy_MeV` | [第2章Source](#source) | 正式NPZ；第9章完整索引 |
| `source_shape_per_MeV` | [第2章Source](#source) | 正式NPZ；第9章完整索引 |
| `target_mass_number` | [第3章Target](#target) | 正式NPZ；第9章完整索引 |
| `target_atomic_mass_u` | [第3章Target](#target) | 正式NPZ；第9章完整索引 |
| `target_number_fraction` | [第3章Target](#target) | 正式NPZ；第9章完整索引 |
| `run_exposures_tyr` | [第3章Target](#target) | 正式NPZ；第9章完整索引 |
| `response_energy_keV` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `response_Ly` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `response_Qy` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `response_SR0` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `cs2_edges_SR0` | [第6章Observable](#observable) | 正式NPZ；第9章完整索引 |
| `response_SR1` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `cs2_edges_SR1` | [第6章Observable](#observable) | 正式NPZ；第9章完整索引 |
| `yield_energy_keV` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `yield_Ly_median` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `yield_Qy_median` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `observable_edges` | [第6章Observable](#observable) | 正式NPZ；第9章完整索引 |

[返回目录](#report-toc)
