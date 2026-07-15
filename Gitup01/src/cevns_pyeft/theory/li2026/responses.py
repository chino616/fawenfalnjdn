from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Mapping, Optional, Tuple
import numpy as np

Basis = Literal['iso', 'np']

@dataclass(frozen=True)
class RKinematics:
    Enu: float
    qabs: float
    m_A: float
    m_N: float

    @property
    def qabs2(self) -> float:
        return self.qabs * self.qabs

    @property
    def qabs3(self) -> float:
        return self.qabs2 * self.qabs

    @property
    def qabs4(self) -> float:
        return self.qabs2 * self.qabs2

def _ci_tau(ci_basis: Mapping[int, Tuple[complex, complex]], i: int, tau: int) -> complex:
    a0, a1 = ci_basis.get(i, (0.0 + 0j, 0.0 + 0j))
    return a0 if tau == 0 else a1

def _ord(ct: complex, cp: complex) -> complex:
    return ct.conjugate() * cp

def _sym(ct_i: complex, ct_j: complex, cp_i: complex, cp_j: complex) -> complex:
    return _ord(ct_i, cp_j) + _ord(ct_j, cp_i)

def _anti(ct_i: complex, ct_j: complex, cp_i: complex, cp_j: complex) -> complex:
    return _ord(ct_i, cp_j) - _ord(ct_j, cp_i)

def responses_R(ci_basis: Mapping[int, Tuple[complex, complex]], kin: RKinematics, *, tau: int, taup: int) -> Dict[str, complex]:
    E = float(kin.Enu)
    qabs = float(kin.qabs)
    qabs2 = float(kin.qabs2)
    qabs3 = float(kin.qabs3)
    qabs4 = float(kin.qabs4)
    mA = float(kin.m_A)
    mN = float(kin.m_N)
    E2 = E * E
    E3 = E2 * E
    E4 = E2 * E2
    c1t, c1p = (_ci_tau(ci_basis, 1, tau), _ci_tau(ci_basis, 1, taup))
    c2t, c2p = (_ci_tau(ci_basis, 2, tau), _ci_tau(ci_basis, 2, taup))
    c3t, c3p = (_ci_tau(ci_basis, 3, tau), _ci_tau(ci_basis, 3, taup))
    c4t, c4p = (_ci_tau(ci_basis, 4, tau), _ci_tau(ci_basis, 4, taup))
    c5t, c5p = (_ci_tau(ci_basis, 5, tau), _ci_tau(ci_basis, 5, taup))
    c6t, c6p = (_ci_tau(ci_basis, 6, tau), _ci_tau(ci_basis, 6, taup))
    c8t, c8p = (_ci_tau(ci_basis, 8, tau), _ci_tau(ci_basis, 8, taup))
    c9t, c9p = (_ci_tau(ci_basis, 9, tau), _ci_tau(ci_basis, 9, taup))
    c10t, c10p = (_ci_tau(ci_basis, 10, tau), _ci_tau(ci_basis, 10, taup))
    c11t, c11p = (_ci_tau(ci_basis, 11, tau), _ci_tau(ci_basis, 11, taup))
    c13t, c13p = (_ci_tau(ci_basis, 13, tau), _ci_tau(ci_basis, 13, taup))
    c14t, c14p = (_ci_tau(ci_basis, 14, tau), _ci_tau(ci_basis, 14, taup))
    b11 = _ord(c1t, c1p)
    b1313 = _ord(c13t, c13p)
    b33 = _ord(c3t, c3p)
    b99 = _ord(c9t, c9p)
    s1_13 = _sym(c1t, c13t, c1p, c13p)
    a9_3 = _anti(c9t, c3t, c9p, c3p)
    b1111 = _ord(c11t, c11p)
    b1010 = _ord(c10t, c10p)
    b44 = _ord(c4t, c4p)
    a10_4 = _anti(c10t, c4t, c10p, c4p)
    s11_14 = _sym(c11t, c14t, c11p, c14p)
    s2_11 = _sym(c2t, c11t, c2p, c11p)
    b1414 = _ord(c14t, c14p)
    s2_14 = _sym(c2t, c14t, c2p, c14p)
    a6_14 = _anti(c6t, c14t, c6p, c14p)
    b22 = _ord(c2t, c2p)
    a6_2 = _anti(c6t, c2t, c6p, c2p)
    b66 = _ord(c6t, c6p)
    b88 = _ord(c8t, c8p)
    b55 = _ord(c5t, c5p)
    b3_8 = _ord(c3t, c8p)
    b9_8 = _ord(c9t, c8p)
    R_M = (4.0 * E2 - qabs2 - 2.0 * E * qabs2 / mA) * b11 + (16.0 * E4 - 4.0 * E2 * qabs2 - 16.0 * E3 * qabs2 / mA + 2.0 * E * qabs4 / mA) * b1313 + qabs2 * b33 + (8.0 * E3 - 2.0 * E * qabs2 - 6.0 * E2 * qabs2 / mA + qabs4 / (2.0 * mA)) * s1_13 + (2j * E * qabs2 / mN - 1j * qabs4 / (2.0 * mA * mN)) * a9_3 + (4.0 * E2 * qabs2 / (mN * mN) - 2.0 * E * qabs4 / (mA * mN * mN)) * b99
    R_SigmaPP = (E2 * qabs2 / (mN * mN) - E * qabs4 / (2.0 * mA * mN * mN) - qabs4 / (4.0 * mN * mN)) * b1111 + qabs4 / (4.0 * mN * mN) * b1010 + (E2 - E * qabs2 / (2.0 * mA)) * b44 + (1j * E * qabs2 / (2.0 * mN) - 1j * qabs4 / (8.0 * mA * mN)) * a10_4 + (E3 * qabs2 / (mA * mN) - E * qabs4 / (4.0 * mA * mN)) * s11_14 + (E2 * qabs2 / (2.0 * mA * mN) - qabs4 / (8.0 * mA * mN)) * s2_11
    R_SigmaP = (2.0 * E4 + 0.5 * E2 * qabs2 - 2.0 * E3 * qabs2 / mA - E * qabs4 / (4.0 * mA)) * b1414 + (E3 + 0.25 * E * qabs2 - 3.0 * E2 * qabs2 / (4.0 * mA) - qabs4 / (16.0 * mA)) * s2_14 + (2j * E2 * qabs2 / mN - 1j * E * qabs4 / (mA * mN)) * a6_14 + (0.5 * E2 + 0.125 * qabs2 - E * qabs2 / (4.0 * mA)) * b22 + (1j * E * qabs2 / mN - 1j * qabs4 / (4.0 * mA * mN)) * a6_2 + (2.0 * E2 * qabs2 / (mN * mN) + qabs4 / (2.0 * mN * mN) - E * qabs4 / (mA * mN * mN)) * b66 + (0.5 * E2 - E * qabs2 / (4.0 * mA) - 0.125 * qabs2) * b44
    R_PhiPP = (4.0 * E2 - 2.0 * E * qabs2 / mA) * b88
    R_PhiPT = (2.0 * E2 - 0.5 * qabs2 - E * qabs2 / mA) * b88
    R_Delta = (2.0 * E2 + 0.5 * qabs2 - E * qabs2 / mA) * b55
    R_MPhiPP = (-2.0 * E * qabs + qabs3 / (2.0 * mA)) * b3_8 + (-4j * E2 * qabs / mN + 2j * E * qabs3 / (mA * mN)) * b9_8
    R_SigmaPDelta = 0.0 + 0j
    return {'M': complex(R_M), 'SigmaPP': complex(R_SigmaPP), 'SigmaP': complex(R_SigmaP), 'PhiPP': complex(R_PhiPP), 'PhiPT': complex(R_PhiPT), 'Delta': complex(R_Delta), 'MPhiPP': complex(R_MPhiPP), 'SigmaPDelta': complex(R_SigmaPDelta)}

