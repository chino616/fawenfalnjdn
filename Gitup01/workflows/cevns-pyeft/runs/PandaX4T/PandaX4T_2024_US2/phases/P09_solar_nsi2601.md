# P09：太阳电子味矢量NSI独立单bin分支

[v3.3同源onboarding/来源/代码/实际结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>)

技术计算已执行；执行授权不等于科学结果接受。P08尚无Slow结果人工接受；P10精确图形复现未成立，分别保持正式门槛未通过。旧分支不变。

```json phase-result
{
  "schema_version": 1,
  "phase": "P09",
  "capability_id": "solar_b8.ee_vector_nsi2601.P09",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SOLAR_NSI_BRANCH.json",
  "input_refs": [
    "data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json",
    "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json"
  ],
  "input_fingerprint": "ee6d5d5e0844e01692ca5612e778e2785db41dcab9172bb89d0955b01830f256",
  "evidence_refs": [
    "data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json",
    "outputs/solar_b8_nsi/20261112_fig4_run2/QA.json"
  ],
  "decision_refs": [
    "D0006"
  ],
  "approval_refs": [
    "W0006"
  ],
  "artifacts": [
    {
      "path": "outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json",
      "sha256": "d8d2d81f5ec523c98fc1dffb665f7b354775855deebf045fbc6672b32a0f7956",
      "role": "actual three-sample NSI calculation; assumptions and paper discrepancy explicit"
    }
  ],
  "checks": [
    {
      "name": "actual numerical forward and inference checks",
      "status": "PASS",
      "command": "python -B tools/finalize_solar_b8_nsi.py --check",
      "result_ref": "outputs/solar_b8_nsi/20261112_fig4_run2/QA.json"
    }
  ],
  "handoff": {
    "channels": [
      {
        "id": "PandaX_paired",
        "representation": "binned_counts",
        "processing": "other",
        "design": "single_sample",
        "likelihood": "gaussian",
        "requires_covariance": false
      },
      {
        "id": "PandaX_US2",
        "representation": "binned_counts",
        "processing": "other",
        "design": "single_sample",
        "likelihood": "gaussian",
        "requires_covariance": false
      },
      {
        "id": "XENONnT",
        "representation": "binned_counts",
        "processing": "other",
        "design": "single_sample",
        "likelihood": "gaussian",
        "requires_covariance": false
      }
    ],
    "prediction_binding": "same three NSI model/kernel/analysis identities, all flavors retained",
    "required_inputs": {
      "available": true,
      "sources": [
        "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json",
        "data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json"
      ],
      "missing": []
    },
    "nuisance_model": "three independent12% Gaussian pulls; exact printed percentages; flat-tail conditional primary, alternatives separate",
    "inference": "each scheme subtracts its own joint global-parameter minimum; Delta<=4.61;601x601; finite enclosing-domain proof,3DE seeds and independent multistart",
    "claim_level": "approximate",
    "benchmark": "outputs/solar_b8_nsi/20261112_fig4_run2/PAPER_COMPARISON.json"
  }
}
```
