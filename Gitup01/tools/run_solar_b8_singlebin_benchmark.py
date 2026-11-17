"""Run the independent 2601.19883 SM single-bin analysis through project Runtime.

Create-only outputs/solar_b8_singlebin/. Default XENONnT result is a partial
integral with rigorous 0<=epsilon<=1 tail bounds. --xenon-tail flat_sensitivity
is a separately identified PROJECT APPROXIMATION, never an official response.
"""
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.solar_singlebin import SAMPLES, INPUT_DIRECTORY, load_singlebin
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.experiments.definition import plain
from cevns_pyeft.statistics.solar_singlebin import profile


def save(path, value):
    path.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def run_sample(sample, output, tail_mode):
    exp = load_singlebin(sample, root=ROOT, tail_mode=tail_mode)
    destination = output/sample
    destination.mkdir()
    steps = [('base',201,120), ('recoil_refined',401,120),
             ('recoil_fine',801,120), ('energy_refined',801,480)]
    results = []; predictions = []
    for label, n_er, n_enu in steps:
        start = time.perf_counter()
        result = predict_experiment(exp, numerics={'n_er':n_er, 'n_enu':n_enu})
        d = result.combined_prediction.diagnostics
        results.append({'step':label,'n_er':n_er,'n_enu':n_enu, 'counts':result.counts.tolist(),
                        'full_interval_events':d['full_interval_events'], 'seconds':time.perf_counter()-start})
        predictions.append(result)
        print(sample, label, 'events', float(result.counts[0]), 'full_interval',
              list(d['full_interval_events']), 'seconds', round(results[-1]['seconds'],2), flush=True)
    checks = []
    for left, right, axis in [(1,2,'recoil'),(2,3,'neutrino_energy')]:
        a = np.r_[predictions[left].counts, predictions[left].combined_prediction.diagnostics['full_interval_events']]
        b = np.r_[predictions[right].counts, predictions[right].combined_prediction.diagnostics['full_interval_events']]
        delta = abs(a-b); tolerance = np.maximum(2e-4, .002*abs(b))
        checks.append({'axis':axis, 'checked':'predicted count and both full-interval endpoints',
                       'absolute_difference':delta.tolist(), 'tolerance_events':tolerance.tolist(),
                       'passed':bool(np.all(delta <= tolerance))})
    if not all(c['passed'] for c in checks):
        save(destination/'CONVERGENCE_FAILURE.json', {'steps':results,'checks':checks})
        raise RuntimeError('single-bin convergence failed; inspect saved diagnostic')
    final = predictions[-1]; d = final.combined_prediction.diagnostics
    statistical_data = json.loads((ROOT/INPUT_DIRECTORY/'fitted_yields.json').read_text(encoding='utf8'))['samples'][sample]
    stats = None
    if d['coverage_complete']:
        stats = plain(evaluate_experiment(exp, final).profile)
    else:
        # Both tails are bounds on unknown data, not hidden model choices.
        # At a fixed SM point Eq.88 is minimized at S=D if D lies in this range.
        try:
            evaluate_experiment(exp, final)
        except ValueError as exc:
            if 'partial acceptance' not in str(exc):
                raise
        else:
            raise AssertionError('partial single-bin likelihood should be rejected')
    interval = list(d['full_interval_events'])
    eval_chi = lambda s: profile(s, statistical_data['D'], statistical_data['sigma_stat'], statistical_data['pull_sigma']).chi2
    closest = min(max(statistical_data['D'], interval[0]), interval[1])
    chi_range = [eval_chi(closest), max(eval_chi(interval[0]), eval_chi(interval[1]))]
    flat = None
    if sample == 'XENONnT':
        epsilon = float(exp.model.observation.efficiency[-1])
        flat_count = d['verified_domain_events']+epsilon*d['unknown_tail_max_events_epsilon_le_1']
        flat = {'events':flat_count,'epsilon_tail':epsilon,'chi2':eval_chi(flat_count),
                'status':'PROJECT_SENSITIVITY_ONLY',
                'derivation':'known integral + epsilon(last)*unselected tail integral',
                'source':'R3 has no numeric tail; constant continuation is an explicit project assumption'}
    summary = {'sample':sample, 'dataset_id':exp.dataset_id, 'analysis':'singlebin_2601_19883',
        'input_card':str(ROOT/INPUT_DIRECTORY/'analysis.input.json'),
        'physics_fingerprint':final.physics_fingerprint, 'analysis_fingerprint':final.analysis_fingerprint,
        'calculation':'SM nuclear Response -> fresh recoil integral -> Total acceptance -> exposure, no fit scale',
        'parameter_point':{'sin2thetaW':exp.definition.reproduction_sin2thetaW,'flux_cm2_s':5.46e6,'nuclear':'R8 local response + shared Li2026 API'},
        'counts':final.counts.tolist(), 'full_interval_events':interval,
        'claim':d['claim'], 'complete_prediction':d['coverage_complete'],
        'experimental_efficiency_coverage_complete':d['experimental_efficiency_coverage_complete'],
        'exposure_tyr':exp.model.exposure_tyr, 'T_bounds_keVnr':list(exp.model.observation.requested_bounds),
        'known_domain_keVnr':d['known_domain_keVnr'], 'fitted_signal_data':statistical_data,
        'components':{'/'.join(k):v.tolist() for k,v in final.combined_prediction.components.items()},
        'statistics':stats,'profiled_chi2_range_due_only_to_unknown_tail':chi_range,
        'flat_tail_sensitivity':flat, 'convergence':{'runs':results,'checks':checks,'passed':True},
        'normalization_ledger':plain(final.combined_prediction.normalization_record),
        'execution':plain(final.record), 'result_acceptance':'NOT_REVIEWED',
        'limitations':['seven available Xe responses; Xe124/126 not renormalized',
                       'external nuclear-table generation/certification unresolved; direct local adoption authorized',
                       'same single-bin method is not certification of paper-code equivalence']}
    save(destination/'SM_RESULT.json',summary)
    save(destination/'PREPARED_MODEL.json',exp.describe())
    grid = np.asarray(d['recoil_keV'])
    raw_rate = sum(d['rate_per_keV_by_isotope_including_exposure'].values())
    known = grid <= exp.model.observation.verified_upper
    accepted = np.zeros_like(grid)
    accepted[known] = raw_rate[known]*exp.model.observation.known_acceptance(grid[known])
    np.savez_compressed(destination/'sm_prediction.npz', recoil_keV=grid, raw_events_per_keV=raw_rate,
                        verified_accepted_events_per_keV=accepted, acceptance_known=known,
                        counts=final.counts, full_interval_events=interval,
                        **{'rate_'+k:v for k,v in d['rate_per_keV_by_isotope_including_exposure'].items()})
    (destination/'README.md').write_text(f'# {sample}：独立单 bin SM\n\n'
        '[数值、来源与收敛](SM_RESULT.json) · [实际输入](PREPARED_MODEL.json) · [反冲数组](sm_prediction.npz)\n\n'
        f'状态：{summary["claim"]}。counts={summary["counts"]}，完整积分范围={interval}。未知尾段的主结果是区间，不是完整点预测；统计器拒绝把部分积分作为完整信号。\n', encoding='utf8')
    return summary


