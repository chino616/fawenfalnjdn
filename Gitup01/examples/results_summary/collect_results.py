"""Build current result tables without changing or refitting scientific sources.

The only new numerical work is evaluation at stored points, algebraic Gaussian
chi-square decomposition, and independent coefficient/scale interval checks.
XLSX authoring is delegated to the adjacent artifact-tool JavaScript builder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "outputs/results_summary_20261115_run2"
ONE = "outputs/one_d_benchmark_20261113_run1"
TWO = "outputs/two_d_benchmark_20261113_run1"
CUT = "outputs/cutoff_scales"
DIM = CUT + "/20261114_dim6_run1"
FULL = CUT + "/20261114_full22_control_run1"
JOINT = CUT + "/20261114_three_group_joint_run1"
COMP = CUT + "/20261114_paper_comparison_run1"
SM = "论文图NoteBook/8. SM_experiment_benchmarks"
TIME = "outputs/csi2021_time_nsi_20261108"
sys.path.insert(0, str(ROOT))
from cevns_pyeft.foundation.constants import G_F

SOURCES: dict[str, str] = {}
CHECKS: list[dict] = []


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def adopt(rel):
    p = (ROOT / rel).resolve()
    if not p.is_relative_to(ROOT) or "backup" in p.relative_to(ROOT).parts:
        raise ValueError("Only explicitly selected active sources: " + str(p))
    SOURCES[p.relative_to(ROOT).as_posix()] = sha(p)
    return p


def read(rel):
    return json.loads(adopt(rel).read_text(encoding="utf-8-sig"))


def source(rel):
    return str(adopt(rel))


def csv_read(rel):
    # Earlier CSVs include code-page damage; use canonical JSON where available.
    return list(csv.DictReader(io.StringIO(adopt(rel).read_text(encoding="utf-8-sig"))))


def write_json(path, value):
    def convert(v):
        if isinstance(v, dict): return {str(k): convert(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)): return [convert(x) for x in v]
        if isinstance(v, np.ndarray): return convert(v.tolist())
        if isinstance(v, np.generic): return convert(v.item())
        if isinstance(v, Path): return str(v)
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("Use explicit open/unbounded flags, never nonfinite JSON")
        return v
    Path(path).write_text(json.dumps(convert(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def test(name, condition, **details):
    CHECKS.append({"check": name, "passed": bool(condition), **details})
    if not condition:
        raise AssertionError(name + ": " + json.dumps(details, ensure_ascii=False))


def close(a, b, atol=2e-8, rtol=2e-9):
    return bool(np.isclose(a, b, atol=atol, rtol=rtol))


def js(v):
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def fmt(v, digits=6):
    if v is None: return "—"
    if isinstance(v, bool): return "是" if v else "否"
    if isinstance(v, (int, float)):
        if v == 0: return "0"
        return f"{v:.{digits}g}"
    return str(v)


def intervals_text(intervals):
    if not intervals: return "空集"
    return " ∪ ".join(("(−∞" if lo is None else "[" + fmt(lo)) + ", " +
                      ("+∞)" if hi is None else fmt(hi) + "]") for lo, hi in intervals)


def col(key, label, width=18, kind="text", format=None):
    return {"key": key, "label": label, "width": width, "kind": kind,
            "format": format or ("0.000000" if kind == "number" else "General")}


def table(key, name, title, note, columns, rows, preview_columns=8):
    test(key + " unique rows", len({r[columns[0]["key"]] for r in rows}) == len(rows), rows=len(rows))
    return {"id": key, "sheet": name, "title": title, "note": note,
            "columns": columns, "rows": rows, "preview_columns": preview_columns}


def hashes_from_manifest(rel):
    m = read(rel)
    count = 0
    for p, h in m.items():
        if isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h):
            test("adopted source " + p, sha(ROOT / p) == h, manifest=rel)
            adopt(p)
            count += 1
    return count


def load_replay():
    sys.path.insert(0, str(ROOT / "examples/two_d_benchmark"))
    from extend_mixed import load_all_models
    planes, sources, _ = load_all_models()  # read-only loader, no snapshot writer
    for p, h in sources.items():
        test("replay source " + p, sha(ROOT / p) == h)
        adopt(p)
    bykey = {p.key: p for p in planes}
    routes = {}
    for p in planes:
        for r in getattr(p, "routes", []): routes[r.name] = r
    solar = next(p.solar for p in planes if hasattr(p, "solar"))
    return bykey, routes, solar


def ground_parts(routes, signals):
    rows = []
    for r, s in zip(routes, signals):
        total, alpha, beta, data, penalty = r.channel.profile(s)
        ch = r.channel
        rows.append({"channel": r.name, "events": float(np.sum(s)),
                     "observed_total": float(ch.observed.sum()), "n_observations": len(ch.observed),
                     "chi2": float(total), "chi2_data": float(data), "chi2_pull": float(penalty),
                     "alpha": float(alpha), "beta": None if ch.background is None else float(beta),
                     "sigma_alpha": ch.alpha_sigma, "sigma_beta": ch.beta_sigma,
                     "decomposition": "stored point evaluated through adopted Gaussian profile"})
    return rows


def solar_parts(solar, signals, indices, retain_pulls=True):
    rows = []
    for i in indices:
        s, d, sig, pull = float(signals[i]), float(solar.D[i]), float(solar.sigma[i]), float(solar.pulls[i])
        alpha = pull ** 2 * s * (d - s) / (sig ** 2 + pull ** 2 * s ** 2) if retain_pulls else 0.
        data = ((d - (1 + alpha) * s) / sig) ** 2
        penalty = (alpha / pull) ** 2
        rows.append({"channel": solar.SAMPLES[i], "events": s, "observed_total": d, "n_observations": 1,
                     "chi2": data + penalty, "chi2_data": data, "chi2_pull": penalty,
                     "alpha": alpha, "beta": None, "sigma_alpha": pull if retain_pulls else None,
                     "sigma_beta": None, "decomposition": "analytic independent yield profile" if retain_pulls else "data-only; normalization pulls removed"})
    return rows


def summarize_parts(parts):
    return {k: sum(r[k] for r in parts) for k in ["chi2", "chi2_data", "chi2_pull", "n_observations"]}


def one_parts(row, routes, solar):
    analysis, par = row["analysis"], row["parameter"]
    value = row.get("best_fit")
    if value is None: value = row.get("reference_point", 0.)
    if analysis in routes or analysis.startswith("COHERENT_"):
        rs = [routes["CsI2021"], routes["Ar2020"]] if analysis.startswith("COHERENT_") else [routes[analysis]]
        return ground_parts(rs, [r.predict(value, par) for r in rs])
    indices = list(range(3)) if analysis == "Solar_joint" else [solar.SAMPLES.index(analysis)]
    if par == "sin2thetaW": signals = solar.weak_signals(value)
    elif par.startswith("fB_"): signals = value * solar.SM
    else: signals = solar.ee_signals(value, par)
    return solar_parts(solar, signals, indices, retain_pulls=par != "fB_data_only")


def scale_segments(intervals, dimension, coupling=1.):
    """Split coefficient intervals at zero, preserving sign and all islands."""
    rows = []
    power = 1 / (dimension - 4)
    for band, (lo, hi) in enumerate(intervals, 1):
        for sign in ["negative", "positive"]:
            a, b = (lo, min(hi, 0.)) if sign == "negative" else (max(lo, 0.), hi)
            if b <= a: continue
            largest, smallest = max(abs(a), abs(b)), min(abs(a), abs(b))
            rows.append({"band": band, "coefficient_sign": sign, "c_lower": a, "c_upper": b,
                         "c_abs_max": largest, "c_abs_min": smallest,
                         "lambda_min_GeV": (coupling / largest) ** power,
                         "lambda_max_GeV": None if smallest == 0 else (coupling / smallest) ** power,
                         "upper_unbounded": smallest == 0, "lower_open": False,
                         "SM_connected": lo <= 0 <= hi})
    return rows


def collect(out):
    one = read(ONE + "/RESULTS.json")
    two = read(TWO + "/BENCHMARK_RESULTS.json")
    main, control, joint = [read(p + "/RESULTS.json") for p in [DIM, FULL, JOINT]]
    compare = read(COMP + "/COMPARISON.json")
    refs1, refs2 = read(ONE + "/REFERENCE_COMPARISON.json"), read(TWO + "/REFERENCE_COMPARISON.json")
    csi_evidence = read(SM + "/CSI2021_COMPARATOR_EVIDENCE.json")
    csi_paper = source("docs/references/COHERENT/2110.07730v2.pdf")
    test("CsI primary comparator PDF", sha(csi_paper) == csi_evidence["source"]["pdf_sha256"])
    counts = {"one_dimension": len(one["scans"]), "SM_parameters": sum(not k.startswith("epsilon_") for k in [r["parameter"] for r in one["scans"].values()]),
              "NSI_one_dimension": sum(r["parameter"].startswith("epsilon_") for r in one["scans"].values()),
              "two_dimensions": len(two["scans"]), "cutoff_main": len(main["results"]),
              "cutoff_control": len(control["results"]), "cutoff_joint": len(joint["results"]),
              "cutoff_paper_comparisons": len(compare["rows"])}
    for key, value in read(out.relative_to(ROOT).as_posix() + "/WRITE_PLAN.json")["expected_records"].items():
        if key in counts: test("count " + key, counts[key] == value, actual=counts[key], expected=value)
    manifest_counts = {p: hashes_from_manifest(p) for p in [ONE + "/SOURCE_MANIFEST.json", TWO + "/BENCHMARK_SOURCE_MANIFEST.json",
                       DIM + "/SOURCE_MANIFEST.json", FULL + "/SOURCE_MANIFEST.json", JOINT + "/SOURCE_MANIFEST.json", COMP + "/SOURCE_MANIFEST.json"]}
    bykey, routes, solar = load_replay()
    for p in [ONE + "/qa/FINAL_CHECKS.json", TWO + "/qa/FINAL_CHECKS.json", DIM + "/FINAL_CHECKS.json", FULL + "/FINAL_CHECKS.json",
              JOINT + "/VALIDATION.json", CUT + "/20261114_comparison_joint_baseline/DELIVERY_QA.json"]: read(p)
    tables, chi_rows, part_rows, interval_rows = [], [], [], []

    def add_chi(record_id, family, analysis, point, dim, value, reference, parts=None, status="declared local-model benchmark", src=None):
        sums = summarize_parts(parts) if parts else {}
        if parts: test("chi-square decomposition " + record_id, close(sums["chi2"], value), residual=sums["chi2"] - value)
        chi_rows.append({"id": record_id, "family": family, "analysis": analysis, "point": js(point), "physics_dimensions": dim,
                         "chi2": value, "chi2_data": sums.get("chi2_data"), "chi2_pull": sums.get("chi2_pull"),
                         "reference_chi2": reference, "delta_reference": None if reference is None else reference - value,
                         "n_observations": sums.get("n_observations"), "status": status, "source": source(src)})
        for i, r in enumerate(parts or [], 1):
            part_rows.append({"id": record_id + "::" + str(i), "record_id": record_id, "family": family, "analysis": analysis, **r, "source": source(src)})

    # Frozen SM points: a joint remains a vector of observations, never a summed measurement.
    for analysis, r in one["SM_points"].items():
        if analysis == "CsI2017_frozen_grid":
            pull = (r["alpha"] / .28) ** 2
            parts = [{"channel": "CsI2017", "events": r["events"], "observed_total": None, "n_observations": 25,
                      "chi2": r["chi2"], "chi2_data": r["chi2"] - pull, "chi2_pull": pull, "alpha": r["alpha"],
                      "beta": None, "sigma_alpha": .28, "sigma_beta": None,
                      "decomposition": "algebraic split of stored chi2 and alpha only; no new array load"}]
        elif analysis in routes:
            parts = ground_parts([routes[analysis]], [routes[analysis].predict()])
        elif analysis.startswith("COHERENT_"):
            parts = ground_parts([routes["CsI2021"], routes["Ar2020"]], [routes["CsI2021"].predict(), routes["Ar2020"].predict()])
        else:
            ids = list(range(3)) if analysis == "Solar_joint" else [solar.SAMPLES.index(analysis)]
            parts = solar_parts(solar, solar.SM, ids)
        add_chi("SM::" + analysis, "SM点", analysis, {"sin2thetaW": r.get("sin2thetaW"), "NSI": 0, "fB": 1}, 0,
                r["chi2"], None, parts, "stored SM/profile point", ONE + "/RESULTS.json")

    smpar, nsi = [], []
    for key, r in one["scans"].items():
        part = one_parts(r, routes, solar)
        ref = r.get("reference_point", 0.)
        row = {"id": key, "analysis": r["analysis"], "parameter": r["parameter"], "best_fit": r.get("best_fit"),
               "chi2_min": r["chi2_min"], "chi2_SM_or_reference": r["reference_chi2"],
               "delta_SM_or_reference": r["reference_chi2"] - r["chi2_min"], "identifiable": r["identifiable"],
               "interval_68": intervals_text(r["intervals"]["68percent"]), "interval_90": intervals_text(r["intervals"]["90percent"]),
               "interval_95": intervals_text(r["intervals"]["95percent"]), "degenerate_minima": js(r.get("degenerate_minima", [])),
               "method": r["method"], "domain": js(r["domain"]), "unit": "dimensionless", "source": source(ONE + "/RESULTS.json")}
        (nsi if r["parameter"].startswith("epsilon_") else smpar).append(row)
        for level, bands in r["intervals"].items():
            for band, (lo, hi) in enumerate(bands, 1):
                interval_rows.append({"id": key + "::" + level + "::" + str(band), "analysis": r["analysis"], "parameter": r["parameter"],
                                      "confidence_percent": {"68percent": 68, "90percent": 90, "95percent": 95}[level],
                                      "delta_chi2": one["thresholds_1d"][level], "band": band, "lower": lo, "upper": hi,
                                      "lower_unbounded": lo is None, "upper_unbounded": hi is None,
                                      "boundary_touch": r.get("boundary_touch", {}).get(level, [False] * len(bands))[band - 1],
                                      "status": "IDENTIFIABLE" if r["identifiable"] else "FLAT_FULL_REAL_AXIS", "source": row["source"]})
        add_chi("1D::" + key, "一维", r["analysis"], {r["parameter"]: r.get("best_fit") if r["identifiable"] else ref}, 1,
                r["chi2_min"], r["reference_chi2"], part, "identifiable" if r["identifiable"] else "flat; point is reference only", ONE + "/RESULTS.json")

    two_rows, views = [], []
    for key, r in two["scans"].items():
        plane = bykey[key]
        best = r["fit"]["best_fit"]
        point = best if best is not None else r["reference_point"]
        signals = plane.signals(point)
        parts = ground_parts(plane.routes, signals) if hasattr(plane, "routes") else solar_parts(plane.solar, signals, plane.indices, getattr(plane, "retain_pulls", True))
        two_rows.append({"id": key, "analysis": r["analysis"], "kind": r["kind"], "parameter_x": r["parameters"][0],
                         "parameter_y": r["parameters"][1], "best_x": None if best is None else best[0], "best_y": None if best is None else best[1],
                         "chi2_min": r["fit"]["chi2_min"], "chi2_reference": r["reference_chi2"],
                         "delta_reference": r["reference_chi2"] - r["fit"]["chi2_min"], "best_fit_semantics": r["best_fit_semantics"],
                         "mode": r["mode"], "status": r["status"], "degenerate_minima": js(r["fit"]["degenerate_minima"]),
                         "domain": js(r["domain"]), "global_surface": str(ROOT / TWO / r["views"]["global"]["surface"]),
                         "global_contours": str(ROOT / TWO / r["views"]["global"]["contours"]),
                         "paper_contours": str(ROOT / TWO / r["views"]["paper_window"]["contours"]), "source": source(TWO + "/BENCHMARK_RESULTS.json")})
        for view, info in r["views"].items():
            for kind in ["surface", "contours"]:
                p = TWO + "/" + info[kind]
                test("2D artifact hash " + p, sha(ROOT / p) == info[kind + "_sha256"])
                adopt(p)
            views.append({"id": key + "::" + view, "record_id": key, "view": view, **info})
        add_chi("2D::" + key, "二维", r["analysis"], dict(zip(r["parameters"], point)), 2,
                r["fit"]["chi2_min"], r["reference_chi2"], parts, r["best_fit_semantics"], TWO + "/BENCHMARK_RESULTS.json")

    # Existing cutoff results already contain all 22 operator structures and joint controls.
    cutoff_rows, scale_rows, coefficient_rows, joint_parts = [], [], [], []
    joint_validation = read(JOINT + "/VALIDATION.json")
    for bundle, prefix, version in [(main, DIM, "dim6_self_consistent"), (control, FULL, "full22_fixed_SM_control"), (joint, JOINT, None)]:
        for r in bundle["results"]:
            ver = r.get("version", version)
            key = ver + "::" + r["analysis_group"] + "::" + r["operator_id"]
            status = r["status"]
            dimensions = r["dimension"]
            row = {"id": key, "analysis": r["analysis_group"], "version": ver, "operator": r["operator_id"], "dimension": dimensions,
                   "flavor": r["flavor"], "status": status, "physical_status": r.get("physical_validation_status", "ADOPTED_DIM6_LOCAL_BENCHMARK"),
                   "coefficient_unit": r.get("coefficient_unit", "GeV^" + str(4 - dimensions)), "best_coefficient": r.get("bestfit_coefficient"),
                   "chi2_min": r["chi2_min"], "chi2_SM": r.get("chi2_SM", r["chi2_min"] if status == "NO_SENSITIVITY" else None),
                   "source": source(prefix + "/RESULTS.json"), "scan": str(ROOT / prefix / r["scan_path"])}
            if ver == "full22_fixed_SM_control" and dimensions == 8:
                row["physical_status"] = "DIM8_PSD_UNRESOLVED_NUMERICAL_CONTROL_ONLY"
            for cl, conf in r["confidence"].items():
                for field, old in [("global", "global_GeV"), ("SM", "sm_connected_GeV"), ("positive", "positive_GeV"), ("negative", "negative_GeV")]:
                    row["lambda_" + cl + "_" + field] = conf.get(old)
                    row["cmax_" + cl + "_" + field] = None
                if status == "NO_SENSITIVITY":
                    coefficient_rows.append({"id": key + "::" + cl + "::1", "result_id": key, "analysis": r["analysis_group"], "version": ver,
                                             "operator": r["operator_id"], "confidence_percent": int(cl), "threshold": conf["threshold"],
                                             "band": 1, "lower": None, "upper": None, "lower_unbounded": True, "upper_unbounded": True,
                                             "unit": row["coefficient_unit"], "status": "FULL_REAL_AXIS_NO_SENSITIVITY", "source": row["source"]})
                    for sign in ["negative", "positive"]:
                        scale_rows.append({"id": key + "::" + cl + "::" + sign, "result_id": key, "analysis": r["analysis_group"], "version": ver,
                                           "operator": r["operator_id"], "dimension": dimensions, "confidence_percent": int(cl), "threshold": conf["threshold"],
                                           "coefficient_sign": sign, "band": 1, "c_lower": None, "c_upper": None, "c_abs_max": None, "c_abs_min": None,
                                           "lambda_min_GeV": 0., "lambda_max_GeV": None, "upper_unbounded": True, "lower_open": True,
                                           "SM_connected": True, "status": "ALL_POSITIVE_SCALES_ALLOWED_NO_FINITE_BOUND", "source": row["source"]})
                    continue
                bands = conf["intervals_coefficient"]
                segments = scale_segments(bands, dimensions, r.get("coupling_abs", 1.))
                test("scale segment count " + key + cl, len(segments) == len(conf["lambda_intervals"]))
                for seg, old in zip(segments, conf["lambda_intervals"]):
                    test("scale segment values " + key + cl + str(seg["band"]) + seg["coefficient_sign"],
                         seg["coefficient_sign"] == old["coefficient_sign"] and close(seg["lambda_min_GeV"], old["lambda_min_GeV"]) and
                         ((seg["lambda_max_GeV"] is old["lambda_max_GeV"] is None) or (seg["lambda_max_GeV"] is not None and old["lambda_max_GeV"] is not None and close(seg["lambda_max_GeV"], old["lambda_max_GeV"]))),
                         original_lower=old["lambda_min_GeV"], recomputed_lower=seg["lambda_min_GeV"])
                    for endpoint in ["min", "max"]:
                        lam = seg["lambda_" + endpoint + "_GeV"]
                        if lam is not None:
                            abs_c = seg["c_abs_max" if endpoint == "min" else "c_abs_min"]
                            test("inverse scale " + key + cl + endpoint + str(seg["band"]) + seg["coefficient_sign"],
                                 close(1 / lam ** (dimensions - 4), abs_c, atol=1e-18, rtol=5e-10))
                    scale_rows.append({"id": key + "::" + cl + "::" + str(seg["band"]) + "::" + seg["coefficient_sign"],
                                       "result_id": key, "analysis": r["analysis_group"], "version": ver, "operator": r["operator_id"],
                                       "dimension": dimensions, "confidence_percent": int(cl), "threshold": conf["threshold"], **seg,
                                       "status": "ALLOWED_INTERVAL", "source": row["source"]})
                for band, (lo, hi) in enumerate(bands, 1):
                    coefficient_rows.append({"id": key + "::" + cl + "::" + str(band), "result_id": key, "analysis": r["analysis_group"], "version": ver,
                                             "operator": r["operator_id"], "confidence_percent": int(cl), "threshold": conf["threshold"], "band": band,
                                             "lower": lo, "upper": hi, "lower_unbounded": False, "upper_unbounded": False,
                                             "unit": row["coefficient_unit"], "status": "ALLOWED_INTERVAL", "source": row["source"]})
                selectors = {"global": segments, "SM": [s for s in segments if s["SM_connected"]],
                             "positive": [s for s in segments if s["coefficient_sign"] == "positive"],
                             "negative": [s for s in segments if s["coefficient_sign"] == "negative"]}
                for field, selected in selectors.items():
                    cm = max((s["c_abs_max"] for s in selected), default=None)
                    row["cmax_" + cl + "_" + field] = cm
                    val = None if cm is None else (1 / cm) ** (1 / (dimensions - 4))
                    old = row["lambda_" + cl + "_" + field]
                    test("scale summary " + key + cl + field, (val is old is None) or (val is not None and old is not None and close(val, old)))
                row["coefficient_intervals_" + cl] = intervals_text(bands)
            cutoff_rows.append(row)
            add_chi("EFT::" + key, "截断能标", r["analysis_group"], {r["operator_id"]: r.get("bestfit_coefficient")}, 1,
                    r["chi2_min"], row["chi2_SM"], None, row["physical_status"] + "; " + status, prefix + "/RESULTS.json")
            if prefix == JOINT:
                vals = r["component_chi2_at_joint_bestfit"]
                test("joint component sum " + key, close(sum(vals.values()), r["chi2_min"]))
                for ch, val in vals.items():
                    joint_parts.append({"id": key + "::" + ch, "result_id": key, "version": ver, "operator": r["operator_id"],
                                        "channel": ch, "joint_best_coefficient": r["bestfit_coefficient"], "chi2_at_joint_best": val,
                                        "chi2_joint_min": r["chi2_min"], "compatibility_cost": r["compatibility_cost_no_calibrated_pvalue"],
                                        "not_a_pvalue": True, "source": row["source"]})
                valset = next(v for v in joint_validation if v["version"] == ver and v["operator_key"] == r["operator_key"])
                bestcheck = min(valset["checks"], key=lambda x: abs(x["x"] - r["bestfit_x"]))
                test("joint nuisance point matched " + key, close(bestcheck["x"], r["bestfit_x"], atol=1e-14))
                psig = np.array([.169, .125, .35, .12, .146, .12, .12, .12])
                penalty = float(np.sum((np.array(bestcheck["pulls"]) / psig) ** 2))
                chi_rows[-1].update(chi2_pull=penalty, chi2_data=r["chi2_min"] - penalty, n_observations=43,
                                    decomposition_source=source(JOINT + "/VALIDATION.json"))
                test("joint independent profile " + key, close(bestcheck["chi2_profile"], r["chi2_min"]))
    counts.update(cutoff_all=len(cutoff_rows), chi_square_rows=len(chi_rows), cutoff_finite=sum(r["status"] != "NO_SENSITIVITY" for r in cutoff_rows))
    test("all cutoff routes", len(cutoff_rows) == 224)
    test("all chi-square rows", len(chi_rows) == 340)

    time_rows = []
    numeric = ["signal_events", "SM_signal_events", "ratio_to_SM", "difference_from_SM_events", "full_support_fluence_events", "prompt_numu_events", "delayed_nue_events", "delayed_numubar_events"]
    for r in csv_read(TIME + "/summary.csv"):
        row = {**r, **{k: float(r[k]) for k in numeric}, "source": source(TIME + "/summary.csv"),
               "status": "SM_FORWARD" if r["point_id"] == "SM" else "NSI_FORWARD_ONLY_NO_CHI2", "reference": "R5 Eqs.(5)-(6), convention only; no published yield table for these points"}
        test("time forward ratio " + r["point_id"], close(row["ratio_to_SM"], row["signal_events"] / row["SM_signal_events"]))
        test("time forward source sum " + r["point_id"], close(sum(row[k] for k in numeric[-3:]), row["signal_events"]))
        time_rows.append(row)
    counts["time_forward_including_SM"] = len(time_rows)
    test("time points incl one SM", len(time_rows) == 24 and sum(r["point_id"] == "SM" for r in time_rows) == 1)

    # SM presentation recipes and their different reference meanings.
    sm_specs = [
        ("CONUS_plus", "有效19箱", "PDF数字化SM", "R2 Fig.1, PDF p10; Eq.(33)", "不同核/源输入；有效1 kg × 119 day", "未认证同输入"),
        ("CsI_time_9x11", "99箱名义SM", "论文SM总率", "R4 arXiv:2110.07730v2 PDF/printed p4, right-column Results first paragraph: 341±11(theory)±42(experiment) events", "仅总率benchmark；拟合信号306±20另列；99箱模板、时间起点和归一化未认证等价", "尚未完全对齐"),
        ("CsI2017", "25箱冻结n_enu=12", "既有本地数字化谱", "R3 energy spectrum", "提取溯源/积分收敛未认证", "未认证"),
        ("Ar2020", "12箱最细保存核", "发布初始CV预期事件模板", "R7 Sections 2.1/2.2/2.6, cevnspdf.txt column 4", "128不是实验拟合信号；PE/keVee冲突保留", "未认证同输入"),
        ("PandaX_paired", "continuous_acceptance 单bin", "旧参考代码口径", "R11 Eqs.(87)-(88); local reference-code recipe", "含通量/核素/味谱等共同变化；不是实验观测", "不同配置"),
        ("PandaX_US2", "continuous_acceptance 单bin", "旧参考代码口径", "R9 Fig.1 and R11 Eqs.(87)-(88)", "不是纯效率开关效应", "不同配置"),
        ("XENONnT", "continuous_acceptance/flat_sensitivity 单bin", "旧参考代码口径", "R10 acceptance; R11 Eqs.(87)-(88)", "尾段敏感性明确；不是实验观测", "不同配置"),
        ("PandaX_US2_multibin", "v3.1 Nuclear Response多bin", "同输入KN控制", "R8 Fig.1 context; adopted v3.1 local arrays", "核响应方法比较；不混入三单bin拟合", "是，局部方法控制"),
        ("XENONnT_multibin", "v3.1 Nuclear Response多bin", "同输入KN控制", "R8 Fig.1 context; adopted v3.1 local arrays", "核响应方法比较；不混入三单bin拟合", "是，局部方法控制")]
    sm_rows, benchmark = [], []
    for idx, (r, spec) in enumerate(zip(csv_read(SM + "/Table_SM_Numerical_Summary.csv"), sm_specs), 1):
        analysis, method, kind, locator, meaning, same = spec
        val = float(r["work_events"])
        ref = None if r["reference_events"] == "--" else float(r["reference_events"])
        diff = None if ref is None else val - ref
        delta = None if ref is None else val / ref - 1
        point = one["SM_points"].get("CsI2017_frozen_grid" if analysis == "CsI2017" else analysis, {})
        if "events" in point:
            ev = point["events"]
            test("SM presentation matches fit SM " + analysis, close(val, ev[0] if isinstance(ev, list) else ev))
        row = {"id": "SM_PLOT_" + str(idx), "analysis": analysis, "method": method, "SM_events": val, "reference_events": ref,
               "chi2_SM": point.get("chi2"), "signal_vector": None, "reference_kind": kind, "same_inputs": same,
               "difference_events": diff, "relative_difference": delta, "interpretation": meaning, "reference_locator": locator,
               "source": source(SM + "/Table_SM_Numerical_Summary.csv")}
        for field in ["reference_theory_uncertainty_events", "reference_experiment_uncertainty_events", "published_fitted_signal_events", "published_fitted_signal_uncertainty_events"]:
            row[field] = None if not r.get(field) else float(r[field])
        if analysis == "CsI_time_9x11":
            test("CsI SM scalar and independent uncertainties", ref == 341. and row["reference_theory_uncertainty_events"] == 11. and row["reference_experiment_uncertainty_events"] == 42. and row["published_fitted_signal_events"] == 306. and row["published_fitted_signal_uncertainty_events"] == 20.)
        sm_rows.append(row)
        benchmark.append({"id": "SM::" + analysis, "family": "SM前向", "analysis": analysis, "parameter_operator": "signal events", "version": method,
                          "local_value": val, "reference_value": ref, "unit": "events", "difference": diff, "relative_difference": delta,
                          "IoU": None, "max_endpoint_difference": None, "local_intervals": None, "reference_intervals": None,
                          "reference_kind": kind, "locator": locator, "scope": meaning + "; " + same, "source": row["source"]})
    for analysis in ["CsI2021", "COHERENT_CsI_Ar_mean_errors", "Solar_joint"]:
        r = one["SM_points"][analysis]
        sm_rows.append({"id": "SM_STAT_" + analysis, "analysis": analysis, "method": "九箱能量/均误差" if analysis != "Solar_joint" else "continuous_acceptance 三单bin联合",
                        "SM_events": r.get("events") if not isinstance(r.get("events"), list) else None, "signal_vector": js(r.get("events")) if isinstance(r.get("events"), list) else None,
                        "chi2_SM": r["chi2"], "reference_events": None, "reference_kind": "独立统计路线SM点", "same_inputs": "不适用",
                        "difference_events": None, "relative_difference": None, "interpretation": "联合保留成员信号向量；没有单一合并观测" if analysis != "CsI2021" else "与CsI-time重叠，不相加",
                        "reference_locator": "R11 Eqs.(86),(88),(90); local statistics contract", "source": source(ONE + "/RESULTS.json")})

    for i, r in enumerate(refs1["CONUS_NSI"], 1):
        benchmark.append({"id": "1D_NSI_" + str(i), "family": "NSI一维", "analysis": r["analysis"], "parameter_operator": r["parameter"], "version": "fixed others; 68% nominal",
                          "local_value": None, "reference_value": None, "unit": "dimensionless", "difference": None, "relative_difference": None,
                          "IoU": None, "max_endpoint_difference": r["max_endpoint_difference"], "local_intervals": intervals_text(r["own_68percent"]),
                          "reference_intervals": intervals_text(r["paper_TableII_1sigma"]), "reference_kind": "论文舍入区间", "locator": r["source"],
                          "scope": "conditional local-model interval comparison; no author input equivalence certification", "source": source(ONE + "/REFERENCE_COMPARISON.json")})
    r = refs1["CONUS_weak_angle"]
    benchmark.append({"id": "1D_CONUS_angle", "family": "SM参数", "analysis": "CONUS_plus", "parameter_operator": "sin2thetaW", "version": "fixed flux",
                      "local_value": r["own_best"], "reference_value": r["paper_best"], "unit": "dimensionless", "difference": r["own_best"] - r["paper_best"],
                      "relative_difference": r["own_best"] / r["paper_best"] - 1, "IoU": None, "max_endpoint_difference": None,
                      "local_intervals": intervals_text(r["own_68percent"]), "reference_intervals": intervals_text([r["paper_68percent"]]),
                      "reference_kind": "论文最佳值与1σ", "locator": r["source"], "scope": r["model_equivalence"], "source": source(ONE + "/REFERENCE_COMPARISON.json")})
    r = refs1["COHERENT_weak_angle_context"]
    own = one["scans"]["COHERENT_CsI_Ar_mean_errors__sin2thetaW"]
    benchmark.append({"id": "1D_COHERENT_angle_context", "family": "SM参数", "analysis": "COHERENT_CsI_Ar_mean_errors", "parameter_operator": "sin2thetaW", "version": "energy Gaussian vs timing/shape",
                      "local_value": own["best_fit"], "reference_value": r["paper_best"], "unit": "dimensionless", "difference": own["best_fit"] - r["paper_best"],
                      "relative_difference": None, "IoU": None, "max_endpoint_difference": None, "local_intervals": intervals_text(own["intervals"]["68percent"]),
                      "reference_intervals": intervals_text([[r["paper_best"] - r["paper_sigma"], r["paper_best"] + r["paper_sigma"]]]),
                      "reference_kind": "不同likelihood的文献背景", "locator": r["source"], "scope": r["reason"], "source": source(ONE + "/REFERENCE_COMPARISON.json")})
    benchmark.append({"id": "Solar_SM_multibin_context", "family": "SM参数", "analysis": "Solar_joint", "parameter_operator": "sin2thetaW/fB", "version": "three totals vs multibin",
                      "reference_kind": "不同likelihood，不能作同输入复现误差", "locator": refs1["solar_context"]["source"], "scope": refs1["solar_context"]["reason"],
                      "source": source(ONE + "/REFERENCE_COMPARISON.json")})
    for r in refs2["graphical_comparisons"]:
        benchmark.append({"id": "2D::" + r["reference_id"], "family": "二维区域", "analysis": two["scans"][r["case"]]["analysis"], "parameter_operator": r["case"], "version": "90% nominal 2D threshold 4.61",
                          "IoU": r["intersection_over_union"], "reference_kind": "PDF图形轮廓", "unit": "geometric fraction", "locator": r["source"],
                          "scope": "IoU不是置信度；原图窗、换轴、even-odd内洞保留；无作者χ²网格", "source": source(TWO + "/REFERENCE_COMPARISON.json")})
    for i, r in enumerate(compare["rows"], 1):
        test("cutoff benchmark ratio " + str(i), close(r["local_90CL_GeV"] / r["paper_fig3_90CL_GeV"], r["ratio_local_over_paper"]))
        benchmark.append({"id": "EFT_PAPER_" + str(i), "family": "截断能标", "analysis": r["analysis_group"], "parameter_operator": r["operator"], "version": r["version"],
                          "local_value": r["local_90CL_GeV"], "reference_value": r["paper_fig3_90CL_GeV"], "unit": "GeV", "difference": r["difference_GeV"],
                          "relative_difference": r["relative_difference_percent"] / 100, "reference_kind": "PDF柱顶几何数字化", "locator": "R11 PDF p22 Fig.3, 90% single-parameter nominal 2.71; |g|=1",
                          "scope": r["comparison_status"], "source": source(COMP + "/COMPARISON.json")})
    for i, r in enumerate(compare["joint_comparison"], 1):
        benchmark.append({"id": "EFT_JOINT_" + str(i), "family": "联合相对单组", "analysis": "CONUS_COHERENT_Solar_joint", "parameter_operator": r["operator"], "version": r["version"],
                          "local_value": r["joint_90CL_GeV"], "reference_value": r["strongest_individual_90CL_GeV"], "unit": "GeV",
                          "difference": r["joint_90CL_GeV"] - r["strongest_individual_90CL_GeV"], "relative_difference": r["joint_relative_to_strongest_percent"] / 100,
                          "reference_kind": "本地最强单组，非论文数值", "locator": "local comparison of own-global-minimum Δχ² curves",
                          "scope": "联合不保证单调增强；independent pulls; " + r["physical_validation_status"], "source": source(COMP + "/COMPARISON.json")})
    for i, r in enumerate(compare["solar_propagation_comparison"], 1):
        benchmark.append({"id": "SOLAR_PROP_" + str(i), "family": "太阳方法控制", "analysis": "Solar_three_singlebins", "parameter_operator": r["operator"], "version": "self-consistent vs fixed-SM control",
                          "local_value": r["self_consistent_GeV"], "reference_value": r["fixed_SM_control_GeV"], "unit": "GeV",
                          "difference": r["self_consistent_GeV"] - r["fixed_SM_control_GeV"], "relative_difference": r["relative_difference_percent"] / 100,
                          "reference_kind": "不同前向版本的方法控制", "locator": "local adopted dim6 / rebuilt full22 control", "scope": r["interpretation"], "source": source(COMP + "/COMPARISON.json")})

    audit = read(ONE + "/ROUTE_AUDIT.json")
    route_rows = []
    for key, r in audit["routes"].items():
        for step in r["steps"]:
            py = step["python"]
            for item in py:
                test("route code hash " + item["path"], sha(ROOT / item["path"]) == item["sha256"])
                adopt(item["path"])
            route_rows.append({"id": key + "::" + step["phase"], "route": key, "phase": step["phase"], "responsibility": step["responsibility"],
                               "python_files": "\n".join(str(ROOT / x["path"]) + ":" + str(x["line"]) + " :: " + x["symbol"] for x in py),
                               "input": step["input_summary"], "calculation": step["calculation_summary"], "output": step["output_summary"],
                               "implementation": step["implementation"], "route_status": r["status"], "execution_evidence": step["execution_evidence"],
                               "source": source(ONE + "/ROUTE_AUDIT.json")})
    test("route responsibilities count", len(route_rows) == 70)

    overview_specs = [
        ("CsI2017", "CsI2017，25 PE箱", None, None, "SM冻结点与图；未做参数扫描", "正式包拒读；无参数核；来源/收敛未认证"),
        ("CsI_time_9x11", "CsI-time，9 PE×11时间箱", None, None, "99箱SM；23个非零NSI前向点＋1 SM", "P09/背景归一/不确定度合同未闭合"),
        ("CsI2021", "CsI2021，九箱能量谱", "CsI2021_9PE", None, "SM、弱角、实矢量NSI、χ²、能标", "保存核回放；与CsI-time重叠"),
        ("Ar2020", "Ar2020，12箱均误差Gaussian", "Ar2020_average", None, "SM、弱角、实矢量NSI、χ²、能标", "PE/keVee冲突、正式包；非对称版本未本轮重扫"),
        ("CONUS_plus", "CONUS+，conusplus_kkl_run1", "CONUS_plus", None, "SM、弱角、NSI、χ²、能标及文献对照", "原始源/核作者等价性、高能尾差异"),
        ("PandaX_paired", "PandaX paired，单bin", "PandaX_paired", None, "continuous_acceptance；SM/弱角/fB/ee-NSI", "v3.4.1有效两味；不是多bin"),
        ("PandaX_US2", "PandaX US2，单bin", "PandaX_US2", None, "continuous_acceptance；SM/弱角/fB/ee-NSI", "v3.4.1；与paired按现统计合同独立"),
        ("XENONnT", "XENONnT，单bin", "XENONnT", None, "continuous_acceptance；SM/弱角/fB/ee-NSI", "XENON尾段flat_sensitivity；v3.5未执行"),
        ("COHERENT_CsI_Ar_mean_errors", "CsI九箱＋Ar均误差联合", "CsI2021_9PE+Ar2020_average", None, "同物理点相加绝对χ²再求联合最小值", "独立pull近似；不叠加重叠CsI样本"),
        ("Solar_joint", "太阳三单bin联合", "Solar_three_singlebins", None, "三拟合信号总数；SM/NSI/弱角/fB/能标", "自由弱角/fB二维存在边界/强简并"),
        ("CONUS_COHERENT_Solar_joint", "CONUS＋COHERENT＋太阳三组联合", None, "all", "6数据通道/43观测/8独立pull；2主＋22控制", "仅EFT单系数；非完整SM/NSI全参数联合"),
        ("PandaX_US2_multibin", "PandaX US2多bin，独立v3.1", None, None, "SM核Response及同输入KN对照", "未追加拟合；不与三单bin叠加"),
        ("XENONnT_multibin", "XENONnT多bin，独立v3.1", None, None, "SM核Response及同输入KN对照", "未追加拟合；不与三单bin叠加")]
    overview = []
    for key, label, cutoff_group, joint_selector, done, gap in overview_specs:
        overview.append({"id": key, "analysis": label, "one_d": sum(r["analysis"] == key for r in one["scans"].values()),
                         "two_d": sum(r["analysis"] == key for r in two["scans"].values()),
                         "cutoff_main": sum(r["analysis_group"] == cutoff_group for r in main["results"]),
                         "cutoff_control": sum(r["analysis_group"] == cutoff_group for r in control["results"]),
                         "cutoff_joint": 24 if joint_selector else 0, "completed": done, "gap": gap,
                         "source": source(JOINT + "/RESULTS.json") if joint_selector else source(ONE + "/RESULTS.json")})
    test("overview sums", all(sum(r[k] for r in overview) == v for k, v in [("one_d", 66), ("two_d", 41), ("cutoff_main", 24), ("cutoff_control", 176), ("cutoff_joint", 24)]))

    defs = [
        {"id": "coupling_abs", "category": "能标约定", "numeric_value": 1., "text_value": "|g|; coefficient c=s |g| / Λ^(d−4)", "unit": "dimensionless", "formula": "Λ=(|g|/|c|)^(1/(d−4))", "locator": "R11 p21 Eqs.(91)-(92)", "source": source("examples/cutoff_scales/inference.py")},
        {"id": "GF", "category": "固定SM参数", "numeric_value": G_F, "text_value": "Fermi coupling; fixed, no GF fit", "unit": "GeV^-2", "formula": None, "locator": "scipy physical_constants or adopted fallback", "source": source("cevns_pyeft/foundation/constants.py")},
        {"id": "kappa", "category": "NSI匹配", "numeric_value": math.sqrt(2) * G_F, "text_value": "c6q1_NP = −sqrt(2) GF epsilon_qV", "unit": "GeV^-2", "formula": "SQRT(2)*GF", "locator": "epsilon_matrix_to_np_wilson", "source": source("cevns_pyeft/statistics/parameters.py")},
        {"id": "flux_reference", "category": "固定源参数", "numeric_value": 5.46e6, "text_value": "ΦB = fB × Φref", "unit": "cm^-2 s^-1", "locator": "adopted singlebin source", "source": source(ONE + "/RESULTS.json")},
        {"id": "threshold_1D_68", "category": "名义阈值", "numeric_value": 1., "text_value": "1D, 68% label", "unit": "delta chi2", "source": source(ONE + "/RESULTS.json")},
        {"id": "threshold_1D_90", "category": "名义阈值", "numeric_value": 2.71, "text_value": "1D, 90% label", "unit": "delta chi2", "source": source(ONE + "/RESULTS.json")},
        {"id": "threshold_1D_95", "category": "名义阈值", "numeric_value": 3.84, "text_value": "1D, 95% label", "unit": "delta chi2", "source": source(ONE + "/RESULTS.json")},
        {"id": "threshold_2D_68", "category": "名义阈值", "numeric_value": 2.30, "text_value": "2D, 68% label", "unit": "delta chi2", "source": source(TWO + "/BENCHMARK_RESULTS.json")},
        {"id": "threshold_2D_90", "category": "名义阈值", "numeric_value": 4.61, "text_value": "2D, 90% label", "unit": "delta chi2", "source": source(TWO + "/BENCHMARK_RESULTS.json")},
        {"id": "threshold_2D_95", "category": "名义阈值", "numeric_value": 5.99, "text_value": "2D, 95% label", "unit": "delta chi2", "source": source(TWO + "/BENCHMARK_RESULTS.json")},
        {"id": "NSI_sign", "category": "符号", "text_value": "C_positive ↔ negative epsilon; C_negative ↔ positive epsilon. Real offdiagonal NSI opens both Hermitian-conjugate entries.", "locator": "epsilon_matrix_to_np_wilson", "source": source("cevns_pyeft/statistics/parameters.py")},
        {"id": "chi2_ground", "category": "统计方法", "text_value": "Σ[D−(1+α)S−(1+β)B]^2/σ² + α²/σα² + β²/σβ²; CONUS omits β", "locator": "R11 Eqs.(86),(90); adopted local arrays", "source": source(ONE + "/STATISTICS_CONTRACT.md")},
        {"id": "chi2_solar", "category": "统计方法", "text_value": "D=[3.5,75,10.7] fitted yields; σ=[1.2985,27.975,3.9483]; independent 0.12 pulls; not raw Poisson", "locator": "R11 Eqs.(87)-(88)", "source": source(ONE + "/STATISTICS_CONTRACT.md")},
        {"id": "flux_modes", "category": "方法区别", "text_value": "fB_data_only removes normalization pulls; existing_pulls_control retains the original independent 12% pulls. Both fix sin²θW in 1D.", "source": source(ONE + "/STATISTICS_CONTRACT.md")},
        {"id": "solar_version", "category": "方法区别", "text_value": "continuous_acceptance + SNuDD v3.4.1 effective two-flavor adiabatic propagation; ee NSI updated pointwise; XENON flat_sensitivity tail; explicit v3.5 full-rho trace not executed", "source": source(TWO + "/BENCHMARK_RESULTS.json")},
        {"id": "cutoff_versions", "category": "方法区别", "text_value": "dim6 main: pointwise solar ee-vector propagation. full22: fixed SM solar state, LNC ee and LNV e↔mu transitions. dim8 PSD unresolved; numerical control only.", "source": source("examples/cutoff_scales/IMPLEMENTATION_20261114.md")},
        {"id": "joint_contract", "category": "联合统计", "text_value": "CONUS19 + CsI9 + Ar12 + 3 solar yields =43 observations; 8 independent pulls; fB=1; weak angles CONUS/solar .23857 and CsI/Ar .2387. No CsI-time/2017 double counting.", "source": source("examples/cutoff_scales/COMPARISON_JOINT_20261114.md")},
        {"id": "intervals", "category": "解释", "text_value": "Global Λ is an infimum of the entire allowed set; a disconnected set is not simply Λ>lower. Strict SM branch contains c=0. Unbounded endpoint is null plus flag; flat response has all Λ>0 allowed.", "source": source("examples/cutoff_scales/IMPLEMENTATION_20261114.md")},
        {"id": "coverage", "category": "解释", "text_value": "Each curve/plane subtracts its own global minimum. Threshold labels nominal; no coverage toys, p-values or fitted degrees of freedom supplied. IoU is geometry, not confidence.", "source": source(TWO + "/BENCHMARK_RESULTS.json")},
        {"id": "scale_meaning", "category": "解释", "text_value": "Λ is a convention-dependent EFT suppression scale for |g|=1, not a certified UV particle mass or EFT-validity energy cutoff.", "locator": "R11 Eq.(91)", "source": source("examples/cutoff_scales/PLAN_20261114.md")},
        {"id": "not_run", "category": "未完成", "text_value": js(one["not_run"]) + "; all_experiments_stacked entry is 20261113 historical scan scope; 20261114 adds only single-coefficient EFT joint, not a general SM/NSI joint fit.", "source": source(ONE + "/RESULTS.json")}
    ]
    reftext = adopt(SM + "/REFERENCES_AND_METHODS.md").read_text(encoding="utf-8")
    for block in re.split(r"(?=\*\*\[R\d+\])", reftext)[1:]:
        block = block.split("\n\n## ")[0]
        refid = re.match(r"\*\*\[(R\d+)\]", block)[1]
        first = block.split("\n")[0]
        locator = next((line.removeprefix("定位：") for line in block.splitlines() if line.startswith("定位：")), "")
        defs.append({"id": refid, "category": "参考文献", "text_value": first.replace("**", ""), "locator": locator,
                     "source": source(SM + "/REFERENCES_AND_METHODS.md")})
    test("eleven bibliography entries", sum(r["category"] == "参考文献" for r in defs) == 11)

    common1 = [col("id", "路线ID", 42), col("analysis", "分析组", 30), col("parameter", "参数", 26), col("best_fit", "最佳值", 16, "number"),
               col("chi2_min", "χ²min", 15, "number"), col("interval_68", "68%完整允许集", 52), col("interval_90", "90%完整允许集", 52), col("interval_95", "95%完整允许集", 52),
               col("identifiable", "可辨识", 12, "boolean"), col("chi2_SM_or_reference", "χ²参考点", 16, "number"), col("delta_SM_or_reference", "Δχ²参考点", 16, "number"),
               col("degenerate_minima", "全部已找简并点", 65), col("method", "处理方式", 75), col("domain", "搜索域", 40), col("source", "来源绝对地址", 90)]
    tables.append(table("overview", "总览", "实验结果总览 · 2026-11-15", "计数按分析路线；联合与其成员不可再次相加。表中控制结果不等于物理接受。", [col("id", "身份", 36), col("analysis", "实验与方法", 42), col("one_d", "一维", 9, "integer"), col("two_d", "二维", 9, "integer"), col("cutoff_main", "能标主版", 12, "integer"), col("cutoff_control", "能标控制", 12, "integer"), col("cutoff_joint", "能标三组联合", 16, "integer"), col("completed", "已完成内容", 70), col("gap", "限制与缺口", 80), col("source", "来源绝对地址", 90)], overview))
    tables.append(table("SM_predictions", "SM预测", "标准模型预测与参考口径", "12行；CsI2021论文SM总率341±11理论±42实验；拟合信号306±20另列；99箱模板未认证对齐。", [col("id", "结果ID", 28), col("analysis", "分析组", 30), col("method", "方法", 44), col("SM_events", "SM events", 17, "number", "0.000000"), col("reference_events", "参考 events", 18, "number"), col("chi2_SM", "χ²SM", 16, "number"), col("relative_difference", "相对参考差异", 18, "number", "0.00%"), col("reference_kind", "参考类型", 30), col("same_inputs", "是否同输入", 25), col("interpretation", "差异含义", 78), col("signal_vector", "联合信号向量", 58), col("reference_locator", "文献与定位", 75), col("source", "来源绝对地址", 90), col("reference_theory_uncertainty_events", "参考理论误差 [events]", 29, "number", "0"), col("reference_experiment_uncertainty_events", "参考实验误差 [events]", 29, "number", "0"), col("published_fitted_signal_events", "发表拟合信号 [events]", 29, "number", "0"), col("published_fitted_signal_uncertainty_events", "拟合信号误差 [events]", 29, "number", "0")], sm_rows))
    tables.append(table("SM_parameters", "SM参数", "一维SM参数结果", "16条：8个条件弱角，4个data-only通量，4个保留pull的通量控制；GF及振荡参数未拟合。", common1, smpar))
    tables.append(table("NSI_one_dimension", "NSI一维", "一维实矢量NSI结果", "50条含6条SNS ττ平坦坐标；每次仅开一个实坐标，其他NSI为0；完整分离区间均保留。", common1, nsi))
    tables.append(table("two_dimension", "二维分析", "二维SM与NSI结果", "41平面；3平坦，9个单太阳总数有连续最佳曲线。代表最佳点不是唯一测量值。二维阈值2.30/4.61/5.99。", [col("id", "平面ID", 55), col("analysis", "分析组", 30), col("parameter_x", "横坐标", 25), col("parameter_y", "纵坐标", 25), col("best_x", "最佳x/代表x", 17, "number"), col("best_y", "最佳y/代表y", 17, "number"), col("chi2_min", "χ²min", 16, "number"), col("delta_reference", "Δχ²参考点", 17, "number"), col("best_fit_semantics", "最佳点含义", 90), col("mode", "统计处理", 45), col("status", "状态", 45), col("degenerate_minima", "全部已找简并点", 90), col("global_surface", "完整域面地址", 100), col("global_contours", "完整域轮廓地址", 100), col("paper_contours", "论文窗轮廓地址", 100), col("source", "结果来源地址", 90)], two_rows))
    tables.append(table("chi_square", "χ²汇总", "SM点与全部拟合χ²", "340条：9 SM点＋66一维＋41二维＋224能标。空白分项表示原来源未给分解，不填0。χ²不是χ²/dof。", [col("id", "统计记录ID", 64), col("family", "类别", 16), col("analysis", "分析组", 34), col("chi2", "χ²", 17, "number"), col("chi2_data", "χ²data", 17, "number"), col("chi2_pull", "χ²pull", 17, "number"), col("reference_chi2", "χ²参考点", 18, "number"), col("delta_reference", "Δχ²参考点", 18, "number"), col("physics_dimensions", "物理维数", 12, "integer"), col("n_observations", "观测数量", 12, "integer"), col("point", "参数点", 75), col("status", "解释/数值范围", 90), col("source", "来源绝对地址", 90)], chi_rows))
    tables.append(table("NSI_forward", "NSI前向", "CsI-time NSI前向结果", "24点含1个SM及23个非零NSI点；该运行SM=353.4655777716773，与SM图集名义运行略有区别。没有χ²或CL。", [col("point_id", "点ID", 32), col("nonzero_epsilon_upper_triangle", "非零ε上三角", 60), col("signal_events", "信号 events", 18, "number"), col("ratio_to_SM", "相对SM", 17, "number"), col("difference_from_SM_events", "与SM差 events", 19, "number"), col("prompt_numu_events", "prompt νμ", 18, "number"), col("delayed_nue_events", "delayed νe", 18, "number"), col("delayed_numubar_events", "delayed anti-νμ", 22, "number"), col("SM_signal_events", "本运行SM events", 22, "number"), col("full_support_fluence_events", "full-support events", 24, "number"), col("status", "状态", 35), col("reference", "文献及范围", 90), col("source", "来源绝对地址", 90)], time_rows))
    cutcols = [col("id", "能标路线ID", 65), col("analysis", "分析组", 38), col("version", "计算版本", 32), col("operator", "算符", 13), col("dimension", "维数d", 9, "integer"), col("flavor", "味结构", 22)]
    for cl in ["90", "95"]:
        for field, label in [("global", "全域保守"), ("SM", "严格SM分支"), ("positive", "系数正"), ("negative", "系数负")]:
            cutcols.append(col("lambda_" + cl + "_" + field, "Λ" + cl + " " + label + " [GeV]", 24, "number", "#,##0.000"))
    cutcols += [col("status", "灵敏度状态", 26), col("physical_status", "物理接受范围", 70), col("best_coefficient", "最佳有符号系数", 24, "number", "0.000000E+00"), col("coefficient_unit", "系数单位", 17)]
    for cl in ["90", "95"]:
        for field in ["global", "SM", "positive", "negative"]:
            cutcols.append(col("cmax_" + cl + "_" + field, "|c|max " + cl + " " + field, 24, "number", "0.000000E+00"))
    cutcols += [col("coefficient_intervals_90", "90%完整系数允许集", 90), col("coefficient_intervals_95", "95%完整系数允许集", 90), col("source", "来源绝对地址", 90), col("scan", "原曲线地址", 100)]
    tables.append(table("cutoff_scales", "截断能标", "LEFT有效抑制能标结果", "224条；|g|=1，GeV。全域下确界与SM分支分列；正负为LEFT系数c符号。dim8及full22限制见物理范围列。", cutcols, cutoff_rows, 9))
    tables.append(table("one_d_intervals", "一维区间", "一维允许区间数值明细", "每行一个连通区间；端点为数值。空端点只有在对应unbounded为TRUE时表示无穷，不代表0。", [col("id", "区间ID", 65), col("analysis", "分析组", 32), col("parameter", "参数", 25), col("confidence_percent", "名义CL [%]", 16, "integer"), col("delta_chi2", "Δχ²阈值", 15, "number", "0.00"), col("band", "区间序号", 12, "integer"), col("lower", "下端点", 18, "number"), col("upper", "上端点", 18, "number"), col("lower_unbounded", "下端无界", 15, "boolean"), col("upper_unbounded", "上端无界", 15, "boolean"), col("boundary_touch", "触及物理边界", 18, "boolean"), col("status", "状态", 32), col("source", "来源绝对地址", 90)], interval_rows))
    tables.append(table("scale_intervals", "能标区间", "能标完整允许区间", "保留每个符号/每个岛。无灵敏度行Λ∈(0,+∞)，0是开端点；有界系数含0时Λ上端无界。", [col("id", "能标区间ID", 75), col("analysis", "分析组", 38), col("version", "计算版本", 32), col("operator", "算符", 13), col("confidence_percent", "名义CL [%]", 16, "integer"), col("coefficient_sign", "系数符号", 16), col("lambda_min_GeV", "Λ下端 [GeV]", 20, "number", "#,##0.000"), col("lambda_max_GeV", "Λ上端 [GeV]", 20, "number", "#,##0.000"), col("upper_unbounded", "Λ上端无界", 18, "boolean"), col("lower_open", "Λ下端开区间", 18, "boolean"), col("SM_connected", "来自SM连通系数带", 24, "boolean"), col("dimension", "维数d", 9, "integer"), col("threshold", "Δχ²阈值", 15, "number", "0.00"), col("band", "原系数区间序号", 20, "integer"), col("c_lower", "有符号c下端", 24, "number", "0.000000E+00"), col("c_upper", "有符号c上端", 24, "number", "0.000000E+00"), col("c_abs_max", "|c|max", 24, "number", "0.000000E+00"), col("c_abs_min", "|c|min", 24, "number", "0.000000E+00"), col("status", "状态", 58), col("source", "来源绝对地址", 90)], scale_rows))
    tables.append(table("coefficient_intervals", "系数区间", "有符号LEFT系数允许区间", "Λ变换的直接输入；单位GeV^(4−d)。无界允许集不以有限网格边界替代。", [col("id", "系数区间ID", 70), col("analysis", "分析组", 38), col("version", "版本", 32), col("operator", "算符", 13), col("confidence_percent", "名义CL [%]", 16, "integer"), col("lower", "c下端", 24, "number", "0.000000E+00"), col("upper", "c上端", 24, "number", "0.000000E+00"), col("unit", "单位", 16), col("threshold", "Δχ²阈值", 15, "number", "0.00"), col("band", "区间序号", 12, "integer"), col("lower_unbounded", "下端无界", 15, "boolean"), col("upper_unbounded", "上端无界", 15, "boolean"), col("status", "状态", 48), col("source", "来源绝对地址", 90)], coefficient_rows))
    tables.append(table("benchmarks", "Benchmark", "逐项benchmark与比较范围", "论文数值、图形、输入控制和联合相对单组分别标识。相对差异=(本地/参考−1)；IoU为几何量。", [col("id", "比较ID", 60), col("family", "类别", 22), col("analysis", "分析组", 38), col("parameter_operator", "参数/算符", 48), col("local_value", "本地值", 20, "number"), col("reference_value", "参考值", 20, "number"), col("relative_difference", "相对差异", 18, "number", "0.00%"), col("IoU", "区域IoU", 18, "number", "0.00%"), col("max_endpoint_difference", "最大区间端点差", 22, "number"), col("unit", "单位", 20), col("difference", "差值", 18, "number"), col("version", "方法版本", 55), col("reference_kind", "参考类型", 44), col("local_intervals", "本地区间", 70), col("reference_intervals", "参考区间", 70), col("locator", "原文定位", 100), col("scope", "可比性与限制", 120), col("source", "来源绝对地址", 90)], benchmark))
    tables.append(table("chi_square_parts", "χ²分项", "既存最佳点的χ²数据项与pull项", "确定性回代；未重新优化。CsI2017仅按原χ²与α作代数拆分。太阳data-only的pull为0有明确方法依据。", [col("id", "分项ID", 70), col("record_id", "统计记录ID", 65), col("channel", "通道", 25), col("chi2", "χ²通道", 17, "number"), col("chi2_data", "χ²data", 17, "number"), col("chi2_pull", "χ²pull", 17, "number"), col("alpha", "α信号pull", 18, "number"), col("beta", "β背景pull", 18, "number"), col("sigma_alpha", "σα", 14, "number"), col("sigma_beta", "σβ", 14, "number"), col("events", "信号 events", 20, "number"), col("observed_total", "观测量总数", 20, "number"), col("n_observations", "观测数", 12, "integer"), col("decomposition", "拆分方式", 100), col("source", "来源绝对地址", 90)], part_rows))
    tables.append(table("joint_components", "联合组成", "三组联合最佳点的六通道组成", "24条×6通道=144行；所有通道均在同一个联合最佳c处取值。compatibility cost仅代数诊断，不是p值。", [col("id", "分项ID", 78), col("operator", "算符", 14), col("version", "版本", 32), col("channel", "底层通道", 27), col("joint_best_coefficient", "联合最佳系数", 24, "number", "0.000000E+00"), col("chi2_at_joint_best", "通道χ²", 18, "number"), col("chi2_joint_min", "联合χ²min", 18, "number"), col("compatibility_cost", "兼容代数代价", 20, "number"), col("not_a_pvalue", "不转为p值", 16, "boolean"), col("source", "来源绝对地址", 90)], joint_parts))
    tables.append(table("computation_routes", "程序路线", "逐实验P01–P10 Python职责", "7条路线×10步；源码存在、当次执行证据与科学接受分别记录。共享步骤不复制物理实现。", [col("id", "步骤ID", 42), col("route", "实验路线", 34), col("phase", "步骤", 11), col("responsibility", "职责", 28), col("input", "输入", 65), col("calculation", "计算内容", 75), col("output", "输出", 65), col("implementation", "实现状态", 34), col("python_files", "Python绝对地址/行号/函数", 130), col("route_status", "路线执行范围", 70), col("execution_evidence", "执行证据范围", 90), col("source", "来源绝对地址", 90)], route_rows, 5))
    tables.append(table("definitions", "定义与文献", "参数定义、统计合同与参考文献", "所有Λ数值采用C_abs=1；仅转换约定可在C7检查缩放，交付值固定恢复为1。参考文献与原文定位在同表。", [col("id", "定义ID", 30), col("category", "类别", 22), col("numeric_value", "数值", 21, "number", "0.000000E+00"), col("text_value", "定义/文献", 140), col("unit", "单位", 22), col("formula", "公式", 60), col("locator", "原文/函数定位", 110), col("source", "采用来源绝对地址", 100)], defs, 5))
    # The inherited manifests plus all explicitly displayed files constitute the protection baseline.
    for p in Path(__file__).parent.glob("*.py"): adopt(p.relative_to(ROOT).as_posix())
    write_json(out / "SOURCE_MANIFEST.json", SOURCES)
    source_rows = [{"id": f"S{i:03d}", "relative_path": p, "absolute_path": str(ROOT / p), "sha256": h} for i, (p, h) in enumerate(sorted(SOURCES.items()), 1)]
    tables.append(table("sources", "来源文件", "采用来源与SHA256", "本轮只读采用，生成前后核对；backup不参与科学输入发现。全部原结果保留原路径。", [col("id", "来源ID", 13), col("relative_path", "Gitup01相对路径", 105), col("sha256", "SHA256", 72), col("absolute_path", "完整绝对路径", 145)], source_rows, 3))

    for t in tables:
        for r in t["rows"]:
            for c in t["columns"]:
                v = r.get(c["key"])
                if c["kind"] in ["number", "integer"] and v is not None:
                    test("typed numeric " + t["id"] + " " + c["key"], isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v))
    counts.update({t["id"] + "_rows": len(t["rows"]) for t in tables})
    payload = {"schema": "cevns_results_summary/1", "date": "2026-11-15", "scope": "latest selected results; approximate local-model benchmark",
               "no_refit": True, "root": str(ROOT), "counts": counts, "manifest_counts": manifest_counts, "tables": tables,
               "two_dimensional_views": views, "source_manifest": str(out / "SOURCE_MANIFEST.json")}
    write_json(out / "TABLES.json", payload)
    (out / "tables").mkdir(exist_ok=True)
    for t in tables:
        with (out / "tables" / (t["id"] + ".csv")).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[c["key"] for c in t["columns"]], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(t["rows"])
    render_markdown(out, payload)
    test("source files unchanged after aggregation", all(sha(ROOT / p) == h for p, h in SOURCES.items()), files=len(SOURCES))
    # Keep the receipt concise; detailed checks are generated deterministically.
    write_json(out / "qa/NUMERICAL_CHECKS.json", {"status": "PASS_READ_ONLY_AGGREGATION", "counts": counts,
               "source_manifest_counts": manifest_counts, "protected_files": len(SOURCES), "checks": len(CHECKS),
               "failed": [r for r in CHECKS if not r["passed"]], "check_classes": ["source and route hashes", "row identities/counts", "stored-point chi2 decompositions",
               "224 cutoff curves, 90/95% full interval transforms and inverse", "joint six-channel sums and independent nuisance record", "82 surface/contour view hashes", "benchmark ratios", "typed numbers"],
               "scope": "No new optimization, coverage calibration, native input repair, or physical acceptance performed."})
    print(json.dumps({"output": str(out), "counts": {k: counts[k] for k in ["one_dimension", "SM_parameters", "NSI_one_dimension", "two_dimensions", "cutoff_all", "chi_square_rows", "time_forward_including_SM"]}, "tables": len(tables), "sources": len(SOURCES), "checks": len(CHECKS)}, ensure_ascii=False))


def md_table(rows, columns):
    def cell(v):
        text = fmt(v).replace("|", "\\|").replace("\n", "<br>")
        # A locator copied from the SM figure directory needs the report's base.
        return text.replace("](CSI2021_COMPARATOR_EVIDENCE.md)", "](<../../论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>)")
    return "\n".join(["| " + " | ".join(title for _, title in columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"] +
                     ["| " + " | ".join(cell(r.get(key)) for key, _ in columns) + " |" for r in rows])


def render_markdown(out, payload):
    ts = {t["id"]: t for t in payload["tables"]}
    parts = ["# 最新实验结果汇总表", "日期：2026-11-15。科学定位：**approximate local-model benchmark**。本轮汇总既存结果，只回代已存最佳点并核对χ²分解/能标变换，没有重新拟合或改变正式输入。",
             "[Excel完整工作簿](CEvNS_Results_Summary_20261115.xlsx) · [机器可读总表](TABLES.json) · [逐类CSV](tables/README.md) · [数值验收](qa/NUMERICAL_CHECKS.json) · [来源哈希](SOURCE_MANIFEST.json)",
             "一维66条=16 SM参数＋50 NSI；二维41面；CsI-time前向24点=1 SM＋23非零NSI。能标224条=24 dim-6主版＋176完整22控制＋24三组联合（2主＋22控制）。主版与控制分别保存，联合不是新增独立实验。",
             "## 实验及完成范围", md_table(ts["overview"]["rows"], [("analysis", "实验/处理方式"), ("one_d", "一维"), ("two_d", "二维"), ("cutoff_main", "能标主"), ("cutoff_control", "能标控制"), ("cutoff_joint", "能标联合"), ("completed", "已完成"), ("gap", "限制")]),
             "## SM前向与不同参照", "下面参考量并不统一等于实验观测；联合信号向量保留在完整工作簿。CsI-time名义SM与其NSI运行的SM略有数值差别，禁止混用归一化。",
             "**CsI2021 Comparator修订依据：** D. Akimov et al. (COHERENT), PRL129,081801(2022), arXiv:2110.07730v2，PDF/页脚第4页右栏Results第一段：论文SM为**341±11(theory)±42(experiment) events**；实验拟合信号为306±20 events，另列为数据。原文PE<60、t_rec<6 μs，profile形状/归一化且时间起点无先验浮动。本地固定零平移/参考窗归一化，99箱模板尚未认证等价。相对SM中心值+3.6556037203%只是总率算术benchmark。[逐字段原句、PDF指纹和边界](<../../论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>)。",
             md_table(ts["SM_predictions"]["rows"], [("analysis", "分析"), ("method", "方法"), ("SM_events", "SM events"), ("reference_events", "参考 events"), ("chi2_SM", "χ²SM"), ("reference_kind", "参考类型"), ("interpretation", "说明"), ("reference_locator", "文献定位")]),
             "## 一维SM参数", "仅sin²θW与fB已扫描；GF、核参数及振荡参数固定。弱角一维固定fB；fB一维固定弱角。data-only去掉原12%归一化pull，control保留；不能混作同一个统计定义。阈值1/2.71/3.84为68/90/95%名义标签。",
             md_table(ts["SM_parameters"]["rows"], [("analysis", "分析"), ("parameter", "参数/方法"), ("best_fit", "最佳值"), ("chi2_min", "χ²min"), ("interval_68", "68%完整允许集"), ("interval_90", "90%完整允许集"), ("interval_95", "95%完整允许集")]),
             "## 一维NSI", "实矢量ε，单坐标变化、其余NSI为0。非对角参数同时打开Hermitian共轭矩阵元；6个ττ坐标全轴平坦，最佳值空白表示不可辨识。",
             md_table(ts["NSI_one_dimension"]["rows"], [("analysis", "分析"), ("parameter", "参数"), ("best_fit", "最佳值"), ("chi2_min", "χ²min"), ("interval_68", "68%"), ("interval_90", "90%"), ("interval_95", "95%")]),
             "## 二维分析", "每个平面减去自己的二维全域最小值，阈值2.30/4.61/5.99。3个ττ平面全域平坦；9个单太阳总数平面有连续最佳曲线，列出的点仅为代表。全部82份面及轮廓原地址列在工作簿，不能将显示窗[-1,1]当先验。",
             "太阳联合同时放开弱角/fB时最佳值落在弱角0的物理边界，反映强相关与简并；不能解释成测得sin²θW=0，亦不能照搬条件一维精度。",
             md_table(ts["two_dimension"]["rows"], [("analysis", "分析"), ("parameter_x", "x"), ("parameter_y", "y"), ("best_x", "最佳/代表x"), ("best_y", "最佳/代表y"), ("chi2_min", "χ²min"), ("best_fit_semantics", "含义")]),
             "## χ²与联合统计", "完整工作簿“χ²汇总”有340条，分项另表。SM点/一维/二维/能标各有自己的物理定义，不能只按χ²数值互相排名。未给dof、p值或coverage toys结果。",
             "地面：Σ[D−(1+α)S−(1+β)B]²/σ²＋α²/σα²＋β²/σβ²；CONUS无β。太阳三个拟合产额D=[3.5,75,10.7]、σ=[1.2985,27.975,3.9483] events，原模型各有独立12%归一化pull。",
             "三组能标联合含CONUS19箱、CsI九箱、Ar十二箱及三个太阳单bin，共43观测、8独立pull。先在同一个系数c相加绝对χ²，再求联合最小值；CsI＋Ar不重复计入，也不加入重叠CsI-time/2017。跨实验相关系统误差未认证，固定弱角仍为CONUS/太阳0.23857及CsI/Ar0.2387。",
             "## 截断能标：定义与主结果", r"采用c=s|g|/Λ^(d−4)，|g|=1，Λ=(|g|/|c|)^(1/(d−4))，单位GeV。维六矢量c=−√2 GF ε，所以正c对应负ε。Λ是约定的EFT有效抑制能标，不是已认证的UV粒子质量或有效理论适用截止能。",
             "全域保守值是完整允许集的下确界，不代表所有更大的Λ均允许。严格SM分支只取包含c=0的系数区间；两个符号及全部孤岛在“能标区间”保存。无响应方向所有Λ>0允许，没有有限下限。名义90/95%阈值为2.71/3.84。",
             md_table([r for r in ts["cutoff_scales"]["rows"] if r["version"] == "dim6_self_consistent"], [("analysis", "分析"), ("operator", "算符"), ("lambda_90_global", "Λ90全域/GeV"), ("lambda_90_SM", "Λ90 SM分支/GeV"), ("lambda_90_positive", "Λ90正c/GeV"), ("lambda_90_negative", "Λ90负c/GeV"), ("lambda_95_global", "Λ95全域/GeV"), ("status", "状态")]),
             "## 完整22算符固定SM态控制", "以下含176条单组/联合组控制及22条三组联合控制。LNC=ee；LNV=e↔μ过渡，偶极/张量反对称、标量对称。太阳固定SM传播；一般LEFT逐点传播尚未实现。dim-8原生点正定性（PSD）问题未闭合，其数值不得称为已接受物理排除。",
             md_table([r for r in ts["cutoff_scales"]["rows"] if r["version"] == "full22_fixed_SM_control"], [("analysis", "分析"), ("operator", "算符"), ("dimension", "d"), ("flavor", "味"), ("lambda_90_global", "Λ90全域/GeV"), ("lambda_90_SM", "Λ90 SM分支/GeV"), ("lambda_95_global", "Λ95全域/GeV"), ("physical_status", "接受范围"), ("status", "灵敏度")]),
             "## CsI-time前向点", "只有前向预测，尚无原生99箱统计拟合；不能给这些点补造χ²、CL或能标限值。",
             md_table(ts["NSI_forward"]["rows"], [("point_id", "点"), ("nonzero_epsilon_upper_triangle", "非零ε"), ("signal_events", "信号 events"), ("ratio_to_SM", "相对本运行SM"), ("status", "状态")]),
             "## 对应benchmark", "引用类型、方法版本和可比性逐行给出。Fig.3参考是PDF柱顶几何数字化；Fig.4 IoU是指定图框内几何交并比。完整22控制差异不能只用匹配的矢量柱代表。联合参考为本地最强单组时，明确不当成论文参考。",
             md_table(ts["benchmarks"]["rows"], [("family", "类别"), ("analysis", "分析"), ("parameter_operator", "参数/算符"), ("version", "版本"), ("local_value", "本地"), ("reference_value", "参考"), ("relative_difference", "相对差异(小数)"), ("IoU", "IoU"), ("max_endpoint_difference", "端点差"), ("reference_kind", "参考类型"), ("locator", "定位"), ("scope", "范围")]),
             "## 定义、来源与文献", md_table(ts["definitions"]["rows"], [("id", "ID"), ("category", "类别"), ("numeric_value", "数值"), ("text_value", "定义或引文"), ("unit", "单位"), ("locator", "定位")]),
             "## 生成与核验", "Python读取明确指定的最新结果JSON并确定性导出TABLES.json及17类CSV；JavaScript使用bundled @oai/artifact-tool生成Excel。全部能标允许集由系数区间独立正逆变换核对；一维/二维最佳点回代数据项与pull项；旧来源文件核对SHA256。",
             "[程序和重跑命令](../../examples/results_summary/README.md) · [文件与验收说明](README.md) · [70步程序路线CSV](tables/computation_routes.csv)"]
    (out / "RESULTS.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / "outputs"):
        raise ValueError("Output must be inside Gitup01/outputs")
    if (out / "TABLES.json").exists():
        raise FileExistsError("Use a new result-summary run; existing numerical tables are immutable")
    if not (out / "WRITE_PLAN.json").exists():
        raise FileNotFoundError("Create the explicit write plan before aggregation")
    (out / "qa").mkdir(exist_ok=True)
    collect(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
