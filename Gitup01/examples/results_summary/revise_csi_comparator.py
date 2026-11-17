"""Trace and publish the CsI2021 SM-total comparator correction, without fits.

Use bundled Python for --evidence / --collection and scientific Python for
--table. Existing selected files must already be backed up in the revision plan.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "论文图NoteBook/8. SM_experiment_benchmarks"
RUN = ROOT / "outputs/results_summary_20261115_run2"
PAPER = ROOT / "docs/references/COHERENT/2110.07730v2.pdf"
EVIDENCE = FIG / "CSI2021_COMPARATOR_EVIDENCE.json"
LOCATOR = ("D. Akimov et al. (COHERENT), PRL 129, 081801 (2022), "
           "arXiv:2110.07730v2, PDF/printed p.4, right column, Results, first paragraph; "
           "SM 341 +/- 11(theory) +/- 42(experiment) events; fitted CEvNS 306 +/- 20 events")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def write(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def prepare_evidence():
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    if EVIDENCE.exists(): raise FileExistsError("Evidence already exists; revise explicitly rather than silently replacing it")
    pdf = PdfReader(PAPER)
    text = pdf.pages[3].extract_text()
    plain = re.sub(r"\s+", " ", text)
    for phrase in [r"observed\s+306", r"341\s*±\s*11", r"42\s*\(experiment\)", r"PE\s*<\s*60", r"6\s*µs", r"without any prior constraint"]:
        if not re.search(phrase, plain): raise ValueError("Primary-page evidence not found: " + phrase)
    source = {"citation": "D. Akimov et al. (COHERENT), Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT, Phys. Rev. Lett. 129, 081801 (2022)",
              "doi": "10.1103/PhysRevLett.129.081801", "arxiv": "2110.07730v2", "pdf": str(PAPER),
              "pdf_sha256": sha(PAPER), "pdf_page_1based": 4, "printed_page": 4, "column": "right", "heading": "Results", "paragraph": 1,
              "locator": LOCATOR, "url": "https://arxiv.org/pdf/2110.07730v2#page=4"}
    quote = "After fitting, we observed 306 ± 20 CEvNS events, consistent with the SM prediction of 341 ± 11(theory) ± 42(experiment)."
    record = {"schema": "cevns_csi2021_comparator_evidence/1", "date": "2026-11-15", "user_annotation": 1,
              "source": source, "quotation": quote,
              "published_SM": {"central_events": 341., "uncertainty_theory_events": 11., "uncertainty_experiment_events": 42., "role": "published SM total prediction, not a fitted yield"},
              "published_fitted_signal": {"central_events": 306., "uncertainty_events": 20., "role": "signal extracted from the experimental PE-time fit; not the SM comparator"},
              "paper_selection": {"PE_upper_exclusive": 60., "t_rec_upper_exclusive_us": 6., "likelihood": "binned PE and t_rec likelihood; normalization and shape nuisance profiled", "timing_onset": "floated without prior constraint", "figure1": "best-fit residual spectra over steady-state background; not nominal SM templates"},
              "local_nominal_SM": {"events": 353.46560868634367, "observable_shape": [9, 11], "PE_range": [0., 60.], "t_rec_range_us": [0., 6.], "timing_onset_us": 0., "fluence_convention": "zero-shift 0-6 us reference-window normalization", "direct_result": "outputs/csi2021_time_sm_20261107/RUN_SUMMARY.json"},
              "comparison": {"absolute_difference_events": 353.46560868634367 - 341., "relative_difference": 353.46560868634367 / 341. - 1.,
                             "meaning": "central total-rate benchmark only; not a reproduction error, significance, chi-square, or coverage check", "uncertainty_combination": "theory and experiment errors retained separately; no assumed combination/covariance", "author_aligned_99bin_SM_template": "NOT_ACQUIRED_OR_ALIGNED", "input_and_normalization_equivalence": "NOT_ESTABLISHED", "integrations_this_revision": 0, "fits_this_revision": 0}}
    write(EVIDENCE, record)
    text_md = """# CsI2021时间分析：Comparator直接依据

本页修正原汇总表将Comparator留空的遗漏。**有论文SM总率参考；尚未取得/对齐的是作者99箱SM数值模板。** 本次仅补文献对照，不改本地预测或统计模型。

