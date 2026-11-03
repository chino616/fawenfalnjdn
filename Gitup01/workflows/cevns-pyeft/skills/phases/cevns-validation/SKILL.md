---
name: cevns-validation
description: Complete P10 capability and scientific-claim validation, verify current runtime integration and release only the reviewed scope with traceable evidence.
---

# P10 — 能力验收、接入与最终科学声明

遵循 [阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
使用 [P10 表单](../../../../_shared/templates/phase/P10_VALIDATION_RELEASE_TEMPLATE.md)
和 [接入代码参考](../../../../_shared/references/phase/P10_VALIDATION_RELEASE_CODE_REFERENCE.md)。

## 1. 按交付目标收集有效证据

读取 Phase 0/变更范围、当前合同、阶段报告及其有效指纹和批准。
分别列 plan_status、machine_gate、human_gate、证据及能力，不混用 NOT_REQUESTED 与 Gate。
P08/P09 未请求不阻断已满足目标的 Slow 交付；已请求但缺失则保留部分完成。
理论审核/变更和能力维护仅验收本次范围及受影响下游，不要求创建新 dataset 或虚构全部阶段批准。

## 2. 分层验证

逐项记录实际运行命令、参考条件、差异和证据：
- 内部数值一致性：单位、轴、归一化、收敛与适用的 Fast 对照。
- 旧程序回归：与明确版本的历史实现/冻结数组一致。
- 论文 forward 复现：指定论文图表、条件、数字化及模型误差。
- 官方 likelihood 复现：指定版本的官方统计输入、模型和推断。

前一层通过不授予后一层。针对本次改变运行目标测试和相关共享/既有实验回归；
核对缓存失效、资源哈希和实际 backend。不得改 reference、容差或物理输入强迫通过。
没有触及物理实现的文档维护不要求无关数值回归。

## 3. 验证 runtime 接入

新实验先在 ExperimentCatalog(builtins=False) 验证 Definition、ResourceCatalog、
load_experiment、predict_experiment，以及已请求的 compile/evaluate。
检验 unsupported capability 会明确拒绝，不能靠 metadata 宣称实现。
Manifest/Catalog 是活动身份权威，旧 registry 是兼容视图；
spec_only/archived 不能进入默认计算。核对 selection 与资源作用域。

先完成候选接入验证和可审核差异，再处理正式激活。
已有实验能力修改不自动新增 manifest 项；仅科研输出也不强制正式激活。

## 4. 最终审核与完成

向用户展示：已验证能力、未满足目标、已知近似、论文差异、实际验证等级、
允许与不允许的科学声明，以及拟暴露的接口和正式变更。
取得 `APPROVE FINAL STATUS` 对精确范围的接受；它不替代另有要求的写入授权。
在有效授权内执行必要接入，再验证正式状态；失败则报告未完成，不写 FULLY_INTEGRATED。

handoff：
`delivery_scope`、`capability_matrix`、`validation_levels`、
`runtime_integration`、`final_claim`、`limitations`。
按已获接受的合同生成 canonical 物理文档：
`physics_docs/experiments/<experiment_slug>/<dataset_id>/experiment_physics.tex`；
该路径仅适用于真实 dataset，工程变更使用其变更报告。
文档生成/编译状态必须如实记录。请求了打包验证时交给 release-validation；
它不能补足物理证据或代替最终科学接受。

权威报告及正式验证成功后返回 Master，由 Master 更新完成索引。
未实现能力保留 BLOCKED/NOT_IMPLEMENTED 的准确能力描述，不能为了“完成十步”伪造通过。
