"""Independent frozen comparisons for the two additional active packages."""
from pathlib import Path
import json
import shutil
import hashlib
import numpy as np
import pytest
from cevns_pyeft.contracts import TheoryPoint
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment,compile_experiment
from cevns_pyeft.experiments.input_package import validate_package
from tests.helpers.regression_cases import points

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={'Ar2020':ROOT/'data/experiments/COHERENT_Ar/Ar2020',
          'CsI2017':ROOT/'data/experiments/COHERENT_CsI/CsI2017'}


@pytest.fixture(scope='module')
def experiments():
    return {sid:load_experiment_package(path) for sid,path in PACKAGES.items()}


@pytest.mark.parametrize('sid',PACKAGES)
def test_all_formal_files_and_roles_are_valid(sid):
    assert validate_package(PACKAGES[sid])['status']=='PASS'
    data=json.loads((PACKAGES[sid]/'experiment.input.yaml').read_text('utf8'))
    assert data['package']['status']=='DRAFT' and data['package']['human_approval']=='NOT_REVIEWED'
    assert data['capabilities']['official_likelihood']['status']=='BLOCKED'
    assert data['capabilities']['general_antineutrino_EFT']['status']=='BLOCKED'
    assert all(p['consumers'] for p in data['parameters'].values() if p['role'] not in ('reference_only','unused_snapshot'))
    if sid=='CsI2017':assert 'numerics.recoil_min_keV' not in data['parameters']


@pytest.mark.parametrize('sid',PACKAGES)
@pytest.mark.parametrize('point_name',['sm','multiflavor'])
def test_package_source_isotope_bins_match_frozen_legacy(sid,point_name,experiments):
    wc,sm=points()[point_name]
    ns={'n_enu':12} if sid=='CsI2017' else dict(n_er=11,n_enu=40,n_pe_bin=8)
    p=predict_experiment(experiments[sid],parameters=TheoryPoint(wc,include_sm=sm),numerics=ns)
    with np.load(ROOT/'tests/reference/interface_refactor_v1/baseline.npz',allow_pickle=False) as ref:
        for label,component in [('mu','prompt_numu'),('e','delayed_nue'),('mub','delayed_numubar')]:
            actual=sum((v for (source,_),v in p.combined_prediction.components.items() if source==component),np.zeros_like(p.counts))
            np.testing.assert_allclose(actual,ref[f'{sid.lower()}/{point_name}/{label}'],rtol=1e-10,atol=1e-12)
        np.testing.assert_allclose(p.counts,ref[f'{sid.lower()}/{point_name}/total'],rtol=1e-10,atol=1e-12)
    assert np.isfinite(evaluate_experiment(experiments[sid],p).chi2)


@pytest.mark.parametrize('sid',PACKAGES)
def test_saved_fast_kernel_preserves_actual_package_identity(sid,experiments,tmp_path):
    from cevns_pyeft.kernels.storage import save_fastscan_template,load_fastscan_template
    ns={'n_er':51,'n_enu':8} if sid=='CsI2017' else dict(n_er=5,n_enu=8,n_obs_sub=3)
    exp=experiments[sid]
    kernel=compile_experiment(exp,numerics=ns)
    file=tmp_path/'kernel.npz';save_fastscan_template(file,kernel)
    reloaded=load_fastscan_template(file)
    one=predict_experiment(exp,backend='fast',kernel=kernel,numerics=ns)
    two=predict_experiment(exp,backend='fast',kernel=reloaded,numerics=ns)
    np.testing.assert_array_equal(one.counts,two.counts)
    with pytest.raises(ValueError,match='identity'):
        predict_experiment(exp,backend='fast',kernel=reloaded,numerics={**ns,'n_enu':9})


@pytest.mark.parametrize('sid',PACKAGES)
def test_two_files_no_external_efficiency_statistics_or_responses(tmp_path,sid):
    package=tmp_path/'two-files';package.mkdir()
    for name in ('experiment.input.yaml','experiment.resources.npz'):
        shutil.copy2(PACKAGES[sid]/name,package/name)
    exp=load_experiment_package(package)
    ns={'n_enu':8} if sid=='CsI2017' else dict(n_er=5,n_enu=8,n_pe_bin=3)
    result=predict_experiment(exp,numerics=ns)
    assert result.counts.shape==((25,) if sid=='CsI2017' else (12,)) and np.isfinite(evaluate_experiment(exp,result).chi2)
    assert set(exp.resolved_resources)=={'package_input','package_arrays'}


def test_detector_parameter_changes_direct_model_and_prediction(tmp_path):
    for name in ('experiment.input.yaml','experiment.resources.npz'):
        shutil.copy2(PACKAGES['Ar2020']/name,tmp_path/name)
    original=load_experiment_package(tmp_path)
    p=predict_experiment(original,numerics=dict(n_er=5,n_enu=8,n_pe_bin=3))
    path=tmp_path/'experiment.input.yaml';data=json.loads(path.read_text('utf8'))
    data['parameters']['detector.mean_linear']['value']*=1.01
    path.write_text(json.dumps(data),encoding='utf8')
    changed=load_experiment_package(tmp_path)
    assert changed.model.observation.mean_linear!=original.model.observation.mean_linear
    assert not np.allclose(p.counts,predict_experiment(changed,numerics=dict(n_er=5,n_enu=8,n_pe_bin=3)).counts)


