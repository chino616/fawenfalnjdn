"""Redraw Fig4 from pinned, already computed surfaces; no physics refitting.

Paper paths are rendered reference geometry. Solar local NSI is unavailable.
The current asymmetric-Ar and mean-error-Ar variants remain separate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'outputs/paper2601_joint_audit_20261111'
REFERENCE = ROOT/'outputs/paper2601_chi2_20261111/paper_reference'
LEVEL = 4.61
COLORS = {'CONUS_plus': '#e99516', 'COHERENT_CsI_Ar': '#2786c7', 'Solar_joint': '#59ad63'}
PAPER_COLORS = {'CONUS_plus': '#ffa726', 'COHERENT_CsI_Ar': '#42a5f5', 'Solar_joint': '#66bb6a'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def surface(path):
    data = load(path)
    if data['chi2'].shape != (len(data['y']), len(data['x'])):
        raise ValueError('Expected chi2[y,x]')
    if not np.allclose(data['delta_chi2'], data['chi2']-data['minimum_chi2'], rtol=0, atol=1e-11):
        raise ValueError('Saved delta chi2/minimum mismatch')
    if not np.array_equal(data['x'], np.linspace(-1, 1, 801)) or not np.array_equal(data['y'], data['x']):
        raise ValueError('Figure expects the audited 801x801 grid')
    return data


def polygons(vertices, experiment):
    return [np.column_stack([row['epsilon_ee_uV'], row['epsilon_ee_dV']])
            for number in (0, 1)
            for row in [vertices[(vertices['experiment'] == experiment) & (vertices['polygon'] == number)]]]


def draw_paper(ax, vertices, experiment, *, fill=False, alpha=1., hatch=None, color=None, linestyle='--', linewidth=1.):
    for points in polygons(vertices, experiment):
        color_here = color or PAPER_COLORS[experiment]
        if fill:
            ax.add_patch(Polygon(points, closed=True, facecolor=color_here, edgecolor=color_here,
                                 alpha=alpha, hatch=hatch, linewidth=.7, zorder=1))
        closed = np.vstack([points, points[0]])
        ax.plot(closed[:, 0], closed[:, 1], color=color_here, ls=linestyle, lw=linewidth, zorder=5)


def contour(ax, data, color, *, style='-', width=1.7, fill=False, zorder=4):
    if fill:
        ax.contourf(data['x'], data['y'], data['delta_chi2'], levels=[-1e-8, LEVEL],
                    colors=[color], alpha=.25, zorder=2)
    result = ax.contour(data['x'], data['y'], data['delta_chi2'], levels=[LEVEL],
                        colors=[color], linewidths=width, linestyles=style, zorder=zorder)
    return [points.copy() for points in result.allsegs[0] if len(points) >= 2]


def axes_style(ax, *, limits=(-1, 1, -1, 1), origin=True):
    ax.set(xlim=limits[:2], ylim=limits[2:], xlabel=r'$\epsilon_{ee}^{uV}$', ylabel=r'$\epsilon_{ee}^{dV}$')
    ax.set_aspect('equal', adjustable='box')
    if limits == (-1, 1, -1, 1):
        ax.set_xticks(np.linspace(-1, 1, 9)); ax.set_yticks(np.linspace(-1, 1, 9))
        ax.tick_params(labelsize=9)
    ax.grid(alpha=.12, lw=.6, zorder=0)
    if origin:
        ax.plot(0, 0, 'k+', ms=7, mew=1.1, zorder=10)


def intersections(paths, *, close=False):
    roots = []
    for points in paths:
        if close:
            points = np.vstack([points, points[0]])
        x, y = points.T
        chosen = np.flatnonzero(((x[:-1] < 0) & (x[1:] >= 0)) | ((x[:-1] >= 0) & (x[1:] < 0)))
        roots.extend((y[chosen]-x[chosen]*(y[chosen+1]-y[chosen])/(x[chosen+1]-x[chosen])).tolist())
    return sorted(set(round(value, 10) for value in roots))


def save_figure(fig, output, name):
    fig.savefig(output/(name+'.png'), dpi=300)
    fig.savefig(output/(name+'.svg'))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--refresh-render', action='store_true', help='Refresh only known render/figure metadata files in this run')
    args = parser.parse_args(); out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    allowed = {'PLAN.json'}
    if args.refresh_render:
        allowed |= {'fig4_paper_vs_corrected.png', 'fig4_paper_vs_corrected.svg',
                    'fig4_difference_detail.png', 'fig4_difference_detail.svg',
                    'FIGURE_MANIFEST.json', 'contour_vertices.npz', 'README.md'}
    if any(path.name not in allowed for path in out.iterdir()):
        parser.error('Use a fresh figure directory')
    plan_path = out/'PLAN.json'
    if not plan_path.exists():
        inputs = [ROOT/'docs/references/General_CEvNS/2601.19883v2.pdf',
                  REFERENCE/'fig4_plotted_polygons.csv', REFERENCE/'PROVENANCE.json',
                  ROOT/'outputs/paper2601_chi2_20261111/COHERENT_CsI_Ar_plane.npz',
                  SOURCE/'CONUS_plus_surface.npz', SOURCE/'current_asymmetric_Ar_surface.npz',
                  SOURCE/'previous_mean_Ar_surface.npz', SOURCE/'SUMMARY.json']
        plan = {'version_date': '2026-11-12', 'operation': 'Plot existing surfaces only; no physics or fit changes',
                'input_files': [{'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(p)} for p in inputs]}
        plan_path.write_text(json.dumps(plan, indent=2)+'\n', encoding='utf8')
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    for row in plan['input_files']:
        if sha(ROOT/row['path']) != row['sha256']:
            raise ValueError('Pinned input changed: '+row['path'])
    provenance = json.loads((REFERENCE/'PROVENANCE.json').read_text(encoding='utf8'))
    if sha(ROOT/'docs/references/General_CEvNS/2601.19883v2.pdf') != provenance['source_sha256']:
        raise ValueError('Paper and extracted paths are from different PDF versions')
    vertices = np.genfromtxt(REFERENCE/'fig4_plotted_polygons.csv', names=True, delimiter=',', dtype=None, encoding='utf8')
    conus = surface(SOURCE/'CONUS_plus_surface.npz')
    asymmetric = surface(SOURCE/'current_asymmetric_Ar_surface.npz')
    mean = surface(SOURCE/'previous_mean_Ar_surface.npz')
    old = load(ROOT/'outputs/paper2601_chi2_20261111/COHERENT_CsI_Ar_plane.npz')
    if not np.allclose(old['chi2'], mean['chi2'], rtol=0, atol=1e-9):
        raise ValueError('Before/after optimizer comparison must use the same raw chi2 surface')
    offset = float(np.median(mean['delta_chi2']-old['delta_chi2']))
    if not np.allclose(mean['delta_chi2']-old['delta_chi2'], offset, rtol=0, atol=1e-10):
        raise ValueError('Optimizer correction is not a constant minimum shift')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'mathtext.fontset': 'stix',
                         'axes.titlesize': 11, 'axes.labelsize': 13, 'svg.fonttype': 'none',
                         'hatch.linewidth': .45, 'savefig.facecolor': 'white'})

    # Full Fig4 comparison: same color families, coordinate range, threshold.
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 6.35))
    fig.subplots_adjust(left=.075, right=.985, bottom=.16, top=.86, wspace=.23)
    for name in ('Solar_joint', 'COHERENT_CsI_Ar', 'CONUS_plus'):
        draw_paper(axes[0], vertices, name, fill=True, alpha=.95, linestyle='-', linewidth=.5)
    axes[0].set_title('(a) Paper Fig.4: extracted PDF regions', pad=12)
    axes[0].legend(handles=[Patch(facecolor=PAPER_COLORS['CONUS_plus'], label='CONUS+'),
                            Patch(facecolor=PAPER_COLORS['COHERENT_CsI_Ar'], label='COHERENT (CsI + Ar)'),
                            Patch(facecolor=PAPER_COLORS['Solar_joint'], label='PandaX-4T + XENONnT')],
                   loc='upper right', fontsize=8, framealpha=.96, edgecolor='.8')
    draw_paper(axes[1], vertices, 'Solar_joint', fill=True, alpha=.10, hatch='///',
               color=COLORS['Solar_joint'], linewidth=1.1)
    paths = {}
    paths['current_asymmetric_Ar'] = contour(axes[1], asymmetric, COLORS['COHERENT_CsI_Ar'], fill=True)
    paths['CONUS_plus'] = contour(axes[1], conus, COLORS['CONUS_plus'], fill=True)
    for name in ('COHERENT_CsI_Ar', 'CONUS_plus'):
        draw_paper(axes[1], vertices, name, color=COLORS[name], linewidth=1., linestyle=(0, (4, 2)))
    axes[1].set_title('(b) Corrected local regions + paper outlines', pad=12)
    axes[1].legend(handles=[Line2D([0], [0], color='.15', lw=1.8, label='Solid: corrected local calculation'),
                            Line2D([0], [0], color='.15', ls='--', lw=1., label='Dashed: paper boundary'),
                            Patch(facecolor='#e7f2e8', edgecolor=COLORS['Solar_joint'], hatch='///', label='Solar: paper only, no local NSI')],
                   loc='upper right', fontsize=7.9, framealpha=.96, edgecolor='.8')
    for ax in axes:
        axes_style(ax)
    fig.suptitle(r'Fig.4 comparison: 90% C.L. ($\Delta\chi^2=4.61$, 2 d.o.f.)', fontsize=14, y=.96)
    fig.text(.5, .045, 'Orange: CONUS+   |   Blue: CsI + Ar (asymmetric Ar errors)   |   Green: paper solar reference only',
             ha='center', fontsize=9)
    save_figure(fig, out, 'fig4_paper_vs_corrected')

    # Split plots and an inner-gap zoom make overlapping boundaries legible.
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 5.8))
    fig.subplots_adjust(left=.055, right=.985, bottom=.27, top=.83, wspace=.25)
    draw_paper(axes[0], vertices, 'CONUS_plus', fill=True, alpha=.12, color=COLORS['CONUS_plus'],
               linestyle='--', linewidth=1.)
    for points in polygons(vertices, 'CONUS_plus'):
        points = np.vstack([points, points[0]]); axes[0].plot(points[:, 0], points[:, 1], 'k--', lw=1., zorder=6)
    contour(axes[0], conus, COLORS['CONUS_plus'])
    axes[0].set_title('(a) CONUS+', pad=10)
    for ax in axes[1:]:
        draw_paper(ax, vertices, 'COHERENT_CsI_Ar', fill=True, alpha=.10, color=COLORS['COHERENT_CsI_Ar'], linewidth=.8)
        for points in polygons(vertices, 'COHERENT_CsI_Ar'):
            points = np.vstack([points, points[0]]); ax.plot(points[:, 0], points[:, 1], 'k--', lw=1.05, zorder=6)
        paths['previous_mean_Ar'] = contour(ax, mean, '#777777', style='-.', width=1.2)
        contour(ax, asymmetric, COLORS['COHERENT_CsI_Ar'], width=1.8)
    paths['old_optimizer_mean_Ar'] = contour(axes[2], old, '#ba4545', style=':', width=1.5, zorder=3)
    axes[1].set_title('(b) COHERENT: two Ar error treatments', pad=10)
    axes[2].set_title('(c) COHERENT inner-gap zoom', pad=10)
    axes_style(axes[0]); axes_style(axes[1])
    axes_style(axes[2], limits=(-.15, .15, .02, .32), origin=False)
    axes[2].axvline(0, color='.65', ls=':', lw=.7, zorder=0)
    paper_roots = intersections(polygons(vertices, 'COHERENT_CsI_Ar'), close=True)
    for y in paper_roots[1:3]:
        axes[2].plot(0, y, 'kx', ms=5, mew=1., zorder=8)
    for y in intersections(paths['current_asymmetric_Ar'])[1:3]:
        axes[2].plot(0, y, 'o', color=COLORS['COHERENT_CsI_Ar'], ms=3.2, zorder=8)
    fig.suptitle('Fig.4 differences: corrected minima, error convention, and the previous search', fontsize=13, y=.96)
    fig.legend(handles=[Line2D([0], [0], color='k', ls='--', label='Paper Fig.4'),
                        Line2D([0], [0], color=COLORS['COHERENT_CsI_Ar'], lw=1.8, label='Corrected: asymmetric Ar'),
                        Line2D([0], [0], color='#777777', ls='-.', label='Corrected: mean-error Ar'),
                        Line2D([0], [0], color='#ba4545', ls=':', label='Before minimum fix: mean-error Ar')],
               loc='lower center', bbox_to_anchor=(.5, .08), ncol=2, frameon=False, fontsize=9)
    fig.text(.5, .025, 'Zoom: black crosses and blue dots show the two inner boundaries at u = 0. Solar has no calculated local contour.',
             ha='center', fontsize=8.7)
    save_figure(fig, out, 'fig4_difference_detail')

    summary = json.loads((SOURCE/'SUMMARY.json').read_text(encoding='utf8'))
    root_checks = []
    for scenario in ('current_asymmetric_Ar', 'previous_mean_Ar'):
        reference = next(r for r in summary['slice_comparison'] if r['scenario'] == scenario and r['epsilon_u'] == 0)
        drawn = intersections(paths[scenario])
        delta = float(np.max(abs(np.asarray(drawn)-reference['model_y_boundaries']))) if len(drawn) == 4 else None
        if delta is None or delta > 2e-4:
            raise ValueError('Drawn contour does not match audited u=0 roots')
        root_checks.append({'scenario': scenario, 'paper_y_at_u0': paper_roots,
                            'drawn_y_at_u0': drawn, 'audited_exact_y_at_u0': reference['model_y_boundaries'],
                            'max_contour_interpolation_difference': delta})
    arrays = {f'{name}_segment_{i}': points for name, segments in paths.items() for i, points in enumerate(segments)}
    np.savez_compressed(out/'contour_vertices.npz', **arrays)
    record = {'date': '2026-11-12', 'source_pdf_page': 23, 'source_figure': 'Fig4',
              'confidence': '90percent, two parameters', 'delta_chi2': LEVEL,
              'paper_plot_title_rounding': 'Paper title says4.6; text p22 specifies4.61',
              'surface_grid': [801, 801], 'axes': ['epsilon_ee_uV', 'epsilon_ee_dV'], 'array_order': '[y,x]',
              'minima': {'CONUS_plus': float(conus['minimum_chi2']), 'current_asymmetric_Ar': float(asymmetric['minimum_chi2']),
                         'previous_mean_Ar': float(mean['minimum_chi2'])},
              'optimizer_correction_constant_delta_chi2': offset,
              'same_raw_chi2_before_after_optimizer': True, 'root_checks': root_checks,
              'solar': 'Paper reference paths only; missing numerical flavor state and XENON acceptance tail prevent local NSI region',
              'style': {'main': 'Left reference paths; right local asymmetric-Ar/CONUS fills and solid edges, paper dashed outlines; solar green hatch is reference only',
                        'detail': 'Paper black dashed; current asymmetric Ar blue; corrected mean Ar gray dashdot; invalid old optimizer red dotted only in zoom'},
              'scientific_changes': False, 'paper_reproduction_certified': False,
              'inputs': plan['input_files'], 'generator': {'path': str(Path(__file__).relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(__file__)}}
    (out/'FIGURE_MANIFEST.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf8')
    for row in plan['input_files']:
        if sha(ROOT/row['path']) != row['sha256']:
            raise ValueError('Plotting changed an input')
    text = '# Fig.4重新绘制：论文与修正结果对照\n\n2026-11-12。只读取现有已核验数值表面和原PDF路径，没有重拟合、修改物理输入或改变置信阈值。\n\n'
    text += '[主图PNG](fig4_paper_vs_corrected.png) · [主图SVG](fig4_paper_vs_corrected.svg) · [分组/放大PNG](fig4_difference_detail.png) · [分组/放大SVG](fig4_difference_detail.svg)\n\n'
    text += '![论文与重绘对照](fig4_paper_vs_corrected.png)\n\n左图按原PDF矢量路径重绘；右图实线和橙/蓝填充为修正后计算，虚线为论文。蓝色计算采用当前Ar非对称误差。绿色斜线区仅为论文太阳联合参考，没有本地太阳NSI计算。\n\n'
    text += '![局部差异](fig4_difference_detail.png)\n\n放大图黑虚线为论文，蓝实线为非对称Ar，灰点划线为均误差Ar，红点线为最小值修复前的错误均误差结果。灰线与红线的原始χ²表面相同，只是二维最小值修复带来Δχ²增加'+f'{offset:.9f}'+'；两种Ar处理分开显示。\n\n'
    text += '| u=0时的边界 | d的四个交点 |\n|---|---|\n| 论文图形 | '+', '.join(f'{v:.6f}' for v in paper_roots)+' |\n'
    for row in root_checks:
        name = '当前非对称Ar' if row['scenario'] == 'current_asymmetric_Ar' else '修正后均误差Ar'
        text += '| '+name+' | '+', '.join(f'{v:.6f}' for v in row['audited_exact_y_at_u0'])+' |\n'
    text += '\n差异仍存在，尤其是COHERENT内外边界；本图没有宣称逐点复现论文。主图与放大图使用同一阈值Δχ²=4.61、同一u/d轴定义。原图轮廓只有PDF图形精度，801网格轮廓插值误差已与先前根求解结果核对。\n\n'
    text += '[来源/绘图与轮廓核验](FIGURE_MANIFEST.json) · [轮廓顶点](contour_vertices.npz) · [计划/备份](PLAN.json) · [绘图代码](../../examples/paper2601_chi2/plot_fig4_comparison.py)\n\n'
    text += '[联合分析完整核查](../paper2601_joint_audit_20261111/README.md) · [Fast专项检查](../paper2601_fast_audit_20261111/README.md) · [返回outputs](../README.md)\n'
    (out/'README.md').write_text(text, encoding='utf8')
    print(json.dumps({'figures': ['fig4_paper_vs_corrected.png', 'fig4_difference_detail.png'],
                      'max_contour_root_difference': max(r['max_contour_interpolation_difference'] for r in root_checks),
                      'unchanged_input_files': len(plan['input_files'])}))


if __name__ == '__main__':
    main()
