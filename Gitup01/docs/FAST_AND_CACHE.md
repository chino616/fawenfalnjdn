# 组合式 Fast 与缓存

Fast 和 Slow 消费同一个 ExperimentModel；通用编译器不识别实验名字、源分量名字、材料质量权重或 PE 专有字段。当前验证范围为 CsI2021 一维 9 箱的 Li2026 双线性系数表示，22 个活跃算符，固定且不依赖扫描参数的入射态，以及非负线性观测折叠。

```python
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.kernels import compile_fast, fast_capability
from cevns_pyeft.core.predict import predict

model = make_csi2021_model("data/responses/responses_all.json")
numerics = IntegrationSettings.legacy_csi2021_v1()
capability = fast_capability(model, numerics=numerics)
assert capability.supported, capability.reasons

kernel = compile_fast(model, numerics=numerics)
point = TheoryPoint(include_sm=True, sin2thetaW=0.2387)
result = kernel.predict(parameters=point)
same = predict(model, parameters=point, numerics=numerics,
               backend="fast", compiled=kernel)
pair = kernel.predict(parameters=point, representation="pair")
```

编译保存 `H[target,source,channel,operator_i,operator_j,observed_bin]`，已包含本运行期注量、真实核数及声明的观测选择。重建使用 `Tr(rho C_i† C_j)`，固定 rho 在核外；Wilson 值及通过 SM 系数注入的 sin²θW 不属于预积分核的依赖。它们进入每次 Prediction 的实际参数记录。子基底必须覆盖本次非零系数及所请求的 SM 算符，缺失时拒绝，不静默忽略。

相互作用须提供 `operator_bilinear_v1` 的系数求值及参数重建接口。源的状态 provider 须提供 `fixed_state_for_fast()`；编译器还核对实际能量网格和每条谱线上的状态。能量依赖 rho、扫描相关态参数、未知过程或缺失能力会抛出 UnsupportedCapabilityError。Slow 继续使用其原有更一般的状态查询。

Li2026 的响应多项式只有一个 owner：`theory/li2026/responses.py::_response_polynomials`。Slow 的味矩阵与 Fast 的算符外积在同一组公式上求值；`coefficients.py` 仅构造匹配和系数表示。新 Fast 使用与 Slow 相同的 cm² 换算。旧 builder 作为兼容实现保留历史换算，因此旧模板的极小归一化偏差仍可复现。

```python
from cevns_pyeft.kernels import save_compiled_kernel, load_compiled_kernel

save_compiled_kernel("csi_kernel.npz", kernel)
loaded = load_compiled_kernel("csi_kernel.npz", model=model)
result = loaded.predict(parameters=point)
```

独立格式 `interface_kernel_v1` 同时保存轴、依赖指纹、full/pair 数组及数组内容哈希。旧格式没有必要的物理指纹，只能经旧 loader 显式使用，不自动补默认值升级。保存/加载不使用 pickle。

内容指纹包括实际求积点上的源谱、谱线、支撑、曝光、核数、核响应数据、观测折叠、分箱、数值设置和相关实现内容；数组包含 dtype/shape 与规范字节。文件路径只作来源记录，相同内容换路径可复用，同路径改内容会失效。构造后核响应原文件改变时，须重建 interaction 快照。统计观测、背景和误差不参与纯物理核的指纹。

```python
from dataclasses import replace
from cevns_pyeft.sources.composable import ScaledSource

changed = replace(model, source=ScaledSource(model.source, 2))
# kernel.predict(model=changed) 会报告 StaleCompiledKernelError。
changed_kernel = compile_fast(changed, numerics=numerics)
changed_result = changed_kernel.predict(parameters=point)
```

`legacy_csi2021_v1` 的线性重排要求总反冲响应非负。编译器检查系数响应的正半定性；不满足时拒绝编译。带符号的单通道不被当成概率截断，原非负截断不能被随意移到每个通道。仅最终浮点舍入量级的负计数允许截到零，并记录诊断。

验证环境保持用户指定的 Conda 不变。发行检查构建 wheel，再用隔离 Python 从 wheel 导入并在项目外读取显式传入的核响应文件；不安装额外环境包。外置 `data/` 仍由调用方明确提供，不假装已经捆绑到 wheel。
