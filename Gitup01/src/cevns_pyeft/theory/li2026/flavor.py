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
DEFAULT_KERNEL_RTOL = 1.0e-10
DEFAULT_KERNEL_ATOL = 0.0


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


def validate_flavor_kernel(
    kernel: object,
    *,
    rtol: float = DEFAULT_KERNEL_RTOL,
    atol: float = DEFAULT_KERNEL_ATOL,
    name: str = "kernel",
) -> FlavorMatrix:
    """Validate a finite Hermitian positive-semidefinite Flavor kernel.

    Both the Hermitian residual and the smallest eigenvalue are compared with
    the kernel's own numerical scale.  In particular, there is no order-one
    tolerance floor, because physical cross-section kernels can be much
    smaller than one in their canonical units.
    """

    kernel = as_flavor_matrix(kernel, name=name)
    rtol = float(rtol)
    atol = float(atol)
    if not np.isfinite(rtol) or rtol < 0.0:
        raise ValueError("rtol must be finite and non-negative")
    if not np.isfinite(atol) or atol < 0.0:
        raise ValueError("atol must be finite and non-negative")

    adjoint = kernel.conj().T
    scale = float(np.linalg.norm(kernel, ord="fro"))
    residual = float(np.linalg.norm(kernel - adjoint, ord="fro"))
    hermitian_tolerance = atol + rtol * scale
    if residual > hermitian_tolerance:
        raise ValueError(
            f"{name} is not Hermitian: residual={residual:.6e}, "
            f"tolerance={hermitian_tolerance:.6e}, scale={scale:.6e}"
        )

    hermitian_kernel = 0.5 * (kernel + adjoint)
    eigenvalues = np.linalg.eigvalsh(hermitian_kernel)
    min_eigenvalue = float(np.min(eigenvalues))
    spectral_scale = float(np.max(np.abs(eigenvalues)))
    psd_tolerance = atol + rtol * spectral_scale
    if min_eigenvalue < -psd_tolerance:
        raise ValueError(
            f"{name} is not positive semidefinite: "
            f"min eigenvalue={min_eigenvalue:.6e}, "
            f"tolerance={psd_tolerance:.6e}, scale={spectral_scale:.6e}"
        )

    return kernel


def contract_density_kernel(
    rho: FlavorMatrix,
    kernel: FlavorMatrix,
    *,
    atol: float = 1e-10,
    kernel_rtol: float = DEFAULT_KERNEL_RTOL,
    kernel_atol: float = DEFAULT_KERNEL_ATOL,
) -> float:
    """Contract an incoming density matrix with a physical kernel as Tr(rho K)."""

    rho = validate_density_matrix(rho, atol=atol)
    kernel = validate_flavor_kernel(
        kernel,
        rtol=kernel_rtol,
        atol=kernel_atol,
        name="kernel",
    )

    value = np.trace(rho @ kernel)
    contraction_scale = float(
        np.linalg.norm(rho, ord="fro")
        * np.linalg.norm(kernel, ord="fro")
    )
    tolerance = float(kernel_atol) + float(kernel_rtol) * contraction_scale
    if abs(value.imag) > tolerance:
        raise ValueError(
            "rho-kernel contraction is not real: "
            f"value={value}, tolerance={tolerance:.6e}, "
            f"scale={contraction_scale:.6e}"
        )
    if value.real < -tolerance:
        raise ValueError(
            "rho-kernel contraction is negative: "
            f"value={value.real:.6e}, tolerance={tolerance:.6e}, "
            f"scale={contraction_scale:.6e}. Check kernel PSD, "
            "interference/sign convention, Flavor contraction, and "
            "kinematic support."
        )
    if value.real < 0.0:
        return 0.0

    return float(value.real)


def _validated_density_for_kernel_grid(
    rho: object,
    grid_shape: tuple[int, ...],
    *,
    atol: float,
) -> FlavorMatrix:
    rho_array = np.asarray(rho, dtype=np.complex128)
    if rho_array.shape == (N_FLAVOR, N_FLAVOR):
        rho_matrix = validate_density_matrix(rho_array, atol=atol)
        if grid_shape == ():
            return rho_matrix
        return np.broadcast_to(rho_matrix, grid_shape + (N_FLAVOR, N_FLAVOR))
    if rho_array.ndim < 3 or rho_array.shape[-2:] != (N_FLAVOR, N_FLAVOR):
        raise ValueError(
            "rho must have shape (3,3) or (...,3,3), "
            f"got {rho_array.shape}"
        )
    if rho_array.shape[:-2] != grid_shape:
        raise ValueError(
            f"rho energy shape must be {grid_shape}, got {rho_array.shape[:-2]}"
        )
    for index in np.ndindex(grid_shape):
        try:
            validate_density_matrix(rho_array[index], atol=atol)
        except ValueError as exc:
            raise ValueError(f"rho{index} is invalid: {exc}") from exc
    return rho_array


