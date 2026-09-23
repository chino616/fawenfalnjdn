# Migration Pre/Post Statistics Comparison

Status: PASS

This directory compares the pre-migration statistics code from `CEvNS-pyEFT-main` with the migrated split statistics package in this worktree.

Scope:
- CsI2021 fixed predictions through the legacy approximate two-pull chi-square.
- CsI2017 fixed predictions through the legacy approximate one-pull chi-square.
- Ar2020 fixed predictions through the legacy approximate IRLS and bounded/minimize profiles.
- Confidence-threshold constants used by the migrated result scripts.

Results:
- Profile comparison rows: 80
- Confidence comparison rows: 9
- Skipped rows: 0
- Failure rows: 0
- Max profile absolute difference: 7.1054273576010019e-15
- Max profile relative difference: 1.3986319915934765e-16

Important limitation:
The bundled pre-migration source contains JSON metadata for COHERENT Fast kernels but not the corresponding `.npz` kernel arrays, so the old Flavor contour program cannot be fully replayed from that bundle alone. The strict comparison here is therefore the statistics layer: identical fixed prediction vectors are sent through old and migrated likelihood/profile code. The Flavor result figures remain legacy approximate topology outputs, not official COHERENT likelihoods.

Artifacts:
- `legacy_statistics_outputs.json`
- `migrated_statistics_outputs.json`
- `profile_comparison.csv`
- `confidence_comparison.csv`
- `summary.json`
