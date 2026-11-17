# 五条主线的 onboarding 与标准模型计算汇总

[全部文件地址与目录结构分析](MAINLINE_FILE_LAYOUT_AUDIT_20261111.md) · [1325项逐文件完整地址](../../outputs/mainline_summary_20261111/FILE_ADDRESSES_20261111.md)

核对日期：2026-11-11，Asia/Shanghai。以用户指定的 `261103Gitup1-CONUS-6/Gitup01` 为主项目；按用户后续明确给出的目录，补充关联的 CONUS+ SM/NSI 隔离 benchmark。这里的“CONUS”就是 **CONUS+ / conusplus_kkl_run1**，onboarding 主文件为 `docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md`。隔离结果作为关联计算汇总，不自动成为默认 Runtime 注册或正式科学批准。

**现状：⁸B 单 bin、CsI-time 有独立 SM 计算和收敛记录；CsI2017、Ar2020 有可运行的旧实现兼容输入包，本次指定网格复算与冻结参考一致；CONUS+ 已有同一数据集的隔离 SM 结果（149.419400 events）和 NSI benchmark，原始科学来源状态仍为 PARTIAL。五条线尚未全部达到同一种科学验证状态。**

CONUS 补充修订：初稿只检查 Gitup01 内部，没有纳入后来由用户明确指出的两处 `.experiment-auto-runs` 结果目录，因此“没有 SM 产物”不能概括该数据集的全部关联工作。以下已补齐结果、位置和适用范围；原有 Gitup01 内部搜索/生成器检查记录仍按当时范围保留。

本文件是现有输入与计算的汇总，不新增物理选择、实验注册或科学批准。来源定位沿用各自的证据台账；本次重新执行的是文件/数组回读、指纹检查、指定网格运行和下述文档检查，没有重新认证全部原始论文。

[本次数值回读与检查](../../outputs/mainline_summary_20261111/README.md) · [机器回读记录](../../outputs/mainline_summary_20261111/INPUT_READBACK.json) · [CONUS 关联 benchmark 补充核对](../../outputs/mainline_summary_20261111/CONUS_BENCHMARK_READBACK.json) · [两条旧实现的实际复算](../../outputs/mainline_summary_20261111/legacy_sm_grid_check.json) · [实验文档总入口](README.md)

<a id="toc"></a>

## 阅读目录

