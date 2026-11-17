"""Fixed-point vector spectra through package loader, component override and Slow.

Masses and couplings are explicitly declared project test choices. They are not
the paper's fit points. This program does not fit data or generate Fig.4 limits.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.package_loader import load_experiment_package, read_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector
from cevns_pyeft.experiments.definition import plain


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def save(path, value):
    path.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')


def link(origin, target, label):
    return '[' + label + '](<' + os.path.relpath(target, origin.parent).replace('\\', '/') + '>)'


def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n|' + '|'.join('---' for _ in headers) + '|\n' + ''.join(
        '| ' + ' | '.join(str(x).replace('|', r'\|') for x in row) + ' |\n' for row in rows)


def prepare(base, point):
    return base if point['id'] == 'SM' else with_solar_light_vector(base,
        mass_MeV=point['mass_MeV'], coupling=point['coupling'], scenario=point['scenario'])


def run_point(base, point, output, config, resume):
    exp = prepare(base, point)
    directory = output / base.dataset_id / point['id']
    if directory.exists():
        if not resume:
            raise FileExistsError('Use a new output directory or --resume: ' + str(directory))
        stored = read(directory / 'RESULT.json')
        if stored['physics_fingerprint'] != exp.physics_fingerprint:
            raise ValueError('Physical input/component changed; use a new output directory')
        if stored['benchmark_point'] != point:
            raise ValueError('Benchmark point changed; use a new output directory')
        return stored
    directory.mkdir(parents=True)
    series = []
    for settings in config['numerics']['grids']:
        started = time.perf_counter()
        prediction = predict_experiment(exp, numerics={key: settings[key] for key in ['n_er', 'n_enu']})
        series.append(dict(settings, counts=prediction.counts.tolist(), total_events=float(prediction.counts.sum()),
            seconds=time.perf_counter() - started))
        print(base.dataset_id, point['id'], settings['label'], f'{prediction.counts.sum():.9f}', flush=True)
    checks = []
    for left, right, axis in [(1, 2, 'recoil'), (2, 3, 'neutrino_energy')]:
        a = np.asarray(series[left]['counts']); b = np.asarray(series[right]['counts'])
        delta = abs(b - a)
        tolerance = np.maximum(config['numerics']['absolute_tolerance_events'],
            config['numerics']['relative_tolerance'] * abs(b))
        checks.append({'axis': axis, 'absolute_difference': delta.tolist(),
            'relative_difference': (delta / np.maximum(abs(b), 1e-30)).tolist(),
            'tolerance_events': tolerance.tolist(), 'passed': bool(np.all(delta <= tolerance))})
    diag = prediction.combined_prediction.diagnostics
    arrays = {'counts': prediction.counts, 'observable_edges': np.asarray(exp.definition.observation.edges)}
    arrays.update({'counts_' + run: p.counts for run, p in prediction.detector_predictions.items()})
    for isotope, grid in diag['recoil_grids_keV'].items():
        arrays['recoil_' + isotope] = grid
        arrays['rate_per_tyr_keV_' + isotope] = diag['true_recoil_rates_per_tyr_keV'][isotope]
    np.savez_compressed(directory / 'prediction.npz', **arrays)
    result = {'date': config['date'], 'dataset_id': base.dataset_id, 'benchmark_point': point,
        'counts': prediction.counts.tolist(), 'total_events': float(prediction.counts.sum()), 'unit': 'events/bin',
        'per_run': {run: p.counts.tolist() for run, p in prediction.detector_predictions.items()},
        'components': {'/'.join(key): values.tolist() for key, values in prediction.combined_prediction.components.items()},
        'physics_fingerprint': exp.physics_fingerprint, 'actual_interaction': exp.model.interaction.describe().as_dict(),
        'execution_record': plain(prediction.record), 'normalization_ledger': plain(prediction.combined_prediction.normalization_record),
        'convergence': {'runs': series, 'checks': checks, 'passed': all(row['passed'] for row in checks)},
        'observable': plain(exp.definition.observation),
        'limits': config['limits'], 'scientific_acceptance': 'NOT_REVIEWED'}
    save(directory / 'RESULT.json', result)
    save(directory / 'PREPARED_MODEL.json', exp.describe())
    (directory / 'README.md').write_text('# ' + point['id'] + '\n\n' + point['parameter_provenance'] +
        '\n\n[Result and convergence](RESULT.json) · [Numerical arrays](prediction.npz) · [Actual Runtime assembly](PREPARED_MODEL.json)\n', encoding='utf8')
    if not result['convergence']['passed']:
        raise ArithmeticError('Numerical convergence failed; the candidate was saved without a PASS claim')
    return result


def signed_fold(base, target, grid, rate):
    """Fold a signed interference diagnostic; never pass it off as a positive signal."""
    model = base.model
    values = {}
    for index, (run, obs) in enumerate(zip(model.run_ids, model.observation)):
        if model.mode == 'xenon_basis':
            p = obs.bin_probabilities(target=target, recoil_keV=grid, binning=model.binning,
                component_id='solar_B8_all_flavors').values
            counts = np.trapezoid(rate[:, None] * p, grid, axis=0)
        else:
            density = rate * obs.acceptance(grid)
            edges = model.binning.axes[0].edges
            counts = np.array([np.trapezoid(density[(grid >= a) & (grid <= b)], grid[(grid >= a) & (grid <= b)])
                for a, b in zip(edges[:-1], edges[1:])])
        values[run] = counts * model.exposures_tyr[index] / (model.anchor_mass_kg / 1000)
    return values


def decomposition(base, point, result, dataset_out):
    vector = prepare(base, point).model.interaction
    sm = read(dataset_out / 'SM/RESULT.json')
    totals = {name: {run: np.zeros_like(np.asarray(sm['counts'])) for run in base.model.run_ids}
        for name in ['interference', 'pure_NP']}
    with np.load(dataset_out / 'SM/prediction.npz', allow_pickle=False) as arrays:
        for target in base.model.targets.isotopes:
            grid = arrays['recoil_' + target.isotope_id]
            rate = arrays['rate_per_tyr_keV_' + target.isotope_id]
            ratio = vector.charge_shift(target, grid) / vector.weak_charge(target, .23857)
            for name, factor in [('interference', 2 * ratio), ('pure_NP', ratio ** 2)]:
                folded = signed_fold(base, target, grid, rate * factor)
                for run, values in folded.items():
                    totals[name][run] += values
    parts = {name: sum(rows.values()) for name, rows in totals.items()}
    reconstructed = np.asarray(sm['counts']) + parts['interference'] + parts['pure_NP']
    computed = np.asarray(result['counts'])
    np.testing.assert_allclose(reconstructed, computed, rtol=5e-12, atol=1e-12)
    record = {'formula': 'N_total=N_SM+N_interference+N_NP, with integrands 1, 2*deltaQ/Q_SM, (deltaQ/Q_SM)^2',
        'method': 'Per-isotope true-recoil reweighting and signed Response integration on the same grid; cross-checks the direct vector Slow calculation.',
        'SM': sm['counts'], 'interference': parts['interference'].tolist(), 'pure_NP': parts['pure_NP'].tolist(),
        'reconstructed_total': reconstructed.tolist(), 'direct_total': result['counts'],
        'maximum_absolute_closure_error_events': float(np.max(abs(computed - reconstructed))),
        'per_run': {run: {name: rows[run].tolist() for name, rows in totals.items()} for run in base.model.run_ids},
        'signed_interference_not_clipped': True, 'passed': True}
    save(dataset_out / point['id'] / 'INTERFERENCE.json', record)
    return record


def xenon_context(base, package):
    files = []; backgrounds = []; observed_file = package / 'statistics/xenonnt_official_observed_bins.txt'
    observed = np.loadtxt(observed_file)[:, 4].reshape(2, 3)
    files.append({'file': observed_file.relative_to(ROOT).as_posix(), 'sha256': sha(observed_file),
        'source': 'R08 fixed author event CSV and native binning; XENONnT-C016; observed counts, not digitized best fit'})
    for index in [0, 1]:
        p = package / f'statistics/xenonnt_sr{index}_background_and_b8_early_release.npz'
        with np.load(p, allow_pickle=False) as arrays:
            exposure = base.model.exposures_tyr[index]
            components = []
            for key in ['ac', 'er', 'rg']:
                values = arrays[key + '_rate_per_tyr_bin']
                # AC/ER are four-dimensional; the neutron template additionally
                # has the two seven-point yield-variation axes. Select their
                # nominal [3,3] slice only when those axes actually exist.
                values = values[3, 3] if values.ndim == 6 else values
                components.append(values.sum(axis=(1, 2, 3)))
            backgrounds.append(sum(components) * exposure)
        files.append({'file': p.relative_to(ROOT).as_posix(), 'sha256': sha(p),
            'source': 'R17 original ac/er/rg HDF5 templates and statistical_model_base.yaml; XENONnT-C042/C045; B8 signal excluded from B'})
    return {'observed_per_run': observed.tolist(), 'background_per_run': np.asarray(backgrounds).tolist(),
        'files': files, 'source_scope': 'Nominal backgrounds for plotting only; no nuisance profiling or likelihood result.'}


COLORS = {'SM': '#172b4d', 'V10_g1': '#2b8cbe', 'V10_g2': '#df8b20', 'V10_g3': '#8c6bb1',
    'BL10_g2': '#159a7b', 'V1_g2': '#cb4c54', 'V100_g2': '#767676'}


def label(point):
    if point['id'] == 'SM': return 'SM'
    scenario = 'V' if point['scenario'] == 'universal' else 'B-L'
    return f"{scenario}: m={point['mass_MeV']:g} MeV, g={point['coupling']:.0e}"


def plot(base, results, config, dataset_out, context=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from scipy.stats import chi2
    primary = ['SM', 'V10_g1', 'V10_g2', 'V10_g3', 'BL10_g2']
    fig, axes = plt.subplots(1, 2, figsize=(13.3, 5.1), constrained_layout=True)
    if context:
        background = np.asarray(context['background_per_run']).sum(axis=0)
        observed = np.asarray(context['observed_per_run']).sum(axis=0)
        x = np.arange(1, 4)
        axes[0].bar(x, background, color='#d8dce6', width=.75, label='Nominal background')
        for sid in primary:
            point = next(p for p in config['points'] if p['id'] == sid)
            axes[0].plot(x, background + np.asarray(results[sid]['counts']), marker='o', ms=4,
                color=COLORS[sid], lw=2, label=label(point))
        alpha = 1 - .682689492137
        lower = np.where(observed > 0, .5 * chi2.ppf(alpha/2, 2*observed), 0)
        upper = .5 * chi2.ppf(1-alpha/2, 2*(observed+1))
        axes[0].errorbar(x, observed, yerr=[observed-lower, upper-observed], fmt='ko', ms=4, capsize=3, label='Observed')
        axes[0].set(xlabel='cS2 analysis bin ordinal', ylabel='Signal + background events / bin',
            title='Fixed-point reconstructed event spectra', xticks=x, ylim=(0, None))
        for point in config['points'][1:]:
            sid = point['id']
            axes[1].plot(x, np.asarray(results[sid]['counts']) / np.asarray(results['SM']['counts']),
                marker='o', ms=4, lw=2, color=COLORS[sid], label=label(point))
        axes[1].set(xlabel='cS2 analysis bin ordinal', ylabel='Signal / SM signal', xticks=x,
            title='Interference and mediator-mass dependence', ylim=(0, None))
        fig.suptitle('XENONnT: flavor-universal vector benchmarks\nNative SR0/SR1 bins summed by ordinal; public early Response', fontsize=13)
    else:
        edges = np.asarray(base.definition.observation.edges); x = (edges[:-1] + edges[1:]) / 2
        for sid in primary:
            point = next(p for p in config['points'] if p['id'] == sid)
            axes[0].stairs(np.asarray(results[sid]['counts']) / np.diff(edges), edges, color=COLORS[sid], lw=2, label=label(point))
        for point in config['points'][1:]:
            sid = point['id']
            axes[1].plot(x, np.asarray(results[sid]['counts']) / np.asarray(results['SM']['counts']),
                lw=2, color=COLORS[sid], label=label(point))
        axes[0].set(xlabel='True recoil energy [keVnr]', ylabel='Accepted projection events / keVnr',
            title='Computed true-recoil diagnostic (1.04 t yr)', xlim=(edges[0], edges[-1]), ylim=(0, None))
        axes[1].set(xlabel='True recoil energy [keVnr]', ylabel='Accepted projection / SM projection',
            title='No prediction in reconstructed electron bins', xlim=(edges[0], edges[-1]), ylim=(0, None))
        fig.suptitle('PandaX-4T US2: light-vector true-recoil benchmarks\nNe response remains missing; these are not Ne-ROI event counts', fontsize=13)
    axes[1].axhline(1, color='#333333', lw=.8, ls='--')
    for index, ax in enumerate(axes):
        ax.grid(alpha=.18)
        if context and index == 1:
            ax.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(.5, -.16), ncol=2, frameon=False)
        else:
            ax.legend(fontsize=7.7, loc='best')
    fig.savefig(dataset_out / 'events.png', dpi=190)
    plt.close(fig)


def dataset_report(base, row, results, decompositions, output, config, context):
    directory = output / base.dataset_id; path = directory / 'BENCHMARK_REPORT.md'
    package = ROOT / row['path']; data, arrays = read_package(package)
    run = ROOT / 'workflows/cevns-pyeft/runs' / row['family'] / base.dataset_id
    register = read(run / 'P00_SOURCE_REGISTER.yaml'); sources = {s['source_id']: s for s in register['sources']}
    xenon = row['family'] == 'XENONnT'
    def cite(ids):
        return '\n'.join('- [' + sid + '] ' + sources[sid]['citation'] for sid in ids) + '\n'
    text = f'# {base.dataset_id}: vector benchmark\n\n**{config["date"]}, DRAFT/PARTIAL.** 固定点前向谱；数值质量/耦合为项目测试选择，不是论文拟合点或90% CL边界。\n\n'
    text += ' · '.join([link(path, output / 'REPORT.md', '共享模型与期刊原始公式'),
        link(path, ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json', '显式测试点卡'),
        link(path, directory / 'events.png', '事例数图'), link(path, package / 'experiment.physics.md', '正式输入与逐项出处')]) + '\n\n'
    text += '<a id="toc"></a>\n\n## 目录\n\n- [已有输入与来源](#inputs)\n- [结果](#results)\n- [验证与缺口](#checks)\n\n<a id="inputs"></a>\n\n## 已有输入与来源\n\n'
    text += table(['模块', '实际数值/数组', '本地数值与直接出处'], [
        ['Source', f'Φ=5.46e6 cm⁻²s⁻¹；829点f(E)，{arrays["source_energy_MeV"][0]:g}–{arrays["source_energy_MeV"][-1]:g} MeV；积分0.999986544',
            link(path, package / 'experiment.resources.npz', 'source_energy_MeV/source_shape_per_MeV') + '；R04官网b8spectrum.txt第一/二列；R01 PDF p5式(11)后给总通量，不重新归一化'],
        ['Target', '天然Xe九核素A=' + ','.join(str(int(a)) for a in arrays['target_mass_number']) + '；1t核数为代数锚点，非实测质量',
            link(path, package / 'experiment.resources.npz', 'target_mass_number/target_atomic_mass_u/target_number_fraction') + '；R09 NIST Xe全部九行。原子质量用于核数，动力学扣54电子质量，见正式参数卡'],
        ['SM与新模型', 'sin²θW=0.23857；KN R=1.23 A^(1/3)fm、a=0.7fm；V κ=1，B−L κ=−1/3',
            'R01 PDF p3式(1)–(3)；R19正式期刊版PDF p5/印刷p4式(2.6),(2.10)。C_V=3Ag²；旧v1记号冲突没有静默混用'],
        ['Response' if xenon else '接受度投影', '每run [16,10,10,3]概率基底，Ly/Qy中位数各501点；支撑0.51–5keVnr' if xenon else '99节点Total(US2)接受度；27个真实反冲箱，非Ne箱',
            link(path, package / 'experiment.resources.npz', '完整响应/产额数组' if xenon else 'efficiency_energy_keV/efficiency') + ('；R17 orthonormal_basis/原HDF5对shadow/S1BDT/S2BDT求和；YBe median JSON；已有选取只施加一次' if xenon else '；R02 2407.10892v3 PDF p3 Fig.1黑色Total(US2)99节点；P(Ne-bin|T)仍为MISSING')],
        ['曝光/Observable', 'SR0=1.174398、SR1=2.342593 t·yr；各自三箱按序号求和' if xenon else '1.04t·yr；0.3–3keVnr区间的27个投影箱',
            'R17 statistical_model_base.yaml livetime_sr0/1与原HDF5 /bins/0；合计3.516991，未改为论文打印3.51' if xenon else 'R02 PDF p3 US2总曝光；本轮箱边界沿用正式包的项目输出坐标，不称为原始Ne边界'],
        ['新参数', 'm=1/10/100MeV；g=1/2/3×10⁻⁵（各点组合见下表）',
            '数值为PROJECT_BENCHMARK_CHOICE，直接采用源为显式测试点卡；R19只提供模型定义与κ，不提供这些测试点的实验依据']])
    text += '\n### 本节参考文献\n\n' + cite(['R01', 'R04', 'R09', 'R17' if xenon else 'R02'])
    text += '\n- [R19] ' + config['formula_source']['citation'] + ' ' + link(path, ROOT / config['formula_source']['file'], '期刊原件') + '；PDF p5，印刷p4。\n'
    if xenon:
        text += '\nSR0原生cS2边界：' + str(arrays['cs2_edges_SR0'].tolist()) + ' PE；SR1：' + str(arrays['cs2_edges_SR1'].tolist()) + ' PE。两个run的箱边界不同，合计图只相加同序号箱。\n'
        text += '\n绘图观测与背景直接文件：\n\n' + table(['文件', '来源与处理'], [[link(path, ROOT / f['file'], Path(f['file']).name), f['source']] for f in context['files']])
        text += '\nD合计37；名义AC/ER/neutron背景合计' + f'{np.sum(context["background_per_run"]):.9f}' + '事例。均只用于作图，无背景profiling；误差棒为项目计算的68.268949% Garwood Poisson区间。\n'
    text += '\n[返回目录](#toc)\n\n<a id="results"></a>\n\n## 结果\n\n'
    headers = ['点', 'm [MeV]', 'g', 'κ'] + (['箱1', '箱2', '箱3'] if xenon else []) + ['总信号/投影 [events]', '相对SM总量']
    rows = []
    for point in config['points']:
        result = results[point['id']]
        rows.append([point['id'], point['mass_MeV'] if point['mass_MeV'] is not None else '—', point['coupling'], point.get('kappa', '—')]
            + ([f'{v:.9f}' for v in result['counts']] if xenon else [])
            + [f'{result["total_events"]:.9f}', f'{result["total_events"]/results["SM"]["total_events"]:.9f}'])
    text += table(headers, rows)
    if not xenon:
        text += '\n**全部数字均为真实反冲接受度加权投影，不是Ne∈[4,8]的重建事件数，不能与论文Ne拟合总数取复现比。**\n'
    text += '\n带符号分解：\n\n' + table(['点', 'SM总量', '干涉项', '纯NP项', '总量', '闭合最大误差 [events]'], [
        [sid, f'{sum(record["SM"]):.9f}', f'{sum(record["interference"]):.9f}', f'{sum(record["pure_NP"]):.9f}',
         f'{sum(record["direct_total"]):.9f}', f'{record["maximum_absolute_closure_error_events"]:.3g}'] for sid, record in decompositions.items()])
    text += '\n' + link(path, directory / 'events.png', '查看图') + ' · ' + link(path, directory / 'counts_by_point.tsv', '全部逐箱TSV') + '\n\n'
    text += '\n'.join('- ' + link(path, directory / p['id'] / 'RESULT.json', p['id'] + '：数组、run/核素分量、参数与收敛') for p in config['points']) + '\n'
    text += '\n[返回目录](#toc)\n\n<a id="checks"></a>\n\n## 验证与缺口\n\n'
    text += table(['点', '最大T加密差异', '最大Eν加密差异', '数值验收'], [
        [sid, f'{max(r["convergence"]["checks"][0]["relative_difference"])*100:.6g}%',
         f'{max(r["convergence"]["checks"][1]["relative_difference"])*100:.6g}%', 'PASS' if r['convergence']['passed'] else 'FAIL'] for sid, r in results.items()])
    text += '\n预定条件逐箱max(2×10⁻⁴ events, 0.2%)；T和Eν分别加密，另含正式源/响应/产额断点。SM与上一轮保存的SM输出逐箱核对。新相互作用通过组件描述与源文件哈希形成独立physics fingerprint；旧输入包及SM数值不改写。\n\n'
    text += ('XENONnT已完成本组参数点的重建谱计算。响应仍为官方早期重铸版本，其与原2024分析的精确等价性未认证；本轮无实验提供的非零新物理信号模板，所以解析极限/分解闭合不等于外部论文曲线复现。' if xenon else
        'PandaX仍缺US2的P(Ne-bin|T)，只阻断Ne重建谱和依赖它的拟合。没有从平均Qy猜出Poisson/Gaussian宽度，也不加c_i。')
    text += '\n\n下一步能力交接：传统接触ε或味非普适NSI需要独立的耦合定义与太阳入射态；S/A/T需要相应标量输入或自旋结构函数核验。本轮没有生成它们，也未计算Fig.4的χ²/90% CL边界。\n\n[返回目录](#toc)\n'
    path.write_text(text, encoding='utf8')
    (directory / 'README.md').write_text('# ' + base.dataset_id + '\n\n' + link(directory / 'README.md', path, '完整计算与来源报告') +
        ' · [Figure](events.png) · [All bins](counts_by_point.tsv) · [Runtime summary](DATASET_RESULT.json)\n\n' +
        ('Reconstructed cS2 event spectra.' if xenon else 'True-recoil diagnostic only; Ne response missing.') + '\n', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/solar_b8_vector/20261108_run1')
    parser.add_argument('--resume', action='store_true', help='reuse only numerical points with the same component/input fingerprint')
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    config = read(args.config)
    assert config['numerics']['grids'][-1] == {'label': 'energy_refined', 'n_er': 801, 'n_enu': 480}
    assert len({p['id'] for p in config['points']}) == len(config['points'])
    assert config['points'][0]['id'] == 'SM'
    assert all(re.fullmatch(r'[A-Za-z0-9_]+', p['id']) for p in config['points'])
    assert sha(ROOT / config['formula_source']['file']) == config['formula_source']['sha256']
    save(output / 'BENCHMARK_CONFIG.json', config)
    datasets = []
    for row in config['packages']:
        package = ROOT / row['path']
        assert sha(package / 'experiment.input.yaml') == row['input_sha256']
        assert sha(package / 'experiment.resources.npz') == row['arrays_sha256']
        base = load_experiment_package(package)
        old = read(ROOT / row['SM_reference_output'] / 'SM_RESULT.json')
        assert base.physics_fingerprint == old['physics_fingerprint']
        results = {point['id']: run_point(base, point, output, config, args.resume) for point in config['points']}
        np.testing.assert_allclose(results['SM']['counts'], old['counts'], rtol=1e-14, atol=1e-14)
        directory = output / base.dataset_id
        decompositions = {p['id']: decomposition(base, p, results[p['id']], directory) for p in config['points'][1:]}
        context = xenon_context(base, package) if row['family'] == 'XENONnT' else None
        if context: save(directory / 'OBSERVED_BACKGROUND.json', context)
        plot(base, results, config, directory, context)
        counts = np.column_stack([results[p['id']]['counts'] for p in config['points']])
        np.savetxt(directory / 'counts_by_point.tsv', counts, delimiter='\t',
            header='events/bin; columns=' + ','.join(p['id'] for p in config['points']))
        dataset_report(base, row, results, decompositions, output, config, context)
        summary = {'dataset_id': base.dataset_id, 'results': results, 'decomposition': decompositions,
            'SM_previous_output_matched': True, 'source_package_sha256': row['input_sha256'],
            'source_array_sha256': row['arrays_sha256'], 'scientific_status': 'DRAFT/PARTIAL; fixed-point spectra, no fit',
            'observable': plain(base.definition.observation)}
        save(directory / 'DATASET_RESULT.json', summary); datasets.append(summary)
    report = output / 'REPORT.md'
    text = '# Solar 8B：轻矢量NSI/NGI benchmark\n\n**' + config['date'] + '，新版本，DRAFT/PARTIAL。** 延续事例数图任务，完成味普适V与B−L固定参数前向计算；不是Fig.4排除限拟合。参数数值为本项目测试选择，不冒充文献拟合点。\n\n'
    text += '<a id="toc"></a>\n\n## 目录\n\n- [共享模型与版本](#model)\n- [测试点和结果](#results)\n- [复算与限制](#reproduce)\n\n<a id="model"></a>\n\n## 共享模型与版本\n\n'
    text += 'SM核、运动学与单位复用原共享模块；新组件只改变相干弱荷。采用正式期刊版PDF p5（印刷p4）式(2.6)、(2.10)：\n\n$$\n' + r'\Delta Q_A(T)=\frac{\kappa\,3A g^2}{\sqrt{2}G_F(m_V^2+2m_A T)},\qquad Q_{A,\rm total}=Q_{A,\rm SM}+\Delta Q_A(T).' + '\n$$\n\n'
    text += 'κ=1（V）、−1/3（B−L）；g无量纲，m_V在卡中用MeV，截面内统一转GeV，T从keVnr转GeV。分母为GeV²，G_F单位GeV⁻²，所以ΔQ无量纲。g是该论文定义的共同有效耦合，B−L相对电荷已由κ处理。\n\n'
    text += '$$\n' + r'\frac{d\sigma}{dT}=\frac{G_F^2m_A}{\pi}F_W^2(q^2)\left(1-\frac{m_AT}{2E_\nu^2}-\frac{T}{E_\nu}\right)(Q_{A,\rm SM}+\Delta Q_A)^2.' + '\n$$\n\n'
    text += '计算中调用已有SM核再做弱荷比值，完全保留SM单位与弹性端点；弱荷为零时用非零参考弱荷作代数归一化，避免除零。SM与新项在振幅中先相加再平方。信号分解为：\n\n$$\n' + r'N_i=N_i^{\rm SM}+N_i^{\rm int}+N_i^{\rm NP},\qquad (Q+\Delta Q)^2=Q^2+2Q\Delta Q+(\Delta Q)^2.' + '\n$$\n\n'
    text += '干涉项允许为负，未剪裁；每个核素在真实反冲T上求值，再通过相同Response折叠。不是对全实验总数乘一个常数。均为味普适对角模型，因此本轮无需太阳味分解或MSW概率表。\n\n'
    text += '**版本核验：** arXiv:2411.11749v1 PDF p4式(10)印为C_V²，正式期刊版式(2.10)已明确C_V=3Ag²。新组件显式采用期刊定义；原SM所用v1、源谱和Response不变。此处不是从sqrt(3A)g代入v1得到的结果。\n\n'
    text += '- [R19] ' + config['formula_source']['citation'] + ' ' + link(report, ROOT / config['formula_source']['file'], '已下载并核验的期刊原件') + '。SHA256 `' + config['formula_source']['sha256'] + '`。\n'
    text += '\n[返回目录](#toc)\n\n<a id="results"></a>\n\n## 测试点和结果\n\n'
    text += table(['点', '模型', 'm [MeV]', 'g', '参数数值来源'], [[p['id'], p['scenario'], p['mass_MeV'] if p['mass_MeV'] else '—', p['coupling'], '原正式SM卡' if p['id'] == 'SM' else '项目选取的测试点；非文献最佳拟合'] for p in config['points']])
    for dataset in datasets:
        directory = output / dataset['dataset_id']
        text += '\n### ' + dataset['dataset_id'] + '\n\n' + link(report, directory / 'BENCHMARK_REPORT.md', '本实验全部输入、具体出处、结果、分解及收敛') + ' · ' + link(report, directory / 'events.png', '图') + '\n\n'
        text += table(['点', 'SM+NP信号/投影总量 [events]'], [[p['id'], f'{dataset["results"][p["id"]]["total_events"]:.9f}'] for p in config['points']])
    text += '\n[返回目录](#toc)\n\n<a id="reproduce"></a>\n\n## 复算与限制\n\n'
    text += '从原项目根目录运行：\n\n```powershell\npython -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/repeat_run\n```\n\n标准Runtime入口示例：\n\n```python\nfrom cevns_pyeft.experiments.solar_vector import load_solar_light_vector\nfrom cevns_pyeft.experiments.runtime import predict_experiment\nexperiment = load_solar_light_vector("data/experiments/XENONnT/XENONnT_2024_SolarB8", mass_MeV=10., coupling=2e-5, scenario="universal")\nresult = predict_experiment(experiment, numerics={"n_er": 801, "n_enu": 480})\nprint(result.counts)\n```\n\n'
    text += '\n'.join('- ' + item for item in config['limits']) + '\n\n外部论文未给这些非零测试点的逐箱参考模板，当前验证等级为解析极限、内部闭合和积分收敛；不称为论文非零点或官方likelihood复现通过。全程未引入c_i。\n\n[返回目录](#toc)\n'
    report.write_text(text, encoding='utf8')
    save(output / 'BENCHMARK_SUMMARY.json', {'date': config['date'], 'config_sha256': sha(args.config),
        'runner_sha256': sha(Path(__file__)), 'datasets': datasets, 'status': 'DRAFT/PARTIAL; no fit; PandaX Ne missing'})
    (output / 'README.md').write_text('# Solar 8B vector benchmark\n\n' + link(output / 'README.md', report, '模型、测试点、全部计算报告和来源') +
        ' · [Summary](BENCHMARK_SUMMARY.json) · [Input card](BENCHMARK_CONFIG.json) · [Preservation baseline](PRESERVATION_BASELINE.json)\n\n' +
        '\n'.join('- ' + link(output / 'README.md', output / d['dataset_id'] / 'README.md', d['dataset_id']) for d in datasets) + '\n', encoding='utf8')
    print('Completed fixed-point vector spectra; no chi2/CL contours were computed.', flush=True)


if __name__ == '__main__':
    main()
