"""Dataset packages: inspect, export, plan, transact, validate and roll back.

Management is explicit and filesystem-based. The runtime registry remains the
only lifecycle authority. Ordinary predictions never import this module.
"""
from __future__ import annotations
import ast
import base64
from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
import zipfile

from .registry_io import (CORE_API_VERSION, CRITICAL, REGISTRY, ManagementError,
                         encoded, find_entry, hash_bytes, parse_json, read_registry,
                         relative_path, safe_path, validate_registry)

INDEX = 'cevns_pyeft/experiments/DATASETS.md'
RESOURCE_MANIFEST = 'data/resource_manifest.json'
PROTECTED = 'tools/workflow_validation/config/PROTECTED_FILES.json'
AREA = 'outputs/dataset-management'
EXCLUDED = {'backup','outputs','.git','__pycache__','.pytest_cache','.pytest-tmp','.ipynb_checkpoints'}
LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)')
MANAGED_LINK = re.compile(r'<!-- dataset-link:([A-Za-z0-9_=-]+) -->.*?<!-- /dataset-link -->')


def _internal(root, relative):
    """Transaction paths may use backup/outputs, but never symlink or escape."""
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root) or path.resolve()!=path.absolute():
        raise ManagementError('internal path escapes managed root')
    current = path
    while current!=root:
        if current.is_symlink():raise ManagementError('symlink in transaction storage')
        current=current.parent
    return path


def _hash(root, name):
    path=safe_path(root,name)
    return hash_bytes(path.read_bytes()) if path.is_file() else None


def _atomic(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temp.open('xb') as stream:
            stream.write(content);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if temp.exists():temp.unlink()


def _top_imports(tree):
    for node in tree:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):continue
        if isinstance(node,(ast.Import,ast.ImportFrom)):yield node
        for child in ast.iter_child_nodes(node):
            if isinstance(child,ast.stmt):yield from _top_imports([child])


def eager_consumers(root, removed, ignored=()):
    modules={name[:-3].replace('/','.') for name in removed if name.endswith('.py')}
    result=[]
    package=Path(root)/'cevns_pyeft'
    for path in sorted(package.rglob('*.py')):
        name=path.relative_to(root).as_posix()
        if name in removed or name in ignored or '__pycache__' in path.parts:continue
        current=name[:-3].replace('/','.')
        context=current.removesuffix('.__init__') if path.name=='__init__.py' else current.rsplit('.',1)[0]
        try:tree=ast.parse(path.read_text('utf-8-sig'))
        except (SyntaxError,UnicodeError) as exc:raise ManagementError(f'cannot audit imports in {name}: {exc}') from exc
        for node in _top_imports(tree.body):
            if isinstance(node,ast.Import):targets=[a.name for a in node.names]
            else:
                target=('.'*node.level)+(node.module or '')
                target=importlib.util.resolve_name(target,context) if node.level else target
                targets=[target,*[target+'.'+a.name for a in node.names]]
            for target in sorted(set(targets)&modules):result.append({'path':name,'line':node.lineno,'imports':target})
    return result


def audit(root, payload=None):
    root=Path(root).resolve();payload=read_registry(root) if payload is None else validate_registry(payload)
    errors=[];owners={f['path']:e['dataset_id'] for e in payload['datasets'] for f in e['owned_files']}
    missing=set()
    for entry in payload['datasets']:
        if entry['installed']:
            for record in entry['owned_files']:
                if not safe_path(root,record['path']).is_file():errors.append('missing owned file: '+record['path'])
            for name in entry.get('shared_dependencies',[]):
                if not safe_path(root,name).is_file():errors.append('missing shared dependency: '+name)
                if name in owners:errors.append('shared dependency is owned by another package: '+name)
            for sid in entry.get('requires_datasets',[]):
                if not find_entry(payload,sid)['installed']:errors.append(f'{entry["dataset_id"]} requires uninstalled {sid}')
                version=entry.get('required_dataset_versions',{}).get(sid)
                if version and find_entry(payload,sid)['package_version']!=version:
                    errors.append(f'{entry["dataset_id"]} requires {sid} version {version}')
        else:missing.update(f['path'] for f in entry['owned_files'])
    consumers=eager_consumers(root,missing)
    errors.extend(f'eager consumer of uninstalled module: {x}' for x in consumers)
    resource_file=safe_path(root,RESOURCE_MANIFEST)
    if resource_file.exists():
        resources=parse_json(resource_file.read_text('utf-8'))['resources'];seen=set()
        active={e['dataset_id']:e for e in payload['datasets'] if e['installed'] and e['status']=='active'}
        for record in resources:
            key=(record['dataset_id'],record['resource_id'])
            if key in seen:errors.append('duplicate resource manifest entry: '+str(key))
            seen.add(key)
            if record['dataset_id'] not in active:errors.append('non-active dataset in active resource manifest: '+record['dataset_id'])
            name=record['canonical_path']
            if _hash(root,name)!=record['sha256']:errors.append('resource hash mismatch: '+name)
        for sid,entry in active.items():
            expected={(sid,r['resource_id']) for r in entry.get('resource_entries',[])}
            if expected and {key for key in seen if key[0]==sid}!=expected:
                errors.append('active resource registration mismatch: '+sid)
    return {'status':'FAIL' if errors else 'PASS','errors':errors,'dataset_count':len(payload['datasets']),
            'installed_ids':[e['dataset_id'] for e in payload['datasets'] if e['installed']],
            'active_ids':[e['dataset_id'] for e in payload['datasets'] if e['installed'] and e['status']=='active'],
            'dependency_audit':'declared package/shared dependencies and eager static imports; fresh-process validation supplements dynamic imports'}


