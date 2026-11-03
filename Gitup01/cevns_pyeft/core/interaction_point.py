"""Small, source-free CEvNS interaction contract for the first extraction step.

This module deliberately does not implement a second cross-section formula.  It
only freezes the boundary between the shared Li2026 interaction chain and the
experiment-specific source, exposure, detector, and statistics layers.

The public coordinates are ``E_nu_GeV`` and ``recoil_keV``.  The returned
kernel and scalar differential cross section are in ``cm^2 / keV``.  Flux,
nuclei, exposure, efficiencies, and binning are intentionally absent.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Optional

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.sources.state import ParticleKind, validate_particle_kind
from cevns_pyeft.theory.kinematics import (
    is_two_body_recoil_allowed,
    two_body_recoil_max_GeV,
    validate_recoil_energy_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    contract_density_kernel,
    validate_density_matrix,
)
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey
from cevns_pyeft.theory.li2026.responses import Basis
from cevns_pyeft.rates.differential import differential_flavor_kernel_nn


@dataclass(frozen=True)
class DifferentialInteractionPoint:
    """Result of one source-free differential interaction evaluation.

    ``particle_kind`` is kept as an explicit state label.  The current shared
    Li2026 kernel is the legacy common nu/antinu route, so ``particle_kernel``
    records that no independent antineutrino sign/helicity kernel was applied.
    This prevents the label from being mistaken for a completed antineutrino
    physics implementation.
    """

    isotope_id: str
    particle_kind: ParticleKind
    energy_GeV: float
    recoil_keV: float
    endpoint_keV: float
    supported: bool
    kernel_cm2_per_keV: FlavorMatrix
    dsigma_cm2_per_keV: float
    particle_kernel: str = "legacy_shared_nu_antinu"

    def __post_init__(self) -> None:
        kernel = np.array(self.kernel_cm2_per_keV, dtype=np.complex128, copy=True)
        if kernel.shape != (3, 3) or not np.all(np.isfinite(kernel)):
            raise ValueError("kernel must be a finite (3, 3) matrix")
        kernel.setflags(write=False)
        object.__setattr__(self, "kernel_cm2_per_keV", kernel)
        value = float(self.dsigma_cm2_per_keV)
        if not math.isfinite(value) or value < 0.0:
            raise ValueError("dsigma_cm2_per_keV must be finite and non-negative")
        object.__setattr__(self, "dsigma_cm2_per_keV", value)


def _positive_finite(value: object, *, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def _target_mass_from_response(response: ResponseW) -> float:
    try:
        mass_number = float(response.get_basic("A"))
    except (TypeError, ValueError) as exc:
        raise ValueError("nuclear response must declare a numeric A") from exc
    return _positive_finite(mass_number * c.AMU_GEV, name="target mass")


def evaluate_li2026_point(
    response: ResponseW,
    *,
    energy_GeV: float,
    recoil_keV: float,
    rho: object,
    particle_kind: ParticleKind = "nu",
    target_mass_GeV: Optional[float] = None,
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]] = None,
    include_sm: bool = True,
    sin2thetaW: Optional[float] = None,
    basis: Basis = "np",
    c10_mass_mode: C10MassMode = "quark_mass_resolved",
) -> DifferentialInteractionPoint:
    """Evaluate one Li2026 differential interaction point.

    The response table and the current public rate API use the legacy
    ``A * AMU_GEV`` nuclear-mass convention.  An explicit target mass is
    accepted only when it agrees with that convention; silently passing a
    different mass here would make the endpoint and the amplitude disagree.
    """

    energy = _positive_finite(energy_GeV, name="energy_GeV")
    recoil = validate_recoil_energy_GeV(float(recoil_keV) * c.keV) / c.keV
    particle = validate_particle_kind(particle_kind)
    density = validate_density_matrix(rho)

    response_mass = _target_mass_from_response(response)
    mass = response_mass if target_mass_GeV is None else _positive_finite(
        target_mass_GeV, name="target_mass_GeV"
    )
    if not math.isclose(mass, response_mass, rel_tol=1.0e-14, abs_tol=0.0):
        raise ValueError(
            "target_mass_GeV must match the current response A*AMU_GEV "
            "convention"
        )

    endpoint_keV = two_body_recoil_max_GeV(energy, mass) / c.keV
    supported = is_two_body_recoil_allowed(
        energy, recoil * c.keV, mass
    )
    result = differential_flavor_kernel_nn(
        response,
        ER_keV=recoil,
        Enu_MeV=energy / c.MeV,
        wc_triplets=wc_triplets,
        include_sm=bool(include_sm),
        sin2thetaW=sin2thetaW,
        basis=basis,
        c10_mass_mode=c10_mass_mode,
    )
    kernel = np.asarray(result.kernel_cm2_per_keV, dtype=np.complex128)
    if kernel.shape != (3, 3):
        raise RuntimeError(
            "scalar interaction evaluation must return a (3, 3) flavor kernel"
        )
    value = contract_density_kernel(density, kernel)
    isotope_id = str(getattr(response, "name", "unknown"))
    return DifferentialInteractionPoint(
        isotope_id=isotope_id,
        particle_kind=particle,
        energy_GeV=energy,
        recoil_keV=recoil,
        endpoint_keV=float(endpoint_keV),
        supported=bool(supported),
        kernel_cm2_per_keV=kernel,
        dsigma_cm2_per_keV=value,
    )


__all__ = ["DifferentialInteractionPoint", "evaluate_li2026_point"]
