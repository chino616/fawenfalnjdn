# Numerical Validation: conus_plus_ge73_pheno

## 1. Validation Scope
This validation reads and summarizes completed Source, Kinematics, Detector Response, Slow, and cumulative Fast artifacts. It does not execute the statistics Skill and does not modify production code, `experiment.yaml`, or reference arrays.

## 2. Source Summary

Source integral: `1.499999997824e+13` cm^-2 s^-1; reference `1.5e13`; relative error `1.450729036458e-09`.

2 MeV matching with delta `1e-07` MeV: left `2.920683331874e+12`, match `2.920683197073e+12`, right `2.920682979462e+12`, relative jump `7.450695797235e-08`.

## 3. Kinematics/Target Summary

Ge73: A=`73`, Z=`32`, N=`41`; target mass `6.799906957156e+01` GeV; T_max(10 MeV) `2.94035189336997` keVnr.

nuclei_per_kg `8.249507890411e+24`; target_seconds `8.481814032605e+31`.

## 4. Detector Response Summary

Max response normalization absolute error: `2.220446049250e-16`. Efficiency: epsilon(159.999)=`0.0`, epsilon(160)=`1.0`, epsilon(160.001)=`1.0`.

## 5. 19-bin Slow Table

| bin | E_low_eVee | E_high_eVee | artifact_counts | reference_counts | recomputed_counts | artifact_minus_reference | recomputed_minus_reference | relative_error | status |
| --- | ---------- | ----------- | --------------- | ---------------- | ----------------- | ------------------------ | -------------------------- | -------------- | ------ |
| 1   | 160        | 170         | 34.17365        | 34.17365         | not_run           | -1.44950718e-12          | not_run                    | 4.24159316e-14 | PASS   |
| 2   | 170        | 180         | 26.521691       | 26.521691        | not_run           | 4.03588274e-12           | not_run                    | 1.52172906e-13 | PASS   |
| 3   | 180        | 190         | 20.613441       | 20.613441        | not_run           | -4.05009359e-12          | not_run                    | 1.96478288e-13 | PASS   |
| 4   | 190        | 200         | 16.029145       | 16.029145        | not_run           | 9.23705556e-13           | not_run                    | 5.76266274e-14 | PASS   |
| 5   | 200        | 210         | 12.459439       | 12.459439        | not_run           | -4.41779946e-12          | not_run                    | 3.54574512e-13 | PASS   |
| 6   | 210        | 220         | 9.6732348       | 9.6732348        | not_run           | -2.71782596e-13          | not_run                    | 2.80963505e-14 | PASS   |
| 7   | 220        | 230         | 7.4958538       | 7.4958538        | not_run           | -1.37667655e-13          | not_run                    | 1.83658405e-14 | PASS   |
| 8   | 230        | 240         | 5.7938705       | 5.7938705        | not_run           | 4.07673895e-13           | not_run                    | 7.03629630e-14 | PASS   |
| 9   | 240        | 250         | 4.4644349       | 4.4644349        | not_run           | -3.94351218e-13          | not_run                    | 8.83317219e-14 | PASS   |
| 10  | 250        | 260         | 3.427636        | 3.427636         | not_run           | 1.70086167e-13           | not_run                    | 4.96220040e-14 | PASS   |
| 11  | 260        | 270         | 2.620971        | 2.620971         | not_run           | 4.45421477e-13           | not_run                    | 1.69945216e-13 | PASS   |
| 12  | 270        | 280         | 1.9952919       | 1.9952919        | not_run           | -2.51576537e-13          | not_run                    | 1.26085077e-13 | PASS   |
| 13  | 280        | 290         | 1.5118023       | 1.5118023        | not_run           | -2.16271445e-13          | not_run                    | 1.43055379e-13 | PASS   |
| 14  | 290        | 300         | 1.1398007       | 1.1398007        | not_run           | -3.03757020e-13          | not_run                    | 2.66500123e-13 | PASS   |
| 15  | 300        | 310         | 0.85496277      | 0.85496277       | not_run           | -4.45199433e-14          | not_run                    | 5.20723767e-14 | PASS   |
| 16  | 310        | 320         | 0.63801577      | 0.63801577       | not_run           | -4.59632332e-14          | not_run                    | 7.20409042e-14 | PASS   |
| 17  | 320        | 330         | 0.47370701      | 0.47370701       | not_run           | -1.11022302e-14          | not_run                    | 2.34369137e-14 | PASS   |
| 18  | 330        | 340         | 0.34999438      | 0.34999438       | not_run           | -3.71924713e-14          | not_run                    | 1.06265910e-13 | PASS   |
| 19  | 340        | 350         | 0.25740532      | 0.25740532       | not_run           | 1.21569421e-14           | not_run                    | 4.72287914e-14 | PASS   |

