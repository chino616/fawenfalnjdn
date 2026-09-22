"""Validation and matching helpers for propagation density matrices."""

from __future__ import annotations

import math
from typing import Literal, Mapping, Optional

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.propagation.base import PropagationState
from cevns_pyeft.theory.li2026.flavor import FlavorMatrix, zero_flavor_matrix
from cevns_pyeft.theory.li2026.left_to_ci import LeftKey
from cevns_pyeft.theory.li2026.operators import canonicalize_wilson_coefficients


WilsonContent = Literal["np_only", "sm_plus_np"]


def validate_energy_grid_GeV(E_nu_GeV: object) -> np.ndarray:
    """Return a finite one-dimensional neutrino-energy grid in GeV."""

    energy = np.atleast_1d(np.asarray(E_nu_GeV, dtype=np.float64))
    if energy.ndim != 1:
        raise ValueError(f"E_nu_GeV must be scalar or one-dimensional, got {energy.shape}")
    if not np.all(np.isfinite(energy)):
        raise ValueError("E_nu_GeV entries must be finite")
    if np.any(energy < 0.0):
        raise ValueError("E_nu_GeV entries must be non-negative")
    return energy


def propagation_state_from_density(
    E_nu_GeV: object,
    rho: object,
    *,
    particle_kind: Literal["nu", "antinu"] = "nu",
) -> PropagationState:
    """Validate backend density output and return a canonical state."""

    return PropagationState(
        energy_GeV=validate_energy_grid_GeV(E_nu_GeV),
        rho=rho,
        particle_kind=particle_kind,
    )


def wilson_np_to_vector_nsi(
    *,
    left_wcs: Optional[Mapping[str, FlavorMatrix]] = None,
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]] = None,
    wilson_content: WilsonContent = "np_only",
) -> dict[str, FlavorMatrix]:
    """Map NP-only vector LEFT coefficients to propagation NSI matrices.

    SNuDD's matter Hamiltonian already contains the SM matter potential.  This
    helper therefore rejects total SM+NP input instead of silently double
    counting the SM piece.  Only C6u1 and C6d1 are accepted for vector NSI
    matching: epsilon^q = -C6q1_NP / (sqrt(2) G_F).
    """

    if wilson_content != "np_only":
        raise ValueError("propagation NSI matching requires wilson_content='np_only'")

    coefficients = canonicalize_wilson_coefficients(
        left_wcs=left_wcs,
        wc_triplets=wc_triplets,
    )
    supported = {(6, 1, "u"), (6, 1, "d")}
    unsupported = sorted(key for key in coefficients if key not in supported)
    if unsupported:
        raise ValueError(f"Unsupported propagation NSI Wilson coefficients: {unsupported}")

    prefactor = -1.0 / (math.sqrt(2.0) * float(c.G_F))
    return {
        "u": prefactor * coefficients.get((6, 1, "u"), zero_flavor_matrix()),
        "d": prefactor * coefficients.get((6, 1, "d"), zero_flavor_matrix()),
    }


__all__ = [
    "WilsonContent",
    "propagation_state_from_density",
    "validate_energy_grid_GeV",
    "wilson_np_to_vector_nsi",
]
