# cevns-pyeft：项目专属任务路由与执行流程

本目录把用户请求连接到已有流程和能力包。[AGENTS.md](AGENTS.md) 规定项目治理，[START_PROMPT_GENERAL.txt](START_PROMPT_GENERAL.txt) 提供启动提示；实际入口是 catalog 中的 `cevns.router.experiment`，对应 [Master Skill](skills/router/cevns-experiment/SKILL.md)。

查看全部能力及维护要求，请打开 [Skill 库总表与增减规则](../../cevns_pyeft/SKILLS.md)。该表从 catalog 与流程 metadata 生成，包含职责、产物、调用关系和文件入口；不是独立的路由权威。

涉及输入文件时，先按[共同输入规范](../_shared/INPUT_STANDARD.md)确定检查要求、格式与实际消费者，再进入所选流程；规范适用于所有实验，填写件与数据按 dataset 隔离。

| 子目录 | 实际职责 |
|---|---|
| [router/](router/) | `routes.yaml` 是任务分类的唯一权威；`scenarios/` 保存分类输入和预期 |
| [definitions/](definitions/) | 9 类 WORKFLOW：实验接入、runtime、理论、资源、归档、能力、发布验证、仓库/README 维护和 Skill QA；规定交接及门槛 |
| [skills/](skills/) | router/onboarding/phases/engineering 中的 17 个包，各自提供单项能力 |
| [qa/](qa/README.md) | `validate_skill_pack.py` 检查目录发现、身份、路由/流程图、链接、场景及保护配置 |

P01–P10 仅属于实验接入流程；历史工程 M0–M7 不是每个任务都必须执行的顺序。普通 runtime 维护由对应流程处理，不因为出现实验名就进入物理材料 intake。

## 管理与新增文件

大幅删减、移动后的说明整理使用[仓库维护](definitions/repository-maintenance/WORKFLOW.md)：从 Git revision 或文件快照提取差异，合并所属 README/上级索引的任务，只同步明确的生成区，再检查旧路径与实际消费者。普通拼写修订仍走 documentation_only；改变 workflow 行为仍走 skill_qa。

新的任务分类修改 `router/routes.yaml`，使用已有或新定义的 workflow ID，并添加分类场景。新流程创建 `definitions/<流程名>/WORKFLOW.md`，声明 Skill 交接；新 Skill 创建相应类别目录与 `SKILL.md`，再登记上级 [catalog.yaml](../catalog.yaml)。目录发现不会自动安装或启用新 Skill。

增减、移动、停用或修改 Skill 时，同步 catalog 的中文职责/产物摘要、真实消费者及相关 README，并用 `python -B tools/update_skill_library.py --write` 更新用户总表。表格遗漏、过期或无效文件入口会使结构检查失败；删除前按总表规则迁移调用引用。

共享规则/模板放上级 `_shared/`；QA 场景放本目录 `qa/scenarios/`，运行产物写任务指定的输出位置，不能伪装成 Skill。运行记录按 Master 和 dataset-layout policy 的获准路径管理，旧 `experiment-integration/runs/` 保留其历史身份。

变更后从根目录运行 `python -B workflows/cevns-pyeft/qa/validate_skill_pack.py`，并运行 `tests/workflows`。结构 PASS 只证明这些显式规则可解析，不替代真实科学结果、代理行为评估或用户审核。

---

[上一级](../README.md) · [项目总览](../../README.md)
