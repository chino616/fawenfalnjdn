"""Independent old-statistics comparison using the exact pre-change code hash.

This check was added after locating the existing optional observation CSV.
It evaluates original code on the already frozen M0 arrays; it does not claim
that a CONUS statistical run was captured before migration.
"""
from pathlib import Path
import subprocess,sys,hashlib,json,types
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment
from cevns_pyeft.experiments.definition import MassTimeExposure
from cevns_pyeft.contracts import TheoryPoint
from dataclasses import replace
out=ROOT/'outputs/experiment_modularization'
manifest=json.loads((out/'m0/manifest.json').read_text())
manifest['hashes']={k.replace(chr(92),'/'):v for k,v in manifest['hashes'].items()}
gitdir=ROOT.parents[1]/'260715Gitup1/.git'
path='src/cevns_pyeft/experiments/conus_plus/statistics.py'
old=subprocess.check_output(['git','--git-dir='+str(gitdir),'show','d7182a116353faf0ba5ba581338db1d2a4b63074:Gitup01/'+path])
# Repository copy may use CRLF; compare normalized line endings as well as bytes.
original_hash=hashlib.sha256(old).hexdigest()
original_crlf_hash=hashlib.sha256(old.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')).hexdigest()
assert manifest['hashes'][path] in (original_hash,original_crlf_hash)
profiling=ROOT/'src/cevns_pyeft/statistics/profiling.py'
assert hashlib.sha256(profiling.read_bytes()).hexdigest()==manifest['hashes']['src/cevns_pyeft/statistics/profiling.py']
module=types.ModuleType('original_conus_statistics')
sys.modules[module.__name__]=module
exec(compile(old,path,'exec'),module.__dict__)
observations=ROOT/'outputs/conus-plus-completion-20261012/statistics/approximate_paper_benchmark/observations_digitized_approx.csv'
rows=np.genfromtxt(observations,delimiter=',',names=True)
reference=np.load(out/'m0/baseline.npz',allow_pickle=False)
base=load_experiment('conus_plus_2025_c2c3c5_ge73_pyeft',resources=ROOT).definition
d=replace(base,physical=replace(base.physical,exposures=tuple(MassTimeExposure(k,x) for k,x in zip(base.observation.detector_ids,(0.,119.,0.)))))
exp=load_experiment(d.dataset_id,definition=d,resources=ResourceCatalog(ROOT,{'observations':observations}))
points={'SM':{},'NP':{(6,1,'u'):2e-7*np.eye(3)},'complex_multiflavor':{(6,1,'u'):np.array([[1e-7,2e-7j,0],[3e-8,-2e-7,0],[0,1e-8j,0]])}}
results=[]
for grid in (0,1):
    ns={'n_recoil':(8,12)[grid],'n_energy':(2,3)[grid]}
    for name,wc in points.items():
        signal=reference[f'CONUS/{grid}/{name}/slow/counts_per_detector_bin'][1]
        expected=module.profile_paper_eq33(signal,rows['observed_excess_per_kg_10eVee'],rows['sigma_used_half_span'])
        p=predict_experiment(exp,parameters=TheoryPoint(wc,sin2thetaW=.23857),numerics=ns)
        actual=evaluate_experiment(exp,p)
        np.testing.assert_allclose(actual.chi2,expected.chi2,rtol=1e-10,atol=1e-12)
        results.append({'grid':grid,'point':name,'old_chi2':expected.chi2,'new_chi2':actual.chi2,'absolute_error':abs(actual.chi2-expected.chi2)})
record={'old_code_commit':'d7182a116353faf0ba5ba581338db1d2a4b63074','old_code_sha256':original_hash,'m0_code_hash_verified':True,
    'observation_path':str(observations),'observation_sha256':hashlib.sha256(observations.read_bytes()).hexdigest(),
    'method':'original code on pre-change frozen C3 counts; explicit effective119 resource override','comparisons':results}
(out/'conus_statistics_comparison.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print('PASS',len(results),'old-code CONUS statistical comparisons')
