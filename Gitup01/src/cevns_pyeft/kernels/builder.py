"""Legacy dataset-routed builders; composed models use kernels.compile_fast.

Particle response polynomials are owned by theory.li2026.responses. This
module retains the historical conversion and array conventions for old APIs.
"""
from __future__ import annotations

import json
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Mapping, Optional, Sequence, Tuple

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.foundation.constants import AMU_GEV, from_energy_gev, to_energy_gev
from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS as load_flux
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
    A_TARGET,
    DEFAULT_ACCEPTANCE,
    PE_BINS_9,
    combine_equal_stoichiometry,
    efficiency as csi_efficiency,
)
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import (
    CSI2017_BINS_25,
    CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    CSI2017_PE_PER_KEV,
)
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import (
    AR_BINS_12,
    AR_DEFAULT_EFFICIENCY_RELATIVE_PATH,
)
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import _er_grid
from cevns_pyeft.rates.differential import (
    emax_muon_dar_mev,
    enr_max_keV,
    p_smearing_csi,
)
from cevns_pyeft.theory.kinematics import minimum_neutrino_energy_GeV
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
from cevns_pyeft.theory.li2026.flavor import zero_flavor_matrix
from cevns_pyeft.theory.li2026.operators import get_operator_spec

from .basis import BasisElement, Triplet, li2026_left_basis, li2026_left_basis_current

SourceFlavor = Literal['e', 'mu', 'mub']
TargetMode = Literal['Cs133', 'I127', 'CsI', 'all']
FLAVORS: Tuple[SourceFlavor, ...] = ('e', 'mu', 'mub')
DEFAULT_FLAVORS: Tuple[SourceFlavor, ...] = FLAVORS
DEFAULT_TARGETS: Tuple[str, ...] = ('Cs133', 'I127')
RAW_TARGETS: Tuple[str, ...] = DEFAULT_TARGETS
TARGET_KEY_MAP: Dict[str, str] = {'Cs133': 'Cs133', 'I127': 'I'}
CHANNELS: Tuple[str, ...] = ('M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta')
_CHANNEL_INDEX: Dict[str, int] = {name: i for i, name in enumerate(CHANNELS)}
_CI_KEYS: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14)
_INVGEV_TO_CM: float = 1.973269804e-14
_CONV_DSIGMA: float = 1e-06 * _INVGEV_TO_CM ** 2
FLAVOR_ACCEPTANCE_ONE = {"e": 1.0, "mu": 1.0, "mub": 1.0}


def _left_operator_template(triplet: Triplet) -> tuple[np.ndarray, tuple[int, int]]:
    matrix = zero_flavor_matrix()
    if get_operator_spec(triplet).lepton_number == "LNV":
        matrix[0, 1] = 1.0 + 0.0j
        return matrix, (0, 1)
    matrix[0, 0] = 1.0 + 0.0j
    return matrix, (0, 0)


def _trapz(y: np.ndarray, x: np.ndarray, axis: int = -1) -> np.ndarray:
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return trapezoid(y, x, axis=axis)
    return np.trapz(y, x, axis=axis)


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


def _response_matrix_np_safe(resp: Any, channel: str, y: float) -> np.ndarray:
    try:
        W = resp.W_np(channel, y)
    except Exception:
        return np.zeros((2, 2), dtype=float)
    if not isinstance(W, list):
        return np.zeros((2, 2), dtype=float)
    arr = np.zeros((2, 2), dtype=float)
    for i in range(2):
        if i >= len(W) or not isinstance(W[i], list):
            continue
        for j in range(2):
            try:
                val = W[i][j]
            except Exception:
                val = 0.0
            arr[i, j] = float(val) if val is not None else 0.0
    return arr


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


def _target_output_names(target_mode: TargetMode) -> List[str]:
    if target_mode == 'Cs133':
        return ['Cs133']
    if target_mode == 'I127':
        return ['I127']
    if target_mode == 'CsI':
        return ['CsI']
    if target_mode == 'all':
        return ['Cs133', 'I127', 'CsI']
    raise ValueError(f'Unknown target_mode={target_mode!r}')


