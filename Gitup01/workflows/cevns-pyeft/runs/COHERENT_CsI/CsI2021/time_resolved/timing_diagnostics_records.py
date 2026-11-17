"""Deterministic diagnostic overlay for r2; never grants a physics approval.

Called after prepare_records.build_records so rebuilding onboarding preserves
the 2026-11-17 timing controls and source review. Runtime does not import this.
"""
from pathlib import Path
import hashlib
import json
import os

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[5]
DATE = '2026-11-17'
REVISION = 'r2+timing-diagnostics-20261117'
USER = ROOT.parent / '重构/2026-11-17 核心修改代码集/2026-11-17 nu mu'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def apply():
    paths = {f: RUN/f for f in ('P00_SOURCE_REGISTER.yaml','P01_EVIDENCE_LEDGER.yaml','P03_PHYSICS_CONTRACT.yaml')}
    p00, p01, p03 = (json.loads(p.read_text('utf8')) for p in paths.values())
    new_sources = [
        ('S_TIMING_README', USER/'README.md', '用户提供νμ交接说明：75ns为诊断，非已验证时钟修正'),
        ('S_TIMING_HANDOFF', USER/'HANDOFF_PROMPT.md', '用户提供主线接入建议：固定观测效率/窗口和零位移分母'),
        ('S_TIMING_ZIP', next(USER.glob('*.zip')), '用户交接包：独立KN与背景适配器及测试；不能认证原生SM主线'),
        ('S_TIMING_ADAPTER', ROOT/'examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py', '本次默认保持的可选时间/背景诊断适配器'),
        ('S_TIMING_DRIVER', ROOT.parent/'重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py', '本次原生SM和KN重新积分、逐箱对照生成器'),
    ]
    ids = {s[0] for s in new_sources}
    p00['sources'] = [s for s in p00['sources'] if s['source_id'] not in ids]
    for sid, path, title in new_sources:
        p00['sources'].append(dict(source_id=sid,title=title,citation=title,source_type='legacy_code',
            uri_or_path=os.path.relpath(path,ROOT).replace('\\','/'),original_url=None,version=DATE,
            sha256=sha(path),bytes=path.stat().st_size,accessed=DATE,
            verification_scope='已读直接材料并运行独立及主线数值对照；75ns仍为可选诊断，官方时钟起点未验证',
            upstream_source_ids=[],numerical_availability='PRESENT',dataset_scope='CsI2021_time_9x11'))
    for s in p00['sources']:
        if s['source_id']=='S_PREPARE':
            s.update(sha256=sha(RUN/'prepare_records.py'),bytes=(RUN/'prepare_records.py').stat().st_size,
                     version='r2 builder + 20261117 deterministic diagnostic overlay')
    value=dict(default_shift_ns=0,diagnostic_shifts_ns=[-125,-50,0,50,75,125],
        positive_shift='h(t-delta), source delayed; observer bins/efficiency fixed',
        q='unshifted integral of full-support normalized h from 0 to 6 us',
        default_fluence_scope='reference_window',scopes=['reference_window','full_support'],
        default_background_mode='raw',background_modes=['raw','prior_posteff','bestfit_posteff','prior_preeff'],
        signal_and_neutrons_shift_together=True,SSB_shifted=False,
        official_onset_verified=False,flight_time_added=False,
        prior_posteff_zero_shift_ROI_events=[18.4,5.6],bestfit_posteff_zero_shift_ROI_events=[17.3,5.5],
        native_nominal_reference_events=353.46560868634367,native_full_support_reference_events=329.01642259688515,
        KN_nominal_reference_events=333.11348797594866,KN_plus75_reference_events=331.2663916870358)
    claim=dict(claim_id='C_TIMING_DIAGNOSTIC',field='20261117可选时间诊断与默认保持',value=value,unit='ns or explicitly named events',
        status='PROJECT_DERIVED',source_id='S_TIMING_README',source_ids=[s[0] for s in new_sources],
        locator='README/HANDOFF timing convention; handoff/background_shift.py; timing_audit/time_weight_shift_adapter.py; main diagnostic driver',
        verification_scope='工程可选控制；默认0ns/raw/reference_window。75ns可改善prompt形状但不是已证明的官方时间零点，KN与原生SM分别比较',
        input_claims=['C_TIME_MARGINAL','C_DENOM','C_TIME_EFF','C_PRIORS'],numerical_resource=None,
        verification_checks=dict(numerical_data='PRESENT',direct_material='READ',upstream='SEE_P00',applicability='DRAFT'),
        output_locations=['docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md#prediction'],adoption='ADOPTED_DRAFT')
    p01['claims']=[c for c in p01['claims'] if c['claim_id']!=claim['claim_id']]+[claim]
    section=p03['sections']['prediction']
    section['fields'][claim['claim_id']]=dict(value=value,unit=claim['unit'],evidence_claims=[claim['claim_id']],
        provenance_status=claim['status'],decision_status='DRAFT',blocking_scope=['official timing-onset certification'])
    if claim['claim_id'] not in section['evidence_refs']:section['evidence_refs'].append(claim['claim_id'])
    p03['timing_diagnostic_controls']=value
    spec=p03['report_spec'];spec['revision']=REVISION;spec['date']=DATE
    change='2026-11-17新增可选时间诊断：默认0ns不变；信号/BRN/NIN同步源平移、固定观测效率和零位移分母；原生SM与KN分开重算'
    if change not in spec['changes']:spec['changes'].append(change)
    issues=[dict(id='G_CLOCK',item='ROOT时钟起点与prompt νμ时间形状',kind='UNVERIFIED_ONSET',status='PARTIAL',
        available='0与+75ns诊断、固定观测窗口/效率的实现及交接包测试；ROOT时间边缘保持原样',
        needed='发布者的ROOT时钟起点、onset定义和作者逐分量时间模板；不能把19.3m/c自动再加一次',
        affects=['官方时间零点认定','prompt逐箱作者复现'],claims=['C_TIMING_DIAGNOSTIC']),
        dict(id='G_FIG1',item='论文图形与正文积分的口径',kind='SOURCE_LEVEL_DIFFERENCE',status='PARTIAL',
        available='已核验原始矢量图与主论文内嵌几何一致；图形信号积分约312.59；截图proxy不作权威',
        needed='作者原始模板解释Fig.1可见曲线与正文306±20、PE/time残差积分的差别',
        affects=['论文图精确总率复现','逐味实验显著性'],claims=['C_TIMING_DIAGNOSTIC'])]
    spec['issues']=[i for i in spec['issues'] if i['id'] not in {r['id'] for r in issues}]+issues
    for issue in spec['issues']:
        if issue['id']=='G_CONFIG':
            issue['available']='统一14.6kg/官方效率/解析DAR谱的原生SM353.465609及全支撑329.016423已生成；20261117高网格逐箱复核一致'
            issue['needed']='同条件本地数值已完成；作者模型/时钟/背景口径等价仍依赖G_CLOCK/G_BG/G_THEORY，不由数值复核认证'
    for data in (p00,p01):data['revision']=REVISION
    for path,data in zip(paths.values(),(p00,p01,p03)):
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return len(p00['sources']), len(p01['claims'])


