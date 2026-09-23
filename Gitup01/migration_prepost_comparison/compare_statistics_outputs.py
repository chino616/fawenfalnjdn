from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

FIELDS = ("chi2", "alpha", "beta", "chi2_data", "chi2_nuisance")
ABS_TOL = 1.0e-8
REL_TOL = 1.0e-10


def _num(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _rel(abs_diff: float, left: float, right: float) -> float:
    denom = max(abs(left), abs(right), 1.0e-30)
    return abs_diff / denom


def _profile_rows(legacy: dict[str, Any], migrated: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    datasets = sorted(set(legacy["profiles"]) | set(migrated["profiles"]))
    for dataset in datasets:
        cases = sorted(set(legacy["profiles"].get(dataset, {})) | set(migrated["profiles"].get(dataset, {})))
        for case in cases:
            old_case = legacy["profiles"].get(dataset, {}).get(case, {})
            new_case = migrated["profiles"].get(dataset, {}).get(case, {})
            methods = [None]
            if dataset == "ar2020":
                methods = ["irls", "bounded"]
            for method in methods:
                old = old_case if method is None else old_case.get(method, {})
                new = new_case if method is None else new_case.get(method, {})
                if isinstance(old, dict) and old.get("available") is False:
                    rows.append({
                        "dataset": dataset,
                        "case": case,
                        "method": method or "default",
                        "field": "all",
                        "legacy": "unavailable",
                        "migrated": "available" if isinstance(new, dict) else "missing",
                        "abs_diff": "",
                        "rel_diff": "",
                        "pass": "SKIP_LEGACY_UNAVAILABLE",
                    })
                    continue
                for field in FIELDS:
                    left = _num(old.get(field) if isinstance(old, dict) else None)
                    right = _num(new.get(field) if isinstance(new, dict) else None)
                    if left is None or right is None:
                        status = "MISSING"
                        abs_diff = ""
                        rel_diff = ""
                    else:
                        diff = abs(left - right)
                        rel = _rel(diff, left, right)
                        status = "PASS" if diff <= ABS_TOL or rel <= REL_TOL else "FAIL"
                        abs_diff = f"{diff:.17g}"
                        rel_diff = f"{rel:.17g}"
                    rows.append({
                        "dataset": dataset,
                        "case": case,
                        "method": method or "default",
                        "field": field,
                        "legacy": "" if left is None else f"{left:.17g}",
                        "migrated": "" if right is None else f"{right:.17g}",
                        "abs_diff": abs_diff,
                        "rel_diff": rel_diff,
                        "pass": status,
                    })
    return rows


def _walk_numbers(prefix: str, obj: Any) -> dict[str, float]:
    if isinstance(obj, dict):
        out: dict[str, float] = {}
        for key, value in obj.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            out.update(_walk_numbers(name, value))
        return out
    if isinstance(obj, (int, float)):
        return {prefix: float(obj)}
    return {}


def _confidence_rows(legacy: dict[str, Any], migrated: dict[str, Any]) -> list[dict[str, Any]]:
    old = _walk_numbers("", legacy["confidence"])
    new = _walk_numbers("", migrated["confidence"])
    rows = []
    for key in sorted(set(old) | set(new)):
        left = old.get(key)
        right = new.get(key)
        if left is None or right is None:
            status = "MISSING"
            abs_diff = ""
            rel_diff = ""
        else:
            diff = abs(left - right)
            rel = _rel(diff, left, right)
            status = "PASS" if diff <= ABS_TOL or rel <= REL_TOL else "FAIL"
            abs_diff = f"{diff:.17g}"
            rel_diff = f"{rel:.17g}"
        rows.append({
            "key": key,
            "legacy": "" if left is None else f"{left:.17g}",
            "migrated": "" if right is None else f"{right:.17g}",
            "abs_diff": abs_diff,
            "rel_diff": rel_diff,
            "pass": status,
        })
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compare(legacy_path: Path, migrated_path: Path, out_dir: Path) -> dict[str, Any]:
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
    profile_rows = _profile_rows(legacy, migrated)
    confidence_rows = _confidence_rows(legacy, migrated)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(out_dir / "profile_comparison.csv", profile_rows, ["dataset", "case", "method", "field", "legacy", "migrated", "abs_diff", "rel_diff", "pass"])
    _write_csv(out_dir / "confidence_comparison.csv", confidence_rows, ["key", "legacy", "migrated", "abs_diff", "rel_diff", "pass"])

    comparable = [r for r in profile_rows + confidence_rows if r["pass"] not in {"SKIP_LEGACY_UNAVAILABLE"}]
    failures = [r for r in comparable if r["pass"] != "PASS"]
    numeric_profile_rows = [r for r in profile_rows if r["abs_diff"] not in {"", None}]
    max_abs = max((float(r["abs_diff"]) for r in numeric_profile_rows), default=0.0)
    max_rel = max((float(r["rel_diff"]) for r in numeric_profile_rows), default=0.0)
    summary = {
        "status": "PASS" if not failures else "FAIL",
        "abs_tolerance": ABS_TOL,
        "rel_tolerance": REL_TOL,
        "profile_rows": len(profile_rows),
        "confidence_rows": len(confidence_rows),
        "skipped_rows": len([r for r in profile_rows if r["pass"] == "SKIP_LEGACY_UNAVAILABLE"]),
        "failure_rows": len(failures),
        "max_profile_abs_diff": max_abs,
        "max_profile_rel_diff": max_rel,
        "legacy_metadata": legacy.get("metadata", {}),
        "migrated_metadata": migrated.get("metadata", {}),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = f"""# Migration Pre/Post Statistics Comparison

Status: {summary['status']}

This directory compares the pre-migration statistics code from `CEvNS-pyEFT-main` with the migrated split statistics package in this worktree.

Scope:
- CsI2021 fixed predictions through the legacy approximate two-pull chi-square.
- CsI2017 fixed predictions through the legacy approximate one-pull chi-square.
- Ar2020 fixed predictions through the legacy approximate IRLS and bounded/minimize profiles.
- Confidence-threshold constants used by the migrated result scripts.

Results:
- Profile comparison rows: {summary['profile_rows']}
- Confidence comparison rows: {summary['confidence_rows']}
- Skipped rows: {summary['skipped_rows']}
- Failure rows: {summary['failure_rows']}
- Max profile absolute difference: {summary['max_profile_abs_diff']:.17g}
- Max profile relative difference: {summary['max_profile_rel_diff']:.17g}

Important limitation:
The bundled pre-migration source contains JSON metadata for COHERENT Fast kernels but not the corresponding `.npz` kernel arrays, so the old Flavor contour program cannot be fully replayed from that bundle alone. The strict comparison here is therefore the statistics layer: identical fixed prediction vectors are sent through old and migrated likelihood/profile code. The Flavor result figures remain legacy approximate topology outputs, not official COHERENT likelihoods.

Artifacts:
- `legacy_statistics_outputs.json`
- `migrated_statistics_outputs.json`
- `profile_comparison.csv`
- `confidence_comparison.csv`
- `summary.json`
"""
    (out_dir / "COMPARISON_REPORT.md").write_text(report, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", required=True)
    parser.add_argument("--migrated", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    summary = compare(Path(args.legacy), Path(args.migrated), Path(args.out_dir))
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
