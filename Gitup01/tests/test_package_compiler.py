from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from cevns_pyeft.experiments.package_compiler import compile_draft, write_package
from cevns_pyeft.experiments.input_package import validate_package
from tests.helpers.onboarding_drafts import synthetic_draft



@pytest.fixture
def tmp_path(tmp_path_factory, request):
    """One isolated task tree; match normal dataset inheritance, not mkdtemp 0700."""
    import os
    import subprocess
    root=tmp_path_factory.getbasetemp()
    if os.name=='nt':
        subprocess.run(['icacls',str(root),'/reset'],check=True,capture_output=True)
    # Normal mkdir inherits like data/experiments; pytest's mkdtemp uses 0700.
    path=root/request.node.name.replace('[','-').replace(']','')
    path.mkdir()
    return path


def test_reproducible_machine_pair_and_two_md_views(tmp_path):
    draft,arrays=synthetic_draft()
    a,report=compile_draft(draft,arrays)
    b,_=compile_draft(draft,dict(reversed(list(arrays.items()))))
    assert a==b and len(a)==4 and report['human_approval']=='NOT_REVIEWED'
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


def _existing_package(relative):
    from cevns_pyeft.experiments.input_package import strict_json, read_arrays
    directory=Path(__file__).resolve().parents[1]/'data/experiments'/relative
    data=strict_json((directory/'experiment.input.yaml').read_text('utf8'))
    arrays=read_arrays((directory/'experiment.resources.npz').read_bytes(),data['resources']['arrays'])
    return data,arrays


@pytest.mark.parametrize('relative,required,excluded', [
    ('COHERENT_CsI/CsI2021', ['Gamma','shape-rate','source.total_pot','nuclear_Cs133_M','nuclear_I127_M','counts/PE'],
     ['b1313','cp[','cn[','source_line','量、函数或索引；非直接标量']),
    ('COHERENT_CsI/CsI2017',['detector.pe_per_keV','counts/bin','确定性'],['detector.quenching_q2','Gamma PE']),
    ('COHERENT_Ar/Ar2020',['nuclear_Ar40_M','detector.mean_quadratic','s(x)','IRLS'],['nuclear_Cs133_M','Gamma PE']),
])
def test_report_content_selection_and_sequential_equations(relative,required,excluded):
    import re
    from cevns_pyeft.experiments.input_package import render_physics
    data,arrays=_existing_package(relative)
    md=render_physics(data,arrays)
    assert all(text in md for text in required)
    assert not any(text in md for text in excluded)
    assert not any(text in md for text in ('.svg',chr(96)*3,'\ufffd','\r'))
    assert len(md.splitlines())<1000
    numbers=[int(n) for n in re.findall(r'<a id="eq-(\d+)">',md)]
    assert numbers==list(range(1,len(numbers)+1))
    anchors=set(re.findall(r'<a id="([^"]+)">',md))
    assert all(ref in anchors for ref in re.findall(r'\]\(#([^)]+)\)',md))
    equations=re.findall(r'\$\$\n(.*?)\n\$\$\n\n(\|.*?)(?=\n\n)',md,re.S)
    assert len(equations)==len(numbers)
    assert not any('&#124;' in text for text in re.findall(r'(?<!\$)\$(?!\$)([^\n$]+)\$(?!\$)',md))
    for _,table in equations:
        symbols=[row.split('|')[1].strip() for row in table.splitlines()[2:]]
        assert len(symbols)==len(set(symbols))


def test_quenching_ref_does_not_expand_public_kinematics():
    from cevns_pyeft.experiments.input_package import render_physics
    data,arrays=_existing_package('COHERENT_CsI/CsI2021')
    md=render_physics(data,arrays)
    for row in md.splitlines():
        if row.startswith('| $q^2$ |'):
            assert 'quenching_q2' not in row and row.endswith('— |')
        if row.startswith('| $q_2$ |'):
            assert '['+chr(96)+'detector.quenching_q2'+chr(96)+'](#param-detector-quenching_q2)' in row
    assert '| $q^2$ |' not in md and '| $q_2$ |' in md


