# Migration Pre/Post Comparison

This folder is a concrete replay harness for comparing the statistics migration.

Run from the repository root:

```powershell
& "F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\git-worktree-f0\Gitup01\migration_prepost_comparison\run_comparison.ps1"
```

What it compares:
- pre-migration code under `F:\Work\2026-07-15 CEvNSpyEFT-Local\CEvNS-pyEFT-main\CEvNS-pyEFT-main`
- migrated statistics code in this worktree
- identical fixed prediction vectors for CsI2021, CsI2017, and Ar2020
- legacy approximate statistics only

Outputs are written to `outputs/`:
- `legacy_statistics_outputs.json`
- `migrated_statistics_outputs.json`
- `profile_comparison.csv`
- `confidence_comparison.csv`
- `summary.json`
- `COMPARISON_REPORT.md`

Important limitation: the pre-migration bundle has COHERENT Fast-kernel JSON metadata but not the matching `.npz` kernel arrays, so this harness cannot fully replay the old Flavor contour figure generator. It tests the migrated statistics layer directly.
