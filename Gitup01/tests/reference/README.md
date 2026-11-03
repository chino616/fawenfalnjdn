# tests/reference：修改前的数值证据

这里保存冻结数组与对应元数据，测试运行只读它们。它们用于判断重构是否保持既有行为，不是运行时自动加载的 Fast 缓存。

| 目录 | 实际消费者 |
|---|---|
| [interface_refactor_v1/](interface_refactor_v1/) | `baseline.npz` 与 `metadata.json` 被 [test_refactor_csi2021_regression.py](../test_refactor_csi2021_regression.py) 用于源/核素/箱计数、raw 语义和近似 χ² 比较 |
| [interface_kernel_v1/](interface_kernel_v1/) | `legacy_builder.npz` 与元数据被 [test_fast_model_contract.py](../test_fast_model_contract.py) 用于确认旧 builder 输出保持一致 |

## 为什么冻结在这里

如果每次从当前代码重新生成“期望值”，实现错误可能同时污染实际值和期望值。独立保存旧输入身份和数组，才能检查行为保持；历史科学限制也仍保留，不因测试通过就消失。

## 管理与新增文件

不手改现有数组、元数据和容差来消除失败。确需新增基线时，建立新的版本目录，记录生成源码/版本、输入资源哈希、参数、网格、单位、数组键及生成方法；由明确的回归测试加载新版本。

基线应在所验证改动之前或由独立可信方法产生，审查数值差异后才用于验收。已有一次性冻结脚本不一定随当前副本提供，不能假设 `tools/` 中存在重建所有旧基线的命令。新的运行缓存或探索结果放 `outputs/`，不要放入本目录。

---

[上一级](../README.md) · [项目总览](../../README.md)
