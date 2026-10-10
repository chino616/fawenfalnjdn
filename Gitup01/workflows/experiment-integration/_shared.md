# Shared Interaction and Gate Contract

本文件只定义跨阶段共用的交互/状态格式，不定义 workflow 路由。

## 1. 用户可见回复：说明实际事情

Skill 的步骤、Gate、文件名和状态字段用于执行与核对，不是给用户的回复模板。
每轮先判断用户此刻是在问问题、了解进度、审核科学选择、查看执行结果，还是
决定是否允许写入；随后直接回答该问题。只提供这轮决定或理解结果所需的信息，
不机械汇报所有内部步骤。活动中的实验迁移回复使用下述分块骨架；块内按本轮
问题选择内容，不强制相同篇幅或重复无关明细。

### 分块版式

状态、回答、用户动作分开写，块与块之间用单独一行 `---` 分隔。适用于模式
选择、阶段进度、旁支问答、物理审核、写入申请、错误和恢复：
该版式的内部标识为 `migration_blocks_v1`；进度索引可以记录此标识以便恢复，
但版式规则以本节为准，不依赖上一条对话的写法。

```markdown
### 当前状态
<实验/模式/正式或隔离候选/当前阶段/是否暂停，一到两行>

---

### 本次回答或进展
<先回答用户本轮问题，再说明与当前任务有关的结果和依据>

---

### 需要你做什么
<一项明确行动及回复方式；没有必需行动就写“无需操作”，并说明下一步或停止点>

---

### 你还可以
<当前真正可用的查看、审查、改模式或暂停入口>
```

四个 `###` 标题、顺序及三条独立的 `---` 是每条用户可见迁移回复的固定外层结构。
回复开头不另加内部日志、阶段标签或无标题的前言；结尾导航放进“你还可以”，
不作为第五块。阶段完成、批准写回、验证结束和进入下一阶段也使用同一结构，
不能把“具体完成了什么”“验证结果”“当前记录”等临时标题改成新的顶层块。

需要核对大量证据或批准文件写入时，在“本次回答或进展”内部使用四级标题
`#### 核对明细`，把证据或每条准确路径及动作放在那里；不要额外插入顶层
`---`。用户看完范围后，在“需要你做什么”中看到批准口令。
自动模式每完成或阻断一个计划内模块时，在“本次回答或进展”概括本模块做了
什么、完成了什么、未完成什么、下一模块要做什么或为何暂停，并用可点击的
**绝对路径**直接链接已存在且指纹核对过的隔离候选报告；完整依据留在报告中，
用户要求时在对话内展示全文。模块仍在执行、报告未生成时明确说明这一点。
不把状态码、英文标签或裸路径当作任何一块的解释。正在等待特定批准时，
“你还可以”只列查看依据、修改当前计划或暂停，不附无关的主线菜单。
“返回主线”“继续迁移”“接着处理当前阶段”“继续 P03”等明确或自然的继续
表达，以及用户在旁支后直接回答当前待办，都视为回到主线；不要求用户记住
固定口令。每次从旁支、暂停、对话压缩、Phase Skill 或隔离候选运行回到主线时，
先重新读取本节，用当前权威进度重建四块；不能延续旁支的自由格式，也不能
照搬上一条回复。自动候选处于审查暂停时，“返回主线”只恢复版式和断点展示；
实际继续执行仍按自动运行协议等待“继续自动”。
“需要你做什么”即使没有待办也要明确写“无需操作”，以免用户误以为漏了指令。

组织回复时先在内部确认：**已经核实什么，尚未核实或尚未执行什么；这对用户的
实验或当前任务有什么影响；接下来由谁做什么，是否需要用户决定。**按这些事实
组织正文，而不是把状态字段逐项翻译成中文。优先写可辨认的对象、具体动作和
实际结果；如果一句话只剩抽象流程名词，补上究竟修改或检查了什么，以及结果
会怎样。

- 用户只是在提问或比较时，先给答案和依据；没有待批事项就不要制造批准请求。
  用户在迁移中提出旁支问题时，再简短说明主线停在哪里、是否受影响。
- 汇报进度或检查结果时，区分**已验证的事实、依据事实作出的判断、计划中的
  动作和未获批准的动作**。失败时说清失败的是哪项检查、它阻断了什么、下一步
  如何处理；不要用状态值代替原因。
- 请求选择时，说明用户要决定的具体物理问题、可选路线及其影响；请求写入时，
  说明实际文件变化和影响范围。已批准的科学选择不因等待写入而重新索取批准。
