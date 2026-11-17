"""Explicit PandaX US2 mean-yield approximation, separate from a full response.

De Romeri et al., arXiv:2411.11749v1, p5 Eqs.(11)--(13), p6 Eq.(15).
The digitized Total(US2) acceptance already contains the electron ROI. Applying
it together with deterministic bin assignment is a declared approximation; the
lost contributions outside the mean-mapped window are reported, not rescaled.
"""
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from cevns_pyeft.contracts import Axis, Binning, IntegrationSettings, LiveTimeExposure
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.rates.folding import trapezoid_weights
from cevns_pyeft.rates.recoil import integrate_recoil_yield
from .catalog import ExperimentCatalog
from .definition import ObservationDefinition, ResourceRef
from .loader import ResourceCatalog, load_experiment
from .solar_b8 import ObservationSet, SolarExecutor, SolarModel


@dataclass(frozen=True)
class MeanYieldObservation:
    yield_energy: np.ndarray
    charge_yield: np.ndarray
    energy: np.ndarray
    efficiency: np.ndarray
    recoil_edges: np.ndarray

    def mean_electrons(self, recoil):
        t = np.asarray(recoil, float)
        if np.any((t < self.yield_energy[0]) | (t > self.yield_energy[-1])):
            raise ValueError('charge-yield extrapolation is not permitted')
        return t * np.interp(t, self.yield_energy, self.charge_yield)

    def acceptance(self, recoil):
        return np.interp(recoil, self.energy, self.efficiency, left=0., right=0.)

    def describe(self):
        return ModuleDescriptor('observation', 'pandax_us2_mean_yield_v1',
            capabilities=('deterministic_electron_bins',), parameters={
                'mapping': 'Ne = T * piecewise_linear_Qy(T); no resolution',
                'Qy_energy_keV': self.yield_energy.tolist(),
                'Qy_electron_per_keV': self.charge_yield.tolist(),
                'acceptance_energy_keV': self.energy.tolist(),
                'Total_US2_acceptance': self.efficiency.tolist(),
                'inverse_mapped_recoil_edges_keV': self.recoil_edges.tolist(),
                'selection': 'published Total(US2), including ROI, once',
                'c_i': 'unity baseline assumption; author values unavailable',
                'outside_mean_window': 'excluded from Ne bins; retained as diagnostic',
                'source': '2411.11749v1 p5 Eqs.(11)-(13), p6 Eq.(15); '
                          '2407.10892v3 p3 Fig.1 and p5 Fig.4 lower'})


def inverse_mean_edges(energy, charge_yield, electron_edges):
    """Invert T*Qy(T), validating every linear segment rather than just nodes."""
    t, q, n = (np.asarray(x, float) for x in (energy, charge_yield, electron_edges))
    if t.ndim != 1 or q.shape != t.shape or t.size < 2:
        raise ValueError('charge yield requires two equal 1D arrays')
    if not all(np.isfinite(x).all() for x in (t, q, n)):
        raise ValueError('nonfinite yield/mapping input')
    if np.any(t < 0) or np.any(q <= 0) or np.any(np.diff(t) <= 0):
        raise ValueError('yield energy must increase and charge yield must be positive')
    slopes = np.diff(q) / np.diff(t)
    if np.any(q[:-1] + t[:-1]*slopes <= 0) or np.any(q[1:] + t[1:]*slopes <= 0):
        raise ValueError('T*Qy must be strictly increasing within every segment')
    if n.ndim != 1 or n.size < 2 or np.any(np.diff(n) <= 0):
        raise ValueError('electron edges must increase')
    if n[0] < t[0]*q[0] or n[-1] > t[-1]*q[-1]:
        raise ValueError('electron window is outside verified Qy support')
    return np.array([brentq(lambda x: x*np.interp(x, t, q)-v, t[0], t[-1],
                            xtol=1e-13) for v in n])


@dataclass(frozen=True)
class MeanMapModel(SolarModel):
    def describe(self):
        result = super().describe()
        result['aggregation'] = 'single combined US2 exposure, eight mean-mapped Ne bins'
        result['claim'] = 'simplified mean-yield approximation, not full detector response'
        return result