def _select_target_arrays(raw: Mapping[str, np.ndarray], target_mode: TargetMode) -> np.ndarray:
    names = _target_output_names(target_mode)
    out: List[np.ndarray] = []
    for name in names:
        if name == 'CsI':
            out.append(combine_equal_stoichiometry(raw['Cs133'], raw['I127']))
        else:
            out.append(np.asarray(raw[name]))
    return np.stack(out, axis=0)

@dataclass(frozen=True)
class TargetStatic:
    target: str
    A: int
    mA_GeV: float
    nucleus_mass_kg: float
    ER_grid_keV: np.ndarray
    ER_weights_keV: np.ndarray
    q0_GeV: np.ndarray
    q2_GeV2: np.ndarray
    qabs_GeV: np.ndarray
    qabs2_GeV2: np.ndarray
    W_by_ER: np.ndarray
    fold_kernel: np.ndarray

@dataclass(frozen=True)
class KernelPayload:
    metadata: Dict[str, Any]
    full_kernel: np.ndarray
    diag: np.ndarray
    pair_re: np.ndarray
    pair_im: np.ndarray
    pair_index: np.ndarray

def _build_target_static(responses_json: str, *, target: str, pe_bins: np.ndarray, ER_min_keV: float, n_ER: int, n_PE_sub: int, pe_step: Optional[float]=None, basis: Literal['np', 'iso']='np') -> TargetStatic:
    if basis != 'np':
        raise NotImplementedError("The matrixized scan currently supports basis='np' only")
    resp_db = ResponseDB(str(responses_json))
    resp = resp_db.get(TARGET_KEY_MAP[target])
    A = int(resp.get_basic('A'))
    mA_GeV = A * float(c.AMU_GEV)
    amu_kg = 1.6605390666e-27
    nucleus_mass_kg = A * amu_kg
    ER_max_keV = enr_max_keV(A, Emax_MeV=emax_muon_dar_mev())
    ER_grid = np.linspace(float(ER_min_keV), float(ER_max_keV), int(n_ER), dtype=float)
    ER_weights = _trapz_weights(ER_grid)
    q0_GeV = ER_grid * 1e-06
    qabs2_GeV2 = 2.0 * mA_GeV * q0_GeV
    qabs_GeV = np.sqrt(np.maximum(qabs2_GeV2, 0.0))
    q2_GeV2 = q0_GeV * q0_GeV - qabs2_GeV2
    H = len(CHANNELS)
    W_by_ER = np.zeros((ER_grid.size, H, 2, 2), dtype=float)
    b_osc = float(resp.get_basic('b'))
    for ier in range(ER_grid.size):
        y = (0.5 * qabs_GeV[ier] * b_osc) ** 2
        for h, channel in enumerate(CHANNELS):
            W_by_ER[ier, h] = _response_matrix_np_safe(resp, channel, float(y))
    M = pe_bins.size - 1
    fold_kernel = np.zeros((ER_grid.size, M), dtype=float)
    pe_eval_grid: Optional[np.ndarray] = None
    if pe_step is not None:
        if float(pe_step) <= 0.0:
            raise ValueError("pe_step must be positive")
        min_bin_width = float(np.min(np.diff(pe_bins)))
        if float(pe_step) > min_bin_width:
            raise ValueError(
                "pe_step must not exceed the smallest PE bin width when "
                "matching the Slow PE interpolation grid"
            )
        pe_eval_grid = np.arange(
            float(pe_bins[0]),
            float(pe_bins[-1]) + 0.5 * float(pe_step),
            float(pe_step),
            dtype=float,
        )
    for ier, ER in enumerate(ER_grid):
        smear_grid = None
        if pe_eval_grid is not None:
            smear_grid = np.asarray(
                [float(p_smearing_csi(float(x), float(ER))) for x in pe_eval_grid],
                dtype=float,
            )
        for ib in range(M):
            left = float(pe_bins[ib])
            right = float(pe_bins[ib + 1])
            xs = np.linspace(left, right, int(n_PE_sub), dtype=float)
            if smear_grid is None:
                smear = np.asarray(
                    [float(p_smearing_csi(float(x), float(ER))) for x in xs],
                    dtype=float,
                )
            else:
                smear = np.interp(xs, pe_eval_grid, smear_grid, left=0.0, right=0.0)
            ys = np.asarray([float(csi_efficiency(float(x))) for x in xs], dtype=float) * smear
            fold_kernel[ier, ib] = float(_trapz(ys, xs)) * ER_weights[ier]
    return TargetStatic(target=target, A=A, mA_GeV=mA_GeV, nucleus_mass_kg=nucleus_mass_kg, ER_grid_keV=ER_grid, ER_weights_keV=ER_weights, q0_GeV=q0_GeV, q2_GeV2=q2_GeV2, qabs_GeV=qabs_GeV, qabs2_GeV2=qabs2_GeV2, W_by_ER=W_by_ER, fold_kernel=fold_kernel)