def test_invalid_units_and_missing_common_snapshot_cannot_fallback(tmp_path):
    for name in ('experiment.input.yaml','experiment.resources.npz'):
        shutil.copy2(PACKAGES['Ar2020']/name,tmp_path/name)
    path=tmp_path/'experiment.input.yaml';data=json.loads(path.read_text('utf8'))
    data['parameters']['target.detector_mass']['unit']='g'
    path.write_text(json.dumps(data),encoding='utf8')
    with pytest.raises(ValueError,match='unit'):
        load_experiment_package(tmp_path)


@pytest.mark.parametrize('fault',['unknown_field','missing_snapshot','snapshot_role','specification_only','blocked_model',
                                'unknown_response_ref','efficiency_unit','source_stale','source_generation_missing',
                                'observable_unit','unbound_parameter','missing_model_dependency'])
def test_executable_package_rejects_incomplete_or_unconsumed_inputs(tmp_path,fault):
    for name in ('experiment.input.yaml','experiment.resources.npz'):
        shutil.copy2(PACKAGES['Ar2020']/name,tmp_path/name)
    path=tmp_path/'experiment.input.yaml';data=json.loads(path.read_text('utf8'))
    if fault=='unknown_field':data['assembly']['detector']['hidden_default']=123
    elif fault=='missing_snapshot':data['parameters'].pop('constants.G_F')
    elif fault=='snapshot_role':
        data['parameters']['constants.G_F'].update(role='unused_snapshot',consumers=[])
        data['models']['li2026_package_interaction_v1']['parameter_refs'].remove('constants.G_F')
    elif fault=='specification_only':data['models']['observed_gaussian_legacy_v1']['binding_status']='SPECIFICATION_ONLY'
    elif fault=='blocked_model':data['models']['observed_gaussian_legacy_v1']['binding_status']='BLOCKED'
    elif fault=='unknown_response_ref':data['assembly']['target']['isotopes'][0]['responses']['M']='missing'
    elif fault=='efficiency_unit':data['resources']['arrays']['efficiency_values']['unit']='PE'
    elif fault=='source_stale':data['parameters']['source.total_pot']['value']*=2
    elif fault=='source_generation_missing':
        meta=data['resources']['arrays']['source_fluence_1'];meta.update(role='direct_input',generation=None)
    elif fault=='observable_unit':data['observable']['unit']='keV'
    elif fault=='unbound_parameter':data['parameters']['detector.mean_linear']['consumers']=[]
    else:data['models']['observed_gaussian_legacy_v1']['depends_on'].append('unknown')
    path.write_text(json.dumps(data),encoding='utf8')
    with pytest.raises(ValueError):load_experiment_package(tmp_path)


def test_statistics_array_edit_keeps_physics_kernel_and_changes_analysis(tmp_path):
    for name in ('experiment.input.yaml','experiment.resources.npz'):
        shutil.copy2(PACKAGES['Ar2020']/name,tmp_path/name)
    original=load_experiment_package(tmp_path)
    ns=dict(n_er=4,n_enu=6,n_obs_sub=3)
    kernel=compile_experiment(original,numerics=ns)
    base=predict_experiment(original,backend='fast',kernel=kernel,numerics=ns)
    path=tmp_path/'experiment.input.yaml';data=json.loads(path.read_text('utf8'))
    archive=tmp_path/'experiment.resources.npz'
    with np.load(archive,allow_pickle=False) as saved:arrays={k:saved[k] for k in saved.files}
    arrays['statistics_observed']+=1
    np.savez(archive,**arrays)
    data['resources']['sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
    data['resources']['arrays']['statistics_observed']['sha256_raw_c_order']=hashlib.sha256(arrays['statistics_observed'].tobytes()).hexdigest()
    path.write_text(json.dumps(data),encoding='utf8')
    changed=load_experiment_package(tmp_path)
    assert changed.physics_fingerprint==original.physics_fingerprint
    assert changed.analysis_fingerprint!=original.analysis_fingerprint
    q=predict_experiment(changed,backend='fast',kernel=kernel,numerics=ns)
    np.testing.assert_array_equal(base.counts,q.counts)
    assert evaluate_experiment(changed,q).chi2!=evaluate_experiment(original,base).chi2


@pytest.mark.parametrize('sid',PACKAGES)
def test_full_operator_complex_flavor_fast_matches_slow_per_component(sid,experiments):
    from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
    rng=np.random.default_rng(20261104)
    coefficients={}
    for spec in LI2026_OPERATOR_SPECS:
        value=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*10.**(-spec.dimension-1)
        if spec.lepton_number=='LNV':np.fill_diagonal(value,0)
        coefficients[spec.key]=value
    point=TheoryPoint(coefficients,include_sm=False)
    exp=experiments[sid]
    slow_ns={'n_enu':8} if sid=='CsI2017' else dict(n_er=5,n_enu=8,n_pe_bin=3)
    fast_ns=dict(n_er=251,n_enu=8) if sid=='CsI2017' else dict(n_er=5,n_enu=8,n_obs_sub=3)
    slow=predict_experiment(exp,parameters=point,numerics=slow_ns)
    fast=predict_experiment(exp,parameters=point,backend='fast',numerics=fast_ns)
    for key,expected in slow.combined_prediction.components.items():
        np.testing.assert_allclose(fast.combined_prediction.components[key],expected,rtol=1e-10,atol=1e-12)
    np.testing.assert_allclose(fast.counts,slow.counts,rtol=1e-10,atol=1e-12)
