"""Independent model checks, exact 1D nesting and published 2D boundary tests."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import numpy as np
from matplotlib.path import Path as Polygon

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import ROOT,ONE,BASIS,LEVELS,TerrestrialPlane,SolarNSIPlane,coefficients,read,sha,write
from extend_mixed import load_all_models
from cevns_pyeft.kernels.compiler import reconstruct_channels
from cevns_pyeft.statistics.parameters import VectorNSIParameters,vector_nsi_to_np_wilson


def independent_profile(channel, signal):
    s=np.asarray(signal,float);weight=1/channel.sigma
    columns=[s*weight];penalties=[1/channel.alpha_sigma]
    b=0. if channel.background is None else channel.background
    if channel.background is not None:
        columns.append(b*weight);penalties.append(1/channel.beta_sigma)
    A=np.vstack([np.column_stack(columns),np.diag(penalties)])
    y=np.r_[(channel.observed-s-b)*weight,np.zeros(len(columns))]
    solution=np.linalg.lstsq(A,y,rcond=None)[0]
    return float(np.sum((A@solution-y)**2))


def ground_checks(planes,results):
    full_pair=[];gaussian=[]
    for plane in planes:
        if not isinstance(plane,TerrestrialPlane): continue
        points=[[.123,-.087],[-.213,.191]]
        best=results[plane.key]['fit']['best_fit']
        if best is not None:points.append(best)
        for point in points:
            extra=vector_nsi_to_np_wilson(VectorNSIParameters(**dict(zip(plane.parameters,point))))
            total=0.
            for r,poly_signal in zip(plane.routes,plane.signals(point)):
                c=coefficients(r.angle)+np.array([extra.get(k,np.zeros((3,3),complex)) for k in BASIS])
                full=reconstruct_channels(r.full,c,r.rhos)
                pair=reconstruct_channels(r.full,c,r.rhos,representation='pair')
                error=float(np.max(np.abs(full-pair)))
                assert error < 1e-6+2e-10*float(np.max(np.abs(full)))
                signal=full.sum(axis=(0,1,2))
                signal_error=float(np.max(np.abs(signal-poly_signal)))
                assert signal_error < 2e-7+2e-10*float(np.max(np.abs(signal)))
                exact=independent_profile(r.channel,signal)
                analytic=float(r.channel.profile(poly_signal)[0])
                assert abs(exact-analytic)<2e-6, (plane.key,point,exact,analytic)
                total+=exact
                full_pair.append({'case':plane.key,'channel':r.name,'point':point,'max_channel_events_difference':error,
                                  'polynomial_events_difference':signal_error})
            error=abs(total-float(plane.cost(point)))
            assert error<2e-6
            gaussian.append({'case':plane.key,'point':point,'chi2_from_independent_augmented_lstsq':total,
                             'max_profile_difference':error})
    return full_pair,gaussian


def nested_checks(planes,old):
    rows=[]
    for plane in planes:
        for axis,param in enumerate(plane.parameters):
            par=param
            if par=='fB':par='fB_existing_pulls_control' if plane.retain_pulls else 'fB_data_only'
            if plane.kind=='SM' and param=='sin2thetaW' and not plane.retain_pulls:continue
            key=plane.analysis+'__'+par
            if key not in old['scans']:continue
            row=old['scans'][key]
            with np.load(ONE/'scans'/(key+'.npz'),allow_pickle=False) as z:
                indices=np.linspace(0,len(z['grid'])-1,13,dtype=int)
                points=np.tile(plane.reference,(len(indices),1)).astype(float)
                points[:,axis]=z['grid'][indices]
                current=np.asarray(plane.cost(points))
                error=float(np.max(np.abs(current-z['chi2'][indices])))
                assert error<3e-6, (plane.key,param,error)
                rows.append({'case':plane.key,'axis':param,'one_d_key':key,'points_checked':len(indices),
                             'max_raw_chi2_difference':error,
                             'expected_delta_offset_1d_minus_2d_min':row['chi2_min']})
    return rows


def solar_runtime_checks(planes,out):
    from extensions.solar_rho_snudd.experiment import load_snudd
    from extensions.solar_rho_snudd.scan import ScanJoint
    from tools.run_solar_b8_snudd_inference import direct_validation
    from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
    solar=next(p for p in planes if isinstance(p,SolarNSIPlane) and p.analysis=='Solar_joint')
    cache=ROOT/'outputs/external/solar_rho_snudd/two_d_benchmark_20261113_validation'
    experiments=[];kernels=[];interaction=None
    for sample in solar.solar.SAMPLES:
        e=load_snudd(sample,cache_root=cache,interaction=interaction)
        interaction=e.model.interaction
        old=SolarNSIKernel.load(solar.solar.directory/'kernels'/(sample+'.npz'))
        k=old.rebind_state(e)
        assert np.array_equal(k.values,old.values)
        experiments.append(e);kernels.append(k)
    joint=ScanJoint(tuple(experiments),tuple(kernels),solar.solar.source)
    minimum=read(out/'BENCHMARK_RESULTS.json')['scans'][solar.key]['fit']['best_fit']
    points=[(-.23,.36),(.41,-.22),tuple(minimum)]
    print('Validating three fresh solar 2D points with isolated SNuDD and Runtime; Slow at the new minimum',flush=True)
    checked=direct_validation(joint,tuple(experiments),tuple(kernels),points)
    independent=[]
    for u,d in points:
        direct=joint.signals(u,d,'flat_sensitivity')
        own=solar.signals([u,d])
        error=float(np.max(np.abs(direct-own)))
        assert error<2e-8
        independent.append({'point':[u,d],'max_events_difference':error,'reference':'existing ScanJoint.signals and current PreparedExperiment Runtime'})
    return {'runtime_and_slow':checked,'separate_two_coordinate_fold_checks':independent,
            'cache':cache.relative_to(ROOT).as_posix(),'claim':'same effective two-flavor ee-equivalent v3.4.1; this does not implement v3.5 full trace'}


def group_polygons(rows,group,x,y):
    out=[]
    for key in sorted({r[group] for r in rows},key=lambda v:int(v)):
        p=np.array([[float(r[x]),float(r[y])] for r in rows if r[group]==key])
        if len(p)>=3:out.append(p)
    return out


def mask_from_outlines(polygons,points):
    # Even-odd fill preserves the holes of published ring regions. It also
    # reduces to a union for disjoint outlines. Do not union away inner holes.
    mask=np.zeros(len(points),bool)
    for p in polygons:mask^=Polygon(p).contains_points(points)
    return mask


def reference_comparison(out,result,planes):
    lookup={p.key:p for p in planes};records=[];sources={};display={}
    p2601=ROOT/'outputs/paper2601_chi2_20261111/paper_reference/fig4_plotted_polygons.csv'
    with p2601.open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    for group,case in [('COHERENT_CsI_Ar','COHERENT_CsI_Ar_mean_errors__NSI_ee'),('CONUS_plus','CONUS_plus__NSI_ee'),('Solar_joint','Solar_joint__NSI_ee')]:
        rows=[r for r in raw if r['experiment']==group]
        polygons=group_polygons(rows,'polygon','epsilon_ee_uV','epsilon_ee_dV')
        real=np.array([[float(r['epsilon_ee_uV']),float(r['epsilon_ee_dV'])] for r in rows if int(r['clipped_at_axis_boundary'])==0])
        display['2601_'+group]={'case':case,'source':'2601.19883v2 Fig4, 90% two-parameter graphical boundary',
             'polygons':[p.tolist() for p in polygons],'bounds':[[-1.,1.],[-1.,1.]],'axis_mapping':'CSV explicitly names physical uV and dV',
             'unclipped_boundary':real.tolist()}
    pc=ROOT/'data/benchmarks/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/benchmark/fig4_blue_polygons.csv'
    provenance=pc.with_name('REFERENCES_PROVENANCE.json');prov=read(provenance)
    pdf=ROOT/'docs/references/CONUS/2501.17843v3.pdf'
    assert sha(pdf)==prov['source_sha256'],'CONUS reference source PDF changed'
    with pc.open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    for panel,case in [('diag_ud','CONUS_plus__NSI_ee'),('fc_ud','CONUS_plus__NSI_emu'),('fc_ud','CONUS_plus__NSI_etau'),
                       ('ring_mu','CONUS_plus__NSI_mixed_ee_emu_dV'),('ring_tau','CONUS_plus__NSI_mixed_ee_etau_dV')]:
        metadata=next(p for p in prov['figure_panels'] if p['panel']==panel)
        rows=[r for r in raw if r['panel']==panel]
        polygons=group_polygons(rows,'polygon_index','x','y')
        original=[metadata['x_parameter'],metadata['y_parameter']]
        parameters=result['scans'][case]['parameters']
        order=[original.index(p) if p in original else (0 if p.endswith('_uV') else 1) for p in parameters]
        # fc_ud is explicitly flavor-equivalent e-mu/e-tau in the paper.
        polygons=[p[:,order] for p in polygons]
        raw_bounds=[[min(metadata['x_tick_values']),max(metadata['x_tick_values'])],
                    [min(metadata['y_tick_values']),max(metadata['y_tick_values'])]]
        bounds=[raw_bounds[i] for i in order]
        real=np.concatenate(polygons)
        keep=np.ones(len(real),bool)
        for j,(lo,hi) in enumerate(bounds):keep&=(real[:,j]>lo+1e-5)&(real[:,j]<hi-1e-5)
        display['2501_'+case]={'case':case,'source':'2501.17843v3 PDF p14 Fig4 blue '+panel+', 90% nominal two-parameter region',
             'polygons':[p.tolist() for p in polygons],'bounds':bounds,'axis_mapping':{'published_axes':original,'our_axes':parameters,'permutation':order},
             'unclipped_boundary':real[keep].tolist()}
    for key,reference in display.items():
        case=reference['case'];r=result['scans'][case];plane=lookup[case]
        with np.load(out/r['views']['paper_window']['surface'],allow_pickle=False) as z:
            points=np.c_[z['physical_x'].ravel(),z['physical_y'].ravel()]
            own=z['delta_chi2'].ravel()<=LEVELS['90percent']
        support=np.ones(len(points),bool)
        for j,(lo,hi) in enumerate(reference['bounds']):support&=(points[:,j]>=lo)&(points[:,j]<=hi)
        paper=mask_from_outlines([np.array(p) for p in reference['polygons']],points)
        union=((own|paper)&support).sum();intersection=((own&paper)&support).sum()
        vertex=np.array(reference['unclipped_boundary'])
        delta=np.asarray(plane.cost(vertex))-r['fit']['chi2_min'] if len(vertex) else np.array([])
        records.append({'reference_id':key,'case':case,'source':reference['source'],
             'comparison_scope':'published graphical region within its original axis window; no author chi2 grid',
             'fill_rule':'even-odd outlines; preserve nested holes','axis_mapping':reference['axis_mapping'],
             'sampled_points':int(support.sum()),'intersection_over_union':float(intersection/union) if union else None,
             'own_fraction':float(own[support].mean()),'paper_fraction':float(paper[support].mean()),
             'published_unclipped_vertices':len(vertex),'own_delta_at_paper_boundary_median':float(np.median(delta)) if len(delta) else None,
             'own_delta_at_paper_boundary_5_95_percentile':np.quantile(delta,[.05,.95]).tolist() if len(delta) else None,
             'exact_paper_equivalence':'NOT_ESTABLISHED; nuclear/source/statistical approximations remain distinct'})
    for p in [p2601,p2601.with_name('PROVENANCE.json'),pc,provenance,pdf]:sources[p.relative_to(ROOT).as_posix()]=sha(p)
    previous=read(ROOT/'outputs/paper2601_chi2_corrected_20261111/SUMMARY.json')
    history=[]
    for name,key in [('CONUS_plus','CONUS_plus__NSI_ee'),('COHERENT_CsI_Ar','COHERENT_CsI_Ar_mean_errors__NSI_ee')]:
        old=previous['planes'][name]['best_fit'];point=old['coordinates']
        current=result['scans'][key]['fit']['chi2_min'];raw=float(lookup[key].cost(point))
        assert abs(raw-old['chi2'])<2e-6 and abs(current-old['chi2'])<2e-6
        history.append({'case':key,'previous_best_chi2':old['chi2'],'new_chi2_min':current,
                        'raw_objective_difference_at_previous_best':raw-old['chi2'],'scope':'same existing local model'})
    oldsolar=read(ROOT/'outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json')['primary_minimum']['minimum']
    key='Solar_joint__NSI_ee';raw=float(lookup[key].cost([oldsolar['epsilon_ee_uV'],oldsolar['epsilon_ee_dV']]))
    assert abs(raw-oldsolar['chi2'])<2e-7 and abs(result['scans'][key]['fit']['chi2_min']-oldsolar['chi2'])<2e-7
    history.append({'case':key,'previous_best_chi2':oldsolar['chi2'],'new_chi2_min':result['scans'][key]['fit']['chi2_min'],
                    'raw_objective_difference_at_previous_best':raw-oldsolar['chi2'],'scope':'same continuous-acceptance effective SNuDD model'})
    write(out/'PAPER_BOUNDARIES.json',display)
    comparison={'graphical_comparisons':records,'historical_numerical_checks':history,
                'solar_SM_reference':{'paper':'2411.11749v1 PDF pp7-8 Fig2, Eqs18-23',
                   'same_likelihood':False,'reason':'published multibin spectra versus current three fitted totals; no author numeric chi2 surface; no fabricated reference contour'},
                'COHERENT_other_flavors':{'paper':'2211.11905v2; 2601.19883v2 NSI convention',
                   'same_likelihood':False,'reason':'current nine-bin energy plus Ar mean-error model does not equal published timing/shape analysis; internal full-kernel and 1D nesting checks supplied'}}
    write(out/'REFERENCE_COMPARISON.json',comparison)
    return comparison,sources


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--skip-fresh-runtime',action='store_true',help='Explicitly mark fresh Runtime verification NOT_RUN; never imply it passed')
    args=parser.parse_args();out=args.output.resolve();result=read(out/'BENCHMARK_RESULTS.json')
    planes,sources,old=load_all_models();lookup={p.key:p for p in planes}
    assert len(result['scans'])==len(planes)==41
    print('Checking mixed-flavor full/pair kernels and independent least-squares nuisance profiles',flush=True)
    pair,gaussian=ground_checks(planes,result['scans']);nesting=nested_checks(planes,old)
    for row in nesting:
        minimum=result['scans'][row['case']]['fit']['chi2_min']
        row['expected_delta_offset_1d_minus_2d_min']-=minimum
        assert row['expected_delta_offset_1d_minus_2d_min']>=-2e-6
    contour=[]
    for key,row in result['scans'].items():
        for view,meta in row['views'].items():
            assert sha(out/meta['surface'])==meta['surface_sha256']
            assert sha(out/meta['contours'])==meta['contours_sha256']
            with np.load(out/meta['surface'],allow_pickle=False) as z:
                assert np.isfinite(z['chi2']).all()
                np.testing.assert_allclose(z['chi2']-row['fit']['chi2_min'],z['delta_chi2'],atol=2e-12,rtol=0)
            with (out/meta['contours']).open(encoding='utf-8') as f:vertices=list(csv.DictReader(f))
            selected=vertices[::max(1,len(vertices)//90)]
            if selected:
                points=np.array([[float(v['x']),float(v['y'])] for v in selected])
                raw=np.asarray(lookup[key].cost(points))-row['fit']['chi2_min']
                levels=np.array([float(v['delta_threshold']) for v in selected])
                residual=float(np.max(np.abs(raw-levels)))
                assert residual<.025
            else:residual=0.
            contour.append({'case':key,'view':view,'vertices_checked':len(selected),'max_delta_residual':residual})
    equivalence=[]
    for stem in ['NSI','NSI_mixed_ee']:
        keys=['CONUS_plus__NSI_emu','CONUS_plus__NSI_etau'] if stem=='NSI' else ['CONUS_plus__NSI_mixed_ee_emu_dV','CONUS_plus__NSI_mixed_ee_etau_dV']
        points=np.array([[.12,-.08],[-.23,.21],[.37,.11]])
        difference=float(np.max(np.abs(lookup[keys[0]].cost(points)-lookup[keys[1]].cost(points))))
        assert difference<2e-10
        equivalence.append({'cases':keys,'max_chi2_difference':difference})
    comparison,reference_sources=reference_comparison(out,result,planes)
    runtime={'status':'NOT_RUN_BY_EXPLICIT_FLAG'} if args.skip_fresh_runtime else solar_runtime_checks(planes,out)
    write(out/'qa/INDEPENDENT_CHECKS.json',{'status':'PASS_ALL_EXECUTED_NUMERICAL_CHECKS' if not args.skip_fresh_runtime else 'PARTIAL_FRESH_RUNTIME_NOT_RUN',
          'full_pair_holdouts':pair,'independent_nuisance_lstsq':gaussian,'one_d_axis_nesting':nesting,
          'refined_contour_checks':contour,'CONUS_flavor_equivalence':equivalence,'solar_runtime':runtime,
          'historical_minima':comparison['historical_numerical_checks'],
          'not_claimed':['fresh native final-grid CsI/Ar loader run','official author likelihood','coverage calibration','solar v3.5 full trace']})
    manifest=read(out/'BENCHMARK_SOURCE_MANIFEST.json');manifest.update(reference_sources)
    for p in HERE.glob('*.py'):manifest[p.relative_to(ROOT).as_posix()]=sha(p)
    write(out/'BENCHMARK_SOURCE_MANIFEST.json',manifest)
    print('Independent 2D validation complete:',len(pair),'full/pair;',len(nesting),'1D slices;',len(contour),'contour views',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
