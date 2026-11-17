# Ar2020：12箱专用观测宽度Gaussian：当前处理方式

版本：**Package v2 / legacy compatibility**；analysis_id：`Ar2020_legacy_SM`。

本文件区别当前分析的处理方式，并链接它实际读取的输入和结果。

| 层次 | 本分析采用的处理 |
|---|---|
| 源与靶 | 已物化SNS运行期积分注量，不重复乘POT或活时间；24 kg Ar40。 |
| 观测与响应 | 均值(0.246+0.00078T)T；σ(x)=0.58√x依赖观测值；效率为表格。 |
| 统计与能力 | 非对称IRLS、有界信号/背景pull .12/.146。 |
| 核结构 | YAML/NPZ中的本地核响应快照，兼容现有Li2026实现。 |
| 最新核对口径 | 本次已运行的回归网格：n_er=11,n_enu=40,n_pe_bin=8；136.632223203事例。 不是默认网格收敛声明。 |

## 文件与运行入口

- [Onboarding/物理说明](<../../../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md>)
- [当前输入](<../../../../data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml>)
- [复算/验证入口](<../../../../examples/experiment_modularization/run_experiments.py>)
- [来源/证据](<../../../../data/experiments/COHERENT_Ar/Ar2020/README.md>)
- [最新核对结果](<../../../../outputs/COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json>)

## 当前范围与限制

- DRAFT/NOT_REVIEWED；官方likelihood与科学发布未通过。
- 现有Physics MD与Renderer不同步，迁移不以改写数组或放松阈值消除该问题。
- Package标为PE的效率坐标来自官方keVee列，单位冲突待科学核对。

[返回最新实验总入口](<../../LATEST_EXPERIMENTS.md>)
