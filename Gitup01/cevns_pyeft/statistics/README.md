# statistics：把预测与指定观测进行比较

事件数预测完成后，`experiments.runtime.evaluate_experiment` 核对实验、物理身份和观测轴，再调用 definition 中绑定的 evaluator。COHERENT 的实际绑定在 [statistics_binding.py](../experiments/coherent/statistics_binding.py)，随后进入本目录的 profiling 函数。

| 文件 | 实际用途 |
|---|---|
| [observables.py](observables.py)、[adapters.py](adapters.py) | 校验轴/箱边界并转换预测单位；CsI2021 的 events/bin 转 counts/PE 只除一次箱宽 |
| [datasets.py](datasets.py)、[tables.py](tables.py) | 统计数据对象、旧入口与 CsI2017 外表的坐标/schema 绑定 |
| [profiling.py](profiling.py)、[likelihoods.py](likelihoods.py) | Gaussian one/two-pull、Ar2020 非对称 IRLS 等实际 χ²/profile 实现 |
| [parameters.py](parameters.py)、[scans.py](scans.py)、[confidence.py](confidence.py) | 扫描参数构造、网格扫描、Δχ² 和区间提取 |
| [predictors.py](predictors.py) | 从旧实验 Slow/Fast 返回结构构建统计向量的兼容入口 |

## 为什么不放进物理预测器

`load_experiment` 跳过 role 为 statistics 的资源，因此缺观测表仍可做物理预测。更换误差或背景应改变统计评价，不应重建纯物理 Fast 核。当前三个实验的统计是明确标记的近似模型，不能直接宣称复现了实验完整官方 likelihood。

## 管理与新增文件

可复用的新似然或 nuisance 求解方法放本目录；某实验选择哪种方法、用哪些观测和误差，由自己的 `StatisticsDefinition` 与 evaluator 绑定。外部观测放 `data/experiments/<实验族>/<dataset_id>/statistics/` 并声明 role、单位、坐标和来源。

新增 evaluator 必须实际把 `Prediction` 转换成该观测的向量，并保留身份/轴验证。仅增加函数不会被 `evaluate_experiment` 自动调用。统计组合也需显式定义，`predict_selection` 不自动相加不同实验的 χ²。检查单位转换一次、同长度不同边界被拒绝、统计变化不使物理核失效，参考 [test_experiment_modularization.py](../../tests/test_experiment_modularization.py)。

## 统计入口与dataset生命周期

旧数据常量按需从已安装definition读取，包级导出排除未安装数据集的常量；具体load/evaluate入口仍先核对Catalog状态。某项物理卸载后，其他实验的统计模块仍可导入和评价。归档/卸载同步当前活动资源清单，保留该实验资源声明用于恢复。

---

[上一级](../README.md) · [项目总览](../../README.md)
