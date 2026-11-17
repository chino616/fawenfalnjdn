"""Export validated NSI arrays, provenance, readable reports and navigation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/"workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved"
DOCS = ROOT/"docs/experiments/COHERENT/CsI2021/time_resolved"
EXAMPLE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def link(label, target, folder, anchor=""):
    return "["+label+"](<"+Path(os.path.relpath(target,folder)).as_posix()+anchor+">)"


def epsilon_text(point):
    flavors = ["e","mu","tau"]
    values = []
    for q in ("u","d"):
        for i in range(3):
            for j in range(i,3):
                value = point["epsilon_"+q][i][j]
                if value != 0:
                    values.append(f"{q}:{flavors[i]},{flavors[j]}={value:.16g}")
    return "; ".join(values) if values else "all zero"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--refresh-reports",action="store_true",help="After preserving prior reports, regenerate without repeating parent navigation changes")
    args=parser.parse_args()
    run=args.run_dir.resolve()
    validation=read(run/"VALIDATION_RESULTS.json")
    assert validation["status"]=="PASS_DECLARED_NSI_FORWARD_POINTS"
    grid=run/validation["finest_grid"]
    report=read(grid/"report.json")
    points=read(run/"points.json")
    original=read(BASE/"sm_benchmark_20261107/SM_CONFIG.json")
    record=BASE/"nsi_benchmark_20261108"
    record.mkdir(exist_ok=True)
    with np.load(run/"benchmark.npz",allow_pickle=False) as source:
        data={key:source[key] for key in source.files}
    signal=data["signal_counts"]
    parts=data["target_component_counts"]
    sm=signal[0]
    pe,times=data["pe_edges"],data["time_edges_us"]
    point_sources={p["id"]:p["origin"] for p in points}
    input_record=BASE/"sm_benchmark_20261107/SM_CONFIG.json"
    config={"date":"2026-11-08","timezone":"Asia/Shanghai","route":"validation_only",
        "request":"用户选择先做NSI事例数与SM对照，未拟合",
        "scope":"24 declared real symmetric vector u/d NSI points; local Cs/I responses; no confidence intervals",
        "parent_SM_config":{"path":str(input_record),"sha256":sha(input_record)},
        "input_fields":original["input_fields"],
        "native_SM_LEFT_coefficients_GeV_minus2":original["native_SM_LEFT_coefficients_GeV_minus2"],
        "runtime_constants":original["runtime_constants"],"native_LECs_convention":original["native_LECs_convention"],
        "native_interaction":original["native_interaction"],
        "NSI_mapping":{"formula":report["mapping"],"source":report["mapping_source"],
            "GF_GeV_minus2":original["runtime_constants"]["G_F"]["value"],
            "literature":report["paper"],
            "derivation":"Project LEFT matching of the vector part of Eq5: epsilonV=epsilonL+epsilonR; quark PL/PR each contribute half the vector current. Transpose follows native [final,initial]. Real symmetric only."},
        "point_source":report["historical_coordinate_source"],"point_definitions":points,
        "integration":report["numerical_settings"],"basis_keys":report["basis_keys"],
        "time_contract":report["time_contract"],"normalization":report["normalization"],
        "model":report["model"],"legacy_time_files":report["legacy_time_files"],
        "response_sha256":report["response_sha256"],
        "driver_sha256":report["driver_sha256"],"coefficient_energy_checks":report["coefficient_energy_checks"],
        "unresolved_external_equivalence":"Parent r2 remains PARTIAL for strict paper reproduction; local resource reuse is the authorized direct input"}
    corner_source=Path(report["mapping_source"]["path"]).parents[1]/"tools/resolve_input_issues.py"
    config["supplemental_point_provenance"]={
        "legacy_u_corners":{"path":str(corner_source),"sha256":sha(corner_source),
            "locator":"precision_points, lines244-249, Cartesian product[-0.4,0.8]^2",
            "verification":"Actual legacy code read; coordinates exactly match the declared four current points"},
        "new_test_stimuli":{"path":str(EXAMPLE/"run_benchmark.py"),"sha256":sha(EXAMPLE/"run_benchmark.py"),
            "locator":"benchmark_points, explicit12-point entries; project-designed tests, not paper data"}}
    config["stored_coefficients"]="benchmark.npz coefficients_GeV_minus2 contains TOTAL native SM plus NSI matrices in basis order; subtract point0 for added NSI"
    write(run/"NSI_CONFIG.json",config)
    write(record/"NSI_CONFIG.json",config)
    rows=[]
    for i,p in enumerate(points):
        total=float(signal[i].sum())
        rows.append({"point_id":p["id"],"nonzero_epsilon_upper_triangle":epsilon_text(p),
            "signal_events":total,"SM_signal_events":float(sm.sum()),"ratio_to_SM":total/float(sm.sum()),
            "difference_from_SM_events":total-float(sm.sum()),
            "full_support_fluence_events":float(data["full_fluence_signal_counts"][i].sum()),
            "prompt_numu_events":float(parts[i,:,0].sum()),"delayed_nue_events":float(parts[i,:,1].sum()),
            "delayed_numubar_events":float(parts[i,:,2].sum()),"origin_kind":p["origin"]["kind"],
            "provenance":"NSI_CONFIG.json; points.json; DATA_DICTIONARY.json"})

    def csvfile(name,columns,records):
        with (run/name).open("w",encoding="utf-8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=columns,lineterminator="\n")
            writer.writeheader();writer.writerows(records)

    csvfile("summary.csv",list(rows[0]),rows)
    bins=[];components=[];energy_rows=[];time_rows=[]
    for i,p in enumerate(points):
        for j in range(9):
            current=float(signal[i,j].sum());reference=float(sm[j].sum())
            energy_rows.append(dict(point_id=p["id"],pe_bin=j,pe_low=float(pe[j]),pe_high=float(pe[j+1]),
                NSI_events=current,SM_events=reference,ratio=current/reference,difference_events=current-reference))
            for k in range(11):
                common=dict(point_id=p["id"],pe_bin=j,time_bin=k,pe_low=float(pe[j]),pe_high=float(pe[j+1]),
                    time_low_us=float(times[k]),time_high_us=float(times[k+1]))
                current=float(signal[i,j,k]);reference=float(sm[j,k])
                bins.append(dict(**common,NSI_events=current,SM_events=reference,ratio=current/reference,difference_events=current-reference))
                for it,target in enumerate(["Cs133","I127"]):
                    for ic,source in enumerate(["prompt_numu","delayed_nue","delayed_numubar"]):
                        components.append(dict(**common,target=target,source=source,events=float(parts[i,it,ic,j,k])))
        for k in range(11):
            current=float(signal[i,:,k].sum());reference=float(sm[:,k].sum())
            time_rows.append(dict(point_id=p["id"],time_bin=k,time_low_us=float(times[k]),time_high_us=float(times[k+1]),
                NSI_events=current,SM_events=reference,ratio=current/reference,difference_events=current-reference))
    for name,records in [("events_99bins.csv",bins),("components_99bins.csv",components),
            ("PE_projection.csv",energy_rows),("time_projection.csv",time_rows)]:
        csvfile(name,list(records[0]),records)
    dictionary={"date":"2026-11-08","all_counts":"Derived forward signal predictions in events/bin; not measured data or fitted predictions",
        "source_chain":["NSI_CONFIG.json input_fields and native constants","points.json per-point matrices and origins",
            validation["finest_grid"]+"/compiled_record.json","benchmark.npz","CSV projections and plots"],
        "axis_order":{"target":["Cs133","I127"],"source":["prompt_numu","delayed_nue","delayed_numubar"],
            "flavor":["e","mu","tau"],"point":[p["id"] for p in points],"PE_edges":pe.tolist(),"time_edges_us":times.tolist()},
        "bin_rule":"All bins left-closed/right-open; PE60 and time6 excluded, declared reconstructed PE boundaries",
        "NPZ":{key:{"shape":list(value.shape),"dtype":str(value.dtype)} for key,value in data.items()},
        "key_semantics":{"signal_counts":"(point,PE,time), sum of both targets and all3 incident source components",
            "target_component_counts":"(point,target,source,PE,time); time follows incident source after summing unobserved final flavor",
            "energy_before_time":"(point,target,source,PE), includes energy response/efficiency, exposure and target count exactly once",
            "channel_counts_before_time":"(point,target,source,response_channel,PE); native channel contributions may be signed, total signal is physical",
            "coefficients_GeV_minus2":"(point,4 operators,final,initial), TOTAL native SM+NSI from coefficient_values; subtract point0 to obtain the added NSI matrices",
            "full_fluence_signal_counts":"Same numerical eta interpreted as full-support fluence, not the primary normalization",
            "time_weights":"(source,time); zero-shift reference-window denominator; time efficiency already included",
            "full_time_weights":"(source,time); full-support fluence interpretation, time efficiency included"},
        "CSV":{"summary.csv":{"rows":len(rows),"counts":"All99 bins; exact nonzero eps upper triangle; offdiagonal reflected by symmetry"},
            "events_99bins.csv":{"rows":len(bins),"columns":"point,PE/time zero-based indices and boundaries,NSI,SM,ratio,delta"},
            "components_99bins.csv":{"rows":len(components),"columns":"point,bin coordinates,target,incident source,events"},
            "PE_projection.csv":{"rows":len(energy_rows),"operation":"sum time axis"},
            "time_projection.csv":{"rows":len(time_rows),"operation":"sum PE axis"}},
        "ratios":"NSI/SM with identical physical inputs and numerical grid; dimensionless; all denominators positive",
        "configuration_sha256":sha(run/"NSI_CONFIG.json"),"benchmark_sha256":sha(run/"benchmark.npz")}
    write(run/"DATA_DICTIONARY.json",dictionary)
    write(run/"RUN_SUMMARY.json",{"date":"2026-11-08","status":validation["status"],"points":rows,
        "units":"events for counts; epsilon and ratios dimensionless","point_sources":point_sources,
        "validation":validation,"strict_paper_reproduction":False})

    # Retain the failed numerical experiment; never overwrite it with PASS.
    if (run/"grid_512_960_axis_neutrino_energy/counts.npz").exists():
        with np.load(run/"grid_512_960/prediction.npz",allow_pickle=False) as z: prior=z["signal_counts"]
        failed=[]
        for axis in ("recoil","neutrino_energy","PE"):
            with np.load(run/("grid_512_960_axis_"+axis)/"counts.npz",allow_pickle=False) as z: coarse=z["parts"].sum(axis=(1,2))
            error=float(np.max(np.abs(prior-coarse)))
            failed.append({"axis":axis,"max_bin_error_events":error,"threshold":.005,"status":"PASS" if error<.005 else "FAIL"})
        write(run/"REJECTED_GRID_512_CHECKS.json",{"status":"FAIL_RETAINED","checks":failed,
            "resolution":"Independently re-evaluated at1024/1920/512/.03125; final grid and results in VALIDATION_RESULTS.json"})
    state=read(run/"SOURCE_STATE.json")
    assert all(sha(ROOT/name)==value for name,value in state["files"].items())
    resource={"date":"2026-11-08","status":"PASS_LOCAL_RESOURCE_REUSE",
        "source_code_files_unchanged":len(state["files"]),"response":{"path":"data/responses/responses_all.json",
            "sha256":sha(ROOT/"data/responses/responses_all.json"),"keys":["nuclei.Cs133","nuclei.I"],"external_generation_equivalence":"UNVERIFIED_OPTIONAL_FOR_LOCAL_REUSE"},
        "parent_register":{"path":str(BASE/"P00_SOURCE_REGISTER.yaml"),"sha256":sha(BASE/"P00_SOURCE_REGISTER.yaml")},
        "parent_evidence":{"path":str(BASE/"P01_EVIDENCE_LEDGER.yaml"),"sha256":sha(BASE/"P01_EVIDENCE_LEDGER.yaml")},
        "local_source_inventory":str(BASE/"data/nuclear_response_inventory.json"),
        "mapping_source":report["mapping_source"],"legacy_time_files":report["legacy_time_files"],
        "scope":"Fingerprints and availability, not independent certification of external source authenticity"}
    write(record/"RESOURCE_AUDIT.json",resource)
    test_root=ET.parse(run/"runtime-tests.xml").getroot()
    suites=list(test_root.iter("testsuite"))
    test_counts={key:sum(int(s.get(key,0)) for s in suites) for key in ("tests","failures","errors","skipped")}
    assert test_counts=={"tests":24,"failures":0,"errors":0,"skipped":0},test_counts
    native=read(run/"NATIVE_SLOW_CHECKS.json")

    def report_text(folder):
        L=lambda label,target,anchor="":link(label,target,folder,anchor)
        sections=[("scope","范围与实际计算链"),("inputs","沿用输入与直接来源"),("nsi","NSI定义与测试点"),
            ("counts","24个点的事例数"),("validation","数值验收与保留失败"),("figures","图和逐箱数据"),
            ("limits","限制与下一步输入"),("reproduce","复算与文件归属")]
        lines=["# CsI2021 时间分辨 NSI 事例数 benchmark","",
            "2026-11-08，Asia/Shanghai。**所列实对称u/d矢量NSI点的前向数值检查通过；严格论文复现仍为待核草稿。** 用户已选择先做未拟合事例数与SM对照。所有结果为信号预测，不是测量或参数区间。","",
            " · ".join([L("来源与配置",record/"NSI_CONFIG.json"),L("核资源审计",record/"RESOURCE_AUDIT.json"),
                L("机器验收",run/"VALIDATION_RESULTS.json"),L("参数矩阵",run/"points.json"),L("逐箱CSV",run/"events_99bins.csv"),
                L("数据字典",run/"DATA_DICTIONARY.json"),L("r2证据",BASE/"P01_EVIDENCE_LEDGER.yaml")]),"",
            '<a id="report-toc"></a>',"","## 目录","",*[f"- [{title}](#{identifier})" for identifier,title in sections],""]
        def section(key,text):
            lines.extend([f'<a id="{key}"></a>',"","## "+dict(sections)[key],"",text,"","[返回目录](#report-toc)",""])
        section("scope", "本轮走validation_only，消费既有r2输入与SM配置。主项目通用predict只支持一维观测：用既有compile_fast生成PE核，再调用既有reconstruct_channels和旧time_acceptance/time_profile生成9×11箱。核形状为(2核素,3入射分量,8响应通道,4算符,4算符,9PE箱)，结果为(24点,2核素,3入射分量,9PE箱,11时间箱)。未修改生产Runtime、核表或冻结参考；本轮工程核未作为正式P08冻结。\n\n"
            +L("计算入口",EXAMPLE/"run_benchmark.py")+" → "+L("主项目编译器",ROOT/"cevns_pyeft/kernels/compiler.py")+" → "+L("原生SM与RESPONSE",ROOT/"cevns_pyeft/theory/li2026/adapter.py")+"；时间权重的原目录和SHA见配置。最终态味求和后仍按入射源分量分配时间，不能把变成τ的末态重新分配成不存在的τ源。")
        adopted=["C_POT","C_YIELD","C_L","C_ETA","C_MASS","C_STOICH","C_MMU","C_MPI","C_LINE","C_ENDPOINT","C_SIN2_PAPER","C_QF","C_QF_DOMAIN","C_LY","C_GAMMA","C_EFF","C_TIME_EFF","C_PE","C_TIME","C_ENDPOINT_RULE","C_RESOURCE_BINDING","C_SOURCE_CHOICE","C_DENOM","C_RECOIL_POLICY"]
        text=["全部数值逐项沿用上一轮SM，未套用旧程序的拟合nuisance。完整常数、LEC和SM矩阵保存在本轮配置（直接实施来源为原代码；其外部逐项等价审计未完成）。以下每项的核验范围和来源SHA均随配置保留。","",
            "| 输入 | 采用值与单位 | 直接来源及定位 |","|---|---|---|"]
        for name in adopted:
            item=config["input_fields"][name]
            sources=" · ".join(L(source["source_id"],ROOT/source["uri_or_path"]) for source in item["direct_sources"])
            text.append("| "+item["field"]+" | "+json.dumps(item["value"],ensure_ascii=False)+" "+item["unit"]+" | "+sources+"；"+item["locator"]+" |")
        text.extend(["","核结构直接采用用户指定的 "+L("原responses_all.json",ROOT/"data/responses/responses_all.json")+"，SHA256 `"+config["response_sha256"]+"`。读取器按(p,n)行列和升幂系数使用数组；q为GeV、b为GeV⁻¹、y=(qb/2)²，指数因子−2，系数无量纲。外部作者生成链未核实；本次原表复用有用户明确选择。完整16个数组见 "+L("逐值NPZ",BASE/"data/nuclear_response_CsI.npz")+"；以下示例和shape直接回读原JSON。","",
            "| 核素 | 实际核表与代表值 | 通道和完整资源 |","|---|---|---|"])
        response=read(ROOT/"data/responses/responses_all.json")
        for target in ("Cs133","I"):
            entry=response["nuclei"][target]
            shapes={name:list(np.asarray(a).shape) for name,a in entry["responses"].items()}
            text.append(f"| {target} | b={entry['basic']['b']:.15g} GeV⁻¹；M_pp系数前三项={entry['responses']['M'][0][0][:3]} | "+json.dumps(shapes)+"；"+L("逐数组定位和归一化",BASE/"data/nuclear_response_inventory.json")+" |")
        text.extend(["","核数沿用当前模型：Cs133、I127各约3.38166366×10²⁵；质量和核计数算法见 "+L("归一化台账",BASE/"sm_benchmark_20261107/NORMALIZATION_LEDGER.json")+"。未另加Helm、核半径修正、曝光或acceptance。官方ROOT原始网址和对象/轴域已在 "+L("P00来源",BASE/"P00_SOURCE_REGISTER.yaml")+" 与 "+L("ROOT实际数组目录",BASE/"data/ROOT_inventory.json")+" 中保留；本轮只采用其三主味时间边缘，能谱用2211 Eq.(29)解析DAR。"])
        section("inputs","\n".join(text))
        gf=config["NSI_mapping"]["GF_GeV_minus2"]
        mapping_path=Path(report["mapping_source"]["path"])
        text=["文献基准为V. De Romeri et al., *Physics implications of a combined analysis of COHERENT CsI and LAr data*, JHEP04(2023)035，"+L("2211.11905v2本地PDF",ROOT/"docs/references/COHERENT/2211.11905v2.pdf")+"，[原始网址](https://arxiv.org/abs/2211.11905v2)，PDF第5页Sec.2.2、式(5)–(6)。它给出矢量NSI定义；不提供本轮24点的预期事件表。","",
            "本轮调用 "+L("旧程序vector_nsi_wilson",mapping_path)+"，将上述定义与项目LEFT约定匹配（项目转换关系，非论文原样公式）：","",
            "$$",r"\Delta C_{61q}[f,i]=-\sqrt{2}\,G_F(\epsilon^{qV})^{\mathsf T}[f,i],\qquad q=u,d.\tag{1}","$$","",
            "| 符号/配置 | 实际值、单位及直接来源 |","|---|---|",
            "| ε | 实对称3×3无量纲矩阵，味顺序(e,μ,τ)；"+L("points.json全部矩阵",run/"points.json")+"。上三角以对称方式复制到下三角，其余为0 |",
            f"| G_F | {gf:.12g} GeV⁻²；"+L("项目常数",ROOT/"cevns_pyeft/foundation/constants.py")+"，运行时SciPy常数表；原SM配置保存实际解析值和来源范围 |",
            "| ΔC61q | 额外NSI项，GeV⁻²，原生算符(6,1,u/d)，矩阵轴[final,initial]；NPZ coefficients_GeV_minus2存储的是SM+NSI总矩阵，减去point0矩阵才是ΔC |",
            "| SM | include_sm=True，保留原SM vector/axial；仅叠加NSI vector。编译基底为(6,1,u),(6,1,d),(6,2,u),(6,2,d) |","",
            "因εV=εL+εR且夸克PL/PR各含1/2矢量流，项目采用−√2GF。实对称范围内转置数值不变；当前检查不认证一般复数相位或非矢量EFT。","",
            "前8点只取 "+L("旧benchmark_points.json",Path(report["historical_coordinate_source"]["path"]))+" 的name/point字段，逐行定位见points.json；不采用旧χ²或拟合nuisance。旧scan_branch坐标只作历史诊断点，不标为本轮或论文最佳拟合。4个u对角边角为项目精度域选择(−0.4或0.8)²，直接位置为 "+L("旧precision_points",corner_source)+" 第244–249行；其余12点为本轮run_benchmark.py::benchmark_points明确设计的有限测试刺激，均非文献测量。两组的直接代码SHA和定位也存入NSI_CONFIG。"]
        section("nsi","\n".join(text))
        text=[f"主约定：零平移0–6μs参考窗注量，PE∈[0,60)、t_rec∈[0,6)μs。最细网格SM为 **{float(sm.sum()):.9f} events**；相同数值eta改作全支撑域注量时为 **{float(data['full_fluence_signal_counts'][0].sum()):.9f} events**。两种注量含义分别保存，不能混用。","",
            "下表ε只列上三角非零值；非对角元素均含对称伴项，未列项为0。完整有效位数、来源kind、Cs/I与各入射味总数见 "+L("summary.csv",run/"summary.csv")+" 和 "+L("points.json",run/"points.json")+"。","",
            "| 点 | 非零ε（无量纲） | 信号事例 | NSI/SM | ΔN |","|---|---|---:|---:|---:|"]
        for row in rows:
            text.append(f"| {row['point_id']} | {row['nonzero_epsilon_upper_triangle']} | {row['signal_events']:.6f} | {row['ratio_to_SM']:.6f} | {row['difference_from_SM_events']:+.6f} |")
        text.extend(["","μ对角正耦合在约0.2处明显压低μ源贡献；eμ非对角±号给出相同增量，eτ仅改变νe入射项，μτ仅改变νμ/反νμ项；ττ对角在无τ源时恢复SM。以上是当前原生模型的计算行为，不能替代实验约束。"])
        section("counts","\n".join(text))
        refinement=next(c for c in validation["checks"] if c["name"]=="all24_NSI_points_grid_refinement")
        independent=next(c for c in validation["checks"] if c["name"]=="independent_recoil_energy_PE_precision_all24_points")
        text=["| 检查 | 实际结果与范围 |","|---|---|",
            f"| 原始Slow对照 | 全24点，16/40 pilot网格；最大核素/源/箱差异{native['max_native_bin_error']:.8g} events。仅证明同网格方法等价，pilot不作精度冻结 |",
            "| 原始系数能量求值对照 | pilot与256/480同网格全24点最大差异4.97379915×10⁻¹⁴ events；"+L("逐项记录",run/"COEFFICIENT_ENERGY_EQUIVALENCE.json")+" |",
            "| 最终网格 | "+json.dumps(validation["settings"])+"；QF下限2keVnr，运动学端点不变 |",
            f"| 整体加密 | {refinement['previous_grid']}→{refinement['current_grid']}；全24点最大总信号箱误差{refinement['total']['max_bin_difference_events']:.9g}，分量箱误差{refinement['components']['max_bin_difference_events']:.9g} events |"]
        for entry in independent["axes"]:
            text.append(f"| 独立{entry['axis']}积分 | 全24点最大总箱差{entry['total']['max_bin_difference_events']:.9g}，分量箱差{entry['components']['max_bin_difference_events']:.9g} events；均<0.005 |")
        text.extend([f"| Runtime回归 | {test_counts['tests']}项通过，0失败；"+L("JUnit",run/"runtime-tests.xml")+"、"+L("实际日志",run/"runtime-tests.log")+" |",
            f"| 输入保护 | {len(state['files'])}个原package/helper Python文件未变；原响应与P00指纹审计见资源记录 |","",
            "保留未通过项：512/960网格在最强u对角角点的独立Eν检查为0.00514593365 events/bin，超过0.005；"+L("失败记录",run/"REJECTED_GRID_512_CHECKS.json")+"和原网格均保留。此次通过来自加密积分，没有放宽门限。","",
            "仅对所列24点验收，未验证连续参数域。为控制运行时间，本轮消费者对四个dim6算符的E²H(E)作二次重构，每个反冲用3个原生定义点与4个原生holdout（含两端点）逐张量检验，rtol=2×10⁻¹⁰、atol=2×10⁻¹²；失败就回到原始能量数组。原始Slow不使用此捷径；生产编译器未改。检查统计与代码SHA在配置内。"])
        section("validation","\n".join(text))
        section("figures", "图中仅画信号；分箱宽度不相同，PE和时间投影分别除以真实ΔPE和Δt。曲线是本次计算，不是论文数字化或拟合结果。图注与 "+L("PLOT_MANIFEST",run/"PLOT_MANIFEST.json")+" 连接输入、点定义与生成代码。\n\n"
            +"![NSI与SM投影](<"+Path(os.path.relpath(run/"figures/nsi_sm_projections.png",folder)).as_posix()+">)\n\n"
            +L("11个时间窗PNG",run/"figures/nsi_time_slices.png")+" · "+L("味分量变化PNG",run/"figures/nsi_flavor_changes.png")+" · "+L("矢量图SVG",run/"figures/nsi_sm_projections.svg")+"\n\n"
            +L("99箱比较CSV",run/"events_99bins.csv")+"（24×99行） · "+L("核素/源逐箱CSV",run/"components_99bins.csv")+"（24×2×3×99行） · "+L("PE投影",run/"PE_projection.csv")+" · "+L("时间投影",run/"time_projection.csv")+" · "+L("全部NPZ",run/"benchmark.npz")+"。轴、单位、列定义、归一化与来源链见数据字典。")
        section("limits", "本轮已具备所列实对称矢量NSI点的未拟合信号预测和SM对照。BRN/NIN未缩放到18.4/5.6，本轮不使用背景、不计算likelihood。原生SM含axial/RESPONSE，尚未与论文辐射修正/Helm逐项等价，不能据此宣布严格复现2211图或官方统计。原表外部导出链继续未核，按用户选择直接复用本地data。PE边界保留为用户指定重建值，不升级为官方原始发布边界。\n\n"
            "| 下一步能力 | 仍需信息或审查 | 当前可执行范围 |\n|---|---|---|\n"
            "| 更多未拟合实对称u/d NSI点 | 明确矩阵；每点重跑同一精度检查 | 可沿本轮链计算，不能默认域内已全验收 |\n"
            "| 统计拟合/区间 | BRN/NIN的曝光、效率、时间归一与18.4/5.6的物理闭合；nuisance域、非负约束、阈值/分支 | 尚未执行，本轮不提供约束 |\n"
            "| 严格2211论文benchmark | 独立Helm/辐射修正配置，论文参考逐箱曲线及可核验误差，时间零点与核半径处理 | 继续待补，不由本轮数值PASS认证 |\n"
            "| 完整ROOT能量—时间模型 | 对照联合分布与当前DAR×时间边缘的逐箱差异，并审阅适用源选择 | 当前采用既定因子化源，未宣称ROOT二维相关被保留 |\n"
            "| 一般复数/非矢量EFT或正式Fast冻结 | 对应理论与能力合同、独立Slow、参数域和人工审查 | 本轮不覆盖 |\n\n"
            +L("r2全部缺口",BASE/"P02_MISSING_AND_CONFLICTS.md")+"保留原状态；本轮不改写此前背景与论文等价问题。")
        section("reproduce", "以下命令从主项目根执行，默认时间/NSI模块位于Gitup01的examples/COHERENT_CsI/time_resolved_common，24点坐标来自项目内最新输入。需numpy/scipy，原文/ROOT指纹回读还需PyYAML/uproot；绘图需matplotlib。为保留旧结果，RUN使用新目录。实际Python、依赖与命令另见本次运行环境记录。\n\n"
            "```powershell\npython -B examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py --output-dir RUN/pilot --n-er 16 --n-enu 40 --n-pe-bin 12 --pe-step 2\n# 原生和checked pilot、256/480、512/960及最终1024/1920各独立目录；完整顺序见示例README\npython -B examples/COHERENT_CsI/time_resolved_nsi/validate_benchmark.py --run-dir RUN --stage native\npython -B examples/COHERENT_CsI/time_resolved_nsi/validate_benchmark.py --run-dir RUN --stage precision --finest grid_1024_1920\npython -B examples/COHERENT_CsI/time_resolved_nsi/summarize_benchmark.py --run-dir RUN\npython -B examples/COHERENT_CsI/time_resolved_nsi/plot_benchmark.py --run-dir RUN\n```\n\n"
            +L("示例与可复算代码",EXAMPLE/"README.md")+" · "+L("本轮完整输出",run/"README.md")+" · "+L("主线计算记录",record/"README.md")+" · "+L("之前SM报告",DOCS/"SM_BENCHMARK.md")+"。所有report副本从本脚本同源生成，路径按输出位置调整。")
        return "\n".join(lines)

    for destination in (DOCS/"NSI_BENCHMARK.md",run/"BENCHMARK.md",record/"08_NSI_FORWARD_BENCHMARK_REPORT.md"):
        if destination.exists() and not args.refresh_reports: raise FileExistsError("Preserve previous report before regenerating: "+str(destination))
        destination.write_text(report_text(destination.parent),encoding="utf-8",newline="\n")
    if args.refresh_reports:
        print(json.dumps({"status":"REPORTS_REFRESHED","points":len(points),"SM_events":float(sm.sum())}))
        return
    # Navigation changes use fresh exact-path backups, separate from scientific input.
    changes={
        ROOT/"examples/COHERENT_CsI/README.md":"\n[时间分辨NSI事例数示例](time_resolved_nsi/README.md)延续同一SM输入，检验24个实对称u/d矢量NSI点，提供未拟合99箱和SM对照；未作参数约束。\n",
        ROOT/"outputs/README.md":"\n## CsI2021 NSI事例数（2026-11-08）\n\n[csi2021_time_nsi_20261108/](csi2021_time_nsi_20261108/README.md)保存24个矢量NSI点、SM对照、原生Slow核对、积分加密、来源与图表；严格论文复现和拟合另保留限制。\n",
        BASE/"README.md":"\n2026-11-08的[NSI前向事例数基准](nsi_benchmark_20261108/README.md)沿用SM输入，按用户选项只做24个实对称u/d矢量NSI点与SM的比较；本轮核查不改变r2缺口或正式Fast/统计阶段状态。\n",
        DOCS/"README.md":"\n[NSI事例数与SM对照（2026-11-08）](NSI_BENCHMARK.md)保存24个有限测试点的未拟合信号、逐箱对照和精度验收；各点来源与当前不能认证的论文/统计主张明确保留。\n"}
    backup=ROOT/"backup/csi-nsi-benchmark-20261108-02"
    if backup.exists(): raise FileExistsError("Choose a fresh backup revision")
    backed=[]
    for target,addition in changes.items():
        relative=target.relative_to(ROOT)
        preserved=backup/relative
        preserved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(target,preserved)
        backed.append({"path":relative.as_posix(),"sha256":sha(target),"backup":preserved.relative_to(ROOT).as_posix()})
    write(backup/"MANIFEST.json",{"date":"2026-11-08","reason":"NSI benchmark parent navigation, before changes","files":backed})
    with (ROOT/"backup/BACKUP_MANIFEST.md").open("a",encoding="utf-8") as stream:
        stream.write("\n- 2026-11-08 NSI benchmark navigation: [exact-path manifest](csi-nsi-benchmark-20261108-02/MANIFEST.json), four parent README snapshots before changes.\n")
    for target,addition in changes.items():
        target.write_text(target.read_text(encoding="utf-8").rstrip()+"\n"+addition,encoding="utf-8")
    write(record/"NAVIGATION_CHANGES.json",{"backups":backed,"scope":"Four existing parent READMEs only; no original physics change"})
    print(json.dumps({"status":"EXPORTED","points":len(points),"SM_events":float(sm.sum()),"csv_rows":len(bins),"report_copies":3}))


if __name__=="__main__":main()
