"""Audit the requested CsI inputs using the existing Response/time interfaces.

Run from Gitup01 with --output-dir and optionally --signal. Scientific blocked
items are recorded separately from executable consistency checks.
"""
from pathlib import Path
from importlib import import_module
import argparse
import csv
import hashlib
import inspect
import json
import sys
import time
from unittest.mock import patch

import numpy as np

PACKAGE = Path(__file__).resolve().parents[1]
PROJECT = PACKAGE.parents[4]
sys.path.insert(0, str(PROJECT / 'src'))
PREFIX = 'cevns_pyeft.experiments.coherent.2021CsI_root_time'
A = import_module(PREFIX + '.analysis_inputs')
D = import_module(PREFIX + '.statistics.datasets')
L = import_module(PREFIX + '.statistics.likelihoods')
B = import_module(PREFIX + '.kernels.builder')
T = import_module(PREFIX + '.time_acceptance')
SOURCE = import_module(PREFIX + '.2021CsI_root_time')
ROOT = import_module(PREFIX + '.root_data')
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import _rate_per_kg, _trapz_weights
from cevns_pyeft.rates.differential import differential_cross_section_nn, p_smearing_csi
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS, sns_component_state
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import efficiency
from cevns_pyeft.foundation import constants
from cevns_pyeft.theory.kinematics import minimum_neutrino_energy_GeV


def verified_sm_cross_section(response, recoil, energies, component, wc_triplets=None):
    """Evaluate the native vector kernel through a checked quadratic in E²*dσ/dT.

    Five direct Response probes validate three interpolation coefficients for
    every recoil/state. A failed check evaluates the full native energy array.
    """
    energies = np.asarray(energies, dtype=float)
    minimum = minimum_neutrino_energy_GeV(recoil * 1e-6,
        int(response.basic['A']) * constants.AMU_GEV) * 1000.
    allowed = energies >= minimum
    result = np.zeros_like(energies)
    if not np.any(allowed):
        return result
    selected = energies[allowed]
    maximum = float(selected.max())
    def direct(points):
        return np.asarray(differential_cross_section_nn(response, float(recoil), points,
            rho=sns_component_state(component), wc_triplets=dict(wc_triplets or {}), include_sm=True,
            sin2thetaW=.2387, c10_mass_mode='quark_mass_resolved').dsigma_cm2_per_keV)
    if selected.size == 1 or maximum - minimum < 1e-8:
        result[allowed] = direct(selected)
        return result
    probes = minimum + (maximum - minimum) * np.array([.10, .31, .52, .73, .94])
    measured = direct(probes)
    scale = max(float(np.max(np.abs(measured * probes ** 2))), 1e-300)
    coefficients = np.polynomial.polynomial.polyfit(probes[[0, 2, 4]] / maximum,
        measured[[0, 2, 4]] * probes[[0, 2, 4]] ** 2 / scale, 2)
    checked = np.polynomial.polynomial.polyval(probes / maximum, coefficients) * scale / probes ** 2
    if not np.allclose(checked, measured, rtol=2e-10, atol=2e-12 * float(np.max(np.abs(measured)))):
        result[allowed] = direct(selected)
        return result
    result[allowed] = np.polynomial.polynomial.polyval(selected / maximum, coefficients) * scale / selected ** 2
    return result


def native_sm_rate(response, flux, recoil, component, n_enu, wc_triplets=None):
    """Use the existing SNS grid, endpoint mask, prompt line and trapezoid rule."""
    energy = np.linspace(0., import_module('cevns_pyeft.rates.differential').emax_muon_dar_mev(), n_enu)
    output = np.zeros_like(recoil)
    line_energy, line_weight = flux['measured']['muLine']
    for index, value in enumerate(recoil):
        minimum = minimum_neutrino_energy_GeV(value * 1e-6,
            int(response.basic['A']) * constants.AMU_GEV) * 1000.
        selected = energy[energy >= minimum]
        if component != 'mu' and len(selected) >= 2:
            cross_section = verified_sm_cross_section(response, value, selected, component, wc_triplets)
            output[index] = _trapz_weights(selected) @ (cross_section * flux['measured'][component](selected))
        if component == 'mu' and line_energy >= minimum:
            output[index] = line_weight * verified_sm_cross_section(response, value, np.array([line_energy]), component, wc_triplets)[0]
    return output / (int(response.basic['A']) * 1.6605390666e-27)


def audited_rate_per_kg(response, flux, recoil, component, wc_triplets, include_sm,
                        sin2thetaW, c10_mass_mode, n_enu, *, source_state):
    """Bound the audit acceleration to the native vector settings checked here."""
    if not include_sm or sin2thetaW != .2387 or c10_mass_mode != 'quark_mass_resolved':
        raise ValueError('Audit acceleration supports only the declared vector benchmark settings')
    return native_sm_rate(response, flux, recoil, component, n_enu, wc_triplets)


def rate_evaluator_sha256():
    code = '\n'.join(inspect.getsource(function) for function in
        [verified_sm_cross_section, native_sm_rate, audited_rate_per_kg])
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_bins(path, columns, arrays):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['PE_bin', 'time_bin', 'PE_lo', 'PE_hi', 'time_lo_us', 'time_hi_us', *columns])
        for i in range(9):
            for j in range(11):
                writer.writerow([i, j, A.PE_EDGES[i], A.PE_EDGES[i + 1],
                                 A.TIME_EDGES[j], A.TIME_EDGES[j + 1],
                                 *[float(array[i, j]) for array in arrays]])


