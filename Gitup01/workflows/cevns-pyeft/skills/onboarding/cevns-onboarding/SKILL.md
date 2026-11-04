---
name: cevns-onboarding
description: DrSai-style paper/material onboarding that merges paper intake, evidence ledger and partial physics-contract construction while enforcing dataset ambiguity and pre-dataset write freezes.
---

# cevns-onboarding — 论文/材料接入

用户可见回复执行 `workflows/_shared/policies/interaction.md`：先回答本轮问题；只在相关时说明材料核查结果、影响和需要用户决定的事项。下方字段用于核对，不是回复模板。

## Ownership

结构化交接按[package 编译器入口](../../../../../tools/compile_experiment_package.py)：
登记来源与逐字段 evidence、单位/轴/归一化、模型依赖、缺失/冲突，再形成 `cevns-onboarding-draft/1`。
AI 不自动理解任意论文；用户手填和 AI 提取走同一确定性编译入口。Physics MD 由同源数据渲染，
人工评审意见先回填 IR，不在 MD 维护第二份数值。机器输入和两份报告的 Schema/一致性 PASS 不通过任何科学 Gate。

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

若 Master 已启用 `workflows/_shared/policies/automation.md` 的隔离低/高自动运行，本 Skill 可以在
隔离副本中预填候选材料与缺失项；这些结果不创建正式 dataset，也不授予正式
Dataset Identity 或 Scientific Claim approval。正式写入仍按本 Skill 下方 Gate。

进入本 Skill 时默认 `read_only`。在用户明确批准 `[WRITE PLAN]` 前，只能读取
材料、扫描候选、展示证据摘要和提出菜单；不得写 `.onboarding_tmp`、正式
P00-P05、physics_docs、data、src、tests 或 registry。

## Onboarding mainline state

执行 `workflows/_shared/policies/progress-continuity.md` 的 `MAINLINE_CONTINUITY_CONTRACT`。本 Skill 只提供 onboarding
权威记录和 checkpoint 信息；当前主线、旁支返回、revision 与 Phase 路由仍由 Master
`cevns-experiment` 所有。

尚无进度文件写入批准时，只在当前对话维持 checkpoint，不声称具备跨会话恢复能力。
若用户批准的 `[WRITE PLAN]` 明确包含以下路径，可以写临时状态：

```text
workflows/cevns-pyeft/.onboarding_tmp/<session_id>/MIGRATION_PROGRESS.md
workflows/cevns-pyeft/.onboarding_tmp/<session_id>/AUTHORIZATION_LOG.yaml
```

临时进度允许 `dataset_id: null`。它不解除 `PRE_DATASET_FREEZE`，不能授权正式 run、
physics_docs、data、src、tests 或 registry，也不能把候选变成已批准 dataset。

普通材料比较、解释或其他旁支不更新临时进度、不增加 revision。只在材料登记步骤、
Dataset/Scientific Claim Gate、blocker、授权、暂停/恢复或关键输入指纹确实变化时，先
更新对应权威记录，再由 Master 核对 `Wxxxx` 和 revision 后更新索引。

## 前期人类节点（H0–H3 / P00–P03）

H0 确认 experiment/dataset/run/release 与目标；H1 审阅材料用途和边界；
H2 按 Source、Target、Interaction、Nuclear Structure、Detector、Observable、Statistics
展示有值/单位/locator/证据类别的摘要；H3 先解释实验配置，再分别确认共享模块选择、
实验专属公式/数据和未决问题。用户不必逐行阅读机器 YAML。

P00 来源身份唯一权威，P01 只用 source_id 引用，不重复维护来源。沿用共享目录中的
[SOURCE_REGISTER_TEMPLATE.yaml](../../../../_shared/templates/onboarding/SOURCE_REGISTER_TEMPLATE.yaml)、EVIDENCE_LEDGER_TEMPLATE.yaml、
[MISSING_AND_CONFLICTS_TEMPLATE.md](../../../../_shared/templates/onboarding/MISSING_AND_CONFLICTS_TEMPLATE.md)、PHYSICS_CONTRACT_TEMPLATE.yaml。
填写记录仍在获准的 runs/<experiment_slug>/<dataset_id>/P00–P03 路径；
H1 人类填写件仍用 EXPERIMENT_USER_INPUT.md，不新增 H0–H3 摘要文件。

