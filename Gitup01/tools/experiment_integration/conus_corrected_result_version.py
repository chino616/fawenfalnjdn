"""Corrected CONUS+ result view with explicit units.

This script is the corrected result *presentation layer* for
conus_plus_ge73_pheno. It does not tune physics parameters and does not modify
the production slow integrator. The correction here is the observable contract:

  - primary result: absolute expected events per 10 eVee bin at 119 kg day;
  - normalized diagnostic: events / (kg day) / 10 eVee bin;
  - official-exposure diagnostic: primary result scaled by 327 / 119.

The 327 kg day number is an exposure-only diagnostic, not an official
detector-level CONUS+ prediction.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


DATASET_ID = "conus_plus_ge73_pheno"
CURRENT_EXPOSURE_KG_DAY = 119.0
OFFICIAL_EXPOSURE_KG_DAY = 327.0
OFFICIAL_SM_EVENTS = 347.0
OFFICIAL_SM_SIGMA = 59.0
OFFICIAL_MEASURED_EVENTS = 395.0
OFFICIAL_MEASURED_SIGMA = 106.0

LEGACY_Y_DATA = np.asarray(
    [
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
    ],
    dtype=float,
)

LEGACY_Y_LOW = np.asarray(
    [
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
    ],
    dtype=float,
)

LEGACY_Y_UP = np.asarray(
    [
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
    ],
    dtype=float,
)


@dataclass(frozen=True)
class CorrectedResult:
    bin_index: int
    e_low_evee: float
    e_high_evee: float
    events_per_bin_119kgday: float

    @property
    def center_evee(self) -> float:
        return 0.5 * (self.e_low_evee + self.e_high_evee)

    @property
    def events_per_kg_day_bin(self) -> float:
        return self.events_per_bin_119kgday / CURRENT_EXPOSURE_KG_DAY

    @property
    def exposure_only_events_per_bin_327kgday(self) -> float:
        return self.events_per_bin_119kgday * OFFICIAL_EXPOSURE_KG_DAY / CURRENT_EXPOSURE_KG_DAY


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def default_run_dir(root: Path) -> Path:
    return root / "workflows" / "experiment-integration" / "runs" / DATASET_ID


def load_cached_slow_counts(path: Path) -> list[CorrectedResult]:
    rows: list[CorrectedResult] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                CorrectedResult(
                    bin_index=int(row["bin"]),
                    e_low_evee=float(row["E_low_eVee"]),
                    e_high_evee=float(row["E_high_eVee"]),
                    events_per_bin_119kgday=float(row["counts"]),
                )
            )
    if len(rows) != 19:
        raise ValueError(f"Expected 19 CONUS+ bins, got {len(rows)} from {path}")
    return rows


def recompute_slow_counts(root: Path) -> list[CorrectedResult]:
    src_path = root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from cevns_pyeft.experiments.conus.detector_response import (  # noqa: WPS433
        reco_energy_bin_edges_evee,
    )
    from cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno import (  # noqa: WPS433,E501
        slow_counts_conus_plus_ge73_pheno,
    )
    from cevns_pyeft.experiments.registry import get_experiment_spec  # noqa: WPS433

    spec = get_experiment_spec(DATASET_ID)
    payload = slow_counts_conus_plus_ge73_pheno(experiment_spec=spec)
    counts = np.asarray(payload["counts_total"], dtype=float)
    edges = np.asarray(reco_energy_bin_edges_evee(spec), dtype=float)
    if counts.size != 19 or edges.size != 20:
        raise ValueError(f"Unexpected slow result shape: counts={counts.size}, edges={edges.size}")
    return [
        CorrectedResult(
            bin_index=index + 1,
            e_low_evee=float(edges[index]),
            e_high_evee=float(edges[index + 1]),
            events_per_bin_119kgday=float(counts[index]),
        )
        for index in range(counts.size)
    ]


def build_summary(rows: list[CorrectedResult], mode: str) -> dict[str, Any]:
    total_119 = sum(row.events_per_bin_119kgday for row in rows)
    total_per_kg_day_bin = sum(row.events_per_kg_day_bin for row in rows)
    total_327 = sum(row.exposure_only_events_per_bin_327kgday for row in rows)
    return {
        "dataset": DATASET_ID,
        "input_mode": mode,
        "corrected_observable_contract": {
            "primary_observable": "expected_signal_events_per_bin",
            "primary_unit": "events per 10 eVee reconstructed-energy bin",
            "primary_exposure_kg_day": CURRENT_EXPOSURE_KG_DAY,
            "normalized_diagnostic_unit": "events per kg day per 10 eVee bin",
            "official_exposure_diagnostic_kg_day": OFFICIAL_EXPOSURE_KG_DAY,
            "warning": "327 kg day scaling is exposure-only, not an official detector-level CONUS+ prediction.",
        },
        "totals": {
            "events_per_bin_total_119kgday": total_119,
            "events_per_kg_day_bin_total": total_per_kg_day_bin,
            "exposure_only_events_total_327kgday": total_327,
            "scale_327_over_119": OFFICIAL_EXPOSURE_KG_DAY / CURRENT_EXPOSURE_KG_DAY,
            "pull_vs_official_sm_347_pm_59": (total_327 - OFFICIAL_SM_EVENTS) / OFFICIAL_SM_SIGMA,
            "pull_vs_official_measured_395_pm_106": (
                total_327 - OFFICIAL_MEASURED_EVENTS
            )
            / OFFICIAL_MEASURED_SIGMA,
        },
    }


def write_csv(path: Path, rows: list[CorrectedResult]) -> None:
    fields = [
        "bin",
        "E_low_eVee",
        "E_high_eVee",
        "E_center_eVee",
        "correct_events_per_10eVee_bin_119kgday",
        "diagnostic_events_per_kg_day_per_10eVee_bin",
        "exposure_only_events_per_10eVee_bin_327kgday",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "bin": row.bin_index,
                    "E_low_eVee": row.e_low_evee,
                    "E_high_eVee": row.e_high_evee,
                    "E_center_eVee": row.center_evee,
                    "correct_events_per_10eVee_bin_119kgday": row.events_per_bin_119kgday,
                    "diagnostic_events_per_kg_day_per_10eVee_bin": row.events_per_kg_day_bin,
                    "exposure_only_events_per_10eVee_bin_327kgday": row.exposure_only_events_per_bin_327kgday,
                }
            )


def write_figures(figures_dir: Path, rows: list[CorrectedResult]) -> list[Path]:
    import matplotlib.pyplot as plt

    figures_dir.mkdir(parents=True, exist_ok=True)
    centers = np.asarray([row.center_evee for row in rows], dtype=float)
    widths = np.asarray([row.e_high_evee - row.e_low_evee for row in rows], dtype=float)
    events_119 = np.asarray([row.events_per_bin_119kgday for row in rows], dtype=float)
    events_327 = np.asarray([row.exposure_only_events_per_bin_327kgday for row in rows], dtype=float)
    yerr = np.vstack([LEGACY_Y_DATA - LEGACY_Y_LOW, LEGACY_Y_UP - LEGACY_Y_DATA])

    outputs: list[Path] = []

    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    ax.bar(
        centers,
        events_119,
        width=widths,
        align="center",
        color="#4c78a8",
        edgecolor="#2f4d6f",
        alpha=0.55,
        label="correct theory: events/bin, 119 kg day",
    )
    ax.errorbar(
        centers,
        LEGACY_Y_DATA,
        yerr=yerr,
        fmt="s",
        color="#222222",
        markersize=4.2,
        capsize=3.0,
        label="legacy/PDF excess data",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.8)
    ax.set_xlabel("Reconstructed energy Eee [eVee]")
    ax.set_ylabel("Events per 10 eVee bin")
    ax.set_title("CONUS+ corrected primary observable")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        out = figures_dir / f"corrected_conus_primary_events_bin_119kgday.{suffix}"
        fig.savefig(out, dpi=180 if suffix == "png" else None)
        outputs.append(out)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.2), gridspec_kw={"width_ratios": [2.2, 1.0]})
    ax = axes[0]
    ax.bar(
        centers,
        events_327,
        width=widths,
        align="center",
        color="#e45756",
        edgecolor="#9b2f30",
        alpha=0.50,
        label="exposure-only theory: events/bin, 327 kg day",
    )
    ax.errorbar(
        centers,
        LEGACY_Y_DATA * OFFICIAL_EXPOSURE_KG_DAY / CURRENT_EXPOSURE_KG_DAY,
        yerr=yerr * OFFICIAL_EXPOSURE_KG_DAY / CURRENT_EXPOSURE_KG_DAY,
        fmt="s",
        color="#222222",
        markersize=4.0,
        capsize=3.0,
        label="legacy/PDF data scaled by 327/119",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.8)
    ax.set_xlabel("Reconstructed energy Eee [eVee]")
    ax.set_ylabel("Exposure-only events per 10 eVee bin")
    ax.set_title("327 kg day exposure-only spectrum")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8.0)

    total_327 = float(np.sum(events_327))
    ax = axes[1]
    labels = ["theory\n327 kg day", "official SM", "official\nmeasured"]
    values = [total_327, OFFICIAL_SM_EVENTS, OFFICIAL_MEASURED_EVENTS]
    errors = [0.0, OFFICIAL_SM_SIGMA, OFFICIAL_MEASURED_SIGMA]
    colors = ["#e45756", "#59a14f", "#f28e2b"]
    x = np.arange(len(labels), dtype=float)
    ax.bar(x, values, yerr=errors, capsize=4, color=colors, alpha=0.62, edgecolor="#333333")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Total events")
    ax.set_title("Total event scale")
    ax.grid(axis="y", alpha=0.25)
    ax.text(0, total_327 + 12.0, f"{total_327:.1f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        out = figures_dir / f"corrected_conus_exposure_diagnostic_327kgday.{suffix}"
        fig.savefig(out, dpi=180 if suffix == "png" else None)
        outputs.append(out)
    plt.close(fig)

    return outputs


def write_report(
    path: Path,
    summary: dict[str, Any],
    rows: list[CorrectedResult],
    figure_paths: list[Path],
) -> None:
    totals = summary["totals"]
    first_rows = "\n".join(
        "| {bin_index} | {e_low_evee:.0f}-{e_high_evee:.0f} | {events_per_bin_119kgday:.12g} | {events_per_kg_day_bin:.12g} | {exposure_only_events_per_bin_327kgday:.12g} |".format(
            **{
                "bin_index": row.bin_index,
                "e_low_evee": row.e_low_evee,
                "e_high_evee": row.e_high_evee,
                "events_per_bin_119kgday": row.events_per_bin_119kgday,
                "events_per_kg_day_bin": row.events_per_kg_day_bin,
                "exposure_only_events_per_bin_327kgday": row.exposure_only_events_per_bin_327kgday,
            }
        )
        for row in rows
    )
    text = f"""# Corrected CONUS+ Result Code Output

