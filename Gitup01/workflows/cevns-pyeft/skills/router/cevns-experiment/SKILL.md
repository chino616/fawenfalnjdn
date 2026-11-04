---
name: cevns-experiment
description: Single master workflow for CEvNS onboarding, runtime migration, repository and README maintenance, archive/resource audits, and release validation. Owns routing, user-visible state, ambiguity gates, and phase transitions.
---

# cevns-experiment — 唯一 Master Skill

## Purpose

正式数据交付按[package 编译器入口](../../../../../tools/compile_experiment_package.py)：
用户填写、AI 摘录或混合资料形成同一 IR，之后由确定性 compiler 生成 YAML/NPZ/Physics MD。
Master 只路由，不理解或执行公式；机器检查与人工 Physics Review 独立，Runtime 不读中间台账。

所有“新增实验 / 从论文接入 / 继续已有 dataset / 仓库与 README 维护 / Skill 调试”都从本 Skill 开始。

本 Skill **只负责状态机和阶段路由**，不亲自实现 source、detector、Slow 等物理代码。

涉及接收、整理或修改实验输入时，先读[共同输入规范](../../../../_shared/INPUT_STANDARD.md)，
选定适用规则/schema，并让材料、合同、data 与实际消费者可以逐项对应。onboarding/P01
及后续使用相关字段的 Phase 都引用该依据；格式检查和科学接受仍按各自既有 Gate 执行。

先读取 [唯一任务路由表](../../../router/routes.yaml)，按用户要改变的内容和科学含义
选择一个 primary route，必要时显式列 supporting routes。实验名称本身不能决定路由。
通过 [catalog](../../../../catalog.yaml) 解析稳定 Skill ID，再读取路由指定的 WORKFLOW.md。
非 onboarding 路由执行其工作流后返回结果，不进入下方物理 intake/Phase 状态机。
源码根为 `cevns_pyeft/`；P01–P10 只属于物理接入。路由别名以 routes.yaml 为准。

## 前期人类审阅（H0–H3）

材料接入在既有 Gate 内使用 H0 身份/目标确认、H1 材料可读摘要、H2 分模块证据摘要、
H3 自然语言物理方案和公式审阅；职责由
[onboarding](../../onboarding/cevns-onboarding/SKILL.md) 的前期节点节定义。
P00 独占来源身份，P01 引用证据，P02 保留缺失/冲突，P03 固化审阅后的 partial contract。
不以原始 YAML 代替人类解释，不为四个节点新增 Markdown。
本条仅覆盖 P00–P03，不改变后续阶段或授予新 Gate/写入批准。

## 仓库维护选项

“维护目录和 README”“大幅删减后配合 Git 同步说明”等请求按 routes.yaml 的
repository_maintenance 进入[维护流程](../../../definitions/repository-maintenance/WORKFLOW.md)，
可执行只读检查、范围内同步、维护验收。用户已明确目标时直接执行，不重复模式确认。
维护以实际 Git revision 或文件快照为比较依据，按目录合并 README/导航任务；
生成区可显式自动同步，人工说明与残留引用由执行者核对。没有 Git 时不初始化；
不因维护文档而隐式授权源码/数据删减、科学改变或 Git 提交/推送。

## 正式物理接入的默认写入状态

正式物理接入原项目默认执行状态是 `read_only`。在用户明确批准原项目 `[WRITE PLAN]` 前，
只能读取文件、扫描候选、展示菜单和给出下一步建议；不得创建 `.onboarding_tmp`、
mock 文件、正式 run、data、src、tests 或 registry 修改。独立候选目录只可在
`workflows/_shared/policies/automation.md` 的带 `plan_id` 启用授权后写入；它不解除原项目的冻结。

## Mainline continuity（Master 所有）

执行 `workflows/_shared/policies/progress-continuity.md` 的 `MAINLINE_CONTINUITY_CONTRACT`，以及 `workflows/_shared/policies/write-authorization.md` 的
`WRITE_AUTHORIZATION_LOG`。Master 是 checkpoint、旁支返回、revision 检查、Gate
失效和 Phase 恢复的唯一 owner；子 Skill 只报告自己的权威结果和建议下一步。

### Progress index

