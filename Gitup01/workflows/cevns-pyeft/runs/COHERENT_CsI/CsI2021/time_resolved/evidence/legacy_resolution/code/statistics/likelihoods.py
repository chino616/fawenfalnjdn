"""Raw-count Poisson deviance, six applicable native nuisance parameters."""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
from scipy.special import xlogy
from ..fast_counts_csi2021_time import fast_counts_csi2021_time

SIGMAS=np.array([.1145,.25,.35,.021])
NAMES=("signal_norm","brn_norm","nin_norm","ssb_norm","time_shift_us","efficiency_shift_pe")
BOUNDS=tuple([(-1/s,None) for s in SIGMAS]+[(-1.,1.),(-1.,1.)])
MODES=("energy","time_nominal","time")


def poisson_deviance(observed,expected):
    n=np.asarray(observed,float);mu=np.asarray(expected,float)
    if n.shape!=mu.shape or not np.isfinite(n).all() or np.any(n<0):
        raise ValueError("Poisson observations must be nonnegative matching counts")
    if not np.isfinite(mu).all() or np.any(mu<0) or np.any((mu==0)&(n>0)):
        return np.inf
    return float(max(0.,2*np.sum(mu-n+xlogy(n,n)-xlogy(n,mu))))


@dataclass
class TimeFit:
    chi2: float
    chi2_data: float
    chi2_prior: np.ndarray
    nuisance: np.ndarray
    expected: np.ndarray
    templates: np.ndarray
    success: bool
    attempts: list
    active_bounds: list
    mode: str

    def as_dict(self):
        return dict(chi2=self.chi2,chi2_data=self.chi2_data,
            chi2_prior=self.chi2_prior.tolist(),nuisance=dict(zip(NAMES,self.nuisance.tolist())),
            success=self.success,attempts=self.attempts,active_bounds=self.active_bounds,mode=self.mode,
            component_totals=(self.templates*np.r_[1+self.nuisance[:4]][:,None,None]).sum(axis=(1,2)).tolist(),
            native_radius_nuisance="unsupported_fixed_zero")


