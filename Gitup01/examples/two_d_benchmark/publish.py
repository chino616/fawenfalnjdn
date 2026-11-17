"""Publish per-experiment two-dimensional benchmarks and uniform paper figures."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
import json
import os
from pathlib import Path
import re
import shutil
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'论文图NoteBook/9. SM_uniform_style'))
from models import LEVELS,read,sha,write
from publication_style import load_style,configure,new_figure,finalize,export

SHORT={'CsI2021':'CsI2021 (9 PE bins)','Ar2020':'Ar2020 (mean errors)',
       'COHERENT_CsI_Ar_mean_errors':'CsI + Ar (mean errors)','CONUS_plus':'CONUS+',
       'PandaX_paired':'PandaX paired','PandaX_US2':'PandaX US2','XENONnT':'XENONnT','Solar_joint':'Solar joint'}
COLORS={'CsI2021':'#215B84','Ar2020':'#64947D','COHERENT_CsI_Ar_mean_errors':'#182530','CONUS_plus':'#5C82A3',
        'PandaX_paired':'#87939B','PandaX_US2':'#64947D','XENONnT':'#215B84','Solar_joint':'#9C89B4'}
TEX={'ee':'ee','mumu':r'\mu\mu','emu':r'e\mu','etau':r'e\tau','mutau':r'\mu\tau','tautau':r'\tau\tau'}


def parameter_tex(parameter):
    if parameter=='sin2thetaW':return r'$\sin^2\theta_W$'
    if parameter=='fB':return r'$f_B=\Phi_{^8B}/\Phi_{\rm ref}$'
    m=re.fullmatch(r'epsilon_(.+)_([ud])V',parameter)
    return r'$\epsilon_{'+TEX[m[1]]+r'}^{'+m[2]+r'V}$'


def relative(path,owner):
    return Path(os.path.relpath(path,owner)).as_posix()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True);parser.add_argument('--figures',type=Path,required=True)
    parser.add_argument('--refresh-draft',action='store_true')
    args=parser.parse_args();out=args.results.resolve();figdir=args.figures.resolve()
    if list(figdir.glob('*.pdf')) and not args.refresh_draft:raise FileExistsError('Use a fresh figure directory')
    result=read(out/'BENCHMARK_RESULTS.json');checks=read(out/'qa/INDEPENDENT_CHECKS.json')
    assert checks['status']=='PASS_ALL_EXECUTED_NUMERICAL_CHECKS'
    references=read(out/'PAPER_BOUNDARIES.json');comparison=read(out/'REFERENCE_COMPARISON.json')
    figdir.mkdir(parents=True,exist_ok=True)
    for n in ['overview','data','qa']:(figdir/n).mkdir(exist_ok=True)
    style=load_style()
    style['layouts']['four_panel']={'height_in':5.8,'axes_rects':[[x,y,.385,.27] for y in [.53,.13] for x in [.095,.59]]}
    style['layouts']['six_panel']={'height_in':7.6,'axes_rects':[[x,y,.385,.19] for y in [.67,.39,.11] for x in [.095,.59]]}
    style['layouts']['three_panel']={'height_in':3.8,'axes_rects':[[.105,.20,.23,.54],[.43,.20,.23,.54],[.755,.20,.23,.54]]}
    style['statistical_series_colors']=COLORS
    style['two_dimensional_nominal_levels']=LEVELS
    style['two_dimensional_roles']={'68percent':'solid boundary, strongest fill','90percent':'dashed boundary, middle fill',
         '95percent':'dotted boundary, lightest fill','published_boundary':'orange dashed, original axis mapping and holes preserved',
         'best_marker':'star; nonunique single-yield points explicitly labelled representative',
         'conditioned_axes':'z1,z2 are numerical coordinates with inverse map in each model JSON, not NSI coupling labels'}
    configure(style);write(figdir/'STYLE.json',style)
    scans=result['scans'];cache={};all_files=[];captions=[]

    def load(key,view):
        tag=(key,view)
        if tag not in cache:
            row=scans[key]
            with np.load(out/row['views'][view]['surface'],allow_pickle=False) as z:
                arrays={k:z[k].copy() for k in z.files}
            with (out/row['views'][view]['contours']).open(encoding='utf-8') as f:paths=list(csv.DictReader(f))
            cache[tag]=(arrays,paths)
        return cache[tag]

    def curve_paths(ax,key,view,levels=None,*,conditioned=False,color=None,label=None,lw=1.15):
        _,paths=load(key,view);color=color or COLORS[scans[key]['analysis']]
        levels=list(LEVELS) if levels is None else levels
        for name in levels:
            rows=[r for r in paths if r['confidence']==name]
            for component in sorted({r['component'] for r in rows},key=int):
                part=[r for r in rows if r['component']==component]
                x='search_x' if conditioned else 'x';y='search_y' if conditioned else 'y'
                pattern={'68percent':'-','90percent':'--','95percent':':'}[name]
                ax.plot([float(r[x]) for r in part],[float(r[y]) for r in part],color=color,ls=pattern,lw=lw)
        if label:ax.plot([],[],color=color,ls='--',label=label)

    def legend_levels(ax,color):
        for name,pattern in [('68percent','-'),('90percent','--'),('95percent',':')]:
            ax.plot([],[],color=color,ls=pattern,label=name[:2]+'% nominal ('+str(LEVELS[name])+')')

    def panel(ax,key,view='paper_window',*,conditioned=False,add_legend=False,add_point=True):
        row=scans[key];color=COLORS[row['analysis']]
        if row['status']=='FLAT_ENTIRE_REAL_PLANE':
            ax.axis('off');ax.text(.5,.5,'No incoming tau population\nLikelihood is constant\nAllowed set: entire real plane\nNo finite contour',
                                   transform=ax.transAxes,ha='center',va='center',fontsize=9)
            return
        arrays,_=load(key,view)
        x,y=(np.meshgrid(arrays['axis_a'],arrays['axis_b'],indexing='xy') if conditioned else (arrays['physical_x'],arrays['physical_y']))
        for level,alpha in [(5.99,.065),(4.61,.10),(2.30,.20)]:
            ax.contourf(x,y,arrays['delta_chi2'],levels=[-1e-5,level],colors=[to_rgba(color,alpha)],antialiased=True)
        curve_paths(ax,key,view,conditioned=conditioned,color=color)
        if conditioned:
            ax.set(xlabel=r'$z_1$ (conditioned)',ylabel=r'$z_2$ (conditioned)',xlim=(-1,1),ylim=(-1,1))
        else:
            ax.set(xlabel=parameter_tex(row['parameters'][0]),ylabel=parameter_tex(row['parameters'][1]))
            if view=='paper_window':
                ax.set(xlim=(float(arrays['axis_a'][0]),float(arrays['axis_a'][-1])),ylim=(float(arrays['axis_b'][0]),float(arrays['axis_b'][-1])))
            elif row['kind']=='SM':
                box=row['views']['global']['region_metrics']['95percent']['grid_bounding_box']
                ax.set(xlim=(0,1),ylim=(0,box[1][1]*1.08))
            else:
                box=np.array(row['views']['global']['region_metrics']['95percent']['grid_bounding_box'])
                center=box.mean(axis=1);radius=(box[:,1]-box[:,0])*.56
                ax.set(xlim=(center[0]-radius[0],center[0]+radius[0]),ylim=(center[1]-radius[1],center[1]+radius[1]))
        point=row['fit']['best_fit']
        if add_point and point is not None:
            p=row['fit'].get('best_white_point') if conditioned else point
            if p is not None and ax.get_xlim()[0]<=p[0]<=ax.get_xlim()[1] and ax.get_ylim()[0]<=p[1]<=ax.get_ylim()[1]:
                ax.plot(*p,marker='*',color=color,ls='None',ms=5)
        if 'one fitted yield' in row['best_fit_semantics']:
            ax.text(.98,.95,'One yield: nonunique best fit',transform=ax.transAxes,ha='right',va='top',fontsize=7.2,
                    bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1.5})
        if add_legend:legend_levels(ax,color)

    def paper_outline(ax,reference_id):
        r=references[reference_id]
        lo,hi=np.array(r['bounds']).T
        for p in r['polygons']:
            p=np.array(p);pairs=np.stack([p,np.roll(p,-1,axis=0)],axis=1)
            near=(np.isclose(pairs,lo,atol=.006)|np.isclose(pairs,hi,atol=.006))
            keep=~np.any(np.all(near,axis=1),axis=1)
            # NaN-separated segments exclude closures along a clipped frame.
            x=[];y=[]
            for pair,ok in zip(pairs,keep):
                if ok:x.extend([pair[0,0],pair[1,0],np.nan]);y.extend([pair[0,1],pair[1,1],np.nan])
            ax.plot(x,y,color=style['colors']['reference'],ls='--',lw=1.0)
        ax.plot([],[],color=style['colors']['reference'],ls='--',label='Published 90% outline')

    def save(fig,path,layout,titles,note,caption,book):
        finalize(fig,layout,titles=titles,note=note,style=style)
        export(fig,path,style);book.savefig(fig,bbox_inches=None,facecolor='white');plt.close(fig)
        path.with_name(path.name+'_caption.txt').write_text(caption+'\n',encoding='utf-8')
        all_files.append(relative(path.with_suffix('.pdf'),figdir));captions.append((relative(path,figdir),caption))
        cache.clear()

    groups=defaultdict(list)
    with PdfPages(figdir/'All_Experiment_Panels.pdf') as book:
        for key,row in scans.items():
            analysis=row['analysis'];folder=figdir/analysis;folder.mkdir(exist_ok=True)
            stem=key.split('__',1)[1];path=folder/stem
            fig,axes=new_figure('two_panel',style)
            panel(axes[0],key,add_legend=True)
            panel(axes[1],key,'global',conditioned=row['kind']=='NSI')
            mode=('Free flux, data-only' if row['mode']=='data_only' else 'Existing 12% pulls' if row['kind']=='SM' else 'Same declared Gaussian nuisance model')
            if row['status']=='FLAT_ENTIRE_REAL_PLANE':note='Tau-diagonal plane: no incoming SNS tau component; all real parameter pairs are allowed.'
            elif row['kind']=='NSI':note='Left: physical display window. Right: full enclosing domain; inverse coordinate map is supplied with the data.'
            else:note=mode+'. Weak-angle / flux correlation and physical boundaries are retained.'
            caption=f"{SHORT[analysis]}: simultaneous two-parameter profile for {', '.join(row['parameters'])}. {mode}. Other physics coordinates are fixed, and only the original nuisance parameters are profiled. Each panel uses the same continuous two-dimensional minimum, chi2_min={row['fit']['chi2_min']:.10f}; the display window is never minimized separately. Nominal two-parameter contours are Delta chi2=2.30,4.61,5.99, without toy coverage calibration. {row['best_fit_semantics']}. "
            caption+=('The right NSI panel uses conditioned numerical coordinates, defined by the recorded affine map, to retain long valleys and every sampled component; finite plot bounds do not define physical parameter priors.' if row['kind']=='NSI' else 'The right panel covers the physical weak-angle interval [0,1] and every potentially allowed nonnegative flux, using a proved rate bound. The reference solar flux is 5.46e6 cm^-2 s^-1.')
            save(fig,path,'two_panel',['(a) '+SHORT[analysis]+' (display)',
                 '(b) Full conditioned domain' if row['kind']=='NSI' else '(b) Full physical domain'],note,caption,book)
            groups[analysis].append((stem,key))
    with PdfPages(figdir/'TwoD_Benchmark_Overview.pdf') as book:
        def overview(stem,keys,layout,titles,note,caption,*,view='paper_window',paper_ids=None):
            fig,axes=new_figure(layout,style)
            for j,(ax,key) in enumerate(zip(axes,keys)):
                panel(ax,key,view,add_legend=j==0)
                if paper_ids and paper_ids[j]:
                    paper_outline(ax,paper_ids[j])
                    bounds=references[paper_ids[j]]['bounds']
                    ax.set(xlim=bounds[0],ylim=bounds[1])
            save(fig,figdir/'overview'/stem,layout,titles,note,caption,book)
        solar=['PandaX_paired','PandaX_US2','XENONnT','Solar_joint']
        overview('Figure_01_SM_Angle_Flux_DataOnly',[n+'__SM_angle_flux_data_only' for n in solar],'four_panel',
                 [SHORT[n] for n in solar],'Free source flux, no additional normalization prior. Full physical weak-angle range.',
                 'Joint weak-angle/solar-flux fits to each fitted yield and the three-yield combination. The flux is free, with no external solar flux prior. Individual yields determine a continuous best-fit ridge. Even the combination is weakly informative along that correlation; the best numerical point lies at the physical weak-angle boundary. These are nominal two-parameter regions of the adopted three-singlebin model, not the multibin contours of arXiv:2411.11749.',view='global')
        overview('Figure_02_SM_Angle_Flux_PullControl',[n+'__SM_angle_flux_existing_pulls_control' for n in solar],'four_panel',
                 [SHORT[n] for n in solar],'Sensitivity model: retain the existing independent 12% rate pulls while fitting source flux.',
                 'Same two physical coordinates as Figure 1, with the existing independent 12% Gaussian rate-normalization pulls retained as an explicitly separate sensitivity model. The shared flux fB is distinct from those independent pulls. Single-yield ridges, physical boundaries and weak angle/flux correlation remain visible; no unique weak-angle measurement is claimed.',view='global')
        names=['CsI2021','Ar2020','CONUS_plus','Solar_joint']
        overview('Figure_03_NSI_Electron_Flavor',[n+'__NSI_ee' for n in names],'four_panel',[SHORT[n] for n in names],
                 'Physical display windows; each region uses its own full-domain two-dimensional minimum.',
                 'Electron-flavor uV/dV NSI planes for the individual saved CsI/Ar/CONUS models and the solar joint model. Nuclear response and stated statistical inputs are preserved. The solar propagation is reevaluated at every parameter point. Long near-cancellation valleys and remote minima are captured by the separately archived enclosing-domain scans, not by assigning a minimum inside this display window.')
        for index,name in [(4,'CsI2021'),(5,'Ar2020'),(6,'COHERENT_CsI_Ar_mean_errors')]:
            keys=[name+'__NSI_'+f for f in ['ee','mumu','emu','etau','mutau','tautau']]
            titles=[parameter_tex(scans[k]['parameters'][0])+' / '+parameter_tex(scans[k]['parameters'][1]) for k in keys]
            overview(f'Figure_{index:02}_NSI_{name}_Flavors',keys,'six_panel',titles,
                     SHORT[name]+': fixed incoming flavors. Tau-diagonal coordinates have no sensitivity.',
                     'Six uV/dV flavor-coordinate planes in the declared energy-only Gaussian model. Real flavor-changing and flavor-preserving coordinates are separate simultaneous two-parameter analyses, with all other NSI zero. The SNS source contains no incoming tau component, making the tau-diagonal plane constant over R^2. Tau final states from flavor-changing interactions remain allowed. For Ar, mean errors are used; this is not a rerun of the distinct asymmetric IRLS likelihood.')
        conus=['CONUS_plus__NSI_ee','CONUS_plus__NSI_emu','CONUS_plus__NSI_etau',
               'CONUS_plus__NSI_mixed_ee_emu_dV','CONUS_plus__NSI_mixed_ee_etau_dV','CONUS_plus__NSI_ee']
        overview('Figure_07_CONUS_Published_Benchmarks',conus,'six_panel',
                 ['(a) ee: uV / dV','(b) e-mu: uV / dV','(c) e-tau: uV / dV','(d) ee-dV / e-mu-dV','(e) ee-dV / e-tau-dV','(f) Diagonal reference comparison'],
                 'Orange: arXiv:2501.17843v3 Fig.4 blue-region outlines; exact axis permutations are recorded.',
                 'Five distinct CONUS+ two-parameter benchmarks, including the mixed flavor-preserving/flavor-changing d-quark planes shown in arXiv:2501.17843v3 Fig.4. Orange curves are extracted published 90% outlines, not invented author chi2 grids. The published upper-left u/d axes are transposed to our explicit (uV,dV) convention. The flavor-changing e-mu and e-tau equality is independently checked. Nested holes are retained in area comparisons.',
                 paper_ids=['2501_'+k for k in conus])
        overview('Figure_08_Solar_NSI_Individual_And_Joint',[n+'__NSI_ee' for n in solar],'four_panel',[SHORT[n] for n in solar],
                 'Continuous acceptance and point-dependent effective SNuDD propagation; XENON tail flat sensitivity.',
                 'Individual three-singlebin and joint ee-vector NSI regions. One fitted yield produces a continuous best-fit ridge rather than a unique two-coordinate estimate. The joint plane uses its own full-domain minimum. The adopted SNuDD v3.4.1 effective two-flavor approximation and explicit XENON acceptance-tail continuation remain unchanged; full-rho trace v3.5 is not implemented by this analysis.')
        mixed=[n+'__NSI_mixed_ee_'+f+'_dV' for n in ['COHERENT_CsI_Ar_mean_errors','CONUS_plus'] for f in ['emu','etau']]
        overview('Figure_09_Mixed_Flavor_dV',mixed,'four_panel',['CsI + Ar: ee / e-mu','CsI + Ar: ee / e-tau','CONUS+: ee / e-mu','CONUS+: ee / e-tau'],
                 'Both axes are d-quark coordinates; other NSI vanish. Each experiment profiles its own nuisance model.',
                 'Mixed flavor-diagonal and flavor-changing d-quark benchmark planes. These are distinct from same-flavor uV/dV scans and reproduce the parameter choices of the lower CONUS+ Fig.4 panels. Fixed nuclear/state models and nuisance widths are preserved; the COHERENT comparison uses nine-bin CsI plus mean-error Ar with independent nuisances.')
        refids=['2601_COHERENT_CsI_Ar','2601_CONUS_plus','2601_Solar_joint'];keys=[references[k]['case'] for k in refids]
        overview('Figure_10_Paper2601_Fig4_Comparison',keys,'three_panel',['(a) CsI + Ar','(b) CONUS+','(c) Solar joint'],
                 'Published orange 90% outlines versus current local models; all use the full-domain minimum.',
                 'Direct graphical comparison with arXiv:2601.19883v2 Fig.4 in its original [-1,1] coupling window. Orange outlines are the published regions. Current calculated 90% boundaries use Delta chi2=4.61 relative to each current model full-domain minimum; the fainter nominal 68/95 boundaries provide context. Inputs and likelihoods are not certified identical to the paper. Window-specific intersection-over-union and unclipped-boundary residuals are reported separately.',paper_ids=refids)
        global_names=['CsI2021','Ar2020','CONUS_plus','Solar_joint']
        overview('Figure_11_NSI_Global_Physical_Domains',[n+'__NSI_ee' for n in global_names],'four_panel',[SHORT[n] for n in global_names],
                 'Full physical coupling extent: long cancellation valleys and remote best points are retained.',
                 'Global physical-axis view of the ee uV/dV regions, from well-conditioned domain scans and refined contour vertices. Large aspect ratios reflect weakly constrained cancellation directions, not a clipping prior. The adopted effective solar propagation at large NSI is a local-model extrapolation, not certification of the full physical three-flavor theory.',view='global')
        fig,axes=new_figure('single',style);ax=axes[0]
        for name in ['COHERENT_CsI_Ar_mean_errors','CONUS_plus','Solar_joint']:
            key=name+'__NSI_ee';curve_paths(ax,key,'paper_window',['90percent'],label=SHORT[name],lw=1.5)
        ax.set(xlabel=parameter_tex('epsilon_ee_uV'),ylabel=parameter_tex('epsilon_ee_dV'),xlim=(-1,1),ylim=(-1,1))
        save(fig,figdir/'overview/Figure_12_NSI_Experiment_Overlay','single',['Simultaneous ee-uV / ee-dV: calculated regions'],
             'Nominal 90% (Delta chi-square = 4.61); each experiment group uses its own full-domain minimum.',
             'Overlay of the independently calculated CsI+Ar, CONUS+ and solar joint nominal 90% contour paths. This is a comparison of experiment groups, not an all-experiment joint fit. Each group retains its own statistical and response model. The identical display rectangle does not limit the numerical search or define a prior.',book)

    # Tables and complete analysis contracts accompany the figures.
    fieldnames=['case','analysis','kind','parameters','mode','status','best_x','best_y','chi2_min','best_point_semantics','display_minimum_offset','global_95_grid_bbox','contours_global','contours_display']
    with (out/'SUMMARY.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
        for key,row in scans.items():
            point=row['fit']['best_fit'];metrics=row['views']['global']['region_metrics']
            w.writerow({'case':key,'analysis':row['analysis'],'kind':row['kind'],'parameters':' / '.join(row['parameters']),
               'mode':row['mode'],'status':row['status'],'best_x':None if point is None else point[0],
               'best_y':None if point is None else point[1],'chi2_min':row['fit']['chi2_min'],
               'best_point_semantics':row['best_fit_semantics'],'display_minimum_offset':row['views']['paper_window']['local_minimum_offset_from_2d_best'],
               'global_95_grid_bbox':json.dumps(metrics.get('95percent',{}).get('grid_bounding_box')),
               'contours_global':row['views']['global']['contours'],'contours_display':row['views']['paper_window']['contours']})
    lines=['# 二维 SM/NSI benchmark 完整结果','','2026-11-13。完成41个声明平面，含3个SNS τ对角平坦平面。现有本地模型的approximate benchmark；正式Runtime、data、Gate和一维结果未改。',
           '','[总表CSV](SUMMARY.csv) · [全部机器结果](BENCHMARK_RESULTS.json) · [统计定义](STATISTICS_CONTRACT.md) · [独立验收](qa/INDEPENDENT_CHECKS.json) · [论文图集](<'+relative(figdir/'README.md',out)+'>)',
           '','## 不同实验完成情况','','| 分析 | 已完成二维平面 | 统计/方法 |','|---|---:|---|']
    for analysis,items in groups.items():
        description='太阳连续接受度、有效SNuDD；独立12% pull与data-only源强拟合分开' if analysis.startswith(('PandaX','XENON','Solar')) else '保存核回放；均误差Gaussian' if analysis=='Ar2020' else '独立实验nuisance联合' if analysis.startswith('COHERENT') else '既有局部Gaussian与核响应'
        lines.append(f'| {analysis} | {len(items)} | {description} |')
    lines+=['','CsI2017参数核/正式输入仍不可用，CsI-time P09未闭合；太阳多bin与v3.5完整ρ/trace未在本轮实现。未把这些能力替换成其他数据或似然。',
            '','## 每个平面的最佳点','','| 分析 | 二维参数 | 最佳点/代表点 | χ²min | 论文窗口最小值偏移 |','|---|---|---|---:|---:|']
    for key,row in scans.items():
        point=row['fit']['best_fit'];text='不可辨识：允许集R²' if point is None else '('+', '.join(f'{p:.7f}' for p in point)+')'
        if 'one fitted yield' in row['best_fit_semantics']:text+='；连续简并中的代表点'
        lines.append(f"| {row['analysis']} | {' / '.join(row['parameters'])} ({row['mode']}) | {text} | {row['fit']['chi2_min']:.9f} | {row['views']['paper_window']['local_minimum_offset_from_2d_best']:.6g} |")
    lines+=['','单个太阳信号总数只约束一个率组合，最佳点是连续曲线。太阳弱角/通量同时自由时，联合最小值落在sin²θW=0物理边界，不能把某一个代表点当作精确弱角或通量测量。上一轮固定通量的一维弱角结果和本轮二维推断的条件不同。',
            '','## 对应论文benchmark','','| 原文图形 | 当前平面 | 原文窗口IoU | 原文非裁剪边界上的当前Δχ²中位数 |','|---|---|---:|---:|']
    for c in comparison['graphical_comparisons']:
        lines.append(f"| {c['reference_id']} | {c['case']} | {c['intersection_over_union']:.6f} | {c['own_delta_at_paper_boundary_median']:.6f} |")
    lines+=['','IoU是原图窗口内的图形区域交并比，不是统计p值或官方likelihood验收。保留环状内洞；CONUS原文diag_ud横纵轴与本项目u/d顺序相反，已按原始坐标元数据显式换轴。没有作者χ²网格，不伪造论文χ²曲面。',
            '','[详细图形与历史数值对照](REFERENCE_COMPARISON.json)记录模型差异。2411.11749v1太阳Fig.2来自多bin谱；2211.11905v2的COHERENT含时间/形状统计，均不作为本轮相同likelihood验收。',
            '','## 全部区域与数据','','每个平面都有models/*.json、完整域/论文窗口各一份surfaces/*.npz和contours/*.csv。NPZ保存两条搜索坐标轴、physical_x/physical_y、rawχ²、相对该面二维最小值的Δχ²；CSV保存每个2.30/4.61/5.99轮廓的全部精化顶点、实际Δχ²、搜索坐标和裁剪标记。全部不连通路径保留。',
            '','global grid_bounding_box仅是二维名义区域的网格外接范围，不是一维profile区间。物理边界与显示截断分开；完整NSI数值域边界均应排除所报区域。算法对正率域进行条件化，并用独立起点/网格复核，不把显示窗口当作完整域。',
            '','## 已执行验证','','- 全部混合u/d与混合味信号多项式有新点与共享full核对照；另有full/pair逐通道和增广最小二乘nuisance核对。',
            '- 二维坐标轴切片与旧一维rawχ²核对；一维与二维Δχ²最小值偏移明确保存。',
            '- 两个新太阳混合参数点及新联合最佳点使用独立隔离SNuDD→Runtime验证；新最佳点另作三样本Slow积分。',
            '- 三个既有ee二维联合/CONUS最佳χ²复算一致；所有完整面、显示面及轮廓顶点均回代检查。',
            '- 不将上述内部数值一致性等同官方似然、全三味大NSI物理适用性或coverage toys。',
            '','[统计合同](STATISTICS_CONTRACT.md) · [全部程序与命令](../../examples/two_d_benchmark/README.md) · [来源清单](BENCHMARK_SOURCE_MANIFEST.json)']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    contract=r'''# 二维统计与参数合同

沿用[一维统计定义](../one_d_benchmark_20261113_run1/STATISTICS_CONTRACT.md)，只把物理坐标数扩展为2。其他NSI为零，其他SM输入固定；地面只profile原来的独立信号/背景Gaussian nuisance。联合在相同物理点相加各实验χ²，再求同一二维面的最小值。

$$\Delta\chi^2(x,y)=\min_{\eta}\chi^2(x,y,\eta)-\min_{x,y,\eta}\chi^2.$$

名义2参数阈值为2.30、4.61、5.99（常规68%、90%、95%）。不使用一维1/2.71/3.84或相加后的各实验独立最佳值。没有coverage toys；非正则FCNC、物理边界和单信号数的不可辨识方向不声称获得了已校准的2自由度覆盖率。

## 物理坐标与可辨识性

- NSI同味平面是实数uV/dV，同时改变两个Wilson矩阵坐标。NSI混合味平面是ee-dV与eμ-dV或eτ-dV，同时改变两个不同味结构。完整核收缩保留交叉项；不是把两条一维Δχ²相加。
- SNS无入射τ，因此三个τ对角平面恒定，允许集是整个实平面。τ末态的味改变项仍有敏感度。
- 太阳只使用既有ee实数传播合同，NSI每点重算Pee(E)。保留continuous_acceptance、SNuDD v3.4.1有效两味绝热传播、七核素核响应及XENON尾段flat_sensitivity。不实现v3.5完整ρ/trace或额外味传播。
- SM二维只对太阳定义：sin²θW∈[0,1]，fB≥0，参考通量5.46×10⁶ cm⁻²s⁻¹。弱角作用所有入射味的SM LEFT系数，源强只乘一次。
- data_only移去额外12%归一化pull以测自由源强；existing_pulls_control保留原三个独立pull作为敏感性分析。二者不是同一目标函数的两种算法。单个总数在二维有连续最佳曲线；联合仍有很强的弱角/通量相关。

## 完整域、显示与轮廓

地面固定态信号为完整二元二次式；以正的总信号二次型和Gaussian Cauchy下界，求出包含所有可能最佳点和名义区域的椭圆。太阳用S≥Pee_min×N_all_electron建立类似域。经变换的包围正方形覆盖椭圆，完整NSI区域不应触碰其数值边界。太阳四组的共同域由各自椭圆的谱范数并集界建立，仅共享传播计算，不合并各自统计。

SM使用物理弱角区间和正信号率上界，按参考样本相对率条件化fB，避免在狭长相关谷漏搜。弱角0/1、源强0是物理边界，与数值截断区别记录。

每个面保存601×601完整域和601×601显示面、连续最佳点、多起点与独立81×81网格搜索、精化轮廓。轮廓CSV包含全部采样路径，顶点用原目标函数沿梯度回代精化；区域拓扑与外接框仍是有限网格诊断，不冒充一维profile区间。完整数学域的证明与数值找到最优点是不同证据，不把随机优化称为解析全局最优证明。

## 直接输入与计算路线

[一维输入快照](../one_d_benchmark_20261113_run1/inputs/README.md)拥有地面full_kernel、rho、D/B/σ实际数组尺寸、轴与来源。采用其原本地数值资源及读法；未重新从受OS阻断的正式CsI/Ar Package读取。太阳源/核来自上一轮已核查的能量分辨数组。BENCHMARK_SOURCE_MANIFEST逐项记录采用来源。

models.py读取和组装→plane_inference.py证明包围域、搜索与轮廓→run_analysis.py运行33个基础面→extend_mixed.py增加8个原文混合平面而不覆盖基础结果→validate_results.py独立核对/Runtime→publish.py只读制表与出图。均为examples层，不是正式实验新增或Gate推进。

claim_level=approximate local-model benchmark；科学/作者等价接受仍NOT_REVIEWED。CsI-time原生P09、CsI2017参数模型、Ar新非对称扫描、太阳多bin/额外味/v3.5、全实验堆叠的相关合同仍未执行。
'''
    (out/'STATISTICS_CONTRACT.md').write_text(contract+'\n',encoding='utf-8')

    for analysis,items in groups.items():
        doc=['# '+SHORT[analysis]+'：二维benchmark','','采用本轮明确模型；当前目录保存每个平面的显示/完整域两面板PDF、SVG、PNG和图注。完整面与全部轮廓位于数值目录。',
             '','| 参数平面 | 图件 | 数值模型与全部扫描 |','|---|---|---|']
        for stem,key in items:
            doc.append(f'| {" / ".join(scans[key]["parameters"])} ({scans[key]["mode"]}) | [PDF]({stem}.pdf) · [SVG]({stem}.svg) · [PNG]({stem}.png) · [图注]({stem}_caption.txt) | [模型/域/拟合](<'+relative(out/'models'/(key+'.json'),figdir/analysis)+'>) |')
        doc+=['','[图集总目录](../README.md) · [统计合同](<'+relative(out/'STATISTICS_CONTRACT.md',figdir/analysis)+'>)']
        (figdir/analysis/'README.md').write_text('\n'.join(doc)+'\n',encoding='utf-8')
    over=['# 二维benchmark论文汇总图','','十二张汇总图采用统一180 mm画布；各实验的单独两面板结果见总目录。','']
    for p in all_files:
        if p.startswith('overview/'):
            stem=Path(p).stem;over.append('- ['+stem+']('+stem+'.pdf) · [PNG]('+stem+'.png) · [SVG]('+stem+'.svg)')
    over+=['','[图集总目录](../README.md)']
    (figdir/'overview/README.md').write_text('\n'.join(over)+'\n',encoding='utf-8')
    captions_md=['# 二维benchmark英文图注','','所有图件使用明确声明的局部模型和名义二维阈值；保持原数据/统计/核定义，未认证官方似然或coverage。','']
    for name,caption in captions:captions_md+=['## '+name,'',caption,'']
    (figdir/'PAPER_CAPTIONS.md').write_text('\n'.join(captions_md)+'\n',encoding='utf-8')
    reftext=(ROOT/'论文图NoteBook/10. OneD_Chi2_Benchmarks/REFERENCES.md').read_text(encoding='utf-8')
    reftext+='\n\n## 本轮二维的直接定位\n\n2501.17843v3：PDF p14 Fig4全部四个参数面与90%蓝色轮廓；2601.19883v2：PDF p22 Eq95后二维Δχ²=4.61，p23 Fig4；2411.11749v1：PDF pp7–8 Fig2与多bin统计，不能作为三单bin同输入验收。原文区域来自项目已有矢量路径提取，逐文件哈希和坐标轴置换保存在结果与来源清单。\n'
    (figdir/'REFERENCES.md').write_text(reftext,encoding='utf-8')
    for name in ['BENCHMARK_RESULTS.json','REFERENCE_COMPARISON.json','PAPER_BOUNDARIES.json','SUMMARY.csv']:
        shutil.copyfile(out/name,figdir/'data'/name)
    for file in (out/'contours').glob('*.csv'):shutil.copyfile(file,figdir/'data'/file.name)
    write(figdir/'data/DATA_INDEX.json',{'scientific_root':relative(out,figdir/'data'),
          'result_hash':sha(out/'BENCHMARK_RESULTS.json'),'coordinate_units':'dimensionless',
          'surface_paths_resolve_against':'scientific_root, not the copied JSON folder',
          'contours':'82 exact-refined contour CSVs; complete raw grids retained as NPZ in the scientific root'})
    (figdir/'data/README.md').write_text('# 二维论文图数据\n\n本目录复制41平面索引、summary和参考边界，以及每个完整域/显示域的82份轮廓CSV。原始601×601 rawχ²和Δχ² NPZ仍由[数值目录](<'+relative(out/'surfaces/README.md',figdir/'data')+'>)拥有，避免形成第二份科学权威。复制JSON内部surface路径必须按DATA_INDEX.json指定的scientific_root解析。\n\n[图集](../README.md)\n',encoding='utf-8')
    figure_readme=['# 二维 SM/NSI benchmark 图集','','41个实验/参数/方法平面，12张论文汇总图；统一180 mm/STIX样式。图件只展示当前本地近似模型，不宣称所有正式实验能力或作者likelihood已完成。',
       '','[论文汇总合集](TwoD_Benchmark_Overview.pdf) · [41平面详细合集](All_Experiment_Panels.pdf) · [12张单独汇总图](overview/README.md)',
       '','| 实验/分析 | 独立平面数 |','|---|---:|']
    for analysis,items in groups.items():figure_readme.append(f'| [{SHORT[analysis]}]({analysis}/README.md) | {len(items)} |')
    figure_readme+=['','[完整数值与benchmark对照](<'+relative(out/'RESULTS.md',figdir)+'>) · [原始面与全部轮廓](data/README.md) · [全部英文图注](PAPER_CAPTIONS.md) · [参考文献](REFERENCES.md) · [统一样式](STYLE.json) · [实际图件验收](qa/README.md)',
       '','同味uV/dV与混合味ee-dV/eμ、eτ-dV分别保存；Ar均误差模型和太阳两种通量统计明确区分。全部面减去自身二维最小值，显示窗口之外的极小点和长谷保留。三个τ对角面全实平面允许；太阳单总数最佳点为连续简并的代表点。',
       '','[生成代码与命令](../../examples/two_d_benchmark/README.md) · [上一轮一维图](<../10. OneD_Chi2_Benchmarks/README.md>) · [上一级](../README.md)']
    (figdir/'README.md').write_text('\n'.join(figure_readme)+'\n',encoding='utf-8')
    (figdir/'qa/README.md').write_text('# 二维图件与链接验收\n\nPDF_QA.json记录页面宽度、字体、矢量和边界；overview-page-*.png/detail-page-*.png为逐页渲染，contact-*.png为视觉核对总览。LINK_CHECKS.json核对当前新文档与导航。数值验收由结果目录的INDEPENDENT_CHECKS.json拥有，不以绘图检查代替物理验证。\n\n[图集](../README.md)\n',encoding='utf-8')
    (out/'models/README.md').write_text('# 每个二维模型与拟合\n\n41份JSON包含参数名、方法、原点χ²、实际二维最小值、多起点/网格结果、包围域证明、完整/显示面的路径与哈希、区域诊断。29份地面系数NPZ按常数/x/y/x²/xy/y²保存完整二元二次式；其中3个τ对角模型恒定。太阳NSI的最终事件率随传播变化，不保存为固定Pee二次式。\n\n[完整结果](../RESULTS.md)\n',encoding='utf-8')
    (out/'surfaces/README.md').write_text('# 完整二维χ²面\n\n每平面global和paper_window各一个NPZ，共82份。axis_a/axis_b是当前数值网格轴，physical_x/physical_y是实际物理参数网格（global可为仿射/率条件化映射），chi2为raw profile值，delta_chi2减该平面的连续二维最小值。所有轴均无量纲。\n\nNSI global数值边界不能当参数先验；τ对角的有限网格只是显示，全平面允许。SM global弱角边界0/1与通量0为物理边界。\n\n[完整结果](../RESULTS.md)\n',encoding='utf-8')
    (out/'contours/README.md').write_text('# 精化二维等高线\n\n82份CSV分别保存每平面的global与paper_window轮廓：名义水平、分支/顶点、实际物理x/y、数值搜索坐标、回代Δχ²和盒边界标记。保留全部采样路径；内洞与不连通分支不删除。单个轮廓投影不是一维profile区间；显示边界闭合也不是真实物理边界。平坦τ对角面的CSV只有表头，允许集为全实平面。\n\n[完整结果](../RESULTS.md)\n',encoding='utf-8')
    (out/'qa/README.md').write_text('# 二维数值与交付验收\n\nPOLYNOMIAL_HOLDOUTS与MIXED_POLYNOMIAL_HOLDOUTS核对新混合点；INDEPENDENT_CHECKS记录full/pair、增广最小二乘、1D切片、轮廓回代、原文边界、隔离SNuDD→Runtime和新最佳点Slow积分。FINAL_CHECKS另记录来源、原件、链接、图件与文件归属。\n\n[完整结果](../RESULTS.md)\n',encoding='utf-8')
    (out/'README.md').write_text('# 二维 SM/NSI benchmark（2026-11-13）\n\n[完整结果与实验汇总](RESULTS.md) · [41平面总表](SUMMARY.csv) · [统计定义](STATISTICS_CONTRACT.md) · [论文图集](<'+relative(figdir/'README.md',out)+'>)\n\nBENCHMARK_RESULTS.json为41平面的当前索引，由不覆盖的基础33面RESULTS.json与额外8面MIXED_RESULTS.json组成。PARTIAL_RESULTS.json仅为中间checkpoint。\n\n[每个模型/拟合](models/README.md) · [完整面](surfaces/README.md) · [全部轮廓](contours/README.md) · [独立验收](qa/README.md) · [文献与历史benchmark](REFERENCE_COMPARISON.json)。WRITE_PLAN、BENCHMARK_SOURCE_MANIFEST、FILE_LIFECYCLE与DELIVERY_MANIFEST分别记录范围/备份、来源哈希、文件归属和交付文件。\n\n[程序与重跑命令](../../examples/two_d_benchmark/README.md) · [上一轮一维结果](../one_d_benchmark_20261113_run1/README.md) · [上一级](../README.md)\n',encoding='utf-8')
    doc=ROOT/'docs/experiments/TWO_DIMENSIONAL_BENCHMARKS_20261113.md'
    doc.write_text('# 各实验二维 SM/NSI benchmark\n\n2026-11-13。完成41个明确参数平面，其中3个τ对角平面完全平坦。逐实验的方法、参数、完整域、最佳点和名义区域分别保存，不修改正式输入或工作流Gate。\n\n[全部实验结果、方法与文献对照](<'+relative(out/'RESULTS.md',doc.parent)+'>) · [所有程序职责与重跑命令](../../examples/two_d_benchmark/README.md) · [论文图集](<'+relative(figdir/'README.md',doc.parent)+'>) · [统计合同](<'+relative(out/'STATISTICS_CONTRACT.md',doc.parent)+'>)\n\nNSI包含支持的同味uV/dV，以及对应CONUS原文Fig.4的混合ee-dV/eμ、eτ-dV；太阳SM同时拟合弱角与自由通量，两种pull定义分别保存。单总数存在连续简并，联合自由通量也不能把固定通量的一维弱角区间当作二维测量精度。\n\nCsI2017参数模型、CsI-time原生P09、Ar新非对称拟合、太阳多bin/额外味/v3.5完整trace仍未在本轮完成。采用本地近似模型，不宣称原文官方似然精确等价。\n\n[上一轮逐步Python路线](COMPUTATION_ROUTES_20261113.md) · [实验总目录](README.md)\n',encoding='utf-8')
    source=read(out/'BENCHMARK_SOURCE_MANIFEST.json')
    for p in [*HERE.glob('*.py'),ROOT/'论文图NoteBook/9. SM_uniform_style/STYLE.json',ROOT/'论文图NoteBook/9. SM_uniform_style/publication_style.py']:
        source[p.relative_to(ROOT).as_posix()]=sha(p)
    write(out/'BENCHMARK_SOURCE_MANIFEST.json',source)
    write(figdir/'FIGURE_MANIFEST.json',{'date':'2026-11-13','case_figures':41,'overview_figures':12,'pdf_files':55,
          'detailed_collection_pages':41,'overview_collection_pages':12,'individual_figures':all_files,
          'width_mm':180,'benchmark_results_sha256':sha(out/'BENCHMARK_RESULTS.json'),'generator_sha256':sha(__file__),
          'pdf_validation':'PENDING'})
    print('Published 41 experiment panels, 12 overview figures, 55 PDFs and full reports',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
