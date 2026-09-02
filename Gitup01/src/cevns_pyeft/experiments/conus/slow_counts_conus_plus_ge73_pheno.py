from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from cevns_pyeft.experiments.conus.detector_response import (
    conus_ge73_efficiency,
    conus_ge73_response_density,
    reco_energy_bin_edges_evee,
)
from cevns_pyeft.experiments.conus.kinematics import (
    AVAILABLE_CROSS_SECTION_MODELS,
    AVAILABLE_KINEMATICS,
    differential_cross_section_conus_ge73,
    enu_min_exact_conus_ge73,
    enu_min_heavy_nucleus_conus_ge73,
    recoil_max_exact_keV,
)
from cevns_pyeft.experiments.conus.source import ENERGY_MAX_MEV, ENERGY_MIN_MEV, load_conus_plus_ge73_reactor_flux
from cevns_pyeft.experiments.registry import get_experiment_spec
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.rates.differential import _trapz

Triplet = tuple[int, int, str]

AVOGADRO_MOL_INV = 6.02214076e23
DATASET_ID = "conus_plus_ge73_pheno"


@dataclass(frozen=True)
class SlowIntegrationSettings:
    n_true_recoil: int = 121
    n_neutrino: int = 240
    reco_step_evee: float = 1.0
    recoil_max_keVnr: float | None = None


def _spec_data(experiment_spec: Any) -> dict[str, Any]:
    data = getattr(experiment_spec, "data", None)
    if isinstance(data, dict):
        return data
    if isinstance(experiment_spec, dict):
        return experiment_spec
    return {}


def _resolve_spec(experiment_spec: Any | None) -> Any:
    return get_experiment_spec(DATASET_ID) if experiment_spec is None else experiment_spec


def _coefficient_triplets(
    coefficients: Mapping[Triplet, complex] | None,
    wc_triplets: Mapping[Triplet, complex] | None,
) -> dict[Triplet, complex]:
    out: dict[Triplet, complex] = {}
    if coefficients:
        out.update({key: complex(value) for key, value in coefficients.items()})
    if wc_triplets:
        out.update({key: complex(value) for key, value in wc_triplets.items()})
    return out


def nuclei_per_kg_ge73(experiment_spec: Any | None = None) -> float:
    spec = _resolve_spec(experiment_spec)
    target = _spec_data(spec).get("target", {})
    molar_mass = float(target.get("molar_mass_g_mol", 73.0)) if isinstance(target, dict) else 73.0
    return AVOGADRO_MOL_INV * 1000.0 / molar_mass


def target_time_normalization(experiment_spec: Any | None = None) -> float:
    spec = _resolve_spec(experiment_spec)
    detector = _spec_data(spec).get("detector", {})
    exposure_kg_day = float(detector.get("exposure_kg_day", 119.0)) if isinstance(detector, dict) else 119.0
    return nuclei_per_kg_ge73(spec) * exposure_kg_day * float(c.SEC_PER_DAY)


def true_recoil_grid_keVnr(settings: SlowIntegrationSettings | None = None) -> np.ndarray:
    cfg = SlowIntegrationSettings() if settings is None else settings
    if int(cfg.n_true_recoil) < 2:
        raise ValueError("n_true_recoil must be >= 2")
    recoil_max = float(recoil_max_exact_keV(ENERGY_MAX_MEV) if cfg.recoil_max_keVnr is None else cfg.recoil_max_keVnr)
    return np.linspace(0.0, recoil_max, int(cfg.n_true_recoil), dtype=float)


def neutrino_grid_for_recoil(
    T_keVnr: float,
    settings: SlowIntegrationSettings | None = None,
    *,
    kinematics: str = "publication_reproduction",
) -> np.ndarray:
    cfg = SlowIntegrationSettings() if settings is None else settings
    if int(cfg.n_neutrino) < 2:
        raise ValueError("n_neutrino must be >= 2")
    if kinematics not in AVAILABLE_KINEMATICS:
        raise ValueError(f"Unknown kinematics {kinematics!r}")
    threshold_fn = (
        enu_min_heavy_nucleus_conus_ge73
        if kinematics == "heavy_nucleus_approximation"
        else enu_min_exact_conus_ge73
    )
    emin = max(float(threshold_fn(float(T_keVnr))), ENERGY_MIN_MEV)
    if emin >= ENERGY_MAX_MEV:
        return np.asarray([], dtype=float)
    return np.linspace(emin, ENERGY_MAX_MEV, int(cfg.n_neutrino), dtype=float)


