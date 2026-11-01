from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

REPO = Path.cwd()
BENCH = REPO / "Benchmark" / "260928 COHENRENT-NSI"
SPEC = BENCH / "benchmark_2211_11905_fig3_fig7"
OUT = BENCH / "native_overlap_comparison"
RAW = OUT / "raw_native_approx"
FIGS = OUT / "figures"
REPRO = FIGS / "reproduced"
COMP = FIGS / "comparison"
PAPER = OUT / "paper_originals"
REPORT = OUT / "NATIVE_OVERLAP_COMPARISON_REPORT.md"
CFG = json.loads((SPEC / "manifest.json").read_text(encoding="utf-8"))

sys.path.insert(0, str(REPO / "src"))
from cevns_pyeft.kernels.storage import build_fastscan_template, save_fastscan_template
from cevns_pyeft.statistics.datasets import ar2020_dataset, csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_ar2020_irls, chi2_csi2021
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.predictors import predict_raw_components
from cevns_pyeft.statistics.scans import scan_grid_2d

THRESHOLD = float(CFG["confidence_2d"])
COLORS = {"csi": "#bf438c", "lar": "#e3a12a", "joint": "#2463ad"}
LABELS = {"csi": "CsI2021 native approx", "lar": "Ar2020 native approx", "joint": "CsI2021 + Ar2020"}
EXISTING = REPO / "results" / "flavor_benchmark" / "COHERENT_highres_all_grid101"
PARAM_TO_FIELD = {
    "eps_ee_uV": "epsilon_ee_uV",
    "eps_ee_dV": "epsilon_ee_dV",
    "eps_mumu_uV": "epsilon_mumu_uV",
    "eps_mumu_dV": "epsilon_mumu_dV",
    "eps_emu_dV": "epsilon_emu_dV",
    "eps_etau_dV": "epsilon_etau_dV",
    "eps_mutau_dV": "epsilon_mutau_dV",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "UNKNOWN"


def ensure_dirs() -> None:
    for p in (RAW, REPRO, COMP):
        p.mkdir(parents=True, exist_ok=True)


def ar_kernel() -> Path:
    path = EXISTING / "ar2020_fast_kernel_ne21_nenu120_nobs8" / "ar2020_fast_kernel.npz"
    if path.exists() and path.with_suffix(".json").exists():
        return path
    kdir = OUT / "kernels" / "ar2020_fast_kernel_ne21_nenu120_nobs8"
    kpath = kdir / "ar2020_fast_kernel.npz"
    if kpath.exists() and kpath.with_suffix(".json").exists():
        return kpath
    kdir.mkdir(parents=True, exist_ok=True)
    kernel = build_fastscan_template("Ar2020", REPO / "data" / "responses" / "responses_all.json", n_er=21, n_enu=120, n_obs_sub=8)
    return save_fastscan_template(kpath, kernel)


def kernels() -> dict[str, Path]:
    return {
        "csi": REPO / "tests" / "reference_CsI2021" / "fast_kernel.npz",
        "lar": ar_kernel(),
    }


def kwargs_from_xy(xname: str, yname: str, x: float, y: float) -> dict[str, float]:
    return {PARAM_TO_FIELD[xname]: float(x), PARAM_TO_FIELD[yname]: float(y)}


def wilson(kwargs: dict[str, float]):
    return vector_nsi_to_np_wilson(VectorNSIParameters(**kwargs))


def chi2(dataset: str, kernel: Path, kwargs: dict[str, float]) -> float:
    experiment = "CsI2021" if dataset == "csi" else "Ar2020"
    pred = predict_raw_components(experiment, wilson(kwargs), mode="fast", fast_kernel_path=kernel)
    if dataset == "csi":
        ds = csi2021_dataset()
        return float(chi2_csi2021(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds).chi2)
    ds = ar2020_dataset()
    return float(chi2_ar2020_irls(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds).chi2)


def maybe_from_existing(spec: dict[str, Any], dataset: str) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    # Existing highres files use x=uV, y=dV. Fig.3 needs x=dV, y=uV, so transpose.
    xname, yname = spec["x"], spec["y"]
    if (xname, yname) == ("eps_ee_dV", "eps_ee_uV"):
        path = EXISTING / f"{'csi2021' if dataset == 'csi' else 'ar2020'}_2d_ee_uV_dV_grid101_range_m1_p1.npz"
    elif (xname, yname) == ("eps_mumu_dV", "eps_mumu_uV"):
        path = EXISTING / f"{'csi2021' if dataset == 'csi' else 'ar2020'}_2d_mumu_uV_dV_grid101_range_m1_p1.npz"
    else:
        return None
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as z:
        x_old = np.asarray(z["x_values"], dtype=float)  # uV
        y_old = np.asarray(z["y_values"], dtype=float)  # dV
        chi = np.asarray(z["chi2_grid"], dtype=float)
    return y_old, x_old, chi.T


def scan_panel(fig_no: str, row: dict[str, Any], grid_n: int, ks: dict[str, Path]) -> Path:
    out = RAW / f"fig{fig_no}_{row['id']}.npz"
    if out.exists():
        return out
    x = np.linspace(float(row["xlim"][0]), float(row["xlim"][1]), grid_n)
    y = np.linspace(float(row["ylim"][0]), float(row["ylim"][1]), grid_n)
    arrays: dict[str, np.ndarray] = {}
    axes_from_existing = None
    for dataset in ("csi", "lar"):
        existing = maybe_from_existing(row, dataset)
        if existing is not None:
            ex, ey, chi = existing
            if np.array_equal(ex, x) and np.array_equal(ey, y):
                print(f"reuse existing Fig.{fig_no} {row['id']} {dataset}", flush=True)
                arrays[f"chi2_{dataset}"] = chi
                axes_from_existing = (ex, ey)
                continue
        print(f"scan Fig.{fig_no} {row['id']} {dataset} {grid_n}x{grid_n}", flush=True)
        result = scan_grid_2d(x, y, lambda xx, yy, d=dataset: chi2(d, ks[d], kwargs_from_xy(row["x"], row["y"], xx, yy)))
        arrays[f"chi2_{dataset}"] = result.chi2_grid
    arrays["chi2_joint"] = arrays["chi2_csi"] + arrays["chi2_lar"]
    np.savez(out, x=x, y=y, **arrays)
    return out


def dchi(arr: np.ndarray) -> np.ndarray:
    return arr - np.nanmin(arr)


def load_grid(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k], dtype=float) for k in z.files}