`MIGRATION_PROGRESS.md` 是可由 Decision Log、Evidence Ledger、Physics Contract、
Phase 报告和 Authorization Log 重建的索引，不是这些记录的替代品。读取索引不构成
physics、scope 或 write approval。

索引模板：

```text
workflows/_shared/templates/onboarding/MIGRATION_PROGRESS_TEMPLATE.md
```

写入授权日志模板：

```text
workflows/_shared/templates/onboarding/AUTHORIZATION_LOG_TEMPLATE.yaml
```

未获得索引文件写入批准时，只在当前对话维持结构化 checkpoint，不声称可跨会话
恢复。获得临时写入批准后使用 `.onboarding_tmp/<session_id>/`；Dataset Identity、
`experiment_slug`、Scope Gate 和正式路径写入均获批后使用：

```text
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
```

### Detours

用户进行比较、解释、代码检查或其他旁支讨论时：

1. 引用进入旁支前已经存在的 checkpoint；
2. 回答旁支，不改变 Gate、pending decision 或 revision；
3. 首次说明旁支主题、主线断点和“主线状态未改变”；
4. 在四块版式的“你还可以”中显示中文主线导航；正在等待明确的物理选择或写入批准时，
   只说明停止位置和该项回复方式，不再附通用菜单。

旁支中的“更喜欢 A”等表达不能自动完成 Physics Decision；任何回答都不能自动解释
为 `APPROVE WRITE`。

### Resume algorithm

收到“返回主线”、自然语言的继续请求，或用户在旁支后直接处理当前待办时，
都先执行本节；不得要求用户必须说出准确导航口令。若当前有已启用的隔离自动运行，先按
`workflows/_shared/policies/automation.md` 用 `run_id` 恢复其候选断点，并同时说明原项目正式进度
未改变；候选处于审查暂停时只展示断点，用户明确回复“继续自动”后才继续执行。
收到“查看正式进度”时只读原项目。隔离计划失效或无法验证时，不回退
为对原项目的写入许可。返回正式主线时固定执行：

恢复的第一条用户可见回复必须重新读取 `workflows/_shared/policies/interaction.md`，并按
`migration_blocks_v1` 依次输出“当前状态—本次回答或进展—需要你做什么—
你还可以”。从旁支、暂停、对话压缩、候选审查恢复或 Phase Skill 返回时
都执行这一格式重置；不从上一条对话推断版式。需要审核的证据和文件清单
放在“本次回答或进展”的内部核对明细中。其后每条主线回复仍执行同一版式；
发送前核对四个固定 `###` 标题、三条分割线以及导航是否位于最后一块。
格式重置只影响表达，不改变 Gate、
审批或进度 revision。

```text
定位唯一当前进度索引；若不存在则定位当前对话 checkpoint
-> 校验 schema_version、revision、experiment_slug/dataset_id 和引用路径
-> 读取 Physics Contract、Decision Log、Evidence Ledger、Authorization Log 和当前 Phase 报告
-> 核对 write scope 与关键输入/contract/code/evidence 指纹
-> 按 implementation manifest 的实际依赖使过期 Gate 和下游 artifact 失效
-> 按 `workflows/_shared/policies/interaction.md` 的四块版式展示恢复摘要
-> 仅在 resume_requires 全部满足后执行结构化 step_id
```

索引缺失或损坏时从权威记录重建。无法确认有效批准、当前 revision 或依赖关系时停在
`BLOCKED` 并列出缺失项，不猜测断点。

### Progress update discipline

只在 `workflows/_shared/policies/progress-continuity.md` 列出的状态变化事件后更新。先完成权威记录，再核对有效 `Wxxxx`，
然后以 optimistic revision check 更新索引。多个对话从同一 revision 开始时，后写者
发现 revision 已变化必须停止并重读，不能覆盖。

## 新实验的用户资料入口

当用户要求新增实验，或把新材料迁移为独立 dataset 时，首次回复必须给出
`workflows/_shared/templates/onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md` 的可打开链接，
并给出 `workflows/_shared/templates/phase/P01_P10_PHASE_TEMPLATES.md`
阶段索引链接，使用户可以选择当前 P 的独立可填写模板。
并说明两种接收方式：

