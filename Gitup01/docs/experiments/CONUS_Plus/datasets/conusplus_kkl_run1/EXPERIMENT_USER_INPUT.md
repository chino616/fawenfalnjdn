# CONUS+ onboarding 用户资料 v3（2026-11-06）

<!-- report-navigation:start -->
[精简说明](experiment.physics.summary.md) · [详细物理说明](experiment.physics.md) · [来源登记 P00](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P00_SOURCE_REGISTER.yaml) · [证据台账 P01](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P01_EVIDENCE_LEDGER.yaml) · [缺失与冲突 P02](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P02_MISSING_AND_CONFLICTS.md) · [配置草稿 P03](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P03_PHYSICS_CONTRACT.yaml) · [Benchmark 登记](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmark/BENCHMARK_REGISTER.md) · [资料目录](README.md)
<!-- report-navigation:end -->

<a id="report-toc"></a>

## 目录

- [H0 身份与目标](#section-1)
- [H1 材料](#section-2)
- [H2 逐数据依据](#section-3)
- [H3 已有选择](#section-4)
- [首次输出后的补充交互](#section-5)
- [待补与下一步](#section-6)

<a id="section-1"></a>

## H0 身份与目标

CONUS_Plus/conusplus_kkl_run1，目标为与 2501.17843v3 的 Eq. (33)、Eq. (34)、Table II 对照的天然锗 Response 适配资料准备。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-2"></a>

## H1 材料

文献、用户 PDF、Flux 截图、原图数字化资料和本地 Response 的角色与核验范围分别登记在 P00。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-3"></a>

## H2 逐数据依据

所有采用项的数值、单位、页/表/式定位和推导输入集中在主文件中。[来源严格标注的详细版](experiment.physics.md)

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-4"></a>

## H3 已有选择

| 决定 | 用户原文 |
| --- | --- |
| D_V2_001 | 我要用Response处理 |
| D_V2_002 | 保留天然锗五同位素，只参考该 PDF 的 Flux 部分（推荐） |
| D_V2_003 | 补上 (0,0) 节点，保证非负；另保留原 PDF 外推作对照（推荐） |
| D_V3_001 | 请你依据你完成的规则，然后重新去写onboarding文件，把数据来源严格标注到文件中。并且将这部分内容并入到主文件中，为进入下面一步做准备 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-5"></a>

## 首次输出后的补充交互

上一轮已说明 Kopeikin 原始数表与 Response 核计算出处缺口。本轮询问其原文、数据包或脚本，用户补充了 Flux 文献图，已确认 Kopeikin 2012 与 Mueller 2011 的书目对应。数字节点的原文定位及 Response 上游数据仍待补。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-6"></a>

## 待补与下一步

| 事项 | 已有依据 | 仍需补充/核验 | 影响与下一步 |
| --- | --- | --- | --- |
| 低能 32 点原始出处 | 用户 PDF 表 2 和本轮 Flux 文献图 | Kopeikin 原文图/表或作者数值文件 | 全谱归一化的原始来源限制，继续向上游核对 |
| Ge Response 数值链 | 本地 JSON、五个 Ge key、读取器与指纹 | 原始核计算论文/数据包/生成脚本及归一化转换 | Response 可信预测前处理 |
| 统计误差约定 | 原图上下误差及算术平均候选列 | 拟合前确认对称化办法，或取得作者数表 | 进入统计实现时确认 |
| 实现核验 | 源谱、靶核数、响应公式与单位已有 | 反中微子接口、Response 归一化、预测单位映射和积分收敛 | Phase 0 中分配实现与验证步骤 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->
