# 实验与数据集文档

[CsI2021主线全部内容查验（2026-11-15）](COHERENT/CsI2021/MAINLINE_REVIEW_20261115.md)：99箱前向与9箱统计分开；24个前向点、26条一维、16个二维面、76条涉及CsI的能标路线及完整程序/文件地址。统一样式旧表未同步Comparator等差异单列，未重算或重画。

[最新SM、参数、NSI、χ²与截断能标汇总表（2026-11-15）](RESULTS_TABLES_20261115.md)：12行SM、16条SM参数、50条NSI一维、41二维、340条χ²、224条能标、128项benchmark及70步Python路线；提供17表Excel/CSV和完整允许集，主版与控制、系数符号及科学缺口分别说明。

[截断能标独立统计Part（2026-11-14）](../../examples/cutoff_scales/README.md)：24条dim-6主路线与176条完整算符控制路线保留；新增24条三组联合（2主＋22控制）、逐算符论文比较及沿用SM视觉角色的新图。独立pull近似、固定太阳传播、LNV味结构与dim-8正定性限制分别记录；原状态快照与数值结果保持原样。

[当前主线总览（2026-11-14）](MAINLINE_STATUS_20261114.md)：各实验实际完成状态、66条一维/41个二维benchmark、方法与太阳版本区别、论文对照范围和下一阶段缺口；[当天回读与来源哈希核对](MAINLINE_STATUS_20261114.evidence.json)。

[各实验二维SM/NSI benchmark（2026-11-13）](TWO_DIMENSIONAL_BENCHMARKS_20261113.md)：同味uV/dV、原文混合味dV以及太阳弱角/通量两种定义，41个平面及逐实验论文对照；[完整数值与未完成能力](../../outputs/two_d_benchmark_20261113_run1/RESULTS.md)。

[每个实验的Python计算路线与逐步输入输出（2026-11-13）](COMPUTATION_ROUTES_20261113.md)：7条路线、P01–P10共70项，源码存在、实际可执行范围和科学接受分别记录。[完整一维SM/NSI χ²结果](../../outputs/one_d_benchmark_20261113_run1/RESULTS.md) · [代码与重跑命令](../../examples/one_d_benchmark/README.md)。

[标准模型论文图集与最新8B结果（2026-11-13）](<../../论文图NoteBook/8. SM_experiment_benchmarks/README.md>)：五条主线按方法分目录，提供PDF/SVG/PNG、参考文献、逐箱数据与图注。8B独立对话已完成交付，本轮已整合continuous_acceptance的SM值及与旧参考配置的区别；[来源与比较范围](<../../论文图NoteBook/8. SM_experiment_benchmarks/REFERENCES_AND_METHODS.md>)。

[当前非8B进展与论文复现状态（2026-11-13）](CURRENT_REPRODUCTION_STATUS.md)：CsI-time、CsI2017、Ar2020与CONUS+的实际版本、SM结果、联合搜索修复、Fast覆盖及论文差异。[本轮回读与身份核对](../../outputs/reproduction_status_20261113/README.md)。该非8B条目保留此前核对范围；8B最新已完成交付见上方论文图集。

[Fig.4原文与修正计算对照图（较早快照）](../../outputs/paper2601_fig4_redraw_20261112/README.md)：同坐标并排及COHERENT局部放大；当时绿色仅为论文参考。太阳最新实际区域见[v3.4.1结果](../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md)。

[本次Fast专项审计](../../outputs/paper2601_fast_audit_20261111/README.md)：与原生Slow独立对照，包含大耦合极小值、缓存身份及最终网格多项式，和联合最小值搜索修复分别验收。

[2601联合结果复核（2026-11-11）](../../outputs/paper2601_joint_audit_20261111/README.md)：CsI＋Ar搜索修复、CONUS二维拟合及合并范围；其中太阳未算NSI的记录已由上方最新状态更新，历史证据保留。

[2601.19883v2 卡方复算（已修复搜索）](../../outputs/paper2601_chi2_corrected_20261111/README.md)：在最新本地输入上核算论文统计公式；Ar误差方案和未闭合的论文条件另见联合复核，原错误最小值只保留为历史证据。

[当前五条实验：最新版本与处理方式](<LATEST_EXPERIMENTS.md>)。本入口仅列当前选定分析；不同方法的输入、代码、结果和审核范围分别说明。

