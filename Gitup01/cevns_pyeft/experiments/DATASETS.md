# Dataset 注册、安装状态与文件归属

本表由唯一 dataset_registry.json 生成；管理操作在同一事务中同步。
installed 与 active 分别表示文件是否安装、是否可默认加载。科学输入与能力的批准由原接入流程管理。

| 实验分组 | dataset ID | 状态 | 已安装 | 版本 | definition | 独占文件 |
|---|---|---|---|---|---|---|
| COHERENT_CsI | CsI2021 | active | True | 1.0.0 | [coherent.csi2021_definition](coherent/csi2021_definition.py) | 7 |
| COHERENT_CsI | CsI2017 | active | True | 1.0.0 | [coherent.csi2017_definition](coherent/csi2017_definition.py) | 12 |
| COHERENT_Ar | Ar2020 | active | True | 1.0.0 | [coherent.ar2020_definition](coherent/ar2020_definition.py) | 5 |

## 各实验的文件与共享依赖

### CsI2021

独占文件：

- [cevns_pyeft/experiments/coherent/csi2021_definition.py](coherent/csi2021_definition.py) — code
- [cevns_pyeft/experiments/coherent/slow_counts_csi2021.py](coherent/slow_counts_csi2021.py) — code
- [cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py](coherent/fast_kernel_csi2021.py) — code
- [cevns_pyeft/experiments/coherent/csi2021.py](coherent/csi2021.py) — code
- [data/experiments/COHERENT_CsI/CsI2021/experiment.yaml](../../data/experiments/COHERENT_CsI/CsI2021/experiment.yaml) — data
- [data/experiments/COHERENT_CsI/CsI2021/README.md](../../data/experiments/COHERENT_CsI/CsI2021/README.md) — documentation
- [data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml](../../data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml) — data

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/csi2021.py`
- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/compiler.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/rates/folding.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/sources/sns.py`
- `cevns_pyeft/targets/materials.py`
- `cevns_pyeft/theory/li2026/amplitude.py`
- `cevns_pyeft/theory/li2026/operators.py`
- `cevns_pyeft/theory/li2026/responses.py`
- `data/responses/responses_all.json`

依赖的其他 dataset：无。

### CsI2017

独占文件：

- [cevns_pyeft/experiments/coherent/csi2017_definition.py](coherent/csi2017_definition.py) — code
- [cevns_pyeft/experiments/coherent/slow_counts_csi2017.py](coherent/slow_counts_csi2017.py) — code
- [cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py](coherent/fast_kernel_csi2017.py) — code
- [data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt](../../data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt) — data
- [data/experiments/COHERENT_CsI/CsI2017/experiment.yaml](../../data/experiments/COHERENT_CsI/CsI2017/experiment.yaml) — data
- [data/experiments/COHERENT_CsI/CsI2017/README.md](../../data/experiments/COHERENT_CsI/CsI2017/README.md) — documentation
- [data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_data.txt](../../data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_data.txt) — data
- [data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_lower.txt](../../data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_lower.txt) — data
- [data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_spectrum.txt](../../data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_spectrum.txt) — data
- [data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_upper.txt](../../data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_upper.txt) — data
- [data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json](../../data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json) — data
- [data/experiments/COHERENT_CsI/CsI2017/statistics/provenance.yaml](../../data/experiments/COHERENT_CsI/CsI2017/statistics/provenance.yaml) — data

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/targets/materials.py`
- `cevns_pyeft/theory/li2026/amplitude.py`
- `cevns_pyeft/theory/li2026/operators.py`
- `cevns_pyeft/theory/li2026/responses.py`
- `data/responses/responses_all.json`

依赖的其他 dataset：无。

### Ar2020

独占文件：

- [cevns_pyeft/experiments/coherent/ar2020_definition.py](coherent/ar2020_definition.py) — code
- [cevns_pyeft/experiments/coherent/slow_counts_ar2020.py](coherent/slow_counts_ar2020.py) — code
- [cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py](coherent/fast_kernel_ar2020.py) — code
- [data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt](../../data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt) — data
- [data/experiments/COHERENT_Ar/Ar2020/statistics/provenance.yaml](../../data/experiments/COHERENT_Ar/Ar2020/statistics/provenance.yaml) — data

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/targets/materials.py`
- `cevns_pyeft/theory/li2026/amplitude.py`
- `cevns_pyeft/theory/li2026/operators.py`
- `cevns_pyeft/theory/li2026/responses.py`
- `data/responses/responses_all.json`

依赖的其他 dataset：无。

[管理命令与恢复](MANAGEMENT.md) · [实验代码说明](README.md)
