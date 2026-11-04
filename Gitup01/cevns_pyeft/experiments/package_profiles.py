"""Code-owned v2 assembly profiles using existing contracts and Runtime."""
from dataclasses import dataclass, replace, field
from pathlib import Path
import hashlib
import numpy as np
from .definition import (ExperimentDefinition, ObservationDefinition, StatisticsDefinition, ResourceRef,
                         SNSRun, digest, frozen_mapping)


@dataclass(frozen=True)
class ArrayEfficiency:
    x: np.ndarray
    y: np.ndarray
    low: float
    threshold: float | None

    def __post_init__(self):
        from cevns_pyeft.contracts.validation import readonly
        x,y=readonly(self.x),readonly(self.y)
        if x.ndim!=1 or len(x)<2 or y.shape!=x.shape or not np.all(np.diff(x)>0):
            raise ValueError('invalid efficiency coordinates/values')
        object.__setattr__(self,'x',x);object.__setattr__(self,'y',y)

    def __call__(self, value):
        x=np.asarray(value,float)
        result=np.interp(x,self.x,self.y,left=self.low,right=float(self.y[-1]))
        if self.threshold is not None:result=np.where(x>self.threshold,result,self.low)
        return np.where(np.isfinite(x),result,0.)

    def describe(self):
        return {'model_id':'legacy_efficiency_curve_v1','coordinates':self.x,'values':self.y,
                'low':self.low,'threshold':self.threshold,'right':'last_value'}


@dataclass(frozen=True)
class ProfileSettings:
    run: SNSRun
    mass_kg: float
    atomic_mass_kg: float
    targets: tuple
    target_id: str | None
    response_key: str | None
    pe_per_keV: float | None
    slow_pe_nodes: int | None
    mean_linear: float | None
    mean_quadratic: float | None
    sigma_coefficient: float | None
    c10_mass_mode: str
    input_parameters: object
    profile: str
    implementation_modules: tuple = ('cevns_pyeft.experiments.package_profiles','cevns_pyeft.experiments.package_components',
        'cevns_pyeft.rates.legacy_observables','cevns_pyeft.rates.recoil','cevns_pyeft.rates.differential',
        'cevns_pyeft.rates.folding','cevns_pyeft.nuclear.response','cevns_pyeft.theory.li2026.amplitude',
        'cevns_pyeft.theory.li2026.left_to_ci','cevns_pyeft.theory.li2026.responses','cevns_pyeft.theory.li2026.coefficients')


def _value(data, key, unit=None):
    p=data['parameters'][key]
    if p['role'] in ('reference_only','unused_snapshot') or p['value'] is None:
        raise ValueError('inactive/missing runtime parameter: '+key)
    if unit is not None and p['unit']!=unit:raise ValueError('runtime parameter unit: '+key+' expected '+unit)
    return p['value']


def _physical(data):
    p=lambda key,unit=None:_value(data,key,unit)
    cfg=data['assembly'];s=cfg['source'];t=cfg['target'];d=cfg['detector']
    run=SNSRun(p(t['mass_ref'],'kg'),p(s['baseline_ref'],'m'),p(s['pot_ref'],'POT'),
        p(s['yield_ref'],'neutrinos/species/POT'),(p('source.tabulation_min'),p('source.tabulation_max')),
        (p('source.mask_min'),p('source.mask_max')),p('source.tabulation_nodes'),p('source.interpolation'))
    ids=tuple(i['id'] for i in t['isotopes'])
    triples=tuple((i,i,p(f'target.{i}.A')) for i in ids)
    statistics_model=cfg['statistics'].get('model_id')
    physics_models=set(data['models'])-{statistics_model}
    values={key: ({f:p[f] for f in ('value','unit','role')}) for key,p in data['parameters'].items()
            if p['role'] not in ('reference_only','unused_snapshot') and physics_models.intersection(p['consumers'])}
    return ProfileSettings(run,p(t['mass_ref'],'kg'),p('target.atomic_mass_kg','kg'),triples,
        ids[0] if len(ids)==1 else None,ids[0] if len(ids)==1 else None,
        *(p(d[k+'_ref'],unit) if k+'_ref' in d else None for k,unit in (
            ('pe_per_keV','PE/keV'),('slow_pe_nodes','1'),('mean_linear','PE/keV'),
            ('mean_quadratic','PE/keV^2'),('sigma_coefficient','PE^0.5'))),
        cfg['interaction']['c10_mass_mode'],values,cfg['profile'])


