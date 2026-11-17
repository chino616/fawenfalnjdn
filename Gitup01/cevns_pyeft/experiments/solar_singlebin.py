"""Independent solar-8B single-bin analysis: 2601.19883v2 Eqs.(84),(87),(88).

Onboarding mapping: source -> SourceSpectrum; target -> build_targets;
total efficiency -> TotalAcceptance; prediction -> SingleBinExecutor;
fitted signal yields -> statistics.solar_singlebin (lazy, separate resource).
This module never imports the multibin solar adapters or reads their NPZ/Qy/D/B.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import numpy as np

from cevns_pyeft.contracts import (Axis, Binning, EnergySupport, IncidentStateBatch,
    IntegrationSettings, LiveTimeExposure, TargetIsotope, TargetInventory, TheoryPoint)
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.foundation.constants import AMU_GEV
from cevns_pyeft.sources.composable import CallableFluenceComponent, DifferentialFluxSource
from cevns_pyeft.theory.li2026.sm_quadratic import SMQuadraticInteraction
from .catalog import ExperimentCatalog
from .definition import ExperimentDefinition, ObservationDefinition, ResourceRef, StatisticsDefinition, plain
from .loader import ResourceCatalog, load_experiment

INPUT_DIRECTORY = 'data/benchmarks/solar_b8_singlebin_2601_19883'
SAMPLES = ('PandaX_paired', 'PandaX_US2', 'XENONnT')
DEPENDENCIES = (
    'cevns_pyeft.experiments.solar_singlebin', 'cevns_pyeft.sources.composable',
    'cevns_pyeft.rates.recoil', 'cevns_pyeft.theory.li2026.sm_quadratic',
    'cevns_pyeft.theory.li2026.adapter', 'cevns_pyeft.rates.differential',
    'cevns_pyeft.theory.li2026.cross_section', 'cevns_pyeft.theory.li2026.amplitude',
    'cevns_pyeft.theory.li2026.left_to_ci', 'cevns_pyeft.theory.li2026.responses',
    'cevns_pyeft.theory.li2026.lec', 'cevns_pyeft.theory.li2026.flavor',
    'cevns_pyeft.theory.li2026.operators', 'cevns_pyeft.nuclear.response',
    'cevns_pyeft.foundation.constants',
)


def read_card(path):
    card = json.loads(Path(path).read_text(encoding='utf8'))
    if card.get('schema') != 'solar_b8_singlebin_analysis/1' or tuple(card['samples']) != SAMPLES:
        raise ValueError('not the independent single-bin analysis card')
    return card


@dataclass(frozen=True)
class SourceSpectrum:
    energy: np.ndarray
    density: np.ndarray
    total_flux: float

    def __call__(self, energy):
        # [R6] Shape and [R5] total flux each appear once; no fitted rescaling.
        return self.total_flux*np.interp(energy, self.energy, self.density, left=0., right=0.)


@dataclass(frozen=True)
class UniversalState:
    def __call__(self, energy_MeV, *, parameters):
        if parameters.values:
            raise UnsupportedCapabilityError('SM is flavor universal; state scan not supported')
        return IncidentStateBatch(energy_MeV, np.eye(3)/3, 'nu', 'SM_universal_trace_one')


def build_targets(table, keys, avogadro):
    # [R7] n_A per tonne = 1e6 g * N_A * number_fraction / full mean molar mass.
    # Preserve the nine-row denominator when only seven nuclear tables exist.
    if table.shape != (9, 3) or not np.isclose(table[:, 2].sum(), 1.):
        raise ValueError('expected the original nine-row natural-Xe composition')
    mean = float(table[:, 1]@table[:, 2])
    isotopes = []
    for number, atom_u, fraction in table:
        key = 'Xe'+str(int(number))
        if key in keys:
            isotopes.append(TargetIsotope(key, int(number)*AMU_GEV,
                atom_u*1e-3/avogadro, 1e6*avogadro*fraction/mean,
                'A*amu for amplitude and kinematics; original atomic mass for nucleus inventory'))
    if tuple(t.isotope_id for t in isotopes) != tuple(keys):
        raise ValueError('isotope selection does not match available table keys')
    mass = sum(t.nucleus_mass_kg*t.number_of_nuclei for t in isotopes)
    return TargetInventory(tuple(isotopes), mass, {'anchor_mass_kg': 1000.,
        'mean_molar_mass_g_mol': mean, 'missing_keys': ['Xe124', 'Xe126'],
        'original_number_fraction_coverage': float(sum(row[2] for row in table if 'Xe'+str(int(row[0])) in keys)),
        'renormalized': False, 'source': 'R7 NIST original nine rows; R8 available nuclear keys'})


@dataclass(frozen=True)
class TotalAcceptance:
    energy: np.ndarray
    efficiency: np.ndarray
    requested_bounds: tuple
    tail_mode: str

    @property
    def verified_upper(self):
        return min(self.requested_bounds[1], float(self.energy[-1]))

    @property
    def complete(self):
        return self.verified_upper >= self.requested_bounds[1]

    def known_acceptance(self, recoil):
        if np.any(recoil < self.energy[0]) or np.any(recoil > self.energy[-1]):
            raise ValueError('unknown total acceptance: no implicit extrapolation')
        return np.interp(recoil, self.energy, self.efficiency)

    def describe(self):
        return {'kind': 'total_ROI_acceptance_in_true_recoil', 'energy_keVnr': self.energy,
                'epsilon': self.efficiency, 'bounds_keVnr': self.requested_bounds,
                'coverage_complete': self.complete, 'tail_mode': self.tail_mode,
                'Qy_mapping': 'not used', 'additional_ROI_cut': False, 'ci': 'absent'}


@dataclass(frozen=True)
class SingleBinModel:
    source: object
    targets: TargetInventory
    interaction: object
    observation: TotalAcceptance
    sample: str
    exposure_tyr: float
    seconds_per_year: float
    binning: Binning

    def describe(self):
        return {'analysis': 'singlebin_2601_19883', 'sample': self.sample,
                'source': self.source.describe().as_dict(), 'targets': plain(self.targets),
                'interaction': self.interaction.describe().as_dict(),
                'observation': self.observation.describe(), 'exposure_tyr': self.exposure_tyr,
                'seconds_per_year': self.seconds_per_year, 'observable': 'fitted signal total, not raw candidate histogram'}


@dataclass(frozen=True)
class SingleBinSettings:
    sample: str
    tail_mode: str
    card_sha256: str
    implementation_modules: tuple = DEPENDENCIES


@dataclass(frozen=True)
class SingleBinPreparation:
    def __call__(self, definition, resources):
        card = read_card(resources['analysis_input'])
        if hashlib.sha256(resources['analysis_input'].read_bytes()).hexdigest() != definition.physical.card_sha256:
            raise ValueError('analysis card changed; rebuild definition')
        settings = card['physics']; sample = card['samples'][definition.physical.sample]
        for rid, name in [('source', 'b8_source.txt'), ('target', 'xe_isotopes.txt'), ('efficiency', sample['efficiency'])]:
            if hashlib.sha256(resources[rid].read_bytes()).hexdigest() != card['files'][name]['sha256']:
                raise ValueError('singlebin resource hash mismatch: '+rid)
        if hashlib.sha256(resources['nuclear_response'].read_bytes()).hexdigest() != settings['nuclear_sha256']:
            raise ValueError('nuclear table differs from the adopted direct resource')
        table = np.loadtxt(resources['source'])
        spectrum = SourceSpectrum(table[:, 0], table[:, 1], settings['flux_cm2_s'])
        support = EnergySupport((float(table[0, 0]), float(table[-1, 0])),
            breakpoints_MeV=tuple(table[1:-1, 0]), interpolation_id='linear_Bahcall_no_renormalization')
        component = CallableFluenceComponent('solar_B8', 'nu', support, spectrum, UniversalState())
        source = DifferentialFluxSource((component,), ModuleDescriptor('source', 'singlebin_B8_flux',
            parameters={'total_flux_cm2_s': spectrum.total_flux, 'shape_integral': float(np.trapezoid(table[:,1], table[:,0])),
                        'shape_rows': len(table), 'source': 'R6 columns 1,2 + R5 Eq.(29)', 'state': 'flavor universal, trace one; no factor three'},
            resources={'sha256': card['files']['b8_source.txt']['sha256']}))
        target = build_targets(np.loadtxt(resources['target']), settings['isotope_keys'], settings['avogadro_per_mol'])
        efficiency = np.loadtxt(resources['efficiency'])
        if np.any(np.diff(efficiency[:,0]) <= 0) or np.any(efficiency[:,1] < 0) or np.any(efficiency[:,1] > 1):
            raise ValueError('invalid total acceptance')
        acceptance = TotalAcceptance(efficiency[:,0], efficiency[:,1], tuple(sample['T_bounds_keVnr']), definition.physical.tail_mode)
        if acceptance.energy[0] > sample['T_bounds_keVnr'][0]:
            raise ValueError('missing low-energy acceptance')
        obs = definition.observation
        model = SingleBinModel(source, target,
            SMQuadraticInteraction(resources['nuclear_response'], tuple(settings['isotope_keys'])),
            acceptance, definition.physical.sample, sample['exposure_tyr'], settings['seconds_per_year'],
            Binning((Axis(obs.name, obs.unit, obs.edges),)))
        return model, SingleBinExecutor(settings['sin2thetaW'])


@dataclass(frozen=True)
class SingleBinExecutor:
    weak_angle: float

    def default_point(self):
        return TheoryPoint(sin2thetaW=self.weak_angle)

    def describe_execution(self, model):
        return {'algorithm': 'fresh true-recoil integral; never sum old observable bins',
                'statistics': 'lazy fitted signal Gaussian Eq.88', 'model': model.describe()}

    def __call__(self, exp, point, backend, ns, kernel):
        from cevns_pyeft.rates.recoil import integrate_recoil_yield
        if backend != 'slow' or kernel is not None:
            raise UnsupportedCapabilityError('single-bin route uses direct Slow, no multibin Fast cache')
        model = exp.model; obs = model.observation
        model.interaction.validate(model.targets, point)
        fluence = model.source.for_run(LiveTimeExposure(model.seconds_per_year, 'one_reference_year'))
        lo, hi = obs.requested_bounds; split = obs.verified_upper
        knots = obs.energy[(obs.energy > lo) & (obs.energy < hi)]
        grid = np.unique(np.r_[np.linspace(lo, hi, ns['n_er']), knots, split])
        known = grid <= split; tail = grid >= split
        integrator = IntegrationSettings(n_er=ns['n_er'], n_enu=ns['n_enu'], strategy='bin_probability_v1')
        parts = {}; rates = {}; lower = 0.; upper_tail = 0.
        for target in model.targets.isotopes:
            rate = integrate_recoil_yield(fluence.components[0], target, model.interaction,
                parameters=point, numerics=integrator, recoil_keV=grid)
            # Per-tonne/year anchor already in nuclei + one reference year.
            density = rate.values_per_keV*target.number_of_nuclei*model.exposure_tyr
            known_count = float(np.trapezoid(density[known]*obs.known_acceptance(grid[known]), grid[known]))
            raw_tail = float(np.trapezoid(density[tail], grid[tail])) if not obs.complete else 0.
            value = known_count
            if not obs.complete and obs.tail_mode == 'flat_sensitivity':
                value += raw_tail*obs.efficiency[-1]  # explicit project assumption, never official data
            parts[('solar_B8', target.isotope_id)] = np.array([value])
            rates[target.isotope_id] = density
            lower += known_count; upper_tail += raw_tail
        counts = sum(parts.values(), np.zeros(1))
        record = {'flux': dict(fluence.normalization_record), 'exposure_tyr': model.exposure_tyr,
            'normalization': 'one reference-year fluence * original nuclei/tonne * exposure_tyr, once',
            'efficiency': 'Total including ROI, once; no extra Ne/S2 window', 'ci': 'absent'}
        complete_prediction = obs.complete or obs.tail_mode == 'flat_sensitivity'
        diagnostic = {'coverage_complete': complete_prediction, 'experimental_efficiency_coverage_complete': obs.complete,
            'claim': 'project_flat_tail_sensitivity' if not obs.complete and complete_prediction else ('complete_integral' if obs.complete else 'partial_integral_and_rigorous_tail_bounds'),
            'known_domain_keVnr': [lo, split], 'requested_domain_keVnr': [lo, hi],
            'verified_domain_events': lower, 'unknown_tail_max_events_epsilon_le_1': upper_tail,
            'full_interval_events': [lower, lower+upper_tail], 'recoil_keV': grid,
            'rate_per_keV_by_isotope_including_exposure': rates,
            'flat_tail_epsilon_assumption': float(obs.efficiency[-1]) if not obs.complete and complete_prediction else None}
        prediction = Prediction(counts, model.binning, parts, record, model.describe(), ns, diagnostic)
        return prediction, {model.sample: prediction}, None, {'profile': 'singlebin_2601_19883', 'claim': diagnostic['claim']}


def load_singlebin(sample, *, root=None, input_directory=None, tail_mode='bounded'):
    """Explicit scoped catalog: does not change default global experiment IDs."""
    if sample not in SAMPLES or tail_mode not in ('bounded', 'flat_sensitivity'):
        raise ValueError('select a declared single-bin sample and explicit tail mode')
    if sample != 'XENONnT' and tail_mode != 'bounded':
        raise ValueError('tail sensitivity only applies to XENONnT')
    if root is None:
        from cevns_pyeft.foundation.paths import resource_root
        root = resource_root()
    root = Path(root).resolve()
    directory = Path(input_directory or root/INPUT_DIRECTORY).resolve()
    card_path = directory/'analysis.input.json'; card = read_card(card_path)
    data = card['samples'][sample]
    dataset = data['dataset_id']+('__flat_tail_sensitivity' if tail_mode == 'flat_sensitivity' else '')
    resources = tuple(ResourceRef(rid, str(path), role=role, semantic=semantic) for rid,path,role,semantic in [
        ('analysis_input', card_path, 'physical', 'independent single-bin analysis card; not a three-file package'),
        ('source', directory/'b8_source.txt', 'physical', 'R6 shape only'),
        ('target', directory/'xe_isotopes.txt', 'physical', 'R7 original natural Xe'),
        ('efficiency', directory/data['efficiency'], 'physical', data['source']),
        ('nuclear_response', root/card['physics']['nuclear_resource'], 'physical', 'R8 user-selected local nuclear table'),
        ('fitted_yields', directory/'fitted_yields.json', 'statistics', 'R1 Eq.88 fitted signal yields, not raw candidates')])
    definition = ExperimentDefinition(dataset, data['experiment_slug'], 'singlebin2601_v3.2.1_'+tail_mode,
        (sample,), SingleBinSettings(sample, tail_mode, hashlib.sha256(card_path.read_bytes()).hexdigest()),
        ObservationDefinition('fitted_signal_yield_bin', 'dimensionless', (0.,1.), (sample,)), resources,
        {'slow': {'n_er': 401, 'n_enu': 240}}, SingleBinPreparation(),
        statistics=StatisticsDefinition('cevns_pyeft.statistics.solar_singlebin:evaluate', .12,
            kind='singlebin_fitted_signal_gaussian', observable_name='fitted signal yield', observable_unit='events',
            status='R1 Eq.88 approximation; external response provenance and X tail limitations tracked'),
        reproduction_sin2thetaW=card['physics']['sin2thetaW'],
        capabilities={'analysis': 'singlebin', 'slow': 'SM nuclear Response integral', 'statistics': 'independent fitted signal Gaussian; partial input rejected'},
        validation=('tests/test_solar_singlebin.py',))
    registry = ExperimentCatalog(builtins=False).register(dataset, definition)
    return load_experiment(dataset, definition=definition, registry=registry, resources=ResourceCatalog(root))