1. 用户自行填写 Markdown 模板（也可直接在对话中按栏目回答）。
2. 用户提供论文、补充材料、数据文件或旧程序；AI 从材料中摘录并预填同一模板，
   标注来源、缺失和冲突，再请用户核对需要决定的项目。

已有材料时直接按方式 2 开始只读提取；已有填写内容时直接按方式 1 核对。
不要要求用户重复填写已可从材料提取的内容。只有实验名称而无材料时，同时展示
模板和两种方式，让用户选择提供填写内容或材料。此说明须在 Step 0a 的候选扫描
可能停止流程之前给出；资料入口不代替 dataset identity、scientific claim 或写入 Gate。

通用模板保持只读。Dataset Identity 与 Scope Gate 获批后，填写结果保存到独立目录：

```text
docs/experiments/<experiment_slug>/datasets/<dataset_id>/EXPERIMENT_USER_INPUT.md
```

目录身份和创建条件执行 `workflows/_shared/policies/dataset-layout.md` 的 `PER_EXPERIMENT_DATASET_DIRECTORY`。

Onboarding 完成后生成的实验 Physics 文档遵循
[Experiment Physics Report Contract](../../../../_shared/references/onboarding/experiment-physics-report-contract.md)：
`experiment.physics.summary.md` 是精简阅读版，`experiment.physics.md` 是详细实现版。
精简版不替代详细版；详细版必须完整记录实验专属 Source、Target、Detector、Observable、
Prediction folding 和 Statistics 的公式与数据。Interaction、Nuclear Structure、
Kinematics 和 Cross-section 等共享模块在实验文档中只登记实际选择的模块 ID/配置，
不得复制其公共理论说明或内部公式。

## Runtime 授权与范围

收到明确的工程迁移请求时，先展示将迁移的模块、资源保护和回滚办法，再执行其已授权范围。
用户已经明确要求导入指定修复包时，不重复索取同一工程动作的批准；该授权不构成新物理输入、
实验激活或 scientific claim 的批准。runtime_existing、resource_audit 与 release_validation
不进入下面的物理候选扫描，也不因已有源码含实验名而触发 P00–P10。

## Step 0 — Onboarding Task Scope（该路由内不可跳过）

仅在路由已进入 experiment-onboarding 后，核对物理任务 scope；下面是物理状态字段，不是第二张任务路由表：

```text
physics_onboarding  新论文/新材料形成新的或重新定义的 dataset
existing_dataset    用户明确给出了唯一已有 dataset_id，并要求继续某阶段
skill_debug         只测试 workflow/菜单/路由，不做真实物理接入
```

如果用户只提供实验名称并要求新增数据接入，不得自动选择 scope；默认候选为 `physics_onboarding`，但必须显示并让用户确认 scope，除非用户已经明确说“仅测试 Skill”。

### Step 0a — 实验名歧义扫描

扫描：

- 用户明确给出的 paper/arXiv/DOI/dataset_id；
- `data/experiments/` 已有 dataset；
- `docs/`/用户附件中的候选材料；
- workflow 占位目录只能标 `PLACEHOLDER`；
- legacy/reference code 只能标 `REFERENCE`。

执行 `workflows/_shared/policies/archive-isolation.md` 的 `BACKUP_QUARANTINE`：候选扫描必须排除 `backup/**`。
其中的目录、代码、论文、spec、run、data、测试和参考数组均不加入 candidate list，
不计入 `candidate_count`，也不能用于推断 `existing_dataset`。用户明确要求恢复或审计
备份时可以读取相关路径，但读取本身仍不构成 dataset 或 physics scope 批准。

构建 candidate list。

确定性规则：

```text
用户明确指定唯一 dataset_id + existing_dataset scope
    -> 可进入相应 Phase（仍显示解析结果）

candidate_count == 0
    -> MUST ASK 用户提供/选择材料

candidate_count == 1 且 dataset identity 不是用户明确指定
    -> MUST SHOW candidate + REQUIRE APPROVAL

candidate_count > 1
    -> MUST SHOW ALL MATERIAL CANDIDATES + STOP
```

禁止使用“上下文足够，因此我推断”为理由跳过菜单。

### Step 0b — Write Approval Gate（不可跳过）

