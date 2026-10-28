"""Capture the unmodified public implementations; never overwrite a freeze.

Run from the project root using the recorded Python environment. The results
are engineering regression evidence, not an integration/convergence approval.
"""
from pathlib import Path
import sys
import json
import hashlib
import platform
import importlib
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
OUT = ROOT / 'outputs/experiment_modularization/m0'
OUT.mkdir(parents=True, exist_ok=True)
reference = np.load(OUT / 'baseline.npz', allow_pickle=False)
errors = []
from cevns_pyeft.kernels.basis import li2026_left_basis_current, coeff_tensor_from_triplets
from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel
from cevns_pyeft.statistics.datasets import load_dataset
from cevns_pyeft.statistics.likelihoods import chi2_for_dataset
from cevns_pyeft.statistics.observables import prediction_vector
from cevns_pyeft.experiments.conus_plus.slow_counts import slow_counts_conus_plus
from cevns_pyeft.experiments.conus_plus.fast_kernel import build_detector_response_matrix, fast_counts_conus_plus_response_matrix

responses = ROOT / 'data/responses/responses_all.json'
points = {'SM': {}, 'NP': {(6, 1, 'u'): 2e-7 * np.eye(3)},
          'complex_multiflavor': {(6, 1, 'u'): np.array([[1e-7, 2e-7j, 0], [3e-8, -2e-7, 0], [0, 1e-8j, 0]])}}
arrays, runs = {}, []
def flatten(prefix, value):
    if isinstance(value, dict):
        for k, v in value.items(): flatten(prefix + '/' + str(k), v)
    elif isinstance(value, np.ndarray) and value.dtype.kind in 'fciub':
        expected = reference[prefix]
        difference = float(np.max(np.abs(value-expected),initial=0))
        relative = float(np.max(np.abs(value-expected)/np.maximum(np.abs(expected),np.finfo(float).tiny),initial=0))
        np.testing.assert_allclose(value,expected,rtol=1e-10,atol=0 if '/kernel/' in prefix else 1e-12,err_msg=prefix)
        errors.append({'key':prefix,'max_absolute':difference,'max_relative':relative})
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for base in ('src', 'data/responses', 'data/datafiles', 'data/experiments/CONUS_Plus')
          for p in (ROOT / base).rglob('*') if p.is_file() and p.suffix in ('.py', '.json', '.csv', '.txt')}
for ds, suffix in ([] if '--only-conus' in sys.argv else [('CsI2021','csi2021'), ('CsI2017','csi2017'), ('Ar2020','ar2020')]):
    slow = getattr(importlib.import_module('cevns_pyeft.experiments.coherent.slow_counts_' + suffix), 'slow_counts_' + suffix)
    fast = getattr(importlib.import_module('cevns_pyeft.experiments.coherent.fast_kernel_' + suffix), 'build_fast_kernel_' + suffix)
    for grid in (0, 1):
        ns = {'n_enu': (12, 18)[grid]}
        if ds != 'CsI2017': ns.update(n_er=(5,7)[grid], n_pe_bin=(3,4)[grid])
        fs = dict(n_enu=ns['n_enu'], n_er=(51,76)[grid] if ds == 'CsI2017' else ns['n_er'])
        if ds == 'CsI2021': fs['n_pe_sub'] = ns['n_pe_bin']
        if ds == 'Ar2020': fs['n_obs_sub'] = ns['n_pe_bin']
        basis = [b for b in li2026_left_basis_current() if b.triplet[0] == 6]
        kernel = fast(responses, basis=basis, **fs)
        flatten(f'{ds}/{grid}/kernel', kernel)
        for name, wc in points.items():
            result = slow(responses, wc, **ns)
            flatten(f'{ds}/{grid}/{name}/slow', result)
            coeff = coeff_tensor_from_triplets(basis, wc, include_sm=True, sin2thetaW=.2387)
            reconstructed = reconstruct_counts_from_kernel(kernel, coeff)
            flatten(f'{ds}/{grid}/{name}/fast', reconstructed)
            data = load_dataset(ds)
            values = result['counts_per_npe' if ds == 'CsI2021' else 'counts_per_bin']['total']
            chi2 = chi2_for_dataset(prediction_vector(values, data.observable), data).chi2
            np.testing.assert_allclose(chi2,reference[f'{ds}/{grid}/{name}/chi2'],rtol=1e-10,atol=1e-12)
            from cevns_pyeft.experiments.loader import load_experiment
            from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment
            from cevns_pyeft.contracts import TheoryPoint
            exp=load_experiment(ds)
            pred=predict_experiment(exp,parameters=TheoryPoint(wc),numerics=ns)
            np.testing.assert_allclose(pred.counts,result['counts_per_bin']['total'],rtol=1e-10,atol=1e-12)
            np.testing.assert_allclose(evaluate_experiment(exp,pred).chi2,chi2,rtol=1e-10,atol=1e-12)
        runs.append({'dataset': ds, 'slow_numerics': ns, 'fast_numerics': fs})
        print(ds, grid, 'verified', flush=True)
for grid in (0,1):
    ns = dict(n_recoil=(8,12)[grid], n_energy=(2,3)[grid])
    cache = build_detector_response_matrix(n_recoil=ns['n_recoil'])
    flatten(f'CONUS/{grid}/kernel', cache)
    for name, wc in points.items():
        flatten(f'CONUS/{grid}/{name}/slow', slow_counts_conus_plus(responses, wc, **ns))
        flatten(f'CONUS/{grid}/{name}/fast', fast_counts_conus_plus_response_matrix(cache, responses, wc, n_energy=ns['n_energy']))
    runs.append({'dataset': 'conus_plus_2025_c2c3c5_ge73_pyeft', 'numerics': ns,
                 'statistics': 'effective119 benchmark is distinct from 357 kg day forward prediction; not rebound'})
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.experiments.runtime import predict_experiment
    from cevns_pyeft.contracts import TheoryPoint
    exp=load_experiment('conus_plus_2025_c2c3c5_ge73_pyeft')
    for name,wc in points.items():
        for backend in ('slow','fast'):
            pred=predict_experiment(exp,parameters=TheoryPoint(wc,sin2thetaW=.23857),numerics=ns,backend=backend)
            expected=reference[f'CONUS/{grid}/{name}/{backend}/counts_per_detector_component_bin']
            actual=pred.legacy_result['counts_per_detector_component_bin']
            np.testing.assert_allclose(actual,expected,rtol=1e-10,atol=1e-12)
    print('CONUS', grid, 'verified', flush=True)
(OUT.parent / ('conus_final_baseline_comparison.json' if '--only-conus' in sys.argv else 'baseline_comparison.json')).write_text(json.dumps({'arrays_checked':len(errors),'comparisons':errors},indent=2),encoding='utf-8')
print('PASS',len(errors),'independent numeric arrays')
