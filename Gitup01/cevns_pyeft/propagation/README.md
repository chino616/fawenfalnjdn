# propagation：把传播结果适配成入射味密度矩阵

本目录提供传播边界，当前三个内置 COHERENT 实验使用 SNS 固定纯味态，不会自动调用这里的 SNuDD 后端。

| 文件 | 输入与输出 |
|---|---|
| [base.py](base.py) | `PropagationState` 保存 `energy_GeV`、`rho[N_E,3,3]`、nu/antinu 标签；检查味顺序、Hermitian、正半定和迹 |
| [density.py](density.py) | `propagation_state_from_density` 验证外部密度；`wilson_np_to_vector_nsi` 仅把 NP-only 的 C6u1/C6d1 映射为传播 NSI |
| [backends/snudd.py](backends/snudd.py) | 将外部 SNuDD 的传播输出接到本项目的状态合同 |

## 为什么独立

传播计算决定入射态，散射计算决定该态与靶核的相互作用；这里不应返回目标材料事件率或探测器计数。NSI 匹配拒绝 SM+NP 总系数，是为了避免外部物质势中的 SM 项重复加入。

## 管理与新增文件

新外部传播适配器放 `backends/<后端名>.py`，实现 `DensityMatrixBackend.density`，返回本项目的 `PropagationState`；通用校验放 `density.py`。第三方依赖应由实际使用该后端的入口明确处理，避免导入基础包即要求所有后端可用。

随后需要源的 `state_provider` 在实际能量网格调用适配器，转换 GeV/MeV 坐标并返回 `IncidentStateBatch`；仅增加 backend 文件不会改变实验预测。检查能量索引、味顺序、态参数依赖和密度矩阵合法性，参考 [test_source_state_p2.py](../../tests/test_source_state_p2.py)。能量依赖 rho 不满足当前组合式 Fast 的固定态条件；适配器存在也不意味着 Solar B8 数据集已经接入。

---

[上一级](../README.md) · [项目总览](../../README.md)
