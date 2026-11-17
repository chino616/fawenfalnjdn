"""Actual optional-source integration tests; pinned external installation required.

Run after the explicit benchmark. Tests consume actual rho/Slow outputs; they
never install packages, mutate pinned originals or replace legacy references.
"""
from pathlib import Path
from dataclasses import replace
import json
import shutil
import sys
import numpy as np
import pytest
from cevns_pyeft.contracts import IncidentStateBatch
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment, validate_snapshot
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from extensions.solar_rho_snudd.experiment import load_snudd
from extensions.solar_rho_snudd.protocol import ROOT, CARD, PIN, read, identity, packet_key, load_packet, validate_rho, sha
from extensions.solar_rho_snudd.export_rho import model_parameters

OUT = ROOT / 'outputs/external/solar_rho_snudd/20261112_run1'


@pytest.fixture(scope='module')
def prepared():
    if not (OUT / 'RESULTS.json').exists():
        pytest.fail('run the authorized external benchmark before its integration tests')
    record = read(OUT / 'RESULTS.json')
    energy = np.array(read(OUT / 'ENERGY_CONTRACT.json')['E_MeV'])
    oldids = BUILTIN_CATALOG.ids()
    experiments = []
    shared = None
    for sample in record['sample_order']:
        e = load_snudd(sample, cache_root=OUT / 'rho_cache', interaction=shared)
        shared = e.model.interaction
        e.model.state_model.prefetch(energy, [p['point'] for p in record['points']])
        k = SolarNSIKernel.load(OUT / 'kernels' / (sample+'.npz'))
        experiments.append((e, k))
    assert BUILTIN_CATALOG.ids() == oldids
    return record, energy, experiments


@pytest.mark.parametrize('u,d', [(0., 0.), (.3, -.1), (-.4, .6), (0., .178), (-17.2630015148, 15.6767532884)])
def test_quark_nucleon_mapping_has_correct_sign_and_scale(u, d):
    matrix, eta, phi = model_parameters(u, d)
    scale = matrix[0, 0]
    p, n = scale*np.sqrt(5)*np.cos(eta)*np.cos(phi), scale*np.sqrt(5)*np.sin(eta)
    assert np.allclose([p, n], [2*u+d, u+2*d], rtol=1e-13, atol=1e-13)
    assert phi == 0 and np.array_equal(matrix[1:], np.zeros((2, 3)))


def test_actual_installed_content_and_parameter_selection():
    c = read(CARD)
    assert c['commit'] == PIN
    assert c['oscillation_actual_GeV_rad']['theta_12'] == .583638
    assert c['oscillation_actual_GeV_rad']['delta_m12'] == 7.42e-5*1e-18
    for name, expected in c['upstream_files'].items():
        assert sha(ROOT / '.externals/SNuDD' / name) == expected
    assert c['production_file']['shape'] == [96, 2]


def test_complete_external_rho_preserved_and_host_isolated(prepared):
    _, energy, exps = prepared
    e, _ = exps[0]
    full = e.model.state_model.full_rho(energy, .3, -.1)
    assert full.shape == (len(energy), 3, 3)
    assert np.allclose(full, full.conj().swapaxes(-1, -2), atol=1e-13)
    assert np.allclose(np.trace(full, axis1=-2, axis2=-1), 1., atol=1e-13)
    assert np.min(np.linalg.eigvalsh(full)) > -1e-13
    off = full.copy()
    off[:, np.arange(3), np.arange(3)] = 0
    assert np.max(abs(off)) > .01  # genuine full flavor matrices, not invented diagonal data
    assert not any(k == 'snudd' or k.startswith('snudd.') for k in sys.modules)


def test_exact_energy_subsets_and_projection(prepared):
    _, energy, exps = prepared
    e, _ = exps[0]
    subset = energy[::17]
    full = e.model.state_model.full_rho(energy, .3, -.1)
    state = e.model.state_model(subset, parameters=nsi_point(.3, -.1).state)
    assert np.array_equal(state.rho[:, 0, 0].real, full[::17, 0, 0].real)
    assert np.allclose(np.trace(state.rho, axis1=-2, axis2=-1), 1.)
    with pytest.raises(ValueError, match='radial'):
        e.model.state_model.pee(subset, radial_order=16)


