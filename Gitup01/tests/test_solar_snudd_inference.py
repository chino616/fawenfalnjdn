"""Full inference: upstream-rho equivalence, joint profiling and saved surfaces.

Run after the explicit full benchmark. No fitting to the paper reference, no
mutable legacy reference arrays, no installation, and no new source packages.
"""
import json
import shutil
import sys
import numpy as np
import pytest
from scipy.optimize import minimize
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from extensions.solar_rho_snudd.experiment import load_snudd
from extensions.solar_rho_snudd.protocol import ROOT, read
from extensions.solar_rho_snudd.scan import ScanSource, ScanJoint

OUT = ROOT / 'outputs/external/solar_rho_snudd/20261112_fig4_run2'


@pytest.fixture(scope='module')
def inference():
    record = read(OUT / 'NSI_RESULTS.json')
    experiments, kernels, shared = [], [], None
    for sample in record['sample_order']:
        e = load_snudd(sample, cache_root=OUT / 'validation_cache', interaction=shared)
        shared = e.model.interaction
        experiments.append(e)
        kernels.append(SolarNSIKernel.load(OUT / 'kernels' / (sample+'.npz')))
    model = ScanJoint(tuple(experiments), tuple(kernels), ScanSource(OUT / 'propagation_source'))
    return record, model


@pytest.mark.parametrize('index', range(5))
def test_exact_source_and_runtime_at_actual_benchmark_points(inference, index):
    record, model = inference
    row = record['direct_Runtime_validation'][index]
    u, d = row['point']
    full = model.runtime_state.full_rho(model.energy, u, d)
    assert np.max(abs(full-model.state.rho(model.energy, u, d))) < 5e-12
    assert np.allclose(model.state.pee(model.energy, u, d), full[:, 0, 0].real, atol=5e-12, rtol=0)
    chis, signals = [], []
    for e, k in zip(model.experiments, model.kernels):
        p = predict_experiment(e, parameters=nsi_point(u, d), backend='fast', kernel=k, numerics=k.record['numerics'])
        signals.append(p.counts[0])
        chis.append(evaluate_experiment(e, p).chi2)
    assert np.allclose(signals, model.signals(u, d), atol=1e-9, rtol=0)
    assert abs(sum(chis)-model.chi2(u, d)) < 1e-10


def test_profile_matches_independent_three_nuisance_optimization(inference):
    _, model = inference
    for u, d in [(0., 0.), (0., .178), (.3, -.1)]:
        signal = model.signals(u, d)
        def chi(alpha):
            return np.sum(((model.D-(1+alpha)*signal)/model.sigma)**2+(alpha/model.pull)**2)
        result = minimize(chi, np.zeros(3), method='BFGS', options={'gtol': 1e-8})
        assert abs(result.fun-model.chi2(u, d)) < 1e-10
        assert np.allclose(result.x, model.detail(u, d)['alpha'], atol=1e-7, rtol=0)


def test_source_hash_and_original_grid_are_enforced(inference, tmp_path):
    _, model = inference
    assert len(model.state.arrays['radial_weights']) == 1000
    assert sum(model.state.active) == 485  # skip only strictly zero weights
    assert abs(model.state.arrays['radial_weights'].sum()-1) < 1e-13
    with pytest.raises(ValueError, match='fixed'):
        model.state.pee([5.], radial_order=16)
    destination = tmp_path / 'source'
    shutil.copytree(OUT / 'propagation_source', destination)
    manifest = read(destination / 'manifest.json')
    manifest['input_card_sha256'] = '0'*64
    (destination / 'manifest.json').write_text(json.dumps(manifest), encoding='utf8')
    with pytest.raises(ValueError, match='stale/corrupt/wrong-source'):
        ScanSource(destination)