def plot(output, records):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(records), figsize=(4.3*len(records),4.4), constrained_layout=True, squeeze=False)
    legend={}
    for ax,row in zip(axes[0],records):
        data = row['fitted_signal_data']; predicted = row['counts'][0]
        ax.errorbar([0],[data['D']],yerr=[data['sigma_stat']],fmt='ko',capsize=5,label='Measured fitted signal (stat.)')
        if row['complete_prediction']:
            ax.plot([.4],[predicted], 's',color='#1673ad',label='Calculated SM'+(' (assumed tail)' if not row['experimental_efficiency_coverage_complete'] else ''))
        else:
            lo,hi = row['full_interval_events']
            ax.vlines(.4,lo,hi,color='#1673ad',lw=5,label='SM range: unknown tail, 0 <= eff <= 1')
            ax.plot([.4],[lo],'_',ms=14,color='#1673ad')
            ax.plot([.6],[row['flat_tail_sensitivity']['events']],'D',mfc='none',color='#9261b2',label='Constant-tail sensitivity only')
        ax.set(title=row['sample'].replace('_',' '), ylabel='Signal events / selected sample', xlim=(-.35,.9), ylim=(0,None))
        ax.set_xticks([]);ax.grid(axis='y',alpha=.2)
        handles,labels=ax.get_legend_handles_labels();legend.update(zip(labels,handles))
    fig.legend(list(legend.values()),list(legend),loc='outside lower center',ncol=2,fontsize=8)
    fig.suptitle(r'Solar $^8$B single-bin SM: nuclear Response; $\Phi=5.46\times10^6$ cm$^{-2}$s$^{-1}$'+'\nExperimental signal fits, not raw candidates; independent of previous multibin analysis',fontsize=11)
    fig.savefig(output/'singlebin_SM_comparison.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,len(records),figsize=(4.3*len(records),4.3),constrained_layout=True,squeeze=False)
    for ax,row in zip(axes[0],records):
        with np.load(output/row['sample']/'sm_prediction.npz') as a:
            t=a['recoil_keV']; known=a['acceptance_known']
            ax.plot(t[known],a['verified_accepted_events_per_keV'][known],color='#1673ad',label='SM x verified Total acceptance')
            if not row['experimental_efficiency_coverage_complete']:
                tail=~known
                tt=np.r_[t[known][-1],t[tail]]; raw=np.r_[a['raw_events_per_keV'][known][-1],a['raw_events_per_keV'][tail]]
                ax.fill_between(tt,0,raw,color='#d5c4e2',alpha=.55,label='Unknown tail envelope (0 <= eff <= 1)')
                ax.plot(tt,raw*row['flat_tail_sensitivity']['epsilon_tail'],'--',color='#9261b2',label='Constant-tail sensitivity')
        ax.set(title=row['sample'],xlabel='True nuclear recoil T [keVnr]',ylabel='Accepted signal events / keVnr',ylim=(0,None));ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('Fresh recoil integrals: these are diagnostic densities, not reconstructed Ne / cS2 bins',fontsize=11)
    fig.savefig(output/'singlebin_recoil_diagnostics.png',dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/solar_b8_singlebin/20261111_response_run1')
    parser.add_argument('--sample',choices=('all',*SAMPLES),default='all')
    parser.add_argument('--xenon-tail',choices=('bounded','flat_sensitivity'),default='bounded')
    args=parser.parse_args();output=args.output.resolve()
    if not output.is_relative_to(ROOT/'outputs/solar_b8_singlebin'):
        raise ValueError('singlebin output must be under outputs/solar_b8_singlebin/, separate from multibin')
    output.mkdir(parents=True,exist_ok=False)
    records=[run_sample(sample,output,args.xenon_tail if sample=='XENONnT' else 'bounded')
             for sample in SAMPLES if args.sample in ('all',sample)]
    complete=all(r['complete_prediction'] for r in records)
    summary={'date':'2026-11-11','analysis':'singlebin_2601_19883','results':records,
             'status':'CALCULATED_WITH_EXPLICIT_TAIL_ASSUMPTION' if complete and args.xenon_tail=='flat_sensitivity' else ('CALCULATED' if complete else 'PARTIAL_XENON_ACCEPTANCE_TAIL'),
             'joint_chi2':sum(r['statistics']['chi2'] for r in records) if complete else None,
             'chi2_range_due_only_to_unknown_tail':[sum(r['profiled_chi2_range_due_only_to_unknown_tail'][i] for r in records) for i in (0,1)],
             'project_flat_tail_sensitivity_joint_chi2':sum(r['flat_tail_sensitivity']['chi2'] if r['sample']=='XENONnT' else r['statistics']['chi2'] for r in records),
             'paper_equivalence':'NOT_CERTIFIED','result_acceptance':'NOT_REVIEWED'}
    save(output/'BENCHMARK_SUMMARY.json',summary)
    plot(output,records)
    table='sample\tSM_count_or_verified_lower\tfull_lower\tfull_upper\tfitted_signal\tstat_sigma\tclaim\n'
    for r in records:
        table+='\t'.join(map(str,[r['sample'],r['counts'][0],*r['full_interval_events'],r['fitted_signal_data']['D'],r['fitted_signal_data']['sigma_stat'],r['claim']]))+'\n'
    (output/'events.tsv').write_text(table,encoding='utf8')
    (output/'README.md').write_text('# Solar B8：单 bin 标准模型实际计算\n\n'
        '[总结果](BENCHMARK_SUMMARY.json) · [数值表](events.tsv) · [信号总数比较](singlebin_SM_comparison.png) · [反冲积分诊断](singlebin_recoil_diagnostics.png)\n\n'
        +''.join(f'- [{r["sample"]}]({r["sample"]}/README.md)\n' for r in records)+
        '\n此处不读取多bin Qy、响应基底、逐箱观测或背景；完整来源与流程见 [主线单bin onboarding](../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md)。XENONnT未知尾段保留区间；紫色空心点/虚线为项目平坦延伸敏感性。\n',encoding='utf8')
    print('Saved',output,'status',summary['status'],'joint_chi2',summary['joint_chi2'],flush=True)


if __name__=='__main__':
    main()
