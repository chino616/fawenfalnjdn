"""CONUS legacy normalization forensic audit.

This is an incremental, read-only diagnostic builder for the
conus_plus_ge73_pheno workflow run. It does not modify production physics code,
experiment metadata, reference arrays, statistics code, or response data.

Outputs:
  workflows/experiment-integration/runs/conus_plus_ge73_pheno/
    LEGACY_NORMALIZATION_FORENSIC_AUDIT.md
    artifacts/legacy_normalization_forensic_summary.json
    artifacts/legacy_normalization_forensic_evidence.csv
    artifacts/legacy_normalization_shape_comparison.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
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
OFFICIAL_ACTIVE_MASS_APPROX_KG = 2.83

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

TERMS = [
    "119",
    "exposure",
    "exposureKgDay",
    "liveTime",
    "days",
    "kg",
    "kg day",
    "binCounts",
    "BinCounts",
    "binHeight",
    "yData",
    "sigmaData",
    "Rexp",
    "Counts",
    "kg^-1",
    "10 eVee",
    "chi2",
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
    if len(rows) != len(Y_DATA):
        raise ValueError(f"slow counts has {len(rows)} bins, expected {len(Y_DATA)}")
    return rows


def cumulative(values: Iterable[float]) -> list[float]:
    total = 0.0
    result: list[float] = []
    for value in values:
        total += value
        result.append(total)
    return result


def rms(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        return math.nan
    return math.sqrt(sum(value * value for value in materialized) / len(materialized))


def chi2_like(residuals: Iterable[float], sigmas: Iterable[float]) -> float:
    return sum((res / sig) ** 2 for res, sig in zip(residuals, sigmas) if sig > 0)


def relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def read_text_lossy(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def collect_line_hits(path: Path, terms: list[str], root: Path) -> list[dict[str, object]]:
    text = read_text_lossy(path)
    hits: list[dict[str, object]] = []
    lowered_terms = [(term, term.lower()) for term in terms]
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        matched = [term for term, low in lowered_terms if low in lowered]
        if matched:
            hits.append(
                {
                    "source": relative_path(path, root),
                    "line": line_no,
                    "terms": "; ".join(matched),
                    "snippet": line.strip()[:500],
                }
            )
    return hits


def legacy_hit_priority(hit: dict[str, object]) -> tuple[int, int]:
    snippet = str(hit.get("snippet", ""))
    terms = str(hit.get("terms", ""))
    line = int(hit.get("line", 0) or 0)
    important = [
        "CreateGeDetectorResponse",
        "exposureKgDay",
        "expoFactor",
        "nucleiPerKg",
        "secPerDay",
        "Make_dNdEreco",
        "dNdEreco",
        "BinCounts",
        "binCountsFast",
        "CreateGeDetectorResponse[CONUSiso,119",
        "CreateGeDetectorResponse[iso,119",
    ]
    if any(token in snippet for token in important):
        return (0, line)
    if "BinCounts" in terms or "exposure" in terms or "exposureKgDay" in terms:
        return (1, line)
    if 2420 <= line <= 2520:
        return (2, line)
    return (3, line)


def collect_ydata_provenance(root: Path, pdf_text: str) -> list[dict[str, object]]:
    candidates = [
        root / "data" / "experiments" / "external" / "user_mathematica",
        root / "docs" / "CONUS_docs",
        root / "workflows" / "experiment-integration" / "runs" / DATASET,
        root / "mdGPT",
        root / "tools" / "experiment_integration",
        root / "data" / "experiments",
        root / "src",
    ]
    exact_needles = ["13.36", "38.08", "29.02", "21.41", "4.5511", "9.4382"]
    records: list[dict[str, object]] = []
    for base in candidates:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".txt", ".md", ".py", ".csv", ".yaml", ".yml", ".json"}:
                continue
            if path.stat().st_size > 3_000_000:
                continue
            text = read_text_lossy(path)
            count = sum(1 for needle in exact_needles if needle in text)
            if count >= 3:
                line_numbers = []
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if any(needle in line for needle in exact_needles):
                        line_numbers.append(line_no)
                records.append(
                    {
                        "source": relative_path(path, root),
                        "matched_anchor_count": count,
                        "line_numbers": ";".join(str(n) for n in line_numbers[:12]),
                        "classification": classify_ydata_source(path, root),
                    }
                )
    pdf_count = sum(1 for needle in exact_needles if needle in pdf_text)
    if pdf_count >= 3:
        records.append(
            {
                "source": "docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf",
                "matched_anchor_count": pdf_count,
                "line_numbers": "pdf text extraction",
                "classification": "current PDF table; secondary interpretation document",
            }
        )
    return records


def classify_ydata_source(path: Path, root: Path) -> str:
    rel = relative_path(path, root)
    if "external/user_mathematica" in rel:
        return "legacy Mathematica source candidate"
    if rel.endswith("00_INPUT_INVENTORY.md"):
        return "workflow intake transcription"
    if "backup_pre_phase1" in rel:
        return "workflow backup transcription"
    if rel.endswith("LEGACY_UNIT_CORRECTION_RESULTS.md"):
        return "derived diagnostic report"
    if rel.endswith("legacy_unit_corrected_comparison.csv"):
        return "derived diagnostic table"
    if rel.endswith("conus_legacy_unit_correction_diagnostic.py"):
        return "hard-coded diagnostic constants"
    if rel.startswith("mdGPT/"):
        return "task prompt"
    return "local occurrence"


def extract_pdf_text(pdf_path: Path) -> tuple[str, str]:
    if not pdf_path.exists():
        return "", "missing"
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(pdf_path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text, f"ok; pages={len(reader.pages)}"
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        return "", f"failed: {exc}"


def pdf_hit_count(text: str, pattern: str) -> int:
    return len(re.findall(re.escape(pattern), text, flags=re.IGNORECASE))


def build_shape_rows(rows: list[BinRow]) -> list[dict[str, object]]:
    theory = [row.theory_abs_119 for row in rows]
    data = [row.y_data for row in rows]
    total_theory = sum(theory)
    total_data = sum(data)
    cum_theory = cumulative(theory)
    cum_data = cumulative(data)
    shape_rows = []
    for row, c_theory, c_data in zip(rows, cum_theory, cum_data):
        shape_rows.append(
            {
                "bin": row.bin_index,
                "E_low_eVee": row.e_low_evee,
                "E_high_eVee": row.e_high_evee,
                "theory_abs_events_bin_119kgday": row.theory_abs_119,
                "yData": row.y_data,
                "theory_minus_yData": row.theory_abs_119 - row.y_data,
                "theory_over_yData": (
                    row.theory_abs_119 / row.y_data if row.y_data != 0 else math.nan
                ),
                "theory_shape_fraction": row.theory_abs_119 / total_theory,
                "yData_shape_fraction": row.y_data / total_data,
                "shape_fraction_difference": (
                    row.theory_abs_119 / total_theory - row.y_data / total_data
                ),
                "cumulative_theory": c_theory,
                "cumulative_yData": c_data,
                "cumulative_theory_fraction": c_theory / total_theory,
                "cumulative_yData_fraction": c_data / total_data,
            }
        )
    return shape_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[BinRow], pdf_text: str, pdf_status: str) -> dict[str, object]:
    theory = [row.theory_abs_119 for row in rows]
    data = [row.y_data for row in rows]
    sigmas = [row.sigma_sym for row in rows]
    residuals = [a - b for a, b in zip(theory, data)]
    theory_per_kg_bin = [value / LEGACY_EXPOSURE_KG_DAY for value in theory]

    total_theory = sum(theory)
    total_data = sum(data)
    exposure_scaled = total_theory * OFFICIAL_EXPOSURE_KG_DAY / LEGACY_EXPOSURE_KG_DAY
    residual_ratio_to_official = OFFICIAL_SM_EVENTS / exposure_scaled

    return {
        "dataset": DATASET,
        "pdf_text_extraction_status": pdf_status,
        "pdf_hit_counts": {
            "119": pdf_hit_count(pdf_text, "119"),
            "327": pdf_hit_count(pdf_text, "327"),
            "347": pdf_hit_count(pdf_text, "347"),
            "395": pdf_hit_count(pdf_text, "395"),
            "kg day": pdf_hit_count(pdf_text, "kg day"),
            "Rexp": pdf_hit_count(pdf_text, "Rexp"),
            "background-subtracted": pdf_hit_count(pdf_text, "background-subtracted"),
        },
        "totals": {
            "theory_abs_events_119kgday": total_theory,
            "yData_direct_sum": total_data,
            "absolute_difference_theory_minus_yData": total_theory - total_data,
            "relative_difference_vs_yData": (total_theory - total_data) / total_data,
            "ratio_theory_over_yData": total_theory / total_data,
            "theory_counts_per_kg_10eV_sum_if_axis_literal": sum(theory_per_kg_bin),
            "yData_abs_events_119kgday_if_axis_literal": total_data
            * LEGACY_EXPOSURE_KG_DAY,
            "exposure_only_scaled_to_327kgday": exposure_scaled,
            "official_effective_mass_327_over_119": OFFICIAL_EXPOSURE_KG_DAY
            / LEGACY_EXPOSURE_KG_DAY,
            "official_active_mass_approx_kg": OFFICIAL_ACTIVE_MASS_APPROX_KG,
            "official_sm_events": OFFICIAL_SM_EVENTS,
            "official_measured_events": OFFICIAL_MEASURED_EVENTS,
            "pull_vs_official_sm": (exposure_scaled - OFFICIAL_SM_EVENTS)
            / OFFICIAL_SM_SIGMA,
            "pull_vs_official_measured": (
                exposure_scaled - OFFICIAL_MEASURED_EVENTS
            )
            / OFFICIAL_MEASURED_SIGMA,
            "residual_ratio_347_over_exposure_scaled": residual_ratio_to_official,
            "residual_percent_change_to_347": (residual_ratio_to_official - 1.0)
            * 100.0,
        },
        "shape_metrics": {
            "chi2_like_absolute_events_using_y_errors": chi2_like(residuals, sigmas),
            "rms_residual_absolute_events": rms(residuals),
            "rms_shape_fraction_difference": rms(
                [
                    a / total_theory - b / total_data
                    for a, b in zip(theory, data)
                ]
            ),
        },
        "classification": {
            "is_150494_numerically_wrong": "NO within the current legacy/PDF/Python contract",
            "is_150494_unit_semantics_wrong": "NO for absolute events/bin at 119 kg day; YES if plotted as kg^-1 per 10 eVee",
            "is_yData_absolute_events_per_bin": "LIKELY, but provenance remains secondary/local",
            "is_old_mathematica_y_axis_label_correct": "UNLIKELY",
            "is_119_live_time_or_exposure": "best supported in executable code as exposureKgDay; physically also equals reactor-on days for a 1 kg normalization",
            "is_current_python_faithful_to_current_pdf": "YES",
            "is_current_pdf_faithful_to_legacy_notebook": "PARTIAL",
            "can_legacy_model_be_claimed_as_official_conus_plus": "NO",
        },
    }


def evidence_rows() -> list[dict[str, str]]:
    return [
        {
            "claim": "119 = kg day",
            "evidence_for": "Mathematica function parameter is exposureKgDay and expoFactor = nucleiPerKg * exposureKgDay * secPerDay; PDF writes X = nGe73/kg * 119 kg day * 86400 s/day.",
            "evidence_against": "Official facts also cite 119 reactor-on days and 327 kg day total exposure; variable name alone is not decisive.",
            "classification": "BEST_SUPPORTED_FOR_EXECUTABLE_CONTRACT",
        },
        {
            "claim": "119 = days",
            "evidence_for": "Official CONUS+ reactor operation is 119 days; 327/119 gives an effective active mass scale.",
            "evidence_against": "Executable Mathematica multiplies by nucleiPerKg before multiplying by 119 and secPerDay, so the numeric contract is kg day or 1 kg * 119 days.",
            "classification": "POSSIBLE_PHYSICAL_PROVENANCE_NOT_DIRECT_CODE_UNIT",
        },
        {
            "claim": "binCounts = absolute events/bin",
            "evidence_for": "dNdEreco includes expoFactor before integration; BinCounts integrates dNdEreco over reconstructed energy.",
            "evidence_against": "Old plot label reportedly uses kg^-1 (10 eVee)^-1.",
            "classification": "STRONGLY_SUPPORTED",
        },
        {
            "claim": "binCounts = counts/kg/bin",
            "evidence_for": "Only supported by the written plot label if read literally.",
            "evidence_against": "No division by exposure is present after bin integration in the located legacy chain.",
            "classification": "UNLIKELY",
        },
        {
            "claim": "yData = absolute events/bin",
            "evidence_for": "Direct sum 132.8131 is numerically close to theory 150.494; PDF labels the table as background-subtracted excess counts.",
            "evidence_against": "Original external provenance of the 19 values was not proven beyond the current PDF/workflow transcription.",
            "classification": "LIKELY_BUT_PROVENANCE_INCOMPLETE",
        },
        {
            "claim": "yData = counts/kg/bin",
            "evidence_for": "Old y-axis label could be read that way.",
            "evidence_against": "Literal conversion implies 15804.7589 events at 119 kg day, incompatible with the published event scale.",
            "classification": "PHYSICALLY_INCOMPATIBLE_UNLESS_MISSING_FACTOR_EXISTS",
        },
        {
            "claim": "old y-axis label is correct",
            "evidence_for": "Reported label text.",
            "evidence_against": "It conflicts with the executable exposure multiplication and with event-scale diagnostics.",
            "classification": "UNLIKELY",
        },
        {
            "claim": "old y-axis label is wrong",
            "evidence_for": "Executable chain produces absolute events/bin; yData direct scale matches absolute counts much better than counts/kg/bin.",
            "evidence_against": "The exact original plotting cell with binHeight was not independently recovered in this run.",
            "classification": "LIKELY",
        },
        {
            "claim": "current PDF exposure interpretation is correct",
            "evidence_for": "It matches the executable formula if 119 is a 1 kg * 119 day effective exposure.",
            "evidence_against": "It may overstate the link to official CONUS+ 327 kg day detector-level exposure.",
            "classification": "PARTIAL",
        },
        {
            "claim": "current Python normalization is correct",
            "evidence_for": "It reproduces the current PDF/legacy contract and yields absolute events/bin.",
            "evidence_against": "That does not make it the official detector-level CONUS+ prediction.",
            "classification": "CORRECT_FOR_CURRENT_CONTRACT",
        },
    ]


def write_evidence_csv(path: Path, rows: list[dict[str, str]]) -> None:
    write_csv(path, rows)


def write_report(
    path: Path,
    summary: dict[str, object],
    evidence: list[dict[str, str]],
    line_hits: list[dict[str, object]],
    ydata_provenance: list[dict[str, object]],
    shape_rows: list[dict[str, object]],
) -> None:
    totals = summary["totals"]  # type: ignore[index]
    shape = summary["shape_metrics"]  # type: ignore[index]
    classification = summary["classification"]  # type: ignore[index]
    pdf_hits = summary["pdf_hit_counts"]  # type: ignore[index]

    top_hits = sorted(line_hits, key=legacy_hit_priority)[:28]
    legacy_hit_table = "\n".join(
        f"| {hit['source']} | {hit['line']} | {hit['terms']} | `{hit['snippet']}` |"
        for hit in top_hits
    )
    provenance_table = "\n".join(
        f"| {row['source']} | {row['matched_anchor_count']} | {row['line_numbers']} | {row['classification']} |"
        for row in ydata_provenance
    )
    evidence_table = "\n".join(
        f"| {row['claim']} | {row['evidence_for']} | {row['evidence_against']} | {row['classification']} |"
        for row in evidence
    )
    first_shape_rows = "\n".join(
        "| {bin} | {theory_abs_events_bin_119kgday:.6g} | {yData:.6g} | {theory_minus_yData:.6g} | {theory_over_yData:.6g} | {cumulative_theory_fraction:.6g} | {cumulative_yData_fraction:.6g} |".format(
            **row
        )
        for row in shape_rows[:10]
    )

    report = f"""# Legacy Normalization Forensic Audit: CONUS+

