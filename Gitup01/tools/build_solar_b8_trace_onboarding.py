"""Document-first full-rho/Tr(rho K) contract; never change physical runtime.

Read existing pinned rho packets and source cards. Preserve old reports/results,
back up navigation/authority before writing, and distinguish requested equations
from the implementation that is actually present. --check is read-only.
"""
from pathlib import Path
import argparse
import ast
import json
import re
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from extensions.solar_rho_snudd.protocol import CARD, PIN, read, save, sha, load_packet
from tools.finalize_solar_b8_snudd import rel, link, put, table, section

DOC = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
FILE = DOC / 'SNUDD_FULL_TRACE_ONBOARDING.v3.5.md'
CONTRACT = DOC / 'SNUDD_FULL_TRACE_CONTRACT.v3.5.json'
OUT = ROOT / 'outputs/external/solar_rho_snudd/20261112_trace_onboarding'
OLD = ROOT / 'outputs/external/solar_rho_snudd/20261112_fig4_run2'
BRANCH = 'snudd_full_rho_trace_contract'
MARKER = 'solar-full-rho-trace-onboarding-v35'
RUNS = [('PandaX4T', 'PandaX4T_2024_US2', 16), ('XENONnT', 'XENONnT_2024_SolarB8', 15)]
OWNERS = ['README.md', 'tools/README.md', 'extensions/solar_rho_snudd/README.md',
    'outputs/external/solar_rho_snudd/README.md', 'docs/experiments/README.md', 'docs/experiments/LATEST_EXPERIMENTS.md',
    'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md', rel(DOC / 'README.md')]


