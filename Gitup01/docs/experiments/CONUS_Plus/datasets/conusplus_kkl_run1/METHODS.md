# CONUS+：SM / 矢量NSI Response：当前处理方式

版本：**onboarding v3 / Response benchmark v1**；analysis_id：`conusplus_kkl_run1_response`。

本文件区别当前分析的处理方式，并链接它实际读取的输入和结果。

| 层次 | 本分析采用的处理 |
|---|---|
| 源与靶 | 反应堆ν̄e；用户选定非负Flux、天然Ge五同位素；1 kg、119 days、160–350 eVee。 |
| 观测与响应 | 19×10 eVee箱；Lindhard k=.162＋真电离能Gaussian，ROI损失保留；Nuclear Response，非论文KN等价。 |
| 统计与能力 | SM：未拟合前向149.419399803事例；NSI：六个实数u/d矢量坐标，误差均值、Gaussian .169归一化pull的近似区间/二维比较。 |
| 方法分目录 | sm_response与nsi_response各自代码、基准data、结果、文档和阶段记录；共享唯一SM装配。 |
| 本地化与缓存 | 代码使用Gitup01显式输入；原运行源码归入一份压缩证据。新源身份需在新输出目录重编译核，不将旧缓存误作当前缓存。 |

## 文件与运行入口

- [Onboarding/物理说明](<experiment.physics.md>)
- [当前输入](<../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>)
- [复算/验证入口](<../../../../../examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py>)
- [来源/证据](<../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P00_SOURCE_REGISTER.yaml>)
- [SM报告](<benchmarks/sm_response_20261106/SM_BENCHMARK.md>)
- [SM结果](<../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json>)
- [NSI报告](<benchmarks/nsi_response_20261106/NSI_BENCHMARK.md>)
- [NSI区间](<../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_intervals.csv>)

## 当前范围与限制

- 原始科学来源PARTIAL，人工接受NOT_REVIEWED；目录集中不自动成为默认活动Runtime dataset。
- Kopeikin原始数表与核响应上游认证未闭合；SM高能谱形与文献仍有差异。
- 当前主项目原onboarding生成器的既有实施指纹问题单独保留。

[返回最新实验总入口](<../../../LATEST_EXPERIMENTS.md>)
