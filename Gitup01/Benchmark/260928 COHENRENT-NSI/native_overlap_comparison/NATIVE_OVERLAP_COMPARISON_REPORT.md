# 2211.11905 Fig.3-Fig.7 native overlap comparison

Status: PARTIAL_NATIVE_APPROXIMATE_COMPARISON

This output follows the benchmark folder definitions, but it is not a paper-matched reproduction. It uses the migrated CEvNS-pyEFT Flavor Fast kernels and legacy approximate statistics, while the paper uses CsI/LAr timing-energy likelihoods and paper-specific nuisance models.

What was generated:
- Paper original page renders for Fig.3-Fig.7 from the local `2211.11905v2.pdf`.
- Native approximate reproduced contours for Fig.3-Fig.6 using CsI2021 and Ar2020 only.
- Side-by-side comparison PNGs for Fig.3-Fig.6.
- A Fig.7 placeholder comparison declaring NGI_MISSING / NOT_COMPARABLE.

Important differences from the benchmark paper:
- LAr is represented by the current Ar2020 legacy approximate likelihood, not the paper Eq. (3.12)-(3.13) timing-energy likelihood.
- CsI uses the current CsI2021 legacy approximate likelihood, not the paper 9 PE x 11 timing Poisson likelihood.
- CsI2017 is intentionally not added to the paper-style joint result.
- Fig.7 NGI scalar/tensor is not reproduced; no surrogate NSI plot was used.
- Paper originals are full page renders, not manually audited figure crops.

Panel status table: `panel_status.csv`.
Raw native approximate NPZ: `raw_native_approx/`.
Reproduced figures: `figures/reproduced/`.
Comparison figures: `figures/comparison/`.

Generated comparison files:
- `figures/comparison/Fig03_native_approx_comparison.png`
- `figures/comparison/Fig04_native_approx_comparison.png`
- `figures/comparison/Fig05_native_approx_comparison.png`
- `figures/comparison/Fig06_native_approx_comparison.png`
- `figures/comparison/Fig07_NGI_not_comparable.png`