原项目写入前执行 `workflows/_shared/policies/write-authorization.md` 的 Write Approval Gate：先说明实际会改的内容及
影响，按用途分组列出准确路径，再说明恢复办法，并请求用户明确回复
`APPROVE WRITE`。不能只给 `Scope/Reason/Create/Modify/Delete` 字段和裸路径。
写入原因按 `workflows/_shared/policies/interaction.md`说明用户任务中的实际变化；已批准的科学选择
不再逐项重述，内部状态和规则标签放在需要核对的明细中。

没有 `APPROVE WRITE` 或有效的 `批准导入 <promotion_id>` 时，Master 不得写原项目。
`skill_debug` 不例外；mock onboarding 文件也需要写入批准。隔离候选运行只按
`workflows/_shared/policies/automation.md` 在独立目录内执行，不借此写原项目。

### 实验身份与状态的通用歧义规则

先区分用户要修改 runtime、归档记录还是物理输入；已有实验状态以 Catalog/Manifest 为准。
同名实验存在多次数据发布、多个靶材/观测配置或 legacy/reference 材料时，列出实际候选，
不得把同名 spec、备份或论文自动解释成 active definition。归档内容只提供来源，不能参与
默认 runtime discovery；恢复或激活另行核对精确 ID、资源与用户授权。

## Step 1 — Input Mode

输入模式：

```text
guided     论文/材料/一句话目标
structured 极简 intent YAML
expert     用户已有完整 contract/physics document
```

上述两种用户资料接收方式与 `guided|structured|expert` 输入模式相互独立；
Markdown 用户模板不是 `structured` 模式的 intent YAML。

若用户没提供完整 contract，可默认 `guided`。仅在材料接收方式会影响用户下一步
操作时，用自然语言说明“我会先从你给的材料整理候选信息，再请你确认 dataset 和
物理选择”；不要单独打印 `[INPUT MODE]` 或让用户解读模式名。

不需要为 guided 本身再让用户做一次无意义确认。

## Runtime route boundary

当请求属于 runtime_existing、new_experiment、archive_experiment、resource_audit 或
release_validation 时，先读取当前代码的 `ExperimentCatalog`、`ExperimentDefinition`、
`ResourceCatalog`、loader/runtime/selection 和资源清单，再按路由指定的 runtime/resource/archive/release 工作流执行。

这些路由必须保持：

1. active manifest IDs = `BUILTIN_CATALOG.ids()` = 默认 runtime 列表；
2. `spec_only` 只可通过 spec API 发现，不能伪装成可加载 definition；
3. `archived` 不进入默认 load、selection、legacy registry 或 statistics；
4. 新实验先用 `ExperimentCatalog(builtins=False)`，Slow 是最小合同；
5. 缺少 statistics 只阻断 evaluate，不得修改物理代码绕过；
6. 每个模块输出 change manifest、resource audit report、contract test plan、validation result。

只有请求明确涉及新物理语义时，才从 runtime 路由返回 P01–P10；P00–P10 的物理证据
流程继续保留。

## Step 2 — Route

### physics_onboarding

读取：

```text
workflows/cevns-pyeft/skills/onboarding/cevns-onboarding/SKILL.md
```

在 onboarding 完成并获得 Dataset Identity + Scientific Claim approval 之前，保持 `PRE_DATASET_FREEZE`。

### existing_dataset

确认唯一 `experiment_slug/dataset_id`。若正式 `00_MIGRATION_PROGRESS.md` 存在，按
Resume algorithm 恢复；若不存在，从当前 contract、decision log、phase reports 和
gates 重建只读 checkpoint。显示：

```text
已批准阶段
当前阻塞阶段
代码/证据自上次批准后是否变化
```

若依赖发生变化，将相关 phase 的 `human_gate` 标回 `NOT_REVIEWED`。

### skill_debug

进入 mock execution：

- 所有候选标 `MOCK`；
- 不写正式 dataset/run；
- 未获 `APPROVE WRITE` 前不写 `.onboarding_tmp` 或任何 mock artifact；
- 可以演示用户菜单、branch、Gate；
- 不得把 mock choice 写成 real approval。

## Step 3 — Phase 0 Scope / Implementation Plan

onboarding handoff 后，形成以下阶段总表；在用户审核整体实施范围时展示，
不把它附在每次答疑或阶段更新后：

