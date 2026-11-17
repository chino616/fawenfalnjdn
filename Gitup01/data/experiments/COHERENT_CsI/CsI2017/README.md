# CsI2017 input package

## 当前 Package 权威

The registered runtime now reads [experiment.input.yaml](experiment.input.yaml)
and [experiment.resources.npz](experiment.resources.npz). The deterministic
[experiment.physics.md](experiment.physics.md) is the human review view, not a
runtime input. The older spec, detector and statistics files below are retained
for historical provenance and explicit table audits; they no longer provide
default runtime parameters.

The package preserves the original fixed 251-node Slow PE grid, deterministic
PE mapping, bin-edge interpolation and approximate one-pull Gaussian statistics.
Its values are legacy-derived, DRAFT, human NOT_REVIEWED. Official likelihood,
general antineutrino EFT and scientific release remain BLOCKED. Dataset identity and related papers are indexed in the
[CsI2017 overview](../../../../docs/experiments/COHERENT/CsI2017/README.md).

[experiment.physics.md](experiment.physics.md) 使用现有共享 Renderer，
按本 dataset 输入选择物理说明、必要公式和简明资源索引；公共 matching/粒子响应不逐项展开。
现有 YAML/NPZ 和权限保持原样，报告可用既有 CLI 的 `--md-only` 只读输入重渲染；
见[package 编译器入口](../../../../tools/compile_experiment_package.py)。

## 保留文件的来源与用途

| 文件 | 来源、列定义和转换 | 当前用途 |
|---|---|---|
| [experiment.input.yaml](experiment.input.yaml) / [experiment.resources.npz](experiment.resources.npz) | 从项目既有 25 箱实现、源谱生成、核响应 JSON 和声明表提取；来源仍标为 `legacy`，不是独立官方确认 | 默认参数/模型与 28 份数组的权威输入 |
| [experiment.physics.md](experiment.physics.md) | 由正式 YAML/NPZ 渲染的说明；不是原始观测或额外参数源 | 人工阅读；本次未重渲染 |
| [experiment.yaml](experiment.yaml) | 旧 Phase 1 兼容规格；含原 PE 坐标、插值与阈值约定 | 兼容/历史说明，非默认 Runtime 输入 |
| [detector/COHERENT_eff.txt](detector/COHERENT_eff.txt) | 36×2：PE、无量纲效率；与下述固定提交同名文件数值及换行归一文本一致 | NPZ 的 `efficiency_energy/values` 分别与两列一致；默认不重读 TXT |
| [statistics/COHERENT_data.txt](statistics/COHERENT_data.txt) | 25×2：旧提取的 PE 横坐标、residual 计数（counts/bin，可负）；不是已验证的原始泊松观测 | NPZ `statistics_observed` 等于第 2 列 |
| [statistics/COHERENT_lower.txt](statistics/COHERENT_lower.txt) | 25×2：独立旧 PE 横坐标、下边界计数（counts/bin）；置信含义未经一手确认 | NPZ `statistics_lower` 等于第 2 列 |
| [statistics/COHERENT_upper.txt](statistics/COHERENT_upper.txt) | 25×2：独立旧 PE 横坐标、上边界计数（counts/bin）；不是已减去观测的误差值 | NPZ `statistics_upper` 等于第 2 列 |
| [statistics/COHERENT_spectrum.txt](statistics/COHERENT_spectrum.txt) | 25×2：旧 PE 横坐标、参考谱计数（counts/bin）；更早的图表/生成链未确认 | NPZ `statistics_spectrum` 等于第 2 列 |
| [statistics/provenance.yaml](statistics/provenance.yaml) | 原项目 `COHERENT_*.txt` / `cutoff_multi.py` 的统计解释、bin edges、pull 与限制 | 保留既有历史说明，未改写为官方 likelihood |

