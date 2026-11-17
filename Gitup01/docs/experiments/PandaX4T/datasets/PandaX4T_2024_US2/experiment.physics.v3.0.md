# PandaX4T_2024_US2 — onboarding v3.0 完整整合版

**2026-11-10修订。新增SM简化八箱实际计算；完整Response与严格论文等价性仍待补，科学接受NOT_REVIEWED。**

[详细版v3.0](<experiment.physics.v3.0.md>) · [精简版v3.0](<experiment.physics.summary.v3.0.md>) · [用户资料v3.0](<EXPERIMENT_USER_INPUT.v3.0.md>) · [两实验完整总文档](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P01_EVIDENCE_LEDGER.yaml>) · [P02当前缺口](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P02_MISSING_AND_CONFLICTS.md>) · [P03配置](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P03_PHYSICS_CONTRACT.yaml>) · [机器标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) · [完整数组](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) · [V/B−L Benchmark卡](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>) · [文档整合验收](<../../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/README.md>) · [简化SM参数卡](<../../../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>) · [简化八箱结果与图](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>)

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

原Response路线已实现SM与V/B−L真实反冲投影；2026-11-10按用户要求新增SM简化平均映射八箱谱。**完整US2逐Ne箱概率核仍MISSING，简化谱已实际计算。**

| 对象/目标 | 采用范围 | 当前能力 |
|---|---|---|
| 数据身份 | PandaX4T_2024_US2 | 同一dataset；不新增采集期或默认全局激活 |
| 物理benchmark | R01 arXiv:2411.11749v1 SM；R19正式期刊V/B−L定义 | 固定点前向谱完成；本轮未计算Fig.2拟合或Fig.4排除线 |
| 方法 | Source→Target→共享截面→完整选后箱概率→counts；PandaX另有显式均值映射简化分支 | SSM通量固定；简化c=1是直接预测，后验拟合谱缩放只作参考 |
| 审核状态 | 文档整合完成；科学结果Human=NOT_REVIEWED | 机器PASS不代替科学接受；PARTIAL能力逐项列于第10章 |

机器输入权威为[正式YAML](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>)与[正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>)；当前人读说明为本版。旧Compiler派生MD保留，不把旧模板的“靶未绑定”等通用文字当作当前实际数组/执行状态。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)


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

物质数使用原子质量；运动学使用 `m_kin[GeV]=atomic_mass[u]×amu_GeV−54×m_e[GeV]`，忽略电子结合能。计算中的1000kg和31557600s是代数归一化锚点，不是虚构实测质量/活时间。现代SI下将u数值当g/mol是明确的摩尔质量常量近似，未称为精确恒等。

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
| Detector | `recoil_efficiency_projection_v1` | 探测器Response独立于Nuclear Structure；具体数学定义见第5章 |

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `interaction.sin2thetaW` | 0.23857 | 1 | R01；2411.11749v1 PDF p3 Eq.(2)后参考弱混合角 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `interaction.include_sm` | True | boolean | 项目配置选择；不是文献测量；本轮用户指定纯标准模型，不扫描BSM | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `nuclear.radius_fm` | 1.23 | fm | R01；2411.11749v1 PDF p3 Eq.(3)后：R_A=1.23 A^(1/3) fm | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `nuclear.skin_fm` | 0.7 | fm | R01；同上，a_k=0.7 fm | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.G_F` | 1.1663787e-05 | GeV^-2 | R18；foundation/constants.py::G_F | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.hbarc_GeV_fm` | 0.1973269804 | GeV fm | R18；foundation/constants.py::HBARC_GEV_FM | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `constants.GeV_inverse2_to_cm2` | 3.893793721e-28 | cm^2 GeV^2 | R18；foundation/constants.py::GEV_INV2_TO_CM2；微分截面另乘1e-6转成每keV | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |

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