- 保留必要的物理量、模型、公式、单位和不确定性，准确说明其物理含义。内部
  审批、文件维护、缓存、版本和路由术语不是物理术语；仅当它们影响当前判断时
  使用，并就地说明实际作用。不要为了通俗而省去影响科学判断的条件。

先给直接结论及其影响，再放必要的证据、操作范围或用户动作。复算过程、测试
明细、路径、指纹和原始状态值可放在后面的核查区；当前决定依赖某项细节时，
在正文中明确它。对话里已作出的决定、尚未写入的决定、已写入且核验过的记录
必须分清。无需用户行动时，不虚构“请你决定”或停止点。

读取 Skill、核对输入、规则命中、阶段边界和 Gate 仍须实际执行，但默认不把
`[READ AGENT]`、`[READ SKILL]`、`[PHASE]`、`[INPUT]`、`[OWNERSHIP]`、
`[PROHIBITED]`、`[RULE]`、`[WHY]`、`[ACTION]` 逐项打印给用户。
用户要求审计、查看依据、完整进度或调试 Skill 时，可以在简短结论之后展开
规则名、路径、证据引用和原始状态值。不得展示模型私有思维链。

输出前自检：遮住文件路径、状态代码和英文标签后，用户能否说出“我的问题得到
什么回答、什么已经发生、有什么影响、我是否要做决定、接下来会怎样”？若不能，
重写正文。精确的 Gate 值、decision ID 和结构化 checkpoint 仍保存在权威记录中，
用户要求审计或当前决定需要时再展示。
再检查版式：是否恰好有上述四个 `###` 顶层标题和三条分割线；所有验证结果、
路径、状态代码是否位于“本次回答或进展”的内部；用户动作是否位于“需要你做什么”；
导航是否位于“你还可以”。任一项不满足，先重排后发送。

## 2. Physics Decision 菜单

正式采纳物理语义的定义、选择、近似或改变时，必须使用显式菜单。
隔离自动运行可以在副本中测试候选，但不能把候选选择写成正式 Physics Decision；
最终导入按 `AUTO_RUN_PROTOCOL.md` 请用户审核实际采用的路线。

```text
需要你决定的物理问题：<标题>

目前已知：...
需要选择：...
不同选择的影响：...

1. 接受 <候选>（需要固定批准口令时同时写明该口令）
2. 选择其他候选或提出修改
3. 查看证据或代码
4. 暂停此决定
```

如果存在 2 个以上互斥物理候选，选项必须把候选逐项列出，不能用“是否接受推断 y/n”隐藏其他候选。

## 3. Machine Gate 与 Human Physics Gate

状态独立记录：

```yaml
machine_gate: PASS|BLOCKED|NOT_RUN
human_gate: APPROVED|REVISE|BLOCKED|NOT_REVIEWED
```

正式阶段只有在二者满足所需条件时才可向后推进。按
`AUTO_RUN_PROTOCOL.md` 在隔离副本中推进的阶段只是候选；候选 Machine PASS
不产生正式 Human approval，也不更新原项目的 Gate。

## 4. confirm_mode

`confirm_mode=minimal` 可以自动通过：

- 重复的执行确认；
- 非物理参数的默认值（前提是 Skill 明确指定）。

它不能自动通过任何原项目文件写入，包括 mkdir、`.onboarding_tmp` mock 文件、
state/ledger/report 文件、正式 run 文件、data/src/tests/registry 修改。
独立目录的写入由 `AUTO_RUN_PROTOCOL.md` 的单次启用授权控制，与
`confirm_mode=minimal` 无关。

它绝不能自动通过：

- dataset identity；
- scientific claim；
- target/isotope interpretation；
- source normalization route；
- detector response approximation；
- statistical data semantics；
- Slow authoritative freeze；
- Fast mathematical meaning；
- final scientific claim。

## 4.1 Write Approval Gate

原项目的任何文件写入均执行本节；隔离候选目录的写入仅在
`AUTO_RUN_PROTOCOL.md` 的带 `plan_id` 启用授权后进行。两者的授权范围不能混用。
写入前按第 1 节说清目的、用户可见的变化、影响范围和完成后的停止点。
用户已审核过的科学细节不机械重述。

用户可见的 `[WRITE PLAN]` 按“文件的用途”组织，不把 `Scope`、`Reason`、
`Create`、`Modify`、`Delete` 等内部字段名或一串裸路径当作说明：

