# 实验 Catalog 与兼容层

Status: CURRENT
Scope: 当前内置清单和加载状态的工程事实。

[manifest.py](../../cevns_pyeft/experiments/manifest.py) 是内置实验身份的唯一清单；当前只有 CsI2021、CsI2017、Ar2020，均声明 Slow、Fast、statistics 能力。实际后端边界仍受各自定义约束。
[catalog.py](../../cevns_pyeft/experiments/catalog.py) 管理 active、archived、spec_only 状态和别名。当前内置 archived/spec_only 列表为空；CONUS 是外部历史归档，不虚构为可加载条目。

[registry.py](../../cevns_pyeft/experiments/registry.py) 保留旧 callable 兼容视图，并从 Catalog 获取活动状态；不是第二套实验身份权威。
ExperimentCatalog(builtins=False) 支持显式自定义定义。[synthetic 示例](../../examples/experiment_modularization/synthetic_dataset.py) 不注册为真实实验。

存在实验 YAML、研究资料或传播适配器不代表完成 Runtime 接入。新实验的科学范围和授权仍由既有工作流处理。
