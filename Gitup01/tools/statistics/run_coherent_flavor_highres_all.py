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
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020
from cevns_pyeft.kernels.storage import build_fastscan_template, save_fastscan_template
from cevns_pyeft.statistics.confidence import confidence_definition
from cevns_pyeft.statistics.datasets import ar2020_dataset, csi2017_dataset, csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_ar2020_irls, chi2_csi2017, chi2_csi2021
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.predictors import predict_raw_components
from cevns_pyeft.statistics.scans import Scan2DResult, scan_grid_2d

DATASET_ORDER = ("CsI2021", "CsI2017", "Ar2020")
DATASET_COLORS = {"CsI2021": "#1f77b4", "CsI2017": "#2ca02c", "Ar2020": "#d62728", "combined": "#111111"}
PLANES = {
    "ee_uV_dV": ("epsilon_ee_uV", "epsilon_ee_dV"),
    "mumu_uV_dV": ("epsilon_mumu_uV", "epsilon_mumu_dV"),
    "emu_uV_dV": ("epsilon_emu_uV", "epsilon_emu_dV"),
}
SUMMARY_FIELDS = [
    "dataset", "plane", "x_parameter", "y_parameter", "x_min", "x_max", "y_min", "y_max", "grid_n",
    "bestfit_x", "bestfit_y", "chi2_min", "dchi2_max", "threshold_90cl", "contour_available",
    "bestfit_on_frame", "contour_touches_frame", "truncated_by_frame",
]


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
    path.write_text("\n".join(f"{key}: {json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list, tuple)) else value}" for key, value in data.items()) + "\n", encoding="utf-8")


def _save_figure(fig: plt.Figure, png_path: Path) -> None:
    fig.savefig(png_path, dpi=300)
    fig.savefig(png_path.with_suffix(".pdf"))


def _wilson(kwargs: dict[str, float]):
    return vector_nsi_to_np_wilson(VectorNSIParameters(**kwargs))


def _ensure_ar_kernel(out_dir: Path, responses: Path, *, n_er: int, n_enu: int, n_obs_sub: int) -> Path:
    kernel_dir = out_dir / f"ar2020_fast_kernel_ne{n_er}_nenu{n_enu}_nobs{n_obs_sub}"
    kernel_path = kernel_dir / "ar2020_fast_kernel.npz"
    if kernel_path.exists() and kernel_path.with_suffix(".json").exists():
        return kernel_path
    kernel_dir.mkdir(parents=True, exist_ok=True)
    kernel = build_fastscan_template("Ar2020", responses, n_er=n_er, n_enu=n_enu, n_obs_sub=n_obs_sub)
    return save_fastscan_template(kernel_path, kernel)


def _profile(dataset: str, pred):
    if dataset == "CsI2021":
        ds = csi2021_dataset()
        return chi2_csi2021(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds)
    if dataset == "CsI2017":
        ds = csi2017_dataset()
        return chi2_csi2017(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds)
    if dataset == "Ar2020":
        ds = ar2020_dataset()
        return chi2_ar2020_irls(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds)
    raise ValueError(dataset)


def _chi2(dataset: str, kernel: Path, kwargs: dict[str, float]) -> float:
    pred = predict_raw_components(dataset, _wilson(kwargs), mode="fast", fast_kernel_path=kernel)
    return float(_profile(dataset, pred).chi2)


def _scan_dataset(dataset: str, kernel: Path, px: str, py: str, values: np.ndarray) -> Scan2DResult:
    return scan_grid_2d(values, values, lambda x, y: _chi2(dataset, kernel, {px: float(x), py: float(y)}))


def _scan_from_npz(path: Path) -> Scan2DResult:
    with np.load(path, allow_pickle=False) as data:
        x = np.asarray(data["x_values"], dtype=float)
        y = np.asarray(data["y_values"], dtype=float)
        chi2 = np.asarray(data["chi2_grid"], dtype=float)
    iy0, ix0 = np.unravel_index(int(np.nanargmin(chi2)), chi2.shape)
    chi2_min = float(chi2[iy0, ix0])
    return Scan2DResult(x, y, chi2, chi2 - chi2_min, float(x[ix0]), float(y[iy0]), chi2_min)


