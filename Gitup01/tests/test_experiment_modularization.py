"""Behavioral acceptance tests against real engines and an independent toy dataset."""
from dataclasses import replace
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import numpy as np
import pytest

from cevns_pyeft.contracts import TheoryPoint, IntegrationSettings
from cevns_pyeft.experiments.catalog import ExperimentCatalog, BUILTIN_CATALOG
from cevns_pyeft.experiments.loader import load_experiment, ResourceCatalog, PreparedExperiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment, predict_selection, compile_experiment
from cevns_pyeft.experiments.selection import AnalysisSelection, parse_selection_yaml

ROOT=Path(__file__).resolve().parents[1]
SMALL={'n_er':5,'n_enu':12,'n_pe_bin':3}

@pytest.fixture(scope='module')
def experiments():
    return {key:load_experiment(key,resources=ROOT) for key in BUILTIN_CATALOG.ids()}

@pytest.fixture(scope='module')
def csi_prediction(experiments):
    return predict_experiment(experiments['CsI2021'],numerics=SMALL)


def test_catalog_is_lazy_and_has_three_exact_ids(tmp_path):
    code="""import sys
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
assert BUILTIN_CATALOG.ids() == ('CsI2021','CsI2017','Ar2020')
BUILTIN_CATALOG.describe()
assert 'cevns_pyeft.nuclear.response' not in sys.modules
assert not any(x.endswith('.slow_counts') for x in sys.modules)
"""
    result=subprocess.run([sys.executable,'-c',code],cwd=tmp_path,env={**os.environ,'PYTHONPATH':str(ROOT)},capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_all_prepared_have_same_outer_type(experiments):
    assert all(isinstance(x,PreparedExperiment) for x in experiments.values())
    assert {x.dataset_id for x in experiments.values()}==set(BUILTIN_CATALOG.ids())
    for key,exp in experiments.items():
        assert exp.describe()['definition']['dataset_id']==key


def test_real_cross_experiment_switch_has_no_global_state(experiments,csi_prediction):
    ar=predict_experiment(experiments['Ar2020'],numerics=SMALL)
    old=predict_experiment(experiments['CsI2017'],numerics={'n_enu':12})
    again=predict_experiment(experiments['CsI2021'],numerics=SMALL)
    assert ar.counts.shape==(12,) and old.counts.shape==(25,)
    np.testing.assert_array_equal(again.counts,csi_prediction.counts)


def test_source_and_response_overrides_control_actual_calculation(experiments,csi_prediction):
    original=experiments['CsI2021']; d=original.definition
    doubled=replace(d,physical=replace(d.physical,run=replace(d.physical.run,total_pot=2*d.physical.run.total_pot)))
    exp=load_experiment(d.dataset_id,resources=ROOT,definition=doubled)
    p=predict_experiment(exp,numerics=SMALL)
    np.testing.assert_allclose(p.counts,csi_prediction.counts*2,rtol=1e-14)
    altered=replace(d,physical=replace(d.physical,gamma_b=d.physical.gamma_b*1.2))
    response=load_experiment(d.dataset_id,resources=ROOT,definition=altered)
    q=predict_experiment(response,numerics=SMALL)
    assert not np.allclose(q.counts,csi_prediction.counts)
    assert response.model.observation.response.describe()['gamma_b']==d.physical.gamma_b*1.2
    assert original.model.observation.response.describe()['gamma_b']==d.physical.gamma_b
    assert exp.physics_fingerprint!=original.physics_fingerprint
    assert response.physics_fingerprint!=original.physics_fingerprint


@pytest.mark.parametrize('dataset',['CsI2017','Ar2020'])
def test_legacy_strategies_consume_independent_response_settings(experiments,dataset):
    base=experiments[dataset]; d=base.definition
    ns={'n_enu':8} if dataset=='CsI2017' else SMALL
    p=predict_experiment(base,numerics=ns)
    physical=replace(d.physical,pe_per_keV=d.physical.pe_per_keV*1.1) if dataset=='CsI2017' else replace(d.physical,sigma_coefficient=.75)
    changed=load_experiment(dataset,resources=ROOT,definition=replace(d,physical=physical))
    q=predict_experiment(changed,numerics=ns)
    assert not np.allclose(p.counts,q.counts)
    assert base.physics_fingerprint!=changed.physics_fingerprint


def test_unknown_ids_alias_conflicts_and_selection_duplicates():
    with pytest.raises(KeyError,match='unknown dataset'): load_experiment('missing')
    catalog=ExperimentCatalog()
    with pytest.raises(ValueError,match='duplicate'): catalog.register('X',None,aliases=('csi2021',))
    with pytest.raises(ValueError,match='duplicate'): AnalysisSelection.from_mapping({'datasets':[{'id':'CsI2021'},{'id':'csi2021'}]})


@pytest.mark.parametrize('document',[
    {'datasets':[{'id':'CsI2021','enabled':'false'}]},
    {'datasets':[{'id':'CsI2021','unused':2}]},
    {'datasets':[{'id':'CsI2017','numerics':{'n_er':51}}]},
    {'datasets':[{'id':'Ar2020','numerics':{'pe_step':2}}]},
    {'datasets':[{'id':'Ar2020','backend':'gpu'}]},
    {'datasets':[], 'joint_chi2':True},
])
def test_strict_selection_rejects_silent_overrides(document):
    with pytest.raises((ValueError,TypeError)): AnalysisSelection.from_mapping(document)


def test_yaml_nested_numerics_and_rejected_structures():
    text='datasets:\n  - id: CsI2021\n    numerics:\n      n_er: 5\n      pe_step: 2.0\n    enabled: true\n  - id: CsI2017\n    enabled: false\n'
    selection=AnalysisSelection.from_mapping(parse_selection_yaml(text))
    assert selection.datasets[0].numerics=={'n_er':5,'pe_step':2.}
    assert not selection.datasets[1].enabled
    for text in ('datasets:\n  - id: CsI2021\n    enabled: true\n    enabled: false',
                 'datasets:\n  - {id: CsI2021}', 'datasets:\n  - id: CsI2021\n    numerics: {n_er: 5}',
                 'datasets:\n  - id: !!python/object:x'):
        with pytest.raises((ValueError,TypeError)): parse_selection_yaml(text)


def test_disabled_missing_resources_are_never_resolved(tmp_path):
    shutil.copy2(ROOT/'data/responses/responses_all.json',tmp_path/'responses.json')
    class Tracked(ResourceCatalog):
        seen=[]
        def resolve(self,ref):
            self.seen.append(ref.id)
            return super().resolve(ref)
    resources=Tracked(tmp_path,{'responses':tmp_path/'responses.json'})
    selection=AnalysisSelection.from_mapping({'datasets':[{'id':'CsI2021','numerics':SMALL},
        {'id':'CsI2017','enabled':False},{'id':'Ar2020','enabled':False}]})
    result=predict_selection(selection,resources=resources)
    assert list(result)==['CsI2021']
    assert resources.seen==['responses']
    with pytest.raises(FileNotFoundError,match='efficiency'):
        load_experiment('CsI2017',resources=resources)


def test_missing_statistics_does_not_block_physics(tmp_path):
    resources=ResourceCatalog(tmp_path,{'responses':ROOT/'data/responses/responses_all.json','efficiency':ROOT/'data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt'})
    exp=load_experiment('CsI2017',resources=resources)
    pred=predict_experiment(exp,numerics={'n_enu':8})
    assert pred.counts.sum()>0
    with pytest.raises(FileNotFoundError,match='statistics resource'):
        evaluate_experiment(exp,pred)


def test_analysis_identity_and_observation_changes_cannot_be_swapped(experiments,csi_prediction):
    base=experiments['CsI2021']; d=base.definition
    changed=load_experiment(d.dataset_id,resources=ROOT,definition=replace(d,analysis_revision='another_analysis'))
    with pytest.raises(ValueError,match='identity'):evaluate_experiment(changed,csi_prediction)
    bad=replace(csi_prediction,combined_prediction=replace(csi_prediction.combined_prediction,
        binning=replace(csi_prediction.combined_prediction.binning,axes=(replace(csi_prediction.combined_prediction.axes[0],unit='eVee'),))))
    with pytest.raises(ValueError,match='axes'):evaluate_experiment(base,bad)


def test_statistics_only_change_preserves_physical_kernel(experiments,csi_prediction):
    base=experiments['CsI2021'];d=base.definition
    changed=load_experiment(d.dataset_id,resources=ROOT,definition=replace(d,statistics=replace(d.statistics,
        observed=tuple(x+1 for x in d.statistics.observed))))
    assert changed.physics_fingerprint==base.physics_fingerprint
    assert changed.analysis_fingerprint!=base.analysis_fingerprint
    assert evaluate_experiment(changed,replace(csi_prediction,analysis_fingerprint=changed.analysis_fingerprint)).chi2!=evaluate_experiment(base,csi_prediction).chi2


def test_legacy_fast_identity_is_checked_before_reconstruction(tmp_path):
    from cevns_pyeft.kernels.storage import build_fastscan_template,save_fastscan_template
    from cevns_pyeft.statistics.predictors import predict_raw_components
    from cevns_pyeft.kernels.basis import li2026_left_basis_current
    basis=[b for b in li2026_left_basis_current() if b.triplet[0]==6]
    kernel=build_fastscan_template('CsI2021',ROOT/'data/responses/responses_all.json',basis=basis,n_er=4,n_enu=8,n_pe_sub=3)
    path=tmp_path/'kernel.npz';save_fastscan_template(path,kernel)
    assert predict_raw_components('csi2021',mode='fast',fast_kernel_path=path).total.values.shape==(9,)
    with pytest.raises(ValueError,match="Ar2020.*CsI2021"):
        predict_raw_components('Ar2020',mode='fast',fast_kernel_path=path)
    with pytest.raises(KeyError,match='unknown dataset'):
        predict_raw_components('imaginary',mode='fast',fast_kernel_path=path)
    with pytest.raises(TypeError,match='cannot consume'):
        predict_raw_components('CsI2021',mode='fast',fast_kernel_path=path,n_er=7)
    metadata=json.loads(path.with_suffix('.json').read_text())
    metadata['pe_bins'][1]+=.1
    path.with_suffix('.json').write_text(json.dumps(metadata))
    # Array/metadata or requested observation mismatch must fail explicitly.
    with pytest.raises(ValueError):predict_raw_components('CsI2021',mode='fast',fast_kernel_path=path)


def test_csi_kernel_rejects_source_and_response_changes_and_roundtrips(experiments,tmp_path):
    from cevns_pyeft.kernels.compiler import compile_fast,StaleCompiledKernelError
    from cevns_pyeft.kernels.interface_storage import save_compiled_kernel,load_compiled_kernel
    exp=experiments['CsI2021'];d=exp.definition
    settings=IntegrationSettings.legacy_csi2021_v1(**SMALL)
    kernel=compile_fast(exp.model,numerics=settings,basis_keys=[(6,1,'u'),(6,1,'d'),(6,2,'u'),(6,2,'d')])
    path=tmp_path/'compiled.npz';save_compiled_kernel(path,kernel)
    loaded=load_compiled_kernel(path,model=exp.model,numerics=settings)
    a=predict_experiment(exp,backend='fast',kernel=loaded,numerics=SMALL)
    b=predict_experiment(exp,numerics=SMALL)
    np.testing.assert_allclose(a.counts,b.counts,rtol=1e-10,atol=1e-12)
    for physical in (replace(d.physical,run=replace(d.physical.run,total_pot=d.physical.run.total_pot*2)),
                     replace(d.physical,gamma_a=d.physical.gamma_a*1.1)):
        other=load_experiment(d.dataset_id,resources=ROOT,definition=replace(d,physical=physical))
        with pytest.raises(StaleCompiledKernelError):predict_experiment(other,backend='fast',kernel=kernel,numerics=SMALL)


@pytest.mark.parametrize('ds',['CsI2017','Ar2020'])
def test_legacy_fast_new_binding_save_load_and_invalidation(experiments,tmp_path,ds):
    from cevns_pyeft.kernels.storage import save_fastscan_template,load_fastscan_template
    exp=experiments[ds];d=exp.definition
    ns={'n_er':51,'n_enu':8} if ds=='CsI2017' else {'n_er':5,'n_enu':8,'n_obs_sub':3}
    kernel=compile_experiment(exp,numerics=ns)
    path=tmp_path/'legacy.npz';save_fastscan_template(path,kernel)
    loaded=load_fastscan_template(path)
    a=predict_experiment(exp,backend='fast',kernel=kernel,numerics=ns)
    b=predict_experiment(exp,backend='fast',kernel=loaded,numerics=ns)
    np.testing.assert_array_equal(a.counts,b.counts)
    changed=load_experiment(ds,resources=ROOT,definition=replace(d,physical=replace(d.physical,mass_kg=d.physical.mass_kg*2)))
    with pytest.raises(ValueError,match='identity / physical'):
        predict_experiment(changed,backend='fast',kernel=loaded,numerics=ns)






def test_different_resource_roots_and_content_changes_are_isolated(tmp_path,experiments):
    ref=next(r for r in experiments['Ar2020'].definition.resources if r.id=='efficiency')
    local=tmp_path/'eff.txt';shutil.copy2(ROOT/ref.path,local)
    exp=load_experiment('Ar2020',resources=ResourceCatalog(ROOT,{'efficiency':local}))
    base=predict_experiment(exp,numerics=SMALL)
    np.testing.assert_array_equal(base.counts,predict_experiment(experiments['Ar2020'],numerics=SMALL).counts)
    rows=local.read_text();local.write_text(rows.replace('0.0','0.00',1)+'\n')
    with pytest.raises(ValueError,match='resource.*changed'):predict_experiment(exp,numerics=SMALL)
    fresh=load_experiment('Ar2020',resources=ResourceCatalog(ROOT,{'efficiency':local}))
    assert fresh.physics_fingerprint!=exp.physics_fingerprint
    np.testing.assert_allclose(predict_experiment(fresh,numerics=SMALL).counts,base.counts,rtol=1e-14)


def test_unconsumed_backend_and_numerical_values_rejected(experiments):
    for ds,key in [('CsI2017','n_er'),('Ar2020','pe_step')]:
        with pytest.raises(TypeError,match='unconsumed'):predict_experiment(experiments[ds],numerics={key:9})
    for value in (True,1,2.5):
        with pytest.raises(ValueError):predict_experiment(experiments['CsI2021'],numerics={'n_er':value})
    with pytest.raises(ValueError,match='unsupported backend'):predict_experiment(experiments['CsI2021'],backend='gpu')


def test_legacy_get_experiment_preserves_dict_return():
    from cevns_pyeft.experiments.registry import get_experiment
    assert isinstance(get_experiment('CsI2021'),dict)


def test_synthetic_extension_uses_public_catalog_and_common_algorithms(tmp_path):
    import importlib.util
    file=ROOT/'examples/experiment_modularization/synthetic_dataset.py'
    spec=importlib.util.spec_from_file_location('synthetic_dataset',file)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    d=module.DEFINITION
    catalog=ExperimentCatalog(builtins=False).register(d.dataset_id,d,aliases=('demo',))
    exp=load_experiment('demo',resources=tmp_path,registry=catalog)
    p=predict_experiment(exp)
    np.testing.assert_allclose(p.counts,module.independent_expected(),rtol=1e-14)
    assert tuple(p.combined_prediction.components)==(('synthetic_beam_alpha','synthetic_nucleus'),)
    assert d.dataset_id not in BUILTIN_CATALOG.ids()
    with pytest.raises(ValueError,match='unsupported backend'):predict_experiment(exp,backend='fast')
    auto=predict_experiment(exp,backend='auto')
    np.testing.assert_array_equal(auto.counts,p.counts)
    assert auto.record['auto_reason']
    selection=AnalysisSelection.from_mapping({'datasets':[{'id':'demo'}]},registry=catalog)
    np.testing.assert_array_equal(predict_selection(selection,registry=catalog,resources=tmp_path)[d.dataset_id].counts,p.counts)


def test_resolved_definition_and_records_are_immutable(experiments):
    exp=experiments['CsI2021']
    with pytest.raises(TypeError): exp.record['actual_model']['binning'][0]['unit']='wrong'
    with pytest.raises(TypeError): exp.definition.numerical_profiles['slow']['n_er']=9
    from cevns_pyeft.experiments.definition import ObservationDefinition
    edges=[0.,1.,2.]
    obs=ObservationDefinition('test','fixture',edges)
    edges[0]=-.5
    assert obs.edges==(0.,1.,2.)


def test_prediction_and_evaluation_record_actual_theory_and_statistics(experiments,csi_prediction):
    result=evaluate_experiment(experiments['CsI2021'],csi_prediction)
    assert result.record['statistics']['observable_unit']=='counts/PE'
    assert result.chi2==result.profile.chi2
    assert len(result.record['statistics_fingerprint'])==64
    point=TheoryPoint({(6,1,'u'):np.eye(3)*1e-7})
    prediction=predict_experiment(experiments['Ar2020'],parameters=point,numerics=SMALL)
    assert prediction.record['theory_point']['wc_triplets']["(6, 1, 'u')"][0][0]['real']==1e-7


def test_statistical_mapping_rejects_same_size_different_bin_edges(experiments,csi_prediction):
    d=experiments['CsI2021'].definition
    edges=list(d.observation.edges);edges[1]+=.1
    changed=load_experiment(d.dataset_id,resources=ROOT,definition=replace(d,observation=replace(d.observation,edges=tuple(edges))))
    p=predict_experiment(changed,numerics=SMALL)
    with pytest.raises(ValueError,match='statistical observation mapping'):evaluate_experiment(changed,p)

@pytest.mark.parametrize('dataset',['CsI2017','Ar2020'])
def test_executor_rejects_relabeling_observable_units(experiments,dataset):
    d=experiments[dataset].definition
    with pytest.raises(ValueError,match='axis'):
        load_experiment(dataset,resources=ROOT,definition=replace(d,observation=replace(d.observation,unit='invented')))


def test_legacy_csi_mass_convention_is_consumed_by_both_backends(experiments):
    d=experiments['CsI2017'].definition
    altered=load_experiment(d.dataset_id,resources=ROOT,definition=replace(d,physical=replace(d.physical,atomic_mass_kg=d.physical.atomic_mass_kg*2)))
    for backend,ns in [('slow',{'n_enu':8}),('fast',{'n_er':51,'n_enu':8})]:
        base=predict_experiment(experiments['CsI2017'],backend=backend,numerics=ns)
        changed=predict_experiment(altered,backend=backend,numerics=ns)
        np.testing.assert_allclose(changed.counts,base.counts*.5,rtol=1e-14)


