# P10: p10

2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.vector.p10",
  "workspace": "canonical",
  "plan_status": "BLOCKED",
  "machine_gate": "BLOCKED",
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
      "status": "BLOCKED",
      "command": "python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/20261108_run1",
      "result_ref": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/DATASET_RESULT.json"
    }
  ],
  "handoff": {
    "delivery_scope": {
      "mode": "theory_change",
      "target": "V/B-L event spectra",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "vector_true_recoil",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/DATASET_RESULT.json"
      },
      {
        "id": "vector_reconstructed_spectrum",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/BENCHMARK_REPORT.md"
      }
    ],
    "validation_levels": {
      "numerical_and_analytic": "PASS",
      "targeted_regressions": "27 passed",
      "published_nonzero_point_template": "UNAVAILABLE",
      "Fig4_exclusion": "NOT_REQUESTED"
    },
    "runtime_integration": "existing standard component API; formal SM packages and default registry unchanged",
    "final_claim": "fixed-point vector forward spectra; explicit response/source limitations",
    "limitations": [
      "Real flavor-universal diagonal vector models only; general flavor NSI, scalar, axial and tensor not implemented in this task.",
      "Public XENONnT early-response accuracy limits retained.",
      "PandaX US2 Ne-bin response remains missing; only acceptance-weighted true-recoil diagnostics computed."
    ]
  }
}
```
