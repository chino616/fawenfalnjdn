# P01–P10 阶段填写模板（通用字段与 CsI2021 结构例）

本文件是阶段模板索引。用户可以从下面选择当前 P 的独立模板直接填写，或提供论文/数据/旧程序让 AI 按同一模板摘录；最初也可先用[通用用户资料模板](../onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md)一次提供材料。每份 P 模板都有用户填写区、AI 核对区、验证与 Gate，避免要求用户编写程序。CsI2021 仅是函数结构示例；其 SNS 通量、Cs/I 靶材、PE 响应、分箱及旧统计数据均不是其他实验的默认值。

使用顺序由 [Master Skill](../../skills/cevns-experiment/SKILL.md) 决定。P01–P10 是 **Phase 1–10 的 Machine Gate ID**；onboarding 的 P00–P05 是产物文件名。Phase 0 先确定 dataset identity、科学声明和模块分类，再在各阶段按需补齐细节。P08/P09 未请求时，在阶段计划中记 `NOT_REQUESTED`。

## 独立填写文件

| 阶段 | 直接填写的模板 | 主要结果 |
| --- | --- | --- |
| P01 | [Dataset](P01_DATASET_TEMPLATE.md) | 数据集身份、观测量、分箱和输出契约 |
| P02 | [Target / Exposure](P02_TARGET_EXPOSURE_TEMPLATE.md) | 同位素、核数和曝光归一化 |
| P03 | [Source](P03_SOURCE_TEMPLATE.md) | 通量/注量、flavor、时间基准 |
| P04 | [Theory / Nuclear Response](P04_THEORY_RESPONSE_TEMPLATE.md)；[核响应实际代码参考](P04_NUCLEAR_RESPONSE_CODE_REFERENCE.md) | 共享理论链、可运行调用与核响应适用性 |
| P05 | [Kinematics / Cross Section](P05_KINEMATICS_CROSS_SECTION_TEMPLATE.md)；[运动学与截面代码参考](P05_KINEMATICS_CROSS_SECTION_CODE_REFERENCE.md) | 精确双体边界、截面单位和模型 |
| P06 | [Detector Response](P06_DETECTOR_RESPONSE_TEMPLATE.md)；[代码参考](P06_DETECTOR_RESPONSE_CODE_REFERENCE.md) | 真反冲到重建量、迁移、效率 |
| P07 | [Slow counts](P07_SLOW_COUNTS_TEMPLATE.md)；[代码参考](P07_SLOW_COUNTS_CODE_REFERENCE.md) | 直接积分、归一化台账和权威逐箱结果 |
| P08（可选） | [Fast counts](P08_FAST_COUNTS_TEMPLATE.md)；[代码参考](P08_FAST_COUNTS_CODE_REFERENCE.md) | 数学表示、缓存条件和逐箱 Slow 对照 |
| P09（按目标可选） | [Statistics](P09_STATISTICS_TEMPLATE.md)；[代码参考](P09_STATISTICS_CODE_REFERENCE.md) | 数据语义、likelihood/χ² 和推断规则 |
| P10 | [Validation / Release](P10_VALIDATION_RELEASE_TEMPLATE.md)；[代码参考](P10_VALIDATION_RELEASE_CODE_REFERENCE.md) | Gate 矩阵、回归与最终可宣称能力 |

**填写约定**：每个关键数值同时给单位及来源定位；缺失填“缺失”，不适用填“不适用”，冲突保留所有来源。多探测器、多运行期、源分量或 Fast 表示按单份模板说明复制记录。用户自行填写与 AI 从材料预填使用相同字段；AI 仍须核对证据、代码接口和复用性。填写表格不替代 Master Skill 所要求的物理决定与 Gate。

## 跨阶段代码契约与复用规则

