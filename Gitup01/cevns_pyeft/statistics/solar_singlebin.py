"""2601.19883v2 PDF p20 Eq.(88), fitted-signal Gaussian, independent pull.

Inputs are the experimental fit's signal yield D and statistical sigma, NOT
integer candidate counts, backgrounds or Poisson errors from the multibin route.
"""
import json
import numpy as np
from .profiling import ProfileResult


def profile(signal, observed, sigma, pull_sigma=.12):
    values = np.array([signal, observed, sigma, pull_sigma], float)
    if not np.all(np.isfinite(values)) or signal < 0 or sigma <= 0 or pull_sigma <= 0:
        raise ValueError('finite nonnegative signal and positive sigmas required')
    denominator = sigma*sigma+pull_sigma*pull_sigma*signal*signal
    alpha = pull_sigma*pull_sigma*signal*(observed-signal)/denominator
    data = ((observed-(1+alpha)*signal)/sigma)**2
    penalty = (alpha/pull_sigma)**2
    return ProfileResult(float(data+penalty), float(alpha), 0., float(data), float(penalty),
                         message='analytic independent Gaussian normalization pull, R1 Eq.88')


def evaluate(experiment, prediction):
    if experiment.definition.statistics.kind != 'singlebin_fitted_signal_gaussian' or prediction.counts.shape != (1,):
        raise ValueError('requires the independent fitted-signal single-bin definition')
    if not prediction.combined_prediction.diagnostics['coverage_complete']:
        raise ValueError('partial acceptance integral cannot enter the full single-bin likelihood')
    ref = next(r for r in experiment.definition.resources if r.id == 'fitted_yields')
    data = json.loads(experiment.resource_catalog.resolve(ref).read_text(encoding='utf8'))
    if data.get('schema') != 'solar_b8_fitted_signal_yields/1':
        raise ValueError('not fitted signal-yield data')
    row = data['samples'][experiment.model.sample]
    if row['meaning'] != 'fitted_signal_yield' or row['unit'] != 'events':
        raise ValueError('raw candidate/background data cannot substitute fitted signal yields')
    return profile(float(prediction.counts[0]), row['D'], row['sigma_stat'], row['pull_sigma'])