def describe(root, dataset=None):
    payload=read_registry(root)
    if dataset is None:
        return [{'dataset_id':e['dataset_id'],'experiment_slug':e['experiment_slug'],'status':e['status'],
                 'installed':e['installed'],'package_version':e['package_version'],'definition':e['definition'],
                 'owned_files':len(e['owned_files']),'capabilities':e.get('capabilities',[])} for e in payload['datasets']]
    entry=deepcopy(find_entry(payload,dataset))
    entry['reverse_dependencies']=[e['dataset_id'] for e in payload['datasets'] if entry['dataset_id'] in e.get('requires_datasets',[])]
    entry['eager_code_consumers']=eager_consumers(root,{f['path'] for f in entry['owned_files']})
    return entry


def export_package(root, dataset, output):
    root=Path(root).resolve();payload=read_registry(root);entry=find_entry(payload,dataset)
    if not entry['installed']:raise ManagementError('cannot export an uninstalled dataset')
    output=Path(output).resolve()
    if output.exists():raise ManagementError('package output exists; choose a new path')
    files=[];contents={}
    for record in entry['owned_files']:
        content=safe_path(root,record['path']).read_bytes()
        files.append({**record,'sha256':hash_bytes(content),'bytes':len(content)})
        contents['payload/'+record['path']]=content
    resources=[]
    resource_file=safe_path(root,RESOURCE_MANIFEST)
    if 'resource_entries' in entry:
        resources=deepcopy(entry['resource_entries'])
    elif resource_file.exists():
        resources=[r for r in parse_json(resource_file.read_text('utf-8'))['resources'] if r['dataset_id']==entry['dataset_id']]
    shared={name:_hash(root,name) for name in entry.get('shared_dependencies',[])}
    if any(value is None for value in shared.values()):raise ManagementError('shared dependency missing during export')
    manifest={'bundle_schema_version':1,'core_api_version':CORE_API_VERSION,'entry':entry,
              'files':files,'shared_dependencies':shared,'resources':resources,
              'integrity_scope':'SHA256 integrity and API compatibility; not a scientific approval or a publisher signature.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json',encoded(manifest))
        for name,content in contents.items():archive.writestr(name,content)
    return {'package':str(output),'sha256':hash_bytes(output.read_bytes()),'dataset_id':entry['dataset_id'],'files':len(files)}


def read_package(package):
    package=Path(package).resolve();content=package.read_bytes()
    if len(content)>1024**3:raise ManagementError('package exceeds 1 GiB compressed limit')
    with zipfile.ZipFile(package) as archive:
        infos=archive.infolist();names=[i.filename for i in infos]
        if len(names)!=len(set(names)) or sum(i.file_size for i in infos)>2*1024**3:
            raise ManagementError('duplicate members or package exceeds 2 GiB extracted limit')
        if any((i.external_attr>>16)&0o170000==0o120000 for i in infos):raise ManagementError('symlink ZIP member')
        manifest=parse_json(archive.read('manifest.json').decode('utf-8'))
        if manifest.get('bundle_schema_version')!=1 or manifest.get('core_api_version')!=CORE_API_VERSION:
            raise ManagementError('incompatible dataset package/API')
        entry=manifest['entry'];records=manifest['files'];paths=[r['path'] for r in records]
        if len(paths)!=len(set(paths)) or set(paths)!={r['path'] for r in entry['owned_files']}:
            raise ManagementError('package ownership/file list mismatch')
        expected={'manifest.json',*['payload/'+relative_path(p) for p in paths]}
        if set(names)!=expected:raise ManagementError('unexpected/missing ZIP member')
        files={}
        for record in records:
            raw=archive.read('payload/'+record['path'])
            if len(raw)!=record['bytes'] or hash_bytes(raw)!=record['sha256']:
                raise ManagementError('package content hash mismatch: '+record['path'])
            files[record['path']]=raw
    return manifest,files,hash_bytes(content)