- 模板中的函数名是**职责示意**，不是强制重命名指令。AI 先记录现有 `文件.symbol`、真实签名、输入输出单位、shape、flavor 轴、边界和错误行为，再决定调用或新增。
- 静态实验数值与数据文件归 `data/experiments/<experiment_slug>/<dataset_id>/`；`experiment_slug` 提供清楚的实验父目录，`dataset_id` 保持机器唯一。实验专有的源、响应或计数编排放在实验适配层。共享 theory、nuclear response、rates、kernels 只在物理定义真正通用时扩展，并核对既有实验回归。
- 逐函数判断：`REUSE`＝物理及接口完全适用；`CONFIG_ONLY`＝仅替换有来源的配置/数据；`ADAPTER`＝共享核心可用、需薄转换层；`SHARED_EXTENSION` 或 `CORE_EXTENSION`＝需扩大共享能力并审查影响；关键资料或适用性未定则 `BLOCKED`。
- 每个新增接口写明纯计算职责、输入输出、单位、数组轴、边界行为和来源；归一化因子只设一个 owner。不要把 CsI 专有通量、PE、靶权重或统计参数复制进通用函数。
- 用户可在各 P 文件只填写物理资料栏；AI 负责代码栏、验证和 Gate。AI 预填的物理字段必须保留原始来源和冲突状态。

## 各阶段共用记录块（复制到每份阶段报告）

