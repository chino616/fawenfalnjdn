from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Mapping, Optional, Tuple
import numpy as np

from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    as_flavor_matrix,
    dagger,
    zero_flavor_matrix,
)

Basis = Literal['iso', 'np']

NR_SECTOR = {
    1: 'LNC',
    2: 'LNC',
    3: 'LNV',
    4: 'LNV',
    5: 'LNC',
    6: 'LNC',
    7: 'LNC',
    8: 'LNV',
    9: 'LNV',
    10: 'LNV',
    11: 'LNC',
    12: 'LNV',
    13: 'LNC',
    14: 'LNC',
}

@dataclass(frozen=True)
class RKinematics:
    """Particle-response kinematics.

    Enu, qabs, m_A, and m_N are in GeV.  All returned response matrices
    from ``responses_R`` carry GeV^-2 when c1-c12 are GeV^-2 and
    c13-c14 are GeV^-3.
    """

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

def _ci_tau(
    ci_basis: Mapping[int, Tuple[FlavorMatrix, FlavorMatrix]],
    i: int,
    tau: int,
) -> FlavorMatrix:
    if tau not in (0, 1):
        raise ValueError(f'tau must be 0 or 1, got {tau}')
    if i not in ci_basis:
        return zero_flavor_matrix()
    a0, a1 = ci_basis[i]
    return a0 if tau == 0 else a1

def _ord(ct: FlavorMatrix, cp: FlavorMatrix) -> FlavorMatrix:
    return dagger(ct) @ as_flavor_matrix(cp)

def _sym(ct_i: FlavorMatrix, ct_j: FlavorMatrix, cp_i: FlavorMatrix, cp_j: FlavorMatrix) -> FlavorMatrix:
    return _ord(ct_i, cp_j) + _ord(ct_j, cp_i)

def _anti(ct_i: FlavorMatrix, ct_j: FlavorMatrix, cp_i: FlavorMatrix, cp_j: FlavorMatrix) -> FlavorMatrix:
    return _ord(ct_i, cp_j) - _ord(ct_j, cp_i)

def _assert_same_sector(i: int, j: int) -> None:
    if i not in NR_SECTOR or j not in NR_SECTOR:
        raise KeyError(f'Unknown NR coefficient index in bilinear: ({i}, {j})')
    if NR_SECTOR[i] != NR_SECTOR[j]:
        raise RuntimeError(
            f'LNC-LNV interference is forbidden: c{i} is {NR_SECTOR[i]}, '
            f'c{j} is {NR_SECTOR[j]}'
        )

def _checked_ord(i: int, j: int, ct: FlavorMatrix, cp: FlavorMatrix) -> FlavorMatrix:
    _assert_same_sector(i, j)
    return _ord(ct, cp)

def _checked_sym(i: int, j: int, ct_i: FlavorMatrix, ct_j: FlavorMatrix, cp_i: FlavorMatrix, cp_j: FlavorMatrix) -> FlavorMatrix:
    _assert_same_sector(i, j)
    return _sym(ct_i, ct_j, cp_i, cp_j)

def _checked_anti(i: int, j: int, ct_i: FlavorMatrix, ct_j: FlavorMatrix, cp_i: FlavorMatrix, cp_j: FlavorMatrix) -> FlavorMatrix:
    _assert_same_sector(i, j)
    return _anti(ct_i, ct_j, cp_i, cp_j)

