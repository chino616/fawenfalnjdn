"""Array adapters for the existing source/interaction contracts; no dataset lookup."""
from dataclasses import dataclass, field
from collections.abc import Mapping
import hashlib
import numpy as np

from cevns_pyeft.contracts.interaction import ElasticKinematics, DifferentialCrossSection
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.source import IncidentStateBatch
from cevns_pyeft.contracts.validation import readonly, freeze
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.sources.state import NeutrinoState


@dataclass(frozen=True)
class ArrayContinuum:
    energy: np.ndarray
    values: np.ndarray

    def __post_init__(self):
        x, y = readonly(self.energy), readonly(self.values)
        if x.ndim != 1 or x.size < 2 or y.shape != x.shape or np.any(np.diff(x) <= 0) or np.any(y < 0):
            raise ValueError('invalid continuum coordinates/values')
        object.__setattr__(self, 'energy', x)
        object.__setattr__(self, 'values', y)

    def __call__(self, energy):
        return np.interp(energy, self.energy, self.values, left=0.0, right=0.0)


@dataclass(frozen=True)
class ZeroContinuum:
    def __call__(self, energy):
        return np.zeros_like(energy, dtype=float)


@dataclass(frozen=True)
class ArraySource:
    fluence: object
    baseline_m: float
    yield_per_pot: float
    base_pot: float
    base_baseline_m: float
    base_yield_per_pot: float
    resource_hashes: Mapping

    def for_run(self, run):
        from cevns_pyeft.contracts.source import POTExposure, DetectorFluence
        from cevns_pyeft.sources.composable import ScaledComponent
        if not isinstance(run, POTExposure) or run.run_id != self.fluence.run_id:
            raise ValueError('package fluence requires its declared POT run')
        if self.baseline_m <= 0 or self.yield_per_pot < 0:
            raise ValueError('invalid explicit source override')
        if self.base_pot == 0 or self.base_yield_per_pot == 0:
            if run.total_pot != self.base_pot or self.yield_per_pot != self.base_yield_per_pot:
                raise ValueError('zero materialized source requires regeneration for nonzero override')
            scale = 1.
        else:
            scale = (run.total_pot / self.base_pot) * (self.yield_per_pot / self.base_yield_per_pot) * (self.base_baseline_m / self.baseline_m)**2
        parts = self.fluence.components if scale == 1 else tuple(ScaledComponent(c, scale) for c in self.fluence.components)
        return DetectorFluence(parts, run.run_id, {**dict(self.fluence.normalization_record),
            'explicit_what_if_scale': scale, 'base_materialized_fluence': True})

    def describe(self):
        return ModuleDescriptor('source', 'package_materialized_fluence_v1',
            capabilities=('slow_1d', 'fixed_state'),
            parameters={'baseline_m': self.baseline_m, 'yield_per_pot': self.yield_per_pot,
                'base_pot': self.base_pot, 'base_baseline_m': self.base_baseline_m,
                'base_yield_per_pot': self.base_yield_per_pot}, resources=self.resource_hashes)


@dataclass(frozen=True)
class ArrayState:
    rho: np.ndarray
    particle_kind: str

    def __post_init__(self):
        state = NeutrinoState(particle_kind=self.particle_kind, rho=self.rho)
        object.__setattr__(self, 'rho', readonly(state.rho, dtype=complex))

    def fixed_state_for_fast(self):
        return NeutrinoState(particle_kind=self.particle_kind, rho=self.rho)

    def __call__(self, energy_MeV, *, parameters):
        if parameters.values:
            raise ValueError('fixed-state model does not consume scanned state parameters')
        return IncidentStateBatch(energy_MeV, self.rho, self.particle_kind, 'sns_fixed_state_v1')


class ArrayResponseW(ResponseW):
    """Existing ResponseW arithmetic with snapshot-safe coefficient containers."""

    def W_np(self, key, y):
        # Generic snapshot() freezes lists to tuples. Restore only the queried
        # channel's container for the existing implementation; no math is copied.
        if key not in self.responses:
            raise KeyError(f'[{self.name}] missing response {key}')
        response = ResponseW(self.name, self.basic, self.exp_factor,
                             {key: np.asarray(self.responses[key]).tolist()})
        return response.W_np(key, y)


