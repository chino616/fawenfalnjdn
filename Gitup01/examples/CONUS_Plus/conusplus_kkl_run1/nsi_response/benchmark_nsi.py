"""NSI likelihood benchmarks using the existing project's coefficient kernel."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('nsi')
from dataclasses import replace
import csv
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import brentq, minimize, minimize_scalar
from scipy.stats import chi2 as chi2_distribution
import sm_model as sm
from nsi_model import BASIS, COUPLINGS, HERE, model, point, verify_snapshot
from prepare_predictions import KERNEL, SLOW_CASES
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.contracts.parameters import TheoryPoint
from cevns_pyeft.core.predict import predict
from cevns_pyeft.kernels.compiler import StaleCompiledKernelError
from cevns_pyeft.kernels.interface_storage import load_compiled_kernel
from cevns_pyeft.statistics.profiling import profile_gaussian_one_pull
OUTPUT = LAYOUT.path('outputs')
THRESHOLDS = {'1sigma': 1.0, '90percent': float(chi2_distribution.ppf(0.9, 1))}
THRESHOLD_2D = float(chi2_distribution.ppf(0.9, 2))
SIGMA_ALPHA = 0.169
PLANE_SPECS = {'diag_ud': ('epsilon_ee_dV', 'epsilon_ee_uV', (-1.0, 1.0), (-1.0, 1.0)), 'fc_ud': ('epsilon_emu_uV', 'epsilon_emu_dV', (-1.0, 1.0), (-1.0, 1.0)), 'ring_mu': ('epsilon_ee_dV', 'epsilon_emu_dV', (-0.4, 0.8), (-0.5, 0.6)), 'ring_tau': ('epsilon_ee_dV', 'epsilon_etau_dV', (-0.4, 0.8), (-0.5, 0.6)), 'fc_ud_tau': ('epsilon_etau_uV', 'epsilon_etau_dV', (-1.0, 1.0), (-1.0, 1.0))}
ONE_DIMENSIONAL = {'epsilon_ee_uV': ('diag_ud', 'y'), 'epsilon_ee_dV': ('diag_ud', 'x'), 'epsilon_emu_uV': ('fc_ud', 'x'), 'epsilon_emu_dV': ('fc_ud', 'y'), 'epsilon_etau_uV': ('fc_ud_tau', 'x'), 'epsilon_etau_dV': ('fc_ud_tau', 'y')}

def csv_write(path, rows):
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def load_observed():
    original = sm.DATA / 'statistics/conusplus_2501_17843v3_fig1_digitized.csv'
    data = np.genfromtxt(original, names=True, delimiter=',', encoding='utf-8')
    assert len(data) == 19
    np.testing.assert_array_equal(data['energy_low_eVee'], sm.EDGES[:-1])
    np.testing.assert_array_equal(data['energy_high_eVee'], sm.EDGES[1:])
    assert np.all(data['error_minus'] > 0) and np.all(data['error_plus'] > 0)
    errors = {'mean': (data['error_minus'] + data['error_plus']) / 2.0, 'lower': data['error_minus'], 'upper': data['error_plus']}
    rows = [{'bin_index': i + 1, 'energy_low_eVee': sm.EDGES[i], 'energy_high_eVee': sm.EDGES[i + 1], 'observed_signed_excess': data['excess'][i], 'sigma_primary_mean': errors['mean'][i], 'sigma_lower_sensitivity': errors['lower'][i], 'sigma_upper_sensitivity': errors['upper'][i], 'unit': 'counts kg^-1 (10 eVee)^-1', 'source_id': '2501_17843v3_p10_fig1_black_vectors'} for i in range(19)]
    csv_write(LAYOUT.path('data/statistics_input.csv'), rows)
    return (data, errors)

def evaluate_polynomial(coefficients, x, y):
    x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    basis = np.stack((np.ones_like(x), x, y, x * x, x * y, y * y), axis=-1)
    return basis @ coefficients

def build_polynomials(kernel):
    polynomials = {}
    for name, (x_name, y_name, _, _) in PLANE_SPECS.items():

        def values(x, y):
            return kernel.predict(parameters=point(**{x_name: x, y_name: y})).counts
        constant = values(0, 0)
        plus_x, minus_x, plus_y, minus_y = (values(1, 0), values(-1, 0), values(0, 1), values(0, -1))
        linear_x, linear_y = ((plus_x - minus_x) / 2.0, (plus_y - minus_y) / 2.0)
        quadratic_x = (plus_x + minus_x) / 2.0 - constant
        quadratic_y = (plus_y + minus_y) / 2.0 - constant
        cross = values(1, 1) - constant - linear_x - linear_y - quadratic_x - quadratic_y
        polynomials[name] = np.array([constant, linear_x, linear_y, quadratic_x, cross, quadratic_y])
    np.savez_compressed(OUTPUT / 'nsi_quadratic_templates.npz', **polynomials)
    return polynomials

def validate_predictions(experiment, kernel, polynomials):
    diagnostics = {'direct_slow_comparisons': []}
    parent = np.load(LAYOUT.path('data/sm_reference/fine_641.npz'))
    zero = predict(experiment, parameters=point(), numerics=sm.settings(161, 641), backend='fast', compiled=kernel)
    np.testing.assert_allclose(zero.counts, parent['counts'], rtol=1e-10, atol=1e-10)
    diagnostics['zero_NSI_parent_SM_max_absolute_error'] = float(np.max(abs(zero.counts - parent['counts'])))
    for name, coordinates, _, n_enu in SLOW_CASES:
        if n_enu != 641:
            continue
        slow = np.load(OUTPUT / ('slow_' + name + '.npz'))
        fast = kernel.predict(parameters=point(**coordinates))
        difference = abs(fast.counts - slow['counts'])
        assert np.all(difference <= 1e-08 + 1e-08 * abs(slow['counts'])), name
        for isotope in sm.ISOTOPES:
            np.testing.assert_allclose(fast.components['reactor_antinu_e', isotope], slow['counts_' + isotope], rtol=1e-08, atol=1e-08)
        diagnostics['direct_slow_comparisons'].append({'case': name, 'couplings': coordinates, 'max_absolute_difference_events': float(difference.max()), 'max_relative_difference': float(np.max(difference / np.maximum(slow['counts'], 1e-100))), 'total_slow': float(slow['counts'].sum()), 'total_fast': float(fast.counts.sum()), 'passed': True})
    fine = np.load(OUTPUT / 'slow_u_ee_005.npz')['counts']
    coarse = np.load(OUTPUT / 'slow_u_ee_005_energy321.npz')['counts']
    convergence = abs(fine - coarse)
    assert np.all(convergence <= 0.0001 + 0.003 * fine)
    diagnostics['nonzero_NSI_energy_grid_refinement'] = {'n_enu': [321, 641], 'coupling': 'epsilon_ee_uV=0.05', 'n_er': 161, 'max_absolute_difference_events': float(convergence.max()), 'max_relative_difference': float(np.max(convergence / fine)), 'passed': True}
    rng = np.random.default_rng(20261106)
    polynomial_error = 0.0
    minimum_value = 1e+100
    for name, (x_name, y_name, x_domain, y_domain) in PLANE_SPECS.items():
        for x, y in zip(rng.uniform(*x_domain, 12), rng.uniform(*y_domain, 12)):
            expected = kernel.predict(parameters=point(**{x_name: x, y_name: y})).counts
            actual = evaluate_polynomial(polynomials[name], x, y)
            error = abs(actual - expected)
            assert np.all(error <= 1e-08 + 1e-10 * abs(expected)), (name, x, y)
            polynomial_error = max(polynomial_error, float(error.max()))
            minimum_value = min(minimum_value, float(actual.min()))
    diagnostics['polynomial_vs_interface_max_absolute_error_events'] = polynomial_error
    diagnostics['polynomial_parameter_points_checked'] = 60
    diagnostics['minimum_random_point_bin_prediction_events'] = minimum_value
    reference = kernel.predict(parameters=point(epsilon_emu_uV=0.12, epsilon_emu_dV=-0.06)).counts
    imaginary = kernel.predict(parameters=point(epsilon_emu_uV=0.12j, epsilon_emu_dV=-0.06j)).counts
    tau = kernel.predict(parameters=point(epsilon_etau_uV=0.12, epsilon_etau_dV=-0.06)).counts
    negative = kernel.predict(parameters=point(epsilon_emu_uV=-0.12, epsilon_emu_dV=0.06)).counts
    pair = kernel.predict(parameters=point(epsilon_emu_uV=0.12, epsilon_emu_dV=-0.06), representation='pair').counts
    for other in (imaginary, tau, negative, pair):
        np.testing.assert_allclose(other, reference, rtol=1e-11, atol=1e-10)
    diagnostics['flavor_phase_evenness_full_pair_checks'] = 'PASS'
    try:
        kernel.predict(model=replace(experiment, run=replace(experiment.run, seconds=experiment.run.seconds * 1.01)))
    except StaleCompiledKernelError:
        diagnostics['changed_exposure_rejects_stale_kernel'] = True
    else:
        raise AssertionError('A changed exposure must invalidate the compiled kernel')
    try:
        kernel.predict(parameters=TheoryPoint(wc_triplets={(7, 1, 'u'): np.eye(3) * 1e-08}))
    except UnsupportedCapabilityError:
        diagnostics['outside_operator_basis_rejected'] = True
    else:
        raise AssertionError('An out-of-subspace coefficient must be rejected')
    diagnostics['representation'] = 'Exact degree-2 real-NSI polynomial from the existing integrated bilinear operator kernel'
    diagnostics['human_gate'] = 'NOT_REVIEWED'
    return diagnostics

def profile(signals, observed, sigma):
    signals = np.asarray(signals, dtype=float)
    if not np.all(np.isfinite(signals)) or np.min(signals) < -1e-08:
        raise ValueError('Invalid NSI spectrum')
    return profile_gaussian_one_pull(signals, observed, sigma, sigma_alpha=SIGMA_ALPHA)

def fit_one_dimension(coefficients, axis, observed, sigma, n_grid=4001):

    def signal(value):
        return evaluate_polynomial(coefficients, value if axis == 'x' else 0.0, value if axis == 'y' else 0.0)

    def objective(value):
        return profile(signal(value), observed, sigma).chi2
    grid = np.linspace(-1, 1, n_grid)
    chi = np.array([objective(value) for value in grid])
    indices = np.flatnonzero((chi[1:-1] <= chi[:-2]) & (chi[1:-1] <= chi[2:])) + 1
    minima = []
    for index in indices:
        optimum = minimize_scalar(objective, bounds=(grid[index - 1], grid[index + 1]), method='bounded', options={'xatol': 1e-12})
        minima.append({'epsilon': float(optimum.x), 'chi2': float(optimum.fun), 'alpha': profile(signal(optimum.x), observed, sigma).alpha})
    minima += [{'epsilon': float(grid[i]), 'chi2': float(chi[i]), 'alpha': profile(signal(grid[i]), observed, sigma).alpha} for i in (0, n_grid - 1)]
    best = min(minima, key=lambda result: result['chi2'])
    intervals = {}
    domain_boundaries = {}
    for label, threshold in THRESHOLDS.items():
        residual = chi - best['chi2'] - threshold
        roots = []
        for index in np.flatnonzero(residual[:-1] * residual[1:] < 0):
            roots.append(float(brentq(lambda value: objective(value) - best['chi2'] - threshold, grid[index], grid[index + 1], xtol=1e-12)))
        split = [-1.0, *roots, 1.0]
        accepted = [[a, b] for a, b in zip(split[:-1], split[1:]) if objective((a + b) / 2) - best['chi2'] <= threshold]
        intervals[label] = accepted
        domain_boundaries[label] = any((a == -1.0 or b == 1.0 for a, b in accepted))
    return {'best_fit': best, 'local_minima': [m for m in minima if -1 < m['epsilon'] < 1], 'intervals': intervals, 'intervals_touch_scan_boundary': domain_boundaries, 'epsilon_grid': grid, 'chi2_grid': chi, 'delta_chi2_grid': chi - best['chi2'], 'alpha_grid': np.array([profile(signal(value), observed, sigma).alpha for value in grid]), 'events_grid': np.array([signal(value).sum() for value in grid]), 'n_grid': n_grid}

def fit_plane(coefficients, specification, observed, sigma, n_grid=501):
    _, _, x_domain, y_domain = specification
    x = np.linspace(*x_domain, n_grid)
    y = np.linspace(*y_domain, n_grid)
    xx, yy = np.meshgrid(x, y)
    signals = evaluate_polynomial(coefficients, xx, yy)
    values = np.fromiter((profile(row, observed, sigma).chi2 for row in signals.reshape(-1, 19)), dtype=float, count=n_grid * n_grid).reshape(n_grid, n_grid)
    best_index = np.unravel_index(np.argmin(values), values.shape)

    def objective(coordinates):
        return profile(evaluate_polynomial(coefficients, coordinates[0], coordinates[1]), observed, sigma).chi2
    starts = [(x[best_index[1]], y[best_index[0]]), (0.0, 0.0), (0.17, 0), (0.35, 0), (0, 0.38)]
    candidates = []
    for start in starts:
        result = minimize(objective, start, method='Powell', bounds=(x_domain, y_domain), options={'xtol': 1e-10, 'ftol': 1e-11, 'maxiter': 500})
        candidates.append({'coordinates': result.x.tolist(), 'chi2': float(result.fun), 'success': bool(result.success)})
    best = min(candidates, key=lambda result: result['chi2'])
    return {'x': x, 'y': y, 'chi2': values, 'delta_chi2': values - best['chi2'], 'best_fit': best, 'minimum_candidates': candidates, 'threshold': THRESHOLD_2D}

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    verify_snapshot()
    experiment = model()
    kernel = load_compiled_kernel(KERNEL, model=experiment, numerics=sm.settings(161, 641))
    print('Loaded fingerprint-checked existing interface kernel', flush=True)
    polynomials = build_polynomials(kernel)
    observed_table, errors = load_observed()
    observed = observed_table['excess']
    validation = validate_predictions(experiment, kernel, polynomials)
    primary, sensitivity = ({}, {})
    scan_rows, interval_rows = ([], [])
    paper_rows = list(csv.DictReader(LAYOUT.path('data/benchmark/tableII_1sigma.csv').open(encoding='utf-8')))
    paper_intervals = {name: [[float(row['lower']), float(row['upper'])] for row in paper_rows if row['coupling'] == name] for name in COUPLINGS}
    for coupling, (plane_name, axis) in ONE_DIMENSIONAL.items():
        result = fit_one_dimension(polynomials[plane_name], axis, observed, errors['mean'])
        stability = fit_one_dimension(polynomials[plane_name], axis, observed, errors['mean'], n_grid=2001)
        assert all((len(result['intervals'][label]) == len(stability['intervals'][label]) for label in THRESHOLDS))
        root_difference = max((abs(a - b) for label in THRESHOLDS for first, second in zip(result['intervals'][label], stability['intervals'][label]) for a, b in zip(first, second)))
        assert root_difference < 5e-06
        assert not any(result['intervals_touch_scan_boundary'].values())
        compact = {key: value for key, value in result.items() if not key.endswith('_grid')}
        compact['interval_grid_stability_max_difference'] = root_difference
        compact['paper_1sigma_intervals'] = paper_intervals[coupling]
        if len(result['intervals']['1sigma']) == len(paper_intervals[coupling]):
            differences = [[a - b for a, b in zip(ours, published)] for ours, published in zip(result['intervals']['1sigma'], paper_intervals[coupling])]
            compact['endpoint_differences_vs_paper'] = differences
            compact['paper_endpoint_tolerance_0_001_passed'] = bool(np.max(abs(np.asarray(differences))) <= 0.001)
        else:
            compact['paper_endpoint_tolerance_0_001_passed'] = False
        primary[coupling] = compact
        sensitivity[coupling] = {}
        for mode in ('lower', 'upper'):
            check = fit_one_dimension(polynomials[plane_name], axis, observed, errors[mode], n_grid=2001)
            sensitivity[coupling][mode] = {'best_fit': check['best_fit'], 'intervals': check['intervals']}
        for index, epsilon in enumerate(result['epsilon_grid']):
            scan_rows.append({'coupling': coupling, 'epsilon': epsilon, 'chi2_profiled': result['chi2_grid'][index], 'delta_chi2': result['delta_chi2_grid'][index], 'alpha_profiled': result['alpha_grid'][index], 'predicted_total_events': result['events_grid'][index], 'provenance_id': 'CONUS_vector_NSI_response_v1'})
        for label, limits in result['intervals'].items():
            for interval_index, (lower, upper) in enumerate(limits, 1):
                interval_rows.append({'coupling': coupling, 'confidence': label, 'delta_chi2_threshold': THRESHOLDS[label], 'interval_index': interval_index, 'lower': lower, 'upper': upper, 'best_fit_epsilon': result['best_fit']['epsilon'], 'minimum_chi2': result['best_fit']['chi2'], 'sigma_mode': 'mean', 'provenance_id': 'CONUS_vector_NSI_response_v1'})
        np.savez_compressed(OUTPUT / ('scan_' + coupling + '.npz'), **{key: value for key, value in result.items() if key.endswith('_grid')})
        print(coupling + ' 1sigma ' + repr(result['intervals']['1sigma']), flush=True)
    csv_write(OUTPUT / 'nsi_intervals.csv', interval_rows)
    csv_write(OUTPUT / 'nsi_scan_1d.csv', scan_rows)
    sm_result = profile(evaluate_polynomial(polynomials['diag_ud'], 0, 0), observed, errors['mean'])
    tested = []
    for signal in (evaluate_polynomial(polynomials['diag_ud'], 0, 0), evaluate_polynomial(polynomials['diag_ud'], 0, 0.19), evaluate_polynomial(polynomials['fc_ud'], 0.2, 0.1)):
        analytic = profile(signal, observed, errors['mean'])

        def alpha_objective(alpha):
            return float(np.sum(((observed - (1 + alpha) * signal) / errors['mean']) ** 2) + (alpha / SIGMA_ALPHA) ** 2)
        numerical = minimize_scalar(alpha_objective, bounds=(-4, 4), method='bounded', options={'xatol': 1e-13})
        assert abs(numerical.fun - analytic.chi2) < 1e-08
        tested.append({'chi2_analytic': analytic.chi2, 'chi2_numeric': float(numerical.fun), 'alpha_analytic': analytic.alpha, 'alpha_numeric': float(numerical.x)})
    validation['analytic_alpha_vs_independent_numeric_minimum'] = tested
    validation['interval_grid_stability'] = 'PASS for 2001 versus 4001 scan samples with independently refined roots'
    validation['observed_negative_values_retained'] = int(np.sum(observed < 0))
    sm.write_json(OUTPUT / 'validation.json', validation)
    sm.write_json(OUTPUT / 'one_dimensional_results.json', primary)
    sm.write_json(OUTPUT / 'error_sensitivity.json', sensitivity)
    planes = {}
    for name in ('diag_ud', 'fc_ud', 'ring_mu', 'ring_tau'):
        print('Computing two-parameter plane ' + name, flush=True)
        result = fit_plane(polynomials[name], PLANE_SPECS[name], observed, errors['mean'])
        np.savez_compressed(OUTPUT / ('plane_' + name + '.npz'), x=result['x'], y=result['y'], chi2=result['chi2'], delta_chi2=result['delta_chi2'])
        planes[name] = {key: value for key, value in result.items() if key not in ('x', 'y', 'chi2', 'delta_chi2')}
    sm.write_json(OUTPUT / 'two_dimensional_results.json', planes)
    polygon_rows = list(csv.DictReader(LAYOUT.path('data/benchmark/fig4_blue_polygons.csv').open(encoding='utf-8')))
    boundary_checks = {}
    for name in planes:
        _, _, x_domain, y_domain = PLANE_SPECS[name]
        selected = [row for row in polygon_rows if row['panel'] == name and min(abs(float(row['x']) - x_domain[0]), abs(float(row['x']) - x_domain[1]), abs(float(row['y']) - y_domain[0]), abs(float(row['y']) - y_domain[1])) > 1e-06]
        values = np.array([profile(evaluate_polynomial(polynomials[name], float(row['x']), float(row['y'])), observed, errors['mean']).chi2 - planes[name]['best_fit']['chi2'] for row in selected])
        boundary_checks[name] = {'non_clipped_vertices': len(selected), 'paper_nominal_delta_chi2': THRESHOLD_2D, 'project_delta_chi2_at_paper_boundary_min': float(values.min()), 'project_delta_chi2_at_paper_boundary_median': float(np.median(values)), 'project_delta_chi2_at_paper_boundary_max': float(values.max())}
    sm.write_json(OUTPUT / 'paper_contour_comparison.json', boundary_checks)
    spectra_rows = []
    spectra_cases = [('SM', {})]
    for coupling, fit in primary.items():
        spectra_cases.append((coupling + '_best', {coupling: fit['best_fit']['epsilon']}))
        for index, (lower, upper) in enumerate(fit['intervals']['1sigma'], 1):
            spectra_cases += [(coupling + f'_1sigma_{index}_lower', {coupling: lower}), (coupling + f'_1sigma_{index}_upper', {coupling: upper})]
    for case_name, coordinates in spectra_cases:
        prediction = kernel.predict(parameters=point(**coordinates))
        for index, value in enumerate(prediction.counts):
            spectra_rows.append({'case': case_name, 'couplings_json': json.dumps(coordinates), 'bin_index': index + 1, 'energy_low_eVee': sm.EDGES[index], 'energy_high_eVee': sm.EDGES[index + 1], 'events_per_bin_1kg_119days': value, **{isotope + '_events': prediction.components['reactor_antinu_e', isotope][index] for isotope in sm.ISOTOPES}, 'provenance_id': 'CONUS_vector_NSI_response_v1'})
    csv_write(OUTPUT / 'nsi_spectra_19bins.csv', spectra_rows)
    summary = {'version': 'NSI_Response_v1_isolated_candidate', 'dataset_id': 'conusplus_kkl_run1', 'created_date': '2026-11-06', 'SM_chi2_profiled': sm_result.chi2, 'SM_alpha_profiled': sm_result.alpha, 'NSI_rows': primary, 'nominal_1D_thresholds': THRESHOLDS, 'nominal_2D_90percent_threshold': THRESHOLD_2D, 'sigma_convention': 'mean of the two delivered digitized error lengths; lower/upper sensitivity also supplied', 'statistic': '2501.17843v3 Eq.(33), existing profile_gaussian_one_pull, Gaussian alpha prior0.169', 'forward': 'existing 4-operator coefficient kernel checked against nonzero direct Slow predictions', 'claim_level': 'approximate', 'human_gate': 'NOT_REVIEWED', 'scientific_provenance_status': 'PARTIAL', 'limitations': ['Inherited SM spectrum discrepancy, user-selected flux and Nuclear Response differ from the paper setup.', 'Low-energy source original numeric table and Ge response original nuclear-computation chain remain unverified.', 'Mean-error convention is an explicit executor choice, with two sensitivity calculations.', 'Nominal delta-chi2 thresholds reproduce the paper comparison convention; coverage near nonregular NSI boundaries was not toy-calibrated.', 'Paper interval endpoints are rounded; blue contours are digitized geometry, without author surface arrays.']}
    sm.write_json(OUTPUT / 'summary.json', summary)
    print('NSI numerical benchmarks and paper comparisons completed', flush=True)
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
