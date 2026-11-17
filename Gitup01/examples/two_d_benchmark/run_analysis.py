"""Run 33 explicit two-dimensional SM/NSI benchmark cases, without overwrites."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import ROOT, ONE, LEVELS, TerrestrialPlane, SolarNSIPlane, load_models, read, sha, write
from plane_inference import contour_grid, grid_points, minimize_plane, shared_solar_domain


def save_contours(path, data):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(['confidence','delta_threshold','component','vertex','x','y','search_x','search_y','actual_delta_chi2','on_box_boundary'])
        for name,paths in data.items():
            for j,record in enumerate(paths):
                for k,(p,z,delta,boundary) in enumerate(zip(record['coordinates'],record['search_coordinates'],record['actual_delta'],record['on_boundary'])):
                    w.writerow([name,LEVELS[name],j,k,*p,*z,delta,int(boundary)])


def polynomial_checks(plane):
    rows=[]
    points=[[-.317,.117],[.271,-.083],[1.77,-1.43],[-9.3,8.27]]
    if not plane.flat: points.append(plane.map([.37,-.21]).tolist())
    for point in points:
        calculated=plane.signals(point)
        for route,approx in zip(plane.routes,calculated):
            exact=plane.direct_signal(route,*point)
            delta=float(np.max(np.abs(exact-approx)))
            tolerance=2e-7+2e-10*max(1.,float(np.max(np.abs(exact))))
            if delta>tolerance: raise ValueError(f'{plane.key}: mixed-coupling polynomial holdout differs')
            rows.append({'analysis':plane.analysis,'flavor':plane.flavor,'channel':route.name,'point':point,
                         'max_events_difference':delta,'tolerance':tolerance})
    return rows


def shared_solar_values(planes, points, title):
    flat=points.reshape(-1,2); values=np.empty((4,len(flat)))
    start=time.perf_counter()
    for first in range(0,len(flat),8192):
        signals=planes[0].signals(flat[first:first+8192])
        for j,plane in enumerate(planes):
            values[j,first:first+len(signals)]=plane.solar.profile(signals,plane.indices)
        if first==0 or first//65536!=(first+len(signals))//65536 or first+len(signals)==len(flat):
            print(f'{title}: {first+len(signals)}/{len(flat)} points; all four sample objectives, {time.perf_counter()-start:.1f}s',flush=True)
    return values.reshape((4,*points.shape[:-1]))


def local_grid(plane,n):
    return grid_points([[-1.,1.],[-1.,1.]] if plane.kind=='NSI' else [[.08,.5],[0.,3.4]],n)


def save_case(out,plane,minimum,global_grid,global_values,local_values,n):
    a,b,z=global_grid; physical=plane.map(z)
    local_a,local_b,local_points=local_grid(plane,n)
    if local_values is None: local_values=plane.cost(local_points.reshape(-1,2)).reshape(n,n)
    views={}
    for name,x,y,mesh,values,is_global in [
        ('global',a,b,physical,global_values,True),
        ('paper_window',local_a,local_b,local_points,local_values,False)]:
        delta=values-minimum['chi2_min']
        surface=out/'surfaces'/(plane.key+'__'+name+'.npz')
        np.savez_compressed(surface,axis_a=x,axis_b=y,physical_x=mesh[...,0],physical_y=mesh[...,1],chi2=values,delta_chi2=delta)
        paths,metrics=contour_grid(plane,x,y,values,minimum['chi2_min'],global_domain=is_global)
        csv_path=out/'contours'/(plane.key+'__'+name+'.csv')
        save_contours(csv_path,paths)
        views[name]={'surface':surface.relative_to(out).as_posix(),'surface_sha256':sha(surface),
                     'contours':csv_path.relative_to(out).as_posix(),'contours_sha256':sha(csv_path),
                     'coordinate_system':'conditioned enclosing domain mapped to physical points' if is_global else 'physical display rectangle',
                     'shape':list(values.shape),'grid_raw_minimum':float(values.min()),
                     'local_minimum_offset_from_2d_best':float(values.min()-minimum['chi2_min']),
                     'region_metrics':metrics}
    row={'analysis':plane.analysis,'kind':plane.kind,'parameters':plane.parameters,
         'flavor':getattr(plane,'flavor',None),'mode':getattr(plane,'mode','same_existing_nuisance_model'),
         'status':'FLAT_ENTIRE_REAL_PLANE' if plane.flat else 'COMPLETED_DECLARED_LOCAL_MODEL',
         'domain':plane.domain,'fit':minimum,'reference_point':plane.reference,
         'reference_chi2':float(plane.cost(plane.reference)),'views':views,
         'nominal_thresholds_2d':LEVELS,'best_fit_semantics':plane.best_fit_semantics,
         'scientific_acceptance':'NOT_REVIEWED; approximate local model, not author likelihood certification'}
    write(out/'models'/(plane.key+'.json'),row)
    if isinstance(plane,TerrestrialPlane):
        np.savez_compressed(out/'models'/(plane.key+'_coefficients.npz'),**{r.name:p for r,p in zip(plane.routes,plane.polynomials)})
    print(f"Finished {plane.key}: chi2={minimum['chi2_min']:.10f}; point={minimum['best_fit']}",flush=True)
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--grid-size',type=int,default=601)
    args=parser.parse_args();out=args.output.resolve();n=args.grid_size
    if (out/'RESULTS.json').exists(): raise FileExistsError('Completed results are immutable; choose a new run')
    out.mkdir(parents=True,exist_ok=True)
    for folder in ['models','surfaces','contours','qa']:(out/folder).mkdir(exist_ok=True)
    started=time.perf_counter();planes,sources,old=load_models()
    print(f'Loaded {len(planes)} cases; unchanged 1D model inputs; {n}x{n} full and display grids',flush=True)
    result={'date':'2026-11-13','claim_level':'approximate local-model two-parameter benchmark',
            'thresholds_2d':LEVELS,'scans':{},'inference':'two physical coordinates at once; other physics coordinates fixed; same independent Gaussian nuisance profiles; subtract each plane own conditioned two-dimensional minimum',
            'not_run':old['not_run'],'one_d_source_results_sha256':sha(ONE/'RESULTS.json'),
            'solar_model':old['solar_method'],'nominal_threshold_coverage':'not calibrated by toys; single-yield ridges, FCNC nonregularity and physical boundaries explicitly retained'}
    result['not_run']['GF_and_oscillation_parameter_scans']='Held fixed; this task adopts NSI u/d pairs and the solar weak-angle/flux pair'
    result['not_run']['all_experiments_stacked']='No newly adopted all-experiment correlation contract; energy/time CsI observations overlap'
    validation=[]
    for plane in [p for p in planes if isinstance(p,TerrestrialPlane)]:
        validation+=polynomial_checks(plane)
        minimum=minimize_plane(plane,old)
        a,b,z=grid_points(plane.domain['bounds'],n)
        values=plane.cost(plane.map(z).reshape(-1,2)).reshape(n,n)
        result['scans'][plane.key]=save_case(out,plane,minimum,(a,b,z),values,None,n)
        write(out/'PARTIAL_RESULTS.json',result)
    solar_planes=[p for p in planes if isinstance(p,SolarNSIPlane)]
    shared_solar_domain(solar_planes)
    a,b,z=grid_points(solar_planes[0].domain['bounds'],81)
    coarse=shared_solar_values(solar_planes,solar_planes[0].map(z),'Solar NSI coarse search')
    minima=[minimize_plane(p,old,coarse_values=c) for p,c in zip(solar_planes,coarse)]
    a,b,z=grid_points(solar_planes[0].domain['bounds'],n)
    global_values=shared_solar_values(solar_planes,solar_planes[0].map(z),'Solar NSI full domain')
    la,lb,lp=local_grid(solar_planes[0],n)
    display_values=shared_solar_values(solar_planes,lp,'Solar NSI paper window')
    for j,plane in enumerate(solar_planes):
        result['scans'][plane.key]=save_case(out,plane,minima[j],(a,b,z),global_values[j],display_values[j],n)
        write(out/'PARTIAL_RESULTS.json',result)
    for plane in [p for p in planes if p.kind=='SM']:
        minimum=minimize_plane(plane,old)
        a,b,z=grid_points(plane.domain['bounds'],n)
        values=plane.cost(plane.map(z).reshape(-1,2)).reshape(n,n)
        result['scans'][plane.key]=save_case(out,plane,minimum,(a,b,z),values,None,n)
        write(out/'PARTIAL_RESULTS.json',result)
    assert len(result['scans'])==33
    result['wall_seconds']=time.perf_counter()-started
    write(out/'RESULTS.json',result)
    write(out/'qa/POLYNOMIAL_HOLDOUTS.json',{'status':'PASS_MIXED_COUPLING_POINT_CHECKS','holdouts':validation,
          'scope':'fresh 2D polynomial versus original shared full-kernel contraction; not a fresh final-grid native Slow run'})
    for p in HERE.glob('*.py'):sources[p.relative_to(ROOT).as_posix()]=sha(p)
    write(out/'SOURCE_MANIFEST.json',sources)
    print(f'Completed all 33 cases in {result["wall_seconds"]:.1f}s',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
