"""Conditioned searches and numerically refined two-parameter contour paths."""
from __future__ import annotations

import numpy as np
import contourpy
from scipy.ndimage import minimum_filter, label
from scipy.optimize import differential_evolution, minimize, minimize_scalar

from models import LEVELS


def grid_points(bounds, n):
    a,b=[np.linspace(*pair,n) for pair in bounds]
    x,y=np.meshgrid(a,b,indexing='xy')
    return a,b,np.stack([x,y],axis=-1)


def shared_solar_domain(planes):
    """One ellipse encloses the union of the four individual proven ellipses."""
    reference=planes[-1].domain
    center=np.array(reference['center']); matrix=np.array(reference['transform'])
    radii=[]
    for plane in planes:
        d=plane.domain
        offset=np.linalg.solve(matrix,np.array(d['center'])-center)
        relative=np.linalg.solve(matrix,np.array(d['transform']))
        radii.append(float(np.linalg.norm(offset)+np.linalg.norm(relative,ord=2)))
    scale=max(radii)*1.01
    for plane,radius in zip(planes,radii):
        original=plane.domain
        enlarged=matrix*scale
        plane.domain={**reference,'center':center.tolist(),'transform':enlarged.tolist(),
                      'individual_bound':original,'union_ellipse_radius':scale,'own_relative_radius_bound':radius,
                      'proof':'Union bound: ||Tref^-1(ci-cref)||+||Tref^-1 Ti||_2 bounds every individual enclosing ellipse. One common enlarged ellipse covers each sample and joint nominal region; no observation is pooled for their chi2.',
                      'axis_enclosing_bounds':np.column_stack([center-np.abs(enlarged).sum(axis=1),center+np.abs(enlarged).sum(axis=1)]).tolist()}


def seed_points(plane, old):
    out=[np.asarray(plane.reference,float)]
    if plane.kind=='NSI':
        for i,par in enumerate(plane.parameters):
            row=old['scans'].get(plane.analysis+'__'+par)
            if row and row['best_fit'] is not None:
                p=np.zeros(2);p[i]=row['best_fit'];out.append(p)
    else:
        s=plane.solar; a=s.angle
        if len(plane.indices)==1:
            i=plane.indices[0];out.append(np.array([a,s.D[i]/s.weak_signals(a)[i]]))
        for a in [0.,s.angle,.5,1.]:
            rates=s.weak_signals(a)[plane.indices]; w=1/s.sigma[plane.indices]**2
            f=max(0.,float(np.sum(s.D[plane.indices]*rates*w)/np.sum(rates*rates*w)))
            out.append(np.array([a,f]))
    return out


def minimize_plane(plane, old, *, coarse_values=None):
    if plane.flat:
        return {'chi2_min':float(plane.cost([0.,0.])),'best_fit':None,'degenerate_minima':[],
                'minimum_scope':'constant over entire R^2; no finite limits','searches':[]}
    bounds=plane.domain['bounds']
    low,high=np.array(bounds).T
    def objective(z):
        z=np.asarray(z,float)
        points=plane.map(z.T if z.ndim==2 and z.shape[-1]!=2 else z)
        return plane.cost(points)
    candidates=[]
    for p in seed_points(plane,old):
        z=plane.inverse(p)
        if np.all(z>=low) and np.all(z<=high):
            candidates.append({'method':'physical_seed','white_point':z.tolist(),'chi2':float(objective(z)),'success':True})
    singleton=plane.analysis!='Solar_joint' and plane.analysis in ('PandaX_paired','PandaX_US2','XENONnT')
    exact_zero=singleton and min(r['chi2'] for r in candidates)<1e-12
    if not exact_zero:
        for seed in (17,41,83):
            fit=differential_evolution(objective,bounds,seed=seed,popsize=20,maxiter=350,
                                       tol=2e-9,atol=2e-10,polish=False,vectorized=True,updating='deferred')
            fit=minimize(objective,fit.x,method='Nelder-Mead',bounds=bounds,
                         options={'xatol':2e-10,'fatol':2e-11,'maxiter':2400})
            candidates.append({'method':'conditioned_DE_then_NelderMead','seed':seed,
                               'white_point':fit.x.tolist(),'chi2':float(fit.fun),'success':bool(fit.success)})
    a,b,z=grid_points(bounds,81)
    costs=np.asarray(objective(z.reshape(-1,2))).reshape(81,81) if coarse_values is None else coarse_values
    indices=np.argwhere(costs==minimum_filter(costs,size=3,mode='nearest'))
    indices=sorted(indices,key=lambda ij:costs[tuple(ij)])[:(4 if exact_zero else 24)]
    for row,col in indices:
        fit=minimize(objective,[a[col],b[row]],method='Nelder-Mead',bounds=bounds,
                     options={'xatol':2e-10,'fatol':2e-11,'maxiter':2400})
        candidates.append({'method':'independent_81_grid_then_local','white_point':fit.x.tolist(),
                           'chi2':float(fit.fun),'success':bool(fit.success)})
    if plane.kind=='SM' and not plane.retain_pulls and not exact_zero:
        # Independent analytic least-squares fB profile, leaving only one angle.
        def profiled(a):
            rate=plane.solar.weak_signals(a)[plane.indices]
            w=1/plane.solar.sigma[plane.indices]**2; D=plane.solar.D[plane.indices]
            flux=max(0.,float(np.sum(D*rate*w)/np.sum(rate*rate*w)))
            return float(plane.cost([a,flux])),flux
        angles=np.linspace(0.,1.,1001); values=np.array([profiled(x)[0] for x in angles])
        loc=np.r_[0,np.where((values[1:-1]<=values[:-2])&(values[1:-1]<=values[2:]))[0]+1,1000]
        for j in loc:
            if j in (0,1000): a=angles[j]
            else: a=float(minimize_scalar(lambda v:profiled(v)[0],bounds=(angles[j-1],angles[j+1]),method='bounded',options={'xatol':1e-12}).x)
            c,f=profiled(a)
            candidates.append({'method':'analytic_flux_independent_angle_profile','white_point':plane.inverse([a,f]).tolist(),'chi2':c,'success':True})
    best=min(candidates,key=lambda c:c['chi2'])
    # A single Gaussian observation has a zero-cost curve; avoid implying a
    # unique best point by selecting a reproducible one from its known axis fit.
    if exact_zero:
        best=next(c for c in candidates if c['method']=='physical_seed' and c['chi2']<1e-12)
    value=0. if exact_zero else float(best['chi2'])
    degenerate=[]
    for c in candidates:
        if c['chi2']-value>2e-7: continue
        z=np.array(c['white_point'])
        if all(np.linalg.norm(z-np.array(d['white_point']))>1e-5 for d in degenerate):
            degenerate.append({'point':plane.map(z).tolist(),'white_point':z.tolist(),'chi2':c['chi2']})
    de=[c['chi2'] for c in candidates if c['method']=='conditioned_DE_then_NelderMead']
    independent=[c['chi2'] for c in candidates if c['method']=='independent_81_grid_then_local']
    difference=abs(min(independent)-value)
    if difference>3e-5: raise ValueError(f'{plane.key}: independent conditioned grid minimum disagrees: {difference}')
    if de and abs(min(de)-value)>3e-5: raise ValueError(f'{plane.key}: DE minimum disagrees')
    return {'chi2_min':value,'best_fit':plane.map(np.array(best['white_point'])).tolist(),
            'best_white_point':best['white_point'],'degenerate_minima':degenerate,'searches':candidates,
            'best_fit_semantics':plane.best_fit_semantics,
            'minimum_scope':'three seeded conditioned DE searches plus independent 81x81 grid/local refinement inside a rate-bounded domain' if de else 'nonnegative chi2 with demonstrated zero-cost ridge; representative point',
            'independent_grid_minimum_difference':difference,'DE_best_difference':None if not de else abs(min(de)-value),
            'nominal_thresholds_not_coverage_calibration':True}


