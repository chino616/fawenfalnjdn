"""Render the same P00/P01/P03 into the CsI time provenance review documents."""
from pathlib import Path
import argparse
import hashlib
import json
import os

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[5]
DOC = ROOT / "docs/experiments/COHERENT/CsI2021/time_resolved"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_link(label, target, current):
    target = Path(target)
    path = os.path.relpath(target, current.parent).replace("\\", "/").replace("%", "%25")
    return f"[{label}](<{path}>)"


def safe(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def value_text(claim):
    value = claim["value"]
    if value is None:
        return "**MISSING**"
    if claim["claim_id"].startswith("C_W_") and isinstance(value, dict):
        return ("shape=" + str(value["shape"]) + ", k=" + str(value["power_range"]) +
                "; c_pp[0:3]=" + str(value["first_three_coefficients"][0][0]))
    if claim["claim_id"] == "C_ROOT":
        return "4个TH2F，每个[15000 time,600 energy]；完整轴域与代表值见下表"
    if claim["claim_id"] in ["C_OBS", "C_CONTROL"]:
        return "9×11，全部数值见详细版Observable矩阵及完整数据文件；sum=" + str(sum(map(sum, value)))
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))
    return str(value)


def resource_link(claim, current):
    resource = claim.get("numerical_resource")
    if not resource:
        return "标量或定义，见直接出处"
    result = local_link(Path(resource["path"]).name, ROOT / resource["path"], current)
    if resource.get("review_npz"):
        result += " · " + local_link("逐值提取供核对", ROOT / resource["review_npz"], current)
    if claim["claim_id"] in ["C_OBS", "C_CONTROL"]:
        result += " · " + local_link("完整99箱观测CSV", RUN / "data/observed_99bins.csv", current)
    for key in ["json_key", "key", "keys", "columns", "shape"]:
        if key in resource:
            result += " " + key + "=" + str(resource[key])
    return result


def citation_links(source_ids, sources, current):
    return " · ".join(local_link(identifier, ROOT / sources[identifier]["uri_or_path"], current)
                      for identifier in source_ids)


def references(source_ids, sources, current, heading_level=3):
    result = "\n" + "#" * heading_level + " 本章标准来源及核验范围\n\n"
    for identifier in sorted(set(source_ids)):
        source = sources[identifier]
        result += "- " + local_link(identifier, ROOT / source["uri_or_path"], current) + " "
        result += source["citation"] + " " + source["verification_scope"] + "。"
        if source.get("original_url"):
            result += " [原始网址](" + source["original_url"] + ")"
        result += "\n"
    return result


def verification_text(checks):
    labels = {
        ("numerical_data", "PRESENT"): "数值资源已取得",
        ("direct_material", "READ"): "直接材料已读",
        ("direct_material", "READ_EXACT_COPY"): "原表逐值回读",
        ("upstream", "SEE_P00"): "上游核验见P00",
        ("upstream", "UNVERIFIED_OPTIONAL_AUDIT"): "外部上游待核（可选）",
        ("applicability", "DRAFT"): "适用性待审",
        ("applicability", "USER_SELECTED_LOCAL_REUSE"): "本次原表复用已选",
        ("original_source", "LOCAL_DATA_RESOURCE"): "直接来源为本地原data",
        ("external_upstream", "UNVERIFIED_OPTIONAL_AUDIT"): "外部上游待核（可选）",
        ("local_extraction", "EXACT_EQUALITY"): "提取值完全一致",
    }
    return "；".join(labels.get((key, value), key + "=" + str(value)) for key, value in checks.items())


def input_table(selected, sources, current):
    body = "| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |\n"
    body += "|---|---|---|---|---|---|\n"
    for claim in selected:
        statuses = {"SOURCE_EXTRACTED": "来源已提取", "PROJECT_DERIVED": "项目推导",
            "USER_CONFIRMED": "用户已确认", "MISSING": "MISSING", "CONFLICT": "存在差异", "REFERENCE_ONLY": "仅参考"}
        adoptions = {"ADOPTED_DRAFT": "本稿候选", "ADOPTED_LOCAL_RESOURCE_BY_USER": "用户选定本地资源",
            "CANDIDATE_UPSTREAM": "候选上游", "LEGACY_DIAGNOSTIC": "旧诊断",
            "OPTIONAL_EXTERNAL_AUDIT": "可选外部审计", "PAPER_REFERENCE": "论文参考"}
        details = claim["verification_scope"] + "；" + verification_text(claim["verification_checks"])
        if claim["input_claims"]:
            details += " 输入=" + ",".join(claim["input_claims"])
        row = [claim["field"] + " `" + claim["claim_id"] + "` " + statuses[claim["status"]] + "；" + adoptions[claim["adoption"]],
               value_text(claim), claim["unit"], resource_link(claim, current),
               citation_links(claim["source_ids"], sources, current) + " " + claim["locator"], details]
        body += "| " + " | ".join(map(safe, row)) + " |\n"
    return body