[返回目录](#report-toc)

<a id="observable"></a>

## 6. Observable、完整分箱与观测身份

| 能力/坐标 | 完整边界 | 采用状态与出处 |
|---|---|---|
| 目标Ne谱 | [4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8] | electron；R01式(12)后与R02 Fig.5；信号P(Ne箱\|T) MISSING |
| 当前真实反冲投影 | [0.299999999496, 0.399999999496, 0.499999999496, 0.599999999496, 0.699999999497, 0.799999999497, 0.899999999497, 0.999999999497, 1.0999999995, 1.1999999995, 1.2999999995, 1.3999999995, 1.4999999995, 1.5999999995, 1.6999999995, 1.7999999995, 1.8999999995, 1.9999999995, 2.0999999995, 2.1999999995, 2.2999999995, 2.3999999995, 2.4999999995, 2.5999999995, 2.6999999995, 2.7999999995, 2.8999999995, 2.9999999995] | keVnr；27箱项目输出选择，完整值来自正式NPZ；已含ROI选取，横轴仍为T，未分配Ne箱 |

原实验Fig.5观测八箱D=[73, 44, 29, 44, 41, 38, 28, 35]，合计332；后续官方事件CSV只用于核对，不凭相同一维计数认证2024完整事件ID。width的µs单位关联R11后续论文，原CSV表头未独立编码单位。

### 本章参考文献与核验范围

- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R11] ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)

[返回目录](#report-toc)

<a id="prediction"></a>

## 7. Prediction folding、执行结果与复算

<a id="eq-prediction"></a>

$$
N_j^{\rm diag}=\mathcal E t_{\rm yr}\sum_A n_A^{(t)}\int_{T_j}^{T_{j+1}}dT\,\epsilon_{\rm US2}(T)\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT} \tag{6}
$$

公式依据：项目真实反冲接受度投影；R02 Fig.1接受度与既有Source/Target/共享截面。不是R01 Ne事件数公式的已实现替代。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $\mathcal E_r$或$\mathcal E$ | 已取得；具体曝光见第3章 | t·yr | R17或R02；参考年注量×参考吨核数×曝光/anchor_tonne |
| $t_{\rm yr}$ | 31557600；每年秒数只施加一次 | s/yr | R18 SEC_PER_YEAR=365.25×86400；单位约定 |
| $n_A^{(t)}$ | 已由九核素中心值推导 | nuclei/t | 第3章核数表 |
| $d\sigma_A/dT$ | 已存在的共享SM或V/B−L组件输出 | cm²/keVnr | 第4章模块/参数；不把核数或效率放进截面 |
| $\epsilon_{\rm US2}$ | 已取得边际总接受度；Ne概率仍MISSING | 1 | 第5章实际数值与有效域 |
| $N_j^{\rm diag}$ | 项目派生真实反冲诊断事件数 | events/bin | 当前已执行的数值结果如下 |

完整Response路线直接在真实T上积分，不使用1/Qy代替能量相关均值映射的Jacobian，也不把均值转换当作概率迁移。

| 输入/配置 | 实际值 | 单位 | 直接出处/处理性质 | 本地文件 |
|---|---|---|---|---|
| `constants.seconds_per_year` | 31557600 | s/yr | R18；365.25×86400=31557600；计算单位约定，不是额外活时间 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `numerics.n_er` | 401 | 1 | 项目配置选择；不是文献测量；Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |
| `numerics.n_enu` | 240 | 1 | 项目配置选择；不是文献测量；Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 | [实际标量卡](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) |

上表401/240为正式包默认基础节点；已保存benchmark显式覆盖为T=201/401/801、Eν=120/480并分别加密，另并入原源谱、响应、产额与输出箱断点。积分为共享recoil/folding的梯形求积；预定逐箱条件max(2×10⁻⁴ events,0.2%)，两种维度分别检查。不能只凭一个相对差异超过0.2%就忽略其绝对容差条件。

<a id="benchmark-results"></a>

| 点 | m[MeV] | g | κ | 信号/投影总量[events] |
|---|---|---|---|---|
| SM | — | 0 | — | 47.026752801 |
| V10_g1 | 10 | 1e-05 | 1 | 29.508388184 |
| V10_g2 | 10 | 2e-05 | 1 | 3.306022173 |
| V10_g3 | 10 | 3e-05 | 1 | 47.477838291 |
| BL10_g2 | 10 | 2e-05 | −1/3 | 77.216760990 |
| V1_g2 | 1 | 2e-05 | 1 | 16.804273790 |
| V100_g2 | 100 | 2e-05 | 1 | 44.708924779 |

