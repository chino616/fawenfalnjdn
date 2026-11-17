"""Explicit solar SM nuclear-table route; detector folding is left unchanged.

Direct nuclear data: data/responses/responses_all.json, read as-is by ResponseDB.
Its external author release/normalization is NOT independently certified. This
adapter adopts the existing Li2026 reader and amplitude convention, without a
Helm/KN factor, spin prefactor, fitted c_i, or flux renormalization.
"""
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
import hashlib

import numpy as np

from cevns_pyeft.contracts import TargetInventory
from cevns_pyeft.contracts.interaction import DifferentialCrossSection, ElasticKinematics
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.foundation import constants
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
from cevns_pyeft.theory.sm_coherent import StandardModelKN
from .catalog import ExperimentCatalog
from .definition import ResourceRef
from .loader import ResourceCatalog, load_experiment
from .solar_b8 import SolarModel

XE_KEYS = ('Xe128', 'Xe129', 'Xe130', 'Xe131', 'Xe132', 'Xe134', 'Xe136')
CHANNELS = ('M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta')
DEPENDENCIES = (
    'cevns_pyeft.experiments.solar_nuclear', 'cevns_pyeft.nuclear.response',
    'cevns_pyeft.rates.differential', 'cevns_pyeft.theory.li2026.amplitude',
    'cevns_pyeft.theory.li2026.left_to_ci', 'cevns_pyeft.theory.li2026.responses',
    'cevns_pyeft.theory.li2026.lec', 'cevns_pyeft.theory.li2026.flavor',
    'cevns_pyeft.theory.li2026.operators', 'cevns_pyeft.foundation.constants',
)


