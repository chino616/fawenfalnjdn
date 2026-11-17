"""Compile the reviewed solar inputs into ordinary v2 Runtime packages."""
from pathlib import Path
import sys,json,hashlib,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.experiments.generic_input import binding_contracts
from cevns_pyeft.experiments.package_compiler import write_package


def build(family,dataset,*,overwrite=False,check=False):
    directory=ROOT/'data/experiments'/family/dataset
    run=ROOT/'workflows/cevns-pyeft/runs'/family/dataset
    xenon=family=='XENONnT';detector='xenon_mono_basis_v1' if xenon else 'recoil_efficiency_projection_v1'
    ids=['solar_b8_flux_v1','explicit_target_inventory_v1','klein_nystrand_v1','coherent_sm_kn_v1',detector,'solar_b8_sm_v1']
    register=json.loads((run/'P00_SOURCE_REGISTER.yaml').read_text(encoding='utf8'))
    sources={row['source_id']:dict(row,kind='primary_or_direct',version=row.get('sha256') or 'see citation',locator=row.get('verification_scope','see citation')) for row in register['sources']}
    sources['USER']={'kind':'project_decision','version':'2026-11-07','locator':'P04_DECISION_LOG.yaml D0001; user requests canonical SM forward benchmark',
                     'citation':'本项目. SM benchmark数值处理约定[CP/OL]. 2026-11-07. 记录在正式Phase 0和参数卡；不是新增实验测量。'}
    params={};arrays={};meta={};models={};model_parameters={mid:[] for mid in ids};model_arrays={mid:[] for mid in ids}
    def parameter(key,v,unit,owner,source,meaning,control=False):
        owners=[owner] if isinstance(owner,str) else owner
        params[key]={'value':v,'unit':unit,'role':'runtime_control' if control else 'direct_input','meaning':meaning,
                     'source_refs':[source],'consumers':owners,'status':'PROJECT_DERIVED' if control else 'SOURCE_EXTRACTED'}
        for mid in owners:model_parameters[mid].append(key)
    def array(key,a,unit,owner,source,meaning,coordinates=False):
        a=np.asarray(a,dtype=float);arrays[key]=a;model_arrays[owner].append(key)
        meta[key]={'key':key,'unit':unit,'shape':list(a.shape),'dtype':str(a.dtype),
                   'axes':[{'name':key+'_axis'+str(i),'unit':unit if a.ndim==1 else '1','rule':'explicit source order; '+meaning} for i in range(a.ndim)],
                   'meaning':meaning,'role':'direct_input','source_refs':[source],
                   'normalization':{'quantity_kind':'coordinate' if coordinates else 'table','runtime_authority':'array',
                                    'included_factors':['selection'] if key.startswith('response_SR') else [],'runtime_factors':[]},
                   'sha256_raw_c_order':'0'*64,'generation':None}
    parameter('source.total_flux',5.46e6,'cm^-2 s^-1',ids[0],'R01','2411.11749v1 PDF p5 Eq.(11)后，参考总通量；形状表不含该值')
    parameter('target.anchor_mass_kg',1000.,'kg',ids[1],'USER','计算归一化锚点1t，不是实测探测器质量；与质量时间因子配对',True)
    parameter('target.Z',54.,'1',[ids[1],ids[3]],'R09','NIST Xenon，Z=54')
    constants=[('avogadro',6.02214076e23,'mol^-1',ids[1],'R13','SI第9版§2.2/Table1精确值'),
      ('amu_GeV',float(c.AMU_GEV),'GeV/u',ids[1],'R18','foundation/constants.py::AMU_GEV；原子质量的GeV换算'),
      ('electron_mass_GeV',float(c.m_e),'GeV',ids[1],'R18','foundation/constants.py::m_e；裸核质量近似扣除Z个电子，忽略电子结合能'),
      ('G_F',float(c.G_F),'GeV^-2',ids[3],'R18','foundation/constants.py::G_F'),
      ('hbarc_GeV_fm',float(c.HBARC_GEV_FM),'GeV fm',ids[2],'R18','foundation/constants.py::HBARC_GEV_FM'),
      ('GeV_inverse2_to_cm2',float(c.GEV_INV2_TO_CM2),'cm^2 GeV^2',ids[3],'R18','foundation/constants.py::GEV_INV2_TO_CM2；微分截面另乘1e-6转成每keV'),
      ('seconds_per_year',float(c.SEC_PER_YEAR),'s/yr',ids[5],'R18','365.25×86400=31557600；计算单位约定，不是额外活时间')]
    for name,v,unit,owner,source,meaning in constants:parameter('constants.'+name,v,unit,owner,source,meaning)
    parameter('nuclear.radius_fm',1.23,'fm',ids[2],'R01','2411.11749v1 PDF p3 Eq.(3)后：R_A=1.23 A^(1/3) fm')
    parameter('nuclear.skin_fm',.7,'fm',ids[2],'R01','同上，a_k=0.7 fm')
    parameter('interaction.sin2thetaW',.23857,'1',ids[3],'R01','2411.11749v1 PDF p3 Eq.(2)后参考弱混合角')
    parameter('interaction.include_sm',True,'boolean',ids[3],'USER','本轮用户指定纯标准模型，不扫描BSM')
    for key,v in [('n_er',401),('n_enu',240)]:parameter('numerics.'+key,v,'1',ids[5],'USER','Slow直接积分基础节点；另并入原表/响应/观测断点，加密检查后记录',True)
    flux=np.loadtxt(directory/'b8_bahcall1996_official.txt',skiprows=16)
    assert flux.shape==(829,4),'Bahcall original header/column contract changed'
    array('source_energy_MeV',flux[:,0],'MeV',ids[0],'R04','Bahcall官网b8spectrum.txt全部829行第一列',True)
    array('source_shape_per_MeV',flux[:,1],'MeV^-1',ids[0],'R04','同表第二列中心归一化谱；不重归一化，不含总通量/效率')
    isotopes=np.loadtxt(directory/'xenon_natural_isotopes_nist_v2.txt')
    for key,column,unit in [('target_mass_number',0,'1'),('target_atomic_mass_u',1,'u'),('target_number_fraction',2,'1')]:
        array(key,isotopes[:,column],unit,ids[1],'R09','NIST天然Xe表全部九行，对应A/原子质量/数丰度')
    if xenon:
        runs=['SR0','SR1'];exposure=[1.174398,2.342593]
        array('run_exposures_tyr',exposure,'t yr',ids[1],'R17','官方statistical_model_base.yaml livetime_sr0/1；每t yr模板的曝光乘数。合计3.516991，与论文打印3.51分别报告')
        for i,run_id in enumerate(runs):
            with np.load(directory/f'detector/xenonnt_sr{i}_response_early_release_basis.npz',allow_pickle=False) as raw:
                if i==0:
                    for name,key,unit in [('response_energy_keV','energy_keVnr','keVnr'),('response_Ly','Ly_photon_per_keV','photon/keVnr'),('response_Qy','Qy_electron_per_keV','electron/keVnr')]:
                        array(name,raw[key],unit,detector,'R17','官方utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP；原HDF5节点',True)
                array('response_'+run_id,raw['probability_basis'].sum(axis=(-3,-2,-1)),'1',detector,'R17',run_id+'原始1600个单能模板，对shadow/S1BDT/S2BDT求和；含全部原模板选取，不额外乘接受度')
                array('cs2_edges_'+run_id,raw['bin_edges_0'],'PE',detector,'R17',run_id+'原HDF5 /bins/0，原样保留',True)
        for kind in ['ly','qy']:
            model=json.loads((directory/f'detector/ybe_early_release/{kind}_ybe_model_median.json').read_text(encoding='utf8'))
            if kind=='ly':array('yield_energy_keV',model['coordinate_system'],'keVnr',detector,'R17','官方YBe median JSON coordinate_system，501节点；仅在响应0.51–5keV域使用',True)
            else:assert np.array_equal(arrays['yield_energy_keV'],model['coordinate_system'])
            array('yield_'+kind.title()+'_median',model['map'],'photon/keVnr' if kind=='ly' else 'electron/keVnr',detector,'R17','data/signal/'+kind+'_ybe_model_median.json 原始map；非旧WIMP Qy')
        edges=np.arange(4,dtype=float);unit='1';name='run-specific cS2 analysis bin index'
    else:
        runs=['US2'];array('run_exposures_tyr',[1.04],'t yr',ids[1],'R02','2407.10892v3 PDF p3 US2总曝光，未拆造逐run曝光')
        efficiency=np.loadtxt(directory/'detector/pandax_us2_acceptance_2407.10892v3.txt')
        array('efficiency_energy_keV',efficiency[:,0],'keVnr',detector,'R02','2407.10892v3 PDF p3 Fig.1黑色Total(US2)99个可见域矢量节点',True)
        array('efficiency',efficiency[:,1],'1',detector,'R02','同曲线接受度；仅展示真实反冲接受度加权，不代表Ne 4–8的迁移概率')
        edges=np.linspace(float(efficiency[0,0]),float(efficiency[-1,0]),28);unit='keVnr';name='efficiency-weighted true nuclear recoil spectrum'
    array('observable_edges',edges,unit,ids[5],'USER','本轮显式输出坐标：'+('按SR0/SR1各自三箱序号相加，不伪造统一PE边界' if xenon else '可见能区分27个真实反冲箱，非电子数箱'),True)
    bindings=binding_contracts()
    descriptions={ids[0]:('source','experiment_specific','太阳8B通量','Bahcall官网829点谱形×论文参考总通量；源仅乘一次参考年秒数，原表积分约0.999986544，不静默校正。'),
        ids[1]:('target','experiment_specific','天然Xe与质量时间归一化','NIST九核素数丰度与原子质量给核数；参考1t×1yr仅为量纲锚点。动力学用扣除电子质量的裸核近似，电子结合能忽略。'),
        ids[2]:('nuclear','shared_framework','Klein–Nystrand核形状因子','选择文献[1]式(3)的共享解析模型；不读取Fig.4所需的EFT核系数。'),
        ids[3]:('theory','shared_framework','树级SM CEvNS','选择文献[1]式(1)–(2)，保留−T/E项，味普适；公式和单位由共享模块实现。'),
        detector:('detector','experiment_specific','官方单能Response' if xenon else '真实反冲接受度诊断',
                  '原模板已含选取；按官方三线性插值和YBe median曲线构造每能量三箱概率。公开重铸模型不宣称精确原likelihood。' if xenon else 'Ne逐箱Response仍缺；本输出只是真实反冲能量上的效率加权积分，不能冒充电子数事件谱。'),
        ids[5]:('prediction','experiment_specific','Slow直接积分','现有Runtime调用共享recoil积分及概率折叠。保留run与核素分量，单独检验Eν/T收敛；不使用c_i或全局拟合重标定。')}
    report_models={}
    for mid in ids:
        group,classification,title,explanation=descriptions[mid]
        refs={'solar_b8_flux_v1':['R01','R04'],'explicit_target_inventory_v1':['R09','R13','R17' if xenon else 'R02'],
              'klein_nystrand_v1':['R01'],'coherent_sm_kn_v1':['R01','R18'],detector:['R17' if xenon else 'R02'],'solar_b8_sm_v1':['USER']}
        depends={ids[0]:[],ids[1]:[],ids[2]:[],ids[3]:[ids[2]],detector:[],ids[5]:ids[:5]}
        models[mid]={'model_type':group,'model_revision':'1','formula':bindings[mid]['formula'],'formula_purpose':'audit_only',
                     'variables':{},'parameter_refs':model_parameters[mid],'resource_refs':model_arrays[mid],'depends_on':depends[mid],
                     'source_refs':refs[mid],'locator':'见本模型说明及每个输入的直接来源/原文件定位','meaning':explanation,
                     'domain':'纯SM，太阳8B；'+('响应0.51–5keV' if xenon else '接受度可见真实反冲能区'),
                     'boundary':'不外推、不重复曝光/效率；缺失能力单独BLOCKED','binding_status':'BOUND_UNVERIFIED','implementation_contract':bindings[mid]['contract']}
        report_models[mid]={'group':group,'content_class':classification,'title':title,'explanation':explanation,'equations':[]}
    cap=lambda status,blockers=[]:{'status':status,'blockers':blockers,'evidence':['P00/P01/P03 canonical records; source-native array verification'],'human_approval':'NOT_REVIEWED'}
    document={'package':{'schema_version':'cevns-experiment-input/2','dataset_id':dataset,'experiment_slug':family,
              'analysis_revision':'sm_forward_20261107_1','scientific_claim':'SM forward benchmark with explicit public response limitations; no inference/CI reproduction',
              'status':'DRAFT','human_approval':'NOT_REVIEWED'},'parameters':params,'models':models,
              'resources':{'archive':'experiment.resources.npz','sha256':'0'*64,'arrays':meta},
              'observable':{'name':name,'unit':unit,'edges_ref':'observable_edges','bin_count':len(edges)-1},
              'assembly':{'profile':'solar_b8_sm_v1','source':{'energy_ref':'source_energy_MeV','shape_ref':'source_shape_per_MeV'},
                'target':{'mass_number_ref':'target_mass_number','atomic_mass_ref':'target_atomic_mass_u','number_fraction_ref':'target_number_fraction','exposures_ref':'run_exposures_tyr'},
                'interaction':{'model_id':ids[3]},'detector':{'mode':'xenon_basis' if xenon else 'recoil_acceptance','model_id':detector,'run_ids':runs},
                'statistics':{},'numerics':{'slow':{'n_er':'numerics.n_er','n_enu':'numerics.n_enu'}}},
              'capabilities':{'signal':cap('PARTIAL',['public recasting precision and exact-paper equivalence remain limited'] if xenon else ['Ne response missing; true-recoil projection only']),
                 'electron_spectrum':cap('PARTIAL' if xenon else 'BLOCKED',[] if xenon else ['PandaX US2 P(Ne-bin|T) absent']),
                 'fast':cap('NOT_APPLICABLE'),'legacy_statistics':cap('NOT_APPLICABLE')},
              'provenance':{'sources':sources,'issues':[{'id':'response_precision','status':'PARTIAL','detail':'最高约6.30%的名义SM重铸差异，不能视为新的实验响应误差先验' if xenon else 'US2电子数响应缺失；真实反冲诊断不替代完整目标','blocks':['strict_paper_reproduction']}]},
              'extensions':{'lab.physics_report':{'models':report_models,'summary':'2026-11-07 SM benchmark输入包，DRAFT/PARTIAL；每个输入附直接来源，旧onboarding保留。',
                    'calculation_steps':['按Bahcall源谱和SM截面求真实反冲率','按天然九核素求和并进行对应响应/接受度投影','乘各run的显式质量时间因子','检查逐箱收敛、组分和及原参考谱差异']}}}
    draft={'ir_version':'cevns-onboarding-draft/1','acquisition':{'mode':'mixed','evidence_claims':[f'{run.relative_to(ROOT).as_posix()}/P01_EVIDENCE_LEDGER.yaml']},
           'requested_capabilities':['signal'],'document':document}
    if not check:
        (run/'SM_ONBOARDING_DRAFT.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        np.savez_compressed(run/'SM_DECLARED_ARRAYS.npz',**arrays)
    report=write_package(draft,arrays,directory,overwrite=overwrite,check=check)
    if not check:(run/'SM_PACKAGE_COMPILATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(dataset,report['status'],len(arrays),'arrays')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overwrite',action='store_true',help='use existing Compiler backup/transaction rules')
    parser.add_argument('--check',action='store_true',help='compare the formal package without overwriting it')
    args=parser.parse_args()
    for family,dataset in [('XENONnT','XENONnT_2024_SolarB8'),('PandaX4T','PandaX4T_2024_US2')]:build(family,dataset,overwrite=args.overwrite,check=args.check)