五份 `COHERENT_*.txt` 的公开对照来源是 Bradley Kavanagh [CEvNS 固定提交的 DataFiles](https://github.com/bradkav/CEvNS/tree/6adce961e769cfbf8edc9acef140ebac46009c36/DataFiles)，五份本地内容仅换行不同。这确认了同版公开表，不证明当年复制路径、数字化工程或官方原始图表。原始数字化/插值步骤及一手图号仍未知；[2017 官方数据释放](https://doi.org/10.5281/zenodo.1228631)作为独立核对入口，未声称这些 TXT 与之相同。

统计 TXT 各自的第一列不是共同 bin edges，不能当作彼此完全相同的箱中心；正式 edges 由 NPZ 声明。`statistics_uncertainty = max((upper-lower)/2, 1e-12)` 与既有数组逐值一致，本次未重新取点、插值、重分箱或改变统计定义。

## NPZ 的 28 个数组

| 数组组 | 个数、坐标/单位 | 来源与消费者 |
|---|---|---|
| `source_energy_MeV`, `source_fluence_1/2`, `rho_0/1/2` | 6；200 点 MeV；连续注量 `cm^-2 MeV^-1`；3×3 味态无量纲 | 原 SNS 代码生成后存入 Package；`integrated_fluence_components_v1` 消费。prompt 能量/积分权重在 YAML，不读 `datafiles/SNSflux_*.txt` |
| `nuclear_Cs133_*`, `nuclear_I127_*` | 14；七通道 × 两核素，`(p,n)` 2×2 升幂系数，无量纲 | 与现有 [responses_all.json](../../../responses/README.md) 的 Cs133/I 条目一致；由 Package 构造响应，外部源表/归一化仍未闭合 |
| `efficiency_energy`, `efficiency_values` | 2；PE、无量纲 | 与保留效率 TXT 两列一致；供表格效率模型 |
| `observable_edges` | 1；26 个 PE edges | 旧 25 箱坐标约定，供观测分箱 |
| `statistics_observed/lower/upper/spectrum/uncertainty` | 5；25 箱，counts/bin | 来自上述第 2 列及误差规则，供现有近似统计/参考用途 |

所有数组的原始哈希均与 YAML 声明一致；这不等于官方来源或统计语义通过科学审查。源表已经是运行期积分注量，不再重复乘 POT、运行时间或另一份绝对通量。

## 本地兼容文件缺口

`statistics/observation_schema.json` 在本地缺失，仍在 Registry 历史归属、Package 的 `provenance.declared_materials` 和保护记录中出现；它不是当前 `package_input/package_arrays` 的资源依赖。依赖该 schema 的旧表审阅/兼容分发不能宣称齐备。本次没有根据 TXT 猜测恢复 schema，也没有删除历史声明来掩盖缺口。

分析所用 ZIP 还漏装本地已存在的正式 YAML/NPZ；本地 Package 未缺失、未重建。后续重新分发应带齐这两个现有文件，并单独解决兼容 schema 的恢复或退出范围。

## 历史 Phase 1 说明（非当前 Runtime 状态）

以下保留早期阶段记录；其中阶段状态、待办和旧路径不构成当前验证或人工批准。

This directory is the Phase 1 runtime dataset specification for the existing
COHERENT CsI2017 reproduction path. It does not implement new experiment
physics.

### Identity and provenance

- Dataset: CsI2017
- Family: COHERENT CsI
- Source: stopped-pion SNS
- Target: equal-stoichiometry CsI using Cs-133 and I-127
- Historical run paths (currently missing; not current approval evidence):
  - workflows/experiment-integration/runs/CsI2017/00_INPUT_INVENTORY.md
  - workflows/experiment-integration/runs/CsI2017/00_IMPLEMENTATION_MANIFEST.yaml

### Observable and output contract

The true axes are incident energy in MeV and recoil energy in keV. The
reconstructed observable is PE. The output contains 25 PE bins for each source
component key mu, e, mub, plus total, with unit expected events per bin.

The PE edges are regular from 0.001 to 50.0 with width 1.99996.

### Statistical mode

The recorded mode is background_subtracted_excess. It is provisional and is
not used by the Flavor Slow migration. Statistics remains blocked pending
authoritative observed/background/covariance provenance.

### Implemented phase

DATASET_VALIDATED only. Existing Python registry behavior is unchanged.

### Pending modules

- Target text validation: Phase 2.
- Canonical SNS source states: Phase 3.
- Theory coverage report: Phase 4.
- Cross-section validation: Phase 5.
- Detector-response validation: Phase 6.
- Flavor-aware Slow counts: Phase 7.
- Fast counts: blocked until P4 Flavor contract.
- Statistics: blocked pending provenance.

### Known blockers

ANTI-NU AUDIT is required before changing interaction-kernel physics.
The 14.57/14.6 kg and physical/legacy prompt-energy differences remain explicit
reproduction conventions and are not resolved in Phase 1.

[数据集目录](../../README.md) · [data 总览](../../../README.md)

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| CsI2017：25PE箱确定性映射 | [Package v2 / legacy compatibility；处理方式](<../../../../docs/experiments/COHERENT/CsI2017/METHODS.md>) | [当前输入](<experiment.input.yaml>) | [最新核对结果](<../../../../outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
