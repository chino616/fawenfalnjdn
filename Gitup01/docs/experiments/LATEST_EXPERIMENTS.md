# 当前五条实验主线：最新版本与处理方式

更新至2026-11-13。[当前非8B计算与论文复现状态](CURRENT_REPRODUCTION_STATUS.md)继续核对CsI-time、CsI2017、Ar2020与CONUS+。8B独立对话的continuous_acceptance（连续效率曲线）最新交付已完成，见本页文末论文图集。下表保留2026-11-11整理的五条SM/前向主线基线，后续太阳版本分别列于本页下方；旧版本保留在原历史位置。

[对应文件夹构造](<LATEST_FOLDER_LAYOUT.md>)

| 实验/分析 | 当前版本 | 方法说明 | Onboarding/输入 | 结果 |
|---|---|---|---|---|
| 太阳⁸B：单bin（三样本） | v3.2.1 / 20261111_response_run2 | [METHODS.md](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/METHODS.md>) | [说明](<PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>) / [输入](<../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>) | [SM结果](<../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>) |
| CsI-time：9PE×11时间箱 | r2 / SM 20261107；NSI 20261108 | [METHODS.md](<COHERENT/CsI2021/time_resolved/METHODS.md>) | [说明](<COHERENT/CsI2021/time_resolved/experiment.physics.md>) / [输入](<../../data/experiments/COHERENT_CsI/CsI2021/time_resolved/analysis_inputs.npz>) | [SM报告](<COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>) / [NSI报告](<COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>) / [观测叠加](<../../outputs/csi2021_time_sm_data_comparison_20261109/README.md>) |
| CsI2017：25PE箱确定性映射 | Package v2 / legacy compatibility | [METHODS.md](<COHERENT/CsI2017/METHODS.md>) | [说明](<../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md>) / [输入](<../../data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml>) | [最新核对结果](<../../outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json>) |
| Ar2020：12箱专用观测宽度Gaussian | Package v2 / legacy compatibility | [METHODS.md](<COHERENT/Ar2020/METHODS.md>) | [说明](<../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md>) / [输入](<../../data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml>) | [最新核对结果](<../../outputs/COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json>) |
| CONUS+：SM / 矢量NSI Response | onboarding v3 / Response benchmark v1 | [METHODS.md](<CONUS_Plus/datasets/conusplus_kkl_run1/METHODS.md>) | [说明](<CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md>) / [输入](<../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) | [SM报告](<CONUS_Plus/datasets/conusplus_kkl_run1/benchmarks/sm_response_20261106/SM_BENCHMARK.md>) / [SM结果](<../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json>) / [NSI报告](<CONUS_Plus/datasets/conusplus_kkl_run1/benchmarks/nsi_response_20261106/NSI_BENCHMARK.md>) / [NSI区间](<../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_intervals.csv>) |

## 方法之间的区别

| 分析 | 观测与探测器处理 | 统计/结果性质 |
|---|---|---|
| 太阳⁸B：单bin（三样本） | paired / US2 / XENONnT各一个信号总数；真反冲×Total接受度积分；不读旧多bin的Qy/Ne/cS2或其缓存。 | 三个拟合信号量的Gaussian，各自独立12% pull；XENONnT缺尾段用区间，joint_chi2=null。 |
| CsI-time：9PE×11时间箱 | QF→光产额→Gamma→PE效率，再施加时间权重；99箱，events/bin；0–6μs参考窗注量为主口径。 | SM为未拟合353.465608686事例；NSI为24点前向对照，不是参数区间或原生二维likelihood。 |
| CsI2017：25PE箱确定性映射 | PE=1.17T，固定251节点、4.9 PE效率阈值；不使用CsI2021 Gamma/时间响应。 | 单28%归一化pull的近似Gaussian，保留有符号residual。 |
| Ar2020：12箱专用观测宽度Gaussian | 均值(0.246+0.00078T)T；σ(x)=0.58√x依赖观测值；效率为表格。 | 非对称IRLS、有界信号/背景pull .12/.146。 |
| CONUS+：SM / 矢量NSI Response | 19×10 eVee箱；Lindhard k=.162＋真电离能Gaussian，ROI损失保留；Nuclear Response，非论文KN等价。 | SM：未拟合前向149.419399803事例；NSI：六个实数u/d矢量坐标，误差均值、Gaussian .169归一化pull的近似区间/二维比较。 |

## Gitup01内的归属

- docs/experiments：当前说明、METHODS和可点击阅读入口。
- data/experiments、data/benchmarks：原物理输入和明确分析专属的数值基准。
- examples：调用公共引擎的复算/验证脚本；CsI-time已采用本地时间模块。
- outputs：最新计算的数值、图、缓存与验证；同次运行内的网格比较是收敛证据。
- workflows/.../runs：来源、决定、合同与阶段记录；不作为Runtime代码依赖。

CONUS+最新SM/NSI已在Gitup01内按上述职责集中；历史输入实现仅保存一份压缩证据，计算入口使用本地显式资源。
数值、DRAFT/PARTIAL、NOT_REVIEWED及Ar单位冲突等限制保持原记录；目录迁入不自动激活新Runtime dataset。

[本次整理与验证](<../../outputs/latest_layout_20261111/README.md>)

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

太阳单bin增加电子味NSI v3.3；旧表中的v3.2.1仍是SM入口。NSI已实际计算，精确论文绿色复现未成立。

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


<!-- paper-sm-20261113:start -->

## 标准模型论文图片与8B最新交付（2026-11-13）

[按实验分目录的完整论文图集](<../../论文图NoteBook/8. SM_experiment_benchmarks/README.md>) · [参考文献、图号与方法区别](<../../论文图NoteBook/8. SM_experiment_benchmarks/REFERENCES_AND_METHODS.md>)。

太阳独立对话已完成2图+1表；本轮引用其最新continuous_acceptance数值：paired 2.48782983649、US2 47.0434197257、XENONnT 11.8573626872 events。旧参考模板的2.54267439331、47.1440697081、9.44080510496单独展示，不当作实验拟合信号或同一配置。三样本总数与2411.11749 Fig.1多bin谱形分别作图。原8B运行/源码未覆盖。

Ar论文图使用已存最细321/1920/64网格139.914559219 events；上表136.632223203是11/40/8指定回归网格，保留为不同数值处理。CsI2017仍为指定n_enu=12兼容结果；CsI-time仍为前向诊断。图片排版验收不将它们提升为官方似然或所有论文等价通过。

<!-- paper-sm-20261113:end -->
