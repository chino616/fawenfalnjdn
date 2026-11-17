# P10: sm_delivery

2026-11-07。按明确交付能力记录机器检查；没有把PARTIAL改成FULLY_INTEGRATED。

物理实施范围见D0001/W0001。机器检查和实际输入/代码指纹见结构化记录；结果尚未由用户验收，不将其记为APPROVED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.sm_delivery",
  "workspace": "canonical",
  "plan_status": "BLOCKED",
  "machine_gate": "BLOCKED",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/00_PHASE0_PLAN.md",
  "input_refs": [
    "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml",
    "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz"
  ],
  "input_fingerprint": "b64c409dee66c30456a8fe7e851c2120524cf005ca4317c0ad99374e72880dde",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0001"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/SM_RESULT.json",
      "sha256": "4290108d9ba41818818bcfc9d19972bee426cbdfa2698f0352d7a809efd6249a",
      "role": "actual result or package"
    },
    {
      "path": "outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/REFERENCE_COMPARISON.json",
      "sha256": "a44f0fd005980c268a3ad117e451feeaaa3db5d5b89b5b4a04012cc0ff532e15",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml",
      "sha256": "c7299d35b5fdb192b425a12cb8b5571ea5218619e1bb5ce2f689e8b08bc1e046",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz",
      "sha256": "56a44e766476c7bc8771e2e98e316c48a97e13d485d006d12324ba473b4f09b8",
      "role": "actual result or package"
    }
  ],
  "checks": [
    {
      "name": "actual artifact and scoped computation",
      "status": "BLOCKED",
      "command": "python -B tools/run_solar_b8_sm_benchmark.py",
      "result_ref": "outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/SM_RESULT.json"
    }
  ],
  "handoff": {
    "delivery_scope": {
      "mode": "dataset_onboarding",
      "target": "canonical SM forward benchmark, response limitations explicit",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "true_recoil_projection",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/SM_RESULT.json"
      },
      {
        "id": "electron_spectrum",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SM_BENCHMARK_REPORT.md"
      }
    ],
    "validation_levels": {
      "numerical_convergence": "PASS",
      "package_Runtime": "PASS",
      "new_contract_tests": "see QA report",
      "existing_regressions": "see QA report",
      "strict_paper_reproduction": "NOT_CERTIFIED",
      "official_likelihood": "NOT_REQUESTED"
    },
    "runtime_integration": "standard package loader/scoped Catalog/predict_experiment; no unconditional global activation",
    "final_claim": "partial: true recoil only, Ne signal not calculated",
    "limitations": [
      "true-recoil acceptance projection only",
      "US2 electron response absent; no SM Ne spectrum computed",
      "human result acceptance NOT_REVIEWED"
    ]
  }
}
```