def background_audit():
    records = {}
    for component, prior in [('brn', 18.4), ('nin', 5.6)]:
        pe = np.loadtxt(PACKAGE / 'data/raw' / (component + 'PE.txt'))
        timing = np.loadtxt(PACKAGE / 'data/raw' / (component + 'Trec.txt'))
        edges = np.r_[timing[:, 0] - .005, timing[-1, 0] + .005]
        cdf = T.TimeMassCDF(timing[:, 1], edges)
        pe_total = float(pe[:, 1].sum())
        pe_roi = float(pe[(pe[:, 0] >= 0) & (pe[:, 0] < 60), 1].sum())
        mask = (timing[:, 0] >= 0) & (timing[:, 0] < 6)
        before = float(timing[mask, 1].sum()) * pe_roi / pe_total
        after = float(cdf.integral([0, 6]).sum()) * pe_roi / pe_total
        raw = float(cdf.integral([0, 6]).sum()) * pe_roi
        records[component] = dict(
            published_prior=prior, full_PE_table_sum=pe_total, ROI_PE_table_sum=pe_roi,
            full_time_table_events=float(timing[:, 1].sum()),
            ROI_time_table_events_before_time_efficiency=float(timing[mask, 1].sum()),
            ROI_time_table_events_after_time_efficiency=float(cdf.integral([0, 6]).sum()),
            full_PE_support=[float(pe[0, 0] - .5), float(pe[-1, 0] + .5)],
            full_time_support_us=edges[[0, -1]].tolist(),
            mean_ROI_time_efficiency=float(cdf.integral([0, 6]).sum() / timing[mask, 1].sum()),
            full_probability_ROI_fraction=pe_roi / pe_total,
            legacy_raw_product_after_time_efficiency=raw,
            probability_normalized_before_time_efficiency=before,
            probability_normalized_after_time_efficiency=after,
            before_efficiency_rounds_to_published_prior=round(before, 1) == prior,
            after_efficiency_difference_from_prior=after - prior,
            extra_exposure_factor=1., energy_efficiency_applied_again=False,
            target_rescaling_applied=False,
            conclusion='BLOCKED_POST_TIME_EFFICIENCY_CONVENTION',
            algebraic_cause='Full-support PE probability normalization removes the large excess factor',
            physical_interpretation_status='CANDIDATE: released PE tables sum to one in PE0--60, not over their full support',
            remaining_cause='The full-support normalization candidate matches Table I before time efficiency after rounding. Supplement instructions require time efficiency. The release does not close this convention.',
            sources=['https://arxiv.org/abs/2110.07730v2',
                     'https://arxiv.org/src/2110.07730v2/anc/' + component + 'PE.txt',
                     'https://arxiv.org/src/2110.07730v2/anc/' + component + 'Trec.txt',
                     'Official Supplement p2 lines60-75 and p7 TableI'])
    dataset = D.load_time_dataset()
    records['SS'] = dict(control_events_0_12_us=dataset.metadata['control_events_0_12_us'],
        decay_constant_per_us=.0494, accepted_events_0_6_us=float(dataset.ssb.sum()),
        published_prior=1286., prior_consistency='PASS_ROUNDING',
        source='https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf',
        locator='p2 lines55--59 and p7 TableI')
    records['status'] = 'BLOCKED_POST_TIME_EFFICIENCY_CONVENTION'
    return records


def time_audit():
    source = SOURCE.load_sns_source_with_time()
    checks = []
    for shift in [-.25, 0., .25]:
        full = T.build_time_weights(source.time_source, A.TIME_EDGES,
            efficiency=T.CsITimeEfficiency(), shift_us=shift,
            template_normalization='full_support', energy_fluence_scope='full_support')
        reference = T.build_time_weights(source.time_source, A.TIME_EDGES,
            efficiency=T.CsITimeEfficiency(), shift_us=shift, reference_window_us=[0, 6],
            template_normalization='reference_window', energy_fluence_scope='full_support')
        error = float(np.max(np.abs(full.effective_weights - reference.effective_weights)))
        np.testing.assert_allclose(full.effective_weights, reference.effective_weights, rtol=3e-15, atol=3e-17)
        checks.append(dict(shift_us=shift, effective_weight_max_error=error,
            reference_fractions=reference.reference_fractions.tolist(),
            reference_shape_integrals=reference.shape_weights.sum(axis=1).tolist()))
    return dict(status='PASS_IMPLEMENTED_CONVENTION', checks=checks,
        positive_shift='Source delayed relative to fixed observer windows and efficiency',
        denominator='Nominal zero-shift reference fraction remains fixed for every shift',
        paper_2211='Reference-window shape on 0--6 us with explicit fluence conversion',
        paper_2211_unspecified='Paper does not fully state its shifted-denominator implementation',
        source='https://arxiv.org/html/2211.11905v2', locator='Sec3.1 Eq32 and p13 footnote8')


