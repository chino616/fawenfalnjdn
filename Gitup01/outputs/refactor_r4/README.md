# refactor_r4：组合式 Fast 与缓存的历史检查

本目录记录“同一模型的 Slow/Fast、显式能力与内容缓存”的工程验证，对应现行 [kernels/compiler.py](../../cevns_pyeft/kernels/compiler.py) 和 [interface_storage.py](../../cevns_pyeft/kernels/interface_storage.py)。

| 内容 | 用途 |
|---|---|
| [task_card.json](task_card.json)、[resolved_model.json](resolved_model.json) | 当时任务目标及模型描述 |
| [fast_slow_comparison.json](fast_slow_comparison.json)、`fast_pytest.xml`、`formula_pytest.xml`、`final_pytest.xml` | 同网格重建、公式及回归结果 |
| [kernels/](kernels/) | small/medium/default 等当时编译出的核文件 |
| [legacy_builder_before.npz](legacy_builder_before.npz) | 旧 builder 的对照证据，不是任意模型均可复用的缓存 |
| [wheel_smoke.json](wheel_smoke.json)、[wheel_kernel.npz](wheel_kernel.npz) | 安装包环境的历史核检查 |
| [original/](original/)、[review.diff](review.diff) | 原件快照与当时改动；`build-temp/` 为构建中间位置 |

## 管理与新增文件

这里的核必须经过对应加载器核对 schema、物理依赖和网格才能复用；路径存在或文件名叫 default 都不够。新的 Fast 检查放新的输出目录，调用 `compile_fast` 与保存 API 生成核，再记录逐源/核素/箱的 Slow 比较和失效测试。

不要手工改 NPZ、把旧核自动升级成新格式，或通过重写旧比较报告消除差异。算法修改进入 `cevns_pyeft/kernels/`，长期回归进入 [test_fast_model_contract.py](../../tests/test_fast_model_contract.py)。历史快照不参与正常包导入。

---

[上一级](../README.md) · [项目总览](../../README.md)
