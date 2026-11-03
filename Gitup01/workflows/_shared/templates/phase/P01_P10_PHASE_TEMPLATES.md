# P01–P10 阶段模板索引

由 [Master Skill](../../../cevns-pyeft/skills/router/cevns-experiment/SKILL.md)安排当前阶段。
用户可填写物理资料，或提供材料由 AI 提取；函数映射、实现与验证由 AI 完成。
填写不等于物理批准。Phase 0 先明确身份、科学目标、范围和已知缺口，细节到使用阶段再补齐。

| 阶段 | 独立模板 | 阶段交付 |
|---|---|---|
| P01 | [Dataset](P01_DATASET_TEMPLATE.md) | 身份、观测量、分箱与输出要求 |
| P02 | [Target / Exposure](P02_TARGET_EXPOSURE_TEMPLATE.md) | 核素、实际核数和曝光约定 |
| P03 | [Source](P03_SOURCE_TEMPLATE.md) | 源分量、通量/注量、入射态和支撑 |
| P04 | [Theory / Nuclear Response](P04_THEORY_RESPONSE_TEMPLATE.md) | 理论覆盖、系数与响应约定、证据限制 |
| P05 | [Kinematics / Cross Section](P05_KINEMATICS_CROSS_SECTION_TEMPLATE.md) | 运动学与截面接口、单位和有效域 |
| P06 | [Detector Response](P06_DETECTOR_RESPONSE_TEMPLATE.md) | 响应密度或逐箱概率、选择归属、观测轴 |
| P07 | [Slow](P07_SLOW_COUNTS_TEMPLATE.md) | 直接积分、收敛、归一化和可复算冻结 |
| P08 | [Fast（可选）](P08_FAST_COUNTS_TEMPLATE.md) | 每种表示的参数域、缓存合同和误差 |
| P09 | [Statistics（按目标）](P09_STATISTICS_TEMPLATE.md) | 数据语义、统计模型和推断范围 |
| P10 | [Validation / Release](P10_VALIDATION_RELEASE_TEMPLATE.md) | 目标验收、接入结果与最终科学声明 |

## 依赖与填写方式

P04–P10 统一遵循 [执行与交接合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)。
P07 消费所需的 P01–P06；P08 要求有效 Slow 冻结；P09 可直接使用 Slow；
采用 Fast 时才依赖对应 P08。P10 根据本次目标验收，未请求的可选能力不伪造 PASS。

每个数值提供单位、版本和来源定位；缺失写明 owner、needed_by_phase、候选来源和阻断范围，
冲突保留全部证据。复用分类沿用 REUSE / CONFIG_ONLY / ADAPTER /
SHARED_EXTENSION / CORE_EXTENSION / BLOCKED，不为示例方便复制实验专有物理。
每个独立响应、Fast 表示或统计模型保留清楚的 capability_id 和适用范围。

实际结果使用 [阶段报告](PHASE_REPORT_TEMPLATE.md)。
P04–P10 的代码参考从各独立模板进入；
[CsI2021 当前调用结构](../../references/phase/CsI2021_CORE_FUNCTION_STRUCTURE.md)
用于 Phase 0 复用分析，其参数不作为新实验默认值。

P01–P10 是阶段/Gate ID；onboarding 的 P00–P05 是材料产物文件名，两套编号不混用。
计划状态、机器检查和人工接受分别记录；NOT_REQUESTED 只在计划状态栏。
