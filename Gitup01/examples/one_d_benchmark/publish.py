"""Publish verified 1D inference, reference comparisons and workflow routes."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT/"论文图NoteBook/9. SM_uniform_style"))
from publication_style import configure, export, finalize, load_style, new_figure
from prediction_routes import read, sha
from run_analysis import write

SHORT = {"CsI2021": "CsI2021 (9 PE bins)", "Ar2020": "Ar2020 (mean errors)",
         "COHERENT_CsI_Ar_mean_errors": "CsI + Ar (mean errors)", "CONUS_plus": "CONUS+",
         "PandaX_paired": "PandaX paired", "PandaX_US2": "PandaX US2", "XENONnT": "XENONnT", "Solar_joint": "Solar joint"}
COLORS = {"CsI2021": "#215B84", "Ar2020": "#64947D", "COHERENT_CsI_Ar_mean_errors": "#182530", "CONUS_plus": "#5C82A3",
          "PandaX_paired": "#87939B", "PandaX_US2": "#64947D", "XENONnT": "#215B84", "Solar_joint": "#9C89B4"}
LINESTYLES = {"CsI2021": "--", "Ar2020": "-.", "COHERENT_CsI_Ar_mean_errors": "-", "CONUS_plus": ":",
              "PandaX_paired": "--", "PandaX_US2": "-.", "XENONnT": ":", "Solar_joint": "-"}


def intervals_text(intervals, digits=6):
    return " ∪ ".join("(−∞, +∞)" if a is None else f"[{a:.{digits}f}, {b:.{digits}f}]" for a, b in intervals)


def relative_link(path, owner):
    return Path(os.path.relpath(path, owner)).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    parser.add_argument("--refresh-draft", action="store_true")
    args = parser.parse_args()
    out, figdir = args.results.resolve(), args.figures.resolve()
    if any(figdir.glob("*.pdf")) and not args.refresh_draft: raise FileExistsError("Choose a new figure directory")
    figdir.mkdir(parents=True, exist_ok=True); (figdir/"qa").mkdir(exist_ok=True)
    result = read(out/"RESULTS.json"); refs = read(out/"REFERENCE_COMPARISON.json")
    validation = read(out/"qa/INDEPENDENT_CHECKS.json")
    style = load_style()
    style["layouts"]["six_panel"] = {"height_in": 7.6, "axes_rects": [[x, y, .385, .175] for y in [.625, .365, .105] for x in [.095, .59]]}
    style["layouts"]["four_panel"] = {"height_in": 5.8, "axes_rects": [[x, y, .385, .24] for y in [.49, .135] for x in [.095, .59]]}
    style["statistical_series_colors"] = COLORS
    style["statistical_series_linestyles"] = LINESTYLES
    style["statistical_color_note"] = "All colored curves are newly evaluated local models, explicitly named by experiment; orange reserved for literature interval markers. No fabricated author chi2 curve is plotted."
    write(figdir/"STYLE.json", style)
    c = configure(style)
    outputs = []
    captions = []

    def curve(ax, analysis, parameter, label=None):
        key = analysis+"__"+parameter
        with np.load(out/"scans"/(key+".npz"), allow_pickle=False) as z:
            ax.plot(z["grid"], z["delta_chi2"], color=COLORS[analysis], linestyle=LINESTYLES[analysis],
                    lw=1.7 if analysis.endswith("joint") or analysis.startswith("COHERENT_") else 1.4,
                    label=label or SHORT[analysis])

    def threshold(ax):
        for level, pattern in [(1., ":"), (2.71, "--"), (3.84, "-.")]:
            ax.axhline(level, color="#ADB7BE", lw=.6, ls=pattern, zorder=0)
        ax.set_ylim(0, 8)
        ax.set_ylabel(r"$\Delta\chi^2$ (1 parameter)")

    def finish(fig, name, layout, titles, note, caption, book):
        finalize(fig, layout, titles=titles, note=note, style=style)
        # Only newly computed curves appear in legend; reference bounds use orange.
        export(fig, figdir/name, style)
        book.savefig(fig, bbox_inches=None, facecolor="white")
        plt.close(fig)
        (figdir/(name+"_caption.txt")).write_text(caption+"\n", encoding="utf-8")
        outputs.append(name); captions.append((name, caption))

    terrestrial = ["CsI2021", "Ar2020", "CONUS_plus", "COHERENT_CsI_Ar_mean_errors"]
    solar = ["PandaX_paired", "PandaX_US2", "XENONnT", "Solar_joint"]
    with PdfPages(figdir/"OneD_Chi2_Collection.pdf") as book:
        fig, ax = new_figure("two_panel", style)
        for a, names in zip(ax, [terrestrial, solar]):
            for name in names: curve(a, name, "sin2thetaW")
            threshold(a); a.set(xlabel=r"$\sin^2\theta_W$", xlim=(.04, .52))
        finish(fig, "Figure_1_SM_Weak_Mixing_Angle", "two_panel", ["(a) Terrestrial CEvNS", "(b) Solar three-singlebin analyses"],
               "Horizontal guides: delta chi-square = 1, 2.71, 3.84; fixed reference fluxes.",
               "One-parameter weak-mixing-angle profiles computed from the full vector/axial response kernels at fixed flux. Panel (a) uses the saved CsI2021 nine-bin, Ar2020 mean-error and CONUS+ Gaussian models; the CsI+Ar curve has independent nuisance parameters. Panel (b) uses three fitted-signal single bins and independent 12% normalization pulls, with the explicitly flat-continued XENON acceptance tail. Each curve subtracts its own continuous 1D minimum. These are local-model approximations, not the timing likelihood in arXiv:2211.11905 or the multibin likelihood in arXiv:2411.11749.", book)

        fig, ax = new_figure("two_panel", style)
        for a, parameter in zip(ax, ["fB_data_only", "fB_existing_pulls_control"]):
            for name in solar: curve(a, name, parameter)
            threshold(a); a.set(xlabel=r"$f_B=\Phi_{^8B}/(5.46\times10^6\,{\rm cm}^{-2}{\rm s}^{-1})$", xlim=(0, 3.4))
        finish(fig, "Figure_2_SM_Solar_Flux", "two_panel", ["(a) Free flux, data-only errors", "(b) Existing 12% pulls retained"],
               "The two panels have different normalization-prior definitions; they are not two algorithms for one likelihood.",
               "Solar flux profiles at fixed sin2thetaW=0.23857. In panel (a), fB is the free source normalization and no solar-model normalization prior or additional 12% pull is applied; the fitted signal-yield Gaussian errors are retained. Panel (b) is an explicitly labelled sensitivity retaining the existing independent 12% rate-normalization pulls while varying fB. Neither panel is the published multibin flux likelihood of arXiv:2411.11749. The Gaussian data-only solution is independently checked analytically.", book)

        fig, ax = new_figure("two_panel", style)
        for a, quark in zip(ax, ["u", "d"]):
            for name in [*terrestrial, "Solar_joint"]: curve(a, name, "epsilon_ee_"+quark+"V")
            threshold(a); a.set(xlabel=r"$\epsilon_{ee}^{"+quark+r"V}$", xlim=(-.25, .65))
        finish(fig, "Figure_3_NSI_Electron_Flavor_Comparison", "two_panel", [r"(a) $\epsilon_{ee}^{uV}$", r"(b) $\epsilon_{ee}^{dV}$"],
               "One real NSI coordinate at a time; all other NSI coordinates are fixed to zero.",
               "Electron-flavor vector NSI profiles for individual experiments and the explicitly defined CsI2021+Ar group. One real coordinate is varied, the other NSI coordinates vanish, and nuisance parameters are profiled. Solar matter propagation is recomputed at every NSI point; terrestrial incoming states are fixed. The comparison uses Delta chi2=1,2.71,3.84 for a declared one-parameter benchmark, not the 4.61 threshold or minimum of a 2D u/d plane. All disconnected allowed branches are preserved in the numerical interval tables.", book)

        fig, ax = new_figure("six_panel", style)
        titles = []
        for a, (flavor, quark) in zip(ax, [(f, q) for f in ["ee", "mumu", "emu"] for q in ["u", "d"]]):
            for name in ["CsI2021", "Ar2020", "COHERENT_CsI_Ar_mean_errors"]: curve(a, name, "epsilon_"+flavor+"_"+quark+"V")
            ftex = {"ee": "ee", "mumu": r"\mu\mu", "emu": r"e\mu"}[flavor]
            threshold(a); a.set(xlabel=r"$\epsilon_{"+ftex+r"}^{"+quark+r"V}$", xlim=(-.24, .65) if flavor != "emu" else (-.31, .31))
            titles.append(r"$\epsilon_{"+ftex+r"}^{"+quark+r"V}$")
        finish(fig, "Figure_4_NSI_COHERENT_Flavors", "six_panel", titles,
               "Energy-only Gaussian benchmark; the Ar errors are averaged, not the separate asymmetric model.",
               "Six terrestrial one-coordinate profiles for ee, mumu and real emu uV/dV, using fixed-state full operator kernels and independent Gaussian signal/background pulls. The muon-flavor changes affect prompt nu_mu and delayed antinu_mu components; real flavor-changing profiles are sign symmetric. These plots do not use the overlapping CsI2021 99-bin time sample or add CsI2017. The unresolved PE/keVee Ar convention remains part of the local model.", book)

        fig, ax = new_figure("six_panel", style)
        titles = []
        for a, (flavor, quark) in zip(ax, [(f, q) for f in ["ee", "emu", "etau"] for q in ["u", "d"]]):
            par = "epsilon_"+flavor+"_"+quark+"V"
            curve(a, "CONUS_plus", par, label="This calculation")
            for j, row in enumerate(next(r for r in refs["CONUS_NSI"] if r["parameter"] == par)["paper_TableII_1sigma"]):
                a.hlines(1., row[0], row[1], colors=c["reference"], linewidth=3, label="Published 1-sigma interval" if j == 0 else "_nolegend_")
            threshold(a)
            a.set(xlim=(-.12, .47) if flavor == "ee" else (-.25, .25), xlabel=r"$\epsilon_{"+{"ee":"ee", "emu":r"e\mu", "etau":r"e\tau"}[flavor]+r"}^{"+quark+r"V}$")
            titles.append(r"$\epsilon_{"+{"ee":"ee", "emu":r"e\mu", "etau":r"e\tau"}[flavor]+r"}^{"+quark+r"V}$")
        finish(fig, "Figure_5_NSI_CONUS_Paper_Intervals", "six_panel", titles,
               "Orange segments are published intervals at delta chi-square = 1; they are not digitized chi-square curves.",
               "CONUS+ real ee, emu and etau one-coordinate vector NSI profiles from the saved Nuclear Response kernel, with a profiled 16.9% Gaussian rate pull. Orange segments reproduce the rounded 1-sigma endpoints of arXiv:2501.17843v3, PDF p13 Table II; the original author chi2 grids are unavailable and no reference profile has been fabricated. The table of endpoint differences quantifies the numerical agreement without certifying full flux/nuclear equivalence.", book)

        fig, ax = new_figure("two_panel", style)
        for a, quark in zip(ax, ["u", "d"]):
            for name in solar: curve(a, name, "epsilon_ee_"+quark+"V")
            threshold(a); a.set(xlabel=r"$\epsilon_{ee}^{"+quark+r"V}$", xlim=(-.45, .88))
        finish(fig, "Figure_6_NSI_Solar_Individual_And_Joint", "two_panel", [r"(a) Solar $\epsilon_{ee}^{uV}$", r"(b) Solar $\epsilon_{ee}^{dV}$"],
               "Continuous acceptance; SNuDD propagation varies with NSI. The XENON tail uses explicit flat continuation.",
               "Solar single-parameter ee-vector NSI profiles for PandaX paired, PandaX US2, XENONnT and the three-sample joint objective. SNuDD's declared effective two-flavor adiabatic matter propagation is evaluated at each scanned point; it is not a fixed-probability polynomial in epsilon. The rate fold uses the existing seven-isotope Nuclear Response and continuous efficiency, with explicit XENON tail flat sensitivity. All curves subtract their own 1D minimum, distinct from the remote two-parameter joint minimum previously found in Fig.4 analysis.", book)

        fig, ax = new_figure("four_panel", style)
        titles = []
        for a, (flavor, quark) in zip(ax, [(f, q) for f in ["etau", "mutau"] for q in ["u", "d"]]):
            for name in ["CsI2021", "Ar2020", "COHERENT_CsI_Ar_mean_errors"]: curve(a, name, "epsilon_"+flavor+"_"+quark+"V")
            tex = r"e\tau" if flavor == "etau" else r"\mu\tau"
            threshold(a); a.set(xlabel=r"$\epsilon_{"+tex+r"}^{"+quark+r"V}$", xlim=(-.55, .55))
            titles.append(r"$\epsilon_{"+tex+r"}^{"+quark+r"V}$")
        finish(fig, "Figure_7_NSI_Tau_Final_State", "four_panel", titles,
               "Tau final states can contribute. Tau-diagonal parameters are unidentifiable for these incoming SNS states.",
               "Additional real flavor-changing etau and mutau profiles in the fixed-state terrestrial benchmark. These transitions can produce an unobserved tau final state even though the SNS source has no tau-flavor incoming population. Pure tau-diagonal coordinates instead give flat likelihoods in this source model; their intervals are correctly reported as unbounded, not as the finite displayed scan range.", book)

    # Export actual values behind all curves, including profiles not pictured.
    (figdir/"data").mkdir(exist_ok=True)
    for file in ["INTERVALS.csv", "RESULTS.json", "REFERENCE_COMPARISON.json", "ROUTE_AUDIT.json", "ROUTE_STEPS.csv"]:
        shutil.copyfile(out/file, figdir/"data"/file)
    for key in result["scans"]:
        with np.load(out/"scans"/(key+".npz"), allow_pickle=False) as z:
            file = figdir/"data"/(key+".csv")
            with file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f); writer.writerow(["parameter_value", "profiled_chi2", "delta_chi2_own_1d_minimum"])
                writer.writerows(zip(z["grid"], z["chi2"], z["delta_chi2"]))
    caption_doc = ["# 一维χ²论文图注", "", "所有图均保留approximate local-model benchmark含义；1、2.71、3.84为声明的1参数阈值，未通过toy MC认证非正则/边界情形的实际覆盖率。", ""]
    for name, caption in captions: caption_doc += ["## "+name, "", caption, ""]
    (figdir/"PAPER_CAPTIONS.md").write_text("\n".join(caption_doc)+"\n", encoding="utf-8")
    # Complete result tables, no silent omission of flat or unavailable routes.
    lines = ["# 一维SM参数与矢量NSI χ²结果", "", "2026-11-13。此报告是现有本地模型的独立一维benchmark；不修改Runtime、data、正式工作流Gate或历史结果。", "",
        f"完成{len(result['scans'])}条参数路线，其中6条tau对角路线在SNS入射态下无敏感度；对应置信集为全实轴。其余路线给出连续最小值和所有分离区间。", "",
        "## SM点与统计输入", "", "| 分析 | SM信号/events | profiled χ² |", "|---|---:|---:|"]
    for name, s in result["SM_points"].items():
        ev = s.get("events", "—"); ev = "/".join(f"{x:.6f}" for x in ev) if isinstance(ev, list) else f"{ev:.6f}" if isinstance(ev, (float, int)) else ev
        lines.append(f"| {name} | {ev} | {s['chi2']:.9f} |")
    groups = {"SM弱混合角": lambda s: s["parameter"] == "sin2thetaW",
              "太阳自由通量：不额外施加12%归一化先验": lambda s: s["parameter"] == "fB_data_only",
              "太阳通量对照：保留既有三个独立12% pull": lambda s: s["parameter"] == "fB_existing_pulls_control",
              "NSI单参数：其他NSI固定为零": lambda s: s["parameter"].startswith("epsilon_")}
    for title, choose in groups.items():
        lines += ["", "## "+title, "", "| 分析 | 参数 | 最佳值 | χ²min | 68%阈值区间 | 90%阈值区间 | 95%阈值区间 |", "|---|---|---:|---:|---|---|---|"]
        for s in result["scans"].values():
            if not choose(s): continue
            minima = s.get("degenerate_minima", [])
            best = "不可辨识" if s["best_fit"] is None else ", ".join(f"{m['value']:.7f}" for m in minima) if minima else f"{s['best_fit']:.7f}"
            lines.append(f"| {s['analysis']} | {s['parameter']} | {best} | {s['chi2_min']:.9f} | "+" | ".join(intervals_text(s["intervals"][k]) for k in ["68percent", "90percent", "95percent"])+" |")
    f = result["scans"]["Solar_joint__fB_data_only"]
    lines += ["", "最佳值栏列出数值上简并的所有一维全局极小点；χ²min为该条曲线自己的连续最小值。CSV中的best_fit为其中一个代表点，完整简并结构以RESULTS.json及本表为准。", "",
        f"太阳联合自由通量：Φ=5.46×10⁶fB，最佳值为{5.46*f['best_fit']:.6f}×10⁶ cm⁻²s⁻¹；68%阈值区间为"+intervals_text([[5.46*a, 5.46*b] for a, b in f["intervals"]["68percent"]])+"×10⁶。", "",
        "## 外部与历史benchmark", "", "CONUS+弱角：论文2501.17843v3 PDF p11 Eq.(34)为0.247±0.052；本次最佳值"+f"{refs['CONUS_weak_angle']['own_best']:.8f}"+"，68%区间"+intervals_text(refs["CONUS_weak_angle"]["own_68percent"])+"。原模型核表/通量差异仍保留。", "",
        "| CONUS参数 | 本次68%区间 | 论文TableII的1σ区间 | 最大端点差 |", "|---|---|---|---:|"]
    for row in refs["CONUS_NSI"]:
        lines.append(f"| {row['parameter']} | {intervals_text(row['own_68percent'])} | {intervals_text(row['paper_TableII_1sigma'])} | {row['max_endpoint_difference']:.8f} |")
    lines += ["", "2211.11905v2 Eq.(41)的COHERENT弱角0.237±0.029来自含时间/形状误差的统计；本次均误差能量Gaussian不是相同likelihood。2411.11749v1 Eqs.(18)–(23)及Fig.2是太阳多bin结果，不与本次三单bin置信宽度作同输入精度验收。没有作者χ²数值网格时不伪造参考曲线。", "",
        "八条既有ee-uV/dV一维最小值本轮重新计算并与此前保存的同目标函数结果一致；2D漏搜修复不替代本轮1D基准。", "",
        "## 验证范围", "", "- 66条曲线的阈值根逐一回代；分离区间、局部/简并最小值、搜索域证明均保存。",
        "- 自由fB的四条路线与独立解析加权最小二乘估计核对。",
        "- 15个新代表点full/pair逐通道对照，18个新弱角原始核截面逐能量对照；固定态二次式均有独立点核对。",
        "- CsI/Ar公开loader因OS问题未重新运行；保存核回放通过不写成正式Package可读或最终网格原生Slow新跑通过。",
        "- 没有运行覆盖率toy MC；非对角NSI在0处的非正则性、物理边界和有限观测导致的渐近限制均保留，不给未经校准的显著性。", "",
        "## 不能生成的能力", ""]
    lines += ["- **"+name+"**："+reason for name, reason in result["not_run"].items()]
    lines += ["", "[逐步代码路线](ROUTE_SUMMARY.md) · [全部数值](RESULTS.json) · [区间CSV](INTERVALS.csv) · [统计合同](STATISTICS_CONTRACT.md) · [独立核验](qa/INDEPENDENT_CHECKS.json)"]
    (out/"RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    contract = r"""# 一维统计与推断合同

