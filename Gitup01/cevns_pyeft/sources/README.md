# sources：给积分器提供注量与入射态

计算器调用 `source.for_run(run)` 得到 `DetectorFluence`，再查询每个分量的连续谱、离散谱线和 `state_at(energy_MeV, parameters=...)`。源对象不包含探测器质量或真实核数。

| 文件 | 现有实现 |
|---|---|
| [sns.py](sns.py) | `SNSLegacySource` 复用 `experiments/coherent/sns.py` 的谱构造；POT、距离和每 POT 产额进入注量，分成 prompt_numu、delayed_nue、delayed_numubar |
| [state.py](state.py) | `NeutrinoState`、纯味态和密度矩阵验证；粒子种类与味索引分别保存 |
| [composable.py](composable.py) | `CallableFluenceComponent`、`IntegratedFluenceSource`、`DifferentialFluxSource` 和 `ScaledSource` |

SNS 要求 `POTExposure`；每秒通量适配器要求 `LiveTimeExposure` 并乘秒数；已积分注量要求匹配的 `IntegratedRunReference`，不再追加曝光。输出连续谱单位是 cm⁻² MeV⁻¹，线权重是 cm⁻²。

## 为什么把源与传播、靶材分开

同一源可作用于不同材料，改变探测器质量不应改变注量。传播后端可以提供 rho，但源仍负责把 rho 与自己的能量、分量和粒子标签对应起来。当前 antinu 标签沿用共享散射核约定，标签本身不增加独立螺旋度计算。

## 管理与新增文件

新源实现放 `sources/<源模型>.py`，给出 `for_run`、`describe()`，每个分量声明支撑、谱线、单位和状态 provider。谱表放外部 `data/` 并由实验资源显式传入。定义 `prepare` 时装配，或用 `components={"source": new_source}` 替换实例。

若需要组合式 Fast，状态 provider 还需提供 `fixed_state_for_fast()`，且与实际网格上的状态一致；不能用虚假的固定态声明绕过检查。验证曝光换算、源缩放、谱线积分和态坐标，见 [test_interface_contracts.py](../../tests/test_interface_contracts.py) 与 [test_source_state_p2.py](../../tests/test_source_state_p2.py)。默认 SNS 谱由代码构造，当前没有直接读取 `data/datafiles/SNSflux_*.txt`。

---

[上一级](../README.md) · [项目总览](../../README.md)
