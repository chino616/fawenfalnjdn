"""Read-only scientific checks and rendered PDF QA for the 20261114 delivery.

Run with a Python containing pypdf, pypdfium2, pdfplumber and Pillow. Only QA
images/records under the named baseline directory are written; no fit is run.
"""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote

import pdfplumber
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/"outputs/cutoff_scales/20261114_comparison_joint_baseline"
FIG_ROOT = ROOT/"论文图NoteBook/12. Cutoff_Scale_Benchmarks"
RUNS = ("20261114_dim6_role_style_run1", "20261114_full22_role_style_run1", "20261114_comparison_joint_run1")
JOINT = ROOT/"outputs/cutoff_scales/20261114_three_group_joint_run1"
COMPARISON = ROOT/"outputs/cutoff_scales/20261114_paper_comparison_run1"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equal(a,b):
    assert math.isclose(float(a),float(b),rel_tol=2e-12,abs_tol=2e-10),(a,b)


def verify():
    qa = BASE/"qa"
    qa.mkdir(exist_ok=True)
    baseline=read(BASE/"BASELINE.json")
    changes=[p for p,h in baseline["protected"].items() if sha(ROOT/p)!=h]
    assert not changes,changes
    manifests=[]
    for run,path in [(r,FIG_ROOT/r/"FIGURE_MANIFEST.json") for r in RUNS]+[("joint",JOINT/"RESULTS.json"),("comparison",COMPARISON/"COMPARISON.json")]:
        record=read(path)
        for p,h in record["source_manifest"].items():
            assert sha(ROOT/p)==h,(run,p)
        for p,h in record.get("outputs",{}).items():
            assert sha(path.parent/p)==h,(run,p)
        manifests.append({"run":run,"sources_checked":len(record["source_manifest"]),"outputs_checked":len(record.get("outputs",{}))})
    record=read(COMPARISON/"COMPARISON.json")
    for row in record["rows"]:
        a,b=row["local_90CL_GeV"],row["paper_fig3_90CL_GeV"]
        equal(a/b,row["ratio_local_over_paper"])
        equal(a-b,row["difference_GeV"])
        equal(100*(a/b-1),row["relative_difference_percent"])
    table_rows=0
    for folder in RUNS[:2]:
        rel="outputs/cutoff_scales/"+("20261114_dim6_run1" if "dim6" in folder else "20261114_full22_control_run1")
        original=read(ROOT/rel/"RESULTS.json")
        idx={(r["analysis_group"],f"O{r['operator_key'][0]}{r['operator_key'][2]}_{r['operator_key'][1]}"):r for r in original["results"]}
        for path in (FIG_ROOT/folder/"plot_data").glob("*.csv"):
            for row in csv.DictReader(path.open(encoding="utf-8")):
                r=idx.get((row["group"],row["operator"]))
                if r is None:
                    assert row["status"]=="NOT_IN_THIS_VERSION" and not row["global_GeV"]
                else:
                    value=r["confidence"][row["CL"]].get("global_GeV")
                    if value is None:assert not row["global_GeV"]
                    else:equal(value,row["global_GeV"])
                table_rows+=1
    joint=read(JOINT/"RESULTS.json")
    ids={r["operator_key"][2]:r for r in joint["results"] if r["version"]=="dim6_self_consistent"}
    curve_rows=0
    for row in csv.DictReader((FIG_ROOT/RUNS[2]/"plot_data/08_DIM6_Joint_Chi2.csv").open(encoding="utf-8")):
        r=ids[row["operator"]]
        total=sum(float(row[k]) for k in ("CONUS_chi2","COHERENT_chi2","solar_chi2"))
        equal(total-r["chi2_min"],row["joint_delta_chi2"])
        equal(float(row["normalized_x"])*r["coefficient_scale"],row["coefficient"])
        curve_rows+=1
    palette=read(ROOT/"论文图NoteBook/9. SM_uniform_style/STYLE.json")["colors"]
    svg=(FIG_ROOT/RUNS[2]/"02_Full22_CONUS_vs_Paper.svg").read_text(encoding="utf-8")
    assert palette["work_SM"].lower() in svg.lower() and palette["reference"].lower() in svg.lower()
    svg=(FIG_ROOT/RUNS[2]/"07_DIM6_Joint_Bounds.svg").read_text(encoding="utf-8")
    assert palette["work_SM"].lower() in svg.lower() and palette["control_or_total"].lower() in svg.lower()
    pdfchecks, contacts, rendered = [], [], 0
    for run in RUNS:
        folder=FIG_ROOT/run
        for path in sorted(folder.glob("*.pdf")):
            reader=PdfReader(path)
            for page in reader.pages:
                equal(float(page.mediabox.width),180/25.4*72)
            with pdfplumber.open(path) as pdf:
                for i,page in enumerate(pdf.pages):
                    outside=[c for c in page.chars if c["text"].strip() and (c["x0"] < -1 or c["x1"]>page.width+1 or c["top"] < -1 or c["bottom"]>page.height+1)]
                    assert not outside,(path.name,i,outside[:3])
            pdfchecks.append({"path":path.relative_to(ROOT).as_posix(),"pages":len(reader.pages),"width_mm":180,"no_outside_page_characters":True})
        collection=pdfium.PdfDocument(folder/"Cutoff_Comparison_Collection.pdf")
        thumbs=[]
        for i in range(len(collection)):
            page=collection[i]
            bitmap=page.render(scale=1.7)
            im=bitmap.to_pil().convert("RGB")
            im.save(qa/f"{run}_page{i+1:02d}.png")
            im.thumbnail((610,800))
            tile=Image.new("RGB",(630,835),"#eef1f3")
            tile.paste(im,((630-im.width)//2,25))
            ImageDraw.Draw(tile).text((12,7),f"{run} / page {i+1}",fill="black")
            thumbs.append(tile)
            rendered+=1
        contact=Image.new("RGB",(1260,835*math.ceil(len(thumbs)/2)),"white")
        for i,im in enumerate(thumbs):contact.paste(im,((i%2)*630,(i//2)*835))
        target=qa/(run+"_contact.png")
        contact.save(target)
        contacts.append(target.relative_to(ROOT).as_posix())
    report={"stage":"AUTOMATIC_CHECKS_AND_PDF_RENDER_COMPLETE_VISUAL_REVIEW_SEPARATE",
            "protected_count":len(baseline["protected"]),"protected_changes":changes,
            "manifest_checks":manifests,"comparison_rows_recomputed":len(record["rows"]),
            "replot_values_checked":table_rows,"joint_curve_rows_checked":curve_rows,
            "palette_source":"论文图NoteBook/9. SM_uniform_style/STYLE.json",
            "pdf_files":pdfchecks,"rendered_collection_pages":rendered,"contacts":contacts}
    # Repository's normal link CLI deliberately excludes outputs; audit only
    # these explicit newly owned/edited output documents with its same parser.
    spec=importlib.util.spec_from_file_location("cutoff_doc_links",ROOT/"tools/validate_docs.py")
    links_module=importlib.util.module_from_spec(spec); spec.loader.exec_module(links_module)
    documents=[ROOT/"outputs/README.md",ROOT/"outputs/cutoff_scales/README.md",
               JOINT/"README.md",COMPARISON/"README.md",BASE/"README.md",BASE/"CHANGE_RECORD.md"]
    link_checks=[]
    for document in documents:
        for line,raw in links_module.link_targets(document.read_text(encoding="utf-8-sig")):
            value=raw.strip().strip("<>")
            if re.match(r"^(https?:|mailto:|data:|#)",value):continue
            target=(document.parent/unquote(value.split("#",1)[0])).resolve()
            assert target.exists(),(document,line,raw)
            link_checks.append({"file":document.relative_to(ROOT).as_posix(),"line":line,"target":raw,"status":"PASS"})
    report["explicit_output_documents_checked"]=len(documents)
    report["explicit_output_links_checked"]=len(link_checks)
    (BASE/"OUTPUT_LINKS.json").write_text(json.dumps(link_checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (BASE/"DELIVERY_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("VERIFIED",len(baseline["protected"]),"protected;",len(record["rows"]),"comparison rows;",table_rows,"bars;",curve_rows,"curve rows;",len(pdfchecks),"PDFs; rendered",rendered,"pages")


if __name__=="__main__":verify()
