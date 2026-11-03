"""Standard-library storage contract for the single dataset registry."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

REGISTRY = 'cevns_pyeft/experiments/dataset_registry.json'
CORE_API_VERSION = 1
CRITICAL = {REGISTRY, 'cevns_pyeft/cli.py', 'cevns_pyeft/__init__.py',
            *(f'cevns_pyeft/experiments/{name}.py' for name in
              ('manifest','catalog','definition','loader','runtime','registry','registry_io','management'))}


class ManagementError(ValueError):
    pass


def parse_json(content):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ManagementError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(content, object_pairs_hook=unique)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')


def hash_bytes(value):
    return hashlib.sha256(value).hexdigest()


def relative_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ManagementError(f'expected a repository-relative POSIX path: {value!r}')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('.','..') for p in path.parts) or path.as_posix()!=value:
        raise ManagementError(f'unsafe/non-canonical path: {value!r}')
    if any(p in {'backup','outputs','.git','__pycache__'} for p in path.parts):
        raise ManagementError(f'not an installable input path: {value}')
    return value


def safe_path(root, value):
    root = Path(root).resolve()
    path = root / relative_path(value)
    cursor = path
    while cursor != root:
        if cursor.is_symlink():
            raise ManagementError(f'symlink is not a managed file: {value}')
        cursor = cursor.parent
    if not path.resolve().is_relative_to(root) or path.resolve()!=path.absolute():
        raise ManagementError(f'path escapes managed root: {value}')
    if path.exists() and not path.is_file():
        raise ManagementError(f'expected a file, not a directory: {value}')
    return path


def validate_registry(payload):
    if payload.get('schema_version')!=1 or payload.get('core_api_version')!=CORE_API_VERSION:
        raise ManagementError('unsupported registry schema/core API version')
    entries = payload.get('datasets')
    if not isinstance(entries,list):
        raise ManagementError('datasets must be an array')
    names, owners = set(), {}
    for entry in entries:
        sid = entry.get('dataset_id')
        if not isinstance(sid,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',sid):
            raise ManagementError(f'invalid dataset ID: {sid!r}')
        aliases = entry.get('aliases',[])
        if not isinstance(aliases,list) or any(not isinstance(a,str) or not a.strip() for a in aliases):
            raise ManagementError(f'invalid aliases: {sid}')
        for name in (sid,*aliases):
            if name in names:
                raise ManagementError(f'duplicate dataset ID/alias: {name}')
            names.add(name)
        if entry.get('status') not in ('active','archived','spec_only') or type(entry.get('installed')) is not bool:
            raise ManagementError(f'invalid lifecycle state: {sid}')
        if not entry['installed'] and entry['status']=='active':
            raise ManagementError(f'uninstalled dataset cannot be active: {sid}')
        module = entry.get('definition','')
        if not isinstance(module,str) or not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+',module):
            raise ManagementError(f'invalid definition entry: {sid}')
        if not isinstance(entry.get('package_version'),str) or not entry['package_version'].strip():
            raise ManagementError(f'missing package version: {sid}')
        if not re.fullmatch(r'[A-Za-z0-9_-]+',entry.get('experiment_slug','')):
            raise ManagementError(f'invalid experiment_slug: {sid}')
        own = entry.get('owned_files',[])
        if not isinstance(own,list) or not own:
            raise ManagementError(f'ownership declaration required: {sid}')
        for record in own:
            name = relative_path(record.get('path'))
            if record.get('role') not in {'code','data','documentation','test'}:
                raise ManagementError(f'invalid owned-file role: {name}')
            if name in CRITICAL or name in owners:
                raise ManagementError(f'critical/shared or multiply owned file: {name}')
            if not name.startswith(('cevns_pyeft/experiments/','data/experiments/','docs/experiments/','tests/')):
                raise ManagementError(f'owned file outside dataset areas: {name}')
            if name.startswith('cevns_pyeft/experiments/') and not name.startswith('cevns_pyeft/experiments/'+module.split('.')[0]+'/'):
                raise ManagementError(f'owned code outside definition namespace: {name}')
            if name.startswith('data/experiments/') and not name.startswith(f'data/experiments/{entry["experiment_slug"]}/{sid}/'):
                raise ManagementError(f'owned data outside dataset directory: {name}')
            owners[name] = sid
        definition = 'cevns_pyeft/experiments/'+module.replace('.','/')+'.py'
        if owners.get(definition)!=sid:
            raise ManagementError(f'definition must be an owned file: {sid}')
        deps=entry.get('shared_dependencies',[])
        if not isinstance(deps,list) or len(deps)!=len(set(deps)):
            raise ManagementError(f'invalid shared dependencies: {sid}')
        for name in deps:relative_path(name)
        if not isinstance(entry.get('requires_datasets',[]),list):
            raise ManagementError(f'invalid dataset dependencies: {sid}')
        pins=entry.get('required_dataset_versions',{})
        if (not isinstance(pins,dict) or not set(pins)<=set(entry.get('requires_datasets',[]))
                or any(not isinstance(v,str) or not v.strip() for v in pins.values())):
            raise ManagementError(f'invalid required dataset versions: {sid}')
    ids={e['dataset_id'] for e in entries}
    graph={e['dataset_id']:e.get('requires_datasets',[]) for e in entries}
    visiting, done=set(),set()
    def visit(sid):
        if sid in visiting:raise ManagementError('dataset dependency cycle: '+sid)
        if sid in done:return
        visiting.add(sid)
        for dep in graph[sid]:
            if dep not in ids:raise ManagementError(f'unknown dataset dependency: {dep}')
            visit(dep)
        visiting.remove(sid);done.add(sid)
    for sid in graph:visit(sid)
    return payload


def read_registry(root):
    return validate_registry(parse_json(safe_path(root,REGISTRY).read_text('utf-8')))


def find_entry(payload, name):
    matches=[e for e in payload['datasets'] if name in (e['dataset_id'],*e.get('aliases',[]))]
    if len(matches)!=1:raise ManagementError(f'unknown or ambiguous dataset: {name}')
    return matches[0]
