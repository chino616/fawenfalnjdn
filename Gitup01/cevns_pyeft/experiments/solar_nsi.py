"""Mainline solar single-bin NSI capability; separate from frozen SM/multibin.

Onboarding Source: SolarMSW; Theory: ElectronVectorNSI (Eq95); Detector: reused
Total acceptance with explicit X-tail choice; Prediction: direct Slow below or
energy-resolved kernel; Statistics: independent fitted-signal pulls (Eq88).
"""
from dataclasses import dataclass, replace
from pathlib import Path
import hashlib,json
import numpy as np
from cevns_pyeft.contracts import IntegrationSettings,LiveTimeExposure
from cevns_pyeft.contracts.modules import ModuleDescriptor,UnsupportedCapabilityError
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.sources.solar_msw import SolarMSW
from cevns_pyeft.theory.li2026.ee_vector_nsi import ElectronVectorNSI,nsi_point,couplings
from .solar_singlebin import load_singlebin,SingleBinModel
from .catalog import ExperimentCatalog
from .definition import ResourceRef
from .loader import ResourceCatalog,load_experiment

INPUT_DIRECTORY='data/benchmarks/solar_b8_nsi_2601_19883'
EXTRA_DEPENDENCIES=('cevns_pyeft.experiments.solar_nsi','cevns_pyeft.sources.solar_msw',
    'cevns_pyeft.theory.li2026.ee_vector_nsi','cevns_pyeft.theory.li2026.coefficients',
    'cevns_pyeft.statistics.parameters','cevns_pyeft.kernels.solar_nsi')


@dataclass(frozen=True)
class NSISettings:
    base:object
    nsi_card_sha256:str
    propagation:str
    tail_mode:str
    profile_name:str
    implementation_modules:tuple


@dataclass(frozen=True)
class NSIModel(SingleBinModel):
    state_model:object
    tail_mode:str

    def describe(self):
        out=super().describe();out.update(analysis='singlebin_2601_ee_vector_nsi',
            solar_state=self.state_model.describe().as_dict(),xenon_tail_mode=self.tail_mode)
        return out


@dataclass(frozen=True)
class NSIPreparation:
    base_definition:object

    def __call__(self,definition,resources):
        data=json.loads(resources['nsi_input'].read_text(encoding='utf8'))
        if hashlib.sha256(resources['nsi_input'].read_bytes()).hexdigest()!=definition.physical.nsi_card_sha256:
            raise ValueError('NSI card changed; rebuild definition')
        name=definition.physical.profile_name
        if hashlib.sha256(resources['solar_profile'].read_bytes()).hexdigest()!=data['files'][name]['sha256']:
            raise ValueError('solar numerical profile differs from source card')
        model,_=self.base_definition.prepare(self.base_definition,resources)
        osc=data['oscillation']
        state=SolarMSW(np.loadtxt(resources['solar_profile']),osc['theta12_rad'],osc['theta13_rad'],osc['dm21_eV2'],
            definition.physical.propagation,data['physics']['radial_quadrature_order_per_panel'])
        component=replace(model.source.components_per_second[0],state_provider=state)
        source=replace(model.source,components_per_second=(component,),descriptor=ModuleDescriptor('source','solar_B8_ee_NSI',
            parameters={'base_flux':model.source.describe().as_dict(),'state':state.describe().as_dict()},
            resources={'solar_profile_sha256':data['files'][name]['sha256']}))
        values={f:getattr(model,f) for f in SingleBinModel.__dataclass_fields__}
        values.update(source=source,interaction=ElectronVectorNSI(resources['nuclear_response'],tuple(t.isotope_id for t in model.targets.isotopes)))
        return NSIModel(**values,state_model=state,tail_mode=definition.physical.tail_mode),NSIExecutor(data['physics']['sin2thetaW'])


def check_point(model,point):
    eu,ed=couplings(point);state=point.state.values
    if set(state)!={'epsilon_ee_uV','epsilon_ee_dV'} or not np.allclose(
        [state['epsilon_ee_uV'],state['epsilon_ee_dV']],[eu,ed],rtol=1e-13,atol=1e-14):
        raise ValueError('scattering and propagation NSI parameters must be bound to the same point')
    model.interaction.validate(model.targets,point)
    return eu,ed


def tail_epsilon(model):
    if model.observation.complete:return 0.
    return {'zero':0.,'unit':1.,'flat_sensitivity':float(model.observation.efficiency[-1]),'bounded':0.}[model.tail_mode]


def make_prediction(model,parts,known,tail,point,numerics,*,backend):
    counts=sum(parts.values(),np.zeros(1));complete=model.observation.complete or model.tail_mode!='bounded'
    prediction=Prediction(counts,model.binning,parts,
        {'exposure_tyr':model.exposure_tyr,'flux_cm2_s':5.46e6,'mass_anchor_tonne':1.,
         'rule':'one reference-year fluence * original nuclei/tonne * exposure_tyr; Total ROI efficiency once',
         'ci':'absent','flux_fit_scale':'absent'},model.describe(),numerics,
        {'coverage_complete':complete,'experimental_efficiency_coverage_complete':model.observation.complete,
         'known_events':float(sum(known.values())),'unselected_tail_events':float(sum(tail.values())),
         'full_signal_bounds':[float(sum(known.values())),float(sum(known.values())+sum(tail.values()))],
         'tail_mode':model.tail_mode,'backend':backend,'parameters_ee':couplings(point),
         'source_state':'physical Pee, equivalent mu/tau split valid only for this ee-vector subspace'})
    return prediction,{model.sample:prediction},None,{'analysis':'solar_ee_vector_nsi','backend':backend,'tail_mode':model.tail_mode}