def test_authored_report_metadata_is_consumed_and_unknown_fields_refs_rejected():
    from cevns_pyeft.experiments.input_package import validate_document
    draft,arrays=synthetic_draft()
    report={'summary':'Authored fixture summary','calculation_steps':['Use the declared test amplitude.'],
            'models':{'constant_v1':{'group':'theory','content_class':'experiment_specific',
                'title':'Declared amplitude','explanation':'Explicit H3 fixture, no experiment claim.',
                'equations':[{'id':'constant','title':'Fixture relation','latex':'y=a',
                    'symbols':[{'symbol':'y','definition':'synthetic output','unit':'1','parameter_ref':None},
                               {'symbol':'a','definition':'declared amplitude','unit':'1','parameter_ref':'amplitude'}]}]}}}
    draft['document']['extensions']={'lab.physics_report':report}
    files,result=compile_draft(draft,arrays)
    md=files['experiment.physics.md'].decode('utf8')
    assert 'Authored fixture summary' in md and 'y=a' in md
    assert 'H3_UNCLASSIFIED_MODEL: constant_v1' not in result['diagnostics']
    assert not any(word in md for word in ('CsI','SNS','quenching','Gamma'))
    for mutation in ('field','parameter','unit','symbol','model','equation'):
        bad=deepcopy(draft['document'])
        meta=bad['extensions']['lab.physics_report']
        equation=meta['models']['constant_v1']['equations'][0]
        if mutation=='field':meta['ignored_unknown']=True
        elif mutation=='parameter':equation['symbols'][1]['parameter_ref']='missing'
        elif mutation=='unit':equation['symbols'][1]['unit']='keV'
        elif mutation=='symbol':equation['symbols'].append(deepcopy(equation['symbols'][0]))
        elif mutation=='model':meta['models']['missing']=meta['models'].pop('constant_v1')
        else:meta['models']['constant_v1']['equations'].append(deepcopy(equation))
        assert validate_document(bad),mutation


def test_md_only_preserves_machine_bytes_and_uses_existing_cli(tmp_path):
    from tools.compile_experiment_package import main
    draft,arrays=synthetic_draft()
    write_package(draft,arrays,tmp_path)
    machine={name:(tmp_path/name).read_bytes() for name in ('experiment.input.yaml','experiment.resources.npz')}
    (tmp_path/'experiment.physics.md').write_text('stale',encoding='utf8')
    assert main(['--output',str(tmp_path),'--md-only','--check'])==1
    assert main(['--output',str(tmp_path),'--md-only','--overwrite'])==0
    assert machine=={name:(tmp_path/name).read_bytes() for name in machine}
    assert validate_package(tmp_path)['status']=='PASS'


def test_writer_stages_next_to_target_repeats_acl_and_reports_identity(tmp_path,monkeypatch):
    import os
    import subprocess
    from cevns_pyeft.experiments import package_compiler as compiler
    draft,arrays=synthetic_draft()
    seen=[]
    real=compiler._check_inherited_acl
    def inspect(paths):
        assert all(p.parent==tmp_path.resolve() for p in paths)
        seen.append([(p.name,p.read_bytes()) for p in paths])
        return real(paths)
    monkeypatch.setattr(compiler,'_check_inherited_acl',inspect)
    monkeypatch.setenv('CEVNS_TARGET_WINDOWS_PRINCIPAL','fixture\\different_user')
    one=write_package(draft,arrays,tmp_path)
    assert one['write_state']=='WRITE_OK' and one['target_user_read_state']=='TARGET_USER_READ_PENDING'
    if os.name=='nt':
        monkeypatch.setenv('CEVNS_TARGET_WINDOWS_PRINCIPAL',subprocess.check_output(['whoami'],text=True).strip())
    draft['document']['parameters']['amplitude']['value']=3.
    two=write_package(draft,arrays,tmp_path,overwrite=True)
    assert len(seen)==4
    assert all(name.endswith('.compiler-tmp') for name,_ in seen[0]+seen[2])
    assert not list(tmp_path.glob('.*.compiler-*'))
    if os.name=='nt':
        assert one['temporary_acl_state']==two['acl_state']=='ACL_INHERITANCE_OK'
        assert two['target_user_read_state']=='TARGET_USER_READ_OK'


@pytest.mark.parametrize('stage',['prepare','second_replace','final_check'])
def test_failed_write_preserves_original_files_and_security(tmp_path,monkeypatch,stage):
    from cevns_pyeft.experiments import package_compiler as compiler
    draft,arrays=synthetic_draft()
    write_package(draft,arrays,tmp_path)
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    before_ids={name:(tmp_path/name).stat().st_ino for name in before}
    original_acl=compiler._check_inherited_acl
    calls=0
    def acl(paths):
        nonlocal calls
        calls+=1
        if stage=='prepare' or (stage=='final_check' and calls==2):
            raise OSError('simulated ACL verification failure')
        return original_acl(paths)
    real_replace=compiler.os.replace
    def replace(source,target):
        if stage=='second_replace' and str(source).endswith('.compiler-tmp') and Path(target).name=='experiment.resources.npz':
            raise OSError('simulated second replacement failure')
        return real_replace(source,target)
    monkeypatch.setattr(compiler,'_check_inherited_acl',acl)
    monkeypatch.setattr(compiler.os,'replace',replace)
    draft['document']['parameters']['amplitude']['value']=3.
    with pytest.raises(OSError,match='simulated'):write_package(draft,arrays,tmp_path,overwrite=True)
    assert before=={name:(tmp_path/name).read_bytes() for name in before}
    assert not list(tmp_path.glob('.*.compiler-*'))
    assert before_ids=={name:(tmp_path/name).stat().st_ino for name in before}
    assert original_acl([tmp_path/name for name in before]) in ('ACL_INHERITANCE_OK','NOT_APPLICABLE')


