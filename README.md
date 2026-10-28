# CEvNS-pyEFT 模块化接口重构快照

上传日期：2026-10-28（Asia/Shanghai）。
分支：`refactor/modular-interfaces-20261028`。
基线：`conus-v2-current-snapshot-20261011` / `e04ab7a9270380d6fd0191735c489e5b7c5fe2e4`。

此分支按用户确认的范围，仅提交当前重构的源码、测试和重构文档变更。保留原分支和提交历史，不代表所有实验已经完成统一配置迁移。

## 已实现与边界

| 部分 | 当前状态 |
|---|---|
| 通用计算 | 带单位/坐标合同的模型组装、Slow、Fast 和内容指纹缓存 |
| CsI2021 | 一维 9 箱模型工厂、统一 Slow/Fast、统计适配及旧 API 兼容 |
| CsI2017、Ar2020 | 保留原实现，通过计数回归和旧 Fast 数组保护；尚未全部迁入统一实验工厂 |
| CONUS+ | 保留独立模块和既有数据/结果；尚未接入同一个 ExperimentModel 工厂 |
| 实验设定集中化 | 仍未完成所有实验的唯一配置来源和统一切换入口 |

下一项架构工作应针对“每个实验有独立、集中的定义文件，以及所有实验统一加载/切换”进行验收。当前新增的组件替换能力不能等同于这一目标已经全面完成。

本轮任务聚焦模块化和接口，外部数据接入任务已移出说明包；不新增实验物理输入，不推进工作流 Human Gate。

## 验证

- 本地完整套件：187 passed，0 failures/errors/skips。
- 新 Fast/Slow：22 个活跃算符，11 组参数与网格组合，最大逐源/逐核素/逐箱差异约 `3.91e-14` events。
- CsI2017、CsI2021、Ar2020 的旧 Fast 数组与本轮改动前参考逐项完全一致。
- Wheel 构建、隔离导入、项目外资源读取，以及源码端到 wheel 端的缓存复用通过。
- 当前新 Fast 支持固定、扫描无关入射态的一维 Li2026 系数表示。旧 Fast 保留历史换算约定；统计仍为 legacy approximate statistics。

上述是已有本地测试日志记录，不宣称新分支已在 GitHub CI 上执行通过。物理/数值约定、适用范围与科学收敛边界见实际报告。

## 文件入口

- [项目说明](Gitup01/README.md)
- [模块化与接口](Gitup01/docs/interface_refactor/README.md)
- [Fast 与缓存用法](Gitup01/docs/interface_refactor/FAST_AND_CACHE.md)
- [R4–R6 实施报告](Gitup01/docs/interface_refactor/R4_R6_REPORT.md)
- [R0–R3 阶段报告](Gitup01/docs/interface_refactor/R0_R3_REPORT.md)
- [原始重构说明包（范围已更新）](重构/CEvNS_pyEFT_interface_refactor_v1/CEvNS_pyEFT_interface_refactor_v1/README.md)

运行现有测试：

```bash
cd Gitup01
python -m pytest -q tests --basetemp=.pytest-tmp/review-run
```

本地验证环境为 Python 3.11、NumPy 2.4.6、SciPy 1.17.1、pytest 9.1.1。源码依赖见 pyproject.toml 和 requirements.txt；data 保持外置目录结构。

本次新提交的范围为 src、测试及其必要参考夹具、源码工具、接口 schema、打包配置和重构 Markdown。保留远端基线已有内容；本次不新增本地实验 data、论文 PDF/ZIP、Notebook、outputs、编译核、wheel 或构建缓存。

187 项通过是当前本地完整输入环境下的验证记录；本分支未新增相应实验数据，执行全部实验测试前需另行准备所需 data。重构报告中的本地 outputs 路径用于记录原始证据，此次未同步上传该目录。报告中的绝对路径和指纹描述本地验证环境，换环境时应核对内容或重新编译缓存。
