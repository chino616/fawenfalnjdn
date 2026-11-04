# docs：理解当前程序与 COHERENT 分析

Status: CURRENT

[项目级迁移报告](PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)与
[活动清单](PROJECT_DATASET_MIGRATION_INVENTORY.md)汇总三个已注册实验的三文件、
默认 Runtime、回归和安装验收；科学接受按能力单列。

[Dataset三文件分发](DATASET_PACKAGE_LIFECYCLE_REPORT.md)记录ownership、wheel/sdist和安装验证。

[通用生成器报告](GENERAL_ONBOARDING_GENERATOR_REPORT.md)记录IR/v2合同与跨实验fixture验收。

[科学来源审查](CSI2021_SCIENTIFIC_PROVENANCE_REPORT.md)区分官方原文抽查、legacy行为及未闭合能力。

[两文件独立验证](CSI2021_STANDALONE_VALIDATION_REPORT.md)记录 I01–I10、安装后运行和网格诊断。

[CsI2021 运行迁移报告](CSI2021_PACKAGE_RUNTIME_MIGRATION_REPORT.md)记录默认入口、兼容视图与数值范围。

[Package Loader 报告](EXPERIMENT_PACKAGE_LOADER_REPORT.md)记录两文件装配与现有 Runtime 的实际连接。

三文件输入架构的受控实现见 [模型绑定报告](PHYSICS_MODEL_BINDING_REPORT.md)；
连续任务状态见 [Tasks 02–10 进度](ONBOARDING_TASKS_02_10_PROGRESS.md)。

这里说明“如何调用程序、物理量如何约定、代码与数据由谁管理、各实验使用哪些输入”。当前目录采用四类文档；实验部分集中于 CsI2017、CsI2021、Ar2020，并保留两项 COHERENT 科学审查。

| 分类 | 从什么问题开始 | 对应代码 |
|---|---|---|
| [user-guide/](user-guide/README.md) | 怎样运行、选后端、换组件、使用缓存 | `experiments.loader/runtime`、`core.predict`、`kernels` |
| [software/](software/README.md) | 文件放哪里、资源根怎样解析、Catalog 怎样注册、wheel 含什么 | `manifest/catalog/loader`、`foundation.resources`、`pyproject.toml` |
| [physics/](physics/README.md) | 单位、味矩阵、运动学与尚待核实的科学约定 | `core.interaction_point`、`theory/li2026`、`nuclear` |
| [experiments/](experiments/README.md) | 某个 COHERENT 数据集怎样绑定参数、观测和分析 | 三份 `coherent/*_definition.py` 与统计绑定 |

## 阅读顺序与实际入口

[正式三文件输入合同](software/experiment-input-package.md)说明 v1 格式、参数角色和
校验命令；[Task 02 报告](EXPERIMENT_INPUT_SCHEMA_REPORT.md)记录 Pilot 语义校正及验收结果。
[Tasks 02–10 续跑进度](ONBOARDING_TASKS_02_10_PROGRESS.md)保存逐任务结果、限制和下一断点。

旧九箱 CsI2021 的[三文件 Onboarding 试点报告](CSI2021_ONBOARDING_PILOT_REPORT.md)
记录当前 07 分支的参数/数组提取、公式解释、一致性检查及缺失和冲突。
正式输入在 [CsI2021 data 目录](../data/experiments/COHERENT_CsI/CsI2021/README.md)，
状态为 DRAFT/PARTIAL；这份审计没有把新输入包接入 Runtime。

先按[根 README](../README.md)跑通一次预测，再读[使用与替换](user-guide/USAGE.md)、[能力矩阵](user-guide/capability-matrix.md)和[参数归属](user-guide/parameter-ownership.md)。想追踪程序，直接从 [loader.py](../cevns_pyeft/experiments/loader.py) 到 [runtime.py](../cevns_pyeft/experiments/runtime.py)，再进入该实验 executor。

两项科学审查分别位于 [statistics review](experiments/COHERENT/reviews/2026-10-22-statistics-review/README.md) 与 [Fig.3–Fig.7 overlap review](experiments/COHERENT/reviews/2026-10-22-fig3-fig7-overlap-review/README.md)，分析定义不同，不能互换数值或把历史报告当作当前重跑结果。

## 管理与新增文档

先按读者的问题选择上述目录，再新建命名明确的 Markdown，并在该分类 README 添加入口。当前接口说明要链接真实代码、输入资源和测试；示例命令应写执行目录、依赖与输出，不能把拟议接口描述为已实现。

物理约定标明单位/轴、来源和验证范围；未闭合问题保持 REVIEW。实验特有资料归对应实验，通用说明归 user-guide/software/physics。新工具输出和工程运行日志放 `outputs/<运行>/`，不要因文件是 Markdown 就全部塞进 docs。

CURRENT 表示当前说明；REFERENCE 表示参考资料；HISTORICAL 表示原任务记录；REVIEW 表示待核实问题。科学审查的 CSV/JSON 和证据应保留原始含义，新增结论用独立说明记录依据。文档改动不构成新实验注册或科学批准。

从根目录运行 `python tools/validate_docs.py --scope docs` 检查本地文件链接；代码示例还需用相应解释器实际核对。更改文档分类时同步本页与上级导航，以最新存在的目录为准。

---

[上一级](../README.md)


## CsI2021 P04–P10 执行审计

[最终执行报告](../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/11_FINAL_EXECUTION_REPORT.md) 汇总本次三文件到真实 P04–P10 的交接、能力 Gate、数值、版本差异和交付；[Skill 问题审计](../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/12_SKILL_WORKFLOW_AUDIT.md) 列出最小修正与未闭合项。
