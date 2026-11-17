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
  "scope_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SINGLEBIN_BRANCH.json",
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
      "path": "outputs/solar_b8_singlebin/20261111_response_run2/XENONnT/SM_RESULT.json",
      "sha256": "b9397438f68950aeaa7281f02845c6f315f4ce282821ee96ee8faed6c6f18d6b",
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
    "exact_claim": "PARTIAL_XENON_ACCEPTANCE_TAIL",
    "samples": [
      "XENONnT"
    ],
    "full_likelihood": "Eq88 fitted signal Gaussian, not official likelihood",
    "fast": "NOT_REQUESTED",
    "scientific_result_acceptance": "NOT_REVIEWED",
    "remaining": [
      "full X2024 acceptance from last native point to 3keV missing",
      "Xe124/Xe126 missing, no renormalization",
      "external nuclear-table source certification unresolved; direct local reuse authorized"
    ],
    "normalization_ledger": {
      "XENONnT": {
        "flux": {
          "input_unit": "cm^-2 s^-1 MeV^-1",
          "live_seconds": 31557600.0,
          "output_unit": "cm^-2 MeV^-1",
          "geometry_included": true
        },
        "exposure_tyr": 3.51,
        "normalization": "one reference-year fluence * original nuclei/tonne * exposure_tyr, once",
        "efficiency": "Total including ROI, once; no extra Ne/S2 window",
        "ci": "absent"
      }
    },
    "output_contract": "one event count per independently identified fitted-signal sample; X partial count plus rigorous full interval",
    "numerics_and_convergence": {
      "XENONnT": {
        "runs": [
          {
            "step": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              11.811080392197173
            ],
            "full_interval_events": [
              11.811080392197173,
              12.168979828386991
            ],
            "seconds": 14.06996460002847
          },
          {
            "step": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              11.8117241003614
            ],
            "full_interval_events": [
              11.8117241003614,
              12.169536845684412
            ],
            "seconds": 12.170244399923831
          },
          {
            "step": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              11.811906272511912
            ],
            "full_interval_events": [
              11.811906272511912,
              12.169698346499638
            ],
            "seconds": 23.08180819998961
          },
          {
            "step": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              11.812101957495969
            ],
            "full_interval_events": [
              11.812101957495969,
              12.16995505731046
            ],
            "seconds": 1.1672548999777064
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              0.00018217215051130609,
              0.00018217215051130609,
              0.00016150081522603443
            ],
            "tolerance_events": [
              0.023623812545023826,
              0.023623812545023826,
              0.024339396692999275
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "checked": "predicted count and both full-interval endpoints",
            "absolute_difference": [
              0.00019568498405675427,
              0.00019568498405675427,
              0.00025671081082201397
            ],
            "tolerance_events": [
              0.02362420391499194,
              0.02362420391499194,
              0.02433991011462092
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
        "XENONnT": "f54732cd010dffd66fe93d6f98e58c78eb2a289abdb972a21949e7a60da75a24"
      },
      "result_acceptance": "NOT_REVIEWED"
    }
  }
}
```
