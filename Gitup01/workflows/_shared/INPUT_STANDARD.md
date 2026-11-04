# 共同输入规范与文件检查入口

本文件是使用者与执行者检查实验输入文件的共同依据。接收新材料、填写资料表、生成实验 data，或修改已有输入时，先从这里确定适用要求，再到对应 schema、模板和实际读取器核对。所有实验共用这些检查要求；每个 dataset 的具体值、文件和审核结论独立保存。

规范版本：`input_standard_version: 1`。一次检查应记录本文件及所用 schema 的路径、版本或 SHA256，保证后续能够判断检查是否仍适用。

## 在整个框架中的位置

```text
共同输入规范（检查什么、依据什么、适用范围）
  → 原始材料与文件身份登记
  → 按规范提取字段、核对数值、保留证据
  → 同一资料模板与 Physics Contract
  → 各 dataset 自己的 data 和显式资源绑定
  → 实际读取检查、对应阶段验证与用户审核
```

输入规范统一检查依据；[Master](../cevns-pyeft/skills/router/cevns-experiment/SKILL.md) 仍按
[唯一路由表](../cevns-pyeft/router/routes.yaml) 选择流程并管理阶段。
[证据与批准政策](policies/evidence-and-approval.md) 管科学决定，
[写入政策](policies/write-authorization.md) 管适用范围内的文件授权。
格式通过、模板填满和文件已经存在都不能代替对应的物理审核。

## 使用者怎样检查一个输入文件

1. 明确它属于哪个 dataset、运行期和配置，承担源谱、效率、观测、背景或参考等哪种角色，以及本次要得到什么结果。
2. 按下表选出适用规则，找到确切 schema 或已有数据集格式说明。某项不适用时记录理由；尚未查清的内容保持缺失。
3. 核对原文件中的列、坐标、数值和公式，把来源定位、单位、归一化、转换和保存位置写入证据台账与合同。转换后的表仍应能追查到原文件的行列或符号。
4. 用真实消费者加载整理后的文件，检查显式资源、数据轴、形状、单位和转换次数；记录运行命令、实际结果及未执行的检查。
5. 按本次目标说明输入可支持哪些能力、缺什么，以及哪些解释需要用户决定。只阻断依赖缺失项的能力，资料整理可继续；当前阶段所需输入未满足时不把该阶段记为通过。

可使用 [输入文件检查记录模板](templates/onboarding/INPUT_FILE_REVIEW_TEMPLATE.md)，也可把同样的信息放进已有 Phase 报告。记录只引用材料、证据、决定与检查结果的权威位置，不另造一套批准状态。

## 所有实验共用的检查要求

| 规则 | 检查内容 | 适用范围与核对要点 |
|---|---|---|
| I01 身份与来源 | dataset、运行期/探测器、文件角色、版本、路径、哈希、source_id | 所有输入；材料路径可为明确提供的外部路径，正式资源再按显式资源根绑定；保留来源定位 |
| I02 目标与输出 | 计算目标、结果性质、计数或率、输出量、轴顺序、shape、单位 | 所有整理结果；官方复现、项目近似和旧程序回归分别说明 |
| I03 列与单位 | 列名或原始列号、坐标/数值列、单位、缺失值、解析规则 | 所有数值输入；例如 MeV 与 keV、PE 与电离能、counts/PE 与 events/bin 必须区分 |
| I04 坐标与分箱 | 坐标支撑、顺序、重复点、精确 bin edges、行到箱的对应、端点规则 | 谱表、效率表、分箱和观测；数字化坐标保留原值，排序、插值或重分箱必须说明依据 |
| I05 归一化 | 源发射谱或探测器通量、每秒或已积分、质量/时间/几何/效率是否已施加 | 信号、响应和参考谱；每个因子只施加一次，POT 积分注量不重复乘活时间 |
| I06 源与表示形式 | ν/反ν、flavor/密度矩阵、连续谱/谱线、公式参数、插值和范围外行为 | 信号源；SNS 的 POT、反应堆的功率/裂变份额等是按源类型启用的要求，不是所有实验的固定字段 |
| I07 靶与曝光 | 同位素、核响应 key、数丰度/质量分数/化学计量、核质量、核数和曝光含义 | 信号模型；原始给定量与项目推导量分开，不能从 kg·day 猜造独立质量和时间 |
| I08 探测器与选择 | 真实量到观测量映射、迁移/分辨率、核归一化范围、效率作用域、阈值和窗口 | 重建谱/逐箱输出；必须区分真实反冲、平均观测量和重建观测量 |
| I09 观测与统计 | raw/ON-OFF/excess 等数据模式、背景、误差、协方差、likelihood、nuisance | 申请统计能力时；保留 residual 的负值，缺协方差不自动补单位阵，原生单位只按明确映射转换 |
| I10 基准与限制 | 外部参考来源、生成参数点、单位/轴/归一化、缺失冲突、实际验证范围 | 复现与能力声明；内部回读、Slow/Fast 一致和官方论文复现分别报告 |

关键字段沿用 [onboarding](../cevns-pyeft/skills/onboarding/cevns-onboarding/SKILL.md) 的结构：
`value / unit / evidence_claims / provenance_status / decision_status / blocking_scope`。
公式附自变量和有效域；数值表附列映射、支撑与插值规则；推导附公式和输入 claim。
缺失保持 `MISSING`，冲突保留各方 claim；状态定义以共享证据政策为准。

## 去哪里找对应规范

