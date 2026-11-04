# CsI2017 dataset specification

This directory is the Phase 1 runtime dataset specification for the existing
COHERENT CsI2017 reproduction path. It does not implement new experiment
physics.

## Identity and provenance

- Dataset: CsI2017
- Family: COHERENT CsI
- Source: stopped-pion SNS
- Target: equal-stoichiometry CsI using Cs-133 and I-127
- Approved inputs:
  - workflows/experiment-integration/runs/CsI2017/00_INPUT_INVENTORY.md
  - workflows/experiment-integration/runs/CsI2017/00_IMPLEMENTATION_MANIFEST.yaml

## Observable and output contract

The true axes are incident energy in MeV and recoil energy in keV. The
reconstructed observable is PE. The output contains 25 PE bins for each source
component key mu, e, mub, plus total, with unit expected events per bin.

The PE edges are regular from 0.001 to 50.0 with width 1.99996.

## Statistical mode

The recorded mode is background_subtracted_excess. It is provisional and is
not used by the Flavor Slow migration. Statistics remains blocked pending
authoritative observed/background/covariance provenance.

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

ANTI-NU AUDIT is required before changing interaction-kernel physics.
The 14.57/14.6 kg and physical/legacy prompt-energy differences remain explicit
reproduction conventions and are not resolved in Phase 1.

# Canonical package authority

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
