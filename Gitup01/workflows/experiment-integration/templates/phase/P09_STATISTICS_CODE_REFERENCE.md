# P09 统计：旧 CsI2021 代码示例与数据语义边界

配合 [P09 填写模板](P09_STATISTICS_TEMPLATE.md) 使用。本例展示当前项目如何把逐箱预测转换为统计观测量，并计算**旧程序近似 Gaussian 双 pull χ²**。它不是 COHERENT 官方 likelihood 的实现，也不是新实验统计模型的默认值。

## 1. 当前代码框架

| 层 | 文件.symbol | 输入与输出 |
| --- | --- | --- |
| 旧统计数据 | [`statistics/datasets.py`](../../../../src/cevns_pyeft/statistics/datasets.py) 的 `csi2021_dataset` | `BinnedDataset`：9 箱观测值、背景、逐箱对称误差和 pull 宽度 |
| 观测量契约 | [`statistics/observables.py`](../../../../src/cevns_pyeft/statistics/observables.py) 的 `StatisticalObservable`、`PredictionVector` | 名称、单位、bin edges 与长度必须相容 |
| 单位映射 | 同文件的 `convert_prediction_to_dataset_observable` | `events/bin → counts/PE` 时除以每箱 PE 宽度 |
| χ² 路由 | [`statistics/likelihoods.py`](../../../../src/cevns_pyeft/statistics/likelihoods.py) 的 `chi2_csi2021` | 先验证观测量，再调用 `profile_gaussian_two_pull` |
| nuisance profile | [`statistics/profiling.py`](../../../../src/cevns_pyeft/statistics/profiling.py) | 解析求解信号/背景两个 pull，返回 `ProfileResult` |

当前实现的结构可写为：

```text
s_i = 已匹配 bin 与单位的信号预测
d_i = 项目旧数据 observed；b_i = 旧背景；σ_i = 对称逐箱误差
model_i = (1+α)s_i + (1+β)b_i
χ² = Σ_i[(d_i-model_i)/σ_i]² + (α/σ_α)² + (β/σ_β)²
```

`csi2021_dataset()` 的 metadata 明确标为 `legacy approximate statistics`。最后一个观测箱为负数，说明不能直接把该数组解释为原始 Poisson 计数。是否与官方数据相同，必须由 P09 的来源审计决定。

## 2. 可运行的观测量转换与 profile 示例

在仓库根目录、已安装项目或设置 `PYTHONPATH=src` 后执行。这里用**人为设定的每箱 1 event** 作为接口演示，不是实验预测。

```python
import numpy as np

from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.observables import (
    convert_prediction_to_dataset_observable,
    observable,
    prediction_vector,
)
from cevns_pyeft.statistics.likelihoods import chi2_csi2021

dataset = csi2021_dataset()
signal_per_bin = prediction_vector(
    np.ones(dataset.n_bins),
    observable("PE signal", "events/bin", dataset.observable.bin_edges),
)
signal_per_pe = convert_prediction_to_dataset_observable(
    signal_per_bin, dataset.observable
)
profile = chi2_csi2021(signal_per_pe, dataset)

assert dataset.n_bins == 9
assert signal_per_pe.observable.unit == "counts/PE"
assert np.isfinite(profile.chi2) and profile.success
print("bins =", dataset.n_bins)
print("last observed =", dataset.observed[-1])
print("toy chi2 =", profile.chi2)
```

本次运行得到 `9` 箱、最后一箱 `-0.831`、玩具输入 `χ²=51.16748557415769`。该数值仅证明旧接口可运行；不证明任何物理参数点、论文结果或官方 likelihood。

## 3. 新实验如何复用

| 所需内容 | 可复用部分 | 何时阻断 |
| --- | --- | --- |
| bin、单位和预测长度核对 | `StatisticalObservable`、`PredictionVector`、相容性检查 | 观测量语义或 bin 对不齐 |
| 已批准的 `events/bin → counts/PE` 变换 | `convert_prediction_to_dataset_observable` | 新实验的单位不同或背景扣除定义不同 |
| Gaussian 双 pull | `profile_gaussian_two_pull` 候选 | 没有明确的误差、背景、pull 先验/相关性证据 |
| 官方 ON/OFF、Poisson、协方差模型 | 不从 `chi2_csi2021` 推断 | 官方输入/公式缺失时 P09 `BLOCKED`；只做 forward model 可 `NOT_REQUESTED` |

用户在 P09 表中提供**观测数据语义、背景、协方差、nuisance 和推断规则的来源**。AI 才能决定使用公共统计 API、写薄适配层或保持阻断；不能只替换 `dataset_id` 即复用旧 χ²。

