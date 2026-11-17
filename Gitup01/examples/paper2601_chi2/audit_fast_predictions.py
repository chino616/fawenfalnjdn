"""Native Slow, operator Fast, interpolation, polynomial and cache audit.

Four-operator comparisons cover the current CsI/Ar/CONUS NSI calculations,
including the far-valley minima. Every native comparison uses identical grids.
No production resource or previous numerical result is modified.
"""
from pathlib import Path
from dataclasses import asdict, replace
import argparse
import json
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
import run_benchmark as bench
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.kernels.compiler import compile_fast, CompiledKernel, reconstruct_channels, StaleCompiledKernelError
from cevns_pyeft.kernels.interface_storage import save_compiled_kernel, load_compiled_kernel
from cevns_pyeft.sources.composable import ScaledSource
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.contracts.validation import plain as record_plain

PREVIOUS = ROOT/'outputs/paper2601_chi2_20261111'
JOINT = ROOT/'outputs/paper2601_joint_audit_20261111'


def save(path, value):
    # Complex flavor coordinates are metadata, preserved as real/imag fields.
    bench.write_json(path, record_plain(value))


def make_point(values, weak_angle):
    return TheoryPoint(vector_nsi_to_np_wilson(VectorNSIParameters(**values)), sin2thetaW=weak_angle)


def comparison(left, right, label):
    if set(left.components) != set(right.components):
        raise ValueError(label+': component keys differ')
    rows = []
    for key in sorted(left.components):
        a, b = np.asarray(left.components[key]), np.asarray(right.components[key])
        delta = abs(a-b); tolerance = 1e-8+1e-10*abs(a)
        rows.append({'source_isotope': list(key), 'max_abs_events': float(delta.max()),
                     'max_relative_error_where_reference_gt_1e_minus_8': float(np.max(delta[a > 1e-8]/a[a > 1e-8])) if np.any(a > 1e-8) else None,
                     'passed': bool(np.all(delta <= tolerance))})
    delta = abs(left.counts-right.counts)
    passed = bool(np.all(delta <= 1e-8+1e-10*abs(left.counts))) and all(row['passed'] for row in rows)
    record = {'label': label, 'reference_total': float(left.counts.sum()), 'tested_total': float(right.counts.sum()),
              'max_abs_bin_events': float(delta.max()), 'components': rows, 'passed': passed}
    if not passed:
        raise ValueError('Fast/Slow discrepancy: '+json.dumps(record))
    return record


def tensor_comparison(left, right):
    # Normalize each target/source/channel block, preserving interference channels.
    delta = abs(left-right)
    scale = np.max(abs(left), axis=(-3, -2, -1), keepdims=True)
    normalized = delta/np.maximum(scale, np.finfo(float).tiny)
    value = float(np.max(normalized))
    if value > 2e-10:
        raise ValueError('Native/checked tensor difference: '+str(value))
    return {'max_normalized_target_source_channel_error': value,
            'normalization': 'max absolute H over operator_i/operator_j/bin within each target/source/channel'}


def raw_reconstruction(kernel, model, parameters):
    full = kernel.full_kernel if isinstance(kernel, CompiledKernel) else kernel['full_kernel']
    rhos = np.array([component.fixed_state_for_fast().rho for component in model.source.for_run(model.run).components])
    coeff = model.interaction.coefficient_values(parameters, bench.BASIS)
    channels = reconstruct_channels(full, coeff, rhos)
    pair = reconstruct_channels(full, coeff, rhos, representation='pair')
    error = float(np.max(abs(channels-pair)))
    raw = channels.sum(axis=2)
    return {'pair_full_max_abs_channel_events': error, 'negative_raw_component_bins': int(np.sum(raw < 0)),
            'most_negative_component_events': float(min(0., raw.min())),
            'sum_abs_negative_roundoff_events': float(np.sum(abs(raw[raw < 0])))}


