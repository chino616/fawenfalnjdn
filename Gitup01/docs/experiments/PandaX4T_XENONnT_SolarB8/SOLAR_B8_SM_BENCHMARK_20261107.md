# 太阳8B：主线SM benchmark

2026-11-07。正式输入包、标准Runtime计算和阶段记录均已进入原项目；科学声明仍为PARTIAL。

| 实验 | 最新onboarding | 实际计算/图/来源 |
|---|---|---|
| XENONnT_2024_SolarB8 | [v2.2](<../XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v2.2.md>) | [SM报告](<../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SM_BENCHMARK_REPORT.md>) |
| PandaX4T_2024_US2 | [v2.2](<../PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v2.2.md>) | [SM报告](<../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SM_BENCHMARK_REPORT.md>) |

XENONnT SM信号12.317233事件；PandaX电子数谱仍缺响应，当前真实反冲投影不替代该目标。

复算：`python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run`。
