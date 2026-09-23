from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


SOURCE_RELATIVE_FILES = [
    "src/cevns_pyeft/statistics/__init__.py",
    "src/cevns_pyeft/statistics/cutoff_single.py",
    "src/cevns_pyeft/statistics/cutoff_multi.py",
    "src/cevns_pyeft/statistics/chi2_2d.py",
    "data/datafiles/COHERENT_data.txt",
    "data/datafiles/COHERENT_lower.txt",
    "data/datafiles/COHERENT_upper.txt",
    "data/datafiles/COHERENT_spectrum.txt",
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


def _metadata(source_root: Path) -> dict[str, Any]:
    rows = []
    for rel in SOURCE_RELATIVE_FILES:
        path = source_root / rel
        stat = path.stat()
        rows.append(
            {
                "relative_path": rel,
                "absolute_path": str(path),
                "size": int(stat.st_size),
                "mtime": stat.st_mtime,
                "sha256": _sha256(path),
            }
        )
    return {
        "source_root": str(source_root),
        "source_git_branch": None,
        "source_git_commit": None,
        "source_git_note": "source directory is not a git repository in the local migration bundle",
        "files": rows,
    }


def generate(source_root: Path, out_dir: Path) -> None:
    sys.path.insert(0, str(source_root / "src"))
    from cevns_pyeft.statistics import cutoff_multi as legacy_multi
    from cevns_pyeft.statistics import cutoff_single as legacy_single

    data_dir = source_root / "data" / "datafiles"
    out_dir.mkdir(parents=True, exist_ok=True)

    csi2021_spec = legacy_multi.csi2021_spec()
    csi2017_spec = legacy_multi.csi2017_spec(data_dir)
    ar_irls_spec = legacy_multi.ar2020_spec(ar_profile_method="irls")
    ar_min_spec = legacy_multi.ar2020_spec(ar_profile_method="minimize")

    cases: dict[str, Any] = {"csi2021": {}, "csi2017": {}, "ar2020": {}}
    csi2021_predictions = {
        "zero": np.zeros(csi2021_spec.bin_edges.size - 1),
        "ones": np.ones(csi2021_spec.bin_edges.size - 1),
        "ramp": np.linspace(0.5, 9.5, csi2021_spec.bin_edges.size - 1),
        "background_width_scaled": np.asarray(csi2021_spec.background) * np.diff(csi2021_spec.bin_edges),
    }
    for name, pred in csi2021_predictions.items():
        cases["csi2021"][name] = _jsonable(legacy_multi.profile_csi2021(pred, csi2021_spec))

    csi2017_predictions = {
        "zero": np.zeros(csi2017_spec.bin_edges.size - 1),
        "ones": np.ones(csi2017_spec.bin_edges.size - 1),
        "legacy_spectrum": legacy_multi.load_csi2017_reference_data(data_dir)["spectrum"],
        "observed": np.asarray(csi2017_spec.data, dtype=float),
    }
    for name, pred in csi2017_predictions.items():
        cases["csi2017"][name] = _jsonable(legacy_multi.profile_csi2017(pred, csi2017_spec))

    ar_predictions = {
        "zero": np.zeros(ar_irls_spec.bin_edges.size - 1),
        "ones": np.ones(ar_irls_spec.bin_edges.size - 1),
        "observed_minus_background": np.asarray(ar_irls_spec.data) - np.asarray(ar_irls_spec.background),
        "ramp": np.linspace(1.0, 24.0, ar_irls_spec.bin_edges.size - 1),
    }
    for name, pred in ar_predictions.items():
        irls = legacy_multi.profile_ar2020(pred, ar_irls_spec)
        try:
            bounded = _jsonable(legacy_multi.profile_ar2020(pred, ar_min_spec))
        except RuntimeError as exc:
            bounded = {"available": False, "message": str(exc)}
        cases["ar2020"][name] = {
            "irls": _jsonable(irls),
            "bounded": bounded,
        }

    np.savez(
        out_dir / "fixed_prediction_cases.npz",
        csi2021_zero=csi2021_predictions["zero"],
        csi2021_ones=csi2021_predictions["ones"],
        csi2021_ramp=csi2021_predictions["ramp"],
        csi2021_background_width_scaled=csi2021_predictions["background_width_scaled"],
        csi2017_zero=csi2017_predictions["zero"],
        csi2017_ones=csi2017_predictions["ones"],
        csi2017_legacy_spectrum=csi2017_predictions["legacy_spectrum"],
        csi2017_observed=csi2017_predictions["observed"],
        ar2020_zero=ar_predictions["zero"],
        ar2020_ones=ar_predictions["ones"],
        ar2020_observed_minus_background=ar_predictions["observed_minus_background"],
        ar2020_ramp=ar_predictions["ramp"],
    )
    (out_dir / "profile_reference.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    (out_dir / "confidence_reference.json").write_text(
        json.dumps(
            {
                "CL_TO_DCHI2_1DOF": legacy_single.CL_TO_DCHI2_1DOF,
                "CL_TO_DCHI2_2DOF": {0.683: 2.30, 0.90: 4.61, 0.95: 5.99, 0.99: 9.21},
                "COHERENT_2D_90CL_THRESHOLD": 4.6,
                "THRESHOLD_90CL_flow_b": 4.61,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "metadata.json").write_text(json.dumps(_metadata(source_root), indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate fixed legacy statistics references from CEvNS-pyEFT-main.")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--out-dir", default="tests/reference/statistics_legacy")
    args = parser.parse_args(argv)
    generate(Path(args.source_root).resolve(), Path(args.out_dir).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


