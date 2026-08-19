# CEvNS Physics Audit: conus_plus_ge73_pheno

## First Page Summary

```text
DATASET: conus_plus_ge73_pheno
CURRENT PREDICTION: 150.49434598713285 events
REFERENCE BENCHMARK: 347 +/- 59 predicted SM events; 395 +/- 106 measured events
RELATIVE DIFFERENCE: -56.62987147344875% versus 347-event benchmark
INTERNAL VALIDATION STATUS: PASS_WITH_OPTIONAL_BLOCKER
EXTERNAL PHYSICS STATUS: MISMATCH
NUMBER OF CRITICAL ISSUES: 2
NUMBER OF HIGH-PRIORITY ISSUES: 2
RECOMMENDED NEXT CHECK: REBUILD_OFFICIAL_DATASET
PHYSICS_AUDIT: MISMATCH
```

Current prediction:

```text
150.49434598713285 events
```

Reference benchmark:

```text
Official CONUS+ observation: 347 +/- 59 predicted SM events and
395 +/- 106 measured events.
```

Main finding:

```text
The current implementation is internally validated, but it is not the official
CONUS+ C2/C3/C5 detector-level analysis. It implements a user-defined
phenomenological effective Ge73 dataset with 119 kg day exposure, pure Ge73,
an ideal 160 eVee threshold, and a 160-350 eVee 19-bin analysis window.
```

The dominant documented external mismatch is dataset identity: the official
CONUS+ benchmark is a detector-level analysis using the real CONUS+ detector
inventory and a reported 327 kg day reactor-on exposure. Applying only the
exposure ratio diagnostically gives:

```text
150.49434598713285 * (327 / 119) = 413.5432868722054 events
```

This moves the result past the official 347-event prediction rather than
reproducing it. Therefore the discrepancy cannot be fixed by a single exposure
rescaling.

## Audit Basis

