"""Build versioned source/target review data, without changing any runtime model.

The low-energy table is transcribed from the user note, not falsely certified as
the original Kopeikin numerical release. --check compares deterministic outputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

import numpy as np
import pdfplumber
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'docs/references/CONUS/2501.17843v3.pdf').is_file())
TAG = 'v3_20261106_provenance'
RUN = ROOT / 'workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1'
SOURCES = RUN / 'sources'
NOTE = SOURCES / 'user_reference_CONUS.pdf'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(name):
    return list(csv.DictReader((HERE / name).read_text(encoding='utf-8').splitlines()))


def encode_csv(names, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(names)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def table_number(text):
    match = re.fullmatch(r'(-?\d+(?:\.\d+)?)(?:\((-?\d+)\))?', text)
    if not match:
        raise ValueError(text)
    return float(match[1]) * (10 ** int(match[2]) if match[2] else 1)


def verify_transcription(coefficients, low_energy, low_shape):
    with pdfplumber.open(SOURCES / '1101.2663v3.pdf') as pdf:
        text = pdf.pages[12].crop((300, 0, 612, 792)).extract_text()
    matches = re.findall(r'^\s*[1-6]\s+(-?\d+(?:\.\d+)?(?:\(-?\d+\))?)\s+', text, re.M)
    primary = np.array([table_number(t) for t in matches])
    if primary.shape != (24,) or not np.allclose(primary.reshape(4, 6), coefficients, rtol=0, atol=1e-14):
        raise ValueError(f'Mueller Table VI transcription differs: {primary.tolist()}')
    with pdfplumber.open(NOTE) as pdf:
        text = pdf.pages[5].extract_text()
    pairs = []
    for line in text.splitlines():
        values = re.fullmatch(r'(\d+\.\d+)\s+(\d+(?:\.\d+)?)\s+(\d+\.\d+)\s+(\d+(?:\.\d+)?)', line.strip())
        if values:
            a, b, c, d = map(float, values.groups())
            pairs.extend([(a, b), (c, d)])
    pairs = np.array(sorted(pairs))
    if pairs.shape != (32, 2) or not np.array_equal(pairs[:, 0], low_energy) or not np.array_equal(pairs[:, 1], low_shape):
        raise ValueError('The 32 nodes differ from Table 2 of the supplied note')
    return {'mueller_24_coefficients_vs_primary_Table_VI': 'PASS',
            'low_32_nodes_vs_supplied_note_Table_2': 'PASS',
            'low_32_nodes_vs_Kopeikin_2012_original_table': 'NOT_VERIFIED_SUBSCRIPTION_FULLTEXT_NOT_ACQUIRED'}


def plot_flux(energy, physical, literal):
    image = Image.new('RGB', (1600, 930), 'white')
    draw = ImageDraw.Draw(image)
    fonts = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(fonts), 23) if fonts.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(fonts), 19) if fonts.exists() else ImageFont.load_default()
    draw.text((48, 22), 'CONUS+ onboarding v3 | reference-PDF Flux, with the approved (0,0) endpoint', fill='black', font=font)
    draw.text((48, 61), 'Blue: v3 nonnegative default; orange: supplied-note linear extrapolation (diagnostic only).', fill='black', font=small)
    for bounds, low_panel in [((100, 130, 1500, 465), False), ((100, 565, 1500, 850), True)]:
        left, top, right, bottom = bounds
        if low_panel:
            x = np.linspace(0, 0.03, 601)
            y1 = np.interp(x, energy, physical) / 1e12
            y2 = np.interp(x, energy, literal) / 1e12
            xmin, xmax = 0., .03
            ymin, ymax = min(y2.min(), 0.) * 1.15, max(y1.max(), y2.max()) * 1.1
            title = 'Low-energy endpoint detail (MeV); vertical axis: 10^12 cm^-2 s^-1 MeV^-1'
        else:
            x, y1, y2 = energy, physical / 1e12, literal / 1e12
            xmin, xmax, ymin, ymax = 0., 10., 0., max(y1.max(), y2.max()) * 1.07
            title = 'Full 0-10 MeV range; vertical axis: 10^12 cm^-2 s^-1 MeV^-1'
        draw.text((left, top - 30), title, fill='black', font=small)
        draw.rectangle(bounds, outline='#334155', width=2)
        px = left + (x - xmin) * (right - left) / (xmax - xmin)
        for y, color in [(y2, '#dc7b21'), (y1, '#1266ad')]:
            py = bottom - (y - ymin) * (bottom - top) / (ymax - ymin)
            draw.line(list(zip(px, np.clip(py, top, bottom))), fill=color, width=3)
        for value in np.linspace(xmin, xmax, 6):
            xx = left + (value - xmin) * (right - left) / (xmax - xmin)
            draw.line((xx, bottom, xx, bottom + 6), fill='black', width=2)
            draw.text((xx - 15, bottom + 8), f'{value:g}', fill='black', font=small)
        for value in np.linspace(ymin, ymax, 5):
            yy = bottom - (value - ymin) * (bottom - top) / (ymax - ymin)
            draw.text((12, yy - 10), f'{value:.2f}', fill='black', font=small)
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


def build():
    config = json.loads((HERE / 'input_choices.json').read_text(encoding='utf-8'))
    rows = read_csv('mueller_coefficients.csv')
    coefficients = np.array([[float(r[f'a{i}']) for i in range(6)] for r in rows])
    low = read_csv('kopeikin_low_energy_transcribed.csv')
    low_energy = np.array([float(r['energy_MeV']) for r in low])
    low_shape = np.array([float(r['relative_shape']) for r in low])
    fractions = read_csv('fission_fractions.csv')
    weights = np.array([float(r['pdf_reference_fraction']) for r in fractions])
    if not np.isclose(weights.sum(), 1., atol=1e-14):
        raise ValueError('Fission fractions do not sum to one')
    source_checks = verify_transcription(coefficients, low_energy, low_shape)

    def high(e):
        e = np.asarray(e, dtype=float)
        powers = np.array([e ** i for i in range(6)])
        return weights @ np.exp(coefficients @ powers)

    match = float(high(2.)) / float(low_shape[-1])
    low_x = np.r_[0., low_energy]
    low_y = np.r_[0., low_shape]
    slope = (low_shape[1] - low_shape[0]) / (low_energy[1] - low_energy[0])
    literal_at_zero = float(low_shape[0] - slope * low_energy[0])
    literal_zero_crossing = float(-literal_at_zero / slope)

    def high_integral(order, start=2., stop=10.):
        nodes, weights_q = np.polynomial.legendre.leggauss(order)
        x = (start + stop) / 2 + (stop - start) / 2 * nodes
        return float((stop - start) / 2 * np.dot(weights_q, high(x)))

    high128, high256 = high_integral(128), high_integral(256)
    low_default = float(np.trapezoid(low_y, low_x)) * match
    low_literal = (float(np.trapezoid(low_shape, low_energy)) +
                   (literal_at_zero + low_shape[0]) * low_energy[0] / 2) * match
    norm_default, norm_literal = float(low_default + high256), float(low_literal + high256)
    energy = np.linspace(0., 10., 10001)

    def shape(e, literal=False):
        values = np.where(e < 2., match * np.interp(e, low_x, low_y), high(e))
        if literal:
            values = np.where(e < low_energy[0], match * (literal_at_zero + slope * e), values)
        return values

    rho_default = shape(energy)
    rho_literal = shape(energy, literal=True)
    total = config['flux_total_cm2_s']
    physical = total * rho_default / norm_default
    literal = total * rho_literal / norm_literal
    flux_columns = ['energy_MeV', 'flux_cm_minus2_s_minus1_MeV_minus1', 'relative_shape', 'segment', 'source_ids',
                    'direct_shape_source_id', 'claimed_primary_source_id', 'input_table_primary_verified', 'normalization_source_id', 'processing_decision_refs', 'tail_within_original_fit_range']
    def flux_bytes(values, rho):
        return encode_csv(flux_columns, ([f'{e:.6f}', f'{v:.12e}', f'{s:.12e}',
                                         'low_note_table' if e < 2 else ('Mueller_fit' if e <= 8 else 'Mueller_tail_extension'),
                                         'S0002;S0004' if e < 2 else 'S0003;S0002',
                                         'S0002' if e < 2 else 'S0003',
                                         'S0004' if e < 2 else 'S0003',
                                         'false' if e < 2 else 'true', 'S0001', 'D_V2_003' if e < 0.01 else '', 'false' if e > 8 else 'true']
                                        for e, v, s in zip(energy, values, rho)))
    outputs = {
        'reactor_flux_default.csv': flux_bytes(physical, rho_default),
        'reactor_flux_reference_linear_extrapolation.csv': flux_bytes(literal, rho_literal),
    }

    # Natural Ge uses atomic masses for atoms/kg and subtracts electron rest masses
    # only for approximate nuclear kinematics; atomic binding correction is omitted explicitly.
    const = config['constants']
    isotope_items = list(config['target_number_fractions'].items())
    mean_mass_u = sum(x * config['target_atomic_masses_u'][key] for key, x in isotope_items)
    target_rows, response_results = [], []
    resource = ROOT / config['nuclear_response_resource']
    spec = importlib.util.spec_from_file_location('conus_v3_response_review', ROOT / 'cevns_pyeft/nuclear/response.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    database = module.ResponseDB(resource)
    for key, number_fraction in isotope_items:
        mass = config['target_atomic_masses_u'][key]
        response = database.get(key)
        A = int(key[2:])
        nuclear_mass = mass * const['atomic_mass_energy_GeV'] - 32 * const['electron_mass_energy_GeV']
        nuclei_kg = number_fraction / (mean_mass_u * const['atomic_mass_kg'])
        target_rows.append([key, A, 32, A - 32, f'{number_fraction:.8f}', f'{mass:.12f}',
                            f'{number_fraction * mass / mean_mass_u:.12f}', f'{nuclei_kg:.12e}',
                            f'{nuclear_mass:.12f}', key, 'S0001;S0005;S0006;S0007'])
        values = [np.asarray(response.W_np(channel, y), dtype=float)
                  for channel in response.keys() for y in [0., .01, .1, 1.]]
        if not all(np.all(np.isfinite(value)) for value in values):
            raise ValueError(f'Nonfinite response: {key}')
        if any(v.shape != (2, 2) for v in values):
            raise ValueError(f'Response is not a (p,n) 2x2 matrix: {key}')
        response_results.append({'isotope': key, 'basic': response.basic, 'channels': response.keys(),
                                 'finite_matrices_at_y': [0., .01, .1, 1.],
                                 'M_at_zero': response.W_np('M', 0.),
                                 'primary_nuclear_calculation_table_provenance': 'NOT_CLOSED'})
    outputs['natural_ge_inventory.csv'] = encode_csv(
        ['isotope', 'A', 'Z', 'N', 'number_fraction', 'atomic_mass_u', 'mass_fraction',
         'nuclei_per_kg', 'nuclear_mass_GeV_approx', 'response_key', 'source_ids'], target_rows)
    integral_grid = float(np.trapezoid(physical, energy))
    checks = {
        'version': TAG, 'source_checks': source_checks,
        'input_note_sha256': digest(NOTE),
        'mueller_primary_pdf_sha256': digest(SOURCES / '1101.2663v3.pdf'),
        'fission_fraction_sum': float(weights.sum()),
        'mueller_mixture_at_2_MeV': float(high(2.)), 'matching_factor': match,
        'normalization_default_MeV': norm_default, 'normalization_literal_reference_MeV': norm_literal,
        'supplied_note_Nrho_6_46089_reproduced': abs(norm_literal - 6.46089) < 5e-6,
        'relative_normalization_change_percent': (norm_default / norm_literal - 1.) * 100.,
        'literal_reference_relative_shape_at_zero': literal_at_zero,
        'literal_reference_negative_below_MeV': literal_zero_crossing,
        'default_low_shape_node_added': [0., 0.],
        'default_flux_min': float(physical.min()), 'default_nonnegative': bool(np.all(physical >= 0)),
        'default_finite': bool(np.all(np.isfinite(physical))),
        'analytic_piecewise_total_flux': total,
        'csv_trapezoid_integral_flux': integral_grid,
        'csv_integral_relative_error': abs(integral_grid / total - 1.),
        'quadrature_128_256_relative_difference': abs(high128 / high256 - 1.),
        'join_left_right_relative_difference': abs(match * low_shape[-1] / float(high(2.)) - 1.),
        'fraction_of_shape_integral_in_8_to_10_MeV_extension': high_integral(256, 8., 10.) / norm_default,
        'mean_atomic_mass_u': mean_mass_u,
        'number_fraction_sum': sum(x for _, x in isotope_items),
        'mass_fraction_sum': sum(float(row[6]) for row in target_rows),
        'response_resource_sha256': digest(resource), 'response_review': response_results,
        'response_scope': 'Structure and finite-value checks only; no external nuclear-table equivalence or antineutrino-kernel audit certified',
        'fit_executed': False, 'runtime_changed': False,
        'nuclear_mass_convention': 'NIST atomic mass*u energy minus Z*electron rest energy; electron binding energy neglected explicitly',
        'coefficient_uncertainty_usage': 'Nominal coefficients only; no extra Mueller shape pulls added to the benchmark cumulative 0.169 pull',
    }
    if not checks['default_nonnegative'] or not checks['default_finite'] or checks['csv_integral_relative_error'] > 2e-6:
        raise ValueError('Flux numeric acceptance failed')
    outputs['numerical_checks.json'] = (json.dumps(checks, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    outputs['flux_comparison.png'] = plot_flux(energy, physical, literal)
    return outputs, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--refresh-draft', action='store_true', help='Explicitly refresh backed-up outputs inside this v3 directory')
    args = parser.parse_args()
    outputs, checks = build()
    for name, payload in outputs.items():
        path = HERE / name
        if args.check:
            if path.read_bytes() != payload:
                raise ValueError('Regeneration differs: ' + name)
        elif path.exists() and path.read_bytes() != payload and not args.refresh_draft:
            raise ValueError('Refusing different existing output: ' + name)
        elif not path.exists() or args.refresh_draft:
            path.write_bytes(payload)
    print(('PASS checked' if args.check else 'Created') + ': v3 Flux/target data; 24 primary coefficients; 32 note nodes; 5 Response keys')
    print(json.dumps({k: checks[k] for k in ['normalization_default_MeV', 'normalization_literal_reference_MeV',
                                          'relative_normalization_change_percent', 'csv_integral_relative_error',
                                          'default_nonnegative', 'mean_atomic_mass_u']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
