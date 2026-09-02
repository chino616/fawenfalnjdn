"""Coherent CEvNS cross sections using the Helm nuclear form factor.

This module deliberately keeps the nuclear Helm form factor scalar in
neutrino-flavor space.  Flavor dependence is carried by a dimensionless
nuclear weak-charge matrix ``Q[alpha, beta]`` with the project convention

    row alpha    = final neutrino flavor,
    column beta  = initial neutrino flavor.

When the outgoing neutrino flavor is unobserved, the detection kernel is

    K = prefactor * F_H(q)^2 * Q^dagger Q,

and an incoming density matrix is contracted as ``Tr(rho K)`` using the
canonical helpers in :mod:`cevns_pyeft.theory.li2026.flavor`.

The default ``kinematics='mathematica'`` reproduces the coherent kinematic
factor used in the uploaded legacy Mathematica Helm block,
``1 - q^2/(4 E_nu^2) = 1 - m_A E_R/(2 E_nu^2)``.  The explicitly requested
``kinematics='exact_vector'`` option adds the recoil-order ``-E_R/E_nu`` term.
"""

from __future__ import annotations

import math
from typing import Literal

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.foundation.units import cm2_per_GeV_to_cm2_per_keV
from cevns_pyeft.theory.helm.form_factor import helm_form_factor_squared
from cevns_pyeft.theory.kinematics import (
    is_two_body_recoil_allowed,
    minimum_neutrino_energy_GeV,
    two_body_recoil_max_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    NeutrinoFlavor,
    as_flavor_matrix,
    contract_density_kernel,
    dagger,
    flavor_projector,
    identity_flavor_matrix,
    zero_flavor_matrix,
)

HelmKinematics = Literal["mathematica", "exact_vector"]
DEFAULT_SIN2_THETA_W = 0.2387


def _validate_target(A: int | float, Z: int | float) -> tuple[float, float, float]:
    a = float(A)
    z = float(Z)
    if not math.isfinite(a) or a <= 0.0:
        raise ValueError(f"A must be positive and finite, got {A!r}")
    if not math.isfinite(z) or z < 0.0 or z > a:
        raise ValueError(f"Z must satisfy 0 <= Z <= A, got Z={Z!r}, A={A!r}")
    return a, z, a - z


def nuclear_mass_GeV(A: int | float, *, amu_GeV: float = c.AMU_GEV) -> float:
    """Return the target-nucleus mass approximation ``m_A = A * u`` in GeV."""

    a = float(A)
    amu = float(amu_GeV)
    if not math.isfinite(a) or a <= 0.0:
        raise ValueError("A must be positive and finite")
    if not math.isfinite(amu) or amu <= 0.0:
        raise ValueError("amu_GeV must be positive and finite")
    return a * amu


