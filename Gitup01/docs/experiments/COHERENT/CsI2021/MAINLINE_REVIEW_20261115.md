# CsI2021 主线现状与查验入口

**整理日期：2026-11-15。** 本页整理当前已存资料、结果和程序；未新增物理计算、未改写旧数值或论文图、未推进科学Gate。所有统计结果仍属于approximate local-model benchmark。

[完整数值表](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/RESULT_TABLES.md>) · [P01–P10逐步Python路线](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/ROUTE_STEPS.md>) · [全部选定文件地址](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/FILE_ADDRESSES.md>) · [机器可读结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/RESULTS_EXTRACT.json>) · [回读检查](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/REVIEW_CHECKS.json>)

## 先区分四种分析身份

| 分析身份 | 观测/方法 | 已经完成 | 当前缺口 | 当前入口 |
|---|---|---|---|---|
| CsI2021_time_9x11 / r2 | 9 PE×11时间箱；未拟合前向预测 | 99箱SM、PE/时间投影、官方C/AC叠加；24个测试点＝1 SM＋23非零NSI | 原生P09、BRN/NIN绝对归一和所需不确定度未闭合；参数χ²未做 | [时间文档](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/README.md>) |
| CsI2021 / 9 PE能谱 | 注册九箱输入；当前统计采用保存核回放和Gaussian近似 | SM＋13条一维（1弱角、12 NSI）＋8个NSI二维面 | 正式YAML/NPZ本次仍被OS拒读；不是原论文完整能量–时间likelihood | [正式输入说明](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2021/README.md>) |
| COHERENT_CsI_Ar_mean_errors | CsI九箱＋Ar12箱；均误差；独立nuisance | 13条一维＋8个NSI二维面；完整域/显示窗和分离区域 | 不代表已完整重扫Ar非对称误差/共享SNS系统学的另一方法 | [一维结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1/RESULTS.md>) / [二维结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/two_d_benchmark_20261113_run1/RESULTS.md>) |
| 截断能标与三组联合 | CsI9、CsI9＋Ar；CONUS＋COHERENT＋太阳三组 | 涉及CsI共76条：52条单组/COHERENT＋24条三组联合；含主版及控制 | full22固定太阳SM态；LNV味合同和dim-8正定性限制保留 | [独立能标Part](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/cutoff_scales/README.md>) |

**样本重叠：**99箱时间与9箱能谱使用重叠CsI2021观测，不能作为独立测量相加；当前CsI＋Ar和三组能标联合只使用九箱CsI身份。CsI2017另有独立身份，未追加进这些联合。二维时间观测前向图与二维参数χ²是两种不同内容。

## SM数字及Comparator的准确含义

| 数字角色 | 数值 | 来源/解释 |
|---|---|---|
| 时间分支名义SM | 353.46560868634367 events | [20261107 RUN_SUMMARY](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_20261107/RUN_SUMMARY.json>) |
| 时间分支全支撑注量敏感性 | 329.01642259688515 events | 另一注量解释，不取代名义版本；见同一RUN_SUMMARY |
| NSI运行零NSI点 | 353.4655777716773 events | [20261108 RUN_SUMMARY](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_nsi_20261108/RUN_SUMMARY.json>)；更细网格的本运行基准 |
| 论文SM总率Comparator | 341 ±11(theory) ±42(experiment) events | 2110.07730v2，PDF/页脚p4右栏Results首段；不是作者99箱数组 |
| 论文实验拟合信号 | 306 ±20 events | 同段；由原文likelihood提取，不能替代论文SM预测 |
| 官方C原始选窗总数 | 1578 events | [原始观测叠加记录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_data_comparison_20261109/COMPARISON_RECORD.json>)；含背景，不是CEvNS净信号 |
| 九箱能谱SM | 328.384641456562 events；χ²SM=4.2367262926474165 | [一维SM_points.CsI2021](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1/RESULTS.json>)；固定sin²θW=0.2387 |
| CsI九箱＋Ar均误差SM | χ²SM=13.869470467114862 | [同一RESULTS的联合SM点](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1/RESULTS.json>) |

原始引文：D. Akimov et al. (COHERENT), *Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT*, Phys. Rev. Lett. 129, 081801 (2022), DOI 10.1103/PhysRevLett.129.081801，arXiv:2110.07730v2。[本地PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/references/COHERENT/2110.07730v2.pdf>)。

> After fitting, we observed 306 ± 20 CEvNS events, consistent with the SM prediction of 341 ± 11(theory) ± 42(experiment).

**准确定位：PDF第4页＝页脚4，右栏Results第一段。** 同页原文使用PE<60、t_rec<6 μs、归一化/形状nuisance与无先验时间起点浮动；本地选定前向运行固定零平移及0–6 μs参考窗注量。本地名义SM比论文SM中心值高12.4656086863 events，即+3.6556037203%。这是总率算术benchmark，不是逐箱复现误差、χ²或统计显著性；没有按341重归一化本地曲线。[完整逐字段文献证据与选窗说明](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>)。

