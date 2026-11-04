"""Deterministic compiler from an acquired/annotated IR to three formal files."""
from copy import deepcopy
from pathlib import Path
import hashlib
import io
import json
import os
import zipfile
import numpy as np

from .input_package import (strict_json, validate_document, validate_arrays, render_physics,
                            dependency_fingerprint, derived_value)
from . import generic_input

IR_VERSION='cevns-onboarding-draft/1'
FORMAL_FILES=('experiment.input.yaml','experiment.resources.npz','experiment.physics.md')


def archive_bytes(arrays):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_STORED) as archive:
        for key,array in sorted(arrays.items()):
            if not key or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in key):
                raise ValueError('unsafe array key: '+key)
            array=np.asarray(array)
            if array.dtype.hasobject or array.dtype.kind not in 'biufc' or not np.isfinite(array).all():
                raise ValueError('unsafe/nonfinite resource: '+key)
            content=io.BytesIO();np.lib.format.write_array(content,array,allow_pickle=False)
            info=zipfile.ZipInfo(key+'.npy',date_time=(1980,1,1,0,0,0));info.external_attr=0o600<<16
            archive.writestr(info,content.getvalue())
    return stream.getvalue()


def compile_draft(draft, arrays):
    if set(draft)!= {'ir_version','acquisition','requested_capabilities','document'} or draft['ir_version']!=IR_VERSION:
        raise ValueError('unsupported/unknown onboarding IR fields/version')
    if draft['acquisition']['mode'] not in ('human','ai','mixed','legacy_migration','synthetic'):
        raise ValueError('unknown acquisition mode')
    if not isinstance(draft['acquisition'].get('evidence_claims'),list):
        raise ValueError('evidence_claims must be explicit')
    data=deepcopy(draft['document'])
    if set(arrays)!=set(data['resources']['arrays']):
        raise ValueError('draft resource bijection differs from arrays')
    arrays={k:np.array(v,copy=True) for k,v in arrays.items()}
    for key,value in arrays.items():
        meta=data['resources']['arrays'][key]
        # Expected axes/units remain authored input, not inferred physical facts.
        if list(value.shape)!=meta['shape'] or str(value.dtype)!=meta['dtype']:
            raise ValueError('declared shape/dtype differs; no implicit precision conversion: '+key)
        meta['sha256_raw_c_order']=hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()
    pending={k for k,p in data['parameters'].items() if p['role']=='derived'}
    while pending:
        ready=[k for k in pending if not pending.intersection(data['parameters'][k]['derivation']['input_refs'])]
        if not ready:raise ValueError('derived parameter dependency cycle')
        for key in sorted(ready):
            p=data['parameters'][key];d=p['derivation'];refs=d['input_refs']
            value=derived_value(d['formula_id'],[data['parameters'][r]['value'] for r in refs])
            # Preserve an existing validated cache's floating-point representation.
            # Reassociating arithmetic alone must not invalidate a materialized array.
            if p['value'] is None or not np.isclose(p['value'],value,rtol=1e-14,atol=0):
                p['value']=value
            if 'adopted_value' in p:p['adopted_value']=p['value']
            d['dependency_fingerprint']=dependency_fingerprint(data,refs,formula_id=d['formula_id'])
            pending.remove(key)
    for meta in data['resources']['arrays'].values():
        generation=meta.get('generation')
        if generation:
            # Compiler must not bless stale arrays merely by refreshing a hash.
            expected=dependency_fingerprint(data,generation['parameter_refs'],generation['model_refs'],generation['resource_refs'])
            if generation['dependency_fingerprint']!=expected:
                raise ValueError('stale materialized resource requires explicit regeneration')
    raw=archive_bytes(arrays)
    data['resources']['archive']='experiment.resources.npz';data['resources']['sha256']=hashlib.sha256(raw).hexdigest()
    generic=data['package']['schema_version']==generic_input.VERSION
    errors=(generic_input.validate if generic else validate_document)(data)
    if not errors:errors=(generic_input.validate_resources if generic else validate_arrays)(data,arrays,raw)
    if errors:raise ValueError('; '.join(errors))
    md=(generic_input.render if generic else render_physics)(data,arrays)
    files={'experiment.input.yaml':(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8'),
           'experiment.resources.npz':raw,'experiment.physics.md':md.encode('utf8')}
    report={'status':'PASS','ir_version':IR_VERSION,'dataset_id':data['package']['dataset_id'],
            'package_status':data['package']['status'],'human_approval':data['package'].get('human_approval',data['package'].get('human_physics_approval')),
            'models':len(data['models']),'parameters':len(data['parameters']),'arrays':len(arrays),
            'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},
            'scope':'compiler checks only; no physics approval or runtime execution'}
    return files,report


def write_package(draft, arrays, output, *, check=False, overwrite=False):
    files,report=compile_draft(draft,arrays)
    output=Path(output)
    if check:
        report['status']='PASS' if all((output/n).is_file() and (output/n).read_bytes()==v for n,v in files.items()) else 'FAIL'
        return report
    present=[n for n in FORMAL_FILES if (output/n).exists()]
    if present and not overwrite:raise FileExistsError('create-only package already exists: '+str(present))
    output.mkdir(parents=True,exist_ok=True)
    if present:
        revision=hashlib.sha256(b''.join((output/n).read_bytes() for n in present)).hexdigest()[:16]
        repository=Path(__file__).resolve().parents[2]
        canonical=(repository/'data/experiments').resolve()
        formal=output.resolve().is_relative_to(canonical)
        backup=(repository/'backup/package_compiler'/output.resolve().relative_to(canonical)/revision
                if formal else output/('compiler-backup-'+revision))
        backup.mkdir(parents=True,exist_ok=False)
        for n in present:(backup/n).write_bytes((output/n).read_bytes())
        if formal:
            with (repository/'backup/BACKUP_MANIFEST.md').open('a',encoding='utf8') as manifest:
                for n in present:
                    manifest.write(f'\n| `{(output/n).resolve().relative_to(repository).as_posix()}` | '
                                   f'`{(backup/n).relative_to(repository).as_posix()}` | '
                                   f'{hashlib.sha256((backup/n).read_bytes()).hexdigest()} | compiler overwrite recovery |')
    for name,value in files.items():
        temporary=output/(name+'.compiler-tmp')
        with temporary.open('xb') as handle:handle.write(value)
        os.replace(temporary,output/name)
    return report
