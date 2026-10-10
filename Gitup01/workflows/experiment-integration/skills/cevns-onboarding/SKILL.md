---
name: cevns-onboarding
description: DrSai-style paper/material onboarding that merges paper intake, evidence ledger and partial physics-contract construction while enforcing dataset ambiguity and pre-dataset write freezes.
---

# cevns-onboarding — 论文/材料接入

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；只在相关时说明材料核查结果、影响和需要用户决定的事项。下方字段用于核对，不是回复模板。

## Ownership

本 Skill 只负责：

```text
材料登记
实验/dataset 候选
证据抽取
冲突/缺失
scientific claim 候选
partial Physics Contract
```

不写生产代码。

若 Master 已启用 `AUTO_RUN_PROTOCOL.md` 的隔离低/高自动运行，本 Skill 可以在
隔离副本中预填候选材料与缺失项；这些结果不创建正式 dataset，也不授予正式
Dataset Identity 或 Scientific Claim approval。正式写入仍按本 Skill 下方 Gate。

进入本 Skill 时默认 `read_only`。在用户明确批准 `[WRITE PLAN]` 前，只能读取
材料、扫描候选、展示证据摘要和提出菜单；不得写 `.onboarding_tmp`、正式
P00-P05、physics_docs、data、src、tests 或 registry。

## Onboarding mainline state

执行 `_shared.md` 的 `MAINLINE_CONTINUITY_CONTRACT`。本 Skill 只提供 onboarding
权威记录和 checkpoint 信息；当前主线、旁支返回、revision 与 Phase 路由仍由 Master
`cevns-experiment` 所有。

尚无进度文件写入批准时，只在当前对话维持 checkpoint，不声称具备跨会话恢复能力。
若用户批准的 `[WRITE PLAN]` 明确包含以下路径，可以写临时状态：

```text
workflows/experiment-integration/.onboarding_tmp/<session_id>/MIGRATION_PROGRESS.md
workflows/experiment-integration/.onboarding_tmp/<session_id>/AUTHORIZATION_LOG.yaml
```

临时进度允许 `dataset_id: null`。它不解除 `PRE_DATASET_FREEZE`，不能授权正式 run、
physics_docs、data、src、tests 或 registry，也不能把候选变成已批准 dataset。

普通材料比较、解释或其他旁支不更新临时进度、不增加 revision。只在材料登记步骤、
Dataset/Scientific Claim Gate、blocker、授权、暂停/恢复或关键输入指纹确实变化时，先
更新对应权威记录，再由 Master 核对 `Wxxxx` 和 revision 后更新索引。

## Step 1 — Materials

读取用户明确提供的：paper/PDF/arXiv/DOI/supplement/data/old code。

使用 `workflows/experiment-integration/templates/onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md` 作为两条
接收路径的共同字段清单：

- **用户自行填写**：逐项核对目标所需字段、数值单位、数据轴、文件版本和来源；
  结合已给材料标出未找到的字段及相互冲突的说法。用户填入的值不自动成为
  经外部资料验证的物理事实。
- **用户提供材料，由 AI 总结**：按相同模板的栏目从论文、补充材料、数据或旧程序
  摘录并预填；每个关键值附来源定位（页/节/表/公式/文件/变量）、单位和证据状态。
  在回复中展示预填摘要，只请用户核对缺失、冲突和需要作物理选择的项目，
  不要求重复填写已提取的内容。旧程序仅作参考，除非用户明确选择其为迁移目标。

两条路径都继续进入 Dataset Candidate Gate、Scientific Claim Gate、Evidence Ledger
与 Missing/Blocking Matrix。预填不等于用户批准；未找到的数值保持 `MISSING`，
冲突保持 `CONFLICT`，不要猜测或以 `0` 代替。获批写入前只在对话中展示摘要。

通用模板本身不得写入实验值。Dataset Identity、`experiment_name`、
`experiment_slug` 和 Scope Gate 获批后，正式填写件使用：

```text
docs/experiment_integration/experiment_inputs/<experiment_slug>/<dataset_id>/EXPERIMENT_USER_INPUT.md
```

同一实验的不同 dataset 共用可读的 `experiment_slug` 父目录，但各自使用独立
`dataset_id` 子目录。创建条件、合法字符和 legacy 兼容规则执行 `_shared.md` 的
`PER_EXPERIMENT_DATASET_DIRECTORY`。

