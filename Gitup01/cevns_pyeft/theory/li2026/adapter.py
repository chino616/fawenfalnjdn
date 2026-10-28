"""Thin adapter over the existing contracted MeV/keV cross section."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from types import MappingProxyType
import hashlib
import numpy as np
from cevns_pyeft.contracts.interaction import DifferentialCrossSection, ElasticKinematics
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.validation import freeze
from cevns_pyeft.foundation.constants import AMU_GEV
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import differential_cross_section_nn
from .lec import DEFAULT_LECS
from .operators import canonicalize_wilson_coefficients


@dataclass(frozen=True)
class Li2026LegacyInteraction:
    responses_json: str | Path
    response_keys: Mapping = field(default_factory=lambda: {"Cs133": "Cs133", "I127": "I"})
    c10_mass_mode: str = "quark_mass_resolved"
    kinematics: ElasticKinematics = field(default_factory=ElasticKinematics, init=False)
    _responses: Mapping = field(init=False, repr=False, compare=False)
    _sha256: str = field(init=False, repr=False)

    @property
    def coefficient_contract(self):
        return "operator_bilinear_v1"

    @property
    def coefficient_channels(self):
        from .coefficients import CHANNELS
        return CHANNELS

    @property
    def operator_keys(self):
        from .operators import LI2026_OPERATOR_SPECS
        return tuple(spec.key for spec in LI2026_OPERATOR_SPECS)

    def coefficient_dsigma(self, *, target, energy_MeV, recoil_keV, basis_keys):
        from .coefficients import differential_coefficients
        return differential_coefficients(self._responses[target.isotope_id], target, energy_MeV,
                                          recoil_keV, basis_keys, c10_mass_mode=self.c10_mass_mode)

    def coefficient_values(self, parameters, basis_keys):
        from cevns_pyeft.rates.differential import _sm_left_dim6
        from .operators import canonicalize_wilson_coefficients
        from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
        values = canonicalize_wilson_coefficients(wc_triplets=parameters.wc_triplets)
        for key, value in _sm_left_dim6(parameters.include_sm, parameters.sin2thetaW).items():
            values[key] = values.get(key, np.zeros((3, 3), complex)) + value
        missing = [key for key, value in values.items() if key not in basis_keys and np.any(value != 0)]
        if missing:
            raise UnsupportedCapabilityError(f"coefficient(s) outside compiled basis: {missing}")
        return np.array([values.get(key, np.zeros((3, 3), complex)) for key in basis_keys])

    def __post_init__(self):
        if self.c10_mass_mode not in ("quark_mass_resolved", "legacy_equal_light_quark_mass", "flavor"):
            raise ValueError("unsupported c10_mass_mode")
        path = Path(self.responses_json).resolve()
        raw = path.read_bytes()
        db = ResponseDB(path)
        object.__setattr__(self, "responses_json", path)
        object.__setattr__(self, "response_keys", freeze(self.response_keys))
        object.__setattr__(self, "_responses", MappingProxyType({key: db.get(value) for key, value in self.response_keys.items()}))
        object.__setattr__(self, "_sha256", hashlib.sha256(raw).hexdigest())

    def validate(self, targets, parameters):
        canonicalize_wilson_coefficients(wc_triplets=parameters.wc_triplets)
        for target in targets.isotopes:
            if target.isotope_id not in self._responses:
                raise ValueError(f"missing nuclear response for {target.isotope_id}")
            resp = self._responses[target.isotope_id]
            if not np.isclose(target.kinematic_mass_GeV, int(resp.basic["A"]) * AMU_GEV, rtol=1e-14):
                raise ValueError("legacy interaction and kinematics must share the A*amu mass convention")

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        energy = np.asarray(energy_MeV, dtype=float)
        incident_state.require_coordinates(energy, incident_state.particle_kind)
        values = differential_cross_section_nn(
            self._responses[target.isotope_id], float(recoil_keV), energy,
            rho=incident_state.rho, particle_kind=incident_state.particle_kind,
            wc_triplets=parameters.wc_triplets, include_sm=parameters.include_sm,
            sin2thetaW=parameters.sin2thetaW, c10_mass_mode=self.c10_mass_mode,
        ).dsigma_cm2_per_keV
        return DifferentialCrossSection(energy, values, float(recoil_keV), "li2026_legacy")

    def describe(self):
        from dataclasses import asdict
        return ModuleDescriptor("interaction", "li2026_legacy", capabilities=("slow_elastic", "operator_bilinear_v1"),
                                parameters={"response_keys": self.response_keys, "c10_mass_mode": self.c10_mass_mode,
                                            "particle_treatment": "legacy_shared_kernel", "lecs": asdict(DEFAULT_LECS),
                                            "basis": "np", "mass_convention": "A_times_amu"},
                                resources={"nuclear_responses_sha256": self._sha256, "path": str(self.responses_json)},
                                dependencies=("incident_state", "theory_point", "nuclear_response"))
