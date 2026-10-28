"""Approximate CONUS+ paper-benchmark statistics.

The primary observable is the 19-bin background-subtracted excess plotted in
Fig. 1 of arXiv:2501.17843v2.  This is a Gaussian benchmark of paper Eq. (33),
not the official CONUS+ on/off likelihood.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cevns_pyeft.statistics.profiling import (
    ProfileResult,
    profile_gaussian_one_pull,
)


from .definition import DEFINITION
N_BINS = len(DEFINITION.observation.edges)-1
SIGMA_ALPHA = DEFINITION.statistics.signal_sigma


def _spectrum(values: object, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.shape != (N_BINS,):
        raise ValueError(f"{name} must contain exactly {N_BINS} bins")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def profile_paper_eq33(
    prediction: object,
    observed_excess: object,
    sigma: object,
    *,
    sigma_alpha: float = SIGMA_ALPHA,
) -> ProfileResult:
    """Analytically profile the common signal-normalization nuisance."""

    signal = _spectrum(prediction, name="prediction")
    observed = _spectrum(observed_excess, name="observed_excess")
    uncertainty = _spectrum(sigma, name="sigma")
    if np.any(signal < 0.0):
        raise ValueError("prediction must be non-negative")
    if np.any(uncertainty <= 0.0):
        raise ValueError("sigma must be strictly positive")
    return profile_gaussian_one_pull(
        signal,
        observed,
        uncertainty,
        sigma_alpha=float(sigma_alpha),
    )


@dataclass(frozen=True)
class QuadraticSpectrum1D:
    """Per-bin exact/local quadratic representation about ``x0``."""

    x0: float
    constant: np.ndarray
    linear: np.ndarray
    quadratic: np.ndarray

    @classmethod
    def from_symmetric_samples(
        cls,
        x0: float,
        step: float,
        minus: object,
        center: object,
        plus: object,
    ) -> "QuadraticSpectrum1D":
        h = float(step)
        if not np.isfinite(h) or h <= 0.0:
            raise ValueError("step must be finite and positive")
        fm = _spectrum(minus, name="minus")
        f0 = _spectrum(center, name="center")
        fp = _spectrum(plus, name="plus")
        return cls(
            x0=float(x0),
            constant=f0.copy(),
            linear=(fp - fm) / (2.0 * h),
            quadratic=(fp + fm - 2.0 * f0) / (2.0 * h * h),
        )

    def evaluate(self, x: float | np.ndarray) -> np.ndarray:
        dx = np.asarray(x, dtype=float) - float(self.x0)
        return (
            self.constant
            + dx[..., None] * self.linear
            + dx[..., None] ** 2 * self.quadratic
        )


@dataclass(frozen=True)
class QuadraticSpectrum2D:
    """Per-bin quadratic in two parameters about the origin."""

    constant: np.ndarray
    linear_x: np.ndarray
    linear_y: np.ndarray
    quadratic_xx: np.ndarray
    quadratic_xy: np.ndarray
    quadratic_yy: np.ndarray

    @classmethod
    def from_axis_and_corner_samples(
        cls,
        step: float,
        center: object,
        x_minus: object,
        x_plus: object,
        y_minus: object,
        y_plus: object,
        xy_plus_plus: object,
    ) -> "QuadraticSpectrum2D":
        h = float(step)
        if not np.isfinite(h) or h <= 0.0:
            raise ValueError("step must be finite and positive")
        f0 = _spectrum(center, name="center")
        fxm = _spectrum(x_minus, name="x_minus")
        fxp = _spectrum(x_plus, name="x_plus")
        fym = _spectrum(y_minus, name="y_minus")
        fyp = _spectrum(y_plus, name="y_plus")
        fxy = _spectrum(xy_plus_plus, name="xy_plus_plus")
        bx = (fxp - fxm) / (2.0 * h)
        by = (fyp - fym) / (2.0 * h)
        cxx = (fxp + fxm - 2.0 * f0) / (2.0 * h * h)
        cyy = (fyp + fym - 2.0 * f0) / (2.0 * h * h)
        cxy = (fxy - f0 - h * bx - h * by - h * h * cxx - h * h * cyy) / (
            h * h
        )
        return cls(f0.copy(), bx, by, cxx, cxy, cyy)

    def evaluate(
        self,
        x: float | np.ndarray,
        y: float | np.ndarray,
    ) -> np.ndarray:
        xx, yy = np.broadcast_arrays(
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
        )
        return (
            self.constant
            + xx[..., None] * self.linear_x
            + yy[..., None] * self.linear_y
            + xx[..., None] ** 2 * self.quadratic_xx
            + (xx * yy)[..., None] * self.quadratic_xy
            + yy[..., None] ** 2 * self.quadratic_yy
        )


__all__ = [
    "N_BINS",
    "SIGMA_ALPHA",
    "QuadraticSpectrum1D",
    "QuadraticSpectrum2D",
    "profile_paper_eq33",
]

