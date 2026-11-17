"""Only the adopted reference statistical semantics; no per-sample pull sum."""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq
from cevns_pyeft.experiments.runtime import validate_snapshot
from .physics import monomials


def shared_profile(signals,D,sigma,pull):
    s=np.asarray(signals,float);D=np.asarray(D,float);sigma=np.asarray(sigma,float)
    if s.shape[-1]!=3 or not np.all(np.isfinite(s)) or np.min(s)<0 or np.min(sigma)<=0 or pull<=0:
        raise ValueError('invalid3-sampleprofile inputs')
    w=1/sigma**2;diff=D-s
    alpha=np.sum(s*diff*w,axis=-1)/(np.sum(s*s*w,axis=-1)+1/pull**2)
    by_sample=((D-(1+alpha[...,None])*s)/sigma)**2
    penalty=(alpha/pull)**2
    return {'chi2':by_sample.sum(axis=-1)+penalty,'alpha':alpha,'chi2_by_sample_data':by_sample,'chi2_shared_pull':penalty}


@dataclass
class ReferenceJoint:
    experiments:tuple
    kernels:tuple
    statistical:object

    def __post_init__(self):
        if tuple(e.model.sample for e in self.experiments)!=('paired','US2','xenon'):raise ValueError('reference joint sample order differs')
        if self.statistical['normalization']!='one shared alpha':raise ValueError('reference recipe requires its declared shared nuisance')
        for e,k in zip(self.experiments,self.kernels):
            validate_snapshot(e);k.validate(e,e.definition.numerical_profiles['fast'])
        self.coefficients=np.stack([k.polynomial(e.model) for e,k in zip(self.experiments,self.kernels)])

    def signals(self,u,d):
        val=np.einsum('...m,sm->...s',monomials(u,d),self.coefficients)
        if np.min(val)<-1e-9:raise ValueError('negative quadratic physical prediction')
        return np.maximum(val,0.)

    def evaluate(self,signals):
        c=self.statistical
        return shared_profile(signals,c['D'],c['sigma_stat'],c['sigma_alpha'])

    def chi2(self,u,d):return self.evaluate(self.signals(u,d))['chi2']

    def scan(self,nodes=601):
        c=self.statistical;lo,hi=c['minimum_domain'];n=c['minimum_grid_nodes']
        sub=np.linspace(lo,hi,n);a,b=np.meshgrid(sub,sub,indexing='xy');small=self.chi2(a,b)
        ij=np.unravel_index(np.argmin(small),small.shape)
        minimum=float(small[ij]);point=[float(sub[ij[1]]),float(sub[ij[0]])]
        axis=np.linspace(lo,hi,nodes);u,d=np.meshgrid(axis,axis,indexing='xy')
        signals=self.signals(u,d);raw=self.evaluate(signals)['chi2']
        return {'epsilon_u':axis,'epsilon_d':axis,'signals':signals,'chi2':raw,'delta_chi2':raw-minimum},\
            {'minimum':minimum,'point':point,'domain':[lo,hi],'grid_nodes':n,'rule':'reference101boxminimum; not unbounded global claim'}

    def crossings(self,minimum,level):
        x=np.linspace(*self.statistical['minimum_domain'],4001)
        y=self.chi2(np.zeros_like(x),x)-minimum-level
        return [float(brentq(lambda d:float(self.chi2(0,d))-minimum-level,a,b,xtol=1e-12))
            for a,b,fa,fb in zip(x[:-1],x[1:],y[:-1],y[1:]) if fa*fb<0]

