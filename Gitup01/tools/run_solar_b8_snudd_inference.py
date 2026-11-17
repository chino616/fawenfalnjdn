"""Full three-sample Eq88 inference for the pinned external SNuDD model.

Same source card, nuclear Response, Total acceptance, and fitted-yield data as
v3.4. The scan evaluates the exact ee-specialized upstream radial quadrature;
direct full-rho Runtime predictions independently validate the representation.
Old runs are read-only. Each tail/propagation control subtracts its own minimum.
"""
from pathlib import Path
import argparse
import importlib.util
import shutil
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.experiments.definition import plain
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from extensions.solar_rho_snudd.experiment import load_snudd
from extensions.solar_rho_snudd.protocol import CARD, read, save, sha
from extensions.solar_rho_snudd.scan import ScanSource, ScanJoint
from tools.run_solar_b8_nsi_benchmark import crossings, reference_crossings, simultaneous_pull_check

SAMPLES = ('PandaX_paired', 'PandaX_US2', 'XENONnT')
MODES = ('flat_sensitivity', 'zero', 'unit', 'profile_bounds')
OLD = ROOT / 'outputs/external/solar_rho_snudd/20261112_run1'
REFERENCE = ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run2/source_evidence/paper_fig4_green_reference.json'


def assemble(out):
    """Load actual PreparedExperiments; only rebind if all fold inputs match."""
    experiments, kernels, shared = [], [], None
    for sample in SAMPLES:
        e = load_snudd(sample, cache_root=out / 'validation_cache', interaction=shared)
        shared = e.model.interaction
        old = SolarNSIKernel.load(OLD / 'kernels' / (sample+'.npz'))
        k = old.rebind_state(e)  # validates fold_dependency_digest, no bypass
        k.validate(e, k.record['numerics'], nsi_point())
        if not np.array_equal(k.values, old.values):
            raise ValueError('unexpected change to nuclear/flux/detector fold')
        (out / 'kernels').mkdir(exist_ok=True)
        k.save(out / 'kernels' / (sample+'.npz'))
        save(out / sample / 'PREPARED_MODEL.json', e.describe())
        experiments.append(e)
        kernels.append(k)
    return tuple(experiments), tuple(kernels)


