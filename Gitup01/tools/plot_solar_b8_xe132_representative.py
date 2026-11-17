"""Plot the user-selected Xe132 representative approximation against seven Xe isotopes.

The saved forward prediction already contains each isotope's full nuclear-table
SM amplitude and detector folding. Change only its absolute number of nuclei to
that of a pure Xe132 reference tonne. This linear target-count conversion is
exact within the existing model; solar flux and detector parameters stay fixed.
It is a plotting/comparison variant, not a change to the canonical seven-isotope
input or default prediction. New output directories only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2'
DEFAULT = ROOT/'outputs/solar_b8_sm/20261110_xe132_representative_plot'
FAMILIES = [('PandaX4T', 'PandaX4T_2024_US2'), ('XENONnT', 'XENONnT_2024_SolarB8')]
TEAL, GRAY, BG = '#007f78', '#606a79', '#a2aaba'


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def link(origin, target, label):
    return '['+label+'](<'+os.path.relpath(target, origin.parent).replace('\\', '/')+'>)'


def poisson_errors(counts):
    """68.268949% central Garwood intervals, with the zero-count lower limit."""
    n = np.asarray(counts, float)
    if np.any(n < 0) or np.any(n != np.floor(n)):
        raise ValueError('Poisson intervals require nonnegative integer observations')
    alpha = 1-.682689492137
    low = np.zeros_like(n)
    positive = n > 0
    low[positive] = .5*chi2.ppf(alpha/2, 2*n[positive])
    high = .5*chi2.ppf(1-alpha/2, 2*(n+1))
    return np.array([n-low, high-n])


def prepare(family, dataset):
    source = BASE/dataset/'RESULT.json'
    previous = read(source)
    prepared_path = BASE/dataset/'PREPARED_MODEL.nuclear.json'
    prepared = read(prepared_path)
    # Refuse to mix saved component counts with changed numerical resources.
    for key, item in prepared['resources'].items():
        if sha(Path(item['path'])) != item['sha256']:
            raise ValueError('changed saved-forward resource: '+key)
    package = ROOT/'data/experiments'/family/dataset
    arrays_path = package/'experiment.resources.npz'
    with np.load(arrays_path, allow_pickle=False) as a:
        A, masses, fractions = (a[key].copy() for key in
            ('target_mass_number', 'target_atomic_mass_u', 'target_number_fraction'))
        native_edges = ({run: a['cs2_edges_'+run].tolist() for run in previous['per_run']}
                        if family == 'XENONnT' else {})
    index = int(np.flatnonzero(A == 132)[0])
    mean_mass = float(masses@fractions)
    avogadro = previous['fixed_parameters']['constants.avogadro']['value']
    pure_nuclei = 1e6*avogadro/float(masses[index])
    old_target = next(t for t in prepared['actual_model']['targets'] if t['isotope_id'] == 'Xe132')
    factor = pure_nuclei/old_target['number_of_nuclei']
    independent_factor = mean_mass/(float(fractions[index])*float(masses[index]))
    np.testing.assert_allclose(factor, independent_factor, rtol=2e-15)
    natural = np.asarray(previous['counts'])
    components = {k: np.asarray(v) for k, v in previous['components'].items()}
    np.testing.assert_allclose(sum(components.values()), natural, rtol=2e-14)
    selected = {k: v for k, v in components.items() if k.endswith('/Xe132')}
    if len(selected) != len(previous['per_run']):
        raise ValueError('one Xe132 component required per run')
    per_run = {run: sum((v for key, v in selected.items() if '@'+run+'/' in key),
                       np.zeros_like(natural))*factor for run in previous['per_run']}
    representative = sum(per_run.values())
    np.testing.assert_allclose(representative, sum(selected.values())*factor, rtol=2e-15)
    refs = previous['references']
    observed, background = np.asarray(refs['observed']), np.asarray(refs['background'])
    assert natural.shape == representative.shape == observed.shape == background.shape
    errorbars = poisson_errors(observed)
    pct = 100*(representative/natural-1)
    ledger_path = ROOT/f'workflows/cevns-pyeft/runs/{family}/{dataset}/P00_SOURCE_REGISTER.yaml'
    ledger = read(ledger_path)
    sources = [row for row in ledger['sources'] if row['source_id'] in
               ('R01','R02','R04','R09','R13','R16','R17','R18','R20')]
    exposures = prepared['actual_model']['exposures_tyr']
    return {'family': family, 'dataset': dataset, 'seven_isotope_counts': natural.tolist(),
        'xe132_counts': representative.tolist(), 'xe132_per_run': {k:v.tolist() for k,v in per_run.items()},
        'seven_isotope_total': float(natural.sum()), 'xe132_total': float(representative.sum()),
        'relative_total_difference_percent': float(100*(representative.sum()/natural.sum()-1)),
        'relative_bin_difference_percent': pct.tolist(),
        'observed': observed.tolist(), 'observed_error_low_high': errorbars.tolist(),
        'reference_background': background.tolist(), 'reference_background_role': refs['role'],
        'observable_edges': previous['observable_edges'], 'native_cs2_edges_PE': native_edges,
        'run_exposures_tyr': exposures,
        'normalization': {'natural_Xe132_number_fraction': float(fractions[index]),
            'natural_mean_atomic_mass_u': mean_mass, 'Xe132_atomic_mass_u': float(masses[index]),
            'avogadro_mol_inverse': avogadro, 'avogadro_source': 'R13 SI defining constant; saved fixed_parameters.constants.avogadro',
            'reference_mass_kg': 1000., 'original_Xe132_nuclei_in_natural_tonne': old_target['number_of_nuclei'],
            'Xe132_nuclei_in_pure_tonne': pure_nuclei, 'nuclei_ratio': factor,
            'derivation': 'N132_pure=1e6*N_A/M132; S132_rep=S132_original*(N132_pure/N132_original)',
            'equivalent_ratio': 'mean_natural_atomic_mass/(natural_132_number_fraction*132_atomic_mass)',
            'flux_cm2_s': previous['fixed_parameters']['source.total_flux']['value'],
            'flux_changed': False, 'detector_changed': False, 'c_i_applied': False},
        'source_records': [{'file': str(source.relative_to(ROOT)), 'sha256': sha(source),
                            'locator': 'components/*@run/Xe132; counts; references; fixed_parameters.constants.avogadro/source.total_flux'},
            {'file': str(prepared_path.relative_to(ROOT)), 'sha256': sha(prepared_path),
             'locator': 'actual_model.targets; all resource SHA256 verified'},
            {'file': str(arrays_path.relative_to(ROOT)), 'sha256': sha(arrays_path),
             'locator': 'target_mass_number, target_atomic_mass_u, target_number_fraction; native PE edges'},
            {'file': str(ledger_path.relative_to(ROOT)), 'sha256': sha(ledger_path),
             'locator': 'sources R01/R02/R04/R09/R13/R16/R17/R18/R20; bibliographic metadata only'}],
        'citations': sources,
        'scope': 'same local nuclear Response convention; full target mass treated as Xe132; fixed original detector/exposure',
        'limits': ['seven-isotope comparison covers 99.8158% natural number abundance',
            'PandaX detector is a deterministic mean-yield approximation' if family=='PandaX4T'
             else 'XENONnT uses the official early-release YBe recasting response; summed bin ordinals have different run PE boundaries',
            'external nuclear author-source certification and exact paper-fit equivalence remain unresolved']}


def setup_style():
    font = Path('C:/Windows/Fonts/msyh.ttc')
    if not font.is_file():
        raise FileNotFoundError('Chinese figure font unavailable: '+str(font))
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=str(font)).get_name(),
        'font.size': 10, 'axes.unicode_minus': False, 'pdf.fonttype': 42,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.titleweight': 'bold', 'axes.labelsize': 10, 'legend.fontsize': 8.2,
        'savefig.facecolor': 'white', 'figure.facecolor': 'white'})


def plot_row(figure, spec, record):
    sub = spec.subgridspec(2, 2, height_ratios=[3.1, .95], hspace=.20, wspace=.22)
    signal_ax = figure.add_subplot(sub[0, 0])
    total_ax = figure.add_subplot(sub[0, 1], sharex=signal_ax)
    difference_ax = figure.add_subplot(sub[1, :])
    natural = np.asarray(record['seven_isotope_counts'])
    representative = np.asarray(record['xe132_counts'])
    b = np.asarray(record['reference_background'])
    panda = record['family']=='PandaX4T'
    edges = np.asarray(record['observable_edges']) if panda else np.arange(4)+.5
    centers = (edges[:-1]+edges[1:])/2
    xlabel = r'电子数 $N_e$（平均映射）' if panda else 'cS2 分箱序号（SR0 + SR1）'
    name = 'PandaX-4T US2' if panda else 'XENONnT'
    exposure = sum(record['run_exposures_tyr'])
    for i, ax in enumerate((signal_ax, total_ax)):
        addition = b if i else 0
        # Gray wider dashed line remains visible beneath the very close teal line.
        ax.stairs(natural+addition, edges, color=GRAY, ls=(0,(4,3)), lw=2.6,
                  label='七核素基准（核 Response）', zorder=2)
        ax.stairs(representative+addition, edges, color=TEAL, lw=1.65,
                  label=r'$^{132}$Xe 代表近似（核 Response）', zorder=3)
        if i:
            ax.stairs(b, edges, color=BG, lw=1.4, label='背景参考', zorder=1)
            ax.errorbar(centers, record['observed'], yerr=record['observed_error_low_high'],
                        fmt='o', color='#20252c', ms=4.0, capsize=2.7,
                        label='实验观测（68.27% Poisson）', zorder=4)
        ax.set_title(name+'：'+('信号 + 背景参考' if i else 'SM 信号'), loc='left', fontsize=11)
        ax.set_ylabel('事例数 / 箱')
        ax.set_ylim(bottom=0)
        ax.set_xlim(edges[0], edges[-1])
        ax.set_xticks(np.arange(4,8.1,1) if panda else [1,2,3])
        ax.grid(axis='y', color='#e6e9ef', lw=.7, zorder=0)
        ax.legend(loc='upper right' if i else 'lower left', frameon=True, framealpha=.94, edgecolor='#d8dce4')
        # The full-width difference axis below supplies the shared x label.
        ax.set_xlabel('')
    signal_ax.text(.98,.96, f'曝光 {exposure:.4g} t·yr\nXe132：{record["xe132_total"]:.3f} 事例\n七核素：{record["seven_isotope_total"]:.3f} 事例',
        transform=signal_ax.transAxes, ha='right', va='top', fontsize=9, color='#333e50')
    diff = np.asarray(record['relative_bin_difference_percent'])
    difference_ax.axhline(0, color='#a7adba', lw=1, ls='--')
    difference_ax.stairs(diff, edges, color=TEAL, lw=1.5, baseline=None)
    difference_ax.plot(centers,diff,'o',color=TEAL,ms=3.2)
    difference_ax.set_ylabel('信号差异 [%]', fontsize=9)
    difference_ax.set_xlabel(xlabel, fontsize=9)
    difference_ax.set_xlim(edges[0],edges[-1])
    difference_ax.set_xticks(np.arange(4,8.1,1) if panda else [1,2,3])
    difference_ax.set_ylim(min(-.15,float(diff.min())-.15),max(.15,float(diff.max())+.15))
    difference_ax.grid(axis='y',color='#e6e9ef',lw=.7)
    difference_ax.tick_params(labelsize=8.5)
    difference_ax.text(.99,.92, r'$100\,(S_i^{132}/S_i^{7\mathrm{iso}}-1)$'+f'；总数差 {record["relative_total_difference_percent"]:+.3f}%',
        transform=difference_ax.transAxes,ha='right',va='top',fontsize=8.5,
        bbox={'facecolor':'white','edgecolor':'none','alpha':.84,'pad':1.5})


def render(records, out):
    setup_style()
    for record in records:
        figure = plt.figure(figsize=(11.6,6.2))
        spec = figure.add_gridspec(1,1,left=.075,right=.985,bottom=.12,top=.88)
        plot_row(figure, spec[0], record)
        figure.suptitle(r'固定 SM 与太阳通量：$^{132}$Xe 代表近似 vs. 七核素核响应计算',y=.97,fontsize=13)
        foot = 'PandaX：nominal Qy 平均映射，无探测器展宽。' if record['family']=='PandaX4T' else 'XENONnT：SR0/SR1 按箱序号相加；各运行期 PE 边界不同。'
        figure.text(.075,.025,foot+' 通量、曝光、接受度不变；原始数据和引文见同目录 README。',fontsize=8,color='#596478')
        for suffix in ('png','pdf'):
            figure.savefig(out/(record['family']+'_xe132_comparison.'+suffix),dpi=200)
        plt.close(figure)
    figure=plt.figure(figsize=(12.3,10.7))
    spec=figure.add_gridspec(2,1,left=.07,right=.985,bottom=.075,top=.92,hspace=.28)
    for i, record in enumerate(records):
        plot_row(figure,spec[i],record)
    figure.suptitle(r'太阳 $^8$B 标准模型：$^{132}$Xe 代表近似',fontsize=16,y=.982)
    figure.text(.5,.946,r'真实核 Response；固定 $\Phi_{^8\mathrm{B}}=5.46\times10^6\ \mathrm{cm}^{-2}\mathrm{s}^{-1}$；无逐箱校准',
                ha='center',fontsize=10,color='#455268')
    figure.text(.07,.022,'PandaX：Qy 平均映射，无探测器展宽。XENONnT：按箱序号合并 SR0/SR1，各运行期 PE 边界不同。',fontsize=8.4,color='#596478')
    for suffix in ('png','pdf'):
        figure.savefig(out/('xe132_comparison.'+suffix),dpi=200)
    plt.close(figure)


def report(records, out):
    origin=out/'README.md'
    text='# Xe132代表近似：SM事例数比较图\n\n用户要求“对应的结果图需要绘制一下”。采用整份靶质量视为Xe132的代表近似；固定原有通量、曝光和探测器处理。七核素主计算与onboarding保持原状。\n\n'
    text+='[总图 PNG](xe132_comparison.png) · [总图 PDF](xe132_comparison.pdf) · [完整逐箱结果/来源](RESULTS.json) · [核对](VALIDATION.json)\n\n'
    text+='| 实验 | Xe132近似 [事例] | 七核素 [事例] | 总数差 | 分箱差最大绝对值 | 图 |\n|---|---:|---:|---:|---:|---|\n'
    for r in records:
        text+='| '+r['family']+' | '+f'{r["xe132_total"]:.9f}'+' | '+f'{r["seven_isotope_total"]:.9f}'+' | '+f'{r["relative_total_difference_percent"]:+.4f}%'+' | '+f'{max(abs(x) for x in r["relative_bin_difference_percent"]):.4f}%'+' | [PNG]('+r['family']+'_xe132_comparison.png) / [PDF]('+r['family']+'_xe132_comparison.pdf) |\n'
    text+='\n绿色实线为Xe132近似；灰色虚线为七核素核Response预测；浅灰线为背景参考；黑点及误差棒为实验观测与68.27% Garwood区间。下方显示相对七核素信号的逐箱百分比差异，便于看清接近重合的两条曲线。\n\n'
    text+='## 核数换算与计算范围\n\n'
    text+='现有逐核素信号已经包含真实核表、振幅、截面、源与探测器折叠。利用事件数对靶核数的线性关系：\n\n$$\nN_{132}^{\\rm pure}=\\frac{10^6N_{\\rm A}}{M_{132}},\\qquad S_i^{132,\\rm rep}=S_i^{132,\\rm natural}\\frac{N_{132}^{\\rm pure}}{N_{132}^{\\rm natural}}.\n$$\n\n'
    text+='这里1吨=10⁶g，M132取NIST原子质量的g/mol数值约定；不是把原26.9086%的那部分计数直接当全靶信号。该换算只改变靶核数，不缩放通量或用实验观测校准。没有重新运行散射积分，复用已收敛的Xe132逐核素结果。\n\n'
    for r in records:
        n=r['normalization']
        text+='### '+r['dataset']+'：实际输入与出处\n\n'
        text+='| 数值/数组 | 值/范围与作用 | 具体出处 |\n|---|---|---|\n'
        text+=f'| Xe132原子质量 | {n["Xe132_atomic_mass_u"]:.12g} u | R09 NIST Xe132行；原包target_atomic_mass_u |\n'
        text+=f'| Xe132天然数丰度 | {n["natural_Xe132_number_fraction"]:.12g} | R09 Xe132行；原包target_number_fraction |\n'
        text+=f'| 天然平均摩尔质量 | {n["natural_mean_atomic_mass_u"]:.12g} g/mol | R09九行原数丰度×原子质量求和 |\n'
        text+=f'| 阿伏伽德罗常量 | {n["avogadro_mol_inverse"]:.12g} mol⁻¹ | R13 SI定义值；原RESULT的fixed_parameters.constants.avogadro |\n'
        text+=f'| 核数换算因子 | {n["nuclei_ratio"]:.12g} | 上式；原核数由实际PREPARED_MODEL读取，双公式交叉核验 |\n'
        text+='| 信号 | '+str(len(r['xe132_counts']))+'箱，events/bin | 下列RESULT的components/*@run/Xe132；本表核数换算 |\n'
        text+='| 观测和背景 | '+str(r['observed'])+'；背景'+str(r['reference_background'])+' | '+('R01 2411.11749v1 p7 Fig.1左，数字化拟合背景仅作参考' if r['family']=='PandaX4T' else 'R17官方早期发布；原观测表与ac/er/rg模板；每run边界见下方')+' |\n'
        text+='| 探测器 | '+('R02 p5 Fig.4下图Qy、p3 Fig.1 Total(US2)，R01式(15)均值映射' if r['family']=='PandaX4T' else 'R17官方YBe单能基底，中位Ly/Qy；不另乘效率')+' | 原forward保持不变 |\n'
        for row in r['source_records']:
            text+='\n'+link(origin,ROOT/row['file'],Path(row['file']).name)+'：'+row['locator']+'；SHA256 `'+row['sha256']+'`。\n'
        if r['native_cs2_edges_PE']:
            text+='\n原生cS2箱界[PE]：'+json.dumps(r['native_cs2_edges_PE'],ensure_ascii=False)+'；本图仅按序号合并，不构造一套共同PE边界。\n'
        text+='\n限制：'+'；'.join(r['limits'])+'。\n\n'
    text+='## 标准参考文献\n\n'
    citations={s['source_id']:s for r in records for s in r['citations']}
    for sid,s in sorted(citations.items()):
        text+='['+sid+'] '+s['citation']+'\n\n'
    text+='## 复画与文件归属\n\n'+link(origin,Path(__file__),'绘图脚本')+'读取RESULT/NPZ并在新目录保存PNG、PDF、逐箱TSV/JSON和来源。运行：\n\n```powershell\npython -B tools/plot_solar_b8_xe132_representative.py --output <新的输出目录>\n```\n\n'+link(origin,ROOT/'outputs/solar_b8_sm/README.md','上级结果导航')+' · '+link(origin,BASE/'README.md','原七核素核Response运行')+'\n'
    origin.write_text(text,encoding='utf8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=DEFAULT)
    args=ap.parse_args()
    records=[prepare(*item) for item in FAMILIES]
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    result={'scope':'postprocessing plot of previously computed Xe132 components with pure-reference-tonne nucleus counts',
        'user_request':'那对应的结果图需要绘制一下','canonical_seven_isotope_input_changed':False,
        'plot_script_sha256':sha(Path(__file__)),'datasets':records}
    save(out/'RESULTS.json',result)
    for r in records:
        np.savetxt(out/(r['family']+'_events_by_bin.tsv'),np.column_stack([np.arange(1,len(r['xe132_counts'])+1),
            r['xe132_counts'],r['seven_isotope_counts'],r['relative_bin_difference_percent'],
            r['observed'],r['reference_background']]),delimiter='\t',
            header='bin Xe132_SM_events seven_isotope_SM_events signal_difference_percent observed_events reference_background_events')
    render(records,out)
    report(records,out)
    checks={'status':'PASS','source_resource_hashes':'all declared saved-forward resources match current files',
        'original_isotope_components_sum_to_signal':'PASS','pure_nucleus_ratio_two_independent_formulas':'PASS',
        'per_run_Xe132_sum_matches_total':'PASS','observed_nonnegative_integer_counts':'PASS',
        'plot_values':'exactly the recorded arrays in RESULTS.json and TSV; no paper blue reference or calibration curve',
        'scope':'linear target-count postprocessing; no new physics-core tests needed',
        'outputs':[p.name for p in out.iterdir() if p.is_file()]}
    save(out/'VALIDATION.json',checks)
    print(json.dumps({'output':str(out),'totals':{r['family']:r['xe132_total'] for r in records}},ensure_ascii=False))


if __name__=='__main__':
    main()
