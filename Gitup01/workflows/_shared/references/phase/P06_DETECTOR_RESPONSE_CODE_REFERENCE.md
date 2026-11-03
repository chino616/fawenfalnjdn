# P06 当前观测算子与选择归属

配合 [P06 模板](../../templates/phase/P06_DETECTOR_RESPONSE_TEMPLATE.md)。

| 可审计锚点 | 职责 |
|---|---|
| `cevns_pyeft/contracts/observation.py::ObservationModel` | bin_probabilities 协议 |
| `cevns_pyeft/contracts/observation.py::BinProbabilities` | (n_true, *binning.shape) 无量纲概率与 included_selections |
| `cevns_pyeft/detectors/csi2021.py::CsIGammaResponse.density` | CsI 条件密度，单位 PE^-1 |
| `cevns_pyeft/detectors/csi2021.py::efficiency_csi2021` | 当前效率定义 owner |
| `cevns_pyeft/detectors/csi2021.py::CsI2021Observation.bin_probabilities` | bin 内积分密度×效率并乘分量接受率 |
| `cevns_pyeft/rates/folding.py::probability_fold` | 每核反冲产额与 bin 概率积分 |
| `cevns_pyeft/rates/folding.py::legacy_density_fold` | 保留旧数值顺序的专用策略 |

源码：[观测合同](../../../../cevns_pyeft/contracts/observation.py)、
[CsI 观测模型](../../../../cevns_pyeft/detectors/csi2021.py)、
[folding](../../../../cevns_pyeft/rates/folding.py)。

bin_probabilities 已包含 CsI 的效率和 selection；P07 不再次应用。
legacy_density_fold 返回 selection 之前的每核结果，core.predict 随后应用 selection。
两条路线必须分别记录因子归属，不能混合执行。
旧 slow_counts_csi2021 导出的效率函数是兼容导出，其定义位于 detectors/csi2021.py。

## 只读概率示例

从项目根目录运行；只核对当前 CsI 响应对象与行和，不验证新探测器。

```python
from pathlib import Path
import numpy as np
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment

experiment = load_experiment("CsI2021", resources=ResourceCatalog(Path.cwd()))
model = experiment.model
component = model.source.for_run(model.run).components[0].component_id
probability = model.observation.bin_probabilities(
    target=model.targets.isotopes[0], recoil_keV=np.array([5.0, 10.0]),
    binning=model.binning, component_id=component,
)
assert probability.values.shape == (2, 9)
assert np.all(probability.values >= 0)
assert np.all(probability.values.sum(axis=1) <= 1 + 1e-10)
print("included selections", probability.included_selections)
```

当前 core.predict 与统一 experiment runtime 只接受一维观测；runtime 的多探测器组合
要求相同 axes/bins 并逐项求和。不同分箱、时间×能量、多通道统计需要明确的能力扩展。
相关测试：[接口合同](../../../../tests/test_interface_contracts.py)、
[组件替换](../../../../tests/test_component_replacement.py)。