def point_cases():
    joint = json.loads((JOINT/'SUMMARY.json').read_text(encoding='utf8'))
    mean = joint['two_parameter_minima']['previous_mean_Ar']['coordinates']
    asymmetric = joint['two_parameter_minima']['current_asymmetric_Ar']['coordinates']
    conus = joint['conus_conditioned_minimum_search']['best_fit']['coordinates']
    diag = lambda x, y: {'epsilon_ee_uV': x, 'epsilon_ee_dV': y}
    return [('SM', {}), ('small_vector', diag(.031, -.017)), ('near_cancellation', diag(.19, 0)),
            ('old_local_joint_minimum', diag(1.883801444255003, -1.3706225077261185)),
            ('corrected_mean_joint_minimum', diag(*mean)), ('current_asymmetric_joint_minimum', diag(*asymmetric)),
            ('CONUS_2d_minimum', diag(*conus)),
            ('complex_flavor_mixed', {'epsilon_ee_uV': .12, 'epsilon_ee_dV': -.08,
                                     'epsilon_emu_uV': .08+.03j, 'epsilon_emu_dV': -.04+.05j})]


def csi_ar(output, name, helper, cases):
    exp = bench.load_experiment(name, resources=bench.ResourceCatalog(ROOT))
    raw_model = exp.model
    checked = helper.CheckedCoefficientEnergy(raw_model.interaction)
    model = replace(raw_model, interaction=checked)
    weak = exp.definition.reproduction_sin2thetaW
    sequences = ([('small', {'n_er': 9, 'n_enu': 24, 'n_pe_bin': 7, 'pe_step': 2.}),
                  ('medium', {'n_er': 33, 'n_enu': 120, 'n_pe_bin': 16, 'pe_step': 1.})]
                 if name == 'CsI2021' else
                 [('small', {'n_er': 11, 'n_enu': 40, 'n_pe_bin': 8}),
                  ('medium', {'n_er': 41, 'n_enu': 240, 'n_pe_bin': 16})])
    records, arrays, guards = [], {}, []
    for grid_name, ns in sequences:
        selected = cases if grid_name == 'small' else [cases[i] for i in (0, 4, 7)]
        if name == 'CsI2021':
            settings = IntegrationSettings.legacy_csi2021_v1(**ns)
            native_kernel = compile_fast(raw_model, numerics=settings, basis_keys=bench.BASIS)
            checked_kernel = compile_fast(model, numerics=settings, basis_keys=bench.BASIS)
            fast = lambda p, k: k.predict(parameters=p)
        else:
            settings = exp.executor._settings(ns)
            native_kernel = bench.compile_profile(raw_model, settings, exp.executor.profile, basis_keys=bench.BASIS)
            checked_kernel = bench.compile_profile(model, settings, exp.executor.profile, basis_keys=bench.BASIS)
            fast = lambda p, k: bench.predict_profile_kernel(k, k_model(k), p, settings, exp.executor.profile)
            k_model = lambda k: raw_model if k is native_kernel else model
        h_native = native_kernel.full_kernel if name == 'CsI2021' else native_kernel['full_kernel']
        h_checked = checked_kernel.full_kernel if name == 'CsI2021' else checked_kernel['full_kernel']
        tensor = tensor_comparison(h_native, h_checked)
        for point_name, values in selected:
            started = time.perf_counter(); p = make_point(values, weak)
            slow = predict_experiment(exp, parameters=p, numerics=ns, backend='slow').combined_prediction
            full = fast(p, native_kernel); interpolated = fast(p, checked_kernel)
            row = {'point': point_name, 'couplings': values, 'grid_label': grid_name, 'grid': ns,
                   'native_Fast_vs_native_Slow': comparison(slow, full, name+' '+point_name),
                   'checked_energy_vs_native_Fast': comparison(full, interpolated, name+' checked energy'),
                   'coefficient_tensor': tensor, 'raw_and_pair': raw_reconstruction(native_kernel, raw_model, p),
                   'seconds': time.perf_counter()-started}
            records.append(row)
            arrays[grid_name+'_'+point_name+'_slow'] = slow.counts
            arrays[grid_name+'_'+point_name+'_fast'] = full.counts
            print(name, grid_name, point_name, 'Slow/Fast max', row['native_Fast_vs_native_Slow']['max_abs_bin_events'], flush=True)
        if name == 'CsI2021':
            for change, altered, num in [('numerics', raw_model, replace(settings, n_enu=settings.n_enu+1)),
                                         ('source', replace(raw_model, source=ScaledSource(raw_model.source, 1.01)), settings)]:
                try:
                    native_kernel.predict(model=altered, numerics=num)
                except StaleCompiledKernelError as exc:
                    guards.append({'changed': change, 'rejected': True, 'message': str(exc)})
                else:
                    raise ValueError('Stale CsI kernel accepted changed '+change)
            path = output/(name+'_'+grid_name+'_kernel.npz')
            save_compiled_kernel(path, native_kernel)
            loaded = load_compiled_kernel(path, model=raw_model, numerics=settings)
            comparison(native_kernel.predict(parameters=make_point(cases[4][1], weak)),
                       loaded.predict(parameters=make_point(cases[4][1], weak)), 'save/load far minimum')
        else:
            try:
                bench.predict_profile_kernel(native_kernel, raw_model, make_point({}, weak),
                                             {**settings, 'n_enu': settings['n_enu']+1}, exp.executor.profile)
            except ValueError as exc:
                guards.append({'changed': 'numerics', 'rejected': True, 'message': str(exc)})
            else:
                raise ValueError('Stale Ar kernel accepted changed numerics')
    # Rebuild the exact final grid and audit saved H and all scan coefficients.
    final = json.loads((PREVIOUS/(name+'_FORWARD.json')).read_text(encoding='utf8'))
    ns = final['runs'][-1]['grid']
    if name == 'CsI2021':
        settings = IntegrationSettings.legacy_csi2021_v1(**ns)
        fine = compile_fast(model, numerics=settings, basis_keys=bench.BASIS)
        fine_predict = lambda p: fine.predict(parameters=p)
        old_record = json.loads((PREVIOUS/(name+'_kernel_record.json')).read_text(encoding='utf8'))
        old_h = bench.load_npz(PREVIOUS/(name+'_kernel.npz'))['full_kernel']
        saved = CompiledKernel(model, settings, bench.BASIS, old_h, old_record)
        saved_predict = lambda p: saved.predict(parameters=p)
    else:
        settings = exp.executor._settings(ns)
        fine = bench.compile_profile(model, settings, exp.executor.profile, basis_keys=bench.BASIS)
        fine_predict = lambda p: bench.predict_profile_kernel(fine, model, p, settings, exp.executor.profile)
        old_record = json.loads((PREVIOUS/(name+'_kernel_record.json')).read_text(encoding='utf8'))
        old_h = bench.load_npz(PREVIOUS/(name+'_kernel.npz'))['full_kernel']
        saved = {'metadata': old_record, 'full_kernel': old_h, 'targets': old_record['targets']}
        saved_predict = lambda p: bench.predict_profile_kernel(saved, model, p, settings, exp.executor.profile)
    now_h = fine.full_kernel if name == 'CsI2021' else fine['full_kernel']
    identity = tensor_comparison(old_h, now_h)
    polynomial = bench.load_npz(PREVIOUS/(name+'_templates_grid8.npz'))['coefficients']
    fine_records = []
    for point_name, values in cases:
        p = make_point(values, weak); current = fine_predict(p); old = saved_predict(p)
        same = comparison(current, old, 'saved/current final '+name)
        poly_error = None
        if set(values) <= {'epsilon_ee_uV', 'epsilon_ee_dV'}:
            expected = bench.polynomial(polynomial, values.get('epsilon_ee_uV', 0), values.get('epsilon_ee_dV', 0))
            poly_error = float(np.max(abs(expected-current.counts)))
            if poly_error > 1e-8:
                raise ValueError(name+' final polynomial differs from public Fast at '+point_name)
        fine_records.append({'point': point_name, 'saved_vs_fresh': same, 'polynomial_max_abs_bin_events': poly_error,
                             'raw_and_pair': raw_reconstruction(fine, model, p)})
    result = {'dataset': name, 'native_Slow_comparisons': records, 'final_grid': ns,
              'final_saved_kernel_tensor': identity, 'final_public_Fast_comparisons': fine_records,
              'checked_energy_statistics': checked.statistics, 'stale_cache_guards': guards,
              'final_native_Slow_run': False,
              'scope': 'Full native Slow at identical small/medium grids; final-grid fresh/public cache, interpolation and polynomial checks; no claim of a full native final-grid Slow execution'}
    save(output/(name+'_FAST_AUDIT.json'), result)
    np.savez_compressed(output/(name+'_prediction_comparisons.npz'), **arrays)
    return result


