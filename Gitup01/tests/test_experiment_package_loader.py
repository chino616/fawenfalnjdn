"""The two files feed existing PreparedExperiment and Runtime contracts."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
import pytest

from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.loader import PreparedExperiment, load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from tests.helpers.regression_cases import GRIDS

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'data/experiments/COHERENT_CsI/CsI2021'
SMALL = GRIDS['small']


@pytest.fixture
def package(tmp_path):
    for name in ('experiment.input.yaml', 'experiment.resources.npz'):
        shutil.copy2(PACKAGE/name, tmp_path/name)
    return tmp_path


def edit(package, fn):
    path = package/'experiment.input.yaml'
    data = json.loads(path.read_text('utf8'))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')


def test_two_files_build_existing_objects_without_md(package):
    exp = load_experiment_package(package)
    assert isinstance(exp, PreparedExperiment)
    assert exp.dataset_id == 'CsI2021'
    assert not (package/'experiment.physics.md').exists()
    assert set(exp.resolved_resources) == {'package_input', 'package_arrays'}
    assert exp.model.targets.isotopes[0].number_of_nuclei > 0
    assert exp.model.source.for_run(exp.model.run).components[2].particle_kind == 'antinu'
    assert not exp.model.source.fluence.components[1].continuum_function.values.flags.writeable
    assert type(load_experiment('CsI2021').definition.prepare).__module__.endswith('package_loader')


def test_initial_package_prediction_and_approximate_statistics_match_frozen_baseline(package):
    exp = load_experiment_package(package)
    prediction = predict_experiment(exp, numerics=SMALL)
    with np.load(ROOT/'tests/reference/interface_refactor_v1/baseline.npz', allow_pickle=False) as frozen:
        np.testing.assert_allclose(prediction.counts, frozen['csi2021/sm/small/counts_per_bin/total'], rtol=1e-10, atol=1e-12)
    metadata = json.loads((ROOT/'tests/reference/interface_refactor_v1/metadata.json').read_text('utf8'))
    assert evaluate_experiment(exp, prediction).chi2 == pytest.approx(metadata['chi2_small_sm'], rel=1e-12)


def test_statistics_only_edit_changes_analysis_identity_not_physics(package):
    original = load_experiment_package(package)
    archive = package/'experiment.resources.npz'
    with np.load(archive, allow_pickle=False) as stored:
        arrays = {key: stored[key] for key in stored.files}
    arrays['statistics_observed'] += .1
    np.savez(archive, **arrays)
    def update(data):
        data['resources']['sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
        data['resources']['arrays']['statistics_observed']['sha256_raw_c_order'] = hashlib.sha256(arrays['statistics_observed'].tobytes()).hexdigest()
    edit(package, update)
    modified = load_experiment_package(package)
    assert modified.physics_fingerprint == original.physics_fingerprint
    assert modified.analysis_fingerprint != original.analysis_fingerprint


@pytest.mark.parametrize('fault', ['archive_hash', 'array_hash', 'absolute_path', 'traversal', 'unknown_model', 'missing_resource', 'stale'])
def test_resource_and_binding_faults_are_rejected(package, fault):
    def corrupt(data):
        if fault == 'archive_hash':
            data['resources']['sha256'] = '0'*64
        elif fault == 'array_hash':
            data['resources']['arrays']['source_fluence_e']['sha256_raw_c_order'] = '0'*64
        elif fault == 'absolute_path':
            data['resources']['archive'] = 'F:/other.npz'
        elif fault == 'traversal':
            data['resources']['archive'] = '../other.npz'
        elif fault == 'unknown_model':
            data['models']['legacy_csi_gamma']['model_id'] = 'python.import'
        elif fault == 'missing_resource':
            data['source']['components'][1]['continuum_ref'] = 'not_present'
        else:
            data['parameters']['source.total_pot']['value'] *= 2
            data['parameters']['source.total_pot']['adopted_value'] = data['parameters']['source.total_pot']['value']
    edit(package, corrupt)
    with pytest.raises(ValueError, match='package input/resource validation'):
        load_experiment_package(package)


def test_blocked_statistics_do_not_block_prediction(package):
    edit(package, lambda d: d['capabilities']['legacy_approximate_statistics'].update(readiness='BLOCKED'))
    exp = load_experiment_package(package)
    assert exp.definition.statistics is None
    prediction = predict_experiment(exp, numerics=SMALL)
    with pytest.raises(ValueError, match='statistics unavailable'):
        evaluate_experiment(exp, prediction)


def test_no_security_validation_bypass(package):
    with pytest.raises(ValueError, match='cannot be disabled'):
        load_experiment_package(package, validate=False)


def test_package_controls_default_sm_inclusion(package):
    def change(data):
        p = data['parameters']['interaction.include_sm']
        p['value'] = p['adopted_value'] = False
    edit(package, change)
    result = predict_experiment(load_experiment_package(package), numerics=SMALL)
    np.testing.assert_array_equal(result.counts, np.zeros(9))
