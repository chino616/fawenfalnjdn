# CsI-time本地共用模块

time_profile.py、time_acceptance.py与原采用文件逐字节相同；vector_nsi.py只提取原映射的_matrix和vector_nsi_wilson，G_F、转置、符号与实对称约束不变。ORIGIN.json保存直接来源和哈希。

这些模块由SM/NSI示例读取，不导入旧目录的核或拟合；最新24点坐标在[data](../../../data/benchmarks/COHERENT_CsI/CsI2021_time/nsi_20261108/points.json)。

[最新实验入口](../../../docs/experiments/LATEST_EXPERIMENTS.md)

<!-- timing-diagnostics-20261117:start -->

## 2026-11-17 可选νμ时间诊断

默认0ns、reference_window及raw背景保持；+75ns仅为对照。信号/BRN/NIN同步平移，观测效率、时间箱、零位移分母及SSB固定。新图按v4主题保留error bar、无斜线阴影。

[结果、逐箱CSV和限制](<../../../outputs/csi2021_timing_diagnostics_20261117/README.md>) · [复算与绘图入口（已撤下）](<../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) · [onboarding补充源](<../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/timing_diagnostics_records.py>)。

新增[timing_diagnostics.py](<timing_diagnostics.py>)供native/minimal/KN诊断入口共用；原有time_profile.py、time_acceptance.py及ORIGIN.json保持原样。

<!-- timing-diagnostics-20261117:end -->


2026-11-18：新增[sm_support.py](sm_support.py)，只保留旧模型装配/IO/数值求值辅助函数，无calculate/main/CLI，供既有NSI与历史验收工具兼容。三个旧SM计算入口已撤下；本轮物理实现等待onboarding合同。