def direct_validation(model, experiments, kernels, points):
    """Direct isolated SNuDD -> full rho -> normal Runtime -> joint statistic."""
    source = np.loadtxt(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt')
    slow_energy = np.unique(np.r_[np.linspace(0., 16.56, 480), source[1:-1, 0]])
    union = np.unique(np.r_[slow_energy[slow_energy > 0], model.energy, [2., 5., 10., 15.]])
    model.runtime_state.prefetch(union, points)
    rows = []
    for i, (u, d) in enumerate(points):
        direct_rho = model.runtime_state.full_rho(model.energy, u, d)
        difference = float(np.max(abs(direct_rho-model.state.rho(model.energy, u, d))))
        if difference > 5e-12:
            raise ValueError('scan representation disagrees with full upstream rho')
        runtime_signals, runtime_chi2, slow_checks = [], [], []
        for e, k in zip(experiments, kernels):
            p = predict_experiment(e, parameters=nsi_point(u, d), backend='fast', kernel=k, numerics=k.record['numerics'])
            runtime_signals.append(float(p.counts[0]))
            runtime_chi2.append(float(evaluate_experiment(e, p).chi2))
            # Three new independent Slow integrations at the newly found minimum.
            if i == len(points)-1:
                slow = predict_experiment(e, parameters=nsi_point(u, d), numerics={'n_er': 801, 'n_enu': 480})
                diff = float(abs(slow.counts[0]-p.counts[0]))
                tolerance = float(max(3e-4, .002*abs(slow.counts[0])))
                if diff > tolerance:
                    raise ValueError('new minimum Slow/Fast validation failed')
                slow_checks.append({'sample': e.model.sample, 'fast': float(p.counts[0]), 'slow': float(slow.counts[0]),
                                    'absolute_difference': diff, 'tolerance': tolerance})
        signal_difference = float(np.max(abs(np.array(runtime_signals)-model.signals(u, d))))
        chi_difference = float(abs(sum(runtime_chi2)-model.chi2(u, d)))
        if signal_difference > 1e-9 or chi_difference > 1e-10:
            raise ValueError('Runtime and joint inference disagree')
        rows.append({'point': [u, d], 'full_rho_max_abs_difference': difference, 'runtime_signals': runtime_signals,
                     'scan_signals': model.signals(u, d).tolist(), 'signal_max_abs_difference': signal_difference,
                     'runtime_sample_chi2': runtime_chi2, 'joint_chi2': float(model.chi2(u, d)),
                     'chi2_abs_difference': chi_difference, 'new_slow_checks': slow_checks})
        print('Direct full-rho Runtime validated:', u, d, 'max rho diff', difference, flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/external/solar_rho_snudd/20261112_fig4_run2')
    parser.add_argument('--grid', type=int, default=601)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'outputs/external/solar_rho_snudd') or args.grid < 101:
        raise ValueError('independent external output and >=101 grid required')
    if (out / 'NSI_RESULTS.json').exists():
        raise FileExistsError('finalized inference runs are immutable; use a new directory')
    start = time.perf_counter()
    experiments, kernels = assemble(out)
    source = ScanSource(out / 'propagation_source')
    model = ScanJoint(experiments, kernels, source)
    fixed = ScanJoint(experiments, kernels, ScanSource(out / 'propagation_source', fixed_sm=True))
    minimums = {}
    for mode in MODES:
        print('Minimizing over certified full-plane domain:', mode, flush=True)
        minimums[mode] = model.minimize(mode)
        save(out / 'MINIMUMS.json', plain(minimums))
        print(mode, minimums[mode]['minimum'], flush=True)
    minimums['fixed_SM_propagation'] = fixed.minimize()
    save(out / 'MINIMUMS.json', plain(minimums))
    best = minimums['flat_sensitivity']['minimum']
    best_point = (best['epsilon_ee_uV'], best['epsilon_ee_dV'])
    direct = direct_validation(model, experiments, kernels,
        [(0., 0.), (.3, -.1), (-.4, .6), (0., .178), best_point])
    save(out / 'DIRECT_RUNTIME_VALIDATION.json', direct)

    line = np.linspace(-1., 1., args.grid)
    xx, yy = np.meshgrid(line, line, indexing='xy')
    u, d = xx.ravel(), yy.ravel()
    blocks = np.empty((len(u), 3, 2))
    for i in range(0, len(u), 768):
        blocks[i:i+768] = model.blocks(u[i:i+768], d[i:i+768])
        if i % (768*64) == 0:
            print('Scanning', i, '/', len(u), flush=True)
    raw, surfaces = {}, {}
    for mode in MODES:
        signals = np.clip(model.D, blocks[:, :, 0], blocks.sum(axis=-1)) if mode == 'profile_bounds' else (
            blocks[:, :, 0]+{'flat_sensitivity': model.epsilon_tail, 'zero': 0., 'unit': 1.}[mode]*blocks[:, :, 1])
        raw[mode] = np.sum((model.D-signals)**2/(model.sigma**2+model.pull**2*signals**2), axis=-1).reshape(xx.shape)
        surfaces[mode] = raw[mode]-minimums[mode]['minimum']['chi2']
    raw['fixed_SM_propagation'] = fixed.batch_grid(xx, yy)
    surfaces['fixed_SM_propagation'] = raw['fixed_SM_propagation']-minimums['fixed_SM_propagation']['minimum']['chi2']

    from matplotlib.path import Path as Polygon
    (out / 'source_evidence').mkdir(exist_ok=True)
    shutil.copy2(REFERENCE, out / 'source_evidence' / REFERENCE.name)
    reference = read(REFERENCE)
    polygons = [np.array(p) for p in reference['polygons']]
    paper_mask = np.any([Polygon(p).contains_points(np.c_[u, d]).reshape(xx.shape) for p in polygons], axis=0)
    own = surfaces['flat_sensitivity'] <= 4.61
    np.savez_compressed(out / 'solar_NSI_surfaces.npz', epsilon_ee_uV=line, epsilon_ee_dV=line,
        signal_known=blocks[:, :, 0].reshape((*xx.shape, 3)), signal_unselected_tail=blocks[:, :, 1].reshape((*xx.shape, 3)),
        paper_green_reference_mask=paper_mask, calculated_primary_allowed_mask=own,
        **{'raw_chi2_'+key: value for key, value in raw.items()}, **{'delta_chi2_'+key: value for key, value in surfaces.items()})
    rows = []
    for x in [-.75, -.5, 0., .5, .75]:
        row = {'epsilon_ee_uV': x, 'paper_green_reference': reference_crossings(polygons, x)}
        for mode in MODES:
            row[mode] = crossings(lambda a, b, mode=mode: model.chi2(a, b, mode), x, minimums[mode]['minimum']['chi2'])
        row['fixed_SM_propagation'] = crossings(fixed.chi2, x, minimums['fixed_SM_propagation']['minimum']['chi2'])
        rows.append(row)
    save(out / 'SLICE_BOUNDARIES.json', rows)
    previous = read(ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run2/PAPER_COMPARISON.json')
    comparison = {'paper': reference['paper'], 'paper_pdf_sha256': reference['sha256'], 'reference_sha256': sha(REFERENCE),
        'paper_is_reference_only': True, 'grid_size': args.grid, 'comparison_window': [-1., 1.],
        'intersection_over_union': float(np.sum(own & paper_mask)/np.sum(own | paper_mask)),
        'calculated_allowed_fraction': float(own.mean()), 'paper_allowed_fraction': float(paper_mask.mean()),
        'intersection_fraction': float((own & paper_mask).mean()), 'symmetric_difference_fraction': float((own ^ paper_mask).mean()),
        'previous_local_B16_IoU': previous['intersection_over_union'],
        'counterexample': {'point': [0., .178], 'computed': model.detail(0., .178),
            'paper_membership': any(Polygon(p).contains_point((0., .178)) for p in polygons),
            'delta_chi2': float(model.chi2(0., .178)-best['chi2'])},
        'slice_boundaries': 'SLICE_BOUNDARIES.json',
        'status': 'CALCULATED_SOLAR_REGION_DIFFERS_FROM_PAPER; NO_TUNING_TO_GRAPHIC'}
    save(out / 'PAPER_COMPARISON.json', comparison)
    packets = [read(p) for p in (out / 'validation_cache').glob('*/manifest.json')]
    result = {'date': '2026-11-12', 'analysis': 'paper2601 single-bin solar ee-vector NSI with pinned SNuDD day propagation',
        'sample_order': list(SAMPLES), 'SM': model.detail(0., 0.), 'primary_minimum': minimums['flat_sensitivity'],
        'controls': {k: v for k, v in minimums.items() if k != 'flat_sensitivity'},
        'plot_window_grid_minimum': {'chi2': float(raw['flat_sensitivity'].min()), 'point': [float(xx.flat[np.argmin(raw['flat_sensitivity'])]), float(yy.flat[np.argmin(raw['flat_sensitivity'])])],
                                     'role': 'diagnostic only; NOT subtracted from the primary surface'},
        'delta_chi2_threshold': 4.61, 'DOF': 2, 'primary_tail': 'flat_sensitivity',
        'source_representation': read(out / 'propagation_source/manifest.json'),
        'statistical_data': {'D': model.D.tolist(), 'sigma_stat': model.sigma.tolist(), 'pull_sigmas': model.pull.tolist(), 'independent': True},
        'independent_pull_checks': [simultaneous_pull_check(model, *p) for p in [(0., 0.), (0., .178), best_point]],
        'direct_Runtime_validation': direct, 'paper_comparison': comparison,
        'source_packets': [{'identity': p['input_identity'], 'adiabatic_diagnostic': p['adiabatic_diagnostic']} for p in packets],
        'source_card_sha256': sha(CARD), 'runner_sha256': sha(Path(__file__)),
        'host_imported_snudd': any(k == 'snudd' or k.startswith('snudd.') for k in sys.modules),
        'status': 'FULL_SOLAR_FIG4_STATISTICAL_CALCULATION_COMPLETE; EXACT_PAPER_REPRODUCTION_NOT_ESTABLISHED',
        'scientific_acceptance': 'NOT_REVIEWED',
        'limits': ['effective two-flavor adiabatic model, vacuum theta13, no Earth regeneration; large-NSI reduction not certified',
            'XENONnT2.77-3keV acceptance absent; primary last-value extrapolation, explicit zero/unit/profile controls',
            'same seven adopted Xe nuclear tables;124/126 omitted without renormalization; external author table certification unresolved',
            'paper exact oscillation/profile/nuclear input card unavailable; no fit to paper boundary'],
        'wall_seconds': time.perf_counter()-start}
    save(out / 'NSI_RESULTS.json', result)
    plot(out, line, surfaces, polygons, model, fixed, minimums, comparison)
    files = [Path(__file__), ROOT / 'extensions/solar_rho_snudd/scan.py', ROOT / 'extensions/solar_rho_snudd/scan_source.py']
    files += [Path(importlib.util.find_spec(name).origin) for name in experiments[0].record['implementation']]
    for p in set(files):
        dest = out / 'source' / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    save(out / 'SOURCE_FINGERPRINTS.json', {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in set(files)})
    print('Completed full SNuDD inference:', best, 'IoU=', comparison['intersection_over_union'], flush=True)


def plot(out, line, surfaces, polygons, model, fixed, minimums, comparison):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(7.6, 7.3), constrained_layout=True)
    ax.contourf(line, line, surfaces['flat_sensitivity'], levels=[-1., 4.61], colors=['#75b27d'], alpha=.7)
    ax.contour(line, line, surfaces['flat_sensitivity'], levels=[4.61], colors=['#176b2d'], linewidths=1.7)
    for p in polygons:
        ax.plot(p[:, 0], p[:, 1], color='#424242', ls='--', lw=1.1)
    ax.plot(0., 0., 'k+', ms=10)
    ax.plot(0., .178, 'o', color='#bb3535', ms=5)
    ax.set(xlim=(-1., 1.), ylim=(-1., 1.), xlabel=r'$\epsilon_{ee}^{uV}$', ylabel=r'$\epsilon_{ee}^{dV}$',
           title='PandaX-4T + XENONnT: solar single-bin NSI\n'+r'90%: $\Delta\chi^2 \leq 4.61$; SNuDD propagation + nuclear Response')
    ax.set_aspect('equal')
    ax.grid(alpha=.15)
    ax.legend(handles=[Patch(facecolor='#75b27d', alpha=.7, label='This calculation: joint solar region'),
        Line2D([], [], color='#424242', ls='--', label='2601.19883v2 Fig.4 green region boundary'),
        Line2D([], [], marker='+', ls='', color='k', label='SM (0, 0)'),
        Line2D([], [], marker='o', ls='', color='#bb3535', label='(0, 0.178): allowed here, excluded in paper')], fontsize=8, loc='lower left')
    fig.savefig(out / 'solar_Fig4_snudd_vs_paper.png', dpi=190)
    plt.close(fig)
    colors = {'flat_sensitivity': '#176b2d', 'zero': '#2174ab', 'unit': '#cc831b',
              'profile_bounds': '#84529b', 'fixed_SM_propagation': '#bb3535'}
    labels = {'flat_sensitivity': 'Last-value X tail (primary)', 'zero': 'Zero X tail', 'unit': 'Unit X tail',
              'profile_bounds': 'Profile unknown X tail', 'fixed_SM_propagation': 'Fixed SM propagation'}
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.5), constrained_layout=True)
    y = np.linspace(-.25, .65, 1201)
    for mode, color in colors.items():
        axes[0].contour(line, line, surfaces[mode], levels=[4.61], colors=[color], linewidths=1.3)
        values = fixed.chi2(np.zeros_like(y), y) if mode == 'fixed_SM_propagation' else model.chi2(np.zeros_like(y), y, mode)
        axes[1].plot(y, values-minimums[mode]['minimum']['chi2'], color=color, lw=1.4)
    axes[0].set(xlim=(-1., 1.), ylim=(-1., 1.), xlabel=r'$\epsilon_{ee}^{uV}$', ylabel=r'$\epsilon_{ee}^{dV}$', title='Separate controls: own joint minimum')
    axes[0].set_aspect('equal')
    axes[0].legend(handles=[Line2D([], [], color=c, label=labels[m]) for m, c in colors.items()], fontsize=7.4, loc='lower left')
    axes[1].axhline(4.61, color='k', ls=':', lw=1.)
    axes[1].set(xlabel=r'$\epsilon_{ee}^{dV}$ at $\epsilon_{ee}^{uV}=0$', ylabel=r'$\Delta\chi^2$ relative to 2D minimum',
                ylim=(0., 10.), title='Actual likelihood slice')
    for ax in axes:
        ax.grid(alpha=.15)
    fig.savefig(out / 'solar_snudd_controls.png', dpi=180)
    plt.close(fig)
    best = minimums['flat_sensitivity']['minimum']
    fig, ax = plt.subplots(figsize=(8.2, 5.4), constrained_layout=True)
    x = np.arange(3)
    ax.errorbar(x, model.D, yerr=model.sigma, fmt='ko', capsize=5, label='Experimental fitted signal, stated 1 sigma')
    ax.plot(x-.055, model.signals(0., 0.), 's', color='#235f9b', label='Computed SM (unshifted)')
    ax.plot(x+.055, best['signal_events'], '^', color='#258346', label='Global NSI minimum (unshifted)')
    ax.plot(x, (1+np.array(best['alpha']))*np.array(best['signal_events']), 'x', color='#c37821', ms=8, label='NSI minimum after independent pulls')
    ax.set(xticks=x, xticklabels=['PandaX paired', 'PandaX US2', 'XENONnT'], ylabel='Signal events', ylim=(0., 112.),
           title='Three single-bin samples; fitted signal is not raw event count')
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(axis='y', alpha=.2)
    fig.savefig(out / 'solar_snudd_signal_comparison.png', dpi=190)
    plt.close(fig)


if __name__ == '__main__':
    main()
