"""Shared nuclear Response, direct Tr(rho K) Slow, and signed bilinear kernel.

Only the reference-specific source, acceptance, units and quadrature live here.
The existing nuclear matching/amplitude/cross-section code is reused unchanged.
"""
from dataclasses import dataclass
import json
import numpy as np
from scipy.interpolate import make_interp_spline
from cevns_pyeft.contracts import TheoryPoint
from cevns_pyeft.experiments.definition import digest
from cevns_pyeft.rates.differential import differential_flavor_kernel_nn
from cevns_pyeft.theory.li2026.flavor import contract_density_kernel_grid

BASIS=((6,1,'u'),(6,1,'d'),(6,2,'u'),(6,2,'d'))


def monomials(u,d):
    u,d=np.broadcast_arrays(np.asarray(u,float),np.asarray(d,float))
    if not np.all(np.isfinite(u)) or not np.all(np.isfinite(d)):raise ValueError('finite real NSI parameters required')
    return np.stack([np.ones_like(u),u,d,u*u,u*d,d*d],axis=-1)


def reference_point(u=0.,d=0.,*,gf=1.1664e-5,angle=.2312):
    monomials(u,d)
    return TheoryPoint({(6,1,'u'):np.diag([-np.sqrt(2)*gf*float(u),0.,0.]),
                        (6,1,'d'):np.diag([-np.sqrt(2)*gf*float(d),0.,0.])},sin2thetaW=angle)


def coefficients(model,point):
    """Total SM+NP LEFT matrices from this recipe's explicit GF and weak angle."""
    c=model.physics
    if not point.include_sm or point.state.values or point.sin2thetaW!=c['sin2thetaW']:
        raise ValueError('reference recipe fixes SM constants and propagation; use its explicit point factory')
    angle=c['sin2thetaW'];g=c['GF_GeV_minus2']/np.sqrt(2)
    C=np.broadcast_to(np.array([-g*(1-8*angle/3),g*(1-4*angle/3),g,-g]),(3,4)).copy()
    if set(point.wc_triplets)-set(BASIS[:2]):raise ValueError('only real electron-flavor vector u,d NSI supported')
    for i,key in enumerate(BASIS[:2]):
        matrix=np.asarray(point.wc_triplets.get(key,np.zeros((3,3))),complex)
        if matrix.shape!=(3,3) or not np.all(np.isfinite(matrix)):raise ValueError('finite3x3Wilson matrices required')
        rest=matrix.copy();rest[0,0]=0
        if np.any(rest!=0) or matrix[0,0].imag:raise ValueError('offdiagonal,mu/tau or complex NSI outside reference recipe')
        C[0,i]+=matrix[0,0].real
    return C


def grid(model,t,n_enu):
    # Reference approximate Emin, in MeV. The shared cross section retains its
    # own physical support check. This is the supplied txt L3170 convention.
    lo=np.sqrt(model.physics['A']*model.physics['kinematic_amu_GeV']*t/2)
    return np.linspace(lo,float(model.source.spectrum[-1,0]),n_enu)


def normalization(model):
    c=model.physics
    return c['kg_per_tonne']/(c['A']*c['kg_per_A_u'])*c['year_days']*c['seconds_per_day']*model.exposure_tyr*c['flux_cm2_s']


def integrate_energy(e,values,order):
    return make_interp_spline(e,values,k=order,axis=0).integrate(float(e[0]),float(e[-1]))