@dataclass(frozen=True)
class MeanMapSettings:
    base_settings: object
    curve_label: str
    implementation_modules: tuple
    method: str = '2411.11749v1 mean mapping, unity c_i baseline'


@dataclass(frozen=True)
class MeanMapPreparation:
    base_definition: object

    def __call__(self, definition, resources):
        base, executor = self.base_definition.prepare(self.base_definition, resources)
        table = np.loadtxt(resources['mean_charge_yield'])
        if table.ndim != 2 or table.shape[1] != 2:
            raise ValueError('Qy input must contain T_keVnr and Qy_electron_per_keV')
        inverse = inverse_mean_edges(table[:, 0], table[:, 1], definition.observation.edges)
        original = base.observation[0]
        if inverse[0] < original.energy[0] or inverse[-1] > original.energy[-1]:
            raise ValueError('mean-mapped bins exceed tabulated acceptance support')
        observation = MeanYieldObservation(table[:, 0], table[:, 1], original.energy,
                                           original.efficiency, inverse)
        obs = definition.observation
        binning = Binning((Axis(obs.name, obs.unit, obs.edges),))
        model = MeanMapModel(base.source, base.targets, base.interaction,
            ObservationSet((observation,)), base.exposures_tyr, base.run_ids, binning,
            base.seconds_per_year, base.anchor_mass_kg, 'pandax_mean_map')
        return model, MeanMapExecutor(executor.include_sm, executor.weak_angle)


@dataclass(frozen=True)
class MeanMapExecutor(SolarExecutor):
    def describe_execution(self, model):
        return {'profile': 'pandax_us2_mean_map_v1', 'model': model.describe(),
                'default_sin2thetaW': self.weak_angle}

    def __call__(self, exp, point, backend, ns, kernel):
        if backend != 'slow' or kernel is not None:
            raise UnsupportedCapabilityError('mean-map benchmark supports direct Slow only')
        m = exp.model
        m.interaction.validate(m.targets, point)
        o = m.observation[0]
        fluence = m.source.for_run(LiveTimeExposure(m.seconds_per_year, 'reference_year'))
        numerics = IntegrationSettings(n_er=ns['n_er'], n_enu=ns['n_enu'],
                                       strategy='bin_probability_v1')
        parts, grids, rates, accepted, outside = {}, {}, {}, {}, {}
        for target in m.targets.isotopes:
            upper = m.interaction.kinematics.maximum_recoil_keV(
                target, max(c.support.integration_domain_MeV[1] for c in fluence.components))
            lo, hi = float(o.energy[0]), min(float(o.energy[-1]), upper)
            if hi <= o.recoil_edges[-1]:
                raise ValueError('source endpoint does not cover declared electron bins')
            knots = np.r_[o.energy, o.yield_energy, o.recoil_edges]
            t = np.unique(np.r_[np.linspace(lo, hi, ns['n_er']),
                                knots[(knots > lo) & (knots < hi)]])
            # Integrate each continuous T interval separately. A step probability
            # at a shared endpoint would introduce a spurious trapezoid half-bin.
            weights = np.zeros((len(t), len(o.recoil_edges)-1))
            for j, (a, b) in enumerate(zip(o.recoil_edges[:-1], o.recoil_edges[1:])):
                mask = (t >= a) & (t <= b)
                weights[mask, j] = trapezoid_weights(t[mask])
            tail_weights = np.zeros((len(t), 2))
            for j, mask in enumerate((t <= o.recoil_edges[0], t >= o.recoil_edges[-1])):
                tail_weights[mask, j] = trapezoid_weights(t[mask])
            for component in fluence.components:
                rate = integrate_recoil_yield(component, target, m.interaction,
                    parameters=point, numerics=numerics, recoil_keV=t)
                scale = target.number_of_nuclei*m.exposures_tyr[0]/(m.anchor_mass_kg/1000)
                density = rate.values_per_keV * o.acceptance(t) * scale
                key = (component.component_id, target.isotope_id)
                parts[key] = density @ weights
                accepted[key] = float(np.trapezoid(density, t))
                outside[key] = density @ tail_weights
                grids[target.isotope_id] = t
                rates[target.isotope_id] = rate.values_per_keV*scale
        counts = sum(parts.values(), np.zeros(m.binning.shape))
        all_accepted = sum(accepted.values())
        tails = sum(outside.values(), np.zeros(2))
        if not np.isclose(all_accepted, counts.sum()+tails.sum(), rtol=1e-12, atol=1e-13):
            raise ValueError('accepted-domain partition does not close')
        ledger = {'reference_fluence': dict(fluence.normalization_record),
            'anchor_mass_kg': m.anchor_mass_kg, 'run_exposures_tyr': m.exposures_tyr.tolist(),
            'mass_time_application': 'one reference-year fluence * anchor nuclei * exposure_tyr/anchor_tonne',
            'efficiency': 'Total(US2), including ROI, once',
            'c_i': 'unity baseline, project convention; no author c_i array obtained',
            'Jacobian': 'change to inverse-mapped T intervals; no extra dT/dNe factor',
            'normalization_adjustment': 'none; no renormalization to accepted-domain total'}
        details = {'n_er_base': ns['n_er'], 'n_enu_base': ns['n_enu'],
            'mode': m.mode, 'quadrature': 'shared recoil integration; continuous T-bin trapezoids',
            'inverse_recoil_edges_keV': o.recoil_edges.tolist()}
        diagnostics = {'true_recoil_rates_at_exposure_per_keV': rates, 'recoil_grids_keV': grids,
            'accepted_domain_total_events': all_accepted,
            'outside_mean_window_events_low_high': tails.tolist(),
            'per_isotope_accepted_domain_events': {k[1]: v for k, v in accepted.items()},
            'accepted_domain_keV': [float(o.energy[0]), float(o.energy[-1])]}
        detector = Prediction(counts, m.binning, parts, ledger, m.describe(), details, diagnostics)
        combined = Prediction(counts, m.binning,
            {(s+'@US2', a): v for (s, a), v in parts.items()}, ledger, m.describe(), details, diagnostics)
        return combined, {'US2': detector}, None, {
            'profile': 'pandax_us2_mean_map_v1', 'input_authority': 'unchanged formal package + explicit Qy resource',
            'algorithm': 'shared SM recoil integration followed by inverse-Qy T-bin integration'}


