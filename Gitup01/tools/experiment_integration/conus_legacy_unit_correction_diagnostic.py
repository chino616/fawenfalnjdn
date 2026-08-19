"""CONUS+ legacy plot-layer unit diagnostic.

This script is intentionally incremental and non-destructive. It reads the
already generated slow bin counts for conus_plus_ge73_pheno and compares them
with the legacy/PDF yData under two explicit unit hypotheses:

H1: yData is absolute expected/excess events per 10 eVee bin.
H2: yData follows the legacy plot label literally:
    counts / kg / (10 eVee bin).

The production CONUS implementation, experiment.yaml, and reference arrays are
not modified by this script.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DATASET = "conus_plus_ge73_pheno"
LEGACY_EXPOSURE_KG_DAY = 119.0
OFFICIAL_EXPOSURE_KG_DAY = 327.0
OFFICIAL_SM_EVENTS = 347.0
OFFICIAL_SM_SIGMA = 59.0
OFFICIAL_MEASURED_EVENTS = 395.0
OFFICIAL_MEASURED_SIGMA = 106.0

Y_DATA = [
    13.36,
    38.08,
    29.02,
    21.41,
    12.36,
    5.222,
    4.5511,
    0.527,
    9.4382,
    2.780,
    4.2655,
    -2.15,
    1.0090,
    -9.962,
    -3.68,
    -7.94,
    0.2413,
    -0.188,
    14.469,
]

Y_LOW = [
    -9.6,
    22.5,
    16.5,
    9.43,
    0.863,
    -6.2,
    -6.4,
    -10.2,
    -1.5,
    -7.2,
    -6.0,
    -12.0,
    -9.29,
    -20.0,
    -13.7,
    -18.0,
    -9.81,
    -10.0,
    4.65,
]

Y_UP = [
    36.11827057182706,
    53.891585309158536,
    41.72384937238493,
    33.62789400278941,
    23.855323105532314,
    16.71892143189214,
    16.049465364946542,
    11.067224546722443,
    20.455973965597394,
    13.08005578800558,
    14.563272896327305,
    8.625941422594138,
    11.306741050674106,
    0.09855880985590204,
    6.373593677359381,
    1.6308693630869442,
    9.82352394235241,
    9.630125523012566,
    23.810692701069286,
]


@dataclass(frozen=True)
class BinRow:
    bin_index: int
    e_low_evee: float
    e_high_evee: float
    theory_abs_119: float
    y_data: float
    y_low: float
    y_up: float

    @property
    def center_evee(self) -> float:
        return 0.5 * (self.e_low_evee + self.e_high_evee)

    @property
    def sigma_sym(self) -> float:
        return 0.5 * ((self.y_up - self.y_data) + (self.y_data - self.y_low))


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def default_run_dir(root: Path) -> Path:
    return root / "workflows" / "experiment-integration" / "runs" / DATASET


def read_slow_counts(path: Path) -> list[BinRow]:
    rows: list[BinRow] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader):
            rows.append(
                BinRow(
                    bin_index=int(row["bin"]),
                    e_low_evee=float(row["E_low_eVee"]),
                    e_high_evee=float(row["E_high_eVee"]),
                    theory_abs_119=float(row["counts"]),
                    y_data=Y_DATA[idx],
                    y_low=Y_LOW[idx],
                    y_up=Y_UP[idx],
                )
            )

    expected = len(Y_DATA)
    if len(rows) != expected:
        raise ValueError(f"slow counts has {len(rows)} bins, expected {expected}")
    return rows


def safe_chi2(residuals: Iterable[float], sigmas: Iterable[float]) -> float:
    return sum((res / sig) ** 2 for res, sig in zip(residuals, sigmas) if sig > 0.0)


def safe_rms(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        return math.nan
    return math.sqrt(sum(value * value for value in materialized) / len(materialized))


def write_comparison_csv(rows: list[BinRow], path: Path) -> None:
    fieldnames = [
        "bin",
        "E_low_eVee",
        "E_high_eVee",
        "E_center_eVee",
        "yData",
        "yLow",
        "yUp",
        "sigma_sym",
        "theory_abs_events_bin_119kgday",
        "theory_counts_per_kg_10eV_if_axis_literal",
        "theory_abs_events_bin_327kgday",
        "yData_as_abs_events_119kgday_if_axis_literal",
        "yData_as_abs_events_327kgday_if_axis_literal",
        "residual_H1_abs_events_119_minus_yData",
        "pull_H1_abs_events_119",
        "residual_H2_perkg10eV_119_minus_yData",
        "pull_H2_perkg10eV",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            theory_per_kg_bin = row.theory_abs_119 / LEGACY_EXPOSURE_KG_DAY
            theory_abs_327 = row.theory_abs_119 * OFFICIAL_EXPOSURE_KG_DAY / LEGACY_EXPOSURE_KG_DAY
            residual_h1 = row.theory_abs_119 - row.y_data
            residual_h2 = theory_per_kg_bin - row.y_data
            sigma = row.sigma_sym
            writer.writerow(
                {
                    "bin": row.bin_index,
                    "E_low_eVee": row.e_low_evee,
                    "E_high_eVee": row.e_high_evee,
                    "E_center_eVee": row.center_evee,
                    "yData": row.y_data,
                    "yLow": row.y_low,
                    "yUp": row.y_up,
                    "sigma_sym": sigma,
                    "theory_abs_events_bin_119kgday": row.theory_abs_119,
                    "theory_counts_per_kg_10eV_if_axis_literal": theory_per_kg_bin,
                    "theory_abs_events_bin_327kgday": theory_abs_327,
                    "yData_as_abs_events_119kgday_if_axis_literal": row.y_data
                    * LEGACY_EXPOSURE_KG_DAY,
                    "yData_as_abs_events_327kgday_if_axis_literal": row.y_data
                    * OFFICIAL_EXPOSURE_KG_DAY,
                    "residual_H1_abs_events_119_minus_yData": residual_h1,
                    "pull_H1_abs_events_119": residual_h1 / sigma if sigma > 0 else math.nan,
                    "residual_H2_perkg10eV_119_minus_yData": residual_h2,
                    "pull_H2_perkg10eV": residual_h2 / sigma if sigma > 0 else math.nan,
                }
            )


def build_summary(rows: list[BinRow]) -> dict[str, object]:
    theory_abs_119 = [row.theory_abs_119 for row in rows]
    y_data = [row.y_data for row in rows]
    sigmas = [row.sigma_sym for row in rows]
    theory_per_kg_bin = [value / LEGACY_EXPOSURE_KG_DAY for value in theory_abs_119]
    theory_abs_327 = [
        value * OFFICIAL_EXPOSURE_KG_DAY / LEGACY_EXPOSURE_KG_DAY
        for value in theory_abs_119
    ]
    residual_h1 = [theory - data for theory, data in zip(theory_abs_119, y_data)]
    residual_h2 = [theory - data for theory, data in zip(theory_per_kg_bin, y_data)]

    total_theory_119 = sum(theory_abs_119)
    total_y = sum(y_data)
    total_theory_per_kg_bin = sum(theory_per_kg_bin)
    total_theory_327 = sum(theory_abs_327)
    total_y_abs_119_if_axis_literal = total_y * LEGACY_EXPOSURE_KG_DAY
    total_y_abs_327_if_axis_literal = total_y * OFFICIAL_EXPOSURE_KG_DAY

    return {
        "dataset": DATASET,
        "inputs": {
            "legacy_exposure_kg_day": LEGACY_EXPOSURE_KG_DAY,
            "official_exposure_kg_day": OFFICIAL_EXPOSURE_KG_DAY,
            "bin_width_eVee": rows[0].e_high_evee - rows[0].e_low_evee,
            "num_bins": len(rows),
        },
        "totals": {
            "theory_abs_events_119kgday": total_theory_119,
            "legacy_yData_direct_sum": total_y,
            "theory_counts_per_kg_10eV_sum_if_axis_literal": total_theory_per_kg_bin,
            "theory_abs_events_327kgday_exposure_only": total_theory_327,
            "yData_abs_events_119kgday_if_axis_literal": total_y_abs_119_if_axis_literal,
            "yData_abs_events_327kgday_if_axis_literal": total_y_abs_327_if_axis_literal,
        },
        "hypothesis_tests": {
            "H1_yData_absolute_events_per_bin": {
                "dimensionally_matches_legacy_axis_label": False,
                "chi2_like_using_symmetric_y_errors": safe_chi2(residual_h1, sigmas),
                "rms_residual": safe_rms(residual_h1),
                "total_residual_theory_minus_yData": total_theory_119 - total_y,
            },
            "H2_yData_counts_per_kg_per_10eV": {
                "dimensionally_matches_legacy_axis_label": True,
                "chi2_like_using_symmetric_y_errors": safe_chi2(residual_h2, sigmas),
                "rms_residual": safe_rms(residual_h2),
                "total_residual_theory_minus_yData": total_theory_per_kg_bin - total_y,
                "implied_yData_abs_events_119kgday": total_y_abs_119_if_axis_literal,
            },
        },
        "official_exposure_diagnostic": {
            "theory_abs_events_327kgday_exposure_only": total_theory_327,
            "official_sm_events": OFFICIAL_SM_EVENTS,
            "official_sm_sigma": OFFICIAL_SM_SIGMA,
            "pull_vs_official_sm": (total_theory_327 - OFFICIAL_SM_EVENTS)
            / OFFICIAL_SM_SIGMA,
            "official_measured_events": OFFICIAL_MEASURED_EVENTS,
            "official_measured_sigma": OFFICIAL_MEASURED_SIGMA,
            "pull_vs_official_measured": (
                total_theory_327 - OFFICIAL_MEASURED_EVENTS
            )
            / OFFICIAL_MEASURED_SIGMA,
        },
        "conclusion": {
            "numerically_closer_hypothesis": "H1_yData_absolute_events_per_bin",
            "dimensionally_consistent_with_legacy_axis_label": (
                "H2_yData_counts_per_kg_per_10eV"
            ),
            "recommended_fix_scope": (
                "Fix comparison/plot-layer unit contract before changing "
                "production CONUS physics integration."
            ),
        },
    }


def write_plots(rows: list[BinRow], figures_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    centers = [row.center_evee for row in rows]
    widths = [row.e_high_evee - row.e_low_evee for row in rows]
    theory_abs_119 = [row.theory_abs_119 for row in rows]
    theory_abs_327 = [
        row.theory_abs_119 * OFFICIAL_EXPOSURE_KG_DAY / LEGACY_EXPOSURE_KG_DAY
        for row in rows
    ]
    theory_per_kg_bin = [
        row.theory_abs_119 / LEGACY_EXPOSURE_KG_DAY for row in rows
    ]
    y_data = [row.y_data for row in rows]
    yerr_low = [row.y_data - row.y_low for row in rows]
    yerr_up = [row.y_up - row.y_data for row in rows]

    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.bar(
        centers,
        theory_abs_119,
        width=widths,
        align="center",
        alpha=0.48,
        label="theory: absolute events/bin, 119 kg day",
        color="#4c78a8",
        edgecolor="#2f4d6f",
    )
    ax.plot(
        centers,
        theory_abs_327,
        color="#e45756",
        linewidth=2.0,
        marker="o",
        markersize=3.5,
        label="theory: exposure-only scaled to 327 kg day",
    )
    ax.errorbar(
        centers,
        y_data,
        yerr=[yerr_low, yerr_up],
        fmt="s",
        color="#222222",
        markersize=4,
        capsize=3,
        label="legacy/PDF yData overlaid directly",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.8)
    ax.set_xlabel("Reconstructed energy Eee [eVee]")
    ax.set_ylabel("Absolute events per 10 eVee bin")
    ax.set_title("CONUS+ direct absolute-bin comparison")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        out = figures_dir / f"legacy_unit_corrected_absolute_events.{suffix}"
        fig.savefig(out, dpi=180 if suffix == "png" else None)
        outputs.append(out)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.bar(
        centers,
        theory_per_kg_bin,
        width=widths,
        align="center",
        alpha=0.58,
        label="theory: counts/kg/(10 eVee), if axis label is literal",
        color="#59a14f",
        edgecolor="#376b31",
    )
    ax.errorbar(
        centers,
        y_data,
        yerr=[yerr_low, yerr_up],
        fmt="s",
        color="#222222",
        markersize=4,
        capsize=3,
        label="legacy/PDF yData treated as axis-literal",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.8)
    ax.set_xlabel("Reconstructed energy Eee [eVee]")
    ax.set_ylabel("Counts / kg / (10 eVee bin)")
    ax.set_title("CONUS+ axis-literal normalized comparison")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        out = figures_dir / f"legacy_unit_corrected_per_kg_bin.{suffix}"
        fig.savefig(out, dpi=180 if suffix == "png" else None)
        outputs.append(out)
    plt.close(fig)

    return outputs


def write_report(summary: dict[str, object], report_path: Path) -> None:
    totals = summary["totals"]  # type: ignore[index]
    tests = summary["hypothesis_tests"]  # type: ignore[index]
    official = summary["official_exposure_diagnostic"]  # type: ignore[index]
    h1 = tests["H1_yData_absolute_events_per_bin"]  # type: ignore[index]
    h2 = tests["H2_yData_counts_per_kg_per_10eV"]  # type: ignore[index]

    text = f"""# CONUS+ Legacy Unit Correction Diagnostic