```text
DATASET: {DATASET}
STATUS: FORENSIC_AUDIT_GENERATED
PRODUCTION_CODE_CHANGED: no
REFERENCE_ARRAYS_CHANGED: no
EXPERIMENT_YAML_CHANGED: no
```

## Primary Finding

The most likely problem is not the numerical CEvNS integration itself. The
executable legacy/PDF/Python chain is internally consistent if the result is
read as absolute events per 10 eVee bin for a 119 kg day, or equivalently
1 kg * 119 day, phenomenological exposure.

The weak point is the written observable convention: the old Mathematica axis
label `Counts [kg^-1 (10 eVee)^-1]` is not compatible with the located
executable normalization unless an additional, currently undocumented,
normalization factor is applied.

```text
IS 150.494 NUMERICALLY WRONG?
{classification["is_150494_numerically_wrong"]}

IS 150.494 UNIT/SEMANTICS WRONG?
{classification["is_150494_unit_semantics_wrong"]}

IS yData ABSOLUTE EVENTS/BIN?
{classification["is_yData_absolute_events_per_bin"]}

IS THE OLD MATHEMATICA Y-AXIS LABEL CORRECT?
{classification["is_old_mathematica_y_axis_label_correct"]}

IS 119 A LIVE-TIME OR AN EXPOSURE?
{classification["is_119_live_time_or_exposure"]}

IS CURRENT PYTHON A FAITHFUL IMPLEMENTATION OF THE CURRENT PDF?
{classification["is_current_python_faithful_to_current_pdf"]}

IS THE CURRENT PDF A FAITHFUL PHYSICAL INTERPRETATION OF THE LEGACY NOTEBOOK?
{classification["is_current_pdf_faithful_to_legacy_notebook"]}

CAN THE LEGACY MODEL BE CLAIMED AS OFFICIAL CONUS+?
{classification["can_legacy_model_be_claimed_as_official_conus_plus"]}
```

