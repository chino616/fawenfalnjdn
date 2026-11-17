"""Extract the fixed benchmark Table II and blue Fig. 4 vector polygons."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('nsi')
import csv
import json
from pathlib import Path
import re
import numpy as np
import pdfplumber
HERE = Path(__file__).resolve().parent
PDF = LAYOUT.path('snapshot/docs/references/CONUS/2501.17843v3.pdf')
DEST = LAYOUT.path('data/benchmark')
EXPECTED_SHA = 'b20923363badde299106a6df83f0dff5308fd69d652b59b9967d32b764057c90'
CITATION = 'V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3.'

def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    import hashlib
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(PDF) != EXPECTED_SHA:
        raise ValueError('The fixed benchmark PDF changed')
    if (DEST / 'tableII_1sigma.csv').exists():
        raise ValueError('Reference extraction already exists; retain this version')
    with pdfplumber.open(PDF) as document:
        text = document.pages[12].extract_text()
        lines = [line for line in text.splitlines() if re.match('ε[ud]V\\s+\\[', line)]
        expected = [('epsilon_ee_uV', 'u', [(-0.037, 0.026), (0.348, 0.411)]), ('epsilon_ee_dV', 'd', [(-0.034, 0.024), (0.322, 0.38)]), ('epsilon_emu_uV', 'u', [(-0.123, 0.123)]), ('epsilon_emu_dV', 'd', [(-0.114, 0.114)]), ('epsilon_etau_uV', 'u', [(-0.123, 0.123)]), ('epsilon_etau_dV', 'd', [(-0.114, 0.114)])]
        if len(lines) != 6:
            raise ValueError('Expected the six NSI rows in Table II')
        rows, table_trace = ([], [])
        for row_number, (line, (coupling, quark, limits)) in enumerate(zip(lines, expected), 1):
            assert line.startswith('ε' + quark + 'V')
            groups = re.findall('\\[([^]]+)\\]', line.replace('−', '-'))
            extracted = [tuple((float(x) for x in group.split(','))) for group in groups[:len(limits)]]
            if extracted != limits:
                raise ValueError('Transcribed NSI intervals differ from the source text: ' + coupling)
            for interval_index, (lower, upper) in enumerate(extracted, 1):
                rows.append({'coupling': coupling, 'interval_index': interval_index, 'lower': lower, 'upper': upper, 'confidence': '1sigma', 'nominal_delta_chi2': 1.0, 'source_id': 'arxiv2501_17843v3_p13_tableII_CONUS'})
            table_trace.append({'row_index': row_number, 'coupling': coupling, 'raw_pdf_text': line, 'CONUS_intervals': extracted, 'COHERENT_column_excluded': True})
        page = document.pages[13]
        panel_specs = [('diag_ud', 1, [-1, -0.5, 0, 0.5, 1], [1, 0.5, 0, -0.5, -1], 'epsilon_ee_dV', 'epsilon_ee_uV'), ('fc_ud', 4, [-1, -0.5, 0, 0.5, 1], [1, 0.5, 0, -0.5, -1], 'epsilon_emu_uV', 'epsilon_emu_dV'), ('ring_mu', 6, [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8], [0.6, 0.4, 0.2, 0, -0.2, -0.4], 'epsilon_ee_dV', 'epsilon_emu_dV'), ('ring_tau', 10, [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8], [0.6, 0.4, 0.2, 0, -0.2, -0.4], 'epsilon_ee_dV', 'epsilon_etau_dV')]
        polygon_rows, panels = ([], [])
        for panel_id, rectangle_index, x_values, y_values, x_name, y_name in panel_specs:
            frame = page.rects[rectangle_index]
            x_ticks = [line for line in page.lines if abs(line['width']) < 1e-07 and abs(line['bottom'] - frame['bottom']) < 1e-05 and (4.8 < line['height'] < 5.5) and (frame['x0'] - 1e-05 <= line['x0'] <= frame['x1'] + 1e-05)]
            y_ticks = [line for line in page.lines if abs(line['height']) < 1e-07 and abs(line['x0'] - frame['x0']) < 1e-05 and (4.8 < line['width'] < 5.5) and (frame['top'] - 1e-05 <= line['top'] <= frame['bottom'] + 1e-05)]
            x_ticks.sort(key=lambda line: line['x0'])
            y_ticks.sort(key=lambda line: line['top'])
            assert len(x_ticks) == len(x_values) and len(y_ticks) == len(y_values)
            x_map = np.polyfit([line['x0'] for line in x_ticks], x_values, 1)
            y_map = np.polyfit([line['top'] for line in y_ticks], y_values, 1)
            residual = max(float(np.max(abs(np.polyval(x_map, [line['x0'] for line in x_ticks]) - x_values))), float(np.max(abs(np.polyval(y_map, [line['top'] for line in y_ticks]) - y_values))))
            assert residual < 1e-07
            polygons = []
            for curve_index, curve in enumerate(page.curves):
                color = curve.get('non_stroking_color')
                blue = isinstance(color, (list, tuple)) and len(color) == 3 and (color[0] < 0.15) and (0.5 < color[1] < 0.7) and (color[2] > 0.75)
                inside = frame['x0'] - 1e-05 <= curve['x0'] <= curve['x1'] <= frame['x1'] + 1e-05 and frame['top'] - 1e-05 <= curve['top'] <= curve['bottom'] <= frame['bottom'] + 1e-05
                if not (blue and curve['fill'] and inside):
                    continue
                assert all((command[0] in ('m', 'l', 'h') for command in curve['path']))
                polygon_index = len(polygons)
                for vertex_index, (x_pdf, y_pdf) in enumerate(curve['pts']):
                    polygon_rows.append({'panel': panel_id, 'polygon_index': polygon_index, 'vertex_index': vertex_index, 'x': float(np.polyval(x_map, x_pdf)), 'y': float(np.polyval(y_map, y_pdf)), 'pdf_x': x_pdf, 'pdf_top': y_pdf, 'source_id': 'arxiv2501_17843v3_p14_fig4_blue'})
                polygons.append({'polygon_index': polygon_index, 'pdf_curve_index': curve_index, 'vertices': len(curve['pts']), 'fill_rule': 'Preserve individual outline; inner boundaries may represent holes.'})
            assert len(polygons) == (1 if panel_id == 'fc_ud' else 2)
            panels.append({'panel': panel_id, 'rectangle_index': rectangle_index, 'x_parameter': x_name, 'y_parameter': y_name, 'x_map': x_map.tolist(), 'y_map': y_map.tolist(), 'x_tick_values': x_values, 'y_tick_values': y_values, 'frame': {key: frame[key] for key in ('x0', 'x1', 'top', 'bottom')}, 'max_tick_residual': residual, 'polygons': polygons})
    write_csv(DEST / 'tableII_1sigma.csv', rows)
    write_csv(DEST / 'fig4_blue_polygons.csv', polygon_rows)
    record = {'citation': CITATION, 'source_pdf': str(PDF), 'source_sha256': sha(PDF), 'table_locator': 'PDF p.13, Table II, CONUS+ (This Work) column, six vector NSI rows, 1sigma caption', 'figure_locator': 'PDF p.14, Fig.4, four panels, blue CONUS+ 90% CL filled-region boundaries', 'method': 'Table values checked against PDF text and visually reviewed table. Polygon paths and all major axis ticks extracted as PDF vectors.', 'table_trace': table_trace, 'figure_panels': panels, 'scope': 'Published rounded intervals and rendered contour boundaries. Author likelihood/surface arrays were not acquired.', 'limitations': ['3-decimal Table II endpoints have publication rounding precision.', 'Vector polygon coordinates describe the plotted geometry, including clipped boundaries at panel edges.', 'The bottom-panel y frames extend to -0.5; calibration uses the labeled -0.4..0.6 major ticks.', 'PDF vector geometry does not establish original likelihood-grid precision.'], 'files': {name: {'sha256': sha(DEST / name)} for name in ('tableII_1sigma.csv', 'fig4_blue_polygons.csv')}, 'extractor_sha256': sha(Path(__file__)), 'created_date': '2026-11-06'}
    (DEST / 'REFERENCES_PROVENANCE.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'table_intervals': len(rows), 'panels': len(panels), 'polygons': sum((len(p['polygons']) for p in panels)), 'vertices': len(polygon_rows)}))
if __name__ == '__main__':
    main()
