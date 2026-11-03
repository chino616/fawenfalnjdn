# detectors：从真实反冲到可观测量

本目录提供响应、效率和选择对象。实际数值求积在 [rates/folding.py](../rates/folding.py) 或 COHERENT 专用执行器完成；探测器对象负责提供折叠所需的物理输入。

| 文件 | 谁在使用，具体做什么 |
|---|---|
| [csi2021.py](csi2021.py) | `assemble_csi2021` 装配 `CsIGammaResponse`、`CsI2021Efficiency`、`CsI2021Observation`；提供 PE 密度或箱概率 |
| [selection.py](selection.py) | `LegacyComponentAcceptance` 提供各源分量的接受率，在折叠路径中施加一次 |
| [coherent.py](coherent.py) | `TabulatedEfficiency` 读取外部效率表；`DeterministicPEObservation` 和 `ObservedGaussianObservation` 保存 CsI2017/Ar2020 专用折叠参数 |

CsI2021 的 Slow 保留“响应积分 → 非负截断 → PE 插值 → 效率 → 箱内积分 → 分量选择”的顺序。CsI2017 是确定性 PE 映射；Ar2020 的 sigma 依赖观测值。三个对象并不具备完全相同的通用概率接口。

## 为什么独立

效率、能量分辨率和接受率改变的是探测到的事件，不应改写 `theory/` 的截面或 `sources/` 的注量。响应独立后，同一反冲谱可以比较不同探测器模型，也能明确何时需要重建 Fast 核。

## 管理与新增文件

新的通用响应实现放本目录独立模块，数据表放 `data/experiments/<实验族>/<dataset_id>/detector/`，具体默认参数放实验 definition。按照 [observation 合同](../contracts/observation.py) 声明轴、单位、密度/箱概率能力及 `describe()`。

在实验 `prepare` 中装配，或通过 `load_experiment(..., components={"observation": ...})` 替换；仅新增类不会改变计算。若对象依赖新的折叠算法，还需在对应 executor 明确接入。检查概率范围、箱闭合、效率和接受率只施加一次；现有例子见 [test_component_replacement.py](../../tests/test_component_replacement.py)。新响应不能自动承诺 legacy Fast 可用。

## 与dataset安装状态分离的默认响应

[legacy_parameters.py](legacy_parameters.py)集中保存原有CsI淬火、Gamma、效率、PE边界与分量接受率默认值；具体definition引用这些公共默认值，也可在已批准范围内显式装配其他参数。公共响应不再为了获得默认数值导入CsI2021的专用definition，卸载该dataset时保留这项共享能力。

---

[上一级](../README.md) · [项目总览](../../README.md)
