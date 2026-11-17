# CsI2021 dataset specification

## Canonical input contract v1 (Task 02)

The three files below now use `cevns-experiment-input/1`, with the original
105 values and all 23 arrays unchanged. Each scalar has an audited role,
consumer and fingerprint scope; derived target quantities are read-only,
and the normalized continuum arrays record their generation dependencies.
The Physics MD is re-rendered from that same contract. Scientific status
remains DRAFT/PARTIAL. The default nine-bin runtime now reads YAML/NPZ through
the [package loader](../../../../cevns_pyeft/experiments/package_loader.py).

Run `python -B tools/validate_experiment_input.py data/experiments/COHERENT_CsI/CsI2021`
from the project root with the `validation` optional dependency installed.
See the [formal input schema](../../../../cevns_pyeft/experiments/input_package.schema.json).
The old `experiment.yaml` is explicitly legacy-compatible; it no longer
grants a current package Fast/statistics approval. Python definition/default
modules are compatibility views of the package and contain no independent
experimental parameter database. Internal regression, Fast scope and standalone validation are separate claims.

## 当前文件与数组的来源核对（2026-11-06）

| 保留文件 | 来源与用途 |
|---|---|
| [experiment.input.yaml](experiment.input.yaml) | 项目既有九箱实现提取的模型、参数、来源定位和数组声明；当前机器权威，科学状态仍为 DRAFT/PARTIAL |
| [experiment.resources.npz](experiment.resources.npz) | 23 个正式数组；与 YAML 逐项哈希一致；默认 Runtime 读取 |
| [experiment.physics.md](experiment.physics.md) / [experiment.physics.summary.md](experiment.physics.summary.md) | 同一 Package 的详细/精简阅读说明，非 Runtime 输入；本次未重新生成 |
| [experiment.yaml](experiment.yaml) | 旧兼容规格；不提供当前默认参数，不替代正式 YAML/NPZ |
| [statistics/provenance.yaml](statistics/provenance.yaml) | 旧 `cutoff_single.py` / `core/engine.py` 中 `CSI_N_EXP`、`CSI_N_BG`、`CSI_EXP_UNC` 的解释；保留原文件及其非官方限制 |

| NPZ 数组组 | 个数、坐标/单位 | 来源与实际消费者 |
|---|---|---|
| `source_energy_MeV`, `source_fluence_e/mub` | 3；200 点 MeV、`cm^-2 MeV^-1` | 既有 `build_neutrino_empirical_flux_sns` 生成；Package 使用已积分注量表，未从旧 SNS TXT 取值 |
| `state_rho_e/mu` | 2；3×3，无量纲 | 既有 `sns_component_state` 固定味态；prompt 能量和线权重另在 YAML |
| `nuclear_Cs133_*`, `nuclear_I127_*` | 14；七通道 × 两核素，`(p,n)` 2×2 升幂系数，无量纲 | 来自本地 [responses_all.json](../../../responses/README.md) Cs133/I 条目，当前逐值一致；由 NPZ 装配，不再读外部 JSON |
| `observable_pe_edges` | 1；10 个 PE edges | 提取时的 `ObservationDefinition.edges`，供九箱分箱 |
| `statistics_observed/background/uncertainty` | 3；9 箱，counts/PE | 提取时的 `StatisticsDefinition`，更早来自上述旧数组；预测 counts/bin 在近似统计前按 PE 箱宽换算 |

YAML 的 `provenance.sources` 保存提取时的代码位置/哈希，部分旧模块后来迁移，定位用于历史追溯。探测器 quenching、Gamma 分辨率与效率公式的系数在正式 YAML，直接来源是既有探测器代码/默认值；这里没有一份待 Runtime 读取的独立效率 TXT，不另建空 `detector/`。外部校准数据、有效域和一手出处仍需核对。

SNS 注量已含 POT、每 POT 产额与基线几何因子；不再重复乘曝光或把单位归一化谱形当作绝对通量。表的掩码、端点、线性插值及不重新归一化的约定按 YAML 保留。核响应匹配现有 JSON 只证明内部一致，未完成外部源表和归一化审查。

