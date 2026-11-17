"""Flavor-universal light-vector CEvNS with explicit SM interference.

DE ROMERI V, PAPOULIAS D K, TERNES C A. JCAP 05 (2025) 012,
doi:10.1088/1475-7516/2025/05/012, published Eqs. (2.6), (2.10).
The published definition is C_V = 3 A g_V^2. arXiv:2411.11749v1
Eq. (10) instead prints C_V^2; these versions must not be conflated.

The existing SM model owns kinematics, KN structure, and absolute units.
This component changes only the coherent weak charge. Couplings are real,
flavor universal, and diagonal. It is not a general LEFT/epsilon adapter.
"""
from dataclasses import dataclass, replace
import numpy as np
from cevns_pyeft.contracts.interaction import DifferentialCrossSection
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.theory.sm_coherent import StandardModelKN


@dataclass(frozen=True)
class LightVectorKN:
    sm: StandardModelKN
    mass_MeV: float
    coupling: float
    scenario: str = 'universal'

    def __post_init__(self):
        if not isinstance(self.sm, StandardModelKN):
            raise TypeError('light vector requires an explicit StandardModelKN reference')
        for name in ('mass_MeV', 'coupling'):
            value = getattr(self, name)
            if isinstance(value, (bool, np.bool_)) or not np.isscalar(value) or not np.isrealobj(value) or not np.isfinite(value):
                raise ValueError(name + ' must be a finite real scalar')
        if self.mass_MeV <= 0 or self.coupling < 0:
            raise ValueError('mediator mass must be positive and coupling non-negative')
        if self.scenario not in ('universal', 'b_minus_l'):
            raise ValueError('scenario must be universal or b_minus_l')

    @property
    def kappa(self):
        return 1.0 if self.scenario == 'universal' else -1.0 / 3.0

    @property
    def kinematics(self):
        return self.sm.kinematics

    def mass_number(self, target):
        return float(self.sm.mass_numbers[self.sm.isotope_ids.index(target.isotope_id)])

    def weak_charge(self, target, sin2thetaW):
        a = self.mass_number(target)
        z = self.sm.proton_number
        return 0.5 * ((1 - 4 * sin2thetaW) * z - (a - z))

    def charge_shift(self, target, recoil_keV):
        t = np.asarray(recoil_keV, dtype=float)
        if np.any(~np.isfinite(t)) or np.any(t < 0):
            raise ValueError('recoil must be finite and non-negative')
        a = self.mass_number(target)
        denominator = (float(self.mass_MeV) * 1e-3) ** 2 + 2 * target.kinematic_mass_GeV * t * 1e-6
        return self.kappa * 3 * a * float(self.coupling) ** 2 / (np.sqrt(2) * self.sm.fermi_GeV_minus2 * denominator)

    def describe(self):
        return ModuleDescriptor('interaction', 'light_vector_kn_v1',
            capabilities=('slow_1d', 'flavor_universal_vector', 'SM_interference', 'NP_only'),
            parameters={'mass_MeV': float(self.mass_MeV), 'coupling': float(self.coupling),
                'scenario': self.scenario, 'kappa': self.kappa, 'g_definition': 'sqrt(g_nu*g_q); charges in kappa',
                'nuclear_coupling': 'C_V=3*A*g^2, published Eq.(2.10)',
                'charge': 'Q_total=include_sm*Q_SM+kappa*3*A*g^2/[sqrt(2)*G_F*(mV^2+2*m*T)]',
                'reference': 'JCAP05(2025)012 PDF p5, printed p4, Eqs.(2.6),(2.10)',
                'scope': 'real flavor-universal diagonal coupling; no propagation NSI or flavor-changing LEFT'},
            resources={'explicit_SM_reference': self.sm.describe().as_dict()})

    def validate(self, targets, parameters):
        self.sm.validate(targets, parameters)

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        q_sm = self.weak_charge(target, parameters.sin2thetaW)
        # The SM kernel is proportional to Q_SM^2. For a vanishing weak charge
        # use s_W^2=1/2 only as an algebraic normalization anchor, Q_ref=-A/2.
        # The physical weak angle still enters q_sm. No singular ratio remains.
        if q_sm == 0:
            reference = replace(parameters, include_sm=True, sin2thetaW=0.5)
            q_reference = -self.mass_number(target) / 2
        else:
            reference = replace(parameters, include_sm=True)
            q_reference = q_sm
        base = self.sm.dsigma_dT(target=target, energy_MeV=energy_MeV, recoil_keV=recoil_keV,
            incident_state=incident_state, parameters=reference)
        q_total = (q_sm if parameters.include_sm else 0.0) + float(self.charge_shift(target, recoil_keV))
        values = base.values_cm2_per_keV * (q_total / q_reference) ** 2
        return DifferentialCrossSection(base.energy_MeV, values, float(recoil_keV), 'light_vector_kn_v1')
