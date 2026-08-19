# Legacy Normalization Forensic Audit: CONUS+

```text
DATASET: conus_plus_ge73_pheno
STATUS: FORENSIC_AUDIT_GENERATED
PRODUCTION_CODE_CHANGED: no
REFERENCE_ARRAYS_CHANGED: no
EXPERIMENT_YAML_CHANGED: no
```

## Primary Finding

The most likely problem is not the numerical CEvNS integration itself. The
executable legacy/PDF/Python chain is internally consistent if the result is
read as absolute events per 10 eVee bin for a 119 kg day, or equivalently
1 kg * 119 day, phenomenological exposure.

The weak point is the written observable convention: the old Mathematica axis
label `Counts [kg^-1 (10 eVee)^-1]` is not compatible with the located
executable normalization unless an additional, currently undocumented,
normalization factor is applied.

```text
IS 150.494 NUMERICALLY WRONG?
NO within the current legacy/PDF/Python contract

IS 150.494 UNIT/SEMANTICS WRONG?
NO for absolute events/bin at 119 kg day; YES if plotted as kg^-1 per 10 eVee

IS yData ABSOLUTE EVENTS/BIN?
LIKELY, but provenance remains secondary/local

IS THE OLD MATHEMATICA Y-AXIS LABEL CORRECT?
UNLIKELY

IS 119 A LIVE-TIME OR AN EXPOSURE?
best supported in executable code as exposureKgDay; physically also equals reactor-on days for a 1 kg normalization

IS CURRENT PYTHON A FAITHFUL IMPLEMENTATION OF THE CURRENT PDF?
YES

IS THE CURRENT PDF A FAITHFUL PHYSICAL INTERPRETATION OF THE LEGACY NOTEBOOK?
PARTIAL

CAN THE LEGACY MODEL BE CLAIMED AS OFFICIAL CONUS+?
NO
```

## Numerical Diagnostics

| Quantity | Value |
|---|---:|
| Current theory, absolute events/bin, 119 kg day | 150.494345987 |
| Legacy/PDF yData direct sum | 132.8131 |
| Theory - yData | 17.6812459871 |
| Relative difference vs yData | 13.312878% |
| Ratio theory/yData | 1.13312878012 |
| Theory if divided by 119, counts/kg/(10 eVee) total | 1.26465836964 |
| yData implied absolute events at 119 kg day if axis literal | 15804.7589 |
| Exposure-only diagnostic scaled to 327 kg day | 413.543286872 |
| Pull vs official SM 347 +/- 59 | 1.12785 |
| Pull vs official measured 395 +/- 106 | 0.174937 |
| 327/119 effective active mass | 2.74789915966 kg |
| Approx official active mass cited in prompt | 2.83 kg |
| Required ratio 347 / exposure-only diagnostic | 0.839089911541 |
| Required residual percent change to 347 | -16.091% |

The statement required by the prompt is therefore:

```text
THE LEGACY AXIS LABEL IS PHYSICALLY INCOMPATIBLE WITH THE PUBLISHED EVENT SCALE
```

unless a missing documented normalization factor is later found.

## Unit Chain

Located executable chain:

```text
dPhi/dE_nu
  x dSigma/dT
  -> S(T), rate per target nucleus per recoil energy

nucleiPerKg = N_A * 1000 / A
expoFactor = nucleiPerKg * exposureKgDay * secPerDay

dNdEreco(Ereco)
  = expoFactor * integral dT S(T) R(Ereco | T)

binCounts
  = integral over reconstructed energy dEreco dNdEreco(Ereco)
```

Interpretation A, `119 = 119 kg day`:

```text
dNdT      -> events / keVnr
dNdEreco  -> events / eVee
binCounts -> absolute events per bin
```

Interpretation B, `119 = 119 day`:

```text
nucleiPerKg * 119 day * secPerDay
```

is equivalent to a 1 kg detector followed for 119 days. The resulting plotted
quantity is still absolute events for that effective 1 kg exposure. It is not
counts/kg/bin unless the final result is divided by mass/exposure.

## Legacy Code Evidence

