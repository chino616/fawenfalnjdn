"""Dataset lifecycle transactions in isolated copies; real smoke tests separate.

Unit cases replace only the expensive numeric subprocess, never source files in
the working repository. The integration cases use the real subprocess/physics.
"""
import base64
from copy import deepcopy
import json
from pathlib import Path
import shutil
import zipfile

import pytest

from cevns_pyeft.experiments import management as manager
from cevns_pyeft.experiments.registry_io import (REGISTRY, ManagementError, encoded,
                                               hash_bytes, read_registry, validate_registry)

REPO=Path(__file__).resolve().parents[1]


@pytest.fixture
def root(tmp_path):
    target=tmp_path/'managed'
    target.mkdir()
    for name in ('cevns_pyeft','data','configs'):
        shutil.copytree(REPO/name,target/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (target/'README.md').write_text(
        '# Manual explanation\n\n[CsI definition](cevns_pyeft/experiments/coherent/csi2021_definition.py)\n'
        '[Ar definition](cevns_pyeft/experiments/coherent/ar2020_definition.py)\n',encoding='utf-8')
    return target


def snapshot(root):
    return {p.relative_to(root).as_posix():p.read_bytes()
            for area in ('cevns_pyeft','data','configs') for p in (root/area).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts} | {'README.md':(root/'README.md').read_bytes()}


@pytest.fixture
def fast_probe(monkeypatch):
    def probe(root,requested=()):
        data=read_registry(root)
        names=[e['dataset_id'] for e in data['datasets'] if e['installed'] and e['status']=='active']
        names+=list(requested)
        return {sid:{'counts':[float(len(sid))],'shape':[1],'unit':'events/bin','chi2':0.}
                for sid in dict.fromkeys(names)}
    monkeypatch.setattr(manager,'_probe',probe)


def test_list_show_audit_and_plan_are_read_only(root):
    before=snapshot(root)
    assert [r['dataset_id'] for r in manager.describe(root)]==['CsI2021','CsI2017','Ar2020']
    show=manager.describe(root,'csi2021')
    assert show['installed'] and show['owned_files'] and show['shared_dependencies']
    assert manager.audit(root)['status']=='PASS'
    plan=manager.make_plan(root,'uninstall','CsI2021')
    assert any(c['operation']=='delete' for c in plan['changes'])
    assert snapshot(root)==before
    assert not (root/'backup').exists() and not (root/'outputs').exists()


def test_uninstall_removes_only_owned_files_and_updates_navigation(root,fast_probe):
    owned=manager.describe(root,'CsI2021')['owned_files']
    shared=root/'data/responses/responses_all.json';shared_bytes=shared.read_bytes()
    unrelated=root/'data/experiments/COHERENT_CsI/CsI2021/private_note.txt'
    unrelated.write_text('user-owned note',encoding='utf-8')
    result=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    assert result['status']=='COMMITTED'
    assert all(not (root/r['path']).exists() for r in owned)
    assert shared.read_bytes()==shared_bytes and unrelated.read_text('utf-8')=='user-owned note'
    entry=manager.describe(root,'CsI2021')
    assert entry['installed'] is False and entry['status']=='archived'
    assert 'dataset-link:' in (root/'README.md').read_text('utf-8')
    assert '未安装' in (root/'README.md').read_text('utf-8')
    assert Path(result['reinstall_package']['package']).is_file()
    assert (root/'backup/BACKUP_MANIFEST.md').is_file()
    assert manager.audit(root)['status']=='PASS'


def test_export_install_archive_activate_and_rollback_restore_exact_bytes(root,fast_probe,tmp_path):
    before=snapshot(root)
    exported=manager.export_package(root,'CsI2021',tmp_path/'csi.zip')
    removal=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    installed=manager.apply_plan(manager.make_plan(root,'install',package=exported['package']))
    assert manager.describe(root,'CsI2021')['status']=='archived'
    resources=json.loads((root/'data/resource_manifest.json').read_text('utf-8'))['resources']
    assert all(r['dataset_id']!='CsI2021' for r in resources)
    assert 'dataset-link:' not in (root/'README.md').read_text('utf-8')
    activation=manager.apply_plan(manager.make_plan(root,'activate','CsI2021'))
    assert manager.describe(root,'CsI2021')['status']=='active'
    manager.rollback(root,activation['transaction_id'])
    manager.rollback(root,installed['transaction_id'])
    manager.rollback(root,removal['transaction_id'])
    assert snapshot(root)==before


def test_failed_rollback_validation_restores_the_post_operation_state(root,fast_probe,monkeypatch):
    result=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    before=snapshot(root)
    def fail(*args,**kwargs):raise ManagementError('simulated validation environment failure')
    monkeypatch.setattr(manager,'_probe',fail)
    with pytest.raises(ManagementError,match='ROLLBACK_FAILED_POST_STATE_RESTORED'):
        manager.rollback(root,result['transaction_id'])
    assert snapshot(root)==before


def test_automatic_failure_rollback_is_complete(root,fast_probe,monkeypatch):
    before=snapshot(root);original=manager._atomic;failed=False
    def interrupted(path,content):
        nonlocal failed
        if path==root/REGISTRY and not failed:
            failed=True
            raise OSError('simulated write failure after owned module removals')
        original(path,content)
    monkeypatch.setattr(manager,'_atomic',interrupted)
    with pytest.raises(ManagementError,match='FAILED_ROLLED_BACK'):
        manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    assert failed and snapshot(root)==before
    journals=list((root/'outputs/dataset-management/transactions').glob('*/journal.json'))
    assert len(journals)==1 and json.loads(journals[0].read_text('utf-8'))['status']=='FAILED_ROLLED_BACK'
    assert not (root/'outputs/dataset-management/operation.lock').exists()


def test_stale_plan_and_edited_plan_do_not_apply(root,fast_probe):
    plan=manager.make_plan(root,'uninstall','CsI2021')
    path=root/'cevns_pyeft/experiments/coherent/csi2021_definition.py'
    path.write_bytes(path.read_bytes()+b'\n# local edit\n')
    before=snapshot(root)
    with pytest.raises(ManagementError,match='stale'):manager.apply_plan(plan)
    assert snapshot(root)==before
    plan=manager.make_plan(root,'uninstall','CsI2021')
    plan['changes'][0]['content_b64']=base64.b64encode(b'edited plan').decode()
    with pytest.raises(ManagementError,match='edited'):manager.apply_plan(plan)
    assert snapshot(root)==before


def test_rollback_refuses_later_user_edits_without_partial_restore(root,fast_probe):
    result=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    path=root/'cevns_pyeft/experiments/coherent/csi2021_definition.py'
    path.write_text('# later unrelated user content\n',encoding='utf-8')
    before=snapshot(root)
    with pytest.raises(ManagementError,match='later edits'):manager.rollback(root,result['transaction_id'])
    assert snapshot(root)==before


def test_backup_hash_is_checked_before_restoring_any_file(root,fast_probe):
    result=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    journal=json.loads(Path(result['journal']).read_text('utf-8'))
    backup=root/next(r['backup'] for r in journal['files'] if r.get('backup'))
    backup.write_bytes(b'corrupted backup')
    before=snapshot(root)
    with pytest.raises(ManagementError,match='backup content changed'):manager.rollback(root,result['transaction_id'])
    assert snapshot(root)==before


def test_required_dataset_and_eager_import_consumers_block_removal(root):
    payload=read_registry(root)
    payload['datasets'][1]['requires_datasets']=['CsI2021']
    (root/REGISTRY).write_bytes(encoded(payload))
    with pytest.raises(ManagementError,match='depend'):manager.make_plan(root,'uninstall','CsI2021')
    payload['datasets'][1]['requires_datasets']=[]
    (root/REGISTRY).write_bytes(encoded(payload))
    consumer=root/'cevns_pyeft/bad_consumer.py'
    consumer.write_text('from cevns_pyeft.experiments.coherent.csi2021_definition import DEFINITION\n',encoding='utf-8')
    with pytest.raises(ManagementError,match='eager code consumers'):manager.make_plan(root,'uninstall','CsI2021')


@pytest.mark.parametrize("path", ["../escape.py", "/absolute.py", "C:/outside.py", "cevns_pyeft/cli.py", "data/responses/responses_all.json"])
def test_unsafe_or_shared_owned_paths_are_rejected(root,path):
    payload=read_registry(root)
    payload['datasets'][0]['owned_files'].append({'path':path,'role':'code'})
    with pytest.raises(ManagementError):validate_registry(payload)


def test_duplicate_ownership_aliases_and_dependency_cycles_are_rejected(root):
    payload=read_registry(root)
    bad=deepcopy(payload);bad['datasets'][1]['owned_files'].append(bad['datasets'][0]['owned_files'][0])
    with pytest.raises(ManagementError,match='multiply owned'):validate_registry(bad)
    bad=deepcopy(payload);bad['datasets'][1]['aliases'].append('csi2021')
    with pytest.raises(ManagementError,match='duplicate'):validate_registry(bad)
    bad=deepcopy(payload);bad['datasets'][0]['requires_datasets']=['CsI2017'];bad['datasets'][1]['requires_datasets']=['CsI2021']
    with pytest.raises(ManagementError,match='cycle'):validate_registry(bad)


def test_pinned_dataset_dependency_version_is_checked(root):
    payload=read_registry(root)
    payload['datasets'][1]['requires_datasets']=['CsI2021']
    payload['datasets'][1]['required_dataset_versions']={'CsI2021':'999.0.0'}
    (root/REGISTRY).write_bytes(encoded(payload))
    assert manager.audit(root)['status']=='FAIL'
    with pytest.raises(ManagementError,match='version mismatch'):manager.make_plan(root,'activate','CsI2017')


def rewrite_bundle(package,destination,mutate_manifest=None,mutate_payload=None,extra=None):
    with zipfile.ZipFile(package) as archive:items={name:archive.read(name) for name in archive.namelist()}
    if mutate_manifest:
        value=json.loads(items['manifest.json']);mutate_manifest(value);items['manifest.json']=encoded(value)
    if mutate_payload:
        name=next(name for name in items if name.startswith('payload/'))
        items[name]=mutate_payload(items[name])
    if extra:items.update(extra)
    with zipfile.ZipFile(destination,'x') as archive:
        for name,content in items.items():archive.writestr(name,content)
    return destination


def test_tampered_incompatible_and_extra_member_packages_are_rejected(root,tmp_path):
    package=Path(manager.export_package(root,'CsI2021',tmp_path/'good.zip')['package'])
    bad=rewrite_bundle(package,tmp_path/'bad_hash.zip',mutate_payload=lambda raw:raw+b'\nchanged')
    with pytest.raises(ManagementError,match='hash mismatch'):manager.read_package(bad)
    bad=rewrite_bundle(package,tmp_path/'bad_api.zip',mutate_manifest=lambda m:m.update(core_api_version=999))
    with pytest.raises(ManagementError,match='incompatible'):manager.read_package(bad)
    bad=rewrite_bundle(package,tmp_path/'bad_member.zip',extra={'../escape.txt':b'x'})
    with pytest.raises(ManagementError,match='ZIP member'):manager.read_package(bad)


def test_changed_package_and_shared_core_reject_saved_install_plan(root,fast_probe,tmp_path):
    package=Path(manager.export_package(root,'CsI2021',tmp_path/'good.zip')['package'])
    manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    plan=manager.make_plan(root,'install',package=package)
    shared=root/'cevns_pyeft/targets/materials.py'
    shared.write_bytes(shared.read_bytes()+b'\n# newer API implementation\n')
    with pytest.raises(ManagementError,match='shared dependency'):manager.apply_plan(plan)


def test_install_will_not_overwrite_an_existing_or_user_created_file(root,fast_probe,tmp_path):
    package=manager.export_package(root,'CsI2021',tmp_path/'good.zip')['package']
    with pytest.raises(ManagementError,match='already installed'):manager.make_plan(root,'install',package=package)
    manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    path=root/'cevns_pyeft/experiments/coherent/csi2021_definition.py'
    path.write_text('user content',encoding='utf-8')
    with pytest.raises(ManagementError,match='overwrite'):manager.make_plan(root,'install',package=package)
    assert path.read_text('utf-8')=='user content'


def test_multiple_removals_keep_other_navigation_markers(root,fast_probe):
    manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    removed=manager.apply_plan(manager.make_plan(root,'uninstall','Ar2020'))
    assert (root/'README.md').read_text('utf-8').count('dataset-link:')==2
    package=removed['reinstall_package']['package']
    manager.apply_plan(manager.make_plan(root,'install',package=package,activate=True))
    text=(root/'README.md').read_text('utf-8')
    assert text.count('dataset-link:')==1 and '[Ar definition]' in text


def test_operation_lock_and_duplicate_export_are_explicit(root,fast_probe,tmp_path):
    package=tmp_path/'good.zip';manager.export_package(root,'CsI2021',package)
    with pytest.raises(ManagementError,match='output exists'):manager.export_package(root,'CsI2021',package)
    with manager._lock(root):
        with pytest.raises(ManagementError,match='operation.lock'):
            manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))


