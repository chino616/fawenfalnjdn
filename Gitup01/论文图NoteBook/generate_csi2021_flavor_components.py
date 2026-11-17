"""Replot the saved CsI2021 flavor stack with propagated C/AC counting bars.

No prediction, fitting, or experiment-input modification is performed.
The AC control-model shape is fixed, so these are partial statistical errors.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import AutoMinorLocator
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from plotting.paper_theme.plot_template import configure as configure_public_theme, load_theme

NOTEBOOK = ROOT / "论文图NoteBook"
DEFAULT_OUTPUT = NOTEBOOK / "CsI2021_Flavor_Components_v4"
NAME = "Figure_CsI2021_Flavor_Components"
# Stable identities: prompt mu, delayed e, delayed antimu, neutron background.
SERIES_INDICES = (0, 1, 2, 3)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                   allow_nan=False) + "\n", encoding="utf-8")


def load(path):
    with np.load(path, allow_pickle=False) as archive:
        return {key: archive[key].copy() for key in archive.files}


def check_covariance(data, saved):
    """Rebuild the 99-bin and projected covariance, including time correlations."""
    c = data["C_raw"]
    a = saved["AC_0_12us_PE_counts"].astype(float)
    p = saved["SSB_time_probabilities"]
    assert c.shape == (9, 11)
    assert a.sum() == 2242
    assert np.all(c >= 0) and np.all(a >= 0)
    assert np.all(c == np.floor(c)) and np.all(a == np.floor(a))
    k, edges = .0494, data["time_edges_us"]
    p_derived = (np.exp(-k * edges[:-1]) - np.exp(-k * edges[1:])) / (1 - np.exp(-k * 12))
    np.testing.assert_allclose(p, p_derived, rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(data["SS_derived"], a[:, None] * p, rtol=1e-12, atol=1e-12)
    components = data["target_component_counts"].sum(axis=0)
    np.testing.assert_allclose(components.sum(axis=0), data["signal_counts"], atol=1e-12)
    ss_cov = np.kron(np.diag(a), np.outer(p, p))
    residual_cov = np.diag(c.ravel()) + ss_cov
    pe_projector = np.kron(np.eye(len(a)), np.ones((1, len(p))))
    time_projector = np.tile(np.eye(len(p)), (1, len(a)))
    pe_cov = pe_projector @ residual_cov @ pe_projector.T
    time_cov = time_projector @ residual_cov @ time_projector.T
    for key, calculated in [("SSB_covariance", ss_cov),
                            ("residual_C_AC_covariance", residual_cov),
                            ("PE_residual_C_AC_covariance", pe_cov),
                            ("time_residual_C_AC_covariance", time_cov)]:
        np.testing.assert_allclose(calculated, saved[key], rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(calculated, calculated.T, atol=1e-12)
        assert np.linalg.eigvalsh(calculated).min() >= -1e-10
    # Independent analytic marginal checks: do not sum individual time-bin errors.
    np.testing.assert_allclose(np.diag(pe_cov), c.sum(axis=1) + a * p.sum() ** 2)
    np.testing.assert_allclose(np.diag(time_cov), c.sum(axis=0) + a.sum() * p ** 2)
    return components, pe_cov, time_cov


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path,
                        default=NOTEBOOK / "9. SM_uniform_style/inputs/time.npz")
    parser.add_argument("--covariance", type=Path,
                        default=ROOT / "outputs/csi2021_time_sm_data_comparison_20261109/counting_covariance.npz")
    parser.add_argument("--theme", type=Path, default=ROOT / "plotting/paper_theme/PAPER_THEME.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if (output / "PROVENANCE.json").exists() or any((output / (NAME + "." + ext)).exists()
                                                  for ext in ("pdf", "svg", "png")):
        parser.error("Choose a new output directory; existing figure runs are preserved")
    output.mkdir(parents=True, exist_ok=True)
    (output / "inputs").mkdir(exist_ok=True)
    sources = {}
    for source, relative in [(args.snapshot, "inputs/time.npz"),
                             (args.covariance, "inputs/counting_covariance.npz"),
                             (args.theme, "PAPER_THEME.json")]:
        source = source.resolve()
        sources[relative] = {"path": str(source), "sha256": sha(source)}
        target = output / relative
        if source != target.resolve():
            shutil.copyfile(source, target)
        assert sha(target) == sources[relative]["sha256"]
    data, saved = load(output / "inputs/time.npz"), load(output / "inputs/counting_covariance.npz")
    public_theme = load_theme(output / "PAPER_THEME.json")
    theme = public_theme.cfg
    components, pe_cov, time_cov = check_covariance(data, saved)
    configure_public_theme(public_theme)
    color, axes, markers = (theme[k] for k in ("colors", "axes", "markers"))
    layout = theme["layouts"]["double_1x2"]
    fig, panels = plt.subplots(1, 2, figsize=(layout["width_mm"] / 25.4,
                                           layout["height_mm"] / 25.4))
    fig.subplots_adjust(left=.085, right=.985, bottom=.205, top=.745, wspace=.30)
    labels = [r"$\nu_\mu$ CE$\nu$NS", r"$\nu_e$ CE$\nu$NS",
              r"$\bar{\nu}_\mu$ CE$\nu$NS", "BRN + NIN (raw)"]
    colors = [theme["series_palette"][index]["bar_fill"] for index in SERIES_INDICES]
    bar_style = theme["bar_style"]
    formats = []
    error_handle = None
    for axis, edges, collapse, cov, tag, xlabel, ylabel, title in [
        (panels[0], data["pe_edges"], 1, pe_cov, "PE",
         "Reconstructed photoelectrons [PE]", "Events / PE", "(a) Flavor components in PE"),
        (panels[1], data["time_edges_us"], 0, time_cov, "time_us",
         r"Reconstructed time [$\mu\mathrm{s}$]", r"Events / $\mu\mathrm{s}$",
         "(b) Flavor components in time")]:
        width = np.diff(edges)
        center = (edges[:-1] + edges[1:]) / 2
        counts = [v.sum(axis=collapse) for v in components]
        counts.append((data["BRN_raw_template"] + data["NIN_raw_template"]).sum(axis=collapse))
        baseline = np.zeros_like(width)
        for index, (values, label, ink) in enumerate(zip(counts, labels, colors)):
            density = values / width
            axis.stairs(baseline + density, edges, baseline=baseline, fill=True,
                        facecolor=ink, alpha=bar_style["fill_alpha"],
                        edgecolor=bar_style["edge_color"], linewidth=bar_style["edge_pt"])
            baseline += density
        axis.stairs(baseline, edges, color=color[bar_style["total_outline_color"]],
                    linewidth=bar_style["total_outline_pt"])
        raw = data["C_raw"].sum(axis=collapse)
        steady = data["SS_derived"].sum(axis=collapse)
        residual = raw - steady
        sigma = np.sqrt(np.diag(cov))
        error_handle = axis.errorbar(center, residual / width, yerr=sigma / width,
            xerr=width / 2, fmt="o", color=color["ink"], markersize=markers["data_pt"],
            elinewidth=markers["errorbar_pt"], capsize=markers["capsize_pt"],
            capthick=markers["errorbar_pt"], zorder=5)
        axis.axhline(0, color=color["neutral"], linewidth=.65, zorder=1)
        low = min(0, np.min((residual - sigma) / width))
        high = max(np.max(baseline), np.max((residual + sigma) / width))
        pad = .07 * (high - low)
        axis.set(xlabel=xlabel, ylabel=ylabel, xlim=(edges[0], edges[-1]),
                 ylim=(low - pad, high + pad))
        axis.set_title(title, loc="left", pad=6)
        axis.grid(axis="y", color=color["grid"], linewidth=axes["grid_pt"],
                  alpha=axes["grid_alpha"])
        axis.xaxis.set_minor_locator(AutoMinorLocator(2))
        axis.yaxis.set_minor_locator(AutoMinorLocator(2))
        axis.tick_params(which="major", direction="in", top=True, right=True,
                         length=axes["major_tick_length_pt"], width=axes["major_tick_width_pt"])
        axis.tick_params(which="minor", direction="in", top=True, right=True,
                         length=axes["minor_tick_length_pt"], width=axes["minor_tick_width_pt"])
        with (output / (tag + "_projection.csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["low", "high", "nu_mu_events", "nu_e_events", "antinu_mu_events",
                "BRN_NIN_raw_events", "C_events", "SSB_estimate_events", "C_minus_SSB_events",
                "C_AC_stat_sigma_events", "C_minus_SSB_density", "C_AC_stat_sigma_density"])
            writer.writerows(zip(edges[:-1], edges[1:], *counts, raw, steady, residual,
                                  sigma, residual / width, sigma / width))
        assert len(axis.containers) == 1
        assert np.all(np.isfinite(sigma)) and np.all(sigma > 0)
    handles = [Patch(facecolor=ink, alpha=bar_style["fill_alpha"],
                     edgecolor=bar_style["edge_color"], linewidth=bar_style["edge_pt"])
               for ink in colors]
    handles += [Line2D([], [], color=color["ink"], lw=bar_style["total_outline_pt"]), error_handle]
    legend = fig.legend(handles, labels + ["SM + BRN + NIN", r"$C-\widehat{\mathrm{SSB}}$ (stat.)"],
        loc="upper center", bbox_to_anchor=(.52, .99), ncol=3,
        handlelength=theme["legends"]["handle_length"],
        columnspacing=theme["legends"]["column_spacing"],
        handletextpad=theme["legends"]["handle_text_pad"])
    fig.text(.5, .035, "Error bars: C + AC counting statistics only.", ha="center",
             fontsize=theme["typography"]["note_pt"])
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in [*fig.texts, *legend.get_texts(),
                 *(t for axis in panels for t in [axis.title, axis._left_title,
                    axis.xaxis.label, axis.yaxis.label, *axis.get_xticklabels(), *axis.get_yticklabels()])]:
        if not text.get_text() or not text.get_visible():
            continue
        box = text.get_window_extent(renderer)
        assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= fig.bbox.x1 and box.y1 <= fig.bbox.y1, text.get_text()
    assert legend.get_window_extent(renderer).y0 > max(axis.get_tightbbox(renderer).y1 for axis in panels)
    for extension in theme["export"]["formats"]:
        fig.savefig(output / (NAME + "." + extension), dpi=theme["export"]["png_dpi"],
                    bbox_inches=None, facecolor="white")
        formats.append(extension)
    plt.close(fig)
    caption = (
        "Flavor-resolved nominal COHERENT CsI2021 CEvNS prediction projected from the saved "
        "9 PE x 11 time bins over 0-60 PE and 0-6 microseconds, with unchanged raw BRN and NIN "
        "templates. The stack order is prompt nu_mu, delayed nu_e, delayed antinu_mu, then neutron "
        "backgrounds; the dark outline is their sum. Points are C minus the saved smooth steady-state "
        "background estimate, not a separately released signal measurement or the published best-fit "
        "residuals. Vertical bars are symmetric one-standard-deviation plug-in Poisson counting "
        "errors from independent C and AC samples, propagated through the fixed AC-derived SSB "
        "model including its time-bin correlations. With A_i the AC counts in PE bin i over "
        "0-12 microseconds (2242 total), p_j = integral_bin_j exp(-k*t) dt / integral_0^12 "
        "exp(-k*t) dt, k=0.0494/us, SSB_ij=A_i*p_j and "
        "Cov(R_ij,R_kl)=delta_ik*delta_jl*C_ij + delta_ik*A_i*p_j*p_l. "
        "Covariances are projected before taking square roots and dividing by the actual bin "
        "widths. Horizontal bars indicate half-bin widths. The SSB time shape is held fixed; "
        "its shape uncertainty, neutron normalization, and detector/signal systematics are omitted. "
        "No fit or signal/background rescaling is performed. Data: COHERENT, Phys. Rev. Lett. "
        "129, 081801 (2022), arXiv:2110.07730v2 ancillary C/AC event releases; the adopted "
        "control model is recorded under claim C_SS in the local P01 evidence ledger."
    )
    (output / (NAME + "_caption.txt")).write_text(caption + "\n", encoding="utf-8")
    write_json(output / "PROVENANCE.json", {
        "date": "2026-11-15", "timezone": "Asia/Shanghai", "sources": sources,
        "generator": {"path": str(Path(__file__).resolve()), "sha256": sha(__file__)},
        "original_generator": "论文图NoteBook/generate_sm_experiment_figures.py:draw_time",
        "original_style_wrapper": "论文图NoteBook/generate_uniform_sm_figures.py",
        "model_evidence": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P01_EVIDENCE_LEDGER.yaml#C_SS",
        "statistical_definition": caption,
        "flattening_order": "PE major, time minor; C order",
        "series": [{"label": label, "color": ink, "hatch": None, "series_index": index}
                   for label, ink, index in zip(labels, colors, SERIES_INDICES)],
        "theme_version": theme["version"],
        "style_revision": "Canonical user-supplied v4 theme; opaque series fills and white divisions from bar_style",
        "file_lifecycle": {"new_figures_data_and_evidence": "README.md",
            "new_generator": "../README.md", "navigation": "docs/experiments/COHERENT/CsI2021/README.md"},
    })
    write_json(output / "VALIDATION.json", {
        "status": "NUMERICAL_AND_ARTIST_CHECKS_PASS; PDF_RENDER_QA_PENDING",
        "snapshot_copied_byte_identically": True,
        "unchanged_signal_counts_events": float(data["signal_counts"].sum()),
        "C_events": int(data["C_raw"].sum()), "AC_control_0_12us_events": 2242,
        "SSB_events": float(data["SS_derived"].sum()),
        "covariance_rederived_and_matches_saved": True,
        "analytic_projection_diagonal_checks": "PASS",
        "errorbar_points_per_panel": [9, 11], "errors_positive_and_finite": True,
        "text_inside_canvas_and_legend_above_panels": True,
        "width_mm": layout["width_mm"], "height_mm": layout["height_mm"],
        "formats": formats, "png_dpi": theme["export"]["png_dpi"], "tight_crop": False,
        "new_predictions": 0, "new_fits": 0, "runtime_modified": False,
    })
    for relative, source in sources.items():
        assert sha(source["path"]) == source["sha256"]
    print(json.dumps({"output": str(output), "formats": formats,
                      "checks": "PASS", "errorbar_points": [9, 11]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
