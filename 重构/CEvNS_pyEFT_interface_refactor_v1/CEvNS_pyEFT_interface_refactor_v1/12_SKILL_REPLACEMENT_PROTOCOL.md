# 供 Skill 使用的模块替换协议

状态：DESIGN。本文件是项目接口的执行说明，不是安装用 SKILL.md，也不替换现有 Master Skill。
相关：[阶段](08_IMPLEMENTATION_PHASES.md) · [验证](11_VALIDATION_AND_ACCEPTANCE.md) · [模板](13_TASK_AND_REVIEW_TEMPLATES.md)。

## 1. Skill 的明确工作对象

Skill 替换的是组装模型中的 slot，而不是根据文件名搜索然后覆盖某个 py。

首批 slot：`source`、`targets`、`interaction`、`observation.response`、`observation.efficiency`、`observation.selection`、`binning`。
运行期是单独的 `run`；源变更与 run 不兼容时，Skill 报告需同步变更的范围。
时间源和一般 Fast 是能力扩展，不因 slot 名称存在而自动支持。

## 2. ModuleDescriptor 最小字段

描述由实际模块实例导出，与运行时校验共用字段定义。

| 字段 | 用途 |
|---|---|
| `slot_kind` | 它可放在哪类插槽 |
| `contract_id/contract_version` | 调用与物理交接合同 |
| `model_id/model_revision` | 实现与物理版本 |
| `capabilities` | 已实现的过程、状态、时间和 Fast 表示能力 |
| `input_contract/output_contract` | 单位、轴、量类型、支撑 |
| `normalization_ownership` | 已含和禁止再含的因子 |
| `parameters` | 实际消费的参数和值 |
| `resources` | 资源身份、内容哈希和必要来源 |
| `dependencies` | 实际读取的其他模型/参数依赖 |
| `validation_entrypoints` | 可运行的合同及模型基准检查 |

协议不要求 metadata 自己证明物理正确。检查还需真实求值、独立基准和阶段报告。
描述与实现不一致时视为模块缺陷，不能用文档声明覆盖实际输出。

## 3. 替换任务分类

| 分类 | 定义 | Skill 动作 |
|---|---|---|
| `PARAMETER_CHANGE` | 同实现、同合同、改变明确参数 | 构造新实例、重新校验、更新依赖结果 |
| `COMPATIBLE_REPLACEMENT` | 新实现满足同合同及能力条件 | 增加实现和测试，更新目标组装选择 |
| `ADAPTER_REQUIRED` | 物理含义兼容但数据单位/结构不同 | 添加显式适配器并验证转换 |
| `CAPABILITY_EXTENSION` | 需要时间相关、能量态、额外过程变量等 | 给出受影响接口与调用方，按授权实施扩展 |
| `PHYSICS_CHANGE` | 改变理论规范、源归一化路线等 | 独立记录物理依据和适用流程 |
| `MISSING_INPUT` | 当前阶段缺少必须资料 | 仅阻断依赖该资料的能力 |

一个任务可以同时属于多类，例如新时间源同时需要 CAPABILITY_EXTENSION 和新的数据输入。
禁止把所有任务都标成“换一个文件”，也禁止把任何参数调整都扩成全项目重构。

## 4. 固定执行算法

### A. 读取真实模型

读取目标实例/工厂、解析后的运行记录、当前 ModuleDescriptor，以及对应合同和源码。检查实际 commit 与待替换模块版本。
不要从旧聊天、文件名或 YAML 中的 `validated` 字样推断当前能力。

### B. 生成 ReplacementPlan

至少记录 old/new slot、任务分类、输入来源、合同差异、允许写入路径、必须保持的旧行为、需要失效的结果和实际测试入口。
模板见 13。计划只是计划，不构成批准或验证通过。
依据当前用户授权和适用 AGENTS 判断能否继续；已有授权覆盖的动作不重复请求。

### C. 实现新模块或适配器

保留旧实现；显式参数；不修改全局默认来让旧程序使用新物理。
同合同替换一般只允许新模块/数据/对应测试和目标工厂变更。若必须修改通用积分器，重新分类为接口/能力扩展并说明原因。
共享理论、核响应、数值模块的额外改动必须与任务目标有关，不能借替换顺便清理不相关代码。

### D. 兼容性预检

核对 process、单位、坐标、source IDs、particle treatment、运行期、选择归属和后端能力。
输出具体诊断，例如“新源使用 reactor_core_1，但旧选择模型只定义 SNS 三分量”；不能自动重命名为 mub 绕过校验。
若新源是每秒 flux 而 run 是 POTExposure，要求给出正确组合，不自动设时间为 1。

### E. 验证与重新计算

先模块合同，再独立模型检查，再真实 predict 链路，再受影响共享回归。
执行实际依赖失效，生成新的预测/核；旧文件可以保留用于复现，不作为新配置结果使用。
新模型结果不必等于旧模型；纯接口迁移则必须保持旧结果。

### F. 交付可审核差异

给出改动位置、公式/输入变化、模块描述、实际测试、物理能力边界和恢复方式。
工作流状态按适用 Master 处理，机器测试不能制造 Human approval。

## 5. 三个替换示例

### 源表替换

新增 TableFluenceSource，声明单位/运行期/支撑/插值；验证连续与谱线结构。只改 source slot。
如果新的输入类型需要不同 run，ReplacementPlan 明确列出 run 更新。固定靶和截面可复用；含源的 H 失效。

### 探测器效率替换

新增 TableEfficiency；核对自变量是 PE 还是 keV，是否已经含阈值/触发/时间选择。
只改变 efficiency slot；每核反冲产额可复用，观测折叠与含效率的 H 重新生成。
不能将效率值乘进源表以避免改接口。

### 相互作用替换

如果过程、运动学和输出量不变，新增 InteractionModel 实现并给出独立基准。
如果新末态使 dσ/dT 不再完整描述过程，分类 CAPABILITY_EXTENSION，不假装与旧接口完全兼容。
Slow 可用不等于 Fast 可用，分别验证。

## 6. 人与 Skill 共用同一可读结构

人读工厂知道采用何种物理组合；读 RecoilYield/Prediction 知道单位和计算进度。
Skill 读取相同对象的机器描述，定位 slot、写入范围和检查入口。
对每个模型提供简短模块说明：物理定义、输入输出、已含因子、支持能力、数据来源、独立基准。不要维护另一套与代码不同步的巨型参数表。

## 7. 完成定义

`replacement_implemented`：实际新实现被目标入口消费。
`contract_verified`：输入输出和兼容性检查通过。
`regression_verified`：应保持的旧行为经过实际回归。
`physics_benchmark_verified`：在明确适用域内通过独立物理基准。
`fast_verified`/`statistics_verified`：分别记录，允许未请求或未实现。

以上记录与代码/数据指纹绑定；后续修改后不能沿用旧 PASS。接口能检查组合是否合法，不能仅靠 schema 保证科学结论正确。