def static_audit(output):
    dataset = D.load_time_dataset()
    bins = dict(status='FROZEN_RECONSTRUCTED_INPUT', pe_edges=A.PE_EDGES.tolist(),
        time_edges_us=A.TIME_EDGES.tolist(), axis_order=['PE', 'time'],
        endpoint_rule='Left closed, right open, including the last upper edge exclusion',
        pe_provenance='PROJECT_DERIVED from official Supplement Fig2 error-bar endpoints',
        time_provenance='SOURCE_EXTRACTED from 2211.11905v2 Fig18 panel labels',
        PE_numeric_official_table_found=False, raw_C_count=int(dataset.observed.sum()),
        raw_AC_count=int(dataset.control.sum()), energy_projection=dataset.observed.sum(axis=1).tolist(),
        sources=['https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf',
                 'https://arxiv.org/pdf/2211.11905v2'])
    synthetic = np.array([[0., 0.], [8., .125], [60., 0.], [8., 6.], [-1., 0.]])
    histogram = D.histogram_events(synthetic)
    assert histogram.sum() == 2 and histogram[0, 0] == 1 and histogram[1, 1] == 1
    bins['edge_event_check'] = 'PASS'
    for recoil in [-1., 0., 1.999, 70.001, 300.]:
        try:
            A.calibrated_scintillation_response(recoil)
        except ValueError:
            continue
        raise AssertionError('QF accepted an out-of-domain recoil')
    checked = np.linspace(2., 70., 2001)
    values = A.calibrated_scintillation_response(checked)
    qf = dict(status='PASS_DOMAIN_ENFORCED', fit_domain_keV=[2., 70.],
        fit_domain_MeV=[.002, .070], measured_point_span_keV=[3., 63.],
        coefficients=[.0554628, 4.30681, -111.707, 840.384],
        monotonic_positive_in_domain=bool(np.all(np.diff(values) > 0) and np.all(values > 0)),
        out_of_domain_behavior='ValueError in calibrated response and smearing',
        source='https://arxiv.org/html/2111.02477v2', locator='Sec8 Fitting approach and Eq8.1',
        prediction_policy='Time Slow/Fast integrate from 2 keV; source-dependent support above70keV blocks the calibrated prediction')
    write_bins(output / 'raw_observations.csv', ['C_raw', 'AC_raw', 'SS_model'],
               [dataset.observed, dataset.control, dataset.ssb])
    return dict(PE_binning=bins, time_normalization=time_audit(),
                neutron_background=background_audit(), QF=qf,
                nuclear_structure=dict(status='USER_SELECTED_RESPONSE',
                    backend='Native ResponseDB + differential_cross_section_nn',
                    resource=str(PROJECT / 'data/responses/responses_all.json'),
                    sha256=hashlib.sha256((PROJECT / 'data/responses/responses_all.json').read_bytes()).hexdigest(),
                    paper_nuclear_equivalence='Separate acceptance required for the Helm and KN reference papers'))


def response_kernel(n_er, n_enu, n_pe, pe_step):
    """Run the original quadratic builder with a locally checked rate evaluator."""
    with patch.object(B, '_rate_per_kg', audited_rate_per_kg):
        kernel = B.build_time_kernel(n_er=n_er, n_enu=n_enu, n_pe_bin=n_pe, pe_step=pe_step)
    kernel.metadata.update(qf_domain_keV=list(A.QF_DOMAIN_KEV),
        audit_rate_evaluator='Checked native vector E^2*dSigma quadratic; full native fallback',
        audit_evaluator_sha256=rate_evaluator_sha256(),
        audit_script_sha256_at_build=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(dict(event='RESPONSE_grid_completed', **kernel.metadata['integration'],
        seconds=kernel.metadata['build_seconds'])), flush=True)
    return kernel


def precision_points():
    previous = json.loads((PACKAGE / 'benchmarks/results_fine/benchmark_points.json').read_text(encoding='utf-8'))
    points = [(row['name'], row['point']) for row in previous]
    points.extend((f'domain_corner_{i}', [ee, mm]) for i, (ee, mm) in enumerate(
        [(ee, mm) for ee in [-.4, .8] for mm in [-.4, .8]]))
    return points


def grid_predictions(kernel):
    fast = import_module(PREFIX + '.fast_counts_csi2021_time').fast_counts_csi2021_time
    cases = []
    predictions = []
    for name, point in precision_points():
        for shift in [-.25, 0., .25]:
            for efficiency_shift in [-1., 0., 1.]:
                cases.append(dict(name=name, point=point, shift_us=shift, efficiency_shift_pe=efficiency_shift))
                predictions.append(fast(kernel, *point, shift_us=shift,
                    efficiency_shift_pe=efficiency_shift).counts_2d)
    return cases, np.array(predictions)


