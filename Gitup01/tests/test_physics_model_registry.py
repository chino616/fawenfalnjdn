"""Exercise real model consumers, independent from the preserved candidate adapter."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest

from cevns_pyeft.experiments.model_registry import BindingSession, model_ids, resolve_model
from cevns_pyeft.contracts import TheoryPoint, IntegrationSettings
from cevns_pyeft.contracts.parameters import StateParameters

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'data/experiments/COHERENT_CsI/CsI2021'


@pytest.fixture
def inputs():
    data = json.loads((PACKAGE/'experiment.input.yaml').read_text(encoding='utf-8'))
    with np.load(PACKAGE/'experiment.resources.npz', allow_pickle=False) as stored:
        arrays = {key: stored[key] for key in stored.files}
    return data, arrays


@pytest.mark.parametrize('mid', model_ids())
def test_every_model_resolves_and_calls_a_real_consumer(mid, inputs):
    s = BindingSession(*inputs)
    binding = resolve_model(mid)
    assert binding.implementation_key and len(binding.revision) == 64
    kwargs = {}
    if mid == 'sns_michel_tabulation_legacy_v1':
        kwargs = {'resource': 'source_fluence_e'}
    elif mid == 'sns_fixed_state_v1':
        kwargs = {'component': s.data['source']['components'][2]}
    elif mid == 'nuclear_np_polynomial_v1':
        kwargs = {'isotope': 'I127'}
    elif mid in ('li2026_matching_v1', 'li2026_R_W_kernel_v1'):
        kwargs = {'isotope': 'Cs133', 'energy_GeV': .04, 'recoil_keV': 5.,
                  'left_hat': s.execute('li2026_sm_left_v1')}
    elif mid == 'csi_quenching_legacy_v1':
        kwargs = {'recoil_keV': np.array([1., 5., 15.])}
    elif mid == 'gaussian_two_pull_legacy_v1':
        kwargs = {'counts': np.arange(1., 10.)}
    elif mid == 'legacy_csi2021_v1':
        from cevns_pyeft.experiments.loader import load_experiment
        kwargs = {'model': load_experiment('CsI2021').model, 'point': TheoryPoint(),
                  'numerics': IntegrationSettings.legacy_csi2021_v1(n_er=5, n_enu=8, n_pe_bin=3, pe_step=3.)}
    result = s.execute(mid, **kwargs)
    assert result is not None
    if mid == 'sns_michel_tabulation_legacy_v1':
        assert result(np.array([20.]))[0] > 0
    elif mid == 'li2026_dsigma_v1':
        target = s.execute('csi_target_inventory_v1').isotopes[0]
        state = s.execute('sns_fixed_state_v1', component=s.data['source']['components'][0])
        energy = np.array([30., 40.])
        assert np.all(result.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=5.,
            incident_state=state(energy, parameters=StateParameters()), parameters=TheoryPoint()).values_cm2_per_keV > 0)
    elif mid == 'elastic_kinematics_v1':
        assert result.maximum_recoil_keV(s.execute('csi_target_inventory_v1').isotopes[0], 40.) > 0
    elif mid == 'legacy_csi_gamma':
        assert result.density(15., 20., target=None) > 0
    elif mid == 'csi2021_logistic_legacy':
        assert 0 < result(15.) < 1
    assert s.report()['models'][mid]['executed']
    assert not s.report()['models'][mid]['end_to_end_verified']


def test_unknown_import_and_changed_formula_rejected(inputs):
    with pytest.raises(ValueError, match='unregistered'):
        resolve_model('os.system')
    data, arrays = inputs
    data['models']['legacy_csi_gamma']['mathematical_definition'] = '__import__("os").system("bad")'
    with pytest.raises(ValueError, match='specification (differs|mismatch)'):
        BindingSession(data, arrays)


@pytest.mark.parametrize('field', ['unit', 'consumer', 'cycle', 'shape', 'axis'])
def test_bad_input_contract_is_rejected(field, inputs):
    data, arrays = inputs
    if field == 'unit':
        data['parameters']['detector.gamma_a']['unit'] = 'PE'
    elif field == 'consumer':
        data['parameters']['detector.gamma_a']['consumers'] = []
    elif field == 'cycle':
        data['models']['legacy_csi_gamma']['depends_on'].append('legacy_csi2021_v1')
    elif field == 'shape':
        arrays['nuclear_Cs133_M'] = arrays['nuclear_Cs133_M'][0]
    else:
        data['resources']['arrays']['nuclear_Cs133_M']['axes'][0]['values'] = ['n', 'p']
    with pytest.raises(ValueError):
        s = BindingSession(data, arrays)
        s.execute('nuclear_np_polynomial_v1', isotope='Cs133')


def test_antinu_kind_and_reference_only_are_preserved(inputs):
    s = BindingSession(*inputs)
    state = s.execute('sns_fixed_state_v1', component=s.data['source']['components'][2])
    assert state(np.array([30.]), parameters=StateParameters()).particle_kind == 'antinu'
    assert state.fixed_state_for_fast().particle_kind == 'antinu'
    with pytest.raises(ValueError, match='no active consumer'):
        s.value('lecs.L9')
    for pid, p in s.data['parameters'].items():
        if p['role'] not in ('reference_only', 'unused_snapshot'):
            assert p['consumers'] and all(c['model_id'] in s.bindings for c in p['consumers'])
        else:
            assert s.report()['parameters'][pid]['status'] == 'reference_only'


@pytest.mark.parametrize('key', ['quenching_q1', 'quenching_q2', 'quenching_q3', 'quenching_q4',
                                'gamma_a', 'gamma_b', 'efficiency_a', 'efficiency_b',
                                'efficiency_c', 'efficiency_d', 'acceptance_e', 'acceptance_mu', 'acceptance_mub'])
def test_detector_perturbation_changes_its_direct_intermediate(key, inputs):
    data, arrays = inputs
    original = BindingSession(data, arrays)
    changed = deepcopy(data)
    p = changed['parameters']['detector.' + key]
    p['value'] *= .99 if key == 'acceptance_mu' else 1.01
    p['adopted_value'] = p['value']
    modified = BindingSession(changed, arrays)
    def intermediate(s):
        if key.startswith('quenching'):
            return s.execute('csi_quenching_legacy_v1', recoil_keV=20.)
        if key.startswith('gamma'):
            return s.execute('legacy_csi_gamma').density(15., 20., target=None)
        if key.startswith('efficiency'):
            return s.execute('csi2021_logistic_legacy')(15.)
        label = key.removeprefix('acceptance_')
        component = next(c['component_id'] for c in data['source']['components'] if c['legacy_label'] == label)
        return s.execute('legacy_component_acceptance').acceptance(component)
    assert not np.isclose(intermediate(original), intermediate(modified), rtol=1e-9, atol=0)


def test_nuclear_adapter_preserves_i127_residual_and_zero_channel(inputs):
    from cevns_pyeft.nuclear.response import ResponseDB
    s = BindingSession(*inputs)
    legacy = ResponseDB(ROOT/'data/responses/responses_all.json')
    for isotope, key in [('Cs133', 'Cs133'), ('I127', 'I')]:
        response = s.execute('nuclear_np_polynomial_v1', isotope=isotope)
        assert 'SigmaPDelta' not in response.keys()
        for channel in response.keys():
            for y in [0., .1, 1.]:
                np.testing.assert_array_equal(response.W_np(channel, y), legacy.get(key).W_np(channel, y))
    assert s.execute('nuclear_np_polynomial_v1', isotope='I127').W_np('M', 0.)[1][1] != 74.**2


@pytest.mark.parametrize('key', ['constants.G_F', 'constants.alpha_em', 'lecs.m_N'])
def test_incompatible_engine_snapshot_is_never_silently_used(key, inputs):
    data, arrays = inputs
    data['parameters'][key]['value'] *= 1.01
    data['parameters'][key]['adopted_value'] = data['parameters'][key]['value']
    with pytest.raises(ValueError, match='snapshot'):
        BindingSession(data, arrays).execute('li2026_dsigma_v1')
