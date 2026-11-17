"""Audit existing routes, run reproducible 1D SM and vector-NSI inference.

All writes are analysis/example/output artifacts. Production datasets, runtime,
canonical workflow gates and original numerical benchmarks are unchanged.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
from inference import THRESHOLDS, polynomial, quadratic_domain, scan
from prediction_routes import (BASIS, CONUS_PARAMETERS, TERRESTRIAL_PARAMETERS, GaussianChannel,
                               coefficients, load_routes, read, sha)
from route_audit import run as audit_routes
from cevns_pyeft.statistics.profiling import profile_gaussian_one_pull, profile_gaussian_two_pull
from cevns_pyeft.rates.differential import _sm_left_dim6


def plain(x):
    if isinstance(x, dict): return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [plain(v) for v in x]
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, Path): return str(x)
    return x


def write(path, value):
    Path(path).write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def write_route_summary(out, report):
    import os
    lines = ["# 实验计算路线逐步核查", "", "2026-11-13。按实际Python文件和函数/类核对P01-P10的职责。阶段有代码不等于当前输入可执行，更不等于正式科学Gate通过。", "",
             "P01数据身份/观测 → P02靶与曝光 → P03源/味态 → P04理论/核表 → P05运动学/截面 → P06探测器 → P07 Slow → P08 Fast → P09统计 → P10验证。公共模块可跨实验复用，不要求复制十套实验专用代码。", "",
             "| 实验/路线 | 当前真实状态 |", "|---|---|"]
    lines += [f"| {name} | {route['status']} |" for name, route in report["routes"].items()]
    for name, route in report["routes"].items():
        entry = route["entry"]
        rel = Path(os.path.relpath(ROOT/entry["path"], out)).as_posix()
        lines += ["", "## " + name, "", route["note"], "", f"入口：[{entry['path']}::{entry['symbol']}](<{rel}>)。", "",
                  "输入：`"+route["input"]+"`；已有证据：`"+route["evidence"]+"`。", "",
                  "| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |", "|---|---|---|---|---|"]
        for step in route["steps"]:
            links = []
            for ref in step["python"]:
                rel = Path(os.path.relpath(ROOT/ref["path"], out)).as_posix()
                links.append(f"[{ref['path']}::{ref['symbol']}](<{rel}>)（L{ref['line']}）")
            lines.append(f"| {step['phase']} | {step['responsibility']}<br>{step['calculation_summary']} | {step['input_summary']} → {step['output_summary']} | " + "<br>".join(links) + f" | {step['implementation']} |")
    lines += ["", "## 共享理论内部链（P04–P05）", "",
              "LEFT系数 → left_to_ci核子系数 → compute_R_matrices粒子响应 → flavor_kernel_onebody_li2026收缩R与W → differential_cross_section_nn按入射态取迹。正式package从NPZ构建核响应，外部ResponseDB路线则由各自显式资源装配；不能仅凭同名类判定两者读取同一文件。", ""]
    for ref in report["shared_theory_chain"]:
        rel = Path(os.path.relpath(ROOT/ref["path"], out)).as_posix()
        lines.append(f"- [{ref['path']}::{ref['symbol']}](<{rel}>)（L{ref['line']}）")
    lines += ["", "## 本次一维分析实际调用链", "",
              "以上是各实验原前向/统计路线。下面列本轮66条扫描的实际编排；冻结核回放不冒称正式loader或原生Slow本轮重跑。", "",
              "| 环节 | 当前Python | 完成内容 |", "|---|---|---|"]
    for stage in report["current_inference_pipeline"]:
        refs = []
        for ref in stage["python"]:
            rel = Path(os.path.relpath(ROOT/ref["path"], out)).as_posix()
            refs.append(f"[{ref['path']}::{ref['symbol']}](<{rel}>)（L{ref['line']}）")
        lines.append("| "+stage["step"]+" | "+"<br>".join(refs)+" | "+stage["operation"]+" |")
    lines += ["", "## 本次需要保留的缺口", "",
        "1. CsI-time P09缺明确raw/on-off统计模型、背景绝对归一和必要不确定度；不把99箱硬套九箱Gaussian。",
        "2. CsI2017正式YAML/NPZ被OS拒绝读取，且没有可用的已验收参数核；本次只回读SM点，不生成弱角/NSI伪扫描。",
        "3. CsI2021/Ar的正式Package也有相同OS读取问题，本次可回放此前验证的固定核及保存的Gaussian输入；这不是本次原生loader重跑通过。",
        "4. Ar非对称统计是另一条已存模型；本次可完整重算的是保存了全部数值输入的均误差benchmark，不能将两者混称。",
        "5. 太阳新完整ρ/显式trace v3.5尚待实现；当前ee对角子空间采用既有经过核对的等价Pee表达，并逐点重算传播。",
        "6. 多bin太阳仍是另一条分析；不把拟合背景、Ne/cS2输入带入本次三单bin推断。", "",
        "[机器索引与源码哈希](ROUTE_AUDIT.json) · [逐步骤CSV](ROUTE_STEPS.csv)"]
    (out/"ROUTE_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def independent_gaussian_checks(route):
    ch = route.channel
    rows = []
    for p, value in [("sin2thetaW", .18), ("sin2thetaW", .32), ("epsilon_ee_uV", .19), ("epsilon_emu_dV", -.21)]:
        s = route.predict(value, p)
        result = ch.profile(s)
        if ch.background is None:
            shared = profile_gaussian_one_pull(s, ch.observed, ch.sigma, sigma_alpha=ch.alpha_sigma)
            A = np.r_[s/ch.sigma, 1/ch.alpha_sigma][:, None]
            b = np.r_[(ch.observed-s)/ch.sigma, 0.]
        else:
            shared = profile_gaussian_two_pull(s, ch.observed, ch.background, ch.sigma,
                                               sigma_alpha=ch.alpha_sigma, sigma_beta=ch.beta_sigma)
            A = np.r_[np.column_stack([s/ch.sigma, ch.background/ch.sigma]),
                      [[1/ch.alpha_sigma, 0], [0, 1/ch.beta_sigma]]]
            b = np.r_[(ch.observed-s-ch.background)/ch.sigma, 0., 0.]
        x = np.linalg.lstsq(A, b, rcond=None)[0]
        direct = float(np.sum((b-A@x)**2))
        error = max(abs(float(result[0])-shared.chi2), abs(float(result[0])-direct))
        if error > 2e-9: raise ValueError("independent Gaussian profile disagreement")
        rows.append({"parameter": p, "point": value, "chi2": float(result[0]), "shared_profile_chi2": shared.chi2,
                     "augmented_lstsq_chi2": direct, "max_difference": error})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grid-size", type=int, default=4001)
    parser.add_argument("--audit-only", action="store_true", help="Refresh source/route documentation only; never overwrite numerical scans")
    args = parser.parse_args()
    out = args.output.resolve()
    if (out/"RESULTS.json").exists() and not args.audit_only: raise FileExistsError("Use a new output; results are immutable")
    out.mkdir(parents=True, exist_ok=True)
    for name in ["inputs", "scans", "qa"]: (out/name).mkdir(exist_ok=True)
    started = time.perf_counter()
    audit = audit_routes(out)
    write_route_summary(out, audit)
    print("Route audit complete: 7 named routes, 70 phase rows", flush=True)
    if args.audit_only:
        return
    routes, solar, sources = load_routes(out)
    print("Loaded verified saved kernels and continuous-acceptance solar source", flush=True)
    validations = {"Gaussian_profiles": {name: independent_gaussian_checks(route) for name, route in routes.items()}}
    validation_identity = []
    for angle in [0., .19, .23857, .35, 1.]:
        delta = angle-solar.angle
        from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
        diff = vector_nsi_to_np_wilson(VectorNSIParameters(epsilon_ee_uV=-4*delta/3, epsilon_ee_dV=2*delta/3))
        before, after = _sm_left_dim6(True, solar.angle), _sm_left_dim6(True, angle)
        err = max(float(np.max(abs(after[k]-before[k]-np.eye(3)*diff.get(k, np.zeros((3, 3)))[0, 0]))) for k in BASIS)
        if err > 1e-19: raise ValueError("universal weak-angle matching identity failed")
        validation_identity.append({"sin2thetaW": angle, "equivalent_universal_epsilon_u": -4*delta/3,
                                    "equivalent_universal_epsilon_d": 2*delta/3, "max_Wilson_absolute_error_GeVm2": err})
    validations["universal_weak_angle_matching"] = validation_identity
    # Verify weak-angle polynomial before integration at native differential level.
    from cevns_pyeft.experiments.solar_singlebin import load_singlebin
    from cevns_pyeft.theory.li2026.ee_vector_nsi import ElectronVectorNSI
    from cevns_pyeft.theory.li2026.sm_quadratic import SMQuadraticInteraction
    from cevns_pyeft.contracts import IncidentStateBatch, TheoryPoint
    sample = load_singlebin("PandaX_US2", root=ROOT)
    interaction = ElectronVectorNSI(ROOT/"data/responses/responses_all.json", tuple(t.isotope_id for t in sample.model.targets.isotopes))
    checks = []
    for target in [sample.model.targets.isotopes[0], sample.model.targets.isotopes[-1]]:
        for recoil in [.35, 1.3, 2.5]:
            energy = np.array([7., 12., 16.])
            c = interaction.spectral_coefficients(target, energy, recoil, solar.angle)
            for angle in [.12, .31, .49]:
                u, d = -4*(angle-solar.angle)/3, 2*(angle-solar.angle)/3
                rebuilt = c @ np.array([1., u, d, u*u, u*d, d*d])
                # No NSI state: a pure incoming flavor still probes universal SM.
                native = sample.model.interaction.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=recoil,
                    incident_state=IncidentStateBatch(energy, np.diag([1., 0., 0.]), "nu", "validation"),
                    parameters=TheoryPoint(sin2thetaW=angle)).values_cm2_per_keV
                scale = max(float(np.max(abs(native))), 1e-100)
                error = float(np.max(abs(rebuilt-native))/scale)
                if error > 2e-9: raise ValueError("solar weak-angle differential reconstruction failed")
                checks.append({"isotope": target.isotope_id, "recoil_keV": recoil, "sin2thetaW": angle,
                               "energies_MeV": energy.tolist(), "max_relative_error": error})
    validations["new_weak_angle_native_differential_checks"] = checks
    print("Independent profiling and new weak-angle differential checks passed", flush=True)
    result = {"date": "2026-11-13", "status": "RUNNING", "claim_level": "approximate",
              "native_package_access": "CsI/Ar OS failure retained; frozen numerical replay explicitly identified",
              "thresholds_1d": THRESHOLDS, "scans": {}, "SM_points": {}, "not_run": {},
              "inference": "one physical coordinate at a time; other new-physics coordinates zero; each curve subtracts own 1D continuous minimum; nuisance profiling not marginalization"}
    full_scans = {}

    def save_scan(name, parameter, fn, domain, *, reference_point=0., physical=False, domain_proof=None, method=""):
        key = name+"__"+parameter
        print("Scanning", key, "domain", domain, flush=True)
        s = scan(fn, domain, label=parameter, reference_point=reference_point,
                 grid_size=args.grid_size, physical_boundaries=physical, domain_proof=domain_proof)
        s["analysis"] = name; s["method"] = method
        numerical = {k: s.pop(k) for k in ["grid", "chi2", "delta_chi2"]}
        np.savez_compressed(out/"scans"/(key+".npz"), **numerical)
        full_scans[key] = numerical
        result["scans"][key] = s
        write(out/"PARTIAL_RESULTS.json", result)
        return s

    polynomials = {}
    for name, route in routes.items():
        result["SM_points"][name] = {"events": float(route.predict().sum()), "chi2": float(route.channel.profile(route.predict())[0]),
                                          "sin2thetaW": route.angle, "statistical_model": "saved mean-error Gaussian"}
        params = CONUS_PARAMETERS if name == "CONUS_plus" else TERRESTRIAL_PARAMETERS
        for parameter in ["sin2thetaW", *params]:
            p = route.polynomial(parameter)
            polynomials[name, parameter] = p
            objective = lambda x, p=p, ch=route.channel: ch.profile(polynomial(p, x))[0]
            if parameter == "sin2thetaW":
                save_scan(name, parameter, objective, (0., 1.), reference_point=route.angle, physical=True,
                          domain_proof="physical weak mixing parameter domain 0<=sin2thetaW<=1; fixed reference flux", method="Gaussian nuisance-profile, weak angle universal across incoming flavors")
            else:
                level = float(objective(0.))+THRESHOLDS["95percent"]+.5
                upper = route.channel.rate_upper_bound(level)
                domain = quadratic_domain(p, upper)
                save_scan(name, parameter, objective, domain or (-1., 1.),
                          domain_proof={"inequality": "chi2 >= (Dtot-Stot-Btot)^2/(sum sigma_i^2+sa^2 Stot^2+sb^2 Btot^2)",
                                        "chi2_level_above_SM": level, "maximum_compatible_signal_total": float(upper)},
                          method="single real NSI coordinate; all other NSI zero; Gaussian pulls profiled")
        validations[name+"_polynomial_holdouts"] = route.holdouts
    csi, ar = routes["CsI2021"], routes["Ar2020"]
    for parameter in ["sin2thetaW", *TERRESTRIAL_PARAMETERS]:
        cp, ap = polynomials["CsI2021", parameter], polynomials["Ar2020", parameter]
        fn = lambda x, cp=cp, ap=ap: csi.channel.profile(polynomial(cp, x))[0]+ar.channel.profile(polynomial(ap, x))[0]
        if parameter == "sin2thetaW":
            domain, proof, physical, reference = (0., 1.), "physical domain; independent CsI and Ar pulls", True, .2387
        else:
            level = float(fn(0.))+THRESHOLDS["95percent"]+.5
            domains = [quadratic_domain(p, route.channel.rate_upper_bound(level)) for p, route in [(cp, csi), (ap, ar)]]
            nonempty = [d for d in domains if d is not None]
            domain = min(nonempty, key=lambda d: d[1]-d[0]) if nonempty else (-1., 1.)
            proof, physical, reference = "If joint chi2<=level each independent nonnegative contribution<=level; use strongest finite event-total bound", False, 0.
        save_scan("COHERENT_CsI_Ar_mean_errors", parameter, fn, domain, physical=physical, reference_point=reference,
                  domain_proof=proof, method="independent nuisance parameters; CsI2021 nine-bin + Ar12-bin mean-error benchmark")
    result["SM_points"]["COHERENT_CsI_Ar_mean_errors"] = {"chi2": result["SM_points"]["CsI2021"]["chi2"]+result["SM_points"]["Ar2020"]["chi2"]}
    print("Terrestrial one-dimensional fits complete", flush=True)

    selections = {s: [i] for i, s in enumerate(solar.SAMPLES)}
    selections["Solar_joint"] = [0, 1, 2]
    for name, indices in selections.items():
        result["SM_points"][name] = {"events": solar.SM[indices].tolist(), "chi2": float(solar.profile(solar.SM, indices)), "sin2thetaW": solar.angle, "flux_cm2_s": 5.46e6,
                                        "tail_mode": "flat_sensitivity; continuous accepted curve"}
        save_scan(name, "sin2thetaW", lambda x, ix=indices: solar.profile(solar.weak_signals(x), ix), (0., 1.),
                  reference_point=solar.angle, physical=True, domain_proof="physical weak angle domain; universal amplitude change, fixed flux5.46e6",
                  method="three-sample Gaussian Eq88; independent .12 pulls for selected samples; no new propagation approximation")
        for retain in [False, True]:
            label = "fB_data_only" if not retain else "fB_existing_pulls_control"
            fn = lambda x, ix=indices, retain=retain: solar.profile(np.asarray(x)[..., None]*solar.SM, ix, retain_pulls=retain)
            # Data-only and .12-pull costs both grow beyond this conservative finite range.
            hi = 5.
            while float(fn(hi)) < float(fn(1.))+THRESHOLDS["95percent"]+.5:
                hi *= 2
                if hi > 160: raise ValueError("flux upper range did not close")
            save_scan(name, label, fn, (0., hi), reference_point=1., physical=True,
                      domain_proof="fB>=0; upper boundary checked excluded beyond SM+95%level; flux is5.46e6*fB",
                      method="data-only free flux: no solar-model flux prior" if not retain else "sensitivity only: retain existing independent .12 normalization pulls while scanning source scale")
    for parameter in ["epsilon_ee_uV", "epsilon_ee_dV"]:
        # Evaluate expensive source state for shared grid once; scalar root/minimum
        # evaluations use the exact same source and are cached across samples.
        coeff_index = [0, 1, 3] if parameter.endswith("uV") else [0, 2, 5]
        electron = solar.electron_coefficients()[:, coeff_index]
        pmin = solar.source.probability_bounds[0]
        for name, indices in selections.items():
            fn = lambda x, ix=indices, p=parameter: solar.profile(solar.ee_signals(x, p), ix)
            level = float(fn(0.))+THRESHOLDS["95percent"]+.5
            domains = []
            for i in indices:
                channel = GaussianChannel(name, solar.D[[i]], solar.sigma[[i]], solar.pulls[i])
                upper = channel.rate_upper_bound(level)
                domains.append(quadratic_domain((pmin*electron[i])[:, None], upper))
            domain = min(domains, key=lambda d: d[1]-d[0])
            save_scan(name, parameter, fn, domain,
                      domain_proof={"inequality": "Nsample >= Pee_min * Ne_all-electron(epsilon); independent Gaussian Cauchy bound", "Pee_min": float(pmin), "level": level},
                      method="SNuDD effective two-flavor propagation recomputed at each NSI point; continuous acceptance plus explicit X-tail flat continuation")
    result["not_run"] = {
        "CsI2021_time_9x11": "P09 likelihood/background normalization/covariance contract incomplete; no automatic Gaussian or Poisson substitution",
        "CsI2017_parameter_scans": "OS denies formal YAML/NPZ reads and no saved parameter-resolved kernel is available; only frozen SM statistic rechecked",
        "Ar_asymmetric_fresh_scans": "Separate previously run scheme; source upper/lower arrays cannot be reopened from protected package. Current fresh scans explicitly use existing mean-error benchmark inputs",
        "solar_offdiagonal_mu_tau_NSI": "External propagation contract supports real ee uV/dV only; fixed-state terrestrial kernel cannot substitute",
        "GF_and_oscillation_parameter_scans": "Externally fixed constants, not requested weak-angle/flux benchmarks; no unsupported multi-parameter fit",
        "all_experiments_stacked": "No adopted all-experiment correlation contract; CsI2021 energy/time share observations",
        "Solar_multibin_additional_fits": "Distinct data/response branch; kept in route inventory, not silently substituted into three-singlebin scope"}
    # Frozen CsI2017 can still provide a verified scalar SM checkpoint.
    c17path = ROOT/"outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json"
    c17 = read(c17path); folder = ROOT/"data/experiments/COHERENT_CsI/CsI2017/statistics"
    obs = np.loadtxt(folder/"COHERENT_data.txt")[:, 1]
    low = np.loadtxt(folder/"COHERENT_lower.txt")[:, 1]; high = np.loadtxt(folder/"COHERENT_upper.txt")[:, 1]
    c17profile = profile_gaussian_one_pull(np.array(c17["counts"]), obs, (high-low)/2, sigma_alpha=.28)
    result["SM_points"]["CsI2017_frozen_grid"] = {"events": c17["total_events"], "chi2": c17profile.chi2, "alpha": c17profile.alpha, "grid": c17["record"]["numerics"], "parameter_scan_executed": False}
    validations["CsI2017_SM_recheck"] = asdict(c17profile)
    # Compare own scans against published/reference local 1D results, not 2D boundaries.
    old = read(ROOT/"outputs/paper2601_chi2_corrected_20261111/SUMMARY.json")
    comparison = []
    for name in ["CsI2021", "Ar2020", "CONUS_plus", "COHERENT_CsI_Ar"]:
        newname = "COHERENT_CsI_Ar_mean_errors" if name == "COHERENT_CsI_Ar" else name
        for parameter in ["epsilon_ee_uV", "epsilon_ee_dV"]:
            current = result["scans"][newname+"__"+parameter]
            previous = old["scans_1d"][name][parameter]
            diff = abs(current["chi2_min"]-previous["best_fit"]["chi2"])
            if diff > 1e-8: raise ValueError("previous one-dimensional minimum differs")
            comparison.append({"analysis": newname, "parameter": parameter, "new_minimum": current["chi2_min"],
                               "previous_minimum": previous["best_fit"]["chi2"], "difference": diff})
    validations["existing_1D_minimum_regression"] = comparison
    result["solar_method"] = {"version": "SNuDD v3.4.1 numerical model", "flux_cm2_s": 5.46e6,
                               "tail_last_acceptance": solar.tail_efficiency, "state_approximation": "effective two-flavor adiabatic; vacuum theta13; no Earth regeneration",
                               "explicit_full_rho_trace_v35_executed": False, "free_flux_inference": "Data-only, no duplicate solar-model normalization prior; old pulls retained separately as sensitivity"}
    result["status"] = "COMPLETED_AVAILABLE_SCANS; MISSING_CAPABILITIES_EXPLICIT"
    result["wall_seconds"] = time.perf_counter()-started
    write(out/"RESULTS.json", result)
    write(out/"VALIDATION.json", {"status": "PASS_DECLARED_NUMERICAL_CHECKS; NOT_OFFICIAL_LIKELIHOOD_OR_EXACT_PAPER_CERTIFICATION", **validations})
    for path, expected in sources.items():
        if sha(ROOT/path) != expected: raise ValueError("source changed during execution: "+path)
    for path in HERE.glob("*.py"): sources[path.relative_to(ROOT).as_posix()] = sha(path)
    write(out/"SOURCE_MANIFEST.json", sources)
    rows = []
    for key, s in result["scans"].items():
        rows.append({"analysis": s["analysis"], "parameter": s["parameter"], "identifiable": s["identifiable"],
                     "best_fit": s["best_fit"], "chi2_min": s["chi2_min"], "chi2_reference": s["reference_chi2"],
                     **{k: json.dumps(s["intervals"][k]) for k in THRESHOLDS}})
    with (out/"INTERVALS.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print("COMPLETED", len(rows), "one-dimensional scans; elapsed", result["wall_seconds"], flush=True)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main()