Current implementation records inspected:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_INPUT_INVENTORY.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/00_IMPLEMENTATION_MANIFEST.yaml
workflows/experiment-integration/runs/conus_plus_ge73_pheno/01_DATASET.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/02_DETECTOR_TARGET.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/03_SOURCE.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/04_THEORY_RESPONSE.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/05_KINEMATICS_CROSS_SECTION.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/06_DETECTOR_RESPONSE.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/07_SLOW_COUNTS.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/08_FAST_COUNTS.md
workflows/experiment-integration/runs/conus_plus_ge73_pheno/09_NUMERICAL_VALIDATION.md
data/experiments/conus_plus_ge73_pheno/experiment.yaml
src/cevns_pyeft/experiments/conus/source.py
src/cevns_pyeft/experiments/conus/kinematics.py
src/cevns_pyeft/experiments/conus/detector_response.py
src/cevns_pyeft/experiments/conus/slow_counts_conus_plus_ge73_pheno.py
src/cevns_pyeft/experiments/conus/fast_cumulative_conus_plus_ge73_pheno.py
```

External references inspected:

```text
docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf
Official Nature/PMC article: https://pmc.ncbi.nlm.nih.gov/articles/PMC12310522/
Official Nature DOI page: https://www.nature.com/articles/s41586-025-09322-2
CONUS+ experiment design paper: https://doi.org/10.1140/epjc/s10052-024-13551-6
```

The official Nature/PMC article reports 119 days of reactor operation,
395 +/- 106 measured antineutrinos, 347 +/- 59 predicted SM events, C2/C3/C5
detectors, total active mass 2.83 +/- 0.02 kg, 327 kg day reactor-on exposure,
and 60 kg day reactor-off exposure.

## Current Contract

| Field | Value | Unit | Source file | Implementation symbol |
|---|---:|---|---|---|
| dataset identity | conus_plus_ge73_pheno | label | experiment.yaml | dataset_id |
| intended claim | CONUS+ phenomenology model | classification | 00_INPUT_INVENTORY.md | dataset_identity |
| detector model | one effective Ge73 detector | label | experiment.yaml | detector.detector_label |
| target composition | pure Ge73 | isotope | experiment.yaml | target.response_key |
| exposure | 119 | kg day | experiment.yaml | detector.exposure_kg_day |
| source normalization | 1.5e13 | cm^-2 s^-1 | experiment.yaml/source.py | PHI0_CM2_S |
| source spectrum | Kopeikin below 2 MeV + Mueller above 2 MeV | shape | source.py | release_reactor_spectrum_shape |
| neutrino support | 0.01 to 10 | MeV | source.py | ENERGY_MIN_MEV / ENERGY_MAX_MEV |
| recoil endpoint | 2.940351893369968 | keVnr | kinematics.py | recoil_max_exact_keV |
| reconstructed support | 160 to 350 | eVee | experiment.yaml | binning |
| binning | 19 bins, 10 eVee width | eVee | experiment.yaml | reco_energy_bin_edges_evee |
| quenching | Lindhard Ge, k = 0.162 | dimensionless | detector_response.py | lindhard_quenching_ge |
| resolution | Gaussian sigma0/F/eta | eVee | detector_response.py | resolution_width_evee |
| efficiency | ideal step at 160 eVee | dimensionless | detector_response.py | conus_ge73_efficiency |
| output | expected events per reconstructed-energy bin | events/bin | slow_counts_conus_plus_ge73_pheno.py | slow_counts_conus_plus_ge73_pheno |
| Slow total prediction | 150.49434598713285 | events | 09_NUMERICAL_VALIDATION.md | slow_reference.npy |

## Intended Physical Claim

```text
current_intent: USER_DEFINED_MODEL
intended_claim: PHENOMENOLOGY_MODEL
same_physical_dataset_as_official_CONUS_PLUS: NO
```

The current implementation explicitly says it must not be mixed with the
official C2/C3/C5 detector-by-detector model. Therefore agreement with the
official 347-event benchmark cannot be claimed from the current dataset
definition.

## External Contract

| Field | External reference value | Unit | Reference | Confidence |
|---|---:|---|---|---|
| experiment | CONUS+ at Leibstadt nuclear power plant | label | Nature/PMC article | HIGH |
| reactor operation | 119 | days | Nature/PMC article | HIGH |
| measured signal | 395 +/- 106 | events | Nature/PMC article | HIGH |
| predicted SM signal | 347 +/- 59 | events | Nature/PMC article | HIGH |
| exposure | 327 | kg day | Nature/PMC Methods | HIGH |
| detector inventory | HPGe detector setup, C2-C5 design family; official analysis uses detector-level model | detector labels | Nature/PMC and CONUS+ experiment paper | MEDIUM |
| threshold | as low as 160 | eVee | Nature/PMC and CONUS+ experiment paper | HIGH |
| flux at site | about 1.45e13 | cm^-2 s^-1 | CONUS+ experiment paper | MEDIUM |
| public full data release | not public at this stage | data availability | Nature/PMC article | HIGH |

## Contract Comparison

Full machine-readable table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_contract_comparison.csv
```

| Physics layer | Current implementation | External reference | Match | Importance | Confidence |
|---|---|---|---|---|---|
| dataset identity | conus_plus_ge73_pheno phenomenology model | Official CONUS+ run 1 detector-level result | DIFFERENT | CRITICAL | HIGH |
| run period | phenomenological_effective_dataset | Nov 2023-Jul 2024 reactor-on run 1 | DIFFERENT | HIGH | HIGH |
| detector inventory | one effective Ge73 detector | C2, C3 and C5 HPGe detectors | DIFFERENT | CRITICAL | HIGH |
| exposure | 119 kg day | 327 kg day reactor-on active-mass exposure | DIFFERENT | CRITICAL | HIGH |
| active mass | included in aggregate 119 kg day | 2.83 +/- 0.02 kg total active mass | DIFFERENT | HIGH | HIGH |
| target composition | pure effective Ge73 | natural HPGe isotope mix in detector crystals | DIFFERENT | HIGH | MEDIUM |
| source normalization | Phi0 = 1.5e13 cm^-2 s^-1 at detector | reactor antineutrino flux at 20.7 m, about 1.45e13 cm^-2 s^-1 | UNCERTAIN | MEDIUM | MEDIUM |
| source spectrum | Kopeikin low energy + Mueller high energy | official reactor-spectrum prediction | UNCERTAIN | MEDIUM | LOW |
| kinematics | Ge73 CEvNS kinematics | Ge CEvNS kinematics | MATCH | LOW | MEDIUM |
| cross section | CEvNS-pyEFT Li2026 full response for Ge73 | SM CEvNS with official assumptions | UNCERTAIN | HIGH | MEDIUM |
| quenching | Lindhard Ge k=0.162 | Lindhard theory with measured quenching parameter | MATCH | MEDIUM | MEDIUM |
| resolution | single Gaussian model | detector-dependent calibration | DIFFERENT | MEDIUM | MEDIUM |
| efficiency | ideal step at 160 eVee | official trigger/cut efficiencies | DIFFERENT | HIGH | MEDIUM |
| thresholds | 160 eVee | as low as 160 eVee | MATCH | MEDIUM | MEDIUM |
| observable definition | expected events/bin | official detector-level signal extraction | DIFFERENT | HIGH | HIGH |
| output units | expected events and events/bin | total events with uncertainty | MATCH | LOW | HIGH |
| statistical data mode | background-subtracted excess planned; not implemented | official background model and fit | MISSING_CURRENT | HIGH | HIGH |

