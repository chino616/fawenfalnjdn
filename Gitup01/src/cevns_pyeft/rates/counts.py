from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple
import math
import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.sources.state import NeutrinoState, pure_flavor_state
from cevns_pyeft.theory.kinematics import minimum_neutrino_energy_GeV
from .differential import (
    ArrayLike,
    Basis,
    Flavor,
    _asarray,
    _trapz,
    if_positive,
    emax_muon_dar_mev,
    enr_max_keV,
    p_smearing_csi,
    differential_cross_section_nn,
)

SourceFlavor = str


def _trapz_weights(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or x.size < 2:
        raise ValueError('x must be 1D with at least 2 points')
    w = np.zeros_like(x)
    dx = np.diff(x)
    w[0] = 0.5 * dx[0]
    w[-1] = 0.5 * dx[-1]
    if x.size > 2:
        w[1:-1] = 0.5 * (dx[:-1] + dx[1:])
    return w


def _choose_phi_cont(flux_obj: Dict[str, Any], flavor: SourceFlavor) -> Callable[[np.ndarray], np.ndarray]:
    if flavor == 'e':
        phi_e = flux_obj['measured']['e']
        return lambda E_MeV: np.asarray(phi_e(E_MeV), dtype=float)
    if flavor == 'mub':
        phi_mub = flux_obj['measured']['mub']
        return lambda E_MeV: np.asarray(phi_mub(E_MeV), dtype=float)
    if flavor == 'mu':
        return lambda E_MeV: np.zeros_like(np.asarray(E_MeV, dtype=float))
    raise ValueError(f'Unknown source flavor {flavor!r}')


def _legacy_sns_component_state(flavor: SourceFlavor) -> NeutrinoState:
    """Preserve the protected Ar2020 wrapper while making rho explicit."""

    if flavor == 'e':
        return pure_flavor_state('e', particle_kind='nu')
    if flavor == 'mu':
        return pure_flavor_state('mu', particle_kind='nu')
    if flavor == 'mub':
        return pure_flavor_state('mu', particle_kind='antinu')
    raise ValueError(f'Unknown source flavor {flavor!r}')


def _rate_per_kg(
    resp,
    flux_obj,
    ER_grid,
    flavor,
    wc_triplets,
    include_sm,
    sin2thetaW,
    c10_mass_mode,
    n_enu,
    *,
    source_state: NeutrinoState,
):
    A = int(resp.basic.get('A'))
    mA_GeV = A * float(c.AMU_GEV)
    mass_kg = A * 1.6605390666e-27
    enu = np.linspace(0.0, emax_muon_dar_mev(), int(n_enu), dtype=float)
    phi = _choose_phi_cont(flux_obj, flavor)
    mu_E0, mu_weight = flux_obj['measured']['muLine']
    out = np.zeros_like(np.asarray(ER_grid, dtype=float))
    for i, ER_keV in enumerate(ER_grid):
        ER_GeV = float(ER_keV) * 1.0e-6
        Emin_GeV = minimum_neutrino_energy_GeV(ER_GeV, mA_GeV)
        mask = enu >= float(c.from_energy_gev(Emin_GeV, 'MeV'))
        cont = 0.0
        if np.any(mask):
            eg = enu[mask]
            ds = differential_cross_section_nn(
                resp,
                float(ER_keV),
                eg,
                rho=source_state,
                wc_triplets=dict(wc_triplets or {}),
                include_sm=include_sm,
                sin2thetaW=sin2thetaW,
                c10_mass_mode=c10_mass_mode,
            ).dsigma_cm2_per_keV
            cont = float(_trapz(_asarray(ds) * phi(eg), eg))
        prompt = 0.0
        if flavor == 'mu' and float(c.to_energy_gev(mu_E0, 'MeV')) >= Emin_GeV:
            ds_mu = differential_cross_section_nn(
                resp,
                float(ER_keV),
                float(mu_E0),
                rho=source_state,
                wc_triplets=dict(wc_triplets or {}),
                include_sm=include_sm,
                sin2thetaW=sin2thetaW,
                c10_mass_mode=c10_mass_mode,
            ).dsigma_cm2_per_keV
            prompt = float(mu_weight) * float(ds_mu)
        out[i] = (cont + prompt) / mass_kg
    return out


def _folded_counts(resp, flux_obj, ER_grid, fold, flavor, wc_triplets, include_sm, sin2thetaW, c10_mass_mode, n_enu):
    rate = _rate_per_kg(
        resp,
        flux_obj,
        ER_grid,
        flavor,
        wc_triplets,
        include_sm,
        sin2thetaW,
        c10_mass_mode,
        n_enu,
        source_state=_legacy_sns_component_state(flavor),
    )
    return np.sum(rate[:, None] * fold, axis=0) * float(flux_obj['basic'].get('detectorMassKg', 1.0))


def _er_grid(resp, n_er):
    A = int(resp.basic.get('A'))
    grid = np.linspace(0.1, enr_max_keV(A, Emax_MeV=emax_muon_dar_mev()), int(n_er), dtype=float)
    return grid, _trapz_weights(grid)

@dataclass(frozen=True)
class DNdPEResult:
    pe: float
    dNdPE_per_kg: float
    meta: Dict[str, Any]

def empirical_dNdPE_response_csi(resp: Any, pe: float, flux_obj: Dict[str, Any], *, source_state: NeutrinoState, flavor: Flavor='all', source: str='SNS', smear_func: Callable[[ArrayLike, float], ArrayLike]=p_smearing_csi, ER_min_keV: float=0.1, n_ER: int=201, n_Enu: int=600, basis: Basis='np', left_wcs: Optional[Dict[str, complex]]=None, wc_triplets: Optional[Dict[Tuple[int, int, str], complex]]=None, include_sm: bool=False, sin2thetaW: Optional[float]=None, c10_mass_mode: str='quark_mass_resolved') -> DNdPEResult:
    A = int(resp.basic.get('A'))
    amu_kg = 1.6605390666e-27
    M_nucleus_kg = A * amu_kg
    Emax_MeV = emax_muon_dar_mev()
    ER_max_keV = enr_max_keV(A, Emax_MeV=Emax_MeV)
    ER_grid = np.linspace(ER_min_keV, ER_max_keV, int(n_ER))
    phi_tot = flux_obj['measured']['totalContinuous']
    phi_e = flux_obj['measured']['e']
    phi_mub = flux_obj['measured']['mub']
    include_mu_line = source == 'SNS' and flavor in ('all', 'mu', 'mmb')
    mu_E0_MeV, mu_weight_cm2 = flux_obj['measured']['muLine']

    def phi_cont(E_MeV: ArrayLike) -> ArrayLike:
        if flavor == 'all':
            return phi_tot(E_MeV)
        if flavor == 'e':
            return phi_e(E_MeV)
        if flavor == 'mub':
            return phi_mub(E_MeV)
        if flavor == 'mmb':
            return phi_mub(E_MeV)
        if flavor == 'mu':
            return 0.0 if np.isscalar(E_MeV) else np.zeros_like(_asarray(E_MeV))
        raise ValueError(f'Unknown flavor {flavor!r}')
    Enu_grid = np.linspace(0.0, Emax_MeV, int(n_Enu))
    rate_per_kg_per_keV = np.zeros_like(ER_grid)
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    for i, ER in enumerate(ER_grid):
        Enu_min_MeV = float(c.from_energy_gev(
            minimum_neutrino_energy_GeV(float(ER) * 1.0e-6, mA_GeV),
            'MeV',
        ))
        if Enu_min_MeV >= Emax_MeV:
            rate_per_kg_per_keV[i] = 0.0
            continue
        mask = Enu_grid >= Enu_min_MeV
        if not np.any(mask):
            rate_per_kg_per_keV[i] = 0.0
            continue
        Eg = Enu_grid[mask]
        ds = differential_cross_section_nn(resp, ER_keV=float(ER), Enu_MeV=Eg, rho=source_state, basis=basis, left_wcs=left_wcs, wc_triplets=wc_triplets, include_sm=include_sm, sin2thetaW=sin2thetaW, c10_mass_mode=c10_mass_mode).dsigma_cm2_per_keV
        phi_vals = _asarray(phi_cont(Eg))
        integrand = _asarray(ds) * phi_vals
        cont_int = _trapz(integrand, Eg)
        mu_term = 0.0
        if include_mu_line:
            ds_mu = differential_cross_section_nn(resp, ER_keV=float(ER), Enu_MeV=float(mu_E0_MeV), rho=source_state, basis=basis, left_wcs=left_wcs, wc_triplets=wc_triplets, include_sm=include_sm, sin2thetaW=sin2thetaW, c10_mass_mode=c10_mass_mode).dsigma_cm2_per_keV
            mu_term = float(mu_weight_cm2) * float(ds_mu)
        rate_per_nucleus_per_keV = cont_int + mu_term
        rate_per_kg_per_keV[i] = rate_per_nucleus_per_keV / M_nucleus_kg
    smear_vals = np.asarray([float(smear_func(pe, float(er))) for er in ER_grid], dtype=float)
    integrand_ER = rate_per_kg_per_keV * smear_vals
    dNdPE = _trapz(integrand_ER, ER_grid)
    meta = {'A': A, 'ER_min_keV': ER_min_keV, 'ER_max_keV': ER_max_keV, 'Emax_MeV': Emax_MeV, 'mu_line': {'included': include_mu_line, 'E0_MeV': float(mu_E0_MeV), 'weight_cm^-2': float(mu_weight_cm2)}, 'basis': basis, 'flavor': flavor, 'n_ER': int(n_ER), 'n_Enu': int(n_Enu)}
    return DNdPEResult(pe=float(pe), dNdPE_per_kg=float(if_positive(dNdPE)), meta=meta)

def bin_events_csi(resp: Any, flux_obj: Dict[str, Any], pe_bins: np.ndarray, *, efficiency: Callable[[ArrayLike], ArrayLike], source_state: NeutrinoState, flavor: Flavor='all', source: str='SNS', smear_func: Callable[[ArrayLike, float], ArrayLike]=p_smearing_csi, basis: Basis='np', left_wcs: Optional[Dict[str, complex]]=None, wc_triplets: Optional[Dict[Tuple[int, int, str], complex]]=None, include_sm: bool=False, sin2thetaW: Optional[float]=None, ER_min_keV: float=0.1, n_ER: int=201, n_Enu: int=600, pe_eval_grid: Optional[np.ndarray]=None, pe_min: Optional[float]=None, pe_max: Optional[float]=None, pe_step: float=3.0, n_PE_bin: int=64, c10_mass_mode: str='quark_mass_resolved') -> np.ndarray:
    pe_bins = np.asarray(pe_bins, dtype=float)
    if pe_bins.ndim != 1 or pe_bins.size < 2:
        raise ValueError('pe_bins must be a 1D array of bin edges')
    if np.any(np.diff(pe_bins) <= 0):
        raise ValueError('pe_bins must be strictly increasing')
    if int(n_PE_bin) < 2:
        raise ValueError('n_PE_bin must be >= 2')
    mass_kg = float(flux_obj['basic'].get('detectorMassKg', 14.57))
    if pe_eval_grid is None:
        a0 = float(pe_bins[0]) if pe_min is None else float(pe_min)
        b0 = float(pe_bins[-1]) if pe_max is None else float(pe_max)
        if pe_step <= 0:
            raise ValueError('pe_step must be positive')
        min_bin_width = float(np.min(np.diff(pe_bins)))
        if float(pe_step) > min_bin_width:
            raise ValueError(
                'pe_step must not exceed the smallest PE bin width when '
                'pe_eval_grid is generated automatically'
            )
        pe_eval_grid = np.arange(a0, b0 + 0.5 * pe_step, pe_step, dtype=float)
    else:
        pe_eval_grid = np.asarray(pe_eval_grid, dtype=float)
    if pe_eval_grid.ndim != 1 or pe_eval_grid.size < 2:
        raise ValueError('pe_eval_grid must be a 1D array with at least 2 points')
    if np.any(np.diff(pe_eval_grid) <= 0):
        raise ValueError('pe_eval_grid must be strictly increasing')
    dndpe_grid = np.array([empirical_dNdPE_response_csi(resp, pe=float(pe), flux_obj=flux_obj, source_state=source_state, flavor=flavor, source=source, smear_func=smear_func, ER_min_keV=ER_min_keV, n_ER=n_ER, n_Enu=n_Enu, basis=basis, left_wcs=left_wcs, wc_triplets=wc_triplets, include_sm=include_sm, sin2thetaW=sin2thetaW, c10_mass_mode=c10_mass_mode).dNdPE_per_kg for pe in pe_eval_grid], dtype=float)
    out = np.zeros(pe_bins.size - 1, dtype=float)
    for i in range(pe_bins.size - 1):
        a, b = (float(pe_bins[i]), float(pe_bins[i + 1]))
        pe_sub = np.linspace(a, b, int(n_PE_bin), dtype=float)
        vals_sub = np.interp(pe_sub, pe_eval_grid, dndpe_grid, left=0.0, right=0.0)
        eff = _asarray(efficiency(pe_sub))
        out[i] = _trapz(vals_sub * eff, pe_sub) * mass_kg
    return out

__all__ = [
    "DNdPEResult",
    "empirical_dNdPE_response_csi",
    "bin_events_csi",
    "_trapz_weights",
    "_choose_phi_cont",
    "_rate_per_kg",
    "_folded_counts",
    "_er_grid",
]
