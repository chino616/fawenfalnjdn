# Legacy Mathematica Regression Audit: conus_plus_ge73_pheno

## Executive Summary

```text
AUDIT_SCOPE: legacy Mathematica contract vs current Python contract
DATASET: conus_plus_ge73_pheno
CURRENT_PYTHON_TOTAL: 150.49434598713285 events
PRIMARY_FINDING: Python largely preserves the legacy Mathematica physics contract
PRIMARY_LEGACY_RISK: Mathematica likely confused reactor-operation days / kg day exposure and also mixed absolute bin events with a per-kg plot label
STATUS: LEGACY_CONTRACT_SUSPICIOUS
RECOMMENDED_NEXT_CHECK: CHECK_LEGACY_BINCOUNT_YDATA_UNITS
```

The evidence now narrows the problem. The current Python implementation is not
obviously a bad translation of the old Mathematica calculation. The more
important issue is that the old Mathematica contract itself appears internally
ambiguous:

1. It treats `119` as `exposureKgDay`, not as reactor-operation days.
2. Its `dNdEreco` closure multiplies by a full exposure normalization before
   bin integration.
3. It then labels `binCounts` as `Counts [kg^-1 (10 eVee)^-1]` while leaving
   `binHeight = binCounts`.
4. It overlays `yData` directly on the same axis.

Therefore the most useful next diagnostic is not yet a broad rebuild of all
CONUS+ physics layers. The immediate breakpoint is:

```text
Are binCounts and yData the same physical quantity?
```

## Evidence From Legacy Mathematica

Legacy source:

```text
data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt
```

### Exposure Contract

The Mathematica function signature defines:

```text
CreateGeDetectorResponse[iso_Association, exposureKgDay_:119, Ethr_:160.0, ...]
```

Then it computes:

```text
nucleiPerKg = NA*(1000.0/A)
expoFactor = nucleiPerKg*exposureKgDay*secPerDay
```

This means the legacy detector response object interprets the default `119` as
an exposure in `kg day`. The source also calls:

```text
det = CreateGeDetectorResponse[CONUSiso, 119, Ethr]
```

So this is not merely a naming issue in a comment. It is the multiplicative
normalization used by the event-rate calculation.

Physical implication:

```text
legacy X = (N_A * 1000 / 73) * 119 kg day * 86400 s/day
```

That is the same exposure contract implemented by Python.

## Evidence From Current Python

Python uses the same exposure-normalization structure:

```text
target_time_normalization = nuclei_per_kg_ge73 * exposure_kg_day * SEC_PER_DAY
```

The current `experiment.yaml` explicitly records:

```text
detector.exposure_kg_day: 119
detector.exposure_semantics: mass_times_live_time
slow_counts.output_unit: expected_events_per_bin
slow_counts.reference_total_counts_sm: 150.49434598713285
```

The Python implementation returns both:

```text
counts_total
counts_per_bin["total"]
counts_per_evee["total"] = counts / bin_width
```

So Python is clearer than the Mathematica plot layer: the public Slow result is
absolute expected events per bin, and any density is a separate derived output.

## Unit Trace

The relevant chain is:

```text
dPhi/dE_nu              cm^-2 s^-1 MeV^-1
dSigma/dT               cm^2 keVnr^-1
S(T)                    s^-1 keVnr^-1 per target nucleus
expoFactor              target nuclei * seconds
dN/dT                   events keVnr^-1
response density         eVee^-1
dN/dE_reco              events eVee^-1
binCounts = integral dE  events per bin
```

Once `expoFactor` has been applied inside `dNdEreco`, integrating over a
10-eVee bin gives absolute expected events:

```text
N_i = integral_{E_i}^{E_{i+1}} dE_reco dN/dE_reco
```

It does not give:

```text
counts kg^-1 (10 eVee)^-1
```

unless one divides by the corresponding detector mass or exposure convention.
The legacy source does not show that division at the `binHeight` line. Instead
it sets:

```text
binHeight = binCounts
```

and labels the frame as:

```text
Counts [kg^-1 (10 eVee)^-1]
```

This is the core internal inconsistency.

## yData Risk

Legacy Mathematica defines:

```text
yData = {13.36, 38.08, 29.02, 21.41, ...}
```

and then overlays:

```text
Point[Transpose[{xC, yData}]]
```

on the same plot as `binHeight = binCounts`, with the same `Counts [kg^-1
(10 eVee)^-1]` axis.

