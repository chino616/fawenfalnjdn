"""Read-only source, CSV and exported XLSX checks plus visual contact sheets.

Uses the standard library for XLSX inspection (never for authoring) and Pillow
for internal QA contact sheets. It does not modify the numerical tables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def letter(index):
    s, n = "", index + 1
    while n:
        s = chr(65 + (n - 1) % 26) + s
        n = (n - 1) // 26
    return s


def parse_cells(xml, strings):
    root = ET.fromstring(xml)
    cells = {}
    for c in root.findall(".//m:sheetData/m:row/m:c", NS):
        typ = c.get("t", "n")
        v = c.find("m:v", NS)
        if typ == "s": val = strings[int(v.text)] if v is not None else None
        elif typ == "inlineStr": val = "".join(n.text or "" for n in c.findall(".//m:t", NS))
        elif typ == "b": val = v.text == "1" if v is not None else None
        elif typ == "n": val = float(v.text) if v is not None and v.text is not None else None
        else: val = v.text if v is not None else None
        if typ == "e": raise ValueError("Excel error " + c.get("r", "") + " " + str(val))
        cells[c.get("r")] = {"value": val, "formula": c.find("m:f", NS), "type": typ}
    return root, cells


def equal(actual, expected):
    if expected is None or expected == "": return actual in [None, ""]
    if isinstance(expected, bool): return isinstance(actual, bool) and actual is expected
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isclose(actual, expected, rel_tol=2e-9, abs_tol=2e-7)
    return actual == expected


def verify(out):
    payload = read(out / "TABLES.json")
    receipt = read(out / "qa/WORKBOOK_CHECKS.json")
    sources = read(out / "SOURCE_MANIFEST.json")
    changed = [p for p, h in sources.items() if sha(ROOT / p) != h]
    if changed: raise ValueError("Adopted sources changed: " + str(changed))
    xlsx = out / "CEvNS_Results_Summary_20261115.xlsx"
    cells_checked, formula_count, filters, panes = 0, 0, [], []
    with zipfile.ZipFile(xlsx) as z:
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        names = [s.get("name") for s in workbook.findall("m:sheets/m:sheet", NS)]
        if names != [t["sheet"] for t in payload["tables"]]: raise ValueError("Sheet order/names differ")
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in r.findall(".//m:t", NS)) for r in shared]
        for index, t in enumerate(payload["tables"], 1):
            xml, cells = parse_cells(z.read(f"xl/worksheets/sheet{index}.xml"), strings)
            for i, c in enumerate(t["columns"]):
                if cells[letter(i) + "6"]["value"] != c["label"]: raise ValueError("Header mismatch: " + t["sheet"])
            for ri, row in enumerate(t["rows"], 7):
                for ci, c in enumerate(t["columns"]):
                    cell = cells.get(letter(ci) + str(ri), {"value": None, "formula": None})
                    if not equal(cell["value"], row.get(c["key"])):
                        raise ValueError(f"Saved value mismatch {t['sheet']}!{letter(ci)}{ri}: {cell['value']!r} != {row.get(c['key'])!r}")
                    cells_checked += 1
            formula_count += sum(c["formula"] is not None for c in cells.values())
            view = xml.find("m:sheetViews/m:sheetView", NS)
            pane = view.find("m:pane", NS)
            if pane is None or pane.get("ySplit") != "6": raise ValueError("Header freeze missing: " + t["sheet"])
            if view.get("showGridLines") != "0": raise ValueError("Visible grid lines: " + t["sheet"])
            panes.append(t["sheet"])
            tab = ET.fromstring(z.read(f"xl/tables/table{index}.xml"))
            if tab.find("m:autoFilter", NS) is None: raise ValueError("Filter missing: " + t["sheet"])
            filters.append(t["sheet"])
            with (out / "tables" / (t["id"] + ".csv")).open(encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            if len(rows) != len(t["rows"]): raise ValueError("CSV record count differs: " + t["sheet"])
            for actual, original in zip(rows, t["rows"]):
                for c in t["columns"]:
                    expected = original.get(c["key"])
                    expected = "" if expected is None else str(expected)
                    if actual[c["key"]] != expected: raise ValueError("CSV changed: " + t["id"] + "." + c["key"])
    if formula_count != receipt["formulas_checked"]: raise ValueError("Formula count mismatch")
    from PIL import Image, ImageDraw, ImageFont
    try: font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    except OSError: font = ImageFont.load_default()
    contacts = []
    for batch in range(0, len(payload["tables"]), 4):
        selected = payload["tables"][batch:batch + 4]
        cards = []
        for t in selected:
            im = Image.open(out / "qa/previews" / (t["id"] + ".png")).convert("RGB")
            im.thumbnail((1450, 850))
            card = Image.new("RGB", (1470, 890), "white")
            ImageDraw.Draw(card).text((12, 8), t["id"] + f" ({len(t['rows'])} rows)", fill="#215B84", font=font)
            card.paste(im, (10, 40))
            cards.append(card)
        contact = Image.new("RGB", (2940, 1780 if len(cards) > 2 else 890), "#DDE5EA")
        for i, card in enumerate(cards): contact.paste(card, ((i % 2) * 1470, (i // 2) * 890))
        p = out / "qa/previews" / f"contact_{batch // 4 + 1:02d}.png"
        contact.save(p)
        contacts.append(str(p))
    result = {"status": "PASS_SAVED_XLSX_AND_CSV_CHECKS", "as_of": payload["date"], "sheets": len(payload["tables"]),
              "record_counts": {t["sheet"]: len(t["rows"]) for t in payload["tables"]}, "saved_cells_checked": cells_checked,
              "cached_formulas_checked": formula_count, "filters_verified": len(filters), "panes_verified": len(panes),
              "sources_unchanged": len(sources), "source_changes": changed, "contacts": contacts,
              "visual_review": "PENDING_EXECUTOR_REVIEW", "native_engine": "artifact-tool recalculation; XLSX cached results independently read through XML; Excel UI not used"}
    write(out / "qa/EXPORTED_FILE_CHECKS.json", result)
    print(json.dumps(result, ensure_ascii=False))


def verify_links(out):
    # The repository checker deliberately excludes outputs, even when selected
    # explicitly. Audit only these task-owned result documents in addition to
    # its normal four-document report; never crawl old outputs or backup.
    selected = [ROOT / p for p in ["examples/README.md", "outputs/README.md", "docs/experiments/README.md",
                "examples/results_summary/README.md", "docs/experiments/RESULTS_TABLES_20261115.md"]]
    selected += [out / p for p in ["README.md", "RESULTS.md", "tables/README.md", "qa/README.md"]]
    selected += [ROOT / "论文图NoteBook" / p for p in ["README.md", "8. SM_experiment_benchmarks/README.md", "8. SM_experiment_benchmarks/REFERENCES_AND_METHODS.md", "8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md", "8. SM_experiment_benchmarks/qa/README.md", "8. SM_experiment_benchmarks/PAPER_CAPTIONS.md"]]
    pattern = re.compile(r"\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+\"[^\"]*\")?\)")
    links, broken = [], []
    for file in selected:
        for line, text in enumerate(file.read_text(encoding="utf-8-sig").splitlines(), 1):
            for m in pattern.finditer(text):
                target = m.group(1) or m.group(2)
                if re.match(r"^(?:https?|mailto|data|plugin|app|codex):", target): continue
                local = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not local: continue
                resolved = (file.parent / local).resolve()
                row = {"file": str(file.relative_to(ROOT)), "line": line, "target": target,
                       "resolved": str(resolved), "status": "PASS" if resolved.exists() else "MISSING"}
                links.append(row)
                if row["status"] == "MISSING": broken.append(row)
    native = read(out / "qa/DOC_LINKS_NATIVE.json")
    result = {"status": "PASS_SCOPED_DOCUMENT_LINKS" if not broken else "BROKEN_LINKS",
              "documents": len(selected), "local_links": len(links), "broken_current_links": broken,
              "native_checker_documents": native["markdown_documents"], "native_checker_links": native["local_links"],
              "scope": "Explicit result-summary and CsI-comparator documents only; outputs handled by this local-file audit because the native checker excludes outputs; no archive traversal.",
              "limitations": "HTTP availability and Markdown anchors not checked; file ownership and prose/CLI references reviewed separately.", "links": links}
    write(out / "qa/DOC_LINKS.json", result)
    (out / "qa/DOC_LINKS.txt").write_text(json.dumps({k: v for k, v in result.items() if k != "links"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if broken: raise ValueError("Broken selected-document links: " + str(broken))
    print(json.dumps({k: result[k] for k in ["status", "documents", "local_links", "native_checker_documents"]}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "outputs/results_summary_20261115_run2")
    p.add_argument("--links-only", action="store_true")
    args = p.parse_args()
    if args.links_only: verify_links(args.output.resolve())
    else: verify(args.output.resolve())