## Layer Classification

| Layer | Classification | Importance | Confidence |
|---|---|---|---|
| dataset identity | DIFFERENT | CRITICAL | HIGH |
| observable and units | DIFFERENT | HIGH | HIGH |
| exposure and normalization | DIFFERENT | CRITICAL | HIGH |
| detector inventory | DIFFERENT | CRITICAL | HIGH |
| source | UNCERTAIN | MEDIUM | MEDIUM |
| target composition | DIFFERENT | HIGH | MEDIUM |
| kinematics | CONSISTENT | LOW | MEDIUM |
| cross section | UNCERTAIN | HIGH | MEDIUM |
| detector response | DIFFERENT | HIGH | MEDIUM |
| analysis window and binning | UNCERTAIN | MEDIUM | MEDIUM |
| statistics | MISSING | HIGH | HIGH |

## Normalization Ledger

Full table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_normalization_ledger.csv
```

| Factor | Value | Unit | Applied where | Number of applications | Expected |
|---|---:|---|---|---:|---|
| source flux | 1.5e13 | cm^-2 s^-1 | source.py flux normalization | 1 | official flux near 1.45e13 cm^-2 s^-1 |
| source geometry | not applied | dimensionless | not applied because flux is detector-position flux | 0 | no second geometry factor |
| nuclei per kg | 8.249507890410958e24 | kg^-1 | target_time_normalization | 1 | Ge73-only current contract |
| isotope abundance | 1.0 | dimensionless | implicit pure Ge73 | 1 | official natural Ge would require isotope mixture |
| exposure | 119 | kg day | target_time_normalization | 1 | official benchmark uses 327 kg day |
| seconds per day | 86400 | s/day | target_time_normalization | 1 | convert day to seconds once |
| differential cross section | computed | cm^2 keVnr^-1 | differential_cross_section_conus_ge73 | 1 | SM/Response contract |
| detector efficiency | step at 160 eVee | dimensionless | detector_response.py | 1 | official efficiency is detector/cut dependent |
| bin integration | 160-350 by 10 eVee | eVee | slow_counts_conus_plus_ge73_pheno.py | 1 | official binned public reference missing |

```text
NORMALIZATION_LEDGER_STATUS: SUSPICIOUS
```

Reason: internally there is no evidence for mass, live time, source geometry,
seconds/day, or isotope abundance being applied twice. The suspicious item is
external: the current exposure contract is 119 kg day, while the official
benchmark commonly used in external phenomenology is 327 kg day.

## Unit Ledger

Full table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_unit_ledger.csv
```

| Quantity | Current unit | Expected unit | Conversion | Status |
|---|---|---|---|---|
| dPhi/dE_nu | cm^-2 s^-1 MeV^-1 | cm^-2 s^-1 MeV^-1 | none | PASS |
| dSigma/dT | cm^2 keVnr^-1 | cm^2 keVnr^-1 | none | PASS |
| nuclei/kg | kg^-1 | kg^-1 | none | PASS |
| exposure | kg day | kg day converted to kg s | multiply by 86400 s/day | PASS |
| dN/dT | events keVnr^-1 | events keVnr^-1 | source * cross section * target seconds | PASS |
| response density | eVee^-1 | eVee^-1 | Gaussian density | PASS |
| dN/dE_reco | events eVee^-1 | events eVee^-1 | fold over recoil | PASS |
| counts/bin | expected events/bin | events/bin or total events depending benchmark | integrate over bin | PASS |
| experimental plotted quantity | not implemented as official detector spectrum | official signal extraction | requires external data release | UNCERTAIN |

