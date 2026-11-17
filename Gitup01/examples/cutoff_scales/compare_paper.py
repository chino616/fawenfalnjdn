"""Quantify Fig3 graphical differences without refitting or retuning inputs."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, new_run, read, sha, write_json
from run_joint import OLD_DIM6, OLD_FULL, MAIN_GROUPS, verify_sources

REFERENCE = "outputs/paper2601_chi2_corrected_20261111/paper_reference"
PAPER = "docs/references/General_CEvNS/2601.19883v2.pdf"
MAP = {"CONUS_plus": "CONUS_plus", "CsI2021_9PE+Ar2020_average": "COHERENT_CsI_Ar",
       "Solar_three_singlebins": "Solar_joint"}


def paper_operator(key):
    d, i, q = key
    return f"O{d}{q}_{i}"


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def compare(output, joint_path):
    output = new_run(output)
    joint_path = Path(joint_path).resolve()
    joint = read((joint_path/"RESULTS.json").relative_to(ROOT).as_posix())
    verify_sources(joint)
    reference_path = ROOT/REFERENCE/"fig3_plotted_limits.csv"
    with reference_path.open(encoding="utf-8-sig", newline="") as f:
        reference = {(r["experiment"], r["operator"]): r for r in csv.DictReader(f)}
    records = {"dim6_self_consistent": read(OLD_DIM6+"/RESULTS.json"),
               "full22_fixed_SM_control": read(OLD_FULL+"/RESULTS.json")}
    rows, sources = [], {}
    for version, record in records.items():
        verify_sources(record)
        for result in record["results"]:
            group = result["analysis_group"]
            if group not in MAIN_GROUPS:
                continue
            key = result["operator_key"]
            ref = reference[MAP[group], paper_operator(key)]
            paper = float(ref["lambda_GeV_from_plotted_height"])
            local = result["confidence"]["90"]["global_GeV"]
            flags = ["graphical_reference_not_author_likelihood", "local_input_and_likelihood_equivalence_unresolved"]
            if version.startswith("full22") and group == "Solar_three_singlebins":
                flags.append("fixed_SM_solar_state_control")
            if result["flavor"] != "ee":
                flags.append("explicit_e_mu_transition_not_certified_paper_flavor_equivalence")
            if key[0] == 8:
                flags.append("pointwise_PSD_validation_unresolved_control_only")
            row = {"version": version, "analysis_group": group, "operator": result["operator_id"],
                   "paper_operator": paper_operator(key), "dimension": key[0], "flavor": result["flavor"],
                   "local_90CL_GeV": local, "paper_fig3_90CL_GeV": paper,
                   "difference_GeV": local-paper, "ratio_local_over_paper": local/paper,
                   "relative_difference_percent": 100*(local/paper-1),
                   "comparison_status": ";".join(flags)}
            rows.append(row)
        directory = OLD_DIM6 if version.startswith("dim6") else OLD_FULL
        for f in ("RESULTS.json", "SOURCE_MANIFEST.json"):
            p = directory+"/"+f; sources[p] = sha(ROOT/p)
    full = [r for r in rows if r["version"].startswith("full22")]
    dim6 = [r for r in rows if r["version"].startswith("dim6")]
    assert len(full) == 66 and len(dim6) == 10
    summary = {}
    for group in MAIN_GROUPS:
        selected = [r for r in full if r["analysis_group"]==group]
        differences = np.array([r["relative_difference_percent"] for r in selected])
        summary[group] = {"count": len(selected), "signed_range_percent": [differences.min(), differences.max()],
                          "median_absolute_percent": np.median(abs(differences)),
                          "within_1_percent": int(np.sum(abs(differences)<=1)),
                          "within_5_percent": int(np.sum(abs(differences)<=5)),
                          "beyond_20_percent": int(np.sum(abs(differences)>20)),
                          "largest_differences": sorted(selected, key=lambda r: abs(r["relative_difference_percent"]), reverse=True)[:5]}
    solar_propagation = []
    for q in ("u", "d"):
        op = "C6"+q+"1"
        a = next(r for r in dim6 if r["operator"]==op and r["analysis_group"]=="Solar_three_singlebins")
        b = next(r for r in full if r["operator"]==op and r["analysis_group"]=="Solar_three_singlebins")
        solar_propagation.append({"operator": op, "self_consistent_GeV": a["local_90CL_GeV"],
                                  "fixed_SM_control_GeV": b["local_90CL_GeV"],
                                  "relative_difference_percent": 100*(a["local_90CL_GeV"]/b["local_90CL_GeV"]-1),
                                  "interpretation": "difference between adopted self-consistent dim6 and rebuilt fixed-SM control, includes forward integration version differences"})
    joint_rows = []
    for r in joint["results"]:
        version = r["version"]
        individual = [a for a in rows if a["version"]==version and a["operator"]==r["operator_id"]]
        strongest = max(a["local_90CL_GeV"] for a in individual)
        value = r["confidence"]["90"]["global_GeV"]
        joint_rows.append({"version": version, "operator": r["operator_id"],
                           "joint_90CL_GeV": value, "strongest_individual_90CL_GeV": strongest,
                           "joint_relative_to_strongest_percent": 100*(value/strongest-1),
                           "chi2_joint_min": r["chi2_min"], "delta_chi2_SM": r["delta_chi2_SM"],
                           "compatibility_cost_not_pvalue": r["compatibility_cost_no_calibrated_pvalue"],
                           "physical_validation_status": r["physical_validation_status"]})
    for p in (REFERENCE+"/fig3_plotted_limits.csv", REFERENCE+"/PROVENANCE.json", PAPER):
        sources[p] = sha(ROOT/p)
    sources[(joint_path/"RESULTS.json").relative_to(ROOT).as_posix()] = sha(joint_path/"RESULTS.json")
    sources[(HERE/"compare_paper.py").relative_to(ROOT).as_posix()] = sha(HERE/"compare_paper.py")
    write_csv(output/"PAPER_COMPARISON_FULL22.csv", full)
    write_csv(output/"PAPER_COMPARISON_DIM6.csv", dim6)
    write_csv(output/"JOINT_VS_INDIVIDUAL.csv", joint_rows)
    write_json(output/"COMPARISON.json", {"schema": SCHEMA, "part_id": PART, "run_id": output.name,
        "stage": "GRAPHICAL_PAPER_COMPARISON_AND_JOINT_SUMMARY", "rows": rows, "full22_summary": summary,
        "solar_propagation_comparison": solar_propagation, "joint_comparison": joint_rows,
        "paper_reference_contract": "2601.19883v2 PDF p22 Fig3 vector bar heights mapped on log axis; not exact author coefficient limits or chi2 grids; small numerical ratios are graphical comparisons, not agreement precision",
        "source_manifest": sources, "joint_run": joint_path.relative_to(ROOT).as_posix()})
    write_json(output/"SOURCE_MANIFEST.json", sources)
    lines = ["# 论文Fig.3逐算符数值比较与三组联合分析", "",
             "[完整22×3比较表](PAPER_COMPARISON_FULL22.csv) · [dim-6主版本比较表](PAPER_COMPARISON_DIM6.csv) · "
             "[联合相对单组](JOINT_VS_INDIVIDUAL.csv) · [机器记录](COMPARISON.json) · [来源](SOURCE_MANIFEST.json)", "",
             "论文参考是本地2601.19883v2 PDF第22页Fig.3的矢量柱顶几何；不是作者精确数值或原始χ²。"
             "差异=(本地/论文−1)×100%。所有90%阈值为2.71，|g|=1；没有为了对齐论文重调输入或系数。", "",
             "## dim-6主版本", "", "| 组 | 算符 | 本地/GeV | 论文图/GeV | 相对差异 |", "|---|---|---:|---:|---:|"]
    for r in dim6:
        lines.append(f"| {r['analysis_group']} | {r['operator']} | {r['local_90CL_GeV']:.4f} | {r['paper_fig3_90CL_GeV']:.4f} | {r['relative_difference_percent']:+.2f}% |")
    lines += ["", "## 完整22算符控制版本", "", "| 组 | 绝对差异中位数 | 5%以内/22 | 超过20%/22 | 差异范围 |", "|---|---:|---:|---:|---:|"]
    for name, s in summary.items():
        a,b=s["signed_range_percent"]
        lines.append(f"| {name} | {s['median_absolute_percent']:.2f}% | {s['within_5_percent']} | {s['beyond_20_percent']} | {a:+.2f}% 至 {b:+.2f}% |")
    lines += ["", "控制版不满足整套复现：各组完整表保留方向和幅度，不能只展示吻合的矢量柱。"
              "LNV采用本地e↔μ矩阵，尚未认证论文初末味/归一化等价；太阳全22固定SM态，dim-8有已记录的原生点PSD拒绝。"
              "其他高维差异尚未被逐项隔离到某一输入或核响应，不能仅归因于读图精度，也不能断言只是统计不同。", "",
              "## 三组联合", "", "| 版本 | 算符 | 联合90%/GeV | 最强单组/GeV | 相对变化 | χ²min |", "|---|---|---:|---:|---:|---:|"]
    for r in joint_rows:
        lines.append(f"| {r['version']} | {r['operator']} | {r['joint_90CL_GeV']:.4f} | {r['strongest_individual_90CL_GeV']:.4f} | {r['joint_relative_to_strongest_percent']:+.2f}% | {r['chi2_joint_min']:.8f} |")
    lines += ["", "6份底层观测只各计一次，43个观测、8个独立nuisance；共同系数c保持相同物理单位。"
              "总χ²先相加再求自己的最小值，不相加各自Δχ²。各自最佳点不一致时，联合下限不保证高于每个单组；"
              "这里的compatibility cost=联合最小值−三个单组最小值之和，只作代数诊断，不转成显著性。"
              "未认证跨实验共享核响应、通量等协方差；弱角保留原主线CONUS/solar=0.23857、CsI/Ar=0.2387。", "",
              "太阳主版本与固定SM控制的矢量差异："]
    for r in solar_propagation:
        lines.append(f"- {r['operator']}: {r['self_consistent_GeV']:.4f} vs {r['fixed_SM_control_GeV']:.4f} GeV ({r['relative_difference_percent']:+.2f}%)；包含两套前向积分版本差别，非纯传播开关实验。")
    lines += ["", "[返回独立Part](../../../examples/cutoff_scales/README.md) · [联合计算](../"+joint_path.name+"/README.md)", ""]
    (output/"README.md").write_text("\n".join(lines), encoding="utf-8")
    print("WROTE", output, "full22 rows", len(full), "dim6 rows", len(dim6), flush=True)
    for name, s in summary.items():
        print(name, "median abs percent", s["median_absolute_percent"], "within5",s["within_5_percent"], "over20",s["beyond_20_percent"], flush=True)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--joint",type=Path,required=True)
    a=p.parse_args(); compare(a.output,a.joint)
