"""Build a viewable PDF preview when the local TeX executable is unavailable."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "conus-plus-completion-20261012" / "paper"
STEMS = (
    "fig_conus_skill_workflow",
    "fig_conus_forward_chain",
    "fig_conus_statistical_benchmark",
    "fig_conus_fast_validation",
    "fig_conus_nsi_four_panels",
)


def main() -> None:
    with PdfPages(OUT / "preview.pdf") as pdf:
        page = plt.figure(figsize=(8.27, 11.69))
        page.text(0.08, 0.92, "CONUS+ completion preview", fontsize=20, weight="bold")
        page.text(0.08, 0.86, "Formal project artifacts; effective-119 approximate benchmark; Ge73-only.", fontsize=11)
        page.text(0.08, 0.81, "The full EFT quadratic kernel and official likelihood remain pending.", fontsize=11)
        page.text(0.08, 0.73, "Included figures:", fontsize=13, weight="bold")
        page.text(0.10, 0.68, "\n".join(STEMS), fontsize=10, va="top")
        pdf.savefig(page)
        plt.close(page)
        for stem in STEMS:
            figure, axis = plt.subplots(figsize=(11, 8))
            axis.imshow(mpimg.imread(OUT.parent / "figures" / f"{stem}.png"))
            axis.axis("off")
            axis.set_title(stem.replace("_", " "))
            pdf.savefig(figure, bbox_inches="tight")
            plt.close(figure)


if __name__ == "__main__":
    main()
