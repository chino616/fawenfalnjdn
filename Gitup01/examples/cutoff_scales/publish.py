"""Read-only cutoff figure publisher; 180mm/STIX and separate method identities."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, read, sha, write_json
sys.path.insert(0, str(ROOT))

COLORS = {"CONUS_plus": "#C17B38", "CsI2021_9PE": "#9C89B4", "Ar2020_average": "#87939B",
          "CsI2021_9PE+Ar2020_average": "#215B84", "PandaX_paired": "#80ABB8", "PandaX_US2": "#B49A74",
          "XENONnT": "#9C89B4", "Solar_three_singlebins": "#64947D"}
LABELS = {"CONUS_plus": "CONUS+", "CsI2021_9PE": "CsI (9 energy bins)", "Ar2020_average": "Ar (average errors)",
          "CsI2021_9PE+Ar2020_average": "CsI + Ar (average errors)", "PandaX_paired": "PandaX paired",
          "PandaX_US2": "PandaX US2", "XENONnT": "XENONnT", "Solar_three_singlebins": "Solar three-sample joint"}


def operator_label(key):
    d, i, q = key
    return rf"$\mathcal{{O}}_{{{i}}}^{{{d}{q}}}$"


def style():
    settings = read("论文图NoteBook/9. SM_uniform_style/STYLE.json")
    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9.5,
                         "axes.labelsize": 10, "axes.titlesize": 10, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
                         "legend.fontsize": 8, "axes.linewidth": .65, "axes.edgecolor": "#36444F",
                         "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 300})
    return settings


def chart(record, groups, operators, cl, *, title, branch="global_GeV", compare_branch=False):
    full = len(operators) > 10
    fig, ax = plt.subplots(figsize=(180/25.4, 4.5 if full else 4.15))
    fig.subplots_adjust(left=.095, right=.985, bottom=.235 if full else .20, top=.76)
    index = {(r["analysis_group"], tuple(r["operator_key"])): r for r in record["results"]}
    x = np.arange(len(operators))
    width = .77/(len(groups)*(2 if compare_branch else 1))
    rows, values, no_response = [], [], []
    for group_index, group in enumerate(groups):
        for branch_index, column in enumerate((branch, "sm_connected_GeV") if compare_branch else (branch,)):
            offset = (group_index*(2 if compare_branch else 1)+branch_index-(len(groups)*(2 if compare_branch else 1)-1)/2)*width
            tops = []
            for j, operator in enumerate(operators):
                row = index.get((group, tuple(operator)))
                confidence = {} if row is None else row["confidence"][cl]
                value = confidence.get(column)
                status = "MISSING_FORWARD" if row is None else confidence["status"]
                rows.append({"group": group, "operator": str(tuple(operator)), "CL": cl, "branch": column,
                             "lambda_GeV": value, "status": status, "x": float(x[j]+offset)})
                if value is not None:
                    tops.append((j, value)); values.append(value)
                else:
                    no_response.append((float(x[j]+offset), status))
            if tops:
                positions = np.array([x[j]+offset for j, _ in tops]); heights = np.array([v for _, v in tops])
                ax.bar(positions, heights-.1, bottom=.1, width=width*.92, color=COLORS[group] if branch_index == 0 else "white",
                       edgecolor=COLORS[group], hatch=None if branch_index == 0 else "///", linewidth=.65)
                if not full and not compare_branch:
                    for pos, value in zip(positions, heights):
                        ax.text(pos, value*1.08, f"{value:.3g}", ha="center", va="bottom", fontsize=6.8, rotation=90 if len(groups)>3 else 0)
    ax.set_yscale("log")
    low = .1 if full else (3. if any(v < 100 for v in values) else 100.)
    high = max(values)*3.7
    ax.set_ylim(low, high)
    ax.set_xlim(-.6, len(operators)-.4)
    for pos, status in no_response:
        text = "zero" if status == "NO_SENSITIVITY" else "pending"
        ax.text(pos, low*1.12, text, ha="center", va="bottom", rotation=90, fontsize=6, color="#65757F")
    ax.set_xticks(x, [operator_label(k) for k in operators], rotation=65 if full else 0)
    ax.set_ylabel(r"Effective scale lower bound $\Lambda$ [GeV]")
    ax.grid(axis="y", which="major", color="#D0D8DE", lw=.4, alpha=.65)
    ax.set_axisbelow(True)
    handles = [Patch(facecolor=COLORS[g], edgecolor=COLORS[g], label=LABELS[g]) for g in groups]
    if compare_branch:
        handles += [Patch(facecolor="#576B79", label="Global conservative"), Patch(facecolor="white", edgecolor="#576B79", hatch="///", label="Strict SM-connected")]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.54,.895), ncol=2 if len(handles)>3 else len(handles), frameon=False,
               columnspacing=1.1, handlelength=1.5)
    fig.text(.095, .96, title, ha="left", va="top", fontsize=10.5)
    mode = "Fixed SM propagation control; LNC ee / LNV e-mu transitions" if record["stage"].startswith("FULL22") else "Real ee coefficient; solar propagation updated at every point"
    fig.text(.095, .91, f"{cl}% nominal CL (1 parameter), |g| = 1", fontsize=8)
    fig.text(.095, .06, mode, fontsize=7.5)
    footnote = ("Control only: dim-8 pointwise positivity validation remains unresolved." if record["stage"].startswith("FULL22")
                else "Local-model benchmark. Missing/zero-response entries have no numerical bar.")
    fig.text(.095, .025, footnote, fontsize=7.2, color="#576B79")
    return fig, rows


def publish(results_path, output):
    results_path, output = Path(results_path).resolve(), Path(output).resolve()
    root = (ROOT/"论文图NoteBook/12. Cutoff_Scale_Benchmarks").resolve()
    if output == root or not output.is_relative_to(root):
        raise ValueError("figure output must be a fresh run under the independent cutoff figure directory")
    if output.exists():
        raise FileExistsError("choose a fresh cutoff figure directory")
    record = json.loads((results_path/"RESULTS.json").read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA or record.get("part_id") != PART or record.get("run_id") != results_path.name:
        raise ValueError("wrong Part/schema/run identity")
    for path, expected in record["source_manifest"].items():
        if sha(ROOT/path) != expected:
            raise ValueError("stale numerical source: "+path)
    output.mkdir(parents=True)
    (output/"plot_data").mkdir()
    settings = style()
    full = record["stage"].startswith("FULL22")
    operators = sorted({tuple(r["operator_key"]) for r in record["results"]})
    if full:
        from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
        operators = [s.key for s in LI2026_OPERATOR_SPECS]
    main = ["CONUS_plus", "CsI2021_9PE+Ar2020_average", "Solar_three_singlebins"]
    ground = ["CONUS_plus", "CsI2021_9PE", "Ar2020_average", "CsI2021_9PE+Ar2020_average"]
    solar = ["PandaX_paired", "PandaX_US2", "XENONnT", "Solar_three_singlebins"]
    selections = [("01_Three_groups_90CL", main, operators, "90", "Full22 control: three experiment groups" if full else "dim-6 supported subset: three experiment groups", False),
                  ("02_Ground_90CL", ground, operators, "90", "Ground experiments: full22 control" if full else "Ground experiments: dim-6", False),
                  ("03_Solar_90CL", solar, operators if full else [(6,1,"u"),(6,1,"d")], "90", "Solar samples: fixed-SM control" if full else "Solar samples: self-consistent ee NSI", False),
                  ("04_Branches_90CL", main, [(6,1,"u"),(6,1,"d")], "90", "Disconnected solutions: global and SM-connected", True),
                  ("05_Three_groups_95CL", main, operators, "95", "Three experiment groups: 95% nominal CL", False)]
    figures = []
    with PdfPages(output/"Cutoff_Scales_Collection.pdf") as collection:
        for stem, groups, ops, cl, title, branches in selections:
            fig, rows = chart(record, groups, ops, cl, title=title, compare_branch=branches)
            for extension in ("pdf", "svg", "png"):
                fig.savefig(output/(stem+"."+extension), dpi=300)
            collection.savefig(fig)
            plt.close(fig)
            with (output/"plot_data"/(stem+".csv")).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            figures.append(stem)
    provenance = {"part_id": PART, "schema": "cutoff_figure_manifest/1", "result_path": str(results_path),
                  "result_sha256": sha(results_path/"RESULTS.json"), "run_id": record["run_id"], "stage": record["stage"],
                  "publisher_sha256": sha(HERE/"publish.py"), "style_source": "论文图NoteBook/9. SM_uniform_style/STYLE.json",
                  "style_sha256": sha(ROOT/"论文图NoteBook/9. SM_uniform_style/STYLE.json"), "width_mm":180,
                  "figures": figures, "comparison_claim": "paper-like display; local results are not author-equivalent limits"}
    write_json(output/"FIGURE_MANIFEST.json", provenance)
    caption = ("Each operator is switched on individually, with the dimensionless coefficient magnitude set to unity. "
               "Bounds are inferred from the full signed one-parameter confidence set, with nuisance parameters profiled. "
               "The global bars retain disconnected solutions; the SM-connected bars require an interval that actually contains zero. "
               "No bar is assigned to a missing forward model or a zero-response direction. "
               "CsI denotes the nine-bin energy likelihood and Ar uses average Gaussian errors. "
               + ("The full22 solar calculation is a fixed-SM-propagation control with LNC ee and explicitly defined LNV e-mu transitions. Dim-8 pointwise positivity validation is unresolved; one native CONUS mixed-amplitude holdout is rejected and retained in the validation record. These bars are nominal control outputs, not accepted physical exclusions for that operator family. " if full
                  else "Solar ee vector propagation is recomputed at every coefficient using the adopted SNuDD v3.4.1 model. ")
               + "XENONnT retains the adopted flat-sensitivity tail. These are local-model benchmarks, not official-likelihood or author-equivalent limits.")
    (output/"CAPTIONS.txt").write_text(caption+"\n", encoding="utf-8")
    links = "\n".join(f"- [{stem} PDF]({stem}.pdf) · [SVG]({stem}.svg) · [PNG]({stem}.png) · [数据](plot_data/{stem}.csv)" for stem in figures)
    (output/"README.md").write_text("# 截断能标独立图集\n\n"
        f"运行：{record['run_id']}；阶段：{record['stage']}。\n\n"
        "[五页PDF合集](Cutoff_Scales_Collection.pdf) · [来源与样式](FIGURE_MANIFEST.json) · [英文图注](CAPTIONS.txt)\n\n"
        +links+"\n\n缺失项和零响应项单独标记。global与SM-connected分支、90%与95%名义阈值分别展示。"
        "完整系数/能标允许集由对应数值结果保存；一根柱高不表示高于它的每个能标都被允许。\n", encoding="utf-8")
    print("PUBLISHED", output, "PDFs", len(figures)+1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    publish(args.results, args.output)