Do not compare the 19-bin current spectrum to official plotted points unless
the official plotted quantity, normalization, detector selection, and units are
all established.

## Numerical Sanity Checks

Full table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_numerical_sanity_checks.csv
```

| Check | Value | Unit |
|---|---:|---|
| current total event prediction | 150.49434598713285 | events |
| event rate per kg day | 1.2646583696397718 | events kg^-1 day^-1 |
| official benchmark total | 347 | events |
| official benchmark sigma | 59 | events |
| current minus benchmark | -196.50565401286715 | events |
| relative difference to benchmark | -0.5662987147344875 | dimensionless |
| pull versus benchmark prediction uncertainty | -3.330604305302833 | sigma_reference |
| exposure-only diagnostic total | 413.5432868722054 | events |
| exposure-only relative difference to benchmark | 0.1917673973262403 | dimensionless |
| fraction first five bins | 0.729571555243437 | dimensionless |
| fraction above 300 eVee | 0.01710550443727139 | dimensionless |
| integrated source flux | 14999999978239.064 | cm^-2 s^-1 |
| maximum recoil at 10 MeV | 2.940351893369968 | keVnr |
| response normalization max absolute error | 2.220446049250313e-16 | dimensionless |

## One-Factor Diagnostic Estimates

These are diagnostic-only calculations. They do not modify production code or
reference arrays.

| Difference | Baseline | Diagnostic change | New result | Ratio to baseline | Distance from benchmark before | Distance from benchmark after |
|---|---:|---|---:|---:|---:|---:|
| Exposure | 150.49434598713285 | 119 kg day -> 327 kg day | 413.5432868722054 | 2.7478991596638656 | -56.62987147344875% | +19.17673973262403% |
| Target composition | 150.49434598713285 | pure Ge73 -> natural Ge | not computed | not computed | -56.62987147344875% | unknown |
| Detector inventory | 150.49434598713285 | effective Ge73 -> detector-level C2/C3/C5 | not computed | not computed | -56.62987147344875% | unknown |
| Detector response | 150.49434598713285 | ideal threshold -> official efficiencies/resolutions | not computed | not computed | -56.62987147344875% | unknown |
| Statistics | 150.49434598713285 | expected counts -> official background/signal fit | not computed | not computed | -56.62987147344875% | unknown |

## Diagnostic Migration Table

Full table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_diagnostic_migration_table.csv
```

| Step | Physics definition | Total prediction | Ratio to previous | Difference from benchmark |
|---:|---|---:|---:|---:|
| 1 | Unchanged current phenomenology implementation | 150.49434598713285 |  | -0.5662987147344875 |
| 2 | DIAGNOSTIC ONLY: replace exposure 119 kg day by 327 kg day, all else unchanged | 413.5432868722054 | 2.7478991596638656 | 0.1917673973262403 |

Conclusion: exposure is a major mismatch, but exposure alone overshoots the
published predicted total. A full official dataset rebuild must also address
detector inventory, isotope composition, detector response, analysis window,
and statistics.

## Issue Cards

### ISSUE 1 - Dataset Identity

Status:

```text
DIFFERENT
```

Current:

```text
conus_plus_ge73_pheno: one effective Ge73 phenomenology dataset.
```

Reference:

```text
Official CONUS+ detector-level observation at Leibstadt.
```

Why it matters:

```text
Dataset identity determines whether a numerical benchmark comparison is valid.
The current run records explicitly say this is not the official C2/C3/C5 model.
```

Diagnostic result:

```text
Current prediction = 150.49434598713285 events.
Official predicted benchmark = 347 +/- 59 events.
```

Conclusion:

```text
The current implementation may be a valid phenomenology model, but it cannot
claim official CONUS+ reproduction.
```

Recommended action:

```text
REBUILD_OFFICIAL_DATASET
```

User decision:

```text
[ ] accept current phenomenology definition
[ ] create official detector-level definition
[ ] inspect more evidence
```

### ISSUE 2 - Observable And Output Unit

Status:

```text
DIFFERENT
```

Current:

```text
Expected events per reconstructed-energy bin, summed over one effective Ge73
detector model.
```

Reference:

```text
Official extracted neutrino signal and SM prediction with uncertainty from a
detector-level analysis.
```

Why it matters:

```text
The official number is not simply a 19-bin pure-Ge73 spectrum in the current
workflow. It includes detector-level data treatment and uncertainty handling.
```

