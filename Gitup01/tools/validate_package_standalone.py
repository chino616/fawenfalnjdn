"""Build/install an engine, then run only two package files outside the source tree."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def driver(args):
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError('choose a fresh run directory: ' + str(output))
    output.mkdir(parents=True)
    temp = output/'build-temp'
    temp.mkdir()
    env = {**os.environ, 'TEMP': str(temp), 'TMP': str(temp), 'PYTHONDONTWRITEBYTECODE': '1'}
    for label, command in [
        ('build', [sys.executable, '-B', '-m', 'pip', 'wheel', str(root), '--no-build-isolation',
                   '--no-deps', '--no-index', '--no-cache-dir', '--wheel-dir', str(output/'wheels')])]:
        result = subprocess.run(command, cwd=output, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output/(label+'.log')).write_text(result.stdout, encoding='utf8')
        result.check_returncode()
    wheel = next((output/'wheels').glob('*.whl'))
    installed = output/'engine'
    command = [sys.executable, '-B', '-m', 'pip', 'install', '--no-deps', '--no-index', '--no-cache-dir',
               '--target', str(installed), str(wheel)]
    result = subprocess.run(command, cwd=output, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output/'install.log').write_text(result.stdout, encoding='utf8')
    result.check_returncode()
    # Restrict only this newly installed throwaway engine. Never touch source files.
    excluded = []
    engine = installed/'cevns_pyeft'
    candidates = [*engine.rglob('*_definition.py'), *engine.rglob('legacy_parameters.py'),
                  engine/'experiments/coherent/csi2021_package.py',
                  engine/'experiments/coherent/csi2021_package_contract.json']
    for path in candidates:
        resolved = path.resolve()
        if not resolved.is_relative_to(installed):
            raise ValueError('invalid isolation removal path')
        if path.is_file():
            excluded.append(path.relative_to(installed).as_posix())
            path.unlink()
    outside = output/'outside-cwd'
    outside.mkdir()
    package = outside/'isolated_package'
    package.mkdir()
    for name in ('experiment.input.yaml', 'experiment.resources.npz'):
        shutil.copy2(Path(args.package)/name, package/name)
    worker_file = outside/'standalone_worker.py'
    shutil.copy2(__file__, worker_file)
    bootstrap = 'import sys,runpy;sys.path.insert(0,sys.argv.pop(1));runpy.run_path(sys.argv.pop(1),run_name="__main__")'
    command = [sys.executable, '-I', '-B', '-c', bootstrap, str(installed), str(worker_file),
               '--worker', '--package', str(package), '--output', str(outside), '--source-root', str(root)]
    result = subprocess.run(command, cwd=outside, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output/'worker.log').write_text(result.stdout, encoding='utf8')
    result.check_returncode()
    report = json.loads((outside/'standalone_results.json').read_text('utf8'))
    import numpy as np
    with np.load(root/'tests/reference/interface_refactor_v1/baseline.npz', allow_pickle=False) as reference:
        comparisons = {}
        for grid in ('small', 'default'):
            expected = reference[f'csi2021/sm/{grid}/counts_per_bin/total']
            actual = np.array(report['prediction'][grid]['counts'])
            np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-12)
            comparisons[grid] = {'max_abs': float(np.max(np.abs(actual-expected))), 'rtol': 1e-10, 'atol': 1e-12}
    report['frozen_internal_comparison'] = comparisons
    report['wheel'] = {'name': wheel.name, 'sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(), 'excluded_from_runtime': excluded}
    report['scope'] = 'isolated wheel install using declared dependencies already installed in the interpreter; same host, two directories; no second physical machine claimed'
    dump(output/'results.json', report)
    print(json.dumps({'status': report['status'], 'report': str(output/'results.json'), 'I01-I10': report['checks']}))


def worker(args):
    import importlib.abc
    import numpy as np
    output, package = Path(args.output), Path(args.package)
    source = Path(args.source_root).resolve()
    access = set()
    class Guard(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, *unused):
            if fullname.endswith(('_definition', '.legacy_parameters', '.csi2021_package')):
                raise ImportError('forbidden legacy experiment import: ' + fullname)
    sys.meta_path.insert(0, Guard())
    def audit(event, values):
        if event != 'open' or not isinstance(values[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(values[0])).resolve()
        if path.is_relative_to(source) and not path.is_relative_to(output.parent):
            raise PermissionError('source-tree runtime dependency: ' + str(path))
        if path.name in ('responses_all.json', 'experiment.physics.md', 'experiment.yaml', 'legacy_parameters.py'):
            raise PermissionError('forbidden runtime resource: ' + str(path))
        if path.is_relative_to(output):
            access.add(path.relative_to(output).as_posix())
    sys.addaudithook(audit)
    from cevns_pyeft.experiments.package_loader import load_experiment_package, definition_from_package
    from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
    from cevns_pyeft.kernels.compiler import compile_fast
    before = time.perf_counter()
    definition_from_package(package)
    parsed = time.perf_counter()-before
    before = time.perf_counter()
    exp = load_experiment_package(package)
    loaded = time.perf_counter()-before
    profiles = {'small': dict(n_er=5,n_enu=12,n_pe_bin=4,pe_step=4.),
                'default': dict(n_er=21,n_enu=120,n_pe_bin=8,pe_step=3.),
                'refined': dict(n_er=41,n_enu=240,n_pe_bin=16,pe_step=1.5)}
    prediction = {}
    results = {}
    for grid, ns in profiles.items():
        before = time.perf_counter()
        pred = predict_experiment(exp, numerics=ns)
        results[grid] = pred
        counts = pred.counts
        assert counts.shape == (9,) and counts.dtype == np.float64
        assert np.isfinite(counts).all() and np.all(counts >= 0)
        assert len(pred.combined_prediction.components) == 6
        assert pred.combined_prediction.unit == 'events/bin'
        prediction[grid] = {'counts': counts.tolist(), 'seconds': time.perf_counter()-before,
                           'numerics': ns, 'total': float(counts.sum()), 'unit': pred.combined_prediction.unit}
    small = results['small']
    approximate = evaluate_experiment(exp, small)
    before = time.perf_counter()
    kernel = compile_fast(exp.model, numerics=exp.executor.settings(profiles['small']))
    fast = kernel.predict(model=exp.model, parameters=exp.executor.default_point(), numerics=exp.executor.settings(profiles['small']))
    np.testing.assert_allclose(fast.counts, small.counts, rtol=1e-10, atol=1e-12)
    fast_seconds = time.perf_counter()-before
    def copy_package(name):
        target = output/name
        target.mkdir()
        for file in ('experiment.input.yaml','experiment.resources.npz'):
            shutil.copy2(package/file, target/file)
        return target
    def document(target):
        return json.loads((target/'experiment.input.yaml').read_text('utf8'))
    changed = copy_package('parameter_perturbation')
    data = document(changed)
    p = data['parameters']['detector.gamma_b']
    p['value'] *= .99
    p['adopted_value'] = p['value']
    dump(changed/'experiment.input.yaml', data)
    altered = load_experiment_package(changed)
    old_mid = exp.model.observation.response.density(15.,20.,target=None)
    new_mid = altered.model.observation.response.density(15.,20.,target=None)
    altered_pred = predict_experiment(altered, numerics=profiles['small'])
    assert old_mid != new_mid and not np.allclose(altered_pred.counts, small.counts, rtol=1e-8)
    resource = copy_package('resource_perturbation')
    data = document(resource)
    with np.load(resource/'experiment.resources.npz',allow_pickle=False) as stored:
        arrays = {k: stored[k] for k in stored.files}
    key='nuclear_Cs133_M'
    arrays[key] *= 1.001
    np.savez(resource/'experiment.resources.npz', **arrays)
    data['resources']['sha256'] = hashlib.sha256((resource/'experiment.resources.npz').read_bytes()).hexdigest()
    data['resources']['arrays'][key]['sha256_raw_c_order'] = hashlib.sha256(arrays[key].tobytes()).hexdigest()
    dump(resource/'experiment.input.yaml',data)
    resource_pred = predict_experiment(load_experiment_package(resource),numerics=profiles['small'])
    assert not np.allclose(resource_pred.counts, small.counts, rtol=1e-8)
    tamper = {}
    for fault in ('archive_sha256','array_key','shape','dtype','unit','model_id','dependency','path','role','materialization'):
        target = copy_package('tamper_'+fault)
        data = document(target)
        meta = data['resources']['arrays']['nuclear_Cs133_M']
        if fault == 'archive_sha256': data['resources']['sha256']='0'*64
        elif fault == 'array_key': data['resources']['arrays'].pop('nuclear_Cs133_M')
        elif fault == 'shape': meta['shape'][-1]+=1
        elif fault == 'dtype': meta['dtype']='float32'
        elif fault == 'unit': meta['unit']='PE'
        elif fault == 'model_id': data['models']['legacy_csi_gamma']['model_id']='unregistered'
        elif fault == 'dependency': data['models']['legacy_csi_gamma']['depends_on']=['legacy_csi_gamma']
        elif fault == 'path': data['resources']['archive']='../escape.npz'
        elif fault == 'role': data['parameters']['detector.gamma_a']['role']='reference_only'
        else: data['resources']['arrays']['source_fluence_e']['generation']['dependency_fingerprint']='0'*64
        dump(target/'experiment.input.yaml',data)
        try: load_experiment_package(target)
        except ValueError as error: tamper[fault]={'status':'PASS','error':str(error)[:1500]}
        else: raise AssertionError('tampering not rejected: '+fault)
    moved = copy_package('moved_package')
    moved_pred = predict_experiment(load_experiment_package(moved),numerics=profiles['small'])
    np.testing.assert_array_equal(moved_pred.counts,small.counts)
    delta = results['refined'].counts-results['default'].counts
    report = {'status':'PASS','checks':{f'I{i:02d}':'PASS' for i in range(1,11)},
        'timings':{'parse_definition_seconds':parsed,'load_prepare_seconds':loaded,'small_fast_compile_predict_seconds':fast_seconds},
        'prediction':prediction,'legacy_approximate_chi2':float(approximate.chi2),'official_likelihood':'BLOCKED',
        'convergence':{'default_to_refined_max_abs':float(np.max(np.abs(delta))),
                       'max_relative':float(np.max(np.abs(delta)/np.maximum(np.abs(results['refined'].counts),1e-30))),
                       'status':'DIAGNOSTIC_ONLY; no external accuracy target or convergence approval'},
        'parameter_perturbation':{'parameter':'detector.gamma_b','factor':.99,'old_intermediate':float(old_mid),
             'new_intermediate':float(new_mid),'counts_delta':(altered_pred.counts-small.counts).tolist()},
        'resource_perturbation':{'key':key,'factor':1.001,'counts_delta':(resource_pred.counts-small.counts).tolist()},
        'tamper':tamper,'runtime_package_files':sorted(p.name for p in package.iterdir()),
        'cwd':str(Path.cwd()),'engine_import':str(__import__('cevns_pyeft').__file__),
        'accessed_output_files':sorted(access),'memory':{'status':'NOT_MEASURED; process timing only'}}
    dump(output/'standalone_results.json',report)
    np.savez(output/'package_predictions.npz', **{k: v.counts for k,v in results.items()})
    print('I01-I10 PASS; isolated two-file engine prediction complete')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--source-root')
    parser.add_argument('--worker',action='store_true')
    args=parser.parse_args()
    worker(args) if args.worker else driver(args)