| 对象 | 格式或填写依据 | 当前实际检查方式与覆盖范围 |
|---|---|---|
| 三文件 Experiment Input Package v1 | [正式 schema](../../cevns_pyeft/experiments/input_package.schema.json) 与[格式/权威说明](../../docs/software/experiment-input-package.md) | [input_package.py](../../cevns_pyeft/experiments/input_package.py) 以严格 JSON-compatible YAML、Draft202012Validator 及跨字段/NPZ/指纹/MD 校验执行；不绑定模型、不等于 Runtime 或科学批准 |
| 实验说明 `experiment.yaml` | [experiment.schema.json](schemas/experiment-input/experiment.schema.json) | [specs.py](../../cevns_pyeft/experiments/specs.py) 的 `validate_experiment_spec_data` 只检查必填字段；没有自动执行完整 JSON Schema 或全部科学要求 |
| 约定的 reactor spectrum、efficiency、bin edges、isotopes 表 | [csv_contracts.json](schemas/experiment-input/csv_contracts.json) 与[格式说明](schemas/experiment-input/README.md) | 这是命名格式约定表；按已选 profile 核对列及数值要求，当前没有覆盖所有 CSV 的通用执行器；`energy_evee` 列约定不强加给 PE 等其他数据 |
| 用户资料表 | [统一输入模板](templates/onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md) | 人填和 AI 摘录共用栏目；每个 dataset 独立填写，数值须附来源 |
| 材料登记 | [input-manifest schema](schemas/input-manifest.schema.yaml) 与[模板](templates/input-manifest.yaml) | 结构检查覆盖登记字段；实际文件存在、哈希和来源真实性仍分别核对 |
| 证据与物理合同 | [evidence-ledger schema](schemas/evidence-ledger.schema.yaml)、[physics-contract schema](schemas/physics-contract.schema.yaml) 与 [onboarding 模板](templates/onboarding/) | 证据状态与物理决定分开；合同结构可由现有 Phase 校验器检查，不能据此认证外部资料 |
| dataset 特有观测坐标 | dataset 自己的 schema，例如 [CsI2017 observation_schema.json](../../data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json) | [tables.py](../../cevns_pyeft/statistics/tables.py) 实际核对 bin、原始数字化坐标、顺序与数值 shape |
| 实际运行输入 | [definition/loader](../../cevns_pyeft/experiments/README.md)、[运行接口合同](../../cevns_pyeft/contracts/README.md)、[资源清单](../../data/resource_manifest.json) | loader/runtime 和各组件核对实际资源、轴、形状及其实现支持的单位/归一化；资源审计核对路径与哈希 |
| 阶段检查与接受 | [Phase 执行合同](references/phase/PHASE_EXECUTION_CONTRACT.md)、[phase-result schema](schemas/phase-result.schema.yaml) | 在已有阶段报告里记录命令、结果、证据、决定和当前版本的实际接受 |

schema 声明的规则与读取器实际执行的规则应分别记录。尚无自动检查器时，保留人工检查记录并说明覆盖范围；不得写成已自动验证。

## 按目标检查足够的输入

| 本次目标 | 当前必须核对的输入 |
|---|---|
| 真实反冲谱 | 身份/输出、源及入射态、靶与归一化、相互作用与运动学 |
| 重建谱或逐箱信号 | 再加探测器响应、效率、窗口与精确分箱 |
| Fast | 对应已验证并获所需接受的 Slow、表示与参数域、缓存依赖 |
| likelihood 或置信区间 | 对应前向预测、观测数据语义、所用统计模型必需的背景/误差/相关性与推断规则 |
| 外部数值复现 | 对应计算输入，以及同条件的外部基准和来源 |

初始收集允许 partial contract；每个后续阶段只在使用相关字段前补齐必要细节。
检查及正式审核仍按现有 Master/Phase 机制执行，不增加独立的全量前置审核。

## 每个实验保存什么，怎样使用共享规范

共享目录维护通用规则、空白表单和格式；填写结果、原始表与决定按
[dataset-layout](policies/dataset-layout.md) 保存到该实验自己的 docs、runs 和 data。
检查记录至少关联“原始文件 → claim → 合同字段 → data 文件/列 → 实际消费者/检查结果”，
使使用者能够逐项核对转换。

只有某实验使用的列映射、特殊响应或具体数值，保留在该实验中。共享规范新增或改变格式时，
记录版本、适用 profile、实际消费者和受影响 dataset；新物理含义按相关阶段审核。
目录移动本身不改变物理字段、审核结果或已有批准。

文件变动后，按实际依赖重新核对受影响输入和下游能力，执行
[progress-continuity](policies/progress-continuity.md)。共享规范版本变化也须说明其是否影响既有检查，
不自动重置无关阶段，不静默把历史结果升级为新版通过。

## 可直接执行的检查

从项目根目录按实际目标运行：

```powershell
python -B tools/validate_resource_manifest.py --root .
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py --check-schemas
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py <实际报告或JSON合同路径> --kind physics
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py
```

其中 `--kind physics` 只用于实际 Physics Contract；阶段报告按
[QA 用法](../cevns-pyeft/qa/README.md) 选择参数。资源审计检查已绑定资源，Phase 校验检查所给记录，
Skill 校验检查流程结构与引用。它们不会自动理解任意新论文、穷尽所有数值文件或批准科学结论。

物理运行包继续通过显式资源与运行接口工作，不把本目录作为运行依赖。
如需新增自动数据检查，应把“声明 → 实际消费者 → 正常/拒绝样例 → 用户可见结果”一起接通。
