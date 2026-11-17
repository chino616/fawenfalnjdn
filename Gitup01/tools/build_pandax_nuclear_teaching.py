"""Versioned PandaX P01-P10 examples: actual nuclear M table, standalone cores.

Only this builder reads the project. Each generated core carries its own arrays
and imports only NumPy/SciPy/stdlib. The old KN teaching directory is preserved.
"""
from pathlib import Path
import ast
import hashlib
import json
import os
import runpy
import sys
import textwrap
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'重构'
OLD=PARENT/'20261110_PandaX_P01_P10_物理与最小代码'
OUT=PARENT/'20261110_PandaX_Response_P01_P10_物理与最小代码'
DATA=ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'
MAIN=ROOT/'docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.1.md'
RESULT=ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/RESULT.json'
sys.path.insert(0,str(OLD/'_核对记录'))
T=runpy.run_path(str(OLD/'_核对记录/build_examples.py'),run_name='authoring_template')


def clean(text):return textwrap.dedent(text).strip()+'\n'
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.rstrip()+'\n',encoding='utf8',newline='\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def link(origin,path,label):return '['+label+'](<'+os.path.relpath(path,origin.parent).replace('\\','/')+'>)'


M_FUNCTION=clean('''
    # [O4/O9] Actual R16 M coefficients; pp,pn,nn, ascending powers of y.
    # No KN/Helm or additional spin normalization is applied.
    def coherent_M(A, mass, recoil_keV):
        b, pp, pn, nn = M_TABLE[int(A)]
        y = (np.sqrt(2*mass*np.asarray(recoil_keV)*1e-6)*b/2)**2
        values = [np.exp(-2*y)*np.polynomial.polynomial.polyval(y,c) for c in (pp,pn,nn)]
        return np.stack([values[0],values[1],values[1],values[2]],axis=-1).reshape(y.shape+(2,2))
''')
DSIGMA=clean('''
    # [O4] c1/M only, with the actual p/n nuclear table.
    def dsigma(A, mass, energy_MeV, recoil_keV, g=G_SM):
        e,t = np.asarray(energy_MeV)*1e-3,np.asarray(recoil_keV)*1e-6
        h = np.maximum(1-mass*t/(2*e*e)-t/e,0.)
        W = coherent_M(A,mass,recoil_keV)
        strength = np.einsum('p,...pq,q->...',g.conj(),W,g).real
        return GF**2*mass/(4*np.pi)*h*strength*GEV2_TO_CM2*1e-6
''')
FAST=clean('''
    # [O7/P08] Integrate the actual M matrix into a bin-dependent coupling kernel.
    def build_kernel(n_r=801,n_enu=480):
        t,e,edges = integration_grid(n_r,n_enu)
        kernel = np.zeros((8,2,2))
        for A,atom_u,fraction in TARGETS:
            if int(A) not in M_TABLE:continue  # missing tables, no renormalization
            W = coherent_M(A,A*AMU,t)
            weight = fixed_weight(A,atom_u,fraction,t,e)
            for p in range(2):
                for n in range(2):kernel[:,p,n] += bin_integrals(t,weight*W[:,p,n],edges)
        return kernel

    def fast_counts(kernel,g):
        return np.einsum('p,ipq,q->i',g.conj(),kernel,g).real
''')


