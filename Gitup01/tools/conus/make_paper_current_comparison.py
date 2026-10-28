"""Make an explicit paper-curve versus response-folded CONUS+ comparison."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "conus-plus-completion-20261012"
PRED = OUT / "statistics" / "approximate_paper_benchmark" / "predictions" / "SM_effective119.csv"


def main() -> None:
    with PRED.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    low = np.asarray([float(row["low_eVee"]) for row in rows])
    high = np.asarray([float(row["high_eVee"]) for row in rows])
    current = np.asarray([float(row["current_response_SM_effective119"]) for row in rows])
    paper = np.asarray([float(row["paper_theory_plot_reference"]) for row in rows])
    difference = current - paper
    ratio = current / paper
    table_path = OUT / "statistics" / "paper_vs_current_comparison.csv"
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["bin_index", "low_eVee", "high_eVee", "current_response_SM_effective119", "paper_theory_digitized", "difference_current_minus_paper", "ratio_current_over_paper", "percent_difference"])
        for index, values in enumerate(zip(low, high, current, paper, difference, ratio)):
            writer.writerow([index, *values, 100.0 * values[4] / values[3]])

    centers = 0.5 * (low + high)
    fig, (ax, residual) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.0]}, constrained_layout=True)
    ax.step(low, current, where="post", color="#0072B2", linewidth=2.2, label="current CONUS+ SM: Ge73 + response, effective 119 kg day")
    ax.step(low, paper, where="post", color="#D55E00", linewidth=2.0, linestyle="--", label="paper theory curve: digitized 2501.17843v2")
    ax.set_ylabel("expected events/bin")
    ax.set_title("CONUS+ current result versus paper theory curve")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.2)
    residual.axhline(0.0, color="black", linewidth=0.8)
    residual.step(low, difference, where="post", color="#009E73", linewidth=2.0, label="current − paper")
    residual.fill_between(centers, 0.0, difference, step="mid", alpha=0.15, color="#009E73")
    residual.set_xlabel("reconstructed energy [eVee]")
    residual.set_ylabel("difference")
    residual.grid(alpha=0.2)
    residual.legend(fontsize=9, loc="lower left")
    ax.text(0.02, 0.97, f"Totals: current={current.sum():.6f}; paper={paper.sum():.6f}; Δ={difference.sum():.6f} ({100*difference.sum()/paper.sum():.2f}%)", transform=ax.transAxes, va="top", fontsize=9, bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.7"})
    figdir = OUT / "figures"
    fig.savefig(figdir / "fig_conus_paper_vs_current.pdf", bbox_inches="tight")
    fig.savefig(figdir / "fig_conus_paper_vs_current.png", dpi=320, bbox_inches="tight")
    plt.close(fig)
    print(table_path)


if __name__ == "__main__":
    main()
