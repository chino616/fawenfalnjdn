# P10｜能力验收与最终科学声明

见 [P10 Skill](../../../cevns-pyeft/skills/phases/cevns-validation/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)、
[接入代码参考](../../references/phase/P10_VALIDATION_RELEASE_CODE_REFERENCE.md)。

## A. 交付目标

对象/dataset、版本、原目标、需交付的接口与科学声明：____。
本次是新接入 / 只读理论审核 / 理论变更 / 能力维护：____。
是否请求正式激活、物理文档或打包验证：____。
未满足原目标时明确部分完成；缩小目标的决定引用：____。

## B. 能力与 Gate

| 阶段/具体 capability_id | 计划状态 | Machine Gate | Human Gate | 输入版本/证据 | 可用能力与限制 |
|---|---|---|---|---|---|
| P01–P06 实际所需项（逐项列） | ____ | ____ | ____ | ____ | ____ |
| P07 Slow/冻结 | ____ | ____ | ____ | ____ | ____ |
| P08 每种表示（逐项列） | ____ | ____ | ____ | ____ | ____ |
| P09 每个统计模型（逐项列） | ____ | ____ | ____ | ____ | ____ |

计划状态：READY / DRAFT / BLOCKED / NOT_REQUESTED。
Machine：NOT_RUN / PASS / BLOCKED；Human：NOT_REVIEWED / APPROVED / REVISE / BLOCKED。
本次未请求项填 NOT_REQUESTED、NOT_RUN、NOT_REVIEWED，不伪造通过。
理论/能力维护引用相关既有合同，不补造无关阶段。

## C. 验证证据

| 层级 | 参考条件与来源 | 实际命令/结果文件 | 差异、精度与结论 |
|---|---|---|---|
| 内部数值一致性/收敛 | ____ | ____ | ____ |
| 旧程序/冻结数组回归 | ____ | ____ | ____ |
| 论文 forward 复现 | ____ | ____ | ____ |
| 官方 likelihood 复现 | ____ | ____ | ____ |
| 受影响既有实验回归 | ____ | ____ | ____ |

这些结论相互独立；缺失的外部证据按实际目标限制声明。

## D. 接入、审核与完成

候选 custom Catalog 验证、Definition/resources/load/predict/compile/evaluate、
unsupported capability、selection、active/spec_only/archived 检查：____。
拟正式变更、授权、回滚与正式验证结果：____。
已验证能力、近似、论文差异、允许/不允许的精确声明：____。
最终用户接受引用：____。
真实 dataset canonical 文档
`physics_docs/experiments/<experiment_slug>/<dataset_id>/experiment_physics.tex`
的生成/编译状态：____；非 dataset 工程工作用其变更报告。

handoff：delivery_scope、capability_matrix、validation_levels、runtime_integration、
final_claim、limitations。写入 [阶段报告](PHASE_REPORT_TEMPLATE.md)，由 Master 判定完成状态。
