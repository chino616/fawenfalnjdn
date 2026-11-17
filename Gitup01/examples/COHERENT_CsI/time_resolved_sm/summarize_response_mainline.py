"""Generate the RESPONSE run explanation from its own arrays and checks."""
from pathlib import Path
import argparse
import json
import os
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
CHANNELS=('M','SigmaPP','SigmaP','PhiPP','PhiPT','Delta','MPhiPP','SigmaPDelta')


def link(label,p,current):
    return '['+label+'](<'+os.path.relpath(p,current.parent).replace('\\','/')+'>)'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--sync-navigation',action='store_true',help='Explicitly update the two owning navigation documents')
    a=parser.parse_args();out=a.run_dir.resolve();current=out/'README.md'
    check=json.loads((out/'CHECKS.json').read_text('utf8'))
    with np.load(out/'channel_audit.npz') as f:z={k:f[k] for k in f.files}
    lines=['# CsI2021 原始RESPONSE主线计算（2026-11-17）','',
        '**本次仅使用原生SM/RESPONSE主线，不导入或调用KN计算代码。** 从`ExperimentModel → predict(backend="slow")`重新积分；另将同一振幅返回的核响应通道作有符号拆分，检查逐箱求和闭合。','',
        '[堆叠图PDF](Figure_RESPONSE_Stacked_Comparison.pdf) · [逐味/背景对照PDF](Figure_RESPONSE_Paper_Components.pdf) · [核响应通道PDF](Figure_RESPONSE_Channel_Contributions.pdf)','',
        '默认保留0ns、reference_window注量和raw中子；+75ns、full_support和prior_posteff分别为独立对照。堆叠图中子明确使用prior_posteff（零位移效率后18.4/5.6）；原始背景未覆盖。全部图使用PAPER_THEME v4，无斜线阴影，保留负残差和数据误差棒。','',
        '## 计数结果','',
        '| 注量口径 | 位移 | νμ | νe | 反νμ | SM总数 |','|---|---:|---:|---:|---:|---:|']
    for scope in ('reference_window','full_support'):
        for shift in (0,75):
            t=z[f'{scope}_{shift:+g}ns_target_flavor_counts'].sum(axis=(0,2,3))
            lines.append(f'| {scope} | {shift:+g}ns | {t[0]:.6f} | {t[1]:.6f} | {t[2]:.6f} | {sum(t):.9f} |')
    lines+=['','信号总数不包含BRN/NIN/SSB。reference_window与full_support使用相同数值η，是不同注量解释；q固定为零位移0–6μs分数，未把删除/q作为物理修正。341仅为不同模型/口径的论文SM参考，未用作调参目标。','',
        '## RESPONSE逐通道拆分','',
        '从现有`flavor_kernel_onebody_li2026(...).pieces`读取八个通道，使用公共相空间转换器的系数转换为截面。三点构造E²dσ/dT二次式、两点独立核验，再用主线相同能量积分和线谱处理；逐通道完成相同QF/Gamma/PE效率及时间折叠。未修改核表、系数匹配、振幅或相空间公式。','',
        '所有干涉项保留正负号，不把各通道当作独立非负概率。`M`指完整振幅M通道，不能等同此前教学P07的M+c1截断。`SigmaPDelta`在当前粒子响应公式中精确为零；存在相应核表不能使其自动产生非零贡献。','',
        '| 核响应通道 | 0ns参考窗有符号事件数 | 占完整信号百分比 |','|---|---:|---:|']
    totals=np.array(check['channel_totals_zero']);total=totals.sum()
    for name,value in zip(CHANNELS,totals):lines.append(f'| {name} | {value:.12f} | {100*value/total:.9f}% |')
    lines += [f'| 合计 | {total:.12f} | 100% |','',
        f"M以外通道合计 **{sum(totals[1:]):.12f}** 事件。时间前通道求和与独立原生Slow预测逐箱最大绝对差 **{check['channel_audit']['max_folded_bin_absolute_error']:.3g}** 事件。",'',
        '当前与论文显示曲线的数十事件总率差远大于M以外通道贡献。因而该差异不能主要归于遗漏这些小通道；下一步应在统一模型/参数口径后检查占主导的M响应、源注量和探测器折叠。此处数值闭合不能唯一证明M核表有误。','',
        '## 与论文图的逐味差异','',
        '参考来自此前已核验的COHERENT 2110.07730v2 Fig.1作者矢量图，原始几何与主论文内嵌图一致；本次只读取paper_*边缘及其误差，不读任何KN预测参与计算。','',
        '| 分量 | RESPONSE 0ns | RESPONSE +75ns | 论文PE投影曲线积分 |','|---|---:|---:|---:|']
    for k,name in enumerate(('νμ','νe','反νμ')):
        v0=z['reference_window_+0ns_target_flavor_counts'].sum(axis=(0,2,3))[k]
        v1=z['reference_window_+75ns_target_flavor_counts'].sum(axis=(0,2,3))[k]
        ref=z['paper_PE_component_events'][k].sum()
        lines.append(f'| {name} | {v0:.6f} | {v1:.6f} | {ref:.6f} |')
    lines += ['', '这些论文分量是最佳拟合模型显示，不是逐味独立测量。可见曲线积分约312.59，与正文306±20的差别保留；论文PE/time残差积分也不同。不从两个边缘反推作者99箱，不作逐味重标定。','',
        '## 16–20 PE具体差值','',
        '下表只比较信号分量，数值为RESPONSE−论文图，单位events/bin。','',
        '| 分量 | 0ns | +75ns |','|---|---:|---:|']
    for k,name in enumerate(('νμ','νe','反νμ')):
        ref=z['paper_PE_component_events'][k,3]
        a0=z['reference_window_+0ns_target_flavor_counts'].sum(axis=(0,3))[k,3]
        a1=z['reference_window_+75ns_target_flavor_counts'].sum(axis=(0,3))[k,3]
        lines.append(f'| {name} | {a0-ref:+.6f} | {a1-ref:+.6f} |')
    channel_focus=z['reference_window_+0ns_target_flavor_channel_counts'].sum(axis=(0,1,4))[:,3]
    lines += ['',f'该PE箱：完整RESPONSE信号 **{channel_focus.sum():.9f}**，M通道 **{channel_focus[0]:.9f}**，M以外合计 **{channel_focus[1:].sum():.9f}** 事件。', '',
        '## 实现、验证与来源边界','',
        '- '+link('run_response_mainline.py',ROOT.parent/'重构/20261118_CsI2021_onboarding_restart/retired_entries/run_response_mainline.py',current)+'：独立主线复算、同一时间前谱重折叠、99箱及投影导出。',
        '- '+link('response_decomposition.py',Path(__file__).with_name('response_decomposition.py'),current)+'：既有振幅通道的有符号诊断与闭合检查。',
        '- '+link('plot_response_mainline.py',Path(__file__).with_name('plot_response_mainline.py'),current)+'：三张v4图；逐味图不添加不存在的模型系统误差。',
        '- '+link('summarize_response_mainline.py',Path(__file__),current)+'：本说明生成器，所有表格来自本次数组。','',
        '完整512/960/256网格、PE步长0.0625、T≥2keVnr；原生总数/时间前PE谱与此前高网格结果一致。通道5点核验、核反冲谱求和、时间前PE求和及99箱求和分别检查。独立回读官方AC12事件重建SSB与计数协方差；协方差先投影后开方。输入核表/时间源/官方TXT/论文参考指纹在运行前后相同。','',
        '本地核表实际来自用户选定data/responses/responses_all.json，核素键Cs133/I、basis=np，全部采用系数见RESPONSE_TABLES.json。本次认证本地读取/折叠的数值闭合；外部作者生成等价仍未核实。解析DAR能谱×ROOT时间边缘的因子化保留，不声称完整ROOT联合源认证。当前反中微子沿用主线legacy_shared_kernel约定，本次未改变或验证新的反中微子螺旋度约定。','',
        '+75ns仅改善prompt时间形状，官方ROOT时钟/onset尚未取得。核表来源、作者最佳拟合参数及背景口径的差异不能由本次逐箱闭合排除。无likelihood拟合，无新物理默认参数选择。','',
        '## 文件归属与重跑','',
        '- native_prediction.npz/native_report.json：本次原生Slow结果，含能量折叠前时间谱、核反冲产额与归一化记录。',
        '- channel_audit.npz：核素×味×8响应通道×PE×time分量；4种信号时间/注量组合及两种中子口径、固定观测/协方差和论文边缘。',
        '- predictions_99bins.csv：8种信号/背景组合×99箱；projections.csv、scenario_totals.csv：各投影和总数。',
        '- energy_before_time.csv：Cs/I×三味×9PE时间前计数；channel_totals.csv和channel_projection_bins.csv为有符号通道贡献。',
        '- paper_component_differences.csv：0/+75ns信号逐味、逐PE/time箱的论文差值。',
        '- RESPONSE_TABLES.json：直接采用的完整Cs/I核表数值及SHA；VECTOR_EXTRACTION.json保留论文矢量提取证据。',
        '- CHECKS.json：数值/来源与图件验收，ARTIFACT_MANIFEST.json登记来源、代码和本目录文件。三张PDF及同名PNG/SVG、render_*.png、PAPER_THEME.json和captions.txt均由本说明管理。','',
        '从Gitup01根目录运行（numpy/scipy/matplotlib）：','',
        '```powershell',
        '# 旧计算入口已于2026-11-18撤出活动目录；本程序只整理历史结果。',
        'python -X utf8 -B examples/COHERENT_CsI/time_resolved_sm/summarize_response_mainline.py --run-dir outputs/csi2021_response_NEW',
        '```','',
        '首次运行拒绝已有目录；`--resume`仅恢复未完成检查点，不覆盖PASS结果。保留既有代码、旧图和原始数据；仅新增本主线诊断入口与结果，并同步示例README/实验METHODS导航。','',
        '[主线计算说明](../../examples/COHERENT_CsI/time_resolved_sm/README.md)']
    current.write_text('\n'.join(lines)+'\n',encoding='utf8')
    (out/'captions.txt').write_text('RESPONSE-native unfitted SM forward calculation for CsI2021. '
        'The primary calculation uses the existing native Slow interfaces and user-selected nuclear RESPONSE table, without importing KN calculations. '
        'Stacked plots use explicitly selected prior_posteff neutron controls; 0 ns is the default and +75 ns a diagnostic source delay. '
        'Source delays apply to signal and neutrons with fixed observer bins/efficiency and zero-shift denominators; SSB stays fixed. '
        'Paper curves/points/errors are verified vector-extracted Fig.1 marginals, not independently measured flavor samples. '
        'Local open-square errors use C/AC counting covariance only. Nuclear-response channel pieces are read from the existing amplitude, '
        'with signed interference retained and checked against full Slow counts. Full M is not the legacy M+c1 truncation. '
        'No fit, no flavor rescaling, no official clock-onset or model-equivalence certification.\n',encoding='utf8')
    if a.sync_navigation:
        raise SystemExit("Retired workflow: navigation is owned by the restarted onboarding")
        targets=[Path(__file__).with_name('README.md'),ROOT/'docs/experiments/COHERENT/CsI2021/time_resolved/METHODS.md']
        start='<!-- response-mainline-20261117:start -->';end='<!-- response-mainline-20261117:end -->'
        for target in targets:
            old=target.read_text('utf8')
            if start in old:
                lo=old.index(start);hi=old.index(end,lo)+len(end);old=old[:lo]+old[hi:]
            note='## 2026-11-17 RESPONSE主线继续计算\n\n'
            note+='主线完整RESPONSE重新积分，并新增8通道有符号拆分与逐层闭合检查。默认0ns/reference_window/raw保持；+75ns及prior_posteff为明确标注的独立诊断。\n\n'
            note+=link('结果、图与逐箱表',current,target)+' · '+link('独立主线入口',ROOT.parent/'重构/20261118_CsI2021_onboarding_restart/retired_entries/run_response_mainline.py',target)+' · '+link('通道拆分',Path(__file__).with_name('response_decomposition.py'),target)+' · '+link('绘图器',Path(__file__).with_name('plot_response_mainline.py'),target)+' · '+link('说明生成器',Path(__file__),target)+'。\n\n'
            note+=f'本次0ns信号353.465609事件；M以外合计{sum(totals[1:]):.9f}事件。新入口不导入KN计算代码；未改变共享振幅、核表或默认Runtime注册。'
            target.write_text(old.rstrip()+'\n\n'+start+'\n\n'+note+'\n\n'+end+'\n',encoding='utf8')
    print(current)


if __name__=='__main__':main()