| Source | Line | Matched terms | Snippet |
|---|---:|---|---|
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2097 | binCounts; BinCounts; Counts | `<|"fFit"->fFit,(*快速近似的谱函数*)"FFit"->FFit,(*快速的一次积分函数：\[Integral]_{Emin}^{E} fFit*)"BinCounts"->Function[{a,b},FFit[b]-FFit[a]]|>];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2127 | binCounts; BinCounts; Counts | `(*或等价写法：SMint=modelSM["BinCounts"]@@@Partition[pbins,2,1];*)` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2432 | exposure | `(* ============================================================Module 4:Detector response (quenching+resolution+exposure+threshold)-保留你所有公式-让 dNdEreco 成为一个闭包：捕获 Sinterp、Tmin/Tmax、expoFactor 等============================================================*)` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2435 | 119; exposure; exposureKgDay; kg | `CreateGeDetectorResponse[iso_Association,exposureKgDay_:119,Ethr_:160.0,(*eVee*)kL_:0.162,eta_:2.96,Fano_:0.1096,sigma0_:20.38]:=Module[{A,Z,NA,secPerDay,nucleiPerKg,expoFactor,epsSym,gSym,QFsym,ErSym,sigmaRes,GausResponse,EffReco},A=iso["A"];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2439 | kg | `nucleiPerKg=NA*(1000.0/A);` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2440 | exposure; exposureKgDay; kg | `expoFactor=nucleiPerKg*exposureKgDay*secPerDay;` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2459 | 119 | `det=CreateGeDetectorResponse[iso,119,160.0];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2494 | binCounts; BinCounts; Counts | `<|"fFit"->fFit,(*快速近似的谱函数*)"FFit"->FFit,(*快速的一次积分函数：\[Integral]_{Emin}^{E} fFit*)"BinCounts"->Function[{a,b},FFit[b]-FFit[a]]|>];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2504 | binCounts; BinCounts; Counts | `(*预先构建好所有\[OpenCurlyDoubleQuote]昂贵对象\[CloseCurlyDoubleQuote]，后面每次只算 binCountsFast（更快）*)sofT=CreateSofT[CONUSiso,CONUSflux,differentialCrossSectionNN];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2506 | 119 | `det=CreateGeDetectorResponse[CONUSiso,119,Ethr];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2510 | binCounts; BinCounts; Counts | `(*返回一个\[OpenCurlyDoubleQuote]零参数函数\[CloseCurlyDoubleQuote] calcRatesCONUS[]，用于你的统一 Table 循环里直接调用*)Function[{},Module[{binCountsFast},binCountsFast=Differences[model["FFit"]/@edgesLocal];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 2511 | binCounts; BinCounts; Counts | `{{{binCountsFast}}}   (*Nt=1,Nc=1,shape {1,1,Nbin}*)]]];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3444 | exposure | `(* ============================================================Module 4:Detector response (quenching+resolution+exposure+threshold)-保留你所有公式-让 dNdEreco 成为一个闭包：捕获 Sinterp、Tmin/Tmax、expoFactor 等============================================================*)` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3447 | 119; exposure; exposureKgDay; kg | `CreateGeDetectorResponse[iso_Association,exposureKgDay_:119,Ethr_:160.0,(*eVee*)kL_:0.162,eta_:2.96,Fano_:0.1096,sigma0_:20.38]:=Module[{A,Z,NA,secPerDay,nucleiPerKg,expoFactor,epsSym,gSym,QFsym,ErSym,sigmaRes,GausResponse,EffReco},A=iso["A"];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3451 | kg | `nucleiPerKg=NA*(1000.0/A);` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3452 | exposure; exposureKgDay; kg | `expoFactor=nucleiPerKg*exposureKgDay*secPerDay;` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3471 | 119 | `det=CreateGeDetectorResponse[iso,119,160.0];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3506 | binCounts; BinCounts; Counts | `<|"fFit"->fFit,(*快速近似的谱函数*)"FFit"->FFit,(*快速的一次积分函数：\[Integral]_{Emin}^{E} fFit*)"BinCounts"->Function[{a,b},FFit[b]-FFit[a]]|>];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3523 | 119 | `CONUSdet=CreateGeDetectorResponse[CONUSiso,119,160.0];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3535 | binCounts; BinCounts; Counts | `binCountsFast=Differences[model["FFit"]/@edges]` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3560 | binCounts; BinCounts; Counts | `calcCONUS[edges_List]:=Module[{sofT,sinterp,det,dNdEreco,dNdErecoNum,model,binCountsFast},sofT=CreateSofT[CONUSiso,CONUSflux,differentialCrossSectionNN];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3562 | 119 | `det=CreateGeDetectorResponse[CONUSiso,119,160.0];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3566 | binCounts; BinCounts; Counts | `binCountsFast=Differences[model["FFit"]/@edges];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3567 | binCounts; BinCounts; Counts | `binCountsFast];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3605 | 119 | `CONUSdet=CreateGeDetectorResponse[CONUSiso,119,160.0];` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3611 | binCounts; BinCounts; Counts | `binCountsFast=Differences[model["FFit"]/@edges]` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3613 | kg; binCounts; BinCounts; binHeight; Counts | `binHeight=binCountsFast; (*counts/(kg\[CenterDot]eVee)*)` |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 3624 | 119 | `CONUSdet=CreateGeDetectorResponse[CONUSiso,119,160.0];` |