def _response_polynomials(kin, ord_, sym_, anti_):
    """Single formula owner for flavor- and operator-space bilinears."""
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
    b11 = ord_(1, 1)
    b1313 = ord_(13, 13)
    b33 = ord_(3, 3)
    b99 = ord_(9, 9)
    s1_13 = sym_(1, 13)
    a9_3 = anti_(9, 3)
    b1111 = ord_(11, 11)
    b1010 = ord_(10, 10)
    b44 = ord_(4, 4)
    a10_4 = anti_(10, 4)
    s11_14 = sym_(11, 14)
    s2_11 = sym_(2, 11)
    b1414 = ord_(14, 14)
    s2_14 = sym_(2, 14)
    a6_14 = anti_(6, 14)
    b22 = ord_(2, 2)
    a6_2 = anti_(6, 2)
    b66 = ord_(6, 6)
    b88 = ord_(8, 8)
    b55 = ord_(5, 5)
    b3_8 = ord_(3, 8)
    b9_8 = ord_(9, 8)
    R_M = (4.0 * E2 - qabs2 - 2.0 * E * qabs2 / mA) * b11 + (16.0 * E4 - 4.0 * E2 * qabs2 - 16.0 * E3 * qabs2 / mA + 2.0 * E * qabs4 / mA) * b1313 + qabs2 * b33 + (8.0 * E3 - 2.0 * E * qabs2 - 6.0 * E2 * qabs2 / mA + qabs4 / (2.0 * mA)) * s1_13 + (2j * E * qabs2 / mN - 1j * qabs4 / (2.0 * mA * mN)) * a9_3 + (4.0 * E2 * qabs2 / (mN * mN) - 2.0 * E * qabs4 / (mA * mN * mN)) * b99
    R_SigmaPP = (E2 * qabs2 / (mN * mN) - E * qabs4 / (2.0 * mA * mN * mN) - qabs4 / (4.0 * mN * mN)) * b1111 + qabs4 / (4.0 * mN * mN) * b1010 + (E2 - E * qabs2 / (2.0 * mA)) * b44 + (1j * E * qabs2 / (2.0 * mN) - 1j * qabs4 / (8.0 * mA * mN)) * a10_4 + (E3 * qabs2 / (mA * mN) - E * qabs4 / (4.0 * mA * mN)) * s11_14 + (E2 * qabs2 / (2.0 * mA * mN) - qabs4 / (8.0 * mA * mN)) * s2_11
    R_SigmaP = (2.0 * E4 + 0.5 * E2 * qabs2 - 2.0 * E3 * qabs2 / mA - E * qabs4 / (4.0 * mA)) * b1414 + (E3 + 0.25 * E * qabs2 - 3.0 * E2 * qabs2 / (4.0 * mA) - qabs4 / (16.0 * mA)) * s2_14 + (2j * E2 * qabs2 / mN - 1j * E * qabs4 / (mA * mN)) * a6_14 + (0.5 * E2 + 0.125 * qabs2 - E * qabs2 / (4.0 * mA)) * b22 + (1j * E * qabs2 / mN - 1j * qabs4 / (4.0 * mA * mN)) * a6_2 + (2.0 * E2 * qabs2 / (mN * mN) + qabs4 / (2.0 * mN * mN) - E * qabs4 / (mA * mN * mN)) * b66 + (0.5 * E2 - E * qabs2 / (4.0 * mA) - 0.125 * qabs2) * b44
    R_PhiPP = (4.0 * E2 - 2.0 * E * qabs2 / mA) * b88
    R_PhiPT = (2.0 * E2 - 0.5 * qabs2 - E * qabs2 / mA) * b88
    R_Delta = (2.0 * E2 + 0.5 * qabs2 - E * qabs2 / mA) * b55
    R_MPhiPP = (-2.0 * E * qabs + qabs3 / (2.0 * mA)) * b3_8 + (-4j * E2 * qabs / mN + 2j * E * qabs3 / (mA * mN)) * b9_8
    # This interference particle response is identically zero in the current
    # Li2026 amplitude convention; a tabulated nuclear SigmaPDelta response
    # therefore contributes zero until the particle-response formula changes.
    R_SigmaPDelta = np.zeros_like(R_M)
    return {'M': R_M, 'SigmaPP': R_SigmaPP, 'SigmaP': R_SigmaP, 'PhiPP': R_PhiPP, 'PhiPT': R_PhiPT, 'Delta': R_Delta, 'MPhiPP': R_MPhiPP, 'SigmaPDelta': R_SigmaPDelta}


def responses_R(
    ci_basis: Mapping[int, Tuple[FlavorMatrix, FlavorMatrix]],
    kin: RKinematics,
    *,
    tau: int,
    taup: int,
) -> Dict[str, FlavorMatrix]:
    coefficients = {i: (_ci_tau(ci_basis, i, tau), _ci_tau(ci_basis, i, taup)) for i in NR_SECTOR}
    def ord_(i, j):
        return _checked_ord(i, j, coefficients[i][0], coefficients[j][1])
    def sym_(i, j):
        return _checked_sym(i, j, coefficients[i][0], coefficients[j][0], coefficients[i][1], coefficients[j][1])
    def anti_(i, j):
        return _checked_anti(i, j, coefficients[i][0], coefficients[j][0], coefficients[i][1], coefficients[j][1])
    return _response_polynomials(kin, ord_, sym_, anti_)


def coefficient_responses_R(ci, kin, *, tau, taup):
    """Evaluate the same polynomials for an operator basis, not flavor matrices."""
    def ord_(i, j):
        _assert_same_sector(i, j)
        return np.outer(np.conjugate(ci[:, i, tau]), ci[:, j, taup])
    def sym_(i, j):
        return ord_(i, j) + ord_(j, i)
    def anti_(i, j):
        return ord_(i, j) - ord_(j, i)
    return _response_polynomials(kin, ord_, sym_, anti_)

def compute_R_matrices(ci_basis: Mapping[int, Tuple[FlavorMatrix, FlavorMatrix]], *, E_nu: float, qabs: Optional[float]=None, qabs2: Optional[float]=None, q: Optional[float]=None, mA: float, mN: float, basis: Basis='np') -> Dict[str, np.ndarray]:
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
    mats: Dict[str, np.ndarray] = {'MM': np.zeros((3, 3, 2, 2), dtype=complex), 'SSPP': np.zeros((3, 3, 2, 2), dtype=complex), 'SSP': np.zeros((3, 3, 2, 2), dtype=complex), 'PhiPP': np.zeros((3, 3, 2, 2), dtype=complex), 'PhiPT': np.zeros((3, 3, 2, 2), dtype=complex), 'DD': np.zeros((3, 3, 2, 2), dtype=complex), 'MPhiPP': np.zeros((3, 3, 2, 2), dtype=complex), 'SigmaPDelta': np.zeros((3, 3, 2, 2), dtype=complex)}
    scalar_to_matkey = {'M': 'MM', 'SigmaPP': 'SSPP', 'SigmaP': 'SSP', 'PhiPP': 'PhiPP', 'PhiPT': 'PhiPT', 'Delta': 'DD', 'MPhiPP': 'MPhiPP', 'SigmaPDelta': 'SigmaPDelta'}
    for tau in (0, 1):
        for taup in (0, 1):
            vals = responses_R(ci_basis, kin, tau=tau, taup=taup)
            for sk, mk in scalar_to_matkey.items():
                mats[mk][:, :, tau, taup] = vals[sk]
    return mats

__all__ = [
    "Basis",
    "NR_SECTOR",
    "RKinematics",
    "responses_R",
    "compute_R_matrices",
]
