"""Quadratic EFT event-kernel utilities for the CONUS+ response chain.

The detector-response matrix in :mod:`fast_kernel` only caches detector
folding.  This module provides the separate mathematical representation needed
for an EFT quadratic event kernel.  It builds the polynomial from a supplied
direct spectrum evaluator, keeps real and imaginary coefficient coordinates
explicit, and validates held-out points.  The evaluator is deliberately
injected so that source, target, exposure and detector contracts cannot be
silently replaced by a kernel builder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np

from cevns_pyeft.theory.li2026.flavor import FLAVOR_ORDER
from cevns_pyeft.theory.li2026.operators import (
    LI2026_OPERATOR_SPECS,
    LeftKey,
)


SpectrumEvaluator = Callable[[Mapping[tuple[int, int, str], np.ndarray]], np.ndarray]


@dataclass(frozen=True)
class EFTCoordinate:
    """One real coordinate of a complex flavor-matrix Wilson coefficient."""

    name: str
    operator: LeftKey
    final_flavor: str
    initial_flavor: str
    component: str
    scale: float


def reactor_visible_coordinates(*, initial_flavor: str = "e") -> tuple[EFTCoordinate, ...]:
    """Return all current Li2026 coordinates visible to one incoming flavor.

    The source is an electron antineutrino state, so only the selected initial
    flavor column can contribute.  LNV operators omit their forbidden diagonal
    element.  Every complex entry is represented by independent real and
    imaginary coordinates.  This is a basis declaration; it does not claim
    that a kernel has already been constructed for every coordinate.
    """

    if initial_flavor not in FLAVOR_ORDER:
        raise ValueError(f"unknown initial flavor {initial_flavor!r}")
    initial_index = FLAVOR_ORDER.index(initial_flavor)
    coordinates: list[EFTCoordinate] = []
    for spec in LI2026_OPERATOR_SPECS:
        for final_index, final_flavor in enumerate(FLAVOR_ORDER):
            if spec.lnv_diagonal_must_vanish and final_index == initial_index:
                continue
            for component in ("real", "imag"):
                label = "Re" if component == "real" else "Im"
                coordinates.append(
                    EFTCoordinate(
                        name=(
                            f"{label}[{spec.name}]"
                            f"[{final_flavor}{initial_flavor}]"
                        ),
                        operator=spec.key,
                        final_flavor=final_flavor,
                        initial_flavor=initial_flavor,
                        component=component,
                        scale=1.0,
                    )
                )
    return tuple(coordinates)


def coordinate_metadata(
    coordinates: Sequence[EFTCoordinate] | None = None,
) -> list[dict[str, object]]:
    """Serialize basis metadata without serializing a numerical kernel."""

    coords = tuple(coordinates or reactor_visible_coordinates())
    return [
        {
            "index": i,
            "name": coord.name,
            "operator": list(coord.operator),
            "final_flavor": coord.final_flavor,
            "initial_flavor": coord.initial_flavor,
            "component": coord.component,
            "scale": coord.scale,
        }
        for i, coord in enumerate(coords)
    ]


def _spectrum(values: object, n_bins: int, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.shape != (n_bins,):
        raise ValueError(f"{name} must contain exactly {n_bins} bins")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def _first_spectrum(values: object, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size == 0 or np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be a finite non-empty spectrum")
    return array


@dataclass(frozen=True)
class EFTQuadraticKernel:
    """Per-bin polynomial ``N(x)=constant+linear*x+x.T@quadratic@x``."""

    coordinate_names: tuple[str, ...]
    constant: np.ndarray
    linear: np.ndarray
    quadratic: np.ndarray
    reference: str = "direct spectrum evaluator"

    def __post_init__(self) -> None:
        names = tuple(self.coordinate_names)
        constant = np.asarray(self.constant, dtype=float)
        linear = np.asarray(self.linear, dtype=float)
        quadratic = np.asarray(self.quadratic, dtype=float)
        if constant.ndim != 1:
            raise ValueError("constant must have shape (n_bins,)")
        n_bins = constant.size
        n_coordinates = len(names)
        if linear.shape != (n_bins, n_coordinates):
            raise ValueError("linear shape must be (n_bins, n_coordinates)")
        if quadratic.shape != (n_bins, n_coordinates, n_coordinates):
            raise ValueError(
                "quadratic shape must be (n_bins, n_coordinates, n_coordinates)"
            )
        if not np.allclose(quadratic, np.swapaxes(quadratic, -1, -2)):
            raise ValueError("quadratic coefficients must be symmetric")
        if not all(np.all(np.isfinite(a)) for a in (constant, linear, quadratic)):
            raise ValueError("kernel coefficients must be finite")
        constant.setflags(write=False)
        linear.setflags(write=False)
        quadratic.setflags(write=False)
        object.__setattr__(self, "coordinate_names", names)
        object.__setattr__(self, "constant", constant)
        object.__setattr__(self, "linear", linear)
        object.__setattr__(self, "quadratic", quadratic)

    @property
    def n_bins(self) -> int:
        return int(self.constant.size)

    @property
    def n_coordinates(self) -> int:
        return len(self.coordinate_names)

    def evaluate(self, coordinates: object) -> np.ndarray:
        values = np.asarray(coordinates, dtype=float)
        if values.shape[-1:] != (self.n_coordinates,):
            raise ValueError(
                f"coordinates must end with ({self.n_coordinates},)"
            )
        return (
            self.constant
            + np.einsum("...j,bj->...b", values, self.linear)
            + np.einsum("...i,bij,...j->...b", values, self.quadratic, values)
        )


def build_quadratic_kernel(
    evaluator: SpectrumEvaluator,
    coordinates: Sequence[EFTCoordinate],
    *,
    steps: Sequence[float] | float,
    reference: str = "direct spectrum evaluator",
) -> EFTQuadraticKernel:
    """Extract an exact quadratic kernel from direct spectrum samples.

    The direct evaluator is called at the origin, both axis points and every
    positive-positive corner.  Therefore a returned kernel is only valid when
    the supplied theory and detector chain is quadratic in these real
    coordinates.  The caller must run :func:`validate_quadratic_kernel` on
    independent held-out points before saving it as a Fast artifact.
    """

    coords = tuple(coordinates)
    if not coords:
        raise ValueError("at least one EFT coordinate is required")
    if np.isscalar(steps):
        step_values = np.full(len(coords), float(steps), dtype=float)
    else:
        step_values = np.asarray(steps, dtype=float)
    if step_values.shape != (len(coords),) or np.any(~np.isfinite(step_values)):
        raise ValueError("steps must contain one finite value per coordinate")
    if np.any(step_values <= 0.0):
        raise ValueError("steps must be positive")

    def mapping(values: np.ndarray) -> dict[LeftKey, np.ndarray]:
        out: dict[LeftKey, np.ndarray] = {}
        for value, coord in zip(values, coords):
            if value == 0.0:
                continue
            matrix = out.setdefault(coord.operator, np.zeros((3, 3), dtype=complex))
            row = FLAVOR_ORDER.index(coord.final_flavor)
            col = FLAVOR_ORDER.index(coord.initial_flavor)
            matrix[row, col] += value * coord.scale * (1.0 if coord.component == "real" else 1.0j)
        return out

    center = _first_spectrum(evaluator(mapping(np.zeros(len(coords)))), name="center")
    n_bins = int(center.size)
    linear = np.zeros((n_bins, len(coords)), dtype=float)
    quadratic = np.zeros((n_bins, len(coords), len(coords)), dtype=float)
    axis_plus: list[np.ndarray] = []
    axis_minus: list[np.ndarray] = []
    for index, step in enumerate(step_values):
        plus_values = np.zeros(len(coords)); plus_values[index] = step
        minus_values = np.zeros(len(coords)); minus_values[index] = -step
        plus = _spectrum(evaluator(mapping(plus_values)), n_bins, name="axis_plus")
        minus = _spectrum(evaluator(mapping(minus_values)), n_bins, name="axis_minus")
        axis_plus.append(plus); axis_minus.append(minus)
        linear[:, index] = (plus - minus) / (2.0 * step)
        quadratic[:, index, index] = (plus + minus - 2.0 * center) / (2.0 * step * step)
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            values = np.zeros(len(coords)); values[i] = step_values[i]; values[j] = step_values[j]
            corner = _spectrum(evaluator(mapping(values)), n_bins, name="corner")
            cross = (corner - center - step_values[i] * linear[:, i] - step_values[j] * linear[:, j] - step_values[i] ** 2 * quadratic[:, i, i] - step_values[j] ** 2 * quadratic[:, j, j]) / (step_values[i] * step_values[j])
            quadratic[:, i, j] = quadratic[:, j, i] = 0.5 * cross
    return EFTQuadraticKernel(tuple(coord.name for coord in coords), center, linear, quadratic, reference)


def validate_quadratic_kernel(
    kernel: EFTQuadraticKernel,
    evaluator: Callable[[Sequence[float]], np.ndarray],
    points: Iterable[Sequence[float]],
    *,
    atol: float = 1.0e-10,
    rtol: float = 1.0e-5,
) -> dict[str, float | int]:
    """Compare a kernel with direct spectra at independent coefficient points."""

    maximum_abs = 0.0
    maximum_rel = 0.0
    checked = 0
    for point in points:
        values = np.asarray(point, dtype=float)
        if values.shape != (kernel.n_coordinates,):
            raise ValueError("held-out point has the wrong coordinate dimension")
        direct = _spectrum(evaluator(values), kernel.n_bins, name="direct")
        predicted = kernel.evaluate(values)
        difference = np.abs(predicted - direct)
        denominator = atol + rtol * np.abs(direct)
        maximum_abs = max(maximum_abs, float(np.max(difference)))
        maximum_rel = max(maximum_rel, float(np.max(difference / np.maximum(np.abs(direct), atol))))
        if np.any(difference > denominator):
            raise ValueError("quadratic kernel failed held-out direct validation")
        checked += 1
    return {"points": checked, "max_abs": maximum_abs, "max_rel": maximum_rel, "atol": atol, "rtol": rtol}


__all__ = [
    "EFTCoordinate",
    "EFTQuadraticKernel",
    "build_quadratic_kernel",
    "coordinate_metadata",
    "reactor_visible_coordinates",
    "validate_quadratic_kernel",
]
