# CsI2021时间分析：当前数值输入

本目录是9PE×11time分析的当前数值资源，与父目录默认注册的一维九箱Package分开。analysis_inputs.npz含时间边缘、观测/背景和轴；nuclear_response_CsI.npz及其inventory保存原核表逐值切片供核对，实际核响应仍调用data/responses原表。

本次从workflow/time_resolved/data逐字节采用最新资源；该原位置保留为来源证据，当前示例读取本目录并核对与证据副本一致。更新不能只改一份数组，latest_experiments.py --check会发现资源分歧。

[处理方式](../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/METHODS.md) · [来源记录](../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md)

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| CsI-time：9PE×11时间箱 | [r2 / SM 20261107；NSI 20261108；处理方式](<../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/METHODS.md>) | [当前输入](<analysis_inputs.npz>) | [SM报告](<../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>) / [NSI报告](<../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>) / [观测叠加](<../../../../../outputs/csi2021_time_sm_data_comparison_20261109/README.md>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
