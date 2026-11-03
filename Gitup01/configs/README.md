# configs：本次分析运行哪些实验

[analysis_selection.example.yaml](analysis_selection.example.yaml) 是当前配置示例，由 [load_selection](../cevns_pyeft/experiments/selection.py) 解析，再交给 [predict_selection](../cevns_pyeft/experiments/runtime.py)。配置选择已有实验，不负责定义新物理模型。

从项目根目录、使用已安装本包的解释器运行：

```powershell
python examples/experiment_modularization/run_experiments.py --resources . --selection configs/analysis_selection.example.yaml
```

脚本将各启用实验的计数按 ID 输出为 JSON。当前示例启用 CsI2021、Ar2020，禁用 CsI2017；不会把不同箱轴的数组或 χ² 自动合并。

## 字段怎样影响代码

每条 dataset 配置支持 `id`、`enabled`、`backend`、`numerics`。ID/别名由 Catalog 检查；禁用项只核对声明；数值键最终由 `resolve_numerics` 对照该实验/后端的 profile 检查。CsI2017 Slow 只接受 `n_enu`，Ar2020 Slow 不消费 `pe_step`，未知键会报错。

当前 YAML 解析只支持文档化的 block 结构，不执行 import，也不提供通用 YAML 的任意对象构造。物理默认值、资源和统计定义仍在实验 definition。

## 管理与新增文件

复制示例为 `configs/<分析名称>.yaml`，编辑本次选择，并通过 `--selection` 或 `load_selection(path)` 显式传入；目录中新增文件不会自动成为默认配置。资源根由 `--resources`/`ResourceCatalog` 单独指定。

新增配置前确认每个 ID 已可加载、所选后端和数值键被实际执行器支持。若要改变曝光、效率或理论点，使用 definition/components/parameters 接口，不在 YAML 中虚构未支持字段。参考 [test_experiment_modularization.py](../tests/test_experiment_modularization.py) 中 selection 的未知键、重复别名和禁用资源测试。

---

[上一级](../README.md)