def assemble(definition,data,arrays):
    from .package_components import (ArraySource,ArrayContinuum,ZeroContinuum,ArrayState,
                                     ArrayInteraction,response_from_arrays,check_engine_snapshot)
    from cevns_pyeft.contracts.source import POTExposure,DetectorFluence,EnergySupport,FluenceLine
    from cevns_pyeft.sources.composable import CallableFluenceComponent
    from cevns_pyeft.contracts.target import TargetIsotope,TargetInventory
    from cevns_pyeft.targets.materials import inventory_from_mass_fractions
    from cevns_pyeft.contracts.observation import Axis,Binning
    from cevns_pyeft.detectors.coherent import DeterministicPEObservation,ObservedGaussianObservation
    from cevns_pyeft.core.model import ExperimentModel
    check_engine_snapshot(data)
    cfg=data['assembly'];p=lambda k,u=None:_value(data,k,u);physical=definition.physical
    original=_physical(data)
    if (physical.run.energy_tabulation,physical.run.node_support,physical.run.num_points,physical.run.interpolation)!=(
            original.run.energy_tabulation,original.run.node_support,original.run.num_points,original.run.interpolation):
        raise ValueError('source tabulation override requires explicit resource regeneration')
    if (physical.targets,physical.profile,physical.c10_mass_mode)!=(original.targets,original.profile,original.c10_mass_mode):
        raise ValueError('target recipe/profile/theory mode requires another explicit package binding')
    if (definition.observation.name,definition.observation.unit)!=('reconstructed PE spectrum','PE'):
        raise ValueError('legacy package profile requires its PE observation axis')
    s=cfg['source'];run=POTExposure(physical.run.total_pot,definition.dataset_id)
    support=EnergySupport((p(s['integration_min_ref'],'MeV'),p(s['integration_max_ref'],'MeV')),
                          (p('source.tabulation_min','MeV'),p('source.tabulation_max','MeV')),
                          interpolation_id='package_linear',convention_id='legacy_sns_mask_DAR')
    parts=[]
    for c in s['components']:
        continuum=ZeroContinuum() if c['continuum_ref'] is None else ArrayContinuum(arrays[s['energy_ref']],arrays[c['continuum_ref']])
        if c['continuum_ref'] is not None:
            norm=data['resources']['arrays'][c['continuum_ref']]['normalization']
            if norm['runtime_factors'] or set(norm['included_factors'])!={'POT','yield','geometry'}:
                raise ValueError('invalid materialized source normalization')
        lines=tuple(FluenceLine(l['id'],p(l['energy_ref'],'MeV'),p(l['fluence_ref'],'cm^-2')) for l in c['lines'])
        parts.append(CallableFluenceComponent(c['id'],c['particle_kind'],support,continuum,ArrayState(arrays[c['rho_ref']],c['particle_kind']),lines))
    fluence=DetectorFluence(tuple(parts),run.run_id,{'authority':'NPZ continuum + derived prompt','extra_factors':[]})
    source=ArraySource(fluence,physical.run.baseline_m,physical.run.yield_per_pot,p(s['pot_ref']),p(s['baseline_ref']),p(s['yield_ref']),
        {k:v['sha256_raw_c_order'] for k,v in data['resources']['arrays'].items() if k.startswith(('source_','rho_'))})
    isotopes=tuple(TargetIsotope(i['id'],p(f'target.{i["id"]}.mass_GeV','GeV'),
        p(f'target.{i["id"]}.mass_kg','kg'),p(f'target.{i["id"]}.nuclei','nuclei'),'legacy_A_times_amu') for i in cfg['target']['isotopes'])
    fractions=[p(f'target.{i.isotope_id}.mass_fraction','1') for i in isotopes]
    base_mass=p(cfg['target']['mass_ref'],'kg');base_atomic=p('target.atomic_mass_kg','kg')
    if physical.mass_kg==base_mass and physical.atomic_mass_kg==base_atomic:
        targets=TargetInventory(isotopes,physical.mass_kg,{'fraction_convention':'mass',
            'fractions':dict(zip((i.isotope_id for i in isotopes),fractions))})
    else:
        parts=tuple(replace(i,nucleus_mass_kg=i.nucleus_mass_kg*physical.atomic_mass_kg/base_atomic,number_of_nuclei=0) for i in isotopes)
        targets=inventory_from_mass_fractions(physical.mass_kg,parts,fractions)
    responses={i['id']:response_from_arrays(data,arrays,i['id'],i['responses']) for i in cfg['target']['isotopes']}
    snapshot={k:p(k) for k,v in data['parameters'].items() if k.startswith(('constants.','lecs.')) and v['role'] not in ('reference_only','unused_snapshot')}
    interaction=ArrayInteraction(responses,physical.c10_mass_mode,snapshot)
    d=cfg['detector'];eff=ArrayEfficiency(arrays[d['efficiency_energy_ref']],arrays[d['efficiency_values_ref']],
        p(d['efficiency_low_ref'],'1'),p(d['efficiency_threshold_ref'],'PE') if d['efficiency_threshold_ref'] else None)
    if cfg['profile']=='deterministic_pe_legacy_v1':
        observation=DeterministicPEObservation(physical.pe_per_keV,physical.slow_pe_nodes,eff)
    elif cfg['profile']=='observed_gaussian_legacy_v1':
        observation=ObservedGaussianObservation(physical.mean_linear,physical.mean_quadratic,physical.sigma_coefficient,eff)
    else:raise ValueError('no executable assembly profile: '+cfg['profile'])
    obs=definition.observation
    return ExperimentModel(source,run,targets,interaction,observation,Binning((Axis(obs.name,obs.unit,obs.edges),)),
                           model_id=cfg['profile'])