```text
Phase 1 Dataset
Phase 2 Target/Exposure
Phase 3 Source
Phase 4 Theory/Response
Phase 5 Kinematics/Cross section
Phase 6 Detector response
Phase 7 Slow
Phase 8 Fast (optional/requested)
Phase 9 Statistics (optional/requested)
Phase 10 Validation/Release
```

面向用户说明每项是“可以开始、仍在整理、受到阻碍、本次未请求”中的哪一种，
以及阻碍的实际原因或开始条件；权威记录继续使用
`READY | DRAFT | BLOCKED | NOT_REQUESTED`。

### 整体方案优先与细节待办

执行 `workflows/_shared/policies/scientific-integrity.md` 的 `PROGRESSIVE_DETAIL_LOOP`。Phase 0 的任务是先形成可审核的
整体路线，而不是在实现开始前穷尽所有细节数据。对尚未进入其负责 Phase 的数值表、
参考数组或可选输入，可以保留 `DRAFT/MISSING/BLOCKED`，但计划中必须写明
`downstream_owner`、`needed_by_phase`、候选来源和阻断范围。

Scope Gate 批准只批准整体路线和已明确的物理范围，不会把待补细节自动批准为物理
输入，也不会授权对应文件写入。

Phase 0 总表与后续各阶段实施记录参照
`workflows/_shared/templates/phase/P01_P10_PHASE_TEMPLATES.md`。
其中的 CsI2021 内容仅用于识别函数职责和候选复用点，不构成新实验的物理输入。

### ⛔ Scope Gate

展示：

- `experiment_name` 与人类可读的 `experiment_slug`；
- dataset_id；
- requested scientific claim；
- 模块分类 `REUSE/CONFIG_ONLY/ADAPTER/SHARED_EXTENSION/CORE_EXTENSION/BLOCKED`；
- planned files；
- blockers。

选项：

```text
1. APPROVE SCOPE
2. REVISE CLAIM / MODULE CLASSIFICATION
3. INSPECT REPOSITORY MAP
4. BLOCK
```

批准后才允许创建正式：

```text
runs/<experiment_slug>/<dataset_id>/00_INPUT_INVENTORY.md
runs/<experiment_slug>/<dataset_id>/00_IMPLEMENTATION_MANIFEST.yaml
runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
```

同一正式持久化计划还须列出 onboarding handoff 的 P00–P05 权威记录；先从对话或已授权临时候选核对输入，
Scope Gate 和写入批准后先写权威记录、再写正式索引，不要求提前存在正式 run。

每个路径和动作仍必须在对应 `[WRITE PLAN]` 中列出。临时目录的批准不能授权这些
正式文件。创建正式索引时重新读取有效批准与权威记录填充，不得直接相信或原样复制
临时索引。

这一步解除 `PRE_DATASET_FREEZE`。

新 dataset 的所有实验专属目录执行 `workflows/_shared/policies/dataset-layout.md` 的
`PER_EXPERIMENT_DATASET_DIRECTORY`。已有平铺目录不得在本步骤静默搬迁；迁移必须列入
implementation manifest，并通过新的路径级 Write Approval Gate。

## Engineering workflow handoff

工程流程的步骤、产物与出口由路由目标 WORKFLOW.md 定义，不在 Master 再维护一套里程碑。
历史迁移序列仅保存在迁移审计中；它不约束普通维护。

## Step 4 — Phase Execution State Machine

阶段编号与默认审查顺序如下。P04–P10 的实际前置条件、记录字段和交接统一使用
[阶段执行合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)。
编号不要求每项能力都执行；Theory/Capability 等独立流程只调用其相关部分。

阶段与 Skill：

```text
1 -> cevns-dataset -> Machine Gate P01
2 -> cevns-target -> Machine Gate P02
3 -> cevns-source -> Machine Gate P03
4 -> cevns-theory-response -> Machine Gate P04
5 -> cevns-kinematics-cross-section -> Machine Gate P05
6 -> cevns-detector-response -> Machine Gate P06
7 -> cevns-slow-counts -> Machine Gate P07
8 -> cevns-fast-counts -> Machine Gate P08
9 -> cevns-statistics -> Machine Gate P09
10 -> cevns-validation -> Machine Gate P10
```

