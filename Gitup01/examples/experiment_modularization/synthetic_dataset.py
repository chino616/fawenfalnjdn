"""Synthetic extension example; deliberately not a registered real experiment."""
from dataclasses import dataclass
import numpy as np
from cevns_pyeft.experiments.definition import ExperimentDefinition, ObservationDefinition
from cevns_pyeft.contracts import (Axis,Binning,BinProbabilities,DetectorFluence,EnergySupport,
    IncidentStateBatch,IntegratedRunReference,IntegrationSettings,TargetInventory,TargetIsotope)
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.interaction import DifferentialCrossSection
from cevns_pyeft.sources.composable import CallableFluenceComponent,IntegratedFluenceSource
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.core.predict import predict

@dataclass(frozen=True)
class Settings:
    flux: float = 2.
    cross_section: float = 3.
    nuclei: float = 2.
    probability: tuple = (.2,.3,.1)

class SyntheticKinematics:
    process_id='elastic_neutrino_nucleus_v1'
    def minimum_energy_MeV(self,target,recoil_keV): return 0.
    def maximum_recoil_keV(self,target,energy_MeV): return 1.

class Interaction:
    kinematics=SyntheticKinematics()
    def __init__(self,value): self.value=value
    def describe(self): return ModuleDescriptor('interaction','synthetic_constant')
    def dsigma_dT(self,*,target,energy_MeV,recoil_keV,incident_state,parameters):
        return DifferentialCrossSection(energy_MeV,np.full_like(energy_MeV,self.value),recoil_keV,'synthetic_constant')

class Observation:
    def __init__(self,definition):
        self.axis_name=definition.observation.name
        self.axis_unit=definition.observation.unit
        self.probabilities=definition.physical.probability
    def describe(self): return ModuleDescriptor('observation','synthetic_probabilities',capabilities=('bin_probabilities_1d',))
    def bin_probabilities(self,*,target,recoil_keV,binning,component_id):
        return BinProbabilities(recoil_keV,binning,np.tile(self.probabilities,(len(recoil_keV),1)))

def state(energy_MeV,*,parameters):
    if parameters.values: raise ValueError('synthetic state has no scan parameters')
    return IncidentStateBatch(energy_MeV,np.diag([1.,0.,0.]),'nu','synthetic_pure_e')

class Execute:
    def __call__(self,exp,point,backend,ns,kernel):
        p=predict(exp.model,parameters=point,numerics=IntegrationSettings(n_er=ns['n_er'],n_enu=ns['n_enu'],strategy='bin_probability_v1'))
        return p,{'detector':p},None,{'strategy':'synthetic bin_probability_v1'}

def prepare(definition,resources):
    p=definition.physical
    component=CallableFluenceComponent('synthetic_beam_alpha','nu',EnergySupport((1.,3.)),lambda e:np.full_like(e,p.flux),state)
    source=IntegratedFluenceSource(DetectorFluence((component,),'synthetic_run'),ModuleDescriptor('source','synthetic_constant'))
    target=TargetIsotope('synthetic_nucleus',1.,1.,p.nuclei)
    model=ExperimentModel(source,IntegratedRunReference('synthetic_run'),TargetInventory((target,),p.nuclei),
        Interaction(p.cross_section),Observation(definition),Binning((Axis(definition.observation.name,definition.observation.unit,definition.observation.edges),)))
    return model,Execute()

DEFINITION=ExperimentDefinition('synthetic_demo_v1','SYNTHETIC','demo1',('synthetic_run',),Settings(),
    ObservationDefinition('synthetic observable','synthetic_unit',(0.,1.,2.,4.)),(),
    {'slow':{'n_er':5,'n_enu':7}},prepare,capabilities={'slow':'synthetic analytic example','fast':'unsupported'})

def independent_expected():
    # Integral over E in [1,3], T in [.1,1], times nuclei and bin probabilities.
    return 2.*3.*(3.-1.)*(1.-.1)*2.*np.array([.2,.3,.1])

if __name__=='__main__':
    from cevns_pyeft.experiments.catalog import ExperimentCatalog
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.experiments.runtime import predict_experiment
    catalog=ExperimentCatalog(builtins=False).register(DEFINITION.dataset_id,DEFINITION,aliases=('demo',))
    exp=load_experiment('demo',registry=catalog)
    result=predict_experiment(exp)
    np.testing.assert_allclose(result.counts,independent_expected(),rtol=1e-14)
    print(dict(dataset=result.dataset_id,counts=result.counts.tolist()))
