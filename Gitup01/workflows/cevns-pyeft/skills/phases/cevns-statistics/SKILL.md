---
name: cevns-statistics
description: Establish P09 observed-data semantics, likelihood and inference contracts for validated predictions while distinguishing required inputs and approximate versus official claims.
---

# P09 — 数据语义、统计模型与推断

遵循 [阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
使用 [P09 表单](../../../../_shared/templates/phase/P09_STATISTICS_TEMPLATE.md)
和 [当前统计绑定](../../../../_shared/references/phase/P09_STATISTICS_CODE_REFERENCE.md)。

## 1. 核对目标与预测

只做 forward 且未请求统计时计划为 NOT_REQUESTED。
统计可使用已验证并获相应接受的 Slow，不要求 P08；采用 Fast 则引用该表示的有效 P08。
区分仅计算目标函数、寻找最佳拟合、给区间或显著性；后两者还需要明确的推断规则。

## 2. 分通道确认观测语义

每个独立通道分别记录四个维度，不把它们混成互斥菜单：
- representation：binned_counts / binned_density / unbinned_events；
- processing：raw / background_subtracted / other；
- design：single_sample / on_off / control_region / joint；
- likelihood：poisson / gaussian / other，并给实际公式。

依据来源定义，不根据整数或负数猜测。核对 bin/事件轴、单位、曝光、
背景是否已扣除、ON/OFF 比例和观测数据版本。
需要新增数据解释时取得 `APPROVE DATA MODE`；后续模型和推断改变另记科学决定。

## 3. 定义统计与 nuisance 合同

固定背景、误差模型、所需协方差/相关性、nuisance 的作用位置/范围/先验、
实际 logL 或 χ²、profiling/marginalization 和外部 benchmark。
仅在所选模型或声明必需的输入缺失时 BLOCKED：
独立 Poisson 不自动要求外部 covariance；Gaussian 对角近似必须有明确依据与接受。
background_subtracted excess 不能直接进入 raw Poisson。
只有总计/显著性不足以重建官方 likelihood；缺官方输入时不得静默改为近似 χ²。

若 nuisance 改变源、截面、响应或选择，应声明其 forward 依赖与重算/缓存策略；
不能用没有证据的总归一化 pull 代替形状变化。
联合通道需明确共享 nuisance/相关性及实际 executor 支持。

## 4. 绑定、验证与推断

优先走 StatisticsDefinition 与 evaluate_experiment，核查预测身份、观测映射与统计资源。
其他接口需给出最薄 adapter 和独立合同，不把旧 CsI Gaussian 当新实验默认模型。
单位/箱宽转换只执行一次；covariance 随相应变换一致转换。

检验 toy/可解析点、无效输入、nuisance 边界与极值、优化收敛和可能的多极小值。
区间/显著性须检查自由度、边界、可辨识性及阈值依据；渐近条件不足时采用有依据的 toys
或限制声明，不能把默认 Δχ² 阈值当通用定理。
记录发表 benchmark 的条件与差异，不要求不存在的官方结果来证明内部数值检查。

## 5. 交付

handoff：
`channels`、`prediction_binding`、`required_inputs`、`nuisance_model`、
`inference`、`claim_level`、`benchmark`。
channels 中明确 requires_covariance；需要时给 covariance_ref。
claim_level 为 internal / legacy_regression / approximate / official_likelihood；
仅按实际证据宣称。P09 技术检查与用户结果接受完成后交回 Master。
