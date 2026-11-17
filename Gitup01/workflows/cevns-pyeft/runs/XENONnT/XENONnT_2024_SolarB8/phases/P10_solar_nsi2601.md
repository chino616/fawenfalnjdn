# P10：太阳电子味矢量NSI独立单bin分支

[v3.3同源onboarding/来源/代码/实际结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>)

技术计算已执行；执行授权不等于科学结果接受。P08尚无Slow结果人工接受；P10精确图形复现未成立，分别保持正式门槛未通过。旧分支不变。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.ee_vector_nsi2601.P10",
  "workspace": "canonical",
  "plan_status": "DRAFT",
  "machine_gate": "BLOCKED",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SOLAR_NSI_BRANCH.json",
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
    "delivery_scope": {
      "mode": "capability_change",
      "target": "computed physical solar ee-vector NSI plus exact paper green comparison",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "conditional_NSI_forward_and_joint_region",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json"
      },
      {
        "id": "exact_paper_Fig4_green_reproduction",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_nsi/20261112_fig4_run2/PAPER_COMPARISON.json"
      }
    ],
    "validation_levels": {
      "technical": "outputs/solar_b8_nsi/20261112_fig4_run2/QA.json",
      "paper_match": "not established;counterexample Delta3.331 at(0,.178)",
      "full_legacy_dataset_regression": "collection OS PermissionError recorded"
    },
    "runtime_integration": "scoped PreparedExperiment -> compile/predict/evaluate; all old global IDs and physical files retained",
    "final_claim": "MAINLINE_NSI_COMPUTED; EXACT_PAPER_GREEN_REPRODUCTION_NOT_ESTABLISHED",
    "limitations": [
      "two-flavor adiabatic model, theta13_m=vacuum, no Earth regeneration",
      "X tail is explicit project assumption; zero/unit and bounded profile controls kept separate",
      "B16 structure is pinned secondary transcription; neutron density uses baryon mass1u approximation",
      "paper exact oscillation/profile/SM input card not published; project choice explicitly sourced",
      "seven directly adopted nuclear tables; Xe124/126 missing, no renormalization; external nuclear author release unverified"
    ]
  }
}
```
