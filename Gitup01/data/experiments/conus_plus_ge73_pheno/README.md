# conus_plus_ge73_pheno

Dataset-phase skeleton for the CONUS+ `73Ge` phenomenology dataset.

This directory currently contains only `experiment.yaml`. Phase 1 records the
dataset identity, effective detector, exposure semantics, regular reconstructed
energy binning, target isotope, expected output axis, and planned future data
files.

No reactor flux tables, detector-response data, Slow counts, Fast kernels,
statistics tables, CSV files, NPY files, or NPZ files are created in Phase 1.

Source document:

```text
docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf
```

Important dataset constraints:

- `dataset_id`: `conus_plus_ge73_pheno`
- Effective detector: `Ge73`
- Target isotope: `73Ge` only
- Exposure: `119 kg day`, already mass times live time
- Analysis window: `160 <= E_reco < 350 eVee`
- Rule binning: 19 bins of width `10 eVee`
- Statistical data mode: `background_subtracted_excess`

The official CONUS+ C2/C3/C5 detector-by-detector model is intentionally not
represented by this dataset.