def contract_density_kernel_grid_reference(
    rho: object,
    kernel: object,
    *,
    atol: float = 1e-10,
    kernel_rtol: float = DEFAULT_KERNEL_RTOL,
    kernel_atol: float = DEFAULT_KERNEL_ATOL,
) -> np.ndarray:
    """Reference pointwise ``Tr(rho K)`` over a Flavor-kernel grid.

    ``rho`` may be a constant ``(3,3)`` density matrix or an array with the
    same leading energy axes as ``kernel``.  ``kernel`` may be ``(3,3)`` or
    ``(...,3,3)``.
    """

    kernel_array = np.asarray(kernel, dtype=np.complex128)
    if kernel_array.shape == (N_FLAVOR, N_FLAVOR):
        rho_matrix = _validated_density_for_kernel_grid(
            rho,
            (),
            atol=atol,
        )
        return np.asarray(
            contract_density_kernel(
                rho_matrix,
                kernel_array,
                atol=atol,
                kernel_rtol=kernel_rtol,
                kernel_atol=kernel_atol,
            )
        )
    if kernel_array.ndim < 3 or kernel_array.shape[-2:] != (N_FLAVOR, N_FLAVOR):
        raise ValueError(
            "kernel must have shape (3,3) or (...,3,3), "
            f"got {kernel_array.shape}"
        )

    grid_shape = kernel_array.shape[:-2]
    rho_grid = _validated_density_for_kernel_grid(
        rho,
        grid_shape,
        atol=atol,
    )
    values = np.zeros(grid_shape, dtype=float)
    for index in np.ndindex(grid_shape):
        values[index] = contract_density_kernel(
            rho_grid[index],
            kernel_array[index],
            atol=atol,
            kernel_rtol=kernel_rtol,
            kernel_atol=kernel_atol,
        )
    return values


def contract_density_kernel_grid(
    rho: object,
    kernel: object,
    *,
    atol: float = 1e-10,
    kernel_rtol: float = DEFAULT_KERNEL_RTOL,
    kernel_atol: float = DEFAULT_KERNEL_ATOL,
) -> np.ndarray:
    """Pointwise ``Tr(rho K)`` over a Flavor-kernel grid."""

    kernel_array = np.asarray(kernel, dtype=np.complex128)
    if kernel_array.shape == (N_FLAVOR, N_FLAVOR):
        return contract_density_kernel_grid_reference(
            rho,
            kernel_array,
            atol=atol,
            kernel_rtol=kernel_rtol,
            kernel_atol=kernel_atol,
        )
    if kernel_array.ndim < 3 or kernel_array.shape[-2:] != (N_FLAVOR, N_FLAVOR):
        raise ValueError(
            "kernel must have shape (3,3) or (...,3,3), "
            f"got {kernel_array.shape}"
        )

    grid_shape = kernel_array.shape[:-2]
    rho_grid = _validated_density_for_kernel_grid(
        rho,
        grid_shape,
        atol=atol,
    )
    flat_kernels = kernel_array.reshape((-1, N_FLAVOR, N_FLAVOR))
    for flat_index, matrix in enumerate(flat_kernels):
        index = np.unravel_index(flat_index, grid_shape)
        validate_flavor_kernel(
            matrix,
            rtol=kernel_rtol,
            atol=kernel_atol,
            name=f"kernel{index}",
        )

    values = np.einsum(
        "...ab,...ba->...",
        rho_grid,
        kernel_array,
        optimize=True,
    )
    contraction_scale = (
        np.linalg.norm(rho_grid, axis=(-2, -1))
        * np.linalg.norm(kernel_array, axis=(-2, -1))
    )
    tolerance = kernel_atol + kernel_rtol * contraction_scale
    imaginary_failure = np.abs(values.imag) > tolerance
    if np.any(imaginary_failure):
        flat_index = int(np.flatnonzero(imaginary_failure)[0])
        index = np.unravel_index(flat_index, values.shape)
        raise ValueError(
            f"rho-kernel contraction at index {index} is not real: "
            f"value={values[index]}, tolerance={tolerance[index]:.6e}, "
            f"scale={contraction_scale[index]:.6e}"
        )

    real_values = np.asarray(values.real)
    negative_failure = real_values < -tolerance
    if np.any(negative_failure):
        flat_index = int(np.flatnonzero(negative_failure)[0])
        index = np.unravel_index(flat_index, values.shape)
        raise ValueError(
            f"rho-kernel contraction at index {index} is negative: "
            f"value={real_values[index]:.6e}, "
            f"tolerance={tolerance[index]:.6e}, "
            f"scale={contraction_scale[index]:.6e}. Check kernel PSD, "
            "interference/sign convention, Flavor contraction, and "
            "kinematic support."
        )

    return np.where(real_values < 0.0, 0.0, real_values)


__all__ = [
    "NeutrinoFlavor",
    "FLAVOR_ORDER",
    "N_FLAVOR",
    "FlavorMatrix",
    "DEFAULT_KERNEL_RTOL",
    "DEFAULT_KERNEL_ATOL",
    "zero_flavor_matrix",
    "identity_flavor_matrix",
    "flavor_projector",
    "as_flavor_matrix",
    "dagger",
    "validate_density_matrix",
    "validate_flavor_kernel",
    "contract_density_kernel",
    "contract_density_kernel_grid_reference",
    "contract_density_kernel_grid",
]