Diagnostic result:

```text
Units are internally consistent, but the observable contract is not the same
as the official analysis contract.
```

Conclusion:

```text
Do not compare bin-by-bin shapes until the official plotted quantity and
normalization convention are established.
```

### ISSUE 3 - Exposure And Normalization

Status:

```text
DIFFERENT
```

Current:

```text
119 kg day
```

Reference:

```text
327 kg day
```

Why it matters:

```text
Event counts scale linearly with exposure when all other physics is held fixed.
```

Diagnostic result:

```text
Current prediction = 150.49434598713285
Exposure-only diagnostic = 413.5432868722054
Reference = 347 +/- 59
```

Conclusion:

```text
Exposure is definitely inconsistent with the external benchmark. It explains
a large part of the sign and scale of the discrepancy, but not the full
benchmark because exposure-only scaling overshoots the official prediction.
```

User decision:

```text
[ ] accept current phenomenology definition
[ ] create official detector-level definition
[ ] inspect more evidence
```

### ISSUE 4 - Detector Inventory

Status:

```text
DIFFERENT
```

Current:

```text
One effective Ge73 detector.
```

Reference:

```text
Official CONUS+ detector-level setup using HPGe detector channels rather than
one pure-isotope effective detector.
```

Why it matters:

```text
Detector inventory controls active mass, detector-dependent threshold,
resolution, trigger efficiency, background model, and exposure accounting.
```

Diagnostic result:

```text
Not computed because detector-specific public arrays were not available in the
current repository.
```

Conclusion:

```text
A detector-level official reproduction cannot be derived from the current
single-effective-detector contract.
```

### ISSUE 5 - Source

Status:

```text
UNCERTAIN
```

Current:

```text
Kopeikin-Mueller reactor electron-antineutrino spectrum normalized to
1.5e13 cm^-2 s^-1 at detector position.
```

Reference:

```text
Official reactor source at 20.7 m, with flux near 1.45e13 cm^-2 s^-1 in the
CONUS+ design paper. The full official source spectrum used in the final
Nature analysis is not imported here.
```

Why it matters:

```text
Source normalization and shape can change the expected event total and recoil
shape.
```

Diagnostic result:

```text
Current integrated flux = 14999999978239.064 cm^-2 s^-1.
```

Conclusion:

```text
The source is internally validated, but external official-source equivalence
is not established.
```

### ISSUE 6 - Target Composition

Status:

```text
DIFFERENT
```

Current:

```text
Pure effective Ge73.
```

Reference:

```text
Official HPGe detector material is natural germanium unless an official
detector-level isotope inventory states otherwise.
```

Why it matters:

```text
CEvNS scales strongly with neutron number and target mass. A pure Ge73 model
is not the same as a natural Ge isotope sum.
```

Diagnostic result:

```text
Not computed because validated isotope-response components for a full natural
Ge CONUS+ detector-level model are not assembled in this dataset.
```

Conclusion:

```text
This is a high-priority difference after dataset/exposure identity.
```

### ISSUE 7 - Kinematics And Cross Section

Status:

```text
UNCERTAIN
```

Current:

```text
CEvNS-pyEFT Li2026 full-response cross section through Ge73 Response data.
```

Reference:

```text
Official SM CEvNS prediction with collaboration assumptions.
```

Why it matters:

```text
Even after normalization is corrected, a different nuclear-response or form
factor model can change the total and spectrum.
```

Diagnostic result:

```text
Internal kinematics pass. Maximum recoil at 10 MeV = 2.940351893369968 keVnr.
```

Conclusion:

```text
Kinematics look physically consistent for Ge, but official cross-section
equivalence is not proven.
```

### ISSUE 8 - Detector Response

Status:

```text
DIFFERENT
```

Current:

```text
Lindhard Ge quenching with k = 0.162, one Gaussian resolution model, and an
ideal step efficiency at 160 eVee.
```

Reference:

```text
Official CONUS+ uses detector-dependent trigger efficiencies, cuts, resolution
calibrations, and background modelling.
```

Why it matters:

```text
The CEvNS spectrum is concentrated near threshold; efficiency and resolution
near 160 eVee can materially change the prediction.
```

Diagnostic result:

```text
Internal response normalization max absolute error = 2.220446049250313e-16.
```

Conclusion:

