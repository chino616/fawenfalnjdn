"""Record verified Python owners for P01-P10 without promoting workflow gates."""
from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASES = ["Dataset/observable", "Target/exposure", "Source/state", "Theory/nuclear response",
          "Kinematics/cross section", "Detector/selection", "Slow counts", "Fast representation",
          "Statistics/inference", "Validation/report"]


def stage_contracts(name):
    """Describe data flow separately from file existence and execution evidence."""
    bins = {"CsI2017_25PE": "25 PE箱", "CsI2021_9PE_energy_only": "9 PE箱",
            "Ar2020_12bin": "12个legacy观测箱", "CsI2021_time_9x11": "9 PE×11时间箱",
            "CONUS_Plus_conusplus_kkl_run1": "19个10 eVee箱",
            "SolarB8_three_singlebins_continuous_acceptance": "paired/US2/XENONnT三个独立信号总数",
            "SolarB8_multibin_separate_branch": "各自Ne/cS2或真实反冲多bin"}[name]
    rows = [
        ["dataset配置、数值资源与observable定义", "读取并绑定身份、单位和bin边界", "definition/model与"+bins],
        ["同位素组成、核质量、质量/曝光定义", "计算核数并保存曝光归属，避免重复归一", "TargetInventory与run/exposure"],
        ["源能谱/谱线、源强、几何、ν/反ν与味态", "建立相同能量轴上的源分量及入射态", "flux/fluence components与rho(E)"],
        ["SM/NSI LEFT系数、核响应数值与约定", "匹配粒子响应并绑定核响应", "interaction及各核响应通道"],
        ["Eν/反冲网格、核质量、入射态和interaction", "施加精确两体运动学并计算每核微分截面", "dσ/dT [cm²/keV]"],
        ["真实反冲、响应/效率数值与观测分箱", "施加真实量到观测量映射和选择，效率只乘一次", "观测箱折叠权重/接受度"],
        ["源、靶、dσ/dT、响应和积分网格", "直接积分能量与反冲，按源/核素分别求和", "SM/参数点预测 [events/bin]："+bins],
        ["已核查前向模型、网格、系数基和缓存身份", "编译或回放明确参数域内的响应表示", "参数点快速预测及源码/输入指纹"],
        ["与预测同语义的观测、误差、背景、nuisance", "profile nuisance；联合时同一物理点相加后求一维最小值", "χ²、Δχ²、最佳值和分离阈值区间"],
        ["当前模型、数值输出、原文/旧结果与验收范围", "核对回归、独立积分/核表示、来源和结果适用范围", "验证JSON、表格、图件与未完成能力记录"],
    ]
    if name in ("CsI2017_25PE", "Ar2020_12bin", "CsI2021_9PE_energy_only"):
        rows[3] = ["正式NPZ内的各核响应系数、常量快照", "response_from_arrays→ArrayInteraction；不重新从ResponseDB读取外部核表", "package-backed核响应和相互作用"]
        rows[4][1] = "ArrayInteraction.dsigma_dT→differential_cross_section_nn；保留全核通道和味迹"
        rows[9][2] += "；当前正式YAML/NPZ读失败单独记录"
    if name == "CsI2017_25PE":
        rows[5] = ["PE=1.17T、效率和251节点PE网格", "确定性PE映射与插值梯形分箱，无额外Gaussian", "25箱效率折叠信号"]
        rows[8][1] = "正式路线28%一pull Gaussian；本次仅重核冻结SM χ²，参数核缺失"
        rows[8][2] = "SM checkpoint；本次弱角/NSI扫描NOT_RUN"
    elif name == "Ar2020_12bin":
        rows[5] = ["均值响应、σ随观测坐标变化的Gaussian与效率", "observed_gaussian_fold在每个观测箱内积分；PE/keVee冲突仍保留", "12箱折叠矩阵"]
        rows[8][1] = "正式路线为非对称IRLS；本次单列均误差Gaussian .12/.146两pull"
        rows[8][2] = "均误差SM/NSI一维结果；未冒称非对称模型重跑"
    elif name == "CsI2021_9PE_energy_only":
        rows[5][1] = "淬灭→Gamma PE迁移→效率与分量接受度→9箱"
        rows[8][1] = "九箱Gaussian .125/.35独立信号/背景pull；本次回放已保存核"
    elif name == "CsI2021_time_9x11":
        rows[5][1] = "Gamma PE响应×经积分的源分量时间权重/时间接受度"
        rows[6][2] = "99箱SM信号、PE/时间投影及24个NSI前向点"
        rows[7] = ["明确EFT点与物理输入指纹", "cached_evaluate缓存已算前向点；不等于已认证任意耦合99箱Fast核", "已存参数点和缓存身份"]
        rows[8] = ["C/AC原始数组与背景候选；BRN/NIN绝对归一和统计合同不全", "未实现本轮可执行的原生P09；不替换为九箱Gaussian", "MISSING / NOT_RUN"]
    elif name == "CONUS_Plus_conusplus_kkl_run1":
        rows[1] = ["天然Ge组成及当前有效归一化定义", "按所选1 kg×119 day口径建立核数和活时间", "Ge各核素TargetInventory和run"]
        rows[2][1] = "选定反应堆谱插值→反νe纯态；几何/源强依所选谱口径施加一次"
        rows[5][1] = "Ge Lindhard淬灭→Gaussian能量分辨率→效率→eVee分箱"
        rows[8][1] = "有符号excess与对称平均误差Gaussian，16.9%信号pull；非raw Poisson"
    elif name == "SolarB8_three_singlebins_continuous_acceptance":
        rows[1][1] = "保留九行天然Xe丰度分母，取七个有核表的同位素，不重新归一丰度"
        rows[2][1] = "SNuDD v3.4.1有效两味绝热传播；ee NSI每点更新Pee(E)，保留显式近似"
        rows[5] = ["三样本Total效率曲线及反冲窗口", "continuous_acceptance积分；XENON缺尾段显式flat_sensitivity", "三个总信号接受度；不与多bin响应混用"]
        rows[7][1] = "能量分辨核系数与每点传播相乘；弱角作用所有味，不把NSI当固定Pee二次式"
        rows[8][1] = "拟合信号总数Gaussian；弱角/NSI独立12% pull；fB data-only和pull control分开"
    elif name == "SolarB8_multibin_separate_branch":
        rows[1][1] = "SolarPreparation原核数→NuclearPreparation七核素筛选，不重新归一丰度"
        rows[3][1] = "SolarNuclearSM沿用ResponseDB与共享振幅；保持完整SM核通道"
        rows[4][1] = "SolarNuclearSM.channel_dsigma计算共享振幅的精确能量二次式并施加两体端点"
        rows[5][1] = "XENON响应基底/Ne或cS2映射，或PandaX真实反冲接受度；不同输出分别保存"
        rows[7] = ["此分支当前仅直接Slow合同", "未登记独立Fast能力；SM能量二次式属于截面内部计算", "NOT_IMPLEMENTED_FOR_THIS_BRANCH"]
        rows[8] = ["此分支的谱与响应；未闭合本轮拟合背景合同", "仅保留前向结果，不替换三单bin观测", "NOT_RUN_FOR_THIS_TASK"]
    return [{"input_summary": a, "calculation_summary": b, "output_summary": c} for a, b, c in rows]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_ref(path, symbol):
    path = ROOT / path
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    names = {node.name: node.lineno for node in ast.walk(tree)
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    if symbol == "<module>": names[symbol] = 1
    if "." in symbol:
        scope = tree
        for name in symbol.split("."):
            found = [node for node in getattr(scope, "body", [])
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name]
            if len(found) != 1:
                raise ValueError(f"Missing/ambiguous qualified symbol {path}:{symbol}")
            scope = found[0]
        names[symbol] = scope.lineno
    if symbol not in names:
        raise ValueError(f"Missing claimed code symbol {path}:{symbol}")
    return {"path": path.relative_to(ROOT).as_posix(), "symbol": symbol,
            "line": names[symbol], "sha256": sha(path)}


def run(output):
    output = Path(output)
    package = "cevns_pyeft/experiments/package_loader.py"
    profiles = "cevns_pyeft/experiments/package_profiles.py"
    nuclear = "cevns_pyeft/nuclear/response.py"
    theory = "cevns_pyeft/theory/li2026/adapter.py"
    kin = "cevns_pyeft/theory/kinematics.py"
    rates = "cevns_pyeft/rates/recoil.py"
    folding = "cevns_pyeft/rates/folding.py"
    stats = "cevns_pyeft/statistics/profiling.py"
    maps = {}

    def add(name, stages, status, entry, input_path, evidence, note):
        assert len(stages) == 10
        flow = stage_contracts(name)
        maps[name] = {"entry": code_ref(*entry), "input": input_path, "evidence": evidence,
                      "status": status, "note": note,
                      "steps": [{"phase": f"P{i+1:02}", "responsibility": PHASES[i],
                                 "python": [code_ref(*ref) for ref in refs],
                                 "implementation": "MISSING" if not refs else "EXISTS",
                                 "execution_evidence": "symbol/source verified; route-level execution scope stated separately",
                                 **flow[i]}
                                for i, refs in enumerate(stages)]}

    common = [[(package, "read_package"), (package, "definition_from_package")],
              [(profiles, "assemble")], [("cevns_pyeft/experiments/package_components.py", "ArraySource")],
              [("cevns_pyeft/experiments/package_components.py", "ArrayInteraction"), ("cevns_pyeft/experiments/package_components.py", "response_from_arrays")],
              [(kin, "is_two_body_recoil_allowed"), ("cevns_pyeft/experiments/package_components.py", "ArrayInteraction.dsigma_dT"), ("cevns_pyeft/rates/differential.py", "differential_cross_section_nn")],
              [(profiles, "ArrayEfficiency"), ("cevns_pyeft/detectors/coherent.py", "DeterministicPEObservation"), ("cevns_pyeft/rates/legacy_observables.py", "fold_weights")],
              [(profiles, "ProfileExecutor"), ("cevns_pyeft/rates/legacy_observables.py", "predict_legacy_observable"), (rates, "integrate_recoil_yield")],
              [(profiles, "compile_profile"), (profiles, "predict_profile_kernel")],
              [(profiles, "evaluate_statistics")],
              [("examples/experiment_modularization/run_experiments.py", "<module>")]]
    add("CsI2017_25PE", common, "PACKAGE_READ_BLOCKED; SM_SNAPSHOT_ONLY",
        ("cevns_pyeft/experiments/coherent/slow_counts_csi2017.py", "slow_counts_csi2017"),
        "data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml + experiment.resources.npz",
        "outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json",
        "P06 deterministic PE=1.17T, fixed 251-node PE grid; P09 28% one-pull Gaussian. No saved parameter-resolved kernel available. Core/package exist but reads fail; schema provenance remains partial.")
    csi21 = [list(x) for x in common]
    csi21[1] = [(package, "_assemble")]
    csi21[5] = [("cevns_pyeft/detectors/csi2021.py", "CsI2021Observation"), ("cevns_pyeft/detectors/csi2021.py", "CsIGammaResponse")]
    csi21[6] = [("cevns_pyeft/core/predict.py", "predict"), (rates, "integrate_recoil_yield"), (folding, "legacy_density_fold")]
    csi21[7] = [("cevns_pyeft/kernels/compiler.py", "compile_fast"), ("cevns_pyeft/kernels/compiler.py", "reconstruct_channels")]
    csi21[8] = [(package, "evaluate_package_statistics")]
    add("CsI2021_9PE_energy_only", csi21, "SAVED_VERIFIED_KERNEL_USABLE; NATIVE_PACKAGE_READ_BLOCKED",
        ("cevns_pyeft/experiments/runtime.py", "predict_experiment"),
        "data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml + experiment.resources.npz",
        "outputs/paper2601_chi2_corrected_20261111/CsI2021_FORWARD.json",
        "Separate from 99-bin time route. Saved final 512/1920/256 grid; Gaussian signal/background pulls .125/.35. New scans explicitly replay frozen kernel, not a new public-loader run.")
    ar = [list(x) for x in common]
    ar[5] = [(profiles, "ArrayEfficiency"), ("cevns_pyeft/detectors/coherent.py", "ObservedGaussianObservation"), ("cevns_pyeft/rates/legacy_observables.py", "observed_gaussian_fold")]
    add("Ar2020_12bin", ar, "SAVED_VERIFIED_KERNEL_USABLE; NATIVE_PACKAGE_READ_BLOCKED",
        ("cevns_pyeft/experiments/coherent/slow_counts_ar2020.py", "slow_counts_ar2020"),
        "data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml + experiment.resources.npz",
        "outputs/paper2601_chi2_corrected_20261111/Ar2020_FORWARD.json",
        "P06 observed-coordinate-width Gaussian, declared PE versus official keVee conflict. Saved 321/1920/64 grid. Mean-error benchmark and legacy asymmetric model are distinct; full asymmetric inputs cannot be reopened now.")
    time = "examples/COHERENT_CsI/time_resolved_common/sm_support.py"
    ts = [[(time, "inputs"), (time, "analysis_input_file")], [("cevns_pyeft/targets/materials.py", "csi_target_inventory")],
          [(time, "build_model"), (time, "time_source")], [(theory, "Li2026LegacyInteraction"), (nuclear, "ResponseDB")],
          [(kin, "is_two_body_recoil_allowed"), (theory, "dsigma_dT")],
          [("cevns_pyeft/detectors/csi2021.py", "CsI2021Observation"),
           ("examples/COHERENT_CsI/time_resolved_common/time_acceptance.py", "build_time_weights")],
          [("cevns_pyeft/core/predict.py", "predict")],
          [("examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py", "cached_evaluate")], [],
          [("examples/COHERENT_CsI/time_resolved_sm/validate_benchmark.py", "main")]]
    add("CsI2021_time_9x11", ts, "OLD_ENTRY_RETIRED; ONBOARDING_RESTART; P09_MISSING",
        (time, "build_model"), "data/experiments/COHERENT_CsI/CsI2021/time_resolved/analysis_inputs.npz",
        "outputs/csi2021_time_sm_20261107/VALIDATION_RESULTS.json",
        "99-bin signal and 24 NSI forward points exist. Missing accepted raw/on-off likelihood and absolute BRN/NIN normalization. Cannot replace with 9-bin Gaussian or invent sqrt(C) full errors.")
    conus = "examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py"
    nsiconus = "examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py"
    cs = [[(conus, "build_model")], [(conus, "build_model")], [(conus, "build_model"), (conus, "reactor_state"), ("cevns_pyeft/experiments/package_components.py", "ArrayContinuum")],
          [(theory, "Li2026LegacyInteraction"), (nuclear, "ResponseDB")], [(theory, "dsigma_dT"), (kin, "is_two_body_recoil_allowed")],
          [(conus, "GeLindhardGaussian")], [("cevns_pyeft/core/predict.py", "predict"), (conus, "main")],
          [("cevns_pyeft/kernels/compiler.py", "compile_fast"), (nsiconus, "build_polynomials")],
          [(nsiconus, "profile"), (nsiconus, "fit_one_dimension")],
          [(nsiconus, "validate_predictions"), ("examples/CONUS_Plus/conusplus_kkl_run1/sm_response/validate_results.py", "main")]]
    add("CONUS_Plus_conusplus_kkl_run1", cs, "LOCAL_FORWARD_AND_GAUSSIAN_NSI_BENCHMARK_DONE",
        ("examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py", "main"),
        "data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json",
        "outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/validation.json",
        "19x10 eVee; natural Ge, selected flux, Nuclear Response, Lindhard+Gaussian; independent effective 1 kg119 day normalization. One .169 Gaussian pull. External KN/author spectrum not exactly equivalent.")
    solar = "cevns_pyeft/experiments/solar_singlebin.py"
    snudd = "extensions/solar_rho_snudd/experiment.py"
    ss = [[(solar, "read_card"), (solar, "load_singlebin")], [(solar, "build_targets")],
          [(solar, "SourceSpectrum"), ("extensions/solar_rho_snudd/state.py", "ExternalSolarState"), ("extensions/solar_rho_snudd/scan.py", "ScanSource")],
          [("cevns_pyeft/theory/li2026/ee_vector_nsi.py", "ElectronVectorNSI"), (nuclear, "ResponseDB")],
          [("cevns_pyeft/theory/li2026/ee_vector_nsi.py", "spectral_coefficients"), (kin, "is_two_body_recoil_allowed")],
          [(solar, "TotalAcceptance")], [("cevns_pyeft/experiments/solar_nsi.py", "NSIExecutor")],
          [("cevns_pyeft/kernels/solar_nsi.py", "SolarNSIKernel"), ("cevns_pyeft/kernels/solar_nsi.py", "compile_kernel")],
          [("cevns_pyeft/statistics/solar_nsi.py", "SolarNSIJoint")],
          [("tools/run_solar_b8_snudd_inference.py", "direct_validation")]]
    add("SolarB8_three_singlebins_continuous_acceptance", ss, "SM_AND_EE_NSI_INFERENCE_DONE_WITH_DECLARED_APPROXIMATIONS",
        (snudd, "load_snudd"), "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json + solar_b8_nsi_2601_19883/nsi.input.json",
        "outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json",
        "Samples PandaX paired/US2/XENONnT. Continuous Total efficiency, explicit X-tail flat sensitivity, seven Xe isotopes, SNuDD effective two-flavor propagation recomputed at ee points, independent .12 pulls. Explicit full-rho trace v3.5 pending, not required to relabel old results.")
    multi = [[("cevns_pyeft/experiments/solar_b8.py", "definition_from_solar")], [("cevns_pyeft/experiments/solar_b8.py", "SolarPreparation"), ("cevns_pyeft/experiments/solar_nuclear.py", "NuclearPreparation")],
             [("cevns_pyeft/experiments/solar_b8.py", "SolarSpectrum")],
             [("cevns_pyeft/experiments/solar_nuclear.py", "SolarNuclearSM"), (nuclear, "ResponseDB")], [("cevns_pyeft/experiments/solar_nuclear.py", "channel_dsigma"), (kin, "is_two_body_recoil_allowed")],
             [("cevns_pyeft/experiments/solar_b8.py", "XenonBasisObservation"), ("cevns_pyeft/experiments/solar_b8.py", "RecoilAcceptanceObservation")],
             [("cevns_pyeft/experiments/solar_b8.py", "SolarExecutor")], [], [],
             [("tools/run_solar_b8_nuclear_benchmark.py", "main")]]
    add("SolarB8_multibin_separate_branch", multi, "SM_FORWARD_DONE; NOT_REUSED_FOR_SINGLEBIN_SCANS",
        ("cevns_pyeft/experiments/solar_nuclear.py", "with_solar_nuclear_response"),
        "data/experiments/PandaX4T/PandaX4T_2024_US2 + XENONnT/XENONnT_2024_SolarB8",
        "outputs/solar_b8_sm/20261110_nuclear_response_run2/RUN_SUMMARY.json",
        "Kept as distinct legacy multibin response. Current task requests mainline singlebin fit; no mixing Qy/Ne/cS2 observations or author fit-background histograms into that likelihood.")
    access = []
    for family, sid in [("COHERENT_CsI", "CsI2017"), ("COHERENT_CsI", "CsI2021"), ("COHERENT_Ar", "Ar2020")]:
        for leaf in ["experiment.input.yaml", "experiment.resources.npz"]:
            path = ROOT / "data/experiments" / family / sid / leaf
            try:
                path.read_bytes()
                access.append({"path": path.relative_to(ROOT).as_posix(), "readable": True, "sha256": sha(path)})
            except OSError as exc:
                access.append({"path": path.relative_to(ROOT).as_posix(), "readable": False, "error": str(exc)})
    report = {"date": "2026-11-13", "routes": maps, "access_checks": access,
              "verification": "Python file and function/class existence, source SHA256, selected actual benchmark inputs and recorded runs; not canonical workflow gate approval",
              "architecture": "P01-P10 are responsibilities, not ten duplicated per-experiment .py files. Shared code implements reusable steps; scripts compose and validate them.",
              "workflow_definition": "workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md",
              "new_analysis_modules": ["route_audit.py", "prediction_routes.py", "inference.py", "run_analysis.py", "validate_results.py", "publish.py"],
              "current_inference_pipeline": [
                  {"step": "参数→系数", "python": [code_ref("examples/one_d_benchmark/prediction_routes.py", "coefficients")],
                   "operation": "弱角写入所有味的SM LEFT系数；单个实NSI经共享映射写入Wilson系数"},
                  {"step": "参数→信号", "python": [code_ref("examples/one_d_benchmark/prediction_routes.py", "FrozenBilinearRoute"), code_ref("examples/one_d_benchmark/prediction_routes.py", "SolarRoute")],
                   "operation": "地面固定核全通道收缩；太阳按能量保留核并在每点重算传播"},
                  {"step": "信号→χ²", "python": [code_ref("examples/one_d_benchmark/prediction_routes.py", "GaussianChannel.profile"), code_ref("examples/one_d_benchmark/prediction_routes.py", "SolarRoute.profile")],
                   "operation": "按声明误差/背景profile nuisance；太阳独立pull或data-only由明确模式选择"},
                  {"step": "χ²→最小值/区间", "python": [code_ref("examples/one_d_benchmark/inference.py", "scan"), code_ref("examples/one_d_benchmark/run_analysis.py", "main")],
                   "operation": "构造单实验/联合目标、有根据的搜索域、连续1D最小化、所有阈值根与分离区间"},
                  {"step": "独立核对/出版图", "python": [code_ref("examples/one_d_benchmark/validate_results.py", "main"), code_ref("examples/one_d_benchmark/publish.py", "main")],
                   "operation": "解析通量、native截面、full/pair和阈值根核对；只读数值制表/出图"},
              ],
              "shared_theory_chain": [
                  code_ref("cevns_pyeft/theory/li2026/left_to_ci.py", "left_to_ci"),
                  code_ref("cevns_pyeft/theory/li2026/responses.py", "compute_R_matrices"),
                  code_ref("cevns_pyeft/theory/li2026/amplitude.py", "flavor_kernel_onebody_li2026"),
                  code_ref("cevns_pyeft/rates/differential.py", "differential_cross_section_nn"),
              ]}
    (output / "ROUTE_AUDIT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = []
    for name, route in maps.items():
        for step in route["steps"]:
            rows.append({"route": name, "phase": step["phase"], "responsibility": step["responsibility"],
                         "py_files_and_symbols": "; ".join(x["path"] + "::" + x["symbol"] for x in step["python"]),
                         "input": step["input_summary"], "calculation": step["calculation_summary"], "output": step["output_summary"],
                         "stage_implementation": step["implementation"], "route_status": route["status"]})
    with (output / "ROUTE_STEPS.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return report


if __name__ == "__main__":
    import sys
    run(Path(sys.argv[1]))
