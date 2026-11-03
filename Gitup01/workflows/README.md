# workflows：开发与实验接入的协作流程

这里管理任务路由、阶段交接、科学证据与结构 QA。Python 预测不会导入本目录，wheel 也不把它作为运行依赖；实际算法权威仍是 `cevns_pyeft/`。

## 入口和真实管理链

先读 [公共规则](AGENTS.md) 与 [项目规则](cevns-pyeft/AGENTS.md)，通过 [catalog.yaml](catalog.yaml) 定位 [Master Skill](cevns-pyeft/skills/router/cevns-experiment/SKILL.md)。它按 [router/routes.yaml](cevns-pyeft/router/routes.yaml) 识别任务意图，再进入对应 `definitions/*/WORKFLOW.md`，交接给相应 Skill。

| 位置 | 管理什么 | 谁消费 |
|---|---|---|
| `catalog.yaml` | 稳定 Skill ID 与路径 | Master/解析器与结构校验器 |
| [cevns-pyeft/](cevns-pyeft/README.md) | 路由、8 类流程定义、17 个 Skill 包和 QA | 工作流执行与管理工具 |
| [_shared/](./_shared/README.md) | 政策、记录 schema、填写模板、代码参考 | 各流程复用同一规则和合同 |
| [experiment-integration/](experiment-integration/README.md) | 原有 dataset 运行、进度和授权记录 | 历史追踪及明确恢复时的核对 |

catalog 管身份，route table 管分类，WORKFLOW 管有序交接，SKILL 管单一能力。拆开后可以检查引用、循环和缺失能力，避免几份 README 分别定义互相冲突的流程。实验名称、论文存在或文件夹出现，不自动触发新实验接入。

## 管理与新增文件

新增 Skill 放 `cevns-pyeft/skills/` 对应类别的独立目录，维护 `SKILL.md` 与 catalog；新增流程放 `definitions/<流程>/WORKFLOW.md`，维护 route table 和交接引用。一般政策放 `_shared/policies/`，模板放 `_shared/templates/`，不要复制到每个 Skill 形成多份权威。

新路由/交接同时增加 router/qa 场景，并运行下面的结构检查。普通工程和文档维护按实际授权执行，不强行进入 P01–P10 物理接入阶段；新数据集或新科学含义仍使用 Master 和已有审核门槛。自动候选运行按 automation policy 在隔离空间管理，不能自动推进正式人工审核。

```powershell
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py --resolve cevns.router.experiment
python -B workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py --repo .
python -B -m unittest discover -s tests/workflows -v
```

命令从项目根目录运行。机器消费的 catalog/routes/schema/场景使用 JSON 语法（YAML 1.2 子集），已有填写模板保留其 YAML 格式。检查通过不等于全局安装了 Skill、自然语言行为验证完成或科学批准。不要把 backup、outputs 或旧运行记录当成活动 Skill/新物理输入。

---

[上一级](../README.md)