def _save_scan_npz(path: Path, result: Scan2DResult, threshold: float, **extra: np.ndarray) -> None:
    np.savez(path, x_values=result.x_values, y_values=result.y_values, chi2_grid=result.chi2_grid, delta_chi2_grid=result.dchi2_grid, threshold=np.array([threshold], dtype=float), **extra)


def _get_or_scan(dataset: str, kernel: Path, px: str, py: str, values: np.ndarray, path: Path) -> Scan2DResult:
    if path.exists():
        print(f"Loading existing {path.name}", flush=True)
        return _scan_from_npz(path)
    print(f"Scanning {dataset} {path.stem} on {values.size}x{values.size} grid...", flush=True)
    return _scan_dataset(dataset, kernel, px, py, values)


def _combine_results(results: Mapping[str, Scan2DResult]) -> Scan2DResult:
    labels = list(results)
    ref = results[labels[0]]
    chi2 = np.zeros_like(ref.chi2_grid, dtype=float)
    for label in labels:
        res = results[label]
        if not np.array_equal(res.x_values, ref.x_values) or not np.array_equal(res.y_values, ref.y_values):
            raise ValueError("combined results require identical grids")
        chi2 += res.chi2_grid
    iy0, ix0 = np.unravel_index(int(np.nanargmin(chi2)), chi2.shape)
    chi2_min = float(chi2[iy0, ix0])
    return Scan2DResult(ref.x_values, ref.y_values, chi2, chi2 - chi2_min, float(ref.x_values[ix0]), float(ref.y_values[iy0]), chi2_min)


def _truncation_flags(result: Scan2DResult, threshold: float, *, edge_tol: float = 1.0e-12) -> dict[str, bool]:
    xmin, xmax = float(result.x_values[0]), float(result.x_values[-1])
    ymin, ymax = float(result.y_values[0]), float(result.y_values[-1])
    bestfit_on_frame = abs(result.bestfit_x - xmin) <= edge_tol or abs(result.bestfit_x - xmax) <= edge_tol or abs(result.bestfit_y - ymin) <= edge_tol or abs(result.bestfit_y - ymax) <= edge_tol
    z = np.asarray(result.dchi2_grid, dtype=float)
    boundary_inside = bool(np.any(z[0, :] <= threshold) or np.any(z[-1, :] <= threshold) or np.any(z[:, 0] <= threshold) or np.any(z[:, -1] <= threshold))
    contour_available = bool(float(np.nanmin(z)) <= threshold <= float(np.nanmax(z)))
    contour_touches_frame = bool(contour_available and boundary_inside)
    return {"bestfit_on_frame": bool(bestfit_on_frame), "contour_touches_frame": contour_touches_frame, "truncated_by_frame": bool(bestfit_on_frame or contour_touches_frame)}


def _plot_heatmap(path: Path, dataset: str, tag: str, px: str, py: str, result: Scan2DResult, threshold: float) -> None:
    flags = _truncation_flags(result, threshold)
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    vmax = max(float(np.nanpercentile(result.dchi2_grid, 95.0)), threshold * 1.1)
    mesh = ax.pcolormesh(result.x_values, result.y_values, result.dchi2_grid, shading="auto", cmap="viridis", vmin=0.0, vmax=vmax)
    fig.colorbar(mesh, ax=ax, label="Delta chi2")
    if float(np.nanmin(result.dchi2_grid)) <= threshold <= float(np.nanmax(result.dchi2_grid)):
        ax.contour(result.x_values, result.y_values, result.dchi2_grid, levels=[threshold], colors="white", linewidths=1.5)
    ax.scatter([result.bestfit_x], [result.bestfit_y], color="white", edgecolor="black", s=26, label="grid best")
    ax.scatter([0.0], [0.0], marker="+", color="#ff4d4d", s=70, label="SM")
    if flags["truncated_by_frame"]:
        ax.text(0.02, 0.98, "TRUNCATED BY FRAME", transform=ax.transAxes, va="top", ha="left", color="white", bbox={"facecolor": "#6b0000", "alpha": 0.85, "pad": 3})
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlabel(px)
    ax.set_ylabel(py)
    ax.set_title(f"{dataset} {tag} high-resolution scan")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    _save_figure(fig, path)
    plt.close(fig)


