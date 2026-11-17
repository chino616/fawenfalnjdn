"""Plot validated, unfitted NSI signal arrays without recomputing physics."""
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
    parser.add_argument("--overwrite", action="store_true", help="Use only after preserving existing figures and manifest")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    validation = json.loads((run/"VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    if validation["status"] != "PASS_DECLARED_NSI_FORWARD_POINTS":
        parser.error("The declared point set must pass numerical validation")
    destination = run/"figures"
    destination.mkdir(exist_ok=args.overwrite)
    with np.load(run/"benchmark.npz", allow_pickle=False) as source:
        data = {key: source[key] for key in source.files}
    index = {name: i for i, name in enumerate(data["point_ids"])}
    counts = data["signal_counts"]
    pe, times = data["pe_edges"], data["time_edges_us"]
    dpe, dt = np.diff(pe), np.diff(times)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "svg.hashsalt": "csi2021_nsi_20261108"})
    styles = [
        ("SM", "SM", "#173e5e", "-"),
        ("mu_cancellation", r"$\epsilon^{uV}_{\mu\mu}=0.2$", "#cb4b16", "-"),
        ("electron_compensation", r"$\epsilon^{uV}_{ee}=-0.12,\ \epsilon^{uV}_{\mu\mu}=0.2$", "#19826e", "--"),
        ("mu_sign_flip", r"$\epsilon^{uV}_{\mu\mu}=0.4$", "#8a50a6", "-."),
        ("d_emu_plus", r"$\epsilon^{dV}_{e\mu}=\epsilon^{dV}_{\mu e}=0.1$", "#b58900", ":"),
    ]
    produced = []

    def save(fig, stem):
        for extension in ("png", "svg"):
            target = destination/(stem+"."+extension)
            fig.savefig(target, dpi=210, facecolor="white",
                metadata={"Date": "2026-11-08", "Creator": "CEvNS-pyEFT unfitted NSI forward benchmark"})
            produced.append({"path": target.relative_to(run).as_posix(), "sha256": sha(target)})
        plt.close(fig)

    footer = ("NSI definition: 2211.11905v2, Sec.2.2 Eqs.(5)-(6). Inputs: 2110.07730v2 ancillary; local Cs/I responses.\n"
        "0-6 us reference-window fluence; reconstructed PE edges; QF restricted to calibration domain. Signal only; no nuisance fit.")
    fig, axes = plt.subplots(2, 2, figsize=(13.1, 8.7), gridspec_kw={"height_ratios": [2.3, 1]}, sharex="col")
    for name, label, color, line in styles:
        row = counts[index[name]]
        for column, (edges, width, projection) in enumerate([(pe, dpe, 1), (times, dt, 0)]):
            y = row.sum(axis=projection)
            baseline = counts[0].sum(axis=projection)
            axes[0, column].stairs(y/width, edges, label=label, color=color, linestyle=line, linewidth=2)
            axes[1, column].stairs(y/baseline, edges, color=color, linestyle=line, linewidth=1.8)
    axes[0, 0].set(ylabel="Signal events / PE", title="PE projection, 0-6 us", ylim=(0, None))
    axes[0, 1].set(ylabel=r"Signal events / $\mu$s", title="Time projection, 0-60 PE", ylim=(0, None))
    axes[1, 0].set(xlabel="Reconstructed photoelectrons (PE)", ylabel="NSI / SM", xlim=(0, 60))
    axes[1, 1].set(xlabel=r"Reconstructed time $t_{rec}$ ($\mu$s)", ylabel="NSI / SM", xlim=(0, 6))
    for axis in axes.ravel():
        axis.grid(axis="y", alpha=.18)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.52, .94), ncol=3, frameon=False, fontsize=11)
    fig.suptitle("CsI2021 vector NSI: unfitted signal versus SM", y=.99, fontsize=18)
    fig.text(.045, .025, footer, fontsize=9, color="#46586a")
    fig.subplots_adjust(left=.075, right=.98, top=.81, bottom=.16, hspace=.13, wspace=.27)
    save(fig, "nsi_sm_projections")

    fig, axes = plt.subplots(3, 4, figsize=(15.4, 10.7))
    for j, axis in enumerate(axes.ravel()[:11]):
        for name, label, color, line in styles:
            axis.stairs(counts[index[name], :, j]/dpe, pe, color=color, linestyle=line, linewidth=1.7)
        axis.set(title=rf"$t_{{rec}}\in[{times[j]:g},{times[j+1]:g})\,\mu s$", xlim=(0,60), ylim=(0,None), xticks=[0,20,40,60])
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
        axis.grid(axis="y", alpha=.16)
        if j%4 == 0: axis.set_ylabel("Signal events / PE")
        if j >= 8: axis.set_xlabel("PE")
    axes.ravel()[11].axis("off")
    axes.ravel()[11].legend(handles, labels, loc="center", frameon=False, fontsize=10)
    fig.suptitle("CsI2021: 11 reconstructed-time windows, signal only", fontsize=18, y=.99)
    fig.text(.055, .018, footer, fontsize=9, color="#46586a")
    fig.subplots_adjust(left=.06, right=.985, top=.92, bottom=.12, hspace=.45, wspace=.34)
    save(fig, "nsi_time_slices")

    names = ["d_emu_plus", "d_etau", "d_mutau", "mixed_ud_emu", "tau_diagonal_control"]
    labels = [r"$d:e\mu=0.1$", r"$d:e\tau=0.1$", r"$d:\mu\tau=0.1$", r"$u:e\mu=0.1$"+"\n"+r"$d:e\mu=-0.05$", r"$u:\tau\tau=0.2$"]
    components = data["target_component_counts"].sum(axis=(1,3,4))
    fig, axis = plt.subplots(figsize=(10.8, 6.2))
    x = np.arange(len(names)); width = .23
    for k, (label, color) in enumerate([(r"prompt $\nu_\mu$", "#cb4b16"), (r"delayed $\nu_e$", "#19826e"), (r"delayed $\bar\nu_\mu$", "#8a50a6")]):
        axis.bar(x+(k-1)*width, [components[index[n],k]-components[0,k] for n in names], width, label=label, color=color)
    axis.set(xticks=x, xticklabels=labels, ylabel=r"$N_{NSI}-N_{SM}$ (signal events)", title="Final-flavor sum retains the incident source timing")
    axis.set_ylim(0,75)
    axis.grid(axis="y", alpha=.18)
    axis.legend(frameon=False, ncol=3, loc="upper center")
    fig.text(.06, .025, footer, fontsize=8.5, color="#46586a")
    fig.subplots_adjust(left=.09, right=.98, top=.88, bottom=.25)
    save(fig, "nsi_flavor_changes")
    manifest = {"date": "2026-11-08", "scope": "Signal-only finite test points; no fit or statistical intervals",
        "input_arrays": {"path": "benchmark.npz", "sha256": sha(run/"benchmark.npz")},
        "configuration": "NSI_CONFIG.json", "column_and_NPZ_provenance": "DATA_DICTIONARY.json",
        "point_definitions": "points.json", "validation_sha256": sha(run/"VALIDATION_RESULTS.json"),
        "plotter_sha256": sha(__file__), "files": produced,
        "densities": "Counts divided by actual PE or time width, not equal-width bins; all curves are derived predictions"}
    (run/"PLOT_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"figures": len(produced), "status": "SAVED"}))


if __name__ == "__main__": main()
