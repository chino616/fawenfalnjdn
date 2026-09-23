from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

try:
    from scipy.optimize import minimize
except Exception:  # pragma: no cover
    minimize = None

ArErrorMode = Literal["piecewise_asym", "average", "max"]


@dataclass(frozen=True)
class ProfileResult:
    chi2: float
    alpha: float
    beta: float
    chi2_data: float
    chi2_nuisance: float
    success: bool = True
    message: str = ""
    iterations: int = 0
    selected_error_side: tuple[str, ...] = ()


def _as_1d(values: object, *, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} is empty")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def _check_same_size(*arrays: np.ndarray) -> None:
    sizes = {arr.size for arr in arrays}
    if len(sizes) != 1:
        raise ValueError(f"array size mismatch: {sorted(sizes)}")


def profile_gaussian_two_pull(
    signal: object,
    observed: object,
    background: object,
    sigma: object,
    *,
    sigma_alpha: float,
    sigma_beta: float,
    clip_bounds: tuple[float, float] | None = None,
) -> ProfileResult:
    s = _as_1d(signal, name="signal")
    d = _as_1d(observed, name="observed")
    b = _as_1d(background, name="background")
    sig = np.clip(_as_1d(sigma, name="sigma"), 1.0e-12, None)
    _check_same_size(s, d, b, sig)
    sa = float(sigma_alpha)
    sb = float(sigma_beta)
    if sa <= 0.0 or sb <= 0.0:
        raise ValueError("sigma_alpha and sigma_beta must be positive")

    w = 1.0 / (sig * sig)
    r0 = d - s - b
    mat = np.array(
        [
            [float(np.sum(w * s * s)) + 1.0 / (sa * sa), float(np.sum(w * s * b))],
            [float(np.sum(w * s * b)), float(np.sum(w * b * b)) + 1.0 / (sb * sb)],
        ],
        dtype=float,
    )
    rhs = np.array([float(np.sum(w * s * r0)), float(np.sum(w * b * r0))], dtype=float)
    try:
        alpha, beta = np.linalg.solve(mat, rhs)
        success = True
        message = "analytic"
    except np.linalg.LinAlgError:
        alpha, beta = 0.0, 0.0
        success = False
        message = "singular profile matrix"

    if clip_bounds is not None:
        lo, hi = float(clip_bounds[0]), float(clip_bounds[1])
        alpha = float(np.clip(alpha, lo, hi))
        beta = float(np.clip(beta, lo, hi))

    model = (1.0 + alpha) * s + (1.0 + beta) * b
    chi2_data = float(np.sum(((d - model) / sig) ** 2))
    chi2_nuis = float((alpha / sa) ** 2 + (beta / sb) ** 2)
    return ProfileResult(
        chi2=float(chi2_data + chi2_nuis),
        alpha=float(alpha),
        beta=float(beta),
        chi2_data=chi2_data,
        chi2_nuisance=chi2_nuis,
        success=success,
        message=message,
    )


def profile_gaussian_one_pull(
    signal: object,
    observed: object,
    sigma: object,
    *,
    sigma_alpha: float,
) -> ProfileResult:
    s = _as_1d(signal, name="signal")
    d = _as_1d(observed, name="observed")
    sig = np.clip(_as_1d(sigma, name="sigma"), 1.0e-12, None)
    _check_same_size(s, d, sig)
    sa = float(sigma_alpha)
    if sa <= 0.0:
        raise ValueError("sigma_alpha must be positive")
    w = 1.0 / (sig * sig)
    denom = float(np.sum(w * s * s) + 1.0 / (sa * sa))
    alpha = float(np.sum(w * s * (d - s)) / denom) if denom > 0.0 else 0.0
    model = (1.0 + alpha) * s
    chi2_data = float(np.sum(((d - model) / sig) ** 2))
    chi2_nuis = float((alpha / sa) ** 2)
    return ProfileResult(
        chi2=float(chi2_data + chi2_nuis),
        alpha=alpha,
        beta=0.0,
        chi2_data=chi2_data,
        chi2_nuisance=chi2_nuis,
        success=denom > 0.0,
        message="analytic one-alpha profile",
    )


def ar_sigma_for_model(
    model: object,
    observed: object,
    lower: object,
    upper: object,
    *,
    error_mode: ArErrorMode = "piecewise_asym",
) -> tuple[np.ndarray, tuple[str, ...]]:
    m = _as_1d(model, name="model")
    d = _as_1d(observed, name="observed")
    lo = _as_1d(lower, name="lower")
    hi = _as_1d(upper, name="upper")
    _check_same_size(m, d, lo, hi)
    sig_minus = np.clip(d - lo, 1.0e-12, None)
    sig_plus = np.clip(hi - d, 1.0e-12, None)
    mode = str(error_mode)
    if mode == "piecewise_asym":
        side = np.where(m > d, "upper", "lower")
        return np.where(m > d, sig_plus, sig_minus), tuple(str(x) for x in side)
    if mode == "average":
        return 0.5 * (sig_plus + sig_minus), tuple("average" for _ in d)
    if mode == "max":
        return np.maximum(sig_plus, sig_minus), tuple("max" for _ in d)
    raise ValueError("error_mode must be one of: piecewise_asym, average, max")