@dataclass(frozen=True)
class ProfilePreparation:
    def __call__(self,definition,resources):
        from .package_loader import read_package
        data,arrays=read_package(resources['package_input'])
        if data['package']['dataset_id']!=definition.dataset_id:raise ValueError('dataset identity differs')
        if resources['package_arrays'].resolve()!=(resources['package_input'].parent/'experiment.resources.npz').resolve():
            raise ValueError('undeclared NPZ resource override')
        if data['capabilities']['signal']['status'] in ('BLOCKED','NOT_APPLICABLE'):raise ValueError('signal capability BLOCKED/NOT_APPLICABLE')
        model=assemble(definition,data,arrays)
        return model,ProfileExecutor(data['assembly']['profile'],_value(data,'interaction.include_sm'),
            _value(data,'interaction.sin2thetaW'),data['capabilities']['fast']['status'] not in ('BLOCKED','NOT_APPLICABLE'),
            _value(data,'numerics.recoil_min_keV','keV') if data['assembly']['profile']=='observed_gaussian_legacy_v1' else None,
            digest(model.describe()))

    def physics_resource_identity(self,definition,resolved):
        from .package_loader import read_package
        data,_=read_package(resolved['package_input'])
        physics_models={k:v for k,v in data['models'].items() if k!=data['assembly']['statistics'].get('model_id')}
        physical_arrays={ref for model in physics_models.values() for ref in model['resource_refs']}
        return {'package_input':digest({'parameters':_physical(data).input_parameters,
                                      'assembly':{k:v for k,v in data['assembly'].items() if k!='statistics'},
                                      'models':{k:{f:v[f] for f in ('model_revision','formula','parameter_refs','resource_refs','depends_on')}
                                                for k,v in physics_models.items()}}),
                'package_arrays':digest({k:v['sha256_raw_c_order'] for k,v in data['resources']['arrays'].items() if k in physical_arrays})}


@dataclass(frozen=True)
class ProfileExecutor:
    profile: str
    include_sm: bool
    sin2thetaW: float
    fast_allowed: bool
    recoil_min_keV: float | None
    native_model_identity: str

    def default_point(self):
        from cevns_pyeft.contracts import TheoryPoint
        return TheoryPoint(include_sm=self.include_sm,sin2thetaW=self.sin2thetaW)

    def describe_execution(self,model):
        return {'profile':self.profile,'model':model.describe(),'default_theory':[self.include_sm,self.sin2thetaW]}

    def _settings(self,ns):
        values=dict(ns)
        if self.profile.startswith('deterministic'):
            values['recoil_min_keV']=None
        else:
            values['recoil_min_keV']=self.recoil_min_keV
            if 'n_obs_sub' in values:values['n_pe_bin']=values.pop('n_obs_sub')
        return values

    def __call__(self,exp,point,backend,ns,kernel):
        from cevns_pyeft.rates.legacy_observables import predict_legacy_observable
        if backend=='slow':
            if kernel is not None:raise ValueError('Slow does not consume a kernel')
            result=predict_legacy_observable(exp.model,point,self._settings(ns),self.profile)
        else:
            if not self.fast_allowed:raise ValueError('package Fast BLOCKED')
            kernel=self.compile(exp,ns) if kernel is None else kernel
            result=predict_profile_kernel(kernel,exp.model,point,self._settings(ns),self.profile)
        return result,{'detector':result},None,{'profile':self.profile,'input_authority':'YAML+NPZ'}

    def compile(self,exp,ns):
        if not self.fast_allowed:raise ValueError('package Fast BLOCKED')
        if digest(exp.model.describe())!=self.native_model_identity:
            raise ValueError('profile Fast does not support replaced components; use Slow or explicit compatible compiler')
        return compile_profile(exp.model,self._settings(ns),self.profile)