**非零m/g数值是项目选取的测试点，不是论文最佳拟合或排除界；κ与耦合定义来自R19。** 直接采用卡：[全部测试点、值的性质与固定输入哈希](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>)。SM总数与上一轮逐箱一致；所有核素、run和逐箱数组已保存。

**上述历史数字是约0.3–3keVnr域内、含ROI的信号总量估计及真实T分布；原V/B−L运行尚无八箱Ne预测。** 新增的SM八箱简化计算如下，不能把不同方法、通量或拟合点的总数直接当同条件复现比。

干涉分解的和允许含负项，完整逐箱表：

| 点 | SM总量 | 干涉项 | 纯NP项 | 闭合最大误差[events] |
|---|---|---|---|---|
| V10_g1 | 47.026752801 | -19.714425270 | 2.196060653 | 1.33e-15 |
| V10_g2 | 47.026752801 | -78.857701082 | 35.136970454 | 1.3e-15 |
| V10_g3 | 47.026752801 | -177.429827434 | 177.880912924 | 1.78e-15 |
| BL10_g2 | 47.026752801 | 26.285900361 | 3.904107828 | 1.78e-15 |
| V1_g2 | 47.026752801 | -122.632538799 | 92.410059789 | 4.88e-15 |
| V100_g2 | 47.026752801 | -2.347120962 | 0.029292941 | 8.88e-16 |

依据为共享矢量振幅的有符号分解及逐核素真实反冲重权重后独立折叠；它是内部解析闭合检验，不是外部非零点模板复现。

### SM前向图

![SM前向图](<../../../../../outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/events.png>)

### V/B−L前向图

![V/B−L前向图](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/events.png>)

| 实际结果/复算 | 入口 |
|---|---|
| SM逐箱、run/核素分量、收敛、参数指纹 | [SM_RESULT.json](<../../../../../outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/SM_RESULT.json>) |
| V/B−L全部点、分解及逐箱数组 | [DATASET_RESULT.json](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/DATASET_RESULT.json>) · [全部逐箱TSV](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/counts_by_point.tsv>) |
| SM复算 | `python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run` |
| V/B−L复算 | `python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/repeat_run` |

标准API可直接运行（以下为本实验路径）：

```python
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector
from cevns_pyeft.experiments.runtime import predict_experiment
sm = load_experiment_package("data/experiments/PandaX4T/PandaX4T_2024_US2")
vector = with_solar_light_vector(sm, mass_MeV=10., coupling=2e-5, scenario="universal")
result = predict_experiment(vector, numerics={"n_er": 801, "n_enu": 480})
print(result.counts)
```

PandaX路径的返回量始终是keVnr投影；更换interaction不会凭空补出电子数Response。

### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

### 2026-11-10：SM简化平均映射八箱结果

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)

| Ne箱 | 映射T[keVnr] | 固定SSM直接SM [events] | 拟合谱×0.65参考 [events] | 历史经验比值（非独立校准） |
|---|---|---|---|---|
| 4–4.5 | 0.660084–0.723217 | 3.602399 | 9.047034 | 2.511391 |
| 4.5–5 | 0.723217–0.787021 | 3.720839 | 8.012209 | 2.153334 |
| 5–5.5 | 0.787021–0.851621 | 3.697757 | 7.027383 | 1.900444 |
| 5.5–6 | 0.851621–0.917067 | 3.557139 | 6.281344 | 1.765842 |
| 6–6.5 | 0.917067–0.983360 | 3.307608 | 5.523747 | 1.670013 |
| 6.5–7 | 0.983360–1.050465 | 3.001446 | 4.831426 | 1.609699 |
| 7–7.5 | 1.050465–1.118330 | 2.661998 | 4.300064 | 1.615352 |
| 7.5–8 | 1.118330–1.186893 | 2.302490 | 3.631125 | 1.577043 |

同轮完整已提取接受度T域积分为47.026765事例；平均映射窗口以下/以上为11.707919/9.467170事例。这量化了用含ROI的总接受度再作均值窗口裁剪的近似损失；未强制重归一化。完整Response路线继续保留，不能用此简化结果声称已取得概率迁移核。

