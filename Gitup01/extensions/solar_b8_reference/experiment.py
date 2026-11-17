"""Scoped PreparedExperiment adapters: old reference recipe, actual core Runtime."""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from cevns_pyeft.contracts import TargetIsotope,TheoryPoint,Axis,Binning
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.definition import ExperimentDefinition,ObservationDefinition,ResourceRef,plain
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction
from cevns_pyeft.foundation.constants import AMU_GEV
from .inputs import ROOT,INPUT,SAMPLES,read_card,sha,verified_table,FixedFlavorSource,ReferenceAcceptance
from .physics import ReferenceKernel,slow_flavors,compile_reference

DEPENDENCIES=('extensions.solar_b8_reference.inputs','extensions.solar_b8_reference.physics','extensions.solar_b8_reference.experiment',
    'cevns_pyeft.rates.differential','cevns_pyeft.theory.li2026.adapter','cevns_pyeft.theory.li2026.coefficients',
    'cevns_pyeft.theory.li2026.flavor','cevns_pyeft.theory.li2026.left_to_ci','cevns_pyeft.theory.li2026.lec',
    'cevns_pyeft.theory.li2026.responses','cevns_pyeft.theory.li2026.amplitude','cevns_pyeft.theory.li2026.cross_section',
    'cevns_pyeft.nuclear.response','cevns_pyeft.foundation.constants')


@dataclass(frozen=True)
class Settings:
    sample:str
    input_sha256:str
    implementation_modules:tuple=DEPENDENCIES


@dataclass(frozen=True)
class ReferenceModel:
    sample:str
    physics:object
    source:FixedFlavorSource
    observation:ReferenceAcceptance
    target:TargetIsotope
    interaction:object
    exposure_tyr:float

    def describe(self):
        return {'recipe':'solar_reference_v1','sample':self.sample,'physics':plain(self.physics),
            'source':self.source.describe(),'observation':self.observation.describe(),'target':plain(self.target),
            'interaction':self.interaction.describe().as_dict(),'exposure_tyr':self.exposure_tyr,
            'statistics':'joint shared pull; cannot sum independent per-sample profilers'}


@dataclass(frozen=True)
class Preparation:
    def __call__(self,definition,resources):
        card=read_card(resources['input']);sample=definition.physical.sample
        if sha(resources['input'])!=definition.physical.input_sha256:raise ValueError('reference card changed')
        p=card['physics'];s=card['samples'][sample]
        if sha(resources['nuclear'])!=p['nuclear_sha256']:raise ValueError('reference nuclear table changed')
        source=FixedFlavorSource(verified_table(resources['source'],card,'b8_source.txt'),
            verified_table(resources['probabilities'],card,'flavor_probabilities.txt'),p)
        detector=ReferenceAcceptance(verified_table(resources['efficiency'],card,s['efficiency']),tuple(s['T_bounds_keVnr']),
            s['energy_guard_gt_keVnr'],s['enforce_table_domain'],p['acceptance_minimum_exclusive'],p['acceptance_interpolation_order'])
        target=TargetIsotope('Xe131',p['A']*AMU_GEV,p['A']*p['kg_per_A_u'],p['kg_per_tonne']/(p['A']*p['kg_per_A_u']),
            'reference nucleus inventory A*1.66054e-27kg; shared amplitude A*amu')
        interaction=Li2026LegacyInteraction(resources['nuclear'],{'Xe131':'Xe131'})
        return ReferenceModel(sample,p,source,detector,target,interaction,s['exposure_tyr']),Executor(p['sin2thetaW'])


@dataclass(frozen=True)
class Executor:
    weak_angle:float

    def default_point(self):return TheoryPoint(sin2thetaW=self.weak_angle)

    def describe_execution(self,model):
        return {'algorithm':'reference source/acceptance and shared nuclear full trace',
            'slow':'actual3x3K then validatedTr(rho K) at every E,T',
            'fast':'same fixed source integrated signed4x4Wilson bilinear by flavor','weak_angle':self.weak_angle}

    def compile(self,experiment,numerics):return compile_reference(experiment,numerics)

    def __call__(self,experiment,point,backend,numerics,kernel):
        model=experiment.model
        if backend=='slow':
            if kernel is not None:raise ValueError('Slow must not consume preintegrated kernel')
            values,diagnostics=slow_flavors(model,point,numerics)
        elif backend=='fast' and isinstance(kernel,ReferenceKernel):
            kernel.validate(experiment,numerics);values=kernel.flavors(model,point)
            diagnostics={'contraction':'flavor-resolved signed nuclear bilinear; fixed-state exact representation'}
        else:raise ValueError('explicit Slow or matching reference Fast kernel required')
        counts=np.array([float(sum(values))])
        binning=Binning((Axis('fitted_signal_total','dimensionless',(0.,1.)),))
        pred=Prediction(counts,binning,{('solar_B8','Xe131'):counts},
            {'total_flux':model.physics['flux_cm2_s'],'exposure_tyr':model.exposure_tyr,'normalization_applied_once':True},
            model.describe(),numerics,{**diagnostics,'events_by_flavor':dict(zip(['e','mu','tau'],values.tolist()))})
        return pred,{model.sample:pred},None,{'reference_recipe':True,'backend':backend}


def load_reference(sample,*,root=ROOT,input_directory=None):
    if sample not in SAMPLES:raise ValueError('select paired,US2,xenon explicitly')
    root=Path(root).resolve();directory=Path(input_directory or root/'data/benchmarks/solar_b8_reference_2601_19883').resolve()
    cardpath=directory/'analysis.input.json';card=read_card(cardpath);s=card['samples'][sample]
    dataset='SolarB8_'+sample+'__reference_recipe_v1'
    refs=(ResourceRef('input',str(cardpath),semantic='explicit reference choices and provenance'),
        ResourceRef('source',str(directory/'b8_source.txt'),semantic='adopted829-pointshape'),
        ResourceRef('probabilities',str(directory/'flavor_probabilities.txt'),semantic='fixed10-nodeflavorprobabilities'),
        ResourceRef('efficiency',str(directory/s['efficiency']),semantic='legacy total acceptance,1%cut'),
        ResourceRef('nuclear',str(root/card['physics']['nuclear_resource']),semantic='shared original nuclear Response'))
    definition=ExperimentDefinition(dataset,'SolarB8_reference','reference_v1',(sample,),Settings(sample,sha(cardpath)),
        ObservationDefinition('fitted_signal_total','dimensionless',(0.,1.),(sample,)),refs,
        {'slow':dict(card['numerics']),'fast':dict(card['numerics'])},Preparation(),
        reproduction_sin2thetaW=card['physics']['sin2thetaW'],
        capabilities={'analysis':'local_reference_recipe','statistics':'joint_only_shared_alpha','source':'fixed_reference_flavor_flux',
            'slow':'actual full Tr(rho K)','fast':'signed bilinear independently checked againstSlow'},
        validation=('tests/test_solar_b8_reference.py',))
    catalog=ExperimentCatalog(builtins=False).register(dataset,definition)
    return load_experiment(dataset,definition=definition,registry=catalog,resources=ResourceCatalog(root))

