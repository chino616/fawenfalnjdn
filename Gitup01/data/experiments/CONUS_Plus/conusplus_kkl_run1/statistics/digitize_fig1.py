"""Extract the 19 CONUS+ data markers/error bars from the fixed v3 PDF.

This offline provenance utility does not register a dataset or run a fit.
Requires pdfplumber, numpy, Pillow, and pdftoppm in the validation environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pdfplumber
from PIL import Image, ImageDraw, ImageFont


SOURCE = Path("docs/references/CONUS/2501.17843v3.pdf")
SOURCE_SHA256 = "b20923363badde299106a6df83f0dff5308fd69d652b59b9967d32b764057c90"
PREFIX = "conusplus_2501_17843v3_fig1_digitized"
SOURCE_ID = "arxiv_2501_17843v3_pdf_p10_fig1"
UNIT = "counts kg^-1 (10 eVee)^-1"
FIELDS = (
    "bin_index", "energy_low_eVee", "energy_high_eVee", "energy_center_eVee",
    "excess", "error_minus", "error_plus", "sigma_mean_derived",
    "error_lower_endpoint", "error_upper_endpoint", "source_id",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def black(color) -> bool:
    if isinstance(color, (list, tuple)):
        return len(color) in (1, 3) and all(abs(float(v)) < 1e-10 for v in color)
    return color is not None and abs(float(color)) < 1e-10


def bbox(obj):
    return {key: obj[key] for key in ("x0", "top", "x1", "bottom")}


def extract(pdf_path: Path):
    if sha256(pdf_path) != SOURCE_SHA256:
        raise ValueError("Source PDF changed; review the figure/calibration before extracting")
    with pdfplumber.open(pdf_path) as document:
        page = document.pages[9]
        # The inner white plot rectangle, excluding the larger figure background.
        frames = [r for r in page.rects if 250 < r["width"] < 270 and 180 < r["height"] < 190]
        if len(frames) != 1:
            raise ValueError("Expected one Fig. 1 plotting rectangle")
        frame = frames[0]
        left, right = frame["x0"], frame["x1"]
        top, bottom = frame["top"], frame["bottom"]
        # Major ticks are longer than minor ticks. Opposite-side ticks are excluded.
        xticks = sorted((i, l) for i, l in enumerate(page.lines)
                        if abs(l["width"]) < 1e-8 and 6 < l["height"] < 7
                        and abs(l["bottom"] - bottom) < 1e-6)
        xticks.sort(key=lambda pair: pair[1]["x0"])
        yticks = [(i, l) for i, l in enumerate(page.lines)
                  if abs(l["height"]) < 1e-8 and 6 < l["width"] < 7
                  and abs(l["x0"] - left) < 1e-6]
        yticks.sort(key=lambda pair: pair[1]["top"])
        if len(xticks) != 5 or len(yticks) != 6:
            raise ValueError("Major-tick count differs from the visually reviewed axes")
        x_values = np.array([150, 200, 250, 300, 350], dtype=float)
        y_values = np.array([80, 60, 40, 20, 0, -20], dtype=float)
        x_positions = np.array([l["x0"] for _, l in xticks])
        y_positions = np.array([l["top"] for _, l in yticks])
        x_map = np.polyfit(x_positions, x_values, 1)
        y_map = np.polyfit(y_positions, y_values, 1)
        x_residual = float(np.max(np.abs(np.polyval(x_map, x_positions) - x_values)))
        y_residual = float(np.max(np.abs(np.polyval(y_map, y_positions) - y_values)))
        if max(x_residual, y_residual) > 1e-5:
            raise ValueError("Axis calibration is not linear within PDF coordinate precision")
        # The legend also contains a black marker; its grey-border box identifies it.
        legends = [c for c in page.curves if c["fill"] and c["stroke"]
                   and 110 < c["width"] < 120 and 25 < c["height"] < 30]
        if len(legends) != 1:
            raise ValueError("Expected one legend rectangle")
        legend = legends[0]
        markers = [(i, c) for i, c in enumerate(page.curves)
                   if c["fill"] and black(c["non_stroking_color"])
                   and 3 < c["width"] < 4.5 and 3 < c["height"] < 4.5
                   and left < c["x0"] < c["x1"] < right
                   and legend["bottom"] < c["top"] < c["bottom"] < bottom]
        markers.sort(key=lambda pair: pair[1]["x0"])
        if len(markers) != 19:
            raise ValueError(f"Expected 19 data markers, found {len(markers)}")
        rows, traces = [], []
        for index, (curve_index, marker) in enumerate(markers, start=1):
            px = (marker["x0"] + marker["x1"]) / 2
            py = (marker["top"] + marker["bottom"]) / 2
            bars = [(i, l) for i, l in enumerate(page.lines)
                    if black(l["stroking_color"]) and abs(l["width"]) < 1e-8
                    and abs(l["x0"] - px) < 1e-5 and l["height"] > 25
                    and top < l["top"] < py < l["bottom"] < bottom]
            if len(bars) != 1:
                raise ValueError(f"Marker {index}: expected one matching vertical error bar")
            line_index, bar = bars[0]
            energy_pdf = float(np.polyval(x_map, px))
            energy = float(155 + 10 * index)
            if abs(energy_pdf - energy) > 1e-5:
                raise ValueError(f"Marker {index} not at the expected 10 eVee bin centre")
            value = float(np.polyval(y_map, py))
            lower = float(np.polyval(y_map, bar["bottom"]))
            upper = float(np.polyval(y_map, bar["top"]))
            minus, plus = value - lower, upper - value
            row = dict(zip(FIELDS, [index, energy - 5, energy + 5, energy,
                                   value, minus, plus, (minus + plus) / 2,
                                   lower, upper, SOURCE_ID]))
            rows.append(row)
            traces.append({
                "bin_index": index, "marker_curve_index_zero_based": curve_index,
                "error_bar_line_index_zero_based": line_index,
                "marker_bbox_pdf_points": bbox(marker),
                "marker_center_pdf_points": [px, py],
                "error_bar_bbox_pdf_points": bbox(bar),
                "error_bar_linewidth_pdf_points": bar["linewidth"],
                "mapped_energy_before_rounding_eVee": energy_pdf,
                "extracted_values_before_rounding": row,
            })
        calibration = {
            "coordinate_system": "PDF points; x from left, y from top; 72 points/inch",
            "page_size_points": [page.width, page.height], "plot_bbox_pdf_points": bbox(frame),
            "legend_excluded_bbox_pdf_points": bbox(legend),
            "x_ticks": [{"pdf_line_index_zero_based": i, "pdf_x": l["x0"], "value_eVee": v}
                        for (i, l), v in zip(xticks, x_values.tolist())],
            "y_ticks": [{"pdf_line_index_zero_based": i, "pdf_top": l["top"], "value": v}
                        for (i, l), v in zip(yticks, y_values.tolist())],
            "energy_eVee_equals_a_times_pdf_x_plus_b": x_map.tolist(),
            "excess_equals_a_times_pdf_top_plus_b": y_map.tolist(),
            "max_x_tick_residual_eVee": x_residual,
            "max_y_tick_residual_in_plot_units": y_residual,
        }
    return rows, traces, calibration


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})
    return stream.getvalue().encode("utf-8")


def overlay(pdf_path, rows, calibration):
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise ValueError("pdftoppm is required for the source-image overlay")
    scale = 6  # 432 dpi
    with tempfile.TemporaryDirectory(prefix="conusplus-fig1-") as temporary:
        prefix = str(Path(temporary) / "source-page")
        subprocess.run([renderer, "-f", "10", "-l", "10", "-r", "432", "-singlefile",
                        "-png", str(pdf_path), prefix], check=True, capture_output=True)
        original = Image.open(prefix + ".png").convert("RGB")
        crop_box = (140 * scale, 72 * scale, 470 * scale, 310 * scale)
        crop = original.crop(crop_box)
    canvas = Image.new("RGB", (crop.width, crop.height + 100), "white")
    canvas.paste(crop, (0, 100))
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 25) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 19) if font_path.exists() else ImageFont.load_default()
    draw.text((25, 12), "CONUS+ | arXiv:2501.17843v3 | PDF page 10, Fig. 1", fill="black", font=font)
    draw.text((25, 51), "Orange circles: CSV data centres; cyan caps: CSV error-bar endpoints; labels: bin index",
              fill="black", font=small)
    ax, bx = calibration["energy_eVee_equals_a_times_pdf_x_plus_b"]
    ay, by = calibration["excess_equals_a_times_pdf_top_plus_b"]
    # Read back rounded CSV values: this overlay validates the delivered table.
    for row in csv.DictReader(io.StringIO(csv_bytes(rows).decode("utf-8"))):
        x = ((float(row["energy_center_eVee"]) - bx) / ax - 140) * scale
        y = ((float(row["excess"]) - by) / ay - 72) * scale + 100
        draw.ellipse((x - 16, y - 16, x + 16, y + 16), outline="#e07700", width=3)
        draw.text((x + 20, y - 9), row["bin_index"], fill="#9e4500", font=small)
        for key in ("error_lower_endpoint", "error_upper_endpoint"):
            endpoint = ((float(row[key]) - by) / ay - 72) * scale + 100
            draw.line((x - 10, endpoint, x + 10, endpoint), fill="#00a7aa", width=3)
    output = io.BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only check of CSV, provenance and overlay hashes")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = next((p for p in here.parents if (p / SOURCE).is_file()), None)
    if root is None:
        raise ValueError("Cannot find the documented source PDF above this data directory")
    pdf = root / SOURCE
    rows, traces, calibration = extract(pdf)
    data = csv_bytes(rows)
    csv_path = here / (PREFIX + ".csv")
    overlay_path = here / (PREFIX + ".overlay.png")
    provenance_path = here / (PREFIX + ".provenance.json")
    checks = {
        "row_count": len(rows), "bin_count_is_19": len(rows) == 19,
        "centres_are_165_to_345_step_10_eVee": True,
        "derived_edges_are_160_to_350_step_10_eVee": True,
        "all_error_lengths_positive": all(r["error_minus"] > 0 and r["error_plus"] > 0 for r in rows),
        "negative_excess_count": sum(r["excess"] < 0 for r in rows),
        "negative_values_preserved": True,
        "max_error_plus_minus_difference": max(abs(r["error_plus"] - r["error_minus"]) for r in rows),
        "csv_rounding_decimal_places": 4,
        "statistical_fit_executed": False,
    }
    metadata = {
        "source_id": SOURCE_ID, "experiment": "CONUS+", "dataset_id": "conusplus_kkl_run1",
        "benchmark_id": "CONUSPLUS_19BIN_EQ33", "created_date": "2026-11-06", "timezone": "Asia/Shanghai",
        "provenance_status": "PROJECT_DERIVED", "data_status": "FIGURE_DIGITIZED_NOT_AUTHOR_NUMERICAL_RELEASE",
        "source": {
            "title": "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering",
            "authors": ["V. De Romeri", "D. K. Papoulias", "G. Sanchez Garcia"],
            "arxiv": "2501.17843v3", "version_date": "2025-04-23",
            "url": "https://arxiv.org/abs/2501.17843v3",
            "doi": "10.1103/PhysRevD.111.075025", "local_path_from_repository_root": SOURCE.as_posix(),
            "sha256": SOURCE_SHA256, "pdf_page_one_based": 10, "figure": "1",
            "extracted_graphics": "black CONUS+ data markers and vertical error bars only; blue theory histogram excluded",
            "upstream_experiment_reference": "Fig. 1 attributes the experimental points to its Ref. [40], CONUS+ measurement 2501.05206; extraction is directly from 2501.17843v3, not that original dataset",
        },
        "quantity": {
            "observable": "reconstructed ionization energy", "energy_unit": "eVee",
            "data_semantics": "reactor-on data minus fitted background; signed excess",
            "excess_and_error_unit": UNIT,
            "already_background_subtracted": True, "raw_poisson_counts": False,
            "preserve_original_plot_normalization": True,
            "exposure_mass_time_or_bin_width_rescaling_applied": False,
            "paper_effective_detector": {"mass_kg": 1, "exposure_kg_day": 119, "threshold_eVee": 160},
        },
        "method": {
            "extraction": "pdfplumber PDF vector paths; circle centres, vertical-line endpoints; linear maps from all major axis ticks",
            "pdfplumber_version": pdfplumber.__version__,
            "energy_centres": "Mapped PDF positions coincide with 165,175,...,345 eVee; stored at these exact bin centres",
            "edges": "PROJECT_DERIVED: centre +/-5 eVee; supported by 10 eVee spacing and 19-bin paper definition; not an author edge file",
            "errors": "error_minus = excess - lower_endpoint; error_plus = upper_endpoint - excess",
            "symmetric_error_optional_column": "sigma_mean_derived = (error_minus + error_plus)/2; a declared arithmetic conversion, not a verified author-code convention",
            "precision": "Four decimal places preserve the plotted geometry reproducibly; they do not imply experimental precision or recovery of unpublished original values",
            "visual_linewidth_reference_scale": {
                "half_error_bar_stroke_in_y_plot_units": abs(calibration["excess_equals_a_times_pdf_top_plus_b"][0]) * traces[0]["error_bar_linewidth_pdf_points"] / 2,
                "meaning": "Visible half-stroke scale only, not a statistical uncertainty or a certified digitization error bound",
            },
            "overlay": "432 dpi rendering of source page cropped to Fig. 1; read-back CSV centres/endpoints overlaid for visual verification",
        },
        "columns": {
            "bin_index": "1-based index, increasing reconstructed energy",
            "energy_low_eVee": "derived lower edge", "energy_high_eVee": "derived upper edge",
            "energy_center_eVee": "plotted data-point energy",
            "excess": "signed central value in original plot units",
            "error_minus": "positive lower error length in original plot units",
            "error_plus": "positive upper error length in original plot units",
            "sigma_mean_derived": "optional symmetric error, arithmetic average of both lengths",
            "error_lower_endpoint": "lower endpoint value in original plot units",
            "error_upper_endpoint": "upper endpoint value in original plot units",
            "source_id": "joins this table to source identity in this provenance file",
        },
        "calibration": calibration, "coordinate_trace": traces, "checks": checks,
        "files": {
            csv_path.name: {"sha256": hashlib.sha256(data).hexdigest()},
            Path(__file__).name: {"sha256": sha256(Path(__file__))},
        },
    }
    if args.check:
        if csv_path.read_bytes() != data:
            raise ValueError("CSV differs from re-extracted source vector data")
        saved = json.loads(provenance_path.read_text(encoding="utf-8"))
        if saved["files"].pop(overlay_path.name)["sha256"] != sha256(overlay_path):
            raise ValueError("Overlay hash differs from its provenance")
        if saved != metadata:
            raise ValueError("Provenance differs from re-extraction")
        print("PASS: 19 rows, all axis anchors, point/bar matches, signed values, CSV/provenance and overlay hashes")
    else:
        if any(p.exists() for p in (csv_path, provenance_path, overlay_path)):
            raise ValueError("Refusing to overwrite existing data; use --check or back up explicitly")
        graphic = overlay(pdf, rows, calibration)
        metadata["files"][overlay_path.name] = {"sha256": hashlib.sha256(graphic).hexdigest()}
        csv_path.write_bytes(data)
        overlay_path.write_bytes(graphic)
        provenance_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Created {csv_path}")
        print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