```text
DATASET: {DATASET_ID}
STATUS: CORRECTED_RESULT_VERSION_RAN
INPUT_MODE: {summary["input_mode"]}
PRODUCTION_CODE_CHANGED: no
```

## Correct Unit Contract

The correct primary result from the existing CONUS+ phenomenological
implementation is:

```text
expected_signal_events_per_bin
unit = events per 10 eVee reconstructed-energy bin
exposure = 119 kg day
```

Do not label this primary result as `kg^-1 (10 eVee)^-1`. If a normalized
diagnostic is needed, divide the absolute bin counts by the same exposure and
label it as:

```text
events / (kg day) / (10 eVee bin)
```

## Totals

| Quantity | Value |
|---|---:|
| Correct primary total, 119 kg day | {totals["events_per_bin_total_119kgday"]:.12g} |
| Normalized diagnostic total, events/(kg day bin) | {totals["events_per_kg_day_bin_total"]:.12g} |
| Exposure-only diagnostic total, 327 kg day | {totals["exposure_only_events_total_327kgday"]:.12g} |
| Scale factor 327/119 | {totals["scale_327_over_119"]:.12g} |
| Pull vs official SM 347 +/- 59 | {totals["pull_vs_official_sm_347_pm_59"]:.6g} |
| Pull vs official measured 395 +/- 106 | {totals["pull_vs_official_measured_395_pm_106"]:.6g} |

