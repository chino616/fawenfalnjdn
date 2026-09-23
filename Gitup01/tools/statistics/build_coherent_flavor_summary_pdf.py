from __future__ import annotations

import csv
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
BASE = ROOT / "results" / "flavor_benchmark" / "COHERENT_highres_all_grid101"
OUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs" / "coherent_flavor_lowres_images"
OUT_PDF = OUT_DIR / "coherent_flavor_highres_grid101_lowres_summary.pdf"
FONT = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf")

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

summary = {}
with (BASE / "highres_scan_summary.csv").open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        summary[(row["dataset"], row["plane"])] = row

with (BASE / "integration_convergence_checks.csv").open(encoding="utf-8", newline="") as f:
    conv_rows = list(csv.DictReader(f))

PLANE_LABELS = {
    "ee_uV_dV": ("epsilon_ee_uV", "epsilon_ee_dV", "电子味对角 NSI: u 夸克与 d 夸克矢量耦合"),
    "mumu_uV_dV": ("epsilon_mumu_uV", "epsilon_mumu_dV", "缪味对角 NSI: u 夸克与 d 夸克矢量耦合"),
    "emu_uV_dV": ("epsilon_emu_uV", "epsilon_emu_dV", "实数 e-mu 非对角 NSI: u 夸克与 d 夸克矢量耦合"),
}
DATASET_LABELS = {"csi2021": "CsI2021", "csi2017": "CsI2017", "ar2020": "Ar2020", "combined": "combined", "overlay": "overlay"}
FIG_ORDER = []
for plane in ("ee_uV_dV", "mumu_uV_dV", "emu_uV_dV"):
    for dataset in ("csi2021", "csi2017", "ar2020", "combined"):
        FIG_ORDER.append((dataset, plane, BASE / f"fig_{dataset}_{plane}_grid101_range_m1_p1.png"))
    FIG_ORDER.append(("overlay", plane, BASE / f"fig_overlay_csi2021_csi2017_ar2020_{plane}_grid101_range_m1_p1.png"))

missing = [str(path) for _, _, path in FIG_ORDER if not path.exists()]
if missing:
    raise FileNotFoundError("Missing expected figures: " + "; ".join(missing))


def lowres_copy(src: Path) -> Path:
    dst = TMP_DIR / (src.stem + "_lowres.jpg")
    im = Image.open(src).convert("RGB")
    im.thumbnail((980, 860), Image.Resampling.LANCZOS)
    im.save(dst, "JPEG", quality=38, optimize=True)
    return dst


def wrapped(text: str, width: int) -> str:
    parts = []
    for para in text.split("\n"):
        if not para.strip():
            parts.append("")
        else:
            parts.extend(textwrap.wrap(para, width=width, break_long_words=False, replace_whitespace=False))
    return "\n".join(parts)


def row_text(dataset: str, plane: str) -> str:
    row = summary.get((dataset, plane))
    if not row:
        return ""
    trunc = "是" if row.get("truncated_by_frame", "").lower() == "true" else "否"
    contour = "有" if row.get("contour_available", "").lower() == "true" else "无"
    return (
        f"网格最佳点: ({float(row['bestfit_x']):.3g}, {float(row['bestfit_y']):.3g}); "
        f"chi2_min={float(row['chi2_min']):.6g}; 90% 等高线: {contour}; "
        f"是否触碰/截断 [-1,1] 图框: {trunc}."
    )


