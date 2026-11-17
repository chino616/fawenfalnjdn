"""Run actual Xe nuclear-table SM and an isotope/mass-matched KN comparison.

No original input or historical result is overwritten. Use a new --output for
each execution. The report generator consumes these actual Runtime records.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.contracts import LiveTimeExposure
from cevns_pyeft.contracts.prediction import RecoilYield
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.experiments.package_loader import load_experiment_package, read_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_mean_map import with_pandax_mean_map
from cevns_pyeft.experiments.solar_nuclear import with_solar_nuclear_response, XE_KEYS, CHANNELS
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.folding import probability_fold, trapezoid_weights

FAMILIES = [('PandaX4T', 'PandaX4T_2024_US2'), ('XENONnT', 'XENONnT_2024_SolarB8')]
TABLE = ROOT/'data/responses/responses_all.json'
DEFAULT = ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(plain(obj), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def nuclear_audit():
    db = ResponseDB(TABLE)
    return {'file': TABLE.relative_to(ROOT).as_posix(), 'sha256': sha(TABLE),
        'direct_source': 'existing local project nuclear table and ResponseDB/Li2026 reader convention',
        'external_authorship_and_conversion': 'UNRESOLVED; not certified as a particular author release',
        'basis': 'np; p,n row/column order', 'q_unit': 'GeV', 'b_unit': 'GeV^-1',
        'y': '(q*b/2)^2', 'W': 'exp(-2*y) sum_k a[k]*y^k; dimensionless',
        'normalization': 'as existing shared amplitude; no extra spin factor or KN/Helm',
        'missing_isotopes': ['Xe124', 'Xe126'], 'covered_number_fraction': .998158,
        'isotopes': {key: {'basic': db.get(key).basic, 'exp_factor': db.get(key).exp_factor,
            'channels': {ch: {'shape': list(np.asarray(db.get(key).responses[ch]).shape),
                'coefficients': db.get(key).responses[ch], 'W_at_y0': db.get(key).W_np(ch, 0.)}
                for ch in CHANNELS}} for key in XE_KEYS}}


def converge(exp):
    rows, predictions = [], []
    for label, nr, ne in [('base', 201, 120), ('recoil', 401, 120), ('energy', 401, 480)]:
        start = time.perf_counter()
        p = predict_experiment(exp, backend='slow', numerics={'n_er': nr, 'n_enu': ne})
        rows.append({'label': label, 'n_er': nr, 'n_enu': ne, 'counts': p.counts.tolist(),
                     'seconds': time.perf_counter()-start})
        predictions.append(p)
        print(exp.dataset_id, exp.definition.physical.nuclear_model, label,
              'events', float(p.counts.sum()), flush=True)
    checks = []
    for axis, a, b in [('recoil', 0, 1), ('neutrino_energy', 1, 2)]:
        delta = abs(predictions[a].counts-predictions[b].counts)
        tolerance = np.maximum(2e-4, .002*abs(predictions[b].counts))
        checks.append({'axis': axis, 'delta_events': delta.tolist(), 'tolerance_events': tolerance.tolist(),
                       'passed': bool(np.all(delta <= tolerance))})
    if not all(c['passed'] for c in checks):
        raise RuntimeError('Independent numerical convergence failed; inspect saved grid log')
    return predictions[-1], {'runs': rows, 'checks': checks, 'passed': True}


def channel_counts(exp, prediction, n_enu):
    """Independent channel folding using the very same T/E nodes and weights.

    This also checks that the channel decomposition reproduces the primary
    standard-Runtime prediction. No channel fractions are guessed or fitted.
    """
    model = exp.model
    fluence = model.source.for_run(LiveTimeExposure(model.seconds_per_year, 'reference_year'))
    parts = {}
    grids = prediction.combined_prediction.diagnostics['recoil_grids_keV']
    for target in model.targets.isotopes:
        t = np.asarray(grids[target.isotope_id])
        for component in fluence.components:
            lo, hi = component.support.integration_domain_MeV
            nodes = np.unique(np.r_[np.linspace(lo, hi, n_enu), component.support.breakpoints_MeV])
            rates = np.zeros((len(t), len(CHANNELS)))
            for j, recoil in enumerate(t):
                emin = model.interaction.kinematics.minimum_energy_MeV(target, recoil)
                e = nodes[(nodes >= emin) & (nodes > 0)]
                if not e.size:
                    continue
                ds = model.interaction.channel_dsigma(target=target, energy_MeV=e, recoil_keV=recoil,
                    incident_state=component.state_at(e, parameters=exp.executor.default_point().state),
                    parameters=exp.executor.default_point())
                rates[j] = np.trapezoid(np.array([ds[ch] for ch in CHANNELS]).T*
                                       component.continuum(e)[:, None], e, axis=0)
            for run_i, (run, observation) in enumerate(zip(model.run_ids, model.observation)):
                scale = target.number_of_nuclei*model.exposures_tyr[run_i]/(model.anchor_mass_kg/1000)
                for ch_i, ch in enumerate(CHANNELS):
                    if model.mode == 'pandax_mean_map':
                        weights = np.zeros((len(t), len(observation.recoil_edges)-1))
                        for b, (a, z) in enumerate(zip(observation.recoil_edges[:-1], observation.recoil_edges[1:])):
                            mask = (t >= a) & (t <= z)
                            weights[mask, b] = trapezoid_weights(t[mask])
                        counts = (rates[:, ch_i]*observation.acceptance(t))@weights*scale
                    else:
                        rate = RecoilYield(component.component_id, target.isotope_id, t, rates[:, ch_i])
                        counts = probability_fold(rate, target, observation, model.binning)*scale
                    parts[ch+'/'+run+'/'+target.isotope_id] = counts
    totals = {ch: sum((v for key, v in parts.items() if key.startswith(ch+'/')),
                     np.zeros_like(prediction.counts)) for ch in CHANNELS}
    np.testing.assert_allclose(sum(totals.values()), prediction.counts, rtol=2e-12, atol=2e-12)
    return {'counts_by_channel': totals, 'counts_by_channel_run_isotope': parts,
            'sum_matches_primary_runtime': True}


def references(family, data, exp):
    if family == 'PandaX4T':
        a = np.loadtxt(data/'statistics/pandax_benchmark_fig1.txt')
        blue = json.loads((ROOT/'outputs/solar_b8_sm/20261109_fig1_comparison/COMPARISON.json').read_text(encoding='utf8'))
        return {'observed': a[:, 3].astype(int), 'background': a[:, 4]+a[:, 5],
            'paper_total': blue['regions']['PandaX']['blue_total_signal_plus_background_events_per_bin'],
            'role': 'digitized Fig.1 postfit background and author total; descriptive reference only'}
    d = np.loadtxt(data/'statistics/xenonnt_official_observed_bins.txt')[:, 4].reshape(2, 3)
    b = []
    for i in (0, 1):
        with np.load(data/f'statistics/xenonnt_sr{i}_background_and_b8_early_release.npz', allow_pickle=False) as a:
            counts = np.zeros(3)
            for ch in ('ac', 'er', 'rg'):
                value = a[ch+'_rate_per_tyr_bin']
                value = value[3, 3] if value.ndim == 6 else value
                counts += value.sum(axis=(1, 2, 3))*exp.model.exposures_tyr[i]
            b.append(counts)
    return {'observed': d.sum(axis=0), 'background': np.array(b).sum(axis=0),
            'per_run_observed': d, 'per_run_background': b,
            'role': 'official early-release D and nominal background; ordinal sum of distinct per-run PE bins'}


def plot(exp, nuclear, control, refs, channels, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from tools.run_solar_b8_sm_benchmark import errors
    x = np.arange(len(nuclear.counts))
    width = np.diff(exp.definition.observation.edges)
    pandax = exp.model.mode == 'pandax_mean_map'
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for i, ax in enumerate(axes):
        b = np.asarray(refs['background']) if i else np.zeros_like(x)
        ax.stairs(nuclear.counts+b, np.arange(len(x)+1)-.5, color='#008877', lw=2,
                  label='Calculated SM: nuclear table')
        ax.stairs(control.counts+b, np.arange(len(x)+1)-.5, color='#b45500', ls='--', lw=1.8,
                  label='Calculated KN control (same isotopes)')
        if i:
            d = np.asarray(refs['observed'])
            ax.stairs(b, np.arange(len(x)+1)-.5, color='gray', lw=1.3, label='Background reference')
            ax.errorbar(x, d, yerr=errors(d), fmt='ko', ms=4, capsize=3, label='Observed (68.27% Poisson)')
            if 'paper_total' in refs:
                ax.stairs(refs['paper_total'], np.arange(len(x)+1)-.5, color='#2165bd', ls=':',
                          lw=1.6, label='Paper Fig.1 S+B (digitized reference)')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{a:g}-{z:g}' for a, z in zip(exp.definition.observation.edges[:-1],
                           exp.definition.observation.edges[1:])] if pandax else ['1', '2', '3'], fontsize=8)
        ax.set_xlabel('Mean-mapped electron bin' if pandax else 'cS2 bin ordinal (SR0 + SR1)')
        ax.set_ylabel('Events / bin')
        ax.set_title('Signal' if i == 0 else 'Signal + reference background')
        ax.set_ylim(bottom=0)
        ax.legend(fontsize=7.4)
    fig.suptitle(exp.dataset_id+' | fixed SSM | 7 Xe isotopes, no renormalization', fontsize=10)
    fig.tight_layout()
    fig.savefig(out/'events.png', dpi=180)
    fig.savefig(out/'events.pdf')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=DEFAULT)
    ap.add_argument('--dataset', choices=['all','PandaX4T','XENONnT'], default='all')
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save(out/'NUCLEAR_INPUT_AUDIT.json', nuclear_audit())
    results = {}
    for family, dataset in FAMILIES:
        if args.dataset not in ('all', family):
            continue
        dest = out/dataset
        dest.mkdir()
        data = ROOT/'data/experiments'/family/dataset
        base = load_experiment_package(data)
        if family == 'PandaX4T':
            base = with_pandax_mean_map(base, qy_file=data/'detector/pandax_qy_nominal.txt')
        exp = with_solar_nuclear_response(base, response_file=TABLE)
        kn = with_solar_nuclear_response(base, response_file=TABLE, nuclear_model='kn_control')
        nuclear, convergence = converge(exp)
        control, kn_convergence = converge(kn)
        channels = channel_counts(exp, nuclear, 480)
        refs = references(family, data, exp)
        pkg, arrays = read_package(data)
        for name, prepared in [('nuclear', exp), ('kn_control', kn)]:
            save(dest/f'PREPARED_MODEL.{name}.json', prepared.describe())
        result = {'date': '2026-11-10', 'dataset_id': dataset, 'calculation': 'actual nuclear-table SM, shared amplitude and standard Slow Runtime',
            'status': 'CALCULATED_LOCAL_TABLE_CONVENTION; EXTERNAL_SOURCE_AND_PAPER_EQUIVALENCE_UNCERTIFIED',
            'counts': nuclear.counts, 'total_events': float(nuclear.counts.sum()),
            'per_run': {run:p.counts for run,p in nuclear.detector_predictions.items()},
            'components': {'/'.join(k): v for k,v in nuclear.combined_prediction.components.items()},
            'unit': 'events/bin', 'observable_edges': exp.definition.observation.edges,
            'kn_control_counts': control.counts, 'kn_control_total': float(control.counts.sum()),
            'relative_difference_to_matched_KN': nuclear.counts/control.counts-1,
            'channel_decomposition': channels, 'references': refs,
            'fixed_parameters': {key: v for key, v in pkg['parameters'].items()
                if v['role'] not in ('unused_snapshot', 'reference_only')},
            'nuclear_overrides': {'resource': 'NUCLEAR_INPUT_AUDIT.json', 'mass': 'A*amu',
                'coverage_number_fraction': .998158, 'c_i': 'not applied', 'flux_adjustment': 'none',
                'KN_parameters': 'inactive in primary nuclear route; used only for control'},
            'diagnostics': plain(nuclear.combined_prediction.diagnostics),
            'convergence': convergence, 'kn_convergence': kn_convergence,
            'physics_fingerprint': exp.physics_fingerprint, 'analysis_fingerprint': exp.analysis_fingerprint,
            'normalization_record': plain(nuclear.combined_prediction.normalization_record),
            'human_result_acceptance': 'NOT_REVIEWED', 'runner_sha256': sha(Path(__file__))}
        save(dest/'RESULT.json', result)
        values = {'counts': nuclear.counts, 'kn_control_counts': control.counts,
            **{'channel_'+ch: v for ch,v in channels['counts_by_channel'].items()},
            **{'component_'+k.replace('/', '_'):v for k,v in result['components'].items()}}
        np.savez_compressed(dest/'prediction.npz', **values)
        np.savetxt(dest/'events_by_bin.tsv', np.column_stack([np.arange(1,len(nuclear.counts)+1),
            nuclear.counts, control.counts, refs['observed'], refs['background']]), delimiter='\t',
            header='bin nuclear_SM_events matched_KN_events observed_events reference_background_events')
        plot(exp, nuclear, control, refs, channels, dest)
        results[dataset] = {'total_events': result['total_events'], 'counts': result['counts'],
            'kn_control_total': result['kn_control_total'], 'channels': channels['counts_by_channel']}
        save(out/'RUN_SUMMARY.json', results)
    print('Completed', out, flush=True)


if __name__ == '__main__':
    main()
