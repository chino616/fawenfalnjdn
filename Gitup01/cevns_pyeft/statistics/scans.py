from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .confidence import delta_chi2


@dataclass(frozen=True)
class Scan1DResult:
    x: np.ndarray
    chi2: np.ndarray
    dchi2: np.ndarray
    bestfit: float
    chi2_min: float


@dataclass(frozen=True)
class Scan2DResult:
    x_values: np.ndarray
    y_values: np.ndarray
    chi2_grid: np.ndarray
    dchi2_grid: np.ndarray
    bestfit_x: float
    bestfit_y: float
    chi2_min: float


def scan_grid_1d(x_values: object, chi2_func: Callable[[float], float]) -> Scan1DResult:
    x = np.asarray(x_values, dtype=float).reshape(-1)
    chi2 = np.asarray([float(chi2_func(float(value))) for value in x], dtype=float)
    idx = int(np.nanargmin(chi2))
    chi2_min = float(chi2[idx])
    return Scan1DResult(x=x, chi2=chi2, dchi2=delta_chi2(chi2, minimum=chi2_min), bestfit=float(x[idx]), chi2_min=chi2_min)


def scan_grid_2d(
    x_values: object,
    y_values: object,
    chi2_func: Callable[[float, float], float],
) -> Scan2DResult:
    x = np.asarray(x_values, dtype=float).reshape(-1)
    y = np.asarray(y_values, dtype=float).reshape(-1)
    chi2 = np.zeros((y.size, x.size), dtype=float)
    for iy, yy in enumerate(y):
        for ix, xx in enumerate(x):
            chi2[iy, ix] = float(chi2_func(float(xx), float(yy)))
    iy0, ix0 = np.unravel_index(int(np.nanargmin(chi2)), chi2.shape)
    chi2_min = float(chi2[iy0, ix0])
    return Scan2DResult(
        x_values=x,
        y_values=y,
        chi2_grid=chi2,
        dchi2_grid=delta_chi2(chi2, minimum=chi2_min),
        bestfit_x=float(x[ix0]),
        bestfit_y=float(y[iy0]),
        chi2_min=chi2_min,
    )


__all__ = ["Scan1DResult", "Scan2DResult", "scan_grid_1d", "scan_grid_2d"]