@dataclass(frozen=True)
class SolarNuclearSM:
    """Reuse the shared SM amplitude, vectorizing only its exact E quadratic.

    For the SM LEFT terms (6,1,u/d),(6,2,u/d), c1,c2,c5,c6,c7 are E-independent;
    all other c's vanish. Thus each R:W is at most quadratic in E (shared
    left_to_ci.py and responses.py). Three allowed energies determine that
    polynomial identically. No event data or paper spectrum enters this step.
    Tests compare a fourth energy and the original scalar cross-section API.
    """
    responses_json: str | Path
    isotope_keys: tuple = XE_KEYS
    kinematics: ElasticKinematics = field(default_factory=ElasticKinematics, init=False)
    _responses: object = field(init=False, repr=False, compare=False)
    _sha256: str = field(init=False, repr=False)
    _coefficients: object = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        path = Path(self.responses_json).resolve()
        db = ResponseDB(path)
        responses = {key: db.get(key) for key in self.isotope_keys}
        object.__setattr__(self, 'responses_json', path)
        object.__setattr__(self, '_sha256', hashlib.sha256(path.read_bytes()).hexdigest())
        object.__setattr__(self, '_responses', MappingProxyType(responses))

        @lru_cache(maxsize=8192)
        def coefficients(isotope, recoil, weak_angle):
            resp = responses[isotope]
            mass = int(resp.basic['A'])*constants.AMU_GEV
            emin = .5*(recoil*1e-6 + np.sqrt((recoil*1e-6)**2+2*mass*recoil*1e-6))
            e0 = max(.020, 1.1*emin)
            h = e0/2
            rows = []
            for energy in (e0, e0+h, e0+2*h):
                result = flavor_kernel_onebody_li2026(resp, E_nu_GeV=energy,
                    ER_keV=recoil, left_hat=_sm_left_dim6(True, weak_angle))
                # SM is flavor universal; keep every implemented nuclear piece.
                row = []
                for key in CHANNELS:
                    kernel = result.pieces[key]
                    scalar = float(kernel[0, 0].real)
                    if not np.allclose(kernel, scalar*np.eye(3), rtol=1e-13, atol=1e-35):
                        raise ValueError('SM quadratic adapter requires a flavor-universal kernel')
                    row.append(scalar)
                rows.append(row)
            f0, f1, f2 = np.asarray(rows)
            quadratic = (f2-2*f1+f0)/2
            linear = f1-f0-quadratic
            coeff = np.array([f0, linear, quadratic])
            coeff.setflags(write=False)
            return e0, h, coeff
        object.__setattr__(self, '_coefficients', coefficients)

    def validate(self, targets, parameters):
        if parameters.wc_triplets or parameters.state.values:
            raise UnsupportedCapabilityError('solar nuclear route is SM only; no BSM/state scan')
        for target in targets.isotopes:
            if target.isotope_id not in self._responses:
                raise ValueError('missing nuclear table: '+target.isotope_id)
            mass = int(self._responses[target.isotope_id].basic['A'])*constants.AMU_GEV
            if not np.isclose(target.kinematic_mass_GeV, mass, rtol=1e-14, atol=0):
                raise ValueError('amplitude, phase space and kinematics require A*amu consistently')

    def channel_dsigma(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        energy = np.asarray(energy_MeV, float)
        incident_state.require_coordinates(energy, 'nu')
        self.validate(TargetView((target,)), parameters)
        recoil = float(recoil_keV)
        if not np.isfinite(recoil) or recoil < 0 or np.any(energy <= 0):
            raise ValueError('finite nonnegative recoil and positive neutrino energies required')
        if not parameters.include_sm:
            return {key: np.zeros_like(energy) for key in CHANNELS}
        e0, h, coeff = self._coefficients(target.isotope_id, recoil, parameters.sin2thetaW)
        eg = energy*1e-3
        x = (eg-e0)/h
        kernels = coeff[0]+x[:, None]*(coeff[1]+x[:, None]*coeff[2])
        # Exact elastic endpoints can cancel three nonzero polynomial terms.
        # Zero only values within their floating evaluation error, including
        # positive residues; this is not a physical clipping prescription.
        bound = 128*np.finfo(float).eps*(abs(coeff[0])+abs(x[:, None]*coeff[1])+
                                        abs(x[:, None]**2*coeff[2]))
        kernels = np.where(abs(kernels) <= bound, 0., kernels)
        # Shared cross_section.py: m/(8*pi*E^2), then cm2/GeV -> cm2/keV.
        factor = target.kinematic_mass_GeV/(8*np.pi*eg**2)*constants.GEV_INV2_TO_CM2*1e-6
        values = kernels*factor[:, None]
        values[energy < self.kinematics.minimum_energy_MeV(target, recoil)] = 0.
        return {key: values[:, i] for i, key in enumerate(CHANNELS)}

    def dsigma_dT(self, **kwargs):
        pieces = self.channel_dsigma(**kwargs)
        total = sum(pieces.values())
        scale = max(float(np.max(abs(total))), 1e-300)
        if np.any(total < -2e-12*scale):
            raise ValueError('negative SM nuclear-table cross section')
        return DifferentialCrossSection(kwargs['energy_MeV'], np.maximum(total, 0.),
            float(kwargs['recoil_keV']), 'solar_sm_nuclear_table_v1')

    def describe(self):
        from dataclasses import asdict
        return ModuleDescriptor('interaction', 'solar_sm_nuclear_table_v1',
            capabilities=('slow_elastic', 'SM_only', 'nuclear_channel_diagnostics'),
            parameters={'basis': 'np; row/column order (p,n)', 'isotope_keys': self.isotope_keys,
                'channels': CHANNELS, 'SM_matching': '_sm_left_dim6 + shared left_to_ci',
                'lecs': asdict(DEFAULT_LECS), 'mass_convention': 'A_times_amu',
                'normalization': 'existing ResponseDB and Li2026 amplitude as-is; no extra factor',
                'energy_vectorization': 'exact SM quadratic, three shared-amplitude evaluations',
                'roundoff': 'zero polynomial cancellation residues <=128*eps*sum(abs(terms))',
                'SigmaPDelta': 'particle response zero in existing implementation',
                'external_nuclear_source_certification': 'UNRESOLVED'},
            resources={'nuclear_responses_sha256': self._sha256, 'path': str(self.responses_json)})


@dataclass(frozen=True)
class TargetView:
    isotopes: tuple


@dataclass(frozen=True)
class NuclearSettings:
    base_settings: object
    nuclear_model: str
    isotope_keys: tuple
    implementation_modules: tuple


@dataclass(frozen=True)
class NuclearPreparation:
    base_definition: object

    def __call__(self, definition, resources):
        model, executor = self.base_definition.prepare(self.base_definition, resources)
        selected = definition.physical.isotope_keys
        lookup = {t.isotope_id: t for t in model.targets.isotopes}
        targets = tuple(replace(lookup[key],
            kinematic_mass_GeV=int(key[2:])*constants.AMU_GEV,
            mass_convention='A*amu for amplitude/kinematics; original atomic mass for nucleus counts')
            for key in selected)
        # TargetInventory requires its stored mass to equal its stored nuclei.
        # The 1-t anchor and all individual nuclei counts remain unchanged.
        covered_mass = sum(t.nucleus_mass_kg*t.number_of_nuclei for t in targets)
        inventory = TargetInventory(targets, covered_mass, {
            **dict(model.targets.composition_record), 'full_material_anchor_kg': model.anchor_mass_kg,
            'omitted_isotopes': [k for k in lookup if k not in selected],
            'subset_policy': 'original absolute nucleus counts; no abundance renormalization'})
        if definition.physical.nuclear_model == 'response':
            interaction = SolarNuclearSM(resources['nuclear_response'], selected)
        else:
            interaction = replace(model.interaction, mass_numbers=tuple(int(k[2:]) for k in selected),
                                  isotope_ids=selected)
        return replace(model, targets=inventory, interaction=interaction), executor


def with_solar_nuclear_response(experiment, *, response_file, nuclear_model='response', isotope_keys=XE_KEYS):
    """Explicit, fingerprinted override for either existing solar detector model.

    The original YAML/NPZ (historical KN input) is preserved. The wrapper binds
    the additional table and records the actual assembly. kn_control uses the
    identical seven isotope counts and A*amu masses for a fair comparison.
    """
    if not isinstance(experiment.model, SolarModel) or not isinstance(experiment.model.interaction, StandardModelKN):
        raise TypeError('nuclear override requires the existing solar SM model')
    if nuclear_model not in ('response', 'kn_control'):
        raise ValueError('select response or kn_control explicitly')
    selected = tuple(isotope_keys)
    if not selected or len(set(selected)) != len(selected) or any(k not in XE_KEYS for k in selected):
        raise ValueError('only distinct, available Xe nuclear keys are supported')
    base = experiment.definition
    modules = tuple(dict.fromkeys((*base.physical.implementation_modules, *DEPENDENCIES)))
    definition = replace(base, physical=NuclearSettings(base.physical, nuclear_model, selected, modules),
        analysis_revision=base.analysis_revision+'__nuclear_table_v1_'+nuclear_model,
        resources=base.resources+(ResourceRef('nuclear_response', Path(response_file).resolve().as_posix(),
            semantic='existing np nuclear polynomial table; external source unresolved'),),
        prepare=NuclearPreparation(base), statistics=None,
        capabilities={**dict(base.capabilities), 'nuclear_structure': nuclear_model,
            'natural_Xe_coverage': 'seven isotopes; Xe124/Xe126 missing, not renormalized',
            'statistics': 'NOT_REQUESTED'},
        validation=base.validation+('tests/test_solar_nuclear_response.py',))
    registry = ExperimentCatalog(builtins=False).register(base.dataset_id, definition)
    catalog = ResourceCatalog(experiment.resource_catalog.root, dict(experiment.resource_catalog.overrides))
    return load_experiment(base.dataset_id, definition=definition, resources=catalog, registry=registry)