[五条主线文件地址与结构审计（2026-11-11）](MAINLINE_FILE_LAYOUT_AUDIT_20261111.md)：全部选定目录和1325个现存文件的地址、402项快照、目录合理性与CONUS结果遗漏原因；[逐文件地址清单](../../outputs/mainline_summary_20261111/FILE_ADDRESSES_20261111.md)。

[五条主线 onboarding 与 SM 汇总（2026-11-11）](MAINLINE_ONBOARDING_SM_SUMMARY_20261111.md)：⁸B单bin、CsI-time、CsI2017、Ar2020、CONUS+的当前入口、输入口径、实际结果、本次核对和后续缺口；[数值回读记录](../../outputs/mainline_summary_20261111/README.md)。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：两种独立分析

[单bin v3.2.1：输入、来源、代码与SM结果](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md>) · [多bin v3.1（保留）](<PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。

单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；[独立数据](<../../data/benchmarks/solar_b8_singlebin_2601_19883/README.md>)、[独立入口](<../../tools/run_solar_b8_singlebin_benchmark.py>)、[独立结果](<../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>)。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## 当前太阳⁸B SM：v3.1 原子核Response

[当前新版本与两实验实际计算](<PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。核表→振幅→截面→事例数；旧KN文档/计算保留。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## 历史v3.0太阳⁸B onboarding：v3.0完整整合版（2026-11-09）

[单文件阅读PandaX与XENONnT：全部输入、来源、SM/V/B−L结果及交接](<PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。本版合并v2.0–v2.3的有效内容；旧版本保留。

<!-- solar-onboarding-v3:end -->

单实验资料按“实验 → datasets → dataset_id”归属；既有COHERENT目录保留兼容布局。每个dataset的README给出当前onboarding、历史版本、数据和流程入口。目录存在不代表实验已进入默认活动清单。

## 单实验目录

| Experiment | 简介 | Dataset |
|---|---|---|
| [COHERENT](COHERENT/README.md) | 利用 SNS 停止 π 衰变中微子源研究 CEvNS | [CsI2017](COHERENT/CsI2017/README.md)、[CsI2021](COHERENT/CsI2021/README.md)、[Ar2020](COHERENT/Ar2020/README.md) |
| [CONUS+](CONUS_Plus/README.md) | 反应堆CEvNS；逐参数出处和待补事项保存在其onboarding中 | [conusplus_kkl_run1](CONUS_Plus/datasets/conusplus_kkl_run1/README.md) |
| [PandaX-4T](PandaX4T/README.md) | 太阳⁸B US2分析；当前v3.0与历史版本分列 | [PandaX4T_2024_US2](PandaX4T/datasets/PandaX4T_2024_US2/README.md) |
| [XENONnT](XENONnT/README.md) | 太阳⁸B分析；当前v3.0与历史版本分列 | [XENONnT_2024_SolarB8](XENONnT/datasets/XENONnT_2024_SolarB8/README.md) |

新增实验或数据集时只为实际存在的身份创建目录，补充其 README，并同步所属实验、本页和相关文献链接。同一探测器的不同数据身份分别说明，不按单篇论文或 arXiv 版本建 Dataset。注册状态以[程序登记](../../cevns_pyeft/experiments/dataset_registry.json)为准，README 不执行注册或科学验证。

[文献总目录](../references/README.md) · [资料目录](../README.md)

## 联合分析目录

| 目录 | 组合对象与内容 |
|---|---|
| [PandaX4T_XENONnT_SolarB8](PandaX4T_XENONnT_SolarB8/README.md) | PandaX-4T 2024 US2 + XENONnT 2024 Solar B8；onboarding v3.0合版、共享Response来源说明及SM/V/B−L benchmark报告 |

联合目录用于跨实验共同文档；它不对应新的实验、dataset或Runtime注册。各实验独立文档与数值输入沿用原目录。当前合版和历史材料由联合目录README集中导航；后续共同报告放入该目录。

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

太阳NSI新v3.3独立于冻结SM v3.2.1与多binv3.1。

[完整新onboarding：实际输入、标准引文、物理与程序](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<../../outputs/external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

<!-- solar-snudd-v341:end -->

<!-- solar-full-rho-trace-onboarding-v35:start -->

## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5

[微分/总截面、事例数积分与三样本差别](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md>) · [明确合同与待改程序](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。

<!-- solar-full-rho-trace-onboarding-v35:end -->