def response_from_arrays(data, arrays, isotope, response_refs=None):
    """Preserve n/p axes and ascending polynomial coefficients, without JSON I/O."""
    p = data['parameters']
    prefix = 'nuclear_' + isotope + '_'
    refs=response_refs if response_refs is not None else {key[len(prefix):]:key for key in arrays if key.startswith(prefix)}
    responses = {channel:arrays[key].tolist() for channel,key in refs.items()}
    for key,unit in [(f'target.{isotope}.A','1'),(f'target.{isotope}.b','GeV^-1'),(f'nuclear.{isotope}.exp_factor','1')]:
        if p[key]['unit']!=unit:raise ValueError('nuclear parameter unit: '+key)
    if set(responses) != {'M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP'}:
        raise ValueError('nuclear response channels incomplete: ' + isotope)
    for key, value in responses.items():
        array = np.asarray(value)
        if array.ndim != 3 or array.shape[:2] != (2, 2):
            raise ValueError('response requires (n/p, n/p, ascending power): ' + key)
        meta = data['resources']['arrays'][refs[key]]
        if meta['unit']!='1':raise ValueError('nuclear response coefficient unit: '+key)
        if [axis['name'] for axis in meta['axes']] != ['nucleon_left', 'nucleon_right', 'polynomial_power']:
            raise ValueError('nuclear response axis contract: ' + key)
        if any(axis['values'] != ['p', 'n'] for axis in meta['axes'][:2]):
            raise ValueError('nuclear response p/n ordering: ' + key)
    return ArrayResponseW(isotope, {'A': p[f'target.{isotope}.A']['value'],
                              'b': p[f'target.{isotope}.b']['value']},
                     p[f'nuclear.{isotope}.exp_factor']['value'], responses)


def check_engine_snapshot(data):
    """This model version binds explicit common-theory snapshots, never fallbacks.

    The existing cross-section and Fast implementations close over common constants
    and DEFAULT_LECS. A different snapshot requires a new engine binding/version.
    A mismatch is rejected rather than accepted and silently ignored.
    """
    from cevns_pyeft.foundation import constants
    from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
    active_lecs=('g_A','B0_m_u','B0_m_d',*(f'L{i}' for i in (*range(1,9),11,12,13,14)),
        'sigma_u_p','sigma_d_p','sigma_u_n','sigma_d_n',*(f'g{i}' for i in range(1,10)),'m_pi','m_N')
    required=[f'constants.{k}' for k in ('G_F','alpha_em','m_mu','m_e','m_pi_charged','AMU_GEV','GEV_INV2_TO_CM2')]
    required += ['lecs.'+k for k in active_lecs]
    missing=[k for k in required if k not in data['parameters']]
    if missing:
        raise ValueError('missing explicit common-engine snapshot: '+str(missing))
    energy_lecs={'L5','L6','L7','L8','L11','L12','L13','L14','sigma_u_p','sigma_d_p','sigma_u_n','sigma_d_n',
                 'g1','g2','g3','g4','m_pi','m_N'}
    for key in required:
        p=data['parameters'][key];name=key.split('.',1)[1]
        unit=({'G_F':'GeV^-2','alpha_em':'1','GEV_INV2_TO_CM2':'cm^2/GeV^-2'}.get(name,'GeV')
              if key.startswith('constants.') else 'GeV^2' if name.startswith('B0_m_') else 'GeV' if name in energy_lecs else '1')
        if p['role'] in ('reference_only','unused_snapshot') or p['value'] is None or p['unit']!=unit:
            raise ValueError('inactive/missing common-engine snapshot or unit: '+key)
    for key, p in data['parameters'].items():
        if key.startswith('constants.'):
            expected = getattr(constants, key.split('.', 1)[1])
        elif key.startswith('lecs.') and p['role'] not in ('reference_only', 'unused_snapshot'):
            expected = getattr(DEFAULT_LECS, key.split('.', 1)[1])
        else:
            continue
        if not np.isclose(p['value'], expected, rtol=1e-15, atol=0):
            raise ValueError('incompatible common-engine snapshot: ' + key)


