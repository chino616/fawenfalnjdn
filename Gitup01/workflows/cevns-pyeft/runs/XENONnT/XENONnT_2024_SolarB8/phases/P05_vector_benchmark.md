# P05: p05

2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P05",
  "capability_id": "solar_b8.vector.p05",
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
    "process_and_mass": "elastic nu-Xe, exact existing mass/endpoint conventions",
    "kinematics": "existing ElasticKinematics",
    "cross_section_api": "LightVectorKN.dsigma_dT -> DifferentialCrossSection",
    "units_and_axes": "E MeV, recoil keVnr, internal GeV, output cm2/keVnr",
    "support_and_limits": "positive mediator mass; real universal coupling; no massless/IR extrapolation",
    "benchmark": "g=0 SM, heavy decoupling, g^4 NP-only, signed interference and cancellation, weak-charge zero case"
  }
}
```