def _build_ci_units(basis_elements, **kwargs):
    from cevns_pyeft.theory.li2026.coefficients import operator_ci_units
    return operator_ci_units(tuple(item.triplet for item in basis_elements), **kwargs)


def _amplitude_kernel_by_channel(**kwargs):
    from cevns_pyeft.theory.li2026.coefficients import amplitude_coefficients_by_channel
    # Keep the legacy array convention and legacy conversion constant unchanged.
    return amplitude_coefficients_by_channel(**kwargs, hermitianize=False)


def _scan_ord(ci, i, tau, j, taup):
    """Legacy bilinear helper retained for existing imports."""
    return np.outer(np.conjugate(ci[:, i, tau]), ci[:, j, taup])


def _scan_sym(ci, i, tau, j, taup):
    return _scan_ord(ci, i, tau, j, taup) + _scan_ord(ci, j, tau, i, taup)


def _scan_anti(ci, i, tau, j, taup):
    return _scan_ord(ci, i, tau, j, taup) - _scan_ord(ci, j, tau, i, taup)


def _build_one_target_kernel(responses_json: str, dataset: str, target: str, basis_elements: Sequence[BasisElement], pe_bins: np.ndarray, ER_min_keV: float, n_ER: int, n_Enu: int, n_PE_sub: int, pe_step: Optional[float], c10_mass_mode: str, flavor_acceptance: Mapping[str, float]) -> Tuple[str, np.ndarray]:
    flux_obj = load_flux(dataset)
    detector_mass_kg = float(flux_obj['basic'].get('detectorMassKg', 14.57))
    static = _build_target_static(responses_json, target=target, pe_bins=pe_bins, ER_min_keV=ER_min_keV, n_ER=n_ER, n_PE_sub=n_PE_sub, pe_step=pe_step, basis='np')
    B = len(basis_elements)
    F = len(FLAVORS)
    H = len(CHANNELS)
    M = pe_bins.size - 1
    Rn = static.ER_grid_keV.size
    kernel_rate = np.zeros((F, H, B, B, Rn), dtype=complex)
    mA = float(static.mA_GeV)
    mN = float(DEFAULT_LECS.m_N)
    Emax_MeV = emax_muon_dar_mev()
    Enu_grid_MeV = np.linspace(0.0, float(Emax_MeV), int(n_Enu), dtype=float)
    phi_cont_funcs = {flv: _choose_phi_cont(flux_obj, flv) for flv in FLAVORS}
    mu_E0_MeV, mu_weight_cm2 = flux_obj['measured']['muLine']
    mu_E0_GeV = float(c.to_energy_gev(float(mu_E0_MeV), 'MeV'))
    for ier in range(Rn):
        q0 = float(static.q0_GeV[ier])
        q2 = float(static.q2_GeV2[ier])
        qabs = float(static.qabs_GeV[ier])
        qabs2 = float(static.qabs2_GeV2[ier])
        W_slice = static.W_by_ER[ier]
        E_min_GeV = minimum_neutrino_energy_GeV(q0, mA)
        E_min_MeV = float(c.from_energy_gev(E_min_GeV, 'MeV'))
        mask = Enu_grid_MeV >= E_min_MeV
        cont_e = np.zeros((H, B, B), dtype=complex)
        cont_mub = np.zeros((H, B, B), dtype=complex)
        if np.any(mask):
            Eg_MeV = Enu_grid_MeV[mask]
            Eg_GeV = np.asarray(c.to_energy_gev(Eg_MeV, 'MeV'), dtype=float)
            ds_cont = np.zeros((Eg_GeV.size, H, B, B), dtype=complex)
            for ie, Enu_GeV in enumerate(Eg_GeV):
                ci = _build_ci_units(basis_elements, E_nu_GeV=float(Enu_GeV), q0_GeV=q0, q2_GeV2=q2, qabs_GeV=qabs, qabs2_GeV2=qabs2, mA_GeV=mA, c10_mass_mode=c10_mass_mode)
                amp = _amplitude_kernel_by_channel(E_nu_GeV=float(Enu_GeV), qabs_GeV=qabs, mA_GeV=mA, mN_GeV=mN, ci=ci, W_slice=W_slice)
                pref = mA / (8.0 * math.pi * float(Enu_GeV) * float(Enu_GeV))
                ds_cont[ie] = pref * _CONV_DSIGMA * amp
            phi_e = phi_cont_funcs['e'](Eg_MeV)
            phi_mub = phi_cont_funcs['mub'](Eg_MeV)
            cont_e = _trapz(ds_cont * phi_e[:, None, None, None], Eg_MeV, axis=0)
            cont_mub = _trapz(ds_cont * phi_mub[:, None, None, None], Eg_MeV, axis=0)
        mu_term = np.zeros((H, B, B), dtype=complex)
        if mu_E0_GeV >= E_min_GeV and mu_weight_cm2 != 0.0:
            ci_mu = _build_ci_units(basis_elements, E_nu_GeV=mu_E0_GeV, q0_GeV=q0, q2_GeV2=q2, qabs_GeV=qabs, qabs2_GeV2=qabs2, mA_GeV=mA, c10_mass_mode=c10_mass_mode)
            amp_mu = _amplitude_kernel_by_channel(E_nu_GeV=mu_E0_GeV, qabs_GeV=qabs, mA_GeV=mA, mN_GeV=mN, ci=ci_mu, W_slice=W_slice)
            pref_mu = mA / (8.0 * math.pi * mu_E0_GeV * mu_E0_GeV)
            mu_term = float(mu_weight_cm2) * (pref_mu * _CONV_DSIGMA * amp_mu)
        kernel_rate[FLAVORS.index('e'), :, :, :, ier] = cont_e / static.nucleus_mass_kg
        kernel_rate[FLAVORS.index('mub'), :, :, :, ier] = cont_mub / static.nucleus_mass_kg
        kernel_rate[FLAVORS.index('mu'), :, :, :, ier] = mu_term / static.nucleus_mass_kg
    full_kernel = np.einsum('fhabr,rm->fhabm', kernel_rate, static.fold_kernel, optimize=True)
    full_kernel = full_kernel * detector_mass_kg
    for ifl, flv in enumerate(FLAVORS):
        full_kernel[ifl] *= float(flavor_acceptance[flv])
    return (target, full_kernel)

