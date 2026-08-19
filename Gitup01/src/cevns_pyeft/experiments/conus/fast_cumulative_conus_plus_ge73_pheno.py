from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from cevns_pyeft.experiments.conus.detector_response import reco_energy_bin_edges_evee
from cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno import (
    DATASET_ID,
    SlowIntegrationSettings,
    slow_counts_conus_plus_ge73_pheno,
)
from cevns_pyeft.experiments.registry import get_experiment_spec

Triplet = tuple[int, int, str]

CUMULATIVE_FAST_MODEL = "conus_plus_ge73_pheno_cumulative_spectrum_v1"
DEFAULT_GRID_STEP_EVEE = 2.0
DEFAULT_N_FIT = 3
DEFAULT_N_CUMULATIVE = 2
DEFAULT_F_FLOOR = 1.0e-300


@dataclass(frozen=True)
class CumulativeFastSettings:
    grid_step_evee: float = DEFAULT_GRID_STEP_EVEE
    n_fit: int = DEFAULT_N_FIT
    n_cumulative: int = DEFAULT_N_CUMULATIVE
    f_floor: float = DEFAULT_F_FLOOR


@dataclass(frozen=True)
class CumulativeFastRepresentation:
    reco_energy_grid_evee: np.ndarray
    dndE_reco_per_evee: np.ndarray
    cumulative_counts: np.ndarray
    metadata: dict[str, Any]


def _spec_data(experiment_spec: Any) -> dict[str, Any]:
    data = getattr(experiment_spec, "data", None)
    if isinstance(data, dict):
        return data
    if isinstance(experiment_spec, dict):
        return experiment_spec
    return {}


def _resolve_spec(experiment_spec: Any | None) -> Any:
    return get_experiment_spec(DATASET_ID) if experiment_spec is None else experiment_spec


