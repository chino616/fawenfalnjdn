"""Execute the isolated adopted-kernel dim-6 cutoff benchmark, create-only."""
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
from inference import scan


def run(output, grid_size=2049):
    started = time.perf_counter()
    output = new_run(output)
    os.environ["NUMBA_CACHE_DIR"] = str(output/"cache")
    from model_adapters import (BASIS, GROUND_GROUPS, SOLAR_GROUPS, GroundObjective, SolarObjective,
                                Solar, load_ground, validate_gaussian_and_polynomials)
    baseline = read("outputs/cutoff_scales/20261114_implementation_baseline/BASELINE.json")
    changed = [path for path, value in baseline["protected"].items() if sha(ROOT/path) != value]
    if changed:
        raise ValueError("protected mainline inputs/source changed: "+repr(changed))
    routes, files = load_ground()
    validation = validate_gaussian_and_polynomials(routes)
    solar = Solar()
    files.update(solar.files)
    for path in HERE.glob("*.py"):
        files[path.relative_to(ROOT).as_posix()] = sha(path)
    (output/"scans").mkdir()
    results = []
    work = [(name, operator, GroundObjective([routes[k] for k in members], operator), "ground_fixed_source_ee")
            for name, members in GROUND_GROUPS.items() for operator in BASIS]
    work += [(name, (6, 1, q), SolarObjective(solar, indices, q), "solar_ee_self_consistent_snudd_v341")
             for name, indices in SOLAR_GROUPS.items() for q in ("u", "d")]
    for name, operator, objective, method in work:
        domain, proof = objective.domain()
        result = scan(objective, domain, coefficient_scale=objective.coefficient_scale, dimension=operator[0],
                      rational=objective.rational, grid_size=grid_size, no_sensitivity=objective.no_sensitivity)
        identifier = f"{name}_C{operator[0]}{operator[2]}{operator[1]}"
        x, values = result.pop("grid_x"), result.pop("chi2_grid")
        np.savez_compressed(output/"scans"/(identifier+".npz"), x=x,
                            coefficient=x*objective.coefficient_scale, chi2=values, delta_chi2=values-result["chi2_min"])
        result.update({"analysis_group": name, "operator_key": list(operator), "operator_id": f"C{operator[0]}{operator[2]}{operator[1]}",
                       "flavor": "ee", "coefficient_tensor": "c * diag(1,0,0)", "method_id": method,
                       "coefficient_unit": "GeV^-2", "domain_proof": proof, "scan_path": "scans/"+identifier+".npz"})
        results.append(result)
        print(name, result["operator_id"], result["status"], result["confidence"]["90"].get("global_GeV"), flush=True)
    protected_changes = [path for path, value in baseline["protected"].items() if sha(ROOT/path) != value]
    if protected_changes:
        raise ValueError("protected file changed during cutoff run")
    record = {"schema": SCHEMA, "part_id": PART, "stage": "DIM6_ADOPTED_KERNEL_BENCHMARK", "date": "2026-11-14",
              "claim_level": "approximate local-model benchmark; no author-equivalent likelihood claim",
              "run_id": output.name, "mainline_root": str(ROOT), "results": results,
              "scope": {"operator_structures": [list(k) for k in BASIS], "flavor": "real ee", "route_count": len(results),
                        "fixed_solar_flux_scale": 1., "solar_method": "continuous_acceptance + SNuDD v3.4.1; XENON flat_sensitivity",
                        "ground_method": "frozen four-operator kernels; Gaussian CsI and average-error Ar; native packages remain unreadable",
                        "untested_claims": "new native package loading, arbitrary LEFT solar scattering, complete22, calibrated coverage"},
              "validation": {"checks": validation, "protected_files_checked": len(baseline["protected"]), "protected_changes": protected_changes,
                             "limits": "saved-kernel polynomial/full/pair and independent statistics checks; new axial native Slow holdouts require readable forward assembly"},
              "source_manifest": files, "wall_seconds": time.perf_counter()-started}
    write_json(output/"RESULTS.json", record)
    write_json(output/"SOURCE_MANIFEST.json", files)
    rows = []
    for r in results:
        for cl, row in r["confidence"].items():
            rows.append({"analysis_group": r["analysis_group"], "operator": r["operator_id"], "flavor": r["flavor"], "CL": cl,
                         "status": row["status"], "Lambda_global_GeV": row.get("global_GeV"),
                         "Lambda_global_TeV": None if row.get("global_GeV") is None else row["global_GeV"]/1000,
                         "Lambda_SM_connected_GeV": row.get("sm_connected_GeV"), "SM_status": row.get("sm_status"),
                         "Lambda_C_positive_GeV": row.get("positive_GeV"), "Lambda_C_negative_GeV": row.get("negative_GeV"),
                         "intervals_coefficient": str(row.get("intervals_coefficient", [])), "method_id": r["method_id"]})
    with (output/"CUTOFF_LIMITS.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (output/"STATISTICS_CONTRACT.md").write_text(
        "# 独立截断能标统计合同\n\n单个实ee LEFT新物理系数，SM保留。90/95%使用1DOF名义阈值2.71/3.84。"
        "每条联合曲线先在同一系数处相加χ²，再减该联合曲线的全局最小值。"
        "global conservative、严格含零SM分支、正负系数和完整Λ区间分别保存。无灵敏度不提供有限限值。\n\n"
        "地面直接采用已存events/bin观测和核，不再次转换箱宽。CsI九箱和Ar均误差各自独立nuisance；"
        "CONUS为19箱单pull。太阳三个拟合信号总数各自12%pull，固定fB=1，使用当前SNuDD v3.4.1 ee传播逐点更新。"
        "XENON尾段沿用flat_sensitivity。CsI-time和CsI2017不被加入。所有固定参数、数组来源和方法边界见RESULTS.json。\n", encoding="utf-8")
    (output/"README.md").write_text(
        "# dim-6截断能标：独立保存核benchmark\n\n"
        "[逐路线结果与完整允许集](RESULTS.json) · [限值表](CUTOFF_LIMITS.csv) · [统计合同](STATISTICS_CONTRACT.md) · "
        "[采用来源](SOURCE_MANIFEST.json) · [代码与重跑](../../../examples/cutoff_scales/README.md)\n\n"
        "24条路线包括2条Ar轴矢量零响应；90/95%结果分别保存。SCANNED是本地保存核推断，"
        "未宣称正式Package本轮可读取或完整22算符已完成。完整scan数组保存在scans/，FINAL_CHECKS.json由后续独立验收写入。\n", encoding="utf-8")
    print("WROTE", output, "routes", len(results), "seconds", round(record["wall_seconds"], 2), flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grid-size", type=int, default=2049)
    args = parser.parse_args()
    run(args.output, args.grid_size)
