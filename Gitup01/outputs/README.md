# outputs：运行结果、缓存与工程验证产物

本目录保存由运行或维护任务产生的结果。`ResourceCatalog` 不会自动搜索 outputs；预测通常先返回内存对象，调用方显式保存核或报告后才形成文件。

| 子目录 | 当前内容及来源 |
|---|---|
| [experiment_modularization/](experiment_modularization/README.md) | 统一实验入口、组件替换、身份与资源管理的历史验收结果 |
| [refactor/](refactor/README.md) | CsI2021 组合式 Slow 重构的阶段检查、比较及原件快照 |
| [refactor_r4/](refactor_r4/README.md) | 组合式 Fast、内容缓存、full/pair 与旧 builder 的历史检查 |
| [refactor03/](refactor03/README.md) | 资源、接口和目录整理的基线、阶段检查与报告 |
| [release/](release/README.md) | `tools/build_wheel.py`、`verify_wheel.py` 写入的构建/隔离运行记录 |

## 为什么与输入和测试参考分开

同一个实验可运行不同 Wilson 点、网格和软件版本。结果必须对应当次输入，不能因文件名相同就当作当前值。冻结回归值归 `tests/reference/`；当前物理输入归 `data/`；这些历史产物只说明其记录的那次运行。

## 新运行如何管理文件

为新任务创建 `outputs/<任务名称或运行标识>/`，把报告、缓存和图表放到该次运行中。建议同时记录 dataset ID、实际代码/资源哈希、理论参数、数值网格、单位、生成命令和输出清单；不要用目录名或 mtime 代替这些身份信息。

核由保存 API 生成，JUnit XML 由测试命令的 `--junitxml` 产生，构建日志由发行工具产生；不要手工修改它们使报告显示 PASS。重新运行优先用新目录，现有历史 `original/` 快照不作为第二份活动源码编辑或导入。发行工具当前固定写 `release/`，运行前应明确会更新其中的日志和描述文件。

---

[上一级](../README.md)


## CsI2021 package 执行（2026-11-04）

[csi2021_package_execution_20261104/](csi2021_package_execution_20261104/README.md) 保存实际网格预测、P04–P09 机器结果、JUnit、打包/拆装证据和固定输入版本。正式阶段 Gate 见该目录链接的 canonical run reports。
# Task10 package migration evidence

`onboarding/task10/` retains the Ar2020/CsI2017 acquisition IR, declared arrays,
compiler/validation reports, regression logs, project installation report and
resource audit. They are engineering evidence, not a second runtime input
authority or human physics decision. Build/install logs and restricted engine
copies stay in the fresh external directory recorded in the report.
