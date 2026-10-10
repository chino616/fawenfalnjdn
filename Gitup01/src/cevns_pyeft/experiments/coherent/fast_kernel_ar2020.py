from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np
from dataclasses import asdict

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
) -> tuple[np.ndarray, np.ndarray]:
    resp = ResponseDB(str(responses_json)).get("Ar40")
    er_grid, er_weights = _er_grid(resp, int(n_er))
    eff = _interp_eff(_data_path(responses_json, efficiency_data_path), 0, 2, low=0.0)
    fold = np.zeros((er_grid.size, bin_edges.size - 1), dtype=float)
    for i, T in enumerate(er_grid):
        mean = (0.246 + 0.00078 * float(T)) * float(T)
        for j, (left, right) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
            x = np.linspace(float(left), float(right), max(2, int(n_obs_sub)), dtype=float)
            sigma = 0.58 * np.sqrt(np.maximum(x, 1.0e-300))
            smear = np.exp(-0.5 * ((x - mean) / sigma) ** 2) / (np.sqrt(2.0 * np.pi) * sigma)
            fold[i, j] = er_weights[i] * float(_trapz(np.asarray(eff(x), dtype=float) * smear, x))
    return er_grid, fold

def build_fast_kernel_ar2020(
    responses_json: str | Path,
    *,
    basis: Optional[Sequence[BasisElement]] = None,
    efficiency_data_path: str | Path = AR_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    bin_edges: np.ndarray = AR_BINS_12,
    n_obs_sub: int = 8,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "quark_mass_resolved",
    n_er: int = 21,
    n_enu: int = 120,
) -> Dict[str, Any]:
    _ = sin2thetaW
    basis_elements = list(basis or li2026_left_basis_current())
    bin_edges = np.asarray(bin_edges, dtype=float)
    er_grid, fold = _ar_fold(
        responses_json,
        n_er=n_er,
        n_obs_sub=n_obs_sub,
        bin_edges=bin_edges,
        efficiency_data_path=efficiency_data_path,
    )
    static = _target_static(responses_json, target="Ar40", er_grid_keV=er_grid, fold_kernel=fold)
    full = _build_one_target_kernel_csi2017_ar(
        static=static,
        dataset="Ar2020",
        basis_elements=basis_elements,
        n_enu=n_enu,
        c10_mass_mode=c10_mass_mode,
        detector_mass_kg=24.0,
    )[None, ...]
    metadata = {
        "model": "li2026_matrixized_ar2020_gaussian_obs_fold",
        "responses": str(responses_json),
        "dataset": "Ar2020",
        "target_mode": "Ar40",
        "targets": ["Ar40"],
        "source_flavors": list(FLAVORS),
        "channels": list(CHANNELS),
        "basis": [asdict(b) for b in basis_elements],
        "pe_bins": bin_edges.tolist(),
        "observable": "Ar prompt observable",
        "n_ER": int(n_er),
        "n_Enu": int(n_enu),
        "n_obs_sub": int(n_obs_sub),
        "efficiency_data_path": str(efficiency_data_path),
        "detector_mass_kg": 24.0,
        "flavor_acceptance": dict(FLAVOR_ACCEPTANCE_ONE),
        "detector_model": "mean=(0.246+0.00078*Tnr)*Tnr, sigma(obs)=0.58*sqrt(obs)",
    }
    return _make_payload(metadata=metadata, full_kernel=full)


__all__ = ["build_fast_kernel_ar2020"]
