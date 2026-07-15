from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Mapping, Optional, Tuple, Union
import math
import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.theory.li2026.amplitude import amplitude_squared_onebody_li2026

ArrayLike = Union[float, int, np.ndarray]
Basis = Literal['np', 'iso']
Flavor = Literal['all', 'e', 'mub', 'mu', 'mmb']

def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)

def _scalar_or_array(arr: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(arr).reshape(-1)[0])
    return arr

def if_positive(x: ArrayLike) -> ArrayLike:
    xx = _asarray(x)
    yy = np.where(xx > 0.0, xx, 0.0)
    return _scalar_or_array(yy, x)

def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    if y.size == 0:
        return 0.0
    trapezoid = getattr(np, 'trapezoid', None)
    if trapezoid is not None:
        return float(trapezoid(y, x))
    return float(np.trapz(y, x))

def _parse_left_wc_key(name: str) -> Optional[Tuple[int, int, str]]:
    import re
    m = re.fullmatch('C(\\d+)([uds])?\\((\\d+)\\)', name)
    if not m:
        return None
    i = int(m.group(1))
    q = m.group(2) or ''
    d = int(m.group(3))
    if q not in {'u', 'd', 's', ''}:
        return None
    return (d, i, q)

def _build_wc_triplets(left_wcs: Optional[Mapping[str, complex]]=None, wc_triplets: Optional[Mapping[Tuple[int, int, str], complex]]=None) -> Dict[Tuple[int, int, str], complex]:
    out: Dict[Tuple[int, int, str], complex] = {}
    if wc_triplets:
        out.update({k: complex(v) for k, v in wc_triplets.items()})
    if left_wcs:
        for k, v in left_wcs.items():
            parsed = _parse_left_wc_key(k)
            if parsed is None:
                continue
            d, i, q = parsed
            out[d, i, q] = complex(v)
    return out

def _sm_left_dim6(include_sm: bool, sin2thetaW: float) -> Dict[Tuple[int, int, str], float]:
    if not include_sm:
        return {}
    s2 = float(sin2thetaW)
    pref = -(1.0 / math.sqrt(2.0)) * float(c.G_F)
    return {(6, 1, 'u'): pref * (1.0 - 8.0 / 3.0 * s2), (6, 1, 'd'): -pref * (1.0 - 4.0 / 3.0 * s2), (6, 2, 'u'): -pref, (6, 2, 'd'): pref}

@dataclass(frozen=True)
class AASResult:
    pieces: np.ndarray
    total: complex
    y: float
    q2: float
    q: float
    ER: float
    Enu: float
    basis: Basis

    def as_dict(self) -> Dict[str, Any]:
        labels = ['M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta']
        return {'pieces': {k: complex(v) for k, v in zip(labels, self.pieces)}, 'pieces_list': [complex(v) for v in self.pieces], 'total': complex(self.total), 'kinematics': {'ER_GeV': float(self.ER), 'Enu_GeV': float(self.Enu), 'q_GeV': float(self.q), 'q2_GeV2': float(self.q2), 'y': float(self.y)}, 'basis': self.basis}

def emax_muon_dar_mev() -> float:
    mmu = float(getattr(c, 'm_mu', 0.1056583745))
    me = float(getattr(c, 'm_e', 0.00051099895))
    mmu_mev = float(c.from_energy_gev(mmu, 'MeV'))
    me_mev = float(c.from_energy_gev(me, 'MeV'))
    return (mmu_mev * mmu_mev - me_mev * me_mev) / (2.0 * mmu_mev)

def enr_max_keV(A: int, *, Emax_MeV: Optional[float]=None) -> float:
    if Emax_MeV is None:
        Emax_MeV = emax_muon_dar_mev()
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    mA_MeV = mA_GeV * 1000.0
    ERmax_MeV = 2.0 * Emax_MeV ** 2 / mA_MeV
    return ERmax_MeV * 1000.0

def eee_quenching_csi(enr_keV: ArrayLike) -> ArrayLike:
    a = 0.0554628
    b = 4.30681
    c3 = -111.707
    d4 = 840.384
    x = _asarray(enr_keV)
    y = x * 0.001
    out = 1000.0 * (a * y + b * y ** 2 + c3 * y ** 3 + d4 * y ** 4)
    return _scalar_or_array(out, enr_keV)

def p_smearing_csi(pe: ArrayLike, enr_keV: float) -> ArrayLike:
    Eee = float(eee_quenching_csi(enr_keV))
    if not Eee > 0.0:
        xx = _asarray(pe)
        out = np.zeros_like(xx)
        return _scalar_or_array(out, pe)
    a = 0.0749 / Eee
    b = 9.56 * Eee
    k = 1.0 + b
    lam = a * (1.0 + b)
    xx = _asarray(pe)
    xx_pos = np.where(xx > 0.0, xx, 0.0)
    log_pdf = k * math.log(lam) - math.lgamma(k) + b * np.log(np.maximum(xx_pos, 1e-300)) - lam * xx_pos
    pdf = np.exp(log_pdf)
    pdf = np.where(xx > 0.0, pdf, 0.0)
    return _scalar_or_array(pdf, pe)