def formula_block(formula, claims, sources, current, number):
    result = "\n" + citation_links(formula["sources"], sources, current) + " " + formula["locator"] + "。\n\n"
    result += "$$\n" + formula["latex"] + r" \tag{" + str(number) + "}\n$$\n\n"
    result += "| 符号 | 数值取得情况 | 数据、数值或定义及出处 |\n|---|---|---|\n"
    for symbol, identifier in formula["symbols"].items():
        if identifier in claims:
            claim = claims[identifier]
            value = safe(value_text(claim)) + " " + safe(claim["unit"])
            location = citation_links(claim["source_ids"], sources, current) + " " + claim["locator"]
            result += f"| {safe(symbol)} | {claim['status']} | {value}；{safe(location)} |\n"
        else:
            result += f"| {safe(symbol)} | 定义或明确限制 | {safe(identifier)} |\n"
    return result


def extra_data(section, claims):
    result = ""
    if section == "source":
        result += "\n| ROOT分量 | shape和完整轴域 | 实际最大权重箱(index,value) | 0–6us分数 |\n|---|---|---|---|\n"
        for row in claims["C_ROOT"]["value"]:
            result += f"| {row['component']} | {row['shape']}；time0–15000ns，energy0–600MeV | {row['representative_cell']} | {row['reference_0_6_us_fraction']:.12g} |\n"
        result += "\n上述数值从S_snsFlux2D各TH2F读取/求和，算法与单位换算登记为C_ROOT及C_TIME_MARGINAL。\n"
    if section == "nuclear":
        result += "\n按用户补充，本次直接调用原data/responses/responses_all.json，资源绑定见C_RESOURCE_BINDING。现有数值和原读取器约定已取得。作者上游与当前表的等价关系尚未证实，属于可选外部审计。S_ELASTIC_CS/S_ELASTIC_I仍只列候选上游，C_W_CONVERSION的MISSING仅限制外部来源认证。\n"
        for key in ["C_W_Cs133_M", "C_W_I127_M"]:
            value = claims[key]["value"]
            matrix = [[values[0] for values in row] for row in value["first_three_coefficients"]]
            result += "\n" + value["nucleus"] + " M(0)实际矩阵，来源为该通道本地JSON的k=0系数。\n\n"
            result += "|  | p列 | n列 |\n|---|---:|---:|\n"
            for label, row in zip(["p行", "n行"], matrix):
                result += f"| {label} | {row[0]:.15g} | {row[1]:.15g} |\n"
        result += "\n零动量残差用于诊断现表；本次沿用原读取器的归一化约定，外部作者归一化对应仍未核实。接近Z²/N²不能认证外部来源。\n"
    if section == "observable":
        for key in ["C_OBS", "C_CONTROL"]:
            claim = claims[key]
            result += "\n### " + claim["field"] + "全部99箱\n\n"
            result += "数值来自" + claim["claim_id"] + "的官方逐事件文件重分箱，端点和坐标见C_PE/C_TIME/C_ENDPOINT_RULE。\n\n"
            result += "| PE范围 | " + " | ".join(str(i) for i in range(11)) + " |\n"
            result += "|---|" + "---:|" * 11 + "\n"
            pe = claims["C_PE"]["value"]
            for index, row in enumerate(claim["value"]):
                result += "| [" + str(pe[index]) + "," + str(pe[index+1]) + ") | "
                result += " | ".join(map(str, row)) + " |\n"
            result += "\n列索引0–10依次对应C_TIME给出的十一时间窗，事件数单位为events/bin。\n"
    return result


