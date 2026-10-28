"""Candidate source and observation components for the shared mass-time route."""
from dataclasses import dataclass
from types import MappingProxyType
import numpy as np
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.source import IncidentStateBatch
from ..definition import plain

@dataclass(frozen=True)
class ReactorSource:
    settings: object
    tables: object
    diagnostic_boundaries: tuple
    @property
    def energy_support_mev(self):return self.settings.energy_support_mev
    @property
    def component_ids(self):return self.settings.components
    def differential_flux(self,component,energy):
        from .source import differential_flux
        return differential_flux(component,energy,data_dir=self.tables,settings=self.settings)
    def integration_breakpoints(self):
        from .source import kopeikin_nodes
        nodes,_=kopeikin_nodes(data_dir=self.tables)
        return np.r_[nodes,self.diagnostic_boundaries]
    def state_at(self,energy,*,parameters):
        from .source import source_state
        if parameters.values:raise ValueError('fixed reactor state does not consume state parameters')
        state=source_state()
        return IncidentStateBatch(energy,state.rho,state.particle_kind,'legacy_reactor_e_antinu')
    def describe(self):
        return ModuleDescriptor('source','stationary_reactor_flux',parameters=plain(self.settings),
            resources={name:{'path':str(path)} for name,path in self.tables.items()})

@dataclass(frozen=True)
class ScaledFluxSource:
    original: object
    factor: float
    def __post_init__(self):
        from cevns_pyeft.contracts.validation import positive
        positive(self.factor,'flux scale',zero=True)
    @property
    def energy_support_mev(self):return self.original.energy_support_mev
    @property
    def component_ids(self):return self.original.component_ids
    def differential_flux(self,component,energy):return self.original.differential_flux(component,energy)*self.factor
    def integration_breakpoints(self):return self.original.integration_breakpoints()
    def state_at(self,energy,*,parameters):return self.original.state_at(energy,parameters=parameters)
    def describe(self):return ModuleDescriptor('source','scaled_stationary_flux',parameters={'factor':self.factor,'original':self.original.describe().as_dict()})

@dataclass(frozen=True)
class GeObservation:
    settings: object
    def acceptance(self,recoil,detector,edges):
        from .detector_response import detector_bin_acceptance
        return detector_bin_acceptance(recoil,detector,settings=self.settings,edges_evee=edges)
    def describe(self):return ModuleDescriptor('observation','legacy_Ge_Gaussian',parameters=plain(self.settings))


def assemble_mass_time(settings,resources,edges):
    from cevns_pyeft.core.mass_time import MassTimeModel
    from cevns_pyeft.contracts.target import TargetIsotope
    from cevns_pyeft.contracts.observation import Axis,Binning
    from cevns_pyeft.foundation.constants import AMU_GEV
    from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction
    target=TargetIsotope(settings.response_key,settings.target_A*AMU_GEV,settings.target_A*1.6605390666e-27,0,'identity_only_normalization_is_nuclei_per_kg')
    source=ReactorSource(settings.source,MappingProxyType({k:resources[k] for k in ('kopeikin','mueller')}),tuple(b[1] for b in settings.energy_region_bounds_mev[:-1]))
    return MassTimeModel(source,target,settings.nuclei_per_kg,
        Li2026LegacyInteraction(resources['responses'],response_keys={settings.response_key:settings.response_key},c10_mass_mode=settings.c10_mass_mode),
        GeObservation(settings.detector),settings.exposures,Binning((Axis('ionization_energy','eVee',edges),)),settings.seconds_per_day)
