# P08：太阳电子味矢量NSI独立单bin分支

[v3.3同源onboarding/来源/代码/实际结果](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>)

技术计算已执行；执行授权不等于科学结果接受。P08尚无Slow结果人工接受；P10精确图形复现未成立，分别保持正式门槛未通过。旧分支不变。

```json phase-result
{
  "schema_version": 1,
  "phase": "P08",
  "capability_id": "solar_b8.ee_vector_nsi2601.P08",
  "workspace": "canonical",
  "plan_status": "DRAFT",
  "machine_gate": "BLOCKED",
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
    "representation": "eft_quadratic_coefficient_kernel",
    "backend": "energy_resolved_ee_vector_nsi_v1",
    "basis_scope": "declared_subspace",
    "parameter_domain": "real ee-uV/dV; algebraic energy kernel, changing Pee applied at every point; two-flavor approximation limits retained",
    "state_treatment": "parameter_dependent",
    "slow_reference": {
      "report_ref": "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/phases/P07_solar_nsi2601.md",
      "sha256": "e9624e503620302036249dac22a1b89d320316c5d75aebbaaba5e67c07d2865c",
      "approval_ref": null
    },
    "cache_dependencies": "physics fingerprint, all fold input digests, numerics, angle, array digest; no fixed-rho generic kernel",
    "validation_summary": "technical PASS:9 actual Slow/Fast points; canonical P08 approval prerequisite not claimed: Slow human acceptance still NOT_REVIEWED"
  }
}
```
