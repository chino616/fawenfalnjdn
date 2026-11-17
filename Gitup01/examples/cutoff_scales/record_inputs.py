"""Record or verify the concrete readable resources used by a full22 model run."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import ROOT,sha,write_json
from forward22 import build_csi,build_ar,build_conus
from cevns_pyeft.contracts.validation import plain


def record(forward,check=False):
    forward=Path(forward).resolve()
    if not forward.is_relative_to((ROOT/'outputs/cutoff_scales').resolve()) or not (forward/'BUILD_PLAN.json').is_file():
        raise ValueError('explicit full22 model-build directory required')
    target=forward/'INPUTS_AND_IDENTITIES.json'
    models={name:plain(factory().describe()) for name,factory in (
        ('CsI2021_9PE',build_csi),('Ar2020_average',build_ar),('CONUS_plus',lambda:build_conus()[0]))}
    files=[]
    for relative in ['data/benchmarks/solar_b8_singlebin_2601_19883','data/experiments/CONUS_Plus/conusplus_kkl_run1']:
        for path in (ROOT/relative).iterdir():
            if path.is_file() and path.suffix.lower() in ['.txt','.csv','.json']:
                files.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    if check:
        old=json.loads(target.read_text(encoding='utf-8'))
        assert old['ground_models']==json.loads(json.dumps(models))
        expected={x['path']:x['sha256'] for x in old['direct_source_files']}
        assert expected=={x['path']:x['sha256'] for x in files}
        print('PASS_INPUT_IDENTITIES',len(models),len(files));return
    if target.exists():raise FileExistsError('concrete adopted input records are create-only')
    write_json(target,{'schema':'cutoff_full22_explicit_inputs/1','ground_models':models,'direct_source_files':files,
        'Ar_efficiency_choice':'historical package column1,column3 numeric convention; no coordinate reinterpretation; confirm adopted dim6 projection',
        'CsI_source':'explicit adopted raw200-node source regeneration and saved raw-byte hashes; targets/detector from readable records',
        'native_package_access':'PermissionError retained; restored models are analysis-only','external_author_equivalence':'UNRESOLVED; direct adopted sources are selected mainline resources'})
    print('RECORDED_INPUT_IDENTITIES',target)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--forward',type=Path,required=True);p.add_argument('--check',action='store_true')
    a=p.parse_args();record(a.forward,a.check)
