from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Tuple, Union
import numpy as np

from cevns_pyeft.foundation.constants import *  # noqa: F401,F403
from cevns_pyeft.sources.state import NeutrinoState, pure_flavor_state

ArrayLike = Union[float, int, np.ndarray]
SourceSpecies = Literal["mu", "e", "mub"]

def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)

def _scalar_or_array(x: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(x).reshape(-1)[0])
    return x

@dataclass(frozen=True)
class SNSDataset:
    name: str
    mdet_kg: float
    L_m: float
    N_POT: float
    r: float
    EnuMin_MeV: float
    EnuMax_MeV: float
    globalEnuMin_MeV: float
    globalEnuMax_MeV: float
def _compatibility_datasets():
    from .csi2021_definition import DEFINITION as d21
    from .csi2017_definition import DEFINITION as d17
    from .ar2020_definition import DEFINITION as dar
    return {d.dataset_id: d.physical.run.legacy_dataset(d.dataset_id) for d in (d17,d21,dar)}

SNS_DATASETS = _compatibility_datasets()

def _n_time_integrated_flux_cm2(L_m: float, N_POT: float, r: float) -> float:
    L_cm = float(from_length_invgev(to_length_invgev(L_m, 'm'), 'cm'))
    return r * N_POT / (4.0 * np.pi * L_cm * L_cm)

def _michel_nue_spectrum(E_MeV: np.ndarray, m_mu_MeV: float) -> np.ndarray:
    return 192.0 * E_MeV ** 2 * (0.5 - E_MeV / m_mu_MeV) / m_mu_MeV ** 3

def _michel_numubar_spectrum(E_MeV: np.ndarray, m_mu_MeV: float) -> np.ndarray:
    return 64.0 * E_MeV ** 2 * (0.75 - E_MeV / m_mu_MeV) / m_mu_MeV ** 3

def _make_interp(xp: np.ndarray, fp: np.ndarray) -> Callable[[ArrayLike], ArrayLike]:
    xp = np.asarray(xp, dtype=float)
    fp = np.asarray(fp, dtype=float)

    def f(x: ArrayLike) -> ArrayLike:
        xx = _asarray(x)
        yy = np.interp(xx, xp, fp, left=0.0, right=0.0)
        return _scalar_or_array(yy, x)
    return f

def loadNeutrinoEmpiricalFluxSNS(dataset: str='CsI2017', *, num_points: int=200, use_interpolation: bool=True) -> Dict[str, Any]:
    if dataset not in SNS_DATASETS:
        raise KeyError(f"Unknown dataset '{dataset}'. Available: {list(SNS_DATASETS)}")
    return build_neutrino_empirical_flux_sns(SNS_DATASETS[dataset], num_points=num_points, use_interpolation=use_interpolation)


