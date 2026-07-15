from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Optional, Tuple, Union
import numpy as np

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.rates.counts import _rate_per_kg
from cevns_pyeft.rates.differential import _trapz

ArrayLike = Union[float, int, np.ndarray]


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


def efficiency_csi2021(pe: ArrayLike, *, params: CsI2021EfficiencyParams=CsI2021EfficiencyParams()) -> ArrayLike:
    x = _asarray(pe)
    eff = params.a / (1.0 + np.exp(-params.b * (x - params.c))) + params.d
    eff = np.maximum(eff, 0.0)
    return _scalar_or_array(eff, pe)


EfficiencyModel = Literal['CsI2021']


def efficiency(pe: ArrayLike, *, model: EfficiencyModel='CsI2021') -> ArrayLike:
    if model == 'CsI2021':
        return efficiency_csi2021(pe)
    raise ValueError(f'Unknown efficiency model: {model}')


Triplet = Tuple[int, int, str]

CSI2017_PE_PER_KEV = 1.17
CSI2017_BINS_25 = np.linspace(0.001, 50.0, 26, dtype=float)
CSI2017_WIDTHS_25 = np.diff(CSI2017_BINS_25)
CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH = 'data/datafiles/COHERENT_eff.txt'


def slow_counts_csi2017(responses_json: str | Path, wc_triplets: Optional[Mapping[Triplet, complex]]=None, *, include_sm: bool=True, sin2thetaW: float=0.2387, c10_mass_mode: str='flavor', n_er: int=21, n_enu: int=120, n_pe_bin: int=8, pe_step: float=3.0, efficiency_data_path: str | Path=CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH) -> Dict[str, Any]:
    _ = (n_er, n_pe_bin, pe_step)
    db, flux = ResponseDB(responses_json), loadNeutrinoEmpiricalFluxSNS('CsI2017')
    eff = _interp_eff(_data_path(responses_json, efficiency_data_path), 0, 1, low=1.0e-10, threshold=4.9)
    pe_grid = np.linspace(CSI2017_BINS_25[0], CSI2017_BINS_25[-1], 251, dtype=float)
    er_grid = pe_grid / CSI2017_PE_PER_KEV
    targets = (('I127', 'I', 127.0 / (127.0 + 133.0)), ('Cs133', 'Cs133', 133.0 / (127.0 + 133.0)))
    raw = {flv: {} for flv in ('mu', 'e', 'mub')}
    counts = {}
    for flv in raw:
        spectrum = np.zeros_like(pe_grid)
        for target, key, weight in targets:
            rate_er = _rate_per_kg(db.get(key), flux, er_grid, flv, wc_triplets, include_sm, sin2thetaW, c10_mass_mode, n_enu)
            dndpe = np.asarray(eff(pe_grid), dtype=float) * 14.6 * (1.0 / CSI2017_PE_PER_KEV) * rate_er
            raw[flv][target] = dndpe
            spectrum += float(weight) * dndpe
        vals = np.zeros(CSI2017_WIDTHS_25.size, dtype=float)
        for i in range(vals.size):
            left, right = CSI2017_BINS_25[i], CSI2017_BINS_25[i + 1]
            inner = pe_grid[(pe_grid > left) & (pe_grid < right)]
            xs = np.r_[left, inner, right]
            vals[i] = float(_trapz(np.interp(xs, pe_grid, spectrum), xs))
        counts[flv] = vals
    counts['total'] = counts['mu'] + counts['e'] + counts['mub']
    return {'counts_per_bin': counts, 'counts_per_npe': {k: v / CSI2017_WIDTHS_25 for k, v in counts.items()}, 'target_flavor_dndpe_grid': raw, 'pe_grid': pe_grid, 'pe_bins': CSI2017_BINS_25.copy(), 'dataset': 'CsI2017'}


__all__ = [
    "ArrayLike",
    "CsI2021EfficiencyParams",
    "efficiency_csi2021",
    "EfficiencyModel",
    "efficiency",
    "CSI2017_PE_PER_KEV",
    "CSI2017_BINS_25",
    "CSI2017_WIDTHS_25",
    "CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH",
    "slow_counts_csi2017",
]
