from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np
from dataclasses import asdict
from .ar2020_definition import DEFINITION

from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import AR_BINS_12, AR_DEFAULT_EFFICIENCY_RELATIVE_PATH
from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.kernels.basis import BasisElement, li2026_left_basis_current
from cevns_pyeft.kernels.builder import FLAVOR_ACCEPTANCE_ONE, FLAVORS, CHANNELS, _build_one_target_kernel_csi2017_ar, _make_payload, _target_static
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.counts import _er_grid
from cevns_pyeft.rates.differential import _trapz

def _ar_fold(
    responses_json: str | Path,
    *,
    n_er: int,
    n_obs_sub: int,
    bin_edges: np.ndarray,
    efficiency_data_path: str | Path,
    physical=None,
) -> tuple[np.ndarray, np.ndarray]:
    from .ar2020_definition import DEFINITION
    from .slow_counts_ar2020 import ar_fold_matrix
    physical = physical or DEFINITION.physical
    resp = ResponseDB(str(responses_json)).get(physical.response_key)
    er_grid, er_weights = _er_grid(resp, int(n_er))
    eff = _interp_eff(_data_path(responses_json, efficiency_data_path), *physical.efficiency_columns, low=physical.efficiency_low)
    fold = ar_fold_matrix(er_grid, er_weights, bin_edges, eff, physical, n_obs_sub)
    return er_grid, fold

def build_fast_kernel_ar2020(
    responses_json: str | Path,
    *,
    basis: Optional[Sequence[BasisElement]] = None,
    efficiency_data_path: str | Path = AR_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    bin_edges: np.ndarray = AR_BINS_12,
    n_obs_sub: int = DEFINITION.numerical_profiles['fast']['n_obs_sub'],
    sin2thetaW: float = DEFINITION.reproduction_sin2thetaW,
    c10_mass_mode: str = DEFINITION.physical.c10_mass_mode,
    n_er: int = DEFINITION.numerical_profiles['fast']['n_er'],
    n_enu: int = DEFINITION.numerical_profiles['fast']['n_enu'],
    definition=None,
) -> Dict[str, Any]:
    from .ar2020_definition import DEFINITION
    from .sns import build_neutrino_empirical_flux_sns
    config = definition or DEFINITION
    physical = config.physical
    if definition is not None:
        bin_edges = config.observation.edges
    flux = build_neutrino_empirical_flux_sns(physical.run.legacy_dataset(config.dataset_id), num_points=physical.run.num_points, use_interpolation=physical.run.interpolation)
    basis_elements = list(basis or li2026_left_basis_current())
    bin_edges = np.asarray(bin_edges, dtype=float)
    er_grid, fold = _ar_fold(
        responses_json,
        n_er=n_er,
        n_obs_sub=n_obs_sub,
        bin_edges=bin_edges,
        efficiency_data_path=efficiency_data_path, physical=physical,
    )
    static = _target_static(responses_json, target=physical.target_id, er_grid_keV=er_grid, fold_kernel=fold)
    full = _build_one_target_kernel_csi2017_ar(
        static=static,
        dataset="Ar2020",
        basis_elements=basis_elements,
        n_enu=n_enu,
        c10_mass_mode=c10_mass_mode,
        detector_mass_kg=physical.mass_kg, flux=flux,
    )[None, ...]
    metadata = {
        "model": "li2026_matrixized_ar2020_gaussian_obs_fold",
        "responses": str(responses_json),
        "dataset": "Ar2020",
        "target_mode": "Ar40",
        "targets": [physical.target_id],
        "source_flavors": list(FLAVORS),
        "channels": list(CHANNELS),
        "basis": [asdict(b) for b in basis_elements],
        "pe_bins": bin_edges.tolist(),
        "observable": "Ar prompt observable",
        "n_ER": int(n_er),
        "n_Enu": int(n_enu),
        "n_obs_sub": int(n_obs_sub),
        "efficiency_data_path": str(efficiency_data_path),
        "detector_mass_kg": physical.mass_kg,
        "flavor_acceptance": dict(FLAVOR_ACCEPTANCE_ONE),
        "detector_model": "Gaussian sigma(observed); legacy units",
        "response_parameters": {"mean_linear":physical.mean_linear,"mean_quadratic":physical.mean_quadratic,"sigma_coefficient":physical.sigma_coefficient},
    }
    return _make_payload(metadata=metadata, full_kernel=full)


__all__ = ["build_fast_kernel_ar2020"]
