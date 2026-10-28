# 使用独立实验定义

本轮运行入口位于 `cevns_pyeft.experiments`。四个正式 ID 为
`CsI2021`、`CsI2017`、`Ar2020`、`conus_plus_2025_c2c3c5_ge73_pyeft`。
分别由 `coherent/csi2021_definition.py`、`coherent/csi2017_definition.py`、
`coherent/ar2020_definition.py`、`conus_plus/definition.py` 管理。
源、曝光、质量、响应、效率、分箱、数值策略和统计绑定均从这些定义装配。
共用材料/理论公式和校准资源继续复用。

```python
from cevns_pyeft.experiments.loader import load_experiment, ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

resources = ResourceCatalog(r"F:\Work\2026-07-15 CEvNSpyEFT-Local\261028Gitup1-CONUS-3\Gitup01")
experiment = load_experiment("CsI2021", resources=resources)
prediction = predict_experiment(experiment)
fit = evaluate_experiment(experiment, prediction)
```

`prediction.counts` 为 events/bin；观测单位在 `prediction.combined_prediction.axes`。
`detector_predictions` 始终使用有名键；CONUS+ 为 C2/C3/C5，每项19箱，合计也是19箱。
不会把探测器轴当成源分量轴，也不会自动合并不同实验的观测或 chi²。

`parameters=None` 使用定义中明确记录的复现弱混合角：COHERENT .2387、CONUS+ .23857。
显式 `TheoryPoint` 优先。数值默认值来自各实验 definition；`numerics` 只接受当前策略
真正消费的键。CsI2017 Slow 固定251个PE点，只接受 `n_enu`；Fast 的 `n_er` 则真正控制
PE网格。Ar2020拒绝无效的 `pe_step`。示例使用小网格，只验证接口，不代表科学收敛。

## 启停和替换

复制 `analysis_selection.example.yaml`，修改 `enabled` 即可增减本次计算对象。
该文件仅允许 `datasets` 列表、`id/enabled/backend/numerics` 和数值键的 block mapping。
内联对象、标签、执行表达式、未知字段、重复键和重复别名均拒绝。
不调用旧的简化 `experiment.yaml` 解析器，也不执行任意导入。

```python
from cevns_pyeft.experiments.selection import load_selection
from cevns_pyeft.experiments.runtime import predict_selection
results = predict_selection(load_selection("analysis_selection.example.yaml"), resources=resources)
```

禁用项仅核对声明，不解析文件、不构造模型、不编译核、不参与统计。
启用项缺少资源时，错误给出逻辑资源 ID 与实际路径。统计资源只在评价时读取；
缺少统计文件仍能计算物理预测。

通过 `dataclasses.replace` 修改一个定义实例，再传给 `load_experiment(..., definition=...)`。
不要改 `SNS_DATASETS` 全局字典来设置新实例。资源位置通过
`ResourceCatalog(root, overrides={"responses":path, "efficiency":path})` 覆盖。
资源内容改变会使现有实例失效，须重新加载；内容相同而位置不同不会改变物理核身份。
统计资源的根/定位参与分析身份，统计数组/误差变化不改变物理核。

可复制的演示见 `examples/experiment_modularization/run_experiments.py`；
新增 synthetic 数据集和解析结果见同目录 `synthetic_dataset.py`。该示例只通过
`ExperimentCatalog(...).register(...)` 注入，未加入正式实验目录。

## Fast

`compile_experiment(experiment,numerics=...)` 编译对应实验实际具备的表示；
`predict_experiment(...,backend="fast",kernel=kernel,numerics=...)` 检查兼容性后重构。
没有传 kernel 时显式 fast 会构建核。`auto` 没有缓存时选择 Slow 并记录原因。

- CsI2021：`interface_kernel_v1`，使用现有全物理依赖指纹，持久化用
  `kernels.interface_storage.save_compiled_kernel/load_compiled_kernel`。
- CsI2017 / Ar2020：保留 `channel_resolved_full_li2026` 兼容表示，附加本实例
  的内容/实现/数值绑定。持久化仍用 `kernels.storage.save_fastscan_template/load_fastscan_template`。
  旧核没有这种绑定时只走原兼容入口，不能假装消费新的物理覆盖。
- CONUS+：`detector_response_matrix`，仅缓存曝光×重构概率×反冲求积权重，
  每个理论点仍计算源/微分率；持久化用实验 `fast_kernel` 中的 save/load 函数。
  自定义响应时，保存和读取都传 `settings=experiment.definition.physical`；自定义分箱也传 edges。

## 统计边界

COHERENT保持现有近似统计；CsI2021 events/bin只除一次箱宽转counts/PE。
Ar2020历史轴/响应单位约定保留，未借本次重构重新解释。
CONUS+ digitized Gaussian benchmark 是独立的 effective119、C3类160eVee响应配置，
不是默认三探测器357kg·day预测的观测。评价默认配置明确拒绝。
使用该既有基准必须显式选择 C2=0、C3=119、C5=0 kg·day，并保持原响应/分箱/源/核数约定。
当前标准 data 路径缺少 digitized CSV，评价会明确报缺失，不阻断预测。
本项目既有观测位于
`outputs/conus-plus-completion-20261012/statistics/approximate_paper_benchmark/observations_digitized_approx.csv`。
使用者可显式设置 `ResourceCatalog(root, overrides={"observations":该文件绝对路径})`，
或提供自己的完整外置资源根；不会自动扫描 workflow 或从历史输出猜测输入。
统计只消费一次 combined_prediction，不为三个探测器复制观测。
所有结果仍是工程复现/近似，未升级为官方似然或科学批准。
