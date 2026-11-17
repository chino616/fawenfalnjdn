# CONUS+ v3 待补数据、来源及实现事项

<a id="report-toc"></a>

## 目录

- [当前缺口](#section-1)
- [本轮补充记录](#section-2)
- [下一步输入](#section-3)

<a id="section-1"></a>

## 当前缺口

| 事项 | 已有依据 | 仍需补充/核验 | 影响与下一步 |
| --- | --- | --- | --- |
| 低能 32 点原始出处 | 用户 PDF 表 2 和本轮 Flux 文献图 | Kopeikin 原文图/表或作者数值文件 | 全谱归一化的原始来源限制，继续向上游核对 |
| Ge Response 数值链 | 本地 JSON、五个 Ge key、读取器与指纹 | 原始核计算论文/数据包/生成脚本及归一化转换 | Response 可信预测前处理 |
| 统计误差约定 | 原图上下误差及算术平均候选列 | 拟合前确认对称化办法，或取得作者数表 | 进入统计实现时确认 |
| 实现核验 | 源谱、靶核数、响应公式与单位已有 | 反中微子接口、Response 归一化、预测单位映射和积分收敛 | Phase 0 中分配实现与验证步骤 |

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-2"></a>

## 本轮补充记录

用户提供 Flux 文献截图，书目已与 benchmark 的 Kopeikin/Mueller 引用对应。原始数值定位继续待补，相关限制已传播到 Flux 派生量。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-3"></a>

## 下一步输入

请补充 Kopeikin 原文中这 32 点的图/表位置或原始数据文件，以及 Ge Response 的原始核计算数据包/生成脚本。当前文档可供 Phase 0 路线审阅。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->
