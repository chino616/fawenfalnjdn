# 已填写示例：COHERENT CsI2021 用户资料表

本文件依照[通用用户资料模板](EXPERIMENT_USER_INPUT_TEMPLATE.md)的第 1–10 节填写，展示具体资料如何进入实验接入流程。依据是**当前项目的 CsI2021 配置和代码**；项目配置不自动等于 COHERENT 官方发表值，也不能直接移植到其他实验。标注“缺失”的内容没有用推测值补齐。本例不是新的 Physics Gate 批准记录。代码迁移只参考[提炼后的核心函数结构](../phase/CsI2021_CORE_FUNCTION_STRUCTURE.md)，不复制 CsI2021 的整段实现。

| 用户资料章节 | 后续主要使用阶段 |
| --- | --- |
| 1–2 实验身份、观测量、分箱 | P01 Dataset |
| 4 靶材、曝光 | P02 Target；散射约定还供 P04–P05 使用 |
| 3 中微子源 | P03 Source |
| 4 核响应、截面和运动学 | P04 Theory、P05 Kinematics |
| 5 探测器响应 | P06 Detector Response |
| 2、4、6 计数定义 | P07 Slow |
| 9 Fast 目标 | P08 Fast |
| 7 统计分析 | P09 Statistics |
| 8、10 基准、缺失和冲突 | P10 Validation 与前序阶段的阻塞判断 |

## 本例的活动来源

