# PandaX4T — PandaX4T_2024_US2

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

2026-11-07 SM benchmark输入包，DRAFT/PARTIAL；每个输入附直接来源，旧onboarding保留。

科学主张：SM forward benchmark with explicit public response limitations; no inference/CI reproduction。包状态 DRAFT / 见能力记录；人工科学审核 NOT_REVIEWED。

YAML 是标量与模型合同权威，NPZ 是数组权威；两份 Markdown 是同源派生说明。本文记录当前实验适配所需的输入与执行约定，不把旧实现恢复值认作官方论文原值。

<a id="section-2"></a>

## 2. Source

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`source.total_flux`](#param-source-total_flux) | 5460000.0 | cm^-2 s^-1 / direct_input | 2411.11749v1 PDF p5 Eq.(11)后，参考总通量；形状表不含该值 |

### 太阳8B通量

模型：`solar_b8_flux_v1`。Bahcall官网829点谱形×论文参考总通量；源仅乘一次参考年秒数，原表积分约0.999986544，不静默校正。

| 合同项 | 当前约定 |
| --- | --- |
| 定义域 | 纯SM，太阳8B；接受度可见真实反冲能区 |
| 边界/裁剪 | 不外推、不重复曝光/效率；缺失能力单独BLOCKED |

<a id="section-3"></a>

## 3. Target

本包靶核素：未绑定。质量分数、单核质量和核数的采用值只列于本节。

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`target.anchor_mass_kg`](#param-target-anchor_mass_kg) | 1000.0 | kg / runtime_control | 计算归一化锚点1t，不是实测探测器质量；与质量时间因子配对 |
| [`target.Z`](#param-target-Z) | 54.0 | 1 / direct_input | NIST Xenon，Z=54 |
| [`constants.avogadro`](#param-constants-avogadro) | 6.02214076e+23 | mol^-1 / direct_input | SI第9版§2.2/Table1精确值 |
| [`constants.amu_GeV`](#param-constants-amu_GeV) | 0.93149410372 | GeV/u / direct_input | foundation/constants.py::AMU_GEV；原子质量的GeV换算 |
| [`constants.electron_mass_GeV`](#param-constants-electron_mass_GeV) | 0.0005109989506900001 | GeV / direct_input | foundation/constants.py::m_e；裸核质量近似扣除Z个电子，忽略电子结合能 |

### 天然Xe与质量时间归一化

模型：`explicit_target_inventory_v1`。NIST九核素数丰度与原子质量给核数；参考1t×1yr仅为量纲锚点。动力学用扣除电子质量的裸核近似，电子结合能忽略。

| 合同项 | 当前约定 |
| --- | --- |
| 定义域 | 纯SM，太阳8B；接受度可见真实反冲能区 |
| 边界/裁剪 | 不外推、不重复曝光/效率；缺失能力单独BLOCKED |

<a id="section-4"></a>

## 4. 本实验选择的共享模块

Interaction 与 Nuclear Structure 是独立选择维度；下表只登记现有模块，不展开 matching、Particle Response、Nuclear Response、Helm、运动学或公共截面公式。

| 选择维度 | 实际 model ID | 已记录绑定状态 |
| --- | --- | --- |
| Nuclear Structure | `klein_nystrand_v1` | BOUND_UNVERIFIED |
| Interaction / 组合接口 | `coherent_sm_kn_v1` | BOUND_UNVERIFIED |

组合配置：{"model_id": "coherent_sm_kn_v1"}；资源按 assembly.target 的显式绑定读取。

当前实际绑定合同入口：[v1 模型合同](../../../../cevns_pyeft/experiments/model_bindings.json)、[v2 组件合同](../../../../cevns_pyeft/experiments/component_bindings.json)。外部理论与核结构约定的未决问题保留在第 10 节，不以失效的历史文档链接代替证据。

<a id="section-5"></a>

## 5. Detector

### 真实反冲接受度诊断

模型：`recoil_efficiency_projection_v1`。Ne逐箱Response仍缺；本输出只是真实反冲能量上的效率加权积分，不能冒充电子数事件谱。

| 合同项 | 当前约定 |
| --- | --- |
| 定义域 | 纯SM，太阳8B；接受度可见真实反冲能区 |
| 边界/裁剪 | 不外推、不重复曝光/效率；缺失能力单独BLOCKED |

<a id="section-6"></a>

## 6. Observable

观测量：efficiency-weighted true nuclear recoil spectrum；坐标单位 keVnr；共 27 箱。

唯一 bin-edge 数组：[`observable_edges`](#res-observable_edges)。完整边界为 0.299999999496, 0.3999999994961481, 0.49999999949629625, 0.5999999994964444, 0.6999999994965926, 0.7999999994967407, 0.8999999994968889, 0.999999999497037, 1.0999999994971852, 1.1999999994973334, 1.2999999994974814, 1.3999999994976298, 1.4999999994977777, 1.5999999994979262, 1.6999999994980741, 1.799999999498222, 1.8999999994983705, 1.9999999994985185, 2.099999999498667, 2.199999999498815, 2.299999999498963, 2.3999999994991112, 2.499999999499259, 2.599999999499407, 2.6999999994995556, 2.7999999994997036, 2.899999999499852, 2.9999999995 keVnr。

| Bin | 下边界 | 上边界 | 宽度 |
| --- | --- | --- | --- |
| 1 | 0.299999999496 | 0.3999999994961481 | 0.10000000000014814 |
| 2 | 0.3999999994961481 | 0.49999999949629625 | 0.10000000000014814 |
| 3 | 0.49999999949629625 | 0.5999999994964444 | 0.10000000000014819 |
| 4 | 0.5999999994964444 | 0.6999999994965926 | 0.10000000000014819 |
| 5 | 0.6999999994965926 | 0.7999999994967407 | 0.10000000000014808 |
| 6 | 0.7999999994967407 | 0.8999999994968889 | 0.10000000000014819 |
| 7 | 0.8999999994968889 | 0.999999999497037 | 0.10000000000014808 |
| 8 | 0.999999999497037 | 1.0999999994971852 | 0.10000000000014819 |
| 9 | 1.0999999994971852 | 1.1999999994973334 | 0.10000000000014819 |
| 10 | 1.1999999994973334 | 1.2999999994974814 | 0.10000000000014797 |
| 11 | 1.2999999994974814 | 1.3999999994976298 | 0.10000000000014841 |
| 12 | 1.3999999994976298 | 1.4999999994977777 | 0.10000000000014797 |
| 13 | 1.4999999994977777 | 1.5999999994979262 | 0.10000000000014841 |
| 14 | 1.5999999994979262 | 1.6999999994980741 | 0.10000000000014797 |
| 15 | 1.6999999994980741 | 1.799999999498222 | 0.10000000000014797 |
| 16 | 1.799999999498222 | 1.8999999994983705 | 0.10000000000014841 |
| 17 | 1.8999999994983705 | 1.9999999994985185 | 0.10000000000014797 |
| 18 | 1.9999999994985185 | 2.099999999498667 | 0.10000000000014841 |
| 19 | 2.099999999498667 | 2.199999999498815 | 0.10000000000014797 |
| 20 | 2.199999999498815 | 2.299999999498963 | 0.10000000000014797 |
| 21 | 2.299999999498963 | 2.3999999994991112 | 0.10000000000014841 |
| 22 | 2.3999999994991112 | 2.499999999499259 | 0.10000000000014797 |
| 23 | 2.499999999499259 | 2.599999999499407 | 0.10000000000014797 |
| 24 | 2.599999999499407 | 2.6999999994995556 | 0.10000000000014841 |
| 25 | 2.6999999994995556 | 2.7999999994997036 | 0.10000000000014797 |
| 26 | 2.7999999994997036 | 2.899999999499852 | 0.10000000000014841 |
| 27 | 2.899999999499852 | 2.9999999995 | 0.10000000000014797 |

边界约定：按显式边界逐箱积分；不从箱数猜测坐标。

<a id="section-7"></a>

## 7. Prediction folding

1. 按Bahcall源谱和SM截面求真实反冲率

2. 按天然九核素求和并进行对应响应/接受度投影

3. 乘各run的显式质量时间因子

4. 检查逐箱收敛、组分和及原参考谱差异

| Parameter ID | 采用值 | 单位 / 角色 | 定义 |
| --- | --- | --- | --- |
| [`constants.seconds_per_year`](#param-constants-seconds_per_year) | 31557600.0 | s/yr / direct_input | 365.25×86400=31557600；计算单位约定，不是额外活时间 |
| [`numerics.n_er`](#param-numerics-n_er) | 401 | 1 / runtime_control | Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 |
| [`numerics.n_enu`](#param-numerics-n_enu) | 240 | 1 / runtime_control | Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录 |

### Slow直接积分

模型：`solar_b8_sm_v1`。现有Runtime调用共享recoil积分及概率折叠。保留run与核素分量，单独检验Eν/T收敛；不使用c_i或全局拟合重标定。

| 合同项 | 当前约定 |
| --- | --- |
| 定义域 | 纯SM，太阳8B；接受度可见真实反冲能区 |
| 边界/裁剪 | 不外推、不重复曝光/效率；缺失能力单独BLOCKED |

<a id="section-8"></a>

## 8. Statistics

<a id="section-9"></a>

## 9. 数值资源

| NPZ key | shape / dtype | 单位 / 含义 | 来源 ID |
| --- | --- | --- | --- |
| <a id="res-source_energy_MeV"></a>`source_energy_MeV` | [829] / float64 | MeV / Bahcall官网b8spectrum.txt全部829行第一列 | R04 |
| <a id="res-source_shape_per_MeV"></a>`source_shape_per_MeV` | [829] / float64 | MeV^-1 / 同表第二列中心归一化谱；不重归一化，不含总通量/效率 | R04 |
| <a id="res-target_mass_number"></a>`target_mass_number` | [9] / float64 | 1 / NIST天然Xe表全部九行，对应A/原子质量/数丰度 | R09 |
| <a id="res-target_atomic_mass_u"></a>`target_atomic_mass_u` | [9] / float64 | u / NIST天然Xe表全部九行，对应A/原子质量/数丰度 | R09 |
| <a id="res-target_number_fraction"></a>`target_number_fraction` | [9] / float64 | 1 / NIST天然Xe表全部九行，对应A/原子质量/数丰度 | R09 |
| <a id="res-run_exposures_tyr"></a>`run_exposures_tyr` | [1] / float64 | t yr / 2407.10892v3 PDF p3 US2总曝光，未拆造逐run曝光 | R02 |
| <a id="res-efficiency_energy_keV"></a>`efficiency_energy_keV` | [99] / float64 | keVnr / 2407.10892v3 PDF p3 Fig.1黑色Total(US2)99个可见域矢量节点 | R02 |
| <a id="res-efficiency"></a>`efficiency` | [99] / float64 | 1 / 同曲线接受度；仅展示真实反冲接受度加权，不代表Ne 4–8的迁移概率 | R02 |
| <a id="res-observable_edges"></a>`observable_edges` | [28] / float64 | keVnr / 本轮显式输出坐标：可见能区分27个真实反冲箱，非电子数箱 | USER |

数组保留原 dtype、精度和顺序，以 allow_pickle=False 读取；哈希、生成依赖和完整轴声明以 YAML 为准，不在正文 dump。

<a id="section-10"></a>

## 10. 来源、限制与状态

| 能力 | 已记录状态 | 人工审核 |
| --- | --- | --- |
| signal | PARTIAL | NOT_REVIEWED |
| electron_spectrum | BLOCKED | NOT_REVIEWED |
| fast | NOT_APPLICABLE | NOT_REVIEWED |
| legacy_statistics | NOT_APPLICABLE | NOT_REVIEWED |

以上是输入中已有的状态，报告生成不重新执行 Runtime，也不提升能力或人工科学接受。

| 问题 ID / 状态 | 限制 | 影响范围 |
| --- | --- | --- |
| response_precision / PARTIAL | US2电子数响应缺失；真实反冲诊断不替代完整目标 | strict_paper_reproduction |

| 来源 ID | 路径 / locator | 种类 / 独立官方核实 |
| --- | --- | --- |
| R01 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R02 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R03 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R04 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R05 | 仅核书目，上游SSM数表保持未独立核验。通量标量的直接来源为R01 | primary_or_direct / 未登记 |
| R06 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R07 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R08 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R09 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R10 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R11 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R12 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R13 | BIPM第9版V4.01，§2.2/Table1在线原文已核。未缓存该PDF | primary_or_direct / 未登记 |
| R14 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R15 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R16 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R17 | 精确数值核验范围按P01与对应章节登记 | primary_or_direct / 未登记 |
| R18 | 实际使用G_F、AMU_GEV、m_e、HBARC_GEV_FM、GEV_INV2_TO_CM2、SEC_PER_YEAR；数值由参数卡固定并与本地模块核对。 | primary_or_direct / 未登记 |
| USER | P04_DECISION_LOG.yaml D0001; user requests canonical SM forward benchmark | project_decision / 未登记 |

<a id="equation-index"></a>

## Appendix A. 公式索引

| 编号 | 实验公式 | 模型 ID |
| --- | --- | --- |

<a id="parameter-index"></a>

## Appendix B. 唯一参数索引

实验采用值只在对应模块表中列一次；共享模块参数通过精确 ID 回到 YAML 配置，不复制公共模块公式或 LEC 数值表。

| Parameter ID | 主文位置 / 配置入口 | 来源定位 |
| --- | --- | --- |
| <a id="param-source-total_flux"></a>`source.total_flux` | source | R01; SOURCE_EXTRACTED |
| <a id="param-target-anchor_mass_kg"></a>`target.anchor_mass_kg` | target | USER; PROJECT_DERIVED |
| <a id="param-target-Z"></a>`target.Z` | target | R09; SOURCE_EXTRACTED |
| <a id="param-constants-avogadro"></a>`constants.avogadro` | target | R13; SOURCE_EXTRACTED |
| <a id="param-constants-amu_GeV"></a>`constants.amu_GeV` | target | R18; SOURCE_EXTRACTED |
| <a id="param-constants-electron_mass_GeV"></a>`constants.electron_mass_GeV` | target | R18; SOURCE_EXTRACTED |
| <a id="param-constants-G_F"></a>`constants.G_F` | 第 4 节共享配置 / YAML；非实验公式 | R18; SOURCE_EXTRACTED |
| <a id="param-constants-hbarc_GeV_fm"></a>`constants.hbarc_GeV_fm` | 第 4 节共享配置 / YAML；非实验公式 | R18; SOURCE_EXTRACTED |
| <a id="param-constants-GeV_inverse2_to_cm2"></a>`constants.GeV_inverse2_to_cm2` | 第 4 节共享配置 / YAML；非实验公式 | R18; SOURCE_EXTRACTED |
| <a id="param-constants-seconds_per_year"></a>`constants.seconds_per_year` | prediction | R18; SOURCE_EXTRACTED |
| <a id="param-nuclear-radius_fm"></a>`nuclear.radius_fm` | 第 4 节共享配置 / YAML；非实验公式 | R01; SOURCE_EXTRACTED |
| <a id="param-nuclear-skin_fm"></a>`nuclear.skin_fm` | 第 4 节共享配置 / YAML；非实验公式 | R01; SOURCE_EXTRACTED |
| <a id="param-interaction-sin2thetaW"></a>`interaction.sin2thetaW` | 第 4 节共享配置 / YAML；非实验公式 | R01; SOURCE_EXTRACTED |
| <a id="param-interaction-include_sm"></a>`interaction.include_sm` | 第 4 节共享配置 / YAML；非实验公式 | USER; SOURCE_EXTRACTED |
| <a id="param-numerics-n_er"></a>`numerics.n_er` | prediction | USER; PROJECT_DERIVED |
| <a id="param-numerics-n_enu"></a>`numerics.n_enu` | prediction | USER; PROJECT_DERIVED |