两份派生报告遵循唯一的
[Experiment Physics Report Contract](../../../../_shared/references/onboarding/experiment-physics-report-contract.md)。
报告元数据中 models 以 model ID 为键；id 不是额外字段。
旧包按既有绑定合同提供只读视图，新 P03/IR 按同一 Schema 填写。
本节不改变 Step 7/8、P04/P05、Phase 0 或后续阶段。

## Step 1 — Materials

读取用户明确提供的：paper/PDF/arXiv/DOI/supplement/data/old code。

以[共同输入规范](../../../../_shared/INPUT_STANDARD.md)作为文件检查与摘录依据，
按资料角色和本次目标选择适用规则。逐文件核对身份、列/单位、坐标、归一化与来源，
记录规范/schema 版本、未检查项及实际消费者；用[检查表](../../../../_shared/templates/onboarding/INPUT_FILE_REVIEW_TEMPLATE.md)
或已有报告保存“原文件 → claim → 合同字段 → data → 消费者”的映射，避免把结构通过写成物理批准。

材料登记时即开始 Evidence Ledger；以下解释与澄清期间持续更新，Step 4 汇总而非首次取证。

使用 `workflows/_shared/templates/onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md` 作为两条
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
docs/experiments/<experiment_slug>/datasets/<dataset_id>/EXPERIMENT_USER_INPUT.md
```

同一实验的不同 dataset 共用可读的 `experiment_slug` 父目录，但各自使用独立
`dataset_id` 子目录。创建条件、合法字符和 legacy 兼容规则执行 `workflows/_shared/policies/dataset-layout.md` 的
`PER_EXPERIMENT_DATASET_DIRECTORY`。

当资料整理已明确下一阶段时，提供
`workflows/_shared/templates/phase/P01_P10_PHASE_TEMPLATES.md` 中
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

扫描仓库材料时必须执行 `workflows/_shared/policies/archive-isolation.md` 的 `BACKUP_QUARANTINE`：完全排除
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

## Step 3a — AI Physics Interpretation

把已选材料映射到 source、target、theory、detector、counts 和 statistics；明确公式/数值的
来源、单位、推导与假设，说明尚存的其他解释和下游影响。解释本身不批准任何物理字段。

## Step 3b — Human Physics Clarification

将会改变物理含义的歧义、近似和冲突交给用户澄清；按共享 evidence-and-approval 政策
记录决定和 claim 引用。已明确批准的选择不重复询问；未解决项保留缺失或冲突状态。
完成当前 handoff 所必需的澄清后，汇总已持续更新的证据并形成 partial contract。

## Step 4 — Evidence Ledger

使用 `workflows/_shared/templates/onboarding/EVIDENCE_LEDGER_TEMPLATE.yaml`。
每条 claim 的 `source_id` 必须引用 P00 中已有的来源；不要在 P01 重复建立 source record。

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

### H2 — Evidence review output

Step 4 完成后，向用户展示分模块证据摘要。正文只列关键事实，不复制完整 Ledger。
对每项关键事实显示：值/候选值、单位、来源定位、证据类别和未决状态。
P01 是逐项证据的权威记录；H2 是供人审阅的摘要，不是第二份证据台账。

## Step 5 — Missing/Blocking Matrix

使用 [P02 Missing and Conflicts 模板](../../../../_shared/templates/onboarding/MISSING_AND_CONFLICTS_TEMPLATE.md)
记录缺失、来源冲突及其对本次目标的影响。

生成：

```text
field | status | blocks dataset | blocks Slow | blocks Fast | blocks statistics | resolution
```

缺一个统计 covariance 不应阻断 signal-only Slow；缺 source normalization 可以阻断 Slow。

### H3 — Experiment configuration and module-choice review

H3 是物理配置确认节点。AI 必须先给出本实验的可读配置草案，再请用户确认。
**模块选择必须按独立维度展示，不能把 Interaction 与 Nuclear Structure 混成一个 Response 选项：**

| 选择维度 | 用户需要确认的内容 | 记录原则 |
|---|---|---|
| Interaction theory | SM、NSI 或项目已注册的 Full EFT 配置 | 只记录选择的 model ID、参数配置和依据 |
| Nuclear structure | Helm 或项目已注册的 Nuclear Response 配置 | 独立于 Interaction 记录 model ID 和资源引用 |
| Kinematics / Cross-section | 项目已注册且兼容的实现 | 记录 model ID；不在实验文档重写公共推导 |
| Detector response | 与本实验校准/观测量匹配的已注册 detector models | 实验专属公式、参数、单位、定义域和施加顺序必须完整记录 |
| Statistics | 与论文规定的数据语义、binning 和 likelihood 相符的模型 | 统计定义必须完整记录，不能只写 model ID |

只展示当前项目 Registry 中真实存在的候选。AI 必须说明候选与实验材料的对应依据、
所需输入和兼容性检查结果；没有注册实现时标记缺失，不得虚构 model ID。
Helm/Response 与 SM/NSI/Full EFT 是两个不同选择轴，是否兼容由已有模块合同检查，
不能凭概念上可组合就宣称实现支持。

#### H3 对实验专属内容的完整性要求

实验配置文档必须达到“实现人员可以据此编写实验适配代码”的程度：

- **Source：** 写出实际谱公式、归一化公式、源分量、味态/粒子标签、参数、单位、
  公式性质（理论衰变谱、几何关系、实验归一化输入或数值表格规则）、端点、mask、
  插值和归一化约定。不能笼统称整个源模型为经验公式或理论公式。
- **Target：** 写出核素组成、质量分数、靶质量、核数公式、所用质量常数和单位。
- **公式参数索引：** 每条实验专属公式后的符号说明必须给出精确 Parameter ID 或 NPZ resource key；不靠名称相似度猜测，确保读者能从公式定位到 YAML/NPZ。
- **Detector：** 对每个实际使用的 detector response 给出完整函数定义、参数值/单位、
  输入输出、定义域、边界/裁剪、归一化以及模块施加顺序。只列参数而不写公式不合格。
- **Observable：** 写出观测量定义、全部 bin edges、单位、边界约定和数据语义。
- **Prediction folding：** 写出本实验如何把源谱、靶核数、公共截面输出、Detector response
  和 bin integration 连接起来；不重推公共截面公式。
- **Statistics：** 写出原文采用的完整 likelihood/χ²、逐 bin 数据、背景、误差/协方差、
  nuisance、先验、相关性、profiling/marginalization、test statistic 和自由度/显著度方法。
  若统计语义或原始数据缺失，明确 BLOCKED/PARTIAL，不能猜测。

#### H3 对共享理论模块的限制

Interaction（SM/NSI/Full EFT）、Nuclear Structure（Helm/Nuclear Response）、
Kinematics 和 Cross-section 属于项目共享模块。实验配置只记录本实验选择的模块 ID、
必要配置值、资源引用和状态。不得在每个实验的 Physics MD 中重写 matching、
Particle Response、Nuclear Response 的公共理论公式、模块内部中间变量或源码算法。
共享模块的原理放在公共模块文档中。

H3 审阅通过只表示用户确认了本次实验配置描述；它不等于后续所有科学结论已批准，
也不自动升级 package/runtime/statistics 状态。

## Step 6 — Partial Physics Contract

填写时以 [P03 Physics Contract 模板](../../../../_shared/templates/onboarding/PHYSICS_CONTRACT_TEMPLATE.yaml)
为基础，保留 `contract_version: 4` 和现有 sections。模块选择按 Interaction 与 Nuclear Structure
分开记录；Physics MD 内容放入 `validation_claim.fields.physics_report`。

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

在不改变 `contract_version: 4` 和既有 section 名称的前提下，P03 的
`theory_response.fields` 必须把以下选择分开记录：

- `interaction_module`：SM / NSI / Full EFT 的实际选择及 model ID；
- `nuclear_structure_module`：Helm / Nuclear Response 的实际选择及 model ID。

`kinematics_cross_section.fields` 分别记录 `kinematics_module` 和
`cross_section_module`；`detector_response.fields` 记录本实验使用的 detector model IDs；
`statistics.fields` 记录与实验论文对应的 statistics model ID。每个字段沿用本合同既有的
`value/unit/evidence_claims/provenance_status/decision_status/blocking_scope` 结构。
不要把 Interaction 和 Nuclear Structure 合并成一个字段，也不要在这些选择字段中复制模块理论。

Physics MD 的人类可读内容元数据放在现有合同规定的位置：

```yaml
sections:
  validation_claim:
    fields:
      physics_report:
        value:
          models: {}
