# scientific-integrity

## 7. PRE_DATASET_FREEZE

在 Dataset Identity Gate `human_gate=APPROVED` 前：

允许读取任意相关资料和仓库文件。
下列冻结约束原项目的正式路径；`workflows/_shared/policies/automation.md` 中的独立候选副本
可以整理未获批准的材料，但不能由此创建正式 dataset 或解除冻结。
只有在用户明确批准 `[WRITE PLAN]` 后，才允许写入：

```text
workflows/cevns-pyeft/.onboarding_tmp/<session_id>/
```

仅限：source register、candidate list、临时 evidence extraction。

经 `[WRITE PLAN]` 明确列出并获得 `APPROVE WRITE` 后，也允许在同一 session 目录写：

```text
MIGRATION_PROGRESS.md
AUTHORIZATION_LOG.yaml
```

二者只记录临时 onboarding 主线和已发生的写入授权，不解除
`PRE_DATASET_FREEZE`，也不授权任何正式 run、data、src、tests 或 registry 写入。

禁止：

```text
创建/重命名正式 runs/<experiment_slug>/<dataset_id>/
修改任何现有 runs/*/*/00_* 或 legacy `runs/*/00_*`
创建 P01-P05 正式 onboarding 产物
创建/修改 data/experiments/<experiment_slug>/<dataset_id>/
修改 src/
修改 tests/
修改 registry
对上述文件执行 backup
把 placeholder 目录解释为真实 dataset
```

原因：未获得 dataset identity 批准，也未获得写入批准，因此 backup rule 尚未触发。


## 8. task_scope 隔离

允许：

```text
physics_onboarding
existing_dataset
skill_debug
```

`skill_debug` 下禁止创建真实 dataset、批准真实 physics contract 或修改 production files。若用户后来要转为真实接入，必须回到 Master Step 0 重新选择 scope。

`skill_debug` 下也不得自动创建 mock 文件。若需要写 mock state、candidate list、
evidence ledger、README 或 scope gate，必须先通过 Write Approval Gate。
两档隔离自动运行只用于真实的 `physics_onboarding` 或 `existing_dataset`，
不把 `skill_debug` 的 mock 文件写入作为自动模式的例外。


## 10. PROGRESSIVE_DETAIL_LOOP

experiment integration 采用“整体方案优先、细节按需回填”：Phase 0 先冻结 dataset
identity、scientific claim、模块分类、阶段计划和已知 blocker，不要求在开始 Phase 1
前穷尽所有数值表、参考数组或可选 capability 的细节。

尚未到使用阶段的字段保持现有的 `DRAFT`、`MISSING` 或 `BLOCKED` 状态，并记录：

```text
downstream_owner
needed_by_phase
candidate_sources
blocking_scope
```

不得为“以后再补”创建新的 evidence status，也不得把 `MISSING` 写成默认值。到达某个
Phase 后，若该 Phase 的必需字段不足，向用户说明缺少的具体内容、它阻断了
当前哪项工作，以及将从已有材料补充哪些信息；必要时再询问用户。补齐后返回
原阶段的暂停位置。规则名和字段 ID 仅在审计或调试时展开。

回填循环固定为：

1. 只定位当前 Phase 所需字段，不重新无范围扫描整个仓库；
2. 优先从已登记材料提取；仍缺失时再询问用户是否有补充文件；
3. 新材料按 onboarding 的多文件对比规则登记独立 `source_id`，保留冲突 claim；
4. 物理语义新增或改变时执行 Physics Decision；任何写入仍执行 Write Approval Gate；
5. 更新 evidence、missing matrix 和 partial contract；
6. 只将受影响 Phase 及其依赖下游的 Human Gate 置回 `NOT_REVIEWED`，并使相关
   reference/cache/validation 失效；无关的已批准阶段保持不变；
7. 返回原来暂停的 Phase，从其 pre-code review 继续，不重新开始 Step 0。

如果缺失字段阻断当前 Phase，则该 Phase 不得进入技术实现或伪造 Machine PASS。
可选 Fast/statistics 的缺失只阻断对应 capability。所有回填仍执行
`BACKUP_QUARANTINE`，不得从 `backup/**` 自动补料。