def compute_R_matrices(ci_basis: Mapping[int, Tuple[complex, complex]], *, E_nu: float, qabs: Optional[float]=None, qabs2: Optional[float]=None, q: Optional[float]=None, mA: float, mN: float, basis: Basis='np') -> Dict[str, np.ndarray]:
    if basis not in {'iso', 'np'}:
        raise ValueError("basis must be 'iso' or 'np'")
    if qabs is None:
        if q is None:
            raise ValueError('compute_R_matrices requires qabs (or backward-compatible q)')
        qabs = float(q)
    else:
        qabs = float(qabs)
    if qabs2 is not None:
        qabs2 = float(qabs2)
        if not np.isclose(qabs2, qabs * qabs, rtol=1e-12, atol=0.0):
            raise ValueError('Inconsistent qabs and qabs2: expected qabs2 == qabs**2')
    kin = RKinematics(Enu=float(E_nu), qabs=float(qabs), m_A=float(mA), m_N=float(mN))
    mats: Dict[str, np.ndarray] = {'MM': np.zeros((2, 2), dtype=complex), 'SSPP': np.zeros((2, 2), dtype=complex), 'SSP': np.zeros((2, 2), dtype=complex), 'PhiPP': np.zeros((2, 2), dtype=complex), 'PhiPT': np.zeros((2, 2), dtype=complex), 'DD': np.zeros((2, 2), dtype=complex), 'MPhiPP': np.zeros((2, 2), dtype=complex), 'SigmaPDelta': np.zeros((2, 2), dtype=complex)}
    scalar_to_matkey = {'M': 'MM', 'SigmaPP': 'SSPP', 'SigmaP': 'SSP', 'PhiPP': 'PhiPP', 'PhiPT': 'PhiPT', 'Delta': 'DD', 'MPhiPP': 'MPhiPP', 'SigmaPDelta': 'SigmaPDelta'}
    for tau in (0, 1):
        for taup in (0, 1):
            vals = responses_R(ci_basis, kin, tau=tau, taup=taup)
            for sk, mk in scalar_to_matkey.items():
                mats[mk][tau, taup] = vals[sk]
    return mats

__all__ = [
    "Basis",
    "RKinematics",
    "responses_R",
    "compute_R_matrices",
]