def chi2_ar_fixed(
    signal: object,
    observed: object,
    background: object,
    lower: object,
    upper: object,
    *,
    alpha: float,
    beta: float,
    sigma_alpha: float,
    sigma_beta: float,
    error_mode: ArErrorMode = "piecewise_asym",
) -> ProfileResult:
    s = _as_1d(signal, name="signal")
    d = _as_1d(observed, name="observed")
    b = _as_1d(background, name="background")
    _check_same_size(s, d, b)
    model = (1.0 + float(alpha)) * s + (1.0 + float(beta)) * b
    sigma, side = ar_sigma_for_model(model, d, lower, upper, error_mode=error_mode)
    chi2_data = float(np.sum(((d - model) / sigma) ** 2))
    chi2_nuis = float((float(alpha) / float(sigma_alpha)) ** 2 + (float(beta) / float(sigma_beta)) ** 2)
    return ProfileResult(
        chi2=float(chi2_data + chi2_nuis),
        alpha=float(alpha),
        beta=float(beta),
        chi2_data=chi2_data,
        chi2_nuisance=chi2_nuis,
        selected_error_side=side,
    )


def profile_ar2020_irls(
    signal: object,
    observed: object,
    background: object,
    lower: object,
    upper: object,
    *,
    sigma_alpha: float,
    sigma_beta: float,
    error_mode: ArErrorMode = "piecewise_asym",
    max_iter: int = 8,
    tol: float = 1.0e-9,
) -> ProfileResult:
    s = _as_1d(signal, name="signal")
    d = _as_1d(observed, name="observed")
    b = _as_1d(background, name="background")
    _check_same_size(s, d, b)
    alpha, beta = 0.0, 0.0
    last_sigma = None
    iterations = 0
    side: tuple[str, ...] = ()
    for index in range(int(max_iter)):
        model = (1.0 + alpha) * s + (1.0 + beta) * b
        sigma, side = ar_sigma_for_model(model, d, lower, upper, error_mode=error_mode)
        prof = profile_gaussian_two_pull(
            s,
            d,
            b,
            sigma,
            sigma_alpha=sigma_alpha,
            sigma_beta=sigma_beta,
            clip_bounds=(-1.0, 1.0),
        )
        iterations = index + 1
        if (
            last_sigma is not None
            and np.array_equal(sigma, last_sigma)
            and abs(prof.alpha - alpha) < float(tol)
            and abs(prof.beta - beta) < float(tol)
        ):
            alpha, beta = prof.alpha, prof.beta
            break
        alpha, beta = prof.alpha, prof.beta
        last_sigma = sigma

    fixed = chi2_ar_fixed(
        s,
        d,
        b,
        lower,
        upper,
        alpha=alpha,
        beta=beta,
        sigma_alpha=sigma_alpha,
        sigma_beta=sigma_beta,
        error_mode=error_mode,
    )
    return ProfileResult(
        chi2=fixed.chi2,
        alpha=float(alpha),
        beta=float(beta),
        chi2_data=fixed.chi2_data,
        chi2_nuisance=fixed.chi2_nuisance,
        success=True,
        message="piecewise_asym_irls" if error_mode == "piecewise_asym" else "fixed_sigma_analytic",
        iterations=iterations,
        selected_error_side=fixed.selected_error_side or side,
    )


def profile_ar2020_bounded(
    signal: object,
    observed: object,
    background: object,
    lower: object,
    upper: object,
    *,
    sigma_alpha: float,
    sigma_beta: float,
    error_mode: ArErrorMode = "piecewise_asym",
) -> ProfileResult:
    if minimize is None:
        raise RuntimeError("scipy.optimize.minimize is required for bounded Ar2020 profiling")
    s = _as_1d(signal, name="signal")
    d = _as_1d(observed, name="observed")
    b = _as_1d(background, name="background")

    def objective(x: np.ndarray) -> float:
        return chi2_ar_fixed(
            s,
            d,
            b,
            lower,
            upper,
            alpha=float(x[0]),
            beta=float(x[1]),
            sigma_alpha=sigma_alpha,
            sigma_beta=sigma_beta,
            error_mode=error_mode,
        ).chi2

    res = minimize(
        objective,
        x0=np.array([0.0, 0.0], dtype=float),
        method="L-BFGS-B",
        bounds=((-1.0, 1.0), (-1.0, 1.0)),
    )
    xbest = np.asarray(res.x if getattr(res, "success", False) else [0.0, 0.0], dtype=float)
    fixed = chi2_ar_fixed(
        s,
        d,
        b,
        lower,
        upper,
        alpha=float(xbest[0]),
        beta=float(xbest[1]),
        sigma_alpha=sigma_alpha,
        sigma_beta=sigma_beta,
        error_mode=error_mode,
    )
    return ProfileResult(
        chi2=fixed.chi2,
        alpha=fixed.alpha,
        beta=fixed.beta,
        chi2_data=fixed.chi2_data,
        chi2_nuisance=fixed.chi2_nuisance,
        success=bool(getattr(res, "success", False)),
        message=str(getattr(res, "message", "")),
        iterations=int(getattr(res, "nit", 0) or 0),
        selected_error_side=fixed.selected_error_side,
    )


__all__ = [
    "ArErrorMode",
    "ProfileResult",
    "ar_sigma_for_model",
    "chi2_ar_fixed",
    "profile_ar2020_bounded",
    "profile_ar2020_irls",
    "profile_gaussian_one_pull",
    "profile_gaussian_two_pull",
]
