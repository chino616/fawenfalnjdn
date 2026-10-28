from dataclasses import replace
from pathlib import Path
import csv,json,shutil
import numpy as np
import pytest
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment,predict_selection
from cevns_pyeft.experiments.selection import AnalysisSelection
from cevns_pyeft.experiments.conus_plus.definition import make_effective119_benchmark_definition
ROOT=Path(__file__).resolve().parents[1]
CID='conus_plus_2025_c2c3c5_ge73_pyeft'
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


def test_i02_mutable_threshold_input_is_copied_and_frozen():
    d=load_experiment(CID,resources=ROOT).definition
    thresholds=list(d.physical.detector.thresholds_evee)
    changed=replace(d,physical=replace(d.physical,detector=replace(d.physical.detector,thresholds_evee=thresholds)))
    exp=load_experiment(CID,definition=changed,resources=ROOT)
    first=predict_experiment(exp,numerics={'n_recoil':8,'n_energy':2})
    thresholds[1]=('C3',320.)
    again=predict_experiment(exp,numerics={'n_recoil':8,'n_energy':2})
    np.testing.assert_array_equal(first.counts,again.counts)
    assert exp.definition.physical.detector.thresholds_evee[1]==('C3',160.)


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


def synthetic_csv(path,*,offset=0,unit='eVee',reverse=False):
    """Synthetic values test the input contract; never physical observations."""
    rows=[]
    for i,lo in enumerate(range(160,350,10)):
        rows.append([lo+offset,lo+10+offset,lo+5+offset,float(i-3),3.,unit])
    if reverse:rows.reverse()
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['low_eVee','high_eVee','center_eVee','observed_excess_per_kg_10eVee','sigma_used_half_span','axis_unit']);writer.writerows(rows)

@pytest.mark.parametrize('kwargs',[{'offset':10000},{'unit':'keVee'},{'reverse':True}])
def test_i04_bad_external_coordinates_units_and_order_rejected(tmp_path,kwargs):
    path=tmp_path/'synthetic.csv';synthetic_csv(path,**kwargs)
    d=make_effective119_benchmark_definition()
    exp=load_experiment(CID,resources=ResourceCatalog(ROOT,{'observations':path}),definition=d)
    pred=predict_experiment(exp,numerics={'n_recoil':8,'n_energy':2})
    with pytest.raises(ValueError,match='coordinate|unit'):evaluate_experiment(exp,pred)


def test_synthetic_statistics_valid_contract_and_csi2017_coordinate_mismatch(tmp_path):
    path=tmp_path/'synthetic.csv';synthetic_csv(path)
    d=make_effective119_benchmark_definition()
    exp=load_experiment(CID,resources=ResourceCatalog(ROOT,{'observations':path}),definition=d)
    assert np.isfinite(evaluate_experiment(exp,predict_experiment(exp,numerics={'n_recoil':8,'n_energy':2})).chi2)
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


@pytest.mark.parametrize('dataset',['CsI2021','CsI2017','Ar2020',CID])
def test_component_source_and_interaction_slots_are_consumed(dataset):
    from cevns_pyeft.contracts.modules import ModuleDescriptor
    from cevns_pyeft.contracts.interaction import DifferentialCrossSection
    base=load_experiment(dataset,resources=ROOT)
    if dataset==CID:
        from cevns_pyeft.experiments.conus_plus.components import ScaledFluxSource
        source=ScaledFluxSource(base.model.source,2.)
        ns={'n_recoil':8,'n_energy':2}
    else:
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


def test_response_matrix_reuses_for_flux_change_but_checks_actual_exposure():
    from cevns_pyeft.experiments.conus_plus.components import ScaledFluxSource
    from cevns_pyeft.experiments.runtime import compile_experiment
    from cevns_pyeft.experiments.definition import MassTimeExposure
    base=load_experiment(CID,resources=ROOT);ns={'n_recoil':8,'n_energy':2}
    kernel=compile_experiment(base,numerics=ns)
    p=predict_experiment(base,backend='fast',kernel=kernel,numerics=ns)
    changed=load_experiment(CID,resources=ROOT,components={'source':ScaledFluxSource(base.model.source,2.)})
    q=predict_experiment(changed,backend='fast',kernel=kernel,numerics=ns)
    np.testing.assert_allclose(q.counts,p.counts*2,rtol=1e-12,atol=1e-12)
    d=make_effective119_benchmark_definition()
    wrong=load_experiment(CID,resources=ROOT,definition=d,components={'exposures':base.model.exposures})
    with pytest.raises(ValueError,match='effective119'):
        evaluate_experiment(wrong,predict_experiment(wrong,numerics=ns))
