"""Continuous one-parameter minima, disconnected confidence sets and bounds."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq, minimize_scalar

THRESHOLDS = {"68percent": 1., "90percent": 2.71, "95percent": 3.84}


def polynomial(p, x):
    x = np.asarray(x, float)
    return p[0]+x[..., None]*(p[1]+x[..., None]*p[2])


def quadratic_domain(p, rate_upper):
    a, b, c = map(float, np.sum(p, axis=-1))
    if abs(c) < 1e-12 and abs(b) < 1e-12:
        return None
    if c <= 0: raise ValueError("cannot bound this signal from a positive quadratic")
    radius2 = (rate_upper-a+b*b/(4*c))/c
    if radius2 <= 0: raise ValueError("invalid signal bound")
    center = -b/(2*c)
    radius = np.sqrt(radius2)
    return (float(center-1.01*radius), float(center+1.01*radius))


def scan(fn, domain, *, label, reference_point, grid_size=4001, physical_boundaries=False, domain_proof=None):
    lo, hi = map(float, domain)
    grid = np.linspace(lo, hi, grid_size)
    if lo <= reference_point <= hi: grid = np.unique(np.r_[grid, reference_point])
    values = np.asarray(fn(grid), float)
    if values.shape != grid.shape or not np.isfinite(values).all(): raise ValueError("invalid chi2 values")
    if np.max(values)-np.min(values) < 1e-11:
        return {"parameter": label, "identifiable": False, "chi2_min": float(values[0]),
                "best_fit": None, "degenerate_minima": [], "reference_chi2": float(fn(reference_point)),
                "intervals": {k: [[None, None]] for k in THRESHOLDS}, "domain": [lo, hi],
                "domain_meaning": "display only; likelihood is constant for the full real parameter axis",
                "grid": grid, "chi2": values, "delta_chi2": values-values[0], "root_checks": []}
    indices = np.r_[0, np.where((values[1:-1] <= values[:-2]) & (values[1:-1] <= values[2:]))[0]+1, len(grid)-1]
    candidates = []
    for i in indices:
        if i == 0 or i == len(grid)-1:
            x, cost = grid[i], values[i]
        else:
            opt = minimize_scalar(lambda v: float(fn(v)), method="bounded", bounds=(grid[i-1], grid[i+1]), options={"xatol": 1e-12})
            x, cost = float(opt.x), float(opt.fun)
        candidates.append({"value": float(x), "chi2": float(cost)})
    best = min(candidates, key=lambda x: x["chi2"])
    minimum = best["chi2"]
    # Each curve subtracts its own one-parameter minimum, never the 2D minimum.
    degenerate = [p for p in candidates if p["chi2"]-minimum <= 1e-7]
    checks, intervals, truncated = [], {}, {}
    for level_name, level in THRESHOLDS.items():
        residual = values-minimum-level
        brackets = np.where(residual[:-1]*residual[1:] < 0)[0]
        roots = [brentq(lambda x: float(fn(x)-minimum-level), grid[i], grid[i+1], xtol=2e-12) for i in brackets]
        for x in roots:
            checks.append({"level": level_name, "root": float(x), "residual": float(fn(x)-minimum-level)})
        cuts = [lo, *roots, hi]
        intervals[level_name] = [[float(a), float(b)] for a, b in zip(cuts[:-1], cuts[1:])
                                if float(fn((a+b)/2))-minimum <= level]
        truncated[level_name] = [((abs(a-lo) < 1e-10) or (abs(b-hi) < 1e-10)) for a, b in intervals[level_name]]
    if not physical_boundaries and any(any(x) for x in truncated.values()):
        raise ValueError(f"confidence set touches a nonphysical search boundary: {label}")
    # A separate coarser partition must recover the same best minimum basin.
    coarse = np.linspace(lo, hi, 1001)
    cv = np.asarray(fn(coarse))
    start = int(np.argmin(cv))
    if start not in (0, len(coarse)-1):
        independently_refined = minimize_scalar(lambda x: float(fn(x)), bounds=(coarse[start-1], coarse[start+1]), method="bounded", options={"xatol": 1e-12})
        if abs(independently_refined.fun-minimum) > 2e-6: raise ValueError("independent 1D minimum check differs")
    else:
        independently_refined = None
    return {"parameter": label, "identifiable": True, "best_fit": best["value"], "chi2_min": minimum,
            "degenerate_minima": degenerate, "candidate_minima": candidates, "reference_point": reference_point,
            "reference_chi2": float(fn(reference_point)), "delta_chi2_reference": float(fn(reference_point)-minimum),
            "intervals": intervals, "thresholds_1d": THRESHOLDS, "boundary_touch": truncated,
            "physical_parameter_boundaries": physical_boundaries, "domain": [lo, hi],
            "domain_proof": domain_proof, "grid": grid, "chi2": values, "delta_chi2": values-minimum,
            "root_checks": checks, "independent_minimum_difference": None if independently_refined is None else float(abs(independently_refined.fun-minimum))}