def _cumulative_trapezoid(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("x and y must be one-dimensional arrays with the same length")
    if x.size < 2:
        raise ValueError("cumulative grid must contain at least two points")
    if np.any(np.diff(x) <= 0.0):
        raise ValueError("cumulative grid must be strictly increasing")
    increments = 0.5 * (y[:-1] + y[1:]) * np.diff(x)
    return np.r_[0.0, np.cumsum(increments)]


def _resample_spectrum(
    reco_energy_grid_evee: np.ndarray,
    dndE_reco_per_evee: np.ndarray,
    bin_edges_evee: np.ndarray,
    settings: CumulativeFastSettings,
) -> tuple[np.ndarray, np.ndarray]:
    source_x = np.asarray(reco_energy_grid_evee, dtype=float)
    source_y = np.asarray(dndE_reco_per_evee, dtype=float)
    edges = np.asarray(bin_edges_evee, dtype=float)
    if source_x.ndim != 1 or source_y.ndim != 1 or source_x.size != source_y.size:
        raise ValueError("input spectrum grid and values must be one-dimensional arrays with matching length")
    if np.any(np.diff(source_x) <= 0.0):
        raise ValueError("input spectrum grid must be strictly increasing")
    if float(settings.grid_step_evee) <= 0.0:
        raise ValueError("grid_step_evee must be positive")

    step = float(settings.grid_step_evee)
    n_steps = int(round((float(edges[-1]) - float(edges[0])) / step))
    target_x = float(edges[0]) + step * np.arange(n_steps + 1, dtype=float)
    if not np.isclose(target_x[-1], edges[-1]):
        target_x = np.r_[target_x[target_x < edges[-1]], float(edges[-1])]
    target_x = np.unique(np.r_[target_x, edges])
    if np.all(source_y > 0.0):
        log_y = np.log(np.maximum(source_y, float(settings.f_floor)))
        target_y = np.exp(np.interp(target_x, source_x, log_y))
    else:
        target_y = np.interp(target_x, source_x, source_y, left=0.0, right=0.0)
    target_y = np.where(target_y > 0.0, target_y, 0.0)
    return target_x, target_y


def build_cumulative_fast_representation(
    slow_spectrum_callable: Callable[..., Mapping[str, Any]] = slow_counts_conus_plus_ge73_pheno,
    experiment_spec: Any | None = None,
    *,
    coefficients: Mapping[Triplet, complex] | None = None,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "flavor",
    slow_integration_settings: SlowIntegrationSettings | None = None,
    fast_settings: CumulativeFastSettings | None = None,
) -> CumulativeFastRepresentation:
    spec = _resolve_spec(experiment_spec)
    settings = CumulativeFastSettings() if fast_settings is None else fast_settings
    slow_settings = slow_integration_settings or SlowIntegrationSettings(reco_step_evee=float(settings.grid_step_evee))
    payload = slow_spectrum_callable(
        coefficients=coefficients,
        experiment_spec=spec,
        wc_triplets=wc_triplets,
        left_wcs=left_wcs,
        include_sm=include_sm,
        cross_section_model=cross_section_model,
        kinematics=kinematics,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
        return_components=True,
        integration_settings=slow_settings,
    )
    edges = reco_energy_bin_edges_evee(spec)
    grid, spectrum = _resample_spectrum(
        np.asarray(payload["reco_energy_grid_evee"], dtype=float),
        np.asarray(payload["dndE_reco_per_evee"], dtype=float),
        edges,
        settings,
    )
    cumulative = _cumulative_trapezoid(spectrum, grid)
    metadata = {
        "model": CUMULATIVE_FAST_MODEL,
        "dataset_id": DATASET_ID,
        "axis": "reco_energy_evee",
        "unit": "expected_events_per_bin",
        "bin_edges_evee": edges.tolist(),
        "fast_settings": asdict(settings),
        "slow_integration_settings": asdict(slow_settings),
        "cross_section_model": str(cross_section_model),
        "kinematics": str(kinematics),
        "include_sm": bool(include_sm),
        "coefficient_dependent": True,
        "representation_scope": "fixed reconstructed spectrum for the supplied coefficient point",
        "eft_template_status": "BLOCKED_UNTIL_COMPLETE_20_GROUP_BASIS_DEFINED",
    }
    return CumulativeFastRepresentation(
        reco_energy_grid_evee=grid,
        dndE_reco_per_evee=spectrum,
        cumulative_counts=cumulative,
        metadata=metadata,
    )


def reconstruct_counts_from_cumulative(
    representation: CumulativeFastRepresentation,
    bin_edges_evee: np.ndarray | None = None,
) -> np.ndarray:
    metadata = dict(representation.metadata)
    edges = np.asarray(bin_edges_evee if bin_edges_evee is not None else metadata["bin_edges_evee"], dtype=float)
    if np.any(np.diff(edges) <= 0.0):
        raise ValueError("bin edges must be strictly increasing")
    grid = np.asarray(representation.reco_energy_grid_evee, dtype=float)
    cumulative = np.asarray(representation.cumulative_counts, dtype=float)
    values = np.interp(edges, grid, cumulative)
    return np.diff(values)


def cumulative_fast_counts_conus_plus_ge73_pheno(
    slow_spectrum_callable: Callable[..., Mapping[str, Any]] = slow_counts_conus_plus_ge73_pheno,
    experiment_spec: Any | None = None,
    *,
    coefficients: Mapping[Triplet, complex] | None = None,
    wc_triplets: Mapping[Triplet, complex] | None = None,
    left_wcs: Mapping[str, complex] | None = None,
    include_sm: bool = True,
    cross_section_model: str = "full_response",
    kinematics: str = "publication_reproduction",
    sin2thetaW: float = 0.23873,
    c10_mass_mode: str = "flavor",
    slow_integration_settings: SlowIntegrationSettings | None = None,
    fast_settings: CumulativeFastSettings | None = None,
    return_representation: bool = False,
) -> dict[str, Any]:
    spec = _resolve_spec(experiment_spec)
    t0 = time.perf_counter()
    representation = build_cumulative_fast_representation(
        slow_spectrum_callable=slow_spectrum_callable,
        experiment_spec=spec,
        coefficients=coefficients,
        wc_triplets=wc_triplets,
        left_wcs=left_wcs,
        include_sm=include_sm,
        cross_section_model=cross_section_model,
        kinematics=kinematics,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
        slow_integration_settings=slow_integration_settings,
        fast_settings=fast_settings,
    )
    counts = reconstruct_counts_from_cumulative(representation, reco_energy_bin_edges_evee(spec))
    runtime = time.perf_counter() - t0
    out: dict[str, Any] = {
        "counts_total": counts.copy(),
        "counts_per_bin": {"total": counts.copy(), "nuebar_Ge73": counts.copy()},
        "reco_energy_bins_evee": reco_energy_bin_edges_evee(spec),
        "axes": ("reco_energy_evee",),
        "unit": "expected_events_per_bin",
        "dataset": DATASET_ID,
        "representation": "cumulative",
        "metadata": dict(representation.metadata),
        "runtime_s": runtime,
    }
    if return_representation:
        out["representation_payload"] = representation
    return out


def validate_cumulative_fast_representation(
    representation: CumulativeFastRepresentation,
    experiment_spec: Any | None = None,
) -> None:
    spec = _resolve_spec(experiment_spec)
    metadata = dict(representation.metadata)
    if metadata.get("model") != CUMULATIVE_FAST_MODEL:
        raise ValueError(f"Unsupported cumulative Fast model: {metadata.get('model')!r}")
    if metadata.get("dataset_id") != DATASET_ID:
        raise ValueError(f"Unsupported dataset_id: {metadata.get('dataset_id')!r}")
    expected_edges = reco_energy_bin_edges_evee(spec)
    stored_edges = np.asarray(metadata.get("bin_edges_evee"), dtype=float)
    if stored_edges.shape != expected_edges.shape or not np.allclose(stored_edges, expected_edges):
        raise ValueError("Stored bin edges do not match the experiment spec")
    grid = np.asarray(representation.reco_energy_grid_evee, dtype=float)
    cumulative = np.asarray(representation.cumulative_counts, dtype=float)
    if grid.ndim != 1 or cumulative.ndim != 1 or grid.size != cumulative.size:
        raise ValueError("Cumulative representation arrays must be one-dimensional with matching length")
    if np.any(np.diff(grid) <= 0.0):
        raise ValueError("Cumulative grid must be strictly increasing")
    if np.any(np.diff(cumulative) < -1.0e-10):
        raise ValueError("Cumulative counts must be monotonic nondecreasing")


def save_cumulative_fast_representation(path: str | Path, representation: CumulativeFastRepresentation) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        reco_energy_grid_evee=np.asarray(representation.reco_energy_grid_evee, dtype=float),
        dndE_reco_per_evee=np.asarray(representation.dndE_reco_per_evee, dtype=float),
        cumulative_counts=np.asarray(representation.cumulative_counts, dtype=float),
    )
    out.with_suffix(".json").write_text(json.dumps(representation.metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def load_cumulative_fast_representation(path: str | Path, experiment_spec: Any | None = None) -> CumulativeFastRepresentation:
    npz_path = Path(path)
    json_path = npz_path.with_suffix(".json")
    if not npz_path.exists():
        raise FileNotFoundError(npz_path)
    if not json_path.exists():
        raise FileNotFoundError(json_path)
    with np.load(npz_path, allow_pickle=False) as arrays:
        representation = CumulativeFastRepresentation(
            reco_energy_grid_evee=np.asarray(arrays["reco_energy_grid_evee"], dtype=float),
            dndE_reco_per_evee=np.asarray(arrays["dndE_reco_per_evee"], dtype=float),
            cumulative_counts=np.asarray(arrays["cumulative_counts"], dtype=float),
            metadata=json.loads(json_path.read_text(encoding="utf-8")),
        )
    validate_cumulative_fast_representation(representation, experiment_spec)
    return representation


__all__ = [
    "CUMULATIVE_FAST_MODEL",
    "CumulativeFastRepresentation",
    "CumulativeFastSettings",
    "build_cumulative_fast_representation",
    "cumulative_fast_counts_conus_plus_ge73_pheno",
    "load_cumulative_fast_representation",
    "reconstruct_counts_from_cumulative",
    "save_cumulative_fast_representation",
    "validate_cumulative_fast_representation",
]