当资料整理已明确下一阶段时，提供
`workflows/experiment-integration/templates/phase/P01_P10_PHASE_TEMPLATES.md` 中
对应 P 阶段的独立填写模板链接。用户可逐阶段填写，也可继续提供材料由 AI
按同一模板预填；函数签名、复用分类和代码风格由 AI 核对，不转嫁给用户。

### Step 1a — Additional Material Check and Comparison

当用户只提供一份参考文件时，在完成材料登记和初步摘录后，可以且通常应主动
询问一次：

```text
是否还有需要一并核对的论文、补充材料、官方数据、旧程序或参考数组？
```

该询问是非阻塞的：

- 用户没有其他文件时，继续处理当前材料；
- 用户已明确要求只使用当前文件时，不重复询问；
- 不得自动搜索或引入用户未指定的外部材料；
- `backup/**` 仍受 `BACKUP_QUARANTINE` 约束。

存在多份材料时，应辅助生成逐项对比，至少覆盖：

```text
文件身份、作者、版本和材料角色
experiment、run period 和 dataset identity
source、target、exposure 和 detector configuration
threshold、analysis window、binning 和数据单位
theory/response、Slow、Fast 和 statistics 定义
数值基准、数据来源和 scientific claim
AGREE | DIFFER | MISSING | CONFLICT 状态及下游影响
```

多份文件不等于多个 dataset。只有运行期、探测器、源、靶材、统计语义等物理配置
确实不同，才拆分为不同 dataset candidate。支持同一数据集的论文、补充材料和数据
文件应保持独立 `source_id`，但归入同一候选。

发生冲突时保留各文件的 claim、locator 和 evidence status，不得静默选择、平均或
覆盖。

同时可以扫描仓库已存在的相关材料，但标记：

```text
USER_SUPPLIED
LOCAL_CANDIDATE
REFERENCE_ONLY
PLACEHOLDER
```

扫描仓库材料时必须执行 `_shared.md` 的 `BACKUP_QUARANTINE`：完全排除
`backup/**`。归档中的论文、旧代码、spec、run、data、测试、参考数组和目录不得
登记为 material source，不得进入 Dataset Candidate Gate、Evidence Ledger、
Scientific Claim Gate 或 Missing/Blocking Matrix。显式的恢复/审计请求只允许读取，
不会自动解除此隔离；恢复材料必须先回到非 `backup/**` 路径，再由 Master 重新路由。

向用户说明正在整理哪些材料、哪些由用户提供、哪些只是仓库里的候选，
以及当前还需要确认什么。内部保留 `input_mode`、`source_id`、来源类型和
文件路径；仅在材料选择、证据审查或 Skill 调试需要时展示完整清单。

**本地存在材料 != 用户选择材料。**

## Step 2 — Dataset Candidate Gate（硬门）

从材料中建立独立 dataset 候选。拆分依据包括：

```text
run period
detector configuration
source configuration
target configuration
threshold/analysis window
binning
observed data/background/covariance/likelihood
```

若候选超过一个：必须列菜单。

示例：

```text
⛔ Step 1b — CONUS Dataset Identity

A. existing conus_plus_ge73_pheno
B. official CONUS+ KKL observation
C. legacy CONUS Brokdorf
D. Skill debug only
E. use other material

1...N 对应候选
Inspect evidence
Block
```

用户批准前不得创建正式 `<experiment_slug>/<dataset_id>/` 目录。

Dataset Identity Gate 必须同时展示并确认：

```text
experiment_name
experiment_slug
dataset_id
```

例如 `CONUS+ / CONUS_Plus / conus_plus_2025_c2c3c5_ge73_pyeft`。其中前两项负责
清晰的人类识别，`dataset_id` 负责机器唯一性；不得用裸实验名代替唯一 dataset。

若需要保存候选扫描或临时 evidence，必须先返回 Master 的 Write Approval Gate，
列出 `.onboarding_tmp/<session_id>/` 下将创建的具体文件，并等待用户回复
`APPROVE WRITE`。

## Step 3 — Scientific Claim Gate

与 dataset identity 分开确认。

候选示例：

```text
publication_forward_reproduction
signal_forward_model
approximate_phenomenology
legacy_numerical_reproduction
official_likelihood_reproduction
```

如果证据缺 official likelihood 输入，应显示：

```text
official_likelihood_reproduction = REQUESTED_BUT_BLOCKED
```

不能伪装 READY。

## Step 4 — Evidence Ledger

对每个 claim 写：

