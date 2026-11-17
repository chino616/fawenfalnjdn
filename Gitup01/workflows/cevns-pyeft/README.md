# cevns-pyeft：项目专属任务路由与执行流程

<!-- solar-nuclear-v31:start -->

## 当前太阳⁸B SM：v3.1 原子核Response

[当前新版本与两实验实际计算](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。核表→振幅→截面→事例数；旧KN文档/计算保留。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## 历史v3.0太阳⁸B onboarding：v3.0完整整合版（2026-11-09）

[单文件阅读PandaX与XENONnT：全部输入、来源、SM/V/B−L结果及交接](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。本版合并v2.0–v2.3的有效内容；旧版本保留。

<!-- solar-onboarding-v3:end -->

本目录把用户请求连接到已有流程和能力包。[AGENTS.md](AGENTS.md) 规定项目治理，[START_PROMPT_GENERAL.txt](START_PROMPT_GENERAL.txt) 提供启动提示；实际入口是 catalog 中的 `cevns.router.experiment`，对应 [Master Skill](skills/router/cevns-experiment/SKILL.md)。

查看全部能力及维护要求，请打开 [Skill 库总表与增减规则](../../cevns_pyeft/SKILLS.md)。该表从 catalog 与流程 metadata 生成，包含职责、产物、调用关系和文件入口；不是独立的路由权威。

涉及输入文件时，先按[共同输入规范](../_shared/INPUT_STANDARD.md)确定检查要求、格式与实际消费者，再进入所选流程；规范适用于所有实验，填写件与数据按 dataset 隔离。

Onboarding 的[强制溯源闭环](../_shared/references/onboarding/data-provenance-contract.md)要求首次可读输出后说明数据/原文核验缺口并与用户交互，补充后回填 P00–P03 和重生成；终稿中每项采用数据都有具体出处或推导/决定。模板和输出规范已接入此责任，现有机器检查不自动认证原文或科学批准。

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


## 实际运行记录

[CsI2021 P04–P10](runs/COHERENT_CsI/CsI2021/README.md) 是用户明确授权的既有数据集执行审计；报告与输出按输入/实现版本记录，不属于可发现的 Skill。

Master 与 Onboarding 的前期节点为 H0 身份目标、H1 材料、H2 证据、H3 物理方案；
P00–P03 权威记录和人工摘要分开，H0–H3 优先在对话展示。
具体字段及三文件生成入口见[package 编译器入口](../../tools/compile_experiment_package.py)；
该修正不改变 P04/P05 或后续 Phase。

已合并 ReadyToMerge 的 H0–H3、P00–P03 模板及
[唯一报告规范](../_shared/references/onboarding/experiment-physics-report-contract.md)：
实验侧完整记录，Interaction / Nuclear Structure 独立选择；精简/详细两份 MD 共用原有生成链。
P04/P05 和后续阶段保留。

<!-- solar-onboarding-history:start -->

## 历史记录（v3.0时期）

[2026-11-07 SM执行记录](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_SM_BENCHMARK_20261107.md>) · [2026-11-08 V/B−L执行记录](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_VECTOR_BENCHMARK_20261108.md>)。旧实验报告与数值保留，各版本链接集中在dataset版本导航；当前SM以页首v3.1为准，旧矢量结果仍按历史版本解释。

<!-- solar-onboarding-history:end -->