Full local evidence hits are written to
`artifacts/legacy_normalization_forensic_evidence.csv`.

## yData Provenance

The exact 19-value provenance is not fully proven from the original
Mathematica source in this run. The values are found in the current PDF text
extraction and workflow transcription, and in derived diagnostic files. That
supports the current dataset input, but it does not prove the original external
paper/table/digitization source.

```text
YDATA_UNIT = LIKELY_ABSOLUTE_EVENTS_PER_BIN_BUT_ORIGINAL_PROVENANCE_UNRESOLVED
```

| Source | Matched anchor count | Lines | Classification |
|---|---:|---|---|
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 6 | 4539;4540;4604 | legacy Mathematica source candidate |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md | 6 | 327;328;329;330;333;335 | workflow intake transcription |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/LEGACY_MATHEMATICA_REGRESSION_AUDIT.md | 4 | 152 | local occurrence |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/LEGACY_NORMALIZATION_FORENSIC_AUDIT.md | 6 | 192;193;194;195;198;200 | local occurrence |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/legacy_normalization_forensic_evidence.csv | 6 | 122;135 | local occurrence |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/legacy_normalization_shape_comparison.csv | 6 | 2;3;4;5;8;10 | local occurrence |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/legacy_unit_corrected_comparison.csv | 6 | 2;3;4;5;7;8;10 | derived diagnostic table |
| workflows/experiment-integration/runs/conus_plus_ge73_pheno/backup_pre_phase1/00_INPUT_INVENTORY.md | 6 | 292;293;294;295;298;300 | workflow intake transcription |
| mdGPT/2026-08-17 CONUS.md | 4 | 242;243;244;245 | task prompt |
| tools/experiment_integration/conus_legacy_normalization_forensic_audit.py | 6 | 37;38;39;40;43;45;260 | local occurrence |
| tools/experiment_integration/conus_legacy_unit_correction_diagnostic.py | 6 | 35;36;37;38;41;43 | hard-coded diagnostic constants |
| data/experiments/external/user_mathematica/2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt | 6 | 4539;4540;4604 | legacy Mathematica source candidate |
| docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf | 6 | pdf text extraction | current PDF table; secondary interpretation document |

PDF extraction status: `ok; pages=12`.

PDF hit counts:

| Pattern | Hits |
|---|---:|
| 119 | 4 |
| 327 | 1 |
| 347 | 1 |
| 395 | 1 |
| kg day | 3 |
| Rexp | 9 |
| background-subtracted | 4 |

## Shape Check

