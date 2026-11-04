# Task 05 — CsI2021 Package-backed Runtime

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。已有修改全部保留，用户指定三文件未编辑。
任务规则、Task 05 与真实 registry→catalog→definition→loader→executor→prediction/statistics
调用链及旧 Slow/Fast 返回合同均已读取。Task 04 已完成。

## 最终行为与文件

默认 CsI2021 Catalog ID 不变，其 csi2021_definition.DEFINITION 改为
definition_from_package 的薄适配；实验数值仅来自 YAML/NPZ。旧 csi2021 工厂和 Fast 入口
分别调用已有 loader 与 interface compiler。新增
[package_compatibility.py](../cevns_pyeft/experiments/package_compatibility.py)
只转换旧 Fast 字典的容器/轴与原 raw-target 质量权重，不复制物理公式。

detectors/legacy_parameters.py 移除全部独立数值，保留从包读取的旧名称视图。
detectors/csi2021.py 的省略参数兼容值延迟读取；显式参数路径完全不导入该视图。
rates/differential.p_smearing_csi 仅在确实缺省 Gamma 参数时导入兼容值。
数学计算、shape-rate、零裁剪和网格/折叠顺序未改变。

修改的机器元数据：17 个模型声明绑定状态、engine binding、默认运行权威、三项技术能力及
其报告/证据哈希；Physics MD 同源重渲染。105 个标量值、23 个数组与 NPZ 原始字节均未变。
NPZ SHA256 仍为 `25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a`。

Schema 接受明确的绑定状态与技术证据声明；无证据的 Runtime PASS/runtime_ready 仍拒绝，
手写 consumed 不作为运行证据。校验这些声明不等于重新运行测试；实际执行由下述测试证明。
jsonschema 现为核心依赖，因为默认 Loader 需要验证输入；validation extra 保留兼容。

更新了 dataset README、旧 experiment.yaml 的权威说明、目录导航与合同说明。
不存在的 workflows/experiment-integration/runs/CsI2021 路径明确为历史缺失记录，不再称 Approved inputs。

## 验证和能力边界

使用 `F:/Work/.codex_conda_envs/codex-py311/python.exe -B`：

- `pytest test_package_runtime_migration.py test_experiment_package_loader.py test_refactor_csi2021_regression.py -k 'not default and not shared_coherent' -q`：**35 passed, 9 deselected**。
- 全 22 个算符的小网格 interface Fast，五组 SM/NP/SM+NP/复数/味矩阵点逐箱与 Slow 一致，
  同时验证旧 Fast 字典重构；rtol=1e-10，atol=1e-12。
- canonical Schema+loader+runtime 的非重复 Fast 分组：**59 passed, 1 deselected**。
- 缺省 Catalog 只解析 package_input/package_arrays；拒绝外部 responses_all.json 文件读取的 guard 下
  仍完成九箱预测。显式探测器参数路径在 legacy_parameters import guard 下运行成功。
- 小/中网格 source×isotope×bin、旧 raw 语义和 Gaussian 近似统计对冻结内部参考一致。

对应机器记录在 `outputs/onboarding/task05/runtime_verification.json`。
default/收敛/真正隔离安装由 Task 06 单独验证；runtime_ready 在本任务保持 false。
Fast 的 PACKAGE_VERIFIED 表示上述有限数值范围，不能推广到所有网格或未审核的一般反中微子 EFT。
legacy Gaussian 继续是 approximate，数据 residual/excess 与显式背景的冲突未裁决。
official likelihood、general antineutrino EFT 和 scientific release 保持 BLOCKED，human NOT_REVIEWED。

## 兼容与恢复

标准历史 responses_all.json 位置参数被保留为明确的兼容占位，不发生读取；其他外部响应覆盖
会报错，需用显式 interaction component 注入。物理默认值不能再由传入旧 JSON 悄悄替换。
这项资源 API 迁移需要将旧测试/调用的 responses resource key 改为两份 package 资源。
不修改冻结 reference 或降低容差。

Task05 现有文件恢复点位于 backup/task05-csi-runtime-20261104/ 并登记 BACKUP_MANIFEST.md。
Task 01 builder 是历史提取工具，其源码指纹与状态预期不再用于认证迁移后的包；当前检查入口为
validate_experiment_input.py，Task 08 提供通用生成器。

全局保护清单/资源生命周期与安装分发在 Task 09 汇总核对；不把本报告写成全局发布 PASS。
最终其他实验/小网格/同预测统计保护回归：16 passed, 25 deselected；七份 Markdown 的 88 个本地链接通过。
下一步 Task 06 在无旧 Definition、legacy_parameters、论文或外部响应表的引擎环境重跑。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md)
