from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Mapping, Optional, Tuple
import math
import warnings

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.theory.li2026.flavor import FlavorMatrix, zero_flavor_matrix
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.operators import LeftKey, validate_operator_coefficient

C10MassMode = Literal['paper', 'quark_mass_resolved', 'flavor']
_Q_TOL = 1e-12
_POLE_TOL = 1e-30

def _C(
    left_hat: Mapping[LeftKey, FlavorMatrix],
    dim: int,
    idx: int,
    quark_flavor: str='',
) -> FlavorMatrix:
    key = (dim, idx, quark_flavor)
    if key not in left_hat:
        return zero_flavor_matrix()
    return validate_operator_coefficient(key, left_hat[key])

@dataclass(frozen=True)
class CiPN:
    p: Dict[int, FlavorMatrix]
    n: Dict[int, FlavorMatrix]
    iso: Dict[int, Tuple[FlavorMatrix, FlavorMatrix]]

@dataclass(frozen=True)
class LeftKinematics:
    q0: float
    q2: float
    qabs: float
    qabs2: float

def _rel_diff(a: float, b: float) -> float:
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) / scale

def _check_close(name: str, a: float, b: float, tol: float=_Q_TOL) -> None:
    if _rel_diff(a, b) > tol:
        raise ValueError(f'Inconsistent {name}: {a} vs {b}')

def _resolve_kinematics(*, q0: Optional[float], q2: Optional[float], qabs: Optional[float], qabs2: Optional[float], q: Optional[float], mA: Optional[float]) -> LeftKinematics:
    if qabs is None:
        if q is None:
            raise ValueError('left_to_ci requires qabs (or backward-compatible q)')
        qabs = float(q)
    else:
        qabs = float(qabs)
        if q is not None:
            _check_close('q and qabs', qabs, float(q))
    if qabs < 0.0:
        raise ValueError('qabs must be non-negative')
    qabs2_from_qabs = qabs * qabs
    if qabs2 is None:
        qabs2 = qabs2_from_qabs
    else:
        qabs2 = float(qabs2)
        _check_close('qabs2 and qabs^2', qabs2, qabs2_from_qabs)
    q0_in = None if q0 is None else float(q0)
    q2_in = None if q2 is None else float(q2)
    if q0_in is not None and q2_in is not None:
        _check_close('q2 and q0^2-qabs2', q2_in, q0_in * q0_in - qabs2)
        return LeftKinematics(q0=q0_in, q2=q2_in, qabs=qabs, qabs2=qabs2)
    if q0_in is not None:
        return LeftKinematics(q0=q0_in, q2=q0_in * q0_in - qabs2, qabs=qabs, qabs2=qabs2)
    if q2_in is not None:
        q0sq = q2_in + qabs2
        if q0sq < -_Q_TOL * max(1.0, abs(q2_in), abs(qabs2)):
            raise ValueError(f'Cannot infer real q0 from q2 + qabs2 = {q0sq}; provide explicit q0 if intended.')
        q0_val = math.sqrt(max(q0sq, 0.0))
        return LeftKinematics(q0=q0_val, q2=q2_in, qabs=qabs, qabs2=qabs2)
    if mA is not None:
        mA = float(mA)
        if not mA > 0.0:
            raise ValueError('mA must be positive when used to infer q0/q2')
        q0_val = qabs2 / (2.0 * mA)
        return LeftKinematics(q0=q0_val, q2=q0_val * q0_val - qabs2, qabs=qabs, qabs2=qabs2)
    return LeftKinematics(q0=0.0, q2=-qabs2, qabs=qabs, qabs2=qabs2)

def _safe_div_by_q2(numerator: FlavorMatrix, q2: float) -> FlavorMatrix:
    if abs(q2) <= _POLE_TOL:
        return zero_flavor_matrix()
    return numerator / q2

def _safe_pion_pole(numerator: FlavorMatrix, m_pi: float, q2: float) -> FlavorMatrix:
    denom = m_pi * m_pi - q2
    if abs(denom) <= _POLE_TOL:
        return zero_flavor_matrix()
    return numerator / denom