`P01`–`P10` 是 Phase 1–10 的 Machine Gate ID；onboarding 的
`P00_SOURCE_REGISTER.yaml`–`P05_CONTRACT_STATUS.md` 是产物文件名，
两套编号用途不同。Fast 和 statistics 若未请求，在 Phase 0 总表中分别记为
`NOT_REQUESTED`；这不是 `machine_gate` 的状态值。

Master 在 Phase 0 的 capability 依赖中明确：P06 可在自身输入就绪后分析；P07 消费本次输出所需的 P01–P06；
P08 要求当前 P07 PASS 和有效 Slow 冻结；P09 采用 Slow 时不依赖 P08，采用 Fast 时依赖指定表示。
P10 验收原目标要求的能力。未请求的可选能力不阻断交付；已请求但受阻时保留部分状态，
不得自动缩小目标。每种 Fast/独立统计模型使用独立 capability_id，不能互相借用 PASS。

每个 Phase 执行：

执行时用 `workflows/_shared/templates/phase/P01_P10_PHASE_TEMPLATES.md` 核对该阶段待填项，
并用 `workflows/_shared/templates/phase/PHASE_REPORT_TEMPLATE.md` 记录实际实现、验证和 Gate。
P04–P10 在同一报告的 `json phase-result` 块保存结构化交接，按 phase-result schema 检查；
这不是新增的批准权威，也不要求另建重复状态文件。旧报告恢复时显式补齐，不自动迁移历史批准。
进入 P01–P10 的具体阶段时，向用户给出索引中**该阶段独立模板**的可打开链接：
用户可自行填写，或提供材料由 AI 按相同栏目预填；不要要求用户自行设计函数。
用户填写区与 AI 函数/复用核对区分开处理，任何预填都不自动构成物理批准。

```text
A. 内部读取对应 Phase Skill；向用户说明本阶段正在处理什么
B. 用日常语言说明该阶段负责的物理内容与当前边界
C. 读取 evidence/contract/code
D. Pre-code Physics Decision（若物理定义尚未 APPROVED）
E. 执行技术实现
F. Machine Gate
G. Post-code Review：公式/函数/单位/数值/诊断
H. Human Physics Approval
I. 写回 contract + decision log + phase report
J. 返回 Master；Master 核对授权和 revision 后更新 progress index
```

上述 H–J 是正式项目的 Gate 和写回顺序。在已启用的隔离自动运行里，Phase Skill
可以生成后续阶段的**候选**，但只能记录候选检查结果；Phase Skill 中“用户批准后
进入下一阶段”的限制继续约束正式 Gate 和导入，不阻止隔离副本做候选探索。
隔离结果不得把 `human_gate` 写成 `APPROVED`，也不得更新原项目进度。

若步骤 C 或 D 发现当前 Phase 的必需细节不足，不得猜测或提前写代码。Master 应按
`PROGRESSIVE_DETAIL_LOOP` 将控制权定向返回 onboarding，只补充具体缺失字段；完成
证据抽取、冲突处理和必要 Physics Decision 后，返回原 Phase 的 pre-code review。
补充内容若改变已批准依赖，只重开受影响 Gate 和下游 Gate，并失效相关 Fast cache、
reference 或 validation，不重置无关 Phase。

Master 不应自动吞掉阶段报告。接收子 Skill 的结果后，按 `workflows/_shared/policies/interaction.md`
重新组织面向用户的回复：先说该阶段实际完成、发现或阻断了什么，再给本轮需要
的证据和下一步；不要直接转贴子 Skill 的状态字段、文件清单或 Gate 标签。
阶段完成、用户批准写回、验证结束或路由进入下一阶段时，即使用户没有说“返回
主线”，也先按当前正式进度重建四块回复。把完成事项、测试和记录链接放在
“本次回答或进展”；把确实需要的用户决定或“无需操作”放在“需要你做什么”；
把查看进度等入口放在“你还可以”。发送前按 `workflows/_shared/policies/interaction.md` 的版式自检；若出现
自定顶层报告标题或独立的结尾导航，重排后再发送。

