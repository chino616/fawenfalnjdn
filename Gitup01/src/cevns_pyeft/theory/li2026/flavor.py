"""Canonical neutrino-flavor conventions and matrix helpers.

Flavor matrices use ``C[alpha, beta]``, where the row ``alpha`` is the
final neutrino flavor and the column ``beta`` is the initial flavor.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

NeutrinoFlavor = Literal["e", "mu", "tau"]
FLAVOR_ORDER = ("e", "mu", "tau")
N_FLAVOR = len(FLAVOR_ORDER)

FlavorMatrix = NDArray[np.complex128]


def zero_flavor_matrix() -> FlavorMatrix:
    """Return a zero matrix in the canonical flavor basis."""

    return np.zeros((N_FLAVOR, N_FLAVOR), dtype=np.complex128)


def identity_flavor_matrix() -> FlavorMatrix:
    """Return the identity matrix in the canonical flavor basis."""

    return np.eye(N_FLAVOR, dtype=np.complex128)


def flavor_projector(flavor: NeutrinoFlavor) -> FlavorMatrix:
    """Return the pure-state density matrix for one active flavor."""

    try:
        idx = FLAVOR_ORDER.index(flavor)
    except ValueError as exc:
        raise ValueError(
            f"Unknown neutrino flavor {flavor!r}; expected one of {FLAVOR_ORDER}"
        ) from exc

    rho = zero_flavor_matrix()
    rho[idx, idx] = 1.0
    return rho


def as_flavor_matrix(value: object, *, name: str = "matrix") -> FlavorMatrix:
    """Validate and convert a value to a finite complex ``(3, 3)`` matrix."""

    arr = np.asarray(value, dtype=np.complex128)

    if arr.shape != (N_FLAVOR, N_FLAVOR):
        raise ValueError(
            f"{name} must have shape ({N_FLAVOR},{N_FLAVOR}), got {arr.shape}"
        )

    if not np.all(np.isfinite(arr.real)):
        raise ValueError(f"{name} has non-finite real entries")

    if not np.all(np.isfinite(arr.imag)):
        raise ValueError(f"{name} has non-finite imaginary entries")

    return arr


def dagger(matrix: FlavorMatrix) -> FlavorMatrix:
    """Return the Hermitian conjugate of a flavor matrix."""

    matrix = as_flavor_matrix(matrix)
    return matrix.conj().T


def validate_density_matrix(
    rho: object,
    *,
    atol: float = 1e-10,
) -> FlavorMatrix:
    """Validate a normalized, Hermitian, positive-semidefinite density matrix."""

    rho = as_flavor_matrix(rho, name="rho")

    if not np.allclose(rho, rho.conj().T, atol=atol, rtol=0.0):
        raise ValueError("rho is not Hermitian")

    tr = np.trace(rho)
    if not np.isclose(tr.real, 1.0, atol=atol, rtol=0.0):
        raise ValueError(f"Tr(rho) != 1: {tr}")

    if abs(tr.imag) > atol:
        raise ValueError(f"Tr(rho) has imaginary part: {tr}")

    eig = np.linalg.eigvalsh(rho)
    if np.min(eig) < -atol:
        raise ValueError(
            f"rho is not positive semidefinite: min eigenvalue={eig.min()}"
        )

    return rho


def contract_density_kernel(
    rho: FlavorMatrix,
    kernel: FlavorMatrix,
    *,
    atol: float = 1e-10,
) -> float:
    """Contract an incoming density matrix with a detection kernel as Tr(rho K)."""

    rho = validate_density_matrix(rho, atol=atol)
    kernel = as_flavor_matrix(kernel, name="kernel")

    value = np.trace(rho @ kernel)
    if abs(value.imag) > atol * max(1.0, abs(value.real)):
        raise ValueError(f"rho-kernel contraction is not real: {value}")

    return float(value.real)


__all__ = [
    "NeutrinoFlavor",
    "FLAVOR_ORDER",
    "N_FLAVOR",
    "FlavorMatrix",
    "zero_flavor_matrix",
    "identity_flavor_matrix",
    "flavor_projector",
    "as_flavor_matrix",
    "dagger",
    "validate_density_matrix",
    "contract_density_kernel",
]
