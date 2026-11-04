from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from cevns_pyeft.experiments.package_compiler import compile_draft, write_package
from cevns_pyeft.experiments.input_package import validate_package
from tests.helpers.onboarding_drafts import synthetic_draft


def test_reproducible_three_files_and_synthetic_table_md_coverage(tmp_path):
    draft,arrays=synthetic_draft()
    a,report=compile_draft(draft,arrays)
    b,_=compile_draft(draft,dict(reversed(list(arrays.items()))))
    assert a==b and len(a)==3 and report['human_approval']=='NOT_REVIEWED'
    md=a['experiment.physics.md'].decode('utf8')
    assert all(key in md for group in ('parameters','models') for key in draft['document'][group])
    assert all(key in md for key in arrays)
    write_package(draft,arrays,tmp_path)
    assert validate_package(tmp_path)['status']=='PASS'


def test_different_identity_and_values_are_not_csi_hardcoded():
    one,arrays=synthetic_draft('Alpha')
    two=deepcopy(one);two['document']['package']['dataset_id']='Beta'
    two['document']['parameters']['amplitude']['value']=7.
    files,_=compile_draft(two,arrays)
    result=json.loads(files['experiment.input.yaml'])
    assert result['package']['dataset_id']=='Beta' and result['parameters']['amplitude']['value']==7.


def test_missing_conflicts_stay_missing_and_blocked():
    draft,arrays=synthetic_draft(missing=True)
    files,_=compile_draft(draft,arrays)
    doc=json.loads(files['experiment.input.yaml'])
    assert doc['parameters']['amplitude']['value'] is None
    assert doc['capabilities']['signal']['status']=='BLOCKED'


def test_check_readonly_create_only_and_explicit_overwrite(tmp_path):
    draft,arrays=synthetic_draft()
    assert write_package(draft,arrays,tmp_path,check=True)['status']=='FAIL'
    assert not list(tmp_path.iterdir())
    write_package(draft,arrays,tmp_path)
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    assert write_package(draft,arrays,tmp_path,check=True)['status']=='PASS'
    assert before=={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(FileExistsError):write_package(draft,arrays,tmp_path)
    draft['document']['parameters']['amplitude']['value']=3.
    write_package(draft,arrays,tmp_path,overwrite=True)
    backup=next(tmp_path.glob('compiler-backup-*'))
    assert {p.name:p.read_bytes() for p in backup.iterdir()}==before


def test_canonical_overwrite_quarantines_recovery_files_outside_active_data(tmp_path,monkeypatch):
    from cevns_pyeft.experiments import package_compiler as compiler
    repository=tmp_path/'repository'
    monkeypatch.setattr(compiler,'__file__',str(repository/'cevns_pyeft/experiments/package_compiler.py'))
    output=repository/'data/experiments/Synthetic/SyntheticCurve'
    draft,arrays=synthetic_draft();write_package(draft,arrays,output)
    before={p.name:p.read_bytes() for p in output.iterdir()}
    draft['document']['parameters']['amplitude']['value']=3.
    write_package(draft,arrays,output,overwrite=True)
    assert {p.name for p in output.iterdir()}==set(before)
    recovery=next((repository/'backup/package_compiler/Synthetic/SyntheticCurve').iterdir())
    assert {p.name:p.read_bytes() for p in recovery.iterdir()}==before
    manifest=(repository/'backup/BACKUP_MANIFEST.md').read_text('utf8')
    assert all(name in manifest for name in before)


@pytest.mark.parametrize('fault',['object','precision','formula','unit','cycle','source','role'])
def test_invalid_science_or_resources_are_not_filled(fault):
    draft,arrays=synthetic_draft();doc=draft['document']
    if fault=='object':arrays['curve']=np.array([object(),object(),object()])
    elif fault=='precision':arrays['curve']=arrays['curve'].astype('float32')
    elif fault=='formula':doc['models']['constant_v1']['formula']='python import arbitrary'
    elif fault=='unit':doc['resources']['arrays']['curve']['axes'][0]['unit']='keV'
    elif fault=='cycle':doc['models']['constant_v1']['depends_on']=['constant_v1']
    elif fault=='source':doc['parameters']['amplitude']['source_refs']=['missing']
    else:doc['parameters']['amplitude']['role']='reference_only'
    with pytest.raises(ValueError):compile_draft(draft,arrays)


def test_csi_fixture_uses_same_compiler_without_legacy_builder(tmp_path):
    root=Path(__file__).resolve().parents[1]
    package=root/'data/experiments/COHERENT_CsI/CsI2021'
    data=json.loads((package/'experiment.input.yaml').read_text('utf8'))
    with np.load(package/'experiment.resources.npz',allow_pickle=False) as stored:
        arrays={k:stored[k] for k in stored.files}
    draft={'ir_version':'cevns-onboarding-draft/1','acquisition':{'mode':'legacy_migration','evidence_claims':[]},
           'requested_capabilities':['legacy_prediction'],'document':data}
    write_package(draft,arrays,tmp_path)
    assert validate_package(tmp_path)['status']=='PASS'
    with np.load(tmp_path/'experiment.resources.npz',allow_pickle=False) as stored:
        for key,value in arrays.items():np.testing.assert_array_equal(stored[key],value)
