# _shared：工作流共用的规则与记录合同

本目录提供可被多个流程引用的一份权威材料。它既不是任务路由表，也不是 Python 运行模块；填写模板不产生批准，代码参考也不替代实际实现。

| 子目录 | 具体用途与消费者 |
|---|---|
| [policies/](policies/) | Master/各流程读取交互、授权、证据、隔离和恢复规则 |
| [schemas/](schemas/) | request、authorization、input manifest、physics contract、evidence ledger 的机器结构 |
| [templates/](templates/) | onboarding、phase、auto 及 scope/input/Phase 0/report 的可填写模板 |
| [references/](references/) | [runtime API](references/runtime-api-map.md)、[物理模块](references/physics-module-map.md)、[测试](references/test-map.md)与阶段代码定位 |

## 规则由哪个文件拥有

| 责任 / 原审计章节 | 权威文件 |
|---|---|
| 活动实验交互 / 1 | [interaction](policies/interaction.md) |
| 科学决策、机器/人工门槛和证据 / 2、3、5、6 | [evidence-and-approval](policies/evidence-and-approval.md) |
| 写入授权与日志 / 4、4.1、12 | [write-authorization](policies/write-authorization.md) |
| 范围、冻结和逐步明确输入 / 7、8、10 | [scientific-integrity](policies/scientific-integrity.md) |
| 实验/dataset 目录身份 / 8.1 | [dataset-layout](policies/dataset-layout.md) |
| 备份/归档隔离 / 9 | [archive-isolation](policies/archive-isolation.md) |
| revision、恢复、指纹和失效 / 11 | [progress-continuity](policies/progress-continuity.md) |
| 隔离自动运行 / 原 4.2 | [automation](policies/automation.md) |

## 管理与新增文件

共享规则只修改对应 policy，AGENTS/Skill 通过链接引用，避免复制另一套正文。新增机器记录结构放 schemas，使用现有 JSON Schema 2020-12/YAML 1.2 JSON 子集，并更新实际消费者与结构验证。

新增空白表单按用途放 `templates/onboarding/`、`templates/phase/` 或 `templates/auto/`；某 dataset 已填写的记录应进入它自己的获准目录，不写回通用模板。代码参考放 references，标明真实路径和函数，由 `audit_references.py` 核对。

修改后检查引用、schema、阶段映射和受影响流程；使用项目 [工作流 README](../README.md) 的结构检查命令。政策变动不能把已有历史授权扩大为新任务授权。

---

[上一级](../README.md) · [项目总览](../../README.md)
