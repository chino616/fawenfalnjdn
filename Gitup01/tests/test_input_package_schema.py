"""Meaningful contract failures; no production registration or physics mutation."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pytest

from cevns_pyeft.experiments.input_package import (
    strict_json, validate_document, validate_arrays, validate_package, read_arrays,
    render_physics, schema_document, dependency_fingerprint,
)

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'data/experiments/COHERENT_CsI/CsI2021'


@pytest.fixture(scope='module')
def canonical():
    data=strict_json((PACKAGE/'experiment.input.yaml').read_text(encoding='utf-8'))
    raw=(PACKAGE/'experiment.resources.npz').read_bytes()
    arrays=read_arrays(raw,data['resources']['arrays'])
    return data,arrays,raw


def test_schema_and_package_and_current_roles(canonical):
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(schema_document())
    data,arrays,raw=canonical
    assert not validate_document(data)
    assert not validate_arrays(data,arrays,raw)
    assert validate_package(PACKAGE)['status']=='PASS'
    assert len(data['parameters'])==105 and len(arrays)==23
    assert all(p['consumers'] or p['role'] in ('unused_snapshot','reference_only') for p in data['parameters'].values())
    for name in ('Sigma_ud','L9','L10','m_u','m_d'):
        p=data['parameters']['lecs.'+name]
        assert p['role']=='unused_snapshot' and not p['consumers'] and not p['affects_fingerprint']
    assert data['parameters']['target.run_mass_metadata']['role']=='reference_only'


@pytest.mark.parametrize('text', ['{"a":1,"a":2}','{"x":NaN}','{"x":Infinity}','{"x":1e400}',
                                 'a: 1','{"x": 1,}', '# comment\n{}', '!!python/object:foo {}'])
def test_only_strict_json_yaml_subset(text):
    with pytest.raises((ValueError,json.JSONDecodeError)):
        strict_json(text)


@pytest.mark.parametrize('case,expected',[
    ('unknown_top','schema'), ('unknown_parameter_field','schema'), ('unknown_model','schema'),
    ('model_cycle','cycle'), ('parameter_cycle','cycle'), ('wrong_unit','unit/slot'),
    ('wrong_resource_unit','resource consumer unit'), ('duplicate_normalization','normalization'),
    ('inactive_marked_active','inactive parameter'), ('stale_resource','stale materialized'),
    ('wrong_derived_value','derived value differs'), ('editable_derived','editable derived'),
    ('fake_official','false official'), ('human_promoted','human approval'),
    ('runtime_promoted','runtime readiness'), ('official_promoted','official likelihood'),
    ('legacy_authority','runtime_authority'), ('missing_consumer','consumer'),
    ('missing_coordinate','coordinate'), ('wrong_axis_unit','coordinate unit'),
    ('wrong_grid','grid size'), ('namespace','schema'), ('fake_binding','schema'),
])
def test_semantic_rejections(canonical,case,expected):
    data=deepcopy(canonical[0])
    params=data['parameters']; model=data['models']; resources=data['resources']['arrays']
    if case=='unknown_top': data['python_callable']='evil.module:main'
    elif case=='unknown_parameter_field': params['source.baseline_m']['fallback']=19.3
    elif case=='unknown_model': model['legacy_csi_gamma']['model_id']='unregistered_gamma'
    elif case=='model_cycle': model['legacy_csi_gamma']['depends_on']=['legacy_csi_gamma']
    elif case=='parameter_cycle': params['source.prompt_energy']['derivation']['input_refs']=['source.prompt_energy']
    elif case=='wrong_unit': params['source.baseline_m']['unit']='keV'
    elif case=='wrong_resource_unit': resources['statistics_observed']['unit']='MeV'
    elif case=='duplicate_normalization': resources['source_fluence_e']['normalization']['runtime_factors']=['POT']
    elif case=='inactive_marked_active': params['lecs.L9']['affects_fingerprint']=True
    elif case=='stale_resource': params['source.baseline_m']['value']=params['source.baseline_m']['adopted_value']=20.0
    elif case=='wrong_derived_value': params['target.Cs133.nuclei']['value']=params['target.Cs133.nuclei']['adopted_value']=1e20
    elif case=='editable_derived': params['source.prompt_energy']['editable']=True
    elif case=='fake_official': params['source.total_pot']['source_kind']='official_primary'
    elif case=='human_promoted': params['source.total_pot']['human_confirmed']=True
    elif case=='runtime_promoted':
        data['package']['runtime_ready']=True
        data.get('extensions', {}).get('codex.runtime_evidence', {}).pop('standalone', None)
    elif case=='official_promoted': data['capabilities']['official_likelihood']['readiness']='LEGACY_ONLY'
    elif case=='legacy_authority': data['legacy_spec']['runtime_authority']='experiment.yaml'
    elif case=='missing_consumer': params['detector.gamma_a']['consumers']=[]
    elif case=='missing_coordinate': resources['source_fluence_e']['axes'][0]['coordinate_ref']='missing_grid'
    elif case=='wrong_axis_unit': resources['source_fluence_e']['axes'][0]['unit']='keV'
    elif case=='wrong_grid': params['numerics.n_er']['value']=params['numerics.n_er']['adopted_value']=2.5
    elif case=='namespace': data['extensions']={'uncontrolled':{}}
    elif case=='fake_binding': model['legacy_csi_gamma']['contract']['binding_status']='BOUND'
    errors=validate_document(data)
    assert errors and any(expected in error for error in errors), errors


def test_controlled_extension_does_not_enable_execution(canonical):
    data=deepcopy(canonical[0])
    data.setdefault('extensions', {})['lab.review_note']={'text':'audit annotation only'}
    assert not validate_document(data)


def test_positional_derivation_inputs_have_distinct_fingerprints(canonical):
    data=canonical[0]
    first=['target.Cs133.A','target.Cs133.A','target.I127.A']
    second=['target.I127.A','target.Cs133.A','target.I127.A']
    assert dependency_fingerprint(data,first,formula_id='mass_fraction.v1') != dependency_fingerprint(data,second,formula_id='mass_fraction.v1')


@pytest.mark.parametrize('case',['missing','extra','shape','dtype','content','archive_hash','coordinate_order'])
def test_npz_rejections(canonical,case):
    data=deepcopy(canonical[0]); arrays={k:v.copy() for k,v in canonical[1].items()}; raw=canonical[2]
    if case=='missing': arrays.pop('statistics_background')
    elif case=='extra': arrays['unrelated_array']=np.array([1.])
    elif case=='shape': arrays['statistics_observed']=arrays['statistics_observed'][:-1]
    elif case=='dtype': arrays['statistics_observed']=arrays['statistics_observed'].astype('float32')
    elif case=='content': arrays['statistics_observed'][0]+=1
    elif case=='archive_hash': raw=raw+b'not identical bytes'
    elif case=='coordinate_order': arrays['observable_pe_edges']=arrays['observable_pe_edges'][::-1]
    assert validate_arrays(data,arrays,raw)


def test_pickle_and_duplicate_zip_members_rejected(canonical):
    metadata={'payload':{}}
    stream=io.BytesIO(); np.savez(stream,payload=np.array([{'no':'execution'}],dtype=object))
    with pytest.raises(ValueError): read_arrays(stream.getvalue(),metadata)
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as archive:
        archive.writestr('payload.npy',b'a')
        with pytest.warns(UserWarning): archive.writestr('payload.npy',b'b')
    with pytest.raises(ValueError,match='duplicate'): read_arrays(stream.getvalue(),metadata)


def test_md_drift_rejected_and_validator_is_read_only(tmp_path,canonical):
    data,arrays,raw=canonical
    (tmp_path/'experiment.input.yaml').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    (tmp_path/'experiment.resources.npz').write_bytes(raw)
    md=tmp_path/'experiment.physics.md'
    md.write_text(render_physics(data,arrays),encoding='utf-8')
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    assert validate_package(tmp_path)['status']=='PASS'
    assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    md.write_text(md.read_text(encoding='utf-8')+'\nextra_parameter=123\n',encoding='utf-8')
    assert validate_package(tmp_path)['status']=='FAIL'


def test_validator_does_not_import_physics_or_old_definition():
    code="import sys; from cevns_pyeft.experiments.input_package import schema_document; schema_document(); assert not any(k.startswith(('cevns_pyeft.theory','cevns_pyeft.experiments.coherent','cevns_pyeft.core.predict')) for k in sys.modules)"
    result=subprocess.run([sys.executable,'-B','-c',code],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
