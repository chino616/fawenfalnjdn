# experiments：实验身份、装配与统一运行入口

本目录回答“给定 dataset ID，到底运行哪套模型、用哪些数据”。内置活动 ID 的唯一清单是 [manifest.py](manifest.py)，目前为 CsI2021、CsI2017、Ar2020。

## 从 ID 到结果

| 文件 | 实际运行责任 |
|---|---|
| [catalog.py](catalog.py) | `ExperimentCatalog` 解析 ID/别名，延迟导入 definition，拒绝 archived/spec_only 的运行 |
| [definition.py](definition.py) | `ExperimentDefinition` 绑定物理设置、资源、观测轴、统计、数值配置和 `prepare` |
| [loader.py](loader.py) | `ResourceCatalog` 解析路径；`load_experiment` 调用 `prepare`，应用组件覆盖、快照与指纹，返回 `PreparedExperiment`；统计文件延迟读取 |
| [assembly.py](assembly.py) | 记录实际组件与执行器身份，防止只改实例却沿用旧缓存身份 |
| [runtime.py](runtime.py) | `predict_experiment`、`compile_experiment`、`evaluate_experiment`、`predict_selection`；校验数值键、输出轴与身份 |
| [selection.py](selection.py) | 严格读取本次运行选择；禁用项不解析资源或执行预测，各实验结果分别返回 |
| [coherent/](coherent/) | 三份 `*_definition.py` 与 `execution.py`；CsI2021 绑定通用 `core.predict`，另外两者绑定 legacy executor |
| [specs.py](specs.py)、[registry.py](registry.py)、[base.py](base.py) | 外置说明 YAML 读取、旧 API 分派与效率等兼容实现；不是第二份活动清单 |

这种分工让“哪个实验可运行”“实验用什么输入”“算法如何执行”分别有明确入口。例如改变观测误差只影响评价，改变物理响应会使对应物理身份和缓存失效。

## 新建一个实验实现

真实新数据集先从[Master 工作流](../../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)确定物理范围和数据证据。获得对应范围的实现授权后：

1. 在 `cevns_pyeft/experiments/<实验族>/` 建立定义与执行模块。现有 COHERENT 用 `<dataset>_definition.py`；一个独立小包也可用 `definition.py`、`execution.py`。
2. 定义 `ExperimentDefinition`，给出唯一 ID、观测轴、资源 role、合法数值键及 `prepare(definition, resources)`。`prepare` 返回模型和 callable executor。
3. executor 接收 `(experiment, point, backend, numerics, kernel)`，返回 `(combined_prediction, detector_predictions, raw_result, execution_record)`；总数、分量、轴必须满足 `runtime.py` 的检查。
4. 数据放入根 `data/experiments/<实验族>/<dataset_id>/`，经 `ResourceRef` 显式绑定；测试放 `tests/test_<模块名>_contract.py`。声明 Fast 或统计能力前实现对应 compiler/evaluator。
5. 先用 `ExperimentCatalog(builtins=False).register(...)` 运行隔离实例。正式激活时只在 `manifest.py` 增加活动 entry，字符串模块路径相对于本包，最终导出 `DEFINITION`。

可参考 [synthetic_dataset.py](../../examples/experiment_modularization/synthetic_dataset.py)。[scaffold_experiment.py](../../tools/scaffold_experiment.py) 能创建 definition/execution、资源与能力说明及合同测试，但生成的是演示骨架，不会更新 manifest，也不产生真实物理模型。

已知实验的默认参数在自己的 definition 维护；单次变化使用 `dataclasses.replace` 或 `components` 覆盖。不要另建活动 ID 列表或用 `experiment.yaml` 的存在代替注册。相关检查见 [test_experiment_modularization.py](../../tests/test_experiment_modularization.py) 和 [test_runtime_migration_contracts.py](../../tests/test_runtime_migration_contracts.py)。

---

[上一级](../README.md) · [项目总览](../../README.md)