## 一维、二维及能标结果目前到哪里

| 结果 | CsI九箱 | CsI九箱＋Ar均误差 | 依据 |
|---|---|---|---|
| 一维参数范围 | sin²θW；ee/μμ/eμ/eτ/μτ/ττ各uV/dV | 同左，共13条 | [26条完整区间](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/RESULT_TABLES.md>) |
| 弱角最佳值 | 0.2270576582192239 | 0.23747728217875724 | [完整精度JSON](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1/RESULTS.json>) |
| 弱角68%区间（固定通量） | [0.19804372168656834, 0.2582125409971899] | [0.21010395911484078, 0.26627226556854977] | 各自一维最小值，Δχ²=1 |
| 二维平面 | 6个同味u/d＋2个混合dV，共8面 | 同左，共8面 | [16面、32份表面/32份轮廓](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/RESULT_TABLES.md>) |
| ee二维代表全域最佳点(uV,dV) | (-7.913124455245639, 7.4662653270248045) | (-10.765544220398679, 10.024848457986412) | 完整简并点保存在原JSON；不是显示窗内极小值 |
| ee二维χ²min | 3.6745023412469116 | 12.56568999955024 | [BENCHMARK_RESULTS.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/two_d_benchmark_20261113_run1/BENCHMARK_RESULTS.json>) |
| dim-6 C6u1 Λ90 global / GeV | 365.4699583589936 | 362.7036037048799 | \|g\|=1，ee，完整允许集下确界 |
| dim-6 C6d1 Λ90 global / GeV | 383.76594136805704 | 379.9064940731772 | [全部76条/正负/SM支](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/RESULT_TABLES.md>) |

ττ在SNS无入射τ的这些坐标下完全平坦：每组有2条平坦一维、1个平坦二维面。所有不连通区间和简并点保留。GF、振荡参数、复NSI相位及任意多参数共同profile没有新扫描。一维和二维阈值分别使用1/2.71/3.84与2.30/4.61/5.99；没有coverage校准。

三组能标联合包含CONUS、CsI9、Ar及三份太阳单bin共6个底层通道，43个观测、8个独立pull；同一系数c处求和绝对χ²再共同最小化，不相加各组Δχ²。2条主版C6u1/C6d1的Λ90 global分别为376.3957132062467/392.5036802389515 GeV，另22条为控制。它不表示已生成任意SM/NSI全实验联合参数面。

## 文献benchmark：逐项能支持什么

| 参考文献及定位 | 本地主线的用途 | 目前达到的对照范围/缺口 | 证据 |
|---|---|---|---|
| 2110.07730v2，p4右栏Results首段；同页Fig.1 | 论文SM总率341及拟合信号306的来源；官方数据身份 | 有总率Comparator；作者同定义99箱SM模板与原生likelihood未对齐 | [直接引文](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>) |
| V. De Romeri et al., JHEP04(2023)035，2211.11905v2，pp12–13 Eqs.(28)–(33)，p35 Fig.18 | PE/时间统计、11时间窗及图形参考 | 原图含最佳拟合预测；本地是名义SM前向，不认证逐箱拟合复现 | [叠加记录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_data_comparison_20261109/COMPARISON_RECORD.json>) / [论文](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/references/COHERENT/2211.11905v2.pdf>) |
| 2211.11905v2，p5 Sec.2.2 Eqs.(5)–(6) | 矢量NSI定义、干涉及末态味求和 | 24个前向测试点有定义/数值检查，不是论文最佳拟合点 | [NSI基准说明](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>) |
| COHERENT, JINST17(2022)P10034，2111.02477v2，Sec.8 PDF p23/印刷p21 Eq.(8.1) | QF及2–70 keVnr拟合适用域 | 公式与采用范围见来源/合同，不据此消除核响应外部生成链缺口 | [P01逐claim证据](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P01_EVIDENCE_LEDGER.yaml>) |
| 2601.19883v2，Fig.4，90%二维COHERENT区域 | CsI9＋Ar均误差ee-u/d平面对照 | 指定原图窗口IoU=89.9366406982%；没有作者χ²网格；非时间99箱认证 | [图形比较数值](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/two_d_benchmark_20261113_run1/REFERENCE_COMPARISON.json>) |
| 2601.19883v2，PDF p22 Fig.3 | CsI＋Ar逐算符能标柱高参考 | C6u1/C6d1主版相对原图约−0.35%/−0.13%；图形数字化参考不等于作者likelihood | [逐算符比较](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/cutoff_scales/20261114_paper_comparison_run1/COMPARISON.json>) |

