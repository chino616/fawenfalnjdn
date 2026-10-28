"""CONUS+ Ge detector response for the approved hybrid candidate dataset.

The candidate uses a full-domain Gaussian density in reconstructed ionization
energy. Efficiency is an exact detector-specific step evaluated on the
reconstructed energy; probability migrating outside the analysis window is
not renormalized back into the window.
"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Mapping, Union

import numpy as np


ArrayLike = Union[float, int, np.ndarray]

from .definition import DEFINITION
DEFAULT_SETTINGS = DEFINITION.physical.detector
GERMANIUM_Z = DEFAULT_SETTINGS.germanium_z
LINDHARD_K = DEFAULT_SETTINGS.lindhard_k
SIGMA0_EVEE = DEFAULT_SETTINGS.sigma0_evee
FANO_FACTOR = DEFAULT_SETTINGS.fano_factor
PAIR_CREATION_ENERGY_EV = DEFAULT_SETTINGS.pair_creation_energy_ev
DETECTOR_ORDER = DEFINITION.observation.detector_ids
DETECTOR_THRESHOLDS_EVEE = MappingProxyType(dict(DEFAULT_SETTINGS.thresholds_evee))
BIN_EDGES_EVEE = np.asarray(DEFINITION.observation.edges)
BIN_EDGES_EVEE.setflags(write=False)


def _scalar_or_array(value: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(value))
    return value


def _finite_nonnegative(value: ArrayLike, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if np.any(~np.isfinite(array)) or np.any(array < 0.0):
        raise ValueError(f"{name} must be finite and non-negative")
    return array


def lindhard_epsilon(recoil_kev: ArrayLike, *, settings=DEFAULT_SETTINGS):
    recoil = _finite_nonnegative(recoil_kev, name="recoil_kev")
    value = 11.5 * settings.germanium_z ** (-7.0 / 3.0) * recoil
    return _scalar_or_array(value, recoil_kev)


def lindhard_g(epsilon: ArrayLike):
    eps = _finite_nonnegative(epsilon, name="epsilon")
    value = 3.0 * eps**0.15 + 0.7 * eps**0.6 + eps
    return _scalar_or_array(value, epsilon)


def quenching_factor(recoil_kev: ArrayLike, *, settings=DEFAULT_SETTINGS):
    epsilon = np.asarray(lindhard_epsilon(recoil_kev, settings=settings), dtype=float)
    g_value = np.asarray(lindhard_g(epsilon), dtype=float)
    value = settings.lindhard_k * g_value / (1.0 + settings.lindhard_k * g_value)
    return _scalar_or_array(value, recoil_kev)


def mean_reconstructed_energy_evee(recoil_kev: ArrayLike, *, settings=DEFAULT_SETTINGS):
    recoil = _finite_nonnegative(recoil_kev, name="recoil_kev")
    value = 1000.0 * np.asarray(quenching_factor(recoil, settings=settings), dtype=float) * recoil
    return _scalar_or_array(value, recoil_kev)


def resolution_sigma_evee(mean_evee: ArrayLike, *, settings=DEFAULT_SETTINGS):
    mean = _finite_nonnegative(mean_evee, name="mean_evee")
    value = np.sqrt(
        settings.sigma0_evee**2 + settings.fano_factor * settings.pair_creation_energy_ev * mean
    )
    return _scalar_or_array(value, mean_evee)


def response_density_evee(reco_evee: ArrayLike, recoil_kev: ArrayLike, *, settings=DEFAULT_SETTINGS):
    reco = np.asarray(reco_evee, dtype=float)
    if np.any(~np.isfinite(reco)):
        raise ValueError("reco_evee must be finite")
    mean = np.asarray(mean_reconstructed_energy_evee(recoil_kev, settings=settings), dtype=float)
    sigma = np.asarray(resolution_sigma_evee(mean, settings=settings), dtype=float)
    z = (reco - mean) / sigma
    density = np.exp(-0.5 * z * z) / (math.sqrt(2.0 * math.pi) * sigma)
    if np.isscalar(reco_evee) and np.isscalar(recoil_kev):
        return float(np.asarray(density))
    return density


def _normal_cdf(z: np.ndarray) -> np.ndarray:
    array = np.asarray(z, dtype=float)
    flat = np.fromiter(
        (
            0.5 * (1.0 + math.erf(float(value) / math.sqrt(2.0)))
            for value in array.flat
        ),
        dtype=float,
        count=array.size,
    )
    return flat.reshape(array.shape)


def response_interval_probability_evee(
    recoil_kev: ArrayLike,
    lower_evee: float,
    upper_evee: float,
    *, settings=DEFAULT_SETTINGS,
):
    lower = float(lower_evee)
    upper = float(upper_evee)
    if not math.isfinite(lower) or not math.isfinite(upper) or upper < lower:
        raise ValueError("response interval must have finite upper >= lower")
    mean = np.asarray(mean_reconstructed_energy_evee(recoil_kev, settings=settings), dtype=float)
    sigma = np.asarray(resolution_sigma_evee(mean, settings=settings), dtype=float)
    probability = _normal_cdf((upper - mean) / sigma) - _normal_cdf(
        (lower - mean) / sigma
    )
    probability = np.clip(probability, 0.0, 1.0)
    return _scalar_or_array(probability, recoil_kev)


def efficiency_reconstructed(reco_evee: ArrayLike, detector: str, *, settings=DEFAULT_SETTINGS):
    try:
        threshold = dict(settings.thresholds_evee)[detector]
    except KeyError as exc:
        raise KeyError(f"unknown CONUS+ detector: {detector!r}") from exc
    reco = np.asarray(reco_evee, dtype=float)
    if np.any(~np.isfinite(reco)):
        raise ValueError("reco_evee must be finite")
    value = (reco >= threshold).astype(float)
    return _scalar_or_array(value, reco_evee)


def detector_bin_acceptance(
    recoil_kev: ArrayLike,
    detector: str,
    *,
    edges_evee: np.ndarray = BIN_EDGES_EVEE,
    settings=DEFAULT_SETTINGS,
) -> np.ndarray:
    try:
        threshold = dict(settings.thresholds_evee)[detector]
    except KeyError as exc:
        raise KeyError(f"unknown CONUS+ detector: {detector!r}") from exc
    edges = np.asarray(edges_evee, dtype=float)
    if edges.ndim != 1 or edges.size < 2 or np.any(~np.isfinite(edges)):
        raise ValueError("edges_evee must be a finite one-dimensional edge array")
    if np.any(np.diff(edges) <= 0.0):
        raise ValueError("edges_evee must be strictly increasing")

    recoil = _finite_nonnegative(recoil_kev, name="recoil_kev")
    mean = np.asarray(mean_reconstructed_energy_evee(recoil, settings=settings), dtype=float)[..., None]
    sigma = np.asarray(resolution_sigma_evee(mean, settings=settings), dtype=float)
    lower = np.maximum(edges[:-1], threshold)
    upper = edges[1:]
    probability = _normal_cdf((upper - mean) / sigma) - _normal_cdf(
        (lower - mean) / sigma
    )
    probability = np.where(upper > lower, probability, 0.0)
    return np.clip(probability, 0.0, 1.0)


def response_contract(*, settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE) -> dict:
    return {
        "true_variable": "nuclear_recoil_energy",
        "true_unit": "keVnr",
        "reconstructed_variable": "ionization_energy",
        "reconstructed_unit": "eVee",
        "quenching_model": "Lindhard",
        "lindhard_k": settings.lindhard_k,
        "resolution_model": "full_real_line_Gaussian",
        "sigma0_evee": settings.sigma0_evee,
        "fano_factor": settings.fano_factor,
        "pair_creation_energy_ev": settings.pair_creation_energy_ev,
        "efficiency_model": "detector_specific_exact_reconstructed_energy_step",
        "thresholds_evee": dict(settings.thresholds_evee),
        "analysis_edges_evee": np.asarray(edges_evee).tolist(),
        "analysis_window_renormalization": False,
    }


__all__ = [
    "BIN_EDGES_EVEE",
    "DETECTOR_ORDER",
    "DETECTOR_THRESHOLDS_EVEE",
    "FANO_FACTOR",
    "GERMANIUM_Z",
    "LINDHARD_K",
    "PAIR_CREATION_ENERGY_EV",
    "SIGMA0_EVEE",
    "detector_bin_acceptance",
    "efficiency_reconstructed",
    "lindhard_epsilon",
    "lindhard_g",
    "mean_reconstructed_energy_evee",
    "quenching_factor",
    "resolution_sigma_evee",
    "response_contract",
    "response_density_evee",
    "response_interval_probability_evee",
]