| 字段 | 请填写 |
| --- | --- |
| experiment_name、experiment_slug、dataset_id、Phase/Gate ID、适用 Skill、目标 capability | `...` |
| 用户材料／AI 摘录；来源版本和页码、表号或文件行号 | `...`；标 `SOURCE_EXTRACTED`、`PROJECT_DERIVED`、`USER_CONFIRMED`、`REFERENCE_ONLY`、`MISSING` 或 `CONFLICT` |
| 已批准的物理定义、单位、适用域和输出轴 | `...`；记录 decision ID |
| 逐函数映射 | `所需职责 → 文件.symbol → 输入/输出/单位/数组轴 → 复用判断 → 验证` |
| 实施文件及最小动作 | `...`；现有通用函数优先核对其适用域 |
| 缺失字段回填 | `字段 → downstream_owner → needed_by_phase → 候选来源 → 阻断范围` |
| Machine Gate | `NOT_RUN / PASS / BLOCKED`；命令、结果和证据路径 |
| Human Physics Gate | `NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；决定与日期 |
| 对外允许的科学声明 | `...`；不得超过已验证的证据 |

复用判断使用 Master 的 `REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`。`REUSE` 仍须核对物理定义、单位、轴、flavor 和边界；`SHARED_EXTENSION`、`CORE_EXTENSION` 须单独审查影响范围。以下示例中的“候选”不表示新实验已获批准。

## P01 — Dataset：`cevns-dataset`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | publication / reproduction / phenomenology / legacy；运行期、包含与排除的探测器、观测量及单位、分析窗口、精确 bin edges、输出轴/shape/unit、观测数据模式、曝光语义及来源。 |
| 函数与复用 | `load_experiment_spec(config_path) → spec`；核对 `experiments/specs.py`、schema、bin 与路径验证。逐项填 `contract field → experiment.yaml key`；schema 不足时标 `BLOCKED` 或申请扩展。 |
| 产物／检查 | `data/experiments/<experiment_slug>/<dataset_id>/experiment.yaml`、`README.md`、`runs/<experiment_slug>/<dataset_id>/01_DATASET.md`；实验目录清晰、dataset ID 唯一、schema、loader、bin 数与输出 shape、data mode。 |
| CsI2021 结构例 | `data/experiments/CsI2021/experiment.yaml` 和 `experiments.specs.load_experiment_spec` 展示配置及装载入口；其数值和 reference 路径需重新核查。 |

## P02 — Target / Exposure：`cevns-target`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 材料、逐同位素丰度及 number/mass fraction 约定、摩尔质量来源、每台探测器有效质量、活时间 **或** kg·day 曝光、每个同位素的核 Response key。 |
| 函数与复用 | `composition → nuclei_per_kg`；`ResponseDB.get(key) → nuclear response`。列出核数/质量的推导和单位；质量与活时间或已给 kg·day 曝光须明确归一化 owner。最终时间因子还须与 P03 的 `flux/fluence` 时间基准核对。 |
| 产物／检查 | `runs/<experiment_slug>/<dataset_id>/02_DETECTOR_TARGET.md`；丰度和、核数可复算、Response key 存在、时间与曝光未重复相乘。通常无需新建 `target.py`。 |
| CsI2021 结构例 | `nuclear.response.ResponseDB.get` 是候选通用入口；`slow_counts_csi2021.combine_equal_stoichiometry` 的 Cs/I 等化学计量仅作结构参考。 |

## P03 — Source：`cevns-source`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 各分量及 flavor/ν或反ν状态、谱公式或表、能量支撑、插值/拼接/外推、通量或注量单位、每秒或时间积分基准、绝对归一化及不确定度。反应堆须在探测器位置绝对通量与功率/裂变率/基线推导中选一条计算路径。 |
| 函数与复用 | `flux_or_fluence(component,Eν) → differential source`；`state(component,Eν) → ρ(Eν), particle_kind`。只输出源，不乘靶核、曝光、探测器响应或分箱。 |
| 产物／检查 | 配置表或最薄 source adapter；支撑区间、积分归一化、分量和、边界连续性、单位、标量与数组行为、诊断曲线。 |
| CsI2021 结构例 | `coherent.sns.loadNeutrinoEmpiricalFluxSNS`、`sns_component_state` 是 SNS 专用；`sources.state.NeutrinoState` 是候选共用状态接口。 |

## P04 — Theory / Nuclear Response：`cevns-theory-response`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 要求的 SM/EFT 模型、系数基底及顺序、flavor 与复系数约定、同位素核响应、需保留与省略的通道、比较模型及有效域。 |
| 函数与复用 | 记录 `Wilson → nucleon matching → nuclear response → amplitude contraction` 的实际文件与 symbol。逐项核对 Response key、flavor 路由及共用 differential API；完整核响应后不得再次乘 Helm。 |
| 产物／检查 | 共享理论回归、Response key/通道、复系数、SM benchmark；共享或核心扩展须说明对既有实验的影响。 |
| CsI2021 结构例 | `rates.differential.differential_flavor_kernel_nn` 是候选通用调用点；新实验须核对理论模型和 ν/反ν 约定。 |

## P05 — Kinematics / Cross Section：`cevns-kinematics-cross-section`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 入射能、真实反冲能、核质量、`dσ/dT` 单位、弹性运动学和近似、比较模型有效域；给出特殊积分边界的出处。 |
| 函数与复用 | `Eν_min(T)`、`T_max(Eν)`、`dσ/dT(Eν,T,target,model)`；记录物理支撑、单位桥接和 flavor 收缩。实验 adapter 仅处理必要的靶/源接口转换。 |
| 产物／检查 | 端点与逆关系、支撑域外行为、单位换算、SM 正定性适用域、EFT 参数点；展示一个可复算端点。 |
| CsI2021 结构例 | `rates.differential.differential_cross_section_nn` 是候选共用函数；须实测新靶与新模型的接口兼容性。 |

## P06 — Detector Response：`cevns-detector-response`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | `T →` 重建量的平均映射及单位、淬火/yield、分辨率或迁移矩阵、效率作用域、阈值、分析窗口/bin、探测器差异；逐参数标官方、数字化或近似。 |
| 函数与复用 | `mean_reconstructed_observable(T)`、`response_density(x|T)`、`efficiency(x或T)`；写清响应全域归一化和效率施加位置。此层不加载源、不算截面、不乘曝光。 |
| 产物／检查 | 映射、响应切片、效率曲线；非负性、归一化、均值/宽度、边界及数组广播。阈值不自动等于阶跃效率。 |
| CsI2021 结构例 | `rates.differential.eee_quenching_csi`、`p_smearing_csi`、`slow_counts_csi2021.efficiency_csi2021` 的接口可参考；PE 物理参数不可移植。 |

## P07 — Slow authoritative counts：`cevns-slow-counts`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 最终计数轴、源/靶/探测器分量输出、每项归一化来源、积分域及参考数值或可验证的收敛要求。 |
| 函数与复用 | `source × dσ/dT × nuclei_per_kg × target mass × time factor(if needed) → dN/dT → detector fold → events/bin`。逐因子记 owner、文件.symbol、输入输出单位；每秒通量按批准的活时间积分，已按运行期积分的注量不再乘活时间。Slow 必须直接积分，不依赖 Fast kernel 或整体重标定。 |
| 产物／检查 | 逐分量和逐 bin、总计、真实与重建谱、网格/容差、归一化检查点；收敛、曝光缩放、支撑域、适用时复系数点及外部参考。P07 Machine PASS 后另需用户批准 Slow 为权威参考。 |
| CsI2021 结构例 | `rates.counts.bin_events_csi` 和 `slow_counts_csi2021.slow_counts_csi2021` 展示积分编排；SNS、Cs/I、PE 与 9 bin 是专有细节。 |

## P08 — Fast（可选）：`cevns-fast-counts`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 加速目的、参数域、误差目标和应用场景；先确认 P07 PASS 且 Slow freeze 已批准。 |
| 函数与复用 | 每种表示单独选 `reconstructed_spectrum_cumulative`、`detector_response_matrix`、`eft_quadratic_coefficient_kernel` 或定义清楚的其他 surrogate。记录构建输入、缓存轴/单位、失效条件、理论空间、构建与评价成本。 |
| 产物／检查 | 逐 bin 列 Slow、Fast、绝对/相对差、容差；覆盖多个参数点和边界，不以总数或全局比例替代。每种表示独立 Gate。 |
| CsI2021 结构例 | `fast_kernel_csi2021.build_fast_kernel_csi2021`、`kernels.reconstruction.reconstruct_from_full_kernel_flavor` 展示重建结构；SNS/CsI 绑定和 ν/反ν kernel 审计限制必须记录。 |

## P09 — Statistics（按目标可选）：`cevns-statistics`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 一种主要数据语义：`raw_counts`、`signal_plus_background`、`on_off`、`background_subtracted_excess` 或 `unbinned_events`；观测数据、bin 对齐、背景、协方差、nuisance、先验/相关性、统计量、区间构造及基准。 |
| 函数与复用 | `signal prediction → expected observable → likelihood/χ² → profiling/scan`；记录每项公式、数据文件、输入 shape/unit 和共享统计 API 是否适用。 |
| 产物／检查 | toy 值、nuisance profiling、发表基准及差异。缺官方 ON/OFF、背景或协方差时，不得声称官方 likelihood；只实现 forward model 可将 P09 记 `NOT_REQUESTED`。 |
| CsI2021 结构例 | `statistics.datasets.csi2021_dataset`、`likelihoods.chi2_csi2021` 属旧程序统计参考，不自动等于官方 likelihood。 |

## P10 — Validation / Release：`cevns-validation`

| 待填写项 | 内容 |
| --- | --- |
| 用户材料／AI 提取 | 可复现的外部基准、目标科学声明、已知近似、发表结果与本实现差异；没有基准时明确能验证到哪一层。 |
| 函数与复用 | `config → source/target/theory/detector → Slow → optional Fast/statistics → registry`；逐层保存对照输出。注册仅暴露机器与物理 Gate 均通过的 capability。 |
| 产物／检查 | 全阶段 Gate 矩阵、dataset 与共享回归、既有实验回归、缓存版本、registry discovery；区分内部一致性、旧程序回归、发表 forward 复现和官方 likelihood 复现。最终科学声明需用户批准。 |
| CsI2021 结构例 | `experiments.registry` 是候选共用暴露位置；若配置所列 `tests/reference_CsI2021/*` 或 `runs/CsI2021/00_*` 在活动目录缺失，记录 `MISSING`，不能宣称相应 reference 回归通过。 |

阶段实际报告仍使用 [PHASE_REPORT_TEMPLATE.md](PHASE_REPORT_TEMPLATE.md) 记录代码变更、公式、单位、测试和 Gate。本文件给出各阶段该填什么；[CsI2021 核心函数结构](CsI2021_CORE_FUNCTION_STRUCTURE.md) 提供函数职责和复用依据。
