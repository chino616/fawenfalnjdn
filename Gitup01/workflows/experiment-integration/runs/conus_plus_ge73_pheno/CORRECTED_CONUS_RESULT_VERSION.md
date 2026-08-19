# Corrected CONUS+ Result Code Output

```text
DATASET: conus_plus_ge73_pheno
STATUS: CORRECTED_RESULT_VERSION_RAN
INPUT_MODE: recompute
PRODUCTION_CODE_CHANGED: no
```

## Correct Unit Contract

The correct primary result from the existing CONUS+ phenomenological
implementation is:

```text
expected_signal_events_per_bin
unit = events per 10 eVee reconstructed-energy bin
exposure = 119 kg day
```

Do not label this primary result as `kg^-1 (10 eVee)^-1`. If a normalized
diagnostic is needed, divide the absolute bin counts by the same exposure and
label it as:

```text
events / (kg day) / (10 eVee bin)
```

## Totals

| Quantity | Value |
|---|---:|
| Correct primary total, 119 kg day | 150.494345987 |
| Normalized diagnostic total, events/(kg day bin) | 1.26465836964 |
| Exposure-only diagnostic total, 327 kg day | 413.543286872 |
| Scale factor 327/119 | 2.74789915966 |
| Pull vs official SM 347 +/- 59 | 1.12785 |
| Pull vs official measured 395 +/- 106 | 0.174937 |

The 327 kg day result is an exposure-only diagnostic, not an official
detector-level CONUS+ prediction.

## Figures

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\260715Gitup1\Gitup01\workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\corrected_conus_primary_events_bin_119kgday.png
F:\Work\2026-07-15 CEvNSpyEFT-Local\260715Gitup1\Gitup01\workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\corrected_conus_primary_events_bin_119kgday.pdf
F:\Work\2026-07-15 CEvNSpyEFT-Local\260715Gitup1\Gitup01\workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\corrected_conus_exposure_diagnostic_327kgday.png
F:\Work\2026-07-15 CEvNSpyEFT-Local\260715Gitup1\Gitup01\workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\corrected_conus_exposure_diagnostic_327kgday.pdf
```

## Bin Results

| Bin | E range [eVee] | Correct events/bin, 119 kg day | Diagnostic events/(kg day bin) | Exposure-only events/bin, 327 kg day |
|---:|---:|---:|---:|---:|
| 1 | 160-170 | 34.1736495196 | 0.287173525374 | 93.9057427974 |
| 2 | 170-180 | 26.5216907114 | 0.222871350516 | 72.8789316187 |
| 3 | 180-190 | 20.6134410025 | 0.173222193298 | 56.6436572086 |
| 4 | 190-200 | 16.0291448351 | 0.134698696094 | 44.0464736226 |
| 5 | 200-210 | 12.4594388924 | 0.104701167163 | 34.2372816623 |
| 6 | 210-220 | 9.67323482403 | 0.0812876875969 | 26.5810738442 |
| 7 | 220-230 | 7.49585376642 | 0.0629903677851 | 20.5978502657 |
| 8 | 230-240 | 5.79387048626 | 0.0486879872795 | 15.9209718404 |
| 9 | 240-250 | 4.46443485758 | 0.0375162593074 | 12.2678167935 |
| 10 | 250-260 | 3.42763600028 | 0.0288036638679 | 9.41879808479 |
| 11 | 260-270 | 2.62097097447 | 0.022024966172 | 7.20216393825 |
| 12 | 270-280 | 1.99529193257 | 0.0167671590972 | 5.48286102479 |
| 13 | 280-290 | 1.51180226261 | 0.0127042206942 | 4.15428016701 |
| 14 | 290-300 | 1.13980067356 | 0.00957815692069 | 3.13205731307 |
| 15 | 300-310 | 0.854962767433 | 0.00718456107086 | 2.34935147017 |
| 16 | 310-320 | 0.638015773237 | 0.00536147708602 | 1.75320300713 |
| 17 | 320-330 | 0.47370700719 | 0.00398073115286 | 1.30169908698 |
| 18 | 330-340 | 0.349994381252 | 0.00294112925422 | 0.961749266129 |
| 19 | 340-350 | 0.257405319239 | 0.00216306990957 | 0.70732386043 |
