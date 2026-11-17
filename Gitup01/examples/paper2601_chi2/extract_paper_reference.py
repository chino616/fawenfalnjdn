"""Read-only PDF vector extraction for 2601.19883v2 Figs. 3 and 4.

Run with the bundled PDF Python (pdfplumber/numpy). Output is create-only.
These are plotted geometries, not author chi-square arrays.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'docs/references/General_CEvNS/2601.19883v2.pdf'
OPERATORS = ['O5_1', 'O6u_1', 'O6d_1', 'O6u_2', 'O6d_2',
             'O7u_1', 'O7d_1', 'O7u_2', 'O7d_2', 'O7u_3', 'O7d_3',
             'O7u_4', 'O7d_4', 'O7u_5', 'O7d_5', 'O7_6', 'O7_7',
             'O8u_1', 'O8d_1', 'O8u_2', 'O8d_2', 'O8_9']


def save_csv(path, rows):
    with path.open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def color_name(color):
    if not isinstance(color, (tuple, list)) or len(color) != 3:
        return None
    r, g, b = color
    if r > .9 and .6 < g < .8 and b < .4:
        return 'CONUS_plus'
    if r < .4 and .5 < g < .8 and b > .85:
        return 'COHERENT_CsI_Ar'
    if r < .6 and g > .65 and b < .6:
        return 'Solar_joint'
    return None


def extract(output):
    if output.exists():
        raise ValueError('Choose a fresh paper-reference directory')
    output.mkdir(parents=True)
    with pdfplumber.open(PAPER) as doc:
        # PDF p22 Fig3. Log axis calibrated against every labeled grid line.
        page = doc.pages[21]
        frame = page.rects[1]
        ys = sorted(set(round(line['top'], 6) for line in page.lines
                        if abs(line['width'] - frame['width']) < .001
                        and abs(line['x0'] - frame['x0']) < .001
                        and line['height'] < .001
                        and isinstance(line.get('stroking_color'), (int, float))
                        and .68 < line['stroking_color'] < .70), reverse=True)
        ticks = [.3, 1, 3, 10, 30, 100, 300, 1000, 10000, 100000]
        if len(ys) != len(ticks):
            raise ValueError('Figure 3 log-axis tick count changed')
        log_map = np.polyfit(ys, np.log10(ticks), 1)
        log_residual = float(np.max(abs(np.polyval(log_map, ys) - np.log10(ticks))))
        if log_residual > 2e-5:
            raise ValueError('Figure 3 axis calibration failed')
        bars = []
        for name in ('CONUS_plus', 'COHERENT_CsI_Ar', 'Solar_joint'):
            selected = sorted([r for r in page.rects if r['fill']
                               and color_name(r.get('non_stroking_color')) == name
                               and 4 < r['width'] < 5
                               and frame['top'] <= r['top'] <= frame['bottom']], key=lambda r: r['x0'])
            if len(selected) != 22:
                raise ValueError(f'Expected 22 Figure 3 bars for {name}, got {len(selected)}')
            for operator, bar in zip(OPERATORS, selected):
                bars.append({'experiment': name, 'operator': operator,
                             'lambda_GeV_from_plotted_height': float(10 ** np.polyval(log_map, bar['top'])),
                             'pdf_x': bar['x0'], 'pdf_top': bar['top'],
                             'source': '2601.19883v2 PDF p22 Fig3; vector bar top, log-axis calibration'})
        save_csv(output / 'fig3_plotted_limits.csv', bars)

        # PDF p23 Fig4. Keep separate filled polygons and their clipping edges.
        page = doc.pages[22]
        frame = page.rects[1]
        xs = sorted(set(round(l['x0'], 6) for l in page.lines if l['width'] < 1e-6
                        and abs(l['top'] - frame['bottom']) < .001
                        and abs(l['height'] - 2.1) < .001))
        ys = sorted(set(round(l['top'], 6) for l in page.lines if l['height'] < 1e-6
                        and abs(l['x1'] - frame['x0']) < .001
                        and abs(l['width'] - 2.1) < .001))
        if len(xs) != 9 or len(ys) != 9:
            raise ValueError('Figure 4 ticks changed')
        xmap = np.polyfit(xs, np.linspace(-1, 1, 9), 1)
        ymap = np.polyfit(ys, np.linspace(1, -1, 9), 1)
        residual = max(float(np.max(abs(np.polyval(xmap, xs) - np.linspace(-1, 1, 9)))),
                       float(np.max(abs(np.polyval(ymap, ys) - np.linspace(1, -1, 9)))))
        if residual > 1e-5:
            raise ValueError('Figure 4 axis calibration failed')
        vertices, polygons = [], []
        counts = {name: 0 for name in ('CONUS_plus', 'COHERENT_CsI_Ar', 'Solar_joint')}
        for index, curve in enumerate(page.curves):
            name = color_name(curve.get('non_stroking_color'))
            if not (name and curve['fill']):
                continue
            if not all(command[0] in ('m', 'l', 'h') for command in curve['path']):
                raise ValueError('Curved path needs an explicit extraction method')
            polygon = counts[name]
            counts[name] += 1
            polygons.append({'experiment': name, 'polygon': polygon, 'pdf_curve_index': index,
                             'vertices': len(curve['pts'])})
            for k, (x, y) in enumerate(curve['pts']):
                ex, ey = float(np.polyval(xmap, x)), float(np.polyval(ymap, y))
                vertices.append({'experiment': name, 'polygon': polygon, 'vertex': k,
                                 'epsilon_ee_uV': ex, 'epsilon_ee_dV': ey,
                                 'clipped_at_axis_boundary': int(max(abs(ex), abs(ey)) > .9999),
                                 'pdf_x': x, 'pdf_top': y})
        if set(counts.values()) != {2}:
            raise ValueError('Expected two filled polygons per experiment in Figure 4')
        save_csv(output / 'fig4_plotted_polygons.csv', vertices)
    record = {'source_pdf': str(PAPER), 'source_sha256': hashlib.sha256(PAPER.read_bytes()).hexdigest(),
              'source_locators': {'statistics': 'PDF pp20-21 Eqs86,88,90',
                                  'one_parameter_threshold': 'PDF p21 Eq92: 2.71',
                                  'two_parameter_threshold': 'PDF p22 after Eq95: 4.61; p23 figure title rounds to 4.6'},
              'fig3_log_axis_map': log_map.tolist(), 'fig3_max_log10_tick_residual': log_residual,
              'fig4_xmap': xmap.tolist(), 'fig4_ymap': ymap.tolist(),
              'fig4_max_tick_residual': residual, 'fig4_polygons': polygons,
              'scope': 'Rendered plot geometry; no author likelihood grids or numerical SM chi2 table supplied.',
              'limits': ['Fig3 bar-height values are graphical extraction, not printed exact values.',
                         'Fig4 filled paths include panel clipping and may include holes; preserve paths separately.',
                         'Non-clipped vertices can test agreement with a computed contour, not certify source-code equivalence.']}
    (output / 'PROVENANCE.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    (output / 'README.md').write_text('# 2601.19883v2: plotted reference geometry\n\n'
        '[Provenance and calibration](PROVENANCE.json) · [Fig3 bars](fig3_plotted_limits.csv) · '
        '[Fig4 polygons](fig4_plotted_polygons.csv)\n\n'
        'PDF pages 20-23 were rendered and visually inspected. These extractions are figure geometries, '
        'not author likelihood arrays. [Parent report](../README.md).\n', encoding='utf8')
    print(json.dumps({'fig3_bars': len(bars), 'fig4_vertices': len(vertices), 'tick_residual': residual}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    extract(parser.parse_args().output.resolve())
