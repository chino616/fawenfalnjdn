"""Overlay official event counts on the saved CsI2021 SM prediction.

No prediction, fit or template normalization is changed.
Raw C counts are compared with signal+unscaled background diagnostics.
SSB-only and all-background subtraction are separately labelled diagnostics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/"workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n",
        encoding="utf-8", newline="\n")


def histogram(events, pe, times):
    selected=(events[:,0]>=pe[0])&(events[:,0]<pe[-1])
    selected&=(events[:,1]>=times[0])&(events[:,1]<times[-1])
    return np.histogram2d(events[selected,0],events[selected,1],bins=(pe,times))[0].astype(int)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--onboarding",type=Path,default=BASE)
    parser.add_argument("--date",default="2026-11-15")
    parser.add_argument("--overwrite",action="store_true",help="Only after preserving existing plots and metadata")
    args=parser.parse_args()
    run=args.run_dir.resolve(); output=args.output_dir.resolve(); base=args.onboarding.resolve()
    if output.exists() and not args.overwrite: parser.error("Choose a fresh output directory to preserve earlier plots")
    validation=read(run/"VALIDATION_RESULTS.json")
    assert validation["status"]=="PASS_SM_FORWARD_NUMERICAL_CHECKS"
    previous_plot=read(run/"PLOT_MANIFEST.json")
    assert sha(run/"benchmark.npz")==previous_plot["data_sha256"]
    grid=read(run/"grid_512_960/report.json")
    assert sha(base/"P00_SOURCE_REGISTER.yaml")==grid["source_register_sha256"]
    register=read(base/"P00_SOURCE_REGISTER.yaml")
    sources={row["source_id"]:row for row in register["sources"]}
    for row in sources.values(): assert sha(ROOT/row["uri_or_path"])==row["sha256"],row["source_id"]
    state=read(run/"SOURCE_STATE_BEFORE_VALIDATION.json")
    # Historical code may have evolved since the saved calculation. Plotting
    # requires the pinned data above, not a claim that today's driver is old code.
    code_before={name:sha(ROOT/name) for name in state["files"]}
    historical_code_differences=[name for name,value in code_before.items() if value!=state["files"][name]]
    with np.load(run/"benchmark.npz",allow_pickle=False) as z:
        keys=["pe_edges","time_edges_us","C_raw","AC_raw","SS_derived","BRN_raw_template",
            "NIN_raw_template","signal_counts","expected_raw_template_diagnostic",
            "signal_excess_raw_template_diagnostic"]
        data={key:z[key] for key in keys}
        flavors=z["target_component_counts"].sum(axis=0)  # mu, e, mub; PE, time
    np.testing.assert_allclose(flavors.sum(axis=0),data["signal_counts"],rtol=1e-14,atol=1e-12)
    pe,times=data["pe_edges"],data["time_edges_us"]
    for key in keys[2:]:
        assert data[key].shape==(9,11) and np.isfinite(data[key]).all(),key
    raw_files={"C_raw":"S_dataBeamOnC","AC_raw":"S_dataBeamOnAC"}
    raw_records=[]
    for name,source_id in raw_files.items():
        file=ROOT/sources[source_id]["uri_or_path"]
        events=np.loadtxt(file)
        rebuilt=histogram(events,pe,times)
        np.testing.assert_array_equal(rebuilt,data[name])
        raw_records.append({"array":name,"source_id":source_id,"path":str(file),"sha256":sha(file),
            "original_url":sources[source_id]["original_url"],"locator":"All event rows; columns0=PE,1=reconstructed_time_us",
            "input_event_shape":list(events.shape),"selected_events":int(rebuilt.sum()),
            "bin_rule":"left closed/right open; PE60 and time6us excluded","rebin_check":"EXACT_MATCH_ALL99_BINS"})
    with np.load(base/"data/analysis_inputs.npz",allow_pickle=False) as z:
        for old,new in [("C_counts","C_raw"),("AC_counts","AC_raw"),("SS_counts","SS_derived")]:
            np.testing.assert_array_equal(z[old],data[new])
    # Rebuild the adopted SSB model from the independent 0-12 us AC sample.
    # These are partial counting errors, with the control time shape fixed.
    ledger=read(base/"P01_EVIDENCE_LEDGER.yaml")
    claims={row["claim_id"]:row for row in ledger["claims"]}
    ac_events=np.loadtxt(ROOT/sources["S_dataBeamOnAC"]["uri_or_path"])
    selected=(ac_events[:,0]>=pe[0])&(ac_events[:,0]<pe[-1])&(ac_events[:,1]>=0)&(ac_events[:,1]<12)
    ac12=np.histogram(ac_events[selected,0],bins=pe)[0]
    k=float(claims["C_TIME_EFF"]["value"][1])
    p_time=np.exp(-k*times[:-1])*(-np.expm1(-k*np.diff(times)))/(-np.expm1(-k*12))
    np.testing.assert_allclose(ac12[:,None]*p_time[None,:],data["SS_derived"],rtol=2e-14,atol=1e-12)
    ss_cov=np.einsum("ik,i,j,l->ijkl",np.eye(len(ac12)),ac12,p_time,p_time).reshape(99,99)
    residual_cov=np.diag(data["C_raw"].ravel())+ss_cov
    counting_sigma=np.sqrt(np.diag(residual_cov)).reshape(9,11)
    projectors={"PE":np.kron(np.eye(9),np.ones((1,11))),
                "time":np.kron(np.ones((1,9)),np.eye(11))}
    projected_cov={name:matrix@residual_cov@matrix.T for name,matrix in projectors.items()}
    background=data["SS_derived"]+data["BRN_raw_template"]+data["NIN_raw_template"]
    expected=data["signal_counts"]+background
    excess=data["C_raw"]-background
    np.testing.assert_allclose(expected,data["expected_raw_template_diagnostic"],rtol=1e-14,atol=1e-12)
    np.testing.assert_allclose(excess,data["signal_excess_raw_template_diagnostic"],rtol=1e-14,atol=1e-12)
    assert abs(float(data["signal_counts"].sum())-validation["SM_total_events"])<1e-12
    output.mkdir(parents=True,exist_ok=args.overwrite)
    figures=output/"figures";figures.mkdir(exist_ok=args.overwrite)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.labelsize":12,
        "axes.spines.top":False,"axes.spines.right":False,"svg.fonttype":"none",
        "svg.hashsalt":"csi2021_sm_data_20261109","axes.titleweight":"bold"})
    produced=[]

    def save(fig,name):
        for extension in ("png","svg"):
            file=figures/(name+"."+extension)
            fig.savefig(file,dpi=220,facecolor="white",metadata={"Date":args.date,"Creator":"CsI2021 SM and official event data comparison"})
            produced.append({"path":file.relative_to(output).as_posix(),"sha256":sha(file)})
        plt.close(fig)

    footer=("Data: COHERENT 2110.07730v2 ancillary; locally rebinned 9 PE x 11 time bins.\n"
        "SM: unfitted local nuclear RESPONSE, 353.465609 events; 0-6 us reference convention. Raw BRN/NIN normalization unresolved.")
    sm_color="#20659a";total_color="#b34c3a";steady_color="#9ca8b3";neutron_color="#c68d28"

    def raw_panel(axis,edges,reduce_axis):
        width=np.diff(edges);center=(edges[:-1]+edges[1:])/2
        project=lambda x:x.sum(axis=reduce_axis)
        observed=project(data["C_raw"])
        axis.stairs(project(data["SS_derived"])/width,edges,color=steady_color,fill=True,alpha=.20,label="SSB from AC control model")
        axis.stairs(project(data["BRN_raw_template"]+data["NIN_raw_template"])/width,edges,color=neutron_color,linestyle=":",linewidth=1.7,label="BRN + NIN, raw templates")
        axis.stairs(project(data["signal_counts"])/width,edges,color=sm_color,linewidth=2.2,label="Nominal SM signal")
        axis.stairs(project(expected)/width,edges,color=total_color,linestyle="--",linewidth=2.1,label="SM + raw background diagnostic")
        axis.errorbar(center,observed/width,xerr=width/2,yerr=np.sqrt(observed)/width,fmt="o",color="#17232e",
            markersize=4.6,capsize=2,elinewidth=1.0,zorder=5,label=r"Observed C data ($\sqrt{C}$ bars)")
        axis.set_ylim(0,None);axis.grid(axis="y",alpha=.15)

    fig,axes=plt.subplots(1,2,figsize=(13.8,6.6))
    raw_panel(axes[0],pe,1);raw_panel(axes[1],times,0)
    axes[0].set(xlabel="Reconstructed photoelectrons (PE)",ylabel="Events / PE",title="PE projection, summed over 0-6 us",xlim=(0,60))
    axes[1].set(xlabel=r"Reconstructed time $t_{rec}$ ($\mu$s)",ylabel=r"Events / $\mu$s",title="Time projection, summed over 0-60 PE",xlim=(0,6))
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="upper center",bbox_to_anchor=(.51,.945),ncol=3,frameon=False,fontsize=10)
    fig.suptitle("CsI2021 raw-count projections: data and unfitted local prediction",fontsize=17,y=.99)
    fig.text(.5,.805,f"Raw C: {int(data['C_raw'].sum())} | SM: {data['signal_counts'].sum():.2f} | total diagnostic: {expected.sum():.2f} | total - C: {expected.sum()-data['C_raw'].sum():.2f} events",ha="center",fontsize=10,color="#596774")
    fig.text(.055,.035,footer+"\nBars: sqrt(C) only. These projections are local diagnostics; De Romeri 2211.11905v2 Fig.18 shows time slices.",fontsize=8.7,color="#46586a")
    fig.subplots_adjust(left=.075,right=.98,top=.70,bottom=.22,wspace=.25)
    save(fig,"sm_data_projections")

    fig,axes=plt.subplots(1,2,figsize=(13.8,5.8))
    for axis,edges,reduce_axis in [(axes[0],pe,1),(axes[1],times,0)]:
        width=np.diff(edges);center=(edges[:-1]+edges[1:])/2
        axis.stairs(data["signal_counts"].sum(axis=reduce_axis)/width,edges,color=sm_color,linewidth=2.4,label="Nominal SM signal")
        name="PE" if reduce_axis==1 else "time"
        sigma=np.sqrt(np.diag(projected_cov[name]))
        axis.errorbar(center,excess.sum(axis=reduce_axis)/width,xerr=width/2,yerr=sigma/width,fmt="o",markersize=5,
            color="#17232e",capsize=2,label="C - SSB - BRN - NIN (C+AC counting bars)",zorder=5)
        axis.axhline(0,color="#8b959d",linewidth=.9,linestyle=":");axis.grid(axis="y",alpha=.15)
    axes[0].set(xlabel="Reconstructed photoelectrons (PE)",ylabel="Events / PE",title="PE projection",xlim=(0,60))
    axes[1].set(xlabel=r"Reconstructed time $t_{rec}$ ($\mu$s)",ylabel=r"Events / $\mu$s",title="Time projection",xlim=(0,6))
    axes[0].legend(frameon=False,fontsize=10)
    fig.suptitle("CsI2021 all-background-subtracted diagnostic: unfitted SM",fontsize=17,y=.99)
    fig.text(.5,.91,"Points = C - SSB - raw BRN - raw NIN; derived values, not a published signal measurement",ha="center",fontsize=10,color="#7f4d3c")
    fig.text(.055,.03,footer+"\nBars: C+AC counting only; fixed SSB time shape and neutron templates. Negative bins retained; not COHERENT Fig.1 Data Residual.",fontsize=8.7,color="#46586a")
    fig.subplots_adjust(left=.075,right=.98,top=.79,bottom=.24,wspace=.25)
    save(fig,"sm_data_excess_diagnostic")

    fig,axes=plt.subplots(3,4,figsize=(15.6,11.0));axes=axes.ravel();width=np.diff(pe)
    for j,axis in enumerate(axes[:11]):
        observed=data["C_raw"][:,j]
        axis.stairs(data["SS_derived"][:,j]/width,pe,color=steady_color,fill=True,alpha=.20)
        neutron=data["BRN_raw_template"][:,j]+data["NIN_raw_template"][:,j]
        axis.stairs((data["SS_derived"][:,j]+neutron)/width,pe,baseline=data["SS_derived"][:,j]/width,
            fill=True,color=neutron_color,alpha=.45)
        axis.stairs(expected[:,j]/width,pe,baseline=(data["SS_derived"][:,j]+neutron)/width,
            fill=True,color=sm_color,alpha=.16)
        axis.stairs(data["signal_counts"][:,j]/width,pe,color=sm_color,linewidth=1.9)
        axis.stairs(expected[:,j]/width,pe,color=total_color,linestyle="--",linewidth=1.8)
        axis.errorbar((pe[:-1]+pe[1:])/2,observed/width,xerr=width/2,yerr=np.sqrt(observed)/width,
            fmt="o",markersize=3.6,capsize=1.8,color="#17232e",elinewidth=.9,zorder=5)
        axis.set(title=rf"$t_{{rec}}\in[{times[j]:g},{times[j+1]:g})\,\mu s$",xlim=(0,60),ylim=(0,None),xticks=[0,20,40,60])
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4,min_n_ticks=3));axis.grid(axis="y",alpha=.13)
        if j%4==0:axis.set_ylabel("Events / PE")
        if j>=8:axis.set_xlabel("PE")
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    slice_handles=[Patch(facecolor=steady_color,alpha=.2,label="SSB control model"),
        Patch(facecolor=neutron_color,alpha=.45,label="BRN + NIN (stacked)"),
        Patch(facecolor=sm_color,alpha=.16,label="Unfitted SM (stacked)"),
        Line2D([],[],color=sm_color,label="SM signal alone"),
        Line2D([],[],color=total_color,linestyle="--",label="SM + all backgrounds"),
        Line2D([],[],color="#17232e",marker="o",linestyle="none",label="Raw C data; sqrt(C) bars")]
    axes[11].axis("off");axes[11].legend(handles=slice_handles,loc="upper left",frameon=False,fontsize=9.0,handlelength=2.5)
    axes[11].text(.04,.08,"Layout target: De Romeri et al.\n2211.11905v2, Fig.18, p35.\nNo paper best-fit curve computed.",transform=axes[11].transAxes,fontsize=9,color="#7f4d3c",va="bottom",linespacing=1.5)
    fig.suptitle("CsI2021 raw-count time slices: unfitted local SM + backgrounds",fontsize=18,y=.99)
    fig.text(.055,.025,footer+"\nDensity per PE within each time window; not divided by window duration. No certified reproduction of Fig.18.",fontsize=8.8,color="#46586a")
    fig.subplots_adjust(left=.06,right=.98,top=.91,bottom=.13,hspace=.43,wspace=.29)
    save(fig,"sm_data_time_slices")

    # COHERENT Fig.1 subtracts SSB only; neutron backgrounds remain in the stack.
    ssb_residual=data["C_raw"]-data["SS_derived"]
    ssb_prediction=data["signal_counts"]+data["BRN_raw_template"]+data["NIN_raw_template"]
    fig,axes=plt.subplots(1,2,figsize=(13.8,6.4))
    for axis,name,edges,reduce_axis in [(axes[0],"PE",pe,1),(axes[1],"time",times,0)]:
        width=np.diff(edges);center=(edges[:-1]+edges[1:])/2
        source_components=flavors.sum(axis=reduce_axis+1)
        neutron=(data["BRN_raw_template"]+data["NIN_raw_template"]).sum(axis=reduce_axis)
        baseline=np.zeros_like(neutron)
        pieces=[neutron,source_components[0],source_components[2],source_components[1]]
        labels=["BRN + NIN, raw templates",r"$\nu_\mu$ CEvNS",r"$\bar\nu_\mu$ CEvNS",r"$\nu_e$ CEvNS"]
        for piece,label,color in zip(pieces,labels,["#c90de5","#aa855d","#ff974d","#ffe17a"]):
            top=baseline+piece
            axis.stairs(top/width,edges,baseline=baseline/width,fill=True,color=color,label=label)
            axis.stairs(top/width,edges,color="#29313a",linewidth=.7)
            baseline=top
        axis.errorbar(center,ssb_residual.sum(axis=reduce_axis)/width,xerr=width/2,
            yerr=np.sqrt(np.diag(projected_cov[name]))/width,fmt="o",color="#17232e",markersize=4.5,
            capsize=2,label="C - SSB (C+AC counting bars)",zorder=5)
        axis.axhline(0,color="#8b959d",linewidth=.8);axis.grid(axis="y",alpha=.13)
        axis.set(xlim=(edges[0],edges[-1]),xlabel="Reconstructed PE" if name=="PE" else r"Reconstructed time ($\mu$s)",
            ylabel="Excess events / PE" if name=="PE" else r"Excess events / $\mu$s",title=name+" projection: only SSB subtracted")
    axes[0].legend(frameon=False,fontsize=9.2,loc="upper right")
    fig.suptitle("CsI2021 SSB-subtracted projections: unfitted local SM + BRN/NIN",fontsize=16,y=.99)
    fig.text(.055,.035,footer+"\nDisplay target: COHERENT 2110.07730v2 Fig.1, p4 (paper shows best fit). Local SSB subtraction; no fit or rescaling.\n"
        "Bars: C+AC counting only; fixed control time shape. Time bins correlated. Neutron/model systematics excluded.",fontsize=8.8,color="#46586a")
    fig.subplots_adjust(left=.075,right=.98,top=.86,bottom=.25,wspace=.25)
    save(fig,"sm_data_ssb_subtracted")

    output_arrays={**data,"background_raw_diagnostic":background,"SM_plus_background_diagnostic":expected,
        "derived_signal_excess":excess,"C_sqrt_counting_error_only":np.sqrt(data["C_raw"]),
        "C_minus_SSB":ssb_residual,"SM_plus_BRN_NIN":ssb_prediction,
        "SM_nu_mu":flavors[0],"SM_nu_e":flavors[1],"SM_anti_nu_mu":flavors[2],
        "C_AC_counting_sigma_only":counting_sigma}
    np.savez_compressed(output/"comparison.npz",**output_arrays)
    np.savez_compressed(output/"counting_covariance.npz",AC_0_12us_PE_counts=ac12,SSB_time_probabilities=p_time,
        SSB_covariance=ss_cov,residual_C_AC_covariance=residual_cov,
        PE_residual_C_AC_covariance=projected_cov["PE"],time_residual_C_AC_covariance=projected_cov["time"])
    value_keys=list(output_arrays)[2:]

    def export_csv(file,columns,rows):
        with file.open("w",encoding="utf-8",newline="") as stream:
            writer=csv.writer(stream,lineterminator="\n");writer.writerow(columns);writer.writerows(rows)

    export_csv(output/"comparison_99bins.csv",["pe_low","pe_high","time_low_us","time_high_us",*value_keys],
        ([pe[i],pe[i+1],times[j],times[j+1],*[output_arrays[key][i,j] for key in value_keys]] for i in range(9) for j in range(11)))
    for name,edges,reduce_axis in [("PE",pe,1),("time",times,0)]:
        projections={key:output_arrays[key].sum(axis=reduce_axis) for key in value_keys
            if key not in ("C_sqrt_counting_error_only","C_AC_counting_sigma_only")}
        projections["C_sqrt_counting_error_only"]=np.sqrt(projections["C_raw"])
        projections["C_AC_counting_sigma_only"]=np.sqrt(np.diag(projected_cov[name]))
        export_csv(output/(name+"_comparison.csv"),[name+"_low",name+"_high",*value_keys],
            ([edges[i],edges[i+1],*[projections[key][i] for key in value_keys]] for i in range(len(edges)-1)))
    selected_sources=["S_MEAS","S_dataBeamOnC","S_dataBeamOnAC","S_SUP","S_brnPE","S_brnTrec","S_ninPE","S_ninTrec","S_PREPARE","S_2211"]
    totals={key:float(output_arrays[key].sum()) for key in value_keys
        if key not in ("C_sqrt_counting_error_only","C_AC_counting_sigma_only")}
    metadata={"date":args.date,"timezone":"Asia/Shanghai","scope":"Plot-only comparison of original official events and unchanged saved SM; no fit or new paper-equivalence claim",
        "source_run":str(run),"benchmark_sha256":sha(run/"benchmark.npz"),"source_validation_sha256":sha(run/"VALIDATION_RESULTS.json"),
        "source_plot_manifest_sha256":sha(run/"PLOT_MANIFEST.json"),"source_register_sha256":sha(base/"P00_SOURCE_REGISTER.yaml"),
        "sources":[sources[key] for key in selected_sources],"official_event_checks":raw_records,
        "benchmark_reference":{"source_id":"S_2211","paper":"V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP04(2023)035, arXiv:2211.11905v2",
            "figure":"Fig.18, PDF page35;11 CsI reconstructed-time windows","equations":"Eqs28-33, PDF pages12-13",
            "original_url":"https://arxiv.org/abs/2211.11905v2","scope":"Comparison target and layout, not a certified numerical reproduction of the paper curves"},
        "SSB_subtracted_reference":{"paper":"COHERENT Collaboration, arXiv:2110.07730v2, PRL129,081801(2022)",
            "figure":"Fig.1, PDF page4", "original_url":"https://arxiv.org/pdf/2110.07730v2#page=4",
            "definition":"Paper Data Residual subtracts SSB only; best-fit CEvNS and BRN/NIN remain in its stack",
            "local_scope":"Local nominal SSB and unfitted signal, not paper best-fit subtraction or curves"},
        "array_shape":[9,11],"axes":{"PE_edges":pe.tolist(),"time_edges_us":times.tolist(),"order":["PE","time"]},
        "counts_unit":"events/bin for NPZ and CSV; figures divide projections by actual bin width",
        "raw_data":"C_raw is the observed coincidence event count; AC_raw is a separate control sample, not extra observed signal",
        "SSB":"SS_derived from original AC model, as documented by C_SS in parent P01; not raw per-bin AC subtraction",
        "neutron_backgrounds":"Use saved raw templates unchanged; published18.4/5.6 priors are not used as rescaling targets",
        "error_bars":{"raw_C":"sqrt(C) counting variation only; symmetric display, not full detector/background/model uncertainty",
            "projection":"sqrt(sum C), not sum sqrt(C)",
            "derived_excess":"Partial C+AC Poisson counting bars; fixed SSB time shape and neutron templates; full systematics unresolved",
            "horizontal":"Half of actual bin width, not measurement uncertainty"},
        "derived_excess":"C_raw-SS_derived-BRN_raw_template-NIN_raw_template; preserve negative values; not an official independent signal measurement",
        "SM_plus_background":"signal_counts+SS_derived+BRN_raw_template+NIN_raw_template; diagnostic only",
        "SSB_only_subtraction":"C_minus_SSB compared to SM_plus_BRN_NIN; neutrons retained on both sides",
        "counting_covariance":{"derivation":"SS_ij=A_i*p_j; Cov(SS_ij,SS_kl)=delta_ik*A_i*p_j*p_l; add diag(C) for residual covariance",
            "flattening_order":"PE major, time minor (C order)","control_range_us":[0,12],"AC_events":int(ac12.sum()),
            "k_per_us":k,"k_source":"P01 C_TIME_EFF and C_SS; original fixed control model",
            "file":"counting_covariance.npz","fixed":"control time shape, neutron backgrounds, physical model",
            "omitted":"control shape uncertainty, neutron normalization and all signal/model systematics; no extra 2.1% pull added"},
        "totals":totals,"physics_runtime_or_inputs_modified":False,"posthoc_normalization":False,
        "total_prediction_minus_observed_events":float(expected.sum()-data["C_raw"].sum()),
        "code_files_checked_unchanged_during_plotting":len(state["files"]),
        "code_differences_from_20261107_snapshot":historical_code_differences,
        "direct_sources_rechecked":len(sources),
        "matplotlib":matplotlib.__version__,"numpy":np.__version__,"plot_script":{"path":str(Path(__file__).resolve()),"sha256":sha(__file__)},
        "plots":produced,"visual_QA":"PENDING"}
    write(output/"COMPARISON_RECORD.json",metadata)
    assert all(sha(ROOT/name)==value for name,value in code_before.items())
    write(output/"CHECKS.json",{"status":"PASS_NUMERICAL_INPUT_AND_EXPORT_CHECKS","date":args.date,
        "exact_official_rebin_matches":2,"raw_C_events":int(data["C_raw"].sum()),"raw_AC_events":int(data["AC_raw"].sum()),
        "all99_bins_and_2_projections":True,"original_SM_and_background_arrays_unchanged":True,
        "code_files_checked_unchanged_during_plotting":len(state["files"]),
        "code_differences_from_20261107_snapshot":historical_code_differences,"sources_rechecked":len(sources),
        "scope":"Existing stored prediction and actual official events; no new integration or statistical-fit validation"})
    print(json.dumps({"status":"PLOTTED","official_C_events":int(data["C_raw"].sum()),"SM_events":float(data["signal_counts"].sum()),"plots":len(produced),"output":str(output)}))


if __name__=="__main__":main()
