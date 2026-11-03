# P04–P10 的执行与交接合同

本文件给 Master 和阶段 Skill 使用：先读本文件，再读当前阶段的 Skill、填写模板和代码参考。
任务路由仍由 routes.yaml 决定；这里定义阶段之间的物理依赖，不新增任务路由或批准权威。

## 从总体方案到交付

材料接入 → dataset identity 与 scientific claim → Phase 0 → P01–P03 →
P04/P05/P06 → P07 → 按需 P08、P09 → P10。

| 阶段 | 开始实施所需的内容 | 交给下游的结果 |
|---|---|---|
| P04 | 目标理论范围、P02 核素、P03 入射态需求 | 理论覆盖表、系数/响应约定、实现适用域 |
| P05 | P04 的有效理论约定、核质量和过程 | 运动学与微分截面接口合同 |
| P06 | P01 观测定义、P02 探测器/运行期、相关源分量标签 | 响应/选择算子及精确输出轴 |
| P07 | 当前输出实际需要的 P01–P06 已验证合同 | 直接积分结果、收敛证据、归一化台账、Slow 冻结 |
| P08 | 当前 P07 PASS 与用户批准的 Slow 冻结 | 每种 Fast 的参数域、缓存身份和逐箱误差 |
| P09 | 已验证并获相应接受的前向预测、统计输入与目标 | 数据语义、统计模型、推断范围和验证 |
| P10 | 本次交付所依赖的阶段结果 | 能力矩阵、验证层级、最终科学声明及接入结果 |

阶段编号是默认审查顺序，不是所有任务都必须执行的十个串行作业。
P06 的材料/响应分析可在其输入就绪后开展；是否推进由 Master 和已批准范围决定。
P09 使用 Slow 时不依赖 P08；使用某个 Fast 时依赖该表示的有效 P08。
P08 受阻不自动阻断 Slow 或采用 Slow 的统计；若原目标必须交付 Fast，最终只能报告部分完成，
不能静默删除该目标。只做 forward 时 P08/P09 可为 NOT_REQUESTED，P10 仍执行。

理论扩展或能力维护由相应 WORKFLOW 调用这些阶段的相关部分，使用明确的对象/变更范围；
不要求虚构新 dataset、重做 P01–P03 或取得无关批准。新实验才适用完整接入前置条件。

## 一次阶段的实际工作

1. 核对当前 scope、上游版本/指纹、批准引用和真实源码。已有效批准的物理选择不重复询问。
2. 从登记材料补齐当前必需字段；列出抽取、推导、近似、冲突及其影响。缺项定向返回 intake，
   补齐后回到本阶段；不重新扫描无关资料。
3. 展示需要新增/改变的物理决定：候选、证据、单位、有效域及对目标的影响。
   正式采纳按 [evidence-and-approval](../../policies/evidence-and-approval.md) 执行。
4. 先判断 REUSE/CONFIG_ONLY/ADAPTER/SHARED_EXTENSION/CORE_EXTENSION/BLOCKED，
   再在既有授权范围内实施或核查已有实现。授权按 [write-authorization](../../policies/write-authorization.md)。
5. 按本阶段预先确定的验收条件执行检查，保存可复算输出。接口烟雾测试不能替代收敛或外部基准。
6. 展示结果、差异和限制，取得本阶段所需的实际人工接受；写回权威记录，再返回 Master。
   Master 根据 [progress-continuity](../../policies/progress-continuity.md) 更新 checkpoint。
   阶段 Skill 不自己选择或自动进入下一个阶段。

[interaction](../../policies/interaction.md) 管用户可见表达；
[automation](../../policies/automation.md) 管隔离候选。隔离检查可以继续生成计划内候选，
但不得把候选 human_gate 写为 APPROVED，也不能推进原项目正式 Gate。

## 状态与记录

| 字段 | 取值与意义 |
|---|---|
| plan_status | READY / DRAFT / BLOCKED / NOT_REQUESTED；是否计划执行及当前准备情况 |
| machine_gate | NOT_RUN / PASS / BLOCKED；针对声明范围的实际技术检查 |
| human_gate | NOT_REVIEWED / APPROVED / REVISE / BLOCKED；用户对该版本结果的接受 |
| evidence status | 沿用共享政策中的六种状态；不借用 Gate 状态 |
| artifact freshness | 输入变化按依赖标为 STALE；STALE 不是 Gate 值 |

NOT_REQUESTED 的阶段不伪造 PASS/APPROVED。已有历史结果可作为带版本引用保留，
本次未请求的记录使用 NOT_RUN / NOT_REVIEWED。
P08 每种表示、P06 每种独立响应、P09 每个独立模型可各有一个 capability_id；
需要全部能力时 Master 汇总这些记录，不能用其中一个 PASS 覆盖其余项。

使用 [阶段报告](../../templates/phase/PHASE_REPORT_TEMPLATE.md) 保存物理解释和结果；
报告中的唯一 `json phase-result` 代码块按
[phase-result schema](../../schemas/phase-result.schema.yaml) 检查。无需为相同结论另建第二份状态权威。
`handoff` 保存阶段特定合同，`input_refs`、`evidence_refs`、`decision_refs` 指向原始权威记录。
`artifacts` 记录实际文件及 SHA256，`checks` 指向实际验证结果。
预先批准物理定义使用 decision_refs；结果接受使用 approval_refs，两者不可互相冒充。

结构校验只验证字段、条件和可选的文件指纹，不能认证人类回复、科学公式或外部证据。
人工批准必须能回溯用户对当前版本的实际决定；不要因 schema PASS 自动填写批准。
旧报告保持原样；在恢复受影响阶段时显式补充新版记录，历史批准不能自动升级。

## 修改影响与科学声明

保留 implementation manifest 中实际的输入依赖：理论/响应/源变更可能使 P07、对应 P08/P09/P10 失效；
仅统计数据变化通常只影响 P09/P10。物理 nuisance 改变 source/interaction/observation 时，
仍要沿真实依赖返回相应阶段，不能把它当作单纯统计文件变更。

P10 分别报告内部数值一致性、旧程序回归、论文 forward 复现、官方 likelihood 复现。
这些是独立的证据结论，不因前一项通过自动授予后一项。最终交付按原目标判定，
未满足的必需项明确报告部分完成；缩小科学目标需要实际科学决定。