def recoil_max_keV(
    E_nu_MeV: float,
    A: int | float,
    *,
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Return the exact elastic maximum nuclear recoil in keV."""

    e = float(E_nu_MeV) * c.MeV
    if not math.isfinite(e) or e <= 0.0:
        raise ValueError("E_nu_MeV must be positive and finite")
    m_a = nuclear_mass_GeV(A, amu_GeV=amu_GeV)
    t_max = two_body_recoil_max_GeV(e, m_a)
    return float(t_max / c.keV)


def minimum_neutrino_energy_MeV(
    ER_keV: float,
    A: int | float,
    *,
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Return the exact minimum neutrino energy for recoil ``E_R`` in MeV."""

    t = float(ER_keV) * c.keV
    if not math.isfinite(t) or t < 0.0:
        raise ValueError("ER_keV must be non-negative and finite")
    m_a = nuclear_mass_GeV(A, amu_GeV=amu_GeV)
    e_min = minimum_neutrino_energy_GeV(t, m_a)
    return float(e_min / c.MeV)


def cevns_kinematic_factor(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    *,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Return the dimensionless coherent recoil kinematic factor.

    ``mathematica``
        ``1 - m_A E_R/(2 E_nu^2)``.  This matches the uploaded legacy
        Mathematica Helm block.

    ``exact_vector``
        ``1 - E_R/E_nu - m_A E_R/(2 E_nu^2)``.

    Kinematically forbidden points are returned as zero for both choices.
    """

    e = float(E_nu_MeV) * c.MeV
    t = float(ER_keV) * c.keV
    if not math.isfinite(e) or e <= 0.0:
        raise ValueError("E_nu_MeV must be positive and finite")
    if not math.isfinite(t) or t < 0.0:
        raise ValueError("ER_keV must be non-negative and finite")
    if kinematics not in ("mathematica", "exact_vector"):
        raise ValueError(
            "kinematics must be 'mathematica' or 'exact_vector', "
            f"got {kinematics!r}"
        )
    m_a = nuclear_mass_GeV(A, amu_GeV=amu_GeV)
    if not is_two_body_recoil_allowed(e, t, m_a):
        return 0.0

    base = 1.0 - m_a * t / (2.0 * e * e)
    if kinematics == "mathematica":
        value = base
    elif kinematics == "exact_vector":
        value = 1.0 - t / two_body_recoil_max_GeV(e, m_a)
    else:
        raise ValueError(
            "kinematics must be 'mathematica' or 'exact_vector', "
            f"got {kinematics!r}"
        )
    return float(value)


def sm_weak_charge(
    A: int | float,
    Z: int | float,
    *,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
) -> float:
    """Return ``Q_W = N - (1 - 4 sin^2 theta_W) Z``.

    This is the weak-charge normalization used by the legacy Mathematica Helm
    cross section.  With this convention the scalar cross-section prefactor is
    ``G_F^2 m_A / (4 pi)``.
    """

    _a, z, n = _validate_target(A, Z)
    s2w = float(sin2_theta_w)
    if not math.isfinite(s2w):
        raise ValueError("sin2_theta_w must be finite")
    return float(n - (1.0 - 4.0 * s2w) * z)


def sm_weak_charge_matrix(
    A: int | float,
    Z: int | float,
    *,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
) -> FlavorMatrix:
    """Return the SM nuclear weak charge as ``Q_W * I_3``."""

    return sm_weak_charge(A, Z, sin2_theta_w=sin2_theta_w) * identity_flavor_matrix()


def nuclear_weak_charge_matrix(
    A: int | float,
    Z: int | float,
    *,
    proton_coupling: object,
    neutron_coupling: object,
) -> FlavorMatrix:
    """Combine proton/neutron flavor couplings into a nuclear charge matrix.

    Parameters are dimensionless ``(3,3)`` flavor matrices in the same
    ``Q_W`` normalization used by :func:`sm_weak_charge`.  Thus the SM inputs
    would be

    ``proton_coupling = -(1 - 4 sin^2 theta_W) * I`` and
    ``neutron_coupling = +I``.

    Under the single-Helm approximation the nuclear amplitude is proportional
    to ``F_H(q) * [Z C_p + N C_n]``.
    """

    _a, z, n = _validate_target(A, Z)
    cp = as_flavor_matrix(proton_coupling, name="proton_coupling")
    cn = as_flavor_matrix(neutron_coupling, name="neutron_coupling")
    return np.asarray(z * cp + n * cn, dtype=np.complex128)


def _helm_prefactor_cm2_per_GeV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    *,
    kinematics: HelmKinematics,
    amu_GeV: float,
) -> float:
    """Return the Helm cross-section prefactor excluding ``Q^dagger Q``."""

    kine = cevns_kinematic_factor(
        E_nu_MeV,
        ER_keV,
        A,
        kinematics=kinematics,
        amu_GeV=amu_GeV,
    )
    if kine == 0.0:
        return 0.0

    m_a = nuclear_mass_GeV(A, amu_GeV=amu_GeV)
    ff2 = float(helm_form_factor_squared(ER_keV, A, amu_GeV=amu_GeV))

    # In natural units dσ/dT is GeV^-3.  GEV_INV2_TO_CM2 converts only the
    # area factor; the canonical theory derivative remains per GeV.
    return float(
        (c.G_F**2 * m_a / (4.0 * math.pi))
        * kine
        * ff2
        * c.GEV_INV2_TO_CM2
    )


def dsigma_dER_helm_cm2_per_GeV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    *,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Return the SM Helm CEvNS differential cross section in cm^2/GeV."""

    _validate_target(A, Z)
    q_w = sm_weak_charge(A, Z, sin2_theta_w=sin2_theta_w)
    pref = _helm_prefactor_cm2_per_GeV(
        E_nu_MeV,
        ER_keV,
        A,
        kinematics=kinematics,
        amu_GeV=amu_GeV,
    )
    if pref == 0.0:
        return 0.0
    return float(pref * q_w * q_w)


def dsigma_dER_helm_kernel_cm2_per_GeV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> FlavorMatrix:
    """Return the flavor detection kernel ``dK/dE_R`` in cm^2/GeV.

    ``weak_charge_matrix`` is dimensionless and follows ``Q[final, initial]``.
    If omitted, the SM value ``Q_W I_3`` is used.  The outgoing flavor is not
    observed, so the matrix entering the initial-flavor space is ``Q^dagger Q``.
    """

    _validate_target(A, Z)
    if weak_charge_matrix is None:
        qmat = sm_weak_charge_matrix(A, Z, sin2_theta_w=sin2_theta_w)
    else:
        qmat = as_flavor_matrix(weak_charge_matrix, name="weak_charge_matrix")

    pref = _helm_prefactor_cm2_per_GeV(
        E_nu_MeV,
        ER_keV,
        A,
        kinematics=kinematics,
        amu_GeV=amu_GeV,
    )
    if pref == 0.0:
        return zero_flavor_matrix()

    kernel = pref * (dagger(qmat) @ qmat)
    return np.asarray(kernel, dtype=np.complex128)


def dsigma_dER_helm_density_cm2_per_GeV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    rho: object,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
    atol: float = 1.0e-10,
) -> float:
    """Return ``Tr[rho dK/dE_R]`` in cm^2/GeV."""

    kernel = dsigma_dER_helm_kernel_cm2_per_GeV(
        E_nu_MeV,
        ER_keV,
        A,
        Z,
        weak_charge_matrix=weak_charge_matrix,
        sin2_theta_w=sin2_theta_w,
        kinematics=kinematics,
        amu_GeV=amu_GeV,
    )
    return contract_density_kernel(rho, kernel, atol=atol)


def dsigma_dER_helm_flavor_cm2_per_GeV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    flavor: NeutrinoFlavor,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Return the Helm cross section for one pure incoming flavor state."""

    return dsigma_dER_helm_density_cm2_per_GeV(
        E_nu_MeV,
        ER_keV,
        A,
        Z,
        flavor_projector(flavor),
        weak_charge_matrix=weak_charge_matrix,
        sin2_theta_w=sin2_theta_w,
        kinematics=kinematics,
        amu_GeV=amu_GeV,
    )


def dsigma_dER_helm_cm2_per_keV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    *,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Explicitly convert the canonical SM Helm result to cm^2/keV."""

    return cm2_per_GeV_to_cm2_per_keV(
        dsigma_dER_helm_cm2_per_GeV(
            E_nu_MeV,
            ER_keV,
            A,
            Z,
            sin2_theta_w=sin2_theta_w,
            kinematics=kinematics,
            amu_GeV=amu_GeV,
        )
    )


def dsigma_dER_helm_kernel_cm2_per_keV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> FlavorMatrix:
    """Explicitly convert the canonical Helm Flavor kernel to cm^2/keV."""

    return cm2_per_GeV_to_cm2_per_keV(
        dsigma_dER_helm_kernel_cm2_per_GeV(
            E_nu_MeV,
            ER_keV,
            A,
            Z,
            weak_charge_matrix=weak_charge_matrix,
            sin2_theta_w=sin2_theta_w,
            kinematics=kinematics,
            amu_GeV=amu_GeV,
        )
    )


def dsigma_dER_helm_density_cm2_per_keV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    rho: object,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
    atol: float = 1.0e-10,
) -> float:
    """Explicitly convert the canonical density contraction to cm^2/keV."""

    return cm2_per_GeV_to_cm2_per_keV(
        dsigma_dER_helm_density_cm2_per_GeV(
            E_nu_MeV,
            ER_keV,
            A,
            Z,
            rho,
            weak_charge_matrix=weak_charge_matrix,
            sin2_theta_w=sin2_theta_w,
            kinematics=kinematics,
            amu_GeV=amu_GeV,
            atol=atol,
        )
    )


