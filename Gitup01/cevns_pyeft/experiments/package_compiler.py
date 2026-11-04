"""Existing compiler: machine input pair plus detailed and summary Markdown."""
from copy import deepcopy
from pathlib import Path
import hashlib
import io
import json
import os
import zipfile
import base64
import subprocess
import shutil
import uuid
import numpy as np

from .input_package import (strict_json, validate_document, validate_arrays, render_physics,
                            dependency_fingerprint, derived_value, read_arrays, validate_package,
                            _report_selection)
from . import generic_input

IR_VERSION='cevns-onboarding-draft/1'
FORMAL_FILES=('experiment.input.yaml','experiment.resources.npz','experiment.physics.md','experiment.physics.summary.md')


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
           'experiment.resources.npz':raw,'experiment.physics.md':md.encode('utf8'),
           'experiment.physics.summary.md':render_physics(data,arrays,summary=True).encode('utf8')}
    report={'status':'PASS','ir_version':IR_VERSION,'dataset_id':data['package']['dataset_id'],
            'package_status':data['package']['status'],'human_approval':data['package'].get('human_approval',data['package'].get('human_physics_approval')),
            'models':len(data['models']),'parameters':len(data['parameters']),'arrays':len(arrays),
            'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},
            'scope':'compiler checks only; no physics approval or runtime execution',
            'diagnostics':['H3_UNCLASSIFIED_MODEL: '+mid for mid in _report_selection(data)[1]]}
    return files,report



def _check_inherited_acl(paths):
    """Read-only ACL check; never attach a sandbox/Everyone ACE."""
    if os.name != 'nt':
        return 'NOT_APPLICABLE'
    encoded=base64.b64encode(json.dumps([str(p) for p in paths]).encode('utf8')).decode('ascii')
    script=r"""
$ErrorActionPreference='Stop'
$paths=ConvertFrom-Json ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('__PATHS__')))
foreach ($path in $paths) {
    $acl=Get-Acl -LiteralPath $path
    if ($acl.AreAccessRulesProtected -or @($acl.Access).Count -eq 0 -or
        @($acl.Access | Where-Object { -not $_.IsInherited }).Count -ne 0) {
        throw ('File does not inherit target directory ACL: '+$path)
    }
}
"""
    subprocess.run([shutil.which('pwsh') or 'powershell.exe','-NoProfile','-NonInteractive','-Command',
                    script.replace('__PATHS__',encoded)],check=True,capture_output=True)
    return 'ACL_INHERITANCE_OK'