1. **会改什么**：按用户能识别的对象分组，说明每组文件具体新增/修改/删除的
   内容及其用途；说清正式配置或代码是否影响运行结果，审核记录会记录哪项
   已发生的决定，进度会指向哪项下一工作。不能只说“更新报告、状态和进度”。
   相同信息只说一次。
2. **影响与恢复**：用中文写明只影响哪个实验和 dataset、是否改变正式配置或
   计算代码、若出错如何恢复。无删除也要明确说明。
3. **准确路径供核对**：在批准请求之前列出每条路径及其新增/修改/删除动作，
   让路径与上述用途一一对应，不让用户从文件名猜测用途。
   可先写共同目录前缀，再列该目录下的文件名；前缀与文件名组合后必须唯一
   确定完整路径。路径放在对应用途组后或单独的路径核对区，不替代用途说明。
4. **单一用户动作**：普通原项目写入请准确回复 `APPROVE WRITE`；隔离候选的
   最终导入按 `AUTO_RUN_PROTOCOL.md` 展示科学结论和路径后，请准确回复
   `批准导入 <promotion_id>`。两种回复只覆盖各自展示的范围；也可提出修改或
   回复 `BLOCK`。等待该回复时不附通用主线菜单。

`Scope` 等内部枚举仍按规范写入 Authorization Log；面向用户说明其实际
边界即可。文件扩展名、阶段编号和 revision 仅在区分路径或当前决定确实需要时
解释。不要在开头和文件分组中重复同一变更，也不要把备份隔离等内部规则展开
为与当前授权无关的长说明。

只有用户明确回复 `APPROVE WRITE` 或有效的 `批准导入 <promotion_id>` 后，
才能执行列出的原项目写入。用户批准只覆盖计划中的准确路径和动作；新增路径
或动作必须重新请求批准。隔离目录的启用口令不授权写入原项目。

原项目默认状态为 `read_only`。读取文件、列目录、运行非写入校验、展示候选菜单
不需要 Write Approval Gate；隔离自动运行中的技术写入不改变这一默认状态。

## 4.2 两档隔离自动运行

Master 收到“进入低自动/高自动”时读取 `AUTO_RUN_PROTOCOL.md`，先只读核查并展示
带警告的计划；请求切换模式本身不是启用或写入许可。只有用户对当前 `plan_id`
给出该协议规定的准确启用回复，才能写计划指定的独立目录。低自动在关键审核点
等待用户，高自动在目标明确且无硬阻碍时连续生成候选结果。两档都不自动写入
原项目，也不自动把候选 Gate 记成正式批准。

用户可以立即降低自动程度、暂停或退出。提高自动程度或扩大范围必须展示新的
计划和警告。隔离目录、原项目和 `backup/**` 是三个不同区域；隔离目录不能作为
原项目的材料发现来源，除非用户明确选择导入并通过正式审核。

## 5. Evidence status

仅使用：

```text
SOURCE_EXTRACTED
PROJECT_DERIVED
USER_CONFIRMED
REFERENCE_ONLY
MISSING
CONFLICT
```

发现冲突时保留所有 claim，不覆盖。

## 6. Decision log

每次 Physics Decision 追加：

```yaml
decision_id: Dxxxx
phase: ...
field: ...
options_shown: [...]
user_choice: ...
evidence_claims: [...]
result: ...
```

## 7. PRE_DATASET_FREEZE

在 Dataset Identity Gate `human_gate=APPROVED` 前：

允许读取任意相关资料和仓库文件。
下列冻结约束原项目的正式路径；`AUTO_RUN_PROTOCOL.md` 中的独立候选副本
可以整理未获批准的材料，但不能由此创建正式 dataset 或解除冻结。
只有在用户明确批准 `[WRITE PLAN]` 后，才允许写入：