## Numerical Diagnostics

| Quantity | Value |
|---|---:|
| Current theory, absolute events/bin, 119 kg day | {totals["theory_abs_events_119kgday"]:.12g} |
| Legacy/PDF yData direct sum | {totals["yData_direct_sum"]:.12g} |
| Theory - yData | {totals["absolute_difference_theory_minus_yData"]:.12g} |
| Relative difference vs yData | {totals["relative_difference_vs_yData"]:.6%} |
| Ratio theory/yData | {totals["ratio_theory_over_yData"]:.12g} |
| Theory if divided by 119, counts/kg/(10 eVee) total | {totals["theory_counts_per_kg_10eV_sum_if_axis_literal"]:.12g} |
| yData implied absolute events at 119 kg day if axis literal | {totals["yData_abs_events_119kgday_if_axis_literal"]:.12g} |
| Exposure-only diagnostic scaled to 327 kg day | {totals["exposure_only_scaled_to_327kgday"]:.12g} |
| Pull vs official SM 347 +/- 59 | {totals["pull_vs_official_sm"]:.6g} |
| Pull vs official measured 395 +/- 106 | {totals["pull_vs_official_measured"]:.6g} |
| 327/119 effective active mass | {totals["official_effective_mass_327_over_119"]:.12g} kg |
| Approx official active mass cited in prompt | {totals["official_active_mass_approx_kg"]:.12g} kg |
| Required ratio 347 / exposure-only diagnostic | {totals["residual_ratio_347_over_exposure_scaled"]:.12g} |
| Required residual percent change to 347 | {totals["residual_percent_change_to_347"]:.6g}% |

