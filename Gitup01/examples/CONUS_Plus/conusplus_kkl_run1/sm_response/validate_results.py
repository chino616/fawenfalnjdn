"""Validate, tabulate and plot repository-local CONUS+ direct Slow predictions."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('sm')
from dataclasses import asdict
import csv
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import quad
from calculate_sm import CONFIG, DATA, EDGES, HERE, ISOTOPES, OUTPUT, POINT, SNAPSHOT, GeLindhardGaussian, build_model, predict, settings, sha256, write_json
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.foundation import constants
from cevns_pyeft.rates.differential import differential_cross_section_nn
from cevns_pyeft.rates.recoil import integrate_recoil_yield
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
from cevns_pyeft.rates.differential import _sm_left_dim6

def csv_write(path, rows):
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def check_normalization_and_response(model):
    response = model.observation
    recoil = np.linspace(0.0, 3.5, 801)
    target = model.targets.isotopes[0]
    probabilities = response.bin_probabilities(target=target, recoil_keV=recoil, binning=model.binning, component_id='reactor_antinu_e')
    maximum_probability_error = 0.0
    for t in (0.02, 0.5, 0.8, 1.1, 1.6):
        mean, sigma = (float(response.mean_eVee(t)), float(response.sigma_eVee(t)))
        numeric = np.array([quad(lambda e: math.exp(-0.5 * ((e - mean) / sigma) ** 2) / (math.sqrt(2 * math.pi) * sigma), low, high, epsabs=1e-14, epsrel=1e-12)[0] for low, high in zip(EDGES[:-1], EDGES[1:])])
        analytic = response.bin_probabilities(target=target, recoil_keV=np.array([t]), binning=model.binning, component_id='reactor_antinu_e').values[0]
        maximum_probability_error = max(maximum_probability_error, float(np.max(abs(numeric - analytic))))
    assert maximum_probability_error < 1e-10
    assert np.all(probabilities.values >= 0)
    assert probabilities.values.sum(axis=1).max() <= 1 + 1e-10
    fluence = model.source.for_run(model.run)
    query = np.linspace(0.0, 10.0, 10001)
    integrated = float(np.trapezoid(fluence.components[0].continuum(query), query))
    expected = CONFIG['flux_total_cm2_s'] * model.run.seconds
    normalization_error = abs(integrated / expected - 1.0)
    assert normalization_error < 1e-06
    outside = fluence.components[0].continuum(np.array([-1.0, 10.01]))
    assert np.array_equal(outside, np.zeros(2))
    return {'max_CDF_vs_independent_bin_quadrature_absolute_error': maximum_probability_error, 'minimum_bin_probability': float(probabilities.values.min()), 'maximum_ROI_probability_row_sum': float(probabilities.values.sum(axis=1).max()), 'full_Gaussian_domain': 'real line; ROI probabilities retain lost tails', 'integrated_fluence_cm_minus2': integrated, 'expected_flux_times_live_seconds_cm_minus2': expected, 'relative_fluence_error': normalization_error, 'outside_source_support_zero': True, 'live_seconds': model.run.seconds}

def check_cross_sections(model):
    rows = []
    sm = _sm_left_dim6(True, POINT.sin2thetaW)
    for target in model.targets.isotopes:
        response = model.interaction._responses[target.isotope_id]
        energy = 6.0
        t = 0.5
        pn = flavor_kernel_onebody_li2026(response, E_nu_GeV=energy * 0.001, ER_keV=t, left_hat=sm, basis='np')
        iso = flavor_kernel_onebody_li2026(response, E_nu_GeV=energy * 0.001, ER_keV=t, left_hat=sm, basis='iso')
        basis_error = float(np.max(abs(pn.kernel - iso.kernel)) / np.max(abs(pn.kernel)))
        assert basis_error < 1e-12
        a = differential_cross_section_nn(response, t, np.array([energy]), rho=np.diag([1.0, 0.0, 0.0]), particle_kind='antinu', include_sm=True, sin2thetaW=POINT.sin2thetaW)
        nu = differential_cross_section_nn(response, t, np.array([energy]), rho=np.diag([1.0, 0.0, 0.0]), particle_kind='nu', include_sm=True, sin2thetaW=POINT.sin2thetaW)
        assert np.array_equal(a.dsigma_cm2_per_keV, nu.dsigma_cm2_per_keV)
        endpoint = model.interaction.kinematics.maximum_recoil_keV(target, energy)
        independent_endpoint = 2 * (energy * 0.001) ** 2 / (target.kinematic_mass_GeV + 2 * energy * 0.001) / 1e-06
        assert abs(endpoint - independent_endpoint) < 1e-12
        inverse = model.interaction.kinematics.minimum_energy_MeV(target, endpoint)
        assert abs(inverse - energy) < 1e-12
        outside = differential_cross_section_nn(response, endpoint * 1.00001, np.array([energy]), rho=np.diag([1.0, 0.0, 0.0]), particle_kind='antinu', include_sm=True, sin2thetaW=POINT.sin2thetaW)
        assert np.all(outside.dsigma_cm2_per_keV == 0)
        at_zero = differential_cross_section_nn(response, 1e-06, np.array([energy]), rho=np.diag([1.0, 0.0, 0.0]), particle_kind='antinu', include_sm=True, sin2thetaW=POINT.sin2thetaW)
        z, n = (response.basic['Z'], response.basic['N'])
        q_w = n - (1 - 4 * POINT.sin2thetaW) * z
        leading = constants.G_F ** 2 * target.kinematic_mass_GeV * q_w ** 2 / (4 * math.pi)
        leading *= constants.GEV_INV2_TO_CM2 * constants.keV
        reference_mass = CONFIG['target_atomic_masses_u'][target.isotope_id] * CONFIG['constants']['atomic_mass_energy_GeV']
        reference_mass -= z * CONFIG['constants']['electron_mass_energy_GeV']
        rows.append({'isotope': target.isotope_id, 'kinematic_mass_GeV_Au': target.kinematic_mass_GeV, 'onboarding_nuclear_mass_GeV_approx': reference_mass, 'mass_relative_difference': target.kinematic_mass_GeV / reference_mass - 1, 'nuclei_at_1kg': target.number_of_nuclei, 'endpoint_at_6MeV_keV': endpoint, 'inverse_energy_MeV': inverse, 'np_vs_isospin_relative_error': basis_error, 'low_recoil_dsigma_vs_pointlike_vector_limit': float(at_zero.dsigma_cm2_per_keV[0] / leading), 'nu_antinu_code_values_identical': True, 'SM_channel_fractions_at_T0_5keV_E6MeV': {key: float(np.real(np.trace(value)) / np.real(np.trace(pn.kernel))) for key, value in pn.pieces.items()}})
    return {'isotopes': rows, 'antineutrino_scope': 'Shared-kernel rate convention in Li et al. 2601.19883v2 PDF p.21 after Eq.(92); code equality is an internal convention check.', 'response_provenance_scope': 'Local tables identified and normalization checked. Original nuclear-computation/conversion chain remains unverified.', 'active_SM_LECs': {name: getattr(DEFAULT_LECS, name) for name in ('L1', 'L2', 'L3', 'L4', 'm_N')}, 'LEC_locator': 'Li et al., arXiv:2601.19883v2, PDF p.8 Table II, for L1-L4; project DEFAULT_LECS.m_N is its explicit local nucleon-mass convention.', 'runtime_constants': {'G_F_GeV_minus2': constants.G_F, 'AMU_GEV': constants.AMU_GEV, 'GEV_INV2_TO_CM2': constants.GEV_INV2_TO_CM2, 'keV_in_GeV': constants.keV}, 'shared_theory_implementation': 'adopted shared theory; current local identity checked in LOCAL_INPUTS.json'}

def check_linear_scaling():
    numerical = settings(9, 17)
    baseline = predict(build_model(), parameters=POINT, numerics=numerical, backend='slow').counts
    record = {}
    for name, overrides in (('flux', {'flux_scale': 2.0}), ('mass', {'mass_scale': 2.0}), ('live_time', {'live_scale': 2.0})):
        doubled = predict(build_model(**overrides), parameters=POINT, numerics=numerical, backend='slow').counts
        error = float(np.max(abs(doubled / (2.0 * baseline) - 1.0)))
        assert error < 1e-12
        record[name + '_doubling_relative_error'] = error
    record['scope'] = 'Normal predict entry point at diagnostic coarse grids, separate from the converged production result.'
    return record

def check_low_true_energy_tail(model):
    cutoff = settings(81, 161).recoil_min_keV
    recoil = np.linspace(1e-06, cutoff, 17)
    component = model.source.for_run(model.run).components[0]
    bins = np.zeros(19)
    for target in model.targets.isotopes:
        spectrum = integrate_recoil_yield(component, target, model.interaction, parameters=POINT, numerics=settings(17, 81), recoil_keV=recoil)
        probability = model.observation.bin_probabilities(target=target, recoil_keV=recoil, binning=model.binning, component_id=component.component_id)
        bins += target.number_of_nuclei * np.trapezoid(spectrum.values_per_keV[:, None] * probability.values, recoil, axis=0)
    assert bins.max() < 0.0001
    return {'paper_true_ionization_min_eVee': 2.96, 'inverse_Lindhard_recoil_min_keV': cutoff, 'diagnostic_lower_recoil_min_keV': 1e-06, 'diagnostic_n_recoil': 17, 'diagnostic_n_enu': 81, 'omitted_low_energy_tail_events_by_bin': bins, 'omitted_low_energy_tail_total_events': float(bins.sum()), 'acceptance': 'absolute omitted contribution below 1e-4 events/bin'}

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    LAYOUT.verify_inputs()
    model = build_model()
    cases = {name: np.load(OUTPUT / (name + '.npz')) for name in ('base', 'energy_refined', 'recoil_refined', 'fine', 'energy_641', 'fine_641')}
    final = cases['fine_641']
    comparisons = {}
    for name, other in (('E_nu_at_fine_recoil', 'fine'), ('recoil_at_fine_E_nu', 'energy_641'), ('both_from_321_energy_grid', 'energy_refined')):
        difference = abs(final['counts'] - cases[other]['counts'])
        relative = difference / np.maximum(final['counts'], 1e-100)
        passed = bool(np.all(difference <= 0.0001 + 0.003 * abs(final['counts'])))
        assert passed, (name, float(relative.max()))
        comparisons[name] = {'reference_case': 'fine_641', 'comparison_case': other, 'max_absolute_difference_events': float(difference.max()), 'max_relative_difference': float(relative.max()), 'passed': passed}
    summed = sum((final['counts_' + isotope] for isotope in ISOTOPES))
    np.testing.assert_allclose(summed, final['counts'], rtol=1e-12, atol=1e-14)
    assert np.all(final['counts'] > 0) and np.all(np.isfinite(final['counts']))
    reference_path = LAYOUT.path('data/benchmark/conusplus_2501_17843v3_fig1_sm_digitized.csv')
    reference = np.genfromtxt(reference_path, names=True, delimiter=',', encoding='utf-8')
    paper = reference['paper_sm_counts_per_kg_per_10eVee']
    observation_path = DATA / 'statistics/conusplus_2501_17843v3_fig1_digitized.csv'
    observed = np.genfromtxt(observation_path, names=True, delimiter=',', encoding='utf-8')
    isotope_totals = {isotope: float(final['counts_' + isotope].sum()) for isotope in ISOTOPES}
    detectors = {}
    for name, mass, days, threshold, paper_total in (('C2', 0.95, 117, 180, 90), ('C3', 0.94, 110, 160, 143), ('C5', 0.94, 119, 170, 113)):
        selected = EDGES[:-1] >= threshold
        total = float(final['counts'][selected].sum() * mass * days / 119.0)
        detectors[name] = {'mass_kg': mass, 'live_days': days, 'threshold_eVee': threshold, 'counts_in_own_window_to_350eVee': total, 'paper_reported_total': paper_total, 'derivation': 'same per-kg per-day spectrum, threshold masks at complete bin edges, mass*days/119'}
    normalizations = json.loads((DATA / 'numerical_checks.json').read_text(encoding='utf-8'))
    signed_reference_ratio = normalizations['normalization_default_MeV'] / normalizations['normalization_literal_reference_MeV']
    rows = []
    for i in range(19):
        rows.append({'bin_index': i + 1, 'energy_low_eVee': EDGES[i], 'energy_high_eVee': EDGES[i + 1], 'energy_center_eVee': (EDGES[i] + EDGES[i + 1]) / 2, 'sm_response_events_per_bin_1kg_119days': final['counts'][i], **{isotope + '_events_per_bin': final['counts_' + isotope][i] for isotope in ISOTOPES}, 'sm_response_counts_per_kg_per_10eVee': final['counts'][i], 'paper_sm_digitized_counts_per_kg_per_10eVee': paper[i], 'response_over_paper_sm': final['counts'][i] / paper[i], 'observed_excess_digitized': observed['excess'][i], 'observed_error_minus': observed['error_minus'][i], 'observed_error_plus': observed['error_plus'][i], 'signed_flux_extrapolation_diagnostic_events': final['counts'][i] * signed_reference_ratio, 'provenance_id': 'conusplus_sm_response_isolated_v1'})
    csv_write(OUTPUT / 'sm_counts_19bins.csv', rows)
    recoil_rows = []
    for target in model.targets.isotopes:
        isotope = target.isotope_id
        recoil = final['recoil_keV_' + isotope]
        probabilities = model.observation.bin_probabilities(target=target, recoil_keV=recoil, binning=model.binning, component_id='reactor_antinu_e')
        means, widths = (model.observation.mean_eVee(recoil), model.observation.sigma_eVee(recoil))
        yields = final['yield_per_nucleus_per_keV_' + isotope] * target.number_of_nuclei
        for t, mean, width, value, probability in zip(recoil, means, widths, yields, probabilities.values.sum(axis=1)):
            recoil_rows.append({'isotope': isotope, 'recoil_keV': t, 'mean_true_ionization_eVee': mean, 'Gaussian_sigma_eVee': width, 'events_per_keV_1kg_119days': value, 'probability_in_160_350eVee_window': probability, 'provenance_id': 'conusplus_sm_response_isolated_v1'})
    csv_write(OUTPUT / 'true_recoil_and_response.csv', recoil_rows)
    print('Checking independent response integrals, cross sections and normalization', flush=True)
    validation = {'source_detector_normalization': check_normalization_and_response(model), 'cross_section_and_target': check_cross_sections(model), 'linear_scaling': check_linear_scaling(), 'low_true_energy_tail': check_low_true_energy_tail(model), 'grid_convergence': comparisons, 'predeclared_tolerance': {'relative': 0.003, 'absolute_events': 0.0001}, 'component_sum': 'PASS', '19_finite_nonnegative_bins': 'PASS', 'observed_negative_values_preserved': int(np.sum(observed['excess'] < 0)), 'fit_executed': False, 'human_gate': 'NOT_REVIEWED'}
    summary = {'calculation': 'SM CEvNS with the existing Li2026 Nuclear Response Slow pipeline', 'dataset_id': 'conusplus_kkl_run1', 'created_date': '2026-11-06', 'prediction_unit': 'events/bin', 'figure_unit': 'counts kg^-1 (10 eVee)^-1', 'mass_kg': 1.0, 'live_days': 119.0, 'exposure_kg_day': 119.0, 'window_eVee': [160.0, 350.0], 'bins': 19, 'bin_width_eVee': 10.0, 'sm_total_events': float(final['counts'].sum()), 'isotope_total_events': isotope_totals, 'paper_digitized_sm_ordinate_sum': float(paper.sum()), 'relative_total_difference_vs_digitized_paper': float(final['counts'].sum() / paper.sum() - 1), 'bin_ratio_min': float(np.min(final['counts'] / paper)), 'bin_ratio_max': float(np.max(final['counts'] / paper)), 'largest_shape_difference': {'bin_index': int(np.argmax(abs(final['counts'] / paper - 1))) + 1, 'relative_difference': float((final['counts'] / paper - 1)[np.argmax(abs(final['counts'] / paper - 1))]), 'absolute_difference_events': float((final['counts'] - paper)[np.argmax(abs(final['counts'] / paper - 1))]), 'interpretation': 'A real shape discrepancy relative to the digitized reference. Its origin is unresolved; total agreement alone does not establish spectrum reproduction.'}, 'derived_individual_detectors': detectors, 'derived_three_detector_sum_events': sum((v['counts_in_own_window_to_350eVee'] for v in detectors.values())), 'paper_reported_three_detector_total': 346, 'signed_reference_flux_diagnostic_total_events': float(final['counts'].sum() * signed_reference_ratio), 'signed_reference_flux_diagnostic': 'Only a derived normalization contrast. All recoil-support energies exceed 0.01 MeV, where the source shapes coincide before normalization. Negative low-end flux is never passed to the physical SourceModel.', 'claim': 'Converged conditional project-model forward prediction with external figure comparison', 'limitations': ['32 low-energy flux nodes traced directly to the supplied note, original Kopeikin numeric table still unverified.', 'Ge Response table identified locally, original nuclear calculation and conversion chain still unverified.', 'Kinematic mass uses existing engine A*u, while NIST atomic masses determine nuclei per kg.', 'Shared neutrino/antineutrino rate-kernel convention follows Li et al. PDF p.21; a helicity-specific theory audit is outside the tested scope.', 'The external paper uses Klein-Nystrand nuclear form factors, this calculation uses project Nuclear Response and the user-selected flux construction.', 'Spectrum shape differs from the paper reference, especially in the small high-energy tail. The discrepancy remains to be traced with author numerical spectra or code.', "SM electron scattering is omitted under the benchmark's O(0.1) event approximation, PDF p.10.", 'Individual-detector comparison is limited to reconstructed energies up to 350 eVee.', 'All output result-acceptance states remain NOT_REVIEWED.']}
    write_json(OUTPUT / 'validation.json', validation)
    write_json(OUTPUT / 'summary.json', summary)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
    fig, (ax, ratio_ax) = plt.subplots(2, 1, figsize=(9.2, 7.4), sharex=True, gridspec_kw={'height_ratios': [3.3, 1.0], 'hspace': 0.07})
    centers = (EDGES[:-1] + EDGES[1:]) / 2
    ax.errorbar(centers, observed['excess'], yerr=np.vstack((observed['error_minus'], observed['error_plus'])), fmt='o', color='#32383f', ms=4.8, capsize=2.5, elinewidth=1.05, label='CONUS+ excess (digitized Fig. 1)', zorder=3)
    ax.stairs(final['counts'], EDGES, color='#cf5338', linewidth=2.1, label='SM Nuclear Response | project Slow')
    ax.plot(centers, paper, color='#286ea6', linestyle='--', linewidth=1.65, label='Paper SM (digitized blue histogram)')
    ax.axhline(0, color='#8e969e', linewidth=0.8)
    ax.set_ylabel('Counts kg$^{-1}$ (10 eVee)$^{-1}$')
    ax.set_title('CONUS+ Standard Model event spectrum', loc='left', fontsize=16, fontweight='bold', pad=38)
    ax.text(0, 1.035, 'Natural Ge | 1 kg effective detector | 119 kg day | 160-350 eVee', transform=ax.transAxes, fontsize=10.5, color='#4a5662')
    ax.legend(loc='upper right', fontsize=9.5, frameon=False)
    ax.grid(axis='y', alpha=0.16)
    text = f"SM Response total  {summary['sm_total_events']:.2f}\nPaper SM ordinate sum  {paper.sum():.2f}"
    ax.text(0.97, 0.8, text, transform=ax.transAxes, ha='right', va='top', fontsize=10, bbox={'facecolor': '#f3f5f7', 'edgecolor': 'none', 'pad': 9})
    ratio_ax.axhline(1, color='#7c8792', linestyle='--', linewidth=1)
    ratio_ax.plot(centers, final['counts'] / paper, 'o-', color='#cf5338', ms=4, linewidth=1.35)
    ratio_ax.set_ylabel('Response /\npaper SM', fontsize=10)
    ratio_ax.set_xlabel('Reconstructed ionization energy [eVee]')
    ratio_ax.grid(alpha=0.17)
    ratio_ax.set_xlim(158, 352)
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.16, top=0.85)
    fig.text(0.12, 0.06, 'Benchmark: De Romeri et al., Phys. Rev. D 111, 075025 (2025), arXiv:2501.17843v3, Fig. 1.\nConditional project prediction. Flux and nuclear-table provenance limits are listed in the source report.', fontsize=8.4, color='#56616b', linespacing=1.5)
    fig.savefig(OUTPUT / 'conusplus_sm_event_spectrum.png', dpi=220, facecolor='white')
    fig.savefig(OUTPUT / 'conusplus_sm_event_spectrum.svg', facecolor='white')
    plt.close(fig)
    write_json(OUTPUT / 'OUTPUT_PROVENANCE.json', {'provenance_id': 'conusplus_sm_response_isolated_v1', 'created_date': '2026-11-06', 'source_map': '../snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json', 'source_register': '../snapshot/workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P00_SOURCE_REGISTER.yaml', 'input_fingerprints': '../review/INPUT_SNAPSHOT.json', 'columns': [{'files': ['sm_counts_19bins.csv', 'true_recoil_and_response.csv'], 'columns': 'all SM prediction/isotope/recoil/response columns', 'direct_inputs': ['input_choices.json', 'reactor_flux_default.csv', 'responses_all.json'], 'derivation': 'calculate_sm.py, existing core.predict -> integrate_recoil_yield -> Li2026LegacyInteraction -> probability_fold; see fine_641.json for actual grid, exposure and nuclei.', 'source_locator': '2501.17843v3 Eqs.(26),(29)-(32) for detector folding; 2601.19883v2 Table II and Eqs.(75)-(78) for theoretical framework; exact executable formula is the fingerprinted local implementation.', 'status': 'PROJECT_DERIVED; upstream flux numeric-table and Response conversion provenance remain partial'}, {'file': 'sm_counts_19bins.csv', 'columns': ['paper_sm_digitized_counts_per_kg_per_10eVee'], 'direct_input': '../data/benchmark/conusplus_2501_17843v3_fig1_sm_digitized.csv', 'source_locator': '2501.17843v3 PDF p.10 Fig.1 blue theoretical histogram', 'status': 'FIGURE_DIGITIZED'}, {'file': 'sm_counts_19bins.csv', 'columns': ['observed_excess_digitized', 'observed_error_minus', 'observed_error_plus'], 'direct_input': '../snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/statistics/conusplus_2501_17843v3_fig1_digitized.csv', 'source_locator': '2501.17843v3 PDF p.10 Fig.1 black markers and error bars, retained signed excess', 'status': 'FIGURE_DIGITIZED'}, {'file': 'sm_counts_19bins.csv', 'columns': ['response_over_paper_sm'], 'derivation': 'same-row SM prediction divided by digitized paper SM, without fitted rescaling', 'status': 'PROJECT_DERIVED'}, {'file': 'sm_counts_19bins.csv', 'columns': ['signed_flux_extrapolation_diagnostic_events'], 'derivation': 'default counts times N_default/N_literal from numerical_checks.json; source shapes are identical above 0.01 MeV before normalization', 'status': 'PROJECT_DERIVED_DIAGNOSTIC'}, {'file': 'sm_counts_19bins.csv', 'columns': ['bin_index', 'energy_low_eVee', 'energy_high_eVee', 'energy_center_eVee'], 'derivation': '19 bins, edges160..350 step10, centres=edge midpoint; retained observation-grid definition', 'source_locator': '2501.17843v3 PDF pp.9-10, 19-bin definition and Fig.1', 'status': 'PROJECT_DERIVED'}], 'software': {'calculate_sm.py': sha256(LAYOUT.path('calculate_sm.py')), 'validate_results.py': sha256(LAYOUT.path('validate_results.py')), 'extract_sm_reference.py': sha256(LAYOUT.path('extract_sm_reference.py'))}, 'files': {p.name: {'sha256': sha256(p)} for p in sorted(OUTPUT.iterdir()) if p.is_file() and p.name != 'OUTPUT_PROVENANCE.json'}, 'human_gate': 'NOT_REVIEWED'})
    print(json.dumps({'total_events': summary['sm_total_events'], 'total_difference_vs_paper': summary['relative_total_difference_vs_digitized_paper'], 'grid_checks': comparisons}, ensure_ascii=False), flush=True)
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
