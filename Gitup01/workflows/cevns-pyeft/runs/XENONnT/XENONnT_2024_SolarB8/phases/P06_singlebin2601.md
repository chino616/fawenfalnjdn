# P06：独立单bin能力（2601.19883v2）

[同源物理/输入/原文/代码/SM结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)

与旧多bin阶段并列；旧gates不重命名、不借用PASS。P06/P07的范围是已有接受度积分及尾段上下界；完整X信号点/联合χ²仍缺尾数据。输入与结果均按本分支标识绑定。

```json phase-result
{
  "schema_version": 1,
  "phase": "P06",
  "capability_id": "solar_b8.singlebin2601.P06",
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
    "representation": "bin_probability",
    "unit": "1",
    "normalization": "sum_at_most_one",
    "included_selections": [
      "published Total/combined ROI selection"
    ],
    "axes": {
      "input": "true nuclear recoil T [keVnr]",
      "output": "one selected fitted-signal yield bin"
    },
    "response_definition": "epsilon(T) is the one-bin accepted probability; X upper-tail probability remains unknown",
    "selection_ownership": "Total/combined includes ROI once; no additional Qy/Ne/cS2 window",
    "validity_domain": {
      "XENONnT": [
        0.5,
        2.77000000180804
      ]
    }
  }
}
```
