from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Optional, Tuple, Union

import numpy as np

from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import bin_events_csi

ArrayLike = Union[float, int, np.ndarray]
EfficiencyModel = Literal["CsI2021"]
Triplet = Tuple[int, int, str]

PE_BINS_9 = np.array([0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001], dtype=float)
PE_WIDTHS_9 = np.diff(PE_BINS_9)
DEFAULT_ACCEPTANCE: Dict[str, float] = {"e": 0.848, "mu": 0.997, "mub": 0.848}
A_TARGET: Dict[str, float] = {"Cs133": 133.0, "I127": 127.0}


def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


def _scalar_or_array(x: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(x).reshape(-1)[0])
    return x


@dataclass(frozen=True)
class CsI2021EfficiencyParams:
    a: float = 1.32045
    b: float = 0.285979
    c: float = 10.8646
    d: float = -0.3333


def efficiency_csi2021(pe: ArrayLike, *, params: CsI2021EfficiencyParams = CsI2021EfficiencyParams()) -> ArrayLike:
    x = _asarray(pe)
    eff = params.a / (1.0 + np.exp(-params.b * (x - params.c))) + params.d
    eff = np.maximum(eff, 0.0)
    return _scalar_or_array(eff, pe)


def efficiency(pe: ArrayLike, *, model: EfficiencyModel = "CsI2021") -> ArrayLike:
    if model == "CsI2021":
        return efficiency_csi2021(pe)
    raise ValueError(f"Unknown efficiency model: {model}")


def combine_equal_stoichiometry(cs: np.ndarray, i: np.ndarray) -> np.ndarray:
    return (A_TARGET["Cs133"] * cs + A_TARGET["I127"] * i) / (A_TARGET["Cs133"] + A_TARGET["I127"])


def slow_counts_csi2021(
    responses_json: str | Path,
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "flavor",
    n_er: int = 21,
    n_enu: int = 120,
    n_pe_bin: int = 8,
    pe_step: float = 3.0,
) -> Dict[str, Any]:
    db = ResponseDB(responses_json)
    flux_obj = loadNeutrinoEmpiricalFluxSNS("CsI2021")
    target_specs = (("Cs133", "Cs133"), ("I127", "I"))
    raw: Dict[str, Dict[str, np.ndarray]] = {}
    for flavor in ("mu", "e", "mub"):
        raw[flavor] = {}
        for target_name, response_key in target_specs:
            resp = db.get(response_key)
            raw[flavor][target_name] = bin_events_csi(
                resp,
                flux_obj,
                PE_BINS_9,
                efficiency=efficiency,
                flavor=flavor,
                wc_triplets=dict(wc_triplets or {}),
                include_sm=bool(include_sm),
                sin2thetaW=float(sin2thetaW),
                n_ER=int(n_er),
                n_Enu=int(n_enu),
                pe_step=float(pe_step),
                n_PE_bin=int(n_pe_bin),
                c10_mass_mode=str(c10_mass_mode),
            )
    counts_bin: Dict[str, np.ndarray] = {}
    for flavor in ("mu", "e", "mub"):
        combined_noacc = combine_equal_stoichiometry(raw[flavor]["Cs133"], raw[flavor]["I127"])
        counts_bin[flavor] = np.asarray(combined_noacc, dtype=float) * float(DEFAULT_ACCEPTANCE[flavor])
    counts_bin["total"] = counts_bin["mu"] + counts_bin["e"] + counts_bin["mub"]
    counts_npe = {key: np.asarray(value, dtype=float) / PE_WIDTHS_9 for key, value in counts_bin.items()}
    return {
        "counts_per_bin": counts_bin,
        "counts_per_npe": counts_npe,
        "target_flavor_counts_per_bin": raw,
        "pe_bins": PE_BINS_9.copy(),
        "model_note": "full Li2026 slow/direct path inlined from current program",
    }


__all__ = [
    "ArrayLike",
    "CsI2021EfficiencyParams",
    "efficiency_csi2021",
    "EfficiencyModel",
    "efficiency",
    "PE_BINS_9",
    "PE_WIDTHS_9",
    "DEFAULT_ACCEPTANCE",
    "A_TARGET",
    "combine_equal_stoichiometry",
    "slow_counts_csi2021",
]
