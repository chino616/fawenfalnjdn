"""Plot saved benchmark arrays; perform no physics calculation or fitting."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    destination = run / "figures"
    if destination.exists() and not args.overwrite:
        parser.error("Figures already exist; use a new directory or --overwrite after reviewing changes")
    destination.mkdir(exist_ok=True)
    validation = json.loads((run / "VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    if validation["status"] != "PASS_SM_FORWARD_NUMERICAL_CHECKS":
        parser.error("Numerical validation must pass before plotting the final benchmark")
    with np.load(run / "benchmark.npz", allow_pickle=False) as source:
        data = {name: source[name] for name in source.files}
    pe = data["pe_edges"]
    times = data["time_edges_us"]
    dpe = np.diff(pe)
    dt = np.diff(times)
    signal = data["signal_counts"]
    flavors = data["target_component_counts"].sum(axis=0)
    total = float(signal.sum())
    labels = [r"$\nu_\mu$ (prompt)", r"$\nu_e$ (delayed)", r"$\bar{\nu}_\mu$ (delayed)"]
    colors = ["#d95f02", "#1b9e77", "#756bb1"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
        "svg.hashsalt": "csi2021_sm_20261107", "axes.titleweight": "bold"})
    produced = []

    def save(fig, name):
        for extension in ("png", "svg"):
            path = destination / (name + "." + extension)
            fig.savefig(path, dpi=220, facecolor="white", metadata={"Date": "2026-11-07", "Creator": "CsI2021 SM benchmark"})
            produced.append({"path": path.relative_to(run).as_posix(), "sha256": sha(path)})
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.1))
    for ic, label in enumerate(labels):
        axes[0].stairs(flavors[ic].sum(axis=1) / dpe, pe, label=label, color=colors[ic], linewidth=1.9)
        axes[1].stairs(flavors[ic].sum(axis=0) / dt, times, label=label, color=colors[ic], linewidth=1.9)
    axes[0].stairs(signal.sum(axis=1) / dpe, pe, label="SM total", color="#17324d", linewidth=2.7)
    axes[1].stairs(signal.sum(axis=0) / dt, times, label="SM total", color="#17324d", linewidth=2.7)
    axes[0].set(xlabel="Reconstructed photoelectrons (PE)", ylabel="Signal events / PE", xlim=(0, 60), ylim=(0, None))
    axes[1].set(xlabel=r"Reconstructed time $t_{rec}$ ($\mu$s)", ylabel=r"Signal events / $\mu$s", xlim=(0, 6), ylim=(0, None))
    axes[0].set_title("PE projection, summed over 0-6 us")
    axes[1].set_title("Time projection, summed over 0-60 PE")
    for axis in axes:
        axis.grid(axis="y", alpha=.18)
    axes[0].legend(frameon=False, fontsize=10)
    fig.suptitle(f"CsI2021 nominal Standard Model signal: {total:.2f} events", fontsize=17, y=.98)
    fig.text(.5, .905, "Local Cs/I nuclear responses | reference-window source normalization | no nuisance fit", ha="center", fontsize=10, color="#4d5b68")
    fig.text(.04, .035, "Inputs: COHERENT 2110.07730v2 ancillary; DAR spectra: 2211.11905v2 Eq.29.\n"
             "QF fit restricted to 2-70 keVnr. PE edges are the declared reconstruction. Full-support fluence result is saved separately.", fontsize=8.5, color="#4d5b68")
    fig.subplots_adjust(left=.075, right=.98, bottom=.20, top=.81, wspace=.26)
    save(fig, "sm_projections")

    fig, axes = plt.subplots(3, 4, figsize=(15.4, 10.8))
    axes = axes.ravel()
    neutron = data["BRN_raw_template"] + data["NIN_raw_template"]
    expected = data["expected_raw_template_diagnostic"]
    for j in range(11):
        axis = axes[j]
        observed = data["C_raw"][:, j]
        axis.errorbar((pe[:-1]+pe[1:])/2, observed/dpe, xerr=dpe/2, yerr=np.sqrt(observed)/dpe,
            fmt="o", markersize=3.7, color="#202a35", capsize=2, elinewidth=.9, zorder=5)
        axis.stairs(signal[:, j]/dpe, pe, color="#2166ac", linewidth=2)
        axis.stairs(data["SS_derived"][:, j]/dpe, pe, color="#8c969e", linewidth=1.6)
        axis.stairs(neutron[:, j]/dpe, pe, color="#b35a36", linestyle="--", linewidth=1.6)
        axis.stairs(expected[:, j]/dpe, pe, color="#202a35", linestyle=":", linewidth=1.8)
        axis.set_title(rf"$t_{{rec}}\in[{times[j]:g},{times[j+1]:g})\,\mu s$", fontsize=11)
        axis.set(xlim=(0, 60), ylim=(0, None), xticks=[0, 20, 40, 60])
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
        axis.grid(axis="y", alpha=.14)
        if j % 4 == 0:
            axis.set_ylabel("Counts / PE")
        if j >= 8:
            axis.set_xlabel("PE")
    axes[11].axis("off")
    handles = [Line2D([], [], marker="o", linestyle="none", color="#202a35", label=r"Raw C data ($\sqrt{C}$ bars)"),
        Line2D([], [], color="#2166ac", linewidth=2, label="Nominal SM signal"),
        Line2D([], [], color="#8c969e", label="SSB from control data"),
        Line2D([], [], color="#b35a36", linestyle="--", label="BRN + NIN: raw templates"),
        Line2D([], [], color="#202a35", linestyle=":", label="SM + raw background diagnostic")]
    axes[11].legend(handles=handles, frameon=False, loc="upper left", fontsize=10, handlelength=2.4)
    axes[11].text(.03, .20, "Background normalization\nis not validated.\nNo best-fit curve is shown.", transform=axes[11].transAxes,
                  fontsize=10, color="#6b5040", va="bottom", linespacing=1.6)
    fig.suptitle("CsI2021 time slices: nominal SM forward calculation", fontsize=18, y=.985)
    fig.text(.5, .95, f"9 PE bins x 11 time intervals | {total:.2f} SM signal events | shapes and raw event data", ha="center", fontsize=11, color="#4d5b68")
    fig.text(.045, .025, "Figure layout follows 2211.11905v2 Fig.18; this is an unfitted project calculation with local nuclear responses.\n"
             "BRN/NIN released tables are used without rescaling to the 18.4/5.6 priors. Counts/PE are not divided by the unequal time-bin widths.", fontsize=9, color="#4d5b68")
    fig.subplots_adjust(left=.06, right=.98, top=.90, bottom=.11, hspace=.40, wspace=.28)
    save(fig, "sm_time_slices")

    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.9))
    values = [signal, data["C_raw"], data["signal_excess_raw_template_diagnostic"]]
    titles = ["Nominal SM signal", "Raw observed C events", "C - SSB - raw BRN/NIN"]
    for index, (axis, array, title) in enumerate(zip(axes, values, titles)):
        if index == 2:
            bound = float(np.max(np.abs(array)))
            image = axis.pcolormesh(times, pe, array, shading="flat", cmap="RdBu_r", vmin=-bound, vmax=bound)
        else:
            image = axis.pcolormesh(times, pe, array, shading="flat", cmap="viridis", vmin=0)
        axis.set(xlabel=r"$t_{rec}$ ($\mu$s)", title=title, xticks=[0, 1, 2, 4, 6], yticks=[0, 8, 16, 24, 40, 60])
        if index == 0:
            axis.set_ylabel("PE")
        fig.colorbar(image, ax=axis, pad=.025, fraction=.05).set_label("Events / bin")
    fig.suptitle("CsI2021: all 99 bins", fontsize=17, y=.985)
    fig.text(.05, .035, "Each color is an event count per PE-time bin, not a density. Unequal PE/time intervals are shown on physical axes.\n"
             "Background-subtracted cells retain negative values; the neutron normalization remains a diagnostic choice.", fontsize=9, color="#4d5b68")
    fig.subplots_adjust(left=.055, right=.975, top=.82, bottom=.21, wspace=.35)
    save(fig, "sm_counts_2d")

    result = {"date": "2026-11-07", "timezone": "Asia/Shanghai", "data_file": "benchmark.npz", "data_sha256": sha(run / "benchmark.npz"),
        "plot_script_sha256": sha(__file__), "matplotlib": matplotlib.__version__, "plots": produced,
        "axes": {"projections": ["events/PE", "events/us"], "time_slices": "events/PE per declared time interval", "heatmap": "events/bin"},
        "fit_performed": False, "background_normalization": "UNRESOLVED_RAW_TEMPLATE_DIAGNOSTIC", "visual_QA": "PENDING"}
    (run / "PLOT_MANIFEST.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"figures": len(produced), "SM_total_events": total, "plot_manifest": str(run / "PLOT_MANIFEST.json")}))


if __name__ == "__main__":
    main()
