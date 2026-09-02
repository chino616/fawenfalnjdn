from __future__ import annotations

import math
from typing import Mapping
import warnings

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.theory.kinematics import is_two_body_recoil_allowed
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    validate_flavor_kernel,
    contract_density_kernel,
    zero_flavor_matrix,
)
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey
from cevns_pyeft.theory.li2026.operators import canonicalize_wilson_coefficients
from cevns_pyeft.theory.li2026.responses import Basis


INVGEV_TO_CM = math.sqrt(c.GEV_INV2_TO_CM2)


def amplitude_kernel_to_dsigma_cm2_per_GeV(
    amplitude_kernel: FlavorMatrix,
    *,
    E_nu_GeV: float,
    m_A_GeV: float,
) -> FlavorMatrix:
    """Apply the Li2026 phase-space prefactor in canonical core units."""

    kernel = validate_flavor_kernel(
        amplitude_kernel,
        name="amplitude_kernel",
    )
    energy = float(E_nu_GeV)
    mass = float(m_A_GeV)
    if not math.isfinite(energy) or energy <= 0.0:
        raise ValueError("E_nu_GeV must be positive and finite")
    if not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("m_A_GeV must be positive and finite")
    prefactor = mass / (8.0 * math.pi * energy**2)
    return kernel * (prefactor * c.GEV_INV2_TO_CM2)


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

    canonical_left_hat = canonicalize_wilson_coefficients(
        wc_triplets=left_hat
    )
    E = float(E_nu_GeV)
    recoil_GeV = float(ER_keV) * c.keV
    A = float(resp.get_basic('A'))
    mA = A * float(c.AMU_GEV)
    if not is_two_body_recoil_allowed(E, recoil_GeV, mA):
        return zero_flavor_matrix()

    amplitude_kernel = flavor_kernel_onebody_li2026(
        resp,
        E_nu_GeV=E,
        ER_keV=float(ER_keV),
        left_hat=canonical_left_hat,
        lecs=lecs,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    ).kernel
    return amplitude_kernel_to_dsigma_cm2_per_GeV(
        amplitude_kernel,
        E_nu_GeV=E,
        m_A_GeV=mA,
    )


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
    "amplitude_kernel_to_dsigma_cm2_per_GeV",
    "dsigma_dER_flavor_kernel_li2026_cm2_per_GeV",
    "dsigma_dER_for_density_li2026_cm2_per_GeV",
    "dsigma_dER_li2026_cm2_per_GeV",
]