@dataclass(frozen=True)
class DSigmaResult:
    dsigma_cm2_per_keV: ArrayLike
    aas: AASResult

def differential_cross_section_nn(resp: Any, ER_keV: float, Enu_MeV: ArrayLike, *, basis: Basis='np', left_wcs: Optional[Dict[str, complex]]=None, wc_triplets: Optional[Dict[Tuple[int, int, str], complex]]=None, include_sm: bool=False, debug_units: bool=False, sin2thetaW: Optional[float]=None, c10_mass_mode: str='flavor') -> DSigmaResult:
    A = int(resp.basic.get('A'))
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    invgev_to_cm = float(getattr(c, 'INV_GEV_TO_CM', 1.973269804e-14))
    conv = 1e-06 * invgev_to_cm ** 2
    Enu_arr = _asarray(Enu_MeV)
    out = np.zeros_like(Enu_arr)
    aas_last: Optional[AASResult] = None
    for idx, Enu1 in np.ndenumerate(Enu_arr):
        Enu_GeV = float(c.to_energy_gev(float(Enu1), 'MeV'))
        if Enu_GeV <= 0.0:
            out[idx] = 0.0
            continue
        ER_GeV = float(ER_keV) * 1e-06
        E_min_GeV = math.sqrt(max(mA_GeV * ER_GeV / 2.0, 0.0))
        if Enu_GeV < E_min_GeV:
            out[idx] = 0.0
            continue
        left_hat = _build_wc_triplets(left_wcs=left_wcs, wc_triplets=wc_triplets)
        if include_sm:
            s2 = float(sin2thetaW) if sin2thetaW is not None else 0.23873
            sm = _sm_left_dim6(True, s2)
            for k, v in sm.items():
                left_hat[k] = complex(left_hat.get(k, 0.0 + 0j)) + complex(v)
        amp = amplitude_squared_onebody_li2026(resp, E_nu_GeV=float(Enu_GeV), ER_keV=float(ER_keV), left_hat=left_hat, basis=basis, c10_mass_mode=c10_mass_mode)
        labels = ['M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta']
        pieces = np.array([complex(amp.pieces.get(k, 0.0)) for k in labels], dtype=complex)
        qabs2 = 2.0 * mA_GeV * ER_GeV
        qabs = math.sqrt(max(qabs2, 0.0))
        b_ho = float(resp.basic.get('b'))
        y = (0.5 * qabs * b_ho) ** 2
        aas = AASResult(pieces=pieces, total=complex(float(amp.amp2)), y=float(y), q2=float(amp.q2), q=float(amp.qabs), ER=float(ER_GeV), Enu=float(Enu_GeV), basis=basis)
        aas_last = aas
        if debug_units:
            print('[units-check]')
            print(f'ER = {ER_GeV:.6e} GeV, Enu = {Enu_GeV:.6e} GeV')
            print(f'mA = {mA_GeV:.6e} GeV')
            print(f'qabs = {qabs:.6e} GeV, q2 = {amp.q2:.6e} GeV^2, y = {y:.6e}')
            print(f'basis = {basis}')
        pref = mA_GeV / (8.0 * math.pi * Enu_GeV * Enu_GeV)
        out[idx] = pref * float(amp.amp2) * conv
    if aas_last is None:
        Enu0_MeV = float(np.ravel(Enu_arr)[0]) if np.size(Enu_arr) > 0 else 0.0
        Enu0_GeV = float(c.to_energy_gev(Enu0_MeV, 'MeV'))
        ER_GeV = float(ER_keV) * 1e-06
        qabs2 = 2.0 * mA_GeV * ER_GeV
        qabs = math.sqrt(max(qabs2, 0.0))
        b_ho = float(resp.basic.get('b'))
        y = (0.5 * qabs * b_ho) ** 2
        q0 = ER_GeV
        q2 = q0 * q0 - qabs2
        aas_last = AASResult(pieces=np.zeros(8, dtype=complex), total=0.0 + 0j, y=float(y), q2=float(q2), q=float(qabs), ER=float(ER_GeV), Enu=float(Enu0_GeV), basis=basis)
    out = if_positive(out)
    return DSigmaResult(_scalar_or_array(out, Enu_MeV), aas_last)

__all__ = [
    "ArrayLike",
    "Basis",
    "Flavor",
    "_asarray",
    "_scalar_or_array",
    "_trapz",
    "AASResult",
    "DSigmaResult",
    "_parse_left_wc_key",
    "_build_wc_triplets",
    "_sm_left_dim6",
    "emax_muon_dar_mev",
    "enr_max_keV",
    "eee_quenching_csi",
    "p_smearing_csi",
    "differential_cross_section_nn",
]