def _plot_overlay(path: Path, tag: str, px: str, py: str, results: Mapping[str, Scan2DResult], threshold: float) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    any_truncated = False
    for label, result in results.items():
        color = DATASET_COLORS[label]
        flags = _truncation_flags(result, threshold)
        any_truncated = any_truncated or flags["truncated_by_frame"]
        if float(np.nanmin(result.dchi2_grid)) <= threshold <= float(np.nanmax(result.dchi2_grid)):
            ax.contour(result.x_values, result.y_values, result.dchi2_grid, levels=[threshold], colors=color, linewidths=1.7)
        ax.scatter([result.bestfit_x], [result.bestfit_y], color=color, s=18, label=f"{label} best")
    ax.scatter([0.0], [0.0], marker="+", color="0.35", s=70, label="SM")
    if any_truncated:
        ax.text(0.02, 0.98, "ONE OR MORE CONTOURS TRUNCATED", transform=ax.transAxes, va="top", ha="left", color="white", bbox={"facecolor": "#6b0000", "alpha": 0.85, "pad": 3})
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlabel(px)
    ax.set_ylabel(py)
    ax.set_title(f"COHERENT Flavor {tag} contours")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    _save_figure(fig, path)
    plt.close(fig)


def _summary_row(dataset: str, tag: str, px: str, py: str, result: Scan2DResult, threshold: float) -> dict[str, object]:
    finite = np.asarray(result.dchi2_grid, dtype=float)
    flags = _truncation_flags(result, threshold)
    return {"dataset": dataset, "plane": tag, "x_parameter": px, "y_parameter": py, "x_min": -1.0, "x_max": 1.0, "y_min": -1.0, "y_max": 1.0, "grid_n": int(result.x_values.size), "bestfit_x": float(result.bestfit_x), "bestfit_y": float(result.bestfit_y), "chi2_min": float(result.chi2_min), "dchi2_max": float(np.nanmax(finite)), "threshold_90cl": float(threshold), "contour_available": bool(float(np.nanmin(finite)) <= threshold <= float(np.nanmax(finite))), **flags}


def _csi_convergence_row(dataset: str, kernel: Path) -> dict[str, object]:
    meta = json.loads(kernel.with_suffix(".json").read_text(encoding="utf-8"))
    ok = bool(meta.get("fast_slow_allclose", False))
    return {"dataset": dataset, "method": "metadata_fast_vs_authoritative_slow_reference", "kernel": str(kernel), "n_er": meta.get("n_ER", ""), "n_enu": meta.get("n_Enu", ""), "n_obs_or_pe_sub": meta.get("n_PE_sub", ""), "slow_reference": meta.get("slow_reference_path", ""), "max_abs_bin_delta": meta.get("max_abs_bin_delta_vs_slow_reference", ""), "total_delta": meta.get("total_delta_vs_slow_reference", ""), "tolerance": f"rtol={meta.get('fast_slow_rtol', '')}; atol={meta.get('fast_slow_atol', '')}", "pass": ok, "note": "authoritative Flavor Fast kernel metadata"}


