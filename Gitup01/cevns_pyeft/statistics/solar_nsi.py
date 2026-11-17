"""Three independent solar pulls (2601 Eq88), joint 2D NSI inference (Delta=4.61).

The incident state is evaluated at each parameter point. In particular the final
event-rate surface is not a constant-state quadratic polynomial in epsilon.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
from scipy.optimize import differential_evolution,minimize
from scipy.ndimage import minimum_filter
from cevns_pyeft.theory.li2026.ee_vector_nsi import monomials,nsi_point


@dataclass
class SolarNSIJoint:
    experiments:tuple
    kernels:tuple

    def __post_init__(self):
        if tuple(e.model.sample for e in self.experiments)!=('PandaX_paired','PandaX_US2','XENONnT'):
            raise ValueError('three independent named solar samples required')
        self.energy=self.kernels[0].energy;self.energy_weights=self.kernels[0].energy_weights
        self.state=self.experiments[0].model.state_model
        for e,k in zip(self.experiments,self.kernels):
            if not np.array_equal(k.energy,self.energy) or e.model.state_model.describe()!=self.state.describe():
                raise ValueError('joint probability needs the same source model and energy quadrature')
            k.validate(e,k.record['numerics'],nsi_point())
        ref=next(r for r in self.experiments[0].definition.resources if r.id=='fitted_yields')
        data=json.loads(self.experiments[0].resource_catalog.resolve(ref).read_text(encoding='utf8'))
        rows=[data['samples'][e.model.sample] for e in self.experiments]
        self.D=np.array([row['D'] for row in rows]);self.sigma=np.array([row['sigma_stat'] for row in rows]);self.pull=np.array([row['pull_sigma'] for row in rows])
        self.templates=np.stack([k.values.sum(axis=0) for k in self.kernels])
        self.sm=np.einsum('sbe,e->sb',self.templates[:,:,0,:],self.energy_weights)
        self.epsilon_tail=float(self.experiments[-1].model.observation.efficiency[-1])

    def blocks(self,eu,ed,*,radial_order=None):
        pee=self.state.pee(self.energy,eu,ed,radial_order=radial_order)
        coeff=monomials(eu,ed)
        out=self.sm+np.einsum('...e,sbme,...m,e->...sb',pee,self.templates[:,:,1:,:],coeff[...,1:],self.energy_weights,optimize=True)
        if np.any(out < -1e-8*np.maximum(1.,np.max(abs(out),axis=(-1,-2),keepdims=True))):raise ValueError('negative solar NSI rate')
        return np.maximum(out,0.)

    def signals(self,eu,ed,tail_mode='flat_sensitivity',*,radial_order=None):
        b=self.blocks(eu,ed,radial_order=radial_order);low=b[...,0];high=b.sum(axis=-1)
        if tail_mode=='profile_bounds':return np.minimum(np.maximum(self.D,low),high)
        if tail_mode not in ('zero','unit','flat_sensitivity'):raise ValueError('explicit tail sensitivity model required')
        factor={'zero':0.,'unit':1.,'flat_sensitivity':self.epsilon_tail}[tail_mode]
        return low+factor*b[...,1]

    def chi2(self,eu,ed,tail_mode='flat_sensitivity',*,radial_order=None):
        s=self.signals(eu,ed,tail_mode,radial_order=radial_order)
        return np.sum((self.D-s)**2/(self.sigma**2+self.pull**2*s*s),axis=-1)

    def batch_grid(self,u,d,tail_mode='flat_sensitivity',chunk=192):
        u,d=np.broadcast_arrays(u,d);a=u.ravel();b=d.ravel();values=np.empty_like(a,dtype=float)
        for i in range(0,len(a),chunk):values[i:i+chunk]=self.chi2(a[i:i+chunk],b[i:i+chunk],tail_mode)
        return values.reshape(u.shape)

    def detail(self,u,d,tail_mode='flat_sensitivity'):
        s=self.signals(u,d,tail_mode);b=self.blocks(u,d)
        alpha=self.pull**2*s*(self.D-s)/(self.sigma**2+self.pull**2*s*s)
        data=((self.D-(1+alpha)*s)/self.sigma)**2;penalty=(alpha/self.pull)**2
        return {'epsilon_ee_uV':float(u),'epsilon_ee_dV':float(d),'chi2':float(sum(data+penalty)),
            'signal_events':s.tolist(),'signal_lower':b[:,0].tolist(),'signal_upper':b.sum(axis=-1).tolist(),
            'observed':self.D.tolist(),'sigma_stat':self.sigma.tolist(),'alpha':alpha.tolist(),
            'chi2_by_sample':(data+penalty).tolist(),'chi2_data':data.tolist(),'chi2_pull':penalty.tolist(),
            'propagation':self.state.propagation,'tail_mode':tail_mode,
            'Pee_at_2_5_10_15_MeV':self.state.pee(np.array([2.,5.,10.,15.]),u,d).tolist()}

    def certified_domain(self,tail_mode='flat_sensitivity',delta=4.61):
        """Finite full-plane search bound from positive rates and P_ee >= P_min.

        If any one sample's minimum possible signal exceeds its profiled-chi2
        upper-rate crossing at SM_chi2+Delta+margin, the point cannot be a joint
        minimum or part of the requested contour. Natural-Xe isotope diversity
        makes the integrated electron cross-section quadratic positive definite.
        """
        coefficient=self.kernels[1].integrated_electron_coefficients(0.)  # fully covered US2, no X-tail assumption
        Q=np.array([[coefficient[3],coefficient[4]/2],[coefficient[4]/2,coefficient[5]]]);linear=coefficient[1:3]
        eigen,vectors=np.linalg.eigh(Q)
        if np.any(eigen<=0):raise ValueError('cannot certify finite full-plane search from this response')
        center=-.5*np.linalg.solve(Q,linear);offset=float(coefficient[0]+linear@center+center@Q@center)
        upper=float(self.chi2(0.,0.,tail_mode));level=upper+delta+.1
        D,sigma,pull=self.D[1],self.sigma[1],self.pull[1];den=1-level*pull*pull
        if den<=0:raise ValueError('pull saturation prevents this finite-domain proof')
        crossing=(D+np.sqrt(level*(pull*pull*D*D+den*sigma*sigma)))/den
        pmin=self.state.probability_bounds[0];radius2=crossing/pmin-offset
        transform=(vectors/np.sqrt(eigen)[None,:])*np.sqrt(radius2)
        return {'center':center.tolist(),'transform':transform.tolist(),'Q_eigenvalues':eigen.tolist(),
            'electron_quadratic_coefficients':coefficient.tolist(),'electron_quadratic_minimum':offset,
            'Pee_min':float(pmin),'SM_chi2_upper_bound':upper,'excluded_chi2_level':level,
            'US2_signal_upper_crossing':float(crossing),'search_square_in_whitened_coordinates':[-1.,1.],
            'proof':'outside unit disk in whitened coordinates: N_US2 >= Pmin*N_all_electron > crossing, so joint chi2 > SM_chi2+Delta+.1; the enclosing square contains every minimum and allowed point',
            'epsilon_axis_enclosing_bounds':np.column_stack([center-np.sum(abs(transform),axis=1),center+np.sum(abs(transform),axis=1)]).tolist()}

    def minimize(self,tail_mode='flat_sensitivity',*,seeds=(17,41,83),grid_size=121):
        domain=self.certified_domain(tail_mode);center=np.array(domain['center']);matrix=np.array(domain['transform'])
        def objective(z):
            z=np.asarray(z);p=center[:,None]+matrix@z if z.ndim==2 else center+matrix@z
            return self.chi2(p[0],p[1],tail_mode)
        candidates=[]
        for seed in seeds:
            result=differential_evolution(objective,[(-1.,1.),(-1.,1.)],seed=seed,popsize=24,maxiter=550,tol=2e-10,atol=1e-11,polish=False,vectorized=True,updating='deferred')
            refined=minimize(objective,result.x,method='Nelder-Mead',options={'xatol':1e-10,'fatol':1e-12,'maxiter':2000})
            candidates.append({'method':'DE_then_NelderMead','seed':seed,'white_point':refined.x.tolist(),'chi2':float(refined.fun),'success':bool(refined.success)})
        line=np.linspace(-1,1,grid_size);xx,yy=np.meshgrid(line,line,indexing='xy')
        p=center[:,None]+matrix@np.stack([xx.ravel(),yy.ravel()]);surface=self.batch_grid(p[0],p[1],tail_mode).reshape(xx.shape)
        minima=(surface==minimum_filter(surface,size=3,mode='nearest'))
        indices=np.argwhere(minima);indices=sorted(indices,key=lambda ij:surface[tuple(ij)])[:32]
        for row,col in indices:
            result=minimize(objective,[line[col],line[row]],method='Nelder-Mead',options={'xatol':1e-10,'fatol':1e-12,'maxiter':2000})
            if np.max(abs(result.x))<=1+1e-7:
                candidates.append({'method':'independent_white_grid_local','white_point':result.x.tolist(),'chi2':float(result.fun),'success':bool(result.success)})
        best=min(candidates,key=lambda c:c['chi2']);point=center+matrix@np.array(best['white_point'])
        if np.max(np.abs(best['white_point']))>=.999:raise ValueError('minimum at certified enclosing boundary; review search')
        return {'minimum':self.detail(*point,tail_mode),'domain':domain,'searches':candidates,
            'grid_size':grid_size,'grid_raw_minimum':float(surface.min()),
            'independent_seed_spread':float(np.ptp([a['chi2'] for a in candidates if a['method']=='DE_then_NelderMead'])),
            'minimum_subtracted':'joint parameter minimum, not SM or sum of per-sample minima'}
