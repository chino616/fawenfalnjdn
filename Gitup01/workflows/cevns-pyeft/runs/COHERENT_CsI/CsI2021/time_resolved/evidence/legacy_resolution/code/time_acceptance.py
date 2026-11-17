"""Counting-layer time selection, separate from source energy/time definitions.

This adapter consumes counts BEFORE time selection. It never evaluates a
cross section, target mass, POT or energy detector response. Normalization
and the input energy-fluence scope must be declared explicitly.
"""
from dataclasses import dataclass
from types import MappingProxyType
from pathlib import Path
import hashlib,json
import numpy as np

@dataclass(frozen=True)
class CsITimeEfficiency:
    start_us: float=.52
    rate_per_us: float=.0494

    def __post_init__(self):
        if not np.isfinite(self.start_us) or not np.isfinite(self.rate_per_us) or self.rate_per_us<0:
            raise ValueError("Invalid time-efficiency constants")

    def __call__(self,t_us):
        t=np.asarray(t_us,dtype=float)
        if not np.isfinite(t).all():raise ValueError("Nonfinite observer time")
        v=np.exp(-self.rate_per_us*np.maximum(t-self.start_us,0.))
        return float(v) if t.ndim==0 else v

    def integral(self,lo_us,hi_us):
        lo,hi=np.broadcast_arrays(np.asarray(lo_us,float),np.asarray(hi_us,float))
        if not np.isfinite(lo).all() or not np.isfinite(hi).all() or np.any(hi<lo):
            raise ValueError("Invalid time-efficiency integration interval")
        if self.rate_per_us==0:return hi-lo
        plain=np.maximum(np.minimum(hi,self.start_us)-lo,0.)
        exp_lo=np.maximum(lo,self.start_us)
        width=np.maximum(hi-exp_lo,0.)
        return plain+np.exp(-self.rate_per_us*(exp_lo-self.start_us))*(-np.expm1(-self.rate_per_us*width))/self.rate_per_us

    @property
    def metadata(self):
        return {"model":"CsI_piecewise_exponential","start_us":self.start_us,"rate_per_us":self.rate_per_us}

def _accepted_full_support_integrals(profile,edges_us,shift_us,efficiency):
    shifted=profile.edges_us+shift_us
    density=profile.bin_masses/np.diff(profile.edges_us)/profile.total_mass
    out=[]
    for a,b in zip(edges_us[:-1],edges_us[1:]):
        lo=np.maximum(shifted[:-1],a);hi=np.minimum(shifted[1:],b);valid=hi>lo
        widths=hi[valid]-lo[valid]
        integral=widths if efficiency is None else np.asarray(efficiency.integral(lo[valid],hi[valid]),float)
        if integral.shape!=widths.shape or not np.isfinite(integral).all() or np.any(integral<0) or np.any(integral>widths+1e-12):
            raise ValueError("Time efficiency must integrate to a finite value between zero and interval width")
        out.append(np.dot(density[valid],integral))
    return np.asarray(out,float)

@dataclass(frozen=True)
class TimeWeightTable:
    components: tuple[str,...]
    time_edges_us: np.ndarray
    shape_weights: np.ndarray
    fluence_conversion: np.ndarray
    reference_fractions: np.ndarray
    metadata: dict

    def __post_init__(self):
        for name in ["time_edges_us","shape_weights","fluence_conversion","reference_fractions"]:
            array=np.array(getattr(self,name),float,copy=True)
            if not np.isfinite(array).all():raise ValueError("Invalid time-weight data")
            array.flags.writeable=False;object.__setattr__(self,name,array)
        if self.shape_weights.shape!=(len(self.components),len(self.time_edges_us)-1):
            raise ValueError("Time weights have incompatible component/bin shape")
        if self.fluence_conversion.shape!=(len(self.components),) or self.reference_fractions.shape!=(len(self.components),):
            raise ValueError("Time weight fluence factors have incompatible shape")
        if np.any(np.diff(self.time_edges_us)<=0) or np.any(self.shape_weights<0) or np.any(self.fluence_conversion<=0) or np.any(self.reference_fractions<=0):
            raise ValueError("Invalid time weights or reference factors")
        object.__setattr__(self,"metadata",MappingProxyType(dict(self.metadata)))

    @property
    def effective_weights(self):
        result=self.shape_weights*self.fluence_conversion[:,None]
        result.flags.writeable=False
        return result

    @property
    def fingerprint(self):
        contract=dict(self.metadata)
        contract["components"]=list(self.components)
        contract["time_edges_us"]=self.time_edges_us.tolist()
        contract["shape_weights"]=self.shape_weights.tolist()
        contract["fluence_conversion"]=self.fluence_conversion.tolist()
        return hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    def apply(self,counts_before_time,*,counts_include_time_acceptance):
        """Return (...,component,PE,time); never silently discard source labels.

        Input must be (component,PE) or (target,component,PE). If only a final
        9-bin total or an already accepted fast kernel is available, the
        components before time selection must be computed/rebuilt first.
        """
        if counts_include_time_acceptance is not False:
            raise ValueError("Supply counts BEFORE time selection; do not multiply old acceptance again")
        values=np.asarray(counts_before_time,float)
        if values.ndim not in (2,3) or values.shape[-2]!=len(self.components):
            raise ValueError("Expected (component,PE) or (target,component,PE) energy counts")
        if not np.isfinite(values).all() or np.any(values<0):
            raise ValueError("Energy counts must be finite and nonnegative")
        return values[...,None]*self.effective_weights[:,None,:]

