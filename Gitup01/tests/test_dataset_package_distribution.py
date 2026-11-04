"""Formal file ownership, export integrity, and exact ignore exceptions."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
import pytest

from cevns_pyeft.experiments.management import export_package, read_package
from cevns_pyeft.experiments.registry_io import read_registry

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('sid',['CsI2021','CsI2017','Ar2020'])
def test_package_export_owns_all_three_files_with_hashes(tmp_path,sid):
    registry=read_registry(ROOT)
    entry=next(e for e in registry['datasets'] if e['dataset_id']==sid)
    names={'experiment.input.yaml','experiment.resources.npz','experiment.physics.md'}
    records=[r for r in entry['owned_files'] if Path(r['path']).name in names]
    assert len(records)==3
    for record in records:
        assert record['sha256']==hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()
        assert record['runtime_required'] == (not record['path'].endswith('physics.md'))
    result=export_package(ROOT,sid,tmp_path/'dataset.zip')
    manifest,files,_=read_package(result['package'])
    assert names <= {Path(k).name for k in files}
    assert {r['resource_id'] for r in manifest['resources']}=={'package_input','package_arrays'}


@pytest.mark.parametrize('base',['data/experiments/COHERENT_CsI/CsI2021/',
                              'data/experiments/COHERENT_CsI/CsI2017/',
                              'data/experiments/COHERENT_Ar/Ar2020/'])
def test_formal_files_unignored_private_files_stay_ignored(base):
    for name in ('experiment.input.yaml','experiment.resources.npz','experiment.physics.md'):
        result=subprocess.run(['git','check-ignore','--no-index',base+name],cwd=ROOT,capture_output=True)
        assert result.returncode==1
    result=subprocess.run(['git','check-ignore','--no-index',base+'private-data.bin'],cwd=ROOT,capture_output=True)
    assert result.returncode==0