def true_recoil_spectrum_per_nucleus_s_keV(
    T_keVnr: float,
    experiment_spec: Any | None = None,
    *,
    coefficients: Mapping[Triplet, complex] | None = None,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "quark_mass_resolved",
    settings: SlowIntegrationSettings | None = None,
) -> float:
    spec = _resolve_spec(experiment_spec)
    if cross_section_model not in AVAILABLE_CROSS_SECTION_MODELS:
        raise ValueError(f"Unknown cross_section_model {cross_section_model!r}")
    if kinematics not in AVAILABLE_KINEMATICS:
        raise ValueError(f"Unknown kinematics {kinematics!r}")
    enu = neutrino_grid_for_recoil(
        float(T_keVnr),
        settings,
        kinematics=kinematics,
    )
    if enu.size == 0:
        return 0.0
    flux = load_conus_plus_ge73_reactor_flux(spec)["measured"]["nuebar"]
    triplets = _coefficient_triplets(coefficients, wc_triplets)
    dsigma = differential_cross_section_conus_ge73(
        enu,
        float(T_keVnr),
        spec,
        model=cross_section_model,
        kinematics=kinematics,
        wc_triplets=triplets,
        left_wcs=dict(left_wcs or {}),
        include_sm=include_sm,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
    )
    integrand = np.asarray(flux(enu), dtype=float) * np.asarray(dsigma, dtype=float)
    return float(_trapz(integrand, enu))