def main():
    with np.load(DATA/'experiment.resources.npz',allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    raw=json.loads((ROOT/'data/responses/responses_all.json').read_text(encoding='utf8'))['nuclei']
    keys=[128,129,130,131,132,134,136]
    mtable='# [O4/O9] R16 responses_all.json, explicit seven-isotope M table.\nM_TABLE = {\n'
    for A in keys:
        item=raw['Xe'+str(A)];co=item['responses']['M']
        mtable+=f'    {A}: ({item["basic"]["b"]!r},\n'
        assert co[0][1]==co[1][0], 'M p/n symmetry required by this minimal example'
        mtable+='        '+repr(co[0][0])+',\n        '+repr(co[0][1])+',\n        '+repr(co[1][1])+'),\n'
    mtable+='}\n'
    target=np.column_stack([a['target_mass_number'],a['target_atomic_mass_u'],a['target_number_fraction']])
    full_source=np.column_stack([a['source_energy_MeV'],a['source_shape_per_MeV']])
    indices=np.unique(np.r_[np.arange(0,len(full_source),10),len(full_source)-1])
    data='\n'.join(T['literal'](name,arr,per_line=5) for name,arr in [('TARGETS',target),('SOURCE',full_source[indices]),
        ('QY',np.loadtxt(DATA/'detector/pandax_qy_nominal.txt')),('EFF',np.column_stack([a['efficiency_energy_keV'],a['efficiency']]))])
    constants=T['CONSTANTS'].replace('AMU, ME = 0.93149410372, 0.00051099895069  # GeV/u, GeV','AMU = 0.93149410372  # [O3/O4] A*amu kinematic mass; original atomic masses set nucleus counts')
    integration=T['INTEGRATION'].replace('mass = atom_u*AMU-Z*ME  # same bare-nucleus convention as the main project','mass = A*AMU  # [O3/O4] same mass in amplitude, phase space and kinematics')
    integration=integration.replace('*form_factor2(A,mass,t)*acceptance(t))  # charge is NOT included','*acceptance(t))  # [O5/O7] nuclear M not yet contracted; selection once')
    integration=integration.replace('density = fixed_weight(A,atom_u,fraction,t,e)*abs(Z*g[0]+(A-Z)*g[1])**2',
        'if int(A) not in M_TABLE:continue  # [O4] Xe124/126 missing, no KN substitute\n        W = coherent_M(A,A*AMU,t)\n        density = fixed_weight(A,atom_u,fraction,t,e)*np.einsum("p,tpq,q->t",g.conj(),W,g).real')
    full=T['IMPORTS']+'from scipy.optimize import brentq\n'+constants+data+mtable+M_FUNCTION+T['DETECTOR']+integration
    stages=json.loads((OLD/'_核对记录/stages.json').read_text(encoding='utf8'))
    generated={}
    def add(key,body,main_body):
        directory=stages[key]['directory']; code='"""'+key+' | Actual M nuclear Response, standalone.\n主文：../../../Gitup01/docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.1.md\n[O编号]为主onboarding章节；本例M-only，七核素，不重归一。\n"""\n'+body+'\n'+T['SAVE']+'\n'+clean(main_body)+'\nif __name__ == "__main__":\n    main()\n'
        # Add chapter comments beside the actual definitions and numerical arrays.
        notes={'fixed_weight':'O2/O3/O4/O5→O7','direct_counts':'O4→O7','coherent_M':'O4/O9','dsigma':'O4','build_kernel':'O7/P08',
               'fast_counts':'O7/P08','recoil_edges':'O5/O6','bin_integrals':'O6/O7','integration_grid':'O7'}
        for name,mark in notes.items():code=code.replace('def '+name+'(', '# ['+mark+'] 具体物理/来源见同章；下列函数实际执行该步。\ndef '+name+'(')
        p=OUT/directory/'core.py';write(p,code);generated[key]={'directory':directory,'lines':len(code.splitlines())}
    for key in ['ONBOARDING','P01','P02','P03','P06']:
        original=(OLD/stages[key]['directory']/'core.py').read_text(encoding='utf8')
        original=original.replace('v3.0','v3.1').replace('共享SM/KN','共享SM单位').replace('再减Z个电子；绑定能按原项目忽略','动力学改用A*AMU，核数仍用原子质量')
        original=original.replace('mass = atom_u*AMU-Z*ME','mass = A*AMU').replace('运动学用裸核质量GeV','运动学用A*amu质量GeV')
        original=original.replace("'model':'SM coherent M/KN','sin2thetaW':S2W,'radius_fm':1.23,'skin_fm':.7", "'model':'actual M nuclear table; seven isotopes, no renormalization','sin2thetaW':S2W")
        original=original.replace("'locator':'R01 p3 Eqs.(1)-(3); framework PDF pp6-8'", "'locator':'R16 actual local M coefficients; R20 amplitude; v3.1 chapter 4'")
        original=original.replace('# coherent M/KN','# actual M table')
        if key=='ONBOARDING':
            original=original.replace('def save_result(result):',mtable+M_FUNCTION+'\ndef save_result(result):')
            original=original.replace('assert FLUX>0 and EXPOSURE>0',
                'assert FLUX>0 and EXPOSURE>0\n    assert sorted(M_TABLE)==[128,129,130,131,132,134,136]\n    assert all(np.array(v[1:]).shape==(3,11) for v in M_TABLE.values())')
            original=original.replace("'model':'actual M nuclear table; seven isotopes, no renormalization','sin2thetaW':S2W",
                "'model':'actual M nuclear table; seven isotopes, no renormalization','sin2thetaW':S2W, 'M_keys':sorted(M_TABLE)")
        p=OUT/stages[key]['directory']/'core.py';write(p,original);generated[key]={'directory':stages[key]['directory'],'lines':len(original.splitlines())}
    kinetic=T['KINEMATICS'].split('def dsigma(')[0]
    nuclear=T['IMPORTS']+constants+mtable+M_FUNCTION
    add('P04',nuclear, '''
    def main():
        A,mass,E,T = 131,131*AMU,.010,1e-6
        W = coherent_M(A,mass,T*1e6)  # [O4] actual W, not an outer(Z,N) proxy
        c = GF/np.sqrt(2)*G_SM
        scalar = (4*E*E-2*mass*T-4*E*T)*(c@W@c)
        save_result({'model':'actual M only','W_pn':W.tolist(),'K_flavor_GeV_minus2':(scalar*np.eye(3)).tolist(),
                     'trace_rho_K_GeV_minus2':float(scalar),'external_table_authorship':'UNRESOLVED'})
    ''')
    add('P05',nuclear+kinetic+DSIGMA, '''
    def main():
        mass,e = 131*AMU,10.
        endpoint = float(recoil_max(e,mass))
        values = dsigma(131,mass,e,np.array([0.,1.,endpoint,1.01*endpoint]))
        assert values[0]>0 and values[1]>0 and abs(values[2])<1e-50 and values[3]==0
        save_result({'mass_GeV':mass,'Tmax_keV':endpoint,'dsigma_cm2_per_keV':values.tolist(),
                     'includes_flux_or_exposure':False,'nuclear':'R16 actual M table'})
    ''')
    add('P07',full, '''
    def main():
        parts = direct_counts()
        counts = parts.sum(axis=0)
        save_result({'counts_events_per_bin':counts.tolist(),'total_events':float(counts.sum()),
                     'isotope_A':[128,129,130,131,132,134,136],'isotope_counts':parts.tolist(),
                     'model':'actual M only; fixed SSM; no calibration; no abundance renormalization'})
    ''')
    add('P08',full+FAST, '''
    def main():
        H = build_kernel()
        errors=[]
        for g in [G_SM,G_SM+np.array([.02,.01]),G_SM.astype(complex)+[.01j,.02j]]:
            direct,fast = direct_counts(g).sum(axis=0),fast_counts(H,g)
            errors.append(float(np.max(abs(direct-fast)/np.maximum(abs(direct),1e-30))))
        assert max(errors)<1e-12
        save_result({'H_bins_pn':H.tolist(),'SM_counts':fast_counts(H,G_SM).tolist(),'max_relative_error':max(errors),
                     'scope':'two constant c1 p/n couplings; not full LEFT or light-mediator scan'})
    ''')
    module=runpy.run_path(str(OUT/stages['P07']['directory']/'core.py'),run_name='authoring_check')
    signal=module['direct_counts']().sum(axis=0)
    original=(OLD/stages['P09']['directory']/'core.py').read_text(encoding='utf8').replace('v3.0','v3.1')
    original=replacement_signal(original,signal)
    write(OUT/stages['P09']['directory']/'core.py',original);generated['P09']={'directory':stages['P09']['directory'],'lines':len(original.splitlines())}
    add('P10',full+FAST, '''
    def main():
        direct = direct_counts().sum(axis=0)
        fast = fast_counts(build_kernel(),G_SM)
        er = direct_counts(n_r=401).sum(axis=0)
        enu = direct_counts(n_enu=240).sum(axis=0)
        assert np.allclose(direct,fast,rtol=1e-12)
        assert np.max(abs(er/direct-1))<.002 and np.max(abs(enu/direct-1))<.002
        save_result({'checks':'PASS: actual M Fast/Slow and separate T/E convergence','counts':direct.tolist(),
                     'total_events':float(direct.sum()),'not_claimed':['complete detector Response','official likelihood','external nuclear certification']})
    ''')
    write(OUT/'requirements.txt','numpy>=2\nscipy>=1.12')
    write(OUT/'run_all.py',(OLD/'run_all.py').read_text(encoding='utf8'))
    snapshot={'version':'nuclear-M-v1','files':[{'file':str(p),'sha256':sha(p)} for p in [SOURCE_PATH(),MAIN,RESULT,DATA/'experiment.input.yaml',DATA/'experiment.resources.npz',Path(__file__)]],
        'source_indices':indices.tolist(),'M_coefficients':'exact repr of original floats; no renormalization','source_table':'84 original nodes; other experimental arrays 12 significant digits'}
    write(OUT/'_核对记录/source_snapshot.json',json.dumps(snapshot,ensure_ascii=False,indent=2))
    write(OUT/'_核对记录/stages.json',json.dumps(generated,ensure_ascii=False,indent=2))
    articles(generated,signal)
    parent=PARENT/'README.md'
    text=parent.read_text(encoding='utf8')
    row='| [20261110 PandaX：真实核Response新版本](20261110_PandaX_Response_P01_P10_物理与最小代码/README.md) | 当前v3.1；onboarding＋P01–P10真实M表、独立最小代码及逐项来源；旧KN例保留 |'
    if row not in text:text=text.replace('|---|---|','|---|---|\n'+row,1)
    text=text.replace('[20261110 PandaX US2：onboarding＋P01–P10]','[20261110 PandaX US2：历史KN例]')
    write(parent,text)
    print(json.dumps({'folder':str(OUT),'stages':generated,'total_events':float(signal.sum())},ensure_ascii=False))


def SOURCE_PATH():return ROOT/'data/responses/responses_all.json'
def replacement_signal(code,signal):
    import re
    return re.sub(r'^SIGNAL = np.array\(.*$',lambda _: 'SIGNAL = np.array('+repr(signal.tolist())+')  # [O7/O8] actual-M P07 snapshot, not digitized signal',code,flags=re.M)


def articles(stages,signal):
    r=json.loads(RESULT.read_text(encoding='utf8'))
    definitions={
        'ONBOARDING':('scope','先固定身份、数据、单位、出处与缺口，形成可计算合同。','check_inputs / build_onboarding_contract','R01/R02/R04/R09/R16；主文第1–10章'),
        'P01':('observable','确定比较的是电子数箱里的原始事件数D_i。','main','R01 p5式(12)后、p7 Fig.1左；Ne=4,4.5,…,8'),
        'P02':('target','用九行天然数丰度与原子摩尔质量算绝对核数；核动力学用A·amu。','TARGETS / main','R09 NIST九行；R02 p3曝光1.04t·yr；R20质量约定'),
        'P03':('source','总通量乘能谱形状，得到每秒每能量中微子数。','SOURCE / flux','R04 Bahcall官网表；R01 p5式(11)后Φ=5.46×10⁶；84点是829点降采样'),
        'P04':('modules','把SM核子耦合与真实核M矩阵收缩成散射振幅。','M_TABLE / coherent_M / main','R16实际Xe M系数；R20 left_to_ci、amplitude及p/n归一化'),
        'P05':('modules','振幅乘相空间，得到每核每keV微分截面。','dsigma / energy_min / recoil_max','R20 m/(8πEν²)，单次cm²/keV转换；精确弹性端点'),
        'P06':('detector','用Qy平均值把反冲T分到Ne箱，并施加总接受度。','QY / EFF / recoil_edges / bin_probabilities','R02 p5 Fig.4下图nominal、p3 Fig.1 Total(US2)；R01式(15)；不展宽'),
        'P07':('prediction','将源×截面×核数×曝光×选择积分成八箱信号。','fixed_weight / direct_counts / bin_integrals','主文第2–7章；七核素原权重，不乘校准c_i；Qy逆映射积分'),
        'P08':('prediction','把每箱的真实M矩阵预积分成H，扫描时只算g†H_i g。','build_kernel / fast_counts','本例按P07积分定义推导；仅两个常数p/n耦合，不是完整LEFT Fast'),
        'P09':('statistics','以S+B为期望与观测D作Poisson比较。','SIGNAL / poisson_deviance','R01式(17)的Poisson核心教学缩减；固定图线拟合背景，非官方profile'),
        'P10':('status','检查积分、Fast/Slow与收敛，并限制可宣称的结果。','main','本地数值一致性；不是外部核表认证或论文精确复现')}
    mapping=[];rows=[]
    for key,stage in sorted(stages.items()):
        anchor,physics,symbols,source=definitions[key]
        code=OUT/stage['directory']/'core.py';tree=ast.parse(code.read_text(encoding='utf8'))
        functions={n.name:[n.lineno,n.end_lineno] for n in tree.body if isinstance(n,ast.FunctionDef)}
        selected={name:functions[name] for name in symbols.split(' / ') if name in functions}
        origin=OUT/stage['directory']/'物理说明.md'
        text='# '+key+'：'+physics+'\n\n'+link(origin,MAIN,'对应主onboarding v3.1')+'（#'+anchor+'） · [核心代码](core.py) · [输入与来源](../ONBOARDING.md)\n\n'+physics+'\n\n'
        if key in ('P04','P05','P07','P08','P10'):
            text+='本例直接求值R16的Xe核M多项式；没有KN或(Z,N)外积替代表。为简洁仅保留c₁/M，主项目另算非零自旋/轨道项。\n\n'
        text+='程序位置：'+', '.join(name+'（'+str(span[0])+'–'+str(span[1])+'行）' for name,span in selected.items())+'。数据和函数旁的[O编号]对应主文章节。\n\n依据：'+source+'；完整标准引文见本目录ONBOARDING.md。\n'
        write(origin,text)
        rows.append('| '+key+' | '+physics+' | '+link(OUT/'README.md',origin,'物理说明')+' | '+link(OUT/'README.md',code,'core.py')+' | '+str(stage['lines'])+' |')
        mapping.append({'stage':key,'file':str(code.relative_to(OUT)),'chapter_anchor':anchor,'functions':selected,'source':source})
    readme='# PandaX：真实核Response的onboarding＋P01–P10最小代码\n\n**核响应新版本；旧KN示例原位保留。** 对应'+link(OUT/'README.md',MAIN,'主onboarding v3.1')+'；只保留c₁/M核心，七核素原绝对权重、固定SSM，代码各自带数值，复制一个core.py到空目录即可运行。\n\n| Skill | 一句话物理 | 短文 | 独立代码 | 行数 |\n|---|---|---|---|---:|\n'+'\n'.join(rows)
    readme+=f'\n\nP07 M-only教学结果 **{signal.sum():.9f}** 事例；主项目M-only {sum(r["channel_decomposition"]["counts_by_channel"]["M"]):.9f}，全部已实现SM通道 {r["total_events"]:.9f}。教学差异来自84点源谱和网格，未重调通量或逐箱归一。\n\n```powershell\npython -m pip install -r requirements.txt\npython run_all.py\n```\n\n[详细输入/来源/程序映射](ONBOARDING.md) · [旧KN示例](../20261110_PandaX_P01_P10_物理与最小代码/README.md) · [核对](<'+os.path.relpath(ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2/TEACHING_VALIDATION.json',OUT).replace('\\','/')+'>)\n'
    write(OUT/'README.md',readme)
    origin=OUT/'ONBOARDING.md'
    text='# PandaX最小核Response例：onboarding输入、来源与程序位置\n\n[主文完整v3.1](<'+os.path.relpath(MAIN,OUT).replace('\\','/')+'>) · [总览](README.md)\n\n核内Response与探测器Response分属第4/5章。本目录只保留真实M表的c₁散射；探测器仍为nominal Qy无分辨率平均映射。\n\n'
    text+='| 实际输入 | 来源及精确定位 | 本目录处理 |\n|---|---|---|\n| Φ、sin²θW | R01 p5式(11)后、p3式(2)后 | 固定5.46×10⁶、0.23857 |\n| f(Eν) | R04官网829行中心谱列1/2 | 每10行留1行及末点，84节点；不重归一 |\n| 靶 | R09 NIST九核素A、原子质量、数丰度 | 九行计算核数分母；仅有M表的七核素参加积分 |\n| M、b | R16 responses_all.json七个Xe键，responses.M/basic.b | 升幂11系数；exp(−2y)；q GeV、b GeV⁻¹；原浮点数repr无损内嵌 |\n| 核匹配/质量 | R20共享LEFT、amplitude、cross_section | c₁=G_F g/√2；A·amu一致；无额外形状或自旋因子 |\n| Qy/接受度 | R02 p5 Fig.4下图、p3 Fig.1黑虚线 | 原36/99节点；12位有效数；Total含ROI只一次 |\n| Ne/D/B | R01 p5分箱、p7 Fig.1左 | 八箱；D原始计数；B仅拟合投影教学固定背景 |\n\n'
    text+='具体函数/行号：\n\n| Skill | 主文章节 | 独立程序位置 |\n|---|---|---|\n'
    for row in mapping:text+='| '+row['stage']+' | ['+row['chapter_anchor']+'](<'+os.path.relpath(MAIN,OUT).replace('\\','/')+'#'+row['chapter_anchor']+'>) | '+', '.join(k+':'+str(v[0]) for k,v in row['functions'].items())+' |\n'
    text+='\n数值来源哈希、源谱保留行与版本记录：[source_snapshot.json](_核对记录/source_snapshot.json)。Xe124/126缺表、不重归一；核表外部作者认证仍未闭合。P09为固定背景教学例，不宣称R01 Fig.2/4结果。\n\n'
    sources=json.loads((ROOT/'workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml').read_text(encoding='utf8'))['sources']
    for sid in ['R01','R02','R04','R09','R16','R20','R18']:
        text+='['+sid+'] '+next(s['citation'] for s in sources if s['source_id']==sid)+'\n\n'
    write(origin,text)
    write(OUT/'_核对记录/code_onboarding_map.json',json.dumps(mapping,ensure_ascii=False,indent=2))
    write(OUT/'_核对记录/README.md','# 来源与构建\n\n构建器：'+link(OUT/'_核对记录/README.md',Path(__file__),'build_pandax_nuclear_teaching.py')+'。仅构建时读取原项目；独立core.py不导入它或其他阶段。\n\n[source_snapshot.json](source_snapshot.json) 固定实际来源；[stages.json](stages.json) 是阶段清单；[code_onboarding_map.json](code_onboarding_map.json) 是实际函数位置。\n')


if __name__=='__main__':main()
