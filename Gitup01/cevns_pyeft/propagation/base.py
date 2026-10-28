"""Canonical propagation-state objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from cevns_pyeft.sources.state import ParticleKind, validate_density_matrices, validate_particle_kind
from cevns_pyeft.theory.li2026.flavor import FLAVOR_ORDER


EnergyGrid = NDArray[np.float64]
DensityGrid = NDArray[np.complex128]
PROPAGATION_FLAVOR_BASIS = tuple(FLAVOR_ORDER)


@dataclass(frozen=True)
class PropagationState:
    """Energy-indexed neutrino flavor density matrices.

    The object deliberately stores only propagation output: no target, CEvNS
    spectrum, rate, detector response, or experiment normalization belongs at
    this boundary.
    """

    energy_GeV: EnergyGrid
    rho: DensityGrid
    particle_kind: ParticleKind = "nu"
    basis: tuple[str, str, str] = PROPAGATION_FLAVOR_BASIS
    unit: str = "dimensionless"

    def __post_init__(self) -> None:
        energy = np.asarray(self.energy_GeV, dtype=np.float64)
        if energy.ndim != 1:
            raise ValueError(f"energy_GeV must have shape (N_E,), got {energy.shape}")
        if not np.all(np.isfinite(energy)):
            raise ValueError("energy_GeV entries must be finite")
        if np.any(energy < 0.0):
            raise ValueError("energy_GeV entries must be non-negative")
        if tuple(self.basis) != PROPAGATION_FLAVOR_BASIS:
            raise ValueError(f"basis must be {PROPAGATION_FLAVOR_BASIS}, got {self.basis!r}")
        if self.unit != "dimensionless":
            raise ValueError("rho unit must be dimensionless")

        rho = np.array(
            validate_density_matrices(self.rho, energy_shape=energy.shape),
            dtype=np.complex128,
            copy=True,
        )
        energy_copy = np.array(energy, dtype=np.float64, copy=True)
        energy_copy.setflags(write=False)
        rho.setflags(write=False)
        object.__setattr__(self, "energy_GeV", energy_copy)
        object.__setattr__(self, "rho", rho)
        object.__setattr__(self, "particle_kind", validate_particle_kind(self.particle_kind))
        object.__setattr__(self, "basis", PROPAGATION_FLAVOR_BASIS)


class DensityMatrixBackend(Protocol):
    """Backend returning only canonical propagation density matrices."""

    def density(self, E_nu_GeV: object, nu: str) -> PropagationState:
        ...


__all__ = [
    "DensityGrid",
    "DensityMatrixBackend",
    "EnergyGrid",
    "PROPAGATION_FLAVOR_BASIS",
    "PropagationState",
]
