# P09｜数据、统计模型与推断

见 [P09 Skill](../../../cevns-pyeft/skills/phases/cevns-statistics/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)、
[当前统计绑定](../../references/phase/P09_STATISTICS_CODE_REFERENCE.md)。

## A. 用户目标与数据

目标：目标函数 / 最佳拟合 / 区间 / 显著性；具体定义与来源：____。
预测来源：已验证 Slow / 指定已验证 Fast；版本和接受记录：____。
仅 forward 且未请求统计时计划填 NOT_REQUESTED。

每个通道分别填写，不把这些维度当互斥模式：
| channel ID | representation | processing | design | likelihood | 数据定义与来源 |
|---|---|---|---|---|---|
| ____ | binned_counts / binned_density / unbinned_events | raw / background_subtracted / other | single_sample / on_off / control_region / joint | poisson / gaussian / other | ____ |

## B. 统计合同

| 内容 | 定义、数值/单位与来源 |
|---|---|
| observed/背景/控制区数据，版本与轴 | ____ |
| 预测到观测的映射、箱宽/单位转换 | ____ |
| 背景扣除状态、ON/OFF 比例 | ____ |
| 所需误差和相关性 | ____ |
| 每通道 requires_covariance | true / false；依据 ____；需要时 covariance_ref ____ |
| nuisance、先验、范围、共享相关性 | ____ |
| 物理 nuisance 的 forward 依赖与重算规则 | ____ |
| 实际 logL/χ² 公式及常数项约定 | ____ |
| profiling/marginalization、优化和多极小值 | ____ |
| 推断统计量、阈值、边界、渐近条件或 toys | ____ |
| 外部 benchmark 与对应条件 | ____ |

缺少所选模型必需输入才阻断对应统计；不自动要求所有模型都有 covariance。
background_subtracted excess 不进入 raw Poisson。
官方输入缺失不自动降级为近似模型；目标改变须明确接受。

## C. 实现与验收

实际 StatisticsDefinition/evaluate_experiment 或明确 adapter：____。
验证身份、轴、单位变换一次、toy/可解析点、nuisance 边界、优化与推断条件。
handoff：channels、prediction_binding、required_inputs、nuisance_model、inference、
claim_level、benchmark。claim_level 取 internal / legacy_regression / approximate / official_likelihood。
用 [阶段报告](PHASE_REPORT_TEMPLATE.md) 保存命令、结果和用户接受，再返回 Master。
