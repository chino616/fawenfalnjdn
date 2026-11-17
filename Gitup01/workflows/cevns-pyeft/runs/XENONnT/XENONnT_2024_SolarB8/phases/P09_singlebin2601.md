# P09：独立单bin能力（2601.19883v2）

[同源物理/输入/原文/代码/SM结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)

与旧多bin阶段并列；旧gates不重命名、不借用PASS。P06/P07的范围是已有接受度积分及尾段上下界；完整X信号点/联合χ²仍缺尾数据。输入与结果均按本分支标识绑定。

```json phase-result
{
  "schema_version": 1,
  "phase": "P09",
  "capability_id": "solar_b8.singlebin2601.P09",
  "workspace": "canonical",
  "plan_status": "BLOCKED",
  "machine_gate": "BLOCKED",
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
    "full_likelihood": "BLOCKED missing X acceptance tail",
    "fast": "NOT_REQUESTED",
    "scientific_result_acceptance": "NOT_REVIEWED",
    "remaining": [
      "full X2024 acceptance from last native point to 3keV missing",
      "Xe124/Xe126 missing, no renormalization",
      "external nuclear-table source certification unresolved; direct local reuse authorized"
    ],
    "channels": [
      {
        "id": "XENONnT",
        "representation": "binned_counts",
        "processing": "other",
        "processing_detail": "experiment-fitted signal yield; not raw candidate counts",
        "design": "single_sample",
        "likelihood": "gaussian",
        "requires_covariance": false
      }
    ],
    "prediction_binding": {
      "XENONnT": "f54732cd010dffd66fe93d6f98e58c78eb2a289abdb972a21949e7a60da75a24"
    },
    "required_inputs": {
      "available": false,
      "sources": [
        "data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json"
      ],
      "missing": [
        "full X2024 acceptance from last native point to 3keV missing"
      ]
    },
    "nuisance_model": "R1 Eq.88: independent Gaussian alpha_k, sigma_alpha=0.12 for every sample",
    "inference": "fixed SM objective only; no confidence interval or parameter fit",
    "claim_level": "approximate",
    "benchmark": "analytic profile against independent numerical optimizer; external R4 arithmetic only"
  }
}
```