def build_neutrino_empirical_flux_sns(ds: SNSDataset, *, num_points: int=200, use_interpolation: bool=True) -> Dict[str, Any]:
    """Evaluate the historical spectrum with explicit immutable dataset parameters."""
    NTimeIntFlux = _n_time_integrated_flux_cm2(ds.L_m, ds.N_POT, ds.r)
    m_mu_MeV = float(from_energy_gev(m_mu, 'MeV'))
    Emin = float(ds.EnuMin_MeV)
    Emax = float(ds.EnuMax_MeV)
    Egmin = float(ds.globalEnuMin_MeV)
    Egmax = float(ds.globalEnuMax_MeV)
    grid = np.linspace(Emin, Emax, int(num_points))
    mask_global = (grid >= Egmin) & (grid <= Egmax)
    phi_e = np.zeros_like(grid)
    phi_mub = np.zeros_like(grid)
    phi_e[mask_global] = NTimeIntFlux * np.clip(_michel_nue_spectrum(grid[mask_global], m_mu_MeV), 0.0, np.inf)
    phi_mub[mask_global] = NTimeIntFlux * np.clip(_michel_numubar_spectrum(grid[mask_global], m_mu_MeV), 0.0, np.inf)
    phi_tot = phi_e + phi_mub
    if use_interpolation:
        phi_e_measured = _make_interp(grid, phi_e)
        phi_mub_measured = _make_interp(grid, phi_mub)
        phi_tot_measured = _make_interp(grid, phi_tot)
    else:

        def phi_e_measured(E_MeV: ArrayLike) -> ArrayLike:
            E = _asarray(E_MeV)
            m = (E >= Egmin) & (E <= Egmax)
            out = np.zeros_like(E)
            out[m] = NTimeIntFlux * np.clip(_michel_nue_spectrum(E[m], m_mu_MeV), 0.0, np.inf)
            return _scalar_or_array(out, E_MeV)

        def phi_mub_measured(E_MeV: ArrayLike) -> ArrayLike:
            E = _asarray(E_MeV)
            m = (E >= Egmin) & (E <= Egmax)
            out = np.zeros_like(E)
            out[m] = NTimeIntFlux * np.clip(_michel_numubar_spectrum(E[m], m_mu_MeV), 0.0, np.inf)
            return _scalar_or_array(out, E_MeV)

        def phi_tot_measured(E_MeV: ArrayLike) -> ArrayLike:
            return _scalar_or_array(_asarray(phi_e_measured(E_MeV)) + _asarray(phi_mub_measured(E_MeV)), E_MeV)
    E0_GeV = (m_pi_charged ** 2 - m_mu ** 2) / (2.0 * m_pi_charged)
    E0_MeV = float(from_energy_gev(E0_GeV, 'MeV'))
    mu_line_measured: Tuple[float, float] = (E0_MeV, NTimeIntFlux)
    mu_line_natural: Tuple[float, float] = (float(E0_GeV), NTimeIntFlux * GEV_INV2_TO_CM2)

    def phi_e_natural(E_GeV: ArrayLike) -> ArrayLike:
        E = _asarray(E_GeV)
        E_MeV = from_energy_gev(E, 'MeV')
        val = _asarray(phi_e_measured(E_MeV))
        out = to_flux_natural(val, 'cm^-2 MeV^-1')
        return _scalar_or_array(out, E_GeV)

    def phi_mub_natural(E_GeV: ArrayLike) -> ArrayLike:
        E = _asarray(E_GeV)
        E_MeV = from_energy_gev(E, 'MeV')
        val = _asarray(phi_mub_measured(E_MeV))
        out = to_flux_natural(val, 'cm^-2 MeV^-1')
        return _scalar_or_array(out, E_GeV)

    def phi_tot_natural(E_GeV: ArrayLike) -> ArrayLike:
        E = _asarray(E_GeV)
        E_MeV = from_energy_gev(E, 'MeV')
        val = _asarray(phi_tot_measured(E_MeV))
        out = to_flux_natural(val, 'cm^-2 MeV^-1')
        return _scalar_or_array(out, E_GeV)
    return {'basic': {'name': ds.name, 'detectorMassKg': ds.mdet_kg, 'baseline_m': ds.L_m, 'N_POT': ds.N_POT, 'r': ds.r, 'EnuRangeMeV': (ds.EnuMin_MeV, ds.EnuMax_MeV), 'globalEnuRangeMeV': (ds.globalEnuMin_MeV, ds.globalEnuMax_MeV), 'NTimeIntegratedFlux_cm^-2': NTimeIntFlux}, 'measured': {'energyUnit': 'MeV', 'fluxUnit': 'cm^-2 MeV^-1', 'e': phi_e_measured, 'mub': phi_mub_measured, 'totalContinuous': phi_tot_measured, 'muLine': mu_line_measured}, 'natural': {'energyUnit': 'GeV', 'e': phi_e_natural, 'mub': phi_mub_natural, 'totalContinuous': phi_tot_natural, 'muLine': mu_line_natural}}
load_neutrino_empirical_flux_sns = loadNeutrinoEmpiricalFluxSNS


def sns_component_state(component: SourceSpecies) -> NeutrinoState:
    """Return the canonical Flavor state for one time-integrated SNS component.

    The component label determines both the incoming Flavor density and the
    particle identity. Antineutrino identity is metadata at this boundary;
    the interaction kernel remains unchanged until the dedicated ANTI-NU
    physics audit.
    """

    if component == "mu":
        return pure_flavor_state("mu", particle_kind="nu")
    if component == "e":
        return pure_flavor_state("e", particle_kind="nu")
    if component == "mub":
        return pure_flavor_state("mu", particle_kind="antinu")
    raise ValueError(
        "SNS state component must be one of ('mu', 'e', 'mub'), "
        f"got {component!r}"
    )


def loadNeutrinoFlux(dataset: str, *, data_dir: Optional[str | Path]=None) -> Dict[str, Any]:
    key = str(dataset).strip()
    if key in SNS_DATASETS:
        return loadNeutrinoEmpiricalFluxSNS(key)
    raise KeyError(f"Unknown COHERENT SNS dataset {dataset!r}. Available: {list(SNS_DATASETS)}")

__all__ = [
    "SNSDataset",
    "SNS_DATASETS",
    "SourceSpecies",
    "sns_component_state",
    "loadNeutrinoEmpiricalFluxSNS",
    "build_neutrino_empirical_flux_sns",
    "load_neutrino_empirical_flux_sns",
    "loadNeutrinoFlux",
]
