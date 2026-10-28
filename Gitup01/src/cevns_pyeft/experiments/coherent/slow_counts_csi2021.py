from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Optional, Tuple, Union

import numpy as np

from cevns_pyeft.detectors.csi2021 import (
    CsI2021EfficiencyParams, efficiency_csi2021, efficiency,
    PE_BINS_9, PE_WIDTHS_9, DEFAULT_ACCEPTANCE,
)

ArrayLike = Union[float, int, np.ndarray]
EfficiencyModel = Literal["CsI2021"]
Triplet = Tuple[int, int, str]

from .csi2021_definition import DEFINITION
A_TARGET: Dict[str, float] = {name:a for name,key,a in DEFINITION.physical.targets}


def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


def _scalar_or_array(x: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(x).reshape(-1)[0])
    return x


def combine_equal_stoichiometry(cs: np.ndarray, i: np.ndarray) -> np.ndarray:
    return (A_TARGET["Cs133"] * cs + A_TARGET["I127"] * i) / (A_TARGET["Cs133"] + A_TARGET["I127"])


def slow_counts_csi2021(
    responses_json: str | Path,
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = DEFINITION.reproduction_sin2thetaW,
    c10_mass_mode: str = DEFINITION.physical.c10_mass_mode,
    n_er: int = DEFINITION.numerical_profiles['slow']['n_er'],
    n_enu: int = DEFINITION.numerical_profiles['slow']['n_enu'],
    n_pe_bin: int = DEFINITION.numerical_profiles['slow']['n_pe_bin'],
    pe_step: float = DEFINITION.numerical_profiles['slow']['pe_step'],
) -> Dict[str, Any]:
    """Compatibility view of the validated composable prediction.

    Historical raw arrays use the full detector mass for EACH isotope and
    precede material fractions and source acceptance. Keep that convention.
    """
    from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
    from cevns_pyeft.core.predict import predict
    from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
    from .csi2021 import make_csi2021_model

    model = make_csi2021_model(responses_json, c10_mass_mode=str(c10_mass_mode))
    prediction = predict(model, parameters=TheoryPoint(dict(wc_triplets or {}), include_sm=bool(include_sm), sin2thetaW=float(sin2thetaW)),
        numerics=IntegrationSettings.legacy_csi2021_v1(n_er=int(n_er), n_enu=int(n_enu), n_pe_bin=int(n_pe_bin), pe_step=float(pe_step)))
    raw: Dict[str, Dict[str, np.ndarray]] = {}
    counts_bin: Dict[str, np.ndarray] = {}
    for flavor, component_id in LEGACY_COMPONENT_IDS.items():
        raw[flavor] = {}
        counts_bin[flavor] = np.zeros(prediction.binning.shape)
        for target in model.targets.isotopes:
            key = (component_id, target.isotope_id)
            before = prediction.diagnostics["preselection_per_nucleus"][key]
            raw[flavor][target.isotope_id] = before * model.targets.detector_mass_kg / target.nucleus_mass_kg
            counts_bin[flavor] += prediction.components[key]
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
