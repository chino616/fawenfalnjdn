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
