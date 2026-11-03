# cevns_pyeft：实际被导入的运行时包

这里保存计算实现。用户入口是 `experiments.loader.load_experiment` 和 `experiments.runtime`；根 [__init__.py](__init__.py) 仅导出版本，[cli.py](cli.py) 仅打印版本。包内的研究 Notebook 不是初始化步骤。

## 运行时职责分工

| 子目录 | 真实对象或函数 | 输入 → 输出 |
|---|---|---|
| [experiments](experiments/README.md) | `load_experiment`、`predict_experiment`、`evaluate_experiment` | dataset ID、资源、参数 → 装配实例、预测、统计评价 |
| [contracts](contracts/README.md) | `TheoryPoint`、`DetectorFluence`、`Prediction` 等 | 定义并校验跨模块传递的数据形状、单位和语义 |
| [core](core/README.md) | `ExperimentModel`、`predict` | 已装配组件 → 通用一维预测 |
| [sources](sources/README.md) | `SNSLegacySource.for_run` | 源设置和曝光 → 探测器位置的积分注量、谱线、入射态 |
| [targets](targets/README.md) | `inventory_from_mass_fractions` | 探测器质量与组成 → 各核素真实核数 |
| [theory](theory/README.md) | Li2026 匹配、粒子响应、截面；Helm 实现 | Wilson 系数和运动学 → 相互作用核/截面 |
| [nuclear](nuclear/README.md) | `ResponseDB`、`ResponseW` | 核响应 JSON → 给定动量处的核响应矩阵 |
| [rates](rates/README.md) | `integrate_recoil_yield`、折叠函数 | 注量和截面 → 反冲产额、观测箱积分 |
| [detectors](detectors/README.md) | 响应、效率和选择对象 | 真实反冲 → 观测概率或响应密度 |
| [kernels](kernels/README.md) | `compile_fast`、`CompiledKernel.predict` | 固定物理装配 → 预积分核 → 多个理论点的计数 |
| [statistics](statistics/README.md) | observable 转换、profiling、scans | 预测和观测 → χ²、扫描与区间 |
| [propagation](propagation/README.md) | `PropagationState`、SNuDD 适配 | 外部传播计算 → 味密度矩阵；不自动接入内置实验 |
| [foundation](foundation/README.md) | 常量、单位、资源路径与有限别名 | 被上述模块共享的基础定义 |

具体装配由 [coherent/execution.py](experiments/coherent/execution.py) 完成。CsI2021 走 `core.predict.predict`；CsI2017/Ar2020 走各自专用执行器。`sources/sns.py` 和旧探测器效率适配仍依赖 COHERENT 实现，不能把这份目录拆分理解为所有具体实验依赖都已消除。

## 为什么这样拆分

实验定义回答“这次计算用哪一组输入”，公共模块回答“这一类量怎样计算”。例如更换 CsI2021 的曝光进入 definition/run，更换响应对象进入 observation，修改所有实验共享的 R 多项式则进入 theory。三者的数值影响和需要重建的缓存不同，因而分开维护。

## 管理与新增文件

先按上表定位责任，再在相应目录创建 Python 模块；新子包需要 `__init__.py`。通过现有调用方显式导入或装配新对象，需要包级公共接口时才补相应导出。不要只创建文件就假设 runtime 会自动发现它。

新增实验使用 `experiments/` 的 custom catalog 路径；新增理论、源或响应实现相应合同后，通过 `load_experiment(..., components=...)` 或新的 definition 接入。数据表放项目外置 `data/`，测试放根 `tests/`，运行产物放 `outputs/`。公共物理行为变化需检查已有实验回归和 Fast 失效规则。

---

[上一级](../README.md)
