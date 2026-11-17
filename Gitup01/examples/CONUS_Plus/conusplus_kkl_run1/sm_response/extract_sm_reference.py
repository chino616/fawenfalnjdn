"""Recover Fig. 1 blue SM ordinate values from the fixed source PDF paths."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('sm')
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pdfplumber
HERE = Path(__file__).resolve().parent
SNAPSHOT = LAYOUT.path('snapshot')
DATA = SNAPSHOT / 'data/experiments/CONUS_Plus/conusplus_kkl_run1'
SOURCE = SNAPSHOT / 'docs/references/CONUS/2501.17843v3.pdf'
DESTINATION = LAYOUT.path('data/benchmark')
PREFIX = 'conusplus_2501_17843v3_fig1_sm_digitized'

def extract():
    spec = importlib.util.spec_from_file_location('digitize_observed', DATA / 'statistics/digitize_fig1.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    observed, _, calibration = reader.extract(SOURCE)
    if reader.csv_bytes(observed) != (DATA / 'statistics/conusplus_2501_17843v3_fig1_digitized.csv').read_bytes():
        raise ValueError('Observed-point re-extraction differs from the delivered v3 table')
    x_map = calibration['energy_eVee_equals_a_times_pdf_x_plus_b']
    y_map = calibration['excess_equals_a_times_pdf_top_plus_b']
    with pdfplumber.open(SOURCE) as document:
        page = document.pages[9]
        candidates = []
        for index, curve in enumerate(page.curves):
            color = curve.get('stroking_color')
            blue = isinstance(color, (list, tuple)) and len(color) == 3 and (color[0] < 0.1) and (color[1] < 0.1) and (color[2] > 0.7)
            if blue and curve['width'] > 200 and (not curve['fill']):
                candidates.append((index, curve))
        if len(candidates) != 1:
            raise ValueError('Expected one unfilled blue histogram outline')
        curve_index, curve = candidates[0]
        segments = []
        for i, (a, b) in enumerate(zip(curve['pts'][:-1], curve['pts'][1:])):
            if b[0] > a[0] and abs(b[1] - a[1]) < 1e-08:
                segments.append({'segment_index': i, 'x_low_eVee': float(np.polyval(x_map, a[0])), 'x_high_eVee': float(np.polyval(x_map, b[0])), 'ordinate': float(np.polyval(y_map, a[1])), 'pdf_start': list(a), 'pdf_end': list(b)})
    rows, trace = ([], [])
    for point in observed:
        centre = point['energy_center_eVee']
        matches = [s for s in segments if s['x_low_eVee'] - 1e-05 <= centre <= s['x_high_eVee'] + 1e-05]
        if len(matches) != 1:
            raise ValueError(f'Expected one histogram level at {centre} eVee')
        segment = matches[0]
        rows.append({'bin_index': point['bin_index'], 'energy_low_eVee': centre - 5, 'energy_high_eVee': centre + 5, 'energy_center_eVee': centre, 'paper_sm_counts_per_kg_per_10eVee': segment['ordinate'], 'source_id': 'arxiv_2501_17843v3_pdf_p10_fig1_blue_sm'})
        trace.append({'bin_index': point['bin_index'], 'sample_at_bin_centre': True, **segment})
    DESTINATION.mkdir(parents=True, exist_ok=True)
    csv_path = DESTINATION / (PREFIX + '.csv')
    if csv_path.exists():
        raise ValueError('Reference already exists. Preserve it or make an explicit revision.')
    with csv_path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    provenance = {'source_id': rows[0]['source_id'], 'created_date': '2026-11-06', 'citation': 'V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3.', 'source_pdf': str(SOURCE), 'source_pdf_sha256': reader.sha256(SOURCE), 'locator': 'PDF page 10, Fig. 1, blue unfilled theoretical histogram outline', 'method': 'PDF vector horizontal-segment ordinates sampled at all 19 observed bin centres', 'quantity_unit': 'counts kg^-1 (10 eVee)^-1', 'rescaling_applied': False, 'scope': 'Recover plotted SM ordinate values, without acquiring author numerical arrays.', 'limitations': ['Nominal 10 eVee bin edges follow the observed-point grid, not a released author edge file.', 'The blue path ends at 345 eVee. The last value is sampled at that endpoint and associated with the nominal 340-350 eVee bin.', 'A small extra plateau before 162.5 eVee is retained in the path trace. The 165 eVee centre selects the dominant first-bin level.', 'PDF-coordinate numerical precision does not establish physical or author-array precision.'], 'calibration': calibration, 'pdf_curve_index_zero_based': curve_index, 'all_blue_horizontal_segments': segments, 'coordinate_trace': trace, 'files': {csv_path.name: {'sha256': reader.sha256(csv_path)}, Path(__file__).name: {'sha256': reader.sha256(Path(__file__))}}, 'checks': {'row_count': len(rows), 'source_hash_matched': True, 'observed_reextraction_matched': True, 'histogram_level_match_count_per_bin': 1, 'sum_of_sampled_ordinates': sum((r['paper_sm_counts_per_kg_per_10eVee'] for r in rows))}}
    (DESTINATION / (PREFIX + '.provenance.json')).write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (DESTINATION / 'README.md').write_text('# Fig. 1 SM 对照数据\n\n[CSV](conusplus_2501_17843v3_fig1_sm_digitized.csv) 保存原图蓝色 SM 线在19个箱中心的纵值。\n\n[来源与逐线段追踪](conusplus_2501_17843v3_fig1_sm_digitized.provenance.json) 保存原文标准引文、页码、PDF指纹、坐标变换和末箱端点限制。\n\n生成入口为 [extract_sm_reference.py](../../extract_sm_reference.py)，图线精度与作者原始数表精度分别保留。\n', encoding='utf-8')
    print(json.dumps(provenance['checks']))
if __name__ == '__main__':
    extract()
