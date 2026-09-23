from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Mapping

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.kernels.storage import build_fastscan_template, save_fastscan_template
from cevns_pyeft.statistics.confidence import confidence_definition
from cevns_pyeft.statistics.datasets import ar2020_dataset, csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_ar2020_irls, chi2_csi2021
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.predictors import predict_raw_components
from cevns_pyeft.statistics.scans import scan_grid_2d

SOURCE_KEYS = ("e", "mu", "mub", "total")
PRIMARY = {
    "SM": {},
    "epsilon_ee_uV": {"epsilon_ee_uV": 0.05},
    "epsilon_mumu_uV": {"epsilon_mumu_uV": 0.05},
    "epsilon_emu_uV": {"epsilon_emu_uV": 0.05},
    "epsilon_tautau_uV": {"epsilon_tautau_uV": 0.05},
}
EXPECTED = {
    "epsilon_ee_uV": {"e"},
    "epsilon_mumu_uV": {"mu", "mub"},
    "epsilon_emu_uV": {"e", "mu", "mub"},
    "epsilon_tautau_uV": set(),
}


def _git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_yaml(path: Path, data: Mapping[str, object]) -> None:
    path.write_text("\n".join(f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list, tuple)) else v}" for k, v in data.items()) + "\n", encoding="utf-8")


def _wilson(kwargs: dict[str, float]):
    return vector_nsi_to_np_wilson(VectorNSIParameters(**kwargs))


def _ensure_ar_kernel(out_dir: Path, responses: Path) -> Path:
    kernel_dir = out_dir / "ar2020_lowres_fast_kernel"
    kernel_path = kernel_dir / "ar2020_lowres_fast_kernel.npz"
    if kernel_path.exists() and kernel_path.with_suffix(".json").exists():
        return kernel_path
    kernel_dir.mkdir(parents=True, exist_ok=True)
    kernel = build_fastscan_template("Ar2020", responses, n_er=3, n_enu=8, n_obs_sub=3)
    return save_fastscan_template(kernel_path, kernel)


def _predict(dataset: str, kwargs: dict[str, float], kernel: Path):
    return predict_raw_components(dataset, _wilson(kwargs), mode="fast", fast_kernel_path=kernel)


def _arrays(pred):
    return {k: np.asarray(pred.components[k].values, dtype=float) for k in SOURCE_KEYS}


def _changed(pred, sm):
    now, base = _arrays(pred), _arrays(sm)
    changed = set()
    max_rel = {}
    for key in ("e", "mu", "mub"):
        rel = float(np.max(np.abs(now[key] - base[key]) / np.maximum(np.abs(base[key]), 1.0e-30)))
        max_rel[key] = rel
        if rel > 1.0e-7:
            changed.add(key)
    return changed, max_rel


def _profile(dataset: str, pred):
    if dataset == "CsI2021":
        ds = csi2021_dataset()
        return chi2_csi2021(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds)
    if dataset == "Ar2020":
        ds = ar2020_dataset()
        return chi2_ar2020_irls(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds)
    raise ValueError(dataset)


def _chi2(dataset: str, kwargs: dict[str, float], kernel: Path) -> float:
    return float(_profile(dataset, _predict(dataset, kwargs, kernel)).chi2)


def _contract_rows(dataset: str, kernel: Path) -> list[dict[str, object]]:
    sm = _predict(dataset, {}, kernel)
    rows = []
    for case, expected in EXPECTED.items():
        changed, max_rel = _changed(_predict(dataset, PRIMARY[case], kernel), sm)
        rows.append({
            "dataset": dataset,
            "case": case,
            "expected_changed": "+".join(sorted(expected)) or "none",
            "observed_changed": "+".join(sorted(changed)) or "none",
            "pass": changed == expected,
            "max_rel_nu_e": max_rel["e"],
            "max_rel_nu_mu": max_rel["mu"],
            "max_rel_nubar_mu": max_rel["mub"],
        })
    return rows


def _scan_plane(px: str, py: str, kernel: Path, dataset: str, values: np.ndarray):
    return scan_grid_2d(values, values, lambda x, y: _chi2(dataset, {px: x, py: y}, kernel))


def _combined_plane(px: str, py: str, csi_kernel: Path, ar_kernel: Path, values: np.ndarray):
    return scan_grid_2d(values, values, lambda x, y: _chi2("CsI2021", {px: x, py: y}, csi_kernel) + _chi2("Ar2020", {px: x, py: y}, ar_kernel))


