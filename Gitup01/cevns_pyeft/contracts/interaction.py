from dataclasses import dataclass
from typing import Protocol
import numpy as np
from cevns_pyeft.theory.kinematics import minimum_neutrino_energy_GeV, two_body_recoil_max_GeV
from .validation import coordinates, readonly


@dataclass(frozen=True)
class ElasticKinematics:
    process_id: str = "elastic_neutrino_nucleus_v1"

    def minimum_energy_MeV(self, target, recoil_keV):
        return minimum_neutrino_energy_GeV(float(recoil_keV) * 1e-6, target.kinematic_mass_GeV) * 1e3

    def maximum_recoil_keV(self, target, energy_MeV):
        return two_body_recoil_max_GeV(float(energy_MeV) * 1e-3, target.kinematic_mass_GeV) * 1e6


@dataclass(frozen=True)
class DifferentialCrossSection:
    energy_MeV: np.ndarray
    values_cm2_per_keV: np.ndarray
    recoil_keV: float
    model_id: str
    unit: str = "cm^2/keV"

    def __post_init__(self):
        energy = coordinates(self.energy_MeV, "cross-section energy")
        values = readonly(self.values_cm2_per_keV)
        if values.shape != energy.shape or np.any(values < 0) or self.unit != "cm^2/keV":
            raise ValueError("invalid cross-section shape, sign or unit")
        if np.any(energy <= 0) or not np.isfinite(self.recoil_keV) or self.recoil_keV < 0:
            raise ValueError("invalid cross-section coordinates")
        object.__setattr__(self, "energy_MeV", energy)
        object.__setattr__(self, "values_cm2_per_keV", values)


class InteractionModel(Protocol):
    kinematics: ElasticKinematics

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters) -> DifferentialCrossSection: ...
    def describe(self): ...