@dataclass(frozen=True)
class ArrayInteraction:
    responses: Mapping
    c10_mass_mode: str
    snapshot: Mapping
    kinematics: ElasticKinematics = field(default_factory=ElasticKinematics, init=False)

    def __post_init__(self):
        object.__setattr__(self, 'responses', freeze(self.responses))
        object.__setattr__(self, 'snapshot', freeze(self.snapshot))

    @property
    def coefficient_contract(self):
        return 'operator_bilinear_v1'

    @property
    def coefficient_channels(self):
        from cevns_pyeft.theory.li2026.coefficients import CHANNELS
        return CHANNELS

    @property
    def operator_keys(self):
        from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
        return tuple(spec.key for spec in LI2026_OPERATOR_SPECS)

    def coefficient_dsigma(self, *, target, energy_MeV, recoil_keV, basis_keys):
        from cevns_pyeft.theory.li2026.coefficients import differential_coefficients
        return differential_coefficients(self.responses[target.isotope_id], target, energy_MeV,
                                         recoil_keV, basis_keys, c10_mass_mode=self.c10_mass_mode)

    def coefficient_values(self, parameters, basis_keys):
        from cevns_pyeft.rates.differential import _sm_left_dim6
        from cevns_pyeft.theory.li2026.operators import canonicalize_wilson_coefficients
        from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
        values = canonicalize_wilson_coefficients(wc_triplets=parameters.wc_triplets)
        for key, value in _sm_left_dim6(parameters.include_sm, parameters.sin2thetaW).items():
            values[key] = values.get(key, np.zeros((3, 3), complex)) + value
        missing = [key for key, value in values.items() if key not in basis_keys and np.any(value != 0)]
        if missing:
            raise UnsupportedCapabilityError('coefficient outside compiled basis: ' + str(missing))
        return np.array([values.get(key, np.zeros((3, 3), complex)) for key in basis_keys])

    def validate(self, targets, parameters):
        from cevns_pyeft.foundation.constants import AMU_GEV
        from cevns_pyeft.theory.li2026.operators import canonicalize_wilson_coefficients
        canonicalize_wilson_coefficients(wc_triplets=parameters.wc_triplets)
        for target in targets.isotopes:
            response = self.responses[target.isotope_id]
            if not np.isclose(target.kinematic_mass_GeV, response.basic['A'] * AMU_GEV, rtol=1e-14):
                raise ValueError('mass convention differs from Li2026 A*amu binding')

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        from cevns_pyeft.rates.differential import differential_cross_section_nn
        energy = np.asarray(energy_MeV, dtype=float)
        incident_state.require_coordinates(energy, incident_state.particle_kind)
        result = differential_cross_section_nn(self.responses[target.isotope_id], float(recoil_keV), energy,
            rho=incident_state.rho, particle_kind=incident_state.particle_kind,
            wc_triplets=parameters.wc_triplets, include_sm=parameters.include_sm,
            sin2thetaW=parameters.sin2thetaW, c10_mass_mode=self.c10_mass_mode)
        if result.particle_kind != incident_state.particle_kind:
            raise ValueError('particle kind lost by interaction')
        return DifferentialCrossSection(energy, result.dsigma_cm2_per_keV, float(recoil_keV), 'li2026_dsigma_v1')

    def describe(self):
        from .definition import digest
        return ModuleDescriptor('interaction', 'li2026_package_arrays_v1',
            capabilities=('slow_elastic', 'operator_bilinear_v1'),
            parameters={'c10_mass_mode': self.c10_mass_mode, 'snapshot': self.snapshot,
                        'particle_treatment': 'legacy_shared_kernel', 'SigmaPDelta': 'zero_particle_response'},
            resources={'responses_sha256': digest({k: {'basic': v.basic, 'exp_factor': v.exp_factor,
                                                        'responses': v.responses} for k, v in self.responses.items()})})