def write_package(draft, arrays, output, *, check=False, overwrite=False, md_only=False):
    """Existing writer, including read-only YAML/NPZ -> MD regeneration.

    A replacement inherits ACLs by normal creation beside its destination.
    Same-directory hard links preserve original bytes AND security for rollback.
    The three-file set is recoverable, not a cross-file atomic transaction.
    """
    output=Path(output).resolve()
    if md_only:
        validation=validate_package(output,check_md=False)
        if validation['status']!='PASS':
            raise ValueError('; '.join(validation['errors']))
        data=strict_json((output/FORMAL_FILES[0]).read_text('utf8'))
        raw=(output/FORMAL_FILES[1]).read_bytes()
        stored=read_arrays(raw,data['resources']['arrays'])
        files={FORMAL_FILES[2]:render_physics(data,stored).encode('utf8'),
               FORMAL_FILES[3]:render_physics(data,stored,summary=True).encode('utf8')}
        report={'status':'PASS','dataset_id':data['package']['dataset_id'],'mode':'md_only',
                'scope':'read-only input validation and MD rendering; no runtime/scientific approval',
                'diagnostics':['H3_UNCLASSIFIED_MODEL: '+mid for mid in _report_selection(data)[1]],
                'sha256':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()}}
    else:
        files,report=compile_draft(draft,arrays)
    if check:
        report['status']='PASS' if all((output/n).is_file() and (output/n).read_bytes()==v for n,v in files.items()) else 'FAIL'
        return report
    present=[n for n in files if (output/n).exists()]
    if present and not overwrite:
        raise FileExistsError('create-only package already exists: '+str(present))
    output.mkdir(parents=True,exist_ok=True)
    if not output.is_dir():
        raise NotADirectoryError(output)
    # Reject aliases: neither backups nor rollback may follow an escaped target.
    if any((output/n).is_symlink() or ((output/n).exists() and not (output/n).is_file()) for n in files):
        raise ValueError('package targets must be regular files')
    if present:
        revision=hashlib.sha256(b''.join((output/n).read_bytes() for n in present)).hexdigest()[:16]
        repository=Path(__file__).resolve().parents[2]
        canonical=(repository/'data/experiments').resolve()
        formal=output.is_relative_to(canonical)
        backup=(repository/'backup/package_compiler'/output.relative_to(canonical)/revision
                if formal else output/('compiler-backup-'+revision))
        backup.mkdir(parents=True,exist_ok=True)
        for n in present:
            content=(output/n).read_bytes()
            target=backup/n
            if target.exists():
                if target.read_bytes()!=content:
                    raise FileExistsError('recovery revision collision: '+str(target))
            else:
                with target.open('xb') as handle:
                    handle.write(content)
                if formal:
                    with (repository/'backup/BACKUP_MANIFEST.md').open('a',encoding='utf8') as manifest:
                        manifest.write('\n| '+str((output/n).relative_to(repository))+' | '+
                                       str(target.relative_to(repository))+' | '+
                                       hashlib.sha256(content).hexdigest()+' | compiler overwrite recovery |')
    staged, originals, installed={}, {}, []
    recovery_failed=False
    try:
        for name,value in files.items():
            temporary=output/('.'+name+'.'+uuid.uuid4().hex+'.compiler-tmp')
            staged[name]=temporary
            # Ordinary file creation, not tempfile's private directory/DACL.
            with temporary.open('xb') as handle:
                handle.write(value);handle.flush();os.fsync(handle.fileno())
            if temporary.read_bytes()!=value:
                raise OSError('temporary content verification failed: '+name)
            if name.endswith(('.yaml','.md')):
                text=value.decode('utf8')
                if text.startswith('\ufeff') or '\r' in text:
                    raise ValueError('text output must be UTF-8 without BOM and use LF')
        report['temporary_acl_state']=_check_inherited_acl(list(staged.values()))
        # Hard links retain original ACLs, including on a post-replacement failure.
        # If the filesystem cannot provide recovery links, fail before replacing.
        for name in present:
            original=output/('.'+name+'.'+uuid.uuid4().hex+'.compiler-rollback')
            os.link(output/name,original)
            originals[name]=original
        for name,temporary in staged.items():
            os.replace(temporary,output/name)
            installed.append(name)
        report['acl_state']=_check_inherited_acl([output/n for n in files])
        for name,value in files.items():
            if (output/name).read_bytes()!=value:
                raise OSError('final readback differs: '+name)
        principal=(subprocess.check_output(['whoami'],text=True).strip() if os.name=='nt' else None)
        target=os.environ.get('CEVNS_TARGET_WINDOWS_PRINCIPAL')
        report.update(write_state='WRITE_OK',execution_user=principal,target_user=target,
                      execution_user_read_state='READ_OK',
                      target_user_read_state=('TARGET_USER_READ_OK' if principal and target and
                                              principal.casefold()==target.casefold() else 'TARGET_USER_READ_PENDING'))
        if report['target_user_read_state']=='TARGET_USER_READ_PENDING':
            report['target_user_check']='In the target user PowerShell run whoami and Get-Content -LiteralPath <each final file>; sandbox readback is not target-user verification.'
    except BaseException as failure:
        for name in reversed(installed):
            try:
                if name in originals:
                    os.replace(originals[name],output/name)
                    originals.pop(name)
                else:
                    (output/name).unlink()
            except OSError:
                recovery_failed=True
        if recovery_failed:
            raise OSError('rollback requires recovery from preserved files: '+str(list(originals.values()))) from failure
        raise
    finally:
        for temporary in [*staged.values(),*([] if recovery_failed else originals.values())]:
            temporary.unlink(missing_ok=True)
    return report