Slow total: `1.504943459871e+02`; min bin `2.574053192391e-01`; max bin `3.417364951955e+01`.

## 6. Slow Convergence Table

| label             | n_true_recoil | n_neutrino | reco_step_evee | total_counts | total_relative_delta_vs_reference | max_bin_relative_delta_vs_reference | runtime_s |
| ----------------- | ------------- | ---------- | -------------- | ------------ | --------------------------------- | ----------------------------------- | --------- |
| coarse            | 41            | 80         | 5              | 150.60904    | 0.00076210397                     | 0.0013250968                        | 1.8518512 |
| medium            | 61            | 120        | 2              | 150.48483    | 6.32334197e-05                    | 0.0001165398                        | 3.8938589 |
| default_reference | 121           | 240        | 1              | 150.49435    | 0.00000000                        | 0.00000000                          | 13.226071 |

Medium convergence: total relative delta `6.323341968326e-05`, max-bin relative delta `1.165397973771e-04`.

## 7. Fast/Slow Table

| point            | slow_total | fast_total | total_absolute_error | total_relative_error | max_bin_absolute_error | max_bin_relative_error | slow_runtime_s | fast_reconstruction_runtime_s | speedup   | status |
| ---------------- | ---------- | ---------- | -------------------- | -------------------- | ---------------------- | ---------------------- | -------------- | ----------------------------- | --------- | ------ |
| sm_full_response | 150.48483  | 150.48483  | 0.00000000           | 0.00000000           | 4.79616347e-14         | 5.75721709e-14         | 2.4246472      | 3.74000520e-05                | 64830.049 | PASS   |
| complex_c61u     | 151.44837  | 151.44837  | 0.00000000           | 0.00000000           | 3.91908728e-14         | 1.51286002e-13         | 3.8889334      | 6.34000171e-05                | 61339.627 | PASS   |
| helm_sm          | 149.22335  | 149.22335  | 8.52651283e-14       | 5.71392684e-16       | 3.63042929e-14         | 1.06937309e-13         | 0.5447895      | 4.99000307e-05                | 10917.619 | PASS   |

## 8. Runtime and Speedup

- `sm_full_response`: max relative error `5.757217090831e-14`, speedup `6.483004898152e+04`.

- `complex_c61u`: max relative error `1.512860019516e-13`, speedup `6.133962698999e+04`.

- `helm_sm`: max relative error `1.069373087233e-13`, speedup `1.091761853125e+04`.

## 9. Failed or Warning Checks

None.

## 10. Optional Blockers
EFT-template Fast is `BLOCKED`: complete 20-group EFT template basis mapping is not yet defined. This does not fail the current cumulative Fast validation.

## 11. Overall Status
`PASS_WITH_OPTIONAL_BLOCKER`

## 12. File Paths

- `notebooks\conus_plus_ge73_pheno_numerical_validation.ipynb`

- `workflows\experiment-integration\runs\conus_plus_ge73_pheno\09_NUMERICAL_VALIDATION.md`

- `workflows\experiment-integration\runs\conus_plus_ge73_pheno\artifacts\numerical_validation_summary.json`

- `workflows\experiment-integration\runs\conus_plus_ge73_pheno\artifacts\numerical_validation_checks.csv`

- `workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\numerical_validation_dashboard.png`

- `workflows\experiment-integration\runs\conus_plus_ge73_pheno\figures\numerical_validation_dashboard.pdf`

- `tests\reference_conus_plus_ge73_pheno\slow_reference.npy`

- `tests\reference_conus_plus_ge73_pheno\cumulative_reference.npz`

- `tests\reference_conus_plus_ge73_pheno\cumulative_reference.json`