def _parallel_target_build(responses_json: str, dataset: str, raw_targets: Sequence[str], basis_elements: Sequence[BasisElement], pe_bins: np.ndarray, ER_min_keV: float, n_ER: int, n_Enu: int, n_PE_sub: int, pe_step: Optional[float], c10_mass_mode: str, flavor_acceptance: Mapping[str, float], n_jobs: int) -> Dict[str, np.ndarray]:
    if int(n_jobs) <= 1 or len(raw_targets) <= 1:
        return {tgt: _build_one_target_kernel(responses_json, dataset, tgt, basis_elements, pe_bins, ER_min_keV, n_ER, n_Enu, n_PE_sub, pe_step, c10_mass_mode, flavor_acceptance)[1] for tgt in raw_targets}
    out: Dict[str, np.ndarray] = {}
    with ProcessPoolExecutor(max_workers=min(int(n_jobs), len(raw_targets))) as ex:
        futs = {ex.submit(_build_one_target_kernel, responses_json, dataset, tgt, basis_elements, pe_bins, ER_min_keV, n_ER, n_Enu, n_PE_sub, pe_step, c10_mass_mode, flavor_acceptance): tgt for tgt in raw_targets}
        for fut in as_completed(futs):
            tgt, arr = fut.result()
            out[tgt] = arr
    return out

