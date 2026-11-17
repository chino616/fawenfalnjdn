"""Publish same-source SM reports, canonical phase handoffs and current navigation."""
from pathlib import Path
from dataclasses import asdict
import hashlib,json,os,re,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/solar_b8_sm/20261107_run1'
FAMILIES=[('XENONnT','XENONnT_2024_SolarB8'),('PandaX4T','PandaX4T_2024_US2')]
CREATED=[];MODIFIED=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def link(origin,p,label,anchor=''):return f'[{label}](<{os.path.relpath(p,origin.parent).replace(chr(92),"/")}{anchor}>)'
def write(p,text):
    (MODIFIED if p.exists() else CREATED).append(rel(p));p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.rstrip()+'\n',encoding='utf8',newline='\n')
def dump(p,obj):write(p,json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False))
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+'|'.join('---' for _ in headers)+'|\n'+''.join('| '+' | '.join(str(x).replace('|',r'\|') for x in row)+' |\n' for row in rows)
def managed(p,text):
    start='<!-- solar-b8-sm-20261107:start -->';end='<!-- solar-b8-sm-20261107:end -->'
    old=p.read_text(encoding='utf8') if p.exists() else '# '+p.parent.name+'\n'
    block=start+'\n\n'+text.rstrip()+'\n\n'+end
    if start in old:
        assert old.count(start)==old.count(end)==1
        new=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda _:block,old,flags=re.S)
    else:new=old.rstrip()+'\n\n'+block
    write(p,new)


def bibliography(register,origin,ids):
    sources={s['source_id']:s for s in register['sources']}
    result='\n### 本章参考文献\n\n'
    for sid in ids:
        row=sources[sid];result+='- ['+sid+'] '+row['citation']
        path=Path(row.get('uri_or_path',''))
        if path.is_file():result+=' '+link(origin,path,'本次数值的直接原件/本地采用源')
        result+='\n'
    return result


def phase_report(run,phase,capability,description,handoff,artifact_paths,input_paths,status='PASS'):
    path=run/'phases'/f'{phase}_{capability}.md'
    record={'schema_version':1,'phase':phase,'capability_id':'solar_b8.'+capability,'workspace':'canonical',
            'plan_status':'READY' if status=='PASS' else 'BLOCKED','machine_gate':status,'human_gate':'NOT_REVIEWED',
            'scope_ref':rel(run/'00_PHASE0_PLAN.md'),'input_refs':[rel(p) for p in input_paths],
            'input_fingerprint':hashlib.sha256(''.join(sha(p) for p in input_paths).encode()).hexdigest(),
            'evidence_refs':[rel(run/'P01_EVIDENCE_LEDGER.yaml')],'decision_refs':['D0001'],'approval_refs':[],
            'artifacts':[{'path':rel(p),'sha256':sha(p),'role':'actual result or package'} for p in artifact_paths],
            'checks':[{'name':'actual artifact and scoped computation','status':status,'command':'python -B tools/run_solar_b8_sm_benchmark.py',
                       'result_ref':rel(artifact_paths[0])}] if artifact_paths else [],'handoff':handoff}
    write(path,f'# {phase}: {capability}\n\n2026-11-07。{description}\n\n物理实施范围见D0001/W0001。机器检查和实际输入/代码指纹见结构化记录；结果尚未由用户验收，不将其记为APPROVED。\n\n```json phase-result\n'+json.dumps(record,ensure_ascii=False,indent=2)+'\n```')
    return path,record


