"""Canonical neutrino source states in active-flavor density space."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple, cast

import numpy as np
from numpy.typing import NDArray

from cevns_pyeft.theory.li2026.flavor import (
    FlavorMatrix,
    NeutrinoFlavor,
    flavor_projector,
    validate_density_matrix,
)


ParticleKind = Literal["nu", "antinu"]
DensityMatrixArray = NDArray[np.complex128]

PARTICLE_KINDS = ("nu", "antinu")


def validate_particle_kind(value: object) -> ParticleKind:
    """Return a canonical particle label or reject an ambiguous value."""

    if not isinstance(value, str) or value not in PARTICLE_KINDS:
        raise ValueError(
            f"particle_kind must be one of {PARTICLE_KINDS}, got {value!r}"
        )
    return cast(ParticleKind, value)


def _canonical_energy_shape(
    energy_shape: Optional[Tuple[int, ...]],
) -> Optional[Tuple[int, ...]]:
    if energy_shape is None:
        return None
    shape = tuple(int(size) for size in energy_shape)
    if any(size < 0 for size in shape):
        raise ValueError(f"energy_shape entries must be non-negative, got {shape}")
    return shape


def validate_density_matrices(
    rho: object,
    *,
    energy_shape: Optional[Tuple[int, ...]] = None,
    atol: float = 1.0e-10,
    name: str = "rho",
) -> DensityMatrixArray:
    """Validate one density matrix or an energy-indexed density-matrix grid.

    A constant (3, 3) density matrix is broadcast over energy_shape.  An
    energy-dependent input must have exactly energy_shape + (3, 3) and is
    validated independently at every energy.
    """

    expected_energy_shape = _canonical_energy_shape(energy_shape)
    try:
        array = np.asarray(rho, dtype=np.complex128)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} cannot be converted to a complex array") from exc

    if array.shape == (3, 3):
        matrix = validate_density_matrix(array, atol=atol)
        if expected_energy_shape in (None, ()):
            return matrix
        return np.broadcast_to(
            matrix,
            expected_energy_shape + (3, 3),
        )

    if array.ndim < 3 or array.shape[-2:] != (3, 3):
        if expected_energy_shape is None:
            expected = "(3,3) or (...,3,3)"
        else:
            expected = f"(3,3) or {expected_energy_shape + (3, 3)}"
        raise ValueError(f"{name} must have shape {expected}, got {array.shape}")

    actual_energy_shape = array.shape[:-2]
    if (
        expected_energy_shape is not None
        and actual_energy_shape != expected_energy_shape
    ):
        raise ValueError(
            f"{name} energy shape must be {expected_energy_shape}, "
            f"got {actual_energy_shape}"
        )

    for index in np.ndindex(actual_energy_shape):
        try:
            validate_density_matrix(array[index], atol=atol)
        except ValueError as exc:
            raise ValueError(f"{name}{index} is invalid: {exc}") from exc

    return array


def pure_flavor_density(flavor: NeutrinoFlavor) -> FlavorMatrix:
    """Return the canonical pure-flavor density matrix."""

    return flavor_projector(flavor)


@dataclass(frozen=True)
class NeutrinoState:
    """A source state with particle identity separate from Flavor density.

    particle_kind is metadata at the current P2 boundary.  The existing
    interaction kernel remains numerically unchanged for nu and antinu until
    the dedicated antineutrino physics audit is completed.
    """

    particle_kind: ParticleKind
    rho: DensityMatrixArray

    def __post_init__(self) -> None:
        particle_kind = validate_particle_kind(self.particle_kind)
        rho = np.array(
            validate_density_matrices(self.rho),
            dtype=np.complex128,
            copy=True,
        )
        rho.setflags(write=False)
        object.__setattr__(self, "particle_kind", particle_kind)
        object.__setattr__(self, "rho", rho)

    @property
    def is_energy_dependent(self) -> bool:
        """Whether this state carries explicit energy axes."""

        return self.rho.ndim > 2

    @property
    def energy_shape(self) -> Optional[Tuple[int, ...]]:
        """Return explicit energy axes, or None for a constant state."""

        if not self.is_energy_dependent:
            return None
        return self.rho.shape[:-2]

    def density_for_energy_shape(
        self,
        energy_shape: Tuple[int, ...],
    ) -> DensityMatrixArray:
        """Resolve this state on an exact neutrino-energy grid shape."""

        shape = _canonical_energy_shape(energy_shape)
        if shape is None:
            raise RuntimeError("energy_shape canonicalization returned None")
        if not self.is_energy_dependent:
            if shape == ():
                return self.rho
            return np.broadcast_to(self.rho, shape + (3, 3))
        if self.energy_shape != shape:
            raise ValueError(
                f"state.rho energy shape must be {shape}, "
                f"got {self.energy_shape}"
            )
        return self.rho


def pure_flavor_state(
    flavor: NeutrinoFlavor,
    *,
    particle_kind: ParticleKind = "nu",
) -> NeutrinoState:
    """Return a pure-flavor neutrino or antineutrino source state."""

    return NeutrinoState(
        particle_kind=particle_kind,
        rho=pure_flavor_density(flavor),
    )


def coerce_neutrino_state(
    value: object,
    *,
    particle_kind: Optional[ParticleKind] = None,
) -> NeutrinoState:
    """Resolve a state object or pair a raw density input with a particle tag."""

    if isinstance(value, NeutrinoState):
        if (
            particle_kind is not None
            and validate_particle_kind(particle_kind) != value.particle_kind
        ):
            raise ValueError(
                "particle_kind contradicts the NeutrinoState label: "
                f"{particle_kind!r} != {value.particle_kind!r}"
            )
        return value

    if particle_kind is None:
        raise ValueError(
            "particle_kind is required when rho is not a NeutrinoState"
        )
    return NeutrinoState(
        particle_kind=validate_particle_kind(particle_kind),
        rho=value,
    )


__all__ = [
    "ParticleKind",
    "DensityMatrixArray",
    "PARTICLE_KINDS",
    "validate_particle_kind",
    "validate_density_matrices",
    "pure_flavor_density",
    "NeutrinoState",
    "pure_flavor_state",
    "coerce_neutrino_state",
]
