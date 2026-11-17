"""Role-colored cutoff replots, paper comparison, and joint-analysis figures.

All colors and typography are read from the user's SM_uniform_style module.
No numerical inference is performed here. Outputs are create-only.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import LogLocator, NullFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, read, sha, write_json
from run_joint import MAIN_GROUPS, OLD_DIM6, OLD_FULL, verify_sources
from compare_paper import write_csv, paper_operator
from forward22 import KEYS

STYLE_DIR = ROOT/"论文图NoteBook/9. SM_uniform_style"
spec = importlib.util.spec_from_file_location("cutoff_publication_style", STYLE_DIR/"publication_style.py")
appearance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(appearance)
STYLE = appearance.load_style()
COLORS = STYLE["colors"]
LABELS = {"CONUS_plus": "CONUS+", "CsI2021_9PE": "CsI: 9 energy bins",
          "Ar2020_average": "Ar: average errors", "CsI2021_9PE+Ar2020_average": "COHERENT: CsI + Ar",
          "Solar_three_singlebins": "Solar: three-sample joint", "PandaX_paired": "PandaX: paired",
          "PandaX_US2": "PandaX: US2", "XENONnT": "XENONnT"}


def operator_label(key):
    d, i, q = key
    return rf"$\mathcal{{O}}_{{{i}}}^{{{d}{q}}}$"


def fresh_directory(path):
    path = Path(path).resolve()
    parent = (ROOT/"论文图NoteBook/12. Cutoff_Scale_Benchmarks").resolve()
    if path==parent or not path.is_relative_to(parent):
        raise ValueError("figure output must belong to isolated cutoff figures")
    path.mkdir(parents=True, exist_ok=False)
    (path/"plot_data").mkdir()
    return path


def canvas(n=1, *, full=False, layout=None):
    s = deepcopy(STYLE)
    if layout is None:
        if full and n>1:
            height = 2.05*n+1.15
            bottom, top, gap = .12, .84, .09
            h = (top-bottom-(n-1)*gap)/n
            rects = [[.1, top-(i+1)*h-i*gap, .875, h] for i in range(n)]
        elif n==1:
            height = 4.35 if full else 3.9
            rects = [[.1,.245 if full else .20,.875,.50 if full else .55]]
        elif n==2:
            height, rects = 3.95, [[.09,.20,.39,.55],[.585,.20,.39,.55]]
        elif n==3:
            height, rects = 3.95, [[.08,.20,.25,.55],[.40,.20,.25,.55],[.72,.20,.25,.55]]
        else:
            height, rects = 6.0, [[.09,.57,.39,.24],[.585,.57,.39,.24],[.09,.17,.39,.24],[.585,.17,.39,.24]]
    else:
        height, rects = layout
    s["layouts"]["cutoff"] = {"height_in": height, "axes_rects": rects}
    s["note_y"] = .035
    fig, axes = appearance.new_figure("cutoff", style=s)
    return fig, axes, s


def finish(fig, s, titles, heading, note, *, xkind="category"):
    appearance.finalize(fig, "cutoff", titles=titles, note=note,
                        xkinds=[xkind]*len(fig.axes), style=s)
    # Heading below the figure-level legend and above panel titles.
    entries = len(fig.legends[0].get_texts()) if fig.legends else 0
    heading_y = .825 if entries>4 else .86 if entries>2 else .905
    fig.text(.1,heading_y,heading,ha="left",va="center",fontsize=s["axis_label_pt"])
    return fig


def category_axis(ax, keys, values, *, full=False):
    ax.set_yscale("log")
    ax.set_xlim(-.65,len(keys)-.35)
    finite = [v for v in values if v is not None and v>0]
    low = .1 if full else 10**np.floor(np.log10(min(finite)*.7))
    ax.set_ylim(low,max(finite)*2.2)
    ax.set_xticks(np.arange(len(keys)),[operator_label(k) for k in keys],rotation=60 if full else 0)
    if full:
        for label in ax.get_xticklabels(): label.set_ha("right")
    ax.set_ylabel(r"$\Lambda_{\rm min}$ [GeV]")
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=7))
    ax.yaxis.set_minor_formatter(NullFormatter())


def bars(ax, positions, values, *, color, label, width=.35, hatch=None):
    chosen=[(x,y) for x,y in zip(positions,values) if y is not None]
    if chosen:
        xx, yy = map(np.array,zip(*chosen))
        ax.bar(xx,yy-.01,bottom=.01,width=width,color=color,edgecolor=color,
               linewidth=STYLE["filled_edge_pt"],hatch=hatch,label=label)


def export(output, stem, fig, data, collection):
    appearance.export(fig,output/stem)
    collection.savefig(fig)
    plt.close(fig)
    write_csv(output/"plot_data"/(stem+".csv"),data)


def manifest(output, sources, stems, captions):
    sources.update({p.relative_to(ROOT).as_posix():sha(p) for p in [STYLE_DIR/"STYLE.json",STYLE_DIR/"publication_style.py",HERE/"publish_comparison.py"]})
    for p,h in sources.items():
        if sha(ROOT/p)!=h: raise ValueError("stale plot source: "+p)
    record={"schema":SCHEMA,"part_id":PART,"run_id":output.name,"source_manifest":sources,
            "style":STYLE,"color_roles":{"local":"work_SM","paper":"reference","joint_total":"control_or_total","branch_or_secondary":"neutral"},
            "figures":stems,"outputs":{p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob("*")) if p.is_file()}}
    write_json(output/"FIGURE_MANIFEST.json",record)
    (output/"CAPTIONS.md").write_text("# Figure captions\n\n"+"\n\n".join(f"**{stem}.** {caption}" for stem,caption in zip(stems,captions))+"\n",encoding="utf-8")
    links="\n".join(f"- [{stem}]({stem}.pdf)" for stem in stems)
    (output/"README.md").write_text("# 统一视觉角色的截断能标图\n\n[PDF合集](Cutoff_Comparison_Collection.pdf) · [英文图注](CAPTIONS.md) · [来源与样式](FIGURE_MANIFEST.json)\n\n"+links+
        "\n\n蓝色=本地计算；橙色=论文Fig.3读图参考；绿色=三组总联合；灰色=分支/次级比较。"
        "颜色与版式直接读取9. SM_uniform_style，实验身份通过独立面板或线型表示。每图有同画布PDF/SVG/PNG与plot_data/逐柱或逐点CSV。"
        "控制版的固定太阳态、LNV过渡味和dim-8正定性缺口不能由图形覆盖；完整统计允许集仍以数值结果为准。\n\n"
        "[返回图集目录](../README.md) · [代码与计算](../../../examples/cutoff_scales/README.md)\n",encoding="utf-8")


def replot(results, output):
    record=read(results+"/RESULTS.json"); verify_sources(record)
    output=fresh_directory(output)
    full=record["stage"].startswith("FULL22")
    keys=list(KEYS) if full else [(6,1,"u"),(6,1,"d"),(6,2,"u"),(6,2,"d")]
    idx={(r["analysis_group"],tuple(r["operator_key"])):r for r in record["results"]}
    selections=[("01_Three_groups_90CL",list(MAIN_GROUPS),keys,"90",False),
                ("02_Ground_90CL",["CONUS_plus","CsI2021_9PE","Ar2020_average","CsI2021_9PE+Ar2020_average"],keys,"90",False),
                ("03_Solar_90CL",["PandaX_paired","PandaX_US2","XENONnT","Solar_three_singlebins"],keys if full else keys[:2],"90",False),
                ("04_Branches_90CL",list(MAIN_GROUPS),keys[1:3] if full else keys[:2],"90",True),
                ("05_Three_groups_95CL",list(MAIN_GROUPS),keys,"95",False)]
    stems,captions=[],[]
    with PdfPages(output/"Cutoff_Comparison_Collection.pdf") as pdf:
        for stem,groups,ops,cl,branch in selections:
            isfull=len(ops)>10
            fig,axes,s=canvas(len(groups),full=isfull)
            data=[]
            for ax,group in zip(axes,groups):
                a=[idx.get((group,tuple(k))) for k in ops]
                vals=[None if r is None else r["confidence"][cl].get("global_GeV") for r in a]
                bars(ax,np.arange(len(ops))-(.18 if branch else 0),vals,color=COLORS["work_SM"],label="Local: global conservative",width=.32 if branch else .65)
                if branch:
                    sm=[r["confidence"][cl].get("sm_connected_GeV") for r in a]
                    bars(ax,np.arange(len(ops))+.18,sm,color=COLORS["neutral"],label="Local: SM-connected",width=.32,hatch="///")
                    vals=vals+sm
                category_axis(ax,ops,vals,full=isfull)
                for j,(key,r) in enumerate(zip(ops,a)):
                    if r is None:
                        status="NOT_IN_THIS_VERSION"
                    else: status=r["confidence"][cl]["status"]
                    v=None if r is None else r["confidence"][cl].get("global_GeV")
                    if v is None:
                        ax.text(j,ax.get_ylim()[0]*1.35,"zero response" if status=="NO_SENSITIVITY" else "not scanned",rotation=90,ha="center",va="bottom")
                    data.append({"group":group,"operator":paper_operator(key),"CL":cl,"global_GeV":v,
                                 "sm_connected_GeV":None if r is None else r["confidence"][cl].get("sm_connected_GeV"),"status":status})
            if not isfull and len(axes)>1:
                limits=(min(ax.get_ylim()[0] for ax in axes),max(ax.get_ylim()[1] for ax in axes))
                for ax in axes: ax.set_ylim(*limits)
            if len(axes)==3 and not isfull:
                for ax in axes[1:]: ax.set_ylabel("")
            heading=("Full22 local control" if full else "dim-6 local benchmark")+f": {cl}% nominal CL, |g| = 1"
            note="Fixed solar SM state; LNC ee / LNV e-mu. Dim-8 positivity unresolved: control only." if full else "Solar ee propagation updated at every coefficient; missing entries have no numerical bar."
            finish(fig,s,[LABELS[g] for g in groups],heading,note)
            export(output,stem,fig,data,pdf);stems.append(stem)
            captions.append(f"Replot of {results}, {cl}% nominal one-parameter confidence, |g|=1. Blue always denotes the local result. Panels identify experiments. Full signed confidence sets and physical validation status remain in the numerical record. "+note)
    manifest(output,{results+"/RESULTS.json":sha(ROOT/results/"RESULTS.json")},stems,captions)
    print("REPLOTTED",output,flush=True)


def publish_comparison(comparison, output):
    path=Path(comparison).resolve()
    record=read((path/"COMPARISON.json").relative_to(ROOT).as_posix())
    verify_sources(record)
    output=fresh_directory(output)
    joint=read(record["joint_run"]+"/RESULTS.json");verify_sources(joint)
    main=read(OLD_DIM6+"/RESULTS.json")
    rows=record["rows"]
    stems,captions=[],[]
    def save(stem,fig,data,caption,pdf):
        export(output,stem,fig,data,pdf);stems.append(stem);captions.append(caption)
    with PdfPages(output/"Cutoff_Comparison_Collection.pdf") as pdf:
        fig,axes,s=canvas(3)
        data=[]
        for ax,group in zip(axes,MAIN_GROUPS):
            selected=[r for r in rows if r["version"].startswith("dim6") and r["analysis_group"]==group]
            keys=[(6,1,"u"),(6,1,"d")]+([] if group==MAIN_GROUPS[2] else [(6,2,"u"),(6,2,"d")])
            xx=np.arange(len(selected)); a=[r["local_90CL_GeV"] for r in selected];b=[r["paper_fig3_90CL_GeV"] for r in selected]
            bars(ax,xx-.18,a,color=COLORS["work_SM"],label="Local benchmark")
            bars(ax,xx+.18,b,color=COLORS["reference"],label="Paper Fig. 3")
            category_axis(ax,keys,a+b)
            data.extend(selected)
        for ax in axes: ax.set_ylim(10,1000)
        for ax in axes[1:]: ax.set_ylabel("")
        finish(fig,s,[LABELS[g] for g in MAIN_GROUPS],"dim-6: local versus paper, 90% nominal CL","Paper bars digitized from PDF geometry; solar local result uses point-dependent propagation.")
        save("01_DIM6_Local_vs_Paper",fig,data,"Adopted dim-6 main results versus graphical 90% bounds from Fig. 3. Solar panel contains only the two supported self-consistent vectors; absence of axial entries is not a zero limit.",pdf)
        full=[r for r in rows if r["version"].startswith("full22")]
        for number,group in enumerate(MAIN_GROUPS,2):
            selected=[next(r for r in full if r["analysis_group"]==group and r["paper_operator"]==paper_operator(k)) for k in KEYS]
            fig,axes,s=canvas(full=True);ax=axes[0];xx=np.arange(len(KEYS))
            a=[r["local_90CL_GeV"] for r in selected];b=[r["paper_fig3_90CL_GeV"] for r in selected]
            bars(ax,xx-.18,a,color=COLORS["work_SM"],label="Local full22 control")
            bars(ax,xx+.18,b,color=COLORS["reference"],label="Paper Fig. 3")
            category_axis(ax,KEYS,a+b,full=True)
            finish(fig,s,[LABELS[group]],"Full22 comparison: 90% nominal CL, |g| = 1","Local: LNC ee / LNV e-mu; solar state fixed. Dim-8 positivity unresolved: control only.")
            save(f"{number:02d}_Full22_{['CONUS','COHERENT','Solar'][number-2]}_vs_Paper",fig,selected,"Every local operator bound is paired with the corresponding graphical paper bar. Differences include unresolved flavor/input/forward-model equivalence; fixed-state solar and all dim-8 entries remain controls.",pdf)
        fig,axes,s=canvas(3,full=True)
        for ax,group in zip(axes,MAIN_GROUPS):
            selected=[next(r for r in full if r["analysis_group"]==group and r["paper_operator"]==paper_operator(k)) for k in KEYS]
            ratio=[r["ratio_local_over_paper"] for r in selected]
            ax.plot(np.arange(22),ratio,"o-",color=COLORS["work_SM"],label="Local / paper")
            ax.axhline(1,color=COLORS["neutral"],ls="--",label="Equal graphical height")
            ax.set_yscale("log");ax.set_ylim(.18,2.8);ax.set_xlim(-.65,21.65)
            ax.set_yticks([.25,.5,1,2],["0.25","0.5","1","2"])
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.set_xticks(np.arange(22),[operator_label(k) for k in KEYS],rotation=60,ha="right")
            ax.set_ylabel("Local / paper")
        finish(fig,s,[LABELS[g] for g in MAIN_GROUPS],"Full22 graphical comparison ratios","Reference is a digitized figure, not an author likelihood. Local full22 values are controls.")
        save("05_Full22_Ratio_to_Paper",fig,full,"Local/paper ratios expose the full pattern of agreement and disagreement rather than only the vector entries. Unity is a geometric comparison, not a certified precision target.",pdf)
        selected=[r for r in record["joint_comparison"] if r["version"].startswith("full22")]
        fig,axes,s=canvas(full=True);ax=axes[0];xx=np.arange(22)
        a=[r["strongest_individual_90CL_GeV"] for r in selected];b=[r["joint_90CL_GeV"] for r in selected]
        bars(ax,xx-.18,a,color=COLORS["work_SM"],label="Strongest single group")
        bars(ax,xx+.18,b,color=COLORS["control_or_total"],label="Three-group joint")
        category_axis(ax,KEYS,a+b,full=True)
        finish(fig,s,["All three groups; six underlying datasets"],"Full22 joint: 90% nominal CL, |g| = 1","Fixed solar SM state; independent pulls. Dim-8 positivity unresolved: control only.")
        save("06_Full22_Joint_vs_Strongest",fig,selected,"Three-group joint versus strongest individual group. Each joint is minimized anew in the common physical coefficient. Bounds need not strengthen monotonically because all curves use their own minima.",pdf)
        fig,axes,s=canvas(2)
        data=[]
        for ax,q in zip(axes,("u","d")):
            op="C6"+q+"1"
            individual=[next(r for r in rows if r["version"].startswith("dim6") and r["analysis_group"]==g and r["operator"]==op) for g in MAIN_GROUPS]
            jr=next(r for r in record["joint_comparison"] if r["version"].startswith("dim6") and r["operator"]==op)
            values=[r["local_90CL_GeV"] for r in individual]+[jr["joint_90CL_GeV"]]
            ax.bar(np.arange(4),values,color=[COLORS["work_SM"]]*3+[COLORS["control_or_total"]],width=.65)
            ax.set_xticks(np.arange(4),["CONUS+","CsI + Ar","Solar joint","All three"],rotation=25,ha="right")
            ax.set_ylim(0,460);ax.set_ylabel(r"$\Lambda_{\rm min}$ [GeV]")
            for x,v in enumerate(values):ax.text(x,v+9,f"{v:.2f}",ha="center")
            data.extend([{ "operator":op,"group":g,"Lambda_GeV":v} for g,v in zip([*MAIN_GROUPS,"all_three_joint"],values)])
        finish(fig,s,[operator_label((6,1,"u")),operator_label((6,1,"d"))],"dim-6 vectors: three-group joint, 90% nominal CL","Solar propagation updated at every c; six datasets, eight independent Gaussian nuisances.")
        save("07_DIM6_Joint_Bounds",fig,data,"Conservative signed-coefficient global bounds for the dim-6 vector main analysis. The strict SM-connected limits are distinct and retained in the machine record.",pdf)
        fig,axes,s=canvas(2)
        data=[]
        for ax,q in zip(axes,("u","d")):
            key=(6,1,q)
            jr=next(r for r in joint["results"] if r["version"].startswith("dim6") and tuple(r["operator_key"])==key)
            with np.load(ROOT/record["joint_run"]/jr["scan_path"],allow_pickle=False) as a:
                coefficient=a["coefficient"];xx=a["x"];components=a["component_chi2"];total=a["delta_chi2"]
            for i,(g,ls) in enumerate(zip(MAIN_GROUPS,("-","--",":"))):
                old=next(r for r in main["results"] if r["analysis_group"]==g and tuple(r["operator_key"])==key)
                values=components[i]-old["chi2_min"]
                ax.plot(xx,values,color=COLORS["work_SM"],ls=ls,label=LABELS[g])
            ax.plot(xx,total,color=COLORS["control_or_total"],label="All three: joint minimum")
            ax.axhline(2.71,color=COLORS["neutral"],ls="--",label="90%: 2.71")
            ax.set_ylim(0,10);ax.set_xlim(-.50,.11)
            ax.set_xlabel(r"$c/(\sqrt{2}G_F)=-\epsilon_{ee}^{qV}$");ax.set_ylabel(r"$\Delta\chi^2$")
            data.extend({"operator":q,"coefficient":float(c),"normalized_x":float(x),"joint_delta_chi2":float(y),
                         "CONUS_chi2":float(v[0]),"COHERENT_chi2":float(v[1]),"solar_chi2":float(v[2])}
                        for c,x,y,v in zip(coefficient,xx,total,components.T))
        finish(fig,s,[operator_label((6,1,"u")),operator_label((6,1,"d"))],"dim-6 vectors: joint and component likelihoods","Each curve subtracts its own minimum. The green joint curve defines the joint confidence set.",xkind="continuous")
        save("08_DIM6_Joint_Chi2",fig,data,"The green total is the sum of absolute profiled component chi2 minus the minimum of that sum. Blue components each subtract their own minima for display only. Disconnected sign-degenerate solutions remain present.",pdf)
        fig,axes,s=canvas(2)
        data=[]
        for ax,q in zip(axes,("u","d")):
            jr=next(r for r in joint["results"] if r["version"].startswith("dim6") and tuple(r["operator_key"])==(6,1,q))
            c=jr["confidence"]["90"]
            vals=[c["global_GeV"],c["sm_connected_GeV"]]
            ax.bar([0,1],vals,color=[COLORS["control_or_total"],COLORS["neutral"]],width=.65)
            ax.set_xticks([0,1],["Global conservative","SM-connected"],rotation=15,ha="right")
            ax.set_ylim(0,1350);ax.set_ylabel(r"$\Lambda_{\rm min}$ [GeV]")
            for x,v in enumerate(vals):ax.text(x,v+25,f"{v:.2f}",ha="center")
            data.extend([{"operator":q,"branch":b,"Lambda_GeV":v} for b,v in zip(["global_conservative","SM_connected"],vals)])
        finish(fig,s,[operator_label((6,1,"u")),operator_label((6,1,"d"))],"Joint limits retain disconnected coefficient branches","SM-connected and global bounds answer different questions; complete intervals are stored numerically.")
        save("09_DIM6_Joint_Branches",fig,data,"Strict SM-connected lower scales and global conservative lower scales for the same joint likelihood. The high-scale SM-connected component does not remove the separate finite-scale allowed island.",pdf)
    manifest(output,{(path/"COMPARISON.json").relative_to(ROOT).as_posix():sha(path/"COMPARISON.json"),
                     record["joint_run"]+"/RESULTS.json":sha(ROOT/record["joint_run"]/"RESULTS.json")},stems,captions)
    print("PUBLISHED",output,len(stems),"figures",flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replot",choices=("dim6","full22"))
    p.add_argument("--comparison",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if bool(a.replot)==bool(a.comparison):p.error("select exactly one replot or comparison")
    if a.replot:replot(OLD_DIM6 if a.replot=="dim6" else OLD_FULL,a.output)
    else:publish_comparison(a.comparison,a.output)
