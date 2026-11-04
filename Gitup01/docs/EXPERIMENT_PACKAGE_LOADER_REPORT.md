# Task 04 — Experiment Package Loader

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。工作区保留所有既有及并行修改；没有 Git 提交。
任务规则/顺序、Task 04 全文和现有 Catalog/Definition/ResourceCatalog/loader/assembly/runtime/
Prediction/statistics/fingerprints 已实际读取。Task 03 已通过。

## 交付与调用链

新增 [package_loader.py](../cevns_pyeft/experiments/package_loader.py) 和
[loader 测试](../tests/test_experiment_package_loader.py)，扩展
[package_components.py](../cevns_pyeft/experiments/package_components.py)。

```python
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

experiment = load_experiment_package(package_directory)
prediction = predict_experiment(experiment)
approximate = evaluate_experiment(experiment, prediction)
```

入口依次验证严格 YAML、闭合 Schema、派生/物化指纹、NPZ 归档/每数组 SHA256、key/shape/
dtype/单位/轴、模型公式版本和引擎快照，构建现有 ExperimentDefinition，注册进已有类型的
隔离 ExperimentCatalog，然后调用现有 load_experiment 返回 PreparedExperiment。
Physics MD 完全不读取。没有第二套 Runtime；计算仍为 core.predict，统计仍为原 Gaussian profiler。

源为 NPZ 连续谱＋YAML 派生谱线；POT、产额、几何、靶质量、效率及 acceptance 各一次。
ArraySource 的基准规模为一；显式 what-if replace 的 POT/距离/产额变化使用相对于物化基准的
比例，并在 normalization 中记录。源表支撑/插值配置变化必须显式重建，不自动生成缺失资源。
靶核数读取经校验的只读推导值；显式质量场景使用现有 inventory_from_mass_fractions。
无响应 JSON、旧 spec、paper、Evidence Ledger 或旧 Definition 数值回退。

模型或单位/资源缺失立即拒绝。BLOCKED 统计只阻断 evaluate，信号仍可运行。
官方 likelihood 和一般反中微子 EFT 保持 BLOCKED。Task 04 不开放尚无包运行证据的 Fast profile。

## 最小共享接口修改与证据

首次新增测试真实失败，定位到两处接口问题：

1. snapshot 将 ResponseW 系数列表冻结为 tuple，旧矩阵识别函数只认 list。
   新 ArrayResponseW 仅恢复当前通道的容器并调用原 ResponseW.W_np，不复制/改变核响应数学。
2. 原 loader 按整份 NPZ/YAML 原始哈希构造物理指纹，统计修改也使物理身份变化。
   新可选 prepare.physics_resource_identity 提供按内容区分的物理投影；旧 adapter 继续原始哈希。
   原始文件哈希仍保存并由 validate_snapshot 检查，修改文件后必须重新加载。

runtime 增加可选 executor.default_point：让 package 的 include_sm 与 sin2thetaW 真正控制缺省
TheoryPoint；旧 executor 无此方法时保持旧逻辑。没有修改理论、Prediction 或 Statistics 数学合同。
所有既有文件修改前保存了 Task04 恢复点；Task03 新增数组适配器在本次持续实现中增量扩展。

## 实际验证

解释器：`F:/Work/.codex_conda_envs/codex-py311/python.exe -B`。

- `pytest tests/test_experiment_package_loader.py tests/test_physics_model_registry.py tests/test_input_package_schema.py -q`：**98 passed**。
- 两文件目录没有 MD；只解析两份显式资源；数组不可写；nu/antinu 标签保留。
- archive/array hash、绝对/越界路径、未知模型、资源缺失、stale、跳过验证均被拒绝。
- 只改统计数组：physics_fingerprint 完全相同，analysis_fingerprint 改变。
- 关闭 package include_sm 后空 BSM 预测精确为零，证明默认参数未被隐藏默认值覆盖。
- 小网格逐箱预测/近似统计与冻结内部基线一致，rtol=1e-10/1e-12；不是官方基准。

开发中一次比较使用了与冻结基线不同的测试网格；改为从原 GRIDS['small'] 引用，
没有改输入值、冻结数组或容差。其他实验/既有 Runtime 回归正在单独执行，结果追加于此。
尚未执行独立安装、默认网格收敛及 package-only Fast，不记 PASS。

默认 CsI2021 definition/registry 入口未切换，旧实验值仍只被旧入口使用；下一任务才切换为
本 Loader。Task 01 的历史 NOT_RUN 记录不被反向改写。

最终既有小网格/同预测统计及 CsI2017/Ar2020 冻结回归：**16 passed, 23 deselected**，
命令为 `pytest tests/test_refactor_csi2021_regression.py -k 'small or same_prediction or shared_coherent' tests/test_runtime_migration_contracts.py -q`；
该 -k 选择未运行不匹配的 runtime_migration 测试，不能声称覆盖全文件。
四份受影响 Markdown 的 64 个本地链接检查通过。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md) · [模型绑定](PHYSICS_MODEL_BINDING_REPORT.md)
