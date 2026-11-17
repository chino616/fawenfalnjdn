# 太阳⁸B单 bin：主线 v3.2.1（新版本）

**独立于多bin的计算与数据方案，已实际运行SM。** 完整读本是[v3.2.1 onboarding](<SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)，含逐项实际输入、标准文献引用与原文位置、代码映射、结果及缺口。

[本次标准模型结果与图](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>) · [独立数据目录](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/README.md>) · [原v3.2审查与修正](<../../../../../重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2/_review/ONBOARDING_REVIEW.md>)

| 文件 | 用途 |
|---|---|
| SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md | 完整规范、来源和主线计算 |
| PandaX4T.singlebin.physics.v3.2.1.md | paired/US2专属入口 |
| XENONnT.singlebin.physics.v3.2.1.md | 2024合并样本与尾域限制 |


[上一级：并列分析导航](<../README.md>)

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| 太阳⁸B：单bin（三样本） | [v3.2.1 / 20261111_response_run2；处理方式](<METHODS.md>) | [当前输入](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>) | [SM结果](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

本目录旧v3.2.1为SM；新v3.3为ee-uV/dV传播+散射和联合区域，来源/误差/缓存独立。

[完整新onboarding：实际输入、标准引文、物理与程序](<NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../../../../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<../../../../outputs/external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

<!-- solar-snudd-v341:end -->

<!-- solar-full-rho-trace-onboarding-v35:start -->

## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5

[微分/总截面、事例数积分与三样本差别](<SNUDD_FULL_TRACE_ONBOARDING.v3.5.md>) · [明确合同与待改程序](<SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。

<!-- solar-full-rho-trace-onboarding-v35:end -->

<!-- solar-nsi-v33:end -->
