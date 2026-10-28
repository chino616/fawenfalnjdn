"""Explicit assembly and adapters for the three distinct COHERENT strategies."""
import numpy as np
from cevns_pyeft.contracts import Prediction, IntegrationSettings
from cevns_pyeft.contracts.observation import Axis, Binning


def assemble_csi2021(definition, responses):
    from cevns_pyeft.core.model import ExperimentModel
    from cevns_pyeft.contracts.source import POTExposure
    from cevns_pyeft.detectors.csi2021 import CsI2021Observation, CsIGammaResponse, CsI2021Efficiency, CsI2021EfficiencyParams
    from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
    from cevns_pyeft.sources.sns import SNSLegacySource, LEGACY_COMPONENT_IDS
    from cevns_pyeft.targets.materials import inventory_from_mass_fractions
    from cevns_pyeft.contracts.target import TargetIsotope
    from cevns_pyeft.foundation.constants import AMU_GEV
    from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction
    p, obs = definition.physical, definition.observation
    selection = LegacyComponentAcceptance({LEGACY_COMPONENT_IDS[k]:v for k,v in p.acceptance})
    observation = CsI2021Observation(selection, CsIGammaResponse(p.quenching,p.gamma_a,p.gamma_b), CsI2021Efficiency(CsI2021EfficiencyParams(*p.efficiency)))
    source = SNSLegacySource(p.run.baseline_m,p.run.yield_per_pot,p.run.energy_tabulation,p.run.node_support,p.run.num_points,p.run.interpolation)
    parts = tuple(TargetIsotope(name,a*AMU_GEV,a*p.atomic_mass_kg,0,'legacy_A_times_amu') for name,key,a in p.targets)
    inventory = inventory_from_mass_fractions(p.mass_kg,parts,[a/sum(t[2] for t in p.targets) for _,_,a in p.targets])
    return ExperimentModel(source,POTExposure(p.run.total_pot,definition.dataset_id),inventory,
        Li2026LegacyInteraction(responses,c10_mass_mode=p.c10_mass_mode),observation,
        Binning((Axis(obs.name,obs.unit,obs.edges),)),model_id='csi2021_legacy_9bin_v1')


def _csi_execute(exp, point, backend, ns, kernel):
    from cevns_pyeft.core.predict import predict
    from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
    numerics = IntegrationSettings.legacy_csi2021_v1(**ns)
    p = predict(exp.model,parameters=point,numerics=numerics,backend=backend,compiled=kernel)
    return p, {'detector':p}, None, {'strategy':numerics.strategy,'representation':'interface_kernel_v1' if backend=='fast' else 'direct'}


class CsI2021Executor:
    def __call__(self, exp, point, backend, ns, kernel):
        return _csi_execute(exp,point,backend,ns,kernel)

    def compile(self,exp,ns):
        from cevns_pyeft.kernels.compiler import compile_fast
        return compile_fast(exp.model,numerics=IntegrationSettings.legacy_csi2021_v1(**ns))


def prepare_csi2021(definition, resources):
    return assemble_csi2021(definition,resources['responses']), CsI2021Executor()


def from_legacy(definition, result, ns, physics_fingerprint):
    obs = definition.observation
    binning = Binning((Axis(obs.name,obs.unit,obs.edges),))
    parts = {(key,'material'):np.asarray(result['counts_per_bin'][key]) for key in ('mu','e','mub')}
    p = Prediction(np.asarray(result['counts_per_bin']['total']),binning,parts,
        {'route':'integrated_detector_fluence_x_nuclei','physical_settings':definition.describe()['physical']},
        {'dataset_id':definition.dataset_id,'physics_fingerprint':physics_fingerprint},ns,
        {'component_axis':'source component; material aggregated; legacy raw retained separately'})
    return p


class LegacyExecutor:
    def __init__(self, slow, builder):
        self.slow, self.builder = slow, builder

    def compile(self, exp, ns):
        result = self.builder(exp.resolved_resources['responses'], efficiency_data_path=exp.resolved_resources['efficiency'],
            definition=exp.definition,c10_mass_mode=exp.definition.physical.c10_mass_mode,**ns)
        from cevns_pyeft.kernels.storage import _basis_from_jsonable
        result['basis'] = _basis_from_jsonable(result['basis'])
        result['metadata'].update(experiment_physics_fingerprint=exp.physics_fingerprint, experiment_numerics=dict(ns),
            flavor_schema_version=1,neutrino_flavor_order=['e','mu','tau'],wilson_flavor_axis={'row':'final','column':'initial'},
            operator_basis_size=len(result['basis']),coefficient_shape=[len(result['basis']),3,3],lnc_lnv_interference=False)
        return result

    def __call__(self, exp, point, backend, ns, kernel):
        if backend == 'slow':
            if kernel is not None:
                raise ValueError('Slow does not consume a saved kernel')
            result = self.slow(exp.resolved_resources['responses'],point.wc_triplets,definition=exp.definition,
                efficiency_data_path=exp.resolved_resources['efficiency'], include_sm=point.include_sm,
                sin2thetaW=point.sin2thetaW,c10_mass_mode=exp.definition.physical.c10_mass_mode,**ns)
        else:
            from cevns_pyeft.kernels.basis import coeff_tensor_from_triplets
            from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel
            kernel = self.compile(exp,ns) if kernel is None else kernel
            meta = kernel['metadata']
            if meta.get('dataset') != exp.dataset_id or meta.get('experiment_physics_fingerprint') != exp.physics_fingerprint or meta.get('experiment_numerics') != dict(ns):
                raise ValueError('legacy kernel identity / physical inputs / numerical settings differ; rebuild')
            if not np.array_equal(kernel['pe_bins'],exp.definition.observation.edges):
                raise ValueError('legacy kernel binning mismatch')
            result = reconstruct_counts_from_kernel(kernel,coeff_tensor_from_triplets(kernel['basis'],point.wc_triplets,
                include_sm=point.include_sm,sin2thetaW=point.sin2thetaW))
        p = from_legacy(exp.definition,result,ns,exp.physics_fingerprint)
        return p, {'detector':p}, result, {'strategy':exp.definition.capabilities[backend], 'cache_status':'legacy_compat; new instance binding required'}


def prepare_csi2017(definition,resources):
    _validate_legacy_axis(definition)
    from .slow_counts_csi2017 import slow_counts_csi2017
    from .fast_kernel_csi2017 import build_fast_kernel_csi2017
    return definition.physical, LegacyExecutor(slow_counts_csi2017,build_fast_kernel_csi2017)


def prepare_ar2020(definition,resources):
    _validate_legacy_axis(definition)
    from .slow_counts_ar2020 import slow_counts_ar2020
    from .fast_kernel_ar2020 import build_fast_kernel_ar2020
    return definition.physical, LegacyExecutor(slow_counts_ar2020,build_fast_kernel_ar2020)


def _validate_legacy_axis(definition):
    obs=definition.observation
    if (obs.name,obs.unit,obs.detector_ids)!=('reconstructed PE spectrum','PE',('detector',)):
        raise ValueError('legacy COHERENT executor requires its PE axis and single detector; add an explicit observable conversion for other units')