The statement required by the prompt is therefore:

```text
THE LEGACY AXIS LABEL IS PHYSICALLY INCOMPATIBLE WITH THE PUBLISHED EVENT SCALE
```

unless a missing documented normalization factor is later found.

## Unit Chain

Located executable chain:

```text
dPhi/dE_nu
  x dSigma/dT
  -> S(T), rate per target nucleus per recoil energy

nucleiPerKg = N_A * 1000 / A
expoFactor = nucleiPerKg * exposureKgDay * secPerDay

dNdEreco(Ereco)
  = expoFactor * integral dT S(T) R(Ereco | T)

binCounts
  = integral over reconstructed energy dEreco dNdEreco(Ereco)
```

Interpretation A, `119 = 119 kg day`:

```text
dNdT      -> events / keVnr
dNdEreco  -> events / eVee
binCounts -> absolute events per bin
```

Interpretation B, `119 = 119 day`:

```text
nucleiPerKg * 119 day * secPerDay
```

is equivalent to a 1 kg detector followed for 119 days. The resulting plotted
quantity is still absolute events for that effective 1 kg exposure. It is not
counts/kg/bin unless the final result is divided by mass/exposure.

## Legacy Code Evidence

| Source | Line | Matched terms | Snippet |
|---|---:|---|---|
{legacy_hit_table}

