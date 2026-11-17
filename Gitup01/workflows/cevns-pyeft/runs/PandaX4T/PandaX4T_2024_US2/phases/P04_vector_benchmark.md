# P04: p04

2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P04",
  "capability_id": "solar_b8.vector.p04",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "outputs/solar_b8_vector/20261108_run1/EXECUTION_PLAN.json",
  "input_refs": [
    "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml",
    "data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz",
    "data/benchmarks/solar_b8_vector_v1/benchmark.input.json",
    "cevns_pyeft/theory/light_vector.py",
    "cevns_pyeft/experiments/solar_vector.py"
  ],
  "input_fingerprint": "12ba6bd34666cda78073cdbe2b28defd8a53e3a982ce6ef2a6a5f73f604285d6",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0002"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/DATASET_RESULT.json",
      "sha256": "4d03fc21ea1bcdafbc1828734813eec27246ce782f0150035dfb0afb268a86bb",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/BENCHMARK_REPORT.md",
      "sha256": "703f1d8a36725ea6f2e7f3ebc96435fc490c74dd0c9e88cd3774f94852bb1c0e",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/events.png",
      "sha256": "7ae934171b53fcf4d99d4fe92695573260a05c927bef377323225b6cae31bd2d",
      "role": "actual vector benchmark result"
    }
  ],
  "checks": [
    {
      "name": "fixed-point Slow and independent signed-interference closure",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/20261108_run1",
      "result_ref": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/DATASET_RESULT.json"
    }
  ],
  "handoff": {
    "theory_scope": "Real flavor-universal light V/B-L; published JCAP Eqs.(2.6),(2.10)",
    "coefficient_convention": "C_V=3 A g^2; kappa=1 or -1/3; SM+NP amplitudes squared together",
    "nuclear_responses": "Existing analytic KN per natural Xe isotope; no spin table for vector",
    "coverage": "universal diagonal vector only; no scalar/axial/tensor or generic flavor LEFT",
    "runtime_binding": "LightVectorKN via standard interaction override",
    "external_evidence_limits": [
      "Real flavor-universal diagonal vector models only; general flavor NSI, scalar, axial and tensor not implemented in this task.",
      "Public XENONnT early-response accuracy limits retained.",
      "PandaX US2 Ne-bin response remains missing; only acceptance-weighted true-recoil diagnostics computed."
    ]
  }
}
```
