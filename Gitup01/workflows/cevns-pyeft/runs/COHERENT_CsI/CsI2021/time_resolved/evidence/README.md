# 本次证据与检查

| 文件或目录 | 内容与适用范围 |
|---|---|
| [legacy_resolution/](legacy_resolution/README.md) | 此前旧目录生成的数值诊断、逐箱CSV、网格数组和相关算法快照。单独保存输入差异，未当作本轮官方参数草稿的同条件结果 |
| `2211.11905v2.txt`、`2202.11002v3.txt`、`Supplement.txt` | 从P00登记的本地原文提取的辅助定位文本，PDF为原始版本权威 |
| `PDG2024_pi_charged_p1.png`、`PDG2024_pi_charged.txt` | 原始质量listing的视觉核对与定位文本 |
| [PROVENANCE_CHECKS.json](PROVENANCE_CHECKS.json) | 实际来源指纹、数组读取/逐值一致、原ResponseDB调用、claim依赖和同源生成检查 |
| [READABILITY_CHECKS.json](READABILITY_CHECKS.json)、[readability/](readability/README.md) | 链接、锚点、实际目录点击、数学节点/编号、桌面与窄视口截图及独立HTML预览 |
| [REVIEW_REPORT.md](REVIEW_REPORT.md) | 本轮验收范围、人工目视复核、未闭合的科学问题和文件/README对应 |
| [ARTIFACT_MANIFEST.json](ARTIFACT_MANIFEST.json) | 本轮来源、证据、配置、生成器、实际数据和派生文件SHA256；不替代P00来源身份 |
| [workflow-tests.log](workflow-tests.log)、[workflow-tests-localtemp.log](workflow-tests-localtemp.log) | 初次全局检查与工作区TEMP/TMP下的复查；本轮检查结果和既有全局问题分开记录 |
| [GLOBAL_WORKFLOW_ISSUES.json](GLOBAL_WORKFLOW_ISSUES.json) | 全局失败的完整条目与当前CsI范围匹配；包含作者README的SSH地址被误判为本地链接这一检查器限制 |
| [PROTECTION_REFRESH.json](PROTECTION_REFRESH.json) | 仅对获准修改的data/responses/README.md刷新保护指纹，未刷新其他保护项 |

逐数据解释以 [P01](../P01_EVIDENCE_LEDGER.yaml) 为权威，检查器不自动证明引文支持所有物理主张。

[上一级](../README.md)


2026-11-18重启输入核查：[INPUT_FILE_REVIEW_20261118.json](INPUT_FILE_REVIEW_20261118.json)。仅证明列出的来源指纹、原始事件重分箱、η/能谱积分、实际核表和ROOT缓存一致；不是r3物理接受或P07通过。