Full local evidence hits are written to
`artifacts/legacy_normalization_forensic_evidence.csv`.

## yData Provenance

The exact 19-value provenance is not fully proven from the original
Mathematica source in this run. The values are found in the current PDF text
extraction and workflow transcription, and in derived diagnostic files. That
supports the current dataset input, but it does not prove the original external
paper/table/digitization source.

```text
YDATA_UNIT = LIKELY_ABSOLUTE_EVENTS_PER_BIN_BUT_ORIGINAL_PROVENANCE_UNRESOLVED
```

| Source | Matched anchor count | Lines | Classification |
|---|---:|---|---|
{provenance_table}

PDF extraction status: `{summary["pdf_text_extraction_status"]}`.

PDF hit counts:

| Pattern | Hits |
|---|---:|
| 119 | {pdf_hits["119"]} |
| 327 | {pdf_hits["327"]} |
| 347 | {pdf_hits["347"]} |
| 395 | {pdf_hits["395"]} |
| kg day | {pdf_hits["kg day"]} |
| Rexp | {pdf_hits["Rexp"]} |
| background-subtracted | {pdf_hits["background-subtracted"]} |

## Shape Check

| Bin | Theory | yData | Theory - yData | Theory / yData | Cum theory frac | Cum yData frac |
|---:|---:|---:|---:|---:|---:|---:|
{first_shape_rows}