```text
workflows/experiment-integration/.onboarding_tmp/<session_id>/
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

## 8.1 PER_EXPERIMENT_DATASET_DIRECTORY

每个正式 dataset 使用“可读实验目录 + 唯一 dataset 子目录”的两级隔离：

```text
<experiment_slug>/<dataset_id>/
```

三个身份字段不得混用：

```yaml
experiment_name: "供文档和用户界面显示的正式实验名称"
experiment_slug: "稳定、可读、文件系统安全的实验目录名"
dataset_id: "程序、registry 和 Physics Gate 使用的唯一数据集标识"
```

`experiment_slug` 应清楚表达实验，例如 `CONUS_Plus`、`COHERENT_CsI`，并只使用
ASCII 字母、数字、下划线或连字符。同一实验的多个 dataset 可以共用
`experiment_slug` 父目录，但每个 `dataset_id` 必须有独立子目录；不得混放 evidence、
decision、数据表、cache、阶段报告或验证结果。

新 dataset 的规范目录为：

```text
docs/experiment_integration/experiment_inputs/<experiment_slug>/<dataset_id>/
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/
physics_docs/experiments/<experiment_slug>/<dataset_id>/
data/experiments/<experiment_slug>/<dataset_id>/
```

通用模板仍只保存在 `workflows/experiment-integration/templates/`，不得写入任何实验
专属值。正式目录只能在 Dataset Identity、`experiment_slug` 和 Scope Gate 获批，且
对应 `[WRITE PLAN]` 获得 `APPROVE WRITE` 后创建。

已有平铺目录属于 legacy compatibility。不得仅因本规则自动移动或重命名；迁移时必须
在 implementation manifest 中登记旧、新路径，并为移动、loader/registry 更新和回归
验证单独取得写入批准。

## 9. BACKUP_QUARANTINE

`backup/**` 是只用于恢复的隔离区，不属于 experiment-integration 的 physics
workspace。Master、onboarding 和所有 Phase 均不得自动扫描或读取其中内容，也不得
把它用于：

```text
material discovery
candidate list / candidate_count
dataset identity / existing_dataset detection
evidence ledger / scientific claim
repository map / migration input
reference arrays / validation baselines
```

只有以下操作可以访问 `backup/**`：

1. 按仓库规则创建或登记备份；
2. 用户明确要求恢复或审计备份。

即使用户明确要求读取备份，读取结果也只具有 recovery/audit 身份，不自动成为
physics evidence、dataset candidate 或迁移输入。若要把恢复内容重新接入实验流程，
必须将其恢复到非 `backup/**` 路径，并重新经过 Master Skill 的 scope、identity、
scientific claim 和 write gates。

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
workflows/experiment-integration/.onboarding_tmp/<session_id>/MIGRATION_PROGRESS.md
workflows/experiment-integration/.onboarding_tmp/<session_id>/AUTHORIZATION_LOG.yaml
```

若没有这项写入批准，只在当前对话维持 checkpoint，不得声称具备跨会话恢复能力。

Dataset Identity、`experiment_slug`、Scope Gate 与正式路径写入均获批后，正式位置为：

```text
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
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

## 12. WRITE_AUTHORIZATION_LOG

Write Approval 与 Physics Decision 分开编号。普通原项目写入只有用户在完整
`[WRITE PLAN]` 后精确回复 `APPROVE WRITE` 才产生 `Wxxxx`。隔离候选导入只有用户
审核完整导入计划后精确回复 `批准导入 <promotion_id>` 才产生对应的 `Wxxxx` 和
独立的 Physics Decision。启用自动模式只授权指定隔离目录；候选计划、模糊同意或
其他问题的回答不产生原项目写入授权。

每条授权至少记录：

```yaml
authorization_id: W0001
status: ACTIVE|EXHAUSTED|REVOKED|SUPERSEDED
approved_at: ISO-8601
approval_message_ref: <当前对话中的原始批准引用>
approval_kind: manual_write|promotion
promotion_id: null
scope: skill_debug|physics_onboarding|existing_dataset
plan_ref: <WRITE PLAN 引用或完整摘要>
allowed_actions: [create, modify, delete]
create_paths: []
modify_paths: []
delete_paths: []
production_paths_affected: false
recovery_plan: ...
supersedes: []
superseded_by: null
```

日志追加写，不覆盖历史授权。`authorization_refs` 只是索引；每次写入仍须核对原批准
的路径、动作和有效范围。临时目录授权不覆盖正式 run；某次创建授权不自动覆盖以后
新增路径。若 `[WRITE PLAN]` 明确批准在列出的状态变化事件持续修改同一个进度文件，
该授权可覆盖这些精确事件；任何路径或动作扩展必须申请新的 `Wxxxx`。

日志文件本身也受 Write Approval Gate 约束。首次日志尚未获准创建时，当前对话中的
原始 `[WRITE PLAN]` 与 `APPROVE WRITE`，或完整导入计划与准确的
`批准导入 <promotion_id>`，是对应写入的权威；日志创建后可按原始批准补录。