def contour(ax, grid: dict[str, np.ndarray], who: str, filled: bool = True) -> None:
    z = dchi(grid[f"chi2_{who}"])
    X, Y = np.meshgrid(grid["x"], grid["y"])
    if float(np.nanmin(z)) <= THRESHOLD <= float(np.nanmax(z)):
        if filled:
            ax.contourf(X, Y, z, levels=[-1e-9, THRESHOLD], colors=[COLORS[who]], alpha=0.18)
        ax.contour(X, Y, z, levels=[THRESHOLD], colors=[COLORS[who]], linewidths=1.8)
    elif float(np.nanmax(z)) <= THRESHOLD:
        ax.text(0.5, 0.96, f"{who} allowed region exceeds frame", transform=ax.transAxes, ha="center", va="top", fontsize=7)
    else:
        ax.text(0.5, 0.96, f"{who} no 90% contour in frame", transform=ax.transAxes, ha="center", va="top", fontsize=7)


def style_axis(ax, row: dict[str, Any]) -> None:
    ax.set_xlabel(row["x"])
    ax.set_ylabel(row["y"])
    ax.set_xlim(*row["xlim"])
    ax.set_ylim(*row["ylim"])
    ax.grid(alpha=0.16)


def plot_fig(fig_no: str) -> Path:
    cfg = CFG["figures"][fig_no]
    fig, axs = plt.subplots(2, 2, figsize=(11, 9), layout="constrained")
    for r, row in enumerate(cfg["rows"]):
        grid = load_grid(RAW / f"fig{fig_no}_{row['id']}.npz")
        for who in ("csi", "lar"):
            contour(axs[r, 0], grid, who, filled=True)
            axs[r, 0].plot([], [], color=COLORS[who], label=LABELS[who])
        contour(axs[r, 1], grid, "joint", filled=True)
        axs[r, 1].plot([], [], color=COLORS["joint"], label=LABELS["joint"])
        style_axis(axs[r, 0], row)
        style_axis(axs[r, 1], row)
        axs[r, 0].set_title(f"{row['id']}: separate CsI2021 / Ar2020")
        axs[r, 1].set_title(f"{row['id']}: joint CsI2021 + Ar2020")
        axs[r, 0].legend(fontsize=8, loc="best")
        axs[r, 1].legend(fontsize=8, loc="best")
    fig.suptitle(f"Native approximate reproduction | Fig. {fig_no} overlap | {cfg['title']}\nNot paper-matched: CEvNS-pyEFT legacy approximate statistics", fontsize=12)
    out = REPRO / f"Fig{int(fig_no):02d}_native_approx_reproduction.png"
    fig.savefig(out, dpi=180)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def paper_page(fig_no: int) -> Path:
    return PAPER / f"paper_page-{fig_no + 16:02d}.png"  # Fig3 page19, Fig4 page20, ...


