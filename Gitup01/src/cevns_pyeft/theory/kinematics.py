"""Exact two-body recoil support shared by CEvNS theory implementations."""

from __future__ import annotations

import math


def _positive_finite(value: object, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def _nonnegative_finite(value: object, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be non-negative and finite")
    return result


def two_body_recoil_max_GeV(E_nu_GeV: float, m_A_GeV: float) -> float:
    """Return ``2 E_nu^2 / (m_A + 2 E_nu)`` in GeV.

    A non-positive neutrino energy is an invalid theory-core input rather than
    a zero-flux integration point.
    """

    energy = _positive_finite(E_nu_GeV, name="E_nu_GeV")
    mass = _positive_finite(m_A_GeV, name="m_A_GeV")
    return 2.0 * energy * energy / (mass + 2.0 * energy)


def validate_recoil_energy_GeV(ER_GeV: float) -> float:
    """Return a finite, non-negative recoil energy or raise ``ValueError``."""

    return _nonnegative_finite(ER_GeV, name="ER_GeV")


def is_two_body_recoil_allowed(
    E_nu_GeV: float,
    ER_GeV: float,
    m_A_GeV: float,
) -> bool:
    """Validate an elastic-recoil point and report whether it is supported.

    ``E_nu_GeV <= 0`` and ``ER_GeV < 0`` raise ``ValueError``.  A recoil
    strictly above the exact two-body endpoint is valid input but unsupported.
    """

    recoil = validate_recoil_energy_GeV(ER_GeV)
    endpoint = two_body_recoil_max_GeV(E_nu_GeV, m_A_GeV)
    return recoil <= endpoint


def minimum_neutrino_energy_GeV(ER_GeV: float, m_A_GeV: float) -> float:
    """Return the exact minimum neutrino energy for an elastic recoil."""

    recoil = _nonnegative_finite(ER_GeV, name="ER_GeV")
    mass = _positive_finite(m_A_GeV, name="m_A_GeV")
    return 0.5 * (
        recoil + math.sqrt(recoil * recoil + 2.0 * mass * recoil)
    )


__all__ = [
    "two_body_recoil_max_GeV",
    "validate_recoil_energy_GeV",
    "is_two_body_recoil_allowed",
    "minimum_neutrino_energy_GeV",
]