def dsigma_dER_helm_flavor_cm2_per_keV(
    E_nu_MeV: float,
    ER_keV: float,
    A: int | float,
    Z: int | float,
    flavor: NeutrinoFlavor,
    *,
    weak_charge_matrix: object | None = None,
    sin2_theta_w: float = DEFAULT_SIN2_THETA_W,
    kinematics: HelmKinematics = "mathematica",
    amu_GeV: float = c.AMU_GEV,
) -> float:
    """Explicitly convert one incoming-Flavor Helm result to cm^2/keV."""

    return cm2_per_GeV_to_cm2_per_keV(
        dsigma_dER_helm_flavor_cm2_per_GeV(
            E_nu_MeV,
            ER_keV,
            A,
            Z,
            flavor,
            weak_charge_matrix=weak_charge_matrix,
            sin2_theta_w=sin2_theta_w,
            kinematics=kinematics,
            amu_GeV=amu_GeV,
        )
    )


__all__ = [
    "HelmKinematics",
    "dsigma_dER_helm_cm2_per_GeV",
    "dsigma_dER_helm_kernel_cm2_per_GeV",
    "dsigma_dER_helm_density_cm2_per_GeV",
    "dsigma_dER_helm_flavor_cm2_per_GeV",
    "DEFAULT_SIN2_THETA_W",
    "nuclear_mass_GeV",
    "recoil_max_keV",
    "minimum_neutrino_energy_MeV",
    "cevns_kinematic_factor",
    "sm_weak_charge",
    "sm_weak_charge_matrix",
    "nuclear_weak_charge_matrix",
    "dsigma_dER_helm_cm2_per_keV",
    "dsigma_dER_helm_kernel_cm2_per_keV",
    "dsigma_dER_helm_density_cm2_per_keV",
    "dsigma_dER_helm_flavor_cm2_per_keV",
]