def compare_image(fig_no: int, repro: Path) -> Path:
    left = Image.open(paper_page(fig_no)).convert("RGB")
    right = Image.open(repro).convert("RGB")
    W, H, gap, head = 1050, 1280, 35, 80
    def fit(im: Image.Image) -> Image.Image:
        im = im.copy()
        im.thumbnail((W, H), Image.Resampling.LANCZOS)
        return im
    left = fit(left)
    right = fit(right)
    canvas = Image.new("RGB", (2 * W + gap, H + head), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((14, 18), f"Paper original page render: Fig. {fig_no} area must be manually crop-audited", fill="black")
    draw.text((W + gap + 14, 18), "CEvNS-pyEFT native approximate reproduction", fill="black")
    canvas.paste(left, ((W - left.width) // 2, head + (H - left.height) // 2))
    canvas.paste(right, (W + gap + (W - right.width) // 2, head + (H - right.height) // 2))
    out = COMP / f"Fig{fig_no:02d}_native_approx_comparison.png"
    canvas.save(out)
    return out


def fig7_placeholder() -> Path:
    original = Image.open(paper_page(7)).convert("RGB")
    original.thumbnail((1050, 1280), Image.Resampling.LANCZOS)
    W, H, gap, head = 1050, 1280, 35, 80
    canvas = Image.new("RGB", (2 * W + gap, H + head), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((14, 18), "Paper original page render: Fig. 7", fill="black")
    draw.text((W + gap + 14, 18), "No native reproduction: NGI scalar/tensor not implemented in this comparison", fill="black")
    canvas.paste(original, ((W - original.width) // 2, head + (H - original.height) // 2))
    lines = [
        "Fig. 7 is NGI scalar/vector/tensor, not vector NSI epsilon.",
        "This run only covers the NSI overlap of Fig. 3-6 with current CEvNS-pyEFT Flavor machinery.",
        "Status: NGI_MISSING / NOT_COMPARABLE.",
        "No fake scalar/tensor arrays were generated.",
    ]
    y = head + 120
    for line in lines:
        draw.text((W + gap + 60, y), line, fill="black")
        y += 42
    out = COMP / "Fig07_NGI_not_comparable.png"
    canvas.save(out)
    return out


def write_report(rows: list[dict[str, Any]], comparisons: list[Path], provenance: dict[str, Any]) -> None:
    csv_path = OUT / "panel_status.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "provenance_native_overlap.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# 2211.11905 Fig.3-Fig.7 native overlap comparison",
        "",
        "Status: PARTIAL_NATIVE_APPROXIMATE_COMPARISON",
        "",
        "This output follows the benchmark folder definitions, but it is not a paper-matched reproduction. It uses the migrated CEvNS-pyEFT Flavor Fast kernels and legacy approximate statistics, while the paper uses CsI/LAr timing-energy likelihoods and paper-specific nuisance models.",
        "",
        "What was generated:",
        "- Paper original page renders for Fig.3-Fig.7 from the local `2211.11905v2.pdf`.",
        "- Native approximate reproduced contours for Fig.3-Fig.6 using CsI2021 and Ar2020 only.",
        "- Side-by-side comparison PNGs for Fig.3-Fig.6.",
        "- A Fig.7 placeholder comparison declaring NGI_MISSING / NOT_COMPARABLE.",
        "",
        "Important differences from the benchmark paper:",
        "- LAr is represented by the current Ar2020 legacy approximate likelihood, not the paper Eq. (3.12)-(3.13) timing-energy likelihood.",
        "- CsI uses the current CsI2021 legacy approximate likelihood, not the paper 9 PE x 11 timing Poisson likelihood.",
        "- CsI2017 is intentionally not added to the paper-style joint result.",
        "- Fig.7 NGI scalar/tensor is not reproduced; no surrogate NSI plot was used.",
        "- Paper originals are full page renders, not manually audited figure crops.",
        "",
        "Panel status table: `panel_status.csv`.",
        "Raw native approximate NPZ: `raw_native_approx/`.",
        "Reproduced figures: `figures/reproduced/`.",
        "Comparison figures: `figures/comparison/`.",
        "",
        "Generated comparison files:",
    ]
    lines.extend([f"- `{p.relative_to(OUT).as_posix()}`" for p in comparisons])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    ks = kernels()
    grid_n = 101
    rows: list[dict[str, Any]] = []
    for fig_no in ("3", "4", "5", "6"):
        for row in CFG["figures"][fig_no]["rows"]:
            path = scan_panel(fig_no, row, grid_n, ks)
            rows.append({
                "figure": f"Fig{fig_no}",
                "panel": row["id"],
                "x": row["x"],
                "y": row["y"],
                "grid_n": grid_n,
                "status": "NATIVE_APPROXIMATE_GENERATED",
                "raw_npz": str(path.relative_to(OUT)),
            })
    comparisons: list[Path] = []
    for fig_no in (3, 4, 5, 6):
        repro = plot_fig(str(fig_no))
        comparisons.append(compare_image(fig_no, repro))
    comparisons.append(fig7_placeholder())
    rows.append({"figure": "Fig7", "panel": "all", "x": "NGI", "y": "NGI", "grid_n": "", "status": "NGI_MISSING_NOT_COMPARABLE", "raw_npz": ""})
    provenance = {
        "mode": "native approximate overlap comparison; not paper-matched reproduction",
        "git_commit": git_commit(),
        "paper_pdf": str((BENCH / "2211.11905v2.pdf").resolve()),
        "paper_sha256": sha256(BENCH / "2211.11905v2.pdf"),
        "manifest_sha256": sha256(SPEC / "manifest.json"),
        "grid_n": grid_n,
        "threshold_2d": THRESHOLD,
        "kernels": {k: str(v) for k, v in ks.items()},
    }
    write_report(rows, comparisons, provenance)
    print(OUT)
    print(REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
