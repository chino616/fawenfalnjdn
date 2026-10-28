from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import numpy as np

from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.experiments.coherent.sns import (
    loadNeutrinoEmpiricalFluxSNS,
    sns_component_state,
)
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import _rate_per_kg
from cevns_pyeft.rates.differential import _trapz

Triplet = Tuple[int, int, str]

from .csi2017_definition import DEFINITION
CSI2017_PE_PER_KEV = DEFINITION.physical.pe_per_keV
CSI2017_BINS_25 = np.asarray(DEFINITION.observation.edges)
CSI2017_WIDTHS_25 = np.diff(CSI2017_BINS_25)
CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH = next(r.path for r in DEFINITION.resources if r.id == 'efficiency')

def slow_counts_csi2017(
    responses_json: str | Path,
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = DEFINITION.reproduction_sin2thetaW,
    c10_mass_mode: str = DEFINITION.physical.c10_mass_mode,
    n_er: int = 21,
    n_enu: int = DEFINITION.numerical_profiles['slow']['n_enu'],
    n_pe_bin: int = 8,
    pe_step: float = 3.0,
    efficiency_data_path: str | Path = CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    definition=None,
) -> Dict[str, Any]:
    config = definition or DEFINITION
    physical = config.physical
    bins = np.asarray(config.observation.edges)
    widths = np.diff(bins)
    from .sns import build_neutrino_empirical_flux_sns
    db = ResponseDB(responses_json)
    flux = build_neutrino_empirical_flux_sns(physical.run.legacy_dataset(config.dataset_id), num_points=physical.run.num_points, use_interpolation=physical.run.interpolation)
    eff = _interp_eff(_data_path(responses_json, efficiency_data_path), *physical.efficiency_columns,
                      low=physical.efficiency_low, threshold=physical.efficiency_threshold)
    pe_grid = np.linspace(bins[0], bins[-1], physical.slow_pe_nodes, dtype=float)
    er_grid = pe_grid / physical.pe_per_keV
    targets = tuple((name,key,a/sum(t[2] for t in physical.targets)) for name,key,a in reversed(physical.targets))
    raw = {flv: {} for flv in ("mu", "e", "mub")}
    counts = {}
    for flv in raw:
        spectrum = np.zeros_like(pe_grid)
        for target, key, weight in targets:
            rate_er = _rate_per_kg(
                db.get(key),
                flux,
                er_grid,
                flv,
                wc_triplets,
                include_sm,
                sin2thetaW,
                c10_mass_mode,
                n_enu,
                source_state=sns_component_state(flv),
                nucleus_mass_kg=next(a for name,key,a in physical.targets if name==target)*physical.atomic_mass_kg,
            )
            dndpe = np.asarray(eff(pe_grid), dtype=float) * physical.mass_kg * (1.0 / physical.pe_per_keV) * rate_er
            raw[flv][target] = dndpe
            spectrum += float(weight) * dndpe
        vals = np.zeros(widths.size, dtype=float)
        for i in range(vals.size):
            left, right = bins[i], bins[i + 1]
            inner = pe_grid[(pe_grid > left) & (pe_grid < right)]
            xs = np.r_[left, inner, right]
            vals[i] = float(_trapz(np.interp(xs, pe_grid, spectrum), xs))
        counts[flv] = vals
    counts["total"] = counts["mu"] + counts["e"] + counts["mub"]
    return {
        "counts_per_bin": counts,
        "counts_per_npe": {k: v / widths for k, v in counts.items()},
        "target_flavor_dndpe_grid": raw,
        "pe_grid": pe_grid,
        "pe_bins": bins.copy(),
        "dataset": config.dataset_id,
    }


__all__ = [
    "CSI2017_PE_PER_KEV",
    "CSI2017_BINS_25",
    "CSI2017_WIDTHS_25",
    "CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH",
    "slow_counts_csi2017",
]
