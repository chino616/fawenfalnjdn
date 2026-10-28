"""Compare the public Fast entry to independent M0 results, not a shared wrapper."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment,compile_experiment
from cevns_pyeft.contracts import TheoryPoint,IntegrationSettings
from cevns_pyeft.kernels.compiler import compile_fast
out=ROOT/'outputs/experiment_modularization';ref=np.load(out/'m0/baseline.npz',allow_pickle=False)
points={'SM':{},'NP':{(6,1,'u'):2e-7*np.eye(3)},'complex_multiflavor':{(6,1,'u'):np.array([[1e-7,2e-7j,0],[3e-8,-2e-7,0],[0,1e-8j,0]])}}
rows=[]
for ds in ('CsI2021','CsI2017','Ar2020'):
    exp=load_experiment(ds,resources=ROOT)
    for grid in (0,1):
        ns={'n_enu':(12,18)[grid],'n_er':(51,76)[grid] if ds=='CsI2017' else (5,7)[grid]}
        if ds=='CsI2021':ns.update(n_pe_bin=(3,4)[grid],pe_step=3.)
        if ds=='Ar2020':ns['n_obs_sub']=(3,4)[grid]
        kernel=compile_fast(exp.model,numerics=IntegrationSettings.legacy_csi2021_v1(**ns),
            basis_keys=[(6,1,'u'),(6,1,'d'),(6,2,'u'),(6,2,'d')]) if ds=='CsI2021' else compile_experiment(exp,numerics=ns)
        for name,wc in points.items():
            p=predict_experiment(exp,parameters=TheoryPoint(wc),backend='fast',numerics=ns,kernel=kernel)
            # CsI2021's current Fast compiler reproduces the current Slow conversion;
            # the old legacy Fast conversion remains protected separately.
            route='slow' if ds=='CsI2021' else 'fast'
            expected=ref[f'{ds}/{grid}/{name}/{route}/counts_per_bin/total']
            np.testing.assert_allclose(p.counts,expected,rtol=1e-10,atol=1e-12)
            rows.append({'dataset':ds,'grid':grid,'point':name,'reference_backend':route,
                'maximum_absolute_error':float(np.max(np.abs(p.counts-expected))),
                'maximum_relative_error':float(np.max(np.abs(p.counts-expected)/np.maximum(np.abs(expected),np.finfo(float).tiny)))})
        print(ds,grid,'unified Fast PASS',flush=True)
(out/'unified_fast_comparison.json').write_text(json.dumps({'comparisons':rows},indent=2),encoding='utf-8')
