# CsI2021

Status: CURRENT
Scope: 当前内置活动实验的工程与资源入口；不新增物理结论。

实验默认值由 [definition](../../../../cevns_pyeft/experiments/coherent/csi2021_definition.py) 维护；外部文件位于 [data](../../../../data/experiments/COHERENT_CsI/CsI2021/)。共享核响应见 [responses_all.json](../../../../data/responses/responses_all.json)。
通过 load_experiment("CsI2021")、predict_experiment 和 evaluate_experiment 运行；资源根需包含 data。能力与专用数值策略见[能力矩阵](../../../user-guide/capability-matrix.md)，参数归属见[说明](../../../user-guide/parameter-ownership.md)。
历史分析属于 [COHERENT reviews](../reviews/)，不与当前预测默认值或最新验收混为一谈。
