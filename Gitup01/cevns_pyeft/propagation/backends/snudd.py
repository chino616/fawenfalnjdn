"""Thin SNuDD density-matrix adapter.

The adapter intentionally depends only on a calculator object exposing
``density(E_nus, nu)``.  It does not import SNuDD targets or spectra and it
does not return CEvNS rates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cevns_pyeft.propagation.base import PropagationState
from cevns_pyeft.propagation.density import propagation_state_from_density, validate_energy_grid_GeV
from cevns_pyeft.sources.state import ParticleKind


@dataclass(frozen=True)
class SNuDDSolarDensityBackend:
    """Wrap a SNuDD SolarDensityMatrixCalculator-like object."""

    calculator: Any
    particle_kind: ParticleKind = "nu"

    def density(self, E_nu_GeV: object, nu: str = "e") -> PropagationState:
        energy = validate_energy_grid_GeV(E_nu_GeV)
        try:
            rho = self.calculator.density(energy, nu)
        except AttributeError as exc:
            raise TypeError("calculator must expose density(E_nus, nu)") from exc
        return propagation_state_from_density(
            energy,
            rho,
            particle_kind=self.particle_kind,
        )


__all__ = ["SNuDDSolarDensityBackend"]
