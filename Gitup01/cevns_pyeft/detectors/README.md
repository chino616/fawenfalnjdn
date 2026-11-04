# detectors：从真实反冲到可观测量

本目录提供响应、效率和选择对象。实际数值求积在 [rates/folding.py](../rates/folding.py) 或 COHERENT 专用执行器完成；探测器对象负责提供折叠所需的物理输入。

| 文件 | 谁在使用，具体做什么 |
|---|---|
| [csi2021.py](csi2021.py) | `assemble_csi2021` 装配 `CsIGammaResponse`、`CsI2021Efficiency`、`CsI2021Observation`；提供 PE 密度或箱概率 |
| [legacy_parameters.py](legacy_parameters.py) | 历史缺省值名称的延迟兼容视图；数值从 CsI2021 YAML/NPZ 读取，显式参数的算法路径不导入此模块 |
| [selection.py](selection.py) | `LegacyComponentAcceptance` 提供各源分量的接受率，在折叠路径中施加一次 |
| [coherent.py](coherent.py) | `TabulatedEfficiency` 读取外部效率表；`DeterministicPEObservation` 和 `ObservedGaussianObservation` 保存 CsI2017/Ar2020 专用折叠参数 |

CsI2021 的 Slow 保留“响应积分 → 非负截断 → PE 插值 → 效率 → 箱内积分 → 分量选择”的顺序。CsI2017 是确定性 PE 映射；Ar2020 的 sigma 依赖观测值。三个对象并不具备完全相同的通用概率接口。

## 为什么独立

效率、能量分辨率和接受率改变的是探测到的事件，不应改写 `theory/` 的截面或 `sources/` 的注量。响应独立后，同一反冲谱可以比较不同探测器模型，也能明确何时需要重建 Fast 核。

## 管理与新增文件

新的通用响应实现放本目录独立模块，数据表放 `data/experiments/<实验族>/<dataset_id>/detector/`，具体默认参数放实验 definition。按照 [observation 合同](../contracts/observation.py) 声明轴、单位、密度/箱概率能力及 `describe()`。

在实验 `prepare` 中装配，或通过 `load_experiment(..., components={"observation": ...})` 替换；仅新增类不会改变计算。若对象依赖新的折叠算法，还需在对应 executor 明确接入。检查概率范围、箱闭合、效率和接受率只施加一次；现有例子见 [test_component_replacement.py](../../tests/test_component_replacement.py)。新响应不能自动承诺 legacy Fast 可用。

## 与dataset安装状态分离的默认响应

[legacy_parameters.py](legacy_parameters.py) 是从 CsI2021 输入包读取缺省参数的兼容视图，未保存独立数值。显式传参的通用算法可独立使用；省略参数或依赖旧默认导出的消费者，仍须在卸载测试中核对其数据依赖。

---

[上一级](../README.md) · [项目总览](../../README.md)


## 输入包执行与延迟导出

[__init__.py](__init__.py) 按需导出具体探测器对象，使 Catalog 的身份查询不因模块导入而装配核响应。CsI2021 audit adapter 从 YAML 显式传入 quenching、Gamma、效率和选择；[P06 报告](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/06_DETECTOR_RESPONSE_REPORT.md) 区分密度归一化与分析窗损失。卸载兼容性需按当前版本另验，不能由延迟导出推断。