```yaml
claim_id: C0001
field: dataset.exposure
value: ...
unit: ...
status: SOURCE_EXTRACTED|PROJECT_DERIVED|REFERENCE_ONLY|MISSING|CONFLICT
source_id: S...
locator: page/section/equation/table/file/symbol
confidence: high|medium|low
downstream_owner: dataset|target|source|theory|kinematics|detector|slow|fast|statistics
```

冲突保留两条 claim，以 `conflict_group` 连接。

项目推导必须写 derivation，例如 `nuclei/kg`、uniform bin edges；不能伪装论文值。

## Step 5 — Missing/Blocking Matrix

生成：

```text
field | status | blocks dataset | blocks Slow | blocks Fast | blocks statistics | resolution
```

缺一个统计 covariance 不应阻断 signal-only Slow；缺 source normalization 可以阻断 Slow。

## Step 6 — Partial Physics Contract

完整 TEX 不是输入要求。

每个字段保存：

```yaml
value: ...
unit: ...
evidence_claims: [...]
provenance_status: ...
decision_status: DRAFT|APPROVED|BLOCKED|NOT_APPLICABLE
blocking_scope: [...]
```

Section：

```text
identity_and_goal
dataset
target_and_exposure
source
theory_response
kinematics_cross_section
detector_response
slow_counts
fast_counts
statistics
validation_claim
```

此阶段只强制冻结：

```text
identity_and_goal
dataset identity
requested scientific claim
```

其他 section 可以 DRAFT/MISSING。

### Progressive Detail Backlog

执行 `_shared.md` 的 `PROGRESSIVE_DETAIL_LOOP`。初次 onboarding 只需把整体方案所需
的 dataset identity、scientific claim、模块边界和已知 blocker 说明清楚；不要求一次
性抽取所有后续数值细节。

对每个尚未补齐、且当前不阻断 handoff 的字段，除现有 evidence/decision 状态外，
还要记录：

```yaml
downstream_owner: dataset|target|source|theory|kinematics|detector|slow|fast|statistics|validation
needed_by_phase: 1|2|3|4|5|6|7|8|9|10
candidate_sources: []
blocking_scope: []
```

`needed_by_phase` 只是收集时机，不是新的 evidence status。字段没有证据时仍必须是
`MISSING`；不得用 `DEFERRED` 掩盖缺失。

## Step 7 — Canonical LaTeX

从模板逐步渲染：

```text
physics_docs/experiments/<experiment_slug>/<dataset_id>/experiment_physics.tex
```

未解决字段必须写 `TBD/BLOCKED`，不能为了完整性填猜测值。

注意：只有 Dataset Identity Gate 批准后才允许写到正式 physics_docs 路径。
在此之前，`.onboarding_tmp` 也必须先通过 Write Approval Gate，不能自动写。

## Step 8 — Handoff

输出：

```text
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P00_SOURCE_REGISTER.yaml
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P01_EVIDENCE_LEDGER.yaml
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P02_MISSING_AND_CONFLICTS.md
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P03_PHYSICS_CONTRACT.yaml
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P04_DECISION_LOG.yaml
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/P05_CONTRACT_STATUS.md
```

这些正式文件只能在 identity approval 后生成。

P00-P05 是 onboarding 权威产物，不是 `MIGRATION_PROGRESS.md`。Onboarding handoff
完成时，把以下信息返回 Master：

```text
experiment_name / experiment_slug / dataset_id
有效 Dataset Identity 与 Scientific Claim decision refs
P00-P05 artifact refs
当前 blockers 与关键 source fingerprints
建议的 master.phase0.scope_gate checkpoint
```

此时不得自行创建正式进度索引。只有 Master 后续取得 Scope Gate 和正式路径
`APPROVE WRITE` 后，才可创建：

```text
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
workflows/experiment-integration/runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
```

创建时必须重新读取 P00-P05、Decision Log 和原始批准，不能原样复制临时状态。正式
索引建立后成为唯一当前索引；临时索引只可保留 handoff pointer，不再更新。改变
dataset 或 scientific claim 时重新评估 scope 与受影响 Gate，不得直接修改 YAML 后
沿用旧批准。

后续 Phase 因缺少具体输入返回 onboarding 时，只重新执行与该字段有关的 Materials、
Evidence Ledger、Missing/Blocking Matrix 和 Partial Physics Contract 步骤。新增材料
执行 Step 1a 的对比规则；物理含义改变时重新请求对应 Physics Decision。补齐后把
控制权交回请求该数据的原 Phase，不自行顺序重跑其他 Phase。

最后返回 Master `cevns-experiment`，不得自行执行 Phase 1。