def test_csi_detailed_is_complete_and_summary_does_not_repeat_formulas_or_bin_data():
    from cevns_pyeft.experiments.input_package import render_physics
    data,arrays=_existing_package('COHERENT_CsI/CsI2021')
    detailed=render_physics(data,arrays)
    summary=render_physics(data,arrays,summary=True)
    for text in ('source_table','source_interpolation'):
        # Internal equation keys are not prose; the actual reviewed math is.
        assert text not in summary
    assert r'E_{\mathrm{mask,min}}' in detailed
    assert r'E_{\mathrm{int,max}}' in detailed
    assert r'\phi_\mu(E_M)=F\delta' in detailed
    assert r'm_{i,\mathrm{kg}}=A_i' in detailed
    assert r'\operatorname{Var}(x)' in detailed
    assert r'\operatorname{Trapz}' in detailed
    assert r'\widehat\alpha' in detailed
    for key in ('state_rho_e','state_rho_mu','statistics_observed','statistics_background','statistics_uncertainty'):
        assert '#res-'+key.replace('.','-') in detailed
    for raw in arrays[data['statistics']['observed_ref']]:
        assert str(float(raw)) in detailed
    for forbidden in (r'c_j^p',r'c_j^n',r'W_{X,i}^{uv}(y)',r'T_{\max}(E)',r'\operatorname{Tr}(\rho K_i)'):
        assert forbidden not in detailed
    assert 'Interaction' in detailed and 'Nuclear Structure' in detailed
    assert 'experiment.physics.summary.md' in detailed
    assert 'experiment.physics.md' in summary
    assert '$$' not in summary and len(summary.splitlines())<90
    assert 'statistics_observed' not in summary


def test_metadata_can_reference_exact_npz_ids_and_shared_models_only_select():
    from cevns_pyeft.experiments.input_package import validate_document
    draft,arrays=synthetic_draft()
    report={'summary':'One authored summary for both views','models':{
        'constant_v1':{'group':'theory','content_class':'shared_framework','title':'Public choice',
            'explanation':'Do not expand this implementation.',
            'equations':[{'id':'shared','title':'Never print this formula','latex':r'\notapublicmacro',
                'symbols':[{'symbol':'a','definition':'amplitude','unit':'1','parameter_ref':'amplitude'}]}]},
        'tabulated_curve_v1':{'group':'source','content_class':'experiment_specific','title':'Declared table',
            'explanation':'Use the explicit synthetic table.',
            'equations':[{'id':'table','title':'Tabulated input','latex':'y=f(E)',
                'symbols':[{'symbol':'E','definition':'coordinate array','unit':'MeV','parameter_ref':'energy'},
                           {'symbol':'y','definition':'table values','unit':'1','parameter_ref':'curve'},
                           {'symbol':'f','definition':'declared interpolation function','unit':'1','parameter_ref':None}]}]}}}
    draft['document']['extensions']={'lab.physics_report':report}
    files,_=compile_draft(draft,arrays)
    detailed=files['experiment.physics.md'].decode('utf8')
    summary=files['experiment.physics.summary.md'].decode('utf8')
    assert 'One authored summary for both views' in detailed and 'One authored summary for both views' in summary
    assert '#res-energy' in detailed and 'y=f(E)' in detailed
    assert 'constant_v1' in detailed and r'\notapublicmacro' not in detailed
    assert 'Never print this formula' not in detailed and 'Do not expand this implementation.' not in detailed
    bad=deepcopy(draft['document'])
    bad['extensions']['lab.physics_report']['models']['tabulated_curve_v1']['equations'][0]['symbols'][0]['unit']='keV'
    assert any('reference/unit' in e for e in validate_document(bad))
    bad=deepcopy(draft['document'])
    bad['extensions']['lab.physics_report']['models']=[]
    assert validate_document(bad)
    bad=deepcopy(draft['document'])
    bad['extensions']['lab.physics_report']['models']['constant_v1']['id']='constant_v1'
    assert validate_document(bad)


def test_summary_consistency_and_md_only_check_are_read_only(tmp_path):
    draft,arrays=synthetic_draft()
    write_package(draft,arrays,tmp_path)
    machine={name:(tmp_path/name).read_bytes() for name in ('experiment.input.yaml','experiment.resources.npz')}
    path=tmp_path/'experiment.physics.summary.md'
    path.write_text('stale summary',encoding='utf8')
    result=validate_package(tmp_path)
    assert result['status']=='FAIL' and any('summary MD differs' in e for e in result['errors'])
    checked=write_package(None,None,tmp_path,md_only=True,check=True)
    assert checked['status']=='FAIL' and path.read_text('utf8')=='stale summary'
    result=write_package(None,None,tmp_path,md_only=True,overwrite=True)
    assert set(result['sha256'])=={'experiment.physics.md','experiment.physics.summary.md'}
    assert machine=={name:(tmp_path/name).read_bytes() for name in machine}
    assert validate_package(tmp_path)['status']=='PASS'
