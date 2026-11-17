# P09：SNuDD完整联合统计与论文比较

[逐项来源与最终计算报告](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际验收](<../../../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/QA.json>) · [完整结果](<../../../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json>)

同源数值求积、全域联合优化、601²面、独立三pull与原生论文图比较均已完成。技术PASS；精确论文复现未成立，结果接受NOT_REVIEWED。不覆盖旧分支或授予人工科学Gate。

```json phase-result
{
  "schema_version": 1,
  "phase": "P09",
  "capability_id": "solar_b8.external_snudd_full_fig4.p09",
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
    "channels": [
      {
        "id": "PandaX_paired",
        "representation": "binned_counts",
        "processing": "other",
        "design": "joint",
        "likelihood": "gaussian",
        "requires_covariance": false,
        "meaning": "experimental fitted signal yield, not raw counts"
      },
      {
        "id": "PandaX_US2",
        "representation": "binned_counts",
        "processing": "other",
        "design": "joint",
        "likelihood": "gaussian",
        "requires_covariance": false,
        "meaning": "experimental fitted signal yield, not raw counts"
      },
      {
        "id": "XENONnT",
        "representation": "binned_counts",
        "processing": "other",
        "design": "joint",
        "likelihood": "gaussian",
        "requires_covariance": false,
        "meaning": "experimental fitted signal yield, not raw counts"
      }
    ],
    "prediction_binding": "outputs/external/solar_rho_snudd/20261112_fig4_run2/DIRECT_RUNTIME_VALIDATION.json",
    "required_inputs": {
      "available": true,
      "sources": [
        "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json"
      ],
      "missing": []
    },
    "nuisance_model": "Eq88 three independent sigma=.12 Gaussian pulls; analytic profile",
    "inference": "each treatment own jointly minimized2Dchi2; threshold4.61; whole plane within declared two-flavor model",
    "claim_level": "approximate",
    "benchmark": "2601.19883v2Fig4 green native vector comparison; exact agreement NOT established",
    "limitations": [
      "last-value X-tail is an explicit assumption; raw experimental tail remains missing",
      "large-NSI two-flavor validity not certified"
    ]
  }
}
```