def refine_signal(output, max_level):
    previous = None
    records = []
    selected = None
    for level in range(max_level + 1):
        n_er, n_enu = 128 * 2 ** level, 240 * 2 ** level
        n_pe = 64 * 2 ** min(level, 2)
        pe_step = .25 / 2 ** min(level, 3)
        kernel = response_kernel(n_er, n_enu, n_pe, pe_step)
        cases, predictions = grid_predictions(kernel)
        signal = import_module(PREFIX + '.fast_counts_csi2021_time').fast_counts_csi2021_time(kernel).counts_2d
        cache = output / f'RESPONSE_er{n_er}_enu{n_enu}.npz'
        kernel.save(cache)
        row = dict(level=level, grid=kernel.metadata['integration'], total_events=float(signal.sum()), cache=cache.name)
        if previous is not None:
            difference = predictions - previous
            row['max_bin_absolute_change'] = float(np.max(np.abs(difference)))
            row['sum_absolute_change'] = float(np.abs(difference).sum())
            row['passed_0p005'] = row['max_bin_absolute_change'] < .005
            worst = np.unravel_index(np.argmax(np.abs(difference)), difference.shape)
            row['worst_case'] = dict(**cases[worst[0]], PE_bin=int(worst[1]), time_bin=int(worst[2]))
            write_bins(output / 'signal_grid_changes.csv', ['previous', 'refined', 'difference'],
                       [previous[worst[0]], predictions[worst[0]], difference[worst[0]]])
            np.savez_compressed(output / 'signal_grid_cases.npz',
                previous=previous, refined=predictions, differences=difference,
                cases_json=np.array(json.dumps(cases)))
        records.append(row)
        write_json(output / 'signal_convergence.json', dict(threshold_events=.005, records=records,
            status='PASS_DECLARED_GRID_CASES' if row.get('passed_0p005') else 'REFINING',
            scope='Legacy eight benchmark points and four domain corners, 3 timing x 3 efficiency shifts, 99 bins; calibrated recoil domain',
            case_count=len(cases)))
        selected = kernel
        if row.get('passed_0p005') and level >= 2:
            result = json.loads((output / 'signal_convergence.json').read_text(encoding='utf-8'))
            return kernel, result
        previous = predictions
    return selected, dict(status='BLOCKED_GRID_TOLERANCE', threshold_events=.005, records=records)


def root_time_bin_weights(edges_us, shift):
    lo = np.maximum(edges_us[:-1][None, :] + shift, A.TIME_EDGES[:-1, None])
    hi = np.minimum(edges_us[1:][None, :] + shift, A.TIME_EDGES[1:, None])
    hi = np.maximum(hi, lo)
    return T.CsITimeEfficiency().integral(lo, hi) / np.diff(edges_us)[None, :]


def root_correlation_audit(output, n_er=256, n_energy=2, n_pe=32):
    """Isolate correlation using identical ROOT energy and time marginals."""
    started = time.perf_counter()
    database = ResponseDB(PROJECT / 'data/responses/responses_all.json')
    flux = loadNeutrinoEmpiricalFluxSNS('CsI2021')
    output.mkdir(parents=True, exist_ok=True)
    energy_nodes, energy_weights = np.polynomial.legendre.leggauss(n_energy)
    pe_nodes, pe_weights = np.polynomial.legendre.leggauss(n_pe)
    pe_points = np.array([.5 * (lo + hi) + .5 * (hi - lo) * pe_nodes
                         for lo, hi in zip(A.PE_EDGES[:-1], A.PE_EDGES[1:])])
    pe_quad = np.array([.5 * (hi - lo) * pe_weights
                       for lo, hi in zip(A.PE_EDGES[:-1], A.PE_EDGES[1:])])
    transfer = np.zeros((3, 9, 600))
    energy_edges = np.arange(601.)
    energies = (.5 * (energy_edges[:-1] + energy_edges[1:]))[:, None] + .5 * energy_nodes
    for target_index, target in enumerate(['Cs133', 'I']):
        response = database.get(target)
        # This comparison is explicitly restricted to the validated QF interval.
        recoil = np.linspace(2., 70., n_er)
        recoil_quad = _trapz_weights(recoil)
        accepted_pe = np.array([(A.calibrated_smearing(pe_points, float(t)) * efficiency(pe_points) * pe_quad).sum(axis=1)
                                for t in recoil])
        nuclei = flux['basic']['detectorMassKg'] * B.MASS_FRACTIONS[target_index] / (int(response.basic['A']) * 1.6605390666e-27)
        for source_index, component in enumerate(B.COMPONENTS):
            cross_sections = np.array([verified_sm_cross_section(response, float(t), energies.ravel(), component)
                                       for t in recoil])
            energy_average = (cross_sections.reshape(n_er, 600, n_energy) * (.5 * energy_weights)[None, None, :]).sum(axis=2)
            transfer[source_index] += nuclei * (accepted_pe * recoil_quad[:, None]).T @ energy_average
    fluence = float(flux['measured']['muLine'][1])
    records = []
    all_joint = np.zeros((9, 11))
    all_factorized = np.zeros((9, 11))
    for source_index, component in enumerate(B.COMPONENTS):
        histogram = ROOT.load_root_histogram(component)
        weights = np.asarray(histogram.weights, dtype=float)
        energy_mass = weights.sum(axis=0)
        time_mass = weights.sum(axis=1)
        total = float(time_mass.sum())
        integration = root_time_bin_weights(histogram.time_edges_us, 0.)
        joint_mass = integration @ weights / total
        factorized_mass = np.outer(integration @ time_mass / total, energy_mass / total)
        joint = fluence * transfer[source_index] @ joint_mass.T
        factorized = fluence * transfer[source_index] @ factorized_mass.T
        difference = joint - factorized
        write_bins(output / f'ROOT_correlation_{component}.csv', ['joint_events', 'factorized_same_marginals_events', 'difference_events'],
                   [joint, factorized, difference])
        records.append(dict(component=component, joint_total=float(joint.sum()), factorized_total=float(factorized.sum()),
            max_bin_absolute_difference=float(np.max(np.abs(difference))), sum_absolute_difference=float(np.abs(difference).sum()),
            ROOT_energy_ge60_fraction=float(energy_mass[60:].sum() / total),
            recoil_domain_keV=[2.,70.], energy_bin_interpolation=f'uniform within original 1 MeV bins, {n_energy}-point Gauss quadrature'))
        all_joint += joint
        all_factorized += factorized
    difference = all_joint - all_factorized
    write_bins(output / 'ROOT_correlation_total.csv', ['joint_events', 'factorized_same_marginals_events', 'difference_events'],
               [all_joint, all_factorized, difference])
    result = dict(status='QUANTIFIED_QF_DOMAIN_LIMITED', records=records,
        grid=dict(n_er=n_er, n_energy_bin=n_energy, n_pe_bin=n_pe),
        max_total_bin_absolute_difference=float(np.max(np.abs(difference))),
        total_joint=float(all_joint.sum()), total_factorized=float(all_factorized.sum()),
        seconds=time.perf_counter() - started,
        comparison_scope='Same ROOT energy marginals and normalization, changes only joint versus factorized time-energy distribution',
        selected_paper_representation='Per-flavor factorized DAR energy spectra and timing, per2211 Eq32 and2202 analysis text',
        full_ROOT_source_acceptance='BLOCKED: additional high-energy tails require a source-model decision and recoil response beyond the calibrated domain',
        numerical_scope='Calibrated recoil interval and declared uniform within-bin ROOT energy interpolation',
        original_url='https://arxiv.org/src/2110.07730v2/anc/snsFlux2D.root')
    write_json(output / 'ROOT_correlation.json', result)
    return result


