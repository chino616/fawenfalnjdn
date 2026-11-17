"""Read-only preflight for the independent cutoff-scale statistics Part.

This inventories adopted mainline artifacts. It does not fit coefficients,
compile kernels, change dataset permissions, or reproduce paper limits.
Only a new directory under outputs/cutoff_scales may receive the audit.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS

GROUND_BASIS = ((6, 1, "u"), (6, 1, "d"), (6, 2, "u"), (6, 2, "d"))
SOLAR = "outputs/external/solar_rho_snudd/20261112_fig4_run2"
REFERENCE = "outputs/paper2601_chi2_corrected_20261111"
KERNELS = {
    "CsI2021_9PE": f"{REFERENCE}/CsI2021_kernel.npz",
    "Ar2020_average": f"{REFERENCE}/Ar2020_kernel.npz",
    "CONUS_plus": "outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_operator_kernel_161_641.npz",
    **{name: f"{SOLAR}/kernels/{name}.npz" for name in ("PandaX_paired", "PandaX_US2", "XENONnT")},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def inspect_file(relative: str) -> dict:
    path = ROOT / relative
    try:
        data = path.read_bytes()
        return {"path": relative, "readable": True, "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest()}
    except OSError as exc:
        return {"path": relative, "readable": False, "error_type": type(exc).__name__,
                "error": str(exc), "dependent_capability": "unavailable through this path"}


def inspect_kernel(relative: str) -> dict:
    info = inspect_file(relative)
    if not info["readable"]:
        return info
    with np.load(ROOT / relative, allow_pickle=False) as archive:
        info["arrays"] = {key: {"shape": list(archive[key].shape), "dtype": str(archive[key].dtype)}
                          for key in archive.files}
        if "full_kernel" in archive:
            full = archive["full_kernel"]
            info["axis_order"] = ["target", "source", "nuclear_channel", "operator_i", "operator_j", "observed_bin"]
            if full.shape[3:5] != (4, 4):
                raise ValueError(f"unexpected adopted operator axes: {relative}")
            info["basis_keys"] = [list(key) for key in GROUND_BASIS]
            info["max_abs_diagonal_by_operator"] = [float(np.max(abs(full[:, :, :, i, i, :]))) for i in range(4)]
            info["max_abs_row_by_operator"] = [float(np.max(abs(full[:, :, :, i, :, :]))) for i in range(4)]
            info["units"] = "operator bilinear counts kernel; coefficients supplied in GeV^(4-d); reconstructed output events/bin"
        for key in ("metadata", "record_json"):
            if key not in archive:
                continue
            record = json.loads(str(archive[key]))
            record = record.get("record", record)
            info["record_selection"] = {k: record[k] for k in (
                "basis_keys", "axes", "sin2thetaW", "numerics", "representation", "state_treatment") if k in record}
        if "energy" in archive:
            energy = archive["energy"]
            info["energy_MeV"] = {"size": energy.size, "min": float(energy.min()), "max": float(energy.max()),
                                  "representative": energy[[0, len(energy)//2, -1]].tolist()}
        if "values" in archive:
            values = archive["values"]
            info["values_range"] = [float(values.min()), float(values.max())]
            info["units"] = "energy-resolved rate-polynomial kernel; reconstruct and integrate with energy_weights to obtain events"
    return info


def nuclear_inventory() -> dict:
    relative = "data/responses/responses_all.json"
    obj = read_json(relative)
    nuclei = obj["nuclei"]
    selected = ("Cs133", "I127", "Ar40", "Ge70", "Ge72", "Ge73", "Ge74", "Ge76",
                "Xe128", "Xe129", "Xe130", "Xe131", "Xe132", "Xe134", "Xe136")
    rows = {}
    for key in selected:
        if key not in nuclei:
            rows[key] = {"status": "MISSING"}
            continue
        item = nuclei[key]
        channels = {}
        for channel, coefficients in item.get("responses", {}).items():
            arr = np.asarray(coefficients, dtype=float)
            channels[channel] = {"shape": list(arr.shape), "first_coefficients": arr.ravel()[:3].tolist()}
        rows[key] = {"basic": item.get("basic", {}), "exp_factor": item.get("exp_factor", -2), "channels": channels}
    return {**inspect_file(relative), "reader": "cevns_pyeft/nuclear/response.py::ResponseDB",
            "metadata": obj.get("meta", {}), "selected_isotopes": rows,
            "adopted_source": "existing project numerical resource and existing reader convention",
            "external_author_release_and_conversion_equivalence": "UNRESOLVED; not required anew for local reuse; required for author-equivalence claims"}


def capabilities(kernel_info: dict) -> list[dict]:
    groups = ("CONUS_plus", "CsI2021_9PE", "Ar2020_average", "CsI2021_9PE+Ar2020_average",
              "PandaX_paired", "PandaX_US2", "XENONnT", "Solar_three_singlebins",
              "CsI2017_25PE", "CsI2021_time_99bin")
    rows = []
    for group in groups:
        for spec in LI2026_OPERATOR_SPECS:
            if group == "CsI2017_25PE":
                status = "BLOCKED_NATIVE_INPUT_AND_NO_ADOPTED_PARAMETER_KERNEL"
            elif group == "CsI2021_time_99bin":
                status = "BLOCKED_NATIVE_STATISTICS_CONTRACT"
            elif group.startswith(("PandaX", "XENON", "Solar")):
                status = ("READY_FOR_NEW_SCAN" if spec.key in GROUND_BASIS[:2]
                          else "MISSING_GENERAL_OPERATOR_FORWARD")
            elif spec.key in GROUND_BASIS:
                index = GROUND_BASIS.index(spec.key)
                zero = (group in kernel_info and kernel_info[group].get("max_abs_row_by_operator", [1]*4)[index] == 0.)
                status = "NO_RESPONSE_IN_ADOPTED_KERNEL" if zero else "READY_FOR_NEW_SCAN"
            else:
                status = "MISSING_GENERAL_OPERATOR_FORWARD"
            if spec.lnv_diagonal_must_vanish:
                flavor = "UNRESOLVED_LNV_TRANSITION_CONVENTION"
            else:
                flavor = "ee; additional flavors require separately named scans"
            rows.append({"analysis_group": group, "operator": spec.name, "dimension": spec.dimension,
                         "lepton_number": spec.lepton_number, "coefficient_unit": f"GeV^{spec.unit_power_GeV}",
                         "status": status, "flavor_contract": flavor, "computed_limit": "NOT_COMPUTED"})
    return rows


def inspect(output: Path) -> None:
    output = output.resolve()
    if not output.is_relative_to((ROOT / "outputs/cutoff_scales").resolve()) or output == (ROOT / "outputs/cutoff_scales").resolve():
        raise ValueError("choose a new run directory under this mainline's outputs/cutoff_scales/")
    if output.exists():
        raise FileExistsError("preflight output is create-only; choose a new run name")
    relative_sources = [
        "docs/experiments/MAINLINE_STATUS_20261114.md",
        "docs/experiments/MAINLINE_STATUS_20261114.evidence.json",
        "docs/references/General_CEvNS/2601.19883v2.pdf",
        f"{REFERENCE}/SUMMARY.json", f"{REFERENCE}/CsI2021_kernel_record.json", f"{REFERENCE}/Ar2020_kernel_record.json",
        f"{REFERENCE}/paper_reference/PROVENANCE.json", f"{REFERENCE}/paper_reference/fig3_plotted_limits.csv",
        f"{REFERENCE}/vector_scale_limits.csv",
        "outputs/one_d_benchmark_20261113_run1/RESULTS.json", "outputs/one_d_benchmark_20261113_run1/SOURCE_MANIFEST.json",
        "outputs/two_d_benchmark_20261113_run1/RESULTS.json", "outputs/two_d_benchmark_20261113_run1/SOURCE_MANIFEST.json",
        "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json",
        "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json",
        f"{SOLAR}/NSI_RESULTS.json", f"{SOLAR}/propagation_source/source.npz", f"{SOLAR}/propagation_source/manifest.json",
        "cevns_pyeft/theory/li2026/operators.py", "cevns_pyeft/theory/li2026/lec.py",
        "cevns_pyeft/theory/li2026/left_to_ci.py", "cevns_pyeft/theory/li2026/responses.py",
        "cevns_pyeft/statistics/profiling.py", "cevns_pyeft/statistics/parameters.py",
        "cevns_pyeft/kernels/compiler.py", "cevns_pyeft/kernels/solar_nsi.py",
        "extensions/solar_rho_snudd/scan.py", "examples/one_d_benchmark/prediction_routes.py",
        "examples/paper2601_chi2/extract_paper_reference.py",
    ]
    sources = [inspect_file(relative) for relative in relative_sources]
    kernels = {name: inspect_kernel(relative) for name, relative in KERNELS.items()}
    native = [inspect_file(f"data/experiments/{family}/{dataset}/{name}")
              for family, dataset in (("COHERENT_CsI", "CsI2021"), ("COHERENT_CsI", "CsI2017"), ("COHERENT_Ar", "Ar2020"))
              for name in ("experiment.input.yaml", "experiment.resources.npz")]
    summary = read_json(f"{REFERENCE}/SUMMARY.json")
    ground_statistics = {name: {k: row.get(k) for k in ("observed", "sigma", "background", "sigma_alpha", "sigma_beta", "signal", "chi2")}
                         for name, row in summary["SM"].items()}
    solar_statistics = read_json("data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json")
    source_path = ROOT / SOLAR / "propagation_source/source.npz"
    with np.load(source_path, allow_pickle=False) as archive:
        c, s, cosine = [float(archive[key]) for key in ("c13_squared", "s13_squared", "cos2theta12")]
        probability_bounds = [s*s+.5*c*c*(1-abs(cosine)), s*s+.5*c*c*(1+abs(cosine))]
        propagation_arrays = {key: {"shape": list(archive[key].shape), "dtype": str(archive[key].dtype)} for key in archive.files}
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "cevns_pyeft").rglob("*.py"))}
    protected.update({item["path"]: item["sha256"] for item in sources if item["readable"]})
    protected.update({item["path"]: item["sha256"] for item in kernels.values() if item["readable"]})
    rows = capabilities(kernels)
    audit = {"schema": "cutoff_scales_preflight/1", "date": "2026-11-14", "timezone": "Asia/Shanghai",
             "stage": "DESIGN_AND_SOURCE_PREFLIGHT_ONLY", "claim": "No cutoff fits or new physics predictions in this audit",
             "mainline_root": str(ROOT), "sources": sources, "kernels": kernels, "native_input_readability": native,
             "ground_statistics": {"source": f"{REFERENCE}/SUMMARY.json::SM", "unit": "events/bin; saved conversion already applied", "datasets": ground_statistics},
             "solar_statistics": solar_statistics, "solar_method": "continuous_acceptance + SNuDD v3.4.1 + XENON flat_sensitivity",
             "solar_propagation": {"arrays": propagation_arrays, "Pee_bounds_in_current_ee_model": probability_bounds},
             "operator_specs": [asdict(spec) for spec in LI2026_OPERATOR_SPECS], "mainline_LECs": asdict(DEFAULT_LECS),
             "nuclear_response": nuclear_inventory(), "capability_counts": {status: sum(row["status"] == status for row in rows) for status in sorted({row["status"] for row in rows})},
             "protected_baseline": protected, "baseline_scope": "all runtime Python plus explicitly adopted inputs/results; not a whole-repository Git audit",
             "limitations": ["Readable local arrays do not certify external authorship or author-equivalent likelihoods.",
                             "A present theory operator does not provide an integrated detector kernel.",
                             "LNV diagonal restriction is the current API contract, not a newly established universal physics theorem.",
                             "No native package permission or scientific Gate changes are made."]}
    output.mkdir(parents=True)
    (output / "SOURCE_AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    with (output / "CAPABILITIES.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "README.md").write_text(
        "# 截断能标独立 Part：方案阶段输入回读\n\n"
        "状态：DESIGN_AND_SOURCE_PREFLIGHT_ONLY。只检查主线已有输入、核、算符与统计身份，没有计算新限值。\n\n"
        "[源码与重跑命令](../../../examples/cutoff_scales/README.md) · "
        "[完整方案](../../../examples/cutoff_scales/PLAN_20261114.md) · "
        "[实际数组、单位、哈希与可读性](SOURCE_AUDIT.json) · [逐算符/实验能力矩阵](CAPABILITIES.csv)\n\n"
        "SOURCE_AUDIT.json 保存采用来源、实际核轴/尺寸/代表值、统计数组、当前 LEC、太阳版本、核响应系数和受保护基线。"
        "CAPABILITIES.csv 的 READY_FOR_NEW_SCAN 表示可进入后续验证计算，不表示已经产生有限限值；"
        "computed_limit 全部为 NOT_COMPUTED。Ar 轴矢量零响应与缺少核/缺少统计合同分别记录。\n\n"
        "实际新增/修改、导航同步和检查记录由本任务的 FILE_LIFECYCLE.json 与 FINAL_CHECKS.json 另行补充；"
        "二者只用于方案交付，不是物理数值验收。\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "stage": audit["stage"], "operator_count": len(LI2026_OPERATOR_SPECS),
                      "capability_rows": len(rows), "counts": audit["capability_counts"],
                      "unreadable_native_files": sum(not x["readable"] for x in native)}, ensure_ascii=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    inspect(parser.parse_args().output)
