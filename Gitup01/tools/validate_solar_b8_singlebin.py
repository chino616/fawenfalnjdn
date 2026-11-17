"""Audit current singlebin resources/results, saved statistics and canonical records.

Explicitly writes only the current QA directory. Numerical results and all
original v3.2/multibin files are read-only. Does not scan backup for inputs.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import numpy as np
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cevns_pyeft.experiments.solar_singlebin import load_singlebin
from cevns_pyeft.experiments.runtime import validate_snapshot,ExperimentPrediction,evaluate_experiment
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.experiments.definition import plain
QA=ROOT/'outputs/solar_b8_singlebin/20261111_validation'
OUT=ROOT/'outputs/solar_b8_singlebin/20261111_response_run2'
DATA=ROOT/'data/benchmarks/solar_b8_singlebin_2601_19883'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,value):p.write_text(json.dumps(plain(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')


def main():
    protected=read(ROOT.parent/'重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2/_review/PROTECTED_BASELINE.json')['files']
    changed=[p for p,h in protected.items() if sha(Path(p))!=h]
    put(QA/'PROTECTED_VALIDATION.json',{'checked':len(protected),'changed':changed,'passed':not changed})
    if changed:raise ValueError('protected originals changed: '+str(changed))
    card=read(DATA/'analysis.input.json')
    for name,ref in card['files'].items():
        if sha(DATA/name)!=ref['sha256']:raise ValueError('data hash changed: '+name)
    audit={'card_sha256':sha(DATA/'analysis.input.json'),'numerical_files':card['files'],
        'references':{k:{a:b for a,b in v.items() if a in ['file','sha256','locator']} for k,v in card['references'].items()},
        'statistics_file_sha256':sha(DATA/'fitted_yields.json'),'models':{}}
    for sample in ['PandaX_paired','PandaX_US2','XENONnT']:
        e=load_singlebin(sample);validate_snapshot(e);result=read(OUT/sample/'SM_RESULT.json')
        if (result['physics_fingerprint'],result['analysis_fingerprint'])!=(e.physics_fingerprint,e.analysis_fingerprint):
            raise ValueError('reload/recompute changed physical analysis: '+sample)
        with np.load(OUT/sample/'sm_prediction.npz',allow_pickle=False) as a:
            if not np.array_equal(a['counts'],result['counts']):raise ValueError('saved counts disagree')
        parts={tuple(k.split('/')):np.array(v) for k,v in result['components'].items()}
        p=Prediction(np.array(result['counts']),e.model.binning,parts,result['normalization_ledger'],e.model.describe(),{},
                     {'coverage_complete':result['complete_prediction']})
        runtime=ExperimentPrediction(e.dataset_id,e.definition.analysis_revision,e.analysis_fingerprint,e.physics_fingerprint,
            p,{sample:p},'slow',{'reuse':'saved forward array, same verified physics/analysis fingerprints; no forward rescaling'})
        entry={'physics_fingerprint':e.physics_fingerprint,'snapshot_valid':True,
               'counts_match_saved_npz':True,'coverage':result['claim']}
        if sample!='XENONnT':
            evaluation=evaluate_experiment(e,runtime)
            if abs(evaluation.chi2-result['statistics']['chi2'])>1e-13:raise ValueError('statistics mismatch')
            entry['statistical_evaluation']=plain(evaluation.record)
        else:
            try:evaluate_experiment(e,runtime)
            except ValueError as exc:
                if 'partial acceptance' not in str(exc):raise
                entry['full_chi2_guard']='REJECTED_PARTIAL_AS_REQUIRED'
            else:raise ValueError('missing partial guard')
        audit['models'][sample]=entry
    put(QA/'INPUT_AND_SNAPSHOT_AUDIT.json',audit)
    schema=read(ROOT/'workflows/_shared/schemas/phase-result.schema.yaml');phases=[];progress_revisions={}
    for fam,ds,revision in [('PandaX4T','PandaX4T_2024_US2',13),('XENONnT','XENONnT_2024_SolarB8',12)]:
        run=ROOT/f'workflows/cevns-pyeft/runs/{fam}/{ds}'
        for p in (run/'phases').glob('*_singlebin2601.md'):
            value=json.loads(re.search(r'```json phase-result\n(.*?)\n```',p.read_text(encoding='utf8'),re.S)[1])
            jsonschema.validate(value,schema);phases.append(p.relative_to(ROOT).as_posix())
        progress=json.loads(re.search(r'```json\n(.*?)\n```',(run/'00_MIGRATION_PROGRESS.md').read_text(encoding='utf8'),re.S)[1])
        progress_revisions[fam]=progress['revision']
        # Later parallel analyses may advance the index; this audit owns only
        # the frozen SM branch and must not require it to remain current.
        branch=progress.get('parallel_analyses',{}).get('singlebin_2601_19883',{})
        if (progress['revision']<revision or 'multibin_2411_11749' not in progress['parallel_analyses']
                or branch.get('input_card_sha256')!=sha(DATA/'analysis.input.json')
                or branch.get('decision_ref')!='D0005' or branch.get('write_ref')!='W0005'):
            raise ValueError('canonical progress identity changed')
    put(QA/'CANONICAL_VALIDATION.json',{'phase_reports':phases,'phase_schema_passed':True,
        'progress_revisions':progress_revisions,'parallel_analyses':True,'scientific_result_acceptance':'NOT_REVIEWED'})
    initial=ET.parse(QA/'tests.xml').getroot();final=ET.parse(QA/'singlebin_final.xml').getroot()
    legacy=[c for c in initial.iter('testcase') if not c.attrib.get('classname','').startswith('tests.test_solar_singlebin')]
    new=list(final.iter('testcase'))
    if len(legacy)!=43 or len(new)!=18 or any(c.find('failure') is not None or c.find('error') is not None for c in legacy+new):
        raise ValueError('expected final 18+43 passing tests')
    put(QA/'TEST_VALIDATION.json',{'distinct_tests_passed':61,'current_singlebin_passed':18,
        'unchanged_legacy_nuclear_CsI2017_CsI2021_Ar2020_passed':43,
        'initial_endpoint_test_issue':'raw legacy API rejects its roundoff-sized negative even-Xe kernel at exact endpoint; new tests strictly compare original API inside support and independently require finite nonnegative exact endpoints; shared core, reference arrays and tolerances unchanged',
        'reports':['tests.xml','singlebin_final.xml'],'final_failures':0})
    (QA/'README.md').write_text('# 单bin主线验收：2026-11-11\n\n'
        '[新onboarding](../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md) · [实际SM运行](../20261111_response_run2/README.md)\n\n'
        '- [测试](TEST_VALIDATION.json)：新分支18项＋原核Response/COHERENT回归43项通过；保留首次端点比较测试失败记录，修正比较方式后重跑全部新分支18项。共享物理核心、原参考与容差未改。\n'
        '- [原文件保护](PROTECTED_VALIDATION.json)：106份原v3.2/多bin模型/数据/冻结结果逐字节不变。\n'
        '- [来源、数值与实际快照](INPUT_AND_SNAPSHOT_AUDIT.json)：当前card/数值哈希、物理与analysis指纹；保存的同一前向数组通过Runtime复核统计来源及结果。\n'
        '- [正式阶段和进度](CANONICAL_VALIDATION.json)：8份阶段报告schema通过；两种分析并列，科学接受NOT_REVIEWED。\n'
        '- [文档链接](LINK_VALIDATION.json)：标准MD检查；[内置资源清单](BUILTIN_RESOURCE_VALIDATION.json)单独检查，三份未改动的COHERENT YAML与全局清单哈希不一致，未改表使其通过，不影响本次独立单bin输入/快照核验。\n'
        '- [文件归属](FILE_LIFECYCLE.json)：新文件、README、上级导航、消费者与备份。\n'
        '- [渲染](READABILITY_VALIDATION.json) · [实际预览](preview/README.md)。\n\n'
        'XENONnT末点到3keV接受度仍MISSING；严格结果为区间，完整联合点χ²空置。核表外部认证和缺Xe124/126分别登记，不宣称论文精确复现。\n',encoding='utf8')
    print('PASS: protected',len(protected),'phase schemas',len(phases),'tests 61; current snapshots/statistics verified')


if __name__=='__main__':main()
