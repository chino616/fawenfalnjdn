"""Write the same benchmark/configuration/evidence into reviewable reports."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from examples.COHERENT_CsI.time_resolved_common import sm_support as driver
from cevns_pyeft.foundation import constants
from cevns_pyeft.rates.differential import _sm_left_dim6


def link(label, target, current):
    return f'[{label}](<{os.path.relpath(target, current.parent).replace(chr(92), "/")}>)'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--legacy-time-dir", type=Path, default=driver.LOCAL_TIME, help="Local adopted time/mapping modules; optional explicit compatibility override")
    parser.add_argument("--record-dir", type=Path, help="Explicit review destination; defaults to run-dir/review_records")
    parser.add_argument("--update-main-doc", action="store_true", help="Also write the explicit main-project SM reading document")
    parser.add_argument("--overwrite-review", action="store_true", help="Regenerate existing review metadata/reports, never numerical inputs")
    parser.add_argument("--visual-reviewed", action="store_true")
    args = parser.parse_args()
    root = driver.ROOT
    run = args.run_dir.resolve()
    onboarding = root / "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved"
    record = args.record_dir.resolve() if args.record_dir else run / "review_records"
    record.mkdir(exist_ok=True)
    if not args.overwrite_review and any((record / name).exists() for name in ("SM_CONFIG.json", "NORMALIZATION_LEDGER.json", "RESOURCE_AUDIT.json", "07_SM_FORWARD_BENCHMARK_REPORT.md")):
        parser.error("Review records exist; choose another directory or explicitly use --overwrite-review")
    claims, register = driver.inputs(onboarding)
    sources = {source["source_id"]: source for source in register["sources"]}
    validation = json.loads((run / "VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    grid_report = json.loads((run / "grid_512_960/report.json").read_text(encoding="utf-8"))
    plot = json.loads((run / "PLOT_MANIFEST.json").read_text(encoding="utf-8"))
    with np.load(run / "benchmark.npz", allow_pickle=False) as data:
        arrays = {key: data[key] for key in data.files}
    assert validation["status"] == "PASS_SM_FORWARD_NUMERICAL_CHECKS"
    tests = ET.parse(run / "runtime-tests.xml")
    suites = list(tests.iter("testsuite"))
    test_summary = {key: sum(int(suite.attrib.get(key, 0)) for suite in suites) for key in ("tests", "failures", "errors", "skipped")}
    assert test_summary["failures"] == test_summary["errors"] == 0
    if args.visual_reviewed:
        for item in plot["plots"]:
            assert driver.sha(run / item["path"]) == item["sha256"]
        plot["visual_QA"] = "PASS"
        plot["visual_review_scope"] = "Three PNG figures inspected with view_image: axes, units, unequal bins, legend, captions, no clipping; SVG generated from the same figures"
        driver.write_json(run / "PLOT_MANIFEST.json", plot)
    adopted = ["C_POT", "C_YIELD", "C_L", "C_ETA", "C_MASS", "C_STOICH", "C_MMU", "C_MPI", "C_LINE", "C_ENDPOINT",
        "C_SIN2_PAPER", "C_QF", "C_QF_DOMAIN", "C_LY", "C_GAMMA", "C_EFF", "C_TIME_EFF", "C_PE", "C_TIME",
        "C_ENDPOINT_RULE", "C_RESOURCE_BINDING", "C_SOURCE_CHOICE", "C_DENOM", "C_RECOIL_POLICY", "C_PRIORS"]
    fields = {}
    for key in adopted:
        claim = claims[key]
        fields[key] = {name: claim[name] for name in ("field", "value", "unit", "locator", "status", "adoption", "verification_scope")}
        fields[key]["direct_sources"] = [{name: sources[source_id].get(name) for name in
            ("source_id", "citation", "uri_or_path", "original_url", "sha256", "verification_scope")} for source_id in claim["source_ids"]]
    native_parameters = grid_report["model"]["interaction"]["parameters"]
    native = native_parameters.get("original", grid_report["model"]["interaction"])
    config = {"date": "2026-11-07", "timezone": "Asia/Shanghai", "route": "validation_only",
        "request": "先以标准模型作为benchmark，对事例数图进行计算，按照已有项目流程",
        "scope": "One nominal pure-SM forward point; no nuisance minimization, no BSM scan and no scientific Slow freeze",
        "dataset_analysis": "CsI2021_time_9x11", "onboarding_revision": register["revision"],
        "main_project": str(root), "source_record": str(onboarding / "P00_SOURCE_REGISTER.yaml"),
        "input_fields": fields, "TheoryPoint": grid_report["model"]["theory_point"],
        "native_interaction": native,
        "native_SM_LEFT_coefficients_GeV_minus2": {str(key): value.real.tolist() for key, value in _sm_left_dim6(True, fields["C_SIN2_PAPER"]["value"]).items()},
        "native_SM_definition": {"direct_source": "cevns_pyeft/rates/differential.py::_sm_left_dim6",
            "contains": "native vector and axial terms; not the paper's independently radiatively corrected Helm prescription",
            "original_paper_equivalence": "NOT_CERTIFIED"},
        "runtime_constants": {key: {"value": float(getattr(constants, key)), "unit": unit,
            "direct_source": "cevns_pyeft/foundation/constants.py"} for key, unit in
            [("G_F", "GeV^-2"), ("AMU_GEV", "GeV"), ("m_p", "GeV"), ("m_n", "GeV"), ("m_e", "GeV"), ("m_mu", "GeV")]},
        "native_LECs_convention": "Full actual values and declared conventions are preserved in native_interaction.parameters.lecs; direct source theory/li2026/lec.py. External formula/source correspondence remains the r2 theory audit limitation.",
        "integration": grid_report["numeric_settings"], "time_contract": grid_report["time_contract"],
        "P06_evaluation": grid_report["P06_response_evaluation"], "SM_evaluation": grid_report["checked_SM_diagnostics"],
        "legacy_time_directory": str(args.legacy_time_dir.resolve()), "legacy_time_files": grid_report["legacy_time_files"],
        "background_mode": "raw_template_integrals; probability normalization alternative saved separately; no matching to priors",
        "data_errorbar_definition": "sqrt(C_raw)/PE_width, display only; not a likelihood or confidence interval"}
    driver.write_json(record / "SM_CONFIG.json", config)
    normalization = {"route": "integrated detector fluence cm^-2 times per-nucleus differential cross section cm^2/keVnr times dT times nucleus count times accepted PE/time probabilities",
        "fluence_owner": "Eq29 DAR input; POT, yield, 4*pi*L^2 once", "eta_cm_minus2": fields["C_ETA"]["value"],
        "nuclei_owner": "targets.materials.csi_target_inventory, actual per-isotope nucleus counts", "nuclei": grid_report["normalization"]["number_of_nuclei"],
        "energy_selection_owner": "CsI2021Observation: official Gamma density and PE efficiency once", "legacy_component_acceptance": "unity before time selection",
        "time_selection_owner": "existing build_time_weights: ROOT time marginal, fixed zero-shift0-6us denominator, observer time efficiency once",
        "reference_fractions": grid_report["time_reference_fractions"], "reference_scope_total_events": validation["SM_total_events"],
        "same_eta_full_fluence_total_events": validation["full_fluence_SM_total_events"],
        "scope_difference_meaning": "The numerical eta is assigned to different physical fluence scopes; a representation-only conversion preserves counts and was checked separately",
        "extra_livetime_POT_mass_factor": False, "posthoc_rescale_to_data_or_prior": False}
    driver.write_json(record / "NORMALIZATION_LEDGER.json", normalization)
    source_state = json.loads((run / "SOURCE_STATE_BEFORE_VALIDATION.json").read_text(encoding="utf-8"))
    assert all(driver.sha(root / name) == expected for name, expected in source_state["files"].items())
    audit = {"date": "2026-11-07", "status": "PASS_FILE_AND_CONFIG_AUDIT", "onboarding_sources": [],
        "runtime_code_files_unchanged": len(source_state["files"]), "response_original_unchanged": grid_report["response_sha256"] == "cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74",
        "scope": "Actual local files, fingerprints, adopted direct inputs and executed readers; no new external-authorship certification"}
    assert audit["response_original_unchanged"]
    for source in register["sources"]:
        actual = driver.sha(root / source["uri_or_path"])
        assert actual == source["sha256"]
        audit["onboarding_sources"].append({"source_id": source["source_id"], "path": source["uri_or_path"], "sha256": actual, "original_url": source.get("original_url")})
    driver.write_json(record / "RESOURCE_AUDIT.json", audit)

    checks = {row["name"]: row for row in validation["checks"]}
    grids = checks["simultaneous_grid_refinement_SM_point_only"]["grids"]
    axes = checks["independent_recoil_energy_and_PE_refinements"]["axes"]
    backgrounds = checks["official_event_histograms_and_unscaled_background_diagnostics"]["backgrounds"]
    equivalence = json.loads((run / "NATIVE_SM_EQUIVALENCE.json").read_text(encoding="utf-8"))
    native_error = max(row["max_target_component_bin_error"] for row in equivalence["records"])

    def report_text(current):
        L = lambda label, path: link(label, path, current)
        body = "# CsI2021 标准模型事例数基准计算\n\n2026-11-07，Asia/Shanghai。**数值前向计算已通过本轮检查；严格论文复现未认证。** 本次为用户请求的未拟合SM点，不构建BSM扫描或把结果自动冻结为下游Fast权威。\n\n"
        body += " · ".join([L("配置与逐项来源", record / "SM_CONFIG.json"), L("归一化台账", record / "NORMALIZATION_LEDGER.json"),
            L("机器验收", run / "VALIDATION_RESULTS.json"), L("99箱CSV", run / "events_99bins.csv"), L("完整数组", run / "benchmark.npz"),
            L("P00", onboarding / "P00_SOURCE_REGISTER.yaml"), L("P01", onboarding / "P01_EVIDENCE_LEDGER.yaml"), L("P03", onboarding / "P03_PHYSICS_CONTRACT.yaml")]) + "\n\n"
        titles = [("scope", "实际调用与主线状态"), ("inputs", "采用输入及出处"), ("counts", "事例数与分量"), ("validation", "数值和运行验收"),
            ("figures", "图表与逐箱输出"), ("limits", "与论文比较的限制"), ("reproduce", "复算命令与文件归属")]
        body += '<a id="report-toc"></a>\n\n## 目录\n\n' + "\n".join(f"- [{title}](#{key})" for key, title in titles) + "\n\n"
        back = "\n\n[返回目录](#report-toc)\n\n"
        body += '<a id="scope"></a>\n\n## 实际调用与主线状态\n\n'
        body += "规范和r2来源记录已写入原主项目。主项目通用predict目前只支持一维观测；本轮用它计算PE信号，再显式复用旧目录time_profile/time_acceptance得到时间分箱，未宣称生产Runtime已原生支持二维likelihood。\n\n"
        body += "执行的是validation_only请求，采用P06/P07的归一化、源/核素分量和独立积分检查。代码链为：" + L("本轮入口", Path(driver.__file__)) + " → " + L("主项目predict", root / "cevns_pyeft/core/predict.py") + " → " + L("原生SM/RESPONSE适配器", root / "cevns_pyeft/theory/li2026/adapter.py") + " → 既有时间权重。原Runtime、原核表、注册和冻结参考未改。" + back
        body += '<a id="inputs"></a>\n\n## 采用输入及出处\n\n| 输入 | 实际值 | 单位 | 直接来源及定位 |\n|---|---|---|---|\n'
        used_sources = set()
        for key in adopted:
            row = fields[key]
            source_links = []
            for source in row["direct_sources"]:
                used_sources.add(source["source_id"])
                source_links.append(L(source["source_id"], root / source["uri_or_path"]))
            value = json.dumps(row["value"], ensure_ascii=False) if isinstance(row["value"], (dict, list)) else str(row["value"])
            cells = [row["field"] + " `" + key + "`", value, row["unit"], " · ".join(source_links) + "；" + row["locator"]]
            body += "| " + " | ".join(cell.replace("|", "\\|").replace("\n", " ") for cell in cells) + " |\n"
        body += "\n核响应仍直接调用原JSON，Cs133/I共16个通道数组；" + L("原数值与基底/单位的详细核对", root / "docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md") + "及" + L("本轮资源审计", record / "RESOURCE_AUDIT.json") + "保留实际数组、哈希与核素映射。\n\n"
        body += "原生SM采用项目 `_sm_left_dim6` 的vector及axial项，额外Wilson系数为空。实际矩阵、GF/质量常数和完整native LEC数值保存在SM_CONFIG和最细网格report。直接实施依据为" + L("SM系数定义", root / "cevns_pyeft/rates/differential.py") + "、" + L("常数", root / "cevns_pyeft/foundation/constants.py") + "与" + L("LEC定义", root / "cevns_pyeft/theory/li2026/lec.py") + "；其外部原文逐项等价审计仍为r2所列PARTIAL，不把native数值可调用写成论文辐射修正已复现。\n\n### 本章标准来源及核验范围\n\n"
        for key in sorted(used_sources):
            source = sources[key]
            body += "- " + L(key, root / source["uri_or_path"]) + " " + source["citation"] + "。定位/核验范围：" + source["verification_scope"]
            if source.get("original_url"):
                body += "；[原始网址](" + source["original_url"] + ")"
            body += "。\n"
        body += back + '<a id="counts"></a>\n\n## 事例数与分量\n\n'
        body += f"主结果：**{validation['SM_total_events']:.9f} events**，PE∈[0,60)、t_rec∈[0,6)μs，源按零平移0–6μs参考窗归一化，实际QF积分从2keVnr起。相同数值eta解释为全支撑域注量时为 **{validation['full_fluence_SM_total_events']:.9f} events**；两者改变了注量范围含义，不能混称同一归一化下的模板差异。\n\n"
        body += "| 入射分量 | Cs133事例 | I127事例 | 合计事例 |\n|---|---:|---:|---:|\n"
        parts = arrays["target_component_counts"].sum(axis=(2, 3))
        for index, label in enumerate(["prompt νμ", "delayed νe", "delayed anti-νμ"]):
            body += f"| {label} | {parts[0,index]:.9f} | {parts[1,index]:.9f} | {parts[:,index].sum():.9f} |\n"
        body += f"| 总计 | {parts[0].sum():.9f} | {parts[1].sum():.9f} | {parts.sum():.9f} |\n\n"
        body += "以上均由benchmark.npz的target_component_counts对分析箱求和，并非独立测量。原C/AC事件分别1578/1295；SSB为项目从控制样本推导的" + f"{arrays['SS_derived'].sum():.9f} events。\n\n"
        body += "| 背景分量 | 原表直接构造，时间效率后 | 全PE表概率候选 | Supplement Table I先验 |\n|---|---:|---:|---:|\n"
        for row in backgrounds:
            body += f"| {row['component']} | {row['raw_template_selected_events']:.9f} | {row['probability_candidate_selected_events']:.9f} | {row['published_prior_events']} |\n"
        body += "\n背景均来自P01登记的官方PE/Trec表，算法复用TimeMassCDF；能量表已含能量效率，不重复施加。未按先验缩放任何模板。两套候选及先验不闭合，归一化问题继续保留，图中合计只作为背景诊断。" + back
        body += '<a id="validation"></a>\n\n## 数值和运行验收\n\n| nT / nEν / nPE每箱 / PE步长 | SM总数 | 与上一网格最大逐箱变化 |\n|---|---:|---:|\n'
        for row in grids:
            settings = row["settings"]
            error = row.get("refinement", {}).get("max_bin_absolute_difference_events")
            body += f"| {settings['n_er']} / {settings['n_enu']} / {settings['n_observed_bin']} / {settings['observed_step']} | {row['total_events']:.9f} | {error:.9g} |\n" if error is not None else f"| {settings['n_er']} / {settings['n_enu']} / {settings['n_observed_bin']} / {settings['observed_step']} | {row['total_events']:.9f} | 首轮 |\n"
        body += "\n| 独立减半的积分轴 | 最大逐箱差/events | 门限/events | 判定 |\n|---|---:|---:|---|\n"
        for row in axes:
            body += f"| {row['axis']} | {row['max_bin_absolute_difference_events']:.9g} | 0.005 | {row['status']} |\n"
        body += f"\n本轮{len(validation['checks'])}组检查全部通过，范围限于该SM点：分量与投影闭合、每味注量、等核数、时间表示转换及固定分母、Gamma归一化/QF域、原生求值一致性、网格、独立折叠、实际质量×注量缩放、事件/背景回读和代码未变。" + L("完整数值证据", run / "VALIDATION_RESULTS.json") + f"保留阈值、最差箱和核验范围。原生逐能量与核验后求值的最大小网格分量误差为{native_error:.9g} events，" + L("对照文件", run / "NATIVE_SM_EQUIVALENCE.json") + "记录实际结果。\n\n"
        body += f"相关既有运行测试：{test_summary['tests']}项通过，{test_summary['failures']}失败、{test_summary['errors']}错误。" + L("测试日志", run / "runtime-tests.log") + " / " + L("JUnit", run / "runtime-tests.xml") + "。该结论不替代此前全局工作流尚存问题的验收。" + back
        body += '<a id="figures"></a>\n\n## 图表与逐箱输出\n\n'
        for name, label in [("sm_projections", "PE/时间投影"), ("sm_time_slices", "11个时间窗"), ("sm_counts_2d", "全部99箱")]:
            body += "- " + L(label + " PNG", run / "figures" / (name + ".png")) + " · " + L("可编辑SVG", run / "figures" / (name + ".svg")) + "\n"
        body += "\n" + L("99箱CSV", run / "events_99bins.csv") + "、" + L("PE投影CSV", run / "PE_projection.csv") + "、" + L("时间投影CSV", run / "time_projection.csv") + "均给出原始箱计数。PE图及各时间窗图除以ΔPE；时间投影除以Δt；二维图是events/bin。图中数据误差棒仅为±sqrt(C)/ΔPE展示，不作为likelihood。\n\n"
        body += ("PNG已目视核对坐标、字号、图例、来源说明、负的背景扣除箱和窄箱显示" if plot["visual_QA"] == "PASS" else "PNG尚待真实目视复核") + "；SVG由同一figure导出。图表源数据与文件指纹见" + L("PLOT_MANIFEST", run / "PLOT_MANIFEST.json") + "。" + back
        body += '<a id="limits"></a>\n\n## 与论文比较的限制\n\n'
        body += "| 主张 | 本次结论 |\n|---|---|\n| 项目原生SM＋原data RESPONSE的99箱前向计算 | 数值检查通过；实际参数和核响应均可追到本地资源及原材料 |\n| 2211.11905v2 Fig.18布局、数据及名义信号计算 | 已计算、已绘图；不是该文best-fit曲线 |\n| 严格2211论文模型及83.2统计基准 | 未认证：原生vector/axial核与论文辐射修正/Helm模型未证明等价；半径nuisance、背景归一及拟合均未闭合 |\n| JHEP2022四pull独立统计benchmark | 本轮未重做统计拟合，不用当前full-support诊断替代该benchmark |\n| PE精确作者边界 | 继续标为用户指定的重建值；时间边界来自Fig.18 |\n| 完整ROOT E-t联合源的等价 | 本轮选择论文解析DAR谱×ROOT时间边缘；未使用完整ROOT能谱/二维相关，也不将旧配置相关差异移称本轮已验收 |\n| QF拟合域外与BSM参数域 | 未作物理预测声明；T<2keVnr贡献排除，完整ROOT高能尾及额外anti-νe不纳入当前DAR源 |\n"
        body += "\n尚未闭合的问题继续见" + L("P02", onboarding / "P02_MISSING_AND_CONFLICTS.md") + "。当前用户对原核表直接复用的选择已执行；外部作者导出链待核不阻断本次本地原表计算。" + back
        body += '<a id="reproduce"></a>\n\n## 复算命令与文件归属\n\n'
        body += "本轮计算Python：`" + sys.executable + "`，Python " + grid_report["python"] + "，NumPy " + grid_report["numpy"] + "；运行时注入既有validation_deps以提供scipy/uproot。绘图使用本机conda的matplotlib，版本" + plot["matplotlib"] + "。实际命令顺序与环境见" + L("运行入口README", root / "examples/COHERENT_CsI/time_resolved_sm/README.md") + "及" + L("本次输出README", run / "README.md") + "。\n\n"
        body += "| 文件范围 | 所属README与消费者 |\n|---|---|\n"
        for label, owner in [("计算/验收/绘图/汇总脚本", root / "examples/COHERENT_CsI/time_resolved_sm/README.md"),
            ("原生/细化网格、CSV、NPZ、图和JUnit", run / "README.md"), ("本轮配置、归一化、来源审计与报告", record / "README.md"),
            ("主文档中的SM报告", root / "docs/experiments/COHERENT/CsI2021/time_resolved/README.md")]:
            body += "| " + label + " | " + L("README", owner) + " |\n"
        body += "\n文件与资源SHA见" + L("ARTIFACT_MANIFEST", run / "ARTIFACT_MANIFEST.json") + "，写入范围及原文件备份见" + L("CHANGE_MANIFEST", record / "CHANGE_MANIFEST.json") + "。代码快照只用于核查与恢复，不是一个自行安装或导入的替代Runtime。\n" + back
        return body

    locations = [run / "BENCHMARK.md", record / "07_SM_FORWARD_BENCHMARK_REPORT.md"]
    if args.update_main_doc:
        locations.append(root / "docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md")
    for path in locations:
        path.write_text(report_text(path), encoding="utf-8", newline="\n")
    archive = run / "CODE_SNAPSHOT.zip"
    snapshot_paths = {root / name for name in source_state["files"]}
    snapshot_paths.update(Path(driver.__file__).parent.glob("*.py"))
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(snapshot_paths):
            output.write(path, path.relative_to(root).as_posix())
        for name in ("time_acceptance.py", "time_profile.py"):
            output.write(args.legacy_time_dir / name, "selected_legacy_time/" + name)
    driver.write_json(run / "RUN_SUMMARY.json", {"date": "2026-11-07", "SM_total_events": validation["SM_total_events"],
        "full_fluence_SM_total_events": validation["full_fluence_SM_total_events"], "per_target_component_events": arrays["target_component_counts"].sum(axis=(2,3)).tolist(),
        "runtime_tests": test_summary, "numerical_checks": len(validation["checks"]), "plot_visual_review": plot["visual_QA"],
        "paper_reproduction": "NOT_CERTIFIED", "human_Slow_freeze": "NOT_REVIEWED"})
    print(json.dumps({"reports": [str(path) for path in locations], "native_SM_total_events": validation["SM_total_events"], "runtime_tests": test_summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
