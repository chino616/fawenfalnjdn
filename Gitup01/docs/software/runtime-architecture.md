# Runtime 架构

Status: CURRENT
Scope: 根据现有代码核对的工程接口，不宣称新的物理能力。

正式包为项目根的 [cevns_pyeft](../../cevns_pyeft/)。[loader](../../cevns_pyeft/experiments/loader.py) 通过 Catalog 取得定义和显式资源，返回 PreparedExperiment；[runtime](../../cevns_pyeft/experiments/runtime.py) 提供 predict_experiment、evaluate_experiment、predict_selection 和 compile_experiment。

ExperimentDefinition 描述实验自己的源、曝光、靶材、响应、分箱、统计输入和数值配置；ExperimentModel 组合可执行组件。公共 theory、nuclear、sources、targets、rates、detectors 和 kernels 提供实现；三个已有实验仍保留各自专用执行策略。

predict_experiment 输出每个数据集自己的 Prediction；evaluate_experiment 负责观测轴和统计转换。selection 不自动把不同实验数组或 χ² 合并。统计输入延迟加载，物理预测不因此强制需要观测表。

细节以 [用户指南](../user-guide/USAGE.md)、[组件合同](../user-guide/COMPONENTS.md)和[能力矩阵](../user-guide/capability-matrix.md)为准。workflows 不被 Runtime 导入或打包。
