"""CsI2017 authority; count mass differs from source metadata."""
from dataclasses import dataclass
import numpy as np
from ..definition import ExperimentDefinition, SNSRun, ResourceRef, ObservationDefinition, StatisticsDefinition

@dataclass(frozen=True)
class CsI2017Settings:
    run: SNSRun = SNSRun(14.57,19.3,1.73e23,.08)
    mass_kg: float = 14.6
    from .csi2021_definition import DEFINITION as _CSI
    targets: tuple = _CSI.physical.targets
    atomic_mass_kg: float = _CSI.physical.atomic_mass_kg
    pe_per_keV: float = 1.17
    slow_pe_nodes: int = 251
    efficiency_columns: tuple = (0,1)
    efficiency_low: float = 1e-10
    efficiency_threshold: float = 4.9
    c10_mass_mode: str = 'quark_mass_resolved'
    implementation_modules: tuple = ('cevns_pyeft.experiments.coherent.execution', 'cevns_pyeft.experiments.coherent.sns', 'cevns_pyeft.rates.counts', 'cevns_pyeft.rates.differential', 'cevns_pyeft.nuclear.response', 'cevns_pyeft.theory.li2026.responses', 'cevns_pyeft.theory.li2026.amplitude', 'cevns_pyeft.theory.li2026.operators', 'cevns_pyeft.kernels.builder', 'cevns_pyeft.kernels.reconstruction', 'cevns_pyeft.experiments.coherent.slow_counts_csi2017', 'cevns_pyeft.experiments.coherent.fast_kernel_csi2017')

    def __post_init__(self):
        if self.targets != self._CSI.physical.targets:
            raise ValueError('CsI2017 component requires the existing Cs133/I127 response recipe')

def prepare(definition, resources):
    from .execution import prepare_csi2017
    return prepare_csi2017(definition, resources)

DEFINITION = ExperimentDefinition('CsI2017','COHERENT_CsI','legacy_25bin_modular_v1',('legacy_CsI2017_run',),
    CsI2017Settings(), ObservationDefinition('reconstructed PE spectrum','PE',tuple(np.linspace(.001,50.,26))),
    (ResourceRef('responses','data/responses/responses_all.json'), ResourceRef('efficiency','data/datafiles/COHERENT_eff.txt'),
     *(ResourceRef(k, f'data/datafiles/COHERENT_{k}.txt','statistics') for k in ('data','lower','upper','spectrum'))),
    {'slow':{'n_enu':120}, 'fast':{'n_er':251,'n_enu':120}}, prepare,
    statistics=StatisticsDefinition('cevns_pyeft.experiments.coherent.statistics_binding:evaluate',.28),
    capabilities={'slow':'deterministic PE mapping; fixed 251 nodes','fast':'legacy_compat channel_resolved_full_li2026','statistics':'legacy approximate Gaussian counts/bin'})
