from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np
from dataclasses import asdict

from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import CSI2017_BINS_25, CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH, CSI2017_PE_PER_KEV
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import combine_equal_stoichiometry
from cevns_pyeft.experiments.base import _data_path, _interp_eff
from cevns_pyeft.kernels.basis import BasisElement, li2026_left_basis_current
from cevns_pyeft.kernels.builder import FLAVOR_ACCEPTANCE_ONE, FLAVORS, CHANNELS, KernelPayload, _build_one_target_kernel_csi2017_ar, _kernel_to_diag_pair_templates, _make_payload, _target_static, _trapz_weights

def _csi2017_fold(
    responses_json: str | Path,
    *,
    pe_bins: np.ndarray,
    pe_per_keV: float,
    n_pe_grid: int,
    efficiency_data_path: str | Path,
) -> tuple[np.ndarray, np.ndarray]:
    eff = _interp_eff(
        _data_path(responses_json, efficiency_data_path),
        0,
        1,
        low=1.0e-10,
        threshold=4.9,
    )
    pe_grid = np.linspace(float(pe_bins[0]), float(pe_bins[-1]), int(n_pe_grid), dtype=float)
    er_grid = pe_grid / float(pe_per_keV)
    fold = np.zeros((er_grid.size, pe_bins.size - 1), dtype=float)
    for ib, (left, right) in enumerate(zip(pe_bins[:-1], pe_bins[1:])):
        mask = (pe_grid >= left - 1.0e-12) & (pe_grid <= right + 1.0e-12)
        xs = pe_grid[mask]
        weights = _trapz_weights(xs) / float(pe_per_keV)
        for x, w in zip(xs, weights):
            ir = int(np.argmin(np.abs(pe_grid - x)))
            fold[ir, ib] += float(w) * float(eff(float(x)))
    return er_grid, fold

def build_fast_kernel_csi2017(
    responses_json: str | Path,
    *,
    basis: Optional[Sequence[BasisElement]] = None,
    efficiency_data_path: str | Path = CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH,
    pe_bins: np.ndarray = CSI2017_BINS_25,
    pe_per_keV: float = CSI2017_PE_PER_KEV,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "quark_mass_resolved",
    n_er: int = 251,
    n_enu: int = 120,
) -> Dict[str, Any]:
    _ = sin2thetaW
    basis_elements = list(basis or li2026_left_basis_current())
    pe_bins = np.asarray(pe_bins, dtype=float)
    er_grid, fold = _csi2017_fold(
        responses_json,
        pe_bins=pe_bins,
        pe_per_keV=pe_per_keV,
        n_pe_grid=n_er,
        efficiency_data_path=efficiency_data_path,
    )
    raw = {}
    for target in ("Cs133", "I127"):
        static = _target_static(responses_json, target=target, er_grid_keV=er_grid, fold_kernel=fold)
        raw[target] = _build_one_target_kernel_csi2017_ar(
            static=static,
            dataset="CsI2017",
            basis_elements=basis_elements,
            n_enu=n_enu,
            c10_mass_mode=c10_mass_mode,
            detector_mass_kg=14.6,
        )
    full = np.stack(
        [raw["Cs133"], raw["I127"], combine_equal_stoichiometry(raw["Cs133"], raw["I127"])],
        axis=0,
    )
    metadata = {
        "model": "li2026_matrixized_csi2017_delta_fold",
        "responses": str(responses_json),
        "dataset": "CsI2017",
        "target_mode": "all",
        "targets": ["Cs133", "I127", "CsI"],
        "source_flavors": list(FLAVORS),
        "channels": list(CHANNELS),
        "basis": [asdict(b) for b in basis_elements],
        "pe_bins": pe_bins.tolist(),
        "pe_per_keV": float(pe_per_keV),
        "n_ER": int(n_er),
        "n_Enu": int(n_enu),
        "efficiency_data_path": str(efficiency_data_path),
        "detector_mass_kg": 14.6,
        "flavor_acceptance": dict(FLAVOR_ACCEPTANCE_ONE),
        "detector_model": "delta PE = 1.17 * Tnr_keV, COHERENT CsI 2017 efficiency",
    }
    return _make_payload(metadata=metadata, full_kernel=full)


__all__ = ["build_fast_kernel_csi2017"]
