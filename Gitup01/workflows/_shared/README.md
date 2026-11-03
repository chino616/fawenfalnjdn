# _shared：所有实验共用的输入规范与协作依据

**检查实验输入文件，先读[共同输入规范](INPUT_STANDARD.md)。** 本目录集中维护所有实验共用的输入要求、格式、空白模板、证据和审核规则，作为使用者与执行者核对原始材料、整理数据和检查读取结果的共同依据。各 dataset 的具体内容与结果保存在自己的目录。

共同规范给出检查内容、适用条件和实际检查入口；任务路由仍由 Master 管理，科学决定、写入授权与运行算法仍由各自权威文件负责。

| 子目录 | 具体用途与消费者 |
|---|---|
| [INPUT_STANDARD.md](INPUT_STANDARD.md) | 使用者、Master 与阶段 Skill 的输入检查入口：要求、适用范围、格式、真实消费者和验证覆盖 |
| [policies/](policies/) | Master/各流程读取交互、授权、证据、隔离和恢复规则 |
| [schemas/](schemas/) | [experiment-input/](schemas/experiment-input/README.md) 管实验配置和命名表格格式；其余 schema 管 request、authorization、input manifest、physics contract、evidence ledger 与 phase result |
| [templates/](templates/) | onboarding、phase、auto 及 scope/input/Phase 0/report 的可填写模板 |
| [references/](references/) | [runtime API](references/runtime-api-map.md)、[物理模块](references/physics-module-map.md)、[测试](references/test-map.md)与阶段代码定位 |

## 规则由哪个文件拥有

| 责任 / 原审计章节 | 权威文件 |
|---|---|
| 检查输入内容、选择适用格式与记录检查覆盖 | [共同输入规范](INPUT_STANDARD.md) |
| 全仓库文件增删、移动和 README/导航同步 | [file-lifecycle](policies/file-lifecycle.md) |
| 活动实验交互 / 1 | [interaction](policies/interaction.md) |
| 科学决策、机器/人工门槛和证据 / 2、3、5、6 | [evidence-and-approval](policies/evidence-and-approval.md) |
| 写入授权与日志 / 4、4.1、12 | [write-authorization](policies/write-authorization.md) |
| 范围、冻结和逐步明确输入 / 7、8、10 | [scientific-integrity](policies/scientific-integrity.md) |
| 实验/dataset 目录身份 / 8.1 | [dataset-layout](policies/dataset-layout.md) |
| 备份/归档隔离 / 9 | [archive-isolation](policies/archive-isolation.md) |
| revision、恢复、指纹和失效 / 11 | [progress-continuity](policies/progress-continuity.md) |
| 隔离自动运行 / 原 4.2 | [automation](policies/automation.md) |

## 管理与新增文件

所有文件操作同时执行[文件与 README 联动维护](policies/file-lifecycle.md)，在本次变更中对应“文件 → 所属 README → 上级导航/消费者 → 检查结果”。删除文件清理条目，目录仍有活动内容就保留说明；当前没有自动改写 README 的监听器。

大幅删减或 Git 差异维护由[仓库维护流程](../cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)执行；它支持显式同步 README 自动目录区，保留人工解释，维护完成后按同一基线验收。

共同输入要求在 INPUT_STANDARD 维护，审批与恢复规则只修改对应 policy；AGENTS/Skill 通过链接引用。新增实验输入格式放 `schemas/experiment-input/`；工作记录结构放 schemas 的对应位置。JSON Schema 使用 2020-12/YAML 1.2 JSON 子集；命名 CSV 格式约定不伪装成 JSON Schema。每种格式都要注明实际消费者及自动/人工检查覆盖。

新增空白表单按用途放 `templates/onboarding/`、`templates/phase/` 或 `templates/auto/`；某 dataset 已填写的记录应进入它自己的获准目录，不写回通用模板。代码参考放 references，标明真实路径和函数，由 `audit_references.py` 核对。

修改后检查引用、schema、阶段映射和受影响流程；使用项目 [工作流 README](../README.md) 的结构检查命令。政策变动不能把已有历史授权扩大为新任务授权。

---

[上一级](../README.md) · [项目总览](../../README.md)
