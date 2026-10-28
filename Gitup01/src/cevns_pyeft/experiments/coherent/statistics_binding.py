"""Statistics chosen by the bound dataset definition, not runtime ID routing."""
import numpy as np
from cevns_pyeft.statistics.datasets import BinnedDataset
from cevns_pyeft.statistics.observables import observable, prediction_vector
from cevns_pyeft.statistics.profiling import profile_gaussian_one_pull, profile_gaussian_two_pull, profile_ar2020_irls


def dataset(definition, resources=None):
    s, obs = definition.statistics, definition.observation
    if s.observed:
        observed = np.asarray(s.observed)
        lower,upper = np.asarray(s.lower),np.asarray(s.upper)
        uncertainty = np.asarray(s.uncertainty) if s.uncertainty else None
    else:
        if resources is None:
            from ..loader import ResourceCatalog
            from pathlib import Path
            resources = ResourceCatalog(Path(__file__).resolve().parents[4])
        paths = {r.id:resources.resolve(r) for r in definition.resources if r.role=='statistics'}
        values = {key:np.loadtxt(path)[:,1].astype(float) for key,path in paths.items()}
        observed,lower,upper = values['data'],values['lower'],values['upper']
        uncertainty = np.clip(.5*((upper-observed)+(observed-lower)),1e-12,None)
    per_width = s.observable_unit == 'counts/PE'
    return BinnedDataset(definition.dataset_id,observed,observable(s.observable_name,s.observable_unit,obs.edges),
        background=np.asarray(s.background) if s.background else None, uncertainty=uncertainty,
        lower=lower if len(lower) else None,upper=upper if len(upper) else None,
        signal_norm_sigma=s.signal_sigma, background_norm_sigma=s.background_sigma,
        uncertainty_kind='asymmetric' if s.kind=='asymmetric_irls' else 'symmetric',
        metadata={'status':s.status, 'analysis_revision':definition.analysis_revision})


def evaluate(exp, prediction):
    s = exp.definition.statistics
    ds = dataset(exp.definition, exp.resource_catalog)
    values = prediction.counts
    if s.observable_unit=='counts/PE':
        values = values/np.diff(exp.definition.observation.edges)
    if s.kind=='gaussian_two_pull':
        return profile_gaussian_two_pull(values,ds.observed,ds.background,ds.uncertainty,sigma_alpha=s.signal_sigma,sigma_beta=s.background_sigma)
    if s.kind=='gaussian_one_pull':
        return profile_gaussian_one_pull(values,ds.observed,ds.uncertainty,sigma_alpha=s.signal_sigma)
    if s.kind=='asymmetric_irls':
        return profile_ar2020_irls(values,ds.observed,ds.background,ds.lower,ds.upper,sigma_alpha=s.signal_sigma,sigma_beta=s.background_sigma)
    raise ValueError('unsupported bound statistical model')