If `yData` was digitized from a plot whose y-axis is per-kg per-10-eVee, then
the legacy Mathematica comparison is dimensionally invalid:

```text
theory: absolute events/bin under 119 kg day
data: counts kg^-1 (10 eVee)^-1
```

If `yData` was instead already converted into absolute per-bin excess events,
then the plot label is wrong but the numeric comparison may be meaningful.

The current repository does not yet prove which interpretation is correct.
This is why the result should be classified as a legacy-unit ambiguity, not as
a confirmed Python translation bug.

## Relation To PHYSICS_AUDIT

The earlier physics audit concluded:

```text
current implementation: internally valid phenomenological Ge73 dataset
official CONUS+ benchmark: different detector-level dataset
PHYSICS_AUDIT = MISMATCH
```

The legacy comparison refines that conclusion:

```text
Python likely reproduces the legacy Mathematica phenomenology model.
The legacy Mathematica model itself likely does not define the official
CONUS+ benchmark contract consistently.
```

This matters because `REBUILD_OFFICIAL_DATASET` remains the correct long-term
action for official CONUS+ reproduction, but a narrower diagnostic should come
first if the immediate question is "why did the old Mathematica plot look
compatible with the data?"

## Findings

| Finding | Status | Severity | Confidence | Explanation |
|---|---|---|---|---|
| Python reproduces legacy exposure convention | CONFIRMED | HIGH | HIGH | Both use nuclei/kg * 119 kg day * 86400 s/day. |
| Legacy `119` is likely not official exposure | CONFIRMED AGAINST OFFICIAL CONTRACT | CRITICAL | HIGH | Official CONUS+ uses 119 reactor-operation days but about 327 kg day reactor-on exposure. |
| Mathematica plot label conflicts with `binCounts` unit | CONFIRMED | CRITICAL | HIGH | `dNdEreco` applies exposure; `binCounts` integrates it; `binHeight=binCounts`; axis says counts/kg/bin. |
| `yData` unit is unresolved | OPEN | CRITICAL | MEDIUM | The array is overlaid directly with `binCounts`; whether it is absolute events or per-kg yield must be traced to its source. |
| Python low-energy source boundary differs from Mathematica | CONFIRMED | LOW | HIGH | Python zeros 0-0.01 MeV to avoid negative extrapolation; threshold makes it negligible for the large discrepancy. |
| Broad Source/Response/Cross-section debugging is not the next best step | RECOMMENDED | HIGH | MEDIUM | Most physics inputs match between Python and legacy Mathematica; the normalization/observable contract is the sharper breakpoint. |

## Current Interpretation Of 132.8131

The legacy array sum is:

```text
sum(yData) = 132.8131
```

This number should not automatically be treated as total observed excess
events. Its interpretation depends on the original y-axis of the source plot or
table:

```text
Case A: yData is absolute events/bin
  sum(yData) = 132.8131 total excess events over 160-350 eVee.

Case B: yData is counts kg^-1 (10 eVee)^-1
  sum(yData) = 132.8131 counts/kg over the 19 displayed bins.
```

Under Case B, comparing `sum(yData)` directly to a theory total event count is
dimensionally wrong.

## Narrow Regression Audit Needed Next

Recommended next action:

```text
CHECK_LEGACY_BINCOUNT_YDATA_UNITS
```

This should answer exactly four questions:

1. From the Mathematica source, what is the complete unit of `dNdEreco` after
   `expoFactor` is applied?
2. What is the final unit of `binCounts` after integrating `dNdEreco` across a
   10-eVee bin?
3. What is the original source and unit of `yData`, `yLow`, and `yUp`?
4. Can `binCounts` and `yData` enter the same plot or chi-square without a
   conversion?

Decision rule:

```text
If yData is per kg per bin:
  legacy Mathematica compared incompatible quantities.

If yData is absolute events per bin:
  legacy plot label is wrong, but the numeric comparison may be meaningful.

If yData source cannot be established:
  statistics/data validation is BLOCKED.
```

## Practical Consequence

Do not repair production Python yet.

The Python implementation currently has a coherent internal contract:

```text
output_unit = expected_events_per_bin
exposure_kg_day = 119
Slow total = 150.49434598713285 events
```

The unresolved issue is whether the legacy data vector and plot label described
the same observable. That has to be decided before changing exposure,
statistics, or official detector modelling.

