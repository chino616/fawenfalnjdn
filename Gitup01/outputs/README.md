# outputs：运行结果、缓存与工程验证产物

[公共论文主题 v4 接入验证（2026-11-15）](paper_theme_v4_integration_20261115/README.md)：模板与 CsI 味分量图的独立试画、输入/CSV 一致性、12/24 系列接口及文档链接核对；公共主题和文件架构见 [plotting/](../plotting/README.md)。

[CsI2021主线现状与完整文件地址（2026-11-15）](csi2021_mainline_review_20261115_run1/README.md)：只读摘录24个前向点、26条一维、16个二维面和76条能标；附20步Python路线、来源哈希、文献依据及版本差异，99箱时间和9箱/联合统计身份分开。

[最新实验结果汇总表（2026-11-15）](results_summary_20261115_run2/README.md)：17表Excel、17类CSV及完整Markdown，覆盖SM、参数、NSI、χ²、224条截断能标和逐项benchmark；完整分离区间、符号、SM分支及计算方法保留，旧结果只读核对。

[截断能标独立Part](cutoff_scales/README.md)：原24条dim-6与176条完整22控制结果保留；新增三组联合、66＋10行论文Fig.3数值差异、统一视觉角色图及保护/渲染验收。固定态控制与逐点太阳传播主结果分别保存，未认证跨实验协方差和dim-8物理正定性。

[二维SM/NSI实验benchmark（2026-11-13）](two_d_benchmark_20261113_run1/README.md)：41平面当前索引、二维系数、82个完整/显示χ²面及轮廓、论文换轴与内洞处理、独立数值验收和统一图件。不同统计方法分别保存，旧一维结果保持原样。

[实验路线与一维SM/NSI χ²（2026-11-13）](one_d_benchmark_20261113_run1/README.md)：70项逐步Python审计、66条单参数结果、全部分离区间、独立数值核对、参考文献和七张论文图。正式输入、Runtime与既有结果保持原样；未执行能力及冻结核回放范围见报告。

[标准模型论文图集（2026-11-13）](<../论文图NoteBook/8. SM_experiment_benchmarks/README.md>)保存在论文图目录，包含CONUS+、CsI-time、CsI2017、Ar2020及太阳单bin/多bin的已存结果重绘、对应文献与逐箱数据。8B最新continuous_acceptance结果已整合；各方法与严格复现范围分别标注。

[当前非8B进展与论文复现状态（2026-11-13）](../docs/experiments/CURRENT_REPRODUCTION_STATUS.md) · [本轮状态回读、指纹与链接检查](reproduction_status_20261113/README.md)。该条目保留此前四条非8B主线核对范围；8B最新已完成交付见上方论文图集。

[Fig.4全图重绘（2026-11-12较早快照）](paper2601_fig4_redraw_20261112/README.md)：原图/修正计算并排、Ar两种误差方案及旧极小值的局部放大；绿色仅为当时论文参考，太阳后续实际计算见上方v3.4.1。

[修复搜索后的常规benchmark](paper2601_chi2_corrected_20261111/README.md)保存与原先相同均误差模型的重算结果，二维联合χ²min已修正；Ar非对称模型另见联合复核，不混作相同处理。

[Fast专项最新审计](paper2601_fast_audit_20261111/README.md)：对CsI、Ar和CONUS逐bin、逐源/核素比较原生Slow、Fast、能量插值、缓存及扫描多项式，覆盖联合拟合大耦合极小值。

[2601联合结果复核（2026-11-11）](paper2601_joint_audit_20261111/README.md)：已修复二维狭长谷漏搜极小值，重算Δχ²；保存Ar处理差异、同时profile检验及图4边界对照。太阳未算NSI的旧状态已由上方最新结果更新。

[最初卡方复算（联合极小值已失效，保留历史证据）](paper2601_chi2_20261111/README.md)：原始SM值和一维对照保留；最新二维轮廓使用上方已修复搜索的结果。

[最新五条实验结果与方法](<../docs/experiments/LATEST_EXPERIMENTS.md>)。本入口仅列当前选定分析；不同方法的输入、代码、结果和审核范围分别说明。

[五条主线汇总核对（2026-11-11）](mainline_summary_20261111/README.md)保存⁸B单bin、CsI-time的数值回读、两条legacy SM指定网格复算、CONUS+关联benchmark核对，以及全部选定文件地址和目录结构审计；对应[计算汇总](../docs/experiments/MAINLINE_ONBOARDING_SM_SUMMARY_20261111.md)与[文件布局分析](../docs/experiments/MAINLINE_FILE_LAYOUT_AUDIT_20261111.md)。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin结果独立保存

