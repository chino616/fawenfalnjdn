"""Versioned physics bindings. All executable dispatch is explicit project code.

Formula strings, source locators and YAML implementation hints are audit data.
Consumption is observed in a BindingSession, never taken from an input flag.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import numpy as np

from .input_package import fingerprint, schema_document, validate_document


@dataclass(frozen=True)
class ModelBinding:
    model_id: str
    version: str
    category: str
    implementation_key: str
    input_schema: dict
    output_schema: dict
    dependencies: tuple
    capability_support: tuple
    numerical_behavior: str
    test_references: tuple
    revision: str
    state: str = 'BOUND_AND_TESTED'


def specification_fingerprint(model):
    return fingerprint({key: model[key] for key in ('mathematical_definition', 'variables', 'depends_on')})


def _contracts():
    return json.loads(Path(__file__).with_name('model_bindings.json').read_text(encoding='utf-8'))


def resolve_model(model_id):
    if model_id not in _IMPLEMENTATIONS:
        raise ValueError('unregistered physics model: ' + str(model_id))
    contract = _contracts()[model_id]
    fn = _IMPLEMENTATIONS[model_id]
    modules = (Path(__file__), Path(__file__).with_name('package_components.py'))
    dependencies = _engine_files(model_id)
    revision = fingerprint({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (*modules, *dependencies)})
    return ModelBinding(model_id, '1', contract['category'], fn.__name__,
        {'parameters': contract['parameter_units'], 'resources': contract['resource_units']},
        {'unit': contract['output_unit'], 'variables': contract['variable_units']},
        tuple(contract['depends_on']), tuple(contract['capabilities']), contract['numerical_behavior'],
        ('tests/test_physics_model_registry.py',), revision)


def _engine_files(mid):
    # These are the same implementation files previously found by importing
    # functions. Code-owned paths preserve lazy catalog/binding descriptions;
    # no path or callable from YAML is used for import dispatch.
    paths={
        'li2026_matching_v1': ('theory/li2026/left_to_ci.py',),
        'li2026_R_W_kernel_v1': ('theory/li2026/amplitude.py',),
        'li2026_dsigma_v1': ('rates/differential.py','theory/li2026/amplitude.py'),
        'li2026_sm_left_v1': ('rates/differential.py',),
        'nuclear_np_polynomial_v1': ('nuclear/response.py',),
        'csi_quenching_legacy_v1': ('rates/differential.py',),
        'legacy_csi_gamma': ('rates/differential.py',),
        'csi2021_logistic_legacy': ('detectors/csi2021.py',),
        'legacy_csi2021_v1': ('core/predict.py',),
        'gaussian_two_pull_legacy_v1': ('statistics/profiling.py',)}
    root=Path(__file__).resolve().parents[1]
    return tuple(root/path for path in paths.get(mid,()))


class BindingSession:
    def __init__(self, data, arrays):
        errors = validate_document(data)
        if errors:
            raise ValueError('; '.join(errors))
        self.data, self.arrays = data, arrays
        self.reads, self.resource_reads, self.executed = set(), set(), set()
        self.bindings = {}
        contracts = _contracts()
        for mid, model in data['models'].items():
            binding = resolve_model(mid)
            if specification_fingerprint(model) != contracts[mid]['specification_fingerprint']:
                raise ValueError('model specification differs from registered version: ' + mid)
            self.bindings[mid] = binding
        for key, meta in data['resources']['arrays'].items():
            value = arrays.get(key)
            if value is None or list(value.shape) != meta['shape'] or str(value.dtype) != meta['dtype']:
                raise ValueError('binding resource shape/dtype: ' + key)
            if not np.all(np.isfinite(value)):
                raise ValueError('non-finite binding array: ' + key)

    def value(self, key):
        p = self.data['parameters'][key]
        if p['role'] in ('reference_only', 'unused_snapshot'):
            raise ValueError('parameter has no active consumer: ' + key)
        self.reads.add(key)
        return p['value']

    def slot(self, mid, slot, *, subject=None):
        matches = [pid for pid, p in self.data['parameters'].items()
                   if any(c['model_id'] == mid and c['slot'] == slot for c in p['consumers'])
                   and (subject is None or '.' + subject + '.' in pid)]
        if len(matches) != 1:
            raise ValueError(f'parameter mapping must resolve once: {mid}.{slot}/{subject}: {matches}')
        return self.value(matches[0])

    def array(self, key):
        if key not in self.data['resources']['arrays']:
            raise ValueError('undeclared package array: ' + key)
        self.resource_reads.add(key)
        return self.arrays[key]

    def execute(self, mid, **kwargs):
        resolve_model(mid)
        if mid not in self.bindings:
            raise ValueError('model absent from package: ' + mid)
        result = _IMPLEMENTATIONS[mid](self, **kwargs)
        self.executed.add(mid)
        return result

    def report(self):
        inactive = ('reference_only', 'unused_snapshot')
        return {
            'models': {mid: {'state': b.state, 'bound': True, 'executed': mid in self.executed,
                             'revision': b.revision, 'end_to_end_verified': False} for mid, b in self.bindings.items()},
            'parameters': {pid: {'specified': True, 'bound': p['role'] not in inactive,
                'read_by_adapter': pid in self.reads,
                'status': 'reference_only' if p['role'] in inactive else ('executed' if pid in self.reads else 'bound'),
                'consumer_models': [c['model_id'] for c in p['consumers']],
                'stale': False, 'end_to_end_verified': False} for pid, p in self.data['parameters'].items()},
            'resource_reads': sorted(self.resource_reads),
            'scope': 'adapter execution only; end-to-end evidence is produced by regression/standalone tools'}


def _fluence(s):
    from .input_package import derived_value
    return derived_value('spherical_fluence.v1', [s.value(k) for k in
        ('source.total_pot', 'source.yield_per_pot', 'source.baseline_m')])


def _continuum(s, *, resource):
    from .package_components import ArrayContinuum
    meta = s.data['resources']['arrays'][resource]
    if meta['normalization']['runtime_factors']:
        raise ValueError('materialized continuum cannot be normalized twice')
    return ArrayContinuum(s.array('source_energy_MeV'), s.array(resource))


def _line(s):
    from cevns_pyeft.contracts.source import FluenceLine
    return FluenceLine('pion_DAR', s.slot('sns_prompt_line_v1', 'energy'), s.slot('sns_prompt_line_v1', 'fluence'))


def _state(s, *, component):
    from .package_components import ArrayState
    return ArrayState(s.array(component['rho_ref']), component['particle_kind'])


def _targets(s):
    from cevns_pyeft.contracts.target import TargetInventory, TargetIsotope
    parts = tuple(TargetIsotope(i, s.value(f'target.{i}.mass_GeV'), s.value(f'target.{i}.mass_kg'),
                               s.value(f'target.{i}.nuclei'), 'legacy_A_times_amu') for i in s.data['target']['isotope_order'])
    return TargetInventory(parts, s.value('target.detector_mass'),
                           {'authority': 'validated derived nuclei; no second inventory normalization'})


def _sm(s, *, point=None):
    from cevns_pyeft.rates.differential import _sm_left_dim6
    from .package_components import check_engine_snapshot
    check_engine_snapshot(s.data)
    include = s.value('interaction.include_sm') if point is None else point.include_sm
    angle = s.value('interaction.sin2thetaW') if point is None else point.sin2thetaW
    s.value('constants.G_F')
    return _sm_left_dim6(include, angle)


def _matching(s, *, left_hat, energy_GeV, recoil_keV, isotope):
    from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
    from cevns_pyeft.theory.li2026.lec import Li2026LECs
    from .package_components import check_engine_snapshot
    check_engine_snapshot(s.data)
    values = {key[5:]: s.value(key) for key, p in s.data['parameters'].items()
              if key.startswith('lecs.') and p['role'] not in ('reference_only', 'unused_snapshot')}
    lecs = Li2026LECs(**values)
    mass = s.value(f'target.{isotope}.mass_GeV')
    t = recoil_keV * 1e-6
    return left_to_ci(left_hat, E_nu=energy_GeV, q0=t, q2=t*t-2*mass*t,
                      qabs2=2*mass*t, qabs=np.sqrt(2*mass*t), mA=mass,
                      c10_mass_mode=s.data['interaction']['c10_mass_mode'], lecs=lecs)


def _kinematics(s):
    from cevns_pyeft.contracts.interaction import ElasticKinematics
    return ElasticKinematics()


def _response(s, *, isotope):
    from .package_components import response_from_arrays
    for key in s.arrays:
        if key.startswith('nuclear_' + isotope + '_'):
            s.array(key)
    s.value(f'target.{isotope}.b')
    s.value(f'nuclear.{isotope}.exp_factor')
    return response_from_arrays(s.data, s.arrays, isotope)


def _kernel(s, *, isotope, energy_GeV, recoil_keV, left_hat):
    from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
    from .package_components import check_engine_snapshot
    check_engine_snapshot(s.data)
    s.value('lecs.m_N')
    return flavor_kernel_onebody_li2026(_response(s, isotope=isotope), E_nu_GeV=energy_GeV,
        ER_keV=recoil_keV, left_hat=left_hat, basis='np', c10_mass_mode=s.data['interaction']['c10_mass_mode'])


def _interaction(s):
    from .package_components import ArrayInteraction, check_engine_snapshot
    check_engine_snapshot(s.data)
    values = {key: s.value(key) for key, p in s.data['parameters'].items()
              if (key.startswith('constants.') or key.startswith('lecs.'))
              and p['role'] not in ('reference_only', 'unused_snapshot')}
    return ArrayInteraction({i: _response(s, isotope=i) for i in s.data['target']['isotope_order']},
                            s.data['interaction']['c10_mass_mode'], values)


def _quenching(s, *, recoil_keV):
    from cevns_pyeft.rates.differential import eee_quenching_csi
    return eee_quenching_csi(recoil_keV, quenching=tuple(s.slot('csi_quenching_legacy_v1', f'q{i}') for i in range(1, 5)))


def _gamma(s):
    from cevns_pyeft.detectors.csi2021 import CsIGammaResponse
    return CsIGammaResponse(tuple(s.slot('csi_quenching_legacy_v1', f'q{i}') for i in range(1, 5)),
                           s.slot('legacy_csi_gamma', 'a0'), s.slot('legacy_csi_gamma', 'b0'))


def _efficiency(s):
    from cevns_pyeft.detectors.csi2021 import CsI2021Efficiency, CsI2021EfficiencyParams
    return CsI2021Efficiency(CsI2021EfficiencyParams(*(s.slot('csi2021_logistic_legacy', k) for k in 'abcd')))


def _acceptance(s):
    from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
    return LegacyComponentAcceptance({c['component_id']: s.slot('legacy_component_acceptance', c['legacy_label'])
                                      for c in s.data['source']['components']})


def _prediction(s, *, model, point, numerics, backend='slow', compiled=None):
    from cevns_pyeft.core.predict import predict
    return predict(model, parameters=point, numerics=numerics, backend=backend, compiled=compiled)


def _statistics(s, *, counts):
    from cevns_pyeft.statistics.profiling import profile_gaussian_two_pull
    stat = s.data['statistics']
    widths = np.diff(s.array(s.data['observable']['edges_ref']))
    signal = np.asarray(counts) / widths
    if signal.shape != widths.shape:
        raise ValueError('statistics/prediction bin shape mismatch')
    sigma = np.maximum(s.array(stat['uncertainty_ref']), s.value('statistics.sigma_floor'))
    return profile_gaussian_two_pull(signal, s.array(stat['observed_ref']), s.array(stat['background_ref']), sigma,
        sigma_alpha=s.value('statistics.sigma_alpha'), sigma_beta=s.value('statistics.sigma_beta'))


_IMPLEMENTATIONS = {
    'sns_fluence_legacy_v1': _fluence, 'sns_michel_tabulation_legacy_v1': _continuum,
    'sns_prompt_line_v1': _line, 'sns_fixed_state_v1': _state, 'csi_target_inventory_v1': _targets,
    'li2026_sm_left_v1': _sm, 'li2026_matching_v1': _matching, 'elastic_kinematics_v1': _kinematics,
    'nuclear_np_polynomial_v1': _response, 'li2026_R_W_kernel_v1': _kernel, 'li2026_dsigma_v1': _interaction,
    'csi_quenching_legacy_v1': _quenching, 'legacy_csi_gamma': _gamma, 'csi2021_logistic_legacy': _efficiency,
    'legacy_component_acceptance': _acceptance, 'legacy_csi2021_v1': _prediction,
    'gaussian_two_pull_legacy_v1': _statistics,
}


def model_ids():
    return tuple(_IMPLEMENTATIONS)
