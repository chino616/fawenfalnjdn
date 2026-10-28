"""The existing Ge73 C2/C3/C5 candidate; no new scientific approval."""
from dataclasses import dataclass
from ..definition import ExperimentDefinition, ResourceRef, ObservationDefinition, StatisticsDefinition, MassTimeExposure

DATASET_ID = 'conus_plus_2025_c2c3c5_ge73_pyeft'
SOURCE_PATH = f'data/experiments/CONUS_Plus/{DATASET_ID}/source'
STATISTICS_PATH = f'data/experiments/CONUS_Plus/{DATASET_ID}/statistics/approximate_paper_benchmark'

@dataclass(frozen=True)
class ReactorSettings:
    total_flux_cm2_s: float = 1.5e13
    normalization_uncertainty: float = .046
    energy_support_mev: tuple = (0.,10.)
    match_energy_mev: float = 2.
    lowest_node_mev: float = .01
    low_end_policy: str = 'linear_extrapolation_clamped_nonnegative'
    components: tuple = ('U235','U238','Pu239','Pu241')

    def __post_init__(self):
        import math
        if not math.isfinite(self.total_flux_cm2_s) or self.total_flux_cm2_s < 0:
            raise ValueError('total flux must be finite and non-negative')
        if self.energy_support_mev[0] != 0 or not self.match_energy_mev < self.energy_support_mev[1] <= 10:
            raise ValueError('source supports [0,Emax] with 2 < Emax <= 10 MeV')
        if self.match_energy_mev != 2 or self.lowest_node_mev != .01 or self.low_end_policy != 'linear_extrapolation_clamped_nonnegative' or self.components != ('U235','U238','Pu239','Pu241'):
            raise ValueError('candidate table matching, state and component convention are fixed')

@dataclass(frozen=True)
class DetectorSettings:
    germanium_z: float = 32.
    lindhard_k: float = .162
    sigma0_evee: float = 20.38
    fano_factor: float = .1096
    pair_creation_energy_ev: float = 2.96
    thresholds_evee: tuple = (('C2',180.),('C3',160.),('C5',170.))

@dataclass(frozen=True)
class ConusSettings:
    source: ReactorSettings = ReactorSettings()
    detector: DetectorSettings = DetectorSettings()
    exposures: tuple = (MassTimeExposure('C2',119.),MassTimeExposure('C3',119.),MassTimeExposure('C5',119.))
    target_A: int = 73
    response_key: str = 'Ge73'
    nuclei_per_kg: float = 8.249507893261811e24
    seconds_per_day: float = 86400.
    energy_region_labels: tuple = ('E_nu_le_8_MeV','E_nu_gt_8_MeV')
    energy_region_bounds_mev: tuple = ((0.,8.),(8.,10.))
    c10_mass_mode: str = 'quark_mass_resolved'
    implementation_modules: tuple = ('cevns_pyeft.experiments.conus_plus.source', 'cevns_pyeft.experiments.conus_plus.detector_response', 'cevns_pyeft.experiments.conus_plus.slow_counts', 'cevns_pyeft.experiments.conus_plus.fast_kernel', 'cevns_pyeft.experiments.conus_plus.execution', 'cevns_pyeft.rates.differential', 'cevns_pyeft.theory.li2026.responses', 'cevns_pyeft.theory.li2026.amplitude', 'cevns_pyeft.nuclear.response')

    def __post_init__(self):
        if self.target_A != 73 or self.response_key != 'Ge73':
            raise ValueError('this dataset preserves the Ge73 candidate')
        if tuple(e.detector_id for e in self.exposures) != ('C2','C3','C5'):
            raise ValueError('exposures must follow named C2/C3/C5 detector order')

def prepare(definition,resources):
    from .execution import prepare_conus
    return prepare_conus(definition,resources)

DEFINITION = ExperimentDefinition(DATASET_ID,'CONUS_Plus','candidate_ge73_modular_v1',('legacy_candidate_run',),
    ConusSettings(),ObservationDefinition('ionization_energy','eVee',tuple(float(x) for x in range(160,351,10)),('C2','C3','C5')),
    (ResourceRef('responses','data/responses/responses_all.json'),ResourceRef('kopeikin',SOURCE_PATH+'/kopeikin_nodes.csv'),
     ResourceRef('mueller',SOURCE_PATH+'/mueller_coefficients.csv'),
     ResourceRef('observations',STATISTICS_PATH+'/observations_digitized_approx.csv','statistics'), ResourceRef('observation_schema',STATISTICS_PATH+'/observation_schema.json','statistics')),
    {'slow':{'n_recoil':96,'n_energy':12},'fast':{'n_recoil':128,'n_energy':16}},prepare,
    statistics=StatisticsDefinition('cevns_pyeft.experiments.conus_plus.execution:evaluate',.169,
        required_exposures=(0.,119.,0.),status='approximate digitized Gaussian; effective119 C3-like only',observable_unit='paper plotted normalization / 10 eVee bin'),
    reproduction_sin2thetaW=.23857,
    capabilities={'slow':'segmented Gauss rate per kg day','fast':'detector_response_matrix; rate recomputed at each point',
                  'statistics':'requires effective119 exposures; unavailable for default 357 forward prediction'})


def make_effective119_benchmark_definition(base=None):
    """The existing approximate profile; does not create a new official dataset ID."""
    from dataclasses import replace
    base=DEFINITION if base is None else base
    return replace(base,physical=replace(base.physical,exposures=tuple(MassTimeExposure(name,value)
        for name,value in zip(base.observation.detector_ids,(0.,119.,0.)))))