def refine_root_correlation(output):
    previous = None
    records = []
    for level in range(5):
        folder = output / f'ROOT_grid_{level}'
        result = root_correlation_audit(folder, 256 * 2 ** level, 2 * 2 ** level, min(32 * 2 ** level, 128))
        table = np.genfromtxt(folder / 'ROOT_correlation_total.csv', delimiter=',', names=True)
        current = np.array([table['joint_events'], table['factorized_same_marginals_events']])
        row = dict(level=level, grid=result['grid'], max_correlation_events=result['max_total_bin_absolute_difference'])
        if previous is not None:
            row['max_prediction_grid_change'] = float(np.max(np.abs(current - previous)))
            row['passed_0p005'] = row['max_prediction_grid_change'] < .005
        records.append(row)
        if row.get('passed_0p005') and level >= 2:
            break
        previous = current
    for name in ['mu', 'e', 'mub', 'total']:
        (output / f'ROOT_correlation_{name}.csv').write_bytes((folder / f'ROOT_correlation_{name}.csv').read_bytes())
    result['convergence'] = dict(status='PASS_DECLARED_GRID_DIFFERENCE' if row.get('passed_0p005') else 'BLOCKED_GRID_TOLERANCE',
        threshold_events=.005, records=records)
    if not row.get('passed_0p005'):
        result['status'] = 'BLOCKED_ROOT_DIAGNOSTIC_PRECISION'
    write_json(output / 'ROOT_correlation.json', result)
    return result


def qf_extrapolation_audit(output, kernel):
    """Quantify the omitted old 0.1--2 keV region using a labelled extrapolation."""
    database = ResponseDB(PROJECT / 'data/responses/responses_all.json')
    flux = loadNeutrinoEmpiricalFluxSNS('CsI2021')
    step = kernel.metadata['integration']['pe_step']
    pe_grid = np.arange(0, 60 + step / 2, step)
    selection = kernel.pe_quadrature * efficiency(kernel.pe_nodes)
    timing = np.array([cdf.integral(A.TIME_EDGES) for cdf in kernel.time_cdfs])
    records = []
    previous = None
    for n_recoil in [256, 512]:
        recoil = np.linspace(.1, 2., n_recoil)
        recoil_weights = _trapz_weights(recoil)
        energy = np.zeros((3, 9))
        # This is the historical polynomial extrapolation, outside the guarded API.
        smearing = np.array([p_smearing_csi(pe_grid, float(t)) for t in recoil])
        for target_index, target in enumerate(['Cs133', 'I']):
            response = database.get(target)
            for source_index, component in enumerate(B.COMPONENTS):
                rate = native_sm_rate(response, flux, recoil, component, 960)
                spectrum = (rate * recoil_weights) @ smearing
                nodes = np.array([np.interp(node, pe_grid, spectrum) for node in kernel.pe_nodes])
                energy[source_index] += (nodes * selection).sum(axis=1) * flux['basic']['detectorMassKg'] * B.MASS_FRACTIONS[target_index]
        prediction = np.einsum('fi,fj->ij', energy, timing)
        row = dict(n_er=n_recoil, n_enu=960, total_events=float(prediction.sum()),
            max_bin_events=float(prediction.max()))
        if previous is not None:
            row['max_grid_change_events'] = float(np.max(np.abs(prediction - previous)))
        previous = prediction
        records.append(row)
    write_bins(output / 'QF_omitted_low_recoil.csv', ['extrapolated_0p1_to_2_keV_events'], [prediction])
    result = dict(status='QUANTIFIED_EXTRAPOLATION_DIAGNOSTIC',
        recoil_interval_keV=[.1, 2.], records=records,
        interpretation='Model-dependent omitted contribution, not a calibrated estimate or an error bound',
        production_policy='The time Slow/Fast entries integrate from2keV and reject out-of-domain response evaluations',
        source='https://arxiv.org/html/2111.02477v2#S8')
    write_json(output / 'QF_extrapolation.json', result)
    return result