```text
DATASET: {DATASET}
STATUS: DIAGNOSTIC_PROGRAM_RAN
SCOPE: comparison/plot-layer unit contract only
PRODUCTION_CODE_CHANGED: no
```

## Purpose

The legacy Mathematica layer multiplies the response by the full exposure before
bin integration, so its `binCounts` are absolute events per 10 eVee bin. The
same layer labels the plot as `Counts [kg^-1 (10 eVee)^-1]` and overlays yData
directly. This diagnostic keeps those two interpretations separate.

## Totals

| Quantity | Value |
|---|---:|
| Theory, absolute events/bin, 119 kg day | {totals["theory_abs_events_119kgday"]:.12g} |
| Legacy/PDF yData direct sum | {totals["legacy_yData_direct_sum"]:.12g} |
| Theory, counts/kg/(10 eVee), if axis label literal | {totals["theory_counts_per_kg_10eV_sum_if_axis_literal"]:.12g} |
| Theory, exposure-only scaled to 327 kg day | {totals["theory_abs_events_327kgday_exposure_only"]:.12g} |
| yData as absolute events at 119 kg day, if axis label literal | {totals["yData_abs_events_119kgday_if_axis_literal"]:.12g} |
| yData as absolute events at 327 kg day, if axis label literal | {totals["yData_abs_events_327kgday_if_axis_literal"]:.12g} |