| Bin | Theory | yData | Theory - yData | Theory / yData | Cum theory frac | Cum yData frac |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 34.1736 | 13.36 | 20.8136 | 2.55791 | 0.227076 | 0.100592 |
| 2 | 26.5217 | 38.08 | -11.5583 | 0.696473 | 0.403306 | 0.387311 |
| 3 | 20.6134 | 29.02 | -8.40656 | 0.710318 | 0.540278 | 0.605814 |
| 4 | 16.0291 | 21.41 | -5.38086 | 0.748676 | 0.646788 | 0.767018 |
| 5 | 12.4594 | 12.36 | 0.0994389 | 1.00805 | 0.729578 | 0.860081 |
| 6 | 9.67323 | 5.222 | 4.45123 | 1.8524 | 0.793854 | 0.899399 |
| 7 | 7.49585 | 4.5511 | 2.94475 | 1.64704 | 0.843663 | 0.933666 |
| 8 | 5.79387 | 0.527 | 5.26687 | 10.9941 | 0.882162 | 0.937634 |
| 9 | 4.46443 | 9.4382 | -4.97377 | 0.473018 | 0.911827 | 1.0087 |
| 10 | 3.42764 | 2.78 | 0.647636 | 1.23296 | 0.934603 | 1.02963 |

Summary:

| Metric | Value |
|---|---:|
| Chi2-like using symmetric y errors | 7.26982 |
| RMS residual, absolute events | 7.90626 |
| RMS normalized-shape fraction difference | 0.059099 |

The arrays are numerically compatible with the same class of observable
(`absolute events/bin`) at the broad diagnostic level, but the bin-by-bin shape
is not a fit result and should not be interpreted as a physics preference.

## Three Separate Normalization Questions

### A. Legacy plot observable

The executable chain plots/integrates absolute bin counts if `binCounts` is used
directly. If the axis says `kg^-1 (10 eVee)^-1`, the label is likely inherited
or stale.

### B. Legacy theory normalization

The theory normalization uses `nucleiPerKg * exposureKgDay * secPerDay`. The
numeric value 119 can be read as 119 kg day, or as a 1 kg detector for 119
reactor-on days. Either way, the output after bin integration is absolute
events for that effective exposure.

### C. Official CONUS+ benchmark

The 413.543286872 value is only an exposure-only diagnostic:

```text
150.494345987 * 327 / 119
```

It is not a new official detector-level prediction.

## Interpretation Hierarchy

### Level 1: raw legacy Mathematica semantics

The located code applies exposure before reconstructed-energy integration and
therefore produces absolute events/bin. The parameter name supports kg day, but
the number 119 also matches reactor-on days in official prose.

### Level 2: current PDF interpretation

The PDF makes the 119 kg day interpretation explicit and treats `Rexp_i` as
background-subtracted excess counts. This is coherent as a phenomenological
dataset contract, but it may be too precise as a statement about official
CONUS+ detector exposure.

### Level 3: current Python implementation

Python is faithful to the current PDF/legacy executable contract: it returns
absolute expected events per bin. No evidence here requires changing the
production integrator.

### Level 4: exposure-corrected diagnostic

Scaling to 327 kg day gives 413.543286872 events. This lies 1.12785 sigma above
the official SM benchmark and 0.174937 sigma above the official measured central
value. That only shows broad event-scale compatibility after exposure scaling.

### Level 5: official CONUS+ detector-level result

Official CONUS+ uses detector-specific exposure, response, efficiency,
thresholds, isotope mixture, source and analysis details. The legacy pure-Ge73
phenomenological model cannot be claimed as the official detector-level model.

## Evidence Table