def _ar_convergence_row(kernel: Path, responses: Path, *, n_er: int, n_enu: int, n_obs_sub: int) -> dict[str, object]:
    fast = predict_raw_components("Ar2020", {}, mode="fast", fast_kernel_path=kernel)
    slow = slow_counts_ar2020(responses, include_sm=True, n_er=n_er, n_enu=n_enu, n_pe_bin=n_obs_sub)
    fast_total = np.asarray(fast.total.values, dtype=float)
    slow_total = np.asarray(slow["counts_per_bin"]["total"], dtype=float)
    delta = fast_total - slow_total
    ok = bool(np.allclose(fast_total, slow_total, rtol=1.0e-9, atol=2.0e-8))
    return {"dataset": "Ar2020", "method": "direct_fast_vs_slow_same_grid_sm", "kernel": str(kernel), "n_er": n_er, "n_enu": n_enu, "n_obs_or_pe_sub": n_obs_sub, "slow_reference": "computed in run from slow_counts_ar2020", "max_abs_bin_delta": float(np.max(np.abs(delta))), "total_delta": float(np.sum(delta)), "tolerance": "rtol=1e-9; atol=2e-8", "pass": ok, "note": "Ar2020 generated Fast kernel checked against matching slow integration for SM counts"}


def _convergence_rows(kernels: Mapping[str, Path], responses: Path, args: argparse.Namespace) -> list[dict[str, object]]:
    return [_csi_convergence_row("CsI2021", kernels["CsI2021"]), _csi_convergence_row("CsI2017", kernels["CsI2017"]), _ar_convergence_row(kernels["Ar2020"], responses, n_er=int(args.ar_n_er), n_enu=int(args.ar_n_enu), n_obs_sub=int(args.ar_n_obs_sub))]


