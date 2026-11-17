"""Onboarding Source/Detector: pinned local arrays, explicit reference choices."""
from pathlib import Path
from dataclasses import dataclass
import hashlib
import json
import numpy as np
from scipy.interpolate import make_interp_spline

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'data/benchmarks/solar_b8_reference_2601_19883'
SAMPLES=('paired','US2','xenon')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_card(path=None):
    path=Path(path or INPUT/'analysis.input.json')
    card=json.loads(path.read_text(encoding='utf8'))
    if card['schema']!='solar_b8_reference_recipe/1' or tuple(card['samples'])!=SAMPLES:
        raise ValueError('not the reviewed reference recipe')
    return card


def verified_table(path,card,name):
    if sha(path)!=card['files'][name]['sha256']:raise ValueError('reference input changed: '+name)
    a=np.loadtxt(path)
    if list(a.shape)!=card['files'][name]['shape'] or not np.all(np.isfinite(a)) or np.any(np.diff(a[:,0])<=0):
        raise ValueError('invalid reference table: '+name)
    a.setflags(write=False)
    return a


@dataclass(frozen=True)
class FixedFlavorSource:
    spectrum:np.ndarray
    probabilities:np.ndarray
    physics:object

    def splines(self):
        # Onboarding Source: supplied txt L3091-3154. Preserve the independently
        # rounded flavor probabilities rather than silently forcing their sum1.
        p=self.probabilities;s=self.spectrum;c=self.physics
        energy=np.linspace(s[0,0],s[-1,0],c['flavor_flux_nodes'])
        shape=np.interp(energy,s[:,0],s[:,1])
        return tuple(make_interp_spline(energy,shape*make_interp_spline(p[:,0],p[:,i],k=c['probability_interpolation_order'])(energy),
            k=c['flavor_flux_interpolation_order']) for i in [1,2,3])

    def describe(self):
        return {'kind':'fixed_reference_flavor_flux','spectrum':self.spectrum,'probabilities':self.probabilities,
            'flux_cm2_s':self.physics['flux_cm2_s'],'no_NSI_propagation_update':True,
            'flavor_interpolation_order':self.physics['flavor_flux_interpolation_order'],
            'flavor_flux_nodes':self.physics['flavor_flux_nodes'],
            'probability_interpolation_order':self.physics['probability_interpolation_order']}


@dataclass(frozen=True)
class ReferenceAcceptance:
    table:np.ndarray
    bounds:tuple
    energy_guard:float
    enforce_domain:bool
    minimum:float
    order:int

    def __call__(self,t):
        t=np.asarray(t,float)
        val=make_interp_spline(self.table[:,0],self.table[:,1],k=self.order)(t)
        valid=(t>self.energy_guard)&(t>=self.bounds[0])&(t<=self.bounds[1])&(val>self.minimum)
        if self.enforce_domain:valid&=(t>=self.table[0,0])&(t<=self.table[-1,0])
        return np.where(valid,val,0.)

    def describe(self):
        return {'kind':'reference_total_acceptance','table':self.table,'T_bounds_keVnr':self.bounds,
            'energy_guard_strict_gt':self.energy_guard,'enforce_table_domain':self.enforce_domain,
            'acceptance_strict_gt':self.minimum,'spline_order':self.order,
            'source':'supplied txt L3030,3040-3088; reference processing,not official XENONnT threshold',
            'ROI_already_included':True,'Qy_used':False,'ci_used':False}

