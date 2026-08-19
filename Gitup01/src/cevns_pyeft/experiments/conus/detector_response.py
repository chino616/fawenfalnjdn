from __future__ import annotations

import math
from typing import Any

import numpy as np

ArrayLike = float | int | np.ndarray

GE_Z = 32
LINDHARD_K = 0.162
RESOLUTION_SIGMA0_EVEE = 20.38
RESOLUTION_FANO = 0.1096
RESOLUTION_ETA_EV = 2.96
EFFICIENCY_THRESHOLD_EVEE = 160.0
RECO_BIN_MIN_EVEE = 160.0
RECO_BIN_MAX_EVEE = 350.0
RECO_BIN_WIDTH_EVEE = 10.0
RECO_BIN_COUNT = 19


def _asarray(x: ArrayLike) -> np.ndarray:
    return np.atleast_1d(np.asarray(x, dtype=float))


def _scalar_or_array(values: np.ndarray, *likes: ArrayLike):
    if all(np.isscalar(like) for like in likes):
        return float(np.asarray(values).reshape(-1)[0])
    return values


def _spec_data(experiment_spec: Any | None) -> dict[str, Any]:
    if experiment_spec is None:
        return {}
    data = getattr(experiment_spec, "data", None)
    if isinstance(data, dict):
        return data
    if isinstance(experiment_spec, dict):
        return experiment_spec
    return {}


def _detector_response_config(experiment_spec: Any | None) -> dict[str, Any]:
    data = _spec_data(experiment_spec)
    config = data.get("detector_response", {})
    return config if isinstance(config, dict) else {}


def _param(experiment_spec: Any | None, key: str, default: float) -> float:
    value = _detector_response_config(experiment_spec).get(key, default)
    return float(value)


def lindhard_quenching_ge(
    T_keVnr: ArrayLike,
    experiment_spec: Any | None = None,
    *,
    Z: int | None = None,
    k: float | None = None,
) -> ArrayLike:
    z_value = int(Z if Z is not None else _param(experiment_spec, "Z", GE_Z))
    k_value = float(k if k is not None else _param(experiment_spec, "lindhard_k", LINDHARD_K))
    recoil = np.maximum(_asarray(T_keVnr), 0.0)
    epsilon_l = 11.5 * float(z_value) ** (-7.0 / 3.0) * recoil
    g = 3.0 * epsilon_l**0.15 + 0.7 * epsilon_l**0.6 + epsilon_l
    q = k_value * g / (1.0 + k_value * g)
    return float(q[0]) if np.isscalar(T_keVnr) else q


def mean_reconstructed_energy_evee(T_keVnr: ArrayLike, experiment_spec: Any | None = None) -> ArrayLike:
    recoil = np.maximum(_asarray(T_keVnr), 0.0)
    mean = 1000.0 * np.asarray(lindhard_quenching_ge(recoil, experiment_spec), dtype=float) * recoil
    return float(mean[0]) if np.isscalar(T_keVnr) else mean


def resolution_width_evee(mean_evee: ArrayLike, experiment_spec: Any | None = None) -> ArrayLike:
    sigma0 = _param(experiment_spec, "resolution_sigma0_evee", RESOLUTION_SIGMA0_EVEE)
    fano = _param(experiment_spec, "resolution_fano", RESOLUTION_FANO)
    eta = _param(experiment_spec, "resolution_eta_ev", RESOLUTION_ETA_EV)
    visible = np.maximum(_asarray(mean_evee), 0.0)
    sigma = np.sqrt(sigma0 * sigma0 + fano * eta * visible)
    return float(sigma[0]) if np.isscalar(mean_evee) else sigma


def conus_ge73_response_density(
    E_reco_eVee: ArrayLike,
    T_keVnr: ArrayLike,
    experiment_spec: Any | None = None,
) -> ArrayLike:
    reco, recoil = np.broadcast_arrays(_asarray(E_reco_eVee), _asarray(T_keVnr))
    mean = np.asarray(mean_reconstructed_energy_evee(recoil, experiment_spec), dtype=float)
    sigma = np.asarray(resolution_width_evee(mean, experiment_spec), dtype=float)
    z = (reco - mean) / sigma
    density = np.exp(-0.5 * z * z) / (sigma * math.sqrt(2.0 * math.pi))
    density = np.where(recoil >= 0.0, density, 0.0)
    return _scalar_or_array(density, E_reco_eVee, T_keVnr)


def conus_ge73_efficiency(E_reco_eVee: ArrayLike, experiment_spec: Any | None = None) -> ArrayLike:
    threshold = _param(experiment_spec, "efficiency_threshold_evee", EFFICIENCY_THRESHOLD_EVEE)
    reco = _asarray(E_reco_eVee)
    eff = np.where(reco >= threshold, 1.0, 0.0)
    return float(eff[0]) if np.isscalar(E_reco_eVee) else eff


def reco_energy_bin_edges_evee(experiment_spec: Any | None = None) -> np.ndarray:
    data = _spec_data(experiment_spec)
    binning = data.get("binning", {})
    if not isinstance(binning, dict):
        binning = {}
    minimum = float(binning.get("minimum_eVee", RECO_BIN_MIN_EVEE))
    maximum = float(binning.get("maximum_eVee", RECO_BIN_MAX_EVEE))
    number = int(binning.get("number_of_bins", RECO_BIN_COUNT))
    edges = np.linspace(minimum, maximum, number + 1, dtype=float)
    if edges.size != number + 1 or np.any(np.diff(edges) <= 0.0):
        raise ValueError("reconstructed-energy bin edges must be strictly increasing")
    return edges


__all__ = [
    "EFFICIENCY_THRESHOLD_EVEE",
    "GE_Z",
    "LINDHARD_K",
    "RECO_BIN_COUNT",
    "RECO_BIN_MAX_EVEE",
    "RECO_BIN_MIN_EVEE",
    "RECO_BIN_WIDTH_EVEE",
    "RESOLUTION_ETA_EV",
    "RESOLUTION_FANO",
    "RESOLUTION_SIGMA0_EVEE",
    "conus_ge73_efficiency",
    "conus_ge73_response_density",
    "lindhard_quenching_ge",
    "mean_reconstructed_energy_evee",
    "reco_energy_bin_edges_evee",
    "resolution_width_evee",
]