## Hypothesis Comparison

| Hypothesis | Unit interpretation | Dimensionally matches legacy axis label | Chi2-like | RMS residual | Total residual |
|---|---|---:|---:|---:|---:|
| H1 | yData = absolute events/bin | no | {h1["chi2_like_using_symmetric_y_errors"]:.6g} | {h1["rms_residual"]:.6g} | {h1["total_residual_theory_minus_yData"]:.6g} |
| H2 | yData = counts/kg/(10 eVee) | yes | {h2["chi2_like_using_symmetric_y_errors"]:.6g} | {h2["rms_residual"]:.6g} | {h2["total_residual_theory_minus_yData"]:.6g} |

## Official Exposure Diagnostic

| Quantity | Value |
|---|---:|
| Theory scaled from 119 to 327 kg day | {official["theory_abs_events_327kgday_exposure_only"]:.12g} |
| Official SM benchmark | {official["official_sm_events"]:.12g} +/- {official["official_sm_sigma"]:.12g} |
| Pull vs official SM | {official["pull_vs_official_sm"]:.6g} |
| Official measured count | {official["official_measured_events"]:.12g} +/- {official["official_measured_sigma"]:.12g} |
| Pull vs official measured | {official["pull_vs_official_measured"]:.6g} |

## Interpretation

