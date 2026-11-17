# CsI2017：25PE箱确定性映射：当前处理方式

版本：**Package v2 / legacy compatibility**；analysis_id：`CsI2017_legacy_SM`。

本文件区别当前分析的处理方式，并链接它实际读取的输入和结果。

| 层次 | 本分析采用的处理 |
|---|---|
| 源与靶 | 已物化SNS运行期积分注量，不重复乘POT或活时间；14.6 kg Cs/I。 |
| 观测与响应 | PE=1.17T，固定251节点、4.9 PE效率阈值；不使用CsI2021 Gamma/时间响应。 |
| 统计与能力 | 单28%归一化pull的近似Gaussian，保留有符号residual。 |
| 核结构 | YAML/NPZ中的本地核响应快照，兼容现有Li2026实现。 |
| 最新核对口径 | 本次已运行的回归网格：n_enu=12；167.558550049事例。 不是默认网格收敛声明。 |

## 文件与运行入口

- [Onboarding/物理说明](<../../../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md>)
- [当前输入](<../../../../data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml>)
- [复算/验证入口](<../../../../examples/experiment_modularization/run_experiments.py>)
- [来源/证据](<../../../../data/experiments/COHERENT_CsI/CsI2017/README.md>)
- [最新核对结果](<../../../../outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json>)

## 当前范围与限制

- DRAFT/NOT_REVIEWED；官方likelihood与科学发布未通过。
- 现有Physics MD与Renderer不同步，迁移不以改写数组或放松阈值消除该问题。
- 兼容observation_schema.json仍缺失，不猜测补造。

[返回最新实验总入口](<../../LATEST_EXPERIMENTS.md>)
