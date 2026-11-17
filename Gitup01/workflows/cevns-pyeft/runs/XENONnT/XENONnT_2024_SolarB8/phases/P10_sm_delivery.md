# P10: sm_delivery

2026-11-07。按明确交付能力记录机器检查；没有把PARTIAL改成FULLY_INTEGRATED。

物理实施范围见D0001/W0001。机器检查和实际输入/代码指纹见结构化记录；结果尚未由用户验收，不将其记为APPROVED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.sm_delivery",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/00_PHASE0_PLAN.md",
  "input_refs": [
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz"
  ],
  "input_fingerprint": "b1311e633159e0d57dfb57290181d68cb3399ef530e63d83292183e20b90e6b1",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0001"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json",
      "sha256": "910c0641cc21d82cc14a55c09692d3dc16499bfaf2fea1a699463923c81305c0",
      "role": "actual result or package"
    },
    {
      "path": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/REFERENCE_COMPARISON.json",
      "sha256": "e2667121f0378025bc11b7b0a8827ad48962cf6be16b53794fa711a33ce1c4f7",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
      "sha256": "271e18b89398ed90c29db2f88924a10514125328a7c27f69de49baa33c1111c4",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz",
      "sha256": "39aa001f5c5657ddbb0099f232ee7e2a81f78ff383da3cf43b0dc214b62fdeb2",
      "role": "actual result or package"
    }
  ],
  "checks": [
    {
      "name": "actual artifact and scoped computation",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_sm_benchmark.py",
      "result_ref": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json"
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
        "id": "sm_forward",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json"
      },
      {
        "id": "electron_spectrum",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SM_BENCHMARK_REPORT.md"
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
    "final_claim": "SM forward reference with explicit public model limits",
    "limitations": [
      "public recasting response has independent model approximation; numerical convergence is not paper equivalence",
      "human result acceptance NOT_REVIEWED"
    ]
  }
}
```
