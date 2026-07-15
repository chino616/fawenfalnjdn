from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple
import math
import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey, left_to_ci
from cevns_pyeft.theory.li2026.responses import Basis, compute_R_matrices

@dataclass(frozen=True)
class Amp2Result:
    amp2: float
    pieces: Dict[str, float]
    basis: Basis
    y: float
    q0: float
    q2: float
    qabs: float
    qabs2: float
    ER_keV: float
    E_nu_GeV: float

    @property
    def q(self) -> float:
        return self.qabs

def _contract_R_W(R: np.ndarray, W: np.ndarray) -> float:
    return float(np.real(np.sum(R * W)))

def _build_ci_basis(*, basis: Basis, ci_obj) -> Dict[int, Tuple[complex, complex]]:
    if basis == 'iso':
        return {int(i): (complex(v[0]), complex(v[1])) for i, v in ci_obj.iso.items()}
    if basis == 'np':
        all_keys = sorted(set(ci_obj.p.keys()) | set(ci_obj.n.keys()))
        return {int(i): (complex(ci_obj.p.get(i, 0.0)), complex(ci_obj.n.get(i, 0.0))) for i in all_keys}
    raise ValueError("basis must be 'iso' or 'np'")

def _get_W_matrix(resp: ResponseW, *, wkey: str, y: float, basis: Basis) -> np.ndarray:
    if basis == 'iso':
        W = resp.W_iso(wkey, y)
    elif basis == 'np':
        W = resp.W_np(wkey, y)
    else:
        raise ValueError("basis must be 'iso' or 'np'")
    if not isinstance(W, list):
        raise TypeError(f"Response '{wkey}' is scalar; expected 2x2 matrix")
    return np.asarray(W, dtype=float)

def amplitude_squared_onebody_li2026(resp: ResponseW, *, E_nu_GeV: float, ER_keV: float, left_hat: Mapping[LeftKey, complex], lecs: Li2026LECs=DEFAULT_LECS, basis: Basis='np', c10_mass_mode: C10MassMode='flavor') -> Amp2Result:
    E = float(E_nu_GeV)
    T = float(ER_keV) * 1e-06
    A = float(resp.get_basic('A'))
    mA = A * float(c.AMU_GEV)
    q0 = T
    qabs2 = 2.0 * mA * T
    qabs = math.sqrt(max(qabs2, 0.0))
    q2 = q0 * q0 - qabs2
    ci = left_to_ci(left_hat, E_nu=E, q0=q0, q2=q2, qabs=qabs, qabs2=qabs2, mA=mA, c10_mass_mode=c10_mass_mode, lecs=lecs)
    ci_basis = _build_ci_basis(basis=basis, ci_obj=ci)
    Rm = compute_R_matrices(ci_basis, E_nu=E, qabs=qabs, qabs2=qabs2, mA=mA, mN=float(lecs.m_N), basis=basis)
    b = float(resp.get_basic('b'))
    y = (0.5 * qabs * b) ** 2
    key_map = {'MM': 'M', 'SSPP': 'SigmaPP', 'SSP': 'SigmaP', 'PhiPP': 'PhiPP', 'PhiPT': 'PhiPT', 'DD': 'Delta', 'MPhiPP': 'MPhiPP'}
    pieces: Dict[str, float] = {}
    total = 0.0
    for rkey, wkey in key_map.items():
        Wm = _get_W_matrix(resp, wkey=wkey, y=y, basis=basis)
        val = _contract_R_W(Rm[rkey], Wm)
        pieces[wkey] = val
        total += val
    if 'SigmaPDelta' in resp.responses:
        pieces['SigmaPDelta'] = 0.0
    return Amp2Result(amp2=float(total), pieces=pieces, basis=basis, y=float(y), q0=float(q0), q2=float(q2), qabs=float(qabs), qabs2=float(qabs2), ER_keV=float(ER_keV), E_nu_GeV=float(E))

__all__ = [
    "Amp2Result",
    "amplitude_squared_onebody_li2026",
]
