# P10：独立单bin能力（2601.19883v2）

[同源物理/输入/原文/代码/SM结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>)

与旧多bin阶段并列；旧gates不重命名、不借用PASS。P06/P07的范围是已有接受度积分及尾段上下界；完整X信号点/联合χ²仍缺尾数据。输入与结果均按本分支标识绑定。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.singlebin2601.P10",
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
    "delivery_scope": {
      "mode": "capability_change",
      "target": "independent singlebin SM nuclear-Response analysis; human scientific acceptance pending",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "bounded_SM_forward",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json"
      },
      {
        "id": "complete_signal_point_and_Eq88",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json"
      }
    ],
    "validation_levels": {
      "internal_contracts": "outputs/solar_b8_singlebin/20261111_validation/TEST_VALIDATION.json",
      "source_and_snapshot": "outputs/solar_b8_singlebin/20261111_validation/INPUT_AND_SNAPSHOT_AUDIT.json",
      "numerical_convergence": "all samples independently refined",
      "paper_equivalence": "NOT_CERTIFIED"
    },
    "runtime_integration": "load_singlebin -> PreparedExperiment -> predict_experiment / evaluate_experiment; scoped catalog, global default IDs unchanged",
    "final_claim": "CALCULATED for seven directly adopted local Xe response tables; no official-likelihood or paper-code identity claim",
    "limitations": [
      "Xe124/Xe126 missing, no renormalization",
      "external nuclear-table source certification unresolved; direct local reuse authorized"
    ]
  }
}
```
