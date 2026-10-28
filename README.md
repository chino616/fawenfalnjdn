# CEvNS-pyEFT · 重构-02

本分支编号：**Refactor-02（重构-02）**。日期：2026-10-29。
分支：`refactor/02-experiment-modularization-20261029`。
承接重构接口分支 `refactor/modular-interfaces-20261028` 的提交 `d7182a1`。

本轮将四个既有实验集中为独立定义，统一加载、预测、评价与启停，保留各自物理约定、
数值策略和已有Fast能力。修改实验设定通过不可变定义实例与显式资源目录完成。

| 实验 | 权威定义 |
|---|---|
| CsI2021 | [csi2021_definition.py](Gitup01/src/cevns_pyeft/experiments/coherent/csi2021_definition.py) |
| CsI2017 | [csi2017_definition.py](Gitup01/src/cevns_pyeft/experiments/coherent/csi2017_definition.py) |
| Ar2020 | [ar2020_definition.py](Gitup01/src/cevns_pyeft/experiments/coherent/ar2020_definition.py) |
| conus_plus_2025_c2c3c5_ge73_pyeft | [definition.py](Gitup01/src/cevns_pyeft/experiments/conus_plus/definition.py) |

## 使用与核验记录

- [重构-02说明](Gitup01/docs/experiment_modularization/RELEASE_02.md)
- [统一接口和参数替换](Gitup01/docs/experiment_modularization/USAGE.md)
- [启停配置](Gitup01/docs/experiment_modularization/analysis_selection.example.yaml)
- [参数归属](Gitup01/docs/experiment_modularization/PARAMETER_OWNERSHIP.md)
- [实际能力](Gitup01/docs/experiment_modularization/CAPABILITY_MATRIX.md)
- [迁移报告与恢复清单](Gitup01/docs/experiment_modularization/MIGRATION_REPORT.md)
- [实施方案](重构/261028_CODEX_EXPERIMENT_MODULARIZATION_PLAN.md)
- [上一轮接口文档](Gitup01/docs/interface_refactor/README.md)

本地全套222项通过；最终补测后去重223项通过；634个独立基线数组回归无差异。
wheel安装后从项目外cwd计算四实验通过。以上是本地验证记录，未宣称GitHub CI通过。

## 上传范围和资源边界

本次提交仅含源码、测试、源码示例/核验工具及重构文档；保留父提交的既有内容。
不新增本地实验数据、论文、Notebook、outputs、backup、核文件、wheel或缓存。
执行完整实验测试前需另行准备data；运行时通过ResourceCatalog指定资源根。
迁移报告中的本地绝对路径与outputs记录用于溯源，本次不包含对应数值产物。

CONUS+ digitized Gaussian统计仅绑定显式effective119 C3类配置，不能用于默认357kg·day
三探测器合计预测，也不是官方on/off likelihood。本轮工程重构未升级科学批准结论。
