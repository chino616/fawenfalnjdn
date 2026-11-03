---
name: cevns-detector-response
description: Define P06 detector observation operators, separating conditional response densities from accepted bin probabilities and verifying selection ownership and axes.
---

# P06 — 探测器观测算子

遵循 [阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
用 [P06 表单](../../../../_shared/templates/phase/P06_DETECTOR_RESPONSE_TEMPLATE.md)
按探测器/运行期填写；实现以 [代码参考](../../../../_shared/references/phase/P06_DETECTOR_RESPONSE_CODE_REFERENCE.md) 为准。

## 目标与前置条件

输入 P01 的观测量/分箱、P02 的探测器身份及相关源分量标签。
把真实反冲映射为重建观测；核 Response 属 P04，不属于本阶段。
输出不含通量、截面、实际核数或曝光。P06 可以在自身输入就绪时分析，不依赖 P05 数值结果。

## 1. 先选择输出表示

明确实际输出：
- conditional_density：R(x|T)，单位为 x 的倒数，按声明完整域归一化。
- bin_probability：P_b(T)，无量纲；若互斥分析箱含效率/选择或窗外损失，总和至多为 1。
- migration_matrix：明确是离散条件概率还是已乘积分权重的算子，记录轴方向、单位、损失和归一化规则。
- deterministic：理想映射或无展宽的确定性模型；给出依据与边界处理，不要求虚构正宽度。

不得把上述对象统一强制归一化为 1。外部矩阵若已包含效率/接受率，必须标记；
不能再次相乘，也不能在分析窗口内重归一化抹掉损失。

## 2. 确认物理和选择归属

逐项给出来源定位与 official/digitized/approximate 属性：
yield/quenching、均值映射、分辨率、效率自变量、阈值类型、
分析窗口和各个 selection 的作用位置。阈值不自动等于阶跃效率。
展示近似及其对目标的影响，需要新的决定时取得 `APPROVE DETECTOR CONTRACT`。

每个探测器/配置期分别说明；合成有效探测器需要明确权重和近似。
多维观测或不同分箱聚合先核对实际 executor 能力，不能只因 Binning 能表达就宣称支持。

## 3. 实现最小接口

优先实现/复用 ObservationModel.bin_probabilities；
如保留 sampled_density 路线，显式注明数值策略。
现有 BinProbabilities.values 使用 (n_true, *binning.shape)，
外部 R[reco,true] 必须显式转换并测试，不能靠矩阵维度相等猜方向。
included_selections 和归一化台账共同说明哪些因子已应用。
可以对响应密度作 bin 积分来生成概率，这不是积分最终事件数。

## 4. 验证并交接

按表示检验：映射有效域；非零展宽模型的正宽度；密度全域积分或概率行和；
效率 [0,1]；阈值与插值边界；相邻 bin 闭合；尾部/窗外迁移；标量/数组轴。
保存有用的映射图、响应切片、效率或矩阵诊断，注明有限积分域遗漏的尾部。

handoff：
`representation`、`unit`、`normalization`、`included_selections`、
`axes`、`response_definition`、`selection_ownership`、`validity_domain`。
P06 PASS 与用户结果接受后交回 Master；P07 直接消费已声明的算子，只补尚未应用的因子。