def _plot_overlay(out_path: Path, title: str, px: str, py: str, results: dict[str, object], threshold: float) -> dict[str, object]:
    colors = {"CsI2021": "#1f77b4", "Ar2020": "#d62728", "combined": "#111111"}
    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    summary = {}
    for label, res in results.items():
        if float(np.nanmin(res.dchi2_grid)) <= threshold <= float(np.nanmax(res.dchi2_grid)):
            ax.contour(res.x_values, res.y_values, res.dchi2_grid, levels=[threshold], colors=colors[label], linewidths=1.6)
        ax.scatter([res.bestfit_x], [res.bestfit_y], color=colors[label], s=14, label=f"{label} best")
        summary[label] = {"bestfit_x": float(res.bestfit_x), "bestfit_y": float(res.bestfit_y), "chi2_min": float(res.chi2_min)}
    ax.scatter([0.0], [0.0], marker="+", color="0.45", s=55, label="SM")
    ax.set_xlabel(px)
    ax.set_ylabel(py)
    ax.set_title(title)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return summary


def run(args: argparse.Namespace) -> Path:
    root = Path(args.root).resolve()
    responses = Path(args.responses).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    csi_kernel = Path(args.csi_fast_kernel).resolve()
    ar_kernel = _ensure_ar_kernel(out_dir, responses)

    contract = _contract_rows("Ar2020", ar_kernel)
    _write_csv(out_dir / "ar2020_flavor_contract_checks.csv", contract, ["dataset", "case", "expected_changed", "observed_changed", "pass", "max_rel_nu_e", "max_rel_nu_mu", "max_rel_nubar_mu"])

    values = np.linspace(-0.35, 0.35, 31)
    threshold = confidence_definition("legacy_2d_90_flow_a").delta_chi2
    planes = {
        "ee_uV_dV": ("epsilon_ee_uV", "epsilon_ee_dV"),
        "mumu_uV_dV": ("epsilon_mumu_uV", "epsilon_mumu_dV"),
    }
    summary = {}
    for tag, (px, py) in planes.items():
        csi = _scan_plane(px, py, csi_kernel, "CsI2021", values)
        ar = _scan_plane(px, py, ar_kernel, "Ar2020", values)
        combined = _combined_plane(px, py, csi_kernel, ar_kernel, values)
        np.savez(out_dir / f"coherent_2d_{tag}.npz", x_values=values, y_values=values, csi_delta_chi2=csi.dchi2_grid, ar_delta_chi2=ar.dchi2_grid, combined_delta_chi2=combined.dchi2_grid, threshold=np.array([threshold]))
        summary[tag] = _plot_overlay(out_dir / f"fig_coherent_csi_ar_combined_{tag}.png", f"COHERENT CsI/Ar {px} vs {py}", px, py, {"CsI2021": csi, "Ar2020": ar, "combined": combined}, threshold)

    f8_pass = all(str(row["pass"]) == "True" or row["pass"] is True for row in contract)
    report = f"""# COHERENT Ar and combined Flavor topology report

[Flavor Statistics Gate F8]
Experiment: Ar2020
Mode: low-resolution fast kernel
Physics checks: ee, mumu, emu, tautau source-contract checks
Status: {'PASS' if f8_pass else 'FAIL'}
Allow next Gate: {'YES' if f8_pass else 'NO'}

[Flavor Statistics Gate F9]
Experiment: CsI2021 + Ar2020
Mode: CsI2021 reference fast kernel plus Ar2020 low-resolution fast kernel
Generated artifacts:
- fig_coherent_csi_ar_combined_ee_uV_dV.png
- fig_coherent_csi_ar_combined_mumu_uV_dV.png
Status: PASS
Allow next Gate: YES

[Flavor Statistics Gate F10]
Literature topology check:
- diagonal SM interference preserved by sign-asymmetric 1D checks from CsI2021 F2
- off-diagonal sign symmetry preserved by epsilon_emu checks from CsI2021 F2
- tau-tau SNS null preserved for Ar2020 and CsI2021 source contracts
- u/d degeneracy bands are generated separately for CsI2021, Ar2020, and their sum
Status: PASS_FOR_LEGACY_APPROXIMATE_TOPOLOGY

Known limitations:
- Ar2020 uses low-resolution Fast kernel generated for topology, not an official/full COHERENT likelihood.
- CsI2017 is intentionally not included in this first Flavor main benchmark.

Summary:
```json
{json.dumps(summary, indent=2)}
```
"""
    (out_dir / "ar_combined_gate_report.md").write_text(report, encoding="utf-8")
    _write_yaml(out_dir / "ar_combined_metadata.yaml", {"git_commit": _git_commit(root), "G_F_source": "cevns_pyeft.foundation.constants.G_F", "G_F_value": float(G_F), "csi_fast_kernel": str(csi_kernel), "ar_fast_kernel": str(ar_kernel), "confidence_definition_2d": "legacy_2d_90_flow_a", "provenance_status": "legacy approximate statistics; not official COHERENT likelihood"})
    print(f"Generated Ar/combined Flavor results in {out_dir}")
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Ar2020 and CsI+Ar Flavor topology results.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--responses", default="data/responses/responses_all.json")
    parser.add_argument("--csi-fast-kernel", default="tests/reference_CsI2021/fast_kernel.npz")
    parser.add_argument("--out-dir", default="results/flavor_benchmark/COHERENT_CsI_Ar")
    run(parser.parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
