# Ar2020 input package

The registered Ar2020 runtime reads [experiment.input.yaml](experiment.input.yaml)
and [experiment.resources.npz](experiment.resources.npz). The generated
[experiment.physics.md](experiment.physics.md) explains the same inputs for human
review and is distributed with the dataset; runtime does not read it.

The package preserves the legacy SNS/Ar40 prediction, observed-energy Gaussian
resolution, tabulated efficiency and approximate asymmetric IRLS statistics.
Values are legacy-derived; package status is DRAFT and human physics review is
NOT_REVIEWED. Official likelihood, general antineutrino EFT and scientific release
remain BLOCKED. Dataset identity and related papers are indexed in the
[Ar2020 overview](../../../../docs/experiments/COHERENT/Ar2020/README.md).

The detector table and statistics provenance directories are retained historical
inputs. The package contains their declared values; normal runtime does not read
these older files. Recompilation uses the common compiler and saved acquisition IR,
with hashes, units, normalization and generated dependencies checked.

[experiment.physics.md](experiment.physics.md) 使用现有共享 Renderer，
按本 dataset 输入选择物理说明、必要公式和简明资源索引；公共 matching/粒子响应不逐项展开。
现有 YAML/NPZ 和权限保持原样，报告可用既有 CLI 的 `--md-only` 只读输入重渲染；
见[package 编译器入口](../../../../tools/compile_experiment_package.py)。
