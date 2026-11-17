"""Rebuild the SAME time-analysis onboarding as an unaccepted r3 draft.

Workflow records only. No physics prediction, compiler promotion or runtime
registration. Old count results remain references, never a new Slow freeze.
"""
from pathlib import Path
import hashlib
import json
import os

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[5]
REVISION='r3-onboarding-restart-20261118'
DATE='2026-11-18'


def read(name):return json.loads((RUN/name).read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):(RUN/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def apply():
    p00,p01,p03=read('P00_SOURCE_REGISTER.yaml'),read('P01_EVIDENCE_LEDGER.yaml'),read('P03_PHYSICS_CONTRACT.yaml')
    decisions=read('DECISION_LOG.json')
    if not any(d.get('id')=='D_RESTART_20261118' for d in decisions['decisions']):
        decisions['decisions'].append(dict(id='D_RESTART_20261118',date=DATE,
            user_instruction='把三个计算入口清理掉先；我要重新处理onboarding，重新走一遍流程计算物理',
            text='同一CsI2021_time_9x11重新整理证据/合同/阶段计划，撤下三个并列入口；原核表直接复用选择沿用',
            scope='document and engineering restart authorization; no new formula/normalization/onset/Slow approval',
            scientific_acceptance='NOT_REVIEWED'))
    decisions['current_review_revision']=REVISION;write('DECISION_LOG.json',decisions)
    source_defs=[
        ('S_LI2026',ROOT/'docs/references/General_CEvNS/2601.19883v2.pdf',
         'G. Li, C.-Q. Song, F.-J. Tang, J.-H. Yu, Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering, arXiv:2601.19883v2 (2026).',
         'PDF p12-19 Eqs40-83/TableIII-IV及p30结论已核读；式75与当前装配的对应存在未闭合问题'),
        ('S_CURRENT_AMPLITUDE',ROOT/'cevns_pyeft/theory/li2026/amplitude.py','Current local one-body amplitude assembly.',
         'flavor_kernel_onebody_li2026与直接R/W收缩已读；未认证与论文式75全等'),
        ('S_CURRENT_R',ROOT/'cevns_pyeft/theory/li2026/responses.py','Current local particle-response polynomials.',
         'R_Delta及强制零R_SigmaPDelta已读；需要独立逐项核验'),
        ('S_RESTART_BUILDER',Path(__file__),'Project deterministic r3 onboarding-restart overlay, 2026-11-18.',
         '仅整理来源、冲突、候选配置和阶段范围，不执行或批准物理计算'),
    ]
    ids={d[0] for d in source_defs};p00['sources']=[s for s in p00['sources'] if s['source_id'] not in ids]
    for sid,path,citation,scope in source_defs:
        p00['sources'].append(dict(source_id=sid,title=citation,citation=citation,source_type='theory_input' if sid=='S_LI2026' else 'legacy_code',
            uri_or_path=os.path.relpath(path,ROOT).replace('\\','/'),original_url='https://arxiv.org/abs/2601.19883v2' if sid=='S_LI2026' else None,
            version=DATE,sha256=sha(path),bytes=path.stat().st_size,accessed=DATE,verification_scope=scope,
            upstream_source_ids=[],numerical_availability='PRESENT',dataset_scope='CsI2021_time_9x11'))
    for source in p00['sources']:
        if source['source_id'] in ('S_DECISION','S_PREPARE'):
            path=ROOT/source['uri_or_path'];source.update(sha256=sha(path),bytes=path.stat().st_size)
        if source['source_id']=='S_TIMING_DRIVER':
            source['verification_scope']='已撤下入口的原字节历史快照；仅作REFERENCE，不是当前计算入口或阶段批准'
    definitions=[
        ('C_RESPONSE_ASSEMBLY_REVIEW','共享RESPONSE装配与论文对应审核',
         dict(state='CONFLICT_PENDING_AUDIT',paper_locator='2601.19883v2 p15 Eq75, p18-19 Eq82',
              implementation='amplitude.py direct contraction; responses.py R_Delta and zero R_SigmaPDelta',
              required='Verify response prefactors, spin/isospin normalization and interference against actual table-generation convention; no correction adopted'),
         'CONFLICT',['S_LI2026','S_CURRENT_AMPLITUDE','S_CURRENT_R','S_LOCAL_W'],['C_RESOURCE_BINDING']),
        ('C_FLUENCE_SCOPE_REVIEW','POT注量与时间支撑域解释',
         dict(eta_cm_minus2=579361763793233.9,adopted_scope=None,
              candidates=['full_support: normalized all-time source with time-window acceptance','reference_window: requires evidence that eta is a 0-6us reference fluence'],
              known='Both numerical definitions are available; closeness to341 is not a selection criterion'),
         'CONFLICT',['S_2211','S_SUP','S_TIME_CODE'],['C_ETA','C_DENOM']),
        ('C_RESTART_SCOPE','本轮重新onboarding范围',
         dict(analysis_id='CsI2021_time_9x11',interaction='SM candidate',nuclear_resource='data/responses/responses_all.json',
              timing_onset_ns=0,plus75ns='REFERENCE_ONLY diagnostic',two_body='not implemented; theory truncation must be disclosed',
              requested=['P01-P07 signal forward','P10 scoped validation'],not_requested=['P08 new Fast','P09 likelihood fit'],
              old_results='REFERENCE_ONLY; no current accepted Slow'),
         'USER_CONFIRMED',['S_DECISION','S_RESTART_BUILDER'],[])
    ]
    new_ids={d[0] for d in definitions};p01['claims']=[c for c in p01['claims'] if c['claim_id'] not in new_ids]
    for cid,field,value,status,sources,inputs in definitions:
        claim=dict(claim_id=cid,field=field,value=value,unit='1',status=status,source_id=sources[0],source_ids=sources,
            locator='r3 restart: explicit source/code comparison and user restart instruction',
            verification_scope='候选整理；不是新公式、新注量或Slow的科学接受',input_claims=inputs,numerical_resource=None,
            verification_checks=dict(numerical_data='PRESENT',direct_material='READ',upstream='SEE_P00',applicability='DRAFT'),
            output_locations=['docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md'],adoption='ADOPTED_DRAFT')
        p01['claims'].append(claim)
        section='nuclear' if cid=='C_RESPONSE_ASSEMBLY_REVIEW' else 'source' if cid=='C_FLUENCE_SCOPE_REVIEW' else 'identity'
        sec=p03['sections'][section];sec['fields'][cid]=dict(value=value,unit='1',evidence_claims=[cid],provenance_status=status,
            decision_status='BLOCKED' if status=='CONFLICT' else 'DRAFT',blocking_scope=['new P07 authoritative freeze'] if status=='CONFLICT' else [])
        if cid not in sec['evidence_refs']:sec['evidence_refs'].append(cid)
    for claim in p01['claims']:
        if claim['claim_id'] in ('C_TIMING_DIAGNOSTIC','C_DIAGNOSTICS'):
            claim.update(status='REFERENCE_ONLY',adoption='LEGACY_DIAGNOSTIC')
            claim['verification_scope']='旧实现/旧配置的诊断值；r3不将其作为已接受的Slow或目标值'
            sec=p03['sections']['prediction']['fields'][claim['claim_id']]
            sec.update(provenance_status='REFERENCE_ONLY',decision_status='DRAFT')
    # Preserve existing resource selection, while making module choices independent.
    p03['module_selection_review']=dict(
        interaction=dict(actual_descriptor='li2026_legacy',theory='SM',status='DRAFT'),
        nuclear_structure=dict(reader='ResponseDB',path='data/responses/responses_all.json',keys={'Cs133':'Cs133','I127':'I'},status='USER_SELECTED_LOCAL_REUSE'),
        kinematics=dict(actual_process_id='elastic_neutrino_nucleus_v1',status='REVIEW_PENDING'),
        cross_section=dict(actual_adapter='Li2026LegacyInteraction',status='BLOCKED_BY_RESPONSE_ASSEMBLY_REVIEW'),
        detector=dict(actual_classes=['CsIGammaResponse','CsI2021Efficiency','CsITimeEfficiency'],status='DRAFT_REVIEW_PENDING'),
        statistics=dict(requested=False,status='NOT_REQUESTED'),
        compiler_binding=dict(status='NOT_RUN',reason='H3 and required shared-theory contract not accepted; do not fabricate a registered99bin profile'))
    p03['scientific_claim']='DRAFT r3: same CsI2021 9x11 SM+local RESPONSE signal forward; no fit, no official onset or full nuclear-theory certification'
    spec=p03['report_spec'];spec.update(revision=REVISION,date=DATE,status='DRAFT_H3_REVIEW_REQUIRED')
    spec['formulas']=[f for f in spec['formulas'] if f['id']!='F_NUCLEAR']
    spec['changes']=['2026-11-18按用户要求重新进行同一99箱分析onboarding，旧计算仅参考，不继承阶段通过',
        '三个并列入口已撤下；保留无CLI的兼容辅助模块，未新建替代计算入口',
        'Interaction/Nuclear/Kinematics/Cross-section/Detector独立列出审核状态',
        '式75装配、核表归一、注量支撑域与两体流截断分别登记缺口；未修改共享公式',
        'P08/P09本轮未请求；阶段报告及Compiler输出只在实际执行后产生']
    issue=dict(id='G_EQ75',item='共享RESPONSE装配与源论文式75对应',kind='THEORY_CONVENTION_CONFLICT',status='BLOCKED',
        available='论文p15/18/19原式、当前amplitude/responses代码及Cs/I实际核表可查',
        needed='核实q²/mN²、-2q/mN、4π/(2J+1)、np/iso归一及DeltaSigma干涉，不通过计数拟合选约定',
        affects=['P04/P05物理接受','P07新权威Slow'],claims=['C_RESPONSE_ASSEMBLY_REVIEW'])
    issue2=dict(id='G_FLUENCE_SCOPE',item='POT总注量与0–6us时间归一解释',kind='NORMALIZATION_CONFLICT',status='BLOCKED',
        available='η由POT/产额/距离计算；两种数值口径均已知',needed='H3明确采用的注量定义与原文依据；不能按结果接近341选择',
        affects=['P03源合同接受','P07总率解释'],claims=['C_FLUENCE_SCOPE_REVIEW'])
    issue3=dict(id='G_TRUNCATION',item='一体流近似与遗漏两体流',kind='THEORY_SCOPE_LIMITATION',status='PARTIAL',
        available='2601.19883v2 p12-13功率计数、p30明确数值仅一体流',
        needed='本轮先明确一体流主张及截断误差未知；若要两体流须另有电流与核矩阵元，不能用非M占比当误差',
        affects=['完整核理论精度声称'],claims=['C_RESTART_SCOPE'])
    spec['issues']=[i for i in spec['issues'] if i['id'] not in ('G_EQ75','G_FLUENCE_SCOPE','G_TRUNCATION')]+[issue,issue2,issue3]
    for row in spec['handoff']:
        if row['capability'].startswith('P07'):
            row.update(state='BLOCKED_BY_CURRENT_PHYSICS_REVIEW',next='先完成H3和P04/P05对应审核，再确定单一阶段计算入口并运行P07')
        if row['capability'].startswith('P10'):row.update(state='NOT_RUN_FOR_R3',next='按r3声明的能力验收；不继承旧诊断PASS')
    for sec in p03['sections'].values():
        if sec.get('decision_status')=='APPROVED':sec['decision_status']='DRAFT'
    p00['revision']=p01['revision']=REVISION
    write('P00_SOURCE_REGISTER.yaml',p00);write('P01_EVIDENCE_LEDGER.yaml',p01);write('P03_PHYSICS_CONTRACT.yaml',p03)
    return len(p00['sources']),len(p01['claims'])


def render_note(current):
    def link(label,p):return '['+label+'](<'+os.path.relpath(p,current.parent).replace('\\','/')+'>)'
    return '\n'.join(['## r3重新onboarding：当前审阅范围','',
        '**同一CsI2021_time_9x11；此版是物理配置草稿，未进入新的正式计数阶段。** 三个并列入口已撤下；旧353.465609及+75ns等结果仅作历史诊断，不是本轮已接受Slow。','',
        '| 独立维度 | 当前候选/资源 | 审核状态 |','|---|---|---|',
        '| Interaction | 原生SM；描述符li2026_legacy | DRAFT，待P04 |',
        '| Nuclear structure | 用户选定原RESPONSE，Cs133/I，np基底 | 原表复用选择保留；外部生成等价待核 |',
        '| Kinematics/Cross-section | 现有elastic_neutrino_nucleus_v1 / Li2026LegacyInteraction | 式75装配与核表归一需P04/P05核对 |',
        '| Detector | 14.6kg；QF→Gamma→PE效率→时间接受；T≥2keVnr候选 | 参数已取得，适用域/低反冲截断待P06复审 |',
        '| Time source | 解析DAR能谱×ROOT时间边缘；0ns | +75ns仅历史对照，官方时钟未验证 |',
        '| Fluence | η=5.793617637932339e14 cm⁻²/味 | full_support与reference_window含义需H3确认 |',
        '| Observable | PE[0,8,12,16,20,24,32,40,48,60]×11时间箱，raw C/AC | 99箱数值已取得；边界来源限制保留 |',
        '| Statistics/Fast | 本轮先做信号前向计算 | P08/P09 NOT_REQUESTED；不运行拟合 |','',
        '已取得官方事件/背景/ROOT、响应系数、原核表与原文。尚缺的是若干物理对应的核验，不是这些数值文件不存在。共享理论公式只在P04/P05核查，实验正文登记模块选择/资源和阻断范围。','',
        'Compiler/Renderer：本轮尚未生成新YAML/NPZ运行包。H3及必要合同接受后，按统一IR→tools/compile_experiment_package.py→机器文件/Physics MD生成，不以旧自定义报告冒充新包。','',
        '需要审核的具体问题：① η按完整时间支撑域还是0–6μs参考窗解释；② 本轮接受的一体流范围及未知两体流误差；③ 背景归一只作分列诊断，暂不认定作者完整模板。共享式75冲突须先核查，不用调参消除。','',
        '当前计划：'+link('Phase0计划',RUN/'00_EXECUTION_PLAN.md')+' · '+link('可恢复进度',RUN/'00_MIGRATION_PROGRESS.md')+' · '+link('来源/冲突',RUN/'P02_MISSING_AND_CONFLICTS.md')+'。',''])


if __name__=='__main__':apply()
