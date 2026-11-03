# CEvNS-pyEFT：从实验定义到事件数

本项目用 Python 计算相干弹性中微子–原子核散射（CEvNS）。当前可通过统一接口加载的实验是 **CsI2021、CsI2017、Ar2020**；活动清单由 [manifest.py](cevns_pyeft/experiments/manifest.py) 管理。实验文档集中介绍这三个 COHERENT 数据集。

## 先跑通一次计算

需要 Python 3.11 及以上版本。以下安装和命令均在 `Gitup01` 根目录执行，`python` 应指向安装本项目依赖的解释器：

```powershell
python -m pip install -e .
python examples/experiment_modularization/run_experiments.py --resources .
```

示例实际调用三个实验的预测接口；CsI2021 还会输出近似 χ²，并演示将 POT 加倍。它使用小积分网格检查接口，不代表数值已经收敛。等价的单实验入口如下，也从根目录运行：

```python
from pathlib import Path
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

resources = ResourceCatalog(Path.cwd())  # 必须是包含 data/ 的目录
experiment = load_experiment("CsI2021", resources=resources)
prediction = predict_experiment(
    experiment, numerics={"n_er": 5, "n_enu": 12, "n_pe_bin": 3}
)
fit = evaluate_experiment(experiment, prediction)
print(prediction.counts.shape)  # (9,)，每箱事件数
print(prediction.combined_prediction.unit)  # events/bin
print(fit.chi2)  # 当前实验绑定的近似统计模型
```

`parameters=None` 使用实验定义中的复现默认值；显式传入 `TheoryPoint` 时以调用方参数为准。`cevns-pyeft` 命令对应 [cli.py](cevns_pyeft/cli.py)，目前只打印版本，计算应使用上面的 Python API 或示例脚本。

## 代码实际怎样运行

```text
dataset_id + ResourceCatalog
  → experiments/catalog.py：从 manifest 找到活动定义
  → experiments/loader.py：解析物理资源，definition.prepare 装配 model/executor
  → experiments/runtime.py：predict_experiment 校验参数并调用 executor
      CsI2021 → core/predict.py → rates/recoil.py → rates/folding.py
      CsI2017 / Ar2020 → coherent/ 下各自的 Slow 或 legacy Fast 执行器
  → ExperimentPrediction：每箱计数、轴、分量和实际运行记录
  → evaluate_experiment：加载统计输入、核对身份并计算近似 χ²
```

相互作用计算还会进入 `theory/li2026/` 和 `nuclear/`：Wilson 系数匹配到核子系数，粒子响应 R 与核响应 W 收缩为味空间核，再与入射密度矩阵收缩。源注量、真实核数、探测器效率在后续层加入，避免同一个归一化因子被重复计算。

| 实验 | 实际预测路径 | Fast 和统计边界 |
|---|---|---|
| CsI2021 | 9 个 PE 箱；组合式模型、gamma 响应与效率折叠 | `interface_kernel_v1`；评价时由 events/bin 除一次箱宽得到 counts/PE，使用近似 Gaussian |
| CsI2017 | 25 个箱；固定 251 个 PE 节点的确定性映射 | legacy Fast；Slow 仅接受 `n_enu`；外部观测表、近似 Gaussian |
| Ar2020 | 12 个箱；sigma 依赖观测值的专用 Gaussian 折叠 | legacy Fast；Slow 不接受 `pe_step`；非对称 IRLS |

统一入口保留了这些算法差异。CsI2017/Ar2020 的 legacy Fast 不支持任意组件替换；CsI2021 的组合式 Fast 要求可用的双线性系数表示和固定、与扫描参数无关的入射态。详见[能力矩阵](docs/user-guide/capability-matrix.md)。

## 为什么分成这些目录

