"""Generate/check the complete v3.4.1 report and its explicit mainline branch.

Old numerical runs, input cards, core Python and v3.4 source remain immutable.
--write updates only this deliverable plus the backed-up navigation/authority.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from extensions.solar_rho_snudd.protocol import CARD, PIN, read, save, sha
from tools.finalize_solar_b8_snudd import rel, link, put, table, section

OUT = ROOT / 'outputs/external/solar_rho_snudd/20261112_fig4_run2'
DOC = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
FILE = DOC / 'SNUDD_FULL_BENCHMARK.v3.4.1.md'
BRANCH = 'external_snudd_full_fig4'
MARKER = 'solar-snudd-v341'
RUNS = [('PandaX4T', 'PandaX4T_2024_US2', 15), ('XENONnT', 'XENONnT_2024_SolarB8', 14)]
CODE = ['extensions/solar_rho_snudd/scan.py', 'extensions/solar_rho_snudd/scan_source.py',
        'tools/run_solar_b8_snudd_inference.py', 'tools/finalize_solar_b8_snudd_inference.py',
        'tools/validate_solar_b8_snudd_inference.mjs', 'tests/test_solar_snudd_inference.py']


def managed(path, body):
    old = path.read_text(encoding='utf8')
    block = f'<!-- {MARKER}:start -->\n\n{body}\n\n<!-- {MARKER}:end -->'
    pattern = r'<!-- '+MARKER+r':start -->.*?<!-- '+MARKER+r':end -->'
    if re.search(pattern, old, re.S):
        new = re.sub(pattern, lambda _: block, old, flags=re.S)
    elif path == DOC / 'README.md':
        if '<!-- solar-nsi-v33:end -->' not in old:
            raise ValueError('frozen singlebin navigation block absent')
        new = old.replace('<!-- solar-nsi-v33:end -->', block+'\n\n<!-- solar-nsi-v33:end -->')
    else:
        new = old.rstrip()+'\n\n'+block+'\n'
    put(path, new)


def generated(qa):
    r = read(OUT / 'NSI_RESULTS.json')
    b = read(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json')
    c = read(CARD)
    compare = r['paper_comparison']
    best = r['primary_minimum']['minimum']
    ln = lambda p, label: link(FILE, p, label)
    headings = [('status', '结果与范围'), ('source', 'Source：通量、振荡和实际传播数据'),
        ('nuclear', 'Target与核振幅Response'), ('detector', 'Detector与单bin数据'),
        ('prediction', '事例数：各阶段实际计算'), ('statistics', 'Statistics：三个独立pull与联合最小值'),
        ('comparison', '与论文Fig.4的定量比较'), ('controls', '尾段和传播对照'),
        ('validation', '验收、主线入口与复算'), ('gaps', '仍未闭合的论文等价条件'), ('references', '标准文献与原件')]
    refs = b['references'] | {'R1': {'citation': 'LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026.',
        'url': 'https://arxiv.org/abs/2601.19883v2', 'locator': 'PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域'},
        **{'S_'+k: v for k, v in c['references'].items()}}
    def cite(*keys):
        return '\n\n'.join('['+key+'] '+refs[key]['citation']+' '+refs[key]['locator']+' '+
            ('[原始网址]('+refs[key]['url']+')。' if refs[key].get('url') else '') for key in keys)
    text = '# 太阳⁸B SNuDD完整统计与论文比较 v3.4.1（新版本）\n\n'
    text += '**2026-11-12。完整计算结果版：已计算三样本联合最小值、601×601二维面及90%区域。2601.19883v2 Fig.4绿色区域的精确复现未通过；科学接受NOT_REVIEWED。** 旧v3.4五点接入结果、v3.3本地传播、v3.2.1 SM、多bin与V/B−L均保留。\n\n'
    text += ' · '.join([ln(CARD, '固定来源/参数卡'), ln(OUT / 'NSI_RESULTS.json', '完整计算结果'), ln(OUT / 'README.md', '数值文件和图'), ln(DOC / 'SNUDD_EXTERNAL_ONBOARDING.v3.4.md', '旧v3.4接入读本')])
    text += '\n\n<a id="toc"></a>\n\n## 目录\n\n'+'\n'.join('- ['+name+'](#'+anchor+')' for anchor, name in headings)+'\n'
    text += section('status', headings[0][1], table(['量', '本次实际结果', '解释/依据'], [
        ['SM三信号[events]', ', '.join(f'{s:.6f}' for s in r['SM']['signal_events']), 'paired、US2、XENONnT；原核Response和Total接受度'],
        ['SM联合χ²', f"{r['SM']['chi2']:.10f}", '式(88)三个独立12%pull的解析profile'],
        ['联合χ²min', f"{best['chi2']:.10f}", f"声明的近似数学模型内全域搜索；(eu,ed)=({best['epsilon_ee_uV']:.8f},{best['epsilon_ee_dV']:.8f})"],
        ['SM的Δχ²', f"{r['SM']['chi2']-best['chi2']:.10f}", '小于4.61，SM在所用二维90%区域内；不据此宣称NSI发现'],
        ['论文图区域交并比', f"{compare['intersection_over_union']:.6%}", '只在[-1,1]²和601²网格比较；不是拟合优度或复现通过率'],
        ['核Response/探测器Response', '核W和原振幅计算；探测器使用单bin Total接受度', '本分支无Ne/S2迁移矩阵、无ci校准；不是多bin谱'],
    ])+'\n\n仅重新计算Fig.4的绿色太阳联合区域；橙色CONUS+与蓝色COHERENT本轮未重算，不列作本轮复现成果。'+cite('R1'))
    src = ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883'
    source = np.loadtxt(src / 'b8_source.txt')
    prod = np.loadtxt(ROOT / c['production_file']['path'])
    osc = c['oscillation_actual_GeV_rad']
    text += section('source', headings[1][1], r'''入射源是地球处所有活跃味的总⁸B通量，谱形与绝对强度分开：

$$
\frac{d\phi_{\rm total}}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu),\qquad
\frac{d\phi_\alpha}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu)\rho_{\alpha\alpha}(E_\nu;eu,ed).
$$

这是总通量和密度矩阵的定义；总通量不随NSI自由缩放。传播改变各味组成；本轮仍用固定5.46×10⁶。统计的12%先验只作用在式(88)的各样本信号项，不能冒称另取了一个标准太阳模型通量。
'''+'\n'+table(['输入', '实际数值/数组、单位', '数值文件与具体依据/核验范围'], [
        ['总通量', '5.46×10⁶ cm⁻²s⁻¹', ln(src / 'analysis.input.json', '只读基础卡')+'；[R5] p5 Eq.(29)，本项目沿用选择；未称为2601作者原始卡'],
        ['谱形', f'829×2；E=0–16.56 MeV；原网格积分={np.trapezoid(source[:,1],source[:,0]):.10g}；首/末(0,0)/(16.56,0)', ln(src / 'b8_source.txt', '原Bahcall表')+'；[R6]官网829行第1/2列；单位MeV、MeV⁻¹；保留原舍入，线性插值，不额外归一'],
        ['密度', 'log10(ne/NA)=2.36−4.52x−0.33exp[−(x/0.075)^1.1]；log10(nn/NA)=1.72−4.80x；mol/cm³', ln(ROOT / '.externals/SNuDD/snudd/nsi/solar_profiles.py', '实际函数')+'；[S_density]直接采用软件拟合；未独立认证原论文每个拟合系数'],
        ['产生位置', f'{list(prod.shape)}；x=r/Rsun，0–0.17；首/末(0,0)/(.17,0)；max={prod[:,1].max():.9g}', ln(ROOT / c['production_file']['path'], '96×2原表')+'；[S_production]表头指向1302.2791；软件线性插值，域外0，按dr归一、不加r²'],
        ['振荡前三项', f"θ12={osc['theta_12']}rad，θ13={osc['theta_13']}rad，Δm21²={osc['delta_m12']*1e18:.8g} eV²", ln(CARD, '实际显式传入值')+'；沿用v3.3固定PEANUTS示例的项目选择；'+ln(ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml', '固定示例原件')],
        ['其余参数', 'θ23=43.3°，δCP=212°，Δm31²=2.513×10⁻³ eV²', ln(ROOT / '.externals/SNuDD/snudd/nsi/oscillation.py', 'osc_params_best')+'；[S_remaining_oscillation]固定软件默认；Δ31用于适用性诊断，μτ分配不影响ee-only事例数'],
        ['传播数值源', '1000径向节点，其中485非零权重；144个正式E节点；完整rho可重建', ln(OUT / 'propagation_source/source.npz', '1000节点数值源')+' / '+ln(OUT / 'propagation_source/manifest.json', '原件hash/实际参数')+'；[S_software]完全相同求积，不用概率插值或缩减非零节点'],
    ])+r'''

传播采用SNuDD有效两味绝热模型并平均质量相位；输出为三维味密度矩阵，**不是完整三味微分方程演化**，不含地球再生。令eu=εee_uV、ed=εee_dV，εp=2eu+ed、εn=eu+2ed，则电子物质势为√2GF·ne[1+εp+(nn/ne)εn]；1是SM，ε只传新物理部分。映射依据[S_nsi_mapping]实际GeneralNSI的ξp、ξn。

扫描只把同一模型的ee-only代数式编译执行；不修改上游或Runtime：每个E、每个耦合点都在原1000点求积。完整ρ=U diag(c13²(1+〈cos2θm〉)/2,c13²(1−〈cos2θm〉)/2,s13²)U†。5个点的完整矩阵已与独立SNuDD进程核对，差异见验收。
'''+'\n\n'+cite('R5', 'R6', 'S_software', 'S_density', 'S_production', 'S_nsi_mapping', 'S_remaining_oscillation'))
    nuclear = read(ROOT / b['physics']['nuclear_resource'])['nuclei']
    nr = []
    for key in b['physics']['isotope_keys']:
        n = nuclear[key]
        m = n['responses']['M']
        nr.append([key, n['basic']['J'], f"{n['basic']['b']:.9g}", str([len(x) for row in m for x in row]),
                   ', '.join(f'{x[0]:.9g}' for row in m for x in row)])
    text += section('nuclear', headings[2][1], table(['输入', '实际值/处理', '直接来源与范围'], [
        ['Xe丰度/质量', '9×3：A=124–136、原子质量[u]、数丰度[1]；首行124,123.905892,.000952', ln(src / 'xe_isotopes.txt', '原9行表')+'；[R7] NIST官网；核数分母用全部9行，再选择7个可用核表'],
        ['靶核数与核质量', 'N_A×10⁶[g]/平均摩尔质量[g/mol]×原数丰度；截面核质量A·amu', ln(ROOT / 'cevns_pyeft/experiments/solar_singlebin.py', 'build_targets')+'；[R10]单位转换，原算法直接沿用'],
        ['核W与振幅', 'basis=(p,n)，y=(qb/2)²；W=e⁻²ʸΣa_k y^k；b单位GeV⁻¹', ln(ROOT / b['physics']['nuclear_resource'], '实际完整核表')+'；[R8]用户指定本地表及既有读取约定；外部作者表认证未闭合'],
        ['NSI匹配', 'C61q_NP=−√2GF·εee_qV [GeV⁻²]；SM也由原共享LEFT振幅计算', ln(ROOT / 'cevns_pyeft/theory/li2026/ee_vector_nsi.py', 'ElectronVectorNSI')+'；[R1] p22 Eq.(95)；不追加KN或自旋归一化因子'],
    ])+'\n\n实际M系数四个位置依次pp,pn,np,nn；系数长度代表shape=(2,2,对应长度)。其他原核通道仍由原振幅读取。\n\n'+table(['核素', 'J', 'b[GeV⁻¹]', 'M四多项式长度', 'a0(pp,pn,np,nn)'], nr)+
        '\n\n七核素原数丰度合计0.998158；未补Xe124/126、未重归一。这里认证本地数值存在、读取约定和本轮复用不变；不把格式名视为已认证外部作者来源。'+cite('R1', 'R7', 'R8', 'R10'))
    rows = []
    for name, config in b['samples'].items():
        a = np.loadtxt(src / config['efficiency'])
        rows.append([name, config['exposure_tyr'], str(config['T_bounds_keVnr']), str(list(a.shape)),
            f'{a[0,0]:.8g}–{a[-1,0]:.8g}；ε首/末={a[0,1]:.8g}/{a[-1,1]:.8g}',
            ln(src / config['efficiency'], '完整表')+'；'+config['source']])
    text += section('detector', headings[3][1], table(['样本', '曝光[t·yr]', 'T积分[keVnr]', '数组shape', '原表范围与代表值', '来源/数值'], rows)+
        '\n\nPandaX Total已含选区，只乘一次；本次不使用Qy映射、Ne/S2逐箱模板或ci。XENONnT第三列是图线可见性/核验标记，效率用第2列。三样本的单bin处理来自[R1] p20 Eq.(87)；具体T界沿用[R4] p13 Table II。paired采用[R2]官方1.20 t·yr，已明确与[R5]1.25的差别。\n\n**MISSING：XENONnT 2.7700000018–3 keVnr的原始接受度。** 主方案将末值0.12398752876529323延伸，是显式项目假设；zero/unit是0≤ε≤1界，profile_bounds另加尾段不确定区间，不称为论文原统计。\n\n'+cite('R1', 'R2', 'R3', 'R4'))
    text += section('prediction', headings[4][1], r'''物理顺序与workflow一致：Source传播 → Target核数 → 原子核Response与振幅 → 截面/运动学 → Total接受度 → 单bin积分 → Statistics。传播与散射使用同一组eu、ed。

$$
\frac{d\sigma_{\rm eff}}{dT}=\frac{d\sigma_{\rm SM}}{dT}
+P_{ee}(E;eu,ed)\left[\frac{d\sigma_e(eu,ed)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right],
$$

$$
S_k=\mathcal E_k\sum_A n_A^{(1\,\mathrm{tonne})}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k(T)
\int_{E_{\min}(T)}^{E_{\max}}dE\,t_{\rm yr}\Phi_{8B}f_{8B}(E)
\frac{d\sigma_{{\rm eff},A}}{dT}.
$$

第一式由ρ与diag(σe,σSM,σSM)的迹得到，只在当前实数ee-only子空间成立，μτ的SM事件仍保留。第二式是[R1] Eqs.(84),(87)按项目曝光单位展开；Ek单位t·yr，n_A^(1 tonne)是每吨该核素的核数，t_yr=31557600 s。各个质量/时间/效率只乘一次。
'''+'\n'+table(['步骤/阶段', '实际程序', '具体输入→输出'], [
        ['P03传播', ln(ROOT / 'extensions/solar_rho_snudd/export_rho.py', '独立SNuDD导出')+'；'+ln(ROOT / 'extensions/solar_rho_snudd/scan.py', '同源数值求积'), '同一密度/产生区/振荡/NSI→ρ(E)；不提供源强和核截面'],
        ['P02/P04/P05', ln(ROOT / 'cevns_pyeft/theory/li2026/ee_vector_nsi.py', '原核Response振幅')+'；'+ln(ROOT / 'cevns_pyeft/experiments/solar_singlebin.py', '原Target'), '原核W、匹配Wilson、运动学→cm²/keV；天然Xe核数'],
        ['P06/P07', ln(ROOT / 'cevns_pyeft/experiments/solar_nsi.py', '原NSIExecutor'), '原源强、ρ和截面→逐T密度→Total效率→3个events/bin'],
        ['P08', ln(ROOT / 'cevns_pyeft/kernels/solar_nsi.py', '原保留E轴的核'), 'K[7核素,known/tail,6单项式,144E]；原801个T网格并入效率节点'],
        ['P09', ln(ROOT / 'cevns_pyeft/statistics/solar_nsi.py', '原三pull联合统计')+'；'+ln(ROOT / 'tools/run_solar_b8_snudd_inference.py', '本轮完整扫描入口'), '逐耦合点重算Pee、收缩K、profile、联合最小化、601²面'],
    ])+'\n\n本轮使用标准load_snudd→PreparedExperiment→predict/evaluate核验扫描。旧v3.4核只在rebind_state验证每个不依赖传播的折叠输入hash一致后复用，保存新的物理身份；实际values逐位不变。'+cite('R1'))
    statsrows = []
    for i, sample in enumerate(r['sample_order']):
        statsrows.append([sample, r['statistical_data']['D'][i], f"{r['statistical_data']['sigma_stat'][i]:.7g}", '.12',
            f"{r['SM']['signal_events'][i]:.9f}", f"{r['SM']['chi2_by_sample'][i]:.9f}", f"{best['signal_events'][i]:.9f}"])
    text += section('statistics', headings[5][1], table(['样本', '实验拟合信号D[events]', 'σstat[events]', 'σα', 'SM信号[events]', 'SM χ²k', '最佳点未移位信号[events]'], statsrows)+
        '\n\nD来自[R2] p2摘要和[R3] p5 Table I的实验信号拟合值；不是原始选中候选计数。σ由[R1] p20 Eq.(88)紧随文字的37.1%、37.3%、36.9%分别乘D推导；三个独立12%pull，按论文简化统计执行，不改成共用一次通量pull。实际数组见'+ln(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json', '统计卡')+r'''

$$
\chi^2=\min_{\alpha_1,\alpha_2,\alpha_3}\sum_k
\left\{\frac{[D_k-(1+\alpha_k)S_k]^2}{\sigma_k^2}+\frac{\alpha_k^2}{0.12^2}\right\}
=\sum_k\frac{(D_k-S_k)^2}{\sigma_k^2+0.12^2S_k^2},
$$

$$
\alpha_k^*=\frac{0.12^2 S_k(D_k-S_k)}{\sigma_k^2+0.12^2S_k^2},\qquad
\Delta\chi^2(eu,ed)=\chi^2(eu,ed)-\min_{eu,ed}\chi^2.
$$

这里右侧是对式(88)独立高斯pull的解析极小化推导，并用独立三变量最小二乘核对。二维90%区域按[R1] p22给定Δχ²≤4.61；本轮未另做覆盖率toy校准。不把很小的SM与最小值差异解读为新物理显著性。
'''+'\n\n各最佳pull='+', '.join(f'{x:.9g}' for x in best['alpha'])+f"。联合χ²min={best['chi2']:.12f}；3个独立DE种子加121²包围域网格多起点，DE结果spread={r['primary_minimum']['independent_seed_spread']:.3g}。"+
        f"图内601²最低χ²={r['plot_window_grid_minimum']['chi2']:.9g}；主面实际减的是全域数学模型的{best['chi2']:.9g}，未减SM或图内最小值。"+
        '\n\nUS2正定电子截面二次型与Pee下界给出包含所有可能最小值/90%点的有限椭圆；搜索在其包围方形内，见'+ln(OUT / 'MINIMUMS.json', '系数、搜索边界和每次优化记录')+'。有限包围域有解析依据，域内多起点收敛是数值检查；不是对任意近似有效性的证明。\n\n'+ln(OUT / 'solar_snudd_signal_comparison.png', '三样本信号/误差图')+'\n\n'+cite('R1', 'R2', 'R3'))
    bounds = next(x for x in read(OUT / 'SLICE_BOUNDARIES.json') if x['epsilon_ee_uV'] == 0)
    text += section('comparison', headings[6][1], '!['+'实际计算与论文边界'+']('+link_path(FILE, OUT / 'solar_Fig4_snudd_vs_paper.png')+')\n\n绿色填充/绿边为本次计算；灰色虚线为论文绿色区域边界，黑十字为SM，红点为(0,.178)。灰线仅验收参考，不参与前向计算、最小化或校准。\n\n'+table(['比较项', '本轮SNuDD计算', '论文原图/依据'], [
        ['eu=0时ed边界', ', '.join(f'{v:.7f}' for v in bounds['flat_sensitivity']), ', '.join(f'{v:.7f}' for v in bounds['paper_green_reference'])],
        ['(0,.178)', f"Δχ²={compare['counterexample']['delta_chi2']:.9f}<4.61，允许", '两块绿色多边形均不含此点，排除'],
        ['[-1,1]²允许面积占比', f"{compare['calculated_allowed_fraction']:.6%}", f"{compare['paper_allowed_fraction']:.6%}；601²网格估计"],
        ['区域交并比IoU', f"{compare['intersection_over_union']:.6%}", 'intersection/union；不能当作统计p值'],
        ['接入前本地B16的IoU', f"{compare['previous_local_B16_IoU']:.6%}", '同一论文原生参考、同样比较框；只用于传播方案对照'],
    ])+'\n\n**结果：整体沿对角线延伸的相关带结构一致，但论文中间的窄禁区未被本计算复现；不能写“Fig.4精确复现成功”。** 换用SNuDD传播没有消除差异。尾段、传播固定与各自最小值的对照已保存；本轮未通过改通量、改味定义、加ci或拟合图线来对齐论文。\n\n论文参考是p23 PDF的386/342顶点两块完整绿色填充路径，已重新从原生PDF逐点核对，坐标差0；不受橙/蓝遮挡影响。原件hash与方法在'+ln(OUT / 'source_evidence/PAPER_VECTOR_VALIDATION.json', '原图独立核验')+'，完整边界在'+ln(OUT / 'source_evidence/paper_fig4_green_reference.json', '参考多边形')+'。其数字化精度不等于作者提供了原始χ²网格。\n\n'+cite('R1'))
    ctlrows = []
    minimums = read(OUT / 'MINIMUMS.json')
    for mode, result in minimums.items():
        p = result['minimum']
        ctlrows.append([mode, f"{p['chi2']:.10f}", f"({p['epsilon_ee_uV']:.6f},{p['epsilon_ee_dV']:.6f})", ', '.join(f'{v:.7f}' for v in bounds[mode])])
    text += section('controls', headings[7][1], table(['方案（各减自己联合最小值）', 'χ²min', '(eu,ed)min', 'eu=0的ed边界'], ctlrows)+
        '\n\nflat_sensitivity为主方案末值延伸；zero/unit为未知尾段效率取0/1；profile_bounds在逐点信号上下界内自由选择最有利信号，是额外未知尾处理；fixed_SM_propagation只改变散射、把传播固定在SM，用于诊断，未取代主模型。\n\n![]('+link_path(FILE, OUT / 'solar_snudd_controls.png')+')\n\n所有对照源于同一原核/统计输入及已声明的尾段选择。不是将几条不同假设下的轮廓合并为一个置信区域。原实验尾段缺失依据见Detector；统计依据仍为[R1] Eq.(88)。')
    direct = r['direct_Runtime_validation']
    slow = direct[-1]['new_slow_checks']
    commands = '''```powershell
# 工作目录：Gitup01；新输出目录，旧结果禁止覆盖。
# 使用已配置的主项目Python；外部导出由独立.venvs/snudd解释器执行。
.venvs/snudd/Scripts/python.exe -B -m extensions.solar_rho_snudd.scan_source --output outputs/external/solar_rho_snudd/NEW_RUN/propagation_source
python -B tools/run_solar_b8_snudd_inference.py --output outputs/external/solar_rho_snudd/NEW_RUN --grid 601
# 本次冻结run的验收及同源文档检查：
python -B -m pytest tests/test_solar_snudd_inference.py tests/test_solar_snudd.py tests/test_solar_nsi.py tests/test_solar_singlebin.py
python -B tools/finalize_solar_b8_snudd_inference.py --check
node tools/validate_solar_b8_snudd_inference.mjs
```'''
    text += section('validation', headings[8][1], table(['检查', '实际结果/证据'], [
        ['直接完整ρ核对', f"5点×144E×3×3；max差={max(x['full_rho_max_abs_difference'] for x in direct):.4g}；"+ln(OUT / 'DIRECT_RUNTIME_VALIDATION.json', '完整记录')],
        ['主线predict/evaluate', f"5点×3样本；事例差最大{max(x['signal_max_abs_difference'] for x in direct):.4g}；联合χ²差最大{max(x['chi2_abs_difference'] for x in direct):.4g}"],
        ['新最佳点Slow/Fast', '; '.join(x['sample']+': |ΔS|='+f"{x['absolute_difference']:.5g}" for x in slow)+' events；容差max(3e−4,0.2%)'],
        ['既有v3.4前向对照', '9个Slow/Fast点及US2的1201×216加密已冻结，本轮只读引用；'+ln(ROOT / 'outputs/external/solar_rho_snudd/20261112_run1/FORWARD_VALIDATION.json', '原记录')],
        ['本轮测试', str(qa['tests_passed'])+'项通过；'+ln(OUT / 'tests.xml', '实际JUnit记录')],
        ['保护', str(qa['protected_files'])+'份原core/data/旧SNuDD源码与结果hash不变；'+ln(OUT / 'QA.json', '本轮验收')],
        ['默认包/注册', '主进程无snudd import；不改默认实验Catalog，不改根依赖；独立显式入口'],
    ])+'\n\n图和表由同一结果JSON/数组生成；'+ln(OUT / 'solar_NSI_surfaces.npz', '实际601²原χ²/Δχ²/信号面')+'、'+ln(OUT / 'SLICE_BOUNDARIES.json', '各切线根')+'可独立重算核对。主线两实验的SNUDD_FIG4_BRANCH.json及P09/P10报告引用本轮结果，不覆盖旧版本报告。\n\n'+commands)
    diagnostic_rows = []
    for label, point in [('SM', (0., 0.)), ('差异点', (0., .178)), ('数学模型最佳点', (best['epsilon_ee_uV'], best['epsilon_ee_dV']))]:
        packet = next(p for p in r['source_packets'] if p['identity']['epsilon_hex'] == [float(x).hex() for x in point])
        diag = packet['adiabatic_diagnostic']
        diagnostic_rows.append([label, f"{diag['minimum_gamma']:.8g}", f"{diag['max_abs_2EV_over_dm31']:.8g}", '4001个径向点；独立两能级有限差分'])
    text += section('gaps', headings[9][1], table(['未闭合项', '本次如何处理', '仍受限的声明'], [
        ['2601作者完整数值卡/原χ²面', '用逐项有来源的项目选择；论文多边形只作参考', '不能确定中间禁区差异唯一来自传播、核表或其他数值约定；需原作者输入/中间量逐项对照'],
        ['大NSI的两味有效近似', '远处最小值给出所声明数学模型下的数值；各ρ包保存γ和2EV/Δ31诊断', '不能把γ大等同完整三味有效；全域数学最小值不等于已认证大耦合物理拟合'],
        ['XENONnT尾段接受度', '明确末值假设＋0/1界及额外profile', '精确论文前向折叠仍缺该原数据；不能说SNuDD补出了探测器数据'],
        ['核响应外部原件', '按用户选择直接复用既有数值/读取约定，七核表公开在本地', '外部作者表/转换认证未闭合；不影响本地重复运行，限制论文同源认证'],
    ])+'\n\n'+table(['点', '最小绝热γ', '最大&#124;2EV/Δm31²&#124;', '核验'], diagnostic_rows)+
        '\n\nγ大仅检查绝热性；2EV/Δ31不小时仍不能保证真空θ13的两味约化。最终能力交接：三样本事例数、SM点χ²、声明近似模型下完整NSI统计与对照均已算出；技术验证与科学接受分开。精确Fig.4复现状态保持未成立。无需等待另一份现成响应矩阵才能重复本次单bin结果。')
    text += section('references', headings[10][1], cite(*refs.keys())+'\n\n全部实际来源文件和hash见固定输入卡、旧来源台账与本轮SOURCE_FINGERPRINTS/DELIVERY_FILES。软件原件直接网址由snudd.input.json的direct_url给出；“软件已核”与“原论文→软件数值已认证”分开保留。')
    return {FILE: text}


def link_path(origin, target):
    import os
    return os.path.relpath(target, origin.parent).replace('\\', '/')


def audit():
    baseline = read(OUT / 'PROTECTED_BASELINE.json')
    changed = [p for p, h in baseline.items() if sha(ROOT / p) != h]
    if changed:
        raise ValueError('protected originals changed: '+str(changed))
    r = read(OUT / 'NSI_RESULTS.json')
    if r['runner_sha256'] != sha(ROOT / 'tools/run_solar_b8_snudd_inference.py') or r['source_card_sha256'] != sha(CARD) or r['host_imported_snudd']:
        raise ValueError('executed code/source/isolation identity changed')
    for p, h in read(OUT / 'SOURCE_FINGERPRINTS.json').items():
        if sha(ROOT / p) != h:
            raise ValueError('executed implementation changed: '+p)
    cases = list(ET.parse(OUT / 'tests.xml').getroot().iter('testcase'))
    if not cases or any(any(t.find(k) is not None for k in ['failure', 'error', 'skipped']) for t in cases):
        raise ValueError('tests not all passed')
    from extensions.solar_rho_snudd.experiment import load_snudd
    from cevns_pyeft.experiments.runtime import validate_snapshot
    from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
    shared, models = None, {}
    for sample in r['sample_order']:
        e = load_snudd(sample, cache_root=OUT / 'validation_cache', interaction=shared)
        shared = e.model.interaction
        validate_snapshot(e)
        saved = read(OUT / sample / 'PREPARED_MODEL.json')
        if saved['physics_fingerprint'] != e.physics_fingerprint or saved['analysis_fingerprint'] != e.analysis_fingerprint:
            raise ValueError('prepared model changed: '+sample)
        k = SolarNSIKernel.load(OUT / 'kernels' / (sample+'.npz'))
        k.validate(e, k.record['numerics'], e.executor.default_point())
        models[sample] = {'physics': e.physics_fingerprint, 'analysis': e.analysis_fingerprint}
    reference = read(OUT / 'source_evidence/PAPER_VECTOR_VALIDATION.json')
    if not reference['verified'] or reference['pdf_sha256'] != sha(ROOT / 'docs/references/General_CEvNS/2601.19883v2.pdf'):
        raise ValueError('paper native vector verification stale')
    return {'date': '2026-11-12', 'machine_status': 'PASS', 'status': r['status'], 'protected_files': len(baseline),
        'protected_changed': changed, 'tests_passed': len(cases), 'current_models': models,
        'scientific_acceptance': 'NOT_REVIEWED', 'exact_paper_reproduction': 'NOT_ESTABLISHED',
        'primary_joint_chi2_minimum': r['primary_minimum']['minimum']['chi2'], 'actual_grid_shape': [601, 601],
        'source_card_sha256': sha(CARD), 'default_catalog_changed': False, 'core_changed': False,
        'full_legacy_regression': 'not rerun; shared core unchanged; previously recorded YAML OS access issue not counted as PASS'}


def register(qa):
    records = {}
    for family, dataset, expected in RUNS:
        run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        progress = run / '00_MIGRATION_PROGRESS.md'
        old = progress.read_text(encoding='utf8')
        p = json.loads(re.search(r'```json\s*\n(.*?)\n```', old, re.S)[1])
        if BRANCH not in p.get('parallel_analyses', {}) and p['revision'] != expected:
            raise ValueError('canonical revision changed; reload')
        auth = read(run / 'AUTHORIZATION_LOG.yaml')
        if not any(x.get('authorization_id') == 'W0008' for x in auth['entries']):
            auth['entries'].append({'authorization_id': 'W0008', 'date': '2026-11-12', 'status': 'ACTIVE', 'approval_kind': 'explicit_user_instruction',
                'user_quote': '具体把接入后，整个流程计算，最后的结果给出；最后统计分析跟要求复现的论文对比',
                'scope': 'same SNuDD source physical definition; complete joint inference, paper comparison and mainline report',
                'write_plan': rel(OUT / 'WRITE_PLAN.json'), 'recovery_plan': 'backup/solar-snudd-inference-20261112-01/MANIFEST.json',
                'scientific_result_acceptance_separate': True})
            save(run / 'AUTHORIZATION_LOG.yaml', auth)
        decisions = read(run / 'P04_DECISION_LOG.yaml')
        if not any(x.get('decision_id') == 'D0008' for x in decisions['entries']):
            decisions['entries'].append({'decision_id': 'D0008', 'date': '2026-11-12', 'user_quote': '最后统计分析跟要求复现的论文对比',
                'scope': 'complete requested statistical calculation without replacing the frozen source/target/statistics model',
                'interpretation': 'same1000-node SNuDD ee specialization; full-plane mathematical model minima;601-square2D90%green comparison',
                'execution_authorized': True, 'result_acceptance': 'NOT_REVIEWED', 'exact_paper_reproduction': 'NOT_ESTABLISHED'})
            save(run / 'P04_DECISION_LOG.yaml', decisions)
        branch = {'analysis_id': BRANCH, 'parent_analysis': 'solar_ee_vector_nsi', 'parent_source': 'external_solar_rho_snudd',
            'version': '3.4.1', 'date': '2026-11-12', 'status': qa['status'], 'machine': 'PASS', 'human': 'NOT_REVIEWED',
            'write_ref': 'W0008', 'decision_ref': 'D0008', 'report': rel(FILE), 'results': rel(OUT / 'NSI_RESULTS.json'),
            'entry': 'tools/run_solar_b8_snudd_inference.py', 'source_card_sha256': sha(CARD), 'qa': rel(OUT / 'QA.json'),
            'exact_paper_reproduction': 'NOT_ESTABLISHED', 'default_global_activation': False}
        reports = {}
        for phase in ['P09', 'P10']:
            f = run / 'phases' / (phase+'_snudd_full_inference.md')
            result = {'schema_version': 1, 'phase': phase, 'capability_id': 'solar_b8.external_snudd_full_fig4.'+phase.lower(),
                'workspace': 'canonical', 'plan_status': 'READY', 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED',
                'scope_ref': rel(OUT / 'WRITE_PLAN.json'), 'input_refs': [rel(CARD), rel(OUT / 'SOURCE_FINGERPRINTS.json')],
                'input_fingerprint': sha(CARD), 'evidence_refs': [rel(OUT / 'QA.json'), rel(OUT / 'DIRECT_RUNTIME_VALIDATION.json')],
                'decision_refs': ['D0008'], 'approval_refs': [],
                'artifacts': [{'path': rel(OUT / 'NSI_RESULTS.json'), 'sha256': sha(OUT / 'NSI_RESULTS.json'), 'role': 'complete approximate-model joint inference'}],
                'checks': [{'name': 'joint inference and actual Runtime consistency', 'status': 'PASS',
                    'command': 'python -B tools/run_solar_b8_snudd_inference.py', 'result_ref': rel(OUT / 'DIRECT_RUNTIME_VALIDATION.json')}],
                'handoff': {}}
            if phase == 'P09':
                result['handoff'] = {'channels': [{'id': s, 'representation': 'binned_counts', 'processing': 'other', 'design': 'joint',
                    'likelihood': 'gaussian', 'requires_covariance': False, 'meaning': 'experimental fitted signal yield, not raw counts'}
                    for s in ['PandaX_paired', 'PandaX_US2', 'XENONnT']],
                    'prediction_binding': rel(OUT / 'DIRECT_RUNTIME_VALIDATION.json'),
                    'required_inputs': {'available': True, 'sources': ['data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json'], 'missing': []},
                    'nuisance_model': 'Eq88 three independent sigma=.12 Gaussian pulls; analytic profile',
                    'inference': 'each treatment own jointly minimized2Dchi2; threshold4.61; whole plane within declared two-flavor model',
                    'claim_level': 'approximate', 'benchmark': '2601.19883v2Fig4 green native vector comparison; exact agreement NOT established',
                    'limitations': ['last-value X-tail is an explicit assumption; raw experimental tail remains missing', 'large-NSI two-flavor validity not certified']}
            else:
                result['handoff'] = {'delivery_scope': {'mode': 'capability_change', 'target': 'complete external SNuDD statistical calculation and paper comparison', 'completion': 'partial'},
                    'capability_matrix': [
                        {'id': 'approximate_model_full_statistics', 'requested': True, 'required_for_claim': True, 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(OUT / 'NSI_RESULTS.json')},
                        {'id': 'exact_paper_green_reproduction', 'requested': True, 'required_for_claim': True, 'machine_gate': 'BLOCKED', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(OUT / 'PAPER_COMPARISON.json')}],
                    'validation_levels': {'internal_numerics': 'PASS', 'Runtime_statistics': 'PASS', 'paper_comparison_computed': True, 'exact_paper_reproduction': 'NOT_ESTABLISHED'},
                    'runtime_integration': 'explicit load_snudd and independent source representation; unchanged core/default catalog',
                    'final_claim': 'complete calculated approximate-model region and quantitative comparison; no exact reproduction claim',
                    'limitations': ['unknown X tail', 'two-flavor approximation', 'external nuclear authorship not certified', 'paper exact input card unavailable']}
            import jsonschema
            jsonschema.Draft202012Validator(read(ROOT / 'workflows/_shared/schemas/phase-result.schema.yaml')).validate(result)
            put(f, '# '+phase+'：SNuDD完整联合统计与论文比较\n\n'+link(f, FILE, '逐项来源与最终计算报告')+' · '+link(f, OUT / 'QA.json', '实际验收')+' · '+link(f, OUT / 'NSI_RESULTS.json', '完整结果')+
                '\n\n同源数值求积、全域联合优化、601²面、独立三pull与原生论文图比较均已完成。技术PASS；精确论文复现未成立，结果接受NOT_REVIEWED。不覆盖旧分支或授予人工科学Gate。\n\n```json phase-result\n'+json.dumps(result, ensure_ascii=False, indent=2)+'\n```\n')
            reports[phase] = rel(f)
        branch['phase_reports'] = reports
        save(run / 'SNUDD_FIG4_BRANCH.json', branch)
        source_branch = read(run / 'SNUDD_SOURCE_BRANCH.json')
        source_branch['full_inference_extension'] = rel(run / 'SNUDD_FIG4_BRANCH.json')
        source_branch['capability']['new_full_Fig4'] = 'COMPUTED; EXACT_PAPER_REPRODUCTION_NOT_ESTABLISHED'
        save(run / 'SNUDD_SOURCE_BRANCH.json', source_branch)
        manifest = read(run / '00_IMPLEMENTATION_MANIFEST.yaml')
        manifest.setdefault('extensions', {})[BRANCH] = branch
        manifest['extensions']['external_solar_rho_snudd'] = source_branch
        save(run / '00_IMPLEMENTATION_MANIFEST.yaml', manifest)
        if BRANCH not in p.get('parallel_analyses', {}):
            p['previous_revision'], p['revision'] = p['revision'], p['revision']+1
        p.setdefault('parallel_analyses', {})[BRANCH] = branch
        p['parallel_analyses']['external_solar_rho_snudd'] = source_branch
        p['current_analysis'] = 'solar_ee_vector_nsi'
        p['current_source_variant'] = 'external_solar_rho_snudd'
        p['current_statistical_variant'] = BRANCH
        p['updated_at'] = '2026-11-12'
        p['checkpoint'] = {'phase_id': 'P10', 'phase_name': 'full SNuDD inference scientific review', 'skill': 'cevns-experiment',
            'step_id': 'phase.P10.human_review', 'next_action': 'review computed region, paper discrepancy, two-flavor validity and unknown X tail', 'resume_requires': []}
        p['authorization_refs'].update(snudd_full_scope='D0008', snudd_full_write='W0008')
        p['artifact_refs'].update(snudd_full_branch=rel(run / 'SNUDD_FIG4_BRANCH.json'), snudd_full_report=rel(FILE))
        p['gates'][BRANCH] = {'machine': 'PASS', 'human': 'NOT_REVIEWED', 'report_ref': reports['P10'], 'decision_refs': ['D0008']}
        current = progress.read_text(encoding='utf8')
        if current != old:
            raise ValueError('concurrent canonical index change')
        put(progress, '# 主线进度：'+dataset+'\n\nSNuDD完整太阳联合统计已计算并与论文Fig.4比较；精确复现未成立，科学接受NOT_REVIEWED。旧分支保留。\n\n```json\n'+json.dumps(p, ensure_ascii=False, indent=2)+'\n```\n')
        managed(run / 'README.md', '## SNuDD完整统计 v3.4.1\n\n'+link(run / 'README.md', FILE, '完整流程、结果和论文比较')+' · '+link(run / 'README.md', run / 'SNUDD_FIG4_BRANCH.json', '主线统计分支')+'。三样本联合区域已算；原文精确复现未通过。')
        records[family] = {'revision': p['revision'], 'reports': reports}
    return records


def navigation():
    owners = ['README.md', 'tools/README.md', 'tests/README.md', 'extensions/README.md', 'extensions/solar_rho_snudd/README.md',
        'outputs/README.md', 'outputs/external/README.md', 'outputs/external/solar_rho_snudd/README.md',
        'docs/experiments/README.md', 'docs/experiments/LATEST_EXPERIMENTS.md', 'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md', rel(DOC / 'README.md')]
    for name in owners:
        p = ROOT / name
        body = '## 太阳完整统计：SNuDD v3.4.1\n\n'+link(p, FILE, '三样本全流程、联合区域和论文比较')+' · '+link(p, OUT / 'README.md', '实际结果、图与验收')+'。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。'
        if name == 'extensions/solar_rho_snudd/README.md':
            body += '\n\n'+link(p, ROOT / CODE[1], 'scan_source.py')+'导出原1000节点数值输入；'+link(p, ROOT / CODE[0], 'scan.py')+'计算相同ee-only代数求积，完整ρ逐点验证；不新增SNuDD导入或概率插值。'
        if name == 'tools/README.md':
            body += '\n\n'+' · '.join(link(p, ROOT / f, Path(f).name) for f in CODE if f.startswith('tools/'))
        if name == 'tests/README.md':
            body += '\n\n'+link(p, ROOT / CODE[-1], '完整推断测试')+'核对完整矩阵、Runtime/联合统计、独立pull、各方案最小值、601²面和实际边界。'
        managed(p, body)
    p = OUT / 'README.md'
    entries = [('NSI_RESULTS.json', '三样本、SM、全域最佳、全部对照及科学边界'), ('MINIMUMS.json', '每方案DE多种子与独立网格多起点搜索'),
        ('solar_NSI_surfaces.npz', '601²原χ²、Δχ²、known/tail信号和参考mask'), ('SLICE_BOUNDARIES.json', '实际4.61根与论文多边形交点'),
        ('PAPER_COMPARISON.json', '区域IoU/差异反例，论文只作验收参考'), ('DIRECT_RUNTIME_VALIDATION.json', '5点完整ρ+15次predict/evaluate+新最佳点3个Slow对照'),
        ('propagation_source/', '固定原1000径向节点的等价数值输入与来源hash'), ('validation_cache/', '实际完整ρ包，按能量/参数内容寻址'),
        ('kernels/', '验证原折叠hash后绑定新PreparedExperiment的3个核'), ('source_evidence/', '原论文绿色矢量路径和独立核对'),
        ('source/', '实际运行及交付源码快照'), ('SOURCE_FINGERPRINTS.json', '执行源码指纹'), ('DELIVERY_FILES.json', '本轮代码/报告/结果指纹'),
        ('PROTECTED_BASELINE.json', '472项保护原件hash'), ('WRITE_PLAN.json', '本轮范围与用户原话'), ('FILE_LIFECYCLE.json', 'README与消费者对应'),
        ('QA.json', '技术验收、科学/精确复现状态分开'), ('tests.xml', '实际测试记录'), ('READABILITY_VALIDATION.json', '目录/公式/图/窄屏实际渲染'),
        ('preview/README.md', '本轮渲染与截图')]
    put(p, '# SNuDD完整太阳联合统计：20261112_fig4_run2\n\n'+link(p, FILE, 'v3.4.1完整物理/来源/统计报告')+' · '+link(p, CARD, '固定实际来源卡')+'\n\n'
        '**完整三样本NSI统计已算出，精确论文复现未通过。** 单bin、核Response、原通量/Total效率，旧数据与结果只读。\n\n![实际区域与论文](solar_Fig4_snudd_vs_paper.png)\n\n'+
        table(['文件', '作用'], [(link(p, OUT / name, name), meaning) for name, meaning in entries])+
        '\n\n[尾段/传播对照](solar_snudd_controls.png) · [三样本信号与实验拟合误差](solar_snudd_signal_comparison.png)\n')
    descriptions = {'propagation_source': 'source.npz含原1000节点输入；manifest.json绑定固定软件、来源卡、原件和导出器hash。跳过严格零权重，不做概率插值。',
        'validation_cache': '每个内容hash子目录含实际SNuDD完整rho.npz与manifest.json。用于完整矩阵/Runtime核对，不替代实验数据。',
        'kernels': '三样本独立物理指纹；每份折叠values与旧v3.4逐位相同；合法rebind_state已核对全部fold输入hash。',
        'source_evidence': 'paper_fig4_green_reference.json为原生PDF两块绿色填充路径，PAPER_VECTOR_VALIDATION.json重新逐点验证。只用于结果对比。',
        'source': '执行代码和交付生成器按原相对路径保存；运行hash见SOURCE_FINGERPRINTS.json，完整交付hash见DELIVERY_FILES.json。'}
    for directory, body in descriptions.items():
        p = OUT / directory / 'README.md'
        put(p, '# '+directory+'\n\n'+body+'\n\n'+link(p, OUT / 'README.md', '返回结果')+'\n')
    for sample in ['PandaX_paired', 'PandaX_US2', 'XENONnT']:
        p = OUT / sample / 'README.md'
        put(p, '# '+sample+'\n\n[PREPARED_MODEL.json](PREPARED_MODEL.json)保存本轮实际指纹和所有依赖；事件数与联合统计见'+link(p, OUT / 'NSI_RESULTS.json', '完整结果')+'。\n')
    return owners


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    qa = audit()
    if args.write:
        save(OUT / 'QA.json', qa)
        for p, text in generated(qa).items():
            put(p, text)
        qa['canonical'] = register(qa)
        owners = navigation()
        save(OUT / 'QA.json', qa)
        mapping = {name: [rel(FILE)] for name in owners}
        mapping['extensions/solar_rho_snudd/README.md'] += CODE[:2]
        mapping['tools/README.md'] += CODE[2:5]
        mapping['tests/README.md'] += CODE[5:]
        mapping[rel(OUT / 'README.md')] = [rel(p) for p in OUT.iterdir() if p.name != 'README.md']
        for family, dataset, _ in RUNS:
            run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
            mapping[rel(run / 'README.md')] = [rel(run / 'SNUDD_FIG4_BRANCH.json')]+list(qa['canonical'][family]['reports'].values())
        save(OUT / 'FILE_LIFECYCLE.json', {'file_owners': mapping, 'backup': 'backup/solar-snudd-inference-20261112-01/MANIFEST.json',
            'default_global_registration': False, 'core_or_data_changed': False, 'git_commit_push': False})
        delivery = {}
        targets = [ROOT / p for p in CODE]+[FILE]
        targets += [OUT / name for name in ['NSI_RESULTS.json', 'MINIMUMS.json', 'solar_NSI_surfaces.npz', 'SLICE_BOUNDARIES.json', 'PAPER_COMPARISON.json']]
        for p in targets:
            delivery[rel(p)] = sha(p)
            if p.suffix in ['.py', '.mjs']:
                dest = OUT / 'source' / p.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and sha(dest) != sha(p):
                    raise ValueError('executed/delivery snapshot changed: '+rel(p))
                if not dest.exists():
                    shutil.copy2(p, dest)
        save(OUT / 'DELIVERY_FILES.json', delivery)
    else:
        for p, text in generated(qa).items():
            if p.read_text(encoding='utf8') != text:
                raise ValueError('stale generated report: '+rel(p))
        for p, h in read(OUT / 'DELIVERY_FILES.json').items():
            if sha(ROOT / p) != h:
                raise ValueError('delivery changed: '+p)
        for family, dataset, _ in RUNS:
            path = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
            p = json.loads(re.search(r'```json\s*\n(.*?)\n```', (path / '00_MIGRATION_PROGRESS.md').read_text(encoding='utf8'), re.S)[1])
            if p['current_statistical_variant'] != BRANCH or BRANCH not in p['parallel_analyses']:
                raise ValueError('canonical full inference branch missing')
    print(json.dumps({'status': qa['machine_status'], 'tests': qa['tests_passed'], 'protected': qa['protected_files'],
        'exact_paper_reproduction': qa['exact_paper_reproduction'], 'mode': 'write' if args.write else 'check'}))


if __name__ == '__main__':
    main()
