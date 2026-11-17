"""Full22 single-operator limits; solar is an explicitly fixed-SM-state control."""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, new_run, read, sha, write_json
from inference import scan
from model_adapters import (Ground, GroundObjective, GROUND_GROUPS, SOLAR_GROUPS, SOLAR_SAMPLES,
                            SOLAR, load_ground)
from forward22 import KEYS, flavor_tensor, LI2026_OPERATOR_SPECS


@dataclass
class PolynomialRoute:
    name: str
    coefficients: np.ndarray
    channel: object

    def polynomial(self, operator, flavor=None):
        return self.coefficients[KEYS.index(tuple(operator))][:, None]


def run(forward, output):
    started = time.perf_counter()
    forward = Path(forward).resolve()
    if not forward.is_relative_to((ROOT/"outputs/cutoff_scales").resolve()):
        raise ValueError("explicit full22 forward directory must belong to this Part")
    required = [forward/(name+"_"+label+".npz") for name in ("CONUS_plus", "CsI2021_9PE", "Ar2020_average", "Solar") for label in ("baseline", "refined")]
    if not all(path.is_file() for path in required):
        raise ValueError("full22 baseline and refined ground/solar inputs are not all available")
    output = new_run(output); (output/"scans").mkdir()
    adopted, source_files = load_ground()
    sources = {path.relative_to(ROOT).as_posix(): sha(path) for path in required}
    for name in ("NATIVE_SLOW_VALIDATION.json", "INPUTS_AND_IDENTITIES.json"):
        path = forward/name
        sources[path.relative_to(ROOT).as_posix()] = sha(path)
    for item in read((forward/"INPUTS_AND_IDENTITIES.json").relative_to(ROOT).as_posix())["direct_source_files"]:
        sources[item["path"]] = item["sha256"]
    sources.update(source_files)
    for path in HERE.glob("*.py"):
        sources[path.relative_to(ROOT).as_posix()] = sha(path)
    for rel in ("data/responses/responses_all.json", "data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md",
                "data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md",
                "data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt",
                "data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json",
                "data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_default.csv",
                f"{SOLAR}/propagation_source/source.npz", f"{SOLAR}/propagation_source/manifest.json"):
        sources[rel] = sha(ROOT/rel)
    data = read("data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json")["samples"]
    from inference import Gaussian
    channels = [Gaussian(np.array([data[s]["D"]]), np.array([data[s]["sigma_stat"]]), data[s]["pull_sigma"]) for s in SOLAR_SAMPLES]
    levels = {}
    for label in ("baseline", "refined"):
        ground = {}
        for name, old in adopted.items():
            with np.load(forward/(name+"_"+label+".npz"), allow_pickle=False) as a:
                full = a["full_kernel"].copy()
            ground[name] = Ground(name, full, old.rhos, old.channel, old.angle, KEYS)
        with np.load(forward/("Solar_"+label+".npz"), allow_pickle=False) as a:
            polynomial = a["polynomial"].copy()
        solar = [PolynomialRoute(name, polynomial[i], channels[i]) for i, name in enumerate(SOLAR_SAMPLES)]
        levels[label] = (ground, solar)
    results, convergence = [], []
    for name, members in {**GROUND_GROUPS, **SOLAR_GROUPS}.items():
        for spec in LI2026_OPERATOR_SPECS:
            key, flavor = spec.key, flavor_tensor(spec.key)
            scans = {}
            proofs = {}
            for label, (ground, solar) in levels.items():
                routes = [ground[k] for k in members] if name in GROUND_GROUPS else [solar[k] for k in members]
                objective = GroundObjective(routes, key, flavor=flavor)
                domain, proof = objective.domain()
                scans[label] = scan(objective, domain, coefficient_scale=objective.coefficient_scale,
                                    dimension=spec.dimension, rational=objective.rational,
                                    grid_size=1025, no_sensitivity=objective.no_sensitivity)
                proofs[label] = proof
            result, previous = scans["refined"], scans["baseline"]
            changes = {}
            for cl, c in result["confidence"].items():
                a, b = c.get("global_GeV"), previous["confidence"][cl].get("global_GeV")
                changes[cl] = None if a is None or b is None else float(a/b-1)
            numeric_status = "PASS_LAMBDA_REFINEMENT" if all(v is None or abs(v) <= .005 for v in changes.values()) else "REFINEMENT_REQUIRED"
            convergence.append({"analysis_group": name, "operator": spec.name, "relative_lambda_change": changes, "status": numeric_status})
            identifier = f"{name}_{spec.name}"
            x, chi2 = result.pop("grid_x"), result.pop("chi2_grid")
            np.savez_compressed(output/"scans"/(identifier+".npz"), x=x, coefficient=x*result["coefficient_scale"], chi2=chi2, delta_chi2=chi2-result["chi2_min"])
            result.update({"analysis_group": name, "operator_id": f"C{key[0]}{key[2]}{key[1]}", "operator_key": list(key),
                           "lepton_number": spec.lepton_number, "flavor": "ee" if spec.lepton_number == "LNC" else "e_mu_transition",
                           "flavor_tensor_per_unit_coefficient": flavor, "coefficient_unit": f"GeV^{4-spec.dimension}",
                           "method_id": "ground_restored_full22" if name in GROUND_GROUPS else "solar_full22_fixed_SM_rho_control",
                           "domain_proof": proofs["refined"], "baseline_limit_90_GeV": previous["confidence"]["90"].get("global_GeV"),
                           "refinement_status": numeric_status, "refinement_relative_lambda_change": changes,
                           "physical_validation_status": "CONTROL_ONLY_POINTWISE_PSD_NOT_CLOSED" if spec.dimension == 8 else "LOCAL_MODEL_CONTROL",
                           "scan_path": "scans/"+identifier+".npz"})
            results.append(result)
            print(name, spec.name, result["status"], result["confidence"]["90"].get("global_GeV"), numeric_status, flush=True)
    record = {"schema": SCHEMA, "part_id": PART, "stage": "FULL22_FIXED_SM_SOLAR_CONTROL", "date": "2026-11-14",
              "run_id": output.name, "results": results, "source_manifest": sources,
              "claim_level": "independent local-model full22 control; not author-equivalent; not arbitrary-LEFT self-consistent solar propagation",
              "flavor_contract": {"LNC": "real ee matrix element", "LNV": "e<->mu transition pair; antisymmetric dipole/tensor and symmetric scalar; each entry has magnitude c",
                                  "source_note": "all actual SNS source species retained; LNV pair can act on incoming mu as well as e",
                                  "primary_locator": "2601.19883v2 PDF p4 Eqs10-12; vanishing same-flavor dipole/tensor; chosen transition is explicit local scenario",
                                  "runtime_contract": "all LNV diagonals remain zero; no change to shared operator validation"},
              "solar_contract": "rho(E;SM) reconstructed from adopted SNuDD v3.4.1 arrays, fixed while scattering changes; this is a control separate from dim6 self-consistent scan",
              "convergence": convergence, "wall_seconds": time.perf_counter()-started,
              "native_validation": read((forward/"NATIVE_SLOW_VALIDATION.json").relative_to(ROOT).as_posix()),
              "remaining_capabilities": ["general-LEFT self-consistent solar matter evolution", "native CsI-time likelihood", "CsI2017 parameter forward", "author-equivalent source and likelihood certification"]}
    write_json(output/"RESULTS.json", record); write_json(output/"SOURCE_MANIFEST.json", sources)
    rows = []
    for r in results:
        for cl, c in r["confidence"].items():
            rows.append({"analysis_group": r["analysis_group"], "operator": r["operator_id"], "dimension":r["dimension"], "flavor":r["flavor"],
                         "CL":cl,"status":c["status"],"Lambda_global_GeV":c.get("global_GeV"),"Lambda_SM_connected_GeV":c.get("sm_connected_GeV"),
                         "SM_status":c.get("sm_status"),"Lambda_C_positive_GeV":c.get("positive_GeV"),"Lambda_C_negative_GeV":c.get("negative_GeV"),
                         "refinement_status":r["refinement_status"],"physical_validation_status":r["physical_validation_status"],"method_id":r["method_id"]})
    with (output/"CUTOFF_LIMITS.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (output/"README.md").write_text("# 完整22算符：独立本地模型控制计算\n\n"
        "[逐路线完整允许集](RESULTS.json) · [限值表](CUTOFF_LIMITS.csv) · [采用来源](SOURCE_MANIFEST.json) · "
        "[代码与方法合同](../../../examples/cutoff_scales/README.md)\n\n"
        "22算符×8分析组，共176条路线。LNC采用ee，LNV采用明确的e↔μ过渡；"
        "太阳固定SM传播控制与dim-6逐点传播结果分别保存。不能将此控制结果写成任意LEFT太阳传播已完成。"
        "地面从可读数值资源/说明/保存记录重建，原网格四算符投影已核对保存核；正式YAML/NPZ仍拒读。"
        "基线与加密能标变化、零响应及待细化项见RESULTS.json。\n",encoding="utf-8")
    print("WROTE_FULL22", output, "routes",len(results), "seconds",record["wall_seconds"], flush=True)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--forward",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();run(a.forward,a.output)
