"""Apply the canonical v4 theme; run a synthetic example without CEvNS imports."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.ticker import AutoMinorLocator, NullLocator
import numpy as np

if __package__:
    from .theme_styles import PaperTheme
else:
    from theme_styles import PaperTheme


def load_theme(path=None):
    """Resolve the default theme relative to this module, not the caller's cwd."""
    path = Path(path) if path is not None else Path(__file__).with_name("PAPER_THEME.json")
    return PaperTheme(path)


def configure(theme=None):
    """Apply typography and axes defaults from the supplied JSON."""
    theme = load_theme() if theme is None else theme
    cfg = theme.cfg
    font, c, a, e = (cfg[key] for key in ("typography", "colors", "axes", "export"))
    plt.rcParams.update({
        "font.family": font["font"], "mathtext.fontset": font["math_font"],
        "font.size": font["body_pt"], "axes.labelsize": font["axis_label_pt"],
        "axes.titlesize": font["panel_title_pt"], "axes.titleweight": font["title_weight"],
        "axes.titlelocation": "left", "text.color": c["ink"],
        "axes.labelcolor": c["ink"], "axes.edgecolor": c["frame"],
        "axes.linewidth": a["frame_pt"], "axes.axisbelow": a["axis_below"],
        "xtick.labelsize": font["tick_label_pt"], "ytick.labelsize": font["tick_label_pt"],
        "xtick.color": c["ink"], "ytick.color": c["ink"],
        "xtick.direction": a["tick_direction"], "ytick.direction": a["tick_direction"],
        "xtick.top": a["ticks_top"], "ytick.right": a["ticks_right"],
        "xtick.major.size": a["major_tick_length_pt"], "ytick.major.size": a["major_tick_length_pt"],
        "xtick.major.width": a["major_tick_width_pt"], "ytick.major.width": a["major_tick_width_pt"],
        "xtick.minor.size": a["minor_tick_length_pt"], "ytick.minor.size": a["minor_tick_length_pt"],
        "xtick.minor.width": a["minor_tick_width_pt"], "ytick.minor.width": a["minor_tick_width_pt"],
        "legend.fontsize": font["legend_pt"], "legend.frameon": cfg["legends"]["frameon"],
        "legend.handlelength": cfg["legends"]["handle_length"],
        "legend.columnspacing": cfg["legends"]["column_spacing"],
        "legend.handletextpad": cfg["legends"]["handle_text_pad"],
        "axes.prop_cycle": cycler(color=c["series_order"]),
        "lines.linewidth": cfg["lines"]["primary_pt"],
        "figure.facecolor": c["background"], "axes.facecolor": c["background"],
        "savefig.facecolor": c["background"], "savefig.transparent": e["transparent_background"],
        "savefig.bbox": None, "savefig.dpi": e["png_dpi"],
        "pdf.fonttype": e["pdf_fonttype"], "ps.fonttype": e["ps_fonttype"],
        "svg.fonttype": e["svg_fonttype"],
    })
    return theme


def new_figure(layout="single_column", theme=None):
    """Return a fixed physical canvas and flat axes; callers own panel labels."""
    theme = configure(theme)
    spec = theme.cfg["layouts"][layout]
    shape = {"single_column": (1, 1), "double_single": (1, 1),
             "double_1x2": (1, 2), "double_1x3": (1, 3),
             "double_2x2": (2, 2), "double_ratio": (2, 1)}[layout]
    options = {}
    if layout == "double_ratio":
        options = {"sharex": True, "gridspec_kw": {
            "height_ratios": [1, spec["lower_to_upper_height_ratio"]]}}
    fig, axes = plt.subplots(*shape, squeeze=False,
        figsize=(spec["width_mm"] / 25.4, spec["height_mm"] / 25.4), **options)
    fig.subplots_adjust(left=.18 if spec["width_mm"] == 86 else .09,
                        right=.975, bottom=.21 if shape[0] == 1 else .13,
                        top=.78 if shape[0] == 1 else .88,
                        wspace=.4, hspace=.65 if layout != "double_ratio" else .08)
    return fig, list(axes.flat)


def style_axis(ax, theme=None, *, xkind="continuous", grid=True):
    """Style ticks/grid without changing values, scales, or axis limits."""
    theme = load_theme() if theme is None else theme
    c, a = theme.cfg["colors"], theme.cfg["axes"]
    if xkind not in {"continuous", "category", "ordinal"}:
        raise ValueError("xkind must be continuous, category, or ordinal")
    if ax.get_xscale() == "linear":
        ax.xaxis.set_minor_locator(AutoMinorLocator(2) if xkind == "continuous" else NullLocator())
    if ax.get_yscale() == "linear":
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which="both", direction=a["tick_direction"],
                   top=a["ticks_top"], right=a["ticks_right"])
    ax.grid(False)
    if grid:
        ax.grid(axis=a["grid_axis_default"], which=a["grid_which_default"],
                color=c["grid"], linewidth=a["grid_pt"], alpha=a["grid_alpha"])
    ax.set_axisbelow(a["axis_below"])
    return ax


def export(fig, stem, theme=None):
    """Export identical canvases and refuse to overwrite existing figure files."""
    theme = load_theme() if theme is None else theme
    settings = theme.cfg["export"]
    stem = Path(stem)
    paths = [stem.with_suffix("." + ext) for ext in settings["formats"]]
    if any(path.exists() for path in paths):
        raise FileExistsError("Choose a new figure stem or output directory")
    stem.parent.mkdir(parents=True, exist_ok=True)
    for path in paths:
        fig.savefig(path, dpi=settings["png_dpi"], bbox_inches=None,
                    transparent=settings["transparent_background"],
                    facecolor=theme.cfg["colors"]["background"])
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    theme = load_theme()
    fig, axes = new_figure("double_1x2", theme)
    x = np.linspace(0, 5, 120)
    for index in range(3):
        axes[0].plot(x, np.exp(-(.4 + .1 * index) * x), markevery=18,
                     **theme.line_style(index, label=f"Series {index + 1}"))
    centers = np.arange(1, 6)
    baseline = np.zeros(5)
    for index in range(3):
        values = (index + 1) * np.exp(-centers / 4)
        axes[1].bar(centers, values, bottom=baseline,
                    **theme.bar_style(index, label=f"Series {index + 1}"))
        baseline += values
    for ax, title, xlabel in zip(axes, ["(a) Line series", "(b) Binned components"],
                                 ["Synthetic coordinate", "Synthetic bin"]):
        ax.set_title(title, loc="left")
        ax.set(xlabel=xlabel, ylabel="Synthetic response [a.u.]")
        style_axis(ax, theme, xkind="continuous" if ax is axes[0] else "ordinal")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center",
               bbox_to_anchor=(.54, .985), ncol=3)
    paths = export(fig, args.output_dir / "Theme_Template", theme)
    plt.close(fig)
    print("Theme v" + theme.cfg["version"] + ": " + ", ".join(str(p) for p in paths))


if __name__ == "__main__":
    main()
