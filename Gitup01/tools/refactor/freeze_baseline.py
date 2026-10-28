"""Capture pre-refactor outputs once; never used to regenerate test references."""
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020
from cevns_pyeft.statistics.predictors import predict_raw_counts
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_csi2021
from cevns_pyeft.theory.li2026.operators import get_operator_spec


def points():
    e = np.diag([1.0, 0.0, 0.0]).astype(complex)
    multi = np.array([[1, 0.2j, 0.1], [0.15, -0.4, 0.2j], [0.05j, 0.3, 0.2]], complex)
    return {
        "sm": ({}, True),
        "np": ({(6, 1, "u"): 1e-6 * e}, False),
        "sm_np": ({(6, 1, "u"): 1e-6 * e}, True),
        "complex": ({(6, 1, "u"): (1e-6 + 2e-7j) * e,
                     (7, 1, "d"): (-3e-7 + 1e-7j) * e}, True),
        "multiflavor": ({(6, 1, "u"): 1e-6 * multi,
                         (8, 1, "d"): -1e-8 * multi}, True),
    }


GRIDS = {
    "small": dict(n_er=5, n_enu=12, n_pe_bin=4, pe_step=4.0),
    "medium": dict(n_er=11, n_enu=40, n_pe_bin=8, pe_step=3.0),
    "default": dict(n_er=21, n_enu=120, n_pe_bin=8, pe_step=3.0),
}


def point_records():
    return {name: {"include_sm": include_sm, "sin2thetaW": .2387, "c10_mass_mode": "quark_mass_resolved",
        "wc_triplets": [{"key": list(key), "real": value.real.tolist(), "imag": value.imag.tolist()}
                        for key, value in wc.items()]} for name, (wc, include_sm) in points().items()}


def audit_document_hashes(metadata):
    """Use the captured input hashes, even if independent new work is ongoing."""
    import re
    audit = ROOT.parent / "重构/CEvNS_pyEFT_interface_refactor_v1/CEvNS_pyEFT_interface_refactor_v1/01_BASELINE_AUDIT.md"
    expected = re.findall(r"\| `([^`]+)` \| `([a-f0-9]{64})` \|", audit.read_text(encoding="utf-8"))
    differences = []
    for name, sha in expected:
        captured = metadata["hashes"].get(name)
        if captured is None:
            captured = hashlib.sha256((ROOT / name).read_bytes()).hexdigest() if (ROOT / name).is_file() else None
        if captured != sha:
            differences.append(name)
    return differences


def main():
    out = ROOT / "tests" / "reference" / "interface_refactor_v1"
    if (out / "baseline.npz").exists() or (out / "metadata.json").exists():
        raise SystemExit("Reference already exists; refusing to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    arrays = {}
    metadata = {
        "origin": "Unmodified user-provided 261028Gitup1-CONUS-3/Gitup01",
        "git_revision": None,
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "rtol": 1e-10, "atol_events": 1e-12,
        "grids": GRIDS, "points": point_records(), "cases": [],
        "hashes": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                   for folder in ("src", "data", "tests")
                   for p in sorted((ROOT / folder).rglob("*"))
                   if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".py", ".json", ".yaml", ".txt")},
    }
    for name, (wc, sm) in points().items():
        for key in wc:
            get_operator_spec(key)
        for grid_name, settings in GRIDS.items():
            if grid_name == "default" and name != "sm":
                continue
            start = time.perf_counter()
            result = slow_counts_csi2021(ROOT / "data/responses/responses_all.json", wc, include_sm=sm, **settings)
            prefix = f"csi2021/{name}/{grid_name}"
            for kind in ("counts_per_bin", "counts_per_npe"):
                for src, values in result[kind].items():
                    arrays[f"{prefix}/{kind}/{src}"] = values
            for src, targets in result["target_flavor_counts_per_bin"].items():
                for target, values in targets.items():
                    arrays[f"{prefix}/raw/{src}/{target}"] = values
            metadata["cases"].append(dict(point=name, grid=grid_name, seconds=time.perf_counter() - start))
            print(prefix, metadata["cases"][-1]["seconds"], flush=True)
    for dataset, fn, settings in (
        ("csi2017", slow_counts_csi2017, dict(n_enu=12)),
        ("ar2020", slow_counts_ar2020, GRIDS["medium"]),
    ):
        for name in ("sm", "multiflavor"):
            wc, sm = points()[name]
            result = fn(ROOT / "data/responses/responses_all.json", wc, include_sm=sm, **settings)
            for src, values in result["counts_per_bin"].items():
                arrays[f"{dataset}/{name}/{src}"] = values
    raw = predict_raw_counts("CsI2021", responses_json=ROOT / "data/responses/responses_all.json", **GRIDS["small"])
    ds = csi2021_dataset()
    metadata["chi2_small_sm"] = float(chi2_csi2021(convert_prediction_to_dataset_observable(raw, ds.observable)).chi2)
    metadata["document_baseline_differences"] = audit_document_hashes(metadata)
    np.savez_compressed(out / "baseline.npz", **arrays)
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Frozen", len(arrays), "arrays; document differences:", metadata["document_baseline_differences"], flush=True)


if __name__ == "__main__":
    main()