def run(args: argparse.Namespace) -> Path:
    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    responses = Path(args.responses).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    kernels = {"CsI2021": Path(args.csi2021_fast_kernel).resolve(), "CsI2017": Path(args.csi2017_fast_kernel).resolve(), "Ar2020": _ensure_ar_kernel(out_dir, responses, n_er=int(args.ar_n_er), n_enu=int(args.ar_n_enu), n_obs_sub=int(args.ar_n_obs_sub))}
    conv_rows = _convergence_rows(kernels, responses, args)
    _write_csv(out_dir / "integration_convergence_checks.csv", conv_rows, ["dataset", "method", "kernel", "n_er", "n_enu", "n_obs_or_pe_sub", "slow_reference", "max_abs_bin_delta", "total_delta", "tolerance", "pass", "note"])
    values = np.linspace(-1.0, 1.0, int(args.grid_n), dtype=float)
    threshold = confidence_definition("legacy_2d_90_flow_a").delta_chi2
    summary_rows: list[dict[str, object]] = []
    for tag, (px, py) in PLANES.items():
        plane_results: dict[str, Scan2DResult] = {}
        for dataset in DATASET_ORDER:
            npz_path = out_dir / f"{dataset.lower()}_2d_{tag}_grid{values.size}_range_m1_p1.npz"
            result = _get_or_scan(dataset, kernels[dataset], px, py, values, npz_path)
            plane_results[dataset] = result
            _save_scan_npz(npz_path, result, threshold)
            _plot_heatmap(out_dir / f"fig_{dataset.lower()}_{tag}_grid{values.size}_range_m1_p1.png", dataset, tag, px, py, result, threshold)
            summary_rows.append(_summary_row(dataset, tag, px, py, result, threshold))
        combined_npz = out_dir / f"combined_2d_{tag}_grid{values.size}_range_m1_p1.npz"
        combined = _scan_from_npz(combined_npz) if combined_npz.exists() else _combine_results(plane_results)
        _save_scan_npz(combined_npz, combined, threshold, csi2021_delta_chi2=plane_results["CsI2021"].dchi2_grid, csi2017_delta_chi2=plane_results["CsI2017"].dchi2_grid, ar2020_delta_chi2=plane_results["Ar2020"].dchi2_grid)
        summary_rows.append(_summary_row("combined", tag, px, py, combined, threshold))
        with_combined = {**plane_results, "combined": combined}
        _plot_heatmap(out_dir / f"fig_combined_{tag}_grid{values.size}_range_m1_p1.png", "combined", tag, px, py, combined, threshold)
        _plot_overlay(out_dir / f"fig_overlay_csi2021_csi2017_ar2020_{tag}_grid{values.size}_range_m1_p1.png", tag, px, py, with_combined, threshold)
    _write_csv(out_dir / "highres_scan_summary.csv", summary_rows, SUMMARY_FIELDS)
    truncated = [row for row in summary_rows if bool(row["truncated_by_frame"])]
    png_count = len(list(out_dir.glob("fig_*.png")))
    pdf_count = len(list(out_dir.glob("fig_*.pdf")))
    pass_status = all(str(row["pass"]).lower() == "true" for row in conv_rows) and png_count >= 15 and pdf_count >= 15
    metadata = {"git_commit": _git_commit(root), "datasets": list(DATASET_ORDER), "planes": {key: list(value) for key, value in PLANES.items()}, "range": [-1.0, 1.0], "grid_n": int(args.grid_n), "grid_points_per_plane_per_dataset": int(values.size * values.size), "figure_count_png": int(png_count), "figure_count_pdf": int(pdf_count), "confidence_definition_2d": "legacy_2d_90_flow_a", "threshold_90cl": float(threshold), "G_F_source": "cevns_pyeft.foundation.constants.G_F", "G_F_value": float(G_F), "kernels": {key: str(value) for key, value in kernels.items()}, "ar_kernel_resolution": {"n_er": int(args.ar_n_er), "n_enu": int(args.ar_n_enu), "n_obs_sub": int(args.ar_n_obs_sub)}, "convergence_pass": bool(all(str(row["pass"]).lower() == "true" for row in conv_rows)), "truncated_results": truncated, "status": "PASS" if pass_status else "FAIL", "provenance_status": "legacy approximate statistics; not official COHERENT likelihood"}
    _write_yaml(out_dir / "highres_metadata.yaml", metadata)
    report = f"""# COHERENT Flavor High-Resolution Scan Report

Status: {'PASS' if pass_status else 'FAIL'}

Configuration:
- Datasets: CsI2021, CsI2017, Ar2020, plus combined sum.
- Planes: ee u/d, mumu u/d, real emu u/d.
- Axis range: [-1, 1] for both x and y.
- Grid: {values.size} x {values.size} per dataset per plane.
- Figures: {png_count} PNG at 300 DPI and {pdf_count} PDF.
- 2D threshold: {threshold} from legacy_2d_90_flow_a.

Numerical gates:
- Integration/Fast matching checks: {'PASS' if all(str(row['pass']).lower() == 'true' for row in conv_rows) else 'FAIL'}.
- Figure artifact count: {'PASS' if png_count >= 15 and pdf_count >= 15 else 'FAIL'}.
- Frame truncation rows: {len(truncated)}. Truncated cases are marked in `highres_scan_summary.csv` and on the affected plots.

Important limitation:
These are legacy approximate statistics and are not official COHERENT likelihoods. Ar2020 uses a generated Fast kernel with the resolution recorded in `highres_metadata.yaml`.

Primary artifacts:
- `integration_convergence_checks.csv`
- `highres_scan_summary.csv`
- `highres_metadata.yaml`
- 15+ `fig_*.png` files at 300 DPI
- matching `fig_*.pdf` files
- matching `.npz` grids for each dataset and combined plane.
"""
    (out_dir / "HIGHRES_REPORT.md").write_text(report, encoding="utf-8")
    print(f"Generated high-resolution Flavor scans in {out_dir}")
    print(f"Status: {'PASS' if pass_status else 'FAIL'}; PNG={png_count}; PDF={pdf_count}; truncated={len(truncated)}")
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate high-resolution COHERENT Flavor scans for CsI2021, CsI2017, and Ar2020.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--responses", default="data/responses/responses_all.json")
    parser.add_argument("--out-dir", default="results/flavor_benchmark/COHERENT_highres_all_grid101")
    parser.add_argument("--grid-n", type=int, default=101)
    parser.add_argument("--csi2021-fast-kernel", default="tests/reference_CsI2021/fast_kernel.npz")
    parser.add_argument("--csi2017-fast-kernel", default="tests/reference_CsI2017/fast_kernel.npz")
    parser.add_argument("--ar-n-er", type=int, default=21)
    parser.add_argument("--ar-n-enu", type=int, default=120)
    parser.add_argument("--ar-n-obs-sub", type=int, default=8)
    run(parser.parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
