# CEvNS-pyEFT · 重构-03

本分支编号：**Refactor-03（重构-03）**。日期：2026-10-29。
分支：`refactor/03-layout-data-interfaces-20261029`。承接重构-02提交 `bd54dba`。

本轮完成源码平铺、实验资源归属整理和实际物理组件接口：保留 `cevns_pyeft` 导入名，
四个实验分别拥有默认定义，通过统一入口装配、预测、评价和启停。

| 实验 | 默认设定的权威入口 |
|---|---|
| CsI2021 | [csi2021_definition.py](Gitup01/cevns_pyeft/experiments/coherent/csi2021_definition.py) |
| CsI2017 | [csi2017_definition.py](Gitup01/cevns_pyeft/experiments/coherent/csi2017_definition.py) |
| Ar2020 | [ar2020_definition.py](Gitup01/cevns_pyeft/experiments/coherent/ar2020_definition.py) |
| conus_plus_2025_c2c3c5_ge73_pyeft | [conus_plus/definition.py](Gitup01/cevns_pyeft/experiments/conus_plus/definition.py) |

- [发布范围与验证边界](Gitup01/docs/RELEASE_03.md)
- [项目安装与入口](Gitup01/README.md)
- [使用、启停和组件替换](Gitup01/docs/USAGE.md)
- [实验参数归属](Gitup01/docs/PARAMETER_OWNERSHIP.md)
- [能力矩阵](Gitup01/docs/CAPABILITY_MATRIX.md)
- [本地完整验证](Gitup01/docs/VALIDATION.md)
- [目录与恢复](Gitup01/docs/LAYOUT.md)
- [重构实施方案](重构/261029_CODEX_REFACTOR03_LAYOUT_DATA_AND_INTERFACES.md)

本地完整资源环境：**237 passed / 0 failed / 0 skipped**；634个数组与18项统计回归通过。
四实验项目外wheel预测、切换/selection/synthetic示例通过。以上为本地记录，未宣称GitHub CI通过。

本次新增内容限源码、测试、源码示例/核验工具、配置/契约和重构文档。
原提交已跟踪的实验数据、论文、workflow和历史输出保留；不新增本地实验数据、论文、Notebook、
数值输出、备份、归档、wheel或核缓存。完整运行需另备与本版资源清单匹配的外部data根。

CsI2017/Ar2020旧Fast对任意新组件明确拒绝；CONUS Fast仍是响应矩阵。
CONUS默认357kg·day与effective119近似Gaussian统计严格区分，未新增官方likelihood或天然Ge结果。
