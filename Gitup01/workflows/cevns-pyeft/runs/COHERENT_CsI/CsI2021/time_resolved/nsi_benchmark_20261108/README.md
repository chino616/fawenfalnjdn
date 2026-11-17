# NSI前向事例数基准记录

2026-11-08，用户明确选择先做未拟合NSI事例数与SM对照。本轮消费同一r2来源与SM配置，原RESPONSE和生产Runtime不变；只验收24个实对称u/d矢量NSI点，不推进正式Fast/likelihood科学冻结。

| 记录 | 用途 |
|---|---|
| [08_NSI_FORWARD_BENCHMARK_REPORT.md](08_NSI_FORWARD_BENCHMARK_REPORT.md) | 与主文档和输出报告同源生成的事例数、来源、图表、验收与下一步输入 |
| [NSI_CONFIG.json](NSI_CONFIG.json) | 完整采用输入、逐项出处、原SM系数、NSI映射、矩阵、最终网格和时间约定 |
| [RESOURCE_AUDIT.json](RESOURCE_AUDIT.json) | 实际响应、原package/helper、r2证据与旧时间代码的指纹和核验边界 |
| [NAVIGATION_CHANGES.json](NAVIGATION_CHANGES.json) | 四个父README修改前的准确路径备份与指纹 |

交付文件到owner README的对应、备份与实际环境见输出目录的[变更清单](../../../../../../../outputs/csi2021_time_nsi_20261108/CHANGE_MANIFEST.json)和[交付指纹](../../../../../../../outputs/csi2021_time_nsi_20261108/ARTIFACT_MANIFEST.json)。

[本轮机器验收与数值数据](../../../../../../../outputs/csi2021_time_nsi_20261108/README.md) · [主项目可读报告](../../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md) · [实际复算代码](../../../../../../../examples/COHERENT_CsI/time_resolved_nsi/README.md) · [r2来源主线](../README.md)

BRN/NIN绝对归一、论文SM/Helm与当前RESPONSE等价、原生二维likelihood及统计区间仍按原[P02](../P02_MISSING_AND_CONFLICTS.md)分能力保留。本轮数值PASS不意味着这些问题已关闭。
