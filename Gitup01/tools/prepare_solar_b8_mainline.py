"""Preserve current files and promote the selected solar-B8 evidence into canonical runs."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'重构/20261106_Onboarding_provenance_revision'
BACKUP=ROOT/'backup/solar-b8-sm-mainline-20261107-01'
FAMILIES=[('PandaX4T','PandaX4T_2024_US2'),('XENONnT','XENONnT_2024_SolarB8')]
QUOTE='现在已经并入主线了是吧。如果没有请并入主线。下面请你先以标准模型作为banchmark，对示例数图进行计算。按照已有项目的流程进行计算。'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

assert not BACKUP.exists(),'Preparation is create-only; inspect the existing canonical checkpoint.'
for row in json.loads((OLD/'DATA_FILES.json').read_text(encoding='utf8')):
    assert sha(ROOT/row['file'])==row['sha256'],row['file']
paths=['cevns_pyeft/experiments/generic_input.py','cevns_pyeft/experiments/generic_input.schema.json',
       'cevns_pyeft/experiments/component_bindings.json','cevns_pyeft/experiments/package_profiles.py',
       'cevns_pyeft/experiments/input_package.py','cevns_pyeft/experiments/README.md',
       'cevns_pyeft/nuclear/README.md','cevns_pyeft/theory/README.md','tools/README.md','tests/README.md',
       'workflows/cevns-pyeft/README.md','data/README.md','data/experiments/README.md','docs/experiments/README.md',
       'docs/references/Solar_CEvNS/README.md','backup/BACKUP_MANIFEST.md','README.md']
for family,dataset in FAMILIES:
    paths.extend([f'data/experiments/{family}/{dataset}/README.md',f'docs/experiments/{family}/datasets/{dataset}/README.md'])
records=[]
for name in paths:
    p=ROOT/name
    if not p.exists():continue
    dest=BACKUP/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    assert sha(p)==sha(dest)
    records.append({'source':name,'backup':dest.relative_to(ROOT).as_posix(),'sha256':sha(p)})
dump(BACKUP/'MANIFEST.json',records)
(BACKUP/'README.md').write_text('# Solar B8 SM mainline backup\n\n2026-11-07. Files preserved before the new SM package profile, canonical phase records and benchmark. MANIFEST.json lists exact paths and hashes. Recovery only; not scientific input.\n',encoding='utf8')
with (ROOT/'backup/BACKUP_MANIFEST.md').open('a',encoding='utf8') as f:
    f.write('\n- 2026-11-07：太阳8B主线/SM benchmark修改前备份：[说明](solar-b8-sm-mainline-20261107-01/README.md) · [指纹](solar-b8-sm-mainline-20261107-01/MANIFEST.json)。\n')

source=json.loads((OLD/'P00_SOURCE_REGISTER.yaml').read_text(encoding='utf8'))
constants=ROOT/'cevns_pyeft/foundation/constants.py'
source['sources'].append({'source_id':'R18','citation':'CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。',
    'uri_or_path':str(constants),'sha256':sha(constants),'verification_scope':'实际使用G_F、AMU_GEV、m_e、HBARC_GEV_FM、GEV_INV2_TO_CM2、SEC_PER_YEAR；数值由参数卡固定并与本地模块核对。'})
for family,dataset in FAMILIES:
    run=ROOT/'workflows/cevns-pyeft/runs'/family/dataset
    run.mkdir(parents=True,exist_ok=False)
    original=json.loads((OLD/f'{family}_P01_EVIDENCE_LEDGER.yaml').read_text(encoding='utf8'))
    original['source_register']='P00_SOURCE_REGISTER.yaml'
    source_copy=dict(source,experiment_slug=family,dataset_id=dataset,revision='sm-forward-20261107-1')
    dump(run/'P00_SOURCE_REGISTER.yaml',source_copy)
    dump(run/'P01_EVIDENCE_LEDGER.yaml',original)
    contract=json.loads((OLD/f'{family}_P03_PHYSICS_CONTRACT.yaml').read_text(encoding='utf8'))
    contract['scientific_claim']='SM forward benchmark; XENONnT official early response; PandaX true-recoil diagnostic until US2 response exists. Exact published fit/CI not claimed.'
    dump(run/'P03_PHYSICS_CONTRACT.yaml',contract)
    (run/'P02_MISSING_AND_CONFLICTS.md').write_text((OLD/'P02_MISSING_AND_HANDOFF.md').read_text(encoding='utf8')+'\n本次SM前向计算不依赖Fig.4的EFT核多项式。PandaX电子数谱仍因US2响应缺失受阻；XENONnT采用早期官方重铸基底，并保留其有限精度声明。\n',encoding='utf8')
    dump(run/'P04_DECISION_LOG.yaml',{'schema_version':1,'entries':[{'decision_id':'D0001','date':'2026-11-07','scope':'canonical integration and SM forward benchmark','user_quote':QUOTE,
        'interpretation':'继续此前指定的Response方法。以2411.11749v1树级SM、KN、Bahcall及参考通量比较事件谱。先交付有输入的计算，不编造PandaX电子数响应。',
        'execution_authorized':True,'result_acceptance':'NOT_REVIEWED','scope_limits':['no c_i','no fitting/CI or BSM scan','no fabricated missing response','existing datasets preserved']}]})
    dump(run/'AUTHORIZATION_LOG.yaml',{'schema_version':1,'log_type':'write_authorization_log','entries':[{'authorization_id':'W0001','status':'ACTIVE','date':'2026-11-07','approval_kind':'manual_write','approval_message_ref':'conversation:2026-11-07-user-sm-benchmark','user_quote':QUOTE,
        'scope':'existing_dataset','allowed_actions':['create','modify'],'create_paths':[str(run.relative_to(ROOT)),f'data/experiments/{family}/{dataset}/experiment.*','cevns_pyeft/experiments/solar_b8.py','cevns_pyeft/experiments/solar_input.py','cevns_pyeft/theory/sm_coherent.py','tools/build_solar_b8_packages.py','tools/run_solar_b8_sm_benchmark.py','tests/test_solar_b8_sm_contract.py'],
        'modify_paths':paths,'delete_paths':[],'production_paths_affected':True,'recovery_plan':str(BACKUP/'MANIFEST.json'),'result_acceptance_separate':True}]})
    (run/'00_PHASE0_PLAN.md').write_text('''# 太阳8B SM前向计算：Phase 0

2026-11-07。用户授权并入主项目并按已有流程计算SM事件谱；结果尚未经用户验收。

| 组件 | 判断 | 实际调用与证据 |
|---|---|---|
| 输入包与运行入口 | REUSE / ADAPTER | v2 Compiler → load_experiment_package → predict_experiment；增加显式solar profile，不复制旧实验参数 |
| Source / Target | CONFIG_ONLY / ADAPTER | Bahcall中心谱、天然Xe九核素、P00/P01；通量×有效秒数×1t核数等价于总质量时间，不声称1t是实测质量 |
| SM / 核运动学 | SHARED_EXTENSION / REUSE | 文献[1]式(1)–(3)树级SM与KN；复用ElasticKinematics、项目常量；不调用Fig.4 EFT系数 |
| Detector | ADAPTER / BLOCKED | XENONnT单能基底在(E,Ly,Qy)插值，边际化三观测轴；PandaX仅真实反冲接受度诊断，电子数谱BLOCKED |
| Slow积分 | REUSE | rates.recoil.integrate_recoil_yield、probability_fold；原样保留每run/核素分量与单位 |
| Fast / Statistics | NOT_REQUESTED | 本轮只做SM前向事件谱与参考谱比较，未请求拟合或扫描 |

## 预定检验

通量/曝光线性缩放、响应概率和≤1、核素/run分量和、分别加密Eν与T。
数值收敛容差逐箱max(2e-4 events, 0.2%)；原模型与公开重铸残差分别报告，不用重标定通过。
外部谱只作对照，不作为重新定义SM输出的输入。保留文献版本、参数点、图、数组和指纹。
加入共享模型后运行现有CsI2017/CsI2021/Ar2020相关回归。

## 授权、范围与恢复

D0001与W0001记录用户原话。只新增solar包、适配器、SM模型、阶段/benchmark记录并维护直接消费者。
旧15份核心onboarding与原数值表保留；已有实验公式、参考数组和容差不改。修改前备份见BACKUP_MANIFEST。
正式科学验收与默认全局激活不由数值PASS替代，结果阶段保留NOT_REVIEWED。
''',encoding='utf8')
    (run/'README.md').write_text(f'# {dataset} 主线记录\n\n2026-11-07：按用户要求并入原项目的阶段记录。\n\n[Phase 0](00_PHASE0_PLAN.md) · [来源](P00_SOURCE_REGISTER.yaml) · [证据](P01_EVIDENCE_LEDGER.yaml) · [合同](P03_PHYSICS_CONTRACT.yaml) · [缺口](P02_MISSING_AND_CONFLICTS.md) · [决定](P04_DECISION_LOG.yaml) · [授权](AUTHORIZATION_LOG.yaml)\n\nSM结果和实际Gate由本轮计算后回填；不将计划当作已计算。\n',encoding='utf8')
    family_readme=run.parent/'README.md'
    if not family_readme.exists():family_readme.write_text(f'# {family} 主线记录\n\n[{dataset}]({dataset}/README.md)\n',encoding='utf8')
print('Verified 45 inputs; created two canonical source/evidence/contract/phase0 records and backups.')
