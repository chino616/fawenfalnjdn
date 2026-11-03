# P09 当前统计绑定与观测映射

配合 [P09 模板](../../templates/phase/P09_STATISTICS_TEMPLATE.md)。

| 可审计锚点 | 当前职责 |
|---|---|
| `cevns_pyeft/experiments/definition.py::StatisticsDefinition` | evaluator、观测映射、统计数据/资源与状态 |
| `cevns_pyeft/experiments/runtime.py::evaluate_experiment` | 核对预测 dataset/analysis/physics 身份、轴和统计绑定 |
| `cevns_pyeft/experiments/coherent/statistics_binding.py::dataset` | 根据实验定义和资源装配统计数据 |
| `cevns_pyeft/experiments/coherent/statistics_binding.py::evaluate` | 现有 Gaussian/IRLS 路由和单位变换 |
| `cevns_pyeft/statistics/observables.py::convert_prediction_to_dataset_observable` | 旧公共观测单位转换 |
| `cevns_pyeft/statistics/profiling.py::profile_gaussian_two_pull` | 现有双 pull Gaussian 计算 |

源码：[runtime](../../../../cevns_pyeft/experiments/runtime.py)、
[统计绑定](../../../../cevns_pyeft/experiments/coherent/statistics_binding.py)。

CsI2021 的当前定义是 legacy approximate Gaussian，evaluate 将 events/bin 除一次箱宽
映射到 counts/PE。不得先手动转换后再次交给会转换的 evaluator。
CsI2017/Ar2020 有各自数据和统计模型；新实验不能仅改 ID 来复用旧 χ²。
统计资源在评价时独立记录哈希；仅更新 observed/error 不意味着重建物理 Fast。

## 只读接口示例

从项目根目录运行。人为小网格预测只用于检查身份与调用，不构成科学拟合。

```python
from pathlib import Path
import numpy as np
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

experiment = load_experiment("CsI2021", resources=ResourceCatalog(Path.cwd()))
prediction = predict_experiment(experiment, numerics={"n_er": 3, "n_enu": 6, "n_pe_bin": 3})
evaluation = evaluate_experiment(experiment, prediction)
assert np.isfinite(evaluation.chi2)
print(evaluation.record["statistics"]["status"])
```

数据 representation、processing、design 和 likelihood 分开审查。
负 excess 不能当 raw Poisson，但统计分类来自来源而不是“是否出现负数”。
是否需要 covariance 由模型和目标决定；官方复现缺必要输入时保持受阻。
当前统一内建绑定不自动实现任意联合/非分箱官方模型。
相关测试：[组件与单位变换](../../../../tests/test_component_replacement.py)、
[实验模块化](../../../../tests/test_experiment_modularization.py)。