def _documents(root):
    for area in ['cevns_pyeft','data','docs','examples','tests','tools','workflows']:
        start=Path(root)/area
        if not start.exists():continue
        for current,dirs,files in os.walk(start):
            dirs[:]=[d for d in dirs if d not in EXCLUDED]
            for name in sorted(files):
                path=Path(current)/name
                if name.endswith('.md') and not path.is_symlink():yield path
    path=Path(root)/'README.md'
    if path.exists():yield path


def _index(root,payload,writes,deletes):
    lines=['# Dataset 注册、安装状态与文件归属','','本表由唯一 dataset_registry.json 生成；管理操作在同一事务中同步。',
           'installed 与 active 分别表示文件是否安装、是否可默认加载。科学输入与能力的批准由原接入流程管理。','',
           '| 实验分组 | dataset ID | 状态 | 已安装 | 版本 | definition | 独占文件 |', '|---|---|---|---|---|---|---|']
    for entry in payload['datasets']:
        name='cevns_pyeft/experiments/'+entry['definition'].replace('.','/')+'.py'
        label='`'+entry['definition']+'`'
        if entry['installed']:label='['+entry['definition']+']('+os.path.relpath(root/name,(root/INDEX).parent).replace('\\','/')+')'
        lines.append('| '+' | '.join([entry['experiment_slug'],entry['dataset_id'],entry['status'],str(entry['installed']),entry['package_version'],label,str(len(entry['owned_files']))])+' |')
    lines+=['','## 各实验的文件与共享依赖','']
    for entry in payload['datasets']:
        lines+=['### '+entry['dataset_id'],'','独占文件：','']
        for record in entry['owned_files']:
            name=record['path'];label='`'+name+'`'
            if entry['installed']:label='['+name+']('+os.path.relpath(root/name,(root/INDEX).parent).replace('\\','/')+')'
            lines.append('- '+label+' — '+record.get('role','input'))
        lines+=['','共享依赖（卸载本项时保留）：','']
        lines.extend('- `'+name+'`' for name in entry.get('shared_dependencies',[]))
        lines+=['','依赖的其他 dataset：'+(', '.join(entry.get('requires_datasets',[])) or '无')+'。','']
    lines+=['[管理命令与恢复](MANAGEMENT.md) · [实验代码说明](README.md)','']
    return '\n'.join(lines).encode('utf-8')


def _sync_links(root,writes,deletes):
    """Retain original links in reversible markers when their files disappear."""
    def exists(path):
        try:name=path.resolve().relative_to(root).as_posix()
        except ValueError:return path.exists()
        if name in writes:return True
        if name in deletes:return False
        if path.is_dir():
            if any(p.startswith(name+'/') for p in writes):return True
            for current,dirs,files in os.walk(path):
                dirs[:]=[d for d in dirs if d not in EXCLUDED]
                if any((Path(current)/p).relative_to(root).as_posix() not in deletes for p in files):return True
            return False
        return path.exists()
    for path in _documents(root):
        name=path.relative_to(root).as_posix()
        if name in deletes or name==INDEX:continue
        before=path.read_bytes();text=writes.get(name,before).decode('utf-8')
        def restore(match):
            try:raw=base64.urlsafe_b64decode(match[1]).decode('utf-8')
            except (ValueError,UnicodeError):raise ManagementError('invalid dataset-link marker: '+name)
            parsed=LINK.fullmatch(raw)
            if parsed:
                from urllib.parse import unquote
                target=unquote(parsed[2].strip().strip('<>').split('#',1)[0])
                if exists((path.parent/target).resolve()):return raw
            return match[0]
        text=MANAGED_LINK.sub(restore,text)
        lines=[];fence=None
        for line in text.splitlines(keepends=True):
            marker=re.match(r'^\s*(`{3,}|~{3,})',line)
            if marker:
                if fence is None:fence=marker[1][0]
                elif fence==marker[1][0]:fence=None
                lines.append(line);continue
            if fence is not None:lines.append(line);continue
            def update(match):
                target=match[2].strip().strip('<>')
                if re.match(r'^(?:[a-z]+:|#)',target,re.I):return match[0]
                from urllib.parse import unquote
                target=unquote(target.split('#',1)[0])
                dest=(path.parent/target).resolve()
                if not dest.is_relative_to(root) or exists(dest):return match[0]
                # Only links affected by this operation; pre-existing unrelated errors are reported separately.
                if not any(dest==root/p or (root/p).is_relative_to(dest) for p in deletes):return match[0]
                token=base64.urlsafe_b64encode(match[0].encode('utf-8')).decode('ascii')
                return '<!-- dataset-link:'+token+' -->'+match[1]+'（该 dataset 未安装）<!-- /dataset-link -->'
            lines.append(LINK.sub(update,line))
        after=''.join(lines).encode('utf-8')
        if after!=before:writes[name]=after