def _kernel_to_diag_pair_templates(full_kernel: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    arr = np.asarray(full_kernel)
    if arr.ndim != 6:
        raise ValueError('full_kernel must have shape (T,F,H,B,B,M)')
    Tsel, F, H, B, B2, M = arr.shape
    if B != B2:
        raise ValueError('Kernel matrix must be square in basis indices')
    diag = np.zeros((B, Tsel, F, H, M), dtype=float)
    for a in range(B):
        diag[a] = np.real(arr[:, :, :, a, a, :])
    pair_list: List[Tuple[int, int]] = []
    pair_re_list: List[np.ndarray] = []
    pair_im_list: List[np.ndarray] = []
    for a in range(B):
        for b in range(a + 1, B):
            pair_list.append((a, b))
            kab = arr[:, :, :, a, b, :]
            pair_re_list.append(np.real(kab))
            pair_im_list.append(-np.imag(kab))
    pair_index = np.asarray(pair_list, dtype=int)
    if pair_re_list:
        pair_re = np.stack(pair_re_list, axis=0)
        pair_im = np.stack(pair_im_list, axis=0)
    else:
        pair_re = np.zeros((0, Tsel, F, H, M), dtype=float)
        pair_im = np.zeros((0, Tsel, F, H, M), dtype=float)
    return (diag, pair_re, pair_im, pair_index)

def reconstruct_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    arr = np.asarray(full_kernel)
    coeffs = np.asarray(coeffs, dtype=complex)
    if arr.ndim == 5:
        return np.einsum('a,fhabm,b->fhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
    if arr.ndim == 6:
        return np.einsum('a,tfhabm,b->tfhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
    raise ValueError('full_kernel must have shape (F,H,B,B,M) or (T,F,H,B,B,M)')

def reconstruct_from_pair_templates(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    coeffs = np.asarray(coeffs, dtype=complex)
    B = coeffs.size
    out = np.zeros_like(np.asarray(diag[0]), dtype=float)
    for a in range(B):
        out = out + abs(coeffs[a]) ** 2 * np.asarray(diag[a], dtype=float)
    for k, (a, b) in enumerate(np.asarray(pair_index, dtype=int)):
        z = np.conjugate(coeffs[a]) * coeffs[b]
        out = out + 2.0 * np.real(z) * np.asarray(pair_re[k], dtype=float)
        out = out + 2.0 * np.imag(z) * np.asarray(pair_im[k], dtype=float)
    return out

def reconstruct_real_events_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_full_kernel(full_kernel, coeffs))

def reconstruct_real_events_from_pair_templates(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_pair_templates(diag=diag, pair_re=pair_re, pair_im=pair_im, pair_index=pair_index, coeffs=coeffs))

def build_matrixized_kernel(*, responses_json: str, dataset: str='CsI2021', basis_elements: Optional[Sequence[BasisElement]]=None, pe_bins: Optional[np.ndarray]=None, target_mode: TargetMode='CsI', ER_min_keV: float=0.1, n_ER: int=41, n_Enu: int=300, n_PE_sub: int=64, pe_step: Optional[float]=3.0, c10_mass_mode: str='quark_mass_resolved', flavor_acceptance: Optional[Mapping[str, float]]=None, n_jobs: int=1) -> KernelPayload:
    if basis_elements is None:
        basis_elements = li2026_left_basis()
    if pe_bins is None:
        pe_bins = PE_BINS_9
    pe_bins = np.asarray(pe_bins, dtype=float)
    if flavor_acceptance is None:
        flavor_acceptance = DEFAULT_ACCEPTANCE
    raw = _parallel_target_build(responses_json=responses_json, dataset=dataset, raw_targets=RAW_TARGETS, basis_elements=basis_elements, pe_bins=pe_bins, ER_min_keV=ER_min_keV, n_ER=n_ER, n_Enu=n_Enu, n_PE_sub=n_PE_sub, pe_step=pe_step, c10_mass_mode=c10_mass_mode, flavor_acceptance=flavor_acceptance, n_jobs=n_jobs)
    full_kernel = _select_target_arrays(raw, target_mode)
    diag, pair_re, pair_im, pair_index = _kernel_to_diag_pair_templates(full_kernel)
    metadata: Dict[str, Any] = {'model': 'li2026_matrixized_v2', 'flavor_schema_version': 1, 'neutrino_flavor_order': ['e', 'mu', 'tau'], 'wilson_flavor_axis': {'row': 'final', 'column': 'initial'}, 'operator_basis_size': len(basis_elements), 'coefficient_shape': [len(basis_elements), 3, 3], 'lnc_lnv_interference': False, 'responses': str(responses_json), 'dataset': str(dataset), 'target_mode': str(target_mode), 'targets': _target_output_names(target_mode), 'source_flavors': list(FLAVORS), 'channels': list(CHANNELS), 'basis': [asdict(b) for b in basis_elements], 'pe_bins': pe_bins.tolist(), 'ER_min_keV': float(ER_min_keV), 'n_ER': int(n_ER), 'n_Enu': int(n_Enu), 'n_PE_sub': int(n_PE_sub), 'n_PE_bin': int(n_PE_sub), 'pe_step': None if pe_step is None else float(pe_step), 'detector_fold_contract': 'Slow PE interpolation grid' if pe_step is not None else 'direct PE sub-bin smearing', 'c10_mass_mode': str(c10_mass_mode), 'n_jobs': int(n_jobs), 'flavor_acceptance': {str(k): float(v) for k, v in flavor_acceptance.items()}, 'kernel_shape': list(np.asarray(full_kernel).shape), 'diag_shape': list(np.asarray(diag).shape), 'pair_re_shape': list(np.asarray(pair_re).shape), 'pair_im_shape': list(np.asarray(pair_im).shape), 'pair_index_shape': list(np.asarray(pair_index).shape), 'notes': ['full_kernel stores operator-space transfer K[target,source_flavor,channel,a,b,bin]; physical Flavor enters only through Tr[rho C_a^dagger C_b] during reconstruction', 'Active basis includes only LEFT coefficients with NR c_i mappings documented in docs/theory/li2026_draft_checked_wilson_R_formulas.md', 'SigmaPDelta is retained as an explicit channel axis; the checked draft gives only the compact form, not an expanded c_i formula', 'CsI is combined from Cs133 and I127 with 133:127 stoichiometric weights at the event-kernel level']}
    return KernelPayload(metadata=metadata, full_kernel=np.asarray(full_kernel), diag=np.asarray(diag), pair_re=np.asarray(pair_re), pair_im=np.asarray(pair_im), pair_index=np.asarray(pair_index))


def _target_static(
    responses_json: str | Path,
    *,
    target: str,
    er_grid_keV: np.ndarray,
    fold_kernel: np.ndarray,
    nucleus_mass_kg=None,
) -> TargetStatic:
    resp = ResponseDB(str(responses_json)).get(TARGET_KEY_MAP.get(target, target))
    A = int(resp.get_basic("A"))
    mA_GeV = A * float(AMU_GEV)
    q0 = np.asarray(er_grid_keV, dtype=float) * 1.0e-6
    qabs2 = 2.0 * mA_GeV * q0
    qabs = np.sqrt(np.maximum(qabs2, 0.0))
    q2 = q0 * q0 - qabs2

    W_by_ER = np.zeros((q0.size, len(CHANNELS), 2, 2), dtype=float)
    b_osc = float(resp.get_basic("b"))
    for i, q in enumerate(qabs):
        y = (0.5 * float(q) * b_osc) ** 2
        for h, channel in enumerate(CHANNELS):
            W_by_ER[i, h] = _response_matrix_np_safe(resp, channel, y)

    return TargetStatic(
        target=target,
        A=A,
        mA_GeV=mA_GeV,
        nucleus_mass_kg=A * 1.6605390666e-27 if nucleus_mass_kg is None else float(nucleus_mass_kg),
        ER_grid_keV=np.asarray(er_grid_keV, dtype=float),
        ER_weights_keV=np.zeros_like(np.asarray(er_grid_keV, dtype=float)),
        q0_GeV=q0,
        q2_GeV2=q2,
        qabs_GeV=qabs,
        qabs2_GeV2=qabs2,
        W_by_ER=W_by_ER,
        fold_kernel=np.asarray(fold_kernel, dtype=float),
    )

def _build_one_target_kernel_csi2017_ar(
    *,
    static: TargetStatic,
    dataset: str,
    basis_elements: Sequence[BasisElement],
    n_enu: int,
    c10_mass_mode: str,
    detector_mass_kg: float,
    flavor_acceptance: Mapping[str, float] = FLAVOR_ACCEPTANCE_ONE,
    flux=None,
) -> np.ndarray:
    flux = load_flux(dataset) if flux is None else flux
    B, F, H = len(basis_elements), len(FLAVORS), len(CHANNELS)
    R = static.ER_grid_keV.size
    kernel_rate = np.zeros((F, H, B, B, R), dtype=complex)
    mA, mN = float(static.mA_GeV), float(DEFAULT_LECS.m_N)

    enu_MeV = np.linspace(0.0, emax_muon_dar_mev(), int(n_enu), dtype=float)
    phi_cont = {flv: _choose_phi_cont(flux, flv) for flv in FLAVORS}
    mu_E0_MeV, mu_weight_cm2 = flux["measured"]["muLine"]
    mu_E0_GeV = float(to_energy_gev(float(mu_E0_MeV), "MeV"))

    for ir in range(R):
        q0 = float(static.q0_GeV[ir])
        q2 = float(static.q2_GeV2[ir])
        qabs = float(static.qabs_GeV[ir])
        qabs2 = float(static.qabs2_GeV2[ir])
        W_slice = static.W_by_ER[ir]
        E_min_GeV = minimum_neutrino_energy_GeV(q0, mA)
        E_min_MeV = float(from_energy_gev(E_min_GeV, "MeV"))

        mask = enu_MeV >= E_min_MeV
        cont_e = np.zeros((H, B, B), dtype=complex)
        cont_mub = np.zeros((H, B, B), dtype=complex)
        if np.any(mask):
            eg_MeV = enu_MeV[mask]
            eg_GeV = np.asarray(to_energy_gev(eg_MeV, "MeV"), dtype=float)
            ds = np.zeros((eg_GeV.size, H, B, B), dtype=complex)
            for ie, Enu_GeV in enumerate(eg_GeV):
                ci = _build_ci_units(
                    basis_elements,
                    E_nu_GeV=float(Enu_GeV),
                    q0_GeV=q0,
                    q2_GeV2=q2,
                    qabs_GeV=qabs,
                    qabs2_GeV2=qabs2,
                    mA_GeV=mA,
                    c10_mass_mode=c10_mass_mode,
                )
                amp = _amplitude_kernel_by_channel(
                    E_nu_GeV=float(Enu_GeV),
                    qabs_GeV=qabs,
                    mA_GeV=mA,
                    mN_GeV=mN,
                    ci=ci,
                    W_slice=W_slice,
                )
                ds[ie] = (mA / (8.0 * math.pi * float(Enu_GeV) ** 2)) * _CONV_DSIGMA * amp
            cont_e = _trapz(ds * phi_cont["e"](eg_MeV)[:, None, None, None], eg_MeV, axis=0)
            cont_mub = _trapz(ds * phi_cont["mub"](eg_MeV)[:, None, None, None], eg_MeV, axis=0)

        mu_term = np.zeros((H, B, B), dtype=complex)
        if mu_E0_GeV >= E_min_GeV and float(mu_weight_cm2) != 0.0:
            ci = _build_ci_units(
                basis_elements,
                E_nu_GeV=mu_E0_GeV,
                q0_GeV=q0,
                q2_GeV2=q2,
                qabs_GeV=qabs,
                qabs2_GeV2=qabs2,
                mA_GeV=mA,
                c10_mass_mode=c10_mass_mode,
            )
            amp = _amplitude_kernel_by_channel(
                E_nu_GeV=mu_E0_GeV,
                qabs_GeV=qabs,
                mA_GeV=mA,
                mN_GeV=mN,
                ci=ci,
                W_slice=W_slice,
            )
            mu_term = float(mu_weight_cm2) * (
                mA / (8.0 * math.pi * mu_E0_GeV * mu_E0_GeV)
            ) * _CONV_DSIGMA * amp

        kernel_rate[FLAVORS.index("e"), :, :, :, ir] = cont_e / static.nucleus_mass_kg
        kernel_rate[FLAVORS.index("mub"), :, :, :, ir] = cont_mub / static.nucleus_mass_kg
        kernel_rate[FLAVORS.index("mu"), :, :, :, ir] = mu_term / static.nucleus_mass_kg

    full = np.einsum("fhabr,rm->fhabm", kernel_rate, static.fold_kernel, optimize=True)
    full = full * float(detector_mass_kg)
    for i, flv in enumerate(FLAVORS):
        full[i] *= float(flavor_acceptance[flv])
    return full

def _payload_dict(payload: KernelPayload) -> Dict[str, Any]:
    return {
        "basis": payload.metadata["basis"],
        "targets": payload.metadata["targets"],
        "source_flavors": payload.metadata["source_flavors"],
        "channels": payload.metadata["channels"],
        "pe_bins": np.asarray(payload.metadata["pe_bins"], dtype=float),
        "kernel_axis_kind": "channel_resolved_full_li2026",
        "metadata": payload.metadata,
        "full_kernel": np.asarray(payload.full_kernel),
        "diag": np.asarray(payload.diag),
        "pair_re": np.asarray(payload.pair_re),
        "pair_im": np.asarray(payload.pair_im),
        "pair_index": np.asarray(payload.pair_index),
    }

def _make_payload(
    *,
    metadata: Dict[str, Any],
    full_kernel: np.ndarray,
) -> Dict[str, Any]:
    diag, pair_re, pair_im, pair_index = _kernel_to_diag_pair_templates(full_kernel)
    metadata = dict(metadata)
    metadata.update(
        kernel_shape=list(np.asarray(full_kernel).shape),
        diag_shape=list(np.asarray(diag).shape),
        pair_re_shape=list(np.asarray(pair_re).shape),
        pair_im_shape=list(np.asarray(pair_im).shape),
        pair_index_shape=list(np.asarray(pair_index).shape),
    )
    return _payload_dict(
        KernelPayload(
            metadata=metadata,
            full_kernel=np.asarray(full_kernel),
            diag=np.asarray(diag),
            pair_re=np.asarray(pair_re),
            pair_im=np.asarray(pair_im),
            pair_index=np.asarray(pair_index),
        )
    )


def save_kernel(path: str | Path, payload: KernelPayload) -> None:
    out = Path(path)
    np.savez_compressed(out, full_kernel=np.asarray(payload.full_kernel), diag=np.asarray(payload.diag), pair_re=np.asarray(payload.pair_re), pair_im=np.asarray(payload.pair_im), pair_index=np.asarray(payload.pair_index), pe_bins=np.asarray(payload.metadata['pe_bins'], dtype=float))
    with open(out.with_suffix('.json'), 'w', encoding='utf-8') as fh:
        json.dump(payload.metadata, fh, ensure_ascii=False, indent=2)


__all__ = [name for name in globals() if not name.startswith('__')]