[单bin v3.2.1：输入、来源、代码与SM结果](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md>) · [多bin v3.1（保留）](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。

单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；[独立数据](<../data/benchmarks/solar_b8_singlebin_2601_19883/README.md>)、[独立入口](<../tools/run_solar_b8_singlebin_benchmark.py>)、[独立结果](<solar_b8_singlebin/20261111_response_run2/README.md>)。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## 太阳⁸B：真实核Response SM

[20261110_nuclear_response_run2](<solar_b8_sm/20261110_nuclear_response_run2/README.md>)保存两实验实际核表预测、同范围KN对照、分量/收敛与来源。run1为端点检查触发的首次部分运行，保留不覆盖。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## Solar B8 onboarding v3.0整合验收

[solar_b8_onboarding_v3/](solar_b8_onboarding_v3/README.md)保存文档合版的输入/来源清单、文件保护、生成一致性与阅读性检查。物理结果沿用既有SM/矢量运行。

<!-- solar-onboarding-v3:end -->

本目录保存由运行或维护任务产生的结果。`ResourceCatalog` 不会自动搜索 outputs；预测通常先返回内存对象，调用方显式保存核或报告后才形成文件。

| 子目录 | 当前内容及来源 |
|---|---|
| [experiment_modularization/](experiment_modularization/README.md) | 统一实验入口、组件替换、身份与资源管理的历史验收结果 |
| [refactor/](refactor/README.md) | CsI2021 组合式 Slow 重构的阶段检查、比较及原件快照 |
| [refactor_r4/](refactor_r4/README.md) | 组合式 Fast、内容缓存、full/pair 与旧 builder 的历史检查 |
| [refactor03/](refactor03/README.md) | 资源、接口和目录整理的基线、阶段检查与报告 |
| [release/](release/README.md) | `tools/build_wheel.py`、`verify_wheel.py` 写入的构建/隔离运行记录 |
| [csi2021_time_sm_20261107/](csi2021_time_sm_20261107/README.md) | 主项目Slow与既有时间权重计算的CsI2021标准模型99箱、投影及时间窗图，含源/核素分量、独立积分收敛和来源指纹 |
| [csi2021_time_sm_data_comparison_20261109/](csi2021_time_sm_data_comparison_20261109/README.md) | 2026-11-15修订：区分De Romeri Fig.18原始计数时间窗与COHERENT Fig.1仅扣SSB投影；四组未拟合图、部分C/AC计数协方差、题注和修订前快照 |

## 为什么与输入和测试参考分开

同一个实验可运行不同 Wilson 点、网格和软件版本。结果必须对应当次输入，不能因文件名相同就当作当前值。冻结回归值归 `tests/reference/`；当前物理输入归 `data/`；这些历史产物只说明其记录的那次运行。

## 新运行如何管理文件

为新任务创建 `outputs/<任务名称或运行标识>/`，把报告、缓存和图表放到该次运行中。建议同时记录 dataset ID、实际代码/资源哈希、理论参数、数值网格、单位、生成命令和输出清单；不要用目录名或 mtime 代替这些身份信息。

核由保存 API 生成，JUnit XML 由测试命令的 `--junitxml` 产生，构建日志由发行工具产生；不要手工修改它们使报告显示 PASS。重新运行优先用新目录，现有历史 `original/` 快照不作为第二份活动源码编辑或导入。发行工具当前固定写 `release/`，运行前应明确会更新其中的日志和描述文件。

---

[上一级](../README.md)


## CsI2021 package 执行（2026-11-04）

当前副本缺少历史`csi2021_package_execution_20261104/`输出目录。历史P04–P09说明、当时的网格与打包结论见[CsI2021执行记录](../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/README.md)，不把缺失目录列为当前可打开结果。
# Task10 package migration evidence

`onboarding/task10/` retains the Ar2020/CsI2017 acquisition IR, declared arrays,
compiler/validation reports, regression logs, project installation report and
resource audit. They are engineering evidence, not a second runtime input
authority or human physics decision. Build/install logs and restricted engine
copies stay in the fresh external directory recorded in the report.

## Onboarding 溯源规则维护（2026-11-06）

[onboarding_provenance_20261106](onboarding_provenance_20261106/README.md)保存主文件/公共流程/模板/输出规范的变更映射、修改前检查和本次验收结果；这是流程维护证据，不是实验输入、原文数字核验或科学批准。


## CONUS+ onboarding v3 整合（2026-11-06）

[conusplus_onboarding_v3_20261106](conusplus_onboarding_v3_20261106/README.md)保存主项目来源标注版的交付清单与实际核验记录。

<!-- solar-b8-sm-20261107:start -->

## 太阳8B标准模型计算（2026-11-07）

[solar_b8_sm/](<solar_b8_sm/README.md>)保存PandaX/XENONnT的标准Runtime结果、逐箱比较和数值验证；PandaX电子数谱仍缺响应。

<!-- solar-b8-sm-20261107:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[solar_b8_vector/](solar_b8_vector/README.md)保存太阳8B的轻媒介子事例数benchmark；明确区分XENONnT重建谱与PandaX真实反冲投影。

<!-- solar-vector-20261108:end -->

## CsI2021 NSI事例数（2026-11-08）

[csi2021_time_nsi_20261108/](csi2021_time_nsi_20261108/README.md)保存24个矢量NSI点、SM对照、原生Slow核对、积分加密、来源与图表；严格论文复现和拟合另保留限制。

<!-- pandax-simplified-20261110:start -->

## PandaX US2简化SM计算

[八箱计算与严格来源记录](solar_b8_sm/20261110_pandax_simplified_run1/README.md)保存2026-11-10用户要求的无分辨率平均映射结果；完整Response与旧运行保留。

<!-- pandax-simplified-20261110:end -->

<!-- xe132-representative-plot:start -->

## Xe132代表近似图

[两实验SM比较图与逐项来源](solar_b8_sm/20261110_xe132_representative_plot/README.md)：固定原通量与曝光，比较Xe132代表近似和七核素核Response预测，包含观测误差棒。

<!-- xe132-representative-plot:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

solar_b8_nsi/保存本轮真实NSI结果、601×601面、核缓存、前向验证和论文差异；不是旧纸面绿色区域。

[完整新onboarding：实际输入、标准引文、物理与程序](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

<!-- solar-snudd-v341:end -->
