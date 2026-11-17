# P10：SNuDD完整联合统计与论文比较

[逐项来源与最终计算报告](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际验收](<../../../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/QA.json>) · [完整结果](<../../../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json>)

同源数值求积、全域联合优化、601²面、独立三pull与原生论文图比较均已完成。技术PASS；精确论文复现未成立，结果接受NOT_REVIEWED。不覆盖旧分支或授予人工科学Gate。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.external_snudd_full_fig4.p10",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "outputs/external/solar_rho_snudd/20261112_fig4_run2/WRITE_PLAN.json",
  "input_refs": [
    "extensions/solar_rho_snudd/snudd.input.json",
    "outputs/external/solar_rho_snudd/20261112_fig4_run2/SOURCE_FINGERPRINTS.json"
  ],
  "input_fingerprint": "942ae3f85b40b07b87ad271d1a0b943440a89d6d1f294c850ef4a720652861b9",
  "evidence_refs": [
    "outputs/external/solar_rho_snudd/20261112_fig4_run2/QA.json",
    "outputs/external/solar_rho_snudd/20261112_fig4_run2/DIRECT_RUNTIME_VALIDATION.json"
  ],
  "decision_refs": [
    "D0008"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json",
      "sha256": "253df0f048de8148dc0a9eeba46376a21d4190fcdf5fcd03e4953d69e323308b",
      "role": "complete approximate-model joint inference"
    }
  ],
  "checks": [
    {
      "name": "joint inference and actual Runtime consistency",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_snudd_inference.py",
      "result_ref": "outputs/external/solar_rho_snudd/20261112_fig4_run2/DIRECT_RUNTIME_VALIDATION.json"
    }
  ],
  "handoff": {
    "delivery_scope": {
      "mode": "capability_change",
      "target": "complete external SNuDD statistical calculation and paper comparison",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "approximate_model_full_statistics",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json"
      },
      {
        "id": "exact_paper_green_reproduction",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/external/solar_rho_snudd/20261112_fig4_run2/PAPER_COMPARISON.json"
      }
    ],
    "validation_levels": {
      "internal_numerics": "PASS",
      "Runtime_statistics": "PASS",
      "paper_comparison_computed": true,
      "exact_paper_reproduction": "NOT_ESTABLISHED"
    },
    "runtime_integration": "explicit load_snudd and independent source representation; unchanged core/default catalog",
    "final_claim": "complete calculated approximate-model region and quantitative comparison; no exact reproduction claim",
    "limitations": [
      "unknown X tail",
      "two-flavor approximation",
      "external nuclear authorship not certified",
      "paper exact input card unavailable"
    ]
  }
}
```