## 标准引文与准确定位

D. Akimov et al. (COHERENT), *Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT*, **Phys. Rev. Lett. 129, 081801 (2022)**, DOI: [10.1103/PhysRevLett.129.081801](https://doi.org/10.1103/PhysRevLett.129.081801), [arXiv:2110.07730v2](https://arxiv.org/abs/2110.07730v2)。

**PDF第4页（页脚同为4）、右栏“Results”第一段**：[原文直达页](https://arxiv.org/pdf/2110.07730v2#page=4) · [项目内原始PDF](<../../docs/references/COHERENT/2110.07730v2.pdf>)。本地PDF的SHA256及逐字段记录见[机器证据](CSI2021_COMPARATOR_EVIDENCE.json)。

原句（仅数学空格作可读排版）：

> After fitting, we observed 306 ± 20 CEvNS events, consistent with the SM prediction of 341 ± 11(theory) ± 42(experiment).

## 数值的不同角色

| 数量 | 数值 / events | 对照中的角色 |
|---|---:|---|
| 本地名义SM | 353.46560868634367 | 已存、未拟合的9 PE×11时间箱信号 |
| 论文SM预期 | **341 ± 11（theory）± 42（experiment）** | 汇总表的SM总率Comparator；两项不确定度分开保留 |
| 实验拟合信号 | 306 ± 20 | 从实验PE–时间likelihood提取的信号；单独列出，不替代SM Comparator |
| 作者同定义99箱SM模板 | 尚未取得或对齐 | 不能用341这一总数替代逐箱谱形及原生χ²验收 |

总率中心值差为 **+12.4656086863 events，即+3.6556037203%**。这是本地值相对论文SM中心值的算术比较，不能称为同输入复现误差、统计显著性或χ²检验。不把11和42自动合成一个误差。

## 选窗与适用范围

同页左栏拟合说明采用 **PE<60、t_rec<6 μs**，在PE与重建时间上做分箱likelihood，profile归一化及形状nuisance；时间起点允许无先验浮动。同页Fig.1图注写明曲线为相对稳态背景的**最佳拟合**CEvNS、BRN和NIN预测。

本地选定运行采用PE∈[0,60)、t_rec∈[0,6) μs、固定零平移和0–6 μs参考窗注量归一化。外层上界一致，并不认证时间起点、核响应、响应折叠、曝光/源归一化和nuisance处理全部相同。因此本次只建立**可追查的论文SM总率benchmark**；原99箱模板等价性、BRN/NIN归一化和P09统计缺口继续保留。

[论文总表](Table_SM_Numerical_Summary.pdf) · [CSV](Table_SM_Numerical_Summary.csv) · [参考文献与方法](REFERENCES_AND_METHODS.md) · [图集目录](README.md)
"""
    (FIG / "CSI2021_COMPARATOR_EVIDENCE.md").write_text(text_md, encoding="utf-8")
    (RUN / "qa/primary_page4.txt").write_text(text, encoding="utf-8")
    doc = pdfium.PdfDocument(str(PAPER))
    doc[3].render(scale=1.5).to_pil().save(RUN / "qa/primary_page4.png")
    print(json.dumps({"evidence": str(EVIDENCE), "paper_sha256": source["pdf_sha256"], "page": 4}, ensure_ascii=False))


def publish_table():
    import numpy as np
    spec = importlib.util.spec_from_file_location("sm_paper_figures", ROOT / "论文图NoteBook/generate_sm_experiment_figures.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    data = {}
    for key in gen.SETS:
        with np.load(FIG / "inputs" / (key + ".npz"), allow_pickle=False) as z: data[key] = {k: z[k].copy() for k in z.files}
    class NoCollection:
        def savefig(self, *args, **kwargs): pass
    gen.style()
    gen.draw_table(data, FIG, NoCollection())
    evidence = read(EVIDENCE)
    metadata = read(FIG / "inputs/metadata.json")
    ref = next(r for r in metadata["references"] if r["id"] == "R4")
    ref["locator"] = LOCATOR
    metadata["csi2021_comparator_revision"] = {"date": "2026-11-15", "evidence": "CSI2021_COMPARATOR_EVIDENCE.json", "scope": "published SM scalar comparator; no arrays or fits changed"}
    for p, role in [(EVIDENCE, "verified primary-page scalar comparator and distinct fitted yield"), (ROOT / "论文图NoteBook/generate_sm_experiment_figures.py", "current plot/table exporter")]:
        metadata["source_files"][p.relative_to(ROOT).as_posix()] = {"path": str(p), "sha256": sha(p), "role": role}
    write(FIG / "inputs/metadata.json", metadata)
    write(FIG / "SOURCE_MANIFEST.json", metadata["source_files"])
    val = read(FIG / "VALIDATION.json")
    val["SM_summary"] = gen.summary_rows(data)
    val["csi2021_comparator_revision"] = {"date": "2026-11-15", "paper_locator": LOCATOR, "paper_sha256": evidence["source"]["pdf_sha256"], "reference_SM_events": 341., "reference_theory_error_events": 11., "reference_experiment_error_events": 42., "measured_signal_events": 306., "measured_signal_error_events": 20., "integrations": 0, "fits": 0, "revision_QA": "../../outputs/results_summary_20261115_run2/qa/COMPARATOR_REVISION_CHECKS.json"}
    val["source_files"] = len(metadata["source_files"])
    val["generator"] = {"path": str(ROOT / "论文图NoteBook/generate_sm_experiment_figures.py"), "sha256": sha(ROOT / "论文图NoteBook/generate_sm_experiment_figures.py")}
    write(FIG / "VALIDATION.json", val)
    print("Updated only the SM summary table and its scalar-comparator metadata")


def replace_collection():
    from pypdf import PdfReader, PdfWriter
    import pypdfium2 as pdfium
    collection = FIG / "SM_Benchmarks_Collection.pdf"
    reader = PdfReader(io.BytesIO(collection.read_bytes()))
    replacement = PdfReader(io.BytesIO((FIG / "Table_SM_Numerical_Summary.pdf").read_bytes()))
    if "SM numerical summary" not in reader.pages[-1].extract_text(): raise ValueError("Last collection page is not the expected summary table")
    before = [p.get_contents().get_data() for p in reader.pages[:-1]]
    writer = PdfWriter()
    for p in reader.pages[:-1]: writer.add_page(p)
    writer.add_page(replacement.pages[0])
    writer.add_metadata({"/Title": "SM benchmarks; CsI2021 scalar comparator corrected", "/Subject": "2110.07730v2 p4 Results; numerical predictions unchanged"})
    tmp = RUN / "qa/collection_revision.tmp.pdf"
    with tmp.open("wb") as f: writer.write(f)
    revised = PdfReader(tmp)
    assert len(revised.pages) == len(reader.pages)
    assert before == [p.get_contents().get_data() for p in revised.pages[:-1]]
    assert "341" in revised.pages[-1].extract_text()
    revised_collection = FIG / "SM_Benchmarks_Collection_20261115_comparator.pdf"
    revised_collection.write_bytes(tmp.read_bytes())
    tmp.unlink()
    doc = pdfium.PdfDocument(str(FIG / "Table_SM_Numerical_Summary.pdf"))
    doc[0].render(scale=2.2).to_pil().save(RUN / "qa/table_pdf_render.png")
    document = pdfium.PdfDocument(str(revised_collection))
    document[len(document) - 1].render(scale=2).to_pil().save(RUN / "qa/collection_last_page.png")
    write(RUN / "qa/PDF_REVISION_CHECKS.json", {"status": "PASS_NON_TABLE_PAGE_CONTENT_PRESERVED", "collection_pages": len(reader.pages), "unchanged_content_stream_pages": len(before), "table_page_contains_341": True, "visual_review": "PENDING", "fits": 0, "integrations": 0, "original_collection": str(collection), "revised_collection": str(revised_collection), "filename_reason": "Original collection denied write access; publish an explicitly named revision and keep the original intact."})
    print(json.dumps({"pages": len(reader.pages), "unchanged_pages": len(before), "table_render": str(RUN / "qa/table_pdf_render.png")}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["evidence", "table", "collection"])
    args = parser.parse_args()
    {"evidence": prepare_evidence, "table": publish_table, "collection": replace_collection}[args.action]()
