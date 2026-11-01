# Phase 0 input inventory — XENONnT 2026 public templates

## Identity

```yaml
experiment_name: XENONnT solar CEvNS public data release
experiment_slug: Solar_B8
dataset_id: xenonnt_2026_sr0_sr1_sr2_public_templates
scope_gate: APPROVED
scientific_claim: public_template_reconstruction
backup_quarantine_applied: true
```

## Registered release

| source ID | path | role | status |
| --- | --- | --- | --- |
| XNT-ARCHIVE | docs/8B/cevns_data_release-sr0_sr1_sr2.zip | fixed official archive | SOURCE_EXTRACTED |
| XNT-RAW | docs/8B/cevns_data_release-sr0_sr1_sr2/XENONnT-cevns_data_release-6c82981 | expanded release | SOURCE_EXTRACTED |
| XNT-README | docs/8B/cevns_data_release-sr0_sr1_sr2/XENONnT-cevns_data_release-6c82981/README.md | data semantics and units | SOURCE_EXTRACTED |
| XNT-BINNING | raw/binning/sr0.yaml, sr1.yaml, sr2.yaml | four-dimensional bin edges | SOURCE_EXTRACTED |
| XNT-DATA | raw/data/sr0.csv, sr1.csv, sr2.csv | post-selection data | SOURCE_EXTRACTED |
| XNT-TEMPLATES | raw/templates/sr*/{ac,er,rg,mono}/*.h5 | signal and background templates | SOURCE_EXTRACTED |
| XNT-LIMITS | raw/limits/sr2/*.csv | published limit references | REFERENCE_ONLY |

## Integrity

Official archive MD5: `e0d740c3347fe13061e9cff576775632`.
The expanded release contains 6,915 HDF5 templates, three binning YAML files,
three data CSV files, five limits CSV files, README, license, and notebook.

## Boundary

The requested result is a public-template reconstruction. P06 remains pending
until HDF5 keys/shapes, axis ordering, template units, exposure mapping, masks,
nuisance priors, correlations, interpolation, and truncation are audited.
The 2024 XENONnT paper benchmark is a separate dataset.

