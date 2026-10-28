"""Segmented quadrature independent of experiment names and source components."""
from dataclasses import dataclass
from types import SimpleNamespace
import numpy as np
from cevns_pyeft.contracts.validation import readonly

@dataclass(frozen=True)
class RecoilRate:
    recoil_keV: np.ndarray
    values: np.ndarray
    component_ids: tuple
    isotope_id: str
    unit: str = 'events/(kg day keVnr)'
    def __post_init__(self):
        object.__setattr__(self,'recoil_keV',readonly(self.recoil_keV))
        object.__setattr__(self,'values',readonly(self.values))
        if self.values.shape!=self.recoil_keV.shape+(len(self.component_ids),) or np.any(self.values<0):raise ValueError('rate axes/sign mismatch')


def segmented_recoil_rate(model,recoil_keV,parameters,*,n_energy,energy_range=None):
    recoil=np.asarray(recoil_keV,dtype=float)
    if np.any(~np.isfinite(recoil)) or np.any(recoil<0):raise ValueError('recoil must be finite and nonnegative')
    if int(n_energy)!=n_energy or n_energy<2:raise ValueError('n_energy must be integer >=2')
    if hasattr(model.interaction,'validate'):model.interaction.validate(SimpleNamespace(isotopes=(model.target,)),parameters)
    support=model.source.energy_support_mev
    requested=support if energy_range is None else energy_range
    breaks=np.asarray(model.source.integration_breakpoints(),dtype=float)
    nodes,weights=np.polynomial.legendre.leggauss(int(n_energy))
    rates=np.zeros((recoil.size,len(model.source.component_ids)))
    for i,t in enumerate(recoil.reshape(-1)):
        lower=max(model.interaction.kinematics.minimum_energy_MeV(model.target,float(t)),support[0],requested[0])
        upper=min(support[1],requested[1])
        if lower>=upper:continue
        segments=np.unique(np.r_[lower,breaks[(breaks>lower)&(breaks<upper)],upper])
        for a,b in zip(segments[:-1],segments[1:]):
            energy=.5*(a+b)+.5*(b-a)*nodes
            integration_weights=.5*(b-a)*weights
            state=model.source.state_at(energy,parameters=parameters.state)
            ds=model.interaction.dsigma_dT(target=model.target,energy_MeV=energy,recoil_keV=float(t),incident_state=state,parameters=parameters).values_cm2_per_keV
            for j,component in enumerate(model.source.component_ids):
                flux=np.asarray(model.source.differential_flux(component,energy),dtype=float)
                if flux.shape!=energy.shape or np.any(flux<0) or not np.all(np.isfinite(flux)):raise ValueError('invalid per-second flux')
                rates[i,j]+=float(np.dot(integration_weights,flux*ds))
    rates*=model.nuclei_per_kg*model.seconds_per_day
    return RecoilRate(recoil,rates.reshape(recoil.shape+(len(model.source.component_ids),)),model.source.component_ids,model.target.isotope_id)