Summary:

| Metric | Value |
|---|---:|
| Chi2-like using symmetric y errors | {shape["chi2_like_absolute_events_using_y_errors"]:.6g} |
| RMS residual, absolute events | {shape["rms_residual_absolute_events"]:.6g} |
| RMS normalized-shape fraction difference | {shape["rms_shape_fraction_difference"]:.6g} |

The arrays are numerically compatible with the same class of observable
(`absolute events/bin`) at the broad diagnostic level, but the bin-by-bin shape
is not a fit result and should not be interpreted as a physics preference.

## Three Separate Normalization Questions

### A. Legacy plot observable

The executable chain plots/integrates absolute bin counts if `binCounts` is used
directly. If the axis says `kg^-1 (10 eVee)^-1`, the label is likely inherited
or stale.

### B. Legacy theory normalization

The theory normalization uses `nucleiPerKg * exposureKgDay * secPerDay`. The
numeric value 119 can be read as 119 kg day, or as a 1 kg detector for 119
reactor-on days. Either way, the output after bin integration is absolute
events for that effective exposure.

### C. Official CONUS+ benchmark

The 413.543286872 value is only an exposure-only diagnostic:

```text
150.494345987 * 327 / 119
```

It is not a new official detector-level prediction.

## Interpretation Hierarchy

### Level 1: raw legacy Mathematica semantics

The located code applies exposure before reconstructed-energy integration and
therefore produces absolute events/bin. The parameter name supports kg day, but
the number 119 also matches reactor-on days in official prose.

### Level 2: current PDF interpretation

The PDF makes the 119 kg day interpretation explicit and treats `Rexp_i` as
background-subtracted excess counts. This is coherent as a phenomenological
dataset contract, but it may be too precise as a statement about official
CONUS+ detector exposure.

### Level 3: current Python implementation

Python is faithful to the current PDF/legacy executable contract: it returns
absolute expected events per bin. No evidence here requires changing the
production integrator.

### Level 4: exposure-corrected diagnostic

Scaling to 327 kg day gives 413.543286872 events. This lies 1.12785 sigma above
the official SM benchmark and 0.174937 sigma above the official measured central
value. That only shows broad event-scale compatibility after exposure scaling.

### Level 5: official CONUS+ detector-level result

Official CONUS+ uses detector-specific exposure, response, efficiency,
thresholds, isotope mixture, source and analysis details. The legacy pure-Ge73
phenomenological model cannot be claimed as the official detector-level model.

## Evidence Table

| Claim | Evidence for | Evidence against | Classification |
|---|---|---|---|
{evidence_table}

## Residual Effects After Exposure Scaling

The exposure-only diagnostic is above the official SM central value. The
required residual correction is:

```text
347 / 413.543286872 = {totals["residual_ratio_347_over_exposure_scaled"]:.12g}
percent change = {totals["residual_percent_change_to_347"]:.6g}%
```

Potential legitimate sources of a correction of this order:

