# progress-continuity

## 11. MAINLINE_CONTINUITY_CONTRACT

### 11.1 可重建索引，不是权威记录

`MIGRATION_PROGRESS.md` 是 Master Skill 的可重建主线索引。它只回答：当前走到哪里、
引用哪些权威记录、满足什么条件后继续。它不是批准、证据或 Gate 结果的权威来源。
隔离自动运行有自己的候选进度；原项目索引在导入前不随候选阶段推进。

权责固定为：

| 内容 | 权威记录 | 进度索引只保存 |
|---|---|---|
| Dataset identity、scope、scientific claim | Decision Log 中的有效 `Dxxxx` 记录 | 决策引用 |
| 写入批准 | `AUTHORIZATION_LOG.yaml` 中的有效 `Wxxxx` 记录；日志尚未获准创建时为当前对话中的原始批准 | 授权引用 |
| 输入和运行证据 | Evidence Ledger、Physics Contract、Phase 报告 | 路径与指纹 |
| Machine/Human Gate | 当前 Phase 报告及批准记录 | 当前 Gate 摘要与引用 |
| 当前阶段和下一动作 | Master Skill 状态机 | 结构化 checkpoint |

读取进度索引本身绝不构成批准。索引里的 `APPROVED` 必须能解析到仍适用于当前
artifact revision 的权威记录；不能解析时降为 `NOT_REVIEWED` 或停止为 `BLOCKED`。

### 11.2 位置与单一当前索引

尚未批准 Dataset Identity 时，只有对应写入计划获批后才可创建：

```text
workflows/cevns-pyeft/.onboarding_tmp/<session_id>/MIGRATION_PROGRESS.md
workflows/cevns-pyeft/.onboarding_tmp/<session_id>/AUTHORIZATION_LOG.yaml
```

若没有这项写入批准，只在当前对话维持 checkpoint，不得声称具备跨会话恢复能力。

Dataset Identity、`experiment_slug`、Scope Gate 与正式路径写入均获批后，正式位置为：

```text
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
```

正式索引建立后成为唯一当前索引。临时索引可以保留指向正式路径的 handoff pointer，
但不得继续与正式索引并列更新。

### 11.3 Checkpoint 与 revision

checkpoint 必须使用 Master 认可的结构化 `step_id`，不得只用自由文本。允许的命名
族为：

```text
master.step0.scope
onboarding.step1.materials
onboarding.step2.dataset_identity
onboarding.step3.scientific_claim
master.phase0.scope_gate
phase.P01..P10.pre_code_decision
phase.P01..P10.implementation
phase.P01..P10.machine_gate
phase.P01..P10.human_review
phase.P01..P10.persist
master.route_next
```

写入前必须重新读取当前 `revision`。更新者只可在自己读取的 revision 仍为当前值时
写入 `revision + 1`，并记录 `previous_revision`。发现版本不一致时停止、重新读取权威
记录和最新索引，不得覆盖较新的 checkpoint。

只在以下事件后更新索引：

```text
阶段或结构化 step 推进
Machine/Human Gate 结果变化
正式 Physics Decision 产生或失效
blocker 变化
批准范围变化
显式暂停或恢复
关键输入、contract、代码或 evidence 指纹变化
临时索引向正式索引交接
```

普通问答、模型比较、解释、只读代码检查和其他不改变主线状态的旁支讨论，不更新
文件、不增加 revision、不改变 Gate。

更新顺序固定为：

1. 先写 Decision Log、Evidence Ledger、Physics Contract 或 Phase 报告等权威记录；
2. 核对本次写入仍在有效 `Wxxxx` 的路径和动作范围内；
3. 校验当前 revision；
4. 最后更新进度索引。

更新中断或索引损坏时，从权威记录重建，不得相信旧索引继续执行。

### 11.4 指纹变化与 Gate 失效

恢复时比较关键输入、contract、代码和 evidence 指纹。变化时：

- 直接受影响的 Machine Gate 置为 `NOT_RUN`；
- 对应 Human Gate 置为 `NOT_REVIEWED`；
- 依据 `00_IMPLEMENTATION_MANIFEST.yaml` 的实际依赖关系，使受影响的下游 Gate 失效；
- 相关 cache/reference/validation 标记为 `STALE`，但 `STALE` 不是 Gate 状态；
- 无依赖关系的已批准 Phase 保持不变。

历史批准记录保留，但不得作为新指纹版本的当前批准引用。改变 dataset identity 或
scientific claim 时必须重新进入 scope 和受影响 Physics Gate，不能只修改索引字段。

### 11.5 用户可见主线导航

活动中的迁移回复在“你还可以”块显示简短的中文导航；有多个 dataset 容易
混淆时再附 `dataset_id`。若正在等待明确的 Physics Decision 或 Write Approval，
在“当前状态”和“需要你做什么”说明停止位置及所需回复；“你还可以”只列
与该决定有关的查看、修改或暂停入口，不附通用导航菜单：

```text
主线进度：<实验名称> → <中文阶段/任务> → <正在等待的决定或下一步>
可回复：返回主线｜继续当前问题｜查看完整进度｜修改范围｜暂停
```

首次进入旁支时额外说明：当前旁支主题、主线断点、主线状态未改变。之后保持一行。
隔离自动运行中，导航必须标明“低自动/高自动候选”，并说明原项目进度未改变；
“返回主线”恢复当前隔离候选断点，“查看正式进度”只读原项目进度。
用户选择“修改范围”时重新进入 Scope/Physics Decision；“查看完整进度”只读取；旁支
中的偏好表达不能自动解释为 Physics Decision 或 `APPROVE WRITE`。