@dataclass(frozen=True)
class NSIExecutor:
    weak_angle:float
    supports_state_parameters=True

    def default_point(self):return nsi_point(sin2thetaW=self.weak_angle)
    def describe_execution(self,model):return {'analysis':'solar_ee_vector_nsi','model':model.describe(),'default_sin2thetaW':self.weak_angle}
    def compile(self,experiment,numerics):
        from cevns_pyeft.kernels.solar_nsi import compile_kernel
        return compile_kernel(experiment,numerics,self.weak_angle)

    def __call__(self,experiment,point,backend,numerics,kernel):
        check_point(experiment.model,point)
        if backend=='fast':
            if kernel is None:raise ValueError('supply the matching energy-resolved NSI kernel')
            return kernel.predict(experiment,point,numerics)
        if backend!='slow' or kernel is not None:raise UnsupportedCapabilityError('explicit Slow or matching solar NSI kernel required')
        from cevns_pyeft.rates.recoil import integrate_recoil_yield
        m=experiment.model;o=m.observation;lo,hi=o.requested_bounds;split=o.verified_upper
        grid=np.unique(np.r_[np.linspace(lo,hi,numerics['n_er']),o.energy[(o.energy>lo)&(o.energy<hi)],split])
        known_mask=grid<=split;tail_mask=grid>=split
        fluence=m.source.for_run(LiveTimeExposure(m.seconds_per_year,'one_reference_year'))
        integrator=IntegrationSettings(n_er=numerics['n_er'],n_enu=numerics['n_enu'],strategy='bin_probability_v1')
        parts={};known={};tails={}
        for target in m.targets.isotopes:
            rate=integrate_recoil_yield(fluence.components[0],target,m.interaction,parameters=point,numerics=integrator,recoil_keV=grid)
            density=rate.values_per_keV*target.number_of_nuclei*m.exposure_tyr
            a=float(np.trapezoid(density[known_mask]*o.known_acceptance(grid[known_mask]),grid[known_mask]))
            b=float(np.trapezoid(density[tail_mask],grid[tail_mask])) if not o.complete else 0.
            key=('solar_B8',target.isotope_id);known[key]=a;tails[key]=b;parts[key]=np.array([a+tail_epsilon(m)*b])
        return make_prediction(m,parts,known,tails,point,numerics,backend='slow')


def load_solar_nsi(sample,*,root=None,propagation='nsi_msw',tail_mode='flat_sensitivity',composition='gs98',interaction=None):
    if propagation not in ('nsi_msw','sm_fixed') or tail_mode not in ('flat_sensitivity','zero','unit','bounded') or composition not in ('gs98','agss09'):
        raise ValueError('select explicit propagation, tail and solar-composition choices')
    base=load_singlebin(sample,root=root)
    root=base.resource_catalog.root;directory=root/INPUT_DIRECTORY;card=directory/'nsi.input.json';data=json.loads(card.read_text(encoding='utf8'))
    if hashlib.sha256((root/data['base_singlebin_card']).read_bytes()).hexdigest()!=data['base_card_sha256']:
        raise ValueError('base singlebin inputs changed; review NSI source contract')
    profile=f'solar_b16_{composition}_profile.txt';physical=NSISettings(base.definition.physical,hashlib.sha256(card.read_bytes()).hexdigest(),
        propagation,tail_mode,profile,tuple(dict.fromkeys((*base.definition.physical.implementation_modules,*EXTRA_DEPENDENCIES))))
    dataset=base.dataset_id+'__ee_vector_nsi_'+propagation+'_'+tail_mode+'_'+composition
    refs=tuple(replace(ref,path=str(directory/'fitted_yields.json')) if ref.id=='fitted_yields' else ref for ref in base.definition.resources)
    refs+=(ResourceRef('nsi_input',str(card),semantic='explicit NSI source/interaction/statistics choices and citations'),
           ResourceRef('solar_profile',str(directory/profile),semantic='r, ne/N_A, derived nn/N_A, B8 production profile; pinned sources'))
    definition=replace(base.definition,dataset_id=dataset,analysis_revision='solar_ee_nsi_v3.3_'+propagation+'_'+tail_mode+'_'+composition,
        physical=physical,resources=refs,prepare=NSIPreparation(base.definition),
        numerical_profiles={'slow':{'n_er':801,'n_enu':480},'fast':{'n_er':801,'n_enu':64}},
        capabilities={'analysis':'singlebin_ee_vector_nsi','slow':'parameter-dependent MSW plus nuclear Response',
                      'fast':'energy_resolved_ee_vector_nsi_v1; never fixed-rho interface kernel','statistics':'three independent Eq88 pulls; exact printed percentages'},
        validation=('tests/test_solar_nsi.py',))
    registry=ExperimentCatalog(builtins=False).register(dataset,definition)
    return load_experiment(dataset,definition=definition,registry=registry,resources=ResourceCatalog(root),
        components={'interaction':interaction} if interaction is not None else None)
