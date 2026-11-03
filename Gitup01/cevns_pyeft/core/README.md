# core：把已经装配好的组件连成计算

[model.py](model.py) 的 `ExperimentModel` 持有 source、run、targets、interaction、observation、binning。[predict.py](predict.py) 使用这些对象执行通用一维预测，不负责寻找实验数据文件。

## 实际执行顺序

`predict(model, parameters=..., numerics=...)` 先调用 `validate_compatibility`，核对过程、轴、单位和能力，然后：

1. `model.source.for_run(model.run)` 得到含曝光的注量。
2. 按核素和源分量调用 `rates.recoil.integrate_recoil_yield`，得到每核反冲产额。
3. 选择 `legacy_density_fold` 或 `probability_fold`，施加响应、效率和选择。
4. 乘该核素的 `number_of_nuclei`，按分量求和，返回 `Prediction` 和诊断记录。

显式 Fast 走 `kernels.compiler`；`auto` 有编译核时用 Fast，否则用 Slow。CsI2021 的 executor 会进入此路径；CsI2017/Ar2020 的专用折叠不由本函数替代。

| 其他文件 | 用途 |
|---|---|
| [interaction_point.py](interaction_point.py) | `evaluate_li2026_point` 计算单个能量/反冲点；输入 GeV 与 keV，输出 cm²/keV，不含源、核数和探测器 |
| [mass_time.py](mass_time.py) | `MassTimeModel` 描述每秒通量、每 kg 核数和质量时间曝光，是独立的归一化约定 |
| [engine.py](engine.py) | 保留历史导入名并对旧实验调用施加生命周期检查 |

## 为什么独立，怎样增加文件

本层管理“先后顺序与组件协调”；积分公式归 `rates/`，实验参数和具体执行策略归 `experiments/`。新增可复用的模型/协调器可在这里创建模块，并声明其消费的合同和输出对象；仅某个实验需要的分支应放该实验 executor。

接入新协调器要修改调用它的 executor；创建模块不会替换现有 `predict`。旧导入兼容由 `engine.py` 管理，不应在那里复制新公式。改动后检查 [接口测试](../../tests/test_interface_contracts.py)、[单点合同](../../tests/test_physics_core_step1.py)及[冻结回归](../../tests/test_refactor_csi2021_regression.py)，特别是曝光、选择和核数各应用一次。

---

[上一级](../README.md) · [项目总览](../../README.md)