def build_time_weights(time_source,time_edges_us,*,efficiency,shift_us=0.,
                       template_normalization,energy_fluence_scope,reference_window_us=None):
    """Build normalized source-time integrals and a separate fluence conversion.

    Let h be full-support normalized, q_ref=integral_ref h. If the template
    is h/q_ref and input counts use FULL fluence, the conversion is q_ref.
    Thus changing the representation alone cannot create extra events.

    Input counts based on REFERENCE-WINDOW fluence use q_input=q_ref;
    full-support input counts use q_input=1. The effective coefficient is
    integral_bin h*efficiency / q_input, independent of template convention.
    """
    names={"full_support","reference_window"}
    if template_normalization not in names or energy_fluence_scope not in names:
        raise ValueError("Declare template normalization and input fluence scope explicitly")
    edges=np.asarray(time_edges_us,float)
    if edges.ndim!=1 or len(edges)<2 or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0):
        raise ValueError("Observed time edges must be finite and strictly increasing")
    if not np.isfinite(shift_us):raise ValueError("Nonfinite time shift")
    if "reference_window" in (template_normalization,energy_fluence_scope) and reference_window_us is None:
        raise ValueError("Reference-window normalization requires explicit reference_window_us")
    window=None if reference_window_us is None else np.asarray(reference_window_us,float)
    if window is not None and (window.shape!=(2,) or not np.isfinite(window).all() or window[1]<=window[0]):
        raise ValueError("Invalid reference time window")
    shape=[];conversion=[];fractions=[]
    for component in time_source.components:
        profile=time_source.profile(component)
        q=1. if window is None else profile.reference_fraction(window)
        qt=1. if template_normalization=="full_support" else q
        qi=1. if energy_fluence_scope=="full_support" else q
        accepted=_accepted_full_support_integrals(profile,edges,float(shift_us),efficiency)
        shape.append(accepted/qt);conversion.append(qt/qi);fractions.append(q)
    eff_meta={"model":"identity"} if efficiency is None else dict(efficiency.metadata)
    metadata={"time_unit":"us","reference_window_us":None if window is None else window.tolist(),
              "template_normalization":template_normalization,"energy_fluence_scope":energy_fluence_scope,
              "fluence_conversion_rule":"q_template/q_input",
              "fixed_nominal_reference_denominator":True,"positive_shift":"source delayed, observer window/efficiency fixed",
              "efficiency":eff_meta,"shift_us":float(shift_us),
              "source_root_sha256":time_source.provenance["raw_sha256"],
              "source_cache_sha256":time_source.provenance["cache_sha256"],
              "time_acceptance_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return TimeWeightTable(tuple(time_source.components),edges,np.array(shape),np.array(conversion),np.array(fractions),metadata)



# Reused from the previously validated Response time2d branch: exact CDF
# primitives for fast shifted time-efficiency integration. No source rescaling.
class TimeMassCDF:
    """Exact primitives of a piecewise constant bin-mass template."""
    def __init__(self,mass,edges):
        self.edges=np.asarray(edges,np.longdouble)
        self.density=np.asarray(mass,np.longdouble)/np.diff(self.edges)
        self.plain=np.r_[np.longdouble(0),np.cumsum(mass,dtype=np.longdouble)]
        exp_mass=self.density*np.exp(-.0494*self.edges[:-1])*(-np.expm1(-.0494*np.diff(self.edges)))/.0494
        self.exp=np.r_[0.,np.cumsum(exp_mass)]
        self.plain_tail=np.r_[np.cumsum(np.asarray(mass,np.longdouble)[::-1])[::-1],0.]
        self.exp_tail=np.r_[np.cumsum(exp_mass[::-1])[::-1],0.]
    def primitive(self,x,exponential=False):
        x=np.asarray(x,np.longdouble)
        idx=np.clip(np.searchsorted(self.edges,x,side="right")-1,0,len(self.density)-1)
        lo=self.edges[idx]; dx=np.clip(x-lo,0,self.edges[idx+1]-lo)
        if exponential:
            v=self.exp[idx]+self.density[idx]*np.exp(-.0494*lo)*(-np.expm1(-.0494*dx))/.0494
            total=self.exp[-1]
        else:
            v=self.plain[idx]+self.density[idx]*dx
            total=self.plain[-1]
        return np.where(x<=self.edges[0],0,np.where(x>=self.edges[-1],total,v))
    def tail(self,x,exponential=False):
        x=np.asarray(x,np.longdouble)
        idx=np.clip(np.searchsorted(self.edges,x,side="right")-1,0,len(self.density)-1)
        lo=np.maximum(x,self.edges[idx]); dx=np.maximum(self.edges[idx+1]-lo,0)
        if exponential:
            v=self.exp_tail[idx+1]+self.density[idx]*np.exp(-.0494*lo)*(-np.expm1(-.0494*dx))/.0494
            total=self.exp[-1]
        else:
            v=self.plain_tail[idx+1]+self.density[idx]*dx
            total=self.plain[-1]
        return np.where(x<=self.edges[0],total,np.where(x>=self.edges[-1],0,v))
    def difference(self,a,b,exponential=False):
        pa=self.primitive(a,exponential); pb=self.primitive(b,exponential)
        total=self.exp[-1] if exponential else self.plain[-1]
        return np.where(pa>total/2,self.tail(a,exponential)-self.tail(b,exponential),pb-pa)
    def integral(self,observed_edges,shift_us=0.):
        edges=np.asarray(observed_edges,np.longdouble)
        lo=edges[:-1]; hi=edges[1:]
        split=np.clip(.52,lo,hi)
        plain=self.difference(lo-shift_us,split-shift_us)
        exp=self.difference(split-shift_us,hi-shift_us,True)
        return np.asarray(plain+np.exp(np.longdouble(-.0494)*(shift_us-.52))*exp,dtype=float)
