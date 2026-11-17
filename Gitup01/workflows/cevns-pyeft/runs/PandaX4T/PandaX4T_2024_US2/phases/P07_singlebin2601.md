# P07：独立单bin能力（2601.19883v2）

[同源物理/输入/原文/代码/SM结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)

与旧多bin阶段并列；旧gates不重命名、不借用PASS。P06/P07的范围是已有接受度积分及尾段上下界；完整X信号点/联合χ²仍缺尾数据。输入与结果均按本分支标识绑定。

```json phase-result
{
  "schema_version": 1,
  "phase": "P07",
  "capability_id": "solar_b8.singlebin2601.P07",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SINGLEBIN_BRANCH.json",
  "input_refs": [
    "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json",
    "data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json"
  ],
  "input_fingerprint": "50c510dbe07d4f41b5c38ce897d1610efcfcc389e107d621009fc57334a0d316",
  "evidence_refs": [
    "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json"
  ],
  "decision_refs": [
    "D0005"
  ],
  "approval_refs": [
    "W0005"
  ],
  "artifacts": [
    {
      "path": "outputs/solar_b8_singlebin/20261111_response_run2/PandaX_paired/SM_RESULT.json",
      "sha256": "0dbee7544d5f9db8b92d1a16a9c3b6a50818df04a29efedd1ae449d2818b7c22",
      "role": "actual SM calculation with convergence and claim"
    },
    {
      "path": "outputs/solar_b8_singlebin/20261111_response_run2/PandaX_US2/SM_RESULT.json",
      "sha256": "13bdf3832b4c496c798ddb552097c564db2367997c85bb8d8e5c84e24c8af81f",
      "role": "actual SM calculation with convergence and claim"
    }
  ],
  "checks": [
    {
      "name": "independent SM integral, declared coverage and separate grids",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_singlebin_benchmark.py --output outputs/solar_b8_singlebin/20261111_response_run2",
      "result_ref": "outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json"
    }
  ],
  "handoff": {
    "exact_claim": "CALCULATED",
    "samples": [
      "PandaX_paired",
      "PandaX_US2"
    ],
    "full_likelihood": "Eq88 fitted signal Gaussian, not official likelihood",
    "fast": "NOT_REQUESTED",
    "scientific_result_acceptance": "NOT_REVIEWED",
    "remaining": [
      "Xe124/Xe126 missing, no renormalization",
      "external nuclear-table source certification unresolved; direct local reuse authorized"
    ],
    "normalization_ledger": {
      "PandaX_paired": {
        "flux": {
          "input_unit": "cm^-2 s^-1 MeV^-1",
          "live_seconds": 31557600.0,
          "output_unit": "cm^-2 MeV^-1",
          "geometry_included": true
        },
        "exposure_tyr": 1.2,
        "normalization": "one reference-year fluence * original nuclei/tonne * exposure_tyr, once",
        "efficiency": "Total including ROI, once; no extra Ne/S2 window",
        "ci": "absent"
      },
      "PandaX_US2": {
        "flux": {
          "input_unit": "cm^-2 s^-1 MeV^-1",
          "live_seconds": 31557600.0,
          "output_unit": "cm^-2 MeV^-1",
          "geometry_included": true
        },
        "exposure_tyr": 1.04,
        "normalization": "one reference-year fluence * original nuclei/tonne * exposure_tyr, once",
        "efficiency": "Total including ROI, once; no extra Ne/S2 window",
        "ci": "absent"
      }
    },
    "output_contract": "one event count per independently identified fitted-signal sample; X partial count plus rigorous full interval",
    "numerics_and_convergence": {
      "PandaX_paired": {
        "runs": [
          {
            "step": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              2.48752550460365
            ],
            "full_interval_events": [
              2.48752550460365,
              2.48752550460365
            ],
            "seconds": 13.96735529997386
          },
          {
            "step": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              2.4875535679839333
            ],
            "full_interval_events": [
              2.4875535679839333,
              2.4875535679839333
            ],
            "seconds": 11.453077199985273
          },
          {
            "step": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              2.487561884394486
            ],
            "full_interval_events": [
              2.487561884394486,
              2.487561884394486
            ],
            "seconds": 22.79778789996635
          },
          {
            "step": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              2.487612254108568
            ],
            "full_interval_events": [
              2.487612254108568,
              2.487612254108568
            ],
            "seconds": 1.1597506999969482
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              8.31641055265564e-06,
              8.31641055265564e-06,
              8.31641055265564e-06
            ],
            "tolerance_events": [
              0.004975123768788972,
              0.004975123768788972,
              0.004975123768788972
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              5.0369714081899275e-05,
              5.0369714081899275e-05,
              5.0369714081899275e-05
            ],
            "tolerance_events": [
              0.004975224508217136,
              0.004975224508217136,
              0.004975224508217136
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "PandaX_US2": {
        "runs": [
          {
            "step": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              47.04018091847705
            ],
            "full_interval_events": [
              47.04018091847705,
              47.04018091847705
            ],
            "seconds": 16.95596660010051
          },
          {
            "step": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              47.04132115750331
            ],
            "full_interval_events": [
              47.04132115750331,
              47.04132115750331
            ],
            "seconds": 11.510829200036824
          },
          {
            "step": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              47.041734510059584
            ],
            "full_interval_events": [
              47.041734510059584,
              47.041734510059584
            ],
            "seconds": 23.686093399999663
          },
          {
            "step": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              47.04205975616543
            ],
            "full_interval_events": [
              47.04205975616543,
              47.04205975616543
            ],
            "seconds": 1.385963200009428
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              0.00041335255627217293,
              0.00041335255627217293,
              0.00041335255627217293
            ],
            "tolerance_events": [
              0.09408346902011917,
              0.09408346902011917,
              0.09408346902011917
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              0.0003252461058451672,
              0.0003252461058451672,
              0.0003252461058451672
            ],
            "tolerance_events": [
              0.09408411951233087,
              0.09408411951233087,
              0.09408411951233087
            ],
            "passed": true
          }
        ],
        "passed": true
      }
    },
    "reference_comparison": "R4 Table II is external, different 5.16e6 flux; never used for scaling",
    "freeze_scope": {
      "physics_fingerprints": {
        "PandaX_paired": "de18a1f56fcd95e2c85b9d0721a5f3ad5b31e2e522ec142f34cfcf2312a8fac5",
        "PandaX_US2": "29c1f3f74a96333c718171ad325255989af092b713693abd968e7fc2a935516b"
      },
      "result_acceptance": "NOT_REVIEWED"
    }
  }
}
```
