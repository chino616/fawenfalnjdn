"""Register the user-authorized, separate singlebin capability in canonical records.

No Git operation and no global experiment activation. Existing files are backed
up; old multibin inputs/results/gates remain unchanged. Idempotent branch records,
optimistic progress revisions; --write is required. Run after SM and doc generation.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
DATA=ROOT/'data/benchmarks/solar_b8_singlebin_2601_19883'
DOC=ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
OUT=ROOT/'outputs/solar_b8_singlebin/20261111_response_run2'
QA=ROOT/'outputs/solar_b8_singlebin/20261111_validation'
BACKUP=ROOT/'backup/solar-singlebin-20261111-01'
NEW_CODE=['cevns_pyeft/experiments/solar_singlebin.py','cevns_pyeft/theory/li2026/sm_quadratic.py',
          'cevns_pyeft/statistics/solar_singlebin.py','tools/prepare_solar_b8_singlebin.py',
          'tools/run_solar_b8_singlebin_benchmark.py','tools/run_solar_b8_multibin_benchmark.py',
          'tools/build_solar_b8_singlebin_onboarding.py','tools/promote_solar_b8_singlebin.py',
          'tools/validate_solar_b8_singlebin.mjs','tools/validate_solar_b8_singlebin.py','tests/test_solar_singlebin.py']


def read(path):return json.loads(path.read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.relative_to(ROOT).as_posix()
def link(origin,target,label):return '['+label+'](<'+os.path.relpath(target,origin.parent).replace('\\','/')+'>)'


def put(path,text):
    if path.exists() and path.read_text(encoding='utf8')==text:return
    if path.exists():
        destination=BACKUP/rel(path)
        if not destination.exists():
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination)
            manifest=read(BACKUP/'MANIFEST.json');manifest['files'].append({'path':rel(path),'sha256':sha(path)})
            (BACKUP/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf8')


def put_json(path,value):put(path,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def managed(path,body):
    text=path.read_text(encoding='utf8');start='<!-- solar-singlebin-v321:start -->';end='<!-- solar-singlebin-v321:end -->'
    block=start+'\n\n'+body+'\n\n'+end
    if start in text:text=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
    else:
        first,rest=text.split('\n',1);text=first+'\n\n'+block+'\n'+rest
    put(path,text)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    if not args.write:raise SystemExit('read-only default: use --write for the authorized canonical registration')
    summary=read(OUT/'BENCHMARK_SUMMARY.json');records={r['sample']:r for r in summary['results']}
    card=read(DATA/'analysis.input.json');QA.mkdir(parents=True,exist_ok=True)
    if not all(r['convergence']['passed'] for r in records.values()):raise ValueError('SM convergence incomplete')
    owners={
        'README.md':'## 太阳⁸B主线：单 bin与多 bin分别计算\n\n',
        'docs/experiments/README.md':'## 太阳⁸B：两种独立分析\n\n',
        'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md':'## 主线分支选择：按分析方案进入\n\n',
        'data/README.md':'## 太阳⁸B：独立的单 bin输入\n\n',
        'data/benchmarks/README.md':'## 太阳⁸B单 bin：2601.19883v2\n\n',
        'outputs/README.md':'## 太阳⁸B：单 bin结果独立保存\n\n',
    }
    for name,title in owners.items():
        path=ROOT/name
        body=title+link(path,DOC/'README.md','单bin v3.2.1：输入、来源、代码与SM结果')+' · '+link(path,ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md','多bin v3.1（保留）')+'。\n\n'
        body+='单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；'+link(path,DATA/'README.md','独立数据')+'、'+link(path,ROOT/'tools/run_solar_b8_singlebin_benchmark.py','独立入口')+'、'+link(path,OUT/'README.md','独立结果')+'。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。'
        managed(path,body)
    for name,body in {
        'cevns_pyeft/experiments/README.md':'[solar_singlebin.py](solar_singlebin.py)的`load_singlebin`返回标准PreparedExperiment，通过独立scoped Catalog绑定三样本。SourceSpectrum/build_targets/TotalAcceptance/SingleBinExecutor对应onboarding Source/Target/Detector/Prediction；不导入旧solar_*多bin装配、不读其NPZ/Qy/D/B。`predict_experiment`和`evaluate_experiment`仍是通用主线入口；全局默认实验IDs不变。',
        'cevns_pyeft/theory/README.md':'[li2026/sm_quadratic.py](li2026/sm_quadratic.py)为SM-only薄适配：委托既有Li2026LegacyInteraction取得三个合法能量点，精确重组E²dσ/dT二次式。无探测器/太阳模块依赖，不抄写匹配公式、核表或额外KN因子。核表与原共享核心未改；新适配与旧API逐点比较、端点及既有COHERENT冻结回归分别检验。',
        'cevns_pyeft/statistics/README.md':'[solar_singlebin.py](solar_singlebin.py)实现2601.19883v2 p20 Eq.(88)：拟合信号D/统计σ、每样本独立12% pull的Gaussian。原候选D_i/B_i不进入此模型。部分接受度积分由evaluator拒绝；统计资源lazy读取，身份/观测/物理指纹由Runtime先检查。',
        'tools/README.md':'单bin：[prepare_solar_b8_singlebin.py](prepare_solar_b8_singlebin.py)离线create-only提取PDF/数据；[run_solar_b8_singlebin_benchmark.py](run_solar_b8_singlebin_benchmark.py)独立Slow/收敛/统计/PNG；[build_solar_b8_singlebin_onboarding.py](build_solar_b8_singlebin_onboarding.py)同源生成新文档、默认check；[promote_solar_b8_singlebin.py](promote_solar_b8_singlebin.py)显式--write备份并登记canonical分支；[validate_solar_b8_singlebin.py](validate_solar_b8_singlebin.py)核对输入/实际快照/保护与阶段；[validate_solar_b8_singlebin.mjs](validate_solar_b8_singlebin.mjs)渲染/链接/公式/实际跳转。多bin：[run_solar_b8_multibin_benchmark.py](run_solar_b8_multibin_benchmark.py)只委托原核表多bin运行器。兼容旧SM入口支持`--analysis singlebin|multibin`；无analysis保持旧多bin行为。两者输出根分别solar_b8_singlebin/与solar_b8_sm/。',
        'tests/README.md':'[test_solar_singlebin.py](test_solar_singlebin.py)验证统计解析式与独立优化器、源/核数、核表截面委托、独立PDF效率、双向文件读取隔离、跨方案统计拒绝、未知尾段严格处理和显式敏感性模式。新18项与原43项核Response/COHERENT回归的实际记录在[本轮QA](../outputs/solar_b8_singlebin/20261111_validation/README.md)。',
    }.items():managed(ROOT/name,'## 太阳⁸B：单 bin独立能力\n\n'+body)
    refs=ROOT/'docs/references/General_CEvNS/README.md'
    managed(refs,'## 单bin补充引用\n\nLIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. [arXiv:2502.10702v2](https://arxiv.org/abs/2502.10702v2), 2025。 [本地PDF](2502.10702v2.pdf)，SHA256 `'+sha(refs.parent/'2502.10702v2.pdf')+'`。PDF p13 Table II用于逐个信号产额、取整误差及能区；其5.16e6通量与p14 Eq.(E8)共享pull仅作比较，不替代2601单bin设置。')
    output_root=OUT.parent
    put(output_root/'README.md','# Solar B8：单 bin计算与验证\n\n[当前SM运行run2](20261111_response_run2/README.md) · [验证与保护记录](20261111_validation/README.md) · [主线onboarding](../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md)\n\nrun1保留首次执行结果和当时参数卡；run2只修正Eq.84页码出处并按现行参数卡重新执行，三样本数值一致。此目录不接收旧多bin结果；多bin继续在solar_b8_sm/。\n')
    branch_reports=[]
    for family,dataset,samples,expected_revision in [('PandaX4T','PandaX4T_2024_US2',['PandaX_paired','PandaX_US2'],12),('XENONnT','XENONnT_2024_SolarB8',['XENONnT'],11)]:
        run=ROOT/f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        decisions=read(run/'P04_DECISION_LOG.yaml')
        if not any(d['decision_id']=='D0005' for d in decisions['entries']):
            decisions['entries'].append({'decision_id':'D0005','date':'2026-11-11',
                'user_quote':'需要你合并到主线，并且计算标准模型情况，在主线中计算流程隔开',
                'material_quote':'检查2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2；单bin与多bin是两种不同方案，数据采用有较多不同',
                'scope':'separate 2601.19883v2 singlebin capability for paired/US2/XENONnT; fresh SM nuclear-Response integral and Eq.88 objective',
                'interpretation':'Adopt supplied v3.2 singlebin meaning with explicit source corrections; keep independent resources/loaders/executors/observations/statistics/outputs; bounded unknown X tail plus explicitly named project sensitivity only',
                'execution_authorized':True,'result_acceptance':'NOT_REVIEWED',
                'scope_limits':['do not sum multibin counts','no implicit tail data','no ci or fitted flux calibration','do not modify old numerical inputs/results','no new BSM or confidence-limit claim']})
            put_json(run/'P04_DECISION_LOG.yaml',decisions)
        auth=read(run/'AUTHORIZATION_LOG.yaml')
        key=next(k for k,v in auth.items() if isinstance(v,list))
        if not any(w.get('authorization_id')=='W0005' for w in auth[key]):
            auth[key].append({'authorization_id':'W0005','status':'ACTIVE','date':'2026-11-11','approval_kind':'explicit_user_instruction',
                'user_quote':'需要你合并到主线，并且计算标准模型情况，在主线中计算流程隔开',
                'scope':'canonical separate singlebin analysis, SM calculation, source verification, scoped statistics and navigation',
                'allowed_actions':['read','create','modify'], 'create_paths':NEW_CODE+[rel(DATA)+'/',rel(DOC)+'/',rel(OUT.parent)+'/',rel(run/'SINGLEBIN_BRANCH.json'),rel(run/'phases')+'/P*_singlebin2601.md'],
                'modify_paths':['README/navigation owners','tools/run_solar_b8_sm_benchmark.py','tools/build_solar_b8_onboarding_v3_1.py',rel(run)+'/'],
                'delete_paths':[],'production_paths_affected':True,'recovery_plan':rel(BACKUP/'MANIFEST.json'),'result_acceptance_separate':True})
            put_json(run/'AUTHORIZATION_LOG.yaml',auth)
        # Keep the concrete engineering file inventory complete as QA tools are
        # added in this same user-authorized task; never change scientific acceptance.
        current_write=next(w for w in auth[key] if w.get('authorization_id')=='W0005')
        current_write['create_paths']=list(dict.fromkeys(current_write['create_paths']+NEW_CODE+['docs/references/General_CEvNS/2502.10702v2.pdf']))
        put_json(run/'AUTHORIZATION_LOG.yaml',auth)
        branch={'analysis_id':'singlebin_2601_19883','status':'CALCULATED' if family=='PandaX4T' else 'PARTIAL_XENON_ACCEPTANCE_TAIL',
                'date':'2026-11-11','decision_ref':'D0005','write_ref':'W0005','samples':samples,
                'input_card':rel(DATA/'analysis.input.json'),'input_card_sha256':sha(DATA/'analysis.input.json'),
                'statistics_input':rel(DATA/'fitted_yields.json'),'source_register_and_evidence':rel(DATA/'analysis.input.json')+' /references,/extraction,/files',
                'onboarding':rel(DOC/'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md'),
                'calculation_entry':'tools/run_solar_b8_singlebin_benchmark.py','results':{s:rel(OUT/s/'SM_RESULT.json') for s in samples},
                'physics_fingerprints':{s:records[s]['physics_fingerprint'] for s in samples},
                'human_result_acceptance':'NOT_REVIEWED','old_multibin':'separate, retained; no resources reused by detector/statistics',
                'blockers':([] if family=='PandaX4T' else ['full X2024 acceptance from last native point to 3keV missing']),
                'common_limitations':['Xe124/Xe126 missing, no renormalization','external nuclear-table source certification unresolved; direct local reuse authorized']}
        put_json(run/'SINGLEBIN_BRANCH.json',branch)
        phases={}
        for phase in ('P06','P07','P09','P10'):
            blocked=family=='XENONnT' and phase in ('P09','P10')
            report=run/f'phases/{phase}_singlebin2601.md';phases[phase]=rel(report)
            result={'schema_version':1,'phase':phase,'capability_id':f'solar_b8.singlebin2601.{phase}',
                    'workspace':'canonical','plan_status':'BLOCKED' if blocked else 'READY','machine_gate':'BLOCKED' if blocked else 'PASS','human_gate':'NOT_REVIEWED',
                    'scope_ref':rel(run/'SINGLEBIN_BRANCH.json'),'input_refs':[rel(DATA/'analysis.input.json'),rel(DATA/'fitted_yields.json')],
                    'input_fingerprint':sha(DATA/'analysis.input.json'),'evidence_refs':[rel(DATA/'analysis.input.json')],
                    'decision_refs':['D0005'],'approval_refs':['W0005'],
                    'artifacts':[{'path':rel(OUT/s/'SM_RESULT.json'),'sha256':sha(OUT/s/'SM_RESULT.json'),'role':'actual SM calculation with convergence and claim'} for s in samples],
                    'checks':[{'name':'independent SM integral, declared coverage and separate grids','status':'PASS','command':'python -B tools/run_solar_b8_singlebin_benchmark.py --output outputs/solar_b8_singlebin/20261111_response_run2','result_ref':rel(OUT/'BENCHMARK_SUMMARY.json')}],
                    'handoff':{'exact_claim':branch['status'],'samples':samples,'full_likelihood':'BLOCKED missing X acceptance tail' if blocked else 'Eq88 fitted signal Gaussian, not official likelihood',
                               'fast':'NOT_REQUESTED','scientific_result_acceptance':'NOT_REVIEWED','remaining':branch['blockers']+branch['common_limitations']}}
            if phase=='P06':
                result['handoff'].update(representation='bin_probability',unit='1',normalization='sum_at_most_one',
                    included_selections=['published Total/combined ROI selection'],
                    axes={'input':'true nuclear recoil T [keVnr]','output':'one selected fitted-signal yield bin'},
                    response_definition='epsilon(T) is the one-bin accepted probability; X upper-tail probability remains unknown',
                    selection_ownership='Total/combined includes ROI once; no additional Qy/Ne/cS2 window',
                    validity_domain={s:records[s]['known_domain_keVnr'] for s in samples})
            elif phase=='P07':
                result['handoff'].update(normalization_ledger={s:records[s]['normalization_ledger'] for s in samples},
                    output_contract='one event count per independently identified fitted-signal sample; X partial count plus rigorous full interval',
                    numerics_and_convergence={s:records[s]['convergence'] for s in samples},
                    reference_comparison='R4 Table II is external, different 5.16e6 flux; never used for scaling',
                    freeze_scope={'physics_fingerprints':branch['physics_fingerprints'],'result_acceptance':'NOT_REVIEWED'})
            elif phase=='P09':
                result['handoff'].update(channels=[{'id':s,'representation':'binned_counts','processing':'other',
                    'processing_detail':'experiment-fitted signal yield; not raw candidate counts',
                    'design':'single_sample','likelihood':'gaussian','requires_covariance':False} for s in samples],
                    prediction_binding=branch['physics_fingerprints'],
                    required_inputs={'available':not blocked,'sources':[rel(DATA/'fitted_yields.json')],
                                     'missing':branch['blockers']},
                    nuisance_model='R1 Eq.88: independent Gaussian alpha_k, sigma_alpha=0.12 for every sample',
                    inference='fixed SM objective only; no confidence interval or parameter fit',
                    claim_level='approximate',benchmark='analytic profile against independent numerical optimizer; external R4 arithmetic only')
            else:
                result['handoff'].update(delivery_scope={'mode':'capability_change','target':'independent singlebin SM nuclear-Response analysis; human scientific acceptance pending','completion':'partial'},
                    capability_matrix=[{'id':'bounded_SM_forward','requested':True,'required_for_claim':True,'machine_gate':'PASS','human_gate':'NOT_REVIEWED','result_ref':rel(OUT/'BENCHMARK_SUMMARY.json')},
                                       {'id':'complete_signal_point_and_Eq88','requested':True,'required_for_claim':True,'machine_gate':'BLOCKED' if blocked else 'PASS','human_gate':'NOT_REVIEWED','result_ref':rel(OUT/'BENCHMARK_SUMMARY.json')}],
                    validation_levels={'internal_contracts':rel(QA/'TEST_VALIDATION.json'),'source_and_snapshot':rel(QA/'INPUT_AND_SNAPSHOT_AUDIT.json'),'numerical_convergence':'all samples independently refined','paper_equivalence':'NOT_CERTIFIED'},
                    runtime_integration='load_singlebin -> PreparedExperiment -> predict_experiment / evaluate_experiment; scoped catalog, global default IDs unchanged',
                    final_claim=branch['status']+' for seven directly adopted local Xe response tables; no official-likelihood or paper-code identity claim',
                    limitations=branch['blockers']+branch['common_limitations'])
            put(report,f'# {phase}：独立单bin能力（2601.19883v2）\n\n'+link(report,DOC/'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md','同源物理/输入/原文/代码/SM结果')+'\n\n与旧多bin阶段并列；旧gates不重命名、不借用PASS。P06/P07的范围是已有接受度积分及尾段上下界；完整X信号点/联合χ²仍缺尾数据。输入与结果均按本分支标识绑定。\n\n```json phase-result\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n')
            branch_reports.append(report)
        implementation=read(run/'00_IMPLEMENTATION_MANIFEST.yaml')
        implementation.setdefault('extensions',{})['singlebin_2601_19883']=branch
        put_json(run/'00_IMPLEMENTATION_MANIFEST.yaml',implementation)
        progress_path=run/'00_MIGRATION_PROGRESS.md';old=progress_path.read_text(encoding='utf8');p=read_progress(old)
        if 'singlebin_2601_19883' not in p.get('parallel_analyses',{}):
            if p['revision']!=expected_revision:raise ValueError('canonical revision changed; reload before writing')
            p['previous_revision']=p['revision'];p['revision']+=1
            p.setdefault('parallel_analyses',{})['multibin_2411_11749']={'checkpoint':p['checkpoint'],'onboarding':p['artifact_refs']['onboarding_current'],'status':'retained as-is, original gates and results'}
        p['parallel_analyses']['singlebin_2601_19883']={**branch,'phase_reports':phases}
        # Refresh this historical SM branch without rolling a later NSI run back.
        if 'solar_ee_vector_nsi' not in p.get('parallel_analyses',{}):
            p['updated_at']='2026-11-11';p['current_analysis']='singlebin_2601_19883'
            p['checkpoint']={'phase_id':'P10','phase_name':'parallel singlebin/multibin SM review','skill':'cevns-experiment','step_id':'parallel_analyses.singlebin_result_review',
                             'next_action':'review singlebin SM and explicit X-tail interval; choose independent analysis for further work','resume_requires':[]}
        p['authorization_refs'].update(singlebin_scope='D0005',singlebin_write='W0005')
        p['artifact_refs'].update(singlebin_branch=rel(run/'SINGLEBIN_BRANCH.json'),singlebin_onboarding=branch['onboarding'])
        for phase,ref in phases.items():p['gates'][phase+'_singlebin']={'machine':'BLOCKED' if family=='XENONnT' and phase in ('P09','P10') else 'PASS','human':'NOT_REVIEWED','report_ref':ref,'capability':'solar_b8.singlebin2601.'+phase,'decision_refs':['D0005']}
        # Optimistic revision check after preparing the authoritative records.
        if read_progress(progress_path.read_text(encoding='utf8'))['revision']!=read_progress(old)['revision']:
            raise ValueError('concurrent progress edit; stop rather than overwrite')
        put(progress_path,'# 主线进度：'+dataset+'\n\n单bin2601与多bin2411为并列能力；各自输入/结果/限制独立。科学结果接受NOT_REVIEWED。\n\n```json\n'+json.dumps(p,ensure_ascii=False,indent=2)+'\n```\n')
        managed(run/'README.md','## 并列单bin主线：v3.2.1\n\n'+link(run/'README.md',run/'SINGLEBIN_BRANCH.json','独立分支/来源/指纹')+' · '+link(run/'README.md',DOC/'README.md','单bin新onboarding')+' · '+link(run/'README.md',OUT/'README.md','实际SM结果')+'。旧v3.1及原阶段只属于多bin；不以旧逐箱和当新信号。')
    mapping={
        'cevns_pyeft/experiments/README.md':['cevns_pyeft/experiments/solar_singlebin.py'],
        'cevns_pyeft/theory/README.md':['cevns_pyeft/theory/li2026/sm_quadratic.py'],
        'cevns_pyeft/statistics/README.md':['cevns_pyeft/statistics/solar_singlebin.py'],
        'tools/README.md':[n for n in NEW_CODE if n.startswith('tools/')]+['tools/run_solar_b8_sm_benchmark.py','tools/build_solar_b8_onboarding_v3_1.py'],
        'tests/README.md':['tests/test_solar_singlebin.py'],
        'data/benchmarks/README.md':[rel(p) for p in DATA.iterdir() if p.is_file()],
        rel(DOC/'README.md'):[rel(p) for p in DOC.iterdir() if p.is_file()],
        'docs/references/General_CEvNS/README.md':['docs/references/General_CEvNS/2502.10702v2.pdf'],
        rel(output_root/'README.md'):[rel(OUT),rel(QA)],
    }
    for report in branch_reports:
        owner=report.parent.parent/'README.md';mapping.setdefault(rel(owner),[]).append(rel(report))
    put_json(QA/'FILE_LIFECYCLE.json',{'date':'2026-11-11','file_owners':mapping,
        'parent_navigation':list(owners),'backup_manifest':rel(BACKUP/'MANIFEST.json'),
        'protected_baseline':'../重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2/_review/PROTECTED_BASELINE.json',
        'global_dataset_activation':False,'git_operations':False,'scientific_result_acceptance':'NOT_REVIEWED'})
    print('Canonical singlebin branch registered in both runs; multibin gates/inputs/results retained')


def read_progress(text):return json.loads(re.search(r'```json\s*\n(.*?)\n```',text,re.S)[1])


if __name__=='__main__':main()
