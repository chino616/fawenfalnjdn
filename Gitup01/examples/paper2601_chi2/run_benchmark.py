"""2601.19883v2 chi-square benchmark with explicit local method variants.

No production inputs, runtime semantics, registry or scientific gates are changed.
Output directory must contain only PLAN_AND_BASELINE.json and/or paper_reference.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict, dataclass, replace
import argparse
import ast
import csv
import hashlib
import importlib.util
import json
import platform
import shutil
import sys
import time
import numpy as np
from scipy.optimize import brentq, differential_evolution, minimize, minimize_scalar

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.experiments.definition import plain
from cevns_pyeft.experiments.package_profiles import compile_profile, predict_profile_kernel
from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.kernels.compiler import compile_fast, reconstruct_channels
from cevns_pyeft.statistics.datasets import load_dataset
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.profiling import (profile_gaussian_one_pull, profile_gaussian_two_pull,
                                             profile_ar2020_irls, profile_ar2020_bounded)
from cevns_pyeft.statistics.solar_singlebin import profile as solar_profile

BASIS = ((6, 1, 'u'), (6, 1, 'd'), (6, 2, 'u'), (6, 2, 'd'))
PAPER = 'docs/references/General_CEvNS/2601.19883v2.pdf'
CONUS = 'outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106'
SOLAR = 'outputs/solar_b8_singlebin/20261111_response_run2'
TRACKED = set()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    path = ROOT / path
    TRACKED.add(path)
    return json.loads(path.read_text(encoding='utf8'))


def load_npz(path):
    path = ROOT / path
    TRACKED.add(path)
    with np.load(path, allow_pickle=False) as data:
        return {k: data[k] for k in data.files}


def write_json(path, value):
    path.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')


def write_csv(path, rows):
    with path.open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def import_file(name, path):
    path = ROOT / path
    TRACKED.add(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def point(x=0., y=0., weak_angle=.2387):
    # Paper p22 Eq95; existing project mapping, no weak-charge rescaling.
    wc = vector_nsi_to_np_wilson(VectorNSIParameters(epsilon_ee_uV=x, epsilon_ee_dV=y))
    return TheoryPoint(wc, include_sm=True, sin2thetaW=weak_angle)


def polynomial(coefficients, x, y):
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    return np.stack([np.ones_like(x), x, y, x*x, x*y, y*y], axis=-1) @ coefficients


def templates(predict):
    c, px, mx, py, my, xy = [predict(x, y) for x, y in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1)]]
    lx, ly = (px-mx)/2, (py-my)/2
    qx, qy = (px+mx)/2-c, (py+my)/2-c
    out = np.array([c, lx, ly, qx, xy-c-lx-ly-qx-qy, qy])
    errors = []
    for x, y in [(.031, -.017), (-.31, .28), (.71, -.62), (.23, .37)]:
        error = float(np.max(abs(polynomial(out, x, y)-predict(x, y))))
        if error > 1e-8:
            raise ValueError('Quadratic template holdout failed')
        errors.append({'x': x, 'y': y, 'max_abs_events': error})
    return out, errors


@dataclass
class Channel:
    name: str
    coefficients: np.ndarray
    observed: np.ndarray
    sigma: np.ndarray
    sigma_alpha: float
    background: np.ndarray | None = None
    sigma_beta: float | None = None

    def __post_init__(self):
        if self.coefficients.shape != (6, self.observed.size) or self.sigma.shape != self.observed.shape:
            raise ValueError('Channel axes differ')
        if np.any(self.sigma <= 0) or not np.all(np.isfinite(self.sigma)):
            raise ValueError('Positive finite uncertainty required; no silent floor')

    def profile_signals(self, signals):
        # Batched normal equations for paper Eqs86/90; checked independently below.
        s = np.asarray(signals)
        w = 1/self.sigma**2
        a11 = np.sum(s*s*w, axis=-1) + 1/self.sigma_alpha**2
        b = 0. if self.background is None else self.background
        residual = self.observed-s-b
        r1 = np.sum(s*residual*w, axis=-1)
        if self.background is None:
            alpha, beta = r1/a11, np.zeros_like(r1)
        else:
            a12 = np.sum(s*b*w, axis=-1)
            a22 = np.sum(b*b*w) + 1/self.sigma_beta**2
            r2 = np.sum(b*residual*w, axis=-1)
            det = a11*a22-a12*a12
            alpha, beta = (r1*a22-r2*a12)/det, (r2*a11-r1*a12)/det
        residual = self.observed-(1+alpha[..., None])*s
        if self.background is not None:
            residual = residual-(1+beta[..., None])*b
        data = np.sum(residual**2*w, axis=-1)
        penalty = (alpha/self.sigma_alpha)**2
        if self.background is not None:
            penalty = penalty+(beta/self.sigma_beta)**2
        return data+penalty, alpha, beta, data, penalty

    def chi2(self, x, y):
        return self.profile_signals(polynomial(self.coefficients, x, y))[0]

    def detail(self, x=0., y=0.):
        s = polynomial(self.coefficients, x, y)
        chi, a, b, data, pen = self.profile_signals(s)
        return {'chi2': float(chi), 'alpha': float(a), 'beta': float(b),
                'chi2_data': float(data), 'chi2_pull': float(pen),
                'predicted_signal_events': float(s.sum()), 'bins': s.size,
                'signal': s.tolist(), 'observed': self.observed.tolist(),
                'sigma': self.sigma.tolist(), 'background': None if self.background is None else self.background.tolist(),
                'sigma_alpha': self.sigma_alpha, 'sigma_beta': self.sigma_beta}


def check_profile(channel):
    checks = []
    for x, y in [(0, 0), (.03, -.01), (.35, 0), (-.25, .4)]:
        s = polynomial(channel.coefficients, x, y)
        actual = channel.profile_signals(s)
        if channel.background is None:
            stock = profile_gaussian_one_pull(s, channel.observed, channel.sigma, sigma_alpha=channel.sigma_alpha)
        else:
            stock = profile_gaussian_two_pull(s, channel.observed, channel.background, channel.sigma,
                        sigma_alpha=channel.sigma_alpha, sigma_beta=channel.sigma_beta)
        def obj(pulls):
            r = channel.observed-(1+pulls[0])*s
            out = (pulls[0]/channel.sigma_alpha)**2
            if channel.background is not None:
                r = r-(1+pulls[1])*channel.background
                out += (pulls[1]/channel.sigma_beta)**2
            return float(np.sum((r/channel.sigma)**2)+out)
        size = 1 if channel.background is None else 2
        opt = minimize(obj, np.full(size, .04), method='BFGS', options={'gtol': 1e-8})
        # A nonnegative scalar covariance identity is independent of the normal solve.
        columns = [channel.sigma_alpha*s]
        baseline = s.copy()
        if channel.background is not None:
            columns.append(channel.sigma_beta*channel.background)
            baseline += channel.background
        matrix = np.stack(columns, axis=-1)
        covariance = np.diag(channel.sigma**2)+matrix@matrix.T
        residual = channel.observed-baseline
        cov_chi = float(residual@np.linalg.solve(covariance, residual))
        diff = max(abs(float(actual[0])-stock.chi2), abs(float(actual[0])-opt.fun), abs(float(actual[0])-cov_chi))
        if diff > 1e-7:
            raise ValueError('Analytic/numerical/covariance profile comparison failed')
        checks.append({'coordinates': [x, y], 'analytic': float(actual[0]), 'stock_runtime': stock.chi2,
                       'numeric': opt.fun, 'covariance_identity': cov_chi, 'max_abs_difference': diff,
                       'optimizer_message': str(opt.message)})
    return checks


def build_forwards(output):
    helper = import_file('_paper2601_csi_nsi', 'examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py')
    summary = {}
    channels = {}
    # Each axis is refined independently before the final joint grid.
    grids = {'CsI2021': [dict(n_er=64, n_enu=240, n_pe_bin=32, pe_step=.5),
                         dict(n_er=128, n_enu=240, n_pe_bin=32, pe_step=.5),
                         dict(n_er=128, n_enu=960, n_pe_bin=32, pe_step=.5),
                         dict(n_er=128, n_enu=960, n_pe_bin=64, pe_step=.25),
                         dict(n_er=256, n_enu=960, n_pe_bin=64, pe_step=.25),
                         dict(n_er=256, n_enu=960, n_pe_bin=128, pe_step=.125),
                         dict(n_er=256, n_enu=960, n_pe_bin=256, pe_step=.0625),
                         dict(n_er=512, n_enu=960, n_pe_bin=256, pe_step=.0625),
                         dict(n_er=512, n_enu=1920, n_pe_bin=256, pe_step=.0625)],
             'Ar2020': [dict(n_er=21, n_enu=120, n_pe_bin=8),
                        dict(n_er=41, n_enu=120, n_pe_bin=8),
                        dict(n_er=41, n_enu=480, n_pe_bin=8),
                        dict(n_er=41, n_enu=480, n_pe_bin=32),
                        dict(n_er=81, n_enu=960, n_pe_bin=32),
                        dict(n_er=161, n_enu=960, n_pe_bin=32),
                        dict(n_er=161, n_enu=1920, n_pe_bin=32),
                        dict(n_er=161, n_enu=1920, n_pe_bin=64),
                        dict(n_er=321, n_enu=1920, n_pe_bin=64)]}
    for name, sequence in grids.items():
        exp = load_experiment(name, resources=ResourceCatalog(ROOT))
        dataset = load_dataset(name)
        weak = exp.definition.reproduction_sin2thetaW
        raw_model = exp.model
        wrapped = helper.CheckedCoefficientEnergy(raw_model.interaction)
        model = replace(raw_model, interaction=wrapped)
        runs, all_coefficients = [], []
        for index, ns in enumerate(sequence):
            started = time.perf_counter()
            if name == 'CsI2021':
                settings = IntegrationSettings.legacy_csi2021_v1(**ns)
                kernel = compile_fast(model, numerics=settings, basis_keys=BASIS)
                predict = lambda x, y: kernel.predict(parameters=point(x, y, weak)).counts
            else:
                settings = exp.executor._settings(ns)
                kernel = compile_profile(model, settings, exp.executor.profile, basis_keys=BASIS)
                predict = lambda x, y: predict_profile_kernel(kernel, model, point(x, y, weak), settings, exp.executor.profile).counts
            coeff, holdouts = templates(predict)
            all_coefficients.append(coeff)
            # Use counts/bin throughout. Density inputs and errors converted together.
            widths = dataset.observable.bin_widths
            if name == 'CsI2021':
                ch = Channel(name, coeff, dataset.observed*widths, dataset.uncertainty*widths,
                             .125, dataset.background*widths, .35)
            else:
                ch = Channel(name, coeff, dataset.observed, (dataset.upper-dataset.lower)/2,
                             .12, dataset.background, .146)
            runs.append({'grid': ns, 'sm': ch.detail(), 'template_holdouts': holdouts,
                         'seconds': time.perf_counter()-started})
            print(name, 'grid', ns, 'events', coeff[0].sum(), 'chi2', runs[-1]['sm']['chi2'], flush=True)
            np.savez_compressed(output/f'{name}_templates_grid{index}.npz', coefficients=coeff)
            if index == len(sequence)-1:
                full = kernel.full_kernel if name == 'CsI2021' else kernel['full_kernel']
                np.savez_compressed(output/f'{name}_kernel.npz', full_kernel=full)
                write_json(output/f'{name}_kernel_record.json', kernel.record if name == 'CsI2021' else kernel['metadata'])
                channels[name] = ch
        convergence = []
        # Recoil comparison uses the last two joint grids; other axes isolate base-grid changes.
        pairs = [(0, 1, 'recoil_early'), (1, 2, 'neutrino_energy_early'), (2, 3, 'observed_response_early')]
        pairs += ([(5, 6, 'observed_response_final'), (6, 7, 'recoil_final'), (7, 8, 'neutrino_energy_final')]
                  if name == 'CsI2021' else
                  [(5, 6, 'neutrino_energy_final'), (6, 7, 'observed_response_final'), (7, 8, 'recoil_final')])
        for a, b, axis in pairs:
            ca, cb = all_coefficients[a][0], all_coefficients[b][0]
            delta = abs(ca-cb)
            chis = abs(runs[a]['sm']['chi2']-runs[b]['sm']['chi2'])
            convergence.append({'axis': axis, 'grid_indices': [a, b], 'max_abs_events': float(delta.max()),
                                'abs_chi2_change': chis,
                                'used_for_final_convergence': axis.endswith('_final'),
                                'passes_declared_SM_tolerance': bool(np.all(delta <= np.maximum(.005, .005*abs(cb))) and chis < .02)})
        # Native direct Slow at a nonzero point, with identical low grid, checks full folding.
        ns = sequence[0]
        native = predict_experiment(exp, parameters=point(.031, -.017, weak), numerics=ns)
        diff = float(np.max(abs(native.counts-polynomial(all_coefficients[0], .031, -.017))))
        if diff > 1e-8:
            raise ValueError(name+' coefficient kernel differs from native Slow')
        record = {'dataset': name, 'physical_fingerprint': exp.physics_fingerprint,
                  'analysis_fingerprint': exp.analysis_fingerprint, 'weak_angle': weak,
                  'model': plain(raw_model.describe()), 'runs': runs, 'convergence': convergence,
                  'checked_coefficient_energy': wrapped.statistics,
                  'native_nonzero_Slow_holdout': {'coordinates': [.031, -.017], 'grid': ns,
                                                'max_abs_events': diff},
                  'statistic': '2601 Eq86, unbounded analytic Gaussian pulls; Ar sigma=(upper-lower)/2 is an explicit local sensitivity choice',
                  'claim': 'local_approximate_paper_form_not_author_reproduction'}
        summary[name] = record
        write_json(output/f'{name}_FORWARD.json', record)
        # Track exact active package and statistical provenance, not presumed external files.
        family = 'COHERENT_CsI' if name == 'CsI2021' else 'COHERENT_Ar'
        for rel in ('experiment.input.yaml', 'experiment.resources.npz', 'statistics/provenance.yaml'):
            TRACKED.add(ROOT/f'data/experiments/{family}/{name}/{rel}')
    return channels, summary


def solar_results():
    data = read_json('data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json')['samples']
    fractions = {'PandaX_paired': .371, 'PandaX_US2': .373, 'XENONnT': .369}
    result = {'source': '2601.19883v2 p20 Eq88', 'joint_chi2': None,
              'reason': 'XENONnT acceptance 2.77-3 keVnr missing; bounded primary, explicit flat-tail sensitivity only',
              'variants': {}}
    for variant in ('paper_percentages', 'current_rounded_sigmas'):
        rows = {}
        joint_min, joint_max, joint_flat = 0., 0., 0.
        for name, dat in data.items():
            sm = read_json(f'{SOLAR}/{name}/SM_RESULT.json')
            sigma = fractions[name]*dat['D'] if variant == 'paper_percentages' else dat['sigma_stat']
            lo, hi = sm['full_interval_events']
            profile = lambda value: plain(asdict(solar_profile(value, dat['D'], sigma, .12)))
            lower = profile(np.clip(dat['D'], lo, hi))['chi2']
            upper = max(profile(lo)['chi2'], profile(hi)['chi2'])
            flat = sm['flat_tail_sensitivity']['events'] if name == 'XENONnT' else sm['counts'][0]
            rows[name] = {'observed_fitted_signal': dat['D'], 'sigma_stat': sigma,
                          'sigma_alpha': .12, 'signal_interval': [lo, hi],
                          'complete': sm['complete_prediction'],
                          'SM_profile': profile(lo) if sm['complete_prediction'] else None,
                          'tail_only_chi2_bounds': [lower, upper],
                          'flat_tail_sensitivity': {'events': flat, 'profile': profile(flat)}}
            joint_min += lower
            joint_max += upper
            joint_flat += profile(flat)['chi2']
        result['variants'][variant] = {'samples': rows, 'joint_chi2_bounds_tail_only': [joint_min, joint_max],
                                      'joint_chi2_flat_tail_sensitivity': joint_flat}
    return result


def conus_channel():
    raw = load_npz(f'{CONUS}/nsi_quadratic_templates.npz')['diag_ud']
    source_file = ROOT/'examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py'
    TRACKED.add(source_file)
    syntax = ast.parse(source_file.read_text(encoding='utf8'))
    declaration = next(node for node in syntax.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'PLANE_SPECS' for target in node.targets))
    source_axes = ast.literal_eval(declaration.value)['diag_ud'][:2]
    if source_axes != ('epsilon_ee_dV', 'epsilon_ee_uV'):
        raise ValueError('Adopted CONUS template axis declaration changed; do not guess order')
    # The old 2501 plot uses x=d,y=u; 2601 Fig4 uses x=u,y=d.
    coeff = raw[[0, 2, 1, 5, 4, 3]]
    path = ROOT/'data/experiments/CONUS_Plus/conusplus_kkl_run1/statistics/conusplus_2501_17843v3_fig1_digitized.csv'
    TRACKED.add(path)
    data = np.genfromtxt(path, names=True, delimiter=',', encoding='utf8')
    channels = {mode: Channel('CONUS_plus_'+mode, coeff, data['excess'], sigma, .169) for mode, sigma in
                [('mean', (data['error_minus']+data['error_plus'])/2),
                 ('lower', data['error_minus']), ('upper', data['error_plus'])]}
    baseline = read_json(f'{CONUS}/summary.json')
    if abs(channels['mean'].detail()['chi2']-baseline['SM_chi2_profiled']) > 1e-10:
        raise ValueError('CONUS input/template regression differs')
    # Latest local rebuild was already checked byte-for-byte/Slow in previous task.
    local = load_npz('outputs/latest_layout_20261111/conus_nsi_local_report/nsi_quadratic_templates.npz')['diag_ud']
    if not np.allclose(raw, local, rtol=1e-12, atol=1e-10):
        raise ValueError('Current local CONUS templates differ from adopted latest calculation')
    axis_checks = []
    for axis, coordinate in enumerate(('epsilon_ee_uV', 'epsilon_ee_dV')):
        row = baseline['NSI_rows'][coordinate]
        for interval in row['intervals']['1sigma']:
            for value in interval:
                delta = float(channels['mean'].chi2(value if axis == 0 else 0., value if axis == 1 else 0.)-row['best_fit']['chi2'])
                if abs(delta-1.) > 1e-7:
                    raise ValueError('CONUS axis assignment failed independent saved 1sigma endpoint check')
                axis_checks.append({'coordinate': coordinate, 'epsilon': value, 'delta_chi2': delta})
    return channels, {'source_axes': source_axes, 'current_axes': ['epsilon_ee_uV', 'epsilon_ee_dV'],
                      'coefficient_row_permutation': [0, 2, 1, 5, 4, 3],
                      'saved_current_1sigma_endpoint_checks': axis_checks}


def reuse_forwards(output, source):
    """Reuse only verified unchanged forward calculations; rerun statistics/scans."""
    source = source.resolve()
    baseline = read_json(source/'PLAN_AND_BASELINE.json')
    validation = read_json(source/'VALIDATION.json')
    if not validation['forward_SM_convergence_all_declared_checks_pass']:
        raise ValueError('Cannot reuse an unconverged forward run')
    for rel, expected in baseline['protected_inputs_and_runtime'].items():
        if sha(ROOT/rel) != expected:
            raise ValueError('Forward dependency changed: '+rel)
    snapshot = source/'run_benchmark_source.py'
    manifest = read_json(source/'INPUT_CODE_MANIFEST.json')
    expected = next(row['sha256'] for row in manifest if row['path'] == 'examples/paper2601_chi2/run_benchmark.py')
    if sha(snapshot) != expected:
        raise ValueError('Saved forward source snapshot is not the executed source')
    old, current = ast.parse(snapshot.read_text(encoding='utf8')), ast.parse(Path(__file__).read_text(encoding='utf8'))
    checked = ['point', 'polynomial', 'templates', 'build_forwards', 'Channel']
    for name in checked:
        before = next(node for node in old.body if getattr(node, 'name', None) == name)
        after = next(node for node in current.body if getattr(node, 'name', None) == name)
        if ast.dump(before, include_attributes=False) != ast.dump(after, include_attributes=False):
            raise ValueError('Forward implementation changed: '+name)
    pinned = read_json(source/'FILES.json')
    pinned = {row['path']: row['sha256'] for row in pinned}
    channels, records, copied = {}, {}, []
    for name in ('CsI2021', 'Ar2020'):
        exp = load_experiment(name, resources=ResourceCatalog(ROOT))
        row = read_json(source/f'{name}_FORWARD.json')
        if row['physical_fingerprint'] != exp.physics_fingerprint or row['analysis_fingerprint'] != exp.analysis_fingerprint:
            raise ValueError('Active experiment identity changed: '+name)
        for p in sorted(source.glob(name+'_*')):
            if not p.is_file() or p.name not in pinned or sha(p) != pinned[p.name]:
                raise ValueError('Unpinned or altered saved forward artifact: '+str(p))
            if (output/p.name).exists():
                raise ValueError('Refuse overwriting forward artifact')
            shutil.copy2(p, output/p.name)
            copied.append({'source': str(p), 'destination': p.name, 'sha256': sha(p)})
        coeff = load_npz(source/f'{name}_templates_grid{len(row["runs"])-1}.npz')['coefficients']
        ds = load_dataset(name)
        if name == 'CsI2021':
            ch = Channel(name, coeff, ds.observed*ds.observable.bin_widths, ds.uncertainty*ds.observable.bin_widths,
                         .125, ds.background*ds.observable.bin_widths, .35)
        else:
            ch = Channel(name, coeff, ds.observed, (ds.upper-ds.lower)/2, .12, ds.background, .146)
        if abs(ch.detail()['chi2']-row['runs'][-1]['sm']['chi2']) > 1e-10:
            raise ValueError('Reused forward/statistical reconstruction differs')
        channels[name], records[name] = ch, row
        family = 'COHERENT_CsI' if name == 'CsI2021' else 'COHERENT_Ar'
        for rel in ('experiment.input.yaml', 'experiment.resources.npz', 'statistics/provenance.yaml'):
            TRACKED.add(ROOT/f'data/experiments/{family}/{name}/{rel}')
    TRACKED.add(snapshot)
    write_json(output/'REUSED_FORWARD.json', {'source_directory': str(source),
              'unchanged_protected_files_checked': len(baseline['protected_inputs_and_runtime']),
              'executed_source_snapshot_sha256': expected, 'unchanged_function_AST': checked,
              'copied_forward_artifacts': copied, 'scope': 'Forward only; all statistical profiles and NSI scans rerun'})
    return channels, records


def one_dimension(objective, axis):
    grid = np.linspace(-1., 1., 8001)
    fn = (lambda x: objective(x, np.zeros_like(x))) if axis == 0 else (lambda x: objective(np.zeros_like(x), x))
    values = np.asarray(fn(grid))
    candidate = [0, len(grid)-1] + [i for i in range(1, len(grid)-1) if values[i] <= values[i-1] and values[i] <= values[i+1]]
    minima = []
    for i in candidate:
        if i in (0, len(grid)-1):
            x, chi = grid[i], values[i]
        else:
            opt = minimize_scalar(fn, bounds=(grid[i-1], grid[i+1]), method='bounded', options={'xatol': 1e-13})
            x, chi = opt.x, opt.fun
        minima.append({'epsilon': float(x), 'chi2': float(chi)})
    best = min(minima, key=lambda row: row['chi2'])
    intervals = {}
    for threshold in (1., 2.71):
        residual = values-best['chi2']-threshold
        roots = [brentq(lambda x: float(fn(x)-best['chi2']-threshold), grid[i], grid[i+1], xtol=1e-13)
                 for i in np.where(residual[:-1]*residual[1:] < 0)[0]]
        cuts = [-1., *roots, 1.]
        intervals[str(threshold)] = [[a, b] for a, b in zip(cuts[:-1], cuts[1:])
                                    if fn((a+b)/2)-best['chi2'] <= threshold]
    return {'axis': axis, 'best_fit': best, 'local_minima': minima, 'intervals': intervals,
            'domain': [-1, 1], 'grid': grid, 'chi2': values, 'delta_chi2': values-best['chi2']}


def fit_plane_minimum(objective, channels, *, sigma_upper=None):
    """Condition the event quadratic form and bound every improvement on SM.

    If chi2 <= T=chi2(SM), each Gaussian pull obeys |alpha|<=sa*sqrt(T).
    Cauchy-Schwarz bounds the sum of residuals by sqrt(T)*||sigma||. Thus,
    S_total <= sum_k [sum(D-B)+sqrt(T)*(||sigma_upper||+sb*sum|B|)] /
                          [1-sa*sqrt(T)].
    This bounds an event-count ellipse whenever the denominators and the event
    quadratic form are positive. Optimizers then search a well-conditioned box
    containing that whole ellipse, not a prematurely stable narrow-valley box.
    sigma_upper is a mathematical bound only, never a replacement fit error.
    """
    total = sum((ch.coefficients.sum(axis=1) for ch in channels), np.zeros(6))
    q = np.array([[total[3], total[4]/2], [total[4]/2, total[5]]])
    eigenvalues, eigenvectors = np.linalg.eigh(q)
    if np.min(eigenvalues) <= 0 or total[0] <= 0:
        raise ValueError('A positive event quadratic form is required for this finite-domain proof')
    center = -.5*np.linalg.solve(q, total[1:3])
    event_min = float(total[0]+total[1:3]@center+center@q@center)
    scale = float(total[0])
    transform = eigenvectors@np.diag(np.sqrt(scale/eigenvalues))
    cutoff = float(objective(0., 0.))
    radius_t = np.sqrt(cutoff)
    upper = 0.; channel_bounds = []
    for ch in channels:
        denominator = 1-ch.sigma_alpha*radius_t
        if denominator <= 0:
            raise ValueError('Pull permits signal scale through zero; no finite search-domain bound proved')
        sigma = ch.sigma if sigma_upper is None else sigma_upper.get(ch.name, ch.sigma)
        background = np.zeros_like(ch.observed) if ch.background is None else ch.background
        sb = 0. if ch.sigma_beta is None else ch.sigma_beta
        numerator = float(np.sum(ch.observed-background)+radius_t*(np.linalg.norm(sigma)+sb*np.sum(abs(background))))
        bound = numerator/denominator
        if not np.isfinite(bound) or bound < 0:
            raise ValueError('Invalid event bound')
        upper += bound
        channel_bounds.append({'channel': ch.name, 'minimum_signal_scale_at_chi2_le_SM': denominator,
                               'signal_count_upper_bound': bound, 'sigma_bound': np.asarray(sigma).tolist()})
    radius = float(np.sqrt(max(0., (upper-event_min)/scale)))*(1+1e-9)+1e-9
    bounds = [(-radius, radius)]*2
    function = lambda z: float(objective(*(center+transform@z)))
    fits, starts, de_values = [], [], []
    for seed in (260119883, 11, 123):
        opt = differential_evolution(function, bounds, seed=seed, tol=1e-11, atol=1e-11,
                                     popsize=30, maxiter=2000, polish=True)
        starts.append(np.asarray(opt.x))
        de_values.append(float(opt.fun))
        fits.append({'method': 'conditioned_differential_evolution', 'seed': seed,
                     'coordinates': (center+transform@opt.x).tolist(), 'conditioned_coordinates': opt.x.tolist(),
                     'chi2': float(opt.fun), 'success': bool(opt.success)})
    # Deterministic, separated seeds test additional branches independently of DE.
    line = np.linspace(-radius, radius, 97)
    zzx, zzy = np.meshgrid(line, line)
    grid = np.stack([zzx.ravel(), zzy.ravel()], axis=-1)
    physical = center+grid@transform.T
    values = np.empty(len(grid))
    for i in range(0, len(grid), 4096):
        values[i:i+4096] = objective(physical[i:i+4096, 0], physical[i:i+4096, 1])
    selected = []
    for index in np.argsort(values):
        z = grid[index]
        if not selected or all(np.linalg.norm(z-other) > .12*radius for other in selected):
            selected.append(z)
        if len(selected) == 8:
            break
    starts.extend(selected)
    starts.append(np.linalg.solve(transform, -center))
    for z in starts:
        opt = minimize(function, z, method='Nelder-Mead', bounds=bounds,
                       options={'xatol': 1e-11, 'fatol': 1e-11, 'maxiter': 4000})
        fits.append({'method': 'conditioned_multistart_Nelder_Mead',
                     'coordinates': (center+transform@opt.x).tolist(), 'conditioned_coordinates': opt.x.tolist(),
                     'chi2': float(opt.fun), 'success': bool(opt.success)})
    minimum = min(fits, key=lambda row: row['chi2'])
    spread = max(de_values)-min(de_values)
    verified = spread < 1e-7 and abs(min(de_values)-minimum['chi2']) < 1e-7 and minimum['chi2'] <= cutoff+1e-8
    if not verified:
        raise ValueError('Conditioned independent searches disagree; inspect candidates instead of claiming convergence')
    geometry = {'event_quadratic_matrix': q.tolist(), 'eigenvalues': eigenvalues.tolist(),
                'original_quadratic_condition_number': float(eigenvalues.max()/eigenvalues.min()),
                'event_minimizing_center': center.tolist(), 'conditioned_to_epsilon_matrix': transform.tolist(),
                'event_minimum_count': event_min, 'event_count_scale': scale, 'SM_chi2_cutoff': cutoff,
                'total_signal_upper_bound_for_any_chi2_better_than_SM': upper,
                'conditioned_radius_bound': radius, 'channel_bound_proof': channel_bounds,
                'scope': 'Full ellipse containing every point that can improve SM under the declared Gaussian pull model; three DE seeds plus deterministic multistarts'}
    return {'best_fit': minimum, 'searches': fits, 'search_geometry': geometry,
            'independent_DE_chi2_spread': spread, 'minimum_search_verified': verified}


def plane(objective, channels, n=801):
    fitted = fit_plane_minimum(objective, channels)
    minimum = fitted['best_fit']
    grid = np.linspace(-1, 1, n)
    xx, yy = np.meshgrid(grid, grid)
    values = np.empty(n*n)
    # Bounded memory for batched per-bin arrays.
    for i in range(0, values.size, 8192):
        values[i:i+8192] = objective(xx.ravel()[i:i+8192], yy.ravel()[i:i+8192])
    values = values.reshape(n, n)
    if values.min() < minimum['chi2']-1e-7:
        raise ValueError('Grid found a lower minimum than the optimizer')
    return {'x': grid, 'y': grid, 'chi2': values, 'delta_chi2': values-minimum['chi2'],
            'minima_search': fitted['searches'], 'best_fit': minimum,
            'minimum_search_geometry': fitted['search_geometry'],
            'minimum_search_verified': fitted['minimum_search_verified'],
            'threshold': 4.61, 'minimum_scope': 'Event-quadratic conditioned search over a proven finite improvement domain, multiple independent starts'}


def legacy_and_time(channels):
    d = load_dataset('CsI2017')
    sm = read_json('outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json')
    csi17 = plain(asdict(profile_gaussian_one_pull(sm['counts'], d.observed, d.uncertainty, sigma_alpha=.28)))
    csi17.update({'events': sm['total_events'], 'grid': sm['record']['numerics'],
                  'scope': 'historical 2017 one-pull Gaussian, not 2601 CsI dataset; no substitution into paper combination'})
    ar = channels['Ar2020']
    ds = load_dataset('Ar2020')
    variants = {'paper_form_mean_error': ar.detail(),
                'legacy_asymmetric_irls': plain(asdict(profile_ar2020_irls(ar.coefficients[0], ds.observed, ds.background,
                                     ds.lower, ds.upper, sigma_alpha=.12, sigma_beta=.146))),
                'legacy_asymmetric_bounded': plain(asdict(profile_ar2020_bounded(ar.coefficients[0], ds.observed, ds.background,
                                     ds.lower, ds.upper, sigma_alpha=.12, sigma_beta=.146)))}
    b = load_npz('outputs/csi2021_time_sm_20261107/benchmark.npz')
    c, ac, ss = b['C_raw'], b['AC_raw'], b['SS_derived']
    s, brn, nin = b['signal_counts'], b['BRN_raw_template'], b['NIN_raw_template']
    # Paper does not define a time-binned likelihood. These explicit diagnostics
    # keep the raw ON/OFF semantics and do not claim Eq86 equivalence.
    time = {'shape': list(s.shape), 'signal_events': float(s.sum()), 'observed_C': int(c.sum()),
            'observed_AC': int(ac.sum()), 'SS_template': float(ss.sum()),
            'BRN_raw': float(brn.sum()), 'NIN_raw': float(nin.sum()),
            'paper_chi2': None,
            'reason': '2601 Eq86 is a 1D energy Gaussian. Current 99-bin raw C/AC need a separately specified time likelihood/background contract. No automatic sqrt(C) errors or prior-driven rescaling.'}
    return {'CsI2017': csi17, 'Ar2020': variants, 'CsI_time': time}


def plot_results(output, planes, scans, channels, references):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    colors = {'CONUS_plus': '#e68b10', 'COHERENT_CsI_Ar': '#187ac0'}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for ax, name in zip(axes, ('CONUS_plus', 'COHERENT_CsI_Ar')):
        p = planes[name]
        ax.contourf(p['x'], p['y'], p['delta_chi2'], levels=[-1e-8, 4.61], colors=[colors[name]], alpha=.3)
        ax.contour(p['x'], p['y'], p['delta_chi2'], levels=[4.61], colors=[colors[name]], linewidths=1.5)
        if references is not None:
            for polygon_index in (0, 1):
                rows = references[(references['experiment'] == name) & (references['polygon'] == polygon_index)]
                if rows.size:
                    ax.plot(rows['epsilon_ee_uV'], rows['epsilon_ee_dV'], 'k--', lw=.8)
        ax.plot(0, 0, 'k+', ms=7)
        ax.set(xlim=(-1, 1), ylim=(-1, 1), xlabel=r'$\epsilon_{ee}^{uV}$', ylabel=r'$\epsilon_{ee}^{dV}$',
               title=name.replace('_', ' ')+'\nLocal inputs; Gaussian paper form')
        ax.set_aspect('equal'); ax.grid(alpha=.15)
        ax.legend(handles=[Line2D([0], [0], color=colors[name], label='Calculated: delta chi2 = 4.61'),
                           Line2D([0], [0], color='k', ls='--', label='Paper Fig4 vector outline')], fontsize=8)
    fig.suptitle('2601.19883v2 Fig4 comparison: partial reproduction; solar NSI unavailable', fontsize=11)
    fig.savefig(output/'fig4_comparison.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for ax, coordinate in zip(axes, ('epsilon_ee_uV', 'epsilon_ee_dV')):
        for name in ('CONUS_plus', 'COHERENT_CsI_Ar'):
            scan = scans[name][coordinate]
            ax.plot(scan['grid'], scan['delta_chi2'], color=colors[name], label=name.replace('_', ' '))
        ax.axhline(2.71, color='k', ls='--', lw=1, label='90% CL: 2.71 (1 dof)')
        ax.set(xlabel=coordinate, ylabel='Profiled delta chi2', xlim=(-.15, .55), ylim=(0, 12))
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle('One coordinate varied; other NSI coordinates fixed to zero', fontsize=11)
    fig.savefig(output/'nsi_1d_profiles.png', dpi=180); plt.close(fig)


def report(output, summary):
    c, a = summary['SM']['CsI2021'], summary['SM']['Ar2020']
    conus = summary['SM']['CONUS_plus']
    sol = summary['solar']['variants']['paper_percentages']
    lines = ['# 2601.19883v2 卡方复算：当前本地输入\n',
             '状态：**PARTIAL_REPRODUCTION / NOT_REVIEWED**。已复算论文形式的统计函数、SM 点和可用矢量 NSI 扫描；没有取得作者原始 χ² 网格，不能宣称图3/图4完整复现。\n',
             '[总数值](SUMMARY.json) · [统计验证](VALIDATION.json) · [输入/代码哈希](INPUT_CODE_MANIFEST.json) · '
             '[原图矢量参考](paper_reference/README.md) · [本次计划和保护基线](PLAN_AND_BASELINE.json) · '
             '[复算代码](../../examples/paper2601_chi2/README.md)\n',
             '## 原文定义与数据版本\n',
             '| 分析 | 论文位置 | 本次处理 |\n|---|---|---|',
             '| CsI2021（一维九箱） | PDF p20 Eq86；Ref42=2110.07730 | 信号/背景两个全箱相关 Gaussian pull .125/.35；counts/PE 的 D/B/σ 一起乘箱宽，改成 counts/bin。 |',
             '| Ar2020 | PDF p20 Eq86；Ref43=2003.10630 | Gaussian pull .12/.146；主对照采用现有上下误差平均，属于明确局部选择；另列旧非对称 IRLS / 有界优化。 |',
             '| 太阳8B三样本 | PDF p20 Eqs87/88 | 各样本独立 .12 pull；主对照 σ=D×37.1%/37.3%/36.9%，另存旧1.3/28/3.95。 |',
             '| CONUS+ | PDF pp20-21 Eqs89/90 | 19个有符号 excess 箱，Gaussian .169 pull；digitized 正负误差均值为主，另有上下误差敏感性。 |',
             '| CsI-time / CsI2017 | 不属于该论文采用的统计实现 | 保留当前99箱计数和2017旧卡方，不把它们加进论文CsI2021+Ar组合。 |\n',
             '## SM 点：只 profile nuisance，不拟合 NSI\n',
             '| 本地分析 | 未拟合 SM 信号 | profiled χ² | α | β |\n|---|---:|---:|---:|---:|',
             f'| CsI2021 九箱 | {c["predicted_signal_events"]:.9f} | {c["chi2"]:.9f} | {c["alpha"]:.9f} | {c["beta"]:.9f} |',
             f'| Ar2020 平均误差 | {a["predicted_signal_events"]:.9f} | {a["chi2"]:.9f} | {a["alpha"]:.9f} | {a["beta"]:.9f} |',
             f'| CONUS+ 平均误差 | {conus["predicted_signal_events"]:.9f} | {conus["chi2"]:.9f} | {conus["alpha"]:.9f} | — |']
    for name in ('PandaX_paired', 'PandaX_US2'):
        row = sol['samples'][name]; q = row['SM_profile']
        lines.append(f'| {name} | {row["signal_interval"][0]:.9f} | {q["chi2"]:.9f} | {q["alpha"]:.9f} | — |')
    bounds = sol['joint_chi2_bounds_tail_only']
    lines += [f'\n太阳三样本联合 χ² 的**尾段不确定性范围**为 [{bounds[0]:.9f}, {bounds[1]:.9f}]；'
              f'显式平尾效率敏感性为 {sol["joint_chi2_flat_tail_sensitivity"]:.9f}。`joint_chi2=null`，范围不是统计置信区间。',
              '\n原文没有给出各实验的 SM χ² 表。上述数字是本地输入计算值，不能用306±20/159±43/395±106三个总信号量替代分箱观测，也不能把83.2（其他文献结果）当作2601参考。\n',
              '## NSI：一维和二维最小值分别计算\n',
              '映射采用论文 p22 Eq95：C61q_NSI = -√2 G_F εee^qV。只改变 ee 的两个实数矢量坐标；μ、τ、其他算符固定原值。'
              '一维按 Eq92 使用 Δχ²=2.71；二维按正文使用4.61（图标题取整为4.6）。每条一维曲线减自己的最小值；二维减二维搜索最小值。'
              'CsI和Ar使用独立的α、β，不把两份数据共用一个pull。\n',
              '| 分析 | 参数 | 90%一维区间 | χ²min |\n|---|---|---|---:|']
    for name, coordinates in summary['scans_1d'].items():
        for coordinate, s in coordinates.items():
            intervals = ' ∪ '.join(f'[{lo:.7f}, {hi:.7f}]' for lo, hi in s['intervals']['2.71'])
            lines.append(f'| {name} | {coordinate} | {intervals} | {s["best_fit"]["chi2"]:.9f} |')
    lines += ['\n[逐点一维扫描](nsi_1d_scans.csv) · [向量算符Λ下界与图3对照](vector_scale_limits.csv)\n',
              '![一维卡方](nsi_1d_profiles.png)\n',
              '![二维与原图对照](fig4_comparison.png)\n',
              '实线/填色为当前本地计算，黑虚线为2601图4 PDF矢量轮廓；当前光谱、误差和输入选择存在差异，曲线相近不证明作者实现等价。'
              '[二维网格/极小值和原图偏差](SUMMARY.json) 保存扩展搜索域及非裁剪轮廓点上的Δχ²，不通过调参数强行贴图。\n',
              '## 未闭合的复现条件\n',
              '- 太阳 NSI：当前单bin入射态仅为SM flavor-universal trace-one；SM不需要的Pνα(E)在ee NSI中成为必需输入。2601引用2409.04703，其计算还讨论NSI传播效应；现有单bin没有该数表/执行合同，不能把νe比例猜成1或1/3。因此太阳二维带和依赖它的图3条形保留NOT_RUN。',
              '- XENONnT总接受度缺2.77–3 keVnr，SM只给尾段界及单独平尾敏感性。',
              '- CsI2021现有九箱D/B/σ为legacy residual数组，扣背景组成尚未由原始发布逐箱确认；99箱时间数据不能自动替代。',
              '- Ar当前效率坐标在包中标PE而官方来源列是keVee；本次保留现值，未静默改单位。原文未指定非对称误差转σ的方法，本次平均误差为可审核近似。',
              '- CONUS使用本地Response和选定通量，与2501.17843的KN设置有差异；观测误差来自2501图1数字化，尚不能认证为2601作者采用的原始数组。',
              '- 图3其余20个算符还需要明确flavor矩阵、LNV最终态、符号分支及相应forward验证；本次只给已验证C61u/d的尺度转换。没有生成或伪造全部算符约束。',
              '- 不给跨全部实验的“精确联合χ²”：其共同系统误差相关性未在此次原文/本地合同中确定。\n',
              '## 验证与文件归属\n',
              'Gaussian解析profile分别与现有Runtime、数值极小化及协方差恒等式核对；核模板有非零原生Slow对照、'
              '独立网格细化；原始data和Runtime的哈希保护见VALIDATION。生产Runtime不导入本示例，未更新dataset注册或科学Gate。\n',
              '[CsI2021 forward/收敛](CsI2021_FORWARD.json) · [Ar forward/收敛](Ar2020_FORWARD.json) · '
              '[太阳两种误差](SOLAR.json) · [2017/时间/Ar方法差异](METHOD_VARIANTS.json) · '
              '[CSV总表](sm_chi2.csv) · [文件清单](FILES.json)\n',
              '[返回outputs](../README.md) · [返回最新五实验导航](../../docs/experiments/LATEST_EXPERIMENTS.md)\n']
    (output/'README.md').write_text('\n'.join(lines), encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-forward', type=Path, help='Explicit previous run with source snapshot, hashes and converged forwards')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(p.name not in ('PLAN_AND_BASELINE.json', 'paper_reference', 'pilot_run1', 'pilot_run2') for p in output.iterdir()):
        parser.error('Choose a fresh output directory; existing results are immutable')
    if not (output/'PLAN_AND_BASELINE.json').exists():
        protected = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                     for area in ('cevns_pyeft', 'data', 'examples/CONUS_Plus', 'examples/COHERENT_CsI')
                     for p in (ROOT/area).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        write_json(output/'PLAN_AND_BASELINE.json', {'request': '2601.19883v2 chi-square benchmark',
                   'route': 'validation_only; no production scientific semantics changes',
                   'protected_inputs_and_runtime': protected,
                   'thresholds': {'profile_abs_chi2': 1e-7, 'forward_abs_chi2': .02,
                                  'forward_bin_abs_or_rel': [.005, .005]},
                   'canonical_gate_changes': False})
    start = time.perf_counter()
    channels, forward = (reuse_forwards(output, args.reuse_forward) if args.reuse_forward else build_forwards(output))
    cc, conus_axes = conus_channel()
    channels['CONUS_plus'] = cc['mean']
    solar = solar_results()
    variants = legacy_and_time(channels)
    validation = {'gaussian_profiles': {name: check_profile(ch) for name, ch in channels.items()},
                  'forward': {name: row['convergence'] for name, row in forward.items()}}
    # Check density-to-count conversion exactly once, including its covariance.
    ds = load_dataset('CsI2021'); widths = ds.observable.bin_widths
    stock = profile_gaussian_two_pull(channels['CsI2021'].coefficients[0]/widths, ds.observed,
                        ds.background, ds.uncertainty, sigma_alpha=.125, sigma_beta=.35)
    difference = abs(stock.chi2-channels['CsI2021'].detail()['chi2'])
    if difference > 1e-9:
        raise ValueError('Density/counts chi2 invariance failed')
    validation['density_count_invariance_abs_chi2'] = difference
    validation['conus_error_sensitivity_SM'] = {name: ch.detail() for name, ch in cc.items()}
    validation['conus_template_axis_contract'] = conus_axes
    objectives = {name: ch.chi2 for name, ch in channels.items()}
    objectives['COHERENT_CsI_Ar'] = lambda x, y: channels['CsI2021'].chi2(x, y)+channels['Ar2020'].chi2(x, y)
    scans, planes, rows, scan_summary = {}, {}, [], {}
    for name, objective in objectives.items():
        scans[name], scan_summary[name] = {}, {}
        for axis, coordinate in enumerate(('epsilon_ee_uV', 'epsilon_ee_dV')):
            scan = one_dimension(objective, axis)
            scans[name][coordinate] = scan
            scan_summary[name][coordinate] = {key: value for key, value in scan.items() if key not in ('grid', 'chi2', 'delta_chi2')}
            rows.extend({'analysis': name, 'coordinate': coordinate, 'epsilon': float(x),
                         'chi2': float(chi), 'delta_chi2': float(delta)} for x, chi, delta in
                         zip(scan['grid'], scan['chi2'], scan['delta_chi2']))
        if name in ('CONUS_plus', 'COHERENT_CsI_Ar'):
            plane_channels = [channels['CONUS_plus']] if name == 'CONUS_plus' else [channels['CsI2021'], channels['Ar2020']]
            planes[name] = plane(objective, plane_channels)
            p = planes[name]
            np.savez_compressed(output/f'{name}_plane.npz', x=p['x'], y=p['y'], chi2=p['chi2'], delta_chi2=p['delta_chi2'])
            print(name, '2D best', p['best_fit'], flush=True)
    write_csv(output/'nsi_1d_scans.csv', rows)
    reference_path = output/'paper_reference/fig4_plotted_polygons.csv'
    references, comparisons = None, {}
    if reference_path.exists():
        references = np.genfromtxt(reference_path, names=True, delimiter=',', dtype=None, encoding='utf8')
        for name, p in planes.items():
            r = references[(references['experiment'] == name) & (references['clipped_at_axis_boundary'] == 0)]
            delta = objectives[name](r['epsilon_ee_uV'], r['epsilon_ee_dV'])-p['best_fit']['chi2']
            comparisons[name] = {'nonclipped_vertices': len(r), 'nominal_paper_delta_chi2': 4.61,
                                 'local_delta_chi2_min': float(delta.min()), 'median': float(np.median(delta)),
                                 'max': float(delta.max()), 'within_10percent_of_4_61_fraction': float(np.mean(abs(delta-4.61)<.461))}
    scale_rows = []
    bars = None
    barpath = output/'paper_reference/fig3_plotted_limits.csv'
    if barpath.exists():
        with barpath.open(encoding='utf8', newline='') as f:
            bars = list(csv.DictReader(f))
    for name in ('CONUS_plus', 'COHERENT_CsI_Ar'):
        for coord, operator in [('epsilon_ee_uV', 'O6u_1'), ('epsilon_ee_dV', 'O6d_1')]:
            intervals = scans[name][coord]['intervals']['2.71']
            for sign in ('C_positive', 'C_negative', 'both_signs_conservative'):
                endpoints = [v for interval in intervals for v in interval
                             if (sign == 'both_signs_conservative' or (v < 0 if sign == 'C_positive' else v > 0))]
                if not endpoints:
                    continue
                maximum = max(abs(v) for v in endpoints)
                limit = 1/np.sqrt(np.sqrt(2)*G_F*maximum)
                paper_value = None
                if bars is not None:
                    selected = [row for row in bars if row['experiment'] == name and row['operator'] == operator]
                    paper_value = float(selected[0]['lambda_GeV_from_plotted_height'])
                scale_rows.append({'analysis': name, 'operator': operator, 'coefficient_sign_branch': sign,
                                   'max_abs_epsilon_90percent': maximum, 'local_lambda_lower_GeV': limit,
                                   'paper_graphical_lambda_GeV': paper_value,
                                   'relative_difference_to_plot': None if paper_value is None else limit/paper_value-1,
                                   'note': '1D profiled minimum; Eq91/95 mapping; sign branch not specified by paper bar'})
    write_csv(output/'vector_scale_limits.csv', scale_rows)
    summary = {'date': '2026-11-11', 'paper': PAPER, 'paper_sha256': sha(ROOT/PAPER),
               'status': 'PARTIAL_REPRODUCTION', 'human_gate': 'NOT_REVIEWED',
               'conus_template_axes': conus_axes,
               'SM': {name: ch.detail() for name, ch in channels.items()}, 'solar': solar,
               'method_variants': variants, 'scans_1d': scan_summary,
               'planes': {name: {k: v for k, v in p.items() if k not in ('x', 'y', 'chi2', 'delta_chi2')} for name, p in planes.items()},
               'fig4_boundary_comparison': comparisons, 'vector_scale_limits': scale_rows,
               'inference': {'1d_delta_chi2': 2.71, '2d_delta_chi2': 4.61, 'coverage': 'paper asymptotic convention; no toy calibration'},
               'not_run': {'solar_nsi': 'Missing oscillation-averaged flavor state numerical contract for ee NSI',
                           'CsI_time_paper_chi2': 'Different data representation and likelihood',
                           'Fig3_other_20_operators': 'Additional flavor/LNV/sign choices and forward validations required'},
               'environment': {'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()},
               'elapsed_seconds': time.perf_counter()-start}
    TRACKED.add(ROOT/PAPER)
    for p in (ROOT/'cevns_pyeft').rglob('*.py'):
        TRACKED.add(p)
    for p in Path(__file__).parent.glob('*'):
        if p.is_file(): TRACKED.add(p)
    manifest = [{'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(p), 'bytes': p.stat().st_size}
                for p in sorted(TRACKED) if p.is_file()]
    write_json(output/'INPUT_CODE_MANIFEST.json', manifest)
    baseline = read_json(output/'PLAN_AND_BASELINE.json')
    changed = [rel for rel, value in baseline['protected_inputs_and_runtime'].items() if sha(ROOT/rel) != value]
    if changed:
        raise ValueError('Protected inputs/runtime changed: '+repr(changed))
    validation['protected_runtime_input_files_unchanged'] = len(baseline['protected_inputs_and_runtime'])
    validation['all_profile_checks_pass'] = True
    validation['scientific_reproduction_certified'] = False
    validation['forward_SM_convergence_all_declared_checks_pass'] = all(c['passes_declared_SM_tolerance']
                                      for row in forward.values() for c in row['convergence'] if c['used_for_final_convergence'])
    validation['planes_minimum_search_stable'] = all(p['minimum_search_verified'] for p in planes.values())
    write_json(output/'VALIDATION.json', validation)
    write_json(output/'SUMMARY.json', summary)
    write_json(output/'SOLAR.json', solar)
    write_json(output/'METHOD_VARIANTS.json', variants)
    smrows = [{'analysis': name, 'predicted_signal_events': ch.detail()['predicted_signal_events'],
               'chi2_profiled': ch.detail()['chi2'], 'alpha': ch.detail()['alpha'], 'beta': ch.detail()['beta']}
              for name, ch in channels.items()]
    write_csv(output/'sm_chi2.csv', smrows)
    plot_results(output, planes, scans, channels, references)
    report(output, summary)
    write_json(output/'FILES.json', [{'path': str(p.relative_to(output)).replace('\\', '/'), 'bytes': p.stat().st_size,
                                     'sha256': sha(p)} for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'FILES.json'])
    print(json.dumps({'status': summary['status'], 'convergence_checks': validation['forward_SM_convergence_all_declared_checks_pass'],
                      'SM_chi2': {k: v['chi2'] for k, v in summary['SM'].items()}, 'elapsed': summary['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