| Claim | Evidence for | Evidence against | Classification |
|---|---|---|---|
| 119 = kg day | Mathematica function parameter is exposureKgDay and expoFactor = nucleiPerKg * exposureKgDay * secPerDay; PDF writes X = nGe73/kg * 119 kg day * 86400 s/day. | Official facts also cite 119 reactor-on days and 327 kg day total exposure; variable name alone is not decisive. | BEST_SUPPORTED_FOR_EXECUTABLE_CONTRACT |
| 119 = days | Official CONUS+ reactor operation is 119 days; 327/119 gives an effective active mass scale. | Executable Mathematica multiplies by nucleiPerKg before multiplying by 119 and secPerDay, so the numeric contract is kg day or 1 kg * 119 days. | POSSIBLE_PHYSICAL_PROVENANCE_NOT_DIRECT_CODE_UNIT |
| binCounts = absolute events/bin | dNdEreco includes expoFactor before integration; BinCounts integrates dNdEreco over reconstructed energy. | Old plot label reportedly uses kg^-1 (10 eVee)^-1. | STRONGLY_SUPPORTED |
| binCounts = counts/kg/bin | Only supported by the written plot label if read literally. | No division by exposure is present after bin integration in the located legacy chain. | UNLIKELY |
| yData = absolute events/bin | Direct sum 132.8131 is numerically close to theory 150.494; PDF labels the table as background-subtracted excess counts. | Original external provenance of the 19 values was not proven beyond the current PDF/workflow transcription. | LIKELY_BUT_PROVENANCE_INCOMPLETE |
| yData = counts/kg/bin | Old y-axis label could be read that way. | Literal conversion implies 15804.7589 events at 119 kg day, incompatible with the published event scale. | PHYSICALLY_INCOMPATIBLE_UNLESS_MISSING_FACTOR_EXISTS |
| old y-axis label is correct | Reported label text. | It conflicts with the executable exposure multiplication and with event-scale diagnostics. | UNLIKELY |
| old y-axis label is wrong | Executable chain produces absolute events/bin; yData direct scale matches absolute counts much better than counts/kg/bin. | The exact original plotting cell with binHeight was not independently recovered in this run. | LIKELY |
| current PDF exposure interpretation is correct | It matches the executable formula if 119 is a 1 kg * 119 day effective exposure. | It may overstate the link to official CONUS+ 327 kg day detector-level exposure. | PARTIAL |
| current Python normalization is correct | It reproduces the current PDF/legacy contract and yields absolute events/bin. | That does not make it the official detector-level CONUS+ prediction. | CORRECT_FOR_CURRENT_CONTRACT |

## Residual Effects After Exposure Scaling

The exposure-only diagnostic is above the official SM central value. The
required residual correction is:

```text
347 / 413.543286872 = 0.839089911541
percent change = -16.091%
```

Potential legitimate sources of a correction of this order:

| Effect | Classification |
|---|---|
| detector-specific efficiency | LIKELY |
| detector thresholds | LIKELY |
| natural-Ge isotope mixture | POSSIBLE |
| official source spectrum | POSSIBLE |
| energy response | LIKELY |
| analysis window | KNOWN |
| detector-specific exposures | KNOWN |
| nuclear-response convention | UNTESTED |

No factor was tuned here to obtain 347.

## Correction Recommendations

### DOCUMENT CORRECTION

State explicitly that the current 150.494 result is absolute events/bin for the
workflow's effective 119 kg day exposure. Mark the legacy y-axis label as
suspect unless a missing normalization factor is found.

### METADATA CORRECTION

Keep `exposure_kg_day: 119` only if the dataset is documented as a
phenomenological 1 kg * 119 day / 119 kg day contract, not as the full official
CONUS+ exposure.

### CODE CORRECTION

No production physics-code correction is justified by this audit. If plots are
generated from `binCounts`, label them as absolute events/bin. If a normalized
axis is required, divide both theory and data by the same exposure convention.

### TEST CORRECTION

Add a comparison-layer unit test that fails if absolute bin counts are plotted
or compared under a `kg^-1 (10 eVee)^-1` label without exposure division.

### NO CHANGE REQUIRED

Do not replace 150.494 with 347. Do not tune physics parameters. Do not update
Slow/Fast references solely to match official CONUS+ central values.

## Central Answer

The legacy Mathematica code can produce a numerically reasonable CONUS-like
spectrum because the executable calculation applies a plausible effective
exposure and integrates to absolute bin counts. The inconsistency enters at the
written convention layer: a normalized y-axis label and ambiguous prose were
attached to a quantity that the code had already normalized to absolute events.

The specific legacy statement most likely wrong is the plot-axis label, followed
by any later interpretation that treats the old calculation as the full official
CONUS+ detector-level model. The calculation itself is not shown to be
numerically wrong by this audit.
