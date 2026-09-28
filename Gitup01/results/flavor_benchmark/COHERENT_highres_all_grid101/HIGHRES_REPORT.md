# COHERENT Flavor High-Resolution Scan Report

Status: PASS

Configuration:
- Datasets: CsI2021, CsI2017, Ar2020, plus combined sum.
- Planes: ee u/d, mumu u/d, real emu u/d.
- Axis range: [-1, 1] for both x and y.
- Grid: 101 x 101 per dataset per plane.
- Figures: 15 PNG at 300 DPI and 15 PDF.
- 2D threshold: 4.61 from legacy_2d_90_flow_a.

Numerical gates:
- Integration/Fast matching checks: PASS.
- Figure artifact count: PASS.
- Frame truncation rows: 12. Truncated cases are marked in `highres_scan_summary.csv` and on the affected plots.

Important limitation:
These are legacy approximate statistics and are not official COHERENT likelihoods. Ar2020 uses a generated Fast kernel with the resolution recorded in `highres_metadata.yaml`.

Primary artifacts:
- `integration_convergence_checks.csv`
- `highres_scan_summary.csv`
- `highres_metadata.yaml`
- 15+ `fig_*.png` files at 300 DPI
- matching `fig_*.pdf` files
- matching `.npz` grids for each dataset and combined plane.
