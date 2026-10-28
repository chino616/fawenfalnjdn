"""Plot reconstructed CONUS+ counts with digitized data and profile statistics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "conus-plus-completion-20261012"
BENCH = OUT / "statistics" / "approximate_paper_benchmark"
FIGURES = OUT / "figures"


def read_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return {name: np.asarray([float(row[name]) for row in rows]) for name in rows[0]}


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.png", dpi=320, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    obs = read_csv(BENCH / "observations_digitized_approx.csv")
    pred = read_csv(BENCH / "predictions" / "SM_effective119.csv")
    weak = read_csv(OUT / "statistics" / "chi2_curves" / "weak_angle.csv")
    mag = read_csv(OUT / "statistics" / "chi2_curves" / "magnetic_moment_cevns_only.csv")
    metrics = json.loads((BENCH / "benchmark_metrics.json").read_text(encoding="utf-8"))
    centers = obs["center_eVee"]
    observed = obs["observed_excess_per_kg_10eVee"]
    sigma_minus = obs["sigma_minus"]
    sigma_plus = obs["sigma_plus"]
    sigma_used = obs["sigma_used_half_span"]
    current = pred["current_response_SM_effective119"]
    paper = pred["paper_theory_plot_reference"]
    alpha = float(metrics["B0_fig1"]["unprofiled_current_SM_alpha_hat"])
    profiled = (1.0 + alpha) * current
    pull = (observed - profiled) / sigma_used

    # Dedicated reconstructed-counts plot.  All overlaid quantities use the
    # paper's effective-119 plotted normalization; the three-detector 357
    # kg-day prediction is intentionally absent.
    fig, (axis, residual) = plt.subplots(2, 1, figsize=(10.5, 7.7), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.0]}, constrained_layout=True)
    axis.errorbar(centers, observed, yerr=np.vstack((sigma_minus, sigma_plus)), fmt="o", ms=5, capsize=3, color="black", label="digitized background-subtracted excess")
    axis.step(pred["low_eVee"], current, where="post", linewidth=2.2, color="#0072B2", label="current Ge73 + response SM")
    axis.step(pred["low_eVee"], paper, where="post", linewidth=2.0, linestyle="--", color="#D55E00", label="paper theory curve (digitized)")
    axis.set_ylabel("paper plotted normalization / 10 eVee bin")
    axis.set_title("CONUS+ reconstructed spectrum: effective 119 kg day benchmark")
    axis.legend(fontsize=9)
    axis.grid(alpha=0.2)
    residual.axhline(0.0, color="black", linewidth=0.8)
    residual.axhline(1.0, color="0.6", linestyle=":")
    residual.axhline(-1.0, color="0.6", linestyle=":")
    residual.bar(centers, pull, width=8.0, color=np.where(pull >= 0.0, "#56B4E9", "#E69F00"), alpha=0.85)
    residual.set_xlabel("reconstructed energy [eVee]")
    residual.set_ylabel("profiled pull")
    residual.grid(alpha=0.2)
    save(fig, "fig_conus_reconstructed_counts_with_data")

    # Complete statistical summary in one view.
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    axes[0, 0].errorbar(centers, observed, yerr=np.vstack((sigma_minus, sigma_plus)), fmt="o", ms=4, capsize=2, color="black", label="digitized excess")
    axes[0, 0].step(pred["low_eVee"], current, where="post", color="#0072B2", linewidth=2, label="current SM")
    axes[0, 0].step(pred["low_eVee"], paper, where="post", color="#D55E00", linestyle="--", linewidth=1.8, label="paper curve")
    axes[0, 0].set(xlabel="Erec [eVee]", ylabel="paper plotted normalization/bin", title="(a) spectrum and digitized errors")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].axhspan(-1.0, 1.0, color="#d9edf7", alpha=0.7, label="±1σ")
    axes[0, 1].axhline(0.0, color="black", linewidth=0.8)
    axes[0, 1].bar(centers, pull, width=8.0, color="#0072B2", alpha=0.8)
    axes[0, 1].set(xlabel="Erec [eVee]", ylabel="(data − profiled SM) / σ", title=f"(b) bin pulls; α̂={alpha:.4f}")
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.2)

    weak_best = float(metrics["B1_weak_angle"]["best_fit"])
    weak_interval = metrics["B1_weak_angle"]["one_sigma_intervals"][0]
    axes[1, 0].plot(weak["sin2thetaW"], weak["delta_chi2"], color="#0072B2", linewidth=2)
    axes[1, 0].axhline(1.0, color="0.4", linestyle="--", label="Δχ²=1")
    axes[1, 0].axvline(weak_best, color="#D55E00", linestyle="-", label=f"best={weak_best:.4f}")
    axes[1, 0].axvspan(float(weak_interval["left"]), float(weak_interval["right"]), color="#009E73", alpha=0.18, label="1σ interval")
    axes[1, 0].set(xlabel=r"$\sin^2\theta_W$", ylabel=r"profile $\Delta\chi^2$", title="(c) weak mixing angle")
    axes[1, 0].set_ylim(bottom=0.0)
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.2)

    mu_best = float(metrics["B4_magnetic_moment"]["best_fit_muB"]) / 1.0e-10
    mu_upper = float(metrics["B4_magnetic_moment"]["upper_90cl_muB"]) / 1.0e-10
    axes[1, 1].plot(mag["mu_eff_over_muB"] / 1.0e-10, mag["delta_chi2"], color="#009E73", linewidth=2)
    axes[1, 1].axhline(2.71, color="0.4", linestyle="--", label="90% threshold")
    axes[1, 1].axvline(mu_best, color="#0072B2", linestyle=":", label=f"best={mu_best:.2f}")
    axes[1, 1].axvline(mu_upper, color="#D55E00", linestyle="-", label=f"90% upper={mu_upper:.2f}")
    axes[1, 1].set(xlabel=r"$\mu_{eff}/(10^{-10}\,\mu_B)$", ylabel=r"profile $\Delta\chi^2$", title="(d) CEvNS-only magnetic moment")
    axes[1, 1].set_ylim(bottom=0.0)
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.2)
    save(fig, "fig_conus_statistical_analysis")

    summary = {
        "status": "APPROXIMATE_DIGITIZED_BENCHMARK",
        "data": "19 background-subtracted excess points digitized from arXiv:2501.17843v2 Fig.1",
        "errors": "asymmetric digitized bars shown; symmetric half-span used in chi2",
        "official_machine_readable_data": False,
        "configuration": "effective 119 kg day, C3-like 160 eVee response",
        "sm_profile": {"chi2": float(metrics["B0_fig1"]["unprofiled_current_SM_chi2"]), "alpha_hat": alpha},
        "weak_angle": {"best": weak_best, "one_sigma": [float(weak_interval["left"]), float(weak_interval["right"])], "chi2_min": float(metrics["B1_weak_angle"]["chi2_min"])},
        "magnetic_moment_cevns_only": {"best_muB": float(metrics["B4_magnetic_moment"]["best_fit_muB"]), "upper_90cl_muB": float(metrics["B4_magnetic_moment"]["upper_90cl_muB"]), "chi2_min": float(metrics["B4_magnetic_moment"]["chi2_min"]), "delta_chi2_threshold": 2.71},
        "p_value": "not reported; official likelihood/covariance and coverage calibration are unavailable",
    }
    (OUT / "statistics" / "statistical_analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
