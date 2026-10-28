"""Integrate declared fluence components into per-nucleus recoil yields."""
import numpy as np
from cevns_pyeft.contracts.prediction import RecoilYield


def _cross_section(component, target, interaction, energy, recoil, parameters):
    state = component.state_at(energy, parameters=parameters.state)
    state.require_coordinates(energy, component.particle_kind)
    cross = interaction.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=recoil,
                                  incident_state=state, parameters=parameters)
    if not np.array_equal(cross.energy_MeV, energy) or cross.recoil_keV != recoil:
        raise ValueError(f"cross-section coordinate mismatch for {component.component_id}/{target.isotope_id}")
    return cross.values_cm2_per_keV


def integrate_recoil_yield(component, target, interaction, *, parameters, numerics, recoil_keV):
    lo, hi = component.support.integration_domain_MeV
    energy_grid = np.unique(np.concatenate((np.linspace(lo, hi, numerics.n_enu), component.support.breakpoints_MeV)))
    output = np.zeros_like(recoil_keV, dtype=float)
    for index, recoil in enumerate(recoil_keV):
        minimum = interaction.kinematics.minimum_energy_MeV(target, float(recoil))
        energy = energy_grid[(energy_grid >= minimum) & (energy_grid > 0)]
        if energy.size:
            values = np.asarray(component.continuum(energy), dtype=float)
            if values.shape != energy.shape or not np.all(np.isfinite(values)) or np.any(values < 0):
                raise ValueError(f"invalid continuum for {component.component_id} at {energy}")
            cross = _cross_section(component, target, interaction, energy, float(recoil), parameters)
            output[index] = np.trapezoid(cross * values, energy)
        for line in component.lines:
            if line.energy_MeV >= minimum:
                query = np.array([line.energy_MeV])
                cross = _cross_section(component, target, interaction, query, float(recoil), parameters)
                output[index] += line.fluence_per_cm2 * float(cross[0])
    return RecoilYield(component.component_id, target.isotope_id, recoil_keV, output)