def make_plan(root,action,dataset=None,package=None,activate=False):
    root=Path(root).resolve();old=read_registry(root);new=deepcopy(old)
    if action not in {'uninstall','install','archive','activate'}:raise ManagementError('unsupported action')
    writes={};deletes=set();bundle_hash=None;package_path=None
    old_entry=None
    if action=='install':
        if package is None:raise ManagementError('install requires a package')
        package_path=str(Path(package).resolve());bundle,files,bundle_hash=read_package(package_path)
        entry=deepcopy(bundle['entry']);dataset=entry['dataset_id']
        records=bundle.get('resources',[])
        if not isinstance(records,list) or any(r.get('dataset_id')!=dataset for r in records):
            raise ManagementError('package resources must belong to the selected dataset')
        keys=[r.get('resource_id') for r in records]
        if any(not isinstance(k,str) or not k for k in keys) or len(keys)!=len(set(keys)):
            raise ManagementError('invalid/duplicate package resource IDs')
        for record in records:
            name=relative_path(record['canonical_path'])
            actual=hash_bytes(files[name]) if name in files else _hash(root,name)
            if actual!=record['sha256']:raise ManagementError('package resource integrity mismatch: '+name)
            if name not in files and name not in entry.get('shared_dependencies',[]):
                raise ManagementError('resource is neither owned nor a declared shared dependency: '+name)
        entry['resource_entries']=deepcopy(records)
        for previous in new['datasets']:
            if previous['dataset_id']==dataset:old_entry=previous;break
        if old_entry and old_entry['installed']:raise ManagementError('dataset already installed; uninstall or roll back explicitly first')
        if old_entry:new['datasets'].remove(old_entry)
        entry.update(installed=True,status='active' if activate else 'archived')
        new['datasets'].append(entry);validate_registry(new)
        for name,expected in bundle['shared_dependencies'].items():
            relative_path(name)
            if _hash(root,name)!=expected:raise ManagementError('shared dependency/API content mismatch: '+name)
        if set(bundle['shared_dependencies'])!=set(entry.get('shared_dependencies',[])):
            raise ManagementError('package shared-dependency declaration mismatch')
        for name,raw in files.items():
            if _hash(root,name) is not None:raise ManagementError('install would overwrite an existing file: '+name)
            writes[name]=raw
    else:
        entry=find_entry(new,dataset);dataset=entry['dataset_id'];old_entry=find_entry(old,dataset)
        if not entry['installed']:raise ManagementError('dataset is not installed')
        if action=='uninstall':
            reverse=[e['dataset_id'] for e in new['datasets'] if e['installed'] and dataset in e.get('requires_datasets',[])]
            if reverse:raise ManagementError('installed datasets depend on this package: '+', '.join(reverse))
            deletes={record['path'] for record in entry['owned_files']}
            for other in new['datasets']:
                if other['installed'] and other['dataset_id']!=dataset and deletes&set(other.get('shared_dependencies',[])):
                    raise ManagementError('cannot remove a declared shared dependency')
            consumers=eager_consumers(root,deletes)
            if consumers:raise ManagementError('eager code consumers must be migrated before uninstall: '+str(consumers))
            for name in deletes:
                if _hash(root,name) is None:raise ManagementError('owned file already missing: '+name)
            entry.update(installed=False,status='archived')
        else:
            entry['status']='active' if action=='activate' else 'archived'
    validate_registry(new)
    for item in new['datasets']:
        if item['installed']:
            for dependency in item.get('requires_datasets',[]):
                if not find_entry(new,dependency)['installed']:raise ManagementError('required dataset is not installed: '+dependency)
                version=item.get('required_dataset_versions',{}).get(dependency)
                if version and find_entry(new,dependency)['package_version']!=version:
                    raise ManagementError(f'required dataset version mismatch: {dependency} needs {version}')
    writes[REGISTRY]=encoded(new)
    resource_path=safe_path(root,RESOURCE_MANIFEST)
    if resource_path.exists():
        resources=parse_json(resource_path.read_text('utf-8'))
        if action in {'install','uninstall','archive','activate'}:
            resources['resources']=[r for r in resources['resources'] if r['dataset_id']!=dataset]
            if entry['installed'] and entry['status']=='active':
                resources['resources'].extend(entry.get('resource_entries',[]))
            writes[RESOURCE_MANIFEST]=encoded(resources)
    # Disable the entry in the default selection while it cannot load. Restore does not invent a prior selection.
    for path in (root/'configs').glob('*.yaml'):
        raw=path.read_text('utf-8')
        if action in {'archive','uninstall'}:
            pattern=r'(^\s*-\s*id:\s*[\'\"]?'+re.escape(dataset)+r'[\'\"]?\s*\n)(.*?)(?=^\s*-\s*id:|\Z)'
            def disable(match):return match[1]+re.sub(r'(?m)^(\s*enabled:\s*)true\s*$',r'\g<1>false',match[2])
            changed=re.sub(pattern,disable,raw,flags=re.M|re.S)
            if changed!=raw:writes[path.relative_to(root).as_posix()]=changed.encode('utf-8')
    writes[INDEX]=_index(root,new,writes,deletes)
    _sync_links(root,writes,deletes)
    protected=safe_path(root,PROTECTED)
    if protected.exists():
        baseline=parse_json(protected.read_text('utf-8'))
        areas=('cevns_pyeft/','data/','configs/','examples/','workflows/_shared/schemas/experiment-input/')
        for name in deletes:baseline['files'].pop(name,None)
        for name,raw in writes.items():
            if name in baseline['files'] or name.startswith(areas):baseline['files'][name]=hash_bytes(raw)
        writes[PROTECTED]=encoded(baseline)
    changes=[]
    for name in sorted(set(writes)|deletes):
        before=_hash(root,name);after=hash_bytes(writes[name]) if name in writes else None
        if before!=after:
            item={'path':name,'before':before,'after':after,'operation':'delete' if after is None else 'add' if before is None else 'modify'}
            if name in writes:item['content_b64']=base64.b64encode(writes[name]).decode('ascii')
            changes.append(item)
    inputs={REGISTRY:_hash(root,REGISTRY)}
    for item in old['datasets']:
        for name in {*(f['path'] for f in item['owned_files']),*item.get('shared_dependencies',[])}:inputs[name]=_hash(root,name)
    plan={'plan_version':1,'root':str(root),'action':action,'dataset_id':dataset,'package':package_path,
          'package_sha256':bundle_hash,'activate':bool(activate),'inputs':inputs,'changes':changes,
          'validation':'fresh-process imports, active Slow/statistics contracts, unaffected prediction equivalence; candidate install validated without activation'}
    plan['plan_id']=hash_bytes(encoded(plan))
    return plan


