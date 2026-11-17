"""Signed one-parameter confidence sets with physical coefficient scaling.

Ground Gaussian polynomial models additionally supply all stationary/threshold
roots of their rational objective. Dense independent partitions verify roots.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial import Polynomial as P
from scipy.optimize import brentq, minimize_scalar

THRESHOLDS = {"90": 2.71, "95": 3.84}


def cutoff(coefficient_abs, dimension, coupling_abs=1.):
    if dimension not in (5, 6, 7, 8) or not np.isfinite(coupling_abs) or coupling_abs <= 0:
        raise ValueError("supported dimension and positive finite dimensionless coupling required")
    c = float(coefficient_abs)
    if not np.isfinite(c) or c <= 0:
        raise ValueError("finite positive coefficient bound required")
    return (coupling_abs / c)**(1/(dimension-4))


@dataclass
class Gaussian:
    observed: np.ndarray
    sigma: np.ndarray
    alpha_sigma: float
    background: np.ndarray | None = None
    beta_sigma: float | None = None

    def __post_init__(self):
        self.observed, self.sigma = np.asarray(self.observed, float), np.asarray(self.sigma, float)
        if self.observed.ndim != 1 or self.sigma.shape != self.observed.shape or not np.isfinite(self.observed).all() or not np.isfinite(self.sigma).all() or np.any(self.sigma <= 0):
            raise ValueError("finite matching observed/sigma arrays required")
        if not 0 < self.alpha_sigma < 1:
            raise ValueError("positive relative normalization uncertainty required")
        if self.background is not None:
            self.background = np.asarray(self.background, float)
            if self.background.shape != self.observed.shape or not np.isfinite(self.background).all() or self.beta_sigma is None or self.beta_sigma <= 0:
                raise ValueError("matching finite background and positive background pull required")

    def profile(self, signal):
        s = np.asarray(signal, float)
        if s.shape[-1:] != self.observed.shape or not np.isfinite(s).all():
            raise ValueError("invalid prediction shape/finiteness")
        scale = np.maximum(1., np.max(abs(s), axis=-1, keepdims=True))
        if np.any(s < -1e-10*scale):
            raise ValueError("negative physical signal")
        w = 1/self.sigma**2
        b = 0. if self.background is None else self.background
        r0 = self.observed-s-b
        aa = np.sum(s*s*w, axis=-1)+1/self.alpha_sigma**2
        ra = np.sum(s*r0*w, axis=-1)
        if self.background is None:
            alpha, beta = ra/aa, np.zeros_like(ra)
        else:
            ab = np.sum(s*b*w, axis=-1)
            bb = float(np.sum(b*b*w)+1/self.beta_sigma**2)
            rb = np.sum(b*r0*w, axis=-1)
            alpha, beta = (ra*bb-rb*ab)/(aa*bb-ab*ab), (rb*aa-ra*ab)/(aa*bb-ab*ab)
        residual = self.observed-(1+alpha[..., None])*s-(1+beta[..., None])*b
        data = np.sum(residual**2*w, axis=-1)
        penalty = (alpha/self.alpha_sigma)**2
        if self.background is not None:
            penalty += (beta/self.beta_sigma)**2
        return data+penalty, alpha, beta, data, penalty

    def rate_upper_bound(self, level):
        b = 0. if self.background is None else float(self.background.sum())
        u = float(self.observed.sum())-b
        variance = float(self.sigma @ self.sigma)
        if self.background is not None:
            variance += (self.beta_sigma*b)**2
        den = 1-level*self.alpha_sigma**2
        if den <= 0:
            raise ValueError("pull saturation: no finite rate-domain proof at this level")
        return (u+math.sqrt(level*(self.alpha_sigma**2*u*u+den*variance)))/den

    def rational(self, coefficients):
        """Analytic profiled chi2=N4(x)/D4(x); fixed background eliminated first."""
        p = np.asarray(coefficients, float)
        w = np.diag(1/self.sigma**2)
        u = self.observed.copy()
        if self.background is not None:
            b = self.background
            wb = w @ b
            w -= np.outer(wb, wb)/(1/self.beta_sigma**2+b @ wb)
            u -= b
        a = P([0.])
        for i in range(3):
            for j in range(3):
                term = np.zeros(i+j+1); term[-1] = p[i] @ w @ p[j]
                a += P(term)
        b = P(p @ w @ u)
        v, inv = float(u @ w @ u), 1/self.alpha_sigma**2
        return P([v*inv])-2*inv*b+(inv+v)*a-b*b, P([inv])+a


def sum_rational(parts):
    numerator, denominator = P([0.]), P([1.])
    for n, d in parts:
        # Positive rescaling avoids ill-conditioned products of large constants.
        scale = max(float(np.max(abs(n.coef))), float(np.max(abs(d.coef))), 1.)
        n, d = n/scale, d/scale
        numerator, denominator = numerator*d+n*denominator, denominator*d
    return numerator, denominator


def real_roots(polynomial, lo, hi):
    # Map the actual proven search interval to [-1,1] before companion roots.
    center, radius = (lo+hi)/2, (hi-lo)/2
    q = polynomial(P([center, radius]))
    scale = float(np.max(abs(q.coef)))
    if scale == 0:
        return []
    q = (q/scale).trim(tol=2e-14)
    return sorted(center+radius*float(z.real) for z in q.roots()
                  if abs(z.imag) < 1e-6 and -1-1e-8 <= z.real <= 1+1e-8)


def convert_intervals(intervals, coefficient_scale, dimension, coupling_abs=1.):
    """Complete interval image, including sign, disjoint islands and infinity."""
    converted = []
    for left, right in intervals:
        for sign, a, b in (("negative", left, min(right, 0.)), ("positive", max(left, 0.), right)):
            if b <= a:
                continue
            large = max(abs(a), abs(b))*coefficient_scale
            small = min(abs(a), abs(b))*coefficient_scale
            converted.append({"coefficient_sign": sign,
                              "lambda_min_GeV": cutoff(large, dimension, coupling_abs),
                              "lambda_max_GeV": None if small == 0 else cutoff(small, dimension, coupling_abs),
                              "upper_unbounded": small == 0})
    return converted


def interval_limits(intervals, coefficient_scale, dimension, coupling_abs=1.):
    if not intervals:
        return {"status": "NO_ALLOWED_INTERVAL", "global_GeV": None, "sm_connected_GeV": None}
    maxima = max(abs(x) for iv in intervals for x in iv)
    connected = [iv for iv in intervals if iv[0] <= 0 <= iv[1]]
    result = {"status": "FINITE", "global_GeV": cutoff(maxima*coefficient_scale, dimension, coupling_abs),
              "C_abs_max_GeV_power": maxima*coefficient_scale,
              "sm_connected_GeV": None if not connected else cutoff(max(abs(v) for v in connected[0])*coefficient_scale, dimension, coupling_abs),
              "sm_status": "SM_EXCLUDED" if not connected else "SM_CONNECTED"}
    for sign in ("positive", "negative"):
        chosen = [(max(a, 0.), b) if sign == "positive" else (a, min(b, 0.)) for a, b in intervals]
        chosen = [iv for iv in chosen if iv[1] > iv[0]]
        result[sign+"_GeV"] = None if not chosen else cutoff(max(abs(v) for iv in chosen for v in iv)*coefficient_scale, dimension, coupling_abs)
    return result


def scan(fn, domain, *, coefficient_scale, dimension, rational=None, grid_size=2049,
         no_sensitivity=False, coupling_abs=1.):
    lo, hi = map(float, domain)
    if not lo < 0 < hi or coefficient_scale <= 0:
        raise ValueError("a proven finite signed domain and positive coefficient scale required")
    if no_sensitivity:
        return {"status": "NO_SENSITIVITY", "coefficient_scale": coefficient_scale, "dimension": dimension,
                "chi2_min": float(fn(0.)), "bestfit_x": None,
                "confidence": {key: {"threshold": threshold, "status": "NO_SENSITIVITY", "intervals_x": [[None, None]],
                                      "global_GeV": None, "sm_connected_GeV": None, "lambda_intervals": []}
                               for key, threshold in THRESHOLDS.items()},
                "grid_x": np.linspace(-1, 1, 101), "chi2_grid": np.full(101, float(fn(0.))), "root_checks": []}
    grid = np.unique(np.r_[np.linspace(lo, hi, grid_size), 0.])
    values = np.asarray(fn(grid), float)
    if values.shape != grid.shape or not np.isfinite(values).all():
        raise ValueError("invalid likelihood grid")
    candidates = [(float(grid[i]), float(values[i])) for i in [0, len(grid)-1]]
    local = np.where((values[1:-1] <= values[:-2]) & (values[1:-1] <= values[2:]))[0]+1
    seeds = list(grid[local])
    if rational is not None:
        n, d = rational
        seeds += real_roots(n.deriv()*d-n*d.deriv(), lo, hi)
    for seed in seeds:
        i = int(np.clip(np.searchsorted(grid, seed), 1, len(grid)-2))
        a, b = grid[max(i-2, 0)], grid[min(i+2, len(grid)-1)]
        opt = minimize_scalar(lambda x: float(fn(x)), bounds=(a, b), method="bounded", options={"xatol": 1e-12})
        candidates.extend([(float(seed), float(fn(seed))), (float(opt.x), float(opt.fun))])
    best, minimum = min(candidates, key=lambda item: item[1])
    # An offset partition provides an independent check of minima basins and roots.
    alternate = np.linspace(lo, hi, 2*grid_size)
    alt_values = np.asarray(fn(alternate))
    alt_local = np.where((alt_values[1:-1] <= alt_values[:-2]) & (alt_values[1:-1] <= alt_values[2:]))[0]+1
    independent = []
    for i in alt_local:
        opt = minimize_scalar(lambda x: float(fn(x)), bounds=(alternate[i-1], alternate[i+1]), method="bounded", options={"xatol": 1e-12})
        independent.append(float(opt.fun))
    difference = abs(min(independent, default=minimum)-minimum)
    if difference > 3e-7:
        raise ValueError(f"independent minimum mismatch: {difference}")
    confidence, checks = {}, []
    for key, threshold in THRESHOLDS.items():
        level = minimum+threshold
        if float(fn(lo)) <= level or float(fn(hi)) <= level:
            raise ValueError("SEARCH_NOT_CLOSED: a numerical boundary remains allowed")
        roots = []
        for gx, gy in ((grid, values), (alternate, alt_values)):
            residual = gy-level
            for i in np.where(residual[:-1]*residual[1:] < 0)[0]:
                roots.append(brentq(lambda x: float(fn(x)-level), gx[i], gx[i+1], xtol=1e-12, rtol=1e-13))
        if rational is not None:
            candidates_r = real_roots(n-level*d, lo, hi)
            boundaries = [lo, *candidates_r, hi]
            for i, r in enumerate(candidates_r, 1):
                a, b = (boundaries[i-1]+r)/2, (boundaries[i+1]+r)/2
                if float(fn(a)-level)*float(fn(b)-level) < 0:
                    roots.append(brentq(lambda x: float(fn(x)-level), a, b, xtol=1e-12, rtol=1e-13))
        roots.sort()
        unique = []
        for r in roots:
            if not unique or abs(r-unique[-1]) > 1e-8*max(1., abs(r)):
                unique.append(float(r))
        intervals = []
        cuts = [lo, *unique, hi]
        for a, b in zip(cuts[:-1], cuts[1:]):
            if float(fn((a+b)/2)) <= level:
                intervals.append([float(a), float(b)])
        if not intervals:
            raise ValueError("no recovered confidence interval despite an interior minimum")
        for r in unique:
            residual = float(fn(r)-level)
            if abs(residual) > 2e-6:
                raise ValueError("threshold root failed likelihood back-substitution")
            checks.append({"CL": key, "x": r, "coefficient": r*coefficient_scale, "residual": residual})
        confidence[key] = {"threshold": threshold, "intervals_x": intervals,
                           "intervals_coefficient": [[a*coefficient_scale, b*coefficient_scale] for a, b in intervals],
                           "lambda_intervals": convert_intervals(intervals, coefficient_scale, dimension, coupling_abs),
                           **interval_limits(intervals, coefficient_scale, dimension, coupling_abs)}
    return {"status": "SCANNED", "dimension": dimension, "coefficient_scale": coefficient_scale,
            "coupling_abs": coupling_abs, "domain_x": [lo, hi], "bestfit_x": best,
            "bestfit_coefficient": best*coefficient_scale, "chi2_min": minimum,
            "chi2_SM": float(fn(0.)), "delta_chi2_SM": float(fn(0.)-minimum),
            "degenerate_minima_x": sorted({x for x, v in candidates if v-minimum < 1e-7}),
            "independent_minimum_difference": difference, "confidence": confidence,
            "grid_x": grid, "chi2_grid": values, "root_checks": checks,
            "minimum_search": "analytic rational stationary roots plus two independent sampled partitions" if rational is not None else "two independent sampled partitions; physical tail proof; continuous local refinement"}