def source_model_comparison(output, kernel):
    """Compare the ROOT joint source with the actual legacy DAR calculation."""
    fast = import_module(PREFIX + '.fast_counts_csi2021_time').fast_counts_csi2021_time
    legacy = fast(kernel).component_counts
    records = []
    columns = ['ROOT_joint_events', 'ROOT_factorized_events', 'legacy_DAR_factorized_events',
               'correlation_difference', 'energy_model_difference', 'total_difference']
    joint_total = np.zeros((9, 11))
    factorized_total = np.zeros((9, 11))
    flux = loadNeutrinoEmpiricalFluxSNS('CsI2021')
    exact_flux = loadNeutrinoEmpiricalFluxSNS('CsI2021', use_interpolation=False)
    energy = np.linspace(0., import_module('cevns_pyeft.rates.differential').emax_muon_dar_mev(), 20001)
    for index, component in enumerate(B.COMPONENTS):
        table = np.genfromtxt(output / f'ROOT_correlation_{component}.csv', delimiter=',', names=True)
        joint = table['joint_events'].reshape(9, 11)
        factorized = table['factorized_same_marginals_events'].reshape(9, 11)
        correlation_difference = joint - factorized
        energy_difference = factorized - legacy[index]
        total_difference = joint - legacy[index]
        write_bins(output / f'ROOT_vs_legacy_{component}.csv', columns,
            [joint, factorized, legacy[index], correlation_difference, energy_difference, total_difference])
        histogram = ROOT.load_root_histogram(component)
        centers = .5 * (histogram.energy_edges_MeV[:-1] + histogram.energy_edges_MeV[1:])
        masses = histogram.energy_marginal
        peak = int(np.argmax(masses))
        row = dict(component=component, ROOT_joint_events=float(joint.sum()),
            ROOT_factorized_events=float(factorized.sum()), legacy_DAR_events=float(legacy[index].sum()),
            max_bin_correlation_difference=float(np.max(np.abs(correlation_difference))),
            max_bin_energy_model_difference=float(np.max(np.abs(energy_difference))),
            max_bin_total_difference=float(np.max(np.abs(total_difference))),
            ROOT_mean_energy_MeV=float(centers @ masses / masses.sum()),
            ROOT_peak_energy_bin_MeV=histogram.energy_edges_MeV[peak:peak + 2].tolist())
        if component == 'mu':
            row['legacy_DAR_line_MeV'] = float(flux['measured']['muLine'][0])
        else:
            for label, source in [('legacy_interpolated', flux), ('analytic_Michel', exact_flux)]:
                density = source['measured'][component](energy)
                integral = _trapz_weights(energy) @ density
                row[label + '_mass_in_DAR_support'] = float(integral / flux['measured']['muLine'][1])
                row[label + '_mean_energy_MeV'] = float(_trapz_weights(energy) @ (energy * density) / integral)
        records.append(row)
        joint_total += joint
        factorized_total += factorized
    dar_total = legacy.sum(axis=0)
    correlation_difference = joint_total - factorized_total
    energy_difference = factorized_total - dar_total
    total_difference = joint_total - dar_total
    write_bins(output / 'ROOT_vs_legacy_total.csv', columns,
        [joint_total, factorized_total, dar_total, correlation_difference, energy_difference, total_difference])
    result = dict(status='QUANTIFIED_THREE_SOURCE_REPRESENTATIONS', records=records,
        total_ROOT_joint_events=float(joint_total.sum()), total_ROOT_factorized_events=float(factorized_total.sum()),
        total_legacy_DAR_events=float(dar_total.sum()),
        total_event_difference=float(total_difference.sum()),
        max_bin_total_difference=float(np.max(np.abs(total_difference))),
        max_bin_correlation_difference=float(np.max(np.abs(correlation_difference))),
        max_bin_energy_model_difference=float(np.max(np.abs(energy_difference))),
        identical_absolute_inputs=dict(detector_mass_kg=float(flux['basic']['detectorMassKg']),
            fluence_per_flavor_cm_minus2=float(flux['measured']['muLine'][1]),
            PE_edges=A.PE_EDGES.tolist(), time_edges_us=A.TIME_EDGES.tolist()),
        legacy_energy_representation='Original SNS 200-point interpolated Michel spectra and exact prompt line',
        energy_difference_scope='Energy marginal, physical endpoint/tails, within-bin representation and associated recoil support',
        calibrated_recoil_scope='ROOT2--70keV versus DAR2keV--kinematic endpoint',
        paper_parameter_difference=dict(paper_detector_mass_kg=14.6, legacy_detector_mass_kg=14.57,
            paper_nominal_sin2thetaW=.23857, legacy_sin2thetaW=.2387,
            legacy_endpoint='Native finite-electron-mass muon DAR endpoint',
            paper_endpoint='m_mu/2 approximation in Eq28'),
        external_paper_status='BLOCKED_FULL_EQUIVALENCE',
        sources=['https://arxiv.org/html/2211.11905v2#S3.SS1',
                 'https://arxiv.org/src/2110.07730v2/anc/snsFlux2D.root'])
    write_json(output / 'ROOT_vs_legacy.json', result)
    return result


