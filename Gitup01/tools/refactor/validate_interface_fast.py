"""Compare real model Fast/Slow outputs without changing frozen references."""
from pathlib import Path
import json
import sys
import time
import numpy as np

PROJECT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PROJECT/"src"), str(PROJECT)]
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.kernels import compile_fast, save_compiled_kernel, load_compiled_kernel
from tools.refactor.freeze_baseline import points, GRIDS


def main():
    folder = PROJECT/"outputs/refactor_r4"
    (folder/"kernels").mkdir(exist_ok=True, parents=True)
    model = make_csi2021_model(PROJECT/"data/responses/responses_all.json")
    report = {"rtol": 1e-10, "atol_events": 1e-12, "basis_size": 22, "cases": [], "compilation": {}}
    for grid, settings in GRIDS.items():
        numerics = IntegrationSettings.legacy_csi2021_v1(**settings)
        start = time.perf_counter()
        kernel = compile_fast(model, numerics=numerics)
        report["compilation"][grid] = {"seconds": time.perf_counter()-start, "shape": list(kernel.full_kernel.shape),
                                       "fingerprint": kernel.record["dependency_fingerprint"]}
        destination = folder/"kernels"/(grid+".npz")
        save_compiled_kernel(destination,kernel)
        loaded = load_compiled_kernel(destination,model=model)
        for name,(wc,sm) in points().items():
            if grid=="default" and name!="sm": continue
            point=TheoryPoint(wc,include_sm=sm)
            start=time.perf_counter(); slow=predict(model,parameters=point,numerics=numerics); slow_time=time.perf_counter()-start
            start=time.perf_counter(); full=kernel.predict(parameters=point); fast_time=time.perf_counter()-start
            pair=loaded.predict(parameters=point,representation="pair")
            comparisons=[]
            for key in slow.components:
                reference=slow.components[key]; actual=full.components[key]; delta=abs(actual-reference)
                limit=report['atol_events']+report['rtol']*abs(reference)
                comparisons.append({'source':key[0],'isotope':key[1],'max_absolute_events':float(delta.max()),
                    'worst_bin':int(np.argmax(delta/limit))+1,'fraction_of_allowed_error':float(np.max(delta/limit)),
                    'passed':bool(np.all(delta<=limit))})
            pair_error=float(np.max(abs(pair.counts-full.counts)))
            assert np.allclose(pair.counts,full.counts,rtol=1e-12,atol=1e-12)
            report['cases'].append({'point':name,'grid':grid,'slow_seconds':slow_time,'fast_seconds':fast_time,
                                    'pair_and_reload_max_absolute':pair_error,'comparisons':comparisons})
        print('Validated',grid,'all 22 operators',flush=True)
    report['status']='PASS' if all(e['passed'] for c in report['cases'] for e in c['comparisons']) else 'FAIL'
    report['maximum_absolute_events']=max(e['max_absolute_events'] for c in report['cases'] for e in c['comparisons'])
    report['worst_fraction_of_allowed_error']=max(e['fraction_of_allowed_error'] for c in report['cases'] for e in c['comparisons'])
    (folder/'fast_slow_comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (folder/'resolved_model.json').write_text(json.dumps(model.describe(),indent=2),encoding='utf-8')
    print(report['status'],report['maximum_absolute_events'],flush=True)
    if report['status']!='PASS': raise SystemExit(1)


if __name__=='__main__':
    main()
