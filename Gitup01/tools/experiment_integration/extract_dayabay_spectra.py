#!/usr/bin/env python3
"""Extract the spectrum blocks from the bundled Daya Bay ancillary text files."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external" / "dayabay"


def write_csv(path: Path, header: list[str], rows: list[list[float]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def section(path: Path, marker: str) -> list[list[float]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(marker))
    i = start
    while i < len(lines) and not (
        lines[i]
        and not lines[i].startswith("#")
        and re.match(r"^[-+0-9.]", lines[i])
    ):
        i += 1
    rows: list[list[float]] = []
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("#"):
            break
        parts = s.split()
        if len(parts) != 3:
            break
        rows.append([float(x) for x in parts])
        i += 1
    return rows


def first_block(path: Path, ncols: int) -> list[list[float]]:
    rows: list[list[float]] = []
    started = False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            if started and not s:
                break
            continue
        parts = s.replace("%", "").split()
        if len(parts) != ncols:
            if started:
                break
            continue
        try:
            rows.append([float(x) for x in parts])
        except ValueError:
            if started:
                break
            continue
        started = True
    return rows


def main() -> None:
    raw = DATA / "UnfoldAntineutrinoSpectra.txt"
    common_header = [
        "energy_mev",
        "spectrum_with_ibd_cm2_per_fission_per_mev",
        "spectrum_without_ibd_per_fission_per_mev",
    ]
    for marker, name in [
        ("# Unfolded [U235]", "dayabay_u235_unfolded.csv"),
        ("# Unfolded [Pu combo]", "dayabay_pu_combo_unfolded.csv"),
        ("# Unfolded [Total]", "dayabay_total_unfolded.csv"),
    ]:
        write_csv(DATA / name, common_header, section(raw, marker))

    write_csv(
        DATA / "dayabay_high_energy.csv",
        common_header + ["relative_uncertainty_percent"],
        first_block(DATA / "AntineutrinoEnergySpectrum_high.txt", 4),
    )
    write_csv(
        DATA / "dayabay_whole_reference.csv",
        ["energy_mev", "spectrum_without_ibd_per_fission_per_mev", "relative_uncertainty"],
        first_block(DATA / "WholeAntineutrinoEnergySpectrum.txt", 3),
    )


if __name__ == "__main__":
    main()