def test_no_energy_interpolation_and_fixed_sm_control(inference):
    _, model = inference
    energy = np.array([.72103456789, 5.14285714285, 13.0000000003])
    full = model.state.rho(energy, .3, -.1)
    assert full.shape == (3, 3, 3)
    assert np.allclose(np.trace(full, axis1=-2, axis2=-1), 1., atol=1e-13)
    assert np.linalg.eigvalsh(full).min() >= -1e-13
    fixed = ScanSource(OUT / 'propagation_source', fixed_sm=True)
    assert np.array_equal(fixed.pee(energy, .3, -.1), model.state.pee(energy, 0., 0.))
    assert np.max(abs(fixed.pee(energy)-model.state.pee(energy, .3, -.1))) > .01
    assert not any(k == 'snudd' or k.startswith('snudd.') for k in sys.modules)


def test_global_minimum_is_not_sm_or_plot_window_minimum(inference):
    record, model = inference
    best = record['primary_minimum']['minimum']
    assert best['chi2'] == pytest.approx(model.chi2(best['epsilon_ee_uV'], best['epsilon_ee_dV']), abs=1e-12)
    assert best['chi2'] < record['SM']['chi2']
    assert record['plot_window_grid_minimum']['chi2'] > best['chi2']
    assert abs(best['epsilon_ee_uV']) > 1
    assert record['primary_minimum']['independent_seed_spread'] < 1e-8
    assert len(record['primary_minimum']['searches']) >= 4
    assert record['scientific_acceptance'] == 'NOT_REVIEWED'


@pytest.mark.parametrize('mode', ['flat_sensitivity', 'zero', 'unit', 'profile_bounds', 'fixed_SM_propagation'])
def test_saved_601_squared_surfaces_match_points_and_own_minimum(inference, mode):
    record, model = inference
    if mode == 'fixed_SM_propagation':
        model = ScanJoint(model.experiments, model.kernels, ScanSource(OUT / 'propagation_source', fixed_sm=True))
    minimums = read(OUT / 'MINIMUMS.json')
    with np.load(OUT / 'solar_NSI_surfaces.npz', allow_pickle=False) as a:
        assert a['delta_chi2_'+mode].shape == (601, 601)
        assert np.allclose(a['raw_chi2_'+mode]-minimums[mode]['minimum']['chi2'], a['delta_chi2_'+mode], atol=0, rtol=0)
        for row, col in [(300, 300), (431, 273), (2, 599)]:
            u, d = a['epsilon_ee_uV'][col], a['epsilon_ee_dV'][row]
            value = model.chi2(u, d) if mode == 'fixed_SM_propagation' else model.chi2(u, d, mode)
            assert value == pytest.approx(a['raw_chi2_'+mode][row, col], rel=1e-11, abs=1e-11)
        if mode == 'flat_sensitivity':
            assert np.array_equal(a['calculated_primary_allowed_mask'], a['delta_chi2_'+mode] <= 4.61)


def test_saved_crossings_are_actual_delta_chi2_roots(inference):
    record, model = inference
    minimum = record['primary_minimum']['minimum']['chi2']
    for row in read(OUT / 'SLICE_BOUNDARIES.json'):
        for d in row['flat_sensitivity']:
            assert float(model.chi2(row['epsilon_ee_uV'], d)-minimum) == pytest.approx(4.61, abs=1e-8)


def test_unchanged_sm_and_frozen_fold_arrays(inference):
    record, model = inference
    old = read(ROOT / 'outputs/external/solar_rho_snudd/20261112_run1/RESULTS.json')
    assert record['SM']['signal_events'] == old['points'][0]['snudd']['signal_events']
    for sample, kernel in zip(record['sample_order'], model.kernels):
        previous = SolarNSIKernel.load(ROOT / 'outputs/external/solar_rho_snudd/20261112_run1/kernels' / (sample+'.npz'))
        assert np.array_equal(kernel.values, previous.values)
        assert kernel.record['fold_dependency_digest'] == previous.record['fold_dependency_digest']


def test_paper_discrepancy_is_preserved_not_marked_as_exact_reproduction(inference):
    record, _ = inference
    comparison = record['paper_comparison']
    assert comparison['paper_is_reference_only']
    assert 0 < comparison['intersection_over_union'] < .99
    assert comparison['counterexample']['paper_membership'] is False
    assert comparison['counterexample']['delta_chi2'] < 4.61
    assert 'EXACT_PAPER_REPRODUCTION_NOT_ESTABLISHED' in record['status']
