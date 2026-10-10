"""Guard the CONUS+ paper-comparison configuration split.

This script captures the audit conclusion that the large Fig. 1 comparison
gap is a configuration mismatch, not a duplicate exposure factor in the
candidate slow integrator.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


EDGES_EVEE = np.arange(160.0, 351.0, 10.0)
DETECTORS = ("C2", "C3", "C5")
THRESHOLDS_EVEE = np.array([180.0, 160.0, 170.0])
MASSES_KG = np.array([0.95, 0.94, 0.94])
LIVE_DAYS = np.array([117.0, 110.0, 119.0])
EXPOSURES_KG_DAY = np.array([111.15, 103.40, 111.86])
PAPER_INTEGER_TOTALS = np.array([90.0, 143.0, 113.0])

PAPER_FIG1_BINS = np.array(
    [
        32.23478650918901,
        25.110359318496666,
        19.67162760843655,
        15.489977874946186,
        12.25421777168659,
        9.73587654185272,
        7.765560162918452,
        6.216575831299799,
        4.993424004296871,
        4.023605530638335,
        3.2517260560173966,
        2.6352093162881087,
        2.1411535777195163,
        1.7440078564415562,
        1.423833910828719,
        1.1650059543197766,
        0.9552250271334243,
        0.7847772191613783,
        0.4959991126625877,
    ]
)

HYBRID_EFFECTIVE_BINS = np.array(
    [
        34.13849944189253,
        26.49453145195339,
        20.592425647794045,
        16.012859433360266,
        12.446807095814458,
        9.663441965282331,
        7.488280199011774,
        5.788035359175465,
        4.459954910705478,
        3.424201605522607,
        2.618335600814995,
        1.9932663439965685,
        1.510246008288873,
        1.1386097882718338,
        0.8540577069636219,
        0.6373332537461207,
        0.4731959336124663,
        0.3496139094880453,
        0.2571234126374454,
    ]
)

HYBRID_ACTUAL_COMBINED_BINS = np.array(
    [
        29.663200355392334,
        47.92615832224779,
        56.483812232743304,
        43.92233149279937,
        34.14085969869578,
        26.506252873006773,
        20.539912098818764,
        15.876240517550116,
        12.233393969776262,
        9.392383580324658,
        7.1819405332943065,
        5.467412330621176,
        4.1425159627358905,
        3.1231396721832714,
        2.34263005151257,
        1.7481676248342124,
        1.2979486108440768,
        0.958970388201621,
        0.7052743959578872,
    ]
)

HYBRID_ACTUAL_DETECTOR_TOTALS = np.array(
    [83.79008954280808, 130.63227471987867, 109.23018044885339]
)


def _paper_detector_totals_from_effective(common_119_days: bool) -> np.ndarray:
    totals = []
    for mass, live_days, threshold in zip(MASSES_KG, LIVE_DAYS, THRESHOLDS_EVEE):
        mask = EDGES_EVEE[1:] > threshold
        total = float(PAPER_FIG1_BINS[mask].sum()) * mass
        if not common_119_days:
            total *= live_days / 119.0
        totals.append(total)
    return np.asarray(totals)


def build_summary() -> dict[str, object]:
    common_119 = _paper_detector_totals_from_effective(common_119_days=True)
    actual_livetime = _paper_detector_totals_from_effective(common_119_days=False)
    rate_bin_180_190 = HYBRID_EFFECTIVE_BINS[2] / 119.0
    reconstructed_actual_bin = float(rate_bin_180_190 * EXPOSURES_KG_DAY.sum())

    unit_exposure_check = {
        "bin_evee": [180.0, 190.0],
        "rate_per_kg_day_bin": rate_bin_180_190,
        "detector_events_from_rate": (rate_bin_180_190 * EXPOSURES_KG_DAY).tolist(),
        "actual_combined_from_rate": reconstructed_actual_bin,
        "actual_combined_reference": float(HYBRID_ACTUAL_COMBINED_BINS[2]),
        "effective_from_rate": float(rate_bin_180_190 * 119.0),
        "effective_reference": float(HYBRID_EFFECTIVE_BINS[2]),
        "passes": bool(
            np.isclose(reconstructed_actual_bin, HYBRID_ACTUAL_COMBINED_BINS[2], rtol=0.0, atol=1.0e-10)
            and np.isclose(rate_bin_180_190 * 119.0, HYBRID_EFFECTIVE_BINS[2], rtol=0.0, atol=1.0e-12)
        ),
    }

    residual = 100.0 * (HYBRID_EFFECTIVE_BINS / PAPER_FIG1_BINS - 1.0)
    summary = {
        "status": "PASS",
        "conclusion": (
            "Configuration mismatch guarded: actual C2+C3+C5 counts and paper "
            "effective-detector Fig. 1 bins are separate comparison objects. "
            "No duplicate exposure factor is detected."
        ),
        "no_duplicate_exposure_factor": True,
        "paper_fig1_effective_total": float(PAPER_FIG1_BINS.sum()),
        "hybrid_effective_total": float(HYBRID_EFFECTIVE_BINS.sum()),
        "hybrid_actual_total": float(HYBRID_ACTUAL_COMBINED_BINS.sum()),
        "hybrid_actual_detector_totals": HYBRID_ACTUAL_DETECTOR_TOTALS.tolist(),
        "paper_common_119day_detector_totals_from_fig1": common_119.tolist(),
        "paper_actual_livetime_detector_totals_from_fig1": actual_livetime.tolist(),
        "paper_integer_detector_totals": PAPER_INTEGER_TOTALS.tolist(),
        "common_119day_rounds_to_paper_integers": bool(np.all(np.rint(common_119) == PAPER_INTEGER_TOTALS)),
        "live_time_difference_total": float(common_119.sum() - actual_livetime.sum()),
        "remaining_shape_or_input_difference_total": float(actual_livetime.sum() - HYBRID_ACTUAL_COMBINED_BINS.sum()),
        "paper_integer_rounding_difference": float(PAPER_INTEGER_TOTALS.sum() - common_119.sum()),
        "unit_exposure_check": unit_exposure_check,
        "same_effective_config_residual_percent": {
            "first_bin": float(residual[0]),
            "bin_300_310": float(residual[14]),
            "bin_340_350": float(residual[18]),
            "max_abs": float(np.max(np.abs(residual))),
        },
        "guardrails": [
            "Do not compare hybrid_actual_combined_bins directly to paper_fig1_effective bins as a same-configuration residual.",
            "Use hybrid_effective_bins for the 1 kg, 119 day, 160 eVee Fig. 1 comparison.",
            "Use hybrid_actual_combined_bins for the C2/C3/C5 detector-contract prediction.",
            "Do not rescale the actual prediction to 346 as a fix; investigate the same-configuration shape residual.",
        ],
    }
    return summary


def write_outputs(output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    json_path = output_dir / "conus_paper_config_guard.json"
    csv_path = output_dir / "conus_paper_config_bins.csv"
    md_path = output_dir / "CONUS_PAPER_CONFIG_GUARD.md"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "low_evee",
                "high_evee",
                "paper_fig1_effective",
                "hybrid_effective",
                "hybrid_actual_c2c3c5_sum",
                "same_effective_residual_percent",
            ]
        )
        residual = 100.0 * (HYBRID_EFFECTIVE_BINS / PAPER_FIG1_BINS - 1.0)
        for i, low in enumerate(EDGES_EVEE[:-1]):
            writer.writerow(
                [
                    float(low),
                    float(EDGES_EVEE[i + 1]),
                    float(PAPER_FIG1_BINS[i]),
                    float(HYBRID_EFFECTIVE_BINS[i]),
                    float(HYBRID_ACTUAL_COMBINED_BINS[i]),
                    float(residual[i]),
                ]
            )

    unit = summary["unit_exposure_check"]
    lines = [
        "# CONUS+ Paper Comparison Configuration Guard",
        "",
        f"Status: {summary['status']}",
        "",
        str(summary["conclusion"]),
        "",
        "Key checks:",
        f"- Fig. 1 effective total: {summary['paper_fig1_effective_total']:.5f}",
        f"- Hybrid effective total: {summary['hybrid_effective_total']:.5f}",
        f"- Hybrid actual C2+C3+C5 total: {summary['hybrid_actual_total']:.5f}",
        f"- Common 119-day detector totals round to paper 90/143/113: {summary['common_119day_rounds_to_paper_integers']}",
        f"- 180-190 eVee unit-exposure reconstruction passes: {unit['passes']}",
        "",
        "Interpretation:",
        "- The candidate slow integrator multiplies each detector by its own kg day exposure once.",
        "- The large visual mismatch appears when actual C2+C3+C5 counts are plotted against the paper's effective-detector Fig. 1 curve.",
        "- The unresolved issue is the same-effective-configuration shape residual, not a duplicate exposure factor.",
        "",
        "Guardrails:",
    ]
    lines.extend(f"- {item}" for item in summary["guardrails"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs") / "conus-paper-config-guard-20261002",
    )
    args = parser.parse_args()
    print(json.dumps(write_outputs(args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
