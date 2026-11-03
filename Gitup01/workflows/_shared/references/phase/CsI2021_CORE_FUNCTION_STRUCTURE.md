# CsI2021 当前结构与阶段映射

用于 Phase 0 复用分析；数字、SNS 源、Cs/I 靶和 PE 参数不是其他实验的默认值。
独立填写入口见 [阶段索引](../../templates/phase/P01_P10_PHASE_TEMPLATES.md)。

```text
Manifest / Catalog → ExperimentDefinition + ResourceCatalog
→ load_experiment → prepare → ExperimentModel + executor
→ predict_experiment
    Slow → core.predict → recoil → folding → 实际核数 → Prediction
    Fast → compile_experiment → interface compiler → CompiledKernel
→ ExperimentPrediction
→ 按目标 evaluate_experiment → 统计输入及评价记录
```

| 阶段 | 当前 owner | 实际交接 |
|---|---|---|
| P01 | definition.observation、loader/selection | 身份、观测轴和分箱 |
| P02 | targets 与 RunExposure | 实际核数、质量约定与运行归一化 |
| P03 | source.for_run 与 state_at | 连续/线谱注量及入射态 |
| P04 | Li2026 matching/amplitude、ResponseDB、interaction adapter | 理论覆盖与约定 |
| P05 | InteractionModel、ElasticKinematics、DifferentialCrossSection | 截面与运动学合同 |
| P06 | CsI2021Observation、response/efficiency/selection | 密度或已含选择的 bin probability |
| P07 | core.predict、rates.recoil、rates.folding | 直接计数、分量及诊断 |
| P08 | kernels.compiler、interface_storage、fingerprint | interface_kernel_v1 与实际依赖 |
| P09 | StatisticsDefinition、statistics_binding、evaluate_experiment | 近似 Gaussian、一次箱宽转换 |
| P10 | Manifest/Catalog/loader/runtime 及阶段报告 | 实际能力和科学证据分别验收 |

实际装配：`cevns_pyeft/experiments/coherent/execution.py::assemble_csi2021`、
`cevns_pyeft/experiments/coherent/execution.py::CsI2021Executor`。
[源码](../../../../cevns_pyeft/experiments/coherent/execution.py)是调用关系权威。

slow_counts_csi2021 是当前 predict 的旧字典包装；raw 目标分量和最终 Prediction.components
归一化不同。旧 bin_events_csi、legacy Fast builder 和 registry 仍可存在，但不能据存在性
把它们画成当前 CsI2021 统一入口的主链。CsI2017/Ar2020 保留各自 executor 与 legacy Fast。

新实验逐组件判断 REUSE/CONFIG_ONLY/ADAPTER/SHARED_EXTENSION/CORE_EXTENSION/BLOCKED：
只有物理定义、轴、单位和能力适配时才复用。当前组合式 Slow 不意味着任意多维观测可执行，
当前 Fast 不意味着支持一般 rho(E)，当前统计不意味着实现官方 likelihood。
对应细节与可运行接口示例分别见 P04–P10 的代码参考，避免在本索引重复维护公式和参数。
