# CsI-time：9PE×11时间箱：当前处理方式

版本：**r2 / SM 20261107；NSI 20261108**；analysis_id：`CsI2021_time_9x11`。

本文件区别当前分析的处理方式，并链接它实际读取的输入和结果。

| 层次 | 本分析采用的处理 |
|---|---|
| 源与靶 | SNS解析DAR能谱×ROOT时间边缘；14.6 kg等化学计量Cs/I，sin²θW=.23857。 |
| 观测与响应 | QF→光产额→Gamma→PE效率，再施加时间权重；99箱，events/bin；0–6μs参考窗注量为主口径。 |
| 统计与能力 | SM为未拟合353.465608686事例；NSI为24点前向对照，不是参数区间或原生二维likelihood。 |
| 本地依赖 | examples/COHERENT_CsI/time_resolved_common内的两份原样时间模块和纯NSI映射；24点坐标为最新已声明输入。 当前99箱数值资源位于data/experiments/.../CsI2021/time_resolved，与来源证据按SHA核对。 |
| 分支区别 | 全支撑注量329.016422597只是另一注量解释；默认注册CsI2021旧一维九箱不能替代本时间分析。 |

## 文件与运行入口

- [Onboarding/物理说明](<experiment.physics.md>)
- [当前输入](<../../../../../data/experiments/COHERENT_CsI/CsI2021/time_resolved/analysis_inputs.npz>)
- [复算/验证入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py>)
- [来源/证据](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml>)
- [SM报告](<SM_BENCHMARK.md>)
- [NSI报告](<NSI_BENCHMARK.md>)
- [观测叠加](<../../../../../outputs/csi2021_time_sm_data_comparison_20261109/README.md>)

## 当前范围与限制

- BRN/NIN绝对归一与严格论文模型等价仍未闭合。
- 旧图/原始C、扣背景诊断与纯信号分别解释；本地化依赖不改变统计含义。

[返回最新实验总入口](<../../../LATEST_EXPERIMENTS.md>)

<!-- timing-diagnostics-20261117:start -->

## 2026-11-17 可选νμ时间诊断

默认0ns、reference_window及raw背景保持；+75ns仅为对照。信号/BRN/NIN同步平移，观测效率、时间箱、零位移分母及SSB固定。新图按v4主题保留error bar、无斜线阴影。

[结果、逐箱CSV和限制](<../../../../../outputs/csi2021_timing_diagnostics_20261117/README.md>) · [复算与绘图入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) · [onboarding补充源](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/timing_diagnostics_records.py>)。

<!-- timing-diagnostics-20261117:end -->

<!-- response-mainline-20261117:start -->

## 2026-11-17 RESPONSE主线继续计算

主线完整RESPONSE重新积分，并新增8通道有符号拆分与逐层闭合检查。默认0ns/reference_window/raw保持；+75ns及prior_posteff为明确标注的独立诊断。

[结果、图与逐箱表](<../../../../../outputs/csi2021_response_mainline_20261117/README.md>) · [独立主线入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_response_mainline.py>) · [通道拆分](<../../../../../examples/COHERENT_CsI/time_resolved_sm/response_decomposition.py>) · [绘图器](<../../../../../examples/COHERENT_CsI/time_resolved_sm/plot_response_mainline.py>) · [说明生成器](<../../../../../examples/COHERENT_CsI/time_resolved_sm/summarize_response_mainline.py>)。

本次0ns信号353.465609事件；M以外合计0.019523518事件。新入口不导入KN计算代码；未改变共享振幅、核表或默认Runtime注册。

<!-- response-mainline-20261117:end -->
