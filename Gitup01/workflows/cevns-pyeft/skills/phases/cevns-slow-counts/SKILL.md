---
name: cevns-slow-counts
description: Produce P07 direct event-count predictions, verify normalization and convergence, and freeze a versioned Slow reference for requested downstream capabilities.
---

# P07 — 直接积分与 Slow 基准冻结

遵循 [阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
使用 [P07 表单](../../../../_shared/templates/phase/P07_SLOW_COUNTS_TEMPLATE.md)
和 [当前积分路径](../../../../_shared/references/phase/P07_SLOW_COUNTS_CODE_REFERENCE.md)。

## 1. 核对计算范围与前置条件

本次输出实际依赖的 P01–P06 合同须已验证并获必要接受，且输入指纹仍有效。
先确定返回真实反冲产额、重建谱还是 events/bin，以及要保存的分量。
若目标只需真实反冲产额，显式记录不使用 P06 的原因和独立输出合同，
不能把它标为已完成探测器折叠或完整 runtime 计数能力。

## 2. 先闭合归一化台账

逐因子记录定义、单位、代码 owner 和已包含内容，选择与实际实现相符的路线：
- 已积分探测器注量 × 每核截面积分 × 实际核数；
- 或每秒通量 × 已明确的活时间 × 每 kg 率 × 质量；
- 其他等价路线须给出单位推导，禁止两条路线混乘。

当前组合式实现使用 for_run 产生的注量、每核 recoil yield、实际 number_of_nuclei。
线谱用积分注量直接求和，不再乘连续谱能量箱宽。
P06 返回已含选择的概率时不再乘同一效率。
需要新决定时展示台账并取得 `APPROVE NORMALIZATION LEDGER`。

## 3. 直接计算

优先采用当前 ExperimentModel / predict_experiment 或适用的共享积分组件；
以实际 executor 为准保留不同实验的数值策略。
Slow 不依赖 EFT kernel、重建谱 cumulative cache 或全局重标定。
复用 P06 规定的响应表不等于依赖 P08；该表若来自加速近似，须有独立精度证据。
不复制 CsI/SNS 的质量、源分量、PE 网格或实验专有折叠。

保存逐 bin 和可分辨的源/同位素/探测器分量、总计、真实谱、
重建诊断、积分范围与实际网格、参数点及归一化检查点。
旧兼容返回的 raw 分量可能尚未施加材料权重或选择，不能直接当最终分量求和。

## 4. 验证数值与科学范围

分别改变 Eν、T、重建量求积精度，检查边界、线谱、阈值和尾部贡献。
预先给出逐 bin 绝对/相对容差；近零 bin 使用绝对误差。
检查分量和、质量/注量缩放、支撑域、总计的有限性和非负性；
干涉分项允许有符号。按声明域覆盖适用的复系数和 flavor 点。
外部参考按来源、条件及精度比较，缺失时明确限制声明；内部收敛不等于论文复现。
小网格接口演示不得冻结为科学基准。

## 5. 冻结与交接

handoff：
`normalization_ledger`、`output_contract`、`numerics_and_convergence`、
`reference_comparison`、`freeze_scope`。
freeze_scope 列明输入/代码/参数域、网格、容差、输出文件指纹以及证据等级；
共同记录按阶段报告保存，不另建相互冲突的冻结权威。

Machine P07 PASS 后展示逐箱、总计、收敛和限制，取得
`APPROVE SLOW AS AUTHORITATIVE REFERENCE` 对当前版本的接受。
只有这个有效冻结可供 P08 作为基准。Master 随后可安排 P08、使用 Slow 的 P09，
或仅 forward 的 P10；不强制构建 Fast。