H1 is numerically much closer to the existing legacy/PDF yData overlay, but it
does not match the old plot axis label. H2 matches the old axis label
dimensionally, but it implies a yData total of
{totals["yData_abs_events_119kgday_if_axis_literal"]:.12g} absolute events at
119 kg day, which is incompatible with the current theory scale and the
published 327 kg day benchmark scale.

The corrected next step is therefore to fix the comparison and plotting unit
contract first: either plot absolute events/bin and label it as such, or divide
all absolute bin counts by the same exposure before using a normalized
counts/kg/(10 eVee) axis. This diagnostic does not justify changing the
production physics integration by itself.
"""
    report_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    root = repo_root_from_script()
    run_dir = default_run_dir(root)
    parser.add_argument("--run-dir", type=Path, default=run_dir)
    parser.add_argument(
        "--slow-counts",
        type=Path,
        default=run_dir / "artifacts" / "slow_bin_counts.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    artifacts_dir = run_dir / "artifacts"
    figures_dir = run_dir / "figures"
    rows = read_slow_counts(args.slow_counts.resolve())
    summary = build_summary(rows)

    csv_path = artifacts_dir / "legacy_unit_corrected_comparison.csv"
    json_path = artifacts_dir / "legacy_unit_corrected_summary.json"
    report_path = run_dir / "LEGACY_UNIT_CORRECTION_RESULTS.md"

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    write_comparison_csv(rows, csv_path)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    figure_paths = write_plots(rows, figures_dir)
    write_report(summary, report_path)

    print(json.dumps(summary, indent=2))
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {report_path}")
    for path in figure_paths:
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()
