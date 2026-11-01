# XENONnT 2026 public-template input

## Identity

```yaml
experiment_name: XENONnT solar CEvNS public data release
experiment_slug: Solar_B8
dataset_id: xenonnt_2026_sr0_sr1_sr2_public_templates
task_scope: physics_onboarding
input_mode: guided
scope_gate: APPROVED
scientific_claim: public_template_reconstruction
```

## Scope

This dataset registers the fixed XENONnT SR0+SR1+SR2 public release. The
release provides post-selection data, four-dimensional binning, background
templates, and monoenergetic nuclear-recoil templates. The mono-NR templates
are detector response templates and are not the 2024 XENONnT efficiency.

The intended result is a reproducible public-template reconstruction. It is
not an official collaboration likelihood unless the nuisance priors,
correlations, masks, exposure mapping, and fitting behavior are independently
verified.

## Four observables

1. corrected S2 amplitude (`cS2`);
2. quantile of `S2_pre / Delta t_pre`;
3. S1 BDT score;
4. S2 BDT score.

## Source release

The local archive is retained under `docs/8B` and has official MD5
`e0d740c3347fe13061e9cff576775632`. The expanded release contains three
science-run data CSV files, three binning YAML files, 6,915 HDF5 templates,
five limits CSV files, the README, license, and example notebook.

## Current audit boundary

Before P06 can pass, inspect HDF5 keys and shapes, axis ordering, template
units, exposure mapping, nuisance grids, masks, interpolation, and truncation.
Do not combine this dataset with the 2024 XENONnT benchmark as independent
data.

