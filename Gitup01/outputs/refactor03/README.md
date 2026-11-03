# refactor03：资源与接口整理的历史工程证据

本目录保存当时目录/资源/接口整理的初始状态、阶段执行和验收记录。它不提供当前 runtime 的资源根，也不声明本次副本已重新完成验收。

| 内容 | 阅读目的 |
|---|---|
| [c0/](c0/) | 初始文件清单、数值基线和 synthetic 探针；其中的假观测只用于当时测试 |
| [final_receipt.json](final_receipt.json)、[environment.json](environment.json) | 当时验收结果与执行环境 |
| [protected_files_check.json](protected_files_check.json)、[observation_provenance_check.json](observation_provenance_check.json) | 原文件与统计来源的核对 |
| [c0_comparison.json](c0_comparison.json)、`c*_*.xml`、`verified_tests.xml/log` | 阶段比较及测试日志 |
| [final_inputs.json](final_inputs.json)、[current_docs_check.json](current_docs_check.json) | 当时输入与文档检查；名称中的 current 只相对于该任务 |

## 与当前实现的关系

资源规则现在由 [ResourceCatalog](../../cevns_pyeft/experiments/loader.py) 和 [foundation/resources.py](../../cevns_pyeft/foundation/resources.py) 执行，接口检查见 [test_refactor03_contracts.py](../../tests/test_refactor03_contracts.py)。审计产物与实现分开保留，便于追溯而不制造第二个配置来源。

## 管理与新增文件

新迁移或整理任务另建 `outputs/<任务>/`，记录当次输入、代码版本、命令和验证输出。保留本目录原记录及旧路径的历史含义；不要把 `c0/probes/` 的 synthetic 数据迁到正式 `data/`，也不要覆盖旧基线使比较显示通过。补充解释写独立说明，并引用原证据文件。

---

[上一级](../README.md) · [项目总览](../../README.md)