- [1. 总表与当前入口](#overview)
- [2. 共同计算链与不同输入口径](#chain)
- [3. ⁸B 单 bin](#solar)
- [4. CsI-time](#csi-time)
- [5. CsI2017](#csi2017)
- [6. Ar2020](#ar)
- [7. CONUS+](#conus)
- [8. 本次核对结果](#checks)
- [9. 后续工作交接](#handoff)

<a id="overview"></a>

## 1. 总表与当前入口

| 主线 | 当前 onboarding / 输入权威 | SM 输出与本次核对 | 结果的适用范围 |
|---|---|---|---|
| ⁸B 单 bin：PandaX paired / US2 / XENONnT | [v3.2.1](PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md)；独立 JSON card 与数值表 | [20261111_response_run2](../../outputs/solar_b8_singlebin/20261111_response_run2/README.md)：**2.487612254 / 47.042059756 / [11.812101957, 12.169955057] events** | 前两项是已采用输入下的完整积分；XENONnT 是效率缺失尾段导致的界限，非误差置信区间 |
| CsI-time：CsI2021_time_9x11 | [r2 详细版](COHERENT/CsI2021/time_resolved/experiment.physics.md)；P00–P03、官方附件、所选本地 Response | [SM 基准报告](COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md)：**353.465608686 events，9×11 箱** | 原生 SM/本地 Response 的未拟合前向结果；不等于论文最佳拟合曲线或原生二维 likelihood |
| CsI2017 | [Physics Input](../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md)；正式 YAML/NPZ，`legacy_25bin_modular_v1` | 本次当前 Runtime：**167.558550049 events，25 箱**；`n_enu=12` | 指定旧回归网格的兼容数值；不是收敛后的默认网格基准 |
| Ar2020 | [Physics Input](../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md)；正式 YAML/NPZ，`observed_gaussian_legacy_v1` | 本次当前 Runtime：**136.632223203 events，12 箱**；`n_er=11,n_enu=40,n_pe_bin=8` | 指定旧回归网格的兼容数值；观测坐标单位仍有待核冲突 |
| CONUS+ | [v3 来源标注版](CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md)，`v3_20261106_provenance`，PARTIAL | [关联 SM benchmark](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/review/SM_BENCHMARK_REPORT_V1.md)：**149.419399803 events，19 箱**；另有[NSI benchmark](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/review/NSI_BENCHMARK_REPORT_V1.md) | 隔离候选已计算并保存验证；未自动推广为主项目默认 Runtime 或严格论文复现 |

注册表目前只有 `CsI2021 / CsI2017 / Ar2020` 三个默认活动 ID，见[唯一注册表](../../cevns_pyeft/experiments/dataset_registry.json)。⁸B 单 bin 使用独立 scoped loader；CsI-time 通过示例装配 PE 预测并施加时间权重；CONUS+ 未登记为默认活动实验。目录存在、数值可读、可运行、工程 PASS 与科学批准分别记录。

[返回目录](#toc)

<a id="chain"></a>

## 2. 共同计算链与不同输入口径

共同计算关系为：**源谱/注量 → 核素与真实核数 → 所选 SM 相互作用和核响应 → 真实反冲产额 → 探测器接受度或重建折叠 → 观测分箱 → 按各自数据语义评价统计量**。共享入口和核响应不能代替实验专属的归一化与坐标合同。

| 核对项 | ⁸B 单 bin | CsI-time | CsI2017 | Ar2020 | CONUS+ 当前方案 |
|---|---|---|---|---|---|
| 源 | 太阳⁸B；5.46×10⁶ cm⁻²s⁻¹ | SNS；3.198×10²³ POT，0.0848/味/POT，19.3 m | SNS；1.73×10²³ POT，0.08/味/POT，19.3 m | SNS；1.38×10²³ POT，0.09/味/POT，27.5 m | 反应堆电子反中微子；1.5×10¹³ cm⁻²s⁻¹，0–10 MeV |
| 靶与曝光 | 天然 Xe；1.20 / 1.04 / 3.51 t·yr | 等化学计量 Cs/I；14.6 kg | Cs/I；实际预测 14.6 kg，14.57 kg 为 reference-only 元数据 | Ar40；24 kg | 天然 Ge70/72/73/74/76；有效质量 1 kg、曝光 119 kg·day 的文献比较方案 |
| sin²θW | 0.23857 | 0.23857 | 包默认 0.2387 | 包默认 0.2387 | 关联 SM 候选采用 0.23857 |
| 探测器 | 总接受度 ε(T)，直接积分信号总数 | QF → 光产额 → Gamma 展宽 → PE 效率 → 时间权重 | PE=1.17×T，固定 251 节点、表格效率与 4.9 PE 阈值 | 均值 `(0.246+0.00078T)T`；宽度 `0.58√x` 依赖观测值 x | Lindhard k=0.162；Gaussian；σ₀=20.38 eVee、Fano=0.1096、电子空穴对能量 2.96 eVee |
| 输出坐标 | 每样本一个信号数 | PE×重建时间；events/bin | 25 个 PE 箱；events/bin | Package 标为 PE 的 12 箱；官方效率表坐标为 keVee | 160–350 eVee，19×10 eVee 箱 |
| 统计 | 拟合信号量 Gaussian，三个独立 12% pull | 本轮未做正式拟合 | 近似 Gaussian，单 28% pull | 近似非对称 IRLS，信号/背景 pull 0.12/0.146 | 关联 NSI 已用有符号 excess、上下误差均值和 0.169 pull 做近似拟合；人工审核仍 NOT_REVIEWED |

各列的直接输入和来源在下面的同节表格列出。SNS 的 NPZ 已保存运行期积分注量，不能重复乘 POT、活时间或另一份绝对通量；太阳采用 t·yr 曝光和每秒通量；CONUS+ 的 119 kg·day 是所选有效曝光，不能误当事件数。

五条线的数据模式、窗口和统计模型不同，本汇总不相加它们的事件总数或 χ²。

[返回目录](#toc)

<a id="solar"></a>

## 3. ⁸B 单 bin：当前主线 v3.2.1

采用 Li et al., arXiv:2601.19883v2，PDF p19 Eq.(84)、p20 Eqs.(87),(88) 的总信号与近似统计方案。它与 [多 bin v3.1](PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md) 并列；旧 Ne/cS2 分箱、Qy 映射和旧 Fast 缓存没有混入本次单 bin。

| 输入/模块 | 本地数值与实际内容 | 直接出处和核验范围 |
|---|---|---|
| [单 bin card](../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json) | 通量、弱混合角、三个样本的曝光/窗口及显式文件绑定 | 通量取 Li et al., arXiv:2409.04703v2，PDF p5 Eq.(29)；sin²θW 为项目采用点，不能声称 2601 重印了全部默认值 |
| [源谱](../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt) | 829×2，0–16.56 MeV；原谱积分约 0.999986544，不再次归一 | Bahcall et al., Phys. Rev. C 54 (1996) 411，官网数表前两列；提取与边界约定见 v3.2.1 |
| [天然 Xe 表](../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt)与[核表](../../data/responses/responses_all.json) | 9 个天然核素的核数；实际有核表的 Xe128/129/130/131/132/134/136 共 7 核素 | NIST Xe 丰度/质量；核响应为用户选定的本地资源。Xe124/126 共 0.1842% 数丰度缺核表，不填 KN、不重归一；外部作者导出链仍未认证 |
| [paired 效率](../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt) / [US2 效率](../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt) | 52×2 / 99×2；T 窗口 1.1–3 / 0.3–3 keVnr；曝光 1.20 / 1.04 t·yr | PandaX Collaboration, PRL 133 (2024) 191001，arXiv:2407.10892v3，PDF p3 Fig.1 Total 曲线；paired 曝光未采用再分析中的 1.25 |
| [XENONnT 效率](../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt) | 40×3，末点约 2.77 keVnr；所需窗口 0.5–3 keVnr，3.51 t·yr | XENON Collaboration, PRL 133 (2024) 191002，arXiv:2408.02877v2，PDF p4 Fig.1 黑色 combined；2.77–3 keVnr 的数值仍 MISSING |
| [信号量与误差](../../data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json) | 3.5±1.3、75±28、10.7±3.95 events；每项独立 12% pull | 原测量的拟合信号量和 Liao et al., arXiv:2502.10702v2 Table II 的取整误差；不是原始候选 Poisson 计数 |

代码为 [solar_singlebin.py](../../cevns_pyeft/experiments/solar_singlebin.py) → [共享 SM 截面适配](../../cevns_pyeft/theory/li2026/sm_quadratic.py) → 每核反冲积分 → 核数、总接受度和曝光；统计在 [statistics/solar_singlebin.py](../../cevns_pyeft/statistics/solar_singlebin.py)。

| 样本 | SM 事件数 | 固定 SM 点的 profile χ² | 解释 |
|---|---:|---:|---|
| PandaX paired | 2.487612254 | 0.576090731 | 采用输入下的完整积分 |
| PandaX US2 | 47.042059756 | 0.958056701 | 采用输入下的完整积分 |
| XENONnT | 已知域 11.812101957；完整窗口界限 [11.812101957,12.169955057] | 主结果不写完整点 χ² | 仅由未知尾段 0≤ε≤1 导出的区间 |

区间只处理效率尾段缺失，未包含通量、核响应或缺少核素等系统不确定性。显式采用平坦尾段假设时，XENONnT 为 11.856471279 events、χ²=0.075874597，属于项目敏感性估计。三样本 χ² 尾段范围为 [1.604371931,1.655982059]；正式主记录 `joint_chi2=null`。

既有结果保存反冲 201→401→801、随后中微子 120→480 的独立加密，三个样本均通过其记录的收敛门限。本次重新回读全部样本的 NPZ/JSON，对照每样本 5 项输入和 15 项实施指纹，均一致；同源生成器 `--check` 检查 6 份文档通过。

[SM 对照图](../../outputs/solar_b8_singlebin/20261111_response_run2/singlebin_SM_comparison.png) · [完整结果 JSON](../../outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json) · [复算入口](../../tools/run_solar_b8_singlebin_benchmark.py)

[返回目录](#toc)

<a id="csi-time"></a>

## 4. CsI-time：r2 输入与 99 箱 SM

阅读入口为 [time_resolved README](COHERENT/CsI2021/time_resolved/README.md)、[onboarding 详细版](COHERENT/CsI2021/time_resolved/experiment.physics.md)和[SM 专属报告](COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md)。这是一份 CsI2021 测量的时间分析，不能用默认注册 `CsI2021` 的旧一维九箱调用代替。

| 输入/模块 | 实际值或数组 | 直接出处、转换及适用性 |
|---|---|---|
| [SM 配置](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/SM_CONFIG.json) | 3.198×10²³ POT、0.0848/味/POT、19.3 m、14.6 kg；sin²θW=0.23857 | COHERENT, PRL129 (2022) 081801 / arXiv:2110.07730v2 Supplement p2；De Romeri et al., JHEP04(2023)035 / arXiv:2211.11905v2 pp12–13 |
| [分析输入目录](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/README.md)与[核表](../../data/responses/responses_all.json) | Cs133/I 键；M 系数各 2×2×11；分析观测 9×11 | 原 data 核表是直接采用源；提取 NPZ 用于核对，不替代原表。外部导出链未认证不阻断已有授权的本地复用 |
| [官方探测器附件](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/README.md) | QF 四系数、光产额 13.35 PE/keVee、Gamma 展宽、官方效率常数项 −0.333322 | scintRespCoefficients.txt / effCoefficients.txt 的 nominal 行；Supplement p3；QF 采用 2–70 keVnr 有效域，计算从 2 keVnr 起 |
| [归一化台账](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sm_benchmark_20261107/NORMALIZATION_LEDGER.json) | 每味 η=5.793617637932339×10¹⁴ cm⁻²；零平移 0–6 μs 参考窗分母 | 主结果的注量范围是显式选择；无额外活时间因子。相同 η 解释为全支撑域会改变结果含义 |
| [完整预测](../../outputs/csi2021_time_sm_20261107/benchmark.npz) / [99 箱 CSV](../../outputs/csi2021_time_sm_20261107/events_99bins.csv) | `(PE,time)=(9,11)`，events/bin；另保存源/核素分解及 full-fluence 诊断 | PE edges=[0,8,12,16,20,24,32,40,48,60]；t edges=[0,.125,.25,.375,.5,.625,.75,.875,1,2,4,6] μs；左闭右开 |

调用链为 [run_benchmark.py](../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py) → 主项目一维 Slow → 既有时间权重。复算仍显式依赖 `--legacy-time-dir`，所用旧时间模块目录位于本项目外的 `260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time`；本次确认目录存在。该依赖未被默认为主项目已封装的二维能力。

| 源分量 | Cs133 / events | I127 / events | 合计 / events |
|---|---:|---:|---:|
| prompt νμ | 24.650290788 | 25.882603398 | 50.532894186 |
| delayed νe | 58.338827480 | 58.464893056 | 116.803720535 |
| delayed anti-νμ | 93.304632100 | 92.824361865 | 186.128993965 |
| 总计 | 176.293750367 | 177.171858319 | **353.465608686** |

同数值 η 采用全支撑域解释时为 **329.016422597** events；不能把两者差别说成同一注量定义下的模板误差。既有最终网格为 `512/960/256/0.0625`（反冲节点/中微子节点/每 PE 箱节点/PE 步长）；其 11 组检查和 24 项 Runtime 测试是历史执行结果。本次未重跑这些检查，但重新核对 99 箱求和、源/核素分解、CSV/NPZ、28 项来源和 124 项源码指纹，均一致。

实验对照使用官方 C=1578、AC=1295 原始事件。SSB=1285.926524、raw BRN=27.423763、raw NIN=6.908565 是当前诊断背景；BRN/NIN 与 18.4/5.6 先验尚未闭合。原始 C 不能与纯信号 353.47 直接作同语义比较。

[2026-11-09 实验叠加图与数据](../../outputs/csi2021_time_sm_data_comparison_20261109/README.md)对应 2211.11905v2 **PDF p35 Fig.18** 的 11 时间窗布局；没有认证为其 best-fit 曲线或 χ²=83.2 的统计复现。完整 ROOT E–t 相关、背景归一、半径 nuisance 和论文核模型等价继续保留限制。

[返回目录](#toc)

<a id="csi2017"></a>

## 5. CsI2017：25 箱旧实现兼容主线

当前权威为[输入目录 README](../../data/experiments/COHERENT_CsI/CsI2017/README.md)、[experiment.input.yaml](../../data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml)和[experiment.resources.npz](../../data/experiments/COHERENT_CsI/CsI2017/experiment.resources.npz)。包状态 DRAFT、人工审核 NOT_REVIEWED；signal/Fast/legacy statistics 的 PASS 只对应旧实现兼容范围。官方 likelihood、一般反中微子 EFT 和 scientific release 均仍 BLOCKED。

| 输入/处理 | 实际内容 | 来源与限制 |
|---|---|---|
| Source / Target | 200 点连续注量表、3 个味态矩阵；1.73×10²³ POT、19.3 m、0.08/味/POT；实际质量 14.6 kg | 从旧 SNS/目标实现提取；14.57 kg 是 reference-only 运行元数据；源注量不重复乘 POT |
| 核响应 | 两核素×七通道，共 14 个 2×2×K 系数数组 | NPZ 与当前本地 responses_all.json 逐值一致；本次核对 14 项通过，外部原表认证另计 |
| 效率与观测 | 36 点效率；PE=1.17T；固定 251 节点；25 箱 edges 从 0.001 到 50 PE | [效率 TXT](../../data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt)与 NPZ 一致；不能用 CsI2021 的 Gamma/时间模型替换 |
| 统计与参考谱 | observed/lower/upper/spectrum/uncertainty 各 25 项；σ=max((upper−lower)/2,10⁻¹²)，28% pull | [统计说明](../../data/experiments/COHERENT_CsI/CsI2017/statistics/provenance.yaml)；有符号 residual。公开对照为 Kavanagh CEvNS 固定提交 `6adce961e769cfbf8edc9acef140ebac46009c36` 的 DataFiles；未认证为官方原始计数 |

28 个数组的 shape、单位、代表值和哈希在[本次回读](../../outputs/mainline_summary_20261111/INPUT_READBACK.json)的 `legacy_packages` 中。背景扣除 residual 的负箱保留，四份统计 TXT 各自的横坐标不能冒充相同的精确箱中心。

本次由当前 `load_experiment → predict_experiment` 实际运行 **n_enu=12**，得到 **167.558550049 events**。三分量为 28.048148797 / 53.259461722 / 86.250939530 events；与[冻结参考](../../tests/reference/interface_refactor_v1/baseline.npz)最大逐箱绝对差 **3.552713679×10⁻¹⁵ events**。

Package 的默认 Slow 是 `n_enu=120`。本次使用 12 是核对既有冻结案例，未检查默认网格收敛、未进行官方统计拟合。[运行记录](../../outputs/mainline_summary_20261111/legacy_sm_grid_check.json)保存全部 25 箱、分量和实际参数点。

本次发现两项文档/资料问题：现有 Physics MD 与当前 YAML/NPZ Renderer 输出不一致；兼容文件 `statistics/observation_schema.json` 缺失。机器输入单独验证 PASS，当前 Runtime 实际预测可运行，不能因此宣称全部三文件或旧兼容资料齐备。

[返回目录](#toc)

<a id="ar"></a>

## 6. Ar2020：12 箱旧实现与坐标冲突

当前权威为[输入目录 README](../../data/experiments/COHERENT_Ar/Ar2020/README.md)、[experiment.input.yaml](../../data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml)和[experiment.resources.npz](../../data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz)。同样为 DRAFT / NOT_REVIEWED，兼容能力与官方科学验证分开。

| 输入/处理 | 实际内容 | 来源与限制 |
|---|---|---|
| Source / Target | 200 点连续注量表、3 个味态矩阵；1.38×10²³ POT、27.5 m、0.09/味/POT；24 kg Ar40 | 旧实现生成的已积分注量；不重复乘 POT/活时间 |
| 核响应 | 七通道，M 数组 2×2×7；七组系数 | 本次与当前本地 Response 的 Ar40 数值逐值一致；外部原表来源仍待核 |
| 效率 | 80 点；NPZ 数值对应官方三列表的第 1、3 列 | [CENNS10AnlAEfficiency.txt](../../data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt)：官方第 1 列为 **keVee**，Package 当前标签为 **PE**。数值一致不解决单位冲突 |
| 重建与分箱 | 均值 `(0.246+0.00078T)T`、σ(x)=0.58√x；13 条 edges=0.001 到 120.001，当前标 PE | σ 依赖观测坐标 x；这是专用旧折叠策略。不能默认为标准的真实反冲 Gaussian 或直接改标签 |
| 统计 | 12 项 observed/background/lower/upper；非对称 IRLS、两个有界 pull | 来自旧 AR 数组；不是官方三维数据的完整 likelihood |
| 官方 SM 对照表 | [cevnspdf.txt](../../data/experiments/COHERENT_Ar/Ar2020/statistics/cevnspdf.txt)，960×4=12 能量×8 F90×10 时间箱 | COHERENT release DOI 10.5281/zenodo.3903810；Companion §2.2，归一化为 6.12 GWhr 的初始 central-value SM，第四列和约 128.000005。不是单位积分概率或实测计数 |

本次在当前 Runtime 实际运行 **n_er=11,n_enu=40,n_pe_bin=8**，得到 **136.632223203 events**；prompt νμ / delayed νe / delayed anti-νμ 为 30.734816022 / 43.634755601 / 62.262651580 events。与旧冻结参考逐箱最大差为 **0**。Package 默认 Slow 为 21/120/8，本次未检查其网格收敛。

**136.6322 与官方模板约 128 的数值不能直接作为论文复现误差。** 源、核物理、坐标及分析窗口的等价尚未建立；官方 signal PDF 未绑定为当前 NPZ 统计输入。本次机器输入单独验证 PASS，含现有 Physics MD 的完整验证 FAIL（Renderer 不一致），未改写原数值或标签。

[返回目录](#toc)

<a id="conus"></a>

## 7. CONUS+：主项目 onboarding 与关联 SM/NSI benchmark

当前入口就是用户指出的 [v3 README](CONUS_Plus/datasets/conusplus_kkl_run1/README.md)、[experiment.physics.md](CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md)，对应[数据目录](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/README.md)及[缺口 P02](../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P02_MISSING_AND_CONFLICTS.md)。所选比较对象是 arXiv:2501.17843v3，Eq.(33)、Eq.(34)、Table II。以下两个关联计算目录的 summary 均声明 `dataset_id=conusplus_kkl_run1`，输入快照的 `source_root` 均指向本 Gitup01。

| 关联计算 | 位置与结果 |
|---|---|
| SM Response | [计算目录](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/README.md)；[报告](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/review/SM_BENCHMARK_REPORT_V1.md)、[19 箱 CSV](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/outputs/sm_counts_19bins.csv)、[summary](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/outputs/summary.json)、[谱图](../../../../.experiment-auto-runs/conusplus-sm-response-20261106/outputs/conusplus_sm_event_spectrum.png) |
| NSI Response | [计算目录](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/README.md)；[报告](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/review/NSI_BENCHMARK_REPORT_V1.md)、[summary](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/outputs/summary.json)、[区间 CSV](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/outputs/nsi_intervals.csv)、[二维区域图](../../../../.experiment-auto-runs/conusplus-nsi-response-20261106/outputs/nsi_contours_2d.png) |

| 输入/模块 | 实际数据与本次回读 | 直接出处和剩余限制 |
|---|---|---|
| [Flux](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_default.csv) | 10001 个能量点，0–10 MeV、步长 0.001 MeV；积分 1.5000000181330584×10¹³ cm⁻²s⁻¹，非负 | [Mueller 24 系数](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/mueller_coefficients.csv)核对其 Table VI；[低能 32 点](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/kopeikin_low_energy_transcribed.csv)核对用户 PDF 表2；Kopeikin 原始数表链未闭合 |
| [裂变份额](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/fission_fractions.csv)与零端点 | 参考方案 U235/U238/Pu239/Pu241=0.56/0.07/0.31/0.06；2 MeV 拼接，补(0,0) | KKL 对照配比为 0.53/0.08/0.32/0.07。两者分别保存，不宣称当前参考配比就是运行测量 |
| [Ge 库存](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/natural_ge_inventory.csv) | 五天然核素；数丰度 0.2057/0.2745/0.0775/0.3650/0.0773；质量与丰度来自 NIST | 原子质量转核质量的约定、1 kg 和 119 kg·day 的有效曝光见详细版；不能把源或曝光重归一来凑比较目标 |
| 核响应/截面 | 关联 SM 已用 Ge70/72/73/74/76 的本地 Response 和 Li2026LegacyInteraction 计算 | 核数采用 NIST 原子质量，运动学采用既有引擎 A×u；沿用 Li et al. p21 Eq.(92) 后的 ν/反ν rate-kernel 约定。原始核表链及更一般的螺旋度适用审计仍另保留 |
| Detector / Observable | Lindhard + Gaussian，160 eVee 阈值；19 个 10 eVee 箱 | 2501.17843v3 pp9–10；按所选近似阈值以上效率为1，不冒称完整官方触发模型 |
| [有符号观测 CSV](../../data/experiments/CONUS_Plus/conusplus_kkl_run1/statistics/conusplus_2501_17843v3_fig1_digitized.csv) | 19 行；counts/kg/(10eVee)，保留负值及上下误差 | 从指定 Fig.1 原生矢量数字化；作者原始数表未取得。关联 NSI 已显式采用上下误差均值，并分别用上下误差复核敏感性；该执行选择不改写原 onboarding 的人工审阅状态 |

关联 SM 实际得到 **149.419399803 events**：1 kg、119 days、160–350 eVee、19 个 10 eVee 箱。五核素贡献依次为 Ge70=31.267456290、Ge72=41.304657952、Ge73=11.707179464、Ge74=53.966883226、Ge76=11.173222871 events。计算沿用 `core.predict → integrate_recoil_yield → Li2026LegacyInteraction → probability_fold`，源曝光和核数各乘一次。

其最终网格 `fine_641` 为反冲161点、中微子641点；保存的独立能量/反冲加密均满足预设 `10⁻⁴ events + 0.3%` 逐箱门限。论文 Fig.1 蓝线中心取点纵值之和为152.092946830，与本计算总量相差−1.7578%；但330–340 eVee箱相对差约−54.8%，对应绝对差−0.429886 events。**总量接近不能认证谱形复现**；本计算用 Nuclear Response 和用户选定 Flux，论文采用 Klein–Nystrand。

关联 NSI 已完成六个实数 u/d 矢量 NSI 的一维区间及 Fig.4 的二维比较，主统计为 Eq.(33) 的19箱近似 Gaussian＋0.169归一化pull。其 SM profiled χ²为 **7.366493276**，α=0.0145647603；两个对角耦合的1σ区间为：

| 耦合 | 本项目关联 NSI 候选的1σ区间 |
|---|---|
| εᵘⱽₑₑ | [−0.036652535,0.025717784] ∪ [0.348216504,0.410333630] |
| εᵈⱽₑₑ | [−0.033872472,0.023756291] ∪ [0.321964969,0.379483131] |
| εᵘⱽₑμ / εᵘⱽₑτ | [−0.122640134,0.122640134] |
| εᵈⱽₑμ / εᵈⱽₑτ | [−0.113377079,0.113377079] |

保存记录中六项与论文 Table II 端点的差均小于预定0.001；这是一项近似 benchmark 一致性记录，不覆盖所有理论约定或频率学覆盖率。所有人工审核仍 NOT_REVIEWED，原始来源仍 PARTIAL。

本次补充回读 SM 的 NPZ/CSV，19箱及逐核素求和完全一致；SM/NSI 两套201项输入快照各自的指纹均一致，且各19项所选输入/文档与当前主项目一致；输出清单分别19/19、42/42项通过。由保存的 SM 计数与 NSI 观测/误差独立计算 χ²，和其记录相差4.44×10⁻¹⁵。详见[补充核对 JSON](../../outputs/mainline_summary_20261111/CONUS_BENCHMARK_READBACK.json)，本轮未重跑积分或扫描。

原 data 的 `numerical_checks.json` 中 `fit_executed=false` 描述的是输入构建记录，不能据此否认后续独立 NSI 拟合。当前 registry 没有 CONUS+、隔离结果尚未自动接入默认 Runtime；这与“已存在关联 SM/NSI 结果”同时成立。文献 sin²θW=0.247±0.052 仍是外部参考，不能写成本次已重新拟合的弱混合角。

初次检查当前主项目时还发现两个复现条件：数据生成器 `--check` 在所用 Python 中缺 `pdfplumber`，本轮未完成该检查；onboarding 生成器 `--check` 因 `package_profiles.py` 与保存的实施指纹不一致而停止。这是当前主项目生成环境/身份核对的限制，不推翻已固定输入快照的关联 benchmark；也不能通过改旧指纹来消除。原始 Kopeikin/Ge Response 来源问题继续保留。

[返回目录](#toc)

<a id="checks"></a>

## 8. 本次核对结果

本次使用 `F:/Work/.codex_conda_envs/codex-py311/python.exe`，NumPy 2.4.6、SciPy 1.17.1；全部运行均为 `-B`，未安装依赖或修改物理实现。精确记录见[INPUT_READBACK.json](../../outputs/mainline_summary_20261111/INPUT_READBACK.json)。

| 本次实际检查 | 结果 | 证明范围 |
|---|---|---|
| ⁸B 三样本 JSON / NPZ、每样本5项输入和15项实施指纹 | 一致 | 保存结果仍对应当前这些直接输入/实施文件；未重算积分 |
| ⁸B 同源文档生成器 `--check` | PASS，6 份文档 | 文档与当前 card/已保存结果一致 |
| CsI-time 99箱、分量求和、CSV/NPZ | 一致 | 353.465608686 events 可从数组独立回读 |
| CsI-time 28项来源 / 124项源码与历史记录 | 28/28、124/124 一致 | 相关历史指纹未变；11组数值检查和24项测试未在本轮重跑 |
| CsI2017 / Ar2020 当前 Runtime 指定网格 SM | 与冻结参考一致 | 最大逐箱差分别3.55×10⁻¹⁵ / 0 events；未执行默认网格收敛或官方拟合 |
| 两个 legacy Package，`validate_package(check_md=False)` | PASS / PASS | 当前 YAML/NPZ 的结构、数组和资源约束 |
| 两个 legacy Package，含 Physics MD 的完整验证 | FAIL / FAIL | 均报 `Physics MD differs from deterministic YAML/NPZ rendering`；不是已验证的三文件同步状态 |
| CONUS+ Flux 独立回读 | 非负，10001点；积分相对目标约1.21×10⁻⁸ | 数值表内部归一化，不证明低能原始出处或 SM 正确 |
| 用户明确指定的 CONUS+ SM/NSI 关联目录 | dataset相同；输入快照各201项、当前输入各19项、输出19/42项均一致 | 已有149.419400事例及NSI候选结果；本次补充回读，不是新运行或正式推广 |
| CONUS+ 已保存SM计数与NSI数据的profile χ² | 7.366493276，和记录差4.44×10⁻¹⁵ | 独立数学回算；不重新扫描NSI或重新认证来源 |
| CONUS+ 数据生成器 `--check` | 本轮环境缺 pdfplumber，未完成 | 环境条件问题，不能据此判定原数据物理错误 |
| CONUS+ onboarding 生成器 `--check` | 指纹冲突，未通过 | 当前 package_profiles.py 与保存的实施身份不同，需审计依赖影响 |

当前副本没有 `.git`，本次以文件 SHA256 建立基线；未虚构提交号。检查记录另保存164项文件的快照，供本轮结束时核对输入和实现未被改写。报告与导航的链接检查由[本次输出目录](../../outputs/mainline_summary_20261111/README.md)记录。

[返回目录](#toc)

<a id="handoff"></a>

## 9. 后续工作交接

| 主线/能力 | 已具备 | 下一步具体工作或输入 | 影响范围 |
|---|---|---|---|
| ⁸B 单 bin 的完整 XENONnT 点预测 | 7核素、源谱、已知效率域、尾段界限 | 补2.77–3 keVnr combined效率；若申请完整天然Xe预测，另补Xe124/126核表 | 完整信号点值及其 χ²；核表外部认证单独处理 |
| CsI-time 的正式统计 / 论文等价 | 99箱 SM、官方C/AC、诊断背景、收敛证据 | 明确BRN/NIN绝对归一；核对论文核模型与耦合、PE精确边界、nuisance/likelihood；记录外部时间模块依赖 | 官方拟合、论文83.2基准、原生二维能力；现有前向结果仍可用 |
| CsI2017 的文档同步与科学复核 | 当前YAML/NPZ、指定网格兼容数值 | 审阅当前Renderer与MD差异；处理缺失兼容schema；补一手观测/误差来源，另做默认网格收敛 | 三文件一致性、正式来源声明和官方统计；本次不重渲染原报告 |
| Ar2020 的坐标与科学复核 | 当前兼容预测、官方效率/SM模板对照表 | 追踪PE/keVee、光产额和观测轴转换，再决定是否更改；审阅MD差异，另做收敛 | 物理坐标、效率作用域、统计解释与官方比较 |
| CONUS+ 的候选结果审阅与主项目交接 | PARTIAL onboarding、关联SM 149.419400事例、收敛记录与NSI近似benchmark | 审阅固定快照的结果与适用约定；补Kopeikin/Ge Response原始来源；追查谱形尾部差异；处理主项目生成器依赖/指纹及候选推广范围 | 不必重复当作从未计算；正式接入、科学接受与严格论文等价仍分开处理 |

本轮交付范围是汇总、回读和指定旧网格的运行核对。原科学缺口、历史阶段状态和输入包均按原记录保留。

[返回目录](#toc)