def refine_paths(paths, cost, bounds, minimum, level, spacing):
    result=[]
    lo,hi=np.asarray(bounds).T
    for raw in paths:
        z=np.asarray(raw,float).copy()
        boundary=np.isclose(z,lo,atol=1e-10)|np.isclose(z,hi,atol=1e-10)
        for _ in range(5):
            residual=np.asarray(cost(z))-minimum-level
            if np.max(np.abs(residual))<5e-9: break
            h=2e-5; grad=np.empty_like(z)
            for j in (0,1):
                plus=z.copy();minus=z.copy();plus[:,j]+=h;minus[:,j]-=h
                grad[:,j]=(np.asarray(cost(plus))-np.asarray(cost(minus)))/(2*h)
            grad[boundary]=0.
            length=np.sum(grad*grad,axis=1)
            step=residual[:,None]*grad/np.maximum(length[:,None],1e-30)
            norm=np.linalg.norm(step,axis=1)
            step*=np.minimum(1.,2*spacing/np.maximum(norm,1e-30))[:,None]
            z=np.minimum(np.maximum(z-step,lo),hi)
        values=np.asarray(cost(z))-minimum
        result.append({'coordinates':z,'max_level_residual':float(np.max(np.abs(values-level))),
                       'on_boundary':boundary.any(axis=1),'actual_delta':values})
    return result


def contour_grid(plane, a,b,chi2,minimum,*,global_domain):
    delta=np.asarray(chi2)-minimum
    if float(np.min(delta)) < -2e-6: raise ValueError(f'{plane.key}: grid found a better minimum')
    if plane.flat:
        return {},{'allowed_set':'R^2','all_thresholds_unbounded':True}
    cost=(lambda z:plane.cost(plane.map(z))) if global_domain else plane.cost
    bounds=[[float(a[0]),float(a[-1])],[float(b[0]),float(b[-1])]]
    gen=contourpy.contour_generator(x=a,y=b,z=delta,line_type='Separate')
    paths={}; metrics={}
    _,_,mesh=grid_points(bounds,len(a))
    physical=plane.map(mesh) if global_domain else mesh
    for name,level in LEVELS.items():
        segments=refine_paths(gen.lines(level),cost,bounds,minimum,level,max(a[1]-a[0],b[1]-b[0]))
        paths[name]=[]
        for segment in segments:
            coordinates=segment['coordinates']; points=plane.map(coordinates) if global_domain else coordinates
            paths[name].append({**segment,'coordinates':points,'search_coordinates':coordinates})
        mask=delta<=level
        boundary=bool(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any())
        allowed=physical[mask]
        metrics[name]={'contour_paths':len(segments),'grid_connected_components':int(label(mask,np.ones((3,3)))[1]),
                       'touches_grid_boundary':boundary,'grid_allowed_fraction':float(mask.mean()),
                       'max_contour_delta_residual':max((s['max_level_residual'] for s in segments),default=0.),
                       'grid_bounding_box':None if not len(allowed) else np.column_stack([allowed.min(axis=0),allowed.max(axis=0)]).tolist(),
                       'bounding_box_meaning':'grid diagnostic for the two-parameter region; not a 1D profiled interval'}
        if metrics[name]['max_contour_delta_residual']>.025: raise ValueError(f'{plane.key}: unresolved contour refinement')
        if global_domain and plane.kind=='NSI' and boundary: raise ValueError(f'{plane.key}: region touches enclosing numerical boundary')
    return paths,metrics
