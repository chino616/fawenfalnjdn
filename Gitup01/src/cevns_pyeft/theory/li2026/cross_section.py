from __future__ import annotations

import math
from typing import Mapping
import warnings

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    contract_density_kernel,
)
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey
from cevns_pyeft.theory.li2026.responses import Basis


INVGEV_TO_CM = 1.973269804e-14


def dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
    resp: ResponseW,
    *,
    E_nu_GeV: float,
    ER_keV: float,
    left_hat: Mapping[LeftKey, FlavorMatrix],
    lecs: Li2026LECs = DEFAULT_LECS,
    basis: Basis = "np",
    c10_mass_mode: C10MassMode = "quark_mass_resolved",
) -> FlavorMatrix:
    """Return the differential cross-section kernel in incoming-flavor space.

    The returned ``(3, 3)`` Hermitian matrix has units of ``cm^2 / GeV``.
    No incoming flavor state is selected or averaged in this core API.
    """

    E = float(E_nu_GeV)
    A = float(resp.get_basic('A'))
    mA = A * float(c.AMU_GEV)
    amplitude_kernel = flavor_kernel_onebody_li2026(
        resp,
        E_nu_GeV=E,
        ER_keV=float(ER_keV),
        left_hat=left_hat,
        lecs=lecs,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    ).kernel

    pref = mA / (8.0 * math.pi * E ** 2)
    conv = 1e-06 * INVGEV_TO_CM ** 2
    return amplitude_kernel * (pref * conv)


def dsigma_dER_for_density_li2026_cm2_per_GeV(
    resp: ResponseW,
    *,
    E_nu_GeV: float,
    ER_keV: float,
    left_hat: Mapping[LeftKey, FlavorMatrix],
    rho: FlavorMatrix,
    lecs: Li2026LECs = DEFAULT_LECS,
    basis: Basis = "np",
    c10_mass_mode: C10MassMode = "quark_mass_resolved",
) -> float:
    """Return ``Tr(rho d-zeta/dER)`` in ``cm^2 / GeV``."""

    kernel = dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
        resp,
        E_nu_GeV=E_nu_GeV,
        ER_keV=ER_keV,
        left_hat=left_hat,
        lecs=lecs,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    )
    return contract_density_kernel(rho, kernel)


def dsigma_dER_li2026_cm2_per_GeV(
    resp: ResponseW,
    *,
    E_nu_GeV: float,
    ER_keV: float,
    left_hat: Mapping[LeftKey, FlavorMatrix],
    rho: FlavorMatrix,
    lecs: Li2026LECs = DEFAULT_LECS,
    basis: Basis = "np",
    c10_mass_mode: C10MassMode = "quark_mass_resolved",
) -> float:
    """Deprecated scalar wrapper requiring an explicit incoming density matrix."""

    warnings.warn(
        "dsigma_dER_li2026_cm2_per_GeV is deprecated; use "
        "dsigma_dER_for_density_li2026_cm2_per_GeV or "
        "dsigma_dER_flavor_kernel_li2026_cm2_per_GeV",
        DeprecationWarning,
        stacklevel=2,
    )
    return dsigma_dER_for_density_li2026_cm2_per_GeV(
        resp,
        E_nu_GeV=E_nu_GeV,
        ER_keV=ER_keV,
        left_hat=left_hat,
        rho=rho,
        lecs=lecs,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    )

__all__ = [
    "INVGEV_TO_CM",
    "dsigma_dER_flavor_kernel_li2026_cm2_per_GeV",
    "dsigma_dER_for_density_li2026_cm2_per_GeV",
    "dsigma_dER_li2026_cm2_per_GeV",
]