def render_note(current):
    """Generated text from the same P03 controls, with navigable primary inputs."""
    c=json.loads((RUN/'P03_PHYSICS_CONTRACT.yaml').read_text('utf8'))['timing_diagnostic_controls']
    def link(label,path):
        return '['+label+'](<'+os.path.relpath(path,current.parent).replace('\\','/')+'>)'
    lines=['## 2026-11-17 νμ时间诊断补充（默认保持）','',
        f"默认 Δt={c['default_shift_ns']} ns，注量口径 `{c['default_fluence_scope']}`，中子模式 `{c['default_background_mode']}`。新增控制不授予论文等价、时钟校准或拟合接受。",'',
        r'对完整支撑域归一化的时间源 $h_f$，使用 $W_{fj}(\delta)=\int_{t_j}^{t_{j+1}}h_f(t-\delta)\epsilon_T(t)dt/q_f$；$q_f=\int_0^6h_f(t)dt$ 固定为零位移值。`full_support` 模式的分母为1。两模式使用相同数值η，是不同注量口径的对照，不能直接删除 `/q` 当作物理修复。','',
        '正位移使源晚到；观测箱及εT(t_rec)固定。信号和BRN/NIN同步平移，SSB、观测C/AC及计数误差不变。中子归一化分母同样锚定零位移，平移后不拉回固定总数。','',
        '| 中子模式 | 明确约定 |','|---|---|',
        '| raw（默认） | 原始官方PE×Trec表，零位移约27.423763/6.908565事件 |',
        '| prior_posteff | 零位移分析窗、时间效率后18.4/5.6事件 |',
        '| bestfit_posteff | 零位移效率后17.3/5.5事件；仅总数控制，不是完整论文最佳拟合模板 |',
        '| prior_preeff | 零位移时间效率前18.4/5.6事件 |','',
        '后三者是独立归一化解释；现有证据尚不能唯一确定论文实现。+75ns为诊断候选，不能据此断定ROOT读错、遗漏飞行时间或已确定作者onset。主线原生SM/RESPONSE保持；KN是独立对照，均未拟合或逐味缩放。','',
        '原生SM参考窗353.465609、全支撑329.016423，相差24.449186事件；KN参考窗333.113488，+75ns约331.266392。341是不同模型/口径的论文SM参考，不作为调参目标。原生二维ROOT联合源的完整等价未验证。','',
        '论文对照采用经主论文内嵌几何核验的原作者矢量图，图中CEνNS积分约312.59，与正文306±20的差别保留；每味分量是论文模型曲线，并非独立逐味测量。截图proxy的νe≈89.23及强制总数不能用于科学定标。','',
        '直接材料：'+link('用户README',USER/'README.md')+' · '+link('交接说明',USER/'HANDOFF_PROMPT.md')+'。','',
        '实际入口：'+link('时间/中子适配器',ROOT/'examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py')+' · '+link('历史入口（已撤下）',ROOT.parent/'重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py')+' · '+link('历史诊断代码（已撤下）',ROOT.parent/'重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py')+' · '+link('本次结果',ROOT/'outputs/csi2021_timing_diagnostics_20261117/README.md')+'。','']
    return '\n'.join(lines)


if __name__=='__main__':apply()
