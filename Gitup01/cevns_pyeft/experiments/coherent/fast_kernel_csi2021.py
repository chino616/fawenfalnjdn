from __future__ import annotations
from .csi2021_definition import DEFINITION

from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np

from cevns_pyeft.kernels.basis import BasisElement, li2026_left_basis_current
from cevns_pyeft.kernels.builder import DEFAULT_ACCEPTANCE, PE_BINS_9, build_matrixized_kernel


def build_fast_kernel_csi2021(responses_json: str | Path, basis: Optional[Sequence[BasisElement]]=None, *, sin2thetaW: float=DEFINITION.reproduction_sin2thetaW, c10_mass_mode: str=DEFINITION.physical.c10_mass_mode, n_er: int=DEFINITION.numerical_profiles['fast']['n_er'], n_enu: int=DEFINITION.numerical_profiles['fast']['n_enu'], n_pe_sub: int=DEFINITION.numerical_profiles['fast']['n_pe_bin'], pe_step: float=DEFINITION.numerical_profiles['fast']['pe_step']) -> Dict[str, Any]:
    _ = sin2thetaW
    payload = build_matrixized_kernel(responses_json=str(responses_json), dataset='CsI2021', basis_elements=list(basis or li2026_left_basis_current()), pe_bins=PE_BINS_9, target_mode='all', ER_min_keV=0.1, n_ER=int(n_er), n_Enu=int(n_enu), n_PE_sub=int(n_pe_sub), pe_step=float(pe_step), c10_mass_mode=str(c10_mass_mode), flavor_acceptance=DEFAULT_ACCEPTANCE, n_jobs=1)
    return {'basis': payload.metadata['basis'], 'targets': payload.metadata['targets'], 'source_flavors': payload.metadata['source_flavors'], 'channels': payload.metadata['channels'], 'pe_bins': np.asarray(payload.metadata['pe_bins'], dtype=float), 'kernel_axis_kind': 'channel_resolved_full_li2026', 'metadata': payload.metadata, 'full_kernel': np.asarray(payload.full_kernel), 'diag': np.asarray(payload.diag), 'pair_re': np.asarray(payload.pair_re), 'pair_im': np.asarray(payload.pair_im), 'pair_index': np.asarray(payload.pair_index)}


__all__ = ["build_fast_kernel_csi2021"]
