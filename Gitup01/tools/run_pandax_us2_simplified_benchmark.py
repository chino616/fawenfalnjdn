"""Calculate the explicitly simplified PandaX US2 SM electron spectrum.

Uses the standard project loader, Runtime, source, targets and SM recoil
integrator. This is an additional approximation, not a replacement for Response.
The historical effective-c_i field is a conditional postfit-template rescaling
diagnostic, not an independently validated detector calibration or SM prediction.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT/'data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json'
DEFAULT_OUTPUT = ROOT/'outputs/solar_b8_sm/20261110_pandax_simplified_run1'
sys.path.insert(0, str(ROOT))
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_mean_map import with_pandax_mean_map


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def link(origin, target, label):
    return '['+label+'](<'+os.path.relpath(target, origin.parent).replace('\\', '/')+'>)'


def table(headers, rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join('---' for _ in headers)+'|\n'+''.join(
        '| '+' | '.join(str(v).replace('|', r'\|').replace('\n', '<br>') for v in row)+' |\n' for row in rows)


def run_curve(experiment, card):
    rows, predictions = [], []
    for grid in card['numerics']['grids']:
        start = time.perf_counter()
        p = predict_experiment(experiment, backend='slow', numerics={k: grid[k] for k in ['n_er', 'n_enu']})
        predictions.append(p)
        rows.append(dict(grid, counts=p.counts.tolist(), total_events=float(p.counts.sum()),
                         seconds=time.perf_counter()-start))
        print(experiment.definition.physical.curve_label, grid['label'], float(p.counts.sum()), flush=True)
    checks = []
    def compare(a, b, axis):
        delta = abs(a.counts-b.counts)
        tol = np.maximum(card['numerics']['absolute_tolerance_events'],
                         card['numerics']['relative_tolerance']*abs(b.counts))
        return {'axis': axis, 'absolute_difference': delta.tolist(), 'tolerance_events': tol.tolist(),
                'max_relative_difference': float(np.max(delta/np.maximum(abs(b.counts), 1e-30))),
                'passed': bool(np.all(delta <= tol))}
    checks += [compare(predictions[1], predictions[2], 'recoil'),
               compare(predictions[2], predictions[3], 'neutrino_energy')]
    # Refine each dimension separately when needed, preserving interpretable checks.
    final = predictions[-1]
    numerics = {k: rows[-1][k] for k in ['n_er', 'n_enu']}
    for axis, key in [('recoil', 'n_er'), ('neutrino_energy', 'n_enu')]:
        current_check = next(x for x in checks if x['axis'] == axis)
        for attempt in range(3):
            if current_check['passed']:
                break
            numerics[key] = 2*numerics[key]-(1 if key == 'n_er' else 0)
            newer = predict_experiment(experiment, numerics=numerics)
            current_check = compare(final, newer, axis)
            checks.append(current_check)
            rows.append(dict(numerics, label=axis+'_adaptive_'+str(attempt+1),
                             counts=newer.counts.tolist(), total_events=float(newer.counts.sum())))
            final = newer
        if not current_check['passed']:
            raise RuntimeError('Numerical convergence criterion failed on '+axis)
    return final, {'runs': rows, 'checks': checks, 'passed': True}


def curve_record(experiment, prediction, convergence):
    d = prediction.combined_prediction.diagnostics
    return {'counts': prediction.counts.tolist(), 'total_events': float(prediction.counts.sum()),
        'inverse_recoil_edges_keV': experiment.model.observation[0].recoil_edges.tolist(),
        'accepted_domain_total_events': float(d['accepted_domain_total_events']),
        'outside_mean_window_events_low_high': d['outside_mean_window_events_low_high'],
        'components': {'/'.join(k): v.tolist() for k, v in prediction.combined_prediction.components.items()},
        'normalization_record': plain(prediction.combined_prediction.normalization_record),
        'physics_fingerprint': prediction.physics_fingerprint,
        'analysis_fingerprint': prediction.analysis_fingerprint,
        'execution_record': plain(prediction.record), 'convergence': convergence}


def plot(out, edges, raw, sensitivity, calibrated, references):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from scipy.stats import chi2
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.5), constrained_layout=True)
    axes[0].stairs(raw, edges, color='#007f7a', lw=2.4, label='Calculated SM: nominal Qy, c=1')
    axes[0].stairs(sensitivity, edges, color='#bd772c', lw=1.7, linestyle='--',
                   label='Calculated SM: best-fit Qy, c=1 (sensitivity)')
    axes[0].stairs(calibrated, edges, color='#a23d91', lw=2, linestyle=':',
                   label='Post-fit template x 0.65 (reference only)')
    axes[0].set_title('Signal only: actual eight-bin calculation')
    background = np.array(references['background_total'])
    x = (edges[:-1]+edges[1:])/2
    axes[1].bar(x, references['cathode'], width=.5, color='#b8cdbb', label='Cathode: digitized post-fit reference')
    axes[1].bar(x, references['MD'], bottom=references['cathode'], width=.5, color='#e6cc8e',
                label='MD: digitized post-fit reference')
    axes[1].stairs(background+raw, edges, color='#007f7a', lw=2.4, label='Calculated uncalibrated SM + reference B')
    axes[1].stairs(background+calibrated, edges, color='#a23d91', lw=2, linestyle=':',
                   label='Rescaled post-fit reference + reference B')
    axes[1].stairs(references['paper_blue_total'], edges, color='#174cba', lw=1.5, linestyle='--',
                   label='2411.11749v1 Fig.1 blue: digitized S+B')
    observed = np.array(references['observed'])
    alpha = 1-.682689492137
    lower = np.where(observed > 0, .5*chi2.ppf(alpha/2, 2*observed), 0.)
    upper = .5*chi2.ppf(1-alpha/2, 2*(observed+1))
    axes[1].errorbar(x, observed, yerr=np.array([observed-lower, upper-observed]),
        fmt='ko', ms=4, capsize=3, elinewidth=1.1, zorder=5,
        label='Observed: 68.27% Poisson intervals')
    axes[1].set_title('Signal + reference backgrounds (no likelihood fit)')
    for ax in axes:
        ax.set(xlabel=r'Mean-mapped electron number $N_e$', ylabel='Events / 0.5 electron bin',
               xlim=(4, 8), ylim=(0, None))
        ax.set_xticks(edges)
        ax.grid(axis='y', alpha=.2)
        ax.legend(fontsize=7.3, loc='upper right')
    fig.suptitle(r'PandaX-4T US2: simplified SM, $\Phi_{8B}=5.46\times10^6$ cm$^{-2}$s$^{-1}$, 1.04 t yr'
        '\nSSM flux fixed; purple: post-fit template rescaling only, not a calibrated SM prediction', fontsize=12)
    fig.savefig(out/'events.png', dpi=190)
    fig.savefig(out/'events.svg')
    plt.close(fig)


def report(out, card, result):
    origin = out/'REPORT.md'
    nominal = result['nominal']; sensitivity = result['bestfit_sensitivity']
    c = result['effective_calibration']; refs = result['references']
    text = '# PandaX US2：标准模型八箱谱，论文简化方法\n\n'
    text += '**2026-11-10。简化分支计算已完成；完整Response与严格论文等价性仍未认证，科学结果待审阅。** '
    text += '这里的绿色曲线来自本轮共享SM积分，不是论文原图或抠图信号重绘。\n\n'
    text += '[计算图](events.png) · [逐箱数组](events_by_bin.tsv) · [参数/收敛/校准记录](RESULT.json) · [实际装配](PREPARED_MODEL.nominal.json) · '+link(origin, CARD, '带原文定位的参数卡')+'\n\n'
    text += '实验黑点误差棒采用68.27%中心Poisson区间（Garwood）：下界χ²(α/2;2D)/2（D=0时为0）、上界χ²(1−α/2;2D+2)/2，α=1−0.682689492137。由已提取的观测整数D计算，属于本项目绘图约定，不是再次数字化论文误差棒，也不包含背景模型误差。\n\n'
    text += '**SSM口径更正：** 直接计算固定Φ₀=5.46×10⁶ cm⁻²s⁻¹，25.851676事例不变。紫线是实验后验拟合谱乘5.46/8.4的条件参考；仍带实验拟合响应参数，不能称为同一基准响应下的“校准后SM”，不能验证绿色预测。历史JSON字段`effective_calibration`保留用于追溯，其角色按本说明解释。\n\n'
    text += '<a id="toc"></a>\n\n## 目录\n\n- [计算结果](#counts)\n- [计算链与方法](#method)\n- [后验拟合谱缩放参考](#calibration)\n- [输入与逐项出处](#inputs)\n- [验收与限制](#validation)\n- [参考文献](#references)\n\n'
    text += '<a id="counts"></a>\n\n## 计算结果\n\n'
    e = result['electron_edges']; t = nominal['inverse_recoil_edges_keV']
    text += table(['Ne箱','对应T [keVnr]','固定SSM直接SM（c=1）','拟合谱×0.65参考','经验比值（非独立校准）','D'],[
        [f'{a:g}–{b:g}', f'{t[i]:.6f}–{t[i+1]:.6f}',f'{nominal["counts"][i]:.6f}',
         f'{c["calibrated_counts"][i]:.6f}', f'{c["coefficients"][i]:.6f}', int(refs['observed'][i])]
         for i,(a,b) in enumerate(zip(e[:-1],e[1:]))])
    text += f'\n固定SSM通量的直接积分信号 **{nominal["total_events"]:.6f}事例**；后验拟合谱缩放参考 **{sum(c["calibrated_counts"]):.6f}事例**，后者不作为校准SM预测。'
    text += f'Best-fit Qy敏感性对照直接积分为{sensitivity["total_events"]:.6f}事例；它不是另一份独立探测器标定。\n\n'
    text += f'完整已提取接受度T域内积分为{nominal["accepted_domain_total_events"]:.6f}事例，其中平均窗口以下/以上分别为'+', '.join(f'{v:.6f}' for v in nominal['outside_mean_window_events_low_high'])+'事例。'
    text += 'Total(US2)已包含ROI；平均映射裁窗会舍弃真实涨落迁入ROI的事件。本轮明确报告该近似损失，没有把八箱强制归一化到旧47.027事例。\n\n[返回目录](#toc)\n\n'
    text += '<a id="method"></a>\n\n## 计算链与方法\n\n'
    text += '依次使用正式Source、天然Xe九核素、共享SM截面、反冲积分、平均映射、八箱积分。入口为`load_experiment_package → with_pandax_mean_map → predict_experiment → MeanMapExecutor → integrate_recoil_yield`；工作流文件不进入Runtime。\n\n'
    text += '$$\nS_i^{\\mathrm{raw}}=\\mathcal E\\sum_A N_A^{(1\\,\\mathrm{t})}\\int_{T(n_i)}^{T(n_{i+1})}dT\\,\\mathcal A_{\\mathrm{US2}}(T)\\int dE_\\nu\\,\\frac{d\\phi}{dE_\\nu}\\frac{d\\sigma_A}{dT}.\n$$\n\n'
    text += '依据：[1] PDF p5式(11)–(13)、p6式(15)；天然同位素求和与核数单位沿用正式包。'
    text += '\n\n'+table(['步骤','实际处理与出处'],[
        ['源','[1] p5式(11)后：Φ=5.46×10⁶ cm⁻²s⁻¹；[3] 官网829点中心谱，积分0.999986544，保留原归一化。'],
        ['截面/核因子','[1] p3式(1)–(3)：sin²θW=0.23857，KN半径系数1.23fm、skin0.7fm；共享SM包含−T/Eν项。天然Xe组成来自[4]。'],
        ['曝光','[1] p5、[2] p3：US2合计1.04t·yr；一年秒数、核数、曝光各施加一次，不虚构逐run拆分。'],
        ['均值映射','[1] p6式(15)；[2] p5 Fig.4下图Nominal线。Qy线性插值，再反解T Qy(T)=Ne。得到0.660084–1.186893keV，与[1] p5脚注3吻合。'],
        ['效率','[2] p3 Fig.1黑色虚线Total(US2)，99点；已含ROI，分段线性，只乘一次。均值裁窗造成的损失单独列出。'],
        ['变量转换','[1] p5式(13)：在反映射T区间直接积分，已经完成变量变换；不额外乘第二次Jacobian。'],
        ['分辨率/参考','[1] p5式(12)后明确不计分辨率；直接结果用项目c_i=1基线，未宣称作者使用1。下面的比值仅为后验拟合谱诊断，未独立标定Response。']])
    text += '\n[返回目录](#toc)\n\n<a id="calibration"></a>\n\n## 后验拟合谱缩放参考（历史名：有效校准）\n\n'
    text += '作者称c_i为简化一维分析的“effective efficiencies”：[1] PDF p5式(12)后，用于匹配[2] Fig.5上图。它不是截面中的新物理参数，也不是天然满足0≤c_i≤1的概率。核与选择的近似、均值裁窗、产额或拟合约定的差异均可能被吸收进这个比值。\n\n'
    text += '$$\n\\widehat c_i=\\frac{S_i^{\\mathrm{exp,fit}}}{S_i^{\\mathrm{raw}}(\\Phi_0)\\,\\Phi_{\\mathrm{fit}}/\\Phi_0},\\qquad S_i^{\\mathrm{cal}}=\\widehat c_i S_i^{\\mathrm{raw}}(\\Phi_0).\n$$\n\n'
    text += '**本项目重建定义，不是作者公布数组。** 锚点来自[2] PDF p6 Fig.5上图拟合信号，所用图线数组积分74.85281657事例（印刷值75±28）；拟合通量Φfit=8.4×10⁶ cm⁻²s⁻¹来自同页结果段。固定其拟合产额/选择/nuisance，按Φ0/Φfit=5.46/8.4线性缩放，得到本轮条件校准信号。未把74.85修成75，也未使用[1] Fig.1蓝线反求c_i。\n\n'
    text += '该比值依赖上述冻结实验拟合点的约定，不能唯一确定作者实际c_i。校准后与锚点的符合是构造闭合，不能再作为独立复现成功的证据。[1] Fig.1蓝线为S+B，只作描述性对照；其全套背景nuisance未与本轮对齐。\n\n[返回目录](#toc)\n\n'
    text += '更明确地，固定探测器参数η时S_i(Φ,η)=Φ·K_i(η)，线性换算成立；本例乘0.65得到的是S_i(Φ₀,η̂_fit)，并未证明等于采用基准响应η₀的S_i(Φ₀,η₀)。[2] PDF p6报告联合拟合后的charge yield位于+0.97σ，图5是该拟合的信号投影；仅换总通量不能把这些响应/系统参数恢复成基准值。\n\n'
    text += '若进行带SSM约束的通量拟合，可按[1]式(17)后给出的12%误差取Φ=(1+α)Φ₀并加入(α/0.12)²；固定点benchmark取α=0。当前未执行这种profile，未将通量调到观测计数。\n\n'
    text += '<a id="inputs"></a>\n\n## 输入与逐项出处\n\n'
    text += table(['文件/数值','性质与核验范围','直接原文定位'],[
        [link(origin,ROOT/row['file'],Path(row['file']).name),row['role']+'；SHA256 `'+row['sha256']+'`',row['locator']]
        for row in card['inputs']])
    text += '\n所有正式标量/处理参数如下，沿用正式包的值、单位及原定位；`reference_only`/`unused_snapshot`不被追加为本轮物理输入。\n\n'
    text += table(['参数','值','单位','原文定位/定义','来源ID'],[
        [key, json.dumps(v['value'],ensure_ascii=False),v['unit'],v.get('meaning',''),', '.join(v.get('source_refs',[]))]
        for key,v in card['parameters'].items()])
    text += '\n'+link(origin,out/'INPUT_EVIDENCE.json','输入shape、范围、代表值、来源全文与运行哈希')+'保存各实际数组核验；'+link(origin,out/'PREPARED_MODEL.nominal.json','完整Runtime装配')+'保存实际核数与组件配置。\n\n[返回目录](#toc)\n\n'
    text += '<a id="validation"></a>\n\n## 验收与限制\n\n'
    text += table(['项目','结果'],[
        ['直接计算','实际8箱Ne积分；信号与九核素分量和一致；通量线性和接受度T域分区通过相关测试。'],
        ['数值收敛','nominal与best-fit均分别加密T和Eν，逐箱满足max(0.0002事例, 0.2%×计数)的项目阈值；完整运行与差值见RESULT.json。'],
        ['来源','既有数字化Qy/效率/参考图线及固定原包逐文件SHA256核对；并未把抠图表称为官方发布数组。'],
        ['完整Response','原US2逐箱概率/涨落与选择模型缺口保留；简化分支不提供该概率核。'],
        ['严格Fig.1复现','未认证：作者c_i与全套nuisance未获得；参考B为图中拟合投影，未当作独立prefit背景或统计输入。'],
        ['χ²/排除限','未请求、未计算；不据此声称完成Fig.2/4。'],
        ['科学审核','执行授权D0003/W0003；结果接受NOT_REVIEWED，不自动推进历史Response的Gate。']])
    delta = np.array(refs['raw_plus_reference_background'])-np.array(refs['paper_blue_total'])
    text += '\n与论文蓝线逐箱的描述性差值（直接SM+参考B−蓝线）为：`'+', '.join(f'{v:+.4f}' for v in delta)+'`事例。不是同一nuisance点的精度验收。\n\n[返回目录](#toc)\n\n'
    text += '<a id="references"></a>\n\n## 参考文献\n\n'
    for i, rid in enumerate(['R01','R02','R04','R09'],1):
        src=next(s for s in card['sources'] if s['source_id']==rid)
        text += f'[{i}] ({rid}) '+src['citation']+'\n\n'
    extra = sorted({rid for v in card['parameters'].values() for rid in v.get('source_refs',[])}-{'R01','R02','R04','R09'})
    for rid in extra:
        src=next((s for s in card['sources'] if s['source_id']==rid),None)
        if src:text += rid+': '+src['citation']+'\n\n'
    text += '[返回目录](#toc)\n'
    origin.write_text(text, encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    card = json.loads(CARD.read_text(encoding='utf8'))
    for row in card['inputs']:
        if sha(ROOT/row['file']) != row['sha256']:
            raise ValueError('Input changed: '+row['file'])
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    package = ROOT/card['package']
    base = load_experiment_package(package)
    with np.load(package/'experiment.resources.npz', allow_pickle=False) as a:
        acceptance = np.loadtxt(package/'detector/pandax_us2_acceptance_2407.10892v3.txt')
        np.testing.assert_array_equal(a['efficiency_energy_keV'], acceptance[:,0])
        np.testing.assert_array_equal(a['efficiency'], acceptance[:,1])
        arrays = {k:a[k].copy() for k in a.files}
    records = {}; predictions = {}; experiments = {}
    for label in ['nominal', 'bestfit']:
        experiment = with_pandax_mean_map(base, qy_file=package/f'detector/pandax_qy_{label}.txt',
            curve_label=label, electron_edges=tuple(card['method']['electron_edges']))
        pred, convergence = run_curve(experiment, card)
        records[label] = curve_record(experiment, pred, convergence)
        predictions[label] = pred; experiments[label] = experiment
        save(out/f'PREPARED_MODEL.{label}.json', experiment.describe())
    raw = predictions['nominal'].counts
    experiment_reference = np.loadtxt(package/'statistics/pandax_original_fig5.txt')
    paper_reference = np.loadtxt(package/'statistics/pandax_benchmark_fig1.txt')
    expected_edges = np.array(card['method']['electron_edges'])
    for a in [experiment_reference, paper_reference]:
        np.testing.assert_array_equal(a[:,1], expected_edges[:-1])
        np.testing.assert_array_equal(a[:,2], expected_edges[1:])
    np.testing.assert_array_equal(experiment_reference[:,3], paper_reference[:,3])
    flux = card['parameters']['source.total_flux']['value']
    anchor = card['effective_calibration']['anchor_flux_cm2_s']
    target = experiment_reference[:,6]*flux/anchor
    coefficients = target/raw
    calibrated = raw*coefficients
    blue_file = ROOT/'outputs/solar_b8_sm/20261109_fig1_comparison/COMPARISON.json'
    blue = json.loads(blue_file.read_text(encoding='utf8'))['regions']['PandaX']['blue_total_signal_plus_background_events_per_bin']
    b = paper_reference[:,4]+paper_reference[:,5]
    references = {'observed': paper_reference[:,3].astype(int).tolist(),
        'cathode': paper_reference[:,4].tolist(), 'MD': paper_reference[:,5].tolist(),
        'background_total': b.tolist(), 'paper_blue_total': blue,
        'raw_plus_reference_background': (raw+b).tolist(),
        'calibrated_plus_reference_background': (calibrated+b).tolist(),
        'comparison_role': 'descriptive only, digitized postfit backgrounds and blue S+B; nuisance points not aligned'}
    result = {'date':'2026-11-10', 'dataset_id':base.dataset_id,
        'calculation':'fixed-SSM SM mean mapping; postfit-template rescaling is reference only',
        'status':'SIMPLIFIED_CALCULATION_COMPLETE; PAPER_EQUIVALENCE_NOT_CERTIFIED',
        'electron_edges':expected_edges.tolist(), 'unit':'events/bin',
        'nominal':records['nominal'], 'bestfit_sensitivity':records['bestfit'],
        'effective_calibration':dict(card['effective_calibration'], coefficients=coefficients.tolist(),
            calibrated_counts=calibrated.tolist(), total_events=float(calibrated.sum()),
            anchor_digitized_events=experiment_reference[:,6].tolist(),
            closure_is_validation=False),
        'references':references, 'benchmark_card':str(CARD), 'benchmark_card_sha256':sha(CARD),
        'reference_role_policy':{'fixed_SSM_flux_cm2_s':flux,'postfit_template_rescaling':'diagnostic reference only',
            'legacy_effective_calibration_field':'not independently validated calibration or fixed-response SSM prediction'},
        'runner_sha256':sha(Path(__file__)), 'human_result_acceptance':'NOT_REVIEWED'}
    save(out/'RESULT.json', result)
    evidence = {'inputs':card['inputs'], 'parameters':card['parameters'], 'sources':card['sources'],
        'formal_arrays':{k:{'shape':list(a.shape),'minimum':float(a.min()),'maximum':float(a.max()),
           'representative_first_middle_last':[float(a.flat[i]) for i in [0,a.size//2,a.size-1]],
           'all_values':a.tolist() if a.size<=50 else None} for k,a in arrays.items()},
        'authority':'Units and provenance of formal keys are retained in experiment.input.yaml',
        'additional_resources':{key:plain(exp.record['resources']['mean_charge_yield']) for key,exp in experiments.items()}}
    save(out/'INPUT_EVIDENCE.json', evidence)
    stored = {'electron_edges':expected_edges, 'counts_nominal_raw':raw,
        'counts_bestfit_raw':predictions['bestfit'].counts, 'ci_reconstructed':coefficients,
        'counts_effective_calibrated':calibrated}
    for label,pred in predictions.items():
        for key, values in pred.combined_prediction.components.items():
            stored[label+'_counts_'+key[1]] = values
        d = pred.combined_prediction.diagnostics
        for isotope,grid in d['recoil_grids_keV'].items():
            stored[label+'_recoil_'+isotope] = grid
            stored[label+'_rate_at_exposure_per_keV_'+isotope] = d['true_recoil_rates_at_exposure_per_keV'][isotope]
    np.savez_compressed(out/'prediction.npz', **stored)
    t = experiments['nominal'].model.observation[0].recoil_edges
    np.savetxt(out/'events_by_bin.tsv', np.column_stack([expected_edges[:-1],expected_edges[1:],t[:-1],t[1:],
        raw,predictions['bestfit'].counts,coefficients,calibrated,paper_reference[:,3],b,blue,raw+b,calibrated+b]),
        delimiter='\t',fmt='%.12g',header='Ne_low Ne_high T_low_keVnr T_high_keVnr SM_raw_nominal SM_raw_bestfit_Qy ci_reconstructed_conditional SM_effective_calibrated observed_D digitized_reference_B digitized_paper_blue_SplusB SM_raw_plus_reference_B SM_calibrated_plus_reference_B')
    plot(out,expected_edges,raw,predictions['bestfit'].counts,calibrated,references)
    report(out,card,result)
    (out/'README.md').write_text('# PandaX US2：SM简化平均映射计算\n\n2026-11-10。实际八箱积分已完成；完整Response旧分支保留。\n\n'
        '[结果与来源说明](REPORT.md) · [图](events.png) · [SVG](events.svg) · [逐箱表](events_by_bin.tsv) · [数值数组](prediction.npz) · [收敛与校准](RESULT.json) · [输入证据](INPUT_EVIDENCE.json)\n\n'
        '[nominal实际装配](PREPARED_MODEL.nominal.json) · [best-fit敏感性装配](PREPARED_MODEL.bestfit.json) · '+link(out/'README.md',CARD,'显式方法参数卡')+' · [SM运行总目录](../README.md)\n\n'
        'SSM通量固定，c=1直接预测25.851676事例。历史effective_calibration字段仅表示实验Fig.5后验拟合谱×0.65的参考；不作为独立校准的SM预测或复现验收。\n',encoding='utf8')
    files=[{'file':p.name,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()]
    save(out/'RUN_MANIFEST.json',{'date':'2026-11-10','files':files,'runner':str(Path(__file__)),
        'runner_sha256':sha(Path(__file__)),'card_sha256':sha(CARD)})
    print(json.dumps({'output':str(out),'raw_total':float(raw.sum()),'effective_calibrated_total':float(calibrated.sum()),
        'accepted_domain_total':records['nominal']['accepted_domain_total_events']},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    main()
