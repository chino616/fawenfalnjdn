# CONUS+ Legacy Unit Correction Diagnostic

```text
DATASET: conus_plus_ge73_pheno
STATUS: DIAGNOSTIC_PROGRAM_RAN
SCOPE: comparison/plot-layer unit contract only
PRODUCTION_CODE_CHANGED: no
```

## Purpose

The legacy Mathematica layer multiplies the response by the full exposure before
bin integration, so its `binCounts` are absolute events per 10 eVee bin. The
same layer labels the plot as `Counts [kg^-1 (10 eVee)^-1]` and overlays yData
directly. This diagnostic keeps those two interpretations separate.

## Totals

| Quantity | Value |
|---|---:|
| Theory, absolute events/bin, 119 kg day | 150.494345987 |
| Legacy/PDF yData direct sum | 132.8131 |
| Theory, counts/kg/(10 eVee), if axis label literal | 1.26465836964 |
| Theory, exposure-only scaled to 327 kg day | 413.543286872 |
| yData as absolute events at 119 kg day, if axis label literal | 15804.7589 |
| yData as absolute events at 327 kg day, if axis label literal | 43429.8837 |

## Hypothesis Comparison

| Hypothesis | Unit interpretation | Dimensionally matches legacy axis label | Chi2-like | RMS residual | Total residual |
|---|---|---:|---:|---:|---:|
| H1 | yData = absolute events/bin | no | 7.26982 | 7.90626 | 17.6812 |
| H2 | yData = counts/kg/(10 eVee) | yes | 21.0545 | 13.7477 | -131.548 |

## Official Exposure Diagnostic

| Quantity | Value |
|---|---:|
| Theory scaled from 119 to 327 kg day | 413.543286872 |
| Official SM benchmark | 347 +/- 59 |
| Pull vs official SM | 1.12785 |
| Official measured count | 395 +/- 106 |
| Pull vs official measured | 0.174937 |

## Interpretation

H1 is numerically much closer to the existing legacy/PDF yData overlay, but it
does not match the old plot axis label. H2 matches the old axis label
dimensionally, but it implies a yData total of
15804.7589 absolute events at
119 kg day, which is incompatible with the current theory scale and the
published 327 kg day benchmark scale.

The corrected next step is therefore to fix the comparison and plotting unit
contract first: either plot absolute events/bin and label it as such, or divide
all absolute bin counts by the same exposure before using a normalized
counts/kg/(10 eVee) axis. This diagnostic does not justify changing the
production physics integration by itself.
