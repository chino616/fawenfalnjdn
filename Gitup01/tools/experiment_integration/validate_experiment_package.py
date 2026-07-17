#!/usr/bin/env python3
"""Validate the bundled CEvNS experiment input package.

Exit code 0 means the package structure is internally consistent. Publication
mode may still be incomplete; missing user inputs are reported separately.
"""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "experiments"


def read_csv(rel: str) -> list[dict[str, str]]:
    path = DATA_ROOT / rel
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def floats(rows: list[dict[str, str]], column: str) -> list[float]:
    return [float(row[column]) for row in rows]


def strictly_increasing(values: list[float]) -> bool:
    return all(b > a for a, b in zip(values, values[1:]))


def missing_cells(rows: list[dict[str, str]], columns: list[str]) -> int:
    count = 0
    for row in rows:
        for column in columns:
            value = row.get(column, "").strip()
            if not value or "REQUIRES_INPUT" in value:
                count += 1
    return count


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    # Public bin edges
    pub_edges = floats(read_csv("conus_plus_2025/bin_edges_evee.csv"), "edge_evee")
    if not strictly_increasing(pub_edges):
        errors.append("CONUS+ bin edges are not strictly increasing")
    if (pub_edges[0], pub_edges[-1]) != (160.0, 800.0):
        errors.append("CONUS+ bin edge range must be 160--800 eVee")

    # Legacy bin edges
    legacy_edges = floats(read_csv("conus_legacy_mathematica/bin_edges_evee.csv"), "edge_evee")
    if not strictly_increasing(legacy_edges):
        errors.append("Legacy bin edges are not strictly increasing")

    # Natural Ge fractions
    iso = read_csv("conus_plus_2025/natural_germanium_isotopes.csv")
    fraction_sum = sum(float(row["number_fraction"]) for row in iso)
    if abs(fraction_sum - 1.0) > 1e-8:
        errors.append(f"Natural Ge fractions sum to {fraction_sum}, expected 1")

    # Legacy fission fractions
    ff = read_csv("conus_legacy_mathematica/fission_fractions.csv")
    fsum = sum(float(row["fraction"]) for row in ff)
    if abs(fsum - 1.0) > 1e-12:
        errors.append(f"Legacy fission fractions sum to {fsum}, expected 1")

    # External parsed spectra
    for rel in [
        "external/dayabay/dayabay_u235_unfolded.csv",
        "external/dayabay/dayabay_pu_combo_unfolded.csv",
        "external/dayabay/dayabay_total_unfolded.csv",
        "external/dayabay/dayabay_high_energy.csv",
        "external/dayabay/dayabay_whole_reference.csv",
    ]:
        rows = read_csv(rel)
        if not rows:
            errors.append(f"No rows parsed in {rel}")
        elif not strictly_increasing(floats(rows, "energy_mev")):
            errors.append(f"Energy is not strictly increasing in {rel}")


    # Executable reproduction spectrum
    repro = read_csv("conus_plus_2025_reproduction/reactor_spectrum_shape.csv")
    e = floats(repro, "energy_mev")
    shape = floats(repro, "normalized_shape_per_mev")
    if not strictly_increasing(e):
        errors.append("Reproduction flux energy is not strictly increasing")
    area = sum((b-a)*(ya+yb)/2 for a,b,ya,yb in zip(e,e[1:],shape,shape[1:]))
    if abs(area-1.0) > 5e-6:
        errors.append(f"Reproduction flux shape integrates to {area}, expected 1")

    # Publication placeholders: report, do not fail package structure.
    spectrum = read_csv("conus_plus_2025/reactor_spectrum_conus_plus_TEMPLATE.csv")
    missing = missing_cells(
        spectrum,
        [
            "U235_per_fission_per_mev",
            "U238_per_fission_per_mev",
            "Pu239_per_fission_per_mev",
            "Pu241_per_fission_per_mev",
        ],
    )
    if missing:
        warnings.append(f"Publication reactor spectrum has {missing} missing cells")

    for detector in ("C2", "C3", "C5"):
        rows = read_csv(f"conus_plus_2025/efficiency_{detector}_TEMPLATE.csv")
        missing = missing_cells(rows, ["efficiency"])
        if missing:
            warnings.append(f"{detector} efficiency has {missing} missing cells")

    print({
        "status": "FAIL" if errors else "PASS_WITH_REQUIRED_INPUTS" if warnings else "PASS",
        "errors": errors,
        "required_inputs": warnings,
    })
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