def definition_from_generic(data,arrays,resource_prefix=''):
    p=lambda k:_value(data,k);cfg=data['assembly'];package=data['package'];prefix=Path(resource_prefix)
    if cfg['profile']=='specification_only':raise ValueError('SPECIFICATION_ONLY package is not executable')
    profiles={backend:{key:p(ref) for key,ref in values.items()} for backend,values in cfg['numerics'].items()}
    if data['capabilities']['fast']['status'] in ('BLOCKED','NOT_APPLICABLE'):profiles.pop('fast',None)
    s=cfg['statistics'];stat=None
    if s and data['capabilities']['legacy_statistics']['status'] not in ('BLOCKED','NOT_APPLICABLE'):
        def vector(name):return tuple(arrays[s[name+'_ref']]) if name+'_ref' in s else ()
        stat=StatisticsDefinition('cevns_pyeft.experiments.package_profiles:evaluate_statistics',p(s['sigma_alpha_ref']),
            p(s['sigma_beta_ref']) if 'sigma_beta_ref' in s else None,observed=vector('observed'),background=vector('background'),
            uncertainty=vector('uncertainty'),lower=vector('lower'),upper=vector('upper'),
            kind='gaussian_one_pull' if s['model_id']=='gaussian_one_pull_legacy_v1' else 'asymmetric_irls',
            observable_unit=s['observable_unit'])
    return ExperimentDefinition(package['dataset_id'],package['experiment_slug'],package['analysis_revision'],
        (package['dataset_id'],),_physical(data),ObservationDefinition(data['observable']['name'],data['observable']['unit'],tuple(arrays[data['observable']['edges_ref']])),
        (ResourceRef('package_input',(prefix/'experiment.input.yaml').as_posix()),ResourceRef('package_arrays',(prefix/'experiment.resources.npz').as_posix())),
        profiles,ProfilePreparation(),statistics=stat,reproduction_sin2thetaW=p('interaction.sin2thetaW'),
        capabilities={'slow':cfg['profile'],'fast':'package_profile_kernel_v1','statistics':'legacy approximate'},
        validation=('tests/test_project_package_migration.py',))


def evaluate_statistics(exp,prediction):
    from cevns_pyeft.statistics.profiling import profile_gaussian_one_pull,profile_ar2020_irls
    s=exp.definition.statistics;counts=prediction.counts
    if s.observable_unit=='counts/PE':counts=counts/np.diff(exp.definition.observation.edges)
    if s.kind=='gaussian_one_pull':return profile_gaussian_one_pull(counts,s.observed,s.uncertainty,sigma_alpha=s.signal_sigma)
    return profile_ar2020_irls(counts,s.observed,s.background,s.lower,s.upper,sigma_alpha=s.signal_sigma,sigma_beta=s.background_sigma)