class ReferenceWindowLikelihood(L.TimeLikelihood):
    """Apply the paper's 6-us shape and the same numerical Eq29 normalization."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_source = SOURCE.load_sns_time_source()

    def templates(self, point=(0., 0.), shift_us=0., efficiency_shift_pe=0.):
        fast = import_module(PREFIX + '.fast_counts_csi2021_time').fast_counts_csi2021_time
        prediction = fast(self.kernel, *point, shift_us=shift_us, efficiency_shift_pe=efficiency_shift_pe)
        weights = T.build_time_weights(self.time_source, A.TIME_EDGES,
            efficiency=T.CsITimeEfficiency(), shift_us=shift_us,
            template_normalization='reference_window', energy_fluence_scope='reference_window',
            reference_window_us=[0, 6])
        signal = weights.apply(prediction.energy_before_time, counts_include_time_acceptance=False).sum(axis=(0, 1))
        return np.array([signal, *self.dataset.backgrounds(shift_us, self.background)])


def time_scope_audit(output, kernel, previous_kernel):
    """Expose the count change from assigning the same eta to different scopes."""
    fast = import_module(PREFIX + '.fast_counts_csi2021_time').fast_counts_csi2021_time
    source = SOURCE.load_sns_time_source()
    tables = {}
    records = []
    for index, shift in enumerate([-.25, 0., .25]):
        prediction = fast(kernel, shift_us=shift)
        converted = T.build_time_weights(source, A.TIME_EDGES, efficiency=T.CsITimeEfficiency(),
            shift_us=shift, template_normalization='reference_window',
            energy_fluence_scope='full_support', reference_window_us=[0, 6])
        paper = T.build_time_weights(source, A.TIME_EDGES, efficiency=T.CsITimeEfficiency(),
            shift_us=shift, template_normalization='reference_window',
            energy_fluence_scope='reference_window', reference_window_us=[0, 6])
        tables[shift] = paper
        converted_counts = converted.apply(prediction.energy_before_time, counts_include_time_acceptance=False).sum(axis=(0, 1))
        paper_counts = paper.apply(prediction.energy_before_time, counts_include_time_acceptance=False).sum(axis=(0, 1))
        np.testing.assert_allclose(converted_counts, prediction.counts_2d, rtol=3e-13, atol=1e-12)
        write_bins(output / f'time_fluence_scope_shift_{index}.csv',
            ['full_fluence_events', 'converted_reference_shape_events', 'same_eta_6us_shape_events', 'scope_difference_events'],
            [prediction.counts_2d, converted_counts, paper_counts, paper_counts - prediction.counts_2d])
        records.append(dict(shift_us=shift, full_fluence_events=prediction.total_events,
            same_eta_6us_shape_events=float(paper_counts.sum()),
            total_scope_difference=float(paper_counts.sum() - prediction.total_events),
            representation_conversion_max_bin_error=float(np.max(np.abs(converted_counts - prediction.counts_2d))),
            fixed_reference_fractions=paper.reference_fractions.tolist()))
    cases, _ = grid_predictions(kernel)
    predictions = []
    for selected in [previous_kernel, kernel]:
        grid = []
        for case in cases:
            prediction = fast(selected, *case['point'], shift_us=case['shift_us'],
                efficiency_shift_pe=case['efficiency_shift_pe'])
            grid.append(tables[case['shift_us']].apply(prediction.energy_before_time,
                counts_include_time_acceptance=False).sum(axis=(0, 1)))
        predictions.append(np.array(grid))
    previous, refined = predictions
    difference = refined - previous
    maximum = float(np.max(np.abs(difference)))
    np.savez_compressed(output / 'time_fluence_scope_grid.npz', previous=previous, refined=refined,
        differences=difference, cases_json=np.array(json.dumps(cases)))
    result = dict(status='PASS_DECLARED_SCOPE_GRID' if maximum < .005 else 'BLOCKED_GRID_TOLERANCE',
        records=records, threshold_events=.005, max_bin_grid_change=maximum, case_count=len(cases),
        scope='Same numerical Eq29 eta with a normalized 0--6us shape; fixed zero-shift denominator',
        physical_full_fluence_conversion='Multiplying reference-window fluence by its nominal fraction preserves full-source counts',
        selected_2211_diagnostic='Literal Eq29+32 numerical convention; fixed-radius Response remains an external diagnostic',
        original_paper='https://arxiv.org/pdf/2211.11905v2#page=12')
    write_json(output / 'time_fluence_scope.json', result)
    return result


def independent_benchmarks(output, kernel):
    dataset = D.load_time_dataset()
    result = {}
    for identifier, sigmas, mode in [
            ('RESPONSE_JHEP2022_4PULL', [.12, .25, .35, .021], 'time_nominal'),
            ('RESPONSE_2211_TIME', [.1145, .25, .35, .021], 'time')]:
        model_class = ReferenceWindowLikelihood if mode == 'time' else L.TimeLikelihood
        model = model_class(kernel, dataset, normalization_sigmas=sigmas)
        fit = model.profile(mode=mode, multistart=3, maxiter=600)
        probability_model = model_class(kernel, dataset, background='full_support_probability',
            normalization_sigmas=sigmas)
        probability_fit = probability_model.profile(mode=mode, multistart=3, maxiter=600)
        record = dict(status='BLOCKED_EXTERNAL_REPRODUCTION', implementation='PASS' if fit.success and probability_fit.success else 'FAIL',
            backend='Native Response', normalization_sigmas=sigmas, mode=mode,
            fit=fit.as_dict(), background_mode='raw_template_integrals',
            blockers=['BRN/NIN post-time-efficiency normalization requires original-author clarification',
                      'User-selected Response nuclear model uses a fixed radius; the 2211 radius nuisance is not implemented' if mode == 'time'
                      else 'User-selected Response nuclear model differs from the JHEP Helm prescription'],
            time_representation='reference_window_0_6_same_numerical_eta_as_Eq29' if mode == 'time' else 'full_support_fixed_time',
            full_support_probability_candidate_fit=probability_fit.as_dict(),
            candidate_status='DIAGNOSTIC_BLOCKED_TIME_EFFICIENCY_CONVENTION',
            original_paper_url='https://arxiv.org/abs/2211.11905v2' if mode == 'time' else 'https://arxiv.org/abs/2202.11002',
            source_equations='Eqs28--32,36,38; seven paper nuisances versus six fixed-radius Response nuisances' if mode == 'time' else 'JHEP05(2022)109 Eq2.6; four normalization pulls',
            reference_target=83.2 if mode == 'time' else None)
        if mode == 'time':
            full = L.TimeLikelihood(kernel, dataset, normalization_sigmas=sigmas).profile(mode=mode, multistart=3, maxiter=600)
            full_probability = L.TimeLikelihood(kernel, dataset, background='full_support_probability',
                normalization_sigmas=sigmas).profile(mode=mode, multistart=3, maxiter=600)
            record['full_fluence_diagnostic_fit'] = full.as_dict()
            record['full_fluence_probability_candidate_fit'] = full_probability.as_dict()
        write_bins(output / (identifier + '_bins.csv'), ['observed', 'CEvNS', 'BRN', 'NIN', 'SS', 'expected', 'residual'],
            [dataset.observed, *[fit.templates[i] * (1 + fit.nuisance[i]) for i in range(4)],
             fit.expected, dataset.observed - fit.expected])
        write_json(output / (identifier + '.json'), record)
        write_bins(output / (identifier + '_probability_candidate_bins.csv'),
            ['observed', 'CEvNS', 'BRN', 'NIN', 'SS', 'expected', 'residual'],
            [dataset.observed, *[probability_fit.templates[i] * (1 + probability_fit.nuisance[i]) for i in range(4)],
             probability_fit.expected, dataset.observed - probability_fit.expected])
        result[identifier] = record
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--signal', action='store_true')
    parser.add_argument('--max-level', type=int, default=4)
    parser.add_argument('--root-correlation', action='store_true')
    parser.add_argument('--source-comparison', action='store_true')
    parser.add_argument('--time-scope', action='store_true')
    args = parser.parse_args()
    if args.signal and args.max_level < 2:
        parser.error('--max-level must be at least2 for the declared refinement checks')
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    record_path = output / 'input_resolution.json'
    result = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else static_audit(output)
    if not args.signal and (args.time_scope or args.source_comparison) and 'signal_convergence' not in result:
        parser.error('--time-scope and --source-comparison require a completed --signal run')
    if args.signal:
        result = static_audit(output)
    write_json(output / 'input_resolution.json', result)
    if args.signal:
        kernel, convergence = refine_signal(output, args.max_level)
        result['signal_convergence'] = convergence
        result['QF']['omitted_low_recoil_sensitivity'] = qf_extrapolation_audit(output, kernel)
        previous = B.TimeKernel.load(output / convergence['records'][-2]['cache'])
        result['time_fluence_scope'] = time_scope_audit(output, kernel, previous)
        result['independent_benchmarks'] = independent_benchmarks(output, kernel)
        write_json(output / 'input_resolution.json', result)
    if args.root_correlation:
        result['ROOT_correlation'] = refine_root_correlation(output)
        write_json(output / 'input_resolution.json', result)
    if args.source_comparison:
        cache = result['signal_convergence']['records'][-1]['cache']
        result['ROOT_vs_legacy'] = source_model_comparison(output, B.TimeKernel.load(output / cache))
        write_json(output / 'input_resolution.json', result)
    if args.time_scope and not args.signal:
        rows = result['signal_convergence']['records']
        kernel = B.TimeKernel.load(output / rows[-1]['cache'])
        previous = B.TimeKernel.load(output / rows[-2]['cache'])
        result['time_fluence_scope'] = time_scope_audit(output, kernel, previous)
        result['independent_benchmarks'] = independent_benchmarks(output, kernel)
        write_json(output / 'input_resolution.json', result)
    print(json.dumps({key:value.get('status', 'RECORDED') for key,value in result.items()}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
