# 当前非8B实验与2601.19883复现状态

更新于2026-11-13。本对话继续处理CsI-time、CsI2017、Ar2020与CONUS+。**8B由另一条正在运行的对话按continuous_acceptance（连续效率曲线）完善，不属于本轮后续计算范围。**

当前结论：四条主线的文件已集中到Gitup01，已有SM及部分NSI结果；联合最小值漏搜缺陷已修复，Fast在声明范围内通过数值对照；论文Fig.4的精确复现仍未成立。本轮更新状态与导航、回读已有文件，没有新增物理计算或重跑测试。[核对证据与变更清单](../../outputs/reproduction_status_20261113/README.md)。

## 四条主线：版本、实际结果与缺口

| 主线 | 当前处理方式与已执行结果 | 待补齐事项 | 当前文件入口 |
|---|---|---|---|
| CsI-time | r2；9PE×11时间箱，99箱SM总数353.465608686 events；NSI已有24点前向对照。0–6 μs参考窗注量为主口径，全支撑注量解释的329.016422597单独保留。 | BRN/NIN绝对归一及严格统计模型尚未闭合；24个前向点不能当作拟合区间或二维likelihood。 | [onboarding](COHERENT/CsI2021/time_resolved/experiment.physics.md)；[方法](COHERENT/CsI2021/time_resolved/METHODS.md)；[SM报告](COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md)；[NSI报告](COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md)；[观测叠加](../../outputs/csi2021_time_sm_data_comparison_20261109/README.md) |
| CsI2017 | Package v2兼容分支；25PE箱，PE=1.17T、251节点及4.9 PE效率阈值；指定n_enu=12回归网格的SM为167.558550049 events。单28%归一化pull近似Gaussian，保留有符号residual。 | 当前是指定网格核对，没有默认网格收敛声明；Physics MD与Renderer不同步、兼容observation_schema.json缺失。科学接受仍为DRAFT/NOT_REVIEWED。 | [onboarding](../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md)；[方法](COHERENT/CsI2017/METHODS.md)；[SM结果](../../outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json) |
| Ar2020 | Package v2兼容分支；12箱、观测值决定宽度的Gaussian，均值(0.246+0.00078T)T、σ(x)=0.58√x；非对称误差、有界信号/背景pull 0.12/0.146。指定n_er=11、n_enu=40、n_pe_bin=8回归网格的SM为136.632223203 events。 | 效率坐标在Package标为PE，而来源为官方keVee列，单位冲突待核对；Physics MD与Renderer不同步。指定网格结果不等于收敛或论文复现。 | [onboarding](../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md)；[方法](COHERENT/Ar2020/METHODS.md)；[SM结果](../../outputs/COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json) |
| CONUS+ | 数据集为conusplus_kkl_run1；onboarding v3 / Response benchmark v1。19×10 eVee箱，160–350 eVee，1 kg×119 days；Lindhard k=0.162、真电离能Gaussian与Nuclear Response；SM为149.419399803 events，NSI六个实数u/d矢量坐标与二维比较已有结果。 | 论文使用KN核形状因子；本地Response与选定Flux不同。高能谱形差异、原始Kopeikin数表和核表上游认证仍未闭合；PARTIAL/NOT_REVIEWED保持。 | [onboarding](CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md)；[方法](CONUS_Plus/datasets/conusplus_kkl_run1/METHODS.md)；[SM结果](../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json)；[NSI报告](CONUS_Plus/datasets/conusplus_kkl_run1/benchmarks/nsi_response_20261106/NSI_BENCHMARK.md) |

CsI2017与CsI2021/time的响应和观测身份不同。论文Fig.4的COHERENT计算采用CsI2021一维九箱＋Ar2020，不是上述99箱CsI-time，也没有自动追加CsI2017。以下联合χ²不应与这些SM总事例数混作同一统计分析。

## 联合最小值：已修复的缺陷与方法区别

已确认的数值问题是原始(u,d)坐标中狭长谷漏搜极小值：扩大搜索框后重复找到同一局部值，不能证明已找到全域最低点。当前采用事例数二次型条件化、有限改进域、多种子和确定性多起点搜索。

| CsI2021一维＋Ar方案 | SM χ² | 二维χ²min | 用途 |
|---|---:|---:|---|
| 平均Ar上下误差 | 13.8694704671 | 12.5656899995 | 与旧计算同目标函数的修正对照 |
| 当前非对称Ar | 13.6896107483 | 12.1289641562 | 本地当前统计模型；作者实现等价未确认 |
| 共享10% SNS通量 | 13.944333902 | 12.565176160 | 相关性敏感性，不作为已知作者协方差 |

旧平均误差χ²min为13.4142259378，故旧表面Δχ²少算0.84853593825。修复搜索后仍保留Ar误差方案差别，不能将模型变化误当作同一次优化修复。[联合复核与逐项证据](../../outputs/paper2601_joint_audit_20261111/README.md)；[修复后同平均误差benchmark](../../outputs/paper2601_chi2_corrected_20261111/README.md)。

