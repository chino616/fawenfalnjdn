"""Helm nuclear form factor for coherent elastic neutrino--nucleus scattering.

The Helm form factor is a *nuclear* quantity and therefore carries no
neutrino-flavor indices.  Flavor dependence belongs to the interaction
couplings/weak-charge matrix handled by :mod:`.cross_section`.

This implementation follows the parameterization used by the project's
legacy Mathematica reference::

    c  = 1.23 A**(1/3) - 0.60 fm
    a  = 0.52 fm
    s  = 0.90 fm
    R1 = sqrt(c**2 + 7*pi**2*a**2/3 - 5*s**2)

and

    F_H(q) = 3 j1(q R1)/(q R1) * exp[-(q s)**2/2].

``helm_form_factor`` returns the amplitude-level form factor ``F_H``;
``helm_form_factor_squared`` returns ``F_H**2`` and corresponds to the older
Mathematica ``HelmFormFactor`` convention used directly in the cross section.
"""

from __future__ import annotations

import math
from typing import TypeAlias

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cevns_pyeft.foundation import constants as c

FloatArray: TypeAlias = NDArray[np.float64]
FloatOrArray: TypeAlias = float | FloatArray

DEFAULT_DIFFUSENESS_FM = 0.52
DEFAULT_SKIN_FM = 0.90
DEFAULT_C0_FM = 1.23
DEFAULT_C1_FM = -0.60


def _positive_mass_number(A: int | float) -> float:
    value = float(A)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"A must be a positive finite mass number, got {A!r}")
    return value


