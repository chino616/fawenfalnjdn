"""Reproduce and package the current CONUS+ completion artifacts.

The runner deliberately keeps three configurations separate: the forward
prediction uses C2/C3/C5 at 119 kg day each, while the paper benchmark uses the
independent effective-119 configuration and its 19 digitized excess points.
The current detector-response matrix is exposed as a Fast artifact; the full
114-coordinate EFT quadratic kernel remains an explicit pending capability.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data" / "experiments" / "CONUS_Plus" / "conus_plus_2025_c2c3c5_ge73_pyeft"
DIAGNOSTICS = ROOT / "workflows" / "experiment-integration" / "runs" / "CONUS_Plus" / "conus_plus_2025_c2c3c5_ge73_pyeft" / "diagnostics"
BENCHMARK = DATASET / "statistics" / "approximate_paper_benchmark"
DEFAULT_OUTPUT = ROOT / "outputs" / "conus-plus-completion-20261012"


def _dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == target.resolve():
        return
    shutil.copy2(source, target)


def _copy_tree(source: Path, target: Path) -> None:
    if source.resolve() == target.resolve():
        return
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write_rows(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def forward(output: Path) -> None:
    """Materialize the direct P06/P07 arrays and their provenance."""

    data = output / "data"
    _copy(DIAGNOSTICS / "03_source_spectrum.csv", data / "source_spectrum.csv")
    _copy(DIAGNOSTICS / "07_true_recoil_spectrum.csv", data / "recoil_spectra.csv")
    _copy(DIAGNOSTICS / "07_slow_counts.csv", data / "bin_counts.csv")
    _copy(DIAGNOSTICS / "07_slow_reference.npz", data / "bin_counts.npz")
    _copy(DIAGNOSTICS / "07_slow_reference.json", data / "bin_counts_metadata.json")
    _copy(DIAGNOSTICS / "07_convergence.csv", data / "integration_convergence.csv")
    _copy(DIAGNOSTICS / "07_normalization_ledger.csv", data / "normalization_ledger.csv")
    _copy(DIAGNOSTICS / "06_detector_response.csv", data / "detector_response.csv")
    _copy(DIAGNOSTICS / "06_detector_response.png", data / "detector_response.png")
    _copy(DIAGNOSTICS / "03_source_spectrum.png", data / "source_spectrum.png")

    rows = _read_rows(DIAGNOSTICS / "07_slow_counts.csv")
    reconstructed = []
    for row in rows:
        reconstructed.append(
            {
                "bin_index": row["bin_index"],
                "low_eVee": row["low_eVee"],
                "high_eVee": row["high_eVee"],
                "C2_events": row["C2_events"],
                "C3_events": row["C3_events"],
                "C5_events": row["C5_events"],
                "combined_events": row["combined_events"],
            }
        )
    _write_rows(data / "reconstructed_spectra.csv", reconstructed)
    _dump(
        data / "forward_metadata.json",
        {
            "dataset_id": "conus_plus_2025_c2c3c5_ge73_pyeft",
            "target": "Ge73-only",
            "detectors": ["C2", "C3", "C5"],
            "exposures_kg_day": {"C2": 119.0, "C3": 119.0, "C5": 119.0},
            "total_exposure_kg_day": 357.0,
            "normalization": "direct differential-rate integration; no reference-count rescaling",
            "source_model": "Kopeikin below 2 MeV + Mueller polynomial through 10 MeV",
            "bin_unit": "events/bin",
            "source_of_arrays": "formal workflows/experiment-integration diagnostics",
        },
    )


def build_kernel(output: Path) -> None:
    """Declare the supported basis and report the honest kernel state."""

    fast = output / "fast"
    fast.mkdir(parents=True, exist_ok=True)
    basis = ROOT / "outputs" / "conus-plus-completion-20261012" / "fast" / "conus_eft_basis.json"
    if basis.exists():
        _copy(basis, fast / "conus_eft_basis.json")
    else:
        from cevns_pyeft.experiments.conus_plus.eft_kernel import coordinate_metadata, reactor_visible_coordinates

        _dump(
            fast / "conus_eft_basis.json",
            {
                "schema_version": 1,
                "dataset_id": "conus_plus_2025_c2c3c5_ge73_pyeft",
                "basis_name": "li2026_reactor_visible_real_coordinates",
                "initial_flavor": "e",
                "coordinate_count": len(reactor_visible_coordinates()),
                "coordinates": coordinate_metadata(),
                "status": "BASIS_DECLARED_KERNEL_BUILD_PENDING",
            },
        )
    _dump(
        fast / "kernel_build_status.json",
        {
            "status": "BASIS_DECLARED_KERNEL_BUILD_PENDING",
            "coordinate_count": 114,
            "detector_matrix_available": True,
            "full_eft_quadratic_kernel_available": False,
            "reason": "A detector-response matrix is not a coefficient-dependent EFT kernel. Direct samples for all 114 real coordinates and independent mixed-point validation remain to be run.",
            "next": "build direct CONUS+ samples with the fixed Ge73/source/response contract, then save conus_kernel.npz only after held-out validation.",
        },
    )


def statistics(output: Path) -> None:
    target = output / "statistics" / "approximate_paper_benchmark"
    _copy_tree(BENCHMARK, target)
    metrics = json.loads((BENCHMARK / "benchmark_metrics.json").read_text(encoding="utf-8"))
    _copy(DIAGNOSTICS / "09_observations_digitized_approx.csv", target / "observations_digitized_approx.csv")
    _copy(DIAGNOSTICS / "09_observations_metadata.json", target / "observations_metadata.json")
    _dump(
        output / "statistics" / "fit_summary.json",
        {
            "status": "PASS_WITH_DOCUMENTED_LIMITATION",
            "likelihood": metrics["data_semantics"],
            "effective_119": {
                "sm_events": metrics["B0_fig1"]["current_SM_total"],
                "paper_digitized_curve_events": metrics["B0_fig1"]["paper_curve_digitized_total"],
                "sin2thetaW_best": metrics["B1_weak_angle"]["best_fit"],
                "sin2thetaW_1sigma": metrics["B1_weak_angle"]["one_sigma_intervals"],
                "magnetic_moment_cevns_only_90cl_muB": metrics["B4_magnetic_moment"]["upper_90cl_muB"],
            },
            "three_detector_119_each": {
                "exposures_kg_day": [119.0, 119.0, 119.0],
                "detector_totals": [89.70778817448614, 150.3408190683611, 116.20231962643969],
                "combined_events": 356.25092686928696,
            },
            "reference": "arXiv:2501.17843v2 Fig.1/Fig.4 benchmark; digitized Gaussian Eq.(33) approximation",
            "official_likelihood": False,
            "electron_scattering": False,
        },
    )
    # A flat table is convenient for downstream plotting and manuscript checks.
    for name in ("weak_angle.csv", "magnetic_moment_cevns_only.csv", "nsi_u.csv", "nsi_d.csv", "nsi_u_d.csv"):
        source = target / "scans" / name
        if source.exists():
            _copy(source, output / "statistics" / "chi2_curves" / name)
    for name in ("nsi_u_d_grid.npz", "fig4_mixed_diagonal_flavor_grid.npz", "fig4_flavor_changing_u_d_grid.npz"):
        source = target / "scans" / name
        if source.exists():
            _copy(source, output / "statistics" / "nsi_grids" / name)


def figures(output: Path) -> None:
    # Import lazily so forward/statistics remain usable in headless minimal installs.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figdir = output / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    source = np.genfromtxt(output / "data" / "source_spectrum.csv", delimiter=",", names=True)
    recoil = np.genfromtxt(output / "data" / "recoil_spectra.csv", delimiter=",", names=True)
    bins = np.genfromtxt(output / "data" / "reconstructed_spectra.csv", delimiter=",", names=True)
    obs = np.genfromtxt(output / "statistics" / "approximate_paper_benchmark" / "observations_digitized_approx.csv", delimiter=",", names=True)
    sm = np.genfromtxt(output / "statistics" / "approximate_paper_benchmark" / "predictions" / "SM_effective119.csv", delimiter=",", names=True)
    weak = np.genfromtxt(output / "statistics" / "chi2_curves" / "weak_angle.csv", delimiter=",", names=True)
    mag = np.genfromtxt(output / "statistics" / "chi2_curves" / "magnetic_moment_cevns_only.csv", delimiter=",", names=True)

    def save(fig: plt.Figure, stem: str) -> None:
        fig.savefig(figdir / f"{stem}.pdf", bbox_inches="tight")
        fig.savefig(figdir / f"{stem}.png", dpi=320, bbox_inches="tight")
        plt.close(fig)

    # K1: three layers, explicit reuse/adaptation, and the stop branch.
    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    colors = {"reuse": "#d9edf7", "adapt": "#fce4d6", "pass": "#dff0d8", "pending": "#fff2cc", "stop": "#f4cccc"}
    ax.text(0.02, 0.91, "INPUT MATERIALS", fontsize=11, weight="bold", color="#444444")
    ax.text(0.02, 0.57, "EXECUTION / GATES", fontsize=11, weight="bold", color="#444444")
    ax.text(0.02, 0.18, "FORMAL PRODUCTS", fontsize=11, weight="bold", color="#444444")

    def box(x, y, w, h, label, color):
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9,
                bbox={"boxstyle": "round,pad=0.55", "facecolor": colors[color], "edgecolor": "#333333"})

    box(.08, .76, .18, .10, "paper PDF +\ndigitized 19 bins", "reuse")
    box(.31, .76, .18, .10, "reactor source tables\nKopeikin/Mueller", "adapt")
    box(.54, .76, .18, .10, "detector parameters\nthreshold/efficiency", "adapt")
    box(.77, .76, .15, .10, "Ge73 response\nJSON database", "reuse")
    box(.08, .40, .18, .11, "input/contract\nchecks", "reuse")
    box(.31, .40, .20, .11, "shared Li2026\ntheory + adapter", "reuse")
    box(.56, .40, .16, .11, "Direct Slow\nP06/P07 PASS", "pass")
    box(.77, .40, .15, .11, "P08 matrix PASS\nEFT kernel pending", "pending")
    box(.20, .07, .18, .11, "experiment.yaml\nconfiguration", "adapt")
    box(.43, .07, .18, .11, "recoil + reconstructed\nbin arrays", "pass")
    box(.66, .07, .16, .11, "χ² scans +\nfigures/tables", "pending")
    box(.84, .24, .13, .10, "missing input\nSTOP / BLOCKED", "stop")

    arrows = [((.17, .76), (.17, .51)), ((.40, .76), (.40, .51)), ((.63, .76), (.63, .51)), ((.84, .76), (.84, .51)), ((.26, .455), (.31, .455)), ((.51, .455), (.56, .455)), ((.72, .455), (.77, .455)), ((.40, .40), (.29, .18)), ((.64, .40), (.52, .18)), ((.84, .40), (.74, .18)), ((.72, .40), (.84, .34))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.4, "color": "#333333"})
    ax.legend(handles=[Patch(facecolor=colors["reuse"], edgecolor="#333333", label="shared/reused framework"), Patch(facecolor=colors["adapt"], edgecolor="#333333", label="CONUS+ input/adapter"), Patch(facecolor=colors["pass"], edgecolor="#333333", label="machine-validated"), Patch(facecolor=colors["pending"], edgecolor="#333333", label="documented partial"), Patch(facecolor=colors["stop"], edgecolor="#333333", label="stop on missing input")], loc="upper center", bbox_to_anchor=(.5, -.01), ncol=3, fontsize=8, frameon=False)
    ax.set_title("K1. CONUS+ Skill-guided integration: reuse, adaptation, validation and stop conditions\nformal project configuration; version record 2026-10-12")
    save(fig, "fig_conus_skill_workflow")

    # K2: source, true recoil and reconstructed events.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), constrained_layout=True)
    axes[0].plot(source["energy_mev"], source["total_flux_cm2_s1_MeV1"], color="#0072B2")
    axes[0].set(xlabel=r"$E_\nu$ [MeV]", ylabel=r"Flux [cm$^{-2}$ s$^{-1}$ MeV$^{-1}$]")
    axes[0].set_title("(a) frozen reactor source")
    axes[1].plot(recoil["recoil_keVnr"], recoil["total_events_per_kg_day_keVnr"], color="#009E73")
    axes[1].set(xlabel=r"$T$ [keVnr]", ylabel="events kg$^{-1}$ day$^{-1}$ keVnr$^{-1}$")
    axes[1].set_title("(b) Ge73 recoil rate")
    centers = 0.5 * (bins["low_eVee"] + bins["high_eVee"])
    for name, color in (("C2_events", "#D55E00"), ("C3_events", "#0072B2"), ("C5_events", "#009E73"), ("combined_events", "#000000")):
        axes[2].step(centers, bins[name], where="mid", label=name.replace("_events", ""), color=color)
    axes[2].errorbar(
        obs["center_eVee"],
        obs["observed_excess_per_kg_10eVee"],
        yerr=np.vstack((obs["sigma_minus"], obs["sigma_plus"])),
        fmt="o",
        ms=3.8,
        capsize=2,
        color="#7A1FA2",
        label="digitized excess ± error (effective 119 only)",
    )
    axes[2].set(xlabel=r"$E_{rec}$ [eVee]", ylabel="events/bin")
    axes[2].set_title("(c) reconstructed counts; data correspond to C3-like effective 119")
    axes[2].legend(fontsize=7)
    save(fig, "fig_conus_forward_chain")

    # K3: benchmark panels.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), constrained_layout=True)
    centers = 0.5 * (obs["low_eVee"] + obs["high_eVee"])
    axes[0].errorbar(centers, obs["observed_excess_per_kg_10eVee"], yerr=obs["sigma_used_half_span"], fmt="o", label="digitized excess", color="#000000")
    axes[0].step(centers, sm["current_response_SM_effective119"], where="mid", label="current SM", color="#0072B2")
    axes[0].step(centers, obs["paper_theory_plot_height"], where="mid", label="paper curve", color="#D55E00")
    axes[0].set(xlabel="Erec [eVee]", ylabel="events/bin", title="(a) effective 119 benchmark")
    axes[0].legend(fontsize=8)
    axes[1].plot(weak["sin2thetaW"], weak["delta_chi2"], color="#0072B2")
    axes[1].axhline(1.0, color="#666666", ls="--")
    axes[1].set(xlabel=r"$\sin^2\theta_W$", ylabel=r"$\Delta\chi^2$", title="(b) weak mixing angle")
    axes[2].plot(mag["mu_eff_over_muB"] / 1e-10, mag["delta_chi2"], color="#009E73")
    axes[2].axhline(2.71, color="#666666", ls="--", label="90% threshold")
    axes[2].set(xlabel=r"$\mu_{eff}/(10^{-10}\,\mu_B)$", ylabel=r"$\Delta\chi^2$", title="(c) CEvNS-only magnetic moment")
    axes[2].legend(fontsize=8)
    save(fig, "fig_conus_statistical_benchmark")

    # K4: the available matrix validation, explicitly not the EFT kernel.
    comparison = np.genfromtxt(DIAGNOSTICS / "08_slow_fast_comparison.csv", delimiter=",", names=True)
    summary = json.loads((DIAGNOSTICS / "08_fast_summary.json").read_text(encoding="utf-8"))
    atol = max(1.0e-10, 1.0e-8 * float(np.max(sm["current_response_SM_effective119"])))
    ratio = comparison["abs_difference"] / (atol + 1.0e-5 * np.abs(comparison["slow_events"]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
    axes[0].plot(comparison["bin_index"], ratio, ".", alpha=0.35, color="#0072B2")
    axes[0].axhline(1.0, color="#D55E00", ls="--")
    axes[0].set(xlabel="reconstructed bin index", ylabel="matrix residual / tolerance", title="detector matrix validation")
    names = [p["name"] for p in summary["points"]]
    direct = [p["slow_seconds"] for p in summary["points"]]
    fast = [p["fast_seconds"] for p in summary["points"]]
    axes[1].bar(np.arange(len(names)) - .18, direct, .36, label="direct")
    axes[1].bar(np.arange(len(names)) + .18, fast, .36, label="matrix path")
    axes[1].set_xticks(np.arange(len(names)), names, rotation=20, ha="right", fontsize=8)
    axes[1].set_ylabel("seconds")
    axes[1].set_title("cost comparison (not EFT-kernel speedup)")
    axes[1].legend(fontsize=8)
    save(fig, "fig_conus_fast_validation")

    # A1: use the formal four-panel candidate image as the numerical artifact;
    # also provide a PDF generated from that image for manuscript workflows.
    source_fig = BENCHMARK / "figures" / "fig4_full_nsi_current.png"
    image = plt.imread(source_fig)
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.imshow(image)
    ax.axis("off")
    ax.set_title("CONUS+ vector NSI benchmark; four panels; approximate digitized likelihood")
    save(fig, "fig_conus_nsi_four_panels")


def run(task: str, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    if task in ("all", "forward"):
        forward(output)
    if task in ("all", "build-kernel"):
        build_kernel(output)
    if task in ("all", "statistics"):
        statistics(output)
    if task in ("all", "figures"):
        if not (output / "data" / "reconstructed_spectra.csv").exists():
            forward(output)
        if not (output / "statistics" / "chi2_curves" / "weak_angle.csv").exists():
            statistics(output)
        figures(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DATASET / "experiment.yaml", help="formal CONUS+ configuration")
    parser.add_argument("--task", choices=("all", "forward", "build-kernel", "statistics", "figures"), default="all")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--resume", action="store_true", help="reuse only artifacts with the formal fixed input paths")
    args = parser.parse_args(argv)
    if not args.config.exists():
        parser.error(f"configuration does not exist: {args.config}")
    if not DIAGNOSTICS.exists():
        parser.error(f"formal diagnostics do not exist: {DIAGNOSTICS}")
    run(args.task, args.output.resolve())
    print(json.dumps({"task": args.task, "output": str(args.output.resolve()), "config": str(args.config.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
