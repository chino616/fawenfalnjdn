"""Actual optional mainline benchmark: file-based SNuDD -> standard Runtime.

No physical calibration. Rebuild separate kernels, compare identical nuclear
fold values, check actual Slow/Fast and retain conditional X-tail uncertainties.
"""
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np
from cevns_pyeft.experiments.definition import plain
from cevns_pyeft.experiments.runtime import compile_experiment, predict_experiment, evaluate_experiment
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from .experiment import load_snudd
from .protocol import ROOT, CARD, read, save, sha

SAMPLES = ('PandaX_paired', 'PandaX_US2', 'XENONnT')
POINTS = [(0., 0.), (.3, -.1), (-.4, .6), (0., .178), (-17.263001514819095, 15.676753288438908)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/external/solar_rho_snudd/20261112_run1')
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'outputs/external/solar_rho_snudd'):
        raise ValueError('use independent external output root')
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'RESULTS.json').exists():
        raise FileExistsError('choose a new output directory; finalized results are immutable')
    start = time.perf_counter()
    oldout = ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run2'
    source = np.loadtxt(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt')
    # Slow uses its linspace + original source breakpoints, threshold subsets.
    # Fast has separate Gauss nodes. Export their union, then exact subset lookup.
    slow_energy = np.unique(np.r_[np.linspace(0., 16.56, 480), source[1:-1, 0]])
    gx, _ = np.polynomial.legendre.leggauss(144)
    fast_energy = 16.56/2 + 16.56/2*gx
    union = np.unique(np.r_[slow_energy[slow_energy > 0], fast_energy, [2., 5., 10., 15.]])
    save(out / 'ENERGY_CONTRACT.json', {'E_MeV': union.tolist(), 'union_nodes': len(union), 'slow_positive_nodes': int(sum(slow_energy > 0)),
        'fast_nodes': 144, 'interpolation': 'NONE; exact coordinate subset lookup; unsupported grids export a separate packet',
        'slow_rule': '480 linspace plus original827 source interior nodes, then recoil-threshold subset', 'fast_rule': '144 Gauss-Legendre nodes'})
    experiments, kernels, oldexperiments, oldkernels, checks = [], [], [], [], []
    shared = None
    for sample in SAMPLES:
        print('Preparing', sample, flush=True)
        e = load_snudd(sample, cache_root=out / 'rho_cache', interaction=shared)
        shared = e.model.interaction
        e.model.state_model.prefetch(union, POINTS)
        k = compile_experiment(e, numerics={'n_er': 801, 'n_enu': 144})
        (out / 'kernels').mkdir(exist_ok=True)
        k.save(out / 'kernels' / (sample+'.npz'))
        save(out / sample / 'PREPARED_MODEL.json', e.describe())
        old = load_solar_nsi(sample, root=ROOT, interaction=shared)
        oldk = SolarNSIKernel.load(oldout / 'kernels' / (sample+'.npz'))
        # These arrays must be identical: only propagation is replaced.
        same = np.array_equal(k.values, oldk.values) and np.array_equal(k.energy, oldk.energy)
        if not same:
            raise ValueError('source magnitude/target/nuclear/detector fold changed unexpectedly')
        validation = {'sample': sample, 'new_kernel_sha256': sha(out / 'kernels' / (sample+'.npz')),
                      'old_and_new_fold_arrays_bitwise_identical': same, 'direct_slow_checks': []}
        for u, d in POINTS[:3]:
            point = nsi_point(u, d)
            fast = predict_experiment(e, parameters=point, backend='fast', kernel=k, numerics=k.record['numerics'])
            slow = predict_experiment(e, parameters=point, numerics={'n_er': 801, 'n_enu': 480})
            diff = abs(fast.counts-slow.counts)
            tolerance = np.maximum(3e-4, .002*abs(slow.counts))
            if not np.all(diff <= tolerance):
                raise ValueError('actual external-state Slow/Fast mismatch')
            validation['direct_slow_checks'].append({'point': [u, d], 'fast': fast.counts.tolist(), 'slow': slow.counts.tolist(),
                'difference': diff.tolist(), 'tolerance': tolerance.tolist(), 'runtime_chi2': evaluate_experiment(e, fast).chi2})
            print(sample, 'Slow/Fast', u, d, fast.counts.tolist(), slow.counts.tolist(), flush=True)
        # Independent quadrature refinement for the new probability weighting.
        if sample == 'PandaX_US2':
            fine = compile_experiment(e, numerics={'n_er': 1201, 'n_enu': 216})
            extra = []
            for u, d in [POINTS[1], POINTS[-1]]:
                p = nsi_point(u, d)
                a = predict_experiment(e, parameters=p, backend='fast', kernel=k, numerics=k.record['numerics']).counts
                b = predict_experiment(e, parameters=p, backend='fast', kernel=fine, numerics=fine.record['numerics']).counts
                if not np.all(abs(a-b) <= np.maximum(3e-4, .002*abs(b))):
                    raise ValueError('external source quadrature refinement failed')
                extra.append({'point': [u, d], 'base': a.tolist(), 'refined': b.tolist(), 'absolute_difference': abs(a-b).tolist()})
            validation['independent_1201x216_refinement'] = extra
        checks.append(validation)
        experiments.append(e)
        kernels.append(k)
        oldexperiments.append(old)
        oldkernels.append(oldk)
    external = SolarNSIJoint(tuple(experiments), tuple(kernels))
    previous = SolarNSIJoint(tuple(oldexperiments), tuple(oldkernels))
    results = []
    for u, d in POINTS:
        results.append({'point': [u, d], 'snudd': external.detail(u, d), 'local_B16_MSW': previous.detail(u, d),
            'snudd_zero_tail': external.detail(u, d, 'zero'), 'snudd_unit_tail': external.detail(u, d, 'unit')})
    if not np.array_equal(external.signals(0, 0), previous.signals(0, 0)):
        raise ValueError('SM flavor universality must preserve the identical folded prediction')
    packets = [read(p) for p in (out / 'rho_cache').glob('*/manifest.json')]
    save(out / 'FORWARD_VALIDATION.json', checks)
    save(out / 'RESULTS.json', {'date': '2026-11-12', 'status': 'INSTALLED_EXTERNAL_SOURCE_BOUND_TO_MAINLINE_RUNTIME; POINT_BENCHMARK_VERIFIED',
        'scientific_acceptance': 'NOT_REVIEWED', 'points': results, 'sample_order': list(SAMPLES),
        'source_card': str(CARD.relative_to(ROOT)).replace('\\', '/'), 'source_card_sha256': sha(CARD),
        'SM_counts_bitwise_unchanged': True, 'SM_chi2': float(external.chi2(0, 0)),
        'host_imported_snudd': any(k == 'snudd' or k.startswith('snudd.') for k in sys.modules),
        'forward_validation': 'FORWARD_VALIDATION.json', 'full_rho_packets': len(packets),
        'packet_adiabatic_diagnostics': [{'input': p['input_identity'], 'diagnostic': p['adiabatic_diagnostic']} for p in packets],
        'new_full_Fig4_region': 'NOT_COMPUTED_BY_THIS_INTEGRATION; this deliverable is an installed source adapter and validated forward/statistical points',
        'limitations': ['effective two-flavor adiabatic SNuDD solar model; not full3-flavor numerical evolution',
            'SNuDD own fitted profiles/production differ fromB16; matched theta12/13/dm21 only',
            'X2.77-3keV tail still unknown; flat assumption and zero/unit bounds explicit',
            'seven local nuclear tables, no124/126 renormalization; external author table certification unresolved'],
        'wall_seconds': time.perf_counter()-start, 'runner_sha256': sha(Path(__file__))})
    plot(out, external, previous, union)
    print('Completed actual external propagation / Runtime benchmark:', out, flush=True)


def plot(out, external, previous, energy):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    e = energy[(energy >= .5) & (energy <= 16.56)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for point, color in zip(POINTS[:3], ['#235e9a', '#cf7621', '#22835c']):
        axes[0].plot(e, external.state.pee(e, *point), color=color, label='SNuDD '+str(point))
        axes[0].plot(e, previous.state.pee(e, *point), color=color, ls='--', alpha=.7)
    axes[0].set(xlabel=r'$E_\nu$ [MeV]', ylabel=r'$P_{ee}$', title='Matched oscillation inputs; different solar profiles')
    axes[0].legend(fontsize=8)
    results = read(out / 'RESULTS.json')['points']
    x = np.arange(3)
    for row, color in zip(results[:3], ['#235e9a', '#cf7621', '#22835c']):
        axes[1].plot(x, row['snudd']['signal_events'], 'o-', color=color, label='SNuDD '+str(row['point']))
        axes[1].plot(x, row['local_B16_MSW']['signal_events'], 'x--', color=color)
    axes[1].set(xticks=x, xticklabels=['PandaX paired', 'PandaX US2', 'XENONnT'], ylabel='Signal events', title='Solid: external; dashed: local B16 MSW')
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / 'snudd_vs_local.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
