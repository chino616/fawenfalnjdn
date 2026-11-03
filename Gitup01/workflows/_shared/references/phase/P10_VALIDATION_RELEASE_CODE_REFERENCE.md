# P10 当前接入权威与验证边界

配合 [P10 模板](../../templates/phase/P10_VALIDATION_RELEASE_TEMPLATE.md)。

| 可审计锚点 | 验收对象 |
|---|---|
| `cevns_pyeft/experiments/manifest.py::BUILTIN_MANIFEST` | 内建活动/spec_only/archived 身份权威 |
| `cevns_pyeft/experiments/catalog.py::ExperimentCatalog` | 自定义与内建 definition 查找、别名、生命周期 |
| `cevns_pyeft/experiments/loader.py::ResourceCatalog` | 明确的 data 根、资源作用域与解析 |
| `cevns_pyeft/experiments/loader.py::load_experiment` | 装配 definition、model/executor 与快照 |
| `cevns_pyeft/experiments/runtime.py::predict_experiment` | 实际前向能力与输出身份 |
| `cevns_pyeft/experiments/runtime.py::evaluate_experiment` | 实际统计绑定与输入身份 |
| `cevns_pyeft/experiments/registry.py::get_slow_count_function` | 旧 callable 兼容视图，不是新增实验的唯一接入点 |

源码：[catalog](../../../../cevns_pyeft/experiments/catalog.py)、
[loader](../../../../cevns_pyeft/experiments/loader.py)、
[runtime](../../../../cevns_pyeft/experiments/runtime.py)。

新实验先用 ExperimentCatalog(builtins=False) 注册候选 definition 并显式传入 loader。
完成实际能力验证后，再在有效科学接受和写入授权下处理正式 manifest。
旧 registry 的默认 metadata discovery 可包含 spec；有 YAML 或 callable 不等于科学验收通过。
新 runtime definition 不必实现旧 SNS 兼容接口。

## 只读身份示例

从项目根目录执行。只证明当前活动集合一致，不代表任一科学复现等级。

```python
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG, ExperimentCatalog
from cevns_pyeft.experiments.manifest import manifest_entries

active = {entry.dataset_id for entry in manifest_entries(status="active")}
assert active == set(BUILTIN_CATALOG.ids())
assert not ExperimentCatalog(builtins=False).ids()
print(sorted(active))
```

验收矩阵分开记录：
1. 软件能力：能否 load/predict/compile/evaluate、unsupported 是否明确拒绝。
2. 数值与科学证据：内部一致性、旧程序回归、论文 forward、官方 likelihood。
3. 接受与发布：有效人工决定、实际写入范围、正式验证和最终声明。

可选能力未请求只影响对应栏；未满足原目标必须报告部分完成。
参考路径先确认存在、版本和条件，再执行比较，不能把配置中的路径当作通过证据。
相关测试：[生命周期与迁移合同](../../../../tests/test_runtime_migration_contracts.py)、
[实验归档隔离](../../../../tests/test_experiment_archive_isolation.py)。
