"""Execute all nuclear-M teaching cores alone and check actual provenance/data."""
from pathlib import Path
from tempfile import TemporaryDirectory
import ast
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT.parent/'重构/20261110_PandaX_Response_P01_P10_物理与最小代码'
OUT=ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2'


def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    snapshot=read(EXAMPLE/'_核对记录/source_snapshot.json')
    for row in snapshot['files']:
        assert sha(Path(row['file']))==row['sha256'],row['file']
    stages=read(EXAMPLE/'_核对记录/stages.json');executions=[];modules={}
    for key,stage in sorted(stages.items()):
        core=EXAMPLE/stage['directory']/'core.py'
        tree=ast.parse(core.read_text(encoding='utf8'));names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names.extend(n.name.split('.')[0] for n in node.names)
            if isinstance(node,ast.ImportFrom):names.append((node.module or '').split('.')[0])
        assert set(names)<={'json','pathlib','numpy','scipy'}
        assert len(core.read_text(encoding='utf8').splitlines())<=200
        with TemporaryDirectory(prefix='pandax-nuclear-core-') as tmp:
            tmp=Path(tmp);shutil.copy2(core,tmp/'core.py')
            run=subprocess.run([sys.executable,'-I','-B',str(tmp/'core.py')],cwd=tmp,
                capture_output=True,text=True,encoding='utf8')
            assert run.returncode==0,(key,run.stderr)
            result=read(tmp/'运行结果.json');shutil.copy2(tmp/'运行结果.json',core.with_name('运行结果.json'))
        executions.append({'stage':key,'lines':stage['lines'],'imports':sorted(set(names)),
            'isolated_execution':'PASS; only core.py in empty directory, python -I -B',
            'core_sha256':sha(core),'result_sha256':sha(core.with_name('运行结果.json'))})
        modules[key]=runpy.run_path(str(core),run_name='independent_inspection')
    p=modules['P07'];signal=p['direct_counts']().sum(axis=0)
    production=read(OUT/'PandaX4T_2024_US2/RESULT.json')
    primary_m=np.asarray(production['channel_decomposition']['counts_by_channel']['M'])
    relative=signal/primary_m-1
    assert np.max(abs(relative))<.001,'0.1% per-bin teaching/source-reduction comparison'
    raw=read(ROOT/'data/responses/responses_all.json')['nuclei']
    for A,(b,pp,pn,nn) in p['M_TABLE'].items():
        item=raw['Xe'+str(A)]
        assert b==item['basic']['b']
        np.testing.assert_array_equal([pp,pn,nn],np.asarray(item['responses']['M'])[[0,0,1],[0,1,1]])
        for recoil in (0.,.8,2.):
            y=2*(A*p['AMU'])*recoil*1e-6*b*b/4
            W=np.array([[np.exp(-2*y)*np.polynomial.polynomial.polyval(y,c)
                for c in row] for row in item['responses']['M']])
            np.testing.assert_allclose(p['coherent_M'](A,A*p['AMU'],recoil),W,rtol=3e-15)
    # Independent amplitude/phase-space check across separate standalone stages.
    out4=read(EXAMPLE/stages['P04']['directory']/'运行结果.json')
    m=131*p['AMU'];expected=out4['trace_rho_K_GeV_minus2']*m/(8*np.pi*.010**2)*p['GEV2_TO_CM2']*1e-6
    actual=float(modules['P05']['dsigma'](131,m,10.,1.))
    np.testing.assert_allclose(actual,expected,rtol=3e-14)
    result={'status':'PASS','executions':executions,'actual_M_coefficients':'exactly match all seven source tables',
        'amplitude_to_cross_section_units':'PASS; independent P04 to P05 calculation',
        'M_only_teaching_counts':signal.tolist(),'M_only_teaching_total':float(signal.sum()),
        'production_M_counts':primary_m.tolist(),'relative_difference_per_bin':relative.tolist(),
        'max_relative_difference':float(np.max(abs(relative))),
        'scope':'actual M only; reduced source; no KN, calibration, abundance renormalization or external certification'}
    (OUT/'TEACHING_VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'independent_files':len(executions),
        'max_lines':max(v['lines'] for v in executions),'M_total':result['M_only_teaching_total'],
        'max_relative_difference':result['max_relative_difference']},ensure_ascii=False))


if __name__=='__main__':main()
