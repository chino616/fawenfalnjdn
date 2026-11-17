"""SM-only algebraic vectorization of the existing Li2026 cross-section API.

No solar/detector/observation imports. At fixed T the implemented SM coefficients
c1,c2,c5,c6,c7 are E-independent, so E^2 dσ/dT is a quadratic polynomial.
Three calls to the existing interaction determine it exactly; no EFT formula,
nuclear coefficients, fitted scale or detector input is duplicated here.
"""
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import numpy as np

from cevns_pyeft.contracts import IncidentStateBatch, TheoryPoint
from cevns_pyeft.contracts.interaction import DifferentialCrossSection, ElasticKinematics
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from .adapter import Li2026LegacyInteraction


@dataclass(frozen=True)
class SMQuadraticInteraction:
    responses_json: str | Path
    isotope_keys: tuple[str, ...]
    kinematics: ElasticKinematics = field(default_factory=ElasticKinematics, init=False)
    _legacy: object = field(init=False, repr=False, compare=False)
    _coefficients: object = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        legacy = Li2026LegacyInteraction(self.responses_json, {k:k for k in self.isotope_keys})
        object.__setattr__(self, '_legacy', legacy)
        object.__setattr__(self, 'responses_json', legacy.responses_json)

        @lru_cache(maxsize=16384)
        def coefficients(target, recoil, weak_angle):
            # All sample energies must be kinematically allowed. Units are GeV
            # only inside this polynomial; the delegated public API takes MeV.
            minimum = self.kinematics.minimum_energy_MeV(target, recoil)
            e0 = max(.020, 1.1*minimum*1e-3)
            h = e0/2
            energy = np.array([e0, e0+h, e0+2*h])*1000
            state = IncidentStateBatch(energy, np.eye(3)/3, 'nu', 'SM_universal_trace_one')
            result = legacy.dsigma_dT(target=target, energy_MeV=energy,
                recoil_keV=recoil, incident_state=state,
                parameters=TheoryPoint(sin2thetaW=weak_angle)).values_cm2_per_keV
            f0, f1, f2 = result*(energy*1e-3)**2
            quadratic = (f2-2*f1+f0)/2
            coeff = np.array([f0, f1-f0-quadratic, quadratic])
            coeff.setflags(write=False)
            return e0, h, coeff
        object.__setattr__(self, '_coefficients', coefficients)

    def validate(self, targets, parameters):
        if parameters.wc_triplets or parameters.state.values:
            raise UnsupportedCapabilityError('quadratic adapter is SM only; no BSM or flavor-state scan')
        self._legacy.validate(targets, parameters)

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        from types import SimpleNamespace
        self.validate(SimpleNamespace(isotopes=(target,)), parameters)
        energy = np.asarray(energy_MeV, float)
        incident_state.require_coordinates(energy, 'nu')
        recoil = float(recoil_keV)
        if not np.isfinite(recoil) or recoil < 0 or np.any(energy <= 0):
            raise ValueError('finite nonnegative recoil and positive neutrino energies required')
        if not parameters.include_sm:
            values = np.zeros_like(energy)
        else:
            e0, h, coeff = self._coefficients(target, recoil, parameters.sin2thetaW)
            x = (energy*1e-3-e0)/h
            terms = np.array([np.full_like(x, coeff[0]), x*coeff[1], x*x*coeff[2]])
            polynomial = terms.sum(axis=0)
            bound = 128*np.finfo(float).eps*np.abs(terms).sum(axis=0)
            polynomial = np.where(abs(polynomial) <= bound, 0., polynomial)
            allowed = energy >= self.kinematics.minimum_energy_MeV(target, recoil)
            if np.any(polynomial[allowed] < 0):
                raise ValueError('negative SM polynomial above floating cancellation error')
            values = np.where(allowed, polynomial/(energy*1e-3)**2, 0.)
        return DifferentialCrossSection(energy, values, recoil, 'li2026_SM_exact_quadratic')

    def describe(self):
        return ModuleDescriptor('interaction', 'li2026_SM_exact_quadratic',
            capabilities=('slow_elastic', 'SM_only'),
            parameters={'delegated': self._legacy.describe().as_dict(),
                        'vectorization': 'E^2 dsigma/dT exact quadratic from three delegated allowed energies',
                        'mass': 'A*amu', 'extra_KN_or_spin_factor': False,
                        'external_nuclear_source_certification': 'UNRESOLVED'},
            resources={'path': str(self.responses_json), 'sha256': self._legacy._sha256})