```

该 `physics_report` value 在 IR 整理时映射到
`document.extensions["lab.physics_report"]`，并由现有 v1/v2 Schema/Validator 严格校验。
每个 model 至少使用现有合同要求的 `group/content_class/title/explanation/equations`（model ID 为映射键）；
每条 equation 使用 `id/title/latex/symbols`，每个 symbol 使用
`symbol/definition/unit/parameter_ref`。不要在 P03 中增加 Validator 不认识的字段。

`content_class` 只能是：

- `experiment_specific`：Source、Target、Detector、Observable、Prediction folding、
  Statistics 等实验专属内容；详细报告必须给出可实现的公式、参数、单位和约定。
- `shared_framework`：Interaction、Nuclear Structure、Kinematics、Cross-section 等共享模块；
  实验报告只显示所选模块 ID/配置，不展开其公共理论公式。
- `implementation_detail`：源码内部别名、AST 赋值、内部循环和纯代码审计项；不进入实验正文。

P03 可以先以 DRAFT 形式形成候选，但**只有达到本次目标所需的实验配置完整度，才能 handoff 给 Physical Implementation**：

- 对本次请求涉及的 Source、Target、模块选择、Detector、Observable 和 Prediction folding，必须有足够的公式、参数、单位、资源引用和数值约定。
- 如果本次目标包含 benchmark/statistics，Statistics 的数据语义、分箱、数据、背景、误差/协方差和统计公式也必须完整。
- 与本次目标无关的能力字段可以保持 `DRAFT/MISSING`。
- 任何阻断本次目标的缺失项都留在 P02；未解决时保持 Onboarding `PARTIAL`，不得宣称可以进入对应物理实施。

Dataset identity 和 requested scientific claim 仍是最先必须确认的硬条件。

### Progressive Detail Backlog

执行 `workflows/_shared/policies/scientific-integrity.md` 的 `PROGRESSIVE_DETAIL_LOOP`。初次 onboarding 只需把整体方案所需
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

注意：只有 Dataset Identity、Scientific Claim、Phase 0 Scope Gate 及对应写入授权均满足后，
才允许写到正式 physics_docs 路径。此前只形成对话中的候选，或使用已单独获准的临时目录。
在此之前，`.onboarding_tmp` 也必须先通过 Write Approval Gate，不能自动写。

## Step 8 — Handoff

先将候选记录、证据与决定引用在对话中，或在已有授权的临时目录中交给 Master 做 Phase 0。
以下是 Scope Gate 和准确路径写入授权满足后的正式目的路径，handoff 本身不创建这些文件：

```text
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P00_SOURCE_REGISTER.yaml
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P01_EVIDENCE_LEDGER.yaml
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P02_MISSING_AND_CONFLICTS.md
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P03_PHYSICS_CONTRACT.yaml
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P04_DECISION_LOG.yaml
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/P05_CONTRACT_STATUS.md
```

这些正式文件须在 identity、scientific claim、Phase 0 scope 和对应路径写入授权均满足后生成。
先完成候选 handoff，再做 Phase 0；Master 获批后统一持久化正式 P00–P05 和 00_* 记录，避免目录创建条件循环。

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
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/00_MIGRATION_PROGRESS.md
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/AUTHORIZATION_LOG.yaml
```

创建时必须核对候选 P00-P05、Decision Log 与原始批准，先写正式权威记录，再写进度索引；不能原样复制临时状态。正式
索引建立后成为唯一当前索引；临时索引只可保留 handoff pointer，不再更新。改变
dataset 或 scientific claim 时重新评估 scope 与受影响 Gate，不得直接修改 YAML 后
沿用旧批准。

后续 Phase 因缺少具体输入返回 onboarding 时，只重新执行与该字段有关的 Materials、
Evidence Ledger、Missing/Blocking Matrix 和 Partial Physics Contract 步骤。新增材料
执行 Step 1a 的对比规则；物理含义改变时重新请求对应 Physics Decision。补齐后把
控制权交回请求该数据的原 Phase，不自行顺序重跑其他 Phase。

最后返回 Master `cevns-experiment`，不得自行执行 Phase 1。