def plan_summary(plan):
    return {k:plan[k] for k in ('plan_id','action','dataset_id','validation')} | {
        'root':plan['root'],'changes':[{k:v for k,v in r.items() if k!='content_b64'} for r in plan['changes']],
        'execution':'read-only plan; no transaction applied'}


PROBE = r'''
import importlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG,ExperimentCatalog
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment
from cevns_pyeft.experiments.registry import list_runtime_experiment_ids
import cevns_pyeft.core.engine
import cevns_pyeft.statistics
assert tuple(list_runtime_experiment_ids())==BUILTIN_CATALOG.ids()
requested=json.loads(sys.argv[2]);ids=list(BUILTIN_CATALOG.ids())
for sid in requested:
    if sid not in ids:ids.append(sid)
result={}
for sid in ids:
    entry=BUILTIN_CATALOG.manifest_entry(sid)
    catalog=BUILTIN_CATALOG
    if entry.status!='active':
        catalog=ExperimentCatalog(builtins=False).register(sid,entry.definition,capabilities=entry.capabilities)
    definition=catalog.definition(sid)
    if 'slow' not in definition.numerical_profiles:raise ValueError('Slow contract required: '+sid)
    numerics={k:{'n_er':3,'n_enu':6,'n_pe_bin':2}.get(k,v) for k,v in definition.numerical_profiles['slow'].items()}
    experiment=load_experiment(sid,resources=ResourceCatalog(root),registry=catalog)
    prediction=predict_experiment(experiment,numerics=numerics)
    value={'counts':prediction.counts.tolist(),'shape':list(prediction.counts.shape),'unit':prediction.combined_prediction.unit}
    if definition.statistics is not None:value['chi2']=float(evaluate_experiment(experiment,prediction).chi2)
    result[sid]=value
print('DATASET_PROBE_JSON='+json.dumps(result,allow_nan=False))
'''


def _probe(root,requested=()):
    process=subprocess.run([sys.executable,'-I','-B','-c',PROBE,str(root),json.dumps(list(requested))],
                           cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=300)
    if process.returncode:
        raise ManagementError('fresh-process validation failed: '+(process.stderr or process.stdout)[-8000:])
    rows=[line for line in process.stdout.splitlines() if line.startswith('DATASET_PROBE_JSON=')]
    if len(rows)!=1:raise ManagementError('invalid validation subprocess result')
    return parse_json(rows[0].split('=',1)[1])


def _compare_unaffected(before,after,affected):
    import math
    for sid,expected in before.items():
        if sid==affected:continue
        if sid not in after:raise ManagementError('unrelated dataset disappeared: '+sid)
        actual=after[sid]
        if actual['shape']!=expected['shape'] or actual['unit']!=expected['unit']:
            raise ManagementError('unrelated observation changed: '+sid)
        for a,b in zip(actual['counts'],expected['counts']):
            if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12):raise ManagementError('unrelated prediction changed: '+sid)
        if 'chi2' in expected and not math.isclose(actual['chi2'],expected['chi2'],rel_tol=1e-12,abs_tol=1e-12):
            raise ManagementError('unrelated statistical evaluation changed: '+sid)


