"""Create-only, reproducible inputs for the independent 2601.19883 single-bin route.

Run with a Python containing numpy and pdfplumber. This is an offline preparation
tool, never imported by Runtime. It neither edits nor sums the multibin package.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def prepare(destination):
    import pdfplumber
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('create-only: choose a new destination')
    panda_pdf = ROOT/'docs/references/Solar_CEvNS/2407.10892v3.pdf'
    xenon_pdf = ROOT/'docs/references/Solar_CEvNS/2408.02877v2.pdf'
    with pdfplumber.open(panda_pdf) as pdf:
        panda_curves = pdf.pages[2].curves
    with pdfplumber.open(xenon_pdf) as pdf:
        xenon_curve = pdf.pages[3].curves[9]
    # [R2] Fig.1 tick calibration: x linear in keVnr, y logarithmic in epsilon.
    panda_axis = dict(x_at_0p5_keV=100.186975605259, x_pt_per_keV=65.73696,
                      y_at_1e_minus3=415.5590709383, y_pt_per_decade=41.074305474712)
    def panda_total(index, lo, hi):
        curve = panda_curves[index]
        if curve['stroking_color'] != 0.0:
            raise ValueError('expected black Total path')
        xy = np.array(curve['pts'])
        # PDF closes this open plotting path by repeating its final vertex.
        xy = xy[np.r_[True, np.any(np.diff(xy, axis=0) != 0, axis=1)]]
        energy = .5+(xy[:, 0]-panda_axis['x_at_0p5_keV'])/panda_axis['x_pt_per_keV']
        if np.any(np.diff(energy) <= 0) or not energy[0] < lo < hi < energy[-1]:
            raise ValueError('unexpected Fig.1 path/support')
        grid = np.r_[lo, energy[(energy > lo) & (energy < hi)], hi]
        # Boundary intersections are made in the native PDF (log efficiency) coordinates.
        y = np.interp(grid, energy, xy[:, 1])
        eff = 10**(-3+(panda_axis['y_at_1e_minus3']-y)/panda_axis['y_pt_per_decade'])
        return np.column_stack([grid, eff]), {'curve_index': index, 'dash': curve.get('dash'),
                                             'native_pdf_points': xy.tolist(), 'axis': panda_axis}
    paired, paired_extraction = panda_total(6, 1.1, 3.)
    us2, us2_extraction = panda_total(9, .3, 3.)
    # [R3] PDF p4 Fig.1 black combined acceptance, both axes linear. The PDF
    # contains vertices below the displayed lower frame; keep their visibility flag.
    xaxis = dict(x_at_0p5_keV=88.59907, x_pt_per_keV=84.6317616066,
                 y_at_0p1=140.79474197159993, y_at_0p5=61.10292846699997,
                 lower_frame_top=160.51846633679997)
    xy = np.array(xenon_curve['pts'])
    energy = .5+(xy[:, 0]-xaxis['x_at_0p5_keV'])/xaxis['x_pt_per_keV']
    eff = .1+(xaxis['y_at_0p1']-xy[:, 1])/((xaxis['y_at_0p1']-xaxis['y_at_0p5'])/.4)
    visible = ((energy >= .5) & (xy[:, 1] <= xaxis['lower_frame_top'])).astype(int)
    xenon = np.column_stack([energy, eff, visible])
    if xenon_curve['stroking_color'] != 0.0 or np.any(np.diff(energy) <= 0):
        raise ValueError('unexpected XENONnT combined path')
    # [R6,R7] Independent snapshots of the adopted source and target values.
    original = ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'
    source_path = original/'b8_bahcall1996_official.txt'
    numeric = []
    for line in source_path.read_text(encoding='utf8').splitlines():
        try:
            row = [float(x) for x in line.split()]
        except ValueError:
            continue
        if len(row) == 4:
            numeric.append(row[:2])
    spectrum = np.array(numeric)
    isotope_path = original/'xenon_natural_isotopes_nist_v2.txt'
    isotopes = np.loadtxt(isotope_path)
    destination.mkdir(parents=True)
    tables = {
        'b8_source.txt': (spectrum, '[R6] Bahcall et al., PRC 54 (1996) 411; official b8spectrum.txt columns 1,2; MeV, MeV^-1; no renormalization'),
        'xe_isotopes.txt': (isotopes, '[R7] NIST Xe isotopic composition; A, atomic_mass_u, original_number_fraction; no subset renormalization'),
        'pandax_paired_total.txt': (paired, '[R2] Bo et al., PRL 133 (2024) 191001, 2407.10892v3 PDF p3 Fig.1 Total paired black solid; T_keVnr, epsilon'),
        'pandax_us2_total.txt': (us2, '[R2] Bo et al., PRL 133 (2024) 191001, 2407.10892v3 PDF p3 Fig.1 Total US2 black dashed; T_keVnr, epsilon'),
        'xenonnt_combined.txt': (xenon, '[R3] Aprile et al., PRL 133 (2024) 191002, 2408.02877v2 PDF p4 Fig.1 black combined; T_keVnr, epsilon, visible_in_frame; NO tail extension'),
    }
    for name, (array, header) in tables.items():
        np.savetxt(destination/name, array, fmt='%.15g', header=header+'\nSee analysis.input.json for full citation, PDF hash, native coordinates and interpolation.')
    references = {
        'R1': {'citation': 'LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.', 'url': 'https://arxiv.org/abs/2601.19883v2', 'file': 'docs/references/General_CEvNS/2601.19883v2.pdf', 'locator': 'PDF p19 Sec.VI.A Eq.(84): recoil rate; PDF p20 Eqs.(87),(88): single-bin integration and independent 12% pulls'},
        'R2': {'citation': 'BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3.', 'url': 'https://arxiv.org/abs/2407.10892v3', 'file': panda_pdf.relative_to(ROOT).as_posix(), 'locator': 'PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI'},
        'R3': {'citation': 'APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2.', 'url': 'https://arxiv.org/abs/2408.02877v2', 'file': xenon_pdf.relative_to(ROOT).as_posix(), 'locator': 'PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr'},
        'R4': {'citation': 'LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025.', 'url': 'https://arxiv.org/abs/2502.10702v2', 'file': 'docs/references/General_CEvNS/2502.10702v2.pdf', 'locator': 'PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted'},
        'R5': {'citation': 'LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024.', 'url': 'https://arxiv.org/abs/2409.04703v2', 'file': 'docs/references/General_CEvNS/2409.04703v2.pdf', 'locator': 'PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2'},
        'R6': {'citation': 'BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06.', 'url': 'https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt', 'direct_local_source': source_path.relative_to(ROOT).as_posix(), 'sha256': sha(source_path), 'locator': '829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained'},
        'R7': {'citation': 'NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06.', 'url': 'https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe', 'direct_local_source': isotope_path.relative_to(ROOT).as_posix(), 'sha256': sha(isotope_path), 'locator': 'nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses'},
        'R8': {'citation': 'CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified.', 'file': 'data/responses/responses_all.json', 'locator': 'Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor'},
        'R9': {'citation': 'Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z].', 'url': 'https://arxiv.org/abs/2411.11749v1', 'locator': 'sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2'},
        'R10': {'citation': 'BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z].', 'url': 'https://www.bipm.org/en/publications/si-brochure', 'locator': 'Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants'},
    }
    for ref in references.values():
        if ref.get('file'):
            ref['sha256'] = sha(ROOT/ref['file'])
    tail_start = float(energy[-1])
    card = {
        'schema': 'solar_b8_singlebin_analysis/1', 'analysis_id': 'solar_b8_singlebin_2601_19883',
        'version': '3.2.1', 'date': '2026-11-11', 'claim': 'project SM nuclear-response calculation using R1 single-bin method; not author-code equivalence',
        'physics': {'flux_cm2_s': 5.46e6, 'flux_source': 'R5 Eq.(29), cross-reference choice for R1',
                    'sin2thetaW': .23857, 'sin2thetaW_source': 'R9', 'seconds_per_year': 31557600.,
                    'avogadro_per_mol': 6.02214076e23, 'constants_source': 'R10',
                    'isotope_keys': ['Xe128','Xe129','Xe130','Xe131','Xe132','Xe134','Xe136'],
                    'nuclear_resource': 'data/responses/responses_all.json', 'nuclear_sha256': sha(ROOT/'data/responses/responses_all.json'),
                    'nuclear_source': 'R8 direct local adoption; external provenance unresolved',
                    'target_policy': 'original nine-row denominator; seven isotope counts; no renormalization',
                    'interpolation': 'piecewise linear in T and epsilon after native PDF extraction; outside tabulation forbidden',
                    'source_interpolation': 'piecewise linear; use original rounded density, no extra normalization',
                    'no_second_ROI_cut': True, 'no_ci': True},
        'samples': {
            'PandaX_paired': {'dataset_id': 'PandaX4T_2024_PAIRED__singlebin2601', 'experiment_slug': 'PandaX4T', 'T_bounds_keVnr': [1.1,3.], 'exposure_tyr': 1.20, 'efficiency': 'pandax_paired_total.txt', 'source': 'R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II', 'coverage': 'COMPLETE'},
            'PandaX_US2': {'dataset_id': 'PandaX4T_2024_US2__singlebin2601', 'experiment_slug': 'PandaX4T', 'T_bounds_keVnr': [.3,3.], 'exposure_tyr': 1.04, 'efficiency': 'pandax_us2_total.txt', 'source': 'R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window', 'coverage': 'COMPLETE'},
            'XENONnT': {'dataset_id': 'XENONnT_2024_SolarB8__singlebin2601', 'experiment_slug': 'XENONnT', 'T_bounds_keVnr': [.5,3.], 'exposure_tyr': 3.51, 'efficiency': 'xenonnt_combined.txt', 'source': 'R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II', 'coverage': 'MISSING_TAIL', 'verified_upper_keVnr': tail_start, 'missing_interval_keVnr': [tail_start,3.], 'clipped_low_vertices': 'native PDF path exists below plotted frame; numeric extraction verified, visually clipped', 'allowed_tail_modes': ['bounded','flat_sensitivity'], 'flat_sensitivity': 'PROJECT ASSUMPTION: epsilon(T>last)=epsilon(last); not an experimental input or official full response'},
        },
        'files': {name: {'sha256': sha(destination/name), 'shape': list(array.shape), 'range_first_column': [float(array[0,0]),float(array[-1,0])], 'first_row': array[0].tolist(), 'last_row': array[-1].tolist()} for name,(array,_) in tables.items()},
        'extraction': {'PandaX_paired': paired_extraction, 'PandaX_US2': us2_extraction,
                       'XENONnT': {'curve_index': 9, 'axis': xaxis, 'native_pdf_points': xy.tolist(), 'pdf_version': '2408.02877v2', 'tail_extended': False}},
        'references': references,
    }
    write_json(destination/'analysis.input.json', card)
    write_json(destination/'fitted_yields.json', {
        'schema': 'solar_b8_fitted_signal_yields/1', 'statistics': 'R1 PDF p20 Eq.(88); independent Gaussian normalization pulls, not raw Poisson',
        'data_origin': 'R4 PDF p13 Table II rounded sigmas, cross-checked fitted yields in R2/R3; 2601 percentage values have small rounding differences',
        'samples': {k: {'D':d,'sigma_stat':s,'pull_sigma':.12,'unit':'events','meaning':'fitted_signal_yield','source':src}
                    for k,d,s,src in [('PandaX_paired',3.5,1.3,'R2 abstract; R4 Table II'),('PandaX_US2',75.,28.,'R2 abstract; R4 Table II'),('XENONnT',10.7,3.95,'R3 Table I: asymmetric -4.2/+3.7 averaged; R4 Table II')]},
        'external_comparison_only': {'source': 'R4 Table II; flux 5.16e6, shared pull Eq.(E8)', 'SM_events': [2.4,44.3,11.2], 'do_not_use_as_project_prediction_or_normalization': True},
    })
    (destination/'README.md').write_text('# Solar B8：独立单 bin 输入（2601.19883v2）\n\n'
        '主线入口：[修订 onboarding](../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md)。\n\n'
        '[analysis.input.json](analysis.input.json)是本分析专属 JSON 格式（不是三文件 Experiment Input Package），拥有全部物理输入、标准引文、精确页/图/式、原始PDF向量和哈希；Runtime仅显式读取本目录及用户选定的共享核表。\n\n'
        '| 文件 | 含义与来源 |\n|---|---|\n'
        '| [b8_source.txt](b8_source.txt) | R6 官网829点前两列；MeV, MeV⁻¹；不含总通量 |\n'
        '| [xe_isotopes.txt](xe_isotopes.txt) | R7 NIST九行 A/原子质量/数丰度；不重归一 |\n'
        '| [pandax_paired_total.txt](pandax_paired_total.txt) | R2 v3 p3 Fig.1黑实线；T,总效率；1.1–3 keVnr |\n'
        '| [pandax_us2_total.txt](pandax_us2_total.txt) | R2 v3 p3 Fig.1黑虚线；T,总效率；0.3–3；已含ROI |\n'
        '| [xenonnt_combined.txt](xenonnt_combined.txt) | R3 v2 p4 Fig.1黑线；T,总接受度,可见标记；末端约2.77 keVnr，未延伸到3 |\n'
        '| [fitted_yields.json](fitted_yields.json) | R2/R3拟合信号、R4 Table II取整误差；R1 Eq.88三个独立12% pull；不含逐箱D/B |\n\n'
        '准备：[prepare_solar_b8_singlebin.py](../../../tools/prepare_solar_b8_singlebin.py)，仅创建新目录；计算：[solar_singlebin.py](../../../cevns_pyeft/experiments/solar_singlebin.py)。数值文件不从多bin NPZ、Qy或响应基底读入，后续修改须独立更新本参数卡和新结果。\n', encoding='utf8')
    print('Created', destination, {k:v['shape'] for k,v in card['files'].items()}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=DEFAULT)
    prepare(parser.parse_args().destination)