def explanation(dataset_key: str, plane: str) -> tuple[str, str]:
    px, py, physics = PLANE_LABELS[plane]
    if dataset_key == "overlay":
        return (
            f"三实验与联合等高线叠加 - {plane}",
            f"参数平面: x={px}, y={py}。{physics}。\n"
            "图中叠加 CsI2021、CsI2017、Ar2020 以及三实验联合的 Delta chi2=4.61 等高线；散点为各自 101x101 网格上的最佳点，SM 原点以十字标出。\n"
            "联合结果构造: 每个实验先使用对应 legacy approximate likelihood 完成 nuisance profiling，然后把同一网格点上的原始 chi2 逐点相加，再对总 chi2 重新取最小值得到 Delta chi2。",
        )
    dataset = DATASET_LABELS[dataset_key]
    if dataset_key == "combined":
        return (
            f"三实验联合 - {plane}",
            f"参数平面: x={px}, y={py}。{physics}。\n"
            "结果得到方式: CsI2021、CsI2017、Ar2020 分别在同一 101x101 网格点完成 nuisance profiling，随后把三个实验的原始 chi2 逐点相加，最后用联合 chi2 的最小值归一化为 Delta chi2。白线为联合 Delta chi2=4.61。\n"
            + row_text("combined", plane),
        )
    return (
        f"{dataset} - {plane}",
        f"参数平面: x={px}, y={py}。{physics}。\n"
        f"结果得到方式: 使用 {dataset} 的 Flavor Fast kernel 在 [-1,1] x [-1,1] 上做 101x101 网格扫描；每个网格点把 NSI epsilon 转为 NP-only Wilson 矩阵，重建三种 SNS source flavor 的事件数，再送入迁移后的 legacy approximate likelihood 做 nuisance profiling。图中颜色是相对该实验网格最小值的 Delta chi2，白线为 2D 90% 阈值 Delta chi2=4.61。\n"
        + row_text(dataset, plane),
    )


def add_text(fig, x, y, text, size=10, color="#111111"):
    fig.text(x, y, text, fontproperties=FONT, fontsize=size, color=color, va="top", ha="left", linespacing=1.24)

with PdfPages(OUT_PDF) as pdf:
    fig = plt.figure(figsize=(11.69, 8.27), dpi=110)
    fig.patch.set_facecolor("white")
    add_text(fig, 0.06, 0.92, "COHERENT Flavor 高分辨率扫描汇总", 20)
    cover = (
        "本 PDF 汇总 COHERENT_highres_all_grid101 中的 15 张图。为了便于快速查看，嵌入图片为低清晰度压缩版本；原始 PNG 保留在结果目录中。\n"
        "扫描设置: 横纵坐标固定为 [-1,1]，网格为 101x101。覆盖 ee、mumu、实数 e-mu 三个二维 NSI 参数平面；每个平面包含 CsI2021、CsI2017、Ar2020、三实验联合以及等高线叠加图。\n"
        "统计说明: 所有结果均为 legacy approximate statistics，不是官方 COHERENT likelihood。2D 90% 阈值使用 Delta chi2=4.61。若最佳点或 90% 区域触碰图框，原图已标注 TRUNCATED BY FRAME，摘要 CSV 也记录截断状态。"
    )
    add_text(fig, 0.06, 0.84, wrapped(cover, 88), 11)
    add_text(fig, 0.06, 0.52, "物理积分 / Fast kernel 匹配检查", 14)
    y = 0.47
    for row in conv_rows:
        line = f"{row['dataset']}: pass={row['pass']}; method={row['method']}; max_abs_bin_delta={row['max_abs_bin_delta']}; total_delta={row['total_delta']}"
        add_text(fig, 0.07, y, wrapped(line, 105), 9)
        y -= 0.075
    add_text(fig, 0.06, 0.08, "Generated from migrated CEvNS-pyEFT Flavor outputs; low-resolution PDF summary.", 8, "#666666")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    for idx, (dataset_key, plane, fig_path) in enumerate(FIG_ORDER, start=1):
        title, body = explanation(dataset_key, plane)
        low_img = lowres_copy(fig_path)
        img = Image.open(low_img)
        fig = plt.figure(figsize=(11.69, 8.27), dpi=110)
        fig.patch.set_facecolor("white")
        add_text(fig, 0.045, 0.955, f"{idx}. {title}", 14)
        add_text(fig, 0.045, 0.90, wrapped(body, 112), 8.8)
        ax = fig.add_axes([0.12, 0.055, 0.76, 0.60])
        ax.imshow(np.asarray(img))
        ax.axis("off")
        fig.text(0.93, 0.025, f"page {idx + 1} / {len(FIG_ORDER) + 1}", fontproperties=FONT, fontsize=7, color="#666666", ha="right")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

print(OUT_PDF)
print(f"pages={len(FIG_ORDER) + 1} size={OUT_PDF.stat().st_size}")
