"""Verify an already built wheel install from outside the project cwd."""
from pathlib import Path
import sys,subprocess,json,os
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/release'
installed=Path(json.loads((OUT/'wheel.json').read_text())['installed'])
outside=ROOT.parents[1]/'outputs/refactor03_wheel_outside_cwd'
outside.mkdir(parents=True,exist_ok=True)
script=r'''import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import cevns_pyeft
assert Path(cevns_pyeft.__file__).is_relative_to(Path(sys.argv[1]))
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment
root=Path(sys.argv[2]);results={}
for key in BUILTIN_CATALOG.ids():
    exp=load_experiment(key,resources=ResourceCatalog(root))
    ns={'n_recoil':8,'n_energy':2} if key.startswith('conus') else {'n_enu':8} if key=='CsI2017' else {'n_er':4,'n_enu':8,'n_pe_bin':3}
    pred=predict_experiment(exp,numerics=ns)
    assert pred.counts.sum()>0
    results[key]={'sum':float(pred.counts.sum()),'shape':list(pred.counts.shape),'unit':pred.combined_prediction.axes[0].unit,'detectors':list(pred.detector_predictions)}
print(json.dumps({'package':cevns_pyeft.__file__,'cwd':str(Path.cwd()),'results':results},indent=2))
'''
p=subprocess.run([sys.executable,'-I','-c',script,str(installed),str(ROOT)],cwd=outside,
    capture_output=True,text=True,env={k:v for k,v in os.environ.items() if k!='PYTHONPATH'})
(OUT/'outside_cwd.log').write_text(p.stdout+p.stderr,encoding='utf-8')
p.check_returncode()
result=json.loads(p.stdout)
(OUT/'outside_cwd.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
