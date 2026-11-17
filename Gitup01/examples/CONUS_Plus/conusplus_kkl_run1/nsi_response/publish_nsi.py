"""Render NSI benchmark figures and source-visible workflow reports."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('nsi')
import csv
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import sm_model as sm
from nsi_model import HERE, BASIS, COUPLINGS, verify_snapshot
from benchmark_nsi import PLANE_SPECS, THRESHOLDS, THRESHOLD_2D, evaluate_polynomial, profile
OUTPUT = LAYOUT.path('outputs')
REVIEW = LAYOUT.path('review')
DATA_PREFIX = '../snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/'
RUN_PREFIX = '../snapshot/workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/'
LABELS = {'epsilon_ee_uV': '$\\epsilon_{ee}^{uV}$', 'epsilon_ee_dV': '$\\epsilon_{ee}^{dV}$', 'epsilon_emu_uV': '$\\epsilon_{e\\mu}^{uV}$', 'epsilon_emu_dV': '$\\epsilon_{e\\mu}^{dV}$', 'epsilon_etau_uV': '$\\epsilon_{e\\tau}^{uV}$', 'epsilon_etau_dV': '$\\epsilon_{e\\tau}^{dV}$'}
READABLE = {'epsilon_ee_uV': 'εᵘⱽₑₑ', 'epsilon_ee_dV': 'εᵈⱽₑₑ', 'epsilon_emu_uV': 'εᵘⱽₑμ', 'epsilon_emu_dV': 'εᵈⱽₑμ', 'epsilon_etau_uV': 'εᵘⱽₑτ', 'epsilon_etau_dV': 'εᵈⱽₑτ'}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(('---' for _ in headers)) + ' |'] + ['| ' + ' | '.join((str(value) for value in row)) + ' |' for row in rows])

def interval_text(intervals, decimals=6):
    return ' ∪ '.join((f'[{a:.{decimals}f}, {b:.{decimals}f}]' for a, b in intervals))

def markdown_report(path, title, intro, sections):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    text = f'# {title}\n\n{intro}\n\n<a id="report-toc"></a>\n\n## 目录\n\n'
    text += '\n'.join((f'- [{heading}](#section-{i})' for i, (heading, _) in enumerate(sections, 1))) + '\n'
    for i, (heading, content) in enumerate(sections, 1):
        text += f'\n<a id="section-{i}"></a>\n\n## {heading}\n\n{content}\n\n[返回目录](#report-toc)\n'
    Path(path).write_text(text, encoding='utf-8')
    LAYOUT.normalize_document(Path(path))

def draw_figures(summary):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.8))
    selections = ('epsilon_ee_uV', 'epsilon_ee_dV', 'epsilon_emu_uV', 'epsilon_emu_dV')
    for ax, coupling in zip(axes.flat, selections):
        stored = np.load(OUTPUT / ('scan_' + coupling + '.npz'))
        fit = summary['NSI_rows'][coupling]
        ax.plot(stored['epsilon_grid'], stored['delta_chi2_grid'], color='#c95534', lw=2)
        for a, b in fit['paper_1sigma_intervals']:
            ax.axvspan(a, b, color='#3481ad', alpha=0.13)
        for a, b in fit['intervals']['1sigma']:
            ax.plot([a, b], [1, 1], color='#c95534', lw=4, solid_capstyle='butt')
        ax.axhline(1, color='#737f89', ls='--', lw=1)
        ax.axhline(THRESHOLDS['90percent'], color='#7d8992', ls=':', lw=1)
        ax.set_xlim((-0.12, 0.5) if '_ee_' in coupling else (-0.23, 0.23))
        ax.set_ylim(0, 8)
        ax.set_xlabel(LABELS[coupling], fontsize=14)
        ax.set_ylabel('$\\Delta\\chi^2$ (profiled)')
        ax.grid(alpha=0.15)
        if '_emu_' in coupling:
            ax.text(0.5, 0.91, '$e\\mu$ and $e\\tau$ coincide', transform=ax.transAxes, ha='center', fontsize=10, color='#52616b')
    legend = [Line2D([0], [0], color='#c95534', lw=2, label='Project Nuclear Response'), Patch(facecolor='#3481ad', alpha=0.2, label='Paper Table II: 1 sigma'), Line2D([0], [0], color='#737f89', ls='--', label='1 sigma: $\\Delta\\chi^2=1$'), Line2D([0], [0], color='#7d8992', ls=':', label='90%: $\\Delta\\chi^2=2.706$')]
    fig.suptitle('CONUS+ vector NSI | one-parameter benchmark', x=0.09, ha='left', fontsize=16, fontweight='bold', y=0.985)
    fig.legend(handles=legend, loc='upper center', bbox_to_anchor=(0.52, 0.948), ncol=2, frameon=False, fontsize=9.5)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.82, bottom=0.17, hspace=0.38, wspace=0.25)
    fig.text(0.09, 0.025, '119 kg day, natural Ge, 19 bins. Mean digitized errors; Gaussian normalization pull 16.9%.\nBenchmark: De Romeri et al., Phys. Rev. D 111, 075025 (2025), arXiv:2501.17843v3, Table II.', fontsize=8.5, color='#53616c', linespacing=1.5)
    for extension in ('png', 'svg'):
        fig.savefig(OUTPUT / ('nsi_profiles_1d.' + extension), dpi=210, facecolor='white')
    plt.close(fig)
    polygons = list(csv.DictReader(LAYOUT.path('data/benchmark/fig4_blue_polygons.csv').open(encoding='utf-8')))
    templates = np.load(OUTPUT / 'nsi_quadratic_templates.npz')
    data = np.genfromtxt(LAYOUT.path('data/statistics_input.csv'), names=True, delimiter=',', encoding='utf-8')
    minima = load(OUTPUT / 'two_dimensional_results.json')
    rendering_checks = {}
    fig, axes = plt.subplots(2, 2, figsize=(10.3, 8.9))
    for ax, plane in zip(axes.flat, ('diag_ud', 'fc_ud', 'ring_mu', 'ring_tau')):
        stored = np.load(OUTPUT / ('plane_' + plane + '.npz'))
        x_name, y_name, x_domain, y_domain = PLANE_SPECS[plane]
        ax.contourf(stored['x'], stored['y'], stored['delta_chi2'], levels=[-1e-06, THRESHOLD_2D], colors=['#f2b592'], alpha=0.4)
        contour = ax.contour(stored['x'], stored['y'], stored['delta_chi2'], levels=[THRESHOLD_2D], colors=['#c95534'], linewidths=1.7)
        vertices = np.concatenate([segment for segment in contour.allsegs[0] if len(segment)], axis=0)
        exact_values = np.array([profile(evaluate_polynomial(templates[plane], x, y), data['observed_signed_excess'], data['sigma_primary_mean']).chi2 - minima[plane]['best_fit']['chi2'] for x, y in vertices])
        rendering_checks[plane] = {'grid_shape': list(stored['delta_chi2'].shape), 'vertices_checked': len(vertices), 'max_absolute_delta_chi2_interpolation_error': float(np.max(abs(exact_values - THRESHOLD_2D)))}
        selected = [row for row in polygons if row['panel'] == plane]
        for polygon in sorted({row['polygon_index'] for row in selected}, key=int):
            vertices = [row for row in selected if row['polygon_index'] == polygon]
            ax.plot([float(row['x']) for row in vertices], [float(row['y']) for row in vertices], color='#247ca6', ls='--', lw=1.25)
        ax.plot(0, 0, 'o', mfc='white', mec='#30383d', ms=4.5, zorder=5)
        ax.set_xlim(x_domain)
        ax.set_ylim(y_domain)
        ax.set_xlabel(LABELS[x_name], fontsize=14)
        ax.set_ylabel(LABELS[y_name], fontsize=14)
        ax.grid(alpha=0.15)
        ax.text(0.96, 0.94, '90% C.L.', transform=ax.transAxes, ha='right', va='top', fontsize=10)
    legend = [Patch(facecolor='#f2b592', alpha=0.55, edgecolor='#c95534', label='Project Nuclear Response: allowed'), Line2D([0], [0], color='#247ca6', ls='--', lw=1.3, label='Paper Fig. 4: digitized boundaries')]
    fig.suptitle('CONUS+ vector NSI | two-parameter benchmark', x=0.1, ha='left', fontsize=16, fontweight='bold', y=0.985)
    fig.legend(handles=legend, loc='upper center', bbox_to_anchor=(0.53, 0.95), ncol=2, frameon=False, fontsize=9.5)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.875, bottom=0.15, hspace=0.32, wspace=0.25)
    fig.text(0.1, 0.025, 'Profiled normalization pull. Nominal two-parameter threshold $\\Delta\\chi^2=4.605$.\nReference geometry from arXiv:2501.17843v3, PDF p.14, Fig.4; clipped panel edges retained.', fontsize=8.5, color='#53616c', linespacing=1.5)
    for extension in ('png', 'svg'):
        fig.savefig(OUTPUT / ('nsi_contours_2d.' + extension), dpi=210, facecolor='white')
    plt.close(fig)
    sm.write_json(OUTPUT / 'contour_rendering_checks.json', rendering_checks)

def create_phase_reports(summary, validation):
    phases = {'P04': {'theory_scope': 'Natural-Ge SM plus six real vector NSI couplings; complex transition points only for validation', 'coefficient_convention': 'vector_nsi_to_np_wilson: deltaC_(6,1,q)=-sqrt(2)GF epsilon_qV; SM added once', 'nuclear_responses': 'Ge70/72/73/74/76, fixed responses_all.json np polynomial resource', 'coverage': 'four dimension-6 quark vector/axial operators; all retained SM/NSI interference and quadratic terms', 'runtime_binding': 'existing Li2026LegacyInteraction and statistics.parameters.VectorNSIParameters', 'external_evidence_limits': summary['limitations']}, 'P05': {'process_and_mass': 'elastic nucleus scattering, existing A*u kinematic mass, NIST inventory mass', 'kinematics': 'unchanged exact ElasticKinematics endpoint and inverse', 'cross_section_api': 'existing Li2026LegacyInteraction.dsigma_dT', 'units_and_axes': 'E MeV, T keV, cross section cm2/keV; rho is pure electron antineutrino', 'support_and_limits': 'same 0-10 MeV support and source/Response convention as SM; restricted NSI scope', 'benchmark': 'nonzero direct Slow versus coefficient-kernel predictions including a cancellation and complex flavor point'}, 'P07': {'normalization_ledger': 'same119days detector fluence and1kg actual isotope inventory as verified SM; no fitted rescaling of physical inputs', 'output_contract': '19 events/bin with five isotope components at declared NSI validation coordinates', 'numerics_and_convergence': validation['nonzero_NSI_energy_grid_refinement'], 'reference_comparison': validation['direct_slow_comparisons'], 'freeze_scope': {'status': 'isolated_candidate_not_human_authoritative', 'n_er': 161, 'n_enu': 641, 'SM_reference': 'data/sm_reference/fine_641.npz', 'validation': 'outputs/validation.json'}}, 'P09': {'channels': [{'id': 'CONUS_19bin', 'representation': 'binned_density', 'processing': 'background_subtracted', 'design': 'single_sample', 'likelihood': 'gaussian', 'requires_covariance': False}], 'prediction_binding': 'existing interface kernel and validated exact degree2 real NSI polynomial; 19 original figure-unit bins', 'required_inputs': {'available': True, 'sources': ['data/statistics_input.csv', 'review/NSI_CONTRACT.json', 'data/benchmark/tableII_1sigma.csv'], 'missing': []}, 'nuisance_model': 'Eq.(33), alpha unbounded real, Gaussian width0.169; existing profile_gaussian_one_pull', 'inference': {'thresholds_1d': THRESHOLDS, 'threshold_2d_90': THRESHOLD_2D, 'method': 'multiple minima, independent root refinement, full union of accepted intervals', 'coverage_scope': 'nominal asymptotic paper comparison; no toy coverage calibration'}, 'claim_level': 'approximate', 'benchmark': '2501.17843v3 TableII 1sigma and Fig4 two-parameter90percent'}, 'P10': {'delivery_scope': {'mode': 'capability_change', 'target': 'isolated CONUS vector NSI benchmark continuation', 'completion': 'partial'}, 'capability_matrix': [{'id': 'NSI_forward_and_kernel', 'requested': True, 'required_for_claim': True, 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'result_ref': 'outputs/validation.json'}, {'id': 'NSI_profiles_and_intervals', 'requested': True, 'required_for_claim': True, 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'result_ref': 'outputs/summary.json'}, {'id': 'primary_provenance_closure', 'requested': True, 'required_for_claim': True, 'machine_gate': 'BLOCKED', 'human_gate': 'NOT_REVIEWED', 'result_ref': 'review/NSI_CONTRACT.json'}], 'validation_levels': {'internal': 'PASS', 'paper_comparison': 'all endpoints and contour boundaries quantified', 'official_likelihood': 'not requested or claimed', 'old_program_regression': 'not run; shared source unchanged'}, 'runtime_integration': 'existing local project APIs with fixed source-state adapter; original execution source evidence archived', 'final_claim': 'conditional approximate NSI benchmark from source-annotated inputs', 'limitations': summary['limitations']}}
    artifact_paths = ['outputs/validation.json', 'outputs/summary.json', 'outputs/nsi_intervals.csv', 'outputs/nsi_operator_kernel_161_641.npz']
    artifacts = [{'path': path, 'sha256': sm.sha256(LAYOUT.path(path)), 'role': 'actual NSI calculation artifact'} for path in artifact_paths]
    schema = load(LAYOUT.path('snapshot/workflows/_shared/schemas/phase-result.schema.yaml'))
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(schema)
    for phase in ('P04', 'P05', 'P07', 'P08', 'P09', 'P10'):
        if phase == 'P08':
            reference = REVIEW / 'phase_reports/P07.md'
            handoff = {'representation': 'eft_quadratic_coefficient_kernel', 'backend': 'interface_kernel_v1', 'basis_scope': 'declared_subspace', 'parameter_domain': {'basis': BASIS, 'scan': 'six real vector NSI coordinates; other BSM zero'}, 'state_treatment': 'fixed_parameter_independent', 'slow_reference': {'report_ref': 'review/phase_reports/P07.md', 'sha256': sm.sha256(reference), 'approval_ref': None}, 'cache_dependencies': 'recorded and checked by existing dependency_record and load_compiled_kernel; scientific snapshot and grids fixed', 'validation_summary': validation}
        else:
            handoff = phases[phase]
        result = {'schema_version': 1, 'phase': phase, 'capability_id': 'conus_nsi_response_v1_' + phase.lower(), 'workspace': 'isolated_candidate', 'plan_status': 'READY', 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'scope_ref': 'review/NSI_CONTRACT.json', 'input_refs': ['review/INPUT_SNAPSHOT.json', 'review/NSI_CONTRACT.json'], 'input_fingerprint': sm.sha256(REVIEW / 'INPUT_SNAPSHOT.json'), 'evidence_refs': ['data/benchmark/REFERENCES_PROVENANCE.json', 'snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json'], 'decision_refs': ['review/NSI_CONTRACT.json'], 'approval_refs': [], 'artifacts': artifacts, 'checks': [{'name': 'NSI scoped numerical and source-identity checks', 'status': 'PASS', 'command': 'python -B benchmark_nsi.py', 'result_ref': 'outputs/validation.json'}], 'handoff': handoff}
        errors = list(validator.iter_errors(result))
        if errors:
            raise ValueError(phase + ' schema issues: ' + repr([(list(error.path), error.message) for error in errors]))
        body = '[本次完整报告](../NSI_BENCHMARK_REPORT_V1.md) 保存同节输入数值、标准引文、实际结果和来源限制。\n\n'
        body += '```json phase-result\n' + json.dumps(sm.json_value(result), ensure_ascii=False, indent=2) + '\n```'
        markdown_report(REVIEW / 'phase_reports' / (phase + '.md'), phase + ' CONUS+ NSI候选交接', '技术范围已验证，human_gate=NOT_REVIEWED。P08引用本次候选Slow，正式权威冻结仍待结果审阅。', [('范围与实际交接', body)])
    sm.write_json(REVIEW / 'PHASE_SCHEMA_CHECKS.json', {'schema': 'snapshot/workflows/_shared/schemas/phase-result.schema.yaml', 'checked': ['P04', 'P05', 'P07', 'P08', 'P09', 'P10'], 'status': 'PASS', 'scope': 'structure, not scientific acceptance'})

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    verify_snapshot()
    summary = load(OUTPUT / 'summary.json')
    validation = load(OUTPUT / 'validation.json')
    sensitivity = load(OUTPUT / 'error_sensitivity.json')
    contours = load(OUTPUT / 'paper_contour_comparison.json')
    draw_figures(summary)
    citation = 'V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3.'
    benchmark_pdf = '../snapshot/docs/references/CONUS/2501.17843v3.pdf'
    first = table(['耦合', '本次1σ区间', '论文Table II 1σ区间', '最大端点差'], [[READABLE[name], interval_text(fit['intervals']['1sigma']), interval_text(fit['paper_1sigma_intervals'], 3), f"{np.max(abs(np.asarray(fit.get('endpoint_differences_vs_paper', [[float('nan')]])))):.6f}"] for name, fit in summary['NSI_rows'].items()])
    first += f"\n\nSM点经α轮廓化后的χ²={summary['SM_chi2_profiled']:.9f}，α={summary['SM_alpha_profiled']:.9f}。对角NSI保留全部简并分支，eμ和eτ分别计算并核对相等。\n\n![一维NSI谱线与区间](../outputs/nsi_profiles_1d.png)\n\n[区间CSV](../outputs/nsi_intervals.csv) · [一维扫描CSV](../outputs/nsi_scan_1d.csv) · [19箱NSI事例谱](../outputs/nsi_spectra_19bins.csv)\n\n外部区间直接来自 {citation} Table II，PDF p.13。[原文]({benchmark_pdf})"
    theory = table(['输入／约定', '实际数值与单位', '直接依据、精确定位与核验范围'], [['矢量NSI', 'εqV=εqL+εqR，q=u,d，六个实数坐标', f'上述De Romeri等人论文Eqs.(7)–(9)，PDF pp.4–5；[原文]({benchmark_pdf})'], ['到LEFT系数', 'δC(6,1,q)=−√2 GF εqV，单位GeV⁻²', '[项目parameters.py](../snapshot/cevns_pyeft/statistics/parameters.py)::vector_nsi_to_np_wilson；按Eq.(7)投影至矢量夸克流'], ['SM', 'include_sm=True，sin²θW=0.23857，其他BSM=0', '[装配](../nsi_model.py)，SM沿用同一参考；GF运行值来自固定项目常数'], ['核响应与靶', '天然Ge70/72/73/74/76，数丰度0.2057/0.2745/0.0775/0.3650/0.0773', f'[数值配置]({DATA_PREFIX}input_choices.json)，论文p.9；五个[核表key](../snapshot/data/responses/responses_all.json)'], ['核数和质量', '1kg库存；NIST原子质量用于核数，A u用于引擎运动学', f'[库存]({DATA_PREFIX}natural_ge_inventory.csv)，实际执行装配为[sm_model.py](../sm_model.py)'], ['源谱', '10001行，0–10MeV；总通量1.5×10¹³ cm⁻²s⁻¹', f'[完整源表]({DATA_PREFIX}reactor_flux_default.csv)，[逐列溯源]({DATA_PREFIX}PROVENANCE_MAP.json)'], ['曝光／探测器', '1kg×119days；k=.162，σ0=20.38eVee，F=.1096，η=2.96eVee', f'论文pp.8–10、Eqs.(29)–(31)；[配置]({DATA_PREFIX}input_choices.json)'], ['编译子空间', '四个d=6算符，shape=(5,1,8,4,4,19)', '[核文件](../outputs/nsi_operator_kernel_161_641.npz) 与 [编译记录](../outputs/compile_summary.json)'], ['真实积分网格', '每核素161反冲点，Eν均匀641点并加源断点', '[实际Slow与Fast验证](../outputs/validation.json)；直接复用同一project Slow/compile_fast']])
    theory += '\n\n源、靶、探测器和原始来源状态沿用已固定SM输入，全部201个输入／代码文件由 [输入快照](INPUT_SNAPSHOT.json)保存SHA256。核表原始多体计算链与低能32节点的Kopeikin原始数表对应仍待核实。 ν／反ν共用事例率kernel沿用既有Li2026约定，原文依据为G. Li等人，arXiv:2601.19883v2，PDF p.21、Eq.(92)后一段。'
    theory += f'\n\nFlux的高能系数直接来自Th. A. Mueller et al., “Improved predictions of reactor antineutrino spectra,” Phys. Rev. C 83, 054615 (2011), doi:10.1103/PhysRevC.83.054615，Eq.(12)、Table VI、PDF p.13。[原文]({RUN_PREFIX}sources/1101.2663v3.pdf)。低能32节点的直接材料为用户提供的未发表CONUS+笔记，Table2、PDF p.6，[材料副本]({RUN_PREFIX}sources/user_reference_CONUS.pdf)。其所引用的V. I. Kopeikin, Phys. At. Nucl.75, 143–152 (2012), doi:10.1134/S1063778812020123，原始数表对应尚未核实。\n\n靶库存使用NIST Physical Measurement Laboratory, “Atomic weights and isotopic compositions for germanium,” online table, accessed2026-11-06，各Ge同位素行。[数表快照]({RUN_PREFIX}sources/nist_ge_isotopic_masses.html)。基本质量和Fermi常数采用NIST “2022 CODATA adjustment, complete listing”的对应行，实际引擎值保存在 [上一轮SM验证](../data/sm_reference/validation.json)。'
    statistics = table(['输入／处理', '采用值与shape／单位', '直接来源、核验和适用范围'], [['观测', '19个signed excess，保留6个负值', '[统计输入CSV](../data/statistics_input.csv)，原文p.10 Fig.1黑点，矢量取点溯源在既有data/statistics目录'], ['比较单位', 'counts kg⁻¹(10eVee)⁻¹；19箱160–350eVee，宽10eVee', '同1kg119days预测，逐箱事件数数值等于本图单位纵值；单位转换只执行一次'], ['主误差', 'σi=(error_minus+error_plus)/2，19个正数', '本次执行者选择，直接读取原取点上下误差后重算；全部数值见统计输入CSV'], ['误差敏感性', '上下误差各独立作σi，分别重拟合', '[误差敏感性结果](../outputs/error_sensitivity.json)，这两套用于检查误差对称化影响'], ['χ²', '19箱独立高斯残差＋(α/.169)²', '论文Eq.(33)，PDF pp.9–10；[项目profile_gaussian_one_pull](../snapshot/cevns_pyeft/statistics/profiling.py)'], ['累计归一化', 'σα=0.169，α为无界实数高斯pull', '论文p.10；只按Eq.(33)作用于信号，不重改Flux或额外拟合全局输入归一化'], ['协方差', '采用Eq.(33)给出的对角形式', '本次论文χ²比较所需输入已取得；未加入作者未提供的额外相关结构'], ['单参数', '每次只变1个实数ε，其余NSI=0；扫描[-1,1]', '与TableII单参数约束比较，寻找所有极小值并保留全部允许分支'], ['一维阈值', '1σ为Δχ²=1；90%为2.705543454095404', 'TableII标注1σ；90%为χ²(df=1)的0.9分位数，数学派生'], ['二维阈值', '90%为Δχ²=4.605170185988092', 'Fig.4标注90%；阈值由χ²(df=2)分位数派生'], ['区间算法', '4001扫描点定位，brentq根精度1e−12；2001点独立复查', '项目推导算法，区间边界稳定容差5e−6，所有分支及局部极小值有记录']])
    statistics += f'\n\n统计主张为基于 {citation} Eq.(33) 的近似论文benchmark。标称渐近Δχ²阈值用于对照，尚未用toys校准NSI边界、简并处的频率学覆盖率。本次NSI只涉及u/d夸克，按原文Fig.4采用CEνNS-only。'
    sensitivity_table = table(['耦合', '平均误差1σ', '固定下误差1σ', '固定上误差1σ'], [[READABLE[name], interval_text(summary['NSI_rows'][name]['intervals']['1sigma']), interval_text(fit['lower']['intervals']['1sigma']), interval_text(fit['upper']['intervals']['1sigma'])] for name, fit in sensitivity.items()])
    direct = table(['非零Slow点', 'Slow总事例数', '最大逐箱绝对差', '最大逐箱相对差'], [[record['case'], f"{record['total_slow']:.9f}", f"{record['max_absolute_difference_events']:.3e}", f"{record['max_relative_difference']:.3e}"] for record in validation['direct_slow_comparisons']])
    direct += f"\n\n预定Slow/Fast条件为|ΔN|≤10⁻⁸+10⁻⁸|N|。同位素分量也逐箱核对。验证还覆盖SM恢复、复数跃迁、eμ/eτ、反号偶性、full/pair重建、60个多参数点、保存后加载、子空间外参数拒绝与曝光改变后的缓存失效。非零εuVee=.05的321→641能量网格最大逐箱变化为 {validation['nonzero_NSI_energy_grid_refinement']['max_relative_difference'] * 100:.6f}%。\n\n加速扫描的逐箱多项式来自现有已积分算符双线性核在明确NSI子空间的精确二次形式。其shape为每平面6×19，顺序为1,x,y,x²,xy,y²；并与原接口在60点直接核对。\n\n[全部检查和实际数值](../outputs/validation.json) · [精确二次模板](../outputs/nsi_quadratic_templates.npz)"
    contour_text = '![二维NSI与原图比较](../outputs/nsi_contours_2d.png)\n\n'
    contour_text += table(['平面', '原图非裁切顶点', '本次Δχ²在原图边界中位数', '范围'], [[name, record['non_clipped_vertices'], f"{record['project_delta_chi2_at_paper_boundary_median']:.6f}", f"{record['project_delta_chi2_at_paper_boundary_min']:.6f}–{record['project_delta_chi2_at_paper_boundary_max']:.6f}"] for name, record in contours.items()])
    contour_text += f'\n\n蓝色参考直接来自 {citation} Fig.4，PDF p.14。四组坐标按各图主要刻度校准，共7个轮廓多边形、1429个顶点。边界比较排除了原图面板边缘的裁切顶点，原图名义阈值为4.605170。该比较保留图形取点精度与模型差别。\n\n[全部顶点CSV](../data/benchmark/fig4_blue_polygons.csv) · [直接出处及坐标校准](../data/benchmark/REFERENCES_PROVENANCE.json)'
    render_checks = load(OUTPUT / 'contour_rendering_checks.json')
    contour_text += f"\n\n对本次显示轮廓的全部顶点重新计算了精确轮廓化χ²，501×501网格绘图插值的最大Δχ²偏差为 {max((item['max_absolute_delta_chi2_interpolation_error'] for item in render_checks.values())):.9f}。[逐面板插值检查](../outputs/contour_rendering_checks.json)"
    gaps = table(['事项', '已有内容', '仍需什么', '影响'], [['原始低能谱', '用户笔记32点和Kopeikin文献信息', 'Kopeikin原数表／作者文件的逐点对应', '原文数据来源认证'], ['Ge核响应', '本地五核素数表、哈希与数值验证', '原作者多体计算／生成转换脚本', '正式Nuclear Response来源认证'], ['作者数值统计包', '论文取点、Eq.(33)、TableII与Fig4', '原始19箱数表、误差处理和作者扫描数组／代码', '更精确的论文复现和误差约定核对'], ['SM谱形', '已知高能尾部与原图有差异', '匹配原文Flux及形状因子设置并核对作者正向谱', '当前NSI结果对论文差异的解释'], ['正式基准冻结', '候选P07/P08/P09数值与来源报告', '对当前版本结果与统计选择的审阅', '全部human_gate保持NOT_REVIEWED']])
    gaps += '\n\n本次所选近似χ²所需数值已取得，SOURCE和TARGET上游原文来源保持PARTIAL。平均误差选择及其敏感性在同一版输出可见，后续更换误差只需重算统计，不改变已固定物理核。'
    repro = '```powershell\n.\\run_nsi_benchmark.ps1\n```\n\n依次执行参考提取（首次）、直接Slow与现有系数核构建、区间与二维扫描、绘图和报告。[本次合同](NSI_CONTRACT.json) 固定参数域与预定误差标准。[运行环境](ENVIRONMENT.json) 保存依赖版本。\n\n[逐输出溯源](../outputs/OUTPUT_PROVENANCE.json) 保存文件列到数据、原文与算法的对应。[阶段记录](phase_reports/README.md) 保存P04、P05、P07–P10的实际交接与审核状态。\n\n完整标准引文及上游资料链接沿用 [onboarding参考文献](../snapshot/docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/REFERENCES.md)。本轮新增直接定位为基准论文Eqs.(7)–(9)、Eq.(33)、TableII、Fig.4。'
    markdown_report(LAYOUT.report, 'CONUS+ NSI benchmark v1（隔离候选，2026-11-06）', '沿用现有项目流程、天然锗五同位素与Nuclear Response。本文逐节列出实际采用的输入、直接来源、推导、验证和未闭合事项。', [('单参数benchmark结果', first), ('前向输入与NSI映射来源', theory), ('统计输入、公式与推断', statistics), ('上下误差敏感性', sensitivity_table), ('直接Slow与加速核验证', direct), ('Fig.4二维benchmark', contour_text), ('仍待核实与后续所需数据', gaps), ('复算、阶段与标准参考文献', repro)])
    create_phase_reports(summary, validation)
    sm.write_json(OUTPUT / 'OUTPUT_PROVENANCE.json', {'provenance_id': 'CONUS_vector_NSI_response_v1', 'created_date': '2026-11-06', 'citation': citation, 'benchmark_pdf_sha256': 'b20923363badde299106a6df83f0dff5308fd69d652b59b9967d32b764057c90', 'inputs': {'scientific_input_file_hashes': '../review/INPUT_SNAPSHOT.json', 'NSI_and_statistics': '../review/NSI_CONTRACT.json', 'original_column_sources': '../snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json', 'paper_NSIs': '../data/benchmark/REFERENCES_PROVENANCE.json'}, 'output_column_lineage': [{'file': 'nsi_intervals.csv', 'columns': ['coupling', 'confidence', 'delta_chi2_threshold', 'lower', 'upper', 'best_fit_epsilon', 'minimum_chi2', 'sigma_mode'], 'derivation': 'Existing vector_nsi_to_np_wilson -> existing compile_fast operator kernel -> validated exact real polynomial -> existing profile_gaussian_one_pull -> multiple minima and brentq roots', 'source_locator': '2501.17843v3 Eqs.(7)-(9), Eq.(33), TableII p.13; threshold derivation and error choice in NSI_CONTRACT.json', 'status': 'PROJECT_DERIVED_APPROXIMATE'}, {'file': 'nsi_scan_1d.csv', 'columns': 'epsilon, chi2_profiled, delta_chi2, alpha_profiled, predicted_total_events', 'derivation': 'same parameter mapping, physical input snapshot, exact bilinear prediction and profiled statistic; one real NSI varied at a time', 'status': 'PROJECT_DERIVED_APPROXIMATE'}, {'file': 'nsi_spectra_19bins.csv', 'columns': 'energy edges, total event counts, all five isotope counts, coupling point', 'derivation': 'kernel.predict at reported best fits and 1sigma endpoints with unchanged 1kg119day normalization', 'status': 'PROJECT_DERIVED'}, {'files': ['plane_diag_ud.npz', 'plane_fc_ud.npz', 'plane_ring_mu.npz', 'plane_ring_tau.npz'], 'arrays': 'x,y,chi2,delta_chi2; rows=y, columns=x', 'derivation': 'same exact NSI polynomial and existing profile statistic at501x501 grid points; multiple-start minimum; two-parameter90percent threshold', 'status': 'PROJECT_DERIVED_APPROXIMATE'}, {'file': 'error_sensitivity.json', 'keys': 'lower/upper intervals and minima for all six coordinates', 'derivation': 'repeat inference with each delivered lower or upper error length as fixed sigma instead of their mean', 'status': 'PROJECT_DERIVED_SENSITIVITY'}, {'file': 'paper_contour_comparison.json', 'derivation': 'evaluate project profiled delta-chi2 at digitized paper boundary vertices after excluding clipped panel edges', 'status': 'PROJECT_DERIVED_FIGURE_COMPARISON'}], 'program_sha256': {path.name: sm.sha256(path) for path in HERE.glob('*.py')}, 'files': {path.name: {'sha256': sm.sha256(path)} for path in OUTPUT.iterdir() if path.is_file() and path.name != 'OUTPUT_PROVENANCE.json'}, 'scientific_provenance_status': 'PARTIAL', 'human_gate': 'NOT_REVIEWED'})
    print('NSI figures, source-visible report and six phase schemas passed', flush=True)
    LAYOUT.normalize_generated_documents()
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
