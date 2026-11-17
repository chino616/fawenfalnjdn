"""Current v3.1 nuclear-Response onboarding, from actual Runtime output.

Keep v3.0 reports and original packages byte-for-byte. This generator owns the
new reports/current navigation and records the same-chain nuclear delta.
--check compares without writes; it does not authenticate an external nuclear
source or promote a human scientific gate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_solar_b8_onboarding_v3 as old
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_mean_map import with_pandax_mean_map
from cevns_pyeft.experiments.solar_nuclear import with_solar_nuclear_response

OUT = ROOT/'outputs/solar_b8_sm/20261110_nuclear_response_run2'
JOINT = ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8'
CENTRAL = JOINT/'SOLAR_B8_ONBOARDING.v3.1.md'
FAMILIES = old.FAMILIES
SOURCE = ROOT/'data/responses/responses_all.json'
MANIFEST = OUT/'ONBOARDING_BUILD_MANIFEST.json'
EXPECTED = {}
link, table, seq, fmt = old.link, old.table, old.seq, old.fmt


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def put(path, text):
    EXPECTED[path] = text.rstrip()+'\n'


def put_json(path, value):
    put(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def managed(path, text):
    before = EXPECTED.get(path, path.read_text(encoding='utf8') if path.is_file() else '# '+path.parent.name+'\n')
    for a,b in {
        '：当前onboarding v3.0':'：onboarding版本',
        '当前统一阅读版本：v3.0':'历史统一阅读版本：v3.0',
        '| 当前入口 |':'| 历史v3.0入口 |',
        '## 当前阅读入口':'## 历史v3.0阅读入口',
        '历史记录（当前内容已整合到v3.0）':'历史记录（v3.0时期）',
        '本页仅以上方v3.0为当前说明':'当前SM以页首v3.1为准，旧矢量结果仍按历史版本解释',
        '当前结论及未决项以v3.0为准':'当时结论按v3.0保留，当前SM及其未决项见页首v3.1',
        '各版本和当前v3.0':'各版本与历史v3.0',
        '当前能力以v3.0和实际运行记录为准':'当前SM能力以v3.1及其实际运行记录为准',
        '当前说明统一为[onboarding v3.0':'当时说明统一为[onboarding v3.0',
        '当前人读版本为docs中的v3.0':'该历史包派生说明对应docs中的v3.0；当前SM阅读v3.1',
    }.items():
        before=before.replace(a,b)
    # Retain old prose, but its navigation block must not call KN the current choice.
    start, end = '<!-- solar-onboarding-v3:start -->', '<!-- solar-onboarding-v3:end -->'
    if start in before:
        before = re.sub(re.escape(start)+'.*?'+re.escape(end),
            lambda m: m[0].replace('当前', '历史v3.0').replace('当前统一', '历史统一'), before, flags=re.S)
    a, z = '<!-- solar-nuclear-v31:start -->', '<!-- solar-nuclear-v31:end -->'
    block = a+'\n\n'+text.strip()+'\n\n'+z
    if a in before:
        after = re.sub(re.escape(a)+'.*?'+re.escape(z), lambda _:block, before, flags=re.S)
    else:
        first, _, rest = before.partition('\n')
        after = first+'\n\n'+block+'\n\n'+rest.lstrip()
    put(path, after)


def current_data(family, dataset):
    d = old.load(family, dataset)
    d['result'] = read(OUT/dataset/'RESULT.json')
    d['actual'] = read(OUT/dataset/'PREPARED_MODEL.nuclear.json')
    base = load_experiment_package(d['base'])
    if not d['xenon']:
        base = with_pandax_mean_map(base, qy_file=d['base']/'detector/pandax_qy_nominal.txt')
    prepared = with_solar_nuclear_response(base, response_file=SOURCE)
    if prepared.physics_fingerprint != d['result']['physics_fingerprint']:
        raise ValueError('actual nuclear implementation/inputs changed; rerun, do not relabel old results')
    d['prepared'] = prepared
    return d


def status_rows(d):
    return [
        ['本地核表SM事例数', '已算；本地ResponseDB/Li2026约定', '数值资源已具备；科学结果接受NOT_REVIEWED'],
        ['完整天然Xe九核素', 'PARTIAL', 'MISSING：Xe124、Xe126核响应系数；未用KN/邻核补齐，七核素不重归一'],
        ['核表外部作者/生成认证', 'UNRESOLVED', 'R16原始作者发布、转换与外部绝对归一化；不阻断用户明确选择的本地复用'],
        ['探测器读出', 'US2无分辨率平均映射' if not d['xenon'] else 'R17早期YBe重铸基底',
            '完整US2接受后P(Ne箱|T)仍未重建' if not d['xenon'] else '严格原2024模型版本等价性待核'],
        ['2411.11749v1 Fig.1等价', '未认证', '该文采用KN且含作者c_i/拟合约定；本轮按用户要求改用核表，论文蓝线只作参考'],
        ['Fig.2/4统计', '未计算', '适用的背景与响应nuisance、拟合/置信区间约定仍需完成'],
        ['V/B−L旧结果', '保留KN历史结果', '本轮只重算SM；不得把旧矢量结果标为核表Response计算']]


def render(d, origin):
    result, model = d['result'], d['prepared'].model
    audit = read(OUT/'NUCLEAR_INPUT_AUDIT.json')
    legacy_sections, _ = old.sections(d, origin)
    legacy = {key:body for key, title, body in legacy_sections}
    chapters = []
    def add(key, title, body):
        chapters.append((key, title, body))
    add('scope', '1. 实验范围、身份与版本',
        '**本版明确采用原子核Response计算，不采用KN作为主预测。** “原子核Response”指振幅内的核结构；探测器响应另见第5章。'
        '本版为2026-11-10新版本v3.1；本地核表约定下已实际计算，外部核源认证仍属草稿，不标成论文精确复现终稿。\n\n'+
        table(['项目','本版选择/来源'], [
            ['dataset', d['dataset']+'；原YAML/NPZ身份与数据不变'],
            ['科学决定', 'D0004：用户“我现在要求按照response计算”，结合“振幅的，原子核的response”；执行授权W0004，结果接受另行登记'],
            ['SM基准参数', 'R01 arXiv:2411.11749v1 p3 Eq.(2)、p5 Eq.(11)后；sin²θW=0.23857，Φ=5.46×10⁶ cm⁻²s⁻¹固定'],
            ['主预测', '本地核表 → 共享SM匹配 → 粒子/核响应收缩 → 截面 → 原有源与探测器处理 → 事例数'],
            ['KN用途', '仅同七核素、同A·amu质量的显式对照；旧九核素KN计算与v3.0原位保留'],
            ['通量与校准', '不拟合或换算通量；不使用作者/经验c_i；无逐箱事后缩放']])+old.refs(d, origin, ['R01','R16']))
    add('source', '2. Source：总通量、谱形与味态', legacy['source'])
    target = legacy['target']
    target = target.replace('物质数使用原子质量；运动学使用 `m_kin[GeV]=atomic_mass[u]×amu_GeV−54×m_e[GeV]`，忽略电子结合能。',
        '物质数仍使用NIST九核素原子质量；**本版振幅、相空间和运动学统一使用 `m_A=A×0.93149410372 GeV`**，依据R20现有共享振幅约定。旧裸核质量仅留在历史KN包中。')
    target += '\n### 本轮实际参与求和的核素\n\n'+table(['核素','原数丰度','本轮每吨绝对核数','质量GeV','处理依据'], [
        [t.isotope_id, fmt(d['arrays']['target_number_fraction'][list(d['arrays']['target_mass_number']).index(int(t.isotope_id[2:]))]),
         fmt(t.number_of_nuclei), fmt(t.kinematic_mass_GeV), 'R09原九行摩尔质量作分母；D0004不重归一；R20质量约定']
        for t in model.targets.isotopes])
    target += '\n覆盖天然Xe数丰度99.8158%；缺失Xe124、Xe126合计0.1842%。这不是给遗漏贡献设0的物理假设，而是只交付已覆盖核素的部分预测。'
    target += f'七核素对应锚点质量{model.targets.detector_mass_kg:.9f}kg；完整材料锚点仍为1000kg，曝光分母不变。\n'
    add('target', '3. Target、核数与曝光', target)
    module = table(['步骤/选择','实际组件','数据/约定的直接依据'], [
        ['主Interaction','solar_sm_nuclear_table_v1；'+link(origin, ROOT/'cevns_pyeft/experiments/solar_nuclear.py','SolarNuclearSM'), 'R20共享SM LEFT与left_to_ci；无一般BSM输入'],
        ['Nuclear Structure','ResponseDB，七个Xe键、八通道', 'R16实际JSON；W=e⁻²ʸΣaₖyᵏ，y=(qb/2)²；q用GeV、b用GeV⁻¹；p/n顺序(p,n)'],
        ['振幅','flavor_kernel_onebody_li2026', 'R20 amplitude.py：compute_R_matrices→_contract_R_W→各通道和；不再乘KN、Helm或额外自旋因子'],
        ['截面','m_A Tr(ρK)/(8πEν²)', 'R20 cross_section.py；先cm²/GeV，再乘10⁻⁶为cm²/keV；核数/效率不在截面中'],
        ['能量数组','固定T下对共享SM振幅作精确二次式重组', 'SM非零c1,c2,c5,c6,c7不依赖E；共享R最高E²；三个合法E点确定系数，非实验拟合；第四点与原逐E API对照见测试'],
        ['端点','精确弹性运动学；A·amu一致', '仅将小于128ε·Σ|多项式项|的浮点相消残差置零，保留非零自旋项'],
        ['KN对照','StandardModelKN；半径1.23fm、skin0.7fm', 'R01 p3 Eq.(3)；只在control使用，与主预测同七核素、同质量、同其余输入']])
    module += '\n### 已打开的真实核数组\n\n'+table(['核素','J','b [GeV⁻¹]','M系数shape','M(0)：pp / pn / nn'], [
        [key, v['basic']['J'], fmt(v['basic']['b']), '2×2×11', seq([v['channels']['M']['W_at_y0'][0][0],
         v['channels']['M']['W_at_y0'][0][1],v['channels']['M']['W_at_y0'][1][1]])] for key,v in audit['isotopes'].items()])
    module += '\n全部八通道的系数、shape、b与y=0矩阵：'+link(origin, OUT/'NUCLEAR_INPUT_AUDIT.json','逐核素完整数值审计')+'；原件：'+link(origin,SOURCE,'responses_all.json')+'。SHA256 `'+audit['sha256']+'`。'
    module += '\n\n下表给出本次实际积分的通道，零项为现有SM/实现的结果，不能据此宣称一般EFT通道都不存在。\n\n'+table(['通道','各箱合计事例','取得/取零依据'],[
        [ch, fmt(sum(values)), '共享SM匹配/粒子响应与R16实际核数组收缩；SigmaPDelta在现有粒子响应定义为0' if ch=='SigmaPDelta' else '共享SM振幅逐通道输出，再用相同源与探测器折叠']
        for ch,values in result['channel_decomposition']['counts_by_channel'].items()])
    lecs = model.interaction.describe().parameters['lecs']
    def lec_unit(key):
        if key in ('B0_m_u','B0_m_d'):
            return 'GeV²'
        if key in ('g_A','L1','L2','L3','L4','g5','g6','g7','g8','g9'):
            return '1'
        return 'GeV'
    module += '\n实际LEC值（沿用R20 `lec.py::DEFAULT_LECS`，本地约定；不是R01另公布的实验输入。表列共享配置全部值，SM主要用L1–L4与m_N）：\n\n'+table(['名称','实际值','单位','直接出处'],[
        [key,fmt(val),lec_unit(key),'R20 lec.py同名字段及类docstring单位合同；constants.LECs_known相应定义'] for key,val in lecs.items()])
    module += old.refs(d,origin,['R16','R20','R18','R01'])
    add('modules','4. 原子核Response、振幅与截面选择',module)
    detector = ('**本章是探测器读出，与第4章原子核Response是两步。** '+
        ('继续使用用户D0003选择的无分辨率平均映射；核表路线不自动补出完整US2迁移概率。\n\n' if not d['xenon'] else
         '继续使用R17官方早期YBe重铸基底与中位产额；已有探测器数值不因换核结构而重提取。\n\n'))
    detector += legacy['detector']
    detector = detector.replace('当前实现对九种Xe同位素共用', '原模型对九种Xe同位素共用；本轮对已覆盖的七种同位素共用')
    if not d['xenon']:
        observation=model.observation[0]
        detector += '\n### 本版实际执行的简化观测\n\n'+table(['输入','实际数值/文件','直接出处和处理'],[
            ['Qy',link(origin,d['base']/'detector/pandax_qy_nominal.txt','36×2 nominal表'), 'R02 2407.10892v3 p5 Fig.4下图；T=0.2–3.1keVnr；分段线性，无外推'],
            ['总接受度',link(origin,d['base']/'detector/pandax_us2_acceptance_2407.10892v3.txt','99×2表'), 'R02 p3 Fig.1黑虚线Total(US2)，已含ROI；只乘一次'],
            ['均值映射','Ne=T Qy(T)', 'R01 p6 Eq.(15)；不展宽；逐箱积分使用逆映射T边界，不另乘第二次Jacobian'],
            ['Ne箱界',seq(d['result']['observable_edges']),'R01 p5式(12)后；8箱'],
            ['反解T边界[keVnr]',seq(observation.recoil_edges),'由实际Qy表逐段线性和brentq反解；完整算法solar_mean_map.py::inverse_mean_edges'],
            ['c_i','不应用，即直接预测基线1','用户选择；不声称作者c_i=1；不匹配拟合图线振幅']])
    add('detector','5. Detector Response、Qy与数值取得状态',detector)
    observable = legacy['observable'].replace('当前真实反冲投影','历史KN包的真实反冲投影（非本版Ne输出）')
    if not d['xenon']:
        observable = '**当前输出为八个Ne箱，边界'+seq(result['observable_edges'])+'；原包27个T箱仅为历史元数据。**\n\n'+observable
    add('observable','6. Observable、完整分箱与观测身份',observable)
    pred = '**本版结果由真实核表独立计算。蓝色论文参考线由图中提取，始终不作为本项目Response预测。**\n\n'
    pred += table(['阶段','实际代码/输入','物理工作与出处'],[
        ['P01–P03','load_experiment_package','读原YAML/NPZ：R04源谱、R09核数、R01参数、实验曝光'],
        ['P04','with_solar_nuclear_response → SolarNuclearSM','显式绑定R16七核素；R20匹配与粒子/核响应收缩'],
        ['P05','SolarNuclearSM.dsigma_dT','同A·amu、精确支撑、m/(8πE²)和cm²/keV转换'],
        ['P06','MeanMapExecutor' if not d['xenon'] else 'SolarExecutor / XenonBasisObservation',
         'R02 Qy+Total接受度+R01平均映射' if not d['xenon'] else 'R17单能基底插值和每run原生PE箱'],
        ['P07','predict_experiment → integrate_recoil_yield','逐核素卷积源谱，再乘核数/曝光与选区折叠；每因子一次'],
        ['P10','run_solar_b8_nuclear_benchmark.py','T与Eν分别加密；逐核素/通道/运行期闭合，保留KN公平对照']])
    pred += '\n### 实际逐箱信号 [events/bin]\n\n'+table(['箱','核表SM','其中M','同范围KN','核表/KN−1'],[
        [i+1,fmt(result['counts'][i]),fmt(result['channel_decomposition']['counts_by_channel']['M'][i]),
         fmt(result['kn_control_counts'][i]),f'{100*result["relative_difference_to_matched_KN"][i]:+.6f}%'] for i in range(len(result['counts']))])
    pred += f'\n合计：**核表SM {result["total_events"]:.9f}**；同范围KN {result["kn_control_total"]:.9f}事例。比较同时改变完整SM核通道与核结构；M-only列可单独查看相干主项。'
    pred += '\n\n'+table(['run','实际信号数组'],[[run,seq(values)] for run,values in result['per_run'].items()])
    if not d['xenon']:
        diag=result['diagnostics']
        pred += f'\n已提取Total接受度T域积分{diag["accepted_domain_total_events"]:.9f}事例；均值窗口下/上方各为'+seq(diag['outside_mean_window_events_low_high'])+'。不能把这些迁移未知的域外事件强行补进八箱。\n'
    pred += '\n'+link(origin,OUT/d['dataset']/'RESULT.json','结果、独立收敛与全部输入参数')+' · '+link(origin,OUT/d['dataset']/'prediction.npz','完整各核素/通道数组')+' · '+link(origin,OUT/d['dataset']/'PREPARED_MODEL.nuclear.json','实际Runtime装配与全部资源哈希')+'\n\n'
    pred += '![核表Response SM与同范围KN](<'+os.path.relpath(OUT/d['dataset']/'events.png', origin.parent).replace('\\','/')+'>)\n\n'
    pred += '绿实线=本版真实核表SM；橙虚线=同七核素KN直接计算；灰线=背景参考；黑点=观测及68.27% Garwood Poisson误差棒。PandaX蓝点线=论文作者S+B数字化参考。没有紫色校准线。\n\n'
    pred += '**历史比较边界。** 旧九核素/旧裸核质量KN结果和旧V/B−L点只在'+link(origin,d['docs']/'experiment.physics.v3.0.md','历史v3.0')+'中保留。R01 Fig.1只作为文献参考，R01 Fig.2/4仍不是本次统计计算。'
    pred += '\n\n当前SM主入口`tools/run_solar_b8_sm_benchmark.py`默认转到本核表路线；只有显式`--legacy-kn`才运行历史KN。原包的KN装配仍可单独加载，不能把它与本版显式核表覆盖混用。'
    if not d['xenon']:
        pred += '\n\n'+link(origin,ROOT.parent/'重构/20261110_PandaX_Response_P01_P10_物理与最小代码/README.md','onboarding＋P01–P10真实M核响应最小代码')+'：各份代码独立运行，至多200行；M-only教学缩减与本版全部已实现SM通道分别标注。'
    add('prediction','7. Prediction folding、执行结果与复算',pred)
    add('statistics','8. Statistics、观测与背景的来源和适用范围',
        '**本轮不作拟合。** 信号前向积分不读取D/B；它们只进入比较图。\n\n'+legacy['statistics'].replace(
            'Ne重建信号MISSING；当前T投影不能代入','本版已有简化Ne核表SM信号；完整探测器涨落信号仍MISSING，不冒充原生拟合输入'))
    resources = 'YAML/NPZ保持原包字节；当前执行权威是“原包＋显式核表覆盖”（PandaX另加Qy），不能只打开原包就认为默认已经更换。实际路径和哈希如下。\n\n'
    resources += table(['资源ID','完整本地数值文件','SHA256','本轮用途/直接定位'],[
        [key,link(origin,Path(row['path']),Path(row['path']).name),row['sha256'],row.get('semantic','原包数据；下列正式键/来源表逐项展开')]
        for key,row in d['actual']['resources'].items()])
    resources += '\n### 原包正式数组全部清单\n\n原包observable_edges与KN配置为保留的历史元数据；当前观测边界与核模型以上述实际装配为准。\n\n'+old.array_table(d,origin,list(d['arrays']))
    resources += '\n### 辅助表与其出处\n\n'+table(['数值文件','shape/范围','单位','直接来源、定位与转换','本版用途'],[
        [link(origin,ROOT/item['file'],Path(item['file']).name),old.coverage(item['content']),item['unit'],
         item['source_id']+'；'+item['locator']+'；'+item['conversion'],item['current_role']] for item in d['raw']])
    resources += '\n第4章的核表审计显示全部实际系数；外部作者来源未闭合是“来源认证待补”，与Xe124/Xe126“数值MISSING”分别记录。\n'
    add('resources','9. 全部数值资源、轴与逐项来源',resources)
    add('status','10. 缺失、交接、验证与完整参考文献',table(['能力','状态','缺口/限制'],status_rows(d))+
        '\n计算入口：\n\n```powershell\npython -B tools/run_solar_b8_nuclear_benchmark.py --output <新的运行目录>\npython -B tools/build_solar_b8_onboarding_v3_1.py --check\n```\n\n'
        '本次验证：'+link(origin,OUT/'VALIDATION.json','实际测试/文件保护/来源检查')+'。旧数值未改，结果接受NOT_REVIEWED；不自动推进历史完整探测器响应或统计门槛。\n'+
        old.refs(d,origin,list(d['sources'])))
    s = '# '+d['dataset']+' — onboarding v3.1：原子核Response新版本\n\n'
    s += '**2026-11-10。主路线：真实核响应表；本地约定下已计算，外部核源认证待补。**\n\n'
    s += ' · '.join([link(origin,d['docs']/'experiment.physics.summary.v3.1.md','精简版'),link(origin,d['docs']/'EXPERIMENT_USER_INPUT.v3.1.md','用户资料'),
        link(origin,CENTRAL,'两实验总入口'),link(origin,d['run']/'P00_SOURCE_REGISTER.yaml','来源'),link(origin,d['run']/'P03_PHYSICS_CONTRACT.yaml','配置/决定'),
        link(origin,OUT/d['dataset']/'RESULT.json','实际Benchmark'),link(origin,d['docs']/'experiment.physics.v3.0.md','旧KN v3.0')])+'\n\n'
    s += '<a id="report-toc"></a>\n\n## 目录\n\n'+'\n'.join('- ['+title+'](#'+key+')' for key,title,body in chapters)+'\n\n'
    for key,title,body in chapters:
        s += '<a id="'+key+'"></a>\n\n## '+title+'\n\n'+body+'\n\n[返回目录](#report-toc)\n\n'
    # Retained detector/source formulas acquire a consecutive local numbering.
    counter = iter(range(1,100))
    s = re.sub(r'\\tag\{\d+\}',lambda _:r'\tag{'+str(next(counter))+'}',s)
    return s


def record_delta(d):
    run, result = d['run'], d['result']
    p00 = read(run/'P00_SOURCE_REGISTER.yaml')
    local = {'source_id':'R20','citation':'CEvNS-pyEFT Project. Li2026 one-body SM matching, nuclear-amplitude and cross-section implementation[CP/OL]. 本地工作副本[2026-11-10]. 直接采用本地代码约定；不将其视为R01的核模型或已认证的上游核数据。',
        'uri_or_path':str(ROOT/'cevns_pyeft/theory/li2026/amplitude.py'),'sha256':sha(ROOT/'cevns_pyeft/theory/li2026/amplitude.py'),
        'locator':'rates/differential.py::_sm_left_dim6; theory/li2026/{left_to_ci,responses,amplitude,cross_section,lec}.py',
        'verification_scope':'SM matching; np contraction; A*amu; m/(8pi E^2); existing LECS; no external nuclear-source authentication'}
    p00['sources'] = [s for s in p00['sources'] if s['source_id']!='R20']+[local]
    for source in p00['sources']:
        if source['source_id']=='R16':
            source['uri_or_path']=str(SOURCE)
            source['verification_scope']='D0004 directly adopts existing local JSON and reader convention; all seven Xe keys/eight arrays opened. External author release and conversion remain unresolved.'
    put_json(run/'P00_SOURCE_REGISTER.yaml',p00)
    d['sources']={s['source_id']:s for s in p00['sources']}
    evidence=read(run/'P01_EVIDENCE_LEDGER.yaml')
    evidence['claims']=[c for c in evidence['claims'] if not c['claim_id'].startswith('NR20261110-')]
    for suffix,field,value,unit,source,locator in [
        ('TABLE','theory_response/nuclear_table',{'file':rel(SOURCE),'sha256':sha(SOURCE),'audit':rel(OUT/'NUCLEAR_INPUT_AUDIT.json'),
            'number_fraction':.998158,'missing':['Xe124','Xe126']},'dimensionless W','R16','seven Xe keys; all eight channels; 2x2x11 M; existing np reader normalization'),
        ('METHOD','theory_response/nuclear_method',{'mass':'A*amu','SM':'existing LEFT matching and all nonzero implemented channels','extra_KN_or_spin_factor':False},'shared code convention','R20','shared amplitude, LEFT/LEC and cross-section APIs'),
        ('RESULT','slow_counts/current_nuclear_SM',{'file':rel(OUT/d['dataset']/'RESULT.json'),'counts':result['counts'],'total_events':result['total_events'],
             'physics_fingerprint':result['physics_fingerprint']},'events/bin',None,'standard Runtime, source and detector folding; independent T/E refinements')]:
        evidence['claims'].append({'claim_id':'NR20261110-'+suffix,'field':field,'status':'PROJECT_DERIVED' if suffix!='TABLE' else 'USER_CONFIRMED',
            'source_id':source,'value':value,'unit':unit,'locator':locator,'decision_refs':['D0004'],
            'verification_scope':'Local numerical existence/reader/Runtime consistency only; external author provenance and exact paper equivalence unresolved'})
    put_json(run/'P01_EVIDENCE_LEDGER.yaml',evidence)
    contract=read(run/'P03_PHYSICS_CONTRACT.yaml')
    contract['scientific_claim']='SM nuclear-table Response forward at fixed R01 parameters, seven Xe isotopes without renormalization; original detector approximation/recasting model. No paper-exact or native-likelihood claim.'
    for section,field,cid,value in [('theory_response','current_nuclear_route','NR20261110-TABLE',{'model':'solar_sm_nuclear_table_v1','resource':rel(SOURCE),'basis':'np','missing':['Xe124','Xe126'],'external_provenance':'UNRESOLVED'}),
        ('kinematics_cross_section','current_nuclear_mass_and_units','NR20261110-METHOD',{'mass':'A*amu','cross_section':'m/(8pi E^2) Tr(rho K)','output_unit':'cm2/keV'}),
        ('slow_counts','current_nuclear_result','NR20261110-RESULT',{'file':rel(OUT/d['dataset']/'RESULT.json'),'counts':result['counts']})]:
        slot=contract['sections'][section]
        slot['fields'][field]={'value':value,'unit':'1' if section!='slow_counts' else 'events/bin','evidence_claims':[cid],
            'provenance_status':'LOCAL_RESOURCE_ADOPTED' if section=='theory_response' else 'PROJECT_DERIVED','decision_status':'DRAFT','blocking_scope':[]}
        slot['decision_refs']=list(dict.fromkeys(slot.get('decision_refs',[])+['D0004']))
    put_json(run/'P03_PHYSICS_CONTRACT.yaml',contract)
    branch={'date':'2026-11-10','decision_ref':'D0004','write_ref':'W0004','scope':'actual nuclear-table SM only',
        'current_onboarding':rel(d['docs']/'experiment.physics.v3.1.md'),'result':rel(OUT/d['dataset']/'RESULT.json'),
        'physics_fingerprint':result['physics_fingerprint'],'resources':d['actual']['resources'],
        'coverage':{'number_fraction':.998158,'missing':['Xe124','Xe126'],'renormalized':False},
        'detector':'US2 deterministic mean mapping' if not d['xenon'] else 'official early YBe recasting basis',
        'external_nuclear_source_certification':'UNRESOLVED','human_result_acceptance':'NOT_REVIEWED',
        'historical_KN_results_and_packages':'preserved; old vector results not relabeled'}
    put_json(run/'NUCLEAR_BRANCH.json',branch)
    implementation=read(run/'00_IMPLEMENTATION_MANIFEST.yaml')
    implementation.setdefault('extensions',{})['nuclear_response_20261110']=dict(branch, actual_implementation=d['actual']['implementation'])
    put_json(run/'00_IMPLEMENTATION_MANIFEST.yaml',implementation)
    progress_path=run/'00_MIGRATION_PROGRESS.md'
    current=progress_path.read_text(encoding='utf8')
    progress=json.loads(re.search(r'```json\n(.*?)\n```',current,re.S)[1])
    parallel = 'singlebin_2601_19883' in progress.get('parallel_analyses', {})
    if not parallel and progress['checkpoint']['step_id']!='nuclear_response.result_review':
        progress['previous_checkpoint']=progress['checkpoint']; progress['previous_revision']=progress['revision']; progress['revision']+=1
    progress['updated_at']=max(progress.get('updated_at',''), '2026-11-10')
    nuclear_checkpoint={'phase_id':'P10','phase_name':'actual nuclear Response SM forward review','skill':'cevns-experiment',
        'step_id':'nuclear_response.result_review','next_action':'review actual nuclear-table prediction and separately tracked coverage/source/response limitations','resume_requires':[]}
    if parallel:
        progress['parallel_analyses'].setdefault('multibin_2411_11749', {})['checkpoint'] = nuclear_checkpoint
    else:
        progress['checkpoint'] = nuclear_checkpoint
    phase=run/'phases/P04_P05_P07_P10_nuclear_response.md'
    for p in ['P04','P05','P07','P10']:
        progress['gates'][p+'_nuclear']={'machine':'PASS','human':'NOT_REVIEWED','report_ref':rel(phase),
            'capability':'solar_b8.local_nuclear_SM.'+p,'decision_refs':['D0004']}
    progress['authorization_refs'].update(nuclear_scope='D0004',nuclear_write='W0004')
    progress['artifact_refs'].update(onboarding_current=rel(d['docs']/'experiment.physics.v3.1.md'),nuclear_evidence=rel(run/'NUCLEAR_BRANCH.json'),nuclear_result=rel(OUT/d['dataset']/'RESULT.json'))
    progress['active_blockers']=['external nuclear author-source certification only: upstream release/normalization unresolved',
        'full natural Xe coverage only: Xe124/Xe126 tables missing',
        'strict paper equivalence only: R01 used KN and author c_i/nuisance points unavailable']+(
            ['full detector-response capability only: US2 accepted Ne-bin kernel not rebuilt'] if not d['xenon'] else ['strict original-2024 detector equivalence only: early recasting model scope retained'])
    put(progress_path,'# 主线进度：'+d['dataset']+'\n\n当前SM核结构路线为真实核表Response；旧KN/矢量结果保留，探测器处理另行标注。结果接受NOT_REVIEWED。\n\n```json\n'+json.dumps(progress,ensure_ascii=False,indent=2)+'\n```')
    put(phase,'# P04/P05/P07/P10：原子核Response SM\n\nD0004/W0004选择本地七核素核表；不改共享公式、旧数据或参考数组。\n\n'+
        table(['核对','实际记录'],[['逐核素/通道与归一化',link(phase,OUT/'NUCLEAR_INPUT_AUDIT.json','全部系数、M(0)、hash与外部来源边界')],
        ['振幅/截面',link(phase,ROOT/'tests/test_solar_nuclear_response.py','原逐能量共享API对照、绝对M收缩、端点与拒绝行为')],
        ['事例数和收敛',link(phase,OUT/d['dataset']/'RESULT.json','实际数值/独立T与E加密/通道闭合')],
        ['当前说明',link(phase,d['docs']/'experiment.physics.v3.1.md','同节输入、标准引用、全部缺口')],
        ['检查结果',link(phase,OUT/'VALIDATION.json','测试与文件保护')],['科学接受','NOT_REVIEWED；不把局部机器PASS提升为完整天然Xe/原生统计/论文等价']])+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');args=ap.parse_args()
    datasets=[current_data(*item) for item in FAMILIES]
    for d in datasets:
        record_delta(d)
        origin=d['docs']/'experiment.physics.v3.1.md'
        put(origin,render(d,origin))
        for name,title in [('experiment.physics.summary.v3.1.md','精简版'),('EXPERIMENT_USER_INPUT.v3.1.md','用户资料')]:
            p=d['docs']/name
            put(p,'# '+d['dataset']+' — onboarding v3.1 '+title+'\n\n**新版本：采用振幅中的原子核Response。** 核表→共享SM振幅→截面→原有探测器处理→事例数；固定SSM，无c_i校准。\n\n'+
                link(p,origin,'完整输入、数据来源、算法和结果')+' · '+link(p,OUT/d['dataset']/'RESULT.json','实际计算')+' · '+link(p,d['docs']/'experiment.physics.v3.0.md','旧KN v3.0')+'\n\n'+
                table(['输入/结果','已确定'],[['核表','responses_all.json；7个Xe核素，99.8158%数丰度，不重归一'],['SM','sin²θW=.23857；Φ=5.46×10⁶ cm⁻²s⁻¹固定；R01参数，核模型按D0004切换'],
                ['探测器','US2 nominal Qy均值映射' if not d['xenon'] else '官方早期YBe重铸基底；原生每run PE箱'],['实际信号',fmt(d['result']['total_events'])+'事例；同范围KN '+fmt(d['result']['kn_control_total'])+'事例'],
                ['数据/决定出处','R01/R02/R04/R09/R16/R17/R20及D0004；详细版同节提供完整标准引文和原文定位']])+'\n'+table(['能力','状态','剩余输入/边界'],status_rows(d))+'\n')
        put_json(d['run']/'ONBOARDING_V3_1_INDEX.json',{'version':'3.1','detailed':rel(origin),'summary':rel(d['docs']/'experiment.physics.summary.v3.1.md'),
            'user_input':rel(d['docs']/'EXPERIMENT_USER_INPUT.v3.1.md'),'source_register':rel(d['run']/'P00_SOURCE_REGISTER.yaml'),
            'evidence_ledger':rel(d['run']/'P01_EVIDENCE_LEDGER.yaml'),'physics_contract':rel(d['run']/'P03_PHYSICS_CONTRACT.yaml'),
            'current_branch':rel(d['run']/'NUCLEAR_BRANCH.json'),'human_result_acceptance':'NOT_REVIEWED'})
        put(d['run']/'P02_MISSING_AND_CONFLICTS.md','# '+d['dataset']+'：当前缺口（核Response v3.1）\n\n'+table(['能力','状态','需要什么'],status_rows(d))+'\n\n'+link(d['run']/'P02_MISSING_AND_CONFLICTS.md',origin,'完整当前onboarding')+'\n')
        for p in [d['docs']/'README.md',d['docs'].parent/'README.md',d['docs'].parent.parent/'README.md',d['base']/'README.md',d['base'].parent/'README.md',d['run']/'README.md']:
            managed(p,'## 当前SM onboarding：v3.1 原子核Response\n\n'+link(p,origin,'完整新版本：实际核表/代码/数据来源/逐箱结果')+' · '+link(p,d['docs']/'experiment.physics.v3.0.md','历史KN v3.0')+'。原包与旧结果保留；当前计算需显式使用核表入口，完整缺口见新版本。')
        dest=OUT/d['dataset']
        put(dest/'README.md','# '+d['dataset']+'：核Response SM实际计算\n\n'+link(dest/'README.md',origin,'当前onboarding')+' · [结果/收敛](RESULT.json) · [图](events.png) · [数组](prediction.npz) · [实际装配](PREPARED_MODEL.nuclear.json)\n\n七核素，不重归一；固定SSM；本地核表约定，外部源认证与精确论文等价性待核。\n')
    put(CENTRAL,'# 太阳⁸B onboarding v3.1：原子核Response新版本\n\n**2026-11-10。当前SM采用真实核响应表，不采用KN主预测。** 完整内容分别集中在两份dataset新版本，旧v3.0保留；V/B−L旧结果仍是KN历史计算。\n\n'+
        table(['实验','当前完整onboarding','实际SM事例','同范围KN'],[[d['dataset'],link(CENTRAL,d['docs']/'experiment.physics.v3.1.md','v3.1：逐项来源、实际数组、算法和局限'),fmt(d['result']['total_events']),fmt(d['result']['kn_control_total'])] for d in datasets])+
        '\n两实验都只用已有七个Xe核素，数丰度99.8158%，不重新归一化。Xe124/Xe126数值缺失与核表外部来源认证待补分别记录。PandaX探测器仍采用已授权的无分辨率平均映射；XENONnT保留官方早期重铸基底。\n\n'+
        link(CENTRAL,OUT/'README.md','完整运行/验证')+' · '+link(CENTRAL,JOINT/'SOLAR_B8_ONBOARDING.v3.0.md','历史KN v3.0总文档')+'\n')
    nav_files=['README.md','docs/experiments/README.md','docs/experiments/PandaX4T_XENONnT_SolarB8/README.md','data/README.md','data/experiments/README.md','workflows/cevns-pyeft/README.md','workflows/cevns-pyeft/runs/README.md']
    for name in nav_files:
        p=ROOT/name;managed(p,'## 当前太阳⁸B SM：v3.1 原子核Response\n\n'+link(p,CENTRAL,'当前新版本与两实验实际计算')+'。核表→振幅→截面→事例数；旧KN文档/计算保留。')
    managed(ROOT/'cevns_pyeft/experiments/README.md','## Solar SM：显式原子核Response入口\n\n[solar_nuclear.py](solar_nuclear.py)提供`with_solar_nuclear_response`：绑定实际七核素JSON，复用共享SM振幅，再交给原有标准Runtime。PandaX先调用`with_pandax_mean_map`。不修改旧KN输入包，不用KN替代缺表核素；源/探测器输入保持原配置。')
    managed(ROOT/'tools/README.md','## Solar SM核Response：计算与onboarding\n\n[run_solar_b8_sm_benchmark.py](run_solar_b8_sm_benchmark.py)默认调用[核表SM运行器](run_solar_b8_nuclear_benchmark.py)，`--legacy-kn`才回到历史KN。核表SM运行器保存同核素同质量KN对照、通道分解和独立网格收敛；必须指定新输出目录。[build_solar_b8_onboarding_v3_1.py](build_solar_b8_onboarding_v3_1.py)从结果/同一证据链生成v3.1，`--check`只读。v3.0生成器接管后只核对冻结历史。[build_pandax_nuclear_teaching.py](build_pandax_nuclear_teaching.py)生成全部11份独立M-only教学代码；[validate_pandax_nuclear_teaching.py](validate_pandax_nuclear_teaching.py)在空目录单文件执行并核对来源/主结果。[validate_solar_b8_nuclear_rendering.mjs](validate_solar_b8_nuclear_rendering.mjs)检查新报告的数学、导航与布局。')
    managed(ROOT/'tests/README.md','## Solar核Response合同\n\n[test_solar_nuclear_response.py](test_solar_nuclear_response.py)验证真实表读取、p/n绝对收缩、共享逐能量API一致性、SM二次重组、同质量/原核数、端点与非法替代拒绝。')
    managed(ROOT/'data/responses/README.md','## 太阳⁸B SM的显式复用\n\nD0004选择本JSON及现有reader约定。[v3.1](../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md)记录七个Xe核素、全部通道和实际核系数；缺Xe124/Xe126，不重归一、不用KN补齐。外部原始作者/转换认证仍待核。')
    for name in ['outputs/README.md','outputs/solar_b8_sm/README.md']:
        p=ROOT/name;managed(p,'## 太阳⁸B：真实核Response SM\n\n'+link(p,OUT/'README.md','20261110_nuclear_response_run2')+'保存两实验实际核表预测、同范围KN对照、分量/收敛与来源。run1为端点检查触发的首次部分运行，保留不覆盖。')
    put(OUT/'README.md','# 太阳⁸B：真实原子核Response SM\n\n[当前onboarding](../../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md) · [核表全部数值/来源边界](NUCLEAR_INPUT_AUDIT.json) · [结果总表](RUN_SUMMARY.json) · [验证](VALIDATION.json)\n\n'+
        '\n'.join('- ['+d['dataset']+']('+d['dataset']+'/README.md)：'+fmt(d['result']['total_events'])+'事例；同范围KN '+fmt(d['result']['kn_control_total']) for d in datasets)+'\n\n固定SSM，无经验c_i。七核素绝对数权重；缺两核素与外部源认证限制保留。由标准Runtime实际运行；不声称论文拟合复现。\n')
    put(OUT/'README.md',EXPECTED[OUT/'README.md']+'\n[实际执行源码与哈希](source/README.md) · [文档图文验收](READABILITY_VALIDATION.json) · [预览](preview/README.md) · [独立教学代码核对](TEACHING_VALIDATION.json) · [文件归属与导航](FILE_LIFECYCLE.json)\n')
    existing=read(MANIFEST) if MANIFEST.is_file() else None
    protected=existing['preserved_history'] if existing else [
        {'file':rel(p),'sha256':sha(p)} for d in datasets for p in [d['docs']/n for n in ['experiment.physics.v3.0.md','experiment.physics.summary.v3.0.md','EXPERIMENT_USER_INPUT.v3.0.md']]+[d['base']/'experiment.input.yaml',d['base']/'experiment.resources.npz']]+[
        {'file':rel(SOURCE),'sha256':sha(SOURCE)}]
    for item in protected:
        if sha(ROOT/item['file'])!=item['sha256']:
            raise ValueError('protected historical artifact changed: '+item['file'])
    changed=[rel(p) for p,text in EXPECTED.items() if not p.is_file() or p.read_bytes()!=text.encode('utf8')]
    if args.check:
        print(json.dumps({'status':'PASS' if not changed else 'DIFF','mismatches':changed,'protected':len(protected)},ensure_ascii=False));raise SystemExit(bool(changed))
    for p,text in EXPECTED.items():
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8',newline='\n')
    manifest={'version':'3.1','date':'2026-11-10','current_combined':rel(CENTRAL),'managed_files':[rel(p) for p in EXPECTED],
        'preserved_history':protected,'results':[{'file':rel(OUT/d['dataset']/'RESULT.json'),'sha256':sha(OUT/d['dataset']/'RESULT.json')} for d in datasets]}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'WRITTEN','files':len(EXPECTED),'changed':len(changed)},ensure_ascii=False))


if __name__=='__main__':
    main()
