"""Generate/check v3.4 source documentation and register the optional mainline branch.

--write synchronizes only explicit navigation/authority records and this run's
delivery records. It never modifies core Python, project data or old results.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from extensions.solar_rho_snudd.protocol import CARD, PIN, read, save, sha
OUT = ROOT / 'outputs/external/solar_rho_snudd/20261112_run1'
DOC = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
FILE = DOC / 'SNUDD_EXTERNAL_ONBOARDING.v3.4.md'
PLAN = ROOT.parent / '重构/2026-11-12_EXTERNAL_SNUDD_ADAPTER_ONBOARDING.md'
MARKER = 'solar-snudd-v34'
BRANCH = 'external_solar_rho_snudd'
RUNS = [('PandaX4T', 'PandaX4T_2024_US2', 14), ('XENONnT', 'XENONnT_2024_SolarB8', 13)]


def rel(p):
    return p.relative_to(ROOT).as_posix()


def link(origin, target, label):
    return '['+label+'](<'+os.path.relpath(target, origin.parent).replace('\\', '/')+'>)'


def put(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf8')


def table(headings, rows):
    return '| '+' | '.join(headings)+' |\n|'+'|'.join('---' for _ in headings)+'|\n'+''.join(
        '| '+' | '.join(str(v).replace('|', '&#124;') for v in row)+' |\n' for row in rows)


def section(anchor, title, text):
    return f'\n<a id="{anchor}"></a>\n\n## {title}\n\n{text}\n\n[返回目录](#toc)\n'


def managed(path, text):
    old = path.read_text(encoding='utf8') if path.exists() else ''
    block = f'<!-- {MARKER}:start -->\n\n{text}\n\n<!-- {MARKER}:end -->'
    pattern = r'<!-- '+MARKER+r':start -->.*?<!-- '+MARKER+r':end -->'
    if re.search(pattern, old, re.S):
        updated = re.sub(pattern, lambda _: block, old, flags=re.S)
    elif path == DOC / 'README.md' and '<!-- solar-nsi-v33:end -->' in old:
        # This directory's frozen SM generator permits its later-analysis
        # navigation inside the explicit v3.3 managed block, not frozen prose.
        updated = old.replace('<!-- solar-nsi-v33:end -->', block+'\n\n<!-- solar-nsi-v33:end -->')
    else:
        updated = old.rstrip()+'\n\n'+block+'\n'
    put(path, updated)


def generated():
    c = read(CARD)
    r = read(OUT / 'RESULTS.json')
    b = read(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json')
    nsicard = read(ROOT / c['baseline_card'])
    tests = read(OUT / 'QA.json')
    ln = lambda p, label: link(FILE, p, label)
    refs = c['references']
    def cite(*keys):
        return '\n\n'.join('['+key+'] '+refs[key]['citation']+' '+refs[key]['locator']+'。' for key in keys)
    headings = [('status', '版本、范围与实际安装'), ('source', 'Source：绝对通量与外部传播数据'),
        ('oscillation', '传播：实际参数、近似及NSI映射'), ('protocol', '文件契约、能量网格与缓存'),
        ('target', 'Target与原子核Response'), ('detector', 'Detector与Observable'), ('prediction', 'Prediction与Statistics：怎样真正进入Runtime'),
        ('results', '实际基准、差异及验收'), ('code', '程序对应与复算'), ('limits', '能力边界和来源缺口'), ('references', '标准文献与固定上游原件')]
    text = '# 太阳⁸B SNuDD外部传播 onboarding v3.4（新版本／主线接入核对版）\n\n'
    text += '**2026-11-12。SNuDD已经安装到独立环境，外部ρ已接入标准PreparedExperiment → predict/compile/evaluate，并完成实际三样本点基准。** 此版与本地B16-MSW v3.3并列，保留原SM、多bin与V/B−L。科学结果接受NOT_REVIEWED；不是完整三味演化，也没有把本次适配器验收称为新Fig.4精确复现。\n\n'
    text += ' · '.join([ln(CARD, '实际来源/参数卡'), ln(OUT / 'README.md', '实际结果与验收'), ln(ROOT / 'extensions/solar_rho_snudd/README.md', '安装/接口入口'), ln(PLAN, '已修订原方案')])
    text += '\n\n<a id="toc"></a>\n\n## 目录\n\n'+'\n'.join('- ['+title+'](#'+anchor+')' for anchor, title in headings)+'\n'
    text += section('status', headings[0][1], table(['对象', '实际位置/数值', '核验范围'], [
        ['官方源码', ln(ROOT / '.externals/SNuDD/README.md', '.externals/SNuDD')+'；commit `'+PIN+'`', '先固定commit再安装；checkout跟踪文件逐项hash；未改上游源码'],
        ['独立Python', ln(ROOT / '.venvs/snudd/pyvenv.cfg', '.venvs/snudd')+'；Python3.11.15', '外部子进程独立依赖；主项目依赖列表未改'],
        ['实际依赖', '; '.join(k+'='+v for k, v in c['versions'].items()), ln(ROOT / 'extensions/solar_rho_snudd/requirements.lock.txt', '完整锁定列表')+'；pip check通过；上游漏声明packaging，独立补齐'],
        ['主进程隔离', str(r['host_imported_snudd']), '运行真实基准后sys.modules未包含snudd；原cevns_pyeft/*.py保持原字节'],
        ['接入范围', 'ee-only实数uV/dV；日间太阳传播；单bin三样本', '独立scoped Catalog及分析指纹；原默认实验列表和入口不变'],
    ])+'\n\n第一次安装使用既有清华镜像未取得构建依赖，改用官方PyPI成功；随后import检查发现packaging遗漏并补齐。'+ln(OUT / 'INSTALL_REPORT.json', '主安装报告')+'、'+ln(OUT / 'INSTALL_PACKAGING_REPORT.json', '补依赖报告')+'保留实际轮子下载URL和hash。'+cite('software'))
    source = np.loadtxt(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt')
    profile = np.loadtxt(OUT / 'source_evidence/snudd_profile_diagnostic.txt')
    raw = np.loadtxt(ROOT / c['production_file']['path'])
    text += section('source', headings[1][1], r'''通量仍为所有活跃味合计的地球处⁸B通量：$d\phi_{\rm total}/dE=\Phi_{8B}f_{8B}(E)$。SNuDD只提供无量纲传播态，不提供本次计算的源强、散射截面、核模型或探测器效率。
'''+'\n'+table(['输入', '实际数值/shape与单位', '本地文件、直接来源和核验范围'], [
        ['总通量', '固定5.46×10⁶ cm⁻²s⁻¹', ln(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json', '只读基础卡')+'；Li et al.,2409.04703v2 p5 Eq.(29)；沿用v3.3项目选择'],
        ['中微子能谱', f'829×2；0–16.56MeV；f单位MeV⁻¹；原网格积分{np.trapezoid(source[:,1],source[:,0]):.10g}', ln(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt', '原Bahcall表')+'；Bahcall et al.,PRC54(1996)411，DOI10.1103/PhysRevC.54.411；官网829行前两列，保留舍入和线性插值'],
        ['电子/中子密度', '解析拟合；ne/N_A、nn/N_A单位mol/cm³；系数见下式', ln(ROOT / '.externals/SNuDD/snudd/nsi/solar_profiles.py', '实际solar_profiles.py')+'；[density]。直接采用软件拟合，未认证与原论文每个拟合数字等价'],
        ['⁸B产生位置', f'{list(raw.shape)}；x={raw[0,0]:g}–{raw[-1,0]:g}；max={raw[:,1].max():.9g}；原表积分={np.trapezoid(raw[:,1],raw[:,0]):.9g}', ln(ROOT / c['production_file']['path'], '实际96×2原表')+'；表头标注[production]；未标为B16发布表'],
        ['实际产生区求积', '0–0.35Rsun，1000等距点；原表线性插值、域外0；按dr归一，不乘r²', ln(ROOT / '.externals/SNuDD/snudd/nsi/nsi_probabilities.py', '_cos_matter_average')+'；直接软件约定'],
        ['诊断数组', f'{list(profile.shape)}；首行'+', '.join(f'{v:.9g}' for v in profile[0]), ln(OUT / 'source_evidence/snudd_profile_diagnostic.txt', 'x/ne/nn/产生区诊断')+'；由实际SNuDD函数求值，并非新输入表'],
    ])+r'''

实际采用的密度函数（[density]直接源码；x=r/Rsun）：

$$
\log_{10}(n_e/N_A)=2.36-4.52x-0.33\exp[-(x/0.075)^{1.1}],\qquad
\log_{10}(n_n/N_A)=1.72-4.80x.
$$

原v3.3的PEANUTS＋Magnus/B16四列表不参与SNuDD传播。本轮替换同时改变太阳密度/产生区方案；新旧Pee差异不应全部归于求解算法精度。全部直接软件文件、版本和哈希由参数卡登记；原论文与软件转录的独立认证保持单列，不用软件hash冒充原文认证。
'''+ '\n\n'+cite('density', 'production'))
    osc = c['oscillation_actual_GeV_rad']
    text += section('oscillation', headings[2][1], table(['参数', '实际采用值', '来源/选择'], [
        ['θ12', f"{osc['theta_12']:.9g}rad", '沿用v3.3 PEANUTS项目输入，显式传入，不用SNuDD默认33.68deg'],
        ['θ13', f"{osc['theta_13']:.9g}rad", '沿用v3.3 PEANUTS项目输入，显式传入'],
        ['Δm²21', f"{osc['delta_m12']*1e18:.9g}eV²", '沿用v3.3的7.42e−5；传给SNuDD换为GeV²'],
        ['θ23 / δCP / Δm²31', f"{np.rad2deg(osc['theta_23']):.8g}deg / {np.rad2deg(osc['delta_cp']):.8g}deg / {osc['delta_m31']*1e18:.8g}eV²", '[remaining_oscillation]固定软件默认；当前ee-only散射下μτ分配不影响事例数，Δ31用于近似有效性诊断'],
        ['传播近似', '两味有效绝热太阳模型，质量相位平均后UρmassU†重建味矩阵；日间，无地球再生', '[software]SolarDensityMatrixCalculator；不是完整三味太阳数值演化'],
    ])+r'''

NSI从项目的实数eu、ed映射到SNuDD因子化参数：$\epsilon_p=2eu+ed$、$\epsilon_n=eu+2ed$，$s=\sqrt{\epsilon_p^2+\epsilon_n^2}/\sqrt5$，$\eta=\operatorname{atan2}(\epsilon_n,\epsilon_p)$，$\varphi=0$，$\epsilon_{\rm matrix}=\operatorname{diag}(s,0,0)$。零点定义η=0。GeneralNSI中的ξp、ξn与矩阵相乘后分别恢复上述质子/中子耦合；ξe=0。只传NP epsilon，SNuDD自行包含标准物质势，不能把SM+NP总Wilson系数再当作NP输入。

输出完整rho在味基底(e,mu,tau)保存，包含实际非对角元。当前散射核为diag(σe,σSM,σSM)，因此只用rho_ee与对角等价投影不会改变本子空间事件数；这项等价不推广到非对角/复数NSI。
'''+'\n\n'+cite('nsi_mapping', 'software', 'remaining_oscillation'))
    grid = read(OUT / 'ENERGY_CONTRACT.json')
    text += section('protocol', headings[3][1], table(['字段/处理', '实际约定', '验证'], [
        ['E_MeV', f"正、有限、严格递增；正式union={grid['union_nodes']}点；Slow={grid['slow_positive_nodes']}，Fast={grid['fast_nodes']}", ln(OUT / 'ENERGY_CONTRACT.json', '完整实际网格')+'；不同网格可另导出，已知并集精确取子集'],
        ['rho_flavour', '(N_E,3,3)，complex128，单位1，味顺序e/mu/tau', '每点Hermitian、trace=1、PSD、finite；完整原矩阵留在rho.npz'],
        ['pee', '(N_E,)，float64，等于Re(rho[:,0,0])', '读取时逐值核对；不静默重归一/裁剪/插值'],
        ['manifest.json', 'commit、依赖版本、实际振荡卡、NSI映射、能量hash、数组文件hash和物理性/绝热诊断', 'cache key包含card内容hash、两耦合IEEE精确表示、能量bytes/shape、source8B、粒子/基底/日间模式'],
        ['缓存', '每个NSI点及能量网格独立目录；允许一次外部进程批量导出多点', '原NPZ摘要验证、错误epsilon/网格/损坏拒绝；首次读取核验完整内容'],
        ['可用性', '无缓存时需独立环境和固定原件；已有有效包可直接读取', '缺环境/导出错误会明确失败，不回退到SM或本地MSW'],
    ])+'\n\n'+ln(ROOT / 'extensions/solar_rho_snudd/protocol.py', '文件合同与校验')+' · '+ln(ROOT / 'extensions/solar_rho_snudd/state.py', '精确坐标状态提供器')+'。正式运行保存'+str(r['full_rho_packets'])+'份完整ρ包；深层hash目录由输出README统一说明，避免逐包产生新文档。')
    targetfile = ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt'
    isotopes = np.loadtxt(targetfile)
    text += section('target', headings[4][1], table(['输入', '实际值/数组', '来源与核验范围'], [
        ['天然Xe', '9×3：A=124–136；首行'+str(isotopes[0].tolist())+'；末行'+str(isotopes[-1].tolist()), ln(targetfile, '原NIST数丰度/原子质量表')+'；NIST Atomic Weights and Isotopic Compositions for Xenon；原9行作每吨核数分母'],
        ['核响应', 'Xe128/129/130/131/132/134/136；原数丰度0.998158；不补124/126、不重归一', ln(ROOT / 'data/responses/responses_all.json', '实际原核表')+'；用户已选既有本地ResponseDB/Li2026约定，外部作者发布认证未闭合'],
        ['核数/核质量', '每吨核数由9行丰度与原子质量计算；截面核质量沿用A·amu', ln(ROOT / 'cevns_pyeft/experiments/solar_singlebin.py', 'build_targets')+'；v3.3同一输入和算法，只读复用'],
        ['散射理论', '原核Response→共享振幅；C61q_NP=−√2G_Fεee_qV', ln(ROOT / 'cevns_pyeft/theory/li2026/ee_vector_nsi.py', '原ElectronVectorNSI')+'；Li et al.,2601.19883v2 p22 Eq.(95)。不调用SNuDD的核截面或Helm'],
    ])+'\n\n逐核素M系数shape、b与代表值完整保留在'+ln(DOC / 'NSI_EE_VECTOR_ONBOARDING.v3.3.md#target', 'v3.3 Target原记录')+'；本轮实际编译的三个核折叠数组与旧数组逐位相同，见前向验证。')
    rows = []
    for sample, config in b['samples'].items():
        name = config['efficiency']
        a = np.loadtxt(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883' / name)
        rows.append([sample, config['exposure_tyr'], str(config['T_bounds_keVnr']), str(list(a.shape)),
                     f'{a[0,0]:.8g}–{a[-1,0]:.8g}; ε={a[0,1]:.8g}/{a[-1,1]:.8g}',
                     ln(ROOT / 'data/benchmarks/solar_b8_singlebin_2601_19883' / name, '原表')+'；'+config['source']])
    text += section('detector', headings[5][1], table(['样本', '曝光[t·yr]', '积分T[keVnr]', 'shape', '原表范围/首末ε[1]', '出处'], rows)+
        '\n\nPandaX：Bo Z et al.,PRL133(2024)191001，DOI10.1103/PhysRevLett.133.191001，2407.10892v3 p3 Fig.1 Total两线。XENONnT：Aprile E et al.,PRL133(2024)191002，DOI10.1103/PhysRevLett.133.191002，2408.02877v2 p4 Fig.1黑combined。T界沿用Liao J et al.,2502.10702v2 p13 Table II。\n\n每样本一个拟合信号数，输出events/bin；Total含ROI选择，只乘一次，无Qy/Ne再切窗、无ci。XENONnT约2.77–3keV效率仍MISSING；主点明确用末点平坦延伸，zero/unit为0≤ε≤1界。软件接入没有补出该缺失实验尾段。')
    text += section('prediction', headings[6][1], r'''扩展Preparation从只读单bin输入构建新模型，把同一ExternalSolarState同时绑定到source.state_provider（Slow）及model.state_model（Fast），再通过原load_experiment生成新的PreparedExperiment。没有修改已装配对象、伪造旧指纹或将rebind_state当作注入函数。

$$
\frac{d\sigma_{\rm eff}}{dT}=\frac{d\sigma_{\rm SM}}{dT}+P_{ee}(E;\epsilon)\left[\frac{d\sigma_e(\epsilon)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right].
$$

此式乘原总通量与Bahcall谱，再按E、T积分，并乘一次原每吨核数、Total效率和曝光。μτ的SM散射保留。新的kernel沿用energy_resolved_ee_vector_nsi_v1算法，保留E轴、每点读取对应Pee；独立编译和保存，不借用旧物理指纹。

统计沿用Li et al.,2601.19883v2 p20 Eq.(88)：三个拟合信号D=(3.5,75,10.7)events，σ=(1.2985,27.975,3.9483)events，分别由37.1%/37.3%/36.9%推导，三个独立12%pull。数据已是实验拟合信号，不再加背景或当作原始Poisson计数：

$$
\chi^2_{\rm prof}(\epsilon)=\sum_k\frac{[D_k-S_k(\epsilon)]^2}{\sigma_k^2+0.12^2S_k(\epsilon)^2}.
$$
'''+'\n\n'+ln(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json', '实际统计数组与逐项来源')+' · '+ln(ROOT / 'cevns_pyeft/statistics/solar_nsi.py', '原联合统计程序')+'。本次实际验证点χ²及Runtime绑定；未运行新的全域最小化/完整Fig.4置信区。')
    rows = []
    for row in r['points']:
        rows.append([str(row['point']), ', '.join(f'{v:.9f}' for v in row['snudd']['signal_events']),
                     f"{row['snudd']['chi2']:.10g}", ', '.join(f'{v:.9f}' for v in row['local_B16_MSW']['signal_events']),
                     f"{row['local_B16_MSW']['chi2']:.10g}"])
    diagnostics = r['packet_adiabatic_diagnostics']
    gammas = [p['diagnostic']['minimum_gamma'] for p in diagnostics if p['diagnostic']['minimum_gamma'] is not None]
    text += section('results', headings[7][1], table(['(eu,ed)', 'SNuDD三信号[events]', 'SNuDD rawχ²', '原B16三信号[events]', '原rawχ²'], rows)+
        '\n\n**SM信号逐位相同**：SM下截面味普适，传播重分味不会改变总信号。NSI下出现差异，传播输入的影响正确进入了散射。统计表和核折叠数组未改变。\n\n'+
        '![]('+os.path.relpath(OUT / 'snudd_vs_local.png', FILE.parent).replace('\\', '/')+')\n\n实线为SNuDD，虚线为本地B16-MSW；振荡θ12/13/Δ21一致，太阳profiles不同。\n\n'+
        f"实际9个Slow/Fast点，另有US2在非零及远处耦合点的1201×216求积加密；容差max(3×10⁻⁴events,0.2%)。本轮测试{tests['tests_passed']}项通过；{tests['protected_files']}份保护文件保持原字节。"+
        '\n\n'+ln(OUT / 'FORWARD_VALIDATION.json', '逐样本前向验证')+' · '+ln(OUT / 'RESULTS.json', '完整实际点结果')+' · '+ln(OUT / 'QA.json', '安装/测试/文件保护/接入验收')+
        '\n\n绝热性另外以两能级劈裂/(2|dθm/dr|)作有限差分诊断，覆盖输入能量与太阳0–1Rsun的4001点。已保存各包最小γ和|2EV/Δ31|；'+
        (f'当前诊断中的最小γ={min(gammas):.9g}。' if gammas else '')+
        'γ≥100只按上游建议作诊断标签，不证明两味近似在大NSI有效。上游gamma_check在此commit将返回(value,label)的tuple与scalar比较，未调用；本项目未修改上游源码。')
    text += section('code', headings[8][1], table(['onboarding责任', '实际程序位置', '输入/输出'], [
        ['安装与来源冻结', ln(ROOT / 'extensions/solar_rho_snudd/prepare.py', 'prepare.py')+' / '+ln(CARD, 'snudd.input.json'), '固定checkout+实际安装信息→明确模型卡/依赖锁'],
        ['传播', ln(ROOT / 'extensions/solar_rho_snudd/export_rho.py', 'export_rho.py'), '唯一import snudd；MeV→GeV、NP-only映射→完整ρ与manifest'],
        ['状态/网格', ln(ROOT / 'extensions/solar_rho_snudd/state.py', 'ExternalSolarState'), '子进程导出、参数/坐标绑定、精确子集→Pee及当前等价态'],
        ['实验接入', ln(ROOT / 'extensions/solar_rho_snudd/experiment.py', 'load_snudd / Preparation'), '新Definition/scoped Catalog→标准PreparedExperiment'],
        ['事件数/统计/实际验收', ln(ROOT / 'extensions/solar_rho_snudd/run_with_rho.py', 'run_with_rho.py')+' / '+ln(ROOT / 'tests/test_solar_snudd.py', 'test_solar_snudd.py'), '原NSIExecutor、kernel和统计API；与旧分支同条件比较'],
    ])+r'''

从Gitup01根目录，以主项目解释器运行（外部传播由适配器自动调用独立Python）：

```powershell
python -B tools/run_solar_b8_snudd_benchmark.py --output outputs/external/solar_rho_snudd/repeat_new
python -B -m extensions.solar_rho_snudd.prepare --check
python -B tools/finalize_solar_b8_snudd.py --check
```

最小API：

```python
from extensions.solar_rho_snudd.experiment import load_snudd
from cevns_pyeft.experiments.runtime import compile_experiment, predict_experiment
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point

experiment = load_snudd('PandaX_US2')  # 显式外部传播入口
numerics = {'n_er': 801, 'n_enu': 144}
kernel = compile_experiment(experiment, numerics=numerics)
prediction = predict_experiment(experiment, parameters=nsi_point(.3, -.1),
    backend='fast', kernel=kernel, numerics=numerics)
print(prediction.counts)  # 原Response/效率/曝光；仅Pee来自外部
```

重装命令、固定commit、pip报告和锁定依赖见扩展README。既有load_solar_nsi(...,propagation='nsi_msw')继续原B16模型，不声称原签名新增了snudd选项。本扩展随工作区运行，未作为根发行包强制依赖。
''')
    text += section('limits', headings[9][1], table(['项目', '当前状态及影响'], [
        ['安装＋ρ导出＋主线Runtime', '已经实际完成；通过新身份和新缓存使用；保留全部完整ρ'],
        ['完整三味太阳演化/地球再生', '本次未实现；day-only有效两味近似，不因3×3输出而升级声明'],
        ['SNuDD太阳输入原文等价性', '直接软件输入与哈希已核；密度拟合/96点产生区相对原论文的认证未独立完成，软件引用与原论文身份分开记录'],
        ['XENONnT尾段', '约2.77–3keV接受度仍MISSING，保留假设及界'],
        ['核表缺口', 'Xe124/126缺失且不重归一，外部作者核表认证未闭合'],
        ['Fig.4绿色区域', '旧v3.3已有计算及论文差异；本轮验证的是SNuDD适配和点预测，未生成新的完整置信区域'],
        ['科学结果接受', 'NOT_REVIEWED；执行授权不冒充物理结果接受'],
    ])+'\n\n移除整个extensions/solar_rho_snudd及其外部checkout/环境后，原主项目不依赖该扩展。根README、.gitignore和正式run记录保留历史入口；移除时按文件生命周期规则同步导航。GPL-3.0上游LICENSE保持原样；本次是本地安装，未作扩展分发。')
    references = ''
    for key, ref in refs.items():
        references += '**['+key+']** '+ref['citation']+'\n\n'+ref['locator']+'。\n\n'
        references += '['+ref['url']+']('+ref['url']+')'
        if ref.get('direct_url'):
            references += ' · [直接采用的固定源码/数据]('+ref['direct_url']+')'
        references += '\n\n'
    references += '复用的源谱、靶、效率、统计完整标准引文与PDF页/式/图定位见'+ln(DOC / 'NSI_EE_VECTOR_ONBOARDING.v3.3.md#references', 'v3.3原始引用与核验范围')+'；这些数值文件本轮保持原字节。'
    text += section('references', headings[10][1], references)
    plan = '# CEvNS-pyEFT：SNuDD外部传播接入方案 v1.1（已实施）\n\n'
    plan += '**2026-11-12。已按审查意见调整、隔离安装、修改文档并接入主线Runtime。** 原设计稿修改前已备份；当前完整同源onboarding为'+link(PLAN, FILE, '新v3.4读本')+'，实际结果为'+link(PLAN, OUT / 'README.md', '三样本前向/统计基准')+'。\n\n'
    plan += table(['原设计问题', '实际修订'], [
        ['main动态版本安装', '先固定完整commit '+PIN+'，再在.venvs/snudd安装；依赖及轮子来源实际记录'],
        ['rebind_state能否注入不明确', '新增扩展Preparation/ExternalSolarState，绑定源和Fast状态，生成新PreparedExperiment；独立编译kernel'],
        ['单份固定能量网格', '导出实际Slow/Fast/诊断节点并集，精确查取子集；无插值/外推；其他网格单独导出'],
        ['振荡参数默认变化', '显式匹配旧θ12/13/Δ21；其余参数数值/来源列出'],
        ['太阳输入来源笼统', '密度拟合源码/系数/上游论文、96×2产生区表、实际径向积分和每文件hash全部登记；不冒称B16'],
        ['只导出ρ未真正计算', '已使用标准predict/compile/evaluate；实际Slow/Fast、共享振幅全ρ等价、缓存拒绝和旧文件保护验收'],
    ])
    plan += '\n\n## 安装与复算\n\n'+link(PLAN, ROOT / 'extensions/solar_rho_snudd/README.md', '扩展安装及最小API')+' · '+link(PLAN, CARD, '实际来源卡')+' · '+link(PLAN, OUT / 'QA.json', '实测验收')+'\n\n'
    plan += '物理源码cevns_pyeft/、原data/、根依赖列表及原SM/多bin/NSI结果保持原字节；只增加扩展与显式工具入口，README、.gitignore、正式run分支记录同步维护。SNuDD仅在独立子进程导入，采用完整ρ数值文件边界；没有全局插件管理器、monkey-patch或默认注册表改变。\n\n'
    plan += '本次是日间有效两味传播适配，不是完整三味太阳演化；现有核表及X尾缺口、原文等价性限制、科学接受NOT_REVIEWED继续保留。\n'
    return {FILE: text, PLAN: plan}


def audit():
    baseline = read(OUT / 'PROTECTED_BASELINE.json')
    changed = [p for p, h in baseline.items() if sha(ROOT / p) != h]
    if changed:
        raise ValueError('protected file changed: '+str(changed))
    result = read(OUT / 'RESULTS.json')
    if result['source_card_sha256'] != sha(CARD) or result['host_imported_snudd'] or not result['SM_counts_bitwise_unchanged']:
        raise ValueError('actual result/card/isolation identity invalid')
    if result['runner_sha256'] != sha(ROOT / 'extensions/solar_rho_snudd/run_with_rho.py'):
        raise ValueError('executed runner changed since calculation')
    from extensions.solar_rho_snudd.prepare import expected_card
    if read(CARD) != expected_card():
        raise ValueError('source installation/card stale')
    xml = OUT / 'tests.xml'
    cases = list(ET.parse(xml).getroot().iter('testcase'))
    failed = [t.attrib for t in cases if any(t.find(k) is not None for k in ['failure', 'error', 'skipped'])]
    if not cases or failed:
        raise ValueError('tests not all passed: '+str(failed))
    checks = read(OUT / 'FORWARD_VALIDATION.json')
    if not all(c['old_and_new_fold_arrays_bitwise_identical'] for c in checks):
        raise ValueError('unrelated physics fold changed')
    from extensions.solar_rho_snudd.experiment import load_snudd
    from cevns_pyeft.experiments.runtime import validate_snapshot
    model_records = {}
    shared = None
    for sample in result['sample_order']:
        e = load_snudd(sample, cache_root=OUT / 'rho_cache', interaction=shared)
        shared = e.model.interaction
        validate_snapshot(e)
        saved = read(OUT / sample / 'PREPARED_MODEL.json')
        if saved['physics_fingerprint'] != e.physics_fingerprint or saved['analysis_fingerprint'] != e.analysis_fingerprint:
            raise ValueError('executed model/analysis identity changed: '+sample)
        model_records[sample] = {'physics_fingerprint': e.physics_fingerprint, 'analysis_fingerprint': e.analysis_fingerprint}
    return {'date': '2026-11-12', 'status': result['status'], 'protected_files': len(baseline), 'protected_changed': changed,
            'tests_passed': len(cases), 'test_classes': {n: sum(t.attrib.get('classname') == n for t in cases) for n in sorted({t.attrib.get('classname') for t in cases})},
            'actual_slow_fast_checks': sum(len(x['direct_slow_checks']) for x in checks), 'SM_counts_bitwise_unchanged': True,
            'all_nuclear_fold_arrays_bitwise_unchanged': True, 'host_imported_snudd': False,
            'independent_install': read(OUT / 'source_evidence/INSTALLATION.json')['versions'],
            'source_card_sha256': sha(CARD), 'scientific_acceptance': 'NOT_REVIEWED',
            'new_full_Fig4_region': 'NOT_COMPUTED; scope is source integration and forward/statistical point benchmark',
            'legacy_full_dataset_regression': 'unchanged core; prior OS access error for CsI2017/CsI2021 YAML retained separately, not counted as passing',
            'upstream_code_modified': False, 'global_default_ids_modified': False, 'current_prepared_models': model_records}


def register(qa):
    records = {}
    for family, dataset, expected in RUNS:
        run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        path = run / '00_MIGRATION_PROGRESS.md'
        old = path.read_text(encoding='utf8')
        p = json.loads(re.search(r'```json\s*\n(.*?)\n```', old, re.S)[1])
        if BRANCH not in p.get('parallel_analyses', {}) and p['revision'] != expected:
            raise ValueError('canonical revision changed; reload before writing')
        log = read(run / 'AUTHORIZATION_LOG.yaml')
        if not any(x.get('authorization_id') == 'W0007' for x in log['entries']):
            log['entries'].append({'authorization_id': 'W0007', 'status': 'ACTIVE', 'date': '2026-11-12', 'approval_kind': 'explicit_user_instruction',
                'user_quote': '请你调整方案，进行安装，修改文档，接入主线', 'scope': 'reviewed optional SNuDD source adapter, isolated installation, actual runtime point benchmark and documentation/mainline branch records',
                'allowed_actions': ['read', 'create', 'modify'], 'create_paths': ['extensions/solar_rho_snudd/', '.externals/SNuDD/', '.venvs/snudd/', 'tools/run_solar_b8_snudd_benchmark.py', 'tools/finalize_solar_b8_snudd.py', 'tools/validate_solar_b8_snudd.mjs', 'tests/test_solar_snudd.py', rel(FILE), 'outputs/external/solar_rho_snudd/'],
                'modify_paths': ['explicit README/navigation owners', '.gitignore', rel(run), str(PLAN)], 'delete_paths': [],
                'recovery_plan': 'backup/solar-snudd-20261112-01/MANIFEST.json', 'result_acceptance_separate': True})
            save(run / 'AUTHORIZATION_LOG.yaml', log)
        decisions = read(run / 'P04_DECISION_LOG.yaml')
        if not any(x.get('decision_id') == 'D0007' for x in decisions['entries']):
            decisions['entries'].append({'decision_id': 'D0007', 'date': '2026-11-12', 'user_quote': '请你调整方案，进行安装，修改文档，接入主线',
                'scope': 'execute revised external SNuDD source design in mainline; preserve original scientific branches',
                'interpretation': 'day-only SNuDD own profiles; explicitly matched theta12/theta13/dm21; ee-only realuV/dV; complete rho retained and equivalent restricted-rate projection',
                'execution_authorized': True, 'result_acceptance': 'NOT_REVIEWED', 'core_changes': False,
                'limits': ['effective two-flavor solar approximation', 'do not relabel as originalB16 propagation', 'no source flux recalibration', 'no full new Fig4 result claimed']})
            save(run / 'P04_DECISION_LOG.yaml', decisions)
        branch = {'analysis_id': BRANCH, 'parent_analysis': 'solar_ee_vector_nsi', 'version': '3.4', 'date': '2026-11-12',
            'status': qa['status'], 'decision_ref': 'D0007', 'write_ref': 'W0007', 'scientific_result_acceptance': 'NOT_REVIEWED',
            'onboarding': rel(FILE), 'source_card': rel(CARD), 'source_card_sha256': sha(CARD), 'entry': 'tools/run_solar_b8_snudd_benchmark.py',
            'loader': 'extensions.solar_rho_snudd.experiment.load_snudd', 'results': rel(OUT / 'RESULTS.json'), 'qa': rel(OUT / 'QA.json'),
            'software_commit': PIN, 'primary_old_branch': 'solar_ee_vector_nsi (retained)', 'default_global_activation': False,
            'capability': {'installation': 'PASS', 'rho_export': 'PASS', 'standard_runtime': 'PASS', 'actual_Slow_Fast': 'PASS', 'new_full_Fig4': 'NOT_RUN', 'human': 'NOT_REVIEWED'}}
        save(run / 'SNUDD_SOURCE_BRANCH.json', branch)
        phases = {}
        for phase, detail in [('P03', '实际SNuDD密度/产生区/振荡值、完整ρ文件及精确能量绑定'), ('P07', '原直接积分核Response/效率/曝光；SNuDD源态真实传入Slow'),
                              ('P08', '新独立能量kernel，9点Slow/Fast与求积加密；科学Slow接受仍NOT_REVIEWED'), ('P09', '原三独立pull统计，实际点χ²与Runtime一致'), ('P10', '独立安装、物理/文件合同、原文件保护与源方案差异；不主张完整新Fig4')]:
            f = run / 'phases' / (phase+'_snudd_source.md')
            put(f, '# '+phase+'：SNuDD外部传播接入\n\n'+detail+'。\n\n'+link(f, FILE, '同源完整onboarding与逐项来源')+' · '+link(f, OUT / 'QA.json', '实际验收')+' · '+link(f, run / 'SNUDD_SOURCE_BRANCH.json', '本分支权威记录')+
                '\n\n本报告记录已执行的能力接入，不虚构阶段人工接受。执行W0007，科学接受NOT_REVIEWED；P08正式科学接受前提仍未满足，技术对照独立记录为PASS。\n')
            phases[phase] = rel(f)
        branch['phase_reports'] = phases
        save(run / 'SNUDD_SOURCE_BRANCH.json', branch)
        manifest = read(run / '00_IMPLEMENTATION_MANIFEST.yaml')
        manifest.setdefault('extensions', {})[BRANCH] = branch
        save(run / '00_IMPLEMENTATION_MANIFEST.yaml', manifest)
        if BRANCH not in p.get('parallel_analyses', {}):
            p['previous_revision'] = p['revision']
            p['revision'] += 1
        p.setdefault('parallel_analyses', {})[BRANCH] = branch
        # The parent NSI analysis remains current; this is its source variant.
        p['current_source_variant'] = BRANCH
        p['updated_at'] = '2026-11-12'
        p['checkpoint'] = {'phase_id': 'P10', 'phase_name': 'external solar source integration review', 'skill': 'cevns-experiment',
                          'step_id': 'phase.P10.human_review', 'next_action': 'review validated SNuDD source variant and explicit approximation/input differences', 'resume_requires': []}
        p['authorization_refs'].update(snudd_source_scope='D0007', snudd_source_write='W0007')
        p['artifact_refs'].update(snudd_source_branch=rel(run / 'SNUDD_SOURCE_BRANCH.json'), snudd_onboarding=rel(FILE))
        p.setdefault('gates', {})['external_snudd_integration'] = {'machine': 'PASS', 'human': 'NOT_REVIEWED', 'report_ref': phases['P10'], 'decision_refs': ['D0007']}
        current = json.loads(re.search(r'```json\s*\n(.*?)\n```', path.read_text(encoding='utf8'), re.S)[1])
        if current['revision'] != json.loads(re.search(r'```json\s*\n(.*?)\n```', old, re.S)[1])['revision']:
            raise ValueError('concurrent index update; stop rather than overwrite')
        put(path, '# 主线进度：'+dataset+'\n\nNSI主分析保留；新增SNuDD外部源变体，实际前向/统计接入已核验，科学接受NOT_REVIEWED。\n\n```json\n'+json.dumps(p, ensure_ascii=False, indent=2)+'\n```\n')
        managed(run / 'README.md', '## 外部传播源：SNuDD v3.4\n\n'+link(run / 'README.md', run / 'SNUDD_SOURCE_BRANCH.json', '独立源变体与全部阶段')+' · '+link(run / 'README.md', FILE, '逐数据新onboarding')+' · '+link(run / 'README.md', OUT / 'README.md', '真实基准')+'。旧主分析保留；实际接入不代替科学结果接受。')
        records[family] = {'revision': p['revision'], 'source_variant': BRANCH, 'parent_analysis': p['current_analysis'], 'reports': phases}
    return records


def navigation(qa):
    owners = ['README.md', 'tools/README.md', 'tests/README.md', 'outputs/README.md', 'docs/experiments/README.md',
              'docs/experiments/LATEST_EXPERIMENTS.md', 'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md', rel(DOC / 'README.md')]
    for name in owners:
        p = ROOT / name
        managed(p, '## 太阳传播可选扩展：SNuDD v3.4\n\n'+link(p, FILE, '已安装并接入主线的新onboarding')+' · '+link(p, ROOT / 'extensions/solar_rho_snudd/README.md', '独立安装/API')+' · '+link(p, OUT / 'README.md', '三样本实际对照')+'。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。')
    reconstruction = ROOT.parent / '重构/README.md'
    managed(reconstruction, '## SNuDD外部传播接入\n\n'+link(reconstruction, PLAN, '已实施修订方案')+' · '+link(reconstruction, FILE, '主线新v3.4完整读本')+' · '+link(reconstruction, OUT / 'README.md', '实际结果')+'。')
    ignore = ROOT / '.gitignore'
    old = ignore.read_text(encoding='utf8')
    if '# Optional external propagation installations' not in old:
        put(ignore, old.rstrip()+'\n\n# Optional external propagation installations\n/.externals/\n/.venvs/\n/outputs/external/solar_rho_snudd/**/rho_cache/\n')
    ext = ROOT / 'extensions/solar_rho_snudd'
    p = ext / 'README.md'
    put(p, '# SNuDD：可移除的外部太阳传播源\n\n'+link(p, FILE, '新v3.4物理/数值/来源读本')+' · '+link(p, OUT / 'README.md', '已经执行的主线基准')+' · '+link(p, CARD, '实际来源/版本/参数卡')+'\n\n'
        '只有export_rho.py在独立解释器内import snudd；其他文件由主项目解释器使用，不把SNuDD加入根依赖。完整ρ文件经验证后进入显式load_snudd→标准Runtime。旧入口不受影响。\n\n'
        '| 文件 | 职责 |\n|---|---|\n'+''.join('| '+link(p, ext / name, name)+' | '+meaning+' |\n' for name, meaning in [
            ('export_rho.py', 'NP-only参数映射、独立太阳传播、完整ρ和诊断'), ('protocol.py', '可版本化文件身份、物理性/内容/坐标核验'),
            ('state.py', '子进程与精确子网格状态提供器'), ('experiment.py', '新Definition/scoped Catalog/PreparedExperiment；源与Fast状态双绑定'),
            ('run_with_rho.py', '实际三样本Slow/Fast/统计与旧源对照'), ('prepare.py', '来源卡与锁定依赖生成/检查'),
            ('snudd.input.json', '实际输入、标准文献、固定commit和哈希'), ('requirements.lock.txt', '实际独立环境版本')])+
        '\n\n## 安装（当前已经完成）\n\n从Gitup01根目录；选择已有Python3.11解释器。先固定commit，再安装。\n\n```powershell\ngit clone --no-checkout https://github.com/SNuDD/SNuDD.git .externals/SNuDD\ngit -C .externals/SNuDD checkout --detach '+PIN+'\npython -m venv .venvs/snudd\n.venvs/snudd/Scripts/python.exe -m pip install --index-url https://pypi.org/simple -e .externals/SNuDD packaging==26.3\n.venvs/snudd/Scripts/python.exe -m pip check\n```\n\n'
        '精确重装应按requirements.lock.txt中固定的NumPy/SciPy/Pandas等版本安装，保留安装报告中的轮子hash。上游packaging依赖漏声明，已明确补齐。使用主项目Python运行tools/run_solar_b8_snudd_benchmark.py，工作进程会自动使用.venvs/snudd。\n\n'
        '原cevns_pyeft/物理源码和data/只读；此扩展不进入根发行包的强制依赖。删除/移走扩展、独立环境与checkout后，原程序仍可运行；移除时同步主线导航。上游GPL-3.0 LICENSE保留在.externals/SNuDD。\n')
    put(ROOT / 'extensions/README.md', '# 显式可选扩展\n\n'+link(ROOT / 'extensions/README.md', p, 'solar_rho_snudd：已安装的太阳传播源')+'。基础包不自动发现或导入扩展；扩展通过独立入口及数值文件契约使用原Runtime。\n')
    put(ROOT / '.externals/README.md', '# 独立上游源码\n\nSNuDD固定commit `'+PIN+'`，通过官方Git仓库下载，保持上游源码和LICENSE；父目录不进入主发行包。安装/消费者见'+link(ROOT / '.externals/README.md', p, '扩展README')+'。\n')
    put(ROOT / '.venvs/README.md', '# 可选扩展独立环境\n\n实际环境为snudd/，Python3.11.15。安装版本/完整来源见'+link(ROOT / '.venvs/README.md', p, 'SNuDD扩展')+'。原主项目解释器及依赖不变。\n')
    put(ROOT / 'outputs/external/README.md', '# 外部模块实际计算\n\n'+link(ROOT / 'outputs/external/README.md', OUT.parent / 'README.md', 'SNuDD太阳传播源')+'。外部安装、文件契约与实际主线结果分别保存；旧太阳输出不覆盖。\n')
    put(OUT.parent / 'README.md', '# SNuDD太阳传播接入\n\n'+link(OUT.parent / 'README.md', OUT / 'README.md', '20261112_run1实际三样本结果')+' · '+link(OUT.parent / 'README.md', FILE, '新v3.4 onboarding')+'。rho_cache/是按参数和能量内容寻址的完整矩阵包，不是实验观测。\n')
    p = OUT / 'README.md'
    put(p, '# SNuDD外部传播：实际主线验收\n\n'+link(p, FILE, '完整新onboarding')+' · '+link(p, CARD, '来源与配置')+' · [结果](RESULTS.json)\n\n'
        '**已完成独立安装、完整ρ导出、标准Runtime接入及三样本点基准。** 原物理源码与数据未改；新的核折叠数组与旧数组逐位相同。SM信号不变，非零NSI的变化来自传播输入。\n\n'
        '![实际Pee与事件数对照](snudd_vs_local.png)\n\n'
        '| 文件/目录 | 实际内容 |\n|---|---|\n'+''.join('| '+link(p, OUT / name, name)+' | '+meaning+' |\n' for name, meaning in [
            ('RESULTS.json', '五个参数点的三信号、联合χ²、尾段上下界与传播诊断'), ('FORWARD_VALIDATION.json', '9个真实Slow/Fast点、独立加密和核折叠不变'),
            ('ENERGY_CONTRACT.json', 'Slow/Fast/诊断点的实际并集与精确取子集合同'), ('QA.json', '测试、安装、原文件保护与接入审计'),
            ('tests.xml', '本轮实际测试'), ('source_evidence/INSTALLATION.json', '固定源码/实际依赖/原数据hash'),
            ('INSTALL_REPORT.json', '官方PyPI的安装包URL与hash'), ('INSTALL_PACKAGING_REPORT.json', '补齐上游漏依赖的记录'),
            ('rho_cache/', '每hash子目录含完整rho.npz和manifest.json；参数/能量/版本绑定'), ('kernels/', '新物理身份的三个独立kernel；旧缓存不能混用'),
            ('PROTECTED_BASELINE.json', '本轮保护文件逐项hash'), ('DELIVERY_FILES.json', '代码/文档/元数据的交付指纹'),
            ('FILE_LIFECYCLE.json', '文件归属、README、上级导航与消费者'), ('READABILITY_VALIDATION.json', '公式、实际目录跳转、图片与窄屏检查'),
            ('LINK_VALIDATION.json', '本次文档本地链接检查'), ('preview/README.md', '实际渲染截图')])+
        '\n\n仅传播输入替换，仍为有效两味近似。X尾数据/缺124、126核表/原文与转录认证限制保留。此次未生成新的完整Fig4区域；科学接受NOT_REVIEWED。\n')
    for directory, body in [('rho_cache', '每个64位hash子目录保存一个实际NSI参数点/能量网格的rho.npz＋manifest.json；完整复矩阵、Pee、版本和物理性/绝热诊断全部保留。由state.py精确取子网格，不插值或静默修复。'),
                            ('kernels', '三个新身份的energy-resolved核；仅与本次PreparedExperiment指纹匹配。核数、源强、效率和截面折叠数组与旧版本逐位相同。'),
                            ('source_evidence', 'INSTALLATION.json拥有固定上游和环境信息；snudd_profile_diagnostic.txt是实际函数的1000×4诊断，不替代原B16数据。')]:
        p = OUT / directory / 'README.md'
        put(p, '# '+directory+'\n\n'+body+'\n\n'+link(p, OUT / 'README.md', '返回运行结果')+' · '+link(p, FILE, '完整输入和来源')+'\n')
    for sample in ['PandaX_paired', 'PandaX_US2', 'XENONnT']:
        p = OUT / sample / 'README.md'
        put(p, '# '+sample+'实际装配\n\n[PREPARED_MODEL.json](PREPARED_MODEL.json)保存标准Runtime的实际源、靶、效率、截面、身份及所有来源hash。事件数和验证见'+link(p, OUT / 'RESULTS.json', '联合点结果')+'。\n')
    return owners


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    qa = audit()
    if args.write:
        save(OUT / 'QA.json', qa)
        for path, text in generated().items():
            put(path, text)
        qa['canonical'] = register(qa)
        owners = navigation(qa)
        save(OUT / 'QA.json', qa)
        mapping = {name: [rel(FILE)] for name in owners}
        mapping['extensions/README.md'] = ['extensions/__init__.py', 'extensions/solar_rho_snudd/']
        mapping['extensions/solar_rho_snudd/README.md'] = [rel(f) for f in CARD.parent.iterdir() if f.is_file() and f.name != 'README.md']
        mapping['tools/README.md'] += ['tools/run_solar_b8_snudd_benchmark.py', 'tools/finalize_solar_b8_snudd.py', 'tools/validate_solar_b8_snudd.mjs']
        mapping['tests/README.md'] += ['tests/test_solar_snudd.py']
        mapping[rel(OUT / 'README.md')] = [rel(f) for f in OUT.iterdir() if f.name != 'README.md']
        mapping[rel(OUT / 'rho_cache/README.md')] = ['rho_cache/<content_key>/rho.npz', 'rho_cache/<content_key>/manifest.json']
        for fam, ds, _ in RUNS:
            run = ROOT / f'workflows/cevns-pyeft/runs/{fam}/{ds}'
            mapping[rel(run / 'README.md')] = [rel(run / 'SNUDD_SOURCE_BRANCH.json')]+list(qa['canonical'][fam]['reports'].values())
        save(OUT / 'FILE_LIFECYCLE.json', {'date': '2026-11-12', 'file_owners': mapping, 'external_original_plan': str(PLAN),
            'backup': 'backup/solar-snudd-20261112-01/MANIFEST.json', 'existing_core_and_data': 'no modifications', 'default_global_registration': False, 'git_commit_or_push': False})
        delivery = {}
        for path in [*CARD.parent.glob('*.py'), CARD, CARD.parent / 'requirements.lock.txt', ROOT / 'extensions/__init__.py',
                     ROOT / 'tools/run_solar_b8_snudd_benchmark.py', ROOT / 'tools/finalize_solar_b8_snudd.py', ROOT / 'tools/validate_solar_b8_snudd.mjs', ROOT / 'tests/test_solar_snudd.py', FILE]:
            delivery[rel(path)] = sha(path)
            if path.suffix == '.py':
                destination = OUT / 'source' / path.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and sha(destination) != sha(path):
                    raise ValueError('immutable delivery source differs: '+rel(path))
                if not destination.exists():
                    shutil.copyfile(path, destination)
        put(OUT / 'source/README.md', '# 实际适配器与工具源码快照\n\n本轮代码逐文件保存在原相对路径，hash见[DELIVERY_FILES.json](../DELIVERY_FILES.json)。不作为新物理输入；上游原件及LICENSE仍在固定checkout，未改写。\n')
        save(OUT / 'DELIVERY_FILES.json', delivery)
    else:
        for path, text in generated().items():
            if path.read_text(encoding='utf8') != text:
                raise ValueError('stale source-generated document: '+str(path))
        for name, h in read(OUT / 'DELIVERY_FILES.json').items():
            if sha(ROOT / name) != h:
                raise ValueError('delivery content changed: '+name)
        for family, ds, _ in RUNS:
            run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{ds}'
            state = json.loads(re.search(r'```json\s*\n(.*?)\n```', (run / '00_MIGRATION_PROGRESS.md').read_text(encoding='utf8'), re.S)[1])
            if state['current_source_variant'] != BRANCH or BRANCH not in state['parallel_analyses']:
                raise ValueError('mainline external source branch missing')
    print(json.dumps({'protected_files': qa['protected_files'], 'tests_passed': qa['tests_passed'], 'status': qa['status'], 'mode': 'write' if args.write else 'check'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
