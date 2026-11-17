"""Three-group cutoff joint: sum absolute profiled chi2, then minimize once.

Create-only analysis. Six adopted data channels, eight independent Gaussian
nuisances, no certified cross-experiment covariance. The two vector routes use
point-dependent solar propagation; the full22 routes remain fixed-state controls.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, new_run, read, sha, write_json
from inference import Gaussian, scan
from model_adapters import (Ground, GroundObjective, Solar, SolarObjective,
                            SOLAR_SAMPLES, load_ground)
from run_full22 import PolynomialRoute
from forward22 import KEYS, LI2026_OPERATOR_SPECS, flavor_tensor

GROUND_NAMES = ("CONUS_plus", "CsI2021_9PE", "Ar2020_average")
MAIN_GROUPS = ("CONUS_plus", "CsI2021_9PE+Ar2020_average", "Solar_three_singlebins")
OLD_DIM6 = "outputs/cutoff_scales/20261114_dim6_run1"
OLD_FULL = "outputs/cutoff_scales/20261114_full22_control_run1"
FORWARD = "outputs/cutoff_scales/20261114_full22_forward_run1"


class CombinedObjective:
    """Sum objectives in one physical coefficient, regardless of their scales."""

    def __init__(self, objectives, coefficient_scale):
        self.objectives = tuple(objectives)
        self.coefficient_scale = float(coefficient_scale)
        self.ratios = tuple(self.coefficient_scale/o.coefficient_scale for o in self.objectives)
        self.no_sensitivity = all(o.no_sensitivity for o in self.objectives)
        self.rational = None

    def __call__(self, x):
        return sum(o(np.asarray(x)*r) for o, r in zip(self.objectives, self.ratios))

    def domain(self, threshold=3.84):
        # Any allowed total has every nonnegative component <= total SM+Delta.
        level = float(self(0.))+threshold
        intervals, proofs = [], []
        for objective, ratio in zip(self.objectives, self.ratios):
            if objective.no_sensitivity:
                continue
            interval, proof = objective.domain(threshold=level-float(objective(0.)))
            intervals.append(np.asarray(interval)/ratio)
            proofs.append({"component_scale": objective.coefficient_scale,
                           "common_scale": self.coefficient_scale,
                           "interval_common_x": intervals[-1], "proof": proof})
        if not intervals:
            return (-1., 1.), {"proof": "all components exactly insensitive"}
        lo, hi = max(p[0] for p in intervals), min(p[1] for p in intervals)
        if not lo < 0 < hi:
            raise ValueError("no certified joint domain containing SM")
        return (lo, hi), {"proof": "intersect necessary component bounds at TOTAL SM chi2 + threshold",
                          "total_level": level, "components": proofs}


def verify_sources(record):
    stale = [p for p, h in record["source_manifest"].items() if sha(ROOT/p) != h]
    if stale:
        raise ValueError("stale adopted numerical source: "+repr(stale))


def full_routes(adopted, label):
    ground = {}
    for name, old in adopted.items():
        with np.load(ROOT/FORWARD/(name+"_"+label+".npz"), allow_pickle=False) as a:
            full = a["full_kernel"].copy()
        ground[name] = Ground(name, full, old.rhos, old.channel, old.angle, KEYS)
    with np.load(ROOT/FORWARD/("Solar_"+label+".npz"), allow_pickle=False) as a:
        polynomial = a["polynomial"].copy()
    data = read("data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json")["samples"]
    solar = []
    for i, name in enumerate(SOLAR_SAMPLES):
        d = data[name]
        channel = Gaussian(np.array([d["D"]]), np.array([d["sigma_stat"]]), d["pull_sigma"])
        solar.append(PolynomialRoute(name, polynomial[i], channel))
    return ground, solar


def channel_data(objective, x):
    if isinstance(objective, CombinedObjective):
        rows = []
        for o, ratio in zip(objective.objectives, objective.ratios):
            rows.extend(channel_data(o, x*ratio))
        return rows
    if isinstance(objective, GroundObjective):
        return [(r.name, r.channel, s) for r, s in zip(objective.routes, objective.signals(x))]
    if isinstance(objective, SolarObjective):
        signals = objective.solar.signals(x, objective.quark)
        return [(SOLAR_SAMPLES[i], objective.solar.channels[i], np.array([signals[i]])) for i in objective.indices]
    raise TypeError(type(objective))


def block_least_squares(rows):
    """Independent joint eight-nuisance solve using one block design matrix."""
    npull = sum(1+(c.background is not None) for _, c, _ in rows)
    nobs = sum(len(c.observed) for _, c, _ in rows)
    design, rhs = np.zeros((nobs+npull, npull)), np.zeros(nobs+npull)
    i, j = 0, 0
    for _, channel, signal in rows:
        n = len(channel.observed)
        background = 0 if channel.background is None else channel.background
        rhs[i:i+n] = (channel.observed-signal-background)/channel.sigma
        design[i:i+n, j] = signal/channel.sigma
        design[nobs+j, j] = 1/channel.alpha_sigma
        i2 = j+1
        if channel.background is not None:
            design[i:i+n, i2] = channel.background/channel.sigma
            design[nobs+i2, i2] = 1/channel.beta_sigma
            i2 += 1
        i, j = i+n, i2
    pulls = np.linalg.lstsq(design, rhs, rcond=None)[0]
    return float(np.sum((rhs-design@pulls)**2)), pulls


def validate(objective, result):
    points = [0., float(result["bestfit_x"])]
    points += [c["x"] for c in result["root_checks"]]
    checks = []
    for x in points:
        rows = channel_data(objective, x)
        names = [r[0] for r in rows]
        if len(names) != len(set(names)) or len(names) != 6:
            raise ValueError("duplicate/missing underlying dataset")
        cost, pulls = block_least_squares(rows)
        expected = float(objective(x))
        np.testing.assert_allclose(cost, expected, atol=3e-8, rtol=3e-10)
        checks.append({"x": x, "chi2_profile": expected, "block_least_squares_chi2": cost,
                       "difference": cost-expected, "pulls": pulls,
                       "observables": sum(len(r[1].observed) for r in rows), "nuisances": len(pulls)})
    return checks


def analyze(output, *, grid_size=2049):
    started = time.perf_counter()
    output = new_run(output)
    (output/"scans").mkdir()
    os.environ["NUMBA_CACHE_DIR"] = str(output/"cache")
    old = {"dim6": read(OLD_DIM6+"/RESULTS.json"), "full22": read(OLD_FULL+"/RESULTS.json")}
    for record in old.values():
        verify_sources(record)
    adopted, sources = load_ground()
    solar = Solar()
    sources.update(solar.files)
    for directory in (OLD_DIM6, OLD_FULL):
        for file in ("RESULTS.json", "SOURCE_MANIFEST.json"):
            sources[directory+"/"+file] = sha(ROOT/directory/file)
    for name in (*GROUND_NAMES, "Solar"):
        for label in ("baseline", "refined"):
            p = f"{FORWARD}/{name}_{label}.npz"
            sources[p] = sha(ROOT/p)
    for f in ("INPUTS_AND_IDENTITIES.json", "NATIVE_SLOW_VALIDATION.json", "NATIVE_PSD_POINT_DETAILS.json"):
        p = FORWARD+"/"+f
        sources[p] = sha(ROOT/p)
    sources.update(old["full22"]["source_manifest"])
    for p in HERE.glob("*.py"):
        sources[p.relative_to(ROOT).as_posix()] = sha(p)
    results, validations = [], []

    def save(objective, key, version, proof, refinement=None):
        result = scan(objective, proof[0], coefficient_scale=objective.coefficient_scale,
                      dimension=key[0], rational=objective.rational,
                      grid_size=grid_size, no_sensitivity=objective.no_sensitivity)
        identifier = version+f"_C{key[0]}{key[2]}{key[1]}"
        x, chi2 = result.pop("grid_x"), result.pop("chi2_grid")
        rows = channel_data(objective, result["bestfit_x"])
        components = {name: float(channel.profile(s)[0]) for name, channel, s in rows}
        if isinstance(objective, CombinedObjective):
            component_curves = np.stack([o(x*r) for o, r in zip(objective.objectives, objective.ratios)])
        else:
            component_curves = np.stack([r.channel.profile(s)[0] for r, s in zip(objective.routes, objective.signals(x))])
            component_curves = np.stack([component_curves[0], component_curves[1:3].sum(axis=0), component_curves[3:].sum(axis=0)])
        np.testing.assert_allclose(component_curves.sum(axis=0), chi2, atol=1e-10, rtol=1e-12)
        np.savez_compressed(output/"scans"/(identifier+".npz"), x=x,
                            coefficient=x*objective.coefficient_scale, chi2=chi2,
                            delta_chi2=chi2-result["chi2_min"], component_chi2=component_curves,
                            component_names=np.array(MAIN_GROUPS))
        previous = [r for r in old["dim6" if version=="dim6_self_consistent" else "full22"]["results"]
                    if tuple(r["operator_key"]) == tuple(key) and r["analysis_group"] in MAIN_GROUPS]
        separate_minima = sum(r["chi2_min"] for r in previous)
        compatibility = result["chi2_min"]-separate_minima
        if compatibility < -1e-6:
            raise ValueError("joint minimum below sum of independent minima")
        result.update({"analysis_group": "CONUS_COHERENT_Solar_joint", "version": version,
                       "operator_key": key, "operator_id": f"C{key[0]}{key[2]}{key[1]}",
                       "flavor": "ee" if next(s for s in LI2026_OPERATOR_SPECS if s.key==tuple(key)).lepton_number=="LNC" else "e_mu_transition",
                       "domain_proof": proof[1], "scan_path": "scans/"+identifier+".npz",
                       "component_chi2_at_joint_bestfit": components,
                       "sum_separate_group_minima": separate_minima,
                       "compatibility_cost_no_calibrated_pvalue": compatibility,
                       "refinement": refinement,
                       "physical_validation_status": ("CONTROL_ONLY_POINTWISE_PSD_NOT_CLOSED" if key[0]==8 else
                           "FIXED_SM_SOLAR_CONTROL" if version.startswith("full22") else "ADOPTED_DIM6_LOCAL_BENCHMARK")})
        check = validate(objective, result)
        validations.append({"version": version, "operator_key": key, "checks": check,
                            "maximum_root_residual": max(abs(c["residual"]) for c in result["root_checks"])})
        results.append(result)
        print(version, result["operator_id"], "90CL", result["confidence"]["90"]["global_GeV"],
              "chi2min", result["chi2_min"], "compatibility_cost", compatibility, flush=True)

    for quark in ("u", "d"):
        key = (6, 1, quark)
        ground = [GroundObjective([adopted["CONUS_plus"]], key),
                  GroundObjective([adopted["CsI2021_9PE"], adopted["Ar2020_average"]], key)]
        sol = SolarObjective(solar, (0, 1, 2), quark)
        objective = CombinedObjective([*ground, sol], sol.coefficient_scale)
        save(objective, key, "dim6_self_consistent", objective.domain())

    levels = {label: full_routes(adopted, label) for label in ("baseline", "refined")}
    for spec in LI2026_OPERATOR_SPECS:
        objectives = {}
        for label, (ground, sol) in levels.items():
            routes = [ground[name] for name in GROUND_NAMES]+sol
            objectives[label] = GroundObjective(routes, spec.key, flavor=flavor_tensor(spec.key))
        baseline = objectives["baseline"]
        reference = scan(baseline, baseline.domain()[0], coefficient_scale=baseline.coefficient_scale,
                         dimension=spec.dimension, rational=baseline.rational, grid_size=grid_size)
        refined = objectives["refined"]
        save(refined, spec.key, "full22_fixed_SM_control", refined.domain(),
             {"baseline_Lambda_90_GeV": reference["confidence"]["90"]["global_GeV"],
              "baseline_Lambda_95_GeV": reference["confidence"]["95"]["global_GeV"]})
        for cl in ("90", "95"):
            change = results[-1]["confidence"][cl]["global_GeV"]/reference["confidence"][cl]["global_GeV"]-1
            results[-1]["refinement"]["relative_change_"+cl] = change
            if abs(change) > .005:
                raise ValueError("joint refinement exceeds 0.5 percent")

    contract = {"definition": "chi2_joint(c)=chi2_CONUS(c)+chi2_CsI(c)+chi2_Ar(c)+sum_k chi2_solar_k(c); Delta=chi2_joint-min_c chi2_joint",
                "data_channels": list(GROUND_NAMES)+list(SOLAR_SAMPLES), "observables": 43, "nuisances": 8,
                "nuisance_assumption": "independent Gaussian pulls, following adopted Eq86/88/90 local benchmark; no cross-experiment covariance certified",
                "signal_pull_sigmas": [0.169, 0.125, 0.12, 0.12, 0.12, 0.12],
                "background_pull_sigmas": {"CsI2021_9PE": .35, "Ar2020_average": .146},
                "weak_angles": {"CONUS_solar": .23857, "CsI_Ar": .2387},
                "solar_flux_scale": 1, "thresholds_1DOF_nominal": {"90": 2.71, "95": 3.84},
                "calibrated_coverage": False,
                "caveats": ["No duplicated CsI+Ar joint on top of its members; CsI-time/2017 excluded",
                            "dim6 vector solar propagation updated with SNuDD v3.4.1 at every c",
                            "full22 solar rho fixed to SM; LNV e<->mu explicit local scenario",
                            "dim8 native pointwise PSD failure retained; no accepted physical dim8 limit",
                            "shared source/nuclear/solar-flux correlations not modeled or fitted",
                            "compatibility cost is not a calibrated significance or goodness-of-fit p value"]}
    record = {"schema": SCHEMA, "part_id": PART, "run_id": output.name,
              "stage": "THREE_GROUP_JOINT_WITH_SEPARATE_MAIN_AND_CONTROL", "date": "2026-11-14",
              "statistics_contract": contract, "results": results,
              "source_manifest": sources, "wall_seconds": time.perf_counter()-started}
    write_json(output/"RESULTS.json", record)
    write_json(output/"SOURCE_MANIFEST.json", sources)
    write_json(output/"VALIDATION.json", validations)
    rows = []
    for r in results:
        for cl, c in r["confidence"].items():
            rows.append({"version": r["version"], "operator": r["operator_id"], "CL": cl,
                         "Lambda_joint_GeV": c["global_GeV"], "Lambda_SM_connected_GeV": c["sm_connected_GeV"],
                         "chi2_min": r["chi2_min"], "bestfit_coefficient": r["bestfit_coefficient"],
                         "Delta_chi2_SM": r["delta_chi2_SM"],
                         "compatibility_cost": r["compatibility_cost_no_calibrated_pvalue"],
                         "physical_validation_status": r["physical_validation_status"]})
    with (output/"JOINT_LIMITS.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (output/"README.md").write_text(
        "# 三组联合χ²：独立截断能标Part\n\n"
        "[结果与完整区间](RESULTS.json) · [限值表](JOINT_LIMITS.csv) · [独立统计验收](VALIDATION.json) · "
        "[来源指纹](SOURCE_MANIFEST.json) · [代码与重跑](../../../examples/cutoff_scales/README.md)\n\n"
        "6份底层数据共43个观测、8个独立Gaussian nuisance。先相加绝对profile χ²，再求联合最小值；"
        "每份数据仅出现一次。2个dim-6矢量主结果逐点重算太阳传播；22算符另为固定太阳SM态控制。"
        "dim-8原生点正定性拒绝尚未闭合，控制数值不是已接受物理排除。"
        "独立pull近似未包含跨实验共享通量/核响应等协方差；采用原主线不同固定弱角，不将其称为作者等价的全局拟合。\n",
        encoding="utf-8")
    print("WROTE", output, "routes", len(results), "seconds", record["wall_seconds"], flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--grid-size", type=int, default=2049)
    a = p.parse_args()
    analyze(a.output, grid_size=a.grid_size)
