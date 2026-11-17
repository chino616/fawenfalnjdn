"""Compile the existing interface kernel and calculate independent NSI Slow checks."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('nsi')
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys
import time
import numpy as np
import sm_model as sm
from nsi_model import BASIS, HERE, model, point, verify_snapshot
from cevns_pyeft.core.predict import predict
from cevns_pyeft.kernels.compiler import compile_fast
from cevns_pyeft.kernels.interface_storage import save_compiled_kernel
OUTPUT = LAYOUT.path('outputs')
KERNEL = OUTPUT / 'nsi_operator_kernel_161_641.npz'
SLOW_CASES = (('u_ee_005', {'epsilon_ee_uV': 0.05}, 161, 641), ('d_ee_034', {'epsilon_ee_dV': 0.34}, 161, 641), ('u_ee_cancellation', {'epsilon_ee_uV': 0.19}, 161, 641), ('emu_u_010', {'epsilon_emu_uV': 0.1}, 161, 641), ('emu_complex_mixed', {'epsilon_emu_uV': 0.08 + 0.03j, 'epsilon_emu_dV': -0.04 + 0.05j}, 161, 641), ('combined_real', {'epsilon_ee_uV': 0.12, 'epsilon_ee_dV': -0.08, 'epsilon_emu_uV': 0.07, 'epsilon_emu_dV': -0.03}, 161, 641), ('u_ee_005_energy321', {'epsilon_ee_uV': 0.05}, 161, 321))

def compile_kernel():
    started = time.perf_counter()
    experiment = model()
    numerical = sm.settings(161, 641)
    kernel = compile_fast(experiment, numerics=numerical, basis_keys=BASIS)
    save_compiled_kernel(KERNEL, kernel)
    result = {'seconds': time.perf_counter() - started, 'basis': BASIS, 'shape': kernel.full_kernel.shape, 'kernel_sha256': sm.sha256(KERNEL), 'record': kernel.record, 'numerics': numerical.__dict__, 'scope': 'Four dimension-6 quark vector/axial operators, SM plus vector NSI only', 'human_gate': 'NOT_REVIEWED'}
    sm.write_json(OUTPUT / 'compile_summary.json', result)
    return {'task': 'compile_kernel', 'seconds': result['seconds'], 'shape': result['shape']}

def slow_case(case):
    name, couplings, n_er, n_enu = case
    started = time.perf_counter()
    experiment = model()
    result = predict(experiment, parameters=point(**couplings), numerics=sm.settings(n_er, n_enu), backend='slow')
    arrays = {'counts': result.counts, 'edges_eVee': sm.EDGES}
    for isotope in sm.ISOTOPES:
        arrays['counts_' + isotope] = result.components['reactor_antinu_e', isotope]
    destination = OUTPUT / ('slow_' + name + '.npz')
    np.savez_compressed(destination, **arrays)
    record = {'name': name, 'couplings': couplings, 'counts': result.counts, 'total_events': float(result.counts.sum()), 'numerics': result.numerical_record, 'normalization': result.normalization_record, 'seconds': time.perf_counter() - started, 'backend': 'slow', 'executor': 'cevns_pyeft.core.predict.predict', 'array_sha256': sm.sha256(destination), 'human_gate': 'NOT_REVIEWED'}
    sm.write_json(OUTPUT / ('slow_' + name + '.json'), record)
    return {'task': name, 'total_events': record['total_events'], 'seconds': record['seconds']}

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    verify_snapshot()
    jobs = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        if not KERNEL.exists():
            jobs.append(executor.submit(compile_kernel))
        for case in SLOW_CASES:
            if not (OUTPUT / ('slow_' + case[0] + '.json')).exists():
                jobs.append(executor.submit(slow_case, case))
        if not jobs:
            print('Prediction artifacts already exist. Check them with benchmark_nsi.py.', flush=True)
        for job in as_completed(jobs):
            print(json.dumps(job.result()), flush=True)
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
