# 太阳⁸B：单bin（三样本）：当前处理方式

版本：**v3.2.1 / 20261111_response_run2**；analysis_id：`solar_b8_singlebin_2601_19883`。

本文件区别当前分析的处理方式，并链接它实际读取的输入和结果。

| 层次 | 本分析采用的处理 |
|---|---|
| 源与靶 | 太阳⁸B；天然Xe的9行核数分母，实际7个有核响应的同位素；曝光分别1.20/1.04/3.51 t·yr。 |
| 观测与响应 | paired / US2 / XENONnT各一个信号总数；真反冲×Total接受度积分；不读旧多bin的Qy/Ne/cS2或其缓存。 |
| 统计与能力 | 三个拟合信号量的Gaussian，各自独立12% pull；XENONnT缺尾段用区间，joint_chi2=null。 |
| 核结构 | 本地Response→共享Li2026；不叠加KN/Helm。 |
| 分支区别 | 本入口只列单bin。既有多bin是不同观测/统计方法，仍保留原目录，不混合输入或结果。 |

## 文件与运行入口

- [Onboarding/物理说明](<SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)
- [当前输入](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)
- [复算/验证入口](<../../../../tools/run_solar_b8_singlebin_benchmark.py>)
- [来源/证据](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)
- [SM结果](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>)

## 当前范围与限制

- XENONnT约2.77–3 keVnr效率缺失；区间只描述该尾段。
- Xe124/126核表缺失，不补KN、不重归一；外部核表认证未闭合。
- 计算已完成不等于科学接受。

[返回最新实验总入口](<../../LATEST_EXPERIMENTS.md>)

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

本文件上方描述冻结SM处理。本轮NSI由新v3.3接入：每点Pee、三独立pull、明确尾假设及论文差异；不覆盖SM原结果。

[完整新onboarding：实际输入、标准引文、物理与程序](<NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
