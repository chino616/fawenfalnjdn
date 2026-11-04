# Ar2020 input package

The registered Ar2020 runtime reads [experiment.input.yaml](experiment.input.yaml)
and [experiment.resources.npz](experiment.resources.npz). The generated
[experiment.physics.md](experiment.physics.md) explains the same inputs for human
review and is distributed with the dataset; runtime does not read it.

The package preserves the legacy SNS/Ar40 prediction, observed-energy Gaussian
resolution, tabulated efficiency and approximate asymmetric IRLS statistics.
Values are legacy-derived; package status is DRAFT and human physics review is
NOT_REVIEWED. Official likelihood, general antineutrino EFT and scientific release
remain BLOCKED. See the [migration report](../../../../docs/PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md).

The detector table and statistics provenance directories are retained historical
inputs. The package contains their declared values; normal runtime does not read
these older files. Recompilation uses the common compiler and saved acquisition IR,
with hashes, units, normalization and generated dependencies checked.
