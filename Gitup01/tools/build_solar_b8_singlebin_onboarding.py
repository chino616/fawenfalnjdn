"""Generate/check v3.2.1 from the independent card and actual SM result.

Original user v3.2 and multibin v3.1 are never rewritten. Default --check is
read-only; --write creates missing documents and refuses different existing ones.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA=ROOT/'data/benchmarks/solar_b8_singlebin_2601_19883'
DOC=ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883'
OUT=ROOT/'outputs/solar_b8_singlebin/20261111_response_run2'
ORIGINAL=ROOT.parent/'重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2'


def read(path):return json.loads(path.read_text(encoding='utf8'))
def link(origin,target,label):return '['+label+'](<'+os.path.relpath(target,origin.parent).replace('\\','/')+'>)'
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+'|'.join('---' for _ in headers)+'|\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
def section(anchor,title,body):return f'\n<a id="{anchor}"></a>\n\n## {title}\n\n{body}\n\n[返回目录](#toc)\n'


def generated():
    from cevns_pyeft.nuclear.response import ResponseDB
    card=read(DATA/'analysis.input.json'); stats=read(DATA/'fitted_yields.json'); summary=read(OUT/'BENCHMARK_SUMMARY.json')
    records={r['sample']:r for r in summary['results']}
    file=DOC/'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md'
    ln=lambda target,label:link(file,target,label)
    source=np.loadtxt(DATA/'b8_source.txt'); iso=np.loadtxt(DATA/'xe_isotopes.txt')
    mean=float(iso[:,1]@iso[:,2]); db=ResponseDB(ROOT/'data/responses/responses_all.json')
    toc=[('review','v3.2审查结论'),('isolation','两条主线流程与文件隔离'),('source','Source：通量与谱形'),('target','Target与原子核Response'),('detector','Detector：总接受度'),('prediction','Prediction：本次积分'),('statistics','Statistics：信号拟合量'),('results','实际标准模型结果'),('workflow','阶段与代码对应'),('handoff','下一步与剩余限制'),('references','标准参考文献')]
    text='# 太阳⁸B单 bin onboarding v3.2.1：主线执行修订稿（新版本）\n\n'
    text+='**2026-11-11。已接入原 Gitup01 主线并实际运行；本版与多 bin v3.1 并列，不替换它。** 原 v3.2 是可审阅规范，不能直接作为 Runtime 输入；本版补齐 paired 效率、核实 XENONnT 2024 图线并给出实际计算。主线代码接入完成不等于论文等价性或科学结果获批；XENONnT尾段仍缺数值依据，保持修订稿。\n\n'
    text+=ln(ORIGINAL/'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.md','用户原稿（保留）')+' · '+ln(DATA/'analysis.input.json','单bin实际物理参数/来源')+' · '+ln(DATA/'fitted_yields.json','独立统计数据')+' · '+ln(OUT/'BENCHMARK_SUMMARY.json','实际计算记录')+' · '+ln(ROOT/'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md','多bin v3.1')+'\n\n<a id="toc"></a>\n\n## 目录\n\n'
    text+='\n'.join(f'- [{title}](#{anchor})' for anchor,title in toc)+'\n'
    text+=section('review','v3.2审查结论',table(['项目','结论与本次处理'],[
        ['物理与统计定义','基本正确：R1 PDF p19 Eq.(84)、p20 Eqs.(87),(88)，三个信号产额single-bin、三个独立12% pull；未采用R4共享pull。'],
        ['可否直接运行','原稿明确DOCUMENTED_SPEC_NOT_EXECUTED；普通YAML不是正式三文件Package。现由独立JSON card及显式loader接入标准Runtime。'],
        ['PandaX paired','原稿MISSING已更新：R2 PDF p3 Fig.1黑实线原生矢量，52×2；曝光采用原实验1.20 t·yr，R5 Table II的1.25保留冲突。'],
        ['PandaX US2','99×2总效率独立重提取；0.3–3积分，不再裁平均Ne=4–8；旧25.86不能当新单bin预测。'],
        ['XENONnT','原稿“未提供”已过时：R3 v2 Fig.1原生黑线40点已取得；仅到约2.77，末段到3仍缺。旧三箱基底相加不替代该效率。'],
        ['通量','5.46e6来自R5 Eq.(29)，是R1所引资料下的显式选择；R1未重印此数。R4的5.16e6与SM参考值只作外部比较。'],
        ['误差与阶段','采用原稿指定R4 Table II取整误差1.3/28/3.95；与R1印出的37.1%/37.3%/36.9%有舍入差异。Statistics属P09，P08属Fast。'],
        ['链接与版本','新版本修正原稿相对v3.1失效链接；旧原稿、原多bin数据/模型/冻结结果保持原字节。'],
    ]))
    text+=section('isolation','两条主线流程与文件隔离',table(['层','多 bin：既有方案','单 bin：本次方案'],[
        ['物理目标','2411.11749v1 Fig.1类型的Ne/cS2谱','2601.19883v2 Eq.87总信号、Eq.88近似χ²'],
        ['实验输入',ln(ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2/README.md','原PandaX Package')+' / '+ln(ROOT/'data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md','原XENON Package'),ln(DATA/'README.md','独立单bin目录')],
        ['探测器处理','PandaX Qy平均映射8箱；XENONnT早期YBe接受概率3箱','真反冲T×Total效率积分；paired/US2/X三个独立样本'],
        ['数据语义','逐箱候选D_i、背景B_i作为谱比较资料','3.5±1.3、75±28、10.7±3.95：实验拟合信号；无显式背景项'],
        ['计算模块',ln(ROOT/'cevns_pyeft/experiments/solar_nuclear.py','solar_nuclear')+' + solar_mean_map/solar_b8',ln(ROOT/'cevns_pyeft/experiments/solar_singlebin.py','solar_singlebin')],
        ['入口',ln(ROOT/'tools/run_solar_b8_multibin_benchmark.py','run_solar_b8_multibin_benchmark.py'),ln(ROOT/'tools/run_solar_b8_singlebin_benchmark.py','run_solar_b8_singlebin_benchmark.py')],
        ['结果根',ln(ROOT/'outputs/solar_b8_sm/README.md','outputs/solar_b8_sm/'),ln(ROOT/'outputs/solar_b8_singlebin/README.md','outputs/solar_b8_singlebin/')],
    ])+'\n\n只共享实验无关的核表、SM匹配/粒子响应/截面及通用Runtime。单bin不导入旧solar_b8、solar_mean_map、solar_nuclear，不读取旧NPZ、Qy、逐箱D/B，不加载旧Fast缓存。资源allowlist、analysis/dataset/observation指纹及维度检查拒绝交叉统计。兼容旧入口不带analysis仍走历史多bin；新任务使用上表明确入口。')
    text+=section('source','Source：通量与谱形',r'定义 $d\phi/dE_\nu=\Phi_{8B} f_{8B}(E_\nu)$。谱形与总通量各乘一次；采用单位迹的味等价入射态，SM味普适，不乘额外三倍，不需要逐味MSW表。此处定义对应R1 Eq.(84)，谱形数据来自R6，通量选择来自R5。'+'\n\n'+table(['输入','实际数值/数组','单位','数值文件与直接出处','核验范围'],[
        ['总通量','5.46×10⁶','cm⁻² s⁻¹',ln(DATA/'analysis.input.json','physics.flux')+'；[R5] PDF p5 Eq.(29)','核对原式；未按拟合结果调整'],
        ['谱形',f'829×2；E={source[0,0]:g}–{source[-1,0]:g}；梯形积分={np.trapezoid(source[:,1],source[:,0]):.12g}','MeV, MeV⁻¹',ln(DATA/'b8_source.txt','源谱')+'；[R6] 官网b8spectrum前两列','原829点提取；保留原精度，不再归一'],
        ['插值与边界','分段线性；表外0；积分含原谱节点','—','[R6]网格 + 项目数值选择；SourceSpectrum及rates.recoil','显式来源/支撑及网格加密检验'],
        ['弱混合角','sin²θW=0.23857','1',ln(DATA/'analysis.input.json','physics.sin2thetaW')+'；[R9]沿用项目SM点','明确项目输入，不冒称R1印出的默认值'],
        ['时间换算','31557600=365.25×86400','s/yr','[R10] Julian年单位约定','仅作单位换算；曝光未再乘独立活时间'],
    ])+'\n\n[R6] '+card['references']['R6']['citation']+'\n\n[R5] '+card['references']['R5']['citation']+' PDF p5 Eq.(29)。')
    targets=[];核=[]
    for number,mass,fraction in iso:
        key='Xe'+str(int(number));available=key in card['physics']['isotope_keys']
        targets.append([key,f'{fraction:.6g}',f'{mass:.12g}',f'{1e6*6.02214076e23*fraction/mean:.9g}', '已读核表' if available else 'MISSING：不计、不补KN、不重归一'])
        if available:
            resp=db.get(key);m=np.asarray(resp.responses['M'])
            核.append([key,resp.basic['J'],f"{resp.basic['b']:.9g}",str(list(m.shape)),f'{m[0,0,0]:.9g}, {m[0,1,0]:.9g}, {m[1,1,0]:.9g}'])
    text+=section('target','Target与原子核Response',r'核数由 $n_A^{(1t)}=10^6 N_A\eta_A/\sum_B\eta_Bm_B^{\rm atom}$ 推导；分母使用完整九行，质量单位g/mol。输入来自[R7]；代数换算位于build_targets。振幅与运动学统一采用 $m_A=A\,m_u$；核数仍用原子质量。'+f' 九行平均摩尔质量={mean:.12g} g/mol；可用七核素原数丰度99.8158%，保留缺失的0.1842%。\n\n'+table(['核素','数丰度','原子质量u','每吨核数（推导）','核响应可用性'],targets)+'\n\n'+ln(DATA/'xe_isotopes.txt','完整9×3 NIST输入')+'；[R7] '+card['references']['R7']['citation']+'\n\n'+table(['key','J','b [GeV⁻¹]','M数组shape','M的pp,pn,nn常数项'],核)+'\n\n核表实际文件：'+ln(ROOT/'data/responses/responses_all.json','responses_all.json')+'，SHA256 `'+card['physics']['nuclear_sha256']+'`。采用已有ResponseDB/Li2026的np基底(p,n)和多项式约定，全部已实现通道进入SM振幅；不乘KN/Helm/额外自旋因子。共享理论公式只在原理论模块维护，本分析通过'+ln(ROOT/'cevns_pyeft/theory/li2026/sm_quadratic.py','SMQuadraticInteraction')+'委托'+ln(ROOT/'cevns_pyeft/theory/li2026/adapter.py','Li2026LegacyInteraction')+'，仅做精确能量二次式向量化。\n\n[R8] '+card['references']['R8']['citation']+' **本地数值可用、直接采用获授权；外部原始作者版本和转换认证仍UNRESOLVED。** 此限制不被内部格式/收敛PASS消除。')
    detector_rows=[]
    for sample,config in card['samples'].items():
        name=config['efficiency'];a=np.loadtxt(DATA/name)
        detector_rows.append([sample,str(list(a.shape)),f'{a[0,0]:.12g}–{a[-1,0]:.12g}',f'{a[0,1]:.9g} / {a[-1,1]:.9g}',ln(DATA/name,name),config['source']])
    text+=section('detector','Detector：总接受度',table(['样本','shape','表内T [keVnr]','首/末ε [1]','数值文件','直接原文定位'],detector_rows)+'\n\nPandaX两线由[R2] PDF p3 Fig.1原生矢量重新提取，横轴线性/纵轴log；图边界交点在原PDF坐标求出，数值文件端点明确为0.3/1.1/3。转为数值后分段线性插值ε(T)，是一项项目数值选择；独立提取的US2 99点与旧原表在其写入精度内一致。Total已含ROI、选择和重建，均只施加一次。\n\nXENONnT用[R3] **2408.02877v2 PDF p4 Fig.1黑色combined**，40×3第三列保留可见标记；低能几段在图框下裁掉，但原生PDF数值路径存在，不能称其为可见曲线逐点核实。末点约2.77 keV，**2.77–3 keV的ε(T)=MISSING**。主结果积分到末点并以0≤ε≤1给未知尾段的严格区间；不静默延伸。平坦延伸仅为单列的项目敏感性估计。\n\n这里的Detector接受度不是原子核Response W，也不是完整重建概率矩阵。按本单bin目标只需总效率；Qy、二维S1/S2 kernel及逐箱迁移不属于这条简化积分的输入。\n\n[R2] '+card['references']['R2']['citation']+'\n\n[R3] '+card['references']['R3']['citation'])
    text+=section('prediction','Prediction：本次积分',r'''采用[R1] PDF p19 Eq.(84)、p20 Eq.(87)，将曝光显式移出通量，并按核素求和：

$$
S_k=\mathcal E_k\sum_A n_A^{(1t)}\,t_{\rm yr}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\epsilon_k(T)
\int_{E_{\min,A}(T)}^{E_{\max}}dE_\nu\,
\Phi_{8B}f_{8B}(E_\nu)\frac{d\sigma_A^{\rm SM}}{dT}.
$$

这里 $\mathcal E_k$ 数值单位t·yr，$n_A^{(1t)}$ 是每吨核数，$t_{\rm yr}$ 是s/yr；其余单位依次keV、MeV、cm⁻²s⁻¹MeV⁻¹、cm²/keV，结果为事件。$E_{\min,A}$、截面与核质量均由共享接口提供。本式的显式曝光和核素求和是对R1写法的单位展开，不新增物理归一化。
'''+'\n'+table(['样本','T积分 [keVnr]','曝光 [t·yr]','直接出处与选择'],[[k,str(v['T_bounds_keVnr']),v['exposure_tyr'],v['source']] for k,v in card['samples'].items()])+r'''

未知XENONnT尾段满足下式。两端来自本次未加效率反冲谱积分，是数值推导的界，不是对缺失实验数据的猜测：

$$
S_{\rm known}\le S_{\rm full}\le S_{\rm known}+\mathcal E\sum_A n_A^{(1t)}t_{\rm yr}\int_{T_*}^{3\,\mathrm{keV}}dT\int dE_\nu\,\Phi f\,d\sigma_A/dT.
$$

执行顺序：源谱×截面 → 每核反冲率 → 原核数 → 总接受度 → 曝光 → 单信号计数。无 $c_i$，无拟合信号标定，无额外ROI窗，无源通量重拟合。每一数值输出都记录实际资源、实现哈希及Runtime物理/analysis指纹。
''')
    stat_rows=[]
    for sample,row in stats['samples'].items():
        stat_rows.append([sample,row['D'],row['sigma_stat'],row['pull_sigma'],row['source']])
    text+=section('statistics','Statistics：信号拟合量',r'''使用[R1] PDF p20 Eq.(88)：

$$
\chi^2=\sum_k\min_{a_k}\left\{\frac{[D_k-(1+a_k)S_k]^2}{\sigma_k^2}+\frac{a_k^2}{0.12^2}\right\}.
$$

$D_k$是实验多维拟合获得的**信号产额**；$\sigma_k$是其统计误差，非原始候选的Poisson误差；每个样本独立一个归一化pull。背景已在实验信号提取中处理，不能再加一次背景项或将3.5等信号量当原始Poisson计数。
'''+'\n'+table(['样本','D [events]','σstat [events]','σa [1]','原文位置'],stat_rows)+r'''

具体数据文件为LINK_STATS。原稿使用[R4] PDF p13 Table II的取整误差；[R1]印出的paired/US2/X百分数37.1%/37.3%/36.9%分别给1.2985/27.975/3.9483事例，差别仅舍入，当前仍明确沿用原稿1.3/28/3.95。

解析profile由对Eq.(88)求导得到，非另一个外部输入：

$$
a_* = \frac{0.12^2 S(D-S)}{\sigma^2+0.12^2 S^2},\qquad
\chi^2_{\rm prof}=\frac{(D-S)^2}{\sigma^2+0.12^2S^2}.
$$

程序独立数值最小化检验此解析式。未作参数扫描、最佳拟合搜索或置信区间。XENONnT部分积分由统计器拒绝作为完整点预测；只计算缺失尾数据导致的χ²范围。使用平坦延伸时，analysis身份与物理指纹独立变化，结果明确为项目假设。
'''.replace('LINK_STATS',ln(DATA/'fitted_yields.json','fitted_yields.json'))+'\n\n[R1] '+card['references']['R1']['citation']+'\n\n[R4] '+card['references']['R4']['citation']+' 原文Table II与Eq.(E8)分别核对；共享pull未采用。')
    result_rows=[]
    for sample,row in records.items():
        bounds=row['full_interval_events']; result_rows.append([sample,f"{row['counts'][0]:.9f}" if row['complete_prediction'] else f'{bounds[0]:.9f}–{bounds[1]:.9f}',f"{row['fitted_signal_data']['D']:g} ± {row['fitted_signal_data']['sigma_stat']:g}",f"{row['statistics']['chi2']:.9g}" if row['statistics'] else '部分积分禁入完整χ²',row['claim']])
    x=records['XENONnT'];flat=x['flat_tail_sensitivity']
    result_body=table(['样本','SM信号 [events]','实验拟合信号 [events]','profile χ²','性质'],result_rows)
    result_body+=f"\n\nXENONnT平坦尾段敏感性：末点ε={flat['epsilon_tail']:.12g}，完整假设积分={flat['events']:.9f}，χ²={flat['chi2']:.9g}。**此点采用项目平坦尾假设，不是官方数据。** 三样本固定SM点χ²的严格范围为{summary['chi2_range_due_only_to_unknown_tail']}；由于缺尾数据，主记录`joint_chi2=null`，没有宣称完整点χ²。采用平坦尾假设时总χ²={summary['project_flat_tail_sensitivity_joint_chi2']:.9g}。\n\n"
    result_body+='三样本各做反冲201→401→801、随后中微子120→480的独立加密；保留源谱与效率原节点。收敛检查同时覆盖信号计数和区间两端，要求max(2e−4 events,0.2%)；不是论文等价性检查。原子核表读取、截面委托、分核素求和、独立曝光及所有实施版本均见'+ln(OUT/'BENCHMARK_SUMMARY.json','完整结果')+'。\n\n'
    result_body+='[R4] Table II在5.16e6通量下列2.4/44.3/11.2，且采用自己的核物理与共享pull；它们仅是外部比较量，未作为校准、源重缩放或程序参考数组。\n\n'
    result_body+='![](<'+os.path.relpath(OUT/'singlebin_SM_comparison.png',file.parent).replace('\\','/')+'>)\n\n黑点为实验拟合信号及所采用统计误差；蓝点为独立SM积分；X蓝竖段为未知尾段区间；紫空心点仅为平坦尾段敏感性。\n\n![](<'+os.path.relpath(OUT/'singlebin_recoil_diagnostics.png',file.parent).replace('\\','/')+'>)\n\n反冲密度是积分诊断，不是重建Ne/cS2直方图。'
    text+=section('results','实际标准模型结果',result_body)
    mapping=[['P01','sample/analysis/observation分离','load_singlebin；独立scoped catalog，不改全局默认IDs'],['P02','天然Xe、核数、曝光','build_targets；SingleBinPreparation；R2/R3/R7'],['P03','源谱与绝对通量','SourceSpectrum；UniversalState；R5/R6'],['P04–P05','原子核W→振幅→截面','SMQuadraticInteraction委托Li2026LegacyInteraction；无KN主预测'],['P06','只采用总ROI效率','TotalAcceptance；不读取Qy/迁移/旧basis'],['P07','重新计算单bin信号','SingleBinExecutor → rates.recoil.integrate_recoil_yield'],['P08','Fast未申请','NOT_REQUESTED；不导入旧cache'],['P09','独立拟合信号Gaussian','statistics.solar_singlebin.profile/evaluate；Runtime.evaluate_experiment'],['P10','来源、隔离、收敛、回归','test_solar_singlebin；科学接受NOT_REVIEWED，缺尾/外部认证保持可见']]
    text+=section('workflow','阶段与代码对应',table(['阶段','物理职责','程序中位置/原文'],mapping)+'\n\n实际源码：'+ln(ROOT/'cevns_pyeft/experiments/solar_singlebin.py','source/target/detector/executor/loader（含onboarding注释）')+' · '+ln(ROOT/'cevns_pyeft/statistics/solar_singlebin.py','单bin统计')+' · '+ln(ROOT/'cevns_pyeft/theory/li2026/sm_quadratic.py','核Response截面委托')+' · '+ln(ROOT/'tests/test_solar_singlebin.py','隔离与数值检验')+'。\n\n从Gitup01根目录分别运行（新输出目录，禁止覆盖）：\n\n```powershell\npython -B tools/run_solar_b8_singlebin_benchmark.py --output outputs/solar_b8_singlebin/repeat_new\npython -B tools/run_solar_b8_multibin_benchmark.py --output outputs/solar_b8_sm/multibin_repeat_new\n```\n\n兼容路由可用`run_solar_b8_sm_benchmark.py --analysis singlebin ...`或`--analysis multibin ...`。两者各自的入口、实验输入、统计量、输出和指纹仍完全分离。')
    text+=section('handoff','下一步与剩余限制',table(['项目','状态','影响与下一步'],[
        ['主线SM单bin计算','已执行','PandaX两通道完整；XENONnT有严谨范围与单列的尾段假设敏感性'],
        ['XENONnT约2.77–3 keV接受度','MISSING','取得2024黑combined曲线完整数值或有依据的低能模型；仅阻断无假设的完整点预测/完整联合χ²'],
        ['Xe124/Xe126核响应','MISSING','七核素结果不重归一；若需100%天然Xe，补独立核表，不以KN替代'],
        ['已有核表外部认证','UNRESOLVED','按用户选择采用本地表；不阻断本地计算，但不能宣称外部原始发布与转换等价已认证'],
        ['官方全响应/官方likelihood','本次未请求','本方法是R1单bin近似，不替代原实验多维likelihood或旧多bin研究'],
        ['科学结果接受','NOT_REVIEWED','机器PASS只证明已记录的检验；未标FULLY_INTEGRATED/论文精确复现'],
    ])+'\n\n原稿与旧多bin保护哈希：'+ln(ORIGINAL/'_review/PROTECTED_BASELINE.json','PROTECTED_BASELINE')+'；逐文件归属与实测验收：'+ln(ROOT/'outputs/solar_b8_singlebin/20261111_validation/README.md','验证记录')+'。')
    refs=''
    for key,ref in card['references'].items():
        refs+=f'**[{key}]** {ref["citation"]}\n\n'
        if ref.get('url'):refs+=f'[{ref["url"]}]({ref["url"]}) · '
        if ref.get('file'):refs+=ln(ROOT/ref['file'],'本地原件')+' · '
        elif ref.get('direct_local_source'):refs+=ln(ROOT/ref['direct_local_source'],'直接采用的本地原表')+' · '
        refs+=ref['locator']+'。\n\n'
        if ref.get('sha256'):refs+='SHA256 `'+ref['sha256']+'`。\n\n'
    text+=section('references','标准参考文献',refs)
    outputs={file:text}
    readme=DOC/'README.md'
    outputs[readme]='# 太阳⁸B单 bin：主线 v3.2.1（新版本）\n\n**独立于多bin的计算与数据方案，已实际运行SM。** 完整读本是'+link(readme,file,'v3.2.1 onboarding')+'，含逐项实际输入、标准文献引用与原文位置、代码映射、结果及缺口。\n\n'+link(readme,OUT/'README.md','本次标准模型结果与图')+' · '+link(readme,DATA/'README.md','独立数据目录')+' · '+link(readme,ORIGINAL/'_review/ONBOARDING_REVIEW.md','原v3.2审查与修正')+'\n\n'+table(['文件','用途'],[['SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md','完整规范、来源和主线计算'],['PandaX4T.singlebin.physics.v3.2.1.md','paired/US2专属入口'],['XENONnT.singlebin.physics.v3.2.1.md','2024合并样本与尾域限制']])+'\n\n'+link(readme,readme.parent.parent/'README.md','上一级：并列分析导航')+'\n'
    for family,samples in [('PandaX4T',['PandaX_paired','PandaX_US2']),('XENONnT',['XENONnT'])]:
        path=DOC/(family+'.singlebin.physics.v3.2.1.md')
        outputs[path]=f'# {family}：单bin物理输入 v3.2.1（新版本/修订稿）\n\n'+link(path,file,'完整onboarding（逐数据来源、公式、核验和代码）')+' · '+link(path,DATA/'analysis.input.json','正式采用的单bin参数卡')+'\n\n'+table(['样本','曝光t·yr','T域keVnr','信号拟合D±σ','本次SM积分'],[[s,card['samples'][s]['exposure_tyr'],str(card['samples'][s]['T_bounds_keVnr']),str(stats['samples'][s]['D'])+'±'+str(stats['samples'][s]['sigma_stat']),str(records[s]['full_interval_events'])] for s in samples])+'\n\n总接受度直接来自'+('R2 Bo et al., PRL 133 (2024) 191001, arXiv:2407.10892v3 PDF p3 Fig.1；paired黑实线、US2黑虚线。' if family=='PandaX4T' else 'R3 Aprile et al., PRL 133 (2024) 191002, arXiv:2408.02877v2 PDF p4 Fig.1黑combined；约2.77–3keV的效率缺失，表中给无假设的完整积分界。')+'天然Xe、源谱与原子核Response及统计的标准引文和实际数值均在完整onboarding相应章节。未使用多bin逐箱数据/Qy，统计只用信号拟合量；无ci。科学接受NOT_REVIEWED。\n'
    review=ORIGINAL/'_review/ONBOARDING_REVIEW.md'
    outputs[review]='# 原v3.2审查：已接入主线单bin独立分支\n\n'+link(review,file,'新v3.2.1全文：审查表、修正与SM实际结果')+' · '+link(review,OUT/'README.md','主线计算和图')+'\n\n原六文件保留原字节。v3.2核心方法基本正确，但它不是可执行输入；paired数值缺失、X2024数据状态过时、X尾域缺失、P08/P09标签及相对链接须修正。新版本落实独立data/loader/executor/statistics/output；原多bin不变。\n\n'+link(review,review.parent/'PROTECTED_BASELINE.json','原稿及旧多bin保护基线')+'\n'
    entry=ORIGINAL/'README.md'
    outputs[entry]='# SOLAR B8 SINGLEBIN v3.2：原稿与主线修订\n\n本目录原六文件为用户提供的v3.2规范，原件保持不变；主线采用'+link(entry,file,'新版本v3.2.1')+'。\n\n'+link(entry,review,'审查与修正说明')+' · '+link(entry,OUT/'README.md','主线SM实际计算')+' · '+link(entry,entry.parent/'SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.md','v3.2原稿')+'\n'
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args();outputs=generated();bad=[]
    for path,expected in outputs.items():
        if path.exists():
            actual=path.read_text(encoding='utf8')
            # Navigation has later owners. Keep the frozen v3.2.1 body strict
            # while allowing explicit, separately maintained directory blocks.
            if path==DOC/'README.md':
                for marker in ('latest-analyses','solar-nsi-v33'):
                    actual=re.sub(r'\n*<!-- '+marker+r':start -->.*?<!-- '+marker+r':end -->\n*','\n',actual,flags=re.S)
                actual=actual.rstrip()+'\n';expected=expected.rstrip()+'\n'
            if actual!=expected:bad.append(str(path))
        elif args.write:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(expected,encoding='utf8')
        else:bad.append(str(path))
    if bad:raise SystemExit('missing/different documents (no existing files overwritten): '+str(bad))
    print(('Created/verified' if args.write else 'Checked'),len(outputs),'same-source documents')


if __name__=='__main__':main()