def left_to_ci(left_hat: Mapping[LeftKey, FlavorMatrix], *, E_nu: float, q0: Optional[float]=None, q2: Optional[float]=None, qabs: Optional[float]=None, qabs2: Optional[float]=None, q: Optional[float]=None, mA: Optional[float]=None, c10_mass_mode: C10MassMode='quark_mass_resolved', lecs: Li2026LECs=DEFAULT_LECS) -> CiPN:
    E_nu = float(E_nu)
    if c10_mass_mode == 'flavor':
        warnings.warn(
            "c10_mass_mode='flavor' is deprecated; use 'quark_mass_resolved'",
            DeprecationWarning,
            stacklevel=2,
        )
        c10_mass_mode = 'quark_mass_resolved'
    kin = _resolve_kinematics(q0=q0, q2=q2, qabs=qabs, qabs2=qabs2, q=q, mA=mA)
    q0 = kin.q0
    q2 = kin.q2
    qabs = kin.qabs
    qabs2 = kin.qabs2
    _ = (qabs, qabs2)
    Ebar = E_nu - 0.5 * q0
    alpha = float(c.alpha_em)
    B0 = float(lecs.m_pi) ** 2 / (float(lecs.m_u) + float(lecs.m_d))
    L1, L2, L3, L4 = (lecs.L1, lecs.L2, lecs.L3, lecs.L4)
    L5, L6, L7, L8 = (lecs.L5, lecs.L6, lecs.L7, lecs.L8)
    L11, L12, L13, L14 = (lecs.L11, lecs.L12, lecs.L13, lecs.L14)
    g1, g2 = (lecs.g1, lecs.g2)
    g3, g4 = (lecs.g3, lecs.g4)
    g5, g6, g7, g8, g9 = (lecs.g5, lecs.g6, lecs.g7, lecs.g8, lecs.g9)
    su_p, sd_p = (lecs.sigma_u_p, lecs.sigma_d_p)
    su_n, sd_n = (lecs.sigma_u_n, lecs.sigma_d_n)
    m_u = float(lecs.m_u)
    m_d = float(lecs.m_d)
    m_pi = float(lecs.m_pi)
    m_N = float(lecs.m_N)
    g_A = float(lecs.g_A)
    C5_1 = _C(left_hat, 5, 1, '')
    C6u1 = _C(left_hat, 6, 1, 'u')
    C6d1 = _C(left_hat, 6, 1, 'd')
    C6u2 = _C(left_hat, 6, 2, 'u')
    C6d2 = _C(left_hat, 6, 2, 'd')
    C7u1 = _C(left_hat, 7, 1, 'u')
    C7d1 = _C(left_hat, 7, 1, 'd')
    C7u2 = _C(left_hat, 7, 2, 'u')
    C7d2 = _C(left_hat, 7, 2, 'd')
    C7u3 = _C(left_hat, 7, 3, 'u')
    C7d3 = _C(left_hat, 7, 3, 'd')
    C7u4 = _C(left_hat, 7, 4, 'u')
    C7d4 = _C(left_hat, 7, 4, 'd')
    C7u5 = _C(left_hat, 7, 5, 'u')
    C7d5 = _C(left_hat, 7, 5, 'd')
    C7_6 = _C(left_hat, 7, 6, '')
    C7_7 = _C(left_hat, 7, 7, '')
    C8u1 = _C(left_hat, 8, 1, 'u')
    C8d1 = _C(left_hat, 8, 1, 'd')
    C8u2 = _C(left_hat, 8, 2, 'u')
    C8d2 = _C(left_hat, 8, 2, 'd')
    C8_9 = _C(left_hat, 8, 9, '')
    if c10_mass_mode == 'paper':
        c10_ud_p = m_u * (C7u5 - C7d5)
        c10_ud_n = m_u * (C7d5 - C7u5)
    elif c10_mass_mode == 'quark_mass_resolved':
        c10_ud_p = m_u * C7u5 - m_d * C7d5
        c10_ud_n = m_d * C7d5 - m_u * C7u5
    else:
        raise ValueError(f'Unknown c10_mass_mode: {c10_mass_mode}')
    cp: Dict[int, FlavorMatrix] = {}
    cp[1] = 2.0 * C6u1 + C6d1 + (g1 + g2) * C7u1 + g2 * C7d1
    cp[2] = 2.0 * (L3 + L4) * C6u2 + 2.0 * L4 * C6d2
    cp[3] = su_p * C7u4 + sd_p * C7d4 + L13 * C7_6 - _safe_div_by_q2(2.0 * alpha * Ebar / math.pi * C5_1, q2)
    cp[4] = 2.0 * (L5 + L6) * C7u3 + 2.0 * L6 * C7d3
    cp[5] = 2.0 * C6u1 + C6d1
    cp[6] = (2.0 + 2.0 * L1 + 2.0 * L2) * C6u1 + (1.0 + 2.0 * L2) * C6d1
    cp[7] = 2.0 * (L3 + L4) * C6u2 + 2.0 * L4 * C6d2
    cp[8] = (L5 + L6) * C7u3 + L6 * C7d3
    cp[9] = (L5 + L6 + L7 + L8) * C7u3 + (L6 + L8) * C7d3
    cp[10] = _safe_pion_pole(B0 * g_A * c10_ud_p, m_pi, q2) + (L11 + L12) * C7u5 + L12 * C7d5 + L14 * C7_7
    cp[11] = 4.0 * (g3 + g4) * C7u2 + 4.0 * g4 * C7d2
    cp[12] = _safe_div_by_q2(alpha * m_N / (3.0 * math.pi) * (1.0 + 2.0 * L1) * C5_1, q2)
    cp[13] = (g5 + g6) * C8u1 + g6 * C8d1 + g9 * C8_9
    cp[14] = 2.0 * (g7 + g8) * C8u2 + 2.0 * g8 * C8d2
    cn: Dict[int, FlavorMatrix] = {}
    cn[1] = C6u1 + 2.0 * C6d1 + (g1 + g2) * C7d1 + g2 * C7u1
    cn[2] = 2.0 * (L3 + L4) * C6d2 + 2.0 * L4 * C6u2
    cn[3] = su_n * C7u4 + sd_n * C7d4 + L13 * C7_6
    cn[4] = 2.0 * (L5 + L6) * C7d3 + 2.0 * L6 * C7u3
    cn[5] = C6u1 + 2.0 * C6d1
    cn[6] = (2.0 + 2.0 * L1 + 2.0 * L2) * C6d1 + (1.0 + 2.0 * L2) * C6u1
    cn[7] = 2.0 * (L3 + L4) * C6d2 + 2.0 * L4 * C6u2
    cn[8] = (L5 + L6) * C7d3 + L6 * C7u3
    cn[9] = (L5 + L6 + L7 + L8) * C7d3 + (L6 + L8) * C7u3
    cn[10] = _safe_pion_pole(B0 * g_A * c10_ud_n, m_pi, q2) + (L11 + L12) * C7d5 + L12 * C7u5 + L14 * C7_7
    cn[11] = 4.0 * (g3 + g4) * C7d2 + 4.0 * g4 * C7u2
    cn[12] = cp[12]
    cn[13] = (g5 + g6) * C8d1 + g6 * C8u1 + g9 * C8_9
    cn[14] = 2.0 * (g7 + g8) * C8d2 + 2.0 * g8 * C8u2
    iso: Dict[int, Tuple[FlavorMatrix, FlavorMatrix]] = {}
    for i in range(1, 15):
        c0 = 0.5 * (cp[i] + cn[i])
        c1 = 0.5 * (cp[i] - cn[i])
        iso[i] = (c0, c1)
    return CiPN(p=cp, n=cn, iso=iso)

__all__ = [
    "LeftKey",
    "C10MassMode",
    "CiPN",
    "LeftKinematics",
    "left_to_ci",
]