独立pull相加已用21箱同时增广最小二乘核对，最大χ²差5.68×10⁻¹⁴。非对称Ar求解器与现有有界Runtime逐点差约6.68×10⁻¹⁰。这些结果验证数值求解，不证明作者输入及误差模型等价。二维Δχ²须减去同一联合目标函数自己的最小值。

## Fig.4仍有哪些差异

在εee^uV=0截线，COHERENT蓝色二维90% CL区域使用Δχ²=4.61，有以下四个交点：

| εee^dV边界 | 第1条 | 第2条 | 第3条 | 第4条 |
|---|---:|---:|---:|---:|
| 论文PDF矢量图形 | −0.094340 | 0.108619 | 0.230654 | 0.437070 |
| 当前非对称Ar计算 | −0.077132 | 0.106309 | 0.243107 | 0.429752 |

中间空隙约比论文宽12.10%。外边界接近不足以证明整条二维带一致。原图数值只具PDF图形精度，详见[截线原始边界](../../outputs/paper2601_joint_audit_20261111/SLICE_BOUNDARIES.json)及[原图与修正结果并排/局部放大](../../outputs/paper2601_fig4_redraw_20261112/README.md)。

CONUS+当前基准SM χ²为7.36649327636，二维χ²min为7.31794198709；u/d轴序及单pull极小化已核对，与论文二维轮廓仍有差异。其SM总数比数字化参考152.092946830低约1.76%，但最高能箱的相对差约−54.78%（绝对差−0.429885663 events），总量接近不代表谱形已复现。[逐箱与来源限制](../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json)。

论文Fig.4分别展示各实验组区域，没有可供核对的全实验堆加轮廓。CsI2021一维与99箱时间分析使用同批观测，不能重复当独立数据；CsI2017也需核实曝光重叠后才能讨论再合并。

## Fast检查覆盖到哪里

[专项Fast审计](../../outputs/paper2601_fast_audit_20261111/README.md)对CsI2021、Ar2020、CONUS+共33个同网格原生Slow/Fast点逐箱、逐源和逐核素比较，包含远处联合最小值、干涉抵消及复数味耦合：

| 已执行核对 | 最大差异或结果 |
|---|---:|
| 原生Slow与Fast逐箱 | 1.0379608284×10⁻¹⁰ events |
| 最终网格扫描多项式与fresh Fast逐箱 | 1.16060050459×10⁻¹⁰ events |
| 既有Fast合同回归 | 38项通过 |
| 联合搜索数值回归 | 2项通过 |

原生Slow直接对照在small/medium网格执行；最终高分辨网格另核对tensor、多项式和缓存身份，没有完整最终网格原生Slow执行结论。此范围也不等同于已审计CsI2017和99箱CsI-time的所有Fast能力。

旧CONUS fine缓存未通过当前依赖身份检查；审计改用新编译核，旧/新H归一差约4.24×10⁻¹⁶，未替换生产缓存。本次重新核对上述审计7份源码指纹，全部匹配；回读原XML确认38＋2项记录，没有本轮新跑测试。[原验收文件](../../outputs/paper2601_fast_audit_20261111/FINAL_CHECKS.json)。

## 后续完善顺序

1. **CsI-time**：补齐BRN/NIN绝对归一、观测/背景及nuisance约定后，再讨论原生时间likelihood与NSI区间；保持与一维数据的统计身份分离。
2. **Ar及COHERENT联合**：首先核实效率坐标的PE/keVee来源、作者上下误差用法和CsI/Ar相关性，再按明确方案重算轮廓；现有平均误差、非对称与共享通量结果分别保存。
3. **CONUS+**：沿用conusplus_kkl_run1的本地入口，对照作者逐箱数值与核/Flux选择，优先追踪高能尾差异；不同物理处理需另存分支，不覆盖现有结果。
4. **CsI2017**：核对Physics MD与Renderer字段对应及缺失的观测schema，再增加有依据的积分收敛证据，保留现有25箱兼容结果。

目前部分CsI/Ar正式YAML及NPZ存在OS拒绝读取问题，本轮没有改权限或把完整回归记为通过。上述缺口是具体物理输入、来源对应或已执行检查的限制；目录整理、链接通过和Fast数值一致不能替代这些证据。

## 文件归属与本轮变更

说明与方法归docs/experiments，实际输入归data，复算入口归examples，数值与图归outputs，来源/合同归workflows的相应记录。CONUS+采用Gitup01内的显式本地资源，历史原运行保留，不以外部自动运行目录作为当前计算入口。

本页由[实验README](README.md)负责；[最新五条主线基线](LATEST_EXPERIMENTS.md)、[文件夹构造](LATEST_FOLDER_LAYOUT.md)与[outputs导航](../../outputs/README.md)同步链接。本轮保存既有导航修改前备份、新状态页、数值回读、链接检查及导航差异，具体文件对应见[FILE_LIFECYCLE.json](../../outputs/reproduction_status_20261113/FILE_LIFECYCLE.json)。8B的连续效率改进由独立对话继续，本页不安排其后续计算。

[返回实验目录](README.md) · [本轮核对证据](../../outputs/reproduction_status_20261113/README.md)