![本轮实际八箱计算](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events.png>)

复算：`python -B tools/run_pandax_us2_simplified_benchmark.py --output outputs/solar_b8_sm/repeat_simplified`。标准Runtime仍负责源、靶、SM和直接反冲积分，新局部适配器只负责逆映射与连续T区间积分。两种Qy曲线均分别检查T和Eν收敛。

[返回目录](#report-toc)

<a id="statistics"></a>

## 8. Statistics、观测与背景的来源和适用范围

**已执行的是固定点前向预测与观测/名义背景作图；统计evaluator、χ²最小化、置信区间未实现/未运行。** 下列R01统计合同作为后续明确依据保留，不因公式写出就声称统计能力已完成。

<a id="eq-mean-counts"></a>

$$
\mu_i=(1+\alpha)(1+\beta_s)S_i(\theta)+\sum_k(1+\beta_k)B_i^k \tag{7}
$$

公式依据：项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。

| 符号/输入 | 定义、值或取得情况 | 单位 | 具体依据/依赖 |
|---|---|---|---|
| $D_i$ | 观测计数已有；原始身份/当前范围见下表 | events/bin | 不是背景扣除残差 |
| $S_i$ | Ne重建信号MISSING；当前T投影不能代入 | events/bin | 第7章相应能力 |
| $B_i^k$ | 拟合/参考投影已有，原prefit形状另待补 | events/bin | 下表严格区分来源版本与用途 |
| $\alpha,\beta_s,\beta_k$ | 定义的统计归一化nuisance；本轮未profile | 1 | R01 PDF p6式(17)后；σ按单独模型表采用 |

<a id="eq-deviance"></a>

$$
\chi^2_{\rm prof}=\min_{\alpha,\boldsymbol\beta}\left[2\sum_i\left(\mu_i-D_i+D_i\ln\frac{D_i}{\mu_i}\right)+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\sum_k\left(\frac{\beta_k}{\sigma_k}\right)^2\right] \tag{8}
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

正式Runtime数值权威是每实验YAML+NPZ。下列目录同时保存原始摘录、转换结果、候选与对照；“本地有文件”和“用于本轮计算”分别列出。完整哈希/原文件到正式键的关系见[本轮机器可读资源与溯源清单](<../../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/NUMERICAL_INVENTORY.json>)。

### 正式包全部数组索引

| 键 | shape | 单位 | 本版详细定义/数值所在章 | 完整文件 |
|---|---|---|---|---|
| `source_energy_MeV` | [829] | MeV | [第2章Source](#source) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `source_shape_per_MeV` | [829] | MeV^-1 | [第2章Source](#source) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_mass_number` | [9] | 1 | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_atomic_mass_u` | [9] | u | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `target_number_fraction` | [9] | 1 | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `run_exposures_tyr` | [1] | t yr | [第3章Target](#target) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `efficiency_energy_keV` | [99] | keVnr | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `efficiency` | [99] | 1 | [第5章Detector](#detector) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |
| `observable_edges` | [28] | keVnr | [第6章Observable](#observable) | [正式NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) |

### 全部辅助数值文件：出处、处理和当前用途

| 文件/claim | 数值覆盖 | 单位 | 直接出处及转换 | 本轮用途/限制 |
|---|---|---|---|---|
| [pandax_qy_nominal.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) `PandaX4T-C001` | [36, 2]，各列范围：[0.2, 3.1]; [2.291009926, 6.829535124] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; Nominal dashed line；PDF vector digitization; logarithmic energy; no gain/efficiency/exposure | 2026-11-10简化平均映射主输入；不是完整Ne迁移概率 |
| [pandax_qy_bestfit.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_bestfit.txt>) `PandaX4T-C002` | [37, 2]，各列范围：[0.2, 3.1]; [4.422195042, 7.470914283] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; Best-fit solid line；joint paired+US2 fitted mean; not US2-only calibration | 简化平均映射的best-fit产额敏感性对照；非独立标定 |
| [pandax_qy_nominal_band.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal_band.txt>) `PandaX4T-C003` | [119, 3]，各列范围：[0.2018500125, 3.055123576]; [0.1202865379, 6.196027928]; [4.518662938, 7.491408703] | column1 keVnr, Qy columns electron/keV, visibility/line-style flags dimensionless | R02；2407.10892v3 PDF p5 Fig.4 lower; same figure; nominal gray +/-1 sigma band；PDF vector band; no covariance inferred | Qy包络参考；未提供Ne迁移概率或联合协方差 |
| [pandax_original_fig5.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_original_fig5.txt>) `PandaX4T-C004` | [8, 7]，各列范围：[1, 8]; [4, 7.5]; [4.5, 8]; [28, 73]; [20.83561346, 31.2185977]; [0.2224757103, 34.093572]; [5.586346254, 13.91851412] | D/background/reference signal events/bin, coordinate columns as declared | R02；2407.10892v3 PDF p6 Fig.5 upper, 4<=Ne<8；D integers; fitted stacked components separated by polygon thickness | 图线拟合/参考投影；非独立prefit背景 |
| [pandax_benchmark_fig1.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt>) `PandaX4T-C005` | [8, 7]，各列范围：[1, 8]; [4, 7.5]; [4.5, 8]; [28, 73]; [20.16574585, 30.44198894]; [0.1657458514, 33.97790043]; [5.687951539, 13.81782768] | D/background/reference signal events/bin, coordinate columns as declared | R01；2411.11749v1 PDF p7 Fig.1 left；benchmark reference components; not independent prefit B | 图线拟合/参考投影；非独立prefit背景 |
| [b8_bahcall1996_official.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) `PandaX4T-C006` | [829, 4]，各列范围：[0, 16.56]; [0, 0.1321716]; [0, 0.1339827]; [0, 0.1304072] | MeV; MeV^-1 | R04；official b8spectrum.txt, all four columns；byte-identical download | 本轮前向输入的直接来源，已封入正式NPZ |
| [xenon_natural_isotopes_nist_v2.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) `PandaX4T-C007` | [9, 3]，各列范围：[124, 136]; [123.905892, 135.907214484]; [0.00089, 0.269086] | 1; u; 1 | R09；Xe rows 124,126,128,129,130,131,132,134,136；parsed central values; uncertainties retained in official source download, not treated as zero | 本轮前向输入的直接来源，已封入正式NPZ |
| [pandax_official_later_run0_events.csv](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run0_events.csv>) `PandaX4T-C008` | 158行；Ne, Width | electron; Width unit follows associated paper, not encoded in CSV header | R10；p4-light-dark-matter/run0_data.csv；byte-identical download | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_official_later_run1_events.csv](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run1_events.csv>) `PandaX4T-C009` | 174行；Ne, Width | electron; Width unit follows associated paper, not encoded in CSV header | R10；p4-light-dark-matter/run1_data.csv；byte-identical download | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_official_later_run_bins_v2.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run_bins_v2.txt>) `PandaX4T-C010` | [16, 5]，各列范围：[0, 1]; [1, 8]; [4, 7.5]; [4.5, 8]; [14, 38] | 1; 1; electron; electron; events/bin | R10；two event CSV; 0.5-electron bins in [4,8]；numpy.histogram by run | 后续259日事件参考；2024完整事件身份未认证 |
| [pandax_response_calibration_2403.04239v2.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>) `PandaX4T-C011` | 10条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R06；2403.04239v2 p21 Table II；manual transcription with visual check | 通用标定参考；非US2 sub-keV完整响应 |
| [pandax_us2_rate_uncertainties_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_us2_rate_uncertainties_2024.v2.1.json>) `PandaX4T-C026` | 8条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R02；2407.10892v3 PDF p5 Table IV, US2 columns；transcribed printed primary-source values | 原2024总数/率误差参考；完整形状另需取得 |
| [pandax_us2_acceptance_2407.10892v3.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>) `PandaX4T-C029` | [99, 2]，各列范围：[0.299999999496, 2.9999999995]; [0.00579130467031, 0.191620952606] | as declared per column/key in the numerical file and chapter | R02；2407.10892v3 PDF p3 Fig.1, black dashed Total(US2), PDF curve index9；native PDF vertices calibrated to linear energy/log efficiency; edge intersections in PDF coordinates | 本轮前向输入的直接来源，已封入正式NPZ |
| [pandax_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_prefit_inputs_2024.v2.1.json>) `PandaX4T-C030` | 10条标量及原误差 | per scalar parameter, explicitly declared in the JSON | R02；2407.10892v3 PDF p4 Table III, US2 Run0/Run1 expectation；transcription of printed prefit totals and uncertainties | 原2024总数/率误差参考；完整形状另需取得 |

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
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R06] LUO Y, BO Z, ZHANG S, et al. (PandaX Collaboration). Signal response model in PandaX-4T[J]. Physical Review D, 2024, 110: 023029. DOI: [10.1103/PhysRevD.110.023029](https://doi.org/10.1103/PhysRevD.110.023029). 实际提取 [arXiv:2403.04239v2](https://arxiv.org/abs/2403.04239v2), 2024-03-08，第 21 页 Table II；本文 NR 拟合适用范围不能外推冒充 US2 sub-keV 校准。 [本地直接采用源](<../../../../references/Solar_CEvNS/2403.04239v2.pdf>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R10] PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)；[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件；属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- [R16] 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [本地直接采用源](<../../../../../data/responses/responses_all.json>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本地直接采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

[返回目录](#report-toc)

<a id="status"></a>

## 10. 缺失、交接、验证与完整参考文献

本版对已运行SM/V/B−L和待补能力分别给出状态；未把过时“无响应/未绑定”或候选模型当作当前事实。

| 下一步能力 | 当前状态 | 具体需要什么/阻断范围 |
|---|---|---|
| 当前SM/V/B−L真实反冲投影 | 可运行；ROI选后总量估计及T分布；缺Ne箱分配 | 可见T域内无新增必需数据；域外贡献待核，保留1.04t·yr合计曝光 |
| PandaX SM简化Ne八箱谱 | SSM通量固定、c=1直接预测；后验拟合谱仅作参考 | 严格作者等价性仍需原c_i及全套拟合点；参考谱缩放不提供独立验证 |
| PandaX完整Response Ne谱 | **BLOCKED / MISSING** | 2024 US2的P(Ne箱\|T)，或能生成它的完整低能响应与选择配置；简化谱不解决该缺口 |
| PandaX逐run预测/原生2D likelihood | 部分输入已有，能力仍待补 | afterglow veto后逐run有效曝光；width完整边界、prefit背景形状及约束/相关性 |
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

2026-11-10简化分支：10项相关测试通过；nominal与best-fit均独立加密T/Eν收敛，量化全T域与平均窗口的差值；作者c_i与nuisance点等价性不在机器PASS的认证范围。[本轮实际结果和验收](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/README.md>)。

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
| 3 | [eq-mean-yield](#eq-mean-yield) | R01 PDF p6式(15)；Qy曲线实际来自R02 PDF p5 Fig.4下图。本式只定义均值，不提供迁移核。 |
| 4 | [eq-response](#eq-response) | 项目对“通过选择并进入Ne箱”的概率定义；R02原生Ne/width分析沿width边际化到本次一维目标。 |
| 5 | [eq-simplified-counts](#eq-simplified-counts) | R01 PDF p5式(11)–(13)、p6式(15)；dR/dT含源、靶核数、SM与R02 Fig.1总接受度。此式为c_i=1的项目基线。 |
| 6 | [eq-prediction](#eq-prediction) | 项目真实反冲接受度投影；R02 Fig.1接受度与既有Source/Target/共享截面。不是R01 Ne事件数公式的已实现替代。 |
| 7 | [eq-mean-counts](#eq-mean-counts) | 项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。 |
| 8 | [eq-deviance](#eq-deviance) | R01 PDF p6式(17)及后文；零观测的Dlog项取连续极限0。当前只记录合同，无minimizer结果。 |

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
| `efficiency_energy_keV` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `efficiency` | [第5章Detector](#detector) | 正式NPZ；第9章完整索引 |
| `observable_edges` | [第6章Observable](#observable) | 正式NPZ；第9章完整索引 |

[返回目录](#report-toc)