```text
The current response is internally normalized but not an official
detector-level response.
```

### ISSUE 9 - Analysis Window And Binning

Status:

```text
UNCERTAIN
```

Current:

```text
160 <= E_reco < 350 eVee, 19 bins of 10 eVee.
```

Reference:

```text
Official total benchmark is not provided as a matching 19-bin machine-readable
spectrum in the current repository.
```

Why it matters:

```text
Changing the upper analysis window, binning, or plotted quantity can change
the total and any shape comparison.
```

Diagnostic result:

```text
Current fraction above 300 eVee = 0.01710550443727139.
```

Conclusion:

```text
The current 160-350 eVee window is a phenomenology choice until matched to a
public official analysis window.
```

### ISSUE 10 - Statistics

Status:

```text
MISSING
```

Current:

```text
Statistics module is planned but not implemented in the validated current
state.
```

Reference:

```text
Official result uses signal extraction with backgrounds, detector data, and
uncertainties.
```

Why it matters:

```text
The official 395 +/- 106 measurement and 347 +/- 59 prediction are not simply
raw counts from the current Slow function.
```

Diagnostic result:

```text
No official likelihood or per-bin covariance is implemented.
```

Conclusion:

```text
Statistics should not be debugged before rebuilding the official physics
contract; this audit stops before statistics.
```

## Discrepancy Tree

```text
Observed discrepancy: current 150.49434598713285 vs official predicted 347
|
+-- Dataset identity [DIFFERENT]
|
+-- Normalization [DIFFERENT]
|   +-- exposure [DIFFERENT: 119 kg day vs 327 kg day]
|   +-- mass/live time [UNKNOWN external detector-level split]
|   +-- source normalization [UNCERTAIN: 1.5e13 vs about 1.45e13]
|   +-- nuclei/kg [OK internal Ge73; DIFFERENT external natural Ge]
|
+-- Source shape [UNKNOWN]
|
+-- Target composition [DIFFERENT]
|
+-- Cross section [UNCERTAIN]
|
+-- Detector [DIFFERENT]
|   +-- threshold [OK approximate 160 eVee]
|   +-- efficiency [DIFFERENT: ideal step vs official detector efficiency]
|   +-- resolution [DIFFERENT: one model vs detector-dependent]
|   +-- quenching [OK/UNCERTAIN: same Lindhard class, official details not fully imported]
|
+-- Observable / units [DIFFERENT]
|
+-- Statistical definition [MISSING_CURRENT]
```

## Figures

Generated audit figures:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/audit_total_benchmark.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/audit_total_benchmark.pdf
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/audit_current_spectrum_and_cumulative.png
workflows/experiment-integration/runs/conus_plus_ge73_pheno/figures/audit_current_spectrum_and_cumulative.pdf
```

The first figure compares current total events, exposure-only diagnostic total,
official predicted total, and official measured total. The second figure shows
the current 19-bin spectrum and cumulative events, plus the exposure-only
diagnostic. Both figures label units explicitly.

## Ranked Likely Causes

Full table:

```text
workflows/experiment-integration/runs/conus_plus_ge73_pheno/artifacts/physics_audit_issue_ranking.csv
```

| Rank | Issue | Severity | Confidence | Estimated impact |
|---:|---|---|---|---|
| 1 | dataset identity | CRITICAL | HIGH | Defines whether official reproduction can be claimed. |
| 2 | exposure and detector inventory | CRITICAL | HIGH | Exposure-only diagnostic changes total by factor 2.748. |
| 3 | target composition | HIGH | MEDIUM | May change rate and spectral shape at moderate/high level. |
| 4 | detector response/statistics | HIGH | MEDIUM | Can explain remaining discrepancy after exposure scaling. |
| 5 | source model | MEDIUM | LOW | Likely moderate, but evidence incomplete. |

## Final Classification

```text
PHYSICS_AUDIT = MISMATCH
```

Reason:

```text
The implementation is internally valid for the declared phenomenological
Ge73 dataset, but one or more external physics contracts disagree with the
official CONUS+ benchmark. The mismatch is documented before any parameter
tuning or repair.
```

Exactly one recommended next action:

```text
REBUILD_OFFICIAL_DATASET
```

This means creating a separate official CONUS+ detector-level dataset contract
with official detector inventory, exposure, target composition, detector
response, analysis window, and statistical treatment. It does not mean deleting
the current phenomenological model.
