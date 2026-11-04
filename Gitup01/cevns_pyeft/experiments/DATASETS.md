# Dataset 注册、安装状态与文件归属

本表由唯一 dataset_registry.json 生成；管理操作在同一事务中同步。
installed 与 active 分别表示文件是否安装、是否可默认加载。科学输入与能力的批准由原接入流程管理。

| 实验分组 | dataset ID | 状态 | 已安装 | 版本 | definition | 独占文件 |
|---|---|---|---|---|---|---|
| COHERENT_CsI | CsI2021 | active | True | 2.0.0 | [coherent.csi2021_definition](coherent/csi2021_definition.py) | 12 |
| COHERENT_CsI | CsI2017 | active | True | 2.0.0 | [coherent.csi2017_definition](coherent/csi2017_definition.py) | 15 |
| COHERENT_Ar | Ar2020 | active | True | 2.0.0 | [coherent.ar2020_definition](coherent/ar2020_definition.py) | 9 |

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
- [cevns_pyeft/experiments/coherent/csi2021_package.py](coherent/csi2021_package.py) — code
- [cevns_pyeft/experiments/coherent/csi2021_package_contract.json](coherent/csi2021_package_contract.json) — data
- [data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml](../../data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml) — data
- [data/experiments/COHERENT_CsI/CsI2021/experiment.resources.npz](../../data/experiments/COHERENT_CsI/CsI2021/experiment.resources.npz) — data
- [data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md](../../data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md) — documentation

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/coherent.py`
- `cevns_pyeft/detectors/csi2021.py`
- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/experiments/component_bindings.json`
- `cevns_pyeft/experiments/generic_input.py`
- `cevns_pyeft/experiments/generic_input.schema.json`
- `cevns_pyeft/experiments/input_package.py`
- `cevns_pyeft/experiments/input_package.schema.json`
- `cevns_pyeft/experiments/model_bindings.json`
- `cevns_pyeft/experiments/model_registry.py`
- `cevns_pyeft/experiments/package_compatibility.py`
- `cevns_pyeft/experiments/package_components.py`
- `cevns_pyeft/experiments/package_loader.py`
- `cevns_pyeft/experiments/package_profiles.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/compiler.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/kernels/storage.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/rates/folding.py`
- `cevns_pyeft/rates/legacy_observables.py`
- `cevns_pyeft/rates/recoil.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/sources/sns.py`
- `cevns_pyeft/statistics/profiling.py`
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
- [data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml](../../data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml) — data
- [data/experiments/COHERENT_CsI/CsI2017/experiment.resources.npz](../../data/experiments/COHERENT_CsI/CsI2017/experiment.resources.npz) — data
- [data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md](../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md) — documentation

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/coherent.py`
- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/experiments/component_bindings.json`
- `cevns_pyeft/experiments/generic_input.py`
- `cevns_pyeft/experiments/generic_input.schema.json`
- `cevns_pyeft/experiments/input_package.py`
- `cevns_pyeft/experiments/input_package.schema.json`
- `cevns_pyeft/experiments/model_bindings.json`
- `cevns_pyeft/experiments/model_registry.py`
- `cevns_pyeft/experiments/package_compatibility.py`
- `cevns_pyeft/experiments/package_components.py`
- `cevns_pyeft/experiments/package_loader.py`
- `cevns_pyeft/experiments/package_profiles.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/kernels/storage.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/rates/folding.py`
- `cevns_pyeft/rates/legacy_observables.py`
- `cevns_pyeft/rates/recoil.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/statistics/profiling.py`
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
- [data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml](../../data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml) — data
- [data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz](../../data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz) — data
- [data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md](../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md) — documentation
- [data/experiments/COHERENT_Ar/Ar2020/README.md](../../data/experiments/COHERENT_Ar/Ar2020/README.md) — documentation

共享依赖（卸载本项时保留）：

- `cevns_pyeft/detectors/coherent.py`
- `cevns_pyeft/detectors/legacy_parameters.py`
- `cevns_pyeft/experiments/coherent/execution.py`
- `cevns_pyeft/experiments/coherent/sns.py`
- `cevns_pyeft/experiments/component_bindings.json`
- `cevns_pyeft/experiments/generic_input.py`
- `cevns_pyeft/experiments/generic_input.schema.json`
- `cevns_pyeft/experiments/input_package.py`
- `cevns_pyeft/experiments/input_package.schema.json`
- `cevns_pyeft/experiments/model_bindings.json`
- `cevns_pyeft/experiments/model_registry.py`
- `cevns_pyeft/experiments/package_compatibility.py`
- `cevns_pyeft/experiments/package_components.py`
- `cevns_pyeft/experiments/package_loader.py`
- `cevns_pyeft/experiments/package_profiles.py`
- `cevns_pyeft/kernels/builder.py`
- `cevns_pyeft/kernels/reconstruction.py`
- `cevns_pyeft/kernels/storage.py`
- `cevns_pyeft/nuclear/response.py`
- `cevns_pyeft/rates/counts.py`
- `cevns_pyeft/rates/differential.py`
- `cevns_pyeft/rates/folding.py`
- `cevns_pyeft/rates/legacy_observables.py`
- `cevns_pyeft/rates/recoil.py`
- `cevns_pyeft/sources/legacy_parameters.py`
- `cevns_pyeft/statistics/profiling.py`
- `cevns_pyeft/targets/materials.py`
- `cevns_pyeft/theory/li2026/amplitude.py`
- `cevns_pyeft/theory/li2026/operators.py`
- `cevns_pyeft/theory/li2026/responses.py`
- `data/responses/responses_all.json`

依赖的其他 dataset：无。

[管理命令与恢复](MANAGEMENT.md) · [实验代码说明](README.md)