def _nonnegative_array(value: ArrayLike, *, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    if np.any(arr < 0.0):
        raise ValueError(f"{name} must be non-negative")
    return arr


def _scalar_or_array(value: np.ndarray) -> FloatOrArray:
    if value.ndim == 0:
        return float(value)
    return np.asarray(value, dtype=np.float64)


def helm_diffraction_radius_fm(
    A: int | float,
    *,
    diffuseness_fm: float = DEFAULT_DIFFUSENESS_FM,
    skin_fm: float = DEFAULT_SKIN_FM,
    c0_fm: float = DEFAULT_C0_FM,
    c1_fm: float = DEFAULT_C1_FM,
) -> float:
    """Return the Helm diffraction radius ``R1`` in fm.

    The parameter convention is the one used in the uploaded Mathematica
    reference: ``c = 1.23 A^(1/3) - 0.60 fm``, ``a = 0.52 fm`` and
    ``s = 0.90 fm``.
    """

    A_f = _positive_mass_number(A)
    a = float(diffuseness_fm)
    s = float(skin_fm)
    c0 = float(c0_fm)
    c1 = float(c1_fm)
    if not all(math.isfinite(x) for x in (a, s, c0, c1)):
        raise ValueError("Helm radius parameters must be finite")
    if a < 0.0 or s < 0.0:
        raise ValueError("diffuseness_fm and skin_fm must be non-negative")

    c_radius = c0 * A_f ** (1.0 / 3.0) + c1
    r1_sq = c_radius**2 + (7.0 / 3.0) * math.pi**2 * a**2 - 5.0 * s**2
    if r1_sq <= 0.0:
        raise ValueError(
            "Helm diffraction-radius squared is non-positive; check A and parameters"
        )
    return math.sqrt(r1_sq)


def momentum_transfer_GeV(
    ER_keV: ArrayLike,
    A: int | float,
    *,
    amu_GeV: float = c.AMU_GEV,
) -> FloatOrArray:
    """Return ``q = sqrt(2 m_A E_R)`` in GeV.

    Parameters
    ----------
    ER_keV:
        Nuclear recoil energy in keV.
    A:
        Nuclear mass number.
    amu_GeV:
        Atomic mass unit in GeV.  The project constant is used by default.
    """

    A_f = _positive_mass_number(A)
    er = _nonnegative_array(ER_keV, name="ER_keV")
    amu = float(amu_GeV)
    if not math.isfinite(amu) or amu <= 0.0:
        raise ValueError("amu_GeV must be positive and finite")
    m_a = A_f * amu
    q = np.sqrt(2.0 * m_a * er * c.keV)
    return _scalar_or_array(q)


def momentum_transfer_fm_inv(
    ER_keV: ArrayLike,
    A: int | float,
    *,
    amu_GeV: float = c.AMU_GEV,
) -> FloatOrArray:
    """Return the recoil momentum transfer in inverse femtometres (fm^-1)."""

    q_gev = np.asarray(momentum_transfer_GeV(ER_keV, A, amu_GeV=amu_GeV))
    q_fm_inv = q_gev / c.HBARC_GEV_FM
    return _scalar_or_array(np.asarray(q_fm_inv, dtype=float))


def helm_form_factor_q(
    q_GeV: ArrayLike,
    A: int | float,
    *,
    diffuseness_fm: float = DEFAULT_DIFFUSENESS_FM,
    skin_fm: float = DEFAULT_SKIN_FM,
    c0_fm: float = DEFAULT_C0_FM,
    c1_fm: float = DEFAULT_C1_FM,
) -> FloatOrArray:
    """Return the amplitude-level Helm form factor for momentum ``q`` in GeV.

    The normalization is ``F_H(0) = 1``.  A series expansion is used near
    ``q R1 = 0`` to avoid the removable ``0/0`` singularity.
    """

    q = _nonnegative_array(q_GeV, name="q_GeV")
    r1 = helm_diffraction_radius_fm(
        A,
        diffuseness_fm=diffuseness_fm,
        skin_fm=skin_fm,
        c0_fm=c0_fm,
        c1_fm=c1_fm,
    )
    s = float(skin_fm)
    if not math.isfinite(s) or s < 0.0:
        raise ValueError("skin_fm must be non-negative and finite")

    q_fm_inv = q / c.HBARC_GEV_FM
    x = q_fm_inv * r1

    # 3*j1(x)/x = 3*(sin(x)-x*cos(x))/x^3.
    # The explicit series removes the x=0 numerical singularity.
    x2 = x * x
    series = 1.0 - x2 / 10.0 + x2 * x2 / 280.0 - x2 * x2 * x2 / 15120.0
    with np.errstate(divide="ignore", invalid="ignore"):
        general = 3.0 * (np.sin(x) - x * np.cos(x)) / (x**3)
    sphere = np.where(np.abs(x) < 1.0e-4, series, general)
    surface = np.exp(-0.5 * (q_fm_inv * s) ** 2)
    ff = sphere * surface
    return _scalar_or_array(np.asarray(ff, dtype=float))


def helm_form_factor(
    ER_keV: ArrayLike,
    A: int | float,
    *,
    amu_GeV: float = c.AMU_GEV,
    diffuseness_fm: float = DEFAULT_DIFFUSENESS_FM,
    skin_fm: float = DEFAULT_SKIN_FM,
    c0_fm: float = DEFAULT_C0_FM,
    c1_fm: float = DEFAULT_C1_FM,
) -> FloatOrArray:
    """Return the amplitude-level Helm form factor ``F_H(E_R, A)``.

    ``ER_keV`` may be a scalar or a NumPy-compatible array.  The returned
    value has the same scalar/array character as the input.
    """

    q_gev = momentum_transfer_GeV(ER_keV, A, amu_GeV=amu_GeV)
    return helm_form_factor_q(
        q_gev,
        A,
        diffuseness_fm=diffuseness_fm,
        skin_fm=skin_fm,
        c0_fm=c0_fm,
        c1_fm=c1_fm,
    )


def helm_form_factor_squared(
    ER_keV: ArrayLike,
    A: int | float,
    **kwargs: float,
) -> FloatOrArray:
    """Return ``F_H(E_R, A)^2``.

    This is the quantity called ``HelmFormFactor`` in the older Mathematica
    cross-section block, where the squared form factor is multiplied directly
    into ``d sigma / d E_R``.
    """

    ff = np.asarray(helm_form_factor(ER_keV, A, **kwargs), dtype=float)
    ff2 = ff * ff
    return _scalar_or_array(ff2)


__all__ = [
    "DEFAULT_DIFFUSENESS_FM",
    "DEFAULT_SKIN_FM",
    "DEFAULT_C0_FM",
    "DEFAULT_C1_FM",
    "helm_diffraction_radius_fm",
    "momentum_transfer_GeV",
    "momentum_transfer_fm_inv",
    "helm_form_factor_q",
    "helm_form_factor",
    "helm_form_factor_squared",
]