若 Phase 输入、contract、代码或 evidence 指纹变化，Master 不按数字顺序机械重置
所有后续 Phase，而是依据 implementation manifest 的 capability 依赖：直接受影响的
Machine Gate 置为 `NOT_RUN`、Human Gate 置为 `NOT_REVIEWED`，相关 cache/reference/
validation 标记为 `STALE`，无关 Gate 保持不变。

## Step 5 — 低自动与高自动切换

用户可选择 `low_auto` 或 `high_auto` 两档隔离自动运行；未启用时保留现有
`stepwise` 人工流程。旧值 `auto_between_physics_gates` 只表示旧版的技术连续执行，
不得解释为已启用新的隔离目录或写入授权。
在任务范围已能说明、第一次进入阶段实施或恢复已有 dataset 时，按
`workflows/_shared/policies/automation.md` 用 `workflows/_shared/policies/interaction.md` 的分块版式介绍低自动、高自动和保持逐步
确认的区别，并请用户选择。已选过或用户已明确指定模式时不重复菜单；只说
“自动运行”时先展示选择，不默认高自动。“选择低自动/选择高自动”只进入只读
计划准备，不是启用。

收到“进入/切换低自动”或“进入/切换高自动”时，读取
`workflows/_shared/policies/automation.md` 和
`workflows/_shared/templates/auto/AUTO_RUN_PLAN_TEMPLATE.yaml`，核对原项目当前断点和输入，
只展示带警告的 `AUTO_RUN_PLAN`，不写文件。用户准确回复 `启用低自动 <plan_id>` 或
`启用高自动 <plan_id>` 后，才创建独立目录并运行。高自动要求唯一 dataset、
明确的科学目标与阶段范围，并且能验证所有写入被限制在独立目录；否则只提供
低自动或继续只读核查。

低自动在候选阶段的关键物理选择和阶段检查处等待用户；高自动可连续生成候选、
运行检查和修复范围内的技术问题，但发现资料冲突、范围越界、隔离失效或检查
无法通过时停止。两档均保持原项目只读、正式 Gate 不变。用户可随时说
`降低为低自动`、`暂停自动` 或 `退出自动`；从低升高必须重新展示计划并取得
新的准确启用回复。

自动运行中，每次有意义的进度更新都按分块版式说明当前正在处理的物理内容，
并在“你还可以”块保留“审查当前物理内容”入口。收到该回复后在安全断点
暂停候选执行，展示当前物理模型、输入、单位、证据、假设和检查结果；未收到
“继续自动”或具体修改前不继续。当前审查不改变正式批准或写入授权。

每个计划内模块完成或受阻时，先按 `workflows/_shared/policies/automation.md` 生成隔离候选模块
报告并登记其路径和指纹，再向用户输出四块进度回复，交代本模块做了什么、
完成了什么、未完成什么、下一模块的目标或停止原因，并给出已核实存在的
**绝对路径可点击报告链接**。报告或登记失败就停止在当前模块；高自动也不能
跳过逐模块汇报而只给最终汇总。报告尚未生成的中途进度不得暗示已有报告。

候选完成后展示完整差异和精确的原项目路径；只有用户审核后准确回复
`批准导入 <promotion_id>`，才按该协议备份、逐文件导入、验证并更新正式 Gate。
Master 分别记录该回复中的科学接受和写入授权，不把自动检查当作用户批准。

## Step 6 — Optional branches

Fast 或 statistics 缺关键输入时：

- 只 BLOCK 对应 capability；P08 受阻时可继续已获批准范围内的 Slow 或采用 Slow 的 P09；
- 不得把 `official likelihood` 静默降级为 `approximate chi2`；
- 可提出 narrowed claim，但必须由用户批准。

## Final

只有 `cevns-validation` 的 final claim 获用户批准（包括对完整候选导入计划的
明确科学接受）且正式项目验证通过后，才允许状态：

```text
FULLY_INTEGRATED
```

完成是相对于已接受的精确目标，而不是“所有十阶段都有 PASS”。P08/P09 计划未请求时，
其本次记录保持 NOT_RUN/NOT_REVIEWED；原目标要求的能力仍受阻时不得记完成。
否则保持最准确的部分状态。Final claim 的权威记录和 Phase 10 报告写入成功后，Master
才可把正式进度索引更新到 completed checkpoint；进度索引本身不能授予
`FULLY_INTEGRATED`。
