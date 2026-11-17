# statistics：把预测与指定观测进行比较

[截断能标独立Part](../../examples/cutoff_scales/README.md)位于分析层：已完成有符号LEFT推断、完整区间/能标转换、dim-6主版本和完整22算符控制版及柱状图。控制版保留固定太阳传播与dim-8正定性缺口；未注册runtime入口或改变本目录既有χ²行为。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin独立能力

[solar_singlebin.py](solar_singlebin.py)实现2601.19883v2 p20 Eq.(88)：拟合信号D/统计σ、每样本独立12% pull的Gaussian。原候选D_i/B_i不进入此模型。部分接受度积分由evaluator拒绝；统计资源lazy读取，身份/观测/物理指纹由Runtime先检查。

<!-- solar-singlebin-v321:end -->

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


## CsI2021 输入包的独立统计入口

包级 [__init__.py](__init__.py) 延迟解析旧 dataset 常量，单独导入 profiler 不加载旧实验 definition。[evaluate_package](../experiments/coherent/csi2021_package.py) 消费同一包的统计数组，events/bin 只除一次 PE 箱宽；[P09 报告](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/09_STATISTICS_REPORT.md) 记录独立正规方程与 Asimov 检查。该能力保持 legacy approximate。

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

solar_nsi.py负责三样本独立pull、联合参数最小值与二维Δχ²面，保持旧统计分支。

[完整新onboarding：实际输入、标准引文、物理与程序](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
