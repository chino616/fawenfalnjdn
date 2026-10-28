"""Ar2020 authority; preserve the historical observable convention."""
from dataclasses import dataclass
import numpy as np
from ..definition import ExperimentDefinition, SNSRun, ResourceRef, ObservationDefinition, StatisticsDefinition

@dataclass(frozen=True)
class Ar2020Settings:
    run: SNSRun = SNSRun(24.,27.5,1.38e23,.09)
    mass_kg: float = 24.
    target_id: str = 'Ar40'
    response_key: str = 'Ar40'
    mean_linear: float = .246
    mean_quadratic: float = .00078
    sigma_coefficient: float = .58
    efficiency_columns: tuple = (0,2)
    efficiency_low: float = 0.
    c10_mass_mode: str = 'quark_mass_resolved'
    implementation_modules: tuple = ('cevns_pyeft.experiments.coherent.execution', 'cevns_pyeft.experiments.coherent.sns', 'cevns_pyeft.rates.counts', 'cevns_pyeft.rates.differential', 'cevns_pyeft.nuclear.response', 'cevns_pyeft.theory.li2026.responses', 'cevns_pyeft.theory.li2026.amplitude', 'cevns_pyeft.theory.li2026.operators', 'cevns_pyeft.kernels.builder', 'cevns_pyeft.kernels.reconstruction', 'cevns_pyeft.experiments.coherent.slow_counts_ar2020', 'cevns_pyeft.experiments.coherent.fast_kernel_ar2020')

def prepare(definition, resources):
    from .execution import prepare_ar2020
    return prepare_ar2020(definition, resources)

DEFINITION = ExperimentDefinition('Ar2020','COHERENT_Ar','legacy_12bin_modular_v1',('legacy_Ar2020_run',),
    Ar2020Settings(), ObservationDefinition('reconstructed PE spectrum','PE',tuple(np.linspace(.001,120.001,13))),
    (ResourceRef('responses','data/responses/responses_all.json'), ResourceRef('efficiency','data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt')),
    {'slow':{'n_er':21,'n_enu':120,'n_pe_bin':8}, 'fast':{'n_er':21,'n_enu':120,'n_obs_sub':8}}, prepare,
    statistics=StatisticsDefinition('cevns_pyeft.experiments.coherent.statistics_binding:evaluate',.12,.146,kind="asymmetric_irls",observable_name="PE spectrum",
        observed=(174.3294,164.8672,82.4428,46.6318,13.6262,22.2221,7.8176,20.0156,25.6136,15.01212,21.41103,6.01039),
        background=(100.9960159,106.1752988,77.09163347,59.16334661,44.02390438,36.45418327,34.86055777,28.0876494,22.50996016,18.92430279,16.53386454,16.13545817),
        lower=(143.625498,140.0398406,62.74900398,29.6812749,-1.394422311,8.167330677,-4.581673307,7.768924303,13.74501992,4.183266932,10.55776892,-3.784860558),
        upper=(218.5258964,196.6135458,106.5737052,66.73306773,30.47808765,38.04780876,21.71314741,33.26693227,38.44621514,26.4940239,32.8685259,15.33864542)),
    capabilities={'slow':'Gaussian sigma(observed) legacy folding','fast':'legacy_compat channel_resolved_full_li2026','statistics':'legacy approximate asymmetric IRLS'})
