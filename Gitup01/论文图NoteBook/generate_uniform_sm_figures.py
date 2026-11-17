"""Apply one publication style to the frozen SM figure inputs.

The earlier generator is imported read-only for its saved-array plotting and
CSV/caption export. This consumer changes artists and layout in memory; it
does not invoke a predictor or alter any scientific arrays or original files.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.container import ErrorbarContainer
from matplotlib.ticker import AutoMinorLocator, NullLocator
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD_SCRIPT = ROOT / "论文图NoteBook/generate_sm_experiment_figures.py"
SPEC = importlib.util.spec_from_file_location("saved_sm_plot_consumer", OLD_SCRIPT)
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
STYLE_SPEC = importlib.util.spec_from_file_location("uniform_publication_style", ROOT / "论文图NoteBook/9. SM_uniform_style/publication_style.py")
STYLE_MODULE = importlib.util.module_from_spec(STYLE_SPEC)
STYLE_SPEC.loader.exec_module(STYLE_MODULE)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                   allow_nan=False) + "\n", encoding="utf-8")


def configure(style):
    palette = STYLE_MODULE.configure(style)
    BASE.BLUE = palette["work_SM"]
    BASE.ORANGE = palette["reference"]
    BASE.GRAY = palette["neutral"]
    BASE.GREEN = palette["control_or_total"]
    BASE.PURPLE = palette["neutron"]
    BASE.DARK = palette["data"]


def family(name):
    if name.startswith("Table_"): return "table"
    if "CONUS" in name: return "conus"
    if "CsI2017" in name: return "csi17"
    if "Ar2020" in name: return "ar"
    if "Singlebin" in name: return "solar"
    if "Multibin" in name: return "multi"
    if "Components" in name: return "components"
    return "time"


def restyle(fig, name, style):
    kind = family(name)
    titles = {
        "conus": ["CONUS+: nominal SM", ""],
        "csi17": ["CsI2017: nominal SM (legacy)"],
        "time": [r"(a) PE projection ($0$-$6\,\mu$s)", "(b) Time projection (0-60 PE)"],
        "components": ["(a) Flavor components in PE", "(b) Flavor components in time"],
        "ar": ["(a) Signal template comparison", "(b) Legacy analysis points"],
        "solar": ["PandaX-4T paired", "PandaX-4T US2", "XENONnT"],
        "multi": ["(a) PandaX-4T US2", "(b) XENONnT (bin ordinals)"],
        "table": ["Standard Model numerical summary"],
    }
    notes = {
        "conus": "Effective 1 kg detector, 119 days. Reference prediction and excess data retain distinct roles.",
        "csi17": "Specified legacy grid; digitized residual limits have unresolved confidence meaning.",
        "time": "Unfitted forward prediction; neutron backgrounds retain their raw-template normalization.",
        "components": "Derived residuals; subtraction covariance is unavailable, so no vertical errors are asserted.",
        "ar": "Ordered bins only: the legacy PE / official keVee correspondence remains unresolved.",
        "solar": "Theoretical predictions and experimental fitted signals are shown separately.",
        "multi": "Reference fitted backgrounds are reused for display; no empirical signal rescaling.",
        "table": "Comparator columns retain their different model meanings; entries are not a joint data sample.",
    }
    layout = {"conus": "spectrum_ratio", "csi17": "single", "solar": "three_panel", "table": "table"}.get(kind, "two_panel")
    xkinds = ["continuous"] * len(fig.axes)
    if kind in {"ar", "solar"}: xkinds = ["ordinal"] * len(fig.axes)
    if kind == "multi": xkinds = ["continuous", "ordinal"]
    STYLE_MODULE.finalize(fig, layout=layout, titles=titles[kind], note=notes[kind], xkinds=xkinds, style=style)
    return kind


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-snapshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--style", type=Path, default=Path(__file__).resolve().parent / "9. SM_uniform_style/STYLE.json")
    parser.add_argument("--refresh-draft", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    snapshot = args.from_snapshot.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.rglob("*.pdf")):
        if not args.refresh_draft or not (output / "WRITE_PLAN.json").is_file():
            parser.error("Use a new folder; --refresh-draft is limited to this task's own WRITE_PLAN")
        assert BASE.read_json(output / "WRITE_PLAN.json")["new_generator"] == Path(__file__).resolve().relative_to(ROOT).as_posix()
    style_path = output / "STYLE.json" if (output / "STYLE.json").is_file() else args.style.resolve()
    style = BASE.read_json(style_path)
    if style_path.resolve() != (output / "STYLE.json").resolve(): write(output / "STYLE.json", style)
    configure(style)
    metadata = BASE.read_json(snapshot / "metadata.json")
    data = {}
    for key in BASE.SETS:
        with np.load(snapshot / (key + ".npz"), allow_pickle=False) as z:
            data[key] = {k: z[k].copy() for k in z.files}
    for name in ["inputs", "qa", *BASE.SETS.values()]: (output / name).mkdir(exist_ok=True)
    for path in snapshot.iterdir():
        if path.suffix == ".npz" or path.name == "metadata.json":
            target = output / "inputs" / path.name
            if target.resolve() != path.resolve(): shutil.copyfile(path, target)
    write(output / "SOURCE_MANIFEST.json", metadata["source_files"])
    figures = []

    def save_uniform(fig, folder, name, caption, book):
        kind = restyle(fig, name, style)
        STYLE_MODULE.export(fig, folder / name, style=style)
        book.savefig(fig, bbox_inches=None, facecolor="white")
        (folder / (name + "_caption.txt")).write_text(caption + "\n", encoding="utf-8")
        figures.append({"name": name, "family": kind, "width_mm": style["width_mm"],
                        "height_mm": float(fig.get_figheight() * 25.4)})
        plt.close(fig)

    BASE.save = save_uniform
    with PdfPages(output / "SM_Uniform_Style_Collection.pdf") as book:
        for key, func in [("conus", BASE.draw_conus), ("time", BASE.draw_time),
                          ("csi17", BASE.draw_csi17), ("ar", BASE.draw_ar),
                          ("solar", BASE.draw_solar), ("multi", BASE.draw_multibin)]:
            func(data[key], output / BASE.SETS[key], book)
        BASE.draw_table(data, output, book)
    BASE.document(data, metadata, output)
    readme = output / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("# 标准模型实验论文图集", "# 标准模型论文图：统一样式版", 1)
    text = text.replace("SM_Benchmarks_Collection.pdf", "SM_Uniform_Style_Collection.pdf")
    text = text.replace("generate_sm_experiment_figures.py", "generate_uniform_sm_figures.py")
    text = text.replace("8. SM_experiment_benchmarks/inputs", "9. SM_uniform_style/inputs")
    text = text.replace("本轮完成绘图、单位与来源核对、CSV导出和PDF渲染验收，不进行新拟合。",
                        "本轮只统一作图样式：180 mm固定图宽、STIX字体、统一配色/线型、外置图例及一致的坐标与误差棒样式。所有原图与数值保持原样。")
    text += "\n\n## 后续复用同一套样式\n\n[详细样式规范](STYLE_GUIDE.md) · [统一样式参数](STYLE.json) · [独立样式模块](publication_style.py) · [可直接调用的模板](plot_template.py) · [色板](PALETTE.png)\n\n复制publication_style.py、STYLE.json和plot_template.py即可用于新图。整套既有实验图可调用上方生成器重画；新实验只需按模板传入自己的已确认数值。\n\n[样式与数据核对](VALIDATION.json) · [原图集](<../8. SM_experiment_benchmarks/README.md>)\n"
    readme.write_text(text, encoding="utf-8")
    (output / "qa/README.md").write_text("# 样式版式与数据检查\n\npage-1.png至page-8.png是合集PDF的逐页渲染，contact_sheet.png是目视检查总览。PDF_QA.json核对固定180 mm图宽、字体与页面边界；DOC_LINK_CHECKS.json核对文档链接；TEMPLATE_CHECK.json记录可复用模块的实际调用。输入和CSV保持原值的检查见上一级VALIDATION.json。\n\n[样式规范](../STYLE_GUIDE.md) · [图集](../README.md)\n", encoding="utf-8")
    original = snapshot.parent
    csv_checks = []
    for file in sorted(output.rglob("*.csv")):
        reference = original / file.relative_to(output)
        assert file.read_bytes() == reference.read_bytes(), file
        csv_checks.append(file.relative_to(output).as_posix())
    input_checks = []
    for file in sorted((output / "inputs").glob("*.npz")):
        assert sha(file) == sha(snapshot / file.name), file
        input_checks.append(file.name)
    if not (output / "ORIGINAL_FILES.json").is_file():
        if (snapshot.parent / "ORIGINAL_FILES.json").is_file():
            shutil.copyfile(snapshot.parent / "ORIGINAL_FILES.json", output / "ORIGINAL_FILES.json")
        else:
            write(output / "ORIGINAL_FILES.json", {p.relative_to(ROOT).as_posix(): sha(p)
                  for p in [OLD_SCRIPT, *snapshot.glob("*.npz")]})
    protection = BASE.read_json(output / "ORIGINAL_FILES.json")
    for name, expected in protection.items(): assert sha(ROOT / name) == expected, name
    write(output / "VALIDATION.json", {
        "status": "PASS_SAME_NUMERICAL_INPUTS_AND_CSV; VISUAL_QA_PENDING",
        "date": "2026-11-13", "changes": "style only", "numerical_calculations": 0,
        "input_snapshot_SHA256_identical": input_checks, "CSV_byte_identical": csv_checks,
        "original_files_unchanged": len(protection), "figures": figures,
        "generator": {"path": str(Path(__file__).resolve()), "sha256": sha(__file__)},
        "base_readonly_consumer": {"path": str(OLD_SCRIPT), "sha256": sha(OLD_SCRIPT)},
        "paper_equivalence": "No new scientific claim; original limitations and captions retained"})
    if not (output / "FILE_LIFECYCLE.json").is_file():
        write(output / "FILE_LIFECYCLE.json", {"scope": "new plotting directory only",
              "owning_README": "README.md", "experiment_owners": {
                  name: name + "/README.md" for name in BASE.SETS.values()},
              "category_owners": {"input snapshots": "inputs/README.md", "render checks": "qa/README.md"}})
    print(json.dumps({"output": str(output), "PDFs": len(list(output.rglob("*.pdf"))),
                      "identical_CSVs": len(csv_checks), "identical_NPZs": len(input_checks),
                      "protected_original_files": len(protection)}, ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main()
