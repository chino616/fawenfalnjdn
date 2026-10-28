"""CONUS+ detector-response-matrix Fast representation.

This cache accelerates only detector folding and recoil-bin integration. It
does not claim to be an EFT quadratic coefficient kernel: the true-recoil
rate is still evaluated by the P07 direct theory/source integration for each
parameter point.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

import numpy as np

from cevns_pyeft.experiments.conus_plus.detector_response import (
    BIN_EDGES_EVEE,
    DETECTOR_ORDER,
    DETECTOR_THRESHOLDS_EVEE,
    FANO_FACTOR,
    LINDHARD_K,
    PAIR_CREATION_ENERGY_EV,
    SIGMA0_EVEE,
    detector_bin_acceptance,
)
from cevns_pyeft.experiments.conus_plus.slow_counts import (
    COMPONENTS,
    DEFAULT_RESPONSE_JSON,
    EXPOSURES_KG_DAY,
    SIN2_THETA_W,
    true_recoil_rate_components_per_kg_day,
)
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.theory.kinematics import two_body_recoil_max_GeV


from .definition import DEFINITION
DEFAULT_SETTINGS = DEFINITION.physical
CACHE_SCHEMA_VERSION = 1
FAST_TYPE = "detector_response_matrix"
Triplet = Tuple[int, int, str]


class StaleConusResponseMatrixError(ValueError):
    """Raised when cache metadata no longer matches the active contract."""


def _coerce_exposures(
    exposures_kg_day: Optional[Mapping[str, float] | np.ndarray],
) -> np.ndarray:
    if exposures_kg_day is None:
        result = np.asarray(EXPOSURES_KG_DAY, dtype=float)
    elif isinstance(exposures_kg_day, Mapping):
        if set(exposures_kg_day) != set(DETECTOR_ORDER):
            raise ValueError(
                f"exposure mapping keys must be {DETECTOR_ORDER}"
            )
        result = np.asarray(
            [exposures_kg_day[key] for key in DETECTOR_ORDER],
            dtype=float,
        )
    else:
        result = np.asarray(exposures_kg_day, dtype=float)
    if result.shape != (len(DETECTOR_ORDER),):
        raise ValueError(
            "exposures_kg_day must have one value per detector"
        )
    if np.any(~np.isfinite(result)) or np.any(result < 0.0):
        raise ValueError(
            "exposures_kg_day must be finite and non-negative"
        )
    return result


def _recoil_quadrature(
    n_recoil: int,
    *, settings=DEFAULT_SETTINGS,
) -> tuple[np.ndarray, np.ndarray, float]:
    if int(n_recoil) != n_recoil or n_recoil < 2:
        raise ValueError("n_recoil must be an integer >= 2")
    mass_gev = settings.target_A * float(c.AMU_GEV)
    maximum_kev = float(
        two_body_recoil_max_GeV(settings.source.energy_support_mev[1] * c.MeV, mass_gev) / c.keV
    )
    nodes, weights = np.polynomial.legendre.leggauss(int(n_recoil))
    recoil = 0.5 * maximum_kev * (nodes + 1.0)
    recoil_weights = 0.5 * maximum_kev * weights
    return recoil, recoil_weights, maximum_kev


def _metadata_without_key(
    *,
    n_recoil: int,
    maximum_kev: float,
    exposures: np.ndarray,
    settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE,
) -> dict[str, Any]:
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "fast_type": FAST_TYPE,
        "dataset_id": "conus_plus_2025_c2c3c5_ge73_pyeft",
        "meaning": (
            "exposure[d] * recoil_weight[t] * "
            "P_d(reco_bin=b | T_t)"
        ),
        "axes": [
            "detector",
            "true_recoil_node",
            "reconstructed_energy_bin",
        ],
        "unit": "kg_day_keVnr",
        "detector_order": list(DETECTOR_ORDER),
        "component_order_for_reconstruction": list(COMPONENTS),
        "bin_edges_evee": np.asarray(edges_evee).tolist(),
        "exposures_kg_day": exposures.tolist(),
        "recoil_quadrature": {
            "kind": "Gauss-Legendre",
            "n_recoil": int(n_recoil),
            "support_kevnr": [0.0, float(maximum_kev)],
        },
        "detector_response_contract": {
            "lindhard_k": settings.detector.lindhard_k,
            **({"germanium_z":settings.detector.germanium_z} if settings.detector.germanium_z != DEFAULT_SETTINGS.detector.germanium_z else {}),
            "sigma0_evee": settings.detector.sigma0_evee,
            "fano_factor": settings.detector.fano_factor,
            "pair_creation_energy_ev": settings.detector.pair_creation_energy_ev,
            "thresholds_evee": dict(settings.detector.thresholds_evee),
            "gaussian_domain": "full_real_line",
            "analysis_window_renormalization": False,
            "efficiency_variable": "reconstructed_energy_evee",
        },
        "accelerates": [
            "detector response CDF evaluation",
            "true-recoil-to-bin contraction",
        ],
        "does_not_accelerate": [
            "reactor spectrum integration",
            "Li2026 amplitude",
            "dSigma/dT",
        ],
        "eft_quadratic_coefficient_kernel": "not_included",
    }


def _cache_key(metadata_without_key: Mapping[str, Any]) -> str:
    stable = json.dumps(
        metadata_without_key,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def build_detector_response_matrix(
    *,
    n_recoil: int = DEFINITION.numerical_profiles['fast']['n_recoil'],
    exposures_kg_day: Optional[Mapping[str, float] | np.ndarray] = None,
    settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE,
) -> dict[str, Any]:
    exposures = _coerce_exposures([e.kg_day for e in settings.exposures] if exposures_kg_day is None else exposures_kg_day)
    recoil, recoil_weights, maximum_kev = _recoil_quadrature(n_recoil, settings=settings)
    acceptance = np.stack(
        [
            detector_bin_acceptance(recoil, detector, settings=settings.detector, edges_evee=edges_evee)
            for detector in DETECTOR_ORDER
        ],
        axis=0,
    )
    weighted = (
        exposures[:, None, None]
        * recoil_weights[None, :, None]
        * acceptance
    )
    metadata = _metadata_without_key(
        n_recoil=int(n_recoil),
        maximum_kev=maximum_kev,
        exposures=exposures, settings=settings, edges_evee=edges_evee,
    )
    metadata["cache_key_sha256"] = _cache_key(metadata)
    cache = {
        "metadata": metadata,
        "recoil_nodes_kev": recoil,
        "recoil_weights_kev": recoil_weights,
        "exposures_kg_day": exposures,
        "bin_edges_evee": np.asarray(edges_evee).copy(),
        "weighted_folding_kg_day_kev": weighted,
    }
    validate_detector_response_matrix(cache, settings=settings, edges_evee=edges_evee)
    return cache


def validate_detector_response_matrix(cache: Mapping[str, Any], *, settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE) -> None:
    metadata = dict(cache.get("metadata", {}))
    if metadata.get("schema_version") != CACHE_SCHEMA_VERSION:
        raise StaleConusResponseMatrixError(
            "unsupported cache schema version"
        )
    if metadata.get("fast_type") != FAST_TYPE:
        raise StaleConusResponseMatrixError(
            "cache is not a detector_response_matrix"
        )

    recoil = np.asarray(cache["recoil_nodes_kev"], dtype=float)
    weights = np.asarray(cache["recoil_weights_kev"], dtype=float)
    exposures = np.asarray(cache["exposures_kg_day"], dtype=float)
    edges = np.asarray(cache["bin_edges_evee"], dtype=float)
    matrix = np.asarray(
        cache["weighted_folding_kg_day_kev"],
        dtype=float,
    )
    n_recoil = int(
        metadata.get("recoil_quadrature", {}).get("n_recoil", -1)
    )

    if recoil.shape != (n_recoil,) or weights.shape != (n_recoil,):
        raise ValueError("recoil nodes/weights do not match metadata")
    if exposures.shape != (len(DETECTOR_ORDER),):
        raise ValueError("exposure axis does not match detector order")
    expected_shape = (
        len(DETECTOR_ORDER),
        n_recoil,
        len(edges_evee) - 1,
    )
    if matrix.shape != expected_shape:
        raise ValueError("weighted folding matrix has the wrong shape")
    if not np.array_equal(edges, edges_evee):
        raise StaleConusResponseMatrixError(
            "analysis bin edges changed"
        )
    if np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0):
        raise ValueError(
            "weighted folding matrix must be finite and non-negative"
        )

    maximum_kev = float(
        metadata["recoil_quadrature"]["support_kevnr"][1]
    )
    expected_recoil, expected_weights, expected_max = _recoil_quadrature(n_recoil, settings=settings)
    if not np.array_equal(recoil, expected_recoil) or not np.array_equal(weights,expected_weights) or maximum_kev != expected_max:
        raise StaleConusResponseMatrixError('source support or recoil quadrature changed')
    current = _metadata_without_key(
        n_recoil=n_recoil,
        maximum_kev=maximum_kev,
        exposures=exposures, settings=settings, edges_evee=edges_evee,
    )
    if metadata.get("cache_key_sha256") != _cache_key(current):
        raise StaleConusResponseMatrixError(
            "cache metadata no longer matches the active response contract"
        )
    for key, value in current.items():
        if metadata.get(key) != value:
            raise StaleConusResponseMatrixError(
                f"cache metadata mismatch for {key}"
            )


def reconstruct_from_detector_response_matrix(
    cache: Mapping[str, Any],
    true_recoil_rate_components_per_kg_day_kev: np.ndarray,
    *, settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE,
) -> np.ndarray:
    """Contract rate[node,component] into events[detector,component,bin]."""

    validate_detector_response_matrix(cache, settings=settings, edges_evee=edges_evee)
    matrix = np.asarray(
        cache["weighted_folding_kg_day_kev"],
        dtype=float,
    )
    rate = np.asarray(
        true_recoil_rate_components_per_kg_day_kev
    )
    if rate.shape != (matrix.shape[1], len(COMPONENTS)):
        raise ValueError(
            "true recoil rate must have shape "
            "(true_recoil_node, reactor_component)"
        )
    if np.iscomplexobj(rate):
        imaginary = np.max(np.abs(rate.imag), initial=0.0)
        scale = max(
            1.0,
            float(np.max(np.abs(rate.real), initial=0.0)),
        )
        if imaginary > 1.0e-10 * scale:
            raise ValueError(
                "true recoil rate has a non-negligible imaginary part"
            )
        rate = rate.real
    rate = np.asarray(rate, dtype=float)
    if np.any(~np.isfinite(rate)) or np.any(rate < 0.0):
        raise ValueError(
            "true recoil rate must be finite and non-negative"
        )
    return np.einsum("dtb,tc->dcb", matrix, rate, optimize=True)


def fast_counts_conus_plus_response_matrix(
    cache: Mapping[str, Any],
    responses_json: str | Path = DEFAULT_RESPONSE_JSON,
    wc_triplets: Optional[Mapping[Triplet, object]] = None,
    *,
    include_sm: bool = True,
    sin2theta_w: float = SIN2_THETA_W,
    n_energy: int = DEFINITION.numerical_profiles['fast']['n_energy'],
    c10_mass_mode: str = DEFAULT_SETTINGS.c10_mass_mode,
    settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE, source_data_dir=None, model=None,
) -> dict[str, Any]:
    validate_detector_response_matrix(cache, settings=settings, edges_evee=edges_evee)
    recoil = np.asarray(cache["recoil_nodes_kev"], dtype=float)
    rate = true_recoil_rate_components_per_kg_day(
        recoil,
        responses_json,
        wc_triplets,
        include_sm=include_sm,
        sin2theta_w=sin2theta_w,
        n_energy=n_energy,
        c10_mass_mode=c10_mass_mode, settings=settings, source_data_dir=source_data_dir, model=model,
    )
    counts = reconstruct_from_detector_response_matrix(cache, rate, settings=settings, edges_evee=edges_evee)
    detector = np.sum(counts, axis=1)
    combined = np.sum(detector, axis=0)
    return {
        "counts_per_detector_component_bin": counts,
        "counts_per_detector_bin": detector,
        "combined_counts_per_bin": combined,
        "detector_totals": np.sum(detector, axis=1),
        "component_totals": np.sum(counts, axis=(0, 2)),
        "total_events": float(np.sum(combined)),
        "cache_key_sha256": cache["metadata"]["cache_key_sha256"],
        "fast_type": FAST_TYPE,
    }


def save_detector_response_matrix(
    path: str | Path,
    cache: Mapping[str, Any],
    *, settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE,
) -> tuple[Path, Path]:
    validate_detector_response_matrix(cache, settings=settings, edges_evee=edges_evee)
    npz_path = Path(path)
    if npz_path.suffix != ".npz":
        raise ValueError(
            "response-matrix cache path must end with .npz"
        )
    json_path = npz_path.with_suffix(".json")
    npz_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        npz_path,
        recoil_nodes_kev=np.asarray(
            cache["recoil_nodes_kev"],
            dtype=float,
        ),
        recoil_weights_kev=np.asarray(
            cache["recoil_weights_kev"],
            dtype=float,
        ),
        exposures_kg_day=np.asarray(
            cache["exposures_kg_day"],
            dtype=float,
        ),
        bin_edges_evee=np.asarray(
            cache["bin_edges_evee"],
            dtype=float,
        ),
        weighted_folding_kg_day_kev=np.asarray(
            cache["weighted_folding_kg_day_kev"],
            dtype=float,
        ),
    )
    json_path.write_text(
        json.dumps(
            cache["metadata"],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return npz_path, json_path


def load_detector_response_matrix(
    path: str | Path,
    *, settings=DEFAULT_SETTINGS, edges_evee=BIN_EDGES_EVEE,
) -> dict[str, Any]:
    npz_path = Path(path)
    json_path = npz_path.with_suffix(".json")
    metadata = json.loads(json_path.read_text(encoding="utf-8"))
    with np.load(npz_path, allow_pickle=False) as arrays:
        cache = {
            "metadata": metadata,
            "recoil_nodes_kev": np.asarray(
                arrays["recoil_nodes_kev"]
            ),
            "recoil_weights_kev": np.asarray(
                arrays["recoil_weights_kev"]
            ),
            "exposures_kg_day": np.asarray(
                arrays["exposures_kg_day"]
            ),
            "bin_edges_evee": np.asarray(arrays["bin_edges_evee"]),
            "weighted_folding_kg_day_kev": np.asarray(
                arrays["weighted_folding_kg_day_kev"]
            ),
        }
    validate_detector_response_matrix(cache, settings=settings, edges_evee=edges_evee)
    return cache


__all__ = [
    "CACHE_SCHEMA_VERSION",
    "FAST_TYPE",
    "StaleConusResponseMatrixError",
    "build_detector_response_matrix",
    "validate_detector_response_matrix",
    "reconstruct_from_detector_response_matrix",
    "fast_counts_conus_plus_response_matrix",
    "save_detector_response_matrix",
    "load_detector_response_matrix",
]
