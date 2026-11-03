# P08 当前 Fast 后端与缓存

配合 [P08 模板](../../templates/phase/P08_FAST_COUNTS_TEMPLATE.md)。
数学表示、实现后端和文件格式分别记录。

| 路线 | 当前入口与限制 |
|---|---|
| 统一实验编译 | `cevns_pyeft/experiments/runtime.py::compile_experiment` 交给实际 executor |
| CsI2021 interface | `cevns_pyeft/kernels/compiler.py::fast_capability`；`cevns_pyeft/kernels/compiler.py::compile_fast` |
| interface 重建 | `cevns_pyeft/kernels/compiler.py::CompiledKernel.predict` |
| interface 存储 | `cevns_pyeft/kernels/interface_storage.py::save_compiled_kernel`；`cevns_pyeft/kernels/interface_storage.py::load_compiled_kernel` |
| 实际编译依赖 | `cevns_pyeft/kernels/fingerprint.py::dependency_record` |
| CsI2017/Ar2020 legacy | `cevns_pyeft/experiments/coherent/execution.py::LegacyExecutor.compile`；保留专用 builder，拒绝任意替换组件 |

源码：[compiler](../../../../cevns_pyeft/kernels/compiler.py)、
[storage](../../../../cevns_pyeft/kernels/interface_storage.py)、
[实际实验装配](../../../../cevns_pyeft/experiments/coherent/execution.py)。

interface_kernel_v1 要求可用的 operator_bilinear_v1、单观测轴、固定且不依赖扫描参数的态、
以及相应 observation 能力。_prepare 还实际核对取样能量上的态和声明是否相符。
full kernel 的轴为 (target,source,channel,basis_i,basis_j,bin)，重建保留复数干涉。
限定 basis_keys 是声明子空间；求值不得带入编译基底外非零系数。

编译固定 source/run、target、observation、数值设置和相关实现；
常量 rho 的复用规则以该后端实际取值/校验为准，不能与一般 rho(E) 混淆。
统计观测和误差不属于此物理核依赖。旧 fast_kernel_csi2021 / kernels.builder 仍存在，
但不是当前 CsI2021 统一入口的 interface 编译路线。

## 只读能力查询

从项目根目录执行。supported=True 只说明接口前提，不能作为 P08 数值 Gate。

```python
from pathlib import Path
from cevns_pyeft.contracts.parameters import IntegrationSettings
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.kernels.compiler import fast_capability

experiment = load_experiment("CsI2021", resources=ResourceCatalog(Path.cwd()))
numerics = IntegrationSettings.legacy_csi2021_v1(n_er=3, n_enu=6, n_pe_bin=3)
capability = fast_capability(experiment.model, numerics=numerics)
print(capability.supported, capability.reasons)
assert capability.supported
```

正式构建使用 compile_experiment(experiment, numerics=批准设置)，
随后 predict_experiment(..., backend="fast", kernel=kernel, numerics=同一设置)。
构建和比较必须处于已批准 P07 范围；小网格查询不替代冻结。
验证依据：[Fast 合同与失效测试](../../../../tests/test_fast_model_contract.py)；
还需目标自己的逐箱、多参数和性能报告。