def handoff(spec, claims, sources, current):
    body = "| 下一步能力 | 当前状态 | 必需输入与出处 | 实际下一步 |\n|---|---|---|---|\n"
    for row in spec["handoff"]:
        inputs = []
        for identifier in row["required"]:
            claim = claims[identifier]
            inputs.append(identifier + " " + claim["status"] + " " + citation_links(claim["source_ids"], sources, current))
        body += "| " + " | ".join(map(safe, [row["capability"], row["state"], "; ".join(inputs), row["next"]])) + " |\n"
    return body


def gap_table(spec):
    body = "| 问题 | 已有数据 | 尚缺数据/溯源 | 影响及当前状态 |\n|---|---|---|---|\n"
    for issue in spec["issues"]:
        body += "| " + " | ".join(map(safe, [issue["id"] + " " + issue["item"], issue["available"], issue["needed"],
            issue["status"] + "；" + ",".join(issue["affects"])])) + " |\n"
    return body


def render():
    p00 = read(RUN / "P00_SOURCE_REGISTER.yaml")
    ledger = read(RUN / "P01_EVIDENCE_LEDGER.yaml")
    contract = read(RUN / "P03_PHYSICS_CONTRACT.yaml")
    sources = {source["source_id"]: source for source in p00["sources"]}
    claims = {claim["claim_id"]: claim for claim in ledger["claims"]}
    spec = contract["report_spec"]
    for source in sources.values():
        path = ROOT / source["uri_or_path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Missing or changed source " + source["source_id"])
    docs = {}
    for name in ["experiment.physics.md", "experiment.physics.summary.md", "EXPERIMENT_USER_INPUT.md"]:
        current = DOC / name
        navigation = " · ".join(local_link(label, target, current) for label, target in [
            ("详细版", DOC / "experiment.physics.md"), ("精简版", DOC / "experiment.physics.summary.md"),
            ("用户资料", DOC / "EXPERIMENT_USER_INPUT.md"), ("来源P00", RUN / "P00_SOURCE_REGISTER.yaml"),
            ("证据P01", RUN / "P01_EVIDENCE_LEDGER.yaml"), ("缺失P02", RUN / "P02_MISSING_AND_CONFLICTS.md"),
            ("配置P03", RUN / "P03_PHYSICS_CONTRACT.yaml"),
            ("Benchmark旧诊断与范围", RUN / "evidence/legacy_resolution/README.md"),
            ("完整数据与生成入口", RUN / "README.md")])
        body = "# CsI2021 时间分辨分析 " + ("详细溯源草稿" if name == "experiment.physics.md" else
            "精简溯源草稿" if name == "experiment.physics.summary.md" else "用户资料与补充记录") + "\n\n"
        body += navigation + "\n\n**修订草稿" + spec["revision"] + "，" + spec["date"] + "，DRAFT/PARTIAL。** 已取得官方事件、背景、ROOT、校准系数及原data中的Cs/I核响应。用户已明确选择直接调用原核表，本次资源复用输入就绪。外部作者生成链仅作未核实的补充事项。BRN/NIN绝对归一及严格论文配置等价仍待补，外部benchmark继续BLOCKED。\n\n"
        if name == "experiment.physics.md":
            body += '<a id="report-toc"></a>\n\n## 目录\n\n'
            for key, title in spec["section_titles"].items():
                body += f"- [{title}](#{key})\n"
            body += "- [缺口与下一步交接](#handoff)\n\n"
            for section, title in spec["section_titles"].items():
                body += f'<a id="{section}"></a>\n\n## {title}\n\n'
                selected = [claims[key] for key in contract["sections"][section]["fields"]]
                if section == "identity":
                    body += "本轮补充记录由同一P00/P01/P03生成。旧隔离候选版本保存在修订归档。\n\n"
                    body += "\n".join("- " + text for text in spec["changes"]) + "\n\n"
                body += input_table(selected, sources, current)
                body += extra_data(section, claims)
                for number, formula in enumerate(spec["formulas"], 1):
                    if formula["section"] == section:
                        body += formula_block(formula, claims, sources, current, number)
                ids = [source_id for claim in selected for source_id in claim["source_ids"]]
                ids.extend(source_id for formula in spec["formulas"] if formula["section"] == section for source_id in formula["sources"])
                body += references(ids, sources, current)
                body += "\n[返回目录](#report-toc)\n\n"
            body += '<a id="handoff"></a>\n\n## 缺口与下一步交接\n\n' + gap_table(spec) + "\n" + handoff(spec, claims, sources, current)
            body += "\n原文核查记录与机器文件检查分别保留。数值存在、来源闭合、转换等价和物理适用性的接受各自有据，程序可运行不能替代它们。\n\n[返回目录](#report-toc)\n"
        else:
            user_input = name == "EXPERIMENT_USER_INPUT.md"
            back = "\n[返回目录](#report-toc)\n\n" if user_input else "\n"
            if user_input:
                body += '<a id="report-toc"></a>\n\n## 目录\n\n'
                for key, title in [
                    ("input-target", "H0 目标与已记录选择"),
                    ("input-materials", "H1 已取得材料与本轮新增"),
                    ("input-values", "H2 实际数值及来源"),
                    ("input-gaps", "来源缺口与影响"),
                    ("input-qa", "H3 补充问答与当前处理"),
                    ("input-handoff", "下一步输入交接"),
                    ("input-sources", "标准来源及核验范围"),
                ]:
                    body += f"- [{title}](#{key})\n"
                body += '\n<a id="input-target"></a>\n\n## H0 目标与已记录选择\n\nCsI2021_time_9x11，使用用户指定RESPONSE，保留两套独立benchmark。用户选项登记在DECISION_LOG，核响应外部来源另行审核。\n'
                body += back + '<a id="input-materials"></a>\n\n## H1 已取得材料与本轮新增\n\n' + "\n".join("- " + text for text in spec["changes"]) + "\n"
                body += back + '<a id="input-values"></a>\n\n## H2 实际数值及来源\n\n'
            selected_ids = ["C_POT", "C_YIELD", "C_L", "C_MASS", "C_RESOURCE_BINDING", "C_W_Cs133_M", "C_W_I127_M", "C_W_CONVERSION",
                "C_QF", "C_QF_DOMAIN", "C_EFF", "C_EFF_LEGACY", "C_PE", "C_TIME", "C_OBS", "C_CONTROL", "C_BG_GAP"]
            body += input_table([claims[key] for key in selected_ids], sources, current)
            body += back + ('<a id="input-gaps"></a>\n\n' if user_input else "")
            body += "## 来源缺口与影响\n\n" + gap_table(spec)
            if user_input:
                body += back + '<a id="input-qa"></a>\n\n## H3 补充问答与当前处理\n\n询问了原始导出脚本或作者数据包位置后，用户明确答复“response本来就可以直接去调用原始的 data中的response”。已回填DECISION_LOG的D_LOCAL_RESPONSE，更新P00/P01/P03并重新生成本版。当前核表按原data直接调用，提取NPZ仅供阅读核验。作者公开密度矩阵和源码保留为可选上游材料，尚未证实的外部对应关系继续如实标注。\n'
            body += back + ('<a id="input-handoff"></a>\n\n' if user_input else "")
            body += "## 下一步输入交接\n\n" + handoff(spec, claims, sources, current)
            body += back + ('<a id="input-sources"></a>\n' if user_input else "")
            body += references([source_id for key in selected_ids for source_id in claims[key]["source_ids"]], sources, current, heading_level=2)
            body += back
        from timing_diagnostics_records import render_note
        body += "\n" + render_note(current)
        from restart_records import render_note as render_restart
        body += "\n" + render_restart(current)
        docs[current] = body
    missing = "# P02 CsI2021时间分析缺失与冲突\n\n修订草稿" + spec["revision"] + "，" + spec["date"] + "。对应同一P00/P01/P03。原data核表复用已获用户选择，外部作者生成链不作为本次复用阻断。\n\n" + gap_table(spec)
    missing += "\n" + handoff(spec, claims, sources, RUN / "P02_MISSING_AND_CONFLICTS.md")
    missing += "\n" + render_note(RUN / "P02_MISSING_AND_CONFLICTS.md")
    missing += "\n" + render_restart(RUN / "P02_MISSING_AND_CONFLICTS.md")
    docs[RUN / "P02_MISSING_AND_CONFLICTS.md"] = missing
    return docs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    reports = render()
    for path, body in reports.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != body:
                raise SystemExit("STALE " + str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8", newline="\n")
        print(("PASS " if args.check else "WROTE ") + str(path))


if __name__ == "__main__":
    main()