@contextmanager
def _lock(root):
    path=_internal(root,AREA+'/operation.lock');path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with path.open('x',encoding='utf-8') as stream:stream.write(json.dumps({'pid':os.getpid()}))
    except FileExistsError as exc:raise ManagementError('another management operation holds operation.lock') from exc
    try:yield
    finally:path.unlink()


def _restore(root,journal,*,check_after):
    # Check every path and every backup before changing any file.
    for item in journal['files']:
        path=safe_path(root,item['path'])
        actual=_hash(root,item['path'])
        if check_after and actual!=item['after']:
            raise ManagementError('rollback would overwrite later edits: '+item['path'])
        if not check_after and actual not in {item['before'],item['after']}:
            raise ManagementError('recovery would overwrite concurrent edits: '+item['path'])
        if item['before'] is not None:
            backup=_internal(root,item['backup'])
            if hash_bytes(backup.read_bytes())!=item['before']:raise ManagementError('backup content changed: '+item['path'])
    for item in reversed(journal['files']):
        path=safe_path(root,item['path'])
        if item['before'] is None:
            if path.exists():path.unlink()
        else:_atomic(path,_internal(root,item['backup']).read_bytes())
    _prune_empty_parents(root,[item['path'] for item in journal['files'] if item['before'] is None])


def _prune_empty_parents(root,names):
    """Remove empty directories only, after checked exact-file operations."""
    root=Path(root).resolve();removed=[]
    boundaries={root/p for p in ('cevns_pyeft/experiments','data/experiments','docs/experiments','tests')}
    for name in sorted(names,key=lambda p:p.count('/'),reverse=True):
        path=(root/relative_path(name)).parent
        while path!=root and path not in boundaries:
            if not any(path.is_relative_to(boundary) for boundary in boundaries):break
            if not path.resolve().is_relative_to(root) or path.is_symlink() or path.resolve()!=path.absolute():
                raise ManagementError('unsafe empty-directory cleanup target: '+str(path))
            if not path.exists():path=path.parent;continue
            try:path.rmdir()
            except OSError:break  # user files, other datasets and nonempty directories remain
            removed.append(path.relative_to(root).as_posix());path=path.parent
    return removed


def apply_plan(plan):
    root=Path(plan['root']).resolve()
    with _lock(root):
        expected=make_plan(root,plan['action'],plan['dataset_id'],plan.get('package'),plan.get('activate',False))
        if expected!=plan:raise ManagementError('plan is stale or was edited; create a new plan')
        before=_probe(root)
        txid=uuid.uuid4().hex
        txdir=_internal(root,AREA+'/transactions/'+txid);txdir.mkdir(parents=True,exist_ok=False)
        backup_root='backup/dataset-management/'+txid
        journal={'transaction_id':txid,'plan_id':plan['plan_id'],'action':plan['action'],'dataset_id':plan['dataset_id'],
                 'status':'PREPARING','files':[],'validation_before':before,'root':str(root),
                 'unchanged_inputs':{name:value for name,value in plan['inputs'].items()
                                     if name not in {r['path'] for r in plan['changes']}}}
        _atomic(txdir/'journal.json',encoded(journal))
        _atomic(_internal(root,AREA+'/operation.lock'),encoded({'pid':os.getpid(),'transaction_id':txid}))
        for item in plan['changes']:
            record={k:v for k,v in item.items() if k!='content_b64'}
            if item['before'] is not None:
                saved=_internal(root,backup_root+'/'+item['path']);saved.parent.mkdir(parents=True,exist_ok=True)
                with saved.open('xb') as stream:stream.write(safe_path(root,item['path']).read_bytes())
                record['backup']=saved.relative_to(root).as_posix()
            journal['files'].append(record)
        manifest=_internal(root,'backup/BACKUP_MANIFEST.md');manifest.parent.mkdir(parents=True,exist_ok=True)
        with manifest.open('a',encoding='utf-8') as stream:
            stream.write('\n\n## Dataset transaction '+txid+'\n\n')
            for item in journal['files']:
                if item.get('backup'):stream.write(f"- `{item['path']}` → `{item['backup']}`; SHA256 `{item['before']}`.\n")
        if plan['action']=='uninstall':
            journal['reinstall_package']=export_package(root,plan['dataset_id'],txdir/'reinstall.zip')
        journal['status']='PREPARED';_atomic(txdir/'journal.json',encoded(journal));_atomic(txdir/'plan.json',encoded(plan))
        try:
            for item in plan['changes']:
                if _hash(root,item['path'])!=item['before']:raise ManagementError('file changed before write: '+item['path'])
                path=safe_path(root,item['path'])
                if item['after'] is None:path.unlink()
                else:_atomic(path,base64.b64decode(item['content_b64']))
            journal['pruned_empty_directories']=_prune_empty_parents(root,[item['path'] for item in plan['changes'] if item['after'] is None])
            _atomic(txdir/'journal.json',encoded(journal))
            result=audit(root)
            if result['errors']:raise ManagementError('post-operation audit failed: '+str(result['errors']))
            requested=[plan['dataset_id']] if plan['action']=='install' else []
            after=_probe(root,requested)
            _compare_unaffected(before,after,plan['dataset_id'])
            journal.update(status='COMMITTED',validation_after=after,audit_after=result)
        except BaseException as exc:
            journal['error']=str(exc)
            try:_restore(root,journal,check_after=False);journal['status']='FAILED_ROLLED_BACK'
            except BaseException as recovery:
                journal.update(status='RECOVERY_REQUIRED',recovery_error=str(recovery))
            _atomic(txdir/'journal.json',encoded(journal))
            raise ManagementError(f'{journal["status"]}; transaction {txid}: {exc}') from exc
        _atomic(txdir/'journal.json',encoded(journal))
        return {'status':journal['status'],'transaction_id':txid,'journal':str(txdir/'journal.json'),
                'reinstall_package':journal.get('reinstall_package'),'changed_files':len(journal['files']),
                'validation':journal.get('audit_after'),'reload_required_for_existing_processes':True}