文献页码、原句及来源核验范围承接已存证据；本轮没有重新提取PDF或下载新材料。原PDF的字节指纹列在文件清单，来源登记明确区分直接采用与候选上游。

## 程序、数据与结果的目录结构

```text
Gitup01/
├─ docs/experiments/COHERENT/CsI2021/       总入口与本次查验文档
│  └─ time_resolved/                      r2 physics、方法、SM/NSI说明
├─ data/experiments/COHERENT_CsI/CsI2021/  九箱正式Package
│  └─ time_resolved/                      99箱分析输入
├─ workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/
│                                         来源登记、合同、官方附件、转换证据
├─ cevns_pyeft/                            共享物理、响应、积分、核、统计
├─ examples/COHERENT_CsI/time_resolved_{sm,nsi,common}/
├─ examples/{one_d_benchmark,two_d_benchmark,cutoff_scales}/
├─ outputs/csi2021_time_{sm,nsi,...}_日期/  已存时间前向结果
├─ outputs/{one_d,two_d}_benchmark_20261113_run1/
├─ outputs/cutoff_scales/20261114_*/       独立能标Part
├─ outputs/results_summary_20261115_run2/  最新综合汇总
├─ outputs/csi2021_mainline_review_20261115_run1/ 本次只读整理
└─ 论文图NoteBook/{8.,9.,10.,11.,12. ...}/ 各层论文图及样式
```

分层总体合理：输入、可运行物理、实验编排、运行结果、展示及workflow证据各有归属。查验困难主要来自“CsI2021”同时指九箱注册与99箱时间分支、后续统计为跨实验共享目录、以及图表快照没有同步。当前总入口将这些关系集中索引，不搬动源文件或重构Runtime。[20步详细输入/输出和Python函数](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/ROUTE_STEPS.md>)。

| 查验项目 | 文件夹/关键文件 |
|---|---|
| r2输入、公式、缺口 | [时间文档目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved>) / [experiment.physics.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md>) |
| 正式九箱/时间输入 | [九箱data](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2021>) / [时间data](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2021/time_resolved>) |
| 官方附件与来源链 | [sources/official](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official>) / [P00来源登记](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml>) / [P03物理合同](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P03_PHYSICS_CONTRACT.yaml>) |
| SM前向与数据叠加 | [SM结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_20261107>) / [官方观测叠加](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_data_comparison_20261109>) |
| NSI前向 | [NSI结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_nsi_20261108>) / [点定义](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_nsi_20261108/points.json>) |
| 一维/二维统计 | [一维目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1>) / [二维目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/two_d_benchmark_20261113_run1>) |
| 保存核身份 | [CsI2021_fixed_model.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/one_d_benchmark_20261113_run1/inputs/CsI2021_fixed_model.npz>) / [原始CsI核记录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/paper2601_chi2_corrected_20261111/CsI2021_kernel_record.json>) |
| dim-6/full22/三组联合 | [dim-6](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/cutoff_scales/20261114_dim6_run1>) / [full22](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/cutoff_scales/20261114_full22_control_run1>) / [三组联合](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/cutoff_scales/20261114_three_group_joint_run1>) |
| 最新总表 | [run2汇总目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/results_summary_20261115_run2>) / [17表Excel](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/results_summary_20261115_run2/CEvNS_Results_Summary_20261115.xlsx>) |

## 已有论文图：当前版本与辅助旧基准

| 内容 | 入口 | 当前状态 |
|---|---|---|
| 时间SM原图/投影 | [8号图集CsI目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/8. SM_experiment_benchmarks/02_CsI2021_time>) / [20261115修订合集](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/8. SM_experiment_benchmarks/SM_Benchmarks_Collection_20261115_comparator.pdf>) | 总表已补论文SM Comparator；投影仍为既存前向结果 |
| 统一风格版 | [9号图集CsI目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/9. SM_uniform_style/02_CsI2021_time>) / [旧数值总表](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/9. SM_uniform_style/Table_SM_Numerical_Summary.csv>) | 20261113快照仍将Comparator写成--；本轮只记录，未重画 |
| 可复用样式规范 | [STYLE_GUIDE.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/9. SM_uniform_style/STYLE_GUIDE.md>) / [publication_style.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/9. SM_uniform_style/publication_style.py>) / [STYLE.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/9. SM_uniform_style/STYLE.json>) | 180mm/STIX、配色角色、图例/线型模板仍可复用；与旧表内容版本分别判断 |
| 一维χ² | [10号图集](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/10. OneD_Chi2_Benchmarks>) / [COHERENT各味](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/10. OneD_Chi2_Benchmarks/Figure_4_NSI_COHERENT_Flavors.pdf>) | 13＋13条九箱/联合扫描对应图与逐点数据 |
| 二维χ² | [CsI九箱图](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/11. TwoD_Chi2_Benchmarks/CsI2021>) / [CsI＋Ar图](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/11. TwoD_Chi2_Benchmarks/COHERENT_CsI_Ar_mean_errors>) / [Fig.4比较](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/11. TwoD_Chi2_Benchmarks/overview/Figure_10_Paper2601_Fig4_Comparison.pdf>) | 每组8面，full/paper window分开；逐平面PDF/PNG/SVG |
| 截断能标最新配色 | [12号图集](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/12. Cutoff_Scale_Benchmarks>) / [比较与联合9图](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/12. Cutoff_Scale_Benchmarks/20261114_comparison_joint_run1>) | 当前role_style入口；原dim6/full22旧配色不是本轮配色版本 |
| 辅助R/W/K与旧探测器图 | [1. paper_figures](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/1. paper_figures>) / [5. nuclear_W_and_kernel_figures](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/5. nuclear_W_and_kernel_figures>) / [6. unified_R_W_K_figures](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/6. unified_R_W_K_figures>) / [7. csi2021_detector_figures](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/论文图NoteBook/7. csi2021_detector_figures>) | 用于程序/物理说明；不同旧网格、弱角或FV基准，不替代当前SM/χ²。部分生成器仍有旧src路径，不能称已验证重跑 |