def publish(family,dataset):
    xenon=family=='XENONnT';data=ROOT/'data/experiments'/family/dataset
    run=ROOT/'workflows/cevns-pyeft/runs'/family/dataset;docs=ROOT/'docs/experiments'/family/'datasets'/dataset
    result=json.loads((OUT/dataset/'SM_RESULT.json').read_text(encoding='utf8'))
    comparison=json.loads((OUT/dataset/'REFERENCE_COMPARISON.json').read_text(encoding='utf8'))
    package=json.loads((data/'experiment.input.yaml').read_text(encoding='utf8'))
    register=json.loads((run/'P00_SOURCE_REGISTER.yaml').read_text(encoding='utf8'))
    sources={s['source_id']:s for s in register['sources']}
    evidence=json.loads((run/'P01_EVIDENCE_LEDGER.yaml').read_text(encoding='utf8'))
    evidence['claims']=[row for row in evidence['claims'] if not row['claim_id'].startswith('SM20261107-')]
    for i,(key,p) in enumerate(package['parameters'].items(),1):
        source=p['source_refs'][0]
        evidence['claims'].append({'claim_id':'SM20261107-P'+str(i).zfill(2),'field':key,'value':p['value'],'unit':p['unit'],
            'status':p['status'],'source_id':source if source in sources else None,'locator':p['meaning'],
            'verification_scope':'本地采用源/打印值/项目约定分别标注；Runtime从新正式包读取','input_claims':[],'decision_refs':['D0001'],
            'output_locations':[f'docs/experiments/{family}/datasets/{dataset}/experiment.physics.v2.2.md']})
    # Package arrays retain the primary extraction chain as well as their new binding.
    # A marginal probability is derived from the released basis, not a new raw release.
    inherited={row['claim_id'] for row in evidence['claims']}
    array_parents={
        'source_energy_MeV':[family+('-C018' if xenon else '-C006')],
        'source_shape_per_MeV':[family+('-C018' if xenon else '-C006')],
        **{key:[family+('-C019' if xenon else '-C007')] for key in
           ['target_mass_number','target_atomic_mass_u','target_number_fraction']},
        'run_exposures_tyr':[family+'-S05',family+'-S06'] if xenon else [family+'-S07'],
        **{key:['XENONnT-C040','XENONnT-C043'] for key in
           ['response_energy_keV','response_Ly','response_Qy']},
        'response_SR0':['XENONnT-C040'],'response_SR1':['XENONnT-C043'],
        'cs2_edges_SR0':['XENONnT-C040'],'cs2_edges_SR1':['XENONnT-C043'],
        'yield_energy_keV':['XENONnT-C034','XENONnT-C037'],
        'yield_Ly_median':['XENONnT-C034'],'yield_Qy_median':['XENONnT-C037'],
        'efficiency_energy_keV':['PandaX4T-C029'],'efficiency':['PandaX4T-C029'],
        'observable_edges':[]}
    array_claims=[]
    with np.load(data/'experiment.resources.npz',allow_pickle=False) as numerical:
        for i,(key,meta) in enumerate(package['resources']['arrays'].items(),1):
            parents=array_parents[key];assert set(parents)<=inherited
            values=np.asarray(numerical[meta['key']]);flat=values.reshape(-1)
            claim='SM20261107-A'+str(i).zfill(2);array_claims.append(claim)
            derived=key.startswith('response_SR') or key=='observable_edges'
            evidence['claims'].append({'claim_id':claim,'field':'resources/arrays/'+key,
                'value':{'file':rel(data/'experiment.resources.npz'),'key':meta['key'],'shape':list(values.shape),
                    'minimum':float(values.min()),'maximum':float(values.max()),
                    'representative_first_middle_last':[float(flat[j]) for j in [0,len(flat)//2,len(flat)-1]],
                    'sha256_raw_c_order':hashlib.sha256(values.tobytes(order='C')).hexdigest()},
                'unit':meta['unit'],'status':'PROJECT_DERIVED' if derived else 'SOURCE_EXTRACTED',
                'source_id':next((ref for ref in meta['source_refs'] if ref in sources),None),
                'locator':meta['meaning'],'input_claims':parents,'decision_refs':['D0001'],
                'verification_scope':'正式包绑定与数组哈希已核对；原始文件及精确定位沿input_claims追溯。'
                    +('原HDF5对其余三观测轴求和，保留原选择通过概率；未重新归一化。' if key.startswith('response_SR') else '')
                    +('本轮项目输出坐标选择，不声称为论文原始分箱。' if key=='observable_edges' else ''),
                'output_locations':[rel(data/'experiment.physics.md'),rel(docs/'experiment.physics.v2.2.md')]})
    evidence['claims'].append({'claim_id':'SM20261107-MODEL','field':'theory_response/sm_runtime_profile',
        'value':{'interaction':'coherent_sm_kn_v1','nuclear_response':'klein_nystrand_v1',
            'implementation':rel(ROOT/'cevns_pyeft/theory/sm_coherent.py'),
            'implementation_sha256':sha(ROOT/'cevns_pyeft/theory/sm_coherent.py')},
        'unit':'1','status':'PROJECT_DERIVED','source_id':'R01','locator':'2411.11749v1 PDF p3 式(1)–(3)，含−T/E的树级SM与Klein–Nystrand；参数从正式包读取。',
        'input_claims':[family+'-S03'],'decision_refs':['D0001'],
        'verification_scope':'解析共享模块实现与参数卡绑定；零反冲弱荷/单位/端点合同验证。不是实验完整likelihood认证。'})
    evidence['claims'].append({'claim_id':'SM20261107-RESULT','field':'prediction/sm_forward','value':{'file':rel(OUT/dataset/'SM_RESULT.json'),
         'counts':result['counts'],'total_events':result['total_events'],'package_sha256':result['input_package_sha256'],
         'resource_sha256':result['resource_archive_sha256'],'physics_fingerprint':result['physics_fingerprint']},'unit':'events/bin',
         'status':'PROJECT_DERIVED','source_id':None,'locator':'正式两文件→load_experiment_package→predict_experiment→共享recoil积分/概率折叠',
         'verification_scope':'固定SM点的数值收敛及逐箱对照；非拟合、非官方likelihood认证','decision_refs':['D0001'],
         'input_claims':['SM20261107-MODEL']+['SM20261107-P'+str(i).zfill(2) for i in range(1,len(package['parameters'])+1)]+array_claims})
    dump(run/'P01_EVIDENCE_LEDGER.yaml',evidence)
    contract=json.loads((run/'P03_PHYSICS_CONTRACT.yaml').read_text(encoding='utf8'))
    for group,field,val,unit,claim in [
        ('theory_response','sm_runtime_profile','coherent_sm_kn_v1 / klein_nystrand_v1','1','SM20261107-MODEL'),
        ('slow_counts','sm_runtime_result',result['counts'],'events/bin','SM20261107-RESULT')]:
        contract['sections'][group]['fields'][field]={'value':val,'unit':unit,'evidence_claims':[claim],
            'provenance_status':'PROJECT_DERIVED','decision_status':'DRAFT','blocking_scope':[]}
    dump(run/'P03_PHYSICS_CONTRACT.yaml',contract)
    inputs=[data/'experiment.input.yaml',data/'experiment.resources.npz']
    artifacts=[OUT/dataset/'SM_RESULT.json',OUT/dataset/'REFERENCE_COMPARISON.json',data/'experiment.input.yaml',data/'experiment.resources.npz']
    phase_records={}
    handoffs={
      'P04':{'theory_scope':'纯树级SM，味普适；文献[1]式(1)-(3)', 'coefficient_convention':'QV=((1-4sin²θW)Z-N)/2; no BSM coefficients',
          'nuclear_responses':'analytic Klein-Nystrand; all nine natural Xe isotopes; no Fig.4 EFT table dependency','coverage':'scalar/vector coherent SM only',
          'runtime_binding':'coherent_sm_kn_v1 and klein_nystrand_v1','external_evidence_limits':['original experiment yield/response differences remain distinct']},
      'P05':{'process_and_mass':'elastic neutrino nucleus; NIST atomic mass minus Z electron masses for kinematics, atomic mass for inventory',
          'kinematics':'existing ElasticKinematics exact endpoints','cross_section_api':'StandardModelKN.dsigma_dT returns DifferentialCrossSection',
          'units_and_axes':'MeV neutrino, keVnr recoil, cm²/keV cross section','support_and_limits':'paper recoil-order SM including -T/E; electron binding energy neglected',
          'benchmark':'zero-recoil weak-charge normalization and endpoint; new contract tests plus convergence'},
      'P06':{'representation':'bin_probability' if xenon else 'deterministic',
          'unit':'1','normalization':'sum_at_most_one','included_selections':['official joint template selection'] if xenon else ['published marginal true-energy acceptance'],
          'axes':'run-specific cS2 bin ordinals, with native PE edges separately retained' if xenon else 'keVnr, not Ne',
          'response_definition':'linear interpolation in (E,Ly,Qy) after exact marginalization' if xenon else 'published efficiency times true recoil density',
          'selection_ownership':'response/acceptance once, no extra efficiency or c_i',
          'validity_domain':'0.51-5keV public recasting support; no extrapolation' if xenon else 'Fig.1 visible recoil domain; Ne prediction remains blocked'},
      'P07':{'normalization_ledger':result['normalization_ledger'],'output_contract':{'observable':package['observable'],'per_run':result['per_run']},
          'numerics_and_convergence':result['convergence'],'reference_comparison':comparison,
          'freeze_scope':{'kind':'versioned numerical candidate reference','physics_fingerprint':result['physics_fingerprint'],
              'arrays':rel(OUT/dataset/'sm_prediction.npz'),'sha256':sha(OUT/dataset/'sm_prediction.npz'),'parameter_point':result['parameter_point'],
              'human_freeze':'NOT_REVIEWED','Fast_authorized':False}}}
    for phase,capability in [('P04','sm_theory'),('P05','sm_cross_section'),('P06','accepted_response' if xenon else 'true_recoil_projection'),('P07','sm_forward')]:
        p,record=phase_report(run,phase,capability,'本轮固定SM前向输出的实际实施与校验，具体数值见结果文件。',handoffs[phase],artifacts,inputs)
        phase_records[phase]={'path':p,'record':record}
    if not xenon:
        handoff=dict(handoffs['P06'],response_definition='MISSING P(Ne-bin|T) for US2; no Poisson/Gaussian substitute chosen',validity_domain='cannot compute requested reconstructed Ne spectrum')
        p,r=phase_report(run,'P06','electron_response','US2逐箱响应缺失，电子数谱未计算；不得把真实反冲投影改名为电子数预测。',handoff,artifacts,inputs,status='BLOCKED')
        phase_records['P06_electron']={'path':p,'record':r}
    for phase,name,text in [('P01','dataset','dataset身份与本轮标准模型前向目标沿用用户已指定对象。正式YAML/NPZ已由Compiler生成，可走标准load/predict接口。'),
                           ('P02','target_exposure','采用NIST九种天然Xe数丰度与原子质量。核数每1t归一化，再乘显式质量时间，不虚构实测质量与活时间。'),
                           ('P03','source','采用Bahcall官网829行中心谱，积分0.999986544；总通量5.46e6 cm^-2s^-1独立施加，味普适SM不需要MSW概率表。')]:
        p=run/'phases'/f'{phase}_{name}.md';write(p,f'# {phase}: {name}\n\n2026-11-07。{text}\n\n实际输入、数值、原文定位和单位见[正式输入包](<{os.path.relpath(data/"experiment.physics.md",p.parent).replace(chr(92),"/")}> )。Machine为本轮明确范围的PASS，Human结果接受仍为NOT_REVIEWED。\n')
        phase_records[phase]={'path':p,'record':{'machine_gate':'PASS','human_gate':'NOT_REVIEWED','capability_id':name}}
    # Human-readable report from the actual saved result, never transcribed numbers.
    report=run/'SM_BENCHMARK_REPORT.md'
    title='XENONnT 2024' if xenon else 'PandaX-4T 2024 US2'
    text=f'# {title}：SM事件谱 benchmark\n\n**2026-11-07，主项目正式入口已接通；科学结果DRAFT/PARTIAL。**\n\n'
    text+=' · '.join([link(report,data/'experiment.physics.md','Compiler详细输入与来源'),link(report,OUT/dataset/'SM_RESULT.json','逐箱结果与收敛'),link(report,OUT/dataset/'events.png','事件数图'),link(report,OUT/dataset/'events.pdf','图PDF'),link(report,run/'00_PHASE0_PLAN.md','执行计划')])+'\n\n'
    text+='<a id="toc"></a>\n\n## 目录\n\n- [模型与来源](#model)\n- [实际数值](#numbers)\n- [验证与限制](#validation)\n- [复算入口](#reproduce)\n\n<a id="model"></a>\n\n## 模型与来源\n\n'
    text+=table(['输入/选择','本轮实际采用','直接出处与核验范围'],[
        ['SM截面/核形状','树级SM含−T/E；Klein–Nystrand，R=1.23 A^(1/3)fm、a=0.7fm','[R01] PDF p3式(1)–(3)，解析共享模块；不借用Fig.4的EFT系数'],
        ['弱混合角','sin²θW=0.23857','[R01] PDF p3式(2)后'],
        ['源谱/总通量','Bahcall中心829点；Φ=5.46×10⁶ cm⁻²s⁻¹','[R04] 官网原表前两列；[R01] PDF p5式(11)后；不重复效率'],
        ['靶','天然Xe九核素，NIST数丰度','[R09] 原子质量给核数；动力学近似扣除54电子质量，忽略电子结合能'],
        ['Response/投影','早期官方YBe基底，按(E,Ly,Qy)线性插值、其余观测轴求和' if xenon else '原图99节点接受度×真实反冲率；Ne响应仍缺',
         '[R17] orthonormal_basis/、signal/*median.json、utils.py::Template.interpolator' if xenon else '[R02] PDF p3 Fig.1黑色Total(US2)'],
        ['曝光','SR0=1.174398、SR1=2.342593 t·yr' if xenon else 'US2合计1.04 t·yr',
         '[R17] statistical_model_base.yaml livetime_sr0/1；合计3.516991，与论文打印3.51分别报告' if xenon else '[R02] PDF p3'],
        ['常量/单位','正式参数卡固定项目G_F、amu、m_e、hbarc与截面换算','[R18] 本地采用的foundation/constants.py；31557600s/yr只出现一次'],
        ['绘图观测误差','68.268949% Garwood Poisson区间，图示用','本轮项目推导：χ²分布分位点，不冒充论文原始误差或完整统计模型']])
    text+='\n### Source、Target与折叠定义\n\n源的总量和能量形状分别施加：\n\n$$\n'+r'\frac{d\phi}{dE_\nu}=\Phi_{8B} f_{8B}(E_\nu).'+'\n$$\n\nPhi的单位cm⁻²s⁻¹，f的单位MeV⁻¹，Eν用MeV。直接依据[R01] PDF p5式(11)及后文与[R04]官网谱表；不是把已含接受度的反冲谱当作中微子通量。\n\n核数由天然数丰度构建：\n\n$$\n'+r'\overline m_{\rm atom}=\sum_A f_A m_{{\rm atom},A},\qquad n_A=\frac{M_{\rm anchor}f_A}{\overline m_{\rm atom}}.'+'\n$$\n\n这里f_A是[R09]的数丰度，m_atom由NIST的u数值乘10⁻³kg/mol再除以[R13]的N_A，采用常用摩尔质量常量1g/mol近似；M_anchor=1000kg是项目归一化锚点。核数单位nuclei，n_A^(t)表示每吨核数。kg原子质量用于物质数，扣除电子后的GeV质量用于运动学，两者分别登记。\n'
    if xenon:
        text+='\n响应为原接受后四维概率的边际化：\n\n$$\n'+r'P_{ri}(T)=\sum_{j,k,l}p_r(i,j,k,l\mid T,L_y(T),Q_y(T)),\qquad 0\leq\sum_iP_{ri}(T)\leq1.'+'\n$$\n\np_r是[R17]每个单能HDF5的接受后箱概率；(E,Ly,Qy)取值按官方utils.py的三线性内插，Ly/Qy取原median表。它已经包含选取，不是需要再乘总效率的归一化条件密度。每run/每同位素的信号为本项目对[R01]式(11)–(12)采用完整Response后的推导：\n\n$$\n'+r'\mu_{ri}^{\rm SM}=\mathcal E_r t_{\rm yr}\sum_A n_A^{(t)}\int dT\,dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}P_{ri}(T).'+'\n$$\n'
    else:
        text+='\n本轮只计算真实能量箱上的接受度加权诊断：\n\n$$\n'+r'N_j^{\rm recoil}=\mathcal E\,t_{\rm yr}\sum_A n_A^{(t)}\int_{T_j}^{T_{j+1}}dT\int dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}\epsilon_{\rm US2}(T).'+'\n$$\n\nepsilon来自[R02] Fig.1黑线。真实能量T的单位keVnr；缺失的是Ne箱的P_i(T)，本式不能作为Ne预测。\n'
    text+='\nE_r/曝光单位t·yr，t_yr=31557600s/yr，n_A^(t)单位nuclei/t，截面输出cm²/keVnr，积分后的mu/N为events/bin。代码先算参考年注量与参考吨核数，再乘exposure/anchor_tonne，与上式等价；曝光、核数及接受率各一次。上述实验侧折叠关系为项目推导，代码owner为solar_b8.SolarExecutor与共享recoil/folding，不含c_i；共享SM/KN内部截面公式只登记模块和[R01]定位。\n'
    text+=bibliography(register,report,['R01','R04','R09','R13','R17' if xenon else 'R02','R18'])
    text+='\n[返回目录](#toc)\n\n<a id="numbers"></a>\n\n## 实际数值\n\n'
    if xenon:
        counts=np.array(result['counts']);native=np.array(comparison['native_release_signal_reference']).sum(axis=0)
        background=sum(np.array(values) for values in comparison['backgrounds'].values()).sum(axis=0);observed=np.array(comparison['observed']).sum(axis=0)
        text+=table(['箱序号','本轮SM信号','原发布名义信号','背景','SM+背景','观测D'],[[i+1,f'{counts[i]:.9f}',f'{native[i]:.9f}',f'{background[i]:.9f}',f'{counts[i]+background[i]:.9f}',int(observed[i])] for i in range(3)])
        text+=f'\n合计SM信号 **{counts.sum():.9f}**，背景 **{background.sum():.9f}**，总期望 **{(counts+background).sum():.9f}**，D=37。单位events/bin。\n\n'
        text+='三箱是各run自身的cS2箱按序号求和；SR0边界[90,170.161773681641,249.889739990234,500]PE，SR1边界[90,155.937850952148,232.292022705078,500]PE。不是一套共同PE边界的重新直方图。\n\n'
        text+=table(['run','箱1','箱2','箱3','合计'],[[run,*[f'{v:.9f}' for v in values],f'{sum(values):.9f}'] for run,values in result['per_run'].items()])
        text+='\n背景与原始信号对照来自[R17]原HDF5名义模板，按相应曝光相乘；D来自官方事件表的直接箱计数，与[R03] PDF p6 Fig.2核对。原发布B8模板仅作信号对照，没有再作为背景加入。\n'
        text+='\n本轮SM与原发布名义信号的三箱相对差异为 '+', '.join(f'{v:+.5f}%' for v in (counts/native-1)*100)+'；逐run最大绝对差异约 '+f'{np.max(abs(np.array(comparison["fractional_difference_per_run_bin"])))*100:.5f}%'+ '。它与此前“同一官方CDF谱重铸验证”的最高6.30%不是同一比较，不能混用。\n'
        text+='\n论文打印总曝光3.51t·yr，本轮响应配套发布采用3.516991t·yr，相差约0.199%。若只把曝光改成3.51，按线性缩放得到总SM '+f'{counts.sum()*3.51/3.516991:.9f}'+ '；默认结果未作这个缩放，也没有通过c_i强行对齐参考。\n'
        text+=bibliography(register,report,['R03','R17'])
    else:
        text+=f'真实反冲可见区间的接受度加权SM投影合计 **{result["total_events"]:.9f}** events；27箱完整数组见结果文件。该数不是Ne∈[4,8]的预测，不能与论文拟合信号{comparison["paper_reference_signal_events"]:.6f}直接取复现比。\n\n'
        text+='图左为本轮计算的真实能量谱；图右为文献[R01] Fig.1数字化的观测、背景及拟合/参考信号，明确标为reference only。US2逐箱响应缺失，所以没有本轮计算的Ne信号直方图。\n'
        text+=bibliography(register,report,['R01','R02'])
    text+='\n[返回目录](#toc)\n\n<a id="validation"></a>\n\n## 验证与限制\n\n'
    text+=table(['加密维度','最大逐箱相对差异','最大绝对差异(events)','预定数值条件'],[[row['axis'],f'{max(row["relative_difference"])*100:.6g}%',f'{max(row["absolute_difference"]):.6g}','PASS：max(2e-4 events, 0.2%)'] for row in result['convergence']['checks']])
    text+='\n运行网格（基础T节点/Eν节点）与总数：\n\n'+table(['步骤','T基础节点','Eν基础节点','总事件数'],[[r['label'],r['n_er'],r['n_enu'],f'{r["total_events"]:.12g}'] for r in result['convergence']['runs']])
    text+='\nEν另并入829点源表断点，T另并入响应、产额和输出箱断点。保存各run/九核素分量，检查非负、组分和、通量线性、弹性端点和截面单位。SM点数值收敛不等于论文曲线/官方likelihood复现；本轮没有拟合、置信区间或BSM扫描。\n\n'
    tests=json.loads((OUT/'TEST_RESULTS.json').read_text(encoding='utf8'))
    text+=f'本轮测试实际为{tests["passed"]}项通过、{tests["failed"]}项失败；新增solar合同7项通过，所选旧实验数值Slow/Fast/分量回归通过。4项失败为两个旧Physics MD同步检查与两个旧资源清单哈希检查。旧输入、数组、MD和资源清单与此前快照逐字节一致；移除新增solar绑定仍能复现旧MD差异，因此不改旧参考或容差来掩盖。'+link(report,OUT/'TEST_RESULTS.json','实际测试记录')+' · '+link(report,OUT/'LEGACY_MD_BASELINE_CHECK.json','旧MD独立对照')+' · '+link(report,OUT/'LEGACY_INPUT_PRESERVATION.json','旧文件指纹')+'。\n\n'
    text+='XENONnT只在公开重铸支持域0.51–5keV使用响应，不外推。8B表最高能量对应的Xe反冲上限低于5keV；低于0.51keV的响应不由本模型认证，0.5–0.51keV的技术截断与原分析差异仍保留。\n' if xenon else 'PandaX缺少固定真实反冲到Ne箱的通过概率；没有用Qy均值、任意Poisson/Gaussian宽度或c_i代替它。仅该重建谱能力受阻。\n'
    text+='\n[返回目录](#toc)\n\n<a id="reproduce"></a>\n\n## 复算入口\n\n从原Gitup01根目录运行：\n\n```powershell\npython -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run\n```\n\n直接标准Runtime入口：\n\n```python\nfrom cevns_pyeft.experiments.package_loader import load_experiment_package\nfrom cevns_pyeft.experiments.runtime import predict_experiment\nexperiment = load_experiment_package("'+rel(data)+'")\nprediction = predict_experiment(experiment, numerics={"n_er": 801, "n_enu": 480})\nprint(prediction.counts)\n```\n\n主项目代码、正式包、阶段记录和结果均已落盘。通过显式输入包加载时使用项目现有scoped Catalog；没有把PARTIAL结果无条件加入默认活动实验清单。旧onboarding保持原位。\n\n[返回目录](#toc)\n'
    write(report,text)
    # New version wrapper owns the calculation handoff; old v2/v2.1 remain untouched.
    onboarding=docs/'experiment.physics.v2.2.md'
    intro=f'# {title} — onboarding v2.2（新版本，SM主线计算草稿）\n\n**2026-11-07，DRAFT/PARTIAL。** 本版补充正式输入包、Runtime执行、逐箱结果、收敛及外部参考差异；旧版原位保留。\n\n'
    intro+=' · '.join([link(onboarding,docs/'experiment.physics.v2.1.md','旧v2.1详细版'),link(onboarding,data/'experiment.physics.md','同源正式包完整数值和来源'),link(onboarding,run/'P00_SOURCE_REGISTER.yaml','P00来源'),link(onboarding,run/'P01_EVIDENCE_LEDGER.yaml','P01证据'),link(onboarding,run/'P03_PHYSICS_CONTRACT.yaml','P03配置'),link(onboarding,report,'本轮SM报告'),link(onboarding,OUT/dataset/'events.png','事件数图')])+'\n\n'
    # Paths in the embedded report are regenerated for this document, not copied verbatim.
    embedded=text[text.index('<a id="toc"></a>'):]
    embedded=re.sub(r'\]\(<([^>]+)>\)',lambda m:'](<'+os.path.relpath((report.parent/m.group(1).split('#',1)[0]).resolve(),onboarding.parent).replace(chr(92),'/')+('' if '#' not in m.group(1) else '#'+m.group(1).split('#',1)[1])+'>)',embedded)
    write(onboarding,intro+embedded)
    summary=docs/'experiment.physics.summary.v2.2.md'
    write(summary,f'# {title} — SM onboarding v2.2精简草稿\n\n2026-11-07。'+link(summary,onboarding,'详细新版与逐项来源')+' · '+link(summary,report,'实际计算/收敛报告')+'\n\n'+
        ('SM三箱：'+', '.join(f'{v:.6f}' for v in result['counts'])+f'，合计{result["total_events"]:.6f}events。使用早期官方Response，保留原分析等价性限制。' if xenon else '真实反冲投影已计算；US2电子数响应仍缺，本轮没有计算Ne信号谱。')+
        '\n\n正式两文件可走load_experiment_package/predict_experiment；Fast/拟合未请求。旧版保留，科学结果尚未由用户验收。')
    user=docs/'EXPERIMENT_USER_INPUT.v2.2.md'
    write(user,f'# {title} — 用户资料v2.2（新版本）\n\n2026-11-07。用户请求：并入主线，以SM作事件数谱benchmark，按现有流程计算。\n\n'+link(user,onboarding,'本版物理模型/数值/具体出处')+' · '+link(user,report,'本轮真实结果')+'\n\n已沿用Response、不引入c_i、旧版保留、逐数据引用的决定；未索取已提供的数据。'+
        ('XENONnT名义响应已运行，外部参考差异逐箱保留。' if xenon else 'PandaX Ne逐箱核缺失，当前只完成真实反冲诊断，缺口不伪造。')+'结果接受保持NOT_REVIEWED。')
    phase10={'delivery_scope':{'mode':'dataset_onboarding','target':'canonical SM forward benchmark, response limitations explicit','completion':'partial'},'capability_matrix':[
        {'id':'sm_forward' if xenon else 'true_recoil_projection','requested':True,'required_for_claim':True,'machine_gate':'PASS','human_gate':'NOT_REVIEWED','result_ref':rel(OUT/dataset/'SM_RESULT.json')},
        {'id':'electron_spectrum','requested':True,'required_for_claim':True,'machine_gate':'PASS' if xenon else 'BLOCKED','human_gate':'NOT_REVIEWED','result_ref':rel(report)}],
        'validation_levels':{'numerical_convergence':'PASS','package_Runtime':'PASS','new_contract_tests':'see QA report','existing_regressions':'see QA report',
                             'strict_paper_reproduction':'NOT_CERTIFIED','official_likelihood':'NOT_REQUESTED'},
        'runtime_integration':'standard package loader/scoped Catalog/predict_experiment; no unconditional global activation',
        'final_claim':'SM forward reference with explicit public model limits' if xenon else 'partial: true recoil only, Ne signal not calculated',
        'limitations':result['limits']+['human result acceptance NOT_REVIEWED']}
    p,r=phase_report(run,'P10','sm_delivery','按明确交付能力记录机器检查；没有把PARTIAL改成FULLY_INTEGRATED。',phase10,artifacts,inputs,status='PASS' if xenon else 'BLOCKED')
    phase_records['P10']={'path':p,'record':r}
    dump(run/'00_IMPLEMENTATION_MANIFEST.yaml',{'revision':1,'date':'2026-11-07','phase0':rel(run/'00_PHASE0_PLAN.md'),
        'runtime':'load_experiment_package -> predict_experiment -> SolarExecutor -> integrate_recoil_yield/probability_fold',
        'input_authority':list(map(rel,inputs)),'actual_implementation':json.loads((OUT/dataset/'PREPARED_MODEL.json').read_text(encoding='utf8'))['implementation'],
        'capabilities':phase10['capability_matrix'],'optional':['P08 Fast NOT_REQUESTED','P09 inference NOT_REQUESTED']})
    gates={phase:{'machine':entry['record']['machine_gate'],'human':'NOT_REVIEWED','report_ref':rel(entry['path']),
                  'capability':entry['record']['capability_id'],'decision_refs':['D0001']} for phase,entry in phase_records.items()}
    progress={'schema_version':1,'revision':1,'previous_revision':None,'updated_at':'2026-11-07','workflow_status':'ACTIVE',
        'task_scope':'existing_dataset','workspace_kind':'canonical','execution_mode':'stepwise','experiment_name':title,
        'experiment_slug':family,'dataset_id':dataset,'checkpoint':{'phase_id':'P10','phase_name':'SM benchmark delivery','skill':'cevns-experiment',
          'step_id':'sm_forward.result_review','next_action':'review numerical benchmark and retained precision limits' if xenon else 'obtain US2 P(Ne-bin|T) to complete electron spectrum','resume_requires':[]},
        'gates':gates,'active_blockers':[] if xenon else ['missing US2 reconstructed electron response'],
        'authorization_refs':{'scope':'D0001','write':'W0001'},'artifact_refs':{'source_register':rel(run/'P00_SOURCE_REGISTER.yaml'),
          'evidence_ledger':rel(run/'P01_EVIDENCE_LEDGER.yaml'),'physics_contract':rel(run/'P03_PHYSICS_CONTRACT.yaml'),
          'decision_log':rel(run/'P04_DECISION_LOG.yaml'),'authorization_log':rel(run/'AUTHORIZATION_LOG.yaml'),
          'implementation_manifest':rel(run/'00_IMPLEMENTATION_MANIFEST.yaml'),'phase_reports':{k:rel(v['path']) for k,v in phase_records.items()}},
        'requested_unfinished_capabilities':[] if xenon else ['reconstructed_Ne_SM_signal'],'human_result_acceptance':'NOT_REVIEWED'}
    index=run/'00_MIGRATION_PROGRESS.md'
    if index.exists():
        old=json.loads(re.search(r'```json\n(.*?)\n```',index.read_text(encoding='utf8'),re.S).group(1));progress.update(revision=old['revision']+1,previous_revision=old['revision'])
    write(index,'# 主线进度：'+dataset+'\n\n本索引不授予科学批准。正式输入包和实际计算已落盘，结果尚待人类审阅。\n\n```json\n'+json.dumps(progress,ensure_ascii=False,indent=2)+'\n```')
    managed(run/'README.md','## 当前SM主线结果\n\n'+' · '.join([link(run/'README.md',index,'当前进度'),link(run/'README.md',report,'SM计算报告'),link(run/'README.md',onboarding,'onboarding v2.2'),link(run/'README.md',data/'experiment.physics.md','正式输入包与来源')]))
    for path in [data/'README.md',docs/'README.md']:
        managed(path,'## 新版v2.2：已运行SM benchmark\n\n'+' · '.join([link(path,onboarding,'新onboarding'),link(path,report,'SM结果与精度'),link(path,index,'主线进度'),link(path,data/'experiment.input.yaml','正式机器输入')])+'\n\n'+('XENONnT三箱Response已接入标准Runtime。' if xenon else 'PandaX仅完成真实反冲投影；Ne逐箱Response仍缺。')+'旧版和原数值表保留。')
    return {'family':family,'dataset':dataset,'onboarding':onboarding,'report':report,'run':run,'phase_records':phase_records}


if __name__=='__main__':
    records=[publish(*item) for item in FAMILIES]
    central=ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_SM_BENCHMARK_20261107.md'
    write(central,'# 太阳8B：主线SM benchmark\n\n2026-11-07。正式输入包、标准Runtime计算和阶段记录均已进入原项目；科学声明仍为PARTIAL。\n\n'+
        table(['实验','最新onboarding','实际计算/图/来源'],[[row['dataset'],link(central,row['onboarding'],'v2.2'),link(central,row['report'],'SM报告')] for row in records])+\
        '\nXENONnT SM信号12.317233事件；PandaX电子数谱仍缺响应，当前真实反冲投影不替代该目标。\n\n复算：`python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run`。')
    for name in ['README.md','docs/experiments/README.md','data/README.md','data/experiments/README.md','workflows/cevns-pyeft/README.md']:
        p=ROOT/name;managed(p,'## 太阳8B SM主线benchmark（2026-11-07）\n\n'+link(p,central,'新版onboarding、真实事件数图与阶段记录')+'。采用正式YAML/NPZ和现有Runtime；明确保留PandaX电子数响应缺口。')
    parents=ROOT/'workflows/cevns-pyeft/runs/README.md'
    managed(parents,'## 太阳8B阶段记录\n\n'+''.join('- '+link(parents,row['run']/'README.md',row['dataset'])+'\n' for row in records))
    for name,text in {
      'cevns_pyeft/experiments/README.md':'新增[solar_b8.py](solar_b8.py)与只读文件合同[solar_input.py](solar_input.py)：显式solar_b8_sm_v1输入包走标准Runtime；XENONnT用官方基底，PandaX只提供真实反冲诊断。包经Compiler生成；不按实验名复制核心算法，不无条件激活PARTIAL包。',
      'cevns_pyeft/theory/README.md':'[sm_coherent.py](sm_coherent.py)提供2411.11749v1式(1)–(3)的纯SM/KN共享模块，参数来自正式包；原EFT与Helm实现不变。',
      'tools/README.md':'[prepare_solar_b8_mainline.py](prepare_solar_b8_mainline.py)保存备份与正式记录；[build_solar_b8_packages.py](build_solar_b8_packages.py)调用既有Compiler；[run_solar_b8_sm_benchmark.py](run_solar_b8_sm_benchmark.py)执行收敛和出图，--resume只复用相同物理指纹；[finalize_solar_b8_mainline.py](finalize_solar_b8_mainline.py)同源生成报告与阶段记录。',
      'tests/README.md':'[test_solar_b8_sm_contract.py](test_solar_b8_sm_contract.py)核对零反冲弱荷/单位、运动学端点、味普适性、天然组分、概率归一化、通量线性和PandaX缺失响应不能被提升。'
    }.items():managed(ROOT/name,'## Solar B8 SM profile\n\n'+text)
    managed(ROOT/'tools/README.md','## Solar B8 SM profile\n\n'+
        '[prepare_solar_b8_mainline.py](prepare_solar_b8_mainline.py)备份/接入；[build_solar_b8_packages.py](build_solar_b8_packages.py)调用既有Compiler（--check只读，--overwrite按原Writer备份）；[run_solar_b8_sm_benchmark.py](run_solar_b8_sm_benchmark.py)标准Runtime/收敛/出图；[finalize_solar_b8_mainline.py](finalize_solar_b8_mainline.py)同源报告；[validate_solar_b8_mainline.py](validate_solar_b8_mainline.py)检查正式包、阶段schema、双文件可移植运行和旧文件保留；[validate_solar_b8_rendering.mjs](validate_solar_b8_rendering.mjs)检查Markdown数学、目录跳转及窄屏渲染。')
    managed(OUT/'README.md','## 主项目交付与验证\n\n'+
        ' · '.join(link(OUT/'README.md',p,label) for p,label in [
            (central,'主线入口与新onboarding'),(OUT/'VALIDATION.json','实际验收记录'),
            (OUT/'TEST_RESULTS.json','95通过/4项既有失败'),(OUT/'READABILITY_VALIDATION.json','渲染与跳转'),
            (OUT/'MAINLINE_DOCUMENTS.json','本轮生成的文档'),(OUT/'CHANGE_MANIFEST.json','完整任务文件与README归属')])+
        '\n\nXENONnT已计算三箱重建事例数；PandaX仅完成真实反冲诊断，电子数响应仍缺。两个实验均不声称严格论文复现通过。')
    parent=OUT.parent/'README.md'
    managed(parent,'## 标准模型事例数谱\n\n'+link(parent,OUT/'README.md','2026-11-07：第一轮SM benchmark')+
        '。每次运行保留参数、输入/代码指纹、逐箱数组、图和能力限制；旧运行原位保留。')
    parent=ROOT/'outputs/README.md'
    managed(parent,'## 太阳8B标准模型计算（2026-11-07）\n\n'+link(parent,OUT.parent/'README.md','solar_b8_sm/')+
        '保存PandaX/XENONnT的标准Runtime结果、逐箱比较和数值验证；PandaX电子数谱仍缺响应。')
    dump(OUT/'MAINLINE_DOCUMENTS.json',{'created':CREATED,'modified':MODIFIED,'central_report':rel(central),'phase_reports':[rel(v['path']) for row in records for v in row['phase_records'].values()]})
    print('Published canonical phase records, two v2.2 onboarding sets, package navigation and actual SM reports.')
