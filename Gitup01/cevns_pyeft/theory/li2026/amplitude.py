from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple
import math
import numpy as np
import warnings

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    as_flavor_matrix,
    validate_flavor_kernel,
    zero_flavor_matrix,
)
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey, left_to_ci
from cevns_pyeft.theory.li2026.responses import Basis, compute_R_matrices

@dataclass(frozen=True)
class FlavorKernelResult:
    """Flavor-space amplitude kernel and per-channel pieces.

    ``kernel`` and ``pieces`` carry GeV^-2.  ``ER_keV`` is converted to
    GeV immediately; q0/qabs are GeV, q2/qabs2 are GeV^2, and y is
    dimensionless because the oscillator length b is GeV^-1.
    """

    kernel: FlavorMatrix
    pieces: Dict[str, FlavorMatrix]
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

def _contract_R_W(R: np.ndarray, W: np.ndarray) -> FlavorMatrix:
    R = np.asarray(R, dtype=np.complex128)
    W = np.asarray(W, dtype=float)
    if R.shape != (3, 3, 2, 2):
        raise ValueError(f'R must have shape (3,3,2,2), got {R.shape}')
    if W.shape != (2, 2):
        raise ValueError(f'W must have shape (2,2), got {W.shape}')
    return np.einsum('abij,ij->ab', R, W, optimize=True)

def _build_ci_basis(*, basis: Basis, ci_obj) -> Dict[int, Tuple[FlavorMatrix, FlavorMatrix]]:
    if basis == 'iso':
        return {
            int(i): (
                as_flavor_matrix(v[0], name=f'c{i}^0'),
                as_flavor_matrix(v[1], name=f'c{i}^1'),
            )
            for i, v in ci_obj.iso.items()
        }
    if basis == 'np':
        all_keys = sorted(set(ci_obj.p.keys()) | set(ci_obj.n.keys()))
        return {
            int(i): (
                as_flavor_matrix(ci_obj.p.get(i, zero_flavor_matrix()), name=f'c{i}^p'),
                as_flavor_matrix(ci_obj.n.get(i, zero_flavor_matrix()), name=f'c{i}^n'),
            )
            for i in all_keys
        }
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

def flavor_kernel_onebody_li2026(resp: ResponseW, *, E_nu_GeV: float, ER_keV: float, left_hat: Mapping[LeftKey, FlavorMatrix], lecs: Li2026LECs=DEFAULT_LECS, basis: Basis='np', c10_mass_mode: C10MassMode='quark_mass_resolved') -> FlavorKernelResult:
    E = float(E_nu_GeV)
    T = float(ER_keV) * c.keV
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
    y = c.y_from_qb(qabs, b)
    key_map = {'MM': 'M', 'SSPP': 'SigmaPP', 'SSP': 'SigmaP', 'PhiPP': 'PhiPP', 'PhiPT': 'PhiPT', 'DD': 'Delta', 'MPhiPP': 'MPhiPP'}
    pieces: Dict[str, FlavorMatrix] = {}
    total = zero_flavor_matrix()
    for rkey, wkey in key_map.items():
        Wm = _get_W_matrix(resp, wkey=wkey, y=y, basis=basis)
        val = _contract_R_W(Rm[rkey], Wm)
        if wkey == 'MPhiPP':
            # A physical interference contribution is the matrix analogue of
            # a scalar real part and must therefore enter Hermitianized.
            val = 0.5 * (val + val.conj().T)
        pieces[wkey] = val
        total += val
    if 'SigmaPDelta' in resp.responses:
        # The current Li2026 particle-response implementation defines
        # R_SigmaPDelta = 0 exactly.  Keep the channel visible in diagnostics,
        # but do not turn the presence of a nuclear response table into a
        # non-zero amplitude contribution.
        pieces['SigmaPDelta'] = zero_flavor_matrix()
    try:
        total = validate_flavor_kernel(
            total,
            name="final Flavor amplitude kernel",
        )
    except ValueError as exc:
        raise RuntimeError(f"Invalid final Flavor amplitude kernel: {exc}") from exc
    return FlavorKernelResult(kernel=total, pieces=pieces, basis=basis, y=float(y), q0=float(q0), q2=float(q2), qabs=float(qabs), qabs2=float(qabs2), ER_keV=float(ER_keV), E_nu_GeV=float(E))

def amplitude_squared_onebody_li2026(resp: ResponseW, *, E_nu_GeV: float, ER_keV: float, left_hat: Mapping[LeftKey, FlavorMatrix], lecs: Li2026LECs=DEFAULT_LECS, basis: Basis='np', c10_mass_mode: C10MassMode='quark_mass_resolved') -> FlavorKernelResult:
    warnings.warn(
        'amplitude_squared_onebody_li2026 now returns a FlavorKernelResult; '
        'use flavor_kernel_onebody_li2026 instead',
        DeprecationWarning,
        stacklevel=2,
    )
    return flavor_kernel_onebody_li2026(
        resp,
        E_nu_GeV=E_nu_GeV,
        ER_keV=ER_keV,
        left_hat=left_hat,
        lecs=lecs,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    )

__all__ = [
    "FlavorKernelResult",
    "flavor_kernel_onebody_li2026",
    "amplitude_squared_onebody_li2026",
]
