from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
import numpy as np

ROOT = Path.cwd()
BASE = ROOT / "Benchmark" / "260928 COHENRENT-NSI" / "native_overlap_comparison"
OUT_DIR = ROOT / "output" / "pdf"
OUT = OUT_DIR / "benchmark_2211_11905_native_overlap_comparison.pdf"
FONT = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf")
OUT_DIR.mkdir(parents=True, exist_ok=True)

report = (BASE / "NATIVE_OVERLAP_COMPARISON_REPORT.md").read_text(encoding="utf-8")
provenance = json.loads((BASE / "provenance_native_overlap.json").read_text(encoding="utf-8"))
with (BASE / "panel_status.csv").open(encoding="utf-8", newline="") as f:
    panel_rows = list(csv.DictReader(f))

comparison_paths = [
    BASE / "figures" / "comparison" / "Fig03_native_approx_comparison.png",
    BASE / "figures" / "comparison" / "Fig04_native_approx_comparison.png",
    BASE / "figures" / "comparison" / "Fig05_native_approx_comparison.png",
    BASE / "figures" / "comparison" / "Fig06_native_approx_comparison.png",
    BASE / "figures" / "comparison" / "Fig07_NGI_not_comparable.png",
]
missing = [str(p) for p in comparison_paths if not p.exists()]
if missing:
    raise FileNotFoundError("Missing comparison figures: " + "; ".join(missing))


def wrap(text: str, width: int = 88) -> str:
    out: list[str] = []
    for para in text.splitlines():
        if not para.strip():
            out.append("")
        else:
            out.extend(textwrap.wrap(para, width=width, break_long_words=False, replace_whitespace=False))
    return "\n".join(out)


def fig_text(fig, x, y, text, size=10, color="#111111", width=88):
    fig.text(x, y, wrap(text, width), fontproperties=FONT, fontsize=size, color=color, va="top", ha="left", linespacing=1.25)


def add_table(fig, rows):
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.64])
    ax.axis("off")
    headers = ["figure", "panel", "x", "y", "status"]
    data = [[r.get(h, "") for h in headers] for r in rows]
    table = ax.table(cellText=data, colLabels=headers, loc="upper left", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1.0, 1.25)
    for (_, _), cell in table.get_celld().items():
        cell.get_text().set_fontproperties(FONT)
        cell.set_edgecolor("#dddddd")

with PdfPages(OUT) as pdf:
    fig = plt.figure(figsize=(11.69, 8.27), dpi=110)
    fig.patch.set_facecolor("white")
    fig_text(fig, 0.05, 0.94, "arXiv:2211.11905 Fig.3-Fig.7 复现对比汇总", 18)
    summary = (
        "本 PDF 汇总 Benchmark/260928 COHENRENT-NSI/native_overlap_comparison 的输出。"
        "结果性质为 PARTIAL_NATIVE_APPROXIMATE_COMPARISON：使用迁移后的 CEvNS-pyEFT Flavor Fast kernel 与 legacy approximate statistics，"
        "不是论文 paper-matched likelihood 复现。\n"
        "Fig.3-Fig.6 生成了 native approximate NSI 重绘和论文页渲染的并排对比。"
        "Fig.7 是 NGI scalar/vector/tensor，当前没有用 NSI 结果伪造复现，已标为 NGI_MISSING / NOT_COMPARABLE。\n"
        f"paper_sha256: {provenance.get('paper_sha256', '')}\n"
        f"git_commit: {provenance.get('git_commit', '')}\n"
        f"grid_n: {provenance.get('grid_n', '')}; threshold_2d: {provenance.get('threshold_2d', '')}"
    )
    fig_text(fig, 0.05, 0.84, summary, 10, width=105)
    fig_text(fig, 0.05, 0.42, "关键限制", 14)
    limits = (
        "1. CsI 使用当前 CsI2021 legacy approximate likelihood，不是论文 9 PE x 11 timing Poisson likelihood。\n"
        "2. Ar 使用当前 Ar2020 legacy approximate likelihood，不是论文 LAr timing-energy Gaussian + shape nuisance likelihood。\n"
        "3. 正式 paper joint 不加入 CsI2017；本对比也未加入 CsI2017。\n"
        "4. 论文原图为整页渲染，尚非人工精裁后的图像区域。"
    )
    fig_text(fig, 0.07, 0.36, limits, 10, width=105)
    fig.text(0.93, 0.025, "page 1", fontproperties=FONT, fontsize=8, color="#666666", ha="right")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    fig = plt.figure(figsize=(11.69, 8.27), dpi=110)
    fig.patch.set_facecolor("white")
    fig_text(fig, 0.05, 0.94, "Panel 状态表", 16)
    fig_text(fig, 0.05, 0.89, "以下表格来自 panel_status.csv；Fig.7 明确标为不可比。", 10)
    add_table(fig, panel_rows)
    fig.text(0.93, 0.025, "page 2", fontproperties=FONT, fontsize=8, color="#666666", ha="right")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    for i, path in enumerate(comparison_paths, start=3):
        im = Image.open(path).convert("RGB")
        fig = plt.figure(figsize=(11.69, 8.27), dpi=110)
        fig.patch.set_facecolor("white")
        title = path.stem.replace("_", " ")
        fig_text(fig, 0.04, 0.96, title, 14)
        note = (
            "左侧为论文 PDF 对应页渲染；右侧为当前 CEvNS-pyEFT native approximate 重绘。"
            "该页用于视觉对照和实现差异定位，不表示已完成 paper-matched 统计复现。"
        )
        if "Fig07" in path.name:
            note = "Fig.7 为 NGI scalar/vector/tensor benchmark；当前结果明确标记为 NGI_MISSING / NOT_COMPARABLE，没有使用 NSI 图替代。"
        fig_text(fig, 0.04, 0.91, note, 8.5, width=130)
        ax = fig.add_axes([0.035, 0.055, 0.93, 0.80])
        ax.imshow(np.asarray(im))
        ax.axis("off")
        fig.text(0.93, 0.025, f"page {i}", fontproperties=FONT, fontsize=8, color="#666666", ha="right")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

print(OUT)
print(f"pages=7 size={OUT.stat().st_size}")
