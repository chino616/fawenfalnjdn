# CsI2021 SM 前向事例数执行记录

本轮按2026-11-07用户请求，用标准模型计算已整理的9×11时间分析事例数。执行validation_only路线并采用P06/P07的归一化、响应与收敛检查；没有把原九箱历史阶段、未接受的Slow冻结或外部论文likelihood升级为当前批准。

| 记录 | 用途及消费者 |
|---|---|
| [07_SM_FORWARD_BENCHMARK_REPORT.md](07_SM_FORWARD_BENCHMARK_REPORT.md) | 实际调用、逐项来源、分量计数、网格/独立轴验收、图表和未认证主张 |
| [SM_CONFIG.json](SM_CONFIG.json) | 本次纯SM点、采用值/单位/原文定位、原生SM/LEC实际数值与核表、既有时间代码路径；不另立P00来源身份 |
| [NORMALIZATION_LEDGER.json](NORMALIZATION_LEDGER.json) | 每味注量、核数、能量/时间选择的归属，参考窗与全注量两种含义，禁止重复因子 |
| [RESOURCE_AUDIT.json](RESOURCE_AUDIT.json) | 28份来源指纹、原核表未变、实际运行代码未变及审计范围 |
| [CHANGE_MANIFEST.json](CHANGE_MANIFEST.json) | 当前任务的新增/配套README维护、来源冻结与备份，不改变活动数据集注册 |
| [PROTECTION_REFRESH.json](PROTECTION_REFRESH.json) | 仅更新本轮已备份并修改的examples/README.md保护指纹；其他保护项不变 |

数值、逐箱CSV、PNG/SVG、原生对照与测试日志统一保存于[本次输出](../../../../../../../outputs/csi2021_time_sm_20261107/README.md)。后续引用主结果须同时引用该轮配置、来源与验证范围；未拟合的原始背景诊断不能作为官方归一化已复现。

[上一级](../README.md)
