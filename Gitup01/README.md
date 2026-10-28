# CEvNS-pyEFT 接口重构

本目录是用户提供的 `261028Gitup1-CONUS-3/Gitup01` 项目。当前重构聚焦模块化与接口：CsI2021 一维 9 箱使用组合式模型、通用 Slow/Fast、内容指纹缓存及统一统计适配，并保留旧 API 和原有物理约定。使用方式见 [组合式接口](docs/interface_refactor/README.md) 和 [Fast 与缓存](docs/interface_refactor/FAST_AND_CACHE.md)，最新验证见 [R4–R6 实施报告](docs/interface_refactor/R4_R6_REPORT.md)。[R0–R3 报告](docs/interface_refactor/R0_R3_REPORT.md) 保留第一阶段的验收事实。

## 目录与职责

| 路径 | 内容 |
| --- | --- |
| `src/cevns_pyeft/foundation` | 常量、单位约定 |
| `src/cevns_pyeft/contracts` | 单位、坐标、曝光、核数、截面、观测及预测合同 |
| `src/cevns_pyeft/theory` | 运动学、Helm、Li2026 EFT 理论与振幅 |
| `src/cevns_pyeft/nuclear` | 核响应数据库接口 |
| `src/cevns_pyeft/sources`、`propagation` | 源态、味结构、传播接口 |
| `src/cevns_pyeft/targets`、`detectors` | 材料到核数、探测器响应、效率与选择 |
| `src/cevns_pyeft/rates`、`kernels` | 微分率、计数和 Fast 核构建、存储、重构 |
| `src/cevns_pyeft/statistics` | 数据、似然、参数、扫描、置信区间 |
| `src/cevns_pyeft/experiments` | 注册接口、实验配置、COHERENT 和 CONUS+ 实现 |
| `src/cevns_pyeft/core`、`cli.py` | 模型组装、统一 predict 入口及旧 engine 兼容 |
| `data`、`schemas` | 实验输入、核响应、统计基准、数据契约 |
| `tests` | 原有测试、冻结的修改前参考及新增接口回归 |
| `tools` | CONUS+ 重现、出图与配置核查脚本 |
| `workflows/experiment-integration` | 实验接入规则、模板和已有诊断记录 |
| `docs` | 论文、约定审计、参考资料和接入材料 |
| `论文图NoteBook` | Notebook、绘图脚本、数值结果和验证记录 |
| `outputs` | 已有 CONUS+ 产物，以及 `refactor/` 中的接口验证、模型描述和变更差异 |

## 使用

在本目录运行，建议使用独立 Python 3.11 或更新版本环境：

```powershell
python -m pip install -e .
python -m pip install pytest
python -m pytest
cevns-pyeft
```

不安装包时，可先设置当前进程的模块路径：

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -B -m cevns_pyeft.cli
```

`data` 是外置资源，不收入 wheel。旧接口与部分历史测试仍应从 `Gitup01` 目录运行；新的 `load_experiment(..., resources=ResourceCatalog(外置数据根))` 支持安装 wheel 后从项目外目录调用。

## 按实验选择和替换

四个既有数据集现分别有独立定义文件：
`experiments/coherent/{csi2021,csi2017,ar2020}_definition.py` 与
`experiments/conus_plus/definition.py`。统一使用 `load_experiment`、
`predict_experiment`、`evaluate_experiment`；通过 selection 配置的 enabled 增减本次计算。
完整例子、资源根设置、参数替换与各实验的 Fast/统计边界见
[独立实验使用说明](docs/experiment_modularization/USAGE.md)、
[参数归属表](docs/experiment_modularization/PARAMETER_OWNERSHIP.md) 和
[能力矩阵](docs/experiment_modularization/CAPABILITY_MATRIX.md)。
旧 `get_experiment` 返回字典的合同保留。

## 基线和限制

- `outputs` 中的数值基线、Fast 基定义，以及 `workflows/.../runs` 中的诊断文件已保留；`tools/conus/run_conus_completion.py` 会读取这些文件。
- CONUS+ 现有 Fast 产物是探测器响应矩阵；完整 114 实坐标 EFT 二次核仍待构建和验证。
- CONUS+ 论文统计对照采用 19 点数字化数据的高斯近似，尚不具备官方似然和电子反冲部分。
- 更多既有结论见 [README_FINAL.md](README_FINAL.md)、[FINAL_STATUS.md](FINAL_STATUS.md)、[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)。这些是复制前的交付状态，不代表本次重新执行了全部历史计算。
- 参考资料中的原始来源路径和历史验证记录保持原样，属于溯源信息；本次清理不将其改写成新的运行记录。

## 8B 参考资料

`docs/8B/cevns_data_release-sr0_sr1_sr2.zip` 完整保留。其 6,930 个文件已与旧目录中的解压版本逐文件校验，完全一致，新目录省去了这份重复解压副本。需要使用参考资料中的原解压路径时，可在本目录执行：

```powershell
Expand-Archive -LiteralPath .\docs\8B\cevns_data_release-sr0_sr1_sr2.zip -DestinationPath .\docs\8B\cevns_data_release-sr0_sr1_sr2
```

这些资料不会自动成为已注册的物理输入；实验接入仍遵循 `AGENTS.md` 的现有规则。