The 327 kg day result is an exposure-only diagnostic, not an official
detector-level CONUS+ prediction.

## Figures

```text
{chr(10).join(str(path) for path in figure_paths)}
```

## Bin Results

| Bin | E range [eVee] | Correct events/bin, 119 kg day | Diagnostic events/(kg day bin) | Exposure-only events/bin, 327 kg day |
|---:|---:|---:|---:|---:|
{first_rows}
"""
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script()
    run_dir = default_run_dir(root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("cached", "recompute"), default="cached")
    parser.add_argument("--run-dir", type=Path, default=run_dir)
    parser.add_argument(
        "--slow-counts",
        type=Path,
        default=run_dir / "artifacts" / "slow_bin_counts.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root_from_script()
    run_dir = args.run_dir.resolve()
    artifacts_dir = run_dir / "artifacts"
    figures_dir = run_dir / "figures"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "recompute":
        rows = recompute_slow_counts(root)
    else:
        rows = load_cached_slow_counts(args.slow_counts.resolve())

    summary = build_summary(rows, args.mode)
    csv_path = artifacts_dir / "corrected_conus_result_version.csv"
    json_path = artifacts_dir / "corrected_conus_result_version_summary.json"
    report_path = run_dir / "CORRECTED_CONUS_RESULT_VERSION.md"

    write_csv(csv_path, rows)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    figure_paths = write_figures(figures_dir, rows)
    write_report(report_path, summary, rows, figure_paths)

    print(json.dumps(summary, indent=2))
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {report_path}")
    for path in figure_paths:
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()