**8号旧合集文件也需区分：**`SM_Benchmarks_Collection.pdf`因Windows拒绝覆盖而保留旧版；本轮当前引用是明确标记20261115_comparator的新合集。最新综合汇总为run2；run1和早期状态报告保留其历史范围。

## Fast与联合分析：错误修复记录的适用范围

先前联合异常的已确认问题是狭长简并方向漏搜全域极小值；现有二维使用修复后的完整域搜索。Fast正确性是另一组独立数值核验，不能用图像接近原文代替。[Fast专项审计](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/paper2601_fast_audit_20261111/README.md>)记录CsI 11个Slow/Fast点，最大逐箱差约4.419×10⁻¹¹ events，最终网格多项式/Fast约1.161×10⁻¹⁰；原生Slow直接比较在small/medium同网格执行，不能改称最终高分辨网格完整Slow验收。[联合搜索修复](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/paper2601_joint_audit_20261111/README.md>)与[修复后的原benchmark](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/paper2601_chi2_corrected_20261111/README.md>)保留独立记录。这些证据不认证99箱任意耦合Fast核，也不补齐原生P09或原文输入等价性。

## 当前需要查验的缺口与差异

| 项目 | 准确现状 | 影响/回看位置 |
|---|---|---|
| 时间P09 | 尚无闭合的原生likelihood、BRN/NIN绝对归一与所需相关/不确定度 | 99箱前向通过不代表参数约束完成；看时间METHODS、P02、P03 |
| 九箱正式文件访问 | 本次二进制只读探测仍PermissionError；没有运行loader修复 | 已有保存核结果保留；不能声称正式入口当前端到端可执行 |
| 作者模板/科学等价 | 有原文SM总率，无对齐99箱SM数组/完整原文likelihood认证 | 总率benchmark、逐箱复现、χ²验收分开 |
| 核响应直接来源 | 用户选择复用本地responses_all.json；当前内部提取/读码约定有记录 | 外部作者生成链仍未认证；候选上游材料不自动成为采用依据 |
| Ar方法 | 当前扫描均误差＋独立pull；非对称/共享通量是另一路 | 不混入当前13/8计数或称全部方法重扫 |
| 图表版本 | 9号总表/合集未同步Comparator；8号旧无日期合集仍保留 | 当前SM数值以8号修订与run2为准；样式规范仍可复用 |
| 早期图件来源 | 1号paper_figures README所指的presenting Notebook在其注明路径未找到 | 已有图/CSV可查，不能将该旧Notebook当作当前已核验可重跑入口 |
| 统计识别度与覆盖 | ττ平坦、NSI远处简并、部分不连通区间；无coverage toys | 不得只报一个显示窗或有限ττ限值 |
| 能标控制 | full22固定太阳态；e↔μ LNV；dim8正定性缺口 | 对控制数值保留控制标签；不是全部算符已接受排除 |

## 本次整理的范围与文件归属

本页归CsI2021 README；只读摘录、完整地址、源码核对与变更记录归[本次整理目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1>)的README。新增总入口并同步CsI2021、实验总目录及outputs三个当前导航；修改前按原相对路径备份并登记。未修改Runtime、data、Gate、已存科学结果或原论文图。文件存在、字节可读、旧来源指纹一致与科学接受是四项不同检查，详见[查验记录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/REVIEW_CHECKS.json>)和[文件变更/README对应](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_mainline_review_20261115_run1/FILE_LIFECYCLE.json>)。
