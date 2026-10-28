# CEvNS-pyEFT

包名为 `cevns_pyeft`，源码位于项目根同名目录。四个已有实验通过统一入口加载、预测、评价。

```python
from cevns_pyeft.experiments.loader import load_experiment, ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

resources = ResourceCatalog("/absolute/path/to/Gitup01")  # 包含 data/ 的根
experiment = load_experiment("CsI2021", resources=resources)
prediction = predict_experiment(experiment)
fit = evaluate_experiment(experiment, prediction)
```

已有ID：`CsI2021`、`CsI2017`、`Ar2020`、`conus_plus_2025_c2c3c5_ge73_pyeft`。
`parameters=None` 使用各自标记的复现默认值，显式 TheoryPoint 优先。
统计数据延迟加载；物理预测不要求先具备统计输入。

## 安装与使用

```powershell
python -m pip install -e .
python -m pytest -q tests --basetemp=.pytest-tmp/local
python examples/experiment_modularization/run_experiments.py --resources . --selection configs/analysis_selection.example.yaml
```

wheel只含运行时包；安装后必须通过 ResourceCatalog 指定外部数据根，不依赖cwd。
旧导入名和旧计数返回键保留。旧统计/spec入口使用明确的资源根及有限兼容映射。

- [文档索引](docs/README.md)
- [接口、启停和组件替换](docs/USAGE.md)
- [目录与历史恢复](docs/LAYOUT.md)
- [实验资源说明](data/README.md)
- [参数归属](docs/PARAMETER_OWNERSHIP.md)
- [能力矩阵](docs/CAPABILITY_MATRIX.md)
- [实际验证与限制](docs/VALIDATION.md)

每个实验的定义决定默认源、曝光、靶材、响应、分箱与数值策略；共用材料属于中立模块。
不同算法保留各自网格和物理约定，不把接口统一解释为全部后端具有相同能力。
CONUS+默认357kg·day预测与effective119数字化统计配置严格区分；后者是近似Gaussian，
不是官方on/off likelihood。本轮未更改科学Gate、天然/单核素假设或任何受保护参考。
