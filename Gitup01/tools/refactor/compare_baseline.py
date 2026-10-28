"""Audit the new path against frozen pre-refactor data without updating it."""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
from tools.refactor.freeze_baseline import points, GRIDS


def main():
    reference = ROOT / "tests/reference/interface_refactor_v1"
    metadata = json.loads((reference / "metadata.json").read_text(encoding="utf-8"))
    model = make_csi2021_model(ROOT / "data/responses/responses_all.json")
    report = {"reference_sha256": hashlib.sha256((reference / "baseline.npz").read_bytes()).hexdigest(),
              "rtol": metadata["rtol"], "atol_events": metadata["atol_events"], "cases": [],
              "same_discrete_algorithm_regression": True, "scientific_convergence_certified": False}
    sm_grids = {}
    with np.load(reference / "baseline.npz", allow_pickle=False) as baseline:
        for case in metadata["cases"]:
            name, grid = case["point"], case["grid"]
            wc, sm = points()[name]
            start = time.perf_counter()
            result = predict(model, parameters=TheoryPoint(wc, include_sm=sm), numerics=IntegrationSettings.legacy_csi2021_v1(**GRIDS[grid]))
            errors = []
            def compare(label, actual, expected):
                delta = np.abs(actual - expected)
                threshold = report["atol_events"] + report["rtol"] * np.abs(expected)
                errors.append({"label": label, "max_absolute_events": float(delta.max()),
                               "max_fraction_of_allowed_error": float(np.max(delta / threshold)),
                               "worst_bin": int(np.argmax(delta / threshold)),
                               "passed": bool(np.all(delta <= threshold))})
            prefix = f"csi2021/{name}/{grid}"
            compare("total", result.counts, baseline[f"{prefix}/counts_per_bin/total"])
            for flavor, component in LEGACY_COMPONENT_IDS.items():
                for target in model.targets.isotopes:
                    key = (component, target.isotope_id)
                    before = result.diagnostics["preselection_per_nucleus"][key]
                    old_raw = baseline[f"{prefix}/raw/{flavor}/{target.isotope_id}"]
                    compare(f"raw/{flavor}/{target.isotope_id}", before * model.targets.detector_mass_kg / target.nucleus_mass_kg, old_raw)
                    fraction = target.number_of_nuclei * target.nucleus_mass_kg / model.targets.detector_mass_kg
                    compare(f"actual/{flavor}/{target.isotope_id}", result.components[key], old_raw * fraction * model.observation.selection.acceptance(component))
            report["cases"].append({"point": name, "grid": grid, "new_seconds": time.perf_counter() - start,
                                     "old_seconds": case["seconds"], "comparisons": errors})
            if name == "sm":
                sm_grids[grid] = result.counts
    report["status"] = "PASS" if all(e["passed"] for c in report["cases"] for e in c["comparisons"]) else "FAIL"
    report["max_absolute_events"] = max(e["max_absolute_events"] for c in report["cases"] for e in c["comparisons"])
    report["max_fraction_of_allowed_error"] = max(e["max_fraction_of_allowed_error"] for c in report["cases"] for e in c["comparisons"])
    report["sm_grid_changes"] = {f"{a}_to_{b}": {"absolute_per_bin": (sm_grids[b] - sm_grids[a]).tolist(),
        "relative_per_bin": ((sm_grids[b] - sm_grids[a]) / np.maximum(np.abs(sm_grids[b]), 1e-300)).tolist()}
        for a, b in (("small", "medium"), ("medium", "default"))}
    out = ROOT / "outputs/refactor"
    out.mkdir(parents=True, exist_ok=True)
    (out / "regression_comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "resolved_model.json").write_text(json.dumps(plain(model.describe()), indent=2), encoding="utf-8")
    (out / "new_file_hashes.json").write_text(json.dumps({str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ("src", "tests", "tools/refactor") for p in sorted((ROOT / folder).rglob("*.py"))
        if "__pycache__" not in p.parts}, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "max_absolute_events", "max_fraction_of_allowed_error")}), flush=True)
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