def with_pandax_mean_map(experiment, *, qy_file, curve_label='nominal',
                         electron_edges=tuple(np.arange(4., 8.25, .5))):
    """Return a separately fingerprinted approximation; preserve the base package."""
    if not isinstance(experiment.model, SolarModel) or experiment.model.mode != 'recoil_acceptance':
        raise TypeError('mean mapping requires the original combined US2 recoil package')
    if experiment.model.run_ids != ('US2',):
        raise ValueError('this approximation has one combined US2 exposure')
    base = experiment.definition
    physical = MeanMapSettings(base.physical, curve_label,
        tuple(base.physical.implementation_modules)+('cevns_pyeft.experiments.solar_mean_map',))
    definition = replace(base, physical=physical,
        analysis_revision=base.analysis_revision+'__mean_map_v1_'+curve_label,
        observation=ObservationDefinition('mean_mapped_electron_number', 'electron', tuple(electron_edges), ('US2',)),
        resources=base.resources+(ResourceRef('mean_charge_yield', Path(qy_file).resolve().as_posix(),
            semantic='2407.10892v3 p5 Fig.4 lower, digitized '+curve_label+' Qy'),),
        prepare=MeanMapPreparation(base), statistics=None,
        capabilities={'slow': 'SM simplified deterministic mean mapping',
            'simplified_mean_map_spectrum': 'available, unity c_i baseline',
            'full_electron_response': 'BLOCKED, original response gap retained',
            'statistics': 'NOT_REQUESTED'},
        validation=('tests/test_solar_mean_map.py', 'tests/test_solar_b8_sm_contract.py'))
    original = experiment.resource_catalog
    resources = ResourceCatalog(original.root, dict(original.overrides))
    registry = ExperimentCatalog(builtins=False).register(base.dataset_id, definition)
    return load_experiment(base.dataset_id, definition=definition, resources=resources, registry=registry)
