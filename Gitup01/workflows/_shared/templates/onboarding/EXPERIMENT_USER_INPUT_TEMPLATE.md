# CEvNS-pyEFT 实验接入资料

> **模板：** `EXPERIMENT_USER_INPUT_TEMPLATE.md`  
> **填写件：** `EXPERIMENT_USER_INPUT.md`  
> **填写件位置：** `docs/experiments/<experiment_slug>/datasets/<dataset_id>/EXPERIMENT_USER_INPUT.md`

本文件是研究人员与 AI 共同使用的 Onboarding 入口。它用来明确实验身份、研究目标、材料和本实验的配置选择。它不是 YAML 表单，也不是项目共享物理模块的说明书。

## 使用方式

- **自行填写：** 只填写已知内容；不知道的地方留空或写“待从材料中确认”。
- **提供材料：** 提供论文、补充材料、官方数据、校准资料或旧程序，由 AI 阅读后预填本文件并给出来源、缺失和冲突。

AI 不应要求用户重复填写可从材料提取的信息，也不得猜测缺失参数。

## 目录

1. [实验身份与目标](#1-实验身份与目标)
2. [已有材料](#2-已有材料)
3. [已知实验条件](#3-已知实验条件)
4. [本次希望采用的模块](#4-本次希望采用的模块)
5. [AI 整理与人类审阅 H0–H3](#5-ai-整理与人类审阅-h0h3)
6. [未决问题与用户反馈](#6-未决问题与用户反馈)
7. [与 P00–P03 的关系](#7-与-p00p03-的关系)

---

# 1. 实验身份与目标

- **实验名称：**
- **合作组 / 实验项目：**
- **论文或公开发布名称：**
- **Dataset / run period / data release：**
- **靶材与探测器：**
- **主要观测量：**
- **论文、DOI、arXiv 或官方网站：**

如果同一实验存在不同 run、探测器配置、靶材、阈值、分箱或数据发布，请分别列出候选，不要默认合并。

### 本次研究目标

希望完成什么物理工作？例如预测信号谱、复现论文 benchmark、比较理论参数、迁移已有分析或进行统计拟合。

> 填写：

### 希望得到的结果

例如 recoil spectrum、PE/S1/S2 spectrum、分箱事件数、time-energy distribution、参数区间或统计显著度。

> 填写：

### 本次不处理的范围

> 填写；没有限制可留空。

---

# 2. 已有材料

只需提供名称、链接或本地路径。哈希、文件解析、单位和坐标检查由 AI/程序完成。

| 材料 | 名称 / 链接 / 路径 | 版本 / 日期 | 备注 |
|---|---|---|---|
| 主论文 |  |  |  |
| Supplement / erratum |  |  |  |
| 官方数据发布 |  |  |  |
| Source / exposure 资料 |  |  |  |
| Target / isotope 资料 |  |  |  |
| Detector calibration |  |  |  |
| Theory / nuclear input |  |  |  |
| Observed/background/covariance |  |  |  |
| 旧程序 / 配置 / benchmark |  |  |  |

### 材料说明

- 哪些材料是必须采用的？
- 哪些只是参考？
- 哪些旧版本不应使用？
- 是否还有尚未提供的重要材料？

> 填写：

---

# 3. 已知实验条件

只填写已知信息，不要求用户自行完成参数提取。

### Source

源类型、源分量、谱、POT/曝光、运行时间、baseline、已知归一化约定。

> 填写：

### Target and exposure

靶材料、核素、质量分数、有效质量、曝光定义。

> 填写：

### Detector

探测器类型、quenching/light yield、resolution、efficiency、acceptance、threshold、analysis window。

> 填写：

### Observable and data

观测量、binning、raw observed、background、uncertainty、covariance、time/energy axes。

> 填写：

### Statistics

论文使用的 likelihood/χ²、nuisance、profile/marginalization 或 benchmark 定义（如果知道）。

> 填写：

---

# 4. 本次希望采用的模块

**本节不是让用户解释这些模块的理论。** AI 应先检查项目 Registry 中实际存在的模块，再列出候选、兼容性和所需输入，由用户确认。

| 独立选择维度 | 候选 / 本次选择 | 依据或待确认 |
|---|---|---|
| Interaction theory | SM / NSI / Full EFT / 其他已注册选项 |  |
| Nuclear structure | Helm / Nuclear Response / 其他已注册选项 |  |
| Kinematics | 项目已注册模块 |  |
| Cross-section | 项目已注册模块 |  |
| Detector response | 与本实验校准和观测量匹配的模块 |  |
| Statistics | 与论文数据和 likelihood 定义匹配的模块 |  |

注意：

- Interaction theory 与 Nuclear structure 是两个不同选择轴。
- Helm / Nuclear Response 不等同于 SM / NSI / Full EFT。
- 只有项目中真实存在且通过接口兼容性检查的模块才可选。
- 如果没有合适模块，标记缺失；不要为填表而虚构模块 ID。
- Statistics 可替换实现，但实验文章确定的 observed data、background、binning、covariance 和 likelihood 语义不能擅自更改。

---

# 5. AI 整理与人类审阅 H0–H3

> 本节由 AI 根据材料预填。每个节点必须以自然语言和适量表格呈现，不把 YAML、源码或完整机器台账贴给用户。

## H0 — 实验身份与目标

AI 总结：

- 识别出的 experiment / dataset / run / release；
- 与同名其他数据集的区别；
- 本次 scientific goal 和 requested observable；
- 当前 identity 是否唯一。

**用户检查：** 实验和数据发布是否选对？

## H1 — 材料审阅

AI 按材料逐项说明：

- 材料是什么、版本是什么；
- 能支持哪些实验事实；
- 不能证明哪些主张；
- 是否存在缺失、冲突或过期版本。

**用户检查：** 材料是否完整、版本是否正确？

## H2 — 证据摘要

AI 按 Source、Target、Interaction、Nuclear Structure、Detector、Observable、Statistics 分组展示关键事实。每项关键事实列出值、单位、出处和证据类别：

- 论文/官方资料直接给出；
- 旧代码提取；
- 明确公式推导；
- 数值表格化/插值生成；
- 仅供参考；
- 缺失或冲突。

**用户检查：** AI 是否忠实提取了材料？有没有把旧代码值误称为官方值？

## H3 — 实验配置与模块选择

AI 展示本实验的完整配置草案。模块选择按独立维度呈现：

1. Interaction：SM / NSI / Full EFT，列实际注册的 model IDs。
2. Nuclear structure：Helm / Nuclear Response，单独列 model ID 和资源引用。
3. Kinematics / Cross-section：只列实际使用的共享模块 ID。
4. Detector：列本实验采用的响应函数、完整公式、参数、单位、定义域和作用顺序。
5. Statistics：列实验论文规定的完整统计模型、分箱、数据、background、uncertainty/covariance、nuisance 和 profiling。

Source、Target、Detector、Observable、Prediction folding 和 Statistics 的实验专属公式必须足够详细，能供实现人员编写实验适配代码。共享 Interaction、Nuclear Structure、Kinematics、Cross-section 只记录选择，不复制公共理论公式。

**用户检查：** 物理配置和模块组合是否符合本实验？统计数据和论文定义是否一致？

---

# 6. 未决问题与用户反馈

每个问题说明它影响本次目标的哪一部分、需要什么材料或决定。来源冲突必须并列保留，不能静默选择。

- **问题：**
- **影响：**
- **需要的材料 / 决定：**

用户对 H0–H3 的反馈：

> 填写或在对话中指出。

---

# 7. 与 P00–P03 的关系

本文件是人类阅读入口，不是机器台账。

| 记录 | 职责 |
|---|---|
| P00 Source Register | 材料身份、版本、路径和 hash；来源身份唯一权威 |
| P01 Evidence Ledger | claim、值、单位、出处、证据状态；只引用 P00 的 source_id |
| P02 Missing and Conflicts | 缺失、冲突、影响和待解决事项 |
| P03 Partial Physics Contract | 实验配置、模块选择和 Physics MD 内容元数据 |

P03 中 Interaction 与 Nuclear Structure 必须分别记录。Physics MD 的实验专属公式与统计定义来自已审阅的 P03 metadata；公共模块的理论说明不复制到每个实验文件。

本文件不批准科学选择，不代表 Runtime 验证或官方 benchmark 复现完成。