def _kernel_identity(model,ns,profile,keys):
    from cevns_pyeft.kernels.fingerprint import implementation_hashes
    return digest({'model':model.describe(),'ns':ns,'profile':profile,'basis':keys,
        'implementation':implementation_hashes(model),'profile_code':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def compile_profile(model,ns,profile,*,basis_keys=None):
    from cevns_pyeft.rates.legacy_observables import recoil_grid,fold_weights
    keys=tuple(model.interaction.operator_keys if basis_keys is None else basis_keys)
    source=model.source.for_run(model.run);components=source.components
    channels=tuple(model.interaction.coefficient_channels)
    full=np.zeros((len(model.targets.isotopes),len(components),len(channels),len(keys),len(keys),model.binning.shape[0]),complex)
    for ti,target in enumerate(model.targets.isotopes):
        recoil=recoil_grid(model,target,ns,profile);fold=fold_weights(model,target,recoil,ns,profile)
        for ri,t in enumerate(recoil):
            for si,c in enumerate(components):
                minimum=model.interaction.kinematics.minimum_energy_MeV(target,float(t))
                grid=np.linspace(*c.support.integration_domain_MeV,ns['n_enu']);grid=grid[(grid>=minimum)&(grid>0)]
                rate=np.zeros((len(channels),len(keys),len(keys)),complex)
                if len(grid)>=2:
                    coefficients=model.interaction.coefficient_dsigma(target=target,energy_MeV=grid,recoil_keV=float(t),basis_keys=keys)
                    rate+=np.trapezoid(coefficients*c.continuum(grid)[:,None,None,None],grid,axis=0)
                for line in c.lines:
                    if line.energy_MeV>=minimum:
                        rate+=line.fluence_per_cm2*model.interaction.coefficient_dsigma(target=target,
                            energy_MeV=np.array([line.energy_MeV]),recoil_keV=float(t),basis_keys=keys)[0]
                full[ti,si]+=rate[:,:,:,None]*fold[ri]*target.number_of_nuclei
    from cevns_pyeft.kernels.compiler import pair_templates
    from cevns_pyeft.kernels.basis import li2026_left_basis_current
    from dataclasses import asdict
    basis_lookup={b.triplet:b for b in li2026_left_basis_current()}
    basis=[basis_lookup[k] for k in keys]
    targets=[t.isotope_id for t in model.targets.isotopes]
    if targets==['Cs133','I127']:
        fractions=[t.number_of_nuclei*t.nucleus_mass_kg/model.targets.detector_mass_kg for t in model.targets.isotopes]
        full=np.stack((full[0]/fractions[0],full[1]/fractions[1],full.sum(axis=0)))
        targets.append('CsI')
    diagonal,real,imag,index=pair_templates(full)
    metadata={'profile_schema':'package_profile_kernel_v1','identity':_kernel_identity(model,ns,profile,keys),
        'basis_keys':keys,'profile':profile,'numerics':dict(ns),'dataset':model.run.run_id,
        'targets':targets,'source_flavors':[c.component_id for c in components],'channels':channels,'basis':[asdict(b) for b in basis],
        'pe_bins':model.binning.axes[0].edges.tolist(),'flavor_schema_version':1,
        'neutrino_flavor_order':['e','mu','tau'],'wilson_flavor_axis':{'row':'final','column':'initial'},
        'operator_basis_size':len(keys),'coefficient_shape':[len(keys),3,3],'lnc_lnv_interference':False,
        'full_sha256':hashlib.sha256(np.ascontiguousarray(full).tobytes()).hexdigest()}
    return {'metadata':metadata,'basis':basis,'targets':targets,'source_flavors':[c.component_id for c in components],
        'channels':channels,'full_kernel':full,'diag':diagonal,'pair_re':real,'pair_im':imag,'pair_index':index,
        'pe_bins':model.binning.axes[0].edges.copy(),'kernel_axis_kind':'channel_resolved_full_li2026'}


def predict_profile_kernel(kernel,model,point,ns,profile):
    from cevns_pyeft.kernels.compiler import reconstruct_channels
    from cevns_pyeft.contracts import Prediction
    meta=kernel['metadata'];keys=tuple(tuple(k) for k in meta['basis_keys'])
    if meta.get('profile_schema')!='package_profile_kernel_v1' or meta['identity']!=_kernel_identity(model,ns,profile,keys):
        raise ValueError('kernel identity / physical inputs / numerical settings differ; rebuild')
    if hashlib.sha256(np.ascontiguousarray(kernel['full_kernel']).tobytes()).hexdigest()!=meta['full_sha256']:
        raise ValueError('kernel content hash differs')
    source=model.source.for_run(model.run)
    rhos=np.asarray([c.fixed_state_for_fast().rho for c in source.components])
    coeff=model.interaction.coefficient_values(point,keys)
    channels=reconstruct_channels(kernel['full_kernel'],coeff,rhos)
    counts=channels.sum(axis=2)
    if kernel['targets']==['Cs133','I127','CsI']:
        fractions=[t.number_of_nuclei*t.nucleus_mass_kg/model.targets.detector_mass_kg for t in model.targets.isotopes]
        counts=np.stack((counts[0]*fractions[0],counts[1]*fractions[1]))
    scale=max(float(np.max(np.abs(counts))),np.finfo(float).tiny)
    if np.any(counts < -1e-12*scale):raise ValueError('negative Fast counts beyond roundoff')
    parts={(c.component_id,t.isotope_id):np.maximum(counts[ti,si],0) for ti,t in enumerate(model.targets.isotopes) for si,c in enumerate(source.components)}
    return Prediction(sum(parts.values(),np.zeros(model.binning.shape)),model.binning,parts,
        {'route':'package profile Fast'},model.describe(),dict(ns),{'channel_counts':channels})
