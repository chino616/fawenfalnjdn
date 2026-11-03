# contracts：模块之间传什么，先在这里约定

本目录定义数据对象、Protocol 和验证规则，供实验装配、Slow/Fast、统计桥共同使用。例如 [core/predict.py](../core/predict.py) 接受 `TheoryPoint` 与 `IntegrationSettings`，源返回 `DetectorFluence`，最后构造 `Prediction`。

| 文件 | 被运行路径消费的约定 |
|---|---|
| [parameters.py](parameters.py) | `TheoryPoint` 保存 Wilson 矩阵、SM 开关和弱混合角；`StateParameters` 保存态参数；`IntegrationSettings` 保存求积设置 |
| [source.py](source.py) | 区分 POT、秒通量、已积分注量；定义连续谱、谱线、能量支撑和入射态批次 |
| [target.py](target.py) | `TargetIsotope`/`TargetInventory` 保存核质量、组成及真实核数 |
| [interaction.py](interaction.py) | `InteractionModel.dsigma_dT` 的输入与 `DifferentialCrossSection` 输出 |
| [observation.py](observation.py) | `Axis`、`Binning` 和无量纲 `BinProbabilities`；检查观测坐标与概率 |
| [prediction.py](prediction.py) | 每核反冲产额 `RecoilYield`、单位为 events/bin 的 `Prediction`；分量之和必须等于总数 |
| [modules.py](modules.py)、[validation.py](validation.py) | 描述符、能力错误、快照和通用数值检查 |

## 为什么独立

同一个“长度为 9 的数组”可能是 events/bin，也可能是 counts/PE；同一通量也可能已经包含曝光。这里用对象和验证明确区别，让 `core`、`rates`、`kernels` 不必各自猜测单位。冻结输入还防止调用方事后修改数组造成装配身份失真。

## 管理与新增文件

跨模块共享的新语义放在相应合同文件；只有出现新的独立边界时才新建合同模块。写明轴顺序、单位、归一化、合法范围、复制/冻结行为，并实现构造时验证。纯算法、实验默认数值和数据读取不放这里。

若需 `from cevns_pyeft.contracts import ...`，同时维护 [__init__.py](__init__.py) 的导入和 `__all__`。新合同必须由生产者实际返回、消费者实际验证；在 [test_interface_contracts.py](../../tests/test_interface_contracts.py) 一类测试中同时检查合法输入与错单位/错形状输入。

---

[上一级](../README.md) · [项目总览](../../README.md)