def true_recoil_spectrum_grid(
    experiment_spec: Any | None = None,
    *,
    coefficients: Mapping[Triplet, complex] | None = None,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "quark_mass_resolved",
    settings: SlowIntegrationSettings | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    grid = true_recoil_grid_keVnr(settings)
    values = np.asarray(
        [
            true_recoil_spectrum_per_nucleus_s_keV(
                float(T),
                experiment_spec,
                coefficients=coefficients,
                wc_triplets=wc_triplets,
                left_wcs=left_wcs,
                include_sm=include_sm,
                cross_section_model=cross_section_model,
                kinematics=kinematics,
                sin2thetaW=sin2thetaW,
                c10_mass_mode=c10_mass_mode,
                settings=settings,
            )
            for T in grid
        ],
        dtype=float,
    )
    return grid, values


def reco_evaluation_grid_evee(experiment_spec: Any | None = None, settings: SlowIntegrationSettings | None = None) -> np.ndarray:
    spec = _resolve_spec(experiment_spec)
    cfg = SlowIntegrationSettings() if settings is None else settings
    if float(cfg.reco_step_evee) <= 0.0:
        raise ValueError("reco_step_evee must be positive")
    edges = reco_energy_bin_edges_evee(spec)
    step = float(cfg.reco_step_evee)
    count = int(round((float(edges[-1]) - float(edges[0])) / step))
    grid = float(edges[0]) + step * np.arange(count + 1, dtype=float)
    if not np.isclose(grid[-1], edges[-1]):
        grid = np.r_[grid[grid < edges[-1]], float(edges[-1])]
    return np.unique(np.r_[grid, edges])


def reconstructed_spectrum_grid(
    experiment_spec: Any | None = None,
    *,
    coefficients: Mapping[Triplet, complex] | None = None,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "quark_mass_resolved",
    settings: SlowIntegrationSettings | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    spec = _resolve_spec(experiment_spec)
    T_grid, spectrum_per_nucleus = true_recoil_spectrum_grid(
        spec,
        coefficients=coefficients,
        wc_triplets=wc_triplets,
        left_wcs=left_wcs,
        include_sm=include_sm,
        cross_section_model=cross_section_model,
        kinematics=kinematics,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
        settings=settings,
    )
    dndT = target_time_normalization(spec) * spectrum_per_nucleus
    reco_grid = reco_evaluation_grid_evee(spec, settings)
    response = np.asarray(conus_ge73_response_density(reco_grid[:, None], T_grid[None, :], spec), dtype=float)
    folded = np.asarray([_trapz(dndT * response_row, T_grid) for response_row in response], dtype=float)
    dndE = np.asarray(conus_ge73_efficiency(reco_grid, spec), dtype=float) * folded
    return reco_grid, dndE, T_grid, dndT


def bin_counts_from_reconstructed_grid(
    reco_grid_evee: np.ndarray,
    dndE_per_evee: np.ndarray,
    experiment_spec: Any | None = None,
) -> np.ndarray:
    spec = _resolve_spec(experiment_spec)
    edges = reco_energy_bin_edges_evee(spec)
    counts = np.zeros(edges.size - 1, dtype=float)
    for i, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (reco_grid_evee > left) & (reco_grid_evee < right)
        xs = np.r_[left, reco_grid_evee[mask], right]
        ys = np.interp(xs, reco_grid_evee, dndE_per_evee, left=0.0, right=0.0)
        counts[i] = float(_trapz(ys, xs))
    return counts


def slow_counts_conus_plus_ge73_pheno(
    coefficients: Mapping[Triplet, complex] | None = None,
    experiment_spec: Any | None = None,
    *,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "quark_mass_resolved",
    return_components: bool = False,
    integration_settings: SlowIntegrationSettings | None = None,
) -> dict[str, Any]:
    if experiment_spec is None and coefficients is not None:
        maybe_spec = coefficients
        maybe_data = getattr(maybe_spec, "data", None)
        if isinstance(maybe_data, dict) or (isinstance(maybe_spec, dict) and "dataset_name" in maybe_spec):
            experiment_spec = maybe_spec
            coefficients = None
    spec = _resolve_spec(experiment_spec)
    reco_grid, dndE, T_grid, dndT = reconstructed_spectrum_grid(
        spec,
        coefficients=coefficients,
        wc_triplets=wc_triplets,
        left_wcs=left_wcs,
        include_sm=include_sm,
        cross_section_model=cross_section_model,
        kinematics=kinematics,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
        settings=integration_settings,
    )
    edges = reco_energy_bin_edges_evee(spec)
    counts = bin_counts_from_reconstructed_grid(reco_grid, dndE, spec)
    widths = np.diff(edges)
    out: dict[str, Any] = {
        "counts_total": counts.copy(),
        "counts_per_bin": {"total": counts.copy(), "nuebar_Ge73": counts.copy()},
        "counts_per_evee": {"total": counts / widths, "nuebar_Ge73": counts / widths},
        "reco_energy_bins_evee": edges.copy(),
        "dataset": DATASET_ID,
        "unit": "expected_events_per_bin",
        "axes": ("reco_energy_evee",),
        "model": {
            "cross_section_model": cross_section_model,
            "kinematics": kinematics,
            "include_sm": bool(include_sm),
        },
        "normalization": {
            "nuclei_per_kg": nuclei_per_kg_ge73(spec),
            "exposure_kg_day": float(_spec_data(spec).get("detector", {}).get("exposure_kg_day", 119.0)),
            "target_seconds": target_time_normalization(spec),
        },
    }
    if return_components:
        out["reco_energy_grid_evee"] = reco_grid.copy()
        out["dndE_reco_per_evee"] = dndE.copy()
        out["true_recoil_grid_keVnr"] = T_grid.copy()
        out["dndT_true_per_keVnr"] = dndT.copy()
    return out


__all__ = [
    "AVOGADRO_MOL_INV",
    "DATASET_ID",
    "SlowIntegrationSettings",
    "bin_counts_from_reconstructed_grid",
    "nuclei_per_kg_ge73",
    "neutrino_grid_for_recoil",
    "reco_evaluation_grid_evee",
    "reconstructed_spectrum_grid",
    "slow_counts_conus_plus_ge73_pheno",
    "target_time_normalization",
    "true_recoil_grid_keVnr",
    "true_recoil_spectrum_grid",
    "true_recoil_spectrum_per_nucleus_s_keV",
]
