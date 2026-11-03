---
name: cevns-kinematics-cross-section
description: Establish P05 elastic kinematics and differential-cross-section contracts with explicit masses, state coordinates, units, support and model validity.
---

# P05 — 运动学与微分截面合同

从 Master 或相关理论变更流程进入。遵循
[阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
使用 [P05 表单](../../../../_shared/templates/phase/P05_KINEMATICS_CROSS_SECTION_TEMPLATE.md)
和 [当前 API 参考](../../../../_shared/references/phase/P05_KINEMATICS_CROSS_SECTION_CODE_REFERENCE.md)。

## 目标与输入

把 P04 已明确的理论路线落实为 P07 可消费的截面接口。
所需输入是过程、靶核质量约定、能量/反冲变量、系数参数与入射态合同。
不重复批准未改变的 P04 内容，不加载通量或乘曝光、核数、效率。

## 1. 固定物理与接口

展示 Eν_min(T)、T_max(Eν)、支撑条件、截面公式及来源。
将精确运动学支撑与允许域内截面公式的近似分别记录。
核对同一个质量定义是否用于运动学、核响应和相空间因子。
明确：
- Eν/T/核质量单位、单次单位转换 owner、输出 dσ/dT 单位。
- incident_state 的能量坐标、particle_kind、flavor 轴、末态求和。
- 标量/数组形状、非法输入与合法但域外输入的区别。
- T=0/小反冲是否存在模型本身的奇异性及积分 cutoff；不强求所有模型在零点有限。
- full-response 与 SM 比较分支的参数范围。

存在新选择时取得 Physics Decision（已有入口为 `APPROVE KINEMATICS/CROSS-SECTION ROUTE`）。

## 2. 绑定现有实现

优先核对 InteractionModel.dsigma_dT、DifferentialCrossSection 与 ElasticKinematics。
Li2026LegacyInteraction 只在其实际核质量、响应与粒子处理约定适用时复用。
薄 adapter 可桥接单位、靶 key 和调用形状；不得在 adapter 内重定义共享物理或加入归一化。
非弹性过程、不同核质量或新理论若当前接口不能表达，列为扩展或 BLOCKED。

## 3. 验证

至少提供一个可独立复算的端点及逆关系；检查端点两侧、负/零能量、
小反冲、数组坐标与单位 Jacobian。用匹配的积分变量检查单位转换只发生一次。
按声明范围验证 SM、非零 EFT、复数/非对角 flavor 点和模型拒绝行为。
物理总截面在适用域应满足相应实数性/非负性；保留干涉分项的符号。

## 4. 交付

handoff：
`process_and_mass`、`kinematics`、`cross_section_api`、`units_and_axes`、
`support_and_limits`、`benchmark`。
提交公式—symbol—数值的对应关系及检查结果，完成 P05 结果审核后返回 Master。
P07 使用同一截面合同；P08 不得为了加速另换截面定义。
