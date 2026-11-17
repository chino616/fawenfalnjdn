# P10: p10

2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "solar_b8.vector.p10",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "outputs/solar_b8_vector/20261108_run1/EXECUTION_PLAN.json",
  "input_refs": [
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz",
    "data/benchmarks/solar_b8_vector_v1/benchmark.input.json",
    "cevns_pyeft/theory/light_vector.py",
    "cevns_pyeft/experiments/solar_vector.py"
  ],
  "input_fingerprint": "25003990a234559ccf2194ad02fd0d730a40f13363fde60c889778bea6e6f491",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0002"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json",
      "sha256": "b64fc73ac1ec96a1cf9c41ed3e0ec680721828e4d807cb959c68842921b58c3b",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/BENCHMARK_REPORT.md",
      "sha256": "d945ce74dc894c59c07ee620f3b486b97207579545b9fa0ef8cdbfbc27f99b87",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/events.png",
      "sha256": "02f9a78ce52928818a7053233acbf2da2f727f676bff7591491c83aafeea0e24",
      "role": "actual vector benchmark result"
    }
  ],
  "checks": [
    {
      "name": "fixed-point Slow and independent signed-interference closure",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/20261108_run1",
      "result_ref": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json"
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
        "id": "vector_forward",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json"
      },
      {
        "id": "vector_reconstructed_spectrum",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/BENCHMARK_REPORT.md"
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
