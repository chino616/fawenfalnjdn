"""Read acquired materials and rebuild the CsI time onboarding evidence draft.

This script reads numerical inputs and records their direct provenance. It does
not run a physics prediction or promote a scientific gate.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import uproot

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[5]
DOC = ROOT / "docs/experiments/COHERENT/CsI2021/time_resolved"
PE = np.array([0, 8, 12, 16, 20, 24, 32, 40, 48, 60.])
TIME = np.array([0, .125, .25, .375, .5, .625, .75, .875, 1, 2, 4, 6.])
REVISION = "r2"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def histogram(events, edges=TIME):
    selected = (events[:, 0] >= 0) & (events[:, 0] < 60)
    selected &= (events[:, 1] >= edges[0]) & (events[:, 1] < edges[-1])
    return np.histogram2d(events[selected, 0], events[selected, 1], bins=(PE, edges))[0].astype(int)


def extract_arrays():
    official = RUN / "sources/official"
    table = json.loads((ROOT / "data/responses/responses_all.json").read_text(encoding="utf-8"))
    nuclear = {}
    metadata = []
    for nucleus, key in [("Cs133", "Cs133"), ("I127", "I")]:
        entry = table["nuclei"][key]
        for channel, coefficients in entry["responses"].items():
            values = np.array(coefficients, dtype=float)
            array_key = nucleus + "_" + channel
            nuclear[array_key] = values
            metadata.append(dict(nucleus=nucleus, json_key=f"nuclei.{key}.responses.{channel}",
                array_key=array_key, shape=list(values.shape), coefficient_order="ascending",
                axes=["outgoing_nucleon(p,n)", "incoming_nucleon(p,n)", "polynomial_power"],
                power_range=[0, values.shape[2] - 1], first_three_coefficients=values[:, :, :3].tolist(),
                exp_factor=entry["exp_factor"], basic=entry["basic"],
                numerical_availability="PRESENT_EXACT_LOCAL_COPY", original_source="LOCAL_DATA_RESOURCE_USER_SELECTED",
                upstream_correspondence="UNVERIFIED_OPTIONAL_EXTERNAL_AUDIT", conversion_equivalence="EXACT_LOCAL_EXTRACTION"))
    np.savez_compressed(RUN / "data/nuclear_response_CsI.npz", **nuclear)
    write_json(RUN / "data/nuclear_response_inventory.json", metadata)
    c = np.loadtxt(official / "dataBeamOnC.txt")
    ac = np.loadtxt(official / "dataBeamOnAC.txt")
    observed, control = histogram(c), histogram(ac)
    ac12 = histogram(ac, np.array([0., 12.])).sum(axis=1)
    rate = .0494
    integrals = np.exp(-rate * TIME[:-1]) * (-np.expm1(-rate * np.diff(TIME))) / rate
    ss = ac12[:, None] * integrals[None, :] / (-np.expm1(-rate * 12) / rate)
    arrays = dict(PE_edges=PE, time_edges_us=TIME, C_counts=observed, AC_counts=control, SS_counts=ss)
    root_inventory = []
    with uproot.open(official / "snsFlux2D.root") as source:
        for component, key in [("mu", "convolved_energy_time_of_nu_mu"),
                ("e", "convolved_energy_time_of_nu_e"),
                ("mub", "convolved_energy_time_of_anti_nu_mu"),
                ("ebar", "convolved_energy_time_of_anti_nu_e")]:
            hist = source[key]
            values, time_edges_ns, energy_edges = hist.to_numpy(flow=False)
            time_mass = values.sum(axis=1, dtype=np.float64)
            energy_mass = values.sum(axis=0, dtype=np.float64)
            arrays[component + "_time_mass"] = time_mass
            arrays[component + "_energy_mass"] = energy_mass
            arrays["ROOT_time_edges_us"] = time_edges_ns / 1000
            arrays["ROOT_energy_edges_MeV"] = energy_edges
            index = np.unravel_index(np.argmax(values), values.shape)
            root_inventory.append(dict(component=component, root_key=key, shape=list(values.shape),
                axes=["time_ns", "energy_MeV"], ranges=[[float(time_edges_ns[0]), float(time_edges_ns[-1])],
                    [float(energy_edges[0]), float(energy_edges[-1])]], sum=float(time_mass.sum()),
                reference_0_6_us_fraction=float(time_mass[:6000].sum() / time_mass.sum()),
                representative_cell=dict(index=list(map(int, index)), value=float(values[index])),
                high_energy_ge60_fraction=float(energy_mass[60:].sum() / energy_mass.sum())))
    np.savez_compressed(RUN / "data/analysis_inputs.npz", **arrays)
    write_json(RUN / "data/ROOT_inventory.json", root_inventory)
    with (RUN / "data/observed_99bins.csv").open("w", encoding="utf-8") as stream:
        stream.write("PE_bin,time_bin,C_raw,AC_raw,SS_derived\n")
        for i in range(9):
            for j in range(11):
                stream.write(f"{i},{j},{observed[i,j]},{control[i,j]},{ss[i,j]:.17g}\n")
    return table, metadata, root_inventory, arrays, c.shape, ac.shape


def build_records():
    table, nuclear, roots, arrays, c_shape, ac_shape = extract_arrays()
    sources = []
    claims = []
    sections = {}

    def source(identifier, path, citation, url, scope, source_type="primary_paper", upstream=()):
        path = ROOT / path
        versions = {"S_MEAS": "arXiv2110.07730v2", "S_SUP": "arXiv2110.07730v2 ancillary",
            "S_2211": "arXiv2211.11905v2", "S_2202": "arXiv2202.11002v3", "S_QF_PAPER": "arXiv2111.02477v2",
            "S_NIST": "CODATA2022; May2024 data update", "S_PDG": "PDG2024 charged pion listing",
            "S_ELASTIC_CS": "commit a979c39c89c615c7e719b84006cafa94526b4517",
            "S_ELASTIC_I": "commit a979c39c89c615c7e719b84006cafa94526b4517",
            "S_MU2E": "commit15bef514375298b57d9b07852870be3c408c2b19; v2"}
        sources.append(dict(source_id=identifier, title=citation, citation=citation,
            source_type=source_type, uri_or_path=relative(path), original_url=url,
            version=versions.get(identifier, "2110.07730v2 ancillary" if source_type == "official_data" else "Local2026-11-06 snapshot pinned by SHA256"),
            sha256=fingerprint(path), bytes=path.stat().st_size, accessed="2026-11-06",
            verification_scope=scope, upstream_source_ids=list(upstream),
            numerical_availability="PRESENT", dataset_scope="CsI2021_time_9x11"))

    def add(section, identifier, label, value, unit, source_ids, locator, *, status="SOURCE_EXTRACTED",
            notes="", resource=None, inputs=(), checks=None, adoption="ADOPTED_DRAFT", blocking_scope=()):
        source_ids = list(source_ids)
        claim = dict(claim_id=identifier, field=label, value=value, unit=unit, status=status,
            source_id=source_ids[0] if source_ids else None, source_ids=source_ids,
            locator=locator, verification_scope=notes or "已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系", input_claims=list(inputs),
            numerical_resource=resource, verification_checks=checks or dict(
                numerical_data="PRESENT", direct_material="READ", upstream="SEE_P00", applicability="DRAFT"),
            output_locations=[relative(DOC / "experiment.physics.md") + "#" + section],
            adoption=adoption)
        claims.append(claim)
        sections.setdefault(section, dict(decision_status="DRAFT", fields={}, evidence_refs=[]))
        sections[section]["fields"][identifier] = dict(value=value, unit=unit,
            evidence_claims=[identifier], provenance_status=status,
            decision_status="BLOCKED" if status == "MISSING" and blocking_scope else "DRAFT",
            blocking_scope=list(blocking_scope))
        sections[section]["evidence_refs"].append(identifier)

    official = relative(RUN / "sources/official")
    source("S_MEAS", "docs/references/COHERENT/2110.07730v2.pdf",
        "D. Akimov et al. (COHERENT), Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT, Phys. Rev. Lett. 129, 081801 (2022), arXiv:2110.07730v2.",
        "https://arxiv.org/abs/2110.07730v2", "版本、实验身份和测量用途已核，数值附件另登记")
    source("S_SUP", official + "/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf",
        "COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary.",
        "https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf",
        "p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读", "supplement", ["S_MEAS"])
    source("S_2211", "docs/references/COHERENT/2211.11905v2.pdf",
        "V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2.",
        "https://arxiv.org/abs/2211.11905v2", "p3、p12–14、p33 Table II、p35 Fig.18 已核")
    source("S_2202", "docs/references/COHERENT/2202.11002v3.pdf",
        "M. Atzori Corona et al., Probing light mediators and (g−2)mu through detection of coherent elastic neutrino nucleus scattering at COHERENT, JHEP 05 (2022) 109, arXiv:2202.11002v3.",
        "https://arxiv.org/abs/2202.11002v3", "arXiv 式(6)与期刊式(2.6)的统计分支及四个归一化误差已读")
    source("S_QF_PAPER", "docs/references/COHERENT/2111.02477v2.pdf",
        "COHERENT Collaboration, Measurement of scintillation response of CsI[Na] to low-energy nuclear recoils by COHERENT, JINST 17 (2022) P10034, arXiv:2111.02477v2.",
        "https://arxiv.org/abs/2111.02477v2", "Sec.8，PDF p23/印刷p21 的2–70keV拟合域与式(8.1)已核")
    for name in ["snsFlux2D.root", "dataBeamOnC.txt", "dataBeamOnAC.txt", "brnPE.txt", "brnTrec.txt",
            "ninPE.txt", "ninTrec.txt", "effCoefficients.txt", "scintRespCoefficients.txt"]:
        source("S_" + name.split(".")[0], official + "/" + name,
            "COHERENT Collaboration, " + name + ", arXiv:2110.07730v2 ancillary data release.",
            "https://arxiv.org/src/2110.07730v2/anc/" + name,
            "实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记", "official_data", ["S_SUP"])
    source("S_LOCAL_W", "data/responses/responses_all.json",
        "CEvNS-pyEFT project, local aggregated responses_all.json, format Mu2eNRET_ResponseW_v1, original export provenance unresolved.",
        None, "用户明确选择直接复用原data核表；Cs133/I八通道已读、逐值提取；现读码的单位/基底约定已核。外部作者生成链仍未核实，不是本次原表复用前置", "legacy_code")
    upstream = RUN / "sources/upstream_nuclear"
    source("S_ELASTIC_CS", relative(upstream / "Elastic/Cs133_GCN5082.txt"),
        "Berkeley Electroweak Physics, Elastic/Cs133_GCN5082.txt, commit a979c39c89c615c7e719b84006cafa94526b4517.",
        "https://github.com/Berkeley-Electroweak-Physics/Elastic/blob/a979c39c89c615c7e719b84006cafa94526b4517/Cs133_GCN5082.txt",
        "作者原始密度矩阵已取得并读到数值；与当前聚合W系数的对应关系仅为候选", "theory_input")
    source("S_ELASTIC_I", relative(upstream / "Elastic/I127_GCN5082.txt"),
        "Berkeley Electroweak Physics, Elastic/I127_GCN5082.txt, commit a979c39c89c615c7e719b84006cafa94526b4517.",
        "https://github.com/Berkeley-Electroweak-Physics/Elastic/blob/a979c39c89c615c7e719b84006cafa94526b4517/I127_GCN5082.txt",
        "作者原始密度矩阵已取得；尚未复算当前聚合系数", "theory_input")
    source("S_MU2E", relative(upstream / "Mu2e_NRET/v2/mathematica/mu2elib_v2.wl"),
        "Berkeley Electroweak Physics, Mu2e_NRET v2/mathematica/mu2elib_v2.wl, commit 15bef514375298b57d9b07852870be3c408c2b19; W. C. Haxton et al., Phys. Rev. C 107, 035504 (2023), DOI 10.1103/PhysRevC.107.035504.",
        "https://github.com/Berkeley-Electroweak-Physics/Mu2e_NRET/blob/15bef514375298b57d9b07852870be3c408c2b19/v2/mathematica/mu2elib_v2.wl",
        "作者代码和README引文已取得；尚未证明当前JSON由此版本生成", "theory_input", ["S_ELASTIC_CS", "S_ELASTIC_I"])
    source("S_NIST", relative(RUN / "sources/NIST_CODATA2022_allascii.txt"),
        "NIST Standard Reference Database 121, CODATA 2022 recommended values, data update May2024, allascii table.",
        "https://physics.nist.gov/cuu/Constants/Table/allascii.txt", "逐常数原始行值与单位已核", "official_data")
    source("S_PDG", relative(RUN / "sources/PDG2024_pi_charged.pdf"),
        "S. Navas et al. (Particle Data Group), Review of Particle Physics, Phys. Rev. D 110, 030001 (2024), charged pion listing.",
        "https://pdg.lbl.gov/2024/listings/rpp2024-list-pi-plus-minus.pdf", "p1 pi± MASS OUR FIT 139.57039±0.00018MeV已视觉核对", "official_data")
    source("S_AUDIT", relative(RUN / "evidence/legacy_resolution/input_resolution.json"),
        "Project-generated CsI input-resolution audit, 2026-11-06, selected legacy260929 checkout. Numerical diagnostic with unresolved primary nuclear provenance.",
        None, "原始输出已回读；其186项测试属于旧目录工程验证，核响应上游缺口传递到物理解释", "legacy_code")
    source("S_AUDIT_CODE", relative(RUN / "evidence/legacy_resolution/code/tools/resolve_input_issues.py"),
        "Project resolve_input_issues.py, native Response numerical diagnostic and recorded input transformations,2026-11-06.",
        None, "算法和文件字节已保留；其余旧共享代码按原SHA引用", "legacy_code")
    for identifier, filename, purpose in [
            ("S_LEGACY_EFF", "legacy/slow_counts_csi2021.py", "旧效率参数及非负裁剪的直接代码"),
            ("S_LEGACY_SNS", "legacy/sns.py", "旧SNS质量元数据与200点插值源的直接代码"),
            ("S_TIME_CODE", "time_acceptance.py", "时间形状、固定参考分母及注量转换的直接代码"),
            ("S_DOMAIN_CODE", "analysis_inputs.py", "2–70keVnr适用域保护的直接代码")]:
        source(identifier, relative(RUN / "evidence/legacy_resolution/code" / filename),
            "Project legacy CsI implementation, " + filename + ", snapshot2026-11-06.",
            None, purpose + "，属于项目实施依据，外部科学来源另记", "legacy_code")
    decision = dict(date="2026-11-06", evidence="Conversation user instructions",
        decisions=[dict(id="D_RESPONSE", text="核结构用RESPONSE处理，两套benchmark独立验收"),
                   dict(id="D_PE", text="用旧程序[0,8,12,16,20,24,32,40,48,60]，无原始数字依据则标重建值"),
                   dict(id="D_REUSE", text="优先复用旧二维预测、背景、时间偏移和likelihood"),
                   dict(id="D_PROVENANCE", text="重写onboarding，将逐数据来源严格写入文件及主规则，保留草稿与缺口"),
                   dict(id="D_LOCAL_RESPONSE", text="response本来就可以直接去调用原始的 data中的response",
                        interpretation="本次以原data/responses/responses_all.json为直接数值来源；外部生成链仍记未核实，不作为原表复用的阻断")])
    existing_path = RUN / "DECISION_LOG.json"
    if existing_path.exists():
        previous = json.loads(existing_path.read_text(encoding="utf-8"))
        known = {d["id"] for d in decision["decisions"]}
        decision["decisions"].extend(d for d in previous.get("decisions", []) if d["id"] not in known)
    write_json(RUN / "DECISION_LOG.json", decision)
    source("S_DECISION", relative(RUN / "DECISION_LOG.json"), "User decisions transcribed from this conversation,2026-11-06.",
        None, "仅记录实际用户选项，不将其视作外部事实核验", "other")
    source("S_PREPARE", relative(Path(__file__)), "Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06.",
        None, "本次提取/直方图/数组逐值核对算法，可重跑", "legacy_code")

    add("identity", "C_ID", "分析身份", "CsI2021_time_9x11", "1", ["S_MEAS", "S_DECISION"],
        "原测量标题与摘要；D_PROVENANCE", notes="同一测量的时间分辨分析草稿，尚未取得终稿科学接受")
    for identifier, label, value, unit, locator in [
            ("C_POT", "累计POT", 3.198e23, "POT", "Supplement p2 lines76–81"),
            ("C_YIELD", "每味每POT产额", .0848, "neutrinos/flavor/POT", "Supplement p2 lines78–81；10%误差"),
            ("C_L", "基线", 19.3, "m", "Supplement p2 lines78–81"),
            ("C_MASS", "论文探测器质量", 14.6, "kg", "Supplement p2 line81；2211 p12 Eq28段落")]:
        add("target" if identifier == "C_MASS" else "source", identifier, label, value, unit, ["S_SUP"], locator)
    for identifier, label, value, unit, locator in [
            ("C_MMU", "muon质量", 105.6583755, "MeV", "allascii line223"),
            ("C_ME", "electron质量", .51099895069, "MeV", "allascii line109"),
            ("C_U", "原子质量单位能量", .93149410372, "GeV", "allascii line24；MeV除1000"),
            ("C_GF", "Fermi常数", 1.1663787e-5, "GeV^-2", "allascii line135")]:
        add("constants", identifier, label, value, unit, ["S_NIST"], locator)
    add("constants", "C_MPI", "带电pion质量", 139.57039, "MeV", ["S_PDG"], "PDF/印刷p1 OUR FIT；误差0.00018MeV")
    add("constants", "C_SIN2_PAPER", "2211名义弱混合角", .23857, "1", ["S_2211"],
        "p3 Sec2.1 Eqs1–3后说明，原文误差(5)", adoption="PAPER_REFERENCE")
    add("constants", "C_SIN2_NATIVE", "旧原生诊断弱混合角", .2387, "1", ["S_AUDIT_CODE"],
        "verified_sm_cross_section直接原生调用的sin2thetaW参数", status="REFERENCE_ONLY",
        notes="项目配置值；与2211名义数值分列，后续统一配置需审阅", adoption="LEGACY_DIAGNOSTIC")
    eta = .0848 * 3.198e23 / (4 * np.pi * (100 * 19.3) ** 2)
    line = (139.57039 ** 2 - 105.6583755 ** 2) / (2 * 139.57039)
    add("source", "C_ETA", "几何稀释后的每味积分注量", eta, "cm^-2", ["S_2211", "S_PREPARE"],
        "p12 Eq29后归一化；prepare_records.py eta表达式", status="PROJECT_DERIVED", inputs=["C_POT", "C_YIELD", "C_L"],
        notes="100是m→cm的精确换算，曝光只施加一次")
    add("source", "C_LINE", "prompt谱线能量", line, "MeV", ["S_2211", "S_PREPARE"], "p12 Eq29；两体衰变公式",
        status="PROJECT_DERIVED", inputs=["C_MPI", "C_MMU"])
    add("source", "C_ENDPOINT", "论文DAR能谱上限", 105.6583755 / 2, "MeV", ["S_2211"],
        "p12 Eqs28–29，m_mu/2近似", status="PROJECT_DERIVED", inputs=["C_MMU"], notes="旧积分器包含electron质量修正，其数值不与此混用")
    add("source", "C_COMPONENTS", "采用的DAR分量", ["nu_mu", "nu_e", "anti_nu_mu"], "1", ["S_2211"], "p12 Eq29")
    add("source", "C_ROOT", "官方ROOT完整二维数组", roots, "weighted bin mass", ["S_snsFlux2D", "S_PREPARE"],
        "各TH2F对象的time(ns),energy(MeV)轴；原始15000×600箱",
        resource=dict(path=relative(RUN / "sources/official/snsFlux2D.root"), keys=[r["root_key"] for r in roots]),
        notes="全部四味已读；默认DAR仅三主味。ROOT权重由源模型单独赋绝对注量")
    add("source", "C_TIME_MARGINAL", "ROOT时间边缘与0–6us分数", [r["reference_0_6_us_fraction"] for r in roots[:3]],
        "probability", ["S_snsFlux2D", "S_PREPARE"], "每TH2F对完整能量轴求和后，前6000个1ns时间箱/全域和",
        status="PROJECT_DERIVED", inputs=["C_ROOT"],
        resource=dict(path=relative(RUN / "data/analysis_inputs.npz"), keys=["mu_time_mass", "e_time_mass", "mub_time_mass"], shape=[3, 15000]))
    add("source", "C_SOURCE_CHOICE", "源表示选择", "DAR解析谱 × ROOT各味时间边缘", "1", ["S_2211", "S_DECISION"],
        "p12 Eq29、p13 Eq32；D_REUSE", status="PROJECT_DERIVED", inputs=["C_COMPONENTS", "C_ROOT"],
        notes="按目标论文形式形成草稿；完整ROOT联合与因子化不同，旧结果只作诊断")
    add("target", "C_STOICH", "Cs/I化学计量", [1, 1], "number ratio", ["S_MEAS", "S_2211"],
        "CsI[Na]靶身份；p12 Eq28后靶核计数定义", notes="Na掺杂未加入第三个靶核贡献，需保留适用性说明")
    add("target", "C_MASS_LEGACY", "旧诊断实际质量", 14.57, "kg", ["S_AUDIT"],
        "ROOT_vs_legacy.identical_absolute_inputs.detector_mass_kg", status="REFERENCE_ONLY",
        notes="旧生成结果的输入；本草稿论文质量14.6kg见C_MASS", adoption="LEGACY_DIAGNOSTIC")
    add("source", "C_INTERPOLATION_LEGACY", "旧Michel谱表示", 200, "nodes over0.001–300MeV", ["S_LEGACY_SNS"],
        "loadNeutrinoEmpiricalFluxSNS num_points=200默认及CsI2021范围；np.interp分段线性",
        status="REFERENCE_ONLY", notes="旧诊断输入，论文解析谱见Eq29，端点和质量约定分列", adoption="LEGACY_DIAGNOSTIC")
    for nucleus, key in [("Cs133", "Cs133"), ("I127", "I")]:
        basic = table["nuclei"][key]["basic"]
        add("target", "C_BASIC_" + nucleus, nucleus + "实际核表元数据", basic, "A,Z,N,J,T dimensionless; b GeV^-1 in current reader",
            ["S_LOCAL_W"], f"nuclei.{key}.basic", status="REFERENCE_ONLY",
            notes="数值已取得；b单位按原读取器约定，用户选择复用原表。外部作者对应仍未核实", checks=dict(numerical_data="PRESENT", direct_material="READ",
                original_source="LOCAL_DATA_RESOURCE", upstream="UNVERIFIED_OPTIONAL_AUDIT", applicability="USER_SELECTED_LOCAL_REUSE"))
    add("nuclear", "C_NUCLEAR_CHOICE", "核结构选择", "native RESPONSE", "1", ["S_DECISION"],
        "D_RESPONSE、D_LOCAL_RESPONSE", status="USER_CONFIRMED", notes="直接调用原data核表；外部生成链不作为本次复用前置")
    add("nuclear", "C_RESOURCE_BINDING", "实际调用资源与核素映射", dict(path="data/responses/responses_all.json",
        reader="cevns_pyeft.nuclear.response.ResponseDB", nucleus_keys={"Cs133": "Cs133", "I127": "I"}), "1",
        ["S_LOCAL_W", "S_DECISION"], "原JSON nuclei.Cs133和nuclei.I；D_LOCAL_RESPONSE", status="USER_CONFIRMED",
        notes="完整原表为调用权威；提取NPZ只用于查看及逐值一致性核验")
    for entry in nuclear:
        add("nuclear", "C_W_" + entry["array_key"], entry["array_key"] + "系数", entry, "dimensionless coefficients under local convention",
            ["S_LOCAL_W", "S_PREPARE"], entry["json_key"] + "；全部2×2×K系数逐值复制",
            status="SOURCE_EXTRACTED", resource=dict(path="data/responses/responses_all.json", json_key=entry["json_key"],
                review_npz=relative(RUN / "data/nuclear_response_CsI.npz"), key=entry["array_key"], shape=entry["shape"]),
            checks=dict(numerical_data="PRESENT", direct_material="READ_EXACT_COPY", original_source="LOCAL_DATA_RESOURCE",
                external_upstream="UNVERIFIED_OPTIONAL_AUDIT", local_extraction="EXACT_EQUALITY", applicability="USER_SELECTED_LOCAL_REUSE"),
            notes="直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记",
            adoption="ADOPTED_LOCAL_RESOURCE_BY_USER")
    add("nuclear", "C_UPSTREAM", "取得的作者核结构材料", ["Elastic Cs133_GCN5082.txt", "Elastic I127_GCN5082.txt", "Mu2e_NRET v1/v2 author code"],
        "1", ["S_ELASTIC_CS", "S_ELASTIC_I", "S_MU2E"], "Elastic全部密度矩阵行；Mu2e_NRET作者README和响应函数实现",
        notes="固定提交及SHA已保存，尚未证实为当前JSON的确切上游", adoption="CANDIDATE_UPSTREAM")
    add("nuclear", "C_W_CONVERSION", "可选外部作者导出链审计", None, "1", ["S_LOCAL_W", "S_MU2E"],
        "缺少当前聚合JSON的原始导出脚本/Notebook、版本、基底/归一化逐项对照", status="MISSING",
        notes="用户已明确接受原data直接调用。外部作者溯源仍未闭合，仅限制外部来源认证，不阻断本次本地资源复用",
        adoption="OPTIONAL_EXTERNAL_AUDIT", blocking_scope=["external_nuclear_source_certification"])
    iodine = table["nuclei"]["I"]["responses"]["M"][1][1][0]
    add("nuclear", "C_I_ZERO", "I127局部M_nn(0)与N²残差", dict(M_nn_0=iodine, N_squared=74 ** 2, residual=iodine - 74 ** 2),
        "1", ["S_LOCAL_W", "S_PREPARE"], "nuclei.I.responses.M[1][1][0]；N=74",
        status="PROJECT_DERIVED", inputs=["C_W_I127_M", "C_BASIC_I127"], notes="内部归一化诊断，不能代替原始核表核验")
    qf = np.loadtxt(RUN / "sources/official/scintRespCoefficients.txt")
    eff = np.loadtxt(RUN / "sources/official/effCoefficients.txt")
    add("detector", "C_QF", "nominal淬灭多项式系数", qf[0].tolist(), "[1,MeV^-1,MeV^-2,MeV^-3]", ["S_scintRespCoefficients", "S_2211"],
        "scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee")
    add("detector", "C_QF_SYSTEMATICS", "淬灭系数全部模型", qf.tolist(), "同nominal系数单位", ["S_scintRespCoefficients"],
        "line7、10、12、15、17；nominal与两条±1sigma方向", resource=dict(path=official + "/scintRespCoefficients.txt", shape=[5, 4]),
        notes="文件全部取得；当前简化统计只使用总率误差，未声称逐形状实现")
    add("detector", "C_QF_DOMAIN", "QF拟合适用域", [2, 70], "keVnr", ["S_QF_PAPER"], "Sec8，PDF p23/印刷p21 Fitting approach",
        notes="校准点范围3–63keVnr，与拟合域分别记录")
    add("detector", "C_LY", "光产额", 13.35, "PE/keVee", ["S_SUP"], "p3 lines90–93")
    add("detector", "C_GAMMA", "Gamma展宽参数", dict(a_numerator=.0749, b_slope=9.56), "a=0.0749/Eee(keVee); b=9.56*Eee(keVee)",
        ["S_SUP", "S_2211"], "Supplement p3 Eq3 lines94–101；2211 p12 Eq31")
    add("detector", "C_EFF", "官方nominal能量效率系数", eff[0].tolist(), "a,d dimensionless; b PE^-1; c PE", ["S_effCoefficients"],
        "effCoefficients.txt line7，公式与x=PE见头部line1–4")
    add("detector", "C_EFF_SYSTEMATICS", "效率系数全部模型", eff.tolist(), "同nominal效率单位", ["S_effCoefficients"],
        "line7、10、12；两条systematic注释均写+1sigma", notes="原发布文件的符号标签歧义保留CONFLICT", status="CONFLICT")
    add("detector", "C_EFF_LEGACY", "旧程序效率常数项", -.3333, "1", ["S_LEGACY_EFF", "S_effCoefficients"],
        "旧slow_counts_csi2021.py CsI2021EfficiencyParams.d；官方line7为−0.333322", status="CONFLICT",
        notes="旧数值结果使用舍入值；本草稿nominal采用官方−0.333322，旧拟合不是本草稿同条件结果", adoption="LEGACY_DIAGNOSTIC")
    add("detector", "C_TIME_EFF", "时间效率转折及衰减", [.52, .0494], "[us,us^-1]", ["S_SUP", "S_2211"],
        "Supplement p2 Eq1 lines64–68；2211 p13 Eq33")
    add("detector", "C_SHIFTS", "时间及效率位移范围", dict(time_shift_us=[-.25, .25], efficiency_shift_PE=[-1, 1]), "us and PE",
        ["S_2211"], "p12 Eq30、p13脚注8和p14 alpha6/alpha7说明", notes="原文无完整shift后分母程序说明，固定nominal分母为项目约定")
    add("observable", "C_PE", "PE边界", PE.tolist(), "PE", ["S_DECISION", "S_SUP"], "D_PE；Supplement p5 Fig2水平误差棒",
        status="PROJECT_DERIVED", notes="指定重建值；尚未取得作者机器数字边界表")
    add("observable", "C_TIME", "时间边界", TIME.tolist(), "us", ["S_2211"], "p35 Fig18全部十一面板标签")
    add("observable", "C_ENDPOINT_RULE", "端点归箱规则", "每箱左闭右开，PE60及t6us排除", "1", ["S_DECISION", "S_PREPARE"],
        "统一端点的用户要求；histogram筛选实现", status="PROJECT_DERIVED")
    for identifier, label, values, key, sid, shape in [
            ("C_OBS", "C逐箱原始计数", arrays["C_counts"], "C_counts", "S_dataBeamOnC", c_shape),
            ("C_CONTROL", "AC逐箱原始计数", arrays["AC_counts"], "AC_counts", "S_dataBeamOnAC", ac_shape)]:
        add("observable", identifier, label, values.tolist(), "events/bin", [sid, "S_PREPARE"],
            f"原始文件全部{shape[0]}行PE,time_us；按C_PE/C_TIME重分箱，轴顺序[PE,time]",
            status="PROJECT_DERIVED", inputs=["C_PE", "C_TIME", "C_ENDPOINT_RULE"],
            resource=dict(path=relative(RUN / "data/analysis_inputs.npz"), key=key, shape=[9, 11]),
            notes=f"总计{int(values.sum())}，为官方逐事件表的项目重分箱值")
    add("statistics", "C_SS", "SS平滑背景", float(arrays["SS_counts"].sum()), "events in0–6us", ["S_dataBeamOnAC", "S_SUP", "S_PREPARE"],
        "AC PE<60、0≤t<12us 2242events；p2 lines55–59指数k=0.0494/us；prepare_records.py integrals",
        status="PROJECT_DERIVED", inputs=["C_CONTROL", "C_TIME_EFF"], resource=dict(path=relative(RUN / "data/analysis_inputs.npz"), key="SS_counts", shape=[9, 11]),
        notes="整文件0–12us作为输入，与0–6us的1295个AC事件区别清楚")
    for component in ["brn", "nin"]:
        pe_table = np.loadtxt(RUN / f"sources/official/{component}PE.txt")
        time_table = np.loadtxt(RUN / f"sources/official/{component}Trec.txt")
        add("statistics", "C_" + component.upper() + "_PE", component.upper() + "能量表", dict(shape=list(pe_table.shape),
            center_range_PE=[float(pe_table[0,0]), float(pe_table[-1,0])], sum=float(pe_table[:,1].sum()), first_rows=pe_table[:4].tolist()),
            "relative bin weight; epsilon_PE already applied", ["S_" + component + "PE", "S_SUP"],
            "PE文件全部两列；Supplement p2 lines60–75", resource=dict(path=official + f"/{component}PE.txt", columns=["PE_center", "weight"]),
            notes="不得重复施加能量效率；发布的绝对概率归一含义未完全闭合")
        add("statistics", "C_" + component.upper() + "_TIME", component.upper() + "时间表", dict(shape=list(time_table.shape),
            center_range_us=[float(time_table[0,0]), float(time_table[-1,0])], sum=float(time_table[:,1].sum()), first_rows=time_table[:4].tolist()),
            "events per0.01us bin at13.99GWhr; before epsilon_T", ["S_" + component + "Trec", "S_SUP"],
            "Trec文件全部两列；Supplement p2 lines62–68", resource=dict(path=official + f"/{component}Trec.txt", columns=["time_us", "events_per_bin"]),
            notes="time效率另施加；曝光只出现一次")
    add("statistics", "C_PRIORS", "官方背景总数prior", [18.4, 5.6, 1286], "events for BRN,NIN,SS", ["S_SUP"],
        "p7 TableI Prior Prediction", notes="不是模板归一化的调节目标")
    add("statistics", "C_PULL_JHEP", "JHEP四pull宽度", [.12, .25, .35, .021], "relative sigma", ["S_2202"],
        "arXiv Eq6后说明，对应期刊Eq2.6")
    add("statistics", "C_PULL_2211", "2211 CEvNS-only归一化宽度", [.1145, .25, .35, .021], "relative sigma", ["S_2211"], "p14 Eqs36、38后说明")
    add("statistics", "C_RADIUS", "2211原文半径nuisance", .05, "relative sigma", ["S_2211"], "p14 alpha4及Eq3的RA变形",
        notes="原生RESPONSE当前固定半径，此原文nuisance尚未形成等价实现", adoption="PAPER_REFERENCE")
    add("statistics", "C_SM_PAPER", "2211论文SM最低卡方", 83.2, "chi2", ["S_2211"], "p33 TableII CsI SM cell",
        notes="外部目标，仅引用原文；不与不一致配置的旧结果直接判PASS", adoption="PAPER_REFERENCE")
    add("prediction", "C_RECOIL_POLICY", "反冲积分域保护", [2, 70], "keVnr", ["S_QF_PAPER", "S_DOMAIN_CODE"],
        "校准Sec8；analysis_inputs.py guards；DAR上界还受运动学约束", status="PROJECT_DERIVED", inputs=["C_QF_DOMAIN"],
        notes="下界从2keV开始是项目截断政策；原先0.1–2keV延拓影响另作诊断")
    add("prediction", "C_DENOM", "平移后的时间归一分母", "固定零位移0–6us参考分数", "1", ["S_TIME_CODE", "S_2211"],
        "time_acceptance.build_time_weights的nominal参考分数；论文p13脚注8未给完整程序细节", status="PROJECT_DERIVED",
        inputs=["C_TIME_MARGINAL"], notes="项目实施约定，未标成作者代码已核")
    audit = json.loads((RUN / "evidence/legacy_resolution/input_resolution.json").read_text(encoding="utf-8"))
    add("prediction", "C_DIAGNOSTICS", "旧实现数值诊断", dict(full_fluence_SM=audit["signal_convergence"]["records"][-1]["total_events"],
        same_eta_6us_SM=audit["time_fluence_scope"]["records"][1]["same_eta_6us_shape_events"],
        max_grid_change=audit["time_fluence_scope"]["max_bin_grid_change"],
        ROOT_correlation_max=audit["ROOT_correlation"]["max_total_bin_absolute_difference"],
        ROOT_vs_legacy_max=audit["ROOT_vs_legacy"]["max_bin_total_difference"]), "events or events/bin", ["S_AUDIT", "S_AUDIT_CODE"],
        "signal_convergence、time_fluence_scope、ROOT_correlation、ROOT_vs_legacy对应JSON字段",
        status="PROJECT_DERIVED", inputs=["C_RESOURCE_BINDING", "C_W_Cs133_M", "C_W_I127_M", "C_ETA", "C_QF", "C_EFF_LEGACY"],
        notes="旧质量14.57kg、弱角0.2387、200点谱插值和效率d=−0.3333；未认证核响应上游，不能作为严格物理预测通过", adoption="LEGACY_DIAGNOSTIC")
    add("statistics", "C_BG_GAP", "BRN/NIN全域概率候选效率后总数", [audit["neutron_background"][c]["probability_normalized_after_time_efficiency"] for c in ["brn", "nin"]],
        "events", ["S_AUDIT", "S_AUDIT_CODE"], "background_audit；分母为各PE表全域和，未用prior作缩放目标", status="PROJECT_DERIVED",
        inputs=["C_BRN_PE", "C_BRN_TIME", "C_NIN_PE", "C_NIN_TIME", "C_TIME_EFF", "C_PRIORS"],
        notes="18.30963327/5.17899996与18.4/5.6不闭合；时间效率前口径仍待发布者说明")

    issues = [
        dict(id="G_NUCLEAR", item="RESPONSE原表复用与可选外部生成链", kind="USER_SELECTED_LOCAL_RESOURCE", status="LOCAL_REUSE_READY",
            available="本地Cs/I全部16个通道数组、作者Elastic密度矩阵和Mu2e_NRET代码已取得",
            needed="本次直接调用原data已获用户明确选择；外部导出Notebook/版本仍可补充，只影响作者来源认证",
            affects=["外部作者来源认证"], claims=["C_RESOURCE_BINDING", "C_W_CONVERSION"]),
        dict(id="G_BG", item="BRN/NIN绝对归一与时间效率", kind="PHYSICAL_NORMALIZATION_CONFLICT", status="BLOCKED",
            available="官方四个表、曝光和两个效率作用域均已取得，候选算法及差额已回读",
            needed="作者明确PE概率归一、Trec绝对归一和TableI在时间效率前/后的口径",
            affects=["P09论文统计组成", "P10外部benchmark"], claims=["C_BG_GAP", "C_PRIORS"]),
        dict(id="G_THEORY", item="原生Interaction/Matching与论文定义", kind="PROVENANCE_REVIEW_PENDING", status="PARTIAL",
            available="原生代码可读取，G_F和质量常数已追到NIST/PDG，弱角两个配置已分列",
            needed="按所选SM/LEFT范围完成核子与匹配数值到原文式及单位的逐项对应；此项是未完成审计，不能写成数值文件不存在",
            affects=["P04共享理论适用性", "同模型外部比较"], claims=["C_GF", "C_SIN2_PAPER", "C_SIN2_NATIVE"]),
        dict(id="G_CONFIG", item="旧诊断与本草稿输入差异", kind="CONFIGURATION_DIFFERENCE", status="PARTIAL",
            available="14.57/14.6kg、−0.3333/−0.333322、.2387/.23857、插值谱/解析谱差异已定位",
            needed="按统一新草稿配置生成新的同条件预测；当前原表可直接复用",
            affects=["同条件数值比较"], claims=["C_DIAGNOSTICS", "C_EFF_LEGACY", "C_MASS"]),
        dict(id="G_PE", item="PE边界原始数字表", kind="RECONSTRUCTION_LIMITATION", status="PROJECT_DERIVED",
            available="用户指定边界、Fig2图示和原事件重分箱",
            needed="严格作者边界复现仍需机器边界表或作者配置；当前保留重建标记",
            affects=["精确作者分箱声称"], claims=["C_PE"]),
        dict(id="G_RADIUS", item="2211半径nuisance与RESPONSE", kind="MODEL_DIFFERENCE", status="BLOCKED",
            available="原文5%约束及当前固定核结构",
            needed="有来源并经审核的RESPONSE半径变形映射，或明确固定半径的不同主张",
            affects=["严格2211七nuisance复现"], claims=["C_RADIUS"]),
        dict(id="G_QF", item="QF范围外贡献", kind="APPLICABILITY_LIMITATION", status="PARTIAL",
            available="2–70keVnr原始拟合域、当前域保护与旧低反冲延拓诊断",
            needed="完整ROOT高能尾的范围外响应及小反nu_e绝对源权重，若以后选择该完整源",
            affects=["完整ROOT源的全反冲预测"], claims=["C_QF_DOMAIN", "C_ROOT"]),
    ]
    formulas = [
        dict(id="F_SOURCE", section="source", latex=r"\eta=\frac{rN_{\rm POT}}{4\pi(100L)^2},\quad E_\pi=\frac{m_\pi^2-m_\mu^2}{2m_\pi}",
            sources=["S_2211"], locator="p12 Eq29与后续归一化段", inputs=["C_YIELD", "C_POT", "C_L", "C_MPI", "C_MMU"],
            symbols={"eta": "C_ETA", "r": "C_YIELD", "N_POT": "C_POT", "L": "C_L", "m_pi": "C_MPI", "m_mu": "C_MMU", "E_pi": "C_LINE"}),
        dict(id="F_DAR", section="source", latex=r"\phi_{\nu_\mu}(E)=\eta\delta(E-E_\pi),\quad\phi_{\nu_e}(E)=\eta\frac{192E^2}{m_\mu^3}\left(\frac12-\frac{E}{m_\mu}\right),\quad\phi_{\bar\nu_\mu}(E)=\eta\frac{64E^2}{m_\mu^3}\left(\frac34-\frac{E}{m_\mu}\right)",
            sources=["S_2211"], locator="p12 Eq29，0≤E≤m_mu/2", inputs=["C_COMPONENTS", "C_ETA", "C_MMU", "C_LINE", "C_ENDPOINT"],
            symbols={"E": "积分变量MeV，数值域见C_ENDPOINT", "phi": "由已列输入定义的每味谱，不另索取实验采样表", "m_mu": "C_MMU", "eta": "C_ETA"}),
        dict(id="F_NUCLEAR", section="nuclear", latex=r"W_{ab}^{X}(y)=e^{-2y}\sum_{k=0}^{K-1}c_{abk}^{X}y^k,\quad y=(qb/2)^2",
            sources=["S_LOCAL_W"], locator="meta.note、exp_factor及各responses系数；现有ResponseW求值规则", inputs=["C_RESOURCE_BINDING", "C_BASIC_Cs133", "C_BASIC_I127"],
            symbols={"c": "实际16个数组已取得，上游仍未核实", "q": "动量变量，现有调用使用GeV", "b": "核表basic.b已取得，原始单位待核", "X,a,b,k": "通道、(p,n)轴和升幂索引定义"}),
        dict(id="F_QF", section="detector", latex=r"E_{ee}[{\rm keVee}]=10^3\sum_{j=1}^{4}q_j\left(10^{-3}T[{\rm keVnr}]\right)^j,\quad \overline{\rm PE}=13.35\,E_{ee}",
            sources=["S_scintRespCoefficients", "S_SUP", "S_QF_PAPER"], locator="系数文件line1–7；Supplement p3 lines90–93；校准Eq8.1", inputs=["C_QF", "C_LY", "C_QF_DOMAIN"],
            symbols={"q_j": "C_QF", "T": "真实反冲变量keVnr，适用域C_QF_DOMAIN", "E_ee,PE_mean": "由该式定义的派生量"}),
        dict(id="F_GAMMA", section="detector", latex=r"G(x\mid E_{ee})=\frac{[a(1+b)]^{1+b}}{\Gamma(1+b)}x^b e^{-a(1+b)x},\quad a=0.0749/E_{ee},\quad b=9.56E_{ee}",
            sources=["S_SUP", "S_2211"], locator="Supplement p3 Eq3；2211 p12 Eq31", inputs=["C_GAMMA", "C_QF"],
            symbols={"x": "重建PE，x≥0", "a,b": "C_GAMMA", "E_ee": "keVee，来自F_QF", "Gamma": "Euler gamma数学函数"}),
        dict(id="F_EFF", section="detector", latex=r"\epsilon_E(x)=\max\left(0,\frac{a}{1+e^{-b(x-c)}}+d\right),\quad x={\rm PE}+\delta_{\rm PE}",
            sources=["S_effCoefficients", "S_2211", "S_LEGACY_EFF"], locator="系数文件头；2211 p12 Eq30；非负裁剪为现有实现约定", inputs=["C_EFF", "C_SHIFTS"],
            symbols={"a,b,c,d": "C_EFF", "delta_PE": "C_SHIFTS", "max(0,...)": "PROJECT_CONVENTION，避免低PE负效率，需审核"}),
        dict(id="F_TIME_EFF", section="detector", latex=r"\epsilon_T(t)=\begin{cases}1&t<0.52\,\mu{\rm s}\\e^{-0.0494(t-0.52)}&t\ge0.52\,\mu{\rm s}\end{cases}",
            sources=["S_SUP", "S_2211"], locator="Supplement p2 Eq1；2211 p13 Eq33", inputs=["C_TIME_EFF"],
            symbols={"t": "观测时间us，位移后效率留在此坐标", "0.52,0.0494": "C_TIME_EFF"}),
        dict(id="F_FOLD", section="prediction", latex=r"N_{ij}=\sum_{A,n}N_A\int_{\mathrm{PE}_i}^{\mathrm{PE}_{i+1}}dx\,\epsilon_E(x)\int dT\,G(x\mid T)\int dE\,\phi_n(E)\frac{d\sigma_{A,n}}{dT}\int_{t_j}^{t_{j+1}}dt\,f_n(t-\delta_t)\epsilon_T(t)",
            sources=["S_2211"], locator="p12 Eq28与p13 Eq32，以重建PE作变量的等价书写", inputs=["C_ETA", "C_QF", "C_GAMMA", "C_EFF", "C_PE", "C_TIME", "C_DENOM", "C_RESOURCE_BINDING"],
            symbols={"N_A": "按已选择的靶核数计算，质量源为C_MASS", "d_sigma/dT": "选定RESPONSE，直接资源C_RESOURCE_BINDING；外部作者链另记", "f_n": "C_TIME_MARGINAL与C_DENOM", "G,epsilon": "Detector已列输入", "x,T,E,t": "积分变量，单位分别PE,keVnr,MeV,us"}),
        dict(id="F_LIKELIHOOD", section="statistics", latex=r"\chi^2=2\sum_{ij}\left[\mu_{ij}-n_{ij}+n_{ij}\ln\frac{n_{ij}}{\mu_{ij}}\right]+\sum_k\left(\frac{\alpha_k}{\sigma_k}\right)^2",
            sources=["S_2202", "S_2211"], locator="2202 Eq6；2211 p14 Eq36，预测组成Eq38", inputs=["C_OBS", "C_SS", "C_PRIORS", "C_PULL_JHEP", "C_PULL_2211", "C_RADIUS", "C_BG_GAP"],
            symbols={"n_ij": "C_OBS，raw C counts", "mu_ij": "CEvNS+BRN+NIN+SS，BRN/NIN归一未闭合", "sigma_k": "两个benchmark各用自身宽度", "alpha_k": "nuisance变量；2211半径项与当前固定RESPONSE不同"}),
    ]
    report = dict(revision=REVISION, date="2026-11-06", status="DRAFT_LOCAL_RESPONSE_SELECTED_OTHER_GAPS_REMAIN",
        analysis_id="CsI2021_time_9x11", section_titles={"identity": "身份、目标与本轮补充", "source": "Source 数值与来源", "target": "Target 与曝光",
            "nuclear": "Nuclear RESPONSE 实际数据和上游缺口", "constants": "常数及单位来源", "detector": "Detector Response 与校准",
            "observable": "Observable、分箱与原始计数", "prediction": "Prediction folding 与旧诊断", "statistics": "Statistics 与独立benchmark"},
        formulas=formulas, issues=issues,
        changes=["按用户补充直接绑定原data/responses/responses_all.json；外部生成链不再阻断本次原表复用",
            "将旧P03中的Helm候选改为用户指定RESPONSE，并展开全部Cs/I数值数组",
            "取得作者固定提交的Elastic密度矩阵及Mu2e_NRET源码，保留未证实的转换对应",
            "将9份官方数值附件、校准原文、NIST/PDG原表并入主项目并给出页行定位",
            "显式列出14.57/14.6kg及−0.3333/−0.333322等旧诊断差异",
            "详细版、精简版、用户资料、P02和交接表从本套记录重生成"],
        handoff=[dict(capability="P04原有RESPONSE资源复用", state="LOCAL_RESOURCE_READY", required=["C_RESOURCE_BINDING", "C_W_Cs133_M", "C_W_I127_M"], next="通过ResponseDB直接加载原data核表，沿原基底/单位约定使用"),
            dict(capability="P06 nominal探测器响应准备", state="DRAFT_INPUTS_PRESENT", required=["C_QF", "C_QF_DOMAIN", "C_GAMMA", "C_EFF", "C_TIME_EFF"], next="按官方nominal系数核对实现，保留systematic标签冲突"),
            dict(capability="P07下一轮逐箱预测准备", state="INPUTS_PRESENT_CONFIG_REVIEW", required=["C_RESOURCE_BINDING", "C_SOURCE_CHOICE", "C_DENOM"], next="复用原核表和预测入口，以明确的14.6kg/官方效率及时间口径生成同条件结果"),
            dict(capability="P09论文统计", state="BLOCKED", required=["C_BG_GAP", "C_RADIUS"], next="闭合背景归一，分别声明固定半径诊断和完整论文nuisance"),
            dict(capability="P10外部benchmark", state="BLOCKED", required=["C_BG_GAP", "C_RADIUS"], next="分别验收用户选定RESPONSE诊断和原论文模型，闭合背景与配置差异")])
    write_json(RUN / "P00_SOURCE_REGISTER.yaml", dict(experiment_slug="COHERENT_CsI", dataset_id="CsI2021", analysis_id=report["analysis_id"], revision=REVISION, sources=sources))
    write_json(RUN / "P01_EVIDENCE_LEDGER.yaml", dict(sources=[], revision=REVISION, claims=claims))
    write_json(RUN / "P03_PHYSICS_CONTRACT.yaml", dict(contract_version=4, dataset_id="CsI2021",
        scientific_claim="DRAFT: time analysis directly reusing user-selected original data/RESPONSE resource; neutron normalization and paper-equivalence gaps remain",
        sections=sections, report_spec=report))
    from timing_diagnostics_records import apply
    apply()  # historical timing diagnostics remain explicitly labelled
    from restart_records import apply as apply_restart
    return apply_restart()  # r3 review state survives a full record rebuild


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    count_sources, count_claims = build_records()
    print(f"Wrote {REVISION} draft with {count_sources} sources and {count_claims} claims")
