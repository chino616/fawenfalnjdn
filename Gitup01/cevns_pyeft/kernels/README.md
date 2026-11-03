# kernels：预积分与参数重建

Fast 把源、靶核、探测器和积分网格固定后，预先积分与 Wilson 系数无关的部分，再用系数双线性重建计数。它复用物理公式，服务于多个理论点的扫描。

## 两种现有路径

| 文件 | 实际调用关系 |
|---|---|
| [compiler.py](compiler.py) | CsI2021 executor 调用 `compile_fast(model, numerics=...)`；生成 `CompiledKernel`，其 `predict` 输出 `Prediction` |
| [fingerprint.py](fingerprint.py) | 建立内容依赖记录，包括源、核数、响应、折叠、网格和实现，检测过期核 |
| [interface_storage.py](interface_storage.py) | 保存/加载 `interface_kernel_v1` NPZ；检查内容哈希、轴、full/pair 一致性，禁用 pickle |
| [basis.py](basis.py)、[builder.py](builder.py) | 旧 Fast 的算符基与核构建；仍被 legacy 实验使用 |
| [reconstruction.py](reconstruction.py)、[storage.py](storage.py) | 旧 full/pair 模板重建、旧格式读写，以及实验实例绑定检查 |

组合式核的轴为 `target × source × channel × operator_i × operator_j × observed_bin`，重建使用 `Tr(rho C_i† C_j)`。当前编译要求一维观测、双线性系数接口和固定且不依赖扫描参数的 rho；能量依赖态不能直接使用这一 Fast。统计观测和误差不进入纯物理核指纹。

## 为什么独立

缓存有自己的适用条件、文件格式和失效规则。把它与直接积分分开，可以明确区分“同一物理模型的参数重建”和“输入已改变、需要重新编译”。旧格式缺少新格式所需的物理指纹，不能自动升级。

## 管理与新增文件

新的通用编译/重建/存储实现放这里；具体实验的参数与特殊编译入口仍由 executor 绑定。若扩展系数表示，先在 interaction 实现 `coefficient_contract`、`coefficient_dsigma`、`coefficient_values`，再更新能力检查、依赖记录和实际消费者。需要包级导出时维护 [__init__.py](__init__.py) 的延迟导出表。

核文件由 `save_compiled_kernel` 或旧格式保存函数生成，放在调用方指定的 `outputs/<运行>/`；不要手改 NPZ 或放入 `data/` 冒充输入。新格式/新依赖需检查逐分量 Fast–Slow 一致性、保存加载、过期拒绝和数组损坏，参考 [test_fast_model_contract.py](../../tests/test_fast_model_contract.py)。可运行用法见 [FAST_AND_CACHE.md](../../docs/user-guide/FAST_AND_CACHE.md)。

## 卸载与共享kernel

公共builder/reconstruction直接使用targets的化学计量组合和detectors的公共响应；专用Fast构建器只在对应dataset分支导入。公共kernel保留于核心库，专用Slow/Fast文件按[文件归属表](../experiments/DATASETS.md)管理；实现依赖指纹包含新公共参数模块，旧缓存应按现有规则重建。

---

[上一级](../README.md) · [项目总览](../../README.md)
