# CsI2021 标准模型事例数基准计算

当前复算默认采用项目内time_resolved_common及最新24点输入，见[METHODS.md](METHODS.md)。下文旧环境、绝对路径与代码指纹是原运行的历史证据；本次路径本地化的等价核对见[整理记录](../../../../../outputs/latest_layout_20261111/README.md)。

2026-11-07，Asia/Shanghai。**数值前向计算已通过本轮检查；严格论文复现未认证。** 本次为用户请求的未拟合SM点，不构建BSM扫描或把结果自动冻结为下游Fast权威。

[配置与逐项来源](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/SM_CONFIG.json>) · [归一化台账](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/NORMALIZATION_LEDGER.json>) · [机器验收](<../../../../../outputs/csi2021_time_sm_20261107/VALIDATION_RESULTS.json>) · [99箱CSV](<../../../../../outputs/csi2021_time_sm_20261107/events_99bins.csv>) · [完整数组](<../../../../../outputs/csi2021_time_sm_20261107/benchmark.npz>) · [P00](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml>) · [P01](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P01_EVIDENCE_LEDGER.yaml>) · [P03](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P03_PHYSICS_CONTRACT.yaml>)

<a id="report-toc"></a>

## 目录

- [实际调用与主线状态](#scope)
- [采用输入及出处](#inputs)
- [事例数与分量](#counts)
- [数值和运行验收](#validation)
- [图表与逐箱输出](#figures)
- [与论文比较的限制](#limits)
- [复算命令与文件归属](#reproduce)

<a id="scope"></a>

## 实际调用与主线状态

规范和r2来源记录已写入原主项目。主项目通用predict目前只支持一维观测；本轮用它计算PE信号，再显式复用旧目录time_profile/time_acceptance得到时间分箱，未宣称生产Runtime已原生支持二维likelihood。

执行的是validation_only请求，采用P06/P07的归一化、源/核素分量和独立积分检查。代码链为：[本轮入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py>) → [主项目predict](<../../../../../cevns_pyeft/core/predict.py>) → [原生SM/RESPONSE适配器](<../../../../../cevns_pyeft/theory/li2026/adapter.py>) → 既有时间权重。原Runtime、原核表、注册和冻结参考未改。

[返回目录](#report-toc)

<a id="inputs"></a>

## 采用输入及出处

| 输入 | 实际值 | 单位 | 直接来源及定位 |
|---|---|---|---|
| 累计POT `C_POT` | 3.198e+23 | POT | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines76–81 |
| 每味每POT产额 `C_YIELD` | 0.0848 | neutrinos/flavor/POT | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines78–81；10%误差 |
| 基线 `C_L` | 19.3 | m | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines78–81 |
| 几何稀释后的每味积分注量 `C_ETA` | 579361763793233.9 | cm^-2 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>)；p12 Eq29后归一化；prepare_records.py eta表达式 |
| 论文探测器质量 `C_MASS` | 14.6 | kg | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 line81；2211 p12 Eq28段落 |
| Cs/I化学计量 `C_STOICH` | [1, 1] | number ratio | [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；CsI[Na]靶身份；p12 Eq28后靶核计数定义 |
| muon质量 `C_MMU` | 105.6583755 | MeV | [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>)；allascii line223 |
| 带电pion质量 `C_MPI` | 139.57039 | MeV | [S_PDG](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf>)；PDF/印刷p1 OUR FIT；误差0.00018MeV |
| prompt谱线能量 `C_LINE` | 29.792140909877446 | MeV | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>)；p12 Eq29；两体衰变公式 |
| 论文DAR能谱上限 `C_ENDPOINT` | 52.82918775 | MeV | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；p12 Eqs28–29，m_mu/2近似 |
| 2211名义弱混合角 `C_SIN2_PAPER` | 0.23857 | 1 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；p3 Sec2.1 Eqs1–3后说明，原文误差(5) |
| nominal淬灭多项式系数 `C_QF` | [0.0554628, 4.30681, -111.707, 840.384] | [1,MeV^-1,MeV^-2,MeV^-3] | [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee |
| QF拟合适用域 `C_QF_DOMAIN` | [2, 70] | keVnr | [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>)；Sec8，PDF p23/印刷p21 Fitting approach |
| 光产额 `C_LY` | 13.35 | PE/keVee | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；p3 lines90–93 |
| Gamma展宽参数 `C_GAMMA` | {"a_numerator": 0.0749, "b_slope": 9.56} | a=0.0749/Eee(keVee); b=9.56*Eee(keVee) | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；Supplement p3 Eq3 lines94–101；2211 p12 Eq31 |
| 官方nominal能量效率系数 `C_EFF` | [1.32045, 0.285979, 10.8646, -0.333322] | a,d dimensionless; b PE^-1; c PE | [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>)；effCoefficients.txt line7，公式与x=PE见头部line1–4 |
| 时间效率转折及衰减 `C_TIME_EFF` | [0.52, 0.0494] | [us,us^-1] | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；Supplement p2 Eq1 lines64–68；2211 p13 Eq33 |
| PE边界 `C_PE` | [0.0, 8.0, 12.0, 16.0, 20.0, 24.0, 32.0, 40.0, 48.0, 60.0] | PE | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；D_PE；Supplement p5 Fig2水平误差棒 |
| 时间边界 `C_TIME` | [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 2.0, 4.0, 6.0] | us | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；p35 Fig18全部十一面板标签 |
| 端点归箱规则 `C_ENDPOINT_RULE` | 每箱左闭右开，PE60及t6us排除 | 1 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>)；统一端点的用户要求；histogram筛选实现 |
| 实际调用资源与核素映射 `C_RESOURCE_BINDING` | {"path": "data/responses/responses_all.json", "reader": "cevns_pyeft.nuclear.response.ResponseDB", "nucleus_keys": {"Cs133": "Cs133", "I127": "I"}} | 1 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>)；原JSON nuclei.Cs133和nuclei.I；D_LOCAL_RESPONSE |
| 源表示选择 `C_SOURCE_CHOICE` | DAR解析谱 × ROOT各味时间边缘 | 1 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>)；p12 Eq29、p13 Eq32；D_REUSE |
| 平移后的时间归一分母 `C_DENOM` | 固定零位移0–6us参考分数 | 1 | [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>)；time_acceptance.build_time_weights的nominal参考分数；论文p13脚注8未给完整程序细节 |
| 反冲积分域保护 `C_RECOIL_POLICY` | [2, 70] | keVnr | [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) · [S_DOMAIN_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/analysis_inputs.py>)；校准Sec8；analysis_inputs.py guards；DAR上界还受运动学约束 |
| 官方背景总数prior `C_PRIORS` | [18.4, 5.6, 1286] | events for BRN,NIN,SS | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；p7 TableI Prior Prediction |

核响应仍直接调用原JSON，Cs133/I共16个通道数组；[原数值与基底/单位的详细核对](<experiment.physics.md>)及[本轮资源审计](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/RESOURCE_AUDIT.json>)保留实际数组、哈希与核素映射。

原生SM采用项目 `_sm_left_dim6` 的vector及axial项，额外Wilson系数为空。实际矩阵、GF/质量常数和完整native LEC数值保存在SM_CONFIG和最细网格report。直接实施依据为[SM系数定义](<../../../../../cevns_pyeft/rates/differential.py>)、[常数](<../../../../../cevns_pyeft/foundation/constants.py>)与[LEC定义](<../../../../../cevns_pyeft/theory/li2026/lec.py>)；其外部原文逐项等价审计仍为r2所列PARTIAL，不把native数值可调用写成论文辐射修正已复现。

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2.。定位/核验范围：p3、p12–14、p33 Table II、p35 Fig.18 已核；[原始网址](https://arxiv.org/abs/2211.11905v2)。
- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06.。定位/核验范围：仅记录实际用户选项，不将其视作外部事实核验。
- [S_DOMAIN_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/analysis_inputs.py>) Project legacy CsI implementation, analysis_inputs.py, snapshot2026-11-06.。定位/核验范围：2–70keVnr适用域保护的直接代码，属于项目实施依据，外部科学来源另记。
- [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) CEvNS-pyEFT project, local aggregated responses_all.json, format Mu2eNRET_ResponseW_v1, original export provenance unresolved.。定位/核验范围：用户明确选择直接复用原data核表；Cs133/I八通道已读、逐值提取；现读码的单位/基底约定已核。外部作者生成链仍未核实，不是本次原表复用前置。
- [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) D. Akimov et al. (COHERENT), Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT, Phys. Rev. Lett. 129, 081801 (2022), arXiv:2110.07730v2.。定位/核验范围：版本、实验身份和测量用途已核，数值附件另登记；[原始网址](https://arxiv.org/abs/2110.07730v2)。
- [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) NIST Standard Reference Database 121, CODATA 2022 recommended values, data update May2024, allascii table.。定位/核验范围：逐常数原始行值与单位已核；[原始网址](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)。
- [S_PDG](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf>) S. Navas et al. (Particle Data Group), Review of Particle Physics, Phys. Rev. D 110, 030001 (2024), charged pion listing.。定位/核验范围：p1 pi± MASS OUR FIT 139.57039±0.00018MeV已视觉核对；[原始网址](https://pdg.lbl.gov/2024/listings/rpp2024-list-pi-plus-minus.pdf)。
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06.。定位/核验范围：本次提取/直方图/数组逐值核对算法，可重跑。
- [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) COHERENT Collaboration, Measurement of scintillation response of CsI[Na] to low-energy nuclear recoils by COHERENT, JINST 17 (2022) P10034, arXiv:2111.02477v2.。定位/核验范围：Sec.8，PDF p23/印刷p21 的2–70keV拟合域与式(8.1)已核；[原始网址](https://arxiv.org/abs/2111.02477v2)。
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary.。定位/核验范围：p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读；[原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)。
- [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) Project legacy CsI implementation, time_acceptance.py, snapshot2026-11-06.。定位/核验范围：时间形状、固定参考分母及注量转换的直接代码，属于项目实施依据，外部科学来源另记。
- [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) COHERENT Collaboration, effCoefficients.txt, arXiv:2110.07730v2 ancillary data release.。定位/核验范围：实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记；[原始网址](https://arxiv.org/src/2110.07730v2/anc/effCoefficients.txt)。
- [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) COHERENT Collaboration, scintRespCoefficients.txt, arXiv:2110.07730v2 ancillary data release.。定位/核验范围：实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记；[原始网址](https://arxiv.org/src/2110.07730v2/anc/scintRespCoefficients.txt)。


[返回目录](#report-toc)

<a id="counts"></a>

## 事例数与分量

主结果：**353.465608686 events**，PE∈[0,60)、t_rec∈[0,6)μs，源按零平移0–6μs参考窗归一化，实际QF积分从2keVnr起。相同数值eta解释为全支撑域注量时为 **329.016422597 events**；两者改变了注量范围含义，不能混称同一归一化下的模板差异。

| 入射分量 | Cs133事例 | I127事例 | 合计事例 |
|---|---:|---:|---:|
| prompt νμ | 24.650290788 | 25.882603398 | 50.532894186 |
| delayed νe | 58.338827480 | 58.464893056 | 116.803720535 |
| delayed anti-νμ | 93.304632100 | 92.824361865 | 186.128993965 |
| 总计 | 176.293750367 | 177.171858319 | 353.465608686 |

以上均由benchmark.npz的target_component_counts对分析箱求和，并非独立测量。原C/AC事件分别1578/1295；SSB为项目从控制样本推导的1285.926523987 events。

| 背景分量 | 原表直接构造，时间效率后 | 全PE表概率候选 | Supplement Table I先验 |
|---|---:|---:|---:|
| BRN | 27.423762642 | 18.309633271 | 18.4 |
| NIN | 6.908564687 | 5.178999958 | 5.6 |

背景均来自P01登记的官方PE/Trec表，算法复用TimeMassCDF；能量表已含能量效率，不重复施加。未按先验缩放任何模板。两套候选及先验不闭合，归一化问题继续保留，图中合计只作为背景诊断。

[返回目录](#report-toc)

<a id="validation"></a>

## 数值和运行验收

| nT / nEν / nPE每箱 / PE步长 | SM总数 | 与上一网格最大逐箱变化 |
|---|---:|---:|
| 128 / 240 / 64 / 0.25 | 353.476373886 | 首轮 |
| 256 / 480 / 128 / 0.125 | 353.463792396 | 0.00195514536 |
| 512 / 960 / 256 / 0.0625 | 353.465608686 | 0.00029940207 |

| 独立减半的积分轴 | 最大逐箱差/events | 门限/events | 判定 |
|---|---:|---:|---|
| recoil | 0.000126401812 | 0.005 | PASS |
| neutrino_energy | 0.00047921892 | 0.005 | PASS |
| observed_PE | 0.000268482775 | 0.005 | PASS |

本轮11组检查全部通过，范围限于该SM点：分量与投影闭合、每味注量、等核数、时间表示转换及固定分母、Gamma归一化/QF域、原生求值一致性、网格、独立折叠、实际质量×注量缩放、事件/背景回读和代码未变。[完整数值证据](<../../../../../outputs/csi2021_time_sm_20261107/VALIDATION_RESULTS.json>)保留阈值、最差箱和核验范围。原生逐能量与核验后求值的最大小网格分量误差为3.55271368e-15 events，[对照文件](<../../../../../outputs/csi2021_time_sm_20261107/NATIVE_SM_EQUIVALENCE.json>)记录实际结果。

相关既有运行测试：24项通过，0失败、0错误。[测试日志](<../../../../../outputs/csi2021_time_sm_20261107/runtime-tests.log>) / [JUnit](<../../../../../outputs/csi2021_time_sm_20261107/runtime-tests.xml>)。该结论不替代此前全局工作流尚存问题的验收。

[返回目录](#report-toc)

<a id="figures"></a>

## 图表与逐箱输出

- [PE/时间投影 PNG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_projections.png>) · [可编辑SVG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_projections.svg>)
- [11个时间窗 PNG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_time_slices.png>) · [可编辑SVG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_time_slices.svg>)
- [全部99箱 PNG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_counts_2d.png>) · [可编辑SVG](<../../../../../outputs/csi2021_time_sm_20261107/figures/sm_counts_2d.svg>)

[99箱CSV](<../../../../../outputs/csi2021_time_sm_20261107/events_99bins.csv>)、[PE投影CSV](<../../../../../outputs/csi2021_time_sm_20261107/PE_projection.csv>)、[时间投影CSV](<../../../../../outputs/csi2021_time_sm_20261107/time_projection.csv>)均给出原始箱计数。PE图及各时间窗图除以ΔPE；时间投影除以Δt；二维图是events/bin。图中数据误差棒仅为±sqrt(C)/ΔPE展示，不作为likelihood。

PNG已目视核对坐标、字号、图例、来源说明、负的背景扣除箱和窄箱显示；SVG由同一figure导出。图表源数据与文件指纹见[PLOT_MANIFEST](<../../../../../outputs/csi2021_time_sm_20261107/PLOT_MANIFEST.json>)。

[返回目录](#report-toc)

<a id="limits"></a>

## 与论文比较的限制

| 主张 | 本次结论 |
|---|---|
| 项目原生SM＋原data RESPONSE的99箱前向计算 | 数值检查通过；实际参数和核响应均可追到本地资源及原材料 |
| 2211.11905v2 Fig.18布局、数据及名义信号计算 | 已计算、已绘图；不是该文best-fit曲线 |
| 严格2211论文模型及83.2统计基准 | 未认证：原生vector/axial核与论文辐射修正/Helm模型未证明等价；半径nuisance、背景归一及拟合均未闭合 |
| JHEP2022四pull独立统计benchmark | 本轮未重做统计拟合，不用当前full-support诊断替代该benchmark |
| PE精确作者边界 | 继续标为用户指定的重建值；时间边界来自Fig.18 |
| 完整ROOT E-t联合源的等价 | 本轮选择论文解析DAR谱×ROOT时间边缘；未使用完整ROOT能谱/二维相关，也不将旧配置相关差异移称本轮已验收 |
| QF拟合域外与BSM参数域 | 未作物理预测声明；T<2keVnr贡献排除，完整ROOT高能尾及额外anti-νe不纳入当前DAR源 |

尚未闭合的问题继续见[P02](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P02_MISSING_AND_CONFLICTS.md>)。当前用户对原核表直接复用的选择已执行；外部作者导出链待核不阻断本次本地原表计算。

[返回目录](#report-toc)

<a id="reproduce"></a>

## 复算命令与文件归属

本轮计算Python：`C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1030-493-0_26.1030.493.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe`，Python 3.12.14，NumPy 2.5.4；运行时注入既有validation_deps以提供scipy/uproot。绘图使用本机conda的matplotlib，版本3.11.0。实际命令顺序与环境见[运行入口README](<../../../../../examples/COHERENT_CsI/time_resolved_sm/README.md>)及[本次输出README](<../../../../../outputs/csi2021_time_sm_20261107/README.md>)。

| 文件范围 | 所属README与消费者 |
|---|---|
| 计算/验收/绘图/汇总脚本 | [README](<../../../../../examples/COHERENT_CsI/time_resolved_sm/README.md>) |
| 原生/细化网格、CSV、NPZ、图和JUnit | [README](<../../../../../outputs/csi2021_time_sm_20261107/README.md>) |
| 本轮配置、归一化、来源审计与报告 | [README](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/README.md>) |
| 主文档中的SM报告 | [README](<README.md>) |

文件与资源SHA见[ARTIFACT_MANIFEST](<../../../../../outputs/csi2021_time_sm_20261107/ARTIFACT_MANIFEST.json>)，写入范围及原文件备份见[CHANGE_MANIFEST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/CHANGE_MANIFEST.json>)。代码快照只用于核查与恢复，不是一个自行安装或导入的替代Runtime。


[返回目录](#report-toc)