class TimeLikelihood:
    def __init__(self,kernel,dataset,background="raw_template_integrals",*,normalization_sigmas=None):
        if not np.array_equal(kernel.pe_edges,np.array([0,8,12,16,20,24,32,40,48,60.])):
            raise ValueError("Signal PE bins differ from observed data")
        self.kernel=kernel;self.dataset=dataset;self.background=background
        self.sigmas=np.array(SIGMAS if normalization_sigmas is None else normalization_sigmas,dtype=float,copy=True)
        if self.sigmas.shape!=(4,) or not np.isfinite(self.sigmas).all() or np.any(self.sigmas<=0):
            raise ValueError("Four finite positive normalization uncertainties are required")
        self.bounds=tuple([(-1/s,None) for s in self.sigmas]+[(-1.,1.),(-1.,1.)])

    def templates(self,point=(0.,0.),shift_us=0.,efficiency_shift_pe=0.):
        signal=fast_counts_csi2021_time(self.kernel,*point,shift_us=shift_us,
                                        efficiency_shift_pe=efficiency_shift_pe).counts_2d
        return np.array([signal,*self.dataset.backgrounds(shift_us,self.background)])

    def profile(self,point=(0.,0.),*,mode="time",observed=None,starts=(),multistart=2,maxiter=300):
        if mode not in MODES:raise ValueError("Unknown likelihood mode")
        n=np.asarray(self.dataset.observed if observed is None else observed,float)
        if n.shape!=(9,11) or np.any(n<0) or not np.isfinite(n).all():
            raise ValueError("Expected nonnegative (9,11) raw count data")
        free=4 if mode=="time_nominal" else 6
        templates_cache={}
        def templates(x):
            key=(float(x[4]),float(x[5])) if free==6 else (0.,0.)
            if key not in templates_cache:
                if len(templates_cache)>256:templates_cache.clear()
                templates_cache[key]=self.templates(point,.25*key[0],key[1])
            return templates_cache[key]
        target=n.sum(axis=1) if mode=="energy" else n
        def objective(x):
            t=templates(x)
            amps=1+self.sigmas*x[:4]
            mu=np.einsum("k,kij->ij",amps,t)
            analysis_mu=mu.sum(axis=1) if mode=="energy" else mu
            data=poisson_deviance(target,analysis_mu)
            if not np.isfinite(data):return 1e30,np.zeros_like(x)
            residual=2*(1-np.divide(target,analysis_mu,out=np.zeros_like(target),where=analysis_mu>0))
            t_used=t.sum(axis=2) if mode=="energy" else t
            g=np.empty(free)
            g[:4]=np.array([np.sum(residual*v)*s for v,s in zip(t_used,self.sigmas)])+2*x[:4]
            if free==6:
                for k in (4,5):
                    h=1e-5
                    a=x.copy();b=x.copy()
                    a[k]=min(1.,x[k]+h);b[k]=max(-1.,x[k]-h)
                    derivative=np.einsum("k,kij->ij",amps,templates(a)-templates(b))/(a[k]-b[k])
                    if mode=="energy":derivative=derivative.sum(axis=1)
                    g[k]=np.sum(residual*derivative)
            return data+float(x[:4]@x[:4]),g
        seeds=[np.asarray(s,float)[:free] for s in starts]
        # Trusted continuation may omit the redundant nominal solve; periodic
        # independent starts are still requested by the scan driver.
        if not seeds or multistart>0:seeds.append(np.zeros(free))
        if multistart>=2:seeds.append(np.array([-.4,-.2,.1,-.2,.25,.3])[:free])
        if multistart>=3:seeds.append(np.array([.4,.2,-.1,.2,-.25,-.3])[:free])
        unique=[]
        for s in seeds:
            if s.shape!=(free,):raise ValueError("Invalid nuisance start")
            if not any(np.array_equal(s,q) for q in unique):unique.append(s)
        attempts=[];solutions=[]
        for s in unique:
            opt=minimize(objective,s,jac=True,bounds=self.bounds[:free],method="L-BFGS-B",
                         options=dict(maxiter=maxiter,ftol=1e-11,gtol=2e-6,maxls=30))
            attempts.append(dict(success=bool(opt.success),message=str(opt.message),
                                 chi2=float(opt.fun),iterations=int(opt.nit),scaled=opt.x.tolist()))
            if opt.success and np.isfinite(opt.fun) and opt.fun<1e20:solutions.append(opt)
        if not solutions:
            seed=min(attempts,key=lambda r:r["chi2"])["scaled"]
            retry=minimize(lambda x:objective(x)[0],seed,bounds=self.bounds[:free],method="Powell",
                           options=dict(maxiter=maxiter,xtol=1e-7,ftol=1e-10))
            attempts.append(dict(success=bool(retry.success),message=str(retry.message),
                                 chi2=float(retry.fun),iterations=int(retry.nit),scaled=retry.x.tolist()))
            if retry.success and np.isfinite(retry.fun) and retry.fun<1e20:solutions.append(retry)
        if not solutions:raise RuntimeError("All profile attempts failed: "+str(attempts))
        best=min(solutions,key=lambda r:r.fun);x=best.x;t=templates(x)
        nu=np.r_[self.sigmas*x[:4],(.25*x[4] if free==6 else 0.),(x[5] if free==6 else 0.)]
        expected=np.einsum("k,kij->ij",1+nu[:4],t)
        data=poisson_deviance(target,expected.sum(axis=1) if mode=="energy" else expected)
        active=[NAMES[k]+":"+side for k,(lo,hi) in enumerate(self.bounds[:free])
                for side,b in (("lower",lo),("upper",hi)) if b is not None and abs(x[k]-b)<1e-5]
        return TimeFit(data+float(x[:4]@x[:4]),data,x[:4]**2,nu,expected,t,True,attempts,active,mode)


def time_deviance_decomposition(observed,expected):
    full=poisson_deviance(observed,expected)
    energy=poisson_deviance(np.sum(observed,axis=1),np.sum(expected,axis=1))
    return dict(joint_data=full,energy_data=energy,conditional_time_data=full-energy)

