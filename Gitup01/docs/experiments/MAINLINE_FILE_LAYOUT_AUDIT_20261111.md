# 五条实验主线的文件地址、目录结构与遗漏原因

2026-11-11，Asia/Shanghai。**职责分层基本合理；实验到分析、运行结果的导航不够完整。CONUS+的输入与计算分别落在主项目和项目外隔离目录，入口缺少关联运行导航。上一版遗漏首先是我的检索范围和结论表述出了问题。**

完整地址已经逐文件列出：[可点击的全部文件地址清单](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/FILE_ADDRESSES_20261111.md>)；[机器清单JSON](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/FILE_INVENTORY_20261111.json>)。本次共枚举 **1325 个不同现存文件**，其中 **402 个快照文件**；另列1个已登记却缺失的文件。

范围为五条选定分析的明确目录、关联SM/NSI结果、显式外部依赖、共享引擎和参考文献。目录内文件完整递归列出，备份、安装依赖、缓存及其他未选定项目副本不遍历；排除规则和逐目录范围在JSON中明示。清单记录文件身份与位置，不把共享文件或快照认作新的dataset。

<a id="toc"></a>

## 目录

- [1. 五条线的主要入口](#entries)
- [2. 代码、统计与复算文件](#code)
- [3. 实际目录关系](#layout)
- [4. 结构是否合理](#assessment)
- [5. 为什么会漏掉](#omission)
- [6. 建议怎样整理](#recommendations)
- [7. 本轮交付与检查](#checks)

<a id="entries"></a>

## 1. 五条线的主要入口

所有表中链接都指向核对过的本机绝对路径；逐文件完整地址见总清单。

| 主线 | 阅读入口 | 输入/来源 | SM结果 |
|---|---|---|---|
| ⁸B 单 bin | [onboarding目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883>) | [独立输入目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/benchmarks/solar_b8_singlebin_2601_19883>) | [SM输出目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/solar_b8_singlebin/20261111_response_run2>) |
| CsI-time | [onboarding目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved>) | [来源/证据/分析输入](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved>) | [SM输出目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_20261107>) |
| CsI2017 | [实验文档目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2017>) | [正式输入和Physics MD](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2017>) | [本次指定网格核对JSON](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/legacy_sm_grid_check.json>) |
| Ar2020 | [实验文档目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/Ar2020>) | [正式输入和Physics MD](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_Ar/Ar2020>) | [本次指定网格核对JSON](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/legacy_sm_grid_check.json>) |
| CONUS+ | [onboarding目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1>) | [实验data目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/CONUS_Plus/conusplus_kkl_run1>) | [关联SM计算目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-sm-response-20261106>) |

### ⁸B 单 bin：三个样本的一套独立分析

- 主文件：[SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)。
- 机器输入：[analysis.input.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)、[fitted_yields.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json>)；同目录保存源谱、Xe库存、三份接受度及README。
- 分支登记：[PandaX SINGLEBIN_BRANCH.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SINGLEBIN_BRANCH.json>)与[XENONnT SINGLEBIN_BRANCH.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SINGLEBIN_BRANCH.json>)，记录输入、计算入口、结果、指纹、人工接受与原多bin关系。
- 当前结果：[BENCHMARK_SUMMARY.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json>)；目录下PandaX_paired、PandaX_US2、XENONnT分别保存SM_RESULT.json、PREPARED_MODEL.json、sm_prediction.npz及README。
- 历史/核对：[全部单bin运行](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/solar_b8_singlebin>)，包括run1、run2、validation；原始v3.2规范与审查目录也已在总清单列出。

### CsI-time：同一CsI2021测量的9×11分析

- 主文件与结果报告：[experiment.physics.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md>)、[SM_BENCHMARK.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>)、[NSI_BENCHMARK.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>)。
- P00/P01/P02/P03、DECISION_LOG、data、sources、evidence及SM/NSI配置记录：[time_resolved工作记录目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved>)。
- SM数值：[benchmark.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_20261107/benchmark.npz>)、[events_99bins.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_20261107/events_99bins.csv>)；该目录同时保存各网格与收敛证据。
- 观测叠加与NSI：[20261109数据叠加](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_sm_data_comparison_20261109>)、[20261108 NSI结果](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/csi2021_time_nsi_20261108>)。
- 默认注册CsI2021的旧一维九箱与本时间分析不是同一个analysis。完整清单把旧一维说明标为关联背景，不把它当作时间分析输入。

### CsI2017 与 Ar2020：正式两机器文件加人类说明

- **CsI2017**：[experiment.input.yaml](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml>)、[experiment.resources.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2017/experiment.resources.npz>)、[experiment.physics.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md>)；detector/与statistics/保留原始或旧版来源核对材料，当前Runtime以YAML/NPZ为权威。
- **Ar2020**：[experiment.input.yaml](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml>)、[experiment.resources.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz>)、[experiment.physics.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md>)；detector/与statistics/保留原始或旧版来源核对材料，当前Runtime以YAML/NPZ为权威。

两者本次SM指定网格复算共用[legacy_sm_grid_check.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/legacy_sm_grid_check.json>)；历史冻结数值位于[baseline.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/tests/reference/interface_refactor_v1/baseline.npz>)。二者不应凭空补一个“已有独立完整SM收敛运行目录”；本次只保存了明确网格的兼容核对。

### CONUS+：同一dataset的主项目资料与两套关联计算

- Onboarding：[experiment.physics.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md>)；相邻summary、用户资料、REFERENCES.md/.bib和README均已列入清单。
- 数据：[data/experiments/CONUS_Plus/conusplus_kkl_run1](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/CONUS_Plus/conusplus_kkl_run1>)。
- 来源、证据、合同与决定：[workflow记录目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1>)。
- SM完整计算目录：[conusplus-sm-response-20261106](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-sm-response-20261106>)；重点文件为calculate_sm.py、run_benchmark.ps1、review/SM_BENCHMARK_REPORT_V1.md、outputs/summary.json、outputs/fine_641.npz、outputs/sm_counts_19bins.csv及outputs/validation.json。
- NSI完整计算目录：[conusplus-nsi-response-20261106](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-nsi-response-20261106>)；重点文件为run_nsi_benchmark.ps1、review/NSI_CONTRACT.json、review/NSI_BENCHMARK_REPORT_V1.md、outputs/summary.json、outputs/nsi_intervals.csv、outputs/nsi_quadratic_templates.npz及outputs/validation.json。
- 两处snapshot/均是固定输入/代码副本，不是新的实验权威；本次已将其中402个文件单独标为snapshot。主项目与两套快照的19项所选输入/文档分别一致，详细核对见计算汇总旁的CONUS_BENCHMARK_READBACK.json。

[返回目录](#toc)

<a id="code"></a>

## 2. 代码、统计与复算文件

| 分析 | 实际入口与实现 |
|---|---|
| ⁸B单bin | [运行器](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/tools/run_solar_b8_singlebin_benchmark.py>)；[实验装配/积分](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/solar_singlebin.py>)；[独立统计](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/statistics/solar_singlebin.py>) |
| CsI-time SM | [run_benchmark.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)；[验证/绘图/汇总](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/COHERENT_CsI/time_resolved_sm>) |
| CsI-time NSI | [NSI入口及核对脚本](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/COHERENT_CsI/time_resolved_nsi>) |
| CsI2017 | [definition](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/csi2017_definition.py>)；[兼容Slow](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py>)；[兼容Fast](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py>) |
| Ar2020 | [definition](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/ar2020_definition.py>)；[兼容Slow](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py>)；[兼容Fast](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py>) |
| CsI2017/Ar当前Package执行 | [package_profiles.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/package_profiles.py>)；[legacy_observables.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/rates/legacy_observables.py>)；[公共runtime](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/experiments/runtime.py>) |
| CONUS+ SM/NSI | [calculate_sm.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-sm-response-20261106/calculate_sm.py>)；[NSI模型](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-nsi-response-20261106/nsi_model.py>)；[编译/预测](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-nsi-response-20261106/prepare_predictions.py>)；[扫描/拟合](<F:/Work/2026-07-15 CEvNSpyEFT-Local/.experiment-auto-runs/conusplus-nsi-response-20261106/benchmark_nsi.py>) |
| 共享物理资源 | [responses_all.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/responses/responses_all.json>)；[公共理论](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/theory>)；[公共rates](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/cevns_pyeft/rates>) |

**CsI-time有两份实际跨副本依赖**：[time_acceptance.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time/time_acceptance.py>)、[time_profile.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time/time_profile.py>)。当前运行器通过显式`--legacy-time-dir`读取它们，文件已单列。仅复制Gitup01并不能保证这条时间分析独立复算。

[返回目录](#toc)

<a id="layout"></a>

## 3. 实际目录关系

```text
F:/Work/2026-07-15 CEvNSpyEFT-Local/
├─ 261103Gitup1-CONUS-6/Gitup01/
│  ├─ docs/experiments/     实验说明、onboarding和阅读导航
│  ├─ data/                正式机器输入、响应、谱表和来源数表
│  ├─ cevns_pyeft/         公共引擎及实验装配
│  ├─ tools/、examples/    计算、验证、绘图和管理入口
│  ├─ workflows/.../runs/  来源、证据、合同、决定、阶段及部分分析输入
│  └─ outputs/             主项目内的运行与验证产物
├─ .experiment-auto-runs/
│  ├─ conusplus-sm-response-20261106/
│  │  ├─ snapshot/        固定的主项目输入/代码
│  │  ├─ outputs/         149.419400事例及网格/图表
│  │  └─ review/          来源、阶段与科学限制
│  └─ conusplus-nsi-response-20261106/
│     ├─ snapshot/
│     ├─ outputs/         NSI扫描/区间/二维区域
│     └─ review/
└─ 260929Gitup1-CONUS-2/Gitup01/.../2021CsI_root_time/
   └─ 两个被CsI-time读取的时间模块
```

有两个不同层次：dataset定义一次测量身份，analysis定义单bin/多bin/时间分析和统计口径，run记录一次计算及其固定输入。目录和索引都需要表达这三层；一个默认Runtime dataset注册表覆盖不了全部分析和隔离运行。

[返回目录](#toc)

<a id="assessment"></a>

## 4. 结构是否合理

| 结构 | 判断 | 原因与当前缺口 |
|---|---|---|
| docs / data / runtime / outputs 职责分离 | 合理 | 人类说明、数值输入、实现和运行结果各自有明确职责，便于版本追踪和避免把结果误读成输入。跨目录需要稳定导航。 |
| CONUS+主项目外的隔离计算 | 作为候选运行合理 | 固定snapshot能保留来源与实现，避免自动改动主项目；当前主项目入口却没有关联这两套已完成运行。 |
| ⁸B单bin与多bin分支隔离 | 相对完整 | 同名物理测量有不同观测/统计，独立card、输出根与SINGLEBIN_BRANCH.json合理；这些分析索引还未形成所有实验共用的导航约定。 |
| CsI-time的docs/workflow/examples/outputs | 基本可导航，复算依赖分散 | README已链接SM、NSI与观测叠加；分析输入放在workflow记录内，且两个时间模块跨到旧项目副本，需要清楚声明可迁移边界。 |
| CsI2017/Ar的Physics MD放在data包内 | 符合当前Package合同 | YAML、NPZ、Physics MD组成可分发输入包，docs入口提供链接即可；实际MD与现有Renderer不同步，属于真实维护问题。 |
| COHERENT与CONUS/PandaX/XENON的层级命名 | 尚不统一 | COHERENT用docs/COHERENT/CsI2017而data用COHERENT_CsI/CsI2017；其他实验又使用datasets/<id>。机器和人都需要别名/身份映射。 |
| 输入、计算、Runtime激活与人工审核状态 | 缺少共同视图 | PARTIAL/NOT_REVIEWED说明来源或接受范围，不能直接回答是否存在计算。原输入构建记录的fit_executed=false也不是整个dataset的最新统计状态。 |

本次额外发现：Registry仍声明[CsI2017统计目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/data/experiments/COHERENT_CsI/CsI2017/statistics>)中的`observation_schema.json`，当前文件缺失；总清单以MISSING单列。Ar的PE/keVee冲突和两份Physics MD的Renderer不一致已在计算汇总记录，不能靠改文件夹名字解决。

[返回目录](#toc)

<a id="omission"></a>

## 5. 为什么会漏掉

直接过程有四步：

1. **我把首次搜索限制在用户给出的Gitup01内。** CONUS+两个结果目录是它的外部同级工作区中的`.experiment-auto-runs`子目录，普通以Gitup01为根的文件搜索不会覆盖；我没有进一步检查同dataset的关联运行。
2. **我把局部搜索结果表述得过强。** 主项目内部未找到结果，只能支持“该搜索范围内未发现”，不能推出整个数据集没有SM。
3. **我错误扩大了状态字段的含义。** PARTIAL是来源/审阅状态；原data中的fit_executed=false属于输入构建记录；Runtime registry也只是默认活动入口。这些都不能否认隔离目录里已有SM/NSI结果。
4. **原入口缺少关联运行导航，增加了漏查概率。** 本次扫描原CONUS文档、data、workflow下29份MD/JSON/YAML，排除本轮新写汇总，两个run名均为零命中。原README链接了更早的v2隔离资料，却没有列这两套后续benchmark；我本可据外部资料的存在继续核查。

因此，目录设计解释了遗漏风险；这次遗漏的直接责任在我的检索和判断。隔离候选不自动成为正式结果，并不意味着它应从资料汇总中消失。

证据在[FILE_INVENTORY_20261111.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/FILE_INVENTORY_20261111.json>)的`CONUS_forward_navigation_check`；默认文档校验器还显式排除outputs目录，见[validate_docs.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/tools/validate_docs.py>)。链接校验通过只能证明已列链接可解析，不能证明所有已完成运行都被列出了。

[返回目录](#toc)

<a id="recommendations"></a>

## 6. 建议怎样整理

建议优先完善身份与导航，再按需要处理物理依赖和文件迁移：

| 顺序 | 建议 | 具体内容 |
|---|---|---|
| 1 | 每个dataset的主README维护分析/运行表 | 至少列analysis_id、单bin/时间等口径、onboarding、输入、代码入口、SM/NSI结果、主项目内/隔离位置与run_id；结果状态链接到原记录。 |
| 2 | 由同一索引生成全项目视图 | 把已有SINGLEBIN_BRANCH.json等记录纳入统一导航；索引引用现有科学合同、参数和审核状态，避免再复制一套物理参数或批准状态。 |
| 3 | 同时展示四种状态 | 分别展示onboarding/来源状态、计算产物存在状态、Runtime注册状态、人工接受状态，允许“PARTIAL但已算完候选”。 |
| 4 | 主入口与run双向关联 | 隔离run记录dataset与source_root；主dataset入口也链接run。文件可继续独立存放，用户从一个入口能走完来源→输入→代码→结果链。 |
| 5 | 明确外部运行依赖 | CsI-time两个跨副本时间模块应有显式依赖/指纹和复算说明；如后续迁移，先核对调用、资源、许可、数值回归及原科学范围。 |
| 6 | 检查覆盖运行清单 | 除本地链接检查，再验证每个已登记run的入口、manifest、结果是否存在，并核对主README是否覆盖。outputs/和隔离run按明确路径检查，不自动改写历史记录。 |
| 7 | 统一展示命名映射 | 明示“⁸B单bin→三样本”“CsI-time→CsI2021_time_9x11”“Ar→Ar2020”“CONUS→conusplus_kkl_run1”；现有导入路径和数据身份按其合同维护。 |

本轮已建立逐文件地址清单与跨实验结构入口，没有移动计算目录、改原onboarding、更新旧保护指纹或修改Runtime。后续整理应维护所属README及生成器的同一来源链；CONUS生成器自身已有指纹核对问题，不应只手改生成报告使其看起来通过。

[返回目录](#toc)

<a id="checks"></a>

## 7. 本轮交付与检查

| 交付 | 用途 |
|---|---|
| [FILE_ADDRESSES_20261111.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/FILE_ADDRESSES_20261111.md>) | 每个选定目录及1325个现存文件的完整绝对地址；402个快照单独标注 |
| [FILE_INVENTORY_20261111.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/FILE_INVENTORY_20261111.json>) | 相同清单的机器结构、目录范围、排除规则、缺失登记和导航检索证据 |
| [LAYOUT_AUDIT_CHECKS.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/outputs/mainline_summary_20261111/LAYOUT_AUDIT_CHECKS.json>) | 地址存在性、文档链接、明确锚点、文件归属、164项原输入/实现保护核对 |

本次没有新的物理计算，前述SM/NSI数值仍以既有汇总和各运行manifest为准。文件地址存在不等于来源认证；未遍历的目录不被写成“没有文件”。

[返回目录](#toc)
