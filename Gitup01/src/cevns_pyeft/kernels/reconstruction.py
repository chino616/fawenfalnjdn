from __future__ import annotations

from typing import Any, Dict, Mapping

import numpy as np

from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import combine_equal_stoichiometry

def reconstruct_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    arr = np.asarray(full_kernel)
    coeffs = np.asarray(coeffs, dtype=complex)
    if arr.ndim == 5:
        return np.einsum('a,fhabm,b->fhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
    if arr.ndim == 6:
        return np.einsum('a,tfhabm,b->tfhm', np.conjugate(coeffs), arr, coeffs, optimize=True)
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

def reconstruct_real_events_from_full_kernel(full_kernel: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_full_kernel(full_kernel, coeffs))

def reconstruct_real_events_from_pair_templates(*, diag: np.ndarray, pair_re: np.ndarray, pair_im: np.ndarray, pair_index: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    return np.real(reconstruct_from_pair_templates(diag=diag, pair_re=pair_re, pair_im=pair_im, pair_index=pair_index, coeffs=coeffs))

def reconstruct_counts_from_kernel(kernel: Mapping[str, Any], coeff_vector: np.ndarray) -> Dict[str, Any]:
    full = np.asarray(kernel['full_kernel'])
    raw = reconstruct_real_events_from_full_kernel(full, np.asarray(coeff_vector, dtype=complex))
    targets = [str(x) for x in kernel['targets']]
    flavors = [str(x) for x in kernel['source_flavors']]
    channel_summed = np.sum(raw, axis=2)
    if 'CsI' in targets:
        target_index = targets.index('CsI')
        by_flavor = {flavor: np.asarray(channel_summed[target_index, i], dtype=float) for i, flavor in enumerate(flavors)}
    else:
        cs = targets.index('Cs133')
        ii = targets.index('I127')
        by_flavor = {flavor: combine_equal_stoichiometry(channel_summed[cs, i], channel_summed[ii, i]) for i, flavor in enumerate(flavors)}
    counts_bin: Dict[str, np.ndarray] = {flavor: np.asarray(by_flavor[flavor], dtype=float) for flavor in ('mu', 'e', 'mub')}
    counts_bin['total'] = counts_bin['mu'] + counts_bin['e'] + counts_bin['mub']
    counts_npe = {key: np.asarray(value, dtype=float) / PE_WIDTHS_9 for key, value in counts_bin.items()}
    return {'counts_per_bin': counts_bin, 'counts_per_npe': counts_npe, 'raw_target_flavor_channel_bin': raw, 'channel_summed_target_flavor_bin': channel_summed, 'pe_bins': np.asarray(kernel['pe_bins'], dtype=float), 'kernel_axis_kind': str(kernel.get('kernel_axis_kind', ''))}


__all__ = [
    "reconstruct_from_full_kernel",
    "reconstruct_from_pair_templates",
    "reconstruct_real_events_from_full_kernel",
    "reconstruct_real_events_from_pair_templates",
    "reconstruct_counts_from_kernel",
]