[COHERENT 2021 论文/ancillary 入口](https://arxiv.org/abs/2110.07730)可用于后续独立核对；尚未证明当前 residual、BRN/NIN 和误差数组是官方完整 likelihood。既有统计 provenance 不改写，背景扣除组成与近似两 pull Gaussian 的解释问题保留。分析所用 ZIP 漏装了本地已存在的正式 YAML/NPZ，本次没有根据旧代码重建或改动它们。

## Three-file onboarding pilot (2026-11-04)

The current nine-bin implementation has an audit-ready **DRAFT / PARTIAL**
input description in exactly three formal files:

- [experiment.input.yaml](experiment.input.yaml): model specifications, scalar
  values, units, normalization, provenance and unresolved scientific issues.
  It uses the JSON subset of YAML 1.2; scalars/models are authoritative here.
- [experiment.resources.npz](experiment.resources.npz): the consumed Cs/I
  nuclear-response coefficients, SNS tables, fixed flavor states, PE edges and
  legacy statistical arrays. Arrays are authoritative here, with declared keys
  and SHA256 in the YAML; read using `allow_pickle=False`.
- [experiment.physics.md](experiment.physics.md): the generated physical
  explanation, parameter tables, formulas and complete array inventory.

From the project root, use `python -B tools/validate_experiment_input.py data/experiments/COHERENT_CsI/CsI2021`
for the current package. `build_csi2021_onboarding_pilot.py --check` describes
the historical extraction baseline and does not certify later runtime metadata.
The tool's `--write` is create-only and refuses existing pilot files;
`--render-md` renders the stored YAML/NPZ explanation to stdout for review.
The tool is a historical extraction aid, not an additional formal package input.

The current runtime consumes only the two machine files and common model algorithms.
No external `responses_all.json`, old spec, paper or Physics MD is read by this path.
Dataset ownership and distribution are audited in Task 09.
Official experiment provenance, general antineutrino EFT treatment and the
external nuclear-response source-table audit remain unresolved. This pilot
does not include ROOTTime, time bins or the 9x11 demo.

The sections below retain the earlier specification's historical state.
Their Phase/status assertions and old run paths are not current validation
evidence. Dataset identity and related papers are indexed in the
[CsI2021 overview](../../../../docs/experiments/COHERENT/CsI2021/README.md).

This directory is the Phase 1 runtime dataset specification for the existing
COHERENT CsI2021 reproduction path. It does not implement new experiment
physics.

## Identity and provenance

- Dataset: CsI2021
- Family: COHERENT CsI
- Source: stopped-pion SNS
- Target: equal-stoichiometry CsI using Cs-133 and I-127
- Historical run paths (currently missing; not approved inputs):
  - workflows/experiment-integration/runs/CsI2021/00_INPUT_INVENTORY.md
  - workflows/experiment-integration/runs/CsI2021/00_IMPLEMENTATION_MANIFEST.yaml

## Observable and output contract

The true axes are incident energy in MeV and recoil energy in keV. The
reconstructed observable is PE. The output contains nine PE bins for each
source component key mu, e, mub, plus total, with unit expected events per bin.

The explicit PE edges are 0.001, 8.001, 12.001, 16.001, 20.001, 24.001,
32.001, 40.001, 48.001 and 60.001.

## Statistical mode

The historical recorded mode is background_subtracted_excess. The approximate
Gaussian two-pull runtime is available for legacy compatibility. Its residual/
excess and added-background interpretation remains unresolved; official
likelihood remains BLOCKED pending authoritative provenance.

## Implemented phase

DATASET_VALIDATED only. Existing Python registry behavior is unchanged.

## Pending modules

- Target text validation: Phase 2.
- Canonical SNS source states: Phase 3.
- Theory coverage report: Phase 4.
- Cross-section validation: Phase 5.
- Detector-response validation: Phase 6.
- Flavor-aware Slow counts: Phase 7.
- Fast counts: blocked until P4 Flavor contract.
- Statistics: blocked pending provenance.

## Known blockers

ANTI-NU AUDIT is required before changing interaction-kernel physics. The
physical/legacy prompt-energy difference remains a reproduction convention.



## P04–P10 执行证据（2026-11-04）

[本次运行索引](../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/README.md) 记录完整七响应/22 算符的 package-only 适配、Slow 网格、Fast 工程候选和近似统计。长积分固定 revision-2 输入及 wheel-01；同期输入元数据更新另存版本并桥接核对。技术证据不改变 DRAFT/PARTIAL 或人工 NOT_REVIEWED。

[experiment.physics.md](experiment.physics.md) 使用现有共享 Renderer，
按本 dataset 输入选择物理说明、必要公式和简明资源索引；公共 matching/粒子响应不逐项展开。
现有 YAML/NPZ 和权限保持原样，报告可用既有 CLI 的 `--md-only` 只读输入重渲染；
见[package 编译器入口](../../../../tools/compile_experiment_package.py)。

[experiment.physics.summary.md](experiment.physics.summary.md) 是精简阅读版；
[experiment.physics.md](experiment.physics.md) 是详细实验适配说明。
二者由同一 YAML/NPZ 和报告元数据通过现有 --md-only 命令生成，
完整公式、逐箱统计和数值约定以详细版为阅读入口；两份 MD 都不是 Runtime 输入。
报告规范只维护在[共享合同](../../../../workflows/_shared/references/onboarding/experiment-physics-report-contract.md)。

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| CsI-time：9PE×11时间箱 | [r2 / SM 20261107；NSI 20261108；处理方式](<../../../../docs/experiments/COHERENT/CsI2021/time_resolved/METHODS.md>) | [当前输入](<time_resolved/analysis_inputs.npz>) | [SM报告](<../../../../docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>) / [NSI报告](<../../../../docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>) / [观测叠加](<../../../../outputs/csi2021_time_sm_data_comparison_20261109/README.md>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
