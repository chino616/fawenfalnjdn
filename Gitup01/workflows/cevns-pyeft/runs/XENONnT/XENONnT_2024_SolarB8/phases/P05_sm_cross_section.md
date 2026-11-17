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
    "process_and_mass": "elastic neutrino nucleus; NIST atomic mass minus Z electron masses for kinematics, atomic mass for inventory",
    "kinematics": "existing ElasticKinematics exact endpoints",
    "cross_section_api": "StandardModelKN.dsigma_dT returns DifferentialCrossSection",
    "units_and_axes": "MeV neutrino, keVnr recoil, cm²/keV cross section",
    "support_and_limits": "paper recoil-order SM including -T/E; electron binding energy neglected",
    "benchmark": "zero-recoil weak-charge normalization and endpoint; new contract tests plus convergence"
  }
}
```
