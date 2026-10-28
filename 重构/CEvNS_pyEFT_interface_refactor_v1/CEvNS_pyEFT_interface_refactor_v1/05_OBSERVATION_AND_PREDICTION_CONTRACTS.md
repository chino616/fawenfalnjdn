# 观测模型、分箱与预测输出

状态：DESIGN。关联：[主链](06_PIPELINE_AND_ASSEMBLY.md) · [接口审阅](09_MODULE_INTERFACE_REVIEW.md)。

## 1. 观测模型组合

`ObservationModel` 组合 detector response、efficiency 和 selection；每个有独立模型标识与参数。
初版可将它们实现为少量函数/数据类，不要求每个标量都成为一个类。

对一维、可分离选择：

\[
B_{sA,i}(T)=a_s\int_{x_i}^{x_{i+1}}dx\,P_A(x|T)\epsilon(x).
\]

`P(x|T)` 是全域归一化的条件概率密度，`epsilon` 是重建量上的检测效率，`a_s` 是 legacy 中独立声明的分量选择。
离散观测使用概率质量和求和。已有经验迁移矩阵可以直接给出入箱概率，不必强行逆推出均值/密度。

## 2. 公开概率接口

```python
# DESIGN：标准的一维响应能力。
observation.bin_probabilities(
    target=target,
    recoil_keV=T_grid,
    binning=binning,
    component_id=component.component_id,
)
# BinProbabilities.values.shape == (n_T, *binning.shape)
```

`BinProbabilities` 保存实际反冲网格、观测轴、概率值、已包含的选择记录与模型身份。
不含源强、运行时间、核数、dT 权重。多个互斥 bins 的概率总和应在数值容差内属于 [0,1]；分析窗口外不要求补到 1。
旧分量接受率作为 `LegacyComponentAcceptance` 实例传入；未知 component_id 报错，不默认套 0.848。
标准观测接口不依赖理论 Wilson 系数。

当选择真实依赖 E、T、t 或源分量，只有在已声明的数学条件下才可以压缩成 B(T)。不能用常数接受率代替尚未实现的联合选择。

## 3. 概率矩阵与加权矩阵

离散数值式为：

\[
N_{sA,i}=n_A\sum_r w_r^{(T)}Y_{sA}(T_r)B_{sA,i}(T_r).
\]

`B.values` 无量纲；`T_quadrature.weights` 为 keV。
若预先生成 `WeightedFold.values = weights[:,None] * B.values`，这个对象单位为 keV，并明确反冲轴和构建依赖。
禁止在 B 中先乘 dT，再由 fold 重复乘一次。

## 4. 保留现有 CsI2021 数值语义

当前算法先在 `pe_eval_grid` 算 dN/dPE，再插值到每箱子网格、乘效率并积分。
直接改成在每个反冲处先积分连续 P(x|T) 的概率矩阵，连续数学上等价，但有限网格结果不保证相同。

首版提供显式的 `legacy_csi2021_v1` 数值策略：

1. 沿用现有反冲、入射能、PE 节点以及箱内子网格。
2. 对每个源/靶先求 Y(T)，然后用同样的 T 求积生成各 PE 节点的 g(x_k)。
3. 保留旧程序在该阶段施加的 `if_positive` 行为及其顺序。
4. 用相同线性插值、效率与梯形积分得到每箱贡献。
5. 通过回归后，才讨论删除无效截断、替换求积或转为预计算线性矩阵。

在截断未激活时，可构造保持同一离散插值的有效 B：对 PE 线性插值基函数 L_k 使用相同箱内积分，令

\[
B_i(T_r)=\sum_k P(x_k|T_r)\,Q_i[\epsilon(x)L_k(x)].
\]

其中 Q_i 是旧箱内求积。若 `if_positive` 实际改变中间值，则这条线性重排并不等价，必须保留执行顺序并报告发生点。
`LegacyPEFold` 属于数值执行后端，不伪装成新的物理效率模型。

## 5. Axis 与 Binning

`Axis` 保存 `name`、`unit`、`edges`、可选 `clock` 和离散/连续定义。
`Binning.axes` 是有序元组；`shape` 由每条轴的箱数生成，不独立手填。

一维：`axes=(PE_axis,)`，shape `(9,)`。
二维：`axes=(PE_axis,reco_time_axis)`，shape `(9,11)`，前提是真实数据确实使用相应边界。
边界严格递增、有限；不同轴不能重名。时间轴必须标记 reconstructed/source、相对脉冲/绝对运行时间。
9×11 只是目标结构示例；本包没有提供经过核验的 11 个时间箱。

## 6. Prediction

建议最少包含：

| 字段 | 定义 |
|---|---|
| `counts` | 总预期事例数，shape 等于 Binning.shape，单位 events/bin |
| `axes` | 与数组顺序一致的 Axis 元组 |
| `components` | `(source_id,isotope_id)` → 实际最终贡献数组 |
| `normalization_record` | 源归一化、核数、选择责任的解析结果 |
| `model_record` | 组件、参数、资源与版本指纹 |
| `numerical_record` | 实际网格、求积、容差、后端 |
| `diagnostics` | 可选的每核 Y(T)、选择前计数、legacy 兼容诊断 |

各核素反冲网格可以不同，使用独立 `RecoilYield` 对象，不为了堆叠而隐式插值。
组件数组与总和验证后才产生最终 Prediction。暴露 `counts_per_npe` 等密度是显式转换操作，不是主存储格式。
多 detector/run 扩展时使用额外标识或明确命名轴，不能把它们平均后隐藏差异。

## 7. 统计适配

沿用现有 `PredictionVector/StatisticalObservable` 的一维兼容能力；增加一个明确的 `to_statistical_vector` 适配器。
对于二维对象，记录 `(PE,time)` 轴顺序、每条轴边界和展平索引。C 顺序时 `flat_index = pe_index*n_time + time_index`，其逆映射必须测试。
预测、观测、背景和协方差使用相同映射。99 元素向量不能与旧 9 箱数组比较。
9 箱减背景 excess 不能反推真实 99 箱观测，也不能直接当 Poisson 原始计数。
仅改统计数据或误差时，不重建物理预测或 Fast 核；对不一致的 observable 明确拒绝。

当前统计定义保持 `legacy approximate statistics` 标识。官方二维 likelihood 的接入需真实数据和系统误差定义，不能由结构升级自动得到。
