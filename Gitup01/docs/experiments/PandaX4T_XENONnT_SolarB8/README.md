# PandaX4T + XENONnT：太阳⁸B联合分析文档

<!-- solar-singlebin-v321:start -->

## 主线分支选择：按分析方案进入

[单bin v3.2.1：输入、来源、代码与SM结果](<singlebin_2601_19883/README.md>) · [多bin v3.1（保留）](<SOLAR_B8_ONBOARDING.v3.1.md>)。

单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；[独立数据](<../../../data/benchmarks/solar_b8_singlebin_2601_19883/README.md>)、[独立入口](<../../../tools/run_solar_b8_singlebin_benchmark.py>)、[独立结果](<../../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>)。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## 当前太阳⁸B SM：v3.1 原子核Response

[当前新版本与两实验实际计算](<SOLAR_B8_ONBOARDING.v3.1.md>)。核表→振幅→截面→事例数；旧KN文档/计算保留。

<!-- solar-nuclear-v31:end -->

**组合对象：PandaX-4T 2024 US2 与 XENONnT 2024 Solar B8。** 本目录集中保存两实验共用的onboarding合版、Response来源说明与SM/V/B−L benchmark报告。它是联合分析的文档目录，不是新的实验或dataset，不参与Runtime注册。

## 历史v3.0阅读入口

| 文件 | 身份与用途 |
|---|---|
| [onboarding v3.0 完整总文档](<SOLAR_B8_ONBOARDING.v3.0.md>) | 当前统一阅读版；包含两实验的全部现行输入、来源、Response、D/B、SM/V/B−L结果和交接 |

## SM逐步计算与workflow核对

[2026-11-09：2411.11749v1 Fig.1的SM Response逐步审计](<SM_RESPONSE_WORKFLOW_AUDIT_20261109.md>)：主项目复算、逐步公式／实际数据／代码入口、run分箱与论文比较边界；各阶段的可计算范围和待补项分别列出。

## 2026-11-10：PandaX SM简化八箱计算

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)


## 历史专题与计算记录

以下文件保留当时的版本、数值和科学状态；当时结论按v3.0保留，当前SM及其未决项见页首v3.1。

| 文件 | 记录范围 |
|---|---|
| [Response参考文献 v2.0](<SOLAR_B8_RESPONSE_REFERENCES.v2.md>) | 2026-11-06，历史来源登记 |
| [Response参考文献 v2.1](<SOLAR_B8_RESPONSE_REFERENCES.v2.1.md>) | 2026-11-06，历史来源修订 |
| [SM benchmark报告](<SOLAR_B8_SM_BENCHMARK_20261107.md>) | 2026-11-07，两实验的SM执行入口 |
| [V/B−L benchmark报告](<SOLAR_B8_VECTOR_BENCHMARK_20261108.md>) | 2026-11-08，两实验的轻矢量媒介子执行入口 |

## 各实验独立文档与数据

| dataset | 独立文档 | 数据与来源 |
|---|---|---|
| PandaX4T_2024_US2 | [各版本与历史v3.0](<../PandaX4T/datasets/PandaX4T_2024_US2/README.md>) | [正式输入、数组及原表](<../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>) |
| XENONnT_2024_SolarB8 | [各版本与历史v3.0](<../XENONnT/datasets/XENONnT_2024_SolarB8/README.md>) | [正式输入、数组及原表](<../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>) |

## 目录维护约定

两实验共同使用的综述、引用与比较报告放在本目录；单实验onboarding继续放在其原dataset目录。数值输入留在`data/experiments/`，原始论文留在`docs/references/`，阶段证据留在各自`workflows/cevns-pyeft/runs/`。后续新增联合文档时同步本表、上级索引和实际生成器，不再平铺到`docs/experiments/`根目录。

[本次目录搬迁与链接验收](<../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/README.md>) · [实验文档总目录](<../README.md>)

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

新增单bin NSI v3.3；旧SM及多bin入口保留。

[完整新onboarding：实际输入、标准引文、物理与程序](<singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../../../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<../../../outputs/external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

<!-- solar-snudd-v341:end -->

<!-- solar-full-rho-trace-onboarding-v35:start -->

## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5

[微分/总截面、事例数积分与三样本差别](<singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md>) · [明确合同与待改程序](<singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。

<!-- solar-full-rho-trace-onboarding-v35:end -->