| ID | 来源 | 性质 |
| --- | --- | --- |
| [S1] | `data/experiments/CsI2021/experiment.yaml` | 项目配置；数据集、源、靶、探测器与输出字段。 |
| [S2] | `src/cevns_pyeft/experiments/coherent/sns.py` | 项目代码；SNS 通量及 flavor 状态。 |
| [S3] | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | 项目代码；效率、分量计数和 Slow 默认参数。 |
| [S4] | `src/cevns_pyeft/rates/differential.py` | 项目代码；quenching、Gamma 迁移核、截面接口。 |
| [S5] | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py` | 项目代码；Fast 构造入口。 |
| [S6] | `data/experiments/CsI2021/statistics/provenance.yaml` | 旧程序统计 provenance；明确不是官方完整 likelihood。 |
| [S7]、[S9] | `src/cevns_pyeft/statistics/datasets.py`、`statistics/likelihoods.py` | 项目代码；旧程序近似统计数组和 Gaussian χ²。 |
| [S8] | `data/experiments/CsI2021/README.md` | 项目说明；统计权威来源尚待核对。 |

当前活动目录中未找到 CsI2021 的官方论文 DOI/补充材料、[S1] 指向的 `workflows/experiment-integration/runs/CsI2021/` 产物或 `tests/reference_CsI2021/` 数组。因此本例展示**项目复现配置的填写方式**，不声称官方论文或外部逐箱结果已复现。

## 1. 实验身份、资料与目标【所有迁移必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 实验名称、运行期和唯一数据集名称 | COHERENT CsI；项目 `dataset_id=CsI2021`；运行标签 `2021_release_current_reproduction`。实际采数起止日期未登记。 | [S1] `dataset_id`、`run.period`；项目配置 |
| 本表覆盖的探测器或运行配置 | 一套 14.57 kg CsI[Na] 配置；Cs-133 与 I-127，PE 观测量，SNS 源。 | [S1] `run`、`detector` |
| 主要论文、补充材料、官方数据文件 | **缺失**：活动资料中没有可核对的 DOI、补充材料版本和官方数据文件。 | [S1] `provenance` 只指向项目文档 |
| 可选的旧程序或参考数组 | [S6] 提到 `cutoff_single.py`/`cutoff_multi.py`；[S1] 列出 Slow/Fast reference 路径，但这些文件当前不存在。 | 参考线索，不是可用外部基准 |
| 本次科学目标 | 展示源、靶、重建 PE 谱、9 个 PE bin 的 Slow 信号及 Fast 构造；统计只作旧程序近似示例。 | [S1] `expected_output`、`phase_boundaries`；[S8] |
| 结果性质 | **项目内 CsI2021 复现配置示例**；官方发表值、官方 likelihood 与最终验证状态待独立证据。 | [S1]、[S6]、[S8] |

## 2. 输出量与数据轴【所有迁移必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 真实核反冲量和单位 | 核反冲能量 `E_R`，keV；入射能量 `E_ν`，MeV。 | [S1] `detector.true_variable`、`source.energy_unit` |
| 最终观测量和单位 | 重建光电子数 `PE`。 | [S1] `detector.reconstructed_observable` |
| 希望保留的分量轴 | 源分量 `mu/e/mub` 和 `total`；Slow 内部还按 `Cs133/I127` 保存靶分量；每个输出数组有 9 bin。 | [S1] `expected_output`；[S3] `raw` |
| 输出是计数还是率 | 主输出为期望 `events/bin`；旧程序统计另用 `counts/PE`，通过每 bin 计数除以 PE 宽度得到。 | [S1] `expected_output.unit`；[S3] `counts_npe` |
| 精确 bin edges | PE：`[0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001]`；9 个相邻 bin，最后上边界保留。 | [S1] `binning` |

## 3. 中微子源【任何信号预测必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 入射粒子、flavor 或 flavor 状态 | `mu`：prompt `ν_μ`、`ρ=|μ⟩⟨μ|`；`e`：delayed `ν_e`、`ρ=|e⟩⟨e|`；`mub`：delayed `反ν_μ`、`ρ=|μ⟩⟨μ|`，另保留 `particle_kind=antinu`。 | [S1] `source`；[S2] `sns_component_state` |
| 需要分别输出的源分量 | `mu`、`e`、`mub` 与 `total`；`mub` 是源分量标签，不是第四个 flavor 态。 | [S2] `SourceSpecies`；[S3] `counts_bin` |
| 能谱公式或数值表 | `mu` 为由 π/μ 质量决定能量的 prompt 线；`e` 和 `mub` 为代码中的 Michel 连续谱，归一化到探测器位置的时间积分注量。 | [S2] `_michel_*_spectrum`、`muLine` |
| 能量范围及单位 | 插值表 `0.001–300 MeV`；非零物理节点掩码 `0.001–56 MeV`。谱与 prompt 线端点由代码公式决定。 | [S1] `source`；[S2] |
| 谱值单位与时间基准 | 连续谱 `cm^-2 MeV^-1`；prompt 线积分权重 `cm^-2`；已经按本项目的 POT 积分，不是每秒通量。 | [S1] `source`；[S2] 返回值 `measured` |
| 数值表处理规则 | 默认 200 节点线性插值；表外为零；配置记录末个物理支撑单元的插值衰减；prompt 线单独处理。 | [S1] `source.interpolation`、`boundary_behavior`；[S2] |

**绝对归一化只选一条路径：**

- [ ] A. 直接给定探测器位置的绝对通量/注量。
- [x] B. 从源量构造探测器位置注量：`N_POT=3.198×10^23`、每 POT 分量系数 `r=0.0848`、距离 `L=19.3 m`；每个 SNS 分量使用 `r N_POT/(4πL_cm²)` 一次。[S1]、[S2]。时间已经包含在 POT 中，不另乘 live time。

这是当前项目的计算路线；没有活动的官方通量表可作独立交叉检查。

## 4. 靶材、曝光、截面与运动学【任何信号预测必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 靶材料和同位素组成 | CsI，Cs:I 化学计量 `1:1`；项目使用 `Cs133` 与 `I127`。配置质量权重 `133/260≈0.511538` 与 `127/260≈0.488462`。 | [S1] `target`；[S3] `combine_equal_stoichiometry` |
| 靶核质量或摩尔质量来源 | 项目以 `A×1.6605390666×10^-27 kg` 近似单核质量（Cs `A=133`，I `A=127`）；这是代码约定，不是论文核质量表。 | [S1] `target.nuclei_per_kg_convention`；[S3] `A_TARGET` |
| 每台探测器的质量与活时间 **或** 已给出的曝光 | 质量 `14.57 kg`；活时间和 `kg·day` 曝光未独立登记。源注量已按 POT 积分，Slow 只乘探测器质量一次。 | [S1] `detector.detector_mass_kg`、`exposure.semantics` |
| 散射模型和参数点 | Slow 默认 `include_sm=True`、`sin²θ_W=0.2387`、`c10_mass_mode=quark_mass_resolved`；可输入 flavor 矩阵 Wilson 系数。无额外 EFT 系数时为项目 SM 默认点。 | [S3] `slow_counts_csi2021` |
| 核 form factor/Response 的要求 | `data/responses/responses_all.json`；Cs-133 key 为 `Cs133`，I-127 key 为 `I`；调用共享 Li2026 响应与截面链。 | [S1] `target.response_keys`；[S3] `target_specs` |
| 运动学和截面约定 | 两体弹性散射；`E_ν` 输入 MeV、`E_R` 输入 keV，共享差分接口输出 `cm²/keV`。边界由共享运动学函数决定。 | [S4] `differential_cross_section_nn` |

**物理边界：**代码保留 `ν/反ν` 标签，但反中微子相互作用 kernel 的专门审计仍待完成；本例不证明一般 EFT 反中微子截面。[S2]

## 5. 探测器响应【要求重建谱或逐箱计数时必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 真实反冲到观测量的平均映射 | 项目先令 `y=E_R/1000`，再用 `E_ee=1000(0.0554628y+4.30681y²−111.707y³+840.384y⁴)` 做 quenching，随后以 Gamma PE 核表示重建变量。 | [S4] `eee_quenching_csi`、`p_smearing_csi` |
| 分辨率或迁移核 | 对 `E_ee>0`，Gamma shape `k=1+9.56E_ee`、rate `λ=(0.0749/E_ee)k`，PE 只在正半轴；非正 `E_ee` 返回零。 | [S4] `p_smearing_csi` |
| 响应核的归一化范围 | 配置声明完整 `PE∈[0,∞)` 上归一化为 1；分析窗口外迁移概率不回填至 9 个 bin。 | [S1] `detector.response_normalization`、`migration_rule` |
| 效率/接受率 | 重建 PE 效率为 `max[1.32045/(1+exp{-0.285979(PE−10.8646)})−0.3333,0]`；源分量接受率 `mu/e/mub = 0.997/0.848/0.848`。 | [S1] `detector.efficiency_parameters`；[S3] `efficiency_csi2021` |
| 阈值、分析窗口和各探测器差异 | 分析区间 `0.001–60.001 PE`，见第 2 节。独立硬件阈值及多探测器差异未记录；第一条 bin edge 不能自动当硬件阈值。 | [S1] `binning`；部分缺失 |

## 6. 逐箱输出检查【要求逐箱计数时必填】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 分箱所用的观测量和单位 | 重建 `PE`。 | [S1] `binning` |
| bin edges 的文件或明确生成规则 | 第 2 节的 10 条显式 PE 边界；最后上边界保留。 | [S1] `binning.edges` |
| 分量输出的含义 | `mu/e/mub` 各源分量分别对 Cs-133、I-127 计算，再按 CsI 化学计量合并并施加分量接受率；`total=mu+e+mub`。 | [S3] `slow_counts_csi2021` |
| 计数归一化 | 已乘项目时间积分注量和 `14.57 kg` 质量的期望 `events/bin`；旧统计接口另除以 PE bin 宽度成为 `counts/PE`。 | [S1] `exposure`；[S3] `counts_bin`、`counts_npe` |

## 7. 统计分析【只在要求 likelihood、χ² 或置信区间时填写】

**项目旧程序的主要数据语义：**

- [ ] 原始逐箱计数
- [ ] 信号加背景计数
- [ ] ON/OFF 数据
- [x] 已扣除背景的 excess / residual（仅旧程序近似来源）
- [ ] 非分箱事件

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 观测数据文件及其 bin/探测器对应关系 | [S7] `CSI2021_OBSERVED_OVER_BIN_WIDTH`，9 个 PE bin，单位 `counts/PE`：`[1.021, 13.195, 18.941, 13.059, 11.043, 5.977, 1.838, 2.274, -0.831]`。末箱为负，不能按 raw Poisson 计数处理。 | [S7]；非官方数据文件 |
| 背景、OFF 数据或背景扣除方法 | [S7] `CSI2021_BACKGROUND_OVER_BIN_WIDTH` 是 BRN+NIN 旧程序近似；未找到可核对的官方 ON/OFF 数据。 | [S6]、[S7] |
| likelihood/χ² 公式或论文位置 | 项目 `chi2_csi2021` 为带信号和背景归一化 nuisance 的 Gaussian 双 pull χ²；官方 likelihood 公式定位缺失。 | [S9]；旧程序近似 |
| nuisance 参数、先验和相关性 | 旧程序信号归一化 `σ_α=0.125`，背景归一化 `σ_β=0.35`。 | [S6]、[S7] |
| 协方差/相关矩阵 | 项目有逐 bin 对称误差数组及上述 pulls；官方完整协方差/相关矩阵缺失。 | [S6]、[S7]；缺失 |
| 检验统计量和置信区间规则 | [S6] 记录旧程序 1D `Δχ²=2.71/3.84/6.63` 和某 2D 扫描的 `4.61`；官方区间构造与基准缺失。 | [S6]；只作旧程序参考 |

[S1] 标 `statistics_validated: false`，并把统计 callable 记为 `BLOCKED_PENDING_AUTHORITATIVE_PROVENANCE`。[S6] 明确该 Gaussian 路线不是官方完整 COHERENT likelihood。

## 8. 外部数值基准【要求复现论文或旧程序数值时填写】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 参考结果 | [S1] 指向 `tests/reference_CsI2021/slow_reference.npy`、`fast_kernel.npz`，但当前活动目录均无此文件；官方逐箱表格也未找到。 | 路径线索；基准缺失 |
| 生成参考结果的输入点 | [S3]、[S5] 默认 `sin²θ_W=0.2387`、`n_er=21`、`n_enu=120`、每 bin 8 个 PE 子点、`pe_step=3.0`。缺参考元数据，不能断言缺失数组以这些默认值生成。 | 代码默认值；参考配置待核对 |
| 参考值的单位、轴顺序和归一化 | 项目预测为 `events/bin`，分量 `mu/e/mub`；缺失的外部文件无法核对其轴、单位和背景含义。 | [S1]、[S3]；外部基准缺失 |
| 参考值的来源类型 | 活动资料只留项目配置中的路径与旧程序统计来源；没有可读取的官方表格、作者代码导出或 reference array。 | [S1]、[S6]；缺失 |

## 9. 补充项【仅在本次目标使用时填写】

| 项目 | CsI2021 填写示例 | 依据/状态 |
| --- | --- | --- |
| 通量、靶丰度、曝光、能标和背景的不确定度及相关性 | [S6] 仅给旧程序信号/背景归一化 pull `0.125/0.35`；其他官方误差及相关性未建立。 | 旧程序近似/缺失 |
| 源、探测器的时间变化或方向信息 | 项目采用 POT 积分后的 SNS 注量和一维 PE 计数；本例不做时间/方向分箱。 | [S1]、[S2]；不适用 |
| flavor 传播模型、密度矩阵 | 三源分量使用固定纯态投影矩阵，未提供随能量或路径变化的 `ρ(E_ν)`；`mub` 保留 `antinu` 标签。 | [S2]；能量依赖模型不适用 |
| Fast 表示的适用参数范围 | [S5] 构造 Li2026 矩阵化 EFT kernel，保留源分量、靶、通道轴；基底、flavor 约定与缓存元数据应对照 P07 验证。独立外部 kernel 基准和可宣称参数域缺失。 | [S5]、[S1]；项目实现与缺失并存 |

## 10. 缺失与冲突

| 字段 | 缺失或冲突的描述 | 已查过的来源 | 影响的计算目标 |
| --- | --- | --- | --- |
| 官方文献与数据版本 | 活动资料没有 CsI2021 论文 DOI、补充材料版本及官方观测数据路径。 | [S1]、[S6]、[S8] | 官方前向/likelihood 复现声明 |
| 外部 Slow/Fast 基准 | [S1] 所列 `tests/reference_CsI2021/` 文件当前不存在。 | [S1] 与活动文件检查 | 外部逐箱回归 |
| Phase 0 产物 | [S8] 指向 `runs/CsI2021/00_*`，但对应活动文件当前不存在。 | [S8] 与活动文件检查 | 审核历史追溯 |
| 统计 provenance | [S6] 仅给旧程序近似，没有官方完整 likelihood、协方差或 ON/OFF 数据。 | [S6]、[S7] | 官方统计结论 |
| 反中微子相互作用 | `particle_kind=antinu` 已记录，但代码说明反中微子 kernel 物理审计未完成。 | [S2] `sns_component_state`；[S8] | 一般 flavor/EFT 反中微子声明 |
| 阶段状态 | [S1] 标 `fast_validated`，[S8] 文字停在 `DATASET_VALIDATED only`；缺活动 run 报告解释差异。 | [S1]、[S8] | 最终完成状态可信度 |

本例示范**如何填写、引用来源、承认缺失和限定声明**。新增实验应复制[空白用户资料模板](EXPERIMENT_USER_INPUT_TEMPLATE.md)，用该实验自己的论文和数据填写。

[S1]: ../../../../data/experiments/CsI2021/experiment.yaml
[S2]: ../../../../src/cevns_pyeft/experiments/coherent/sns.py
[S3]: ../../../../src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py
[S4]: ../../../../src/cevns_pyeft/rates/differential.py
[S5]: ../../../../src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py
[S6]: ../../../../data/experiments/CsI2021/statistics/provenance.yaml
[S7]: ../../../../src/cevns_pyeft/statistics/datasets.py
[S8]: ../../../../data/experiments/CsI2021/README.md
[S9]: ../../../../src/cevns_pyeft/statistics/likelihoods.py
