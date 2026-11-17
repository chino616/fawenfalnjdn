"""Package-backed solar-B8 SM adapters; common Runtime and direct integration.

Input authority is experiment.input.yaml + experiment.resources.npz. No workflow
records or downloaded author code are imported at runtime. XENONnT uses accepted
bin probabilities; PandaX's separate true-recoil projection does not invent Ne response.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from cevns_pyeft.contracts import (Axis,Binning,BinProbabilities,EnergySupport,IncidentStateBatch,
                                  LiveTimeExposure,TargetIsotope,TargetInventory,IntegrationSettings,TheoryPoint)
from cevns_pyeft.contracts.modules import ModuleDescriptor,UnsupportedCapabilityError,fingerprint
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.contracts.validation import readonly,plain
from cevns_pyeft.sources.composable import CallableFluenceComponent,DifferentialFluxSource
from cevns_pyeft.theory.sm_coherent import StandardModelKN
from .definition import ExperimentDefinition,ObservationDefinition,ResourceRef,digest


def value(data,key):return data['parameters'][key]['value']


@dataclass(frozen=True)
class SolarSpectrum:
    energy: np.ndarray
    shape: np.ndarray
    total_flux: float
    def __call__(self,energy):return self.total_flux*np.interp(energy,self.energy,self.shape,left=0.,right=0.)


@dataclass(frozen=True)
class UniversalSMState:
    def __call__(self,energy_MeV,*,parameters):
        if parameters.values:raise UnsupportedCapabilityError('flavor-universal SM has no state scan')
        return IncidentStateBatch(energy_MeV,np.eye(3)/3,'nu','flavor_equivalent_trace_one')


@dataclass(frozen=True)
class XenonBasisObservation:
    energy: np.ndarray
    light: np.ndarray
    charge: np.ndarray
    probability: np.ndarray
    yield_energy: np.ndarray
    light_median: np.ndarray
    charge_median: np.ndarray
    native_cs2_edges: np.ndarray
    axis_name: str
    axis_unit: str
    def describe(self):
        return ModuleDescriptor('observation','xenon_mono_basis_v1',capabilities=('bin_probabilities_1d',),
            parameters={'energy_support_keV':[float(self.energy[0]),float(self.energy[-1])],
                        'native_cs2_edges_PE':self.native_cs2_edges.tolist(),'interpolation':'linear (E,Ly,Qy), median official YBe',
                        'outside_policy':'zero within this explicitly truncated recasting model; no extrapolation',
                        'included_selection':'official source template selection, once'},
            resources={'basis_shape':list(self.probability.shape),'content':fingerprint({'energy':self.energy.tolist(),
                'light':self.light.tolist(),'charge':self.charge.tolist(),'probability':self.probability.tolist(),
                'yield_energy':self.yield_energy.tolist(),'Ly':self.light_median.tolist(),'Qy':self.charge_median.tolist()})})
    def bin_probabilities(self,*,target,recoil_keV,binning,component_id):
        if (binning.axes[0].name,binning.axes[0].unit)!=(self.axis_name,self.axis_unit):raise ValueError('response observation mismatch')
        recoil=np.asarray(recoil_keV);mask=(recoil>=self.energy[0])&(recoil<=self.energy[-1])
        probabilities=np.zeros((len(recoil),3))
        points=np.column_stack([recoil[mask],np.interp(recoil[mask],self.yield_energy,self.light_median),
                                np.interp(recoil[mask],self.yield_energy,self.charge_median)])
        probabilities[mask]=RegularGridInterpolator((self.energy,self.light,self.charge),self.probability,bounds_error=True)(points)
        return BinProbabilities(recoil,binning,probabilities,('official_early_release_joint_selection',))


@dataclass(frozen=True)
class RecoilAcceptanceObservation:
    energy: np.ndarray
    efficiency: np.ndarray
    axis_name: str
    axis_unit: str
    def describe(self):
        return ModuleDescriptor('observation','recoil_efficiency_projection_v1',capabilities=('true_recoil_projection',),
            parameters={'meaning':'efficiency-weighted true recoil, no electron ROI migration',
                        'energy':self.energy.tolist(),'efficiency':self.efficiency.tolist(),'outside_policy':'not evaluated'})
    def acceptance(self,t):return np.interp(t,self.energy,self.efficiency,left=0.,right=0.)


@dataclass(frozen=True)
class ObservationSet:
    observations: tuple
    def __iter__(self):return iter(self.observations)
    def __getitem__(self,index):return self.observations[index]
    def describe(self):return ModuleDescriptor('observation','solar_run_observations_v1',parameters={'runs':[o.describe().as_dict() for o in self.observations]})


@dataclass(frozen=True)
class SolarModel:
    source: DifferentialFluxSource
    targets: TargetInventory
    interaction: StandardModelKN
    observation: ObservationSet
    exposures_tyr: np.ndarray
    run_ids: tuple
    binning: Binning
    seconds_per_year: float
    anchor_mass_kg: float
    mode: str
    def describe(self):
        return {'source':self.source.describe().as_dict(),'interaction':self.interaction.describe().as_dict(),
                'observations':[o.describe().as_dict() for o in self.observation],
                'targets':[asdict(t) for t in self.targets.isotopes],'exposures_tyr':self.exposures_tyr.tolist(),
                'anchor_mass_kg':self.anchor_mass_kg,'seconds_per_year':self.seconds_per_year,'run_ids':self.run_ids,
                'mode':self.mode,'aggregation':'sum of run-specific cS2 bin ordinals' if self.mode=='xenon_basis' else 'true recoil bins'}


@dataclass(frozen=True)
class SolarSettings:
    mode: str
    input_parameters: object
    implementation_modules: tuple=('cevns_pyeft.experiments.solar_b8','cevns_pyeft.experiments.solar_input',
        'cevns_pyeft.theory.sm_coherent','cevns_pyeft.rates.recoil','cevns_pyeft.rates.folding',
        'cevns_pyeft.theory.kinematics','cevns_pyeft.sources.composable')


def settings(data):
    return SolarSettings(data['assembly']['detector']['mode'],{k:{f:p[f] for f in ('value','unit','role')}
        for k,p in data['parameters'].items() if p['role'] not in ('reference_only','unused_snapshot')})


@dataclass(frozen=True)
class SolarPreparation:
    def __call__(self,definition,resources):
        from .package_loader import read_package
        data,arrays=read_package(resources['package_input'])
        if data['package']['dataset_id']!=definition.dataset_id:raise ValueError('solar package identity mismatch')
        if digest(definition.physical)!=digest(settings(data)):raise ValueError('regenerate the package for changed solar settings')
        if resources['package_arrays'].resolve()!=(resources['package_input'].parent/'experiment.resources.npz').resolve():raise ValueError('undeclared archive override')
        p=lambda k:value(data,k);cfg=data['assembly'];source=cfg['source'];detector=cfg['detector']
        spectrum=SolarSpectrum(arrays[source['energy_ref']],arrays[source['shape_ref']],p('source.total_flux'))
        energies=spectrum.energy
        support=EnergySupport((float(energies[0]),float(energies[-1])),breakpoints_MeV=tuple(energies[1:-1]),interpolation_id='linear_official_Bahcall')
        component=CallableFluenceComponent('solar_B8_all_flavors','nu',support,spectrum,UniversalSMState())
        flux=DifferentialFluxSource((component,),ModuleDescriptor('source','solar_b8_flux_v1',parameters={
            'total_flux_cm2_s':spectrum.total_flux,'shape_integral':float(np.trapezoid(spectrum.shape,energies)),
            'original_table_not_renormalized':True,'flavor':'flavor-universal trace-one representative, no oscillation probabilities needed'},
            resources={'table':fingerprint({'energy':energies.tolist(),'shape':spectrum.shape.tolist()})}))
        atom_u=arrays['target_atomic_mass_u'];fraction=arrays['target_number_fraction'];numbers=arrays['target_mass_number']
        mean=float(np.dot(atom_u,fraction));atom_kg=atom_u*1e-3/p('constants.avogadro')
        counts=p('target.anchor_mass_kg')*p('constants.avogadro')*1e3*fraction/mean
        target_ids=tuple('Xe'+str(int(a)) for a in numbers)
        isotope=tuple(TargetIsotope(sid,float(mass*p('constants.amu_GeV')-p('target.Z')*p('constants.electron_mass_GeV')),
                      float(mkg),float(n),'atomic mass for inventory; stripped nucleus mass minus electrons, binding energy neglected')
                      for sid,mass,mkg,n in zip(target_ids,atom_u,atom_kg,counts))
        targets=TargetInventory(isotope,p('target.anchor_mass_kg'),{'reference':'NIST natural number fractions',
             'mean_molar_mass_g_per_mol':mean,'anchor':'algebraic normalization, not measured detector mass'})
        interaction=StandardModelKN(p('constants.G_F'),p('constants.GeV_inverse2_to_cm2'),p('constants.hbarc_GeV_fm'),
                    p('nuclear.radius_fm'),p('nuclear.skin_fm'),int(p('target.Z')),tuple(numbers),target_ids)
        obs=definition.observation;binning=Binning((Axis(obs.name,obs.unit,obs.edges),))
        if detector['mode']=='xenon_basis':
            observations=tuple(XenonBasisObservation(arrays['response_energy_keV'],arrays['response_Ly'],arrays['response_Qy'],
                 arrays['response_'+run],arrays['yield_energy_keV'],arrays['yield_Ly_median'],arrays['yield_Qy_median'],
                 arrays['cs2_edges_'+run],obs.name,obs.unit) for run in detector['run_ids'])
        else:
            observations=(RecoilAcceptanceObservation(arrays['efficiency_energy_keV'],arrays['efficiency'],obs.name,obs.unit),)
        model=SolarModel(flux,targets,interaction,ObservationSet(observations),arrays['run_exposures_tyr'],tuple(detector['run_ids']),binning,
                         p('constants.seconds_per_year'),p('target.anchor_mass_kg'),detector['mode'])
        return model,SolarExecutor(p('interaction.include_sm'),p('interaction.sin2thetaW'))


@dataclass(frozen=True)
class SolarExecutor:
    include_sm: bool
    weak_angle: float
    def default_point(self):return TheoryPoint(include_sm=self.include_sm,sin2thetaW=self.weak_angle)
    def describe_execution(self,model):return {'profile':'solar_b8_sm_v1','model':model.describe(),'default_sin2thetaW':self.weak_angle}
    def __call__(self,exp,point,backend,ns,kernel):
        from cevns_pyeft.rates.recoil import integrate_recoil_yield
        from cevns_pyeft.rates.folding import probability_fold
        if backend!='slow' or kernel is not None:raise UnsupportedCapabilityError('solar SM benchmark supports direct Slow only')
        model=exp.model;model.interaction.validate(model.targets,point)
        fluence=model.source.for_run(LiveTimeExposure(model.seconds_per_year,'reference_year'))
        integrator=IntegrationSettings(n_er=ns['n_er'],n_enu=ns['n_enu'],strategy='bin_probability_v1')
        per_run={run:{} for run in model.run_ids};recoils={};raw_values={}
        for target in model.targets.isotopes:
            max_e=fluence.components[0].support.integration_domain_MeV[1]
            upper=model.interaction.kinematics.maximum_recoil_keV(target,max_e)
            if model.mode=='xenon_basis':
                o=model.observation[0];lo=float(o.energy[0]);hi=min(float(o.energy[-1]),upper)
                extra=np.r_[o.energy,o.yield_energy]
            else:
                o=model.observation[0];lo=float(model.binning.axes[0].edges[0]);hi=min(float(model.binning.axes[0].edges[-1]),upper)
                extra=np.r_[o.energy,model.binning.axes[0].edges]
            recoil=np.unique(np.r_[np.linspace(lo,hi,ns['n_er']),extra[(extra>lo)&(extra<hi)]])
            for component in fluence.components:
                rate=integrate_recoil_yield(component,target,model.interaction,parameters=point,numerics=integrator,recoil_keV=recoil)
                recoils[target.isotope_id]=recoil;raw_values[target.isotope_id]=rate.values_per_keV*target.number_of_nuclei
                for i,(run,observation) in enumerate(zip(model.run_ids,model.observation)):
                    if model.mode=='xenon_basis':
                        values=probability_fold(rate,target,observation,model.binning)
                    else:
                        density=rate.values_per_keV*observation.acceptance(recoil)
                        edges=model.binning.axes[0].edges
                        values=np.array([np.trapezoid(density[(recoil>=a)&(recoil<=b)],recoil[(recoil>=a)&(recoil<=b)]) for a,b in zip(edges[:-1],edges[1:])])
                    per_run[run][(component.component_id,target.isotope_id)]=values*target.number_of_nuclei*model.exposures_tyr[i]/(model.anchor_mass_kg/1000)
        record={'reference_fluence':dict(fluence.normalization_record),'anchor_mass_kg':model.anchor_mass_kg,
                'run_exposures_tyr':model.exposures_tyr.tolist(),'mass_time_application':'one reference-year fluence * anchor nuclei * exposure_tyr/anchor_tonne',
                'efficiency':'included in response; applied once','c_i':'absent'}
        details={'n_er_base':ns['n_er'],'n_enu_base':ns['n_enu'],'additional_source_knots':len(fluence.components[0].support.breakpoints_MeV),
                 'recoil_grids_keV':recoils,'mode':model.mode,'quadrature':'trapezoid including response, yield and observable breakpoints'}
        detectors={run:Prediction(sum(parts.values(),np.zeros(model.binning.shape)),model.binning,parts,record,model.describe(),details)
                   for run,parts in per_run.items()}
        combined_parts={(source+'@'+run,isotope):counts for run,parts in per_run.items() for (source,isotope),counts in parts.items()}
        total=sum(combined_parts.values(),np.zeros(model.binning.shape))
        prediction=Prediction(total,model.binning,combined_parts,record,model.describe(),details,
             {'true_recoil_rates_per_tyr_keV':raw_values,'recoil_grids_keV':recoils,'response_domain':'official early recasting support' if model.mode=='xenon_basis' else 'Fig.1 visible true-energy domain, not Ne ROI'})
        return prediction,detectors,None,{'profile':'solar_b8_sm_v1','input_authority':'YAML+NPZ','algorithm':'shared direct recoil integration and accepted probability folding'}


def definition_from_solar(data,arrays,resource_prefix=''):
    prefix=Path(resource_prefix);package=data['package'];cfg=data['assembly'];p=lambda k:value(data,k)
    return ExperimentDefinition(package['dataset_id'],package['experiment_slug'],package['analysis_revision'],tuple(cfg['detector']['run_ids']),
        settings(data),ObservationDefinition(data['observable']['name'],data['observable']['unit'],tuple(arrays[data['observable']['edges_ref']]),tuple(cfg['detector']['run_ids'])),
        (ResourceRef('package_input',(prefix/'experiment.input.yaml').as_posix()),ResourceRef('package_arrays',(prefix/'experiment.resources.npz').as_posix())),
        {'slow':{k:p(ref) for k,ref in cfg['numerics']['slow'].items()}},SolarPreparation(),reproduction_sin2thetaW=p('interaction.sin2thetaW'),
        capabilities={'slow':'SM direct forward calculation','electron_spectrum':'response' if cfg['detector']['mode']=='xenon_basis' else 'BLOCKED missing US2 response','statistics':'NOT_REQUESTED'},
        validation=('tests/test_solar_b8_sm_contract.py',))
