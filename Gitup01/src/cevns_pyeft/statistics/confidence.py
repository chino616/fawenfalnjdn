from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import math
import numpy as np

try:
    from scipy.optimize import minimize_scalar, root_scalar
except Exception:  # pragma: no cover
    minimize_scalar = None
    root_scalar = None


@dataclass(frozen=True)
class ConfidenceDefinition:
    name: str
    confidence_level: float
    dof: int
    delta_chi2: float
    legacy_source: str


LEGACY_CONFIDENCE_DEFINITIONS: dict[str, ConfidenceDefinition] = {
    "legacy_1d_90": ConfidenceDefinition("legacy_1d_90", 0.90, 1, 2.71, "cutoff_single.py CL_TO_DCHI2_1DOF"),
    "legacy_1d_95": ConfidenceDefinition("legacy_1d_95", 0.95, 1, 3.84, "cutoff_single.py CL_TO_DCHI2_1DOF"),
    "legacy_1d_99": ConfidenceDefinition("legacy_1d_99", 0.99, 1, 6.63, "cutoff_single.py CL_TO_DCHI2_1DOF"),
    "legacy_2d_90_flow_a": ConfidenceDefinition("legacy_2d_90_flow_a", 0.90, 2, 4.61, "chi2_2d.py CL_TO_DCHI2_2DOF"),
    "legacy_2d_90_flow_b": ConfidenceDefinition("legacy_2d_90_flow_b", 0.90, 2, 4.61, "chi2_2d.py THRESHOLD_90CL"),
    "legacy_2d_90_rounded_api": ConfidenceDefinition("legacy_2d_90_rounded_api", 0.90, 2, 4.6, "chi2_2d.py COHERENT_2D_90CL_THRESHOLD default scan_eps_ud"),
}

CL_TO_DCHI2_1DOF: dict[float, float] = {0.90: 2.71, 0.95: 3.84, 0.99: 6.63}
CL_TO_DCHI2_2DOF: dict[float, float] = {0.683: 2.30, 0.90: 4.61, 0.95: 5.99, 0.99: 9.21}


def delta_chi2(values: object, *, minimum: float | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    min_value = float(np.nanmin(arr) if minimum is None else minimum)
    return arr - min_value


def _crossing_linear(x1: float, y1: float, x2: float, y2: float) -> float:
    if y2 == y1:
        return float(0.5 * (x1 + x2))
    return float(x1 + (0.0 - y1) * (x2 - x1) / (y2 - y1))


def _root_or_linear(func: Callable[[float], float], x1: float, x2: float) -> float:
    y1 = float(func(x1))
    y2 = float(func(x2))
    if abs(y1) < 1.0e-14:
        return float(x1)
    if abs(y2) < 1.0e-14:
        return float(x2)
    if y1 * y2 > 0.0 or root_scalar is None:
        return _crossing_linear(x1, y1, x2, y2)
    try:
        res = root_scalar(lambda x: float(func(float(x))), bracket=[float(x1), float(x2)], method="brentq")
        return float(res.root)
    except Exception:
        return _crossing_linear(x1, y1, x2, y2)


def extract_intervals(
    coeff_grid: object,
    dchi2_grid: object,
    threshold: float,
    *,
    root_func: Callable[[float], float] | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    x = np.asarray(coeff_grid, dtype=float).reshape(-1)
    y = np.asarray(dchi2_grid, dtype=float).reshape(-1) - float(threshold)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    order = np.argsort(x)
    x, y = x[order], y[order]
    inside = y <= 0.0
    intervals: list[dict[str, Any]] = []
    open_edge = False
    if x.size == 0 or not np.any(inside):
        return intervals, False
    groups = np.split(np.where(inside)[0], np.where(np.diff(np.where(inside)[0]) > 1)[0] + 1)
    for group in groups:
        left_i, right_i = int(group[0]), int(group[-1])
        if left_i == 0:
            left = float(x[0])
            closed_left = False
            open_edge = True
        else:
            left = _root_or_linear(root_func, float(x[left_i - 1]), float(x[left_i])) if root_func else _crossing_linear(float(x[left_i - 1]), float(y[left_i - 1]), float(x[left_i]), float(y[left_i]))
            closed_left = True
        if right_i == x.size - 1:
            right = float(x[-1])
            closed_right = False
            open_edge = True
        else:
            right = _root_or_linear(root_func, float(x[right_i]), float(x[right_i + 1])) if root_func else _crossing_linear(float(x[right_i]), float(y[right_i]), float(x[right_i + 1]), float(y[right_i + 1]))
            closed_right = True
        if np.isfinite(left) and np.isfinite(right) and right >= left:
            intervals.append({"left": float(left), "right": float(right), "closed_left": closed_left, "closed_right": closed_right})
    return intervals, bool(open_edge)


def refine_global_minimum(
    coeff_grid: object,
    chi2_grid: object,
    chi2_func: Callable[[float], float],
    *,
    scan_all_segments: bool = True,
) -> tuple[float, float, dict[str, Any]]:
    x = np.asarray(coeff_grid, dtype=float).reshape(-1)
    y = np.asarray(chi2_grid, dtype=float).reshape(-1)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    order = np.argsort(x)
    x, y = x[order], y[order]
    if x.size == 0:
        return math.nan, math.nan, {"status": "empty_grid"}
    candidates: list[tuple[float, float, str]] = [(float(xx), float(yy), "grid") for xx, yy in zip(x, y)]
    if minimize_scalar is not None and x.size >= 2:
        local = {0, int(x.size - 1)}
        for i in range(1, x.size - 1):
            if y[i] <= y[i - 1] and y[i] <= y[i + 1]:
                local.add(int(i))
        for i in sorted(local):
            if 0 < i < x.size - 1:
                try:
                    opt = minimize_scalar(
                        lambda z: float(chi2_func(float(z))),
                        bounds=(float(x[i - 1]), float(x[i + 1])),
                        method="bounded",
                    )
                    if opt.success and np.isfinite(opt.x) and np.isfinite(opt.fun):
                        candidates.append((float(opt.x), float(opt.fun), "local_refine"))
                except Exception:
                    pass
        if scan_all_segments:
            for i in range(x.size - 1):
                try:
                    opt = minimize_scalar(
                        lambda z: float(chi2_func(float(z))),
                        bounds=(float(x[i]), float(x[i + 1])),
                        method="bounded",
                    )
                    if opt.success and np.isfinite(opt.x) and np.isfinite(opt.fun):
                        candidates.append((float(opt.x), float(opt.fun), "segment_refine"))
                except Exception:
                    pass
    best_x, best_y, source = min(candidates, key=lambda item: item[1])
    return float(best_x), float(best_y), {"status": "ok", "best_source": source, "n_candidates": len(candidates)}


def confidence_definition(name: str) -> ConfidenceDefinition:
    try:
        return LEGACY_CONFIDENCE_DEFINITIONS[str(name)]
    except KeyError as exc:
        raise ValueError(f"unknown confidence definition {name!r}") from exc


__all__ = [
    "CL_TO_DCHI2_1DOF",
    "CL_TO_DCHI2_2DOF",
    "ConfidenceDefinition",
    "LEGACY_CONFIDENCE_DEFINITIONS",
    "confidence_definition",
    "delta_chi2",
    "extract_intervals",
    "refine_global_minimum",
]
