"""Authoritative settings for the existing nine-bin CsI2021 analysis."""
from dataclasses import dataclass
from ..definition import ExperimentDefinition, SNSRun, ResourceRef, ObservationDefinition, StatisticsDefinition

from cevns_pyeft.targets.recipes import CSI_RECIPE as CSI_TARGET_RECIPE, LEGACY_ATOMIC_MASS_KG
from cevns_pyeft.detectors.legacy_parameters import CSI_RESPONSE_DEFAULTS, CSI_PE_EDGES, CSI_COMPONENT_ACCEPTANCE

@dataclass(frozen=True)
class CsI2021Settings:
    run: SNSRun = SNSRun(14.57, 19.3, 3.198e23, .0848)
    mass_kg: float = 14.57
    targets: tuple = CSI_TARGET_RECIPE
    atomic_mass_kg: float = LEGACY_ATOMIC_MASS_KG
    quenching: tuple = CSI_RESPONSE_DEFAULTS.quenching
    gamma_a: float = CSI_RESPONSE_DEFAULTS.gamma_a
    gamma_b: float = CSI_RESPONSE_DEFAULTS.gamma_b
    efficiency: tuple = CSI_RESPONSE_DEFAULTS.efficiency
    acceptance: tuple = CSI_COMPONENT_ACCEPTANCE
    c10_mass_mode: str = 'quark_mass_resolved'
    implementation_modules: tuple = ('cevns_pyeft.targets.materials', 'cevns_pyeft.detectors.legacy_parameters', 'cevns_pyeft.sources.legacy_parameters', 'cevns_pyeft.experiments.coherent.execution', 'cevns_pyeft.experiments.coherent.sns', 'cevns_pyeft.rates.counts', 'cevns_pyeft.rates.differential', 'cevns_pyeft.nuclear.response', 'cevns_pyeft.theory.li2026.responses', 'cevns_pyeft.theory.li2026.amplitude', 'cevns_pyeft.theory.li2026.operators', 'cevns_pyeft.kernels.builder', 'cevns_pyeft.kernels.reconstruction', 'cevns_pyeft.detectors.csi2021', 'cevns_pyeft.sources.sns', 'cevns_pyeft.kernels.compiler', 'cevns_pyeft.rates.folding')

    def __post_init__(self):
        if self.targets != CSI_TARGET_RECIPE:
            raise ValueError('CsI2021 component requires the existing Cs133/I127 recipe; register another component for other targets')

def prepare(definition, resources):
    from .execution import prepare_csi2021
    return prepare_csi2021(definition, resources)

DEFINITION = ExperimentDefinition('CsI2021', 'COHERENT_CsI', 'legacy_9bin_modular_v1', ('legacy_CsI2021_run',),
    CsI2021Settings(), ObservationDefinition('reconstructed PE spectrum', 'PE',
        CSI_PE_EDGES),
    (ResourceRef('responses', 'data/responses/responses_all.json', semantic='nuclear response database'),),
    {'slow': {'n_er':21,'n_enu':120,'n_pe_bin':8,'pe_step':3.},
     'fast': {'n_er':21,'n_enu':120,'n_pe_bin':8,'pe_step':3.}}, prepare,
    statistics=StatisticsDefinition('cevns_pyeft.experiments.coherent.statistics_binding:evaluate', .125, .35, kind="gaussian_two_pull", observable_unit="counts/PE",
        observed=(1.021,13.195,18.941,13.059,11.043,5.977,1.838,2.274,-.831),
        background=(0.,.229,.455,.48,.429,.329,.229,.179,.154),
        uncertainty=(.454695767,3.816688713,4.717813051,4.304453263,3.858024691,2.543540564,2.466380071,2.339616402,1.785714286)),
    capabilities={'slow':'ExperimentModel legacy_csi2021_v1','fast':'interface_kernel_v1', 'statistics':'legacy approximate Gaussian counts/PE'})
