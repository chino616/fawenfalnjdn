"""Existing deterministic-PE and observed-sigma strategies on explicit models.

These algorithms were moved from dataset wrappers. Theory, recoil integration,
targets and source state still use the common contracted implementations.
"""
import numpy as np
from cevns_pyeft.contracts import Prediction, IntegrationSettings
from cevns_pyeft.rates.recoil import integrate_recoil_yield
from cevns_pyeft.rates.folding import trapezoid_weights


def recoil_grid(model, target, ns, profile):
    obs=model.observation
    edges=model.binning.axes[0].edges
    if profile=='deterministic_pe_legacy_v1':
        pe=np.linspace(edges[0],edges[-1],ns.get('n_er',obs.slow_pe_nodes),dtype=float)
        return pe/obs.pe_per_keV
    source=model.source.for_run(model.run)
    endpoint=max(max([c.support.integration_domain_MeV[1]]+[l.energy_MeV for l in c.lines]) for c in source.components)
    return np.linspace(ns['recoil_min_keV'],model.interaction.kinematics.maximum_recoil_keV(target,endpoint),ns['n_er'])


def observed_gaussian_fold(recoil, weights, edges, efficiency, observation, n_observed):
    """Original Ar sigma(observed), not a true-recoil Gaussian approximation."""
    fold=np.zeros((len(recoil),len(edges)-1))
    for i,t in enumerate(recoil):
        mean=(observation.mean_linear+observation.mean_quadratic*t)*t
        for j,(left,right) in enumerate(zip(edges[:-1],edges[1:])):
            x=np.linspace(left,right,max(2,int(n_observed)),dtype=float)
            sigma=observation.sigma_coefficient*np.sqrt(np.maximum(x,1e-300))
            smear=np.exp(-.5*((x-mean)/sigma)**2)/(np.sqrt(2*np.pi)*sigma)
            fold[i,j]=weights[i]*float(np.trapezoid(np.asarray(efficiency(x),float)*smear,x))
    return fold


def fold_weights(model, target, recoil, ns, profile):
    edges=model.binning.axes[0].edges
    obs=model.observation
    if profile=='observed_gaussian_legacy_v1':
        return observed_gaussian_fold(recoil,trapezoid_weights(recoil),edges,obs.efficiency,obs,ns['n_pe_bin'])
    pe=recoil*obs.pe_per_keV
    basis=np.eye(len(pe))
    weights=np.zeros((len(pe),len(edges)-1))
    for j,(left,right) in enumerate(zip(edges[:-1],edges[1:])):
        sub=np.r_[left,pe[(pe>left)&(pe<right)],right]
        for i,row in enumerate(basis):weights[i,j]=np.trapezoid(np.interp(sub,pe,row),sub)
    return weights*np.asarray(obs.efficiency(pe))[:,None]/obs.pe_per_keV


def predict_legacy_observable(model, point, ns, profile):
    fluence=model.source.for_run(model.run)
    parts,raw,raw_density={},{},{}
    obs=model.observation
    edges=model.binning.axes[0].edges
    # Preserve the historical deterministic isotope sum ordering exactly.
    targets=tuple(reversed(model.targets.isotopes)) if profile.startswith('deterministic') else model.targets.isotopes
    for component in fluence.components:
        if profile.startswith('deterministic'):
            pe=np.linspace(edges[0],edges[-1],obs.slow_pe_nodes,dtype=float)
            combined=np.zeros_like(pe)
        for target in targets:
            recoil=recoil_grid(model,target,ns,profile)
            value=integrate_recoil_yield(component,target,model.interaction,parameters=point,
                numerics=IntegrationSettings(n_enu=ns['n_enu']),recoil_keV=recoil)
            rate=value.values_per_keV/target.nucleus_mass_kg
            key=(component.component_id,target.isotope_id)
            if profile.startswith('deterministic'):
                density=np.asarray(obs.efficiency(pe),float)*model.targets.detector_mass_kg*(1./obs.pe_per_keV)*rate
                raw_density[key]=density
                fraction=model.targets.composition_record['fractions'][target.isotope_id]
                weighted=fraction*density
                combined+=weighted
                bins=np.array([np.trapezoid(np.interp(np.r_[a,pe[(pe>a)&(pe<b)],b],pe,weighted),
                        np.r_[a,pe[(pe>a)&(pe<b)],b]) for a,b in zip(edges[:-1],edges[1:])])
            else:
                fold=observed_gaussian_fold(recoil,trapezoid_weights(recoil),edges,obs.efficiency,obs,ns['n_pe_bin'])
                fraction=target.number_of_nuclei*target.nucleus_mass_kg/model.targets.detector_mass_kg
                bins=np.sum(rate[:,None]*fold,axis=0)*model.targets.detector_mass_kg*fraction
                raw[key]=bins
            parts[key]=bins
    counts=sum(parts.values(),np.zeros(model.binning.shape))
    return Prediction(counts,model.binning,parts,{'route':'integrated_fluence_times_nuclei','profile':profile},
        model.describe(),dict(ns),{'raw_target_counts':raw,'raw_target_density':raw_density,
                                 'pe_grid':pe if profile.startswith('deterministic') else np.array([])})
