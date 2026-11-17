# P05: sm_cross_section

2026-11-07。本轮固定SM前向输出的实际实施与校验，具体数值见结果文件。

物理实施范围见D0001/W0001。机器检查和实际输入/代码指纹见结构化记录；结果尚未由用户验收，不将其记为APPROVED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P05",
  "capability_id": "solar_b8.sm_cross_section",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
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
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_sm_benchmark.py",
      "result_ref": "outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/SM_RESULT.json"
    }
  ],
  "handoff": {
    "process_and_mass": "elastic neutrino nucleus; NIST atomic mass minus Z electron masses for kinematics, atomic mass for inventory",
    "kinematics": "existing ElasticKinematics exact endpoints",
    "cross_section_api": "StandardModelKN.dsigma_dT returns DifferentialCrossSection",
    "units_and_axes": "MeV neutrino, keVnr recoil, cm²/keV cross section",
    "support_and_limits": "paper recoil-order SM including -T/E; electron binding energy neglected",
    "benchmark": "zero-recoil weak-charge normalization and endpoint; new contract tests plus convergence"
  }
}
```