| Effect | Classification |
|---|---|
| detector-specific efficiency | LIKELY |
| detector thresholds | LIKELY |
| natural-Ge isotope mixture | POSSIBLE |
| official source spectrum | POSSIBLE |
| energy response | LIKELY |
| analysis window | KNOWN |
| detector-specific exposures | KNOWN |
| nuclear-response convention | UNTESTED |

No factor was tuned here to obtain 347.

## Correction Recommendations

### DOCUMENT CORRECTION

State explicitly that the current 150.494 result is absolute events/bin for the
workflow's effective 119 kg day exposure. Mark the legacy y-axis label as
suspect unless a missing normalization factor is found.

### METADATA CORRECTION

Keep `exposure_kg_day: 119` only if the dataset is documented as a
phenomenological 1 kg * 119 day / 119 kg day contract, not as the full official
CONUS+ exposure.

### CODE CORRECTION

No production physics-code correction is justified by this audit. If plots are
generated from `binCounts`, label them as absolute events/bin. If a normalized
axis is required, divide both theory and data by the same exposure convention.

### TEST CORRECTION

Add a comparison-layer unit test that fails if absolute bin counts are plotted
or compared under a `kg^-1 (10 eVee)^-1` label without exposure division.

### NO CHANGE REQUIRED

Do not replace 150.494 with 347. Do not tune physics parameters. Do not update
Slow/Fast references solely to match official CONUS+ central values.

## Central Answer

The legacy Mathematica code can produce a numerically reasonable CONUS-like
spectrum because the executable calculation applies a plausible effective
exposure and integrates to absolute bin counts. The inconsistency enters at the
written convention layer: a normalized y-axis label and ambiguous prose were
attached to a quantity that the code had already normalized to absolute events.

The specific legacy statement most likely wrong is the plot-axis label, followed
by any later interpretation that treats the old calculation as the full official
CONUS+ detector-level model. The calculation itself is not shown to be
numerically wrong by this audit.
"""
    path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    root = repo_root_from_script()
    run_dir = default_run_dir(root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=run_dir)
    parser.add_argument(
        "--slow-counts",
        type=Path,
        default=run_dir / "artifacts" / "slow_bin_counts.csv",
    )
    parser.add_argument(
        "--legacy-source",
        type=Path,
        default=root
        / "data"
        / "experiments"
        / "external"
        / "user_mathematica"
        / "2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=root
        / "docs"
        / "CONUS_docs"
        / "2026_07_16_CEvNSpyEFT - CONUS.pdf",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root_from_script()
    run_dir = args.run_dir.resolve()
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    rows = read_slow_counts(args.slow_counts.resolve())
    pdf_text, pdf_status = extract_pdf_text(args.pdf.resolve())
    summary = build_summary(rows, pdf_text, pdf_status)
    shape_rows = build_shape_rows(rows)

    line_hits = collect_line_hits(args.legacy_source.resolve(), TERMS, root)
    ydata_provenance = collect_ydata_provenance(root, pdf_text)
    evidence = evidence_rows()

    summary_path = artifacts_dir / "legacy_normalization_forensic_summary.json"
    shape_path = artifacts_dir / "legacy_normalization_shape_comparison.csv"
    evidence_path = artifacts_dir / "legacy_normalization_forensic_evidence.csv"
    report_path = run_dir / "LEGACY_NORMALIZATION_FORENSIC_AUDIT.md"

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_csv(shape_path, shape_rows)

    all_evidence_rows: list[dict[str, object]] = [
        {
            "record_type": "claim",
            "claim": row["claim"],
            "evidence_for": row["evidence_for"],
            "evidence_against": row["evidence_against"],
            "classification": row["classification"],
            "source": "",
            "line": "",
            "terms": "",
            "snippet": "",
        }
        for row in evidence
    ]
    all_evidence_rows.extend(
        {
            "record_type": "legacy_line_hit",
            "claim": "",
            "evidence_for": "",
            "evidence_against": "",
            "classification": "",
            "source": hit["source"],
            "line": hit["line"],
            "terms": hit["terms"],
            "snippet": hit["snippet"],
        }
        for hit in line_hits
    )
    write_csv(evidence_path, all_evidence_rows)
    write_report(report_path, summary, evidence, line_hits, ydata_provenance, shape_rows)

    print(json.dumps(summary, indent=2))
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {shape_path}")
    print(f"Wrote: {evidence_path}")
    print(f"Wrote: {report_path}")


if __name__ == "__main__":
    main()