def test_full_density_and_ee_projection_give_same_shared_amplitude(prepared):
    _, _, exps = prepared
    e, _ = exps[0]
    energy = np.array([5., 10.])
    full = e.model.state_model.full_rho(energy, .3, -.1)
    target = e.model.targets.isotopes[3]
    p = nsi_point(.3, -.1)
    reference = e.model.interaction._legacy.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=.5,
        incident_state=IncidentStateBatch(energy, full, 'nu', 'actual_external_full_rho'), parameters=p)
    projected = e.model.interaction.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=.5,
        incident_state=e.model.state_model(energy, parameters=p.state), parameters=p)
    assert np.allclose(reference.values_cm2_per_keV, projected.values_cm2_per_keV, rtol=1e-11, atol=0)


def test_old_cache_rejected_and_new_model_fully_bound(prepared):
    _, _, exps = prepared
    e, k = exps[1]
    old = SolarNSIKernel.load(ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run2/kernels/PandaX_US2.npz')
    assert np.array_equal(k.values, old.values)
    with pytest.raises(ValueError, match='stale/wrong'):
        predict_experiment(e, parameters=nsi_point(), backend='fast', kernel=old, numerics=old.record['numerics'])
    with pytest.raises(ValueError, match='execution inputs changed'):
        validate_snapshot(replace(e, model=replace(e.model, exposure_tyr=2*e.model.exposure_tyr)))


def test_real_slow_fast_components_statistics_and_sm_invariance(prepared):
    record, _, exps = prepared
    assert record['SM_counts_bitwise_unchanged']
    for row in read(OUT / 'FORWARD_VALIDATION.json'):
        assert row['old_and_new_fold_arrays_bitwise_identical']
        for point in row['direct_slow_checks']:
            assert np.all(np.array(point['difference']) <= point['tolerance'])
    chi = 0.
    for (e, k), expected in zip(exps, record['points'][1]['snudd']['signal_events']):
        p = predict_experiment(e, parameters=nsi_point(.3, -.1), backend='fast', kernel=k, numerics=k.record['numerics'])
        assert p.counts[0] == pytest.approx(expected, rel=1e-13)
        assert sum(v[0] for v in p.combined_prediction.components.values()) == pytest.approx(expected, rel=1e-13)
        chi += evaluate_experiment(e, p).chi2
    assert chi == pytest.approx(record['points'][1]['snudd']['chi2'], abs=1e-12)


def test_packets_reject_wrong_coordinates_couplings_or_corruption(prepared, tmp_path):
    _, energy, _ = prepared
    expected = identity(energy, .3, -.1, sha(CARD))
    original = OUT / 'rho_cache' / packet_key(expected)
    with pytest.raises(ValueError, match='wrong NSI/energy'):
        load_packet(original, identity(energy[::2], .3, -.1, sha(CARD)))
    with pytest.raises(ValueError, match='wrong NSI/energy'):
        load_packet(original, identity(energy, -.3, -.1, sha(CARD)))
    destination = tmp_path / 'damaged_packet'
    shutil.copytree(original, destination)
    with np.load(destination / 'rho.npz', allow_pickle=False) as a:
        values = {k: a[k].copy() for k in a.files}
    values['rho_flavour'][0, 0, 0] += .01
    np.savez_compressed(destination / 'rho.npz', **values)
    with pytest.raises(ValueError, match='corrupt'):
        load_packet(destination, expected)


def test_unphysical_states_and_nonfinite_inputs_rejected():
    with pytest.raises(ValueError, match='trace-one'):
        validate_rho([1.], np.zeros((1, 3, 3)))
    with pytest.raises(ValueError, match='PSD'):
        validate_rho([1.], np.array([np.diag([-1., 1., 1.])]))
    with pytest.raises(ValueError, match='finite'):
        model_parameters(np.nan, 0.)
