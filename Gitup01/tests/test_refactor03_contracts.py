from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment,predict_selection
from cevns_pyeft.experiments.selection import AnalysisSelection
ROOT=Path(__file__).resolve().parents[1]
NS={'n_er':5,'n_enu':12,'n_pe_bin':3}


def test_i01_unknown_and_ambiguous_resource_keys_rejected(tmp_path):
    with pytest.raises(KeyError,match='unknown or unused'):
        load_experiment('CsI2021',resources=ResourceCatalog(ROOT,{'respones':tmp_path/'missing'}))
    selection=AnalysisSelection.from_mapping({'datasets':[{'id':'CsI2017','enabled':False},{'id':'Ar2020','enabled':False}]})
    with pytest.raises(KeyError,match='ambiguous'):
        predict_selection(selection,resources=ResourceCatalog(ROOT,{'efficiency':tmp_path/'missing'}))
    assert predict_selection(selection,resources=ResourceCatalog(ROOT,{('CsI2017','efficiency'):tmp_path/'missing'}))=={}
    with pytest.raises(KeyError,match='scoped'):
        predict_selection(selection,resources=ResourceCatalog(ROOT,{('CsI2021','efficiency'):tmp_path/'missing'}))




def test_i03_prepare_changes_actual_identity_and_rejects_cross_evaluation():
    base=load_experiment('CsI2021',resources=ROOT)
    def doubled(definition,resources):
        model,executor=base.definition.prepare(definition,resources)
        return replace(model,source=replace(model.source,yield_per_pot=model.source.yield_per_pot*2)),executor
    custom=load_experiment('CsI2021',resources=ROOT,definition=replace(base.definition,prepare=doubled))
    p=predict_experiment(base,numerics=NS);q=predict_experiment(custom,numerics=NS)
    np.testing.assert_allclose(q.counts,p.counts*2,rtol=1e-14)
    assert base.physics_fingerprint!=custom.physics_fingerprint
    with pytest.raises(ValueError,match='physical'):evaluate_experiment(base,q)





def test_csi2017_coordinate_mismatch(tmp_path):
    base=load_experiment('CsI2017',resources=ROOT)
    ref=next(r for r in base.definition.resources if r.id=='data')
    path=tmp_path/'wrong_data.txt';arr=np.loadtxt(ROOT/ref.path);arr[:,0]+=100;np.savetxt(path,arr)
    exp=load_experiment('CsI2017',resources=ResourceCatalog(ROOT,{'data':path}))
    from cevns_pyeft.experiments.coherent.statistics_binding import dataset
    with pytest.raises(ValueError,match='coordinate'):dataset(exp.definition,exp.resource_catalog)


def test_data_alias_conflicts_and_duplicate_specs_rejected(tmp_path):
    from cevns_pyeft.foundation.resources import resolve_resource
    from cevns_pyeft.experiments.specs import discover_experiment_spec_paths
    old=tmp_path/'data/datafiles/COHERENT_eff.txt'
    new=tmp_path/'data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt'
    old.parent.mkdir(parents=True);new.parent.mkdir(parents=True)
    old.write_text('1 2');new.write_text('1 3')
    with pytest.raises(ValueError,match='conflicting'):resolve_resource(tmp_path,'data/datafiles/COHERENT_eff.txt')
    for name in ('one','two'):
        p=tmp_path/'data/experiments'/name/'experiment.yaml';p.parent.mkdir(exist_ok=True)
        p.write_text('dataset_name: same\nsource_type: synthetic\ntarget_mode: fixture\n')
    with pytest.raises(ValueError,match='duplicate'):discover_experiment_spec_paths(tmp_path)


@pytest.mark.parametrize('dataset',['CsI2021','CsI2017','Ar2020'])
def test_component_source_and_interaction_slots_are_consumed(dataset):
    from cevns_pyeft.contracts.modules import ModuleDescriptor
    from cevns_pyeft.contracts.interaction import DifferentialCrossSection
    base=load_experiment(dataset,resources=ROOT)
    from cevns_pyeft.sources.composable import ScaledSource
    source=ScaledSource(base.model.source,2.)
    ns={'n_enu':8} if dataset=='CsI2017' else NS
    p=predict_experiment(base,numerics=ns)
    changed=load_experiment(dataset,resources=ROOT,components={'source':source})
    q=predict_experiment(changed,numerics=ns)
    np.testing.assert_allclose(q.counts,p.counts*2,rtol=1e-12,atol=1e-12)
    assert changed.physics_fingerprint!=base.physics_fingerprint
    class HalfInteraction:
        def __init__(self,original):self.original=original;self.kinematics=original.kinematics
        def describe(self):return ModuleDescriptor('interaction','synthetic_test_half',parameters={'scale':.5,'original':self.original.describe().as_dict()})
        def dsigma_dT(self,**kwargs):
            result=self.original.dsigma_dT(**kwargs)
            return replace(result,values_cm2_per_keV=result.values_cm2_per_keV*.5)
    altered=load_experiment(dataset,resources=ROOT,components={'interaction':HalfInteraction(base.model.interaction)})
    np.testing.assert_allclose(predict_experiment(altered,numerics=ns).counts,p.counts*.5,rtol=1e-12,atol=1e-12)
    with pytest.raises(ValueError,match='physical'):evaluate_experiment(base,q)


def test_legacy_custom_response_and_material_slots_and_fast_rejection():
    from cevns_pyeft.targets.materials import inventory_from_mass_fractions
    base=load_experiment('CsI2017',resources=ROOT)
    ns={'n_enu':8};p=predict_experiment(base,numerics=ns)
    response=replace(base.model.observation,pe_per_keV=1.3)
    q=predict_experiment(load_experiment('CsI2017',resources=ROOT,components={'observation':response}),numerics=ns)
    assert not np.allclose(p.counts,q.counts)
    material=inventory_from_mass_fractions(base.model.targets.detector_mass_kg,base.model.targets.isotopes,(.9,.1))
    changed=load_experiment('CsI2017',resources=ROOT,components={'targets':material})
    assert not np.allclose(predict_experiment(changed,numerics=ns).counts,p.counts)
    from cevns_pyeft.experiments.runtime import compile_experiment
    with pytest.raises(ValueError,match='replaced components'):compile_experiment(changed,numerics={'n_er':51,'n_enu':8})