def slow_flavors(model,point,numerics):
    """Actual full3x3flavor kernel API and validated trace at every E,T node."""
    C=coefficients(model,point);wc={key:np.diag(C[:,i]) for i,key in enumerate(BASIS)}
    t=np.linspace(*model.observation.bounds,numerics['n_er']);fluxes=model.source.splines()
    density=np.empty((len(t),3));trace_errors=[]
    for j,recoil in enumerate(t):
        e=grid(model,float(recoil),numerics['n_enu'])
        f=np.stack([s(e) for s in fluxes],axis=-1)
        if np.min(f)<-1e-14:raise ValueError('negative interpolated flavor source')
        f=np.maximum(f,0.);mag=f.sum(axis=-1)
        rho=np.zeros((len(e),3,3),complex)
        normalized=np.divide(f,mag[:,None],out=np.full_like(f,1/3),where=mag[:,None]>0)
        rho[:,np.arange(3),np.arange(3)]=normalized
        K=differential_flavor_kernel_nn(model.interaction._responses['Xe131'],float(recoil),e,
            wc_triplets=wc,include_sm=False).kernel_cm2_per_keV
        total=mag*contract_density_kernel_grid(rho,K)
        flavors=f*np.diagonal(K,axis1=-2,axis2=-1).real
        trace_errors.append(float(np.max(abs(total-flavors.sum(axis=-1)))/max(float(np.max(abs(total))),1e-100)))
        density[j]=integrate_energy(e,flavors,model.physics['E_integrand_interpolation_order'])
    flavors=normalization(model)*np.trapezoid(density*model.observation(t)[:,None],t,axis=0)
    if np.min(flavors)<0:raise ValueError('negative integrated physical signal')
    return flavors,{'max_trace_vs_flavor_sum_relative_error':max(trace_errors),
        'flavor_kernel':'differential_flavor_kernel_nn','contraction':'contract_density_kernel_grid:Tr(rho K)',
        'reference_probability_sum_in_source':True}


@dataclass(frozen=True)
class ReferenceKernel:
    matrices:np.ndarray
    physical_fingerprint:str
    numerics:object

    def __post_init__(self):
        a=np.array(self.matrices,float,copy=True)
        if a.shape!=(3,4,4) or not np.all(np.isfinite(a)) or not np.allclose(a,a.swapaxes(-1,-2),rtol=1e-12,atol=1e-20):
            raise ValueError('invalid flavor-resolved signed bilinear kernel')
        a.setflags(write=False);object.__setattr__(self,'matrices',a)

    def validate(self,experiment,numerics):
        if self.physical_fingerprint!=experiment.physics_fingerprint or dict(numerics)!=dict(self.numerics):
            raise ValueError('stale or wrong reference kernel: physical identity or numerical profile differs')

    def flavors(self,model,point):
        C=coefficients(model,point)
        values=np.einsum('fi,fij,fj->f',C,self.matrices,C)
        if np.min(values)<-1e-10:raise ValueError('negative bilinear physical prediction')
        return np.maximum(values,0.)

    def polynomial(self,model):
        C=coefficients(model,TheoryPoint(sin2thetaW=model.physics['sin2thetaW']))
        h=self.matrices[0];s=-np.sqrt(2)*model.physics['GF_GeV_minus2']
        return np.array([np.einsum('fi,fij,fj->',C,self.matrices,C),2*s*h[0]@C[0],2*s*h[1]@C[0],s*s*h[0,0],2*s*s*h[0,1],s*s*h[1,1]])

    def save(self,path):
        record={'representation':'reference_fixed_flavor_full_bilinear/1','physical_fingerprint':self.physical_fingerprint,'numerics':dict(self.numerics)}
        np.savez_compressed(path,matrices=self.matrices,record=np.array(json.dumps(record)),
            integrity=np.array(digest({'record':record,'matrices':self.matrices})))

    @classmethod
    def load(cls,path):
        with np.load(path,allow_pickle=False) as z:
            a=z['matrices'];r=json.loads(str(z['record']))
            if r['representation']!='reference_fixed_flavor_full_bilinear/1' or str(z['integrity'])!=digest({'record':r,'matrices':a}):
                raise ValueError('corrupt or wrong reference kernel representation')
            return cls(a,r['physical_fingerprint'],r['numerics'])


def compile_reference(experiment,numerics):
    m=experiment.model;t=np.linspace(*m.observation.bounds,numerics['n_er']);splines=m.source.splines()
    density=np.zeros((len(t),3,4,4))
    for j,recoil in enumerate(t):
        e=grid(m,float(recoil),numerics['n_enu'])
        H=m.interaction.coefficient_dsigma(target=m.target,energy_MeV=e,recoil_keV=float(recoil),basis_keys=BASIS).sum(axis=1).real
        for f,s in enumerate(splines):
            density[j,f]=integrate_energy(e,H*s(e)[:,None,None],m.physics['E_integrand_interpolation_order'])
    h=normalization(m)*np.trapezoid(density*m.observation(t)[:,None,None,None],t,axis=0)
    return ReferenceKernel(h,experiment.physics_fingerprint,dict(numerics))

