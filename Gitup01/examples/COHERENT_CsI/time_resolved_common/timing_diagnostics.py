"""Optional CsI2021 timing controls; no fitted onset or default physics change.

Positive delta delays the source h(t-delta). Observer bins and efficiency stay
fixed. All normalization denominators are evaluated at ZERO shift. SSB is not
an argument: this adapter must never translate the steady-state background.
"""
from pathlib import Path
import numpy as np

try:
    from .time_acceptance import TimeMassCDF, CsITimeEfficiency
except ImportError:  # direct example/module loading
    from time_acceptance import TimeMassCDF, CsITimeEfficiency

SCOPES = ("reference_window", "full_support")
BACKGROUND_MODES = ("raw", "prior_posteff", "bestfit_posteff", "prior_preeff")
PRIOR = {"BRN": 18.4, "NIN": 5.6}
BESTFIT = {"BRN": 17.3, "NIN": 5.5}


def validate_shift(shift_ns):
    value = float(shift_ns)
    if not np.isfinite(value) or abs(value) > 250:
        raise ValueError("Diagnostic timing shift must be finite and within +/-250 ns")
    return value / 1000.


def signal_time_weights(profile_path, time_edges_us, *, shift_ns=0., fluence_scope="reference_window"):
    """ROOT marginal weights in (mu,e,mub) order, plus fixed nominal q.

    Supports both the main analysis_inputs and the minimal time_profiles NPZ.
    Energy counts MUST precede time selection. No E-time joint-source claim.
    """
    shift_us = validate_shift(shift_ns)
    if fluence_scope not in SCOPES:
        raise ValueError("Unknown energy fluence scope")
    edges = np.asarray(time_edges_us, float)
    if edges.ndim != 1 or not np.isfinite(edges).all() or np.any(np.diff(edges) <= 0):
        raise ValueError("Invalid observed time edges")
    weights, fractions = [], []
    with np.load(profile_path, allow_pickle=False) as z:
        for f in ("mu", "e", "mub"):
            source_edges = z[f + "_time_edges_us"] if f + "_time_edges_us" in z else z["ROOT_time_edges_us"]
            mass = z[f + "_time_mass"]
            cdf = TimeMassCDF(mass / mass.sum(), source_edges)
            q = float(cdf.difference(0., 6.))
            weights.append(cdf.integral(edges, shift_us) / (q if fluence_scope == "reference_window" else 1.))
            fractions.append(q)
    return np.asarray(weights), np.asarray(fractions)


def integrate_time(mass, source_edges, observed_edges, *, shift_us=0., efficiency=True):
    """Integrate piecewise uniform count masses, keeping efficiency in t_rec."""
    src = np.asarray(source_edges, float) + shift_us
    mass = np.asarray(mass, float)
    if len(src) != len(mass) + 1 or np.any(np.diff(src) <= 0):
        raise ValueError("Invalid source mass bins")
    out = []
    for left, right in zip(observed_edges[:-1], observed_edges[1:]):
        lo, hi = np.maximum(src[:-1], left), np.minimum(src[1:], right)
        active = hi > lo
        integral = CsITimeEfficiency().integral(lo[active], hi[active]) if efficiency else hi[active] - lo[active]
        out.append(np.dot((mass / np.diff(src))[active], integral))
    return np.asarray(out)


def neutron_templates(official_dir, pe_edges, time_edges_us, *, shift_ns=0., mode="raw"):
    """Official TXT shapes; explicit ZERO-shift normalization conventions.

    prior_posteff: ROI after time efficiency is 18.4/5.6 at zero shift.
    bestfit_posteff: analogous 17.3/5.5 totals, NOT full paper fitted templates.
    prior_preeff: ROI before time efficiency is 18.4/5.6 at zero shift.
    These are independent diagnostic interpretations, not uniquely certified
    implementations of the paper. Raw PE tables already include PE efficiency.
    """
    shift_us = validate_shift(shift_ns)
    if mode not in BACKGROUND_MODES:
        raise ValueError("Unknown background normalization mode")
    result = {}
    for component in ("BRN", "NIN"):
        prefix = component.lower()
        en = np.loadtxt(Path(official_dir) / (prefix + "PE.txt"))
        tr = np.loadtxt(Path(official_dir) / (prefix + "Trec.txt"))
        e = np.histogram(en[:, 0], bins=pe_edges, weights=en[:, 1])[0]
        src = np.r_[tr[:, 0] - .005, tr[-1, 0] + .005]
        t = integrate_time(tr[:, 1], src, time_edges_us, shift_us=shift_us)
        if mode != "raw":
            denominator = integrate_time(tr[:, 1], src, time_edges_us, efficiency=mode != "prior_preeff").sum()
            total = BESTFIT[component] if mode == "bestfit_posteff" else PRIOR[component]
            result[component] = np.outer(e / e.sum(), t / denominator) * total
        else:
            result[component] = np.outer(e, t)
        if not np.isfinite(result[component]).all() or np.any(result[component] < 0):
            raise ValueError("Invalid neutron prediction")
    return result