def line_of(file, name):
    tree = ast.parse((ROOT / file).read_text(encoding='utf8'))
    return next(n.lineno for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def rho_evidence():
    result = read(OLD / 'NSI_RESULTS.json')
    best = result['primary_minimum']['minimum']
    points = [('SM', 0., 0.), ('Fig4_difference_point', 0., .178),
              ('previous_mathematical_minimum', best['epsilon_ee_uV'], best['epsilon_ee_dV'])]
    rows = []
    manifests = list((OLD / 'validation_cache').glob('*/manifest.json'))
    for label, u, d in points:
        candidates = []
        for path in manifests:
            m = read(path)
            if m['input_identity']['epsilon_hex'] == [float(u).hex(), float(d).hex()]:
                energy, rho, verified = load_packet(path.parent, m['input_identity'])
                if np.any(energy == 10.):
                    candidates.append((len(energy), path, energy, rho, verified))
        if not candidates:
            raise ValueError('existing direct full-rho packet missing: '+label)
        _, path, energy, rho, m = max(candidates, key=lambda item: item[0])
        matrix = rho[np.flatnonzero(energy == 10.)[0]]
        rows.append({'label': label, 'epsilon_ee_uV': u, 'epsilon_ee_dV': d,
            'manifest': rel(path), 'manifest_sha256': sha(path), 'npz': rel(path.parent / 'rho.npz'),
            'rho_npz_sha256': sha(path.parent / 'rho.npz'), 'shape': list(rho.shape),
            'E_MeV_range': [float(energy.min()), float(energy.max())], 'flavor_order': ['e', 'mu', 'tau'],
            'rho10MeV_real': matrix.real.tolist(), 'rho10MeV_imag': matrix.imag.tolist(),
            'verified_packet_checks': m['physical_checks'], 'role': 'existing direct SNuDD output, no recomputation or projection'})
    return rows


def implementation_evidence():
    entries = [
        ('extensions/solar_rho_snudd/state.py', '__call__', 'CURRENT: builds diag(Pee,(1-Pee)/2,(1-Pee)/2); must pass raw full rho instead'),
        ('cevns_pyeft/theory/li2026/ee_vector_nsi.py', 'dsigma_dT', 'CURRENT: scalar SM+rho_ee correction; must call full flavor-kernel trace'),
        ('cevns_pyeft/rates/differential.py', 'differential_flavor_kernel_nn', 'AVAILABLE: returns actual incoming-flavor3x3 K, cm2/keV, before state contraction'),
        ('cevns_pyeft/theory/li2026/flavor.py', 'contract_density_kernel_grid', 'AVAILABLE: validated einsum(...ab,...ba), actual Tr(rho K)'),
        ('cevns_pyeft/kernels/solar_nsi.py', 'blocks', 'CURRENT: stores scalar ee coefficients and consumes Pee; new matrix representation required'),
        ('cevns_pyeft/kernels/solar_nsi.py', 'predict', 'CURRENT: calls state_model.pee; full-rho matrix contraction required'),
        ('cevns_pyeft/statistics/solar_nsi.py', 'blocks', 'CURRENT: joint scan uses scalar Pee; must bind the same full-rho trace evaluator'),
        ('extensions/solar_rho_snudd/scan.py', 'rho', 'AVAILABLE: same upstream quadrature reconstructs full rho; not currently used by joint-rate blocks'),
    ]
    return [{'file': f, 'symbol': name, 'line': line_of(f, name), 'sha256': sha(ROOT / f), 'actual_status': status}
            for f, name, status in entries]


def contract(rhos, implementation):
    base = read(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json')
    return {'schema': 'solar_full_rho_trace_onboarding/1', 'version': '3.5', 'date': '2026-11-12',
        'status': 'ONBOARDING_UPDATED; RUNTIME_FULL_TRACE_PENDING',
        'user_method': '散射端需要改用trace(rho K)', 'this_round': '先修改onboarding，给出截面与事例数积分；不修改运行物理代码或重算结果',
        'parent_source_card': rel(CARD), 'source_card_sha256': sha(CARD), 'software_commit': PIN,
        'base_input_card': 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json',
        'base_input_card_sha256': sha(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json'),
        'state': {'basis': 'flavor', 'order': ['e', 'mu', 'tau'], 'phase_convention': 'pinned SNuDD.UPMNS',
            'shape': ['N_E', 3, 3], 'dtype': 'complex128', 'unit': '1', 'required': 'native complete rho; no flavor dephasing or mu/tau redistribution'},
        'kernel': {'definition': 'K_A(E,T)=d boldsigma_A/dT in incoming flavor space; outgoing flavor summed',
            'basis': 'same flavor basis and phases as rho', 'shape': ['N_E', 3, 3], 'unit': 'cm2/keV',
            'state_contraction': 'sum_ab rho_ab K_ba = trace(rho @ K)', 'current_shared_api': 'cevns_pyeft.rates.differential.differential_flavor_kernel_nn',
            'solar_runtime_binding': 'NOT_IMPLEMENTED', 'new_energy_resolved_matrix_kernel_arrays': 'NOT_GENERATED'},
        'fixed_inputs': {'flux_cm2_s': base['physics']['flux_cm2_s'], 'sin2thetaW': base['physics']['sin2thetaW'],
            'seconds_per_year': base['physics']['seconds_per_year'], 'isotope_keys': base['physics']['isotope_keys'],
            'samples': base['samples']},
        'forbidden_substitutions': ['diag(Pee,(1-Pee)/2,(1-Pee)/2)', 'rho_ee-only production contraction',
            'constant unit-trace representative state for NSI', 'scalar old kernel relabeled as full flavor kernel',
            'all-flavor NSI substituted for ee-only NSI', 'unrecorded phase-convention changes', 'flux or ci fitted to paper boundary'],
        'availability': {'native_rho_packets': 'AVAILABLE_VERIFIED', 'shared_K_API': 'AVAILABLE_INSPECTED',
            'shared_trace_API': 'AVAILABLE_INSPECTED', 'source_to_full_rho_binding': 'PENDING_IMPLEMENTATION',
            'full_trace_Slow': 'NOT_RUN', 'full_trace_Fast': 'NOT_RUN', 'full_trace_statistics': 'NOT_RUN',
            'rho_figures': 'NOT_GENERATED_THIS_DOCUMENT_FIRST_STEP'},
        'rho_input_evidence': rhos, 'implementation_evidence': implementation,
        'scientific_result_acceptance': 'NOT_REVIEWED',
        'existing_limits': ['two-flavor adiabatic solar source, not full3flavor ODE', 'X acceptance2.77-3keV missing; explicit primary last-value assumption',
            'seven locally selected Xe tables,124/126 omitted without renormalization; external source certification unresolved',
            'exact paper Fig4 equivalence not established'],
        'generalization_limit': 'current source mapping is real diagonal ee uV/dV only; off-diagonal/complex NSI needs separate propagation and phase-convention review'}


def generated(c):
    base = read(ROOT / c['base_input_card'])
    source = read(CARD)
    refs = base['references'] | {'R1': {'citation': 'LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026.',
        'url': 'https://arxiv.org/abs/2601.19883v2', 'locator': 'PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维4.61阈值；p23 Fig.4'},
        **{'S_'+k: v for k, v in source['references'].items()}}
    ln = lambda p, label: link(FILE, p, label)
    def cite(*keys):
        return '\n\n'.join('['+k+'] '+refs[k]['citation']+' '+refs[k]['locator']+' '+
            ('[原始网址]('+refs[k]['url']+')。' if refs[k].get('url') else '') for k in keys)
    headings = [('scope', '新要求、当前实现与版本'), ('source', '入射通量和完整rho'),
        ('cross-section', '核Response、微分截面和总截面'), ('events', '事例数：完整积分与单bin形式'),
        ('experiments', '哪些公式相同，哪些输入不同'), ('statistics', '统计与旧结果的关系'),
        ('implementation', '程序逐处对应和必须修改的内容'), ('handoff', '下一步验收与交接'), ('references', '标准文献与直接来源')]
    text = '# 太阳⁸B完整ρ与Tr(ρK) onboarding v3.5（新版本／实施前合同）\n\n'
    text += '**2026-11-12。按用户要求先更新onboarding：源端传完整SNuDD味密度矩阵，散射端实际计算Tr(ρK)。本轮只改文档、来源核对和主线待办；运行物理代码、事例数与统计结果尚未按新合同重算。** 旧v3.4/v3.4.1及其结果保留，不能把旧投影实现标成新版trace实现。\n\n'
    text += ' · '.join([ln(CONTRACT, '新版机器可读合同'), ln(CARD, '既有固定来源/参数卡'), ln(OUT / 'README.md', '输入与源码核对'), ln(DOC / 'SNUDD_FULL_BENCHMARK.v3.4.1.md', '旧统计报告')])
    text += '\n\n<a id="toc"></a>\n\n## 目录\n\n'+'\n'.join('- ['+title+'](#'+anchor+')' for anchor, title in headings)+'\n'
    text += section('scope', headings[0][1], table(['对象', '本版要求', '当前真实状态'], [
        ['Source', '完整复数ρ(E)，味顺序e,μ,τ；不重分配μ/τ，不删除非对角元', '原始完整NPZ已存在；当前state.__call__仍返回等价对角投影，待改'],
        ['散射', '先从原核Response/振幅构造3×3 K，再实际Tr(ρK)', '共享K/trace API已存在；太阳专用dsigma分支仍使用Pee简式，待接入'],
        ['事例数与Fast', '保留E轴及K的两个味指标；每个参数点用完整ρ收缩', '当前太阳Fast和联合扫描都是标量Pee表示；新版矩阵核尚未生成'],
        ['统计', '沿用2601式(88)，前向信号改由新版trace得到', '旧601²面仍属旧实现；本轮没有重命名或重算'],
        ['范围', 'PandaX paired、US2和XENONnT的2601单bin；实数ee-only uV/dV', 'SM、多bin、V/B−L各自保留；不自动扩大到非对角NSI'],
    ])+'\n\n方法选择来自用户原话“散射端需要改用trace(rho K)”；本轮顺序来自“你先把onboarding修改了”“总的截面积分公式也给一下”“截面，事例数公式”。这是明确的方法要求，不把程序待实现包装成已完成。')
    src = ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883'
    rows = []
    for row in c['rho_input_evidence']:
        rows.append([row['label'], f"({row['epsilon_ee_uV']:.8g},{row['epsilon_ee_dV']:.8g})", str(row['shape']),
            f"{row['E_MeV_range'][0]:.9g}–{row['E_MeV_range'][1]:.9g}", ln(ROOT / row['npz'], '原始rho.npz')])
    text += section('source', headings[1][1], r'''定义Φ8B为地球处所有活跃味合计的总通量，f8B为谱形；ρ为每个能量的单位迹密度矩阵，不包含通量或曝光：

$$
\frac{d\phi_{\rm tot}}{dE}=\Phi_{8B}f_{8B}(E),\qquad
F(E)=\frac{d\phi_{\rm tot}}{dE}\,\rho(E),\qquad
\rho=\rho^\dagger,\quad\operatorname{Tr}\rho=1,\quad\rho\succeq0.
$$

F是通量矩阵，单位cm⁻²s⁻¹MeV⁻¹；ρ单位1，shape=(N_E,3,3)。本版后续公式采用“总通量×单位迹ρ”的写法；若改用F，公式中不能再乘一次总通量。
'''+'\n'+table(['输入', '实际数值/数组', '数值位置、具体出处与核验范围'], [
        ['总通量/谱形', 'Φ=5.46×10⁶ cm⁻²s⁻¹；829×2，E=0–16.56MeV，f单位MeV⁻¹，原网格积分0.999986544', ln(src / 'b8_source.txt', 'Bahcall原表')+'；[R5]p5 Eq.(29)总通量；[R6]官网第1/2列；保留原舍入与线性插值，不任意改通量'],
        ['振荡值', 'θ12=.583638rad、θ13=.149575rad、Δm21²=7.42×10⁻⁵eV²；θ23=43.3°、δ=212°、Δm31²=2.513×10⁻³eV²', ln(CARD, '实际输入卡')+'；前三项为沿用v3.3固定PEANUTS示例的项目选择：'+ln(ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml', '实际示例Neutrinos字段')+'；其余[S_remaining_oscillation]固定软件默认'],
        ['电子/中子密度', 'log10(ne/NA)=2.36−4.52x−.33exp[−(x/.075)^1.1]；log10(nn/NA)=1.72−4.80x；mol/cm³', ln(ROOT / '.externals/SNuDD/snudd/nsi/solar_profiles.py', '实际解析函数')+'；[S_density]直接采用固定软件拟合，原论文系数认证单列'],
        ['产生区/求积', '原96×2表，x=0–.17Rsun；软件在0–.35的1000节点按dr求积归一、线性插值、域外0', ln(ROOT / source['production_file']['path'], '原产生区数据')+'；[S_production]表头原文；不乘r²'],
        ['实际ρ', '下表；均为独立SNuDD进程输出的完整复矩阵，包含非零非对角元', ln(OUT / 'RHO_INPUT_AUDIT.json', '逐包身份、哈希和10MeV矩阵')+'；[S_software]density_mass→density；没有新生成矩阵'],
    ])+'\n\n'+table(['点', '(eu,ed)', 'shape', 'E范围[MeV]', '原始数值'], rows)+r'''

传播仍为SNuDD有效两味绝热模型、产生区平均及质量相位平均，再用UρmassU†转换成完整味矩阵；不含地球再生，不是完整三味ODE。质量相位平均并不意味着味基底的非对角元必须为零。

**基底/相位：** ρ采用固定SNuDD.UPMNS的味相位约定。当前实数对角ee NSI的K对味重定相不变；若以后加入非对角耦合，ρ、Wilson矩阵及K须一起转换。不能只按另一个PMNS约定修改ρ非对角元的符号；本版未批准该扩展。
'''+'\n\n'+cite('R5', 'R6', 'S_software', 'S_density', 'S_production', 'S_remaining_oscillation'))
    text += section('cross-section', headings[2][1], r'''先区分三个对象：核响应 $W_X^{NN'}(q)$ 作用在核子p/n空间；$K_A(E,T)$ 是求和出射中微子味、包含核振幅和截面相空间因子的**入射味空间3×3微分截面矩阵**；探测器迁移/接受度作用在真实反冲T与实验读数x之间。三者不是同一个Response。

设A标识同位素，α、β标识入射味，f为出射味。K由共享核振幅构造，其结构为：

$$
[K_A(E,T)]_{\alpha\beta}
=\mathcal P_A(E,T)\sum_f
\overline{\mathcal M_{f\alpha}^*(E,T)\mathcal M_{f\beta}(E,T)},
\qquad K_A=K_A^\dagger\succeq0.
$$

横线代表既有振幅约定中的核自旋平均/求和，P代表其相空间和单位因子；不在此额外加自旋或KN因子。实际Li2026核心的截面步骤对其振幅核乘m_A/(8πE²)及GeV⁻²→cm²，再将cm²/GeV换为cm²/keV；由cross_section.py和rates/differential.py拥有归一化。

**微分截面：**

$$
\frac{d\sigma_A}{dT}(E,T;\rho,\epsilon)
=\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)]
=\sum_{\alpha,\beta}\rho_{\alpha\beta}(E;\epsilon)
[K_A(E,T;\epsilon)]_{\beta\alpha}.
$$

K和dσ/dT单位cm²/keV；ρ无量纲。矩阵指标必须反向相乘，不能用同位置元素乘积代替迹。展开后是Σα ρααKαα+2ReΣα<β ραβKβα，实部和虚部干涉都由迹保留。

**固定入射能量E的物理总截面：**

$$
\sigma_A(E;\rho,\epsilon)=
\int_0^{T_{\max,A}(E)}dT\,
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

此量单位cm²，不含探测器效率、靶核数、曝光或源通量。若需要某实验的“选中有效截面”，应另外标注：

$$
\sigma^{\rm sel}_{k,A}(E)=
\int_0^{T_{\max,A}(E)}dT\,a_k(T)\,
\operatorname{Tr}[\rho(E)K_A(E,T)].
$$

这里k是实验样本，a_k是完整选择概率；它不是微观核截面的一部分。

**所有实验共用的弹性运动学：**

$$
T_{\max,A}(E)=\frac{2E^2}{m_A+2E},\qquad
E_{\min,A}(T)=\frac{T+\sqrt{T^2+2m_AT}}{2}.
$$

这两式内部的E、T、m_A必须使用相同能量单位。实际程序入口E使用MeV、T使用keV，进入核心后统一为GeV；不能直接把不同单位的数值代入上式。

当前ee-only实数矢量NSI仍按[R1]p22 Eq.(95)设置C61q_NP=−√2GF·εee_qV·diag(1,0,0)，再加完整SM。若算得K为对角且Kμμ=Kττ，这是当前Wilson模型产生的结果；程序依然传完整ρ并实际计算矩阵迹，不以这个性质为理由改写Source或跳过迹。
'''+'\n'+table(['截面所需输入', '实际数值/约定', '出处与实现位置'], [
        ['核W', 'Xe128/129/130/131/132/134/136；basis p,n；W=e⁻²ʸΣa_k y^k，y=(qb/2)²', ln(ROOT / 'data/responses/responses_all.json', '既有完整数值核表')+'；[R8]用户选用本地表，外部作者原表认证未闭合；读取[nuclear.response]'],
        ['Xe丰度/质量', '9×3，A124–136；七核表按原数丰度，合计.998158，不重归一；核质量A·amu', ln(src / 'xe_isotopes.txt', 'NIST九行')+'；[R7]；核数分母仍用九行平均摩尔质量'],
        ['SM点/NSI', 'sin²θW=.23857；NP只有ee,uV/dV；单位GeV⁻²', ln(src / 'analysis.input.json', '原物理卡')+'；[R9]明确项目选择；[R1]Eq.(95)；'+ln(ROOT / 'cevns_pyeft/theory/li2026/ee_vector_nsi.py', 'nsi_point/Wilson映射')],
        ['完整K函数', '已存在，输出E.shape+(3,3)，complex128，cm²/keV；太阳专用接入待改', ln(ROOT / 'cevns_pyeft/rates/differential.py', 'differential_flavor_kernel_nn，第225行')+'；'+ln(ROOT / 'cevns_pyeft/theory/li2026/cross_section.py', '截面相空间/单位定义')],
        ['迹函数', '已存在，einsum(...ab,...ba)，验证ρ与K；不是论文数值表', ln(ROOT / 'cevns_pyeft/theory/li2026/flavor.py', 'contract_density_kernel_grid，第281行')],
    ])+'\n\n迹公式是密度矩阵散射概率的定义；上面的总截面、选择截面由微分截面积分得到，属显式推导。核振幅采用[R1]框架与已有共享实现，不引用另一篇图线替代K。'+cite('R1', 'R7', 'R8', 'R9'))
    text += section('events', headings[3][1], r'''令k表示样本，$n_A$ 是靶中同位素A的核数，$t_k$ 是观测时间；先用最直观的固定靶核数形式表示。$P_{k,i}(T)$ 是反冲T进入实验第i箱并通过选择的概率：

$$
S_{k,i}=t_k\sum_A n_A
\int_0^{E_{\max}}dE\,\Phi_{8B}f_{8B}(E)
\int_0^{T_{\max,A}(E)}dT\,P_{k,i}(T)
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

这是**事例数**，单位events；与截面的区别是增加了源通量、靶核数、观测时间和选择概率。微观K、完整ρ及迹的形式不随探测器改变。

若探测器给出真实反冲到读数x的核R_k(x|T)，则：

$$
P_{k,i}(T)=\int_{x\in\mathrm{bin}_{k,i}}dx\,\mathcal R_k(x\mid T).
$$

若R已经包含效率/ROI，不能再乘一次同一效率。若R只是归一化为1的条件分辨函数，则需在所声明的位置单独乘效率。多bin方案用各自P_{k,i}；不能把单bin的总接受度反推为已取得逐箱迁移核。

**本次2601单bin方案：** 采用实验Total/combined接受度和已选定的真实T积分界，不再做一次Ne/S2选区转换：

$$
a_k(T)=\mathbf1_{[T_{\min,k},T_{\max,k}]}(T)\,\varepsilon_k^{\rm Total}(T).
$$

项目数据给的是曝光 $\mathcal E_k$ [tonne·yr]，不需要任意拆成质量和时间。定义 $n_A^{(1\mathrm t)}$ 为每吨该核素核数，$t_{\rm yr}=31557600$ s/yr，则上式写成实际计算形式：

$$
S_k=\mathcal E_k\sum_A n_A^{(1\mathrm t)}t_{\rm yr}\Phi_{8B}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k^{\rm Total}(T)
\int_{E_{\min,A}(T)}^{E_{\max}}dE\,f_{8B}(E)
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

若E_min超过E_max，该T点贡献为0。T单位keV、K单位cm²/keV，E单位MeV、f单位MeV⁻¹。用完整核素平均摩尔质量Mbar [g/mol]与数丰度η_A计算：

$$
n_A^{(1\mathrm t)}=\frac{10^6\,\mathrm{g}}{\overline M}\,N_{\rm Av}\eta_A,
\qquad \overline M=\sum_A\eta_A M_A.
$$

这些式子是[R1]Eqs.(84),(87)按本项目通量/单位/曝光约定展开。每吨核数、曝光和一年秒数各用一次；若另选已含曝光的积分通量，必须相应移除外面的同一时间/质量因子。
'''+'\n'+table(['输入/符号', '实际值或定义', '出处'], [
        ['Φ、f、ρ、K', '同上一、二节；K必须由完整矩阵接口返回', '各节逐项来源；K太阳新绑定仍PENDING'],
        ['n_A^(1t)', '九行NIST丰度质量构成Mbar，选择七核表；不补缺核表、不重归一', ln(src / 'xe_isotopes.txt', '实际九行数组')+'；[R7]；'+ln(ROOT / 'cevns_pyeft/experiments/solar_singlebin.py', 'build_targets原换算')],
        ['t_yr、N_Av', '31557600s/yr；6.02214076×10²³mol⁻¹', '[R10]Julian year项目单位约定及SI常数'],
        ['曝光/ε/T界', '下节三样本对照；具体数组、有效域和尾段假设分别保存', '[R2][R3]曝光与接受度；[R4]Table II积分界'],
    ])+'\n\n'+cite('R1', 'R2', 'R3', 'R4', 'R7', 'R10'))
    exp_rows = []
    for name, config in base['samples'].items():
        a = np.loadtxt(src / config['efficiency'])
        exp_rows.append([name, config['exposure_tyr'], str(config['T_bounds_keVnr']), str(list(a.shape)),
            f'{a[0,0]:.8g}–{a[-1,0]:.8g}；ε首/末={a[0,1]:.8g}/{a[-1,1]:.8g}', ln(src / config['efficiency'], '完整表')+'；'+config['source']])
    text += section('experiments', headings[4][1], table(['物理对象/公式', '本次是否共用', '具体差别在哪里'], [
        ['核振幅→K、dσ/dT=Tr(ρK)、σ=∫dT Tr(ρK)', 'PandaX与XENONnT相同', '相同Xe核素、同一Wilson点和核表时K相同；不因实验名另乘一个核截面修正'],
        ['太阳Φ、f及ρ(E)', '本次三样本相同', '都用同一地球处⁸B日间平均源；未模拟地点/时段相关地球再生，不能声称包含该差别'],
        ['弹性Emin/Tmax及每吨天然Xe核数', '相同定义与资源', '随核素质量A变化；本次不按实验换核素或重新归一丰度'],
        ['S=源×核数×时间×选择×Tr(ρK)双积分', '同一总公式', 'k下标的曝光、ε和T窗口不同，数值不能直接复用'],
        ['实验读数和迁移', '一般不同', 'paired依赖成对S1/S2选择，US2依赖无配对S2/电子选择，XENONnT有自身S2选择；本次均已折入各自Total/combined的单bin方案'],
        ['多bin与单bin', '同一个总概率积分框架，具体P不同', '多bin用P_k,i(T)，单bin用完整ROI接受度及指定T窗口；数据与流程继续隔开'],
        ['统计形式', '本次同用Eq.(88)独立pull', '实验D和σ不同；这不是对所有实验普适的likelihood规则'],
    ])+'\n\n更广泛地，其他实验也共用矩阵迹和源/靶/选择双积分的结构，但K随核素与相互作用变，ρ和通量随源及传播变，选择概率随探测器变。反中微子必须用对应的反中微子K和ρ；不能直接复用太阳中微子的数值。这些区别不能仅靠更换一个曝光常数处理。\n\n'+table(['样本', '曝光[t·yr]', 'T积分[keVnr]', '数组shape', '原表支撑与代表值', '数值及精确来源'], exp_rows)+
        '\n\nPandaX的两条Total来自[R2]p3 Fig.1，XENONnT的combined来自[R3]p4 Fig.1；积分界来自[R4]p13 Table II。paired采用官方1.20 t·yr，未采用[R5]表中的1.25。\n\n**仍缺的实验数据：XENONnT约2.7700000018–3keVnr接受度。** 旧主方案末点0.12398752876529323恒值延伸只是显式项目假设，zero/unit是0≤ε≤1界；保留这些方案，不能在修改trace时静默填补、调归一或改通量。PandaX两份Total覆盖本次积分界。\n\n'+cite('R2', 'R3', 'R4', 'R5'))
    yields = read(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json')
    text += section('statistics', headings[5][1], r'''[R1]p20 Eq.(88)所用D是实验拟合信号量，不是原始候选事例数。每个样本有独立12%归一化pull：

$$
\chi^2(\epsilon)=\min_{\{\alpha_k\}}\sum_k\left[
\frac{(D_k-(1+\alpha_k)S_k(\epsilon))^2}{\sigma_k^2}
+\frac{\alpha_k^2}{0.12^2}\right]
=\sum_k\frac{(D_k-S_k(\epsilon))^2}{\sigma_k^2+0.12^2S_k(\epsilon)^2}.
$$

右侧为逐pull解析极小化推导。新版只要求把S换成完整trace前向结果，观测量、误差定义与统计结构不随本轮改变。二维阈值沿用论文p22的Δχ²≤4.61，减联合参数最小值。
'''+'\n'+table(['样本', 'D[events]', 'σ[events]', 'σα', '来源'], [[name, row['D'], f"{row['sigma_stat']:.7g}", row['pull_sigma'],
            '[R2]p2/[R3]p5 Table I的拟合信号；σ按[R1]p20的37.1%/37.3%/36.9%乘D'] for name, row in yields['samples'].items()])+
        '\n\n实际数组：'+ln(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json', '拟合信号/误差卡')+'。旧v3.4.1的SM信号、χ²和601²区域仍是旧执行记录；新矩阵接口完成且验证后，另存新版结果。当前不声称改文档便已重算，也不预设trace改写会消除论文禁区差异。'+cite('R1', 'R2', 'R3'))
    implementation_rows = [[ln(ROOT / row['file'], Path(row['file']).name), row['symbol']+'，第'+str(row['line'])+'行', row['actual_status']]
                           for row in c['implementation_evidence']]
    text += section('implementation', headings[6][1], table(['程序位置', '符号/位置', '已核实行为与必须改什么'], implementation_rows)+r'''

后续散射入口必须实际执行下面这个结构；这是现有共享API的调用说明，不宣称已替换生产入口：

```python
# Source: raw native flavor density, shape (N_E, 3, 3), no projection.
rho = source.full_rho(E_MeV, epsilon_ee_uV, epsilon_ee_dV)

# Theory/Response: actual K before selecting incoming flavor, cm^2/keV.
K = differential_flavor_kernel_nn(
    nuclear_response, T_keV, E_MeV,
    wc_triplets=point.wc_triplets,  # NP only; SM added once below
    include_sm=True, sin2thetaW=point.sin2thetaW,
).kernel_cm2_per_keV

# Cross section: all flavor entries are retained up to the contraction.
dsigma_dT = contract_density_kernel_grid(rho, K)
```

Source给Slow的IncidentStateBatch.rho须与原ρ包精确相同；Fast须保留K的两个味指标及E轴，收缩采用rho[...,a,b]K[...,b,a]，不能仍读Pee再把旧标量核称为完整矩阵核。若用精确系数分解加速，需展示各味矩阵系数及其与共享振幅的等价核验，并给独立缓存格式/指纹。

本轮只规定以上算法合同。共享函数已存在不等于太阳专用Runtime、Fast与联合统计已接好；不能只改报告中的公式而保留实际执行路径不变。
'''+'\n\n'+ln(OUT / 'IMPLEMENTATION_AUDIT.json', '源码SHA、精确行号与逐处状态')+'；'+ln(CONTRACT, '完整必改清单与禁用替代')+'。')
    text += section('handoff', headings[7][1], table(['交接项', '当前状态', '下一步具体验收'], [
        ['ρ来源/数值', 'AVAILABLE', '画原始完整矩阵实/虚部、对角元随E；核验trace=1、Hermitian、PSD及质量/味基底变换；不要画投影冒充ρ'],
        ['Source→Runtime', 'PENDING', '实际source.state_at的每个矩阵元与原SNuDD包一致，包括非对角元'],
        ['K→截面', '共享API AVAILABLE，太阳绑定PENDING', '按共享核Response生成K；核验Hermitian/PSD、能区、单位和实际Tr(ρK)，并与直接振幅比对'],
        ['矩阵指标', 'NOT_RUN', '加入复数非对角正定ρ和K的纯数学测试，抓出ρ_abK_ab、只取对角、丢虚部等错误；不因此扩大物理NSI范围'],
        ['单bin事件数', 'NOT_RUN', '三样本执行同一双积分，核对逐核素贡献、曝光/通量/Total只用一次；新旧结果另存比较'],
        ['Fast/联合统计', 'NOT_RUN', '新矩阵核与直接Slow逐点比对；统计只消费该同一trace前向；通过后另算/另存区域'],
        ['文献精确复现', '未成立', '保留两味近似、X尾段和核表外部原件认证边界；不靠归一化或味定义改动贴图'],
    ])+'\n\n当前待办是实现/接入未改，不是缺一份新的ρ数据。用户当前要求先更新本版onboarding；本轮没有修改物理代码、生成新K/ρ图或重算统计。已有数据来源、方法选择和待实现接口已集中在本版，不需要从旧版零散拼接。')
    text += section('references', headings[8][1], cite(*refs.keys())+'\n\n本版直接读取固定输入卡、原数值表和ρ包，逐文件hash在新版合同及输入审计中。标准引文、具体原文位置、软件/表格转录核验范围分别保留；不把程序字段名、文件存在或hash当成原论文真实性认证。')
    return text


def managed(path, body):
    old = path.read_text(encoding='utf8')
    block = f'<!-- {MARKER}:start -->\n\n{body}\n\n<!-- {MARKER}:end -->'
    pattern = r'<!-- '+MARKER+r':start -->.*?<!-- '+MARKER+r':end -->'
    if re.search(pattern, old, re.S):
        new = re.sub(pattern, lambda _: block, old, flags=re.S)
    elif path == DOC / 'README.md':
        if '<!-- solar-nsi-v33:end -->' not in old:
            raise ValueError('singlebin navigation boundary missing')
        new = old.replace('<!-- solar-nsi-v33:end -->', block+'\n\n<!-- solar-nsi-v33:end -->')
    else:
        new = old.rstrip()+'\n\n'+block+'\n'
    put(path, new)


def backup_and_baseline():
    if (OUT / 'PROTECTED_BASELINE.json').exists():
        return
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = read(OLD / 'PROTECTED_BASELINE.json') | read(OLD / 'DELIVERY_FILES.json')
    save(OUT / 'PROTECTED_BASELINE.json', baseline)
    paths = [ROOT / name for name in OWNERS]
    for family, dataset, _ in RUNS:
        run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        paths += [run / name for name in ['README.md', 'AUTHORIZATION_LOG.yaml', 'P04_DECISION_LOG.yaml', '00_IMPLEMENTATION_MANIFEST.yaml', '00_MIGRATION_PROGRESS.md']]
    number = 1
    while (ROOT / f'backup/solar-snudd-trace-onboarding-20261112-{number:02d}').exists():
        number += 1
    destination = ROOT / f'backup/solar-snudd-trace-onboarding-20261112-{number:02d}'
    hashes = {}
    for p in paths:
        dest = destination / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        hashes[rel(p)] = sha(p)
    save(destination / 'MANIFEST.json', {'date': '2026-11-12', 'purpose': 'document-first complete rho/trace onboarding', 'files': hashes})
    manifest = ROOT / 'backup/BACKUP_MANIFEST.md'
    with manifest.open('a', encoding='utf8') as f:
        f.write('\n2026-11-12：'+destination.name+'；完整ρ/Tr(ρK)新onboarding及主线待办；逐文件备份和hash见该MANIFEST。\n')
    save(OUT / 'WRITE_PLAN.json', {'date': '2026-11-12', 'user_quote': '散射端需要改用trace(rho K)；先把onboarding修改；给出截面和事例数公式、不同实验的共同与不同',
        'create': ['tools/build_solar_b8_trace_onboarding.py', 'tools/validate_solar_b8_trace_onboarding.mjs', rel(FILE), rel(CONTRACT), rel(OUT)+'/',
                   *[f'workflows/cevns-pyeft/runs/{f}/{d}/SNUDD_FULL_TRACE_BRANCH.json' for f, d, _ in RUNS]],
        'modify': [rel(p) for p in paths], 'backup': rel(destination / 'MANIFEST.json'),
        'not_changed': ['runtime physical code', 'data', 'pinned upstream', 'source card', 'old reports', 'old numerical results'],
        'status': 'documentation first; implementation remains pending'})


def register():
    records = {}
    for family, dataset, expected in RUNS:
        run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        progress = run / '00_MIGRATION_PROGRESS.md'
        old = progress.read_text(encoding='utf8')
        p = json.loads(re.search(r'```json\s*\n(.*?)\n```', old, re.S)[1])
        if BRANCH not in p.get('parallel_analyses', {}) and p['revision'] != expected:
            raise ValueError('canonical revision changed before documentation update')
        auth = read(run / 'AUTHORIZATION_LOG.yaml')
        if not any(e.get('authorization_id') == 'W0009' for e in auth['entries']):
            auth['entries'].append({'authorization_id': 'W0009', 'status': 'ACTIVE', 'date': '2026-11-12', 'approval_kind': 'explicit_user_instruction',
                'user_quote': '你先把onboarding修改了；总的截面积分公式也给一下；截面，事例数公式',
                'scope': 'document-first full-rho/trace requirement, universal cross-section/event equations, per-experiment inputs and actual implementation gap',
                'write_plan': rel(OUT / 'WRITE_PLAN.json'), 'runtime_changes_this_round': False, 'scientific_result_acceptance_separate': True})
            save(run / 'AUTHORIZATION_LOG.yaml', auth)
        decisions = read(run / 'P04_DECISION_LOG.yaml')
        if not any(e.get('decision_id') == 'D0009' for e in decisions['entries']):
            decisions['entries'].append({'decision_id': 'D0009', 'date': '2026-11-12', 'user_quote': '散射端需要改用trace(rho K)',
                'method_selection': 'USER_EXPLICITLY_REQUIRED', 'scope': 'native full SNuDD rho, actual incoming-flavor K and Tr(rho K) in Slow/Fast/joint forward',
                'supersedes': 'D0007 use of ee-equivalent projected state as current implementation target',
                'implementation_status': 'PENDING; current round onboarding only', 'result_acceptance': 'NOT_REVIEWED'})
            save(run / 'P04_DECISION_LOG.yaml', decisions)
        branch = {'analysis_id': BRANCH, 'version': '3.5', 'status': 'ONBOARDING_UPDATED_RUNTIME_PENDING',
            'write_ref': 'W0009', 'decision_ref': 'D0009', 'onboarding': rel(FILE), 'contract': rel(CONTRACT),
            'availability_audit': rel(OUT / 'RHO_INPUT_AUDIT.json'), 'implementation_audit': rel(OUT / 'IMPLEMENTATION_AUDIT.json'),
            'runtime_full_trace': 'NOT_IMPLEMENTED', 'full_trace_statistics': 'NOT_RUN', 'old_numerical_results_preserved': True, 'human_result_review': 'NOT_REVIEWED'}
        save(run / 'SNUDD_FULL_TRACE_BRANCH.json', branch)
        manifest = read(run / '00_IMPLEMENTATION_MANIFEST.yaml')
        manifest.setdefault('extensions', {})[BRANCH] = branch
        save(run / '00_IMPLEMENTATION_MANIFEST.yaml', manifest)
        if BRANCH not in p.get('parallel_analyses', {}):
            p['previous_revision'], p['revision'] = p['revision'], p['revision']+1
        p.setdefault('parallel_analyses', {})[BRANCH] = branch
        p['current_onboarding'] = rel(FILE)
        p['required_scattering_contraction'] = 'full_rho_trace_K'
        p['pending_implementation'] = BRANCH
        p['updated_at'] = '2026-11-12'
        p['checkpoint'] = {'phase_id': 'P07', 'phase_name': 'full rho trace implementation pending', 'skill': 'cevns-experiment',
            'step_id': 'phase.P07.implementation_pending', 'next_action': 'implement documented full-rho trace; then validate counts and statistics; current round is documentation first', 'resume_requires': []}
        p['authorization_refs'].update(full_trace_method='D0009', full_trace_onboarding_write='W0009')
        p['artifact_refs'].update(full_trace_onboarding=rel(FILE), full_trace_contract=rel(CONTRACT), full_trace_branch=rel(run / 'SNUDD_FULL_TRACE_BRANCH.json'))
        p['gates']['full_rho_trace'] = {'machine': 'NOT_RUN', 'human': 'NOT_REVIEWED', 'report_ref': rel(FILE), 'decision_refs': ['D0009']}
        if progress.read_text(encoding='utf8') != old:
            raise ValueError('concurrent progress update')
        put(progress, '# 主线进度：'+dataset+'\n\n已更新v3.5完整ρ与Tr(ρK) onboarding；新要求的运行实现和重算待做。旧结果保留，不将旧投影实现称为新版trace。\n\n```json\n'+json.dumps(p, ensure_ascii=False, indent=2)+'\n```\n')
        managed(run / 'README.md', '## 当前onboarding：完整ρ与Tr(ρK) v3.5\n\n'+link(run / 'README.md', FILE, '截面、总截面、事例数和实验差别')+' · '+link(run / 'README.md', run / 'SNUDD_FULL_TRACE_BRANCH.json', '方法变更与待实现状态')+'。本轮先文档；运行代码与统计尚未改写。')
        records[family] = {'revision': p['revision'], 'branch': rel(run / 'SNUDD_FULL_TRACE_BRANCH.json')}
    return records


def navigation():
    for name in OWNERS:
        p = ROOT / name
        body = '## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5\n\n'+link(p, FILE, '微分/总截面、事例数积分与三样本差别')+' · '+link(p, CONTRACT, '明确合同与待改程序')+'。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。'
        if name == 'tools/README.md':
            body += '\n\n'+link(p, ROOT / 'tools/build_solar_b8_trace_onboarding.py', '同源文档生成/检查')+'（--write或--check，只操作文档/来源审计/主线待办）；'+link(p, ROOT / 'tools/validate_solar_b8_trace_onboarding.mjs', '公式、目录和渲染校验')+'。'
        managed(p, body)
    p = OUT / 'README.md'
    put(p, '# 完整ρ与Tr(ρK)：onboarding先行更新\n\n'+link(p, FILE, '新v3.5读本')+' · '+link(p, CONTRACT, '新版合同')+'\n\n'
        '**只更新文档与来源/实施核对，未修改运行物理代码，也未生成新矩阵核、ρ图或统计。**\n\n'+table(['文件', '用途'], [
            ('[RHO_INPUT_AUDIT.json](RHO_INPUT_AUDIT.json)', '三个既有直接SNuDD完整ρ包、hash、shape、能域及10MeV代表矩阵'),
            ('[IMPLEMENTATION_AUDIT.json](IMPLEMENTATION_AUDIT.json)', '8个实际函数/方法的位置、源码hash、当前行为与待改项'),
            ('[WRITE_PLAN.json](WRITE_PLAN.json)', '用户要求、文档范围、备份和明确不改的物理对象'),
            ('[PROTECTED_BASELINE.json](PROTECTED_BASELINE.json)', '原core/data/源代码/旧数值与报告保护hash'),
            ('[QA.json](QA.json)', '本轮文档及来源一致性检查；不冒称物理运行验收'),
            ('[DELIVERY_FILES.json](DELIVERY_FILES.json)', '新文档、合同和生成器指纹'),
            ('[FILE_LIFECYCLE.json](FILE_LIFECYCLE.json)', '文件归属、README与当前主线导航'),
            ('[READABILITY_VALIDATION.json](READABILITY_VALIDATION.json)', '公式/目录跳转/本地链接/窄屏渲染，单独执行'),
            ('[preview/README.md](preview/README.md)', '实际渲染预览')])+'\n')


def audit(c):
    baseline = read(OUT / 'PROTECTED_BASELINE.json')
    changed = [p for p, h in baseline.items() if sha(ROOT / p) != h]
    if changed:
        raise ValueError('protected physical or old deliverable changed: '+str(changed))
    if c['rho_input_evidence'] != rho_evidence() or c['implementation_evidence'] != implementation_evidence():
        raise ValueError('documented input/implementation audit stale')
    return {'date': '2026-11-12', 'document_contract_check': 'PASS', 'protected_files': len(baseline), 'protected_changed': [],
        'rho_packets_read_and_validated': len(c['rho_input_evidence']), 'actual_functions_inspected': len(c['implementation_evidence']),
        'runtime_physics_modified': False, 'new_matrix_kernel_generated': False, 'full_trace_runtime_test': 'NOT_RUN',
        'rho_figures': 'NOT_GENERATED', 'statistics_recomputed': False, 'scientific_result_acceptance': 'NOT_REVIEWED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.write:
        backup_and_baseline()
        c = contract(rho_evidence(), implementation_evidence())
        save(CONTRACT, c)
        save(OUT / 'RHO_INPUT_AUDIT.json', c['rho_input_evidence'])
        save(OUT / 'IMPLEMENTATION_AUDIT.json', c['implementation_evidence'])
        put(FILE, generated(c))
        qa = audit(c)
        qa['canonical'] = register()
        navigation()
        save(OUT / 'QA.json', qa)
        mapping = {name: [rel(FILE), rel(CONTRACT)] for name in OWNERS}
        mapping['tools/README.md'] += ['tools/build_solar_b8_trace_onboarding.py', 'tools/validate_solar_b8_trace_onboarding.mjs']
        mapping[rel(OUT / 'README.md')] = [rel(p) for p in OUT.iterdir() if p.name != 'README.md']
        for family, dataset, _ in RUNS:
            path = f'workflows/cevns-pyeft/runs/{family}/{dataset}'
            mapping[path+'/README.md'] = [path+'/SNUDD_FULL_TRACE_BRANCH.json']
        save(OUT / 'FILE_LIFECYCLE.json', {'file_owners': mapping, 'backup': read(OUT / 'WRITE_PLAN.json')['backup'], 'runtime_or_data_modified': False})
        save(OUT / 'DELIVERY_FILES.json', {rel(p): sha(p) for p in [FILE, CONTRACT, Path(__file__), ROOT / 'tools/validate_solar_b8_trace_onboarding.mjs']})
    else:
        c = read(CONTRACT)
        qa = audit(c)
        if FILE.read_text(encoding='utf8') != generated(c):
            raise ValueError('onboarding is stale relative to generator and actual inputs')
        for p, h in read(OUT / 'DELIVERY_FILES.json').items():
            if sha(ROOT / p) != h:
                raise ValueError('new delivery changed: '+p)
        for family, dataset, _ in RUNS:
            path = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}/00_MIGRATION_PROGRESS.md'
            p = json.loads(re.search(r'```json\s*\n(.*?)\n```', path.read_text(encoding='utf8'), re.S)[1])
            if p['current_onboarding'] != rel(FILE) or p['required_scattering_contraction'] != 'full_rho_trace_K':
                raise ValueError('mainline document/method pointer not updated')
    print(json.dumps({'document_check': qa['document_contract_check'], 'protected': qa['protected_files'], 'runtime_trace': qa['full_trace_runtime_test'], 'statistics_recomputed': False}))


if __name__ == '__main__':
    main()
