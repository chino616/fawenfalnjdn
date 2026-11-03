# P07 当前直接积分路径

配合 [P07 模板](../../templates/phase/P07_SLOW_COUNTS_TEMPLATE.md)。

## 真实调用链

```text
load_experiment → definition.prepare → model + executor
predict_experiment
  CsI2021 → core.predict.predict
             → rates.recoil.integrate_recoil_yield
             → legacy_density_fold 或 probability_fold
             → actual number_of_nuclei → Prediction
  CsI2017/Ar2020 → 各自 executor 与数值策略
→ ExperimentPrediction
```

| 可审计锚点 | 合同 |
|---|---|
| `cevns_pyeft/experiments/runtime.py::predict_experiment` | dataset、参数、数值设置、输出轴和探测器和校验 |
| `cevns_pyeft/core/model.py::ExperimentModel` | source/run/targets/interaction/observation/binning 装配 |
| `cevns_pyeft/core/predict.py::predict` | 当前 CsI2021 组合式积分与诊断 |
| `cevns_pyeft/rates/recoil.py::integrate_recoil_yield` | 连续注量积分和离散线谱求和，返回每核每 keV 产额 |
| `cevns_pyeft/rates/folding.py::probability_fold` | 按响应 bin 概率折叠 |
| `cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::slow_counts_csi2021` | 调用组合式 predict 的旧字典兼容视图 |

源码：[runtime](../../../../cevns_pyeft/experiments/runtime.py)、
[直接预测](../../../../cevns_pyeft/core/predict.py)、
[每核积分](../../../../cevns_pyeft/rates/recoil.py)。

当前组合式归一化为：
```text
for_run 注量 × dσ/dT → 每核 dY/dT
∫dT (dY/dT) P_bin(T) → 每核逐箱产额
× 实际核数 → events/bin
```
注量已包含运行期归一化，实际核数已包含质量和同位素权重。
线谱积分注量直接乘线能处的截面。legacy_density 路线另有明确 selection 位置，见 P06。
兼容字典的 target_flavor_counts_per_bin 使用每同位素完整探测器质量且在材料权重/接受率之前；
它不等同于 Prediction.components 的最终物理分量，不能直接求和替代 total。

## 小网格接口示例

从项目根目录执行。这是接口 smoke，不是收敛结果、冻结数组或论文复现。

```python
from pathlib import Path
import numpy as np
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment

experiment = load_experiment("CsI2021", resources=ResourceCatalog(Path.cwd()))
result = predict_experiment(experiment, numerics={"n_er": 3, "n_enu": 6, "n_pe_bin": 3})
prediction = result.combined_prediction
assert prediction.counts.shape == (9,)
assert prediction.unit == "events/bin"
assert np.allclose(prediction.counts, sum(prediction.components.values()))
print("smoke total", float(prediction.counts.sum()))
```

正式 P07 需分别加密积分维度、检查尾部和阈值、核查归一化，再冻结指定范围。
CsI2017 固定 PE 节点、Ar2020 的 observed-dependent sigma 均有专用策略，
不要把 CsI2021 的数值参数强传给它们。
相关测试：[CsI2021 回归](../../../../tests/test_refactor_csi2021_regression.py)、
[接口合同](../../../../tests/test_interface_contracts.py)。
