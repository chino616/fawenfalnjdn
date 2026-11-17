"""Render the source-cited CONUS+ v3 review documents from explicit records and tables."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

from report_markdown import prepare_markdown, file_link, document_links


RUN = Path(__file__).resolve().parent
ROOT = next(parent for parent in RUN.parents if (parent / "cevns_pyeft/experiments/model_bindings.json").is_file())
DOC = ROOT / "docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1"
DATA = ROOT / "data/experiments/CONUS_Plus/conusplus_kkl_run1"
OBS = DATA / "statistics/conusplus_2501_17843v3_fig1_digitized.csv"
VERSION = "v3_20261106_provenance"
DETAIL = DOC / "experiment.physics.md"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def table(headers, values):
    def cell(value):
        return str(value).replace("|", "&#124;").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in values)
    return "\n".join(lines) + "\n\n"


def compact(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def source_records(seed):
    sources = copy.deepcopy(seed["old_source_register"]["sources"])
    local_names = {
        "S0002": RUN / "sources/user_reference_CONUS.pdf",
        "S0003": RUN / "sources/1101.2663v3.pdf",
        "S0004": RUN / "sources/kopeikin_2012_publisher.html",
        "S0005": RUN / "sources/nist_ge_isotopic_masses.html",
        "S0006": RUN / "sources/nist_codata2022_allascii.txt",
        "S0009": RUN / "sources/neon_2023_publisher.html",
        "S0011": OBS,
    }
    for source in sources:
        path = local_names.get(source["source_id"], ROOT / source["uri_or_path"])
        if digest(path) != source["sha256"]:
            raise ValueError("Material differs from its verified v2 source " + source["source_id"])
        source["uri_or_path"] = relative(path)
        source["sha256"] = digest(path)
        source.setdefault("bibtex", "")
        if source["source_id"] == "S0009":
            source["locator"] = "Fig. 23 caption, U235/Pu239/U238/Pu241 order"
        if source["source_id"] == "S0010":
            source["locator"] = "arXiv:2501.05206v3, PDF p. 6, reactor flux paragraph"
        if source["source_id"] == "S0011":
            source["reference_number"] = 11
            source["citation"] = "CEvNS-pyEFT project, CONUS+ Fig. 1 vector-digitized data and provenance, release 2026-11-06, derived numerical asset from Ref. [1]."
            source["bibtex"] = "@misc{CONUSFig1Digitized, author={{CEvNS-pyEFT project}}, title={CONUS+ Fig. 1 Vector-Digitized Data and Provenance}, year={2026}, note={Derived from arXiv:2501.17843v3, PDF p.10, Fig.1; release 2026-11-06}}"

    additions = [
        ("S0012", 12, "Project implementation identities", RUN / "sources/project_implementation_manifest.json",
         "CEvNS-pyEFT project, Model bindings, package statistics dispatch and nuclear response reader, local software snapshot, 2026-11-06.",
         "model_bindings.json model keys, package_profiles.py::definition_from_generic/evaluate_statistics, profiling.py::profile_gaussian_one_pull", None, None, "local_code_identity_checked"),
        ("S0013", 13, "BIPM SI Brochure", RUN / "sources/bipm_si_brochure_9_v4_01.pdf",
         "Bureau international des poids et mesures, The International System of Units (SI), 9th ed. (2019), version 4.01 (June 2026), DOI 10.59161/AUEZ1291.",
         "Chapter 4, Table 8, day row, PDF p. 142 / printed p. 140. SI prefixes in Chapter 3.",
         "https://www.bipm.org/documents/20126/41483022/SI-Brochure-9.pdf", "10.59161/AUEZ1291", "primary_numeric_definition_checked"),
        ("S0014", 14, "User configuration decisions", DATA / "input_choices.json",
         "User and CEvNS-pyEFT project, CONUS+ configuration decisions recorded in the onboarding conversation, 2026-11-06, local project record.",
         "user_decisions entries D_V2_001, D_V2_002, D_V2_003 and D_V3_001", None, None, "user_decision_transcription"),
        ("S0015", 15, "Numerical input generation", DATA / "build_inputs.py",
         "CEvNS-pyEFT project, CONUS+ source and natural-Ge input generation, build_inputs.py, version v3_20261106_provenance (2026), local reproducible calculation.",
         "build, verify_transcription and plot_flux functions", None, None, "local_algorithm_and_rebuild_checked"),
        ("S0016", 16, "User Flux reference figure", RUN / "sources/user_flux_reference_slide.png",
         "User-provided Flux reference figure identifying Kopeikin (2012) and Mueller et al. (2011), received 2026-11-06, unpublished reference image.",
         "Two bibliography bullets and the low/high-energy split", None, None, "bibliographic_identification_only"),
    ]
    for sid, number, title, path, citation, locator, url, doi, verification in additions:
        sources.append({"source_id": sid, "reference_number": number, "title": title,
                        "uri_or_path": relative(path), "sha256": digest(path), "citation": citation,
                        "locator": locator, "url": url, "doi": doi, "verification": verification,
                        "accessed": "2026-11-06", "bibtex": ""})
    return sources


def prepare_records(seed, sources):
    contract = copy.deepcopy(seed["old_physics_contract"])
    claims = copy.deepcopy(seed["old_evidence_ledger"]["claims"])
    config = read_json(DATA / "input_choices.json")
    checks = read_json(DATA / "numerical_checks.json")
    source_map = {source["source_id"]: source for source in sources}
    field_map = {key: field for section in contract["sections"].values() for key, field in section["fields"].items()}
    claim_map = {claim["field"]: claim for claim in claims}

    def update(key, **values):
        claim_map[key].update(values)
        for item in ("value", "unit"):
            if item in values:
                field_map[key][item] = values[item]
        if "status" in values:
            field_map[key]["provenance_status"] = values["status"]

    def add(section, key, value, unit, sid, locator, status="SOURCE_EXTRACTED"):
        cid = f"C{len(claims) + 1:04d}"
        claim = {"claim_id": cid, "field": key, "value": value, "unit": unit,
                 "status": status, "source_id": sid, "locator": locator, "notes": "", "decision_refs": []}
        claims.append(claim)
        claim_map[key] = claim
        field_map[key] = {"value": value, "unit": unit, "evidence_claims": [cid],
                          "provenance_status": status, "decision_status": "DRAFT", "blocking_scope": []}
        contract["sections"][section]["fields"][key] = field_map[key]
        contract["sections"][section]["evidence_refs"].append(cid)

    update("document.version", value=VERSION, source_id="S0014", status="PROJECT_DERIVED", locator="Current rewrite and main-project integration request")
    update("experiment_slug", source_id="S0014", locator="Project namespace chosen for the requested main-project CONUS+ integration")
    update("requested_claim", value="保留天然锗五同位素，采用 Nuclear Response 和参考 PDF Flux，对照 2501.17843v3 的式 (33)、式 (34) 与表 II", source_id="S0014", locator="D_V2_001/D_V2_002 与 D_V3_001")
    update("source.endpoint_mode", value="加入 (0,0)，在零点与首个原节点之间线性插值", source_id="S0014", locator="D_V2_003")
    update("source.flavor", value="electron antineutrino", locator="Ref. [1], PDF p. 8, reactor-source paragraph")
    update("source.low_nodes", unit="(MeV,1)")
    update("source.flux_table", value=relative(DATA / "reactor_flux_default.csv"), source_id="S0015", locator="build, flux_bytes and piecewise normalization")
    update("source.formula_vs_grid", value="分段公式和原始节点定义谱形，CSV 按 0.001 MeV 间隔采样", source_id="S0015", locator="build，分段处方与 CSV 采样")
    update("source.match_factor", source_id="S0015", locator="build, high(2)/low_shape[-1]")
    update("source.normalization_integral", source_id="S0015", locator="build, low_default + high256")
    update("target.number_fractions", status="SOURCE_EXTRACTED", locator="Ref. [1], PDF p. 9, natural-Ge paragraph. NIST Ge composition rows agree.")
    update("nuclear_structure_module", source_id="S0014", locator="D_V2_001 and D_V2_002")
    for key in ("interaction_module", "kinematics_module", "cross_section_module"):
        update(key, source_id="S0012", locator=f"model_bindings.json exact key {field_map[key]['value']}")
    update("statistics.model_id", source_id="S0012", locator="package_profiles.py::definition_from_generic/evaluate_statistics and profiling.py::profile_gaussian_one_pull")
    update("numerics.seconds_per_day", source_id="S0013", status="SOURCE_EXTRACTED", locator="Chapter 4, Table 8, day row. PDF p. 142 / printed p. 140")
    update("numerics.plan", value="按低能节点、2 MeV 拼接点和运动学边界分段积分，将 Gaussian 积入各观测箱，并在使用前核对收敛与窗口损失", source_id="S0001", locator="由式 (26)–(32)、源谱节点和观测箱边界推导的候选积分方案")
    update("fast.requested", source_id="S0014", locator="D_V3_001, current requested deliverable")
    update("statistics.inference", value="一维 1σ 对照采用 Δχ²=1，每次扫描一个 NSI，其余 NSI 固定零，并保留不连通区间。拟合前审阅本约定", status="PROJECT_DERIVED", locator="[1] 式 (34) 与表 II 的 1σ 标记，以及本版候选单参数比较约定")
    update("provenance.open_items", locator="Current P02 source gaps and implementation backlog")
    update("version.scope", source_id="S0014", value="v3 来源标注版与数据已整合至主项目，原始出处待补项和 Phase 0 准备事项随文档记录", locator="D_V3_001")
    update("interaction.sin2thetaW_reference", locator="Ref. [1], Sec. II.A, PDF p. 3, low-energy reference 0.23857(5)")
    update("benchmark.targets", locator="Ref. [1], Eq. (34), PDF p. 11, and Table II CONUS+ column, PDF p. 13")

    add("target_and_exposure", "target.atomic_mass_u", config["target_atomic_masses_u"], "u", "S0005", "Ge isotope rows, relative atomic mass column")
    for key, value, unit, locator in [
        ("constants.atomic_mass_kg", config["constants"]["atomic_mass_kg"], "kg", "atomic mass constant row"),
        ("constants.atomic_mass_energy_GeV", config["constants"]["atomic_mass_energy_GeV"], "GeV", "atomic mass constant energy equivalent in MeV, divided by 1000"),
        ("constants.electron_mass_energy_GeV", config["constants"]["electron_mass_energy_GeV"], "GeV", "electron mass energy equivalent in MeV, divided by 1000"),
        ("constants.avogadro_per_mol", config["constants"]["avogadro_per_mol"], "mol^-1", "Avogadro constant row, exact"),
    ]:
        add("target_and_exposure", key, value, unit, "S0006", locator)
    add("target_and_exposure", "constants.atomic_mass_energy_MeV", 931.49410372, "MeV", "S0006", "atomic mass constant energy equivalent in MeV row")
    add("target_and_exposure", "constants.electron_mass_energy_MeV", 0.51099895069, "MeV", "S0006", "electron mass energy equivalent in MeV row")
    update("constants.atomic_mass_energy_GeV", status="PROJECT_DERIVED")
    update("constants.electron_mass_energy_GeV", status="PROJECT_DERIVED")
    add("source", "source.kkl_comparison_fractions", {row["isotope"]: float(row["kkl_comparison_fraction"]) for row in rows("fission_fractions.csv")}, "1", "S0010", "PDF p. 6, reactor-flux paragraph, U235/U238/Pu239/Pu241 order")
    add("source", "source.grid_step", config["flux_grid_step_MeV"], "MeV", "S0015", "build, linspace(0,10,10001)", "PROJECT_DERIVED")
    add("source", "source.low_endpoint_node", [0, 0], "(MeV,1)", "S0014", "D_V2_003, energy in MeV and relative shape", "USER_CONFIRMED")
    add("source", "source.initial_density", [[1, 0, 0], [0, 0, 0], [0, 0, 0]], "1", "S0001", "Project representation of the electron-antineutrino state as |e><e| in the ordered (e,mu,tau) active-flavor basis", "PROJECT_DERIVED")
    add("detector_response", "detector.fwhm_reference", 48, "eVee", "S0001", "PDF p. 9, paragraph following Eq. (30)")
    add("source", "source.reference_identification", ["Kopeikin 2012", "Mueller et al. 2011"], "1", "S0016", "User figure, bibliography bullets")

    dependencies = {
        "source.match_factor": ["source.mueller_coefficients", "source.fission_fractions", "source.low_nodes", "source.join_energy"],
        "source.normalization_integral": ["source.match_factor", "source.low_nodes", "source.low_endpoint_node", "source.energy_max", "source.mueller_coefficients", "source.fission_fractions"],
        "source.flux_table": ["source.total_flux", "source.normalization_integral", "source.match_factor", "source.low_nodes", "source.mueller_coefficients", "source.fission_fractions", "source.low_endpoint_node", "source.grid_step"],
        "target.atomic_mass_kg": ["target.atomic_mass_u", "constants.atomic_mass_kg"],
        "target.nuclei_per_kg": ["target.number_fractions", "target.atomic_mass_kg"],
        "target.nuclear_mass_GeV": ["target.atomic_mass_u", "constants.atomic_mass_energy_GeV", "constants.electron_mass_energy_GeV", "detector.Z"],
        "statistics.sigma_mean": ["statistics.error_minus", "statistics.error_plus"],
        "observable.edges_eVee": ["statistics.observed"],
        "statistics.inference": ["benchmark.targets"],
        "source.initial_density": ["source.flavor"],
        "constants.atomic_mass_energy_GeV": ["constants.atomic_mass_energy_MeV"],
        "constants.electron_mass_energy_GeV": ["constants.electron_mass_energy_MeV"],
        "numerics.plan": ["source.flux_table", "observable.edges_eVee", "target.nuclei_per_kg"],
    }
    primary_labels = {
        "S0001": "benchmark 原文相应位置已核", "S0002": "用户 PDF 转录已核，上游数字表待核",
        "S0003": "Mueller 原文 24 个系数已核", "S0005": "NIST 原始数值行已核",
        "S0006": "2022 CODATA 数值行已核", "S0007": "本地表与键已核，原始核计算出处待核",
        "S0010": "CONUS+ 原文运行配比已核", "S0011": "原图向量取点可重建，作者原始数表待取得",
        "S0012": "当前代码身份与引用位置已核", "S0013": "BIPM 单位定义已核",
        "S0014": "用户选择逐字记录", "S0015": "项目推导和生成方法可重建", "S0016": "截图书目对应已核",
    }
    for claim in claims:
        key = claim["field"]
        claim["input_claims"] = [claim_map[name]["claim_id"] for name in dependencies.get(key, [])]
        claim["upstream_source_ids"] = ["S0004"] if key == "source.low_nodes" else []
        claim["verification_scope"] = primary_labels.get(claim["source_id"], "来源及使用范围见 P00")
        if claim["status"] == "PROJECT_DERIVED" and claim["source_id"] != "S0011":
            claim["verification_scope"] = "项目推导或拟采用方案，输入核验范围沿依赖链查阅"
        claim["output_locations"] = [{"file": relative(DETAIL), "anchor": "source-" + key.replace(".", "-")}, {"file": relative(RUN / "P03_PHYSICS_CONTRACT.yaml"), "field": key}]
        claim["unresolved_upstream_source_ids"] = []
        if key == "source.low_nodes":
            claim["unresolved_upstream_source_ids"] = ["S0004"]
        if key in ("nuclear.response_resource", "nuclear.response_keys"):
            claim["unresolved_upstream_source_ids"] = ["S0007"]
    by_id = {claim["claim_id"]: claim for claim in claims}

    def unresolved(claim, trail=()):
        if claim["claim_id"] in trail:
            raise ValueError("Evidence dependency cycle")
        result = set(claim["unresolved_upstream_source_ids"])
        for cid in claim["input_claims"]:
            result.update(unresolved(by_id[cid], trail + (claim["claim_id"],)))
        return sorted(result)

    for claim in claims:
        claim["unresolved_upstream_source_ids"] = unresolved(claim)
        if claim["status"] == "PROJECT_DERIVED" and claim["input_claims"]:
            claim["derivation"] = {"method": claim["locator"], "input_claims": claim["input_claims"], "upstream_limits_propagated": True}
    for section in contract["sections"].values():
        section["decision_status"] = "DRAFT"
    contract["scientific_claim"] = "Natural-Ge Nuclear Response adaptation using the source-cited reference-PDF Flux, compared with arXiv:2501.17843v3 Eq. (33), Eq. (34) and Table II."
    metadata = contract["sections"]["validation_claim"]["fields"]["physics_report"]["value"]
    metadata["summary"] = "v3 主项目来源标注版，天然 Ge、Nuclear Response 和参考 PDF Flux。Kopeikin 原始数表与 Response 原始核计算出处待核。"
    return config, checks, claims, contract


def render_documents(sources, config, checks, claims, contract):
    source_map = {source["source_id"]: source for source in sources}
    claim_map = {claim["field"]: claim for claim in claims}
    by_id = {claim["claim_id"]: claim for claim in claims}
    files = {}
    emitted_parameter_anchors = set()

    def cite(sid, locator="", owner=DETAIL):
        source = source_map[sid]
        target = file_link(f'[{source["reference_number"]}]', DOC / "REFERENCES.md", owner)
        target = target[:-1] + f'#ref-{source["reference_number"]})'
        return target + (" " + locator if locator else "")

    def provenance(key):
        claim = claim_map[key]
        text = cite(claim["source_id"], claim["locator"])
        if claim["input_claims"]:
            text += "，输入 " + ", ".join(by_id[cid]["field"] for cid in claim["input_claims"])
        return text

    def parameter_table(keys):
        values = []
        for key in keys:
            claim = claim_map[key]
            anchor = f"`{key}`"
            if key not in emitted_parameter_anchors:
                anchor = f'<a id="source-{key.replace(".", "-")}"></a>' + anchor
                emitted_parameter_anchors.add(key)
            values.append((anchor, compact(claim["value"]), claim["unit"], provenance(key), claim["verification_scope"]))
        return table(["参数/精确字段", "采用值", "单位", "直接出处及定位/推导输入", "核验范围"], values)

    equation_notes = {
        "mueller_shape": ("S0003", "Mueller et al. (2011)，PDF p. 13，式 (12) 与表 VI。裂变权重来自用户笔记 PDF p. 5，式 (1.22)–(1.26)。", ["source.mueller_coefficients", "source.fission_fractions"]),
        "source_match": ("S0002", "用户笔记 PDF p. 5，式 (1.27)–(1.28)。零端点按用户决定 D_V2_003 加入。", ["source.match_factor", "source.low_nodes", "source.low_endpoint_node"]),
        "absolute_flux": ("S0002", "用户笔记 PDF pp. 4–5，式 (1.16)–(1.20)。总通量取 benchmark PDF p. 8，第 III 节。", ["source.total_flux", "source.normalization_integral"]),
        "natural_inventory": ("S0005", "NIST 原子质量与数丰度及 CODATA 质量常数，按数分数求每公斤核数。", ["target.number_fractions", "target.atomic_mass_u", "constants.atomic_mass_kg", "target.nuclei_per_kg"]),
        "lindhard": ("S0001", "benchmark PDF p. 9，式 (31)，含 11.5、3、0.15、0.7、0.6 系数与指数。", ["detector.Z", "detector.k"]),
        "gaussian": ("S0001", "benchmark PDF p. 9，式 (29)–(30)。全域归一化由 Gaussian 定义得到。", ["detector.sigma0", "detector.fano", "detector.pair_energy"]),
        "bin_probability": ("S0001", "由 benchmark 式 (26)、(29)、(32) 对观测箱积分得到。", ["observable.edges_eVee"]),
        "fold": ("S0001", "由 benchmark PDF pp. 8–9，式 (26)、(32) 改写为对核反冲能积分。每天秒数见 BIPM 表 8。", ["source.flux_table", "target.nuclei_per_kg", "target.exposure", "numerics.seconds_per_day"]),
        "chi2": ("S0001", "benchmark PDF pp. 9–10，式 (33)。", ["statistics.observed", "statistics.sigma_mean", "statistics.sigma_alpha"]),
        "profile": ("S0001", "对 benchmark 式 (33) 的共同归一化参数求导并令导数为零得到。", ["statistics.observed", "statistics.sigma_mean", "statistics.sigma_alpha"]),
    }
    formula_index = []
    equation_number = 0

    def equations(section_name):
        nonlocal equation_number
        body = ""
        for equation in contract["sections"][section_name]["fields"].get("paper_equations", {}).get("value", []):
            equation_number += 1
            sid, explanation, inputs = equation_notes[equation["id"]]
            anchor = "formula-" + equation["id"].replace("_", "-")
            body += f'<a id="{anchor}"></a>\n\n**{equation["title"].split(" [")[0]}**\n\n'
            body += "依据与处理过程见 " + cite(sid) + "。" + explanation + "\n\n"
            body += "$$\n" + equation["latex"] + f" \\tag{{{equation_number}}}\n$$\n\n"
            symbol_rows = []
            for symbol in equation["symbols"]:
                key = symbol["parameter_ref"]
                source_text = provenance(key) if key else f"本式定义的变量或中间量，依据见本式说明"
                symbol_rows.append(("$" + symbol["symbol"] + "$", symbol["definition"], symbol["unit"], f"`{key}`" if key else "本式变量/推导量", source_text))
            body += table(["符号", "定义", "单位", "精确参数位置", "依据与来源定位"], symbol_rows)
            formula_index.append({"id": equation["id"], "output_anchor": anchor, "source_ids": [sid],
                                  "input_claims": [claim_map[key]["claim_id"] for key in inputs], "number": equation_number})
        return body

    detail = "# CONUS+ onboarding v3（2026-11-06，来源标注与下一步准备版）\n\n"
    detail += "本数据集为 `CONUS_Plus/conusplus_kkl_run1`。采用天然锗五同位素、Nuclear Response、参考 PDF 的 Flux 和非负零端点。当前处于资料与方案审阅阶段，整体为 PARTIAL。\n\n"
    detail += "## 1. 实验范围与本次补充\n\n"
    detail += "本次已把具体出处写到参数、公式和数值表旁。高能系数核到 Mueller 原文，低能点核到用户 PDF，观测点核到指定 benchmark 图 1。用户提供的 Flux 截图对应 Kopeikin 与 Mueller 两篇文献。" + cite("S0016") + "\n\n"
    detail += "待补的原始来源有两项，Kopeikin 32 点对应的原文表/图，以及本地 Ge Response 表的原始核计算数据和生成链。已经向用户询问这些材料的名称、链接或脚本。计算准备中的接口核验列在第 10 节。\n\n"
    detail += parameter_table(["requested_claim", "target.number_fractions", "nuclear_structure_module", "source.endpoint_mode", "version.scope"])
    detail += "## 2. Source\n\n"
    detail += "入射为电子反中微子，低于 2 MeV 使用参考 PDF 的低能谱表，高于或等于 2 MeV 使用 Mueller 系数。高能谱具体采用 Mueller 四核素表。" + cite("S0001", "PDF pp. 8–9，第 III 节") + " " + cite("S0003", "式 (12)，表 VI") + "\n\n"
    detail += parameter_table(["source.flavor", "source.initial_density", "source.total_flux", "source.energy_max", "source.join_energy", "source.fission_fractions", "source.kkl_comparison_fractions", "source.match_factor", "source.normalization_integral", "source.low_endpoint_node", "source.grid_step"])
    detail += "### 高能谱的全部系数\n\n"
    detail += "各行依次为 a0 至 a5，指数中的能量按 E/MeV 取数值。原始每 MeV 每裂变谱在本处先作为相对形状，再按探测器处总通量归一化。" + cite("S0003", "PDF p. 13，表 VI") + "\n\n"
    detail += table(["核素", "a0", "a1", "a2", "a3", "a4", "a5", "直接出处"], [(row["isotope"], *(row[f"a{i}"] for i in range(6)), cite("S0003", "表 VI，PDF p. 13")) for row in rows("mueller_coefficients.csv")])
    detail += "### 低能谱的全部节点\n\n"
    detail += "以下 32 个点直接转录自用户 PDF 表 2，PDF 第 6 页、印刷第 5 页。原表将其归于 Kopeikin。原始论文中对应的数值表或图仍待定位，当前按相对形状使用。" + cite("S0002") + " " + cite("S0004") + "\n\n"
    detail += table(["节点行", "能量 / MeV", "相对谱值", "直接出处", "核验范围"], [(index, row["energy_MeV"], row["relative_shape"], cite("S0002", "表 2，PDF p. 6"), "转录已核，上游原表待核") for index, row in enumerate(rows("kopeikin_low_energy_transcribed.csv"), 1)])
    detail += equations("source")
    detail += "参考 PDF 配比为 U235/U238/Pu239/Pu241 = 0.56/0.07/0.31/0.06。NEON 图 23 图注可交叉核对该模型配比。CONUS+ 运行期配比为 0.53/0.08/0.32/0.07。两组值均保存在数据表中。" + cite("S0002", "式 (1.22)–(1.25)") + " " + cite("S0009", "图 23 图注") + " " + cite("S0010", "PDF p. 6") + "\n\n"
    detail += "Mueller 原文的参考谱主要覆盖 2–8 MeV。本版按参考 PDF 将多项式延用到 10 MeV，并记录尾部扩展。全谱归一化包含低能段，因此低能原始来源的缺口也影响全谱绝对通量的溯源范围。" + cite("S0003") + " " + cite("S0002", "式 (1.18)、(1.28)") + "\n\n"
    detail += f'由原先线性外推算得零能量处相对谱为 {checks["literal_reference_relative_shape_at_zero"]:.4f}，零点位于 {checks["literal_reference_negative_below_MeV"]:.9f} MeV。加入零节点后的归一积分为 {checks["normalization_default_MeV"]:.12f} MeV，对照外推为 {checks["normalization_literal_reference_MeV"]:.12f} MeV，相对变化 {checks["relative_normalization_change_percent"]:.6f}%。这些值来自同一输入重建。' + cite("S0015", "build") + "\n\n"
    detail += "## 3. Target 与物理常数\n\n"
    detail += parameter_table(["target.detector_mass", "target.exposure", "target.atomic_mass_u", "constants.atomic_mass_kg", "constants.atomic_mass_energy_MeV", "constants.atomic_mass_energy_GeV", "constants.electron_mass_energy_MeV", "constants.electron_mass_energy_GeV", "constants.avogadro_per_mol"])
    detail += equations("target_and_exposure")
    detail += table(["核素", "数分数", "原子质量 / u", "每公斤核数", "近似核质量 / GeV", "直接依据"], [(row["isotope"], row["number_fraction"], row["atomic_mass_u"], row["nuclei_per_kg"], row["nuclear_mass_GeV_approx"], cite("S0005", "Ge 对应行") + " + " + cite("S0006", "质量常数") + "，按本节公式推导") for row in rows("natural_ge_inventory.csv")])
    detail += "每公斤核数使用中性原子质量。运动学核质量采用原子质量能量减去 Z 个电子静质量的近似，电子结合能修正作为明确的近似项记录。" + cite("S0015", "build 中 nuclear_mass 与 nuclei_kg") + "\n\n"
    detail += "## 4. 本实验选择的共享模块\n\n"
    detail += parameter_table(["interaction_module", "nuclear_structure_module", "nuclear.response_resource", "nuclear.response_keys", "kinematics_module", "cross_section_module", "interaction.fermi_GeV_minus2", "interaction.sin2thetaW_reference"])
    detail += "Ge70、Ge72、Ge73、Ge74、Ge76 的本地 Response 键均可读取。数值来源目前定位到 responses_all.json 的相应 nuclei 条目，原始核计算出处保留待核状态。共享理论选择参考 Li 等人的框架，数值表的原始来源单独记录。" + cite("S0007") + " " + cite("S0008") + "\n\n"
    detail += "## 5. Detector\n\n"
    detail += parameter_table(["detector.Z", "detector.k", "detector.fwhm_reference", "detector.sigma0", "detector.fano", "detector.pair_energy", "detector.threshold", "detector.efficiency", "numerics.minimum_true_ionization"])
    detail += equations("detector_response")
    detail += "处理顺序为真实核反冲、Lindhard 电离能、Gaussian 重建能、观测能分箱。Lindhard 中反冲能取 keV，分辨率中电离能取 eVee。采用 benchmark 阈值以上约 100% 的效率近似，Gaussian 窗口外尾部计作接受损失。" + cite("S0001", "PDF pp. 8–10，式 (26)、(29)–(32)") + "\n\n"
    detail += "## 6. Observable 与逐箱观测数据\n\n"
    detail += parameter_table(["observable.processing", "observable.native_unit", "observable.edges_eVee"])
    detail += "数据由指定 PDF 第 10 页图 1 的黑点和误差棒向量提取。表内能量为 eVee，观测和误差单位均为 counts kg^-1 (10 eVee)^-1。下表保留负中心值。mean 列为上下误差算术平均，当前作为候选统计约定记录。" + cite("S0001", "图 1") + " " + cite("S0011", "CSV、provenance JSON 与 overlay") + "\n\n"
    detail += table(["箱", "中心 / eVee", "excess", "下误差", "上误差", "候选 mean", "数据出处"], [(row["bin_index"], row["energy_center_eVee"], row["excess"], row["error_minus"], row["error_plus"], row["sigma_mean_derived"], cite("S0011", "第 " + row["bin_index"] + " 行，源图 [1] 图 1")) for row in rows("statistics/conusplus_2501_17843v3_fig1_digitized.csv")])
    detail += "## 7. Prediction folding\n\n"
    detail += parameter_table(["numerics.seconds_per_day", "numerics.plan"])
    detail += equations("slow_counts")
    detail += "按核素分别积分后按每公斤核数相加，曝光和秒/天换算各施加一次。反冲积分取 keVnr，源能积分取 MeV，所需截面输出为 cm²/keVnr。预测向图轴单位的转换、反中微子接口及积分收敛列入下一步实现审阅。" + cite("S0001", "式 (26)、(32)") + " " + cite("S0013", "表 8") + "\n\n"
    detail += "## 8. Statistics 与 Benchmark\n\n"
    detail += parameter_table(["statistics.model_id", "statistics.sigma_alpha", "statistics.inference"])
    detail += equations("statistics")
    detail += "累计归一化宽度取 0.169。误差列直接保留图形提取的上下端点，拟合前需要确认候选对称化约定。该项具体问题已经列入 P02。" + cite("S0001", "PDF p. 10，式 (33) 后的段落") + " " + cite("S0011") + "\n\n"
    targets = claim_map["benchmark.targets"]["value"]
    detail += "弱混合角文献目标为 0.247 ± 0.052，来源为式 (34)。向量 NSI 的 1σ 比较目标取表 II 的 CONUS+ 列。" + cite("S0001", "PDF pp. 11、13") + "\n\n"
    detail += table(["参数", "文献区间", "出处"], [(key, compact(value), cite("S0001", "表 II，PDF p. 13，CONUS+ 列")) for key, value in targets.items() if key != "weak_angle"])
    detail += "## 9. 数值资源与逐字段来源索引\n\n"
    detail += "各物理输入的文件、列、行范围、单位和处理链集中在配套来源映射中。" + file_link("来源映射", DATA / "PROVENANCE_MAP.json", DETAIL) + "\n\n"
    detail += table(["字段", "证据性质", "具体出处/推导链", "核验范围"], [(f'<a id="source-{claim["field"].replace(".", "-")}-index"></a>`{claim["field"]}`', claim["status"], provenance(claim["field"]), claim["verification_scope"]) for claim in claims])
    detail += "## 10. 来源缺口与下一步准备\n\n"
    detail += "现有数据已可重建 Flux 和天然锗库存。进入 Phase 0 时可以据本文件审阅路线、输入与实现范围。进入依赖这些输入的可信计算前，需要处理下列事项。\n\n"
    detail += gap_table()
    detail += "用户在补充交互中提供了 Flux 参考截图，已据此确认两篇文献的书目对应。32 点的原文数值定位和 Response 原始数据链继续保留待补。" + cite("S0016") + "\n\n"
    detail += "## 11. 标准参考文献\n\n"
    for source in sorted(sources, key=lambda item: item["reference_number"]):
        detail += f'[{source["reference_number"]}] {source["citation"]} ' + cite(source["source_id"], "来源记录及阅读入口") + "\n\n"

    # Every field receives exactly one stable evidence anchor in the detailed document.
    for claim in claims:
        anchor = f'<a id="source-{claim["field"].replace(".", "-")}"></a>'
        if anchor not in detail:
            detail = detail.replace(f'<a id="source-{claim["field"].replace(".", "-")}-index"></a>', anchor)
    files[DETAIL] = detail

    refs = "# CONUS+ onboarding v3 标准参考文献与核验范围\n\n## 文献与文件入口\n\n"
    for source in sorted(sources, key=lambda item: item["reference_number"]):
        number = source["reference_number"]
        refs += f'<a id="ref-{number}"></a>\n\n[{number}] {source["citation"]}\n\n'
        refs += source["locator"] + "。核验范围为 `" + source["verification"] + "`。\n\n"
        links = [file_link("本地原文或直接材料", ROOT / source["uri_or_path"], DOC / "REFERENCES.md")]
        if source.get("doi"):
            links.append("[DOI](https://doi.org/" + source["doi"] + ")")
        if source.get("url"):
            links.append("[官方入口](" + source["url"] + ")")
        refs += " · ".join(links) + "\n\n"
        refs += "SHA256 `" + source["sha256"] + "`。\n\n"
    refs += "## 来源与数据的对应\n\n具体数据定位和上游核验范围见详细版逐字段来源索引及 P01。低能表直接来自用户 PDF，截图支持书目对应。Response 的数值直接来自本地 JSON。\n\n"
    files[DOC / "REFERENCES.md"] = refs
    journal_entries = {
        "S0001": ("De Romeri, V. and Papoulias, D. K. and Sanchez Garcia, G.", "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering", "Physical Review D", "111", "075025", "2025", "2501.17843v3"),
        "S0003": ("Mueller, Th. A. and others", "Improved Predictions of Reactor Antineutrino Spectra", "Physical Review C", "83", "054615", "2011", "1101.2663v3"),
        "S0004": ("Kopeikin, V. I.", "Flux and Spectrum of Reactor Antineutrinos", "Physics of Atomic Nuclei", "75", "143--152", "2012", None),
        "S0009": ("Choi, J. J. and others", "Exploring coherent elastic neutrino-nucleus scattering using reactor electron antineutrinos in the NEON experiment", "European Physical Journal C", "83", "226", "2023", None),
        "S0010": ("Ackermann, N. and others", "Direct observation of coherent elastic antineutrino-nucleus scattering", "Nature", "643", "1229--1233", "2025", "2501.05206v3"),
    }
    bibtex = []
    for source in sources:
        entry = source.get("bibtex")
        if source["source_id"] in journal_entries:
            author, title, journal, volume, pages, year, arxiv = journal_entries[source["source_id"]]
            fields = {"author": author, "title": title, "journal": journal, "volume": volume, "pages": pages, "year": year, "doi": source["doi"]}
            if arxiv:
                fields.update(eprint=arxiv, archivePrefix="arXiv")
            entry = "@article{" + source["source_id"] + ",\n" + ",\n".join("  " + key + "={" + value + "}" for key, value in fields.items()) + "\n}"
        elif source["source_id"] == "S0008":
            entry = "@article{S0008, author={Li, Gang and Song, Chuan-Qiang and Tang, Feng-Jie and Yu, Jiang-Hao}, title={Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering}, year={2026}, eprint={2601.19883v2}, archivePrefix={arXiv}}"
        if not entry:
            entry = "@misc{" + source["source_id"] + ",\n  title={" + source["title"] + "},\n  year={2026},\n  note={" + source["citation"].replace("_", "\\_") + "}\n}"
        bibtex.append(entry)
    files[DOC / "REFERENCES.bib"] = "\n\n".join(bibtex) + "\n"

    summary = "# CONUS+ onboarding v3 精简版（2026-11-06）\n\n"
    summary += "主文件已整合本轮数据来源和引用，版本状态为 PARTIAL。采用天然 Ge 五同位素、Nuclear Response、参考 PDF 的 Flux 和用户选定的零端点。\n\n"
    summary += "## 已有资料\n\n"
    summary += "Mueller 24 系数已核原表，32 个低能点已核用户 PDF 表 2，天然锗质量/丰度和物理常数已核 NIST/CODATA，19 个观测点已核指定图 1。" + file_link("详细版参数与公式", DETAIL, DOC / "experiment.physics.summary.md") + "\n\n"
    summary += "## 当前缺口\n\n" + gap_table()
    summary += "## 下一步\n\n可据详细版进行 Phase 0 路线与输入审阅。数据的原始出处补充、Response 接口核验和拟合前误差约定分别列在 P02。" + file_link("待补事项", RUN / "P02_MISSING_AND_CONFLICTS.md", DOC / "experiment.physics.summary.md") + "\n\n"
    files[DOC / "experiment.physics.summary.md"] = summary

    user = "# CONUS+ onboarding 用户资料 v3（2026-11-06）\n\n## H0 身份与目标\n\n"
    user += "CONUS_Plus/conusplus_kkl_run1，目标为与 2501.17843v3 的 Eq. (33)、Eq. (34)、Table II 对照的天然锗 Response 适配资料准备。\n\n"
    user += "## H1 材料\n\n文献、用户 PDF、Flux 截图、原图数字化资料和本地 Response 的角色与核验范围分别登记在 P00。\n\n"
    user += "## H2 逐数据依据\n\n所有采用项的数值、单位、页/表/式定位和推导输入集中在主文件中。" + file_link("来源严格标注的详细版", DETAIL, DOC / "EXPERIMENT_USER_INPUT.md") + "\n\n"
    user += "## H3 已有选择\n\n"
    user += table(["决定", "用户原文"], [(item["decision_id"], item["verbatim"]) for item in config["user_decisions"]])
    user += "## 首次输出后的补充交互\n\n上一轮已说明 Kopeikin 原始数表与 Response 核计算出处缺口。本轮询问其原文、数据包或脚本，用户补充了 Flux 文献图，已确认 Kopeikin 2012 与 Mueller 2011 的书目对应。数字节点的原文定位及 Response 上游数据仍待补。\n\n"
    user += "## 待补与下一步\n\n" + gap_table()
    files[DOC / "EXPERIMENT_USER_INPUT.md"] = user

    provenance_map = resource_provenance(claim_map)
    files[DATA / "PROVENANCE_MAP.json"] = dump(provenance_map)
    files[RUN / "SOURCE_COVERAGE.json"] = dump({"version": VERSION, "adopted_fields": len(claims), "unmapped_fields": [],
        "scope": "Mechanical field-to-source/locator/output mapping and propagated limits. Original-source factual checks are recorded separately.",
        "fields": [{"field": claim["field"], "claim_id": claim["claim_id"], "source_id": claim["source_id"],
                    "locator": claim["locator"], "output_locations": claim["output_locations"],
                    "unresolved_upstream_source_ids": claim["unresolved_upstream_source_ids"]} for claim in claims], "formulas": formula_index})
    files[RUN / "P00_SOURCE_REGISTER.yaml"] = dump({"experiment_slug": "CONUS_Plus", "dataset_id": "conusplus_kkl_run1", "document_version": VERSION, "sources": sources})
    files[RUN / "P01_EVIDENCE_LEDGER.yaml"] = dump({"sources": [], "claims": claims})
    files[RUN / "P03_PHYSICS_CONTRACT.yaml"] = dump(contract)
    files[RUN / "P04_DECISION_LOG.yaml"] = dump({"document_version": VERSION, "decisions": config["user_decisions"], "supplementation": {"question": "32 个低能谱点和 Ge Response 的上游原始材料", "user_reply": "我发你图，你看一下是不是这两篇文献中的", "material_source_id": "S0016", "result": "Flux 书目对应已核，原始数字表和 Response 生成链待补"}, "overall_human_gate": "NOT_REVIEWED"})
    files[RUN / "P02_MISSING_AND_CONFLICTS.md"] = "# CONUS+ v3 待补数据、来源及实现事项\n\n## 当前缺口\n\n" + gap_table() + "## 本轮补充记录\n\n用户提供 Flux 文献截图，书目已与 benchmark 的 Kopeikin/Mueller 引用对应。原始数值定位继续待补，相关限制已传播到 Flux 派生量。\n\n## 下一步输入\n\n请补充 Kopeikin 原文中这 32 点的图/表位置或原始数据文件，以及 Ge Response 的原始核计算数据包/生成脚本。当前文档可供 Phase 0 路线审阅。\n"
    files[RUN / "P05_CONTRACT_STATUS.md"] = "# CONUS+ v3 状态与下一步\n\n逐字段来源映射已建立，整体为 PARTIAL。下一步为 Phase 0 路线、输入和实现范围审阅。原始来源缺口与待确认的统计约定见 P02。Human Gate 为 NOT_REVIEWED。\n"
    files[RUN / "benchmark/BENCHMARK_REGISTER.md"] = "# CONUS+ v3 Benchmark 登记\n\n目标为 arXiv:2501.17843v3 的 Eq. (33)、Eq. (34) 与 Table II，原文页码和数值列在详细版第 8 节。当前为参考目标与输入准备记录。对比需要记录 Nuclear Response、参考裂变配比和图形数字化带来的条件差别。\n\n" + file_link("主文件", DETAIL, RUN / "benchmark/BENCHMARK_REGISTER.md") + "\n"

    for directory in (DOC, DATA, RUN):
        title = "CONUS+ onboarding v3 主入口" if directory == DOC else ("CONUS+ v3 数据与来源" if directory == DATA else "CONUS+ v3 来源记录与生成")
        body = "# " + title + "（2026-11-06）\n\n当前版本为 `" + VERSION + "`，整体状态为 PARTIAL。\n\n## 阅读与使用\n\n"
        for label, target in [("详细主文件", DETAIL), ("精简版", DOC / "experiment.physics.summary.md"), ("标准参考文献", DOC / "REFERENCES.md"), ("逐数据来源映射", DATA / "PROVENANCE_MAP.json"), ("待补事项", RUN / "P02_MISSING_AND_CONFLICTS.md")]:
            body += "- " + file_link(label, target, directory / "README.md") + "\n"
        body += "\n## 文件归属\n\n"
        if directory == DATA:
            body += "CSV 保存原始转录或派生数据，PROVENANCE_MAP.json 精确说明各列/行范围的来源与转换。input_choices.json 保存配置及用户决定。build_inputs.py 生成 Flux、天然锗库存、numerical_checks.json 和对照图。statistics/ 保存图 1 数字化 CSV、溯源 JSON、叠加图和取点脚本。\n\n"
            body += table(["文件", "内容"], [(file_link(name, DATA / name, DATA / "README.md"), meaning) for name, meaning in [("mueller_coefficients.csv", "原表 24 系数"), ("kopeikin_low_energy_transcribed.csv", "用户 PDF 的 32 节点"), ("fission_fractions.csv", "参考配比与 KKL 对照"), ("reactor_flux_default.csv", "非负默认 Flux"), ("reactor_flux_reference_linear_extrapolation.csv", "原线性外推对照"), ("natural_ge_inventory.csv", "逐核素库存"), ("numerical_checks.json", "数值重建记录"), ("flux_comparison.png", "默认谱与原外推对照")]])
        elif directory == RUN:
            body += "P00–P05 保存来源、证据、问题、配置、决定与当前状态。ONBOARDING_SEED.json 与 OLD_VERSION_FINGERPRINTS.json 记录既有 v2 的历史来源和指纹。build_onboarding_v3.py 读取显式配置/数据，report_markdown.py 处理导航。sources/ 拥有论文/网页/用户图和代码身份快照，benchmark/ 拥有对照目标，qa/ 拥有实际检查、预览与截图。SOURCE_COVERAGE.json 保存字段/公式覆盖。\n\n"
        else:
            body += "experiment.physics.md 为详细主文件，summary 为精简版，EXPERIMENT_USER_INPUT.md 保存人类审阅与补充交互，REFERENCES.md 与 REFERENCES.bib 提供标准引用。主项目采用本版入口，既有 v2 保留在原隔离目录。\n\n"
            old_detail = next(Path(record["path"]) for record in read_json(RUN / "OLD_VERSION_FINGERPRINTS.json") if record["path"].replace("\\", "/").endswith("/experiment.physics.md"))
            body += file_link("既有 v2 详细版", old_detail, DOC / "README.md") + "\n\n"
        body += "## 复查与当前缺口\n\n" + gap_table()
        body += "从项目根运行数据与文档生成脚本的 `--check` 可只读核对本轮输出。当前可进入 Phase 0 规划审阅，涉及原始来源和接口的事项按 P02 补齐。\n"
        files[directory / "README.md"] = body
    files[RUN / "sources/README.md"] = "# CONUS+ v3 直接材料与来源快照\n\n来源身份、标准引用、版本、定位和哈希统一见 P00。用户 Flux 图支持文献识别，用户 PDF 表 2 支持直接转录，Kopeikin 出版社网页支持书目信息。BIPM 手册支持单位定义，project_implementation_manifest.json 记录当前代码身份。其余文献/官方网页按 P00 的具体用途使用。\n\n" + file_link("P00 来源登记", RUN / "P00_SOURCE_REGISTER.yaml", RUN / "sources/README.md") + "\n"
    for path, body in list(files.items()):
        if path.suffix == ".md":
            nav = document_links(path, RUN, user_input=path.name == "EXPERIMENT_USER_INPUT.md") if path.parent == DOC and path.name.startswith(("experiment.", "EXPERIMENT_")) else []
            files[path] = prepare_markdown(body, links=nav, toc=path.name != "experiment.physics.summary.md")
    if (ROOT / "docs/experiments/latest_analysis_index.json").is_file():
        sys.path.insert(0, str(ROOT))
        from tools.latest_experiments import readme_section
        benchmark_path = RUN / "benchmark/BENCHMARK_REGISTER.md"
        files[benchmark_path] += "\n## 当前关联计算\n\n最新SM/NSI候选已集中到Gitup01；" + file_link("当前方法和结果", DOC / "METHODS.md", benchmark_path) + "。科学来源PARTIAL、人工审核NOT_REVIEWED保持。\n"
        for directory in (DOC, DATA, RUN):
            path = directory / "README.md"
            files[path] = files[path].rstrip() + "\n\n" + readme_section(ROOT, path)
    return files


def gap_table():
    return table(["事项", "已有依据", "仍需补充/核验", "影响与下一步"], [
        ("低能 32 点原始出处", "用户 PDF 表 2 和本轮 Flux 文献图", "Kopeikin 原文图/表或作者数值文件", "全谱归一化的原始来源限制，继续向上游核对"),
        ("Ge Response 数值链", "本地 JSON、五个 Ge key、读取器与指纹", "原始核计算论文/数据包/生成脚本及归一化转换", "Response 可信预测前处理"),
        ("统计误差约定", "原图上下误差及算术平均候选列", "拟合前确认对称化办法，或取得作者数表", "进入统计实现时确认"),
        ("实现核验", "源谱、靶核数、响应公式与单位已有", "反中微子接口、Response 归一化、预测单位映射和积分收敛", "Phase 0 中分配实现与验证步骤"),
    ])


def resource_provenance(claim_map):
    def claim_ids(*keys):
        return [claim_map[key]["claim_id"] for key in keys]
    entries = [
        ("mueller_coefficients.csv", ["a0", "a1", "a2", "a3", "a4", "a5"], "all 4 rows", ["S0003"], claim_ids("source.mueller_coefficients"), "Mueller Table VI, PDF p.13", "direct transcription, 24/24 original coefficients checked"),
        ("kopeikin_low_energy_transcribed.csv", ["energy_MeV", "relative_shape"], "all 32 rows", ["S0002"], claim_ids("source.low_nodes"), "User PDF Table 2, PDF p.6 / printed p.5", "direct transcription, claimed upstream S0004 numeric table unverified"),
        ("fission_fractions.csv", ["pdf_reference_fraction"], "all 4 rows", ["S0002", "S0009"], claim_ids("source.fission_fractions"), "User PDF Eqs.(1.22)-(1.25), NEON Fig.23 caption", "direct reference mixture, isotope order explicit"),
        ("fission_fractions.csv", ["kkl_comparison_fraction"], "all 4 rows", ["S0010"], claim_ids("source.kkl_comparison_fractions"), "arXiv:2501.05206v3 PDF p.6", "comparison column only"),
        ("reactor_flux_default.csv", ["energy_MeV", "relative_shape", "flux_cm_minus2_s_minus1_MeV_minus1"], "all 10001 rows", ["S0015", "S0001", "S0002", "S0003", "S0014"], claim_ids("source.flux_table"), "build_inputs.py::build and full input dependency chain", "piecewise linear/polynomial, zero node, common normalization, low-table limit propagated to the whole normalized spectrum"),
        ("reactor_flux_reference_linear_extrapolation.csv", ["energy_MeV", "relative_shape", "flux_cm_minus2_s_minus1_MeV_minus1"], "all 10001 rows", ["S0015", "S0002", "S0003", "S0001"], claim_ids("source.flux_table"), "User PDF Eqs.(1.27)-(1.31), original first-two-point linear extrapolation", "signed diagnostic counterpart with its own normalization"),
        ("natural_ge_inventory.csv", ["number_fraction", "atomic_mass_u"], "all 5 rows", ["S0005", "S0001"], claim_ids("target.number_fractions", "target.atomic_mass_u"), "NIST Ge isotope rows, benchmark PDF p.9", "direct number fractions and atomic masses"),
        ("natural_ge_inventory.csv", ["mass_fraction", "nuclei_per_kg", "nuclear_mass_GeV_approx"], "all 5 rows", ["S0015", "S0005", "S0006"], claim_ids("target.nuclei_per_kg", "target.nuclear_mass_GeV"), "build_inputs.py::build and input constants", "explicit inventory formula, atomic mass minus electron rest masses for approximate nuclear mass"),
        ("natural_ge_inventory.csv", ["A", "Z", "N", "response_key"], "all 5 rows", ["S0007", "S0005"], claim_ids("nuclear.response_keys", "detector.Z"), "nuclei.Ge70/Ge72/Ge73/Ge74/Ge76.basic and NIST atomic number", "isotope identity and local Response key mapping"),
        ("statistics/conusplus_2501_17843v3_fig1_digitized.csv", ["excess", "error_minus", "error_plus", "error_lower_endpoint", "error_upper_endpoint", "energy_center_eVee"], "all 19 rows", ["S0001", "S0011"], claim_ids("statistics.observed", "statistics.error_minus", "statistics.error_plus"), "benchmark PDF p.10 Fig.1; coordinate_trace in provenance JSON", "vector marker and error-bar extraction, original axis units and signed values preserved"),
        ("statistics/conusplus_2501_17843v3_fig1_digitized.csv", ["bin_index", "energy_low_eVee", "energy_high_eVee", "sigma_mean_derived"], "all 19 rows", ["S0011"], claim_ids("observable.edges_eVee", "statistics.sigma_mean"), "Ordered plotted centers, centers +/-5 eVee; average of error lengths", "derived row index, edges and candidate symmetric-error convention"),
        ("numerical_checks.json", ["all numerical leaves"], "$..*", ["S0015"], claim_ids("source.flux_table", "target.nuclei_per_kg"), "build_inputs.py::build", "derived diagnostics, source hashes and explicitly prescribed numerical check points"),
    ]
    column_units = {
        "energy_MeV": "MeV", "relative_shape": "1", "flux_cm_minus2_s_minus1_MeV_minus1": "cm^-2*s^-1*MeV^-1",
        "pdf_reference_fraction": "1", "kkl_comparison_fraction": "1", "number_fraction": "1", "atomic_mass_u": "u",
        "mass_fraction": "1", "nuclei_per_kg": "nuclei/kg", "nuclear_mass_GeV_approx": "GeV",
        "A": "1", "Z": "1", "N": "1", "response_key": "isotope identifier", "bin_index": "1",
        "energy_center_eVee": "eVee", "energy_low_eVee": "eVee", "energy_high_eVee": "eVee",
    }
    for key in ("excess", "error_minus", "error_plus", "error_lower_endpoint", "error_upper_endpoint", "sigma_mean_derived"):
        column_units[key] = "counts/kg/(10eVee)"
    for index in range(6):
        column_units[f"a{index}"] = "1, exponent uses numerical E/MeV"
    return {"version": VERSION, "records": [{"file": relative(DATA / name), "columns_or_keys": columns, "range": scope,
             "column_units": {column: column_units.get(column, "diagnostic keys carry units in their names; local Response unit limits are stated in response_asset") for column in columns},
             "source_ids": sources, "claim_ids": claims, "locator": locator, "transformation": transform,
             "sha256": digest(DATA / name)} for name, columns, scope, sources, claims, locator, transform in entries],
            "response_asset": {"file": "data/responses/responses_all.json", "sha256": digest(ROOT / "data/responses/responses_all.json"),
             "keys": ["nuclei.Ge70", "nuclei.Ge72", "nuclei.Ge73", "nuclei.Ge74", "nuclei.Ge76"], "source_id": "S0007", "upstream_numeric_provenance": "PENDING",
             "units_and_normalization": "Local table declares dimensionless response coefficients/W. Oscillator length b must be inverse to the chosen momentum unit. Original nuclear-table normalization and conversion need audit."},
            "configuration": {"file": relative(DATA / "input_choices.json"), "source_field_authority": relative(RUN / "P01_EVIDENCE_LEDGER.yaml"), "decision_source": "S0014"}}


def verify_inputs(seed):
    for record in seed["old_fingerprints"]:
        if digest(record["path"]) != record["sha256"]:
            raise ValueError("Preserved v2 artifact changed " + record["path"])
    for record in read_json(RUN / "sources/project_implementation_manifest.json")["files"]:
        if digest(ROOT / record["path"]) != record["sha256"]:
            raise ValueError("Implementation identity changed " + record["path"])


def publish_outputs(files, *, check, refresh):
    payloads = {path: body.encode("utf-8") for path, body in files.items()}
    previous = {path: path.read_bytes() if path.exists() else None for path in payloads}
    changed = [path for path in payloads if previous[path] != payloads[path]]
    if check:
        if changed:
            raise ValueError("Generated output differs " + ", ".join(relative(path) for path in changed))
        return
    existing = [path for path in changed if previous[path] is not None]
    if existing and not refresh:
        raise ValueError("Existing different output requires an explicit draft refresh " + relative(existing[0]))
    if existing:
        backup = ROOT / "backup" / ("conusplus_v3_render_" + uuid.uuid4().hex)
        lines = []
        for path in existing:
            target = backup / relative(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(previous[path])
            lines.append("- " + relative(path) + " -> " + relative(target) + " SHA256 " + hashlib.sha256(previous[path]).hexdigest())
        with (ROOT / "backup/BACKUP_MANIFEST.md").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("\n## CONUS+ v3 generated draft revision\n\n" + "\n".join(lines) + "\n")
    written = []
    pending = []
    try:
        for path in changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
            pending.append(temporary)
            temporary.write_bytes(payloads[path])
            os.replace(temporary, path)
            written.append(path)
            if path.read_bytes() != payloads[path]:
                raise OSError("Written file readback differs " + relative(path))
    except Exception:
        for path in reversed(written):
            if previous[path] is None:
                path.unlink()
            else:
                path.write_bytes(previous[path])
        raise
    finally:
        for path in pending:
            path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh-draft", action="store_true")
    args = parser.parse_args()
    seed = read_json(RUN / "ONBOARDING_SEED.json")
    verify_inputs(seed)
    sources = source_records(seed)
    config, checks, claims, contract = prepare_records(seed, sources)
    files = render_documents(sources, config, checks, claims, contract)
    publish_outputs(files, check=args.check, refresh=args.refresh_draft)
    verify_inputs(seed)
    print(dump({"result": "PASS_CHECKED" if args.check else "GENERATED", "version": VERSION,
                "files": len(files), "source_records": len(sources), "adopted_fields": len(claims),
                "open_primary_source_chains": ["Kopeikin numerical table", "Ge Response nuclear calculation"], "overall_status": "PARTIAL"}).strip())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
