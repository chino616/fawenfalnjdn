# experiment_modularization：统一实验入口的历史验收结果

本目录记录 `load_experiment/predict_experiment/evaluate_experiment` 模块化及资源/组件身份检查，不是加载实验所需的数据目录。

| 文件或子目录 | 如何阅读 |
|---|---|
| [final_receipt.json](final_receipt.json)、[test_summary.json](test_summary.json) | 当时任务的范围、结果和环境/产物定位 |
| [baseline_comparison.json](baseline_comparison.json)、[unified_fast_comparison.json](unified_fast_comparison.json) | 旧结果比较与统一 Fast 的比较证据 |
| `*pytest.xml`、`acceptance_*.xml`、`identity_final.xml` | 各次测试执行记录，按文件所对应阶段解释 |
| [m0/](m0/) | 起始基线数组及描述 |
| [protected_tests_check.json](protected_tests_check.json)、[review_commit_comparison.json](review_commit_comparison.json) | 参考/测试保护与当时版本比较 |

## 与代码的关系

现行实现见 [experiments](../../cevns_pyeft/experiments/README.md)，行为检查见 [test_experiment_modularization.py](../../tests/test_experiment_modularization.py)。报告里保存的旧绝对路径、构建位置和通过项数属于当时环境，不证明当前 checkout 已运行相同验证。

## 管理与新增文件

这些文件是历史输出，先通过 receipt/manifest 找到生成范围再解释单个数组。新的模块化任务应创建新的 `outputs/<运行标识>/`，运行相应测试并生成自己的报告，不覆写本目录的基线或旧 PASS 记录。

若需要补充对旧报告的解释，单独保存注明日期和依据的说明并链接原文件；不要直接修改原 XML/JSON 的结果。真正的实现改动放 `cevns_pyeft/`，可执行回归放 `tests/`。

---

[上一级](../README.md) · [项目总览](../../README.md)
