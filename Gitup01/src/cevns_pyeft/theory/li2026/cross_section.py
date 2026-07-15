from __future__ import annotations

from typing import Mapping
import math

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.theory.li2026.amplitude import amplitude_squared_onebody_li2026
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey
from cevns_pyeft.theory.li2026.responses import Basis

INVGEV_TO_CM = 1.973269804e-14

def dsigma_dER_li2026_cm2_per_GeV(resp: ResponseW, *, E_nu_GeV: float, ER_keV: float, left_hat: Mapping[LeftKey, complex], lecs: Li2026LECs=DEFAULT_LECS, basis: Basis='iso', c10_mass_mode: C10MassMode='flavor') -> float:
    E = float(E_nu_GeV)
    A = float(resp.get_basic('A'))
    mA = A * float(c.AMU_GEV)
    amp2 = amplitude_squared_onebody_li2026(resp, E_nu_GeV=E, ER_keV=float(ER_keV), left_hat=left_hat, lecs=lecs, basis=basis, c10_mass_mode=c10_mass_mode).amp2
    pref = mA / (8.0 * math.pi * E ** 2)
    conv = 1e-06 * INVGEV_TO_CM ** 2
    return float(pref * amp2 * conv)

__all__ = [
    "INVGEV_TO_CM",
    "dsigma_dER_li2026_cm2_per_GeV",
]
