from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class StatisticalObservable:
    name: str
    unit: str
    bin_edges: np.ndarray

    @property
    def bin_widths(self) -> np.ndarray:
        return np.diff(np.asarray(self.bin_edges, dtype=float))


@dataclass(frozen=True)
class PredictionVector:
    values: np.ndarray
    observable: StatisticalObservable
    metadata: Mapping[str, object] | None = None


def _as_1d(values: object, *, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} is empty")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def observable(
    name: str,
    unit: str,
    bin_edges: object,
) -> StatisticalObservable:
    edges = _as_1d(bin_edges, name="bin_edges")
    if edges.size < 2:
        raise ValueError("bin_edges must contain at least two edges")
    if np.any(np.diff(edges) <= 0.0):
        raise ValueError("bin_edges must be strictly increasing")
    return StatisticalObservable(name=str(name), unit=str(unit), bin_edges=edges)


def prediction_vector(
    values: object,
    stat_observable: StatisticalObservable,
    *,
    metadata: Mapping[str, object] | None = None,
) -> PredictionVector:
    arr = _as_1d(values, name="prediction")
    if arr.size != stat_observable.bin_edges.size - 1:
        raise ValueError(
            "prediction/bin mismatch: "
            f"prediction={arr.size}, bins={stat_observable.bin_edges.size - 1}"
        )
    return PredictionVector(values=arr, observable=stat_observable, metadata=metadata)


def observables_compatible(
    left: StatisticalObservable,
    right: StatisticalObservable,
    *,
    atol: float = 1.0e-12,
) -> bool:
    return (
        left.name == right.name
        and left.unit == right.unit
        and left.bin_edges.shape == right.bin_edges.shape
        and bool(np.allclose(left.bin_edges, right.bin_edges, rtol=0.0, atol=atol))
    )


def validate_prediction_for_observable(
    prediction: PredictionVector,
    expected: StatisticalObservable,
    *,
    atol: float = 1.0e-12,
) -> np.ndarray:
    if not observables_compatible(prediction.observable, expected, atol=atol):
        raise ValueError(
            "prediction observable mismatch: "
            f"got {prediction.observable.name!r}/{prediction.observable.unit!r}, "
            f"expected {expected.name!r}/{expected.unit!r}"
        )
    values = _as_1d(prediction.values, name="prediction")
    if values.size != expected.bin_edges.size - 1:
        raise ValueError(
            f"prediction shape {values.shape} does not match {expected.bin_edges.size - 1} bins"
        )
    return values


def convert_prediction_to_dataset_observable(
    prediction: PredictionVector,
    target: StatisticalObservable,
) -> PredictionVector:
    source = prediction.observable
    values = _as_1d(prediction.values, name="prediction")
    if source.bin_edges.shape != target.bin_edges.shape or not np.allclose(
        source.bin_edges,
        target.bin_edges,
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError("prediction and dataset bin edges are incompatible")

    if source.name == target.name and source.unit == target.unit:
        converted = values
    elif source.unit == "events/bin" and target.unit in {"counts/PE", "counts/bin-width"}:
        converted = values / target.bin_widths
    elif source.unit == "events/bin" and target.unit == "counts/bin":
        converted = values
    else:
        raise ValueError(
            f"unsupported observable conversion: {source.unit!r} -> {target.unit!r}"
        )

    return PredictionVector(
        values=np.asarray(converted, dtype=float),
        observable=target,
        metadata={**dict(prediction.metadata or {}), "converted_from_unit": source.unit},
    )


__all__ = [
    "PredictionVector",
    "StatisticalObservable",
    "convert_prediction_to_dataset_observable",
    "observable",
    "observables_compatible",
    "prediction_vector",
    "validate_prediction_for_observable",
]
