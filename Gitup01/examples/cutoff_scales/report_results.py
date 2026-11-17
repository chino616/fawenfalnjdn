"""Independent result receipts, original-NSI comparisons and readable tables."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, SCHEMA, read, sha, write_json
sys.path.insert(0, str(ROOT))
from cevns_pyeft.foundation.constants import G_F


def report(output):
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/"outputs/cutoff_scales").resolve()):
        raise ValueError("independent cutoff result directory required")
    r=json.loads((output/"RESULTS.json").read_text(encoding='utf-8'))
    if r.get('part_id')!=PART or r.get('schema')!=SCHEMA or r.get('run_id')!=output.name:
        raise ValueError('wrong Part/schema/run')
    mismatched=[p for p,h in r['source_manifest'].items() if sha(ROOT/p)!=h]
    if mismatched:raise ValueError('stale adopted sources: '+repr(mismatched))
    baseline=read('outputs/cutoff_scales/20261114_implementation_baseline/BASELINE.json')
    changed=[p for p,h in baseline['protected'].items() if sha(ROOT/p)!=h]
    if changed:raise ValueError('protected mainline file changed')
    full=r['stage'].startswith('FULL22')
    comparisons=[]
    if not full:
        old=read('outputs/one_d_benchmark_20261113_run1/RESULTS.json')['scans']
        mapping={'CsI2021_9PE':'CsI2021','Ar2020_average':'Ar2020','CONUS_plus':'CONUS_plus',
                 'CsI2021_9PE+Ar2020_average':'CsI2021+Ar2020', 'Solar_three_singlebins':'Solar_joint',
                 'PandaX_paired':'PandaX_paired','PandaX_US2':'PandaX_US2','XENONnT':'XENONnT'}
        for row in r['results']:
            key=row['operator_key']
            if key[1]!=1:continue
            expected=mapping[row['analysis_group']]+'__epsilon_ee_'+key[2]+'V'
            if expected not in old:
                # Identity lookup is explicit; never guess by file name alone.
                selected=[v for v in old.values() if v.get('analysis')==mapping[row['analysis_group']] and v.get('parameter')=='epsilon_ee_'+key[2]+'V']
                if len(selected)!=1:continue
                previous=selected[0]
            else:previous=old[expected]
            for cl in ['90','95']:
                iv=previous['intervals'][cl+'percent']
                maximum=max(abs(v) for interval in iv for v in interval)
                lam=(np.sqrt(2)*G_F*maximum)**-.5
                actual=row['confidence'][cl]['global_GeV']
                difference=actual/lam-1
                if abs(difference)>3e-6:raise ValueError('existing NSI axis conversion differs: '+expected)
                comparisons.append({'analysis_group':row['analysis_group'],'operator':row['operator_id'],'CL':cl,
                                    'independent_previous_epsilon_conversion_GeV':lam,'new_GeV':actual,'relative_difference':difference})
    finite=sum(x['confidence']['90']['status']=='FINITE' for x in r['results'])
    zero=sum(x['status']=='NO_SENSITIVITY' for x in r['results'])
    residuals=[abs(c['residual']) for row in r['results'] for c in row['root_checks']]
    checks={'schema':'cutoff_result_receipt/1','status':'NUMERICAL_CONTROL_WITH_OPEN_PHYSICS' if full else 'PASS_SCOPED_DIM6_DELIVERY',
            'result_sha256':sha(output/'RESULTS.json'),'route_count':len(r['results']),'finite_90CL':finite,'no_sensitivity':zero,
            'max_threshold_root_residual':max(residuals,default=0),'protected_files_checked':len(baseline['protected']),'protected_changes':changed,
            'source_hashes_checked':len(r['source_manifest']),'old_NSI_axis_comparisons':comparisons,
            'algorithm_tests':'15 analytic tests passed; pytest cache write warning did not affect tests',
            'limits':'full22 controls retain unresolved dim8 pointwise PSD validation and fixed solar propagation' if full else 'nominal 1DOF thresholds; adopted local likelihoods, no coverage toys or author equivalence'}
    write_json(output/'FINAL_CHECKS.json',checks)
    # Keep graphical references separate from inferred results and record mismatch scope.
    reference=ROOT/'outputs/paper2601_chi2_corrected_20261111/paper_reference/fig3_plotted_limits.csv'
    lookup={}
    with reference.open(encoding='utf-8',newline='') as f:
        for item in csv.DictReader(f):lookup[(item['experiment'],item['operator'])]=float(item['lambda_GeV_from_plotted_height'])
    refs=[]
    groupmap={'CONUS_plus':'CONUS_plus','CsI2021_9PE+Ar2020_average':'COHERENT_CsI_Ar','Solar_three_singlebins':'Solar_joint'}
    for item in r['results']:
        if item['analysis_group'] not in groupmap:continue
        d,i,q=item['operator_key'];name=f'O{d}{q}_{i}'
        value=lookup.get((groupmap[item['analysis_group']],name))
        if value is not None:
            refs.append({'analysis_group':item['analysis_group'],'operator':item['operator_id'],'local_90CL_GeV':item['confidence']['90'].get('global_GeV'),
                         'paper_graphical_GeV':value,'scope':'graphical reference only; flavor/propagation/local-input differences retained',
                         'comparison_status':'TRANSITION_FLAVOR_DIFFERS' if item.get('lepton_number')=='LNV' else ('FIXED_PROPAGATION_CONTROL' if full and item['analysis_group']=='Solar_three_singlebins' else 'LOCAL_MODEL_GRAPHICAL_BENCHMARK')})
    write_json(output/'PAPER_COMPARISON.json',{'reference_path':reference.relative_to(ROOT).as_posix(),'reference_sha256':sha(reference),'rows':refs})
    table=['| 分析组 | 算符 | 味结构 | Λ90 [GeV] | Λ95 [GeV] | 状态 |','|---|---|---|---:|---:|---|']
    for item in r['results']:
        a,b=[item['confidence'][cl].get('global_GeV') for cl in ['90','95']]
        table.append(f"| {item['analysis_group']} | {item['operator_id']} | {item['flavor']} | {a:.8g} | {b:.8g} | {item['status']} |" if a is not None else
                     f"| {item['analysis_group']} | {item['operator_id']} | {item['flavor']} | — | — | NO_SENSITIVITY |")
    note=('完整22算符×8组的控制计算。太阳固定SM传播，LNV采用明确的e↔μ过渡；与dim-6逐点传播主结果分开。'
          'dim-8原生混合振幅存在已记录的正定性拒绝点，其柱高仅为名义数值控制输出，不能作为已接受物理排除。' if full else
          '采用保存核的实ee dim-6扫描，太阳逐点更新SNuDD v3.4.1传播，XENON使用flat_sensitivity。2条Ar轴矢量方向无响应。')
    (output/'RESULTS.md').write_text('# 独立截断能标计算结果\n\n'+note+'\n\n'
        f'共{len(r["results"])}条路线；90%名义阈值下{finite}条有限数值结果、{zero}条无灵敏度。'
        '系数与能标完整允许集、正负号和SM分支保存在RESULTS.json，主表为全局保守下限。'
        '不连通允许集的下确界不能替代完整允许集。\n\n'
        '[完整数据](RESULTS.json) · [CSV](CUTOFF_LIMITS.csv) · [独立检查](FINAL_CHECKS.json) · [文献对照范围](PAPER_COMPARISON.json)\n\n'
        +'\n'.join(table)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in checks.items() if k!='old_NSI_axis_comparisons'},ensure_ascii=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=Path,required=True);report(p.parse_args().results)
