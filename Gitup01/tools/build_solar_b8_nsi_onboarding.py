"""Generate/check the v3.3 NSI reader from the adopted cards and actual run.

This tool writes documentation only. It does not run or calibrate physics, alter
the frozen v3.2.1 reader, or certify the paper's unpublished implementation.
"""
from pathlib import Path
import argparse
import json
import os
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA = ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883'
BASE = ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883'
OUT = ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run2'
DOC = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
FILE = DOC / 'NSI_EE_VECTOR_ONBOARDING.v3.3.md'


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def link(origin, target, label):
    return '[' + label + '](<' + os.path.relpath(target, origin.parent).replace('\\', '/') + '>)'


def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n|' + '|'.join('---' for _ in headers) + '|\n' + ''.join(
        '| ' + ' | '.join(str(v).replace('|', '&#124;') for v in row) + ' |\n' for row in rows)


def section(anchor, title, body):
    return f'\n<a id="{anchor}"></a>\n\n## {title}\n\n{body}\n\n[返回目录](#toc)\n'


def generated():
    from cevns_pyeft.nuclear.response import ResponseDB
    c, b = read(DATA / 'nsi.input.json'), read(BASE / 'analysis.input.json')
    r, comparison = read(OUT / 'NSI_RESULTS.json'), read(OUT / 'PAPER_COMPARISON.json')
    ln = lambda p, label: link(FILE, p, label)
    refs = {**b['references'], **c['references']}

    def cite(*keys):
        return '\n\n'.join('[' + k + '] ' + refs[k]['citation'] + ' ' + refs[k].get('locator', '') + '。' for k in keys)

    headings = [('scope', '本轮目标、版本与三条隔离流程'), ('source', 'Source：通量、密度与产生区'),
                ('state', 'Source：电子味存活概率'), ('target', 'Target与原子核Response'),
                ('interaction', 'Interaction：只改变电子味散射'), ('detector', 'Detector与Observable：三个单bin'),
                ('prediction', 'Prediction：Slow与保留能量轴的Fast'), ('statistics', 'Statistics：联合区域'),
                ('results', '实际结果、对照与论文差异'), ('code', 'Onboarding到程序及复算'),
                ('handoff', '核验范围和下一步'), ('references', '标准参考文献与原件')]
    text = '# 太阳⁸B电子味矢量NSI onboarding v3.3：主线计算与核对版（新版本）\n\n'
    text += '**2026-11-12。已在原 Gitup01 实现并完成三样本联合计算。** 本版集中给出实际数值、来源、代码和结果；旧SM v3.2.1、多bin v3.1和轻媒介子V/B−L版本保留。\n\n'
    text += '**能力结论：NSI区域已经算出；2601.19883v2 Fig.4绿色区域的精确复现尚未成立。** 传播采用明确的两味绝热近似，XENONnT尾段采用显式项目假设并做界；论文中间窄禁区与本计算不一致。科学接受仍为NOT_REVIEWED，不将数值通过升级为原文等价或终稿认证。\n\n'
    text += ' · '.join([ln(DATA / 'nsi.input.json', 'NSI来源与参数卡'), ln(BASE / 'analysis.input.json', '只读基础输入'),
                         ln(OUT / 'README.md', '实际结果与验收'), ln(ROOT / 'tools/run_solar_b8_nsi_benchmark.py', '主线运行入口')])
    text += '\n\n<a id="toc"></a>\n\n## 目录\n\n' + '\n'.join(f'- [{title}](#{anchor})' for anchor, title in headings) + '\n'
    text += section('scope', headings[0][1], table(['流程', '输入与模型', '程序/结果'], [
        ['旧多bin', '2411.11749v1；Ne/cS2、Qy、逐箱数据/背景及旧响应', ln(ROOT / 'tools/run_solar_b8_multibin_benchmark.py', 'multibin入口')],
        ['旧单bin SM v3.2.1', '固定SM、三份Total效率；原舍入误差1.3/28/3.95', ln(DOC / 'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md', '冻结读本')],
        ['本版单bin NSI v3.3', '实数ee-uV/dV；传播+散射；精确论文百分比误差；独立kernel', ln(DATA / 'README.md', 'NSI目录') + ' / ' + ln(OUT / 'README.md', '独立输出')],
    ]) + '\n\n只读复用旧单bin的谱形、同位素与Total表。NSI独立data、dataset/analysis身份、状态、相互作用、统计和缓存；不读取多bin的Qy、D_i、B_i、c_i，也不把V/B−L轻媒介子结果改名为接触NSI。新loader使用scoped Catalog，不改变全局默认实验列表。')

    spectrum = np.loadtxt(BASE / 'b8_source.txt')
    profile_rows = []
    for name in ['solar_b16_gs98_profile.txt', 'solar_b16_agss09_profile.txt']:
        a = np.loadtxt(DATA / name)
        profile_rows.append([name, str(list(a.shape)), '; '.join(f'{lo:.8g}–{hi:.8g}' for lo, hi in zip(a.min(0), a.max(0))),
                             ', '.join(f'{v:.8g}' for v in a[0]), ln(DATA / name, '完整数值')])
    text += section('source', headings[1][1], r'''总通量与谱形分开：$d\phi/dE_\nu=\Phi_{8B}f_{8B}(E_\nu)$；不因拟合、换核响应或开启NSI而重标定太阳通量。
''' + '\n' + table(['输入', '实际数值/数组、单位', '数值文件、出处与核验范围'], [
        ['总通量', '5.46×10⁶ cm⁻²s⁻¹；固定', ln(DATA / 'nsi.input.json', 'physics') + '；[propagation] p5 Eq.(29)。2601未重印作者输入卡，属明确项目选取'],
        ['谱形', f'829×2；E=0–16.56 MeV，f单位MeV⁻¹；原网格积分={np.trapezoid(spectrum[:,1],spectrum[:,0]):.10g}', ln(BASE / 'b8_source.txt', 'b8_source.txt') + '；[R6]官网原829行前两列；分段线性、表外0、保留原精度'],
        ['振荡参数', 'θ12=0.583638 rad；θ13=0.149575 rad；Δm²21=7.42×10⁻⁵ eV²', ln(ROOT / 'outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml', '固定PEANUTS示例 Neutrinos') + '；[peanuts]。明确项目选择，不冒称2601作者卡'],
        ['弱混合角', 'sin²θW=0.23857，单位1', ln(BASE / 'analysis.input.json', '基础物理卡') + '；[R9]既有项目SM点'],
        ['时间与常数', '31557600 s/yr；N_A=6.02214076×10²³ mol⁻¹', '[R10]单位约定；G_F、ℏc使用' + ln(ROOT / 'cevns_pyeft/foundation/constants.py', '共享常数')],
    ]) + '\n\nprofile列顺序：r/Rsun、ne/N_A [mol/cm³]、nn/N_A [mol/cm³]、⁸B产生区分布[任意整体归一]。\n\n' + table(['profile', 'shape', '逐列范围', '首行代表值', '文件'], profile_rows) + r'''

主计算B16-GS98；AGSS09仅作密度/产生区敏感性，总通量仍固定5.46×10⁶。PEANUTS原产生区表1000行，取列1/3/9，电子密度从log10转换；Magnus质量密度2000行，取半径严格相同的前1000行，无跨模型插值。原四表保留在NSI数据目录，逐文件SHA256见参数卡。

**中子密度是PROJECT_DERIVED**：$n_n/N_A=\rho_{\rm mass}-n_e/N_A$，采用中性物质和每重子1u近似。它不是论文直接发布的中子密度表。产生区按 $dr$ 积分归一；原表已是径向分布，不能额外乘 $r^2$。

PEANUTS固定commit `39ef11f6d10014822809da65fa60752ea21aabb6`。Magnus固定commit `7eb53ef0b3e960b3b10383fef99bfe0c9110cc8f`的质量密度是**明确采用的二手转录**。原作者结构表URL本轮返回403/HTML验证页，原47列文件与此转录的等价性未独立认证；没有将HTML当数据，也未执行下载的外部代码。
''' + '\n\n' + cite('propagation', 'R6', 'R9', 'R10', 'b16', 'peanuts', 'magnus'))

    text += section('state', headings[2][1], r'''太阳先产生电子味中微子，传播后只有 $P_{ee}$ 部分仍以电子味到达。开启电子味NSI时，不能继续采用SM的味等价代表态。

采用[propagation] PDF p10 Appendix B Eqs.(B4)–(B9)的**两味绝热近似**：$\theta_{13,m}=\theta_{13}$，忽略地球再生。实数ee-only矢量子空间给出：

$$
n_u=2n_e+n_n,\quad n_d=n_e+2n_n,\qquad
V_{ee}=\sqrt2G_F(n_e+n_u\epsilon_{ee}^{uV}+n_d\epsilon_{ee}^{dV}),
$$

$$
A=2E_\nu\cos^2\theta_{13}V_{ee},\qquad
\cos2\theta_{12,m}=\frac{\Delta m_{21}^2\cos2\theta_{12}-A}{\sqrt{(\Delta m_{21}^2\cos2\theta_{12}-A)^2+(\Delta m_{21}^2\sin2\theta_{12})^2}},
$$

$$
P_{ee}(E_\nu;\epsilon)=\sin^4\theta_{13}
+\frac{\cos^4\theta_{13}}2\left[1+\cos2\theta_{12}\int dr\,w_{8B}(r)\cos2\theta_{12,m}(E_\nu,r;\epsilon)\right],\quad\int dr\,w_{8B}=1.
$$

以上是原文B4–B9在ee-only子空间的代入；$\epsilon_D^q=-\cos^2\theta_{13}\epsilon_{ee}^{qV}/2$，$\epsilon_N=0$，u、d的势相加。密度与角度数值均见上一节实际文件，没有缺省的“真实Pee数组”。程序每个参数点重算Pee，不复用固定SM概率。
''' + '\n' + table(['数值函数', '实际取得与验证', '程序/结果'], [
        ['Pee(E;eu,ed)', '上述两味模型；能量MeV→eV，密度mol/cm³→自然单位；每径向面板8阶Gauss', ln(ROOT / 'cevns_pyeft/sources/solar_msw.py', 'SolarMSW.pee / radial_quadrature')],
        ['SM Pee(2,5,10,15MeV)', ', '.join(f'{p:.9f}' for p in r['SM']['Pee_at_2_5_10_15_MeV']), ln(OUT / 'NSI_RESULTS.json', '实际数值')],
        ['状态ρ(E)', 'diag(Pee,(1−Pee)/2,(1−Pee)/2)，shape=N_E×3×3；逐能量检查finite/PSD/trace=1', 'μ/τ相等分配仅在两味SM散射相同的ee-vector子空间观测等价，并非分别Pμ、Pτ的传播预测'],
        ['独立核验', '原生径向1000点积分、2×2 Hamiltonian本征向量、真空限与概率界；径向8→16阶', ln(ROOT / 'tests/test_solar_nsi.py', '测试') + ' / ' + ln(OUT / 'NSI_RESULTS.json', '径向收敛')],
    ]) + '\n\n' + cite('propagation') + '\n\n**适用限制：这不是完整三味数值演化。** 尤其大耦合处的全平面最小值是本近似模型的外推；不能由数值收敛证明θ13,m近似在所有大耦合仍准确。')

    isotopes = np.loadtxt(BASE / 'xe_isotopes.txt')
    mean = isotopes[:, 1] @ isotopes[:, 2]
    db = ResponseDB(ROOT / 'data/responses/responses_all.json')
    rows = []
    for number, mass, fraction in isotopes:
        key = 'Xe' + str(int(number))
        if key in b['physics']['isotope_keys']:
            resp = db.get(key)
            a = np.asarray(resp.responses['M'])
            detail = f"J={resp.basic['J']}; b={resp.basic['b']:.8g} GeV⁻¹; M{list(a.shape)}; pp/pn/nn a0={a[0,0,0]:.7g}/{a[0,1,0]:.7g}/{a[1,1,0]:.7g}"
        else:
            detail = 'MISSING：不计入、不补KN、不重归一'
        rows.append([key, f'{fraction:.6g}', f'{mass:.11g}', f'{1e6*6.02214076e23*fraction/mean:.8g}', detail])
    text += section('target', headings[3][1], r'''核数仍用完整九行NIST数丰度作分母：$n_A^{(1t)}=10^6N_A\eta_A/\sum_B\eta_Bm_B^{\rm atom}$。截面内部核质量沿用共享 $A m_u$ 约定。''' + f' 平均摩尔质量={mean:.11g} g/mol；实际七核素数丰度99.8158%。\n\n' + table(['核素key', '数丰度[1]', '原子质量[u]', '每吨核数[推导]', '实际M核表'], rows) + '\n\n' + ln(BASE / 'xe_isotopes.txt', '9×3原子质量/丰度表') + '；' + ln(ROOT / 'data/responses/responses_all.json', '实际核响应数值文件') + '。核表SHA256 `' + b['physics']['nuclear_sha256'] + '`。\n\n采用ResponseDB的(p,n)基底、W=e⁻²ʸ∑a_k yᵏ和已有全部实现通道M/SigmaPP/SigmaP/PhiPP/PhiPT/Delta/MPhiPP/SigmaPDelta；经原Li2026适配器进入振幅。没有再乘KN、Helm或额外自旋因子。共享理论公式在原模块维护，本文件只记录调用与实际资源。核表数值可用；外部作者原始版本和转换仍未独立认证，保留为R8本地直接采用来源。\n\n' + cite('R7', 'R8'))

    text += section('interaction', headings[4][1], r'''[paper2601] PDF p22 Eq.(95)采用 $C_{1,q}^{(6),\mathrm{NSI}}=-\sqrt2G_F\epsilon_{ee}^{qV}$，q=u,d，单位GeV⁻²；只有味矩阵ee元非零。SM及共享的LEFT→核子匹配、粒子响应R与核响应W、振幅归一化全部委托既有Li2026LegacyInteraction。

在本子空间，μ、τ仍是SM截面，因此实际入射态收缩为：

$$
\frac{d\sigma_{\rm eff}}{dT}
=\frac{d\sigma_{\rm SM}}{dT}
+P_{ee}(E_\nu;\epsilon)\left[\frac{d\sigma_e(\epsilon)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right].
$$

这是味密度矩阵与对角散射核收缩的代数式。即使电子味振幅被NSI抵消，$(1-P_{ee})\sigma_{\rm SM}$仍在，不能把全部太阳通量都按电子味NSI散射。
''' + '\n' + table(['对象', '实际输入/输出', '位置与依据'], [
        ['扫描参数', '实数εee-uV、εee-dV；无量纲；其余NSI=0', ln(ROOT / 'cevns_pyeft/theory/li2026/ee_vector_nsi.py', 'nsi_point / couplings') + '；Eq.(95)；非法味、复数和非对角项拒绝'],
        ['截面', 'cm²/keV；E轴MeV，T轴keVnr；6个单项式1,eu,ed,eu²,eu·ed,ed²', 'ElectronVectorNSI.spectral_coefficients；共享适配器四个SM vector/axial维6基底；固定T的E²dσ精确二次代数，不是拟合校准'],
        ['传播/散射绑定', '同一组(eu,ed)，错误参数点拒绝', ln(ROOT / 'cevns_pyeft/experiments/solar_nsi.py', 'check_point')],
    ]) + '\n\n' + cite('paper2601', 'propagation'))

    detector = []
    for sample, cfg in b['samples'].items():
        a = np.loadtxt(BASE / cfg['efficiency'])
        detector.append([sample, str(list(a.shape)), f'{a[0,0]:.9g}–{a[-1,0]:.9g}', f'{a[0,1]:.9g}/{a[-1,1]:.9g}',
                         str(cfg['T_bounds_keVnr']), cfg['exposure_tyr'], ln(BASE / cfg['efficiency'], '数值表') + '；' + cfg['source']])
    text += section('detector', headings[5][1], table(['样本', 'shape', '表内T[keVnr]', '首/末ε[1]', '积分T[keVnr]', '曝光[t·yr]', '数据与直接位置'], detector) + r'''

PandaX来自[R2] 2407.10892v3 PDF p3 Fig.1黑Total paired实线、US2虚线；曝光1.20、1.04 t·yr来自原实验。2409 Table II的paired=1.25与其冲突，本版沿用原实验1.20。XENONnT来自[R3] 2408.02877v2 PDF p4 Fig.1黑combined；3.51 t·yr。积分T界来自[R4] PDF p13 Table II。均为原生PDF矢量坐标提取，转数值后分段线性插值。X表第三列保留可见标记，低端在图框下的原生路径已提取，但不能声称逐点视觉核实。

**XENONnT约2.77–3 keVnr效率仍为MISSING。** 主扫描明确令ε(T)=末点0.123987528765，名称flat_sensitivity，是项目假设；另算zero/unit的0≤ε≤1两端，以及逐参数点对未知尾信号区间的无惩罚profile。后者是附加未知尾nuisance，不冒称论文原likelihood。范围外不静默插值为实验数据。

总效率已含选择和ROI，只乘一次；本单bin积分不再要求Qy、S1/S2二维概率矩阵或按Ne切窗。这里的探测器效率与原子核Response W是不同物理对象。
''' + '\n\n' + cite('R2', 'R3', 'R4'))

    kernel_rows = []
    for sample in ['PandaX_paired', 'PandaX_US2', 'XENONnT']:
        with np.load(OUT / 'kernels' / (sample + '.npz'), allow_pickle=False) as k:
            kernel_rows.append([sample, str(list(k['values'].shape)), f"{k['energy'][0]:.8g}–{k['energy'][-1]:.8g} MeV", ln(OUT / 'kernels' / (sample + '.npz'), '实际kernel')])
    text += section('prediction', headings[6][1], r'''[paper2601] p19 Eq.(84)、p20 Eq.(87)，曝光、每吨核数和时间展开一次：

$$
S_k=\mathcal E_k\sum_A n_A^{(1t)}t_{\rm yr}\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k(T)
\int_{E_{\min,A}(T)}^{16.56\,\mathrm{MeV}}dE_\nu\,\Phi_{8B}f_{8B}(E_\nu)\frac{d\sigma_{{\rm eff},A}}{dT}.
$$

输出每样本shape=(1,)，单位events/bin；核表→振幅→截面→含味概率的反冲率→Total效率→曝光→一个信号数。源通量、核数、效率、曝光各一次。没有c_i、信号标定或为贴图调整通量。

Fast只预积与味态无关的部分，保留E轴：$S_k=\sum_{A,j}w_j[K_{kA,0}(E_j)+P_{ee}(E_j;\epsilon)\sum_{m=1}^5K_{kA,m}(E_j)p_m(\epsilon)]$。K中已含源强、核数、曝光和效率；p_m为上节单项式。**Pee在每个扫描点重算，最终率面不是固定二次式。** 后端`energy_resolved_ee_vector_nsi_v1`独立于原固定ρ的interface_kernel_v1。
''' + '\n' + table(['样本', 'K shape', '实际Gauss E轴', '文件'], kernel_rows) + '\n\nK轴依次[核素, 已知段/未施效率尾段, 6单项式, E]；energy_weights另存MeV权重。NPZ禁止pickle，数组摘要和所有折叠依赖指纹均校验；只更换传播/profile时，rebind_state先要求源强/靶/曝光/效率/截面与数值设置的digest完全相同。\n\n实际检验：T节点401→801，E Gauss96→144；9个Slow(801×480)对Fast点包括SM、(0.3,−0.1)、(−17.3,15.7)，同时检查三个样本。容差max(3×10⁻⁴ events,0.2%)；径向8→16阶独立核验。详见' + ln(OUT / 'FORWARD_VALIDATION.json', '前向实测记录') + '。\n\n' + cite('paper2601'))

    text += section('statistics', headings[7][1], r'''采用[paper2601] PDF p20 Eq.(88)和p22的二维90%阈值4.61。观测是实验拟合信号产额，非逐箱原始候选；不再添加背景或使用Poisson计数。三个样本各自一个独立12% Gaussian pull：

$$
\chi^2(\epsilon)=\sum_{k=1}^{3}\min_{a_k}\left\{\frac{[D_k-(1+a_k)S_k(\epsilon)]^2}{\sigma_k^2}+\frac{a_k^2}{0.12^2}\right\},\qquad
\chi^2_{\rm prof}=\sum_k\frac{(D_k-S_k)^2}{\sigma_k^2+0.12^2S_k^2}.
$$
''' + '\n' + table(['样本顺序', 'D[events]', 'σstat[events]', '来源与处理'], [
        [s, d, sig, '[paper2601] p20 Eq.(88)文本；σ=D×' + pct + '，本轮精确采用印出百分数']
        for s, d, sig, pct in zip(['PandaX paired', 'PandaX US2', 'XENONnT'], c['statistics']['D'], c['statistics']['sigma_stat'], ['37.1%', '37.3%', '36.9%'])]) + '\n\n实际数组：' + ln(DATA / 'fitted_yields.json', 'NSI独立统计表') + '。旧v3.2.1舍入误差表保持原字节；本次SMχ²有相应微小区别。解析pull由Eq.(88)求导，已用独立的同时三pull线性最小二乘及Runtime逐样本统计核对。\n\n' + r'''定义 $\Delta\chi^2(\epsilon)=\chi^2(\epsilon)-\min_{\epsilon_{ee}^{uV},\epsilon_{ee}^{dV}}\chi^2$；减去联合参数最小值，不减SM值或各实验独立最小值之和。每种尾段/传播方案分别求自己的最小值。

绘图区为[-1,1]²的601×601网格，**最小化不局限图框**。利用Pee正下界、天然Xe电子散射正定二次型和US2正信号给出包围所有相关点的有限椭圆；白化后3个独立DE随机种子(17/41/83)加独立121×121网格局部多起点搜索。该包围域证明属于项目数值推导，仅在所声明近似模型内成立；不是对完整三味传播大耦合物理有效性的证明。
''' + '\n\n' + ln(OUT / 'MINIMUMS.json', '全域界、所有搜索点和最小值') + ' · ' + ln(ROOT / 'cevns_pyeft/statistics/solar_nsi.py', 'SolarNSIJoint') + '\n\n' + cite('paper2601'))

    best = r['primary_minimum']['minimum']
    result_rows = [['SM', '(0,0)', f"{r['SM']['chi2']:.12g}", ', '.join(f'{v:.9f}' for v in r['SM']['signal_events'])],
                   ['本近似模型联合最小值', f"({best['epsilon_ee_uV']:.8f},{best['epsilon_ee_dV']:.8f})", f"{best['chi2']:.12g}", ', '.join(f'{v:.9f}' for v in best['signal_events'])]]
    slices = next(v for v in read(OUT / 'SLICE_BOUNDARIES.json') if v['epsilon_ee_uV'] == 0)
    slice_rows = [[key, ', '.join(f'{v:.9f}' for v in values)] for key, values in slices.items() if isinstance(values, list)]
    text += section('results', headings[8][1], table(['位置', '(eu,ed)', 'raw χ²', 'paired/US2/X信号[events]'], result_rows) + '\n\n下图绿色填充是**本轮实际计算**；灰虚线才是论文PDF绿色矢量轮廓参照。论文轮廓在优化和前向扫描之后读取，仅用于比较，没有进入likelihood、效率、通量或kernel。\n\n![](' + os.path.relpath(OUT / 'solar_Fig4_computed_vs_paper.png', FILE.parent).replace('\\', '/') + ')\n\n' + f"601×601网格mask交并比={comparison['intersection_over_union']:.9f}，只是图形核对指标，不是物理精度认证。在(eu,ed)=(0,0.178)，本计算rawχ²={comparison['counterexample']['computed']['chi2']:.9f}、Δχ²={comparison['counterexample']['delta_chi2']:.9f}<4.61，允许；原PDF绿色多边形却排除此点。\n\n" + table(['eu=0截线', 'ed边界'], slice_rows) + '\n\nzero/unit尾段、固定SM传播和AGSS09 profile均未恢复论文中间禁区。将所有味散射都改成电子味NSI的诊断在此点得到χ²≈21.7914，但那是另一个物理模型，**未采纳，也不能据此断言作者的代码这样实现**。当前差异原因尚未确定。\n\n![](' + os.path.relpath(OUT / 'solar_NSI_controls.png', FILE.parent).replace('\\', '/') + ')\n\n![](' + os.path.relpath(OUT / 'solar_Pee_NSI.png', FILE.parent).replace('\\', '/') + ')\n\n' + ln(OUT / 'NSI_RESULTS.json', '全部数值与限制') + ' · ' + ln(OUT / 'PAPER_COMPARISON.json', '差异记录') + ' · ' + ln(OUT / 'source_evidence/paper_fig4_green_reference.json', '原PDF参考轮廓/坐标标定') + '\n\n' + cite('paper2601'))

    mapping = [
        ['P01', '三样本单bin身份与来源卡', 'experiments/solar_nsi.py::load_solar_nsi；独立scoped Catalog'],
        ['P02', '同位素核数、曝光（只读基础输入）', 'experiments/solar_singlebin.py::build_targets / SingleBinPreparation'],
        ['P03', '绝对源强、产生区平均Pee与ρ', 'sources/solar_msw.py::SolarMSW / SolarDiagonalState'],
        ['P04–P05', 'ee-only Wilson系数→共享振幅/核Response/截面', 'theory/li2026/ee_vector_nsi.py::nsi_point / ElectronVectorNSI'],
        ['P06', '三份Total效率及显式X尾假设', 'experiments/solar_nsi.py::tail_epsilon；旧TotalAcceptance只读复用'],
        ['P07', '实际按E、T积分，输出三信号', 'experiments/solar_nsi.py::NSIExecutor.__call__ / make_prediction'],
        ['P08', '保留E的K，每点重算Pee', 'kernels/solar_nsi.py::compile_kernel / SolarNSIKernel.blocks / rebind_state'],
        ['P09', '三pull解析profile、联合最小值、二维面', 'statistics/solar_nsi.py::SolarNSIJoint.chi2 / certified_domain / minimize'],
        ['P10', '收敛、Slow/Fast、来源/保护、图形差异', 'run_solar_b8_nsi_benchmark.py；test_solar_nsi.py；finalize_solar_b8_nsi.py'],
    ]
    text += section('code', headings[9][1], table(['阶段', '物理职责', '程序对应'], mapping) + '\n\n' + ' · '.join(ln(ROOT / p, Path(p).name) for p in [
        'cevns_pyeft/sources/solar_msw.py', 'cevns_pyeft/theory/li2026/ee_vector_nsi.py',
        'cevns_pyeft/experiments/solar_nsi.py', 'cevns_pyeft/kernels/solar_nsi.py', 'cevns_pyeft/statistics/solar_nsi.py']) + '''

源码各模块docstring/核心函数注释标注上述职责；共享理论公式不在实验loader复制。以下是实际Runtime最小调用，注释同时指出onboarding输入：

```python
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from cevns_pyeft.experiments.runtime import compile_experiment, predict_experiment

# Source/Target/Detector：显式NSI卡 + 只读单bin表；X尾假设有独立analysis身份。
experiment = load_solar_nsi('PandaX_US2', propagation='nsi_msw', tail_mode='flat_sensitivity')
# Interaction与Source使用相同epsilon；不把SM代表态带入NSI。
point = nsi_point(0.3, -0.1)
# Prediction：E保留在kernel中；每点重算Pee，再与核Response截面收缩。
numerics = {'n_er': 801, 'n_enu': 144}
kernel = compile_experiment(experiment, numerics=numerics)
prediction = predict_experiment(experiment, parameters=point, backend='fast', kernel=kernel, numerics=numerics)
print(prediction.counts)  # events/bin，不是逐箱Ne谱
```

从Gitup01根目录复算到新目录（拒绝覆盖已有最终结果）。当前runner还从output/source_evidence读取只作比较的参考轮廓，需先显式复制，避免计算完才因缺比较文件失败：

```powershell
New-Item -ItemType Directory -Force outputs/solar_b8_nsi/repeat_new/source_evidence
Copy-Item -LiteralPath outputs/solar_b8_nsi/20261112_fig4_run2/source_evidence/paper_fig4_green_reference.json -Destination outputs/solar_b8_nsi/repeat_new/source_evidence/
python -B tools/run_solar_b8_nsi_benchmark.py --output outputs/solar_b8_nsi/repeat_new --grid 601
```

数据已经存在，不需要再次运行create-only准备器。其来源转换可读prepare_solar_b8_nsi.py；文档由build_solar_b8_nsi_onboarding.py同源生成，默认--check只读，--write仅更新本版派生说明。
''')
    text += section('handoff', headings[10][1], table(['能力/材料', '当前状态', '影响'], [
        ['实际太阳NSI前向与联合区域', 'COMPUTED；内部数值验证通过', '有真实计算图、参数面、最小值与代码快照；与旧单bin/多bin隔离'],
        ['论文Fig.4绿色形状精确复现', 'NOT_ESTABLISHED', '指定差异点与截线；需核对作者传播、散射、输入卡及统计约定，不能以贴图调参代替'],
        ['XENONnT约2.77–3 keV接受度', 'MISSING；假设及界已算', '限制无假设点预测；不阻断本版明确条件的区域'],
        ['作者振荡/太阳模型精确卡', '未公布/未取得', '本版明确用固定PEANUTS示例与B16表；不能认证作者数值相同'],
        ['完整三味传播/大NSI有效性', '本版未实现', '大耦合全域最小值属于两味近似；后续严谨大域研究需改进传播并独立复算'],
        ['太阳结构原始47列表', '二手固定分发已采用；原始等价未独立核实', '不把转录来源冒充官网原件认证'],
        ['Xe124/126及核表外部认证', '前两核MISSING，外部认证UNRESOLVED', '七核素不重归一；只主张既有本地核表约定下的计算'],
        ['科学结果接受', 'NOT_REVIEWED', '记录用户执行授权，不虚构结果接受或FULLY_INTEGRATED'],
    ]) + '\n\n本轮42项太阳相关测试通过；完整旧COHERENT dataset回归在collection时被两份既有experiment.input.yaml的OS权限错误阻碍，默认与提权读取均失败。未改权限、旧数据或参考值，不将它们记为本轮PASS。164份保护基线及当前实现/缓存指纹逐项验收见' + ln(OUT / 'QA.json', '主线QA') + '。输入可用性、来源认证、数值通过与论文等价分别记录。')

    bibliography = ''
    for key, ref in refs.items():
        bibliography += f'**[{key}]** {ref["citation"]}\n\n' + ref.get('locator', '') + '。\n\n'
        if ref.get('url'):
            bibliography += '[' + ref['url'] + '](' + ref['url'] + ') · '
        path = ref.get('file', ref.get('direct_local_source'))
        if path:
            bibliography += ln(ROOT / path, '直接本地材料') + ' · '
        bibliography += ref.get('verification', '') + '\n\n'
        if ref.get('sha256'):
            bibliography += 'SHA256 `' + ref['sha256'] + '`。\n\n'
    text += section('references', headings[11][1], bibliography)
    return {FILE: text}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, expected in generated().items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding='utf8')
        elif not path.exists() or path.read_text(encoding='utf8') != expected:
            raise SystemExit('Missing/stale v3.3 document: ' + str(path))
    print('PASS: same-source NSI v3.3 onboarding' + (' written' if args.write else ' checked'))


if __name__ == '__main__':
    main()