本轮继承已选择的本地近似统计，正式数据、先验和Runtime未改。用户明确请求弱角、太阳通量与NSI扫描；自由通量的去先验定义作为本轮独立分析模型，不替换生产模型，结果接受仍NOT_REVIEWED。

## 实际通道与数据语义

| 通道 | representation/processing/design | 观测 | 本轮统计 | 需要外部协方差？ |
|---|---|---|---|---|
| CsI2021九箱 | binned_counts / legacy residual / single_sample | 保存benchmark的D、B、σ；源数组counts/PE已整体乘箱宽一次 | Gaussian；信号.125、背景.35独立全箱相关pull | 已选对角近似不需要；官方似然等价未确认 |
| Ar2020十二箱 | binned_counts / legacy analysis arrays / single_sample | 保存D、B与上下误差的均值σ | Gaussian；信号.12、背景.146独立pull，保留为mean-error方法 | 本近似不需要；未替代原非对称模型 |
| CONUS+十九箱 | binned_counts effective normalization / signed excess / single_sample | 原PDF数字化D与平均上下误差σ | Gaussian；.169全箱信号pull | 本近似不需要；不宣称author原始数组 |
| 太阳三单bin | three fitted signal yields / fit-derived / joint | D=[3.5,75,10.7]，σ=[1.2985,27.975,3.9483] events | Gaussian；弱角/NSI使用独立.12 pull | 按2601 Eq88独立近似；不是raw Poisson |
| CsI-time99箱 | raw/on-off event arrays | C/AC及背景候选齐备 | P09未闭合，NOT_RUN | 所需项由待定统计合同决定，不能自动编造 |

