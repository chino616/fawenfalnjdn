from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

import numpy as np

from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import combine_equal_stoichiometry
from cevns_pyeft.sources.state import pure_flavor_density
from cevns_pyeft.theory.li2026.flavor import FLAVOR_ORDER, validate_density_matrix


def _validate_coeff_tensor(coeffs: np.ndarray) -> np.ndarray:
    tensor = np.asarray(coeffs, dtype=np.complex128)
    if tensor.ndim != 3 or tensor.shape[-2:] != (3, 3):
        raise ValueError(
            "Flavor Fast coefficients must have shape (B,3,3), "
            f"got {tensor.shape}"
        )
    if not np.all(np.isfinite(tensor.real)) or not np.all(np.isfinite(tensor.imag)):
        raise ValueError("Flavor Fast coefficients must be finite")
    return tensor


def coefficient_bilinear_reference(coeffs: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """Reference ``B_IJ = Tr[rho C_I^dagger C_J]`` implementation."""

    tensor = _validate_coeff_tensor(coeffs)
    rho_matrix = validate_density_matrix(rho)
    basis_size = tensor.shape[0]
    out = np.zeros((basis_size, basis_size), dtype=np.complex128)
    for i in range(basis_size):
        for j in range(basis_size):
            out[i, j] = np.trace(rho_matrix @ tensor[i].conj().T @ tensor[j])
    return out


def coefficient_bilinear(coeffs: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """Optimized ``B_IJ = Tr[rho C_I^dagger C_J]`` implementation."""

    tensor = _validate_coeff_tensor(coeffs)
    rho_matrix = validate_density_matrix(rho)
    return np.einsum(
        "ab,ifb,jfa->ij",
        rho_matrix,
        np.conjugate(tensor),
        tensor,
        optimize=True,
    )


def source_density_for_fast_flavor(flavor: str) -> np.ndarray:
    """Map legacy SNS source labels to canonical incoming density matrices."""

    if flavor == "mub":
        return pure_flavor_density("mu")
    if flavor in FLAVOR_ORDER:
        return pure_flavor_density(flavor)  # type: ignore[arg-type]
    raise ValueError(f"Unknown source flavor {flavor!r}")


def source_densities_for_fast_flavors(flavors: Sequence[str]) -> np.ndarray:
    return np.stack([source_density_for_fast_flavor(str(flavor)) for flavor in flavors], axis=0)


def _coefficient_bilinears_for_sources(coeffs: np.ndarray, rhos: np.ndarray) -> np.ndarray:
    tensor = _validate_coeff_tensor(coeffs)
    rho_grid = np.asarray(rhos, dtype=np.complex128)
    if rho_grid.ndim != 3 or rho_grid.shape[-2:] != (3, 3):
        raise ValueError(f"source densities must have shape (F,3,3), got {rho_grid.shape}")
    out = np.zeros((rho_grid.shape[0], tensor.shape[0], tensor.shape[0]), dtype=np.complex128)
    for index, rho in enumerate(rho_grid):
        out[index] = coefficient_bilinear(tensor, rho)
    return out

def reconstruct_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    arr = np.asarray(full_kernel)
    coeffs = np.asarray(coeffs, dtype=complex)
    if arr.ndim == 5:
        return np.einsum('a,fhabm,b->fhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
    if arr.ndim == 6:
        return np.einsum('a,tfhabm,b->tfhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
    raise ValueError('full_kernel must have shape (F,H,B,B,M) or (T,F,H,B,B,M)')


def reconstruct_from_full_kernel_flavor(
    full_kernel: np.ndarray,
    coeffs: np.ndarray,
    source_rhos: np.ndarray,
) -> np.ndarray:
    arr = np.asarray(full_kernel)
    bilinear = _coefficient_bilinears_for_sources(coeffs, source_rhos)
    if arr.ndim == 5:
        if arr.shape[0] != bilinear.shape[0] or arr.shape[2:4] != bilinear.shape[1:3]:
            raise ValueError("full_kernel and flavor bilinears have incompatible shapes")
        return np.einsum("fhabm,fab->fhm", arr, bilinear, optimize=True)
    if arr.ndim == 6:
        if arr.shape[1] != bilinear.shape[0] or arr.shape[3:5] != bilinear.shape[1:3]:
            raise ValueError("full_kernel and flavor bilinears have incompatible shapes")
        return np.einsum("tfhabm,fab->tfhm", arr, bilinear, optimize=True)
    raise ValueError('full_kernel must have shape (F,H,B,B,M) or (T,F,H,B,B,M)')

def reconstruct_from_pair_templates(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    coeffs = np.asarray(coeffs, dtype=complex)
    B = coeffs.size
    out = np.zeros_like(np.asarray(diag[0]), dtype=float)
    for a in range(B):
        out = out + abs(coeffs[a]) ** 2 * np.asarray(diag[a], dtype=float)
    for k, (a, b) in enumerate(np.asarray(pair_index, dtype=int)):
        z = np.conjugate(coeffs[a]) * coeffs[b]
        out = out + 2.0 * np.real(z) * np.asarray(pair_re[k], dtype=float)
        out = out + 2.0 * np.imag(z) * np.asarray(pair_im[k], dtype=float)
    return out


def _source_factor_for_template(factors: np.ndarray, template: np.ndarray) -> np.ndarray:
    if template.ndim == 4:
        return factors[None, :, None, None]
    if template.ndim == 3:
        return factors[:, None, None]
    raise ValueError(f"template must have source-flavor axis, got shape {template.shape}")


def reconstruct_from_pair_templates_flavor(
    *,
    diag: np.ndarray,
    pair_re: np.ndarray,
    pair_im: np.ndarray,
    pair_index: np.ndarray,
    coeffs: np.ndarray,
    source_rhos: np.ndarray,
) -> np.ndarray:
    bilinear = _coefficient_bilinears_for_sources(coeffs, source_rhos)
    diag_arr = np.asarray(diag, dtype=float)
    out = np.zeros_like(diag_arr[0], dtype=float)
    for a in range(bilinear.shape[1]):
        factor = np.real(bilinear[:, a, a])
        out = out + _source_factor_for_template(factor, out) * diag_arr[a]
    for k, (a, b) in enumerate(np.asarray(pair_index, dtype=int)):
        z = bilinear[:, a, b]
        re_factor = np.real(z)
        im_factor = np.imag(z)
        out = out + 2.0 * _source_factor_for_template(re_factor, out) * np.asarray(pair_re[k], dtype=float)
        out = out + 2.0 * _source_factor_for_template(im_factor, out) * np.asarray(pair_im[k], dtype=float)
    return out

def reconstruct_real_events_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_full_kernel(full_kernel, coeffs))


def reconstruct_real_events_from_full_kernel_flavor(full_kernel: np.ndarray, coeffs: np.ndarray, source_rhos: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_full_kernel_flavor(full_kernel, coeffs, source_rhos))

def reconstruct_real_events_from_pair_templates(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_pair_templates(diag=diag, pair_re=pair_re, pair_im=pair_im, pair_index=pair_index, coeffs=coeffs))


def reconstruct_real_events_from_pair_templates_flavor(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray, source_rhos: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_pair_templates_flavor(diag=diag, pair_re=pair_re, pair_im=pair_im, pair_index=pair_index, coeffs=coeffs, source_rhos=source_rhos))

def reconstruct_counts_from_kernel(kernel: Mapping[str, Any], coeff_vector: np.ndarray) -> Dict[str, Any]:
    full = np.asarray(kernel['full_kernel'])
    targets = [str(x) for x in kernel['targets']]
    flavors = [str(x) for x in kernel['source_flavors']]
    coeffs = np.asarray(coeff_vector)
    if coeffs.ndim == 3:
        source_rhos = source_densities_for_fast_flavors(flavors)
        raw = reconstruct_real_events_from_full_kernel_flavor(full, coeffs, source_rhos)
    else:
        raw = reconstruct_real_events_from_full_kernel(full, np.asarray(coeffs, dtype=complex))
    channel_summed = np.sum(raw, axis=2)
    if 'CsI' in targets:
        target_index = targets.index('CsI')
        by_flavor = {flavor: np.asarray(channel_summed[target_index, i], dtype=float) for i, flavor in enumerate(flavors)}
    elif 'Cs133' in targets and 'I127' in targets:
        cs = targets.index('Cs133')
        ii = targets.index('I127')
        by_flavor = {flavor: combine_equal_stoichiometry(channel_summed[cs, i], channel_summed[ii, i]) for i, flavor in enumerate(flavors)}
    elif len(targets) == 1:
        by_flavor = {flavor: np.asarray(channel_summed[0, i], dtype=float) for i, flavor in enumerate(flavors)}
    else:
        raise ValueError(f'Unsupported target layout for Fast reconstruction: {targets}')
    counts_bin: Dict[str, np.ndarray] = {flavor: np.asarray(by_flavor[flavor], dtype=float) for flavor in ('mu', 'e', 'mub')}
    counts_bin['total'] = counts_bin['mu'] + counts_bin['e'] + counts_bin['mub']
    pe_widths = np.diff(np.asarray(kernel['pe_bins'], dtype=float))
    counts_npe = {key: np.asarray(value, dtype=float) / pe_widths for key, value in counts_bin.items()}
    return {'counts_per_bin': counts_bin, 'counts_per_npe': counts_npe, 'raw_target_flavor_channel_bin': raw, 'channel_summed_target_flavor_bin': channel_summed, 'pe_bins': np.asarray(kernel['pe_bins'], dtype=float), 'kernel_axis_kind': str(kernel.get('kernel_axis_kind', ''))}


__all__ = [
    "reconstruct_from_full_kernel",
    "coefficient_bilinear_reference",
    "coefficient_bilinear",
    "source_density_for_fast_flavor",
    "source_densities_for_fast_flavors",
    "reconstruct_from_full_kernel_flavor",
    "reconstruct_from_pair_templates",
    "reconstruct_from_pair_templates_flavor",
    "reconstruct_real_events_from_full_kernel",
    "reconstruct_real_events_from_full_kernel_flavor",
    "reconstruct_real_events_from_pair_templates",
    "reconstruct_real_events_from_pair_templates_flavor",
    "reconstruct_counts_from_kernel",
]