def rollback(root,txid):
    root=Path(root).resolve()
    if not re.fullmatch(r'[0-9a-f]{32}',txid):raise ManagementError('invalid transaction ID')
    path=_internal(root,AREA+'/transactions/'+txid+'/journal.json')
    with _lock(root):
        journal=parse_json(path.read_text('utf-8'))
        if journal['root']!=str(root) or journal['transaction_id']!=txid:
            raise ManagementError('transaction root/identity mismatch')
        if journal['status'] not in {'COMMITTED','PREPARED','RECOVERY_REQUIRED','ROLLING_BACK'}:
            raise ManagementError('transaction is not rollbackable: '+journal['status'])
        for name,expected in journal.get('unchanged_inputs',{}).items():
            if _hash(root,name)!=expected:raise ManagementError('rollback dependency changed: '+name)
        # Validate the old backups and target preconditions before saving or writing rollback images.
        for item in journal['files']:
            actual=_hash(root,item['path'])
            if journal['status']=='COMMITTED' and actual!=item['after']:
                raise ManagementError('rollback would overwrite later edits: '+item['path'])
            if item['before'] is not None and hash_bytes(_internal(root,item['backup']).read_bytes())!=item['before']:
                raise ManagementError('backup content changed: '+item['path'])
        inverse={'files':[]};attempt=uuid.uuid4().hex
        for item in journal['files']:
            actual=_hash(root,item['path'])
            record={'path':item['path'],'before':actual,'after':item['before']}
            if actual is not None:
                saved=_internal(root,'backup/dataset-management/'+txid+'/rollback-'+attempt+'/'+item['path'])
                saved.parent.mkdir(parents=True,exist_ok=True)
                with saved.open('xb') as stream:stream.write(safe_path(root,item['path']).read_bytes())
                record['backup']=saved.relative_to(root).as_posix()
            inverse['files'].append(record)
        manifest=_internal(root,'backup/BACKUP_MANIFEST.md')
        with manifest.open('a',encoding='utf-8') as stream:
            stream.write('\n\n## Dataset rollback attempt '+attempt+'\n\n')
            for item in inverse['files']:
                if item.get('backup'):stream.write(f"- `{item['path']}` → `{item['backup']}`; SHA256 `{item['before']}`.\n")
        previous_status=journal['status']
        journal['rollback_preimages']=inverse
        journal['status']='ROLLING_BACK'
        journal['pre_rollback_status']=previous_status
        _atomic(path,encoded(journal))
        _atomic(_internal(root,AREA+'/operation.lock'),encoded({'pid':os.getpid(),'transaction_id':txid}))
        try:
            _restore(root,journal,check_after=previous_status=='COMMITTED')
            audit_result=audit(root)
            if audit_result['errors']:raise ManagementError('rollback audit failed: '+str(audit_result['errors']))
            restored=_probe(root)
            _compare_unaffected(journal['validation_before'],restored,'')
        except BaseException as exc:
            try:
                _restore(root,inverse,check_after=False)
                journal['rollback_error']=str(exc)
                journal['status']=previous_status
                outcome='ROLLBACK_FAILED_POST_STATE_RESTORED'
            except BaseException as recovery:
                journal.update(status='RECOVERY_REQUIRED',rollback_error=str(exc),recovery_error=str(recovery))
                outcome='RECOVERY_REQUIRED'
            _atomic(path,encoded(journal))
            raise ManagementError(outcome+': '+str(exc)) from exc
        journal.update(status='ROLLED_BACK',rollback_validation=restored)
        _atomic(path,encoded(journal))
    return {'status':'ROLLED_BACK','transaction_id':txid,'validation':audit_result,
            'reload_required_for_existing_processes':True}