def conus(output, helper, cases):
    folder = ROOT/'examples/CONUS_Plus/conusplus_kkl_run1/nsi_response'
    sys.path.insert(0, str(folder))
    import nsi_model as nsi
    raw_model = nsi.model(); checked = helper.CheckedCoefficientEnergy(raw_model.interaction)
    model = replace(raw_model, interaction=checked)
    weak = nsi.sm.POINT.sin2thetaW
    rows, arrays, guards = [], {}, []
    for label, er, enu in [('small', 9, 40), ('medium', 33, 161)]:
        settings = nsi.sm.settings(er, enu)
        native = compile_fast(raw_model, numerics=settings, basis_keys=bench.BASIS)
        approximate = compile_fast(model, numerics=settings, basis_keys=bench.BASIS)
        tensor = tensor_comparison(native.full_kernel, approximate.full_kernel)
        selected = cases if label == 'small' else [cases[i] for i in (0, 6, 7)]
        for point_name, values in selected:
            p = make_point(values, weak); started = time.perf_counter()
            slow = predict(raw_model, parameters=p, numerics=settings, backend='slow')
            fast = native.predict(parameters=p); energy = approximate.predict(parameters=p)
            row = {'grid': asdict(settings), 'point': point_name, 'couplings': values,
                   'native_Fast_vs_native_Slow': comparison(slow, fast, 'CONUS '+point_name),
                   'checked_energy_vs_native_Fast': comparison(fast, energy, 'CONUS checked energy'),
                   'coefficient_tensor': tensor, 'raw_and_pair': raw_reconstruction(native, raw_model, p),
                   'seconds': time.perf_counter()-started}
            rows.append(row)
            arrays[label+'_'+point_name+'_slow'] = slow.counts
            arrays[label+'_'+point_name+'_fast'] = fast.counts
            print('CONUS+', label, point_name, 'Slow/Fast max', row['native_Fast_vs_native_Slow']['max_abs_bin_events'], flush=True)
        path = output/('CONUS_'+label+'_kernel.npz'); save_compiled_kernel(path, native)
        loaded = load_compiled_kernel(path, model=raw_model, numerics=settings)
        comparison(native.predict(parameters=make_point(cases[6][1], weak)), loaded.predict(parameters=make_point(cases[6][1], weak)), 'CONUS save/load')
        try:
            native.predict(numerics=replace(settings, n_enu=settings.n_enu+1))
        except StaleCompiledKernelError as exc:
            guards.append({'changed': 'numerics', 'rejected': True, 'message': str(exc)})
        else:
            raise ValueError('CONUS stale kernel accepted different grid')
    settings = nsi.sm.settings(161, 641)
    fine = compile_fast(model, numerics=settings, basis_keys=bench.BASIS)
    polynomial = bench.load_npz(PREVIOUS/'../CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_quadratic_templates.npz')['diag_ud'][[0, 2, 1, 5, 4, 3]]
    old_path = ROOT/'outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_operator_kernel_161_641.npz'
    # Public loading must not silently ignore the migration/code fingerprint.
    try:
        old = load_compiled_kernel(old_path, model=raw_model, numerics=settings)
        cache_status = {'accepted_by_public_loader': True}
    except StaleCompiledKernelError as exc:
        cache_status = {'accepted_by_public_loader': False, 'exception': type(exc).__name__, 'message': str(exc),
                        'handling': 'Recompiled from current model; did not bypass dependency check'}
    with np.load(old_path, allow_pickle=False) as stored:
        old_h = stored['full_kernel'].copy()
    tensor = tensor_comparison(old_h, fine.full_kernel)
    fine_rows = []
    for point_name, values in cases:
        p = make_point(values, weak); current = fine.predict(parameters=p)
        poly_error = None
        if set(values) <= {'epsilon_ee_uV', 'epsilon_ee_dV'}:
            expected = bench.polynomial(polynomial, values.get('epsilon_ee_uV', 0), values.get('epsilon_ee_dV', 0))
            poly_error = float(np.max(abs(expected-current.counts)))
            if poly_error > 1e-8:
                raise ValueError('CONUS old polynomial differs from fresh current fine Fast')
        fine_rows.append({'point': point_name, 'fresh_total': float(current.counts.sum()),
                          'polynomial_max_abs_bin_events': poly_error,
                          'raw_and_pair': raw_reconstruction(fine, model, p)})
    save_compiled_kernel(output/'CONUS_current_fine_kernel.npz', fine)
    result = {'dataset': 'CONUS_plus', 'native_Slow_comparisons': rows, 'final_grid': asdict(settings),
              'final_native_Slow_run': False, 'original_cache_loading': cache_status,
              'old_vs_fresh_fine_tensor': tensor, 'final_public_Fast_comparisons': fine_rows,
              'checked_energy_statistics': checked.statistics, 'stale_cache_guards': guards,
              'scope': 'Native Slow at identical small/medium grids; fresh final-grid kernel and adopted polynomial comparison; old-migration cache identity rejection is retained explicitly'}
    save(output/'CONUS_FAST_AUDIT.json', result)
    np.savez_compressed(output/'CONUS_prediction_comparisons.npz', **arrays)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    allowed = {'PLAN_AND_BASELINE.json', 'fast_contract_regression.xml', 'pytest_tmp', 'first_pass'}
    if any(p.name not in allowed for p in out.iterdir()):
        parser.error('Choose fresh Fast-audit output')
    start = time.perf_counter()
    helper = bench.import_file('_paper2601_csi_nsi', 'examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py')
    cases = point_cases()
    results = {}
    for name in ('CsI2021', 'Ar2020'):
        results[name] = csi_ar(out, name, helper, cases)
    results['CONUS_plus'] = conus(out, helper, cases)
    maximum = max(row['native_Fast_vs_native_Slow']['max_abs_bin_events'] for result in results.values() for row in result['native_Slow_comparisons'])
    polynomial_maximum = max((row['polynomial_max_abs_bin_events'] or 0.) for result in results.values() for row in result['final_public_Fast_comparisons'])
    summary = {'status': 'PASS_DECLARED_FAST_NUMERICAL_CHECKS', 'scientific_paper_reproduction': False,
               'native_Slow_cases': sum(len(result['native_Slow_comparisons']) for result in results.values()),
               'max_native_Slow_Fast_bin_difference_events': maximum,
               'max_final_polynomial_public_Fast_bin_difference_events': polynomial_maximum,
               'results': results, 'elapsed_seconds': time.perf_counter()-start,
               'limitations': ['Full final-grid native Slow was not executed; native low/medium comparisons and final-grid tensor/polynomial/cache checks are separate.',
                               'The current solar single-bin analysis is SM-only and uses no Fast kernel.',
                               'Passing Fast-Slow identities does not establish the paper data/response/statistical choices.']}
    save(out/'SUMMARY.json', summary)
    baseline_path = out/'PLAN_AND_BASELINE.json'
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding='utf8'))
        changed = [rel for rel, value in baseline['protected_inputs_and_runtime'].items() if bench.sha(ROOT/rel) != value]
        if changed:
            raise ValueError('Protected input/runtime changed: '+repr(changed))
        save(out/'PROTECTION.json', {'unchanged_input_runtime_files': len(baseline['protected_inputs_and_runtime']), 'changed': changed})
    files = [Path(__file__), HERE/'run_benchmark.py', HERE/'audit_joint_analysis.py',
             ROOT/'cevns_pyeft/kernels/compiler.py', ROOT/'cevns_pyeft/kernels/interface_storage.py',
             ROOT/'cevns_pyeft/experiments/package_profiles.py', ROOT/'cevns_pyeft/theory/li2026/coefficients.py']
    save(out/'SOURCE_MANIFEST.json', [{'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': bench.sha(p)} for p in files])
    write_report(out, summary)
    save(out/'FILES.json', [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': bench.sha(p)} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'FILES.json'])
    print(json.dumps({'status': summary['status'], 'native_cases': summary['native_Slow_cases'], 'max_event_difference': maximum,
                      'max_polynomial_difference': polynomial_maximum}), flush=True)


def write_report(out, result):
    lines = ['# Fast专项审计：数值范围与结果\n',
             '**本轮使用原生Slow作独立参考，所有对照固定相同网格。** 不以优化器修复或原图外边界接近作为Fast正确的证据。\n',
             '[详细数值](SUMMARY.json) · [输入保护](PROTECTION.json) · [源码指纹](SOURCE_MANIFEST.json) · '
             '[既有Fast合同回归](fast_contract_regression.xml) · [文件清单](FILES.json) · '
             '[联合分析修复](../paper2601_joint_audit_20261111/README.md) · [复算入口](../../examples/paper2601_chi2/README.md)\n',
             '| 模型 | 原生Slow/Fast点数 | 最大逐箱差/events | 最终网格多项式/Fast最大逐箱差 |\n|---|---:|---:|---:|']
    for name, row in result['results'].items():
        maximum = max(r['native_Fast_vs_native_Slow']['max_abs_bin_events'] for r in row['native_Slow_comparisons'])
        pm = max((r['polynomial_max_abs_bin_events'] or 0.) for r in row['final_public_Fast_comparisons'])
        lines.append(f'| {name} | {len(row["native_Slow_comparisons"])} | {maximum:.4g} | {pm:.4g} |')
    lines += ['\n逐点覆盖SM、小矢量扰动、干涉抵消、旧局部极小值、新找到的约(10.4,-9.3)与(10.7,-9.6)点、CONUS二维极小值、复数味非对角耦合。'
              '逐源、逐核素、逐bin数组另保存；不是只比较总事例数。\n',
              '核对层次：原生Slow→原生四算符Fast；原生Fast→经过原生probe验证的能量插值Fast；full→pair重建；最终网格fresh Fast→保存核/扫描多项式。'
              '每层有自己的误差和原始数组。未通过改变观测、响应或阈值迫使一致。\n',
              '## 缓存和裁剪\n',
              '改变物理源或积分网格时，旧核须拒绝；保存/加载须保持数值。原CONUS迁移前fine核的当前依赖检查结果记录在CONUS_FAST_AUDIT；'
              '如果身份不匹配，本次重新编译，未跳过检查。随后对比原始H及已采用多项式，区分元数据身份与数值内容。\n',
              '每个点记录full/pair逐通道差、裁剪前负分量bin数量及其事例数总量。干涉通道可为负，检查对象是通道相加后的物理分量，不能把每个干涉通道裁零。\n',
              '## 验证边界\n',
              '原生Slow在small/medium的同网格运行；最终高分辨网格重新编译、检查tensor/多项式和缓存身份。'
              '**没有声称已执行完整512×1920等最终网格的原生Slow。** 这些是不同核验，不把较小网格的通过改名为最终Slow收敛。\n',
              '太阳单bin当前为SM-only直接积分，没有被本轮当成具有Fast或ee NSI能力。通用22算符合同回归的覆盖见XML；'
              '本轮三个实验专属核的直接对照范围是实际使用的4个dim6算符。\n',
              '联合分析此前已确认的数值缺陷是狭长方向漏搜极小值；本次Fast检验与该结论分别保存。即使Fast与Slow一致，'
              'CsI/Ar观测语义、效率坐标、作者误差/相关性以及太阳缺失输入仍决定能否复现论文。\n',
              '[CsI逐点](CsI2021_FAST_AUDIT.json) · [Ar逐点](Ar2020_FAST_AUDIT.json) · [CONUS逐点](CONUS_FAST_AUDIT.json) · [返回outputs](../README.md)\n']
    (out/'README.md').write_text('\n'.join(lines), encoding='utf8')


if __name__ == '__main__':
    main()
