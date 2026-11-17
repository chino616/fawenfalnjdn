# CONUS+ v3 来源记录与生成（2026-11-06）

当前版本为 `v3_20261106_provenance`，整体状态为 PARTIAL。

<a id="report-toc"></a>

## 目录

- [阅读与使用](#section-1)
- [文件归属](#section-2)
- [复查与当前缺口](#section-3)

<a id="section-1"></a>

## 阅读与使用

- [详细主文件](../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.md)
- [精简版](../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/experiment.physics.summary.md)
- [标准参考文献](../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/REFERENCES.md)
- [逐数据来源映射](../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json)
- [待补事项](P02_MISSING_AND_CONFLICTS.md)

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-2"></a>

## 文件归属

P00–P05 保存来源、证据、问题、配置、决定与当前状态。ONBOARDING_SEED.json 与 OLD_VERSION_FINGERPRINTS.json 记录既有 v2 的历史来源和指纹。build_onboarding_v3.py 读取显式配置/数据，report_markdown.py 处理导航。sources/ 拥有论文/网页/用户图和代码身份快照，benchmark/ 拥有对照目标，qa/ 拥有实际检查、预览与截图。SOURCE_COVERAGE.json 保存字段/公式覆盖。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-3"></a>

## 复查与当前缺口

| 事项 | 已有依据 | 仍需补充/核验 | 影响与下一步 |
| --- | --- | --- | --- |
| 低能 32 点原始出处 | 用户 PDF 表 2 和本轮 Flux 文献图 | Kopeikin 原文图/表或作者数值文件 | 全谱归一化的原始来源限制，继续向上游核对 |
| Ge Response 数值链 | 本地 JSON、五个 Ge key、读取器与指纹 | 原始核计算论文/数据包/生成脚本及归一化转换 | Response 可信预测前处理 |
| 统计误差约定 | 原图上下误差及算术平均候选列 | 拟合前确认对称化办法，或取得作者数表 | 进入统计实现时确认 |
| 实现核验 | 源谱、靶核数、响应公式与单位已有 | 反中微子接口、Response 归一化、预测单位映射和积分收敛 | Phase 0 中分配实现与验证步骤 |

从项目根运行数据与文档生成脚本的 `--check` 可只读核对本轮输出。当前可进入 Phase 0 规划审阅，涉及原始来源和接口的事项按 P02 补齐。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| CONUS+：SM / 矢量NSI Response | [onboarding v3 / Response benchmark v1；处理方式](<../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/METHODS.md>) | [当前输入](<../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) | [SM报告](<../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/benchmarks/sm_response_20261106/SM_BENCHMARK.md>) / [SM结果](<../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json>) / [NSI报告](<../../../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/benchmarks/nsi_response_20261106/NSI_BENCHMARK.md>) / [NSI区间](<../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_intervals.csv>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
