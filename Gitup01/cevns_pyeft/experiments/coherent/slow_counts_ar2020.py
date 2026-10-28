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

from .ar2020_definition import DEFINITION
AR_BINS_12 = np.asarray(DEFINITION.observation.edges)
AR_WIDTHS_12 = np.diff(AR_BINS_12)
AR_DEFAULT_EFFICIENCY_RELATIVE_PATH = next(r.path for r in DEFINITION.resources if r.id == 'efficiency')
AR_D = np.asarray(DEFINITION.statistics.observed)
AR_B = np.asarray(DEFINITION.statistics.background)
AR_DMIN = np.asarray(DEFINITION.statistics.lower)
AR_DMAX = np.asarray(DEFINITION.statistics.upper)

def slow_counts_ar2020(
    responses_json: str | Path,
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = DEFINITION.reproduction_sin2thetaW,
    c10_mass_mode: str = DEFINITION.physical.c10_mass_mode,
    n_er: int = DEFINITION.numerical_profiles['slow']['n_er'],
    n_enu: int = DEFINITION.numerical_profiles['slow']['n_enu'],
    n_pe_bin: int = DEFINITION.numerical_profiles['slow']['n_pe_bin'],
    pe_step: float = 3.0,
    efficiency_data_path: str | Path = AR_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    definition=None, model=None,
) -> Dict[str, Any]:
    config = definition or DEFINITION
    physical = config.physical
    if model is None:
        from .execution import assemble_legacy
        model=assemble_legacy(config,{'responses':Path(responses_json),'efficiency':_data_path(responses_json,efficiency_data_path)})
    from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
    components={part.component_id:part for part in model.source.for_run(model.run).components}
    observation=model.observation
    bins = np.asarray(config.observation.edges)
    widths = np.diff(bins)
    from .sns import build_neutrino_empirical_flux_sns
    db = ResponseDB(responses_json)
    flux = build_neutrino_empirical_flux_sns(physical.run.legacy_dataset(config.dataset_id), num_points=physical.run.num_points, use_interpolation=physical.run.interpolation)
    flux['basic']['detectorMassKg'] = physical.mass_kg
    resp = db.get(physical.response_key)
    eff=observation.efficiency
    if len(model.targets.isotopes)!=1:raise ValueError("this legacy Gaussian strategy requires one declared isotope")
    isotope=model.targets.isotopes[0]
    from cevns_pyeft.rates.counts import _rate_per_kg,_trapz_weights
    endpoint=max(max(part.support.integration_domain_MeV[1],*(line.energy_MeV for line in part.lines)) if part.lines else part.support.integration_domain_MeV[1] for part in components.values())
    ER=np.linspace(.1,model.interaction.kinematics.maximum_recoil_keV(isotope,endpoint),int(n_er))
    W=_trapz_weights(ER)
    fold=ar_fold_matrix(ER,W,bins,eff,observation,n_pe_bin)
    raw={}
    from .sns import sns_component_state
    for flv in ('mu','e','mub'):
        rate=_rate_per_kg(resp,flux,ER,flv,wc_triplets,include_sm,sin2thetaW,c10_mass_mode,n_enu,
            source_state=sns_component_state(flv),source_component=components[LEGACY_COMPONENT_IDS[flv]],target=isotope,interaction=model.interaction)
        raw[flv]={physical.target_id:np.sum(rate[:,None]*fold,axis=0)*model.targets.detector_mass_kg}
    counts = {flv: raw[flv][physical.target_id] for flv in raw}
    counts["total"] = counts["mu"] + counts["e"] + counts["mub"]
    return {
        "counts_per_bin": counts,
        "counts_per_npe": {k: v / widths for k, v in counts.items()},
        "target_flavor_counts_per_bin": raw,
        "pe_bins": bins.copy(),
        "dataset": config.dataset_id,
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


def ar_fold_matrix(recoil, weights, bins, eff, physical, n_observed):
    fold = np.zeros((recoil.size, len(bins)-1))
    for i,T in enumerate(recoil):
        mean = (physical.mean_linear + physical.mean_quadratic * T) * T
        for j in range(len(bins)-1):
            x = np.linspace(bins[j], bins[j+1], max(2,int(n_observed)), dtype=float)
            sigma = physical.sigma_coefficient * np.sqrt(np.maximum(x,1e-300))
            smear = np.exp(-.5*((x-mean)/sigma)**2)/(np.sqrt(2*np.pi)*sigma)
            fold[i,j] = weights[i] * float(_trapz(np.asarray(eff(x),dtype=float)*smear,x))
    return fold
