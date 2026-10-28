# CEvNS-pyEFT 接口与物理传递重构执行文档包

版本：1.0 · 编制日期：2026-10-28（Asia/Shanghai）

目标仓库：`chino616/fawenfalnjdn`；目标目录：`Gitup01/`。
核对分支：`conus-v2-current-snapshot-20261011`。
源码基线：`e04ab7a9270380d6fd0191735c489e5b7c5fe2e4`。

**本包是交给 Codex 的重构说明与验收规范，不是已实现的新框架，也不是可直接安装的 Skill。**
本包最初作为设计说明创建。当前实施状态以 Gitup01/docs/interface_refactor 的阶段报告、实际代码和测试日志为准。

## 1. 要实现的结果

从目前“具体实验入口调用共享函数”的结构，逐步形成以下结构：

1. 实验入口明确选择源、运行期、靶核、相互作用、观测模型和分箱。
2. 共用积分器只消费约定好的物理对象，不识别 SNS/CsI 的名字和专有字段。
3. 单位、分量轴、归一化责任和适用物理条件可被程序检查。
4. 旧实现与新实现同时存在；通过替换模型中的一个组件比较结果。
5. Skill 能读到实际接口、组件依赖、支持能力和验证入口，执行范围明确的模块替换。

首先完成 **CsI2021 一维 9 箱、保持现有行为的接口迁移**。随后完成同一物理模型的 Fast、缓存、接口审阅和发行验证。CsI2017/Ar2020 是必须保护的共享代码回归对象，不在第一阶段自动迁移其物理约定。

## 2. Codex 从哪里开始

首先阅读 [00_CODEX_START_HERE.md](00_CODEX_START_HERE.md)。
如果要直接提供任务提示词，使用其中的“可复制的启动任务”，并明确你实际授权的阶段范围。

本包可以放在项目外，也可以在获得对应写入授权后放在 `Gitup01/docs/refactor_interfaces/`。
文中 `src/`、`tests/`、`data/` 和 `workflows/` 路径均相对于 **Gitup01/**。
文档之间的链接相对于本包，所有建议路径均以文字给出，不假装这些文件已经存在。

## 3. 阅读导航

| 文档 | 用途 | 何时读取 |
|---|---|---|
| [00_CODEX_START_HERE.md](00_CODEX_START_HERE.md) | 执行入口、授权范围、优先级与恢复规则 | 每次开始或恢复 |
| [01_BASELINE_AUDIT.md](01_BASELINE_AUDIT.md) | 已核实的源码事实、符号锚点及证据边界 | 开始修改前 |
| [02_ARCHITECTURE_AND_DECISIONS.md](02_ARCHITECTURE_AND_DECISIONS.md) | 架构、依赖方向、设计决策 | 所有阶段 |
| [03_SOURCE_AND_EXPOSURE_CONTRACTS.md](03_SOURCE_AND_EXPOSURE_CONTRACTS.md) | 源、运行期、连续谱、谱线和入射态 | 源与积分阶段 |
| [04_TARGET_AND_INTERACTION_CONTRACTS.md](04_TARGET_AND_INTERACTION_CONTRACTS.md) | 靶核数、截面及运动学接口 | 理论适配阶段 |
| [05_OBSERVATION_AND_PREDICTION_CONTRACTS.md](05_OBSERVATION_AND_PREDICTION_CONTRACTS.md) | 探测器、选择、分箱和输出对象 | 折叠与统计接口阶段 |
| [06_PIPELINE_AND_ASSEMBLY.md](06_PIPELINE_AND_ASSEMBLY.md) | 实验组装、计算步骤与兼容包装 | 主链实现阶段 |
| [07_FILE_CHANGE_MAP.md](07_FILE_CHANGE_MAP.md) | 当前文件到新职责的映射、修改顺序 | 编写变更计划时 |
| [08_IMPLEMENTATION_PHASES.md](08_IMPLEMENTATION_PHASES.md) | R0–R6 的输入、动作、验收和边界 | 每阶段执行 |
| [09_MODULE_INTERFACE_REVIEW.md](09_MODULE_INTERFACE_REVIEW.md) | 模块合同、组件替换和交付边界 | R5–R6 |
| [10_FAST_KERNEL_AND_CACHE.md](10_FAST_KERNEL_AND_CACHE.md) | Fast 数学能力、物理指纹、失效规则 | Fast 阶段 |
| [11_VALIDATION_AND_ACCEPTANCE.md](11_VALIDATION_AND_ACCEPTANCE.md) | 必要测试、误差标准及报告要求 | 实现与审核 |
| [12_SKILL_REPLACEMENT_PROTOCOL.md](12_SKILL_REPLACEMENT_PROTOCOL.md) | 供 Skill 执行的替换协议 | 每次替换 |
| [13_TASK_AND_REVIEW_TEMPLATES.md](13_TASK_AND_REVIEW_TEMPLATES.md) | 任务卡、替换卡、阶段报告和断点模板 | 记录实际工作 |
| [14_RISKS_AND_OPEN_INPUTS.md](14_RISKS_AND_OPEN_INPUTS.md) | 未闭合物理问题及资料缺口 | 涉及能力扩展时 |
| [15_PACKAGE_MANIFEST.md](15_PACKAGE_MANIFEST.md) | 文档清单、哈希与本包质量检查结果 | 核验文档包 |

## 4. 必须区分的状态

- `CURRENT`：在给定提交的源码中已核对。
- `DESIGN`：本包提出的目标接口，不能直接 import。
- `IMPLEMENTED`：后续执行者实际写入并接入调用链；本包不预授此状态。
- `VERIFIED`：指定检查实际运行并通过；需要日志和参数。
- `MISSING`：缺少数据、证据或必要实现。

设计文档完整、接口代码存在、旧结果复现、新物理正确，是四种不同的完成程度。

## 5. 当前验证边界

源码与已有测试内容已经阅读；本次会话曾用粗网格检查 CsI2021 的 9 箱结构和源分量求和，以及二维输入与现有 9 箱观测的维度冲突。这些不是收敛的科学 benchmark。
此处描述原始文档生成时的验证边界；后续执行已使用用户指定的 Conda 环境，实际测试结果见项目实施报告。
本包中的未来测试名和新 API 均为实施要求，不能列入已通过检查。

包内不含目标仓库副本、预计算 Fast 核或虚构的测试结果。