实际三条地面输入快照见inputs/*_fixed_model.npz，源头为SOURCE_MANIFEST.json中的既有最终网格与SUMMARY。太阳实际输入是data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json；对应2+1样本使用同一传播/能量轴，XENON缺尾段显式flat_sensitivity。

## 公式

地面模型为

$$\chi^2(\theta,\alpha,\beta)=\sum_i\frac{[D_i-(1+\alpha)S_i(\theta)-(1+\beta)B_i]^2}{\sigma_i^2}+\frac{\alpha^2}{\sigma_\alpha^2}+\frac{\beta^2}{\sigma_\beta^2}.$$

无背景pull的CONUS只保留α。地面Gaussian nuisance为原benchmark的无界解析profile，不偷偷套Ar[-1,1]的另一模型；每个独立实验用自己的α、β。联合先相加同一个物理θ下各自profile χ²，再寻找联合θ最小值。

太阳弱角/NSI采用

$$\chi^2=\sum_k\frac{[D_k-S_k(\theta)]^2}{\sigma_k^2+0.12^2S_k(\theta)^2},$$

等于对三个独立Gaussian归一化pull解析最小化。连续接受度和SNuDD传播均沿用当前模型；ee-NSI传播在每个参数点重算，最终信号不是固定Pee的二次多项式。

太阳自由通量主图用

$$\chi^2(f_B)=\sum_k[D_k-f_BS_{k,\rm SM}]^2/\sigma_k^2,\quad f_B\ge0,\quad\Phi_{^8B}=5.46\times10^6f_B\ {\rm cm}^{-2}{\rm s}^{-1}.$$

它是data-only的标准模型源强估计，不额外使用12%太阳模型通量先验；另一组control保留原独立12%归一化pull供敏感性比较。两种推断模型明确分开。

## 变量与参数域

sin²θW在[0,1]内扫描，其他SM输入固定；全核矢量/轴矢量响应保留，不用简单Qw²比值缩放整个实验。太阳SM对所有入射味通用，弱角变化在LEFT系数层严格等价于全味eu=-4Δsin²θW/3、ed=+2Δsin²θW/3，且已与原始截面核对；这里不乘Pee来当成仅ee的NSI。

NSI映射δC61q=-√2GF εqV；一次仅扫描一个实数耦合，其他NSI为0。COHERENT固定源支持ee、mumu、emu、etau、mutau；tautau对该无τ入射源无敏感度。CONUS采用已验证ee/emu/etau六个实数坐标；太阳传播合同仅支持ee-uV/dV。非对角复相位与同时多参数profile不属于本轮。

每条曲线计算连续1D最小值及独立粗网格再细化核对。NSI搜索范围由正二次事件总数与Gaussian Cauchy下界推导，避免仅凭绘图窗口声称全局；太阳再结合Pee下界。Δχ²=χ²profile(θ)-χ²min,1D；采用1、2.71、3.84阈值作为68%/90%/95%一参数benchmark。边界与不可辨识性单列；没有coverage toys，不将这些惯例自动视作所有NSI子空间的严格覆盖率或显著性。

## 实现分工

prediction_routes.py读取验证过的固定核、共享LEFT映射、原核矩阵收缩和太阳能量分辨状态；inference.py计算参数域、连续最小值及每个阈值的根；run_analysis.py装配各实验并执行扫描；validate_results.py作独立最小二乘、解析自由通量及原始截面核对；publish.py只读数值并绘图/生成报告。它们都是examples层，不被runtime导入。

## 接受边界

claim_level=approximate；科学/作者等价接受=NOT_REVIEWED。本轮技术验证证明声明的数值一致性，不推进P01-P10正式Gate，不重写旧误差或响应，不把CsI-time、CsI2017或其他受阻路线替换成更容易的似然。
"""
    (out/"STATISTICS_CONTRACT.md").write_text(contract+"\n", encoding="utf-8")
    figs = ["# 一维χ² benchmark论文图集", "", "2026-11-13。沿用180 mm/STIX统一版式；保存全部66条单参数路线的数值与区间。该图集区分已计算的近似模型和无法执行的能力。", "",
        "[七图合集](OneD_Chi2_Collection.pdf) · [完整结果与区间]("+relative_link(out/"RESULTS.md", figdir)+") · [每条实验计算路线]("+relative_link(out/"ROUTE_SUMMARY.md", figdir)+")", "",
        "| 图 | 内容 |", "|---|---|"]
    for name in outputs:
        figs.append(f"| [{name}.pdf]({name}.pdf) · [PNG]({name}.png) · [SVG]({name}.svg) | [对应英文图注]({name}_caption.txt) |")
    figs += ["", "[全部区间CSV](data/INTERVALS.csv) · [机器结果](data/RESULTS.json) · [文献比较](data/REFERENCE_COMPARISON.json) · [英文图注汇总](PAPER_CAPTIONS.md)", "",
        "data中还包含66份逐点CSV，每份含参数值、profile χ²和相对于该曲线自身1D最小值的Δχ²；τ对角的无敏感度路线标为全实轴，不把显示范围误称限值。", "",
        "图的颜色区分当前实验序列，橙色只表示论文的区间标记；没有作者数值网格时不绘制虚构的参考χ²曲线。仍遵循[统一规范](<../9. SM_uniform_style/STYLE_GUIDE.md>)，扩展序列配色见[STYLE.json](STYLE.json)。", "",
        "[统计合同]("+relative_link(out/"STATISTICS_CONTRACT.md", figdir)+") · [参考文献](REFERENCES.md) · [图件核对](qa/README.md) · [生成器](../../examples/one_d_benchmark/publish.py) · [上一级](../README.md)"]
    (figdir/"README.md").write_text("\n".join(figs)+"\n", encoding="utf-8")
    (figdir/"data/README.md").write_text("# 一维扫描图表数据\n\n66份命名CSV保存每条物理参数路线的原始profile χ²及自身最小值Δχ²。RESULTS.json保存全部极小值、区间、边界及假设；INTERVALS.csv便于查看全部区间；ROUTE_AUDIT/ROUTE_STEPS保存源码定位；REFERENCE_COMPARISON明确哪些文献结果具有相同目标、哪些只作背景参照。\n\n[图集](../README.md)\n", encoding="utf-8")
    reference_text = """# 本轮采用的参考文献

- G. Li, C.-Q. Song, F.-J. Tang and J.-H. Yu, *Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering*, [arXiv:2601.19883v2](https://arxiv.org/abs/2601.19883v2). [本地PDF](<../../docs/references/General_CEvNS/2601.19883v2.pdf>)。PDF p20 Eqs86–88、p21 Eq90/92、p22 Eq95：Gaussian定义、独立太阳pull、单参数阈值和NSI映射。
- V. De Romeri, D. K. Papoulias and G. Sanchez Garcia, *Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering*, Phys. Rev. D111,075025(2025), DOI10.1103/PhysRevD.111.075025, [arXiv:2501.17843v3](https://arxiv.org/abs/2501.17843v3). [本地PDF](<../../docs/references/CONUS/2501.17843v3.pdf>)。PDF p10 Eq33、p11 Eq34、p13 TableII：CONUS统计、弱角及六参数1σ对照。
- V. De Romeri et al., *Physics implications of a combined analysis of COHERENT CsI and LAr data*, JHEP04(2023)035, [arXiv:2211.11905v2](https://arxiv.org/abs/2211.11905v2). [本地PDF](<../../docs/references/COHERENT/2211.11905v2.pdf>)。PDF pp12–15输入/统计、p16 Eq41、p17 Fig1：含时间/形状误差的弱角结果；本次仅作不同likelihood背景对照。
- V. De Romeri, D. K. Papoulias and C. A. Ternes, *Bounds on new neutrino interactions from the first CEvNS data at direct detection experiments*, [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1). [本地PDF](<../../docs/references/Solar_CEvNS/2411.11749v1.pdf>)。PDF pp7–8 Eqs18–23/Fig2：太阳多bin通量和弱角；本次三单bin范围不同。
- D. Akimov et al. (COHERENT), *Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT*, PRL129,081801(2022), [arXiv:2110.07730v2](https://arxiv.org/abs/2110.07730v2)。[本地PDF](<../../docs/references/COHERENT/2110.07730v2.pdf>)；time原始C/AC及官方拟合与本地九箱legacy统计的区别保留。
- D. Akimov et al. (COHERENT), *First Measurement of Coherent Elastic Neutrino-Nucleus Scattering on Argon*, PRL126,012002(2021), [arXiv:2003.10630v7](https://arxiv.org/abs/2003.10630v7)。[本地PDF](<../../docs/references/COHERENT/2003.10630v7.pdf>)。
- D. Akimov et al. (COHERENT), *Observation of Coherent Elastic Neutrino-Nucleus Scattering*, Science357,1123(2017), [arXiv:1708.01294v1](https://arxiv.org/abs/1708.01294v1)。[本地PDF](<../../docs/references/COHERENT/1708.01294v1.pdf>)；本次仅核对已存25箱SM点。

论文、原始数据和项目现有数值表为不同证据层级。引用论文不意味着当前本地观测、响应、误差和相关性已与作者实现逐项等价。
"""
    (figdir/"REFERENCES.md").write_text(reference_text+"\n", encoding="utf-8")
    (figdir/"qa/README.md").write_text("# 图件与数据验收\n\npage-*.png为合集逐页渲染；contact_sheet.png为目视总览；PDF_QA.json记录180 mm固定画布、字体和页面边界；DOC_LINK_CHECKS.json记录新报告/导航链接。数值检验来自结果目录qa/INDEPENDENT_CHECKS.json，不将PDF排版检查计作物理验证。\n\n[图集](../README.md)\n", encoding="utf-8")
    (out/"README.md").write_text("# 实验计算路线与一维SM/NSI χ² benchmark\n\n[逐步Python路线总表](ROUTE_SUMMARY.md) · [完整结果](RESULTS.md) · [统计模型合同](STATISTICS_CONTRACT.md) · [全部区间](INTERVALS.csv) · [统一版式论文图](<"+relative_link(figdir/"README.md", out)+">)\n\n本次核查7条分析路线的70个步骤，完成66条声明的一维扫描，包括弱角、两种太阳通量定义以及可验证矢量NSI。CsI-time原生似然和CsI2017参数扫描仍有明确阻断；具体not_run见RESULTS.json。\n\nROUTE_AUDIT.json/ROUTE_STEPS.csv拥有实际py函数及哈希；scans拥有每条rawχ²/Δχ²；inputs拥有地面固定核与统计快照；SOURCE_MANIFEST.json记录所有采用来源；VALIDATION.json与qa/INDEPENDENT_CHECKS.json记录已执行数值核对；REFERENCE_COMPARISON.json区分论文数字与模型差异；WRITE_PLAN.json和FILE_LIFECYCLE.json记录范围、父导航备份及归属。\n\n[入口代码](../../examples/one_d_benchmark/README.md) · [返回outputs](../README.md)\n", encoding="utf-8")
    (out/"inputs/README.md").write_text("# 本轮地面分析固定模型快照\n\nCsI2021、Ar2020、CONUS_plus的NPZ分别保存既有最终核、外部固定rho和保存的统计数组。它们属于可审核的冻结benchmark回放，不是绕过失败loader而新注册的活动dataset。原来的内核与输入从未覆盖。太阳实际核/源引用见SOURCE_MANIFEST.json，仍从原路径只读消费。\n\n[结果](../RESULTS.md) · [统计合同](../STATISTICS_CONTRACT.md)\n", encoding="utf-8")
    (out/"scans/README.md").write_text("# 每条一维扫描\n\n每个NPZ含grid、chi2、delta_chi2三个等长数组，delta只减去对应曲线的连续1D最小值。实际极值、区间、阈值和有根据的域保存在上一级RESULTS.json；不使用二维全局最小值或简单显示框界。\n\n[区间总表](../INTERVALS.csv) · [结果报告](../RESULTS.md)\n", encoding="utf-8")
    (out/"qa/README.md").write_text("# 实际验收范围\n\nINDEPENDENT_CHECKS.json记录解析自由通量、原始逐能量微分截面、full/pair响应及所有阈值根回代；不是新的最终网格Slow积分、官方likelihood或toy coverage认证。文档、路径及最终原件保护检查另存FINAL_CHECKS.json。\n\n[结果](../RESULTS.md) · [路线](../ROUTE_SUMMARY.md)\n", encoding="utf-8")
    # Standalone route documentation in the experiment documentation tree.
    route_text = (out/"ROUTE_SUMMARY.md").read_text(encoding="utf-8")
    import re
    def relink(match):
        raw = match.group(1)
        oldpath = (out/raw).resolve()
        return "](<"+relative_link(oldpath, ROOT/"docs/experiments")+">)"
    route_text = re.sub(r"\]\(<([^>]+)>\)", relink, route_text)
    route_text = route_text.replace("](ROUTE_AUDIT.json)", "]("+relative_link(out/"ROUTE_AUDIT.json", ROOT/"docs/experiments")+")")
    route_text = route_text.replace("](ROUTE_STEPS.csv)", "]("+relative_link(out/"ROUTE_STEPS.csv", ROOT/"docs/experiments")+")")
    route_text += "\n\n[一维计算完整结果]("+relative_link(out/"RESULTS.md", ROOT/"docs/experiments")+") · [实验总目录](README.md)\n"
    (ROOT/"docs/experiments/COMPUTATION_ROUTES_20261113.md").write_text(route_text, encoding="utf-8")
    sources = read(out/"SOURCE_MANIFEST.json")
    for p in [*HERE.glob("*.py"), ROOT/"论文图NoteBook/9. SM_uniform_style/STYLE.json", ROOT/"论文图NoteBook/9. SM_uniform_style/publication_style.py"]:
        sources[p.relative_to(ROOT).as_posix()] = sha(p)
    write(out/"SOURCE_MANIFEST.json", sources)
    write(figdir/"FIGURE_MANIFEST.json", {"date": "2026-11-13", "figures": outputs,
        "source_results_sha256": sha(out/"RESULTS.json"), "source_interval_csv_sha256": sha(out/"INTERVALS.csv"),
        "generator_sha256": sha(__file__), "physical_width_mm": 180, "PDF_validation": "PENDING"})
    print("Published", len(outputs), "figures; full interval report and 66 raw-chi2 CSVs")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main()
