"""Audit joint objectives and actual Fig4 boundaries, without changing inputs.

The previous mean-Ar-error analysis, current asymmetric Ar analysis and a
shared-flux sensitivity remain separate. This is not an author-likelihood fit.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys
import time
import numpy as np
from scipy.optimize import brentq, differential_evolution, minimize_scalar

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import run_benchmark as prior
from cevns_pyeft.experiments.solar_singlebin import load_singlebin
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.statistics.profiling import profile_ar2020_bounded, profile_ar2020_irls

PREVIOUS = ROOT/'outputs/paper2601_chi2_20261111'


def save(path, value):
    prior.write_json(path, value)


def get_channels():
    summary = json.loads((PREVIOUS/'SUMMARY.json').read_text(encoding='utf8'))
    channels = {}
    for name in ('CsI2021', 'Ar2020'):
        row = summary['SM'][name]
        coefficients = prior.load_npz(PREVIOUS/f'{name}_templates_grid8.npz')['coefficients']
        channels[name] = prior.Channel(name, coefficients, np.array(row['observed']), np.array(row['sigma']),
                                      row['sigma_alpha'], np.array(row['background']), row['sigma_beta'])
    conus, axis_contract = prior.conus_channel()
    return summary, channels['CsI2021'], channels['Ar2020'], conus['mean'], axis_contract


class AsymmetricAr:
    """Convex piecewise-Gaussian objective; bounded Newton with line search.

    Each fixed-sign quadratic subproblem is minimized exactly over [-1,1]^2,
    including edge re-optimization. Independent stock bounded optimization is
    used for holdouts. No reference errors or pull widths are changed.
    """
    def __init__(self, channel):
        self.channel = channel
        self.data = prior.load_dataset('Ar2020')
        self.minus = self.data.observed-self.data.lower
        self.plus = self.data.upper-self.data.observed
        if np.any(self.minus <= 0) or np.any(self.plus <= 0):
            raise ValueError('Positive original asymmetric errors required')
        self.max_projected_step = 0.
        self.max_iterations = 0

    def evaluate(self, signals):
        s = np.asarray(signals, float)
        d, b = self.data.observed, self.data.background
        r0 = d-s-b
        alpha = np.zeros(s.shape[:-1]); beta = alpha.copy()

        def cost(a, bb):
            model = (1+a[..., None])*s+(1+bb[..., None])*b
            sig = np.where(model > d, self.plus, self.minus)
            return np.sum(((d-model)/sig)**2, axis=-1)+(a/.12)**2+(bb/.146)**2

        for iteration in range(60):
            model = (1+alpha[..., None])*s+(1+beta[..., None])*b
            sigma = np.where(model > d, self.plus, self.minus)
            w = 1/sigma**2
            aa = np.sum(s*s*w, axis=-1)+1/.12**2
            ab = np.sum(s*b*w, axis=-1)
            bb = np.sum(b*b*w, axis=-1)+1/.146**2
            u = np.sum(s*r0*w, axis=-1); v = np.sum(b*r0*w, axis=-1)
            det = aa*bb-ab*ab
            a0 = (u*bb-v*ab)/det; b0 = (v*aa-u*ab)/det
            # Four edges plus an interior candidate; never merely clip both pulls.
            candidates = [(np.clip(a0, -1, 1), np.clip(b0, -1, 1))]
            for fixed in (-1., 1.):
                candidates += [(np.full_like(alpha, fixed), np.clip((v-ab*fixed)/bb, -1, 1)),
                               (np.clip((u-ab*fixed)/aa, -1, 1), np.full_like(beta, fixed))]
            qcost = lambda a, z: aa*a*a+2*ab*a*z+bb*z*z-2*u*a-2*v*z
            target_a, target_b = candidates[0]
            best = qcost(target_a, target_b)
            for ca, cb in candidates[1:]:
                value = qcost(ca, cb); choose = value < best
                target_a, target_b = np.where(choose, ca, target_a), np.where(choose, cb, target_b)
                best = np.minimum(best, value)
            da, db = target_a-alpha, target_b-beta
            ga = 2*(aa*alpha+ab*beta-u); gb = 2*(ab*alpha+bb*beta-v)
            pg_a = alpha-np.clip(alpha-ga/(2*aa), -1, 1)
            pg_b = beta-np.clip(beta-gb/(2*bb), -1, 1)
            projected = np.maximum(abs(pg_a), abs(pg_b))
            if float(np.max(projected)) < 2e-10:
                break
            old = cost(alpha, beta)
            step = np.ones_like(alpha)
            descent = ga*da+gb*db
            for _ in range(35):
                new_a, new_b = alpha+step*da, beta+step*db
                trial = cost(new_a, new_b)
                bad = trial > old+1e-4*step*descent+1e-12
                if not np.any(bad):
                    break
                step = np.where(bad, step/2, step)
            alpha, beta = alpha+step*da, beta+step*db
        # Check the final constrained first-order condition in pull coordinates.
        model = (1+alpha[..., None])*s+(1+beta[..., None])*b
        w = 1/np.where(model > d, self.plus, self.minus)**2
        residual = d-model
        ga = -2*np.sum(s*residual*w, axis=-1)+2*alpha/.12**2
        gb = -2*np.sum(b*residual*w, axis=-1)+2*beta/.146**2
        curvature_a = 2*(np.sum(s*s*w, axis=-1)+1/.12**2)
        curvature_b = 2*(np.sum(b*b*w, axis=-1)+1/.146**2)
        violation = float(max(np.max(abs(alpha-np.clip(alpha-ga/curvature_a, -1, 1))),
                              np.max(abs(beta-np.clip(beta-gb/curvature_b, -1, 1)))))
        if violation > 1e-8:
            raise ValueError('Asymmetric profile KKT condition failed: '+str(violation))
        self.max_projected_step = max(self.max_projected_step, violation)
        self.max_iterations = max(self.max_iterations, iteration+1)
        return cost(alpha, beta), alpha, beta

    def chi2(self, x, y):
        return self.evaluate(prior.polynomial(self.channel.coefficients, x, y))[0]


def simultaneous_profile(csi, ar, x, y, common_flux=False):
    """Independent augmented least squares, also defining the sensitivity model."""
    sx, sy = prior.polynomial(csi.coefficients, x, y), prior.polynomial(ar.coefficients, x, y)
    shape = sx.shape[:-1]
    residual = np.concatenate([csi.observed-sx-csi.background, ar.observed-sy-ar.background], axis=-1)
    sig = np.r_[csi.sigma, ar.sigma]
    zeros_x, zeros_y = np.zeros_like(sx), np.zeros_like(sy)
    if common_flux:
        # p21 states 10% CsI flux contribution. Sharing it with Ar is only a sensitivity.
        columns = [np.concatenate([.10*sx, .10*sy], axis=-1),
                   np.concatenate([np.sqrt(.125**2-.10**2)*sx, zeros_y], axis=-1),
                   np.concatenate([zeros_x, np.sqrt(.12**2-.10**2)*sy], axis=-1),
                   np.concatenate([np.broadcast_to(.35*csi.background, sx.shape), zeros_y], axis=-1),
                   np.concatenate([zeros_x, np.broadcast_to(.146*ar.background, sy.shape)], axis=-1)]
    else:
        columns = [np.concatenate([.125*sx, zeros_y], axis=-1),
                   np.concatenate([np.broadcast_to(.35*csi.background, sx.shape), zeros_y], axis=-1),
                   np.concatenate([zeros_x, .12*sy], axis=-1),
                   np.concatenate([zeros_x, np.broadcast_to(.146*ar.background, sy.shape)], axis=-1)]
    matrix = np.stack(columns, axis=-1)/sig[:, None]
    r = residual/sig
    count = len(columns)
    if not shape:
        augmented = np.vstack([matrix, np.eye(count)])
        pulls = np.linalg.lstsq(augmented, np.r_[r, np.zeros(count)], rcond=None)[0]
    else:
        normal = np.einsum('...bi,...bj->...ij', matrix, matrix)+np.eye(count)
        rhs = np.einsum('...bi,...b->...i', matrix, r)
        pulls = np.linalg.solve(normal, rhs[..., None])[..., 0]
    remaining = r-np.einsum('...bi,...i->...b', matrix, pulls)
    return np.sum(remaining**2, axis=-1)+np.sum(pulls**2, axis=-1), pulls


def paper_intersections(vertices, name, xvalue):
    roots = []
    for polygon in (0, 1):
        row = vertices[(vertices['experiment'] == name) & (vertices['polygon'] == polygon)]
        x, y = row['epsilon_ee_uV'], row['epsilon_ee_dV']
        x, y = np.r_[x, x[0]], np.r_[y, y[0]]
        chosen = np.flatnonzero(((x[:-1] < xvalue) & (x[1:] >= xvalue)) |
                               ((x[:-1] >= xvalue) & (x[1:] < xvalue)))
        roots.extend((y[chosen]+(xvalue-x[chosen])*(y[chosen+1]-y[chosen])/(x[chosen+1]-x[chosen])).tolist())
    return sorted(set(round(value, 12) for value in roots))


def model_intersections(objective, minimum, xvalue):
    grid = np.linspace(-1., 1., 16001)
    f = lambda y: objective(xvalue+np.zeros_like(y), y)-minimum-4.61
    values = f(grid)
    indices = np.flatnonzero(values[:-1]*values[1:] < 0)
    return [brentq(lambda y: float(f(y)), grid[i], grid[i+1], xtol=1e-12) for i in indices]


def fit_minimum(objective, channels, sigma_upper=None):
    result = prior.fit_plane_minimum(objective, channels, sigma_upper=sigma_upper)
    return result['best_fit'], result


def solar_audit(previous):
    source = previous['solar']['variants']['paper_percentages']
    names = ('PandaX_paired', 'PandaX_US2', 'XENONnT')
    rows = [source['samples'][name] for name in names]
    signals = np.array([row['flat_tail_sensitivity']['events'] for row in rows])
    observed = np.array([row['observed_fitted_signal'] for row in rows])
    sigma = np.array([row['sigma_stat'] for row in rows])
    matrix = np.diag(.12*signals/sigma)
    residual = (observed-signals)/sigma
    pulls = np.linalg.lstsq(np.vstack([matrix, np.eye(3)]), np.r_[residual, np.zeros(3)], rcond=None)[0]
    numerical = float(np.sum((residual-matrix@pulls)**2)+pulls@pulls)
    common = prior.profile_gaussian_one_pull(signals, observed, sigma, sigma_alpha=.12)
    # Verify the current single-bin route cannot silently produce an ee NSI fit.
    try:
        predict_experiment(load_singlebin('PandaX_US2', root=ROOT), parameters=prior.point(.01, 0, .23857),
                           numerics={'n_er': 5, 'n_enu': 5})
    except UnsupportedCapabilityError as exc:
        rejection = str(exc)
    else:
        raise ValueError('SM-only solar route unexpectedly accepted ee NSI')
    return {'paper_contract': '2601v2 p20 Eq88: three independent pulls, each .12; sum raw chi2 then subtract joint parameter minimum for scans',
            'SM_joint_primary_value': None, 'SM_tail_only_bounds': source['joint_chi2_bounds_tail_only'],
            'flat_tail_sensitivity_only': {'independent_analytic': source['joint_chi2_flat_tail_sensitivity'],
                                         'independent_simultaneous_lstsq': numerical,
                                         'shared_pull_not_Eq88': common.chi2},
            'samples': [{'name': name, 'observed': row['observed_fitted_signal'], 'sigma': row['sigma_stat'],
                         'signal_interval': row['signal_interval']} for name, row in zip(names, rows)],
            'solar_NSI_computed': False, 'SM_only_guard_rejection': rejection,
            'missing': ['Numerical oscillation-averaged flavor state P_nu_alpha(E;epsilon_u,epsilon_d), Eq87 and Ref26 AppB',
                        'If computing propagation: solar electron/neutron density and B8 production profiles, oscillation inputs and chosen NSI treatment',
                        'XENONnT total acceptance from approximately2.77 to3 keVnr'],
            'claim_correction': 'No solar combined NSI contour was computed in the previous run. SM tail bounds are not NSI confidence intervals.'}


def plot(output, vertices, previous, scenarios, minima, solar, conus, conus_fit):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    grid = np.linspace(-1, 1, 801)
    xx, yy = np.meshgrid(grid, grid)
    surfaces = {}
    for name, objective in scenarios.items():
        values = np.empty(xx.size)
        for i in range(0, values.size, 4096):
            values[i:i+4096] = objective(xx.ravel()[i:i+4096], yy.ravel()[i:i+4096])
        surfaces[name] = values.reshape(xx.shape)-minima[name]['chi2']
        np.savez_compressed(output/(name+'_surface.npz'), x=grid, y=grid, delta_chi2=surfaces[name],
                            chi2=values.reshape(xx.shape), minimum_chi2=minima[name]['chi2'])
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.9), constrained_layout=True)
    c = prior.load_npz(PREVIOUS/'CONUS_plus_plane.npz')
    conus_delta = c['chi2']-conus_fit['best_fit']['chi2']
    np.savez_compressed(output/'CONUS_plus_surface.npz', x=c['x'], y=c['y'], chi2=c['chi2'],
                        delta_chi2=conus_delta, minimum_chi2=conus_fit['best_fit']['chi2'])
    axes[0].contour(c['x'], c['y'], conus_delta, levels=[4.61], colors=['#e68b10'], linewidths=1.5)
    axes[1].contour(grid, grid, surfaces['previous_mean_Ar'], levels=[4.61], colors=['#6b89aa'], linestyles='--')
    axes[1].contourf(grid, grid, surfaces['current_asymmetric_Ar'], levels=[-1e-7, 4.61], colors=['#2b80b6'], alpha=.18)
    axes[1].contour(grid, grid, surfaces['current_asymmetric_Ar'], levels=[4.61], colors=['#1f73a5'], linewidths=1.5)
    for ax, name in zip(axes, ('CONUS_plus', 'COHERENT_CsI_Ar', 'Solar_joint')):
        for polygon in (0, 1):
            row = vertices[(vertices['experiment'] == name) & (vertices['polygon'] == polygon)]
            ax.plot(row['epsilon_ee_uV'], row['epsilon_ee_dV'], 'k:', lw=1.1)
        ax.set(xlim=(-1, 1), ylim=(-1, 1), xlabel=r'$\epsilon_{ee}^{uV}$', ylabel=r'$\epsilon_{ee}^{dV}$')
        ax.set_aspect('equal'); ax.grid(alpha=.15)
    axes[0].set_title('CONUS+\nTwo-parameter comparison')
    axes[0].legend(handles=[Line2D([0], [0], color='#e68b10', label='Previous local calculation'),
                           Line2D([0], [0], color='k', ls=':', label='Paper Fig4 boundary')], fontsize=8)
    axes[1].set_title('COHERENT: CsI + Ar\nAr error convention changes the inner gap')
    axes[1].legend(handles=[Line2D([0], [0], color='#1f73a5', label='Current asymmetric Ar'),
                           Line2D([0], [0], color='#6b89aa', ls='--', label='Previous mean-error Ar'),
                           Line2D([0], [0], color='k', ls=':', label='Paper Fig4 boundary')], fontsize=7, loc='upper right')
    axes[2].set_title('Solar: paired + US2 + XENONnT\nNo calculated NSI contour')
    axes[2].text(0, -.02, 'Paper boundary only\nFlavor state and XENON tail missing', ha='center', va='center',
                 fontsize=9, bbox={'facecolor': 'white', 'alpha': .9, 'edgecolor': '.8'})
    fig.suptitle('Joint-result audit: paper agreement has not been established', fontsize=12)
    fig.savefig(output/'all_groups_audit.png', dpi=180); plt.close(fig)
    y = np.linspace(-.15, .50, 4001)
    fig, ax = plt.subplots(figsize=(8, 4.7), constrained_layout=True)
    palette = {'previous_mean_Ar': '#6b89aa', 'current_asymmetric_Ar': '#1f73a5', 'shared_10percent_SNS_flux': '#916197'}
    labels = {'previous_mean_Ar': 'Previous mean-error Ar', 'current_asymmetric_Ar': 'Current asymmetric Ar',
              'shared_10percent_SNS_flux': 'Shared SNS flux sensitivity (not adopted)'}
    for name, objective in scenarios.items():
        ax.plot(y, objective(np.zeros_like(y), y)-minima[name]['chi2'], color=palette[name], label=labels[name])
    roots = paper_intersections(vertices, 'COHERENT_CsI_Ar', 0.)
    for k, value in enumerate(roots):
        ax.axvline(value, color='k', ls=':', lw=1, label='Paper Fig4 boundaries at u=0' if k == 0 else None)
    ax.axhline(4.61, color='k', ls='--', lw=1, label='Two-parameter threshold 4.61')
    ax.set(xlabel=r'$\epsilon_{ee}^{dV}$ at $\epsilon_{ee}^{uV}=0$', ylabel=r'$\Delta\chi^2$ relative to each 2D minimum',
           ylim=(0, 8), title='The discrepancy concerns the inner gap, not only the outer limit')
    ax.grid(alpha=.18); ax.legend(fontsize=8)
    fig.savefig(output/'joint_slice_u0.png', dpi=180); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(p.name not in ('PLAN_AND_BASELINE.json', 'unconditioned_search') for p in output.iterdir()):
        parser.error('Use a fresh audit directory')
    start = time.perf_counter()
    previous, csi, ar, conus, axes = get_channels()
    asymmetric = AsymmetricAr(ar)
    scenarios = {'previous_mean_Ar': lambda x, y: csi.chi2(x, y)+ar.chi2(x, y),
                 'current_asymmetric_Ar': lambda x, y: csi.chi2(x, y)+asymmetric.chi2(x, y),
                 'shared_10percent_SNS_flux': lambda x, y: simultaneous_profile(csi, ar, x, y, True)[0]}
    checks = []
    rng = np.random.default_rng(260119883)
    points = [(0., 0.), (.1, .08), (.2, 0.), (.4, 0.), (1., -1.),
              *map(tuple, rng.uniform(-1, 1, (30, 2)))]
    for x, y in points:
        mean = float(scenarios['previous_mean_Ar'](x, y))
        simultaneous, pulls = simultaneous_profile(csi, ar, x, y)
        signal = prior.polynomial(ar.coefficients, x, y)
        exact = asymmetric.evaluate(signal)
        native = profile_ar2020_bounded(signal, asymmetric.data.observed, asymmetric.data.background,
                                       asymmetric.data.lower, asymmetric.data.upper, sigma_alpha=.12, sigma_beta=.146)
        legacy = profile_ar2020_irls(signal, asymmetric.data.observed, asymmetric.data.background,
                                    asymmetric.data.lower, asymmetric.data.upper, sigma_alpha=.12, sigma_beta=.146)
        if abs(mean-float(simultaneous)) > 1e-8 or abs(float(exact[0])-native.chi2) > 1e-7:
            raise ValueError('Independent joint/asymmetric optimizer check failed')
        checks.append({'coordinates': [x, y], 'sum_profiled_mean': mean, 'simultaneous_four_pull_lstsq': float(simultaneous),
                       'asymmetric_newton': float(exact[0]), 'stock_bounded': native.chi2, 'stock_irls': legacy.chi2,
                       'max_joint_abs_difference': abs(mean-float(simultaneous)),
                       'max_asymmetric_abs_difference': abs(float(exact[0])-native.chi2),
                       'stock_bounded_success': native.success, 'simultaneous_unit_pull_order': ['CsI_signal', 'CsI_background', 'Ar_signal', 'Ar_background'],
                       'simultaneous_unit_pulls': pulls.tolist()})
    minima, search, sm = {}, {}, {}
    for name, objective in scenarios.items():
        sigma_upper = {'Ar2020': np.maximum(asymmetric.plus, asymmetric.minus)} if name == 'current_asymmetric_Ar' else None
        minima[name], search[name] = fit_minimum(objective, [csi, ar], sigma_upper)
        sm[name] = float(objective(0., 0.))
        print(name, 'SM', sm[name], 'minimum', minima[name], flush=True)
    vertices = np.genfromtxt(PREVIOUS/'paper_reference/fig4_plotted_polygons.csv', names=True,
                             delimiter=',', dtype=None, encoding='utf8')
    slices = []
    for x in (-.75, -.5, -.25, 0., .25, .5, .75):
        original = paper_intersections(vertices, 'COHERENT_CsI_Ar', x)
        for name, objective in scenarios.items():
            roots = model_intersections(objective, minima[name]['chi2'], x)
            slices.append({'scenario': name, 'epsilon_u': x, 'paper_y_boundaries': original,
                           'model_y_boundaries': roots,
                           'boundary_count_matches': len(original) == len(roots),
                           'max_abs_coordinate_difference_if_count_matches': max(abs(a-b) for a, b in zip(original, roots)) if len(original) == len(roots) and roots else None,
                           'model_delta_chi2_at_paper_boundaries': [float(objective(x, y)-minima[name]['chi2']) for y in original]})
    solar = solar_audit(previous)
    conus_fit = prior.fit_plane_minimum(conus.chi2, [conus])
    bad_sum = {}
    for coordinate in ('epsilon_ee_uV', 'epsilon_ee_dV'):
        single_min_sum = sum(previous['scans_1d'][name][coordinate]['best_fit']['chi2'] for name in ('CsI2021', 'Ar2020'))
        joint_minimum = previous['scans_1d']['COHERENT_CsI_Ar'][coordinate]['best_fit']['chi2']
        bad_sum[coordinate] = {'joint_parameter_minimum': joint_minimum, 'sum_of_separate_parameter_minima': single_min_sum,
                               'wrong_delta_offset_if_subtracting_separate_minima': joint_minimum-single_min_sum,
                               'previous_code_used_correct_joint_minimum': True}
    conus_check = []
    for x, y in points[:8]:
        signal = prior.polynomial(conus.coefficients, x, y)
        mat = np.r_[conus.sigma_alpha*signal/conus.sigma, 1.][:, None]
        rhs = np.r_[(conus.observed-signal)/conus.sigma, 0.]
        nuisance = np.linalg.lstsq(mat, rhs, rcond=None)[0]
        chi = float(np.sum((rhs-mat@nuisance)**2))
        if abs(chi-float(conus.chi2(x, y))) > 1e-8:
            raise ValueError('CONUS direct scalar profile check failed')
        conus_check.append({'coordinates': [x, y], 'lstsq_chi2': chi, 'profile_chi2': float(conus.chi2(x, y))})
    plot(output, vertices, previous, scenarios, minima, solar, conus, conus_fit)
    boundary = vertices[(vertices['experiment'] == 'COHERENT_CsI_Ar') & (vertices['clipped_at_axis_boundary'] == 0)]
    boundary_checks = {}
    for name, objective in scenarios.items():
        delta = objective(boundary['epsilon_ee_uV'], boundary['epsilon_ee_dV'])-minima[name]['chi2']
        boundary_checks[name] = {'vertices': len(delta), 'min': float(delta.min()), 'median': float(np.median(delta)),
                                 'max': float(delta.max()), 'within_10percent_of_4_61_fraction': float(np.mean(abs(delta-4.61) < .461))}
    summary = {'status': 'JOINT_PAPER_REPRODUCTION_NOT_ESTABLISHED', 'human_gate': 'NOT_REVIEWED',
               'date': '2026-11-11', 'SM_joint_scenarios': sm, 'two_parameter_minima': minima, 'minimum_search': search,
               'slice_comparison': slices, 'boundary_checks': boundary_checks, 'joint_minimum_identity_audit': bad_sum,
               'solar': solar, 'conus_axis_contract': axes, 'conus_lstsq_checks': conus_check,
               'conus_conditioned_minimum_search': conus_fit,
               'optimizer_defect': {'previous_mean_joint_minimum': previous['planes']['COHERENT_CsI_Ar']['best_fit']['chi2'],
                   'corrected_mean_joint_minimum': minima['previous_mean_Ar']['chi2'],
                   'delta_chi2_understatement_in_previous_surface': previous['planes']['COHERENT_CsI_Ar']['best_fit']['chi2']-minima['previous_mean_Ar']['chi2'],
                   'cause': 'Unconditioned narrow-valley optimization and early stopping after two coincident local modes; not a change of objective, input or threshold'},
               'cross_all_experiments': {'paper_fig4': 'Three separately fitted groups, not their intersection or a single all-experiment fit',
                   'all_experiment_fit_reproduced': False,
                   'avoid_double_counting': ['CsI2021 1D and 99-bin time analysis use the same data and cannot be independent terms',
                                            'CsI2017 is not a replacement for the CsI2021 term in paper Fig4; overlap must be verified before combining exposures']},
               'confirmed_method_difference': 'Previous joint benchmark averaged Ar errors instead of retaining the current asymmetric Ar definition',
               'not_proven_causes': ['A unique author joint nuisance correlation matrix was not obtained',
                                      'Legacy CsI observed/background/error interpretation and Ar efficiency coordinate units remain unresolved',
                                      'Close Fig3 outer scale limits do not validate Fig4 inner boundaries'],
               'elapsed_seconds': time.perf_counter()-start}
    validation = {'independent_profile_checks': checks, 'max_joint_abs_error': max(c['max_joint_abs_difference'] for c in checks),
                  'max_asymmetric_abs_error': max(c['max_asymmetric_abs_difference'] for c in checks),
                  'asymmetric_max_projected_KKT_step': asymmetric.max_projected_step,
                  'asymmetric_max_iterations': asymmetric.max_iterations,
                  'solar_independent_lstsq_error': abs(solar['flat_tail_sensitivity_only']['independent_analytic']-solar['flat_tail_sensitivity_only']['independent_simultaneous_lstsq']),
                  'paper_contour_reproduction_pass': False,
                  'conditioned_searches_verified': all(row['minimum_search_verified'] for row in search.values()) and conus_fit['minimum_search_verified'],
                  'numeric_checks_pass': True}
    save(output/'SUMMARY.json', summary); save(output/'VALIDATION.json', validation)
    save(output/'SOLAR_AUDIT.json', solar)
    save(output/'SLICE_BOUNDARIES.json', slices)
    prior.write_csv(output/'SM_JOINT_COMPARISON.csv', [{'scenario': name, 'chi2_SM': sm[name], 'chi2_2d_min': minima[name]['chi2']} for name in scenarios])
    write_report(output, summary, validation)
    plan_path = output/'PLAN_AND_BASELINE.json'
    if plan_path.exists():
        baseline = json.loads(plan_path.read_text(encoding='utf8'))
        modified = [rel for group in ('protected_inputs_and_runtime', 'previous_numerical_artifacts')
                    for rel, expected in baseline[group].items() if prior.sha(ROOT/rel) != expected]
        if modified:
            raise ValueError('Protected scientific inputs/results changed: '+repr(modified))
        save(output/'PROTECTION.json', {'modified_protected_files': modified,
                                      'runtime_input_files_checked': len(baseline['protected_inputs_and_runtime']),
                                      'previous_numerical_files_checked': len(baseline['previous_numerical_artifacts'])})
    paths = [Path(__file__), HERE/'run_benchmark.py', PREVIOUS/'SUMMARY.json', PREVIOUS/'paper_reference/fig4_plotted_polygons.csv',
             PREVIOUS/'CsI2021_templates_grid8.npz', PREVIOUS/'Ar2020_templates_grid8.npz',
             ROOT/'data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz',
             ROOT/'data/experiments/COHERENT_Ar/Ar2020/statistics/provenance.yaml',
             ROOT/'data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml',
             ROOT/'cevns_pyeft/statistics/profiling.py', ROOT/'cevns_pyeft/experiments/solar_singlebin.py',
             ROOT/'cevns_pyeft/propagation/backends/snudd.py', ROOT/'docs/references/General_CEvNS/2601.19883v2.pdf']
    save(output/'INPUT_CODE_MANIFEST.json', [{'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': prior.sha(p)} for p in paths])
    save(output/'FILES.json', [{'path': str(p.relative_to(output)).replace('\\', '/'), 'sha256': prior.sha(p), 'bytes': p.stat().st_size}
                              for p in sorted(output.iterdir()) if p.is_file() and p.name != 'FILES.json'])
    print(json.dumps({'status': summary['status'], 'joint_checks': validation['max_joint_abs_error'],
                      'asymmetric_checks': validation['max_asymmetric_abs_error'], 'SM': sm}), flush=True)


def write_report(output, result, checks):
    x0 = [row for row in result['slice_comparison'] if row['epsilon_u'] == 0]
    text = ['# 联合分析复核：未通过论文轮廓复现\n',
            '**结论：前一轮联合结果确有数值问题，不能视为2601.19883v2的复现结果。** '
            '已修复二维搜索漏掉更低极小值的缺陷，并分开保留Ar误差处理差异；联合加法和独立pull解析极小化本身通过独立核算。'
            '修复后仍有论文边界偏差，不能把它宣称为最终论文结果。\n',
            '[总数值](SUMMARY.json) · [数值核验](VALIDATION.json) · [逐截面边界](SLICE_BOUNDARIES.json) · '
            '[太阳联合核对](SOLAR_AUDIT.json) · [输入与代码](INPUT_CODE_MANIFEST.json) · [原数据保护](PROTECTION.json) · '
            '[文件清单](FILES.json) · [复算入口](../../examples/paper2601_chi2/README.md)\n',
            '## CsI＋Ar：明确的方法差异\n',
            '前一轮将Ar上下误差平均化，以固定σ使用Gaussian双pull；当前Ar主线是按预测/数据位置选择误差侧的非对称模型。'
            '这会改变参数相关的χ²形状，不只是给SM常数加一个偏移。保留三种独立方案，不修改数据或调节误差贴图：\n',
            '| 方案 | SM χ² | 二维 χ²min | 定位 |\n|---|---:|---:|---|']
    labels = {'previous_mean_Ar': ('此前平均误差', '近似对照；不代表当前Ar主线'),
              'current_asymmetric_Ar': ('当前非对称Ar', '本地现有统计模型；仍非已确认的作者实现'),
              'shared_10percent_SNS_flux': ('共享10% SNS通量', '相关性敏感性；非论文已确定的联合协方差')}
    for name, (label, meaning) in labels.items():
        text.append(f'| {label} | {result["SM_joint_scenarios"][name]:.9f} | {result["two_parameter_minima"][name]["chi2"]:.9f} | {meaning} |')
    text += ['\n## 直接检查图4内侧边界\n',
             '固定 εee^uV=0，论文图4蓝带有四个交点。以下列的是二维区域与该截线的交点，使用二维最小值和Δχ²=4.61，'
             '不是把另一坐标profile掉的一维区间。原图数值只有PDF图形精度。\n',
             '| 方案 | εee^dV 的四条边界 |\n|---|---|',
             '| 论文PDF矢量图形 | '+', '.join(f'{v:.6f}' for v in x0[0]['paper_y_boundaries'])+' |']
    for row in x0:
        text.append('| '+labels[row['scenario']][0]+' | '+', '.join(f'{v:.6f}' for v in row['model_y_boundaries'])+' |')
    text += ['\n由此可见：此前外侧尺度下界相差不到0.4%，不能证明中间禁区或整条二维带一致。'
             '当前非对称Ar改善部分内侧边界，但没有逐点重合。\n',
             '![三个实验组逐项核对](all_groups_audit.png)\n',
             '![联合卡方截面](joint_slice_u0.png)\n',
             '## 联合数学与最小值核验\n',
             f'**已确认的优化器缺陷：** 原均误差联合χ²min={result["optimizer_defect"]["previous_mean_joint_minimum"]:.9f}，'
             f'条件化搜索得到{result["optimizer_defect"]["corrected_mean_joint_minimum"]:.9f}；'
             f'旧表面Δχ²因此少算{result["optimizer_defect"]["delta_chi2_understatement_in_previous_surface"]:.9f}。'
             '此前在原始(u,d)坐标扩大box后两次找到同一个局部模式，便错误地当作搜索稳定；该判据现已移除。\n',
             '新搜索先由总事件数二次型平移、旋转和缩放坐标，再用Gaussian pull与残差的Cauchy界，'
             '构造包含所有可能优于SM点的有限事件椭圆。三组独立随机种子加确定性网格多起点在该域内核验。'
             '搜索几何、计数上界推导项、所有候选及其差异保存于SUMMARY。没有通过改变参考阈值或数据抬高/压低最小值。\n',
             r'对于独立pull，实际计算为 $\min_{a_C,b_C,a_A,b_A}(\chi_C^2+\chi_A^2)=\min_{a_C,b_C}\chi_C^2+\min_{a_A,b_A}\chi_A^2$，'
             'NSI坐标在两实验间必须相同。已把所有21箱放进一次增广最小二乘独立核对，'
             f'最大差异为 {checks["max_joint_abs_error"]:.3g}。没有发现χ²相加、箱宽换算或独立pull重复计数错误。\n',
             '扫描必须减去联合目标函数自己的最小值，不能减去两个实验各自的NSI最小值之和。'
             '前一轮采用了联合目标函数这一正确形式，但其最小值数值漏搜，已如上修正；限制搜索到图框也不能作为无依据的修复。'
             '搜索域和各方案最小值均单独保存在SUMMARY。\n',
             '非对称Ar与现有Runtime有界数值优化逐点核对，采用box边界再优化和线搜索，避免把解析解的两个pull简单裁剪当作通用有界极小值。'
             f'本轮核对最大χ²差为 {checks["max_asymmetric_abs_error"]:.3g}；这验证求解器，不验证论文输入来源。\n',
             '## 太阳三样本与CONUS\n',
             '2601 Eq88明确是三个独立12% pull，不能把其他参考文献的单个共享pull直接搬来。'
             '已用同时三pull最小二乘复核：平尾假设下χ²='+f'{result["solar"]["flat_tail_sensitivity_only"]["independent_analytic"]:.9f}'+'。'
             '该数仍是明确假设的SM点，主值保持null；接受度尾段造成的SM界为'+str(result['solar']['SM_tail_only_bounds'])+'。\n',
             '**太阳绿色NSI联合带上一轮根本未计算。** 当前单binSM路径会拒绝ee NSI；传播适配器的存在不等于具有数值Pνα(E)输入。'
             '所缺传播/味态和XENON尾段见SOLAR_AUDIT。不能把SMχ²范围当成绿色带已经复现。\n',
             'CONUS图4是u/d两个参数同时拟合，不是跨实验联合。旧模板(d,u)已与2601的(u,d)统一；本轮再次以独立单pull最小二乘核对。'
             '本地CONUS轮廓与原图仍有偏差，不能据此替其他联合组背书。\n',
             '## 所有实验不能直接堆加\n',
             '论文图4展示CONUS、COHERENT(CsI＋Ar)、太阳三样本三个分别拟合的区域，没有给出它们的全实验联合参考轮廓。'
             'CsI2021一维与99箱时间分析使用同一批观测，不能同时作为独立项；CsI2017也不能未经曝光重叠核实就再加进来。'
             '本轮没有另造“全实验联合已复现”的结论。\n',
             '## 仍需补齐的论文等价条件\n',
             '| 条件 | 当前证据与影响 |\n|---|---|',
             '| CsI九箱观测/背景/σ的原始处理 | 当前是legacy residual数组；其扣背景组成、误差与作者采用表的等价尚未确认。 |',
             '| Ar误差和效率坐标 | 当前主线非对称模型已分别重算；论文未在式86给出可逐箱验证的误差处理，PE/keVee坐标来源冲突仍保留。 |',
             '| CsI与Ar nuisance相关性 | 原文给总宽度，不提供本次可读的联合相关矩阵；10%共享通量仅作敏感性，未被选作“更贴图”的新主模型。 |',
             '| 太阳味态 | ee NSI需要Pνα(E;ε)；当前单bin只有SM通用味态，不允许填1/3替代。 |',
             '| XENON接受度尾段 | 约2.77–3 keVnr未取得，阻断无额外假设的完整联合点和绿色NSI带。 |\n',
             '下一步要复现原图，需取得或逐项重建上述作者级输入/约定。现有资料只能确定方法差异及其数值影响，尚不能唯一判定剩余差异来自哪一个输入；不将差异归咎于论文，也不强行拟合图形。\n',
             '[前一轮结果（保留为对照）](../paper2601_chi2_20261111/README.md) · [返回outputs](../README.md)\n']
    (output/'README.md').write_text('\n'.join(text), encoding='utf8')


if __name__ == '__main__':
    main()
