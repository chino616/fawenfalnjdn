# PandaX4T — PandaX4T_2024_US2 — Physics Summary

状态：DRAFT / 见能力记录；人工科学审核 NOT_REVIEWED。

2026-11-07 SM benchmark输入包，DRAFT/PARTIAL；每个输入附直接来源，旧onboarding保留。

[详细实现说明](experiment.physics.md) 包含完整实验公式、符号、参数、分箱、逐 bin 数据和数值约定。

## 关键实验输入

| 输入 | 当前值 | 单位 |
| --- | --- | --- |

| 探测器组件 | 本次选择 |
| --- | --- |
| 真实反冲接受度诊断 | `recoil_efficiency_projection_v1` |

## 共享模块选择

| 独立维度 | 已登记 model ID | 绑定状态 |
| --- | --- | --- |
| Nuclear Structure | `klein_nystrand_v1` | BOUND_UNVERIFIED |
| Interaction / 组合接口 | `coherent_sm_kn_v1` | BOUND_UNVERIFIED |

Interaction 与 Nuclear Structure 分开选择；表中的状态是已有记录，不代表本次重新运行或科学接受。

## Observable / Statistics

观测量：efficiency-weighted true nuclear recoil spectrum；27 箱，范围 0.299999999496–2.9999999995 keVnr。完整边界见详细版第 6 节。

统计选择：未提供。数据单位：未声明。

## 主要限制

- response_precision：US2电子数响应缺失；真实反冲诊断不替代完整目标

完整限制、来源与能力记录见[详细版第 10 节](experiment.physics.md#section-10)。