| 目录 | 在实际运行中的职责 | 这样拆分的原因 |
|---|---|---|
| [cevns_pyeft/](cevns_pyeft/README.md) | 被 Python 导入的实现，包括实验装配、物理、积分、缓存、统计 | 算法可以复用，实验的默认参数和专用策略仍有明确归属 |
| [data/](data/README.md) | 由定义中的 `ResourceRef` 指定并经 `ResourceCatalog` 解析的输入 | 数据根可独立于源码和安装位置；资源变动能通过哈希追踪 |
| [configs/](configs/README.md) | `load_selection` 读取本次启用的实验、后端和数值设置 | 本次运行选择与实验的物理默认定义分开 |
| [examples/](examples/README.md) | 调用公共接口的运行脚本与 synthetic 扩展示例 | 用户从最小调用学习，不必从旧兼容接口拼接流程 |
| [tests/](tests/README.md) | 核对接口、单位、组件替换、冻结数值和缓存失效 | 工程重构需要证明旧结果没有被意外改写 |
| [tools/](tools/README.md) | 构建、资源审计、文档检查和实验脚手架 | 这些操作有文件读写或管理职责，不进入每次物理预测 |
| [schemas/](schemas/README.md) | 实验说明和 CSV 格式的声明 | 格式约定可独立阅读；实际入口是否执行验证由消费者代码决定 |
| [docs/](docs/README.md) | 使用方法、物理约定、架构和 COHERENT 科学审查 | 当前接口说明、科学待核实问题和实验研究结果分开管理 |
| [workflows/](workflows/README.md) | 人与工具协作的接入流程、授权记录和结构 QA | 审核流程不被运行时导入，也不作为物理数据源 |
| [outputs/](outputs/README.md) | 本地运行报告、缓存、构建记录和历史重构证据 | 结果与输入分开，loader 不会把旧输出当成当前实验数据 |
| [论文图NoteBook/](论文图NoteBook/README.md) | 调用现有计算接口生成论文图、表格和数值检查 | 绘图风格、展示网格和研究输出不混入物理公式 |

根目录的 [pyproject.toml](pyproject.toml) 管理包名、依赖、`cevns-pyeft` 命令和包发现；[requirements.txt](requirements.txt) 提供运行依赖列表；[AGENTS.md](AGENTS.md) 规定仓库维护边界。wheel 的包发现限定为 `cevns_pyeft*`，外置 `data/` 需另行提供，不能依赖当前工作目录自动搜索。

## 新增文件放在哪里，怎样接入

| 要新增的内容 | 创建位置与接入方法 |
|---|---|
| 通用物理公式或算法 | 放入 `cevns_pyeft/theory/`、`rates/`、`detectors/` 等对应职责目录，由调用方显式导入；添加文件本身不会改变预测路径 |
| 某实验的默认参数或专用算法 | 放入 `cevns_pyeft/experiments/<实验族>/`，通过 `ExperimentDefinition.prepare` 绑定 model/executor，避免在通用积分层增加实验名分支 |
| 新的真实数据集 | 先按[实验接入入口](workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)明确数据和物理范围；代码、数据、说明、测试分别进入对应目录。先用 custom catalog 验证，正式激活时维护 `experiments/manifest.py` |
| 新数据文件 | 放入 `data/experiments/<实验族>/<dataset_id>/` 的相应子目录；声明资源 ID、role、路径、坐标/单位、来源，并维护资源清单；单放一个 CSV 不会被加载 |
| 新运行组合 | 参照 `configs/analysis_selection.example.yaml` 创建配置，显式传给 `load_selection` 或示例脚本的 `--selection` |
| 新使用示例、测试或说明 | 分别放入 `examples/`、`tests/test_*.py`、`docs/` 对应分类，并从该目录 README 增加入口 |
| 新报告、缓存或图表 | 放入新的 `outputs/<任务或运行>/`，或绘图脚本指定的输出目录，记录生成入口和参数，不覆盖历史验收证据 |

每个一级、二级目录的 README 进一步说明文件归属、真实消费者、创建步骤及应检查的行为。新增模块若需要包级导出，还需维护相应 `__init__.py`；并不存在“扫描所有新文件自动启用”的插件机制。

## 修改后如何检查

从根目录运行与改动相关的检查：

```powershell
python -m pytest -q tests --basetemp=.pytest-tmp/local
python tools/validate_resource_manifest.py --root .
python tools/validate_docs.py --scope docs
```

共享理论、核响应、积分或 Fast 的改动需要覆盖三个已有实验的回归；不能通过改写冻结数组或放宽容差获得通过。新增 README 也属于历史工作流保护清单的文件管理范围，具体见 [tools/workflow_validation](tools/workflow_validation/README.md)。

当前保留的[反中微子审计](docs/physics/physics-audits/antineutrino_sign_helicity_audit.md)和[核响应源表审计](docs/physics/nuclear-responses/nuclear_response_convention_audit.md)仍有未闭合问题。COHERENT 科学审查中的历史结果按报告当时的代码和环境解释。
