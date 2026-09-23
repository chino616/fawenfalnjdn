from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

SOURCE_RELATIVE_FILES = [
    "src/cevns_pyeft/statistics/__init__.py",
    "src/cevns_pyeft/statistics/confidence.py",
    "src/cevns_pyeft/statistics/datasets.py",
    "src/cevns_pyeft/statistics/likelihoods.py",
    "src/cevns_pyeft/statistics/profiling.py",
    "src/cevns_pyeft/statistics/observables.py",
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if hasattr(value, "__dict__"):
        return {key: _jsonable(val) for key, val in value.__dict__.items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _metadata(repo_root: Path) -> dict[str, Any]:
    rows = []
    for rel in SOURCE_RELATIVE_FILES:
        path = repo_root / rel
        rows.append(
            {
                "relative_path": rel,
                "absolute_path": str(path),
                "size": int(path.stat().st_size),
                "sha256": _sha256(path),
            }
        )
    return {
        "kind": "migrated_post_split",
        "repo_root": str(repo_root),
        "python": sys.executable,
        "python_version": platform.python_version(),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "files": rows,
        "note": "Direct run of the migrated split statistics package.",
    }


def collect(repo_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo_root / "src"))
    from cevns_pyeft.statistics import confidence as conf
    from cevns_pyeft.statistics.datasets import ar2020_dataset, csi2017_dataset, csi2021_dataset
    from cevns_pyeft.statistics.likelihoods import chi2_ar2020_bounded, chi2_ar2020_irls, chi2_csi2017, chi2_csi2021
    from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable, observable, prediction_vector

    data_dir = repo_root / "data" / "datafiles"
    csi2021 = csi2021_dataset()
    csi2017 = csi2017_dataset(data_dir)
    ar2020 = ar2020_dataset()

    predictions: dict[str, dict[str, np.ndarray]] = {
        "csi2021": {
            "zero": np.zeros(csi2021.n_bins),
            "ones": np.ones(csi2021.n_bins),
            "ramp": np.linspace(0.5, 9.5, csi2021.n_bins),
            "background_width_scaled": np.asarray(csi2021.background) * csi2021.observable.bin_widths,
        },
        "csi2017": {
            "zero": np.zeros(csi2017.n_bins),
            "ones": np.ones(csi2017.n_bins),
            "legacy_spectrum": np.asarray(csi2017.metadata["spectrum_reference"], dtype=float),
            "observed": np.asarray(csi2017.observed, dtype=float),
        },
        "ar2020": {
            "zero": np.zeros(ar2020.n_bins),
            "ones": np.ones(ar2020.n_bins),
            "observed_minus_background": np.asarray(ar2020.observed) - np.asarray(ar2020.background),
            "ramp": np.linspace(1.0, 24.0, ar2020.n_bins),
        },
    }

    cases: dict[str, Any] = {"csi2021": {}, "csi2017": {}, "ar2020": {}}
    raw_csi2021 = observable("reconstructed PE spectrum", "events/bin", csi2021.observable.bin_edges)
    for name, pred in predictions["csi2021"].items():
        converted = convert_prediction_to_dataset_observable(prediction_vector(pred, raw_csi2021), csi2021.observable)
        cases["csi2021"][name] = _jsonable(chi2_csi2021(converted, csi2021))
    for name, pred in predictions["csi2017"].items():
        cases["csi2017"][name] = _jsonable(chi2_csi2017(prediction_vector(pred, csi2017.observable), csi2017))
    for name, pred in predictions["ar2020"].items():
        pv = prediction_vector(pred, ar2020.observable)
        cases["ar2020"][name] = {
            "irls": _jsonable(chi2_ar2020_irls(pv, ar2020)),
            "bounded": _jsonable(chi2_ar2020_bounded(pv, ar2020)),
        }

    return {
        "metadata": _metadata(repo_root),
        "profiles": cases,
        "confidence": {
            "CL_TO_DCHI2_1DOF": _jsonable(conf.CL_TO_DCHI2_1DOF),
            "CL_TO_DCHI2_2DOF": _jsonable(conf.CL_TO_DCHI2_2DOF),
            "COHERENT_2D_90CL_THRESHOLD": conf.confidence_definition("legacy_2d_90_rounded_api").delta_chi2,
            "THRESHOLD_90CL_flow_b": conf.confidence_definition("legacy_2d_90_flow_b").delta_chi2,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = collect(Path(args.repo_root).resolve())
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


