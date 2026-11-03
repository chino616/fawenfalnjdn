# workflows：开发与实验接入的协作流程

这里管理任务路由、阶段交接、科学证据与结构 QA。Python 预测不会导入本目录，wheel 也不把它作为运行依赖；实际算法权威仍是 `cevns_pyeft/`。

**检查和整理实验输入，从[共同输入规范](_shared/INPUT_STANDARD.md)开始。** 它把文件身份、字段/单位、坐标、归一化、证据和实际消费者连接起来；所有实验按同一依据检查，各自保存输入与审核结论。

## 入口和真实管理链

完整能力索引见 [Skill 库总表与增减规则](../cevns_pyeft/SKILLS.md)：按类别/阶段列出全部登记项、中文职责、产物、调用流程和 `SKILL.md` 入口。新增或移除能力时按该页清单维护 catalog、调用方和 README，再同步生成表。

先读 [公共规则](AGENTS.md) 与 [项目规则](cevns-pyeft/AGENTS.md)，通过 [catalog.yaml](catalog.yaml) 定位 [Master Skill](cevns-pyeft/skills/router/cevns-experiment/SKILL.md)。它按 [router/routes.yaml](cevns-pyeft/router/routes.yaml) 识别任务意图，再进入对应 `definitions/*/WORKFLOW.md`，交接给相应 Skill。

| 位置 | 管理什么 | 谁消费 |
|---|---|---|
| `catalog.yaml` | 稳定 Skill ID 与路径 | Master/解析器与结构校验器 |
| [cevns-pyeft/](cevns-pyeft/README.md) | 路由、9 类流程定义、17 个 Skill 包和 QA | 工作流执行与管理工具 |
| [_shared/](./_shared/README.md) | 共同输入规范、实验输入/记录 schema、空白模板、政策和代码参考 | 使用者与各流程共用检查依据，按目标核对相应输入 |
| [experiment-integration/](experiment-integration/README.md) | 原有 dataset 运行、进度和授权记录 | 历史追踪及明确恢复时的核对 |

catalog 管身份，route table 管分类，WORKFLOW 管有序交接，SKILL 管单一能力。拆开后可以检查引用、循环和缺失能力，避免几份 README 分别定义互相冲突的流程。实验名称、论文存在或文件夹出现，不自动触发新实验接入。

## 管理与新增文件

用户可直接说“维护文件架构和 README”“大幅删减后按 Git 同步说明”或“检查维护结果”，由 Master 路由到[仓库维护流程](cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)。它提供只读影响计划、按范围同步和验收三种工作；实现入口是[readme_maintenance.py](../tools/readme_maintenance.py)。

新增、删除、移动或改名文件时，按[联动维护规则](_shared/policies/file-lifecycle.md)同步所属 README、父级入口及实际绑定，并用本次文件清单核对；不等用户另行提醒更新说明。

新增 Skill 放 `cevns-pyeft/skills/` 对应类别的独立目录，维护 `SKILL.md` 与 catalog；新增流程放 `definitions/<流程>/WORKFLOW.md`，维护 route table 和交接引用。一般政策放 `_shared/policies/`，模板放 `_shared/templates/`，不要复制到每个 Skill 形成多份权威。

Skill 表的生成数据还包括 catalog 中的 `summary_zh`、`outputs_zh` 展示摘要。执行 `python -B tools/update_skill_library.py --write` 显式同步表格；`--check` 和下方结构检查只读检查其是否过期。目录文件清单仍由 `readme_maintenance.py` 管理，不能用它覆盖 Skill 表。

新路由/交接同时增加 router/qa 场景，并运行下面的结构检查。普通工程和文档维护按实际授权执行，不强行进入 P01–P10 物理接入阶段；新数据集或新科学含义仍使用 Master 和已有审核门槛。自动候选运行按 automation policy 在隔离空间管理，不能自动推进正式人工审核。

P04–P10 的依赖和阶段结果使用 [执行合同](./_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)；
阶段报告和 schema 检查见 [QA 说明](cevns-pyeft/qa/README.md)。完整工作流测试需要其中列出的
工具依赖 jsonschema；这不会成为物理运行包的依赖。

```powershell
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py --resolve cevns.router.experiment
python -B workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py --repo .
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py --check-schemas
python -B -m unittest discover -s tests/workflows -v
```

命令从项目根目录运行。机器消费的 catalog/routes/schema/场景使用 JSON 语法（YAML 1.2 子集），已有填写模板保留其 YAML 格式。检查通过不等于全局安装了 Skill、自然语言行为验证完成或科学批准。不要把 backup、outputs 或旧运行记录当成活动 Skill/新物理输入。

---

[上一级](../README.md)

<!-- readme-inventory:start -->
**当前活动目录内容（自动维护区）**

备份、生成结果和历史/冻结证据不列入此区；用途见人工说明。

| 路径 | 类型 |
|---|---|
| [_shared/](_shared/README.md) | 目录 |
| [cevns-pyeft/](cevns-pyeft/README.md) | 目录 |
| [experiment-integration/](experiment-integration/README.md) | 目录 |
| [AGENTS.md](AGENTS.md) | 文件 |
| [catalog.yaml](catalog.yaml) | 文件 |
<!-- readme-inventory:end -->
