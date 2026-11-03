# refactor：CsI2021 组合式 Slow 重构的历史输出

[task_card.json](task_card.json) 记录 R0–R3 工作范围：保留 CsI2021 九箱计数、旧 raw/API 与统计语义，同时引入显式组件和通用预测链。

| 内容 | 对应代码或验证目的 |
|---|---|
| [resolved_model.json](resolved_model.json)、[replacement_cards.json](replacement_cards.json) | 当时实际装配与组件替换说明，对应 `core/model.py`、源/靶材/响应接口 |
| [regression_comparison.json](regression_comparison.json)、`r*_*.xml`、`final_pytest.xml` | 旧计数与新流程的比较、各阶段测试结果 |
| [changes.json](changes.json)、[review.diff](review.diff)、[checkpoint.json](checkpoint.json) | 当时文件变更、补丁与进度 |
| [original/](original/) | 修改前原件快照，包含旧 src 布局；不是当前运行包 |
| [check_parallel_fast.py](check_parallel_fast.py)、相关 JSON | 当时的辅助诊断；先检查其路径/依赖再考虑执行 |

## 为什么保留在 outputs

这些内容用于解释重构经过。当前公式与入口以 [运行时包](../../cevns_pyeft/README.md)为准，冻结测试以 [tests/reference](../../tests/reference/README.md) 为准，不能从本目录导入旧实现替代现行代码。

## 管理与新增文件

不要在 `original/` 修改或新增活动源码，不把旧 task card 的授权当成新任务权限。新一轮重构在独立输出目录保存自己的基线、测试命令、差异和 receipt；对本次历史结果的补充说明应与原证据分开，并注明引用的文件/版本。旧一次性工具不是通用构建入口，现行工具从根 `tools/` 查找。

---

[上一级](../README.md) · [项目总览](../../README.md)