def test_recover_pending_transaction_and_refuse_live_owner(root,fast_probe,monkeypatch):
    before=snapshot(root)
    removal=manager.apply_plan(manager.make_plan(root,'uninstall','CsI2021'))
    path=Path(removal['journal']);journal=json.loads(path.read_text('utf-8'))
    journal['status']='PREPARED';path.write_bytes(encoded(journal))
    lock=root/'outputs/dataset-management/operation.lock'
    lock.write_bytes(encoded({'pid':123456,'transaction_id':removal['transaction_id']}))
    monkeypatch.setattr(manager,'_pid_running',lambda pid:True)
    with pytest.raises(ManagementError,match='owner process'):manager.recover(root,removal['transaction_id'])
    assert lock.exists()
    monkeypatch.setattr(manager,'_pid_running',lambda pid:False)
    assert manager.recover(root,removal['transaction_id'])['status']=='ROLLED_BACK'
    assert snapshot(root)==before
    assert manager.history(root)[0]['status']=='ROLLED_BACK'


@pytest.mark.parametrize('sid',['CsI2021','CsI2017','Ar2020'])
def test_real_uninstall_reinstall_and_reverse_rollback_keep_other_experiments_working(root,sid):
    before=snapshot(root)
    removal=manager.apply_plan(manager.make_plan(root,'uninstall',sid))
    assert removal['status']=='COMMITTED'
    installation=manager.apply_plan(manager.make_plan(root,'install',package=removal['reinstall_package']['package'],activate=True))
    assert manager.describe(root,sid)['installed'] is True
    manager.rollback(root,installation['transaction_id'])
    manager.rollback(root,removal['transaction_id'])
    assert snapshot(root)==before
