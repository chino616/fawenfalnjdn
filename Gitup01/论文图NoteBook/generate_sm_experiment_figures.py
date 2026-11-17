"""Plot existing SM benchmark arrays, preserving methods and reference roles.

This is a plotting/export consumer, not a new prediction or likelihood runner.
Use --from-snapshot <previous-package>/inputs for a self-contained replot into
a new directory. The first export reads the explicitly selected local runs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, GRAY, GREEN, PURPLE, DARK = (
    "#245b87", "#bc6433", "#8a939b", "#6c9a85", "#987db2", "#17232e")
SETS = {
    "conus": "01_CONUS_Plus", "time": "02_CsI2021_time",
    "csi17": "03_CsI2017", "ar": "04_Ar2020",
    "solar": "05_SolarB8_singlebin", "multi": "06_SolarB8_multibin"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                   allow_nan=False) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def export_csv(path, columns, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def records(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def references():
    return [
        dict(id="R1", citekey="Ackermann2025CONUS", arxiv="2501.05206v3",
             author="N. Ackermann et al. (CONUS+)", year="2025",
             title="Direct observation of coherent elastic antineutrino-nucleus scattering",
             path="docs/references/CONUS/2501.05206v3.pdf",
             locator="Experimental excess spectrum and detector thresholds; experimental source of R2 Fig.1 data"),
        dict(id="R2", citekey="DeRomeri2025CONUS", arxiv="2501.17843v3",
             author="V. De Romeri, D. K. Papoulias and G. Sanchez Garcia", year="2025",
             title="Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering",
             journal="Phys. Rev. D 111, 075025", doi="10.1103/PhysRevD.111.075025",
             path="docs/references/CONUS/2501.17843v3.pdf",
             locator="PDF p10 Fig.1: 19-bin blue SM histogram and black excess points; Eq.(33) and effective 1 kg,119 day convention"),
        dict(id="R3", citekey="Akimov2017CsI", arxiv="1708.01294v1",
             author="D. Akimov et al. (COHERENT)", year="2017",
             title="Observation of Coherent Elastic Neutrino-Nucleus Scattering",
             journal="Science 357, 1123-1126", doi="10.1126/science.aao0990",
             path="docs/references/COHERENT/1708.01294v1.pdf",
             locator="CsI2017 energy spectrum; current COHERENT_*.txt local digitizations retain unresolved extraction provenance"),
        dict(id="R4", citekey="Akimov2022CsI", arxiv="2110.07730v2",
             author="D. Akimov et al. (COHERENT)", year="2022",
             title="Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT",
             journal="Phys. Rev. Lett. 129, 081801", doi="10.1103/PhysRevLett.129.081801",
             path="docs/references/COHERENT/2110.07730v2.pdf",
             locator="PDF/printed p4, right column, Results first paragraph: SM 341 +/- 11(theory) +/- 42(experiment), fitted CEvNS 306 +/- 20 events; left column PE<60, t_rec<6 us; Fig.1 is best-fit residuals, not nominal SM templates"),
        dict(id="R5", citekey="DeRomeri2023COHERENT", arxiv="2211.11905v2",
             author="V. De Romeri et al.", year="2023",
             title="Physics implications of a combined analysis of COHERENT CsI and LAr data",
             journal="JHEP 04 (2023) 035",
             path="docs/references/COHERENT/2211.11905v2.pdf",
             locator="PDF pp12-13 Eqs.(28)-(33); p35 Fig.18: PE/time binning and forward-model comparison"),
        dict(id="R6", citekey="Akimov2021Ar", arxiv="2003.10630v7",
             author="D. Akimov et al. (COHERENT)", year="2021",
             title="First Measurement of Coherent Elastic Neutrino-Nucleus Scattering on Argon",
             journal="Phys. Rev. Lett. 126, 012002", doi="10.1103/PhysRevLett.126.012002",
             path="docs/references/COHERENT/2003.10630v7.pdf",
             locator="CENNS-10 Analysis A measurement; official signal release normalized to initial central-value SM prediction"),
        dict(id="R7", citekey="COHERENT2020ArRelease", arxiv="2006.12659v2",
             author="D. Akimov et al. (COHERENT)", year="2020",
             title="COHERENT Collaboration data release from the first detection of coherent elastic neutrino-nucleus scattering on argon",
             path="docs/references/COHERENT/2006.12659v2.pdf",
             doi="10.5281/zenodo.3903810",
             locator="Release companion sections 2.1/2.2/2.6: cevnspdf.txt energy x F90 x time; expected signal counts, not a unit-normalized PDF"),
        dict(id="R8", citekey="DeRomeri2024Solar", arxiv="2411.11749v1",
             author="V. De Romeri, D. K. Papoulias and C. A. Ternes", year="2024",
             title="Bounds on new neutrino interactions from the first CEvNS data at direct detection experiments",
             path="docs/references/Solar_CEvNS/2411.11749v1.pdf",
             locator="PDF p7 Fig.1: fitted-background stacks and blue S+B prediction; not three-single-bin observable"),
        dict(id="R9", citekey="Bo2024PandaX", arxiv="2407.10892v3",
             author="Z. Bo et al. (PandaX-4T)", year="2024",
             title="First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T",
             path="docs/references/Solar_CEvNS/2407.10892v3.pdf",
             locator="PDF p3 Fig.1 Total(US2) acceptance; p5 Fig.4 charge yield; p6 Fig.5 fitted components"),
        dict(id="R10", citekey="Aprile2024XENONnT", arxiv="2408.02877v2",
             author="E. Aprile et al. (XENONnT)", year="2024",
             title="First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT",
             path="docs/references/Solar_CEvNS/2408.02877v2.pdf",
             locator="Acceptance and SR0/SR1 selection; fitted components used as descriptive background reference"),
        dict(id="R11", citekey="Li2026CEvNS", arxiv="2601.19883v2",
             author="G. Li, C.-Q. Song, F.-J. Tang and J.-H. Yu", year="2026",
             title="Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering",
             path="docs/references/General_CEvNS/2601.19883v2.pdf",
             locator="Solar three-single-bin analysis, Eqs.(87)-(88); Fig.4 joint ee-vector NSI benchmark"),
    ]


def collect_inputs(root, solar_export):
    source_files = {}

    def source(path, role):
        path = Path(path)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        try:
            label = path.relative_to(root).as_posix()
        except ValueError:
            label = str(path)
        source_files[label] = dict(path=str(path), sha256=digest(path), role=role)
        return path

    def js(p, role="existing numerical result"):
        return read_json(source(p, role))

    conus_file = source("outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/sm_counts_19bins.csv", "unchanged 19-bin counts, observed points, digitized reference")
    rows = records(conus_file)
    column = lambda name: np.array([float(row[name]) for row in rows])
    conus = {"edges": np.r_[column("energy_low_eVee"), column("energy_high_eVee")[-1]],
             "signal": column("sm_response_events_per_bin_1kg_119days"),
             "reference": column("paper_sm_digitized_counts_per_kg_per_10eVee"),
             "observed": column("observed_excess_digitized"),
             "error_minus": column("observed_error_minus"), "error_plus": column("observed_error_plus")}
    js("outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json")
    js("data/benchmarks/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/benchmark/conusplus_2501_17843v3_fig1_sm_digitized.provenance.json", "PDF-vector extraction convention")

    with np.load(source("outputs/csi2021_time_sm_20261107/benchmark.npz", "saved nominal SM, three flavors and official observed/control counts"), allow_pickle=False) as z:
        time = {k: z[k].copy() for k in ["pe_edges", "time_edges_us", "target_component_counts", "signal_counts", "C_raw", "AC_raw", "SS_derived", "BRN_raw_template", "NIN_raw_template"]}
    np.testing.assert_allclose(time["target_component_counts"].sum(axis=(0, 1)), time["signal_counts"], atol=1e-12)
    comparison = js("outputs/csi2021_time_sm_data_comparison_20261109/COMPARISON_RECORD.json", "official event sources and background/error-bar conventions")
    for item in comparison["official_event_checks"]:
        p = source(item["path"], "official released event rows; independent histogram verification")
        events = np.loadtxt(p)
        m = (events[:, 0] >= 0) & (events[:, 0] < 60) & (events[:, 1] >= 0) & (events[:, 1] < 6)
        rebuilt = np.histogram2d(events[m, 0], events[m, 1], bins=(time["pe_edges"], time["time_edges_us"]))[0]
        np.testing.assert_array_equal(rebuilt, time[item["array"]])

    c = js("outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json")
    p = Path("data/experiments/COHERENT_CsI/CsI2017/statistics")
    tables = {name: np.loadtxt(source(p / ("COHERENT_" + name + ".txt"), "existing local digitization; original extraction not newly certified")) for name in ["data", "lower", "upper", "spectrum"]}
    source("data/experiments/COHERENT_CsI/CsI2017/README.md", "declared legacy edges: 26 points from 0.001 to 50.0 PE; TXT point abscissae are not shared edges")
    csi17 = dict(edges=np.linspace(.001, 50., 26), signal=np.array(c["counts"]),
                 x=tables["data"][:, 0], observed=tables["data"][:, 1],
                 error_minus=tables["data"][:, 1] - tables["lower"][:, 1],
                 error_plus=tables["upper"][:, 1] - tables["data"][:, 1],
                 reference=tables["spectrum"][:, 1])

    a = js("outputs/paper2601_chi2_corrected_20261111/Ar2020_FORWARD.json")
    a_last = a["runs"][-1]["sm"]
    p = source("data/experiments/COHERENT_Ar/Ar2020/statistics/cevnspdf.txt", "official released initial-CV expected events, 12x8x10; no extra normalization")
    raw = np.loadtxt(io.StringIO(p.read_text().replace("*^", "e")))
    energy = np.unique(raw[:, 0])
    ref = np.array([raw[raw[:, 0] == e, 3].sum() for e in energy])
    assert raw.shape == (960, 4) and abs(ref.sum() - 128.) < 1e-4
    ar = dict(edges=np.arange(.5, 13.5, 1.), signal=np.array(a_last["signal"]),
              reference=ref, official_energy_centers_keVee=energy,
              observed=np.array(a_last["observed"]), background=np.array(a_last["background"]),
              sigma=np.array(a_last["sigma"]),
              grid=np.array(list(a["runs"][-1]["grid"].values())))
    coarse = js("outputs/COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json")
    ar["coarse_signal"] = np.array(coarse["counts"])

    sr = records(source(solar_export / "data/SM_event_predictions.csv", "latest completed section58 delivery; distinct continuous/reference/fitted-signal columns"))
    solar = {k: np.array([float(row[k]) for row in sr]) for k in sr[0] if k != "sample"}
    solar["sample"] = np.array([row["sample"] for row in sr])
    solar_meta = js(solar_export / "data/numerical_results.json", "latest solar statistical result and source identity")
    contour_metrics = js(solar_export / "data/contour_metrics.json", "latest solar method comparison; no new NSI scan in this task")
    js(solar_export / "VALIDATION.json", "delivery validation, not new runtime validation")

    p = source("data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt", "R8 fitted background components and observed counts")
    pandax = np.loadtxt(p)
    p = source("data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt", "R8 fitted backgrounds and observed counts; display bins are not certified common run edges")
    xenon = np.loadtxt(p)
    p = js("outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/RESULT.json")
    x = js("outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/RESULT.json")
    ref = js("outputs/solar_b8_sm/20261109_fig1_comparison/COMPARISON.json", "native PDF blue total S+B staircase, descriptive comparison only")
    multi = dict(p_edges=np.array(p["observable_edges"]), p_signal=np.array(p["counts"]),
                 p_kn=np.array(p["kn_control_counts"]), p_observed=pandax[:, 3],
                 p_cathode=pandax[:, 4], p_md=pandax[:, 5], p_fitted_signal=pandax[:, 6],
                 p_reference_total=np.array(ref["regions"]["PandaX"]["blue_total_signal_plus_background_events_per_bin"]),
                 x_edges=np.array(x["observable_edges"]), x_signal=np.array(x["counts"]),
                 x_kn=np.array(x["kn_control_counts"]), x_observed=xenon[:, 3],
                 x_ac=xenon[:, 4], x_neutron=xenon[:, 5], x_er=xenon[:, 6],
                 x_fitted_signal=xenon[:, 7],
                 x_reference_total=np.array(ref["regions"]["XENONnT"]["blue_total_signal_plus_background_events_per_bin"]))
    refs = references()
    for item in refs:
        item["sha256"] = digest(source(item["path"], "local primary paper; adopted figure/equation locator"))
        item["url"] = "https://arxiv.org/abs/" + item["arxiv"]
    metadata = dict(date="2026-11-13", timezone="Asia/Shanghai", source_files=source_files,
                    references=refs, latest_solar_status=solar_meta["records"],
                    latest_solar_contour_metrics=contour_metrics,
                    ar_grid=a["runs"][-1]["grid"], csI2017_grid=c["record"]["numerics"],
                    mode="Replot saved prediction arrays; no new integration, fit or physics normalization")
    return dict(conus=conus, time=time, csi17=csi17, ar=ar, solar=solar, multi=multi), metadata


def style():
    plt.rcParams.update({"font.family": "DejaVu Serif", "mathtext.fontset": "dejavuserif",
        "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
        "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 8.5,
        "axes.linewidth": .8, "axes.edgecolor": "#3f4c56", "axes.labelcolor": DARK,
        "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True,
        "ytick.right": True, "lines.linewidth": 1.7, "pdf.fonttype": 42,
        "ps.fonttype": 42, "svg.fonttype": "none", "svg.hashsalt": "SM-benchmarks-20261113"})


def poisson(y):
    alpha = 1 - .6827
    low = np.where(y > 0, .5 * chi2.ppf(alpha / 2, 2 * np.maximum(y, 1)), 0.)
    high = .5 * chi2.ppf(1 - alpha / 2, 2 * (y + 1))
    return np.array([y - low, high - y])


def legend_above(fig, ax, ncol=3, y=.99):
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.51, y),
               ncol=ncol, frameon=False, columnspacing=1.5, handlelength=2.4)


def save(fig, folder, name, caption, collection):
    fig.savefig(folder / (name + ".pdf"), bbox_inches="tight", pad_inches=.08,
                metadata={"Title": name, "Creator": "CEvNS-pyEFT SM figure exporter"})
    fig.savefig(folder / (name + ".svg"), bbox_inches="tight", pad_inches=.08)
    fig.savefig(folder / (name + ".png"), dpi=300, bbox_inches="tight", pad_inches=.08)
    collection.savefig(fig, bbox_inches="tight", pad_inches=.08)
    (folder / (name + "_caption.txt")).write_text(caption + "\n", encoding="utf-8")
    plt.close(fig)


def draw_conus(d, folder, book):
    e, s, ref = d["edges"], d["signal"], d["reference"]
    centers = .5 * (e[1:] + e[:-1])
    fig, (ax, ratio) = plt.subplots(2, 1, figsize=(7.1, 5.7), sharex=True,
                                  gridspec_kw={"height_ratios": [3.2, 1], "hspace": .06})
    ax.stairs(s, e, color=BLUE, label="This work: Nuclear Response")
    ax.stairs(ref, e, color=ORANGE, linestyle="--", label="Reference SM [R2], digitized")
    ax.errorbar(centers, d["observed"], yerr=[d["error_minus"], d["error_plus"]],
                fmt="o", color=DARK, ms=3.3, capsize=1.8, lw=.8, label="CONUS+ excess [R1,R2]")
    ax.set(ylabel=r"Counts kg$^{-1}$ (10 eV$_{ee}$)$^{-1}$", xlim=(160, 350))
    ax.set_title("CONUS+: nominal SM energy spectrum", loc="left", pad=8)
    ax.axhline(0, color=GRAY, lw=.7)
    ax.text(.97, .93, "Effective 1 kg detector, 119 days\n" + f"This work: {s.sum():.3f}; reference: {ref.sum():.3f}",
            ha="right", va="top", transform=ax.transAxes, fontsize=8.5)
    ratio.stairs(s / ref, e, color=BLUE)
    ratio.axhline(1, color=ORANGE, ls="--", lw=1)
    ratio.set(xlabel=r"Reconstructed ionization energy (eV$_{ee}$)", ylabel="Work / ref.", ylim=(.35, 1.12))
    ratio.set_yticks([.5, .75, 1.])
    for a in (ax, ratio): a.grid(axis="y", alpha=.12)
    legend_above(fig, ax, ncol=2)
    fig.subplots_adjust(left=.12, right=.98, bottom=.10, top=.82)
    caption = ("CONUS+ nominal SM spectrum in 19 reconstructed-ionization bins for the adopted effective 1 kg,119 day convention. "
        "The Nuclear Response prediction (blue) is compared with the blue SM histogram digitized from De Romeri et al., arXiv:2501.17843v3, PDF p10 Fig.1 [R2] (orange), "
        "and CONUS+ excess points originating from Ackermann et al., arXiv:2501.05206v3 [R1]. The lower panel is the ratio of the two theoretical spectra. "
        "The ordinate sum is an effective-detector comparison, not the three-detector event total. Different flux/nuclear choices remain; no normalization fit or rescaling was applied.")
    save(fig, folder, "Figure_SM_CONUS_Plus", caption, book)
    export_csv(folder / "spectrum.csv", ["low_eVee", "high_eVee", "work_events", "reference_digitized", "observed_excess", "error_minus", "error_plus", "work_over_reference"],
        zip(e[:-1], e[1:], s, ref, d["observed"], d["error_minus"], d["error_plus"], s / ref))


def draw_time(d, folder, book):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.6))
    for a, edges, collapse, xlabel in [(axes[0], d["pe_edges"], 1, "Reconstructed photoelectrons (PE)"),
            (axes[1], d["time_edges_us"], 0, r"Reconstructed time ($\mu$s)")]:
        width = np.diff(edges); center = (edges[1:] + edges[:-1]) / 2
        project = lambda k: d[k].sum(axis=collapse) / width
        ss = project("SS_derived"); neutrons = project("BRN_raw_template") + project("NIN_raw_template")
        a.stairs(ss, edges, fill=True, color=GRAY, alpha=.22, label="Estimated steady-state background")
        a.stairs(neutrons, edges, color=ORANGE, ls=":", label="BRN + NIN, raw templates")
        a.stairs(project("signal_counts"), edges, color=BLUE, label="Nominal SM signal")
        a.stairs(ss + neutrons + project("signal_counts"), edges, color=GREEN, ls="--", label="SM + reference backgrounds (unfitted)")
        obs = d["C_raw"].sum(axis=collapse)
        a.errorbar(center, obs / width, yerr=np.sqrt(obs) / width, xerr=width / 2,
                   fmt="o", color=DARK, ms=3, capsize=1.5, lw=.7, label="Released coincidence data")
        a.set(xlabel=xlabel, xlim=(edges[0], edges[-1]), ylim=(0, None))
        a.grid(axis="y", alpha=.12)
    axes[0].set(ylabel="Events / PE", title="(a) PE projection, 0-6 microseconds")
    axes[1].set(ylabel=r"Events / $\mu$s", title="(b) Time projection, 0-60 PE")
    legend_above(fig, axes[0], ncol=2)
    fig.subplots_adjust(left=.065, right=.985, bottom=.15, top=.72, wspace=.24)
    fig.text(.5, .015, "Nominal SM: 353.466 events. Unfitted backgrounds; released data [R4].", ha="center", fontsize=8.4)
    caption = ("COHERENT CsI2021 PE and time projections of the saved 9x11-bin calculation, compared with the official arXiv:2110.07730v2 ancillary coincidence events [R4]. "
        "The nominal SM signal uses the fixed zero-shift 0-6 microsecond reference-fluence convention; response/binning follow [R4,R5]. Every projection is divided by its actual bin width. "
        "The steady-state estimate and raw BRN/NIN templates are shown without fitted normalization. Vertical bars are sqrt(sum C) counting variation only; "
        "horizontal bars are half-bin widths. This is a forward-model diagnostic, not the published best-fit residual plot or a fit validation.")
    save(fig, folder, "Figure_SM_CsI2021_Raw_Projections", caption, book)

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.6))
    components = d["target_component_counts"].sum(axis=0)
    labels = [r"$\nu_\mu$ CE$\nu$NS", r"$\nu_e$ CE$\nu$NS", r"$\bar\nu_\mu$ CE$\nu$NS", "BRN + NIN, raw"]
    colors = ["#b49a74", "#e8cf78", "#db9b73", PURPLE]
    for a, e, collapse, xlabel in [(axes[0], d["pe_edges"], 1, "Reconstructed photoelectrons (PE)"),
            (axes[1], d["time_edges_us"], 0, r"Reconstructed time ($\mu$s)")]:
        w = np.diff(e); center = (e[1:] + e[:-1]) / 2; base = np.zeros_like(w)
        arrays = [z.sum(axis=collapse) / w for z in components]
        arrays.append((d["BRN_raw_template"] + d["NIN_raw_template"]).sum(axis=collapse) / w)
        for values, label, color in zip(arrays, labels, colors):
            a.stairs(base + values, e, baseline=base, fill=True, color=color, alpha=.85, linewidth=.5, label=label)
            base += values
        a.stairs(base, e, color=DARK, lw=.9)
        residual = (d["C_raw"] - d["SS_derived"]).sum(axis=collapse) / w
        a.plot(center, residual, "o", color=DARK, ms=3.5, label="C - estimated SSB (diagnostic)")
        a.axhline(0, color=GRAY, lw=.7); a.set(xlabel=xlabel, xlim=(e[0], e[-1])); a.grid(axis="y", alpha=.12)
    axes[0].set(ylabel="Events / PE", title="(a) Flavor components in PE")
    axes[1].set(ylabel=r"Events / $\mu$s", title="(b) Flavor components in time")
    legend_above(fig, axes[0], ncol=3)
    fig.subplots_adjust(left=.065, right=.985, bottom=.15, top=.72, wspace=.24)
    fig.text(.5, .015, "Derived residuals; no vertical bars because subtraction covariance is unavailable.", ha="center", fontsize=8.4)
    caption = ("Flavor-resolved nominal CsI2021 CEvNS signal and unchanged raw neutron-background templates. Points are derived C minus the saved steady-state estimate, "
        "not a separately released signal measurement. No vertical error bars are drawn because the background covariance and absolute neutron normalization are unresolved. "
        "The published residual panels in [R4] use fitted backgrounds and therefore have a different meaning. Flavor order is prompt nu_mu, delayed nu_e, delayed antinu_mu; no refit is performed.")
    save(fig, folder, "Figure_SM_CsI2021_Components_Diagnostic", caption, book)
    for tag, e, collapse in [("PE", d["pe_edges"], 1), ("time_us", d["time_edges_us"], 0)]:
        names = ["signal_counts", "C_raw", "AC_raw", "SS_derived", "BRN_raw_template", "NIN_raw_template"]
        vals = [d[k].sum(axis=collapse) for k in names]
        export_csv(folder / (tag + "_projection.csv"), ["low", "high", *names], zip(e[:-1], e[1:], *vals))


def draw_csi17(d, folder, book):
    fig, ax = plt.subplots(figsize=(7.1, 4.8))
    ax.stairs(d["signal"], d["edges"], color=BLUE, label="This work: legacy SM grid")
    ax.stairs(d["reference"], d["edges"], color=ORANGE, ls="--", label="Local reference digitization [R3]")
    ax.errorbar(d["x"], d["observed"], yerr=[d["error_minus"], d["error_plus"]], fmt="o", color=DARK,
                ms=3, capsize=1.7, lw=.7, label="Local residual digitization")
    ax.axhline(0, color=GRAY, lw=.7)
    ax.set(xlabel="Reconstructed photoelectrons (PE)", ylabel="Events / reconstructed bin", xlim=(0, 50),
           title="CsI2017: legacy forward-model comparison")
    ax.grid(axis="y", alpha=.12)
    ax.text(.98, .94, f"Work: {d['signal'].sum():.3f} events\nReference ordinate sum: {d['reference'].sum():.3f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.5)
    legend_above(fig, ax, ncol=2)
    fig.subplots_adjust(left=.11, right=.98, bottom=.13, top=.78)
    caption = ("CsI2017 25-bin legacy SM result, computed previously at the explicitly recorded n_enu=12 regression grid, with the existing local reference spectrum and signed residual/error digitizations associated with [R3]. "
        "The declared 26 edges run from 0.001 to 50.0 PE (width 1.99996 PE); original digitized data-point abscissae are retained, and table rows are compared by order. The current response uses PE=1.17T and a 4.9 PE efficiency threshold. "
        "The external extraction chain and confidence meaning of the digitized lower/upper limits are unresolved; this low-order regression run is not a convergence-certified or official likelihood reproduction. No fit or empirical signal normalization is applied.")
    save(fig, folder, "Figure_SM_CsI2017_Legacy", caption, book)
    export_csv(folder / "spectrum.csv", ["low_PE", "high_PE", "work_events", "reference_local", "digitized_x_PE", "signed_residual", "error_minus", "error_plus"],
        zip(d["edges"][:-1], d["edges"][1:], d["signal"], d["reference"], d["x"], d["observed"], d["error_minus"], d["error_plus"]))


def draw_ar(d, folder, book):
    e, s, ref = d["edges"], d["signal"], d["reference"]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.7))
    axes[0].stairs(s, e, color=BLUE, label="This work: finest saved SM grid")
    axes[0].stairs(ref, e, color=ORANGE, ls="--", label="Released initial-CV SM [R6,R7]")
    axes[0].stairs(d["coarse_signal"], e, color=GRAY, ls=":", label="Earlier regression grid")
    axes[0].set(title="(a) Signal prediction and released template", ylabel="Events / reconstructed bin")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].text(.98, .61, f"Work: {s.sum():.3f} events\nRelease: {ref.sum():.3f} events", transform=axes[0].transAxes,
                 fontsize=8.5, ha="right", va="top")
    axes[1].stairs(d["background"], e, color=GRAY, fill=True, alpha=.22, label="Legacy background")
    axes[1].stairs(s + d["background"], e, color=BLUE, label="SM + legacy background (unfitted)")
    axes[1].errorbar(np.arange(1, 13), d["observed"], yerr=d["sigma"], fmt="o", color=DARK,
                     ms=3, capsize=1.5, lw=.7, label="Legacy points, mean error")
    axes[1].set(title="(b) Legacy analysis-data diagnostic")
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.set(xlabel="Reconstructed bin index", xlim=(.5, 12.5), ylim=(0, None), xticks=[1, 3, 5, 7, 9, 11])
        ax.grid(axis="y", alpha=.12)
    fig.text(.5, .015, "Bin ordering only: the legacy PE / official keVee coordinate mismatch remains unresolved. No fit or rescaling.", ha="center", fontsize=8.4)
    fig.subplots_adjust(left=.065, right=.99, top=.86, bottom=.17, wspace=.22)
    caption = ("Ar2020 nominal SM at the finest saved grid (n_er=321,n_enu=1920,n_pe_bin=64), compared by ordered bin with the released initial-central-value CENNS-10 Analysis A signal template [R6,R7]. "
        "The reference is the sum of cevnspdf.txt over eight F90 and ten time bins for each of twelve energy bins; its total is 128.000005 events and it is not multiplied by another exposure. "
        "The earlier 136.632223-event regression-grid prediction is a separate numerical check. Panel (b) uses the unchanged local legacy observed/background arrays and mean asymmetric errors for display only. "
        "The package labels its coordinate PE whereas the official release is in keVee; because this mismatch and input equivalence are unresolved, axes use bin ordinals, and this figure is not a physical-energy spectrum reproduction claim.")
    save(fig, folder, "Figure_SM_Ar2020_Ordered_Bins", caption, book)
    export_csv(folder / "spectrum.csv", ["bin_index", "official_energy_center_keVee", "work_fine_events", "released_CV_events", "work_regression_events", "legacy_observed", "legacy_background", "legacy_mean_error"],
        zip(np.arange(1, 13), d["official_energy_centers_keVee"], s, ref, d["coarse_signal"], d["observed"], d["background"], d["sigma"]))


def draw_solar(d, folder, book):
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 3.7))
    labels = ["PandaX paired", "PandaX US2", "XENONnT"]
    colors = [BLUE, ORANGE, GRAY]
    methods = ["continuous_acceptance", "reference_matched", "reference_template"]
    display = ["Continuous acceptance", "Reference-aligned independent", "Reference code template"]
    for i, (ax, name) in enumerate(zip(axes, labels)):
        datum, err = d["experiment_fitted_signal"][i], d["experiment_sigma_adopted"][i]
        ax.axhspan(datum - err, datum + err, color="#d7dce0", alpha=.40)
        ax.axhline(datum, color=DARK, ls=":", lw=1)
        for k, (method, color) in enumerate(zip(methods, colors)):
            value = d[method][i]
            ax.plot(k, value, marker=["o", "s", "D"][k], color=color, ms=7, linestyle="none", label=display[k])
            ax.annotate(f"{value:.3f}", (k, value), xytext=(3 if k == 0 else 0, -17 if (i == 2 and k != 0) else 10),
                        textcoords="offset points", fontsize=8, ha="center",
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": .8, "pad": .3})
        ax.errorbar(3, datum, yerr=err, fmt="o", color=DARK, capsize=3, ms=4, label="Experimental fitted signal")
        ax.set(xticks=[0, 1, 2, 3], xticklabels=["Main", "Aligned", "Code", "Fit"],
               xlim=(-.5, 3.55), ylim=(0, (datum + err) * 1.35), title=name)
        ax.grid(axis="y", alpha=.12)
    axes[0].set_ylabel("Signal events")
    legend_above(fig, axes[0], ncol=2)
    fig.subplots_adjust(left=.065, right=.99, top=.73, bottom=.17, wspace=.25)
    fig.text(.5, .02, r"Solar $^{8}$B single-bin benchmark [R9-R11]: theory predictions and measured fitted signal are distinct quantities.", ha="center", fontsize=8.5)
    caption = ("Solar 8B SM signal-event predictions for PandaX paired, PandaX US2 and XENONnT, from the completed 2026-11-13 section58 delivery. "
        "Main is the continuous-acceptance SNuDD/natural-Xe branch with independent pulls; Aligned is an independent Nuclear Response calculation under the old reference recipe; Code is the supplied reference-template calculation. "
        "The black points and gray bands are the experimental fitted signals with the adopted statistical errors, not reference theoretical predictions [R9-R11]. "
        "The old recipe also changes flux, isotope inventory, fixed flavor spectra and acceptance truncation: differences between the three theory series are not attributable solely to acceptance. "
        "In the continuous branch, the unavailable XENONnT acceptance tail is continued flat as an explicit sensitivity assumption. No new source integration or fit was performed in this plotting task.")
    save(fig, folder, "Figure_SM_SolarB8_Singlebin", caption, book)
    export_csv(folder / "event_predictions.csv", ["sample", *methods, "experiment_fitted_signal", "experiment_sigma_adopted"],
        zip(d["sample"], *[d[k] for k in methods], d["experiment_fitted_signal"], d["experiment_sigma_adopted"]))


def draw_multibin(d, folder, book):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.8))
    for ax, tag, backgrounds, labels, colors in [
        (axes[0], "p", ["cathode", "md"], ["Cathode (reference fit)", "MD (reference fit)"], ["#a1bba0", "#e1c97d"]),
        (axes[1], "x", ["ac", "neutron", "er"], ["AC (reference fit)", "Neutron (reference fit)", "ER (reference fit)"], ["#aaa1c4", "#d5bc76", "#80abb8"])]:
        e = d[tag + "_edges"]; base = np.zeros(len(e) - 1)
        for key, label, color in zip(backgrounds, labels, colors):
            v = d[tag + "_" + key]
            ax.stairs(base + v, e, baseline=base, fill=True, color=color, alpha=.78, label=label)
            base += v
        ax.stairs(base + d[tag + "_signal"], e, color=BLUE, label="This work SM + reference B")
        ax.stairs(base + d[tag + "_kn"], e, color=GREEN, ls=":", lw=1.2, label="Matched KN SM + reference B")
        ax.stairs(d[tag + "_reference_total"], e, color=ORANGE, ls="--", label="Paper total S+B [R8], digitized")
        center = .5 * (e[1:] + e[:-1]); obs = d[tag + "_observed"]
        ax.errorbar(center, obs, yerr=poisson(obs), fmt="o", color=DARK, ms=3, capsize=1.5, lw=.7, label="Observed events")
        ax.grid(axis="y", alpha=.12); ax.set(xlim=(e[0], e[-1]), ylim=(0, None))
        ax.legend(frameon=False, fontsize=7.3, loc="upper right")
    axes[0].set(xlabel=r"Mean-mapped electrons $N_e$", ylabel="Events / 0.5-electron bin", title="(a) PandaX US2: nominal response")
    axes[1].set(xlabel="cS2 analysis bin index (SR0 + SR1)", ylabel="Events / analysis bin", title="(b) XENONnT: ordinal comparison", xticks=[.5, 1.5, 2.5], xticklabels=["1", "2", "3"])
    axes[0].set_ylim(0, 115); axes[1].set_ylim(0, 40)
    fig.subplots_adjust(left=.065, right=.99, top=.86, bottom=.17, wspace=.22)
    fig.text(.5, .015, "Separate multi-bin analysis: fixed SSM, no fitted signal rescaling; reference backgrounds are reused only for display.", ha="center", fontsize=8.4)
    caption = ("Separate multi-bin solar 8B SM illustration, corresponding to the observable types in De Romeri et al., arXiv:2411.11749v1, PDF p7 Fig.1 [R8]. "
        "Blue is the saved seven-isotope Nuclear Response SM prediction plus the digitized reference fitted backgrounds; green is the same-input KN control; orange is the native-PDF blue total S+B staircase from [R8]. "
        "No fitted-signal histogram is relabeled as an independent SM prediction and no empirical c_i or 0.65 factor is used. "
        "Left: nominal mean charge-yield mapping, eight 0.5-electron bins; accepted-ROI efficiency does not supply a full independent resolution model. "
        "Right: SR0+SR1 predictions compared by the three ordered analysis bins, not by a newly assumed common S2 edge set; run-specific selection/response alignment is incomplete. "
        "Observed-event bars are central 68.27% Garwood intervals, not model uncertainty. The panels are descriptive forward-model comparisons, not an exact reproduction of the paper fit or the newer single-bin analysis.")
    save(fig, folder, "Figure_SM_SolarB8_Multibin", caption, book)
    for tag, names in [("p", ["signal", "kn", "observed", "cathode", "md", "fitted_signal", "reference_total"]),
                       ("x", ["signal", "kn", "observed", "ac", "neutron", "er", "fitted_signal", "reference_total"])]:
        e = d[tag + "_edges"]
        export_csv(folder / (tag + "_bins.csv"), ["low", "high", *names], zip(e[:-1], e[1:], *[d[tag + "_" + k] for k in names]))


def summary_rows(data):
    rows = []
    def add(name, value, reference, meaning): rows.append([name, float(value), reference, meaning])
    c, t, l, a, s, m = [data[k] for k in ["conus", "time", "csi17", "ar", "solar", "multi"]]
    add("CONUS+ effective detector", c["signal"].sum(), c["reference"].sum(), "Digitized SM [R2]; different nuclear/flux inputs")
    evidence = csi_comparator_evidence()
    add("CsI2021 time, nominal", t["signal_counts"].sum(), evidence["published_SM"]["central_events"],
        "Published SM total [R4], p.4 Results; total-rate benchmark, 99-bin alignment unverified")
    add("CsI2017 legacy grid", l["signal"].sum(), l["reference"].sum(), "Local spectrum digitization [R3]; provenance partial")
    add("Ar2020 finest saved grid", a["signal"].sum(), a["reference"].sum(), "Initial-CV release [R7]; ordered bins, units unresolved")
    for i, sample in enumerate(["PandaX paired, single-bin", "PandaX US2, single-bin", "XENONnT, single-bin"]):
        add(sample, s["continuous_acceptance"][i], s["reference_template"][i], "Continuous main / old reference-code recipe [R11]")
    add("PandaX US2, multi-bin", m["p_signal"].sum(), m["p_kn"].sum(), "Nuclear Response / same-input KN control [R8]")
    add("XENONnT, multi-bin", m["x_signal"].sum(), m["x_kn"].sum(), "Nuclear Response / same-input KN control [R8]")
    return rows


def csi_comparator_evidence():
    path = ROOT / "论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.json"
    record = read_json(path)
    assert digest(record["source"]["pdf"]) == record["source"]["pdf_sha256"], "CsI comparator primary PDF changed"
    assert record["source"]["pdf_page_1based"] == 4
    return record


def draw_table(data, output, book):
    rows = summary_rows(data)
    evidence = csi_comparator_evidence()
    for name in ["CSI2021_COMPARATOR_EVIDENCE.json", "CSI2021_COMPARATOR_EVIDENCE.md"]:
        original = ROOT / "论文图NoteBook/8. SM_experiment_benchmarks" / name
        if original.resolve() != (output / name).resolve(): shutil.copyfile(original, output / name)
    extra_columns = ["reference_theory_uncertainty_events", "reference_experiment_uncertainty_events", "published_fitted_signal_events", "published_fitted_signal_uncertainty_events", "reference_locator", "reference_pdf_sha256"]
    extra = [evidence["published_SM"]["uncertainty_theory_events"], evidence["published_SM"]["uncertainty_experiment_events"], evidence["published_fitted_signal"]["central_events"], evidence["published_fitted_signal"]["uncertainty_events"], evidence["source"]["locator"], evidence["source"]["pdf_sha256"]]
    export_csv(output / "Table_SM_Numerical_Summary.csv", ["analysis", "work_events", "reference_events", "comparison_meaning", *extra_columns],
               [r + (extra if i == 1 else [None] * len(extra_columns)) for i, r in enumerate(rows)])
    fig, ax = plt.subplots(figsize=(7.1, 5.7)); ax.axis("off")
    cells = [[textwrap.fill(n, 21), f"{v:.6f}", f"{ref:.6f}" if isinstance(ref, (float, np.floating)) else ref, textwrap.fill(meaning, 40)] for n, v, ref, meaning in rows]
    cells[1][2] = "341 ± 11 (th)\n± 42 (exp)"
    table = ax.table(cellText=cells, colLabels=["Analysis", "SM events", "Comparator", "Comparator meaning"],
                     cellLoc="left", colLoc="left", colWidths=[.235, .125, .13, .51], loc="center")
    table.auto_set_font_size(False); table.set_fontsize(8.3); table.scale(1, 2.38)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor("#d5dce2"); cell.set_linewidth(.5)
        if i == 0: cell.set_facecolor("#e8eff4"); cell.set_text_props(weight="bold", color=DARK)
        elif i % 2 == 0: cell.set_facecolor("#f6f8fa")
    ax.set_title("SM numerical summary: distinct methods and reference roles", fontsize=13, pad=12)
    footer = "All values are saved nominal predictions. Comparators do not imply identical inputs, response or fit status. CsI2021 [R4, p.4]: SM total 341 ± 11(theory) ± 42(experiment); experimental fitted signal 306 ± 20 is separate."
    fig.text(.03, .02, textwrap.fill(footer, 100), fontsize=8.2, va="bottom")
    fig.subplots_adjust(left=.025, right=.98, top=.89, bottom=.13)
    save(fig, output, "Table_SM_Numerical_Summary", "Nominal SM event totals and explicitly identified reference roles. CsI2021 comparator: D. Akimov et al. (COHERENT), Phys. Rev. Lett. 129, 081801 (2022), arXiv:2110.07730v2, PDF/printed p.4, right-column Results first paragraph: SM 341 +/- 11(theory) +/- 42(experiment) events. The 306 +/- 20 event result is the experimental fitted signal and is not the SM comparator. The local 353.465608686-event prediction is 3.655603720% above the published SM central total; inputs and 99-bin template equivalence remain unverified. Table entries are not a joint statistical sample.", book)
    tex = [r"\begin{tabular}{lrr}", r"\hline", "Analysis & SM events & Comparator " + chr(92) * 2, r"\hline"]
    for i, (n, v, ref, _) in enumerate(rows):
        comp = f"{ref:.6f}" if isinstance(ref, (float, np.floating)) else ref
        if i == 1: comp = r"$341 \pm 11_{\mathrm{th}} \pm 42_{\mathrm{exp}}$"
        tex.append(n.replace("+", r"$+$") + f" & {v:.6f} & {comp} " + r"\\")
    tex += [r"\hline", r"\end{tabular}", r"\par\smallskip{\footnotesize CsI2021 reference: COHERENT, PRL 129, 081801 (2022), arXiv:2110.07730v2, p.~4, Results first paragraph. The SM comparator is $341\pm11_{\rm theory}\pm42_{\rm experiment}$ events. The fitted signal $306\pm20$ events is a separate data result. This is a total-rate comparison; 99-bin template equivalence is unverified.}"]
    (output / "Table_SM_Numerical_Summary.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")


def document(data, metadata, output):
    titles = dict(conus="CONUS+ SM spectrum", time="CsI2021 PE/time projections", csi17="CsI2017 legacy spectrum",
                  ar="Ar2020 released-template comparison", solar="Latest solar single-bin SM", multi="Separate solar multi-bin spectrum")
    files = {}
    for key, foldername in SETS.items():
        folder = output / foldername
        pdfs = sorted(folder.glob("*.pdf"))
        body = ["# " + titles[key], "", "本目录由同一绘图脚本读取已保存数值生成；没有重算物理或重新拟合。", ""]
        for pdf in pdfs:
            stem = pdf.stem
            body += [f"[{stem}.pdf]({stem}.pdf) · [PNG]({stem}.png) · [SVG]({stem}.svg) · [英文图注]({stem}_caption.txt)", ""]
        body += ["CSV保存图中实际数值；原始数值快照在[inputs](../inputs/README.md)。",
                 "[逐项来源及可比性](../REFERENCES_AND_METHODS.md) · [完整图注](../PAPER_CAPTIONS.md) · [图集导航](../README.md)", ""]
        (folder / "README.md").write_text("\n".join(body), encoding="utf-8")
        files[key] = [f"{foldername}/{p.name}" for p in pdfs]
    refs = metadata["references"]
    source_text = ["# 参考文献、实际采用数据与比较边界", "", "## 文献", ""]
    bib = []
    for ref in refs:
        relative = Path(ref["path"])
        import os
        link = Path(os.path.relpath(ROOT / relative, output)).as_posix()
        source_text += [f"**[{ref['id']}] {ref['author']} ({ref['year']}). {ref['title']}.** " +
                        f"{ref.get('journal', '')} [arXiv:{ref['arxiv']}]({ref['url']}) · [本地PDF](<{link}>)。",
                        "定位：" + ref["locator"] + "。", ""]
        fields = dict(author=ref["author"], title=ref["title"], year=ref["year"], eprint=ref["arxiv"], archivePrefix="arXiv")
        if ref.get("journal"): fields["journal"] = ref["journal"]
        if ref.get("doi"): fields["doi"] = ref["doi"]
        bib.append("@article{" + ref["citekey"] + ",\n" + ",\n".join("  " + k + " = {" + v + "}" for k, v in fields.items()) + "\n}")
    source_text += ["## 各图的比较性质", "",
        "- CONUS+：本程序预测与R2原PDF蓝线、R1/R2实验excess分别列出。有效1 kg×119 day的纵坐标和不等于三探测器346/347事例总数；本地149.4194对数字化152.0929，高能尾仍有差异。",
        "- CsI-time：总率Comparator为R4 PDF/页脚第4页右栏Results第一段的341±11(theory)±42(experiment) events；306±20是实验拟合信号，另列。直接原句、选窗、PDF指纹和适用边界见[Comparator证据](CSI2021_COMPARATOR_EVIDENCE.md)。官方C/AC重分箱与背景诊断保留，作者99箱SM模板尚未对齐，BRN/NIN绝对归一及P09未闭合。",
        "- CsI2017：采用当前25箱、n_enu=12兼容回归结果；本地COHERENT_*.txt为既有数字化资料。外部提取链与收敛未认证，不能将它称为已严格复现R3。",
        "- Ar2020：采用已有最细321/1920/64网格139.914559结果，不将136.632223粗网格核对值作为最新精度。官方cevnspdf第4列就是预期事件，960项直接求和128.000005；不归一化为1或再乘曝光。PE/keVee冲突未解，图按箱序比较；legacy点与官方三维观测不混称。",
        "- 太阳单bin：更新至2026-11-13已完成的Section58图表交付。主线continuous_acceptance不采用1%截断；旧参考口径的独立计算与代码模板分别列出。三类理论预测与实验拟合信号不同。旧口径还改变通量、核素和味谱/统计，不能将所有变化只归因于效率。",
        "- 太阳多bin：它是独立旧v3.1谱形分支；固定SSM、真实核Response，对照同输入KN。拟合背景仅用于展示。本图不将经验0.65倍拟合信号当独立SM；XENONnT用分析箱序，避免暗示SR0/SR1具有同一S2边界。",
        "", "## 最新8B约束的更新", "",
        "最新独立交付已完成2图+1表及Slow/Fast范围说明；此任务只引用其已完成数值。Δχ²统一为4.61：continuous_acceptance的Fig.4绿色mask IoU=0.8420325453；参考条件对齐的独立计算为0.9697972038；参考代码模板为0.9948128525。它们是网格/图框内的几何指标，不是复现成功率。主线尚无中间排除缝；旧参考配置可重现缝但宽度不同。", "",
        "本图集未执行新的NSI扫描。原交付的数值/方法信息已作为inputs元数据保存；当前新任务不修改主项目运行时或科学默认值。", "",
        "## 输入身份与重画", "",
        "[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)给出实际采用文件的原路径、角色和SHA256；[inputs/README.md](inputs/README.md)说明本地图表快照。新脚本只作图及导出，不宣称重新通过原运行的科学或回归验收。"]
    (output / "REFERENCES_AND_METHODS.md").write_text("\n".join(source_text) + "\n", encoding="utf-8")
    (output / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")
    captions = ["# 论文图注草稿", "", "以下英文图注与对应图的数据身份一致。图形可排版使用，带诊断或来源缺口的结果须保留其限定。", ""]
    for p in sorted(output.glob("**/*_caption.txt")):
        if p.parent.name == "inputs": continue
        captions += ["## " + p.stem.removesuffix("_caption"), "", p.read_text(encoding="utf-8"), ""]
    (output / "PAPER_CAPTIONS.md").write_text("\n".join(captions), encoding="utf-8")
    rows = ["# 标准模型实验论文图集", "", "2026-11-13。覆盖五条选定实验主线，并将太阳单bin与多bin分开。所有数值来自已执行计算；本轮完成绘图、单位与来源核对、CSV导出和PDF渲染验收，不进行新拟合。", "",
            "[全图PDF](SM_Benchmarks_Collection.pdf) · [数值表PDF](Table_SM_Numerical_Summary.pdf) · [CSV](Table_SM_Numerical_Summary.csv) · [LaTeX表](Table_SM_Numerical_Summary.tex)", "",
            "| 目录 | 内容 |", "|---|---|"]
    rows += [f"| [{foldername}](<{foldername}/README.md>) | {titles[key]} |" for key, foldername in SETS.items()]
    rows += ["", "[参考文献与方法区别](REFERENCES_AND_METHODS.md) · [BibTeX](references.bib) · [英文图注](PAPER_CAPTIONS.md) · [实际输入清单](SOURCE_MANIFEST.json) · [本地数据快照](inputs/README.md)",
             "", "## 已知差异", "",
             "8B连续效率主线、旧参考配置、实验拟合信号分别展示；多bin谱形不替代三样本总数。CsI-time当前是未拟合前向诊断；CsI2017为指定粗网格及本地数字化资料；Ar采用最细已存网格，但PE/keVee问题未解；CONUS+谱形仍不同于数字化论文。不得将图件排版完成写成所有实验精确复现通过。", "",
             "## 重画与归属", "", "生成器：[generate_sm_experiment_figures.py](../generate_sm_experiment_figures.py)。只依赖numpy/scipy/matplotlib；本地快照可在缺少原C盘8B工作目录时重画。", "", "```powershell",
             "& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B '论文图NoteBook/generate_sm_experiment_figures.py' --from-snapshot '论文图NoteBook/8. SM_experiment_benchmarks/inputs' --output-dir '论文图NoteBook/SM_replot_NEW'", "```", "",
             "主目录拥有总表、图注、参考文献、来源清单、验证摘要及合并PDF。各实验README拥有PDF/PNG/SVG、图注和CSV；inputs拥有NPZ/metadata快照；qa拥有PDF渲染与检查。", "",
             "[验证摘要](VALIDATION.json) · [文件变更与归属](FILE_LIFECYCLE.json) · [PDF渲染检查](qa/README.md) · [上一级](../README.md)"]
    (output / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (output / "inputs/README.md").write_text("# 图表数值快照\n\n六个NPZ分别对应conus/time/csi17/ar/solar/multi；只含无pickle数值或字符串数组。metadata.json保留实际源路径、SHA256、文献定位及最新太阳方法对照。它们是本次图表的输入快照，不是新的活动物理dataset。\n\n[源清单](../SOURCE_MANIFEST.json) · [图集](../README.md)\n", encoding="utf-8")
    (output / "qa/README.md").write_text("# 图件核对\n\nrendered_page_*.png为合并PDF的逐页渲染；contact_sheet.png为其阅读检查总览。PDF_QA.json记录页面/字体/边界检查与实际目视情况；DOC_LINK_CHECKS.json记录本次导航链接核对。它们不作为物理计算或完整回归通过证据。\n\n[图集](../README.md)\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--from-snapshot", type=Path)
    parser.add_argument("--refresh-generated", action="store_true", help="Refresh this task's own plot drafts after recording their hashes; requires its WRITE_PLAN.json")
    parser.add_argument("--solar-export", type=Path, default=Path("C:/Users/Ultimator/Documents/Codex/2026-11-13/8b/outputs/section58_solar_b8"))
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.rglob("*.pdf")):
        if not args.refresh_generated or not (output / "WRITE_PLAN.json").is_file():
            parser.error("Output contains existing PDFs; choose a fresh directory to preserve prior runs")
        plan = read_json(output / "WRITE_PLAN.json")
        assert plan["generator"] == Path(__file__).resolve().relative_to(ROOT).as_posix()
        write_json(output / "qa/PLOT_REVISION_before_refresh.json", {
            "reason": "Refine this task's unfinalized plot drafts; scientific source arrays unchanged",
            "previous_plot_files": {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*")
                                    if p.is_file() and p.suffix in {".pdf", ".png", ".svg"}}})
    output.mkdir(parents=True, exist_ok=True)
    for name in ["inputs", "qa", *SETS.values()]: (output / name).mkdir(exist_ok=True)
    if args.from_snapshot:
        snapshot = args.from_snapshot.resolve()
        metadata = read_json(snapshot / "metadata.json")
        data = {}
        for key in SETS:
            with np.load(snapshot / (key + ".npz"), allow_pickle=False) as z:
                data[key] = {k: z[k].copy() for k in z.files}
    else:
        data, metadata = collect_inputs(ROOT, args.solar_export.resolve())
    next(r for r in metadata["references"] if r["id"] == "R4")["locator"] = next(r for r in references() if r["id"] == "R4")["locator"]
    comparator_path = ROOT / "论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.json"
    metadata["source_files"][comparator_path.relative_to(ROOT).as_posix()] = dict(path=str(comparator_path), sha256=digest(comparator_path), role="published CsI2021 SM total comparator, verified on primary PDF p4")
    for key, values in data.items():
        for name, value in values.items():
            if np.issubdtype(value.dtype, np.number):
                assert np.isfinite(value).all(), (key, name)
        np.savez_compressed(output / "inputs" / (key + ".npz"), **values)
    write_json(output / "inputs/metadata.json", metadata)
    write_json(output / "SOURCE_MANIFEST.json", metadata["source_files"])
    style()
    with PdfPages(output / "SM_Benchmarks_Collection.pdf") as book:
        draw_conus(data["conus"], output / SETS["conus"], book)
        draw_time(data["time"], output / SETS["time"], book)
        draw_csi17(data["csi17"], output / SETS["csi17"], book)
        draw_ar(data["ar"], output / SETS["ar"], book)
        draw_solar(data["solar"], output / SETS["solar"], book)
        draw_multibin(data["multi"], output / SETS["multi"], book)
        draw_table(data, output, book)
    document(data, metadata, output)
    if not args.from_snapshot:
        for source in metadata["source_files"].values():
            assert digest(source["path"]) == source["sha256"], source["path"]
    validation = dict(status="PASS_SAVED_ARRAY_EXPORT_CHECKS; PDF_VISUAL_QA_PENDING",
        date="2026-11-13", physics_integrations_this_run=0, fits_this_run=0,
        observed_C_AC_independent_rebin="EXACT_99_BIN_MATCH" if not args.from_snapshot else "uses previously verified snapshot",
        source_files=len(metadata["source_files"]), original_sources_unchanged=True,
        SM_summary=summary_rows(data), runtime_modified=False, input_datasets_modified=False,
        new_physics_acceptance="NOT_CLAIMED", exact_paper_reproduction="NOT_CLAIMED",
        generator=dict(path=str(Path(__file__).resolve()), sha256=digest(__file__)),
        figure_PDFs=9, actual_PDF_files=len(list(output.rglob("*.pdf"))),
        numpy=np.__version__, matplotlib=matplotlib.__version__)
    write_json(output / "VALIDATION.json", validation)
    print(json.dumps({"output": str(output), "pdf_count": validation["actual_PDF_files"], "source_files": len(metadata["source_files"]), "status": validation["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main()