def refresh_index(root):
    """Explicit maintainer operation for a registry edit, independent of physics."""
    root=Path(root).resolve();payload=read_registry(root)
    _atomic(safe_path(root,INDEX),_index(root,payload,{},set()))


def history(root):
    root=Path(root).resolve();directory=_internal(root,AREA+'/transactions')
    result=[]
    for path in sorted(directory.glob('*/journal.json')):
        record=parse_json(_internal(root,path.relative_to(root).as_posix()).read_text('utf-8'))
        result.append({key:record.get(key) for key in ('transaction_id','dataset_id','action','status','error','rollback_error')})
    return result


def _pid_running(pid):
    if type(pid) is not int or pid<=0:raise ManagementError('invalid lock PID')
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:return ctypes.get_last_error()!=87  # access denied is not proof of death
        try:
            code=wintypes.DWORD()
            kernel.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
            if not kernel.GetExitCodeProcess(handle,ctypes.byref(code)):return True
            return code.value==259
        finally:
            kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle(handle)
    try:os.kill(pid,0)
    except ProcessLookupError:return False
    except PermissionError:return True
    return True


def recover(root,txid):
    """Recover an interrupted exact transaction; never break a live process lock."""
    root=Path(root).resolve()
    if not re.fullmatch(r'[0-9a-f]{32}',txid):raise ManagementError('invalid transaction ID')
    journal_path=_internal(root,AREA+'/transactions/'+txid+'/journal.json')
    journal=parse_json(journal_path.read_text('utf-8'))
    if journal['root']!=str(root) or journal['transaction_id']!=txid:raise ManagementError('transaction root/identity mismatch')
    lock=_internal(root,AREA+'/operation.lock')
    if lock.exists():
        owner=parse_json(lock.read_text('utf-8'))
        if owner.get('transaction_id') not in (None,txid):raise ManagementError('lock belongs to another transaction')
        if _pid_running(owner.get('pid')):raise ManagementError('cannot recover while the owner process is running')
        lock.unlink()
    if journal['status'] in {'PREPARED','RECOVERY_REQUIRED','ROLLING_BACK'}:return rollback(root,txid)
    if journal['status']=='PREPARING':
        with _lock(root):
            journal['status']='ABORTED_NO_WRITES';_atomic(journal_path,encoded(journal))
    return {'transaction_id':txid,'status':journal['status'],'audit':audit(root),
            'recovery':'completed/no-write transactions are not undone; use rollback explicitly for a committed transaction'}


def cli(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2],help='managed code/resource root, containing cevns_pyeft/ and data/')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list');sub.add_parser('history');show=sub.add_parser('show');show.add_argument('dataset')
    sub.add_parser('audit')
    export=sub.add_parser('export');export.add_argument('dataset');export.add_argument('--output',type=Path,required=True)
    for action in ('uninstall','archive','activate','install'):
        cmd=sub.add_parser(action);cmd.add_argument('subject');cmd.add_argument('--apply',action='store_true')
        cmd.add_argument('--plan',type=Path,help='save exact read-only plan to a new file')
        if action=='install':cmd.add_argument('--activate',action='store_true',help='explicitly register installed definition as active')
    apply=sub.add_parser('apply');apply.add_argument('plan',type=Path)
    undo=sub.add_parser('rollback');undo.add_argument('transaction_id')
    recovery=sub.add_parser('recover');recovery.add_argument('transaction_id')
    args=parser.parse_args(argv);root=args.root.resolve()
    try:
        if args.command=='list':result=describe(root)
        elif args.command=='history':result=history(root)
        elif args.command=='show':result=describe(root,args.dataset)
        elif args.command=='audit':result=audit(root)
        elif args.command=='export':result=export_package(root,args.dataset,args.output)
        elif args.command=='rollback':result=rollback(root,args.transaction_id)
        elif args.command=='recover':result=recover(root,args.transaction_id)
        elif args.command=='apply':
            plan=parse_json(args.plan.read_text('utf-8'))
            if plan['root']!=str(root):raise ManagementError('plan --root mismatch')
            result=apply_plan(plan)
        else:
            plan=make_plan(root,args.command,None if args.command=='install' else args.subject,
                           args.subject if args.command=='install' else None,getattr(args,'activate',False))
            if args.plan:
                args.plan.parent.mkdir(parents=True,exist_ok=True)
                with args.plan.open('x',encoding='utf-8') as stream:stream.write(encoded(plan).decode('utf-8'))
            result=apply_plan(plan) if args.apply else plan_summary(plan)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if isinstance(result,dict) and result.get('status')=='FAIL' else 0
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)},ensure_ascii=False,indent=2));return 1


if __name__=='__main__':raise SystemExit(cli())
