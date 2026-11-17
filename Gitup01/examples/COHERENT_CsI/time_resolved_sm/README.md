# CsI2021 时间分析：旧入口已撤下

2026-11-18按用户指令移除三个并列计算入口，重新进入onboarding。此目录目前没有正式SM计数入口。

| 保留文件 | 用途 |
|---|---|
| validate_benchmark.py / summarize_benchmark.py | 历史结果校验与汇总，引用无CLI的公共支持模块；不构成本轮阶段通过 |
| plot_benchmark.py / plot_data_comparison.py / plot_response_mainline.py | 已有结果的绘图工具 |
| response_decomposition.py | 既有实现的一体流通道诊断，源论文式(75)装配尚待核查 |
| summarize_response_mainline.py | 历史RESPONSE结果说明；禁止重建旧活动导航 |

[当前onboarding](../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md) · [清理记录](<../../../../重构/20261118_CsI2021_onboarding_restart/README.md>)
