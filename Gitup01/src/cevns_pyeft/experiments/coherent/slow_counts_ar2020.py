from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import numpy as np

from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import _er_grid, _folded_counts
from cevns_pyeft.rates.differential import _trapz

Triplet = Tuple[int, int, str]

AR_BINS_12 = np.linspace(0.001, 120.001, 13, dtype=float)
AR_WIDTHS_12 = np.diff(AR_BINS_12)
AR_DEFAULT_EFFICIENCY_RELATIVE_PATH = "data/datafiles/CENNS10AnlAEfficiency.txt"
AR_D = np.array((174.3294, 164.8672, 82.4428, 46.6318, 13.6262, 22.2221, 7.8176, 20.0156, 25.6136, 15.01212, 21.41103, 6.01039), dtype=float)
AR_B = np.array((100.9960159, 106.1752988, 77.09163347, 59.16334661, 44.02390438, 36.45418327, 34.86055777, 28.0876494, 22.50996016, 18.92430279, 16.53386454, 16.13545817), dtype=float)
AR_DMIN = np.array((143.625498, 140.0398406, 62.74900398, 29.6812749, -1.394422311, 8.167330677, -4.581673307, 7.768924303, 13.74501992, 4.183266932, 10.55776892, -3.784860558), dtype=float)
AR_DMAX = np.array((218.5258964, 196.6135458, 106.5737052, 66.73306773, 30.47808765, 38.04780876, 21.71314741, 33.26693227, 38.44621514, 26.4940239, 32.8685259, 15.33864542), dtype=float)


def slow_counts_ar2020(
    responses_json: str | Path,
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "quark_mass_resolved",
    n_er: int = 21,
    n_enu: int = 120,
    n_pe_bin: int = 8,
    pe_step: float = 3.0,
    efficiency_data_path: str | Path = AR_DEFAULT_EFFICIENCY_RELATIVE_PATH,
) -> Dict[str, Any]:
    _ = pe_step
    db, flux = ResponseDB(responses_json), loadNeutrinoEmpiricalFluxSNS("Ar2020")
    resp = db.get("Ar40")
    eff = _interp_eff(_data_path(responses_json, efficiency_data_path), 0, 2, low=0.0)
    ER, W = _er_grid(resp, n_er)
    fold = np.zeros((ER.size, AR_WIDTHS_12.size), dtype=float)
    for i, T in enumerate(ER):
        mean = (0.246 + 0.00078 * T) * T
        for j in range(AR_WIDTHS_12.size):
            x = np.linspace(AR_BINS_12[j], AR_BINS_12[j + 1], max(2, int(n_pe_bin)), dtype=float)
            sigma = 0.58 * np.sqrt(np.maximum(x, 1.0e-300))
            smear = np.exp(-0.5 * ((x - mean) / sigma) ** 2) / (np.sqrt(2.0 * np.pi) * sigma)
            fold[i, j] = W[i] * float(_trapz(np.asarray(eff(x), dtype=float) * smear, x))
    raw = {
        flv: {
            "Ar40": _folded_counts(resp, flux, ER, fold, flv, wc_triplets, include_sm, sin2thetaW, c10_mass_mode, n_enu)
        }
        for flv in ("mu", "e", "mub")
    }
    counts = {flv: raw[flv]["Ar40"] for flv in raw}
    counts["total"] = counts["mu"] + counts["e"] + counts["mub"]
    return {
        "counts_per_bin": counts,
        "counts_per_npe": {k: v / AR_WIDTHS_12 for k, v in counts.items()},
        "target_flavor_counts_per_bin": raw,
        "pe_bins": AR_BINS_12.copy(),
        "dataset": "Ar2020",
    }


__all__ = [
    "AR_BINS_12",
    "AR_WIDTHS_12",
    "AR_DEFAULT_EFFICIENCY_RELATIVE_PATH",
    "AR_D",
    "AR_B",
    "AR_DMIN",
    "AR_DMAX",
    "slow_counts_ar2020",
]
